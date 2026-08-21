#!/usr/bin/env python3
"""
FireMon Device Health Report -> Excel

Parses the text export of FireMon's Device Health Report and produces a workbook
with a summary, a full device table, an action list, and a licensing view.

Usage:
    python firemon_health_to_excel.py DeviceHealthReport.txt [output.xlsx]

Export the source file from Security Manager:
    Reports -> Reports Library -> Health Check -> Device Health Report
    Run against All Devices, then export/copy as text.

Requires openpyxl (pip install openpyxl).
"""

import re
import sys
from collections import Counter
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

FONT = "Arial"

# ---------------------------------------------------------------- classification

# Ordered: first pattern that matches wins, so put specific before general.
CATEGORIES = [
    ("AZURE-SECRET",    r"AADSTS7000215"),
    ("BAD-CREDS",       r"INVALID_CREDENTIALS|Invalid credentials"),
    ("SSH-KEY",         r"SSH Key changed"),
    ("ZSCALER-API",     r"HTTPSConnectionPool|ConnectTimeoutError"),
    ("SSH-TIMEOUT",     r"Timeout exceeded"),
    ("NEVER-RETRIEVED", r"never received a retrieval status"),
    ("OK-STALE",        r"^Success"),
    ("LOGSERVER",       r"^Not applicable$"),
]

# Category -> (plain-English meaning, who has to act)
TRIAGE = {
    "AZURE-SECRET": (
        "Expired client secret on the Azure app registration",
        "Cloud Eng - rotate secret, then update it on the Azure management station",
    ),
    "BAD-CREDS": (
        "SSH connects but the service account is rejected",
        "Network Eng - supply current credentials for the FireMon service account",
    ),
    "SSH-KEY": (
        "Device SSH host key changed; FireMon will not accept it",
        "Enable 'Automatically Update SSH Keys' on the device, then force a retrieval",
    ),
    "SSH-TIMEOUT": (
        "SSH never answered - no banner, no auth prompt",
        "Network Eng - confirm mgmt IP is current and collector IP is permitted on vty",
    ),
    "ZSCALER-API": (
        "TCP connection to the Zscaler API timed out before authentication",
        "Collector owner - allow egress from the data collector to the API host on 443",
    ),
    "NEVER-RETRIEVED": (
        "Collector has never had a retrieval status for this device",
        "Onboarding was never completed - re-add the device",
    ),
    "OK-STALE": (
        "Last retrieval succeeded; nothing since",
        "No action on credentials - check schedule and change detection",
    ),
    "LOGSERVER": (
        "Log server - retrieval not applicable",
        "None",
    ),
    "NO-ERROR-TEXT": (
        "Failing but no retrieval error was recorded",
        "Force a manual retrieval to capture a current error",
    ),
    "NOT-LICENSED": (
        "Inactive or unlicensed - no health data collected",
        "Removal candidate if the device is decommissioned",
    ),
    "OTHER": ("Unrecognised retrieval error", "Review manually"),
}

# ---------------------------------------------------------------- parsing

DEVICE_RE = re.compile(r"^(?P<name>.+?)\s*\(ID:\s*(?P<id>\d+)\)\t(?P<rest>.*)$")
HEALTH_VALUES = {"Critical", "Healthy", "Inactive", "Unlicensed", "Warning"}

SECTION_HEADERS = {
    "Health Check Results", "GENERAL", "RETRIEVAL", "CHANGE DETECTION",
    "USAGE", "LAST RETRIEVAL", "LAST REVISION", "CHANGE MONITORING",
    "CHANGE DATA", "LOG MONITORING", "USAGE DATA", "DEVICE LICENSED",
    "DC GROUP ASSIGNED", "DEVICE UNLICENSED",
}


def _collect(lines, start_label, stop_labels):
    """Return the lines under start_label up to the next section header."""
    out = []
    grabbing = False
    for ln in lines:
        s = ln.strip()
        if s == start_label:
            grabbing = True
            continue
        if grabbing:
            if s in stop_labels or s in SECTION_HEADERS:
                break
            out.append(s)
    return " ".join(x for x in out if x).strip()


def parse_report(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        raw = fh.read().splitlines()

    devices = []
    i = 0
    while i < len(raw):
        m = DEVICE_RE.match(raw[i])
        if not m:
            i += 1
            continue

        cols = m.group("rest").split("\t")
        dev = {
            "id": int(m.group("id")),
            "name": m.group("name").strip(),
            "description": cols[0].strip() if len(cols) > 0 else "",
            "cluster": cols[1].strip() if len(cols) > 1 else "",
            "mgmt_ip": cols[2].strip() if len(cols) > 2 else "",
            "vendor": cols[3].strip() if len(cols) > 3 else "",
            "health": cols[4].strip() if len(cols) > 4 else "",
        }

        # Health usually lands on the following line; the trailing tab leaves it blank above.
        j = i + 1
        if not dev["health"] and j < len(raw) and raw[j].strip() in HEALTH_VALUES:
            dev["health"] = raw[j].strip()
            j += 1

        # Everything up to the next device row is this device's health block.
        block = []
        while j < len(raw) and not DEVICE_RE.match(raw[j]):
            block.append(raw[j])
            j += 1

        dev.update(parse_block(block))
        devices.append(dev)
        i = j

    return devices


def parse_block(lines):
    text = "\n".join(lines)
    out = {
        "licensed": "DEVICE LICENSED" in text,
        "collector": "",
        "last_retrieval": "",
        "retrieval_date": "",
        "rev_id": "", "rev_type": "", "rev_date": "",
        "rev_user": "", "rev_changes": "", "rev_result": "",
        "change_monitoring": "", "log_monitoring": "",
        "usage_data": "", "logged_conns": "",
        "ssh_target": "",
    }

    m = re.search(r"assigned to this device \(([^)]+)\)", text)
    if m:
        out["collector"] = m.group(1)

    out["last_retrieval"] = _collect(lines, "LAST RETRIEVAL", {"LAST REVISION"})

    m = re.search(r"[Ll]ast updated on (\d+/\d+/\d+) at ([\d:]+\s*[AP]M)",
                  out["last_retrieval"])
    if m:
        out["retrieval_date"] = f"{m.group(1)} {m.group(2)}"

    # pexpect dumps the exact ssh invocation - pull user@host out of it.
    m = re.search(r"'(-p)',\s*'(\d+)',\s*'([^']+@[\d.]+)'", out["last_retrieval"])
    if m:
        out["ssh_target"] = f"{m.group(3)}:{m.group(2)}"

    for key, label in [("rev_id", "Revision ID"), ("rev_type", "Type"),
                       ("rev_user", "User"), ("rev_changes", "Change Count"),
                       ("rev_result", "Result")]:
        m = re.search(rf"^{label}:\s*(.+)$", text, re.M)
        if m:
            out[key] = m.group(1).strip()

    m = re.search(r"^Date/Time:\s*(.+)$", text, re.M)
    if m:
        out["rev_date"] = m.group(1).strip()

    out["change_monitoring"] = _collect(lines, "CHANGE MONITORING", {"CHANGE DATA"})
    out["log_monitoring"] = _collect(lines, "LOG MONITORING", {"USAGE DATA"})
    out["usage_data"] = _collect(lines, "USAGE DATA", {"Logged Connections"})
    out["usage_data"] = re.sub(r"Logged Connections.*$", "", out["usage_data"]).strip()

    m = re.search(r"Logged Connections \(Last 24 hours\):\s*(\d+)", text)
    if m:
        out["logged_conns"] = int(m.group(1))

    return out


def classify(dev):
    if dev["health"] in ("Inactive", "Unlicensed"):
        return "NOT-LICENSED"
    lr = dev["last_retrieval"]
    if not lr:
        return "NO-ERROR-TEXT"
    for name, pattern in CATEGORIES:
        if re.search(pattern, lr):
            return name
    return "OTHER"


def days_since(datestr):
    """'6/29/26 8:44:34 PM' -> integer days, or '' when unparseable."""
    if not datestr:
        return ""
    m = re.match(r"(\d+)/(\d+)/(\d+)", datestr)
    if not m:
        return ""
    mo, day, yr = (int(x) for x in m.groups())
    yr += 2000 if yr < 100 else 0
    try:
        return (datetime.now() - datetime(yr, mo, day)).days
    except ValueError:
        return ""


# ---------------------------------------------------------------- workbook

HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(name=FONT, bold=True, size=14)
BODY = Font(name=FONT, size=10)
BOLD = Font(name=FONT, size=10, bold=True)
NOTE = Font(name=FONT, size=9, italic=True, color="595959")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

SEVERITY_FILL = {
    "AZURE-SECRET": "FFC7CE",
    "BAD-CREDS": "FFC7CE",
    "SSH-KEY": "FFEB9C",
    "SSH-TIMEOUT": "FFC7CE",
    "ZSCALER-API": "FFC7CE",
    "NEVER-RETRIEVED": "FFEB9C",
    "NO-ERROR-TEXT": "FFEB9C",
    "OK-STALE": "C6EFCE",
    "LOGSERVER": "EDEDED",
    "NOT-LICENSED": "EDEDED",
}


def write_header(ws, headers, row=1):
    for c, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def autosize(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def add_table(ws, name, ncols, nrows, header_row=1):
    if nrows == 0:
        return
    ref = f"A{header_row}:{get_column_letter(ncols)}{header_row + nrows}"
    t = Table(displayName=name, ref=ref)
    t.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showRowStripes=True, showColumnStripes=False
    )
    ws.add_table(t)


def sheet_devices(wb, devices):
    ws = wb.create_sheet("All Devices")
    headers = [
        "Device ID", "Device Name", "Vendor", "Health", "Category",
        "Mgmt IP", "Cluster", "Data Collector", "Last Retrieval",
        "Days Stale", "Retrieval Detail", "SSH Target",
        "Revision Date", "Revision Result", "Revision User",
        "Change Monitoring", "Log Monitoring", "Usage Data", "Description",
    ]
    write_header(ws, headers)

    for r, d in enumerate(sorted(devices, key=lambda x: (x["vendor"], x["name"].lower())), 2):
        vals = [
            d["id"], d["name"], d["vendor"], d["health"], d["category"],
            d["mgmt_ip"], d["cluster"], d["collector"], d["retrieval_date"],
            days_since(d["retrieval_date"]), d["last_retrieval"][:500], d["ssh_target"],
            d["rev_date"], d["rev_result"], d["rev_user"],
            d["change_monitoring"], d["log_monitoring"][:300], d["usage_data"][:200],
            d["description"],
        ]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.font = BODY
            cell.alignment = Alignment(vertical="top")
        fill = SEVERITY_FILL.get(d["category"])
        if fill:
            ws.cell(row=r, column=5).fill = PatternFill("solid", fgColor=fill)

    add_table(ws, "AllDevices", len(headers), len(devices))
    autosize(ws, [9, 42, 12, 10, 16, 15, 18, 30, 18, 10, 60, 24,
                  26, 20, 18, 18, 34, 30, 40])
    ws.auto_filter.ref = ws.dimensions
    return ws


def sheet_summary(wb, devices, src, report_date):
    ws = wb.create_sheet("Summary", 0)
    ws["A1"] = "FireMon Device Health - Summary"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = f"Source: {src}"
    ws["A2"].font = NOTE
    ws["A3"] = f"Report generated by FireMon: {report_date or 'unknown'}"
    ws["A3"].font = NOTE
    ws["A4"] = f"Workbook built: {datetime.now():%Y-%m-%d %H:%M}"
    ws["A4"].font = NOTE
    ws["A5"] = ("Counts are COUNTIF formulas over 'All Devices' - edit the category "
                "there and every total below follows.")
    ws["A5"].font = NOTE

    n = len(devices)
    last = n + 1  # header occupies row 1 on All Devices

    row = 7
    ws.cell(row=row, column=1, value="BY HEALTH").font = BOLD
    row += 1
    write_header(ws, ["Health", "Devices"], row)
    ws.freeze_panes = None
    for h in ["Critical", "Healthy", "Inactive", "Unlicensed"]:
        row += 1
        ws.cell(row=row, column=1, value=h).font = BODY
        c = ws.cell(row=row, column=2,
                    value=f"=COUNTIF('All Devices'!$D$2:$D${last},A{row})")
        c.font = BODY
    row += 1
    ws.cell(row=row, column=1, value="Total").font = BOLD
    ws.cell(row=row, column=2, value=f"=COUNTA('All Devices'!$A$2:$A${last})").font = BOLD

    row += 2
    ws.cell(row=row, column=1, value="BY FAILURE CATEGORY").font = BOLD
    row += 1
    write_header(ws, ["Category", "Devices", "What it means", "Who acts"], row)
    cat_start = row + 1
    for cat in [c for c, _ in CATEGORIES] + ["NO-ERROR-TEXT", "NOT-LICENSED", "OTHER"]:
        row += 1
        ws.cell(row=row, column=1, value=cat).font = BODY
        ws.cell(row=row, column=2,
                value=f"=COUNTIF('All Devices'!$E$2:$E${last},A{row})").font = BODY
        meaning, owner = TRIAGE.get(cat, ("", ""))
        ws.cell(row=row, column=3, value=meaning).font = BODY
        ws.cell(row=row, column=4, value=owner).font = BODY
        fill = SEVERITY_FILL.get(cat)
        if fill:
            ws.cell(row=row, column=1).fill = PatternFill("solid", fgColor=fill)
    row += 1
    ws.cell(row=row, column=1, value="Total").font = BOLD
    ws.cell(row=row, column=2,
            value=f"=SUM(B{cat_start}:B{row - 1})").font = BOLD

    row += 2
    ws.cell(row=row, column=1, value="BY VENDOR").font = BOLD
    row += 1
    write_header(ws, ["Vendor", "Devices", "Licensed", "Critical"], row)
    for v in sorted({d["vendor"] for d in devices if d["vendor"]}):
        row += 1
        ws.cell(row=row, column=1, value=v).font = BODY
        ws.cell(row=row, column=2,
                value=f"=COUNTIF('All Devices'!$C$2:$C${last},A{row})").font = BODY
        ws.cell(row=row, column=3,
                value=(f"=COUNTIFS('All Devices'!$C$2:$C${last},A{row},"
                       f"'All Devices'!$D$2:$D${last},\"Critical\")"
                       f"+COUNTIFS('All Devices'!$C$2:$C${last},A{row},"
                       f"'All Devices'!$D$2:$D${last},\"Healthy\")")).font = BODY
        ws.cell(row=row, column=4,
                value=(f"=COUNTIFS('All Devices'!$C$2:$C${last},A{row},"
                       f"'All Devices'!$D$2:$D${last},\"Critical\")")).font = BODY

    autosize(ws, [30, 12, 58, 62])
    return ws


def sheet_actions(wb, devices):
    ws = wb.create_sheet("Action List")
    ws["A1"] = "Devices needing action, grouped by root cause"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = ("Excludes log servers, inactive/unlicensed devices, and devices whose "
                "last retrieval succeeded.")
    ws["A2"].font = NOTE

    actionable = [c for c, _ in CATEGORIES if c not in ("OK-STALE", "LOGSERVER")]
    actionable += ["NO-ERROR-TEXT", "OTHER"]

    row = 4
    for cat in actionable:
        rows = [d for d in devices if d["category"] == cat]
        if not rows:
            continue
        meaning, owner = TRIAGE.get(cat, ("", ""))
        ws.cell(row=row, column=1, value=f"{cat}  ({len(rows)})").font = Font(
            name=FONT, bold=True, size=11)
        fill = SEVERITY_FILL.get(cat)
        if fill:
            ws.cell(row=row, column=1).fill = PatternFill("solid", fgColor=fill)
        row += 1
        ws.cell(row=row, column=1, value=meaning).font = NOTE
        row += 1
        ws.cell(row=row, column=1, value=f"Owner: {owner}").font = NOTE
        row += 1

        write_header(ws, ["Device ID", "Device Name", "Vendor", "Mgmt IP",
                          "SSH Target", "Last Retrieval", "Days Stale",
                          "Data Collector"], row)
        ws.freeze_panes = None
        row += 1
        for d in sorted(rows, key=lambda x: x["name"].lower()):
            vals = [d["id"], d["name"], d["vendor"], d["mgmt_ip"], d["ssh_target"],
                    d["retrieval_date"], days_since(d["retrieval_date"]), d["collector"]]
            for c, v in enumerate(vals, 1):
                cell = ws.cell(row=row, column=c, value=v)
                cell.font = BODY
                cell.border = BOX
            row += 1
        row += 2

    autosize(ws, [10, 46, 12, 17, 26, 20, 11, 34])
    return ws


def sheet_licensing(wb, devices):
    ws = wb.create_sheet("Licensing")
    ws["A1"] = "Licensing position"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = ("Derived from the Device Health Report. Confirm against a clean run of the "
                "Device Inventory Report before quoting externally.")
    ws["A2"].font = NOTE

    lic = [d for d in devices if d["health"] in ("Critical", "Healthy")]
    unl = [d for d in devices if d["health"] == "Unlicensed"]
    ina = [d for d in devices if d["health"] == "Inactive"]

    row = 4
    write_header(ws, ["Vendor", "Licensed", "Unlicensed", "Inactive", "Total"], row)
    ws.freeze_panes = None
    start = row + 1
    for v in sorted({d["vendor"] for d in devices if d["vendor"]}):
        row += 1
        ws.cell(row=row, column=1, value=v).font = BODY
        for col, subset in ((2, lic), (3, unl), (4, ina)):
            ws.cell(row=row, column=col,
                    value=sum(1 for d in subset if d["vendor"] == v)).font = BODY
        ws.cell(row=row, column=5, value=f"=SUM(B{row}:D{row})").font = BODY
    row += 1
    ws.cell(row=row, column=1, value="Total").font = BOLD
    for col in range(2, 6):
        L = get_column_letter(col)
        ws.cell(row=row, column=col, value=f"=SUM({L}{start}:{L}{row - 1})").font = BOLD

    row += 2
    ws.cell(row=row, column=1,
            value="Devices not consuming a license (removal candidates)").font = BOLD
    row += 1
    write_header(ws, ["Device ID", "Device Name", "Vendor", "Health",
                      "Mgmt IP", "Cluster", "Description"], row)
    ws.freeze_panes = None
    row += 1
    for d in sorted(unl + ina, key=lambda x: (x["vendor"], x["name"].lower())):
        vals = [d["id"], d["name"], d["vendor"], d["health"],
                d["mgmt_ip"], d["cluster"], d["description"]]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=row, column=c, value=v)
            cell.font = BODY
            cell.border = BOX
        row += 1

    autosize(ws, [10, 46, 12, 12, 17, 22, 48])
    return ws


def build(devices, src, report_date, out_path):
    wb = Workbook()
    wb.remove(wb.active)
    sheet_devices(wb, devices)
    sheet_actions(wb, devices)
    sheet_licensing(wb, devices)
    sheet_summary(wb, devices, src, report_date)
    wb.move_sheet("Summary", offset=-3)
    wb.save(out_path)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "firemon_device_health.xlsx"

    devices = parse_report(src)
    if not devices:
        print("No devices parsed. Is this the Device Health Report text export?")
        sys.exit(1)

    for d in devices:
        d["category"] = classify(d)

    report_date = ""
    with open(src, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh.read().splitlines()[:5]:
            if re.match(r"^[A-Z][a-z]+ \d+, \d{4}", ln.strip()):
                report_date = ln.strip()
                break

    build(devices, src, report_date, out)

    print(f"Parsed {len(devices)} devices -> {out}\n")
    for cat, n in Counter(d["category"] for d in devices).most_common():
        print(f"  {n:4d}  {cat:16s} {TRIAGE.get(cat, ('', ''))[0]}")
    print()
    for h, n in Counter(d["health"] for d in devices).most_common():
        print(f"  {n:4d}  {h}")


if __name__ == "__main__":
    main()
