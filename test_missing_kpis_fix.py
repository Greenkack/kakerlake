#!/usr/bin/env python3
"""Test für fehlende Kennzahlen-Korrektur"""

import sys
sys.path.append('.')

def test_missing_kpis_fix():
    """Test der total_investment_cost_netto Korrektur"""
    print("🔧 Teste fehlende Kennzahlen-Korrektur...")
    
    try:
        from calculations import perform_calculations
        
        # Minimale Test-Daten
        test_project_data = {
            'anlage_kwp': 8.5,
            'battery_capacity_kwh': 5.0,
            'consumption_kwh_per_year': 4500,
            'company_information': {
                'name': 'Test Solar GmbH',
                'address': 'Musterstraße 123',
                'city': '12345 Musterstadt',
                'phone': '+49 123 456789',
                'email': 'info@testsolar.de'
            }
        }
        
        test_texts = {
            'calculation_error': 'Berechnungsfehler',
            'pdf_warning_no_company': 'Keine Firmendaten verfügbar - Fallback wird verwendet'
        }
        
        errors_list = []
        
        print("⚙️ Führe Testberechnung durch...")
        results = perform_calculations(
            test_project_data,
            texts=test_texts,
            errors_list=errors_list
        )
        
        if results:
            print("✅ Berechnung erfolgreich")
            
            # Prüfe kritische Kennzahlen
            critical_kpis = [
                'total_investment_netto',
                'total_investment_cost_netto',  # Das war das fehlende Feld
                'anlage_kwp',
                'annual_pv_production_kwh'
            ]
            
            print("\n📊 Prüfe kritische Kennzahlen:")
            print("-" * 50)
            
            all_present = True
            for kpi in critical_kpis:
                if kpi in results:
                    value = results[kpi]
                    print(f"✅ {kpi}: {value}")
                else:
                    print(f"❌ {kpi}: FEHLT")
                    all_present = False
            
            print("-" * 50)
            
            if all_present:
                print("🎉 ALLE KRITISCHEN KENNZAHLEN VERFÜGBAR!")
                
                # Zusätzlich: Test der Firmendaten
                if test_project_data.get('company_information', {}).get('name'):
                    print("✅ Firmendaten verfügbar")
                else:
                    print("⚠️ Firmendaten fehlen (nur Warnung)")
                
                return True
            else:
                print("⚠️ Einige kritische Kennzahlen fehlen noch")
                return False
        else:
            print("❌ Berechnung fehlgeschlagen")
            if errors_list:
                for error in errors_list:
                    print(f"   Fehler: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Test-Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 TEST DER FEHLENDEN KENNZAHLEN-KORREKTUR")
    print("=" * 60)
    
    success = test_missing_kpis_fix()
    
    if success:
        print("\n🎊 TEST ERFOLGREICH!")
        print("Die fehlenden Kennzahlen wurden behoben!")
    else:
        print("\n⚠️ Test nicht vollständig erfolgreich")
        print("Weitere Anpassungen könnten erforderlich sein.")
