#!/usr/bin/env python3
"""Test der LCOE-Korrektur"""
import sys
import traceback

try:
    from calculations import AdvancedCalculationsIntegrator
    print("✅ AdvancedCalculationsIntegrator importiert")
    
    integrator = AdvancedCalculationsIntegrator()
    print("✅ Integrator-Instanz erstellt")
    
    params = {
        'investment': 15000,
        'annual_production': 8000,
        'lifetime': 25,
        'discount_rate': 0.04
    }
    
    result = integrator.calculate_lcoe_advanced(params)
    print("✅ calculate_lcoe_advanced ausgeführt")
    
    required_keys = ['lcoe_simple', 'lcoe_discounted', 'grid_comparison', 'savings_potential']
    
    print("\n📊 LCOE-Test Ergebnisse:")
    print("-" * 40)
    
    all_ok = True
    for key in required_keys:
        if key in result:
            value = result[key]
            print(f"✅ {key}: {value:.4f}")
        else:
            print(f"❌ {key}: FEHLT")
            all_ok = False
    
    print("-" * 40)
    if all_ok:
        print("🎉 ALLE ERFORDERLICHEN LCOE-FELDER VERFÜGBAR!")
    else:
        print("⚠️ Einige Felder fehlen noch")
        
    print(f"\nAlle verfügbaren Keys: {list(result.keys())}")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    traceback.print_exc()
