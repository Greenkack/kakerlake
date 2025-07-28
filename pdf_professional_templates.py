# pdf_professional_templates.py
# -*- coding: utf-8 -*-
"""
pdf_professional_templates.py

Professionelle PDF-Templates für die Solar-App mit verschiedenen Designoptionen.
Erweitert das bestehende Template-System um moderne, professionelle Layouts.

Basiert auf: pdf_templates.py, theming/pdf_styles.py
Erweitert um: Professionelle Templates, Farbkombinationen, Layout-Optionen

Author: GitHub Copilot (Erweiterung des bestehenden Systems)
Version: 1.0 - Professionelle Erweiterung
"""

from typing import Dict, Any, List, Optional, Tuple
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
import colorsys

# Importiere bestehende Templates und Themes (falls verfügbar)
try:
    from pdf_templates import get_cover_letter_template, get_project_summary_template
    from theming.pdf_styles import get_theme, AVAILABLE_THEMES
    _EXISTING_TEMPLATES_AVAILABLE = True
except ImportError:
    _EXISTING_TEMPLATES_AVAILABLE = False

# Professionelle Farbpaletten basierend auf aktuellen Design-Trends
PROFESSIONAL_COLOR_SCHEMES = {
    "Corporate Blue": {
        "primary": "#1e3a8a",      # Tiefes Corporate Blau
        "secondary": "#3b82f6",    # Helleres Blau
        "accent": "#06b6d4",       # Cyan Akzent
        "text_dark": "#1f2937",    # Dunkelgrau
        "text_light": "#6b7280",   # Mittelgrau
        "background": "#ffffff",   # Weiß
        "background_light": "#f8fafc", # Sehr helles Grau
        "success": "#10b981",      # Grün für Erfolg
        "warning": "#f59e0b",      # Orange für Warnung
        "error": "#ef4444",        # Rot für Fehler
    },
    
    "Solar Energy": {
        "primary": "#059669",      # Solargrün
        "secondary": "#10b981",    # Helleres Grün
        "accent": "#f59e0b",       # Sonnengelb
        "text_dark": "#064e3b",    # Dunkelgrün
        "text_light": "#6b7280",   # Grau
        "background": "#ffffff",   # Weiß
        "background_light": "#f0fdf4", # Sehr helles Grün
        "success": "#22c55e",      # Helles Grün
        "warning": "#eab308",      # Gelb
        "error": "#dc2626",        # Rot
    },
    
    "Premium Gray": {
        "primary": "#374151",      # Elegantes Grau
        "secondary": "#6b7280",    # Helleres Grau
        "accent": "#8b5cf6",       # Violett Akzent
        "text_dark": "#111827",    # Fast Schwarz
        "text_light": "#9ca3af",   # Helles Grau
        "background": "#ffffff",   # Weiß
        "background_light": "#f9fafb", # Sehr helles Grau
        "success": "#10b981",      # Grün
        "warning": "#f59e0b",      # Orange
        "error": "#ef4444",        # Rot
    },
    
    "Modern Teal": {
        "primary": "#0f766e",      # Teal
        "secondary": "#14b8a6",    # Helleres Teal
        "accent": "#f97316",       # Orange Akzent
        "text_dark": "#134e4a",    # Dunkles Teal
        "text_light": "#6b7280",   # Grau
        "background": "#ffffff",   # Weiß
        "background_light": "#f0fdfa", # Sehr helles Teal
        "success": "#22c55e",      # Grün
        "warning": "#eab308",      # Gelb
        "error": "#dc2626",        # Rot
    }
}

# Professionelle Template-Definitionen
PROFESSIONAL_TEMPLATES = {
    "Executive Report": {
        "name": "Executive Report",
        "description": "Professionelles Unternehmens-Layout mit klarer Hierarchie",
        "color_scheme": "Corporate Blue",
        "layout": {
            "cover_style": "full_image_overlay",
            "header_height": 2.5 * cm,
            "footer_height": 1.5 * cm,
            "margins": {
                "top": 2.5 * cm,
                "bottom": 2.5 * cm,
                "left": 2.0 * cm,
                "right": 2.0 * cm
            },
            "page_numbers": True,
            "watermark": False
        },
        "typography": {
            "main_font": "Helvetica",
            "heading_font": "Helvetica-Bold",
            "accent_font": "Helvetica-Oblique",
            "h1_size": 24,
            "h2_size": 18,
            "h3_size": 14,
            "body_size": 11,
            "caption_size": 9
        }
    },
    
    "Solar Professional": {
        "name": "Solar Professional",
        "description": "Speziell für Solarenergie-Angebote optimiert",
        "color_scheme": "Solar Energy",
        "layout": {
            "cover_style": "split_design",
            "header_height": 2.0 * cm,
            "footer_height": 1.2 * cm,
            "margins": {
                "top": 2.0 * cm,
                "bottom": 2.0 * cm,
                "left": 2.0 * cm,
                "right": 2.0 * cm
            },
            "page_numbers": True,
            "watermark": False
        },
        "typography": {
            "main_font": "Helvetica",
            "heading_font": "Helvetica-Bold",
            "accent_font": "Helvetica-Oblique",
            "h1_size": 22,
            "h2_size": 16,
            "h3_size": 13,
            "body_size": 10,
            "caption_size": 8
        }
    },
    
    "Premium Minimal": {
        "name": "Premium Minimal",
        "description": "Elegantes, minimalistisches Design für Premium-Kunden",
        "color_scheme": "Premium Gray",
        "layout": {
            "cover_style": "minimal_text",
            "header_height": 1.5 * cm,
            "footer_height": 1.0 * cm,
            "margins": {
                "top": 3.0 * cm,
                "bottom": 3.0 * cm,
                "left": 2.5 * cm,
                "right": 2.5 * cm
            },
            "page_numbers": True,
            "watermark": False
        },
        "typography": {
            "main_font": "Helvetica",
            "heading_font": "Helvetica-Bold",
            "accent_font": "Helvetica-Oblique",
            "h1_size": 28,
            "h2_size": 20,
            "h3_size": 15,
            "body_size": 12,
            "caption_size": 10
        }
    },
    
    "Modern Tech": {
        "name": "Modern Tech",
        "description": "Modernes, technologieorientiertes Design",
        "color_scheme": "Modern Teal",
        "layout": {
            "cover_style": "geometric_design",
            "header_height": 2.2 * cm,
            "footer_height": 1.3 * cm,
            "margins": {
                "top": 2.2 * cm,
                "bottom": 2.2 * cm,
                "left": 2.0 * cm,
                "right": 2.0 * cm
            },
            "page_numbers": True,
            "watermark": False
        },
        "typography": {
            "main_font": "Helvetica",
            "heading_font": "Helvetica-Bold",
            "accent_font": "Helvetica-Oblique",
            "h1_size": 26,
            "h2_size": 19,
            "h3_size": 14,
            "body_size": 11,
            "caption_size": 9
        }
    }
}

def get_professional_template(template_name: str) -> Dict[str, Any]:
    """
    Gibt die Konfiguration für ein professionelles Template zurück.
    
    Args:
        template_name (str): Name des gewünschten Templates
        
    Returns:
        Dict[str, Any]: Template-Konfiguration mit Farben, Layout und Typography
    """
    if template_name not in PROFESSIONAL_TEMPLATES:
        template_name = "Executive Report"  # Fallback
    
    template = PROFESSIONAL_TEMPLATES[template_name].copy()
    color_scheme_name = template["color_scheme"]
    template["colors"] = PROFESSIONAL_COLOR_SCHEMES[color_scheme_name]
    
    return template

def get_all_professional_templates() -> List[str]:
    """
    Gibt eine Liste aller verfügbaren professionellen Template-Namen zurück.
    
    Returns:
        List[str]: Liste der Template-Namen
    """
    return list(PROFESSIONAL_TEMPLATES.keys())

def get_template_preview_info(template_name: str) -> Dict[str, str]:
    """
    Gibt Vorschau-Informationen für ein Template zurück.
    
    Args:
        template_name (str): Name des Templates
        
    Returns:
        Dict[str, str]: Informationen für die Vorschau
    """
    template = PROFESSIONAL_TEMPLATES.get(template_name, PROFESSIONAL_TEMPLATES["Executive Report"])
    color_scheme = PROFESSIONAL_COLOR_SCHEMES[template["color_scheme"]]
    
    return {
        "name": template["name"],
        "description": template["description"],
        "primary_color": color_scheme["primary"],
        "secondary_color": color_scheme["secondary"],
        "accent_color": color_scheme["accent"],
        "color_scheme_name": template["color_scheme"]
    }

def create_professional_cover_letter_template(
    template_name: str,
    customer_name: str = "{customer_name}",
    offer_id: str = "{offer_id}",
    company_name: str = "{company_name}",
    contact_person: str = "{contact_person}"
) -> str:
    """
    Erstellt ein professionelles Anschreiben basierend auf dem gewählten Template.
    
    Args:
        template_name (str): Name des Templates
        customer_name (str): Name des Kunden
        offer_id (str): Angebotsnummer
        company_name (str): Name des Unternehmens
        contact_person (str): Ansprechpartner
        
    Returns:
        str: Formatierter Anschreiben-Text
    """
    template = get_professional_template(template_name)
    
    if template_name == "Executive Report":
        return f"""
Sehr geehrte Damen und Herren von {customer_name},

im Namen von {company_name} danken wir Ihnen für das Vertrauen und die Gelegenheit, Ihnen unser professionelles Angebot vorlegen zu dürfen.

**Angebotsnummer: {offer_id}**

Als führender Anbieter im Bereich nachhaltiger Energielösungen haben wir eine maßgeschneiderte Photovoltaikanlage für Ihr Objekt konzipiert. Unser Angebot basiert auf einer detaillierten Analyse Ihrer Gegebenheiten und Anforderungen.

Die nachfolgenden Seiten enthalten eine umfassende Darstellung der geplanten Installation, einschließlich technischer Spezifikationen, Wirtschaftlichkeitsberechnung und erwarteter Umweltwirkung.

Gerne stehen wir Ihnen für Rückfragen und zur Terminvereinbarung persönlich zur Verfügung.

Mit freundlichen Grüßen

{contact_person}
{company_name}
"""
    
    elif template_name == "Solar Professional":
        return f"""
Liebe Kundin, lieber Kunde von {customer_name},

die Zukunft der Energie ist solar – und Sie sind dabei, ein Teil dieser Zukunft zu werden!

**Ihr persönliches Solarangebot: {offer_id}**

Unsere Experten von {company_name} haben für Sie eine hocheffiziente Photovoltaikanlage geplant, die optimal auf Ihre Bedürfnisse abgestimmt ist. Dabei stehen Qualität, Wirtschaftlichkeit und Umweltschutz im Mittelpunkt.

In diesem Angebot finden Sie:
• Detaillierte Anlagenplanung mit modernster Technologie
• Präzise Wirtschaftlichkeitsberechnung über 20 Jahre
• Umfassende Garantie- und Serviceleistungen
• Ihre persönliche CO₂-Bilanz

Lassen Sie uns gemeinsam Ihre Energieunabhängigkeit gestalten und einen wichtigen Beitrag zum Klimaschutz leisten.

Ihr Solar-Team
{contact_person}
{company_name}
"""
    
    elif template_name == "Premium Minimal":
        return f"""
Sehr geehrte Damen und Herren,

Angebot {offer_id}

Mit diesem Schreiben übermitteln wir Ihnen unser exklusives Angebot für eine Premium-Photovoltaikanlage.

Unser Unternehmen {company_name} steht für höchste Qualitätsstandards und individuelle Lösungen im Bereich erneuerbarer Energien.

Die vorgeschlagene Anlage wurde sorgfältig auf Ihre spezifischen Anforderungen abgestimmt und verspricht optimale Erträge bei minimaler Wartung.

Wir freuen uns auf Ihre Rückmeldung.

{contact_person}
{company_name}
"""
    
    else:  # Modern Tech
        return f"""
Hallo {customer_name}!

**Solar Innovation für Ihr Zuhause – Angebot {offer_id}**

Willkommen in der Zukunft der Energiegewinnung! {company_name} präsentiert Ihnen eine intelligente Photovoltaiklösung, die Technologie und Nachhaltigkeit perfekt vereint.

**Was Sie erwartet:**
→ Modernste Solartechnologie mit höchster Effizienz
→ Smart-Home Integration für optimalen Eigenverbrauch
→ Transparente Kostenkalkulation und ROI-Berechnung
→ Nachhaltiger Beitrag zur Energiewende

Unser interdisziplinäres Team hat eine Lösung entwickelt, die nicht nur Ihre Stromkosten reduziert, sondern auch Ihren ökologischen Fußabdruck minimiert.

Bereit für die Energierevolution?

{contact_person}
{company_name} – Ihr Partner für intelligente Energielösungen
"""

def create_professional_project_summary_template(template_name: str) -> str:
    """
    Erstellt eine professionelle Projektzusammenfassung basierend auf dem gewählten Template.
    
    Args:
        template_name (str): Name des Templates
        
    Returns:
        str: Formatierte Projektzusammenfassung
    """
    template = get_professional_template(template_name)
    
    if template_name == "Executive Report":
        return """
**PROJEKTZUSAMMENFASSUNG**

Gegenstand dieses Angebots ist die Planung, Lieferung und Installation einer hochmodernen Photovoltaikanlage inklusive optionaler Energiespeicherlösung und Elektromobilitäts-Infrastruktur.

**Projektumfang:**
• Detaillierte Standortanalyse und Ertragsberechnung
• Premium-Komponenten von zertifizierten Herstellern
• Professionelle Installation durch qualifizierte Fachkräfte
• Umfassende Garantie- und Serviceleistungen
• Unterstützung bei Fördermittelanträgen

**Projektziele:**
• Maximierung der Energieunabhängigkeit
• Optimierung der Betriebskosten
• Minimierung der CO₂-Emissionen
• Steigerung des Immobilienwerts

Alle vorgeschlagenen Komponenten entsprechen höchsten Qualitätsstandards und gewährleisten eine langfristige, wirtschaftliche Energieversorgung.
"""
    
    elif template_name == "Solar Professional":
        return """
**IHR WEG ZUR SOLARENERGIE**

Diese umfassende Photovoltaiklösung wurde speziell für Ihre Bedürfnisse entwickelt und kombiniert neueste Technologie mit bewährter Qualität.

**Ihre Vorteile auf einen Blick:**
🔹 Hocheffiziente Solarmodule mit erstklassiger Leistungsgarantie
🔹 Intelligenter Wechselrichter für optimale Energieausbeute
🔹 Optional: Batteriespeicher für maximale Unabhängigkeit
🔹 Optional: Wallbox für umweltfreundliche Elektromobilität

**Unser Versprechen:**
• Turnkey-Lösung: Alles aus einer Hand
• Qualitätskomponenten mit Langzeitgarantie
• Professionelle Installation und Inbetriebnahme
• Persönlicher Service und Betreuung

Mit dieser Anlage investieren Sie nicht nur in Ihre finanzielle Zukunft, sondern leisten auch einen wertvollen Beitrag zum Umweltschutz.
"""
    
    elif template_name == "Premium Minimal":
        return """
**Photovoltaikanlage Premium**

Exklusive Energielösung für anspruchsvolle Kunden.

Diese Anlage vereint höchste technische Standards mit ästhetischem Design und gewährleistet optimale Energieausbeute bei minimaler Wartung.

Komponenten ausgewählter Premiumhersteller garantieren Langlebigkeit und Effizienz.

Installation durch zertifizierte Spezialisten.

Umfassende Garantieleistungen inklusive.
"""
    
    else:  # Modern Tech
        return """
**SMART SOLAR SYSTEM 2025**

Intelligente Photovoltaiklösung der nächsten Generation

**Tech-Features:**
• AI-optimierte Ertragsvorhersage
• Cloud-basiertes Monitoring
• Smart-Grid Kompatibilität
• IoT-Integration

**Innovation trifft Nachhaltigkeit:**
Diese Anlage nutzt modernste Technologien für maximale Effizienz und bietet Ihnen vollständige Transparenz über Ihre Energieproduktion und -verbrauch.

**Connected Energy:**
Vernetzte Komponenten ermöglichen intelligentes Energiemanagement und automatische Optimierung für höchste Rentabilität.

Die Zukunft der Energie ist smart, vernetzt und nachhaltig.
"""

# Hilfsfunktionen für die Integration mit dem bestehenden System
def integrate_with_existing_templates():
    """
    Integriert die professionellen Templates mit dem bestehenden Template-System.
    Erweitert die verfügbaren Optionen ohne bestehende Funktionalität zu beeinträchtigen.
    """
    if _EXISTING_TEMPLATES_AVAILABLE:
        # Erweitere bestehende Templates um professionelle Optionen
        pass
    
    return True

def get_template_color_preview(template_name: str) -> Dict[str, str]:
    """
    Gibt Farbinformationen für die Vorschau in der UI zurück.
    
    Args:
        template_name (str): Name des Templates
        
    Returns:
        Dict[str, str]: Farben für die Vorschau
    """
    template = get_professional_template(template_name)
    colors = template["colors"]
    
    return {
        "primary": colors["primary"],
        "secondary": colors["secondary"],
        "accent": colors["accent"],
        "background": colors["background"]
    }
