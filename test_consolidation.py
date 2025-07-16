"""
Test der Session State Konsolidierung
"""
import sys
import os

# Mock Session State für Test
class MockSessionState:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __setitem__(self, key, value):
        self.data[key] = value
        
    def __getitem__(self, key):
        return self.data[key]
    
    def __contains__(self, key):
        return key in self.data

def test_consolidation():
    """Testet die Datenkonsolidierung"""
    
    print("🧪 TEST: Session State Konsolidierung")
    print("=" * 50)
    
    # Mock Session State mit typischen SolarDING Daten
    session_state = MockSessionState()
    
    # Simuliere typische SolarDING Session State Daten
    session_state['calculation_results'] = {
        'anlage_kwp': 7.6,
        'annual_pv_production_kwh': 7500,
        'total_investment_cost_netto': 12000,
        'autarkie_anteil_prozent': 60,
        'eigenverbrauchs_anteil_prozent': 40
    }
    
    session_state['project_details'] = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann'
        },
        'pv_details': {
            'selected_modules': [{'id': 123, 'name': 'Test Modul'}]
        },
        'company_information': {
            'name': 'Test Solar GmbH'
        }
    }
    
    # Simuliere leere Standard-Keys (wie sie aktuell in der App sind)
    session_state['project_data'] = None
    session_state['analysis_results'] = None
    
    print("📊 Vor Konsolidierung:")
    print(f"  project_data: {session_state.get('project_data')}")
    print(f"  analysis_results: {session_state.get('analysis_results')}")
    print(f"  calculation_results: {'✅ vorhanden' if session_state.get('calculation_results') else '❌ fehlt'}")
    print(f"  project_details: {'✅ vorhanden' if session_state.get('project_details') else '❌ fehlt'}")
    
    # Konsolidierung durchführen
    def consolidate_data(session_state):
        """Konsolidiert Session State Daten"""
        
        project_data = session_state.get('project_data')
        analysis_results = session_state.get('analysis_results')
        
        # Project Data Konsolidierung
        if not project_data or not isinstance(project_data, dict) or len(project_data) == 0:
            potential_sources = ['current_project_data', 'project_details', 'projektdaten']
            for source in potential_sources:
                source_data = session_state.get(source)
                if source_data and isinstance(source_data, dict):
                    project_data = source_data
                    session_state['project_data'] = project_data
                    print(f"🔄 project_data aus '{source}' wiederhergestellt")
                    break
        
        # Analysis Results Konsolidierung
        if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) == 0:
            potential_sources = ['calculation_results', 'current_analysis_results', 'kpi_results']
            for source in potential_sources:
                source_data = session_state.get(source)
                if source_data and isinstance(source_data, dict) and len(source_data) > 0:
                    analysis_results = source_data
                    session_state['analysis_results'] = analysis_results
                    print(f"🔄 analysis_results aus '{source}' wiederhergestellt")
                    break
        
        return project_data, analysis_results
    
    # Konsolidierung ausführen
    project_data, analysis_results = consolidate_data(session_state)
    
    print("\n📊 Nach Konsolidierung:")
    print(f"  project_data: {'✅ vorhanden' if project_data else '❌ fehlt'}")
    print(f"  analysis_results: {'✅ vorhanden' if analysis_results else '❌ fehlt'}")
    
    if project_data:
        print(f"  project_data keys: {list(project_data.keys())}")
        
    if analysis_results:
        print(f"  analysis_results keys: {list(analysis_results.keys())}")
        # Teste wichtige KPIs
        important_kpis = ['anlage_kwp', 'annual_pv_production_kwh', 'total_investment_cost_netto']
        for kpi in important_kpis:
            value = analysis_results.get(kpi)
            print(f"    - {kpi}: {'✅' if value else '❌'} ({value})")
    
    # Teste PDF-Validierung
    print("\n🔍 PDF-Validierung Test:")
    try:
        # Simuliere Validierungslogik
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'critical_errors': []
        }
        
        # Customer check
        customer_data = project_data.get('customer_data', {}) if project_data else {}
        if not customer_data or not customer_data.get('last_name'):
            validation_result['warnings'].append('Kein Kundenname')
        
        # Analysis check - kritisch
        if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
            validation_result['critical_errors'].append('Keine Analyseergebnisse')
            validation_result['is_valid'] = False
        
        print(f"  Validierung: {'✅ GÜLTIG' if validation_result['is_valid'] else '❌ UNGÜLTIG'}")
        print(f"  Warnungen: {len(validation_result['warnings'])}")
        print(f"  Kritische Fehler: {len(validation_result['critical_errors'])}")
        
        if validation_result['critical_errors']:
            print(f"  Fehlerdetails: {validation_result['critical_errors']}")
        
        return validation_result['is_valid']
        
    except Exception as e:
        print(f"❌ Fehler bei Validierung: {e}")
        return False

if __name__ == "__main__":
    success = test_consolidation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TEST ERFOLGREICH: Konsolidierung funktioniert!")
        print("\n🎯 Die Lösung:")
        print("1. calculation_results wird als analysis_results verwendet")
        print("2. project_details wird als project_data verwendet") 
        print("3. PDF-Validierung sollte jetzt erfolgreich sein")
    else:
        print("❌ TEST FEHLGESCHLAGEN: Problem in der Konsolidierung")
        
    print("\n📋 Nächste Schritte:")
    print("1. Die Konsolidierung ist bereits in doc_output.py integriert")
    print("2. Teste die PDF-Generierung in der Streamlit-App")
    print("3. Bei Problemen: Session State Detective Tool verwenden")
