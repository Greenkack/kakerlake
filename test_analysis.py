#!/usr/bin/env python3
"""
Test für analysis.py render_analysis Funktion
"""

import sys
import os

# Session State Simulation für Test
class MockSessionState:
    def __init__(self):
        self.data = {
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
    
    def text_area(self, label, content, height=None):
        print(f"ST_TEXT_AREA: {label}")
    
    def write(self, content):
        print(f"ST_WRITE: {content}")

# Mock streamlit globaly
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

try:
    from analysis import render_analysis
    
    print("SUCCESS: analysis.py erfolgreich importiert")
    
    # Test der render_analysis Funktion
    test_texts = {
        "dashboard_header": "Test Dashboard",
        "analysis_module_critical_error": "Kritischer Fehler im Analysemodul"
    }
    
    test_results = {
        "total_power": 8000,
        "annual_production": 7000
    }
    
    print("TESTE: render_analysis Funktion...")
    render_analysis(test_texts, test_results)
    print("SUCCESS: render_analysis erfolgreich ausgeführt")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())
