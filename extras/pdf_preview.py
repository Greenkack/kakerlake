#!/usr/bin/env python3
"""
PDF Vorschau und Bearbeitungsmodul für SolarDING
Ermöglicht Vorschau, Bearbeitung und individuelle Seitenreihenfolge
"""

import streamlit as st
import io
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

def show_pdf_preview_interface(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str],
    texts: Dict[str, str],
    generate_pdf_func: callable
) -> Optional[bytes]:
    """
    Zeigt die PDF-Vorschau-Benutzeroberfläche mit Bearbeitungsoptionen.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse  
        company_info: Firmendaten
        company_logo_base64: Firmenlogo
        texts: Übersetzungen
        generate_pdf_func: PDF-Generierungsfunktion
    
    Returns:
        PDF-Bytes oder None
    """
    
    st.subheader("🔍 PDF-Vorschau & Bearbeitung")
    st.markdown("---")
    
    # PDF-DESIGN OPTIONEN
    with st.expander("🎨 PDF-Design anpassen", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Layout-Optionen:**")
            include_custom_footer = st.checkbox("📄 Custom Footer mit Datum/Seite", value=True, help="| Angebot TT.MMM.JJJJ | Seite xx von xxx |")
            include_header_logo = st.checkbox("🏢 Firmenlogo rechts oben", value=True, help="Logo auf jeder Seite rechts oben")
            include_company_logo = st.checkbox("🖼️ Firmenlogo auf Deckblatt", value=True)
            include_product_images = st.checkbox("📸 Produktbilder einbinden", value=True)
            
        with col2:
            st.markdown("**Inhalts-Optionen:**")
            include_optional_details = st.checkbox("ℹ️ Detaillierte Komponenteninfos", value=True)
            include_visualizations = st.checkbox("📊 Diagramme & Grafiken", value=True)
            include_all_documents = st.checkbox("📋 Alle Anhänge einbinden", value=False)
    
    # SEITENAUSWAHL UND REIHENFOLGE (Das wird BOMBE!)
    st.markdown("### 🔥 SEITENREIHENFOLGE ANPASSEN (BOMBE!)")
    
    # Verfügbare Sektionen
    available_sections = {
        "ProjectOverview": {"title": "🏠 Projektübersicht & Eckdaten", "description": "Grunddaten der geplanten Anlage"},
        "TechnicalComponents": {"title": "🔧 Systemkomponenten", "description": "Module, Wechselrichter, Speicher"},
        "CostDetails": {"title": "💰 Kostenaufstellung", "description": "Detaillierte Preisübersicht"},
        "Economics": {"title": "📈 Wirtschaftlichkeit", "description": "Amortisation und Rendite"},
        "SimulationDetails": {"title": "🧮 Simulationsergebnisse", "description": "Ertragsprognose und Verbrauch"},
        "CO2Savings": {"title": "🌱 CO₂-Einsparung", "description": "Umweltbeitrag Ihrer Anlage"},
        "Visualizations": {"title": "📊 Grafische Auswertung", "description": "Charts und Diagramme"},
        "FutureAspects": {"title": "🚗 Zukunftsaspekte", "description": "E-Mobilität & Wärmepumpe"},
        
        # NEUE SEKTIONEN
        "CompanyProfile": {"title": "🏢 Unternehmensprofil", "description": "Über uns und Kontakt"},
        "Certifications": {"title": "🏆 Zertifizierungen", "description": "Qualitätsstandards & Auszeichnungen"},
        "References": {"title": "⭐ Kundenstimmen", "description": "Referenzen & Bewertungen"},
        "Installation": {"title": "🔨 Installation", "description": "Ablauf der Montagearbeiten"},
        "Maintenance": {"title": "🛠️ Wartung & Service", "description": "Langzeitbetreuung"},
        "Financing": {"title": "🏦 Finanzierung", "description": "KfW, Bank, Leasing-Optionen"},
        "Insurance": {"title": "🛡️ Versicherungsschutz", "description": "Absicherung Ihrer Investition"},
        "Warranty": {"title": "✅ Garantie", "description": "Herstellergarantien & Gewährleistung"}
    }
    
    # Session State für Seitenreihenfolge initialisieren
    if 'pdf_page_order' not in st.session_state:
        st.session_state.pdf_page_order = [
            "ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"
        ]
    
    if 'available_sections_pool' not in st.session_state:
        st.session_state.available_sections_pool = [
            key for key in available_sections.keys() 
            if key not in st.session_state.pdf_page_order
        ]
    
    # Drag & Drop ähnliche Benutzeroberfläche
    col_selected, col_available = st.columns([1, 1])
    
    with col_selected:
        st.markdown("**📋 Ausgewählte Seiten (in Reihenfolge):**")
        
        # Aktuelle Seitenreihenfolge anzeigen und bearbeiten
        for i, section_key in enumerate(st.session_state.pdf_page_order):
            section_info = available_sections.get(section_key, {"title": section_key, "description": ""})
            
            col_info, col_up, col_down, col_remove = st.columns([3, 0.5, 0.5, 0.5])
            
            with col_info:
                st.write(f"**{i+1}.** {section_info['title']}")
                st.caption(section_info['description'])
            
            with col_up:
                if st.button("⬆️", key=f"up_{section_key}_{i}", help="Nach oben"):
                    if i > 0:
                        st.session_state.pdf_page_order[i], st.session_state.pdf_page_order[i-1] = \
                        st.session_state.pdf_page_order[i-1], st.session_state.pdf_page_order[i]
                        st.rerun()
            
            with col_down:
                if st.button("⬇️", key=f"down_{section_key}_{i}", help="Nach unten"):
                    if i < len(st.session_state.pdf_page_order) - 1:
                        st.session_state.pdf_page_order[i], st.session_state.pdf_page_order[i+1] = \
                        st.session_state.pdf_page_order[i+1], st.session_state.pdf_page_order[i]
                        st.rerun()
            
            with col_remove:
                if st.button("❌", key=f"remove_{section_key}_{i}", help="Entfernen"):
                    st.session_state.pdf_page_order.remove(section_key)
                    st.session_state.available_sections_pool.append(section_key)
                    st.rerun()
            
            st.markdown("---")
    
    with col_available:
        st.markdown("**📚 Verfügbare Seiten:**")
        
        for section_key in st.session_state.available_sections_pool:
            section_info = available_sections.get(section_key, {"title": section_key, "description": ""})
            
            col_info, col_add = st.columns([3, 0.5])
            
            with col_info:
                st.write(section_info['title'])
                st.caption(section_info['description'])
            
            with col_add:
                if st.button("➕", key=f"add_{section_key}", help="Hinzufügen"):
                    st.session_state.pdf_page_order.append(section_key)
                    st.session_state.available_sections_pool.remove(section_key)
                    st.rerun()
            
            st.markdown("---")
    
    # QUICK ACTIONS
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Standard-Reihenfolge"):
            st.session_state.pdf_page_order = ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"]
            st.session_state.available_sections_pool = [
                key for key in available_sections.keys() 
                if key not in st.session_state.pdf_page_order
            ]
            st.rerun()
    
    with col2:
        if st.button("📋 Alle Seiten hinzufügen"):
            st.session_state.pdf_page_order = list(available_sections.keys())
            st.session_state.available_sections_pool = []
            st.rerun()
    
    with col3:
        if st.button("🗑️ Alle entfernen außer Basis"):
            st.session_state.pdf_page_order = ["ProjectOverview"]
            st.session_state.available_sections_pool = [
                key for key in available_sections.keys() 
                if key != "ProjectOverview"
            ]
            st.rerun()
    
    with col4:
        if st.button("🎯 Marketing-Fokus"):
            st.session_state.pdf_page_order = [
                "ProjectOverview", "CompanyProfile", "References", 
                "TechnicalComponents", "CostDetails", "Financing", "Warranty"
            ]
            st.session_state.available_sections_pool = [
                key for key in available_sections.keys() 
                if key not in st.session_state.pdf_page_order
            ]
            st.rerun()
    
    # PDF GENERIEREN UND VORSCHAU
    st.markdown("---")
    st.markdown("### 🚀 PDF erstellen")
    
    col_generate, col_info = st.columns([1, 2])
    
    with col_generate:
        if st.button("🔥 PDF GENERIEREN & VORSCHAU", type="primary", use_container_width=True):
            # Inclusion Options zusammenstellen
            inclusion_options = {
                "include_company_logo": include_company_logo,
                "include_product_images": include_product_images,
                "include_all_documents": include_all_documents,
                "include_optional_component_details": include_optional_details,
                "selected_charts_for_pdf": [] if not include_visualizations else ["deckungsgrad_chart", "monthly_generation_chart"],
                "include_custom_footer": include_custom_footer,
                "include_header_logo": include_header_logo
            }
            
            # PDF generieren mit angepasster Seitenreihenfolge
            try:
                with st.spinner("🔄 PDF wird erstellt..."):
                    pdf_bytes = generate_pdf_func(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        company_info=company_info,
                        company_logo_base64=company_logo_base64,
                        selected_title_image_b64=None,
                        selected_offer_title_text="Ihr individuelles Photovoltaik-Angebot",
                        selected_cover_letter_text="Sehr geehrter Kunde,\n\nwir freuen uns, Ihnen unser maßgeschneidertes Angebot für eine Photovoltaikanlage unterbreiten zu können.",
                        sections_to_include=st.session_state.pdf_page_order,  # CUSTOM REIHENFOLGE!
                        inclusion_options=inclusion_options,
                        load_admin_setting_func=lambda x, default=None: default,
                        save_admin_setting_func=lambda x, y: None,
                        list_products_func=lambda: [],
                        get_product_by_id_func=lambda x: {
                            "brand": "Test-Marke",
                            "model_name": "Test-Modell", 
                            "category": "modul",
                            "capacity_w": 425,
                            "efficiency_percent": 20.5
                        },
                        db_list_company_documents_func=lambda x, y: [],
                        active_company_id=1,
                        texts=texts,
                        use_modern_design=True
                    )
                
                if pdf_bytes:
                    st.success("✅ PDF erfolgreich erstellt!")
                    
                    # PDF Vorschau einbetten
                    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
                    
                    st.markdown("### 👀 PDF-VORSCHAU:")
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    
                    # Download-Button
                    st.download_button(
                        label="💾 PDF HERUNTERLADEN",
                        data=pdf_bytes,
                        file_name=f"Solar_Angebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    return pdf_bytes
                    
                else:
                    st.error("❌ Fehler bei der PDF-Erstellung!")
                    
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")
    
    with col_info:
        st.info(f"""
        📊 **Aktuelle Konfiguration:**
        - **Seiten:** {len(st.session_state.pdf_page_order)}
        - **Reihenfolge:** {' → '.join([available_sections.get(s, {}).get('title', s).split(' ')[1] if ' ' in available_sections.get(s, {}).get('title', s) else s for s in st.session_state.pdf_page_order[:3]])}{'...' if len(st.session_state.pdf_page_order) > 3 else ''}
        - **Layout:** {'✅' if include_custom_footer else '❌'} Footer, {'✅' if include_header_logo else '❌'} Header-Logo
        - **Inhalte:** {'✅' if include_optional_details else '❌'} Details, {'✅' if include_visualizations else '❌'} Grafiken
        """)
    
    return None


def create_pdf_template_presets() -> Dict[str, List[str]]:
    """
    Erstellt vordefinierte Template-Presets für verschiedene Anwendungsfälle.
    
    Returns:
        Dictionary mit Template-Namen und Sektionslisten
    """
    
    return {
        "Standard": [
            "ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"
        ],
        "Ausführlich": [
            "ProjectOverview", "TechnicalComponents", "CostDetails", 
            "Economics", "SimulationDetails", "CO2Savings", "Visualizations"
        ],
        "Marketing-Fokus": [
            "CompanyProfile", "References", "ProjectOverview", 
            "TechnicalComponents", "CostDetails", "Financing", "Warranty"
        ],
        "Technisch-detailliert": [
            "ProjectOverview", "TechnicalComponents", "SimulationDetails",
            "Visualizations", "CostDetails", "Installation", "Maintenance"
        ],
        "Verkaufs-optimiert": [
            "ProjectOverview", "Economics", "CO2Savings", "References",
            "TechnicalComponents", "Financing", "Insurance", "Warranty"
        ],
        "Kompakt": [
            "ProjectOverview", "TechnicalComponents", "CostDetails"
        ],
        "Vollständig": [
            "ProjectOverview", "TechnicalComponents", "CostDetails", "Economics",
            "SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects",
            "CompanyProfile", "Certifications", "References", "Installation",
            "Maintenance", "Financing", "Insurance", "Warranty"
        ]
    }
