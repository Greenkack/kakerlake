# pdf_ui_design_enhancement.py
# -*- coding: utf-8 -*-
"""
Modular optionale Design-Erweiterung für das bestehende PDF-UI System
Vollständig kompatibel und integrierbar ohne Änderung des bestehenden Codes
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import traceback

# Sichere Imports
try:
    from pdf_design_enhanced_modern import (
        get_modern_design_system, 
        get_modern_component_library,
        get_available_modern_color_schemes,
        get_modern_color_scheme_preview
    )
    MODERN_DESIGN_AVAILABLE = True
except ImportError:
    MODERN_DESIGN_AVAILABLE = False

def render_modern_pdf_design_options():
    """
    Hauptfunktion für moderne PDF-Design-Optionen
    Vollständig optional und modular
    """
    
    # Hauptschalter für moderne Features
    modern_design_enabled = st.checkbox(
        "🎨 **Moderne PDF-Design Features aktivieren** *(Premium)*",
        value=st.session_state.get('modern_pdf_design_enabled', False),
        key='modern_pdf_design_enabled',
        help="Aktiviert erweiterte Design-Features für professionelle PDF-Ausgabe mit Farben, modernen Layouts und verbesserter Typografie."
    )
    
    if modern_design_enabled:
        st.markdown("---")
        
        # Design-Schema Auswahl
        st.subheader("🎨 Design-Schema")
        
        color_scheme_options = {
            'premium_blue_modern': '🔷 Premium Blue Modern - Professionelles Business-Design',
            'solar_professional_enhanced': '🌞 Solar Professional Enhanced - Nachhaltiges Grün-Design',
            'executive_luxury': '👔 Executive Luxury - Luxuriöses Gold-Akzent Design'
        }
        
        selected_scheme = st.selectbox(
            "Wählen Sie Ihr bevorzugtes Farbschema:",
            options=list(color_scheme_options.keys()),
            format_func=lambda x: color_scheme_options[x],
            index=0,
            key='modern_pdf_color_scheme'
        )
        
        # Farbvorschau anzeigen
        if selected_scheme and MODERN_DESIGN_AVAILABLE:
            try:
                colors = get_modern_color_scheme_preview(selected_scheme)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f'<div style="background-color: {colors["primary"]}; padding: 20px; border-radius: 8px; text-align: center; color: white; font-weight: bold;">Primary</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div style="background-color: {colors["secondary"]}; padding: 20px; border-radius: 8px; text-align: center; color: white; font-weight: bold;">Secondary</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div style="background-color: {colors["accent"]}; padding: 20px; border-radius: 8px; text-align: center; color: white; font-weight: bold;">Accent</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div style="background-color: {colors["success"]}; padding: 20px; border-radius: 8px; text-align: center; color: white; font-weight: bold;">Success</div>', unsafe_allow_html=True)
            except ImportError:
                st.info("Farbvorschau wird geladen...")
        
        st.markdown("---")
        
        # Erweiterte Features
        st.subheader("📋 Erweiterte PDF-Abschnitte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            executive_summary = st.checkbox(
                "📋 Executive Summary",
                value=st.session_state.get('modern_pdf_executive_summary', True),
                key='modern_pdf_executive_summary',
                help="Fügt eine professionelle Executive Summary-Seite am Anfang hinzu"
            )
            
            enhanced_charts = st.checkbox(
                "📊 Erweiterte Diagramme",
                value=st.session_state.get('modern_pdf_enhanced_charts', True),
                key='modern_pdf_enhanced_charts',
                help="Verwendet moderne Chart-Designs mit besserer Visualisierung"
            )
            
            product_showcase = st.checkbox(
                "🛠️ Moderne Produktpräsentation",
                value=st.session_state.get('modern_pdf_product_showcase', True),
                key='modern_pdf_product_showcase',
                help="Erweiterte Produktdarstellung mit Bildern und detaillierten Spezifikationen"
            )
        
        with col2:
            environmental_section = st.checkbox(
                "🌍 Umwelt & Nachhaltigkeit",
                value=st.session_state.get('modern_pdf_environmental_section', True),
                key='modern_pdf_environmental_section',
                help="Zusätzlicher Abschnitt über CO₂-Einsparungen und Umwelt-Impact"
            )
            
            technical_details = st.checkbox(
                "⚡ Erweiterte technische Details",
                value=st.session_state.get('modern_pdf_technical_details', True),
                key='modern_pdf_technical_details',
                help="Detaillierte technische Spezifikationen mit modernem Layout"
            )
            
            financial_breakdown = st.checkbox(
                "💰 Detaillierte Finanzanalyse",
                value=st.session_state.get('modern_pdf_financial_breakdown', True),
                key='modern_pdf_financial_breakdown',
                help="Erweiterte Finanzaufschlüsselung mit professionellen Tabellen"
            )
        
        # Aktivierte Features Zusammenfassung
        active_features = []
        if executive_summary:
            active_features.append("📋 Executive Summary")
        if enhanced_charts:
            active_features.append("📊 Erweiterte Diagramme")
        if environmental_section:
            active_features.append("🌍 Umwelt-Sektion")
        if product_showcase:
            active_features.append("🛠️ Produktpräsentation")
        if technical_details:
            active_features.append("⚡ Tech-Details")
        if financial_breakdown:
            active_features.append("💰 Finanzanalyse")
        
        if active_features:
            st.success(f"✅ **{len(active_features)} erweiterte Features aktiv:** {', '.join(active_features)}")
        else:
            st.info("💡 Wählen Sie Features für erweiterte PDF-Ausgabe")
        
        # Hinweise
        st.markdown("---")
        st.info("""
        💡 **Hinweise zu modernen PDF-Features:**
        - Alle Features sind vollständig optional und modular
        - Die bestehende PDF-Funktionalität bleibt 100% erhalten
        - Moderne Features erweitern nur die visuelle Darstellung
        - Sie können jederzeit zwischen klassischem und modernem Design wechseln
        """)
        
    else:
        # Reset alle moderne Design-Einstellungen wenn deaktiviert
        for key in st.session_state.keys():
            if key.startswith('modern_pdf_') and key != 'modern_pdf_design_enabled':
                st.session_state[key] = False
        
        st.info("Klassische PDF-Ausgabe aktiv. Aktivieren Sie moderne Features für erweiterte Design-Optionen.")

def get_modern_design_configuration() -> Dict[str, Any]:
    """
    Gibt die aktuelle Konfiguration der modernen Design-Features zurück
    """
    if not st.session_state.get('modern_pdf_design_enabled', False):
        return {'enable_modern_design': False}
    
    return {
        'enable_modern_design': True,
        'color_scheme': st.session_state.get('modern_pdf_color_scheme', 'premium_blue_modern'),
        'add_executive_summary': st.session_state.get('modern_pdf_executive_summary', False),
        'add_environmental_section': st.session_state.get('modern_pdf_environmental_section', False),
        'enhance_charts': st.session_state.get('modern_pdf_enhanced_charts', False),
        'use_product_showcase': st.session_state.get('modern_pdf_product_showcase', False),
        'use_technical_details': st.session_state.get('modern_pdf_technical_details', False),
        'use_financial_breakdown': st.session_state.get('modern_pdf_financial_breakdown', False)
    }

def get_modern_design_enabled() -> bool:
    """Prüft ob moderne Design-Features aktiviert sind"""
    return st.session_state.get('modern_pdf_design_enabled', False)

def get_current_modern_color_scheme_name() -> str:
    """Gibt den aktuell gewählten Farbschema-Namen zurück"""
    return st.session_state.get('modern_pdf_color_scheme', 'premium_blue_modern')

def render_modern_pdf_design_ui(texts: Dict[str, str]) -> Dict[str, Any]:
    """
    Rendert das moderne Design-UI als optionale Erweiterung
    Gibt Design-Konfiguration zurück für PDF-Generator
    """
    if not MODERN_DESIGN_AVAILABLE:
        st.info("Moderne Design-Features sind derzeit nicht verfügbar.")
        return {'enabled': False}
    
    design_config = {'enabled': False}
    
    with st.container():
        st.markdown("### 🎨 **Moderne Design-Erweiterung** *(Optional)*")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # Hauptschalter für moderne Features
            use_modern_design = st.checkbox(
                "✨ **Erweiterte Design-Features aktivieren**",
                value=st.session_state.get('pdf_modern_design_enabled', False),
                key="pdf_modern_design_enabled",
                help="Aktiviert moderne Farben, Layouts, Info-Boxen und professionelle Bildintegration"
            )
            
            design_config['enabled'] = use_modern_design
        
        with col2:
            if use_modern_design:
                # Zeige Status-Indikator
                st.success("🎨 Moderne Features aktiv")
            else:
                st.info("🔧 Standard Design aktiv")
        
        with col3:
            if use_modern_design:
                # Schnell-Toggle für oft verwendete Features
                st.caption("Quick-Toggle:")
                quick_charts = st.checkbox("📊", key="pdf_quick_charts", 
                                         value=st.session_state.get('pdf_modern_charts_enabled', True),
                                         help="Moderne Charts")
                quick_colors = st.checkbox("🎨", key="pdf_quick_colors",
                                         value=st.session_state.get('pdf_modern_colors_enabled', True), 
                                         help="Erweiterte Farben")
        
        if use_modern_design:
            st.markdown("---")
            
            # Erweiterte Konfiguration in Tabs
            design_tab1, design_tab2, design_tab3 = st.tabs([
                "🎨 Design-Schema", "📋 PDF-Abschnitte", "⚙️ Layout-Optionen"
            ])
            
            with design_tab1:
                # Farbschema-Auswahl
                st.subheader("Farbschema wählen")
                
                color_schemes = get_available_modern_color_schemes()
                
                scheme_options = {}
                for scheme_id, scheme_data in color_schemes.items():
                    scheme_options[scheme_id] = f"{scheme_data['name']} - {scheme_data['description']}"
                
                selected_scheme = st.selectbox(
                    "Verfügbare Design-Schemata:",
                    options=list(scheme_options.keys()),
                    format_func=lambda x: scheme_options[x],
                    index=0,
                    key='pdf_modern_color_scheme'
                )
                
                design_config['color_scheme'] = selected_scheme
                
                # Farbvorschau
                if selected_scheme:
                    try:
                        colors = get_modern_color_scheme_preview(selected_scheme)
                        st.caption("Farbvorschau:")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown(f'<div style="background: {colors["primary"]}; padding: 15px; border-radius: 6px; text-align: center; color: white; font-size: 12px; font-weight: bold;">Primary</div>', unsafe_allow_html=True)
                        with col2:
                            st.markdown(f'<div style="background: {colors["secondary"]}; padding: 15px; border-radius: 6px; text-align: center; color: white; font-size: 12px; font-weight: bold;">Secondary</div>', unsafe_allow_html=True)
                        with col3:
                            st.markdown(f'<div style="background: {colors["accent"]}; padding: 15px; border-radius: 6px; text-align: center; color: white; font-size: 12px; font-weight: bold;">Accent</div>', unsafe_allow_html=True)
                        with col4:
                            st.markdown(f'<div style="background: {colors["success"]}; padding: 15px; border-radius: 6px; text-align: center; color: white; font-size: 12px; font-weight: bold;">Success</div>', unsafe_allow_html=True)
                        
                        # Anwendungshinweis
                        scheme_info = color_schemes.get(selected_scheme, {})
                        if scheme_info.get('use_case'):
                            st.info(f"💡 **Ideal für:** {scheme_info['use_case']}")
                    
                    except Exception as e:
                        st.warning(f"Farbvorschau konnte nicht geladen werden: {e}")
            
            with design_tab2:
                # PDF-Abschnitte konfigurieren
                st.subheader("Zusätzliche PDF-Abschnitte")
                
                section_col1, section_col2 = st.columns(2)
                
                with section_col1:
                    add_executive_summary = st.checkbox(
                        "📋 Executive Summary",
                        value=st.session_state.get('pdf_modern_executive_summary', True),
                        key='pdf_modern_executive_summary',
                        help="Professionelle Zusammenfassung am Anfang der PDF"
                    )
                    
                    add_environmental = st.checkbox(
                        "🌍 Umwelt & Nachhaltigkeit",
                        value=st.session_state.get('pdf_modern_environmental', True),
                        key='pdf_modern_environmental',
                        help="CO₂-Einsparungen und Umwelt-Impact"
                    )
                    
                    enhanced_product_showcase = st.checkbox(
                        "🛠️ Erweiterte Produktpräsentation",
                        value=st.session_state.get('pdf_modern_products', True),
                        key='pdf_modern_products',
                        help="Moderne Produktdarstellung mit Bildern"
                    )
                
                with section_col2:
                    enhanced_charts = st.checkbox(
                        "📊 Moderne Diagramme",
                        value=st.session_state.get('pdf_modern_charts_enabled', True),
                        key='pdf_modern_charts_detailed',
                        help="Erweiterte Chart-Designs mit Farben"
                    )
                    
                    technical_details = st.checkbox(
                        "⚡ Detaillierte Technik-Sektion",
                        value=st.session_state.get('pdf_modern_technical', True),
                        key='pdf_modern_technical',
                        help="Erweiterte technische Spezifikationen"
                    )
                    
                    financial_breakdown = st.checkbox(
                        "💰 Finanzanalyse-Erweiterung",
                        value=st.session_state.get('pdf_modern_financial', True),
                        key='pdf_modern_financial',
                        help="Detaillierte Kostenaufschlüsselung"
                    )
                
                design_config.update({
                    'add_executive_summary': add_executive_summary,
                    'add_environmental_section': add_environmental,
                    'enhance_charts': enhanced_charts,
                    'use_product_showcase': enhanced_product_showcase,
                    'use_technical_details': technical_details,
                    'use_financial_breakdown': financial_breakdown
                })
            
            with design_tab3:
                # Layout-Einstellungen
                st.subheader("Layout & Typografie")
                
                layout_col1, layout_col2 = st.columns(2)
                
                with layout_col1:
                    modern_typography = st.checkbox(
                        "🔤 Moderne Typografie",
                        value=st.session_state.get('pdf_modern_typography', True),
                        key='pdf_modern_typography',
                        help="Erweiterte Schrift-Hierarchie"
                    )
                    
                    info_boxes = st.checkbox(
                        "📦 Info-Boxen & Highlights",
                        value=st.session_state.get('pdf_modern_info_boxes', True),
                        key='pdf_modern_info_boxes',
                        help="Moderne Info-Boxen für wichtige Hinweise"
                    )
                    
                    enhanced_tables = st.checkbox(
                        "📊 Moderne Tabellen",
                        value=st.session_state.get('pdf_modern_tables', True),
                        key='pdf_modern_tables',
                        help="Zebra-Striping und Farb-Akzente"
                    )
                
                with layout_col2:
                    professional_spacing = st.checkbox(
                        "📏 Professionelle Abstände",
                        value=st.session_state.get('pdf_modern_spacing', True),
                        key='pdf_modern_spacing',
                        help="Optimierte Seitenaufteilung"
                    )
                    
                    header_enhancement = st.checkbox(
                        "🎯 Erweiterte Header",
                        value=st.session_state.get('pdf_modern_headers', True),
                        key='pdf_modern_headers',
                        help="Moderne Abschnitts-Header mit Farben"
                    )
                    
                    image_optimization = st.checkbox(
                        "🖼️ Bild-Optimierung",
                        value=st.session_state.get('pdf_modern_images', True),
                        key='pdf_modern_images',
                        help="Automatische Bildgrößen-Anpassung"
                    )
                
                design_config.update({
                    'use_modern_typography': modern_typography,
                    'use_info_boxes': info_boxes,
                    'use_enhanced_tables': enhanced_tables,
                    'use_professional_spacing': professional_spacing,
                    'use_header_enhancement': header_enhancement,
                    'use_image_optimization': image_optimization
                })
                
                # Erweiterte Optionen
                st.markdown("---")
                with st.expander("⚙️ Erweiterte Einstellungen", expanded=False):
                    custom_logo = st.text_input(
                        "Logo-Pfad (optional):",
                        value=st.session_state.get('pdf_modern_logo_path', ''),
                        key='pdf_modern_logo_path',
                        help="Pfad zu Ihrem Firmenlogo"
                    )
                    
                    custom_footer = st.text_area(
                        "Benutzerdefinierter Footer:",
                        value=st.session_state.get('pdf_modern_footer', ''),
                        key='pdf_modern_footer',
                        help="Zusätzlicher Footer-Text",
                        height=60
                    )
                    
                    page_margins = st.slider(
                        "Seitenränder (cm):",
                        min_value=1.0,
                        max_value=4.0,
                        value=st.session_state.get('pdf_modern_margins', 2.0),
                        step=0.5,
                        key='pdf_modern_margins'
                    )
                    
                    design_config.update({
                        'custom_logo_path': custom_logo,
                        'custom_footer_text': custom_footer,
                        'page_margins': page_margins
                    })
            
            # Aktivierte Features Zusammenfassung
            st.markdown("---")
            active_features = []
            if design_config.get('add_executive_summary'): active_features.append("📋 Executive Summary")
            if design_config.get('add_environmental_section'): active_features.append("🌍 Umwelt-Sektion")
            if design_config.get('enhance_charts'): active_features.append("📊 Moderne Charts")
            if design_config.get('use_product_showcase'): active_features.append("🛠️ Produktpräsentation")
            if design_config.get('use_technical_details'): active_features.append("⚡ Tech-Details")
            if design_config.get('use_financial_breakdown'): active_features.append("💰 Finanzanalyse")
            
            if active_features:
                st.success(f"✅ **{len(active_features)} erweiterte Features aktiv:** {', '.join(active_features)}")
            else:
                st.info("💡 Wählen Sie Features für erweiterte PDF-Ausgabe")
        
        else:
            # Reset moderne Features wenn deaktiviert
            design_config = {'enabled': False}
        
        if use_modern_design:
            with col2:
                # Farbschema-Auswahl
                available_schemes = get_available_modern_color_schemes()
                scheme_names = list(available_schemes.keys())
                scheme_options = [f"🎨 {available_schemes[name]['name']}" for name in scheme_names]
                
                selected_scheme_idx = st.selectbox(
                    "🎨 **Modernes Farbschema:**",
                    options=range(len(scheme_names)),
                    format_func=lambda i: scheme_options[i],
                    index=st.session_state.get('pdf_modern_scheme_index', 0),
                    key="pdf_modern_scheme_index",
                    help="Wählen Sie das moderne Farbschema für Ihr PDF"
                )
                
                selected_scheme = scheme_names[selected_scheme_idx]
                design_config['color_scheme'] = selected_scheme
                
                # Schema-Info anzeigen
                scheme_info = available_schemes[selected_scheme]
                st.caption(f"📖 {scheme_info['description']}")
                st.caption(f"🎯 **Ideal für:** {scheme_info['use_case']}")
            
            with col3:
                # Farbvorschau
                try:
                    preview_colors = get_modern_color_scheme_preview(selected_scheme)
                    st.markdown("**Farbvorschau:**")
                    
                    color_html = f"""
                    <div style="display: flex; gap: 3px; margin: 5px 0;">
                        <div style="width: 15px; height: 15px; background: {preview_colors['primary']}; border-radius: 3px;" title="Primär"></div>
                        <div style="width: 15px; height: 15px; background: {preview_colors['secondary']}; border-radius: 3px;" title="Sekundär"></div>
                        <div style="width: 15px; height: 15px; background: {preview_colors['accent']}; border-radius: 3px;" title="Akzent"></div>
                        <div style="width: 15px; height: 15px; background: {preview_colors['success']}; border-radius: 3px;" title="Erfolg"></div>
                    </div>
                    """
                    st.markdown(color_html, unsafe_allow_html=True)
                except Exception:
                    st.caption("Vorschau nicht verfügbar")
            
            # Erweiterte Design-Optionen
            st.markdown("---")
            st.markdown("**🛠️ Erweiterte Design-Optionen:**")
            
            col_opts1, col_opts2, col_opts3 = st.columns(3)
            
            with col_opts1:
                # Info-Boxen
                enable_info_boxes = st.checkbox(
                    "📋 Info-Boxen verwenden",
                    value=st.session_state.get('pdf_modern_info_boxes', True),
                    key="pdf_modern_info_boxes",
                    help="Fügt stilvolle Info-Boxen für wichtige Informationen hinzu"
                )
                design_config['info_boxes'] = enable_info_boxes
                
                # Erweiterte Typografie
                enhanced_typography = st.checkbox(
                    "🔤 Erweiterte Typografie",
                    value=st.session_state.get('pdf_modern_typography', True),
                    key="pdf_modern_typography",
                    help="Verwendet moderne Schriftgrößen und -hierarchien"
                )
                design_config['enhanced_typography'] = enhanced_typography
            
            with col_opts2:
                # Moderne Tabellen
                modern_tables = st.checkbox(
                    "📊 Moderne Tabellen",
                    value=st.session_state.get('pdf_modern_tables', True),
                    key="pdf_modern_tables",
                    help="Aktiviert moderne Tabellen-Designs mit besserer Lesbarkeit"
                )
                design_config['modern_tables'] = modern_tables
                
                # Bildergalerien
                image_galleries = st.checkbox(
                    "🖼️ Erweiterte Bilddarstellung",
                    value=st.session_state.get('pdf_modern_images', True),
                    key="pdf_modern_images",
                    help="Verbesserte Bilddarstellung mit Beschreibungen"
                )
                design_config['enhanced_images'] = image_galleries
            
            with col_opts3:
                # Finanz-Cards
                financial_cards = st.checkbox(
                    "💰 Finanz-Zusammenfassungen",
                    value=st.session_state.get('pdf_modern_financial', True),
                    key="pdf_modern_financial",
                    help="Moderne Darstellung von Finanzinformationen"
                )
                design_config['financial_cards'] = financial_cards
                
                # Header-Bereiche
                modern_headers = st.checkbox(
                    "🎯 Moderne Abschnitt-Header",
                    value=st.session_state.get('pdf_modern_headers', True),
                    key="pdf_modern_headers",
                    help="Professionelle Header für Abschnitte"
                )
                design_config['modern_headers'] = modern_headers
            
            # Info über aktivierte Features
            if use_modern_design:
                activated_features = []
                if enable_info_boxes: activated_features.append("Info-Boxen")
                if enhanced_typography: activated_features.append("Erweiterte Typografie")
                if modern_tables: activated_features.append("Moderne Tabellen")
                if image_galleries: activated_features.append("Bildergalerien")
                if financial_cards: activated_features.append("Finanz-Cards")
                if modern_headers: activated_features.append("Moderne Headers")
                
                if activated_features:
                    st.success(f"✅ **Aktiviert:** {', '.join(activated_features)}")
                else:
                    st.info("ℹ️ Moderne Design-Features sind aktiviert, aber keine spezifischen Optionen gewählt.")
    
    return design_config

def get_modern_design_integration_config() -> Dict[str, Any]:
    """
    Gibt die aktuelle Konfiguration für die Integration in PDF-Generatoren zurück
    """
    if not MODERN_DESIGN_AVAILABLE:
        return {'enabled': False}
    
    return {
        'enabled': st.session_state.get('pdf_modern_design_enabled', False),
        'color_scheme': st.session_state.get('pdf_modern_scheme_index', 0),
        'info_boxes': st.session_state.get('pdf_modern_info_boxes', True),
        'enhanced_typography': st.session_state.get('pdf_modern_typography', True),
        'modern_tables': st.session_state.get('pdf_modern_tables', True),
        'enhanced_images': st.session_state.get('pdf_modern_images', True),
        'financial_cards': st.session_state.get('pdf_modern_financial', True),
        'modern_headers': st.session_state.get('pdf_modern_headers', True),
    }

def create_modern_pdf_content_enhancer(design_config: Dict[str, Any], 
                                      project_data: Dict[str, Any], 
                                      analysis_results: Dict[str, Any]) -> Optional[Any]:
    """
    Erstellt einen Content-Enhancer basierend auf der modernen Design-Konfiguration
    """
    if not design_config.get('enabled', False) or not MODERN_DESIGN_AVAILABLE:
        return None
    
    try:
        design_system = get_modern_design_system()
        component_library = get_modern_component_library(design_system)
        
        # Farbschema aus Index ableiten
        scheme_names = list(get_available_modern_color_schemes().keys())
        scheme_index = design_config.get('color_scheme', 0)
        if isinstance(scheme_index, int) and 0 <= scheme_index < len(scheme_names):
            color_scheme = scheme_names[scheme_index]
        else:
            color_scheme = 'premium_blue_modern'  # Fallback
        
        # Content-Enhancer Objekt erstellen
        class ModernContentEnhancer:
            def __init__(self):
                self.design_system = design_system
                self.component_library = component_library
                self.color_scheme = color_scheme
                self.config = design_config
            
            def enhance_financial_content(self, financial_data: Dict[str, Any]) -> List:
                """Erweitert Finanzinhalte mit modernem Design"""
                if not self.config.get('financial_cards', True):
                    return []
                
                return self.component_library.create_solar_calculation_showcase(
                    financial_data, self.color_scheme
                )
            
            def enhance_technical_content(self, tech_data: Dict[str, Any]) -> List:
                """Erweitert technische Inhalte"""
                if not self.config.get('modern_tables', True):
                    return []
                
                return self.component_library.create_technical_specifications_modern(
                    tech_data, self.color_scheme
                )
            
            def enhance_product_content(self, products: List[Dict]) -> List:
                """Erweitert Produktdarstellung"""
                if not self.config.get('enhanced_images', True):
                    return []
                
                return self.component_library.create_product_showcase(
                    products, self.color_scheme
                )
            
            def create_info_box(self, title: str, content: str, box_type: str = 'info') -> List:
                """Erstellt Info-Box wenn aktiviert"""
                if not self.config.get('info_boxes', True):
                    return []
                
                return self.design_system.create_professional_info_box(
                    title, content, box_type, self.color_scheme
                )
            
            def create_section_header(self, title: str, subtitle: str = "") -> List:
                """Erstellt modernen Abschnitt-Header"""
                if not self.config.get('modern_headers', True):
                    return []
                
                return self.design_system.create_modern_header_section(
                    title, subtitle, color_scheme=self.color_scheme
                )
            
            def get_enhanced_styles(self) -> Dict:
                """Gibt erweiterte Styles zurück"""
                if not self.config.get('enhanced_typography', True):
                    return {}
                
                return self.design_system.get_enhanced_paragraph_styles(self.color_scheme)
            
            def get_enhanced_table_style(self, table_type: str = 'data'):
                """Gibt erweiterte Tabellen-Styles zurück"""
                if not self.config.get('modern_tables', True):
                    return None
                
                return self.design_system.create_enhanced_table_style(self.color_scheme, table_type)
        
        return ModernContentEnhancer()
        
    except Exception as e:
        # Graceful fallback
        print(f"Fehler beim Erstellen des Modern Content Enhancers: {e}")
        return None

# Hilfsfunktion für Integration in bestehende UI
def integrate_modern_design_section_into_existing_ui(texts: Dict[str, str], 
                                                   position: str = "before_submit") -> Dict[str, Any]:
    """
    Integriert die moderne Design-Sektion in die bestehende UI
    position: "before_submit", "after_sections", "in_sidebar"
    """
    if position == "before_submit":
        st.markdown("---")
        design_config = render_modern_pdf_design_ui(texts)
        st.markdown("---")
        return design_config
    elif position == "in_sidebar":
        with st.sidebar:
            st.markdown("### 🎨 Design-Optionen")
            design_config = render_modern_pdf_design_ui(texts)
        return design_config
    else:
        return render_modern_pdf_design_ui(texts)

# Export-Funktionen für andere Module
def get_modern_design_enabled() -> bool:
    """Prüft ob moderne Design-Features aktiviert sind"""
    return MODERN_DESIGN_AVAILABLE and st.session_state.get('pdf_modern_design_enabled', False)

def get_current_modern_color_scheme_name() -> str:
    """Gibt den Namen des aktuell gewählten Farbschemas zurück"""
    if not MODERN_DESIGN_AVAILABLE:
        return 'standard'
    
    scheme_names = list(get_available_modern_color_schemes().keys())
    scheme_index = st.session_state.get('pdf_modern_scheme_index', 0)
    
    if 0 <= scheme_index < len(scheme_names):
        return scheme_names[scheme_index]
    
    return 'premium_blue_modern'

def export_modern_design_config_for_pdf_generator() -> Dict[str, Any]:
    """
    Exportiert die vollständige Design-Konfiguration für PDF-Generatoren
    """
    base_config = get_modern_design_integration_config()
    
    if base_config.get('enabled', False):
        base_config['color_scheme_name'] = get_current_modern_color_scheme_name()
        
        # Zusätzliche Metadaten
        base_config['design_system_version'] = '1.0.0'
        base_config['available_schemes'] = list(get_available_modern_color_schemes().keys()) if MODERN_DESIGN_AVAILABLE else []
    
    return base_config
