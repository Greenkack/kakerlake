#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Skript: Systematischer Vergleich zwischen Einzel-PDF und Multi-PDF
Analysiert die Datenstruktur und PDF-Generierung, um herauszufinden,
warum in der Multi-PDF nicht alle Module/Komponenten angezeigt werden.
"""

import logging
import json
import sys
import os
from typing import Dict, Any, Optional, List

# Setup für besseres Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_pdf_comparison.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def analyze_project_data_structure(project_data: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Analysiert die Struktur von project_data"""
    
    logging.info(f"\n{'='*50}")
    logging.info(f"ANALYSE PROJECT_DATA - {source}")
    logging.info(f"{'='*50}")
    
    analysis = {
        "source": source,
        "has_project_data": bool(project_data),
        "top_level_keys": list(project_data.keys()) if project_data else [],
        "customer_data": {},
        "project_details": {},
        "other_data": {}
    }
    
    if not project_data:
        logging.warning(f"{source}: Keine project_data vorhanden!")
        return analysis
    
    # Customer Data analysieren
    customer_data = project_data.get("customer_data", {})
    analysis["customer_data"] = {
        "exists": bool(customer_data),
        "keys": list(customer_data.keys()) if customer_data else [],
        "last_name": customer_data.get("last_name", "NICHT GESETZT"),
        "first_name": customer_data.get("first_name", "NICHT GESETZT"),
    }
    
    # Project Details analysieren (KRITISCH!)
    project_details = project_data.get("project_details", {})
    analysis["project_details"] = {
        "exists": bool(project_details),
        "keys": list(project_details.keys()) if project_details else [],
        "selected_module_id": project_details.get("selected_module_id", "NICHT GESETZT"),
        "selected_inverter_id": project_details.get("selected_inverter_id", "NICHT GESETZT"), 
        "selected_storage_id": project_details.get("selected_storage_id", "NICHT GESETZT"),
        "module_quantity": project_details.get("module_quantity", "NICHT GESETZT"),
        "include_storage": project_details.get("include_storage", "NICHT GESETZT"),
        "include_additional_components": project_details.get("include_additional_components", "NICHT GESETZT"),
    }
    
    # Andere wichtige Daten
    for key in ["consumption_data", "roof_data", "location_data", "technical_specs"]:
        if key in project_data:
            analysis["other_data"][key] = {
                "exists": True,
                "keys": list(project_data[key].keys()) if isinstance(project_data[key], dict) else "NOT_DICT"
            }
    
    # Detaillierte Ausgabe
    logging.info(f"{source} - Top Level Keys: {analysis['top_level_keys']}")
    logging.info(f"{source} - Customer Data Keys: {analysis['customer_data']['keys']}")
    logging.info(f"{source} - Project Details Keys: {analysis['project_details']['keys']}")
    logging.info(f"{source} - Selected Module ID: {analysis['project_details']['selected_module_id']}")
    logging.info(f"{source} - Selected Inverter ID: {analysis['project_details']['selected_inverter_id']}")
    logging.info(f"{source} - Selected Storage ID: {analysis['project_details']['selected_storage_id']}")
    logging.info(f"{source} - Module Quantity: {analysis['project_details']['module_quantity']}")
    
    return analysis

def analyze_analysis_results_structure(analysis_results: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Analysiert die Struktur von analysis_results"""
    
    logging.info(f"\n{'='*50}")
    logging.info(f"ANALYSE ANALYSIS_RESULTS - {source}")
    logging.info(f"{'='*50}")
    
    analysis = {
        "source": source,
        "has_analysis_results": bool(analysis_results),
        "keys": list(analysis_results.keys()) if analysis_results else [],
        "critical_kpis": {},
        "chart_data": {}
    }
    
    if not analysis_results:
        logging.warning(f"{source}: Keine analysis_results vorhanden!")
        return analysis
    
    # Kritische KPIs prüfen
    critical_kpis = [
        "anlage_kwp", "annual_pv_production_kwh", "total_investment_netto",
        "amortization_time_years", "self_supply_rate_percent", "annual_financial_benefit_year1"
    ]
    
    for kpi in critical_kpis:
        analysis["critical_kpis"][kpi] = {
            "exists": kpi in analysis_results,
            "value": analysis_results.get(kpi, "NICHT GESETZT"),
            "type": type(analysis_results.get(kpi, None)).__name__
        }
    
    # Chart-Daten prüfen
    chart_keys = [k for k in analysis_results.keys() if k.endswith('_chart_bytes')]
    analysis["chart_data"] = {
        "total_charts": len(chart_keys),
        "chart_keys": chart_keys,
        "non_null_charts": [k for k in chart_keys if analysis_results.get(k) is not None]
    }
    
    # Detaillierte Ausgabe
    logging.info(f"{source} - Gesamt Keys: {len(analysis['keys'])}")
    logging.info(f"{source} - Critical KPIs verfügbar: {[k for k, v in analysis['critical_kpis'].items() if v['exists']]}")
    logging.info(f"{source} - Charts verfügbar: {analysis['chart_data']['total_charts']}")
    logging.info(f"{source} - Charts mit Daten: {len(analysis['chart_data']['non_null_charts'])}")
    
    return analysis

def compare_pdf_function_calls(project_data_1: Dict, analysis_results_1: Dict, source_1: str,
                              project_data_2: Dict, analysis_results_2: Dict, source_2: str) -> Dict[str, Any]:
    """Vergleicht die Parameter für generate_offer_pdf zwischen zwei Quellen"""
    
    logging.info(f"\n{'='*60}")
    logging.info(f"VERGLEICH PDF-FUNKTIONSAUFRUFE")
    logging.info(f"Quelle 1: {source_1} vs Quelle 2: {source_2}")
    logging.info(f"{'='*60}")
    
    comparison = {
        "source_1": source_1,
        "source_2": source_2,
        "differences": [],
        "critical_issues": []
    }
    
    # Projekt-Details vergleichen
    pd1 = project_data_1.get("project_details", {}) if project_data_1 else {}
    pd2 = project_data_2.get("project_details", {}) if project_data_2 else {}
    
    critical_fields = ["selected_module_id", "selected_inverter_id", "selected_storage_id", 
                      "module_quantity", "include_storage"]
    
    for field in critical_fields:
        val1 = pd1.get(field, "MISSING")
        val2 = pd2.get(field, "MISSING")
        
        if val1 != val2:
            diff = f"Field '{field}': {source_1}={val1} vs {source_2}={val2}"
            comparison["differences"].append(diff)
            logging.warning(f"UNTERSCHIED: {diff}")
            
            if field in ["selected_module_id", "selected_inverter_id"]:
                comparison["critical_issues"].append(f"Kritisch: {field} unterschiedlich!")
    
    # Analysis Results vergleichen
    ar1 = analysis_results_1 if analysis_results_1 else {}
    ar2 = analysis_results_2 if analysis_results_2 else {}
    
    kpi_fields = ["anlage_kwp", "annual_pv_production_kwh", "module_quantity"]
    
    for field in kpi_fields:
        val1 = ar1.get(field, "MISSING")
        val2 = ar2.get(field, "MISSING")
        
        if val1 != val2:
            diff = f"KPI '{field}': {source_1}={val1} vs {source_2}={val2}"
            comparison["differences"].append(diff)
            logging.warning(f"KPI UNTERSCHIED: {diff}")
    
    # Zusammenfassung
    if comparison["critical_issues"]:
        logging.error(f"KRITISCHE PROBLEME GEFUNDEN: {len(comparison['critical_issues'])}")
        for issue in comparison["critical_issues"]:
            logging.error(f"  - {issue}")
    else:
        logging.info("Keine kritischen Unterschiede in den Produktfeldern gefunden.")
    
    return comparison

def simulate_single_pdf_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Simuliert Datenstruktur wie sie bei einer normalen Einzel-PDF verwendet wird"""
    
    logging.info("Simuliere Einzel-PDF Datenstruktur...")
    
    # Typische project_data Struktur aus der normalen App
    project_data = {
        "customer_data": {
            "salutation": "Herr",
            "first_name": "Max",
            "last_name": "Mustermann", 
            "address": "Musterstraße",
            "house_number": "123",
            "zip_code": "12345",
            "city": "Musterstadt"
        },
        "project_details": {
            "selected_module_id": 1,  # Beispiel-ID
            "selected_inverter_id": 5,  # Beispiel-ID
            "selected_storage_id": 10,  # Beispiel-ID
            "module_quantity": 25,
            "include_storage": True,
            "include_additional_components": False,
            "visualize_roof_in_pdf_satellite": False
        },
        "consumption_data": {
            "annual_consumption_kwh": 4500
        }
    }
    
    # Typische analysis_results Struktur
    analysis_results = {
        "anlage_kwp": 10.0,
        "annual_pv_production_kwh": 9500,
        "total_investment_netto": 18750,
        "amortization_time_years": 12.5,
        "self_supply_rate_percent": 67.8,
        "annual_financial_benefit_year1": 1380,
        "monthly_prod_cons_chart_bytes": b"fake_chart_data_1",
        "cost_projection_chart_bytes": b"fake_chart_data_2",
        "cumulative_cashflow_chart_bytes": b"fake_chart_data_3"
    }
    
    return project_data, analysis_results

def simulate_multi_pdf_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Simuliert Datenstruktur wie sie vom Multi-Offer-Generator erstellt wird"""
    
    logging.info("Simuliere Multi-PDF Datenstruktur...")
    
    # Diese Struktur wird in multi_offer_generator.py erstellt
    project_data = {
        "customer_data": {
            "salutation": "Herr",
            "first_name": "Max",
            "last_name": "Mustermann",
            "address": "Musterstraße", 
            "house_number": "123",
            "zip_code": "12345",
            "city": "Musterstadt"
        },
        "project_details": {
            "module_quantity": 25,
            "include_storage": True,
            "include_additional_components": False,
            "selected_module_id": 1,  # Wird in _prepare_offer_data gesetzt
            "selected_inverter_id": 5,  # Wird in _prepare_offer_data gesetzt
            "selected_storage_id": 10,  # Wird in _prepare_offer_data gesetzt
            "selected_storage_storage_power_kw": 5.12
        }
    }
    
    # Mock-Berechnungsergebnisse (können unterschiedlich sein!)
    analysis_results = {
        "anlage_kwp": 10.0,
        "annual_pv_production_kwh": 9500,
        "total_investment_netto": 18750,
        "amortization_time_years": 12.5,
        "self_supply_rate_percent": 65.0,  # Könnte abweichen!
        "annual_financial_benefit_year1": 1200  # Könnte abweichen!
    }
    
    return project_data, analysis_results

def main():
    """Hauptfunktion: Führt den vollständigen Vergleich durch"""
    
    logging.info("="*80)
    logging.info("STARTE SYSTEMATISCHE PDF-VERGLEICHSANALYSE")
    logging.info("Ziel: Unterschiede zwischen Einzel-PDF und Multi-PDF finden")
    logging.info("="*80)
    
    try:
        # 1. Simuliere beide Datenstrukturen
        single_project_data, single_analysis_results = simulate_single_pdf_data()
        multi_project_data, multi_analysis_results = simulate_multi_pdf_data()
        
        # 2. Analysiere beide Strukturen einzeln
        single_analysis = analyze_project_data_structure(single_project_data, "EINZEL-PDF")
        multi_analysis = analyze_project_data_structure(multi_project_data, "MULTI-PDF")
        
        single_ar_analysis = analyze_analysis_results_structure(single_analysis_results, "EINZEL-PDF")
        multi_ar_analysis = analyze_analysis_results_structure(multi_analysis_results, "MULTI-PDF")
        
        # 3. Vergleiche die Strukturen
        comparison = compare_pdf_function_calls(
            single_project_data, single_analysis_results, "EINZEL-PDF",
            multi_project_data, multi_analysis_results, "MULTI-PDF"
        )
        
        # 4. Erstelle Zusammenfassung
        logging.info(f"\n{'='*60}")
        logging.info("ZUSAMMENFASSUNG DER ANALYSE")
        logging.info(f"{'='*60}")
        
        total_differences = len(comparison["differences"])
        critical_issues = len(comparison["critical_issues"])
        
        logging.info(f"Gefundene Unterschiede: {total_differences}")
        logging.info(f"Kritische Probleme: {critical_issues}")
        
        if critical_issues == 0:
            logging.info("✅ Keine kritischen Unterschiede in der Datenstruktur gefunden!")
            logging.info("Das Problem liegt wahrscheinlich NICHT in der Datenübergabe.")
            logging.info("Mögliche andere Ursachen:")
            logging.info("  - Unterschiede in PDF-Template/Rendering-Logik")
            logging.info("  - Verschiedene inclusion_options zwischen Einzel- und Multi-PDF")
            logging.info("  - Unterschiedliche sections_to_include Parameter")
            logging.info("  - Fehler in get_product_by_id_func oder ähnlichen Callback-Funktionen")
        else:
            logging.error("❌ Kritische Unterschiede gefunden!")
            logging.error("Diese könnten die Ursache für fehlende Module/Komponenten sein.")
        
        # 5. Speichere detaillierte Ergebnisse
        results = {
            "single_pdf_analysis": single_analysis,
            "multi_pdf_analysis": multi_analysis,
            "comparison": comparison,
            "summary": {
                "total_differences": total_differences,
                "critical_issues": critical_issues,
                "analysis_completed": True
            }
        }
        
        with open("pdf_comparison_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logging.info(f"\nDetaillierte Ergebnisse in 'pdf_comparison_results.json' gespeichert.")
        logging.info("Debug-Log in 'debug_pdf_comparison.log' verfügbar.")
        
        return results
        
    except Exception as e:
        logging.error(f"Fehler bei der Analyse: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    results = main()
    if results:
        print("\n✅ Analyse abgeschlossen. Siehe Log-Dateien für Details.")
    else:
        print("\n❌ Analyse fehlgeschlagen. Siehe Log für Details.")
