"""
Ermittelt aus allen PDF-Vorlagen jeden Textblock
und speichert X/Y (Ursprung links-unten) in YAML.
"""
from pathlib import Path
import re, yaml, pdfplumber, collections

SRC = Path("pdf_templates_static")              # hier liegen 01.pdf … 06.pdf
OUT = Path("coords_raw.yaml")

all_pages = collections.OrderedDict()

for pdf_file in sorted(SRC.glob("[01][02][03][04][05][06].pdf")):
    doc = pdfplumber.open(pdf_file)
    page = doc.pages[0]                   # jede deiner Vorlagen hat 1 Seite
    h = page.height
    # Zeilen bilden
    lines = {}
    for w in page.extract_words():
        key = round(w["top"], 1)          # Zeilenhöhe als Gruppenschlüssel
        lines.setdefault(key, []).append(w)
    # sortiert durchgehen
    page_dict = collections.OrderedDict()
    for top in sorted(lines):
        wlist = sorted(lines[top], key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in wlist)
        slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60]
        x = min(w["x0"] for w in wlist)
        y = h - min(w["top"] for w in wlist)
        page_dict[slug] = [round(x, 1), round(y, 1)]
    all_pages[pdf_file.stem] = page_dict

yaml.dump(all_pages, open(OUT, "w"), allow_unicode=True)
print("✓ Koordinaten in", OUT)
