# gui_integration_test.py
"""Test für die Integration der neuen Features in die Haupt-GUI"""

import streamlit as st
import os
import sys

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    st.set_page_config(
        page_title="Solar-App - Mit neuen Features",
        page_icon="☀️",
        layout="wide"
    )
    
    # Initialize session state
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "input"
    
    st.title("☀️ Solar-App - Erweiterte Version")
    st.markdown("---")
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🧭 Navigation")
        
        # Navigation buttons
        page_options = {
            "📝 Eingabe": "input",
            "📊 Analyse": "analysis", 
            "⚡ Schnellkalkulation": "quick_calc",
            "👥 Kunden (CRM)": "crm",
            "ℹ️ Info-Plattform": "info_platform",
            "⚙️ Optionen": "options",
            "👨‍💼 Admin": "admin",
            "📄 PDF-Ausgabe": "doc_output",
            "🤖 AI-Begleiter": "ai_companion",
            "🏢 Multi-Angebote": "multi_offers"
        }
        
        for label, key in page_options.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.selected_page = key
                st.rerun()
        
        # Current page indicator
        st.markdown("---")
        current_page_label = next((label for label, key in page_options.items() 
                                 if key == st.session_state.selected_page), "Unbekannt")
        st.markdown(f"**Aktuelle Seite:** {current_page_label}")
    
    # Main content area
    selected_page = st.session_state.selected_page
    
    if selected_page == "input":
        render_input_page()
    elif selected_page == "analysis":
        render_analysis_page()
    elif selected_page == "quick_calc":
        render_quick_calc_page()
    elif selected_page == "crm":
        render_crm_page()
    elif selected_page == "info_platform":
        render_info_platform_page()
    elif selected_page == "options":
        render_options_page()
    elif selected_page == "admin":
        render_admin_page()
    elif selected_page == "doc_output":
        render_doc_output_page()
    elif selected_page == "ai_companion":
        render_ai_companion_page()
    elif selected_page == "multi_offers":
        render_multi_offers_page()
    else:
        st.error(f"Unbekannte Seite: {selected_page}")

def render_input_page():
    st.header("📝 Dateneingabe")
    st.info("Diese Seite würde die normale Dateneingabe-Funktionalität enthalten.")
    
    # Beispiel für bestehende Funktionalität
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Kundendaten")
        st.text_input("Kundenname", placeholder="Max Mustermann")
        st.text_input("Adresse", placeholder="Musterstraße 123")
        
    with col2:
        st.subheader("Projektdaten")
        st.number_input("Anlagenleistung (kWp)", min_value=0.0, value=10.0, step=0.5)
        st.selectbox("Modultyp", ["Monokristallin", "Polykristallin", "Dünnschicht"])

def render_analysis_page():
    st.header("📊 Analyse")
    st.info("Diese Seite würde die Analyse-Funktionalität enthalten.")

def render_quick_calc_page():
    st.header("⚡ Schnellkalkulation")
    st.info("Diese Seite würde die Schnellkalkulations-Funktionalität enthalten.")

def render_crm_page():
    st.header("👥 Kunden (CRM)")
    st.info("Diese Seite würde die CRM-Funktionalität enthalten.")

def render_info_platform_page():
    st.header("ℹ️ Info-Plattform")
    st.info("Diese Seite würde die Info-Plattform-Funktionalität enthalten.")

def render_options_page():
    st.header("⚙️ Optionen")
    st.info("Diese Seite würde die Optionen-Funktionalität enthalten.")

def render_admin_page():
    st.header("👨‍💼 Admin")
    st.info("Diese Seite würde die Admin-Funktionalität enthalten.")

def render_doc_output_page():
    st.header("📄 PDF-Ausgabe")
    st.info("Diese Seite würde die PDF-Ausgabe-Funktionalität enthalten.")

def render_ai_companion_page():
    """Rendert die AI-Begleiter Seite"""
    st.header("🤖 AI-Begleiter (DeepSeek)")
    
    try:
        from ai_companion import render_ai_companion
        render_ai_companion()
    except ImportError as e:
        st.error(f"Fehler beim Laden des AI-Begleiters: {e}")
        st.info("Stellen Sie sicher, dass ai_companion.py verfügbar ist.")
    except Exception as e:
        st.error(f"Unerwarteter Fehler: {e}")
        st.code(str(e))

def render_multi_offers_page():
    """Rendert die Multi-Angebote Seite"""
    st.header("🏢 Multi-Firmen-Angebotsgenerator")
    
    try:
        from multi_offer_generator import render_multi_offer_generator
        render_multi_offer_generator()
    except ImportError as e:
        st.error(f"Fehler beim Laden des Multi-Angebotsgenerators: {e}")
        st.info("Stellen Sie sicher, dass multi_offer_generator.py verfügbar ist.")
    except Exception as e:
        st.error(f"Unerwarteter Fehler: {e}")
        st.code(str(e))

if __name__ == "__main__":
    main()
