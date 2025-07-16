#!/usr/bin/env python3
"""
Test der render_analysis Funktion mit korrekten Dependencies
"""

print("=== Test render_analysis ===")

# Mock Streamlit für Test
class MockSt:
    def __init__(self):
        self.session_state = {}
    def error(self, msg): print(f"ST-ERROR: {msg}")
    def warning(self, msg): print(f"ST-WARNING: {msg}")
    def info(self, msg): print(f"ST-INFO: {msg}")
    def header(self, msg): print(f"ST-HEADER: {msg}")
    def success(self, msg): print(f"ST-SUCCESS: {msg}")

import sys
sys.modules['streamlit'] = MockSt()

import analysis

# Test ob Dependencies verfügbar sind
print(f"Dependencies verfügbar: {analysis._ANALYSIS_DEPENDENCIES_AVAILABLE}")

if analysis._ANALYSIS_DEPENDENCIES_AVAILABLE:
    print("✓ Dependencies sind verfügbar - kein kritischer Fehler erwartet")
else:
    print("✗ Dependencies nicht verfügbar - kritischer Fehler erwartet")

# Test render_analysis
texts = {"dashboard_header": "Test Dashboard"}

try:
    analysis.render_analysis(texts)
    print("✓ render_analysis ausgeführt ohne kritischen Fehler")
except Exception as e:
    print(f"✗ render_analysis Fehler: {e}")

print("=== Test abgeschlossen ===")
