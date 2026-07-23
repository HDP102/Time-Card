"""
notify_rule_owners.py
=====================
Workstream 1 — Rule Recertification Owner Notifications
PG&E | Project Bluetooth Mode

What this script does:
  1. Reads Leonard's Excel spreadsheet (all 218 device tabs)
  2. Parses each rule's AMPS owner data from Source/Destination columns
  3. Deduplicates owners across rules — one notification per owner
  4. Sends each owner a notification listing their rules with three options:
       A) Recertify  B) Clean up / Remove  C) Review with the team
  5. Supports Email (SMTP) and/or Teams (incoming webhook)
  6. Logs all notifications sent to a CSV for tracking

Usage:
  py -m pip install openpyxl requests
  py notify_rule_owners.py

Configuration (edit CONFIG block below):
  EXCEL_PATH      — path to Leonard's spreadsheet
  NOTIFY_EMAIL    — True/False
  NOTIFY_TEAMS    — True/False
  DRY_RUN         — True = print only, do NOT send anything
  SENDER_EMAIL    — your CorpID@pge.com address
  SMTP_HOST       — mailhost (PG&E internal)
  TEAMS_WEBHOOK   — your Teams incoming webhook URL
"""

import ast
import csv
import json
import logging
import smtplib
import re
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests
from openpyxl import load_workbook

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
EXCEL_PATH      = "Timesheet.xlsx"              # Path to Leonard's spreadsheet
NOTIFY_EMAIL    = True                           # Send email notifications
NOTIFY_TEAMS    = False                          # Send Teams notifications
DRY_RUN         = True                           # True = print only, don't send

SENDER_EMAIL    = "hardik.patel@pge.com"         # Your CorpID@pge.com
SMTP_HOST       = "mailhost"                     # PG&E internal mailhost
SMTP_PORT       = 25

TEAMS_WEBHOOK   = "<YOUR_TEAMS_WEBHOOK_URL>"    # Teams incoming webhook URL

LOG_FILE        = f"notifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# TEST MODE — sends only ONE email to SENDER_EMAIL (yourself) using the first
# owner's rules as sample data. Use this to verify formatting before going live.
# Set DRY_RUN = False and TEST_MODE = True to send a single real test email.
TEST_MODE       = False

# Tags to SKIP — base rules and standard exceptions don't need owner notifications
SKIP_TAGS       = {"BaseRule", "ToolsRule", "ToolsRules"}

# Shadowing: skip fully shadowed rules (already being handled via decommission workstream)
SKIP_SHADOWED   = True
# ─────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── Owner parsing ──────────────────────────────────────────────────────────────

def parse_owner_string(raw):
    """
    Parse the AMPS owner string from Leonard's spreadsheet.
    Format: "10.x.x.x = {'APP-123': {'hostname': {'APP-123': {'Client Owner': 'Name (ID)'}}}}\n..."
    Returns list of dicts: [{email, name, role, app_id, ip}]
    """
    owners = []
    if not raw or "Skip AMPS" in raw or "No APPID" in raw:
        return owners

    # Each line is one IP entry
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or "=" not in line:
            continue

        try:
            ip_part, dict_part = line.split("=", 1)
            ip = ip_part.strip()
            data = ast.literal_eval(dict_part.strip())

            # Navigate: {app_id: {hostname: {app_id_list: {owner_fields}}}}
            for app_id, hostname_map in data.items():
                for hostname, inner in hostname_map.items():
                    for app_key, fields in inner.items():
                        if not isinstance(fields, dict):
                            continue
                        for role, value in fields.items():
                            if not value or not isinstance(value, str):
                                continue
                            # Extract name and CorpID from "Lastname, Firstname (CORPID)"
                            match = re.match(r"(.+?)\s*\(([A-Z0-9]+)\)", value)
                            if match:
                                name   = match.group(1).strip()
                                corpid = match.group(2).strip()
                                email  = f"{corpid}@pge.com"
                                owners.append({
                                    "email":   email,
                                    "name":    name,
                                    "corpid":  corpid,
                                    "role":    role,
                                    "app_id":  app_id,
                                    "ip":      ip,
                                    "hostname": hostname,
                                })
        except Exception:
            continue

    return owners


def extract_primary_owner(owners):
    """
    Pick the best single owner to notify per rule.
    Priority: Client Owner > Cyber Owner > IT SME > IT Lead
    """
    priority = ["Client Owner", "Cyber Owner", "IT SME", "IT Lead", "IT SME backup"]
    for role in priority:
        for o in owners:
            if o["role"] == role:
                return o
    return owners[0] if owners else None


# ── Excel reading ──────────────────────────────────────────────────────────────

def load_rules(excel_path):
    """
    Read all tabs from Leonard's spreadsheet.
    Returns list of rule dicts.
    """
    log.info(f"Loading spreadsheet: {excel_path}")
    wb = load_workbook(excel_path, read_only=True, data_only=True)
    rules = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        headers = None

        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                headers = list(row)
                col = {h: idx for idx, h in enumerate(headers) if h}
                continue

            if not any(row):
                continue

            def g(field):
                idx = col.get(field)
                return row[idx] if idx is not None else None

            # Skip base/tools rules
            tags = str(g("Tags") or "")
            if any(t in tags for t in SKIP_TAGS):
                continue

            # Skip fully shadowed if configured
            shadow = str(g("Shadowing Status") or "")
            if SKIP_SHADOWED and shadow == "FULLY_SHADOWED":
                continue

            rules.append({
                "sheet":        sheet_name,
                "device_name":  g("Device Name"),
                "policy_name":  g("Policy Name"),
                "rule_name":    g("ID on Device"),
                "source":       g("Source"),
                "destination":  g("Destination"),
                "service":      g("Service"),
                "application":  g("Application"),
                "action":       g("Action"),
                "tags":         tags,
                "last_hit":     g("Last Hit"),
                "shadowing":    shadow,
                "ticket_id":    g("Ticket ID"),
                "app_name":     g("Application Name"),
                "disabled":     g("Disabled"),
                "src_owners_raw": g("Source AMPS owners list"),
                "dst_owners_raw": g("Destination AMPS owners list"),
                "business_justification": g("Policy Name + tag + FER close date + Business Justification"),
            })

    total_sheets = len(wb.sheetnames)
    wb.close()
    log.info(f"Loaded {len(rules)} rules across {total_sheets} devices")
    return rules


# ── Owner aggregation ──────────────────────────────────────────────────────────

def build_owner_rule_map(rules):
    """
    Returns dict: {email -> {"owner": owner_dict, "rules": [rule, ...]}}
    Groups all rules under their primary owner's email.
    """
    owner_map = {}

    for rule in rules:
        all_owners = []
        all_owners += parse_owner_string(rule.get("src_owners_raw", "") or "")
        all_owners += parse_owner_string(rule.get("dst_owners_raw", "") or "")

        owner = extract_primary_owner(all_owners)
        if not owner:
            continue

        email = owner["email"]
        if email not in owner_map:
            owner_map[email] = {"owner": owner, "rules": []}
        owner_map[email]["rules"].append(rule)

    return owner_map


# ── Message formatting ─────────────────────────────────────────────────────────

def format_email(owner, rules):
    """Build HTML email body."""
    # Name format is "Lastname, Firstname" — extract first name for greeting
    parts = owner["name"].split(",")
    name = parts[1].strip().split()[0] if len(parts) > 1 else parts[0].strip()

    rows = ""
    for r in rules:
        last_hit = str(r.get("last_hit") or "Never")

        # Fix ticket ID — Excel sometimes reads as float (e.g. 0.110789 100376)
        raw_ticket = r.get("ticket_id") or ""
        ticket_lines = []
        for t in str(raw_ticket).strip().split("\n"):
            t = t.strip()
            if t and t not in ("0", "0.0"):
                try:
                    ticket_lines.append(str(int(float(t))) if "." in t else t)
                except ValueError:
                    ticket_lines.append(t)
        ticket_display = ", ".join(ticket_lines) if ticket_lines else "N/A"

        # Truncate long source/destination strings for readability
        src = str(r.get("source") or "")
        dst = str(r.get("destination") or "")
        src = (src[:60] + "...") if len(src) > 60 else src
        dst = (dst[:60] + "...") if len(dst) > 60 else dst

        rows += f"""
        <tr>
          <td style='padding:6px;border:1px solid #ddd'>{r['device_name'] or ''}</td>
          <td style='padding:6px;border:1px solid #ddd'>{r['rule_name'] or ''}</td>
          <td style='padding:6px;border:1px solid #ddd;font-size:11px'>{src}</td>
          <td style='padding:6px;border:1px solid #ddd;font-size:11px'>{dst}</td>
          <td style='padding:6px;border:1px solid #ddd'>{last_hit}</td>
          <td style='padding:6px;border:1px solid #ddd'>{ticket_display}</td>
        </tr>"""

    html = f"""
    <html><body style='font-family:Arial,sans-serif;color:#333'>
    <p>Hi {name},</p>

    <p>As part of PG&E's annual firewall rule recertification process, the following
    firewall rules have been identified as requiring your review. These rules are
    associated with applications or assets you own.</p>

    <p><strong>Please review the rules below and choose one of the following options
    for each:</strong></p>

    <ol>
      <li><strong>Recertify</strong> — The rule is still needed and should remain active.</li>
      <li><strong>Clean up / Remove</strong> — The rule is no longer needed and can be disabled/deleted.</li>
      <li><strong>Review with the team</strong> — You are unsure and would like to discuss with the NPS Automation team.</li>
    </ol>

    <table style='border-collapse:collapse;width:100%;font-size:13px'>
      <thead>
        <tr style='background:#003366;color:white'>
          <th style='padding:8px;text-align:left'>Device</th>
          <th style='padding:8px;text-align:left'>Rule Name</th>
          <th style='padding:8px;text-align:left'>Source</th>
          <th style='padding:8px;text-align:left'>Destination</th>
          <th style='padding:8px;text-align:left'>Last Hit</th>
          <th style='padding:8px;text-align:left'>Ticket ID</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>

    <p style='margin-top:20px'>Please reply to this email with your decision for each rule,
    or contact the NPS Automation team to schedule a review.</p>

    <p>If you have any questions, please reach out directly.</p>

    <p>Thank you,<br>
    <strong>NPS Automation Team</strong><br>
    PG&E Network & Platform Security</p>

    <p style='font-size:11px;color:#888'>
    This is an automated notification from the NPS firewall recertification process.
    Rule count in this notification: {len(rules)}
    </p>
    </body></html>
    """
    return html


def format_teams_card(owner, rules):
    """Build Teams adaptive card payload for incoming webhook."""
    parts = owner["name"].split(",")
    name = parts[1].strip().split()[0] if len(parts) > 1 else parts[0].strip()
    rule_lines = []
    for r in rules:
        last_hit = str(r.get("last_hit") or "Never")
        raw_ticket = r.get("ticket_id") or ""
        ticket_lines = []
        for t in str(raw_ticket).strip().split("\n"):
            t = t.strip()
            if t and t not in ("0", "0.0"):
                try:
                    ticket_lines.append(str(int(float(t))) if "." in t else t)
                except ValueError:
                    ticket_lines.append(t)
        ticket_display = ", ".join(ticket_lines) if ticket_lines else "N/A"
        rule_lines.append(
            f"• **{r['rule_name'] or 'Unnamed'}** | Device: {r['device_name']} | "
            f"Last Hit: {last_hit} | Ticket: {ticket_display}"
        )

    rules_text = "\n\n".join(rule_lines)

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🔒 Firewall Rule Recertification Required",
                            "weight": "Bolder",
                            "size": "Medium",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Hi **{name}**, the following firewall rules require your review.",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "**Your Rules:**",
                            "weight": "Bolder",
                            "spacing": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": rules_text,
                            "wrap": True,
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "**Please choose one action for each rule:**",
                            "weight": "Bolder",
                            "spacing": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": "✅ **A) Recertify** — Rule is still needed\n\n"
                                    "🗑️ **B) Clean up / Remove** — Rule is no longer needed\n\n"
                                    "💬 **C) Review with the team** — Need to discuss",
                            "wrap": True,
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Reply to this message or contact the NPS Automation team.",
                            "wrap": True,
                            "spacing": "Medium",
                            "isSubtle": True
                        }
                    ]
                }
            }
        ]
    }
    return payload


# ── Sending ────────────────────────────────────────────────────────────────────

def send_email(to_email, owner, rules, dry_run=True):
    subject = f"Action Required: Firewall Rule Recertification ({len(rules)} rule{'s' if len(rules) > 1 else ''})"
    html_body = format_email(owner, rules)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))

    if dry_run:
        log.info(f"[DRY RUN] Would email: {to_email} | {len(rules)} rules | Subject: {subject}")
        return True

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        log.info(f"Email sent: {to_email}")
        return True
    except Exception as e:
        log.error(f"Email failed to {to_email}: {e}")
        return False


def send_teams(owner, rules, dry_run=True):
    payload = format_teams_card(owner, rules)

    if dry_run:
        log.info(f"[DRY RUN] Would Teams-notify: {owner['name']} | {len(rules)} rules")
        return True

    if not TEAMS_WEBHOOK or TEAMS_WEBHOOK.startswith("<"):
        log.warning("Teams webhook not configured, skipping")
        return False

    try:
        resp = requests.post(
            TEAMS_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        if resp.status_code in (200, 202):
            log.info(f"Teams notification sent: {owner['name']}")
            return True
        else:
            log.error(f"Teams failed for {owner['name']}: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        log.error(f"Teams error for {owner['name']}: {e}")
        return False


# ── Logging ────────────────────────────────────────────────────────────────────

def write_log(log_file, rows):
    with open(log_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp", "email", "name", "corpid", "role",
            "rule_count", "email_sent", "teams_sent", "device_list"
        ])
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"Notification log written to: {log_file}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if DRY_RUN:
        log.info("=" * 60)
        log.info("DRY RUN MODE — no notifications will actually be sent")
        log.info("Set DRY_RUN = False in CONFIG to send for real")
        log.info("=" * 60)

    # 1. Load rules
    rules = load_rules(EXCEL_PATH)

    # 2. Group by owner
    owner_map = build_owner_rule_map(rules)
    log.info(f"Unique owners to notify: {len(owner_map)}")

    # 3. Notify each owner
    log_rows = []

    # TEST MODE: take the first owner's rules, redirect email to SENDER_EMAIL
    if TEST_MODE and not DRY_RUN:
        log.info("=" * 60)
        log.info("TEST MODE — sending ONE sample email to yourself")
        log.info(f"Recipient overridden to: {SENDER_EMAIL}")
        log.info("=" * 60)
        first_email, first_data = next(iter(owner_map.items()))
        test_owner = first_data["owner"].copy()
        test_rules = first_data["rules"]
        send_email(SENDER_EMAIL, test_owner, test_rules, dry_run=False)
        log.info("Test email sent. Review your inbox, then set TEST_MODE = False to run for real.")
        return

    for email, data in owner_map.items():
        owner = data["owner"]
        owner_rules = data["rules"]

        email_ok = False
        teams_ok = False

        if NOTIFY_EMAIL:
            email_ok = send_email(email, owner, owner_rules, dry_run=DRY_RUN)

        if NOTIFY_TEAMS:
            teams_ok = send_teams(owner, owner_rules, dry_run=DRY_RUN)

        devices = list({r["device_name"] for r in owner_rules if r["device_name"]})

        log_rows.append({
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "email":       email,
            "name":        owner["name"],
            "corpid":      owner["corpid"],
            "role":        owner["role"],
            "rule_count":  len(owner_rules),
            "email_sent":  email_ok,
            "teams_sent":  teams_ok,
            "device_list": "; ".join(devices[:5]) + ("..." if len(devices) > 5 else ""),
        })

    # 4. Write log
    write_log(LOG_FILE, log_rows)

    # 5. Summary
    print("\n" + "=" * 60)
    print("  NOTIFICATION SUMMARY")
    print(f"  Total rules processed:    {len(rules)}")
    print(f"  Unique owners identified: {len(owner_map)}")
    print(f"  Email notifications:      {'enabled' if NOTIFY_EMAIL else 'disabled'}")
    print(f"  Teams notifications:      {'enabled' if NOTIFY_TEAMS else 'disabled'}")
    print(f"  Dry run:                  {DRY_RUN}")
    print(f"  Log file:                 {LOG_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
