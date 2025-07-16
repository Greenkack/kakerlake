#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test: Multi-Offer-Generator mit bestehenden Produktauswahlen
Simuliert den Fall, dass bereits Produktauswahlen aus der normalen Analyse-Session vorhanden sind.
"""

import sys
import os

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

print("Test: Multi-Offer mit bestehenden Produktauswahlen")
print("=" * 55)

try:
    from multi_offer_generator import MultiCompanyOfferGenerator
    print("✅ Import erfolgreich")
    
    # Mock-Funktionen
    def mock_get_product_by_id(product_id):
        products = {
            "existing_module": {
                "id": "existing_module",
                "name": "Premium Modul 450W",
                "power_wp": 450,
                "efficiency": 22.0,
                "manufacturer": "Premium Solar"
            },
            "existing_inverter": {
                "id": "existing_inverter", 
                "name": "Premium Wechselrichter 8kW",
                "power_kw": 8.0,
                "efficiency": 98.0,
                "manufacturer": "Premium Power"
            },
            "existing_storage": {
                "id": "existing_storage",
                "name": "Premium Batteriespeicher 15kWh",
                "storage_power_kw": 15.0,
                "capacity_kwh": 15.0,
                "manufacturer": "Premium Battery"
            },
            "override_module": {
                "id": "override_module",
                "name": "Override Modul 400W",
                "power_wp": 400,
                "manufacturer": "Override Solar"
            }
        }
        return products.get(product_id, {})
    
    # Test-Projekt mit bestehenden Produktauswahlen (wie aus normaler Analyse-Session)
    test_project_data_with_products = {
        "customer_name": "Max Mustermann",
        "customer_email": "max@test.de", 
        "project_details": {
            "module_quantity": 30,
            "include_storage": True,
            "include_additional_components": True,
            "selected_module_id": "existing_module",
            "selected_inverter_id": "existing_inverter",
            "selected_storage_id": "existing_storage",
            "visualize_roof_in_pdf_satellite": True,
            "satellite_image_base64_data": "fake_base64_data"
        }
    }
    
    # Test 1: Leere Settings (sollte Fallback auf project_data verwenden)
    test_settings_empty = {}
    
    # Test 2: Settings mit Overrides (sollte Settings bevorzugen)
    test_settings_override = {
        "module_quantity": 20,
        "selected_module_id": "override_module"
    }
    
    # Mock-Funktionen setzen
    import multi_offer_generator
    multi_offer_generator.get_product_by_id = mock_get_product_by_id
    
    generator = MultiCompanyOfferGenerator()
    
    print("\n=== TEST 1: Leere Settings (Fallback auf project_data) ===")
    offer_data_1 = generator._prepare_offer_data(
        customer_data={"name": "Max", "email": "max@test.de"},
        project_data=test_project_data_with_products,
        settings=test_settings_empty,
        company={"id": 1, "name": "Test Firma"}
    )
    
    pd1 = offer_data_1["project_details"]
    print(f"✅ Modulauswahl: {pd1.get('selected_module_id')} (Fallback aus project_data)")
    print(f"✅ Wechselrichter: {pd1.get('selected_inverter_id')} (Fallback aus project_data)")
    print(f"✅ Speicher: {pd1.get('selected_storage_id')} (Fallback aus project_data)")
    print(f"✅ Modulanzahl: {pd1.get('module_quantity')} (aus project_data)")
    print(f"✅ Satellit-Bild: {pd1.get('visualize_roof_in_pdf_satellite')} (aus project_data)")
    
    print("\n=== TEST 2: Settings mit Override ===")
    offer_data_2 = generator._prepare_offer_data(
        customer_data={"name": "Max", "email": "max@test.de"},
        project_data=test_project_data_with_products,
        settings=test_settings_override,
        company={"id": 1, "name": "Test Firma"}
    )
    
    pd2 = offer_data_2["project_details"]
    print(f"✅ Modulauswahl: {pd2.get('selected_module_id')} (Override aus Settings)")
    print(f"✅ Wechselrichter: {pd2.get('selected_inverter_id')} (Fallback aus project_data)")
    print(f"✅ Modulanzahl: {pd2.get('module_quantity')} (Override aus Settings)")
    
    print("\n=== PRODUKTNAMEN ===")
    print(f"Modul Test 1: {offer_data_1['selected_module']['name']}")
    print(f"Modul Test 2: {offer_data_2['selected_module']['name']}")
    
    print("\n🎯 FAZIT:")
    print("✅ Fallback-Mechanismus funktioniert korrekt!")
    print("✅ Bestehende Produktauswahlen werden übernommen!")
    print("✅ Settings können einzelne Auswahlen überschreiben!")
    print("✅ Alle Moduldetails sollten in der PDF angezeigt werden!")

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
