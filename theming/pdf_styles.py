# theming/pdf_styles.py
# -*- coding: utf-8 -*-
"""
pdf_styles.py

Dieses Modul zentralisiert alle Design- und Stil-Definitionen für die PDF-Generierung.
Es ermöglicht ein einfaches Umschalten zwischen verschiedenen visuellen Themes, um eine
konsistente und professionelle Markendarstellung zu gewährleisten.

Jedes Theme ist ein Dictionary, das Farben, Schriftarten und andere Stil-Attribute
definiert.

Author: Suratina Sicmislar
Version: 1.0 (AI-Generated & Future-Proof)
"""

# Basis-Schriftarten (können durch eigene .ttf-Dateien erweitert werden)
FONT_FAMILY_SANS = "Helvetica"
FONT_FAMILY_SERIF = "Times"
FONT_BOLD_SANS = "Helvetica-Bold"

# Definition der verschiedenen Themes
# Jedes Theme kann einfach kopiert und angepasst werden.

THEME_MODERN_DARK = {
    "name": "Modern Dark",
    "colors": {
        "primary": "#3498db",  # Ein kräftiges Blau
        "secondary": "#2ecc71",  # Ein frisches Grün
        "background": "#2c3e50",  # Dunkler Schiefer
        "text": "#ecf0f1",  # Helles Grau/Weiß
        "header_text": "#ffffff",
        "table_header_bg": "#34495e", # Etwas hellerer Schiefer
        "table_row_bg_even": "#2c3e50",
        "table_row_bg_odd": "#34495e",
        "footer_text": "#bdc3c7", # Helles Grau
    },
    "fonts": {
        "family_main": FONT_FAMILY_SANS,
        "family_bold": FONT_BOLD_SANS,
        "size_h1": 20,
        "size_h2": 16,
        "size_body": 10,
        "size_footer": 8,
    },
    "logo_path": "assets/logos/logo_white.png",  # Annahme: Es gibt verschiedene Logos
    "background_image": None,
}


THEME_CLASSIC_LIGHT = {
    "name": "Classic Light",
    "colors": {
        "primary": "#2980b9",  # Ein seriöses Blau
        "secondary": "#8e44ad",  # Ein edles Violett
        "background": "#ffffff",  # Weiß
        "text": "#34495e",  # Dunkelgrau
        "header_text": "#ffffff",
        "table_header_bg": "#2980b9",
        "table_row_bg_even": "#ecf0f1", # Sehr helles Grau
        "table_row_bg_odd": "#ffffff",
        "footer_text": "#7f8c8d", # mittleres Grau
    },
    "fonts": {
        "family_main": FONT_FAMILY_SERIF,
        "family_bold": FONT_BOLD_SANS,
        "size_h1": 22,
        "size_h2": 18,
        "size_body": 11,
        "size_footer": 9,
    },
    "logo_path": "assets/logos/logo_color.png",
    "background_image": None,
}

THEME_ECO_GREEN = {
    "name": "Öko Grün",
    "colors": {
        "primary": "#27ae60",  # Ein sattes Grün
        "secondary": "#f39c12",  # Ein sonniges Gelb/Orange
        "background": "#ffffff",
        "text": "#2c3e50",
        "header_text": "#ffffff",
        "table_header_bg": "#27ae60",
        "table_row_bg_even": "#e8f8ef",
        "table_row_bg_odd": "#ffffff",
        "footer_text": "#7f8c8d",
    },
    "fonts": {
        "family_main": FONT_FAMILY_SANS,
        "family_bold": FONT_BOLD_SANS,
        "size_h1": 20,
        "size_h2": 16,
        "size_body": 10,
        "size_footer": 8,
    },
    "logo_path": "assets/logos/logo_green.png",
    "background_image": None,
}

# Neues modernes Theme mit frischen Farben
THEME_SOLAR_MODERN = {
    "name": "Solar Modern",
    "colors": {
        "primary": "#1B365D",  # Dunkelblau
        "secondary": "#2E8B57",  # Solargrün
        "background": "#F8F9FA",  # Helles Grau
        "text": "#333333",  # Dunkles Grau
        "header_text": "#ffffff",
        "table_header_bg": "#1B365D",
        "table_row_bg_even": "#FFFFFF",
        "table_row_bg_odd": "#F1F3F5",
        "footer_text": "#6C757D",
    },
    "fonts": {
        "family_main": FONT_FAMILY_SANS,
        "family_bold": FONT_BOLD_SANS,
        "size_h1": 22,
        "size_h2": 17,
        "size_body": 10,
        "size_footer": 8,
    },
    "logo_path": "assets/logos/logo_modern.png",
    "background_image": None,
}


# Eine Liste aller verfügbaren Themes für einfache Iteration in der UI
AVAILABLE_THEMES = {
    "Modern Dark": THEME_MODERN_DARK,
    "Classic Light": THEME_CLASSIC_LIGHT,
    "Öko Grün": THEME_ECO_GREEN,
    "Solar Modern": THEME_SOLAR_MODERN,
}


def get_theme(theme_name: str) -> dict:
    """
    Gibt das Wörterbuch für ein bestimmtes Theme zurück.
    Fällt auf ein Standard-Theme zurück, wenn der Name ungültig ist.

    Args:
        theme_name (str): Der Name des gewünschten Themes.

    Returns:
        dict: Das Konfigurationswörterbuch des Themes.
    """
    return AVAILABLE_THEMES.get(theme_name, THEME_CLASSIC_LIGHT)
