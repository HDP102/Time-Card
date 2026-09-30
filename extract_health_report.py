#!/usr/bin/env python3
"""
Extract a FireMon "Device Health Report" PDF into CSV + JSON.

Usage:
    pip install pdfplumber
    python extract_health_report.py "Device Health Report.pdf"

Outputs (next to the PDF):
    <name>_devices.csv   one row per device, one column per health check
    <name>_devices.json  same data, nested
    <name>_raw.txt       layout-preserved text dump (fallback if parsing is off)
"""
import csv
import json
import re
import sys
from pathlib import Path

import pdfplumber

ID_RE = re.compile(r"\(ID:\s*(\d+)\)")
HEALTH_WORDS = {"Healthy", "Warning", "Critical", "Inactive", "Unlicensed", "Unknown"}
SECTION_TITLES = {"HEALTH CHECK RESULTS", "GENERAL", "RETRIEVAL", "CHANGE DETECTION", "USAGE"}
HEADER_FIELDS = ["device", "description", "cluster", "mgmt_ip", "vendor", "health"]
HEADER_LABELS = ["Device", "Description", "Cluster", "Management", "Vendor", "Health"]
NOISE_RE = re.compile(r"^(Page \d+( of \d+)?|Device Health Report|Devices:\s*\d+)$", re.I)


def page_lines(page, y_tol=3):
    """Group words into lines by vertical position."""
    words = page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=False)
    words.sort(key=lambda w: (round(w["top"]), w["x0"]))
    lines, cur, cur_top = [], [], None
    for w in words:
        if cur_top is None or abs(w["top"] - cur_top) <= y_tol:
            cur.append(w)
            cur_top = w["top"] if cur_top is None else cur_top
        else:
            lines.append(sorted(cur, key=lambda x: x["x0"]))
            cur, cur_top = [w], w["top"]
    if cur:
        lines.append(sorted(cur, key=lambda x: x["x0"]))
    return lines


def text_of(words):
    return " ".join(w["text"] for w in words)


def header_bounds(line):
    """Column boundaries from the table header row (labels are centred, so use midpoints)."""
    centers = {}
    for w in line:
        if w["text"] in HEADER_LABELS and w["text"] not in centers:
            centers[w["text"]] = (w["x0"] + w["x1"]) / 2
    if len(centers) < 6:
        return None
    c = [centers[l] for l in HEADER_LABELS]
    return [(c[i] + c[i + 1]) / 2 for i in range(5)]


def section_bounds(line):
    """Column boundaries for GENERAL / RETRIEVAL / CHANGE DETECTION / USAGE."""
    xs = {}
    for w in line:
        if w["text"] in ("RETRIEVAL", "CHANGE", "USAGE") and w["text"] not in xs:
            xs[w["text"]] = w["x0"] - 3
    if len(xs) < 3:
        return None
    return [xs["RETRIEVAL"], xs["CHANGE"], xs["USAGE"]]


def col_index(x, bounds):
    for i, b in enumerate(bounds):
        if x < b:
            return i
    return len(bounds)


def parse_section(lines):
    """Split one section column into {LABEL: value} using all-caps label lines."""
    out, label = {}, None
    for raw in lines:
        line = re.sub(r"^[^\w(]+", "", raw).strip()  # strip icon glyphs
        if not line or line.upper() in SECTION_TITLES:
            continue
        if re.fullmatch(r"[A-Z][A-Z /&-]+", line):
            label = line.replace(" ", "_")
            out[label] = ""
        elif label:
            out[label] = (out[label] + " " + line).strip()
        else:
            out["_unlabelled"] = (out.get("_unlabelled", "") + " " + line).strip()
    return out


def extract(pdf_path):
    devices, dev, state = [], None, "start"
    hbounds = sbounds = None
    raw_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            raw_pages.append(f"===== PAGE {pno} =====\n" + (page.extract_text(layout=True) or ""))
            for line in page_lines(page):
                t = text_of(line)
                if NOISE_RE.match(t.strip()):
                    continue

                hb = header_bounds(line)
                if hb:
                    hbounds = hb
                    continue

                if ID_RE.search(t) and hbounds:
                    dev = {f: "" for f in HEADER_FIELDS}
                    dev.update(page=pno, _sections=[[], [], [], []])
                    devices.append(dev)
                    state = "header"

                if dev is None:
                    continue

                if "Health Check Results" in t or "Health Check Results".replace(" ", "") in t:
                    state = "health"
                sb = section_bounds(line)
                if sb and "DETECTION" in t:
                    sbounds, state = sb, "health"
                    continue

                if state == "header":
                    cols = [[] for _ in HEADER_FIELDS]
                    for w in line:
                        cols[col_index(w["x0"], hbounds)].append(w["text"])
                    for f, words in zip(HEADER_FIELDS, cols):
                        if words:
                            dev[f] = (dev[f] + " " + " ".join(words)).strip()
                elif state == "health" and sbounds:
                    cols = [[] for _ in range(4)]
                    for w in line:
                        cols[col_index(w["x0"], sbounds)].append(w["text"])
                    for i, words in enumerate(cols):
                        if words:
                            dev["_sections"][i].append(" ".join(words))

    rows = []
    for d in devices:
        m = ID_RE.search(d["device"])
        name, spill = (d["device"][:m.start()], d["device"][m.end():]) if m else (d["device"], "")
        row = {
            "id": m.group(1) if m else "",
            "name": name.strip(),
            "description": f"{spill.strip()} {d['description']}".strip(),
            "cluster": d["cluster"],
            "mgmt_ip": d["mgmt_ip"],
            "vendor": d["vendor"],
            "health": next((w for w in d["health"].split() if w in HEALTH_WORDS), d["health"]),
            "page": d["page"],
        }
        for sec, name in zip(d["_sections"], ["general", "retrieval", "change", "usage"]):
            for label, val in parse_section(sec).items():
                row[f"{name}.{label}"] = val
        rows.append(row)
    return rows, "\n\n".join(raw_pages)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pdf_path = Path(sys.argv[1])
    rows, raw = extract(pdf_path)
    stem = pdf_path.with_suffix("")

    Path(f"{stem}_raw.txt").write_text(raw, encoding="utf-8")
    Path(f"{stem}_devices.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")

    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(f"{stem}_devices.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Parsed {len(rows)} devices")
    print(f"  {stem}_devices.csv\n  {stem}_devices.json\n  {stem}_raw.txt")


if __name__ == "__main__":
    main()
