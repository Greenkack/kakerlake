#!/usr/bin/env python3
"""
Finaler Test für das ursprüngliche KeyError-Problem
"""

def test_original_keyerror():
    """Teste das ursprüngliche KeyError-Problem"""
    try:
        import analysis
        
        # Mock session state
        import streamlit as st
        
        # Erstelle Mock-Daten wie sie von gui.py kommen würden
        texts = {'test': 'Test'}
        calculation_results = {
            'anlage_kwp': 10.5,
            'annual_pv_production_kwh': 10500,
            'annual_self_supply_kwh': 3200,
            'total_investment_cost_netto': 21000,
            'simulation_period_years_effective': 20
        }
        
        # Simuliere den Aufruf, der das KeyError verursacht hat
        project_data = {
            'energy_consumption_annual_kwh': 4200,
            'electricity_price_per_kwh': 0.33
        }
        
        # Test der erweiterten Berechnungen, die das KeyError verursacht haben
        print("Testing render_extended_calculations_dashboard...")
        
        # Clear session state to force re-creation of calculator
        if hasattr(st, 'session_state') and 'extended_calculator' in st.session_state:
            del st.session_state['extended_calculator']
        
        analysis.render_extended_calculations_dashboard(
            project_data, calculation_results, texts
        )
        
        print("✓ render_extended_calculations_dashboard läuft ohne KeyError!")
        
        # Teste auch die spezifische Funktion, die das Problem hatte
        if hasattr(st, 'session_state') and 'extended_calculator' in st.session_state:
            calculator = st.session_state['extended_calculator']
            
            system_data = {
                'system_kwp': calculation_results.get('anlage_kwp', 10),
                'annual_pv_production_kwh': calculation_results.get('annual_pv_production_kwh', 10000),
                'annual_consumption_kwh': project_data.get('energy_consumption_annual_kwh', 4000),
                'self_consumption_kwh': calculation_results.get('annual_self_supply_kwh', 3000),
                'electricity_price_per_kwh': project_data.get('electricity_price_per_kwh', 0.32),
                'feed_in_tariff_per_kwh': 0.08,
                'total_investment': calculation_results.get('total_investment_cost_netto', 20000)
            }
            
            battery_results = calculator.calculate_battery_optimization(system_data)
            
            # Teste alle Keys, die das ursprüngliche Problem verursacht haben
            critical_keys = [
                'optimal_battery_size_kwh',
                'optimal_battery_investment', 
                'battery_payback_years'
            ]
            
            print("Teste kritische Keys:")
            for key in critical_keys:
                if key in battery_results:
                    print(f"✓ {key}: {battery_results[key]}")
                else:
                    print(f"✗ {key}: FEHLT!")
                    return False
        
        print("✓ Alle kritischen Keys sind vorhanden!")
        return True
        
    except KeyError as e:
        print(f"✗ KeyError immer noch vorhanden: {e}")
        return False
    except Exception as e:
        print(f"✗ Anderer Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Finaler Test für KeyError-Behebung ===")
    success = test_original_keyerror()
    print(f"\n=== Ergebnis: {'✓ PROBLEM BEHOBEN' if success else '✗ PROBLEM BESTEHT NOCH'} ===")
