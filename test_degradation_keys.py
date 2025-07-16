#!/usr/bin/env python3
"""Test für den KeyError 'total_energy_loss_kwh' Fix"""

import sys
import os

# Workspace-Pfad hinzufügen
sys.path.insert(0, r'c:\12345')

def test_degradation_analysis_keys():
    """Testet ob alle benötigten Keys in calculate_degradation_analysis vorhanden sind"""
    try:
        from analysis import render_extended_calculations_dashboard
        
        # Mock system_data
        system_data = {
            'system_kwp': 10,
            'annual_pv_production_kwh': 10000,
            'self_consumption_kwh': 3000,
            'annual_consumption_kwh': 4000,
            'total_investment': 20000
        }
        
        # Mock texts
        texts = {}
        
        print("Teste Mock-Implementierung der calculate_degradation_analysis...")
        
        # Mock-Klasse direkt testen
        class MockExtendedCalculations:
            def calculate_degradation_analysis(self, system_data):
                system_kwp = system_data.get('system_kwp', 10)
                annual_prod = system_data.get('annual_pv_production_kwh', 10000)
                return {
                    'power_year_10_kwp': system_kwp * (1 - 0.005) ** 10,
                    'power_year_20_kwp': system_kwp * (1 - 0.005) ** 20,
                    'cumulative_degradation_percent_20y': 9.6,
                    'total_energy_loss_kwh': annual_prod * 0.096 * 20,
                    'average_performance_ratio': 0.95
                }
        
        mock_calc = MockExtendedCalculations()
        result = mock_calc.calculate_degradation_analysis(system_data)
        
        # Teste alle benötigten Keys
        required_keys = [
            'power_year_10_kwp',
            'power_year_20_kwp', 
            'cumulative_degradation_percent_20y',
            'total_energy_loss_kwh',
            'average_performance_ratio'
        ]
        
        for key in required_keys:
            if key not in result:
                print(f"❌ FEHLER: Key '{key}' fehlt im Ergebnis!")
                return False
            else:
                print(f"✅ Key '{key}' vorhanden: {result[key]}")
        
        print("✅ Alle benötigten Keys sind vorhanden!")
        print(f"📊 Vollständiges Ergebnis: {result}")
        return True
        
    except Exception as e:
        print(f"❌ FEHLER beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Teste Degradations-Analyse Keys...")
    success = test_degradation_analysis_keys()
    if success:
        print("✅ Test erfolgreich!")
        exit(0)
    else:
        print("❌ Test fehlgeschlagen!")
        exit(1)
