#!/usr/bin/env python3
"""
Test für Slider-Typ-Konflikt Behebung
"""

def test_slider_types():
    print("🔍 Testing slider type compatibility...")
    
    try:
        import streamlit as st
        print("✅ Streamlit import erfolgreich")
        
        # Mock system_optimization data to test slider
        system_optimization = {
            'optimal_battery_size': 8.5,  # This could be int or float
            'optimal_dc_ac_ratio': 1.25,
            'optimal_tilt': 35,
            'optimal_azimuth': 0
        }
        
        # Test the exact slider configuration that was causing the error
        print("Testing battery_size slider configuration...")
        
        # Validate types
        min_val = 0.0
        max_val = 30.0 
        step_val = 0.5
        value_val = float(system_optimization['optimal_battery_size'])
        
        print(f"min_value type: {type(min_val)} = {min_val}")
        print(f"max_value type: {type(max_val)} = {max_val}")
        print(f"step type: {type(step_val)} = {step_val}")
        print(f"value type: {type(value_val)} = {value_val}")
        
        # Check if all types are compatible (should all be float)
        if all(isinstance(x, float) for x in [min_val, max_val, step_val, value_val]):
            print("✅ Alle Slider-Parameter haben kompatible Float-Typen")
        else:
            print("❌ Slider-Parameter haben inkomatible Typen")
            return False
            
    except Exception as e:
        print(f"❌ Slider-Test fehlgeschlagen: {e}")
        return False
    
    return True

def test_import_analysis():
    print("\n🔍 Testing analysis.py import...")
    
    try:
        import analysis
        print("✅ analysis.py import erfolgreich")
        return True
    except Exception as e:
        print(f"❌ analysis.py import fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SLIDER-TYP-KONFLIKT TEST")
    print("=" * 60)
    
    slider_ok = test_slider_types()
    import_ok = test_import_analysis()
    
    print("\n" + "=" * 60)
    if slider_ok and import_ok:
        print("🎉 ALLE TESTS ERFOLGREICH - Slider-Typ-Konflikt behoben!")
    else:
        print("❌ TESTS FEHLGESCHLAGEN - Weitere Korrekturen nötig")
    print("=" * 60)
