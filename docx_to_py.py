#!/usr/bin/env python3
"""
docx_to_py.py — flatten a .docx into a single self-contained Python file.

Usage:
    python docx_to_py.py "Illumio_App_Enforcement_procedure - UPDATED (1).docx"
    python docx_to_py.py input.docx -o doc_data.py
    python docx_to_py.py input.docx --images          # also dump images to ./<stem>_images/
    python docx_to_py.py input.docx --no-runs         # smaller output, text only

Produces a .py file containing META, BLOCKS, IMAGES, and a main() that prints
an outline. Everything stays in document order, including tables and images.
"""

import argparse
import os
import pprint
import re
import sys
import zipfile
from datetime import datetime

try:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    sys.exit("python-docx missing. Install with:  pip install python-docx")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
EMU_PER_IN = 914400


# ---------------------------------------------------------------- helpers

def heading_level(style_name):
    """Return 1..9 for Heading N / Title, else None."""
    if not style_name:
        return None
    s = style_name.strip().lower()
    if s == "title":
        return 0
    m = re.match(r"^heading\s*(\d)$", s)
    return int(m.group(1)) if m else None


def list_info(par, style_name=None):
    """(is_list, numId, ilvl). Checks numbering XML first, then list styles."""
    pPr = par._p.find(f"{W}pPr")
    numPr = pPr.find(f"{W}numPr") if pPr is not None else None
    if numPr is not None:
        numId = numPr.find(f"{W}numId")
        ilvl = numPr.find(f"{W}ilvl")
        return (
            True,
            numId.get(f"{W}val") if numId is not None else None,
            int(ilvl.get(f"{W}val")) if ilvl is not None else 0,
        )
    # Fallback: Word also marks bullets/numbers purely by style.
    if style_name and re.match(r"^List (Bullet|Number|Paragraph|Continue)", style_name.strip()):
        m = re.search(r"(\d)$", style_name.strip())
        return True, None, int(m.group(1)) - 1 if m else 0
    return False, None, None


def run_data(run):
    """Formatting-aware run dict. Only emits keys that are actually set."""
    d = {"text": run.text}
    f = run.font
    for key, val in (
        ("b", run.bold),
        ("i", run.italic),
        ("u", run.underline),
        ("strike", f.strike),
        ("sub", f.subscript),
        ("sup", f.superscript),
    ):
        if val:
            d[key] = True
    if f.size is not None:
        d["pt"] = round(f.size.pt, 1)
    if f.name:
        d["font"] = f.name
    try:
        if f.color is not None and f.color.rgb is not None:
            d["color"] = str(f.color.rgb)
    except (AttributeError, ValueError):
        pass
    if run.style and run.style.name not in ("Default Paragraph Font", None):
        d["style"] = run.style.name
    return d


def hyperlinks(par):
    """[(text, url)] for external links in this paragraph."""
    out = []
    rels = par.part.rels
    for link in par._p.findall(f".//{W}hyperlink"):
        rid = link.get(f"{R}id")
        text = "".join(t.text or "" for t in link.findall(f".//{W}t"))
        if rid and rid in rels:
            out.append({"text": text, "url": rels[rid].target_ref})
    return out


def images_in(par):
    """Image refs inside a paragraph, with display size in inches."""
    found = []
    rels = par.part.rels
    for blip in par._p.findall(f".//{A}blip"):
        rid = blip.get(f"{R}embed")
        if not rid or rid not in rels:
            continue
        target = rels[rid].target_ref
        name = os.path.basename(target)
        rec = {"rid": rid, "file": name}
        ext = blip.getparent()
        while ext is not None and not ext.tag.endswith("}inline") and not ext.tag.endswith("}anchor"):
            ext = ext.getparent()
        if ext is not None:
            extent = ext.find(f".//{A}ext")
            if extent is not None:
                try:
                    rec["w_in"] = round(int(extent.get("cx")) / EMU_PER_IN, 2)
                    rec["h_in"] = round(int(extent.get("cy")) / EMU_PER_IN, 2)
                except (TypeError, ValueError):
                    pass
            docPr = ext.find(f".//{W}docPr") or ext.find(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"
            )
            if docPr is None:
                for child in ext.iter():
                    if child.tag.endswith("}docPr"):
                        docPr = child
                        break
            if docPr is not None:
                if docPr.get("name"):
                    rec["name"] = docPr.get("name")
                if docPr.get("descr"):
                    rec["alt"] = docPr.get("descr")
        found.append(rec)
    return found


def textbox_text(par):
    """Text living inside shapes/text boxes anchored to this paragraph."""
    chunks = []
    for txbx in par._p.findall(f".//{W}txbxContent"):
        for p in txbx.findall(f"{W}p"):
            t = "".join(n.text or "" for n in p.findall(f".//{W}t"))
            if t.strip():
                chunks.append(t)
    return chunks


def par_block(par, keep_runs=True):
    text = par.text
    style = par.style.name if par.style else None
    lvl = heading_level(style)
    is_list, num_id, ilvl = list_info(par, style)
    imgs = images_in(par)
    boxes = textbox_text(par)
    links = hyperlinks(par)

    if not text.strip() and not imgs and not boxes:
        return None

    b = {"type": "heading" if lvl is not None else "p", "text": text}
    if style and style != "Normal":
        b["style"] = style
    if lvl is not None:
        b["level"] = lvl
    if is_list:
        b["list"] = True
        b["ilvl"] = ilvl
        if num_id:
            b["num_id"] = num_id
    if par.alignment is not None:
        b["align"] = str(par.alignment).split()[0]
    if keep_runs:
        runs = [run_data(r) for r in par.runs if r.text]
        if any(len(r) > 1 for r in runs):
            b["runs"] = runs
    if links:
        b["links"] = links
    if imgs:
        b["images"] = imgs
    if boxes:
        b["textbox"] = boxes
    return b


def table_block(tbl, keep_runs=True):
    rows = []
    for row in tbl.rows:
        cells = []
        seen = set()
        for cell in row.cells:
            if id(cell._tc) in seen:
                continue
            seen.add(id(cell._tc))
            inner = []
            for child in cell._tc:
                if child.tag == f"{W}p":
                    blk = par_block(Paragraph(child, cell), keep_runs)
                    if blk:
                        inner.append(blk)
                elif child.tag == f"{W}tbl":
                    inner.append(table_block(Table(child, cell), keep_runs))
            cells.append({"text": cell.text, "blocks": inner} if inner else {"text": cell.text})
        rows.append(cells)
    b = {"type": "table", "rows": rows}
    if tbl.style and tbl.style.name:
        b["style"] = tbl.style.name
    b["dims"] = [len(tbl.rows), len(tbl.columns)]
    return b


def walk(parent, keep_runs=True):
    """Yield blocks in true document order (paragraphs and tables interleaved)."""
    body = parent.element.body if hasattr(parent, "element") else parent._element
    for child in body.iterchildren():
        if child.tag == f"{W}p":
            blk = par_block(Paragraph(child, parent), keep_runs)
            if blk:
                yield blk
        elif child.tag == f"{W}tbl":
            yield table_block(Table(child, parent), keep_runs)


def extract_images(path, out_dir):
    saved = []
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.startswith("word/media/"):
                os.makedirs(out_dir, exist_ok=True)
                dest = os.path.join(out_dir, os.path.basename(n))
                with z.open(n) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                saved.append({"file": os.path.basename(n), "bytes": z.getinfo(n).file_size})
    return saved


def image_inventory(path):
    with zipfile.ZipFile(path) as z:
        return [
            {"file": os.path.basename(n), "bytes": z.getinfo(n).file_size}
            for n in z.namelist()
            if n.startswith("word/media/")
        ]


def headers_footers(d):
    out = {"headers": [], "footers": []}
    for i, sec in enumerate(d.sections):
        for key, obj in (("headers", sec.header), ("footers", sec.footer)):
            try:
                txt = [p.text for p in obj.paragraphs if p.text.strip()]
            except Exception:
                txt = []
            if txt:
                out[key].append({"section": i, "text": txt})
    return out


# ---------------------------------------------------------------- emit

TEMPLATE = '''#!/usr/bin/env python3
# Auto-generated from {src!r} on {when}
# by docx_to_py.py — do not hand-edit; regenerate instead.
#
# META    : document properties and counts
# BLOCKS  : every paragraph / heading / table, in document order
# IMAGES  : embedded media inventory
# HF      : header and footer text
#
# Block shapes:
#   {{"type":"heading","level":N,"text":...,"style":...}}
#   {{"type":"p","text":...,"style":...,"list":bool,"ilvl":N,
#     "runs":[...],"links":[...],"images":[...],"textbox":[...]}}
#   {{"type":"table","dims":[rows,cols],"rows":[[{{"text":...}},...],...]}}

META = {meta}

IMAGES = {images}

HF = {hf}

BLOCKS = {blocks}


def outline(max_level=3):
    """Print the heading tree."""
    for b in BLOCKS:
        if b["type"] == "heading" and b.get("level", 9) <= max_level:
            print("  " * b.get("level", 0) + b["text"])


def plain_text():
    """Whole document as flat text."""
    out = []
    for b in BLOCKS:
        if b["type"] == "table":
            for row in b["rows"]:
                out.append(" | ".join(c["text"] for c in row))
        else:
            out.append(b["text"])
    return "\\n".join(out)


def find(needle):
    """Index + block for every block containing needle (case-insensitive)."""
    n = needle.lower()
    return [(i, b) for i, b in enumerate(BLOCKS)
            if n in str(b.get("text", "")).lower()
            or (b["type"] == "table" and n in str(b["rows"]).lower())]


if __name__ == "__main__":
    print(f"{{META['paragraphs']}} paragraphs, {{META['tables']}} tables, "
          f"{{len(IMAGES)}} images, {{META['words']}} words\\n")
    outline()
'''


def main():
    ap = argparse.ArgumentParser(description="Flatten a .docx into a Python data file.")
    ap.add_argument("docx", help="path to .docx")
    ap.add_argument("-o", "--out", help="output .py (default: <stem>_data.py)")
    ap.add_argument("--images", action="store_true", help="also extract media to <stem>_images/")
    ap.add_argument("--no-runs", action="store_true", help="skip per-run formatting (smaller file)")
    args = ap.parse_args()

    if not os.path.isfile(args.docx):
        sys.exit(f"not found: {args.docx}")

    d = docx.Document(args.docx)
    keep_runs = not args.no_runs
    blocks = list(walk(d, keep_runs))

    stem = os.path.splitext(os.path.basename(args.docx))[0]
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", stem).strip("_")
    out_path = args.out or f"{safe}_data.py"

    if args.images:
        imgs = extract_images(args.docx, f"{safe}_images")
    else:
        imgs = image_inventory(args.docx)

    cp = d.core_properties
    words = sum(len(b.get("text", "").split()) for b in blocks)
    meta = {
        "source": os.path.basename(args.docx),
        "extracted": datetime.now().isoformat(timespec="seconds"),
        "title": cp.title or None,
        "author": cp.author or None,
        "last_modified_by": cp.last_modified_by or None,
        "created": str(cp.created) if cp.created else None,
        "modified": str(cp.modified) if cp.modified else None,
        "revision": cp.revision,
        "paragraphs": sum(1 for b in blocks if b["type"] in ("p", "heading")),
        "headings": sum(1 for b in blocks if b["type"] == "heading"),
        "tables": sum(1 for b in blocks if b["type"] == "table"),
        "words": words,
        "sections": len(d.sections),
    }

    def pyrepr(obj):
        # pprint emits valid Python literals (None/True/False), unlike json.
        return pprint.pformat(obj, indent=1, width=100, sort_dicts=False)

    body = TEMPLATE.format(
        src=os.path.basename(args.docx),
        when=datetime.now().strftime("%Y-%m-%d %H:%M"),
        meta=pyrepr(meta),
        images=pyrepr(imgs),
        hf=pyrepr(headers_footers(d)),
        blocks=pyrepr(blocks),
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body)

    size = os.path.getsize(out_path) / 1024
    print(f"wrote {out_path}  ({size:.0f} KB)")
    print(f"  {meta['paragraphs']} paragraphs, {meta['headings']} headings, "
          f"{meta['tables']} tables, {len(imgs)} images, {meta['words']} words")
    if args.images:
        print(f"  images -> {safe}_images/")
    if size > 900:
        print("  NOTE: large. Re-run with --no-runs to shrink it.")


if __name__ == "__main__":
    main()
