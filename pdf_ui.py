# pdf_ui.py
"""
Datei: pdf_ui.py
Zweck: Benutzeroberfläche für die Konfiguration und Erstellung von Angebots-PDFs.
       Ermöglicht die Auswahl von Vorlagen, Inhalten und spezifischen Diagrammen in einem Dreispaltenlayout.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-08 (Datenstatus-Anzeige und Fallback-PDF-Option hinzugefügt)
"""
import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import base64
import traceback
import os
import json
import pandas as pd
from datetime import datetime


# --- Fallback-Funktionsreferenzen ---
def _dummy_load_admin_setting_pdf_ui(key, default=None):
    if key == "pdf_title_image_templates":
        return [{"name": "Standard-Titelbild (Fallback)", "data": None}]
    if key == "pdf_offer_title_templates":
        return [
            {
                "name": "Standard-Titel (Fallback)",
                "content": "Angebot für Ihre Photovoltaikanlage",
            }
        ]
    if key == "pdf_cover_letter_templates":
        return [
            {
                "name": "Standard-Anschreiben (Fallback)",
                "content": "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.",
            }
        ]
    elif key == "active_company_id":
        return None
    elif key == "pdf_offer_presets":
        return []  # Korrekter Fallback als Liste
    return default


def _dummy_save_admin_setting_pdf_ui(key, value):
    return False


def _dummy_generate_offer_pdf(*args, **kwargs):
    st.error(
        "PDF-Generierungsfunktion (pdf_generator.py) nicht verfügbar oder fehlerhaft (Dummy in pdf_ui.py aktiv)."
    )
    return None


def _dummy_get_active_company_details() -> Optional[Dict[str, Any]]:
    return {"name": "Dummy Firma AG", "id": 0, "logo_base64": None}


def _dummy_list_company_documents(
    company_id: int, doc_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    return []


# PDF-VORSCHAU INTEGRATION (NEU)
try:
    from pdf_preview import show_pdf_preview_interface, create_pdf_template_presets

    _PDF_PREVIEW_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _PDF_PREVIEW_AVAILABLE = False

    def show_pdf_preview_interface(*args, **kwargs):
        st.error(" PDF-Vorschau-Modul nicht verfügbar!")
        return None

    def create_pdf_template_presets():
        return {}


# TOM-90 PDF RENDERER INTEGRATION (NEU)
try:
    from tom90_renderer import generate_tom90_offer_pdf
    from tom90_pdf_composer_ui import display_tom90_pdf_ui

    _TOM90_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _TOM90_AVAILABLE = False

    def generate_tom90_offer_pdf(*args, **kwargs):
        st.error(" TOM-90 Renderer nicht verfügbar!")
        return None

    def display_tom90_pdf_ui(*args, **kwargs):
        st.error(" TOM-90 UI nicht verfügbar!")
        return None


try:
    from doc_output import _show_pdf_data_status
    from pdf_generator import generate_offer_pdf
    from pdf_widgets import orderable_multiselect

    # ... weitere Ihrer Importe
    _DEPENDENCIES_AVAILABLE = True
    _WIDGET_AVAILABLE = True
except ImportError:
    _DEPENDENCIES_AVAILABLE = False
    _WIDGET_AVAILABLE = False

    # Definieren Sie hier Ihre Dummy-Funktionen für den Fall, dass Importe fehlschlagen
    def _show_pdf_data_status(*args, **kwargs):
        return True

    def generate_offer_pdf(*args, **kwargs):
        st.error("pdf_generator.py nicht gefunden.")
        return None

    def orderable_multiselect(title, sections, default_order, key):
        st.warning("pdf_widgets.py nicht gefunden. Standard-Auswahl wird verwendet.")
        return [{"key": k, "name": v, "active": True} for k, v in sections.items()]


def get_text_pdf_ui(texts_dict, key, fallback_text=None):
    return texts_dict.get(key, fallback_text or key)


# --- Hilfsfunktionen ---
def get_text_pdf_ui(
    texts_dict: Dict[str, str], key: str, fallback_text: Optional[str] = None
) -> str:
    if not isinstance(texts_dict, dict):
        return (
            fallback_text
            if fallback_text is not None
            else key.replace("_", " ").title() + " (Texte fehlen)"
        )
    return texts_dict.get(
        key,
        (
            fallback_text
            if fallback_text is not None
            else key.replace("_", " ").title() + " (Text-Key fehlt)"
        ),
    )


def _get_all_available_chart_keys(
    analysis_results: Dict[str, Any], chart_key_map: Dict[str, str]
) -> List[str]:
    if not analysis_results or not isinstance(analysis_results, dict):
        return []
    return [k for k in chart_key_map.keys() if analysis_results.get(k) is not None]


def _get_all_available_company_doc_ids(
    active_company_id: Optional[int], db_list_company_documents_func: Callable
) -> List[int]:
    if active_company_id is None or not callable(db_list_company_documents_func):
        return []
    docs = db_list_company_documents_func(active_company_id, None)
    return [doc["id"] for doc in docs if isinstance(doc, dict) and "id" in doc]


# --- Haupt-Render-Funktion für die PDF UI ---
def render_pdf_ui(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    get_active_company_details_func: Callable[
        [], Optional[Dict[str, Any]]
    ] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[
        [int, Optional[str]], List[Dict[str, Any]]
    ] = _dummy_list_company_documents,
):
    st.header(get_text_pdf_ui(texts, "menu_item_doc_output", "Angebotsausgabe (PDF)"))

    # === AUTOMATISCHE DATEN-BACKUP ===
    # Sichere die aktuellen Daten automatisch in Session State
    if analysis_results and len(analysis_results) > 0:
        st.session_state.current_analysis_results = analysis_results.copy()
    if project_data and len(project_data) > 0:
        st.session_state.current_project_data = project_data.copy()

    # === SESSION STATE VALIDATION & AUTO-RECOVERY ===
    # Überprüfe und stelle sicher, dass alle notwendigen Daten verfügbar sind

    # Debug-Information (optional erweitert)
    with st.expander(" Session State Status", expanded=False):
        st.write("**Aktuelle Datenverfügbarkeit:**")
        st.write(
            f"- Analysis Results: {' Verfügbar' if analysis_results and len(analysis_results) > 0 else ' Leer'}"
        )
        st.write(
            f"- Project Data: {' Verfügbar' if project_data and len(project_data) > 0 else ' Leer'}"
        )
        st.write(
            f"- Session Calculation Results: {' Verfügbar' if st.session_state.get('calculation_results') else ' Leer'}"
        )
        st.write(
            f"- Session Project Data: {' Verfügbar' if st.session_state.get('project_data') else ' Leer'}"
        )
        st.write(
            f"- PDF Backup: {' Verfügbar' if st.session_state.get('pdf_generation_analysis_backup') else ' Leer'}"
        )
        if analysis_results:
            st.write(f"- Analysis Keys: {list(analysis_results.keys())[:5]}...")

    if not analysis_results or len(analysis_results) == 0:
        st.warning(" Keine Analyseergebnisse verfügbar. Versuche Wiederherstellung...")

        # Versuche Daten aus Session State zu laden
        session_calc_results = st.session_state.get("calculation_results", {})
        backup_calc_results = st.session_state.get("calculation_results_backup", {})

        if (
            session_calc_results
            and isinstance(session_calc_results, dict)
            and len(session_calc_results) > 0
        ):
            analysis_results = session_calc_results
            st.success(
                " Analyseergebnisse automatisch aus Session State wiederhergestellt!"
            )
        elif backup_calc_results and isinstance(backup_calc_results, dict):
            # Backup kann 'results' Schlüssel haben oder direkt die Daten
            if "results" in backup_calc_results and isinstance(
                backup_calc_results["results"], dict
            ):
                analysis_results = backup_calc_results["results"]
                st.info(" Analyseergebnisse aus Backup wiederhergestellt!")
            else:
                analysis_results = backup_calc_results
                st.info(" Analyseergebnisse aus Backup wiederhergestellt!")
        else:
            st.error(
                " Keine Analyseergebnisse verfügbar. Bitte führen Sie zuerst eine Berechnung durch."
            )
            st.stop()

    # Projektdaten validieren
    if not project_data or len(project_data) == 0:
        st.warning(" Keine Projektdaten verfügbar. Versuche Wiederherstellung...")
        session_project_data = st.session_state.get("project_data", {})
        if (
            session_project_data
            and isinstance(session_project_data, dict)
            and len(session_project_data) > 0
        ):
            project_data = session_project_data
            st.success(" Projektdaten automatisch wiederhergestellt!")
        else:
            st.error(
                " Keine Projektdaten verfügbar. Bitte konfigurieren Sie zuerst ein Projekt."
            )
            st.stop()

    # === PDF LAYOUT AUSWAHL ===
    st.subheader(" PDF Layout auswählen")
    layout_choice = st.selectbox(
        "Wählen Sie das PDF-Layout:",
        options=["Standard Layout", "TOM-90 Modernes Layout", "Klassisches Layout"],
        index=0,
        help="Das TOM-90 Layout bietet ein modernes, modulares Design mit erweiterten Funktionen.",
    )

    # === TOM-90 LAYOUT BEREICH ===
    if layout_choice == "TOM-90 Modernes Layout":
        if _TOM90_AVAILABLE:
            st.success(" TOM-90 Renderer verfügbar")
            render_tom90_pdf_section(
                texts,
                project_data,
                analysis_results,
                get_active_company_details_func,
                get_product_by_id_func,
            )
            return  # Beende hier für TOM-90 Layout
        else:
            st.error(" TOM-90 Renderer nicht verfügbar. Verwende Standard Layout.")
            layout_choice = "Standard Layout"

    # === STANDARD LAYOUT (BESTEHENDE FUNKTIONALITÄT) ===

    # --- PDF-Sektionen früh definieren ---
    all_pdf_sections = {
        "ProjectOverview": get_text_pdf_ui(
            texts, "pdf_section_title_projectoverview", "1. Projektübersicht"
        ),
        "TechnicalComponents": get_text_pdf_ui(
            texts, "pdf_section_title_technicalcomponents", "2. Systemkomponenten"
        ),
        "CostDetails": get_text_pdf_ui(
            texts, "pdf_section_title_costdetails", "3. Kostenaufstellung"
        ),
        "Economics": get_text_pdf_ui(
            texts, "pdf_section_title_economics", "4. Wirtschaftlichkeit"
        ),
        "SimulationDetails": get_text_pdf_ui(
            texts, "pdf_section_title_simulationdetails", "5. Simulation"
        ),
        "CO2Savings": get_text_pdf_ui(
            texts, "pdf_section_title_co2savings", "6. CO₂-Einsparung"
        ),
        "Visualizations": get_text_pdf_ui(
            texts, "pdf_section_title_visualizations", "7. Grafiken"
        ),
        "FutureAspects": get_text_pdf_ui(
            texts, "pdf_section_title_futureaspects", "8. Zukunftsaspekte"
        ),
    }

    if not _WIDGET_AVAILABLE:
        st.error(
            "Kritisches UI-Modul 'pdf_widgets.py' nicht gefunden. Drag-and-Drop ist nicht verfügbar."
        )
        return
    # Debug-Bereich hinzufügen
    render_pdf_debug_section(
        texts,
        project_data,
        analysis_results,
        get_active_company_details_func,
        db_list_company_documents_func,
        get_product_by_id_func,
    )

    # --- Dynamische Inhalte außerhalb der Form ---
    st.subheader(" zusätzliche Inhalte")

    col1, col2 = st.columns(2)
    with col1:
        # --- Frei gestaltbare Textbereiche ---
        if "custom_text_blocks" not in st.session_state:
            st.session_state.custom_text_blocks = []
        if st.button(" gestaltbare Textbereich hinzufügen"):
            st.session_state.custom_text_blocks.append({"title": "", "content": ""})

    with col2:
        # --- Frei einfügbare Bilder ---
        if "custom_images" not in st.session_state:
            st.session_state.custom_images = []
        if st.button(" zusätzliches Bild / Foto hinzufügen"):
            st.session_state.custom_images.append(
                {"title": "", "description": "", "data": None, "filename": ""}
            )

    col1, col2 = st.columns(2)

    with col1:
        default_order = list(all_pdf_sections.keys())
        st.markdown("---")
        st.subheader("1. Kategorien für den PDF Inhalt wählen")

        final_section_config = orderable_multiselect(
            title="PDF-Hauptinhalte wählen und ordnen",
            sections=all_pdf_sections,
            default_order=default_order,
            key="pdf_final_section_config",
        )

        st.markdown("---")
        st.subheader("2. Features / Highlights auswählen")

        with col1:
            # PDF-Qualität und Format
            pdf_quality = st.selectbox(
                "PDF-Qualität",
                ["Standard", "Hoch", "Druck-Qualität"],
                help="Höhere Qualität = größere Dateien, aber bessere Darstellung",
                key="pdf_quality_select_v1_unique",
            )

        # Zwei umfassende Menü-Sektionen
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("####  **Kern-Inhalte & Darstellung**")

            include_company_logo = st.checkbox(
                " Firmenlogo anzeigen",
                value=True,
                help="Logo der aktiven Firma im PDF-Header",
                key="pdf_include_company_logo_main",
            )

            include_product_images = st.checkbox(
                " Produktbilder einbinden",
                value=True,
                help="Bilder der gewählten PV-Module, Wechselrichter etc.",
                key="pdf_include_product_images_main",
            )

            include_technical_specs = st.checkbox(
                " Detaillierte Technik-Spezifikationen",
                value=True,
                help="Umfassende technische Details zu allen Komponenten",
                key="pdf_include_technical_specs_main",
            )

            include_cost_breakdown = st.checkbox(
                " Detaillierte Kostenaufschlüsselung",
                value=True,
                help="Aufschlüsselung nach Modulen, Wechselrichtern, Installation etc.",
                key="pdf_include_cost_breakdown_main",
            )

            include_charts_graphs = st.checkbox(
                " Wirtschaftlichkeits-Diagramme",
                value=True,
                help="ROI, Amortisation, Ersparnisse über die Zeit",
                key="pdf_include_charts_graphs_main",
            )

            include_co2_analysis = st.checkbox(
                " CO₂-Einsparung & Nachhaltigkeit",
                value=True,
                help="Umweltbilanz und CO₂-Reduktion der Anlage",
                key="pdf_include_co2_analysis_main",
            )

        with col2:
            st.markdown("####  **Erweiterte Features & Anhänge**")

            include_simulation_details = st.checkbox(
                " Detaillierte Simulationsergebnisse",
                value=True,
                help="Monats-/Jahresproduktion, Verbrauchsanalyse, Eigenverbrauch",
            )

            include_roof_visualization = st.checkbox(
                " Dachvisualisierung & Satellitenbilder",
                value=True,
                help="Satellitenaufnahme mit PV-Modulplatzierung",
            )

            include_future_scenarios = st.checkbox(
                " Zukunftsszenarien & Erweiterungen",
                value=True,
                help="E-Auto-Integration, Speicher-Upgrade, Strompreisentwicklung",
            )

            include_legal_info = st.checkbox(
                " Rechtliche Hinweise & Garantien",
                value=True,
                help="Garantiebedingungen, Versicherung, rechtliche Aspekte",
            )

            include_installation_timeline = st.checkbox(
                " Installations-Zeitplan & Prozess",
                value=True,
                help="Projektablauf von der Bestellung bis zur Inbetriebnahme",
            )

            include_product_datasheets = st.checkbox(
                " Produktdatenblätter als Anhang",
                value=True,
                help="Vollständige Herstellerdatenblätter anhängen (größere PDF)",
            )

        st.markdown("---")
        st.subheader("3. Reihenfolge & Inhalte der Sektionen")

        # --- FUNKTIONIERENDES DRAG-AND-DROP ---
        # HINWEIS: Nutzt Ihre bestehende all_sections_map
        # Ich habe "Attachments" hinzugefügt, da dies eine wählbare Sektion ist.
        all_sections_map = {
            "TitlePageCoverLetter": "Titel & Anschreiben",
            "KeyVisuals": "Kennzahlen-Übersicht (Donuts)",
            "TechnicalComponents": "Technische Komponenten",
            "MainCharts": "Wirtschaftlichkeits-Analyse",
            "CostsAndEconomics": "Kosten & Tabellen",
            "SideBySideSims": "Simulations-Vergleich",
            "CustomImages": "Individuelle Bilder",
            "CustomTexts": "Individuelle Texte",
            "HighlightBox": "Highlight-Box",
            "OptionalCharts": "Weitere Diagramme",
            "Attachments": "Anhänge (Datenblätter, Dokumente)",  # <-- Hinzugefügt für Vollständigkeit
        }

        # Die Standard-Reihenfolge wird aus Ihrer Map generiert
        default_order = list(all_sections_map.keys())

        # Aufruf des neuen, funktionierenden Widgets mit Ihrer Map
        final_section_config = orderable_multiselect(
            title="PDF-Sektionen anordnen & auswählen",
            sections=all_sections_map,
            default_order=default_order,
            key="pdf_final_section_config",
        )

        st.markdown("---")
        st.subheader("4. Freie Gestaltung")

        # --- Frei gestaltbare Textbereiche (nur Eingabefelder, Buttons sind außerhalb) ---
        for i, text_block in enumerate(st.session_state.get("custom_text_blocks", [])):
            with st.container(border=True):
                text_block["title"] = st.text_input(
                    "Überschrift für Textblock", key=f"custom_text_title_{i}"
                )
                text_block["content"] = st.text_area(
                    "Inhalt des Textblocks", key=f"custom_text_content_{i}"
                )

        # --- Frei einfügbare Bilder (nur Eingabefelder, Buttons sind außerhalb) ---
        for i, image_slot in enumerate(st.session_state.get("custom_images", [])):
            with st.container(border=True):
                image_slot["title"] = st.text_input(
                    "Bild-Überschrift", key=f"custom_img_title_{i}"
                )
                uploaded_file = st.file_uploader(
                    "Bilddatei",
                    type=["png", "jpg", "jpeg"],
                    key=f"custom_img_upload_{i}",
                )
                if uploaded_file:
                    image_slot["data"] = uploaded_file.getvalue()
                    image_slot["filename"] = uploaded_file.name
                if image_slot.get("filename"):
                    st.caption(f"Geladen: {image_slot['filename']}")
                image_slot["description"] = st.text_area(
                    "Bild-Beschreibung", key=f"custom_img_desc_{i}"
                )

        # --- Nebeneinanderliegende Simulationen ---
        # (Ihre bestehende `chart_key_to_friendly_name_map` wird hier benötigt)
        all_available_chart_keys = (
            list(analysis_results.keys()) if analysis_results else []
        )
        chart_key_map = {
            k: k.replace("_chart_bytes", "").replace("_", " ").title()
            for k in all_available_chart_keys
        }

        side_by_side_sim_keys = st.multiselect(
            "Wählen Sie 2 Simulationen für eine Vergleichsansicht",
            options=[
                k
                for k in all_available_chart_keys
                if "switcher" in k or "3d" in k.lower()
            ],
            format_func=lambda x: chart_key_map.get(x, x),
            max_selections=2,
        )

        # --- Highlight-Box ---
        include_highlight_box = st.checkbox("Highlight-Box ('Ihr Vorteil') einfügen?")
        highlight_box_title = ""
        highlight_box_content = ""
        if include_highlight_box:
            highlight_box_title = st.text_input(
                "Titel für Highlight-Box", "Ihr entscheidender Vorteil"
            )
            highlight_box_content = st.text_area(
                "Inhalt für Highlight-Box",
                "Mit dieser Photovoltaikanlage sichern Sie sich...",
            )

        # --- PDF-Design auswählen ---
        theme_name = st.selectbox(
            "PDF-Design auswählen",
            options=["Modern", "Klassisch", "Minimalistisch"],
            index=0,
            help="Wählen Sie das visuelle Design für das generierte PDF-Dokument.",
        )

        # --- SUBMIT BUTTON ---
        submitted = st.button(
            " Finales PDF erstellen", type="primary", use_container_width=True
        )
    # --- PDF-Generierungslogik nach dem Submit ---
    if submitted:
        # === LETZTE VALIDIERUNG VOR PDF-GENERIERUNG ===
        # Sicherheitsprüfung: Nochmals validieren, dass alle Daten verfügbar sind
        if not analysis_results or len(analysis_results) == 0:
            st.error(
                " Analyseergebnisse vor PDF-Generierung verloren gegangen. Bitte starten Sie die Berechnung erneut."
            )
            st.stop()

        if not project_data or len(project_data) == 0:
            st.error(
                " Projektdaten vor PDF-Generierung verloren gegangen. Bitte konfigurieren Sie das Projekt erneut."
            )
            st.stop()

        # === BACKUP DER AKTUELLEN DATEN ===
        # Sicherung der Daten für persistente Nutzung
        st.session_state.pdf_generation_analysis_backup = analysis_results.copy()
        st.session_state.pdf_generation_project_backup = project_data.copy()
        st.session_state.pdf_generation_timestamp = datetime.now().isoformat()

        with st.spinner("Seggeli Ultra komponiert Ihr PDF..."):
            active_company = get_active_company_details_func()
            company_info_for_pdf = active_company if active_company else {}
            active_sections_df = pd.DataFrame(final_section_config)
            active_sections_df = active_sections_df[active_sections_df["active"]]
            section_order = active_sections_df["key"].tolist()
            # Key-Mapping von UI-Namen zurück zu internen Keys
            reverse_section_map = {v: k for k, v in all_sections_map.items()}

            # Verwende final_section_config für die finale Reihenfolge
            final_section_order = section_order

            pdf_params = {
                "project_data": project_data,
                "analysis_results": analysis_results,
                "company_info": get_active_company_details_func(),
                "texts": texts,
                "theme_name": theme_name,
                "section_order": section_order,
                # ... füllen Sie hier alle weiteren benötigten Parameter auf
                "get_product_by_id_func": get_product_by_id_func,
            }

            with st.spinner("Seggeli Ultra komponiert Ihr PDF..."):
                pdf_bytes = generate_offer_pdf(**pdf_params)

                if pdf_bytes:
                    st.success(" PDF erfolgreich komponiert!")
                    st.download_button(
                        label=" PDF Herunterladen",
                        data=pdf_bytes,
                        file_name=f"Angebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="standard_pdf_download_btn",
                    )
                else:
                    st.error(" PDF-Erstellung fehlgeschlagen.")

            # Erweiterte Inclusion-Optionen aus UI-Checkboxen erstellen
            inclusion_options = {
                "include_company_logo": include_company_logo,
                "include_product_images": include_product_images,
                "include_technical_specs": include_technical_specs,
                "include_cost_breakdown": include_cost_breakdown,
                "include_charts_graphs": include_charts_graphs,
                "include_co2_analysis": include_co2_analysis,
                "include_simulation_details": include_simulation_details,
                "include_roof_visualization": include_roof_visualization,
                "include_future_scenarios": include_future_scenarios,
                "include_legal_info": include_legal_info,
                "include_installation_timeline": include_installation_timeline,
                "include_product_datasheets": include_product_datasheets,
                "pdf_quality": pdf_quality,
                "theme_name": theme_name,
            }

            try:
                pdf_bytes = generate_offer_pdf(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info_for_pdf,
                    texts=texts,
                    theme_name=theme_name,
                    inclusion_options=inclusion_options,  # Erweiterte Optionen übergeben
                    section_order_df=active_sections_df,  # DataFrame statt Liste übergeben
                    custom_images_list=st.session_state.get("custom_images", []),
                    custom_text_blocks_list=st.session_state.get(
                        "custom_text_blocks", []
                    ),
                    side_by_side_sim_keys=side_by_side_sim_keys,
                    highlight_box_data={
                        "include": include_highlight_box,
                        "title": highlight_box_title,
                        "content": highlight_box_content,
                    },
                    get_product_by_id_func=get_product_by_id_func,
                    db_list_company_documents_func=db_list_company_documents_func,
                    active_company_id=company_info_for_pdf.get("id"),
                    # Erweiterte Template-Parameter
                    selected_title_image_b64=None,
                    selected_offer_title_text="Ihr individuelles Solaranlagen-Angebot",
                    selected_cover_letter_text="Sehr geehrte Damen und Herren,\n\nwir freuen uns, Ihnen unser maßgeschneidertes Angebot für Ihre Photovoltaikanlage zu präsentieren.",
                )
            except Exception as e:
                st.error(f"Fehler bei PDF-Generierung: {str(e)}")
                pdf_bytes = None

            if pdf_bytes:
                st.success(" PDF erfolgreich komponiert!")
                st.download_button(
                    label=" PDF Herunterladen",
                    data=pdf_bytes,
                    file_name=f"Angebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="secondary_pdf_download_btn",
                )
            else:
                st.error(" PDF-Erstellung fehlgeschlagen.")

    if "pdf_generating_lock_v1" not in st.session_state:
        st.session_state.pdf_generating_lock_v1 = False
    if "pdf_inclusion_options" not in st.session_state:
        st.session_state.pdf_inclusion_options = {
            "include_company_logo": True,
            "include_product_images": True,
            "include_all_documents": True,
            "company_document_ids_to_include": [],
            "selected_charts_for_pdf": [],
            "include_optional_component_details": True,
        }
    if "pdf_selected_main_sections" not in st.session_state:
        st.session_state.pdf_selected_main_sections = [
            "ProjectOverview",
            "TechnicalComponents",
            "CostDetails",
            "Economics",
            "SimulationDetails",
            "CO2Savings",
            "Visualizations",
            "FutureAspects",
        ]
    if "pdf_preset_name_input" not in st.session_state:
        st.session_state.pdf_preset_name_input = ""

    minimal_data_ok = True
    if not project_data or not isinstance(project_data, dict):
        project_data = {}
        minimal_data_ok = False
    customer_data_pdf = project_data.get("customer_data", {})
    project_details_pdf = project_data.get("project_details", {})
    if not (
        project_details_pdf.get("module_quantity")
        and (
            project_details_pdf.get("selected_module_id")
            or project_details_pdf.get("selected_module_name")
        )
        and (
            project_details_pdf.get("selected_inverter_id")
            or project_details_pdf.get("selected_inverter_name")
        )
    ):
        minimal_data_ok = False
    if not minimal_data_ok:
        st.info(
            get_text_pdf_ui(
                texts,
                "pdf_creation_minimal_data_missing_info",
                "Minimale Projektdaten...fehlen.",
            )
        )
        return
    if not analysis_results or not isinstance(analysis_results, dict):
        analysis_results = {}
        st.info(
            get_text_pdf_ui(
                texts,
                "pdf_creation_no_analysis_for_pdf_info",
                "Analyseergebnisse unvollständig...",
            )
        )

    active_company = get_active_company_details_func()
    company_info_for_pdf = (
        active_company if active_company else {"name": "Ihre Firma (Fallback)"}
    )
    company_logo_b64_for_pdf = (
        active_company.get("logo_base64") if active_company else None
    )
    active_company_id_for_docs = (
        active_company.get("id") if active_company else None
    )  # Korrigiert: None statt 0 als Fallback
    if "pdf_theme_name" not in st.session_state:
        st.session_state.pdf_theme_name = "Blau Elegant"
    if "custom_images" not in st.session_state:
        st.session_state.custom_images = []
    if "custom_text_blocks" not in st.session_state:
        st.session_state.custom_text_blocks = []

    if active_company:
        st.caption(
            f"Angebot für Firma: **{active_company.get('name', 'Unbekannt')}** (ID: {active_company_id_for_docs})"
        )
    else:
        st.warning("Keine aktive Firma ausgewählt. PDF verwendet Fallback-Daten.")

    # DATENSTATUS-ANZEIGE UND EMPFEHLUNGEN
    st.markdown("---")
    data_status = _show_pdf_data_status(project_data, analysis_results, texts)

    # Wenn kritische Daten fehlen, PDF-Formular nicht anzeigen
    if data_status == False:
        return
    elif data_status == "fallback":
        # Fallback-PDF erstellen
        try:
            from pdf_generator import _create_no_data_fallback_pdf

            customer_data = project_data.get("customer_data", {})
            fallback_pdf = _create_no_data_fallback_pdf(texts, customer_data)

            if fallback_pdf:
                st.success(" Einfaches Info-PDF erstellt!")
                st.download_button(
                    label=" Info-PDF herunterladen",
                    data=fallback_pdf,
                    file_name=f"PV_Info_{customer_data.get('last_name', 'Interessent')}.pdf",
                    mime="application/pdf",
                    key="fallback_pdf_download_btn",
                )
            else:
                st.error("Fehler beim Erstellen des Info-PDFs")
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Fallback-PDFs: {e}")
        return

    st.markdown("---")

    # Vorlagen und Presets laden
    (
        title_image_templates,
        offer_title_templates,
        cover_letter_templates,
        pdf_presets,
    ) = ([], [], [], [])
    try:
        title_image_templates = load_admin_setting_func("pdf_title_image_templates", [])
        offer_title_templates = load_admin_setting_func("pdf_offer_title_templates", [])
        cover_letter_templates = load_admin_setting_func(
            "pdf_cover_letter_templates", []
        )

        # KORREKTUR: `load_admin_setting_func` gibt bereits eine Liste zurück, wenn der Wert als JSON-Array gespeichert wurde.
        # Kein erneutes `json.loads` nötig.
        loaded_presets = load_admin_setting_func(
            "pdf_offer_presets", []
        )  # Standard ist eine leere Liste
        if isinstance(loaded_presets, list):
            pdf_presets = loaded_presets
        elif (
            isinstance(loaded_presets, str) and loaded_presets.strip()
        ):  # Fallback, falls doch als String gespeichert
            try:
                pdf_presets = json.loads(loaded_presets)
                if not isinstance(
                    pdf_presets, list
                ):  # Sicherstellen, dass es eine Liste ist
                    st.warning(
                        "PDF-Presets sind nicht im korrekten Listenformat gespeichert. Werden zurückgesetzt."
                    )
                    pdf_presets = []
            except json.JSONDecodeError:
                st.warning(
                    "Fehler beim Parsen der PDF-Presets aus der Datenbank. Werden zurückgesetzt."
                )
                pdf_presets = []
        else:  # Default, falls nichts geladen oder unerwarteter Typ
            pdf_presets = []

        # Typsicherheit für andere Vorlagen
        if not isinstance(title_image_templates, list):
            title_image_templates = []
        if not isinstance(offer_title_templates, list):
            offer_title_templates = []
        if not isinstance(cover_letter_templates, list):
            cover_letter_templates = []

    except Exception as e_load_data:
        st.error(f"Fehler beim Laden von PDF-Vorlagen oder Presets: {e_load_data}")
        # Fallback-Werte sicherstellen
        (
            title_image_templates,
            offer_title_templates,
            cover_letter_templates,
            pdf_presets,
        ) = ([], [], [], [])

    # ... (Rest der Funktion render_pdf_ui wie in der vorherigen Antwort) ...    # (Initialisierung Session State für Vorlagenauswahl, Definitionen für "Alles auswählen/abwählen", Callbacks, UI-Elemente)
    if "selected_title_image_name_doc_output" not in st.session_state:
        st.session_state.selected_title_image_name_doc_output = (
            title_image_templates[0]["name"]
            if title_image_templates and isinstance(title_image_templates[0], dict)
            else None
        )
    if "selected_title_image_b64_data_doc_output" not in st.session_state:
        st.session_state.selected_title_image_b64_data_doc_output = (
            title_image_templates[0]["data"]
            if title_image_templates and isinstance(title_image_templates[0], dict)
            else None
        )
    if "selected_offer_title_name_doc_output" not in st.session_state:
        st.session_state.selected_offer_title_name_doc_output = (
            offer_title_templates[0]["name"]
            if offer_title_templates and isinstance(offer_title_templates[0], dict)
            else None
        )
    if "selected_offer_title_text_content_doc_output" not in st.session_state:
        st.session_state.selected_offer_title_text_content_doc_output = (
            offer_title_templates[0]["content"]
            if offer_title_templates and isinstance(offer_title_templates[0], dict)
            else ""
        )
    if "selected_cover_letter_name_doc_output" not in st.session_state:
        st.session_state.selected_cover_letter_name_doc_output = (
            cover_letter_templates[0]["name"]
            if cover_letter_templates and isinstance(cover_letter_templates[0], dict)
            else None
        )
    if "selected_cover_letter_text_content_doc_output" not in st.session_state:
        st.session_state.selected_cover_letter_text_content_doc_output = (
            cover_letter_templates[0]["content"]
            if cover_letter_templates and isinstance(cover_letter_templates[0], dict)
            else ""
        )

    default_pdf_sections_map = all_pdf_sections  # Verwende die früh definierte Version
    all_main_section_keys = list(default_pdf_sections_map.keys())
    chart_key_to_friendly_name_map = {
        "monthly_prod_cons_chart_bytes": get_text_pdf_ui(
            texts,
            "pdf_chart_label_monthly_compare",
            "Monatl. Produktion/Verbrauch (2D)",
        ),
        "cost_projection_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_cost_projection", "Stromkosten-Hochrechnung (2D)"
        ),
        "cumulative_cashflow_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_cum_cashflow", "Kumulierter Cashflow (2D)"
        ),
        "consumption_coverage_pie_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_consum_coverage_pie", "Verbrauchsdeckung (Kreis)"
        ),
        "pv_usage_pie_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_pv_usage_pie", "PV-Nutzung (Kreis)"
        ),
        "daily_production_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_daily_3d", "Tagesproduktion (3D)"
        ),
        "weekly_production_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_weekly_3d", "Wochenproduktion (3D)"
        ),
        "yearly_production_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_yearly_3d_bar", "Jahresproduktion (3D-Balken)"
        ),
        "project_roi_matrix_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_roi_matrix_3d", "Projektrendite-Matrix (3D)"
        ),
        "feed_in_revenue_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_feedin_3d", "Einspeisevergütung (3D)"
        ),
        "prod_vs_cons_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_prodcons_3d", "Verbr. vs. Prod. (3D)"
        ),
        "tariff_cube_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_tariffcube_3d", "Tarifvergleich (3D)"
        ),
        "co2_savings_value_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_co2value_3d", "CO2-Ersparnis vs. Wert (3D)"
        ),
        "investment_value_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_investval_3D", "Investitionsnutzwert (3D)"
        ),
        "storage_effect_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_storageeff_3d", "Speicherwirkung (3D)"
        ),
        "selfuse_stack_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_selfusestack_3d", "Eigenverbr. vs. Einspeis. (3D)"
        ),
        "cost_growth_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_costgrowth_3d", "Stromkostensteigerung (3D)"
        ),
        "selfuse_ratio_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_selfuseratio_3d", "Eigenverbrauchsgrad (3D)"
        ),
        "roi_comparison_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_roicompare_3d", "ROI-Vergleich (3D)"
        ),
        "scenario_comparison_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_scenariocomp_3d", "Szenarienvergleich (3D)"
        ),
        "tariff_comparison_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_tariffcomp_3d", "Vorher/Nachher Stromkosten (3D)"
        ),
        "income_projection_switcher_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_incomeproj_3d", "Einnahmenprognose (3D)"
        ),
        "yearly_production_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_pvvis_yearly", "PV Visuals: Jahresproduktion"
        ),
        "break_even_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_pvvis_breakeven", "PV Visuals: Break-Even"
        ),
        "amortisation_chart_bytes": get_text_pdf_ui(
            texts, "pdf_chart_label_pvvis_amort", "PV Visuals: Amortisation"
        ),
    }
    all_available_chart_keys_for_selection = _get_all_available_chart_keys(
        analysis_results, chart_key_to_friendly_name_map
    )
    all_available_company_doc_ids_for_selection = _get_all_available_company_doc_ids(
        active_company_id_for_docs, db_list_company_documents_func
    )

    def select_all_options():
        st.session_state.pdf_inclusion_options["include_company_logo"] = True
        st.session_state.pdf_inclusion_options["include_product_images"] = True
        st.session_state.pdf_inclusion_options["include_all_documents"] = True
        st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = (
            all_available_company_doc_ids_for_selection[:]
        )
        st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = (
            all_available_chart_keys_for_selection[:]
        )
        st.session_state.pdf_inclusion_options["include_optional_component_details"] = (
            True
        )
        st.session_state.pdf_selected_main_sections = all_main_section_keys[:]
        st.success("Alle Optionen ausgewählt!")

    def deselect_all_options():
        st.session_state.pdf_inclusion_options["include_company_logo"] = False
        st.session_state.pdf_inclusion_options["include_product_images"] = False
        st.session_state.pdf_inclusion_options["include_all_documents"] = False
        st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = []
        st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = []
        st.session_state.pdf_inclusion_options["include_optional_component_details"] = (
            False
        )
        st.session_state.pdf_selected_main_sections = []
        st.success("Alle Optionen abgewählt!")

    def load_preset_on_click(preset_name_to_load: str):
        selected_preset = next(
            (p for p in pdf_presets if p["name"] == preset_name_to_load), None
        )
        if selected_preset and "selections" in selected_preset:
            selections = selected_preset["selections"]
            st.session_state.pdf_inclusion_options["include_company_logo"] = (
                selections.get("include_company_logo", True)
            )
            st.session_state.pdf_inclusion_options["include_product_images"] = (
                selections.get("include_product_images", True)
            )
            st.session_state.pdf_inclusion_options["include_all_documents"] = (
                selections.get("include_all_documents", False)
            )
            st.session_state.pdf_inclusion_options[
                "company_document_ids_to_include"
            ] = selections.get("company_document_ids_to_include", [])
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = (
                selections.get("selected_charts_for_pdf", [])
            )
            st.session_state.pdf_inclusion_options[
                "include_optional_component_details"
            ] = selections.get("include_optional_component_details", True)
            st.session_state.pdf_selected_main_sections = selections.get(
                "pdf_selected_main_sections", all_main_section_keys[:]
            )
            st.success(f"Vorlage '{preset_name_to_load}' geladen.")
        else:
            st.warning(
                f"Vorlage '{preset_name_to_load}' nicht gefunden oder fehlerhaft."
            )

    def save_current_selection_as_preset():
        preset_name = st.session_state.get("pdf_preset_name_input", "").strip()
        if not preset_name:
            st.error("Bitte einen Namen für die Vorlage eingeben.")
            return
        if any(p["name"] == preset_name for p in pdf_presets):
            st.warning(f"Eine Vorlage mit dem Namen '{preset_name}' existiert bereits.")
            return
        current_selections = {
            "include_company_logo": st.session_state.pdf_inclusion_options.get(
                "include_company_logo"
            ),
            "include_product_images": st.session_state.pdf_inclusion_options.get(
                "include_product_images"
            ),
            "include_all_documents": st.session_state.pdf_inclusion_options.get(
                "include_all_documents"
            ),
            "company_document_ids_to_include": st.session_state.pdf_inclusion_options.get(
                "company_document_ids_to_include"
            ),
            "selected_charts_for_pdf": st.session_state.pdf_inclusion_options.get(
                "selected_charts_for_pdf"
            ),
            "include_optional_component_details": st.session_state.pdf_inclusion_options.get(
                "include_optional_component_details"
            ),
            "pdf_selected_main_sections": st.session_state.get(
                "pdf_selected_main_sections"
            ),
        }
        new_preset = {"name": preset_name, "selections": current_selections}
        updated_presets = pdf_presets + [new_preset]
        try:
            if save_admin_setting_func(
                "pdf_offer_presets", json.dumps(updated_presets)
            ):
                st.success(f"Vorlage '{preset_name}' erfolgreich gespeichert!")
                st.session_state.pdf_preset_name_input = ""
                # Um die Liste der Presets im Selectbox zu aktualisieren, ist ein Rerun nötig.
                # Dies geschieht, wenn das Hauptformular abgesendet wird oder durch eine andere Interaktion.
                # Alternativ könnte man hier ein st.rerun() erzwingen, aber das kann die Formularinteraktion stören.
            else:
                st.error(
                    "Fehler beim Speichern der Vorlage in den Admin-Einstellungen."
                )
        except Exception as e_save_preset:
            st.error(f"Fehler beim Speichern der Vorlage: {e_save_preset}")

    st.markdown("---")
    st.subheader(
        get_text_pdf_ui(
            texts, "pdf_template_management_header", "Vorlagen & Schnellauswahl"
        )
    )
    col_preset1, col_preset2 = st.columns([3, 2])
    with col_preset1:
        preset_names = [
            p["name"] for p in pdf_presets if isinstance(p, dict) and "name" in p
        ]
        if preset_names:
            selected_preset_name_to_load = st.selectbox(
                get_text_pdf_ui(texts, "pdf_load_preset_label", "Vorlage laden"),
                options=[
                    get_text_pdf_ui(
                        texts, "pdf_no_preset_selected_option", "-- Keine Vorlage --"
                    )
                ]
                + preset_names,
                key="pdf_preset_load_select_v1_stable",
            )
            if selected_preset_name_to_load != get_text_pdf_ui(
                texts, "pdf_no_preset_selected_option", "-- Keine Vorlage --"
            ):
                if st.button(
                    get_text_pdf_ui(
                        texts,
                        "pdf_load_selected_preset_button",
                        "Ausgewählte Vorlage anwenden",
                    ),
                    key="pdf_load_preset_btn_v1_stable",
                    on_click=load_preset_on_click,
                    args=(selected_preset_name_to_load,),
                ):
                    pass
        else:
            st.caption(
                get_text_pdf_ui(
                    texts,
                    "pdf_no_presets_available_caption",
                    "Keine Vorlagen gespeichert.",
                )
            )
    with col_preset2:
        st.text_input(
            get_text_pdf_ui(
                texts, "pdf_new_preset_name_label", "Name für neue Vorlage"
            ),
            key="pdf_preset_name_input",
        )
        st.button(
            get_text_pdf_ui(
                texts, "pdf_save_current_selection_button", "Aktuelle Auswahl speichern"
            ),
            on_click=save_current_selection_as_preset,
            key="pdf_save_preset_btn_v1_stable",
        )
    col_global_select1, col_global_select2 = st.columns(2)
    with col_global_select1:
        st.button(
            f" {get_text_pdf_ui(texts, 'pdf_select_all_button', 'Alle Optionen auswählen')}",
            on_click=select_all_options,
            key="pdf_select_all_btn_v1_stable",
            use_container_width=True,
        )
    with col_global_select2:
        st.button(
            f" {get_text_pdf_ui(texts, 'pdf_deselect_all_button', 'Alle Optionen abwählen')}",
            on_click=deselect_all_options,
            key="pdf_deselect_all_btn_v1_stable",
            use_container_width=True,
        )
    st.markdown("---")

    # Hauptformular
    # ... (Rest des Formulars und der PDF-Generierungslogik wie in der vorherigen Antwort, mit der Korrektur für st.form_submit_button) ...
    form_submit_key = "pdf_final_submit_btn_v13_corrected_again"
    submit_button_disabled = st.session_state.pdf_generating_lock_v1
    with st.form(
        key="pdf_generation_form_v13_final_locked_options_main", clear_on_submit=False
    ):
        st.subheader(get_text_pdf_ui(texts, "pdf_config_header", "PDF-Konfiguration"))
        with st.container():
            st.markdown(
                "**"
                + get_text_pdf_ui(
                    texts,
                    "pdf_template_selection_info",
                    "Vorlagen für das Angebot auswählen",
                )
                + "**"
            )
            title_image_options = {
                t.get("name", f"Bild {i+1}"): t.get("data")
                for i, t in enumerate(title_image_templates)
                if isinstance(t, dict) and t.get("name")
            }
            if not title_image_options:
                title_image_options = {
                    get_text_pdf_ui(
                        texts,
                        "no_title_images_available",
                        "Keine Titelbilder verfügbar",
                    ): None
                }
            title_image_keys = list(title_image_options.keys())
            idx_title_img = (
                title_image_keys.index(
                    st.session_state.selected_title_image_name_doc_output
                )
                if st.session_state.selected_title_image_name_doc_output
                in title_image_keys
                else 0
            )
            selected_title_image_name = st.selectbox(
                get_text_pdf_ui(texts, "pdf_select_title_image", "Titelbild auswählen"),
                options=title_image_keys,
                index=idx_title_img,
                key="pdf_title_image_select_v13_form",
            )
            if (
                selected_title_image_name
                != st.session_state.selected_title_image_name_doc_output
            ):
                st.session_state.selected_title_image_name_doc_output = (
                    selected_title_image_name
                )
                st.session_state.selected_title_image_b64_data_doc_output = (
                    title_image_options.get(selected_title_image_name)
                )
            offer_title_options = {
                t.get("name", f"Titel {i+1}"): t.get("content")
                for i, t in enumerate(offer_title_templates)
                if isinstance(t, dict) and t.get("name")
            }
            if not offer_title_options:
                offer_title_options = {
                    get_text_pdf_ui(
                        texts,
                        "no_offer_titles_available",
                        "Keine Angebotstitel verfügbar",
                    ): "Standard Angebotstitel"
                }
            offer_title_keys = list(offer_title_options.keys())
            idx_offer_title = (
                offer_title_keys.index(
                    st.session_state.selected_offer_title_name_doc_output
                )
                if st.session_state.selected_offer_title_name_doc_output
                in offer_title_keys
                else 0
            )
            selected_offer_title_name = st.selectbox(
                get_text_pdf_ui(
                    texts, "pdf_select_offer_title", "Überschrift/Titel auswählen"
                ),
                options=offer_title_keys,
                index=idx_offer_title,
                key="pdf_offer_title_select_v13_form",
            )
            if (
                selected_offer_title_name
                != st.session_state.selected_offer_title_name_doc_output
            ):
                st.session_state.selected_offer_title_name_doc_output = (
                    selected_offer_title_name
                )
                st.session_state.selected_offer_title_text_content_doc_output = (
                    offer_title_options.get(selected_offer_title_name, "")
                )
            cover_letter_options = {
                t.get("name", f"Anschreiben {i+1}"): t.get("content")
                for i, t in enumerate(cover_letter_templates)
                if isinstance(t, dict) and t.get("name")
            }
            if not cover_letter_options:
                cover_letter_options = {
                    get_text_pdf_ui(
                        texts,
                        "no_cover_letters_available",
                        "Keine Anschreiben verfügbar",
                    ): "Standard Anschreiben"
                }
            cover_letter_keys = list(cover_letter_options.keys())
            idx_cover_letter = (
                cover_letter_keys.index(
                    st.session_state.selected_cover_letter_name_doc_output
                )
                if st.session_state.selected_cover_letter_name_doc_output
                in cover_letter_keys
                else 0
            )
            selected_cover_letter_name = st.selectbox(
                get_text_pdf_ui(
                    texts, "pdf_select_cover_letter", "Anschreiben auswählen"
                ),
                options=cover_letter_keys,
                index=idx_cover_letter,
                key="pdf_cover_letter_select_v13_form",
            )
            if (
                selected_cover_letter_name
                != st.session_state.selected_cover_letter_name_doc_output
            ):
                st.session_state.selected_cover_letter_name_doc_output = (
                    selected_cover_letter_name
                )
                st.session_state.selected_cover_letter_text_content_doc_output = (
                    cover_letter_options.get(selected_cover_letter_name, "")
                )
        st.markdown("---")
        st.markdown(
            "**"
            + get_text_pdf_ui(
                texts, "pdf_content_selection_info", "Inhalte für das PDF auswählen"
            )
            + "**"
        )
        col_pdf_content1_form, col_pdf_content2_form, col_pdf_content3_form = (
            st.columns(3)
        )
        with col_pdf_content1_form:
            st.session_state.pdf_inclusion_options["include_company_logo"] = (
                st.checkbox(
                    get_text_pdf_ui(
                        texts, "pdf_include_company_logo_label", "Firmenlogo anzeigen?"
                    ),
                    value=st.session_state.pdf_inclusion_options.get(
                        "include_company_logo", True
                    ),
                    key="pdf_cb_logo_v13_form_main_stable",
                )
            )
            st.session_state.pdf_inclusion_options["include_product_images"] = (
                st.checkbox(
                    get_text_pdf_ui(
                        texts,
                        "pdf_include_product_images_label",
                        "Produktbilder anzeigen? (Haupt & Zubehör)",
                    ),
                    value=st.session_state.pdf_inclusion_options.get(
                        "include_product_images", True
                    ),
                    key="pdf_cb_prod_img_v13_form_main_stable",
                )
            )
            st.session_state.pdf_inclusion_options[
                "include_optional_component_details"
            ] = st.checkbox(
                get_text_pdf_ui(
                    texts,
                    "pdf_include_optional_component_details_label",
                    "Details zu optionalen Komponenten anzeigen?",
                ),
                value=st.session_state.pdf_inclusion_options.get(
                    "include_optional_component_details", True
                ),
                key="pdf_cb_opt_comp_details_v13_form_main_stable",
            )
            st.session_state.pdf_inclusion_options["include_all_documents"] = (
                st.checkbox(
                    get_text_pdf_ui(
                        texts,
                        "pdf_include_all_documents_label",
                        "Alle Datenblätter & ausgew. Firmendokumente anhängen?",
                    ),
                    value=st.session_state.pdf_inclusion_options.get(
                        "include_all_documents", True
                    ),
                    key="pdf_cb_all_docs_v13_form_main_stable",
                )
            )
            st.markdown(
                "**"
                + get_text_pdf_ui(
                    texts,
                    "pdf_options_select_company_docs",
                    "Spezifische Firmendokumente für Anhang",
                )
                + "**"
            )
            if (
                active_company_id_for_docs is not None
                and isinstance(active_company_id_for_docs, int)
                and callable(db_list_company_documents_func)
            ):
                company_docs_list_form = db_list_company_documents_func(
                    active_company_id_for_docs, None
                )
                if company_docs_list_form:
                    current_selected_doc_ids_form = (
                        st.session_state.pdf_inclusion_options.get(
                            "company_document_ids_to_include", []
                        )
                    )
                    # Die temporäre Liste wird nicht mehr benötigt, da Checkboxen direkt den Session State beeinflussen (müssten, oder hier gesammelt)
                    # Für die on_click Callbacks der globalen Buttons ist es besser, wenn Checkboxen direkt den State widerspiegeln.
                    # Aber für den Form-Submit sammeln wir die Werte NEU basierend auf den aktuellen Checkbox-Zuständen im Formular.
                    selected_doc_ids_in_form = []
                    for doc_item_form in company_docs_list_form:
                        if isinstance(doc_item_form, dict) and "id" in doc_item_form:
                            doc_id_item_form = doc_item_form["id"]
                            doc_label_item_form = f"{doc_item_form.get('display_name', doc_item_form.get('file_name', 'Unbenannt'))} ({doc_item_form.get('document_type')})"
                            if st.checkbox(
                                doc_label_item_form,
                                value=(
                                    doc_id_item_form in current_selected_doc_ids_form
                                ),
                                key=f"pdf_cb_company_doc_form_{doc_id_item_form}_v13_stable",
                            ):
                                selected_doc_ids_in_form.append(doc_id_item_form)
                    # Dieser Wert wird beim Submit verwendet
                    st.session_state.pdf_inclusion_options[
                        "_temp_company_document_ids_to_include"
                    ] = selected_doc_ids_in_form
                else:
                    st.caption(
                        get_text_pdf_ui(
                            texts,
                            "pdf_no_company_documents_available",
                            "Keine Dokumente für Firma hinterlegt.",
                        )
                    )
            else:
                st.caption(
                    get_text_pdf_ui(
                        texts,
                        "pdf_select_active_company_for_docs",
                        "Aktive Firma nicht korrekt.",
                    )
                )
        with col_pdf_content2_form:
            st.markdown(
                "**"
                + get_text_pdf_ui(
                    texts,
                    "pdf_options_column_main_sections",
                    "Hauptsektionen im Angebot",
                )
                + "**"
            )
            current_selected_main_sections_in_state_form = st.session_state.get(
                "pdf_selected_main_sections", all_main_section_keys[:]
            )
            selected_sections_in_form = []
            for (
                section_key_form,
                section_label_from_map_form,
            ) in default_pdf_sections_map.items():
                if st.checkbox(
                    section_label_from_map_form,
                    value=(
                        section_key_form in current_selected_main_sections_in_state_form
                    ),
                    key=f"pdf_section_cb_form_{section_key_form}_v13_stable",
                ):
                    selected_sections_in_form.append(section_key_form)
            st.session_state["_temp_pdf_selected_main_sections"] = (
                selected_sections_in_form
            )
        with col_pdf_content3_form:
            st.markdown(
                "**"
                + get_text_pdf_ui(
                    texts, "pdf_options_column_charts", "Diagramme & Visualisierungen"
                )
                + "**"
            )
            if analysis_results and isinstance(analysis_results, dict):
                available_chart_keys_form = _get_all_available_chart_keys(
                    analysis_results, chart_key_to_friendly_name_map
                )
                ordered_display_keys_form = [
                    k_map
                    for k_map in chart_key_to_friendly_name_map.keys()
                    if k_map in available_chart_keys_form
                ]
                for k_avail_form in available_chart_keys_form:
                    if k_avail_form not in ordered_display_keys_form:
                        ordered_display_keys_form.append(k_avail_form)
                current_selected_charts_in_state_form = (
                    st.session_state.pdf_inclusion_options.get(
                        "selected_charts_for_pdf", []
                    )
                )
                selected_charts_in_form = []
                for chart_key_form in ordered_display_keys_form:
                    friendly_name_form = chart_key_to_friendly_name_map.get(
                        chart_key_form,
                        chart_key_form.replace("_chart_bytes", "")
                        .replace("_", " ")
                        .title(),
                    )
                    if st.checkbox(
                        friendly_name_form,
                        value=(chart_key_form in current_selected_charts_in_state_form),
                        key=f"pdf_include_chart_form_{chart_key_form}_v13_stable",
                    ):
                        selected_charts_in_form.append(chart_key_form)
                st.session_state.pdf_inclusion_options[
                    "_temp_selected_charts_for_pdf"
                ] = selected_charts_in_form
            else:
                st.caption(
                    get_text_pdf_ui(
                        texts,
                        "pdf_no_charts_to_select",
                        "Keine Diagrammdaten für PDF-Auswahl.",
                    )
                )
        st.markdown("---")
        submitted_generate_pdf = st.form_submit_button(
            label=f"**{get_text_pdf_ui(texts, 'pdf_generate_button', 'Angebots-PDF erstellen')}**",
            type="primary",
            disabled=submit_button_disabled,
        )
        if (
            submitted_generate_pdf
        ):  # Werte aus temporären Keys in die Haupt-Session-State-Keys übernehmen
            st.session_state.pdf_inclusion_options[
                "company_document_ids_to_include"
            ] = st.session_state.pdf_inclusion_options.pop(
                "_temp_company_document_ids_to_include", []
            )
            st.session_state.pdf_selected_main_sections = st.session_state.pop(
                "_temp_pdf_selected_main_sections", []
            )
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = (
                st.session_state.pdf_inclusion_options.pop(
                    "_temp_selected_charts_for_pdf", []
                )
            )

    if submitted_generate_pdf and not st.session_state.pdf_generating_lock_v1:
        st.session_state.pdf_generating_lock_v1 = True
        pdf_bytes = None
        try:  # Datenvalidierung vor PDF-Erstellung
            try:
                from pdf_generator import (
                    _validate_pdf_data_availability,
                    _create_no_data_fallback_pdf,
                )

                validation_result = _validate_pdf_data_availability(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    texts=texts,
                )

                # Zeige Validierungsstatus an
                if not validation_result["is_valid"]:
                    st.warning(
                        f" Unvollständige Daten erkannt: {', '.join(validation_result['missing_data_summary'])}"
                    )
                    st.info("Ein vereinfachtes Informations-PDF wird erstellt.")

                    if validation_result["critical_errors"] > 0:
                        st.error(
                            f" {validation_result['critical_errors']} kritische Fehler gefunden. Erstelle Fallback-PDF..."
                        )

                        # Erstelle Fallback-PDF
                        pdf_bytes = create_fallback_pdf(
                            issues=validation_result["missing_data"],
                            warnings=validation_result["warnings"],
                            texts=texts,
                        )
                        st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
                        st.success(" Fallback-PDF erfolgreich erstellt!")
                        return
                    else:
                        st.info(
                            f"ℹ {validation_result['warnings']} Warnungen. PDF wird mit verfügbaren Daten erstellt."
                        )
                else:
                    st.success(" Alle Daten vollständig verfügbar.")

            except ImportError:
                st.warning(
                    "Datenvalidierung nicht verfügbar. Fahre mit normaler PDF-Erstellung fort."
                )

            with st.spinner(
                get_text_pdf_ui(
                    texts,
                    "pdf_generation_spinner",
                    "PDF wird generiert, bitte warten...",
                )
            ):
                final_inclusion_options_to_pass = (
                    st.session_state.pdf_inclusion_options.copy()
                )
                final_sections_to_include_to_pass = (
                    st.session_state.pdf_selected_main_sections[:]
                )
                pdf_bytes = _generate_offer_pdf_safe(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info_for_pdf,
                    company_logo_base64=company_logo_b64_for_pdf,
                    selected_title_image_b64=st.session_state.selected_title_image_b64_data_doc_output,
                    selected_offer_title_text=st.session_state.selected_offer_title_text_content_doc_output,
                    selected_cover_letter_text=st.session_state.selected_cover_letter_text_content_doc_output,
                    sections_to_include=final_sections_to_include_to_pass,
                    inclusion_options=final_inclusion_options_to_pass,
                    load_admin_setting_func=load_admin_setting_func,
                    save_admin_setting_func=save_admin_setting_func,
                    list_products_func=list_products_func,
                    get_product_by_id_func=get_product_by_id_func,
                    db_list_company_documents_func=db_list_company_documents_func,
                    active_company_id=active_company_id_for_docs,
                    texts=texts,
                )
            st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
        except Exception as e_gen_final_outer:
            st.error(
                f"{get_text_pdf_ui(texts, 'pdf_generation_exception_outer', 'Kritischer Fehler im PDF-Prozess (pdf_ui.py):')} {e_gen_final_outer}"
            )
            st.text_area(
                "Traceback PDF Erstellung (pdf_ui.py):",
                traceback.format_exc(),
                height=250,
            )
            st.session_state.generated_pdf_bytes_for_download_v1 = None
        finally:
            st.session_state.pdf_generating_lock_v1 = False
            st.session_state.selected_page_key_sui = "doc_output"
            st.rerun()
    if "generated_pdf_bytes_for_download_v1" in st.session_state:
        pdf_bytes_to_download = st.session_state.pop(
            "generated_pdf_bytes_for_download_v1"
        )
        if pdf_bytes_to_download and isinstance(pdf_bytes_to_download, bytes):
            customer_name_for_file = customer_data_pdf.get("last_name", "Angebot")
            file_name_customer_part = (
                str(customer_name_for_file).replace(" ", "_")
                if customer_name_for_file and str(customer_name_for_file).strip()
                else "Photovoltaik_Angebot"
            )
            timestamp_file = base64.b32encode(os.urandom(5)).decode("utf-8").lower()
            file_name = f"Angebot_{file_name_customer_part}_{timestamp_file}.pdf"
            st.success(
                get_text_pdf_ui(
                    texts, "pdf_generation_success", "PDF erfolgreich erstellt!"
                )
            )
            st.download_button(
                label=get_text_pdf_ui(
                    texts, "pdf_download_button", "PDF herunterladen"
                ),
                data=pdf_bytes_to_download,
                file_name=file_name,
                mime="application/pdf",
                key=f"pdf_download_btn_final_{timestamp_file}_v13_final_stable",
            )
        elif pdf_bytes_to_download is None and not st.session_state.get(
            "pdf_generating_lock_v1", True
        ):
            st.error(
                get_text_pdf_ui(
                    texts,
                    "pdf_generation_failed_no_bytes_after_rerun",
                    "PDF-Generierung fehlgeschlagen (keine Daten nach Rerun).",
                )
            )


# NEU: PDF-VORSCHAU & BEARBEITUNG FUNKTION (BOMBE!)
def show_advanced_pdf_preview(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    texts: Dict[str, str],
    load_admin_setting_func: Callable = _dummy_load_admin_setting_pdf_ui,
    save_admin_setting_func: Callable = _dummy_save_admin_setting_pdf_ui,
    get_active_company_details_func: Callable = _dummy_get_active_company_details,
    list_products_func: Callable = lambda: [],
    get_product_by_id_func: Callable = lambda x: {},
    db_list_company_documents_func: Callable = _dummy_list_company_documents,
) -> Optional[bytes]:
    """
    Erweiterte PDF-Vorschau mit Bearbeitungsmöglichkeiten und Seitenreihenfolge.
    Das wird BOMBE! 

    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        texts: Übersetzungstexte
        ... weitere Callback-Funktionen

    Returns:
        PDF-Bytes falls erfolgreich generiert, sonst None
    """

    if not _PDF_PREVIEW_AVAILABLE:
        st.error(" PDF-Vorschau-Modul ist nicht verfügbar!")
        st.info(
            " Installieren Sie die erforderlichen Abhängigkeiten für die PDF-Vorschau."
        )
        return None

    # Firmendaten abrufen
    company_details = get_active_company_details_func()
    if not company_details:
        st.warning(" Keine aktive Firma gefunden. Verwende Standardwerte.")
        company_details = {
            "name": "Ihre Solarfirma",
            "street": "Musterstraße 1",
            "zip_code": "12345",
            "city": "Musterstadt",
            "phone": "+49 123 456789",
            "email": "info@ihresolarfirma.de",
            "id": 1,
        }

    company_logo_base64 = company_details.get("logo_base64")

    # PDF-Vorschau-Interface aufrufen
    return show_pdf_preview_interface(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_details,
        company_logo_base64=company_logo_base64,
        texts=texts,
        generate_pdf_func=lambda **kwargs: _generate_offer_pdf_safe(
            load_admin_setting_func=load_admin_setting_func,
            save_admin_setting_func=save_admin_setting_func,
            list_products_func=list_products_func,
            get_product_by_id_func=get_product_by_id_func,
            db_list_company_documents_func=db_list_company_documents_func,
            active_company_id=company_details.get("id", 1),
            **kwargs,
        ),
    )


# --- Debug-Bereich für PDF-Anhänge ---
def render_pdf_debug_section(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    get_active_company_details_func: Callable,
    db_list_company_documents_func: Callable,
    get_product_by_id_func: Callable,
):
    """Rendert einen Debug-Bereich für PDF-Anhänge"""
    with st.expander(" Debug: PDF-Anhänge-Prüfung", expanded=False):
        st.subheader("Systemstatus")

        # PyPDF Verfügbarkeit prüfen
        try:
            from pypdf import PdfReader, PdfWriter

            pypdf_status = " pypdf verfügbar"
        except ImportError:
            try:
                from PyPDF2 import PdfReader, PdfWriter

                pypdf_status = " PyPDF2 verfügbar (Fallback)"
            except ImportError:
                pypdf_status = " Keine PDF-Bibliothek verfügbar"

        st.write(f"**PDF-Bibliothek:** {pypdf_status}")

        # Aktive Firma prüfen
        active_company = get_active_company_details_func()
        if active_company:
            st.write(
                f"**Aktive Firma:** {active_company.get('name')} (ID: {active_company.get('id')})"
            )

            # Firmendokumente prüfen
            company_docs = db_list_company_documents_func(
                active_company.get("id"), None
            )
            st.write(f"**Verfügbare Firmendokumente:** {len(company_docs)}")
            for doc in company_docs:
                doc_path = os.path.join(
                    os.getcwd(), "data", "company_docs", doc.get("relative_db_path", "")
                )
                status = "" if os.path.exists(doc_path) else ""
                st.write(f"  {status} {doc.get('display_name')} (ID: {doc.get('id')})")
        else:
            st.write("**Aktive Firma:**  Keine aktive Firma")

        # Projektdetails prüfen
        project_details = project_data.get("project_details", {})
        st.write("**Ausgewählte Produkte:**")

        product_ids = [
            ("Modul", project_details.get("selected_module_id")),
            ("Wechselrichter", project_details.get("selected_inverter_id")),
            (
                "Batteriespeicher",
                (
                    project_details.get("selected_storage_id")
                    if project_details.get("include_storage")
                    else None
                ),
            ),
        ]

        for comp_type, prod_id in product_ids:
            if prod_id:
                try:
                    product_info = get_product_by_id_func(prod_id)
                    if product_info:
                        datasheet_path = product_info.get("datasheet_link_db_path")
                        if datasheet_path:
                            full_path = os.path.join(
                                os.getcwd(),
                                "data",
                                "product_datasheets",
                                datasheet_path,
                            )
                            status = "" if os.path.exists(full_path) else ""
                            st.write(
                                f"  {status} {comp_type}: {product_info.get('model_name')} (ID: {prod_id})"
                            )
                            if not os.path.exists(full_path):
                                st.write(f"     Datenblatt fehlt: {full_path}")
                        else:
                            st.write(
                                f"   {comp_type}: {product_info.get('model_name')} (Kein Datenblatt-Pfad)"
                            )
                    else:
                        st.write(
                            f"   {comp_type}: Produkt ID {prod_id} nicht in DB gefunden"
                        )
                except Exception as e:
                    st.write(
                        f"   {comp_type}: Fehler beim Laden von ID {prod_id}: {e}"
                    )
            else:
                st.write(f"  - {comp_type}: Nicht ausgewählt")

        # Current PDF inclusion options anzeigen
        st.subheader("Aktuelle PDF-Einstellungen")
        if "pdf_inclusion_options" in st.session_state:
            options = st.session_state.pdf_inclusion_options
            st.json(options)
        else:
            st.write("Keine PDF-Einstellungen in Session State")


def render_tom90_pdf_section(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]],
    get_product_by_id_func: Callable,
):
    """
    Rendert den TOM-90 PDF-Bereich mit allen verfügbaren Funktionen.
    """
    st.markdown("---")
    st.subheader(" TOM-90 Modernes PDF Layout")
    st.info(
        "Dies ist ein Testbereich für das neue TOM-90 Layout mit modularer Struktur."
    )

    # === SESSION STATE VALIDATION FÜR TOM-90 ===
    # Erneute Validierung der Daten für TOM-90 spezifisch
    if not analysis_results or len(analysis_results) == 0:
        st.error(
            " TOM-90: Keine Analyseergebnisse verfügbar. Versuche Wiederherstellung..."
        )

        # Versuche aus Backup zu laden
        backup_analysis = st.session_state.get("pdf_generation_analysis_backup", {})
        session_analysis = st.session_state.get("calculation_results", {})

        if backup_analysis and len(backup_analysis) > 0:
            analysis_results = backup_analysis
            st.success(" TOM-90: Analyseergebnisse aus PDF-Backup wiederhergestellt!")
        elif session_analysis and len(session_analysis) > 0:
            analysis_results = session_analysis
            st.success(
                " TOM-90: Analyseergebnisse aus Session State wiederhergestellt!"
            )
        else:
            st.error(
                " TOM-90: Keine Daten verfügbar. Bitte führen Sie zuerst eine Berechnung durch."
            )
            return

    if not project_data or len(project_data) == 0:
        st.error(
            " TOM-90: Keine Projektdaten verfügbar. Versuche Wiederherstellung..."
        )

        backup_project = st.session_state.get("pdf_generation_project_backup", {})
        session_project = st.session_state.get("project_data", {})

        if backup_project and len(backup_project) > 0:
            project_data = backup_project
            st.success(" TOM-90: Projektdaten aus PDF-Backup wiederhergestellt!")
        elif session_project and len(session_project) > 0:
            project_data = session_project
            st.success(" TOM-90: Projektdaten aus Session State wiederhergestellt!")
        else:
            st.error(
                " TOM-90: Keine Projektdaten verfügbar. Bitte konfigurieren Sie zuerst ein Projekt."
            )
            return

    # Layout-Optionen für TOM-90
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("####  Design-Einstellungen")

        # Primärfarbe wählen
        primary_color = st.color_picker(
            "Primärfarbe für Überschriften und Akzente",
            value="#003366",
            help="Wählen Sie die Hauptfarbe des PDF-Layouts (z.B. Unternehmensfarbe).",
        )

        # Theme auswählen
        theme_name = st.selectbox(
            "PDF-Theme auswählen",
            options=["Blau Elegant", "Öko Grün", "Salt & Pepper"],
            index=0,
            help="Wählen Sie das grundlegende Farbschema für das PDF.",
        )

        # Titel-Optionen
        offer_title = st.text_input(
            "Angebots-Titel",
            value="Ihr Angebot für eine moderne Photovoltaikanlage",
            help="Haupttitel auf der ersten Seite",
        )

    with col2:
        st.markdown("####  Inhalt-Einstellungen")

        # Block-Auswahl für TOM-90
        include_have_you_known = st.checkbox(
            " Infobox 'Haben Sie gewusst?' einfügen",
            value=True,
            help="Interessante Fakten zu Photovoltaik",
        )

        include_financing = st.checkbox(
            " Finanzierungsvergleich (Kurzfassung) einfügen",
            value=True,
            help="Kurze Übersicht der Finanzierungsoptionen",
        )

        include_savings_summary = st.checkbox(
            " Ersparnis-Zusammenfassung einfügen",
            value=True,
            help="Übersicht der erwarteten Ersparnisse",
        )

        include_financing_details = st.checkbox(
            " Detaillierte Finanzierungsberechnungen einfügen",
            value=True,
            help="Umfassende Finanzierungsanalyse",
        )

    # Finanzierungsdetails (nur wenn Hauptschalter aktiv)
    if include_financing_details:
        st.markdown("####  Finanzierungsdetails")
        col3, col4 = st.columns(2)

        with col3:
            include_annuity = st.checkbox("Annuitätendarlehen", value=True)
            include_leasing = st.checkbox("Leasing", value=True)
            include_depreciation = st.checkbox("Abschreibung", value=True)

        with col4:
            include_comparison = st.checkbox(
                "Finanzierungsvergleich (Detail)", value=True
            )
            include_tax = st.checkbox("Kapitalertragsteuer", value=True)
            include_contracting = st.checkbox("Contracting", value=True)

    # Layout-Optionen
    st.markdown("####  Layout-Optionen")
    col5, col6 = st.columns(2)

    with col5:
        include_page_logo = st.checkbox("Firmenlogo unten links anzeigen", value=True)
        include_page_numbers = st.checkbox("Seitenzahlen anzeigen", value=True)

    with col6:
        # Weitere Layout-Optionen können hier hinzugefügt werden
        pass

    # Benutzerdefinierte Inhalte
    st.markdown("####  Benutzerdefinierte Inhalte")

    # Textfelder
    with st.expander(" Eigene Textblöcke hinzufügen"):
        custom_texts = []
        for i in range(2):  # Bis zu 2 Textblöcke
            title_key = f"tom90_title_{i}"
            body_key = f"tom90_body_{i}"

            title = st.text_input(f"Titel {i+1}", value="", key=title_key)
            body = st.text_area(f"Text {i+1}", value="", key=body_key)

            if title or body:
                custom_texts.append({"title": title, "body": body})

    # Bilder
    with st.expander(" Eigene Bilder hinzufügen"):
        custom_images = []
        custom_captions = []
        for i in range(2):  # Bis zu 2 Bilder
            uploaded = st.file_uploader(
                f"Bild {i+1} hochladen",
                type=["png", "jpg", "jpeg"],
                key=f"tom90_img_{i}",
            )
            if uploaded is not None:
                data = uploaded.read()
                if data:
                    custom_images.append(base64.b64encode(data).decode("utf-8"))
                    caption = st.text_input(
                        f"Bildunterschrift {i+1}", value="", key=f"tom90_caption_{i}"
                    )
                    custom_captions.append(caption)

    # Diagramm-Beschreibungen
    with st.expander(" Diagramm-Beschreibungen anpassen"):
        desc_donut = st.text_area(
            "Beschreibung für Donut-Charts",
            value="Diese Grafiken zeigen die Verteilung des erzeugten Solarstroms.",
            key="tom90_desc_donut",
        )
        desc_bar = st.text_area(
            "Beschreibung für Balkendiagramm",
            value="Das Balkendiagramm stellt die Wirtschaftlichkeit über die Jahre dar.",
            key="tom90_desc_bar",
        )
        desc_prod = st.text_area(
            "Beschreibung für Produktions/Verbrauchs-Diagramm",
            value="Hier sehen Sie den Vergleich zwischen PV-Produktion und Ihrem Stromverbrauch.",
            key="tom90_desc_prod",
        )

    # PDF Generierung
    st.markdown("---")
    st.subheader(" PDF Generierung")

    if st.button(" TOM-90 PDF erstellen", type="primary", use_container_width=True):
        with st.spinner("Erstelle TOM-90 PDF..."):
            try:
                # Sammle alle Optionen
                inclusion_options = {
                    "include_have_you_known": include_have_you_known,
                    "include_financing": include_financing,
                    "include_savings_summary": include_savings_summary,
                    "include_financing_details": include_financing_details,
                    "include_page_logo": include_page_logo,
                    "include_page_numbers": include_page_numbers,
                }

                # Finanzierungsdetails hinzufügen falls aktiv
                if include_financing_details:
                    inclusion_options.update(
                        {
                            "include_financing_details_annuity": include_annuity,
                            "include_financing_details_leasing": include_leasing,
                            "include_financing_details_depreciation": include_depreciation,
                            "include_financing_details_comparison": include_comparison,
                            "include_financing_details_tax": include_tax,
                            "include_financing_details_contracting": include_contracting,
                        }
                    )

                # Benutzerdefinierte Inhalte
                texts_for_pdf = {
                    "custom_texts": custom_texts,
                    "custom_images": custom_images,
                    "custom_image_captions": custom_captions,
                    "description_donut_charts": desc_donut,
                    "description_bar_chart": desc_bar,
                    "description_prod_vs_cons_chart": desc_prod,
                }

                # Firmeninformationen laden
                company_info = get_active_company_details_func()

                # PDF generieren
                pdf_bytes = generate_tom90_offer_pdf(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info or {},
                    company_logo_base64=None,  # Wird aus company_info geladen
                    selected_title_image_b64=None,
                    selected_offer_title_text=offer_title,
                    inclusion_options=inclusion_options,
                    texts=texts_for_pdf,
                    theme_name=theme_name,
                    primary_color=primary_color,
                )

                if pdf_bytes:
                    # Session State für persistente Downloads
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"TOM90_Angebot_{timestamp}.pdf"

                    st.session_state.tom90_pdf_bytes = pdf_bytes
                    st.session_state.tom90_pdf_filename = filename
                    st.session_state.tom90_pdf_timestamp = timestamp

                    st.success(" TOM-90 PDF erfolgreich erstellt!")

                    # Download-Button
                    st.download_button(
                        label=" TOM-90 PDF Herunterladen",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                        key="tom90_pdf_download_btn_primary",
                    )

                    # PDF Vorschau (wenn möglich)
                    if len(pdf_bytes) < 5 * 1024 * 1024:  # Nur bis 5MB
                        try:
                            encoded = base64.b64encode(pdf_bytes).decode("utf-8")
                            pdf_display = f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="600" type="application/pdf"></iframe>'
                            st.markdown("####  PDF Vorschau")
                            st.markdown(pdf_display, unsafe_allow_html=True)
                        except Exception:
                            st.info(
                                "PDF zu groß für Vorschau, aber Download verfügbar."
                            )
                    else:
                        st.info("PDF zu groß für Vorschau, aber Download verfügbar.")
                else:
                    st.error(
                        " Fehler bei der PDF-Erstellung. Überprüfen Sie die Eingabedaten."
                    )

            except Exception as e:
                st.error(f" Unerwarteter Fehler bei der PDF-Erstellung: {str(e)}")
                if st.checkbox("Debug-Details anzeigen"):
                    st.code(traceback.format_exc())

    # Persistente Downloads (falls PDF bereits erstellt wurde)
    if "tom90_pdf_bytes" in st.session_state and st.session_state.tom90_pdf_bytes:
        st.markdown("---")
        st.markdown("####  Persistente Downloads")
        st.info(
            f"Letztes PDF erstellt: {st.session_state.get('tom90_pdf_timestamp', 'Unbekannt')}"
        )

        col_download, col_reset = st.columns([3, 1])
        with col_download:
            st.download_button(
                label=" Letztes TOM-90 PDF erneut herunterladen",
                data=st.session_state.tom90_pdf_bytes,
                file_name=st.session_state.get(
                    "tom90_pdf_filename", "TOM90_Angebot.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
                key="tom90_pdf_download_btn_persistent",
            )
        with col_reset:
            if st.button(" Reset", help="Lösche gespeichertes PDF"):
                for key in [
                    "tom90_pdf_bytes",
                    "tom90_pdf_filename",
                    "tom90_pdf_timestamp",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()


# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-05, Gemini Ultra: TypeError bei `st.form_submit_button` in `pdf_ui.py` durch Entfernen des ungültigen `key`-Arguments behoben.
# 2025-06-05, Gemini Ultra: Buttons "Alles auswählen", "Alles abwählen" und Vorlagenmanagement (Laden/Speichern) in `pdf_ui.py` implementiert.
#                           Vorlagen werden als JSON unter dem Admin-Setting 'pdf_offer_presets' gespeichert.
#                           Callbacks für die Buttons aktualisieren `st.session_state.pdf_inclusion_options` und `st.session_state.pdf_selected_main_sections`.
#                           Checkbox-Logik angepasst, um Auswahl im Formular temporär zu sammeln und bei Submit in Session State zu schreiben.
# 2025-06-05, Gemini Ultra: TypeError beim Laden von PDF-Presets behoben. `json.loads` wird nicht mehr auf bereits geparste Listen angewendet.
#                           Sicherheitsprüfungen für geladene Presets hinzugefügt. Fallback für `active_company_id_for_docs` auf `None` korrigiert.
#                           Sicherere Initialisierung der Vorlagenauswahl im Session State.
# 2025-06-06, Gemini Ultra: Debug-Bereich für PDF-Anhänge hinzugefügt. Prüft Verfügbarkeit von PyPDF, aktive Firma, Firmendokumente und Projektdetails.
# 2025-06-07, Gemini Ultra: PDF-Vorschau-Integration hinzugefügt.
# 2025-06-07, Gemini Ultra: Erweiterte PDF-Vorschau-Funktion (BOMBE!) hinzugefügt.
# 2025-06-08, Gemini Ultra: Datenstatus-Anzeige und Fallback-PDF-Option hinzugefügt.
