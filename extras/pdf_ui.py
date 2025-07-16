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
from doc_output import _show_pdf_data_status

# --- Fallback-Funktionsreferenzen ---
def _dummy_load_admin_setting_pdf_ui(key, default=None):
    if key == 'pdf_title_image_templates': return [{'name': 'Standard-Titelbild (Fallback)', 'data': None}]
    if key == 'pdf_offer_title_templates': return [{'name': 'Standard-Titel (Fallback)', 'content': 'Angebot für Ihre Photovoltaikanlage'}]
    if key == 'pdf_cover_letter_templates': return [{'name': 'Standard-Anschreiben (Fallback)', 'content': 'Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.'}]
    elif key == 'active_company_id': return None
    elif key == 'pdf_offer_presets': return [] # Korrekter Fallback als Liste
    return default
def _dummy_save_admin_setting_pdf_ui(key, value): return False
def _dummy_generate_offer_pdf(*args, **kwargs):
    st.error("PDF-Generierungsfunktion (pdf_generator.py) nicht verfügbar oder fehlerhaft (Dummy in pdf_ui.py aktiv).")
    return None
def _dummy_get_active_company_details() -> Optional[Dict[str, Any]]:
    return {"name": "Dummy Firma AG", "id": 0, "logo_base64": None}
def _dummy_list_company_documents(company_id: int, doc_type: Optional[str]=None) -> List[Dict[str, Any]]:
    return []

_generate_offer_pdf_safe = _dummy_generate_offer_pdf
try:
    from pdf_generator import generate_offer_pdf
    _generate_offer_pdf_safe = generate_offer_pdf
except (ImportError, ModuleNotFoundError): pass 
except Exception: pass

# PDF-VORSCHAU INTEGRATION (NEU)
try:
    from pdf_preview import show_pdf_preview_interface, create_pdf_template_presets
    _PDF_PREVIEW_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _PDF_PREVIEW_AVAILABLE = False
    
    def show_pdf_preview_interface(*args, **kwargs):
        st.error("❌ PDF-Vorschau-Modul nicht verfügbar!")
        return None
    
    def create_pdf_template_presets():
        return {}

# --- Hilfsfunktionen ---
def get_text_pdf_ui(texts_dict: Dict[str, str], key: str, fallback_text: Optional[str] = None) -> str:
    if not isinstance(texts_dict, dict):
        return fallback_text if fallback_text is not None else key.replace("_", " ").title() + " (Texte fehlen)"
    return texts_dict.get(key, fallback_text if fallback_text is not None else key.replace("_", " ").title() + " (Text-Key fehlt)")

def _get_all_available_chart_keys(analysis_results: Dict[str, Any], chart_key_map: Dict[str, str]) -> List[str]:
    if not analysis_results or not isinstance(analysis_results, dict):
        return []
    return [k for k in chart_key_map.keys() if analysis_results.get(k) is not None]

def _get_all_available_company_doc_ids(active_company_id: Optional[int], db_list_company_documents_func: Callable) -> List[int]:
    if active_company_id is None or not callable(db_list_company_documents_func):
        return []
    docs = db_list_company_documents_func(active_company_id, None)
    return [doc['id'] for doc in docs if isinstance(doc, dict) and 'id' in doc]

# --- Haupt-Render-Funktion für die PDF UI ---
def render_pdf_ui(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    load_admin_setting_func: Callable[[str, Any], Any],
    save_admin_setting_func: Callable[[str, Any], bool],
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    get_active_company_details_func: Callable[[], Optional[Dict[str, Any]]] = _dummy_get_active_company_details,
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]] = _dummy_list_company_documents
):
    st.header(get_text_pdf_ui(texts, "menu_item_doc_output", "Angebotsausgabe (PDF)"))
    
    # Debug-Bereich hinzufügen
    render_pdf_debug_section(
        texts, project_data, analysis_results, 
        get_active_company_details_func, db_list_company_documents_func, get_product_by_id_func
    )

    if 'pdf_generating_lock_v1' not in st.session_state: st.session_state.pdf_generating_lock_v1 = False
    if 'pdf_inclusion_options' not in st.session_state:
        st.session_state.pdf_inclusion_options = {
            "include_company_logo": True, "include_product_images": True, 
            "include_all_documents": False, "company_document_ids_to_include": [],
            "selected_charts_for_pdf": [], "include_optional_component_details": True
        }
    if "pdf_selected_main_sections" not in st.session_state:
         st.session_state.pdf_selected_main_sections = ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics", "SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects"]
    if 'pdf_preset_name_input' not in st.session_state: st.session_state.pdf_preset_name_input = ""

    minimal_data_ok = True 
    if not project_data or not isinstance(project_data, dict): project_data = {}; minimal_data_ok = False
    customer_data_pdf = project_data.get('customer_data', {}); project_details_pdf = project_data.get('project_details', {})
    if not (project_details_pdf.get('module_quantity') and (project_details_pdf.get('selected_module_id') or project_details_pdf.get('selected_module_name')) and (project_details_pdf.get('selected_inverter_id') or project_details_pdf.get('selected_inverter_name'))): minimal_data_ok = False
    if not minimal_data_ok: 
        st.info(get_text_pdf_ui(texts, "pdf_creation_minimal_data_missing_info", "Minimale Projektdaten...fehlen."))
        return
    if not analysis_results or not isinstance(analysis_results, dict): 
        analysis_results = {}
        st.info(get_text_pdf_ui(texts, "pdf_creation_no_analysis_for_pdf_info", "Analyseergebnisse unvollständig..."))
    
    active_company = get_active_company_details_func()
    company_info_for_pdf = active_company if active_company else {"name": "Ihre Firma (Fallback)"}
    company_logo_b64_for_pdf = active_company.get('logo_base64') if active_company else None
    active_company_id_for_docs = active_company.get('id') if active_company else None # Korrigiert: None statt 0 als Fallback
    
    if active_company: 
        st.caption(f"Angebot für Firma: **{active_company.get('name', 'Unbekannt')}** (ID: {active_company_id_for_docs})")
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
            customer_data = project_data.get('customer_data', {})
            fallback_pdf = _create_no_data_fallback_pdf(texts, customer_data)
            
            if fallback_pdf:
                st.success("📄 Einfaches Info-PDF erstellt!")
                st.download_button(
                    label="📥 Info-PDF herunterladen",
                    data=fallback_pdf,
                    file_name=f"PV_Info_{customer_data.get('last_name', 'Interessent')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Fehler beim Erstellen des Info-PDFs")
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Fallback-PDFs: {e}")
        return
    
    st.markdown("---")

    # Vorlagen und Presets laden
    title_image_templates, offer_title_templates, cover_letter_templates, pdf_presets = [], [], [], []
    try:
        title_image_templates = load_admin_setting_func('pdf_title_image_templates', [])
        offer_title_templates = load_admin_setting_func('pdf_offer_title_templates', [])
        cover_letter_templates = load_admin_setting_func('pdf_cover_letter_templates', [])
        
        # KORREKTUR: `load_admin_setting_func` gibt bereits eine Liste zurück, wenn der Wert als JSON-Array gespeichert wurde.
        # Kein erneutes `json.loads` nötig.
        loaded_presets = load_admin_setting_func('pdf_offer_presets', []) # Standard ist eine leere Liste
        if isinstance(loaded_presets, list):
            pdf_presets = loaded_presets
        elif isinstance(loaded_presets, str) and loaded_presets.strip(): # Fallback, falls doch als String gespeichert
            try:
                pdf_presets = json.loads(loaded_presets)
                if not isinstance(pdf_presets, list): # Sicherstellen, dass es eine Liste ist
                    st.warning("PDF-Presets sind nicht im korrekten Listenformat gespeichert. Werden zurückgesetzt.")
                    pdf_presets = []
            except json.JSONDecodeError:
                st.warning("Fehler beim Parsen der PDF-Presets aus der Datenbank. Werden zurückgesetzt.")
                pdf_presets = []
        else: # Default, falls nichts geladen oder unerwarteter Typ
            pdf_presets = []

        # Typsicherheit für andere Vorlagen
        if not isinstance(title_image_templates, list): title_image_templates = []
        if not isinstance(offer_title_templates, list): offer_title_templates = []
        if not isinstance(cover_letter_templates, list): cover_letter_templates = []

    except Exception as e_load_data:
        st.error(f"Fehler beim Laden von PDF-Vorlagen oder Presets: {e_load_data}")
        # Fallback-Werte sicherstellen
        title_image_templates, offer_title_templates, cover_letter_templates, pdf_presets = [], [], [], []
    
    # ... (Rest der Funktion render_pdf_ui wie in der vorherigen Antwort) ...    # (Initialisierung Session State für Vorlagenauswahl, Definitionen für "Alles auswählen/abwählen", Callbacks, UI-Elemente)
    if "selected_title_image_name_doc_output" not in st.session_state: st.session_state.selected_title_image_name_doc_output = title_image_templates[0]['name'] if title_image_templates and isinstance(title_image_templates[0], dict) else None
    if "selected_title_image_b64_data_doc_output" not in st.session_state: st.session_state.selected_title_image_b64_data_doc_output = title_image_templates[0]['data'] if title_image_templates and isinstance(title_image_templates[0], dict) else None
    if "selected_offer_title_name_doc_output" not in st.session_state: st.session_state.selected_offer_title_name_doc_output = offer_title_templates[0]['name'] if offer_title_templates and isinstance(offer_title_templates[0], dict) else None
    if "selected_offer_title_text_content_doc_output" not in st.session_state: st.session_state.selected_offer_title_text_content_doc_output = offer_title_templates[0]['content'] if offer_title_templates and isinstance(offer_title_templates[0], dict) else ""
    if "selected_cover_letter_name_doc_output" not in st.session_state: st.session_state.selected_cover_letter_name_doc_output = cover_letter_templates[0]['name'] if cover_letter_templates and isinstance(cover_letter_templates[0], dict) else None
    if "selected_cover_letter_text_content_doc_output" not in st.session_state: st.session_state.selected_cover_letter_text_content_doc_output = cover_letter_templates[0]['content'] if cover_letter_templates and isinstance(cover_letter_templates[0], dict) else ""

    default_pdf_sections_map = {"ProjectOverview": get_text_pdf_ui(texts, "pdf_section_title_projectoverview", "1. Projektübersicht"),"TechnicalComponents": get_text_pdf_ui(texts, "pdf_section_title_technicalcomponents", "2. Systemkomponenten"),"CostDetails": get_text_pdf_ui(texts, "pdf_section_title_costdetails", "3. Kostenaufstellung"),"Economics": get_text_pdf_ui(texts, "pdf_section_title_economics", "4. Wirtschaftlichkeit"),"SimulationDetails": get_text_pdf_ui(texts, "pdf_section_title_simulationdetails", "5. Simulation"),"CO2Savings": get_text_pdf_ui(texts, "pdf_section_title_co2savings", "6. CO₂-Einsparung"),"Visualizations": get_text_pdf_ui(texts, "pdf_section_title_visualizations", "7. Grafiken"),"FutureAspects": get_text_pdf_ui(texts, "pdf_section_title_futureaspects", "8. Zukunftsaspekte")}
    all_main_section_keys = list(default_pdf_sections_map.keys())
    chart_key_to_friendly_name_map = {'monthly_prod_cons_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_monthly_compare", "Monatl. Produktion/Verbrauch (2D)"),'cost_projection_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_cost_projection", "Stromkosten-Hochrechnung (2D)"),'cumulative_cashflow_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_cum_cashflow", "Kumulierter Cashflow (2D)"),'consumption_coverage_pie_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_consum_coverage_pie", "Verbrauchsdeckung (Kreis)"),'pv_usage_pie_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pv_usage_pie", "PV-Nutzung (Kreis)"),'daily_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_daily_3d", "Tagesproduktion (3D)"),'weekly_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_weekly_3d", "Wochenproduktion (3D)"),'yearly_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_yearly_3d_bar", "Jahresproduktion (3D-Balken)"),'project_roi_matrix_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_roi_matrix_3d", "Projektrendite-Matrix (3D)"),'feed_in_revenue_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_feedin_3d", "Einspeisevergütung (3D)"),'prod_vs_cons_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_prodcons_3d", "Verbr. vs. Prod. (3D)"),'tariff_cube_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_tariffcube_3d", "Tarifvergleich (3D)"),'co2_savings_value_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_co2value_3d", "CO2-Ersparnis vs. Wert (3D)"),'investment_value_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_investval_3D", "Investitionsnutzwert (3D)"),'storage_effect_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_storageeff_3d", "Speicherwirkung (3D)"),'selfuse_stack_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_selfusestack_3d", "Eigenverbr. vs. Einspeis. (3D)"),'cost_growth_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_costgrowth_3d", "Stromkostensteigerung (3D)"),'selfuse_ratio_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_selfuseratio_3d", "Eigenverbrauchsgrad (3D)"),'roi_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_roicompare_3d", "ROI-Vergleich (3D)"),'scenario_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_scenariocomp_3d", "Szenarienvergleich (3D)"),'tariff_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_tariffcomp_3d", "Vorher/Nachher Stromkosten (3D)"),'income_projection_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_incomeproj_3d", "Einnahmenprognose (3D)"),'yearly_production_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_yearly", "PV Visuals: Jahresproduktion"),'break_even_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_breakeven", "PV Visuals: Break-Even"),'amortisation_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_amort", "PV Visuals: Amortisation")}
    all_available_chart_keys_for_selection = _get_all_available_chart_keys(analysis_results, chart_key_to_friendly_name_map)
    all_available_company_doc_ids_for_selection = _get_all_available_company_doc_ids(active_company_id_for_docs, db_list_company_documents_func)

    def select_all_options():
        st.session_state.pdf_inclusion_options["include_company_logo"] = True; st.session_state.pdf_inclusion_options["include_product_images"] = True; st.session_state.pdf_inclusion_options["include_all_documents"] = True; st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = all_available_company_doc_ids_for_selection[:]; st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = all_available_chart_keys_for_selection[:]; st.session_state.pdf_inclusion_options["include_optional_component_details"] = True; st.session_state.pdf_selected_main_sections = all_main_section_keys[:]
        st.success("Alle Optionen ausgewählt!")
    def deselect_all_options():
        st.session_state.pdf_inclusion_options["include_company_logo"] = False; st.session_state.pdf_inclusion_options["include_product_images"] = False; st.session_state.pdf_inclusion_options["include_all_documents"] = False; st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = []; st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = []; st.session_state.pdf_inclusion_options["include_optional_component_details"] = False; st.session_state.pdf_selected_main_sections = []
        st.success("Alle Optionen abgewählt!")
    def load_preset_on_click(preset_name_to_load: str):
        selected_preset = next((p for p in pdf_presets if p['name'] == preset_name_to_load), None)
        if selected_preset and 'selections' in selected_preset:
            selections = selected_preset['selections']
            st.session_state.pdf_inclusion_options["include_company_logo"] = selections.get("include_company_logo", True)
            st.session_state.pdf_inclusion_options["include_product_images"] = selections.get("include_product_images", True)
            st.session_state.pdf_inclusion_options["include_all_documents"] = selections.get("include_all_documents", False)
            st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = selections.get("company_document_ids_to_include", [])
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = selections.get("selected_charts_for_pdf", [])
            st.session_state.pdf_inclusion_options["include_optional_component_details"] = selections.get("include_optional_component_details", True)
            st.session_state.pdf_selected_main_sections = selections.get("pdf_selected_main_sections", all_main_section_keys[:])
            st.success(f"Vorlage '{preset_name_to_load}' geladen.")
        else: 
            st.warning(f"Vorlage '{preset_name_to_load}' nicht gefunden oder fehlerhaft.")
    
    def save_current_selection_as_preset():
        preset_name = st.session_state.get("pdf_preset_name_input", "").strip()
        if not preset_name:
            st.error("Bitte einen Namen für die Vorlage eingeben.")
            return
        if any(p['name'] == preset_name for p in pdf_presets): 
            st.warning(f"Eine Vorlage mit dem Namen '{preset_name}' existiert bereits.")
            return
        current_selections = {
            "include_company_logo": st.session_state.pdf_inclusion_options.get("include_company_logo"),
            "include_product_images": st.session_state.pdf_inclusion_options.get("include_product_images"),
            "include_all_documents": st.session_state.pdf_inclusion_options.get("include_all_documents"),
            "company_document_ids_to_include": st.session_state.pdf_inclusion_options.get("company_document_ids_to_include"),
            "selected_charts_for_pdf": st.session_state.pdf_inclusion_options.get("selected_charts_for_pdf"),
            "include_optional_component_details": st.session_state.pdf_inclusion_options.get("include_optional_component_details"),
            "pdf_selected_main_sections": st.session_state.get("pdf_selected_main_sections")
        }
        new_preset = {"name": preset_name, "selections": current_selections}
        updated_presets = pdf_presets + [new_preset]
        try:
            if save_admin_setting_func('pdf_offer_presets', json.dumps(updated_presets)):
                st.success(f"Vorlage '{preset_name}' erfolgreich gespeichert!")
                st.session_state.pdf_preset_name_input = ""
                # Um die Liste der Presets im Selectbox zu aktualisieren, ist ein Rerun nötig.
                # Dies geschieht, wenn das Hauptformular abgesendet wird oder durch eine andere Interaktion.
                # Alternativ könnte man hier ein st.rerun() erzwingen, aber das kann die Formularinteraktion stören.
            else: 
                st.error("Fehler beim Speichern der Vorlage in den Admin-Einstellungen.")
        except Exception as e_save_preset:
            st.error(f"Fehler beim Speichern der Vorlage: {e_save_preset}")

    st.markdown("---"); st.subheader(get_text_pdf_ui(texts, "pdf_template_management_header", "Vorlagen & Schnellauswahl"))
    col_preset1, col_preset2 = st.columns([3,2])
    with col_preset1:
        preset_names = [p['name'] for p in pdf_presets if isinstance(p,dict) and 'name' in p]
        if preset_names:
            selected_preset_name_to_load = st.selectbox(get_text_pdf_ui(texts, "pdf_load_preset_label", "Vorlage laden"), options=[get_text_pdf_ui(texts, "pdf_no_preset_selected_option", "-- Keine Vorlage --")] + preset_names, key="pdf_preset_load_select_v1_stable")
            if selected_preset_name_to_load != get_text_pdf_ui(texts, "pdf_no_preset_selected_option", "-- Keine Vorlage --"):
                if st.button(get_text_pdf_ui(texts, "pdf_load_selected_preset_button", "Ausgewählte Vorlage anwenden"), key="pdf_load_preset_btn_v1_stable", on_click=load_preset_on_click, args=(selected_preset_name_to_load,)): pass
        else: 
            st.caption(get_text_pdf_ui(texts, "pdf_no_presets_available_caption", "Keine Vorlagen gespeichert."))
    with col_preset2:
        st.text_input(get_text_pdf_ui(texts, "pdf_new_preset_name_label", "Name für neue Vorlage"), key="pdf_preset_name_input")
        st.button(get_text_pdf_ui(texts, "pdf_save_current_selection_button", "Aktuelle Auswahl speichern"), on_click=save_current_selection_as_preset, key="pdf_save_preset_btn_v1_stable")
    col_global_select1, col_global_select2 = st.columns(2)
    with col_global_select1: st.button(f"✅ {get_text_pdf_ui(texts, 'pdf_select_all_button', 'Alle Optionen auswählen')}", on_click=select_all_options, key="pdf_select_all_btn_v1_stable", use_container_width=True)
    with col_global_select2: st.button(f"❌ {get_text_pdf_ui(texts, 'pdf_deselect_all_button', 'Alle Optionen abwählen')}", on_click=deselect_all_options, key="pdf_deselect_all_btn_v1_stable", use_container_width=True)
    st.markdown("---")
    
    # Hauptformular
    # ... (Rest des Formulars und der PDF-Generierungslogik wie in der vorherigen Antwort, mit der Korrektur für st.form_submit_button) ...
    form_submit_key = "pdf_final_submit_btn_v13_corrected_again" 
    submit_button_disabled = st.session_state.pdf_generating_lock_v1
    with st.form(key="pdf_generation_form_v13_final_locked_options_main", clear_on_submit=False):
        st.subheader(get_text_pdf_ui(texts, "pdf_config_header", "PDF-Konfiguration"))
        with st.container():
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_template_selection_info", "Vorlagen für das Angebot auswählen") + "**")
            title_image_options = {t.get('name', f"Bild {i+1}"): t.get('data') for i, t in enumerate(title_image_templates) if isinstance(t,dict) and t.get('name')}
            if not title_image_options: title_image_options = {get_text_pdf_ui(texts, "no_title_images_available", "Keine Titelbilder verfügbar"): None}
            title_image_keys = list(title_image_options.keys()); idx_title_img = title_image_keys.index(st.session_state.selected_title_image_name_doc_output) if st.session_state.selected_title_image_name_doc_output in title_image_keys else 0
            selected_title_image_name = st.selectbox(get_text_pdf_ui(texts, "pdf_select_title_image", "Titelbild auswählen"), options=title_image_keys, index=idx_title_img, key="pdf_title_image_select_v13_form")
            if selected_title_image_name != st.session_state.selected_title_image_name_doc_output : st.session_state.selected_title_image_name_doc_output = selected_title_image_name; st.session_state.selected_title_image_b64_data_doc_output = title_image_options.get(selected_title_image_name)
            offer_title_options = {t.get('name', f"Titel {i+1}"): t.get('content') for i, t in enumerate(offer_title_templates) if isinstance(t,dict) and t.get('name')}
            if not offer_title_options: offer_title_options = {get_text_pdf_ui(texts, "no_offer_titles_available", "Keine Angebotstitel verfügbar"): "Standard Angebotstitel"}
            offer_title_keys = list(offer_title_options.keys()); idx_offer_title = offer_title_keys.index(st.session_state.selected_offer_title_name_doc_output) if st.session_state.selected_offer_title_name_doc_output in offer_title_keys else 0
            selected_offer_title_name = st.selectbox(get_text_pdf_ui(texts, "pdf_select_offer_title", "Überschrift/Titel auswählen"), options=offer_title_keys, index=idx_offer_title, key="pdf_offer_title_select_v13_form")
            if selected_offer_title_name != st.session_state.selected_offer_title_name_doc_output: st.session_state.selected_offer_title_name_doc_output = selected_offer_title_name; st.session_state.selected_offer_title_text_content_doc_output = offer_title_options.get(selected_offer_title_name, "")
            cover_letter_options = {t.get('name', f"Anschreiben {i+1}"): t.get('content') for i, t in enumerate(cover_letter_templates) if isinstance(t,dict) and t.get('name')}
            if not cover_letter_options: cover_letter_options = {get_text_pdf_ui(texts, "no_cover_letters_available", "Keine Anschreiben verfügbar"): "Standard Anschreiben"}
            cover_letter_keys = list(cover_letter_options.keys()); idx_cover_letter = cover_letter_keys.index(st.session_state.selected_cover_letter_name_doc_output) if st.session_state.selected_cover_letter_name_doc_output in cover_letter_keys else 0
            selected_cover_letter_name = st.selectbox(get_text_pdf_ui(texts, "pdf_select_cover_letter", "Anschreiben auswählen"), options=cover_letter_keys, index=idx_cover_letter, key="pdf_cover_letter_select_v13_form")
            if selected_cover_letter_name != st.session_state.selected_cover_letter_name_doc_output: st.session_state.selected_cover_letter_name_doc_output = selected_cover_letter_name; st.session_state.selected_cover_letter_text_content_doc_output = cover_letter_options.get(selected_cover_letter_name, "")
        st.markdown("---")
        st.markdown("**" + get_text_pdf_ui(texts, "pdf_content_selection_info", "Inhalte für das PDF auswählen") + "**")
        col_pdf_content1_form, col_pdf_content2_form, col_pdf_content3_form = st.columns(3)
        with col_pdf_content1_form: 
            st.session_state.pdf_inclusion_options["include_company_logo"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_company_logo_label", "Firmenlogo anzeigen?"), value=st.session_state.pdf_inclusion_options.get("include_company_logo", True), key="pdf_cb_logo_v13_form_main_stable")
            st.session_state.pdf_inclusion_options["include_product_images"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_product_images_label", "Produktbilder anzeigen? (Haupt & Zubehör)"), value=st.session_state.pdf_inclusion_options.get("include_product_images", True), key="pdf_cb_prod_img_v13_form_main_stable")
            st.session_state.pdf_inclusion_options["include_optional_component_details"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_optional_component_details_label", "Details zu optionalen Komponenten anzeigen?"), value=st.session_state.pdf_inclusion_options.get("include_optional_component_details", True), key="pdf_cb_opt_comp_details_v13_form_main_stable")
            st.session_state.pdf_inclusion_options["include_all_documents"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_all_documents_label", "Alle Datenblätter & ausgew. Firmendokumente anhängen?"), value=st.session_state.pdf_inclusion_options.get("include_all_documents", False), key="pdf_cb_all_docs_v13_form_main_stable")
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_select_company_docs", "Spezifische Firmendokumente für Anhang") + "**")
            if active_company_id_for_docs is not None and isinstance(active_company_id_for_docs, int) and callable(db_list_company_documents_func):
                company_docs_list_form = db_list_company_documents_func(active_company_id_for_docs, None)
                if company_docs_list_form:
                    current_selected_doc_ids_form = st.session_state.pdf_inclusion_options.get("company_document_ids_to_include", [])
                    # Die temporäre Liste wird nicht mehr benötigt, da Checkboxen direkt den Session State beeinflussen (müssten, oder hier gesammelt)
                    # Für die on_click Callbacks der globalen Buttons ist es besser, wenn Checkboxen direkt den State widerspiegeln.
                    # Aber für den Form-Submit sammeln wir die Werte NEU basierend auf den aktuellen Checkbox-Zuständen im Formular.
                    selected_doc_ids_in_form = []
                    for doc_item_form in company_docs_list_form:
                        if isinstance(doc_item_form, dict) and 'id' in doc_item_form:
                            doc_id_item_form = doc_item_form['id']
                            doc_label_item_form = f"{doc_item_form.get('display_name', doc_item_form.get('file_name', 'Unbenannt'))} ({doc_item_form.get('document_type')})"
                            if st.checkbox(doc_label_item_form, value=(doc_id_item_form in current_selected_doc_ids_form), key=f"pdf_cb_company_doc_form_{doc_id_item_form}_v13_stable"):
                                selected_doc_ids_in_form.append(doc_id_item_form)
                    # Dieser Wert wird beim Submit verwendet
                    st.session_state.pdf_inclusion_options["_temp_company_document_ids_to_include"] = selected_doc_ids_in_form
                else: 
                    st.caption(get_text_pdf_ui(texts, "pdf_no_company_documents_available", "Keine Dokumente für Firma hinterlegt."))
            else:
                st.caption(get_text_pdf_ui(texts, "pdf_select_active_company_for_docs", "Aktive Firma nicht korrekt."))
        with col_pdf_content2_form: 
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_main_sections", "Hauptsektionen im Angebot") + "**")
            current_selected_main_sections_in_state_form = st.session_state.get("pdf_selected_main_sections", all_main_section_keys[:])
            selected_sections_in_form = []
            for section_key_form, section_label_from_map_form in default_pdf_sections_map.items():
                if st.checkbox(section_label_from_map_form, value=(section_key_form in current_selected_main_sections_in_state_form), key=f"pdf_section_cb_form_{section_key_form}_v13_stable"):
                    selected_sections_in_form.append(section_key_form)
            st.session_state["_temp_pdf_selected_main_sections"] = selected_sections_in_form
        with col_pdf_content3_form: 
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_charts", "Diagramme & Visualisierungen") + "**")
            if analysis_results and isinstance(analysis_results, dict):
                available_chart_keys_form = _get_all_available_chart_keys(analysis_results, chart_key_to_friendly_name_map)
                ordered_display_keys_form = [k_map for k_map in chart_key_to_friendly_name_map.keys() if k_map in available_chart_keys_form]
                for k_avail_form in available_chart_keys_form: 
                    if k_avail_form not in ordered_display_keys_form: ordered_display_keys_form.append(k_avail_form)
                current_selected_charts_in_state_form = st.session_state.pdf_inclusion_options.get("selected_charts_for_pdf", [])
                selected_charts_in_form = []
                for chart_key_form in ordered_display_keys_form:
                    friendly_name_form = chart_key_to_friendly_name_map.get(chart_key_form, chart_key_form.replace('_chart_bytes', '').replace('_', ' ').title())
                    if st.checkbox(friendly_name_form, value=(chart_key_form in current_selected_charts_in_state_form), key=f"pdf_include_chart_form_{chart_key_form}_v13_stable"):
                        selected_charts_in_form.append(chart_key_form)
                st.session_state.pdf_inclusion_options["_temp_selected_charts_for_pdf"] = selected_charts_in_form
            else: 
                st.caption(get_text_pdf_ui(texts, "pdf_no_charts_to_select", "Keine Diagrammdaten für PDF-Auswahl."))
        st.markdown("---")
        submitted_generate_pdf = st.form_submit_button(label=f"**{get_text_pdf_ui(texts, 'pdf_generate_button', 'Angebots-PDF erstellen')}**", type="primary", disabled=submit_button_disabled)
        if submitted_generate_pdf: # Werte aus temporären Keys in die Haupt-Session-State-Keys übernehmen
            st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = st.session_state.pdf_inclusion_options.pop("_temp_company_document_ids_to_include", [])
            st.session_state.pdf_selected_main_sections = st.session_state.pop("_temp_pdf_selected_main_sections", [])
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = st.session_state.pdf_inclusion_options.pop("_temp_selected_charts_for_pdf", [])
            
    if submitted_generate_pdf and not st.session_state.pdf_generating_lock_v1:
        st.session_state.pdf_generating_lock_v1 = True
        pdf_bytes = None 
        try:            # Datenvalidierung vor PDF-Erstellung
            try:
                from pdf_generator import _validate_pdf_data_availability, _create_no_data_fallback_pdf
                
                validation_result = _validate_pdf_data_availability(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    texts=texts
                )
                
                # Zeige Validierungsstatus an
                if not validation_result['is_valid']:
                    st.warning(f"⚠️ Unvollständige Daten erkannt: {', '.join(validation_result['missing_data_summary'])}")
                    st.info("Ein vereinfachtes Informations-PDF wird erstellt.")
                    
                    if validation_result['critical_errors'] > 0:
                        st.error(f"❌ {validation_result['critical_errors']} kritische Fehler gefunden. Erstelle Fallback-PDF...")
                        
                        # Erstelle Fallback-PDF
                        pdf_bytes = create_fallback_pdf(
                            issues=validation_result['missing_data'],
                            warnings=validation_result['warnings'],
                            texts=texts
                        )
                        st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
                        st.success("✅ Fallback-PDF erfolgreich erstellt!")
                        return
                    else:
                        st.info(f"ℹ️ {validation_result['warnings']} Warnungen. PDF wird mit verfügbaren Daten erstellt.")
                else:
                    st.success("✅ Alle Daten vollständig verfügbar.")
                    
            except ImportError:
                st.warning("Datenvalidierung nicht verfügbar. Fahre mit normaler PDF-Erstellung fort.")
                
            with st.spinner(get_text_pdf_ui(texts, 'pdf_generation_spinner', 'PDF wird generiert, bitte warten...')):
                final_inclusion_options_to_pass = st.session_state.pdf_inclusion_options.copy()
                final_sections_to_include_to_pass = st.session_state.pdf_selected_main_sections[:]
                pdf_bytes = _generate_offer_pdf_safe(project_data=project_data, analysis_results=analysis_results, company_info=company_info_for_pdf, company_logo_base64=company_logo_b64_for_pdf, selected_title_image_b64=st.session_state.selected_title_image_b64_data_doc_output, selected_offer_title_text=st.session_state.selected_offer_title_text_content_doc_output, selected_cover_letter_text=st.session_state.selected_cover_letter_text_content_doc_output, sections_to_include=final_sections_to_include_to_pass, inclusion_options=final_inclusion_options_to_pass, load_admin_setting_func=load_admin_setting_func, save_admin_setting_func=save_admin_setting_func, list_products_func=list_products_func, get_product_by_id_func=get_product_by_id_func, db_list_company_documents_func=db_list_company_documents_func, active_company_id=active_company_id_for_docs, texts=texts)
            st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
        except Exception as e_gen_final_outer: st.error(f"{get_text_pdf_ui(texts, 'pdf_generation_exception_outer', 'Kritischer Fehler im PDF-Prozess (pdf_ui.py):')} {e_gen_final_outer}"); st.text_area("Traceback PDF Erstellung (pdf_ui.py):", traceback.format_exc(), height=250); st.session_state.generated_pdf_bytes_for_download_v1 = None
        finally: st.session_state.pdf_generating_lock_v1 = False; st.session_state.selected_page_key_sui = "doc_output"; st.rerun() 
    if 'generated_pdf_bytes_for_download_v1' in st.session_state:
        pdf_bytes_to_download = st.session_state.pop('generated_pdf_bytes_for_download_v1') 
        if pdf_bytes_to_download and isinstance(pdf_bytes_to_download, bytes):
            customer_name_for_file = customer_data_pdf.get('last_name', 'Angebot'); file_name_customer_part = str(customer_name_for_file).replace(' ', '_') if customer_name_for_file and str(customer_name_for_file).strip() else "Photovoltaik_Angebot"
            timestamp_file = base64.b32encode(os.urandom(5)).decode('utf-8').lower(); file_name = f"Angebot_{file_name_customer_part}_{timestamp_file}.pdf"
            st.success(get_text_pdf_ui(texts, "pdf_generation_success", "PDF erfolgreich erstellt!")); st.download_button(label=get_text_pdf_ui(texts, "pdf_download_button", "PDF herunterladen"), data=pdf_bytes_to_download, file_name=file_name, mime="application/pdf", key=f"pdf_download_btn_final_{timestamp_file}_v13_final_stable")
        elif pdf_bytes_to_download is None and not st.session_state.get('pdf_generating_lock_v1', True) : st.error(get_text_pdf_ui(texts, "pdf_generation_failed_no_bytes_after_rerun", "PDF-Generierung fehlgeschlagen (keine Daten nach Rerun)."))

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
    db_list_company_documents_func: Callable = _dummy_list_company_documents
) -> Optional[bytes]:
    """
    Erweiterte PDF-Vorschau mit Bearbeitungsmöglichkeiten und Seitenreihenfolge.
    Das wird BOMBE! 🚀
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        texts: Übersetzungstexte
        ... weitere Callback-Funktionen
    
    Returns:
        PDF-Bytes falls erfolgreich generiert, sonst None
    """
    
    if not _PDF_PREVIEW_AVAILABLE:
        st.error("❌ PDF-Vorschau-Modul ist nicht verfügbar!")
        st.info("💡 Installieren Sie die erforderlichen Abhängigkeiten für die PDF-Vorschau.")
        return None
    
    # Firmendaten abrufen
    company_details = get_active_company_details_func()
    if not company_details:
        st.warning("⚠️ Keine aktive Firma gefunden. Verwende Standardwerte.")
        company_details = {
            "name": "Ihre Solarfirma",
            "street": "Musterstraße 1",
            "zip_code": "12345",
            "city": "Musterstadt",
            "phone": "+49 123 456789",
            "email": "info@ihresolarfirma.de",
            "id": 1
        }
    
    company_logo_base64 = company_details.get('logo_base64')
    
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
            active_company_id=company_details.get('id', 1),
            **kwargs
        )
    )

# --- Debug-Bereich für PDF-Anhänge ---
def render_pdf_debug_section(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    get_active_company_details_func: Callable,
    db_list_company_documents_func: Callable,
    get_product_by_id_func: Callable
):
    """Rendert einen Debug-Bereich für PDF-Anhänge"""
    with st.expander("🔍 Debug: PDF-Anhänge-Prüfung", expanded=False):
        st.subheader("Systemstatus")
        
        # PyPDF Verfügbarkeit prüfen
        try:
            from pypdf import PdfReader, PdfWriter
            pypdf_status = "✅ pypdf verfügbar"
        except ImportError:
            try:
                from PyPDF2 import PdfReader, PdfWriter
                pypdf_status = "✅ PyPDF2 verfügbar (Fallback)"
            except ImportError:
                pypdf_status = "❌ Keine PDF-Bibliothek verfügbar"
        
        st.write(f"**PDF-Bibliothek:** {pypdf_status}")
        
        # Aktive Firma prüfen
        active_company = get_active_company_details_func()
        if active_company:
            st.write(f"**Aktive Firma:** {active_company.get('name')} (ID: {active_company.get('id')})")
            
            # Firmendokumente prüfen
            company_docs = db_list_company_documents_func(active_company.get('id'), None)
            st.write(f"**Verfügbare Firmendokumente:** {len(company_docs)}")
            for doc in company_docs:
                doc_path = os.path.join(os.getcwd(), "data", "company_docs", doc.get("relative_db_path", ""))
                status = "✅" if os.path.exists(doc_path) else "❌"
                st.write(f"  {status} {doc.get('display_name')} (ID: {doc.get('id')})")
        else:
            st.write("**Aktive Firma:** ❌ Keine aktive Firma")
        
        # Projektdetails prüfen
        project_details = project_data.get('project_details', {})
        st.write("**Ausgewählte Produkte:**")
        
        product_ids = [
            ('Modul', project_details.get('selected_module_id')),
            ('Wechselrichter', project_details.get('selected_inverter_id')),
            ('Batteriespeicher', project_details.get('selected_storage_id') if project_details.get('include_storage') else None)
        ]
        
        for comp_type, prod_id in product_ids:
            if prod_id:
                try:
                    product_info = get_product_by_id_func(prod_id)
                    if product_info:
                        datasheet_path = product_info.get("datasheet_link_db_path")
                        if datasheet_path:
                            full_path = os.path.join(os.getcwd(), "data", "product_datasheets", datasheet_path)
                            status = "✅" if os.path.exists(full_path) else "❌"
                            st.write(f"  {status} {comp_type}: {product_info.get('model_name')} (ID: {prod_id})")
                            if not os.path.exists(full_path):
                                st.write(f"    ❌ Datenblatt fehlt: {full_path}")
                        else:
                            st.write(f"  ❌ {comp_type}: {product_info.get('model_name')} (Kein Datenblatt-Pfad)")
                    else:
                        st.write(f"  ❌ {comp_type}: Produkt ID {prod_id} nicht in DB gefunden")
                except Exception as e:
                    st.write(f"  ❌ {comp_type}: Fehler beim Laden von ID {prod_id}: {e}")
            else:
                st.write(f"  - {comp_type}: Nicht ausgewählt")
        
        # Current PDF inclusion options anzeigen
        st.subheader("Aktuelle PDF-Einstellungen")
        if 'pdf_inclusion_options' in st.session_state:
            options = st.session_state.pdf_inclusion_options
            st.json(options)
        else:
            st.write("Keine PDF-Einstellungen in Session State")

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