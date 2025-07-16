#!/usr/bin/env python3
"""Test für render_technical_calculations und den KeyError 'energy_loss_kwh'"""

import sys
import os

# Mock für Streamlit
class MockStreamlit:
    def __init__(self):
        self.session_state = {}
    
    def subheader(self, text):
        print(f"SUBHEADER: {text}")
    
    def expander(self, text, expanded=True):
        print(f"EXPANDER: {text} (expanded={expanded})")
        return MockContext()
    
    def columns(self, n):
        return [MockContext() for _ in range(n)]
    
    def metric(self, label, value, delta=None):
        print(f"METRIC: {label} = {value} (delta: {delta})")

class MockContext:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def metric(self, label, value, delta=None):
        print(f"METRIC: {label} = {value} (delta: {delta})")

class MockPlotly:
    class graph_objects:
        class Figure:
            def __init__(self, data=None):
                self.data = data
            def update_layout(self, **kwargs):
                pass
        class Heatmap:
            def __init__(self, **kwargs):
                pass

# Mock imports
sys.modules['streamlit'] = MockStreamlit()
sys.modules['plotly'] = MockPlotly()
sys.modules['plotly.graph_objects'] = MockPlotly.graph_objects

# Jetzt die echten imports
try:
    from calculations import AdvancedCalculationsIntegrator
    print("✓ AdvancedCalculationsIntegrator erfolgreich importiert")
except ImportError as e:
    print(f"✗ Fehler beim Import: {e}")
    sys.exit(1)

def test_render_technical_calculations():
    """Test der render_technical_calculations Funktion"""
    print("\n=== TEST: render_technical_calculations ===")
    
    try:
        # Mock Streamlit setup
        import streamlit as st
        st = MockStreamlit()
        
        # Import der render_technical_calculations Funktion
        # Da wir sie nicht direkt importieren können, simulieren wir die Logik
        integrator = AdvancedCalculationsIntegrator()
        
        # Test-Daten
        project_data = {
            'expected_annual_production': 12000,
            'system_kwp': 8.5,
            'location': 'München'
        }
        
        calc_results = {
            'anlage_kwp': 8.5,
            'annual_pv_production_kwh': 12000,
            'total_investment_cost_netto': 25000
        }
        
        texts = {'de': 'Deutsch'}
        
        # Simuliere die kritische Stelle aus render_technical_calculations
        print("Teste den kritischen Code-Bereich...")
        shading_analysis = integrator.calculate_shading_analysis(project_data)
        print(f"✓ shading_analysis erfolgreich berechnet: {type(shading_analysis)}")
        
        # Teste die kritische Stelle, die den KeyError verursacht
        try:
            annual_shading_loss = shading_analysis['annual_shading_loss']
            energy_loss_kwh = shading_analysis['energy_loss_kwh']  # Hier tritt der KeyError auf
            worst_month = shading_analysis['worst_month']
            worst_month_loss = shading_analysis['worst_month_loss']
            
            print(f"✓ annual_shading_loss: {annual_shading_loss}")
            print(f"✓ energy_loss_kwh: {energy_loss_kwh}")
            print(f"✓ worst_month: {worst_month}")
            print(f"✓ worst_month_loss: {worst_month_loss}")
            
            # Simuliere die st.metric Aufrufe, die in der echten Funktion stehen
            st.metric(
                "Jahresverlust durch Verschattung",
                f"{annual_shading_loss:.1f}%",
                delta=f"-{energy_loss_kwh:.0f} kWh"
            )
            st.metric(
                "Kritischster Monat", 
                worst_month,
                delta=f"{worst_month_loss:.1f}% Verlust"
            )
            
            print("✓ Alle st.metric Aufrufe erfolgreich")
            return True
            
        except KeyError as e:
            print(f"✗ KeyError beim Zugriff auf shading_analysis: {e}")
            print(f"Verfügbare Keys: {list(shading_analysis.keys())}")
            return False
            
    except Exception as e:
        print(f"✗ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_render_technical_calculations()
    if success:
        print("\n🎉 Test erfolgreich!")
        sys.exit(0)
    else:
        print("\n❌ Test fehlgeschlagen!")
        sys.exit(1)
