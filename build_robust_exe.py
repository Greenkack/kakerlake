#!/usr/bin/env python3
"""
Robuster Build für die Streamlit-App mit verbesserter Fehlerbehandlung
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("=== Robuster Build für OmersSolarDingelDangel ===")
    
    # Arbeitsverzeichnis
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    launcher_file = src_dir / "robust_launcher.py"
    
    # Prüfen ob Launcher existiert
    if not launcher_file.exists():
        print(f"FEHLER: {launcher_file} nicht gefunden!")
        return 1
      # Alte Builds aufräumen (mit Fehlerbehandlung)
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    for dir_path in [dist_dir, build_dir]:
        if dir_path.exists():
            print(f"Aufräumen: {dir_path}")
            try:
                shutil.rmtree(dir_path)
            except PermissionError:
                print(f"Warnung: Konnte {dir_path} nicht löschen (Datei in Verwendung)")
                # Versuche nur Inhalte zu löschen
                try:
                    for item in dir_path.iterdir():
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                except Exception as e:
                    print(f"Warnung: Teilweises Aufräumen fehlgeschlagen: {e}")
            except Exception as e:
                print(f"Warnung: Aufräumen fehlgeschlagen: {e}")
    
    # PyInstaller-Kommando
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "OmersSolarDingelDangel_Robust",
        "--icon", "Omer.ico",
        
        # Alle wichtigen Module explizit einschließen
        "--hidden-import", "streamlit",
        "--hidden-import", "streamlit.cli",
        "--hidden-import", "streamlit.web.cli",
        "--hidden-import", "streamlit.runtime",
        "--hidden-import", "streamlit.runtime.scriptrunner",
        "--hidden-import", "streamlit.runtime.state",
        "--hidden-import", "streamlit.components.v1",
        "--hidden-import", "altair",
        "--hidden-import", "plotly",
        "--hidden-import", "pandas",
        "--hidden-import", "numpy",
        "--hidden-import", "sqlite3",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "reportlab",
        "--hidden-import", "reportlab.pdfgen",
        "--hidden-import", "reportlab.lib",
        "--hidden-import", "requests",
        "--hidden-import", "json",
        "--hidden-import", "csv",
        "--hidden-import", "io",
        "--hidden-import", "base64",
        
        # Streamlit-Daten sammeln
        "--collect-data", "streamlit",
        "--collect-submodules", "streamlit",
        
        # Andere wichtige Daten
        "--collect-data", "altair",
        "--collect-data", "plotly",
        
        # Problematische Module ausschließen, um Konflikte zu vermeiden
        "--exclude-module", "google.protobuf",
        "--exclude-module", "grpcio",
        "--exclude-module", "tensorflow",
        "--exclude-module", "torch",
        "--exclude-module", "torchvision",
        
        # Alle wichtigen Dateien einschließen
        "--add-data", f"{src_dir / 'omerssolar' / 'gui.py'};omerssolar",
        "--add-data", f"{src_dir / 'omerssolar' / 'database.py'};omerssolar",
        "--add-data", f"{src_dir / 'omerssolar' / 'calculations.py'};omerssolar",
        "--add-data", f"{src_dir / 'omerssolar' / 'pdf_generator.py'};omerssolar",
        "--add-data", f"{src_dir / 'omerssolar' / 'utils.py'};omerssolar",
        
        # Datenverzeichnis
        "--add-data", f"{project_root / 'data'};data",
        
        # Lokalisierung
        "--add-data", f"{project_root / 'de.json'};.",
        
        # Runtime-Hook für zusätzliche Konfiguration
        "--runtime-hook", str(project_root / "runtime-hook.py"),
        
        # Launcher als Hauptdatei
        str(launcher_file)
    ]
    
    print("Starte PyInstaller...")
    print(f"Kommando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, cwd=project_root)
        print("✅ Build erfolgreich!")
        
        # EXE-Datei prüfen
        exe_file = dist_dir / "OmersSolarDingelDangel_Robust.exe"
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
