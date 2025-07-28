# pdf_professional_ui.py
# -*- coding: utf-8 -*-
"""
pdf_professional_ui.py

Professionelle UI-Erweiterungen für die PDF-Template-Auswahl.
Erweitert das bestehende UI-System um moderne Template-Optionen und Vorschaufunktionen.

Basiert auf: pdf_ui.py, pdf_widgets.py
Erweitert um: Template-Auswahl, Farbvorschau, Live-Preview-Funktionen

Author: GitHub Copilot (Erweiterung des bestehenden Systems)
Version: 1.0 - Professionelle UI-Erweiterung
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import hex2color

# Importiere bestehende Module (falls verfügbar)
try:
    from pdf_ui import *  # Bestehende UI-Funktionen bleiben verfügbar
    from pdf_widgets import *  # Bestehende Widgets bleiben verfügbar
    from pdf_professional_templates import (
        get_professional_template,
        get_all_professional_templates,
        get_template_preview_info,
        get_template_color_preview
    )
    from pdf_styles import (
        get_professional_color_palette,
        get_professional_paragraph_styles,
        PROFESSIONAL_COLOR_PALETTES,
        ColorScheme,
        PDFVisualEnhancer,
        PDFThemeManager,
        ProfessionalPDFBackgrounds
    )
    _EXISTING_UI_AVAILABLE = True
except ImportError:
    _EXISTING_UI_AVAILABLE = False
    
    # Fallback-Klassen für den Fall, dass pdf_styles nicht verfügbar ist
    class ColorScheme:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def to_dict(self):
            return self.__dict__
    
    class PDFVisualEnhancer:
        def __init__(self):
            pass
    
    class PDFThemeManager:
        def __init__(self):
            pass
    
    class ProfessionalPDFBackgrounds:
        def __init__(self):
            pass

# PDF-Widgets Integration
try:
    from pdf_widgets import PDFSectionManager, render_pdf_structure_manager
    _PDF_WIDGETS_AVAILABLE = True
except ImportError:
    _PDF_WIDGETS_AVAILABLE = False
    
    class PDFSectionManager:
        def __init__(self):
            pass
        def render_drag_drop_interface(self, texts):
            st.info("PDF-Widgets nicht verfügbar")
    
    def render_pdf_structure_manager(texts):
        st.info("PDF-Struktur-Manager nicht verfügbar")

def render_professional_template_selector() -> str:
    """
    Erweiterte Template-Auswahl mit professionellen Optionen.
    Ergänzt die bestehende Template-Auswahl um moderne Designs.
    
    Returns:
        str: Name des ausgewählten Templates
    """
    st.markdown("### 🎨 Professionelle PDF-Templates")
    
    # Hole alle verfügbaren Templates
    try:
        professional_templates = get_all_professional_templates()
    except:
        professional_templates = ["Executive Report", "Solar Professional", "Premium Minimal", "Modern Tech"]
    
    # Template-Auswahl mit Vorschau
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_template = st.selectbox(
            "Wählen Sie ein professionelles Design:",
            professional_templates,
            index=0,
            help="Verschiedene professionelle Layouts für unterschiedliche Zielgruppen"
        )
        
        # Template-Beschreibung anzeigen
        try:
            template_info = get_template_preview_info(selected_template)
            st.write(f"**{template_info['name']}**")
            st.write(template_info['description'])
        except:
            st.write("Professionelles Template für Ihre PDF-Ausgabe")
    
    with col2:
        # Farbvorschau anzeigen
        render_color_preview(selected_template)
    
    return selected_template

def render_color_preview(template_name: str):
    """
    Zeigt eine Farbvorschau für das gewählte Template.
    Neue Funktion zur visuellen Darstellung der Farbpalette.
    
    Args:
        template_name (str): Name des Templates
    """
    try:
        colors = get_template_color_preview(template_name)
        
        # Erstelle Farbvorschau-Grafik
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1)
        
        # Farbblöcke zeichnen
        color_names = ['primary', 'secondary', 'accent', 'background']
        for i, color_name in enumerate(color_names):
            if color_name in colors:
                rect = patches.Rectangle((i, 0), 1, 1, 
                                       facecolor=colors[color_name], 
                                       edgecolor='white', 
                                       linewidth=1)
                ax.add_patch(rect)
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Farbpalette", fontsize=10)
        ax.axis('off')
        
        st.pyplot(fig, use_container_width=True)
        plt.close()
        
    except Exception as e:
        st.write("Farbvorschau nicht verfügbar")

def render_professional_customization_panel(selected_template: str) -> Dict[str, Any]:
    """
    Erweiterte Anpassungsoptionen für professionelle Templates.
    Ergänzt bestehende Anpassungsoptionen um professionelle Features.
    
    Args:
        selected_template (str): Name des ausgewählten Templates
        
    Returns:
        Dict[str, Any]: Anpassungsoptionen für das Template
    """
    st.markdown("### ⚙️ Template-Anpassungen")
    
    customizations = {}
    
    # Layout-Optionen
    with st.expander("📐 Layout-Optionen", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            customizations['include_cover_page'] = st.checkbox(
                "Deckblatt hinzufügen", 
                value=True,
                help="Professionelles Deckblatt mit Firmenlogo und Titel"
            )
            
            customizations['include_table_of_contents'] = st.checkbox(
                "Inhaltsverzeichnis", 
                value=False,
                help="Automatisches Inhaltsverzeichnis für umfangreiche Dokumente"
            )
            
        with col2:
            customizations['page_numbers'] = st.checkbox(
                "Seitenzahlen", 
                value=True,
                help="Seitennummerierung im Footer"
            )
            
            customizations['watermark'] = st.checkbox(
                "Wasserzeichen", 
                value=False,
                help="Dezentes Firmenwasserzeichen im Hintergrund"
            )
    
    # Inhalts-Module
    with st.expander("📋 Inhalts-Module", expanded=True):
        st.write("Wählen Sie die Inhalte für Ihr PDF:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customizations['include_executive_summary'] = st.checkbox(
                "Zusammenfassung", 
                value=True,
                help="Kurze Projektzusammenfassung auf der ersten Seite"
            )
            
            customizations['include_technical_details'] = st.checkbox(
                "Technische Details", 
                value=True,
                help="Detaillierte technische Spezifikationen"
            )
            
            customizations['include_financial_analysis'] = st.checkbox(
                "Wirtschaftlichkeitsanalyse", 
                value=True,
                help="Kosten-Nutzen-Analyse und ROI-Berechnung"
            )
            
        with col2:
            customizations['include_charts'] = st.checkbox(
                "Diagramme und Grafiken", 
                value=True,
                help="Visuelle Darstellung von Ertrag und Einsparungen"
            )
            
            customizations['include_environmental_impact'] = st.checkbox(
                "Umweltwirkung", 
                value=True,
                help="CO₂-Einsparung und Nachhaltigkeitsaspekte"
            )
            
            customizations['include_appendix'] = st.checkbox(
                "Anhänge", 
                value=False,
                help="Zusätzliche Dokumente und Datenblätter"
            )
    
    # Stil-Anpassungen
    with st.expander("🎨 Stil-Anpassungen", expanded=False):
        customizations['custom_logo'] = st.file_uploader(
            "Eigenes Logo hochladen",
            type=['png', 'jpg', 'jpeg'],
            help="Ersetzen Sie das Standard-Logo durch Ihr eigenes (empfohlen: PNG mit transparentem Hintergrund)"
        )
        
        customizations['company_colors'] = st.checkbox(
            "Firmenfarben verwenden",
            value=False,
            help="Passen Sie die Farbpalette an Ihre Corporate Identity an"
        )
        
        if customizations['company_colors']:
            col1, col2 = st.columns(2)
            with col1:
                customizations['primary_color'] = st.color_picker(
                    "Primärfarbe",
                    value="#1e3a8a",
                    help="Hauptfarbe für Überschriften und Akzente"
                )
            with col2:
                customizations['secondary_color'] = st.color_picker(
                    "Sekundärfarbe",
                    value="#3b82f6",
                    help="Ergänzende Farbe für Highlights"
                )
    
    return customizations

def render_professional_preview_panel(template_name: str, customizations: Dict[str, Any]):
    """
    Erweiterte Vorschau für professionelle Templates.
    Zeigt eine realistische Vorschau des konfigurierten PDFs.
    
    Args:
        template_name (str): Name des Templates
        customizations (Dict[str, Any]): Anpassungsoptionen
    """
    st.markdown("### 👀 Live-Vorschau")
    
    try:
        # Erstelle Mock-Vorschau
        preview_image = create_template_mockup(template_name, customizations)
        
        if preview_image:
            st.image(preview_image, caption=f"Vorschau: {template_name}", use_column_width=True)
        else:
            st.info("Vorschau wird generiert...")
            
    except Exception as e:
        st.warning("Vorschau temporär nicht verfügbar. Das finale PDF wird korrekt erstellt.")

def create_template_mockup(template_name: str, customizations: Dict[str, Any]) -> Optional[Image.Image]:
    """
    Erstellt eine Mock-Vorschau des Templates.
    Neue Funktion zur visuellen Darstellung der Template-Konfiguration.
    
    Args:
        template_name (str): Name des Templates
        customizations (Dict[str, Any]): Anpassungsoptionen
        
    Returns:
        Optional[Image.Image]: Vorschau-Bild oder None
    """
    try:
        # Erstelle ein Mock-PDF-Layout
        img_width, img_height = 400, 565  # A4 Verhältnis
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Hole Template-Farben
        try:
            colors = get_template_color_preview(template_name)
            primary_color = colors.get('primary', '#1e3a8a')
            secondary_color = colors.get('secondary', '#3b82f6')
        except:
            primary_color = '#1e3a8a'
            secondary_color = '#3b82f6'
        
        # Zeichne Header
        if customizations.get('include_cover_page', True):
            draw.rectangle([0, 0, img_width, 80], fill=primary_color)
            draw.text((20, 30), f"PDF Template: {template_name}", fill='white')
        
        # Zeichne Content-Bereiche
        y_pos = 100
        if customizations.get('include_executive_summary', True):
            draw.rectangle([20, y_pos, img_width-20, y_pos+40], outline=secondary_color, width=2)
            draw.text((30, y_pos+10), "Zusammenfassung", fill='black')
            y_pos += 60
        
        if customizations.get('include_technical_details', True):
            draw.rectangle([20, y_pos, img_width-20, y_pos+60], outline=secondary_color, width=2)
            draw.text((30, y_pos+10), "Technische Details", fill='black')
            y_pos += 80
        
        if customizations.get('include_financial_analysis', True):
            draw.rectangle([20, y_pos, img_width-20, y_pos+80], outline=secondary_color, width=2)
            draw.text((30, y_pos+10), "Wirtschaftlichkeitsanalyse", fill='black')
            y_pos += 100
        
        if customizations.get('include_charts', True):
            draw.rectangle([20, y_pos, img_width-20, y_pos+60], outline=secondary_color, width=2)
            draw.text((30, y_pos+10), "Diagramme", fill='black')
        
        # Footer
        if customizations.get('page_numbers', True):
            draw.text((img_width-50, img_height-30), "Seite 1", fill='gray')
        
        return img
        
    except Exception as e:
        return None

def render_professional_template_ui():
    """
    Hauptfunktion für die professionelle Template-UI.
    Integriert alle Komponenten in eine benutzerfreundliche Oberfläche.
    Erweitert die bestehende UI ohne sie zu beeinträchtigen.
    """
    st.markdown("## 📄 Professionelle PDF-Konfiguration")
    st.markdown("---")
    
    # Erweiterte UI-Modi
    ui_mode = st.radio(
        "Konfigurationsmodus:",
        ["🎨 Template-Design", "📋 Struktur-Manager", "🔧 Erweiterte Einstellungen"],
        horizontal=True
    )
    
    if ui_mode == "🎨 Template-Design":
        return render_template_design_mode()
    elif ui_mode == "📋 Struktur-Manager":
        return render_structure_manager_mode()
    else:
        return render_advanced_settings_mode()

def render_template_design_mode():
    """Template-Design-Modus mit erweiterten Optionen."""
    
    # Template-Auswahl
    selected_template = render_professional_template_selector()
    
    st.markdown("---")
    
    # Theme-Manager Integration
    if _EXISTING_UI_AVAILABLE:
        theme_manager = PDFThemeManager()
        render_theme_manager_interface(theme_manager, selected_template)
    
    st.markdown("---")
    
    # Anpassungsoptionen
    customizations = render_professional_customization_panel(selected_template)
    
    st.markdown("---")
    
    # Vorschau
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_professional_preview_panel(selected_template, customizations)
    
    with col2:
        st.markdown("### 📋 Konfiguration")
        st.json({
            "template": selected_template,
            "aktive_module": [k for k, v in customizations.items() if v is True],
            "anpassungen": len([k for k, v in customizations.items() if v is not True and v is not False])
        })
        
        if st.button("🚀 PDF generieren", type="primary"):
            st.success("PDF-Generierung gestartet!")
            return selected_template, customizations
    
    return selected_template, customizations

def render_structure_manager_mode():
    """Struktur-Manager-Modus mit PDF-Widgets Integration."""
    
    if _PDF_WIDGETS_AVAILABLE:
        # Verwende PDF-Widgets für erweiterte Strukturverwaltung
        texts = {"menu_item_doc_output": "PDF-Ausgabe"}  # Fallback-Texte
        render_pdf_structure_manager(texts)
        
        # Rückgabe der konfigurierten Struktur
        if hasattr(st.session_state, 'pdf_section_order'):
            customizations = {
                'section_order': st.session_state.pdf_section_order,
                'section_contents': getattr(st.session_state, 'pdf_section_contents', {}),
                'structure_mode': True
            }
            return "Custom Structure", customizations
    else:
        st.warning("PDF-Widgets nicht verfügbar. Verwende Basis-Strukturmanager.")
        return render_basic_structure_manager()
    
    return "Standard", {}

def render_basic_structure_manager():
    """Basis-Strukturmanager als Fallback."""
    st.markdown("### 📋 Basis PDF-Struktur")
    
    # Einfache Sektionsauswahl
    sections = {
        'cover_page': '📄 Deckblatt',
        'summary': '📋 Zusammenfassung', 
        'technical': '⚙️ Technische Details',
        'financial': '💰 Wirtschaftlichkeit',
        'charts': '📊 Diagramme',
        'environmental': '🌱 Umweltwirkung'
    }
    
    selected_sections = st.multiselect(
        "Wählen Sie die PDF-Abschnitte:",
        options=list(sections.keys()),
        default=['cover_page', 'summary', 'technical', 'financial'],
        format_func=lambda x: sections[x]
    )
    
    # Reihenfolge anpassen
    if len(selected_sections) > 1:
        st.markdown("**Reihenfolge anpassen:**")
        reordered_sections = []
        for i, section in enumerate(selected_sections):
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                st.write(f"{i+1}.")
            with col2:
                st.write(sections[section])
            with col3:
                if i > 0 and st.button("⬆️", key=f"up_{i}"):
                    selected_sections[i], selected_sections[i-1] = selected_sections[i-1], selected_sections[i]
                    st.rerun()
            with col4:
                if i < len(selected_sections)-1 and st.button("⬇️", key=f"down_{i}"):
                    selected_sections[i], selected_sections[i+1] = selected_sections[i+1], selected_sections[i]
                    st.rerun()
    
    customizations = {
        'selected_sections': selected_sections,
        'basic_structure': True
    }
    
    return "Basic Structure", customizations

def render_advanced_settings_mode():
    """Erweiterte Einstellungen mit Theme-Manager und Visual-Enhancer."""
    
    st.markdown("### 🔧 Erweiterte PDF-Einstellungen")
    
    # Theme Manager Integration
    if _EXISTING_UI_AVAILABLE:
        st.markdown("#### 🎨 Theme-Manager")
        theme_manager = PDFThemeManager()
        render_advanced_theme_settings(theme_manager)
        
        st.markdown("---")
        
        # Visual Enhancer Integration
        st.markdown("#### ✨ Visual-Enhancer")
        visual_enhancer = PDFVisualEnhancer()
        render_visual_enhancer_settings(visual_enhancer)
        
        st.markdown("---")
        
        # Background Manager
        st.markdown("#### 🖼️ Hintergrund-Manager")
        bg_manager = ProfessionalPDFBackgrounds()
        render_background_settings(bg_manager)
    
    customizations = {
        'advanced_mode': True,
        'theme_settings': st.session_state.get('theme_settings', {}),
        'visual_settings': st.session_state.get('visual_settings', {}),
        'background_settings': st.session_state.get('background_settings', {})
    }
    
    return "Advanced", customizations

def render_theme_manager_interface(theme_manager: PDFThemeManager, selected_template: str):
    """Rendert die Theme-Manager-Oberfläche."""
    
    st.markdown("#### 🎨 Theme-Verwaltung")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Verfügbare Themes anzeigen
        try:
            available_themes = theme_manager.get_all_available_themes()
            current_theme = st.selectbox(
                "Theme auswählen:",
                options=available_themes,
                index=0 if selected_template not in available_themes else available_themes.index(selected_template)
            )
        except:
            current_theme = selected_template
        
        # Theme-Details anzeigen
        try:
            theme_config = theme_manager.get_professional_theme(current_theme)
            
            with st.expander("Theme-Details anzeigen"):
                st.json(theme_config)
        except:
            st.info("Theme-Details werden geladen...")
    
    with col2:
        # Custom Color Scheme erstellen
        st.markdown("**Custom Farben:**")
        
        custom_primary = st.color_picker("Primärfarbe", value="#1e3a8a")
        custom_secondary = st.color_picker("Sekundärfarbe", value="#3b82f6")
        custom_accent = st.color_picker("Akzentfarbe", value="#06b6d4")
        
        if st.button("🎨 Custom Theme erstellen"):
            custom_scheme = ColorScheme(
                primary=custom_primary,
                secondary=custom_secondary,
                accent=custom_accent,
                background="#ffffff",
                text="#1f2937",
                success="#10b981",
                warning="#f59e0b",
                error="#ef4444"
            )
            
            st.session_state.custom_color_scheme = custom_scheme.to_dict()
            st.success("Custom Theme erstellt!")

def render_advanced_theme_settings(theme_manager: PDFThemeManager):
    """Erweiterte Theme-Einstellungen."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Typography-Einstellungen:**")
        
        font_family = st.selectbox(
            "Schriftfamilie:",
            ["Helvetica", "Times", "Courier"],
            key="theme_font_family"
        )
        
        base_font_size = st.slider(
            "Basis-Schriftgröße:",
            min_value=8,
            max_value=16,
            value=11,
            key="theme_base_font_size"
        )
        
        line_spacing = st.slider(
            "Zeilenabstand:",
            min_value=1.0,
            max_value=2.0,
            value=1.4,
            step=0.1,
            key="theme_line_spacing"
        )
    
    with col2:
        st.markdown("**Layout-Einstellungen:**")
        
        margin_style = st.selectbox(
            "Rand-Stil:",
            ["Standard", "Breit", "Schmal", "Asymmetrisch"],
            key="theme_margin_style"
        )
        
        header_style = st.selectbox(
            "Header-Stil:",
            ["Standard", "Minimal", "Erweitert"],
            key="theme_header_style"
        )
        
        page_orientation = st.selectbox(
            "Seitenausrichtung:",
            ["Hochformat", "Querformat"],
            key="theme_page_orientation"
        )
    
    # Theme-Einstellungen speichern
    theme_settings = {
        'font_family': font_family,
        'base_font_size': base_font_size,
        'line_spacing': line_spacing,
        'margin_style': margin_style,
        'header_style': header_style,
        'page_orientation': page_orientation
    }
    
    st.session_state.theme_settings = theme_settings

def render_visual_enhancer_settings(visual_enhancer: PDFVisualEnhancer):
    """Visual-Enhancer-Einstellungen."""
    
    st.markdown("**Visuelle Verbesserungen:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_shadows = st.checkbox("Schatten aktivieren", value=False, key="visual_shadows")
        enable_gradients = st.checkbox("Farbverläufe aktivieren", value=True, key="visual_gradients")
        enable_rounded_corners = st.checkbox("Abgerundete Ecken", value=True, key="visual_rounded")
        
    with col2:
        chart_style = st.selectbox(
            "Diagramm-Stil:",
            ["Modern", "Klassisch", "Minimal", "Vibrant"],
            key="visual_chart_style"
        )
        
        icon_style = st.selectbox(
            "Icon-Stil:",
            ["Filled", "Outlined", "Rounded"],
            key="visual_icon_style"
        )
        
        animation_level = st.selectbox(
            "Animations-Level:",
            ["Keine", "Minimal", "Standard", "Erweitert"],
            key="visual_animation_level"
        )
    
    # Visual-Einstellungen speichern
    visual_settings = {
        'shadows': enable_shadows,
        'gradients': enable_gradients,
        'rounded_corners': enable_rounded_corners,
        'chart_style': chart_style,
        'icon_style': icon_style,
        'animation_level': animation_level
    }
    
    st.session_state.visual_settings = visual_settings

def render_background_settings(bg_manager: ProfessionalPDFBackgrounds):
    """Hintergrund-Einstellungen."""
    
    st.markdown("**Hintergrund-Optionen:**")
    
    background_type = st.selectbox(
        "Hintergrund-Typ:",
        ["Einfarbig", "Verlauf", "Muster", "Bild", "Wasserzeichen"],
        key="bg_type"
    )
    
    if background_type == "Einfarbig":
        bg_color = st.color_picker("Hintergrundfarbe:", value="#ffffff", key="bg_color")
        bg_settings = {'type': 'solid', 'color': bg_color}
        
    elif background_type == "Verlauf":
        col1, col2 = st.columns(2)
        with col1:
            gradient_start = st.color_picker("Start-Farbe:", value="#ffffff", key="gradient_start")
        with col2:
            gradient_end = st.color_picker("End-Farbe:", value="#f8fafc", key="gradient_end")
        
        gradient_direction = st.selectbox(
            "Verlaufs-Richtung:",
            ["Vertikal", "Horizontal", "Diagonal"],
            key="gradient_direction"
        )
        
        bg_settings = {
            'type': 'gradient',
            'start_color': gradient_start,
            'end_color': gradient_end,
            'direction': gradient_direction
        }
        
    elif background_type == "Wasserzeichen":
        watermark_text = st.text_input("Wasserzeichen-Text:", key="watermark_text")
        watermark_opacity = st.slider("Transparenz:", 0.0, 1.0, 0.1, key="watermark_opacity")
        
        bg_settings = {
            'type': 'watermark',
            'text': watermark_text,
            'opacity': watermark_opacity
        }
        
    else:
        bg_settings = {'type': 'none'}
    
    st.session_state.background_settings = bg_settings

def render_template_comparison():
    """
    Vergleichsansicht verschiedener Templates.
    Neue Funktion zur Gegenüberstellung der verfügbaren Designs.
    """
    st.markdown("### 🔍 Template-Vergleich")
    
    try:
        templates = get_all_professional_templates()
    except:
        templates = ["Executive Report", "Solar Professional", "Premium Minimal", "Modern Tech"]
    
    # Auswahl von bis zu 3 Templates zum Vergleich
    selected_templates = st.multiselect(
        "Wählen Sie bis zu 3 Templates zum Vergleich:",
        templates,
        default=templates[:3] if len(templates) >= 3 else templates,
        max_selections=3
    )
    
    if selected_templates:
        cols = st.columns(len(selected_templates))
        
        for i, template in enumerate(selected_templates):
            with cols[i]:
                st.markdown(f"**{template}**")
                
                # Template-Info
                try:
                    info = get_template_preview_info(template)
                    st.write(info['description'])
                    
                    # Farbvorschau
                    render_color_preview(template)
                    
                except:
                    st.write("Professionelles Template")
                
                # Mock-Vorschau
                try:
                    mock_customizations = {
                        'include_cover_page': True,
                        'include_executive_summary': True,
                        'include_technical_details': True,
                        'page_numbers': True
                    }
                    preview = create_template_mockup(template, mock_customizations)
                    if preview:
                        st.image(preview, use_column_width=True)
                except:
                    st.info("Vorschau wird geladen...")

# --- INTEGRATION MIT BESTEHENDEM SYSTEM ---

def integrate_professional_ui_with_existing():
    """
    Integriert die professionelle UI mit dem bestehenden System.
    Stellt sicher, dass alle bestehenden Funktionen weiterhin verfügbar sind.
    """
    if _EXISTING_UI_AVAILABLE:
        # Bestehende UI-Funktionen bleiben unverändert verfügbar
        # Neue professionelle Funktionen werden als Ergänzung angeboten
        pass
    
    return True

# Beispiel für erweiterte Integration
def render_enhanced_pdf_ui():
    """
    Erweiterte PDF-UI, die bestehende und neue Funktionen kombiniert.
    """
    st.sidebar.markdown("### PDF-Optionen")
    
    ui_mode = st.sidebar.radio(
        "UI-Modus wählen:",
        ["Standard", "Professionell", "Vergleich"],
        index=1
    )
    
    if ui_mode == "Standard" and _EXISTING_UI_AVAILABLE:
        # Verwende bestehende UI-Funktionen
        st.info("Standard-UI wird geladen...")
        
    elif ui_mode == "Professionell":
        # Verwende neue professionelle UI
        return render_professional_template_ui()
        
    elif ui_mode == "Vergleich":
        # Zeige Template-Vergleich
        render_template_comparison()
        return None, {}
    
    return None, {}
