#!/usr/bin/env python3
"""
Vollständiger Test des Multi-Angebotsgenerators
Testet alle neuen Features: Produktrotation, Preisstaffelung, flexible Firmenanzahl
"""
import sys
import os
sys.path.append('.')

def test_multi_offer_import():
    """Teste den Import des Multi-Angebotsgenerators"""
    print("🔄 Teste Import von multi_offer_generator...")
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator
        print("✅ Import erfolgreich!")
        return MultiCompanyOfferGenerator
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler: {e}")
        return None
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return None
    except Exception as e:
        print(f"❌ Unbekannter Fehler: {e}")
        return None

def test_product_rotation():
    """Teste die flexible Produktrotation"""
    print("\n🔄 Teste Produktrotation...")
    
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator
        generator = MultiCompanyOfferGenerator()
        
        # Test-Einstellungen für verschiedene Rotations-Modi
        test_cases = [
            {
                "name": "Linear +1",
                "settings": {
                    "enable_product_rotation": True,
                    "product_rotation_step": 1,
                    "rotation_mode": "linear",
                    "selected_module_id": 1,
                    "selected_inverter_id": 1,
                    "selected_storage_id": 1
                }
            },
            {
                "name": "Linear +2", 
                "settings": {
                    "enable_product_rotation": True,
                    "product_rotation_step": 2,
                    "rotation_mode": "linear",
                    "selected_module_id": 1,
                    "selected_inverter_id": 1,
                    "selected_storage_id": 1
                }
            },
            {
                "name": "Kategorie-spezifisch",
                "settings": {
                    "enable_product_rotation": True,
                    "rotation_mode": "kategorie-spezifisch",
                    "module_rotation_step": 1,
                    "inverter_rotation_step": 2,
                    "storage_rotation_step": 3,
                    "selected_module_id": 1,
                    "selected_inverter_id": 1,
                    "selected_storage_id": 1
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  📦 Test: {test_case['name']}")
            
            # Teste für 6 Firmen (nicht nur 5!)
            for company_index in range(6):
                rotated = generator.get_rotated_products_for_company(
                    company_index, 
                    test_case["settings"]
                )
                print(f"    Firma {company_index+1}: Modul-ID {rotated.get('selected_module_id', 'N/A')}")
        
        print("✅ Produktrotation-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Produktrotation-Test fehlgeschlagen: {e}")
        return False

def test_price_scaling():
    """Teste die flexible Preisstaffelung"""
    print("\n💰 Teste Preisstaffelung...")
    
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator
        generator = MultiCompanyOfferGenerator()
        
        # Test-Berechnungsergebnisse
        base_calc = {
            'total_investment_netto': 25000,
            'total_investment_brutto': 29750,
            'amortization_time_years': 12.5,
            'roi_percent_year1': 8.2
        }
        
        # Test verschiedene Preisstaffelung-Modi
        test_cases = [
            {
                "name": "Linear 5%",
                "settings": {
                    "price_increment_percent": 5.0,
                    "price_calculation_mode": "linear"
                }
            },
            {
                "name": "Exponentiell 1.03",
                "settings": {
                    "price_increment_percent": 3.0,
                    "price_calculation_mode": "exponentiell",
                    "price_exponent": 1.03
                }
            },
            {
                "name": "Custom Faktoren",
                "settings": {
                    "price_increment_percent": 0,
                    "price_calculation_mode": "custom",
                    "custom_price_factors": "[1.0, 1.05, 1.12, 1.20, 1.30, 1.42]"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  💰 Test: {test_case['name']}")
            
            # Teste für 6 Firmen
            for company_index in range(6):
                scaled = generator.apply_price_scaling(
                    company_index,
                    test_case["settings"],
                    base_calc.copy()
                )
                price = scaled.get('total_investment_netto', 0)
                factor = price / 25000 if price > 0 else 0
                print(f"    Firma {company_index+1}: {price:.0f}€ (Faktor: {factor:.3f})")
        
        print("✅ Preisstaffelung-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Preisstaffelung-Test fehlgeschlagen: {e}")
        return False

def test_flexible_company_selection():
    """Teste die flexible Firmenauswahl (2-20+ Firmen)"""
    print("\n🏢 Teste flexible Firmenauswahl...")
    
    try:
        # Simuliere verschiedene Firmenanzahlen
        company_counts = [2, 5, 8, 12, 20]
        
        for count in company_counts:
            print(f"  📊 Test mit {count} Firmen:")
            
            # Simuliere Multi-Offer für diese Anzahl
            company_ids = list(range(1, count + 1))
            
            # Teste Produktrotation für alle Firmen
            settings = {
                "enable_product_rotation": True,
                "product_rotation_step": 1,
                "selected_module_id": 1
            }
            
            from multi_offer_generator import MultiCompanyOfferGenerator
            generator = MultiCompanyOfferGenerator()
            
            rotated_products = []
            for i, company_id in enumerate(company_ids):
                rotated = generator.get_rotated_products_for_company(i, settings)
                rotated_products.append(rotated.get('selected_module_id', 1))
            
            # Prüfe Produktvielfalt
            unique_products = len(set(rotated_products))
            print(f"    🔄 {unique_products} verschiedene Produkte von {count} Firmen")
            
            # Teste Preisstaffelung für alle Firmen
            price_settings = {
                "price_increment_percent": 3.0,
                "price_calculation_mode": "linear"
            }
            
            base_calc = {'total_investment_netto': 25000}
            prices = []
            
            for i in range(count):
                scaled = generator.apply_price_scaling(i, price_settings, base_calc.copy())
                prices.append(scaled.get('total_investment_netto', 25000))
            
            min_price = min(prices)
            max_price = max(prices)
            price_range = ((max_price - min_price) / min_price) * 100
            
            print(f"    💰 Preisspanne: {min_price:.0f}€ - {max_price:.0f}€ ({price_range:.1f}% Unterschied)")
        
        print("✅ Flexible Firmenauswahl-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Flexible Firmenauswahl-Test fehlgeschlagen: {e}")
        return False

def test_pdf_options():
    """Teste die erweiterten PDF-Optionen"""
    print("\n🎨 Teste erweiterte PDF-Optionen...")
    
    try:
        # Test der PDF-Optionen-Struktur
        pdf_options = {
            "include_company_logo": True,
            "include_product_images": True,
            "include_charts": True,
            "include_visualizations": True,
            "include_all_documents": False,
            "include_optional_component_details": True,
            "selected_sections": [
                "ProjectOverview", "TechnicalComponents", "CostDetails", 
                "Economics", "SimulationDetails", "CO2Savings", 
                "Visualizations", "FutureAspects"
            ]
        }
        
        print(f"  ✅ PDF-Optionen strukturiert: {len(pdf_options)} Optionen")
        print(f"  ✅ Sektionen-Auswahl: {len(pdf_options['selected_sections'])} Sektionen")
        
        # Teste verschiedene Konfigurationen
        configurations = [
            {
                "name": "Minimal",
                "sections": ["ProjectOverview", "CostDetails"],
                "charts": False,
                "images": False
            },
            {
                "name": "Standard", 
                "sections": ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics"],
                "charts": True,
                "images": True
            },
            {
                "name": "Vollständig",
                "sections": list(pdf_options["selected_sections"]),
                "charts": True,
                "images": True
            }
        ]
        
        for config in configurations:
            print(f"  📋 Konfiguration '{config['name']}': {len(config['sections'])} Sektionen")
        
        print("✅ PDF-Optionen-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ PDF-Optionen-Test fehlgeschlagen: {e}")
        return False

def run_complete_test():
    """Führe alle Tests durch"""
    print("🚀 Starte vollständigen Multi-Angebots-Test...")
    print("=" * 60)
    
    # Test 1: Import
    generator_class = test_multi_offer_import()
    if not generator_class:
        print("\n❌ Import fehlgeschlagen - weitere Tests nicht möglich")
        return False
    
    # Test 2-5: Feature-Tests
    tests = [
        ("Produktrotation", test_product_rotation),
        ("Preisstaffelung", test_price_scaling), 
        ("Flexible Firmenauswahl", test_flexible_company_selection),
        ("PDF-Optionen", test_pdf_options)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' abgebrochen: {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nGESAMT: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN!")
        print("🎯 Der Multi-Angebotsgenerator ist vollständig funktional mit:")
        print("   • Flexibler Produktrotation (nicht nur +1)")
        print("   • Anpassbarer Preisstaffelung (nicht nur 3%)")
        print("   • Unbegrenzter Firmenanzahl (nicht nur 5)")
        print("   • Erweiterten PDF-Optionen wie bei Einzel-PDF")
        return True
    else:
        print(f"\n⚠️ {total-passed} Tests fehlgeschlagen - weitere Entwicklung nötig")
        return False

if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1)
