#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: Multi-Offer PDF-Datenstruktur
Prüft, ob die Datenstruktur für die PDF-Generierung korrekt erstellt wird.
"""

import sys
import json

# Mock Streamlit Session State
class MockSessionState:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)

# Mock streamlit
class MockStreamlit:
    class session_state:
        _instance = MockSessionState()
        
        @classmethod
        def get(cls, key, default=None):
            return cls._instance.get(key, default)
    
    @staticmethod
    def warning(msg):
        print(f"Warning: {msg}")

sys.modules['streamlit'] = MockStreamlit()

print("Test: Multi-Offer PDF-Datenstruktur")
print("=" * 40)

try:
    from multi_offer_generator import MultiCompanyOfferGenerator
    print("✅ Import erfolgreich")
    
    # Mock-Funktionen
    def mock_get_product_by_id(product_id):
        products = {
            "module_1": {
                "id": "module_1",
                "name": "Test Modul 400W",
                "power_wp": 400,
                "efficiency": 20.5,
                "manufacturer": "Test Solar"
            },
            "inverter_1": {
                "id": "inverter_1", 
                "name": "Test Wechselrichter 5kW",
                "power_kw": 5.0,
                "efficiency": 96.5,
                "manufacturer": "Test Inverter Co"
            },
            "storage_1": {
                "id": "storage_1",
                "name": "Test Batteriespeicher 10kWh",
                "storage_power_kw": 10.0,
                "capacity_kwh": 10.0,
                "manufacturer": "Test Battery Inc"
            }
        }
        return products.get(product_id, {})
    
    # Mock generate_offer_pdf
    def mock_generate_offer_pdf(project_data, **kwargs):
        print("\n=== PDF-GENERIERUNG AUFGERUFEN ===")
        print(f"project_data Keys: {list(project_data.keys())}")
        
        if "project_details" in project_data:
            print("✅ project_details gefunden")
            project_details = project_data["project_details"]
            print(f"project_details: {json.dumps(project_details, indent=2, ensure_ascii=False)}")
            
            # Prüfe kritische Felder
            required_fields = ["selected_module_id", "selected_inverter_id", "selected_storage_id"]
            for field in required_fields:
                if field in project_details:
                    print(f"✅ {field}: {project_details[field]}")
                else:
                    print(f"❌ {field}: FEHLT")
        else:
            print("❌ project_details FEHLEN - PDF wird keine Module anzeigen!")
        
        return b"Mock PDF Content"
    
    # Mock-Funktionen setzen
    import multi_offer_generator
    multi_offer_generator.get_product_by_id = mock_get_product_by_id
    multi_offer_generator.generate_offer_pdf = mock_generate_offer_pdf
    
    # Test-Daten
    test_project_data = {
        "customer_name": "Max Mustermann",
        "customer_email": "max@test.de",
        "consumption_data": {
            "annual_consumption_kwh": 4500,
            "electricity_price_kwh": 0.32
        }
    }
    
    test_settings = {
        "module_quantity": 25,
        "include_storage": True,
        "selected_module_id": "module_1",
        "selected_inverter_id": "inverter_1", 
        "selected_storage_id": "storage_1"
    }
    
    test_company = {
        "id": 1,
        "name": "Test Solar GmbH",
        "email": "info@testsolar.de"
    }
    
    # Generator testen
    generator = MultiCompanyOfferGenerator()
    
    # Angebotsdaten vorbereiten
    offer_data = generator._prepare_offer_data(
        customer_data={"name": "Max Mustermann", "email": "max@test.de"},
        project_data=test_project_data,
        settings=test_settings,
        company=test_company
    )
    
    print("\n=== ANGEBOTSDATEN STRUKTUR ===")
    print(f"offer_data Keys: {list(offer_data.keys())}")
    print(f"project_details verfügbar: {'project_details' in offer_data}")
    
    # PDF generieren (sollte die korrekte Datenstruktur erstellen)
    print("\n=== PDF-GENERIERUNG TESTEN ===")
    pdf_result = generator._generate_company_pdf(offer_data, test_company)
    
    if pdf_result:
        print("✅ PDF-Generierung erfolgreich")
    else:
        print("❌ PDF-Generierung fehlgeschlagen")

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
