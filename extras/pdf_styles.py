# pdf_styles.py
"""
Datei: pdf_styles.py
Zweck: Definiert zentrale Stile (Farben, Schriften, Absatz- und Tabellenstile)
       für die PDF-Generierung in der Solar-App.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-05 (Korrigierter Import für Dict)
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.lib.units import cm, mm
from reportlab.platypus import TableStyle
from typing import Dict # KORREKTUR: Import für Dict hinzugefügt

# --- Basisschriftarten ---
FONT_FAMILY_NORMAL = "Helvetica"
FONT_FAMILY_BOLD = "Helvetica-Bold"
FONT_FAMILY_ITALIC = "Helvetica-Oblique"

# --- Standardfarbpalette (kann dynamisch überschrieben werden) ---
DEFAULT_PRIMARY_COLOR_HEX = "#003366" 
DEFAULT_SECONDARY_COLOR_HEX = "#EFEFEF"
DEFAULT_TEXT_COLOR_HEX = "#2C2C2C"   
DEFAULT_SEPARATOR_LINE_COLOR_HEX = "#B0B0B0"

def get_color_palette(primary_hex: str = DEFAULT_PRIMARY_COLOR_HEX,
                      secondary_hex: str = DEFAULT_SECONDARY_COLOR_HEX,
                      text_hex: str = DEFAULT_TEXT_COLOR_HEX,
                      separator_hex: str = DEFAULT_SEPARATOR_LINE_COLOR_HEX) -> Dict[str, colors.Color]: # Hier war der NameError
    """Gibt ein Dictionary mit den Farbobjekten zurück."""
    return {
        "primary": colors.HexColor(primary_hex),
        "secondary": colors.HexColor(secondary_hex),
        "text": colors.HexColor(text_hex),
        "separator": colors.HexColor(separator_hex),
        "white": colors.white,
        "black": colors.black,
        "grey": colors.grey,
        "darkgrey": colors.darkgrey,
    }

# ... (Rest der Datei pdf_styles.py bleibt unverändert wie von Ihnen zuletzt bereitgestellt) ...
def get_pdf_stylesheet(color_palette: Dict[str, colors.Color]) -> StyleSheet1:
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(name='Normal', fontName=FONT_FAMILY_NORMAL, fontSize=10, leading=12, textColor=color_palette['text']))
    stylesheet.add(ParagraphStyle(name='NormalLeft', parent=stylesheet['Normal'], alignment=TA_LEFT))
    stylesheet.add(ParagraphStyle(name='NormalRight', parent=stylesheet['Normal'], alignment=TA_RIGHT))
    stylesheet.add(ParagraphStyle(name='NormalCenter', parent=stylesheet['Normal'], alignment=TA_CENTER))
    stylesheet.add(ParagraphStyle(name='NormalJustify', parent=stylesheet['Normal'], alignment=TA_JUSTIFY))
    stylesheet.add(ParagraphStyle(name='HeaderFooterText', parent=stylesheet['Normal'], fontSize=8, textColor=color_palette['darkgrey']))
    stylesheet.add(ParagraphStyle(name='PageInfo', parent=stylesheet['HeaderFooterText'], alignment=TA_CENTER))
    stylesheet.add(ParagraphStyle(name='DocumentTitleHeader', parent=stylesheet['HeaderFooterText'], fontName=FONT_FAMILY_BOLD, alignment=TA_RIGHT, fontSize=9))
    stylesheet.add(ParagraphStyle(name='CompanyAddressFooter', parent=stylesheet['HeaderFooterText'], fontSize=7, alignment=TA_LEFT))
    stylesheet.add(ParagraphStyle(name='OfferMainTitle', fontName=FONT_FAMILY_BOLD, fontSize=22, leading=26, alignment=TA_CENTER, spaceBefore=1.5*cm, spaceAfter=1.5*cm, textColor=color_palette['primary']))
    stylesheet.add(ParagraphStyle(name='SectionTitle', fontName=FONT_FAMILY_BOLD, fontSize=16, leading=19, spaceBefore=1.2*cm, spaceAfter=0.6*cm, keepWithNext=1, textColor=color_palette['primary']))
    stylesheet.add(ParagraphStyle(name='SubSectionTitle', fontName=FONT_FAMILY_BOLD, fontSize=13, leading=16, spaceBefore=0.8*cm, spaceAfter=0.4*cm, keepWithNext=1, textColor=color_palette['primary']))
    stylesheet.add(ParagraphStyle(name='ComponentTitle', parent=stylesheet['SubSectionTitle'], fontSize=11, spaceBefore=0.6*cm, spaceAfter=0.3*cm, alignment=TA_LEFT, textColor=color_palette['text']))
    stylesheet.add(ParagraphStyle(name='CompanyInfoDeckblatt', parent=stylesheet['NormalCenter'], fontSize=9, leading=11, spaceAfter=0.8*cm, textColor=color_palette['text']))
    stylesheet.add(ParagraphStyle(name='CustomerAddressDeckblatt', parent=stylesheet['NormalLeft'], fontSize=11, leading=14, spaceBefore=2*cm, spaceAfter=1*cm, textColor=color_palette['text']))
    stylesheet.add(ParagraphStyle(name='OfferDetailsDeckblatt', parent=stylesheet['NormalRight'], fontSize=10, leading=12, spaceBefore=0.5*cm))
    stylesheet.add(ParagraphStyle(name='CoverLetter', parent=stylesheet['NormalJustify'], fontSize=11, leading=15, spaceBefore=0.5*cm, spaceAfter=0.5*cm, firstLineIndent=0))
    stylesheet.add(ParagraphStyle(name='CustomerAddressInner', parent=stylesheet['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.2*cm, spaceAfter=0.8*cm)) 
    stylesheet.add(ParagraphStyle(name='BoldText', parent=stylesheet['NormalLeft'], fontName=FONT_FAMILY_BOLD))
    stylesheet.add(ParagraphStyle(name='ItalicText', parent=stylesheet['NormalLeft'], fontName=FONT_FAMILY_ITALIC))
    stylesheet.add(ParagraphStyle(name='TableText', parent=stylesheet['NormalLeft'], fontSize=9, leading=11))
    stylesheet.add(ParagraphStyle(name='TableTextSmall', parent=stylesheet['NormalLeft'], fontSize=8, leading=10))
    stylesheet.add(ParagraphStyle(name='TableNumber', parent=stylesheet['NormalRight'], fontSize=9, leading=11))
    stylesheet.add(ParagraphStyle(name='TableLabel', parent=stylesheet['NormalLeft'], fontName=FONT_FAMILY_BOLD, fontSize=9, leading=11))
    stylesheet.add(ParagraphStyle(name='TableHeader', parent=stylesheet['NormalCenter'], fontName=FONT_FAMILY_BOLD, fontSize=9, leading=11, textColor=color_palette['white'], backColor=color_palette['primary']))
    stylesheet.add(ParagraphStyle(name='TableBoldRight', parent=stylesheet['TableNumber'], fontName=FONT_FAMILY_BOLD))
    stylesheet.add(ParagraphStyle(name='ImageCaption', parent=stylesheet['NormalCenter'], fontName=FONT_FAMILY_ITALIC, fontSize=8, spaceBefore=0.1*cm, textColor=color_palette['grey']))
    stylesheet.add(ParagraphStyle(name='ChartTitle', parent=stylesheet['SubSectionTitle'], alignment=TA_CENTER, spaceBefore=0.8*cm, spaceAfter=0.3*cm, fontSize=12))
    return stylesheet
def get_base_table_style(color_palette: Dict[str, colors.Color]) -> TableStyle:
    return TableStyle([('TEXTCOLOR', (0,0), (-1,-1), color_palette['text']),('FONTNAME', (0,0), (-1,-1), FONT_FAMILY_NORMAL),('FONTSIZE', (0,0), (-1,-1), 9),('LEADING', (0,0), (-1,-1), 11),('GRID', (0,0), (-1,-1), 0.5, color_palette['separator']),('VALIGN', (0,0), (-1,-1), 'MIDDLE'),('LEFTPADDING', (0,0), (-1,-1), 3*mm),('RIGHTPADDING', (0,0), (-1,-1), 3*mm),('TOPPADDING', (0,0), (-1,-1), 2*mm),('BOTTOMPADDING', (0,0), (-1,-1), 2*mm)])
def get_data_table_style(color_palette: Dict[str, colors.Color]) -> TableStyle:
    return TableStyle([('BACKGROUND',(0,0),(-1,0), color_palette['primary']), ('TEXTCOLOR',(0,0),(-1,0), color_palette['white']), ('FONTNAME',(0,0),(-1,0), FONT_FAMILY_BOLD),('ALIGN',(0,0),(-1,0), 'CENTER'),('GRID',(0,0),(-1,-1), 0.5, color_palette['separator']),('VALIGN',(0,0),(-1,-1), 'MIDDLE'),('FONTNAME',(0,1),(-1,-1), FONT_FAMILY_NORMAL),('FONTSIZE',(0,1),(-1,-1), 9),('ALIGN',(0,1),(0,-1), 'LEFT'),('ALIGN',(1,1),(-1,-1), 'RIGHT'),('LEFTPADDING',(0,0),(-1,-1), 2*mm), ('RIGHTPADDING',(0,0),(-1,-1), 2*mm),('TOPPADDING',(0,0),(-1,-1), 1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1), 1.5*mm), ('TEXTCOLOR',(0,1),(-1,-1), color_palette['text'])])
def get_product_table_style(color_palette: Dict[str, colors.Color]) -> TableStyle:
    return TableStyle([('TEXTCOLOR',(0,0),(-1,-1), color_palette['text']),('FONTNAME',(0,0),(0,-1), FONT_FAMILY_BOLD), ('ALIGN',(0,0),(0,-1), 'LEFT'),('FONTNAME',(1,0),(1,-1), FONT_FAMILY_NORMAL), ('ALIGN',(1,0),(1,-1), 'LEFT'),('VALIGN',(0,0),(-1,-1), 'TOP'),('LEFTPADDING',(0,0),(-1,-1), 2*mm), ('RIGHTPADDING',(0,0),(-1,-1), 2*mm),('TOPPADDING',(0,0),(-1,-1), 1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1), 1.5*mm)])
def get_main_product_table_style() -> TableStyle:
    return TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0)])
# Änderungshistorie
# 2025-06-05, Gemini Ultra: Erstellung der Datei pdf_styles.py.
#                           Definition von Basisschriftarten und Standardfarbpalette.
#                           Funktion get_color_palette() zur dynamischen Erzeugung einer Farbpalette.
#                           Funktion get_pdf_stylesheet() zur Erzeugung des StyleSheet1-Objekts mit Absatzstilen.
#                           Funktionen get_base_table_style(), get_data_table_style(), get_product_table_style(), get_main_product_table_style()
#                           zur Erzeugung spezifischer Tabellenstile. Stile sind nun zentralisiert und modular.
# 2025-06-05, Gemini Ultra: Import von `Dict` aus `typing` hinzugefügt.