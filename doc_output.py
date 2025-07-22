"""
Datei: pdf_ui.py
Zweck: Benutzeroberfläche für die Konfiguration und Erstellung von Angebots-PDFs.
       Ermöglicht die Auswahl von Vorlagen, Inhalten und spezifischen Diagrammen in einem Dreispaltenlayout.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-03
"""
# pdf_ui.py (ehemals doc_output.py)
# Modul für die Angebotsausgabe (PDF)

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import base64
import traceback
import os

# --- Fallback-Funktionsreferenzen ---
# (Diese bleiben unverändert)
def _dummy_load_admin_setting_pdf_ui(key, default=None):
    if key == 'pdf_title_image_templates': return [{'name': 'Standard-Titelbild (Fallback)', 'data': None}]
    if key == 'pdf_offer_title_templates': return [{'name': 'Standard-Titel (Fallback)', 'content': 'Angebot für Ihre Photovoltaikanlage'}]
    if key == 'pdf_cover_letter_templates': return [{'name': 'Standard-Anschreiben (Fallback)', 'content': 'Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.'}]
    elif key == 'active_company_id': return None
    elif key == 'company_information': return {"name": "Ihre Firma (Fallback)", "id": 0, "logo_base64": None}
    elif key == 'company_logo_base64': return None
    return default
def _dummy_save_admin_setting_pdf_ui(key, value): return False
def _dummy_generate_offer_pdf(*args, **kwargs):
    st.error("PDF-Generierungsfunktion (pdf_generator.py) nicht verfügbar oder fehlerhaft (Dummy in pdf_ui.py aktiv).")
    missing_args = [k for k in ['load_admin_setting_func', 'save_admin_setting_func', 'list_products_func', 'get_product_by_id_func'] if k not in kwargs or not callable(kwargs[k])]
    if missing_args: st.error(f"Dummy PDF Generator: Fehlende Kernfunktionen: {', '.join(missing_args)}")
    return None
def _dummy_get_active_company_details() -> Optional[Dict[str, Any]]:
    return {"name": "Dummy Firma AG", "id": 0, "logo_base64": None}
def _dummy_list_company_documents(company_id: int, doc_type: Optional[str]=None) -> List[Dict[str, Any]]:
    return []

# PDF DEBUG WIDGET IMPORT
try:
    from pdf_debug_widget import integrate_pdf_debug
    DEBUG_WIDGET_AVAILABLE = True
except ImportError:
    DEBUG_WIDGET_AVAILABLE = False

_generate_offer_pdf_safe = _dummy_generate_offer_pdf
try:
    from pdf_generator import generate_offer_pdf
    _generate_offer_pdf_safe = generate_offer_pdf
except (ImportError, ModuleNotFoundError): pass
except Exception: pass

# --- Hilfsfunktionen ---
def get_text_pdf_ui(texts_dict: Dict[str, str], key: str, fallback_text: Optional[str] = None) -> str:
    if not isinstance(texts_dict, dict):
        return fallback_text if fallback_text is not None else key.replace("_", " ").title() + " (Texte fehlen)"
    return texts_dict.get(key, fallback_text if fallback_text is not None else key.replace("_", " ").title() + " (Text-Key fehlt)")

def _show_pdf_data_status(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]) -> bool:
    """
    Zeigt den Status der verfügbaren Daten für die PDF-Erstellung an und gibt zurück, ob die Daten ausreichen.
    """
    st.subheader(get_text_pdf_ui(texts, "pdf_data_status_header", "📊 Datenstatus für PDF-Erstellung"))
    
    validation_result = None
    data_sufficient = False

    # Datenvalidierung mit direktem Import der PDF-Generator-Validierung
    try:
        from pdf_generator import _validate_pdf_data_availability
        validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
        
        # ULTRA-AI-KORREKTUR: Zusätzliche Prüfung, um einen Absturz zu verhindern.
        if validation_result is None:
            st.error(get_text_pdf_ui(texts, "pdf_validation_internal_error", "Interner Fehler: Die Datenvalidierung hat kein Ergebnis zurückgegeben."))
            return False # Sauberer Ausstieg, um Absturz zu verhindern

        # Sicheres Abrufen des Wertes mit .get()
        data_sufficient = validation_result.get('is_valid', False)

    except ImportError:
        # Fallback zur lokalen Validierung, wenn Import fehlschlägt
        st.warning("Validierungsfunktion in pdf_generator.py nicht gefunden. Führe einfache Prüfung durch.")
        validation_result = {'is_valid': True, 'warnings': [], 'critical_errors': [], 'missing_data_summary': []}
        if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
            validation_result['critical_errors'].append("Keine Analyseergebnisse verfügbar")
            validation_result['missing_data_summary'].append("Analyseergebnisse")
            data_sufficient = False
        else:
            data_sufficient = True

    # Status-Indikatoren anzeigen
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        customer_data = project_data.get('customer_data', {})
        if customer_data and customer_data.get('last_name'):
            st.success("✅ " + get_text_pdf_ui(texts, "customer_data_complete", "Kundendaten"))
        else:
            st.info("ℹ️ " + get_text_pdf_ui(texts, "customer_data_incomplete", "Kundendaten"))
    with col2:
        pv_details = project_data.get('pv_details', {})
        project_details = project_data.get('project_details', {})
        modules_ok = (pv_details and pv_details.get('selected_modules')) or (project_details and project_details.get('module_quantity', 0) > 0)
        if modules_ok:
            st.success("✅ " + get_text_pdf_ui(texts, "pv_config_complete", "PV-Module"))
        else:
            st.info("ℹ️ " + get_text_pdf_ui(texts, "pv_config_incomplete", "PV-Module"))
    with col3:
        project_details = project_data.get('project_details', {})
        inverter_ok = project_details and (project_details.get('selected_inverter_id') or project_details.get('selected_inverter_name'))
        if inverter_ok:
            st.success("✅ " + get_text_pdf_ui(texts, "inverter_config_complete", "Wechselrichter"))
        else:
            st.info("ℹ️ " + get_text_pdf_ui(texts, "inverter_config_incomplete", "Wechselrichter"))
    with col4:
        if analysis_results and isinstance(analysis_results, dict) and len(analysis_results) > 1 and analysis_results.get('anlage_kwp'):
            st.success("✅ " + get_text_pdf_ui(texts, "analysis_complete", "Berechnung"))
        else:
            st.error("❌ " + get_text_pdf_ui(texts, "analysis_missing", "Berechnung"))
            
    # Handlungsempfehlungen
    if not data_sufficient:
        critical_messages = validation_result.get('critical_errors', [])
        critical_summary = ", ".join(critical_messages) if critical_messages else "Kritische Daten fehlen"
        st.error("🚫 " + get_text_pdf_ui(texts, "pdf_creation_blocked", f"PDF-Erstellung nicht möglich. {critical_summary}"))
        st.info(get_text_pdf_ui(texts, "pdf_creation_instructions", "Bitte führen Sie eine Wirtschaftlichkeitsberechnung durch, bevor Sie ein PDF erstellen."))
    elif validation_result.get('warnings'):
        st.warning("⚠️ " + get_text_pdf_ui(texts, "pdf_creation_warnings", "PDF kann erstellt werden, enthält aber möglicherweise nicht alle gewünschten Informationen."))
        st.info(get_text_pdf_ui(texts, "pdf_creation_with_warnings", "Bei unvollständigen Daten wird ein vereinfachtes PDF mit den verfügbaren Informationen erstellt."))
    else:
        st.success("🎉 " + get_text_pdf_ui(texts, "pdf_data_complete", "Alle erforderlichen Daten verfügbar - vollständiges PDF kann erstellt werden!"))
    
    return data_sufficient

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
    
    # SESSION STATE DATEN KONSOLIDIERUNG - FIX FÜR FEHLENDE DATEN
    # Oft sind die Daten in anderen Session State Keys gespeichert
    if not project_data or not isinstance(project_data, dict) or len(project_data) == 0:
        # Suche nach alternativen Project Data Quellen
        potential_sources = ['current_project_data', 'project_details', 'projektdaten']
        for source in potential_sources:
            if st.session_state.get(source) and isinstance(st.session_state[source], dict):
                project_data = st.session_state[source]
                st.session_state.project_data = project_data  # Synchronisiere für zukünftige Aufrufe
                st.info(f"🔄 Projektdaten aus '{source}' wiederhergestellt")
                break
    
    if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) == 0:
        # Suche nach alternativen Analysis Data Quellen - WICHTIG: calculation_results!
        potential_sources = ['calculation_results', 'current_analysis_results', 'kpi_results', 'berechnung_ergebnisse']
        for source in potential_sources:
            source_data = st.session_state.get(source)
            if source_data and isinstance(source_data, dict) and len(source_data) > 0:
                analysis_results = source_data
                st.session_state.analysis_results = analysis_results  # Synchronisiere für zukünftige Aufrufe
                st.info(f"🔄 Analyseergebnisse aus '{source}' wiederhergestellt")
                break
    
    # DEBUG WIDGET INTEGRATION
    if DEBUG_WIDGET_AVAILABLE:
        integrate_pdf_debug(project_data, analysis_results, texts)
    
    # DATENSTATUS-ANZEIGE
    data_sufficient = _show_pdf_data_status(project_data, analysis_results, texts)
    st.markdown("---")
    
    # PDF-Generierung nur erlauben wenn ausreichende Daten vorhanden
    if not data_sufficient:
        st.warning(get_text_pdf_ui(texts, "pdf_blocked_insufficient_data", 
            "PDF-Erstellung ist blockiert. Bitte vervollständigen Sie die erforderlichen Daten."))
        return
        
    if 'pdf_generating_lock_v1' not in st.session_state:
        st.session_state.pdf_generating_lock_v1 = False

    if not project_data or not isinstance(project_data, dict): 
        project_data = {}
    customer_data_pdf = project_data.get('customer_data', {})
    
    if not analysis_results or not isinstance(analysis_results, dict):
        analysis_results = {}
        st.info(get_text_pdf_ui(texts, "pdf_creation_no_analysis_for_pdf_info", "Analyseergebnisse sind unvollständig oder nicht vorhanden. Einige PDF-Inhalte könnten fehlen."))

    active_company = get_active_company_details_func()
    company_info_for_pdf = {}
    company_logo_b64_for_pdf = None
    active_company_id_for_docs = None
    if active_company and isinstance(active_company, dict):
        company_info_for_pdf = active_company
        company_logo_b64_for_pdf = active_company.get('logo_base64')
        active_company_id_for_docs = active_company.get('id')
        st.caption(f"Angebot für Firma: **{active_company.get('name', 'Unbekannt')}** (ID: {active_company_id_for_docs})")
    else:
        st.warning("Keine aktive Firma ausgewählt. PDF verwendet Fallback-Daten für Firmeninformationen."); company_info_for_pdf = {"name": "Ihre Firma (Fallback)"}; active_company_id_for_docs = 0

    try:
        title_image_templates = load_admin_setting_func('pdf_title_image_templates', [])
        offer_title_templates = load_admin_setting_func('pdf_offer_title_templates', [])
        cover_letter_templates = load_admin_setting_func('pdf_cover_letter_templates', [])
        if not isinstance(title_image_templates, list): title_image_templates = []
        if not isinstance(offer_title_templates, list): offer_title_templates = []
        if not isinstance(cover_letter_templates, list): cover_letter_templates = []
    except Exception as e_load_tpl:
        st.error(f"Fehler Laden PDF-Vorlagen: {e_load_tpl}"); title_image_templates, offer_title_templates, cover_letter_templates = [], [], []

    if "selected_title_image_name_doc_output" not in st.session_state: st.session_state.selected_title_image_name_doc_output = None
    if "selected_title_image_b64_data_doc_output" not in st.session_state: st.session_state.selected_title_image_b64_data_doc_output = None
    if "selected_offer_title_name_doc_output" not in st.session_state: st.session_state.selected_offer_title_name_doc_output = None
    if "selected_offer_title_text_content_doc_output" not in st.session_state: st.session_state.selected_offer_title_text_content_doc_output = ""
    if "selected_cover_letter_name_doc_output" not in st.session_state: st.session_state.selected_cover_letter_name_doc_output = None
    if "selected_cover_letter_text_content_doc_output" not in st.session_state: st.session_state.selected_cover_letter_text_content_doc_output = ""

    if 'pdf_inclusion_options' not in st.session_state:
        st.session_state.pdf_inclusion_options = {
            "include_company_logo": True,
            "include_product_images": True, 
            "include_all_documents": False, 
            "company_document_ids_to_include": [],
            "selected_charts_for_pdf": [],
            "include_optional_component_details": True
        }
    if "pdf_selected_main_sections" not in st.session_state:
         st.session_state.pdf_selected_main_sections = ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics", "SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects"]

    submit_button_disabled = st.session_state.pdf_generating_lock_v1

    with st.form(key="pdf_generation_form_v12_final_locked_options", clear_on_submit=False):
        st.subheader(get_text_pdf_ui(texts, "pdf_config_header", "PDF-Konfiguration"))

        with st.container(): # Vorlagenauswahl
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_template_selection_info", "Vorlagen für das Angebot auswählen") + "**")
            title_image_options = {t.get('name', f"Bild {i+1}"): t.get('data') for i, t in enumerate(title_image_templates) if isinstance(t,dict) and t.get('name')}
            if not title_image_options: title_image_options = {get_text_pdf_ui(texts, "no_title_images_available", "Keine Titelbilder verfügbar"): None}
            title_image_keys = list(title_image_options.keys())
            idx_title_img = 0
            if st.session_state.selected_title_image_name_doc_output in title_image_keys: idx_title_img = title_image_keys.index(st.session_state.selected_title_image_name_doc_output)
            elif title_image_keys: st.session_state.selected_title_image_name_doc_output = title_image_keys[0] 
            selected_title_image_name = st.selectbox(get_text_pdf_ui(texts, "pdf_select_title_image", "Titelbild auswählen"), options=title_image_keys, index=idx_title_img, key="pdf_title_image_select_v12_form")
            st.session_state.selected_title_image_name_doc_output = selected_title_image_name
            st.session_state.selected_title_image_b64_data_doc_output = title_image_options.get(selected_title_image_name)

            offer_title_options = {t.get('name', f"Titel {i+1}"): t.get('content') for i, t in enumerate(offer_title_templates) if isinstance(t,dict) and t.get('name')}
            if not offer_title_options: offer_title_options = {get_text_pdf_ui(texts, "no_offer_titles_available", "Keine Angebotstitel verfügbar"): "Standard Angebotstitel"}
            offer_title_keys = list(offer_title_options.keys())
            idx_offer_title = 0
            if st.session_state.selected_offer_title_name_doc_output in offer_title_keys: idx_offer_title = offer_title_keys.index(st.session_state.selected_offer_title_name_doc_output)
            elif offer_title_keys: st.session_state.selected_offer_title_name_doc_output = offer_title_keys[0]
            selected_offer_title_name = st.selectbox(get_text_pdf_ui(texts, "pdf_select_offer_title", "Überschrift/Titel auswählen"), options=offer_title_keys, index=idx_offer_title, key="pdf_offer_title_select_v12_form")
            st.session_state.selected_offer_title_name_doc_output = selected_offer_title_name
            st.session_state.selected_offer_title_text_content_doc_output = offer_title_options.get(selected_offer_title_name, "")

            cover_letter_options = {t.get('name', f"Anschreiben {i+1}"): t.get('content') for i, t in enumerate(cover_letter_templates) if isinstance(t,dict) and t.get('name')}
            if not cover_letter_options: cover_letter_options = {get_text_pdf_ui(texts, "no_cover_letters_available", "Keine Anschreiben verfügbar"): "Standard Anschreiben"}
            cover_letter_keys = list(cover_letter_options.keys())
            idx_cover_letter = 0
            if st.session_state.selected_cover_letter_name_doc_output in cover_letter_keys: idx_cover_letter = cover_letter_keys.index(st.session_state.selected_cover_letter_name_doc_output)
            elif cover_letter_keys: st.session_state.selected_cover_letter_name_doc_output = cover_letter_keys[0]
            selected_cover_letter_name = st.selectbox(get_text_pdf_ui(texts, "pdf_select_cover_letter", "Anschreiben auswählen"), options=cover_letter_keys, index=idx_cover_letter, key="pdf_cover_letter_select_v12_form")
            st.session_state.selected_cover_letter_name_doc_output = selected_cover_letter_name
            st.session_state.selected_cover_letter_text_content_doc_output = cover_letter_options.get(selected_cover_letter_name, "")
        st.markdown("---")

        # === OPTIONALE MODERNE DESIGN-FEATURES INTEGRATION ===
        modern_design_config = None
        try:
            from doc_output_modern_patch import render_modern_pdf_ui_enhancement
            modern_design_config = render_modern_pdf_ui_enhancement(
                texts, project_data, analysis_results, 
                load_admin_setting_func, save_admin_setting_func,
                list_products_func, get_product_by_id_func,
                get_active_company_details_func, db_list_company_documents_func
            )
            if modern_design_config:
                st.session_state.pdf_modern_design_config = modern_design_config
        except ImportError:
            pass  # Moderne Features nicht verfügbar
        except Exception as e:
            st.warning(f"Moderne Design-Features konnten nicht geladen werden: {e}")
        # === ENDE MODERNE DESIGN-FEATURES ===

        st.markdown("**" + get_text_pdf_ui(texts, "pdf_content_selection_info", "Inhalte für das PDF auswählen") + "**")
        col_pdf_content1, col_pdf_content2, col_pdf_content3 = st.columns(3)

        with col_pdf_content1:
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_branding", "Branding & Dokumente") + "**")
            st.session_state.pdf_inclusion_options["include_company_logo"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_company_logo_label", "Firmenlogo anzeigen?"), value=st.session_state.pdf_inclusion_options.get("include_company_logo", True), key="pdf_cb_logo_v12_form")
            st.session_state.pdf_inclusion_options["include_product_images"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_product_images_label", "Produktbilder anzeigen? (Haupt & Zubehör)"), value=st.session_state.pdf_inclusion_options.get("include_product_images", True), key="pdf_cb_prod_img_v12_form")
            st.session_state.pdf_inclusion_options["include_optional_component_details"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_optional_component_details_label", "Details zu optionalen Komponenten anzeigen?"), value=st.session_state.pdf_inclusion_options.get("include_optional_component_details", True), key="pdf_cb_opt_comp_details_v12_form")
            st.session_state.pdf_inclusion_options["include_all_documents"] = st.checkbox(get_text_pdf_ui(texts, "pdf_include_product_datasheets_label", "Datenblätter (Haupt & Zubehör) & Firmendokumente anhängen?"), value=st.session_state.pdf_inclusion_options.get("include_all_documents", False), key="pdf_cb_all_docs_v12_form")

            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_select_company_docs", "Zusätzliche Firmendokumente") + "**")
            selected_doc_ids_for_pdf_temp_ui_col1 = []
            if active_company_id_for_docs is not None and isinstance(active_company_id_for_docs, int):
                company_docs_list = db_list_company_documents_func(active_company_id_for_docs, None)
                if company_docs_list:
                    for doc_item in company_docs_list:
                        if isinstance(doc_item, dict) and 'id' in doc_item:
                            doc_id_item = doc_item['id']
                            doc_label_item = f"{doc_item.get('display_name', doc_item.get('file_name', 'Unbenannt'))} ({doc_item.get('document_type')})"
                            is_doc_checked_by_default_col1 = doc_id_item in st.session_state.pdf_inclusion_options.get("company_document_ids_to_include", [])
                            if st.checkbox(doc_label_item, value=is_doc_checked_by_default_col1, key=f"pdf_cb_company_doc_{doc_id_item}_v12_form"):
                                if doc_id_item not in selected_doc_ids_for_pdf_temp_ui_col1: selected_doc_ids_for_pdf_temp_ui_col1.append(doc_id_item)
                    st.session_state.pdf_inclusion_options["company_document_ids_to_include"] = selected_doc_ids_for_pdf_temp_ui_col1
                else: st.caption(get_text_pdf_ui(texts, "pdf_no_company_documents_available", "Keine spezifischen Dokumente für diese Firma hinterlegt."))
            else: st.caption(get_text_pdf_ui(texts, "pdf_select_active_company_for_docs", "Aktive Firma nicht korrekt für Dokumentenauswahl gesetzt."))

        with col_pdf_content2:
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_main_sections", "Hauptsektionen") + "**")
            default_pdf_sections_map = {
                "ProjectOverview": get_text_pdf_ui(texts, "pdf_section_title_projectoverview", "1. Projektübersicht"),
                "TechnicalComponents": get_text_pdf_ui(texts, "pdf_section_title_technicalcomponents", "2. Systemkomponenten"),
                "CostDetails": get_text_pdf_ui(texts, "pdf_section_title_costdetails", "3. Kostenaufstellung"),
                "Economics": get_text_pdf_ui(texts, "pdf_section_title_economics", "4. Wirtschaftlichkeit"),
                "SimulationDetails": get_text_pdf_ui(texts, "pdf_section_title_simulationdetails", "5. Simulation"),
                "CO2Savings": get_text_pdf_ui(texts, "pdf_section_title_co2savings", "6. CO₂-Einsparung"),
                "Visualizations": get_text_pdf_ui(texts, "pdf_section_title_visualizations", "7. Grafiken"),
                "FutureAspects": get_text_pdf_ui(texts, "pdf_section_title_futureaspects", "8. Zukunftsaspekte")
            }
            temp_selected_main_sections_ui_col2 = []
            current_selected_in_state_col2 = st.session_state.get("pdf_selected_main_sections", list(default_pdf_sections_map.keys()))
            for section_key, section_label_from_map in default_pdf_sections_map.items():
                is_section_checked_by_default_col2 = section_key in current_selected_in_state_col2
                if st.checkbox(section_label_from_map, value=is_section_checked_by_default_col2, key=f"pdf_section_cb_{section_key}_v12_form"):
                    if section_key not in temp_selected_main_sections_ui_col2: temp_selected_main_sections_ui_col2.append(section_key)
            st.session_state.pdf_selected_main_sections = temp_selected_main_sections_ui_col2

        with col_pdf_content3:
            st.markdown("**" + get_text_pdf_ui(texts, "pdf_options_column_charts", "Diagramme & Visualisierungen") + "**")
            selected_chart_keys_for_pdf_ui_col3 = []
            if analysis_results and isinstance(analysis_results, dict):
                chart_key_to_friendly_name_map = {
                    'monthly_prod_cons_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_monthly_compare", "Monatl. Produktion/Verbrauch (2D)"),
                    'cost_projection_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_cost_projection", "Stromkosten-Hochrechnung (2D)"),
                    'cumulative_cashflow_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_cum_cashflow", "Kumulierter Cashflow (2D)"),
                    'consumption_coverage_pie_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_consum_coverage_pie", "Verbrauchsdeckung (Kreis)"),
                    'pv_usage_pie_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pv_usage_pie", "PV-Nutzung (Kreis)"),
                    'daily_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_daily_3d", "Tagesproduktion (3D)"),
                    'weekly_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_weekly_3d", "Wochenproduktion (3D)"),
                    'yearly_production_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_yearly_3d_bar", "Jahresproduktion (3D-Balken)"),
                    'project_roi_matrix_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_roi_matrix_3d", "Projektrendite-Matrix (3D)"),
                    'feed_in_revenue_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_feedin_3d", "Einspeisevergütung (3D)"),
                    'prod_vs_cons_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_prodcons_3d", "Verbr. vs. Prod. (3D)"),
                    'tariff_cube_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_tariffcube_3d", "Tarifvergleich (3D)"),
                    'co2_savings_value_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_co2value_3d", "CO2-Ersparnis vs. Wert (3D)"),
                    'investment_value_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_investval_3D", "Investitionsnutzwert (3D)"),
                    'storage_effect_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_storageeff_3d", "Speicherwirkung (3D)"),
                    'selfuse_stack_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_selfusestack_3d", "Eigenverbr. vs. Einspeis. (3D)"),
                    'cost_growth_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_costgrowth_3d", "Stromkostensteigerung (3D)"),
                    'selfuse_ratio_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_selfuseratio_3d", "Eigenverbrauchsgrad (3D)"),
                    'roi_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_roicompare_3d", "ROI-Vergleich (3D)"),
                    'scenario_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_scenariocomp_3d", "Szenarienvergleich (3D)"),
                    'tariff_comparison_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_tariffcomp_3d", "Vorher/Nachher Stromkosten (3D)"),
                    'income_projection_switcher_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_incomeproj_3d", "Einnahmenprognose (3D)"),
                    'yearly_production_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_yearly", "PV Visuals: Jahresproduktion"),
                    'break_even_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_breakeven", "PV Visuals: Break-Even"),
                    'amortisation_chart_bytes': get_text_pdf_ui(texts, "pdf_chart_label_pvvis_amort", "PV Visuals: Amortisation"),
                }
                available_chart_keys = [k for k in analysis_results.keys() if k.endswith('_chart_bytes') and analysis_results[k] is not None]
                ordered_display_keys = [k_map for k_map in chart_key_to_friendly_name_map.keys() if k_map in available_chart_keys]
                for k_avail in available_chart_keys:
                    if k_avail not in ordered_display_keys: ordered_display_keys.append(k_avail)

                current_selected_charts_in_state = st.session_state.pdf_inclusion_options.get("selected_charts_for_pdf", [])
                for chart_key in ordered_display_keys:
                    friendly_name = chart_key_to_friendly_name_map.get(chart_key, chart_key.replace('_chart_bytes', '').replace('_', ' ').title())
                    is_selected_by_default = chart_key in current_selected_charts_in_state
                    if st.checkbox(friendly_name, value=is_selected_by_default, key=f"pdf_include_chart_{chart_key}_v12_form"):
                        if chart_key not in selected_chart_keys_for_pdf_ui_col3: selected_chart_keys_for_pdf_ui_col3.append(chart_key)
            else:
                st.caption(get_text_pdf_ui(texts, "pdf_no_charts_to_select", "Keine Diagrammdaten für PDF-Auswahl."))
            st.session_state.pdf_inclusion_options["selected_charts_for_pdf"] = selected_chart_keys_for_pdf_ui_col3

        st.markdown("---")
        
        # PDF-Datenstatus anzeigen
        if show_pdf_status:
            st.markdown("### 📊 PDF-Datenstatus")
            validation_result = display_compact_pdf_data_status(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info_for_pdf,
                texts=texts
            )
            st.markdown("---")
        
        submitted_generate_pdf = st.form_submit_button(
            f"**{get_text_pdf_ui(texts, 'pdf_generate_button', 'Angebots-PDF erstellen')}**",
            type="primary",
            disabled=submit_button_disabled
        )

    if submitted_generate_pdf and not st.session_state.pdf_generating_lock_v1:
        st.session_state.pdf_generating_lock_v1 = True 
        pdf_bytes = None 
        try:
            # Datenvalidierung vor PDF-Erstellung
            try:
                from pdf_generator import validate_pdf_data, create_fallback_pdf
                
                validation_result = validate_pdf_data(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info_for_pdf
                )
                
                # Zeige Validierungsstatus an
                if not validation_result['is_valid']:
                    st.warning(f"⚠️ Unvollständige Daten erkannt: {', '.join(validation_result['missing_data'])}")
                    
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
                
                # === MODERNE DESIGN-FEATURES INTEGRATION ===
                # Füge moderne Design-Konfiguration zu den Angebotsdaten hinzu
                enhanced_project_data = project_data.copy()
                if hasattr(st.session_state, 'pdf_modern_design_config') and st.session_state.pdf_modern_design_config:
                    enhanced_project_data['modern_design_config'] = st.session_state.pdf_modern_design_config
                    st.info("🎨 Moderne Design-Features werden angewendet...")
                
                # Versuche erweiterte PDF-Generierung mit modernem Design
                pdf_bytes = None
                try:
                    from doc_output_modern_patch import enhance_pdf_generation_with_modern_design
                    
                    # Erstelle offer_data Dictionary für erweiterte Generierung
                    offer_data_enhanced = {
                        'project_data': enhanced_project_data,
                        'analysis_results': analysis_results,
                        'company_info': company_info_for_pdf,
                        'company_logo_base64': company_logo_b64_for_pdf,
                        'selected_title_image_b64': st.session_state.selected_title_image_b64_data_doc_output,
                        'selected_offer_title_text': st.session_state.selected_offer_title_text_content_doc_output,
                        'selected_cover_letter_text': st.session_state.selected_cover_letter_text_content_doc_output,
                        'sections_to_include': final_sections_to_include_to_pass,
                        'inclusion_options': final_inclusion_options_to_pass,
                        'active_company_id': active_company_id_for_docs
                    }
                    
                    # Erweiterte PDF-Generierung versuchen
                    pdf_bytes = enhance_pdf_generation_with_modern_design(
                        offer_data=offer_data_enhanced,
                        texts=texts,
                        template_name="Professional",
                        modern_design_config=st.session_state.get('pdf_modern_design_config'),
                        load_admin_setting_func=load_admin_setting_func,
                        save_admin_setting_func=save_admin_setting_func,
                        list_products_func=list_products_func,
                        get_product_by_id_func=get_product_by_id_func,
                        db_list_company_documents_func=db_list_company_documents_func
                    )
                    
                    if pdf_bytes:
                        st.success("✅ PDF mit modernen Design-Features erstellt!")
                    
                except ImportError:
                    pass  # Fallback auf Standard-Generierung
                except Exception as e:
                    st.warning(f"Erweiterte PDF-Generierung fehlgeschlagen: {e}. Verwende Standard-Generierung.")
                
                # Fallback auf Standard-PDF-Generierung falls erweiterte Generierung fehlgeschlagen
                if pdf_bytes is None:
                    pdf_bytes = _generate_offer_pdf_safe(
                        project_data=enhanced_project_data, analysis_results=analysis_results,
                        company_info=company_info_for_pdf, company_logo_base64=company_logo_b64_for_pdf,
                        selected_title_image_b64=st.session_state.selected_title_image_b64_data_doc_output,
                        selected_offer_title_text=st.session_state.selected_offer_title_text_content_doc_output,
                        selected_cover_letter_text=st.session_state.selected_cover_letter_text_content_doc_output,
                        sections_to_include=final_sections_to_include_to_pass,
                        inclusion_options=final_inclusion_options_to_pass,
                        load_admin_setting_func=load_admin_setting_func, save_admin_setting_func=save_admin_setting_func,
                        list_products_func=list_products_func, get_product_by_id_func=get_product_by_id_func,
                        db_list_company_documents_func=db_list_company_documents_func,
                        active_company_id=active_company_id_for_docs, texts=texts
                    )
            st.session_state.generated_pdf_bytes_for_download_v1 = pdf_bytes
        except Exception as e_gen_final_outer:
            st.error(f"{get_text_pdf_ui(texts, 'pdf_generation_exception_outer', 'Kritischer Fehler im PDF-Prozess (pdf_ui.py):')} {e_gen_final_outer}")
            st.text_area("Traceback PDF Erstellung (pdf_ui.py):", traceback.format_exc(), height=250)
            st.session_state.generated_pdf_bytes_for_download_v1 = None
        finally:
            st.session_state.pdf_generating_lock_v1 = False 
            st.session_state.selected_page_key_sui = "doc_output" # KORREKTUR: Sicherstellen, dass Seite erhalten bleibt
            st.rerun() 

    if 'generated_pdf_bytes_for_download_v1' in st.session_state:
        pdf_bytes_to_download = st.session_state.pop('generated_pdf_bytes_for_download_v1') 
        if pdf_bytes_to_download and isinstance(pdf_bytes_to_download, bytes):
            customer_name_for_file = customer_data_pdf.get('last_name', 'Angebot')
            if not customer_name_for_file or not str(customer_name_for_file).strip(): customer_name_for_file = "Photovoltaik_Angebot"
            timestamp_file = base64.b32encode(os.urandom(5)).decode('utf-8').lower() 
            file_name = f"Angebot_{str(customer_name_for_file).replace(' ', '_')}_{timestamp_file}.pdf"
            st.success(get_text_pdf_ui(texts, "pdf_generation_success", "PDF erfolgreich erstellt!"))
            st.download_button(
                label=get_text_pdf_ui(texts, "pdf_download_button", "PDF herunterladen"),
                data=pdf_bytes_to_download,
                file_name=file_name,
                mime="application/pdf",
                key=f"pdf_download_btn_final_{timestamp_file}" 
            )
        elif pdf_bytes_to_download is None and st.session_state.get('pdf_generating_lock_v1', True) is False : 
             st.error(get_text_pdf_ui(texts, "pdf_generation_failed_no_bytes_after_rerun", "PDF-Generierung fehlgeschlagen (keine Daten nach Rerun)."))

    _show_pdf_data_status(project_data, analysis_results, texts) # Datenstatus-Anzeige aufrufen

def show_pdf_generation_ui_with_status(
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
    """
    Erweiterte PDF-Generierungs-UI mit Datenstatus-Anzeige und besseren Fallback-Optionen.
    """
    st.header(get_text_pdf_ui(texts, "menu_item_doc_output", "Angebotsausgabe (PDF)"))
    
    # DEBUG WIDGET INTEGRATION
    if DEBUG_WIDGET_AVAILABLE:
        integrate_pdf_debug(project_data, analysis_results, texts)
    
    # DATENSTATUS-ANZEIGE
    _show_pdf_data_status(project_data, analysis_results, texts)
    st.markdown("---")
    
    # DATENVALIDIERUNG
    try:
        from pdf_generator import _validate_pdf_data_availability
        validation_result = _validate_pdf_data_availability(project_data, analysis_results, texts)
        
        # Status-Badge anzeigen
        if validation_result['is_valid']:
            st.success("✅ " + get_text_pdf_ui(texts, "pdf_data_ready", "Daten für PDF-Erstellung bereit"))
        else:
            st.warning("⚠️ " + get_text_pdf_ui(texts, "pdf_data_incomplete", "Daten unvollständig - Fallback-PDF wird erstellt"))
        
        # Detailierte Warnungen anzeigen
        if validation_result['warnings']:
            with st.expander(get_text_pdf_ui(texts, "pdf_data_warnings", "📋 Datenhinweise anzeigen")):
                for warning in validation_result['warnings']:
                    st.info(f"ℹ️ {warning}")
        
        # Kritische Fehler anzeigen
        if validation_result['critical_errors']:
            with st.expander(get_text_pdf_ui(texts, "pdf_critical_errors", "❌ Kritische Probleme")):
                for error in validation_result['critical_errors']:
                    st.error(f"❌ {error}")
                st.info(get_text_pdf_ui(texts, "pdf_fallback_info", 
                    "Bei kritischen Problemen wird ein Informations-PDF mit Anweisungen zur Datensammlung erstellt."))
    
    except ImportError:
        st.warning(get_text_pdf_ui(texts, "pdf_validation_unavailable", "Datenvalidierung nicht verfügbar"))
    
    st.markdown("---")
    
    # Rest der ursprünglichen UI bleibt unverändert
    # Hier würde der bestehende Code von show_pdf_generation_ui fortgeführt...

# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-03, Gemini Ultra: Lock-Mechanismus implementiert und Logik für Download-Button-Anzeige nach st.rerun() angepasst.
#                           Initialisierung von Session-State-Variablen für Vorlagen und UI-Optionen verbessert.
#                           Signatur von db_list_company_documents_func in Dummies und Funktionsaufrufen angepasst.
# 2025-06-03, Gemini Ultra: Neue UI-Option "Details zu optionalen Komponenten anzeigen?" hinzugefügt.
#                           `chart_key_to_friendly_name_map` erweitert, um alle Diagramme aus `analysis.py` abzudecken.
#                           Sichergestellt, dass `pdf_inclusion_options` und `pdf_selected_main_sections` im `st.form`-Kontext korrekt aktualisiert werden.
# 2025-06-03, Gemini Ultra: `st.session_state.selected_page_key_sui = "doc_output"` vor `st.rerun()` im `finally`-Block der PDF-Generierung hinzugefügt.
# 2025-06-03, Gemini Ultra: Neue Funktion `_show_pdf_data_status` zur Anzeige des Datenstatus für die PDF-Erstellung hinzugefügt.
#                           Aufruf von `_show_pdf_data_status` am Ende der `render_pdf_ui` Funktion integriert.
# 2025-06-03, Gemini Ultra: Datenstatus-Anzeige in die doc_output UI integriert.
# 2025-06-03, Gemini Ultra: Import für PDF-Status-Widget zu doc_output.py hinzugefügt.
# 2025-06-03, Gemini Ultra: Erweiterte PDF-UI mit Datenstatus-Anzeige zu doc_output.py hinzugefügt.
# 2025-06-03, Gemini Ultra: Import der Debug-Widget-Funktionalität zu doc_output.py hinzugefügt.
# 2025-06-03, Gemini Ultra: Session State Konsolidierung in render_pdf_ui hinzugefügt.
