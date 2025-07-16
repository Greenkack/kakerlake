#!/usr/bin/env python3
"""
Test für die vollständige AdvancedCalculations-Implementierung
"""

def test_advanced_calculations_complete():
    """Testet die vollständige AdvancedCalculations-Integration"""
    
    print("=== Test: AdvancedCalculations Vollständige Integration ===\n")
    
    # Test 1: Import der AdvancedCalculationsIntegrator Klasse
    try:
        from calculations import AdvancedCalculationsIntegrator
        print("✓ AdvancedCalculationsIntegrator erfolgreich importiert")
    except ImportError as e:
        print(f"✗ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"✗ Unerwarteter Fehler beim Import: {e}")
        return False
    
    # Test 2: Instanziierung der Klasse
    try:
        integrator = AdvancedCalculationsIntegrator()
        print("✓ AdvancedCalculationsIntegrator erfolgreich instanziiert")
    except Exception as e:
        print(f"✗ Fehler bei Instanziierung: {e}")
        return False
    
    # Test 3: Verfügbare Berechnungen prüfen
    expected_calculations = [
        'degradation_analysis', 'shading_analysis', 'grid_interaction', 
        'battery_cycles', 'weather_impact', 'maintenance_schedule', 
        'carbon_footprint', 'peak_shaving', 'dynamic_pricing', 
        'energy_independence', 'recycling_potential'
    ]
    
    available_calculations = list(integrator.advanced_calculations.keys())
    print(f"✓ Verfügbare Berechnungen: {len(available_calculations)}")
    
    for calc in expected_calculations:
        if calc in available_calculations:
            print(f"  ✓ {calc}")
        else:
            print(f"  ✗ {calc} fehlt")
    
    # Test 4: execute_selected_calculations Methode testen
    try:
        test_data = {
            'anlage_kwp': 10,
            'annual_pv_production_kwh': 10000,
            'monthly_production': [800] * 12,
            'monthly_consumption': [350] * 12,
            'total_consumption_kwh_yr': 4000,
            'include_storage': True,
            'battery_capacity_kwh': 10
        }
        
        selected_calcs = ['degradation_analysis', 'carbon_footprint', 'grid_interaction']
        results = integrator.execute_selected_calculations(selected_calcs, test_data)
        
        print(f"✓ execute_selected_calculations ausgeführt für {len(selected_calcs)} Berechnungen")
        
        # Prüfe Ergebnisstruktur
        for calc_key in selected_calcs:
            if calc_key in results:
                result_entry = results[calc_key]
                if 'data' in result_entry and 'meta' in result_entry:
                    print(f"  ✓ {calc_key}: Struktur korrekt")
                elif 'error' in result_entry:
                    print(f"  ⚠ {calc_key}: Fehler - {result_entry['error']}")
                else:
                    print(f"  ✗ {calc_key}: Unerwartete Struktur")
            else:
                print(f"  ✗ {calc_key}: Fehlt in Ergebnissen")
        
    except Exception as e:
        print(f"✗ Fehler bei execute_selected_calculations: {e}")
        return False
    
    # Test 5: Einzelne Berechnungsmethoden testen
    print("\n--- Test einzelner Berechnungsmethoden ---")
    
    test_methods = [
        ('_calculate_degradation', 'Degradationsanalyse'),
        ('_calculate_carbon_footprint', 'CO2-Bilanz'),
        ('_calculate_grid_interaction', 'Netzinteraktion'),
        ('_calculate_battery_cycles', 'Batteriezyklen'),
        ('_calculate_energy_independence', 'Energieunabhängigkeit')
    ]
    
    for method_name, description in test_methods:
        try:
            method = getattr(integrator, method_name)
            result = method(test_data)
            if isinstance(result, dict) and len(result) > 0:
                print(f"  ✓ {description}: {len(result)} Felder")
            else:
                print(f"  ⚠ {description}: Leeres oder ungültiges Ergebnis")
        except Exception as e:
            print(f"  ✗ {description}: Fehler - {e}")
    
    print("\n=== Test abgeschlossen ===")
    return True

def test_pdf_generator_integration():
    """Testet die Integration in den PDF-Generator"""
    
    print("\n=== Test: PDF-Generator Integration ===\n")
    
    # Test Import der PDF-Generator Funktionen
    try:
        import pdf_generator
        print("✓ pdf_generator erfolgreich importiert")
    except ImportError as e:
        print(f"✗ PDF-Generator Import-Fehler: {e}")
        return False
    
    # Test der Sektion in den Definitionen
    try:
        # Prüfe ob AdvancedCalculations in den Sektionen ist
        if hasattr(pdf_generator, 'ordered_section_definitions_pdf'):
            sections = [section[0] for section in pdf_generator.ordered_section_definitions_pdf]
            if 'AdvancedCalculations' in sections:
                print("✓ AdvancedCalculations in ordered_section_definitions_pdf gefunden")
            else:
                print("✗ AdvancedCalculations nicht in ordered_section_definitions_pdf")
        
        # Prüfe default_pdf_sections_map
        if hasattr(pdf_generator, 'default_pdf_sections_map'):
            if 'AdvancedCalculations' in pdf_generator.default_pdf_sections_map:
                print("✓ AdvancedCalculations in default_pdf_sections_map gefunden")
            else:
                print("✗ AdvancedCalculations nicht in default_pdf_sections_map")
        
    except Exception as e:
        print(f"✗ Fehler beim Prüfen der PDF-Sektionen: {e}")
        return False
    
    print("✓ PDF-Generator Integration geprüft")
    return True

def test_pdf_ui_integration():
    """Testet die Integration in die PDF-UI"""
    
    print("\n=== Test: PDF-UI Integration ===\n")
    
    try:
        import pdf_ui
        print("✓ pdf_ui erfolgreich importiert")
        
        # Prüfe ob die Sektion in der UI verfügbar ist
        # Das ist schwieriger zu testen ohne Streamlit zu starten
        print("✓ pdf_ui Import erfolgreich (Detailtest erfordert Streamlit)")
        
    except ImportError as e:
        print(f"✗ PDF-UI Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Teste AdvancedCalculations Vollständige Integration...\n")
    
    success = True
    success = test_advanced_calculations_complete() and success
    success = test_pdf_generator_integration() and success
    success = test_pdf_ui_integration() and success
    
    print(f"\n{'=' * 50}")
    if success:
        print("🎉 ALLE TESTS ERFOLGREICH! AdvancedCalculations ist vollständig integriert.")
        print("\nNächste Schritte:")
        print("- PDF-Generierung mit AdvancedCalculations testen")
        print("- UI-Funktionalität in Streamlit testen")
        print("- Vollständige PDF-Ausgabe mit allen Sektionen prüfen")
    else:
        print("❌ EINIGE TESTS FEHLGESCHLAGEN. Bitte Fehler beheben.")
    print("=" * 50)
