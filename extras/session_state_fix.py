
def consolidate_session_state():
    """
    Konsolidiert Session State Daten für die PDF-Generierung
    Füge diese Funktion in gui.py ein und rufe sie vor der PDF-Generierung auf
    """
    import streamlit as st
    
    # 1. PROJEKTDATEN KONSOLIDIERUNG
    if not st.session_state.get('project_data'):
        # Suche nach alternativen Project-Data Quellen
        potential_project_sources = [
            'current_project_data',
            'project_details', 
            'project_info',
            'projektdaten'
        ]
        
        for source in potential_project_sources:
            if st.session_state.get(source):
                st.session_state.project_data = st.session_state[source]
                print(f"📊 project_data aus {source} wiederhergestellt")
                break
        
        # Falls immer noch keine Daten, versuche Kombination
        if not st.session_state.get('project_data'):
            combined_data = {}
            
            # Kundendaten
            customer_sources = ['customer_data', 'kunde_daten', 'current_customer']
            for source in customer_sources:
                if st.session_state.get(source):
                    combined_data['customer_data'] = st.session_state[source]
                    break
            
            # PV-Daten  
            pv_sources = ['pv_details', 'pv_daten', 'solar_config']
            for source in pv_sources:
                if st.session_state.get(source):
                    combined_data['pv_details'] = st.session_state[source]
                    break
            
            # Projekt-Details
            detail_sources = ['project_details', 'projekt_details', 'installation_details']
            for source in detail_sources:
                if st.session_state.get(source):
                    combined_data['project_details'] = st.session_state[source]
                    break
            
            # Firmeninfo
            company_sources = ['company_information', 'firma_info', 'company_data']
            for source in company_sources:
                if st.session_state.get(source):
                    combined_data['company_information'] = st.session_state[source]
                    break
            
            if combined_data:
                st.session_state.project_data = combined_data
                print(f"📊 project_data aus kombinierten Quellen erstellt: {list(combined_data.keys())}")
    
    # 2. ANALYSEERGEBNISSE KONSOLIDIERUNG
    if not st.session_state.get('analysis_results'):
        # Suche nach alternativen Analysis-Data Quellen
        potential_analysis_sources = [
            'current_analysis_results',
            'kpi_results',
            'calculation_results',
            'berechnung_ergebnisse',
            'analysis_data',
            'wirtschaftlichkeit'
        ]
        
        for source in potential_analysis_sources:
            if st.session_state.get(source) and isinstance(st.session_state[source], dict):
                st.session_state.analysis_results = st.session_state[source]
                print(f"📈 analysis_results aus {source} wiederhergestellt")
                break
    
    # 3. DATENVALIDIERUNG
    project_data = st.session_state.get('project_data')
    analysis_results = st.session_state.get('analysis_results')
    
    print(f"🔍 Nach Konsolidierung:")
    print(f"  - project_data: {'✅' if project_data else '❌'} ({type(project_data).__name__})")
    print(f"  - analysis_results: {'✅' if analysis_results else '❌'} ({type(analysis_results).__name__})")
    
    if project_data:
        print(f"  - project_data keys: {list(project_data.keys()) if isinstance(project_data, dict) else 'Not a dict'}")
    if analysis_results:
        print(f"  - analysis_results keys: {list(analysis_results.keys()) if isinstance(analysis_results, dict) else 'Not a dict'}")
    
    return project_data, analysis_results

# INTEGRATION BEISPIEL:
# Füge dies in die PDF-Generierungssektion deiner gui.py ein:

def before_pdf_generation():
    """Rufe dies vor jeder PDF-Generierung auf"""
    project_data, analysis_results = consolidate_session_state()
    
    if not project_data:
        st.error("❌ Keine Projektdaten verfügbar. Bitte füllen Sie die Projektdaten aus.")
        return False
    
    if not analysis_results:
        st.error("❌ Keine Analyseergebnisse verfügbar. Bitte führen Sie eine Wirtschaftlichkeitsberechnung durch.")
        return False
    
    return True
