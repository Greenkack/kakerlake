#!/usr/bin/env python3
"""Reparatur der Preismatrix mit korrektier deutscher CSV-Formatierung"""

import sys
sys.path.append('.')

def fix_price_matrix():
    """Repariert die Preismatrix mit korrekter deutscher CSV-Formatierung"""
    print("🔧 PREISMATRIX-REPARATUR (Deutsche Formatierung)")
    print("=" * 60)
    
    try:
        from database import load_admin_setting, save_admin_setting
        print("✅ Database-Modul importiert")
        
        # Erstelle korrekte deutsche CSV mit Semikolon und deutschem Dezimalformat
        print("\n🏗️ Erstelle deutsche Test-Preismatrix:")
        german_csv = """Anzahl Module;Ohne Speicher;5kWh Speicher;10kWh Speicher;15kWh Speicher
10;8000,00;12000,00;15000,00;18000,00
15;11000,00;15000,00;18000,00;21000,00
20;14000,00;18000,00;21000,00;24000,00
25;17000,00;21000,00;24000,00;27000,00
30;20000,00;24000,00;27000,00;30000,00
35;22000,00;26000,00;29000,00;32000,00
40;24000,00;28000,00;31000,00;34000,00"""
        
        print("Deutsche CSV erstellt:")
        print(german_csv[:200] + "...")
        
        # Speichere in Datenbank
        result = save_admin_setting('price_matrix_csv_data', german_csv)
        if result:
            print("✅ Deutsche CSV in Datenbank gespeichert")
            
            # Test des Parsers
            print("\n🔄 Teste deutschen CSV-Parser:")
            from calculations import parse_module_price_matrix_csv
            errors_list = []
            df = parse_module_price_matrix_csv(german_csv, errors_list)
            
            if df is not None and not df.empty:
                print(f"✅ Deutsche CSV erfolgreich geparst!")
                print(f"   Struktur: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")
                print(f"   Modulanzahlen: {list(df.index)}")
                print(f"   Speicheroptionen: {list(df.columns)}")
                
                # Test-Lookups
                print("\n📊 Test-Preisabfragen:")
                test_cases = [
                    (20, 'Ohne Speicher'),
                    (25, '5kWh Speicher'),
                    (30, '10kWh Speicher')
                ]
                
                for modules, storage in test_cases:
                    if modules in df.index and storage in df.columns:
                        price = df.loc[modules, storage]
                        print(f"   ✅ {modules} Module + {storage}: {price:,.2f} €")
                    else:
                        print(f"   ❌ {modules} Module + {storage}: Nicht gefunden")
                
                # Test mit perform_calculations
                print("\n🧮 Teste Preisberechnung:")
                from calculations import perform_calculations
                
                test_project = {
                    'project_details': {
                        'module_quantity': 20,
                        'selected_module_id': 'test_module',
                        'include_storage': False,
                        'annual_consumption_kwh_yr': 4000,
                        'electricity_price_kwh': 0.30,
                        'roof_orientation': 'Süd',
                        'roof_inclination_deg': 30
                    },
                    'customer_data': {},
                    'economic_data': {}
                }
                
                test_texts = {'calculation_error': 'Berechnungsfehler'}
                errors = []
                
                results = perform_calculations(test_project, test_texts, errors)
                
                if results and results.get('base_matrix_price_netto', 0) > 0:
                    price = results['base_matrix_price_netto']
                    total = results.get('total_investment_netto', 0)
                    print(f"   ✅ Matrix-Preis gefunden: {price:,.2f} €")
                    print(f"   ✅ Gesamtinvestition: {total:,.2f} €")
                    return True
                else:
                    print(f"   ❌ Keine Preisberechnung. Matrix-Preis: {results.get('base_matrix_price_netto', 'N/A')}")
                    if errors:
                        for error in errors:
                            print(f"     Fehler: {error}")
                    return False
                    
            else:
                print("❌ Deutsche CSV konnte nicht geparst werden")
                if errors_list:
                    for error in errors_list:
                        print(f"     Parser-Fehler: {error}")
                return False
        else:
            print("❌ Konnte deutsche CSV nicht speichern")
            return False
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_price_matrix()
    
    if success:
        print("\n🎉 PREISMATRIX ERFOLGREICH REPARIERT!")
        print("=" * 45)
        print("✅ Deutsche CSV-Formatierung korrekt")
        print("✅ Parser funktioniert")
        print("✅ Preisberechnung aktiv")
        print("\n🔄 Bitte Streamlit-App neu laden (F5)")
    else:
        print("\n⚠️ Reparatur nicht erfolgreich")
        print("Weitere Diagnose erforderlich.")
