#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Umfassender Test: Multi-Offer-Generator Produktdaten-Integration
Simuliert verschiedene Szenarien der PDF-Generierung mit Produktdaten.
"""

import sys
import json
import logging

# Logging einrichten
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
    
    @staticmethod
    def error(msg):
        print(f"Error: {msg}")

sys.modules['streamlit'] = MockStreamlit()

print("🔧 Umfassender Test: Multi-Offer PDF-Produktdaten")
print("=" * 55)

try:
    from multi_offer_generator import MultiCompanyOfferGenerator
    print("✅ Import erfolgreich")
    
    # Realistische Mock-Funktionen
    def mock_get_product_by_id(product_id):
        products = {
            "jinko_400w": {
                "id": "jinko_400w",
                "name": "JinkoSolar Tiger Pro 400W",
                "power_wp": 400,
                "efficiency": 20.78,
                "manufacturer": "JinkoSolar",
                "dimensions": "1722 x 1134 x 30 mm",
                "weight": 20.5
            },
            "fronius_symo_5": {
                "id": "fronius_symo_5", 
                "name": "Fronius Symo 5.0-3-M",
                "power_kw": 5.0,
                "efficiency": 97.1,
                "manufacturer": "Fronius",
                "phases": 3
            },
            "tesla_powerwall": {
                "id": "tesla_powerwall",
                "name": "Tesla Powerwall 2",
                "storage_power_kw": 13.5,
                "capacity_kwh": 13.5,
                "manufacturer": "Tesla",
                "round_trip_efficiency": 90
            }
        }
        return products.get(product_id, {})
    
    def mock_list_products():
        return [
            mock_get_product_by_id("jinko_400w"),
            mock_get_product_by_id("fronius_symo_5"),
            mock_get_product_by_id("tesla_powerwall")
        ]
    
    # PDF-Mock mit detaillierter Analyse
    def mock_generate_offer_pdf(project_data, **kwargs):
        print("\n🎯 === PDF-GENERIERUNG ANALYSE ===")
        print(f"Erhaltene project_data Struktur:")
        print(f"  Hauptebene Keys: {list(project_data.keys())}")
        
        # Kundenddaten prüfen
        if "customer_data" in project_data:
            customer = project_data["customer_data"]
            print(f"✅ Kundendaten: {customer.get('name', 'N/A')}")
        
        # Projektdetails prüfen (KRITISCH für Module)
        if "project_details" in project_data:
            details = project_data["project_details"]
            print(f"✅ project_details gefunden mit {len(details)} Feldern")
            
            # Produktauswahl analysieren
            module_id = details.get("selected_module_id")
            inverter_id = details.get("selected_inverter_id") 
            storage_id = details.get("selected_storage_id")
            
            print(f"  📦 Modul ID: {module_id}")
            print(f"  🔌 Wechselrichter ID: {inverter_id}")
            print(f"  🔋 Speicher ID: {storage_id}")
            print(f"  📊 Modulanzahl: {details.get('module_quantity', 'N/A')}")
            print(f"  🔋 Speicher inkl.: {details.get('include_storage', 'N/A')}")
            
            # Prüfe ob IDs zu echten Produkten auflösen
            if module_id:
                module_product = mock_get_product_by_id(module_id)
                if module_product:
                    print(f"  ✅ Modul auflösbar: {module_product['name']}")
                else:
                    print(f"  ❌ Modul ID '{module_id}' nicht gefunden!")
            
            if inverter_id:
                inverter_product = mock_get_product_by_id(inverter_id)
                if inverter_product:
                    print(f"  ✅ Wechselrichter auflösbar: {inverter_product['name']}")
                else:
                    print(f"  ❌ Wechselrichter ID '{inverter_id}' nicht gefunden!")
            
            if storage_id:
                storage_product = mock_get_product_by_id(storage_id)
                if storage_product:
                    print(f"  ✅ Speicher auflösbar: {storage_product['name']}")
                else:
                    print(f"  ❌ Speicher ID '{storage_id}' nicht gefunden!")
                    
        else:
            print("❌ KRITISCH: project_details fehlen - PDF wird KEINE Module anzeigen!")
            return None
        
        # Weitere wichtige Felder
        if "consumption_data" in project_data:
            print(f"✅ Verbrauchsdaten verfügbar")
        
        print(f"📋 sections_to_include: {kwargs.get('sections_to_include', [])}")
        
        # Simuliere erfolgreiche PDF-Generierung
        print("🎉 PDF-Generierung simuliert erfolgreich!")
        return b"Mock PDF with all product details"
    
    # Mock-Funktionen setzen
    import multi_offer_generator
    multi_offer_generator.get_product_by_id = mock_get_product_by_id
    multi_offer_generator.list_products = mock_list_products
    multi_offer_generator.generate_offer_pdf = mock_generate_offer_pdf
    
    # === SZENARIO 1: Neue Produktauswahl ===
    print("\n🧪 === SZENARIO 1: Neue Produktauswahl im Multi-Offer ===")
    
    test_project_data_1 = {
        "customer_name": "Max Mustermann",
        "customer_email": "max@test.de",
        "customer_address": "Teststraße 123, 12345 Teststadt",
        "consumption_data": {
            "annual_consumption_kwh": 5500,
            "electricity_price_kwh": 0.35
        }
    }
    
    test_settings_1 = {
        "module_quantity": 20,
        "include_storage": True,
        "selected_module_id": "jinko_400w",
        "selected_inverter_id": "fronius_symo_5", 
        "selected_storage_id": "tesla_powerwall"
    }
    
    generator = MultiCompanyOfferGenerator()
    
    offer_data_1 = generator._prepare_offer_data(
        customer_data={"name": "Max Mustermann", "email": "max@test.de"},
        project_data=test_project_data_1,
        settings=test_settings_1,
        company={"id": 1, "name": "Solar Firma A"}
    )
    
    pdf_result_1 = generator._generate_company_pdf(offer_data_1, {"id": 1, "name": "Solar Firma A"})
    print(f"Szenario 1 Ergebnis: {'✅ Erfolgreich' if pdf_result_1 else '❌ Fehlgeschlagen'}")
    
    # === SZENARIO 2: Fallback auf existing project_details ===
    print("\n🧪 === SZENARIO 2: Fallback auf bestehende Projektdaten ===")
    
    test_project_data_2 = {
        "customer_name": "Anna Schmidt",
        "customer_email": "anna@test.de",
        "project_details": {
            "module_quantity": 30,
            "include_storage": False,
            "selected_module_id": "jinko_400w",
            "selected_inverter_id": "fronius_symo_5"
        }
    }
    
    test_settings_2 = {}  # Leer - sollte Fallback verwenden
    
    offer_data_2 = generator._prepare_offer_data(
        customer_data={"name": "Anna Schmidt", "email": "anna@test.de"},
        project_data=test_project_data_2,
        settings=test_settings_2,
        company={"id": 2, "name": "Solar Firma B"}
    )
    
    pdf_result_2 = generator._generate_company_pdf(offer_data_2, {"id": 2, "name": "Solar Firma B"})
    print(f"Szenario 2 Ergebnis: {'✅ Erfolgreich' if pdf_result_2 else '❌ Fehlgeschlagen'}")
    
    print("\n🎯 === FAZIT ===")
    if pdf_result_1 and pdf_result_2:
        print("✅ Alle Szenarien erfolgreich!")
        print("✅ Multi-Offer PDF sollte jetzt alle Module korrekt anzeigen!")
        print("✅ Sowohl neue Auswahl als auch Fallback funktionieren!")
    else:
        print("❌ Mindestens ein Szenario fehlgeschlagen!")

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
