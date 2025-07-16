# build_exe.py
"""
Script zur automatischen .exe Erstellung für Ömers Solar Dingel Dangel
Mit Code-Signing und UPX Komprimierung
Verwendung: python build_exe.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🔨 Ömers Solar Dingel Dangel - EXE Builder")
    print("=" * 50)
    
    # Prüfe ob PyInstaller installiert ist
    try:
        import PyInstaller
        print(f"✅ PyInstaller gefunden: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller nicht gefunden!")
        print("Installiere mit: pip install pyinstaller")
        return
    
    # Aktuelles Verzeichnis
    base_path = Path(__file__).parent
      # PyInstaller Kommando
    cmd = [
        "pyinstaller",
        "--onefile",                    # Einzelne .exe Datei
        "--windowed",                   # Kein Konsolen-Fenster  
        "--name=OemersSolarDingelDangel", # Name der .exe
        "--icon=solar_icon.ico",       # Icon (falls vorhanden)
        
        # Zusätzliche Dateien einschließen
        "--add-data=de.json;.",
        "--add-data=data;data",
        "--add-data=*.py;.",
        
        # Hidden Imports (wichtig für Streamlit)
        "--hidden-import=streamlit",
        "--hidden-import=pandas", 
        "--hidden-import=numpy",
        "--hidden-import=plotly",
        "--hidden-import=reportlab",
        "--hidden-import=sqlite3",
        "--hidden-import=requests",
        "--hidden-import=openpyxl",
        
        # Streamlit spezifische Imports
        "--hidden-import=streamlit.runtime",
        "--hidden-import=streamlit.runtime.caching",
        "--hidden-import=streamlit.runtime.uploaded_file_manager",
        
        # Plotly spezifische Imports  
        "--hidden-import=plotly.graph_objects",
        "--hidden-import=plotly.express",
        
        # Entry Point
        "gui.py"
    ]
    
    print("🚀 Starte PyInstaller...")
    print(f"Kommando: {' '.join(cmd)}")
    
    try:
        # PyInstaller ausführen
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller erfolgreich!")
          # Ergebnis anzeigen
        dist_path = base_path / "dist" / "OemersSolarDingelDangel.exe"
        if dist_path.exists():
            print(f"✅ EXE erstellt: {dist_path}")
            print(f"📁 Größe: {dist_path.stat().st_size / (1024*1024):.1f} MB")
            
            # Code-Signing versuchen
            sign_executable(dist_path)
            
            # UPX Komprimierung versuchen  
            compress_with_upx(dist_path)
            
            # Startscript erstellen
            create_launcher_script(base_path)
            
        else:
            print("❌ EXE Datei nicht gefunden!")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller Fehler: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")

def sign_executable(exe_path):
    """Signiert die erstellte EXE mit Code-Signing"""
    try:
        # Prüfe ob signtool verfügbar ist
        subprocess.run(["signtool"], check=True, capture_output=True)
        print("✅ SignTool gefunden")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ SignTool nicht gefunden - Code-Signing übersprungen")
        print("Installieren Sie Windows SDK für Code-Signing")
        return False
    
    try:
        print("🔒 Code-Signing...")
        cmd = [
            "signtool", "sign",
            "/n", "Ömer Solar Dingel Dangel",  # Zertifikat-Name
            "/t", "http://timestamp.sectigo.com",  # Timestamp Server
            "/fd", "sha256",
            "/d", "Ömers Solar Dingel Dangel",
            str(exe_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Code-Signing erfolgreich!")
        
        # Verifikation
        verify_cmd = ["signtool", "verify", "/pa", "/v", str(exe_path)]
        subprocess.run(verify_cmd, check=True, capture_output=True)
        print("✅ Signatur verifiziert!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Code-Signing fehlgeschlagen: {e}")
        print("Tipp: Erstellen Sie ein Zertifikat oder verwenden Sie ein kommerzielles")
        return False

def compress_with_upx(exe_path, compression_level="--best"):
    """Komprimiert die EXE mit UPX"""
    try:
        # Prüfe UPX Installation
        subprocess.run(["upx", "--version"], check=True, capture_output=True)
        print("✅ UPX gefunden")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ UPX nicht gefunden - Komprimierung übersprungen")
        print("Download: https://upx.github.io/")
        return False
    
    if not exe_path.exists():
        print(f"❌ EXE nicht gefunden: {exe_path}")
        return False
    
    # Original-Größe
    original_size = exe_path.stat().st_size
    print(f"📏 Original-Größe: {original_size / (1024*1024):.1f} MB")
    
    # Backup erstellen
    backup_path = exe_path.with_suffix('.exe.backup')
    shutil.copy2(exe_path, backup_path)
    print(f"💾 Backup erstellt: {backup_path.name}")
    
    try:
        # UPX Komprimierung
        print(f"🗜️ UPX Komprimierung ({compression_level})...")
        cmd = ["upx", compression_level, "--lzma", str(exe_path)]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Neue Größe
        compressed_size = exe_path.stat().st_size
        saved_bytes = original_size - compressed_size
        saved_percent = (saved_bytes / original_size) * 100
        
        print(f"✅ UPX Komprimierung erfolgreich!")
        print(f"📏 Komprimierte Größe: {compressed_size / (1024*1024):.1f} MB")
        print(f"💾 Ersparnis: {saved_bytes / (1024*1024):.1f} MB ({saved_percent:.1f}%)")
        
        # Backup entfernen da erfolgreich
        backup_path.unlink()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ UPX Komprimierung fehlgeschlagen: {e}")
        # Original wiederherstellen
        if backup_path.exists():
            shutil.copy2(backup_path, exe_path)
            backup_path.unlink()
            print("🔄 Original wiederhergestellt")
        return False

def create_launcher_script(base_path):
    """Erstellt ein Startscript für die Streamlit App"""
    launcher_content = '''@echo off
echo Starte Ömers Solar Dingel Dangel...
echo.
echo HINWEIS: Nach dem Start öffnet sich automatisch der Browser
echo mit der Anwendung. Falls nicht, gehe zu: http://localhost:8501
echo.
echo Drücke Ctrl+C zum Beenden
echo.

rem Starte die Streamlit App
streamlit run gui.py --server.port 8501 --server.address localhost

pause
'''
    
    launcher_path = base_path / "start_oemers_solar.bat"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"✅ Startscript erstellt: {launcher_path.name}")

if __name__ == "__main__":
    main()
