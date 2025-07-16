#!/usr/bin/env python3
"""
Test für shading_analysis KeyError-Behebung
"""

def test_shading_analysis():
    """Teste die shading_analysis Methode"""
    try:
        from calculations import AdvancedCalculationsIntegrator
        
        integrator = AdvancedCalculationsIntegrator()
        
        # Test data
        project_data = {
            'expected_annual_production': 10000,
            'pv_capacity_kwp': 10
        }
        
        # Teste shading_analysis
        shading_analysis = integrator.calculate_shading_analysis(project_data)
        
        # Teste alle Keys, die in analysis.py verwendet werden
        required_keys = [
            'shading_matrix',
            'annual_shading_loss', 
            'energy_loss_kwh',  # Das war der fehlende Key
            'worst_month',
            'worst_month_loss',
            'optimization_potential'
        ]
        
        print("=== Test shading_analysis Keys ===")
        missing_keys = []
        
        for key in required_keys:
            if key in shading_analysis:
                print(f"✓ {key}: {shading_analysis[key]}")
            else:
                print(f"✗ {key}: FEHLT!")
                missing_keys.append(key)
        
        if missing_keys:
            print(f"\n✗ Fehlende Keys: {missing_keys}")
            return False
        else:
            print(f"\n✓ Alle {len(required_keys)} Keys vorhanden!")
            return True
            
    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_shading_analysis()
