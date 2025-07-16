#!/usr/bin/env python3
"""Test für die behobenen AttributeError und KeyError Probleme"""

import sys

def test_recycling_potential():
    """Test der calculate_recycling_potential Methode"""
    print("=== TEST: calculate_recycling_potential ===")
    
    try:
        from calculations import AdvancedCalculationsIntegrator
        
        integrator = AdvancedCalculationsIntegrator()
        
        # Test-Daten
        calc_results = {'anlage_kwp': 8.5}
        project_data = {'location': 'München'}
        
        # Methode aufrufen
        result = integrator.calculate_recycling_potential(calc_results, project_data)
        print("✓ calculate_recycling_potential erfolgreich aufgerufen")
        
        # Keys prüfen
        expected_keys = [
            'material_composition', 'recycling_rate', 'material_value',
            'co2_savings_recycling', 'end_of_life_cost', 'recycling_revenue'
        ]
        
        missing_keys = []
        for key in expected_keys:
            if key in result:
                print(f"✓ Key '{key}' vorhanden")
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

def test_optimization_suggestions():
    """Test der generate_optimization_suggestions Methode"""
    print("\n=== TEST: generate_optimization_suggestions ===")
    
    try:
        from calculations import AdvancedCalculationsIntegrator
        
        integrator = AdvancedCalculationsIntegrator()
        
        # Test-Daten
        calc_results = {'anlage_kwp': 8.5, 'total_investment_netto': 20000}
        project_data = {'location': 'München'}
        
        # Methode aufrufen
        result = integrator.generate_optimization_suggestions(calc_results, project_data)
        print("✓ generate_optimization_suggestions erfolgreich aufgerufen")
        
        # top_recommendations prüfen
        if 'top_recommendations' in result:
            top_recs = result['top_recommendations']
            print(f"✓ top_recommendations vorhanden: {len(top_recs)} Empfehlungen")
            
            # Keys in der ersten Empfehlung prüfen
            if top_recs:
                first_rec = top_recs[0]
                expected_keys = ['title', 'description', 'annual_benefit', 'investment', 'payback', 'roi_improvement']
                
                missing_keys = []
                for key in expected_keys:
                    if key in first_rec:
                        print(f"✓ Key '{key}' in top_recommendations vorhanden: {first_rec[key]}")
                    else:
                        print(f"✗ Key '{key}' FEHLT in top_recommendations!")
                        missing_keys.append(key)
                
                if missing_keys:
                    print(f"\n✗ FEHLER: Fehlende Keys in top_recommendations: {missing_keys}")
                    return False
                else:
                    print("\n✓ Alle benötigten Keys in top_recommendations sind vorhanden")
                    return True
            else:
                print("✗ FEHLER: top_recommendations ist leer")
                return False
        else:
            print("✗ FEHLER: top_recommendations Key fehlt")
            return False
            
    except Exception as e:
        print(f"✗ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_syntax():
    """Syntax-Check für calculations.py"""
    print("\n=== SYNTAX-CHECK ===")
    try:
        import py_compile
        py_compile.compile('c:/12345/calculations.py', doraise=True)
        print("✓ calculations.py hat keine Syntaxfehler")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ Syntaxfehler in calculations.py: {e}")
        return False

if __name__ == "__main__":
    success = all([
        test_syntax(),
        test_recycling_potential(),
        test_optimization_suggestions()
    ])
    
    if success:
        print("\n🎉 Alle Tests erfolgreich!")
        print("AttributeError und KeyError sollten jetzt behoben sein.")
        sys.exit(0)
    else:
        print("\n❌ Ein oder mehrere Tests fehlgeschlagen!")
        sys.exit(1)
