# options.py
# Modul für den Optionen Tab (E)

import streamlit as st
from typing import Dict, Any # Optional, für Typ-Hinweise
from theming.pdf_styles import AVAILABLE_THEMES

# Importiere benötigte Funktionen/Daten (falls Optionen darauf zugreifen)
try:
    # Beispiel: Wenn Optionen Admin Settings speichert/lädt
    from database import load_admin_setting, save_admin_setting
    options_dependencies_available = True
except ImportError as e:
    st.error(f"FEHLER: Benötigte Module für Optionen konnten nicht geladen werden: {e}")
    options_dependencies_available = False
    # Definiere Dummy Funktionen, falls Import fehlschlägt
    def load_admin_setting(key, default=None): return default
    def save_admin_setting(key, value): pass

def display_options_ui():
    st.header("Globale Einstellungen")
    
    st.subheader("PDF Design & Layout")

    # NEU: Auswahl des PDF-Themes
    theme_names = list(AVAILABLE_THEMES.keys())
    
    # Setze den Index auf das aktuell ausgewählte Theme oder das erste in der Liste
    current_theme_name = st.session_state.get("pdf_theme_name", theme_names[0])
    current_index = theme_names.index(current_theme_name) if current_theme_name in theme_names else 0

    selected_theme = st.selectbox(
        "Wählen Sie ein Design-Theme für Ihre PDF-Angebote:",
        options=theme_names,
        index=current_index,
        key="pdf_theme_selector"
    )

    # Speichere die Auswahl im Session State für den PDF-Generator
    if selected_theme:
        st.session_state["pdf_theme_name"] = selected_theme

    # ... (weitere Optionen für Ränder, etc. können hier folgen)


# KORREKTUR: render_options Funktion mit korrekter Signatur, die **kwargs akzeptiert
def render_options(texts: Dict[str, str], **kwargs): # KORREKTUR: **kwargs hinzugefügt
    """
    Rendert den Optionen Tab (E) der Streamlit Anwendung.
    Ermöglicht die Konfiguration von App-Einstellungen.

    Args:
        texts: Dictionary mit den lokalisierten Texten.
        **kwargs: Zusätzliche Keyword-Argumente, z.B. 'module_name' von gui.py.
    """
    # Der Header wird in gui.py gesetzt, aber hier kann der Modulname aus kwargs geholt werden, falls nötig
    module_name = kwargs.get('module_name', texts.get("menu_item_options", "Optionen"))

    # --- Hier kommt der Inhalt für die Optionen hin ---
    # st.write(f"Willkommen im {module_name} Bereich.") # Beispiel Nutzung des übergebenen Namens

    st.info(texts.get("options_content_placeholder", "Die App-Einstellungen können hier konfiguriert werden (Platzhalter).")) # Neuer Text Schlüssel

    # Beispiel für Sprachauswahl (Platzhalter)
    # st.subheader(texts.get("options_language_header", "Sprache auswählen")) # Neuer Text Schlüssel
    # selected_lang = st.selectbox(texts.get("options_language_label", "Sprache"), ["de", "en"], index=0) # Neuer Text Schlüssel
    # # Wenn die Sprache geändert wird, sollten Sie dies im Session State speichern und die App neu laden lassen
    # if st.session_state.get('language', 'de') != selected_lang:
    #    st.session_state['language'] = selected_lang
    #    st.rerun() # App neu starten mit neuer Sprache

    # Beispiel für Lade-/Speicherverhalten (Platzhalter)
    # st.subheader(texts.get("options_save_load_header", "Speicherverhalten")) # Neuer Text Schlüssel
    # auto_save = st.checkbox(texts.get("options_auto_save", "Projekte automatisch speichern"), value=load_admin_setting('auto_save_projects', False)) # Neuer Text Schlüssel
    # if st.button(texts.get("options_save_settings_button", "Optionen speichern")): # Neuer Text Schlüssel
    #    save_admin_setting('auto_save_projects', auto_save)
    #    st.success(texts.get("options_settings_saved_success", "Optionen gespeichert!")) # Neuer Text Schlüssel


    # Entfernen Sie dies, wenn Sie den Inhalt implementieren