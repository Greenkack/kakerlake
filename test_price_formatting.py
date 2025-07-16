#!/usr/bin/env python3
"""
Test-Skript für deutsche Preisformatierung
Testet die format_kpi_value Funktion aus analysis.py
"""

import sys
import os

# Module importieren
try:
    from analysis import format_kpi_value
    print("✓ format_kpi_value erfolgreich aus analysis.py importiert")
except ImportError as e:
    print(f"✗ Fehler beim Importieren von format_kpi_value: {e}")
    sys.exit(1)

def test_price_formatting():
    """Testet die deutsche Preisformatierung"""
    print("\n=== TEST: Deutsche Preisformatierung ===")
    
    # Testdaten
    test_values = [
        (20857, "€", "20.857 €"),
        (20857.50, "€", "20.857,50 €"),
        (1234567.89, "€", "1.234.567,89 €"),
        (1000, "€", "1.000 €"),
        (100.5, "€", "100,50 €"),
        (0, "€", "0 €"),
        (999.99, "€", "999,99 €"),
        (1000000, "€", "1.000.000 €"),
    ]
    
    print("Eingabewert\t\tErwartet\t\tErgebnis\t\tStatus")
    print("-" * 80)
    
    for value, unit, expected in test_values:
        result = format_kpi_value(value, unit, precision=2 if isinstance(value, float) and value != int(value) else 0)
        status = "✓ OK" if result == expected else "✗ FEHLER"
        print(f"{value}\t\t\t{expected}\t\t{result}\t\t{status}")
        
        if status == "✗ FEHLER":
            print(f"   -> Erwartet: '{expected}', bekommen: '{result}'")
    
    print("\n=== TEST: Spezielle Fälle ===")
    
    # Spezielle Fälle
    special_tests = [
        (None, "€", "k.A."),
        (float('inf'), "€", "Nicht berechenbar"),
        ("20857", "€", "20.857 €"),  # String-Eingabe
        (20857.123, "Jahre", "20857,12 Jahre"),  # Jahre-Formatierung
    ]
    
    for value, unit, description in special_tests:
        result = format_kpi_value(value, unit)
        print(f"format_kpi_value({value}, '{unit}') = '{result}' ({description})")

def test_american_vs_german():
    """Vergleicht amerikanische vs. deutsche Formatierung"""
    print("\n=== VERGLEICH: Amerikanisch vs. Deutsch ===")
    
    test_value = 20857.50
    
    # Amerikanische Formatierung (Standard Python)
    american = f"{test_value:,.2f} €"
    
    # Deutsche Formatierung (unsere Funktion)
    german = format_kpi_value(test_value, "€", precision=2)
    
    print(f"Amerikanische Formatierung: {american}")
    print(f"Deutsche Formatierung:      {german}")
    print(f"Problem gelöst: {'✓ JA' if german != american else '✗ NEIN'}")

if __name__ == "__main__":
    print("DEUTSCHE PREISFORMATIERUNG - TESTSKRIPT")
    print("=" * 50)
    
    test_price_formatting()
    test_american_vs_german()
    
    print("\n" + "=" * 50)
    print("Test abgeschlossen.")
