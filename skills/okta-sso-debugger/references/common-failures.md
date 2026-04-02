# Common SSO Failure Modes

Catalog of real failures encountered while debugging Lucerna tenant SSO configurations. Each entry includes symptoms, root cause, diagnosis steps, and fix.

**Check F0 first. It is the most common root cause and wastes the most time when missed.**

---

## F0: trustClaims: true on IdP — The Silent Killer

**Symptoms:**
- UNSATISFIABLE on every login for federated users
- System log `policy.evaluate_sign_on` target is **Okta Dashboard** (not the Leap app)
- System log references "Authenticator Enrollment Policy / Default Policy"
- All access policy settings look correct
- All enrollment settings look correct
- Nothing else explains the failure

**Root cause:** The IdP's `policy.trustClaims` is `true`. This is NOT visible in the Okta admin UI — API only.

When `trustClaims: true`, OIE re-evaluates the IdP authentication through the full pipeline: Global Session Policy → Dashboard access policy → Default MFA enrollment policy. The Default enrollment policy requires `okta_password: REQUIRED` (a system constraint that cannot be changed). JIT-provisioned federated users have no password enrolled → UNSATISFIABLE.

When `trustClaims: false`, OIE accepts the IdP assertion and routes directly to the target app's access policy via the Relay State.

**Diagnosis:**
```bash
uv run python -m src.okta.okta_api --env ciam get /api/v1/idps/{idpId}
# Check: policy.trustClaims
```

Also check the system log `policy.evaluate_sign_on` event — if the target is "Okta Dashboard" instead of the Leap app, this is almost certainly the cause.

**Fix:**
```bash
# Fetch IdP, set trustClaims to false, PUT back
```

**Prevention:** When creating any new SAML2 IdP, always verify `trustClaims: false` via API after creation. All working Lucerna IdPs (Sanitas, Carle) have this set to `false`.

**History:** This was the root cause of the Carle Health SSO failure (2026-03-31 to 2026-04-01). Multiple rounds of access policy, enrollment policy, and constraint changes were attempted before discovering this single boolean. It caused ~3 hours of debugging across multiple sessions.

---

## F1: UNSATISFIABLE — Constraint Cannot Be Met

**Symptoms:**
- User sees "invalid username & password" or generic login error
- Okta system log shows `outcome.reason: "UNSATISFIABLE"` or `"INVALID_CREDENTIALS"`
- Event type: `policy.evaluate_sign_on`

**Root cause:** The access policy rule's ASSURANCE constraint requires an authenticator type the user doesn't have enrolled.

**Common scenarios:**
1. Constraint requires `password` only, but JIT user only has `email` enrolled
2. Constraint is empty `{}` — OIE interprets this ambiguously and fails
3. User was manually created without any factor enrollment

**Diagnosis:**
```bash
# Check user's enrolled factors
uv run python -m src.okta.okta_api --env ciam get /api/v1/users/{userId}/factors

# Check what the access policy rule requires
uv run python -m src.okta.tenant_sso validate "Tenant Name" --domain example.com
```

**Fix:** Set constraint to `knowledge: { required: true, types: ["password", "email"] }` — accepts either factor.

**Prevention:** The `tenant_sso.py` validator checks `auth_1fa_sso_rule` but does not yet inspect constraint types. Consider adding a check for `email` in constraint types.

---

## F2: Wrong Group in Access Policy vs IdP Auto-Assign

**Symptoms:**
- New users from external IdP can't log in
- Existing users (manually assigned to correct group) work fine
- Okta system log shows access policy catch-all DENY

**Root cause:** The IdP auto-assign groups and the access policy group conditions reference different groups.

Example: IdP assigns `leap-tenant-prod-carle Access Group` but access policy Rule 0 requires `Carle Health SSO Users`.

**Diagnosis:**
```bash
# Run discovery to see which groups the IdP auto-assigns
uv run python -m src.okta.tenant_sso discover "Tenant Name" --domain example.com

# In the output, compare:
# - IdP policy.provisioning.groups → what gets auto-assigned
# - Auth policy rules → what group conditions they check
```

**Fix:** Add the access-policy-required group to the IdP's auto-assign group list.

**Prevention:** The `tenant_sso.py` validator checks `auth_1fa_sso_rule` to confirm a 1FA rule exists for tenant groups. Cross-reference the specific group IDs in IdP provisioning with those in the auth policy.

---

## F3: IDP Discovery Rule Misconfiguration

**Symptoms:**
- User sees native Okta login (password box) instead of being redirected to their corporate IdP
- User from Domain A gets routed to Domain B's IdP
- Lucerna staff can't access a tenant app after rule changes

**Root cause variants:**

### F3a: Missing or inactive routing rule
No rule matches the user's email domain for the target app. They fall to the Default Rule (native Okta login).

### F3b: Wrong app exclusion
A rule was modified to exclude a specific app, breaking a legitimate login path. Example: excluding the Carle app from the Lucerna workforce SSO rule prevented Lucerna staff from accessing Carle's Leap instance.

### F3c: Priority ordering conflict
A broad rule at a higher priority intercepts users before a more specific rule can match.

**Diagnosis:**
```bash
# List all IDP discovery rules and their priorities
uv run python -m src.okta.okta_api --env ciam get "/api/v1/policies?type=IDP_DISCOVERY"
# Then for each policy ID:
uv run python -m src.okta.okta_api --env ciam get "/api/v1/policies/{policyId}/rules"
```

**Fix:** Depends on variant. Always verify the full priority chain after changes.

---

## F4: Profile Enrollment Email Verification Prompt

**Symptoms:**
- New federated SSO user sees "verify your email" screen after IdP authentication
- User gets confused, thinks something is wrong, abandons login
- Eventually times out or enters wrong verification code

**Root cause:** The app's profile enrollment policy has `emailVerification: true`. This is correct for self-service signup but wrong for federated SSO where the IdP already verified identity.

**Diagnosis:**
```bash
uv run python -m src.okta.tenant_sso validate "Tenant Name" --domain example.com
# Check: enrollment_no_email validation result
```

**Fix:** Set `activationRequirements.emailVerification: false` in the enrollment policy rule.

---

## F5: Missing App Assignment

**Symptoms:**
- User exists in Okta, is in the correct group, has correct factors
- Still can't access the app
- System log shows no access policy evaluation (user never reaches it)

**Root cause:** The user is not assigned to the OIDC application (directly or via group assignment).

**Diagnosis:**
```bash
# Check user's app assignments
uv run python -m src.okta.okta_api --env ciam get "/api/v1/users/{userId}/appLinks"
```

**Fix:**
```bash
# Assign user to app
POST /api/v1/apps/{appId}/users  {"id": "{userId}", "scope": "USER"}
```

---

## F6: Missing Profile Mapping (email)

**Symptoms:**
- User is JIT-provisioned but has no email factor enrolled
- Access policy with email constraint fails (UNSATISFIABLE)
- User profile in Okta shows blank email

**Root cause:** The IdP → Okta profile mapping doesn't include an `email` field mapping. The SAML assertion may carry email in a non-standard attribute name.

**Diagnosis:**
```bash
uv run python -m src.okta.tenant_sso validate "Tenant Name" --domain example.com
# Check: mapping_email validation result
```

**Fix:** Add or correct the email mapping in the IdP's profile mapping configuration.

---

## F7: Account Linking Failure — Duplicate Users

**Symptoms:**
- User has two Okta accounts (one pre-provisioned, one JIT-created)
- Login works but user lands in wrong tenant or sees wrong data
- Or: login fails because the JIT account isn't assigned to the app

**Root cause:** The IdP's `accountLink.action` is not `AUTO`, or the `subject.userNameTemplate` produces a username that doesn't match the pre-existing account's login.

**Diagnosis:**
```bash
# Search for duplicate users
uv run python -m src.okta.okta_api --env ciam get "/api/v1/users?search=profile.email eq \"user@example.com\""
```

**Fix:** Ensure `accountLink.action: "AUTO"` and verify `subject.userNameTemplate` produces the same format as existing usernames (typically `String.toLowerCase(idpuser.subjectNameId)`).

---

## F8: Multi-Domain Tenant — New Domain Not in Routing Rule

**Symptoms:**
- Existing domains work fine for SSO
- Users from a newly added email domain see native Okta login instead of IdP redirect

**Root cause:** The IDP Discovery routing rule's domain patterns don't include the new domain. This is common with Sanitas (which uses both `mysanitas.com` and `sanitas.com`).

**Diagnosis:**
```bash
uv run python -m src.okta.tenant_sso discover "Tenant Name" --domain newdomain.com
# If no routing rules match, the domain isn't configured
```

**Fix:** Add the new domain pattern to the existing routing rule's `conditions.userIdentifier.patterns` array.

**Note:** Also update the Leap app configuration to recognize the new domain (this is a Leap-side change, not Okta).

---

## F9: Expired or Invalid API Token

**Symptoms:**
- Debugging scripts return HTTP 401
- Token worked previously but no longer does

**Root cause:** Okta API tokens expire after 30 days of non-use, or an admin revoked the token.

**Fix:** Create a new token. See `references/okta-token-setup.md` for scoped read-only token creation.

---

## Debugging Priority Order

When a user reports "I can't log in," investigate in this order:

1. **What domain?** → determines which IDP Discovery rule should fire
2. **System log events** → the `outcome.reason` tells you exactly what failed
3. **User exists?** → search by email
4. **User status?** → ACTIVE, PROVISIONED, STAGED, SUSPENDED, DEPROVISIONED
5. **Enrolled factors?** → must have factors matching the access policy constraint
6. **Group membership?** → must be in the group required by the access policy ALLOW rule
7. **App assignment?** → must be assigned to the OIDC app
8. **IDP Discovery?** → is the user hitting the right routing rule?
9. **Profile mapping?** → are email/login mapped correctly from the IdP?
