"""
mea_token_test.py - get an Entra ID token for the MEA proxy and show what is in it.

Calls Entra ID only. It does NOT call MuleSoft or MEA, so no account is touched.
Uses the same certificate login as mea_disable.py (put both files in the Escalation folder).

One-time setup (also needed by mea_disable.py):
    py -m pip install msal cryptography

Run:
    py mea_token_test.py            show the token's claims
    py mea_token_test.py --raw      also print the token, to paste into Postman as {{jwt}}

The token is a short-lived bearer credential (about an hour): don't save it in
files, chats or git.
"""
import argparse
import base64
import json
import sys
from datetime import datetime

import mea_disable as m

# ── Non-prod values (Ashish / Brindha, 11/6/2026) ──
m.TENANT_ID = "e84bb675-81b1-4f49-985b-3e2d77c6c94d"
m.CLIENT_ID = "5035d019-f182-4373-85c9-bcb4040ea139"
# PG&E pattern (MRAD wiki "Azure AD Client OAuth Client Authentication"): the app requests
# a token for its OWN App ID URI, so aud = api://<our client ID>.
# The api:// form needs an Application ID URI on the app (AADSTS500011 until Ashish sets it).
# The bare client ID works without one. MuleSoft accepts both (Brindha, 11/6).
m.SCOPE     = "5035d019-f182-4373-85c9-bcb4040ea139/.default"
EXPECTED_AUD = ["5035d019-f182-4373-85c9-bcb4040ea139",
                "api://5035d019-f182-4373-85c9-bcb4040ea139"]   # MuleSoft audience values


def claims(token):
    body = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", action="store_true", help="print the token itself (for Postman)")
    args = ap.parse_args()

    print(f"Tenant: {m.TENANT_ID}\nClient: {m.CLIENT_ID}\nScope:  {m.SCOPE}\n")
    try:
        token = m.entra_token()
    except SystemExit as e:
        msg = str(e)
        print(msg)
        if "AADSTS500011" in msg:
            print("\n-> Entra has no app with that scope/App ID URI. Brindha's audience needs a "
                  "matching app registration (Ashish), or a different scope.")
        elif "AADSTS700027" in msg or "AADSTS700024" in msg:
            print("\n-> Certificate not accepted: check it is uploaded on the app registration "
                  "and the .crt/.key pair matches.")
        elif "AADSTS65001" in msg or "AADSTS501051" in msg:
            print("\n-> Our app isn't granted access to that API yet (Ashish to grant/consent).")
        sys.exit(1)

    c = claims(token)
    print("Got a token. Key claims:")
    for k in ("aud", "iss", "appid", "azp", "roles", "ver", "tid"):
        if k in c:
            print(f"  {k:6} = {c[k]}")
    print(f"  expires = {datetime.fromtimestamp(c['exp']):%Y-%m-%d %H:%M:%S} (local)")

    ok = c.get("aud") in EXPECTED_AUD
    print(f"\naud matches what MuleSoft checks: {'YES' if ok else 'NO'}")
    if not ok:
        print(f"  MuleSoft expects: {EXPECTED_AUD}\n  Token has:        {c.get('aud')}\n"
              "  -> send both to Brindha; one side has to change.")

    if args.raw:
        print(f"\nToken (paste into Postman {{{{jwt}}}}, expires in about an hour):\n{token}")


if __name__ == "__main__":
    main()
