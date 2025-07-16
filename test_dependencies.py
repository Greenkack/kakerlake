#!/usr/bin/env python3
"""
Test der analysis.py Abhängigkeiten
"""

print("=== Test der Analysis Dependencies ===")

import analysis

print(f"_CALCULATIONS_PERFORM_CALCULATIONS_AVAILABLE: {analysis._CALCULATIONS_PERFORM_CALCULATIONS_AVAILABLE}")
print(f"_DATABASE_LOAD_ADMIN_SETTING_AVAILABLE: {analysis._DATABASE_LOAD_ADMIN_SETTING_AVAILABLE}")
print(f"_ANALYSIS_DEPENDENCIES_AVAILABLE: {analysis._ANALYSIS_DEPENDENCIES_AVAILABLE}")

# Test der Funktionen
texts = {"dashboard_header": "Test Dashboard"}

try:
    # Test perform_calculations
    result = analysis.perform_calculations({})
    print(f"✓ perform_calculations verfügbar: {type(result)}")
except Exception as e:
    print(f"✗ perform_calculations Fehler: {e}")

try:
    # Test load_admin_setting
    setting = analysis.load_admin_setting('global_constants')
    print(f"✓ load_admin_setting verfügbar: {type(setting)}")
except Exception as e:
    print(f"✗ load_admin_setting Fehler: {e}")

print("=== Test abgeschlossen ===")
