# local_storage.py
# Modul zur Verwaltung des lokalen Speicherns und Ladens von Daten (z. B. letzte Projektkonfiguration)

import json
import os
from typing import Any, Dict, Optional

LOCAL_STORAGE_DIR = os.path.join(os.getcwd(), "local_storage")

# Stelle sicher, dass das Verzeichnis existiert
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

def get_storage_file_path(file_name: str) -> str:
    """Gibt den vollständigen Pfad zur Datei im lokalen Speicherverzeichnis zurück."""
    safe_name = file_name.replace("/", "_").replace("\\", "_")
    return os.path.join(LOCAL_STORAGE_DIR, f"{safe_name}.json")

def save_local_data(file_name: str, data: Dict[str, Any]) -> None:
    """Speichert ein Dictionary als JSON-Datei lokal."""
    try:
        with open(get_storage_file_path(file_name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[local_storage] Fehler beim Speichern von {file_name}: {e}")

def load_local_data(file_name: str) -> Optional[Dict[str, Any]]:
    """Lädt ein lokal gespeichertes JSON-Dictionary."""
    try:
        with open(get_storage_file_path(file_name), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[local_storage] Fehler beim Laden von {file_name}: {e}")
        return None

def delete_local_data(file_name: str) -> None:
    """Löscht eine gespeicherte Datei aus dem lokalen Speicher."""
    try:
        os.remove(get_storage_file_path(file_name))
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[local_storage] Fehler beim Löschen von {file_name}: {e}")
