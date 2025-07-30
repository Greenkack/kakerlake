import fitz
import os

OUTPUT_DIR = "output"
pdf_neu = fitz.open()

anzahl_seiten = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith("_details.txt")])

for seite in range(1, anzahl_seiten + 1):
    detailfile = os.path.join(OUTPUT_DIR, f"seite_{seite}_details.txt")

    # Seitengröße laden
    with open(detailfile, "r", encoding="utf-8") as df:
        seiten_info = df.readline().split(":")[1].strip().split(",")
        rect = fitz.Rect([float(c) for c in seiten_info])

    # Seite exakt erzeugen
    page = pdf_neu.new_page(width=rect.width, height=rect.height)

    # Texte exakt einfügen
    textfile = os.path.join(OUTPUT_DIR, f"seite_{seite}_texte.txt")
    with open(textfile, "r", encoding="utf-8") as tf:
        blocks = tf.read().split("-" * 40)
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 5:
                text = lines[0][6:]
                position = eval(lines[1][10:])
                schriftart = lines[2][12:]
                schriftgroesse = float(lines[3][13:])
                farbe = int(lines[4][7:])

                # Text exakt platzieren
                page.insert_textbox(
                    fitz.Rect(position),
                    text,
                    fontsize=schriftgroesse,
                    fontname="helv",  # Standard oder exakte Fontdatei notwendig
                    fill=farbe,
                )

    # Bilder exakt einfügen
    bildpos_file = os.path.join(OUTPUT_DIR, f"seite_{seite}_bilder_positionen.txt")
    if os.path.exists(bildpos_file):
        with open(bildpos_file, "r", encoding="utf-8") as bf:
            for line in bf:
                parts = line.strip().split(":")
                bildname = f"seite_{seite}_bild_{parts[0].split()[1].strip()}.png"
                bildpath = os.path.join(OUTPUT_DIR, bildname)
                rect = fitz.Rect(eval(parts[1].strip()))
                if os.path.exists(bildpath):
                    page.insert_image(rect, filename=bildpath)

    # Formen exakt einfügen (Linien, Rechtecke)
    formenfile = os.path.join(OUTPUT_DIR, f"seite_{seite}_formen.txt")
    if os.path.exists(formenfile):
        shape = page.new_shape()
        with open(formenfile, "r", encoding="utf-8") as sf:
            for line in sf:
                if line.startswith("Linie von"):
                    coords = line[9:].split("nach")
                    p1 = eval(coords[0].strip())
                    p2 = eval(coords[1].strip())
                    shape.draw_line(p1, p2)
                elif line.startswith("Rechteck:"):
                    rect_coords = eval(line[9:].strip())
                    rect = fitz.Rect(rect_coords)
                    shape.draw_rect(rect)
            shape.finish(color=(0, 0, 0), fill=None, width=0.5)
            
        from txt_to_pdf_integration import generate_pdf_from_txt_files

        pdf_bytes = generate_pdf_from_txt_files(
            project_data=project_data, analysis_results=analysis_results
        )
            

# PDF speichern
pdf_neu.save("output/final_recreated.pdf")
print(" PDF exakt neu erstellt.")
