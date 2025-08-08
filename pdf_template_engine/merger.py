# merger.py  (nur die Pfad-Definition und Schleife ändern)
from pathlib import Path, PurePosixPath
import io
from pypdf import PdfReader, PdfWriter

BG = Path(__file__).parent / "bg_pdf"      # << NEU

def merge_first_six_pages(overlay_bytes: bytes) -> bytes:
    writer = PdfWriter()
    ovl = PdfReader(io.BytesIO(overlay_bytes))

    for i in range(1, 7):
        base = PdfReader(BG / f"nt_{i:02d}.pdf").pages[0]
        base.merge_page(ovl.pages[i-1])    # Overlay drüber
        writer.add_page(base)

    out = io.BytesIO(); writer.write(out)
    return out.getvalue()
