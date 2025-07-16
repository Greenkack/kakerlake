#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live-Debug-Skript: Analysiert echte Streamlit-Session-Daten
für PDF-Generierung und vergleicht Einzel- vs Multi-PDF Parameter
"""

import streamlit as st
import logging
import json
from typing import Dict, Any, List

def debug_live_pdf_data():
    """Analysiert Live-Daten aus der Streamlit Session für PDF-Debugging"""
    
    st.title("🔍 Live PDF-Debug-Analyse")
    st.markdown("Analysiert die echten Session-Daten für PDF-Generierung")
    
    # Session State Keys analysieren
    st.subheader("📋 Session State Übersicht")
    
    important_keys = [
        'calculation_results', 
        'multi_offer_calc_results',
        'project_data',
        'pdf_inclusion_options',
        'pdf_selected_main_sections',
        'TEXTS'
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Verfügbare Session Keys:**")
        for key in important_keys:
            if key in st.session_state:
                data = st.session_state[key]
                if isinstance(data, dict):
                    st.success(f"✅ {key}: {len(data)} Einträge")
                elif isinstance(data, list):
                    st.success(f"✅ {key}: {len(data)} Elemente")
                else:
                    st.success(f"✅ {key}: {type(data).__name__}")
            else:
                st.error(f"❌ {key}: Nicht vorhanden")
    
    with col2:
        st.write("**Chart-Verfügbarkeit:**")
        calc_results = st.session_state.get('calculation_results', {})
        if calc_results:
            chart_keys = [k for k in calc_results.keys() if k.endswith('_chart_bytes')]
            chart_with_data = [k for k in chart_keys if calc_results.get(k) is not None]
            
            st.metric("Gesamt Charts", len(chart_keys))
            st.metric("Charts mit Daten", len(chart_with_data))
            
            if chart_with_data:
                st.write("**Verfügbare Charts:**")
                for chart in chart_with_data[:5]:  # Erste 5 anzeigen
                    st.text(f"• {chart}")
        else:
            st.error("Keine calculation_results gefunden")
    
    # Detailanalyse
    st.subheader("🔬 Detailanalyse")
    
    # Tab-Layout für verschiedene Analysen
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Calculation Results", 
        "🏗️ Project Data", 
        "📄 PDF Settings",
        "🆚 Vergleich"
    ])
    
    with tab1:
        st.write("**Analysis/Calculation Results:**")
        calc_results = st.session_state.get('calculation_results', {})
        
        if calc_results:
            # KPIs anzeigen
            kpi_cols = st.columns(3)
            with kpi_cols[0]:
                st.metric("Anlage kWp", calc_results.get('anlage_kwp', 'N/A'))
            with kpi_cols[1]:
                st.metric("PV-Produktion", f"{calc_results.get('annual_pv_production_kwh', 'N/A')} kWh")
            with kpi_cols[2]:
                st.metric("Investition", f"{calc_results.get('total_investment_netto', 'N/A')} €")
            
            # Charts analysieren
            chart_keys = [k for k in calc_results.keys() if k.endswith('_chart_bytes')]
            if chart_keys:
                st.write(f"**{len(chart_keys)} Chart-Keys gefunden:**")
                chart_status = []
                for chart_key in chart_keys:
                    has_data = calc_results.get(chart_key) is not None
                    chart_status.append({
                        "Chart": chart_key,
                        "Status": "✅ Mit Daten" if has_data else "❌ Leer",
                        "Typ": type(calc_results.get(chart_key)).__name__
                    })
                
                st.dataframe(chart_status, use_container_width=True)
            else:
                st.warning("Keine Chart-Daten in calculation_results gefunden")
        else:
            st.error("Keine calculation_results in Session State")
    
    with tab2:
        st.write("**Project Data:**")
        project_data = st.session_state.get('project_data', {})
        
        if project_data:
            # Customer Data
            customer_data = project_data.get('customer_data', {})
            if customer_data:
                st.write("**Kundendaten:**")
                st.json({k: v for k, v in customer_data.items() if k in ['salutation', 'first_name', 'last_name', 'city']})
            
            # Project Details - KRITISCH!
            project_details = project_data.get('project_details', {})
            if project_details:
                st.write("**Project Details (KRITISCH für PDF):**")
                critical_fields = {
                    "selected_module_id": project_details.get("selected_module_id", "❌ NICHT GESETZT"),
                    "selected_inverter_id": project_details.get("selected_inverter_id", "❌ NICHT GESETZT"),
                    "selected_storage_id": project_details.get("selected_storage_id", "❌ NICHT GESETZT"),
                    "module_quantity": project_details.get("module_quantity", "❌ NICHT GESETZT"),
                    "include_storage": project_details.get("include_storage", "❌ NICHT GESETZT")
                }
                
                for field, value in critical_fields.items():
                    if "❌" in str(value):
                        st.error(f"{field}: {value}")
                    else:
                        st.success(f"{field}: {value}")
            else:
                st.error("Keine project_details gefunden - KRITISCHES PROBLEM!")
        else:
            st.error("Keine project_data in Session State")
    
    with tab3:
        st.write("**PDF-Einstellungen:**")
        
        # PDF Inclusion Options
        pdf_options = st.session_state.get('pdf_inclusion_options', {})
        if pdf_options:
            st.write("**Inclusion Options:**")
            st.json(pdf_options)
        else:
            st.warning("Keine pdf_inclusion_options - werden Defaults verwendet")
        
        # PDF Selected Sections
        pdf_sections = st.session_state.get('pdf_selected_main_sections', [])
        if pdf_sections:
            st.write("**Ausgewählte PDF-Sektionen:**")
            for i, section in enumerate(pdf_sections, 1):
                st.text(f"{i}. {section}")
        else:
            st.warning("Keine pdf_selected_main_sections - werden Defaults verwendet")
    
    with tab4:
        st.write("**Multi-PDF vs Einzel-PDF Vergleich:**")
        
        # Simuliere Multi-PDF Parameter (wie in multi_offer_generator.py)
        multi_sections = [
            "ProjectOverview",
            "TechnicalComponents", 
            "CostDetails",
            "Economics",
            "SimulationDetails",
            "CO2Savings", 
            "Visualizations",
            "FutureAspects"
        ]
        
        multi_options = {
            "include_company_logo": True,
            "include_product_images": True,
            "include_all_documents": False,
            "company_document_ids_to_include": [],
            "selected_charts_for_pdf": [],  # Wird dynamisch gefüllt
            "include_optional_component_details": True
        }
        
        # Normale PDF Parameter
        normal_sections = st.session_state.get('pdf_selected_main_sections', [])
        normal_options = st.session_state.get('pdf_inclusion_options', {})
        
        # Vergleich anzeigen
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Multi-PDF Parameter:**")
            st.write(f"Sektionen: {len(multi_sections)}")
            for section in multi_sections:
                st.text(f"• {section}")
            
            st.write("**Multi-PDF Options:**")
            for key, value in multi_options.items():
                st.text(f"• {key}: {value}")
        
        with col2:
            st.write("**Normale PDF Parameter:**")
            st.write(f"Sektionen: {len(normal_sections)}")
            for section in normal_sections:
                st.text(f"• {section}")
            
            st.write("**Normale PDF Options:**")
            for key, value in normal_options.items():
                if key == 'selected_charts_for_pdf':
                    st.text(f"• {key}: {len(value)} Charts")
                else:
                    st.text(f"• {key}: {value}")
        
        # Unterschiede hervorheben
        st.subheader("🔍 Gefundene Unterschiede:")
        
        # Sektions-Unterschiede
        missing_sections = set(normal_sections) - set(multi_sections)
        extra_sections = set(multi_sections) - set(normal_sections)
        
        if missing_sections:
            st.error(f"Multi-PDF fehlen Sektionen: {', '.join(missing_sections)}")
        if extra_sections:
            st.info(f"Multi-PDF hat zusätzliche Sektionen: {', '.join(extra_sections)}")
        
        # Options-Unterschiede
        for key in normal_options:
            if key not in multi_options:
                st.warning(f"Multi-PDF fehlt Option: {key}")
            elif key == 'selected_charts_for_pdf':
                normal_charts = len(normal_options.get(key, []))
                multi_charts = len(multi_options.get(key, []))
                if normal_charts != multi_charts:
                    st.error(f"Chart-Anzahl unterschiedlich: Normal={normal_charts}, Multi={multi_charts}")
    
    # Action Buttons
    st.subheader("🔧 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Session State aktualisieren"):
            st.rerun()
    
    with col2:
        if st.button("📊 Chart-Diagnose"):
            calc_results = st.session_state.get('calculation_results', {})
            chart_keys = [k for k in calc_results.keys() if k.endswith('_chart_bytes')]
            
            st.write("**Detaillierte Chart-Diagnose:**")
            for chart_key in chart_keys:
                chart_data = calc_results.get(chart_key)
                if chart_data is not None:
                    data_type = type(chart_data).__name__
                    data_size = len(chart_data) if hasattr(chart_data, '__len__') else 'N/A'
                    st.success(f"✅ {chart_key}: {data_type}, Size: {data_size}")
                else:
                    st.error(f"❌ {chart_key}: None")
    
    with col3:
        if st.button("💾 Debug-Daten exportieren"):
            debug_data = {
                "calculation_results_keys": list(st.session_state.get('calculation_results', {}).keys()),
                "project_data_structure": {
                    "has_customer_data": bool(st.session_state.get('project_data', {}).get('customer_data')),
                    "has_project_details": bool(st.session_state.get('project_data', {}).get('project_details')),
                    "project_details_keys": list(st.session_state.get('project_data', {}).get('project_details', {}).keys())
                },
                "pdf_settings": {
                    "sections": st.session_state.get('pdf_selected_main_sections', []),
                    "options_keys": list(st.session_state.get('pdf_inclusion_options', {}).keys())
                }
            }
            
            st.download_button(
                label="💾 Debug-Daten herunterladen",
                data=json.dumps(debug_data, indent=2, ensure_ascii=False),
                file_name="streamlit_pdf_debug.json",
                mime="application/json"
            )

if __name__ == "__main__":
    # Standalone ausführbar für direktes Debugging
    debug_live_pdf_data()
