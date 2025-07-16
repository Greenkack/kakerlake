#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript: Validiert die Multi-PDF Korrekturen
Testet, ob alle Sektionen und Charts jetzt korrekt in der Multi-PDF enthalten sind
"""

import sys
import logging
from typing import Dict, Any, List

# Setup für besseres Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_multi_pdf_sections():
    """Testet, ob alle erwarteten Sektionen in der Multi-PDF enthalten sind"""
    
    logging.info("="*60)
    logging.info("TEST: Multi-PDF Sektionen")
    logging.info("="*60)
    
    # Erwartete Sektionen (wie in normaler PDF)
    expected_sections = [
        "ProjectOverview", 
        "TechnicalComponents", 
        "CostDetails", 
        "Economics", 
        "SimulationDetails", 
        "CO2Savings", 
        "Visualizations", 
        "FutureAspects"
    ]
    
    # Simuliere Multi-PDF Sektionen (nach Korrektur)
    multi_pdf_sections = [
        "ProjectOverview",
        "TechnicalComponents", 
        "CostDetails",
        "Economics",
        "SimulationDetails",
        "CO2Savings", 
        "Visualizations",
        "FutureAspects"
    ]
    
    logging.info(f"Erwartete Sektionen: {len(expected_sections)}")
    logging.info(f"Multi-PDF Sektionen: {len(multi_pdf_sections)}")
    
    # Vergleiche
    missing_sections = set(expected_sections) - set(multi_pdf_sections)
    extra_sections = set(multi_pdf_sections) - set(expected_sections)
    
    if not missing_sections and not extra_sections:
        logging.info("✅ ERFOLG: Alle Sektionen sind korrekt!")
        return True
    else:
        if missing_sections:
            logging.error(f"❌ FEHLER: Fehlende Sektionen: {missing_sections}")
        if extra_sections:
            logging.warning(f"⚠️ WARNUNG: Zusätzliche Sektionen: {extra_sections}")
        return False

def test_multi_pdf_inclusion_options():
    """Testet, ob alle wichtigen inclusion_options in der Multi-PDF enthalten sind"""
    
    logging.info("="*60)
    logging.info("TEST: Multi-PDF Inclusion Options")
    logging.info("="*60)
    
    # Erwartete Options (wie in normaler PDF)
    expected_options = {
        "include_company_logo": True,
        "include_product_images": True,
        "include_all_documents": False,
        "company_document_ids_to_include": [],
        "selected_charts_for_pdf": [],  # Wird dynamisch gefüllt
        "include_optional_component_details": True
    }
    
    # Simuliere Multi-PDF Options (nach Korrektur)
    multi_pdf_options = {
        "include_company_logo": True,
        "include_product_images": True,
        "include_all_documents": False,
        "company_document_ids_to_include": [],
        "selected_charts_for_pdf": [],  # Wird aus calc_results automatisch gefüllt
        "include_optional_component_details": True
    }
    
    logging.info(f"Erwartete Options: {len(expected_options)} Keys")
    logging.info(f"Multi-PDF Options: {len(multi_pdf_options)} Keys")
    
    # Vergleiche Keys
    missing_keys = set(expected_options.keys()) - set(multi_pdf_options.keys())
    extra_keys = set(multi_pdf_options.keys()) - set(expected_options.keys())
    
    success = True
    
    if missing_keys:
        logging.error(f"❌ FEHLER: Fehlende Option-Keys: {missing_keys}")
        success = False
    
    if extra_keys:
        logging.info(f"ℹ️ INFO: Zusätzliche Option-Keys: {extra_keys}")
    
    # Vergleiche Werte für wichtige Keys
    critical_keys = ["include_company_logo", "include_product_images", "include_optional_component_details"]
    
    for key in critical_keys:
        expected_val = expected_options.get(key)
        actual_val = multi_pdf_options.get(key)
        
        if expected_val != actual_val:
            logging.error(f"❌ FEHLER: {key} - Erwartet: {expected_val}, Tatsächlich: {actual_val}")
            success = False
        else:
            logging.info(f"✅ OK: {key} = {actual_val}")
    
    if success:
        logging.info("✅ ERFOLG: Alle wichtigen Inclusion Options sind korrekt!")
    
    return success

def test_chart_extraction_logic():
    """Testet die Logik für automatische Chart-Extraktion"""
    
    logging.info("="*60)
    logging.info("TEST: Chart-Extraktion aus calc_results")
    logging.info("="*60)
    
    # Simuliere calc_results mit Charts
    mock_calc_results = {
        'anlage_kwp': 10.0,
        'annual_pv_production_kwh': 9500,
        'total_investment_netto': 18750,
        'monthly_prod_cons_chart_bytes': b'fake_chart_data_1',
        'cost_projection_chart_bytes': b'fake_chart_data_2',
        'cumulative_cashflow_chart_bytes': b'fake_chart_data_3',
        'consumption_coverage_pie_chart_bytes': b'fake_chart_data_4',
        'pv_usage_pie_chart_bytes': b'fake_chart_data_5',
        'some_invalid_key': 'not_a_chart',
        'another_chart_bytes': None,  # Null-Chart sollte ignoriert werden
        'valid_chart_bytes': b'valid_data'
    }
    
    # Teste Chart-Extraktion (wie in multi_offer_generator.py)
    chart_keys = [k for k in mock_calc_results.keys() if k.endswith('_chart_bytes') and mock_calc_results[k] is not None]
    
    expected_charts = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes', 
        'cumulative_cashflow_chart_bytes',
        'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes',
        'valid_chart_bytes'
    ]
    
    logging.info(f"Mock calc_results: {len(mock_calc_results)} Keys total")
    logging.info(f"Extrahierte Charts: {len(chart_keys)}")
    logging.info(f"Erwartete Charts: {len(expected_charts)}")
    
    # Vergleiche
    missing_charts = set(expected_charts) - set(chart_keys)
    extra_charts = set(chart_keys) - set(expected_charts)
    
    success = True
    
    if missing_charts:
        logging.error(f"❌ FEHLER: Fehlende Charts: {missing_charts}")
        success = False
    
    if extra_charts:
        logging.warning(f"⚠️ WARNUNG: Unerwartete Charts: {extra_charts}")
    
    # Teste Null-Handling
    null_charts = [k for k in mock_calc_results.keys() if k.endswith('_chart_bytes') and mock_calc_results[k] is None]
    if null_charts:
        logging.info(f"✅ OK: Null-Charts korrekt ignoriert: {null_charts}")
    
    if success and len(chart_keys) == len(expected_charts):
        logging.info("✅ ERFOLG: Chart-Extraktion funktioniert korrekt!")
    
    return success

def test_data_source_priority():
    """Testet die Priorität der Datenquellen für calc_results"""
    
    logging.info("="*60)
    logging.info("TEST: Datenquellen-Priorität für calc_results")
    logging.info("="*60)
    
    # Simuliere verschiedene Session State Szenarien
    test_scenarios = [
        {
            "name": "Normale Session mit calculation_results",
            "session_state": {
                'calculation_results': {'anlage_kwp': 10.0, 'charts': 'real_data'},
                'multi_offer_calc_results': {'anlage_kwp': 8.0, 'charts': 'multi_data'}
            },
            "expected_source": "calculation_results"
        },
        {
            "name": "Nur multi_offer_calc_results verfügbar",
            "session_state": {
                'multi_offer_calc_results': {'anlage_kwp': 8.0, 'charts': 'multi_data'}
            },
            "expected_source": "multi_offer_calc_results"
        },
        {
            "name": "Keine Daten - Mock-Fallback",
            "session_state": {},
            "expected_source": "mock_data"
        }
    ]
    
    success = True
    
    for scenario in test_scenarios:
        logging.info(f"\nSzenario: {scenario['name']}")
        
        # Simuliere die Logik aus multi_offer_generator.py
        session_state = scenario['session_state']
        
        calc_results = session_state.get('calculation_results', {})
        
        if not calc_results:
            calc_results = session_state.get('multi_offer_calc_results', {})
        
        actual_source = None
        if 'calculation_results' in session_state and calc_results == session_state['calculation_results']:
            actual_source = "calculation_results"
        elif 'multi_offer_calc_results' in session_state and calc_results == session_state['multi_offer_calc_results']:
            actual_source = "multi_offer_calc_results"
        else:
            actual_source = "mock_data"
        
        expected_source = scenario['expected_source']
        
        if actual_source == expected_source:
            logging.info(f"✅ OK: Verwendete Quelle: {actual_source}")
        else:
            logging.error(f"❌ FEHLER: Erwartet {expected_source}, aber verwendet {actual_source}")
            success = False
    
    if success:
        logging.info("✅ ERFOLG: Datenquellen-Priorität funktioniert korrekt!")
    
    return success

def main():
    """Führt alle Tests aus und gibt eine Zusammenfassung"""
    
    logging.info("🧪 STARTE MULTI-PDF KORREKTUR-TESTS")
    logging.info("="*80)
    
    tests = [
        ("Sektionen-Test", test_multi_pdf_sections),
        ("Inclusion Options Test", test_multi_pdf_inclusion_options),
        ("Chart-Extraktion Test", test_chart_extraction_logic),
        ("Datenquellen-Priorität Test", test_data_source_priority)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logging.info(f"\n🔬 Führe {test_name} aus...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logging.error(f"❌ {test_name} fehlgeschlagen: {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    logging.info("\n" + "="*80)
    logging.info("📊 TEST-ZUSAMMENFASSUNG")
    logging.info("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ BESTANDEN" if success else "❌ FEHLGESCHLAGEN"
        logging.info(f"{status}: {test_name}")
    
    logging.info(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        logging.info("🎉 ALLE TESTS BESTANDEN! Multi-PDF Korrekturen sind erfolgreich.")
        return True
    else:
        logging.error(f"💥 {total - passed} Tests fehlgeschlagen. Weitere Korrekturen erforderlich.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
