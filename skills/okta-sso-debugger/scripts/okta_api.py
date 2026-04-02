# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "click>=8.0", "python-dotenv>=1.0"]
# ///
"""
Okta API client and CLI. Standalone — no repo dependency.
Run with: uv run okta_api.py ...

Setup:
    export okta_ciam='{"orgUrl": "https://hdp.okta.com", "token": "..."}'
    # Or create .env file in current directory with the line above

CLI:
    python okta_api.py user "user@example.com"
    python okta_api.py user-factors "user@example.com"
    python okta_api.py user-logs "user@example.com" --days 7
    python okta_api.py user-groups "user@example.com"
    python okta_api.py get /api/v1/idps/{idpId}
"""

import asyncio
import json
import os
import sys
import time

try:
    import click
    import httpx
    from dotenv import load_dotenv
except ImportError:
    sys.exit("Missing dependencies. Run: pip install httpx click python-dotenv")

load_dotenv(override=True)


class OktaAPI:
    def __init__(self, org_url: str, token: str):
        self.org_url = org_url.rstrip("/")
        self.token = token
        self.client = httpx.AsyncClient(
            base_url=self.org_url,
            headers={
                "Authorization": f"SSWS {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    @classmethod
    def from_env(cls, env_name: str = "ciam") -> "OktaAPI":
        config = json.loads(os.environ.get(f"okta_{env_name.lower()}", "{}"))
        org_url = config.get("orgUrl", "")
        token = config.get("token", "")
        if not org_url or not token:
            raise ValueError(f"Missing orgUrl or token in okta_{env_name} env var")
        return cls(org_url, token)

    def _check_rate_limit(self, headers: httpx.Headers):
        remaining = headers.get("X-Rate-Limit-Remaining")
        if remaining and int(remaining) < 3:
            reset = int(headers.get("X-Rate-Limit-Reset", "0"))
            wait = min(5, max(0, reset - int(time.time()) + 1))
            print(f"  ⏳ Rate limit low ({remaining} remaining), waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)

    async def get(self, path: str, params: dict | None = None) -> list | dict:
        results = []
        url = path
        while url:
            resp = await self.client.get(url, params=params if url == path else None)
            self._check_rate_limit(resp.headers)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                results.extend(data)
            else:
                return data
            url = _next_link(resp.headers.get("link", ""))
        return results

    async def post(self, path: str, body: dict) -> dict:
        resp = await self.client.post(path, json=body)
        self._check_rate_limit(resp.headers)
        resp.raise_for_status()
        return resp.json()

    async def put(self, path: str, body: dict | None = None) -> dict | None:
        resp = await self.client.put(path, json=body or {})
        self._check_rate_limit(resp.headers)
        resp.raise_for_status()
        return resp.json() if resp.content else None

    async def close(self):
        await self.client.aclose()


def _next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        if 'rel="next"' in part:
            return part.split(";")[0].strip().strip("<>")
    return None


def okta(env: str = "ciam") -> OktaAPI:
    """Convenience factory — use in scripts: api = okta()"""
    return OktaAPI.from_env(env)


def run(coro):
    """Run an async coroutine synchronously — use in scripts: run(api.get(...))"""
    return asyncio.run(_run_and_close(coro))


async def _run_and_close(coro):
    return await coro


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
@click.option("--env", default="ciam", show_default=True, help="Okta env name (reads okta_<env> from .env)")
@click.option("--raw", is_flag=True, help="Output raw JSON without formatting")
@click.pass_context
def cli(ctx, env, raw):
    ctx.ensure_object(dict)
    ctx.obj["env"] = env
    ctx.obj["raw"] = raw


def _print(data, raw: bool):
    if raw:
        print(json.dumps(data))
    else:
        print(json.dumps(data, indent=2))


@cli.command()
@click.argument("path")
@click.option("--param", "-p", multiple=True, help="Query param as key=value (repeatable)")
@click.pass_context
def get(ctx, path, param):
    """GET an Okta API path with automatic pagination."""
    params = dict(p.split("=", 1) for p in param) if param else None

    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            data = await api.get(path, params=params)
        finally:
            await api.close()
        return data

    _print(asyncio.run(_run()), ctx.obj["raw"])


@cli.command()
@click.argument("path")
@click.option("--file", "-f", type=click.File("r"), default="-", help="JSON body file (default: stdin)")
@click.pass_context
def post(ctx, path, file):
    """POST JSON body to an Okta API path."""
    body = json.load(file)

    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            data = await api.post(path, body)
        finally:
            await api.close()
        return data

    _print(asyncio.run(_run()), ctx.obj["raw"])


@cli.command()
@click.argument("path")
@click.option("--file", "-f", type=click.File("r"), default=None, help="JSON body file (optional)")
@click.pass_context
def put(ctx, path, file):
    """PUT to an Okta API path (e.g. assign policy to app)."""
    body = json.load(file) if file else None

    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            data = await api.put(path, body)
        finally:
            await api.close()
        return data

    result = asyncio.run(_run())
    if result:
        _print(result, ctx.obj["raw"])
    else:
        print("✅ 204 No Content (success)")


@cli.command()
@click.argument("policy_id")
@click.pass_context
def policy(ctx, policy_id):
    """Show a policy and all its rules."""
    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            pol = await api.get(f"/api/v1/policies/{policy_id}")
            rules = await api.get(f"/api/v1/policies/{policy_id}/rules")
        finally:
            await api.close()
        return {"policy": pol, "rules": rules}

    _print(asyncio.run(_run()), ctx.obj["raw"])


@cli.command()
@click.argument("email")
@click.pass_context
def user(ctx, email):
    """Look up an Okta user by email."""
    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            results = await api.get("/api/v1/users", params={"search": f'profile.email eq "{email}"'})
        finally:
            await api.close()
        return results[0] if results else {}

    _print(asyncio.run(_run()), ctx.obj["raw"])


@cli.command("user-groups")
@click.argument("email")
@click.pass_context
def user_groups(ctx, email):
    """List groups for an Okta user."""
    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            users = await api.get("/api/v1/users", params={"search": f'profile.email eq "{email}"'})
            if not users:
                return []
            uid = users[0]["id"]
            groups = await api.get(f"/api/v1/users/{uid}/groups")
        finally:
            await api.close()
        return [{"id": g["id"], "name": g["profile"]["name"]} for g in groups]

    _print(asyncio.run(_run()), ctx.obj["raw"])


@cli.command("user-factors")
@click.argument("email")
@click.pass_context
def user_factors(ctx, email):
    """List enrolled authenticator factors for a user."""
    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            users = await api.get("/api/v1/users", params={"search": f'profile.email eq "{email}"'})
            if not users:
                return {"error": f"User not found: {email}"}
            uid = users[0]["id"]
            factors = await api.get(f"/api/v1/users/{uid}/factors")
        finally:
            await api.close()
        return [{"type": f["factorType"], "provider": f["provider"],
                 "status": f["status"], "profile": f.get("profile", {})}
                for f in factors]

    _print(asyncio.run(_run()), ctx.obj["raw"])


@cli.command("user-logs")
@click.argument("email")
@click.option("--days", "-d", default=7, show_default=True, help="Look back N days")
@click.option("--limit", "-n", default=20, show_default=True)
@click.pass_context
def user_logs(ctx, email, days, limit):
    """Show recent Okta system log events for a user."""
    from datetime import datetime, timedelta, timezone

    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            users = await api.get("/api/v1/users", params={"search": f'profile.email eq "{email}"'})
            if not users:
                return {"error": f"User not found: {email}"}
            uid = users[0]["id"]
            since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            logs = await api.get("/api/v1/logs", params={
                "filter": f'target.id eq "{uid}"',
                "since": since,
                "limit": str(limit),
                "sortOrder": "DESCENDING",
            })
        finally:
            await api.close()
        return [{"time": e["published"][:19], "event": e["eventType"],
                 "result": e.get("outcome", {}).get("result", ""),
                 "reason": e.get("outcome", {}).get("reason", "")}
                for e in logs]

    data = asyncio.run(_run())
    if ctx.obj["raw"] or (isinstance(data, dict) and "error" in data):
        _print(data, ctx.obj["raw"])
    else:
        for e in data:
            reason = f" | {e['reason']}" if e['reason'] else ""
            print(f"{e['time']}  {e['result']:8s}  {e['event']}{reason}")


@cli.command("app-policies")
@click.argument("app_id")
@click.pass_context
def app_policies(ctx, app_id):
    """Show the auth and enrollment policies assigned to an app."""
    async def _run():
        api = OktaAPI.from_env(ctx.obj["env"])
        try:
            app = await api.get(f"/api/v1/apps/{app_id}")
            links = app.get("_links", {})
            ap_url = links.get("accessPolicy", {}).get("href", "")
            pe_url = links.get("profileEnrollment", {}).get("href", "")
            ap_id = ap_url.split("/")[-1] if ap_url else None
            pe_id = pe_url.split("/")[-1] if pe_url else None

            result = {"app": app.get("label"), "app_id": app_id}
            if ap_id:
                ap = await api.get(f"/api/v1/policies/{ap_id}")
                ap["_rules"] = await api.get(f"/api/v1/policies/{ap_id}/rules")
                result["auth_policy"] = ap
            if pe_id:
                pe = await api.get(f"/api/v1/policies/{pe_id}")
                pe["_rules"] = await api.get(f"/api/v1/policies/{pe_id}/rules")
                result["enrollment_policy"] = pe
        finally:
            await api.close()
        return result

    _print(asyncio.run(_run()), ctx.obj["raw"])


if __name__ == "__main__":
    cli()
