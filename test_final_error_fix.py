#!/usr/bin/env python3
"""Finaler Test der AttributeError und KeyError Behebung"""

import sys

def test_final_fix():
    """Finaler Test aller Korrekturen"""
    print("=== FINALER TEST: AttributeError und KeyError Behebung ===")
    
    try:
        # Import-Test
        from calculations import AdvancedCalculationsIntegrator
        print("✓ AdvancedCalculationsIntegrator erfolgreich importiert")
        
        integrator = AdvancedCalculationsIntegrator()
        print("✓ Integrator erfolgreich erstellt")
        
        # Test calculate_recycling_potential (AttributeError war hier)
        calc_results = {'anlage_kwp': 8.5, 'total_investment_netto': 20000}
        project_data = {'location': 'München'}
        
        recycling_result = integrator.calculate_recycling_potential(calc_results, project_data)
        print("✓ calculate_recycling_potential funktioniert")
        print(f"  - Recycling-Rate: {recycling_result['recycling_rate']}%")
        print(f"  - Material-Wert: {recycling_result['material_value']} €")
        
        # Test generate_optimization_suggestions (KeyError 'annual_benefit' war hier)
        optimization_result = integrator.generate_optimization_suggestions(calc_results, project_data)
        print("✓ generate_optimization_suggestions funktioniert")
        
        if 'top_recommendations' in optimization_result:
            top_recs = optimization_result['top_recommendations']
            print(f"  - {len(top_recs)} Optimierungsempfehlungen gefunden")
            
            # Teste die kritischen Keys, die den KeyError verursacht haben
            first_rec = top_recs[0]
            annual_benefit = first_rec.get('annual_benefit', 'FEHLT')
            investment = first_rec.get('investment', 'FEHLT')
            payback = first_rec.get('payback', 'FEHLT')
            roi_improvement = first_rec.get('roi_improvement', 'FEHLT')
            
            print(f"  - annual_benefit: {annual_benefit}")
            print(f"  - investment: {investment}")
            print(f"  - payback: {payback}")
            print(f"  - roi_improvement: {roi_improvement}")
            
            # Prüfe, ob alle Keys vorhanden sind
            if all(val != 'FEHLT' for val in [annual_benefit, investment, payback, roi_improvement]):
                print("✓ Alle kritischen Keys sind vorhanden!")
                return True
            else:
                print("✗ Einige Keys fehlen noch!")
                return False
        else:
            print("✗ top_recommendations Key fehlt")
            return False
            
    except AttributeError as e:
        print(f"✗ AttributeError noch vorhanden: {e}")
        return False
    except KeyError as e:
        print(f"✗ KeyError noch vorhanden: {e}")
        return False
    except Exception as e:
        print(f"✗ Anderer Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_fix()
    
    if success:
        print("\n🎉 ERFOLG: Beide Fehler behoben!")
        print("   - AttributeError: 'AdvancedCalculationsIntegrator' object has no attribute 'calculate_recycling_potential' → BEHOBEN")
        print("   - KeyError: 'annual_benefit' → BEHOBEN")
        print("   Die Analyse sollte jetzt ohne diese Fehler funktionieren.")
        sys.exit(0)
    else:
        print("\n❌ FEHLER: Es gibt noch Probleme.")
        sys.exit(1)
