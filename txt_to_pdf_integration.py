"""
TXT-zu-PDF Integration für das Hauptsystem
Ersetzt die komplexe PDF-Generierung durch die einfache TXT-basierte Lösung

Autor: GitHub Copilot
Datum: 28.07.2025
"""

import os
import subprocess
import sys
from typing import Dict, Any, Optional
import traceback

def generate_pdf_from_txt_files(
    project_data: Dict[str, Any] = None,
    analysis_results: Dict[str, Any] = None,
    **kwargs
) -> Optional[bytes]:
    """
    Generiert PDF aus TXT-Dateien im input-Ordner
    
    Args:
        project_data: Projektdaten (werden für künftige Erweiterungen verwendet)
        analysis_results: Analyseergebnisse (werden für künftige Erweiterungen verwendet)
        **kwargs: Weitere Parameter (für Kompatibilität)
    
    Returns:
        bytes: PDF-Bytes oder None bei Fehler
    """
    try:
        # Pfade definieren
        base_dir = os.getcwd()
        pdf_script = os.path.join(base_dir, "pdf_erstellen_komplett.py")
        output_pdf = os.path.join(base_dir, "recreated_full.pdf")
        
        # Prüfen ob das Script existiert
        if not os.path.exists(pdf_script):
            print(f"❌ PDF-Script nicht gefunden: {pdf_script}")
            return None
        
        # Prüfen ob input-Ordner existiert
        input_dir = os.path.join(base_dir, "input")
        if not os.path.exists(input_dir):
            print(f"❌ Input-Ordner nicht gefunden: {input_dir}")
            return None
        
        print("📄 Starte TXT-zu-PDF Generierung...")
        
        # PDF-Script ausführen
        result = subprocess.run(
            [sys.executable, pdf_script],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ PDF-Script Fehler: {result.stderr}")
            return None
        
        # Prüfen ob PDF erstellt wurde
        if not os.path.exists(output_pdf):
            print(f"❌ PDF-Datei nicht erstellt: {output_pdf}")
            return None
        
        # PDF-Bytes lesen
        with open(output_pdf, 'rb') as f:
            pdf_bytes = f.read()
        
        print("✅ PDF erfolgreich aus TXT-Dateien erstellt!")
        return pdf_bytes
        
    except subprocess.TimeoutExpired:
        print("❌ PDF-Generierung Timeout nach 30 Sekunden")
        return None
    except Exception as e:
        print(f"❌ Fehler bei TXT-zu-PDF Generierung: {e}")
        print(traceback.format_exc())
        return None

def update_txt_files_from_project_data(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any]
) -> bool:
    """
    Aktualisiert TXT-Dateien im input-Ordner basierend auf den Projektdaten
    
    Args:
        project_data: Aktuelle Projektdaten
        analysis_results: Aktuelle Analyseergebnisse
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        base_dir = os.getcwd()
        input_dir = os.path.join(base_dir, "input")
        
        if not os.path.exists(input_dir):
            print(f"❌ Input-Ordner nicht gefunden: {input_dir}")
            return False
        
        # TODO: Hier können später dynamische TXT-Updates implementiert werden
        # basierend auf project_data und analysis_results
        
        # Beispiel für künftige Erweiterung:
        # - Kundendaten in seite_1_texte.txt schreiben
        # - Berechnungsergebnisse in entsprechende Seiten einfügen
        # - Diagramme als Bilder exportieren und in input-Ordner speichern
        
        print("ℹ️ TXT-Dateien werden derzeit manuell gepflegt")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren der TXT-Dateien: {e}")
        return False

def check_txt_system_requirements() -> Dict[str, bool]:
    """
    Prüft ob alle Anforderungen für das TXT-System erfüllt sind
    
    Returns:
        Dict mit Status-Informationen
    """
    base_dir = os.getcwd()
    requirements = {
        'pdf_script_exists': os.path.exists(os.path.join(base_dir, "pdf_erstellen_komplett.py")),
        'input_dir_exists': os.path.exists(os.path.join(base_dir, "input")),
        'txt_files_found': False,
        'all_pages_available': False
    }
    
    # Prüfe TXT-Dateien
    input_dir = os.path.join(base_dir, "input")
    if requirements['input_dir_exists']:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
        requirements['txt_files_found'] = len(txt_files) > 0
        
        # Prüfe ob alle 20 Seiten verfügbar sind
        page_files = [f for f in txt_files if f.startswith('seite_') and '_texte.txt' in f]
        if page_files:
            page_numbers = []
            for file in page_files:
                try:
                    num = int(file.split('_')[1])
                    page_numbers.append(num)
                except:
                    pass
            requirements['all_pages_available'] = len(page_numbers) >= 20
    
    return requirements

def get_system_status() -> str:
    """
    Gibt den aktuellen Status des TXT-Systems zurück
    
    Returns:
        str: Status-Nachricht
    """
    requirements = check_txt_system_requirements()
    
    status_parts = []
    
    if requirements['pdf_script_exists']:
        status_parts.append("✅ PDF-Script verfügbar")
    else:
        status_parts.append("❌ PDF-Script fehlt")
    
    if requirements['input_dir_exists']:
        status_parts.append("✅ Input-Ordner gefunden")
    else:
        status_parts.append("❌ Input-Ordner fehlt")
    
    if requirements['txt_files_found']:
        status_parts.append("✅ TXT-Dateien gefunden")
    else:
        status_parts.append("❌ Keine TXT-Dateien")
    
    if requirements['all_pages_available']:
        status_parts.append("✅ 20+ Seiten verfügbar")
    else:
        status_parts.append("⚠️ Weniger als 20 Seiten")
    
    return " | ".join(status_parts)

# Kompatibilitäts-Wrapper für bestehende Funktionen
def generate_offer_pdf(*args, **kwargs) -> Optional[bytes]:
    """
    Wrapper-Funktion für Kompatibilität mit bestehendem System
    Leitet Anfragen an die TXT-basierte PDF-Generierung weiter
    """
    return generate_pdf_from_txt_files(*args, **kwargs)

if __name__ == "__main__":
    # Test der Integration
    print("🧪 Teste TXT-zu-PDF Integration...")
    print(f"Status: {get_system_status()}")
    
    # Test-PDF generieren
    pdf_bytes = generate_pdf_from_txt_files()
    if pdf_bytes:
        print(f"✅ Test erfolgreich! PDF-Größe: {len(pdf_bytes)} bytes")
    else:
        print("❌ Test fehlgeschlagen!")
