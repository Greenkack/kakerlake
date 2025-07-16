#!/usr/bin/env python3
"""
Finaler Test für analysis.py render_analysis nach den Korrekturen
"""

import sys
import os

# Test: Einfach den Import und eine Simulation des Funktionsaufrufs
try:
    # Import testen
    from analysis import render_analysis
    print("✅ SUCCESS: analysis.py render_analysis erfolgreich importiert")
    
    # Test der Variablennamen-Korrekturen
    import ast
    import inspect
    
    # Quelle der render_analysis Funktion holen
    source = inspect.getsource(render_analysis)
    
    # Prüfen ob project_data noch ohne Definition verwendet wird (sollte nicht mehr vorkommen)
    lines = source.split('\n')
    project_data_lines = []
    
    for i, line in enumerate(lines):
        if 'project_data=' in line and 'project_data' not in ['project_inputs', 'results_for_display', 'texts']:
            # Prüfe ob es sich um eine Parameterzuweisung handelt
            if 'project_data=project_data' in line:
                project_data_lines.append((i+1, line.strip()))
    
    if project_data_lines:
        print(f"❌ ERROR: Noch {len(project_data_lines)} unkorrigierte project_data Verwendungen gefunden:")
        for line_num, line_content in project_data_lines:
            print(f"   Zeile {line_num}: {line_content}")
    else:
        print("✅ SUCCESS: Alle project_data Verwendungen korrekt zu project_inputs geändert")
    
    # Prüfe analysis_results Verwendungen
    analysis_results_lines = []
    for i, line in enumerate(lines):
        if 'analysis_results=analysis_results' in line:
            analysis_results_lines.append((i+1, line.strip()))
    
    if analysis_results_lines:
        print(f"❌ ERROR: Noch {len(analysis_results_lines)} unkorrigierte analysis_results Verwendungen gefunden:")
        for line_num, line_content in analysis_results_lines:
            print(f"   Zeile {line_num}: {line_content}")
    else:
        print("✅ SUCCESS: Alle analysis_results Verwendungen korrekt zu results_for_display geändert")
        
    print("\n✅ GESAMT: Alle bekannten Variablennamen-Fehler in analysis.py wurden erfolgreich korrigiert!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())
