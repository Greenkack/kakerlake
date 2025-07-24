# Datei: theming/pdf_styles.py
# FINALER CODESTAND by Seggeli Ultra

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import TableStyle, Table

# --- GRUNDLEGENDE SCHRIFTARTEN-DEFINITIONEN (Annahme: diese sind bereits vorhanden) ---
FONT_FAMILY_SANS = "Helvetica"
FONT_BOLD_SANS = "Helvetica-Bold"
FONT_FAMILY_SERIF = "Times-Roman"
FONT_BOLD_SERIF = "Times-Bold"

# --- THEME 1: BLAU ELEGANT (ERWEITERT) ---
THEME_BLUE_ELEGANT = {
    "name": "Blau Elegant",
    "colors": {
        "primary": "#2980b9",
        "secondary": "#3498db",
        "background": "#ffffff",
        "text_body": "#34495e",
        "text_heading": "#2c3e50",
        "header_text": "#ffffff",
        "table_header_bg": "#2980b9",
        "table_row_bg_even": "#ecf0f1",
        "table_row_bg_odd": "#ffffff",
        "footer_text": "#7f8c8d",
        "highlight_bg": "#f9f9f9",
        "highlight_border": "#2980b9",
    },
    "fonts": {
        "family_main": FONT_FAMILY_SANS,
        "family_bold": FONT_BOLD_SANS,
        "size_h1": 22, "size_h2": 18, "size_h3": 14,
        "size_body": 10, "size_description": 9, "size_footer": 9,
    },
    "logo_path": "assets/logos/logo_color.png",
    "logo_placement": "every_page",
    "logo_pos": (17, 27), # in cm
    "logo_size": (3, 1.5), # in cm
    "show_page_numbers": True,
}

# --- THEME 2: ÖKO GRÜN (ERWEITERT) ---
THEME_ECO_GREEN = {
    "name": "Öko Grün",
    "colors": {
        "primary": "#27ae60",
        "secondary": "#f39c12",
        "background": "#ffffff",
        "text_body": "#2c3e50",
        "text_heading": "#2c3e50",
        "header_text": "#ffffff",
        "table_header_bg": "#27ae60",
        "table_row_bg_even": "#e8f8ef",
        "table_row_bg_odd": "#ffffff",
        "footer_text": "#7f8c8d",
        "highlight_bg": "#e8f8ef",
        "highlight_border": "#27ae60",
    },
    "fonts": {
        "family_main": FONT_FAMILY_SANS,
        "family_bold": FONT_BOLD_SANS,
        "size_h1": 20, "size_h2": 16, "size_h3": 13,
        "size_body": 10, "size_description": 9, "size_footer": 8,
    },
    "logo_path": "assets/logos/logo_color.png",
    "logo_placement": "every_page",
    "logo_pos": (17, 27),
    "logo_size": (3, 1.5),
    "show_page_numbers": True,
}

# --- THEME 3: SALT & PEPPER (NEU) ---
THEME_SALT_N_PEPPER = {
    "name": "Salt & Pepper",
    "colors": {
        "primary": "#000000", "secondary": "#444444", "background": "#FFFFFF",
        "text_body": "#000000", "text_heading": "#000000", "header_text": "#FFFFFF",
        "table_header_bg": "#000000", "table_row_bg_even": "#EEEEEE", "table_row_bg_odd": "#FFFFFF",
        "footer_text": "#888888", "highlight_bg": "#F5F5F5", "highlight_border": "#000000",
    },
    "fonts": {
        "family_main": FONT_FAMILY_SERIF, "family_bold": FONT_BOLD_SERIF,
        "size_h1": 20, "size_h2": 16, "size_h3": 12, "size_body": 10, "size_description": 9, "size_footer": 8,
    },
    "logo_path": "assets/logos/logo_bw.png",
    "logo_placement": "title_only",
    "logo_pos": (17, 27),
    "logo_size": (3, 1.5),
    "show_page_numbers": True,
}

# --- AVAILABLE_THEMES für Import-Kompatibilität ---
AVAILABLE_THEMES = {
    "Blau Elegant": THEME_BLUE_ELEGANT,
    "Öko Grün": THEME_ECO_GREEN,
    "Salt & Pepper": THEME_SALT_N_PEPPER,
}

# --- ZENTRALE FUNKTION ZUM LADEN UND VERARBEITEN EINES THEMES ---
def get_theme(theme_name: str = "Blau Elegant") -> dict:
    """
    Lädt ein Theme-Dictionary und generiert daraus ReportLab-spezifische Style-Objekte.
    """
    themes = {
        "Blau Elegant": THEME_BLUE_ELEGANT,
        "Öko Grün": THEME_ECO_GREEN,
        "Salt & Pepper": THEME_SALT_N_PEPPER,
    }
    theme_data = themes.get(theme_name, THEME_BLUE_ELEGANT)
    
    # Alias für einfachen Zugriff
    fonts = theme_data["fonts"]
    colors_map = theme_data["colors"]

    # Generiere ParagraphStyles
    styles = {
        'h1': ParagraphStyle(name='h1', fontName=fonts['family_bold'], fontSize=fonts['size_h1'], textColor=colors.HexColor(colors_map['text_heading']), alignment=TA_LEFT, leading=fonts['size_h1'] * 1.2),
        'h2': ParagraphStyle(name='h2', fontName=fonts['family_bold'], fontSize=fonts['size_h2'], textColor=colors.HexColor(colors_map['text_heading']), alignment=TA_LEFT, leading=fonts['size_h2'] * 1.2, spaceBefore=10),
        'h3': ParagraphStyle(name='h3', fontName=fonts['family_bold'], fontSize=fonts['size_h3'], textColor=colors.HexColor(colors_map['text_heading']), alignment=TA_LEFT, leading=fonts['size_h3'] * 1.2, spaceBefore=8),
        'BodyText': ParagraphStyle(name='BodyText', fontName=fonts['family_main'], fontSize=fonts['size_body'], textColor=colors.HexColor(colors_map['text_body']), alignment=TA_LEFT, leading=fonts['size_body'] * 1.5),
        'ChartDescription': ParagraphStyle(name='ChartDescription', fontName=fonts['family_main'], fontSize=fonts['size_description'], textColor=colors.HexColor(colors_map['text_body']), alignment=TA_CENTER, leading=fonts['size_description'] * 1.4),
        'SmallTextRight': ParagraphStyle(name='SmallTextRight', fontName=fonts['family_main'], fontSize=fonts['size_footer'], textColor=colors.HexColor(colors_map['footer_text']), alignment=TA_RIGHT),
        'ErrorText': ParagraphStyle(name='ErrorText', fontName=fonts['family_main'], fontSize=fonts['size_body'], textColor=colors.red, alignment=TA_LEFT),
        'ItalicText': ParagraphStyle(name='ItalicText', fontName=f"{fonts['family_main']}-Oblique", fontSize=fonts['size_body'], textColor=colors.HexColor(colors_map['text_body']), alignment=TA_LEFT, leading=fonts['size_body'] * 1.5),
    }
    
    # Füge die rohen Daten und die generierten Styles zum Theme hinzu
    theme_data['styles'] = styles
    return theme_data

# --- ZENTRALE FUNKTION ZUR ERSTELLUNG VON TABELLEN-STYLES (NEU) ---
def create_modern_table_style(theme: dict) -> TableStyle:
    """
    Erzeugt ein modernes TableStyle-Objekt basierend auf einem übergebenen Theme-Dictionary.
    """
    fonts = theme.get("fonts", {})
    colors_map = theme.get("colors", {})

    style = TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(colors_map.get("table_header_bg", "#000000"))),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(colors_map.get("header_text", "#FFFFFF"))),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), fonts.get("family_bold", "Helvetica-Bold")),
        ('FONTSIZE', (0, 0), (-1, 0), fonts.get("size_body", 10)),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Body
        ('FONTNAME', (0, 1), (-1, -1), fonts.get("family_main", "Helvetica")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(colors_map.get("text_body", "#000000"))),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 1), (-1, -1), 10),
        ('RIGHTPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

        # Gitter
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ])
    return style
