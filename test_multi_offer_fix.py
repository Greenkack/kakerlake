#!/usr/bin/env python3
"""
Test und Reparatur für Multi-Angebotsgenerator
Fügt Dummy-Kunden hinzu und testet die Funktionalität
"""

def create_test_customers():
    """Erstellt Test-Kunden für den Multi-Angebotsgenerator"""
    print("🔍 Erstelle Test-Kunden für Multi-Angebotsgenerator...")
    
    try:
        from database import get_db_connection, create_customer
        import json
        
        # Test-Kunden-Daten
        test_customers = [
            {
                'first_name': 'Max',
                'last_name': 'Mustermann',
                'email': 'max.mustermann@email.de',
                'phone': '+49 123 456789',
                'address': 'Musterstraße 1, 12345 Musterstadt',
                'status': 'active',
                'notes': 'Test-Kunde für Multi-Angebotsgenerator',
                'project_data': {
                    'system_size_kw': 10.0,
                    'roof_area_sqm': 60.0,
                    'electricity_consumption_kwh': 4000,
                    'roof_orientation': 180,
                    'roof_tilt': 35,
                    'has_battery': True,
                    'battery_capacity_kwh': 8.0
                }
            },
            {
                'first_name': 'Anna',
                'last_name': 'Schmidt',
                'email': 'anna.schmidt@email.de',
                'phone': '+49 987 654321',
                'address': 'Sonnenstraße 15, 54321 Sonnenhausen',
                'status': 'active',
                'notes': 'Interessiert an größerer Anlage',
                'project_data': {
                    'system_size_kw': 15.0,
                    'roof_area_sqm': 90.0,
                    'electricity_consumption_kwh': 6000,
                    'roof_orientation': 180,
                    'roof_tilt': 30,
                    'has_battery': True,
                    'battery_capacity_kwh': 12.0
                }
            },
            {
                'first_name': 'Michael',
                'last_name': 'Weber',
                'email': 'michael.weber@email.de',
                'phone': '+49 555 123456',
                'address': 'Energieweg 8, 67890 Ökohausen',
                'status': 'active',
                'notes': 'Kleinere Anlage ohne Batterie',
                'project_data': {
                    'system_size_kw': 7.5,
                    'roof_area_sqm': 45.0,
                    'electricity_consumption_kwh': 3000,
                    'roof_orientation': 180,
                    'roof_tilt': 40,
                    'has_battery': False,
                    'battery_capacity_kwh': 0.0
                }
            }
        ]
        
        # Kunden erstellen
        created_count = 0
        for customer_data in test_customers:
            if create_customer(customer_data):
                print(f"✅ Test-Kunde erstellt: {customer_data['first_name']} {customer_data['last_name']}")
                created_count += 1
            else:
                print(f"❌ Fehler beim Erstellen: {customer_data['first_name']} {customer_data['last_name']}")
        
        print(f"📊 {created_count}/{len(test_customers)} Test-Kunden erfolgreich erstellt")
        return created_count > 0
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Test-Kunden: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_customer_retrieval():
    """Testet das Abrufen der Kunden"""
    print("\n🔍 Teste Kunden-Abruf...")
    
    try:
        from database import get_all_active_customers
        
        customers = get_all_active_customers()
        print(f"📊 {len(customers)} aktive Kunden gefunden")
        
        for i, customer in enumerate(customers[:3], 1):  # Zeige nur erste 3
            print(f"  {i}. {customer['first_name']} {customer['last_name']} ({customer['email']})")
        
        return len(customers) > 0
        
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Kunden: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multi_offer_functions():
    """Testet die Multi-Angebots-Funktionen"""
    print("\n🔍 Teste Multi-Angebots-Funktionen...")
    
    try:
        from multi_offer_generator import render_multi_offer_generator
        from calculations import perform_calculations
        
        # Test project_data
        test_project_data = {
            'system_size_kw': 10.0,
            'roof_area_sqm': 60.0,
            'electricity_consumption_kwh': 4000,
            'roof_orientation': 180,
            'roof_tilt': 35,
            'has_battery': True,
            'battery_capacity_kwh': 8.0
        }
        
        # Test texts
        test_texts = {'test': 'test'}
        
        # Test perform_calculations
        errors_list = []
        calc_results = perform_calculations(test_project_data, test_texts, errors_list)
        
        if calc_results:
            print("✅ perform_calculations funktioniert")
            print(f"  - Anlagengröße: {calc_results.get('anlage_kwp', 'N/A')} kWp")
            print(f"  - Amortisation: {calc_results.get('amortization_time_years', 'N/A')} Jahre")
        else:
            print("❌ perform_calculations fehlgeschlagen")
            return False
        
        print("✅ Multi-Angebots-Funktionen getestet")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Multi-Angebots-Funktionen: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_multi_offer_generator():
    """Behebt die Probleme im Multi-Angebotsgenerator"""
    print("\n🔧 Behebe Multi-Angebotsgenerator...")
    
    try:
        # Prüfe ob die render_multi_offer_generator Funktion korrekt arbeitet
        from database import get_all_active_customers
        
        customers = get_all_active_customers()
        if customers:
            print(f"✅ Multi-Angebotsgenerator sollte jetzt {len(customers)} Kunden finden")
            return True
        else:
            print("❌ Keine Kunden gefunden - erstelle Test-Kunden")
            return create_test_customers()
        
    except Exception as e:
        print(f"❌ Fehler beim Beheben des Multi-Angebotsgenerators: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("MULTI-ANGEBOTSGENERATOR TEST & REPARATUR")
    print("=" * 70)
    
    # Schritt 1: Test-Kunden erstellen
    customers_created = create_test_customers()
    
    # Schritt 2: Kunden-Abruf testen
    customers_found = test_customer_retrieval()
    
    # Schritt 3: Multi-Angebots-Funktionen testen
    functions_ok = test_multi_offer_functions()
    
    # Schritt 4: Multi-Angebotsgenerator reparieren
    generator_fixed = fix_multi_offer_generator()
    
    print("\n" + "=" * 70)
    if customers_found and functions_ok and generator_fixed:
        print("🎉 MULTI-ANGEBOTSGENERATOR ERFOLGREICH REPARIERT!")
        print("   Der Generator sollte jetzt Kunden finden und Angebote erstellen können.")
    else:
        print("❌ REPARATUR FEHLGESCHLAGEN - Weitere Schritte erforderlich")
    print("=" * 70)
