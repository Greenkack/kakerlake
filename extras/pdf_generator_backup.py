"""
Datei: pdf_generator.py
Zweck: Erzeugt Angebots-PDFs für die Solar-App.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-03
"""
# pdf_generator.py

from __future__ import annotations
import base64
import io
import math
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
import os
from io import BytesIO

_REPORTLAB_AVAILABLE = False
_PYPDF_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (Frame, Image, PageBreak, PageTemplate,
        Paragraph, SimpleDocTemplate, Spacer, Table,
        TableStyle, Flowable, KeepInFrame, KeepTogether)
    from reportlab.lib import pagesizes
    _REPORTLAB_AVAILABLE = True
except ImportError:
    pass
except Exception as e_reportlab_import:
    pass

try:
    from pypdf import PdfReader, PdfWriter
    _PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        _PYPDF_AVAILABLE = True
    except ImportError:
        class PdfReader: # type: ignore
            def __init__(self, *args, **kwargs): pass
            @property
            def pages(self): return []
        class PdfWriter: # type: ignore
            def __init__(self, *args, **kwargs): pass
            def add_page(self, page): pass
            def write(self, stream): pass
        _PYPDF_AVAILABLE = False
except Exception as e_pypdf_import:
    class PdfReader: # type: ignore
        def __init__(self, *args, **kwargs): pass
        @property
        def pages(self): return []
    class PdfWriter: # type: ignore
        def __init__(self, *args, **kwargs): pass
        def add_page(self, page): pass
        def write(self, stream): pass
    _PYPDF_AVAILABLE = False

_PDF_GENERATOR_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Da pdf_generator.py im selben Verzeichnis wie der data/ Ordner liegt, ist der Basis-Pfad korrekt
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "product_datasheets")
COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "company_docs")


def get_text(texts_dict: Dict[str, str], key: str, fallback_text_value: Optional[str] = None) -> str:
    if not isinstance(texts_dict, dict): return fallback_text_value if fallback_text_value is not None else key
    if fallback_text_value is None: fallback_text_value = key.replace("_", " ").title() + " (PDF-Text fehlt)"
    retrieved = texts_dict.get(key, fallback_text_value)
    return str(retrieved)

def format_kpi_value(value: Any, unit: str = "", na_text_key: str = "not_applicable_short", precision: int = 2, texts_dict: Optional[Dict[str,str]] = None) -> str:
    current_texts = texts_dict if texts_dict is not None else {}
    na_text = get_text(current_texts, na_text_key, "k.A.")
    if value is None or (isinstance(value, (float, int)) and math.isnan(value)): return na_text
    if isinstance(value, str) and value == na_text: return value
    if isinstance(value, str):
        try:
            cleaned_value_str = value
            if '.' in value and ',' in value:
                 if value.rfind('.') > value.rfind(','): cleaned_value_str = value.replace(',', '')
                 elif value.rfind(',') > value.rfind('.'): cleaned_value_str = value.replace('.', '')
            cleaned_value_str = cleaned_value_str.replace(',', '.')
            value = float(cleaned_value_str)
        except ValueError: return value

    if isinstance(value, (int, float)):
        if math.isinf(value): return get_text(current_texts, "value_infinite", "Nicht berechenbar")
        if unit == "Jahre": return get_text(current_texts, "years_format_string_pdf", "{val:.1f} Jahre").format(val=value)
        
        formatted_num_en = f"{value:,.{precision}f}"
        formatted_num_de = formatted_num_en.replace(",", "#TEMP#").replace(".", ",").replace("#TEMP#", ".")
        return f"{formatted_num_de} {unit}".strip()
    return str(value)

STYLES: Any = {}
FONT_NORMAL = "Helvetica"; FONT_BOLD = "Helvetica-Bold"; FONT_ITALIC = "Helvetica-Oblique"
# KORREKTUR: Standardfarben gemäß neuen Designrichtlinien
PRIMARY_COLOR_HEX = "#1B365D"  # Dunkelblau - Professionell und vertrauensvoll 
SECONDARY_COLOR_HEX = "#2E8B57" # Solargrün - Nachhaltigkeit und Energie
ACCENT_COLOR_HEX = "#FFB347"       # Sonnenorange - Wärme und Optimismus
TEXT_COLOR_HEX = "#2C3E50"         # Anthrazit - Optimale Lesbarkeit
BACKGROUND_COLOR_HEX = "#F8F9FA"   # Hellgrau - Modern und Clean
TEXT_COLOR_HEX = "#333333"
SEPARATOR_LINE_COLOR_HEX = "#E9ECEF" # Subtile, moderne Linienfarbe

# Moderne Farbpalette als Dictionary für bessere Zugänglichkeit
COLORS = {
    'accent_primary': PRIMARY_COLOR_HEX,
    'accent_secondary': SECONDARY_COLOR_HEX,
    'accent_orange': ACCENT_COLOR_HEX,
    'text_dark': TEXT_COLOR_HEX,
    'background_light': BACKGROUND_COLOR_HEX,
    'separator_line': SEPARATOR_LINE_COLOR_HEX,
    'table_header_bg': PRIMARY_COLOR_HEX,
    'table_header_text': '#FFFFFF',
    'table_row_bg': '#FAFBFC',
    'table_alt_row_bg': '#F1F3F4',
    'table_border': '#E1E5E9',
    'success_green': '#28A745',
    'warning_orange': '#FFC107',
    'error_red': '#DC3545',
    'info_blue': '#17A2B8'
}

if _REPORTLAB_AVAILABLE:
    STYLES = getSampleStyleSheet()
    STYLES.add(ParagraphStyle(name='NormalLeft', alignment=TA_LEFT, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='NormalRight', alignment=TA_RIGHT, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='NormalCenter', alignment=TA_CENTER, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='Footer', parent=STYLES['NormalCenter'], fontName=FONT_ITALIC, fontSize=8, textColor=colors.darkgrey)) # Dunkleres Grau für Footer
    STYLES.add(ParagraphStyle(name='OfferTitle', parent=STYLES['h1'], fontName=FONT_BOLD, fontSize=24, alignment=TA_CENTER, spaceBefore=1.5*cm, spaceAfter=1.5*cm, textColor=colors.HexColor(PRIMARY_COLOR_HEX), leading=28)) # Größer und eleganter
    STYLES.add(ParagraphStyle(name='SectionTitle', parent=STYLES['h2'], fontName=FONT_BOLD, fontSize=16, spaceBefore=1.2*cm, spaceAfter=0.8*cm, keepWithNext=1, textColor=colors.HexColor(PRIMARY_COLOR_HEX), leading=20)) # Moderner
    STYLES.add(ParagraphStyle(name='SubSectionTitle', parent=STYLES['h3'], fontName=FONT_BOLD, fontSize=13, spaceBefore=1*cm, spaceAfter=0.5*cm, keepWithNext=1, textColor=colors.HexColor(SECONDARY_COLOR_HEX), leading=16)) # Sekundärfarbe für Abwechslung
    STYLES.add(ParagraphStyle(name='ComponentTitle', parent=STYLES['SubSectionTitle'], fontSize=11, spaceBefore=0.5*cm, spaceAfter=0.2*cm, alignment=TA_LEFT, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CompanyInfoDeckblatt', parent=STYLES['NormalCenter'], fontName=FONT_NORMAL, fontSize=9, leading=11, spaceAfter=0.5*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CoverLetter', parent=STYLES['NormalLeft'], fontSize=11, leading=15, spaceBefore=0.5*cm, spaceAfter=0.5*cm, alignment=TA_JUSTIFY, firstLineIndent=0, leftIndent=0, rightIndent=0, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Etwas mehr Zeilenabstand    # Neuer Stil für rechtsbündige Kundenadresse auf Deckblatt
    STYLES.add(ParagraphStyle(name='CustomerAddressDeckblattRight', parent=STYLES['NormalRight'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CustomerAddressInner', parent=STYLES['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Für Anschreiben etc.
    # FEHLENDER STYLE - CustomerAddress (allgemein)
    STYLES.add(ParagraphStyle(name='CustomerAddress', parent=STYLES['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    
    STYLES.add(ParagraphStyle(name='TableText', parent=STYLES['NormalLeft'], fontName=FONT_NORMAL, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Helvetica für Tabellentext
    STYLES.add(ParagraphStyle(name='TableTextSmall', parent=STYLES['NormalLeft'], fontName=FONT_NORMAL, fontSize=8, leading=10, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableNumber', parent=STYLES['NormalRight'], fontName=FONT_NORMAL, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableLabel', parent=STYLES['NormalLeft'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    # KORREKTUR: Tabellenheader Farbe und Textfarbe
    STYLES.add(ParagraphStyle(name='TableHeader', parent=STYLES['NormalCenter'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.white, backColor=colors.HexColor(PRIMARY_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableBoldRight', parent=STYLES['NormalRight'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='ImageCaption', parent=STYLES['NormalCenter'], fontName=FONT_ITALIC, fontSize=8, spaceBefore=0.1*cm, textColor=colors.grey))
    STYLES.add(ParagraphStyle(name='ChartTitle', parent=STYLES['SubSectionTitle'], alignment=TA_CENTER, spaceBefore=0.6*cm, spaceAfter=0.2*cm, fontSize=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='ChapterHeader', parent=STYLES['NormalRight'], fontName=FONT_NORMAL, fontSize=9, textColor=colors.grey, alignment=TA_RIGHT))

    TABLE_STYLE_DEFAULT = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL),('ALIGN',(1,0),(1,-1),'LEFT'), # Werte linksbündig für Standardtabelle
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)), # Dezente Gridlinien
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),3*mm), ('RIGHTPADDING',(0,0),(-1,-1),3*mm),
        ('TOPPADDING',(0,0),(-1,-1),2*mm), ('BOTTOMPADDING',(0,0),(-1,-1),2*mm)
    ])
    # KORREKTUR: DATA_TABLE_STYLE für Konsistenz
    DATA_TABLE_STYLE = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PRIMARY_COLOR_HEX)), # Kopfzeile Primärfarbe
        ('TEXTCOLOR',(0,0),(-1,0),colors.white), # Kopfzeile Text weiß
        ('FONTNAME',(0,0),(-1,0),FONT_BOLD),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL), # Datenzellen Helvetica
        ('ALIGN',(0,1),(0,-1),'LEFT'), # Erste Datenspalte links
        ('ALIGN',(1,1),(-1,-1),'RIGHT'), # Andere Datenspalten rechts (für Zahlen)
        ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm), 
        ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)) # Textfarbe Datenzellen
    ])
    PRODUCT_TABLE_STYLE = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL), ('ALIGN',(1,0),(1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm)
    ])
    PRODUCT_MAIN_TABLE_STYLE = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)])

    # MODERNE TABELLENSTYLES mit Zebra-Streifen
    def create_zebra_table_style(num_rows, header_bg=PRIMARY_COLOR_HEX, alt_bg=BACKGROUND_COLOR_HEX):
        """Erstellt einen modernen Tabellenstil mit Zebra-Streifen"""
        style = [
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(header_bg)), # Header
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),FONT_BOLD),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL),
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
            ('LEFTPADDING',(0,0),(-1,-1),3*mm),
            ('RIGHTPADDING',(0,0),(-1,-1),3*mm),
            ('TOPPADDING',(0,0),(-1,-1),2.5*mm),
            ('BOTTOMPADDING',(0,0),(-1,-1),2.5*mm),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ]
        # Zebra-Streifen für ungerade Zeilen
        for row in range(1, num_rows):
            if row % 2 == 0:  # Jede zweite Zeile
                style.append(('BACKGROUND',(0,row),(-1,row),colors.HexColor(alt_bg)))
        return TableStyle(style)
        
    # MODERNE PRODUKT-TABELLE mit Schatten-Effekt
    MODERN_PRODUCT_TABLE_STYLE = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), 
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL),
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),4*mm),
        ('RIGHTPADDING',(0,0),(-1,-1),4*mm),
        ('TOPPADDING',(0,0),(-1,-1),3*mm),
        ('BOTTOMPADDING',(0,0),(-1,-1),3*mm),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#FFFFFF")),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ('LINEBELOW',(0,0),(-1,0),2,colors.HexColor(PRIMARY_COLOR_HEX)), # Elegante Unterstreichung
    ])

class PageNumCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._page_layout_callback = kwargs.pop('onPage_callback', None)
        self._callback_kwargs = kwargs.pop('callback_kwargs', {})
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.total_pages = 0 
        self.current_chapter_title_for_header = '' 
    def showPage(self): 
        self._saved_page_states.append(dict(self.__dict__))
        super().showPage()
    
    def save(self):
        self.total_pages = len(self._saved_page_states)
        for state_idx, state in enumerate(self._saved_page_states):
            self.__dict__.update(state) 
            self._pageNumber = state_idx + 1 
            if self._page_layout_callback:
                self._page_layout_callback(canvas_obj=self, doc_template=self._doc, **self._callback_kwargs)
        super().save()

class SetCurrentChapterTitle(Flowable):
    def __init__(self, title): Flowable.__init__(self); self.title = title
    def wrap(self, availWidth, availHeight): return 0,0
    def draw(self):
        if hasattr(self, 'canv'): self.canv.current_chapter_title_for_header = self.title

# Einfache HRFlowable für Trennlinien, falls die ReportLab Version sie nicht direkt hat
class SimpleHRFlowable(Flowable):
    def __init__(self, width="100%", thickness=0.5, color=colors.HexColor(SEPARATOR_LINE_COLOR_HEX), spaceBefore=0.2*cm, spaceAfter=0.2*cm, vAlign='BOTTOM'):
        Flowable.__init__(self)
        self.width_spec = width
        self.thickness = thickness
        self.color = color
        self.spaceBefore = spaceBefore
        self.spaceAfter = spaceAfter
        self.vAlign = vAlign # Kann 'TOP', 'MIDDLE', 'BOTTOM' sein

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        # y-Position anpassen basierend auf vAlign und Höhe des Flowables (nur thickness)
        y_pos = 0
        if self.vAlign == 'TOP':
            y_pos = -self.thickness 
        elif self.vAlign == 'MIDDLE':
            y_pos = -self.thickness / 2.0
        # Für 'BOTTOM' ist y_pos = 0 korrekt

        self.canv.line(0, y_pos, self.drawWidth, y_pos) # drawWidth wird von ReportLab gesetzt
        self.canv.restoreState()

    def wrap(self, availWidth, availHeight):
        self.drawWidth = availWidth # Nutze die verfügbare Breite
        if isinstance(self.width_spec, str) and self.width_spec.endswith('%'):
            self.drawWidth = availWidth * (float(self.width_spec[:-1]) / 100.0)
        elif isinstance(self.width_spec, (int, float)):
            self.drawWidth = self.width_spec
        return self.drawWidth, self.thickness + self.spaceBefore + self.spaceAfter

    def getSpaceBefore(self):
        return self.spaceBefore

    def getSpaceAfter(self):
        return self.spaceAfter

class SetCurrentChapterTitle(Flowable):
    def __init__(self, title): Flowable.__init__(self); self.title = title
    def wrap(self, availWidth, availHeight): return 0,0
    def draw(self):
        if hasattr(self, 'canv'): self.canv.current_chapter_title_for_header = self.title

def _update_styles_with_dynamic_colors(design_settings: Dict[str, str]):
    global PRIMARY_COLOR_HEX, SECONDARY_COLOR_HEX, SEPARATOR_LINE_COLOR_HEX, STYLES, DATA_TABLE_STYLE
    if not _REPORTLAB_AVAILABLE: return

    PRIMARY_COLOR_HEX = design_settings.get('primary_color', "#0055A4")
    # SECONDARY_COLOR_HEX wird aktuell nicht stark verwendet, da #F2F2F2 sehr hell ist.
    # Für Hintergründe etc. können wir es definieren, aber Tabellenheader nutzen Primärfarbe.
    SECONDARY_COLOR_HEX = design_settings.get('secondary_color', "#F2F2F2") 
    SEPARATOR_LINE_COLOR_HEX = design_settings.get('separator_color', "#CCCCCC") # Eigene Farbe für Trennlinien

    if STYLES: # Nur wenn STYLES initialisiert wurde
        STYLES['OfferTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['SectionTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['SubSectionTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX) # Subsektionen auch in Primärfarbe
        
        # Tabellenheader explizit mit Primärfarbe und weißem Text
        STYLES['TableHeader'].backColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['TableHeader'].textColor = colors.white
        
        DATA_TABLE_STYLE = TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PRIMARY_COLOR_HEX)), 
            ('TEXTCOLOR',(0,0),(-1,0),colors.white), 
            ('FONTNAME',(0,0),(-1,0),FONT_BOLD), ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL),
            ('ALIGN',(0,1),(0,-1),'LEFT'), ('ALIGN',(1,1),(-1,-1),'RIGHT'),
            ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
            ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm), 
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX))
        ])


def _get_image_flowable(image_data_input: Optional[Union[str, bytes]], desired_width: float, texts: Dict[str, str], caption_text_key: Optional[str] = None, max_height: Optional[float] = None, align: str = 'CENTER') -> List[Any]:
    flowables: List[Any] = []
    if not _REPORTLAB_AVAILABLE: return flowables
    img_data_bytes: Optional[bytes] = None

    if isinstance(image_data_input, str) and image_data_input.strip().lower() not in ["", "none", "null", "nan"]:
        try:
            if image_data_input.startswith('data:image'): image_data_input = image_data_input.split(',', 1)[1]
            img_data_bytes = base64.b64decode(image_data_input)
        except Exception: img_data_bytes = None 
    elif isinstance(image_data_input, bytes): img_data_bytes = image_data_input
    
    if img_data_bytes:
        try:
            if not img_data_bytes: raise ValueError("Bilddaten sind leer nach Verarbeitung.")
            img_file_like = io.BytesIO(img_data_bytes)
            img_reader = ImageReader(img_file_like)
            iw, ih = img_reader.getSize()
            if iw <= 0 or ih <= 0: raise ValueError(f"Ungültige Bilddimensionen: w={iw}, h={ih}")
            aspect = ih / float(iw) if iw > 0 else 1.0
            img_h_calc = desired_width * aspect; img_w_final, img_h_final = desired_width, img_h_calc
            if max_height and img_h_calc > max_height: img_h_final = max_height; img_w_final = img_h_final / aspect if aspect > 0 else desired_width
            
            # KORREKTUR: Stelle sicher, dass img_w_final und img_h_final positiv sind
            if img_w_final <=0 or img_h_final <=0:
                raise ValueError(f"Finale Bilddimensionen ungültig: w={img_w_final}, h={img_h_final}")

            img = Image(io.BytesIO(img_data_bytes), width=img_w_final, height=img_h_final)
            img.hAlign = align.upper(); flowables.append(img)
            if caption_text_key:
                caption_text = get_text(texts, caption_text_key, "")
                if caption_text and not caption_text.startswith(caption_text_key) and not caption_text.endswith("(PDF-Text fehlt)"):
                    flowables.append(Spacer(1, 0.1*cm)); flowables.append(Paragraph(caption_text, STYLES['ImageCaption']))
        except Exception: 
            if caption_text_key :
                caption_text_fb = get_text(texts, caption_text_key, "")
                if caption_text_fb and not caption_text_fb.startswith(caption_text_key):
                     flowables.append(Paragraph(f"<i>({caption_text_fb}: {get_text(texts, 'image_not_available_pdf', 'Bild nicht verfügbar')})</i>", STYLES['ImageCaption']))
    elif caption_text_key:
        caption_text_fb = get_text(texts, caption_text_key, "")
        if caption_text_fb and not caption_text_fb.startswith(caption_text_key):
            flowables.append(Paragraph(f"<i>({caption_text_fb}: {get_text(texts, 'image_not_available_pdf', 'Bild nicht verfügbar')})</i>", STYLES['ImageCaption']))
    return flowables

def page_layout_handler(canvas_obj: canvas.Canvas, doc_template: SimpleDocTemplate, texts_ref: Dict[str, str], company_info_ref: Dict, company_logo_base64_ref: Optional[str], offer_number_ref: str, page_width_ref: float, page_height_ref: float, margin_left_ref: float, margin_right_ref: float, margin_top_ref: float, margin_bottom_ref: float, doc_width_ref: float, doc_height_ref: float, include_custom_footer_ref: bool = True, include_header_logo_ref: bool = True):
    canvas_obj.saveState()
    current_chapter_title = getattr(canvas_obj, 'current_chapter_title_for_header', '')
    page_num = canvas_obj.getPageNumber()

    # MODERNER HEADER für alle Seiten außer Deckblatt
    if page_num > 1:
        # Elegante Header-Linie in Primärfarbe
        canvas_obj.setStrokeColor(colors.HexColor(PRIMARY_COLOR_HEX))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(margin_left_ref, page_height_ref - margin_top_ref + 0.3*cm, 
                       page_width_ref - margin_right_ref, page_height_ref - margin_top_ref + 0.3*cm)
        
        # Header-Text in moderner Typografie
        canvas_obj.setFont(FONT_NORMAL, 9)
        canvas_obj.setFillColor(colors.HexColor(TEXT_COLOR_HEX))
        header_text = f"Photovoltaik-Angebot • {company_info_ref.get('name', '')}"
        canvas_obj.drawString(margin_left_ref, page_height_ref - margin_top_ref + 0.7*cm, header_text)
          # Seitenzahl elegant rechts
        canvas_obj.setFont(FONT_NORMAL, 9)
        canvas_obj.setFillColor(colors.HexColor(SECONDARY_COLOR_HEX))
        page_text = f"Seite {page_num}"
        canvas_obj.drawRightString(page_width_ref - margin_right_ref, page_height_ref - margin_top_ref + 0.7*cm, page_text)    # FIRMENLOGO RECHTS OBEN auf jeder Seite (NEU wie gewünscht) - OPTIONAL
    if company_logo_base64_ref and include_header_logo_ref:
        try:
            logo_width, logo_height = 3*cm, 2*cm  # Größe für Header-Logo
            if not company_logo_base64_ref:
                raise ValueError("Kein gültiges Logo bereitgestellt.")
            logo_bytes_header = base64.b64decode(company_logo_base64_ref.split(',',1)[1]) if ',' in company_logo_base64_ref and len(company_logo_base64_ref.split(',',1)) > 1 else base64.b64decode(company_logo_base64_ref)
            img_reader_header = ImageReader(io.BytesIO(logo_bytes_header))
            iw, ih = img_reader_header.getSize()
            aspect = ih / float(iw) if iw > 0 else 1.0
            
            final_w_header, final_h_header = logo_width, logo_width * aspect
            if final_h_header > logo_height:
                final_h_header = logo_height
                final_w_header = final_h_header / aspect if aspect > 0 else logo_width
            
            # Rechts oben positionieren
            logo_x = page_width_ref - margin_right_ref - final_w_header
            logo_y = page_height_ref - margin_top_ref - final_h_header
            
            canvas_obj.drawImage(img_reader_header, logo_x, logo_y, 
                                 width=final_w_header, height=final_h_header, mask='auto', preserveAspectRatio=True)
        except Exception as e:
            print(f"Fehler beim Zeichnen des Logos im Header: {e}")

    # MODERNER FOOTER für alle Seiten
    footer_y = margin_bottom_ref - 0.8*cm    
    # Footer-Linie in Sekundärfarbe
    canvas_obj.setStrokeColor(colors.HexColor(SEPARATOR_LINE_COLOR_HEX))
    canvas_obj.setLineWidth(1)
    canvas_obj.line(margin_left_ref, footer_y + 0.5*cm, 
                   page_width_ref - margin_right_ref, footer_y + 0.5*cm)
    
    # Firmenlogo in Fußzeile (links)
    if company_logo_base64_ref:
        try:
            # Logik zum Zeichnen des Logos im Footer (wie zuvor)
            # _get_image_flowable ist für die Story, hier direkter Canvas-Draw:
            logo_width, logo_height = 1.8*cm, 1.0*cm # Zielgröße
            logo_bytes_for_draw = base64.b64decode(company_logo_base64_ref.split(',',1)[1]) if ',' in company_logo_base64_ref and len(company_logo_base64_ref.split(',',1)) > 1 else base64.b64decode(company_logo_base64_ref)
            img_reader_logo = ImageReader(io.BytesIO(logo_bytes_for_draw))
            iw, ih = img_reader_logo.getSize()
            aspect = ih / float(iw) if iw > 0 else 1.0
            
            final_w, final_h = logo_width, logo_width * aspect
            if final_h > logo_height:
                final_h = logo_height
                final_w = final_h / aspect if aspect > 0 else logo_width
            
            canvas_obj.drawImage(img_reader_logo, margin_left_ref, margin_bottom_ref * 0.30, 
                                 width=final_w, height=final_h, mask='auto', preserveAspectRatio=True)
        except Exception: pass
          # Kapitelüberschrift in Kopfzeile (rechts)
        if current_chapter_title:
            p_chapter = Paragraph(current_chapter_title, STYLES['ChapterHeader'])
            p_w, p_h = p_chapter.wrapOn(canvas_obj, doc_width_ref - (2.5*cm), margin_top_ref) 
            p_chapter.drawOn(canvas_obj, page_width_ref - margin_right_ref - p_w, page_height_ref - margin_top_ref + 0.3*cm)
        
    # CUSTOM FOOTER (OPTIONAL wie gewünscht)
    if include_custom_footer_ref:
        # Seitennummer und Angebotsinfo in Fußzeile (MITTIG wie gewünscht)
        page_info_text = get_text(texts_ref, "pdf_page_x_of_y", "Seite {current} von {total}").format(current=str(page_num), total=str(getattr(canvas_obj, 'total_pages', '??')))
        
        # NEUES FORMAT: "| Angebot TT.MMM.JJJJ | Seite xx von xxx |"
        offer_date = datetime.now().strftime('%d.%b.%Y')  # TT.MMM.JJJJ Format (z.B. 17.Jun.2025)
        footer_text = f"| Angebot {offer_date} | {page_info_text} |"
        
        # Footer mittig positionieren (wie gewünscht)
        canvas_obj.setFont(FONT_ITALIC, 8)
        text_width = canvas_obj.stringWidth(footer_text, FONT_ITALIC, 8)
        center_x = page_width_ref / 2
        canvas_obj.drawString(center_x - text_width/2, margin_bottom_ref * 0.45, footer_text)

        # Firmen-Fußzeilentext (linksbündig, nicht zentriert, gemäß neuer Anforderung)
        # "links die Firmendaten („Ömer’s Solar-Ding GmbH, Musterstraße 12, 12345 Musterstadt“)"
        company_footer_address_parts = [
            company_info_ref.get('name', ''),
            company_info_ref.get('street', ''),
            f"{company_info_ref.get('zip_code', '')} {company_info_ref.get('city', '')}".strip()
        ]
        company_footer_address = " | ".join(filter(None, company_footer_address_parts))
        if company_footer_address: # Nur zeichnen, wenn Text vorhanden ist
            canvas_obj.setFont(FONT_NORMAL, 7)
            # Positionierung direkt über dem Logo im Footer, falls vorhanden, oder etwas höher
            footer_text_y_pos = margin_bottom_ref * 0.85 if company_logo_base64_ref else margin_bottom_ref * 0.45
            canvas_obj.drawString(margin_left_ref, footer_text_y_pos, company_footer_address)

    canvas_obj.restoreState()

def _generate_complete_salutation_line(customer_data: Dict, texts: Dict[str, str]) -> str:
    salutation_value = customer_data.get("salutation") 
    title = customer_data.get("title", "")
    first_name = customer_data.get("first_name", "")
    last_name = customer_data.get("last_name", "")

    name_parts = [p for p in [title, first_name, last_name] if p and str(p).strip()]
    customer_full_name_for_salutation = " ".join(name_parts).strip()

    salutation_key_base = "salutation_polite"
    if isinstance(salutation_value, str):
        sl_lower = salutation_value.lower().strip()
        if sl_lower == "herr": salutation_key_base = "salutation_male_polite"
        elif sl_lower == "frau": salutation_key_base = "salutation_female_polite"
        elif sl_lower == "familie":
            fam_name = last_name if last_name and str(last_name).strip() else customer_data.get("company_name", get_text(texts, "family_default_name_pdf", "Familie"))
            return f"{get_text(texts, 'salutation_family_polite', 'Sehr geehrte Familie')} {str(fam_name).strip()},"
        elif sl_lower == "firma": 
            company_name_val = customer_data.get("company_name", "") or last_name 
            if company_name_val: return f"{get_text(texts, 'salutation_company_polite', 'Sehr geehrte Damen und Herren der Firma')} {str(company_name_val).strip()},"
            else: return get_text(texts, 'salutation_generic_fallback', 'Sehr geehrte Damen und Herren,')
    
    default_salutation_text = get_text(texts, salutation_key_base, "Sehr geehrte/r")
    
    if customer_full_name_for_salutation:
        return f"{default_salutation_text} {customer_full_name_for_salutation},"
    else: 
        return get_text(texts, 'salutation_generic_fallback', 'Sehr geehrte Damen und Herren,')


def _replace_placeholders(text_template: str, customer_data: Dict, company_info: Dict, offer_number: str, texts_dict: Dict[str, str], analysis_results_for_placeholder: Optional[Dict[str, Any]] = None) -> str:
    if text_template is None: text_template = ""
    processed_text = str(text_template)
    now_date_str = datetime.now().strftime('%d.%m.%Y')
    complete_salutation_line = _generate_complete_salutation_line(customer_data, texts_dict)
    
    ersatz_dict = {
        "[VollständigeAnrede]": complete_salutation_line,
        "[Ihr Name/Firmenname]": str(company_info.get("name", get_text(texts_dict, "company_name_default_placeholder_pdf", "Ihr Solarexperte"))),
        "[Angebotsnummer]": str(offer_number),
        "[Datum]": now_date_str,
        "[KundenNachname]": str(customer_data.get("last_name", "")),
        "[Nachname]": str(customer_data.get("last_name", "")),  # NEUER PLATZHALTER wie gewünscht
        "[KundenVorname]": str(customer_data.get("first_name", "")),
        "[KundenAnredeFormell]": str(customer_data.get("salutation", "")),
        "[KundenTitel]": str(customer_data.get("title", "")),
        "[KundenStrasseNr]": f"{customer_data.get('address','')} {customer_data.get('house_number','',)}".strip(),
        "[KundenPLZOrt]": f"{customer_data.get('zip_code','')} {customer_data.get('city','',)}".strip(),
        "[KundenFirmenname]": str(customer_data.get("company_name", "")),
    }
    if analysis_results_for_placeholder and isinstance(analysis_results_for_placeholder, dict):
        anlage_kwp_val = analysis_results_for_placeholder.get('anlage_kwp')
        ersatz_dict["[AnlagenleistungkWp]"] = format_kpi_value(anlage_kwp_val, "kWp", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if anlage_kwp_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")
        
        total_invest_brutto_val = analysis_results_for_placeholder.get('total_investment_brutto')
        ersatz_dict["[GesamtinvestitionBrutto]"] = format_kpi_value(total_invest_brutto_val, "€", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if total_invest_brutto_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")

        annual_benefit_yr1_val = analysis_results_for_placeholder.get('annual_financial_benefit_year1')
        ersatz_dict["[FinanziellerVorteilJahr1]"] = format_kpi_value(annual_benefit_yr1_val, "€", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if annual_benefit_yr1_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")

    for placeholder, value_repl in ersatz_dict.items():
        processed_text = processed_text.replace(placeholder, str(value_repl))
    return processed_text

def _get_next_offer_number(texts: Dict[str,str], load_admin_setting_func: Callable, save_admin_setting_func: Callable) -> str:
    try:
        current_suffix_obj = load_admin_setting_func('offer_number_suffix', 1000)
        current_suffix = int(str(current_suffix_obj)) if current_suffix_obj is not None else 1000
        next_suffix = current_suffix + 1
        save_admin_setting_func('offer_number_suffix', next_suffix)
        return f"AN{datetime.now().year}-{next_suffix:04d}"
    except Exception: 
        return f"AN{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def _prepare_cost_table_for_pdf(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[List[Any]]:
    cost_data_pdf = []
    cost_items_ordered_pdf = [
        ('base_matrix_price_netto', 'base_matrix_price_netto', True, 'TableText'),
        ('cost_modules_aufpreis_netto', 'cost_modules', True, 'TableText'),
        ('cost_inverter_aufpreis_netto', 'cost_inverter', True, 'TableText'),
        ('cost_storage_aufpreis_product_db_netto', 'cost_storage', True, 'TableText'),
        ('total_optional_components_cost_netto', 'total_optional_components_cost_netto_label', True, 'TableText'),
        ('cost_accessories_aufpreis_netto', 'cost_accessories_aufpreis_netto', True, 'TableText'),
        ('cost_scaffolding_netto', 'cost_scaffolding_netto', True, 'TableText'),
        ('cost_misc_netto', 'cost_misc_netto', True, 'TableText'),
        ('cost_custom_netto', 'cost_custom_netto', True, 'TableText'),
        ('subtotal_netto', 'subtotal_netto', True, 'TableBoldRight'),
        ('one_time_bonus_eur', 'one_time_bonus_eur_label', True, 'TableText'),
        ('total_investment_netto', 'total_investment_netto', True, 'TableBoldRight'),
        ('vat_rate_percent', 'vat_rate_percent', False, 'TableText'),
        ('total_investment_brutto', 'total_investment_brutto', True, 'TableBoldRight'),
    ]
    for result_key, label_key, is_euro_val, base_style_name in cost_items_ordered_pdf:
        value_cost = analysis_results.get(result_key)
        if value_cost is not None:
            if value_cost == 0.0 and result_key not in ['total_investment_netto', 'total_investment_brutto', 'subtotal_netto', 'vat_rate_percent', 'base_matrix_price_netto', 'one_time_bonus_eur']:
                continue
            label_text_pdf = get_text(texts, label_key, label_key.replace("_", " ").title())
            unit_pdf = "€" if is_euro_val else "%" if label_key == 'vat_rate_percent' else ""
            precision_pdf = 1 if label_key == 'vat_rate_percent' else 2
            formatted_value_str_pdf = format_kpi_value(value_cost, unit=unit_pdf, precision=precision_pdf, texts_dict=texts)
            value_style_name = base_style_name
            if result_key in ['total_investment_netto', 'total_investment_brutto', 'subtotal_netto']: value_style_name = 'TableBoldRight'
            elif is_euro_val or unit_pdf == "%": value_style_name = 'TableNumber'
            value_style = STYLES.get(value_style_name, STYLES['TableText'])
            cost_data_pdf.append([Paragraph(str(label_text_pdf), STYLES.get('TableLabel')), Paragraph(str(formatted_value_str_pdf), value_style)])
    return cost_data_pdf

def _prepare_simulation_table_for_pdf(analysis_results: Dict[str, Any], texts: Dict[str, str], num_years_to_show: int = 10) -> List[List[Any]]:
    sim_data_for_pdf_final: List[List[Any]] = []
    header_config_pdf = [
        (get_text(texts,"analysis_table_year_header","Jahr"), None, "", 0, 'TableText'),
        (get_text(texts,"annual_pv_production_kwh","PV Prod."), 'annual_productions_sim', "kWh", 0, 'TableNumber'),
        (get_text(texts,"annual_financial_benefit","Jährl. Vorteil"), 'annual_benefits_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"annual_maintenance_cost_sim","Wartung"), 'annual_maintenance_costs_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"analysis_table_annual_cf_header","Jährl. CF"), 'annual_cash_flows_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"analysis_table_cumulative_cf_header","Kum. CF"), 'cumulative_cash_flows_sim_display', "€", 2, 'TableBoldRight')
    ]
    header_row_pdf = [Paragraph(hc[0], STYLES['TableHeader']) for hc in header_config_pdf]
    sim_data_for_pdf_final.append(header_row_pdf)

    sim_period_eff_pdf = int(analysis_results.get('simulation_period_years_effective', 0))
    if sim_period_eff_pdf == 0: return sim_data_for_pdf_final

    actual_years_to_display_pdf = min(sim_period_eff_pdf, num_years_to_show)
    cumulative_cash_flows_base_sim = analysis_results.get('cumulative_cash_flows_sim', [])
    if cumulative_cash_flows_base_sim and len(cumulative_cash_flows_base_sim) == (sim_period_eff_pdf + 1) :
        analysis_results['cumulative_cash_flows_sim_display'] = cumulative_cash_flows_base_sim[1:]
    else: 
        analysis_results['cumulative_cash_flows_sim_display'] = [None] * sim_period_eff_pdf

    for i_pdf in range(actual_years_to_display_pdf):
        row_items_formatted_pdf = [Paragraph(str(i_pdf + 1), STYLES.get(header_config_pdf[0][4]))]
        for j_pdf, header_conf_item in enumerate(header_config_pdf[1:]):
            result_key_pdf, unit_pdf, precision_pdf, style_name_data_pdf = header_conf_item[1], header_conf_item[2], header_conf_item[3], header_conf_item[4]
            current_list_pdf = analysis_results.get(str(result_key_pdf), [])
            value_to_format_pdf = current_list_pdf[i_pdf] if isinstance(current_list_pdf, list) and i_pdf < len(current_list_pdf) else None
            formatted_str_pdf = format_kpi_value(value_to_format_pdf, unit=unit_pdf, precision=precision_pdf, texts_dict=texts, na_text_key="value_not_available_short_pdf")
            row_items_formatted_pdf.append(Paragraph(str(formatted_str_pdf), STYLES.get(style_name_data_pdf, STYLES['TableText'])))
        sim_data_for_pdf_final.append(row_items_formatted_pdf)

    if sim_period_eff_pdf > num_years_to_show:
        ellipsis_row_pdf = [Paragraph("...", STYLES['TableText']) for _ in header_config_pdf]
        for cell_para_pdf in ellipsis_row_pdf: cell_para_pdf.style.alignment = TA_CENTER
        sim_data_for_pdf_final.append(ellipsis_row_pdf)
    return sim_data_for_pdf_final

def _create_product_table_with_image(details_data_prod: List[List[Any]], product_image_flowables_prod: List[Any], available_width: float) -> List[Any]:
    if not _REPORTLAB_AVAILABLE: return []
    story_elements: List[Any] = []
    if details_data_prod and product_image_flowables_prod:
        text_table_width = available_width * 0.62
        image_cell_width = available_width * 0.35
        text_table = Table(details_data_prod, colWidths=[text_table_width * 0.4, text_table_width * 0.6])
        text_table.setStyle(PRODUCT_TABLE_STYLE)
        image_cell_content = [Spacer(1, 0.1*cm)] + product_image_flowables_prod
        image_frame = KeepInFrame(image_cell_width, 6*cm, image_cell_content)
        combined_table_data = [[text_table, image_frame]]
        combined_table = Table(combined_table_data, colWidths=[text_table_width + 0.03*available_width, image_cell_width])
        combined_table.setStyle(PRODUCT_MAIN_TABLE_STYLE)
        story_elements.append(combined_table)
    elif details_data_prod:
        text_only_table = Table(details_data_prod, colWidths=[available_width * 0.4, available_width * 0.6])
        text_only_table.setStyle(PRODUCT_TABLE_STYLE)
        story_elements.append(text_only_table)
    elif product_image_flowables_prod:
        story_elements.extend(product_image_flowables_prod)
    return story_elements

def _add_product_details_to_story(
    story: List[Any], product_id: Optional[Union[int, float]],
    component_name_text: str, texts: Dict[str,str],
    available_width: float, get_product_by_id_func_param: Callable,
    include_product_images: bool
):
    """
    VERBESSERTE Produktdetails mit korrekten Bezeichnungen und Seitenumbruch-Schutz
    """
    if not _REPORTLAB_AVAILABLE: return
    
    # SEITENUMBRUCH-SCHUTZ: Sammle alle Elemente in einer Liste
    protected_elements: List[Any] = []
    
    product_details: Optional[Dict[str, Any]] = None
    if product_id is not None and callable(get_product_by_id_func_param):
        product_details = get_product_by_id_func_param(product_id)

    if not product_details:
        protected_elements.append(Paragraph(f"{component_name_text}: {get_text(texts,'details_not_available_pdf', 'Details nicht verfügbar')}", STYLES.get('NormalLeft')))
        protected_elements.append(Spacer(1, 0.3*cm))
        
        # SEITENUMBRUCH-SCHUTZ anwenden
        story.append(KeepTogether(protected_elements))
        return

    # VERBESSERTE PRODUKTBEZEICHNUNG
    brand = product_details.get('brand', '').strip()
    model = product_details.get('model_name', '').strip()
    
    # Korrekte Darstellung: "Marke Modell" oder fallback zu ursprünglichem Namen
    if brand and model:
        full_product_name = f"{brand} {model}"
    elif brand:
        full_product_name = brand
    elif model:
        full_product_name = model
    else:
        full_product_name = component_name_text
    
    # Titel mit vollständiger Produktbezeichnung
    protected_elements.append(Paragraph(f"{component_name_text}: {full_product_name}", STYLES.get('ComponentTitle')))
    
    details_data_prod: List[List[Any]] = []

    default_fields_prod = [
        ('brand', 'product_brand'), ('model_name', 'product_model'),
        ('warranty_years', 'product_warranty')
    ]
    component_specific_fields_prod: List[Tuple[str,str]] = []
    cat_lower_prod = str(product_details.get('category', "")).lower()

    if cat_lower_prod == 'modul':
        component_specific_fields_prod = [('capacity_w', 'product_capacity_wp'), ('efficiency_percent', 'product_efficiency'), ('length_m', 'product_length_m'), ('width_m', 'product_width_m'), ('weight_kg', 'product_weight_kg')]
    elif cat_lower_prod == 'wechselrichter':
        component_specific_fields_prod = [('power_kw', 'product_power_kw'), ('efficiency_percent', 'product_efficiency_inverter')]
    elif cat_lower_prod == 'batteriespeicher':
        component_specific_fields_prod = [('storage_power_kw', 'product_capacity_kwh'), ('power_kw', 'product_power_storage_kw'), ('max_cycles', 'product_max_cycles_label')]
    elif cat_lower_prod == 'wallbox':
        component_specific_fields_prod = [('power_kw', 'product_power_wallbox_kw')]
    elif cat_lower_prod == 'energiemanagementsystem': # HINZUGEFÜGT: EMS
        component_specific_fields_prod = [('description', 'product_description_short')] # Beispiel, anpassen!
    elif cat_lower_prod == 'leistungsoptimierer': # HINZUGEFÜGT: Optimierer
        component_specific_fields_prod = [('efficiency_percent', 'product_optimizer_efficiency')] # Beispiel
    elif cat_lower_prod == 'carport': # HINZUGEFÜGT: Carport
        component_specific_fields_prod = [('length_m', 'product_length_m'), ('width_m', 'product_width_m')] # Beispiel
    # Notstrom und Tierabwehr könnten generische Felder wie Beschreibung verwenden oder spezifische, falls vorhanden
    elif cat_lower_prod == 'notstromversorgung':
        component_specific_fields_prod = [('power_kw', 'product_emergency_power_kw')] # Beispiel
    elif cat_lower_prod == 'tierabwehrschutz':
        component_specific_fields_prod = [('description', 'product_description_short')] # Beispiel
    
    all_fields_to_display_prod = default_fields_prod + component_specific_fields_prod
    for key_prod, label_text_key_prod in all_fields_to_display_prod:
        value_prod = product_details.get(key_prod)
        label_prod = get_text(texts, label_text_key_prod, key_prod.replace("_", " ").title())
        
        if value_prod is not None and str(value_prod).strip() != "":
            unit_prod, prec_prod = "", 2
            if key_prod == 'capacity_w': unit_prod, prec_prod = "Wp", 0
            elif key_prod == 'power_kw': unit_prod, prec_prod = "kW", 1 # Für WR, Speicher, Wallbox etc.
            elif key_prod == 'storage_power_kw': unit_prod, prec_prod = "kWh", 1
            elif key_prod.endswith('_percent'): unit_prod, prec_prod = "%", 1
            elif key_prod == 'warranty_years': unit_prod, prec_prod = "Jahre", 0
            elif key_prod == 'max_cycles': unit_prod, prec_prod = "Zyklen", 0
            elif key_prod.endswith('_m'): unit_prod, prec_prod = "m", 3
            elif key_prod == 'weight_kg': unit_prod, prec_prod = "kg", 1
            
            value_str_prod = format_kpi_value(value_prod, unit=unit_prod, precision=prec_prod, texts_dict=texts, na_text_key="value_not_available_short_pdf")
            details_data_prod.append([Paragraph(str(label_prod), STYLES.get('TableLabel')), Paragraph(str(value_str_prod), STYLES.get('TableText'))])

    product_image_flowables_prod: List[Any] = []
    if include_product_images:
        product_image_base64_prod = product_details.get('image_base64')
        if product_image_base64_prod:
            img_w_prod = min(available_width * 0.30, 5*cm); img_h_max_prod = 5*cm
            product_image_flowables_prod = _get_image_flowable(product_image_base64_prod, img_w_prod, texts, None, img_h_max_prod, align='CENTER')
    
    # Tabelle zu geschützten Elementen hinzufügen
    table_elements = _create_product_table_with_image(details_data_prod, product_image_flowables_prod, available_width)
    protected_elements.extend(table_elements)
    
    # Beschreibung hinzufügen
    description_prod_val = product_details.get('description')
    if description_prod_val and str(description_prod_val).strip():
        protected_elements.append(Spacer(1, 0.2*cm))
        protected_elements.append(Paragraph(f"<i>{str(description_prod_val).strip()}</i>", STYLES.get('TableTextSmall')))
    
    protected_elements.append(Spacer(1, 0.5*cm))

    # SEITENUMBRUCH-SCHUTZ: Gesamtes Produktmodul zusammenhalten
    story.append(KeepTogether(protected_elements))


def generate_offer_pdf(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    sections_to_include: Optional[List[str]],
    inclusion_options: Dict[str, Any],
    load_admin_setting_func: Callable, 
    save_admin_setting_func: Callable, 
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    active_company_id: Optional[int],
    texts: Dict[str, str],
    use_modern_design: bool = True,
    **kwargs
) -> Optional[bytes]:
    """
    Erzeugt ein PDF-Angebot für Photovoltaik-Projekte.
    
    Args:
        project_data: Projektdaten mit Kunden- und Komponenteninformationen
        analysis_results: Ergebnisse der Wirtschaftlichkeitsanalyse
        company_info: Firmeninformationen
        company_logo_base64: Base64-kodiertes Firmenlogo
        selected_title_image_b64: Base64-kodiertes Titelbild
        selected_offer_title_text: Titel des Angebots
        selected_cover_letter_text: Anschreiben-Text
        sections_to_include: Liste der einzuschließenden Sektionen
        inclusion_options: Optionen für zusätzliche Inhalte
        load_admin_setting_func: Funktion zum Laden von Admin-Einstellungen
        save_admin_setting_func: Funktion zum Speichern von Admin-Einstellungen
        list_products_func: Funktion zum Auflisten von Produkten
        get_product_by_id_func: Funktion zum Abrufen von Produkten nach ID
        db_list_company_documents_func: Funktion zum Abrufen von Firmendokumenten
        active_company_id: ID der aktiven Firma
        texts: Übersetzungstexte
        use_modern_design: Ob modernes Design verwendet werden soll
        **kwargs: Zusätzliche Parameter
        
    Returns:
        PDF-Bytes oder None bei Fehlern
    """
    
    if not _REPORTLAB_AVAILABLE:
        print("⚠️ ReportLab nicht verfügbar - kann kein PDF erstellen")
        return _create_no_data_fallback_pdf(texts, project_data.get('customer_data', {}) if project_data else {})
   
    # DATENVALIDIERUNG: Prüfe Verfügbarkeit der erforderlichen Daten
    validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
    
    # Wenn kritische Daten fehlen, erstelle Fallback-PDF
    if not validation_result['is_valid']:
        print(f"⚠️ PDF-Erstellung: Kritische Daten fehlen: {', '.join(validation_result['critical_errors'])}")
        customer_data = project_data.get('customer_data', {}) if project_data else {}
        return _create_no_data_fallback_pdf(texts, customer_data)
    
    # Warnungen ausgeben, wenn Daten unvollständig sind
    if validation_result['warnings']:
        print(f"⚠️ PDF-Erstellung: Daten unvollständig: {', '.join(validation_result['missing_data_summary'])}")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")
    
    try:
        # Design-Einstellungen laden
        design_settings = load_admin_setting_func('pdf_design_settings', {
            'primary_color': PRIMARY_COLOR_HEX, 
            'secondary_color': SECONDARY_COLOR_HEX
        })
        if isinstance(design_settings, dict):
            _update_styles_with_dynamic_colors(design_settings)
        
        # PDF-Konfiguration
        buffer = BytesIO()
        offer_number = _get_next_offer_number(texts, load_admin_setting_func, save_admin_setting_func)
        
        # Angebotsnummer optional aus inclusion_options überschreiben
        if inclusion_options.get('custom_offer_number'):
            offer_number = inclusion_options['custom_offer_number']
        
        # PDF-Dokument erstellen
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=pagesizes.A4,
            topMargin=2*cm, 
            bottomMargin=2*cm, 
            leftMargin=2*cm, 
            rightMargin=2*cm
        )
        
        # Story-Elemente sammeln
        story = []
        
        # Deckblatt
        story.extend(_create_cover_page(
            project_data, company_info, company_logo_base64, 
            selected_title_image_b64, selected_offer_title_text,
            selected_cover_letter_text, offer_number, texts
        ))
        
        # Seitenumbruch nach Deckblatt
        story.append(PageBreak())
        
        # Inhaltssektionen
        if sections_to_include:
            if 'project_overview' in sections_to_include:
                story.extend(_create_project_overview_section(project_data, texts))
            
            if 'components' in sections_to_include and project_data:
                story.extend(_create_components_section(
                    project_data, list_products_func, get_product_by_id_func, texts
                ))
            
            if 'analysis' in sections_to_include and analysis_results:
                story.extend(_create_analysis_section(analysis_results, texts))
            
            if 'costs' in sections_to_include and analysis_results:
                story.extend(_create_costs_section(analysis_results, texts))
            
            if 'financing' in sections_to_include and analysis_results:
                story.extend(_create_financing_section(analysis_results, texts))
        
        # Footer-Informationen
        story.extend(_create_footer_section(company_info, texts))
        
        # PDF erstellen
        doc.build(story)
        main_pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Anhänge hinzufügen, falls gewünscht
        if inclusion_options.get('include_all_documents') and _PYPDF_AVAILABLE:
            return _append_additional_documents(
                main_pdf_bytes, inclusion_options, project_data,
                get_product_by_id_func, db_list_company_documents_func,
                active_company_id
            )
        
        return main_pdf_bytes
        
    except Exception as e:
        print(f"❌ Fehler bei PDF-Erstellung: {e}")
        traceback.print_exc()
        # Fallback-PDF erstellen
        customer_data = project_data.get('customer_data', {}) if project_data else {}

def _create_cover_page(
    project_data: Dict[str, Any], 
    company_info: Dict[str, Any], 
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    offer_number: str,
    texts: Dict[str, str]
) -> List[Any]:
    """Erstellt das Deckblatt für das PDF"""
    elements = []
    
    # Titel
    elements.append(Paragraph(selected_offer_title_text, STYLES.get('OfferTitle')))
    elements.append(Spacer(1, 1*cm))
    
    # Angebotsnummer
    elements.append(Paragraph(
        f"{get_text(texts, 'offer_number', 'Angebots-Nr.')}: {offer_number}",
        STYLES.get('SectionTitle')
    ))
    elements.append(Spacer(1, 1*cm))
    
    # Firmenlogo falls vorhanden
    if company_logo_base64:
        try:
            logo_image = _get_image_flowable(company_logo_base64, 4*cm, texts)
            if logo_image:
                elements.extend(logo_image)
                elements.append(Spacer(1, 1*cm))
        except Exception:
            pass
    
    # Firmeninformationen
    company_text = f"""
    <b>{company_info.get('name', '')}</b><br/>
    {company_info.get('street', '')}<br/>
    {company_info.get('zip_code', '')} {company_info.get('city', '')}<br/>
    """
    elements.append(Paragraph(company_text, STYLES.get('NormalCenter')))
    elements.append(Spacer(1, 2*cm))
    
    # Kundendaten falls verfügbar
    if project_data and project_data.get('customer_data'):
        customer = project_data['customer_data']
        customer_text = f"""
        <b>{get_text(texts, 'customer_info', 'Kunde')}:</b><br/>
        {customer.get('first_name', '')} {customer.get('last_name', '')}<br/>
        {customer.get('street', '')}<br/>
        {customer.get('zip_code', '')} {customer.get('city', '')}
        """
        elements.append(Paragraph(customer_text, STYLES.get('NormalLeft')))
    
    return elements


def _create_project_overview_section(project_data: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Projektübersicht"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'project_overview_title', 'Projektübersicht'),
        STYLES.get('SectionTitle')
    ))
    
    if project_data and project_data.get('project_details'):
        details = project_data['project_details']
        
        # Grunddaten
        data = []
        if details.get('module_quantity'):
            data.append([
                get_text(texts, 'module_count', 'Anzahl Module'),
                str(details['module_quantity'])
            ])
        
        if details.get('peak_power'):
            data.append([
                get_text(texts, 'peak_power', 'Spitzenleistung'),
                f"{details['peak_power']} kWp"
            ])
        
        if data:
            table = Table(data)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(table)
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_components_section(
    project_data: Dict[str, Any], 
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    texts: Dict[str, str]
) -> List[Any]:
    """Erstellt die Komponenten-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'components_title', 'Systemkomponenten'),
        STYLES.get('SectionTitle')
    ))
    
    if project_data and project_data.get('project_details'):
        details = project_data['project_details']
        
        # Module
        if details.get('selected_module_id'):
            try:
                module = get_product_by_id_func(details['selected_module_id'])
                if module:
                    elements.append(Paragraph(
                        f"<b>{get_text(texts, 'solar_module', 'Solarmodul')}:</b> {module.get('model_name', 'Unbekannt')}",
                        STYLES.get('NormalLeft')
                    ))
            except Exception:
                pass
        
        # Wechselrichter
        if details.get('selected_inverter_id'):
            try:
                inverter = get_product_by_id_func(details['selected_inverter_id'])
                if inverter:
                    elements.append(Paragraph(
                        f"<b>{get_text(texts, 'inverter', 'Wechselrichter')}:</b> {inverter.get('model_name', 'Unbekannt')}",
                        STYLES.get('NormalLeft')
                    ))
            except Exception:
                pass
        
        # Speicher
        if details.get('include_storage') and details.get('selected_storage_id'):
            try:
                storage = get_product_by_id_func(details['selected_storage_id'])
                if storage:
                    elements.append(Paragraph(
                        f"<b>{get_text(texts, 'battery_storage', 'Batteriespeicher')}:</b> {storage.get('model_name', 'Unbekannt')}",
                        STYLES.get('NormalLeft')
                    ))
            except Exception:
                pass
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_analysis_section(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Analyse-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'analysis_title', 'Wirtschaftlichkeitsanalyse'),
        STYLES.get('SectionTitle')
    ))
    
    # Wirtschaftlichkeits-KPIs
    data = []
    
    if analysis_results.get('annual_yield_kwh'):
        data.append([
            get_text(texts, 'annual_yield', 'Jährlicher Ertrag'),
            f"{analysis_results['annual_yield_kwh']:,.0f} kWh".replace(',', '.')
        ])
    
    if analysis_results.get('autarkie_grad_percent'):
        data.append([
            get_text(texts, 'self_sufficiency', 'Autarkiegrad'),
            f"{analysis_results['autarkie_grad_percent']:.1f}%"
        ])
    
    if analysis_results.get('eigenverbrauch_percent'):
        data.append([
            get_text(texts, 'self_consumption', 'Eigenverbrauch'),
            f"{analysis_results['eigenverbrauch_percent']:.1f}%"
        ])
    
    if analysis_results.get('payback_years'):
        data.append([
            get_text(texts, 'payback_period', 'Amortisationszeit'),
            f"{analysis_results['payback_years']:.1f} Jahre"
        ])
    
    if data:
        table = Table(data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table)
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_costs_section(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Kosten-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'costs_title', 'Kostenübersicht'),
        STYLES.get('SectionTitle')
    ))
    
    data = []
    
    # Investitionskosten
    if analysis_results.get('total_investment_cost'):
        data.append([
            get_text(texts, 'investment_cost', 'Investitionskosten'),
            f"{analysis_results['total_investment_cost']:,.2f} €".replace(',', '.')
        ])
    
    # Jährliche Einsparungen
    if analysis_results.get('annual_savings'):
        data.append([
            get_text(texts, 'annual_savings', 'Jährliche Einsparungen'),
            f"{analysis_results['annual_savings']:,.2f} €".replace(',', '.')
        ])
    
    # 20-Jahre Gewinn
    if analysis_results.get('total_profit_20_years'):
        data.append([
            get_text(texts, 'total_profit_20y', 'Gewinn nach 20 Jahren'),
            f"{analysis_results['total_profit_20_years']:,.2f} €".replace(',', '.')
        ])
    
    if data:
        table = Table(data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table)
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_financing_section(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Finanzierungs-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'financing_title', 'Finanzierungsmöglichkeiten'),
        STYLES.get('SectionTitle')
    ))
    
    elements.append(Paragraph(
        get_text(texts, 'financing_info', 'Sprechen Sie uns auf individuelle Finanzierungslösungen an.'),
        STYLES.get('NormalLeft')
    ))
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_footer_section(company_info: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt den Footer-Bereich"""
    elements = []
    
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph(
        get_text(texts, 'contact_info', 'Kontaktinformationen'),
        STYLES.get('SectionTitle')
    ))
    
    contact_text = f"""
    <b>{company_info.get('name', '')}</b><br/>
    {company_info.get('street', '')}<br/>
    {company_info.get('zip_code', '')} {company_info.get('city', '')}<br/>
    """
    
    if company_info.get('phone'):
        contact_text += f"Tel.: {company_info['phone']}<br/>"
    
    if company_info.get('email'):
        contact_text += f"E-Mail: {company_info['email']}<br/>"
    
    elements.append(Paragraph(contact_text, STYLES.get('NormalLeft')))
    
    return elements


def _append_additional_documents(
    main_pdf_bytes: bytes,
    inclusion_options: Dict[str, Any],
    project_data: Dict[str, Any],
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int]
) -> bytes:
    """Fügt zusätzliche Dokumente an das Haupt-PDF an"""
    
    if not _PYPDF_AVAILABLE:
        return main_pdf_bytes
    
    try:
        pdf_writer = PdfWriter()
        
        # Haupt-PDF hinzufügen
        main_reader = PdfReader(BytesIO(main_pdf_bytes))
        for page in main_reader.pages:
            pdf_writer.add_page(page)
        
        # Produktdatenblätter hinzufügen
        if project_data and project_data.get('project_details'):
            details = project_data['project_details']
            product_ids = []
            
            for key in ['selected_module_id', 'selected_inverter_id', 'selected_storage_id']:
                if details.get(key):
                    product_ids.append(details[key])
            
            for product_id in product_ids:
                try:
                    product = get_product_by_id_func(product_id)
                    if product and product.get('datasheet_link_db_path'):
                        datasheet_path = os.path.join(
                            PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, 
                            product['datasheet_link_db_path']
                        )
                        if os.path.exists(datasheet_path):
                            datasheet_reader = PdfReader(datasheet_path)
                            for page in datasheet_reader.pages:
                                pdf_writer.add_page(page)
                except Exception:
                    pass
        
        # Firmendokumente hinzufügen
        if (inclusion_options.get('company_document_ids_to_include') and 
            active_company_id and callable(db_list_company_documents_func)):
            
            try:
                company_docs = db_list_company_documents_func(active_company_id, None)
                for doc_info in company_docs:
                    if doc_info.get('id') in inclusion_options['company_document_ids_to_include']:
                        if doc_info.get('relative_db_path'):
                            doc_path = os.path.join(
                                COMPANY_DOCS_BASE_DIR_PDF_GEN,
                                doc_info['relative_db_path']
                            )
                            if os.path.exists(doc_path):
                                doc_reader = PdfReader(doc_path)
                                for page in doc_reader.pages:
                                    pdf_writer.add_page(page)
            except Exception:
                pass
        
        # Zusammengebautes PDF zurückgeben
        final_buffer = BytesIO()
        pdf_writer.write(final_buffer)
        final_pdf_bytes = final_buffer.getvalue()
        final_buffer.close()
        
        return final_pdf_bytes
        
    except Exception:
        # Bei Fehlern das Original-PDF zurückgeben
        return main_pdf_bytes


def _validate_pdf_data_availability(
    project_data: Dict[str, Any], 
    analysis_results: Dict[str, Any], 
    texts: Dict[str, str]
) -> Dict[str, Any]:
    """
    Validiert die verfügbaren Daten für die PDF-Erstellung.
    
    Returns:
        Dict mit is_valid, warnings, critical_errors, missing_data_summary
    """
    
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'critical_errors': [],
        'missing_data_summary': []
    }
    
    # Kritische Prüfungen (führen zu is_valid=False)
    if not texts or not isinstance(texts, dict):
        validation_result['critical_errors'].append('Keine Texte verfügbar')
        validation_result['is_valid'] = False
    
    # Warnungen (führen nicht zu is_valid=False)
    if not project_data or not isinstance(project_data, dict):
        validation_result['warnings'].append('Keine Projektdaten verfügbar')
        validation_result['missing_data_summary'].append('Projektdaten')
    else:
        if not project_data.get('customer_data', {}).get('last_name'):
            validation_result['warnings'].append('Kein Kundenname verfügbar')
            validation_result['missing_data_summary'].append('Kundendaten')
        
        if not project_data.get('project_details', {}).get('module_quantity'):
            validation_result['warnings'].append('Keine Modulanzahl verfügbar')
            validation_result['missing_data_summary'].append('Komponentendaten')
    
    if not analysis_results or not isinstance(analysis_results, dict):
        validation_result['warnings'].append('Keine Analyseergebnisse verfügbar')
        validation_result['missing_data_summary'].append('Wirtschaftlichkeitsdaten')
    
    return validation_result


def _create_no_data_fallback_pdf(texts: Dict[str, str], customer_data: Dict[str, Any] = None) -> bytes:
    """
    Erstellt ein Fallback-PDF wenn nicht genügend Daten vorhanden sind.
    
    Args:
        texts: Text-Dictionary
        customer_data: Optionale Kundendaten
        
    Returns:
        PDF-Bytes
    """
    
    if not _REPORTLAB_AVAILABLE:
        # Text-basiertes Fallback
        return b"PDF-Erstellung nicht verfuegbar. ReportLab nicht installiert."
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    title = get_text(texts, 'pdf_no_data_title', 'Photovoltaik-Angebot - Daten unvollständig')
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 1*cm))
    
    # Kundenanrede falls verfügbar
    if customer_data and customer_data.get('last_name'):
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        customer_text = get_text(texts, 'pdf_no_data_customer', f'Für: {customer_name}')
        story.append(Paragraph(customer_text, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # Haupttext
    main_text = get_text(texts, 'pdf_no_data_message', 
        '''Liebe Kundin, lieber Kunde,

        für die Erstellung Ihres individuellen Photovoltaik-Angebots benötigen wir noch einige wichtige Informationen:

        <b>Erforderliche Daten:</b>
        • Gewünschte PV-Module und Komponenten
        • Technische Angaben zu Ihrem Dach/Standort
        • Verbrauchsdaten für die Wirtschaftlichkeitsberechnung

        <b>Nächste Schritte:</b>
        1. Vervollständigen Sie die Komponentenauswahl
        2. Führen Sie die Wirtschaftlichkeitsberechnung durch
        3. Erstellen Sie das finale Angebot

        Vielen Dank für Ihr Verständnis.''')
    
    story.append(Paragraph(main_text, styles['Normal']))
    story.append(Spacer(1, 1*cm))
    
    # Kontaktinformationen
    contact_text = get_text(texts, 'pdf_no_data_contact', 
        'Kontakt: Bitte wenden Sie sich an unser Beratungsteam für weitere Unterstützung.')
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
    pv_details_pdf = current_project_data_pdf.get("project_details", {})
    available_width_content = doc.width

    # --- Deckblatt ---
    try:
        if selected_title_image_b64:
            img_flowables_title = _get_image_flowable(selected_title_image_b64, doc.width, texts, max_height=doc.height / 1.8, align='CENTER')
            if img_flowables_title: story.extend(img_flowables_title); story.append(Spacer(1, 0.5 * cm))

        if include_company_logo_opt and company_logo_base64:
            logo_flowables_deckblatt = _get_image_flowable(company_logo_base64, 6*cm, texts, max_height=3*cm, align='CENTER')
            if logo_flowables_deckblatt: story.extend(logo_flowables_deckblatt); story.append(Spacer(1, 0.5 * cm))

        offer_title_processed_pdf = _replace_placeholders(selected_offer_title_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
        story.append(Paragraph(offer_title_processed_pdf, STYLES.get('OfferTitle')))
        
        company_info_html_pdf = "<br/>".join(filter(None, [
            f"<b>{company_info.get('name', '')}</b>", company_info.get("street", ""),
            f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip(),
            (f"{get_text(texts, 'pdf_phone_label_short', 'Tel.')}: {company_info.get('phone', '')}" if company_info.get('phone') else None),
            (f"{get_text(texts, 'pdf_email_label_short', 'Mail')}: {company_info.get('email', '')}" if company_info.get('email') else None),
            (f"{get_text(texts, 'pdf_website_label_short', 'Web')}: {company_info.get('website', '')}" if company_info.get('website') else None),
            (f"{get_text(texts, 'pdf_taxid_label', 'StNr/USt-ID')}: {company_info.get('tax_id', '')}" if company_info.get('tax_id') else None),
        ]))
        story.append(Paragraph(company_info_html_pdf, STYLES.get('CompanyInfoDeckblatt')))
          # KORRIGIERTES 4-ZEILEN-FORMAT wie gewünscht:
        # [Anrede] [Titel]
        # [Nachname] [Vorname]  
        # [Strasse] [Hausnummer]
        # [Postleitzahl] [Ort]
        line1 = f"{customer_pdf.get('salutation','')} {customer_pdf.get('title','')}".strip()
        line2 = f"{customer_pdf.get('last_name','')} {customer_pdf.get('first_name','')}".strip()
        line3 = f"{customer_pdf.get('address','')} {customer_pdf.get('house_number','')}".strip()
        line4 = f"{customer_pdf.get('zip_code','')} {customer_pdf.get('city','')}".strip()
        
        customer_address_block_pdf_lines = [line1, line2, line3, line4]
        # Firmenname falls vorhanden zusätzlich einfügen
        if customer_pdf.get("company_name"):
            customer_address_block_pdf_lines.insert(1, str(customer_pdf.get("company_name")))
            
        customer_address_block_pdf = "<br/>".join(filter(None, customer_address_block_pdf_lines))
        story.append(Paragraph(customer_address_block_pdf, STYLES.get("CustomerAddress")))
        
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"{get_text(texts, 'pdf_offer_number_label', 'Angebotsnummer')}: <b>{offer_number_final}</b>", STYLES.get('NormalRight')))
        story.append(Paragraph(f"{get_text(texts, 'pdf_offer_date_label', 'Datum')}: {datetime.now().strftime('%d.%m.%Y')}", STYLES.get('NormalRight')))
        story.append(PageBreak())
    except Exception as e_cover:
        story.append(Paragraph(f"Fehler bei Erstellung des Deckblatts: {e_cover}", STYLES.get('NormalLeft')))
        story.append(PageBreak())

    # --- Anschreiben ---
    try:
        story.append(SetCurrentChapterTitle(get_text(texts, "pdf_chapter_title_cover_letter", "Anschreiben")))
        company_sender_address_lines = [company_info.get("name", ""), company_info.get("street", ""), f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip()]
        story.append(Paragraph("<br/>".join(filter(None,company_sender_address_lines)), STYLES.get('NormalLeft'))) 
        story.append(Spacer(1, 1.5*cm))
        story.append(Paragraph(customer_address_block_pdf, STYLES.get('NormalLeft')))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(datetime.now().strftime('%d.%m.%Y'), STYLES.get('NormalRight')))
        story.append(Spacer(1, 0.5*cm))
        offer_subject_text = get_text(texts, "pdf_offer_subject_line_param", "Ihr persönliches Angebot für eine Photovoltaikanlage, Nr. {offer_number}").format(offer_number=offer_number_final)
        story.append(Paragraph(f"<b>{offer_subject_text}</b>", STYLES.get('NormalLeft')))
        story.append(Spacer(1, 0.5*cm))

        cover_letter_processed_pdf = _replace_placeholders(selected_cover_letter_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
        cover_letter_paragraphs = cover_letter_processed_pdf.split('\n') 
        for para_text in cover_letter_paragraphs:
            if para_text.strip(): 
                story.append(Paragraph(para_text.replace('\r',''), STYLES.get('CoverLetter'))) 
            else: 
                story.append(Spacer(1, 0.2*cm)) 
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(get_text(texts, "pdf_closing_greeting", "Mit freundlichen Grüßen"), STYLES.get('NormalLeft')))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(str(company_info.get("name", "")), STYLES.get('NormalLeft')))
        story.append(PageBreak())
    except Exception as e_letter:
        story.append(Paragraph(f"Fehler bei Erstellung des Anschreibens: {e_letter}", STYLES.get('NormalLeft')))
        story.append(PageBreak())    # --- Dynamische Sektionen ---
    active_sections_set_pdf = set(sections_to_include or [])
    
    section_chapter_titles_map = {
        "ProjectOverview": get_text(texts, "pdf_chapter_title_overview", "Projektübersicht"),
        "TechnicalComponents": get_text(texts, "pdf_chapter_title_components", "Komponenten"),
        "CostDetails": get_text(texts, "pdf_chapter_title_cost_details", "Kosten"),
        "Economics": get_text(texts, "pdf_chapter_title_economics", "Wirtschaftlichkeit"),
        "SimulationDetails": get_text(texts, "pdf_chapter_title_simulation", "Simulation"),
        "CO2Savings": get_text(texts, "pdf_chapter_title_co2", "CO₂-Einsparung"),
        "Visualizations": get_text(texts, "pdf_chapter_title_visualizations", "Visualisierungen"),
        "FutureAspects": get_text(texts, "pdf_chapter_title_future_aspects", "Zukunftsaspekte"),
        
        # NEUE OPTIONALE SEITENVORLAGEN (5+ wie gewünscht)
        "CompanyProfile": get_text(texts, "pdf_chapter_title_company_profile", "Unternehmensprofil"),
        "Certifications": get_text(texts, "pdf_chapter_title_certifications", "Zertifizierungen & Qualität"),
        "References": get_text(texts, "pdf_chapter_title_references", "Referenzen & Kundenstimmen"), 
        "Installation": get_text(texts, "pdf_chapter_title_installation", "Installation & Montage"),
        "Maintenance": get_text(texts, "pdf_chapter_title_maintenance", "Wartung & Service"),        "Financing": get_text(texts, "pdf_chapter_title_financing", "Finanzierungsmöglichkeiten"),
        "Insurance": get_text(texts, "pdf_chapter_title_insurance", "Versicherungsschutz"),
        "Warranty": get_text(texts, "pdf_chapter_title_warranty", "Garantie & Gewährleistung")
    }
    
    ordered_section_definitions_pdf = [
        ("ProjectOverview", "pdf_section_title_overview", "1. Projektübersicht & Eckdaten"),
        ("TechnicalComponents", "pdf_section_title_components", "2. Angebotene Systemkomponenten"),
        ("CostDetails", "pdf_section_title_cost_details", "3. Detaillierte Kostenaufstellung"),
        ("Economics", "pdf_section_title_economics", "4. Wirtschaftlichkeit im Überblick"),
        ("SimulationDetails", "pdf_section_title_simulation", "5. Simulationsübersicht (Auszug)"),
        ("CO2Savings", "pdf_section_title_co2", "6. Ihre CO₂-Einsparung"),
        ("Visualizations", "pdf_section_title_visualizations", "7. Grafische Auswertungen"),
        ("FutureAspects", "pdf_chapter_title_future_aspects", "8. Zukunftsaspekte & Erweiterungen"),
        
        # NEUE OPTIONALE SEITENVORLAGEN (individuell gestaltbar)
        ("CompanyProfile", "pdf_section_title_company_profile", "9. Unser Unternehmen"),
        ("Certifications", "pdf_section_title_certifications", "10. Zertifizierungen & Qualitätsstandards"),
        ("References", "pdf_section_title_references", "11. Referenzen & Kundenerfahrungen"),
        ("Installation", "pdf_section_title_installation", "12. Professionelle Installation"),
        ("Maintenance", "pdf_section_title_maintenance", "13. Wartung & Langzeitservice"),
        ("Financing", "pdf_section_title_financing", "14. Flexible Finanzierungslösungen"),
        ("Insurance", "pdf_section_title_insurance", "15. Umfassender Versicherungsschutz"),        ("Warranty", "pdf_section_title_warranty", "16. Herstellergarantie & Gewährleistung")
    ]
    current_section_counter_pdf = 1
    for section_key_current, title_text_key_current, default_title_current in ordered_section_definitions_pdf:
        if section_key_current in active_sections_set_pdf:
            try:
                chapter_title_for_header_current = section_chapter_titles_map.get(section_key_current, default_title_current.split('. ',1)[-1] if '. ' in default_title_current else default_title_current)
                story.append(SetCurrentChapterTitle(chapter_title_for_header_current))
                numbered_title_current = f"{current_section_counter_pdf}. {get_text(texts, title_text_key_current, default_title_current.split('. ',1)[-1] if '. ' in default_title_current else default_title_current)}"
                story.append(Paragraph(numbered_title_current, STYLES.get('SectionTitle')))
                story.append(Spacer(1, 0.2 * cm))

                if section_key_current == "ProjectOverview":
                    if pv_details_pdf.get('visualize_roof_in_pdf_satellite', False) and pv_details_pdf.get('satellite_image_base64_data'):
                        story.append(Paragraph(get_text(texts,"satellite_image_header_pdf","Satellitenansicht Objekt"), STYLES.get('SubSectionTitle')))
                        sat_img_flowables = _get_image_flowable(pv_details_pdf['satellite_image_base64_data'], available_width_content * 0.8, texts, caption_text_key="satellite_image_caption_pdf", max_height=10*cm)
                        if sat_img_flowables: story.extend(sat_img_flowables); story.append(Spacer(1, 0.5*cm))
                    
                    overview_data_content_pdf = [
                        [get_text(texts,"anlage_size_label_pdf", "Anlagengröße"),format_kpi_value(current_analysis_results_pdf.get('anlage_kwp'),"kWp",texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                        [get_text(texts,"module_quantity_label_pdf","Anzahl Module"),str(pv_details_pdf.get('module_quantity', get_text(texts, "value_not_available_short_pdf")))],
                        [get_text(texts,"annual_pv_production_kwh_pdf", "Jährliche PV-Produktion (ca.)"),format_kpi_value(current_analysis_results_pdf.get('annual_pv_production_kwh'),"kWh",precision=0,texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                        [get_text(texts,"self_supply_rate_percent_pdf", "Autarkiegrad (ca.)"),format_kpi_value(current_analysis_results_pdf.get('self_supply_rate_percent'),"%",precision=1,texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                    ]
                    if pv_details_pdf.get('include_storage'):
                         overview_data_content_pdf.extend([[get_text(texts,"selected_storage_capacity_label_pdf", "Speicherkapazität"),format_kpi_value(pv_details_pdf.get('selected_storage_storage_power_kw'),"kWh",texts_dict=texts, na_text_key="value_not_available_short_pdf")]])
                    if overview_data_content_pdf:
                        overview_table_data_styled_content_pdf = [[Paragraph(str(cell[0]),STYLES.get('TableLabel')),Paragraph(str(cell[1]),STYLES.get('TableText'))] for cell in overview_data_content_pdf]
                        overview_table_content_pdf = Table(overview_table_data_styled_content_pdf,colWidths=[available_width_content*0.5,available_width_content*0.5])
                        overview_table_content_pdf.setStyle(TABLE_STYLE_DEFAULT)
                        
                        # SEITENUMBRUCH-SCHUTZ für Übersichtstabelle
                        story.append(KeepTogether([overview_table_content_pdf]))

                elif section_key_current == "TechnicalComponents":
                    story.append(Paragraph(get_text(texts, "pdf_components_intro", "Nachfolgend die Details zu den Kernkomponenten Ihrer Anlage:"), STYLES.get('NormalLeft')))
                    story.append(Spacer(1, 0.3*cm))
                    
                    main_components = [
                        (pv_details_pdf.get("selected_module_id"), get_text(texts, "pdf_component_module_title", "PV-Module")),
                        (pv_details_pdf.get("selected_inverter_id"), get_text(texts, "pdf_component_inverter_title", "Wechselrichter")),
                    ]
                    if pv_details_pdf.get("include_storage"):
                        main_components.append((pv_details_pdf.get("selected_storage_id"), get_text(texts, "pdf_component_storage_title", "Batteriespeicher")))
                    
                    for comp_id, comp_title in main_components:
                        if comp_id: _add_product_details_to_story(story, comp_id, comp_title, texts, available_width_content, get_product_by_id_func, include_product_images_opt)

                    # ERWEITERUNG: Optionale Komponenten / Zubehör
                    if pv_details_pdf.get('include_additional_components', False) and include_optional_component_details_opt:
                        story.append(Paragraph(get_text(texts, "pdf_additional_components_header_pdf", "Optionale Komponenten"), STYLES.get('SubSectionTitle')))
                        optional_comps_map = {
                            'selected_wallbox_id': get_text(texts, "pdf_component_wallbox_title", "Wallbox"),
                            'selected_ems_id': get_text(texts, "pdf_component_ems_title", "Energiemanagementsystem"),
                            'selected_optimizer_id': get_text(texts, "pdf_component_optimizer_title", "Leistungsoptimierer"),
                            'selected_carport_id': get_text(texts, "pdf_component_carport_title", "Solarcarport"),
                            'selected_notstrom_id': get_text(texts, "pdf_component_emergency_power_title", "Notstromversorgung"),
                            'selected_tierabwehr_id': get_text(texts, "pdf_component_animal_defense_title", "Tierabwehrschutz")
                        }
                        any_optional_component_rendered = False
                        for key, title in optional_comps_map.items():
                            opt_comp_id = pv_details_pdf.get(key)
                            if opt_comp_id: 
                                _add_product_details_to_story(story, opt_comp_id, title, texts, available_width_content, get_product_by_id_func, include_product_images_opt)
                                any_optional_component_rendered = True
                        if not any_optional_component_rendered:
                            story.append(Paragraph(get_text(texts, "pdf_no_optional_components_selected_for_details", "Keine optionalen Komponenten für Detailanzeige ausgewählt."), STYLES.get('NormalLeft')))
                        
                elif section_key_current == "CostDetails":
                    cost_table_data_final_pdf = _prepare_cost_table_for_pdf(current_analysis_results_pdf, texts)
                    if cost_table_data_final_pdf:
                        cost_table_obj_final_pdf = Table(cost_table_data_final_pdf, colWidths=[available_width_content*0.6, available_width_content*0.4])
                        cost_table_obj_final_pdf.setStyle(TABLE_STYLE_DEFAULT)
                        
                        # SEITENUMBRUCH-SCHUTZ für Kostentabelle
                        cost_elements = [cost_table_obj_final_pdf]
                        
                        if current_analysis_results_pdf.get('base_matrix_price_netto', 0.0) == 0 and current_analysis_results_pdf.get('cost_storage_aufpreis_product_db_netto', 0.0) > 0: 
                            cost_elements.extend([Spacer(1,0.2*cm), Paragraph(get_text(texts, "analysis_storage_cost_note_single_price_pdf", "<i>Hinweis: Speicherkosten als Einzelposten, da kein Matrix-Pauschalpreis.</i>"), STYLES.get('TableTextSmall'))])
                        elif current_analysis_results_pdf.get('base_matrix_price_netto', 0.0) > 0 and current_analysis_results_pdf.get('cost_storage_aufpreis_product_db_netto', 0.0) > 0:
                            cost_elements.extend([Spacer(1,0.2*cm), Paragraph(get_text(texts, "analysis_storage_cost_note_matrix_pdf", "<i>Hinweis: Speicherkosten als Aufpreis, da Matrixpreis 'Ohne Speicher' verwendet wurde.</i>"), STYLES.get('TableTextSmall'))])
                        
                        story.append(KeepTogether(cost_elements))

                elif section_key_current == "Economics":
                    eco_kpi_data_for_pdf_table = [
                        [get_text(texts, "total_investment_brutto_pdf", "Gesamtinvestition (Brutto)"), format_kpi_value(current_analysis_results_pdf.get('total_investment_brutto'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "annual_financial_benefit_pdf", "Finanzieller Vorteil (Jahr 1, ca.)"), format_kpi_value(current_analysis_results_pdf.get('annual_financial_benefit_year1'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "amortization_time_years_pdf", "Amortisationszeit (ca.)"), format_kpi_value(current_analysis_results_pdf.get('amortization_time_years'), "Jahre", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "simple_roi_percent_label_pdf", "Einfache Rendite (Jahr 1, ca.)"), format_kpi_value(current_analysis_results_pdf.get('simple_roi_percent'), "%", precision=1, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "lcoe_euro_per_kwh_label_pdf", "Stromgestehungskosten (LCOE, ca.)"), format_kpi_value(current_analysis_results_pdf.get('lcoe_euro_per_kwh'), "€/kWh", precision=3, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "npv_over_years_pdf", "Kapitalwert über Laufzeit (NPV, ca.)"), format_kpi_value(current_analysis_results_pdf.get('npv_value'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "irr_percent_pdf", "Interner Zinsfuß (IRR, ca.)"), format_kpi_value(current_analysis_results_pdf.get('irr_percent'), "%", precision=1, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")]                    ]
                    if eco_kpi_data_for_pdf_table:
                        eco_kpi_table_styled_content = [[Paragraph(str(cell[0]), STYLES.get('TableLabel')), Paragraph(str(cell[1]), STYLES.get('TableNumber'))] for cell in eco_kpi_data_for_pdf_table]
                        eco_table_object = Table(eco_kpi_table_styled_content, colWidths=[available_width_content*0.6, available_width_content*0.4])
                        eco_table_object.setStyle(TABLE_STYLE_DEFAULT)
                          # SEITENUMBRUCH-SCHUTZ für Wirtschaftlichkeitstabelle
                        story.append(KeepTogether([eco_table_object]))
                        
                elif section_key_current == "SimulationDetails":
                    sim_table_data_content_pdf = _prepare_simulation_table_for_pdf(current_analysis_results_pdf, texts, num_years_to_show=10)
                    if len(sim_table_data_content_pdf) > 1:
                        sim_table_obj_final_pdf = Table(sim_table_data_content_pdf, colWidths=None)
                        sim_table_obj_final_pdf.setStyle(DATA_TABLE_STYLE)
                        
                        # SEITENUMBRUCH-SCHUTZ für Simulationstabelle
                        story.append(KeepTogether([sim_table_obj_final_pdf]))
                    else: 
                        story.append(Paragraph(get_text(texts, "pdf_simulation_data_not_available", "Simulationsdetails nicht ausreichend für Tabellendarstellung."), STYLES.get('NormalLeft')))

                elif section_key_current == "CO2Savings":
                    co2_savings_val = current_analysis_results_pdf.get('annual_co2_savings_kg', 0.0)
                    trees_equiv = current_analysis_results_pdf.get('co2_equivalent_trees_per_year', 0.0)
                    car_km_equiv = current_analysis_results_pdf.get('co2_equivalent_car_km_per_year', 0.0)
                    airplane_km_equiv = co2_savings_val / 0.23 if co2_savings_val > 0 else 0.0
                    
                    # Verbesserter CO₂-Text mit mehr Details und professioneller Formatierung
                    co2_intro = get_text(texts, "pdf_co2_intro", "Mit Ihrer neuen Photovoltaikanlage leisten Sie einen wertvollen Beitrag zum Klimaschutz:")
                    story.append(Paragraph(co2_intro, STYLES.get('NormalLeft')))
                    story.append(Spacer(1, 0.2 * cm))
                    
                    # Haupteinsparung hervorheben
                    co2_main = get_text(texts, "pdf_annual_co2_main", "🌱 <b>Jährliche CO₂-Einsparung: {co2_savings_kg_formatted} kg</b>").format(
                        co2_savings_kg_formatted=format_kpi_value(co2_savings_val, "", precision=0, texts_dict=texts)
                    )
                    story.append(Paragraph(co2_main, STYLES.get('HeadingCenter')))
                    story.append(Spacer(1, 0.3 * cm))
                    
                    # Anschauliche Vergleiche in einer schönen Tabelle
                    co2_data = [
                        [get_text(texts, "pdf_co2_comparison_header", "Vergleich"), get_text(texts, "pdf_co2_equivalent_header", "Entspricht")],
                        ["🌳 Bäume (CO₂-Bindung)", f"{trees_equiv:.0f} Bäume pro Jahr"],
                        ["🚗 Autofahrten", f"{car_km_equiv:,.0f} km weniger pro Jahr"],
                        ["✈️ Flugreisen", f"{airplane_km_equiv:,.0f} km weniger pro Jahr"],
                        ["📊 CO₂-Fußabdruck", get_text(texts, "pdf_co2_footprint_reduction", "Deutliche Reduktion Ihres persönlichen CO₂-Fußabdrucks")]
                    ]
                    
                    co2_table = Table(co2_data, colWidths=[8*cm, 8*cm])
                    co2_table.setStyle(TableStyle([
                        # Header-Stil
                        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header_bg']),
                        ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['table_header_text']),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        
                        # Datenzeilen
                        ('BACKGROUND', (0, 1), (-1, -1), COLORS['table_row_bg']),
                        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_dark']),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                        
                        # Rahmen und Linien
                        ('GRID', (0, 0), (-1, -1), 1, COLORS['table_border']),
                        ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['accent_primary']),
                        
                        # Zebra-Streifen für bessere Lesbarkeit
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['table_row_bg'], COLORS['table_alt_row_bg']]),
                        
                        # Padding
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ]))
                    
                    story.append(co2_table)
                    story.append(Spacer(1, 0.3 * cm))

                for section_key_current, title_text_key_current, default_title_current in ordered_section_definitions_pdf:
                    co2_chart_bytes = current_analysis_results_pdf.get('co2_savings_chart_bytes')
                if co2_chart_bytes:
                    try:
                        co2_img = ImageReader(io.BytesIO(co2_chart_bytes))
                        co2_image = Image(co2_img, width=16*cm, height=10*cm)
                        story.append(co2_image)
                        story.append(Spacer(1, 0.2 * cm))
                    except Exception as e:
                        print(f"Fehler beim Einfügen der CO₂-Grafik: {e}")
                    
                    # Abschließender motivierender Text
                    co2_conclusion = get_text(texts, "pdf_co2_conclusion", "Diese Zahlen verdeutlichen den positiven Umweltbeitrag Ihrer Photovoltaikanlage. Über die gesamte Betriebsdauer von 25+ Jahren summiert sich die CO₂-Einsparung auf mehrere Tonnen – ein wichtiger Schritt für den Klimaschutz und nachfolgende Generationen.")
                    story.append(Paragraph(co2_conclusion, STYLES.get('NormalLeft')))

                
                if section_key_current in active_sections_set_pdf:
                    if section_key_current == "Visualizations":
                        story.append(Paragraph(
                            get_text(
                                texts,
                                "pdf_visualizations_intro",
                                "Die folgenden Diagramme visualisieren die Ergebnisse Ihrer Photovoltaikanlage und deren Wirtschaftlichkeit:"
                            ),
                            STYLES.get('NormalLeft')
                        ))
                        # Spacer gehört hier _ohne_ except
                        story.append(Spacer(1, 0.3 * cm))

                            # ERWEITERUNG: …
                        charts_config_for_pdf_generator = {
                    'monthly_prod_cons_chart_bytes':       {"title_key": "pdf_chart_title_monthly_comp_pdf",    "default_title": "Monatl. Produktion/Verbrauch (2D)"},
                    'cost_projection_chart_bytes':         {"title_key": "pdf_chart_label_cost_projection",      "default_title": "Stromkosten-Hochrechnung (2D)"},
                    'cumulative_cashflow_chart_bytes':     {"title_key": "pdf_chart_label_cum_cashflow",        "default_title": "Kumulierter Cashflow (2D)"},
                    'consumption_coverage_pie_chart_bytes':{"title_key": "pdf_chart_title_consumption_coverage_pdf","default_title": "Deckung Gesamtverbrauch (Jahr 1)"},
                    'pv_usage_pie_chart_bytes':            {"title_key": "pdf_chart_title_pv_usage_pdf",        "default_title": "Nutzung PV-Strom (Jahr 1)"},
                    'daily_production_switcher_chart_bytes':{"title_key": "pdf_chart_label_daily_3d",            "default_title": "Tagesproduktion (3D)"},
                    'weekly_production_switcher_chart_bytes':{"title_key": "pdf_chart_label_weekly_3d",           "default_title": "Wochenproduktion (3D)"},
                    'yearly_production_switcher_chart_bytes':{"title_key": "pdf_chart_label_yearly_3d_bar",      "default_title": "Jahresproduktion (3D-Balken)"},
                    'project_roi_matrix_switcher_chart_bytes':{"title_key": "pdf_chart_label_roi_matrix_3d",      "default_title": "Projektrendite-Matrix (3D)"},
                    'feed_in_revenue_switcher_chart_bytes':{"title_key": "pdf_chart_label_feedin_3d",           "default_title": "Einspeisevergütung (3D)"},
                    'prod_vs_cons_switcher_chart_bytes':   {"title_key": "pdf_chart_label_prodcons_3d",        "default_title": "Verbr. vs. Prod. (3D)"},
                    'tariff_cube_switcher_chart_bytes':    {"title_key": "pdf_chart_label_tariffcube_3d",      "default_title": "Tarifvergleich (3D)"},
                    'co2_savings_value_switcher_chart_bytes':{"title_key": "pdf_chart_label_co2value_3d",       "default_title": "CO₂-Ersparnis vs. Wert (3D)"},
                    'co2_savings_chart_bytes':            {"title_key": "pdf_chart_label_co2_realistic",       "default_title": "CO₂-Einsparung (Realistische Darstellung)"},
                    'investment_value_switcher_chart_bytes':{"title_key": "pdf_chart_label_investval_3D",       "default_title": "Investitionsnutzwert (3D)"},
                    'storage_effect_switcher_chart_bytes':{"title_key": "pdf_chart_label_storageeff_3d",       "default_title": "Speicherwirkung (3D)"},
                    'selfuse_stack_switcher_chart_bytes': {"title_key": "pdf_chart_label_selfusestack_3d",    "default_title": "Eigenverbr. vs. Einspeis. (3D)"},
                    'cost_growth_switcher_chart_bytes':    {"title_key": "pdf_chart_label_costgrowth_3d",      "default_title": "Stromkostensteigerung (3D)"},
                    'selfuse_ratio_switcher_chart_bytes':  {"title_key": "pdf_chart_label_selfuseratio_3d",    "default_title": "Eigenverbrauchsgrad (3D)"},
                    'roi_comparison_switcher_chart_bytes':{"title_key": "pdf_chart_label_roicompare_3d",     "default_title": "ROI-Vergleich (3D)"},
                    'scenario_comparison_switcher_chart_bytes':{"title_key": "pdf_chart_label_scenariocomp_3d","default_title": "Szenarienvergleich (3D)"},
                    'tariff_comparison_switcher_chart_bytes':{"title_key": "pdf_chart_label_tariffcomp_3d",   "default_title": "Vorher/Nachher Stromkosten (3D)"},
                    'income_projection_switcher_chart_bytes':{"title_key": "pdf_chart_label_incomeproj_3d",   "default_title": "Einnahmenprognose (3D)"},
                    'yearly_production_chart_bytes':      {"title_key": "pdf_chart_label_pvvis_yearly",       "default_title": "PV Visuals: Jahresproduktion"},
                    'break_even_chart_bytes':             {"title_key": "pdf_chart_label_pvvis_breakeven",    "default_title": "PV Visuals: Break-Even"},
                    'amortisation_chart_bytes':           {"title_key": "pdf_chart_label_pvvis_amort",        "default_title": "PV Visuals: Amortisation"},
                }

                charts_added_count = 0
                selected_charts_for_pdf_opt = inclusion_options.get("selected_charts_for_pdf", [])

                for chart_key, config in charts_config_for_pdf_generator.items():
                    if chart_key not in selected_charts_for_pdf_opt:
                        continue

                    chart_image_bytes = current_analysis_results_pdf.get(chart_key)
                    if isinstance(chart_image_bytes, (bytes, bytearray)):
                        title = get_text(texts, config["title_key"], config["default_title"])
                        story.append(Paragraph(title, STYLES.get('ChartTitle')))
                        flowables = _get_image_flowable(
                            chart_image_bytes,
                            available_width_content * 0.9,
                            texts,
                            max_height=12 * cm,
                            align='CENTER'
                        )
                        story.extend(flowables)
                        story.append(Spacer(1, 0.7 * cm))
                        charts_added_count += 1
                    else:
                        placeholder = get_text(
                            texts,
                            "pdf_chart_load_error_placeholder_param",
                            f"(Fehler beim Laden: {config['default_title']})"
                        )
                        story.append(Paragraph(placeholder, STYLES.get('NormalCenter')))
                        story.append(Spacer(1, 0.5 * cm))

                if selected_charts_for_pdf_opt and charts_added_count == 0:
                    story.append(Paragraph(
                        get_text(texts, "pdf_selected_charts_not_renderable",
                                 "Ausgewählte Diagramme konnten nicht geladen/angezeigt werden."),
                        STYLES.get('NormalCenter')
                    ))
                elif not selected_charts_for_pdf_opt:
                    story.append(Paragraph(
                        get_text(texts, "pdf_no_charts_selected_for_section",
                                 "Keine Diagramme für diese Sektion ausgewählt."),
                        STYLES.get('NormalCenter')
                    ))

            # … hier folgen ggf. weitere elif-Blöcke für andere Sektionen …
            except Exception as e:                                           
                error_text = get_text(
                texts,
                "pdf_visualizations_error",
                "Fehler beim Erstellen der Diagramme."
            )
            story.append(Paragraph(error_text, STYLES.get('NormalLeft')))

# ─── Ende der Abschnitts-Schleife ───────────────────────────────────────────
# main_pdf_bytes: Optional[bytes] = Nonemain_pdf_bytes: Optional[bytes] = None
mamain_offer_buffer = BytesIO()
la    'texts_ref':                 texts,
  layout_callback_kwargs_build = {    'company_logo_base64_ref':   company_logo_base64 if include_company_logo_opt else None,
      'texts_ref':                 texts,    'page_width_ref':            doc.pagesize[0],
      'company_info_ref':          company_info,    'margin_left_ref':           doc.leftMargin,
      'company_logo_base64_ref':   company_logo_base64 if include_company_logo_opt else None,    'margin_top_ref':            doc.topMargin,
      'offer_number_ref':          offer_number_final,    'include_custom_footer_ref': include_custom_footer_opt,
      'page_width_ref':            doc.pagesize[0],}

      'margin_left_ref':           doc.leftMargin,    doc.build(
      'margin_right_ref':          doc.rightMargin,        canvasmaker=lambda *args, **kwargs_c: PageNumCanvas(
      'margin_top_ref':            doc.topMargin,            onPage_callback=page_layout_handler,
      'margin_bottom_ref':         doc.bottomMargin,            **kwargs_c
      'include_custom_footer_ref': include_custom_footer_opt,    )
      'include_header_logo_ref':   include_header_logo_optelse:
      )        
# if main_offer_buffer:
  if doc and story:          # Ensure this code is placed inside the generate_offer_pdf function, properly indented:if not main_pdf_bytes: 
if    doc.build(    return main_pdf_bytes

          canvasmaker=lambda *args, **kwargs_c: PageNumCanvas(    debug_info = {
              *args,        'company_docs_found': [],
              onPage_callback=page_layout_handler,        'total_paths_to_append': 0
              callback_kwargs=layout_callback_kwargs_build,    product_ids_for_datasheets = list(filter(None, [
              **kwargs_c        pv_details_pdf.get("selected_inverter_id"),
          )    ]))
      ]        comp_id_val = pv_details_pdf.get(opt_id_key)
      main_pdf_bytes = main_offer_buffer.getvalue()        # Duplikate entfernen, falls ein Produkt mehrfach auftaucht (unwahrscheinlich, aber sicher)

el    main_pdf_bytes = None        product_ids_for_datasheets = list(filter(None, [
          datasheet_path_from_db: pv_details_pdf.get("selected_inverter_id"),
  if main_offer_buffer:        debug_info['product_datasheets_found'].append({'id': prod_id, 'model': product_info.get('model_name'), 'path': full_datasheet_path})
      main_offer_buffer.close()          debug_info['product_datasheets_missing'].append({'id': prod_id, 'model': product_info.get('model_name'), 'path': full_datasheet_path})
              debug_info['product_datasheets_missing'].append({'id': prod_id, 'model': product_info.get('model_name'), 'reason': 'Kein Datenblatt-Pfad in DB'})
  if not main_pdf_bytes:            debug_info['product_datasheets_missing'].append({'id': prod_id, 'reason': 'Produkt nicht in DB gefunden'})
      return main_pdf_bytes            if comp_id_val:
      if company_document_ids_to_include_opt and active_company_id is not None and callable(db_list_company_documents_func):
  # Wenn kein Zusammenführen mit Anhängen gewünscht oder PyPDF fehlt          product_ids_for_datasheets = list(set(product_ids_for_datasheets))                if doc_info.get('id') in company_document_ids_to_include_opt:
  if not (include_all_documents_opt and _PYPDF_AVAILABLE):          for prod_id in product_ids_for_datasheets:                        full_doc_path = os.path.join(COMPANY_DOCS_BASE_DIR_PDF_GEN, relative_doc_path)
      # Keine Anhänge mergen, direkt zurück                  product_info = get_product_by_id_func(prod_id)                        else:
      return main_pdf_bytes                      datasheet_path_from_db = product_info.get("datasheet_link_db_path")        except Exception as e_company_docs:
                            full_datasheet_path = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, datasheet_path_from_db)    debug_info['total_paths_to_append'] = len(paths_to_append)
  debug_info = {                              paths_to_append.append(full_datasheet_path)    
      'product_datasheets_missing': [],                          else:        for page in main_offer_reader.pages: 
      'company_docs_found': [],                      else:
      'company_docs_missing': [],                  else:            datasheet_reader = PdfReader(pdf_path)
      'total_paths_to_append': 0              except Exception:        except Exception as e_append_ds:
  }                          pdf_writer.write(final_buffer)
            if company_document_ids_to_include_opt and active_company_id is not None and callable(db_list_company_documents_func):        return main_pdf_bytes 
  # Produktdatenblätter sammeln                  all_company_docs_for_active_co = db_list_company_documents_func(active_company_id, None)
deproduct_ids_for_datasheets = list(filter(None, [                      if doc_info.get('id') in company_document_ids_to_include_opt:    
      pv_details_pdf.get("selected_module_id"),                          if relative_doc_path:        texts: Text-Dictionary
      pv_details_pdf.get("selected_inverter_id"),                              if os.path.exists(full_doc_path):    """
      pv_details_pdf.get("selected_storage_id") if pv_details_pdf.get("include_storage") else None                                  debug_info['company_docs_found'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'path': full_doc_path})        'critical_errors': [],
  ]))                                  debug_info['company_docs_missing'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'path': full_doc_path})    # Kundendaten prüfen (nicht kritisch)
  for opt_id_key in ['selected_wallbox_id', 'selected_ems_id', 'selected_optimizer_id', 'selected_carport_id', 'selected_notstrom_id', 'selected_tierabwehr_id']:                              debug_info['company_docs_missing'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'reason': 'Kein relativer Pfad in DB'})            get_text(texts, 'pdf_warning_no_customer_name', 'Kein Kundenname verfügbar - wird als "Kunde" angezeigt')
      comp_id_val = pv_details_pdf.get(opt_id_key)                  pass    # PV-Details prüfen
      if comp_id_val:          debug_info['total_paths_to_append'] = len(paths_to_append)    # Entweder module in pv_details ODER module_quantity in project_details ist ausreichend
          product_ids_for_datasheets.append(comp_id_val)          if not paths_to_append:    elif project_details and project_details.get('module_quantity', 0) > 0:
  product_ids_for_datasheets = list(set(product_ids_for_datasheets))                  validation_result['warnings'].append(
            try:        # Nur als Warnung, nicht als kritischer Fehler
  paths_to_append = []              for page in main_offer_reader.pages:        # Wirklich leere oder sehr minimale Analyse ist ein kritischer Fehler
            except Exception:        validation_result['is_valid'] = False
  # Produktdatenblätter-Pfade ermitteln          # und geben nur Warnungen aus, wenn wichtige KPIs fehlen
  if callable(get_product_by_id_func):          for pdf_path in paths_to_append:            if not analysis_results.get(kpi):
      for prod_id in product_ids_for_datasheets:                  datasheet_reader = PdfReader(pdf_path)            missing_kpi_names = ', '.join(missing_kpis)
          try:                      pdf_writer.add_page(page)            validation_result['missing_data_summary'].extend(missing_kpis)
              product_info = get_product_by_id_func(prod_id)              except Exception:    if not project_data.get('company_information', {}).get('name'):
              if product_info:          validation_result['missing_data_summary'].append('Firmendaten')
                  datasheet_path_from_db = product_info.get("datasheet_link_db_path")          try:          f"Warnungen={len(validation_result['warnings'])}, "
                  if datasheet_path_from_db:              final_pdf_bytes = final_buffer.getvalue()def _create_no_data_fallback_pdf(texts: Dict[str, str], customer_data: Dict[str, Any] = None) -> bytes:
                      full_datasheet_path = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, datasheet_path_from_db)          except Exception:    Args:
                      if os.path.exists(full_datasheet_path):          finally:    Returns:
                          paths_to_append.append(full_datasheet_path)    from reportlab.lib.units import cm
                      else:    
                          debug_info['product_datasheets_missing'].append({    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
                              'id': prod_id,    story = []
                              'model': product_info.get('model_name'),    # Titel
                              'path': full_datasheet_path    story.append(Paragraph(title, styles['Title']))
                          })    
                  else:    if customer_data and customer_data.get('last_name'):
                      debug_info['product_datasheets_missing'].append({        customer_text = get_text(texts, 'pdf_no_data_customer', f'Für: {customer_name}')
                          'id': prod_id,        story.append(Spacer(1, 0.5*cm))
                          'model': product_info.get('model_name'),    # Haupttext
                          'reason': 'Kein Datenblatt-Pfad in DB'        '''Liebe Kundin, lieber Kunde,
                      })        für die Erstellung Ihres individuellen Photovoltaik-Angebots benötigen wir noch einige wichtige Informationen:
              else:        <b>Erforderliche Daten:</b>
                  debug_info['product_datasheets_missing'].append({        • Gewünschte PV-Module und Komponenten
                      'id': prod_id,        • Technische Angaben zu Ihrem Dach/Standort
                      'reason': 'Produkt nicht in DB gefunden'        <b>Nächste Schritte:</b>
                  })        2. Führen Sie die Wirtschaftlichkeitsberechnung durch
          except:        
              pass    
      story.append(Spacer(1, 1*cm))
  # Firmendokumente sammeln    # Kontaktinformationen
  if company_document_ids_to_include_opt and active_company_id is not None and callable(db_list_company_documents_func):        'Kontakt: Bitte wenden Sie sich an unser Beratungsteam für weitere Unterstützung.')
      try:    
          all_company_docs_for_active_co = db_list_company_documents_func(active_company_id, None)    buffer.seek(0)
          for doc_info in all_company_docs_for_active_co:    
#             if doc_info.get('id') in company_document_ids_to_include_opt:# 2025-06-03, Gemini Ultra: PageNumCanvas.save() korrigiert, um Duplizierung des PDF-Inhalts zu verhindern.
#                 relative_doc_path = doc_info.get("relative_db_path")#                           Aufruf von `db_list_company_documents_func` mit `doc_type=None` versehen.
#                 if relative_doc_path:#                           Sicherstellung, dass ausgewählte Diagramme für PDF-Visualisierungen berücksichtigt werden.
#                     full_doc_path = os.path.join(COMPANY_DOCS_BASE_DIR_PDF_GEN, relative_doc_path)# 2025-06-03, Gemini Ultra: `charts_config_for_pdf_generator` erweitert, um alle Diagramme aus `pdf_ui.py` abzudecken.
#                     if os.path.exists(full_doc_path):#                           Logik zum Anhängen von Produktdatenblättern erweitert, um auch Zubehör-Datenblätter zu berücksichtigen.
#                         paths_to_append.append(full_doc_path)# 2025-06-03, Gemini Ultra: Validierungs- und Fallback-Funktionen für PDF-Erstellung ohne ausreichende Daten hinzugefügt.
#                         debug_info['company_docs_found'].append({                            'id': doc_info.get('id'),                            'name': doc_info.get('display_name'),                            'path': full_doc_path                        })                    else:                        debug_info['company_docs_missing'].append({                            'id': doc_info.get('id'),                            'name': doc_info.get('display_name'),                            'path': full_doc_path                        })                else:                    debug_info['company_docs_missing'].append({                        'id': doc_info.get('id'),                        'name': doc_info.get('display_name'),                        'reason': 'Kein relativer Pfad in DB'                    })    except:        passdebug_info['total_paths_to_append'] = len(paths_to_append)if not paths_to_append:    # Keine zusätzlichen PDFs    return main_pdf_bytes# Haupt-PDF einlesen und Seiten in Writer übertragenpdf_writer = PdfWriter()try:    main_offer_reader = PdfReader(io.BytesIO(main_pdf_bytes))    for page in main_offer_reader.pages:        pdf_writer.add_page(page)except Exception as e_read_main:    return main_pdf_bytes# Weitere PDFs anhängenfor pdf_path in paths_to_append:    try:        datasheet_reader = PdfReader(pdf_path)        for page in datasheet_reader.pages:            pdf_writer.add_page(page)    except:        pass# Neues PDF zusammenbauenfinal_buffer = io.BytesIO()try:    pdf_writer.write(final_buffer)    final_pdf_bytes = final_buffer.getvalue()finally:    final_buffer.close()return final_pdf_bytesreturn final_pdf_bytesn.