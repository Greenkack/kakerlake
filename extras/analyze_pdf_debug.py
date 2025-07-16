"""
Standalone Debug-Skript für PDF-Generierung
Dieses Skript analysiert die aktuellen PDF-Dateien und zeigt mögliche Probleme auf.
"""
import os
import re
import traceback
from typing import Dict, Any, List, Optional

def print_separator(title: str):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def analyze_pdf_generator():
    """Analysiert die pdf_generator.py Datei"""
    print_separator("ANALYSE: pdf_generator.py")
    
    if not os.path.exists("pdf_generator.py"):
        print("❌ pdf_generator.py nicht gefunden!")
        return False
    
    try:
        with open("pdf_generator.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Suche nach der generate_offer_pdf Funktion
        generate_func_match = re.search(r'def generate_offer_pdf\(.*?\):', content, re.DOTALL)
        if generate_func_match:
            print("✅ generate_offer_pdf Funktion gefunden")
        else:
            print("❌ generate_offer_pdf Funktion nicht gefunden!")
            return False
        
        # Suche nach der Validierungslogik
        validation_check = re.search(r'validation_result = _validate_pdf_data_availability', content)
        if validation_check:
            print("✅ Validierungsaufruf gefunden")
        else:
            print("❌ Validierungsaufruf nicht gefunden!")
        
        # Suche nach der Fallback-Logik
        fallback_check = re.search(r'if not validation_result\[\'is_valid\'\]:', content)
        if fallback_check:
            print("✅ Fallback-Logik gefunden")
        else:
            print("❌ Fallback-Logik nicht gefunden!")
        
        # Suche nach der _validate_pdf_data_availability Funktion
        validate_func_match = re.search(r'def _validate_pdf_data_availability\(.*?\):', content, re.DOTALL)
        if validate_func_match:
            print("✅ _validate_pdf_data_availability Funktion gefunden")
            
            # Analysiere die Validierungsfunktion
            func_start = validate_func_match.end()
            func_end = content.find('def _create_no_data_fallback_pdf', func_start)
            if func_end == -1:
                func_end = len(content)
            
            func_content = content[func_start:func_end]
            
            # Prüfe kritische Validierungsbedingungen
            critical_checks = [
                r'validation_result\[\'is_valid\'\] = False',
                r'critical_errors',
                r'analysis_results.*isinstance.*dict',
                r'len\(analysis_results\)'
            ]
            
            for check in critical_checks:
                if re.search(check, func_content):
                    print(f"✅ Kritische Validierung gefunden: {check}")
                else:
                    print(f"⚠️ Kritische Validierung möglicherweise fehlt: {check}")
        else:
            print("❌ _validate_pdf_data_availability Funktion nicht gefunden!")
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Analysieren von pdf_generator.py: {e}")
        traceback.print_exc()
        return False

def analyze_doc_output():
    """Analysiert die doc_output.py Datei"""
    print_separator("ANALYSE: doc_output.py")
    
    if not os.path.exists("doc_output.py"):
        print("❌ doc_output.py nicht gefunden!")
        return False
    
    try:
        with open("doc_output.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Suche nach der _show_pdf_data_status Funktion
        status_func_match = re.search(r'def _show_pdf_data_status\(.*?\):', content, re.DOTALL)
        if status_func_match:
            print("✅ _show_pdf_data_status Funktion gefunden")
        else:
            print("❌ _show_pdf_data_status Funktion nicht gefunden!")
        
        # Suche nach der Blockierungslogik
        blocking_check = re.search(r'if not data_sufficient:', content)
        if blocking_check:
            print("✅ Blockierungslogik gefunden")
            
            # Finde die Zeile nach der Blockierungslogik
            blocking_start = blocking_check.end()
            next_lines = content[blocking_start:blocking_start+200]
            if 'return' in next_lines:
                print("⚠️ PDF-Erstellung wird bei unvollständigen Daten blockiert!")
            else:
                print("✅ Blockierung scheint korrekt implementiert")
        else:
            print("❌ Blockierungslogik nicht gefunden!")
        
        # Suche nach PDF-Generierungsaufruf
        pdf_gen_call = re.search(r'_generate_offer_pdf_safe\(', content)
        if pdf_gen_call:
            print("✅ PDF-Generierungsaufruf gefunden")
        else:
            print("❌ PDF-Generierungsaufruf nicht gefunden!")
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Analysieren von doc_output.py: {e}")
        traceback.print_exc()
        return False

def analyze_pdf_ui():
    """Analysiert die pdf_ui.py Datei"""
    print_separator("ANALYSE: pdf_ui.py")
    
    if not os.path.exists("pdf_ui.py"):
        print("❌ pdf_ui.py nicht gefunden!")
        return False
    
    try:
        with open("pdf_ui.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Suche nach Syntaxfehlern
        lines = content.split('\n')
        
        syntax_issues = []
        for i, line in enumerate(lines):
            # Suche nach problematischen Einzeiler-if-Anweisungen
            if re.match(r'.*else:\s*st\..*', line.strip()):
                syntax_issues.append(f"Zeile {i+1}: Möglicher Einzeiler-if: {line.strip()}")
            
            # Suche nach fehlenden Doppelpunkten
            if re.match(r'.*else\s*st\..*', line.strip()) and ':' not in line:
                syntax_issues.append(f"Zeile {i+1}: Fehlender Doppelpunkt: {line.strip()}")
        
        if syntax_issues:
            print("⚠️ Mögliche Syntaxprobleme gefunden:")
            for issue in syntax_issues:
                print(f"  {issue}")
        else:
            print("✅ Keine offensichtlichen Syntaxprobleme gefunden")
        
        # Suche nach PDF-Generierungslogik
        pdf_gen_check = re.search(r'generate_offer_pdf|_generate_offer_pdf_safe', content)
        if pdf_gen_check:
            print("✅ PDF-Generierungslogik gefunden")
        else:
            print("❌ PDF-Generierungslogik nicht gefunden!")
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Analysieren von pdf_ui.py: {e}")
        traceback.print_exc()
        return False

def check_imports():
    """Prüft die Importierbarkeit der PDF-Module"""
    print_separator("IMPORT-CHECKS")
    
    try:
        # Teste pdf_generator Import
        print("Teste pdf_generator Import...")
        import pdf_generator
        print("✅ pdf_generator erfolgreich importiert")
        
        # Teste spezifische Funktionen
        if hasattr(pdf_generator, 'generate_offer_pdf'):
            print("✅ generate_offer_pdf Funktion verfügbar")
        else:
            print("❌ generate_offer_pdf Funktion nicht verfügbar!")
        
        if hasattr(pdf_generator, '_validate_pdf_data_availability'):
            print("✅ _validate_pdf_data_availability Funktion verfügbar")
        else:
            print("❌ _validate_pdf_data_availability Funktion nicht verfügbar!")
        
        if hasattr(pdf_generator, '_create_no_data_fallback_pdf'):
            print("✅ _create_no_data_fallback_pdf Funktion verfügbar")
        else:
            print("❌ _create_no_data_fallback_pdf Funktion nicht verfügbar!")
        
        return True
    except ImportError as e:
        print(f"❌ Import-Fehler bei pdf_generator: {e}")
        return False
    except Exception as e:
        print(f"❌ Allgemeiner Fehler beim Import-Check: {e}")
        traceback.print_exc()
        return False

def run_validation_test():
    """Führt einen Validierungstest durch"""
    print_separator("VALIDIERUNGSTEST")
    
    try:
        from pdf_generator import _validate_pdf_data_availability
        
        # Test mit vollständigen Daten
        print("Test 1: Vollständige Daten")
        project_data = {
            'customer_data': {'first_name': 'Max', 'last_name': 'Mustermann'},
            'pv_details': {'selected_modules': [{'id': 1, 'name': 'Test'}]},
            'project_details': {'module_quantity': 20},
            'company_information': {'name': 'Test GmbH'}
        }
        analysis_results = {
            'anlage_kwp': 7.6,
            'annual_pv_production_kwh': 7500,
            'total_investment_cost_netto': 12000
        }
        texts = {'pdf_error_no_analysis': 'Keine Analyse'}
        
        result = _validate_pdf_data_availability(project_data, analysis_results, texts)
        print(f"Ergebnis: is_valid={result['is_valid']}, Warnungen={len(result['warnings'])}, Fehler={len(result['critical_errors'])}")
        
        # Test mit leeren Daten
        print("\nTest 2: Leere Daten")
        empty_result = _validate_pdf_data_availability({}, {}, texts)
        print(f"Ergebnis: is_valid={empty_result['is_valid']}, Warnungen={len(empty_result['warnings'])}, Fehler={len(empty_result['critical_errors'])}")
        
        # Test mit minimalen Analysedaten
        print("\nTest 3: Minimale Analysedaten")
        minimal_analysis = {'some_value': 123}
        minimal_result = _validate_pdf_data_availability(project_data, minimal_analysis, texts)
        print(f"Ergebnis: is_valid={minimal_result['is_valid']}, Warnungen={len(minimal_result['warnings'])}, Fehler={len(minimal_result['critical_errors'])}")
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Validierungstest: {e}")
        traceback.print_exc()
        return False

def main():
    print_separator("PDF DEBUG ANALYSE")
    print("Analysiere die aktuellen PDF-Dateien auf mögliche Probleme...")
    
    # Führe alle Analysen durch
    results = []
    results.append(analyze_pdf_generator())
    results.append(analyze_doc_output())
    results.append(analyze_pdf_ui())
    results.append(check_imports())
    results.append(run_validation_test())
    
    # Zusammenfassung
    print_separator("ZUSAMMENFASSUNG")
    successful_tests = sum(results)
    total_tests = len(results)
    
    print(f"Erfolgreich: {successful_tests}/{total_tests} Tests")
    
    if successful_tests == total_tests:
        print("✅ Alle Tests bestanden - das Problem liegt wahrscheinlich in den Daten oder der Streamlit-Logik")
    else:
        print("❌ Einige Tests fehlgeschlagen - es gibt Probleme in den PDF-Modulen")
    
    print("\nEmpfohlene nächste Schritte:")
    print("1. Führe das Streamlit Debug-Tool aus: streamlit run streamlit_pdf_debug.py")
    print("2. Überprüfe die Session State Daten in der App")
    print("3. Prüfe die Konsolen-Ausgaben während der PDF-Generierung")

if __name__ == "__main__":
    main()
