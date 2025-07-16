#!/usr/bin/env python3
"""
Test der PDF-Vorschau-Funktionalität
"""

import streamlit as st
import sys
import os

# Aktuelles Verzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    st.set_page_config(
        page_title="PDF-Vorschau Test",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 PDF-Vorschau & Bearbeitung Test")
    st.markdown("---")
    
    try:
        from pdf_ui import show_advanced_pdf_preview
        from locales import load_translations
        
        # Test-Daten
        project_data = {
            "customer_data": {
                "salutation": "Herr",
                "title": "",
                "first_name": "Max",
                "last_name": "Mustermann", 
                "company_name": "",
                "address": "Musterstraße",
                "house_number": "123",
                "zip_code": "12345",
                "city": "Musterstadt"
            },
            "project_details": {
                "module_quantity": 20,
                "selected_module_id": 1144,
                "selected_inverter_id": 1145,
                "include_storage": True,
                "selected_storage_id": 1146
            }
        }
        
        analysis_results = {
            "anlage_kwp": 8.5,
            "yearly_generation_kwh": 8500,
            "eigenverbrauch_kwh": 3500,
            "einspeise_kwh": 5000,
            "cost_savings_yearly": 1200,
            "amortization_years": 12,
            "co2_savings_kg_yearly": 4250
        }
        
        texts = load_translations("de") or {}
        
        # PDF-Vorschau anzeigen
        pdf_result = show_advanced_pdf_preview(
            project_data=project_data,
            analysis_results=analysis_results,
            texts=texts
        )
        
        if pdf_result:
            st.success("✅ PDF erfolgreich erstellt und angezeigt!")
        
    except ImportError as e:
        st.error(f"❌ Import-Fehler: {e}")
        st.info("💡 Stellen Sie sicher, dass alle Module verfügbar sind.")
    
    except Exception as e:
        st.error(f"❌ Fehler: {e}")
        st.code(f"Traceback: {str(e)}", language="text")

if __name__ == "__main__":
    main()
