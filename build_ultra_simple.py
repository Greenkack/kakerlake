#!/usr/bin/env python3
"""
Vereinfachter Build für die Streamlit-App mit direktem PyInstaller-Aufruf
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=== Vereinfachter Build für OmersSolarDingelDangel ===")
      # Arbeitsverzeichnis
    project_root = Path(__file__).parent.absolute()
    src_dir = project_root / "src"
    launcher_file = src_dir / "browser_launcher.py"
    
    # Prüfen ob Launcher existiert
    if not launcher_file.exists():
        print(f"FEHLER: {launcher_file} nicht gefunden!")
        return 1
      # PyInstaller-Kommando
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--name=OmersSolarDingelDangel_Ultra",
        "--icon=Omer.ico",
        # Wichtige Module einbinden
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web",
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.scriptrunner",
        "--hidden-import=streamlit.runtime.state",
        "--hidden-import=streamlit.components.v1",
        "--hidden-import=altair",
        "--hidden-import=plotly",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=sqlite3",
        # Daten einbinden
        "--add-data", f"{src_dir/'omerssolar'};omerssolar",
        "--add-data", f"{project_root/'data'};data",
        "--add-data", f"{project_root/'de.json'};.",
        # Module ausschließen
        "--exclude-module=tensorflow",
        "--exclude-module=torch",
        "--exclude-module=google.protobuf",
        "--exclude-module=grpcio",
        # Extra Optimierungen
        "--noupx",  # UPX komprimierung deaktivieren für bessere Stabilität
        # Hauptdatei
        str(launcher_file)
    ]
    
    print("Starte vereinfachten PyInstaller-Build...")
    print(f"Kommando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print("✅ Build erfolgreich!")
        
        # EXE-Datei prüfen
        exe_file = project_root / "dist" / "OmersSolarDingelDangel_Ultra.exe"
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
