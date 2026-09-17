"""
verify_run.py
=============
Check the output of a tag_app_ids.py / recert_processor.py run and print a verdict.

Reads the plan workbooks, reconciles the counts against each other, runs the
integrity checks, and prints a short report. No intermediate file — run it after
every run and read the last line.

Unlike audit_outputs.py this produces no data file and exposes no rule content. The
output is counts and pass/fail only, so it is safe to screenshot or paste anywhere.

USAGE
  Put this beside recert_output/ and tag_output/, then:

      py verify_run.py

  Exit code is 0 when everything passes, 1 when anything fails.
"""

import sys
from collections import Counter
from pathlib import Path

OUTPUT_DIRS = ["recert_output", "tag_output"]
RLM_MARKER = "##RLM##"

PASS, FAIL, WARN = "PASS", "FAIL", "warn"
results = []


def check(ok, label, detail=""):
    results.append((PASS if ok else FAIL, label, detail))
    return ok


def note(label, detail=""):
    results.append((WARN, label, detail))


def load(path):
    from openpyxl import load_workbook
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
    except PermissionError:
        return None, None, "open in Excel"
    except Exception as e:
        return None, None, str(e)[:50]
    ws = wb[wb.sheetnames[0]]
    it = ws.iter_rows(values_only=True)
    try:
        headers = [str(h).strip() if h is not None else "" for h in next(it)]
    except StopIteration:
        wb.close()
        return [], [], None
    rows = [list(r) for r in it if any(v is not None and str(v).strip() for v in r)]
    wb.close()
    return headers, rows, None


def col(headers, name):
    low = [h.lower() for h in headers]
    return low.index(name.lower()) if name.lower() in low else None


def val(row, i):
    if i is None or i >= len(row) or row[i] is None:
        return ""
    return str(row[i]).strip()


def uids(book):
    if not book:
        return set()
    h, r = book
    i = col(h, "rule_uid")
    return {val(x, i) for x in r if val(x, i)} if i is not None else set()


def main():
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        sys.exit("openpyxl is required:  py -m pip install openpyxl")

    here = Path(__file__).resolve().parent
    books, skipped = {}, []

    for d in OUTPUT_DIRS:
        folder = here / d
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.xlsx")):
            if path.name.startswith("~$"):
                continue
            h, r, err = load(path)
            if err:
                skipped.append((path.name, err))
                continue
            books[path.stem] = (h, r)

    if not books:
        sys.exit("No .xlsx found in " + " or ".join(OUTPUT_DIRS))

    print("=" * 66)
    print("  RUN VERIFICATION")
    print("=" * 66)
    for name in sorted(books):
        print(f"  {name:<32}{len(books[name][1]):>8,} rows")
    for name, err in skipped:
        print(f"  {name:<32}{'SKIPPED':>8}  ({err})")
        note(f"{name} not checked", err)

    headline = {}

    # ── tag_plan ────────────────────────────────────────────────────────
    if "tag_plan" in books:
        h, rows = books["tag_plan"]
        i_uid  = col(h, "rule_uid")
        i_app  = col(h, "app_ids")
        i_skip = col(h, "skip")
        i_old  = col(h, "old_description")
        i_new  = col(h, "new_description")
        i_act  = col(h, "action")

        total = len(rows)
        uid_vals = [val(r, i_uid) for r in rows]
        dupes = sum(1 for _, c in Counter(u for u in uid_vals if u).items() if c > 1)

        skip_t = skip_f = 0
        app_filled = no_app = rlm = rlm_marker = 0
        skip_changed = write_empty = write_no_app = rlm_not_skipped = 0
        new_filled = old_filled = 0

        for r in rows:
            skipped_row = val(r, i_skip).upper() == "TRUE"
            old, new = val(r, i_old), val(r, i_new)
            app, act = val(r, i_app), val(r, i_act)
            skip_t += skipped_row
            skip_f += not skipped_row
            app_filled += bool(app)
            new_filled += bool(new)
            old_filled += bool(old)
            # Count RLM by the ACTION, not by the marker. build_new_description checks
            # "no app id" first, so a rule with an RLM description AND no app id is
            # classified as no-app-id. Counting by marker would double-count it.
            if RLM_MARKER in act:
                rlm += 1
            if RLM_MARKER in old:
                rlm_marker += 1
                if not skipped_row:
                    rlm_not_skipped += 1
            if "no app id" in act.lower():
                no_app += 1
            if skipped_row and old != new:
                skip_changed += 1
            if not skipped_row:
                if not new:
                    write_empty += 1
                if not app:
                    write_no_app += 1

        preserved = sum(1 for r in rows
                        if val(r, i_skip).upper() == "TRUE" and val(r, i_old))

        print("\n  TAG_PLAN RECONCILIATION")
        checks = [
            (app_filled == skip_f + rlm,
             "app_ids filled = writable + RLM-skipped",
             f"{app_filled:,} = {skip_f:,} + {rlm:,}"),
            (rlm <= rlm_marker,
             "RLM action count <= rules with an RLM description",
             f"{rlm:,} <= {rlm_marker:,}"),
            (no_app == total - app_filled,
             "no-app-id = rows - app_ids filled",
             f"{no_app:,} = {total:,} - {app_filled:,}"),
            (skip_t == no_app + rlm,
             "skip TRUE = no-app-id + RLM",
             f"{skip_t:,} = {no_app:,} + {rlm:,}"),
            (skip_t + skip_f == total,
             "skip TRUE + FALSE = rows",
             f"{skip_t:,} + {skip_f:,} = {total:,}"),
            (new_filled == skip_f + preserved,
             "new_description filled = writable + preserved",
             f"{new_filled:,} = {skip_f:,} + {preserved:,}"),
        ]
        for ok, label, detail in checks:
            check(ok, label, detail)
            print(f"    [{PASS if ok else FAIL}] {label:<44} {detail}")

        print("\n  TAG_PLAN INTEGRITY")
        integ = [
            (dupes == 0,            "no duplicate rule_uid",          f"{dupes:,} found"),
            (rlm_not_skipped == 0,  "every ##RLM## rule is skipped",  f"{rlm_not_skipped:,} not skipped"),
            (skip_changed == 0,     "skipped rows left unchanged",    f"{skip_changed:,} changed"),
            (write_empty == 0,      "no empty new_description on a write", f"{write_empty:,} empty"),
            (write_no_app == 0,     "no write without an app id",     f"{write_no_app:,} found"),
        ]
        for ok, label, detail in integ:
            check(ok, label, detail)
            print(f"    [{PASS if ok else FAIL}] {label:<44} {detail}")

        headline["writable"] = (skip_f, total)
        headline["rlm"] = (rlm, total)
        headline["rlm_marker"] = (rlm_marker, total)
        headline["no_app"] = (no_app, total)

    # ── decision plans ──────────────────────────────────────────────────
    print("\n  DECISION PLAN INTEGRITY")

    def purity(name, column, expect):
        if name not in books:
            return
        h, rows = books[name]
        i = col(h, column)
        if i is None:
            return
        vals = Counter(val(r, i) for r in rows if val(r, i))
        bad = {k: v for k, v in vals.items() if k not in expect}
        ok = not bad
        check(ok, f"{name}: {column} only {sorted(expect)}",
              f"{dict(vals)}" if bad else f"{sum(vals.values()):,} rows")
        print(f"    [{PASS if ok else FAIL}] {name+': '+column:<44} "
              + (f"unexpected {bad}" if bad else f"all {sorted(expect)[0] if len(expect)==1 else 'valid'}"))

    purity("disable_plan", "hit_state", {"stale"})
    purity("held_back_from_disable", "hit_state", {"never", "recent"})

    pairs = [
        ("disable_plan", "held_back_from_disable", "both disabled and held back"),
        ("recertify_plan", "disable_plan", "both recertified and disabled"),
        ("recertify_plan", "held_back_from_disable", "recertify rule in cleanup hold-back"),
        ("need_assistance", "disable_plan", "need-assistance rule scheduled for disable"),
    ]
    for a, b, why in pairs:
        if a in books and b in books:
            overlap = uids(books[a]) & uids(books[b])
            ok = not overlap
            check(ok, f"no overlap: {a} / {b}", why)
            print(f"    [{PASS if ok else FAIL}] no overlap {a} / {b:<22} "
                  f"{len(overlap):,} shared")

    if "tag_plan" in books:
        tp = uids(books["tag_plan"])
        for n in ("recertify_plan", "disable_plan", "held_back_from_disable"):
            if n in books:
                missing = uids(books[n]) - tp
                ok = not missing
                check(ok, f"{n} UIDs all present in tag_plan", f"{len(missing):,} missing")
                print(f"    [{PASS if ok else FAIL}] {n+' UIDs in tag_plan':<44} "
                      f"{len(missing):,} missing")

    # ── headline numbers ────────────────────────────────────────────────
    print("\n  HEADLINE NUMBERS")
    if "writable" in headline:
        n, t = headline["writable"]
        print(f"    tagging: writable now              {n:>8,}  ({100*n/t:.1f}%)")
        n, t = headline["rlm"]
        print(f"    tagging: blocked on RLM format     {n:>8,}  ({100*n/t:.1f}%)")
        m, t = headline["rlm_marker"]
        if m != n:
            print(f"    tagging: have an RLM description   {m:>8,}  "
                  f"({m-n:,} of those also lack an app id)")
        n, t = headline["no_app"]
        print(f"    tagging: no app id in any sheet    {n:>8,}  ({100*n/t:.1f}%)")

    d = len(books["disable_plan"][1]) if "disable_plan" in books else 0
    hb = len(books["held_back_from_disable"][1]) if "held_back_from_disable" in books else 0
    if d or hb:
        tot = d + hb
        print(f"    cleanup: disable-able              {d:>8,}  ({100*d/tot:.1f}% of {tot:,})")
        print(f"    cleanup: held, no hit data         {hb:>8,}  ({100*hb/tot:.1f}%)")
    if "recertify_plan" in books:
        print(f"    recertify tickets planned          {len(books['recertify_plan'][1]):>8,}")
    if "decision_conflicts" in books:
        print(f"    decisions conflicting across lists {len(books['decision_conflicts'][1]):>8,}")
    if "need_assistance" in books:
        print(f"    need assistance                    {len(books['need_assistance'][1]):>8,}")

    # ── verdict ─────────────────────────────────────────────────────────
    failed = [r for r in results if r[0] == FAIL]
    warned = [r for r in results if r[0] == WARN]
    passed = [r for r in results if r[0] == PASS]

    print("\n" + "=" * 66)
    if failed:
        print(f"  FAILED — {len(failed)} check(s) did not pass")
        for _, label, detail in failed:
            print(f"    ! {label}  ({detail})")
    else:
        print(f"  ALL {len(passed)} CHECKS PASSED")
    for _, label, detail in warned:
        print(f"  ! {label} — {detail}")
    print("=" * 66 + "\n")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
