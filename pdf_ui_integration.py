# pdf_ui_integration.py
# -*- coding: utf-8 -*-
"""
pdf_ui_integration.py

Integration der professionellen PDF-Templates in das bestehende UI-System.
Erweitert pdf_ui.py um professionelle Template-Optionen ohne die bestehende Funktionalität zu beeinträchtigen.

Basiert auf: pdf_ui.py
Erweitert um: Professionelle Template-Auswahl, erweiterte Anpassungsoptionen

Author: GitHub Copilot (Erweiterung des bestehenden Systems)
Version: 1.0 - UI-Integration für professionelle Templates
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import base64
import traceback
import os
import json

# Importiere bestehende UI-Module
try:
    from pdf_ui import render_pdf_ui, get_text_pdf_ui
    _EXISTING_PDF_UI_AVAILABLE = True
except ImportError:
    _EXISTING_PDF_UI_AVAILABLE = False
    
    # Fallback-Funktionen
    def render_pdf_ui(*args, **kwargs):
        st.error("Bestehende PDF-UI nicht verfügbar")
        return None
    
    def get_text_pdf_ui(texts_dict, key, fallback=None):
        return fallback or key

# Importiere professionelle Module
try:
    from pdf_professional_ui import (
        render_professional_template_selector,
        render_professional_customization_panel,
        render_professional_preview_panel,
        render_template_comparison,
        render_professional_template_ui
    )
    from pdf_generator_professional import create_professional_pdf_with_template
    from pdf_professional_templates import get_all_professional_templates
    from pdf_widgets import PDFSectionManager
    from pdf_styles import PDFThemeManager, PDFVisualEnhancer, ColorScheme
    _PROFESSIONAL_UI_AVAILABLE = True
except ImportError:
    _PROFESSIONAL_UI_AVAILABLE = False
    
    # Fallback-Funktionen
    def render_professional_template_selector():
        return "Standard"
    
    def render_professional_customization_panel(template):
        return {}
    
    def render_professional_preview_panel(template, customizations):
        pass
    
    def render_template_comparison():
        pass
    
    def render_professional_template_ui():
        return "Standard", {}
    
    def create_professional_pdf_with_template(*args, **kwargs):
        raise Exception("Professionelle PDF-Generierung nicht verfügbar")
    
    def get_all_professional_templates():
        return ["Standard"]
    
    # Fallback-Klassen
    class PDFSectionManager:
        def __init__(self): pass
        def initialize_session_state(self): pass
        def render_drag_drop_interface(self, texts): pass
    
    class PDFThemeManager:
        def __init__(self): pass
        def get_professional_theme(self, name): return {}
    
    class PDFVisualEnhancer:
        def __init__(self): pass
    
    class ColorScheme:
        def __init__(self, **kwargs): pass

def render_enhanced_pdf_ui(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]] = None,
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]] = None
):
    """
    Erweiterte PDF-UI, die bestehende und professionelle Funktionen kombiniert.
    Ersetzt render_pdf_ui als Haupteingangspunkt mit erweiterten Optionen.
    
    Args:
        Alle Parameter wie bei render_pdf_ui
    """
    
    # Header mit erweiterten Optionen
    st.header(get_text_pdf_ui(texts, "menu_item_doc_output", "Professionelle PDF-Ausgabe"))
    
    # UI-Modus-Auswahl in der Sidebar
    with st.sidebar:
        st.markdown("### 🎨 PDF-Design-Optionen")
        
        ui_mode = st.radio(
            "Design-Modus wählen:",
            ["🔧 Standard-UI", "⭐ Professionelle Templates", "🧩 Widget-Struktur", "🔍 Template-Vergleich"],
            index=1 if _PROFESSIONAL_UI_AVAILABLE else 0,
            help="Wählen Sie zwischen der klassischen PDF-Erstellung und den neuen professionellen Templates"
        )
        
        # Schnellzugriff auf häufige Einstellungen
        st.markdown("---")
        st.markdown("### ⚡ Schnelleinstellungen")
        
        quick_cover_page = st.checkbox("✅ Deckblatt hinzufügen", value=True)
        quick_charts = st.checkbox("📊 Diagramme einbinden", value=True)
        quick_environmental = st.checkbox("🌱 Umweltwirkung zeigen", value=True)
        
        # Erweiterte Optionen
        st.markdown("---")
        st.markdown("### 🎯 Erweiterte Optionen")
        
        enable_visual_enhancements = st.checkbox("🎨 Visual Enhancements", value=True)
        enable_custom_themes = st.checkbox("🌈 Benutzerdefinierte Themes", value=False)
        enable_background_effects = st.checkbox("🖼️ Hintergrund-Effekte", value=False)
    
    # Haupt-UI basierend auf gewähltem Modus
    if ui_mode == "🔧 Standard-UI" and _EXISTING_PDF_UI_AVAILABLE:
        st.info("💡 **Standard-Modus**: Bewährte PDF-Erstellung mit allen bekannten Funktionen")
        
        # Erweitere die Standard-UI um einige professionelle Optionen
        with st.expander("🎨 Zusätzliche Design-Optionen", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                enhanced_colors = st.checkbox(
                    "Erweiterte Farbpalette verwenden",
                    value=False,
                    help="Nutzt professionelle Farbkombinationen für ein moderneres Aussehen"
                )
                
            with col2:
                enhanced_typography = st.checkbox(
                    "Verbesserte Typografie",
                    value=False,
                    help="Optimiert Schriftgrößen und -abstände für bessere Lesbarkeit"
                )
        
        # Rufe bestehende UI auf
        result = render_pdf_ui(
            texts, project_data, analysis_results,
            load_admin_setting_func, save_admin_setting_func,
            list_products_func, get_product_by_id_func,
            get_active_company_details_func, db_list_company_documents_func
        )
        
        return result
        
    elif ui_mode == "⭐ Professionelle Templates" and _PROFESSIONAL_UI_AVAILABLE:
        st.success("🌟 **Professioneller Modus**: Moderne Templates mit erweiterten Design-Optionen")
        
        return render_professional_pdf_interface(
            texts, project_data, analysis_results,
            load_admin_setting_func, save_admin_setting_func,
            list_products_func, get_product_by_id_func,
            get_active_company_details_func, db_list_company_documents_func,
            quick_cover_page, quick_charts, quick_environmental,
            enable_visual_enhancements, enable_custom_themes, enable_background_effects
        )
        
    elif ui_mode == "🧩 Widget-Struktur":
        st.info("🧩 **Widget-Modus**: Erweiterte Strukturverwaltung mit Drag & Drop")
        
        return render_widget_based_pdf_interface(
            texts, project_data, analysis_results,
            load_admin_setting_func, save_admin_setting_func,
            list_products_func, get_product_by_id_func,
            get_active_company_details_func, db_list_company_documents_func,
            quick_cover_page, quick_charts, quick_environmental,
            enable_visual_enhancements, enable_custom_themes, enable_background_effects
        )
        
    elif ui_mode == "🔍 Template-Vergleich":
        st.info("🔍 **Vergleichs-Modus**: Vergleichen Sie verschiedene Templates")
        render_template_comparison()
        return None
        
    else:
        st.warning("⚠️ Gewählter Modus nicht verfügbar. Fallback auf Standard-Funktionen.")
        
        if _EXISTING_PDF_UI_AVAILABLE:
            return render_pdf_ui(
                texts, project_data, analysis_results,
                load_admin_setting_func, save_admin_setting_func,
                list_products_func, get_product_by_id_func,
                get_active_company_details_func, db_list_company_documents_func
            )
        else:
            st.error("❌ Keine PDF-UI-Module verfügbar")
            return None

def render_professional_pdf_interface(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable,
    save_admin_setting_func: Callable,
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable,
    db_list_company_documents_func: Callable,
    quick_cover_page: bool = False,
    quick_charts: bool = False,
    quick_environmental: bool = False
) -> Optional[bytes]:
    """Vollständige professionelle PDF-Interface mit erweiterten Funktionen"""
    
    # Tab-System für organisierte Darstellung
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Template", 
        "🎨 Design", 
        "🔧 Struktur", 
        "⚙️ Optionen",
        "📄 Vorschau"
    ])
    
    pdf_config = {}
    
    with tab1:
        # Template-Auswahl
        try:
            if _PROFESSIONAL_UI_AVAILABLE:
                from pdf_professional_ui import render_professional_template_selector
                template_config = render_professional_template_selector()
                pdf_config.update(template_config)
            else:
                st.info("Professional UI nicht verfügbar - Standard Template wird verwendet")
                pdf_config['template'] = 'executive_report'
        except Exception as e:
            st.warning(f"Template-Auswahl Fehler: {e}")
            pdf_config['template'] = 'executive_report'
    
    with tab2:
        # Design-Anpassungen
        try:
            if _PROFESSIONAL_UI_AVAILABLE:
                from pdf_professional_ui import render_professional_customization_panel
                customization_config = render_professional_customization_panel()
                pdf_config.update(customization_config)
            else:
                st.info("Design-Anpassungen nicht verfügbar")
        except Exception as e:
            st.warning(f"Design-Anpassung Fehler: {e}")
    
    with tab3:
        # Struktur-Management
        render_enhanced_pdf_structure(texts)
    
    with tab4:
        # Erweiterte Optionen
        advanced_config = render_advanced_pdf_controls(texts)
        quality_config = render_pdf_quality_settings()
        pdf_config.update({
            'advanced_options': advanced_config,
            'quality_settings': quality_config
        })
    
    with tab5:
        # Vorschau-System
        render_pdf_preview(pdf_config)
    
    # PDF-Generierung
    if st.button("🎨 Professionelles PDF generieren", type="primary", use_container_width=True):
        try:
            # Professionellen Generator verwenden
            if _PROFESSIONAL_GENERATOR_AVAILABLE:
                from pdf_generator_professional import ProfessionalPDFGenerator
                
                generator = ProfessionalPDFGenerator()
                pdf_buffer = generator.generate_professional_pdf(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    config=pdf_config,
                    texts=texts
                )
                
                if pdf_buffer:
                    st.success("✅ Professionelles PDF erfolgreich generiert!")
                    
                    # Download-Button
                    st.download_button(
                        label="📄 PDF herunterladen",
                        data=pdf_buffer.getvalue(),
                        file_name=f"professional_offer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    return pdf_buffer.getvalue()
                else:
                    st.error("❌ Fehler bei der PDF-Generierung")
                    return None
            else:
                st.error("❌ Professional PDF Generator nicht verfügbar")
                return None
                
        except Exception as e:
            st.error(f"❌ Fehler bei der PDF-Generierung: {e}")
            return None
    
    return None

def render_enhanced_pdf_structure(texts: Dict[str, str]):
    """Erweiterte PDF-Struktur-Verwaltung mit Widget-Integration"""
    st.markdown("### 📋 PDF-Struktur verwalten")
    
    try:
        # PDF Widgets verwenden falls verfügbar
        if 'pdf_widgets' in globals():
            from pdf_widgets import render_pdf_structure_manager
            render_pdf_structure_manager(texts)
        else:
            # Fallback-Implementierung
            st.info("📋 Widget-System wird geladen...")
            
            # Minimale Widget-Funktionalität
            section_order = st.session_state.get('pdf_section_order', [
                'cover_page', 'project_overview', 'technical_components', 
                'cost_details', 'economics'
            ])
            
            st.markdown("### Sektionsreihenfolge")
            for i, section in enumerate(section_order):
                st.write(f"{i+1}. {section}")
                
    except ImportError:
        # Fallback-Implementierung wenn pdf_widgets.py nicht verfügbar
        st.info("📋 Widget-System wird geladen...")
        
        # Minimale Widget-Funktionalität
        section_order = st.session_state.get('pdf_section_order', [
            'cover_page', 'project_overview', 'technical_components', 
            'cost_details', 'economics'
        ])
        
        st.markdown("### Sektionsreihenfolge")
        for i, section in enumerate(section_order):
            st.write(f"{i+1}. {section}")

def render_advanced_pdf_controls(texts: Dict[str, str] = None):
    """Erweiterte PDF-Steuerungselemente"""
    st.markdown("### 🔧 Erweiterte PDF-Optionen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Seitenzahlen-Optionen
        st.markdown("#### 📄 Seitennummerierung")
        page_numbers = st.checkbox("Seitenzahlen anzeigen", value=True)
        page_number_position = st.selectbox(
            "Position",
            ["Unten Mitte", "Unten Rechts", "Oben Rechts"],
            disabled=not page_numbers
        )
        
    with col2:
        # Wasserzeichen-Optionen  
        st.markdown("#### 🌊 Wasserzeichen")
        enable_watermark = st.checkbox("Wasserzeichen aktivieren")
        if enable_watermark:
            watermark_text = st.text_input("Text", value="ENTWURF")
            watermark_opacity = st.slider("Transparenz", 10, 50, 20)
    
    with col3:
        # Sicherheits-Optionen
        st.markdown("#### 🔒 Sicherheit")
        password_protect = st.checkbox("Passwort-Schutz")
        if password_protect:
            pdf_password = st.text_input("Passwort", type="password")
            restrict_editing = st.checkbox("Bearbeitung beschränken")
    
    return {
        'page_numbers': page_numbers if page_numbers else False,
        'page_number_position': page_number_position if page_numbers else None,
        'watermark': {
            'enabled': enable_watermark,
            'text': watermark_text if enable_watermark else None,
            'opacity': watermark_opacity if enable_watermark else None
        } if enable_watermark else None,
        'security': {
            'password': pdf_password if password_protect else None,
            'restrict_editing': restrict_editing if password_protect else False
        } if password_protect else None
    }

def render_pdf_quality_settings():
    """PDF-Qualitäts- und Ausgabeeinstellungen"""
    st.markdown("### ⚙️ Qualitäts-Einstellungen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bildqualität
        st.markdown("#### 🖼️ Bilder")
        image_quality = st.slider(
            "Bildqualität", 
            min_value=50, 
            max_value=100, 
            value=85,
            help="Höhere Werte = bessere Qualität, größere Dateien"
        )
        
        image_compression = st.selectbox(
            "Komprimierung",
            ["Automatisch", "Verlustfrei", "Optimiert"],
            help="Optimiert reduziert Dateigröße bei guter Qualität"
        )
    
    with col2:
        # PDF-Ausgabe
        st.markdown("#### 📄 PDF-Ausgabe")
        pdf_version = st.selectbox(
            "PDF-Version",
            ["1.4 (Standard)", "1.7 (Erweitert)", "2.0 (Neueste)"],
            index=1
        )
        
        color_profile = st.selectbox(
            "Farbprofil",
            ["sRGB (Standard)", "CMYK (Druck)", "Graustufen"]
        )
    
    return {
        'image_quality': image_quality,
        'image_compression': image_compression,
        'pdf_version': pdf_version,
        'color_profile': color_profile
    }

def render_pdf_preview(pdf_config: Dict[str, Any]):
    """PDF-Vorschau-System"""
    st.markdown("### 👁️ PDF-Vorschau")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Mock-Vorschau
        st.markdown("#### 📄 Seitenvorschau")
        
        # Template-basierte Vorschau
        template = pdf_config.get('template', 'executive_report')
        
        if template == 'executive_report':
            st.markdown("""
            **Executive Report Template**
            - 🏢 Professionelles Corporate Design
            - 📊 Integrierte Diagramme und Charts
            - 🎨 Moderne Farbgebung
            - 📝 Strukturierte Inhaltsblöcke
            """)
        elif template == 'solar_professional':
            st.markdown("""
            **Solar Professional Template**
            - ☀️ Solar-optimierte Darstellung
            - 🔧 Technische Detailansichten
            - 📈 Energieertrag-Visualisierung
            - 🌱 Umwelt-Fokus
            """)
        else:
            st.markdown("**Standardvorschau**")
    
    with col2:
        # Konfigurationsübersicht
        st.markdown("#### ⚙️ Aktuelle Einstellungen")
        
        if pdf_config:
            for key, value in pdf_config.items():
                if isinstance(value, dict):
                    st.write(f"**{key}:** {len(value)} Optionen")
                else:
                    st.write(f"**{key}:** {value}")
        else:
            st.write("Keine Konfiguration verfügbar")
    save_admin_setting_func: Callable,
    list_products_func: Callable, 
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable,
    db_list_company_documents_func: Callable,
    quick_cover_page: bool = True,
    quick_charts: bool = True,
    quick_environmental: bool = True
):
    """
    Professionelle PDF-Interface mit erweiterten Template-Optionen.
    """
    
    # Datenvalidierung und Status
    st.markdown("### 📋 Projekt-Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        project_status = "✅ Verfügbar" if project_data else "❌ Fehlend"
        st.metric("Projektdaten", project_status)
    
    with col2:
        analysis_status = "✅ Verfügbar" if analysis_results else "❌ Fehlend"
        st.metric("Analysedaten", analysis_status)
    
    with col3:
        company_details = get_active_company_details_func() if get_active_company_details_func else None
        company_status = "✅ Verfügbar" if company_details else "❌ Fehlend"
        st.metric("Firmendaten", company_status)
    
    st.markdown("---")
    
    # Template-Auswahl
    st.markdown("### 🎨 Template-Auswahl")
    selected_template = render_professional_template_selector()
    
    st.markdown("---")
    
    # Anpassungsoptionen
    st.markdown("### ⚙️ Konfiguration")
    customizations = render_professional_customization_panel(selected_template)
    
    # PDF-Widgets Integration
    if _PROFESSIONAL_UI_AVAILABLE:
        st.markdown("### 🧩 Erweiterte Inhalts-Widgets")
        try:
            widget_manager = PDFSectionManager()
            widget_manager.initialize_session_state()
            
            # Widget-Interface nur anzeigen wenn aktiviert
            if st.checkbox("📝 Erweiterte Widget-Bearbeitung aktivieren", value=False):
                widget_manager.render_drag_drop_interface(texts)
                
                # Widget-Konfiguration zu Anpassungen hinzufügen
                customizations['widget_sections'] = st.session_state.get('pdf_section_order', [])
                customizations['widget_contents'] = st.session_state.get('pdf_section_contents', {})
                customizations['enable_widgets'] = True
            else:
                customizations['enable_widgets'] = False
        except Exception as e:
            st.warning(f"Widget-Integration nicht verfügbar: {str(e)}")
            customizations['enable_widgets'] = False
    
    # Erweiterte Theme-Anpassungen
    if _PROFESSIONAL_UI_AVAILABLE:
        with st.expander("🎨 Erweiterte Theme-Anpassungen", expanded=False):
            try:
                theme_manager = PDFThemeManager()
                
                # Color Scheme Auswahl
                available_schemes = ["modern_blue", "elegant_dark", "eco_green", "corporate_gray", "solar_orange"]
                selected_scheme = st.selectbox(
                    "Farbschema wählen:",
                    available_schemes,
                    index=0,
                    help="Professionelle Farbpaletten für verschiedene Stile"
                )
                customizations['color_scheme'] = selected_scheme
                
                # Visual Enhancement Optionen
                visual_options = st.columns(3)
                with visual_options[0]:
                    customizations['enhance_charts'] = st.checkbox(
                        "Chart-Verbesserungen", 
                        value=True,
                        help="Erweiterte Diagramm-Stile anwenden"
                    )
                
                with visual_options[1]:
                    customizations['gradient_backgrounds'] = st.checkbox(
                        "Gradient-Hintergründe", 
                        value=False,
                        help="Subtile Farbverläufe für modernen Look"
                    )
                
                with visual_options[2]:
                    customizations['advanced_typography'] = st.checkbox(
                        "Erweiterte Typografie", 
                        value=True,
                        help="Optimierte Schrift-Hierarchie"
                    )
                
                # Background Pattern Optionen
                st.markdown("**Hintergrund-Muster:**")
                bg_cols = st.columns(4)
                
                with bg_cols[0]:
                    customizations['background_pattern'] = st.selectbox(
                        "Muster-Typ",
                        ["none", "geometric", "organic", "minimal", "tech"],
                        index=0,
                        help="Subtile Hintergrund-Muster"
                    )
                
                with bg_cols[1]:
                    customizations['pattern_opacity'] = st.slider(
                        "Muster-Transparenz",
                        0.0, 0.1, 0.03,
                        step=0.01,
                        help="Wie stark soll das Muster sichtbar sein?"
                    )
                
                with bg_cols[2]:
                    customizations['pattern_color'] = st.selectbox(
                        "Muster-Farbe",
                        ["auto", "primary", "secondary", "neutral"],
                        index=0,
                        help="Farbauswahl für das Hintergrund-Muster"
                    )
                
            except Exception as e:
                st.warning(f"Erweiterte Theme-Optionen nicht verfügbar: {str(e)}")
    
    # Schnelleinstellungen einbeziehen
    customizations.update({
        'include_cover_page': quick_cover_page,
        'include_charts': quick_charts,
        'include_environmental_impact': quick_environmental
    })
    
    st.markdown("---")
    
    # Erweiterte Einstellungen
    with st.expander("🔧 Erweiterte Einstellungen", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            customizations['custom_company_name'] = st.text_input(
                "Firmenname überschreiben",
                value=company_details.get('name', '') if company_details else '',
                help="Lassen Sie leer, um den Standard-Firmennamen zu verwenden"
            )
            
            customizations['custom_offer_title'] = st.text_input(
                "Angebots-Titel",
                value="Ihr persönliches Photovoltaik-Angebot",
                help="Individueller Titel für das Angebot"
            )
            
        with col2:
            customizations['language_style'] = st.selectbox(
                "Sprachstil",
                ["Professionell (Sie)", "Persönlich (Du)", "Technisch"],
                index=0,
                help="Bestimmt die Ansprache und Tonalität des Dokuments"
            )
            
            customizations['detail_level'] = st.selectbox(
                "Detailgrad",
                ["Kompakt", "Standard", "Ausführlich"],
                index=1,
                help="Bestimmt den Umfang der technischen Details"
            )
    
    # Live-Vorschau
    st.markdown("---")
    st.markdown("### 👀 Vorschau")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_professional_preview_panel(selected_template, customizations)
    
    with col2:
        st.markdown("#### 📊 Konfiguration")
        st.json({
            "template": selected_template,
            "module_anzahl": len([k for k, v in customizations.items() if k.startswith('include_') and v]),
            "anpassungen": len([k for k, v in customizations.items() if not k.startswith('include_') and v not in [True, False, None, '']])
        })
        
        # Geschätzte Seitenzahl
        estimated_pages = estimate_pdf_pages(customizations)
        st.metric("Geschätzte Seiten", f"~{estimated_pages}")
    
    st.markdown("---")
    
    # PDF-Generierung
    st.markdown("### 🚀 PDF-Generierung")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📄 Professionelles PDF erstellen", type="primary", use_container_width=True):
            generate_professional_pdf_with_ui(
                project_data, analysis_results, company_details,
                selected_template, customizations
            )

def estimate_pdf_pages(customizations: Dict[str, Any]) -> int:
    """
    Schätzt die Anzahl der PDF-Seiten basierend auf den gewählten Modulen.
    """
    pages = 0
    
    if customizations.get('include_cover_page', True):
        pages += 1
    
    if customizations.get('include_executive_summary', True):
        pages += 1
    
    if customizations.get('include_technical_details', True):
        pages += 1 if customizations.get('detail_level', 'Standard') == 'Kompakt' else 2
    
    if customizations.get('include_financial_analysis', True):
        pages += 2
    
    if customizations.get('include_charts', True):
        pages += 1
    
    if customizations.get('include_environmental_impact', True):
        pages += 1
    
    if customizations.get('include_appendix', False):
        pages += 2
    
    return max(pages, 1)

def generate_professional_pdf_with_ui(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_details: Dict[str, Any],
    template_name: str,
    customizations: Dict[str, Any]
):
    """
    Generiert das professionelle PDF mit UI-Feedback.
    """
    
    # Progress-Tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔄 Bereite Daten vor...")
        progress_bar.progress(10)
        
        # Zusammenstellung der Angebotsdaten
        offer_data = {
            'project_data': project_data,
            'analysis_results': analysis_results,
            'company': company_details,
            'customer': {
                'name': project_data.get('customer_name', 'Kunde'),
            },
            'offer_id': f"ANB-{datetime.now().strftime('%Y%m%d')}-001",
            'date': datetime.now().strftime('%d.%m.%Y')
        }
        
        progress_bar.progress(30)
        status_text.text("🎨 Erstelle Template...")
        
        # Dateiname generieren
        customer_name = offer_data['customer']['name'].replace(' ', '_')
        filename = f"angebot_{customer_name}_{template_name.replace(' ', '_').lower()}.pdf"
        
        progress_bar.progress(50)
        status_text.text("📄 Generiere PDF...")
        
        # PDF erstellen
        pdf_path = create_professional_pdf_with_template(
            offer_data=offer_data,
            template_name=template_name,
            customizations=customizations,
            filename=filename
        )
        
        progress_bar.progress(90)
        status_text.text("✅ PDF erfolgreich erstellt!")
        
        progress_bar.progress(100)
        
        # Download-Button anzeigen
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.success(f"✅ PDF erfolgreich erstellt: {filename}")
            st.download_button(
                label="📥 PDF herunterladen",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary"
            )
        else:
            st.error("❌ PDF-Datei konnte nicht gefunden werden")
            
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("❌ Fehler bei der PDF-Erstellung")
        st.error(f"Fehler bei der PDF-Generierung: {str(e)}")
        
        # Fallback auf Standard-PDF
        st.info("🔄 Versuche Fallback auf Standard-PDF...")
        try:
            # Hier könnte der bestehende PDF-Generator als Fallback verwendet werden
            st.warning("⚠️ Fallback auf Standard-PDF-Generator nicht implementiert")
        except:
            st.error("❌ Auch Fallback-PDF-Generierung fehlgeschlagen")

# --- KOMPATIBILITÄTS-LAYER ---

def enhanced_render_pdf_ui(*args, **kwargs):
    """
    Drop-in Replacement für render_pdf_ui mit erweiterten Funktionen.
    Kann bestehende render_pdf_ui Aufrufe ersetzen ohne Code-Änderungen.
    """
    return render_enhanced_pdf_ui(*args, **kwargs)

# Integration mit bestehenden Modulen
if _EXISTING_PDF_UI_AVAILABLE:
    # Erweitere bestehende Funktionen um professionelle Optionen
    original_render_pdf_ui = render_pdf_ui
    
    def extended_render_pdf_ui(*args, **kwargs):
        """Erweiterte Version der bestehenden render_pdf_ui Funktion."""
        
        # Prüfe ob professionelle Templates gewünscht sind
        if st.session_state.get('use_professional_templates', False):
            return render_enhanced_pdf_ui(*args, **kwargs)
        else:
            return original_render_pdf_ui(*args, **kwargs)
    
    # Setze erweiterte Funktion als Standard
    render_pdf_ui = extended_render_pdf_ui

# Hilfsfunktionen für die Integration
def get_template_recommendations(project_data: Dict[str, Any]) -> List[str]:
    """
    Gibt Template-Empfehlungen basierend auf Projektdaten zurück.
    """
    if not project_data:
        return ["Executive Report"]
    
    recommendations = []
    
    # Empfehlungen basierend auf Anlagengröße
    system_power = project_data.get('system_power', 0)
    if system_power > 50:
        recommendations.append("Executive Report")
    elif system_power > 20:
        recommendations.append("Solar Professional")
    else:
        recommendations.append("Premium Minimal")
    
    # Immer Modern Tech als Alternative
    recommendations.append("Modern Tech")
    
    return list(set(recommendations))

def validate_template_requirements(template_name: str, project_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> List[str]:
    """
    Validiert ob alle benötigten Daten für ein Template verfügbar sind.
    
    Returns:
        List[str]: Liste der fehlenden Anforderungen
    """
    missing_requirements = []
    
    if not project_data:
        missing_requirements.append("Projektdaten fehlen")
    
    if not analysis_results:
        missing_requirements.append("Analyseergebnisse fehlen")
    
    # Template-spezifische Validierungen
    if template_name == "Executive Report":
        if not project_data.get('system_power'):
            missing_requirements.append("Anlagenleistung nicht definiert")
    
    return missing_requirements

# Import datetime für Datumsfunktionen
from datetime import datetime
