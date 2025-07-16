"""
Session State Detective - Findet alle verfügbaren Daten im Session State
"""
import streamlit as st
import json
from typing import Dict, Any, List

def analyze_all_session_state():
    """Analysiert alle Session State Daten und kategorisiert sie"""
    
    st.title("🕵️ Session State Detective")
    st.markdown("Dieses Tool durchsucht **alle** Session State Daten und findet potenzielle Projektdaten und Analyseergebnisse.")
    
    # Alle Session State Keys holen
    all_keys = list(st.session_state.keys())
    
    st.info(f"📊 Gefunden: {len(all_keys)} Session State Keys")
    
    # Kategorisierung
    categories = {
        'Potential Project Data': [],
        'Potential Analysis Data': [],
        'Customer Data': [],
        'PV Data': [],
        'PDF Related': [],
        'UI State': [],
        'Other': []
    }
    
    # Alle Keys durchgehen und kategorisieren
    for key in all_keys:
        value = st.session_state.get(key)
        key_lower = key.lower()
        
        # Versuche herauszufinden, was die Daten enthalten
        is_dict = isinstance(value, dict)
        is_list = isinstance(value, list)
        has_content = value is not None and (
            (is_dict and len(value) > 0) or 
            (is_list and len(value) > 0) or 
            (not is_dict and not is_list)
        )
        
        if not has_content:
            continue
            
        # Kategorisierung basierend auf Key-Namen und Inhalten
        if any(word in key_lower for word in ['project', 'kunde', 'customer', 'daten', 'data']) and is_dict:
            if any(subkey in str(value).lower() for subkey in ['customer', 'pv', 'module', 'inverter', 'company']):
                categories['Potential Project Data'].append((key, value))
            else:
                categories['Other'].append((key, value))
        elif any(word in key_lower for word in ['analysis', 'kpi', 'calculation', 'result', 'berechnung']) and is_dict:
            if any(subkey in str(value).lower() for subkey in ['kwp', 'kwh', 'cost', 'euro', 'autarkie', 'eigenverbrauch']):
                categories['Potential Analysis Data'].append((key, value))
            else:
                categories['Other'].append((key, value))
        elif any(word in key_lower for word in ['customer', 'kunde']) and is_dict:
            categories['Customer Data'].append((key, value))
        elif any(word in key_lower for word in ['pv', 'solar', 'module', 'wechselrichter', 'inverter']) and (is_dict or is_list):
            categories['PV Data'].append((key, value))
        elif 'pdf' in key_lower:
            categories['PDF Related'].append((key, value))
        elif any(word in key_lower for word in ['page', 'tab', 'selected', 'current', 'active']):
            categories['UI State'].append((key, value))
        else:
            categories['Other'].append((key, value))
    
    # Ergebnisse anzeigen
    for category, items in categories.items():
        if items:
            with st.expander(f"📁 {category} ({len(items)} Items)", expanded=(category in ['Potential Project Data', 'Potential Analysis Data'])):
                for key, value in items:
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.code(key)
                        if isinstance(value, dict):
                            st.caption(f"Dict: {len(value)} keys")
                        elif isinstance(value, list):
                            st.caption(f"List: {len(value)} items")
                        else:
                            st.caption(f"{type(value).__name__}")
                    
                    with col2:
                        if isinstance(value, dict):
                            # Zeige Dict-Struktur
                            dict_keys = list(value.keys())
                            if len(dict_keys) <= 10:
                                st.write("Keys:", ", ".join(f"`{k}`" for k in dict_keys))
                            else:
                                st.write("Keys:", ", ".join(f"`{k}`" for k in dict_keys[:10]) + f" ... (+{len(dict_keys)-10} more)")
                            
                            # Zeige Werte-Beispiele
                            sample_data = {}
                            for k, v in list(value.items())[:3]:
                                if isinstance(v, (str, int, float, bool)):
                                    sample_data[k] = v
                                elif isinstance(v, dict):
                                    sample_data[k] = f"Dict({len(v)} keys)"
                                elif isinstance(v, list):
                                    sample_data[k] = f"List({len(v)} items)"
                                else:
                                    sample_data[k] = str(type(v).__name__)
                            
                            if sample_data:
                                st.json(sample_data)
                        
                        elif isinstance(value, list) and value:
                            st.write(f"First item: {type(value[0]).__name__}")
                            if len(value) <= 5:
                                st.write("Items:", value)
                            else:
                                st.write("Sample items:", value[:3], "...")
                        
                        else:
                            value_str = str(value)
                            if len(value_str) > 100:
                                st.write(value_str[:100] + "...")
                            else:
                                st.write(value_str)
    
    return categories

def find_potential_data():
    """Findet potenzielle Projekt- und Analysedaten"""
    
    st.header("🎯 Potenzielle Datenquellen")
    
    # Durchsuche alle Session State Daten nach Dictionary-Strukturen
    project_candidates = []
    analysis_candidates = []
    
    for key, value in st.session_state.items():
        if isinstance(value, dict) and len(value) > 0:
            value_str = str(value).lower()
            
            # Check for project data indicators
            project_indicators = ['customer', 'kunde', 'pv', 'module', 'wechselrichter', 'inverter', 'company', 'firma']
            project_score = sum(1 for indicator in project_indicators if indicator in value_str)
            
            # Check for analysis data indicators
            analysis_indicators = ['kwp', 'kwh', 'cost', 'kosten', 'euro', 'autarkie', 'eigenverbrauch', 'amortisation', 'co2']
            analysis_score = sum(1 for indicator in analysis_indicators if indicator in value_str)
            
            if project_score >= 2:
                project_candidates.append((key, value, project_score))
            
            if analysis_score >= 2:
                analysis_candidates.append((key, value, analysis_score))
    
    # Sortiere nach Score
    project_candidates.sort(key=lambda x: x[2], reverse=True)
    analysis_candidates.sort(key=lambda x: x[2], reverse=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Projekt-Daten Kandidaten")
        if project_candidates:
            for key, value, score in project_candidates:
                with st.expander(f"📊 {key} (Score: {score})"):
                    st.json(value)
                    
                    if st.button(f"Als project_data verwenden", key=f"use_project_{key}"):
                        st.session_state.project_data = value
                        st.success(f"✅ {key} als project_data gesetzt!")
                        st.rerun()
        else:
            st.warning("Keine Projekt-Daten-Kandidaten gefunden")
    
    with col2:
        st.subheader("📈 Analyse-Daten Kandidaten")
        if analysis_candidates:
            for key, value, score in analysis_candidates:
                with st.expander(f"📊 {key} (Score: {score})"):
                    st.json(value)
                    
                    if st.button(f"Als analysis_results verwenden", key=f"use_analysis_{key}"):
                        st.session_state.analysis_results = value
                        st.success(f"✅ {key} als analysis_results gesetzt!")
                        st.rerun()
        else:
            st.warning("Keine Analyse-Daten-Kandidaten gefunden")

def create_test_data():
    """Erstellt Test-Daten für die PDF-Generierung"""
    
    st.header("🧪 Test-Daten erstellen")
    st.info("Falls keine echten Daten gefunden werden, können hier Test-Daten erstellt werden.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Test-Projektdaten erstellen"):
            test_project_data = {
                'customer_data': {
                    'first_name': 'Max',
                    'last_name': 'Mustermann',
                    'address': 'Musterstraße 123',
                    'zip': '12345',
                    'city': 'Musterstadt',
                    'email': 'max.mustermann@example.com'
                },
                'pv_details': {
                    'selected_modules': [
                        {'id': 123, 'name': 'Test-Modul 400W', 'power_wp': 400}
                    ],
                    'module_quantity': 20
                },
                'project_details': {
                    'selected_inverter_id': 456,
                    'selected_inverter_name': 'Test-Wechselrichter 8kW',
                    'house_type': 'Einfamilienhaus',
                    'roof_type': 'Satteldach'
                },
                'company_information': {
                    'name': 'SolarDING Test GmbH',
                    'street': 'Firmenstraße 1',
                    'zip': '54321',
                    'city': 'Firmenstadt'
                }
            }
            
            st.session_state.project_data = test_project_data
            st.success("✅ Test-Projektdaten erstellt!")
            st.json(test_project_data)
    
    with col2:
        if st.button("📈 Test-Analysedaten erstellen"):
            test_analysis_results = {
                'anlage_kwp': 8.0,
                'annual_pv_production_kwh': 8500,
                'total_investment_cost_netto': 15000,
                'autarkie_anteil_prozent': 65,
                'eigenverbrauchs_anteil_prozent': 45,
                'yearly_co2_saved_kg': 4000,
                'amortization_years': 9.5,
                'stromkosten_alt_jahr': 2400,
                'stromkosten_neu_jahr': 850
            }
            
            st.session_state.analysis_results = test_analysis_results
            st.success("✅ Test-Analysedaten erstellt!")
            st.json(test_analysis_results)

def export_session_state():
    """Exportiert den kompletten Session State"""
    
    st.header("💾 Session State Export")
    
    if st.button("📤 Kompletten Session State exportieren"):
        # Konvertiere alle Daten zu JSON-serialisierbaren Formaten
        export_data = {}
        
        for key, value in st.session_state.items():
            try:
                # Teste ob JSON-serialisierbar
                json.dumps(value, default=str)
                export_data[key] = value
            except:
                # Falls nicht serialisierbar, konvertiere zu String
                export_data[key] = str(value)
        
        st.download_button(
            label="💾 Session State als JSON herunterladen",
            data=json.dumps(export_data, indent=2, ensure_ascii=False, default=str),
            file_name="session_state_complete.json",
            mime="application/json"
        )
        
        st.success("Session State Export bereit!")

def main():
    st.set_page_config(page_title="Session State Detective", page_icon="🕵️", layout="wide")
    
    # Sidebar Navigation
    st.sidebar.title("🕵️ Session State Detective")
    page = st.sidebar.radio("Navigation", [
        "🔍 Alle Daten analysieren",
        "🎯 Potenzielle Daten finden", 
        "🧪 Test-Daten erstellen",
        "💾 Session State exportieren"
    ])
    
    if page == "🔍 Alle Daten analysieren":
        analyze_all_session_state()
    elif page == "🎯 Potenzielle Daten finden":
        find_potential_data()
    elif page == "🧪 Test-Daten erstellen":
        create_test_data()
    elif page == "💾 Session State exportieren":
        export_session_state()
    
    # Quick Actions in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Quick Actions")
    
    if st.sidebar.button("🔄 Session State löschen"):
        st.session_state.clear()
        st.sidebar.success("Session State geleert!")
        st.rerun()
    
    # Zeige aktuelle Daten Status
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Aktueller Status")
    
    project_data = st.session_state.get('project_data')
    analysis_results = st.session_state.get('analysis_results')
    
    if project_data:
        st.sidebar.success("✅ project_data vorhanden")
    else:
        st.sidebar.error("❌ project_data fehlt")
    
    if analysis_results:
        st.sidebar.success("✅ analysis_results vorhanden")
    else:
        st.sidebar.error("❌ analysis_results fehlt")

if __name__ == "__main__":
    main()
