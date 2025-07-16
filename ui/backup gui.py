# gui.py
"""Haupt-GUI für Ömer’s Solar-App – kompakte, FUNKTIONSFÄHIGE Version (Mai 2025)."""

from __future__ import annotations # MUSS DIE ALLERERSTE CODE-ZEILE SEIN

import importlib
import traceback
from typing import Any, Callable, Dict, List, Optional, IO, Union
import io
import pandas as pd
import streamlit as st
import sys
import os
import json

# --- BESTEHENDE STRUKTUR ---
EXTRA = os.path.join(sys.prefix, "extras")
if EXTRA not in sys.path:
    sys.path.insert(0, EXTRA)
try:
    import streamlit_shadcn_ui as sui
    SUI_AVAILABLE = True
except ImportError:
    SUI_AVAILABLE = False
    sui = None

import_errors: List[str] = []

# Initialtexte laden
_texts_initial: Dict[str, str] = {}
try:
    _temp_base_dir = os.path.dirname(os.path.abspath(__file__))
    _temp_file_path = os.path.join(_temp_base_dir, 'de.json')
    if os.path.exists(_temp_file_path):
        with open(_temp_file_path, 'r', encoding='utf-8') as f:
            loaded_texts = json.load(f)
            if isinstance(loaded_texts, dict) and loaded_texts:
                _texts_initial = loaded_texts
            else:
                _texts_initial = {"app_title": "Omers Solar Kakerlake"}
    else:
        raise FileNotFoundError("de.json nicht gefunden.")
except (FileNotFoundError, ValueError, json.JSONDecodeError) as e_json_load_specific:
    _texts_initial = {
        "app_title": "Omers Solar Kakerlake", "menu_item_input": "Projekt- Bedarfsanalyse",
        "menu_item_analysis": "Ergebnisse & Visualisierungen", "menu_item_quick_calc": "Schnellkalkulation",
        "menu_item_crm": "Kundenmanagement CRM", "menu_item_info_platform": "Kundenmanagement CRM",
        "menu_item_options": "Administration & Verwaltung", "menu_item_admin": "Administration & Verwaltung",
        "menu_item_doc_output": "Dokumenterstellung & Output", "sidebar_navigation_title": "Angebotserstellung",
        "sidebar_select_area": "Bereich:", "import_errors_title": "⚠️ Ladefehler",
        "db_init_error": "DB Init Fehler:", "module_unavailable": "⚠ Modul fehlt",
        "module_unavailable_details": "Funktion nicht da.", "pdf_creation_no_data_info": "PDF: Bitte zuerst Daten eingeben & berechnen.",
        "gui_critical_error_no_db": "Kritischer Fehler! Datenbankmodul nicht geladen.",
        "gui_critical_error": "Ein kritischer Fehler ist in der Anwendung aufgetreten!",
        "menu_item_heatpump": "Wärmepumpen Simulator",
        "menu_item_crm_dashboard": "Dashboard",
        "menu_item_crm_pipeline": "Pipeline Kunden",
        "menu_item_crm_calendar": "Kalender"
    }
except Exception as e_json_load_general:
    _texts_initial = { "app_title": "Omers Solar Kakerlake" }

TEXTS: Dict[str, str] = {}

locales_module: Optional[Any] = None
database_module: Optional[Any] = None
product_db_module: Optional[Any] = None
data_input_module: Optional[Any] = None
calculations_module: Optional[Any] = None
analysis_module: Optional[Any] = None
crm_module: Optional[Any] = None
admin_panel_module: Optional[Any] = None
doc_output_module: Optional[Any] = None 
quick_calc_module: Optional[Any] = None
info_platform_module: Optional[Any] = None
options_module: Optional[Any] = None
pv_visuals_module: Optional[Any] = None
ai_companion_module: Optional[Any] = None
multi_offer_module: Optional[Any] = None
heatpump_ui_module: Optional[Any] = None
crm_dashboard_ui_module: Optional[Any] = None
crm_pipeline_ui_module: Optional[Any] = None
crm_calendar_ui_module: Optional[Any] = None

_parse_price_matrix_csv_from_calculations: Optional[Callable[[Union[str, io.StringIO], List[str]], Optional[pd.DataFrame]]] = None
_parse_price_matrix_excel_from_calculations: Optional[Callable[[Optional[bytes], List[str]], Optional[pd.DataFrame]]] = None

def import_module_with_fallback(module_name: str, import_errors_list: List[str]):
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError as e:
        error_message = f"Import-Fehler Modul '{module_name}': {e}"
        import_errors_list.append(error_message)
        return None
    except Exception as e_general_import:
        error_message = f"Allg. Import-Fehler Modul '{module_name}': {e_general_import}"
        import_errors_list.append(error_message)
        return None

def get_text_gui(key: str, default_text: Optional[str] = None) -> str:
    base_texts = TEXTS if TEXTS else _texts_initial
    if default_text is None:
        default_text = _texts_initial.get(key, key.replace("_", " ").title() + " (Fallback GUI Text)")
    return base_texts.get(key, default_text)


def initialize_database_once():
    if database_module and callable(getattr(database_module, 'init_db', None)):
        try:
            database_module.init_db() # type: ignore
        except Exception as e_init_db:
            error_msg_db = get_text_gui("db_init_error", "Fehler bei DB-Initialisierung:") + f" {e_init_db}"
            import_errors.append(error_msg_db)
    else:
        error_msg_db_mod_missing = get_text_gui("db_init_error", "Fehler bei DB-Initialisierung:") + " database_module oder init_db Funktion nicht verfügbar."
        import_errors.append(error_msg_db_mod_missing)

def main():
    global TEXTS # Erlaube Modifikation der globalen TEXTS Variable
    
    loaded_translations: Any = None 

    if locales_module and callable(getattr(locales_module, 'load_translations', None)):
        try:
            loaded_translations = locales_module.load_translations('de')
        except Exception as e_load_loc:
            # print(f"GUI FEHLER: locales_module.load_translations('de') ist fehlgeschlagen: {e_load_loc}") # Logging für Entwickler
            if 'import_errors' in globals() and isinstance(globals()['import_errors'], list):
                globals()['import_errors'].append(f"Fehler beim Laden der Übersetzungen: {e_load_loc}")
            loaded_translations = None 
    
    if isinstance(loaded_translations, dict) and loaded_translations: 
        TEXTS = loaded_translations
    else:
        if loaded_translations is not None: 
            if 'import_errors' in globals() and isinstance(globals()['import_errors'], list):
                globals()['import_errors'].append(f"WARNUNG: Übersetzungsdaten (locales.py) sind kein gültiges Dictionary (Typ: {type(loaded_translations)}). Verwende Fallback-Texte.")
            # else: print(f"GUI WARNUNG: Übersetzungsdaten (locales.py) sind kein gültiges Dictionary (Typ: {type(loaded_translations)}). Verwende Fallback-Texte.") # Logging für Entwickler
        
        if isinstance(_texts_initial, dict):
            TEXTS = _texts_initial.copy()
        else: 
            TEXTS = {"app_title": "Solar App (Kritischer Text-Fallback)"}
            if 'import_errors' in globals() and isinstance(globals()['import_errors'], list):
                globals()['import_errors'].append("KRITISCH: _texts_initial ist kein Dictionary! Minimale Fallback-Texte verwendet.")
            # else: print("GUI KRITISCH: _texts_initial ist kein Dictionary! Minimale Fallback-Texte verwendet.") # Logging für Entwickler


    st.set_page_config(page_title=get_text_gui("app_title"), layout="wide")
    
    # KORREKTUR: Initialisierung von project_data, falls es nicht existiert.    # Dies verhindert, dass `project_data` bei einem unerwarteten Rerun verloren geht, bevor es von `data_input.py` initialisiert wurde.
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {'customer_data': {}, 'project_details': {}, 'economic_data': {}}
    if 'calculation_results' not in st.session_state: # Sicherstellen, dass auch calc_results initialisiert ist
        st.session_state.calculation_results = {}

    with st.sidebar:
        st.title(get_text_gui("sidebar_navigation_title"))
        page_options = {
            get_text_gui("menu_item_input"): "input",
            get_text_gui("menu_item_analysis"): "analysis",
            get_text_gui("menu_item_quick_calc"): "quick_calc",
            get_text_gui("menu_item_crm"): "crm",
            get_text_gui("menu_item_heatpump"): "heatpump",           # NEU
            get_text_gui("menu_item_crm_dashboard"): "crm_dashboard", # NEU
            get_text_gui("menu_item_crm_pipeline"): "crm_pipeline",   # NEU
            get_text_gui("menu_item_crm_calendar"): "crm_calendar",   # NEU
            get_text_gui("menu_item_info_platform"): "info_platform",
            get_text_gui("menu_item_options"): "options",
            get_text_gui("menu_item_admin"): "admin",
            get_text_gui("menu_item_doc_output"): "doc_output"
        }
        page_options_list = list(page_options.items())
    

        if 'selected_page_key_sui' not in st.session_state:
            st.session_state.selected_page_key_sui = page_options_list[0][1] 

        # Temporärer Speicher für den zuletzt ausgewählten Key, um "Springen" durch Reruns während der Sidebar-Erstellung zu minimieren
        # Diese Variable wird nur während des Sidebar-Renders verwendet.
        _current_render_selected_key = st.session_state.selected_page_key_sui

        for label, key in page_options_list:
            button_variant = "default" if _current_render_selected_key != key else "secondary"
            
            # KORREKTUR: Verwende einen eindeutigen, aber stabilen Key für die Navigationsbuttons.
            # Der Navigations-State wird über `st.session_state.selected_page_key_sui` verwaltet.
            # Das `st.rerun()` nach dem Klick ist korrekt, um die Seite neu zu laden.
            nav_button_key = f"nav_button_to_{key}" # Stabiler Key

            if SUI_AVAILABLE and sui:
                try:
                    if sui.button(label, key=nav_button_key, variant=button_variant, className="w-full justify-start mb-1"):
                        if st.session_state.selected_page_key_sui != key: # Nur Rerun, wenn sich die Seite ändert
                            st.session_state.selected_page_key_sui = key
                            st.rerun() 
                except AttributeError: 
                    if st.sidebar.button(label or "Unbenannter Button", key=nav_button_key, use_container_width=True):
                        if st.session_state.selected_page_key_sui != key:
                            st.session_state.selected_page_key_sui = key
                            st.rerun()
                    if key == page_options_list[0][1] and "sui_button_fallback_warning" not in st.session_state:
                         st.sidebar.warning("Hinweis: sui.button nicht optimal. Standard-Buttons als Fallback.") 
                         st.session_state.sui_button_fallback_warning = True
            else: 
                if st.sidebar.button(label or "Unbenannter Button", key=nav_button_key, use_container_width=True):
                    if st.session_state.selected_page_key_sui != key:
                        st.session_state.selected_page_key_sui = key
                        st.rerun()
                if key == page_options_list[0][1] and "sui_unavailable_warning" not in st.session_state and not SUI_AVAILABLE:
                    st.sidebar.info("Hinweis: streamlit_shadcn_ui nicht verfügbar. Standard-Buttons werden verwendet.")
                    st.session_state.sui_unavailable_warning = True
        
        selected_page_key = st.session_state.selected_page_key_sui


    if import_errors:
        with st.sidebar:
            st.markdown("---"); st.subheader(get_text_gui("import_errors_title"))
            for error_msg in import_errors: st.error(error_msg)
            st.markdown("---")

    conn = database_module.get_db_connection() if database_module else None
    
    page_render_map = {
        "input": (data_input_module, "display_data_input"),
        "analysis": (analysis_module, "display_analysis_dashboard"),
        "admin": (admin_panel_module, "display_admin_panel"),
        "doc_output": (doc_output_module, "display_doc_output_ui"),
        "quick_calc": (quick_calc_module, "render_quick_calc"),
        "crm": (crm_module, "render_crm"),
        "info_platform": (info_platform_module, "render_info_platform"),
        "options": (options_module, "display_options_ui"),
        # Neue Seiten
        "heatpump": (heatpump_ui_module, "display_heatpump_ui"),
        "crm_dashboard": (crm_dashboard_ui_module, "display_crm_dashboard_ui"),
        "crm_pipeline": (crm_pipeline_ui_module, "display_pipeline_ui"),
        "crm_calendar": (crm_calendar_ui_module, "display_calendar_ui"),
    }

    module_to_render, func_name = page_render_map.get(selected_page_key, (None, None))
   
    # Seiten-Rendering basierend auf Auswahl
    if selected_page_key == "input":
        st.header(get_text_gui("menu_item_input"))
        if data_input_module and callable(getattr(data_input_module, 'render_data_input', None)):
            # KORREKTUR: `render_data_input` sollte `st.session_state.project_data` direkt modifizieren
            # und muss es nicht unbedingt zurückgeben. Der Rückgabewert wird hier nicht mehr benötigt.
            data_input_module.render_data_input(TEXTS) 
        else:
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_input", "Eingabemodul nicht verfügbar.")))

    elif selected_page_key == "analysis":
        st.header(get_text_gui("menu_item_analysis"))
        if analysis_module and callable(getattr(analysis_module, 'render_analysis', None)):
            try:
                analysis_module.render_analysis(TEXTS, st.session_state.get("calculation_results")) # calculation_results direkt übergeben
            except Exception as e_render_analysis:
                st.error(f"Fehler beim Rendern des Analyse-Tabs: {e_render_analysis}")
                st.text_area("Traceback Analysis:", traceback.format_exc(), height=200)
        else:
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_analysis", "Analysemodul nicht verfügbar.")))

    elif selected_page_key == "admin":
        st.header(get_text_gui("menu_item_admin"))
        required_modules_for_admin_render = [admin_panel_module, database_module, product_db_module, calculations_module]
        if all(m is not None for m in required_modules_for_admin_render) and callable(getattr(admin_panel_module, 'render_admin_panel', None)):
            admin_kwargs_pass = {
                "texts": TEXTS, # KORREKTUR: TEXTS direkt übergeben, statt als Tuple zu versuchen
                "get_db_connection_func": getattr(database_module, 'get_db_connection', None),
                "save_admin_setting_func": getattr(database_module, 'save_admin_setting', None),
                "load_admin_setting_func": getattr(database_module, 'load_admin_setting', None),
                "parse_price_matrix_csv_func": _parse_price_matrix_csv_from_calculations, 
                "parse_price_matrix_excel_func": _parse_price_matrix_excel_from_calculations, 
                "list_products_func": getattr(product_db_module, 'list_products', None),
                "add_product_func": getattr(product_db_module, 'add_product', None),
                "update_product_func": getattr(product_db_module, 'update_product', None),
                "delete_product_func": getattr(product_db_module, 'delete_product', None),
                "get_product_by_id_func": getattr(product_db_module, 'get_product_by_id', None),
                "get_product_by_model_name_func": getattr(product_db_module, 'get_product_by_model_name', None),
                "list_product_categories_func": getattr(product_db_module, 'list_product_categories', None),
                "db_list_companies_func": getattr(database_module, 'list_companies', None),
                "db_add_company_func": getattr(database_module, 'add_company', None),
                "db_get_company_by_id_func": getattr(database_module, 'get_company', None),
                "db_update_company_func": getattr(database_module, 'update_company', None),
                "db_delete_company_func": getattr(database_module, 'delete_company', None),
                "db_set_default_company_func": getattr(database_module, 'set_default_company', None),
                "db_add_company_document_func": getattr(database_module, 'add_company_document', None),
                "db_list_company_documents_func": getattr(database_module, 'list_company_documents', None),
                "db_delete_company_document_func": getattr(database_module, 'delete_company_document', None)
            }
            all_critical_funcs_valid = True
            for func_name_key, func_obj in admin_kwargs_pass.items():
                 if func_name_key.endswith('_func'):
                     is_callable_admin = callable(func_obj)
                     if func_name_key in ["parse_price_matrix_csv_func", "parse_price_matrix_excel_func", "get_db_connection_func", "save_admin_setting_func", "load_admin_setting_func"]:
                         if not is_callable_admin: all_critical_funcs_valid = False; 
            if not all_critical_funcs_valid:
                 st.error("Einige Kernfunktionen für das Admin-Panel (DB-Zugriff oder Parser) konnten nicht geladen werden. Bitte Terminal prüfen.")
            else:
                try: admin_panel_module.render_admin_panel(**admin_kwargs_pass) # type: ignore
                except Exception as e_render_admin:
                    st.error(f"Fehler im Admin-Panel: {e_render_admin}")
                    st.text_area("Traceback Admin:", traceback.format_exc(), height=200)
        else:
            missing_modules_admin_list = [name for name, mod in [("Admin-Panel", admin_panel_module), ("Datenbank", database_module), ("Produkt-DB", product_db_module), ("Berechnungen", calculations_module)] if not mod]
            st.warning(get_text_gui("module_unavailable_details", f"Admin-Panel oder dessen Abhängigkeiten ({', '.join(missing_modules_admin_list)}) nicht verfügbar."))

    elif selected_page_key == "doc_output":
        st.header(get_text_gui("menu_item_doc_output"))
        
        # Tabs für PDF-Ausgabe erstellen
        tab_single_pdf, tab_multi_offers = st.tabs(["📄 Einzelangebot PDF", "🏢 Multi-Firmen-Angebote"])
        
        with tab_single_pdf:
            if doc_output_module and database_module and product_db_module and callable(getattr(doc_output_module, 'render_pdf_ui', None)):
                project_data_doc = st.session_state.get('project_data', {})
                calc_results_doc = st.session_state.get("calculation_results", {})
                if not project_data_doc or not project_data_doc.get('project_details',{}).get('module_quantity') or not calc_results_doc: 
                    st.info(get_text_gui("pdf_creation_no_data_info"))
                else:
                    pdf_ui_kwargs_pass = {
                        "texts": TEXTS, "project_data": project_data_doc, "analysis_results": calc_results_doc,
                        "load_admin_setting_func": getattr(database_module, 'load_admin_setting', None),
                        "save_admin_setting_func": getattr(database_module, 'save_admin_setting', None), 
                        "list_products_func": getattr(product_db_module, 'list_products', None), 
                        "get_product_by_id_func": getattr(product_db_module, 'get_product_by_id', None), 
                        "get_active_company_details_func": getattr(database_module, 'get_active_company', None),
                        "db_list_company_documents_func": getattr(database_module, 'list_company_documents', None)
                    }
                    critical_funcs_for_pdf_check = [ val for key, val in pdf_ui_kwargs_pass.items() if key.endswith("_func") ]
                    if not all(f is not None and callable(f) for f in critical_funcs_for_pdf_check):
                         st.error("Einige Kernfunktionen für die PDF-Ausgabe (DB-Zugriff o.ä.) konnten nicht geladen werden oder sind nicht aufrufbar.")
                    else:
                        try: doc_output_module.render_pdf_ui(**pdf_ui_kwargs_pass) # type: ignore
                        except Exception as e_render_pdf:
                            st.error(f"Fehler beim Rendern der PDF UI: {e_render_pdf}")
                            st.text_area("Traceback PDF UI:", traceback.format_exc(), height=200)
            else:
                st.warning(get_text_gui("module_unavailable_details", "PDF-Ausgabemodul oder dessen Abhängigkeiten sind nicht verfügbar."))
        
        with tab_multi_offers:
            st.subheader("🏢 Multi-Firmen-Angebotsgenerator")
            if multi_offer_module and callable(getattr(multi_offer_module, 'render_multi_offer_generator', None)):
                multi_offer_module.render_multi_offer_generator(TEXTS, project_data_doc, calc_results_doc)

                # Aufruf der neuen Produktauswahl-Logik
                if hasattr(multi_offer_module, 'render_product_selection'):
                    multi_offer_module.render_product_selection()
            else:
                st.warning("⚠️ Multi-Angebots-Modul nicht verfügbar.")
    
    elif selected_page_key == "quick_calc":
        st.header(get_text_gui("menu_item_quick_calc"))
        if quick_calc_module and callable(getattr(quick_calc_module, 'render_quick_calc', None)):
             quick_calc_module.render_quick_calc(TEXTS, module_name=get_text_gui("menu_item_quick_calc")) # type: ignore
        else: st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_quick_calc","Schnellkalkulation nicht verfügbar.")))
    elif selected_page_key == "crm":
        st.header(get_text_gui("menu_item_crm"))
        if crm_module and database_module and callable(getattr(crm_module, 'render_crm', None)):
            crm_module.render_crm(TEXTS, getattr(database_module, 'get_db_connection', None)) # type: ignore
        else: st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm","CRM nicht verfügbar.")))
    elif selected_page_key == "info_platform":
        st.header(get_text_gui("menu_item_info_platform"))
        if info_platform_module and callable(getattr(info_platform_module, 'render_info_platform', None)):
            info_platform_module.render_info_platform(TEXTS, module_name=get_text_gui("menu_item_info_platform")) # type: ignore
        else: st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_info","Info-Plattform nicht verfügbar.")))
    elif selected_page_key == "options":
        st.header(get_text_gui("menu_item_options"))
          # Tabs für die Optionen erstellen
        tab_general, tab_ai = st.tabs(["⚙️ Allgemeine Einstellungen", "🤖 AI-Begleiter"])
        
        with tab_general:
            if options_module and callable(getattr(options_module, 'render_options', None)):
                options_module.render_options(TEXTS, module_name=get_text_gui("menu_item_options")) # type: ignore
            else: 
                st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_options","Optionen nicht verfügbar.")))
                
        with tab_ai:
            st.subheader("🤖 AI-Begleiter (DeepSeek)")
            if ai_companion_module and callable(getattr(ai_companion_module, 'render_ai_companion', None)):
                ai_companion_module.render_ai_companion()
            else:
                st.warning("⚠️ AI-Begleiter Modul nicht verfügbar.")
    elif selected_page_key == "heatpump":
        st.header(get_text_gui("menu_item_heatpump"))
        if heatpump_ui_module and callable(getattr(heatpump_ui_module, 'render_heatpump', None)):
            heatpump_ui_module.render_heatpump(TEXTS, module_name=get_text_gui("menu_item_heatpump")) # type: ignore
        else: 
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_heatpump","Schnellkalkulation nicht verfügbar.")))
    elif selected_page_key == "crm_dashboard":
        st.header(get_text_gui("menu_item_crm_dashboard"))
        if crm_dashboard_ui_module and callable(getattr(crm_dashboard_ui_module, 'render_crm_dashboard', None)):
            crm_dashboard_ui_module.render_crm_dashboard(TEXTS, module_name=get_text_gui("menu_item_crm_dashboard")) # type: ignore
        else: 
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm_dashboard","Schnellkalkulation nicht verfügbar.")))
              elif selected_page_key == "crm_pipeline":
        st.header(get_text_gui("menu_item_crm_pipeline"))
        if crm_pipeline_ui_module and callable(getattr(crm_pipeline_ui_module, 'render_crm_pipeline', None)):
            crm_pipeline_ui_module.render_crm_pipeline(TEXTS, module_name=get_text_gui("menu_item_crm_pipeline")) # type: ignore
        else: 
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm_pipeline","Schnellkalkulation nicht verfügbar.")))
            
    elif selected_page_key == "crm_calendar":
        st.header(get_text_gui("menu_item_crm_calendar"))        if crm_calendar_ui_module and callable(getattr(crm_calendar_ui_module, 'render_crm_calendar', None)):
            crm_calendar_ui_module.render_crm_calendar(TEXTS, module_name=get_text_gui("menu_item_crm_calendar")) # type: ignore
        else: 
            st.warning(get_text_gui("module_unavailable_details", get_text_gui("fallback_title_crm_calendar","Schnellkalkulation nicht verfügbar.")))


if __name__ == "__main__":
    try:
        locales_module = import_module_with_fallback("locales", import_errors)
        database_module = import_module_with_fallback("database", import_errors)
        product_db_module = import_module_with_fallback("product_db", import_errors) 
        data_input_module = import_module_with_fallback("data_input", import_errors)
        calculations_module = import_module_with_fallback("calculations", import_errors)
        analysis_module = import_module_with_fallback("analysis", import_errors)
        crm_module = import_module_with_fallback("crm", import_errors)
        admin_panel_module = import_module_with_fallback("admin_panel", import_errors)
        doc_output_module = import_module_with_fallback("pdf_ui", import_errors)
        quick_calc_module = import_module_with_fallback("quick_calc", import_errors)
        info_platform_module = import_module_with_fallback("options", import_errors)
        options_module = import_module_with_fallback("options", import_errors)
        pv_visuals_module = import_module_with_fallback("pv_visuals", import_errors)
        ai_companion_module = import_module_with_fallback("ai_companion", import_errors)
        multi_offer_module = import_module_with_fallback("multi_offer_generator", import_errors)
        crm_calendar_module = import_module_with_fallback("crm_calendar_ui", import_errors)
        crm_pipeline_ui_module = import_module_with_fallback("crm_pipeline_ui", import_errors)
        crm_dashboard_ui_module = import_module_with_fallback("crm_dashboard_ui", import_errors)
        heatpump_ui_module = import_module_with_fallback("heatpump_ui", import_errors)
        
        if calculations_module:
            if hasattr(calculations_module, 'parse_module_price_matrix_csv'):
                _parse_price_matrix_csv_from_calculations = calculations_module.parse_module_price_matrix_csv
            if hasattr(calculations_module, 'parse_module_price_matrix_excel'): 
                _parse_price_matrix_excel_from_calculations = calculations_module.parse_module_price_matrix_excel

        if 'db_initialized' not in st.session_state:
            if database_module: initialize_database_once()
            st.session_state['db_initialized'] = True
            
        if database_module: 
            main()
        else:
            st.set_page_config(page_title=_texts_initial.get("app_title", "Fehler"), layout="wide")
            st.error(get_text_gui("gui_critical_error_no_db", "Datenbankmodul nicht geladen. Anwendung kann nicht starten."))
            if import_errors:
                with st.sidebar:
                    st.subheader("Ladefehler")
                    for err_msg_display in import_errors: st.error(err_msg_display)

    except Exception as e_global_gui_main_block:
        critical_error_text_for_display_main_block = get_text_gui("gui_critical_error", "Ein kritischer Fehler ist in der Anwendung aufgetreten!")
        try:
            if not getattr(st, "_is_page_config_allowed", True): 
                 st.set_page_config(page_title="Kritischer Fehler", layout="wide")
            st.error(f"{critical_error_text_for_display_main_block}\nDetails: {e_global_gui_main_block}")
            st.text_area("Traceback Global:", traceback.format_exc(), height=300)
        except Exception: pass
# Änderungshistorie
# 2025-06-03, Gemini Ultra: Globale Variable TEXTS direkt zugewiesen und Fallback-Logik für Textinitialisierung robuster gestaltet.
#                           Sichergestellt, dass `st.session_state.project_data` und `calculation_results` initialisiert werden.
#                           Navigationslogik in der Sidebar angepasst, um `st.rerun()` nur bei tatsächlichem Seitenwechsel auszulösen.
#                           Übergabe von `st.session_state.calculation_results` an `analysis_module.render_analysis` sichergestellt.
#                           Rückgabewert von `data_input_module.render_data_input` wird nicht mehr explizit in `st.session_state.project_data` in `gui.py` geschrieben, da das Modul dies intern handhaben sollte.
#                           Die `texts`-Variable für `render_admin_panel` wird nun als Dictionary übergeben.
# 2025-06-04, Gemini Ultra: Multi-Angebots-Modul zu PDF-Ausgabe hinzugefügt.
# 2025-06-05, Gemini Ultra: Neue Produktauswahl-Logik in die Multi-Firmen-Angebots-UI integriert.