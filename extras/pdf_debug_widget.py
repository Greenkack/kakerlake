"""
PDF Debug Widget für Integration in die SolarDING App
Dieses Widget kann direkt in die bestehende Streamlit-App eingebaut werden
"""
import streamlit as st
import traceback
import json
from typing import Dict, Any, Optional

def show_pdf_debug_widget(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]):
    """
    Zeigt ein Debug-Widget für die PDF-Generierung an
    
    Args:
        project_data: Die aktuellen Projektdaten
        analysis_results: Die aktuellen Analyseergebnisse
        texts: Text-Dictionary
    """
    
    # Debug-Widget in einem Expander
    with st.expander("🔧 PDF Debug-Informationen", expanded=False):
        st.markdown("**Debug-Informationen für PDF-Generierung**")
        
        # Tab-Layout für bessere Übersicht
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Daten", "🔍 Validierung", "🚀 Test", "💾 Export"])
        
        with tab1:
            st.subheader("Aktuelle Daten")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Projektdaten:**")
                if project_data:
                    st.success(f"✅ Projektdaten vorhanden ({len(project_data)} Keys)")
                    
                    # Wichtige Datenteile prüfen
                    customer_data = project_data.get('customer_data', {})
                    pv_details = project_data.get('pv_details', {})
                    project_details = project_data.get('project_details', {})
                    company_info = project_data.get('company_information', {})
                    
                    st.write(f"- Kundendaten: {'✅' if customer_data.get('last_name') else '❌'}")
                    st.write(f"- PV-Details: {'✅' if pv_details.get('selected_modules') else '❌'}")
                    st.write(f"- Projekt-Details: {'✅' if project_details else '❌'}")
                    st.write(f"- Firmeninfo: {'✅' if company_info.get('name') else '❌'}")
                    
                    if st.checkbox("Projektdaten Details anzeigen"):
                        st.json(project_data)
                else:
                    st.error("❌ Keine Projektdaten vorhanden")
            
            with col2:
                st.write("**Analyseergebnisse:**")
                if analysis_results:
                    st.success(f"✅ Analyseergebnisse vorhanden ({len(analysis_results)} Keys)")
                    
                    # Wichtige KPIs prüfen
                    important_kpis = ['anlage_kwp', 'annual_pv_production_kwh', 'total_investment_cost_netto']
                    for kpi in important_kpis:
                        value = analysis_results.get(kpi)
                        st.write(f"- {kpi}: {'✅' if value else '❌'} ({value})")
                    
                    if st.checkbox("Analyseergebnisse Details anzeigen"):
                        st.json(analysis_results)
                else:
                    st.error("❌ Keine Analyseergebnisse vorhanden")
        
        with tab2:
            st.subheader("PDF-Validierung")
            
            try:
                from pdf_generator import _validate_pdf_data_availability
                
                # Validierung durchführen
                validation_result = _validate_pdf_data_availability(
                    project_data or {}, 
                    analysis_results or {}, 
                    texts
                )
                
                # Ergebnisse anzeigen
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if validation_result['is_valid']:
                        st.success("✅ **GÜLTIG**")
                    else:
                        st.error("❌ **UNGÜLTIG**")
                
                with col2:
                    st.metric("Warnungen", len(validation_result.get('warnings', [])))
                
                with col3:
                    st.metric("Kritische Fehler", len(validation_result.get('critical_errors', [])))
                
                # Details
                if validation_result.get('warnings'):
                    st.warning("**Warnungen:**")
                    for warning in validation_result['warnings']:
                        st.write(f"⚠️ {warning}")
                
                if validation_result.get('critical_errors'):
                    st.error("**Kritische Fehler:**")
                    for error in validation_result['critical_errors']:
                        st.write(f"❌ {error}")
                
                if validation_result.get('missing_data_summary'):
                    st.info("**Fehlende Daten:**")
                    st.write(", ".join(validation_result['missing_data_summary']))
                
                # Debugging-Ausgabe
                st.write("**Validation Result (Raw):**")
                st.json(validation_result)
                
            except Exception as e:
                st.error(f"❌ Fehler bei der Validierung: {e}")
                st.code(traceback.format_exc())
        
        with tab3:
            st.subheader("PDF-Generierungstest")
            
            if st.button("🚀 Test-PDF generieren", help="Generiert eine Test-PDF mit den aktuellen Daten"):
                try:
                    from pdf_generator import generate_offer_pdf
                    
                    with st.spinner("PDF wird generiert..."):
                        pdf_bytes = generate_offer_pdf(
                            project_data=project_data or {},
                            analysis_results=analysis_results or {},
                            company_info=project_data.get('company_information', {}) if project_data else {},
                            company_logo_base64=None,
                            selected_title_image_b64=None,
                            selected_offer_title_text="Test-PDF Debug",
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
                            file_name="debug_test.pdf",
                            mime="application/pdf"
                        )
                        
                        # Analysiere PDF-Größe
                        pdf_size = len(pdf_bytes)
                        st.info(f"PDF-Größe: {pdf_size:,} Bytes ({pdf_size/1024:.1f} KB)")
                        
                    else:
                        st.error("❌ PDF-Generierung fehlgeschlagen - keine Bytes zurückgegeben")
                        
                except Exception as e:
                    st.error(f"❌ Fehler bei der PDF-Generierung: {e}")
                    st.code(traceback.format_exc())
        
        with tab4:
            st.subheader("Debug-Daten Export")
            
            if st.button("📤 Debug-Daten als JSON exportieren"):
                debug_data = {
                    'timestamp': str(st._get_widget_id()),
                    'project_data': project_data,
                    'analysis_results': analysis_results,
                    'session_state_keys': list(st.session_state.keys()),
                    'pdf_session_keys': {
                        key: str(st.session_state.get(key)) 
                        for key in st.session_state.keys() 
                        if 'pdf' in key.lower()
                    }
                }
                
                try:
                    # Validierungsergebnis hinzufügen
                    from pdf_generator import _validate_pdf_data_availability
                    validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
                    debug_data['validation_result'] = validation_result
                except:
                    debug_data['validation_result'] = "Fehler beim Abrufen"
                
                st.download_button(
                    label="💾 Debug-Daten herunterladen",
                    data=json.dumps(debug_data, indent=2, ensure_ascii=False, default=str),
                    file_name="pdf_debug_data.json",
                    mime="application/json"
                )
                
                st.success("Debug-Daten bereit zum Download!")

def add_debug_console_output():
    """Fügt Debug-Ausgaben zur Konsole hinzu"""
    
    # JavaScript für Console-Logging
    console_js = """
    <script>
    console.log("=== PDF DEBUG START ===");
    console.log("Session State Keys:", Object.keys(window.parent.streamlit.session_state || {}));
    console.log("Current URL:", window.location.href);
    console.log("=== PDF DEBUG END ===");
    </script>
    """
    
    st.components.v1.html(console_js, height=0)

def show_detailed_session_state():
    """Zeigt detaillierte Session State Informationen"""
    
    with st.expander("🗂️ Detaillierter Session State", expanded=False):
        st.subheader("Session State Analyse")
        
        # Alle Keys kategorisieren
        all_keys = list(st.session_state.keys())
        
        categories = {
            'PDF': [k for k in all_keys if 'pdf' in k.lower()],
            'Project': [k for k in all_keys if 'project' in k.lower()],
            'Analysis': [k for k in all_keys if 'analysis' in k.lower()],
            'Customer': [k for k in all_keys if 'customer' in k.lower()],
            'PV': [k for k in all_keys if 'pv' in k.lower()],
            'Other': [k for k in all_keys if not any(cat.lower() in k.lower() for cat in ['pdf', 'project', 'analysis', 'customer', 'pv'])]
        }
        
        for category, keys in categories.items():
            if keys:
                st.write(f"**{category} ({len(keys)} Keys):**")
                for key in sorted(keys):
                    value = st.session_state.get(key)
                    if isinstance(value, dict):
                        st.write(f"- `{key}`: Dict mit {len(value)} Einträgen")
                    elif isinstance(value, list):
                        st.write(f"- `{key}`: Liste mit {len(value)} Elementen")
                    else:
                        value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        st.write(f"- `{key}`: {type(value).__name__} = {value_str}")

# Hilfsfunktion zur einfachen Integration
def integrate_pdf_debug(project_data, analysis_results, texts):
    """
    Einfache Integration des Debug-Widgets in bestehende UI
    
    Verwendung:
    from pdf_debug_widget import integrate_pdf_debug
    integrate_pdf_debug(project_data, analysis_results, texts)
    """
    
    # Debug-Widget nur anzeigen wenn bestimmte Bedingung erfüllt ist
    if st.sidebar.checkbox("🔧 PDF Debug aktivieren", help="Aktiviert erweiterte Debug-Informationen"):
        show_pdf_debug_widget(project_data, analysis_results, texts)
        add_debug_console_output()
        show_detailed_session_state()
        
        # Zusätzliche Debug-Meldungen in der Sidebar
        with st.sidebar:
            st.markdown("---")
            st.subheader("🔧 Debug Status")
            
            if project_data:
                st.success("✅ Projektdaten")
            else:
                st.error("❌ Projektdaten")
            
            if analysis_results:
                st.success("✅ Analyseergebnisse")
            else:
                st.error("❌ Analyseergebnisse")
            
            # Quick-Test Button
            if st.button("⚡ Quick-Validierung"):
                try:
                    from pdf_generator import _validate_pdf_data_availability
                    result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
                    if result['is_valid']:
                        st.success("✅ Validierung OK")
                    else:
                        st.error(f"❌ Validierung fehlgeschlagen: {len(result['critical_errors'])} Fehler")
                except Exception as e:
                    st.error(f"❌ Validierung-Error: {str(e)[:50]}...")
