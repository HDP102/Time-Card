# NPS Automation — Firewall Rule Recertification Scripts

Supporting automation for the annual firewall rule recertification campaign. Four
scripts cover the cycle end to end: notifying rule owners, recording their decisions
back into Tufin, and acting on those decisions.

| | |
|---|---|
| **Author** | Hardik Patel |
| **Created** | September 2026 |
| **Last modified by** | |
| **Date modified** | |
| **Repository** | `pgetech/NPS-Automation` |
| **Language** | Python 3.9+ |
| **Dependencies** | `openpyxl`, `requests` |

---

## At a glance

| Script | Path | Purpose | Scheduled |
|---|---|---|---|
| `notify_rule_owners.py` | `NPS-Automation/Notify/` | Email rule owners their rules and collect decisions | Manual |
| `notify_special.py` | `NPS-Automation/Notify/` | Same, driven by a per-list batch table | Manual |
| `tag_app_ids.py` | `NPS-Automation/RecertProcessor/` | Write App-IDs into the Tufin rule description field | Manual |
| `recert_processor.py` | `NPS-Automation/RecertProcessor/` | Create recertification and decommission tickets in Tufin | Manual |

**None of these run on a schedule.** All four are run deliberately by an operator. The
two that write to Tufin default to dry run and must be switched to live explicitly.

---

## notify_rule_owners.py

**Path:** `NPS-Automation/Notify/notify_rule_owners.py`

Reads the firewall rule spreadsheet, resolves each rule's owner from AMPS data, groups
rules by owner, and contacts them with three options: Recertify, Clean up / Remove, or
Review with the team. Each owner receives an Excel attachment with a Decision dropdown
so responses come back in a uniform, auditable format.

**Run modes** (`RUN_MODE` in CONFIG):

| Mode | Behaviour |
|---|---|
| `notify` | Email each owner their rules, plus an optional Teams card |
| `remind` | Chase owners who have not responded, with a days-outstanding count |
| `announce` | One heads-up card to the team channel before a wave goes out |
| `digest` | One status card to the team channel; contacts no owners |

**Key settings**

- `DRY_RUN` — `True` prints instead of sending. Default.
- `SKIP_RESPONDED` — skips owners who have already answered, so reminders only reach
  people who still owe a decision
- `NOTIFY_ROLES` — which owner roles are contacted (IT SME, IT Lead, Client Owner,
  IT Director, and so on)
- `NOTIFY_ONLY` / `EXCLUDE_OWNERS` / `NOTIFY_DEVICES` — filters that apply in every
  mode, including dry run and test sends
- `SMTP_HOST` — PG&E internal mailhost, port 25

**Scheduling:** none. Run manually when a wave or reminder is due.

---

## notify_special.py

**Path:** `NPS-Automation/Notify/notify_special.py`

The same notification logic, driven by a batch table. The recertification campaign runs
across eleven separate SharePoint lists, and each has its own spreadsheet, list URL, and
scope. `BATCHES` holds that mapping; setting `BATCH = n` selects one, so a wave can be
sent per list without editing paths and links by hand each time.

Also supports SharePoint mode, where the email points owners at their list rather than
attaching a spreadsheet, and owners record decisions directly in SharePoint.

**Key settings**

- `BATCH` — which of the eleven lists to send for
- `BATCHES` — the per-list table of spreadsheet, SharePoint URL, and scope
- All settings from `notify_rule_owners.py` also apply

**Scheduling:** none. Run manually per batch.

---

## tag_app_ids.py

**Path:** `NPS-Automation/RecertProcessor/tag_app_ids.py`

Writes each rule's App-ID into its Tufin rule description field, so rules can be
associated with the application they serve. This is the foundation for routing future
recertification notices by application rather than by spreadsheet.

**How it works**

1. Reads every reporting view matching `EXCEL_PATH` (a glob processes all eleven lists
   in one run)
2. Resolves each row to a Tufin rule UID via the `Rule-ID-Mapping.xlsx` workbook
3. Fetches rules from Tufin, builds the new description, and writes it back by UID
4. Writes `tag_output/tag_plan.xlsx` listing every intended change

**Key settings**

- `DRY_RUN` — `True` writes the plan file only, changes nothing. Default.
- `EXCEL_PATH` — input reporting views; accepts a glob such as `report_*.xlsx`
- `MAPPING_PATH` — the Rule-ID-Mapping workbook
- `RULE_FILTER` — which Tufin rules to fetch (TQL syntax, matches the Rule Viewer)
- `DESC_APPID_PREFIX` — the label written into the description

**Behaviour worth knowing**

Rules whose description already contains `##RLM##` are **skipped, not appended to**.
Another team writes App-IDs into that field in a different format. Appending would leave
two competing conventions in one field, so those rules are listed in the plan with the
reason and left alone until the format is agreed.

**Scheduling:** none. Run manually, review the plan, then run live.

---

## recert_processor.py

**Path:** `NPS-Automation/RecertProcessor/recert_processor.py`

Turns owner decisions into Tufin tickets. Recertify decisions become recertification
tickets; Cleanup/Remove decisions become disable tickets, subject to a traffic check.

**How it works**

1. Refuses to run if the campaign has closed or a reporting view is stale
2. Reads and merges every reporting view matching `REPORT_PATH`
3. Resolves each decision to a rule UID via `Rule-ID-Mapping.xlsx`
4. Fetches candidate rules from Tufin, carrying last-hit data
5. Creates recertification tickets, and disable tickets for cleanup rules that pass the
   last-hit guard
6. Writes all plan files **before** creating tickets, so a ticket failure cannot destroy
   the run's analysis

**Key settings**

- `DRY_RUN` — `True` validates tickets via Tufin's own dry-run flag without creating
  anything. Default.
- `REPORT_PATH` — input reporting views; accepts a glob
- `RUN_TAG` — a unique label per run, written into the disable ticket subject.
  **Change this every run.**
- `CAMPAIGN_END_DATE` / `REPORT_MAX_AGE_DAYS` — refuse to act on a closed campaign or a
  stale export
- `LAST_HIT_THRESHOLD_DAYS` — a rule hit within this window is never disabled
- `NEVER_HIT_POLICY` — how to treat rules with no hit data: `skip` (default) or
  `disable`

**Output** (in `recert_output/`)

| File | Contents |
|---|---|
| `recertify_plan.xlsx` | Rules submitted for recertification |
| `disable_plan.xlsx` | Rules submitted for disable, with hit date and run tag |
| `held_back_from_disable.xlsx` | Cleanup rules the guard refused, with the reason |
| `need_assistance.xlsx` | Owner asked for help; no ticket created |
| `decision_conflicts.xlsx` | Rules with different decisions in different lists |
| `rejected_by_tufin.xlsx` | Rules Tufin refused as ineligible |

**Scheduling:** none. Run manually, review the plan files, then run live.

---

## Shared design notes

### Rules are addressed by UID

The reporting views carry decisions and App-IDs but no Tufin rule UID. The
`Rule-ID-Mapping.xlsx` workbook maps Device Name + rule name to a SecureTrack Rule ID
for the whole estate, and both write-capable scripts resolve through it.

An earlier version matched on rule name alone. Rule names repeat across devices, and a
single spreadsheet row was found matching 100 rules on different devices. There is no
name-only fallback — if a row cannot be resolved to one rule, it is reported and skipped.

### Reporting-view headers are not consistent

Across the eleven lists the device column appears as `Device Name`, `Device Group`,
`Device group`, or `Title`, and the App-ID column as `App-ID` or `Application ID`. Both
are configured as alias lists. The scripts log which name each sheet matched, and report
the resolve rate per sheet so a list that finds its columns but cannot match the mapping
is visible rather than silently contributing nothing.

### The last-hit guard has a known limit

The guard holds back any rule hit within the threshold. It can only do that where Tufin
has hit data, and **Tufin cannot see hit counts on multi-VSYS firewalls** — roughly 72%
of the estate. On the GDN batch, 89 of 96 cleanup rules had no hit data at all.

The guard therefore proves a rule **is** in use. It cannot prove a rule is **not**. Hit
data for the disable decision needs to come from Panorama.

### Dry run is the default

Both Tufin-writing scripts default to `DRY_RUN = True`. Every intended change is written
to a reviewable plan file first. Live runs are a deliberate config change, not the
default state.

---

## Setup

```
py -m pip install openpyxl requests
```

Credentials are prompted at runtime and never stored. They can be supplied via the
`SECURETRACK_USER` and `SECURETRACK_PASSWORD` environment variables for an unattended
run, but must never be written into the files — these go to the repository.

Note that the SecureTrack API role is granted separately from UI access. An account can
sign in to the Tufin web interface and still receive 403 from the GraphQL API.

---

## Open items

| Item | Owner | Status |
|---|---|---|
| Rule description format — reconcile `app_id:` with the existing `##RLM##` convention | TBD | Open; tagging skips RLM rules until settled |
| Production endpoint, workflow names, and API role | Tufin platform owner | Open |
| Last-hit threshold — 90 days flat, or 90 for delete / 65 for disable | Process owner | Open; defaults to 90 |
| Policy for rules with no hit data | Process owner | Open; defaults to skip |
| Device+rule pairs with conflicting UIDs in the mapping workbook | Mapping owner | Open; those rules are skipped |
| DR rules require a tag added to the Panoramas | Firewall team | Open |
