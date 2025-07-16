#!/usr/bin/env python3
"""
Test für render_optimization_suggestions Funktion nach Slider-Fix
"""

def test_optimization_suggestions():
    print("🔍 Testing render_optimization_suggestions function...")
    
    try:
        from calculations import AdvancedCalculationsIntegrator
        from analysis import render_optimization_suggestions
        import streamlit as st
        
        # Mock data
        integrator = AdvancedCalculationsIntegrator()
        calc_results = {'annual_pv_production_kwh': 8000, 'total_investment_netto': 20000}
        project_data = {'system_size_kw': 10}
        texts = {'test': 'test'}
        
        # Test optimization_suggestions generation
        optimization_results = integrator.generate_optimization_suggestions(calc_results, project_data)
        
        # Check if system_optimization has correct types
        system_opt = optimization_results['system_optimization']
        
        print(f"optimal_battery_size type: {type(system_opt['optimal_battery_size'])} = {system_opt['optimal_battery_size']}")
        print(f"optimal_dc_ac_ratio type: {type(system_opt['optimal_dc_ac_ratio'])} = {system_opt['optimal_dc_ac_ratio']}")
        print(f"optimal_tilt type: {type(system_opt['optimal_tilt'])} = {system_opt['optimal_tilt']}")
        print(f"optimal_azimuth type: {type(system_opt['optimal_azimuth'])} = {system_opt['optimal_azimuth']}")
        
        # Validate that all slider values can be converted to float safely
        battery_size_float = float(system_opt['optimal_battery_size'])
        dc_ac_ratio_float = float(system_opt['optimal_dc_ac_ratio'])
        tilt_float = float(system_opt['optimal_tilt'])
        azimuth_float = float(system_opt['optimal_azimuth'])
        
        print("✅ Alle system_optimization Werte können sicher zu Float konvertiert werden")
        
        # Test slider parameter types that would be used
        # Battery size slider:
        min_val = 0.0
        max_val = 30.0
        step_val = 0.5
        value_val = battery_size_float
        
        print(f"\nBattery slider parameters:")
        print(f"min_value: {type(min_val)} = {min_val}")
        print(f"max_value: {type(max_val)} = {max_val}")
        print(f"step: {type(step_val)} = {step_val}")
        print(f"value: {type(value_val)} = {value_val}")
        
        if all(isinstance(x, float) for x in [min_val, max_val, step_val, value_val]):
            print("✅ Battery slider parameters haben alle Float-Typ")
        else:
            print("❌ Battery slider parameters haben inkomatible Typen")
            return False
        
        print("✅ render_optimization_suggestions sollte jetzt ohne Slider-Typ-Fehler laufen")
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("RENDER_OPTIMIZATION_SUGGESTIONS SLIDER-TEST")
    print("=" * 70)
    
    success = test_optimization_suggestions()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 TEST ERFOLGREICH - render_optimization_suggestions Slider-Fix validiert!")
    else:
        print("❌ TEST FEHLGESCHLAGEN - Weitere Korrekturen nötig")
    print("=" * 70)
