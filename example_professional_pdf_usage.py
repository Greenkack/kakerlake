# example_professional_pdf_usage.py
# -*- coding: utf-8 -*-
"""
example_professional_pdf_usage.py

Beispiel-Implementierung für die Verwendung der professionellen PDF-Templates.
Zeigt, wie die erweiterten Funktionen in bestehende Anwendungen integriert werden können.

Author: GitHub Copilot
Version: 1.0 - Beispiel und Demo
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime

# Import der professionellen PDF-Module
try:
    from pdf_ui_integration import render_enhanced_pdf_ui, get_template_recommendations
    from pdf_generator_professional import create_professional_pdf_with_template
    from pdf_professional_templates import get_all_professional_templates, get_template_preview_info
    _PROFESSIONAL_PDF_AVAILABLE = True
except ImportError:
    _PROFESSIONAL_PDF_AVAILABLE = False

def demo_professional_pdf_integration():
    """
    Demo-Funktion, die zeigt, wie die professionellen PDF-Templates 
    in eine bestehende Streamlit-Anwendung integriert werden können.
    """
    
    if not _PROFESSIONAL_PDF_AVAILABLE:
        st.error("❌ Professionelle PDF-Module nicht verfügbar")
        return
    
    st.title("🌟 Professionelle PDF-Templates - Demo")
    st.markdown("---")
    
    # Demo-Daten erstellen
    demo_project_data = {
        'customer_name': 'Mustermann GmbH',
        'system_power': 25.6,
        'annual_yield': 24500,
        'investment_cost': 35000,
        'location': 'München',
        'roof_area': 180,
        'module_count': 64
    }
    
    demo_analysis_results = {
        'annual_savings': 2800,
        'payback_period': 12.5,
        'co2_savings_annual': 12500,
        'self_consumption_rate': 0.65,
        'roi_20_years': 18500
    }
    
    demo_company_details = {
        'name': 'Solar Excellence GmbH',
        'id': 1,
        'address': 'Sonnenstraße 123, 80333 München',
        'phone': '+49 89 123456789',
        'email': 'info@solar-excellence.de',
        'logo_base64': None
    }
    
    # Template-Auswahl Demo
    st.markdown("### 🎨 Verfügbare Templates")
    
    try:
        available_templates = get_all_professional_templates()
    except:
        available_templates = ["Executive Report", "Solar Professional", "Premium Minimal", "Modern Tech"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_template = st.selectbox(
            "Wählen Sie ein Template:",
            available_templates,
            index=0
        )
        
        # Template-Empfehlungen
        recommendations = get_template_recommendations(demo_project_data)
        if selected_template in recommendations:
            st.success(f"✅ **{selected_template}** wird für dieses Projekt empfohlen!")
        else:
            st.info(f"💡 Empfohlen für dieses Projekt: {', '.join(recommendations)}")
    
    with col2:
        # Template-Informationen
        try:
            template_info = get_template_preview_info(selected_template)
            st.markdown(f"**{template_info['name']}**")
            st.write(template_info['description'])
            
            # Farbvorschau
            st.markdown("**Farbpalette:**")
            colors_html = f"""
            <div style="display: flex; gap: 5px; margin: 10px 0;">
                <div style="width: 30px; height: 30px; background-color: {template_info['primary_color']}; border-radius: 3px;" title="Primärfarbe"></div>
                <div style="width: 30px; height: 30px; background-color: {template_info['secondary_color']}; border-radius: 3px;" title="Sekundärfarbe"></div>
                <div style="width: 30px; height: 30px; background-color: {template_info['accent_color']}; border-radius: 3px;" title="Akzentfarbe"></div>
            </div>
            """
            st.markdown(colors_html, unsafe_allow_html=True)
            
        except:
            st.write("Template-Informationen werden geladen...")
    
    st.markdown("---")
    
    # Anpassungsoptionen Demo
    st.markdown("### ⚙️ Anpassungsoptionen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Layout-Optionen**")
        include_cover = st.checkbox("Deckblatt", value=True)
        include_toc = st.checkbox("Inhaltsverzeichnis", value=False)
        page_numbers = st.checkbox("Seitenzahlen", value=True)
    
    with col2:
        st.markdown("**Inhalts-Module**")
        include_summary = st.checkbox("Zusammenfassung", value=True)
        include_technical = st.checkbox("Technische Details", value=True)
        include_financial = st.checkbox("Wirtschaftlichkeit", value=True)
        include_charts = st.checkbox("Diagramme", value=True)
    
    with col3:
        st.markdown("**Stil-Optionen**")
        language_style = st.selectbox("Ansprache", ["Professionell (Sie)", "Persönlich (Du)"])
        detail_level = st.selectbox("Detailgrad", ["Kompakt", "Standard", "Ausführlich"])
    
    # Customizations-Dictionary erstellen
    customizations = {
        'include_cover_page': include_cover,
        'include_table_of_contents': include_toc,
        'page_numbers': page_numbers,
        'include_executive_summary': include_summary,
        'include_technical_details': include_technical,
        'include_financial_analysis': include_financial,
        'include_charts': include_charts,
        'include_environmental_impact': True,
        'language_style': language_style,
        'detail_level': detail_level,
        'custom_company_name': demo_company_details['name'],
        'custom_offer_title': 'Ihr maßgeschneidertes Photovoltaik-Angebot'
    }
    
    st.markdown("---")
    
    # Projekt-Übersicht
    st.markdown("### 📊 Projekt-Übersicht")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Anlagenleistung",
            f"{demo_project_data['system_power']} kWp",
            delta=f"{demo_project_data['module_count']} Module"
        )
    
    with col2:
        st.metric(
            "Jahresertrag",
            f"{demo_project_data['annual_yield']:,} kWh",
            delta=f"{demo_analysis_results['self_consumption_rate']*100:.0f}% Eigenverbrauch"
        )
    
    with col3:
        st.metric(
            "Investition",
            f"{demo_project_data['investment_cost']:,} €",
            delta=f"Amortisation: {demo_analysis_results['payback_period']:.1f} Jahre"
        )
    
    with col4:
        st.metric(
            "CO₂-Einsparung",
            f"{demo_analysis_results['co2_savings_annual']:,} kg/Jahr",
            delta="Umweltschutz"
        )
    
    st.markdown("---")
    
    # PDF-Generierung Demo
    st.markdown("### 🚀 PDF-Generierung")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📄 Demo-PDF erstellen", type="primary", use_container_width=True):
            generate_demo_pdf(demo_project_data, demo_analysis_results, demo_company_details, 
                            selected_template, customizations)

def generate_demo_pdf(project_data: Dict[str, Any], analysis_results: Dict[str, Any], 
                     company_details: Dict[str, Any], template_name: str, customizations: Dict[str, Any]):
    """
    Generiert ein Demo-PDF mit den professionellen Templates.
    """
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔄 Bereite Demo-Daten vor...")
        progress_bar.progress(20)
        
        # Demo-Angebotsdaten zusammenstellen
        offer_data = {
            'project_data': project_data,
            'analysis_results': analysis_results,
            'company': company_details,
            'customer': {
                'name': project_data['customer_name'],
                'location': project_data['location']
            },
            'offer_id': f"DEMO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'date': datetime.now().strftime('%d.%m.%Y')
        }
        
        progress_bar.progress(40)
        status_text.text("🎨 Wende Template an...")
        
        # Dateiname für Demo
        filename = f"demo_{template_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        progress_bar.progress(60)
        status_text.text("📄 Erstelle PDF...")
        
        # PDF mit professionellem Template erstellen
        pdf_path = create_professional_pdf_with_template(
            offer_data=offer_data,
            template_name=template_name,
            customizations=customizations,
            filename=filename
        )
        
        progress_bar.progress(80)
        status_text.text("✅ PDF erfolgreich erstellt!")
        
        progress_bar.progress(100)
        
        # Download-Button anzeigen
        import os
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.success(f"✅ Demo-PDF erfolgreich erstellt!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Demo-PDF herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            
            # Zusätzliche Informationen
            st.info(f"""
            📋 **PDF-Details:**
            - Template: {template_name}
            - Seiten: ~{estimate_pages(customizations)}
            - Größe: {len(pdf_bytes) / 1024:.1f} KB
            - Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
            """)
            
        else:
            st.error("❌ PDF-Datei konnte nicht gefunden werden")
    
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("❌ Fehler bei der PDF-Erstellung")
        st.error(f"Fehler bei der Demo-PDF-Generierung: {str(e)}")
        
        # Debug-Informationen für Entwicklung
        with st.expander("🔧 Debug-Informationen"):
            st.code(f"""
Template: {template_name}
Customizations: {customizations}
Error: {str(e)}
            """)

def estimate_pages(customizations: Dict[str, Any]) -> int:
    """Schätzt die Anzahl der PDF-Seiten."""
    pages = 1  # Mindestens eine Seite
    
    if customizations.get('include_cover_page', True):
        pages += 1
    if customizations.get('include_executive_summary', True):
        pages += 1
    if customizations.get('include_technical_details', True):
        pages += 1 if customizations.get('detail_level') == 'Kompakt' else 2
    if customizations.get('include_financial_analysis', True):
        pages += 2
    if customizations.get('include_charts', True):
        pages += 1
    
    return pages

def show_integration_examples():
    """
    Zeigt Beispiele für die Integration in bestehende Anwendungen.
    """
    
    st.markdown("### 💻 Integration in bestehende Anwendungen")
    
    st.markdown("""
    Die professionellen PDF-Templates können einfach in bestehende Anwendungen integriert werden:
    """)
    
    # Code-Beispiel 1: Ersetzung der bestehenden PDF-UI
    st.markdown("#### 1. Ersetzung der bestehenden PDF-UI")
    
    code_example_1 = '''
# Bestehender Code:
from pdf_ui import render_pdf_ui

result = render_pdf_ui(texts, project_data, analysis_results, ...)

# Neuer Code (Drop-in Replacement):
from pdf_ui_integration import render_enhanced_pdf_ui

result = render_enhanced_pdf_ui(texts, project_data, analysis_results, ...)
    '''
    
    st.code(code_example_1, language='python')
    
    # Code-Beispiel 2: Direkte Verwendung der professionellen Generator
    st.markdown("#### 2. Direkte Verwendung des professionellen Generators")
    
    code_example_2 = '''
from pdf_generator_professional import create_professional_pdf_with_template

# Angebotsdaten vorbereiten
offer_data = {
    'project_data': your_project_data,
    'analysis_results': your_analysis_results,
    'company': company_details,
    'customer': {'name': 'Kunde XY'},
    'offer_id': 'ANB-2025-001'
}

# Anpassungen definieren
customizations = {
    'include_cover_page': True,
    'include_charts': True,
    'language_style': 'Professionell (Sie)'
}

# PDF erstellen
pdf_path = create_professional_pdf_with_template(
    offer_data=offer_data,
    template_name="Executive Report",
    customizations=customizations,
    filename="angebot.pdf"
)
    '''
    
    st.code(code_example_2, language='python')
    
    # Code-Beispiel 3: Template-Auswahl in Streamlit
    st.markdown("#### 3. Template-Auswahl in Streamlit-Apps")
    
    code_example_3 = '''
from pdf_professional_ui import render_professional_template_selector

# Template-Auswahl rendern
selected_template = render_professional_template_selector()

# Anpassungen sammeln
customizations = render_professional_customization_panel(selected_template)

# Vorschau anzeigen
render_professional_preview_panel(selected_template, customizations)
    '''
    
    st.code(code_example_3, language='python')

# Hauptfunktion für die Demo-Seite
def main():
    """Hauptfunktion für die Demo-Anwendung."""
    
    st.set_page_config(
        page_title="Professionelle PDF-Templates Demo",
        page_icon="📄",
        layout="wide"
    )
    
    # Navigation
    tab1, tab2, tab3 = st.tabs(["🎨 Template-Demo", "💻 Integration", "📚 Dokumentation"])
    
    with tab1:
        demo_professional_pdf_integration()
    
    with tab2:
        show_integration_examples()
    
    with tab3:
        st.markdown("### 📚 Dokumentation")
        st.markdown("""
        #### Verfügbare Templates:
        
        1. **Executive Report**: Professionelles Unternehmens-Layout für hochwertige Angebote
        2. **Solar Professional**: Speziell für Solarenergie optimiert mit grünen Akzenten
        3. **Premium Minimal**: Elegantes, minimalistisches Design für Premium-Kunden
        4. **Modern Tech**: Modernes, technologieorientiertes Design
        
        #### Anpassungsoptionen:
        
        - **Layout**: Deckblatt, Inhaltsverzeichnis, Seitenzahlen, Wasserzeichen
        - **Inhalte**: Modulare Auswahl von Inhaltsabschnitten
        - **Stil**: Firmenfarben, Logo, Sprachstil, Detailgrad
        
        #### Integration:
        
        Die professionellen Templates erweitern das bestehende System ohne dessen 
        Funktionalität zu beeinträchtigen. Alle bestehenden Codes bleiben funktionsfähig.
        """)

if __name__ == "__main__":
    main()
