"""
profile_rule_export.py
======================
Read-only profiler for a Tufin rule-viewer CSV export.

Answers the questions that decide how the recert/tagging scripts should join and
what they can trust, WITHOUT reproducing the rule data itself. Output is counts,
percentages and column names only — no rule names, IPs, zones or comments — so
the report is safe to paste into a chat or a ticket.

Usage:
    py profile_rule_export.py Tools-Base-Rule_report_2026-09-08.csv

    (with no argument it looks for a single .csv in the current folder)

Stdlib only. Nothing to install. Opens the file read-only and writes nothing.
"""

import csv
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# Tufin exports put a preamble above the real header, so the header row is found
# by looking for a known column rather than assumed to be row 1.
HEADER_MARKERS = ("seq no.", "securetrack rule id", "id on device")

RECENT_DAYS = 90

# Header name -> the aliases seen in exports. Matching is case- and space-insensitive
# and falls back to "starts with", because Excel and the rule viewer truncate names.
WANTED = {
    "uid":        ["securetrack rule id", "securetrack ruleid", "securetrack id"],
    "id_on_dev":  ["id on device"],
    "rule_name":  ["rule name"],
    "device_id":  ["device id"],
    "device_nm":  ["device name"],
    "policy":     ["policy name"],
    "disabled":   ["disabled"],
    "last_hit":   ["last hit"],
    "last_mod":   ["last modified", "last modif"],
    "tags":       ["tags"],
    "comment":    ["comment"],
    "rule_desc":  ["rule description", "rule desc"],
    "app":        ["application"],
    "app_owner":  ["application owner"],
    "cert":       ["certification status", "certification"],
    "ticket_id":  ["ticket id"],
}

DATE_FORMATS = ["%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y", "%d/%m/%Y",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M"]

UID_RE = re.compile(r"^[A-Za-z0-9_\-]{20,24}==$")
FER_RE = re.compile(r"\bFER\s*\d{4,6}\b", re.IGNORECASE)


def find_file(argv):
    if len(argv) > 1:
        p = Path(argv[1])
        if not p.exists():
            sys.exit(f"Not found: {p}")
        return p
    here = sorted(Path(".").glob("*.csv"))
    if len(here) == 1:
        return here[0]
    if not here:
        sys.exit("No .csv in this folder. Pass the path as an argument.")
    sys.exit("Several .csv files here — pass the one you want as an argument:\n  "
             + "\n  ".join(p.name for p in here))


def read_rows(path):
    """Return (header, rows). Skips the export preamble above the real header."""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, newline="", encoding=encoding) as f:
                reader = csv.reader(f)
                header, rows = None, []
                for raw in reader:
                    if header is None:
                        low = [c.strip().lower() for c in raw]
                        if any(any(c.startswith(m) for m in HEADER_MARKERS) for c in low):
                            header = [c.strip() for c in raw]
                        continue
                    if any(str(c).strip() for c in raw):
                        rows.append(raw)
                if header is None:
                    sys.exit("Could not find the header row. Expected a column like "
                             "'Seq No.' or 'SecureTrack Rule ID'.")
                return header, rows
        except UnicodeDecodeError:
            continue
    sys.exit("Could not decode the file in utf-8 or latin-1.")


def map_columns(header):
    low = [h.strip().lower() for h in header]
    found = {}
    for key, aliases in WANTED.items():
        for i, h in enumerate(low):
            if h in aliases or any(h.startswith(a) for a in aliases):
                found[key] = i
                break
    return found


def cell(row, idx):
    if idx is None or idx >= len(row):
        return ""
    v = row[idx]
    return "" if v is None else str(v).strip()


def parse_date(value):
    if not value or set(value) == {"#"}:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            continue
    return None


def pct(n, total):
    return f"{100.0 * n / total:.1f}%" if total else "n/a"


def line(label, n, total, extra=""):
    print(f"  {label:<34}{n:>7,}  {pct(n, total):>7}  {extra}")


def main():
    path = find_file(sys.argv)
    header, rows = read_rows(path)
    col = map_columns(header)
    total = len(rows)

    print("=" * 74)
    print(f"  {path.name}")
    print(f"  {total:,} data rows, {len(header)} columns")
    print("=" * 74)

    missing = [k for k in ("uid", "id_on_dev", "rule_name") if k not in col]
    if missing:
        print(f"\n  MISSING EXPECTED COLUMNS: {missing}")
        print("  Column names found (first 40):")
        for h in header[:40]:
            print(f"    - {h}")
        print()

    # ── Join key ──────────────────────────────────────────────────────────
    print("\nJOIN KEY")
    if "uid" in col:
        uids = [cell(r, col["uid"]) for r in rows]
        present = [u for u in uids if u]
        wellformed = [u for u in present if UID_RE.match(u)]
        line("SecureTrack Rule ID present", len(present), total)
        line("looks like a valid UID", len(wellformed), total, "(ends ==)")
        dupes = [u for u, c in Counter(present).items() if c > 1]
        line("duplicate UIDs", len(dupes), total,
             "<- should be 0" if dupes else "")
        if present:
            lens = Counter(len(u) for u in present)
            print(f"  UID lengths seen: {dict(sorted(lens.items()))}")
    else:
        print("  No SecureTrack Rule ID column found.")

    # ── Name columns ──────────────────────────────────────────────────────
    if "id_on_dev" in col and "rule_name" in col:
        same = both = 0
        for r in rows:
            a, b = cell(r, col["id_on_dev"]), cell(r, col["rule_name"])
            if a and b:
                both += 1
                if a == b:
                    same += 1
        print("\nNAME COLUMNS")
        line("ID on Device == Rule Name", same, both or 1,
             "<- of rows where both are set")
        if both and same != both:
            print(f"  {both - same:,} row(s) disagree — the flip-flop, if it is here")

        names = [cell(r, col["rule_name"]) for r in rows]
        nonblank = [n for n in names if n]
        dupe_names = [n for n, c in Counter(nonblank).items() if c > 1]
        line("duplicate rule names", len(dupe_names), total,
             "<- why matching on name is fragile" if dupe_names else "")

    # ── Scope ─────────────────────────────────────────────────────────────
    print("\nSCOPE")
    for key, label in (("device_nm", "distinct device names"),
                       ("device_id", "distinct device IDs"),
                       ("policy", "distinct policy names")):
        if key in col:
            vals = {cell(r, col[key]) for r in rows if cell(r, col[key])}
            print(f"  {label:<34}{len(vals):>7,}")
    if "disabled" in col:
        dis = sum(1 for r in rows if cell(r, col["disabled"]).lower() == "true")
        line("already disabled", dis, total)

    # ── Hit data — the one that decides the safety guard ───────────────────
    print("\nHIT DATA  (decides whether the last-hit guard can be trusted here)")
    if "last_hit" in col:
        parsed, unparsed, blank = [], 0, 0
        for r in rows:
            raw = cell(r, col["last_hit"])
            if not raw or set(raw) == {"#"}:
                blank += 1
                continue
            d = parse_date(raw)
            if d:
                parsed.append(d)
            else:
                unparsed += 1
        line("has a last-hit date", len(parsed), total)
        line("blank / never hit", blank, total)
        if unparsed:
            line("present but unparsed", unparsed, total, "<- date format differs")
        if parsed:
            cutoff = datetime.now() - timedelta(days=RECENT_DAYS)
            recent = sum(1 for d in parsed if d >= cutoff)
            line(f"hit within {RECENT_DAYS} days", recent, total,
                 "<- these must never be disabled")
            print(f"  date range: {min(parsed):%Y-%m-%d} to {max(parsed):%Y-%m-%d}")
            years = Counter(d.year for d in parsed)
            print("  by year: " + ", ".join(f"{y}:{c}" for y, c in sorted(years.items())))
    else:
        print("  No Last Hit column found.")

    # ── Fields the tagging script writes to or reads ──────────────────────
    print("\nMETADATA FIELDS")
    if "rule_desc" in col:
        vals = [cell(r, col["rule_desc"]) for r in rows]
        nonblank = [v for v in vals if v]
        line("Rule Description populated", len(nonblank), total,
             "<- tagging writes here")
        if nonblank:
            multiline = sum(1 for v in nonblank if "\n" in v)
            has_appid = sum(1 for v in nonblank if "app_id" in v.lower())
            has_fer = sum(1 for v in nonblank if FER_RE.search(v))
            print(f"  of those: {multiline:,} multi-line, "
                  f"{has_appid:,} already contain 'app_id', {has_fer:,} contain a FER")
            print(f"  longest is {max(len(v) for v in nonblank):,} chars")
    if "comment" in col:
        vals = [cell(r, col["comment"]) for r in rows]
        nonblank = [v for v in vals if v]
        line("Comment populated", len(nonblank), total)
        line("Comment contains a FER", sum(1 for v in nonblank if FER_RE.search(v)), total)
    for key, label in (("app", "Application populated"),
                       ("app_owner", "Application Owner populated"),
                       ("tags", "Tags populated"),
                       ("cert", "Certification populated"),
                       ("ticket_id", "Ticket ID populated")):
        if key in col:
            n = sum(1 for r in rows if cell(r, col[key]))
            line(label, n, total)

    if "tags" in col:
        tags = Counter()
        for r in rows:
            for t in re.split(r"[,;|]", cell(r, col["tags"])):
                t = t.strip()
                if t:
                    tags[t] += 1
        if tags:
            print("\n  tag values (top 10):")
            for t, c in tags.most_common(10):
                print(f"    {t:<28}{c:>7,}")

    print("\n" + "=" * 74)
    print("  No rule names, addresses, zones or comment text appear above.")
    print("=" * 74 + "\n")


if __name__ == "__main__":
    main()
