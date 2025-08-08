# pdf_template_engine/prepare_backgrounds.py
from pathlib import Path
from pdf2image import convert_from_path   # pip install pdf2image

SRC = Path(__file__).parent.parent / 'pdf_templates_static'
DST = Path(__file__).parent / 'bg'
DST.mkdir(exist_ok=True)

for i in range(1, 7):
    pdf_in  = SRC / f'{i:02d}.pdf'
    png_out = DST / f'{i:02d}.png'
    img = convert_from_path(pdf_in, dpi=300)[0]
    img.save(png_out)
    print('✓ exportiert', png_out)
