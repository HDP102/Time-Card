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
| `remind` | Yes | Chases owners who have not responded, with a days-outstanding count |
| `announce` | No | One heads-up card to the team channel before a wave goes out |
| `digest` | No | One status card to the team channel: notified / responded / outstanding |

### `notify`
The standard run. The companion Teams card carries no rule data — it tells the owner to check their email and confirms the message is legitimate. That last part matters: an unexpected internal email with an Excel attachment asking you to fill in a form and reply is exactly what security awareness training tells people to distrust, and this is a security team sending dozens of them.

### `remind`
Reads `RESPONDED_FILE` and skips anyone listed. Reads the `notifications_*.csv` logs from previous runs to work out how long each owner has been outstanding, and skips anyone notified less than `REMIND_AFTER_DAYS` ago. Reminder wording replaces the original pitch and includes the wait time.

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
    ├── notifications_*.csv       ← one per owner-contacting run
    └── discarded/                ← move a bad run's log here to void it
```

`responded.csv`, `responses/` and `logs/discarded/` appear only once a real send has actually delivered at least one email. Dry runs and test sends write a log and nothing else, so rehearsing never litters the folder.

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

Real sends to a small group are the sensible way to pilot this, but a real send writes real history — the script will then believe those people were notified, and reminders will age from that date.

To void a run, delete its log from `logs/`, or move it into `logs/discarded/`. Anything inside `discarded/` is ignored when history is read, and moving it back restores it. Deleting is permanent; moving is reversible, so prefer moving if you might want the record later.

The console prints the exact path after every real send, so you always know which file to remove:

```
INFO To discard this run, delete logs/notifications_20260724_141553.csv
     or move it into logs/discarded — it will stop counting as notified
```

---

## Dry Run / Test / Production

| Mode | Config | Filters apply? | Who receives mail |
|------|--------|----------------|-------------------|
| **Dry run** | `DRY_RUN = True` | Yes | Nobody. Prints what would be sent and writes the CSV log |
| **Test** | `DRY_RUN = False`, `TEST_MODE = True` | Yes | You. One email per matched owner, all sent to `SENDER_EMAIL` |
| **Production** | `DRY_RUN = False`, `TEST_MODE = False` | Yes | The actual rule owners |

Test mode does not change what the script builds — only where it sends. The email an owner would have received arrives in your inbox exactly as they would see it, greeting and all.

### A Note on Teams

Filters apply to Teams cards exactly as they apply to email, in every run mode.

Routing is the part that differs. A webhook posts to one fixed destination, so there is no per-owner address to override the way there is with email. Three settings handle this:

| Setting | Destination | Used by |
|---------|-------------|---------|
| `TEAMS_WEBHOOK` | Team channel | `announce`, `digest`, and owner cards if no per-user flow exists |
| `TEAMS_USER_WEBHOOK` | An individual owner's chat | `notify` and `remind` owner cards |
| `TEAMS_WEBHOOK_TEST` | Your own chat or a private channel | Anything, whenever `TEST_MODE = True` |

**Owner-directed cards need `TEAMS_USER_WEBHOOK`** — a Power Automate flow that reads a `recipient` field from the request body and posts to that person's chat. The script sends the owner's CorpID address as `recipient`, which is their UPN. Without this flow, owner cards fall back to the channel and the script warns you each time.

Cards built during a test run carry a `🧪 TEST — not an official notification` header naming the owner they were generated for, so a stray test card is never mistaken for a real one.

Practical guidance:
- Point the channel webhook at a private or team-only channel until the process is approved
- Always scope test runs with `NOTIFY_ONLY` so you post one or two cards, not dozens
- `TEAMS_DELAY_SECONDS` spaces out the posts; webhooks throttle a tight loop
- Email and Teams are independent — set `NOTIFY_EMAIL = False` to exercise Teams on its own
- Cards never contain rule data. They point the owner at the email, which keeps rule detail out of a channel where it may not belong

> ⚠️ Classic Office 365 connector webhooks were retired by Microsoft in May 2026 and no longer deliver. Any webhook URL you are given must come from the **Workflows / Power Automate** app. Workflows can post to a chat as well as a channel, which is what makes per-user and personal-test webhooks possible. Note that Adaptive Cards posted this way appear as the default Flow bot — custom bot name and icon are not supported. Confirm current behaviour with whoever provisions the webhook.

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

Owner-contacting runs (`notify`, `remind`) write a timestamped CSV log into `logs/`. `announce` and `digest` contact nobody and write no log.


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
| Far more test emails than expected | Test mode sends one per owner in scope. Set `NOTIFY_ONLY` to narrow it |
| Ticket ID shows unexpected format | Update to latest version of the script |
| Greeting shows last name instead of first | Update to latest version of the script |
| Teams notification not sending | Check webhook URL is filled in and `NOTIFY_TEAMS = True` |
| Teams posts failing partway through a run | The webhook is throttling. Raise `TEAMS_DELAY_SECONDS` |
| `RUN_MODE "..." not recognised` | Use exactly one of: notify, remind, announce, digest |
| Owner cards landing in the channel instead of a DM | `TEAMS_USER_WEBHOOK` is empty. The script warns each time this happens |
| "Nobody is due a reminder right now" | Everyone has responded, or nobody was notified more than `REMIND_AFTER_DAYS` ago. Reminders need a prior real notify run — dry runs and test sends do not count |
| Reminder says an owner was never notified | History comes from `logs/notifications_*.csv`. Check the log was not deleted or moved into `logs/discarded/` |
| Test cards indistinguishable from real ones | Test-run cards carry a TEST banner. If it is missing, the run was not in test mode |

---

## Important Notes

- Keep the `logs/` folder — `remind` and `digest` read it for history. Removing a log voids that run
- **Never hard-code passwords** in the script — SMTP requires no authentication, keep it that way
- **Do not use `@exchange.pge.com`** addresses as sender or recipient — PG&E blocks these
- **Label the script as Confidential** when sharing internally via email
- **Do not send the script outside PG&E**
- The script currently covers **ODN NERC low and medium sites only**. Additional device groups will be added as the rule spreadsheet is expanded
- **BCSI-sensitive rules must be routed to separate outputs** from non-BCSI rules, and ODN and UDN rules must be kept in separate reports. This separation is not yet implemented in the script and must be in place before a production send

---

## Contact

Reach out to the NPS Automation team for questions, approvals, or to report issues.
