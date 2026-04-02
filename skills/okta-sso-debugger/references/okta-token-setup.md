# Creating an Okta API Token for SSO Debugging

Guide the user through creating a scoped API token for the CIAM Okta org (`hdp.okta.com`). The goal is a token with the minimum permissions needed for read-only SSO debugging.

## Token Types

### Option A: Read-Only Admin Token (Recommended for debugging)

Create a token scoped to a **Read-Only Administrator** role. This allows querying all SSO configuration objects without risk of accidental modification.

**Steps:**
1. Log into `hdp.okta.com` as a Super Admin
2. Navigate to **Security → API → Tokens**
3. Click **Create Token**
4. Name it descriptively: `sso-debug-readonly-YYYY-MM` (include date for rotation tracking)
5. The token inherits the creating admin's permissions

**Important:** The token inherits the *current user's* role. To create a truly read-only token:
- Either: create it while logged in as a Read-Only Admin
- Or: create a service account with Read-Only Admin role, log in as that account, and create the token

### Option B: Scoped OAuth2 Token (More secure, more complex)

For production automation, use OAuth2 client credentials with specific scopes:

Required scopes for SSO debugging (all read-only):
- `okta.users.read` — user lookup, factor enrollment, group membership
- `okta.apps.read` — application configuration
- `okta.policies.read` — access policies, enrollment policies, IDP discovery
- `okta.idps.read` — identity provider configuration
- `okta.groups.read` — group details
- `okta.logs.read` — system log events

This approach requires creating an OAuth2 service app in Okta, which is more setup but more secure for long-term use.

### Option C: Temporary Super Admin Token (Quick and dirty)

For immediate debugging emergencies:
1. Use an existing Super Admin session
2. Create a token, do the debugging, then **immediately revoke** the token
3. Name it `temp-sso-debug-DELETEME`

## Configuring the Token for lucerna-infra Scripts

The `OktaAPI` client reads credentials from environment variables as JSON:

```bash
# In .env file:
okta_ciam='{"orgUrl": "https://hdp.okta.com", "token": "00abc123..."}'

# For workforce Okta (if needed):
okta_workforce='{"orgUrl": "https://lucernahealth.okta.com", "token": "00xyz789..."}'
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv(override=True)

from src.okta.okta_api import OktaAPI
api = OktaAPI.from_env("ciam")
```

## Token Rotation

Okta SSWS tokens expire after **30 days of non-use**. If the token returns 401:
1. The token has expired from inactivity, or
2. An admin revoked it

Create a new one following the steps above. No way to extend or reactivate an expired token.

## Verifying the Token Works

```bash
cd ~/dev/lucerna-infra
uv run python -m src.okta.okta_api --env ciam get /api/v1/org
```

Expected: JSON with org details. If 401: token is invalid or expired.

## Security Notes

- Never commit tokens to git (`.env` is gitignored)
- Rotate tokens monthly or after each debugging session
- Prefer read-only tokens; only escalate to write access when the user needs to make a specific change
- The skill workflow is designed so that **Claude reads and diagnoses**, while the **user makes changes** in the Okta admin UI
