"""
tom90_pdf_composer_ui.py
------------------------

Interaktive Streamlit‑Oberfläche zur Erzeugung eines Angebots im
TOM‑90‑Design.  Dieses Modul erweitert die bestehende PDF‑Composer‑UI um
eine Layout‑Auswahl sowie eine Farbauswahl für die Primärfarbe.  Wird
das TOM‑90‑Layout gewählt, erzeugt die UI eine Vorschau über die
Funktion ``generate_tom90_offer_pdf`` aus ``tom90_renderer.py``.

Diese Datei ist unabhängig von der bestehenden UI und kann als
Beispiel oder als neuer Einstiegspunkt genutzt werden.  Sie beeinflusst
keine bestehenden Dateien und bietet eine alternative Darstellung mit
Farbauswahl.  Um die UI im Streamlit‑Umfeld zu verwenden, integrieren
Sie die Funktion ``display_tom90_pdf_ui`` in Ihre Haupt‑Streamlit‑App.
"""
from __future__ import annotations

import base64
import os
import tempfile
from typing import Dict, Any

import streamlit as st

from tom90_renderer import generate_tom90_offer_pdf


def display_tom90_pdf_ui(offer_data: Dict[str, Any], analysis_results: Dict[str, Any], company_info: Dict[str, Any]) -> None:
    """Zeigt eine UI zur Konfiguration und Vorschau von TOM‑90‑PDFs.

    Die Nutzer können zwischen dem Standard‑Layout und dem TOM‑90‑Layout
    wählen und die Primärfarbe für das TOM‑90‑Design anpassen.  Eine
    Live‑Vorschau wird nach jeder Änderung neu erstellt.

    Args:
        offer_data: Projektdaten für das Angebot.
        analysis_results: Ergebnisdaten der Analyse.
        company_info: Firmeninformationen.
    """
    st.header("PDF‑Ausgabe konfigurieren")
    st.markdown("Wählen Sie das gewünschte Layout und passen Sie die Farben an.")

    # Layout-Auswahl: Standard oder TOM‑90
    layout_option = st.selectbox(
        "Layout wählen",
        options=["Standard", "TOM‑90"],
        index=1,
        help="Wählen Sie 'TOM‑90', um das moderne Layout mit modularer Blockstruktur zu verwenden."
    )

    # Farbauswahl nur für TOM‑90
    primary_color: str = "#003366"
    if layout_option == "TOM‑90":
        primary_color = st.color_picker(
            "Primärfarbe für Überschriften und Fußzeile", value="#003366",
            help="Wählen Sie die Hauptfarbe des PDF‑Layouts (z. B. Unternehmensfarbe)."
        )

    # Live-Vorschau
    st.subheader("Live‑Vorschau")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            if layout_option == "TOM‑90":
                # Erstelle PDF im TOM‑90 Design
                pdf_bytes = generate_tom90_offer_pdf(
                    project_data=offer_data,
                    analysis_results=analysis_results,
                    company_info=company_info,
                    company_logo_base64=None,
                    selected_title_image_b64=None,
                    selected_offer_title_text="Ihr Angebot",
                    inclusion_options={},
                    texts={},
                    theme_name="Blau Elegant",
                    primary_color=primary_color,
                )
                if pdf_bytes:
                    tmp.write(pdf_bytes)
            else:
                # Fallback: Verwenden Sie die bestehende PDF‑Erzeugung hier
                tmp.write(b"")
            # Datei lesen und als Base64 einbetten
            with open(tmp.name, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{encoded}" width="700" height="900" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Fehler bei der PDF‑Vorschau: {e}")
