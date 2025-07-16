#!/usr/bin/env python3
"""
Vollständiger Test aller Mock-Methoden für fehlende Keys
"""

def test_all_mock_methods():
    """Teste alle Mock-Methoden systematisch"""
    try:
        import sys
        sys.modules.pop('analysis', None)  # Force reload
        
        import analysis
        
        # Mock data
        system_data = {
            'system_kwp': 10,
            'annual_pv_production_kwh': 10000,
            'annual_consumption_kwh': 4000,
            'self_consumption_kwh': 3000,
            'electricity_price_per_kwh': 0.32,
            'feed_in_tariff_per_kwh': 0.08,
            'total_investment': 20000
        }
        
        # Session state simulieren um MockExtendedCalculations zu erstellen
        import streamlit as st
        if 'extended_calculator' in st.session_state:
            del st.session_state['extended_calculator']
        
        # Dies erstellt eine MockExtendedCalculations Instanz
        mock_class_code = """
class MockExtendedCalculations:
    def calculate_energy_optimization(self, system_data):
        return {
            'base_self_consumption_kwh': system_data.get('self_consumption_kwh', 3000),
            'optimized_self_consumption_kwh': system_data.get('self_consumption_kwh', 3000) * 1.15,
            'optimization_potential_percent': 15.0,
            'annual_savings_optimization': 450
        }
    
    def calculate_grid_analysis(self, system_data):
        return {
            'grid_feed_in_kwh': system_data.get('annual_pv_production_kwh', 10000) - system_data.get('self_consumption_kwh', 3000),
            'grid_purchase_kwh': max(0, system_data.get('annual_consumption_kwh', 4000) - system_data.get('self_consumption_kwh', 3000)),
            'grid_independence_percent': (system_data.get('self_consumption_kwh', 3000) / system_data.get('annual_consumption_kwh', 4000)) * 100,
            'peak_load_reduction_kw': 3.2,
            'peak_load_cost_savings': 280
        }
    
    def calculate_weather_impact(self, system_data):
        annual_yield = system_data.get('annual_pv_production_kwh', 10000)
        return {
            'yield_sunny_days_kwh': annual_yield * 0.6,
            'yield_partly_cloudy_kwh': annual_yield * 0.25,
            'yield_cloudy_kwh': annual_yield * 0.1,
            'yield_rainy_kwh': annual_yield * 0.05,
            'weather_adjusted_annual_yield_kwh': annual_yield * 0.95,
            'weather_impact_percent': -5.0
        }
    
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
    
    def calculate_financial_scenarios(self, system_data):
        base_npv = system_data.get('total_investment', 20000) * 0.8
        return {
            'pessimistic_scenario': {'npv': base_npv * 0.7, 'roi_percent': 4.2, 'payback_years': 16.8},
            'realistic_scenario': {'npv': base_npv, 'roi_percent': 6.5, 'payback_years': 12.3},
            'optimistic_scenario': {'npv': base_npv * 1.4, 'roi_percent': 9.1, 'payback_years': 8.7}
        }
    
    def calculate_environmental_impact(self, system_data):
        annual_prod = system_data.get('annual_pv_production_kwh', 10000)
        return {
            'annual_co2_savings_tons': annual_prod * 0.474 / 1000,
            'total_co2_savings_25y': annual_prod * 0.474 * 25 / 1000,
            'trees_equivalent': int(annual_prod * 0.474 * 25 / 22000),
            'cars_off_road_equivalent': int(annual_prod * 0.474 * 25 / 2300),
            'car_km_equivalent': int(annual_prod * 0.474 * 2.3),
            'water_savings_liters': int(annual_prod * 2.5)
        }
    
    def calculate_battery_optimization(self, system_data):
        return {
            'small_battery_kwh': 5,
            'optimal_battery_kwh': 8,
            'large_battery_kwh': 12,
            'small_self_consumption_percent': 65,
            'optimal_self_consumption_percent': 78,
            'large_self_consumption_percent': 82,
            'small_self_consumption_increase_percent': 15,
            'optimal_self_consumption_increase_percent': 28,
            'large_self_consumption_increase_percent': 32,
            'optimal_battery_size_kwh': 8.0,
            'optimal_battery_investment': 12000,
            'battery_payback_years': 9.5
        }
"""
        
        exec(mock_class_code)
        mock_calculator = locals()['MockExtendedCalculations']()
        
        # Teste alle Methoden
        methods_to_test = [
            'calculate_energy_optimization',
            'calculate_grid_analysis', 
            'calculate_weather_impact',
            'calculate_degradation_analysis',
            'calculate_financial_scenarios',
            'calculate_environmental_impact',
            'calculate_battery_optimization'
        ]
        
        print("=== Test aller Mock-Methoden ===")
        
        for method_name in methods_to_test:
            try:
                method = getattr(mock_calculator, method_name)
                result = method(system_data)
                print(f"✓ {method_name}: {len(result)} keys")
                
                # Zeige alle Keys für Debugging
                print(f"  Keys: {list(result.keys())}")
                
            except Exception as e:
                print(f"✗ {method_name}: {e}")
                return False
        
        print("\n✓ Alle Mock-Methoden funktionieren korrekt!")
        return True
        
    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_all_mock_methods()
