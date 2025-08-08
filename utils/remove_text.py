# utils/remove_text.py
# -----------------------------------------------------------
# erzeugt textfreie Kopien (nt_01.pdf … nt_06.pdf)
# -----------------------------------------------------------

from pathlib import Path
import fitz            # PyMuPDF  ->  pip install pymupdf

BASE = Path(__file__).resolve().parent.parent        # Projekt-Root
SRC  = BASE / "pdf_templates_static"                 # Ordner mit 01.pdf …
DST  = SRC / "notext"                                # Zielordner
DST.mkdir(parents=True, exist_ok=True)

for pdf_in in SRC.glob("[0-9][0-9].pdf"):            # alle 01.pdf … 06.pdf
    print("Bearbeite", pdf_in.name)
    doc = fitz.open(pdf_in)
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:                   # Text-Block
                r = fitz.Rect(block["bbox"])
                page.add_redact_annot(r, fill=(1, 1, 1))
        page.apply_redactions()                      # Text vollständig ausgeblendet
    out = DST / f"nt_{pdf_in.name}"
    doc.save(out)
    print(" ✓ gespeichert:", out.name)
