"""
hrv_owner_export.py - HRV owner recertification status for Power BI.

One row per App ID + owner role + owner, with how many of that app's rules are
certified, decertified or still pending. No rule-level detail (per Swapnil).

  Rules, App ID, status : Tufin SecureTrack GraphQL (Keycloak login).
                          App ID   = "app_id: APP-xxxx" in the rule description.
                          Status   = ruleUserData.certification; CERTIFIED / DECERTIFIED
                                     count only if timeCertified >= CAMPAIGN_START, anything
                                     older or missing is Pending.
  Owners by role        : the sheets in SharedData, used only as an App ID -> owner phone
                          book (App-ID + role columns, or AMPS owner text). Rule rows in the
                          sheets are not matched to Tufin.
                          App IDs no sheet knows fall back to the SecureApp owner when a
                          linked SecureApp application has the same APP number, else
                          "Owner unknown".
  Output                : one .xlsx, fixed name and columns, overwritten each run, written to
                          the OneDrive-synced HRV Power BI folder.

Run: py hrv_owner_export.py      (schedule daily with Task Scheduler)
Creds: SECURETRACK_USER / SECURETRACK_PASSWORD env vars (ticketAPI), else prompted.
"""
import csv
import getpass
import json
import os
import re
import sys
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

import requests
import urllib3
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

urllib3.disable_warnings()

# ═══════════════════════════════ CONFIG ═══════════════════════════════
TUFIN_HOST      = "keeppgesecure.utility.pge.com"        # prod
# Scope: every Palo Alto rule (~59k on 2026-10-22). Rules without "app_id:" in the
# description are counted under "No App ID" so the totals match Tufin.
SCOPE_FILTER    = "vendor='PALO_ALTO'"
PAGE_SIZE       = 500
VERIFY_TLS      = False
TIMEOUT         = 120

CAMPAIGN_START  = "2026-09-24"   # certifications before this are an older campaign -> Pending

SCRIPT_DIR      = Path(__file__).resolve().parent
SHARED_ROOT     = SCRIPT_DIR.parent                      # .../NPS-Automation
# Owner sheets: the SharedData subfolder inside the synced HRV Power BI folder. If that
# folder isn't there, falls back to the repo's SharedData. The run log prints which one.
DATA_DIR_SHAREPOINT = Path(os.path.expandvars(
    r"%USERPROFILE%\OneDrive - PGE\Cybersecurity Network Protection Services - HRV Power BI\SharedData"))
DATA_DIR        = DATA_DIR_SHAREPOINT if DATA_DIR_SHAREPOINT.is_dir() else SHARED_ROOT / "SharedData"
INPUT_GLOB      = ["*.xlsx", "*.xlsm", "*.csv"]
INPUT_EXCLUDE   = ["~$*", "*TEST*", "*test*", "HRV_Owner_Recert_Status*", "Rule-ID-Mapping*",
                   "decision_conflicts*", "scope_dropped*"]

# HRV Power BI folder (Cybersecurity Network Protection Services site, Shared Documents),
# synced to this PC. SharePoint: https://pge.sharepoint.com/sites/msteams_8a1a57/Shared%20Documents/HRV%20Power%20BI
# Either "Sync" or "Add shortcut to My files" works. The script searches the OneDrive /
# synced-site folders under your user profile for a folder named OUTPUT_FOLDER_NAME
# (it must sit inside a "Cybersecurity Network Protection Services" path). If it isn't
# found the run stops - it never silently writes somewhere Power BI can't see.
OUTPUT_FOLDER_NAME = "HRV Power BI"
SITE_HINT          = "Cybersecurity Network Protection Services"
OUTPUT_DIR      = r"%USERPROFILE%\OneDrive - PGE\Cybersecurity Network Protection Services - HRV Power BI"
                         # None = search instead
OUTPUT_NAME     = "HRV_Owner_Recert_Status.xlsx"         # keep fixed - Power BI points at it
# Power BI time-series file: one row per App ID per run date, appended each run (a rerun on
# the same date replaces that date's rows). Fixed name and column order - add new columns
# only at the end.
METRICS_NAME    = "HRV_Recert_Metrics.csv"
SHEET_NAME      = "Owner Status"   # per App ID / role / owner summary (kept for existing reports)
RULES_SHEET     = "Rules"          # one row per rule - use this for Power BI / dashboards
OWNERS_SHEET    = "Owners"         # App ID -> role -> owner, links to Rules on App ID

# RAG on the last certification date (any campaign): Green = within RAG_GREEN_MONTHS,
# Amber = RAG_GREEN_MONTHS to RAG_RED_MONTHS, Red = older, or never certified.
RAG_GREEN_MONTHS = 9
RAG_RED_MONTHS   = 12

# Sheet column aliases - first header found wins (headers differ across the eleven lists)
COL_APP_ID   = ["App-ID", "Application ID", "AppID", "App ID", "APP ID", "Single APPID"]
ROLE_COLUMNS = ["IT SME", "IT SME Backup", "IT Lead", "IT Lead Delegate",
                "Client Owner", "IT Director", "IT Senior Leader"]
COL_AMPS     = ["Source AMPS owners list", "Destination AMPS owners list"]
NO_APP       = "No App ID"
NO_OWNER     = "Owner unknown"
SA_ROLE      = "SecureApp Owner"
# ══════════════════════════════════════════════════════════════════════

def resolve_out_dir():
    if OUTPUT_DIR:
        p = Path(os.path.expandvars(OUTPUT_DIR))
        if p.is_dir():
            return p
        log(f"  OUTPUT_DIR not found ({p}) - searching instead")
    home = Path(os.environ.get("USERPROFILE") or Path.home())
    roots = [d for d in home.iterdir() if d.is_dir() and
             (d.name.startswith("OneDrive") or d.name.upper().replace("&", "") == "PGE")]
    hits = []
    for root in roots:                         # synced site: <root>\<Site> - Documents\HRV Power BI
        for depth in ("*", "*/*", "*/*/*"):    # shortcut:    <root>\HRV Power BI (or a level down)
            for p in root.glob(f"{depth}"):
                if p.name.endswith(OUTPUT_FOLDER_NAME) and p.is_dir():
                    hits.append(p)
    hits = list(dict.fromkeys(hits))
    preferred = [p for p in hits if SITE_HINT.lower() in str(p).lower()]
    if preferred or hits:
        found = (preferred or hits)[0]
        if len(hits) > 1:
            log(f"  several '{OUTPUT_FOLDER_NAME}' folders found, using {found}: {hits}")
        return found
    raise SystemExit("HRV Power BI folder is not synced to this PC. In SharePoint open "
                     "Shared Documents > HRV Power BI and click Sync (or Add shortcut to My files), "
                     "then run again. Or set OUTPUT_DIR to the local folder path.")


OUT_DIR = None
HEARTBEAT_DIR = SHARED_ROOT / "heartbeats"
CORPID_RE = re.compile(r"^(.*?)\s*\(([A-Za-z0-9]{3,8})\)\s*$")
APP_RE = re.compile(r"APP[-_ ]?(\d+)", re.I)


def log(msg):
    print(f"{datetime.now():%H:%M:%S} {msg}", flush=True)


def app_ids(text):
    """'app_id: APP-1980' / 'APP-1980, APP-22' / '1980' -> ['APP-1980', ...]"""
    s = str(text or "").strip()
    if s.isdigit():
        return [f"APP-{s}"]
    return list(dict.fromkeys(f"APP-{n}" for n in APP_RE.findall(s)))


def find_col(header, names):
    low = [h.lower() for h in header]
    return next((low.index(n.lower()) for n in names if n.lower() in low), None)


# ───────────────────────── owner phone book (sheets) ─────────────────────────

def people(cell, role):
    """'Last, First (CORPID)' -> list of (role, corpid, name, email). Splits on ; or newline."""
    out = []
    for part in re.split(r"[;\n]", str(cell or "")):
        m = CORPID_RE.match(part.strip())
        if m:
            cid = m.group(2).upper()
            out.append((role, cid, m.group(1).strip(), f"{cid}@pge.com"))
    return out


ROLE_ALIASES = {r.lower(): r for r in ROLE_COLUMNS}
ROLE_ALIASES.update({"it sme back up": "IT SME Backup"})
_AMPS_ENTRY = re.compile(r"\n(?=\s*[\w.:/-]+\s*=\s*\{)")
_AMPS_APP = re.compile(r"""['"](APP-[A-Za-z0-9]+)['"]""")
_AMPS_ROLE = re.compile(r"""(['"])([^'"]+?)\1\s*:\s*(?:'([^']*?\([A-Za-z0-9]{3,8}\))'|"([^"]*?\([A-Za-z0-9]{3,8}\))")""")


def parse_amps(cell):
    """AMPS owners text -> {APP-ID: [owner, ...]}. 'Skip AMPS ...' / blank -> {}."""
    out = {}
    s = str(cell or "").strip()
    if not s or s.lower().startswith("skip amps"):
        return out
    for chunk in _AMPS_ENTRY.split(s):
        apps = _AMPS_APP.findall(chunk)
        if not apps:
            continue
        lst = out.setdefault(apps[0].upper(), [])
        for _q, k, v1, v2 in _AMPS_ROLE.findall(chunk):
            role = ROLE_ALIASES.get(k.strip().lower())
            if role:
                lst += people(v1 or v2, role)
    return out


def read_rows(path):
    """Header + data rows of the first tab. Header = first row (of 20) with owner columns."""
    if path.suffix.lower() == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    else:
        try:
            wb = load_workbook(path, read_only=True, data_only=True)
        except PermissionError:
            raise SystemExit(f"{path.name} is open in Excel - close it and run again.")
        rows = [list(r) for r in wb[wb.sheetnames[0]].iter_rows(values_only=True)]
        wb.close()
    for i, row in enumerate(rows[:20]):
        header = [str(h).strip() if h is not None else "" for h in row]
        if any(h in header for h in ROLE_COLUMNS + COL_AMPS):
            return header, rows[i + 1:]
    return None, []


def load_phonebook():
    """{APP-ID: set((role, corpid, name, email))} from every owner sheet in SharedData."""
    files = sorted({f for p in INPUT_GLOB for f in DATA_DIR.glob(p)
                    if f.is_file() and not any(fnmatch(f.name, x) for x in INPUT_EXCLUDE)})
    book, report = defaultdict(set), []
    for f in files:
        header, rows = read_rows(f)
        if header is None:
            report.append((f.name, "no owner columns - not used"))
            continue
        c_app = find_col(header, COL_APP_ID)
        roles = {r: header.index(r) for r in ROLE_COLUMNS if r in header}
        amps = [i for i in (find_col(header, [a]) for a in COL_AMPS) if i is not None]
        before = sum(len(v) for v in book.values())
        for row in rows:
            g = lambda i: row[i] if i is not None and i < len(row) else None
            for i in amps:
                for app, owners in parse_amps(g(i)).items():
                    book[app].update(owners)
            if roles and c_app is not None:
                for app in app_ids(g(c_app)):
                    for role, i in roles.items():
                        book[app].update(people(g(i), role))
        added = sum(len(v) for v in book.values()) - before
        fmt = "AMPS" if amps else ("roles" if c_app is not None else "roles, no App-ID column - not used")
        report.append((f.name, f"{fmt}, {added} new app-owner entries"))
        log(f"  {f.name}: {fmt}, +{added}")
    return book, report


# ─────────────────────────────── Tufin ────────────────────────────────

class Tufin:
    """GraphQL client: Keycloak password grant, token refreshed on 401."""

    def __init__(self):
        self.user = os.environ.get("SECURETRACK_USER") or input("SecureTrack user: ").strip()
        self.pw = os.environ.get("SECURETRACK_PASSWORD") or getpass.getpass("SecureTrack password: ")
        self.token = None

    def login(self):
        r = requests.post(
            f"https://{TUFIN_HOST}/auth/realms/tufin-realm/protocol/openid-connect/token",
            data={"grant_type": "password", "client_id": "admin-cli",
                  "username": self.user, "password": self.pw},
            verify=VERIFY_TLS, timeout=TIMEOUT)
        if r.status_code != 200:
            raise SystemExit(f"Tufin login failed ({r.status_code}): {r.text[:200]}")
        self.token = r.json()["access_token"]

    def query(self, q, variables=None, retry=True):
        if not self.token:
            self.login()
        r = requests.post(f"https://{TUFIN_HOST}/v2/api/sync/graphql",
                          json={"query": q, "variables": variables or {}},
                          headers={"Authorization": f"Bearer {self.token}"},
                          verify=VERIFY_TLS, timeout=TIMEOUT)
        if r.status_code == 401 and retry:
            self.token = None
            return self.query(q, variables, retry=False)
        r.raise_for_status()
        data = r.json()
        if data.get("errors"):
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        return data["data"]


RULES_QUERY = """
query Scope($filter: String!, $first: Int!, $offset: Long!) {
  rules(filter: $filter) {
    count
    values(first: $first, offset: $offset) {
      id
      idOnDevice
      name
      disabled
      timeLastModified
      device { name }
      ruleUserData {
        ruleDescription
        saApplications { name owner }
        certification { status timeCertified timeExpiration }
      }
    }
  }
}"""
COUNT_QUERY = "query C($filter: String!) { rules(filter: $filter) { count } }"


def fetch_rules(t):
    rules, offset, total = [], 0, None
    while True:
        block = t.query(RULES_QUERY, {"filter": SCOPE_FILTER, "first": PAGE_SIZE,
                                      "offset": offset})["rules"]
        total = block.get("count", total)
        vals = block.get("values") or []
        for v in vals:
            ud = v.get("ruleUserData") or {}
            cert = ud.get("certification") or {}
            rules.append({"id": str(v.get("id")),
                          "device": (v.get("device") or {}).get("name") or "",
                          "rule": v.get("idOnDevice") or v.get("name") or "",
                          "disabled": bool(v.get("disabled")),
                          "modified": v.get("timeLastModified"),
                          "apps": app_ids(ud.get("ruleDescription")),
                          "sa": ud.get("saApplications") or [],
                          "status": cert.get("status"), "time": cert.get("timeCertified"),
                          "expires": cert.get("timeExpiration")})
        offset += PAGE_SIZE
        log(f"  Tufin: {min(offset, total or 0):,} of {total:,} rules")
        if not vals or offset >= (total or 0):
            break
    return rules


def status_of(rule, start):
    if not rule["status"] or not rule["time"]:
        return "Pending"
    if datetime.fromisoformat(rule["time"].replace("Z", "+00:00")) < start:
        return "Pending"
    return {"CERTIFIED": "Certified", "DECERTIFIED": "Decertified"}.get(rule["status"], "Pending")


# ─────────────────────────────── output ───────────────────────────────

DUE_COLS = ["Needs Recertification", "Overdue", "Due 0-15 Days", "Due 16-30 Days",
            "Due 31-60 Days"]
HEADERS = (["App ID", "Role", "Owner Name", "LAN ID", "Email", "Total Rules", "Certified",
            "Decertified", "Pending", "% Complete", "Status"] + DUE_COLS + ["Last Updated"])


def due_bucket(rule, now):
    """From the certification expiry date. Never certified counts as Overdue."""
    exp = parse_dt(rule.get("expires"))
    if exp is None:
        return "Overdue", None
    days = (exp - now).days
    if days < 0:
        return "Overdue", days
    if days <= 15:
        return "Due 0-15 Days", days
    if days <= 30:
        return "Due 16-30 Days", days
    if days <= 60:
        return "Due 31-60 Days", days
    return "Not Due", days


def build_rows(rules, book, start):
    per_app = defaultdict(lambda: defaultdict(int))     # app -> status counts
    sa_owner = defaultdict(set)                         # app -> SecureApp owners (same APP no.)
    now = datetime.now()
    for r in rules:
        st = status_of(r, start)
        r["st"] = st
        r["due"], r["days_left"] = due_bucket(r, now)
        for app in r["apps"] or [NO_APP]:
            per_app[app][st] += 1
            per_app[app]["total"] += 1
            if r["due"] != "Not Due":
                per_app[app][r["due"]] += 1
                per_app[app]["Needs Recertification"] += 1
            for sa in r["sa"]:
                if sa.get("owner") and app in app_ids(sa.get("name")):
                    cid = str(sa["owner"]).upper()
                    sa_owner[app].add((SA_ROLE, cid, "", f"{cid}@pge.com"))
    today = datetime.now().strftime("%Y-%m-%d")
    out, unknown = [], 0
    for app in sorted(per_app, key=lambda a: (a == NO_APP, a)):
        c = per_app[app]
        done = c["Certified"] + c["Decertified"]
        status = "Complete" if done == c["total"] else "Not Started" if done == 0 else "In Progress"
        owners = book.get(app) or sa_owner.get(app)
        if not owners:
            unknown += app != NO_APP
            owners = {(NO_OWNER if app != NO_APP else "", "", "", "")}
        for role, cid, name, email in sorted(owners, key=lambda o: (ROLE_COLUMNS.index(o[0])
                                             if o[0] in ROLE_COLUMNS else 99, o[1])):
            out.append([app, role, name, cid, email, c["total"], c["Certified"],
                        c["Decertified"], c["Pending"], round(done / c["total"], 4), status]
                       + [c[d] for d in DUE_COLS] + [today])
    return out, unknown, sa_owner


# ─────────────────────────── rule-level tabs ───────────────────────────

def parse_dt(v):
    """Tufin ISO timestamp -> naive datetime (Excel/Power BI friendly), or None."""
    if not v:
        return None
    return datetime.fromisoformat(str(v).replace("Z", "+00:00")).replace(tzinfo=None)


def months_back(d, n):
    y, m = divmod(d.month - 1 - n, 12)
    year, month = d.year + y, m + 1
    import calendar
    return d.replace(year=year, month=month, day=min(d.day, calendar.monthrange(year, month)[1]))


def rag_of(last_cert, now):
    if last_cert is None:
        return "Red"
    if last_cert >= months_back(now, RAG_GREEN_MONTHS):
        return "Green"
    if last_cert >= months_back(now, RAG_RED_MONTHS):
        return "Amber"
    return "Red"


RULE_HEADERS = (["Rule ID", "Device", "Rule Name", "App ID", "All App IDs", "Disabled",
                 "Campaign Status", "Last Certification", "Certification Result",
                 "Certification Expires", "Days Until Expiry", "Due", "Days Since Certification", "RAG",
                 "Last Modified"] + ROLE_COLUMNS + ["Last Updated"])
OWNER_HEADERS = ["App ID", "Role", "Owner Name", "LAN ID", "Email"]


def owners_for(app, book, sa_owner):
    return book.get(app) or sa_owner.get(app) or set()


def build_rule_rows(rules, book, sa_owner):
    now = datetime.now()
    out = []
    for r in rules:
        apps = r["apps"]
        roles = defaultdict(list)
        for app in apps:
            for role, cid, name, _e in sorted(owners_for(app, book, sa_owner)):
                label = f"{name} ({cid})" if name else cid
                if role in ROLE_COLUMNS and label not in roles[role]:
                    roles[role].append(label)
        last = parse_dt(r["time"])
        out.append([r["id"], r["device"], r["rule"], apps[0] if apps else NO_APP,
                     ";".join(apps), "Yes" if r["disabled"] else "No", r["st"], last,
                     {"CERTIFIED": "Certified", "DECERTIFIED": "Decertified"}.get(r["status"], ""),
                     parse_dt(r["expires"]), r["days_left"], r["due"],
                     (now - last).days if last else None,
                     rag_of(last, now), parse_dt(r["modified"])]
                    + ["; ".join(roles[c]) for c in ROLE_COLUMNS] + [now.date()])
    return out


def build_owner_rows(rules, book, sa_owner):
    apps = sorted({a for r in rules for a in r["apps"]})
    out = []
    for app in apps:
        for role, cid, name, email in sorted(owners_for(app, book, sa_owner),
                                             key=lambda o: (ROLE_COLUMNS.index(o[0])
                                                            if o[0] in ROLE_COLUMNS else 99, o[1])):
            out.append([app, role, name, cid, email])
    return out


def add_table(wb, title, headers, rows, date_cols=(), pct_cols=()):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for r in rows:
        ws.append(r)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
    for i, h in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = max(12, min(len(h) + 4, 40))
        if h in date_cols:
            for (c,) in ws.iter_rows(min_row=2, min_col=i, max_col=i):
                c.number_format = "yyyy-mm-dd"
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws


def write_xlsx(rows, run_info, rule_rows=(), owner_rows=()):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
    for row in ws.iter_rows(min_row=2, min_col=10, max_col=10):
        row[0].number_format = "0%"
    for i, h in enumerate(HEADERS, 1):
        ws.column_dimensions[get_column_letter(i)].width = max(12, len(h) + 4)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    add_table(wb, RULES_SHEET, RULE_HEADERS, rule_rows,
              date_cols=("Last Certification", "Certification Expires", "Last Modified",
                         "Last Updated"))
    add_table(wb, OWNERS_SHEET, OWNER_HEADERS, owner_rows)
    info = wb.create_sheet("Run Info")
    for r in run_info:
        info.append(r)
    info.column_dimensions["A"].width = 45
    info.column_dimensions["B"].width = 45
    final, tmp = OUT_DIR / OUTPUT_NAME, OUT_DIR / ("~tmp_" + OUTPUT_NAME)
    wb.save(tmp)
    return replace_locked(tmp, final)


def replace_locked(tmp, final):
    """Always the same file - never a second copy. If it is locked (open in Excel, or OneDrive
    mid-upload) wait up to 10 minutes for it to free up, then stop with an error."""
    import time
    for attempt in range(60):
        try:
            os.replace(tmp, final)
            return final
        except PermissionError:
            if attempt == 0:
                log(f"  {final.name} is locked (open in Excel or OneDrive syncing) - "
                    f"waiting up to 10 minutes for it to close")
            time.sleep(10)
    tmp.unlink(missing_ok=True)
    raise SystemExit(f"{final.name} stayed locked for 10 minutes - close it in Excel "
                     f"(desktop and SharePoint/Teams) and rerun. Nothing was written.")


# ─────────────────────────── Power BI metrics CSV ───────────────────────────

METRIC_ROLE_COLS = [r.replace(" ", "_") for r in ROLE_COLUMNS]
METRIC_HEADERS = (["Date", "App_ID"] + METRIC_ROLE_COLS +
                  ["Due_0_15_Days", "Due_16_30_Days", "Due_31_60_Days", "Recertified",
                   "Overdue", "Total_Rules"])


def clean(v):
    """No leading/trailing/double spaces - Power BI matching is exact."""
    return " ".join(str(v).split()) if v not in (None, "") else ""


def build_metric_rows(rules, book, sa_owner, run_date):
    """One row per App ID. Recertified = currently certified and not yet expired."""
    now = datetime.now()
    per_app = defaultdict(lambda: defaultdict(int))
    for r in rules:
        exp = parse_dt(r.get("expires"))
        current = r.get("status") == "CERTIFIED" and exp is not None and exp >= now
        for app in r["apps"] or [NO_APP]:
            c = per_app[app]
            c["Total_Rules"] += 1
            c["Recertified"] += current
            c[{"Overdue": "Overdue", "Due 0-15 Days": "Due_0_15_Days",
               "Due 16-30 Days": "Due_16_30_Days", "Due 31-60 Days": "Due_31_60_Days"}
              .get(r["due"], "Not_Due")] += 1
    out = []
    for app in sorted(per_app, key=lambda a: (a == NO_APP, a)):
        roles = defaultdict(list)
        if app != NO_APP:
            for role, cid, name, _e in sorted(owners_for(app, book, sa_owner)):
                label = clean(f"{name} ({cid})" if name else cid)
                if role in ROLE_COLUMNS and label not in roles[role]:
                    roles[role].append(label)
        c = per_app[app]
        out.append([run_date, clean(app)] + ["; ".join(roles[r]) for r in ROLE_COLUMNS]
                   + [c["Due_0_15_Days"], c["Due_16_30_Days"], c["Due_31_60_Days"],
                      c["Recertified"], c["Overdue"], c["Total_Rules"]])
    return out


def write_metrics_csv(metric_rows, run_date):
    """Append this run's rows to the history file, replacing any rows for the same date."""
    final, tmp = OUT_DIR / METRICS_NAME, OUT_DIR / ("~tmp_" + METRICS_NAME)
    keep = []
    if final.exists():
        with open(final, newline="", encoding="utf-8-sig") as f:
            rd = csv.reader(f)
            header = next(rd, None)
            if header and header[:len(METRIC_HEADERS)] == METRIC_HEADERS[:len(header)]:
                keep = [row for row in rd if row and row[0] != run_date]
            elif header:
                log(f"  {METRICS_NAME} has different columns - starting a new history")
    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(METRIC_HEADERS)
        for row in keep:
            w.writerow(row + [""] * (len(METRIC_HEADERS) - len(row)))
        w.writerows(metric_rows)
    replace_locked(tmp, final)
    return final, len(keep)


def heartbeat(status, message=""):
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    (HEARTBEAT_DIR / "hrv_owner_export.json").write_text(json.dumps(
        {"time": datetime.now().isoformat(timespec="seconds"), "status": status,
         "message": message}, indent=1))


def run():
    global OUT_DIR
    OUT_DIR = resolve_out_dir()
    log(f"Output folder: {OUT_DIR}")
    start = datetime.fromisoformat(CAMPAIGN_START).replace(tzinfo=timezone.utc)
    log(f"Owner phone book from {DATA_DIR}")
    book, report = load_phonebook()
    log(f"  {len(book):,} App IDs with owners")
    t = Tufin()
    log(f"Pulling rules from Tufin: {SCOPE_FILTER}")
    rules = fetch_rules(t)
    untagged = sum(1 for r in rules if not r["apps"])
    rows, unknown, sa_owner = build_rows(rules, book, start)
    rule_rows = build_rule_rows(rules, book, sa_owner)
    owner_rows = build_owner_rows(rules, book, sa_owner)
    due = defaultdict(int)
    for r in rules:
        due[r["due"]] += 1
    rag = defaultdict(int)
    for r in rule_rows:
        rag[r[RULE_HEADERS.index("RAG")]] += 1

    counts = defaultdict(int)
    for r in rules:
        counts[r["st"]] += 1
    apps = {a for r in rules for a in r["apps"]}
    run_info = [["Run time", datetime.now().strftime("%Y-%m-%d %H:%M")],
                ["Scope (Tufin filter)", SCOPE_FILTER],
                ["Campaign start", CAMPAIGN_START],
                ["Rules in scope", len(rules)],
                *[[k, counts[k]] for k in ("Certified", "Decertified", "Pending")],
                ["App IDs", len(apps)],
                ["App IDs with no owner in any sheet", unknown],
                ["Rules with no app_id (counted under No App ID)", untagged],
                *[[f"{d} (rules)", due[d]] for d in DUE_COLS[1:] + ["Not Due"]],
                [f"RAG Green (certified within {RAG_GREEN_MONTHS} months)", rag["Green"]],
                [f"RAG Amber ({RAG_GREEN_MONTHS}-{RAG_RED_MONTHS} months)", rag["Amber"]],
                [f"RAG Red (over {RAG_RED_MONTHS} months or never)", rag["Red"]],
                [], ["Owner sheet", "Used as"], *report]
    path = write_xlsx(rows, run_info, rule_rows, owner_rows)
    run_date = datetime.now().strftime("%Y-%m-%d")
    metric_rows = build_metric_rows(rules, book, sa_owner, run_date)
    mpath, prior = write_metrics_csv(metric_rows, run_date)
    log(f"Metrics: {len(metric_rows):,} App ID rows for {run_date} (+{prior:,} earlier rows kept) "
        f"-> {mpath}")
    log(f"{len(rules):,} rules, {len(apps):,} apps: "
        + ", ".join(f"{k} {v:,}" for k, v in counts.items())
        + f" | {unknown} apps without owners | {untagged:,} rules with no App ID")
    log(f"Owner Status {len(rows):,} rows | Rules {len(rule_rows):,} | Owners {len(owner_rows):,} "
        f"| RAG G/A/R {rag['Green']:,}/{rag['Amber']:,}/{rag['Red']:,} -> {path}")
    return f"{len(rules)} rules, {len(rows)} rows"


if __name__ == "__main__":
    try:
        heartbeat("ok", run())
    except SystemExit as e:
        heartbeat("failed", str(e))
        log(str(e))
        sys.exit(1)
    except Exception:
        tb = traceback.format_exc()
        heartbeat("failed", tb)
        log(tb)
        sys.exit(1)
