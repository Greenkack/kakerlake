#!/usr/bin/env python3
"""Test für den KeyError bei shading_analysis"""

import sys
import os

# Sicherstellen, dass alle imports funktionieren
try:
    from calculations import AdvancedCalculationsIntegrator
    print("✓ AdvancedCalculationsIntegrator erfolgreich importiert")
except ImportError as e:
    print(f"✗ Fehler beim Import von AdvancedCalculationsIntegrator: {e}")
    sys.exit(1)

def test_shading_analysis():
    """Test der calculate_shading_analysis Methode"""
    print("\n=== TEST: calculate_shading_analysis ===")
    
    try:
        integrator = AdvancedCalculationsIntegrator()
        print("✓ AdvancedCalculationsIntegrator erfolgreich initialisiert")
        
        # Test-Daten
        project_data = {
            'expected_annual_production': 12000,
            'system_kwp': 8.5,
            'location': 'München'
        }
        
        # Methode aufrufen
        result = integrator.calculate_shading_analysis(project_data)
        print("✓ calculate_shading_analysis erfolgreich aufgerufen")
        
        # Rückgabe-Wert prüfen
        print(f"Rückgabe-Typ: {type(result)}")
        print(f"Keys in der Rückgabe: {list(result.keys())}")
        
        # Spezifische Keys prüfen, die in analysis.py verwendet werden
        required_keys = [
            'annual_shading_loss',
            'energy_loss_kwh',  # Dieser Key verursacht den KeyError
            'worst_month',
            'worst_month_loss',
            'shading_matrix'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key in result:
                print(f"✓ Key '{key}' vorhanden: {result[key]}")
            else:
                print(f"✗ Key '{key}' FEHLT!")
                missing_keys.append(key)
        
        if missing_keys:
            print(f"\n✗ FEHLER: Fehlende Keys: {missing_keys}")
            return False
        else:
            print("\n✓ Alle benötigten Keys sind vorhanden")
            return True
            
    except Exception as e:
        print(f"✗ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shading_analysis()
    if success:
        print("\n🎉 Test erfolgreich!")
        sys.exit(0)
    else:
        print("\n❌ Test fehlgeschlagen!")
        sys.exit(1)
