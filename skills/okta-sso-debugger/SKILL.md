---
name: okta-sso-debugger
description: This skill should be used when debugging, reviewing, or documenting Okta CIAM SSO configurations for Lucerna Health Leap tenants. Triggers on tenant SSO issues, login failures, Okta debugging, IDP discovery problems, access policy troubleshooting, JIT provisioning issues, or when asked to document how a tenant's SSO works. Also triggers when onboarding a new tenant's SSO or adding a new email domain to an existing tenant.
---

# Okta SSO Debugger

Diagnose, validate, and document Okta CIAM SSO configurations for Leap tenant applications. This skill encodes lessons from production SSO failures and provides a systematic workflow for finding and fixing configuration problems.

**Key principle:** Claude reads and diagnoses. The user makes all changes in the Okta admin UI or via approved scripts with `--live` flags.

## Prerequisites

This skill bundles its own scripts in `scripts/`. No external repo required.

Scripts use PEP 723 inline metadata — `uv run` handles dependencies automatically. No manual install needed.

### Getting the Okta API Token

**Always start by testing the existing token:**
```bash
uv run scripts/okta_api.py --env ciam get /api/v1/org
```

If this returns org details → token works, proceed to the workflow.

If this returns **401** or errors about missing env vars, the token is expired or not configured. Walk the user through these steps:

**Step 1 — Create token in Okta admin UI:**
1. Go to `https://hdp.okta.com` → sign in as admin
2. Navigate to **Security → API → Tokens**
3. Click **Create Token**
4. Name it `sso-debug-YYYY-MM` (e.g., `sso-debug-2026-04`)
5. **Copy the token value immediately** — it's only shown once

**Step 2 — Configure the token:**

The scripts read from environment variables. Either export directly or create a `.env` file in the working directory:
```bash
okta_ciam={"orgUrl": "https://hdp.okta.com", "token": "PASTE_TOKEN_HERE"}
```

The token inherits the creating admin's permissions. For read-only debugging, ideally create the token while logged in as a Read-Only Administrator. For quick debugging, a Super Admin token works — just revoke it after the session.

**Step 3 — Verify:**
```bash
uv run scripts/okta_api.py --env ciam get /api/v1/org
```

**Token expiration:** Okta SSWS tokens expire after **30 days of non-use**. If the team debugs SSO infrequently, expect to create a new token each session.

For more detail on token types and security, read `references/okta-token-setup.md`.

## The #1 Thing to Check First

**Before anything else**, verify the tenant IdP's `trustClaims` setting:

```bash
uv run scripts/okta_api.py --env ciam get /api/v1/idps/{idpId}
# Look for: policy.trustClaims — MUST be false
```

When `trustClaims` is `true`, OIE re-evaluates the IdP authentication through the entire policy pipeline — including the Okta Dashboard's access policy and the Default MFA enrollment policy (which requires password enrollment). JIT-provisioned federated users have no password → **UNSATISFIABLE** on every login.

This setting is **not visible in the Okta admin UI**. It can only be checked and changed via API. It is the single most common root cause of "unable to sign in" for federated SSO users.

To fix:
```bash
uv run scripts/okta_api.py --env ciam get /api/v1/idps/{idpId} > /tmp/idp.json
# Edit /tmp/idp.json: set policy.trustClaims to false, remove _links
uv run scripts/okta_api.py --env ciam put /api/v1/idps/{idpId} --file /tmp/idp.json
```

## Workflow

Two distinct modes. Determine which applies:

### Mode A: "A specific user can't log in"

This is a targeted investigation. Follow this sequence — do NOT skip to later steps.

**Step 1 — Check trustClaims (90 seconds, catches the #1 root cause):**
```bash
uv run scripts/tenant_sso.py discover "Tenant Name" --domain example.com 2>&1 | grep "Identity Providers"
uv run scripts/okta_api.py --env ciam get /api/v1/idps/{idpId}
# policy.trustClaims MUST be false
```
If `true` → fix it → test again → likely solved.

**Step 2 — Check system logs for the failing user:**
```bash
uv run scripts/okta_api.py user-logs "user@example.com" --days 3
```
Look at the `policy.evaluate_sign_on` event:
- Target is **Okta Dashboard** → `trustClaims` issue (back to Step 1)
- Target is **the Leap app** → access policy issue (continue to Step 3)
- No events at all → user may not be reaching Okta (check IDP Discovery, Azure config)

**Step 3 — Check user state:**
```bash
uv run scripts/okta_api.py user "user@example.com"
uv run scripts/okta_api.py user-factors "user@example.com"
uv run scripts/okta_api.py user-groups "user@example.com"
```
Cross-reference: user must be in the group required by the access policy's ALLOW rule, and must have a factor matching the constraint (typically `email` for JIT users).

**Step 4 — Check access policy constraints:**
Run full validation if Steps 1-3 don't reveal the issue:
```bash
uv run scripts/tenant_sso.py validate "Tenant Name" --domain example.com
```

**Step 5 — Trace the full path.** Read `references/oie-sso-concepts.md` and `references/common-failures.md` to match the failure to a known pattern.

### Mode B: "Review/setup/document tenant SSO"

This is a holistic assessment. Covers initial setup, ongoing health, and documentation.

#### B1: Discovery & Validation

```bash
# Discovery: find all SSO artifacts for a tenant
uv run scripts/tenant_sso.py discover "Tenant Name" --domain example.com

# Validation: run 22 best-practice checks
uv run scripts/tenant_sso.py validate "Tenant Name" --domain example.com

# Full report: markdown with all details + validation
uv run scripts/tenant_sso.py report "Tenant Name" --domain example.com
```

Cross-reference any failures against `references/common-failures.md` for known root causes and fixes.

#### B2: Documentation

After understanding the configuration, generate a comprehensive SSO flow document.

**Output location:** Obsidian vault at `/Users/carl/cloud/gdrive/obsidian-vault-carlkibler/Lucerna/`

**Document template — include all of these sections:**

1. **Overview** — which email domains, which Leap instance, which IdP
2. **Key IDs** — table of Okta object IDs (App, IdP, Access Policy, Groups, IDP Discovery Policy)
3. **Login Flow** — step-by-step walkthrough of what happens when a user logs in
4. **Access Policy Rules** — table with priority, rule name, group condition, decision, constraint
5. **IDP Discovery Rules** — which domains route to which IdPs
6. **JIT Provisioning** — what happens on first login (groups, factors, profile mastering)
7. **Lucerna Staff Path** — how internal users access this tenant's app
8. **Troubleshooting Checklist** — tenant-specific debugging steps with exact API commands
9. **Change Log** — dated record of configuration changes and why

**Naming convention:** `{tenant-slug}-sso-flow.md` (e.g., `carle-sso-flow.md`, `sanitas-sso-flow.md`)

#### B3: Fixing Issues

When issues are identified, present findings to the user with:
1. **What's wrong** — specific misconfiguration identified
2. **Why it's wrong** — reference the OIE concept or common failure mode
3. **What to change** — exact setting, where in the UI, what value
4. **Risk assessment** — will this change affect other tenants or users?

**Never make write API calls without explicit user approval.**

## Key Okta CIAM Details

- **Org:** `hdp.okta.com`
- **Environment variable:** `okta_ciam` in `.env`
- **All tenant Leap apps** are OIDC apps in this org
- **Workforce Okta** (`lucernahealth.okta.com`) is separate — Lucerna staff authenticate there first, then federate into CIAM

## Reference Files

| File | When to read |
|------|-------------|
| `references/oie-sso-concepts.md` | Before debugging — understand trustClaims, ASSURANCE, JIT, IDP Discovery |
| `references/common-failures.md` | When you find a specific failure — look up the failure mode |
| `references/okta-token-setup.md` | When the API token is missing or expired (401) |

## Bundled Scripts

All scripts are in `scripts/` with PEP 723 inline deps. Run with `uv run` — no install step needed.

| Script | Purpose |
|--------|---------|
| `scripts/okta_api.py` | Okta API client + CLI with user/factor/log/group/policy commands |
| `scripts/tenant_sso.py` | Discover, validate (22 checks), and report on tenant SSO config |

### okta_api.py CLI Commands

| Command | Usage | Purpose |
|---------|-------|---------|
| `user` | `user "email@example.com"` | Look up user by email (ID, status, profile) |
| `user-groups` | `user-groups "email@example.com"` | List group membership |
| `user-factors` | `user-factors "email@example.com"` | List enrolled authenticator factors |
| `user-logs` | `user-logs "email@example.com" --days 7` | Recent system log events (formatted) |
| `app-policies` | `app-policies {appId}` | Show auth + enrollment policies for an app |
| `policy` | `policy {policyId}` | Show policy and all its rules |
| `get` | `get /api/v1/...` | Raw GET with pagination |
| `post` | `post /api/v1/... --file body.json` | POST JSON body |
| `put` | `put /api/v1/...` | PUT (e.g., assign policy) |

All commands accept `--env ciam` (default) or `--env workforce`.

### tenant_sso.py Validation Checks (22)

Key checks that catch the most common SSO failures, listed by priority:

| Check | What it catches |
|-------|----------------|
| `idp_trust_claims` | **#1 root cause.** `trustClaims: true` causes UNSATISFIABLE for all JIT users on IdP-initiated flows |
| `auth_constraint_email` | Constraint doesn't accept email factor — JIT users will get UNSATISFIABLE |
| `auth_constraint_not_empty` | Empty constraints cause UNSATISFIABLE in OIE |
| `idp_groups_match_policy` | IdP auto-assign groups don't include the group required by access policy |
| `idp_no_deprecated` | Deprecated IdP still ACTIVE (cleanup candidate) |
| `enrollment_no_email` | Email verification required on enrollment (warning — JIT bypasses this) |

## Multi-Domain Tenant Considerations

Some tenants use multiple email domains (e.g., Sanitas uses 7 domains). When working with multi-domain tenants:

1. The `tenant_sso.py` discovery tool automatically finds additional domains from routing rules
2. Verify ALL domains are in the IDP Discovery routing rule's pattern list
3. Verify the Leap application itself recognizes all domains (Leap-side configuration, not Okta)
4. When a new domain is added, both Okta routing rules AND Leap settings need updating
