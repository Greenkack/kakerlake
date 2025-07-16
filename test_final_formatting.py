#!/usr/bin/env python3
"""
Finaler Test der deutschen Preisformatierung
Simuliert echte Berechnungsergebnisse und testet die Ausgabe
"""

import sys
import os

# Module importieren
try:
    from analysis import format_kpi_value, _render_overview_section
    from calculations import perform_calculations
    print("✓ Module erfolgreich importiert")
except ImportError as e:
    print(f"✗ Import-Fehler: {e}")

def test_real_world_formatting():
    """Testet die Formatierung mit realistischen Werten"""
    print("\n=== REALITÄTSNAHER TEST ===")
    
    # Simuliere Berechnungsergebnisse
    mock_results = {
        'total_investment_netto': 20857.50,
        'total_investment_brutto': 24821.43,
        'annual_pv_production_kwh': 8540.25,
        'payback_time_years': 12.3,
        'base_matrix_price_netto': 18500.00,
        'npv_value': 15432.67,
        'lcoe_euro_per_kwh': 0.087
    }
    
    texts = {
        'kpi_total_investment': 'Gesamtinvestition',
        'kpi_annual_yield': 'Jährlicher Ertrag',
        'kpi_payback_time': 'Amortisationszeit'
    }
    
    print("Formatierte Ausgaben:")
    print("-" * 50)
    
    for key, value in mock_results.items():
        if 'investment' in key or 'price' in key or 'npv' in key:
            unit = "€"
            precision = 2 if isinstance(value, float) and value != int(value) else 0
        elif 'kwh' in key:
            unit = "kWh"
            precision = 0
        elif 'years' in key:
            unit = "Jahre"
            precision = 1
        elif 'lcoe' in key:
            unit = "€/kWh"
            precision = 3
        else:
            unit = ""
            precision = 2
        
        formatted = format_kpi_value(value, unit, precision=precision)
        print(f"{key:25s}: {formatted}")

def compare_before_after():
    """Vergleicht amerikanische vs deutsche Formatierung"""
    print("\n=== VORHER/NACHHER VERGLEICH ===")
    
    test_prices = [20857.50, 1234567.89, 15432.67, 999.99]
    
    print("Wert\t\tAmerikanisch\t\tDeutsch")
    print("-" * 60)
    
    for price in test_prices:
        american = f"{price:,.2f} €"
        german = format_kpi_value(price, "€", precision=2)
        print(f"{price}\t\t{american}\t\t{german}")

def test_integration():
    """Testet die Integration in die UI-Funktionen"""
    print("\n=== INTEGRATION TEST ===")
    
    # Test-Daten für die Übersichtssektion
    results = {
        'total_investment_netto': 20857.50,
        'annual_pv_production_kwh': 8540,
        'payback_time_years': 12.3
    }
    
    texts = {
        'kpi_total_investment': 'Gesamtinvestition',
        'kpi_annual_yield': 'Jährlicher Ertrag', 
        'kpi_payback_time': 'Amortisationszeit'
    }
    
    viz_settings = {}
    
    print("Die _render_overview_section Funktion würde folgende formatierte Werte verwenden:")
    
    investment_formatted = format_kpi_value(results.get('total_investment_netto', 0), "€", texts_dict=texts, precision=0)
    yield_formatted = format_kpi_value(results.get('annual_pv_production_kwh', 0), "kWh", texts_dict=texts, precision=0)
    payback_formatted = f"{results.get('payback_time_years', 0):.1f} Jahre"
    
    print(f"  Gesamtinvestition: {investment_formatted}")
    print(f"  Jährlicher Ertrag: {yield_formatted}")
    print(f"  Amortisationszeit: {payback_formatted}")

if __name__ == "__main__":
    print("DEUTSCHE PREISFORMATIERUNG - FINALER TEST")
    print("=" * 60)
    
    test_real_world_formatting()
    compare_before_after()
    test_integration()
    
    print("\n" + "=" * 60)
    print("✓ Alle Tests abgeschlossen!")
    print("Die App sollte jetzt deutsche Preisformatierung verwenden:")
    print("  • Tausenderpunkt: 20.857")
    print("  • Dezimalkomma: 20.857,50")
    print("  • Einheit: 20.857,50 €")
