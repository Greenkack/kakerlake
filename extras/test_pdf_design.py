#!/usr/bin/env python3
"""
Test-Script für die verbesserte PDF-Generierung
"""

import sys
import os
import json
from datetime import datetime

# Aktuelles Verzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pdf_generator import generate_offer_pdf
    from locales import get_text_dict
    print("✓ Module erfolgreich importiert")
except ImportError as e:
    print(f"✗ Import-Fehler: {e}")
    sys.exit(1)

def create_test_data():
    """Erstellt Test-Daten für die PDF-Generierung"""
    
    # Test-Projektdaten
    project_data = {
        "customer_data": {
            "salutation": "Herr",
            "title": "",
            "first_name": "Max", 
            "last_name": "Mustermann",
            "company_name": "",
            "address": "Musterstraße",
            "house_number": "123",
            "zip_code": "12345",
            "city": "Musterstadt"
        },
        "project_details": {
            "module_quantity": 20,
            "selected_module_id": 1144,
            "selected_inverter_id": 1145,
            "include_storage": True,
            "selected_storage_id": 1146,
            "include_additional_components": False
        }
    }
    
    # Test-Analyseergebnisse  
    analysis_results = {
        "anlage_kwp": 8.5,
        "annual_pv_production_kwh": 8500,
        "self_supply_rate_percent": 75.2,
        "total_investment_cost": 18500,
        "annual_savings": 1850,
        "payback_period_years": 10.5
    }
    
    # Test-Firmeninformationen
    company_info = {
        "name": "Ömer's Solar-Ding GmbH",
        "street": "Sonnenstraße 42",
        "zip_code": "12345",
        "city": "Solarstadt",
        "phone": "+49 123 456789",
        "email": "info@solar-ding.de",
        "website": "www.solar-ding.de",
        "tax_id": "DE123456789"
    }
    
    # Test-Texte
    texts = get_text_dict("de")  # Deutsche Texte
    
    return project_data, analysis_results, company_info, texts

def test_pdf_generation():
    """Testet die PDF-Generierung mit den neuen Design-Verbesserungen"""
    
    print("🔄 Starte PDF-Design-Test...")
    
    try:
        # Test-Daten erstellen
        project_data, analysis_results, company_info, texts = create_test_data()
        
        # PDF-Generierung testen
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            texts=texts,
            company_info=company_info,
            selected_offer_title_text="Ihr individuelles Photovoltaik-Angebot",
            selected_cover_letter_text="Sehr geehrter {salutation_line},\n\nwir freuen uns, Ihnen unser maßgeschneidertes Angebot für eine Photovoltaikanlage unterbreiten zu können.",
            offer_number="2025-001",
            sections_to_include=["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"],
            inclusion_options={
                "include_company_logo": True,
                "include_all_documents": False,
                "include_optional_component_details": True,
                "selected_charts_for_pdf": []
            },
            get_product_by_id_func=lambda x: {
                "brand": "Test-Marke",
                "model_name": "Test-Modell",
                "category": "modul",
                "capacity_w": 425,
                "efficiency_percent": 20.5
            },
            db_list_company_documents_func=lambda x, y: [],
            active_company_id=1,
            company_document_ids_to_include=[],
            company_logo_base64=None
        )
        
        if pdf_bytes:
            # PDF-Datei speichern
            output_file = f"test_angebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"✓ PDF erfolgreich erstellt: {output_file}")
            print(f"  Dateigröße: {len(pdf_bytes)} Bytes")
            return True
        else:
            print("✗ PDF-Generierung fehlgeschlagen - keine Bytes zurückgegeben")
            return False
            
    except Exception as e:
        print(f"✗ Fehler bei PDF-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("PDF-DESIGN VERBESSERUNG - TEST")
    print("=" * 60)
    
    # Test durchführen
    success = test_pdf_generation()
    
    print("=" * 60)
    if success:
        print("✅ TEST ERFOLGREICH - PDF-Design wurde verbessert!")
        print("\nVerbesserungen:")
        print("• Moderne Farbpalette (Dunkelblau, Solargrün)")
        print("• Eleganteres Deckblatt-Layout") 
        print("• Verbesserte Typografie und Abstände")
        print("• Professionellere Tabellen mit Zebra-Streifen")
        print("• Modernere Kopf- und Fußzeilen")
    else:
        print("❌ TEST FEHLGESCHLAGEN - Bitte Fehler beheben")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
