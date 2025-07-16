"""
Streamlit Debug-Tool für PDF-Generierung
Dieses Tool wird dir genau zeigen, wo das Problem bei der PDF-Generierung liegt.
"""
import streamlit as st
import traceback
import json
from typing import Dict, Any, Optional
import sys
import os

def debug_header():
    """Zeigt Debug-Header an"""
    st.title("🔧 PDF Debug Tool")
    st.markdown("---")
    st.info("Dieses Tool hilft dabei, das Problem mit der PDF-Generierung zu identifizieren.")

def debug_session_state():
    """Debuggt den Session State"""
    st.subheader("📊 Session State Debug")
    
    with st.expander("Session State Inhalte"):
        # Alle relevanten Session State Keys anzeigen
        relevant_keys = [key for key in st.session_state.keys() if 
                        'project' in key.lower() or 
                        'analysis' in key.lower() or 
                        'customer' in key.lower() or
                        'pv' in key.lower() or
                        'pdf' in key.lower()]
        
        if relevant_keys:
            st.write("**Relevante Session State Keys:**")
            for key in sorted(relevant_keys):
                value = st.session_state.get(key)
                if isinstance(value, dict):
                    st.write(f"- `{key}`: Dict mit {len(value)} Einträgen")
                    if st.checkbox(f"Details für {key} anzeigen", key=f"show_{key}"):
                        st.json(value)
                else:
                    st.write(f"- `{key}`: {type(value).__name__} = {str(value)[:100]}...")
        else:
            st.warning("Keine relevanten Session State Keys gefunden")

def debug_project_data():
    """Debuggt die Projektdaten"""
    st.subheader("🏠 Projektdaten Debug")
    
    # Versuche Projektdaten aus verschiedenen Quellen zu holen
    project_data_sources = [
        ('st.session_state.project_data', st.session_state.get('project_data')),
        ('st.session_state.current_project_data', st.session_state.get('current_project_data')),
        ('st.session_state.project_details', st.session_state.get('project_details')),
    ]
    
    project_data = None
    for source_name, data in project_data_sources:
        if data and isinstance(data, dict):
            st.success(f"✅ Projektdaten gefunden in: `{source_name}`")
            project_data = data
            break
        else:
            st.error(f"❌ Keine Daten in: `{source_name}` ({type(data).__name__})")
    
    if project_data:
        with st.expander("Projektdaten Details"):
            st.json(project_data)
            
        # Spezifische Checks
        col1, col2, col3 = st.columns(3)
        
        with col1:
            customer_data = project_data.get('customer_data', {})
            if customer_data and customer_data.get('last_name'):
                st.success("✅ Kundendaten OK")
            else:
                st.error("❌ Kundendaten fehlen")
                
        with col2:
            pv_details = project_data.get('pv_details', {})
            project_details = project_data.get('project_details', {})
            modules_ok = (pv_details and pv_details.get('selected_modules')) or \
                        (project_details and project_details.get('module_quantity', 0) > 0)
            if modules_ok:
                st.success("✅ PV-Module OK")
            else:
                st.error("❌ PV-Module fehlen")
                
        with col3:
            company_info = project_data.get('company_information', {})
            if company_info and company_info.get('name'):
                st.success("✅ Firmeninfo OK")
            else:
                st.error("❌ Firmeninfo fehlt")
    
    return project_data

def debug_analysis_results():
    """Debuggt die Analyseergebnisse"""
    st.subheader("📈 Analyseergebnisse Debug")
    
    # Versuche Analyseergebnisse aus verschiedenen Quellen zu holen
    analysis_sources = [
        ('st.session_state.analysis_results', st.session_state.get('analysis_results')),
        ('st.session_state.current_analysis_results', st.session_state.get('current_analysis_results')),
        ('st.session_state.kpi_results', st.session_state.get('kpi_results')),
        ('st.session_state.calculation_results', st.session_state.get('calculation_results')),
    ]
    
    analysis_results = None
    for source_name, data in analysis_sources:
        if data and isinstance(data, dict) and len(data) > 0:
            st.success(f"✅ Analyseergebnisse gefunden in: `{source_name}`")
            analysis_results = data
            break
        else:
            st.error(f"❌ Keine Daten in: `{source_name}` ({type(data).__name__}, Länge: {len(data) if isinstance(data, dict) else 'N/A'})")
    
    if analysis_results:
        with st.expander("Analyseergebnisse Details"):
            st.json(analysis_results)
            
        # Wichtige KPIs prüfen
        important_kpis = ['anlage_kwp', 'annual_pv_production_kwh', 'total_investment_cost_netto']
        col1, col2, col3 = st.columns(3)
        
        for i, kpi in enumerate(important_kpis):
            with [col1, col2, col3][i]:
                value = analysis_results.get(kpi)
                if value:
                    st.success(f"✅ {kpi}: {value}")
                else:
                    st.error(f"❌ {kpi} fehlt")
    
    return analysis_results

def debug_pdf_validation(project_data, analysis_results):
    """Debuggt die PDF-Validierung"""
    st.subheader("🔍 PDF-Validierung Debug")
    
    try:
        # Texte für Validierung
        texts = {
            'pdf_warning_no_customer_name': 'Kein Kundenname verfügbar',
            'pdf_warning_no_modules': 'Keine PV-Module ausgewählt',
            'pdf_error_no_analysis': 'Keine Analyseergebnisse verfügbar',
            'pdf_warning_no_company': 'Keine Firmendaten verfügbar',
            'not_applicable_short': 'k.A.'
        }
        
        # Import der Validierungsfunktion
        from pdf_generator import _validate_pdf_data_availability
        
        st.info("Führe PDF-Validierung durch...")
        
        # Validierung durchführen
        validation_result = _validate_pdf_data_availability(
            project_data or {}, 
            analysis_results or {}, 
            texts
        )
        
        # Ergebnisse anzeigen
        col1, col2 = st.columns(2)
        
        with col1:
            if validation_result['is_valid']:
                st.success("✅ **PDF-Validierung: BESTANDEN**")
            else:
                st.error("❌ **PDF-Validierung: FEHLGESCHLAGEN**")
        
        with col2:
            st.metric("Warnungen", len(validation_result.get('warnings', [])))
            st.metric("Kritische Fehler", len(validation_result.get('critical_errors', [])))
        
        # Details anzeigen
        if validation_result.get('warnings'):
            st.warning("⚠️ **Warnungen:**")
            for warning in validation_result['warnings']:
                st.write(f"- {warning}")
        
        if validation_result.get('critical_errors'):
            st.error("❌ **Kritische Fehler:**")
            for error in validation_result['critical_errors']:
                st.write(f"- {error}")
        
        if validation_result.get('missing_data_summary'):
            st.info("📋 **Fehlende Daten:**")
            st.write(", ".join(validation_result['missing_data_summary']))
        
        return validation_result
        
    except Exception as e:
        st.error(f"Fehler bei der PDF-Validierung: {e}")
        st.code(traceback.format_exc())
        return None

def debug_pdf_generation(project_data, analysis_results):
    """Debuggt die PDF-Generierung"""
    st.subheader("📄 PDF-Generierung Debug")
    
    if st.button("🚀 Test-PDF generieren"):
        try:
            from pdf_generator import generate_offer_pdf
            
            # Basistexte
            texts = {
                'pdf_title': 'Debug-PDF',
                'pdf_warning_no_customer_name': 'Kein Kundenname verfügbar',
                'pdf_warning_no_modules': 'Keine PV-Module ausgewählt',
                'pdf_error_no_analysis': 'Keine Analyseergebnisse verfügbar',
                'pdf_warning_no_company': 'Keine Firmendaten verfügbar',
                'not_applicable_short': 'k.A.'
            }
            
            with st.spinner("PDF wird generiert..."):
                pdf_bytes = generate_offer_pdf(
                    project_data=project_data or {},
                    analysis_results=analysis_results or {},
                    company_info=project_data.get('company_information', {}) if project_data else {},
                    company_logo_base64=None,
                    selected_title_image_b64=None,
                    selected_offer_title_text="Debug-PDF",
                    selected_cover_letter_text="Debug-Anschreiben",
                    sections_to_include=["overview", "products", "economics"],
                    inclusion_options={
                        'include_company_logo': False,
                        'include_product_images': True,
                        'include_all_documents': False,
                        'company_document_ids_to_include': [],
                        'include_optional_component_details': True,
                        'include_custom_footer': True,
                        'include_header_logo': False
                    },
                    load_admin_setting_func=lambda key, default: default,
                    save_admin_setting_func=lambda key, value: None,
                    list_products_func=lambda: [],
                    get_product_by_id_func=lambda id: None,
                    db_list_company_documents_func=lambda company_id, doc_type=None: [],
                    active_company_id=1,
                    texts=texts
                )
            
            if pdf_bytes:
                st.success("✅ PDF erfolgreich generiert!")
                st.download_button(
                    label="📥 Debug-PDF herunterladen",
                    data=pdf_bytes,
                    file_name="debug_pdf.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("❌ PDF-Generierung fehlgeschlagen - keine Bytes zurückgegeben")
                
        except Exception as e:
            st.error(f"Fehler bei der PDF-Generierung: {e}")
            st.code(traceback.format_exc())

def debug_streamlit_state():
    """Debuggt spezifische Streamlit-Zustände"""
    st.subheader("🔧 Streamlit State Debug")
    
    # Prüfe PDF-bezogene Session State Variablen
    pdf_states = {
        'pdf_generating_lock_v1': st.session_state.get('pdf_generating_lock_v1'),
        'generated_pdf_bytes_for_download_v1': st.session_state.get('generated_pdf_bytes_for_download_v1'),
        'selected_page_key_sui': st.session_state.get('selected_page_key_sui'),
        'pdf_inclusion_options': st.session_state.get('pdf_inclusion_options'),
        'pdf_selected_main_sections': st.session_state.get('pdf_selected_main_sections')
    }
    
    for key, value in pdf_states.items():
        if value is not None:
            st.write(f"- `{key}`: {type(value).__name__} = {str(value)[:100]}...")
        else:
            st.write(f"- `{key}`: None")

def main():
    debug_header()
    
    # Debug Session State
    debug_session_state()
    st.markdown("---")
    
    # Debug Projektdaten
    project_data = debug_project_data()
    st.markdown("---")
    
    # Debug Analyseergebnisse
    analysis_results = debug_analysis_results()
    st.markdown("---")
    
    # Debug PDF-Validierung
    validation_result = debug_pdf_validation(project_data, analysis_results)
    st.markdown("---")
    
    # Debug PDF-Generierung
    debug_pdf_generation(project_data, analysis_results)
    st.markdown("---")
    
    # Debug Streamlit State
    debug_streamlit_state()
    st.markdown("---")
    
    # Zusammenfassung
    st.subheader("📋 Debug-Zusammenfassung")
    
    issues = []
    if not project_data:
        issues.append("❌ Keine Projektdaten gefunden")
    if not analysis_results:
        issues.append("❌ Keine Analyseergebnisse gefunden")
    if validation_result and not validation_result.get('is_valid'):
        issues.append("❌ PDF-Validierung fehlgeschlagen")
    
    if issues:
        st.error("**Gefundene Probleme:**")
        for issue in issues:
            st.write(issue)
    else:
        st.success("✅ Alle grundlegenden Checks bestanden!")
    
    # Raw Data Export für weitere Analyse
    if st.button("📤 Debug-Daten als JSON exportieren"):
        debug_data = {
            'project_data': project_data,
            'analysis_results': analysis_results,
            'validation_result': validation_result,
            'session_state_keys': list(st.session_state.keys()),
            'pdf_states': {
                key: str(st.session_state.get(key)) 
                for key in st.session_state.keys() 
                if 'pdf' in key.lower()
            }
        }
        
        st.download_button(
            label="💾 Debug-Daten herunterladen",
            data=json.dumps(debug_data, indent=2, ensure_ascii=False),
            file_name="pdf_debug_data.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
