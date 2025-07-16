#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrekter Launcher für Omers PV Kakerlake
Verwendet die exakten Kommandos, die der User nutzt
"""

import os
import sys
import time
import subprocess
import webbrowser
import socket
from pathlib import Path

# UTF-8 Encoding für die gesamte Anwendung setzen
if sys.platform == "win32":
    # Windows UTF-8 Modus aktivieren
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Für subprocess calls
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'German_Germany.1252')
        except:
            pass

def safe_print(msg):
    """Sichere Print-Funktion"""
    try:
        print(msg, flush=True)
    except:
        pass

def get_bundle_dir():
    """Bundle-Verzeichnis ermitteln"""
    if getattr(sys, 'frozen', False):
        # In PyInstaller EXE
        bundle_dir = sys._MEIPASS
        app_dir = Path(sys.executable).parent
    else:
        # Im Script
        bundle_dir = Path(__file__).parent
        app_dir = bundle_dir
    
    return str(bundle_dir), str(app_dir)

def check_gui_file(bundle_dir):
    """Prüfen ob gui.py existiert"""
    gui_file = os.path.join(bundle_dir, 'gui.py')
    if os.path.exists(gui_file):
        safe_print("✅ gui.py gefunden")
        return True
    else:
        safe_print(f"❌ gui.py nicht gefunden in {bundle_dir}")
        return False

def wait_for_server(port=8501, timeout=30):
    """Warten bis Server erreichbar ist"""
    safe_print(f"Warte auf Server auf Port {port}...")
    
    for i in range(timeout):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                safe_print("✅ Server ist bereit!")
                return True
        except:
            pass
        
        if i % 5 == 0:
            safe_print(f"Warte... ({i}/{timeout})")
        time.sleep(1)
    
    return False

def start_streamlit_server(bundle_dir):
    """Streamlit-Server mit den korrekten Parametern starten"""
    
    # In das Bundle-Verzeichnis wechseln
    os.chdir(bundle_dir)
    
    # UTF-8 Environment für Streamlit setzen
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    env['LANG'] = 'de_DE.UTF-8'
    env['LC_ALL'] = 'de_DE.UTF-8'
    
    # Die exakten Parameter verwenden, die der User nutzt
    cmd = [
        "py", "-m", "streamlit", "run", "gui.py",
        "--server.fileWatcherType=poll",
        "--server.runOnSave=false",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    
    safe_print("Starte Streamlit-Server...")
    safe_print(f"Kommando: {' '.join(cmd)}")
    safe_print("Server wird auf http://localhost:8501 verfügbar sein")
    
    try:
        # Streamlit-Prozess starten
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            cwd=bundle_dir,
            env=env,  # UTF-8 Environment übergeben
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        
        safe_print(f"✅ Streamlit-Prozess gestartet (PID: {process.pid})")
        return process
        
    except FileNotFoundError:
        safe_print("❌ Python oder Streamlit nicht gefunden!")
        safe_print("Versuche alternativen Weg...")
        
        # Fallback: python statt py
        cmd[0] = "python"
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                cwd=bundle_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            safe_print(f"✅ Streamlit-Prozess gestartet (PID: {process.pid})")
            return process
        except Exception as e:
            safe_print(f"❌ Fehler beim Starten: {e}")
            return None
    
    except Exception as e:
        safe_print(f"❌ Fehler beim Starten von Streamlit: {e}")
        return None

def open_browser(url="http://localhost:8501"):
    """Browser öffnen"""
    try:
        safe_print("✅ Browser wird geöffnet...")
        webbrowser.open(url)
        return True
    except Exception as e:
        safe_print(f"⚠️ Browser konnte nicht geöffnet werden: {e}")
        safe_print(f"Bitte öffnen Sie manuell: {url}")
        return False

def main():
    """Hauptfunktion"""
    safe_print("=" * 50)
    safe_print("Omers PV Kakerlake - Korrekter Launcher")
    safe_print("=" * 50)
    
    # Bundle-Verzeichnis ermitteln
    bundle_dir, app_dir = get_bundle_dir()
    safe_print(f"Bundle: {bundle_dir}")
    safe_print(f"App: {app_dir}")
    
    # GUI-Datei prüfen
    if not check_gui_file(bundle_dir):
        input("Drücken Sie Enter zum Beenden...")
        return
    
    # Streamlit-Server starten
    process = start_streamlit_server(bundle_dir)
    if not process:
        input("Drücken Sie Enter zum Beenden...")
        return
    
    # Auf Server warten
    if wait_for_server():
        # Browser öffnen
        open_browser()
        
        safe_print("=" * 50)
        safe_print("🎉 Omers PV Kakerlake läuft!")
        safe_print("📱 URL: http://localhost:8501")
        safe_print("🔄 Zum Beenden einfach dieses Fenster schließen")
        safe_print("=" * 50)
        
        # Warten bis der Prozess beendet wird
        try:
            process.wait()
        except KeyboardInterrupt:
            safe_print("Server wird beendet...")
            process.terminate()
    else:
        safe_print("❌ Server konnte nicht gestartet werden!")
        safe_print("Prozess-Output:")
        try:
            stdout, stderr = process.communicate(timeout=5)
            if stdout:
                safe_print("STDOUT:", stdout.decode('utf-8', errors='ignore'))
            if stderr:
                safe_print("STDERR:", stderr.decode('utf-8', errors='ignore'))
        except:
            pass
        
        process.terminate()
        input("Drücken Sie Enter zum Beenden...")

if __name__ == "__main__":
    main()
