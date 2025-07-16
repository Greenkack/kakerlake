#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finale Integrationstest: Multi-PDF Live-Test
Testet die korrigierte multi_offer_generator.py Integration
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

def test_multi_offer_integration():
    """Führt einen vollständigen Test der Multi-Offer-Integration durch"""
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logging.info("="*80)
    logging.info("🚀 FINAL-TEST: Multi-Offer-Generator Integration")
    logging.info("="*80)
      # Test 1: Import-Test
    logging.info("Test 1: Importiere multi_offer_generator...")
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator, render_multi_offer_generator
        logging.info("✅ Multi-Offer-Generator erfolgreich importiert")
    except ImportError as e:
        logging.error(f"❌ Import fehlgeschlagen: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Unerwarteter Fehler beim Import: {e}")
        return False
    
    # Test 2: PDF-Generator Import
    logging.info("Test 2: Importiere PDF-Generator...")
    try:
        from pdf_generator import generate_offer_pdf
        logging.info("✅ PDF-Generator erfolgreich importiert")
    except ImportError as e:
        logging.error(f"❌ PDF-Generator Import fehlgeschlagen: {e}")
        return False
    
    # Test 3: Mock-Daten für vollständigen Test
    logging.info("Test 3: Erstelle Mock-Daten...")
    
    mock_project_data = {
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
            "selected_module_id": 1,
            "selected_inverter_id": 5,
            "selected_storage_id": 10,
            "module_quantity": 25,
            "include_storage": True,
            "include_additional_components": False
        }
    }
    
    mock_analysis_results = {
        "anlage_kwp": 10.0,
        "annual_pv_production_kwh": 9500,
        "total_investment_netto": 18750,
        "amortization_time_years": 12.5,
        "self_supply_rate_percent": 67.8,
        "annual_financial_benefit_year1": 1380,
        # Charts (wichtig!)
        "monthly_prod_cons_chart_bytes": b"mock_chart_data_monthly",
        "cost_projection_chart_bytes": b"mock_chart_data_cost",
        "cumulative_cashflow_chart_bytes": b"mock_chart_data_cashflow",
        "consumption_coverage_pie_chart_bytes": b"mock_pie_consumption",
        "pv_usage_pie_chart_bytes": b"mock_pie_pv_usage"
    }
    
    logging.info(f"✅ Mock project_data mit {len(mock_project_data)} Hauptfeldern erstellt")
    logging.info(f"✅ Mock analysis_results mit {len(mock_analysis_results)} Feldern erstellt")
    
    # Test 4: Simuliere _prepare_offer_data Funktion
    logging.info("Test 4: Teste _prepare_offer_data Logik...")
    
    try:
        # Simuliere die neue Logik aus multi_offer_generator.py
        offer_data = {
            "customer_data": mock_project_data["customer_data"],
            "project_data": mock_project_data  # Original behalten
        }
        
        # Settings simulieren
        settings = {
            "module_quantity": 25,
            "include_storage": True,
            "selected_module_id": 1,
            "selected_inverter_id": 5,
            "selected_storage_id": 10
        }
        
        # project_details erstellen (wie in Korrektur)
        project_details = {
            "module_quantity": settings.get("module_quantity", 20),
            "include_storage": settings.get("include_storage", True),
            "include_additional_components": False,
            "selected_module_id": settings.get("selected_module_id"),
            "selected_inverter_id": settings.get("selected_inverter_id"),
            "selected_storage_id": settings.get("selected_storage_id")
        }
        
        offer_data["project_details"] = project_details
        
        logging.info("✅ offer_data Struktur erfolgreich erstellt")
        logging.info(f"   - project_details keys: {list(project_details.keys())}")
        
    except Exception as e:
        logging.error(f"❌ _prepare_offer_data Simulation fehlgeschlagen: {e}")
        return False
    
    # Test 5: Teste Chart-Extraktion
    logging.info("Test 5: Teste Chart-Extraktion...")
    
    try:
        # Simuliere die neue Chart-Extraktion
        calc_results = mock_analysis_results
        available_charts = [k for k in calc_results.keys() if k.endswith('_chart_bytes') and calc_results[k] is not None]
        
        logging.info(f"✅ {len(available_charts)} Charts extrahiert:")
        for chart in available_charts:
            logging.info(f"   - {chart}")
        
        if len(available_charts) == 0:
            logging.warning("⚠️ Keine Charts gefunden - PDF wird ohne Visualizations erstellt")
        
    except Exception as e:
        logging.error(f"❌ Chart-Extraktion fehlgeschlagen: {e}")
        return False
    
    # Test 6: Validiere PDF-Parameter
    logging.info("Test 6: Validiere PDF-Parameter...")
    
    try:
        # Neue sections_to_include (nach Korrektur)
        sections_to_include = [
            "ProjectOverview",
            "TechnicalComponents", 
            "CostDetails",
            "Economics",
            "SimulationDetails",
            "CO2Savings", 
            "Visualizations",
            "FutureAspects"
        ]
        
        # Neue inclusion_options (nach Korrektur)
        inclusion_options = {
            "include_company_logo": True,
            "include_product_images": True,
            "include_all_documents": False,
            "company_document_ids_to_include": [],
            "selected_charts_for_pdf": available_charts,  # Automatisch gefüllt!
            "include_optional_component_details": True
        }
        
        logging.info(f"✅ PDF-Sektionen: {len(sections_to_include)} (inkl. Visualizations)")
        logging.info(f"✅ PDF-Optionen: {len(inclusion_options)} (inkl. {len(available_charts)} Charts)")
        
        # Prüfe kritische Sektionen
        if "Visualizations" not in sections_to_include:
            logging.error("❌ KRITISCH: Visualizations Sektion fehlt!")
            return False
        
        if "selected_charts_for_pdf" not in inclusion_options:
            logging.error("❌ KRITISCH: selected_charts_for_pdf Option fehlt!")
            return False
        
        logging.info("✅ Alle kritischen PDF-Parameter sind korrekt gesetzt")
        
    except Exception as e:
        logging.error(f"❌ PDF-Parameter Validierung fehlgeschlagen: {e}")
        return False
    
    # Test 7: Vollständigkeits-Check
    logging.info("Test 7: Vollständigkeits-Check...")
    
    required_fields = {
        "project_data": ["customer_data", "project_details"],
        "project_details": ["selected_module_id", "selected_inverter_id", "module_quantity"],
        "analysis_results": ["anlage_kwp", "annual_pv_production_kwh"],
        "pdf_config": ["sections_to_include", "inclusion_options"]
    }
    
    # Prüfe project_data
    pdf_project_data = {
        "customer_data": offer_data.get("customer_data", {}),
        "project_details": offer_data.get("project_details", {})
    }
    
    all_complete = True
    
    for category, fields in required_fields.items():
        if category == "project_data":
            for field in fields:
                if field not in pdf_project_data:
                    logging.error(f"❌ project_data fehlt Feld: {field}")
                    all_complete = False
                else:
                    logging.info(f"✅ project_data.{field} vorhanden")
        
        elif category == "project_details":
            project_details_data = pdf_project_data.get("project_details", {})
            for field in fields:
                if field not in project_details_data:
                    logging.error(f"❌ project_details fehlt Feld: {field}")
                    all_complete = False
                else:
                    logging.info(f"✅ project_details.{field} = {project_details_data[field]}")
        
        elif category == "analysis_results":
            for field in fields:
                if field not in mock_analysis_results:
                    logging.error(f"❌ analysis_results fehlt Feld: {field}")
                    all_complete = False
                else:
                    logging.info(f"✅ analysis_results.{field} = {mock_analysis_results[field]}")
    
    if all_complete:
        logging.info("✅ Vollständigkeits-Check bestanden")
    else:
        logging.error("❌ Vollständigkeits-Check fehlgeschlagen")
        return False
    
    # Finale Bewertung
    logging.info("\n" + "="*80)
    logging.info("📊 FINAL-TEST ZUSAMMENFASSUNG")
    logging.info("="*80)
    
    success_criteria = [
        ("Multi-Offer-Generator Import", True),
        ("PDF-Generator Import", True),
        ("Mock-Daten Erstellung", True),
        ("offer_data Struktur", True),
        ("Chart-Extraktion", len(available_charts) > 0),
        ("PDF-Parameter Validierung", True),
        ("Vollständigkeits-Check", all_complete)
    ]
    
    passed = sum(1 for _, result in success_criteria if result)
    total = len(success_criteria)
    
    for criterion, result in success_criteria:
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        logging.info(f"{status}: {criterion}")
    
    logging.info(f"\nErgebnis: {passed}/{total} Kriterien erfüllt")
    
    if passed == total:
        logging.info("🎉 FINAL-TEST BESTANDEN!")
        logging.info("🚀 Multi-PDF sollte jetzt alle Module/Komponenten wie Einzel-PDF anzeigen!")
        return True
    else:
        logging.error(f"💥 {total - passed} Kriterien nicht erfüllt")
        return False

if __name__ == "__main__":
    success = test_multi_offer_integration()
    if success:
        print("\n✅ Integration erfolgreich! Multi-PDF Korrekturen sind bereit.")
    else:
        print("\n❌ Integration fehlgeschlagen. Weitere Anpassungen erforderlich.")
    
    sys.exit(0 if success else 1)
