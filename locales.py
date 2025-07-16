# locales.py
import json
import os
from typing import Dict, List, Optional, Tuple

# Importiere die globale Fehlerliste aus app_status.py
try:
    from app_status import import_errors as global_import_errors # Geändert
except ImportError:
    # Fallback, falls app_status.py nicht gefunden wird (sollte nicht passieren, wenn es existiert)
    print("LOCALES WARNUNG: app_status.py nicht gefunden, Fehler können nicht global gesammelt werden.")
    global_import_errors: List[str] = []


# Funktion zum Laden der Übersetzungen
def load_translations(lang_code: str = 'de') -> Optional[Dict[str, str]]:
    """Lädt Übersetzungsdaten aus einer JSON-Datei für den gegebenen Sprachcode."""
    # KORREKTUR: `global_import_errors` ist jetzt direkt verfügbar, kein erneuter Import von `gui` nötig.
    # from gui import import_errors as global_import_errors # Entfernt

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, f"{lang_code}.json")
    default_texts = {
        "app_title": "Ömers Solar Kakerlake",
        "error_loading_translations": "Fehler beim Laden der Übersetzungen.",
        "language_file_not_found": "Sprachdatei nicht gefunden: {filepath}",
        # Füge hier weitere absolut notwendige Fallback-Texte hinzu,
        # die benötigt werden, BEVOR die Haupt-TEXTS-Variable in gui.py gefüllt ist.
    }

    try:
        if not os.path.exists(file_path):
            error_msg = default_texts["language_file_not_found"].format(filepath=file_path)
            print(f"LOCALES FEHLER: {error_msg}")
            if global_import_errors is not None: # Sicherstellen, dass die Liste existiert
                global_import_errors.append(error_msg)
            return default_texts

        with open(file_path, 'r', encoding='utf-8') as f:
            texts = json.load(f)
            if not isinstance(texts, dict):
                raise ValueError("Übersetzungsdatei hat kein Dictionary-Format.")
            # print(f"LOCALES INFO: Übersetzungen für '{lang_code}' erfolgreich geladen aus {file_path}")
            return texts
    except FileNotFoundError: # Sollte durch obigen Check abgedeckt sein, aber zur Sicherheit
        error_msg = default_texts["language_file_not_found"].format(filepath=file_path)
        print(f"LOCALES FEHLER: {error_msg}")
        if global_import_errors is not None:
           global_import_errors.append(error_msg)
        return default_texts
    except json.JSONDecodeError as e_json:
        error_msg = f"JSON-Dekodierungsfehler in {file_path}: {e_json}"
        print(f"LOCALES FEHLER: {error_msg}")
        if global_import_errors is not None:
           global_import_errors.append(error_msg)
        return default_texts
    except Exception as e:
        error_msg = f"Allgemeiner Fehler beim Laden von {file_path}: {e}"
        print(f"LOCALES FEHLER: {error_msg}")
        if global_import_errors is not None:
            global_import_errors.append(error_msg)
        return default_texts

def get_text(key: str, locale: str = 'de', fallback: str = None, **kwargs) -> str:
    """
    Holt einen übersetzten Text für den gegebenen Schlüssel.
    
    Args:
        key (str): Textschlüssel
        locale (str): Sprache (Standard: 'de')
        fallback (str): Fallback-Text wenn Schlüssel nicht gefunden
        **kwargs: Format-Parameter für den Text
    
    Returns:
        str: Übersetzter oder Fallback-Text
    """
    # Lade Übersetzungen
    translations = load_translations(locale)
    
    # Hol den Text oder verwende Fallback
    text = translations.get(key, fallback or key)
    
    # Formatiere mit kwargs wenn vorhanden
    try:
        return text.format(**kwargs) if kwargs else text
    except (KeyError, ValueError):
        return text

if __name__ == '__main__':
    # Testen der Ladefunktion
    german_texts = load_translations('de')
    if german_texts and german_texts.get("app_title") != "Ömers Solar Kakerlake":
        print("Deutsche Übersetzungen erfolgreich geladen:")
        # print(f"  Titel: {german_texts.get('app_title')}")
        # print(f"  Fehlermeldung (Beispiel): {german_texts.get('error_general_calculation')}")
    else:
        print("Fehler beim Laden der deutschen Übersetzungen oder Fallback verwendet.")

    # Test mit einer nicht existierenden Sprache
    non_existent_texts = load_translations('xx')
    if non_existent_texts and non_existent_texts.get("app_title") == "Ömers Solar Kakerlake":
        print("\nFallback für nicht existierende Sprache 'xx' korrekt geladen.")
    else:
        print("\nFehler beim Test mit nicht existierender Sprache.")

    if global_import_errors:
        print("\nAufgetretene Importfehler während des locales-Tests:")
        for err in global_import_errors:
            print(f"  - {err}")