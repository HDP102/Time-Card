"""
audit_outputs.py
================
Audit the output workbooks produced by tag_app_ids.py and recert_processor.py, and
emit a single Python file capturing the result.

WHY THIS EXISTS
  The plan files run to tens of thousands of rows, which is too much to eyeball and
  too much to hand to anyone for review. This reduces them to the things that actually
  determine whether a run is correct: complete statistics, cross-file consistency,
  every anomaly found, and a small sample of real rows to confirm formatting.

  It reads only. It never modifies a plan file.

USAGE
  Put this in the same folder as recert_output/ and tag_output/, then:

      py audit_outputs.py

  Writes audit_data.py beside it. That file is the thing to share for review.

WHAT GOES INTO audit_data.py
  - row counts, headers, and per-column fill rates for every workbook
  - value distributions for every low-cardinality column
  - cross-file integrity checks (overlaps that should not exist, totals that should
    reconcile)
  - every anomaly found, with counts and examples
  - decision_conflicts in full when small — it is the file needing human review
  - SAMPLE_ROWS rows per workbook, taken from the start, middle and end

  Rule names and UIDs appear in the samples and anomaly examples. Set SAMPLE_ROWS = 0
  to reduce that to statistics only.
"""

import datetime
import pprint
import re
import sys
from collections import Counter
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

OUTPUT_DIRS = ["recert_output", "tag_output"]
OUT_FILE    = "audit_data.py"

SAMPLE_ROWS = 15          # rows kept per workbook (0 = statistics only)
FULL_IF_UNDER = 60        # workbooks smaller than this are captured in full
MAX_DISTINCT = 25         # a column with more distinct values than this is summarised
MAX_ANOMALY_EXAMPLES = 8

UID_RE = re.compile(r"^[A-Za-z0-9_\-]{20,24}==$")


def load(path):
    """Read a workbook into (headers, rows). Returns (None, None) on failure."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        sys.exit("openpyxl is required:  py -m pip install openpyxl")
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
    except PermissionError:
        print(f"  ! {path.name} is open in Excel — close it and re-run")
        return None, None
    except Exception as e:
        print(f"  ! {path.name}: {e}")
        return None, None

    ws = wb[wb.sheetnames[0]]
    it = ws.iter_rows(values_only=True)
    try:
        headers = [str(h).strip() if h is not None else "" for h in next(it)]
    except StopIteration:
        wb.close()
        return [], []
    rows = [list(r) for r in it if any(v is not None and str(v).strip() for v in r)]
    wb.close()
    return headers, rows


def cell(row, i):
    if i is None or i >= len(row) or row[i] is None:
        return ""
    return str(row[i]).strip()


def col_index(headers, name):
    low = [h.lower() for h in headers]
    n = name.lower()
    return low.index(n) if n in low else None


def profile(headers, rows):
    """Per-column fill rate and value distribution."""
    out = {}
    total = len(rows)
    for i, h in enumerate(headers):
        vals = [cell(r, i) for r in rows]
        filled = sum(1 for v in vals if v)
        distinct = Counter(v for v in vals if v)
        entry = {
            "filled": filled,
            "fill_pct": round(100.0 * filled / total, 1) if total else 0.0,
            "distinct": len(distinct),
        }
        if 0 < len(distinct) <= MAX_DISTINCT:
            entry["values"] = dict(distinct.most_common())
        else:
            entry["top_5"] = dict(distinct.most_common(5))
        out[h] = entry
    return out


def sample(headers, rows):
    if SAMPLE_ROWS <= 0 or not rows:
        return []
    if len(rows) <= FULL_IF_UNDER:
        picks = rows
    else:
        n = max(1, SAMPLE_ROWS // 3)
        mid = len(rows) // 2
        picks = rows[:n] + rows[mid:mid + n] + rows[-n:]
    return [dict(zip(headers, [cell(r, i) for i in range(len(headers))]))
            for r in picks[:max(SAMPLE_ROWS, FULL_IF_UNDER if len(rows) <= FULL_IF_UNDER else 0)]]


def uid_set(headers, rows):
    i = col_index(headers, "rule_uid")
    if i is None:
        return set()
    return {cell(r, i) for r in rows if cell(r, i)}


# ─────────────────────────────────────────────
# Anomaly checks
# ─────────────────────────────────────────────

def check_uids(name, headers, rows, anomalies):
    i = col_index(headers, "rule_uid")
    if i is None:
        return
    uids = [cell(r, i) for r in rows]
    blank = sum(1 for u in uids if not u)
    if blank:
        anomalies.append({"file": name, "issue": "blank rule_uid", "count": blank})

    malformed = [u for u in uids if u and not UID_RE.match(u)]
    if malformed:
        anomalies.append({"file": name, "issue": "rule_uid not in expected format",
                          "count": len(malformed),
                          "examples": malformed[:MAX_ANOMALY_EXAMPLES]})

    dupes = [u for u, c in Counter(u for u in uids if u).items() if c > 1]
    if dupes:
        anomalies.append({"file": name, "issue": "duplicate rule_uid",
                          "count": len(dupes),
                          "examples": dupes[:MAX_ANOMALY_EXAMPLES]})


def check_tag_plan(headers, rows, anomalies):
    """A skipped row must be unchanged; a written row must have a new description."""
    i_skip = col_index(headers, "skip")
    i_old  = col_index(headers, "old_description")
    i_new  = col_index(headers, "new_description")
    i_act  = col_index(headers, "action")
    i_app  = col_index(headers, "app_ids")
    if None in (i_skip, i_old, i_new):
        return

    skip_but_changed = written_but_empty = write_without_app = 0
    for r in rows:
        skipped = cell(r, i_skip).upper() == "TRUE"
        old, new = cell(r, i_old), cell(r, i_new)
        if skipped and old != new:
            skip_but_changed += 1
        if not skipped:
            if not new:
                written_but_empty += 1
            if i_app is not None and not cell(r, i_app):
                write_without_app += 1

    if skip_but_changed:
        anomalies.append({"file": "tag_plan", "count": skip_but_changed,
                          "issue": "row marked skip but new_description differs from old "
                                   "— a skipped rule must be left untouched"})
    if written_but_empty:
        anomalies.append({"file": "tag_plan", "count": written_but_empty,
                          "issue": "row not skipped but new_description is empty"})
    if write_without_app:
        anomalies.append({"file": "tag_plan", "count": write_without_app,
                          "issue": "row would be written but has no app_ids"})

    # every RLM rule must be skipped
    if i_act is not None:
        rlm_written = sum(1 for r in rows
                          if "##RLM##" in cell(r, i_old)
                          and cell(r, i_skip).upper() != "TRUE")
        if rlm_written:
            anomalies.append({"file": "tag_plan", "count": rlm_written,
                              "issue": "rule has a ##RLM## description but is NOT skipped "
                                       "— the RLM guard should have caught it"})


def check_hit_states(name, headers, rows, expect, anomalies):
    i = col_index(headers, "hit_state")
    if i is None:
        return
    bad = [cell(r, i) for r in rows if cell(r, i) and cell(r, i) not in expect]
    if bad:
        anomalies.append({"file": name, "count": len(bad),
                          "issue": f"hit_state outside {sorted(expect)}",
                          "examples": sorted(set(bad))[:MAX_ANOMALY_EXAMPLES]})


def cross_checks(books, anomalies):
    """Overlaps that should not exist, and totals that should reconcile."""
    def uids(n):
        b = books.get(n)
        return uid_set(b["headers"], b["_rows"]) if b else set()

    checks = []
    pairs = [
        ("disable_plan", "held_back_from_disable",
         "a rule cannot be both scheduled for disable and held back"),
        ("recertify_plan", "disable_plan",
         "a rule cannot be both recertified and disabled"),
        ("recertify_plan", "held_back_from_disable",
         "a rule marked recertify should not be in the cleanup hold-back set"),
        ("need_assistance", "disable_plan",
         "a rule marked need-assistance should not be scheduled for disable"),
    ]
    for a, b, why in pairs:
        if a in books and b in books:
            overlap = uids(a) & uids(b)
            checks.append({"between": [a, b], "overlap": len(overlap), "expected": 0,
                           "ok": not overlap, "why": why,
                           "examples": sorted(overlap)[:MAX_ANOMALY_EXAMPLES]})
            if overlap:
                anomalies.append({"file": f"{a} / {b}", "count": len(overlap),
                                  "issue": f"UIDs in both files — {why}",
                                  "examples": sorted(overlap)[:MAX_ANOMALY_EXAMPLES]})

    # cleanup total should reconcile
    if "disable_plan" in books and "held_back_from_disable" in books:
        d = len(books["disable_plan"]["_rows"])
        h = len(books["held_back_from_disable"]["_rows"])
        checks.append({"metric": "cleanup decisions accounted for",
                       "disable_plan": d, "held_back": h, "total": d + h,
                       "note": "should equal the Cleanup/Remove count in the run log"})

    # every planned rule should also appear in tag_plan (same estate, same fetch)
    if "tag_plan" in books:
        tp = uids("tag_plan")
        for n in ("recertify_plan", "disable_plan", "held_back_from_disable"):
            if n in books:
                missing = uids(n) - tp
                checks.append({"metric": f"{n} UIDs present in tag_plan",
                               "missing": len(missing), "expected": 0,
                               "ok": not missing,
                               "examples": sorted(missing)[:MAX_ANOMALY_EXAMPLES]})
    return checks


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    here = Path(__file__).resolve().parent
    books, anomalies, files_seen = {}, [], []

    for d in OUTPUT_DIRS:
        folder = here / d
        if not folder.is_dir():
            print(f"  - {d}/ not found, skipping")
            continue
        for path in sorted(folder.glob("*.xlsx")):
            if path.name.startswith("~$"):
                continue
            headers, rows = load(path)
            if headers is None:
                continue
            name = path.stem
            files_seen.append(f"{d}/{path.name}")
            print(f"  {d}/{path.name}: {len(rows):,} rows")

            books[name] = {
                "folder": d,
                "file": path.name,
                "rows": len(rows),
                "headers": headers,
                "columns": profile(headers, rows),
                "sample": sample(headers, rows),
                "_rows": rows,
            }
            check_uids(name, headers, rows, anomalies)

    if not books:
        sys.exit("No .xlsx found in " + " or ".join(OUTPUT_DIRS) +
                 ". Run the scripts first, or check this file's location.")

    if "tag_plan" in books:
        b = books["tag_plan"]
        check_tag_plan(b["headers"], b["_rows"], anomalies)
    if "disable_plan" in books:
        b = books["disable_plan"]
        check_hit_states("disable_plan", b["headers"], b["_rows"], {"stale"}, anomalies)
    if "held_back_from_disable" in books:
        b = books["held_back_from_disable"]
        check_hit_states("held_back_from_disable", b["headers"], b["_rows"],
                         {"never", "recent"}, anomalies)

    checks = cross_checks(books, anomalies)

    for b in books.values():
        del b["_rows"]

    payload = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sample_rows_per_file": SAMPLE_ROWS,
        "files": files_seen,
        "workbooks": books,
        "integrity_checks": checks,
        "anomalies": anomalies,
    }

    out = here / OUT_FILE
    with open(out, "w", encoding="utf-8") as f:
        f.write('"""\n')
        f.write("audit_data.py — generated by audit_outputs.py. Do not edit by hand.\n\n")
        f.write("Statistics, integrity checks, anomalies and samples for the plan files\n")
        f.write("produced by tag_app_ids.py and recert_processor.py.\n")
        f.write('"""\n\n')
        f.write("DATA = ")
        f.write(pprint.pformat(payload, width=100, sort_dicts=False))
        f.write("\n")

    print(f"\n  {len(books)} workbook(s), {sum(b['rows'] for b in books.values()):,} rows")
    print(f"  {len(anomalies)} anomaly finding(s)")
    if anomalies:
        for a in anomalies[:10]:
            print(f"    ! {a['file']}: {a['issue']} ({a.get('count', '?')})")
    failed = [c for c in checks if c.get("ok") is False]
    print(f"  {len(checks) - len(failed)}/{len(checks)} integrity check(s) passed")
    for c in failed:
        print(f"    ! {c.get('between') or c.get('metric')}")
    print(f"\n  Written: {out}")
    print(f"  Size: {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
