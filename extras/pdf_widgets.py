#!/usr/bin/env python3
"""
Erweiterte Widgets für die PDF-Vorschau
Drag & Drop ähnliche Funktionalität und Template-Verwaltung
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import json

def create_drag_drop_section_manager(
    available_sections: Dict[str, Dict[str, str]],
    session_key_order: str = "pdf_page_order",
    session_key_pool: str = "available_sections_pool"
) -> List[str]:
    """
    Erstellt eine erweiterte Drag & Drop ähnliche Sektion-Verwaltung.
    
    Args:
        available_sections: Dict mit Sektions-IDs und deren Informationen
        session_key_order: Session State Key für die Reihenfolge
        session_key_pool: Session State Key für verfügbare Sektionen
    
    Returns:
        Aktuelle Seitenreihenfolge
    """
    
    # Session State initialisieren
    if session_key_order not in st.session_state:
        st.session_state[session_key_order] = [
            "ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"
        ]
    
    if session_key_pool not in st.session_state:
        st.session_state[session_key_pool] = [
            key for key in available_sections.keys() 
            if key not in st.session_state[session_key_order]
        ]
    
    # Template-Presets
    st.markdown("#### 📋 Template-Presets")
    col1, col2, col3, col4 = st.columns(4)
    
    presets = {
        "🎯 Standard": ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"],
        "📊 Ausführlich": ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics", "SimulationDetails", "CO2Savings", "Visualizations"],
        "🚀 Marketing": ["CompanyProfile", "References", "ProjectOverview", "TechnicalComponents", "CostDetails", "Financing", "Warranty"],
        "🔧 Technisch": ["ProjectOverview", "TechnicalComponents", "SimulationDetails", "Visualizations", "Installation", "Maintenance"]
    }
    
    for i, (preset_name, preset_sections) in enumerate(presets.items()):
        col = [col1, col2, col3, col4][i]
        with col:
            if st.button(preset_name, use_container_width=True):
                st.session_state[session_key_order] = [
                    s for s in preset_sections if s in available_sections
                ]
                st.session_state[session_key_pool] = [
                    key for key in available_sections.keys()
                    if key not in st.session_state[session_key_order]
                ]
                st.rerun()
    
    st.markdown("---")
    
    # Haupt-Verwaltungsbereich
    col_current, col_available = st.columns([1.2, 0.8])
    
    with col_current:
        st.markdown("#### 📋 Gewählte Seiten (Reihenfolge)")
        
        if not st.session_state[session_key_order]:
            st.info("ℹ️ Keine Seiten ausgewählt. Fügen Sie Seiten aus der rechten Spalte hinzu.")
        else:
            # Kompakte Darstellung mit besserer UX
            for i, section_key in enumerate(st.session_state[session_key_order]):
                section_info = available_sections.get(section_key, {
                    "title": section_key, 
                    "description": "Unbekannte Sektion"
                })
                
                with st.container():
                    col_pos, col_info, col_actions = st.columns([0.5, 2, 1])
                    
                    with col_pos:
                        st.markdown(f"**{i+1}.**")
                    
                    with col_info:
                        st.markdown(f"**{section_info['title']}**")
                        st.caption(section_info['description'])
                    
                    with col_actions:
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button("⬆️", key=f"up_{section_key}_{i}", help="Nach oben", disabled=(i == 0)):
                                st.session_state[session_key_order][i], st.session_state[session_key_order][i-1] = \
                                st.session_state[session_key_order][i-1], st.session_state[session_key_order][i]
                                st.rerun()
                        
                        with action_col2:
                            if st.button("⬇️", key=f"down_{section_key}_{i}", help="Nach unten", disabled=(i == len(st.session_state[session_key_order]) - 1)):
                                st.session_state[session_key_order][i], st.session_state[session_key_order][i+1] = \
                                st.session_state[session_key_order][i+1], st.session_state[session_key_order][i]
                                st.rerun()
                        
                        with action_col3:
                            if st.button("❌", key=f"remove_{section_key}_{i}", help="Entfernen"):
                                st.session_state[session_key_order].remove(section_key)
                                st.session_state[session_key_pool].append(section_key)
                                st.rerun()
                
                st.markdown("---")
    
    with col_available:
        st.markdown("#### 📚 Verfügbare Seiten")
        
        if not st.session_state[session_key_pool]:
            st.info("ℹ️ Alle Seiten wurden bereits hinzugefügt.")
        else:
            # Kategorisierung der verfügbaren Seiten
            categories = {
                "🏠 Basis": ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"],
                "📊 Analyse": ["SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects"],
                "🏢 Unternehmen": ["CompanyProfile", "Certifications", "References"],
                "🔧 Service": ["Installation", "Maintenance", "Warranty"],
                "💰 Finanzen": ["Financing", "Insurance"]
            }
            
            for category_name, category_sections in categories.items():
                available_in_category = [
                    s for s in category_sections 
                    if s in st.session_state[session_key_pool]
                ]
                
                if available_in_category:
                    with st.expander(f"{category_name} ({len(available_in_category)})", expanded=True):
                        for section_key in available_in_category:
                            section_info = available_sections.get(section_key, {
                                "title": section_key,
                                "description": "Unbekannte Sektion"
                            })
                            
                            col_info, col_add = st.columns([3, 1])
                            
                            with col_info:
                                st.markdown(f"**{section_info['title']}**")
                                st.caption(section_info['description'])
                            
                            with col_add:
                                if st.button("➕", key=f"add_{section_key}", help="Hinzufügen"):
                                    st.session_state[session_key_order].append(section_key)
                                    st.session_state[session_key_pool].remove(section_key)
                                    st.rerun()
    
    # Quick Actions
    st.markdown("---")
    st.markdown("#### ⚡ Quick Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("➕ Alle hinzufügen", use_container_width=True):
            st.session_state[session_key_order] = list(available_sections.keys())
            st.session_state[session_key_pool] = []
            st.rerun()
    
    with action_col2:
        if st.button("🗑️ Alle entfernen", use_container_width=True):
            st.session_state[session_key_pool] = list(available_sections.keys())
            st.session_state[session_key_order] = []
            st.rerun()
    
    with action_col3:
        if st.button("🔄 Reihenfolge umkehren", use_container_width=True):
            st.session_state[session_key_order] = st.session_state[session_key_order][::-1]
            st.rerun()
    
    with action_col4:
        if st.button("🎲 Zufällig mischen", use_container_width=True):
            import random
            random.shuffle(st.session_state[session_key_order])
            st.rerun()
    
    return st.session_state[session_key_order]


def create_pdf_settings_panel() -> Dict[str, Any]:
    """
    Erstellt ein Panel für PDF-Einstellungen und Layout-Optionen.
    
    Returns:
        Dictionary mit allen PDF-Einstellungen
    """
    
    st.markdown("#### ⚙️ PDF-Einstellungen")
    
    # Layout-Optionen
    with st.expander("🎨 Layout & Design", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            include_custom_footer = st.checkbox(
                "📄 Custom Footer", 
                value=True, 
                help="| Angebot TT.MMM.JJJJ | Seite xx von xxx |"
            )
            include_header_logo = st.checkbox(
                "🏢 Header-Logo", 
                value=True, 
                help="Firmenlogo rechts oben auf jeder Seite"
            )
            include_company_logo = st.checkbox(
                "🖼️ Deckblatt-Logo", 
                value=True,
                help="Firmenlogo auf dem Deckblatt"
            )
        
        with col2:
            include_product_images = st.checkbox(
                "📸 Produktbilder", 
                value=True,
                help="Bilder von Modulen, Wechselrichtern etc."
            )
            include_optional_details = st.checkbox(
                "ℹ️ Detaillierte Infos", 
                value=True,
                help="Ausführliche Komponentenbeschreibungen"
            )
            include_visualizations = st.checkbox(
                "📊 Diagramme", 
                value=True,
                help="Charts und grafische Auswertungen"
            )
    
    # Inhalts-Optionen
    with st.expander("📋 Inhalte & Anhänge"):
        include_all_documents = st.checkbox(
            "📎 Alle Dokumente anhängen", 
            value=False,
            help="Datenblätter und Firmendokumente als PDF-Anhang"
        )
        
        include_charts = st.multiselect(
            "📈 Spezifische Diagramme auswählen:",
            options=[
                "deckungsgrad_chart",
                "monthly_generation_chart", 
                "yearly_comparison_chart",
                "economics_chart",
                "co2_savings_chart"
            ],
            default=["deckungsgrad_chart", "monthly_generation_chart"] if include_visualizations else [],
            help="Wählen Sie spezifische Diagramme für die PDF aus"
        )
    
    # Erweiterte Optionen
    with st.expander("🔧 Erweiterte Optionen"):
        use_modern_design = st.checkbox(
            "✨ Modernes Design verwenden", 
            value=True,
            help="Nutzt die neue moderne Farbpalette und Typografie"
        )
        
        custom_title = st.text_input(
            "📝 Angebot-Titel anpassen:",
            value="Ihr individuelles Photovoltaik-Angebot",
            help="Titel auf dem Deckblatt der PDF"
        )
        
        custom_cover_letter = st.text_area(
            "📄 Anschreiben anpassen:",
            value="Sehr geehrter Kunde,\n\nwir freuen uns, Ihnen unser maßgeschneidertes Angebot für eine Photovoltaikanlage unterbreiten zu können.",
            height=100,
            help="Persönlicher Text auf dem Deckblatt"
        )
    
    return {
        "include_custom_footer": include_custom_footer,
        "include_header_logo": include_header_logo,
        "include_company_logo": include_company_logo,
        "include_product_images": include_product_images,
        "include_optional_component_details": include_optional_details,
        "include_all_documents": include_all_documents,
        "selected_charts_for_pdf": include_charts,
        "use_modern_design": use_modern_design,
        "custom_title": custom_title,
        "custom_cover_letter": custom_cover_letter
    }
