# doc_output_modern_patch.py
# -*- coding: utf-8 -*-
"""
Optionale Erweiterung für doc_output.py mit modernen Design-Features
Kann optional in bestehende UI integriert werden ohne Code-Änderungen
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import traceback

# Sichere Imports
try:
    from pdf_ui_design_enhancement import (
        integrate_modern_design_section_into_existing_ui,
        export_modern_design_config_for_pdf_generator,
        get_modern_design_enabled
    )
    from pdf_generator_modern_integration import (
        integrate_modern_design_into_existing_pdf_generation,
        check_modern_design_availability,
        get_integration_status_info
    )
    MODERN_INTEGRATION_AVAILABLE = True
except ImportError:
    MODERN_INTEGRATION_AVAILABLE = False

def render_modern_pdf_ui_enhancement(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable, 
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]] = None,
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Optionale Erweiterung der PDF-UI mit modernen Design-Features
    Kann in bestehende render_pdf_ui() Funktion integriert werden
    """
    
    if not MODERN_INTEGRATION_AVAILABLE:
        return None
    
    modern_design_config = None
    
    try:
        # Verfügbarkeitsprüfung
        availability = check_modern_design_availability()
        
        if availability.get('modern_design_system', False):
            # Moderne Design-UI rendern
            st.markdown("---")
            modern_design_config = integrate_modern_design_section_into_existing_ui(
                texts, position="before_submit"
            )
            
            # Zusätzliche Informationen falls verfügbar
            if modern_design_config.get('enabled', False):
                with st.expander("ℹ️ Informationen zu modernen Design-Features", expanded=False):
                    st.markdown("""
                    **🎨 Moderne Design-Features umfassen:**
                    
                    - **Erweiterte Farbschemata:** Professionelle Farbpaletten basierend auf modernen Design-Standards
                    - **Info-Boxen:** Stilvolle Hervorhebungen für wichtige Informationen
                    - **Moderne Typografie:** Verbesserte Schriftgrößen und -hierarchien
                    - **Erweiterte Tabellen:** Bessere Lesbarkeit durch moderne Tabellen-Designs
                    - **Bildergalerien:** Professionelle Produktpräsentation mit Beschreibungen
                    - **Finanz-Cards:** Moderne Darstellung von Wirtschaftlichkeitsdaten
                    - **Abschnitt-Header:** Professionelle Trennung der PDF-Bereiche
                    """)
                    
                    # Integrationsstatus anzeigen
                    st.code(get_integration_status_info())
        else:
            # Info über fehlende Features
            st.info("💡 **Moderne Design-Features:** Derzeit nicht verfügbar. Installieren Sie die erweiterten Design-Module für zusätzliche PDF-Gestaltungsoptionen.")
        
        return modern_design_config
        
    except Exception as e:
        st.warning(f"Warnung: Moderne Design-Features konnten nicht geladen werden: {e}")
        return None

def enhance_pdf_generation_with_modern_design(
    offer_data: Dict[str, Any],
    texts: Dict[str, str],
    template_name: str,
    modern_design_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Optional[str]:
    """
    Erweitert bestehende PDF-Generierung mit modernen Design-Features
    Falls moderne Features nicht verfügbar, fällt auf Standard-Generierung zurück
    """
    
    if not MODERN_INTEGRATION_AVAILABLE:
        return None
    
    try:
        # Moderne Design-Konfiguration in offer_data integrieren
        if modern_design_config and modern_design_config.get('enabled', False):
            # Design-Konfiguration zu Angebotsdaten hinzufügen
            if 'modern_design_config' not in offer_data:
                offer_data['modern_design_config'] = modern_design_config
        
        # Erweiterte PDF-Generierung mit modernem Design
        pdf_path = integrate_modern_design_into_existing_pdf_generation(
            offer_data=offer_data,
            texts=texts,
            template_name=template_name,
            **kwargs
        )
        
        return pdf_path
        
    except Exception as e:
        print(f"Fehler bei erweiterter PDF-Generierung: {e}")
        traceback.print_exc()
        return None

def show_modern_design_preview_if_enabled(modern_design_config: Optional[Dict[str, Any]],
                                        texts: Dict[str, str]):
    """
    Zeigt Vorschau der modernen Design-Features falls aktiviert
    """
    if not modern_design_config or not modern_design_config.get('enabled', False):
        return
    
    if not MODERN_INTEGRATION_AVAILABLE:
        return
    
    try:
        with st.expander("👀 **Vorschau: Moderne Design-Features**", expanded=False):
            st.markdown("### Ausgewählte Design-Konfiguration:")
            
            # Farbschema
            color_scheme_name = modern_design_config.get('color_scheme_name', 'Unbekannt')
            st.write(f"**🎨 Farbschema:** {color_scheme_name}")
            
            # Aktivierte Features
            activated_features = []
            feature_mapping = {
                'info_boxes': '📋 Info-Boxen',
                'enhanced_typography': '🔤 Erweiterte Typografie',
                'modern_tables': '📊 Moderne Tabellen',
                'enhanced_images': '🖼️ Erweiterte Bilddarstellung',
                'financial_cards': '💰 Finanz-Zusammenfassungen',
                'modern_headers': '🎯 Moderne Abschnitt-Header'
            }
            
            for feature_key, feature_name in feature_mapping.items():
                if modern_design_config.get(feature_key, False):
                    activated_features.append(feature_name)
            
            if activated_features:
                st.write("**✅ Aktivierte Features:**")
                for feature in activated_features:
                    st.write(f"  • {feature}")
            else:
                st.write("**ℹ️ Keine spezifischen Features aktiviert** (Grundlegende moderne Gestaltung wird angewendet)")
            
            # Beispiel-Vorschau
            st.markdown("---")
            st.markdown("**📋 Beispiel einer Info-Box:**")
            
            if modern_design_config.get('info_boxes', True):
                st.success("✅ **Erfolg:** Diese Art von stilvoller Info-Box wird in Ihrem PDF verwendet!")
                st.info("ℹ️ **Information:** Wichtige Details werden hervorgehoben dargestellt.")
                st.warning("⚠️ **Hinweis:** Besondere Aufmerksamkeit für wichtige Punkte.")
            else:
                st.write("Info-Boxen sind deaktiviert - Standard-Formatierung wird verwendet.")
            
    except Exception as e:
        st.warning(f"Vorschau konnte nicht angezeigt werden: {e}")

def integrate_modern_design_status_indicator(texts: Dict[str, str]):
    """
    Integriert Status-Indikator für moderne Design-Features
    """
    if not MODERN_INTEGRATION_AVAILABLE:
        return
    
    try:
        # Status in Sidebar oder als kleinen Indikator
        availability = check_modern_design_availability()
        
        if availability.get('full_integration_possible', False):
            if get_modern_design_enabled():
                st.sidebar.success("🎨 Moderne Design-Features: **Aktiviert**")
            else:
                st.sidebar.info("🎨 Moderne Design-Features: **Verfügbar**")
        elif availability.get('modern_design_system', False):
            st.sidebar.warning("🎨 Moderne Design-Features: **Teilweise verfügbar**")
        else:
            st.sidebar.error("🎨 Moderne Design-Features: **Nicht verfügbar**")
            
    except Exception:
        pass  # Stille Behandlung um Haupt-UI nicht zu stören

# Wrapper-Funktionen für einfache Integration in bestehende doc_output.py

def wrap_existing_pdf_ui_with_modern_features(original_render_pdf_ui_func):
    """
    Wrapper für bestehende render_pdf_ui Funktion um moderne Features zu erweitern
    """
    def enhanced_render_pdf_ui(*args, **kwargs):
        # Originale Funktion ausführen
        result = original_render_pdf_ui_func(*args, **kwargs)
        
        # Moderne Features hinzufügen falls verfügbar
        if MODERN_INTEGRATION_AVAILABLE and len(args) >= 3:
            texts = args[0] if len(args) > 0 else kwargs.get('texts', {})
            project_data = args[1] if len(args) > 1 else kwargs.get('project_data', {})
            analysis_results = args[2] if len(args) > 2 else kwargs.get('analysis_results', {})
            
            try:
                # Status-Indikator hinzufügen
                integrate_modern_design_status_indicator(texts)
                
                # Moderne Design-UI hinzufügen
                modern_config = render_modern_pdf_ui_enhancement(
                    texts, project_data, analysis_results,
                    *args[3:], **{k: v for k, v in kwargs.items() if k not in ['texts', 'project_data', 'analysis_results']}
                )
                
                # Vorschau anzeigen
                if modern_config:
                    show_modern_design_preview_if_enabled(modern_config, texts)
                
            except Exception as e:
                st.warning(f"Moderne Design-Features konnten nicht integriert werden: {e}")
        
        return result
    
    return enhanced_render_pdf_ui

def wrap_existing_pdf_generation_with_modern_features(original_generate_pdf_func):
    """
    Wrapper für bestehende PDF-Generierungsfunktion um moderne Features zu erweitern
    """
    def enhanced_generate_pdf(*args, **kwargs):
        # Moderne Design-Konfiguration aus Session State holen
        modern_config = None
        if MODERN_INTEGRATION_AVAILABLE:
            try:
                modern_config = export_modern_design_config_for_pdf_generator()
            except Exception:
                pass
        
        # Erweiterte PDF-Generierung versuchen
        if modern_config and modern_config.get('enabled', False):
            try:
                # Erweiterte Generierung
                enhanced_result = enhance_pdf_generation_with_modern_design(
                    *args, modern_design_config=modern_config, **kwargs
                )
                
                if enhanced_result:
                    return enhanced_result
            except Exception as e:
                print(f"Erweiterte PDF-Generierung fehlgeschlagen, Fallback auf Standard: {e}")
        
        # Fallback auf originale Funktion
        return original_generate_pdf_func(*args, **kwargs)
    
    return enhanced_generate_pdf

# Direkte Integration für schnelle Verwendung
def apply_modern_design_patch_to_existing_system():
    """
    Wendet moderne Design-Features auf das bestehende System an
    Nur verwenden wenn sichere Integration gewünscht ist
    """
    if not MODERN_INTEGRATION_AVAILABLE:
        return False
    
    try:
        # Hier könnte automatisches Patching implementiert werden
        # Derzeit nur informative Rückgabe
        return True
    except Exception:
        return False
