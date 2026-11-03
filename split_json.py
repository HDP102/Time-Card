#!/usr/bin/env python3
"""Split any large Illumio JSON export (workloads, inventory, rulesets, labels)
into smaller files for upload.

Usage:
    py split_json.py Workloads_AllLabels_JSON_....json
    py split_json.py Inventory.json 900 --slim
    py split_json.py Inventory.json 900 --slim --out C:\\Users\\CF02639\\Downloads\\split

Arguments:
    file        the JSON export (must be a JSON array, as Illumio exports are)
    size        target KB per part (default 900)
    --slim      drop bulky fields not needed for policy work (timestamps,
                authors, open service ports, agent/VEN detail, vulnerabilities)
    --out DIR   folder to write parts into. Default: a new folder named
                <file>_split created next to the export.

Each record stays whole (never cut across files). An index.txt lists which
record (by name/hostname) landed in which part.
"""
import json
import sys
from pathlib import Path

NOISE = {
    "created_at", "updated_at", "created_by", "updated_by",
    "deleted_at", "deleted_by", "update_type", "caps",
    "services", "agent", "vulnerabilities_summary", "vulnerability_summary",
    "detected_vulnerabilities", "ike_authentication_certificate",
    "container_cluster", "selectively_enforced_services",
}


def slim(obj):
    if isinstance(obj, dict):
        return {k: slim(v) for k, v in obj.items() if k not in NOISE}
    if isinstance(obj, list):
        return [slim(v) for v in obj]
    return obj


def label_for(rec):
    if not isinstance(rec, dict):
        return "?"
    for k in ("name", "hostname", "value", "href"):
        if rec.get(k):
            return str(rec[k])
    return "?"


def parse_args(argv):
    args, out, do_slim = [], None, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--slim":
            do_slim = True
        elif a == "--out":
            i += 1
            out = argv[i]
        else:
            args.append(a)
        i += 1
    return args, out, do_slim


def main():
    args, out, do_slim = parse_args(sys.argv[1:])
    if not args:
        sys.exit(__doc__)
    src = Path(args[0])
    limit = int(args[1]) * 1024 if len(args) > 1 else 900 * 1024

    with open(src, encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    if do_slim:
        data = slim(data)

    out_dir = Path(out) if out else src.with_name(src.stem + "_split")
    out_dir.mkdir(parents=True, exist_ok=True)

    parts, cur, size = [], [], 2
    for rec in data:
        n = len(json.dumps(rec, indent=1)) + 2
        if cur and size + n > limit:
            parts.append(cur)
            cur, size = [], 2
        cur.append(rec)
        size += n
    if cur:
        parts.append(cur)

    index = []
    for i, chunk in enumerate(parts, 1):
        name = f"{src.stem}_part{i:02d}.json"
        with open(out_dir / name, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=1)
        index += [f"{name}\t{label_for(r)}" for r in chunk]
        kb = (out_dir / name).stat().st_size // 1024
        print(f"{name}: {len(chunk)} records, {kb} KB")

    (out_dir / "index.txt").write_text("\n".join(index), encoding="utf-8")
    print(f"\n{len(data)} records -> {len(parts)} files in {out_dir}")


if __name__ == "__main__":
    main()
