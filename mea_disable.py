"""
mea_disable.py - submit the recertification disable list to MEA (SailPoint) through the
MuleSoft proxy.

  Input   : disable_list_<date>.csv written by escalation_notify.py (column CorpID), or any
            CSV/one-ID-per-line file given with --input.
  Auth    : Entra ID client credentials with a certificate (JWT client assertion) -> bearer
            token -> MuleSoft proxy. MuleSoft passes the body to SailPoint unchanged.
  Request : POST {"workflowArgs": {"users": "AB12,CD34", "requestedBy": <LAN ID>,
                                   "certificationID": <campaign ref>}}
            One request per run with every user (BATCH_SIZE = 0). MEA rule: 5 or fewer users
            are disabled automatically; more than 5 creates approval work items for our team.
  Result  : the launch returns a requestID only (the workflow runs afterwards). Completion is
            confirmed by MEA's notification email / MEA link. Every request and response is
            logged to mea_output/ for evidence, and a summary goes to NOTIFY_TO.

Run by hand:   py mea_disable.py --input disable_list_20261207.csv
From escalation_notify.py:  DISABLE_HANDOFF = "command"
                            DISABLE_COMMAND = ["py", r"<path>\\mea_disable.py", "--input", "{file}"]
Exit code 0 = submitted (or dry run), 1 = failed - escalation_notify treats non-zero as failure.

Requires: py -m pip install msal requests cryptography
"""
import argparse
import csv
import json
import os
import re
import smtplib
import sys
import traceback
from datetime import datetime
from email.mime.text import MIMEText
from html import escape
from pathlib import Path

import requests

# ═══════════════════════════════ CONFIG ═══════════════════════════════
DRY_RUN          = True    # True = build and log the request, call nothing. Default until tested.

# ── Environment: pick one; each has its own Entra app, certificate and MuleSoft URL ──
# None of these values are secrets (IDs and URLs). The only secret is the private .key
# file: it stays on the machine, never in git. Set MEA_CERT_FILE / MEA_KEY_FILE env vars
# to point at the files on a server instead of these defaults.
ENVIRONMENT      = "nonprod"   # "nonprod" (MuleSoft QA -> SailPoint QA) | "prod"
PROFILES = {
    "nonprod": {   # QA tested 11/9/2026 (KXYB, DUL8 disabled). Entra app: Ashish; JWT policy: Brindha
        "MULESOFT_URL": "https://api-ch-q.ss.pge.com/mea-udn-proxy-api/v1/accountdisable",   # QA (dev was api-ch-d.nonprod)
        "TENANT_ID":    "e84bb675-81b1-4f49-985b-3e2d77c6c94d",
        "CLIENT_ID":    "5035d019-f182-4373-85c9-bcb4040ea139",   # NPS Firewall Automation - MEA ... APP-1593 (S2S)
        "SCOPE":        "5035d019-f182-4373-85c9-bcb4040ea139/.default",   # token aud = client ID
        "CERT_FILE":    r"C:\Users\H2PR\certs\mea-lab\nps_fw_mea_lab.crt",
        "KEY_FILE":     r"C:\Users\H2PR\certs\mea-lab\nps_fw_mea_lab.key",
    },
    "prod": {      # TBD - needs its own Entra app registration, certificate and CRQ
        "MULESOFT_URL": "TBD",
        "TENANT_ID":    "TBD",
        "CLIENT_ID":    "TBD",
        "SCOPE":        "TBD",
        "CERT_FILE":    "TBD",
        "KEY_FILE":     "TBD",
    },
}
VERIFY_TLS       = True
TIMEOUT          = 120
AUTH_MODE        = "entra"  # "entra" | "none" (local mock server only)

# ── Request ──
REQUESTED_BY     = "H2PR"   # LAN ID of the person submitting (per MEA)
CERTIFICATION_ID = "NPS-FER-RECERT-2026"   # reference shown on the MEA request
BATCH_SIZE       = 0        # 0 = every user in one request (MEA routes >5 to approval)
MAX_USERS        = 50       # safety stop: refuse a list bigger than this (--force overrides)
ID_COLUMNS       = ["CorpID", "LAN ID", "LANID", "users"]

# ── Mail ──
SENDER_EMAIL     = "h2pr@pge.com"
NOTIFY_TO        = ["h2pr@pge.com", "cybersecuritynetworkprotectionservices@pge.com"]
SMTP_HOST        = "mailhost"
SMTP_PORT        = 25
# ══════════════════════════════════════════════════════════════════════

if ENVIRONMENT not in PROFILES:
    raise SystemExit(f"ENVIRONMENT must be one of {list(PROFILES)}, not {ENVIRONMENT!r}")
_p = PROFILES[ENVIRONMENT]
MULESOFT_URL = _p["MULESOFT_URL"]
TENANT_ID    = _p["TENANT_ID"]
CLIENT_ID    = _p["CLIENT_ID"]
SCOPE        = _p["SCOPE"]
CERT_FILE    = os.environ.get("MEA_CERT_FILE") or _p["CERT_FILE"]
KEY_FILE     = os.environ.get("MEA_KEY_FILE") or _p["KEY_FILE"]

SCRIPT_DIR = Path(__file__).resolve().parent
OUT = SCRIPT_DIR / "mea_output"
LOG_CSV = OUT / "mea_requests.csv"
LANID_RE = re.compile(r"^[A-Za-z0-9]{3,8}$")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def log(msg):
    print(f"{datetime.now():%H:%M:%S} {msg}", flush=True)


# ─────────────────────────────── input ───────────────────────────────

def read_users(path):
    """LAN IDs from the disable-list CSV (CorpID column) or a plain one-per-line file."""
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Input not found: {p}")
    with open(p, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]
    col = next((header.index(c.lower()) for c in ID_COLUMNS if c.lower() in header), None)
    values = [r[col] for r in rows[1:] if len(r) > col] if col is not None else [r[0] for r in rows if r]
    users, bad = [], []
    for v in values:
        v = str(v).strip().upper()
        if not v:
            continue
        (users if LANID_RE.match(v) else bad).append(v)
    if bad:
        raise SystemExit(f"Not valid LAN IDs (fix the file): {bad[:10]}")
    return list(dict.fromkeys(users))          # de-duplicate, keep order


# ─────────────────────────────── auth ────────────────────────────────

def entra_token():
    """Client credentials with a certificate. Thumbprint is read from CERT_FILE."""
    try:
        import msal
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes
    except ImportError:
        raise SystemExit("Missing packages: py -m pip install msal cryptography")
    for name, v in (("TENANT_ID", TENANT_ID), ("CLIENT_ID", CLIENT_ID), ("SCOPE", SCOPE)):
        if not v or v == "TBD":
            raise SystemExit(f"{name} is not set (comes from Azure SSO)")
    cert = x509.load_pem_x509_certificate(Path(CERT_FILE).read_bytes())
    thumb = cert.fingerprint(hashes.SHA1()).hex()
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential={"private_key": Path(KEY_FILE).read_text(), "thumbprint": thumb})
    res = app.acquire_token_for_client(scopes=[SCOPE])
    if "access_token" not in res:
        raise SystemExit(f"Entra token failed: {res.get('error')}: {res.get('error_description')}")
    return res["access_token"]


# ─────────────────────────────── call ────────────────────────────────

def payload(users):
    return {"workflowArgs": {"users": ",".join(users), "requestedBy": REQUESTED_BY,
                             "certificationID": CERTIFICATION_ID}}


def submit(users, token):
    """One launch. No automatic retry - a retry after an unclear failure could launch twice."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(MULESOFT_URL, json=payload(users), headers=headers,
                      verify=VERIFY_TLS, timeout=TIMEOUT)
    try:
        body = r.json()
    except ValueError:
        body = {"raw": r.text[:2000]}
    ok = r.status_code == 200 and bool(body.get("requestID")) and not body.get("errors") \
        and not body.get("failure")
    return ok, r.status_code, body


def record(users, status, body, result):
    OUT.mkdir(parents=True, exist_ok=True)
    new = not LOG_CSV.exists()
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["Time", "Environment", "Result", "HTTP", "Request ID", "User Count",
                        "Users", "Requested By", "Certification ID", "Approval Needed",
                        "Errors / Warnings"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), ENVIRONMENT, result, status,
                    body.get("requestID", ""), len(users), ",".join(users), REQUESTED_BY,
                    CERTIFICATION_ID, "yes" if len(users) > 5 else "no",
                    json.dumps({"errors": body.get("errors"), "warnings": body.get("warnings")})])
    (OUT / f"{STAMP}_{result}.json").write_text(json.dumps(
        {"request": payload(users), "http": status, "response": body}, indent=1))


def notify(subject, lines):
    if DRY_RUN or not NOTIFY_TO:
        log(f"[summary not emailed] {subject}")
        return
    try:
        m = MIMEText("<br>".join(escape(x) for x in lines), "html")
        m["Subject"], m["From"], m["To"] = subject, SENDER_EMAIL, ", ".join(NOTIFY_TO)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as s:
            s.sendmail(SENDER_EMAIL, NOTIFY_TO, m.as_string())
    except Exception as e:
        log(f"Could not send summary email: {e}")


# ─────────────────────────────── main ────────────────────────────────

def main():
    global DRY_RUN
    ap = argparse.ArgumentParser(description="Submit a disable list to MEA via MuleSoft.")
    ap.add_argument("--input", required=True, help="disable_list_<date>.csv or one LAN ID per line")
    ap.add_argument("--dry-run", action="store_true", help="force dry run whatever the config says")
    ap.add_argument("--force", action="store_true", help=f"allow more than MAX_USERS ({MAX_USERS})")
    a = ap.parse_args()
    DRY_RUN = DRY_RUN or a.dry_run

    users = read_users(a.input)
    log(f"{len(users)} account(s) from {a.input} | env={ENVIRONMENT} | dry_run={DRY_RUN}")
    if not users:
        log("Nothing to submit.")
        return 0
    if len(users) > MAX_USERS and not a.force:
        raise SystemExit(f"{len(users)} accounts exceeds MAX_USERS={MAX_USERS} - check the list, "
                         f"or rerun with --force")
    batches = [users] if not BATCH_SIZE else [users[i:i + BATCH_SIZE]
                                              for i in range(0, len(users), BATCH_SIZE)]

    if DRY_RUN:
        for b in batches:
            log("[DRY_RUN] would POST " + json.dumps(payload(b)))
            record(b, "", {}, "dry_run")
        log(f"Dry run logged to {OUT}")
        return 0

    if not MULESOFT_URL or MULESOFT_URL == "TBD":
        raise SystemExit("MULESOFT_URL is not set (comes from the MuleSoft developer)")
    token = entra_token() if AUTH_MODE == "entra" else None

    lines, failed = [], 0
    for b in batches:
        ok, status, body = submit(b, token)
        result = "submitted" if ok else "failed"
        record(b, status, body, result)
        rid = body.get("requestID", "-")
        approval = " - more than 5 users, MEA approval work items created" if len(b) > 5 else ""
        line = f"{result.upper()}: {len(b)} account(s), requestID {rid}, HTTP {status}{approval}"
        log(line)
        lines.append(line)
        if not ok:
            failed += 1
            lines.append(f"  response: {json.dumps(body)[:800]}")
    lines += ["", f"Accounts: {', '.join(users)}", f"Requested by: {REQUESTED_BY}",
              f"Certification ID: {CERTIFICATION_ID}", f"Environment: {ENVIRONMENT}",
              "Completion is confirmed by MEA's notification email (MEA link)."]
    notify(f"{'FAILED' if failed else 'Submitted'}: MEA disable request - {len(users)} account(s) "
           f"[{ENVIRONMENT}]", lines)
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as e:
        if isinstance(e.code, str):
            log(e.code)
            sys.exit(1)
        raise
    except Exception:
        log(traceback.format_exc())
        sys.exit(1)
