# crm.py
# Modul für das Customer Relationship Management (CRM)

import streamlit as st
import sqlite3
import re
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import traceback
import pandas as pd

try:
    from database import get_db_connection as real_get_db_connection
    if not callable(real_get_db_connection): raise ImportError("Imported get_db_connection is not callable.")
    get_db_connection_safe_crm = real_get_db_connection
except ImportError as e:
    def _dummy_get_db_connection_ie(): # type: ignore
        print(f"crm.py: Importfehler für database.py: {e}. Dummy DB-Verbindung genutzt.")
        return None
    get_db_connection_safe_crm = _dummy_get_db_connection_ie
    print(f"crm.py: Importfehler für database.py: {e}. Dummy DB Funktionen werden genutzt.")
except Exception as e:
    def _dummy_get_db_connection_ex(): # type: ignore
        print(f"crm.py: Fehler beim Laden von database.py: {e}. Dummy DB-Verbindung genutzt.")
        return None
    get_db_connection_safe_crm = _dummy_get_db_connection_ex
    print(f"crm.py: Fehler beim Laden von database.py: {e}. Dummy DB Funktionen werden genutzt.")

def get_text_crm(texts_dict: Dict[str, str], key: str, fallback_text: Optional[str] = None) -> str:
    return texts_dict.get(key, fallback_text if fallback_text is not None else key.replace("_", " ").title())

def create_tables_crm(conn: sqlite3.Connection):
    cursor = conn.cursor()
    # KORREKTUR: Alle Spalten in der CREATE TABLE Anweisung definieren.
    # ALTER TABLE wird verwendet, um fehlende Spalten HINZUZUFÜGEN,
    # falls die Tabelle bereits ohne sie existiert.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salutation TEXT,
            title TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company_name TEXT,
            address TEXT,
            house_number TEXT,
            zip_code TEXT,
            city TEXT,
            state TEXT,
            region TEXT,
            email TEXT,
            phone_landline TEXT,
            phone_mobile TEXT,
            income_tax_rate_percent REAL DEFAULT 0.0,
            creation_date TEXT,
            last_updated TEXT
        )
    """)
    conn.commit() # Commit changes before attempting ALTER TABLE

    # KORREKTUR: Migrationslogik für fehlende Spalten nach der initialen Erstellung
    # Dies ist eine gängige Methode, um das Schema zu aktualisieren, ohne Daten zu verlieren.
    # Wir versuchen, jede Spalte hinzuzufügen und fangen den Fehler ab, wenn sie bereits existiert.
    current_customer_columns = [col[1] for col in conn.execute("PRAGMA table_info(customers)").fetchall()]
    
    columns_to_add = {
        "state": "TEXT",
        "region": "TEXT",
        "email": "TEXT",
        "phone_landline": "TEXT",
        "phone_mobile": "TEXT",
        "income_tax_rate_percent": "REAL DEFAULT 0.0",
        "creation_date": "TEXT",
        "last_updated": "TEXT"
    }

    for col_name, col_type in columns_to_add.items():
        if col_name not in current_customer_columns:
            try:
                cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                conn.commit()
                print(f"CRM DB: Spalte '{col_name}' zur Tabelle 'customers' hinzugefügt.")
            except sqlite3.OperationalError as e:
                # Dies sollte nur bei "duplicate column name" passieren, was ok ist.
                print(f"CRM DB migration warning: Konnte Spalte '{col_name}' nicht hinzufügen, da sie bereits existiert oder ein anderer Fehler auftrat: {e}")
            except Exception as e:
                print(f"CRM DB migration ERROR adding column '{col_name}': {e}")
    
    conn.commit() # Sicherstellen, dass alle ALTER TABLEs committed sind

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            project_status TEXT,
            roof_type TEXT,
            roof_covering_type TEXT,
            free_roof_area_sqm REAL,
            roof_orientation TEXT,
            roof_inclination_deg INTEGER,
            building_height_gt_7m INTEGER,
            annual_consumption_kwh REAL,
            costs_household_euro_mo REAL,
            annual_heating_kwh REAL,
            costs_heating_euro_mo REAL,
            anlage_type TEXT,
            feed_in_type TEXT,
            module_quantity INTEGER,
            selected_module_id INTEGER,
            selected_inverter_id INTEGER,
            include_storage INTEGER,
            selected_storage_id INTEGER,
            selected_storage_storage_power_kw REAL,
            include_additional_components INTEGER,
            selected_wallbox_id INTEGER,
            selected_ems_id INTEGER,
            selected_optimizer_id INTEGER,
            selected_carport_id INTEGER,
            selected_notstrom_id INTEGER,
            selected_tierabwehr_id INTEGER,
            visualize_roof_in_pdf INTEGER,
            latitude REAL,
            longitude REAL,
            creation_date TEXT,
            last_updated TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    conn.commit()

def save_customer(conn: sqlite3.Connection, customer_data: Dict[str, Any]) -> Optional[int]:
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    customer_data['last_updated'] = now
    
    table_info_cursor = conn.execute(f"PRAGMA table_info(customers)").fetchall()
    existing_db_columns = [info[1] for info in table_info_cursor]

    data_to_save = {k: v for k, v in customer_data.items() if k in existing_db_columns}

    if 'id' in data_to_save and data_to_save['id']:
        # Update existing customer
        customer_id = data_to_save['id']
        fields = [f"{k}=?" for k in data_to_save if k != 'id']
        values = [data_to_save[k] for k in data_to_save if k != 'id']
        values.append(customer_id)
        cursor.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
        return customer_id
    else:
        fields = ', '.join(data_to_save.keys())
        placeholders = ', '.join(['?'] * len(data_to_save))
        cursor.execute(f"INSERT INTO customers ({fields}) VALUES ({placeholders})", list(data_to_save.values()))
        conn.commit()
        return cursor.lastrowid

def load_customer(conn: sqlite3.Connection, customer_id: int) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def delete_customer(conn: sqlite3.Connection, customer_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE customer_id=?", (customer_id,))
    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    return cursor.rowcount > 0

def load_all_customers(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def save_project(conn: sqlite3.Connection, project_data: Dict[str, Any]) -> Optional[int]:
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    project_data['last_updated'] = now
    project_data['creation_date'] = project_data.get('creation_date', now)

    table_info_cursor = conn.execute(f"PRAGMA table_info(projects)").fetchall()
    existing_columns = [info[1] for info in table_info_cursor]
    
    insert_data = {k: v for k, v in project_data.items() if k in existing_columns}

    if 'id' in project_data and project_data['id']:
        project_id = project_data['id']
        fields = [f"{k}=?" for k in insert_data if k != 'id']
        values = [insert_data[k] for k in insert_data if k != 'id']
        values.append(project_id)
        cursor.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
        return project_id
    else:
        fields = ', '.join(insert_data.keys())
        placeholders = ', '.join(['?'] * len(insert_data))
        cursor.execute(f"INSERT INTO projects ({fields}) VALUES ({placeholders})", list(insert_data.values()))
        conn.commit()
        return cursor.lastrowid

def load_project(conn: sqlite3.Connection, project_id: int) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def delete_project(conn: sqlite3.Connection, project_id: int) -> bool:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    return cursor.rowcount > 0

def load_projects_for_customer(conn: sqlite3.Connection, customer_id: int) -> List[Dict[str, Any]]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE customer_id=?", (customer_id,))
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def render_crm(texts: Dict[str, str], get_db_connection_func: Callable[[], Optional[sqlite3.Connection]]):
    st.header(get_text_crm(texts, "menu_item_crm", "Kundenverwaltung (CRM - C)"))

    conn = get_db_connection_func()
    if conn is None:
        st.error(get_text_crm(texts, "db_connection_unavailable", "Datenbankverbindung nicht verfügbar. CRM-Funktionen eingeschränkt."))
        return

    create_tables_crm(conn) # Erstellt die Tabellen (inkl. neuer Spalten) oder fügt Spalten hinzu

    view_mode = st.session_state.get('crm_view_mode', 'customer_list')
    selected_customer_id = st.session_state.get('selected_customer_id', None)
    selected_project_id = st.session_state.get('selected_project_id', None)

    if view_mode == 'customer_list':
        st.subheader(get_text_crm(texts, "crm_customer_list_header", "Alle Kunden"))
        
        if st.button(get_text_crm(texts, "crm_add_new_customer_button", "➕ Neuen Kunden anlegen"), key="add_new_customer_btn"):
            st.session_state['crm_view_mode'] = 'add_customer'
            st.session_state['selected_customer_id'] = None
            st.session_state['selected_project_id'] = None
            st.rerun()

        customers = load_all_customers(conn)
        if customers:
            df_customers = pd.DataFrame(customers)
            # KORREKTUR: hide_row_index durch hide_index ersetzen
            st.dataframe(df_customers, use_container_width=True, hide_index=True)
            
            for customer in customers:
                col_c_id, col_c_name, col_c_actions = st.columns([0.5, 2, 2])
                col_c_id.write(customer['id'])
                col_c_name.write(f"{customer.get('first_name', '')} {customer.get('last_name', '')} ({customer.get('city', '')})")
                
                with col_c_actions:
                    btn_view = col_c_actions.button(get_text_crm(texts, "crm_view_button", "Ansehen"), key=f"view_customer_{customer['id']}")
                    btn_edit = col_c_actions.button(get_text_crm(texts, "crm_edit_button", "Bearbeiten"), key=f"edit_customer_{customer['id']}")
                    
                    delete_button_key = f"del_customer_{customer['id']}"
                    confirm_delete_key = f"confirm_delete_customer_{customer['id']}"

                    if btn_view:
                        st.session_state['selected_customer_id'] = customer['id']
                        st.session_state['crm_view_mode'] = 'view_customer'
                        st.rerun()
                    if btn_edit:
                        st.session_state['selected_customer_id'] = customer['id']
                        st.session_state['crm_view_mode'] = 'edit_customer'
                        st.rerun()
                    
                    if col_c_actions.button(get_text_crm(texts, "crm_delete_button", "Löschen"), key=delete_button_key):
                        if st.session_state.get(confirm_delete_key, False):
                            if delete_customer(conn, customer['id']):
                                st.success(get_text_crm(texts, "crm_customer_deleted", "Kunde gelöscht."))
                                del st.session_state[confirm_delete_key]
                                st.rerun()
                            else:
                                st.error(get_text_crm(texts, "crm_delete_customer_failed", "Löschen fehlgeschlagen."))
                        else:
                            st.warning(get_text_crm(texts, "crm_confirm_delete_customer", "Sicher? Klick nochmal zum Bestätigen."))
                            st.session_state[confirm_delete_key] = True
                        
        else:
            st.info(get_text_crm(texts, "crm_no_customers_found", "Keine Kunden in der Datenbank."))

    elif view_mode == 'add_customer' or view_mode == 'edit_customer':
        customer_to_edit = {}
        if view_mode == 'edit_customer' and selected_customer_id:
            customer_to_edit = load_customer(conn, selected_customer_id) or {}
            st.subheader(get_text_crm(texts, "crm_edit_customer_header", f"Kunden bearbeiten: {customer_to_edit.get('first_name', '')} {customer_to_edit.get('last_name', '')}"))
        else:
            st.subheader(get_text_crm(texts, "crm_add_customer_header", "Neuen Kunden anlegen"))

        with st.form("customer_form", clear_on_submit=False):
            st.write(get_text_crm(texts, "crm_customer_form_intro", "Kundendaten eingeben/bearbeiten:"))
            
            salutation = st.selectbox(get_text_crm(texts, "salutation_label", "Anrede"), options=['Herr', 'Frau', 'Familie', 'Divers', ''], index=['Herr', 'Frau', 'Familie', 'Divers', ''].index(customer_to_edit.get('salutation', '')))
            title = st.text_input(get_text_crm(texts, "title_label", "Titel"), value=customer_to_edit.get('title', ''))
            first_name = st.text_input(get_text_crm(texts, "first_name_label", "Vorname"), value=customer_to_edit.get('first_name', ''))
            last_name = st.text_input(get_text_crm(texts, "last_name_label", "Nachname"), value=customer_to_edit.get('last_name', ''))
            company_name = st.text_input(get_text_crm(texts, "company_name_label", "Firmenname (optional)"), value=customer_to_edit.get('company_name', ''))
            
            address = st.text_input(get_text_crm(texts, "street_label", "Straße"), value=customer_to_edit.get('address', ''))
            house_number = st.text_input(get_text_crm(texts, "house_number_label", "Hausnummer"), value=customer_to_edit.get('house_number', ''))
            zip_code = st.text_input(get_text_crm(texts, "zip_code_label", "PLZ"), value=customer_to_edit.get('zip_code', ''))
            city = st.text_input(get_text_crm(texts, "city_label", "Ort"), value=customer_to_edit.get('city', ''))
            state = st.text_input(get_text_crm(texts, "state_label", "Bundesland"), value=customer_to_edit.get('state', ''))
            region = st.text_input(get_text_crm(texts, "region_label", "Region"), value=customer_to_edit.get('region', ''))
            
            email = st.text_input(get_text_crm(texts, "email_label", "E-Mail"), value=customer_to_edit.get('email', ''))
            phone_landline = st.text_input(get_text_crm(texts, "phone_landline_label", "Telefon (Festnetz)"), value=customer_to_edit.get('phone_landline', ''))
            phone_mobile = st.text_input(get_text_crm(texts, "phone_mobile_label", "Telefon (Mobil)"), value=customer_to_edit.get('phone_mobile', ''))
            income_tax_rate_percent = st.number_input(get_text_crm(texts, "income_tax_rate_label", "Einkommenssteuersatz (%)"), min_value=0.0, max_value=100.0, value=float(customer_to_edit.get('income_tax_rate_percent', 0.0)))


            submitted = st.form_submit_button(get_text_crm(texts, "crm_save_customer_button", "Kunden speichern"))
            if submitted:
                new_customer_data = {
                    'id': customer_to_edit.get('id'),
                    'salutation': salutation if salutation else None,
                    'title': title if title else None,
                    'first_name': first_name,
                    'last_name': last_name,
                    'company_name': company_name if company_name else None,
                    'address': address if address else None,
                    'house_number': house_number if house_number else None,
                    'zip_code': zip_code if zip_code else None,
                    'city': city if city else None,
                    'state': state if state else None,
                    'region': region if region else None,
                    'email': email if email else None,
                    'phone_landline': phone_landline if phone_landline else None,
                    'phone_mobile': phone_mobile if phone_mobile else None,
                    'income_tax_rate_percent': income_tax_rate_percent,
                    'creation_date': customer_to_edit.get('creation_date', datetime.now().isoformat())
                }
                
                if not new_customer_data['first_name'] or not new_customer_data['last_name']:
                    st.error(get_text_crm(texts, "crm_name_required_error", "Vor- und Nachname sind Pflichtfelder."))
                else:
                    saved_id = save_customer(conn, new_customer_data)
                    if saved_id:
                        st.success(get_text_crm(texts, "crm_customer_saved", "Kunde erfolgreich gespeichert!"))
                        st.session_state['crm_view_mode'] = 'customer_list'
                        st.session_state['selected_customer_id'] = saved_id
                        st.rerun()
                    else:
                        st.error(get_text_crm(texts, "crm_customer_save_failed", "Fehler beim Speichern des Kunden."))
            
            if st.form_submit_button(get_text_crm(texts, "crm_cancel_button", "Abbrechen")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.session_state['selected_customer_id'] = None
                st.rerun()

    elif view_mode == 'view_customer' or view_mode == 'add_project' or view_mode == 'edit_project' or view_mode == 'view_project':
        if selected_customer_id is None:
            st.error(get_text_crm(texts, "crm_no_customer_selected", "Kein Kunde ausgewählt."))
            if st.button(get_text_crm(texts, "crm_back_to_list_button", "Zurück zur Kundenliste")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.rerun()
            return

        current_customer = load_customer(conn, selected_customer_id)
        if not current_customer:
            st.error(get_text_crm(texts, "crm_customer_not_found", "Kunde nicht gefunden."))
            if st.button(get_text_crm(texts, "crm_back_to_list_button", "Zurück zur Kundenliste")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.rerun()
            return

        st.subheader(get_text_crm(texts, "crm_customer_details_header", "Kundendetails"))
        st.write(f"**{get_text_crm(texts, 'first_name_label', 'Vorname')}:** {current_customer.get('first_name', '')}")
        st.write(f"**{get_text_crm(texts, 'last_name_label', 'Nachname')}:** {current_customer.get('last_name', '')}")
        st.write(f"**{get_text_crm(texts, 'email_label', 'E-Mail')}:** {current_customer.get('email', '')}")
        st.write(f"**{get_text_crm(texts, 'address_label', 'Adresse')}:** {current_customer.get('address', '')} {current_customer.get('house_number', '')}, {current_customer.get('zip_code', '')} {current_customer.get('city', '')}")
        st.write(f"**{get_text_crm(texts, 'income_tax_rate_label', 'Einkommenssteuersatz')}:** {current_customer.get('income_tax_rate_percent', 0.0)}%")

        st.markdown("---")
        st.subheader(get_text_crm(texts, "crm_projects_header", "Projekte des Kunden"))

        if st.button(get_text_crm(texts, "crm_add_new_project_button", "➕ Neues Projekt anlegen"), key="add_new_project_btn_2"):
            st.session_state['crm_view_mode'] = 'add_project'
            st.session_state['selected_project_id'] = None
            st.rerun()

        projects = load_projects_for_customer(conn, selected_customer_id)
        if projects:
            df_projects = pd.DataFrame(projects)
            # KORREKTUR: hide_row_index durch hide_index ersetzen
            st.dataframe(df_projects, use_container_width=True, hide_index=True)

            for project in projects:
                col_p_id, col_p_name, col_p_actions = st.columns([0.5, 2, 2])
                col_p_id.write(project['id'])
                col_p_name.write(project.get('project_name', ''))

                with col_p_actions:
                    btn_view_p = col_p_actions.button(get_text_crm(texts, "crm_view_button", "Ansehen"), key=f"view_project_{project['id']}")
                    btn_edit_p = col_p_actions.button(get_text_crm(texts, "crm_edit_button", "Bearbeiten"), key=f"edit_project_{project['id']}")
                    delete_project_button_key = f"del_project_{project['id']}"
                    confirm_delete_project_key = f"confirm_delete_project_{project['id']}"

                    if btn_view_p:
                        st.session_state['selected_project_id'] = project['id']
                        st.session_state['crm_view_mode'] = 'view_project'
                        st.rerun()
                    if btn_edit_p:
                        st.session_state['selected_project_id'] = project['id']
                        st.session_state['crm_view_mode'] = 'edit_project'
                        st.rerun()
                    
                    if col_p_actions.button(get_text_crm(texts, "crm_delete_button", "Löschen"), key=delete_project_button_key):
                        if st.session_state.get(confirm_delete_project_key, False):
                            if delete_project(conn, project['id']):
                                st.success(get_text_crm(texts, "crm_project_deleted", "Projekt gelöscht."))
                                del st.session_state[confirm_delete_project_key]
                                st.rerun()
                            else:
                                st.error(get_text_crm(texts, "crm_delete_project_failed", "Löschen fehlgeschlagen."))
                        else:
                            st.warning(get_text_crm(texts, "crm_confirm_delete_project", "Sicher? Klick nochmal zum Bestätigen."))
                            st.session_state[confirm_delete_project_key] = True
        else:
            st.info(get_text_crm(texts, "crm_no_projects_found", "Keine Projekte für diesen Kunden."))

        if st.button(get_text_crm(texts, "crm_back_to_customers_button", "Zurück zu Kundenprojekten"), key="back_to_customer_list_from_projects"):
            st.session_state['crm_view_mode'] = 'customer_list'
            st.session_state['selected_customer_id'] = None
            st.session_state['selected_project_id'] = None
            st.rerun()

    elif view_mode == 'add_project' or view_mode == 'edit_project':
        project_to_edit = {}
        if view_mode == 'edit_project' and selected_project_id:
            project_to_edit = load_project(conn, selected_project_id) or {}
            st.subheader(get_text_crm(texts, "crm_edit_project_header", f"Projekt bearbeiten: {project_to_edit.get('project_name', '')}"))
        else:
            st.subheader(get_text_crm(texts, "crm_add_project_header", "Neues Projekt anlegen"))

        st.info(get_text_crm(texts, "crm_project_data_from_input_tab_info", "Projektdaten können aus dem 'Projektdateneingabe (A)' Tab geladen werden, oder manuell eingegeben werden."))
        
        if st.button(get_text_crm(texts, "crm_load_from_input_tab", "Daten aus Eingabe-Tab laden"), key="load_from_input_tab_btn"):
            if 'project_data' in st.session_state:
                st.session_state['crm_temp_project_data'] = st.session_state['project_data']
                st.success(get_text_crm(texts, "crm_data_loaded_from_input", "Daten aus Eingabe-Tab geladen. Bitte unten prüfen und speichern."))
            else:
                st.warning(get_text_crm(texts, "crm_no_data_in_input_tab", "Keine Daten im Eingabe-Tab gefunden."))

        with st.form("project_form", clear_on_submit=False):
            project_data_form = st.session_state.get('crm_temp_project_data', project_to_edit)
            
            project_name = st.text_input(get_text_crm(texts, "crm_project_name_label", "Projektname"), value=project_data_form.get('project_name', ''))
            project_status = st.selectbox(get_text_crm(texts, "crm_project_status_label", "Status"), options=['Angebot', 'In Planung', 'Installiert', 'Abgeschlossen', 'Storniert', ''], index=['Angebot', 'In Planung', 'Installiert', 'Abgeschlossen', 'Storniert', ''].index(project_data_form.get('project_status', '')))

            st.subheader(get_text_crm(texts, "crm_general_project_details_header", "Allgemeine Projektdetails"))
            col_roof_type, col_roof_covering = st.columns(2)
            roof_type = col_roof_type.selectbox(get_text_crm(texts, "roof_type_label", "Dachart"), options=['Satteldach', 'Flachdach', 'Sonstiges', ''], index=['Satteldach', 'Flachdach', 'Sonstiges', ''].index(project_data_form.get('roof_type', '')))
            roof_covering_type = col_roof_covering.selectbox(get_text_crm(texts, "roof_covering_label", "Dachdeckungsart"), options=['Ziegel', 'Blech', 'Bitumen', ''], index=['Ziegel', 'Blech', 'Bitumen', ''].index(project_data_form.get('roof_covering_type', '')))
            
            col_roof_area, col_orientation = st.columns(2)
            free_roof_area_sqm = col_roof_area.number_input(get_text_crm(texts, "free_roof_area_label", "Freie Dachfläche (m²)"), min_value=0.0, value=float(project_data_form.get('free_roof_area_sqm', 0.0)))
            roof_orientation = col_orientation.selectbox(get_text_crm(texts, "roof_orientation_label", "Dachausrichtung"), options=['Süd', 'Ost', 'West', 'Nord', ''], index=['Süd', 'Ost', 'West', 'Nord', ''].index(project_data_form.get('roof_orientation', '')))
            
            roof_inclination_deg = st.number_input(get_text_crm(texts, "roof_inclination_label", "Dachneigung (Grad)"), min_value=0, max_value=90, value=int(project_data_form.get('roof_inclination_deg', 30)))
            building_height_gt_7m = st.checkbox(get_text_crm(texts, "building_height_gt_7m_label", "Gebäudehöhe > 7 Meter"), value=bool(project_data_form.get('building_height_gt_7m', False)))

            st.subheader(get_text_crm(texts, "crm_consumption_details_header", "Verbrauchsdetails"))
            col_cons_hh, col_costs_hh = st.columns(2)
            annual_consumption_kwh = col_cons_hh.number_input(get_text_crm(texts, "annual_consumption_kwh_label", "Jahresverbrauch Haushalt (kWh)"), min_value=0.0, value=float(project_data_form.get('annual_consumption_kwh_yr', 0.0)))
            costs_household_euro_mo = col_costs_hh.number_input(get_text_crm(texts, "monthly_costs_household_label", "Monatliche Kosten Haushalt (€)"), min_value=0.0, value=float(project_data_form.get('costs_household_euro_mo', 0.0)))
            
            col_cons_heat, col_costs_heat = st.columns(2)
            annual_heating_kwh = col_cons_heat.number_input(get_text_crm(texts, "annual_heating_kwh_optional_label", "Jahresverbrauch Heizung (kWh, optional)"), min_value=0.0, value=float(project_data_form.get('consumption_heating_kwh_yr', 0.0)))
            costs_heating_euro_mo = col_cons_heat.number_input(get_text_crm(texts, "monthly_costs_heating_optional_label", "Monatliche Kosten Heizung (€, optional)"), min_value=0.0, value=float(project_data_form.get('costs_heating_euro_mo', 0.0)))

            st.subheader(get_text_crm(texts, "crm_system_details_header", "Systemdetails"))
            anlage_type = st.selectbox(get_text_crm(texts, "anlage_type_label", "Anlagentyp"), options=['Neuanlage', 'Bestandsanlage', ''], index=['Neuanlage', 'Bestandsanlage', ''].index(project_data_form.get('anlage_type', '')))
            feed_in_type = st.selectbox(get_text_crm(texts, "feed_in_type_label", "Einspeisetyp"), options=['Teileinspeisung', 'Volleinspeisung', ''], index=['Teileinspeisung', 'Volleinspeisung', ''].index(project_data_form.get('feed_in_type', '')))

            col_modules, col_inverter = st.columns(2)
            module_quantity = col_modules.number_input(get_text_crm(texts, "module_quantity_label", "Anzahl PV Module"), min_value=0, value=int(project_data_form.get('module_quantity', 0)))
            
            module_products = []
            if 'product_db_module' in st.session_state and st.session_state.product_db_module:
                 module_products = st.session_state.product_db_module.list_products(category='Modul')
            module_options = [get_text_crm(texts, "please_select_option", "--- Bitte wählen ---")] + [p['model_name'] for p in module_products if p.get('model_name')]
            
            selected_module_name = col_inverter.selectbox(get_text_crm(texts, "module_model_label", "PV Modul Modell"), options=module_options, index=module_options.index(project_data_form.get('selected_module_name', get_text_crm(texts, "please_select_option", "--- Bitte wählen ---"))))
            selected_module_id = next((p['id'] for p in module_products if p['model_name'] == selected_module_name), None)
            
            inverter_products = []
            if 'product_db_module' in st.session_state and st.session_state.product_db_module:
                inverter_products = st.session_state.product_db_module.list_products(category='Wechselrichter')
            inverter_options = [get_text_crm(texts, "please_select_option", "--- Bitte wählen ---")] + [p['model_name'] for p in inverter_products if p.get('model_name')]
            
            selected_inverter_name = st.selectbox(get_text_crm(texts, "inverter_model_label", "Wechselrichter Modell"), options=inverter_options, index=inverter_options.index(project_data_form.get('selected_inverter_name', get_text_crm(texts, "please_select_option", "--- Bitte wählen ---"))))
            selected_inverter_id = next((p['id'] for p in inverter_products if p['model_name'] == selected_inverter_name), None)

            include_storage = st.checkbox(get_text_crm(texts, "include_storage_label", "Batteriespeicher einplanen"), value=bool(project_data_form.get('include_storage', False)))
            selected_storage_id = None
            selected_storage_storage_power_kw = 0.0

            if include_storage:
                storage_products = []
                if 'product_db_module' in st.session_state and st.session_state.product_db_module:
                    storage_products = st.session_state.product_db_module.list_products(category='Batteriespeicher')
                storage_options = [get_text_crm(texts, "please_select_option", "--- Bitte wählen ---")] + [p['model_name'] for p in storage_products if p.get('model_name')]

                selected_storage_name = st.selectbox(get_text_crm(texts, "storage_model_label", "Speicher Modell"), options=storage_options, index=storage_options.index(project_data_form.get('selected_storage_name', get_text_crm(texts, "please_select_option", "--- Bitte wählen ---"))))
                selected_storage_id = next((p['id'] for p in storage_products if p['model_name'] == selected_storage_name), None)
                
                selected_storage_storage_power_kw = st.number_input(get_text_crm(texts, "storage_capacity_manual_label", "Gewünschte Gesamtkapazität (kWh)"), min_value=0.0, value=float(project_data_form.get('selected_storage_storage_power_kw', 0.0)))
            
            include_additional_components = st.checkbox(get_text_crm(texts, "include_additional_components_label", "Zusätzliche Komponenten einplanen"), value=bool(project_data_form.get('include_additional_components', False)))

            selected_wallbox_id = None
            selected_ems_id = None
            selected_optimizer_id = None
            selected_carport_id = None
            selected_notstrom_id = None
            selected_tierabwehr_id = None

            if include_additional_components:
                st.info(get_text_crm(texts, "crm_additional_components_placeholder", "Zusätzliche Komponenten können hier ausgewählt werden (Platzhalter)."))

            visualize_roof_in_pdf = st.checkbox(get_text_crm(texts, "visualize_roof_in_pdf_label", "Dachbelegung in PDF visualisieren (Luftbild)"), value=bool(project_data_form.get('visualize_roof_in_pdf', False)))
            latitude = st.number_input(get_text_crm(texts, "latitude_label", "Breitengrad"), value=float(project_data_form.get('latitude', 0.0)))
            longitude = st.number_input(get_text_crm(texts, "longitude_label", "Längengrad"), value=float(project_data_form.get('longitude', 0.0)))

            submitted_project = st.form_submit_button(get_text_crm(texts, "crm_save_project_button", "Projekt speichern"))
            if submitted_project:
                new_project_data = {
                    'id': project_to_edit.get('id'),
                    'customer_id': selected_customer_id,
                    'project_name': project_name,
                    'project_status': project_status if project_status else None,
                    'roof_type': roof_type if roof_type else None,
                    'roof_covering_type': roof_covering_type if roof_covering_type else None,
                    'free_roof_area_sqm': free_roof_area_sqm,
                    'roof_orientation': roof_orientation if roof_orientation else None,
                    'roof_inclination_deg': roof_inclination_deg,
                    'building_height_gt_7m': int(building_height_gt_7m),
                    'annual_consumption_kwh': annual_consumption_kwh,
                    'costs_household_euro_mo': costs_household_euro_mo,
                    'annual_heating_kwh': annual_heating_kwh,
                    'costs_heating_euro_mo': costs_heating_euro_mo,
                    'anlage_type': anlage_type if anlage_type else None,
                    'feed_in_type': feed_in_type if feed_in_type else None,
                    'module_quantity': module_quantity,
                    'selected_module_id': selected_module_id,
                    'selected_inverter_id': selected_inverter_id,
                    'include_storage': int(include_storage),
                    'selected_storage_id': selected_storage_id,
                    'selected_storage_storage_power_kw': selected_storage_storage_power_kw,
                    'include_additional_components': int(include_additional_components),
                    'selected_wallbox_id': selected_wallbox_id,
                    'selected_ems_id': selected_ems_id,
                    'selected_optimizer_id': selected_optimizer_id,
                    'selected_carport_id': selected_carport_id,
                    'selected_notstrom_id': selected_notstrom_id,
                    'selected_tierabwehr_id': selected_tierabwehr_id,
                    'visualize_roof_in_pdf': int(visualize_roof_in_pdf),
                    'latitude': latitude,
                    'longitude': longitude,
                    'creation_date': project_to_edit.get('creation_date', datetime.now().isoformat())
                }

                if not project_name:
                    st.error(get_text_crm(texts, "crm_project_name_required_error", "Projektname ist ein Pflichtfeld."))
                else:
                    saved_project_id = save_project(conn, new_project_data)
                    if saved_project_id:
                        st.success(get_text_crm(texts, "crm_project_saved", "Projekt erfolgreich gespeichert!"))
                        st.session_state['crm_view_mode'] = 'view_customer'
                        st.session_state['selected_project_id'] = saved_project_id
                        st.rerun()
                    else:
                        st.error(get_text_crm(texts, "crm_project_save_failed", "Fehler beim Speichern des Projekts."))
            
            if st.form_submit_button(get_text_crm(texts, "crm_cancel_button", "Abbrechen")):
                st.session_state['crm_view_mode'] = 'view_customer'
                st.session_state['selected_project_id'] = None
                st.rerun()

    elif view_mode == 'view_project':
        if selected_customer_id is None:
            st.error(get_text_crm(texts, "crm_no_customer_selected", "Kein Kunde ausgewählt."))
            if st.button(get_text_crm(texts, "crm_back_to_list_button", "Zurück zur Kundenliste")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.rerun()
            return

        current_customer = load_customer(conn, selected_customer_id)
        if not current_customer:
            st.error(get_text_crm(texts, "crm_customer_not_found", "Kunde nicht gefunden."))
            if st.button(get_text_crm(texts, "crm_back_to_list_button", "Zurück zur Kundenliste")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.rerun()
            return

        if selected_project_id is None:
            st.error(get_text_crm(texts, "crm_no_project_selected", "Kein Projekt ausgewählt."))
            if st.button(get_text_crm(texts, "crm_back_to_list_button", "Zurück zur Kundenliste")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.rerun()
            return

        project_details = load_project(conn, selected_project_id)
        if not project_details:
            st.error(get_text_crm(texts, "crm_project_not_found", "Projekt nicht gefunden."))
            if st.button(get_text_crm(texts, "crm_back_to_list_button", "Zurück zur Kundenliste")):
                st.session_state['crm_view_mode'] = 'customer_list'
                st.rerun()
            return

        st.subheader(get_text_crm(texts, "crm_project_details_header", "Projektdetails"))
        st.write(f"**{get_text_crm(texts, 'crm_project_name_label', 'Projektname')}:** {project_details.get('project_name', '')}")
        st.write(f"**{get_text_crm(texts, 'crm_project_status_label', 'Status')}:** {project_details.get('project_status', '')}")
        st.write(f"**{get_text_crm(texts, 'anlage_type_label', 'Anlagentyp')}:** {project_details.get('anlage_type', '')}")
        st.write(f"**{get_text_crm(texts, 'feed_in_type_label', 'Einspeisetyp')}:** {project_details.get('feed_in_type', '')}")
        st.write(f"**{get_text_crm(texts, 'module_quantity_label', 'Anzahl PV Module')}:** {project_details.get('module_quantity', '')}")
        st.write(f"**{get_text_crm(texts, 'module_model_label', 'PV Modul Modell')}:** {project_details.get('selected_module_name', 'N/A')}")
        st.write(f"**{get_text_crm(texts, 'inverter_model_label', 'Wechselrichter Modell')}:** {project_details.get('selected_inverter_name', 'N/A')}")
        st.write(f"**{get_text_crm(texts, 'include_storage_label', 'Speicher eingeplant')}:** {'Ja' if project_details.get('include_storage') else 'Nein'}")
        if project_details.get('include_storage'):
            st.write(f"**{get_text_crm(texts, 'storage_model_label', 'Speicher Modell')}:** {project_details.get('selected_storage_name', 'N/A')}")
            st.write(f"**{get_text_crm(texts, 'storage_capacity_manual_label', 'Speicherkapazität')}:** {project_details.get('selected_storage_storage_power_kw', 0.0)} kWh")
        
        st.write(f"**{get_text_crm(texts, "visualize_roof_in_pdf_label", "Dachvisualisierung in PDF")}:** {'Ja' if project_details.get('visualize_roof_in_pdf') else 'Nein'}")
        st.write(f"**{get_text_crm(texts, "latitude_label", "Breitengrad")}:** {project_details.get('latitude', 'N/A')}")
        st.write(f"**{get_text_crm(texts, "longitude_label", "Längengrad")}:** {project_details.get('longitude', 'N/A')}")


        col_view_p_buttons = st.columns(3)
        if col_view_p_buttons[0].button(get_text_crm(texts, "crm_edit_project_button", "Projekt bearbeiten"), key=f"edit_project_btn_view_{selected_project_id}"):
            st.session_state['crm_view_mode'] = 'edit_project'
            st.rerun()
        if col_view_p_buttons[1].button(get_text_crm(texts, "crm_delete_button", "Projekt löschen"), key=f"delete_project_btn_view_{selected_project_id}"):
            if st.session_state.get(f"confirm_delete_project_view_{selected_project_id}", False):
                if delete_project(conn, selected_project_id):
                    st.success(get_text_crm(texts, "crm_project_deleted", "Projekt gelöscht."))
                    st.session_state['crm_view_mode'] = 'view_customer'
                    st.session_state['selected_project_id'] = None
                    del st.session_state[f"confirm_delete_project_view_{selected_project_id}"]
                    st.rerun()
                else:
                    st.error(get_text_crm(texts, "crm_delete_project_failed", "Löschen fehlgeschlagen."))
            else:
                st.warning(get_text_crm(texts, "crm_confirm_delete_project", "Sicher? Klick nochmal zum Bestätigen."))
                st.session_state[f"confirm_delete_project_view_{selected_project_id}"] = True
        
        if st.button(get_text_crm(texts, "crm_back_to_customer_projects_button", "Zurück zu Kundenprojekten"), key="back_from_project_details"):
            st.session_state['crm_view_mode'] = 'customer_list'
            st.session_state['selected_customer_id'] = None
            st.session_state['selected_project_id'] = None
            st.rerun()


    conn.close()

# --- Testlauf für crm.py ---
if __name__ == "__main__":
    print("--- Testlauf für crm.py ---")
    
    class MockDatabase:
        def get_db_connection(self):
            conn = sqlite3.connect(':memory:')
            conn.row_factory = sqlite3.Row
            create_tables_crm(conn) # Erstelle die Tabellen und migriere
            return conn

    class MockAdminSettings:
        def load_admin_setting(self, key, default=None):
            if key == 'salutation_options': return ['Herr', 'Frau', 'Familie', 'Divers']
            if key == 'title_options': return ['Dr.', 'Prof.', 'Mag.', 'Ing.', None]
            return default

    class MockProductDB:
        def list_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
            if category == 'Modul':
                return [{'id': 1, 'model_name': 'TestModul 400Wp', 'category': 'Modul'}, {'id': 2, 'model_name': 'SuperModul 450Wp', 'category': 'Modul'}]
            elif category == 'Wechselrichter':
                return [{'id': 3, 'model_name': 'WR PowerInverter 10kW', 'category': 'Wechselrichter'}]
            elif category == 'Batteriespeicher':
                return [{'id': 4, 'model_name': 'BatteryStore 10kWh', 'category': 'Batteriespeicher'}]
            return []
        
        def get_product_by_model_name(self, model_name: str) -> Optional[Dict[str, Any]]:
            if "TestModul" in model_name:
                return {'id': 1, 'model_name': 'TestModul 400Wp', 'category': 'Modul', 'capacity_w': 400.0, 'length_m': 1.7, 'width_m': 1.0}
            if "WR PowerInverter" in model_name:
                return {'id': 3, 'model_name': 'WR PowerInverter 10kW', 'category': 'Wechselrichter', 'power_kw': 10.0}
            if "BatteryStore" in model_name:
                return {'id': 4, 'model_name': 'BatteryStore 10kWh', 'category': 'Batteriespeicher', 'storage_power_kw': 10.0}
            return None
        
        def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
            if product_id == 1:
                return {'id': 1, 'model_name': 'TestModul 400Wp', 'category': 'Modul', 'capacity_w': 400.0, 'length_m': 1.7, 'width_m': 1.0}
            return None

    _original_get_db_connection_safe_crm = get_db_connection_safe_crm
    get_product_by_model_name_safe = None
    _original_get_product_by_model_name_safe = get_product_by_model_name_safe
    load_admin_setting_safe = None
    _original_load_admin_setting_safe = load_admin_setting_safe
    list_products_safe = None
    _original_list_products_safe = list_products_safe

    mock_db = MockDatabase()
    get_db_connection_safe_crm = mock_db.get_db_connection
    load_admin_setting_safe = MockAdminSettings().load_admin_setting
    list_products_safe = MockProductDB().list_products
    get_product_by_model_name_safe = MockProductDB().get_product_by_model_name

    conn_test = get_db_connection_safe_crm()
    if conn_test:
        print("Datenbankverbindung im crm.py Test verfügbar.")
        
        dummy_texts_for_crm = {}

        print("\nTeste create_tables_crm...")
        create_tables_crm(conn_test)
        print("create_tables_crm abgeschlossen (keine Fehler erwartet).")

        print("\nTeste save_customer...")
        test_customer_data = {
            'salutation': 'Herr', 'first_name': 'Max', 'last_name': 'Mustermann',
            'email': 'max.mustermann@example.com', 'city': 'Musterstadt',
            'creation_date': datetime.now().isoformat()
        }
        test_customer_data['state'] = 'NRW'
        test_customer_data['region'] = 'West'
        test_customer_data['phone_landline'] = '02303-123456'
        test_customer_data['phone_mobile'] = '0176-98765432'
        test_customer_data['income_tax_rate_percent'] = 42.0

        customer_id = save_customer(conn_test, test_customer_data)
        print(f"Kunde gespeichert mit ID: {customer_id}")

        print("\nTeste load_customer...")
        if customer_id:
            loaded_customer = load_customer(conn_test, customer_id)
            print(f"Geladener Kunde: {loaded_customer}")
        
        print("\nTeste load_all_customers...")
        all_customers = load_all_customers(conn_test)
        print(f"Gefundene Kunden: {len(all_customers)}")
        for cust in all_customers:
            print(f" - {cust.get('first_name')} {cust.get('last_name')} (ID: {cust.get('id')})")

        print("\nTeste save_project...")
        if customer_id:
            test_project_data = {
                'customer_id': customer_id,
                'project_name': 'PV Anlage Musterhaus',
                'project_status': 'Angebot',
                'module_quantity': 20,
                'selected_module_id': 1,
                'selected_inverter_id': 3,
                'include_storage': 1,
                'selected_storage_id': 4,
                'selected_storage_storage_power_kw': 10.0,
                'visualize_roof_in_pdf': 1,
                'latitude': 52.5, 'longitude': 13.4,
                'creation_date': datetime.now().isoformat()
            }
            project_id = save_project(conn_test, test_project_data)
            print(f"Projekt gespeichert mit ID: {project_id}")

            print("\nTeste load_project...")
            if project_id:
                loaded_project = load_project(conn_test, project_id)
                print(f"Geladenes Projekt: {loaded_project}")

            print("\nTeste load_projects_for_customer...")
            projects_for_customer = load_projects_for_customer(conn_test, customer_id)
            print(f"Projekte für Kunde {customer_id}: {len(projects_for_customer)}")

            if project_id:
                print(f"\nTeste delete_project (ID: {project_id})...")
                if delete_project(conn_test, project_id):
                    print("Projekt erfolgreich gelöscht.")
                else:
                    print("Fehler beim Löschen des Projekts.")
            
        print(f"\nTeste delete_customer (ID: {customer_id})...")
        if delete_customer(conn_test, customer_id):
            print("Kunde erfolgreich gelöscht.")
        else:
            print("Fehler beim Löschen des Kunden.")

        conn_test.close()

    else:
         print("\nFEHLER: Keine Datenbankverbindung für Test verfügbar.")

    print("\n--- Testlauf beendet ---")