# Okta Identity Engine — SSO Concepts That Bite

This reference covers OIE behaviors that are non-obvious and have caused production SSO failures at Lucerna. These are the concepts an engineer MUST understand before debugging tenant SSO.

## trustClaims — The Most Dangerous Boolean in Okta

**`policy.trustClaims`** on an IdP controls whether OIE re-evaluates the authentication context claims from the external IdP through the full policy pipeline.

- **`false` (correct):** OIE accepts the IdP assertion at face value. The flow routes directly to the target app (via Relay State) and evaluates only that app's access policy.
- **`true` (dangerous for federated SSO):** OIE re-evaluates the authentication through Global Session Policy → Okta Dashboard access policy → Default MFA enrollment policy. The Default enrollment policy requires `okta_password: REQUIRED` (immutable system constraint). JIT-provisioned users have no password → **UNSATISFIABLE**.

### Why this is so dangerous

1. **Not visible in the Okta admin UI** — can only be checked via API
2. **The symptoms look like an access policy problem** — the UNSATISFIABLE error is identical to a constraint mismatch, leading investigators to chase access policy settings, enrollment policies, and constraint types instead
3. **The Default MFA enrollment policy's password requirement CANNOT be changed** — Okta enforces `okta_password: REQUIRED` on the Default Policy as a system constraint
4. **Custom enrollment policies make it WORSE** — setting `okta_password: NOT_ALLOWED` on a custom policy creates an irreconcilable conflict between the custom policy and other policies in the chain

### How to check

```bash
uv run python -m src.okta.okta_api --env ciam get /api/v1/idps/{idpId}
# Look for: policy.trustClaims — must be false
```

### How to identify in system logs

When `trustClaims: true`, the `policy.evaluate_sign_on` event's target will be **"Okta Dashboard"** instead of the Leap app. This is the smoking gun.

---

## ASSURANCE Type Evaluates Enrolled Factors, Not Session Method

The second most important thing to understand about OIE access policies.

When an access policy rule uses `verificationMethod.type: "ASSURANCE"`, the constraint evaluates the user's **enrolled authenticator list** — NOT the authentication method used in the current session.

```json
{
  "factorMode": "1FA",
  "constraints": [
    {
      "knowledge": {
        "required": true,
        "types": ["password", "email"]
      }
    }
  ]
}
```

This means: "user must have at least one of password OR email **enrolled** as an authenticator." It does NOT mean the user must enter a password or click an email link right now.

### Why this matters for federated SSO

JIT-provisioned users from external IdPs (Azure AD, etc.) typically:
- Have **email** factor enrolled (Okta auto-enrolls during JIT)
- Do **NOT** have a password (they authenticate via their corporate IdP)

If the constraint only lists `"types": ["password"]`, JIT users with only email enrolled will get **UNSATISFIABLE** — the policy cannot be satisfied and login fails silently.

### The fix

Always include both `"password"` and `"email"` in the types array for rules that cover federated SSO users:

```json
"knowledge": { "required": true, "types": ["password", "email"] }
```

This works for both:
- SSO users (email enrolled only) — satisfied by email
- Direct Okta users (password enrolled) — satisfied by password

## IDP Discovery Policy — Priority-Ordered Rules

IDP Discovery fires **before** authentication. It determines which identity provider handles the user based on their email domain and the target application.

Rules evaluate in **priority order** (lowest number = highest priority). First match wins.

### Rule anatomy

Each rule has:
- **Domain patterns**: email suffixes to match (e.g., `carle.com`, `mysanitas.com`)
- **App conditions**: optionally restrict to specific apps (by app ID)
- **Provider**: which IdP to route to (external SAML2, or Okta native login)
- **Priority**: evaluation order

### Multi-domain tenants

Some tenants have multiple email domains (e.g., Sanitas has `mysanitas.com` AND `sanitas.com`). A single routing rule can contain multiple domain patterns. When discovering SSO artifacts, always check for additional domains in routing rules — the `tenant_sso.py` discovery tool does this automatically.

### Common mistakes

1. **Excluding an app from a rule when you shouldn't**: If Lucerna staff access a tenant app via workforce SSO (Rule 1), excluding that app from Rule 1 breaks their login path.
2. **Wrong priority order**: A catch-all rule at priority 1 will intercept users meant for later rules.
3. **Forgetting the Default Rule**: The default rule (highest priority number) typically routes to native Okta login. Anyone not matching a specific rule lands here.

## JIT Provisioning (Just-In-Time)

When a user authenticates via an external IdP for the first time, Okta can automatically create their account. This is controlled by the IdP's `policy.provisioning` settings.

### Key settings

| Setting | Expected Value | Why |
|---------|---------------|-----|
| `action` | `AUTO` | Automatically provision on first login |
| `profileMaster` | `true` | External IdP owns profile attributes |
| `accountLink.action` | `AUTO` | Link to existing Okta user if username matches |

### What happens during JIT

1. Okta receives SAML assertion from external IdP
2. Maps username via `subject.userNameTemplate` (typically `String.toLowerCase(idpuser.subjectNameId)`)
3. Searches for existing Okta user with matching username
4. If found: links session. If not: creates new user.
5. Auto-assigns groups configured in the IdP's `groups` setting
6. Enrolls email factor (NOT password — user authenticates via external IdP)

### Auto-assign groups — critical

The IdP configuration specifies which groups to auto-assign to JIT-provisioned users. If the **access policy** requires membership in a specific group (e.g., "Carle Health SSO Users"), that group MUST be in the IdP's auto-assign list. Otherwise, new users get provisioned but immediately fail the access policy check.

This was the root cause of the Carle SSO failure: the IdP assigned users to the "Access Group" but the access policy required "SSO Users" — a different group.

## Access Policies — Rule Evaluation

Access policies are bound to applications. When a user reaches the app after IDP Discovery and authentication, the access policy evaluates rules in priority order.

### Rule structure

Each rule has:
- **Group conditions**: which Okta groups must the user be in
- **Access decision**: ALLOW or DENY
- **Factor mode**: 1FA or 2FA
- **Constraints**: ASSURANCE requirements (see above)

### Catch-all rule

Every access policy has a catch-all rule (typically priority 99) with no group conditions. This is usually set to **DENY** with an impossible constraint (device-bound possession). Any user not matching a specific rule hits this and is denied.

### Implications

If a user is not in the correct group for any ALLOW rule, they fall through to the catch-all DENY. The error may appear as "access denied" or sometimes a confusing "invalid username & password" message.

## Profile Enrollment Policies

These control what happens when a new user is being provisioned. The key setting is `emailVerification`:

- `false`: No email verification required (correct for federated SSO — the IdP already verified identity)
- `true`: Okta sends a verification email before completing enrollment (wrong for SSO — causes confusing UX)

For tenant SSO apps, enrollment policy MUST have `emailVerification: false`.

## Profile Mappings (IdP to Okta User)

When an external IdP sends a SAML assertion, Okta maps claim attributes to Okta user profile fields. Critical mappings:

| Okta Field | Source | Notes |
|------------|--------|-------|
| `login` | `idpuser.subjectNameId` or `idpuser.email` | Must match for account linking |
| `email` | `idpuser.email` or `idpuser.subjectNameId` | Required for email factor enrollment |
| `firstName` | Varies by IdP | Profile display |
| `lastName` | Varies by IdP | Profile display |

Missing `email` mapping prevents email factor enrollment, which then causes ASSURANCE constraint failures.

## The Lucerna SSO Architecture

All Leap tenant apps use Okta CIAM (`hdp.okta.com`) as the identity broker:

```
User → Tenant Leap App → Okta CIAM → IDP Discovery → External IdP (Azure AD)
                                                     ↓
                                               SAML assertion
                                                     ↓
                                          Okta CIAM JIT provision
                                                     ↓
                                          Access Policy evaluation
                                                     ↓
                                          OIDC token → Leap App
```

Lucerna staff access tenant apps via a different path:
```
Lucerna User → Tenant Leap App → Okta CIAM → IDP Discovery → Workforce Okta SSO
```

Both paths converge at the same access policy evaluation step.
