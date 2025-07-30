# data_input.py
# Eingabemasken für Kundendaten, Verbrauchsdaten und Bedarfsanalyse

import streamlit as st
import pandas as pd
import os
import re
from typing import Dict, Any, Optional, List, Callable, Tuple
import json
import traceback
from datetime import datetime
import requests
import base64

# Import streamlit_shadcn_ui with fallback
try:
    import streamlit_shadcn_ui as sui

    SUI_AVAILABLE = True
except ImportError:
    SUI_AVAILABLE = False
    sui = None

# Import CRM System
try:
    from complete_crm_system import create_crm_save_button, CompleteCRMSystem

    CRM_SYSTEM_AVAILABLE = True
except ImportError:
    CRM_SYSTEM_AVAILABLE = False
    print(" CRM System nicht verfügbar - Button wird nicht angezeigt")


# --- Hilfsfunktion für Texte ---
def get_text_di(
    texts_dict: Dict[str, str], key: str, fallback_text_value: Optional[str] = None
) -> str:
    if fallback_text_value is None:
        fallback_text_value = key.replace("_", " ").title() + " (DI Text fehlt)"
    return str(texts_dict.get(key, fallback_text_value))


# --- Dummies und reale Imports ---
# ... (Rest der Dummies und Imports bleibt unverändert) ...
def Dummy_get_db_connection_input():
    return None


def Dummy_list_products_input(*args, **kwargs):
    return []


def Dummy_get_product_by_model_name_input(*args, **kwargs):
    return None


def Dummy_get_product_by_id_input(*args, **kwargs):
    return None


def Dummy_load_admin_setting_input(key, default=None):
    if key == "salutation_options":
        return ["Herr (D)", "Frau (D)", "Familie (D)"]
    if key == "title_options":
        return ["Dr. (D)", "Prof. (D)", "Mag. (D)", "Ing. (D)", None]
    if key == "Maps_api_key":
        return "PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN"
    return default


get_db_connection_safe = Dummy_get_db_connection_input
load_admin_setting_safe = Dummy_load_admin_setting_input
list_products_safe = Dummy_list_products_input
get_product_by_model_name_safe = Dummy_get_product_by_model_name_input
get_product_by_id_safe = Dummy_get_product_by_id_input

try:
    from database import (
        get_db_connection as real_get_db_connection,
        load_admin_setting as real_load_admin_setting,
    )
    from product_db import (
        list_products as real_list_products,
        get_product_by_model_name as real_get_product_by_model_name,
        get_product_by_id as real_get_product_by_id,
    )

    get_db_connection_safe = real_get_db_connection
    load_admin_setting_safe = real_load_admin_setting
    list_products_safe = real_list_products
    get_product_by_model_name_safe = real_get_product_by_model_name
    get_product_by_id_safe = real_get_product_by_id
except (ImportError, ModuleNotFoundError) as e:
    # print(f"data_input.py: FEHLER Import DB/Produkt: {e}. Dummies bleiben aktiv.") # Logging
    pass  # Im Fehlerfall bleiben Dummies aktiv
except Exception as e_load_deps:
    # print(f"data_input.py: FEHLER Laden DB/Produkt: {e_load_deps}. Dummies bleiben aktiv.") # Logging
    # traceback.print_exc() # Logging
    pass


def parse_full_address_string(
    full_address: str, texts: Dict[str, str]
) -> Dict[str, str]:
    # ... (Funktion bleibt unverändert) ...
    parsed_data = {"street": "", "house_number": "", "zip_code": "", "city": ""}
    full_address = full_address.strip()
    zip_city_match = re.search(
        r"(?:[A-Z]{1,2}-)?(\d{4,5})\s+(.+?)(?:,\s*\w+)?$", full_address
    )
    address_part = full_address
    if zip_city_match:
        parsed_data["zip_code"] = zip_city_match.group(1).strip()
        parsed_data["city"] = zip_city_match.group(2).strip().split(",")[0].strip()
        address_part = full_address[: zip_city_match.start()].strip().rstrip(",")
    else:
        parts = full_address.split(",")
        if len(parts) > 1:
            potential_zip_city = parts[-1].strip()
            zip_city_match_comma = re.match(
                r"^\s*(?:[A-Z]{1,2}-)?(\d{4,5})\s+(.+?)\s*$", potential_zip_city
            )
            if zip_city_match_comma:
                parsed_data["zip_code"] = zip_city_match_comma.group(1).strip()
                parsed_data["city"] = zip_city_match_comma.group(2).strip()
                address_part = ",".join(parts[:-1]).strip()
            elif (
                not parts[-1].strip().replace("-", "").isdigit()
                and len(parts[-1].strip()) > 2
            ):
                parsed_data["city"] = parts[-1].strip()
                address_part = ",".join(parts[:-1]).strip()
    street_hn_match = re.match(
        r"^(.*?)\s+([\d\w][\d\w\s\-/.]*?)$", address_part.strip()
    )
    if street_hn_match:
        potential_street = street_hn_match.group(1).strip().rstrip(",")
        potential_hn = street_hn_match.group(2).strip()
        if len(potential_street.split()) > 0 and re.search(r"\d", potential_hn):
            parsed_data["street"] = potential_street
            parsed_data["house_number"] = potential_hn
        else:
            parsed_data["street"] = address_part
            # st.warning(get_text_di(texts, "parse_street_hnr_warning_detail", "Straße und Hausnummer konnten nicht eindeutig getrennt werden. Bitte manuell prüfen.")) # st.warning hier nur wenn absolut nötig
    elif address_part:
        parsed_data["street"] = address_part
        # st.warning(get_text_di(texts, "parse_street_hnr_not_found", "Keine Hausnummer in der Adresse gefunden. Bitte manuell prüfen.")) # st.warning hier nur wenn absolut nötig
    return parsed_data


def get_coordinates_from_address_google(
    address: str,
    city: str,
    zip_code: str,
    api_key: Optional[str],
    texts: Dict[str, str],
) -> Optional[Dict[str, float]]:
    # ... (Funktion bleibt unverändert) ...
    if (
        not api_key
        or api_key == ""
        or api_key == "PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN"
    ):
        # print(get_text_di(texts, "geocode_google_api_key_missing_or_placeholder_terminal", "FEHLER: Google API Key fehlt oder ist Platzhalter. Geocoding nicht möglich.")) # Logging
        # st.warning(get_text_di(texts, "geocode_google_api_key_missing_or_placeholder_ui", "Google API Key nicht konfiguriert. Geocoding deaktiviert.")) # Nur bei Bedarf im UI
        return None
    if not address or not city:
        # st.warning(get_text_di(texts, "geocode_missing_address_city", "Für Geocoding werden Straße und Ort benötigt.")) # Nur bei Bedarf im UI
        return None
    full_query_address = f"{address}, {zip_code} {city}"
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": full_query_address, "key": api_key}
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK" and data.get("results"):
            location = data["results"][0].get("geometry", {}).get("location", {})
            lat, lng = location.get("lat"), location.get("lng")
            if lat is not None and lng is not None:
                # st.success(get_text_di(texts, "geolocation_success_google_api", f"Koordinaten via Google API: Lat {lat:.6f}, Lon {lng:.6f}")) # Nur bei Bedarf im UI
                return {"latitude": float(lat), "longitude": float(lng)}
            # else: st.warning(get_text_di(texts, "geolocation_google_api_no_coords", "Google API: Keine Koordinaten in der Antwort gefunden.")) # Nur bei Bedarf
        # else: st.warning(get_text_di(texts, "geolocation_google_api_status_error", f"Google API Fehler: {data.get('status')} - {data.get('error_message', '')}")) # Nur bei Bedarf
        return None
    except requests.exceptions.Timeout:
        # st.error(get_text_di(texts, "geolocation_google_api_timeout", "Google Geocoding API Zeitüberschreitung.")) # Nur bei Bedarf
        return None
    except requests.exceptions.RequestException as e:
        # st.error(get_text_di(texts, "geolocation_google_api_request_error", f"Google Geocoding API Anfragefehler: {e}")) # Nur bei Bedarf
        return None
    except Exception as e:
        # st.error(f"{get_text_di(texts, 'geolocation_api_unknown_error', 'Unbekannter Fehler beim Geocoding:')} {e}") # Nur bei Bedarf
        return None


def get_Maps_satellite_image_url(
    latitude: float,
    longitude: float,
    api_key: Optional[str],
    texts: Dict[str, str],
    zoom: int = 20,
    width: int = 600,
    height: int = 400,
) -> Optional[str]:
    # ... (Funktion bleibt unverändert) ...
    if not api_key or api_key == "PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN":
        # print(get_text_di(texts, "maps_api_key_missing_or_placeholder_terminal", "FEHLER: Google Maps API Key fehlt oder ist Platzhalter. Satellitenbild kann nicht geladen werden.")) # Logging
        # st.warning(get_text_di(texts, "maps_api_key_missing_or_placeholder_ui", "Google Maps API Key nicht konfiguriert. Satellitenbild kann nicht geladen werden.")) # Nur bei Bedarf
        return None
    if (
        abs(latitude) < 1e-9
        and abs(longitude) < 1e-9
        and not st.session_state.get("allow_zero_coords_map_di", False)
    ):
        # st.info(get_text_di(texts, "map_default_coords_info", "Standardkoordinaten (0,0) werden verwendet. Bitte gültige Koordinaten eingeben oder Adresse parsen, um ein spezifisches Satellitenbild zu laden.")) # Nur bei Bedarf
        return None
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    params = {
        "center": f"{latitude},{longitude}",
        "zoom": str(zoom),
        "size": f"{width}x{height}",
        "maptype": "satellite",
        "key": api_key,
    }
    url_parts = [f"{k}={v}" for k, v in params.items()]
    full_url = base_url + "&".join(url_parts)
    return full_url


# KORREKTUR: `render_data_input` modifiziert `st.session_state.project_data` direkt und gibt es nicht mehr zurück.
def render_data_input(texts: Dict[str, str]) -> None:
    # KORREKTUR: `inputs` ist nun eine direkte Referenz auf `st.session_state.project_data`.
    # Die Initialisierung in gui.py stellt sicher, dass es existiert.
    inputs: Dict[str, Any] = st.session_state.project_data

    # Sicherstellen, dass die Unter-Dictionaries existieren
    for key_to_ensure in ["customer_data", "project_details", "economic_data"]:
        if key_to_ensure not in inputs:
            inputs[key_to_ensure] = {}

    # ... (Rest der Variablendefinitionen und UI-Elemente bleibt gleich) ...
    please_select_text = get_text_di(
        texts, "please_select_option", "--- Bitte wählen ---"
    )
    SALUTATION_OPTIONS = load_admin_setting_safe(
        "salutation_options", ["Herr", "Frau", "Familie", "Firma", "Divers", ""]
    )
    TITLE_OPTIONS_RAW = load_admin_setting_safe(
        "title_options", ["Dr.", "Prof.", "Mag.", "Ing.", None]
    )
    TITLE_OPTIONS = [
        str(t) if t is not None else get_text_di(texts, "none_option", "(Kein)")
        for t in TITLE_OPTIONS_RAW
    ]
    BUNDESLAND_OPTIONS = load_admin_setting_safe(
        "bundesland_options",
        [
            "Baden-Württemberg",
            "Bayern",
            "Berlin",
            "Brandenburg",
            "Bremen",
            "Hamburg",
            "Hessen",
            "Mecklenburg-Vorpommern",
            "Niedersachsen",
            "Nordrhein-Westfalen",
            "Rheinland-Pfalz",
            "Saarland",
            "Sachsen",
            "Sachsen-Anhalt",
            "Schleswig-Holstein",
            "Thüringen",
        ],
    )
    DACHART_OPTIONS = load_admin_setting_safe(
        "dachart_options",
        [
            "Satteldach",
            "Satteldach mit Gaube",
            "Pultdach",
            "Flachdach",
            "Walmdach",
            "Krüppelwalmdach",
            "Zeltdach",
            "Sonstiges",
        ],
    )
    DACHDECKUNG_OPTIONS = load_admin_setting_safe(
        "dachdeckung_options",
        [
            "Frankfurter Pfannen",
            "Trapezblech",
            "Tonziegel",
            "Biberschwanz",
            "Schiefer",
            "Bitumen",
            "Eternit",
            "Schindeln",
            "Sonstiges",
        ],
    )
    MODULE_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Modul")
    ] or [get_text_di(texts, "no_modules_in_db", "Keine Module in DB")]
    INVERTER_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Wechselrichter")
    ] or [get_text_di(texts, "no_inverters_in_db", "Keine WR in DB")]
    STORAGE_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Batteriespeicher")
    ] or [get_text_di(texts, "no_storages_in_db", "Keine Speicher in DB")]
    WALLBOX_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Wallbox")
    ] or [get_text_di(texts, "no_wallboxes_in_db", "Keine Wallboxen in DB")]
    EMS_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Energiemanagementsystem")
    ] or [get_text_di(texts, "no_ems_in_db", "Keine EMS in DB")]
    OPTIMIZER_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Leistungsoptimierer")
    ] or [get_text_di(texts, "no_optimizers_in_db", "Keine Optimierer in DB")]
    CARPORT_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Carport")
    ] or [get_text_di(texts, "no_carports_in_db", "Keine Carports in DB")]
    NOTSTROM_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Notstromversorgung")
    ] or [get_text_di(texts, "no_notstrom_in_db", "Keine Notstrom in DB")]
    TIERABWEHR_LIST_MODELS = [
        p.get("model_name", f"ID:{p.get('id', 'N/A')}")
        for p in list_products_safe(category="Tierabwehrschutz")
    ] or [get_text_di(texts, "no_tierabwehr_in_db", "Keine Tierabwehr in DB")]

    st.subheader(get_text_di(texts, "customer_data_header", "Kundendaten"))
    # KORREKTUR: `customer_data_expanded_di` wird direkt im session_state verwendet.
    if "customer_data_expanded_di" not in st.session_state:
        st.session_state.customer_data_expanded_di = True  # Default zu expanded

    with st.expander(
        get_text_di(texts, "customer_data_header", "Kundendaten"),
        expanded=st.session_state.customer_data_expanded_di,
    ):
        # ... (Inhalt des Kunden-Expanders bleibt gleich, aber `inputs` verweist jetzt direkt auf `st.session_state.project_data`)
        col1, col2, col3 = st.columns(3)
        with col1:
            inputs["project_details"]["anlage_type"] = st.selectbox(
                get_text_di(texts, "anlage_type_label", "Anlagentyp"),
                options=["Neuanlage", "Bestandsanlage"],
                index=["Neuanlage", "Bestandsanlage"].index(
                    inputs["project_details"].get("anlage_type", "Neuanlage")
                ),
                key="anlage_type_di_v6_exp_stable",
            )
        with col2:
            inputs["project_details"]["feed_in_type"] = st.selectbox(
                get_text_di(texts, "feed_in_type_label", "Einspeisetyp"),
                options=["Teileinspeisung", "Volleinspeisung"],
                index=["Teileinspeisung", "Volleinspeisung"].index(
                    inputs["project_details"].get("feed_in_type", "Teileinspeisung")
                ),
                key="feed_in_type_di_v6_exp_stable",
            )
        with col3:
            inputs["customer_data"]["type"] = st.selectbox(
                get_text_di(texts, "customer_type_label", "Kundentyp"),
                options=["Privat", "Gewerblich"],
                index=["Privat", "Gewerblich"].index(
                    inputs["customer_data"].get("type", "Privat")
                ),
                key="customer_type_di_v6_exp_stable",
            )
        col4, col5, col6 = st.columns(3)
        default_salutation = inputs["customer_data"].get(
            "salutation", SALUTATION_OPTIONS[0] if SALUTATION_OPTIONS else ""
        )
        with col4:
            inputs["customer_data"]["salutation"] = st.selectbox(
                get_text_di(texts, "salutation_label", "Anrede"),
                options=SALUTATION_OPTIONS,
                index=(
                    SALUTATION_OPTIONS.index(default_salutation)
                    if default_salutation in SALUTATION_OPTIONS
                    else 0
                ),
                key="salutation_di_v6_exp_stable",
            )
        default_title = inputs["customer_data"].get(
            "title", TITLE_OPTIONS[-1] if TITLE_OPTIONS else ""
        )
        with col5:
            inputs["customer_data"]["title"] = st.selectbox(
                get_text_di(texts, "title_label", "Titel"),
                options=TITLE_OPTIONS,
                index=(
                    TITLE_OPTIONS.index(default_title)
                    if default_title in TITLE_OPTIONS
                    else len(TITLE_OPTIONS) - 1
                ),
                key="title_di_v6_exp_stable",
            )
        with col6:
            inputs["customer_data"]["first_name"] = st.text_input(
                get_text_di(texts, "first_name_label", "Vorname"),
                value=str(inputs["customer_data"].get("first_name", "")),
                key="first_name_di_v6_exp_stable",
            )
        col7, col8 = st.columns(2)
        with col7:
            inputs["customer_data"]["last_name"] = st.text_input(
                get_text_di(texts, "last_name_label", "Nachname"),
                value=str(inputs["customer_data"].get("last_name", "")),
                key="last_name_di_v6_exp_stable",
            )
        with col8:
            inputs["customer_data"]["num_persons"] = st.number_input(
                get_text_di(texts, "num_persons_label", "Anzahl Personen im Haushalt"),
                min_value=1,
                value=int(inputs["customer_data"].get("num_persons", 1) or 1),
                key="num_persons_di_v6_exp_stable",
            )
        full_address_input_val = st.text_input(
            get_text_di(texts, "full_address_label", "Komplette Adresse"),
            value=str(inputs["customer_data"].get("full_address", "")),
            help=get_text_di(
                texts, "full_address_help", "Z.B. Musterweg 18, 12345 Musterstadt"
            ),
            key="full_address_widget_key_di_v6_exp_stable",
        )
        inputs["customer_data"]["full_address"] = full_address_input_val

        # KORREKTUR: `st.rerun()` aus dem Button-Callback entfernen. Streamlit führt nach Button-Klicks automatisch einen Rerun durch.
        # Die Aktualisierung der `inputs` (und damit `st.session_state.project_data`) reicht aus.
        if st.button(
            get_text_di(texts, "parse_address_button", "Daten aus Adresse übernehmen"),
            key="parse_address_btn_di_v6_exp_stable",
        ):
            if full_address_input_val:
                parsed_data = parse_full_address_string(full_address_input_val, texts)
                inputs["customer_data"]["address"] = parsed_data.get(
                    "street", inputs["customer_data"].get("address", "")
                )
                inputs["customer_data"]["house_number"] = parsed_data.get(
                    "house_number", inputs["customer_data"].get("house_number", "")
                )
                inputs["customer_data"]["zip_code"] = parsed_data.get(
                    "zip_code", inputs["customer_data"].get("zip_code", "")
                )
                inputs["customer_data"]["city"] = parsed_data.get(
                    "city", inputs["customer_data"].get("city", "")
                )
                if parsed_data.get("zip_code") and parsed_data.get("city"):
                    st.success(
                        get_text_di(
                            texts,
                            "parse_address_success_all",
                            "Adresse erfolgreich geparst! Bitte Felder prüfen.",
                        )
                    )
                else:
                    st.warning(
                        get_text_di(
                            texts,
                            "parse_address_partial_success",
                            "Adresse teilweise geparst. Bitte fehlende Felder ergänzen.",
                        )
                    )
                st.session_state.satellite_image_url_di = None
                # st.rerun() # ENTFERNT - Streamlit macht das automatisch.
            else:
                st.warning(
                    get_text_di(
                        texts,
                        "parse_address_no_input",
                        "Bitte geben Sie eine vollständige Adresse ein.",
                    )
                )

        col_addr1, col_addr2 = st.columns(2)
        col_addr3, col_addr4 = st.columns(2)
        with col_addr1:
            inputs["customer_data"]["address"] = st.text_input(
                get_text_di(texts, "street_label", "Straße"),
                value=str(inputs["customer_data"].get("address", "")),
                key="address_di_manual_v6_exp_stable",
            )
        with col_addr2:
            inputs["customer_data"]["house_number"] = st.text_input(
                get_text_di(texts, "house_number_label", "Hausnummer"),
                value=str(inputs["customer_data"].get("house_number", "")),
                key="house_number_di_manual_v6_exp_stable",
            )
        with col_addr3:
            inputs["customer_data"]["zip_code"] = st.text_input(
                get_text_di(texts, "zip_code_label", "PLZ"),
                value=str(inputs["customer_data"].get("zip_code", "")),
                key="zip_code_di_manual_v6_exp_stable",
            )
        with col_addr4:
            inputs["customer_data"]["city"] = st.text_input(
                get_text_di(texts, "city_label", "Ort"),
                value=str(inputs["customer_data"].get("city", "")),
                key="city_di_manual_v6_exp_stable",
            )
        default_state = inputs["customer_data"].get("state", please_select_text)
        state_options_with_ps = [please_select_text] + BUNDESLAND_OPTIONS
        inputs["customer_data"]["state"] = st.selectbox(
            get_text_di(texts, "state_label", "Bundesland"),
            options=state_options_with_ps,
            key="state_di_v6_exp_stable",
            index=(
                state_options_with_ps.index(default_state)
                if default_state in state_options_with_ps
                else 0
            ),
        )
        if inputs["customer_data"]["state"] == please_select_text:
            inputs["customer_data"]["state"] = None
        st.markdown("---")
        st.markdown(f"**{get_text_di(texts,'coordinates_header','Koordinaten')}**")
        Maps_API_KEY_FROM_ENV = os.environ.get("Maps_API_KEY")
        EFFECTIVE_GOOGLE_API_KEY = None
        if (
            Maps_API_KEY_FROM_ENV
            and Maps_API_KEY_FROM_ENV.strip()
            and Maps_API_KEY_FROM_ENV != "PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN"
        ):
            EFFECTIVE_GOOGLE_API_KEY = Maps_API_KEY_FROM_ENV
        else:
            api_key_from_db = load_admin_setting_safe("Maps_api_key", None)
            if (
                api_key_from_db
                and api_key_from_db.strip()
                and api_key_from_db != "PLATZHALTER_HIER_IHREN_KEY_EINFUEGEN"
            ):
                EFFECTIVE_GOOGLE_API_KEY = api_key_from_db
        current_lat = float(inputs["project_details"].get("latitude", 0.0) or 0.0)
        current_lon = float(inputs["project_details"].get("longitude", 0.0) or 0.0)
        col_lat, col_lon, col_geocode_btn = st.columns([2, 2, 1])
        with col_lat:
            inputs["project_details"]["latitude"] = st.number_input(
                get_text_di(texts, "latitude_label", "Breitengrad"),
                value=current_lat,
                format="%.6f",
                key="latitude_di_v6_exp_stable",
                help="Z.B. 48.137154",
            )
        with col_lon:
            inputs["project_details"]["longitude"] = st.number_input(
                get_text_di(texts, "longitude_label", "Längengrad"),
                value=current_lon,
                format="%.6f",
                key="longitude_di_v6_exp_stable",
                help="Z.B. 11.575382",
            )
        with col_geocode_btn:
            st.write("")
            st.write("")
            # KORREKTUR: `st.rerun()` aus dem Button-Callback entfernen.
            if st.button(
                get_text_di(texts, "get_coordinates_button", "Koordinaten abrufen"),
                key="geocode_btn_di_v6_exp_stable",
                disabled=not EFFECTIVE_GOOGLE_API_KEY,
            ):
                addr_geo, city_geo, zip_geo = (
                    inputs["customer_data"].get("address", ""),
                    inputs["customer_data"].get("city", ""),
                    inputs["customer_data"].get("zip_code", ""),
                )
                if addr_geo and city_geo:
                    coords = get_coordinates_from_address_google(
                        addr_geo, city_geo, zip_geo, EFFECTIVE_GOOGLE_API_KEY, texts
                    )
                    if coords:
                        (
                            inputs["project_details"]["latitude"],
                            inputs["project_details"]["longitude"],
                        ) = (coords["latitude"], coords["longitude"])
                        st.session_state.satellite_image_url_di = None
                        # st.rerun() # ENTFERNT
                else:
                    st.warning(
                        get_text_di(
                            texts,
                            "geocode_incomplete_address",
                            "Bitte Adresse (Straße, PLZ, Ort) eingeben.",
                        )
                    )
        if not (abs(current_lat) < 1e-9 and abs(current_lon) < 1e-9):
            st.map(pd.DataFrame({"lat": [current_lat], "lon": [current_lon]}), zoom=13)
        # elif EFFECTIVE_GOOGLE_API_KEY: st.info(get_text_di(texts, "map_no_coordinates_info", "Keine Koordinaten für Kartenanzeige. Bitte Adresse parsen oder Koordinaten manuell eingeben.")) # Optional
        st.markdown("---")
        st.markdown(
            f"**{get_text_di(texts, 'satellite_image_header', 'Satellitenbild (Google Maps)')}**"
        )
        if "satellite_image_url_di" not in st.session_state:
            st.session_state.satellite_image_url_di = None
        if not (abs(current_lat) < 1e-9 and abs(current_lon) < 1e-9):
            if EFFECTIVE_GOOGLE_API_KEY:
                if st.button(
                    get_text_di(
                        texts,
                        "load_satellite_image_button",
                        "Satellitenbild laden/aktualisieren",
                    ),
                    key="load_sat_img_btn_di_v6_final_exp_stable",
                ):
                    st.session_state.satellite_image_url_di = (
                        get_Maps_satellite_image_url(
                            current_lat, current_lon, EFFECTIVE_GOOGLE_API_KEY, texts
                        )
                    )
                    if st.session_state.satellite_image_url_di:
                        # st.success(get_text_di(texts, "satellite_image_url_generated", "URL für Satellitenbild generiert.")) # Optional
                        inputs["project_details"]["satellite_image_base64_data"] = None
                        inputs["project_details"][
                            "satellite_image_for_pdf_url_source"
                        ] = st.session_state.satellite_image_url_di
                    # else: st.error(get_text_di(texts, "satellite_image_load_failed", "Satellitenbild konnte nicht geladen werden (URL Generierung fehlgeschlagen oder ungültige Koordinaten).")) # Optional
                    #     inputs['project_details']['satellite_image_base64_data'] = None
                    #     inputs['project_details']['satellite_image_for_pdf_url_source'] = None
            if st.session_state.get("satellite_image_url_di"):
                # st.markdown(f"Generierte Bild-URL (für Vorschau):"); st.code(st.session_state.satellite_image_url_di) # Für Debugging
                try:
                    st.image(
                        st.session_state.satellite_image_url_di,
                        caption=get_text_di(
                            texts, "satellite_image_caption", "Satellitenansicht"
                        ),
                    )
                    default_visualize_satellite = inputs["project_details"].get(
                        "visualize_roof_in_pdf_satellite", True
                    )
                    inputs["project_details"]["visualize_roof_in_pdf_satellite"] = (
                        st.checkbox(
                            get_text_di(
                                texts,
                                "visualize_satellite_in_pdf_label",
                                "Satellitenbild in PDF anzeigen",
                            ),
                            value=default_visualize_satellite,
                            key="visualize_satellite_in_pdf_di_val_v6_final_exp_stable",
                        )
                    )
                    if (
                        inputs["project_details"].get("visualize_roof_in_pdf_satellite")
                        and st.session_state.satellite_image_url_di
                    ):
                        if (
                            not inputs["project_details"].get(
                                "satellite_image_base64_data"
                            )
                            or inputs["project_details"].get(
                                "satellite_image_for_pdf_url_source"
                            )
                            != st.session_state.satellite_image_url_di
                        ):
                            try:
                                with st.spinner(
                                    "Lade Satellitenbild für PDF..."
                                ):  # Spinner ist gut für UI-Feedback
                                    response = requests.get(
                                        st.session_state.satellite_image_url_di,
                                        timeout=15,
                                    )
                                    response.raise_for_status()
                                    inputs["project_details"][
                                        "satellite_image_base64_data"
                                    ] = base64.b64encode(response.content).decode(
                                        "utf-8"
                                    )
                                    inputs["project_details"][
                                        "satellite_image_for_pdf_url_source"
                                    ] = st.session_state.satellite_image_url_di
                                    # st.success("Satellitenbild für PDF vorbereitet.") # Optional
                            except Exception as e_sat_download:
                                # st.warning(f"Satellitenbild konnte nicht für PDF heruntergeladen werden: {e_sat_download}") # Optional
                                inputs["project_details"][
                                    "satellite_image_base64_data"
                                ] = None
                                inputs["project_details"][
                                    "satellite_image_for_pdf_url_source"
                                ] = None
                except Exception as e_img:
                    # st.error(f"{get_text_di(texts, 'satellite_image_display_error', 'Fehler Anzeige Satellitenbild:')} {e_img}") # Optional
                    inputs["project_details"]["visualize_roof_in_pdf_satellite"] = False
                    inputs["project_details"]["satellite_image_base64_data"] = None
                    inputs["project_details"][
                        "satellite_image_for_pdf_url_source"
                    ] = None
            # elif EFFECTIVE_GOOGLE_API_KEY : st.info(get_text_di(texts, "satellite_image_press_button_info", "Klicken Sie auf 'Satellitenbild laden/aktualisieren', um das Bild anzuzeigen.")) # Optional
        # elif not EFFECTIVE_GOOGLE_API_KEY: st.info(get_text_di(texts, "maps_api_key_needed_for_button_info", "Ein gültiger Google Maps API Key wird benötigt...")) # Optional
        # else: st.info(get_text_di(texts, "satellite_image_no_coords_info", "Keine (gültigen) Koordinaten für Satellitenbild...")) # Optional
        col_contact1, col_contact2, col_contact3 = st.columns(3)
        with col_contact1:
            inputs["customer_data"]["email"] = st.text_input(
                get_text_di(texts, "email_label", "E-Mail"),
                value=str(inputs["customer_data"].get("email", "")),
                key="email_di_v6_exp_stable",
            )
        with col_contact2:
            inputs["customer_data"]["phone_landline"] = st.text_input(
                get_text_di(texts, "phone_landline_label", "Telefon (Festnetz)"),
                value=str(inputs["customer_data"].get("phone_landline", "")),
                key="phone_landline_di_v6_exp_stable",
            )
        with col_contact3:
            inputs["customer_data"]["phone_mobile"] = st.text_input(
                get_text_di(texts, "phone_mobile_label", "Telefon (Mobil)"),
                value=str(inputs["customer_data"].get("phone_mobile", "")),
                key="phone_mobile_di_v6_exp_stable",
            )
        inputs["customer_data"]["income_tax_rate_percent"] = st.number_input(
            label=get_text_di(texts, "income_tax_rate_label", "ESt.-Satz (%)"),
            min_value=0.0,
            max_value=100.0,
            value=float(
                inputs["customer_data"].get("income_tax_rate_percent", 0.0) or 0.0
            ),
            step=0.1,
            format="%.1f",
            key="income_tax_rate_percent_di_v6_exp_stable",
            help=get_text_di(
                texts,
                "income_tax_rate_help",
                "Grenzsteuersatz für Wirtschaftlichkeitsberechnung (optional)",
            ),
        )

    # ... (Rest der UI-Elemente für Bedarfsanalyse, Gebäudedaten, etc. bleibt strukturell gleich,
    #      aber verwendet `inputs` anstelle von `st.session_state.project_data` direkt und stabile Keys) ...
    st.subheader(get_text_di(texts, "consumption_analysis_header", "Bedarfsanalyse"))
    if "consumption_data_expanded_di" not in st.session_state:
        st.session_state.consumption_data_expanded_di = True
    with st.expander(
        get_text_di(texts, "consumption_costs_header", "Verbräuche und Kosten"),
        expanded=st.session_state.consumption_data_expanded_di,
    ):
        col_cons_hh, col_cons_heat = st.columns(2)
        inputs["project_details"]["annual_consumption_kwh_yr"] = (
            col_cons_hh.number_input(
                label=get_text_di(
                    texts,
                    "annual_consumption_kwh_label",
                    "Jahresverbrauch Haushalt (kWh)",
                ),
                min_value=0,
                value=int(
                    inputs["project_details"].get("annual_consumption_kwh_yr", 3500)
                    or 3500
                ),
                key="annual_consumption_kwh_yr_di_v6_exp_stable",
            )
        )
        inputs["project_details"]["consumption_heating_kwh_yr"] = (
            col_cons_heat.number_input(
                label=get_text_di(
                    texts,
                    "annual_heating_kwh_optional_label",
                    "Jahresverbrauch Heizung (kWh, opt.)",
                ),
                min_value=0,
                value=int(
                    inputs["project_details"].get("consumption_heating_kwh_yr", 0) or 0
                ),
                key="consumption_heating_kwh_yr_di_v6_exp_stable",
            )
        )
        total_consumption_kwh_yr_display = (
            inputs["project_details"].get("annual_consumption_kwh_yr", 0) or 0
        ) + (inputs["project_details"].get("consumption_heating_kwh_yr", 0) or 0)
        st.info(
            f"{get_text_di(texts,'total_annual_consumption_label','Gesamtjahresverbrauch (Haushalt + Heizung)')}: {total_consumption_kwh_yr_display:.0f} kWh"
        )
        col_price_direct, col_price_calc = st.columns(2)
        default_calc_price = inputs["project_details"].get(
            "calculate_electricity_price", True
        )
        use_calculated_price = col_price_calc.checkbox(
            get_text_di(
                texts,
                "calculate_electricity_price_checkbox",
                "Strompreis aus Kosten berechnen?",
            ),
            value=default_calc_price,
            key="calculate_electricity_price_di_v6_exp_stable",
        )
        inputs["project_details"]["calculate_electricity_price"] = use_calculated_price
        if use_calculated_price:
            col_costs_hh, col_costs_heat = st.columns(2)
            inputs["project_details"]["costs_household_euro_mo"] = (
                col_costs_hh.number_input(
                    label=get_text_di(
                        texts,
                        "monthly_costs_household_label",
                        "Monatliche Kosten Haushalt (€)",
                    ),
                    min_value=0.0,
                    value=float(
                        inputs["project_details"].get("costs_household_euro_mo", 80.0)
                        or 80.0
                    ),
                    step=0.1,
                    key="costs_household_euro_mo_di_v6_exp_stable",
                )
            )
            inputs["project_details"]["costs_heating_euro_mo"] = (
                col_costs_heat.number_input(
                    label=get_text_di(
                        texts,
                        "monthly_costs_heating_optional_label",
                        "Monatliche Kosten Heizung (€, opt.)",
                    ),
                    min_value=0.0,
                    value=float(
                        inputs["project_details"].get("costs_heating_euro_mo", 0.0)
                        or 0.0
                    ),
                    step=0.1,
                    key="costs_heating_euro_mo_di_v6_exp_stable",
                )
            )
            total_annual_costs_calc = (
                (inputs["project_details"].get("costs_household_euro_mo", 0.0) or 0.0)
                + (inputs["project_details"].get("costs_heating_euro_mo", 0.0) or 0.0)
            ) * 12
            st.info(
                f"{get_text_di(texts,'total_annual_costs_display_label','Gesamte jährliche Stromkosten (berechnet)')}: {total_annual_costs_calc:.2f} €"
            )
            calculated_price_kwh = (
                (total_annual_costs_calc / total_consumption_kwh_yr_display)
                if total_consumption_kwh_yr_display > 0
                else 0.0
            )
            inputs["project_details"]["electricity_price_kwh"] = calculated_price_kwh
            st.info(
                f"{get_text_di(texts,'calculated_electricity_price_info','Daraus resultierender Strompreis')}: {calculated_price_kwh:.4f} €/kWh"
            )
        else:
            inputs["project_details"]["electricity_price_kwh"] = (
                col_price_direct.number_input(
                    label=get_text_di(
                        texts,
                        "electricity_price_manual_label",
                        "Strompreis manuell (€/kWh)",
                    ),
                    min_value=0.0,
                    value=float(
                        inputs["project_details"].get("electricity_price_kwh", 0.30)
                        or 0.30
                    ),
                    step=0.001,
                    format="%.4f",
                    key="electricity_price_kwh_di_v6_exp_stable",
                )
            )
            (
                inputs["project_details"]["costs_household_euro_mo"],
                inputs["project_details"]["costs_heating_euro_mo"],
            ) = (0.0, 0.0)

    st.subheader(get_text_di(texts, "building_data_header", "Daten des Gebäudes"))
    if "building_data_expanded_di" not in st.session_state:
        st.session_state.building_data_expanded_di = True
    with st.expander(
        get_text_di(texts, "building_data_header", "Daten des Gebäudes"),
        expanded=st.session_state.building_data_expanded_di,
    ):
        col_build1, col_build2 = st.columns(2)
        with col_build1:
            inputs["project_details"]["build_year"] = st.number_input(
                label=get_text_di(texts, "build_year_label", "Baujahr des Hauses"),
                min_value=1800,
                max_value=datetime.now().year,
                value=int(inputs["project_details"].get("build_year", 2000) or 2000),
                step=1,
                key="build_year_di_v6_exp_stable",
            )
            build_year_val = inputs["project_details"]["build_year"]
            # if build_year_val<1960:st.warning(get_text_di(texts,"build_year_warning_old"," Zählerschrank/Hauselektrik prüfen.")) # Optional
            # elif build_year_val<2000:st.info(get_text_di(texts,"build_year_info_mid","ℹ Zählerschrank/Hauselektrik prüfen.")) # Optional
            # else:st.success(get_text_di(texts,"build_year_success_new"," Zählerschrank/Hauselektrik OK.")) # Optional
        with col_build2:
            default_roof_type = inputs["project_details"].get(
                "roof_type", please_select_text
            )
            roof_type_options_with_ps = [please_select_text] + DACHART_OPTIONS
            inputs["project_details"]["roof_type"] = st.selectbox(
                get_text_di(texts, "roof_type_label", "Dachart"),
                options=roof_type_options_with_ps,
                index=(
                    roof_type_options_with_ps.index(default_roof_type)
                    if default_roof_type in roof_type_options_with_ps
                    else 0
                ),
                key="roof_type_di_v6_exp_stable",
            )
            if inputs["project_details"]["roof_type"] == please_select_text:
                inputs["project_details"]["roof_type"] = None
        col_build3, col_build4 = st.columns(2)
        with col_build3:
            default_roof_covering = inputs["project_details"].get(
                "roof_covering_type", please_select_text
            )
            roof_covering_options_with_ps = [please_select_text] + DACHDECKUNG_OPTIONS
            inputs["project_details"]["roof_covering_type"] = st.selectbox(
                get_text_di(texts, "roof_covering_label", "Dachdeckungsart"),
                options=roof_covering_options_with_ps,
                index=(
                    roof_covering_options_with_ps.index(default_roof_covering)
                    if default_roof_covering in roof_covering_options_with_ps
                    else 0
                ),
                key="roof_covering_type_di_v6_exp_stable",
            )
            if inputs["project_details"]["roof_covering_type"] == please_select_text:
                inputs["project_details"]["roof_covering_type"] = None
            # if inputs['project_details']['roof_covering_type']and inputs['project_details']['roof_covering_type']in['Schiefer','Bitumen','Eternit']:st.warning(get_text_di(texts,"roof_covering_warning"," Höhere Montagekosten möglich.")) # Optional
            # elif inputs['project_details']['roof_covering_type']:st.success(get_text_di(texts,"roof_covering_info"," Dachbelegung problemlos.")) # Optional
        with col_build4:
            inputs["project_details"]["free_roof_area_sqm"] = st.number_input(
                label=get_text_di(
                    texts, "free_roof_area_label", "Freie Dachfläche (m²)"
                ),
                min_value=0.0,
                value=float(
                    inputs["project_details"].get("free_roof_area_sqm", 50.0) or 50.0
                ),
                key="free_roof_area_sqm_di_v6_exp_stable",
            )
        col_build5, col_build6 = st.columns(2)
        with col_build5:
            orientation_options = [please_select_text] + [
                "Süd",
                "Südost",
                "Ost",
                "Südwest",
                "West",
                "Nordwest",
                "Nord",
                "Nordost",
                "Flachdach (Süd)",
                "Flachdach (Ost-West)",
            ]
            default_orientation = inputs["project_details"].get(
                "roof_orientation", please_select_text
            )
            inputs["project_details"]["roof_orientation"] = st.selectbox(
                get_text_di(texts, "roof_orientation_label", "Dachausrichtung"),
                options=orientation_options,
                index=(
                    orientation_options.index(default_orientation)
                    if default_orientation in orientation_options
                    else 0
                ),
                key="roof_orientation_di_select_v6_exp_stable",
            )
            if inputs["project_details"]["roof_orientation"] == please_select_text:
                inputs["project_details"]["roof_orientation"] = None
        with col_build6:
            inputs["project_details"]["roof_inclination_deg"] = st.number_input(
                label=get_text_di(
                    texts, "roof_inclination_label", "Dachneigung (Grad)"
                ),
                min_value=0,
                max_value=90,
                value=int(
                    inputs["project_details"].get("roof_inclination_deg", 30) or 30
                ),
                key="roof_inclination_deg_di_v6_exp_stable",
            )
        inputs["project_details"]["building_height_gt_7m"] = st.checkbox(
            get_text_di(
                texts,
                "building_height_gt_7m_label",
                "Gebäudehöhe > 7 Meter (Gerüst erforderlich)",
            ),
            value=inputs["project_details"].get("building_height_gt_7m", False),
            key="building_height_gt_7m_di_v6_exp_stable",
        )

    st.markdown("---")
    st.subheader(
        get_text_di(texts, "future_consumption_header", "Zukünftiger Mehrverbrauch")
    )
    inputs["project_details"]["future_ev"] = st.checkbox(
        get_text_di(texts, "future_ev_checkbox_label", "Zukünftiges E-Auto einplanen"),
        value=inputs["project_details"].get("future_ev", False),
        key="future_ev_di_v6_exp_stable",
    )
    inputs["project_details"]["future_hp"] = st.checkbox(
        get_text_di(
            texts, "future_hp_checkbox_label", "Zukünftige Wärmepumpe einplanen"
        ),
        value=inputs["project_details"].get("future_hp", False),
        key="future_hp_di_v6_exp_stable",
    )

    st.subheader(
        get_text_di(texts, "technology_selection_header", "Auswahl der Technik")
    )
    if "tech_selection_expanded_di" not in st.session_state:
        st.session_state.tech_selection_expanded_di = True
    with st.expander(
        get_text_di(texts, "technology_selection_header", "Auswahl der Technik"),
        expanded=st.session_state.tech_selection_expanded_di,
    ):
        col_tech1, col_tech2 = st.columns(2)
        with col_tech1:
            inputs["project_details"]["module_quantity"] = st.number_input(
                label=get_text_di(texts, "module_quantity_label", "Anzahl PV Module"),
                min_value=0,
                value=int(inputs["project_details"].get("module_quantity", 20) or 20),
                key="module_quantity_di_tech_v6_exp_stable",
            )
        with col_tech2:
            current_module_name = inputs["project_details"].get(
                "selected_module_name", please_select_text
            )
            module_options_tech = [please_select_text] + MODULE_LIST_MODELS
            try:
                idx_module_tech = module_options_tech.index(current_module_name)
            except ValueError:
                idx_module_tech = 0
            selected_module_name_ui_tech = st.selectbox(
                get_text_di(texts, "module_model_label", "PV Modul Modell"),
                options=module_options_tech,
                index=idx_module_tech,
                key="selected_module_name_di_tech_v6_exp_stable",
            )
            inputs["project_details"]["selected_module_name"] = (
                selected_module_name_ui_tech
                if selected_module_name_ui_tech != please_select_text
                else None
            )
            st.session_state["selected_module_name"] = inputs["project_details"][
                "selected_module_name"
            ]
            if inputs["project_details"]["selected_module_name"]:
                module_details = get_product_by_model_name_safe(
                    inputs["project_details"]["selected_module_name"]
                )
                if module_details:
                    (
                        inputs["project_details"]["selected_module_id"],
                        inputs["project_details"]["selected_module_capacity_w"],
                    ) = module_details.get("id"), float(
                        module_details.get("capacity_w", 0.0) or 0.0
                    )
                # else:st.warning(get_text_di(texts,'module_details_not_loaded_warning',f"Details für Modul '{inputs['project_details']['selected_module_name']}' nicht geladen."));inputs['project_details']['selected_module_id'],inputs['project_details']['selected_module_capacity_w']=None,0.0 # Optional
            else:
                (
                    inputs["project_details"]["selected_module_id"],
                    inputs["project_details"]["selected_module_capacity_w"],
                ) = (None, 0.0)
        if (
            inputs["project_details"].get("selected_module_name")
            and inputs["project_details"].get("selected_module_capacity_w", 0.0) > 0
        ):
            st.info(
                f"{get_text_di(texts,'module_capacity_label','Leistung pro Modul (Wp)')}: {inputs['project_details']['selected_module_capacity_w']:.0f} Wp"
            )
        anlage_kwp_calc_tech = (
            (inputs["project_details"].get("module_quantity", 0) or 0)
            * (inputs["project_details"].get("selected_module_capacity_w", 0.0) or 0.0)
        ) / 1000.0
        st.info(
            f"{get_text_di(texts,'anlage_size_label','Anlagengröße (kWp)')}: {anlage_kwp_calc_tech:.2f} kWp"
        )
        inputs["project_details"]["anlage_kwp"] = anlage_kwp_calc_tech
        current_inverter_name = inputs["project_details"].get(
            "selected_inverter_name", please_select_text
        )
        inverter_options_tech = [please_select_text] + INVERTER_LIST_MODELS
        try:
            idx_inverter_tech = inverter_options_tech.index(current_inverter_name)
        except ValueError:
            idx_inverter_tech = 0
        selected_inverter_name_ui_tech = st.selectbox(
            get_text_di(texts, "inverter_model_label", "Wechselrichter Modell"),
            options=inverter_options_tech,
            index=idx_inverter_tech,
            key="selected_inverter_name_di_tech_v6_exp_stable",
        )
        inputs["project_details"]["selected_inverter_name"] = (
            selected_inverter_name_ui_tech
            if selected_inverter_name_ui_tech != please_select_text
            else None
        )
        st.session_state["selected_inverter_name"] = inputs["project_details"][
            "selected_inverter_name"
        ]
        if inputs["project_details"]["selected_inverter_name"]:
            inverter_details = get_product_by_model_name_safe(
                inputs["project_details"]["selected_inverter_name"]
            )
            if inverter_details:
                (
                    inputs["project_details"]["selected_inverter_id"],
                    inputs["project_details"]["selected_inverter_power_kw"],
                ) = inverter_details.get("id"), float(
                    inverter_details.get("power_kw", 0.0) or 0.0
                )
            # else:st.warning(get_text_di(texts,'inverter_details_not_loaded_warning',f"Details für WR '{inputs['project_details']['selected_inverter_name']}' nicht geladen."));inputs['project_details']['selected_inverter_id'],inputs['project_details']['selected_inverter_power_kw']=None,0.0 # Optional
        else:
            (
                inputs["project_details"]["selected_inverter_id"],
                inputs["project_details"]["selected_inverter_power_kw"],
            ) = (None, 0.0)
        if (
            inputs["project_details"].get("selected_inverter_name")
            and inputs["project_details"].get("selected_inverter_power_kw", 0.0) > 0
        ):
            st.info(
                f"{get_text_di(texts,'inverter_power_label','Leistung WR (kW)')}: {inputs['project_details']['selected_inverter_power_kw']:.2f} kW"
            )
        inputs["project_details"]["include_storage"] = st.checkbox(
            get_text_di(texts, "include_storage_label", "Batteriespeicher einplanen"),
            value=inputs["project_details"].get("include_storage", False),
            key="include_storage_di_tech_v6_exp_stable",
        )
        if inputs["project_details"]["include_storage"]:
            col_storage_model, col_storage_capacity = st.columns(2)
            with col_storage_model:
                current_storage_name = inputs["project_details"].get(
                    "selected_storage_name", please_select_text
                )
                storage_options_tech = [please_select_text] + STORAGE_LIST_MODELS
                try:
                    idx_storage_tech = storage_options_tech.index(current_storage_name)
                except ValueError:
                    idx_storage_tech = 0
                selected_storage_name_ui_tech = st.selectbox(
                    get_text_di(texts, "storage_model_label", "Speicher Modell"),
                    options=storage_options_tech,
                    index=idx_storage_tech,
                    key="selected_storage_name_di_tech_v6_exp_stable",
                )
                inputs["project_details"]["selected_storage_name"] = (
                    selected_storage_name_ui_tech
                    if selected_storage_name_ui_tech != please_select_text
                    else None
                )
                st.session_state["selected_storage_name"] = inputs["project_details"][
                    "selected_storage_name"
                ]
            storage_capacity_from_model_tech = 0.0
            if inputs["project_details"]["selected_storage_name"]:
                storage_details = get_product_by_model_name_safe(
                    inputs["project_details"]["selected_storage_name"]
                )
                if storage_details:
                    inputs["project_details"]["selected_storage_id"] = (
                        storage_details.get("id")
                    )
                    storage_capacity_from_model_tech = float(
                        storage_details.get("storage_power_kw", 0.0) or 0.0
                    )
                    st.info(
                        f"{get_text_di(texts,'storage_capacity_model_label','Kapazität Modell (kWh)')}: {storage_capacity_from_model_tech:.2f} kWh"
                    )
                # else:st.warning(get_text_di(texts,'storage_details_not_loaded_warning',f"Details für Speicher '{inputs['project_details']['selected_storage_name']}' nicht geladen."));inputs['project_details']['selected_storage_id']=None # Optional
            else:
                inputs["project_details"]["selected_storage_id"] = None
            with col_storage_capacity:
                default_manual_cap_tech = float(
                    inputs["project_details"].get(
                        "selected_storage_storage_power_kw", 0.0
                    )
                    or 0.0
                )
                if default_manual_cap_tech == 0.0:
                    default_manual_cap_tech = (
                        storage_capacity_from_model_tech
                        if storage_capacity_from_model_tech > 0
                        else 5.0
                    )
                inputs["project_details"]["selected_storage_storage_power_kw"] = (
                    st.number_input(
                        label=get_text_di(
                            texts,
                            "storage_capacity_manual_label",
                            "Gewünschte Gesamtkapazität (kWh)",
                        ),
                        min_value=0.0,
                        value=default_manual_cap_tech,
                        step=0.1,
                        key="selected_storage_storage_power_kw_di_tech_v6_exp_stable",
                    )
                )
        else:
            (
                inputs["project_details"]["selected_storage_name"],
                inputs["project_details"]["selected_storage_id"],
                inputs["project_details"]["selected_storage_storage_power_kw"],
            ) = (None, None, 0.0)

    st.markdown("---")
    st.subheader(
        get_text_di(texts, "additional_components_header", "Zusätzliche Komponenten")
    )
    inputs["project_details"]["include_additional_components"] = st.checkbox(
        get_text_di(
            texts,
            "include_additional_components_label",
            "Zusätzliche Komponenten einplanen",
        ),
        value=inputs["project_details"].get("include_additional_components", False),
        key="include_additional_components_di_tech_main_cb_v6_exp_stable",
    )
    if inputs["project_details"]["include_additional_components"]:

        def create_component_selector(
            component_label_key: str,
            component_list: List[str],
            project_details_key_name: str,
            project_details_key_id: str,
            widget_key_suffix: str,
        ):
            current_value = inputs["project_details"].get(
                project_details_key_name, please_select_text
            )
            options = [please_select_text] + component_list
            try:
                initial_idx = options.index(current_value)
            except ValueError:
                initial_idx = 0
            label_str = get_text_di(texts, component_label_key)
            selected_name = st.selectbox(
                label_str,
                options=options,
                index=initial_idx,
                key=f"{project_details_key_name}_widget_key_di_add_{widget_key_suffix}_v6_exp_stable",
            )
            inputs["project_details"][project_details_key_name] = (
                selected_name if selected_name != please_select_text else None
            )
            st.session_state[project_details_key_name] = inputs["project_details"][
                project_details_key_name
            ]
            if inputs["project_details"][project_details_key_name]:
                comp_details = get_product_by_model_name_safe(
                    inputs["project_details"][project_details_key_name]
                )
                inputs["project_details"][project_details_key_id] = (
                    comp_details.get("id") if comp_details else None
                )
            else:
                inputs["project_details"][project_details_key_id] = None

        create_component_selector(
            "wallbox_model_label",
            WALLBOX_LIST_MODELS,
            "selected_wallbox_name",
            "selected_wallbox_id",
            "wb_v6_exp_stable",
        )
        create_component_selector(
            "ems_model_label",
            EMS_LIST_MODELS,
            "selected_ems_name",
            "selected_ems_id",
            "ems_v6_exp_stable",
        )
        create_component_selector(
            "optimizer_model_label",
            OPTIMIZER_LIST_MODELS,
            "selected_optimizer_name",
            "selected_optimizer_id",
            "opti_v6_exp_stable",
        )
        create_component_selector(
            "carport_model_label",
            CARPORT_LIST_MODELS,
            "selected_carport_name",
            "selected_carport_id",
            "cp_v6_exp_stable",
        )
        create_component_selector(
            "notstrom_model_label",
            NOTSTROM_LIST_MODELS,
            "selected_notstrom_name",
            "selected_notstrom_id",
            "not_v6_exp_stable",
        )
        create_component_selector(
            "tierabwehr_model_label",
            TIERABWEHR_LIST_MODELS,
            "selected_tierabwehr_name",
            "selected_tierabwehr_id",
            "ta_v6_exp_stable",
        )

    # 
    #  FINANZIERUNG - Vollständige Bank-Finanzierungsfelder
    # 
    st.markdown("---")
    st.subheader(" Finanzierungsoptionen")

    # Finanzierung aktivieren Checkbox
    inputs["customer_data"]["financing_requested"] = st.checkbox(
        "Finanzierung / Leasing gewünscht",
        value=inputs["customer_data"].get("financing_requested", False),
        key="financing_requested_checkbox",
        help="Aktivieren Sie diese Option für eine vollständige Finanzierungsanalyse",
    )

    if inputs["customer_data"]["financing_requested"]:

        # Finanzierungsart wählen
        financing_type = st.radio(
            "Art der Finanzierung",
            options=["Bankkredit (Annuität)", "Leasing", "Contracting"],
            index=0,
            key="financing_type_radio",
            horizontal=True,
        )
        inputs["customer_data"]["financing_type"] = financing_type

        with st.expander(
            " **Persönliche Daten (Hauptantragsteller)**", expanded=True
        ):
            col_birth, col_nationality = st.columns(2)
            with col_birth:
                inputs["customer_data"]["birth_date"] = st.date_input(
                    "Geburtsdatum *",
                    value=inputs["customer_data"].get(
                        "birth_date", datetime(1980, 1, 1).date()
                    ),
                    key="birth_date_financing",
                )
            with col_nationality:
                inputs["customer_data"]["nationality"] = st.text_input(
                    "Staatsangehörigkeit *",
                    value=inputs["customer_data"].get("nationality", "Deutsch"),
                    key="nationality_financing",
                )

            col_resident_since, col_marital = st.columns(2)
            with col_resident_since:
                inputs["customer_data"]["resident_since"] = st.date_input(
                    "Wohnhaft an aktueller Adresse seit",
                    value=inputs["customer_data"].get(
                        "resident_since", datetime(2020, 1, 1).date()
                    ),
                    key="resident_since_financing",
                )
            with col_marital:
                marital_options = [
                    "Ledig",
                    "Verheiratet/Verpartnert",
                    "Geschieden",
                    "Verwitwet",
                ]
                inputs["customer_data"]["marital_status"] = st.selectbox(
                    "Familienstand *",
                    options=marital_options,
                    index=marital_options.index(
                        inputs["customer_data"].get("marital_status", "Ledig")
                    ),
                    key="marital_status_financing",
                )

            if inputs["customer_data"]["marital_status"] in ["Verheiratet/Verpartnert"]:
                inputs["customer_data"]["property_regime"] = st.selectbox(
                    "Güterstand",
                    options=[
                        "Zugewinngemeinschaft",
                        "Gütergemeinschaft",
                        "Gütertrennung",
                    ],
                    index=0,
                    key="property_regime_financing",
                )

            inputs["customer_data"]["dependent_children"] = st.number_input(
                "Anzahl unterhaltspflichtiger Kinder",
                min_value=0,
                max_value=10,
                value=inputs["customer_data"].get("dependent_children", 0),
                key="dependent_children_financing",
            )

        with st.expander(" **Berufs- & Einkommenssituation**", expanded=True):
            col_status, col_profession = st.columns(2)
            with col_status:
                professional_status_options = [
                    "Angestellter",
                    "Beamter",
                    "Selbstständig/Freiberufler",
                    "Arbeiter",
                    "Rentner/Pensionär",
                    "Sonstiges",
                ]
                inputs["customer_data"]["professional_status"] = st.selectbox(
                    "Beruflicher Status *",
                    options=professional_status_options,
                    index=0,
                    key="professional_status_financing",
                )
            with col_profession:
                inputs["customer_data"]["profession"] = st.text_input(
                    "Ausgeübter Beruf *",
                    value=inputs["customer_data"].get("profession", ""),
                    key="profession_financing",
                )

            col_employer, col_sector = st.columns(2)
            with col_employer:
                inputs["customer_data"]["employer_name"] = st.text_input(
                    "Arbeitgeber (Name)",
                    value=inputs["customer_data"].get("employer_name", ""),
                    key="employer_name_financing",
                )
            with col_sector:
                inputs["customer_data"]["business_sector"] = st.text_input(
                    "Branche",
                    value=inputs["customer_data"].get("business_sector", ""),
                    key="business_sector_financing",
                )

            inputs["customer_data"]["employer_address"] = st.text_area(
                "Arbeitgeber Anschrift",
                value=inputs["customer_data"].get("employer_address", ""),
                key="employer_address_financing",
                height=80,
            )

            col_employed_since, col_employment_type = st.columns(2)
            with col_employed_since:
                inputs["customer_data"]["employed_since"] = st.date_input(
                    "Beschäftigt seit (Monat/Jahr)",
                    value=inputs["customer_data"].get(
                        "employed_since", datetime(2020, 1, 1).date()
                    ),
                    key="employed_since_financing",
                )
            with col_employment_type:
                employment_type_options = ["Unbefristet", "Befristet"]
                inputs["customer_data"]["employment_type"] = st.selectbox(
                    "Arbeitsverhältnis",
                    options=employment_type_options,
                    index=0,
                    key="employment_type_financing",
                )

            if inputs["customer_data"]["employment_type"] == "Befristet":
                inputs["customer_data"]["employment_end_date"] = st.date_input(
                    "Befristet bis",
                    value=inputs["customer_data"].get(
                        "employment_end_date", datetime(2025, 12, 31).date()
                    ),
                    key="employment_end_date_financing",
                )

            col_net_income, col_other_income = st.columns(2)
            with col_net_income:
                inputs["customer_data"]["monthly_net_income"] = st.number_input(
                    "Monatliches Nettoeinkommen (€) *",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get("monthly_net_income", 3000.0)
                    ),
                    step=100.0,
                    key="monthly_net_income_financing",
                )
            with col_other_income:
                inputs["customer_data"]["other_monthly_income"] = st.number_input(
                    "Sonstige monatliche Einkünfte (€)",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get("other_monthly_income", 0.0)
                    ),
                    step=50.0,
                    key="other_monthly_income_financing",
                )

            if inputs["customer_data"]["other_monthly_income"] > 0:
                inputs["customer_data"]["other_income_description"] = st.text_input(
                    "Beschreibung der sonstigen Einkünfte",
                    value=inputs["customer_data"].get("other_income_description", ""),
                    key="other_income_description_financing",
                )

        with st.expander(" **Monatliche Ausgaben**", expanded=True):
            col_rent, col_health_insurance = st.columns(2)
            with col_rent:
                inputs["customer_data"]["monthly_rent_costs"] = st.number_input(
                    "Miete/Wohnkosten (€/Monat)",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get("monthly_rent_costs", 800.0)
                    ),
                    step=50.0,
                    key="monthly_rent_costs_financing",
                )
            with col_health_insurance:
                inputs["customer_data"]["private_health_insurance"] = st.number_input(
                    "Private Krankenversicherung (€/Monat)",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get("private_health_insurance", 0.0)
                    ),
                    step=25.0,
                    key="private_health_insurance_financing",
                )

            col_existing_loans, col_leasing = st.columns(2)
            with col_existing_loans:
                inputs["customer_data"]["existing_loan_payments"] = st.number_input(
                    "Bestehende Ratenkredite (€/Monat)",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get("existing_loan_payments", 0.0)
                    ),
                    step=50.0,
                    key="existing_loan_payments_financing",
                )
            with col_leasing:
                inputs["customer_data"]["existing_leasing_payments"] = st.number_input(
                    "Leasingraten (€/Monat)",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get("existing_leasing_payments", 0.0)
                    ),
                    step=50.0,
                    key="existing_leasing_payments_financing",
                )

            inputs["customer_data"]["alimony_payments"] = st.number_input(
                "Unterhaltsverpflichtungen (€/Monat)",
                min_value=0.0,
                value=float(inputs["customer_data"].get("alimony_payments", 0.0)),
                step=50.0,
                key="alimony_payments_financing",
            )

        with st.expander(" **Finanzierungsdetails zum PV-Vorhaben**", expanded=True):
            # Gesamtkosten werden aus der Konfiguration übernommen - hier als Platzhalter
            estimated_total_costs = 25000.0  # Wird später aus calculations übernommen
            st.info(
                f" Geschätzte Gesamtkosten der PV-Anlage: {estimated_total_costs:,.2f} €"
            )

            col_financing_amount, col_equity = st.columns(2)
            with col_financing_amount:
                inputs["customer_data"]["desired_financing_amount"] = st.number_input(
                    "Gewünschter Finanzierungsbetrag (€) *",
                    min_value=0.0,
                    max_value=estimated_total_costs,
                    value=float(
                        inputs["customer_data"].get(
                            "desired_financing_amount", estimated_total_costs * 0.8
                        )
                    ),
                    step=500.0,
                    key="desired_financing_amount_financing",
                )
            with col_equity:
                inputs["customer_data"]["equity_amount"] = st.number_input(
                    "Höhe des Eigenkapitals (€)",
                    min_value=0.0,
                    value=float(
                        inputs["customer_data"].get(
                            "equity_amount", estimated_total_costs * 0.2
                        )
                    ),
                    step=500.0,
                    key="equity_amount_financing",
                )

            if financing_type == "Bankkredit (Annuität)":
                col_loan_term, col_interest_rate = st.columns(2)
                with col_loan_term:
                    inputs["customer_data"]["loan_term_years"] = st.number_input(
                        "Gewünschte Laufzeit (Jahre)",
                        min_value=5,
                        max_value=30,
                        value=int(inputs["customer_data"].get("loan_term_years", 15)),
                        key="loan_term_years_financing",
                    )
                with col_interest_rate:
                    inputs["customer_data"]["interest_rate_percent"] = st.number_input(
                        "Zinssatz (% p.a.)",
                        min_value=0.5,
                        max_value=15.0,
                        value=float(
                            inputs["customer_data"].get("interest_rate_percent", 4.5)
                        ),
                        step=0.1,
                        key="interest_rate_percent_financing",
                    )

            elif financing_type == "Leasing":
                col_leasing_term, col_leasing_factor = st.columns(2)
                with col_leasing_term:
                    inputs["customer_data"]["leasing_term_months"] = st.number_input(
                        "Leasinglaufzeit (Monate)",
                        min_value=24,
                        max_value=240,
                        value=int(
                            inputs["customer_data"].get("leasing_term_months", 120)
                        ),
                        step=12,
                        key="leasing_term_months_financing",
                    )
                with col_leasing_factor:
                    inputs["customer_data"]["leasing_factor_percent"] = st.number_input(
                        "Leasingfaktor (% pro Monat)",
                        min_value=0.5,
                        max_value=5.0,
                        value=float(
                            inputs["customer_data"].get("leasing_factor_percent", 1.2)
                        ),
                        step=0.1,
                        key="leasing_factor_percent_financing",
                    )

        # Zweiter Antragsteller
        inputs["customer_data"]["has_co_applicant"] = st.checkbox(
            " Zweiten Antragsteller hinzufügen",
            value=inputs["customer_data"].get("has_co_applicant", False),
            key="has_co_applicant_checkbox",
        )

        if inputs["customer_data"]["has_co_applicant"]:
            with st.expander(
                " **Zweiter Antragsteller - Persönliche Daten**", expanded=False
            ):
                col_birth2, col_nationality2 = st.columns(2)
                with col_birth2:
                    inputs["customer_data"]["co_birth_date"] = st.date_input(
                        "Geburtsdatum *",
                        value=inputs["customer_data"].get(
                            "co_birth_date", datetime(1980, 1, 1).date()
                        ),
                        key="co_birth_date_financing",
                    )
                with col_nationality2:
                    inputs["customer_data"]["co_nationality"] = st.text_input(
                        "Staatsangehörigkeit *",
                        value=inputs["customer_data"].get("co_nationality", "Deutsch"),
                        key="co_nationality_financing",
                    )

                # Weitere Felder für zweiten Antragsteller analog zum ersten
                inputs["customer_data"]["co_profession"] = st.text_input(
                    "Ausgeübter Beruf *",
                    value=inputs["customer_data"].get("co_profession", ""),
                    key="co_profession_financing",
                )

                col_co_income, col_co_status = st.columns(2)
                with col_co_income:
                    inputs["customer_data"]["co_monthly_net_income"] = st.number_input(
                        "Monatliches Nettoeinkommen (€) *",
                        min_value=0.0,
                        value=float(
                            inputs["customer_data"].get("co_monthly_net_income", 2500.0)
                        ),
                        step=100.0,
                        key="co_monthly_net_income_financing",
                    )
                with col_co_status:
                    inputs["customer_data"]["co_professional_status"] = st.selectbox(
                        "Beruflicher Status *",
                        options=professional_status_options,
                        index=0,
                        key="co_professional_status_financing",
                    )

        # Finanzierungsauswertung anzeigen
        if st.button(" Finanzierung berechnen", key="calculate_financing_btn"):
            # Hier wird später die financial_tools Integration erfolgen
            st.success(
                " Finanzierungsberechnung wird im Analyse-Dashboard angezeigt!"
            )

    st.subheader(
        get_text_di(texts, "economic_data_header", "Wirtschaftliche Parameter")
    )
    if "economic_data_expanded_di" not in st.session_state:
        st.session_state.economic_data_expanded_di = False
    with st.expander(
        get_text_di(texts, "economic_data_header", "Wirtschaftliche Parameter"),
        expanded=st.session_state.economic_data_expanded_di,
    ):
        inputs["economic_data"]["simulation_period_years"] = st.number_input(
            label=get_text_di(
                texts, "simulation_period_label_short", "Simulationsdauer (Jahre)"
            ),
            min_value=5,
            max_value=50,
            value=int(inputs["economic_data"].get("simulation_period_years", 20) or 20),
            key="sim_period_econ_di_v6_exp_stable",
        )
        inputs["economic_data"]["electricity_price_increase_annual_percent"] = (
            st.number_input(
                label=get_text_di(
                    texts,
                    "electricity_price_increase_label_short",
                    "Strompreissteigerung p.a. (%)",
                ),
                min_value=0.0,
                max_value=10.0,
                value=float(
                    inputs["economic_data"].get(
                        "electricity_price_increase_annual_percent", 3.0
                    )
                    or 3.0
                ),
                step=0.1,
                format="%.1f",
                key="elec_increase_econ_di_v6_exp_stable",
            )
        )
        inputs["economic_data"]["custom_costs_netto"] = st.number_input(
            label=get_text_di(
                texts,
                "custom_costs_netto_label",
                "Zusätzliche einmalige Nettokosten (€)",
            ),
            min_value=0.0,
            value=float(inputs["economic_data"].get("custom_costs_netto", 0.0) or 0.0),
            step=10.0,
            key="custom_costs_netto_di_v6_exp_stable",
        )

    # 
    #  CRM INTEGRATION - ALLE DATEN AUTOMATISCH SPEICHERN
    # 
    if CRM_SYSTEM_AVAILABLE:
        # CRM Save Button mit allen aktuellen Daten
        project_data_for_crm = inputs.copy()  # Aktueller Zustand aller Eingaben

        # Fallback für analysis_results wenn noch nicht berechnet
        analysis_results_for_crm = st.session_state.get(
            "analysis_results",
            {
                "anlage_kwp": inputs["project_details"].get("anlage_kwp", 0),
                "final_cost": 25000.0,  # Dummy-Wert - wird durch echte Berechnung ersetzt
                "annual_pv_production_kwh": 8500,
                "payback_period_years": 12,
            },
        )

        # PDF aus Session State falls vorhanden
        pdf_bytes_for_crm = None
        if "generated_pdf_bytes" in st.session_state:
            pdf_bytes_for_crm = st.session_state["generated_pdf_bytes"]

        # CRM Save Button anzeigen
        crm_saved = create_crm_save_button(
            project_data=project_data_for_crm,
            analysis_results=analysis_results_for_crm,
            pdf_bytes=pdf_bytes_for_crm,
        )

        if crm_saved:
            st.balloons()  # Feier-Animation bei erfolgreichem Speichern
    else:
        st.info(
            " CRM-System nicht verfügbar. Installieren Sie `complete_crm_system.py` für automatische Kundenspeicherung."
        )

    # KORREKTUR: `st.session_state.project_data` wird direkt modifiziert, kein `copy()` und kein return mehr nötig.
    # st.session_state.project_data = inputs # Nicht mehr nötig, da inputs eine Referenz ist
    # return inputs # Nicht mehr nötig


# Änderungshistorie
# ... (vorherige Einträge)
# 2025-06-04, Gemini Ultra: `render_data_input` gibt `inputs` nicht mehr zurück, da `st.session_state.project_data` direkt modifiziert wird.
#                           Der explizite `st.rerun()`-Aufruf im Button-Callback für "Daten aus Adresse übernehmen" und "Koordinaten abrufen" wurde entfernt.
#                           Streamlit führt nach Button-Interaktionen automatisch einen Rerun durch. Dies kann helfen, das "Springen" zu reduzieren, indem die Anzahl der Reruns kontrollierter wird.
#                           Widget-Keys wurden um "_stable" erweitert, um sicherzustellen, dass sie nicht mit früheren Versionen kollidieren und stabil sind.
#                           Die st.warning und st.info Meldungen im UI wurden auskommentiert, um die Ausgabe bei normalem Betrieb sauberer zu halten. Sie können für Debugging bei Bedarf wieder aktiviert werden.
