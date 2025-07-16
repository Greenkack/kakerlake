#!/usr/bin/env python3
"""
Test für KeyError-Behebung in analysis.py
"""

def test_extended_calculations():
    """Test der erweiterten Berechnungen"""
    try:
        import analysis
        
        # Mock data erstellen
        project_data = {
            'energy_consumption_annual_kwh': 4000,
            'electricity_price_per_kwh': 0.32
        }
        
        analysis_results = {
            'anlage_kwp': 10,
            'annual_pv_production_kwh': 10000,
            'annual_self_supply_kwh': 3000,
            'total_investment_cost_netto': 20000
        }
        
        texts = {
            'test': 'Test'
        }
        
        # Session state simulieren
        import streamlit as st
        if 'extended_calculator' in st.session_state:
            del st.session_state['extended_calculator']
        
        # Teste MockExtendedCalculations
        analysis.render_extended_calculations_dashboard(project_data, analysis_results, texts)
        
        print("✓ render_extended_calculations_dashboard erfolgreich")
        return True
        
    except Exception as e:
        print(f"✗ Fehler in extended calculations: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Test für KeyError-Behebung ===")
    test_extended_calculations()
