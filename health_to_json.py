#!/usr/bin/env python3
"""
Convert a FireMon Device Health Report PDF (health.pdf) into health.json.

Usage (run in the folder that contains health.pdf):
    pip install pdfplumber
    python health_to_json.py

Output: health.json - one entry per device / management station with its
header fields (name, ID, IP, vendor, health) and each health check section
(general, retrieval, change detection, usage), plus the parsed last revision.
"""
import json
import re
from pathlib import Path

import pdfplumber

PDF_FILE = "health.pdf"
JSON_FILE = "health.json"

ID_RE = re.compile(r"\(ID:\s*(\d+)\)")
IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
HEALTH = ("Healthy", "Warning", "Critical", "Inactive", "Unlicensed", "Unknown")
VENDORS = ("Check Point", "Cisco", "Microsoft", "Zscaler", "Illumio", "F5",
           "Palo Alto Networks", "Fortinet", "Juniper", "Aruba")
SECTIONS = ("general", "retrieval", "change_detection", "usage")
LABELS = {
    "DEVICE LICENSED", "DC GROUP ASSIGNED", "LAST RETRIEVAL", "LAST REVISION",
    "CHANGE MONITORING", "CHANGE DATA", "LOG MONITORING", "USAGE DATA",
}
SKIP = {"HEALTH CHECK RESULTS", "GENERAL", "RETRIEVAL", "CHANGE DETECTION", "USAGE"}
NOISE = re.compile(r"^(Page \d+( of \d+)?|Device Health Report|Devices:\s*\d+|"
                   r"Management Stations:\s*\d+|FIREMON.*)$", re.I)
REV_FIELDS = {
    "Revision ID": "revision_id", "Type": "type", "Date/Time": "datetime",
    "User": "user", "Change Count": "change_count", "Result": "result",
}


def lines_of(page, tol=3):
    """Group the page's words into visual lines."""
    words = sorted(page.extract_words(x_tolerance=2, y_tolerance=2),
                   key=lambda w: (round(w["top"]), w["x0"]))
    lines, cur, top = [], [], None
    for w in words:
        if top is not None and abs(w["top"] - top) > tol:
            lines.append(cur)
            cur, top = [], None
        cur.append(w)
        top = w["top"] if top is None else top
    if cur:
        lines.append(cur)
    return [sorted(l, key=lambda w: w["x0"]) for l in lines]


def join(words):
    return " ".join(w["text"] for w in words).strip()


def column_starts(line):
    """X positions of the RETRIEVAL / CHANGE DETECTION / USAGE section headings."""
    xs = {}
    for w in line:
        t = w["text"].upper()
        if t in ("RETRIEVAL", "CHANGE", "USAGE") and t not in xs:
            xs[t] = w["x0"] - 3
    return [xs["RETRIEVAL"], xs["CHANGE"], xs["USAGE"]] if len(xs) == 3 else None


def which_col(x, starts):
    return sum(x >= s for s in starts)


def parse_header(text):
    """'Name (ID: 12) description 10.1.1.1 Vendor Health' -> dict."""
    m = ID_RE.search(text)
    rest = text[m.end():].strip()
    health = next((h for h in HEALTH if re.search(rf"\b{h}\b", rest)), "")
    rest = re.sub(rf"\b{health}\b", "", rest).strip() if health else rest
    vendor = next((v for v in VENDORS if v in rest), "")
    if vendor:  # vendor column sits at the right, so drop its last occurrence only
        head, _, tail = rest.rpartition(vendor)
        rest = (head + tail).strip()
    ip = IP_RE.search(rest)
    mgmt_ip = ip.group(0) if ip else ""
    if ip:
        rest = rest.replace(mgmt_ip, "").strip()
    rest = rest.replace("No Management IP", "").strip()
    return {
        "id": int(m.group(1)), "name": text[:m.start()].strip(),
        "description": re.sub(r"\s{2,}", " ", rest), "management_ip": mgmt_ip,
        "vendor": vendor, "health": health,
    }


def parse_section(lines):
    """Turn a section's text lines into {LABEL: text}."""
    out, label = {}, None
    for raw in lines:
        line = re.sub(r"^[^\w(]+", "", raw).strip()   # drop status icons
        if not line or line.upper() in SKIP:
            continue
        up = line.upper()
        if up in LABELS:
            label = up.lower().replace(" ", "_")
            out[label] = ""
        elif label:
            out[label] = (out[label] + " " + line).strip()
    return out


def parse_revision(text):
    rev = {}
    keys = "|".join(map(re.escape, REV_FIELDS))
    for k, v in re.findall(rf"({keys}):\s*(.*?)(?=\s+(?:{keys}):|$)", text):
        rev[REV_FIELDS[k]] = int(v) if REV_FIELDS[k] in ("revision_id", "change_count") and v.isdigit() else v.strip()
    return rev


def main():
    pdf_path = Path(PDF_FILE)
    if not pdf_path.exists():
        raise SystemExit(f"{PDF_FILE} not found in {Path.cwd()}")

    devices, dev, starts = [], None, None
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for line in lines_of(page):
                text = join(line)
                if not text or NOISE.match(text):
                    continue
                if ID_RE.search(text):                       # new device row
                    dev = parse_header(text)
                    dev["_cols"] = [[] for _ in SECTIONS]
                    devices.append(dev)
                    continue
                if dev is None:
                    continue
                s = column_starts(line)
                if s and "DETECTION" in text.upper():         # section heading row
                    starts = s
                    continue
                if starts is None:
                    continue
                cols = [[] for _ in SECTIONS]
                for w in line:
                    cols[which_col(w["x0"], starts)].append(w)
                for i, words in enumerate(cols):
                    if words:
                        dev["_cols"][i].append(join(words))

    for d in devices:
        cols = d.pop("_cols")
        d["health_checks"] = {name: parse_section(c) for name, c in zip(SECTIONS, cols)}
        last_rev = d["health_checks"]["retrieval"].get("last_revision", "")
        if last_rev:
            d["last_revision"] = parse_revision(last_rev)

    Path(JSON_FILE).write_text(json.dumps({"device_count": len(devices),
                                           "devices": devices}, indent=2), encoding="utf-8")
    print(f"Parsed {len(devices)} devices -> {JSON_FILE}")


if __name__ == "__main__":
    main()
