# notify_rule_owners.py
### PG&E | NPS Automation — Firewall Rule Recertification Notification Script

---

## What This Script Does

Reads the firewall rule spreadsheet, identifies the owner of each rule via AMPS data, groups all rules under each owner, and sends them a notification with three options:

1. **Recertify** — The rule is still needed
2. **Clean up / Remove** — The rule is no longer needed
3. **Review with the team** — Not sure, wants to discuss

Supports both **Email** (PG&E internal SMTP) and **Teams** (incoming webhook).

**Every owner receives an Excel attachment** with a Decision dropdown, regardless of how many rules they have. The response format is deliberately uniform — one parseable artifact per owner keeps the audit trail consistent and avoids hand-transcribing free-text email replies.

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
RUN_MODE             = "notify"      # notify | remind | announce | digest

EXCEL_PATH           = "firewall_rule_report.xlsx"
NOTIFY_EMAIL         = True
NOTIFY_TEAMS         = False
DRY_RUN              = True
TEST_MODE            = False
TEST_LIMIT           = 1             # max emails a test run sends you; 0 = no cap

SENDER_EMAIL         = "corpid@pge.com"   # Your CorpID@pge.com
SMTP_HOST            = "mailhost"         # PG&E internal SMTP — do not change
SMTP_PORT            = 25

TEAMS_WEBHOOK        = "<CHANNEL_WEBHOOK>"   # team channel — announce, digest
TEAMS_USER_WEBHOOK   = ""                    # Power Automate flow that DMs an owner
TEAMS_WEBHOOK_TEST   = ""                    # test destination, "" reuses the above
TEAMS_DELAY_SECONDS  = 1                     # pause between posts to avoid throttling

RESPONDED_FILE       = "responded.csv"       # owners who have already replied
RESPONSES_DIR        = "responses"           # save replied-to spreadsheets here
LOGS_DIR             = "logs"                # run logs; reminders read these
REMIND_AFTER_DAYS    = 14                    # only chase after this long

NOTIFY_ROLES         = ["IT SME", "IT SME Backup", "IT Lead", "Client Owner"]
GROUP_BY             = "app_id"   # "app_id" (one email per app) or "owner" (one per person)
RESPONSE_METHOD      = "sharepoint"   # "sharepoint" (owners edit the list) or "attachment" (reply with file)
SHAREPOINT_LINK      = "<SHAREPOINT_LIST_LINK>"   # the list link for this network — set per run
EMAIL_SCOPE          = ""             # network/list label shown in the subject (GDN/ODN/Medium)
RECERT_DEADLINE      = "9/18"         # "all rules must be recertified by" date
RECERT_WINDOW        = "one week"     # "please respond within" phrasing
FAQ_LINK             = "<pre-filled>" # public How-To / FAQ doc link
OFFICE_HOURS_INFO    = "<pre-filled>" # office-hours Teams blocks (update if meetings change)
SENDER_SIGNATURE     = "<pre-filled>" # sign-off; set to whoever/whichever mailbox sends

NOTIFY_ONLY          = []      # whitelist of CorpIDs — [] = everyone
EXCLUDE_OWNERS       = []      # blacklist of CorpIDs — [] = exclude nobody
NOTIFY_DEVICES       = []      # only these devices/sites — [] = all devices

SKIP_TAGS            = {"BaseRule", "ToolsRule", "ToolsRules"}
SKIP_SHADOWED        = True
```

> ⚠️ Never put passwords in this script. The PG&E SMTP relay requires no authentication.

---

## Run Modes

`RUN_MODE` picks the job. Filters apply to all four.

| Mode | Contacts owners? | What it does |
|------|------------------|--------------|
| `notify` | Yes | The main run. Emails each owner their rules as an Excel attachment, plus an optional companion Teams card |
| `remind` | Yes | Chases owners who have not responded. Distinct subject and body — no process explainer, states how long it has been, re-attaches the same spreadsheet |
| `announce` | No | One heads-up card to the team channel before a wave goes out |
| `digest` | No | One status card to the team channel: notified / responded / outstanding |

### `notify`
The standard run. The companion Teams card carries no rule data — it tells the owner to check their email and confirms the message is legitimate. That last part matters: an unexpected internal email with an Excel attachment asking you to fill in a form and reply is exactly what security awareness training tells people to distrust, and this is a security team sending dozens of them.

### `remind`
Reads `RESPONDED_FILE` and skips anyone listed. Reads `logs/notifications.csv` from previous runs to work out how long each owner has been outstanding, and skips anyone notified less than `REMIND_AFTER_DAYS` ago. Reminder wording replaces the original entirely:

| | Original | Reminder |
|---|---|---|
| Subject | Action Required: Firewall Rule Recertification (12 rules) | Reminder: Firewall Rule Recertification Still Outstanding (12 rules) |
| Opening | Explains the annual recertification process | States no decisions have been received, and how many days it has been |
| Attachment | Their rule list | The same list again, so they need not hunt for the original email |
| Extra | — | Invites them to flag if they already replied or no longer own the rules |

The days-outstanding line is omitted when there is no notification history to age against.

Requires at least one prior real `notify` run — dry runs and test sends are deliberately excluded from history, so rehearsing never makes the script think someone was contacted.

### `announce`
Posts once to the team channel describing what is about to land, what it looks like, and who to ask. Cuts down "is this phishing?" traffic before it starts. Contacts nobody.

### `digest`
Posts a status roll-up to the team channel: response rate, counts notified / responded / outstanding, rules still outstanding, age of the oldest outstanding request, and the five largest holdouts by rule count. Contacts nobody, needs no per-user setup, and is the cheapest way to give the team a live picture of progress.

---

## Response Tracking

### Folder layout

The script creates these itself — you do not need to make them by hand:

```
Notify/
├── notify_rule_owners.py
├── firewall_rule_report.xlsx     ← must match EXCEL_PATH
├── responded.csv                 ← created after the first real send
├── responses/                    ← created after the first real send
└── logs/
    └── notifications.csv         ← one running log; every run appends to it
```

`responded.csv` and `responses/` appear only once a real send has actually delivered at least one email. Dry runs and test sends write a log and nothing else, so rehearsing never litters the folder.

### Recording who replied

`responded.csv` is a plain list, one CorpID per line under a `corpid` header:

```
corpid
ABC1
XYZ2
```

Add a line as each reply arrives. `remind` skips anyone listed; `digest` counts them as responded. Nothing writes to this file automatically — it is yours to maintain.

Save the returned spreadsheets into `responses/`. They are named after the owner's CorpID, so the folder doubles as a record of who has replied and what they decided.

### Discarding a bad run

Real sends to a small group are the sensible way to pilot this, but a real send writes real history — the script will then treat those people as notified, and reminders will age from that date.

To void a run, open `logs/notifications.csv`, delete the relevant row(s), and save. Delete the whole row (all columns), not just the timestamp. Those owners then stop counting as notified, so `remind` will pick them up again and `digest` won't count them as done.

The console prints a reminder of this after every real send.

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

## Spreadsheet Formats

The script auto-detects which of two source formats it's given — no setting to change:

**Role-column format** (the current one). A single flat sheet with owner role columns already filled in (IT SME, IT SME Backup, IT Lead, IT Lead Delegate, Client Owner, IT Director, IT Senior Leader), each as `Last, First (CORPID)`, plus a `Single APPID` / `App-ID` column. Owners are pre-resolved in the sheet — no AMPS lookup needed.

**AMPS-string format** (the original). Many device-group tabs, owners parsed out of the `Source/Destination AMPS owners list` columns. Still supported for older files.

### Which config applies to which format

| Setting | Old (AMPS) | New (role-column) |
|---|---|---|
| `RUN_MODE`, `NOTIFY_EMAIL`, `NOTIFY_TEAMS`, `DRY_RUN`, `TEST_MODE`, `TEST_LIMIT`, `SENDER_EMAIL`, `SKIP_TAGS`, `SKIP_SHADOWED` | yes | yes |
| `NOTIFY_ONLY` / `EXCLUDE_OWNERS` | yes | yes — checks every recipient of a grouped email |
| `NOTIFY_DEVICES` | yes | yes |
| `NOTIFY_ROLES`, `GROUP_BY` | ignored | yes |

`NOTIFY_ONLY` on the new format keeps any app whose email includes a whitelisted person; `EXCLUDE_OWNERS` drops a blacklisted person from a grouped email but still notifies the rest. So scoping a test with `NOTIFY_ONLY = ["<corpid>"]` works the same way in both formats.

### Who gets notified, and how it's grouped (role-column format)

`NOTIFY_ROLES` controls which role columns are contacted. Default is IT SME, IT SME Backup, IT Lead, and Client Owner — the set agreed in review. IT Director and IT Senior Leader are deliberately left out; add them to the list if that changes.

`GROUP_BY` controls the grouping:
- `"app_id"` (default) — **one email per app ID**, sent to all that app's role-holders together, each getting the same attachment. This matches the "by app ID so people don't get a message per policy" requirement.
- `"owner"` — one email per person, covering every rule they own across all app IDs.

In a group email the greeting names everyone on it and a line calls out the app ID and the listed owners, noting any one of them can complete the review.

---

## How Owners Respond

`RESPONSE_METHOD` controls the email that goes out:

- **`sharepoint`** (default) — sends the full recertification email: the ask, the four
  disposition options (Recertify / Recertify–DR / Cleanup–Remove / Need Assistance),
  background, how-to steps, FAQ, office hours, and a sign-off. Owners record their decisions
  directly in the linked SharePoint list. **No attachment** and no per-rule content in the
  body — the list holds the rules. Requires `SHAREPOINT_LINK`; the script refuses to send if
  it's still the placeholder.
- **`attachment`** — sends a shorter email with the owner's rules attached as Excel; they fill
  in the Decision column and reply with the file.

### Editable email content

The long instructional prose is built into the script. The parts that change between runs or
that shouldn't be buried in code are config values, pre-filled with the current content:

| Setting | What it is |
|---|---|
| `SHAREPOINT_LINK` | The list link — **differs per list** (ODN Part1/Part2, GDN, Medium). Set it to match the sheet you're sending. Use the list share link (`.../:l:/r/...`), not a single-item link. Left as a placeholder because it's per-run and contains a personal-site path. |
| `EMAIL_SCOPE` | The network/list label added to the subject so recipients getting multiple emails can tell them apart, e.g. `GDN` → "...Firewall Rules - GDN". Set it per run next to `SHAREPOINT_LINK`; leave `""` to omit it. |
| `RECERT_DEADLINE` / `RECERT_WINDOW` | The due date and response window shown in the email. |
| `FAQ_LINK` | The public How-To / FAQ document link. |
| `OFFICE_HOURS_INFO` | The office-hours Teams blocks. Update if the meetings change (they carry live join links and passcodes). |
| `SENDER_SIGNATURE` | The sign-off. Set it to whoever — or whichever mailbox — is actually sending. |

The subject in SharePoint mode is **"ACT: Execute Recertification of Firewall Rules"**.

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
INFO [DRY RUN] Would email: corpid@pge.com | X rules | Subject: Action Required...
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
> `TEST_LIMIT` caps how many emails a test run can send you — it defaults to 1, so an unfiltered test gives you a single sample rather than dozens. Raise it to see more, or set it to 0 to send one per matched owner. The cap applies to test mode only and never limits a real send.

Check your inbox. You should receive an email titled:
```
Action Required: Firewall Rule Recertification (X rules)
```

Review:
- Does the greeting say "Hi [First Name]"?
- Does the rule table look clean and readable?
- Are the ticket IDs correct?
- Are source/destination columns truncated cleanly?
- Does the Excel attachment open with a working Decision dropdown in column G?

Pick one CorpID with many rules and one with only a few — the attachment should look right either way.

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

Then scope the run so only one card goes out and verify it lands correctly:

```python
DRY_RUN     = False
TEST_MODE   = True
NOTIFY_ONLY = ["ABC1"]
NOTIFY_TEAMS = True
```

The card will arrive in the webhook's channel with a TEST banner on it. Set `NOTIFY_EMAIL = False` first if you want to check Teams without also sending yourself email.

---

### Step 5 — Announce (optional but recommended)
Before the first real wave, post a heads-up to the team channel:
```python
RUN_MODE  = "announce"
DRY_RUN   = False
TEST_MODE = False
```
Contacts no owners. Gives the team something to point at when someone asks whether the email is real.

---

### Step 6 — Production Run
Once everything is approved:

```python
RUN_MODE  = "notify"
DRY_RUN   = False
TEST_MODE = False
```

Consider starting with a single site in `NOTIFY_DEVICES` as a pilot before opening it up to everyone. When you are ready for the full run, clear all three filter lists.

The script emails every owner in scope and records the run in the CSV log. Keep that log — reminders and digests read it.

> ⚠️ Before every production run, confirm `TEST_MODE = False` and check `RUN_MODE` and the filter lists are what you intend. The console prints the mode, owner count, and active filters before sending — read it.

---

### Step 7 — Track and Chase
As replies come in, add each responder's CorpID to `responded.csv`.

Status roll-up to the team channel at any time:
```python
RUN_MODE = "digest"
```

Chase the stragglers once enough time has passed:
```python
RUN_MODE          = "remind"
REMIND_AFTER_DAYS = 14
```
Dry run both first — `remind` in particular, so you can confirm the skip counts look right before anything goes out.

---

## Output Files

Owner-contacting runs (`notify`, `remind`) append to one running log, `logs/notifications.csv`. `announce` and `digest` contact nobody and write no log.


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
| attachment_sent | Always True — every owner gets an attachment |
| dry_run | True if this row came from a rehearsal, not a real send |
| test_mode | True if the mail was redirected to you rather than the owner |
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
| Far more test emails than expected | Raise or lower `TEST_LIMIT` — it caps test sends and defaults to 1. `TEST_LIMIT = 0` removes the cap |
| Ticket ID shows unexpected format | Update to latest version of the script |
| Greeting shows last name instead of first | Update to latest version of the script |
| Teams notification not sending | Check webhook URL is filled in and `NOTIFY_TEAMS = True` |
| Teams posts failing partway through a run | The webhook is throttling. Raise `TEAMS_DELAY_SECONDS` |
| `RUN_MODE "..." not recognised` | Use exactly one of: notify, remind, announce, digest |
| Owner cards landing in the channel instead of a DM | `TEAMS_USER_WEBHOOK` is empty. The script warns each time this happens |
| "Nobody is due a reminder right now" | Everyone has responded, or nobody was notified more than `REMIND_AFTER_DAYS` ago. Reminders need a prior real notify run — dry runs and test sends do not count |
| Reminder says an owner was never notified | History comes from `logs/notifications.csv`. Check their row was not deleted |
| Test cards indistinguishable from real ones | Test-run cards carry a TEST banner. If it is missing, the run was not in test mode |

---

## Important Notes

- Keep `logs/notifications.csv` — `remind` and `digest` read it for history. Deleting a row voids that owner's notification
- **Never hard-code passwords** in the script — SMTP requires no authentication, keep it that way
- **Do not use `@exchange.pge.com`** addresses as sender or recipient — PG&E blocks these
- **Label the script as Confidential** when sharing internally via email
- **Do not send the script outside PG&E**
- The script currently covers **ODN NERC low and medium sites only**. Additional device groups will be added as the rule spreadsheet is expanded
- **BCSI-sensitive rules must be routed to separate outputs** from non-BCSI rules, and ODN and UDN rules must be kept in separate reports. This separation is not yet implemented in the script and must be in place before a production send

---

## Contact

Reach out to the NPS Automation team for questions, approvals, or to report issues.
