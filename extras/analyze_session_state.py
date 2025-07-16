"""
Quick-Fix für Session State Keys in der SolarDING App
Dieses Skript analysiert die häufigsten Probleme und bietet Lösungen.
"""
import os
import re
from typing import List, Tuple

def find_session_state_assignments():
    """Findet alle Session State Zuweisungen in Python-Dateien"""
    
    print("🔍 Suche Session State Zuweisungen in Python-Dateien...")
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('test_') and not f.startswith('debug_')]
    
    assignments = []
    
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Suche nach Session State Zuweisungen
                    if 'st.session_state' in line and '=' in line and not line.strip().startswith('#'):
                        # Extrahiere den Key
                        match = re.search(r'st\.session_state\.(\w+)\s*=', line)
                        if match:
                            key = match.group(1)
                            assignments.append((file, i+1, key, line.strip()))
        except Exception as e:
            print(f"Fehler beim Lesen von {file}: {e}")
    
    return assignments

def find_session_state_reads():
    """Findet alle Session State Lesezugriffe"""
    
    print("🔍 Suche Session State Lesezugriffe...")
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and not f.startswith('test_') and not f.startswith('debug_')]
    
    reads = []
    
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Suche nach Session State Lesezugriffen
                    if 'st.session_state' in line and not '=' in line.split('st.session_state')[0] and not line.strip().startswith('#'):
                        # Extrahiere Keys
                        matches = re.findall(r'st\.session_state\.get\([\'"](\w+)[\'"]', line)
                        matches += re.findall(r'st\.session_state\.(\w+)', line)
                        
                        for key in matches:
                            if key not in ['get', 'keys', 'items', 'values', 'pop', 'clear']:
                                reads.append((file, i+1, key, line.strip()))
        except Exception as e:
            print(f"Fehler beim Lesen von {file}: {e}")
    
    return reads

def analyze_key_patterns():
    """Analysiert Session State Key Muster"""
    
    print("=" * 80)
    print(" SESSION STATE ANALYSE ".center(80))
    print("=" * 80)
    
    assignments = find_session_state_assignments()
    reads = find_session_state_reads()
    
    print(f"\n📝 Gefunden: {len(assignments)} Zuweisungen, {len(reads)} Lesezugriffe")
    
    # Kategorisiere Keys
    project_keys = set()
    analysis_keys = set()
    customer_keys = set()
    pv_keys = set()
    pdf_keys = set()
    other_keys = set()
    
    all_keys = set()
    
    for file, line, key, code in assignments + reads:
        all_keys.add(key)
        
        key_lower = key.lower()
        if any(word in key_lower for word in ['project', 'daten']):
            project_keys.add(key)
        elif any(word in key_lower for word in ['analysis', 'kpi', 'calculation', 'result', 'berechnung']):
            analysis_keys.add(key)
        elif any(word in key_lower for word in ['customer', 'kunde']):
            customer_keys.add(key)
        elif any(word in key_lower for word in ['pv', 'solar', 'module', 'wechselrichter', 'inverter']):
            pv_keys.add(key)
        elif 'pdf' in key_lower:
            pdf_keys.add(key)
        else:
            other_keys.add(key)
    
    print("\n📊 Key-Kategorien:")
    print(f"🏠 Projekt-Keys: {sorted(project_keys)}")
    print(f"📈 Analyse-Keys: {sorted(analysis_keys)}")
    print(f"👤 Kunden-Keys: {sorted(customer_keys)}")
    print(f"☀️ PV-Keys: {sorted(pv_keys)}")
    print(f"📄 PDF-Keys: {sorted(pdf_keys)}")
    print(f"🔧 Andere Keys: {sorted(other_keys)}")
    
    # Suche nach häufigsten Keys
    key_usage = {}
    for file, line, key, code in assignments + reads:
        key_usage[key] = key_usage.get(key, 0) + 1
    
    print(f"\n🔥 Häufigste Keys:")
    for key, count in sorted(key_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {key}: {count}x")
    
    # Detaillierte Analyse für potenzielle Projektdaten
    print(f"\n🔍 Detailanalyse für Projektdaten-Keys:")
    for key in sorted(project_keys.union(customer_keys).union(pv_keys)):
        print(f"\n🔑 Key: {key}")
        assignments_for_key = [item for item in assignments if item[2] == key]
        reads_for_key = [item for item in reads if item[2] == key]
        
        if assignments_for_key:
            print(f"  📝 Zuweisungen ({len(assignments_for_key)}):")
            for file, line, _, code in assignments_for_key:
                print(f"    {file}:{line} -> {code}")
        
        if reads_for_key:
            print(f"  👁️ Lesezugriffe ({len(reads_for_key)}):")
            for file, line, _, code in reads_for_key[:3]:  # Nur erste 3 zeigen
                print(f"    {file}:{line} -> {code}")
            if len(reads_for_key) > 3:
                print(f"    ... und {len(reads_for_key)-3} weitere")
    
    # Analyse für Analysis-Keys
    print(f"\n🔍 Detailanalyse für Analysis-Keys:")
    for key in sorted(analysis_keys):
        print(f"\n🔑 Key: {key}")
        assignments_for_key = [item for item in assignments if item[2] == key]
        
        if assignments_for_key:
            print(f"  📝 Zuweisungen ({len(assignments_for_key)}):")
            for file, line, _, code in assignments_for_key:
                print(f"    {file}:{line} -> {code}")
    
    return all_keys, project_keys, analysis_keys

def suggest_fixes():
    """Schlägt Fixes für häufige Probleme vor"""
    
    print("=" * 80)
    print(" LÖSUNGSVORSCHLÄGE ".center(80))
    print("=" * 80)
    
    print("""
🔧 HÄUFIGE PROBLEME UND LÖSUNGEN:

1. 📊 FEHLENDE project_data:
   Problem: st.session_state.project_data ist None
   Lösung: Prüfe diese alternativen Keys:
   - current_project_data
   - project_details
   - customer_data + pv_details + company_information (kombinieren)

2. 📈 FEHLENDE analysis_results:
   Problem: st.session_state.analysis_results ist None
   Lösung: Prüfe diese alternativen Keys:
   - current_analysis_results
   - kpi_results
   - calculation_results
   - berechnung_ergebnisse

3. 🔄 SESSION STATE SYNCHRONISATION:
   Problem: Daten werden in verschiedenen Keys gespeichert
   Lösung: Füge Synchronisationscode hinzu:
   
   ```python
   # In der gui.py oder wo Daten verarbeitet werden
   if 'some_project_key' in st.session_state and not st.session_state.get('project_data'):
       st.session_state.project_data = st.session_state.some_project_key
   
   if 'some_analysis_key' in st.session_state and not st.session_state.get('analysis_results'):
       st.session_state.analysis_results = st.session_state.some_analysis_key
   ```

4. 📄 PDF-GENERIERUNG DEBUGGING:
   Problem: PDF zeigt Fallback obwohl Daten da sind
   Lösung: Verwende das Session State Detective Tool
   
   ```bash
   streamlit run session_state_detective.py --server.port 8504
   ```

5. 🏗️ DATENSTRUKTUR VEREINHEITLICHUNG:
   Problem: Inkonsistente Datenstrukturen
   Lösung: Erstelle eine zentrale Datenkonsolidierungsfunktion
""")

def create_session_state_fix():
    """Erstellt ein Fix-Skript für Session State Probleme"""
    
    fix_code = '''
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
'''
    
    with open('session_state_fix.py', 'w', encoding='utf-8') as f:
        f.write(fix_code)
    
    print("💾 session_state_fix.py erstellt!")
    print("📋 Kopiere den Code aus dieser Datei in deine gui.py")

def main():
    print("🕵️ SESSION STATE DETECTIVE - Standalone Analyse")
    print("=" * 80)
    
    if not os.path.exists('gui.py'):
        print("❌ gui.py nicht gefunden. Bitte führe dieses Skript im SolarDING App Verzeichnis aus.")
        return
    
    all_keys, project_keys, analysis_keys = analyze_key_patterns()
    suggest_fixes()
    create_session_state_fix()
    
    print("=" * 80)
    print("🎯 NÄCHSTE SCHRITTE:")
    print("1. Öffne das Session State Detective Tool: http://localhost:8504")
    print("2. Analysiere deine echten Session State Daten")
    print("3. Implementiere die Fixes aus session_state_fix.py")
    print("4. Teste die PDF-Generierung erneut")

if __name__ == "__main__":
    main()
