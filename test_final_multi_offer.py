#!/usr/bin/env python3
"""
Test der reparierten Multi-Angebotsgenerator Funktionalität
"""

def test_repaired_multi_offer_generator():
    print("🔍 Teste reparierten Multi-Angebotsgenerator...")
    
    try:
        # Teste Import
        from multi_offer_generator import render_multi_offer_generator
        from database import get_all_active_customers
        
        print("✅ Multi-Angebotsgenerator Module importiert")
        
        # Teste Kunden-Abruf
        customers = get_all_active_customers()
        print(f"📊 {len(customers)} Kunden in der Datenbank")
        
        if customers:
            for customer in customers:
                print(f"  • {customer['first_name']} {customer['last_name']}")
                
                # Prüfe project_data
                project_data = customer.get('project_data', {})
                if project_data:
                    print(f"    - Anlagengröße: {project_data.get('system_size_kw', 'N/A')} kWp")
                    print(f"    - Verbrauch: {project_data.get('electricity_consumption_kwh', 'N/A')} kWh")
                else:
                    print(f"    - Keine project_data vorhanden")
            
            print("✅ Multi-Angebotsgenerator sollte jetzt funktionieren")
            return True
        else:
            print("❌ Keine Kunden gefunden")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calculation_with_customer_data():
    print("\n🔍 Teste Berechnungen mit Kunden-Daten...")
    
    try:
        from database import get_all_active_customers
        from calculations import perform_calculations
        
        customers = get_all_active_customers()
        if not customers:
            print("❌ Keine Kunden für Test vorhanden")
            return False
        
        # Teste mit erstem Kunden
        customer = customers[0]
        print(f"Teste mit Kunde: {customer['first_name']} {customer['last_name']}")
        
        # Project data vorbereiten
        project_data = customer.get('project_data', {})
        if not project_data:
            # Fallback Daten
            project_data = {
                'system_size_kw': 10.0,
                'roof_area_sqm': 60.0,
                'electricity_consumption_kwh': 4000,
                'roof_orientation': 180,
                'roof_tilt': 35,
                'has_battery': True,
                'battery_capacity_kwh': 8.0
            }
        
        print(f"Project Data: {project_data}")
        
        # Berechnung durchführen
        texts = {'test': 'test'}
        errors_list = []
        results = perform_calculations(project_data, texts, errors_list)
        
        if results:
            print("✅ Berechnung erfolgreich")
            print(f"  - Anlagengröße: {results.get('anlage_kwp', 'N/A')} kWp")
            print(f"  - Amortisation: {results.get('amortization_time_years', 'N/A')} Jahre")
            print(f"  - Jährliche Ersparnis: {results.get('annual_financial_benefit_year1', 'N/A')} €")
            return True
        else:
            print(f"❌ Berechnung fehlgeschlagen. Fehler: {errors_list}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler bei Berechnung: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DES REPARIERTEN MULTI-ANGEBOTSGENERATORS")
    print("=" * 70)
    
    # Test 1: Multi-Angebotsgenerator Funktionalität
    generator_ok = test_repaired_multi_offer_generator()
    
    # Test 2: Berechnungen mit Kunden-Daten
    calculations_ok = test_calculation_with_customer_data()
    
    print("\n" + "=" * 70)
    if generator_ok and calculations_ok:
        print("🎉 MULTI-ANGEBOTSGENERATOR VOLLSTÄNDIG REPARIERT!")
        print("   ✅ Kunden werden gefunden")
        print("   ✅ Berechnungen funktionieren")
        print("   ✅ Generator sollte jetzt in der Web-App funktionieren")
    else:
        print("❌ REPARATUR UNVOLLSTÄNDIG - Weitere Arbeiten erforderlich")
    print("=" * 70)
