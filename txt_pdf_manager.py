"""
TXT-zu-PDF Integration für das Hauptsystem
Ersetzt die komplexe PDF-Generierung durch die einfache TXT-basierte Lösung

Autor: GitHub Copilot
Datum: 28.07.2025
"""

import os
import subprocess
import re
import sys
from typing import Dict, Any, Optional
import traceback


def generate_pdf_from_txt_files(project_data=True, analysis_results=True, **kwargs):
    try:
        # Vor jeder PDF-Erzeugung: Platzhalter in den TXT-Dateien ersetzen
        try:
            update_txt_files_from_project_data(
                project_data or {}, analysis_results or {}
            )
        except Exception as update_err:
            print(f"⚠️ TXT-Update vor PDF-Erstellung fehlgeschlagen: {update_err}")

   
        # Pfade definierent
        base_dir = os.getcwd()
        pdf_script = os.path.join(base_dir, "pdf_erstellen_komplett.py")
        output_pdf = os.path.join(base_dir, "recreated_full.pdf")

        # Prüfen ob das Script existiert
        if not os.path.exists(pdf_script):
            print(f" PDF-Script nicht gefunden: {pdf_script}")
            return None

        # Prüfen ob input-Ordner existiert
        input_dir = os.path.join(base_dir, "input")
        if not os.path.exists(input_dir):
            print(f" Input-Ordner nicht gefunden: {input_dir}")
            return None

        # 🔥 NEUE DYNAMISCHE DATENINTEGRATION
        print("🔄 Integriere dynamische Kundendaten zur Laufzeit...")
        dynamic_texts = None
        
        try:
            from runtime_dynamic_replacer import RuntimeDynamicReplacer
            from dynamic_data_integrator import DynamicDataIntegrator
            
            # Dynamische Daten vorbereiten
            integrator = DynamicDataIntegrator()
            dynamic_data = integrator.prepare_dynamic_data(
                project_data=project_data or {},
                analysis_results=analysis_results or {},
                company_info=kwargs.get('company_info', {}),
                customer_data=kwargs.get('customer_data', project_data or {})
            )
            
            # TXT-Dateien zur Laufzeit verarbeiten
            replacer = RuntimeDynamicReplacer()
            dynamic_texts = replacer.load_and_process_txt_files(dynamic_data)
            
            print(f"✅ {len(dynamic_data)} dynamische Werte integriert")
            print(f"✅ {len(dynamic_texts)} TXT-Dateien mit echten Kundendaten verarbeitet")
            
        except Exception as dynamic_error:
            print(f"⚠️ Dynamische Datenintegration fehlgeschlagen: {dynamic_error}")
            print("📄 Verwende Original-TXT-Dateien")
            dynamic_texts = None

        # Dynamische Platzhalter in den TXT-Dateien ersetzen (LEGACY - nicht mehr verwendet)
        update_txt_files_from_project_data(project_data or {}, analysis_results or {})

        print("📄 Starte dynamische PDF-Generierung...")

        # Verwende dynamische Texte falls verfügbar
        if dynamic_texts:
            print("✅ Verwende verarbeitete dynamische Texte für PDF-Erstellung")
            try:
                from dynamic_pdf_creator import create_dynamic_pdf
                
                pdf_bytes = create_dynamic_pdf(dynamic_texts)
                
                if pdf_bytes:
                    print(f"✅ Dynamische PDF erfolgreich erstellt ({len(pdf_bytes)} bytes)")
                    
                    # Optional: PDF auch als Datei speichern
                    with open(output_pdf, 'wb') as f:
                        f.write(pdf_bytes)
                    
                    return pdf_bytes
                else:
                    print("❌ Dynamische PDF-Erstellung fehlgeschlagen")
                    
            except Exception as dynamic_pdf_error:
                print(f"⚠️ Dynamische PDF-Erstellung fehlgeschlagen: {dynamic_pdf_error}")
                print("📄 Fallback zu Original-System...")
        
        # Fallback: Original-System verwenden
        print("📄 Verwende Original TXT-zu-PDF System...")

        # PDF-Script ausführen
        result = subprocess.run(
            [sys.executable, pdf_script],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f" PDF-Script Fehler: {result.stderr}")
            return None

        # Prüfen ob PDF erstellt wurde
        if not os.path.exists(output_pdf):
            print(f" PDF-Datei nicht erstellt: {output_pdf}")
            return None

        # PDF-Bytes lesen
        with open(output_pdf, "rb") as f:
            pdf_bytes = f.read()

        print(" PDF erfolgreich aus TXT-Dateien erstellt!")
        return pdf_bytes

    except subprocess.TimeoutExpired:
        print(" PDF-Generierung Timeout nach 30 Sekunden")
        return None
    except Exception as e:
        print(f" Fehler bei TXT-zu-PDF Generierung: {e}")
        print(traceback.format_exc())
        return None


def update_txt_files_from_project_data(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any]
) -> bool:
    """
    Aktualisiert alle *_texte.txt im input-Ordner, indem Platzhalter wie {customer_name}
    durch die realen Werte aus project_data, analysis_results und company_info ersetzt werden.
    """
    try:
        base_dir = os.getcwd()
        input_dir = os.path.join(base_dir, "input")
        if not os.path.exists(input_dir):
            print(f"❌ Input-Ordner nicht gefunden: {input_dir}")
            return False

        # DynamicDataIntegrator importieren
        try:
            from dynamic_data_integrator import DynamicDataIntegrator
        except Exception as import_err:
            print(f"❌ Konnte dynamic_data_integrator nicht importieren: {import_err}")
            return False

        integrator = DynamicDataIntegrator()

        # Firmeninformationen aus project_data extrahieren (verschiedene Schlüssel unterstützen)
        company_info: Dict[str, Any] = {}
        if isinstance(project_data, dict):
            company_info = (
                project_data.get('company_information', {})
                or project_data.get('company_data', {})
                or project_data.get('company_info', {})
                or {}
            )

        # Optionales customer_data extrahieren
        customer_data: Optional[Dict[str, Any]] = None
        if isinstance(project_data, dict):
            customer_data = project_data.get('customer_data')

        # Dynamische Daten vorbereiten (enthält alle benötigten Schlüssel/Werte)
        dynamic_data = integrator.prepare_dynamic_data(
            project_data=project_data or {},
            analysis_results=analysis_results or {},
            company_info=company_info or {},
            customer_data=customer_data or None
        )

        # Alle TXT-Dateien mit _texte.txt durchgehen und Platzhalter ersetzen
        txt_files = [f for f in os.listdir(input_dir) if f.endswith('_texte.txt')]
        if not txt_files:
            print("⚠️ Keine TXT-Dateien gefunden, keine Aktualisierung notwendig")
            return True

        for file_name in txt_files:
            file_path = os.path.join(input_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                original_content = content

                for key, value in dynamic_data.items():
                    placeholder = f"{{{key}}}"
                    if placeholder in content:
                        replacement = '' if value is None else str(value)
                        content = content.replace(placeholder, replacement)

                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Platzhalter in {file_name} aktualisiert")
                else:
                    print(f"ℹ️ Keine Platzhalter zu ersetzen in {file_name}")
            except Exception as file_err:
                print(f"❌ Fehler beim Bearbeiten der Datei {file_name}: {file_err}")
                return False

        print("✅ Alle TXT-Dateien erfolgreich aktualisiert")
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
        "pdf_script_exists": os.path.exists(
            os.path.join(base_dir, "pdf_erstellen_komplett.py")
        ),
        "input_dir_exists": os.path.exists(os.path.join(base_dir, "input")),
        "txt_files_found": False,
        "all_pages_available": False,
    }

    # Prüfe TXT-Dateien
    input_dir = os.path.join(base_dir, "input")
    if requirements["input_dir_exists"]:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
        requirements["txt_files_found"] = len(txt_files) > 0

        # Prüfe ob alle 20 Seiten verfügbar sind
        page_files = [
            f for f in txt_files if f.startswith("seite_") and "_texte.txt" in f
        ]
        if page_files:
            page_numbers = []
            for file in page_files:
                try:
                    num = int(file.split("_")[1])
                    page_numbers.append(num)
                except:
                    pass
            requirements["all_pages_available"] = len(page_numbers) >= 20

    return requirements


def get_system_status() -> str:
    """
    Gibt den aktuellen Status des TXT-Systems zurück

    Returns:
        str: Status-Nachricht
    """
    requirements = check_txt_system_requirements()

    status_parts = []

    if requirements["pdf_script_exists"]:
        status_parts.append(" PDF-Script verfügbar")
    else:
        status_parts.append(" PDF-Script fehlt")

    if requirements["input_dir_exists"]:
        status_parts.append(" Input-Ordner gefunden")
    else:
        status_parts.append(" Input-Ordner fehlt")

    if requirements["txt_files_found"]:
        status_parts.append(" TXT-Dateien gefunden")
    else:
        status_parts.append(" Keine TXT-Dateien")

    if requirements["all_pages_available"]:
        status_parts.append(" 20+ Seiten verfügbar")
    else:
        status_parts.append(" Weniger als 20 Seiten")

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
        print(f" Test erfolgreich! PDF-Größe: {len(pdf_bytes)} bytes")
    else:
        print(" Test fehlgeschlagen!")
