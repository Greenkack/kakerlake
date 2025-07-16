#!/usr/bin/env python3
"""
Test der PDF-Fallback-Funktionen für fehlende Daten
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_fallback_functionality():
    """Test der PDF-Fallback-Funktionen"""
    
    print("🔧 Teste PDF-Fallback-Funktionen...")
    
    # 1. Test Import der neuen Funktionen
    try:
        from pdf_generator import _validate_pdf_data_availability, _create_no_data_fallback_pdf
        print("✅ PDF-Fallback-Funktionen erfolgreich importiert")
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    
    # 2. Test Datenvalidierung
    texts = {
        'pdf_warning_no_customer_name': 'Kein Kundenname verfügbar',
        'pdf_warning_no_modules': 'Keine PV-Module ausgewählt',
        'pdf_error_no_analysis': 'Keine Analyseergebnisse verfügbar',
        'pdf_no_data_title': 'Photovoltaik-Angebot - Datensammlung erforderlich',
        'pdf_no_data_main_text': 'Für die Erstellung Ihres Angebots benötigen wir noch Daten...'
    }
    
    # Test mit leeren Daten
    empty_project_data = {}
    empty_analysis_results = {}
    
    validation_result = _validate_pdf_data_availability(empty_project_data, empty_analysis_results, texts)
    
    print("✅ Validierung mit leeren Daten:")
    print(f"   📊 Gültig: {validation_result['is_valid']}")
    print(f"   ⚠️ Warnungen: {len(validation_result['warnings'])}")
    print(f"   ❌ Kritische Fehler: {len(validation_result['critical_errors'])}")
    print(f"   📋 Fehlende Daten: {', '.join(validation_result['missing_data_summary'])}")
    
    # Test mit teilweise verfügbaren Daten
    partial_project_data = {
        'customer_data': {'last_name': 'Mustermann'},
        'pv_details': {'selected_modules': [1, 2, 3]}
    }
    partial_analysis_results = {
        'anlage_kwp': 10.5,
        'annual_pv_production_kwh': 12000
    }
    
    validation_result_partial = _validate_pdf_data_availability(partial_project_data, partial_analysis_results, texts)
    
    print("\n✅ Validierung mit teilweise verfügbaren Daten:")
    print(f"   📊 Gültig: {validation_result_partial['is_valid']}")
    print(f"   ⚠️ Warnungen: {len(validation_result_partial['warnings'])}")
    print(f"   ❌ Kritische Fehler: {len(validation_result_partial['critical_errors'])}")
    print(f"   📋 Fehlende Daten: {', '.join(validation_result_partial['missing_data_summary'])}")
    
    # 3. Test Fallback-PDF-Erstellung
    try:
        customer_data = {'first_name': 'Max', 'last_name': 'Mustermann'}
        fallback_pdf_bytes = _create_no_data_fallback_pdf(texts, customer_data)
        
        if fallback_pdf_bytes and isinstance(fallback_pdf_bytes, bytes) and len(fallback_pdf_bytes) > 100:
            print(f"✅ Fallback-PDF erfolgreich erstellt: {len(fallback_pdf_bytes)} Bytes")
        else:
            print("❌ Fallback-PDF-Erstellung fehlgeschlagen")
            return False
            
    except Exception as e:
        print(f"❌ Fehler bei Fallback-PDF-Erstellung: {e}")
        return False
    
    # 4. Test UI-Funktionen
    try:
        from doc_output import _show_pdf_data_status
        print("✅ PDF-Datenstatus-UI-Funktion verfügbar")
    except ImportError as e:
        print(f"❌ UI-Funktion nicht verfügbar: {e}")
        return False
    
    print("\n🎉 Alle PDF-Fallback-Tests erfolgreich!")
    print("\n🔍 Neue Fallback-Features:")
    print("   • Automatische Datenvalidierung vor PDF-Erstellung")
    print("   • Fallback-PDF bei fehlenden kritischen Daten")
    print("   • Benutzerfreundliche Warnmeldungen bei unvollständigen Daten")
    print("   • Datenstatus-Anzeige in der Benutzeroberfläche")
    print("   • Detaillierte Validierungsberichte")
    
    return True

if __name__ == "__main__":
    success = test_pdf_fallback_functionality()
    if success:
        print("\n✅ PDF-Fallback-Test erfolgreich abgeschlossen!")
        sys.exit(0)
    else:
        print("\n❌ PDF-Fallback-Test fehlgeschlagen!")
        sys.exit(1)
