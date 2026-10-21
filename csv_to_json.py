#!/usr/bin/env python3
"""Convert an Illumio traffic CSV export to JSON.

Usage:
    python traffic_csv_to_json.py traffic.csv            # writes traffic.json
    python traffic_csv_to_json.py traffic.csv out.json   # custom output name

Skips any report/metadata lines above the real header row, strips blank
columns, and turns empty cells into null.
"""
import csv
import json
import sys
from pathlib import Path

HEADER_HINTS = ("source", "destination", "port", "protocol", "service")


def find_header(rows):
    """Return the index of the first row that looks like the column header."""
    for i, row in enumerate(rows):
        cells = [c.strip().lower() for c in row]
        hits = sum(any(h in c for h in HEADER_HINTS) for c in cells)
        if hits >= 2:
            return i
    return 0  # fall back to the first row


def convert(src, dst):
    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    if not rows:
        sys.exit(f"{src} is empty")

    h = find_header(rows)
    header = [c.strip() for c in rows[h]]
    keep = [i for i, name in enumerate(header) if name]  # drop unnamed columns

    records = []
    for row in rows[h + 1:]:
        if not any(c.strip() for c in row):
            continue  # skip blank lines
        rec = {}
        for i in keep:
            val = row[i].strip() if i < len(row) else ""
            rec[header[i]] = val if val != "" else None
        records.append(rec)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    print(f"{len(records)} rows -> {dst}")
    if h:
        print(f"(skipped {h} metadata line(s) above the header)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".json")
    convert(src, dst)
