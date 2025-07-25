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

    # Farbauswahl und Modul-Optionen nur für TOM‑90
    primary_color: str = "#003366"
    inclusion_options: Dict[str, Any] = {}
    texts: Dict[str, Any] = {}
    if layout_option == "TOM‑90":
        # Primärfarbe wählen
        primary_color = st.color_picker(
            "Primärfarbe für Überschriften und Fußzeile", value="#003366",
            help="Wählen Sie die Hauptfarbe des PDF‑Layouts (z. B. Unternehmensfarbe)."
        )
        # Optional ein-/ausschaltbare Blöcke
        inclusion_options['include_have_you_known'] = st.checkbox(
            "Infobox 'Haben Sie gewusst?' einfügen", value=True
        )
        inclusion_options['include_financing'] = st.checkbox(
            "Finanzierungsvergleich (Kurzfassung) einfügen", value=True
        )
        inclusion_options['include_savings_summary'] = st.checkbox(
            "Ersparnis‑Zusammenfassung einfügen", value=True
        )
        inclusion_options['include_financing_details'] = st.checkbox(
            "Detaillierte Finanzierungsberechnungen einfügen", value=True
        )
        # Unteroptionen für Finanzierungsdetails (nur sichtbar wenn Hauptschalter aktiv)
        if inclusion_options['include_financing_details']:
            st.markdown("*Finanzierungsdetails*:")
            inclusion_options['include_financing_details_annuity'] = st.checkbox(
                "Annuitätendarlehen", value=True
            )
            inclusion_options['include_financing_details_leasing'] = st.checkbox(
                "Leasing", value=True
            )
            inclusion_options['include_financing_details_depreciation'] = st.checkbox(
                "Abschreibung", value=True
            )
            inclusion_options['include_financing_details_comparison'] = st.checkbox(
                "Finanzierungsvergleich (Detail)", value=True
            )
            inclusion_options['include_financing_details_tax'] = st.checkbox(
                "Kapitalertragsteuer", value=True
            )
            inclusion_options['include_financing_details_contracting'] = st.checkbox(
                "Contracting", value=True
            )

        # Optionen für Seitenzahlen und Logo
        st.markdown("**Seitennummerierung & Logo**")
        inclusion_options['include_page_logo'] = st.checkbox(
            "Firmenlogo unten links anzeigen", value=True
        )
        inclusion_options['include_page_numbers'] = st.checkbox(
            "Seitenzahlen anzeigen", value=True
        )

        # Benutzerdefinierte Textfelder
        st.markdown("**Benutzerdefinierte Textfelder**")
        custom_texts = []
        title1 = st.text_input("Titel 1", value="")
        body1 = st.text_area("Text 1", value="")
        if title1 or body1:
            custom_texts.append({"title": title1, "body": body1})
        title2 = st.text_input("Titel 2", value="", key="title2")
        body2 = st.text_area("Text 2", value="", key="body2")
        if title2 or body2:
            custom_texts.append({"title": title2, "body": body2})

        # Benutzerdefinierte Bilder
        st.markdown("**Benutzerdefinierte Bilder**")
        custom_images = []
        custom_captions = []
        uploaded1 = st.file_uploader("Bild 1 hochladen", type=["png", "jpg", "jpeg"])
        if uploaded1 is not None:
            data = uploaded1.read()
            if data:
                custom_images.append(base64.b64encode(data).decode("utf-8"))
                caption1 = st.text_input("Bildunterschrift 1", value="")
                custom_captions.append(caption1)
        uploaded2 = st.file_uploader("Bild 2 hochladen", type=["png", "jpg", "jpeg"], key="img2")
        if uploaded2 is not None:
            data2 = uploaded2.read()
            if data2:
                custom_images.append(base64.b64encode(data2).decode("utf-8"))
                caption2 = st.text_input("Bildunterschrift 2", value="", key="caption2")
                custom_captions.append(caption2)

        # Diagramm-Beschreibungen
        st.markdown("**Diagramm-Beschreibungen**")
        desc_donut = st.text_area("Beschreibung für Donut‑Charts", value="")
        desc_bar = st.text_area("Beschreibung für Balkendiagramm", value="", key="desc_bar")
        desc_prod = st.text_area("Beschreibung für Produktions/Verbrauchs‑Diagramm", value="", key="desc_prod")

        # Texte für das PDF bereitstellen
        texts = {
            'custom_texts': custom_texts,
            'custom_images': custom_images,
            'custom_image_captions': custom_captions,
            'description_donut_charts': desc_donut,
            'description_bar_chart': desc_bar,
            'description_prod_vs_cons_chart': desc_prod,
        }

    # Live-Vorschau
    st.subheader("Live‑Vorschau")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            if layout_option == "TOM‑90":
                pdf_bytes = generate_tom90_offer_pdf(
                    project_data=offer_data,
                    analysis_results=analysis_results,
                    company_info=company_info,
                    company_logo_base64=None,
                    selected_title_image_b64=None,
                    selected_offer_title_text="Ihr Angebot",
                    inclusion_options=inclusion_options,
                    texts=texts,
                    theme_name="Blau Elegant",
                    primary_color=primary_color,
                )
                if pdf_bytes:
                    tmp.write(pdf_bytes)
            else:
                tmp.write(b"")
            with open(tmp.name, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{encoded}" width="700" height="900" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Fehler bei der PDF‑Vorschau: {e}")

        pdf_bytes = generate_tom90_offer_pdf(
        project_data=offer_data,
        analysis_results=analysis_results,
        company_info=company_info,
        company_logo_base64=None,
        selected_title_image_b64=None,
        selected_offer_title_text="Ihr Angebot",
        inclusion_options=inclusion_options,
        texts=texts,
        theme_name="Blau Elegant",
        primary_color=primary_color,
        list_products_func=list_products_func,       # <-- Funktion zum Listen der Produkte
        get_product_by_id_func=get_product_by_id_func  # <-- Funktion zum Abrufen eines Produkts
    )
