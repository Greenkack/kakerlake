#!/usr/bin/env python3
"""
Test für den spezifischen AttributeError in analysis.py
"""

import sys
import os

# Mock streamlit und session_state
class MockSessionState:
    def __init__(self):
        self.data = {
            "calculations_integrator": MockIntegrator(),
            "project_data": {
                "pv_modules": 20,
                "module_power": 400,
                "roof_area": 100,
                "location": "Berlin"
            },
            "calculation_results": {
                "total_power": 8000,
                "annual_production": 7000,
                "investment_cost": 15000
            }
        }
    
    def get(self, key, default=None):
        return self.data.get(key, default)

class MockIntegrator:
    """Mock AdvancedCalculationsIntegrator ohne die fehlenden Methoden"""
    
    def calculate_energy_optimization(self, system_data):
        return {"optimization_potential": 15}
    
    def calculate_grid_analysis(self, system_data):
        return {"grid_relief": 0.4}
    
    def calculate_weather_impact(self, system_data):
        return {"weather_impact": 5}
    
    def calculate_degradation_analysis(self, system_data):
        return {"annual_degradation": 0.5}
    
    def calculate_financial_scenarios(self, system_data):
        return {"scenarios": {}}
    
    def calculate_environmental_impact(self, system_data):
        return {"co2_savings": 4.3}
    
    def calculate_battery_optimization(self, system_data):
        return {"optimal_size": 10}

# Mock streamlit
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
    
    def error(self, msg):
        print(f"ST_ERROR: {msg}")
    
    def warning(self, msg):
        print(f"ST_WARNING: {msg}")
    
    def header(self, text):
        print(f"ST_HEADER: {text}")
    
    def subheader(self, text):
        print(f"ST_SUBHEADER: {text}")
    
    def expander(self, title, expanded=False):
        return MockExpander()
    
    def columns(self, n):
        return [MockColumn() for _ in range(n)]
    
    def write(self, content):
        print(f"ST_WRITE: {content}")
    
    def metric(self, label, value, help=None):
        print(f"ST_METRIC: {label} = {value}")

class MockExpander:
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

class MockColumn:
    def metric(self, label, value, help=None):
        print(f"ST_COLUMN_METRIC: {label} = {value}")

# Mock streamlit globaly
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

try:
    from analysis import render_technical_calculations, render_financial_scenarios, render_environmental_calculations, render_optimization_suggestions
    
    print("SUCCESS: analysis.py render-Funktionen erfolgreich importiert")
    
    # Test mit MockIntegrator
    integrator = MockIntegrator()
    test_results = {
        "annual_pv_production_kwh": 8000,
        "system_kwp": 10
    }
    test_project_data = {
        "roof_area": 100,
        "orientation": "south"
    }
    test_texts = {
        "technical_calculations": "Technische Berechnungen",
        "financial_scenarios": "Finanzszenarien"
    }
    
    print("\nTESTE: render_technical_calculations...")
    try:
        render_technical_calculations(integrator, test_results, test_project_data, test_texts)
        print("SUCCESS: render_technical_calculations erfolgreich (oder graceful failure)")
    except AttributeError as e:
        print(f"EXPECTED_ERROR: {e} (Das ist der erwartete AttributeError)")
    except Exception as e:
        print(f"OTHER_ERROR: {e}")
    
    print("\nTESTE: render_financial_scenarios...")
    try:
        render_financial_scenarios(integrator, test_results, test_project_data, test_texts)
        print("SUCCESS: render_financial_scenarios erfolgreich (oder graceful failure)")
    except AttributeError as e:
        print(f"EXPECTED_ERROR: {e}")
    except Exception as e:
        print(f"OTHER_ERROR: {e}")
    
    print("\nAlle Tests abgeschlossen. Mit Try-Catch-Blöcken sollten die AttributeErrors abgefangen werden.")
    
except Exception as e:
    print(f"IMPORT_ERROR: {e}")
    import traceback
    print(traceback.format_exc())
