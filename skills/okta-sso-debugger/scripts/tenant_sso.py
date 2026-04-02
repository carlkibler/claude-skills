# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "click>=8.0", "python-dotenv>=1.0"]
# ///
"""
Tenant SSO Discovery & Validation Tool. Standalone — run with: uv run tenant_sso.py ...

CLI usage:
    uv run tenant_sso.py discover "Carle Health" --domain carle.com
    uv run tenant_sso.py validate "Sanitas" --domain mysanitas.com
    uv run tenant_sso.py report "Carle Health" --domain carle.com
"""

import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime

try:
    import click
except ImportError:
    sys.exit("Missing dependencies. Run: pip install httpx click python-dotenv")

from okta_api import OktaAPI

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TenantSSO:
    name: str
    domains: list[str] = field(default_factory=list)
    idps: list[dict] = field(default_factory=list)
    idp_mappings: list[dict] = field(default_factory=list)
    idp_auto_groups: dict = field(default_factory=dict)     # idp_id → [group_id, ...]
    routing_rules: list[dict] = field(default_factory=list)
    groups: list[dict] = field(default_factory=list)
    apps: list[dict] = field(default_factory=list)          # includes _auth_policy, _enrollment_policy
    auth_policies: list[dict] = field(default_factory=list) # deduped across apps
    enrollment_policies: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def _fuzzy(text: str, hints: list[str]) -> bool:
    t = text.lower()
    return any(h.lower() in t for h in hints if h)


async def discover_tenant(api: OktaAPI, name: str, domain: str | None = None) -> TenantSSO:
    hints = [h for h in [name, domain] if h]
    tenant = TenantSSO(name=name)
    if domain:
        tenant.domains.append(domain)

    print(f"\n🔍 Discovering SSO artifacts for '{name}' (hints: {hints})\n", file=sys.stderr)

    # --- IdPs ---
    print("  → Identity Providers...", file=sys.stderr)
    all_idps = await api.get("/api/v1/idps")
    tenant.idps = [i for i in all_idps if _fuzzy(i.get("name", ""), hints)]
    idp_ids = {i["id"] for i in tenant.idps}
    print(f"    {len(tenant.idps)} matched", file=sys.stderr)

    for idp in tenant.idps:
        groups_cfg = idp.get("policy", {}).get("provisioning", {}).get("groups", {})
        assignments = groups_cfg.get("assignments", [])
        if assignments:
            tenant.idp_auto_groups[idp["id"]] = assignments

    # --- IdP profile mappings ---
    print("  → Profile Mappings...", file=sys.stderr)
    all_mappings = await api.get("/api/v1/mappings")
    mapping_ids = [m["id"] for m in all_mappings
                   if m.get("source", {}).get("id") in idp_ids]
    for mid in mapping_ids:
        m = await api.get(f"/api/v1/mappings/{mid}")
        tenant.idp_mappings.append(m)
    print(f"    {len(tenant.idp_mappings)} matched", file=sys.stderr)

    # --- IdP Discovery routing rules ---
    print("  → IdP Routing Rules...", file=sys.stderr)
    disc_policies = await api.get("/api/v1/policies?type=IDP_DISCOVERY")
    for pol in disc_policies:
        rules = await api.get(f"/api/v1/policies/{pol['id']}/rules")
        for rule in rules:
            rule_str = json.dumps(rule).lower()
            # Match by domain hint OR by IdP ID reference
            if any(d.lower() in rule_str for d in tenant.domains) or \
               any(iid in rule_str for iid in idp_ids):
                if rule not in tenant.routing_rules:
                    tenant.routing_rules.append(rule)
                    # Discover additional domains from this rule
                    for pat in rule.get("conditions", {}).get("userIdentifier", {}).get("patterns", []):
                        v = pat.get("value", "")
                        if v and v not in tenant.domains:
                            tenant.domains.append(v)
    # Re-check routing rules with expanded domains
    for pol in disc_policies:
        rules = await api.get(f"/api/v1/policies/{pol['id']}/rules")
        for rule in rules:
            rule_str = json.dumps(rule).lower()
            if any(d.lower() in rule_str for d in tenant.domains):
                if rule not in tenant.routing_rules:
                    tenant.routing_rules.append(rule)
    print(f"    {len(tenant.routing_rules)} matched (domains: {tenant.domains})", file=sys.stderr)

    # --- Groups ---
    print("  → Groups...", file=sys.stderr)
    search_terms = list(hints)
    for d in tenant.domains:
        prefix = d.split(".")[0]
        if prefix and prefix not in search_terms:
            search_terms.append(prefix)
    # Also search for groups referenced in IdP auto-assign
    auto_group_ids = set()
    for gids in tenant.idp_auto_groups.values():
        auto_group_ids.update(gids)
    for hint in search_terms:
        groups = await api.get(f"/api/v1/groups?q={hint}")
        for g in groups:
            if g not in tenant.groups:
                tenant.groups.append(g)
    for gid in auto_group_ids:
        if not any(g["id"] == gid for g in tenant.groups):
            try:
                g = await api.get(f"/api/v1/groups/{gid}")
                tenant.groups.append(g)
            except Exception:
                pass
    print(f"    {len(tenant.groups)} matched", file=sys.stderr)

    # --- Apps ---
    print("  → Apps...", file=sys.stderr)
    all_apps = await api.get("/api/v1/apps?limit=200")
    domain_patterns = [re.escape(d.split(".")[0]) for d in tenant.domains]
    for app in all_apps:
        label = app.get("label", "").lower()
        name_field = app.get("name", "").lower()
        if _fuzzy(label, hints) or _fuzzy(name_field, hints) or \
           any(re.search(p, label) for p in domain_patterns):
            # Enrich with policies via _links
            links = app.get("_links", {})
            ap_url = links.get("accessPolicy", {}).get("href", "")
            pe_url = links.get("profileEnrollment", {}).get("href", "")
            ap_id = ap_url.split("/")[-1] if ap_url else None
            pe_id = pe_url.split("/")[-1] if pe_url else None

            if ap_id:
                ap = await api.get(f"/api/v1/policies/{ap_id}")
                ap["_rules"] = await api.get(f"/api/v1/policies/{ap_id}/rules")
                app["_auth_policy"] = ap
                if not any(p["id"] == ap_id for p in tenant.auth_policies):
                    tenant.auth_policies.append(ap)
            if pe_id:
                pe = await api.get(f"/api/v1/policies/{pe_id}")
                pe["_rules"] = await api.get(f"/api/v1/policies/{pe_id}/rules")
                app["_enrollment_policy"] = pe
                if not any(p["id"] == pe_id for p in tenant.enrollment_policies):
                    tenant.enrollment_policies.append(pe)

            # Add OIDC settings summary
            oidc = app.get("settings", {}).get("oauthClient", {})
            app["_oidc"] = {
                "initiate_login_uri": oidc.get("initiate_login_uri"),
                "redirect_uris": oidc.get("redirect_uris", []),
                "grant_types": oidc.get("grant_types", []),
            }
            tenant.apps.append(app)
    print(f"    {len(tenant.apps)} matched", file=sys.stderr)

    return tenant


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

CHECKS = [
    # (id, description, severity)
    ("idp_trust_claims",        "IdP trustClaims is false (required for IdP-initiated SSO)","error"),
    ("idp_exists",              "At least one active IdP found",                           "error"),
    ("idp_saml2",               "IdP uses SAML2 protocol",                                 "error"),
    ("idp_jit_auto",            "IdP JIT provisioning action is AUTO",                     "error"),
    ("idp_profile_master",      "IdP JIT profileMaster is true",                           "warning"),
    ("idp_account_link",        "IdP accountLink action is AUTO",                          "warning"),
    ("idp_no_deprecated",       "No deprecated IdPs still ACTIVE",                         "warning"),
    ("idp_groups_match_policy", "IdP auto-assign groups include access policy group",      "error"),
    ("routing_rule_exists",     "IdP routing rule found for tenant domain(s)",             "error"),
    ("routing_active",          "All routing rules are ACTIVE",                            "error"),
    ("group_exists",            "At least one tenant group found",                         "warning"),
    ("app_exists",              "At least one OIDC app found",                             "error"),
    ("app_no_login_uri",        "App initiate_login_uri is empty (avoids Dashboard loop)", "warning"),
    ("app_auth_code",           "App grant_types includes authorization_code",             "warning"),
    ("app_no_implicit",         "App grant_types does not use implicit (deprecated)",      "info"),
    ("enrollment_no_email",     "Enrollment policy does not require email verification",   "warning"),
    ("auth_1fa_sso_rule",       "Auth policy has a 1FA rule for tenant SSO group",         "error"),
    ("auth_constraint_email",   "Auth 1FA constraint accepts email factor (for JIT users)","error"),
    ("auth_constraint_not_empty","Auth 1FA constraint is not empty (empty = UNSATISFIABLE)","error"),
    ("auth_no_device_req",      "Auth policy 1FA rule has no device-bound constraint",     "warning"),
    ("mapping_email",           "IdP profile mapping includes email field",                "error"),
    ("mapping_login",           "IdP profile mapping includes login field",                "error"),
]


def validate_tenant(tenant: TenantSSO) -> list[dict]:
    results = []

    def result(check_id: str, passed: bool, detail: str = ""):
        sev = next(s for cid, _, s in CHECKS if cid == check_id)
        desc = next(d for cid, d, _ in CHECKS if cid == check_id)
        results.append({
            "check": check_id,
            "description": desc,
            "passed": passed,
            "severity": sev,
            "detail": detail,
        })

    active_idps = [i for i in tenant.idps if i.get("status") == "ACTIVE"]

    trust_claims_bad = [i for i in active_idps
                        if i.get("policy", {}).get("trustClaims") is True]
    result("idp_trust_claims", not trust_claims_bad,
           f"trustClaims=true on: {[i['name'] for i in trust_claims_bad]} — WILL CAUSE UNSATISFIABLE for JIT users"
           if trust_claims_bad else "All active IdPs have trustClaims=false")

    result("idp_exists", bool(active_idps),
           f"{len(active_idps)} active IdP(s): {[i['name'] for i in active_idps]}")

    saml_idps = [i for i in active_idps if i.get("type") == "SAML2"]
    result("idp_saml2", bool(saml_idps),
           f"{len(saml_idps)} SAML2 IdP(s)")

    jit_auto = [i for i in active_idps
                if i.get("policy", {}).get("provisioning", {}).get("action") == "AUTO"]
    result("idp_jit_auto", len(jit_auto) == len(active_idps),
           f"{len(jit_auto)}/{len(active_idps)} have JIT action=AUTO")

    pm_true = [i for i in active_idps
               if i.get("policy", {}).get("provisioning", {}).get("profileMaster") is True]
    result("idp_profile_master", len(pm_true) == len(active_idps),
           f"{len(pm_true)}/{len(active_idps)} have profileMaster=true")

    acct_auto = [i for i in active_idps
                 if i.get("policy", {}).get("accountLink", {}).get("action") == "AUTO"]
    result("idp_account_link", len(acct_auto) == len(active_idps),
           f"{len(acct_auto)}/{len(active_idps)} have accountLink=AUTO")

    deprecated_active = [i for i in active_idps
                         if "deprecated" in i.get("name", "").lower()]
    result("idp_no_deprecated", not deprecated_active,
           f"Deprecated but ACTIVE: {[i['name'] for i in deprecated_active]}" if deprecated_active
           else "No deprecated IdPs found active")

    active_rules = [r for r in tenant.routing_rules if r.get("status") == "ACTIVE"]
    result("routing_rule_exists", bool(active_rules),
           f"{len(active_rules)} routing rule(s) for domains {tenant.domains}")
    result("routing_active", len(active_rules) == len(tenant.routing_rules),
           f"{len(active_rules)}/{len(tenant.routing_rules)} are ACTIVE")

    result("group_exists", bool(tenant.groups),
           f"{len(tenant.groups)} group(s): {[g['profile']['name'] for g in tenant.groups]}")

    oidc_apps = [a for a in tenant.apps if a.get("signOnMode") == "OPENID_CONNECT"
                 and a.get("status") == "ACTIVE"]
    result("app_exists", bool(oidc_apps),
           f"{len(oidc_apps)} active OIDC app(s)")

    apps_no_login_uri = [a for a in oidc_apps if not a.get("_oidc", {}).get("initiate_login_uri")]
    result("app_no_login_uri", len(apps_no_login_uri) == len(oidc_apps),
           f"{len(apps_no_login_uri)}/{len(oidc_apps)} have no initiate_login_uri")

    apps_auth_code = [a for a in oidc_apps
                      if "authorization_code" in a.get("_oidc", {}).get("grant_types", [])]
    result("app_auth_code", len(apps_auth_code) == len(oidc_apps),
           f"{len(apps_auth_code)}/{len(oidc_apps)} include authorization_code grant")

    apps_implicit = [a for a in oidc_apps
                     if "implicit" in a.get("_oidc", {}).get("grant_types", [])]
    result("app_no_implicit", not apps_implicit,
           f"{len(apps_implicit)} app(s) still use implicit grant (deprecated)")

    # Enrollment policy: no email verification required
    no_email_policies = []
    for pe in tenant.enrollment_policies:
        for rule in pe.get("_rules", []):
            ev = rule.get("actions", {}).get("profileEnrollment", {}) \
                     .get("activationRequirements", {}).get("emailVerification")
            if ev is False:
                no_email_policies.append(pe["name"])
    result("enrollment_no_email", bool(no_email_policies),
           f"Policies without email verification: {no_email_policies}" if no_email_policies
           else "All enrollment policies require email verification")

    # Auth policy: 1FA rule for tenant group
    tenant_group_ids = {g["id"] for g in tenant.groups}
    sso_rules_1fa = []
    device_bound_violations = []
    constraint_has_email = []
    constraint_empty = []
    policy_required_groups: set[str] = set()
    for ap in tenant.auth_policies:
        for rule in ap.get("_rules", []):
            conds = (rule.get("conditions") or {}).get("people", {}).get("groups", {})
            included = set(conds.get("include", []))
            if included & tenant_group_ids:
                policy_required_groups.update(included & tenant_group_ids)
                v = rule.get("actions", {}).get("appSignOn", {}).get("verificationMethod", {})
                rule_label = f"{ap['name']} / {rule['name']}"
                if v.get("factorMode") == "1FA":
                    sso_rules_1fa.append(rule_label)
                constraints = v.get("constraints", [])
                for c in constraints:
                    if c.get("possession", {}).get("deviceBound") == "REQUIRED":
                        device_bound_violations.append(rule_label)
                    knowledge = c.get("knowledge", {})
                    if knowledge:
                        types = knowledge.get("types", [])
                        if "email" in types:
                            constraint_has_email.append(rule_label)
                        if not types:
                            constraint_empty.append(rule_label)
                    elif not c.get("possession"):
                        constraint_empty.append(rule_label)

    result("auth_1fa_sso_rule", bool(sso_rules_1fa),
           f"1FA rules covering tenant group: {sso_rules_1fa}" if sso_rules_1fa
           else "No 1FA rule found that includes tenant group")
    result("auth_constraint_email", bool(constraint_has_email),
           f"Rules with email in knowledge types: {constraint_has_email}" if constraint_has_email
           else "No 1FA rule accepts email factor — JIT users with only email enrolled will get UNSATISFIABLE")
    result("auth_constraint_not_empty", not constraint_empty,
           f"Rules with empty constraints (will fail): {constraint_empty}" if constraint_empty
           else "All constraints specify factor types")
    result("auth_no_device_req", not device_bound_violations,
           f"Device-bound violations: {device_bound_violations}" if device_bound_violations
           else "No device-bound constraints on tenant SSO rules")

    # Cross-reference: IdP auto-assign groups vs access policy required groups
    all_auto_groups: set[str] = set()
    for gids in tenant.idp_auto_groups.values():
        all_auto_groups.update(gids)
    missing_groups = policy_required_groups - all_auto_groups
    if policy_required_groups:
        group_names = {g["id"]: g["profile"]["name"] for g in tenant.groups}
        missing_names = [group_names.get(gid, gid) for gid in missing_groups]
        result("idp_groups_match_policy",
               not missing_groups,
               f"Missing from IdP auto-assign: {missing_names}" if missing_groups
               else f"All policy groups ({[group_names.get(g, g) for g in policy_required_groups]}) are auto-assigned by IdP")
    else:
        result("idp_groups_match_policy", False,
               "No policy groups found to cross-reference")

    # Profile mappings
    all_props = {}
    for m in tenant.idp_mappings:
        all_props.update(m.get("properties", {}))
    result("mapping_email", "email" in all_props,
           f"email mapped: {all_props.get('email', {}).get('expression', 'NOT FOUND')}")
    result("mapping_login", "login" in all_props,
           f"login mapped: {all_props.get('login', {}).get('expression', 'NOT FOUND')}")

    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(tenant: TenantSSO, checks: list[dict]) -> str:
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Tenant SSO Profile: {tenant.name}")
    lines.append(f"\nGenerated: {now}\n")
    lines.append(f"**Domains:** {', '.join(tenant.domains)}\n")

    # Validation summary
    errors   = [c for c in checks if not c["passed"] and c["severity"] == "error"]
    warnings = [c for c in checks if not c["passed"] and c["severity"] == "warning"]
    infos    = [c for c in checks if not c["passed"] and c["severity"] == "info"]
    passed   = [c for c in checks if c["passed"]]

    lines.append("## Validation Summary\n")
    lines.append(f"- ✅ Passed: {len(passed)}")
    lines.append(f"- ❌ Errors: {len(errors)}")
    lines.append(f"- ⚠️  Warnings: {len(warnings)}")
    lines.append(f"- ℹ️  Info: {len(infos)}")
    lines.append("")

    if errors or warnings or infos:
        lines.append("### Issues\n")
        for c in errors + warnings + infos:
            icon = "❌" if c["severity"] == "error" else ("⚠️" if c["severity"] == "warning" else "ℹ️")
            lines.append(f"{icon} **{c['description']}**")
            if c["detail"]:
                lines.append(f"   {c['detail']}")
        lines.append("")

    # IdPs
    lines.append("## Identity Providers\n")
    for idp in tenant.idps:
        pol = idp.get("policy", {})
        prov = pol.get("provisioning", {})
        subj = pol.get("subject", {})
        lines.append(f"### {idp.get('name')} (`{idp['id']}`)")
        lines.append(f"- Status: {idp.get('status')} | Type: {idp.get('type')}")
        lines.append(f"- SSO URL: {idp.get('protocol',{}).get('endpoints',{}).get('sso',{}).get('url','N/A')}")
        lines.append(f"- JIT: action={prov.get('action')}, profileMaster={prov.get('profileMaster')}")
        lines.append(f"- AccountLink: {pol.get('accountLink',{}).get('action')}")
        lines.append(f"- Subject: matchType={subj.get('matchType')}, template=`{subj.get('userNameTemplate',{}).get('template','N/A')}`")
        auto_gids = tenant.idp_auto_groups.get(idp["id"], [])
        if auto_gids:
            group_names = {g["id"]: g["profile"]["name"] for g in tenant.groups}
            auto_names = [group_names.get(gid, gid) for gid in auto_gids]
            lines.append(f"- Auto-assign groups: {auto_names}")
        lines.append("")

    # Profile Mappings
    if tenant.idp_mappings:
        lines.append("## Profile Mappings (IdP → Okta User)\n")
        for m in tenant.idp_mappings:
            src = m.get("source", {}).get("name", "?")
            lines.append(f"### {src}")
            for k, v in sorted(m.get("properties", {}).items()):
                expr = v.get("expression", "?") if isinstance(v, dict) else v
                push = v.get("pushStatus", "") if isinstance(v, dict) else ""
                lines.append(f"- `{k}`: `{expr}`" + (f" *(push: {push})*" if push else ""))
            lines.append("")

    # Routing Rules
    lines.append("## IdP Routing Rules\n")
    for rule in tenant.routing_rules:
        uid = rule.get("conditions", {}).get("userIdentifier", {})
        patterns = uid.get("patterns", [])
        providers = rule.get("actions", {}).get("idp", {}).get("providers", [])
        lines.append(f"### {rule.get('name')} (`{rule.get('id')}`)")
        lines.append(f"- Status: {rule.get('status')} | Priority: {rule.get('priority')}")
        lines.append(f"- Domain patterns: {[p['value'] for p in patterns]}")
        lines.append(f"- Routes to: {[p.get('name', p.get('id')) for p in providers]}")
        lines.append("")

    # Groups
    lines.append("## Groups\n")
    for g in tenant.groups:
        p = g.get("profile", {})
        lines.append(f"- **{p.get('name')}** (`{g['id']}`): {p.get('description') or 'no description'}")
    lines.append("")

    # Apps
    lines.append("## Applications\n")
    for app in tenant.apps:
        oidc = app.get("_oidc", {})
        ap = app.get("_auth_policy", {})
        pe = app.get("_enrollment_policy", {})
        lines.append(f"### {app.get('label')} (`{app['id']}`)")
        lines.append(f"- Status: {app.get('status')} | Mode: {app.get('signOnMode')}")
        lines.append(f"- initiate_login_uri: `{oidc.get('initiate_login_uri') or 'none'}`")
        lines.append(f"- redirect_uris: {oidc.get('redirect_uris', [])}")
        lines.append(f"- grant_types: {oidc.get('grant_types', [])}")
        if ap:
            lines.append(f"- Auth Policy: **{ap.get('name')}** (`{ap.get('id')}`)")
            for r in ap.get("_rules", []):
                a = r.get("actions", {}).get("appSignOn", {})
                v = a.get("verificationMethod", {})
                conds = (r.get("conditions") or {}).get("people", {}).get("groups", {})
                lines.append(f"  - Rule `{r['name']}` (p{r['priority']}): access={a.get('access')}, {v.get('factorMode')} | groups={conds.get('include','[]')}")
        if pe:
            ev = None
            for r in pe.get("_rules", []):
                ev = r.get("actions", {}).get("profileEnrollment", {}) \
                       .get("activationRequirements", {}).get("emailVerification")
            lines.append(f"- Enrollment Policy: **{pe.get('name')}** | emailVerification={ev}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
@click.option("--env", default="ciam", show_default=True)
@click.pass_context
def cli(ctx, env):
    ctx.ensure_object(dict)
    ctx.obj["env"] = env


async def _discover(env, name, domain):
    api = OktaAPI.from_env(env)
    try:
        return await discover_tenant(api, name, domain)
    finally:
        await api.close()


@cli.command()
@click.argument("name")
@click.option("--domain", "-d", default=None)
@click.option("--output", "-o", type=click.Path(), default=None)
@click.pass_context
def discover(ctx, name, domain, output):
    """Discover all SSO artifacts for a tenant and output as JSON."""
    tenant = asyncio.run(_discover(ctx.obj["env"], name, domain))
    data = {
        "name": tenant.name,
        "domains": tenant.domains,
        "idps": tenant.idps,
        "idp_mappings": tenant.idp_mappings,
        "idp_auto_groups": tenant.idp_auto_groups,
        "routing_rules": tenant.routing_rules,
        "groups": tenant.groups,
        "apps": tenant.apps,
        "auth_policies": tenant.auth_policies,
        "enrollment_policies": tenant.enrollment_policies,
    }
    out = json.dumps(data, indent=2, default=str)
    if output:
        with open(output, "w") as f:
            f.write(out)
        print(f"Saved to {output}")
    else:
        print(out)


@cli.command()
@click.argument("name")
@click.option("--domain", "-d", default=None)
@click.pass_context
def validate(ctx, name, domain):
    """Validate a tenant's SSO configuration against best practices."""
    tenant = asyncio.run(_discover(ctx.obj["env"], name, domain))
    checks = validate_tenant(tenant)

    errors   = [c for c in checks if not c["passed"] and c["severity"] == "error"]
    warnings = [c for c in checks if not c["passed"] and c["severity"] == "warning"]
    passed   = [c for c in checks if c["passed"]]

    print(f"\n{'='*60}")
    print(f"  SSO Validation: {name}")
    print(f"{'='*60}")
    print(f"\n✅ Passed: {len(passed)}  ❌ Errors: {len(errors)}  ⚠️  Warnings: {len(warnings)}\n")

    for c in checks:
        icon = "✅" if c["passed"] else ("❌" if c["severity"] == "error" else ("⚠️ " if c["severity"] == "warning" else "ℹ️ "))
        print(f"  {icon} {c['description']}")
        if not c["passed"] and c["detail"]:
            print(f"       {c['detail']}")

    print()


@cli.command()
@click.argument("name")
@click.option("--domain", "-d", default=None)
@click.option("--output", "-o", type=click.Path(), default=None)
@click.pass_context
def report(ctx, name, domain, output):
    """Generate a full Markdown SSO profile report for a tenant."""
    tenant = asyncio.run(_discover(ctx.obj["env"], name, domain))
    checks = validate_tenant(tenant)
    md = generate_report(tenant, checks)

    if output:
        with open(output, "w") as f:
            f.write(md)
        print(f"Report saved to {output}")
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_name = name.lower().replace(" ", "_")
        path = os.path.join(OUTPUT_DIR, f"tenant_sso_{safe_name}_{date_str}.md")
        with open(path, "w") as f:
            f.write(md)
        print(f"\n📋 Report saved: {path}\n")
        # Also print validation summary to stdout
        errors = [c for c in checks if not c["passed"] and c["severity"] == "error"]
        warnings = [c for c in checks if not c["passed"] and c["severity"] == "warning"]
        passed = [c for c in checks if c["passed"]]
        print(f"✅ {len(passed)} passed  ❌ {len(errors)} errors  ⚠️  {len(warnings)} warnings\n")
        for c in checks:
            if not c["passed"]:
                icon = "❌" if c["severity"] == "error" else "⚠️ "
                print(f"  {icon} {c['description']}: {c['detail']}")


if __name__ == "__main__":
    cli()
