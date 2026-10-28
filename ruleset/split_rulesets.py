#!/usr/bin/env python3
"""Split an Illumio ruleset JSON export into smaller files for upload.

Usage:
    py split_rulesets.py Rulesets_JSON_....json            # ~900 KB chunks
    py split_rulesets.py Rulesets_JSON_....json 500        # ~500 KB chunks
    py split_rulesets.py Rulesets_JSON_....json 900 --slim # drop timestamps/authors

Writes <name>_part01.json, _part02.json, ... into a folder named <name>_split.
Each ruleset stays whole (never cut across files). Also writes an index file
listing which rulesets landed in which part.
"""
import json
import sys
from pathlib import Path

NOISE = {"created_at", "updated_at", "created_by", "updated_by",
         "deleted_at", "deleted_by", "update_type", "caps"}


def slim(obj):
    if isinstance(obj, dict):
        return {k: slim(v) for k, v in obj.items() if k not in NOISE}
    if isinstance(obj, list):
        return [slim(v) for v in obj]
    return obj


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    src = Path(args[0])
    limit = int(args[1]) * 1024 if len(args) > 1 else 900 * 1024
    do_slim = "--slim" in sys.argv

    with open(src, encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]
    if do_slim:
        data = slim(data)

    out_dir = src.with_name(src.stem + "_split")
    out_dir.mkdir(exist_ok=True)

    parts, cur, size = [], [], 2
    for rs in data:
        n = len(json.dumps(rs, indent=1)) + 2
        if cur and size + n > limit:
            parts.append(cur)
            cur, size = [], 2
        cur.append(rs)
        size += n
    if cur:
        parts.append(cur)

    index = []
    for i, chunk in enumerate(parts, 1):
        name = f"{src.stem}_part{i:02d}.json"
        with open(out_dir / name, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=1)
        for rs in chunk:
            index.append(f"{name}\t{len(rs.get('rules', []))} rules\t{rs.get('name', '?')}")
        kb = (out_dir / name).stat().st_size // 1024
        print(f"{name}: {len(chunk)} rulesets, {kb} KB")

    (out_dir / "index.txt").write_text("\n".join(index), encoding="utf-8")
    print(f"\n{len(data)} rulesets -> {len(parts)} files in {out_dir}")


if __name__ == "__main__":
    main()
