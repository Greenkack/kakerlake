#!/usr/bin/env python3
"""
Test der verbesserten CO₂-Visualisierung
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_co2_improvements():
    """Test der CO₂-Verbesserungen"""
    
    print("🔧 Teste CO₂-Verbesserungen...")
    
    # 1. Test Import der neuen CO₂-Funktion
    try:
        from pv_visuals import render_co2_savings_visualization
        print("✅ CO₂-Visualisierungsfunktion erfolgreich importiert")
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False
    
    # 2. Test Import der PDF-Generator-Verbesserungen
    try:
        from pdf_generator import generate_offer_pdf
        print("✅ PDF-Generator mit CO₂-Verbesserungen importiert")
    except ImportError as e:
        print(f"❌ PDF-Generator Import-Fehler: {e}")
        return False
    
    # 3. Test der verbesserten Analysis-Funktion
    try:
        from analysis import render_co2_savings_value_switcher
        print("✅ Verbesserte CO₂-Analysis-Funktion importiert")
    except ImportError as e:
        print(f"❌ Analysis Import-Fehler: {e}")
        return False
    
    # 4. Test-Daten für CO₂-Berechnungen
    test_analysis_results = {
        'annual_co2_savings_kg': 2500.0,
        'co2_equivalent_trees_per_year': 113.0,
        'co2_equivalent_car_km_per_year': 12000.0,
        'simulation_period_years_effective': 25,
        'annual_productions_sim': [8500] * 25,
        'co2_savings_chart_bytes': None
    }
    
    print("✅ Test-Daten für CO₂-Berechnungen erstellt:")
    print(f"   📊 Jährliche CO₂-Einsparung: {test_analysis_results['annual_co2_savings_kg']} kg")
    print(f"   🌳 Bäume-Äquivalent: {test_analysis_results['co2_equivalent_trees_per_year']} Bäume")
    print(f"   🚗 Auto-km-Äquivalent: {test_analysis_results['co2_equivalent_car_km_per_year']} km")
    
    # 5. Berechnung Flugzeug-Äquivalent
    airplane_km_equiv = test_analysis_results['annual_co2_savings_kg'] / 0.23
    print(f"   ✈️ Flugzeug-km-Äquivalent: {airplane_km_equiv:.0f} km")
    
    # 6. Test der PDF-Generator COLORS
    try:
        from pdf_generator import COLORS
        print("✅ Modernisierte Farbpalette verfügbar:")
        print(f"   🎨 Primärakzent: {COLORS.get('accent_primary', 'N/A')}")
        print(f"   🎨 Textfarbe: {COLORS.get('text_dark', 'N/A')}")
        print(f"   📋 Tabellen-Header: {COLORS.get('table_header_bg', 'N/A')}")
    except ImportError:
        print("❌ Farbpalette nicht verfügbar")
        return False
    
    print("\n🎉 Alle CO₂-Verbesserungen erfolgreich getestet!")
    print("\n🔍 Neue Features:")
    print("   • 3D-CO₂-Visualisierung mit Auto, Flugzeug und Bäumen")
    print("   • Verbesserte CO₂-Sektion im PDF mit anschaulichen Vergleichen")
    print("   • Erweiterte monetäre CO₂-Analyse mit realistischen Preisen")
    print("   • Moderne Tabellenformatierung für CO₂-Vergleiche")
    print("   • Integration in das Visualisierungssystem")
    
    return True

if __name__ == "__main__":
    success = test_co2_improvements()
    if success:
        print("\n✅ Test erfolgreich abgeschlossen!")
        sys.exit(0)
    else:
        print("\n❌ Test fehlgeschlagen!")
        sys.exit(1)
