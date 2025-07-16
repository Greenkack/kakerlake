#!/usr/bin/env python3
"""
Debug-Build für OmersSolarDingelDangel
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=== Debug-Build für OmersSolarDingelDangel ===")
    
    # Arbeitsverzeichnis
    project_root = Path(__file__).parent.absolute()
    src_dir = project_root / "src"
    debug_launcher = src_dir / "ultra_debug_launcher.py"
    
    # Prüfen ob Launcher existiert
    if not debug_launcher.exists():
        print(f"FEHLER: {debug_launcher} nicht gefunden!")
        return 1
    
    # PyInstaller-Kommando
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        # Wichtig: Console muss aktiviert sein für Debug-Ausgaben
        "--console",
        "--name=OmersSolarDingelDangel_Debug",
        "--icon=Omer.ico",
        # Debug-Optionen
        "--debug=all",
        "--log-level=DEBUG",
        # Wichtige Hidden Imports
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.cli",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=pandas",
        "--hidden-import=plotly",
        "--hidden-import=sqlite3",
        "--hidden-import=PIL",
        # Dateien und Daten
        "--add-data", f"{project_root/\"data\"};data",
        "--add-data", f"{project_root/\"de.json\"};.",
        # Konfliktmodule ausschließen
        "--exclude-module=tensorflow",
        "--exclude-module=torch",
        "--exclude-module=google.protobuf",
        # Debug-Launcher
        str(debug_launcher)
    ]
    
    print("Starte Debug-Build...")
    print(f"Kommando: {\" \".join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print("✅ Build erfolgreich!")
        
        # EXE-Datei prüfen
        exe_file = project_root / "dist" / "OmersSolarDingelDangel_Debug.exe"
        if exe_file.exists():
            print(f"✅ EXE erstellt: {exe_file}")
            print(f"   Größe: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
            return 0
        else:
            print("❌ EXE-Datei wurde nicht erstellt!")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller-Fehler: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
