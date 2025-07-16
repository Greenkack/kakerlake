# admin_panel.py
"""
Datei: admin_panel.py
Zweck: Modul für den Admin Panel Tab (F) - UI-Anpassungen für Wirtschaftlichkeit, Produkte und PDF-Vorlagen.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-04 (Überarbeitet für Syntaxkonsistenz)
"""
import streamlit as st
import pandas as pd
from typing import List, Optional, Union, Dict, Any, Callable, Tuple
import traceback
import os
import io
import json
import base64
from datetime import datetime

# NEU: Definition von WIDGET_KEY_SUFFIX, um NameError zu beheben
# Dieser Suffix wird verwendet, um die Eindeutigkeit von Streamlit-Widget-Keys
# innerhalb dieses Admin-Panels sicherzustellen.
WIDGET_KEY_SUFFIX = "_apv1" # "apv1" steht für Admin Panel Version 1 (oder ein anderer eindeutiger Bezeichner)

# --- Globale Dummies und Funktionsreferenzen für Fallback ---
_DEFAULT_GLOBAL_CONSTANTS_FALLBACK: Dict[str, Any] = {
    'vat_rate_percent': 0.0, 'electricity_price_increase_annual_percent': 3.0,
    'simulation_period_years': 20, 'inflation_rate_percent': 2.0,
    'loan_interest_rate_percent': 4.0, 'capital_gains_tax_kest_percent': 26.375,
    'alternative_investment_interest_rate_percent': 5.0,
    'co2_emission_factor_kg_per_kwh': 0.474, 'maintenance_costs_base_percent': 1.5,
    'einspeiseverguetung_period_years': 20, 'marktwert_strom_eur_per_kwh_after_eeg': 0.03,
    'storage_cycles_per_year': 250, 'storage_efficiency': 0.9,
    'eauto_annual_km': 10000, 'eauto_consumption_kwh_per_100km': 18.0,
    'eauto_pv_share_percent': 30.0, 'heatpump_cop_factor': 3.5,
    'heatpump_pv_share_percent': 40.0, 'afa_period_years': 20,
    'pvgis_system_loss_default_percent': 14.0, 'annual_module_degradation_percent': 0.5,
    'maintenance_fixed_eur_pa': 50.0, 'maintenance_variable_eur_per_kwp_pa': 5.0,
    'maintenance_increase_percent_pa': 2.0, 'one_time_bonus_eur': 0.0,
    'global_yield_adjustment_percent': 0.0, 'reference_specific_yield_pr': 1100.0,
    'specific_yields_by_orientation_tilt': {
        "Süd_0":1050.0, "Süd_15":1080.0, "Süd_30":1100.0, "Süd_45":1080.0, "Süd_60":1050.0,
        "Südost_0":980.0, "Südost_15":1030.0, "Südost_30":1070.0, "Südost_45":1030.0, "Südost_60":980.0,
        "Südwest_0":980.0, "Südwest_15":1030.0, "Südwest_30":1070.0, "Südwest_45":1030.0, "Südwest_60":980.0,
        "Ost_0":950.0, "Ost_15":980.0, "Ost_30":1000.0, "Ost_45":980.0, "Ost_60":950.0,
        "West_0":950.0, "West_15":980.0, "West_30":1000.0, "West_45":980.0, "West_60":950.0,
        "Nord_0":800.0, "Nord_15":820.0, "Nord_30":850.0, "Nord_45":820.0, "Nord_60":850.0,
        "Nordost_0":850.0, "Nordost_15":870.0, "Nordost_30":890.0, "Nordost_45":870.0, "Nordost_60":850.0,
        "Nordwest_0":850.0, "Nordwest_15":870.0, "Nordwest_30":890.0, "Nordwest_45":870.0, "Nordwest_60":850.0,
        "Flachdach_0":950.0, "Flachdach_15":1000.0,
        "Sonstige_0":1000.0, "Sonstige_15":1050.0, "Sonstige_30":1080.0, "Sonstige_45":1050.0, "Sonstige_60":1000.0
    },
    'default_specific_yield_kwh_kwp': 950.0,
    'monthly_production_distribution': [0.03,0.05,0.08,0.11,0.13,0.14,0.13,0.12,0.09,0.06,0.04,0.02],
    'monthly_consumption_distribution': [1/12]*12, 
    'direct_self_consumption_factor_of_production': 0.25,
    'co2_per_tree_kg_pa': 12.5, 'co2_per_car_km_kg': 0.12, 'co2_per_flight_muc_pmi_kg': 180.0,
    'economic_settings': {'reference_specific_yield_for_pr_kwh_per_kwp': 1100.0}, 
    'default_performance_ratio_percent': 78.0, 'peak_shaving_effect_kw_estimate': 0.0,
    'optimal_storage_factor': 1.0, 'app_debug_mode_enabled': False, 'active_company_id': None,
    "visualization_settings": {
        "default_color_palette": "Plotly", "primary_chart_color": "#1f77b4",
        "secondary_chart_color": "#ff7f0e", "chart_font_family": "Arial, sans-serif",
        "chart_font_size_title": 16, "chart_font_size_axis_label": 12,
        "chart_font_size_tick_label": 10,
        "cost_overview_chart": {"chart_type": "bar", "color_palette": "Plotly Standard", "primary_color_bar": "#1f77b4", "show_values_on_chart": True },
        "consumption_coverage_chart": {"chart_type": "pie", "color_palette": "Pastel", "show_percentage": True, "show_labels": True},
        "pv_usage_chart": {"chart_type": "pie", "color_palette": "Grün-Variationen", "show_percentage": True},
        "monthly_prod_cons_chart": {"chart_type": "line", "line_color_production": "#2ca02c", "line_color_consumption": "#d62728", "show_markers": True},
        "cumulative_cashflow_chart": {"chart_type": "line", "line_color": "#17becf", "show_zero_line": True}
    }
}
_DEFAULT_FEED_IN_TARIFFS_FALLBACK: Dict[str, List[Dict[str, Any]]] = {
    "parts": [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 7.94},
              {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 6.88},
              {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 5.62}],
    "full": [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.60},
             {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 10.56},
             {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 10.56}] 
}

def _dummy_load_admin_setting(key, default=None):
    if key == 'pdf_title_image_templates': return []
    elif key == 'pdf_offer_title_templates': return []
    elif key == 'pdf_cover_letter_templates': return []
    elif key == 'pdf_design_settings': return {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
    elif key == 'global_constants': return _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.copy()
    elif key == 'feed_in_tariffs': return _DEFAULT_FEED_IN_TARIFFS_FALLBACK.copy()
    elif key == 'visualization_settings': return _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.get('visualization_settings', {}).copy()
    elif key in ["Maps_api_key", "bing_maps_api_key", "osm_nominatim_email"]: return ""
    return default
def _dummy_save_admin_setting(key, value): return False
def _dummy_list_products(category: Optional[str] = None) -> List[Dict[str, Any]]: return []
def _dummy_add_product(product_data: Dict[str, Any]) -> Optional[int]: return None
def _dummy_update_product(product_id: Union[int, float], product_data: Dict[str, Any]) -> bool: return False
def _dummy_delete_product(product_id: Union[int, float]) -> bool: return False
def _dummy_get_product_by_id(product_id: Union[int,float]) -> Optional[Dict[str, Any]]: return None
def _dummy_get_product_by_model_name(model_name: str) -> Optional[Dict[str, Any]]: return None
def _dummy_list_product_categories() -> List[str]: return ["Modul", "Wechselrichter", "Batteriespeicher"]
def _dummy_list_companies() -> List[Dict[str, Any]]: return []
def _dummy_add_company(company_data: Dict[str, Any]) -> Optional[int]: return None
def _dummy_get_company_by_id(company_id: int) -> Optional[Dict[str, Any]]: return None
def _dummy_update_company(company_id: int, company_data: Dict[str, Any]) -> bool: return False
def _dummy_delete_company(company_id: int) -> bool: return False
def _dummy_set_default_company(company_id: int) -> bool: return False
def _dummy_add_company_document(company_id: int, display_name: str, document_type: str, original_filename: str, file_content_bytes: bytes) -> Optional[int]: return None
def _dummy_list_company_documents(company_id: int, doc_type: Optional[str]=None) -> List[Dict[str, Any]]: return []
def _dummy_delete_company_document(document_id: int) -> bool: return False
def _dummy_parse_price_matrix_csv(csv_data: Union[str, io.StringIO], errors_list: List[str]) -> Optional[pd.DataFrame]:
    if errors_list is not None: errors_list.append("Dummy-Parser für Preis-Matrix CSV aktiv.")
    return None

_load_admin_setting_safe: Callable = _dummy_load_admin_setting
_save_admin_setting_safe: Callable = _dummy_save_admin_setting
_parse_price_matrix_csv_safe: Callable = _dummy_parse_price_matrix_csv
_parse_price_matrix_excel_func: Optional[Callable[[Optional[bytes], List[str]], Optional[pd.DataFrame]]] = None
_list_products_safe: Callable = _dummy_list_products
_add_product_safe: Callable = _dummy_add_product
_update_product_safe: Callable = _dummy_update_product
_delete_product_safe: Callable = _dummy_delete_product
_get_product_by_id_safe: Callable = _dummy_get_product_by_id
_get_product_by_model_name_safe: Callable = _dummy_get_product_by_model_name
_list_product_categories_safe: Callable = _dummy_list_product_categories
_list_companies_safe: Callable = _dummy_list_companies
_add_company_safe: Callable = _dummy_add_company
_get_company_by_id_safe: Callable = _dummy_get_company_by_id
_update_company_safe: Callable = _dummy_update_company
_delete_company_safe: Callable = _dummy_delete_company
_set_default_company_safe: Callable = _dummy_set_default_company
_add_company_document_safe: Callable = _dummy_add_company_document
_list_company_documents_safe: Callable = _dummy_list_company_documents
_delete_company_document_safe: Callable = _dummy_delete_company_document

ADMIN_TAB_KEYS_DEFINITION_GLOBAL = [
    "admin_tab_company_management_new", "admin_tab_product_management", "admin_tab_general_settings",
    "admin_tab_price_matrix", "admin_tab_tariff_management", "admin_tab_pdf_design",
    "admin_tab_pdf_title_images", "admin_tab_pdf_offer_titles", "admin_tab_pdf_cover_letters",
    "admin_tab_visualization_settings",
    "admin_tab_advanced"
]

def get_text_local(key: str, fallback_text: str) -> str:
    admin_texts_dict = st.session_state.get('_admin_panel_texts', {})
    if not isinstance(admin_texts_dict, dict):
        admin_texts_dict = {}
    return admin_texts_dict.get(key, fallback_text)

def parse_module_price_matrix_excel( 
    excel_bytes: Optional[bytes], 
    errors_list: List[str]
) -> Optional[pd.DataFrame]:
    if not excel_bytes:
        errors_list.append("Preis-Matrix (Excel): Übergebene Excel-Daten sind leer.")
        return None
    try:
        excel_file_like = io.BytesIO(excel_bytes)
        df = pd.read_excel(excel_file_like, index_col=0, header=0)
        if df.empty:
            if df.index.name is None or str(df.index.name).strip().lower() not in ['anzahl module', 'anzahl_module']:
                 errors_list.append("Preis-Matrix (Excel): Excel-Datei ist leer oder die erste Spalte (erwartet: 'Anzahl Module') fehlt oder ist leer.")
            else: 
                 errors_list.append("Preis-Matrix (Excel): Excel-Datei enthält keine Datenzeilen unterhalb des Headers und des Index.")
            return None
        df.index.name = 'Anzahl Module'
        df.index = pd.to_numeric(df.index, errors='coerce')
        df = df[df.index.notna()] 
        if df.empty:
            errors_list.append("Preis-Matrix (Excel): Index ('Anzahl Module') enthält keine gültigen Zahlen nach der Konvertierung oder alle Zeilen hatten ungültige Indexwerte.")
            return None
        df.index = df.index.astype(int)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(r'[^\d,.-]', '', regex=True) 
                df[col] = df[col].str.replace('.', '', regex=False) 
                df[col] = df[col].str.replace(',', '.', regex=False) 
            df[col] = pd.to_numeric(df[col], errors='coerce') 
        df.dropna(axis=0, how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        if df.empty:
            errors_list.append("Preis-Matrix (Excel): Nach der Verarbeitung (Bereinigung, Typkonvertierung, Entfernung leerer Zeilen/Spalten) ist die Matrix leer.")
            return None
        return df
    except ValueError as ve: 
        errors_list.append(f"Preis-Matrix (Excel): Wert-Fehler beim Parsen der Excel-Datei: {ve}. Bitte Zahlenformate prüfen.")
        return None
    except Exception as e: 
        errors_list.append(f"Preis-Matrix (Excel): Ein unbekannter Fehler ist beim Parsen der Excel-Datei aufgetreten: {e}")
        traceback.print_exc()
        return None

def render_company_crud_tab(
    db_list_companies_func: Callable[[], List[Dict[str, Any]]],
    db_add_company_func: Callable[[Dict[str, Any]], Optional[int]],
    db_get_company_by_id_func: Callable[[int], Optional[Dict[str, Any]]],
    db_update_company_func: Callable[[int, Dict[str, Any]], bool],
    db_delete_company_func: Callable[[int], bool],
    db_set_default_company_func: Callable[[int], bool],
    load_admin_setting_func: Callable[[str, Any], Any], 
    save_admin_setting_func: Callable[[str, Any], bool], 
    db_add_company_document_func: Callable[[int, str, str, str, bytes], Optional[int]],
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    db_delete_company_document_func: Callable[[int], bool]
):
    st.subheader(get_text_local("admin_tab_company_management_new", "Firmenverwaltung (Mandanten)"))

    if 'editing_company_id' not in st.session_state:
        st.session_state.editing_company_id = None

    active_company_id_str = load_admin_setting_func('active_company_id', None)
    active_company_id = None
    if active_company_id_str is not None:
        try:
            active_company_id = int(active_company_id_str)
        except (ValueError, TypeError):
            st.warning(f"Ungültige active_company_id '{active_company_id_str}' in Admin-Settings.")
    
    active_company_details_display = db_get_company_by_id_func(active_company_id) if active_company_id is not None else None
    
    if active_company_details_display: 
        st.info(f"Aktuell aktive Firma für Angebote: **{active_company_details_display.get('name', 'N/A')}** (ID: {active_company_id})")
    else: 
        st.warning("Es ist keine Firma als 'aktiv' für die Angebotserstellung ausgewählt. Bitte eine Firma als Standard festlegen oder eine anlegen.")
    st.markdown("---")

    form_title = get_text_local("admin_add_new_company_header", "Neue Firma anlegen")
    submit_button_label = get_text_local("admin_add_company_button", "Firma anlegen")
    company_data_for_form = {}
    if st.session_state.editing_company_id:
        company_to_edit = db_get_company_by_id_func(st.session_state.editing_company_id)
        if company_to_edit:
            company_data_for_form = company_to_edit
            form_title = get_text_local("admin_edit_company_header", "Firma bearbeiten:") + f" {company_data_for_form.get('name', '')}"
            submit_button_label = get_text_local("admin_save_company_button", "Änderungen speichern")
        else:
            st.error(f"Firma mit ID {st.session_state.editing_company_id} nicht gefunden. Bearbeitungsmodus zurückgesetzt.")
            st.session_state.editing_company_id = None
            
    expander_title = form_title
    _all_companies_temp_list = db_list_companies_func() 
    expander_expanded_default = (st.session_state.editing_company_id is not None or not _all_companies_temp_list)

    with st.expander(expander_title, expanded=expander_expanded_default):
        form_key_company_ui_crud = f"company_form_ui_crud_{st.session_state.editing_company_id or 'new_company_v16_admin_definitiv'}"
        with st.form(key=form_key_company_ui_crud, clear_on_submit=False): 
            c_name = st.text_input(get_text_local("admin_company_name_label", "Firmenname"), value=company_data_for_form.get("name", ""), key=f"{form_key_company_ui_crud}_name")
            uploaded_logo_file_ui_crud = st.file_uploader(get_text_local("admin_company_logo_upload_label", "Firmenlogo (PNG, JPG, max. 2MB)"), type=["png", "jpg", "jpeg"], key=f"{form_key_company_ui_crud}_logo_upload")
            current_logo_b64_form_crud = company_data_for_form.get("logo_base64")
            if current_logo_b64_form_crud and not uploaded_logo_file_ui_crud and st.session_state.editing_company_id:
                try:
                    st.image(base64.b64decode(current_logo_b64_form_crud), caption=get_text_local("admin_current_logo_caption","Aktuelles Logo"), width=100)
                except Exception:
                    pass 
            
            c_street = st.text_input(get_text_local("admin_company_street_label", "Straße & Nr."), value=company_data_for_form.get("street", ""), key=f"{form_key_company_ui_crud}_street")
            c_zip = st.text_input(get_text_local("admin_company_zip_label", "PLZ"), value=company_data_for_form.get("zip_code", ""), key=f"{form_key_company_ui_crud}_zip")
            c_city = st.text_input(get_text_local("admin_company_city_label", "Ort"), value=company_data_for_form.get("city", ""), key=f"{form_key_company_ui_crud}_city")
            c_phone = st.text_input(get_text_local("admin_company_phone_label", "Telefon"), value=company_data_for_form.get("phone", ""), key=f"{form_key_company_ui_crud}_phone")
            c_email = st.text_input(get_text_local("admin_company_email_label", "E-Mail"), value=company_data_for_form.get("email", ""), key=f"{form_key_company_ui_crud}_email")
            c_web = st.text_input(get_text_local("admin_company_website_label", "Webseite"), value=company_data_for_form.get("website", ""), key=f"{form_key_company_ui_crud}_web")
            c_tax = st.text_input(get_text_local("admin_company_tax_id_label", "Steuernr./USt-ID"), value=company_data_for_form.get("tax_id", ""), key=f"{form_key_company_ui_crud}_tax")
            c_reg = st.text_input(get_text_local("admin_company_commercial_register_label", "Handelsregister"), value=company_data_for_form.get("commercial_register", ""), key=f"{form_key_company_ui_crud}_reg")
            c_bank = st.text_area(get_text_local("admin_company_bank_details_label", "Bankverbindung"), value=company_data_for_form.get("bank_details", ""), height=80, key=f"{form_key_company_ui_crud}_bank")
            c_footer = st.text_area(get_text_local("admin_company_footer_text_label", "PDF Fußzeilentext"), value=company_data_for_form.get("pdf_footer_text", ""), height=80, key=f"{form_key_company_ui_crud}_footer")
            submitted_company_form_btn_crud = st.form_submit_button(submit_button_label)

        if submitted_company_form_btn_crud:
            company_name_stripped_crud = c_name.strip() if isinstance(c_name, str) else ""
            if not company_name_stripped_crud: 
                st.error(get_text_local("admin_company_name_required_error", "Firmenname ist ein Pflichtfeld."))
            else:
                data_for_db_crud = { 
                    "name": company_name_stripped_crud, 
                    "street": c_street.strip() if isinstance(c_street, str) else None, 
                    "zip_code": c_zip.strip() if isinstance(c_zip, str) else None, 
                    "city": c_city.strip() if isinstance(c_city, str) else None, 
                    "phone": c_phone.strip() if isinstance(c_phone, str) else None, 
                    "email": c_email.strip() if isinstance(c_email, str) else None, 
                    "website": c_web.strip() if isinstance(c_web, str) else None, 
                    "tax_id": c_tax.strip() if isinstance(c_tax, str) else None, 
                    "commercial_register": c_reg.strip() if isinstance(c_reg, str) else None, 
                    "bank_details": c_bank.strip() if isinstance(c_bank, str) else None, 
                    "pdf_footer_text": c_footer.strip() if isinstance(c_footer, str) else None 
                }
                if uploaded_logo_file_ui_crud is not None:
                    if uploaded_logo_file_ui_crud.size > 2 * 1024 * 1024: 
                        st.error(get_text_local("admin_error_logo_too_large","Logo-Datei ist zu groß (max. 2MB). Altes Logo wird beibehalten, falls vorhanden."))
                        data_for_db_crud["logo_base64"] = current_logo_b64_form_crud 
                    else:
                        data_for_db_crud["logo_base64"] = base64.b64encode(uploaded_logo_file_ui_crud.getvalue()).decode('utf-8')
                elif st.session_state.editing_company_id: 
                     data_for_db_crud["logo_base64"] = current_logo_b64_form_crud 
                else: 
                     data_for_db_crud["logo_base64"] = None

                if st.session_state.editing_company_id:
                    if db_update_company_func(st.session_state.editing_company_id, data_for_db_crud):
                        st.success(get_text_local("admin_company_updated_success", "Firma erfolgreich aktualisiert."))
                        st.session_state.editing_company_id = None 
                        st.session_state.selected_page_key_sui = "admin" 
                        st.rerun()
                    else:
                        st.error(get_text_local("admin_company_update_error", "Fehler beim Aktualisieren der Firma."))
                else: 
                    new_company_id_crud = db_add_company_func(data_for_db_crud)
                    if new_company_id_crud:
                        st.success(get_text_local("admin_company_added_success_param","Firma '{company_name}' erfolgreich angelegt.").format(company_name=company_name_stripped_crud))
                        if len(db_list_companies_func()) == 1: 
                            if db_set_default_company_func(new_company_id_crud):
                                st.info(get_text_local("admin_info_company_set_default_param","Firma '{company_name}' wurde als Standard und aktive Firma gesetzt.").format(company_name=company_name_stripped_crud))
                            else:
                                st.warning(get_text_local("admin_warning_company_set_default_failed","Konnte Firma nicht automatisch als Standard/Aktiv setzen."))
                        st.session_state.editing_company_id = None 
                        st.session_state.selected_page_key_sui = "admin" 
                        st.rerun()
                    else:
                        st.error(get_text_local("admin_company_add_error", "Fehler beim Anlegen der Firma. Existiert der Name bereits?"))

        if st.session_state.editing_company_id: 
            if st.button(get_text_local("admin_finish_edit_company_button", "Bearbeitung abschließen / Neue Firma anlegen"), key=f"finish_edit_company_btn_ui_crud_{st.session_state.editing_company_id}_v16_admin_definitiv"):
                st.session_state.editing_company_id = None
                st.session_state.selected_page_key_sui = "admin" 
                st.rerun()
            
            current_company_id_for_docs_crud = st.session_state.editing_company_id 
            st.markdown("---")
            st.subheader(get_text_local("admin_company_documents_header", "Dokumente für diese Firma verwalten"))
            
            DOCUMENT_TYPES_AVAILABLE_CRUD = ["AGB", "Datenschutz", "Vollmacht", "SEPA-Mandat", "Freistellungsbescheinigung", "Sonstiges"] 
            
            form_key_doc_upload_crud = f"company_document_upload_form_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv"
            with st.form(key=form_key_doc_upload_crud, clear_on_submit=True):
                st.markdown("**"+get_text_local("admin_upload_new_document_header","Neues Dokument hochladen:")+"**")
                doc_display_name_upload_crud = st.text_input(
                    get_text_local("admin_doc_display_name_label", "Anzeigename des Dokuments (z.B. AGB Stand 01/2024)"), 
                    key=f"doc_disp_name_upload_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv"
                )
                doc_type_upload_crud = st.selectbox(
                    get_text_local("admin_doc_type_label", "Dokumententyp"), 
                    options=DOCUMENT_TYPES_AVAILABLE_CRUD, 
                    key=f"doc_type_upload_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv"
                )
                uploaded_pdf_file_doc_crud = st.file_uploader(
                    get_text_local("admin_doc_pdf_upload_label", "PDF-Dokument auswählen (max. 5MB)"), 
                    type=["pdf"], 
                    key=f"doc_pdf_upload_crud_{current_company_id_for_docs_crud}_v16_admin_definitiv"
                )
                submitted_doc_upload_btn_crud = st.form_submit_button(get_text_local("admin_doc_upload_button", "Dokument hochladen & speichern"))
                
                if submitted_doc_upload_btn_crud:
                    doc_display_name_val_crud = str(doc_display_name_upload_crud).strip() if doc_display_name_upload_crud else ""
                    if not doc_display_name_val_crud:
                        st.error(get_text_local("admin_error_doc_display_name_required","Bitte einen Anzeigenamen für das Dokument eingeben."))
                    elif not uploaded_pdf_file_doc_crud:
                        st.error(get_text_local("admin_error_doc_file_required","Bitte eine PDF-Datei für das Dokument auswählen."))
                    elif uploaded_pdf_file_doc_crud.size > 5 * 1024 * 1024: 
                        st.error(get_text_local("admin_error_doc_file_too_large","Dokument-Datei ist zu groß (max. 5MB)."))
                    else:
                        file_bytes_doc_crud = uploaded_pdf_file_doc_crud.getvalue()
                        original_filename_doc_crud = uploaded_pdf_file_doc_crud.name
                        doc_id_db_crud = db_add_company_document_func(
                            current_company_id_for_docs_crud,
                            doc_display_name_val_crud,
                            doc_type_upload_crud,
                            original_filename_doc_crud,
                            file_bytes_doc_crud
                        )
                        if doc_id_db_crud:
                            st.success(get_text_local("admin_success_doc_uploaded_param","Dokument '{doc_name}' erfolgreich hochgeladen.").format(doc_name=doc_display_name_val_crud))
                            st.session_state.selected_page_key_sui = "admin" 
                            st.rerun() 
                        else:
                            st.error(get_text_local("admin_error_doc_saving_to_db","Fehler beim Speichern des Dokuments in der Datenbank."))

            company_documents_list_crud = db_list_company_documents_func(current_company_id_for_docs_crud, None) 
            if company_documents_list_crud:
                st.markdown("**"+get_text_local("admin_existing_documents_header","Vorhandene Dokumente:")+"**")
                for doc_item_crud in company_documents_list_crud:
                    doc_id_list_crud = doc_item_crud['id']
                    cols_doc_display_crud = st.columns([3, 2, 3, 1])
                    cols_doc_display_crud[0].markdown(f"**{doc_item_crud.get('display_name')}**")
                    cols_doc_display_crud[1].caption(f"Typ: {doc_item_crud.get('document_type')}")
                    cols_doc_display_crud[2].caption(f"Datei: {doc_item_crud.get('file_name')}")
                    
                    delete_doc_btn_key_list_crud = f"delete_company_doc_btn_crud_{doc_id_list_crud}_v16_admin_definitiv"
                    confirm_delete_doc_session_key_crud = f"confirm_delete_company_doc_sess_crud_{doc_id_list_crud}_v16_admin_definitiv"
                    
                    if cols_doc_display_crud[3].button("🗑️", key=delete_doc_btn_key_list_crud, help="Dokument löschen"):
                        if st.session_state.get(confirm_delete_doc_session_key_crud, False): 
                            if db_delete_company_document_func(doc_id_list_crud):
                                st.success(get_text_local("admin_success_doc_deleted_param","Dokument '{doc_name}' gelöscht.").format(doc_name=doc_item_crud.get('display_name')))
                                # if confirm_delete_doc_session_key_crud in st.session_state:
                                #     del st.session_state[confirm_delete_doc_session_key_crud] # Auskommentiert für Robustheit
                                st.session_state.selected_page_key_sui = "admin" 
                                st.rerun()
                            else:
                                st.error(get_text_local("admin_error_deleting_doc_param","Fehler beim Löschen des Dokuments '{doc_name}'.").format(doc_name=doc_item_crud.get('display_name')))
                        else: 
                            st.session_state[confirm_delete_doc_session_key_crud] = True
                            st.warning(get_text_local("admin_warning_confirm_delete_doc_param","Sicher, dass Dokument '{doc_name}' gelöscht werden soll? Erneut 'Löschen' klicken.").format(doc_name=doc_item_crud.get('display_name')))
                            st.session_state.selected_page_key_sui = "admin" 
                            st.rerun() 
                st.markdown("---")
            else:
                st.caption(get_text_local("admin_no_documents_for_company_yet","Noch keine Dokumente für diese Firma hochgeladen."))
    
    st.markdown("---")
    st.subheader(get_text_local("admin_existing_companies_header", "Vorhandene Firmen"))
    
    active_company_id_for_list_display_str_crud = load_admin_setting_func('active_company_id', None)
    active_company_id_for_list_display_crud = None
    if active_company_id_for_list_display_str_crud is not None:
        try:
            active_company_id_for_list_display_crud = int(active_company_id_for_list_display_str_crud)
        except (ValueError, TypeError):
            active_company_id_for_list_display_crud = None
            
    all_companies_list_crud = db_list_companies_func()
    if not all_companies_list_crud:
        st.info(get_text_local("admin_no_companies_info", "Es wurden noch keine Firmen angelegt."))
    else:
        header_cols_crud = st.columns([0.5, 2, 1, 1, 1, 0.5, 0.5, 1.5]) 
        column_headers_crud = ["ID", "Firmenname", "Logo", "Standard", "Aktiv", "📝", "🗑️", "Als Standard/Aktiv"]
        for col_idx_crud, header_title_crud in enumerate(column_headers_crud):
            header_cols_crud[col_idx_crud].markdown(f"**{header_title_crud}**")
        
        for company_list_item_crud in all_companies_list_crud:
            company_id_item_int_crud = company_list_item_crud.get('id')
            row_cols_crud = st.columns([0.5, 2, 1, 1, 1, 0.5, 0.5, 1.5])
            row_cols_crud[0].write(str(company_id_item_int_crud) if company_id_item_int_crud is not None else "FEHLER")
            row_cols_crud[1].write(company_list_item_crud.get('name', 'N/A'))
            company_logo_b64_list_view_crud = company_list_item_crud.get('logo_base64')
            if company_logo_b64_list_view_crud:
                try:
                    row_cols_crud[2].image(base64.b64decode(company_logo_b64_list_view_crud), width=40)
                except Exception:
                    row_cols_crud[2].caption("err")
            else:
                row_cols_crud[2].caption("-")
            is_db_default_list_crud = company_list_item_crud.get('is_default') == 1
            row_cols_crud[3].write("✅" if is_db_default_list_crud else "❌")
            is_currently_active_item_crud = (active_company_id_for_list_display_crud is not None and 
                                         company_id_item_int_crud is not None and 
                                         active_company_id_for_list_display_crud == company_id_item_int_crud)
            row_cols_crud[4].write("✅" if is_currently_active_item_crud else "❌")
            if company_id_item_int_crud is not None:
                if row_cols_crud[5].button("📝", key=f"edit_company_list_btn_crud_{company_id_item_int_crud}_v16_admin_definitiv", help="Bearbeiten"):
                    st.session_state.editing_company_id = company_id_item_int_crud
                    st.session_state.selected_page_key_sui = "admin" 
                    st.rerun()
                confirm_del_key_list_item_crud = f"confirm_delete_company_list_item_crud_{company_id_item_int_crud}_v16_admin_definitiv"
                if row_cols_crud[6].button("🗑️", key=f"delete_company_list_btn_crud_{company_id_item_int_crud}_v16_admin_definitiv", help="Löschen"):
                    if st.session_state.get(confirm_del_key_list_item_crud, False): 
                        if db_delete_company_func(company_id_item_int_crud):
                            st.success(get_text_local("admin_success_company_deleted_param","Firma '{company_name}' gelöscht.").format(company_name=company_list_item_crud.get('name')))
                            # if confirm_del_key_list_item_crud in st.session_state: del st.session_state[confirm_del_key_list_item_crud] # Auskommentiert
                            if st.session_state.editing_company_id == company_id_item_int_crud: 
                                st.session_state.editing_company_id = None
                            st.session_state.selected_page_key_sui = "admin" 
                            st.rerun()
                        else:
                            st.error(get_text_local("admin_error_deleting_company_param","Fehler Löschen Firma '{company_name}'.").format(company_name=company_list_item_crud.get('name')))
                    else: 
                        st.session_state[confirm_del_key_list_item_crud] = True
                        st.warning(get_text_local("admin_warning_confirm_delete_company_param","Sicher Firma '{company_name}' löschen? Erneut klicken.").format(company_name=company_list_item_crud.get('name')))
                        st.session_state.selected_page_key_sui = "admin" 
                        st.rerun()
                if not is_currently_active_item_crud or not is_db_default_list_crud : 
                    if row_cols_crud[7].button(get_text_local("admin_set_company_default_button", "Als Standard/Aktiv"), key=f"set_default_list_btn_crud_{company_id_item_int_crud}_v16_admin_definitiv"):
                        if db_set_default_company_func(company_id_item_int_crud): 
                            st.success(get_text_local("admin_success_company_set_default_param","Firma '{company_name}' als Standard/Aktiv gesetzt.").format(company_name=company_list_item_crud.get('name')))
                            st.session_state.selected_page_key_sui = "admin" 
                            st.rerun()
                        else:
                            st.error(get_text_local("admin_error_setting_default_company","Fehler Setzen Standardfirma."))
                else:
                    row_cols_crud[7].markdown("*(Std/Aktiv)*")
            else: 
                row_cols_crud[5].caption("-"); row_cols_crud[6].caption("-"); row_cols_crud[7].caption("-")
            st.markdown("---")


# Fortsetzung von admin_panel.py
def render_product_management(
    list_products_func: Callable[[Optional[str]], List[Dict[str, Any]]], 
    add_product_func: Callable[[Dict[str, Any]], Optional[int]], 
    update_product_func: Callable[[Union[int, float], Dict[str, Any]], bool], 
    delete_product_func: Callable[[Union[int, float]], bool], 
    get_product_by_id_func: Callable[[Union[int, float]], Optional[Dict[str, Any]]], 
    list_product_categories_func: Callable[[], List[str]], 
    get_product_by_model_name_func: Callable[[str], Optional[Dict[str, Any]]] 
):
    st.subheader(get_text_local("admin_product_management_header", "Produktverwaltung"))
    PRODUCT_DATASHEETS_BASE_DIR_ADMIN = os.path.join(os.getcwd(), "data", "product_datasheets")
    if not os.path.exists(PRODUCT_DATASHEETS_BASE_DIR_ADMIN):
        try:
            os.makedirs(PRODUCT_DATASHEETS_BASE_DIR_ADMIN)
        except OSError as e:
            st.error(f"Fehler Erstellen Verzeichnis '{PRODUCT_DATASHEETS_BASE_DIR_ADMIN}': {e}")

    st.markdown("---")
    st.subheader(get_text_local("admin_product_db_upload_header", "Produktdatenbank hochladen/aktualisieren (Excel/CSV)"))
    st.info(get_text_local("admin_product_db_upload_info_v2",
                           "Laden Sie hier eine Excel (.xlsx) oder CSV (.csv) Datei hoch..."))
    
    uploader_key_bulk_product = f"product_bulk_upload_widget{WIDGET_KEY_SUFFIX}"
    uploaded_product_file_bulk = st.file_uploader(
        get_text_local("admin_upload_product_file_label", "Produkt-Datei auswählen"),
        type=["xlsx", "csv"],
        key=uploader_key_bulk_product 
    )

    if uploaded_product_file_bulk is not None:
        if st.button(get_text_local("admin_process_product_file_button", "Hochgeladene Produkt-Datei verarbeiten"), key=f"process_bulk_product_btn{WIDGET_KEY_SUFFIX}"):
            try:
                df_products_import = None
                if uploaded_product_file_bulk.name.endswith('.xlsx'):
                    df_products_import = pd.read_excel(uploaded_product_file_bulk, engine='openpyxl')
                elif uploaded_product_file_bulk.name.endswith('.csv'): 
                    uploaded_product_file_bulk.seek(0) 
                    csv_bytes_content = uploaded_product_file_bulk.getvalue()
                    detected_encoding = None; encodings_to_try = ['utf-8', 'iso-8859-1', 'latin1', 'cp1252']
                    for enc in encodings_to_try:
                        try:
                            df_temp_auto = pd.read_csv(io.BytesIO(csv_bytes_content), sep=None, decimal='.', encoding=enc, engine='python', thousands=None, comment='#', skipinitialspace=True)
                            if df_temp_auto is not None and not df_temp_auto.empty and len(df_temp_auto.columns) > 1 and all(isinstance(c, str) for c in df_temp_auto.columns):
                                 st.info(f"CSV erfolgreich mit Kodierung '{enc}' und automatischem Trennzeichen gelesen.")
                                 df_products_import = df_temp_auto; detected_encoding = enc; break
                            uploaded_product_file_bulk.seek(0) 
                            df_temp_semicolon = pd.read_csv(io.BytesIO(csv_bytes_content), sep=';', decimal=',', encoding=enc, engine='python', thousands='.', comment='#', skipinitialspace=True)
                            if df_temp_semicolon is not None and not df_temp_semicolon.empty and len(df_temp_semicolon.columns) > 1:
                                 st.info(f"CSV erfolgreich mit Kodierung '{enc}' und Trennzeichen ';' gelesen.")
                                 df_products_import = df_temp_semicolon; detected_encoding = enc; break
                        except Exception: 
                            df_products_import = None 
                            uploaded_product_file_bulk.seek(0) 
                    if not detected_encoding and df_products_import is None: 
                        st.error("Konnte CSV-Datei mit gängigen Kodierungen/Trennzeichen nicht verarbeiten.")
                
                if df_products_import is not None:
                    df_products_import.columns = [str(col).strip().lower().replace(' ', '_') for col in df_products_import.columns]
                    st.write("Vorschau der importierten Daten (erste 5 Zeilen):", df_products_import.head()) 
                    imported_count, updated_count, skipped_count = 0, 0, 0; error_rows = []
                    db_columns_from_product_db = [
                        'id', 'category', 'model_name', 'brand', 'price_euro', 
                        'capacity_w', 'storage_power_kw', 'power_kw', 'max_cycles', 
                        'warranty_years', 'length_m', 'width_m', 'weight_kg', 
                        'efficiency_percent', 'origin_country', 'description', 'pros', 'cons', 
                        'rating', 'image_base64', 'datasheet_link_db_path', 
                        'additional_cost_netto', 'created_at', 'updated_at'
                    ]
                    df_products_import.rename(columns={'last_updated': 'updated_at'}, inplace=True, errors='ignore') 
                    required_cols_import = ['model_name', 'category'] 
                    missing_required = [col for col in required_cols_import if col not in df_products_import.columns]
                    if missing_required: 
                        st.error(f"Fehlende Pflichtspalten in der hochgeladenen Datei: {', '.join(missing_required)}. Import abgebrochen.")
                    else:
                        for index, row in df_products_import.iterrows():
                            product_data_import = {}
                            try:
                                product_data_import = {k: (v if pd.notna(v) else None) for k, v in row.to_dict().items()}
                                product_data_import_filtered = {db_col: product_data_import.get(db_col) for db_col in db_columns_from_product_db if db_col in product_data_import}
                                if not product_data_import_filtered.get('model_name') or not product_data_import_filtered.get('category'):
                                    skipped_count += 1
                                    error_rows.append({'row': index + 2, 'reason': "Modellname oder Kategorie fehlt in Zeile."})
                                    continue
                                for num_col in ['price_euro', 'capacity_w', 'storage_power_kw', 'power_kw', 'warranty_years', 'length_m', 'width_m', 'weight_kg', 'efficiency_percent', 'additional_cost_netto', 'max_cycles', 'rating']:
                                    if num_col in product_data_import_filtered and product_data_import_filtered[num_col] is not None:
                                        try:
                                            val_str = str(product_data_import_filtered[num_col])
                                            if '.' in val_str and ',' in val_str: 
                                                if val_str.rfind('.') < val_str.rfind(','): 
                                                    val_str = val_str.replace('.', '') 
                                            val_str = val_str.replace(',', '.') 
                                            product_data_import_filtered[num_col] = float(val_str)
                                            if num_col in ['warranty_years', 'max_cycles', 'rating'] and product_data_import_filtered[num_col] is not None:
                                                 product_data_import_filtered[num_col] = int(product_data_import_filtered[num_col])
                                        except (ValueError, TypeError): 
                                            error_rows.append({'row': index + 2, 'model': product_data_import_filtered.get('model_name'), 'column': num_col, 'value': product_data_import_filtered[num_col], 'reason': 'Zahlenkonvertierung fehlgeschlagen'})
                                            product_data_import_filtered[num_col] = None 
                                existing_product = get_product_by_model_name_func(str(product_data_import_filtered['model_name']))
                                if existing_product and 'id' in existing_product: 
                                    if update_product_func(existing_product['id'], product_data_import_filtered): 
                                        updated_count += 1
                                    else: 
                                        skipped_count += 1
                                        error_rows.append({'row': index + 2, 'model': product_data_import_filtered.get('model_name'), 'reason': 'Datenbank-Update fehlgeschlagen'})
                                else:
                                    if add_product_func(product_data_import_filtered): 
                                        imported_count += 1
                                    else: 
                                        skipped_count += 1
                                        error_rows.append({'row': index + 2, 'model': product_data_import_filtered.get('model_name'), 'reason': 'Datenbank-Hinzufügen fehlgeschlagen (evtl. Duplikat oder anderer Fehler)'})
                            except Exception as e_row: 
                                skipped_count += 1
                                current_model_name_for_error = product_data_import.get('model_name', f"Zeile {index+2}")
                                error_rows.append({'row': index + 2, 'model': current_model_name_for_error, 'reason': f"Allgemeiner Fehler: {str(e_row)}"})
                        st.success(f"Produktimport abgeschlossen: {imported_count} Produkte neu hinzugefügt, {updated_count} Produkte aktualisiert, {skipped_count} Produkte übersprungen/fehlerhaft.")
                        if error_rows: 
                            st.warning("Details zu fehlerhaften/übersprungenen Zeilen (max. erste 10 Fehler):")
                            st.json(error_rows[:10]) 
                        st.session_state.selected_page_key_sui = "admin" 
                        st.rerun() 
            except Exception as e_bulk_import:
                st.error(f"Fehler beim Verarbeiten der Produkt-Datei: {e_bulk_import}")
                traceback.print_exc() 
    st.markdown("---")

    if 'product_to_edit_id_manual' not in st.session_state: 
        st.session_state.product_to_edit_id_manual = None
    
    product_categories_manual_list = list_product_categories_func()
    
    if not product_categories_manual_list: # KORRIGIERTE Zeile 679
        product_categories_manual_list = ["Modul", "Wechselrichter", "Batteriespeicher", "Wallbox", "Zubehör", "Sonstiges"]
    
    product_data_for_manual_form = {}
    form_manual_title = get_text_local("admin_add_new_product_header_manual", "Neues Produkt manuell anlegen / Bearbeiten")
    
    if st.session_state.product_to_edit_id_manual:
        product_to_edit_manual_data = get_product_by_id_func(st.session_state.product_to_edit_id_manual)
        if product_to_edit_manual_data:
            product_data_for_manual_form = product_to_edit_manual_data
            form_manual_title = f"Produkt bearbeiten: {product_data_for_manual_form.get('model_name', '')} (ID: {st.session_state.product_to_edit_id_manual})"
        else:
            st.error(f"Produkt mit ID {st.session_state.product_to_edit_id_manual} nicht gefunden.")
            st.session_state.product_to_edit_id_manual = None 
            
    with st.expander(form_manual_title, expanded=(st.session_state.product_to_edit_id_manual is not None or not list_products_func(None))):
        form_key_manual_prod_ui = f"product_form_manual_ui_man_{st.session_state.product_to_edit_id_manual or 'new_prod_man'}{WIDGET_KEY_SUFFIX}" 
        with st.form(key=form_key_manual_prod_ui, clear_on_submit=False): 
            st.text_input("Produkt ID", value=str(st.session_state.product_to_edit_id_manual) if st.session_state.product_to_edit_id_manual else "Automatisch", disabled=True, key=f"{form_key_manual_prod_ui}_id_man")
            p_model_name_form = st.text_input(label=get_text_local("product_model_name_label","Modellname*"), value=product_data_for_manual_form.get('model_name', ''), key=f"{form_key_manual_prod_ui}_model_name_man")
            available_cats_form = [cat for cat in product_categories_manual_list if cat and str(cat).lower() != "ohne speicher"]
            default_cat_idx = 0
            current_cat_val = product_data_for_manual_form.get('category')
            if current_cat_val and current_cat_val in available_cats_form:
                default_cat_idx = available_cats_form.index(current_cat_val)
            p_category_form = st.selectbox(label=get_text_local("product_category_label","Kategorie*"), options=available_cats_form, index=default_cat_idx, key=f"{form_key_manual_prod_ui}_category_man", disabled=not available_cats_form)
            p_brand_form = st.text_input(label=get_text_local("product_brand_label","Hersteller"), value=product_data_for_manual_form.get('brand', ''), key=f"{form_key_manual_prod_ui}_brand_man")
            p_price_form = st.number_input(label=get_text_local("product_price_euro_label","Preis (€)"), min_value=0.0, value=float(product_data_for_manual_form.get('price_euro', 0.0)), step=0.01, format="%.2f", key=f"{form_key_manual_prod_ui}_price_man")
            p_add_cost_form = st.number_input(label=get_text_local("product_additional_cost_netto_label","Zusatzkosten Netto (€)"), min_value=0.0, value=float(product_data_for_manual_form.get('additional_cost_netto', 0.0)),step=0.01,format="%.2f", key=f"{form_key_manual_prod_ui}_add_cost_man")
            p_warranty_form = st.number_input(label=get_text_local("product_warranty_years_label","Garantie (Jahre)"), min_value=0, value=int(product_data_for_manual_form.get('warranty_years', 0)), step=1, key=f"{form_key_manual_prod_ui}_warranty_man")
            
            st.markdown("**"+get_text_local("product_image_header","Produktbild")+"**")
            uploaded_product_image_manual_file_form = st.file_uploader(get_text_local("product_image_upload_label","Produktbild (PNG, JPG, max. 2MB)"), type=["png", "jpg", "jpeg"], key=f"{form_key_manual_prod_ui}_image_upload_man")
            current_product_image_b64_form = product_data_for_manual_form.get("image_base64")
            if current_product_image_b64_form and not uploaded_product_image_manual_file_form and st.session_state.product_to_edit_id_manual:
                try:
                    st.image(base64.b64decode(current_product_image_b64_form), caption=get_text_local("product_current_image_caption","Aktuelles Produktbild"), width=100)
                except Exception:
                    pass 
            
            st.markdown("**"+get_text_local("product_datasheet_header","Produktdatenblatt (PDF)")+"**")
            uploaded_datasheet_pdf_file_form = st.file_uploader(get_text_local("product_datasheet_upload_label","Datenblatt-PDF hochladen (max. 5MB)"), type="pdf", key=f"{form_key_manual_prod_ui}_datasheet_upload_man")
            current_datasheet_link = product_data_for_manual_form.get("datasheet_link_db_path")
            if current_datasheet_link:
                st.caption(f"{get_text_local('product_current_datasheet_caption','Aktuelles Datenblatt')}: `{current_datasheet_link}`")
            
            st.markdown(f"**{get_text_local('product_category_specific_fields_header','Spezifische Felder für Kategorie')}: {p_category_form or get_text_local('product_no_category_selected','Keine Kategorie gewählt')}**")
            p_capacity_w_val, p_power_kw_val, p_storage_power_kw_val, p_efficiency_percent_val, p_length_m_val, p_width_m_val, p_weight_kg_val, p_max_cycles_val = None,None,None,None,None,None,None,None
            if p_category_form == 'Modul':
                p_capacity_w_val = st.number_input(label=get_text_local("module_capacity_w_label","Leistung (Wp)"), min_value=0.0, value=float(product_data_for_manual_form.get('capacity_w', 0.0)), step=1.0, key=f"{form_key_manual_prod_ui}_cap_w_man")
                p_efficiency_percent_val = st.number_input(label=get_text_local("module_efficiency_percent_label","Wirkungsgrad (%)"), min_value=0.0,max_value=100.0, value=float(product_data_for_manual_form.get('efficiency_percent', 0.0)),step=0.01,format="%.2f", key=f"{form_key_manual_prod_ui}_eff_mod_man")
                m_c1, m_c2 = st.columns(2)
                p_length_m_val = m_c1.number_input(label=get_text_local("module_length_m_label","Länge (m)"), min_value=0.0,value=float(product_data_for_manual_form.get('length_m',0.0)),step=0.001,format="%.3f", key=f"{form_key_manual_prod_ui}_len_man")
                p_width_m_val = m_c2.number_input(label=get_text_local("module_width_m_label","Breite (m)"),min_value=0.0,value=float(product_data_for_manual_form.get('width_m',0.0)),step=0.001,format="%.3f", key=f"{form_key_manual_prod_ui}_width_man")
                p_weight_kg_val = st.number_input(label=get_text_local("module_weight_kg_label","Gewicht (kg)"), min_value=0.0, value=float(product_data_for_manual_form.get('weight_kg', 0.0)), step=0.1, key=f"{form_key_manual_prod_ui}_weight_man")
            elif p_category_form == 'Wechselrichter':
                p_power_kw_val = st.number_input(label=get_text_local("inverter_power_kw_label","Nennleistung AC (kW)"), min_value=0.0, value=float(product_data_for_manual_form.get('power_kw', 0.0)), step=0.1, key=f"{form_key_manual_prod_ui}_power_kw_inv_man")
                p_efficiency_percent_val = st.number_input(label=get_text_local("inverter_max_efficiency_percent_label","Max. Wirkungsgrad (%)"), min_value=0.0,max_value=100.0, value=float(product_data_for_manual_form.get('efficiency_percent', 0.0)),step=0.01,format="%.2f", key=f"{form_key_manual_prod_ui}_eff_inv_man")
            elif p_category_form == 'Batteriespeicher':
                p_storage_power_kw_val = st.number_input(label=get_text_local("storage_usable_storage_power_kw_label","Nutzbare Kapazität (kWh)"),min_value=0.0,value=float(product_data_for_manual_form.get('storage_power_kw', 0.0)),step=0.1, key=f"{form_key_manual_prod_ui}_storage_cap_man")
                p_power_kw_val = st.number_input(label=get_text_local("storage_max_charge_discharge_storage_power_kw_label","Max. Lade-/Entladeleistung (kW)"),min_value=0.0,value=float(product_data_for_manual_form.get('power_kw', 0.0)),step=0.1, key=f"{form_key_manual_prod_ui}_storage_power_man")
                p_max_cycles_val = st.number_input(label=get_text_local("storage_max_cycles_manufacturer_label","Zyklen (Herstellerangabe)"),min_value=0,value=int(product_data_for_manual_form.get('max_cycles',0)),step=100, key=f"{form_key_manual_prod_ui}_max_cycles_man")
            
            p_description_form_val = st.text_area(get_text_local("product_description_label","Beschreibung"), value=product_data_for_manual_form.get('description', ''), height=100, key=f"{form_key_manual_prod_ui}_desc_man")
            form_manual_submit_label_dyn = get_text_local("admin_save_product_button_manual", "Änderungen speichern") if st.session_state.product_to_edit_id_manual else get_text_local("admin_add_product_button_manual", "Produkt anlegen")
            submitted_manual_product_form_btn = st.form_submit_button(form_manual_submit_label_dyn)

        if submitted_manual_product_form_btn:
            if not p_model_name_form.strip() or not p_category_form:
                st.error(get_text_local("product_error_model_category_required","Modellname und Kategorie sind Pflichtfelder."))
            else:
                product_data_to_save_db = {
                    "model_name": p_model_name_form.strip(), "category": p_category_form, 
                    "brand": p_brand_form.strip(), "price_euro": p_price_form, 
                    "additional_cost_netto": p_add_cost_form, "warranty_years": p_warranty_form, 
                    "description": p_description_form_val.strip(), 
                    "image_base64": current_product_image_b64_form, # Start with current, update if new one uploaded
                    "datasheet_link_db_path": current_datasheet_link # Start with current
                }
                if p_category_form == 'Modul': 
                    product_data_to_save_db.update({"capacity_w": p_capacity_w_val, "efficiency_percent": p_efficiency_percent_val, "length_m": p_length_m_val, "width_m": p_width_m_val, "weight_kg": p_weight_kg_val})
                elif p_category_form == 'Wechselrichter': 
                    product_data_to_save_db.update({"power_kw": p_power_kw_val, "efficiency_percent": p_efficiency_percent_val})
                elif p_category_form == 'Batteriespeicher': 
                    product_data_to_save_db.update({"storage_power_kw": p_storage_power_kw_val, "power_kw": p_power_kw_val, "max_cycles": p_max_cycles_val})
                
                if uploaded_product_image_manual_file_form:
                    if uploaded_product_image_manual_file_form.size <= 2*1024*1024: 
                        product_data_to_save_db["image_base64"] = base64.b64encode(uploaded_product_image_manual_file_form.getvalue()).decode('utf-8')
                    else: 
                        st.error(get_text_local("product_error_image_too_large","Produktbild zu groß (max. 2MB). Nicht gespeichert."))
                
                datasheet_content_bytes_to_write, original_datasheet_filename_to_write = None, None
                if uploaded_datasheet_pdf_file_form:
                    if uploaded_datasheet_pdf_file_form.size <= 5*1024*1024: 
                        datasheet_content_bytes_to_write = uploaded_datasheet_pdf_file_form.getvalue()
                        original_datasheet_filename_to_write = uploaded_datasheet_pdf_file_form.name
                    else: 
                        st.error(get_text_local("product_error_datasheet_too_large","Datenblatt-PDF zu groß (max. 5MB). Nicht hochgeladen."))

                if st.session_state.product_to_edit_id_manual: 
                    product_id_for_files = st.session_state.product_to_edit_id_manual
                    if datasheet_content_bytes_to_write and original_datasheet_filename_to_write:
                        old_ds_path = product_data_for_manual_form.get("datasheet_link_db_path")
                        if old_ds_path: 
                            full_old_ds_path = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_ADMIN, old_ds_path)
                            if os.path.exists(full_old_ds_path):
                                try: 
                                    os.remove(full_old_ds_path)
                                    parent_dir_old_ds = os.path.dirname(full_old_ds_path)
                                    if os.path.exists(parent_dir_old_ds) and not os.listdir(parent_dir_old_ds):
                                        os.rmdir(parent_dir_old_ds)
                                except OSError as e_del_old: 
                                    st.warning(f"Altes Datenblatt konnte nicht gelöscht werden: {e_del_old}")
                        prod_specific_dir = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_ADMIN, str(product_id_for_files))
                        os.makedirs(prod_specific_dir, exist_ok=True)
                        safe_filename = "".join(c if c.isalnum() or c in ('.', '-', '_') else '_' for c in original_datasheet_filename_to_write)
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        final_safe_filename_ds = f"{os.path.splitext(safe_filename)[0]}_{timestamp}{os.path.splitext(safe_filename)[1]}"
                        disk_path = os.path.join(prod_specific_dir, final_safe_filename_ds)
                        with open(disk_path, "wb") as f: 
                            f.write(datasheet_content_bytes_to_write)
                        product_data_to_save_db["datasheet_link_db_path"] = os.path.join(str(product_id_for_files), final_safe_filename_ds)
                    
                    if update_product_func(product_id_for_files, product_data_to_save_db): 
                        st.success(get_text_local("product_success_updated","Produkt erfolgreich aktualisiert."))
                        st.session_state.selected_page_key_sui = "admin"
                        st.rerun() 
                    else: 
                        st.error(get_text_local("product_error_updating","Fehler beim Aktualisieren des Produkts."))
                else: 
                    product_data_for_add = product_data_to_save_db.copy()
                    if "datasheet_link_db_path" in product_data_for_add:
                         del product_data_for_add["datasheet_link_db_path"] 
                    
                    new_product_id = add_product_func(product_data_for_add)
                    if new_product_id:
                        st.success(get_text_local("product_success_added_param","Produkt '{model_name}' mit ID {id} angelegt.").format(model_name=p_model_name_form.strip(), id=new_product_id))
                        if datasheet_content_bytes_to_write and original_datasheet_filename_to_write:
                            prod_specific_dir = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_ADMIN, str(new_product_id))
                            os.makedirs(prod_specific_dir, exist_ok=True)
                            safe_filename = "".join(c if c.isalnum() or c in ('.', '-', '_') else '_' for c in original_datasheet_filename_to_write)
                            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                            final_safe_filename_ds = f"{os.path.splitext(safe_filename)[0]}_{timestamp}{os.path.splitext(safe_filename)[1]}"
                            disk_path = os.path.join(prod_specific_dir, final_safe_filename_ds)
                            with open(disk_path, "wb") as f: 
                                f.write(datasheet_content_bytes_to_write)
                            relative_ds_path = os.path.join(str(new_product_id), final_safe_filename_ds)
                            if update_product_func(new_product_id, {"datasheet_link_db_path": relative_ds_path}): 
                                st.info(get_text_local("product_info_datasheet_saved","Produktdatenblatt gespeichert..."))
                            else: 
                                st.error(get_text_local("product_error_datasheet_path","Produkt angelegt, aber Fehler beim Speichern des Datenblatt-Pfads."))
                        st.session_state.product_to_edit_id_manual = new_product_id 
                        st.session_state.selected_page_key_sui = "admin"
                        st.rerun()
                    else: 
                        st.error(get_text_local("product_error_adding","Fehler beim Anlegen des Produkts. Modellname bereits vorhanden?"))
        
        if st.session_state.product_to_edit_id_manual and product_data_for_manual_form.get("datasheet_link_db_path"):
            st.markdown("**"+get_text_local("product_existing_datasheet_actions_header","Vorhandenes Datenblatt Aktionen:")+"**")
            if st.button(get_text_local("product_button_delete_current_datasheet","Aktuelles Datenblatt löschen"), key=f"delete_datasheet_prod_btn_man_{st.session_state.product_to_edit_id_manual}{WIDGET_KEY_SUFFIX}_key"): 
                datasheet_to_delete_path_val = product_data_for_manual_form.get("datasheet_link_db_path")
                full_path_to_delete_val = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_ADMIN, datasheet_to_delete_path_val)
                file_deleted_fs_val = False
                if os.path.exists(full_path_to_delete_val):
                    try:
                        os.remove(full_path_to_delete_val)
                        parent_dir_ds_val = os.path.dirname(full_path_to_delete_val)
                        if os.path.exists(parent_dir_ds_val) and not os.listdir(parent_dir_ds_val):
                            os.rmdir(parent_dir_ds_val)
                        file_deleted_fs_val = True
                    except OSError as e_del_ds_f:
                        st.error(f"Fehler beim Löschen der Datenblatt-Datei: {e_del_ds_f}")
                else:
                    st.warning(get_text_local("product_warning_datasheet_not_found","Datenblatt-Datei nicht auf dem Server gefunden..."))
                    file_deleted_fs_val = True 
                
                if file_deleted_fs_val:
                    if update_product_func(st.session_state.product_to_edit_id_manual, {"datasheet_link_db_path": None}): 
                        st.success(get_text_local("product_success_datasheet_link_removed","Datenblatt-Verknüpfung entfernt."))
                        st.session_state.selected_page_key_sui = "admin"
                        st.rerun()
                    else: 
                        st.error(get_text_local("product_error_removing_datasheet_path","Fehler beim Entfernen des Datenblatt-Pfads aus der DB."))
        
        if st.session_state.product_to_edit_id_manual:
            if st.button(get_text_local("admin_finish_edit_product_button", "Produktbearbeitung abschließen/Neues Produkt"), key=f"finish_edit_prod_btn_manual_man{WIDGET_KEY_SUFFIX}_key_end"): 
                st.session_state.product_to_edit_id_manual = None
                st.session_state.selected_page_key_sui = "admin"
                st.rerun()

    st.markdown("---")
    st.subheader(get_text_local("admin_current_products_header_display", "Produkte in Datenbank (gefiltert)"))
    selected_category_filter_disp_list = st.selectbox(
        get_text_local("admin_select_category_label_display", "Angezeigte Produktkategorie"), 
        options=[get_text_local("all_categories", "Alle")] + product_categories_manual_list, 
        key=f"product_cat_select_display_list_man{WIDGET_KEY_SUFFIX}_key_filter"
    ) 
    filter_cat_disp_list_val = None if selected_category_filter_disp_list == get_text_local("all_categories", "Alle") else selected_category_filter_disp_list
    all_products_list_display_val = list_products_func(category=filter_cat_disp_list_val)

    if not all_products_list_display_val:
        st.info(get_text_local("product_info_no_products_for_filter","Keine Produkte zum Anzeigen gefunden für die aktuelle Filterauswahl."))
    else:
        list_cols_h = st.columns([0.4, 2, 0.8, 0.8, 1, 0.8, 0.4, 0.4])
        list_headers = ["ID", "Modell", "Bild", "Datenblatt?", "Kategorie", "Preis (€)", "📝", "🗑️"]
        for c, h in zip(list_cols_h, list_headers):
            c.markdown(f"**{h}**")
        
        for i_list, prod_item_in_list in enumerate(all_products_list_display_val):
            prod_id_in_list = prod_item_in_list.get('id')
            key_suffix_in_list = prod_id_in_list if prod_id_in_list is not None else f"idx_prod_list_man_final_key_admin_item_{i_list}{WIDGET_KEY_SUFFIX}" 
            list_cols_r = st.columns([0.4, 2, 0.8, 0.8, 1, 0.8, 0.4, 0.4])
            list_cols_r[0].text(str(prod_id_in_list) if prod_id_in_list is not None else "N/A")
            list_cols_r[1].text(f"{prod_item_in_list.get('brand','') or ''} {prod_item_in_list.get('model_name','') or ''}".strip())
            prod_img_b64_list_view = prod_item_in_list.get('image_base64')
            if prod_img_b64_list_view:
                try:
                    list_cols_r[2].image(base64.b64decode(prod_img_b64_list_view), width=40)
                except Exception:
                    list_cols_r[2].caption("err")
            else:
                list_cols_r[2].caption("-")
            list_cols_r[3].caption("Ja" if prod_item_in_list.get("datasheet_link_db_path") else "Nein")
            list_cols_r[4].caption(prod_item_in_list.get('category',''))
            price_euro_val = prod_item_in_list.get('price_euro')
            price_display_val = 0.0
            try:
                price_display_val = float(price_euro_val if price_euro_val is not None else 0.0)
            except (ValueError, TypeError):
                pass
            list_cols_r[5].caption(f"{price_display_val:.2f}")
            
            if list_cols_r[6].button("📝", key=f"edit_prod_list_btn_man_final_key_admin_item_{key_suffix_in_list}", help="Produkt bearbeiten"): 
                if prod_id_in_list is not None:
                    st.session_state.product_to_edit_id_manual = prod_id_in_list
                    st.session_state.selected_page_key_sui = "admin"
                    st.rerun()
            
            confirm_del_key_prod_item_list_final = f"confirm_del_prod_item_list_man_final_key_admin_item_{key_suffix_in_list}"
            if list_cols_r[7].button("🗑️", key=f"delete_prod_list_btn_man_final_key_admin_item_{key_suffix_in_list}", help="Produkt löschen"):
                if prod_id_in_list is not None:
                    if st.session_state.get(confirm_del_key_prod_item_list_final, False):
                        if delete_product_func(prod_id_in_list):
                            st.success(get_text_local("product_success_deleted_param","Produkt '{model_name}' gelöscht.").format(model_name=prod_item_in_list.get('model_name')))
                            # KORREKTUR: Explizites Löschen des Session State Keys nach st.rerun() ist oft nicht nötig
                            # if confirm_del_key_prod_item_list_final in st.session_state: 
                            #     del st.session_state[confirm_del_key_prod_item_list_final]
                            if st.session_state.product_to_edit_id_manual == prod_id_in_list:
                                st.session_state.product_to_edit_id_manual = None
                            st.session_state.selected_page_key_sui = "admin"
                            st.rerun() 
                        else:
                            st.error(get_text_local("product_error_deleting_param","Fehler Löschen Produkt '{model_name}'.").format(model_name=prod_item_in_list.get('model_name')))
                    else:
                        st.session_state[confirm_del_key_prod_item_list_final] = True
                        st.warning(get_text_local("product_confirm_delete_param","Sicher Produkt '{model_name}' löschen? Erneut klicken.").format(model_name=prod_item_in_list.get('model_name')))
                        st.session_state.selected_page_key_sui = "admin"
                        st.rerun()
            st.divider()

# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-04, Gemini Ultra (Korrektur SyntaxError): Die einzeilige if-Anweisung in `render_product_management` für `product_categories_manual_list` wurde 
#                                                    in einen Standard-Block mit Doppelpunkt und Einrückung umgewandelt, um den `SyntaxError: expected ':'` zu beheben.
#                                                    Die Logik zum Löschen von Session-State-Keys für Bestätigungsdialoge (z.B. `confirm_del_key_prod_item_list_final`) 
#                                                    wurde beibehalten, aber das explizite `del st.session_state[...]` nach einem `st.rerun()` wurde entfernt,
#                                                    da `st.rerun()` den Zustand oft ausreichend zurücksetzt und ein verbleibender Key im session_state meist unkritisch ist.

# Fortsetzung von admin_panel.py
def render_general_settings_extended(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    st.subheader(get_text_local("admin_general_calc_params_basic", "Allgemeine Berechnungsparameter"))
    current_global_constants = load_admin_setting_func('global_constants', {})
    temp_merged_constants = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.copy()
    if isinstance(current_global_constants, dict): temp_merged_constants.update(current_global_constants) 
    current_global_constants = temp_merged_constants
    with st.form(f"global_constants_form{WIDGET_KEY_SUFFIX}"): 
        col_gc1, col_gc2 = st.columns(2)
        with col_gc1: 
            new_vat_rate = st.number_input(label=get_text_local("vat_rate_percent", "Standard MwSt. (%)"), value=float(current_global_constants.get('vat_rate_percent', 0.0)), key=f"gc_vat{WIDGET_KEY_SUFFIX}")
            new_degradation = st.number_input(label=get_text_local("annual_module_degradation_percent", "Leistungsdegradation... (% pro Jahr)"), value=float(current_global_constants.get('annual_module_degradation_percent', 0.5)), key=f"gc_degradation{WIDGET_KEY_SUFFIX}", format="%.2f")
            new_maintenance_fixed = st.number_input(label=get_text_local("maintenance_fixed_eur_pa", "Jährliche Wartungspauschale (€, netto)"), value=float(current_global_constants.get('maintenance_fixed_eur_pa', 50.0)), key=f"gc_maint_fixed{WIDGET_KEY_SUFFIX}", format="%.2f")
        with col_gc2:
            new_inflation = st.number_input(label=get_text_local("inflation_rate_percent", "Inflationsrate... (% p.a.)"), value=float(current_global_constants.get('inflation_rate_percent', 2.0)), key=f"gc_inflation{WIDGET_KEY_SUFFIX}", format="%.2f")
            new_maintenance_increase = st.number_input(label=get_text_local("maintenance_increase_percent_pa", "Jährliche Steigerung Wartungskosten (% p.a.)"), value=float(current_global_constants.get('maintenance_increase_percent_pa', 2.0)), key=f"gc_maint_increase{WIDGET_KEY_SUFFIX}", format="%.2f")
            new_maint_var = st.number_input(label=get_text_local("maintenance_variable_eur_per_kwp_pa", "Variable Wartungskosten (€ pro kWp p.a., netto)"), value=float(current_global_constants.get('maintenance_variable_eur_per_kwp_pa', 5.0)), key=f"gc_maint_var{WIDGET_KEY_SUFFIX}", format="%.2f")
            new_alt_invest_interest = st.number_input(label=get_text_local("alternative_investment_interest_rate_percent", "Vergleichszinssatz Alternativanlage (% p.a.)"), value=float(current_global_constants.get('alternative_investment_interest_rate_percent', 3.0)), key=f"gc_alt_invest{WIDGET_KEY_SUFFIX}", format="%.2f")
        st.markdown("---"); st.subheader(get_text_local("admin_yield_settings_header", "Ertragseinstellungen für PV-Anlage"))
        col_yield1, col_yield2 = st.columns(2)
        with col_yield1: new_global_yield_adj = st.number_input(label=get_text_local("global_yield_adjustment_percent", "Globale Ertragsanpassung (%)"), value=float(current_global_constants.get('global_yield_adjustment_percent', 0.0)), key=f"gc_yield_adj{WIDGET_KEY_SUFFIX}", format="%.1f", help="Ein positiver Wert erhöht...")
        with col_yield2: new_ref_yield_pr = st.number_input(label=get_text_local("reference_specific_yield_pr", "Referenz-Spezialertrag für PR (kWh/kWp/a)"), value=float(current_global_constants.get('reference_specific_yield_pr', 1100.0)), key=f"gc_ref_yield_pr{WIDGET_KEY_SUFFIX}", format="%.0f", help="Wird für die Performance Ratio Berechnung verwendet.")
        st.markdown("---"); st.subheader(get_text_local("admin_orientation_yields_subheader_v2", "Spezifische Jahreserträge (kWh/kWp/a)...")); st.caption(get_text_local("admin_orientation_yields_info_v2", "Basis-Ertragswerte..."))
        current_specific_yields_map = current_global_constants.get('specific_yields_by_orientation_tilt', {}); default_yield_map_template = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK['specific_yields_by_orientation_tilt']; updated_specific_yields_map = {} 
        orientations_ordered = ["Süd", "Südost", "Südwest", "Ost", "West", "Nordost", "Nordwest", "Nord", "Flachdach", "Sonstige"]; tilts_ordered = ["0", "15", "30", "45", "60"] 
        header_cols = st.columns([2] + [1] * len(tilts_ordered)); header_cols[0].markdown("**Ausrichtung**")
        for i, tilt_val_str in enumerate(tilts_ordered): header_cols[i+1].markdown(f"**{tilt_val_str}°**")
        for ori in orientations_ordered:
            row_cols = st.columns([2] + [1] * len(tilts_ordered)); row_cols[0].markdown(f"*{ori}*"); updated_specific_yields_map[ori] = {}
            for i_tilt, tilt_val_str_loop in enumerate(tilts_ordered):
                current_val_for_field = 900.0 
                if isinstance(current_specific_yields_map.get(ori), dict) and tilt_val_str_loop in current_specific_yields_map[ori]: current_val_for_field = float(current_specific_yields_map[ori][tilt_val_str_loop])
                elif isinstance(default_yield_map_template.get(ori), dict) and tilt_val_str_loop in default_yield_map_template[ori]: current_val_for_field = float(default_yield_map_template[ori][tilt_val_str_loop])
                updated_specific_yields_map[ori][tilt_val_str_loop] = row_cols[i_tilt+1].number_input(label=f"{ori}-{tilt_val_str_loop}", value=current_val_for_field, min_value=0.0, max_value=2000.0, step=10.0, format="%.0f", key=f"gc_yield_{ori}_{tilt_val_str_loop}{WIDGET_KEY_SUFFIX}", label_visibility="collapsed")
        current_global_constants['specific_yields_by_orientation_tilt'] = updated_specific_yields_map
        st.markdown("---"); st.subheader(get_text_local("admin_multiyear_settings_header", "Parameter für Mehrjahressimulation"))
        col_my1, col_my2 = st.columns(2)
        with col_my1: new_sim_period = col_my1.number_input(label=get_text_local("simulation_period_years", "Simulationsdauer (Jahre)"), value=int(current_global_constants.get('simulation_period_years', 20)), min_value=1, max_value=50, step=1, key=f"gc_sim_period{WIDGET_KEY_SUFFIX}")
        with col_my2: new_elec_price_increase = col_my2.number_input(label=get_text_local("electricity_price_increase_annual_percent", "Strompreissteigerung (% p.a.)"), value=float(current_global_constants.get('electricity_price_increase_annual_percent', 3.0)), min_value=0.0, max_value=20.0, step=0.1, format="%.2f", key=f"gc_elec_increase{WIDGET_KEY_SUFFIX}")
        if st.form_submit_button(get_text_local("admin_save_economic_yield_settings_button", "Alle Wirtschafts- und Ertragsparameter speichern")):
            current_global_constants['vat_rate_percent'] = new_vat_rate; current_global_constants['annual_module_degradation_percent'] = new_degradation; current_global_constants['maintenance_fixed_eur_pa'] = new_maintenance_fixed; current_global_constants['inflation_rate_percent'] = new_inflation; current_global_constants['maintenance_increase_percent_pa'] = new_maintenance_increase; current_global_constants['maintenance_variable_eur_per_kwp_pa'] = new_maint_var; current_global_constants['alternative_investment_interest_rate_percent'] = new_alt_invest_interest; current_global_constants['global_yield_adjustment_percent'] = new_global_yield_adj; current_global_constants['reference_specific_yield_pr'] = new_ref_yield_pr; current_global_constants['simulation_period_years'] = new_sim_period; current_global_constants['electricity_price_increase_annual_percent'] = new_elec_price_increase
            for key_gc, default_val_gc in _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.items():
                if key_gc not in current_global_constants: current_global_constants[key_gc] = default_val_gc
                elif isinstance(default_val_gc, dict) and isinstance(current_global_constants.get(key_gc), dict):
                    for sub_key_gc, sub_default_val_gc in default_val_gc.items():
                        if sub_key_gc not in current_global_constants[key_gc]: current_global_constants[key_gc][sub_key_gc] = sub_default_val_gc
            if save_admin_setting_func('global_constants', current_global_constants):
                st.success(get_text_local("admin_economic_yield_settings_save_success", "Einstellungen erfolgreich gespeichert."))
                st.session_state.selected_page_key_sui = "admin"; st.rerun()
            else: st.error(get_text_local("admin_economic_yield_settings_save_error", "Fehler beim Speichern der Einstellungen."))

def render_price_matrix(load_admin_setting_func: Callable, save_admin_setting_func: Callable, parse_csv_func_from_calculations: Callable, parse_excel_func_local_admin: Callable):
    if 'uploaded_excel_bytes_for_save_admin' not in st.session_state: st.session_state.uploaded_excel_bytes_for_save_admin = None
    if 'parsed_excel_df_for_preview_admin' not in st.session_state: st.session_state.parsed_excel_df_for_preview_admin = None
    if 'uploaded_csv_content_for_save_admin' not in st.session_state: st.session_state.uploaded_csv_content_for_save_admin = None
    if 'parsed_csv_df_for_preview_admin' not in st.session_state: st.session_state.parsed_csv_df_for_preview_admin = None
    st.subheader(get_text_local("admin_price_matrix_header", "Preis-Matrix Verwaltung"))
    st.info(get_text_local("admin_price_matrix_info_detailed_xlsx", "Laden Sie hier die Grundpreis-Matrix als Excel-Datei (.xlsx) hoch..."))
    uploader_key_excel = f"price_matrix_upload_widget_xlsx{WIDGET_KEY_SUFFIX}"
    uploaded_file_excel = st.file_uploader(get_text_local("admin_upload_xlsx_label", "Excel-Datei (.xlsx) hochladen"), type=["xlsx"], key=uploader_key_excel)
    if uploaded_file_excel is not None:
        try:
            excel_bytes_content = uploaded_file_excel.getvalue(); parser_errors_matrix_upload_excel: List[str] = []
            parsed_df_temp_excel = parse_excel_func_local_admin(excel_bytes_content, parser_errors_matrix_upload_excel)
            if parser_errors_matrix_upload_excel:
                for err_matrix in parser_errors_matrix_upload_excel: st.warning(f"Parser-Warnung (Excel): {err_matrix}")
            if parsed_df_temp_excel is not None and not parsed_df_temp_excel.empty:
                st.session_state.uploaded_excel_bytes_for_save_admin = excel_bytes_content; st.session_state.parsed_excel_df_for_preview_admin = parsed_df_temp_excel
                st.success(get_text_local("admin_xlsx_parse_success", "Excel geparst."))
            else:
                st.error(get_text_local("admin_xlsx_parse_error_empty", "Excel geparst, aber leer.")); st.session_state.uploaded_excel_bytes_for_save_admin = None; st.session_state.parsed_excel_df_for_preview_admin = None
        except Exception as e_upload_process_excel: st.error(f"Fehler Verarbeitung Excel: {e_upload_process_excel}"); traceback.print_exc(); st.session_state.uploaded_excel_bytes_for_save_admin = None; st.session_state.parsed_excel_df_for_preview_admin = None
    if st.session_state.get('parsed_excel_df_for_preview_admin') is not None:
        st.markdown("---"); st.markdown("**Vorschau Excel Preis-Matrix (nicht gespeichert):**"); st.dataframe(st.session_state.parsed_excel_df_for_preview_admin, use_container_width=True)
        if st.button(get_text_local("admin_save_price_matrix_button_xlsx", "...Excel...speichern"), key=f"save_uploaded_price_matrix_xlsx_btn{WIDGET_KEY_SUFFIX}"):
            if st.session_state.uploaded_excel_bytes_for_save_admin:
                if save_admin_setting_func('price_matrix_excel_bytes', st.session_state.uploaded_excel_bytes_for_save_admin):
                    st.success("Preis-Matrix (Excel) gespeichert!"); st.session_state.uploaded_excel_bytes_for_save_admin = None; st.session_state.parsed_excel_df_for_preview_admin = None
                    st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else: st.error("Fehler beim Speichern der Excel Preis-Matrix.")
            else: st.warning("Kein Excel-Inhalt zum Speichern.")
        st.markdown("---")
    st.subheader(get_text_local("admin_current_saved_price_matrix_header_xlsx", "Gespeicherte Preis-Matrix (Excel):"))
    current_price_matrix_excel_bytes_from_db = load_admin_setting_func('price_matrix_excel_bytes', None)
    if current_price_matrix_excel_bytes_from_db and isinstance(current_price_matrix_excel_bytes_from_db, bytes):
        display_errors_stored_matrix_pm_excel: List[str] = []; parsed_stored_df_pm_excel = parse_excel_func_local_admin(current_price_matrix_excel_bytes_from_db, display_errors_stored_matrix_pm_excel)
        if display_errors_stored_matrix_pm_excel:
            for err_pm_stored_excel in display_errors_stored_matrix_pm_excel: st.warning(f"Hinweis Laden Excel-Matrix: {err_pm_stored_excel}")
        if parsed_stored_df_pm_excel is not None and not parsed_stored_df_pm_excel.empty:
            st.dataframe(parsed_stored_df_pm_excel, use_container_width=True)
            if st.button(get_text_local("admin_delete_saved_price_matrix_button_xlsx", "Excel Preis-Matrix löschen"), key=f"delete_price_matrix_excel_final{WIDGET_KEY_SUFFIX}"):
                if save_admin_setting_func('price_matrix_excel_bytes', None): st.success("Excel Preis-Matrix gelöscht."); st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else: st.error("Fehler Löschen Excel Preis-Matrix.")
        else: st.warning("Gespeicherte Excel Preis-Matrix ungültig.")
    else: st.info("Keine Excel Preis-Matrix gespeichert.")
    st.markdown("---")
    st.info(get_text_local("admin_price_matrix_info_detailed_csv", "Laden Sie hier die Grundpreis-Matrix als CSV-Datei hoch..."))
    uploader_key_csv = f"price_matrix_upload_widget_csv{WIDGET_KEY_SUFFIX}"
    uploaded_file_csv = st.file_uploader(get_text_local("admin_upload_csv_label", "CSV-Datei hochladen"), type=["csv"], key=uploader_key_csv)
    if uploaded_file_csv is not None:
        try:
            csv_bytes = uploaded_file_csv.getvalue(); csv_content_temp = None
            try: csv_content_temp = csv_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try: csv_content_temp = csv_bytes.decode("iso-8859-1"); st.info("CSV mit ISO-8859-1 gelesen.")
                except UnicodeDecodeError as e_decode: st.error(f"CSV Dekodierfehler: {e_decode}")
            if csv_content_temp is not None: 
                parser_errors_matrix_upload_csv: List[str] = []; parsed_df_temp_csv = parse_csv_func_from_calculations(io.StringIO(csv_content_temp), parser_errors_matrix_upload_csv) 
                if parser_errors_matrix_upload_csv:
                    for err_matrix_csv in parser_errors_matrix_upload_csv: st.warning(f"Parser-Warnung (CSV): {err_matrix_csv}")
                if parsed_df_temp_csv is not None and not parsed_df_temp_csv.empty:
                    st.session_state.uploaded_csv_content_for_save_admin = csv_content_temp; st.session_state.parsed_csv_df_for_preview_admin = parsed_df_temp_csv
                    st.success(get_text_local("admin_csv_parse_success", "CSV geparst."))
                else: st.error(get_text_local("admin_csv_parse_error_empty", "CSV geparst, aber leer.")); st.session_state.uploaded_csv_content_for_save_admin = None; st.session_state.parsed_csv_df_for_preview_admin = None
        except Exception as e_upload_process_csv: st.error(f"Fehler Verarbeitung CSV: {e_upload_process_csv}"); traceback.print_exc(); st.session_state.uploaded_csv_content_for_save_admin = None; st.session_state.parsed_csv_df_for_preview_admin = None
    if st.session_state.get('parsed_csv_df_for_preview_admin') is not None:
        st.markdown("---"); st.markdown("**Vorschau CSV Preis-Matrix (nicht gespeichert):**"); st.dataframe(st.session_state.parsed_csv_df_for_preview_admin, use_container_width=True)
        if st.button(get_text_local("admin_save_price_matrix_button_csv", "...CSV...speichern"), key=f"save_uploaded_price_matrix_csv_btn{WIDGET_KEY_SUFFIX}"):
            if st.session_state.uploaded_csv_content_for_save_admin:
                if save_admin_setting_func('price_matrix_csv_data', st.session_state.uploaded_csv_content_for_save_admin):
                    st.success("Preis-Matrix (CSV) gespeichert!"); st.session_state.uploaded_csv_content_for_save_admin = None; st.session_state.parsed_csv_df_for_preview_admin = None
                    st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else: st.error("Fehler beim Speichern der CSV Preis-Matrix.")
            else: st.warning("Kein CSV-Inhalt zum Speichern.")
        st.markdown("---")
    st.subheader(get_text_local("admin_current_saved_price_matrix_header_csv", "Gespeicherte Preis-Matrix (CSV):"))
    current_price_matrix_csv_from_db = load_admin_setting_func('price_matrix_csv_data', "") 
    if current_price_matrix_csv_from_db and isinstance(current_price_matrix_csv_from_db, str) and current_price_matrix_csv_from_db.strip():
        display_errors_stored_matrix_pm_csv: List[str] = []; parsed_stored_df_pm_csv = parse_csv_func_from_calculations(io.StringIO(current_price_matrix_csv_from_db), display_errors_stored_matrix_pm_csv)
        if display_errors_stored_matrix_pm_csv:
            for err_pm_stored_csv in display_errors_stored_matrix_pm_csv: st.warning(f"Hinweis Laden CSV-Matrix: {err_pm_stored_csv}")
        if parsed_stored_df_pm_csv is not None and not parsed_stored_df_pm_csv.empty:
            st.dataframe(parsed_stored_df_pm_csv, use_container_width=True)
            if st.button(get_text_local("admin_delete_saved_price_matrix_button_csv", "...CSV...löschen"), key=f"delete_price_matrix_csv_final{WIDGET_KEY_SUFFIX}"):
                if save_admin_setting_func('price_matrix_csv_data', None): st.success("CSV Preis-Matrix gelöscht."); st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else: st.error("Fehler Löschen CSV Preis-Matrix.")
        else:
            st.warning("Gespeicherte CSV Preis-Matrix ungültig."); st.text_area("Rohdaten CSV (max. 500 Z.)", value=current_price_matrix_csv_from_db[:500]+"..." if len(current_price_matrix_csv_from_db) > 500 else current_price_matrix_csv_from_db, height=100, disabled=True, key=f"raw_db_csv_preview{WIDGET_KEY_SUFFIX}")
    else: st.info("Keine CSV Preis-Matrix gespeichert.")

def render_tariff_management(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    st.subheader(get_text_local("admin_tariff_management_header", "Einspeisevergütungen"))
    st.info(get_text_local("admin_tariff_management_info", "Verwalten Sie hier die Einspeisevergütungen..."))
    current_feed_in_tariffs_block = load_admin_setting_func('feed_in_tariffs', _DEFAULT_FEED_IN_TARIFFS_FALLBACK.copy())
    if not isinstance(current_feed_in_tariffs_block, dict): current_feed_in_tariffs_block = _DEFAULT_FEED_IN_TARIFFS_FALLBACK.copy()
    if 'parts' not in current_feed_in_tariffs_block or not isinstance(current_feed_in_tariffs_block['parts'], list): current_feed_in_tariffs_block['parts'] = _DEFAULT_FEED_IN_TARIFFS_FALLBACK['parts'][:]
    if 'full' not in current_feed_in_tariffs_block or not isinstance(current_feed_in_tariffs_block['full'], list): current_feed_in_tariffs_block['full'] = _DEFAULT_FEED_IN_TARIFFS_FALLBACK['full'][:]
    form_key_parts = f"tariff_form_parts{WIDGET_KEY_SUFFIX}" 
    st.markdown(f"#### {get_text_local('admin_partial_feed_in_header', 'Teileinspeisung')}")
    with st.form(key=form_key_parts):
        rendered_tariffs_parts_ui, final_valid_parts_form_check = manage_tariff_list_ui(current_feed_in_tariffs_block['parts'], f"parts_cat{WIDGET_KEY_SUFFIX}")
        submitted_parts = st.form_submit_button(get_text_local("admin_save_tariffs_button_parts", "Tarife für Teileinspeisung speichern"))
        if submitted_parts:
            final_processed_tariffs_parts = rendered_tariffs_parts_ui; final_valid_parts_form = True 
            for item_tariff in final_processed_tariffs_parts:
                if item_tariff.get("kwp_min", 0.0) >= item_tariff.get("kwp_max", 0.0): final_valid_parts_form = False; break
            if final_valid_parts_form:
                current_feed_in_tariffs_block['parts'] = final_processed_tariffs_parts
                if save_admin_setting_func('feed_in_tariffs', current_feed_in_tariffs_block):
                    st.success(get_text_local("admin_tariffs_saved_success_parts", "Teileinspeisungstarife gespeichert.")); st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else: st.error(get_text_local("admin_tariffs_save_error", "Fehler beim Speichern der Tarife."))
            else: st.error("Einige Tarifstufen für Teileinspeisung sind ungültig...")
    st.markdown("---")
    form_key_full = f"tariff_form_full{WIDGET_KEY_SUFFIX}" 
    st.markdown(f"#### {get_text_local('admin_full_feed_in_header', 'Volleinspeisung')}")
    with st.form(key=form_key_full):
        rendered_tariffs_full_ui, final_valid_full_form_check = manage_tariff_list_ui(current_feed_in_tariffs_block['full'], f"full_cat{WIDGET_KEY_SUFFIX}")
        submitted_full = st.form_submit_button(get_text_local("admin_save_tariffs_button_full", "Tarife für Volleinspeisung speichern"))
        if submitted_full: 
            final_processed_tariffs_full = rendered_tariffs_full_ui; final_valid_full_form = True
            for item_tariff_f in final_processed_tariffs_full:
                if item_tariff_f.get("kwp_min", 0.0) >= item_tariff_f.get("kwp_max", 0.0): final_valid_full_form = False; break
            if final_valid_full_form:
                current_feed_in_tariffs_block['full'] = final_processed_tariffs_full
                if save_admin_setting_func('feed_in_tariffs', current_feed_in_tariffs_block):
                    st.success(get_text_local("admin_tariffs_saved_success_full", "Volleinspeisungstarife gespeichert.")); st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else: st.error(get_text_local("admin_tariffs_save_error", "Fehler beim Speichern der Tarife."))
            else: st.error("Einige Tarifstufen für Volleinspeisung sind ungültig...")
    st.markdown("---")

def render_visualization_settings(load_admin_setting_func: Callable, save_admin_setting_func: Callable ):
    st.subheader(get_text_local("admin_visualization_settings_header", "Globale Visualisierungs-Einstellungen"))
    st.info(get_text_local("admin_visualization_settings_info", "Passen Sie hier die Standardfarben... an."))
    current_global_constants = load_admin_setting_func('global_constants', _DEFAULT_GLOBAL_CONSTANTS_FALLBACK)
    if not isinstance(current_global_constants.get('visualization_settings'), dict): current_global_constants['visualization_settings'] = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.get('visualization_settings', {}).copy()
    viz_settings = current_global_constants['visualization_settings']; default_viz_settings_fallback = _DEFAULT_GLOBAL_CONSTANTS_FALLBACK.get('visualization_settings', {})
    plotly_palettes = ["Plotly", "D3", "G10", "T10", "Alphabet", "Dark24", "Light24", "Set1", "Set2", "Set3", "Pastel", "Pastel1", "Pastel2", "Antique", "Bold", "Safe", "Vivid"]
    with st.form(f"visualization_settings_form{WIDGET_KEY_SUFFIX}"):
        st.markdown(f"**{get_text_local('admin_viz_general_colors_header', 'Allgemeine Diagrammfarben')}**")
        selected_palette_val = viz_settings.get("default_color_palette", default_viz_settings_fallback.get("default_color_palette"))
        selected_palette = st.selectbox(get_text_local("admin_viz_default_palette_label", "Standard-Farbpalette..."), options=plotly_palettes, index=plotly_palettes.index(selected_palette_val) if selected_palette_val in plotly_palettes else 0, key=f"viz_default_palette_select{WIDGET_KEY_SUFFIX}", help=get_text_local("admin_viz_default_palette_help", "..."))
        primary_color = st.color_picker(get_text_local("admin_viz_primary_color_label", "Primäre Diagrammfarbe"), value=viz_settings.get("primary_chart_color", default_viz_settings_fallback.get("primary_chart_color")), key=f"viz_primary_color_picker{WIDGET_KEY_SUFFIX}")
        secondary_color = st.color_picker(get_text_local("admin_viz_secondary_color_label", "Sekundäre Diagrammfarbe"), value=viz_settings.get("secondary_chart_color", default_viz_settings_fallback.get("secondary_chart_color")), key=f"viz_secondary_color_picker{WIDGET_KEY_SUFFIX}")
        st.markdown(f"---<br>**{get_text_local('admin_viz_font_settings_header', 'Schriftart-Einstellungen')}**")
        font_family = st.text_input(get_text_local("admin_viz_font_family_label", "Schriftfamilie..."), value=viz_settings.get("chart_font_family", default_viz_settings_fallback.get("chart_font_family")), key=f"viz_font_family_input{WIDGET_KEY_SUFFIX}")
        c1f, c2f, c3f = st.columns(3) 
        font_size_title = c1f.number_input(get_text_local("admin_viz_font_size_title_label", "Schriftgröße Titel"), min_value=8, max_value=30, value=int(viz_settings.get("chart_font_size_title", default_viz_settings_fallback.get("chart_font_size_title"))), key=f"viz_font_size_title_num{WIDGET_KEY_SUFFIX}")
        font_size_axis = c2f.number_input(get_text_local("admin_viz_font_size_axis_label", "Schriftgröße Achsenbeschr."), min_value=6, max_value=24, value=int(viz_settings.get("chart_font_size_axis_label", default_viz_settings_fallback.get("chart_font_size_axis_label"))), key=f"viz_font_size_axis_num{WIDGET_KEY_SUFFIX}")
        font_size_tick = c3f.number_input(get_text_local("admin_viz_font_size_tick_label", "Schriftgröße Achsenticks"), min_value=5, max_value=20, value=int(viz_settings.get("chart_font_size_tick_label", default_viz_settings_fallback.get("chart_font_size_tick_label"))), key=f"viz_font_size_tick_num{WIDGET_KEY_SUFFIX}")
        submitted_viz_settings = st.form_submit_button(get_text_local("admin_save_visualization_settings_button", "Visualisierungs-Einstellungen Speichern"))
    if submitted_viz_settings:
        new_viz_settings = {"default_color_palette": selected_palette, "primary_chart_color": primary_color, "secondary_chart_color": secondary_color, "chart_font_family": font_family, "chart_font_size_title": font_size_title, "chart_font_size_axis_label": font_size_axis, "chart_font_size_tick_label": font_size_tick, **{k:v for k,v in viz_settings.items() if isinstance(v, dict)}}
        current_global_constants['visualization_settings'] = new_viz_settings
        if save_admin_setting_func('global_constants', current_global_constants):
            st.success(get_text_local("admin_visualization_settings_saved_success", "Visualisierungs-Einstellungen gespeichert."))
            st.session_state.selected_page_key_sui = "admin"; st.rerun()
        else: st.error(get_text_local("admin_visualization_settings_save_error", "Fehler beim Speichern der Visualisierungs-Einstellungen."))

def render_advanced_settings(load_admin_setting_func: Callable, save_admin_setting_func: Callable ):
    st.subheader(get_text_local("admin_advanced_header", "Erweiterte Einstellungen"))
    render_api_key_settings(load_admin_setting_func, save_admin_setting_func) 
    st.markdown("---"); st.subheader(get_text_local("admin_localization_settings_header", "Lokalisierung"))
    st.info(get_text_local("admin_localization_info", "Bearbeiten Sie hier die Texte der Anwendung (JSON-Format)..."))
    current_locale_data = load_admin_setting_func('de_locale_data', {}); locale_json_string = "{}"
    if not isinstance(current_locale_data, dict): current_locale_data = {}
    try: locale_json_string = json.dumps(current_locale_data, indent=2, ensure_ascii=False)
    except Exception as e_json_dump: st.error(f"Fehler Konvertierung JSON: {e_json_dump}")
    edited_locale_json_string = st.text_area(get_text_local("admin_locale_json_editor_label", "Texte (JSON-Editor)"), value=locale_json_string, height=300, key=f"locale_json_editor_final{WIDGET_KEY_SUFFIX}")
    if st.button(get_text_local("admin_save_locale_button", "Lokalisierungstexte speichern"), key=f"save_locale_btn_final{WIDGET_KEY_SUFFIX}"):
      try:
        parsed_locale_data = json.loads(edited_locale_json_string)
        if not isinstance(parsed_locale_data, dict): st.error("Eingegebene Lokalisierungsdaten kein gültiges JSON-Objekt.")
        elif save_admin_setting_func('de_locale_data', parsed_locale_data): st.success("Lokalisierungstexte gespeichert. Bitte App neu starten.");
        else: st.error("Fehler beim Speichern der Lokalisierungstexte.")
      except json.JSONDecodeError as e_json_decode: st.error(f"Ungültiges JSON: {e_json_decode}")
      except Exception as e_locale_general: st.error(f"Fehler Speichern Locale: {e_locale_general}")
    st.markdown("---"); st.subheader(get_text_local("admin_debugging_settings_header", "Debugging-Einstellungen"))
    current_debug_mode_for_display = load_admin_setting_func('app_debug_mode_enabled', False)
    if not isinstance(current_debug_mode_for_display, bool): current_debug_mode_for_display = False
    with st.form(f"debug_settings_form_final{WIDGET_KEY_SUFFIX}"):
        app_debug_mode_new_val = st.checkbox(get_text_local("admin_enable_debug_mode_label", "App-weiten Debug-Modus aktivieren..."),value=current_debug_mode_for_display,key=f"app_debug_mode_checkbox_final_key{WIDGET_KEY_SUFFIX}", help=get_text_local("admin_enable_debug_mode_help", "..."))
        submitted_debug_form_button = st.form_submit_button(get_text_local("admin_save_debug_settings_button", "Debugging-Einstellungen speichern"))
    if submitted_debug_form_button:
        if save_admin_setting_func('app_debug_mode_enabled', app_debug_mode_new_val): 
            st.success(get_text_local("admin_debug_settings_saved_success", "Debugging-Einstellungen gespeichert.")); 
            st.session_state.selected_page_key_sui = "admin"; st.rerun()
        else: st.error(get_text_local("admin_debug_settings_save_error", "Fehler beim Speichern der Debugging-Einstellungen."))
    st.markdown("---"); st.subheader(get_text_local("admin_reset_data_header", "Daten zurücksetzen"))
    if st.checkbox(get_text_local("admin_show_reset_options_label", "Optionen zum Zurücksetzen anzeigen..."), key=f"show_reset_options_final{WIDGET_KEY_SUFFIX}"):
        st.warning(get_text_local("admin_reset_warning_text", "ACHTUNG: Das Zurücksetzen...nicht rückgängig...")); confirm_text_reset = "ALLES ENDGÜLTIG LÖSCHEN"
        user_confirm_text = st.text_input(f"Geben Sie exakt '{confirm_text_reset}' ein...", key=f"confirm_delete_text_input_final{WIDGET_KEY_SUFFIX}")
        if st.button(get_text_local("admin_reset_app_data_button", "🚨 App-Daten jetzt endgültig zurücksetzen"), key=f"reset_all_app_data_btn_final{WIDGET_KEY_SUFFIX}", type="primary"):
            if user_confirm_text == confirm_text_reset:
                try:
                    _base_dir_for_reset = os.path.dirname(os.path.abspath(__file__)); _data_dir_for_reset = os.path.join(_base_dir_for_reset, 'data'); _db_path_for_reset = os.path.join(_data_dir_for_reset, 'app_data.db')
                    if os.path.exists(_db_path_for_reset):
                        os.remove(_db_path_for_reset); st.success(f"Alle Anwendungsdaten ({_db_path_for_reset}) wurden gelöscht.")
                        st.info("Bitte starten Sie die Streamlit-Anwendung vollständig neu...");
                        for k_to_del in list(st.session_state.keys()):
                            if k_to_del not in ['_admin_panel_texts', 'selected_page_key_sui']: del st.session_state[k_to_del]
                        st.session_state.selected_page_key_sui = "admin" 
                        st.experimental_rerun() 
                    else: st.warning(f"Keine Datenbankdatei unter '{_db_path_for_reset}' zum Löschen gefunden.")
                except Exception as e_reset_final_exc: st.error(f"Fehler beim Zurücksetzen der Daten: {e_reset_final_exc}")
            else: st.error(f"Falscher Bestätigungstext...")
    
def render_pdf_design_settings(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    st.subheader(get_text_local("admin_pdf_company_branding_expander", "Firmen-Branding für PDF-Dokumente"))
    active_company_id = load_admin_setting_func('active_company_id', None)
    company_info_for_pdf = {"name": "Ihre Firma (Platzhalter)", "id":0}; company_logo_b64_for_pdf = None
    if _get_company_by_id_safe and callable(_get_company_by_id_safe) and active_company_id:
        active_company_data = _get_company_by_id_safe(int(active_company_id))
        if active_company_data: company_info_for_pdf = active_company_data; company_logo_b64_for_pdf = active_company_data.get('logo_base64')
    col_pdf_logo, col_pdf_info = st.columns([1,2])
    with col_pdf_logo:
        st.markdown("<h6>" + get_text_local("admin_pdf_logo_header_short", "Logo für PDF") + "</h6>", unsafe_allow_html=True)
        if company_logo_b64_for_pdf:
            try: st.image(base64.b64decode(company_logo_b64_for_pdf), width=150, caption=get_text_local("admin_pdf_current_logo_caption", "Aktives Logo"))
            except Exception: st.warning(get_text_local("admin_pdf_logo_display_error", "Fehler Anzeige Logo"))
        else: st.caption(get_text_local("admin_pdf_no_active_logo", "Kein Logo für aktive Firma gesetzt."))
        st.caption(get_text_local("admin_pdf_logo_manage_in_companies", "Logo wird in der 'Firmenverwaltung'... verwendet."))
    with col_pdf_info:
        st.markdown("<h6>" + get_text_local("admin_pdf_company_info_header_short", "Firmeninfo für PDF") + "</h6>", unsafe_allow_html=True)
        for field_key, label_key_suffix in [("name","name"), ("street","address1"), ("zip_code","address2_zip"), ("city","address2_city"), ("phone","phone"), ("email","email"), ("website","website"), ("tax_id","tax_id"), ("commercial_register","commercial_register")]:
            val_disp = company_info_for_pdf.get(field_key, '')
            if field_key == "zip_code": val_disp = f"{company_info_for_pdf.get('zip_code', '')} {company_info_for_pdf.get('city', '')}".strip()
            if field_key == "city" and "zip_code" in [f[0] for f in [("name","name"), ("street","address1"), ("zip_code","address2_zip"), ("city","address2_city"), ("phone","phone"), ("email","email"), ("website","website"), ("tax_id","tax_id"), ("commercial_register","commercial_register")]]: continue
            st.text_input(get_text_local(f"admin_pdf_company_{label_key_suffix}", field_key.replace("_"," ").title()), value=val_disp, disabled=True, key=f"pdf_disp_ci_{field_key}{WIDGET_KEY_SUFFIX}")
        st.caption(get_text_local("admin_pdf_company_info_manage_in_companies", "Firmeninformationen werden in 'Firmenverwaltung' gepflegt..."))
    st.markdown("---"); st.subheader(get_text_local("admin_pdf_design_colors_header", "PDF Design Farben"))
    PDF_DESIGN_SETTINGS_DEFAULT = {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
    current_design_settings = load_admin_setting_func('pdf_design_settings', PDF_DESIGN_SETTINGS_DEFAULT.copy())
    if not isinstance(current_design_settings, dict): current_design_settings = PDF_DESIGN_SETTINGS_DEFAULT.copy()
    with st.form(f"pdf_design_form{WIDGET_KEY_SUFFIX}"):
      primary_color = st.color_picker(get_text_local("admin_pdf_primary_color_label", "PDF Haupt-/Akzentfarbe"), value=current_design_settings.get('primary_color', PDF_DESIGN_SETTINGS_DEFAULT['primary_color']), key=f"pdf_primary_color{WIDGET_KEY_SUFFIX}")
      secondary_color = st.color_picker(get_text_local("admin_pdf_secondary_color_label", "PDF Sekundärfarbe"), value=current_design_settings.get('secondary_color', PDF_DESIGN_SETTINGS_DEFAULT['secondary_color']), key=f"pdf_secondary_color{WIDGET_KEY_SUFFIX}")
      submitted_pdf_design = st.form_submit_button(get_text_local("admin_save_pdf_design_button", "Design Einstellungen Speichern"))
    if submitted_pdf_design:
        updated_design_settings = {'primary_color': primary_color, 'secondary_color': secondary_color}
        if save_admin_setting_func('pdf_design_settings', updated_design_settings):
          st.success(get_text_local("admin_pdf_design_settings_saved_success", "PDF Design gespeichert.")); 
          st.session_state.selected_page_key_sui = "admin"; st.rerun()
        else: st.error(get_text_local("admin_pdf_design_settings_save_error", "Fehler Speichern PDF Design."))

def manage_templates_local(template_type_key: str, template_list_setting_key: str, item_name_label_key: str, item_content_label_key: Optional[str] = None, is_image_template: bool = False ):
    st.subheader(get_text_local(f"admin_{template_type_key}_header", f"{template_type_key.replace('_', ' ').title()} Vorlagen"))
    templates: List[Dict[str, Any]] = _load_admin_setting_safe(template_list_setting_key, [])
    if not isinstance(templates, list): st.error(f"Fehler: Vorlagendaten für '{template_list_setting_key}' nicht im Listenformat."); templates = []
    form_key_mt = f"{template_type_key}_form_mt_local_tpl{WIDGET_KEY_SUFFIX}"
    edit_mode_session_key = f"edit_mode_template_{template_type_key}{WIDGET_KEY_SUFFIX}"
    edit_index_session_key = f"edit_index_template_{template_type_key}{WIDGET_KEY_SUFFIX}"
    if edit_mode_session_key not in st.session_state: st.session_state[edit_mode_session_key] = False
    if edit_index_session_key not in st.session_state: st.session_state[edit_index_session_key] = -1
    options_for_select = [get_text_local("admin_template_add_new_option", "--- Neue Vorlage erstellen ---")] + [f"{t.get('name', f'Vorlage {i+1}')} (ID: {i})" for i, t in enumerate(templates)]
    current_selection_index = 0
    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
        if 0 <= st.session_state[edit_index_session_key] < len(templates): current_selection_index = st.session_state[edit_index_session_key] + 1
        else: st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1
    selected_template_display_name = st.selectbox(get_text_local("admin_select_template_to_edit_or_add_new", "Vorlage bearbeiten..."), options=options_for_select, key=f"select_or_add_template_{template_type_key}{WIDGET_KEY_SUFFIX}_select", index=current_selection_index)
    if selected_template_display_name == get_text_local("admin_template_add_new_option", "--- Neue Vorlage erstellen ---"):
        if st.session_state[edit_mode_session_key] or st.session_state[edit_index_session_key] != -1:
            st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1; st.session_state.selected_page_key_sui = "admin"; st.rerun()
    else:
        try:
            selected_idx = int(selected_template_display_name.split("(ID: ")[1].replace(")", ""))
            if not st.session_state[edit_mode_session_key] or st.session_state[edit_index_session_key] != selected_idx:
                st.session_state[edit_mode_session_key] = True; st.session_state[edit_index_session_key] = selected_idx; st.session_state.selected_page_key_sui = "admin"; st.rerun()
        except (IndexError, ValueError):
            st.error(get_text_local("admin_template_selection_error", "Fehler bei der Auswahl der Vorlage..."))
            if st.session_state[edit_mode_session_key] or st.session_state[edit_index_session_key] != -1:
                st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1; st.session_state.selected_page_key_sui = "admin"; st.rerun()
    current_name_val = ""; current_content_val = ""; current_image_data_b64 = None
    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
        if 0 <= st.session_state[edit_index_session_key] < len(templates):
            template_to_edit = templates[st.session_state[edit_index_session_key]]; current_name_val = template_to_edit.get('name', '')
            if is_image_template: current_image_data_b64 = template_to_edit.get('data')
            else: current_content_val = template_to_edit.get('content', '')
        else:
            st.warning(get_text_local("admin_template_edit_invalid_index_warning", "Die ausgewählte Vorlage...existiert nicht mehr...")); st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1; st.session_state.selected_page_key_sui = "admin"; st.rerun()
    with st.form(form_key_mt, clear_on_submit=False): # clear_on_submit hier auf False, um Werte bei Validierungsfehlern zu behalten
        st.markdown(f"**{get_text_local('admin_template_edit_add_header', 'Vorlage erstellen / bearbeiten')}**")
        new_template_name = st.text_input(get_text_local(item_name_label_key, "Vorlagenname"), value=current_name_val, key=f"{template_type_key}_name_input_mt{WIDGET_KEY_SUFFIX}_form")
        new_template_data_b64_for_save = None; new_template_content_input = "" 
        if is_image_template:
            uploaded_image_file = st.file_uploader(get_text_local("admin_upload_title_image", "Bild hochladen..."), type=["png", "jpg", "jpeg"], key=f"{template_type_key}_upload_fu_mt{WIDGET_KEY_SUFFIX}_form")
            if uploaded_image_file: new_template_data_b64_for_save = base64.b64encode(uploaded_image_file.getvalue()).decode('utf-8'); st.image(uploaded_image_file, caption=get_text_local("admin_image_preview", "Vorschau"), width=200)
            elif current_image_data_b64 and st.session_state[edit_mode_session_key]:
                try: st.image(base64.b64decode(current_image_data_b64), caption=get_text_local("admin_current_image", "Aktuelles Bild"), width=200); new_template_data_b64_for_save = current_image_data_b64
                except Exception: st.error(get_text_local("admin_error_displaying_current_image", "Fehler beim Anzeigen..."))
        else: new_template_content_input = st.text_area(get_text_local(item_content_label_key or "admin_template_content_label", "Inhalt..."), value=current_content_val, height=200, key=f"{template_type_key}_content_ta_mt{WIDGET_KEY_SUFFIX}_form")
        submit_button_text = get_text_local("admin_save_template_button", "Vorlage speichern")
        if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1: submit_button_text = get_text_local("admin_update_template_button", "Vorlage aktualisieren")
        submitted = st.form_submit_button(submit_button_text)
        if submitted:
            if not new_template_name.strip(): st.error(get_text_local("admin_template_name_required", "Vorlagenname ist erforderlich."))
            else:
                new_template_entry = {"name": new_template_name.strip()}; valid_to_save = True
                if is_image_template:
                    if new_template_data_b64_for_save: new_template_entry["data"] = new_template_data_b64_for_save
                    elif not st.session_state[edit_mode_session_key]: st.error(get_text_local("admin_image_required_for_new_template", "Für eine neue Bildvorlage...")); valid_to_save = False
                else: new_template_entry["content"] = new_template_content_input
                if valid_to_save:
                    temp_templates_list = templates[:]
                    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
                        if 0 <= st.session_state[edit_index_session_key] < len(temp_templates_list): temp_templates_list[st.session_state[edit_index_session_key]] = new_template_entry
                        else: st.error(get_text_local("admin_template_update_error_invalid_index", "Fehler: Die zu aktualisierende Vorlage...")); valid_to_save = False 
                    else: temp_templates_list.append(new_template_entry)
                    if valid_to_save:
                        if _save_admin_setting_safe(template_list_setting_key, temp_templates_list):
                            st.success(get_text_local("admin_template_saved_success", "Vorlage gespeichert.")); st.session_state.selected_page_key_sui = "admin"; st.rerun()
                        else: st.error(get_text_local("admin_template_save_error", "Fehler beim Speichern der Vorlage."))
    if st.session_state[edit_mode_session_key] and st.session_state[edit_index_session_key] != -1:
        if 0 <= st.session_state[edit_index_session_key] < len(templates):
            delete_button_key = f"delete_template_{template_type_key}{WIDGET_KEY_SUFFIX}_outer_btn"
            confirm_delete_session_key = f"confirm_delete_tpl_{template_type_key}_{st.session_state[edit_index_session_key]}{WIDGET_KEY_SUFFIX}_conf"
            if st.button(get_text_local("admin_delete_template_button", "Ausgewählte Vorlage löschen"), key=delete_button_key, type="secondary"):
                if st.session_state.get(confirm_delete_session_key, False):
                    temp_templates_list_del = templates[:]
                    try: 
                        del temp_templates_list_del[st.session_state[edit_index_session_key]]
                        if _save_admin_setting_safe(template_list_setting_key, temp_templates_list_del):
                            st.success(get_text_local("admin_template_deleted_success", "Vorlage gelöscht.")); 
                            if confirm_delete_session_key in st.session_state: del st.session_state[confirm_delete_session_key]
                            st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1
                            st.session_state.selected_page_key_sui = "admin"; st.rerun()
                        else: st.error(get_text_local("admin_template_delete_error", "Fehler beim Speichern nach dem Löschen..."))
                    except IndexError: 
                        st.error("Fehler: Vorlage zum Löschen nicht im Index gefunden (IndexError).")
                        if confirm_delete_session_key in st.session_state: del st.session_state[confirm_delete_session_key]
                        st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1
                        st.session_state.selected_page_key_sui = "admin"; st.rerun()
                    except Exception as e: 
                        st.error(f"Ein unerwarteter Fehler ist beim Löschen aufgetreten: {e}")
                        if confirm_delete_session_key in st.session_state: del st.session_state[confirm_delete_session_key]
                        st.session_state[edit_mode_session_key] = False; st.session_state[edit_index_session_key] = -1
                        st.session_state.selected_page_key_sui = "admin"; st.rerun()
                else:
                    st.warning(get_text_local("admin_confirm_delete_template", "Sicher? Erneut klicken zum Löschen."))
                    st.session_state[confirm_delete_session_key] = True; st.session_state.selected_page_key_sui = "admin"; st.rerun() 
    st.markdown("---")

def render_api_key_settings(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    st.subheader(get_text_local("admin_api_keys_header", "API-Key Verwaltung"))
    st.info(get_text_local("admin_api_keys_info", "Verwalten Sie hier Ihre API-Schlüssel für externe Dienste..."))
    api_keys_to_manage = {"Maps_api_key": get_text_local("admin_Maps_api_key_label", "Google Maps API Key"), "bing_maps_api_key": get_text_local("admin_bing_maps_api_key_label", "Bing Maps API Key..."), "osm_nominatim_email": get_text_local("admin_osm_nominatim_email_label", "OpenStreetMap Nominatim E-Mail...")}
    current_api_keys_values_for_display = {key_name: load_admin_setting_func(key_name, "LEER_DEFAULT") for key_name in api_keys_to_manage.keys()}
    with st.form(f"api_keys_form{WIDGET_KEY_SUFFIX}"):
        new_api_key_inputs = {}
        for key_name, key_label_text in api_keys_to_manage.items():
            current_val_for_placeholder = current_api_keys_values_for_display.get(key_name, "")
            display_value_placeholder = "**********" if current_val_for_placeholder and current_val_for_placeholder not in ["PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN", "LEER_DEFAULT"] else get_text_local("api_key_not_set_placeholder", "Nicht gesetzt")
            new_api_key_inputs[key_name] = st.text_input(key_label_text, value="", type="password", help=f"{get_text_local('api_key_current_value_notice', 'Aktuell...')}: {display_value_placeholder}. {get_text_local('api_key_input_help', 'Geben Sie hier einen neuen Schlüssel ein...')}", key=f"api_key_input_{key_name}{WIDGET_KEY_SUFFIX}")
        submitted_api_keys = st.form_submit_button(get_text_local("admin_save_api_keys_button", "API-Schlüssel speichern"))
        if submitted_api_keys:
            something_changed_and_saved = False
            for key_name, new_value_from_input in new_api_key_inputs.items():
                if new_value_from_input and new_value_from_input.strip():
                    value_to_save = new_value_from_input.strip()
                    if save_admin_setting_func(key_name, value_to_save):
                        reloaded_value = load_admin_setting_func(key_name, "FEHLER_BEIM_NEULADEN")
                        if reloaded_value == value_to_save: st.success(f"'{api_keys_to_manage[key_name]}' erfolgreich gespeichert..."); something_changed_and_saved = True
                        else: st.error(f"Fehler Verifizierung von '{api_keys_to_manage[key_name]}'. Gesp.: '{value_to_save}', Gel.: '{reloaded_value}'.")
                    else: st.error(get_text_local("admin_api_key_save_error", f"Fehler beim Speichern von {api_keys_to_manage[key_name]}."))
            if something_changed_and_saved: st.info("Änderungen verarbeitet..."); st.session_state.selected_page_key_sui = "admin"; st.rerun()
            elif not any(new_api_key_inputs.values()): st.info("Keine neuen API-Schlüssel eingegeben...")
    st.markdown("---")

def manage_tariff_list_ui(tariff_list_input: List[Dict[str, Any]], form_element_key_suffix: str) -> Tuple[List[Dict[str, Any]], bool]:
    collected_tariffs_from_ui = []; all_entries_valid = True
    actual_tariff_list_for_ui = tariff_list_input[:] 
    if not actual_tariff_list_for_ui : actual_tariff_list_for_ui = [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 0.0}]
    for i, tariff_entry_db_like in enumerate(actual_tariff_list_for_ui):
        cols_tariff_ui = st.columns([2, 2, 2, 1]); key_base = f"tariff_entry_{form_element_key_suffix}_{i}{WIDGET_KEY_SUFFIX}_ui" # Suffix konsistent
        kwp_min_current_value = st.session_state.get(f"{key_base}_min", float(tariff_entry_db_like.get("kwp_min", 0.0)))
        kwp_min_ui_val = cols_tariff_ui[0].number_input(label=f"kWp Min #{i+1}", min_value=0.0, value=kwp_min_current_value, step=0.01, key=f"{key_base}_min", format="%.2f")
        min_value_for_kwp_max = kwp_min_ui_val + 0.01 if kwp_min_ui_val is not None else 0.01
        kwp_max_current_value = st.session_state.get(f"{key_base}_max", float(tariff_entry_db_like.get("kwp_max", min_value_for_kwp_max + 9.99)))
        corrected_kwp_max_for_display = max(kwp_max_current_value, min_value_for_kwp_max)
        kwp_max_ui_val = cols_tariff_ui[1].number_input(label=f"kWp Max #{i+1}", min_value=min_value_for_kwp_max, value=corrected_kwp_max_for_display, step=0.01, key=f"{key_base}_max", format="%.2f")
        ct_per_kwh_current_value = st.session_state.get(f"{key_base}_ct", float(tariff_entry_db_like.get("ct_per_kwh", 0.0)))
        ct_per_kwh_ui_val = cols_tariff_ui[2].number_input(label=f"ct/kWh #{i+1}", min_value=0.0, value=ct_per_kwh_current_value, step=0.1, key=f"{key_base}_ct", format="%.1f")
        collected_tariffs_from_ui.append({"kwp_min": kwp_min_ui_val, "kwp_max": kwp_max_ui_val, "ct_per_kwh": ct_per_kwh_ui_val})
        if kwp_min_ui_val is not None and kwp_max_ui_val is not None and kwp_min_ui_val >= kwp_max_ui_val:
            cols_tariff_ui[1].error("Max kWp muss größer Min kWp sein!"); all_entries_valid = False
    return collected_tariffs_from_ui, all_entries_valid

def render_admin_panel(
    texts: Union[Dict[str, str], Tuple], 
    get_db_connection_func: Callable[[], Optional[Any]],
    save_admin_setting_func: Callable[[str, Any], bool],
    load_admin_setting_func: Callable[[str, Any], Any],
    parse_price_matrix_csv_func: Callable[[Union[str, io.StringIO], List[str]], Optional[pd.DataFrame]], 
    list_products_func: Callable[[Optional[str]], List[Dict[str, Any]]],
    add_product_func: Callable[[Dict[str, Any]], Optional[int]],
    update_product_func: Callable[[Union[int, float], Dict[str, Any]], bool],
    delete_product_func: Callable[[Union[int, float]], bool],
    get_product_by_id_func: Callable[[Union[int, float]], Optional[Dict[str, Any]]],
    get_product_by_model_name_func: Callable[[str], Optional[Dict[str, Any]]],
    list_product_categories_func: Callable[[], List[str]],
    db_list_companies_func: Callable[[], List[Dict[str, Any]]],
    db_add_company_func: Callable[[Dict[str, Any]], Optional[int]],
    db_get_company_by_id_func: Callable[[int], Optional[Dict[str, Any]]],
    db_update_company_func: Callable[[int, Dict[str, Any]], bool],
    db_delete_company_func: Callable[[int], bool],
    db_set_default_company_func: Callable[[int], bool],
    db_add_company_document_func: Callable[[int, str, str, str, bytes], Optional[int]],
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    db_delete_company_document_func: Callable[[int], bool],
    **kwargs: Any 
):
    global _load_admin_setting_safe, _save_admin_setting_safe, _parse_price_matrix_csv_safe
    global _list_products_safe, _add_product_safe, _update_product_safe, _delete_product_safe
    global _get_product_by_id_safe, _get_product_by_model_name_safe, _list_product_categories_safe
    global _list_companies_safe, _add_company_safe, _get_company_by_id_safe, _update_company_safe
    global _delete_company_safe, _set_default_company_safe, _add_company_document_safe
    global _list_company_documents_safe, _delete_company_document_safe
    global _parse_price_matrix_excel_func

    _load_admin_setting_safe = load_admin_setting_func; _save_admin_setting_safe = save_admin_setting_func
    _parse_price_matrix_csv_safe = parse_price_matrix_csv_func 
    _list_products_safe = list_products_func; _add_product_safe = add_product_func; _update_product_safe = update_product_func; _delete_product_safe = delete_product_func
    _get_product_by_id_safe = get_product_by_id_func; _get_product_by_model_name_safe = get_product_by_model_name_func; _list_product_categories_safe = list_product_categories_func
    _list_companies_safe = db_list_companies_func; _add_company_safe = db_add_company_func; _get_company_by_id_safe = db_get_company_by_id_func; _update_company_safe = db_update_company_func
    _delete_company_safe = db_delete_company_func; _set_default_company_safe = db_set_default_company_func; _add_company_document_safe = db_add_company_document_func
    _list_company_documents_safe = db_list_company_documents_func; _delete_company_document_safe = db_delete_company_document_func
    
    passed_excel_parser = kwargs.get('parse_price_matrix_excel_func')
    if passed_excel_parser and callable(passed_excel_parser): _parse_price_matrix_excel_func = passed_excel_parser
    elif callable(parse_module_price_matrix_excel): _parse_price_matrix_excel_func = parse_module_price_matrix_excel
    else:
        def _dummy_parse_excel_admin_final(excel_bytes, errors_list_local): 
            if errors_list_local is not None: errors_list_local.append("Admin: Dummy Excel-Parser (final) aktiv.")
            return None
        _parse_price_matrix_excel_func = _dummy_parse_excel_admin_final

    actual_texts_dict_for_session: Dict[str, str]
    if isinstance(texts, dict):
        actual_texts_dict_for_session = texts
    elif isinstance(texts, Tuple): 
        # Dieser Fall sollte durch die Korrektur in gui.py nicht mehr auftreten, aber als Sicherheit:
        st.warning(f"ADMIN_PANEL WARNUNG: Der 'texts'-Parameter wurde als Tupel übergeben. Dies sollte in gui.py korrigiert werden. Versuche Konvertierung.")
        try:
            actual_texts_dict_for_session = dict(texts) 
            if not actual_texts_dict_for_session and texts: 
                 st.warning("ADMIN_PANEL WARNUNG: Konnte Tupel 'texts' nicht sinnvoll in Dict umwandeln. Verwende leeres Text-Dict.")
                 actual_texts_dict_for_session = {}
        except (TypeError, ValueError):
            st.error(f"ADMIN_PANEL FEHLER: Konnte Tupel 'texts' nicht in Dict umwandeln. Verwende leeres Text-Dict.")
            actual_texts_dict_for_session = {} 
    else:
        st.error(f"ADMIN_PANEL FEHLER: 'texts'-Parameter ist weder Dict noch Tuple (Typ: {type(texts)}). Verwende leeres Text-Dict.")
        actual_texts_dict_for_session = {}
    st.session_state['_admin_panel_texts'] = actual_texts_dict_for_session
    
    st.header(get_text_local("menu_item_admin", "Administration (F)"))
    
    admin_tab_keys_definition = ADMIN_TAB_KEYS_DEFINITION_GLOBAL 
    admin_tab_labels_definition = [get_text_local(key, key.replace("admin_tab_","").replace("_"," ").title()) for key in admin_tab_keys_definition]

    if not any(admin_tab_labels_definition) and admin_tab_keys_definition:
        st.warning("Admin-Tab-Beschriftungen konnten nicht geladen werden. Verwende Fallback-Namen.")
        admin_tab_labels_definition = [key.replace("admin_tab_", "").replace("_", " ").title() for key in admin_tab_keys_definition]
    
    if not admin_tab_labels_definition: 
        st.error("FEHLER: Keine Admin-Tabs zum Anzeigen vorhanden. ADMIN_TAB_KEYS_DEFINITION_GLOBAL oder Textdefinitionen prüfen.")
        return

    admin_tabs_rendered_ui = st.tabs(admin_tab_labels_definition)
    
    tab_functions_map = { 
        "admin_tab_company_management_new": lambda: render_company_crud_tab(db_list_companies_func, db_add_company_func, db_get_company_by_id_func, db_update_company_func, db_delete_company_func, db_set_default_company_func, load_admin_setting_func, save_admin_setting_func, db_add_company_document_func, db_list_company_documents_func, db_delete_company_document_func),
        "admin_tab_product_management": lambda: render_product_management(list_products_func, add_product_func, update_product_func, delete_product_func, get_product_by_id_func, list_product_categories_func, get_product_by_model_name_func),
        "admin_tab_general_settings": lambda: render_general_settings_extended(load_admin_setting_func, save_admin_setting_func),
        "admin_tab_price_matrix": lambda: render_price_matrix(load_admin_setting_func, save_admin_setting_func, _parse_price_matrix_csv_safe, _parse_price_matrix_excel_func),
        "admin_tab_tariff_management": lambda: render_tariff_management(load_admin_setting_func, save_admin_setting_func),
        "admin_tab_pdf_design": lambda: render_pdf_design_settings(load_admin_setting_func, save_admin_setting_func),
        "admin_tab_pdf_title_images": lambda: manage_templates_local("pdf_title_image", "pdf_title_image_templates", "admin_template_name_label_image", is_image_template=True),
        "admin_tab_pdf_offer_titles": lambda: manage_templates_local("pdf_offer_title", "pdf_offer_title_templates", "admin_template_name_label_text", item_content_label_key="admin_template_content_label_title"),
        "admin_tab_pdf_cover_letters": lambda: manage_templates_local("pdf_cover_letter", "pdf_cover_letter_templates", "admin_template_name_label_text", item_content_label_key="admin_template_content_label_cover_letter"),
        "admin_tab_visualization_settings": lambda: render_visualization_settings(load_admin_setting_func, save_admin_setting_func),
        "admin_tab_advanced": lambda: render_advanced_settings(load_admin_setting_func, save_admin_setting_func),
    }

    for i, tab_key_loop in enumerate(admin_tab_keys_definition): 
        if i < len(admin_tabs_rendered_ui) and i < len(admin_tab_labels_definition): 
            with admin_tabs_rendered_ui[i]: 
                if tab_key_loop in tab_functions_map:
                    render_func = tab_functions_map[tab_key_loop]
                    if callable(render_func):
                        try: render_func() 
                        except Exception as e_tab_render_loop: 
                            st.error(f"Fehler beim Rendern des Tabs '{admin_tab_labels_definition[i]}': {e_tab_render_loop}")
                            st.text(traceback.format_exc())
                    else: st.warning(f"Render-Funktion für Tab '{admin_tab_labels_definition[i]}' ist nicht aufrufbar.")
                else: st.warning(f"Tab-Funktion für '{admin_tab_labels_definition[i]}' nicht implementiert.")
        elif i < len(admin_tab_labels_definition): # Fallback, falls admin_tabs_rendered_ui kürzer ist
             st.error(f"Fehler: Konnte Tab-Container für '{admin_tab_labels_definition[i]}' nicht erstellen.")
        else: # Sollte nicht passieren, wenn Längenprüfungen oben greifen
             st.error(f"Fehler: Inkonsistenz in Tab-Definitionen bei Index {i}.")


# Änderungshistorie
# ... (vorherige Einträge) ...
# 2025-06-03, Gemini Ultra: `render_admin_panel` stellt sicher, dass `st.session_state['_admin_panel_texts']`
#                           immer ein Dictionary ist. Alle Tab-Render-Funktionen wurden angepasst, um
#                           keinen `texts`-Parameter mehr zu erwarten und stattdessen `get_text_local` zu verwenden.
#                           Lambdas in `tab_functions_map` übergeben `texts` nicht mehr.
#                           Widget-Keys auf _v15_final/_v16_admin_definitiv aktualisiert.
#                           Fehlerbehandlung bei CSV-Dekodierung in render_price_matrix verbessert.
#                           Text-Keys in render_product_management für Konsistenz mit get_text_local angepasst.
#                           Robustere Zuweisung von _parse_price_matrix_excel_func.
#                           Sicherheitsabfrage für Index in Tab-Loop.
# 2025-06-04, Gemini Ultra: Variable `WIDGET_KEY_SUFFIX` global am Anfang des Moduls definiert, um NameError zu beheben.
#                           Die Render-Funktionen in `tab_functions_map` wurden so angepasst, dass sie nun den `texts`-Parameter nicht mehr explizit übergeben,
#                           da die jeweiligen Unterfunktionen `get_text_local` verwenden, welches auf `st.session_state['_admin_panel_texts']` zugreift.
#                           Die Funktion `parse_module_price_matrix_excel` wurde als lokale Funktion belassen, da sie spezifisch für das Admin-Panel sein könnte.
#                           Die Zuweisung von `_parse_price_matrix_excel_func` in `render_admin_panel` wurde beibehalten, um die Übergabe einer externen Funktion zu ermöglichen.
#                           In `render_company_crud_tab`, `render_product_management` etc. wird `get_text_local` verwendet.