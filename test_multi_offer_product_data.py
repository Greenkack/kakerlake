#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test-Skript für Multi-Offer-Generator Produktdaten-Integration
Prüft, ob die Produktdaten korrekt für die PDF-Generierung strukturiert werden.
"""

import sys
import os
import logging

# Mock Streamlit Session State
class MockSessionState:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __getitem__(self, key):
        return self.data[key]

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
    
    @staticmethod
    def error(msg):
        print(f"Error: {msg}")

# Mock imports
sys.modules['streamlit'] = MockStreamlit()

# Test imports
print("Multi-Offer-Generator Produktdaten Test")
print("=" * 50)

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
    
    def mock_list_products():
        return [
            mock_get_product_by_id("module_1"),
            mock_get_product_by_id("inverter_1"), 
            mock_get_product_by_id("storage_1")
        ]
    
    # Test-Daten
    test_project_data = {
        "customer_name": "Max Mustermann",
        "customer_email": "max@test.de",
        "customer_address": "Teststraße 123, 12345 Teststadt",
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
      # Generator instanziieren
    generator = MultiCompanyOfferGenerator()
    print("✅ Generator instanziiert")
    
    # Mock-Funktionen setzen
    import multi_offer_generator
    multi_offer_generator.get_product_by_id = mock_get_product_by_id
    multi_offer_generator.list_products = mock_list_products
    
    # Angebotsdaten vorbereiten
    offer_data = generator._prepare_offer_data(
        customer_data={"name": "Max Mustermann", "email": "max@test.de"},
        project_data=test_project_data,
        settings=test_settings,
        company=test_company
    )
    
    print("✅ Angebotsdaten vorbereitet")
    
    # Prüfe Struktur der offer_data
    print("\n=== STRUKTUR DER ANGEBOTSDATEN ===")
    print(f"Keys: {list(offer_data.keys())}")
    
    # Prüfe project_details (KRITISCH für PDF)
    if "project_details" in offer_data:
        print("✅ project_details gefunden")
        project_details = offer_data["project_details"]
        print(f"project_details keys: {list(project_details.keys())}")
        
        # Prüfe Produktauswahl
        required_fields = ["selected_module_id", "selected_inverter_id", "selected_storage_id"]
        for field in required_fields:
            if field in project_details:
                print(f"✅ {field}: {project_details[field]}")
            else:
                print(f"❌ {field}: FEHLT")
        
        # Prüfe weitere wichtige Felder
        if "module_quantity" in project_details:
            print(f"✅ module_quantity: {project_details['module_quantity']}")
        
        if "include_storage" in project_details:
            print(f"✅ include_storage: {project_details['include_storage']}")
            
        if "selected_storage_storage_power_kw" in project_details:
            print(f"✅ selected_storage_storage_power_kw: {project_details['selected_storage_storage_power_kw']}")
    else:
        print("❌ project_details FEHLEN - PDF wird keine Module anzeigen!")
    
    # Prüfe Produktdaten
    print("\n=== PRODUKTDATEN ===")
    if "selected_module" in offer_data:
        module = offer_data["selected_module"]
        print(f"✅ Modul: {module.get('name', 'Unbekannt')} ({module.get('power_wp', 0)}W)")
    
    if "selected_inverter" in offer_data:
        inverter = offer_data["selected_inverter"]
        print(f"✅ Wechselrichter: {inverter.get('name', 'Unbekannt')} ({inverter.get('power_kw', 0)}kW)")
    
    if "selected_storage" in offer_data:
        storage = offer_data["selected_storage"]
        print(f"✅ Speicher: {storage.get('name', 'Unbekannt')} ({storage.get('capacity_kwh', 0)}kWh)")
    
    print("\n🎯 FAZIT:")
    if "project_details" in offer_data and all(field in offer_data["project_details"] for field in required_fields):
        print("✅ Produktdaten-Struktur ist korrekt für PDF-Generierung!")
        print("✅ Alle Module sollten jetzt in der PDF angezeigt werden!")
    else:
        print("❌ Produktdaten-Struktur ist unvollständig!")
        
    print("\n=== VOLLSTÄNDIGE project_details STRUKTUR ===")
    if "project_details" in offer_data:
        import json
        print(json.dumps(offer_data["project_details"], indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
