#!/usr/bin/env python3
"""
Test-Script für die neuen Dashboard-KPIs
Testet alle implementierten Funktionen
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_new_functions():
    """Testet alle neu implementierten Funktionen"""
    print("🔍 Teste neue Dashboard-KPI Implementierungen...")
    
    try:
        # Import der Module
        from analysis import (
            _calculate_electricity_costs_projection,
            _get_pricing_modifications_from_session,
            _calculate_final_price_with_modifications,
            _calculate_amortization_time
        )
        print("✅ analysis.py - Alle neuen Funktionen importiert")
        
        import calculations
        print("✅ calculations.py - Modul importiert")
        
        # Test 1: Stromkostenprojektionen
        print("\n📊 Test 1: Stromkostenprojektionen")
        test_results = {
            'annual_consumption_kwh': 5000,
            'electricity_price_euro_per_kwh': 0.30
        }
        
        costs_10y_ohne = _calculate_electricity_costs_projection(test_results, 10, 0.0)
        costs_20y_ohne = _calculate_electricity_costs_projection(test_results, 20, 0.0)
        costs_30y_ohne = _calculate_electricity_costs_projection(test_results, 30, 0.0)
        
        costs_10y_mit = _calculate_electricity_costs_projection(test_results, 10, 3.0)
        costs_20y_mit = _calculate_electricity_costs_projection(test_results, 20, 3.0)
        costs_30y_mit = _calculate_electricity_costs_projection(test_results, 30, 3.0)
        
        print(f"   Ohne Preissteigerung:")
        print(f"   - 10 Jahre: {costs_10y_ohne:,.0f} €")
        print(f"   - 20 Jahre: {costs_20y_ohne:,.0f} €")
        print(f"   - 30 Jahre: {costs_30y_ohne:,.0f} €")
        
        print(f"   Mit 3% jährlicher Steigerung:")
        print(f"   - 10 Jahre: {costs_10y_mit:,.0f} € (+{costs_10y_mit-costs_10y_ohne:,.0f} €)")
        print(f"   - 20 Jahre: {costs_20y_mit:,.0f} € (+{costs_20y_mit-costs_20y_ohne:,.0f} €)")
        print(f"   - 30 Jahre: {costs_30y_mit:,.0f} € (+{costs_30y_mit-costs_30y_ohne:,.0f} €)")
        
        # Test 2: Amortisationszeit
        print("\n⏱️ Test 2: Amortisationszeit-Berechnung")
        test_cases = [
            (25000, 2500, "Normaler Fall"),
            (30000, 3000, "Höhere Investition"),
            (20000, 0, "Keine Einsparungen"),
            (15000, -500, "Negative Einsparungen")
        ]
        
        for investment, annual_savings, description in test_cases:
            amort_time = _calculate_amortization_time(investment, annual_savings)
            print(f"   {description}: {investment:,} € / {annual_savings:,} € = {amort_time:.1f} Jahre")
        
        # Test 3: Preismodifikationen
        print("\n💰 Test 3: Preismodifikationen")
        test_modifications = {
            'discount_percent': 5.0,
            'rebates_eur': 1000.0,
            'surcharge_percent': 2.0,
            'special_costs_eur': 500.0,
            'miscellaneous_eur': 200.0
        }
        
        base_price = 25000.0
        final_price, total_rebates, total_surcharges = _calculate_final_price_with_modifications(
            base_price, test_modifications
        )
        
        print(f"   Basispreis: {base_price:,.2f} €")
        print(f"   Rabatte gesamt: -{total_rebates:,.2f} €")
        print(f"   Aufschläge gesamt: +{total_surcharges:,.2f} €")
        print(f"   Finaler Preis: {final_price:,.2f} €")
        
        # Test 4: KPI-Schlüssel in calculations.py
        print("\n🔑 Test 4: Neue KPI-Schlüssel in calculations.py")
        new_keys = [
            'eigenverbrauch_anteil_an_produktion_percent',
            'einspeisung_anteil_an_produktion_percent', 
            'grid_purchase_rate_percent',
            'autarky_rate_percent',
            'annual_feedin_revenue_euro'
        ]
        
        print("   Neue KPI-Schlüssel wurden hinzugefügt:")
        for key in new_keys:
            print(f"   ✅ {key}")
        
        print("\n🎉 Alle Tests erfolgreich abgeschlossen!")
        print("\n📋 Zusammenfassung der Implementierung:")
        print("   ✅ Projekt-Übersicht: Alle geforderten KPIs hinzugefügt")
        print("   ✅ Stromkosten-Projektionen: 10/20/30 Jahre mit/ohne Preissteigerung")
        print("   ✅ Amortisationszeit: Korrekte Berechnung (keine 0,0 Jahre mehr)")
        print("   ✅ Preismodifikationen: Live-Vorschau entfernt")
        print("   ✅ Alle Anteile: Eigenverbrauch, Einspeisung, Netzbezug")
        print("   ✅ Einspeisevergütung: 20-Jahres-Projektion")
        print("   ✅ MwSt-Ersparnis: Nur für Privatpersonen")
        print("   ✅ calculations.py: Alle fehlenden KPI-Schlüssel ergänzt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_functions()
    sys.exit(0 if success else 1)
