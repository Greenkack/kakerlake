#!/usr/bin/env python3
"""
Test für Import und Syntax nach finaler Korrektur der Syntaxfehler
"""

def test_imports():
    print("🔍 Testing imports after syntax fixes...")
    
    try:
        import calculations
        print("✅ calculations.py import erfolgreich")
    except Exception as e:
        print(f"❌ calculations.py import fehlgeschlagen: {e}")
        return False
    
    try:
        import analysis
        print("✅ analysis.py import erfolgreich")
    except Exception as e:
        print(f"❌ analysis.py import fehlgeschlagen: {e}")
        return False
    
    return True

def test_calculations_methods():
    print("\n🔍 Testing calculations methods...")
    
    try:
        from calculations import AdvancedCalculationsIntegrator
        integrator = AdvancedCalculationsIntegrator()
        
        # Test generate_optimization_suggestions
        calc_results = {'annual_pv_production_kwh': 8000}
        project_data = {'system_size_kw': 10}
        
        result = integrator.generate_optimization_suggestions(calc_results, project_data)
        
        # Check if top_recommendations exist and have required keys
        if 'top_recommendations' in result:
            for rec in result['top_recommendations']:
                required_keys = ['title', 'description', 'annual_benefit', 'investment', 'payback', 'roi_improvement', 'difficulty']
                missing_keys = [key for key in required_keys if key not in rec]
                if missing_keys:
                    print(f"❌ Fehlende Keys in top_recommendations: {missing_keys}")
                    return False
            print("✅ generate_optimization_suggestions funktioniert korrekt")
        else:
            print("❌ 'top_recommendations' Key fehlt in result")
            return False
        
    except Exception as e:
        print(f"❌ calculations methods test fehlgeschlagen: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("FINALER SYNTAX- UND IMPORT-TEST")
    print("=" * 60)
    
    imports_ok = test_imports()
    methods_ok = test_calculations_methods() if imports_ok else False
    
    print("\n" + "=" * 60)
    if imports_ok and methods_ok:
        print("🎉 ALLE TESTS ERFOLGREICH - Syntaxfehler behoben!")
    else:
        print("❌ TESTS FEHLGESCHLAGEN - Weitere Korrekturen nötig")
    print("=" * 60)
