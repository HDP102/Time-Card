# notify_rule_owners.py
### PG&E | NPS Automation — Firewall Rule Recertification Notification Script

---

## What This Script Does

Reads the firewall rule spreadsheet, identifies the owner of each rule via AMPS data, groups all rules under each owner, and sends them a notification with three options:

1. **Recertify** — The rule is still needed
2. **Clean up / Remove** — The rule is no longer needed
3. **Review with the team** — Not sure, wants to discuss

Supports both **Email** (PG&E internal SMTP) and **Teams** (incoming webhook).

Owners with a small number of rules get an inline table in the email body. Owners with more rules get an Excel attachment with a dropdown in the Decision column. The cutoff is set by `ATTACHMENT_THRESHOLD`.

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

Open `notify_rule_owners.py` in a text editor or VS Code and edit the **CONFIG block** near the top of the file.

```python
EXCEL_PATH           = "firewall_rule_report.xlsx"  # Path to the rule spreadsheet
NOTIFY_EMAIL         = True          # Send email notifications
NOTIFY_TEAMS         = False         # Send Teams notifications (need webhook URL first)
DRY_RUN              = True          # True = print only, don't send anything real

SENDER_EMAIL         = "corpid@pge.com"   # Your CorpID@pge.com
SMTP_HOST            = "mailhost"         # PG&E internal SMTP — do not change
SMTP_PORT            = 25                 # Do not change

TEAMS_WEBHOOK        = "<YOUR_TEAMS_WEBHOOK_URL>"   # Fill in once webhook is received

TEST_MODE            = False   # True = send to yourself instead of the real owners
ATTACHMENT_THRESHOLD = 8       # Above this rule count, send an Excel attachment

NOTIFY_ONLY          = []      # Whitelist of CorpIDs — [] = notify everyone
EXCLUDE_OWNERS       = []      # Blacklist of CorpIDs — [] = exclude nobody
NOTIFY_DEVICES       = []      # Only these devices/sites — [] = all devices

SKIP_TAGS            = {"BaseRule", "ToolsRule", "ToolsRules"}
SKIP_SHADOWED        = True
```

> ⚠️ Never put passwords in this script. The PG&E SMTP relay requires no authentication.

---

## The Three Modes

| Mode | Config | Filters apply? | Who receives mail |
|------|--------|----------------|-------------------|
| **Dry run** | `DRY_RUN = True` | Yes | Nobody. Prints what would be sent and writes the CSV log |
| **Test** | `DRY_RUN = False`, `TEST_MODE = True` | Yes | You. One email per matched owner, all sent to `SENDER_EMAIL` |
| **Production** | `DRY_RUN = False`, `TEST_MODE = False` | Yes | The actual rule owners |

Test mode does not change what the script builds — only where it sends. The email an owner would have received arrives in your inbox exactly as they would see it, greeting and all.

---

## Filters — Controlling Who Gets Notified

The three filter lists let you scope a run to a specific set of owners or sites. They apply in **all three modes**, so a dry run, a test send, and a production send with the same filters all cover exactly the same people.

All three stack. An owner must pass every active filter to be notified. Leave a list empty to turn that filter off.

### `NOTIFY_ONLY` — whitelist
Only these CorpIDs get notified. Everyone else is skipped.
```python
NOTIFY_ONLY = ["ABC1", "XYZ2"]   # [] = notify everyone
```

### `EXCLUDE_OWNERS` — blacklist
These CorpIDs are always skipped, even if they also appear in the whitelist. The blacklist wins.
```python
EXCLUDE_OWNERS = ["ABC1"]        # [] = exclude nobody
```

### `NOTIFY_DEVICES` — device / site filter
Only notify owners who have rules on the named devices or sites. Matching is partial and case-insensitive, and checks the spreadsheet tab name, the Device Name column, and the Policy Name column — so a short site name is enough to match all its variants.

An owner's rule list is also trimmed to just the matching devices, so they only receive rules for the site you are working on rather than their full list.
```python
NOTIFY_DEVICES = ["Site_Name_A", "Site_Name_B"]   # [] = all devices
```

### Common Patterns

| Goal | Config |
|------|--------|
| Preview one owner's email in your own inbox | `NOTIFY_ONLY = ["ABC1"]`, `TEST_MODE = True`, `DRY_RUN = False` |
| Pilot one site with real owners | `NOTIFY_DEVICES = ["Site_Name_A"]`, `TEST_MODE = False`, `DRY_RUN = False` |
| Everyone except one owner | `EXCLUDE_OWNERS = ["ABC1"]` |
| Full production run | All three lists `[]`, `TEST_MODE = False`, `DRY_RUN = False` |

Every run prints the owner count before and after filtering, plus which filters were active, so you can confirm the scope before anything goes out.

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
INFO Unique owners before filters: XX
INFO Unique owners after filters:  XX
INFO   No filters active — all owners in scope
INFO [DRY RUN] Would email: corpid@pge.com | X rules | inline table
...
NOTIFICATION SUMMARY
  Total rules loaded:       XXXX
  Owners found:             XX
  Owners notified:          XX
```

Also check the generated CSV log file — it lists every owner, their rule count, and device list.

✅ If the owner count and rule count look correct, the script is reading the data correctly.

---

### Step 2 — Test Mode (real emails, all sent to you)
**Goal:** See exactly what the emails look like in your actual inbox.

Pick one or two CorpIDs from the dry run CSV and scope the run to them:
```python
DRY_RUN     = False
TEST_MODE   = True
NOTIFY_ONLY = ["ABC1"]
```

Run the script. Every matched owner's email is sent to your own address (`SENDER_EMAIL`) instead of theirs. One CorpID in `NOTIFY_ONLY` means one email; two means two.

> ⚠️ You must be on the PG&E network or VPN for this to work — the script connects to `mailhost` on port 25.
>
> ⚠️ Running test mode with no filters sends one email per owner to your own inbox, which can be dozens of messages. The script warns you when the count is high. Use `NOTIFY_ONLY` to keep it small.

Check your inbox. You should receive an email titled:
```
Action Required: Firewall Rule Recertification (X rules)
```

Review:
- Does the greeting say "Hi [First Name]"?
- Does the rule table look clean and readable?
- Are the ticket IDs correct?
- Are source/destination columns truncated cleanly?
- For a large owner, does the Excel attachment open with a working Decision dropdown?

To check both formats, pick one CorpID with more rules than `ATTACHMENT_THRESHOLD` and one with fewer.

✅ If the emails look good, you're ready for team review.

---

### Step 3 — Get Sign-Off from Your Supervisor
Before sending to real rule owners:
- Show the dry run CSV and a sample test email to your supervisor for approval
- Confirm the owner list and rule counts look correct
- Discuss whether owners with large rule counts should be notified in batches by device group — `NOTIFY_DEVICES` is how you do this

---

### Step 4 — Wire In Teams (once webhook URL is received)
Once the Teams incoming webhook URL has been provided:

```python
TEAMS_WEBHOOK = "https://outlook.office.com/webhook/..."
NOTIFY_TEAMS  = True
```

Set `TEST_MODE = True` and `DRY_RUN = False` with a filter in place to send one Teams notification and verify it lands correctly before going live.

---

### Step 5 — Production Run
Once everything is approved:

```python
DRY_RUN   = False
TEST_MODE = False
```

Consider starting with a single site in `NOTIFY_DEVICES` as a pilot before opening it up to everyone. When you're ready for the full run, clear all three filter lists.

The script will send emails (and Teams if configured) to the owners in scope. The CSV log records every notification sent.

> ⚠️ Before every production run, confirm `TEST_MODE = False` and check the filter lists are what you intend. The console prints the owner count and active filters before sending — read it.

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
| attachment_sent | True if their rules were sent as an Excel attachment |
| email_sent | True/False |
| teams_sent | True/False |
| device_list | Sites/devices their rules cover |

---

## Rules That Are Skipped

The script automatically skips:
- **Base rules** (tagged `BaseRule`, `ToolsRule`, `ToolsRules`) — standard infrastructure rules that don't need recertification
- **Fully shadowed rules** — already being handled by the decommission workstream
- **Rules with no resolvable owner** — broad subnet rules where the AMPS lookup returns no usable owner

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `py` not recognized | Python not installed — request via PG&E IT Store |
| `ModuleNotFoundError: openpyxl` | Run `py -m pip install openpyxl requests` |
| Email not arriving | Must be on PG&E network or VPN. Check you're not using an `@exchange.pge.com` address as sender |
| "No owners matched the filters" | A filter list is too narrow or has a typo. CorpIDs are matched case-insensitively; device names are partial matches |
| Far more test emails than expected | Test mode sends one per owner in scope. Set `NOTIFY_ONLY` to narrow it |
| Expected an attachment but got an inline table | The owner's rule count is at or below `ATTACHMENT_THRESHOLD`. Lower the threshold to force attachments |
| Ticket ID shows unexpected format | Update to latest version of the script |
| Greeting shows last name instead of first | Update to latest version of the script |
| Teams notification not sending | Check webhook URL is filled in and `NOTIFY_TEAMS = True` |

---

## Important Notes

- **Never hard-code passwords** in the script — SMTP requires no authentication, keep it that way
- **Do not use `@exchange.pge.com`** addresses as sender or recipient — PG&E blocks these
- **Label the script as Confidential** when sharing internally via email
- **Do not send the script outside PG&E**
- The script currently covers **ODN NERC low and medium sites only**. Additional device groups will be added as the rule spreadsheet is expanded
- **BCSI-sensitive rules must be routed to separate outputs** from non-BCSI rules, and ODN and UDN rules must be kept in separate reports. This separation is not yet implemented in the script and must be in place before a production send

---

## Contact

Reach out to the NPS Automation team for questions, approvals, or to report issues.
