# notify_rule_owners.py
### PG&E | NPS Automation — Firewall Rule Recertification Notification Script

---

## What This Script Does

Reads the firewall rule spreadsheet, identifies the owner of each rule via AMPS data, groups all rules under each owner, and sends them a notification with three options:

1. **Recertify** — The rule is still needed
2. **Clean up / Remove** — The rule is no longer needed
3. **Review with the team** — Not sure, wants to discuss

Supports both **Email** (PG&E internal SMTP) and **Teams** (incoming webhook).

---

## Prerequisites

### 1. Install Python
Request and install Python through the **PG&E IT Store**. Once installed, open PowerShell and verify:
```powershell
py --version
```
Should print something like `Python 3.11.9`

### 2. Install Required Libraries
```powershell
py -m pip install openpyxl requests
```

### 3. Place Files Together
Put these in the same folder:
```
📁 Notify/
  ├── notify_rule_owners.py
  ├── README.md
  └── firewall_rule_report.xlsx   ← the rule spreadsheet
```

---

## Configuration

Open `notify_rule_owners.py` in a text editor or VS Code and edit the **CONFIG block** near the top (around line 44):

```python
EXCEL_PATH    = "firewall_rule_report.xlsx"  # Path to the rule spreadsheet
NOTIFY_EMAIL  = True          # Send email notifications
NOTIFY_TEAMS  = False         # Send Teams notifications (need webhook URL first)
DRY_RUN       = True          # True = print only, don't send anything real
TEST_MODE     = False         # True = send ONE test email to yourself only

SENDER_EMAIL  = "corpid@pge.com"   # Your CorpID@pge.com
SMTP_HOST     = "mailhost"         # PG&E internal SMTP — do not change
SMTP_PORT     = 25                 # Do not change

TEAMS_WEBHOOK = "<YOUR_TEAMS_WEBHOOK_URL>"   # Fill in once webhook is received
```

> ⚠️ Never put passwords in this script. The PG&E SMTP relay requires no authentication.

---

## How to Run

Open PowerShell, navigate to the folder where the script is saved, and run:
```powershell
py notify_rule_owners.py
```

---

## Testing Step by Step

Follow this order — do not skip steps.

---

### Step 1 — Dry Run (no emails sent)
**Goal:** Verify the script reads the spreadsheet correctly and identifies owners.

In the config set:
```python
DRY_RUN   = True
TEST_MODE = False
```

Run the script. You should see output like:
```
INFO Loaded rules across all devices
INFO Unique owners to notify: X
INFO [DRY RUN] Would email: corpid@pge.com | X rules
...
NOTIFICATION SUMMARY
  Total rules processed:    XXXX
  Unique owners identified: XX
```

Also check the generated CSV log file — it lists every owner, their rule count, and device list.

✅ If the owner count and rule count look correct, the script is reading the data correctly.

---

### Step 2 — Test Mode (one real email to yourself)
**Goal:** See exactly what the email looks like in your actual inbox.

In the config set:
```python
DRY_RUN   = False
TEST_MODE = True
```

Run the script. It will send **one email to your own address** (`SENDER_EMAIL`) using the first owner's rules as sample data. No other emails go out.

> ⚠️ You must be on the PG&E network or VPN for this to work — the script connects to `mailhost` on port 25.

Check your inbox. You should receive an email titled:
```
Action Required: Firewall Rule Recertification (X rules)
```

Review:
- Does the greeting say "Hi [First Name]"?
- Does the rule table look clean and readable?
- Are the ticket IDs correct?
- Are source/destination columns truncated cleanly?

✅ If the email looks good, you're ready for team review.

---

### Step 3 — Get Sign-Off from Your Supervisor
Before sending to real rule owners:
- Show the dry run CSV and a sample test email to your supervisor for approval
- Confirm the owner list and rule counts look correct
- Discuss whether owners with large rule counts should be notified in batches by device group

---

### Step 4 — Wire In Teams (once webhook URL is received)
Once the Teams incoming webhook URL has been provided:

```python
TEAMS_WEBHOOK = "https://outlook.office.com/webhook/..."
NOTIFY_TEAMS  = True
```

Set `TEST_MODE = True` and `DRY_RUN = False` to send one Teams notification to verify it lands correctly before going live.

---

### Step 5 — Production Run
Once everything is approved:

```python
DRY_RUN   = False
TEST_MODE = False
```

Run the script. It will send emails (and Teams if configured) to all owners. The CSV log will record every notification sent.

> ⚠️ Double-check `TEST_MODE = False` before production. If `TEST_MODE = True`, only one email goes out regardless of other settings.

---

## Output Files

Each run generates a timestamped CSV log:
```
notifications_YYYYMMDD_HHMMSS.csv
```

Columns:
| Column | Description |
|--------|-------------|
| timestamp | When the notification was sent |
| email | Owner's PG&E email |
| name | Owner's full name |
| corpid | Owner's CorpID |
| role | Owner role (Client Owner, Cyber Owner, etc.) |
| rule_count | Number of rules in their notification |
| email_sent | True/False |
| teams_sent | True/False |
| device_list | Sites/devices their rules cover |

---

## Rules That Are Skipped

The script automatically skips:
- **Base rules** (tagged `BaseRule`, `ToolsRule`, `ToolsRules`) — standard infrastructure rules that don't need recertification
- **Fully shadowed rules** — already being handled by the decommission workstream
- **Rules with no resolvable owner** — broad subnet rules where AMPS lookup returns "Skip AMPS due to subnets"

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `py` not recognized | Python not installed — request via PG&E IT Store |
| `ModuleNotFoundError: openpyxl` | Run `py -m pip install openpyxl requests` |
| Email not arriving | Must be on PG&E network or VPN. Check you're not using `@exchange.pge.com` as sender |
| Ticket ID shows unexpected format | Update to latest version of the script |
| Greeting shows last name instead of first | Update to latest version of the script |
| Teams notification not sending | Check webhook URL is filled in and `NOTIFY_TEAMS = True` |

---

## Important Notes

- **Never hard-code passwords** in the script — SMTP requires no authentication, keep it that way
- **Do not use `@exchange.pge.com`** addresses as sender or recipient — PG&E blocks these
- **Label the script as Confidential** when sharing internally via email
- **Do not send the script outside PG&E**
- The script currently covers **ODN NERC low and medium sites only**. Additional device groups will be added as the rule spreadsheet is expanded.

---

## Contact

Reach out to the NPS Automation team for questions, approvals, or to report issues.
