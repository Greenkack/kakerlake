import fitz, os, glob, re, ast

# Pfade
BASE_DIR   = os.getcwd()                     # C:\123456\12345
DATA_DIR   = os.path.join(BASE_DIR, "input") # enthält seite_*_*.txt und seite_*_bild_*.*
OUTPUT_PDF = os.path.join(BASE_DIR, "recreated_full.pdf")

# Neues PDF
doc = fitz.open()

# 0) Liste aller Seiten-Nummern
detail_files = glob.glob(os.path.join(DATA_DIR, "seite_*_details.txt"))
page_nums = sorted({
    int(re.search(r"seite_(\d+)_details\.txt", os.path.basename(f)).group(1))
    for f in detail_files
})

for p in page_nums:
    # A) Seitengröße lesen
    rect = None
    with open(os.path.join(DATA_DIR, f"seite_{p}_details.txt"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("Seitengröße:"):
                m = re.search(r"Rect\(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)", line)
                x0, y0, x1, y1 = map(float, m.groups())
                rect = fitz.Rect(x0, y0, x1, y1)
                break
    if rect is None:
        continue

    # Neue Seite in exakter Größe
    page = doc.new_page(width=rect.width, height=rect.height)

    # B) Texte einfügen – mit insert_text, um sicher sichtbar zu sein
    txt_path = os.path.join(DATA_DIR, f"seite_{p}_texte.txt")
    if os.path.exists(txt_path):
        for block in open(txt_path, encoding="utf-8").read().split("-"*40):
            lines = [l for l in block.splitlines() if l.strip()]
            d = {}
            for L in lines:
                if L.startswith("Text:"):
                    d["text"] = L.split("Text:",1)[1].strip()
                elif L.startswith("Position:"):
                    d["bbox"] = ast.literal_eval(L.split("Position:",1)[1].strip())
                elif L.startswith("Schriftgröße:"):
                    d["size"] = float(L.split("Schriftgröße:",1)[1].strip())
                elif L.startswith("Farbe:"):
                    d["color"] = int(L.split("Farbe:",1)[1].strip())
            if "text" in d and "bbox" in d:
                x0, y0, x1, y1 = d["bbox"]
                # RGB 0–255 → 0–1
                r = (d["color"] >> 16 & 255) / 255
                g = (d["color"] >> 8  & 255) / 255
                b = (d["color"]       & 255) / 255
                # Zeichne den Text oben-links im Textfeld
                page.insert_text(
                    (x0, y0),
                    d["text"],
                    fontname="helv",          # Fallback auf Helvetica
                    fontsize=d.get("size", 12),
                    color=(r, g, b)
                )

    # C) Bilder platzieren
    imgpos = os.path.join(DATA_DIR, f"seite_{p}_bilder_positionen.txt")
    if os.path.exists(imgpos):
        for L in open(imgpos, encoding="utf-8"):
            m = re.match(r"Bild (\d+): Rect\(([^)]+)\)", L)
            if not m: continue
            idx, coords = m.group(1), m.group(2)
            bbox = ast.literal_eval(f"({coords})")
            for ext in ("png","jpg","jpeg","tif","tiff"):
                fn = os.path.join(DATA_DIR, f"seite_{p}_bild_{idx}.{ext}")
                if os.path.exists(fn):
                    page.insert_image(fitz.Rect(bbox), filename=fn)
                    break

    # D) Formen direkt auf Seite zeichnen
    form_path = os.path.join(DATA_DIR, f"seite_{p}_formen.txt")
    if os.path.exists(form_path):
        for L in open(form_path, encoding="utf-8"):
            L = L.strip()
            # Linie
            if L.startswith("Linie von"):
                pts = re.findall(r"\(([^,]+), ([^)]+)\)", L)
                p1 = tuple(map(float, pts[0]))
                p2 = tuple(map(float, pts[1]))
                page.draw_line(p1, p2, color=(0,0,0), width=0.5)
            # Rechteck
            elif L.startswith("Rechteck:"):
                m = re.search(r"Rect\(([^)]+)\)", L)
                if m:
                    vals = [float(v) for v in m.group(1).split(",")]
                    page.draw_rect(fitz.Rect(*vals), color=(0,0,0), width=0.5)
            # Bezier‑Kurve
            elif L.startswith("Bezier-Kurve:"):
                pts = re.findall(r"Point\(([^)]+)\)", L)
                P = [tuple(map(float, pt.split(", "))) for pt in pts]
                if len(P)==4:
                    page.draw_bezier(P[0], P[1], P[2], P[3], color=(0,0,0), width=0.5)

    # E) Annotationen
    annot_path = os.path.join(DATA_DIR, f"seite_{p}_annotationen.txt")
    if os.path.exists(annot_path):
        for block in open(annot_path, encoding="utf-8").read().split("-"*40):
            lines = [l for l in block.splitlines() if l.strip()]
            ad = {}
            for L in lines:
                if L.startswith("Inhalt:"):
                    ad["content"] = L.split("Inhalt:",1)[1].strip()
                elif L.startswith("Position:"):
                    ad["rect"] = ast.literal_eval(L.split("Position:",1)[1].strip())
            if ad.get("content") and ad.get("rect"):
                page.add_text_annot(fitz.Rect(ad["rect"]), ad["content"])

# 4) PDF speichern
doc.save(OUTPUT_PDF)
print("✅ Fertig – Deine PDF liegt hier:", OUTPUT_PDF)
