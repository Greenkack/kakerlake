#!/usr/bin/env python3
"""
VOLLSTÄNDIGES CRM-KUNDENMANAGEMENT SYSTEM
=========================================

Automatische Übernahme ALLER Daten aus der Bedarfsanalyse:
- Persönliche Kundendaten
- Verbrauchswerte & Gebäudedaten
- Berechnungsergebnisse
- Generierte PDFs
- Angebote & Preise
- Sondervereinbarungen

MIT EINEM KLICK → VOLLSTÄNDIG IM CRM!
"""

import streamlit as st
import sqlite3
import json
import base64
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import traceback
import pandas as pd

# Import bestehender Module
try:
    from database import get_db_connection
    from crm import create_tables_crm

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print(" Database Module nicht verfügbar - verwende Dummy-Funktionen")


class CompleteCRMSystem:
    """Vollständiges CRM-System für automatische Datenübernahme."""

    def __init__(self):
        self.init_database()

    def init_database(self):
        """Initialisiert die erweiterte CRM-Datenbank."""
        if not DATABASE_AVAILABLE:
            return

        try:
            conn = get_db_connection()
            if conn:
                self.create_extended_crm_tables(conn)
                conn.close()
                print(" CRM-Datenbank erfolgreich initialisiert")
        except Exception as e:
            print(f" CRM Database Init Error: {e}")
            # Versuche lokale SQLite-Datenbank zu erstellen
            self.create_fallback_database()

    def create_extended_crm_tables(self, conn: sqlite3.Connection):
        """Erstellt alle erweiterten CRM-Tabellen."""
        cursor = conn.cursor()

        # 1. ERWEITERTE KUNDENTABELLE
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- PERSÖNLICHE DATEN
                salutation TEXT,
                title TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                company_name TEXT,
                
                -- KONTAKTDATEN
                email TEXT UNIQUE,
                phone_landline TEXT,
                phone_mobile TEXT,
                
                -- ADRESSE
                street TEXT,
                house_number TEXT,
                zip_code TEXT,
                city TEXT,
                state TEXT,
                country TEXT DEFAULT 'Deutschland',
                
                -- ZUSÄTZLICHE INFOS
                income_tax_rate_percent REAL DEFAULT 42.0,
                notes TEXT,
                customer_type TEXT DEFAULT 'Privatkunde',
                lead_source TEXT,
                
                -- ZEITSTEMPEL
                creation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                
                -- STATUS
                status TEXT DEFAULT 'aktiv'
            )
        """
        )

        # 2. PROJEKTE MIT VOLLSTÄNDIGEN DATEN
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                
                -- PROJEKT BASICS
                project_name TEXT NOT NULL,
                project_status TEXT DEFAULT 'Bedarfsanalyse',
                priority TEXT DEFAULT 'normal',
                
                -- GEBÄUDEDATEN (AUS BEDARFSANALYSE)
                building_type TEXT,
                roof_type TEXT,
                roof_covering_type TEXT,
                roof_orientation TEXT,
                roof_angle REAL,
                free_roof_area_sqm REAL,
                building_age_years INTEGER,
                heating_type TEXT,
                has_heat_pump BOOLEAN DEFAULT 0,
                has_electric_car BOOLEAN DEFAULT 0,
                
                -- VERBRAUCHSDATEN
                annual_consumption_kwh REAL,
                monthly_consumption_data TEXT, -- JSON Array
                electricity_price_ct_per_kwh REAL,
                feed_in_tariff_ct_per_kwh REAL,
                
                -- TECHNISCHE KONFIGURATION
                anlage_kwp REAL,
                module_quantity INTEGER,
                module_type TEXT,
                inverter_type TEXT,
                battery_capacity_kwh REAL,
                battery_type TEXT,
                
                -- FINANZIELLE DATEN
                total_investment_eur REAL,
                final_cost_eur REAL,
                financing_type TEXT,
                down_payment_eur REAL,
                loan_amount_eur REAL,
                loan_interest_rate REAL,
                loan_duration_years INTEGER,
                
                -- BERECHNUNGSERGEBNISSE
                annual_pv_production_kwh REAL,
                self_consumption_percent REAL,
                independence_degree_percent REAL,
                payback_period_years REAL,
                total_savings_20_years_eur REAL,
                co2_savings_tons_20_years REAL,
                
                -- SONDERVEREINBARUNGEN
                special_agreements TEXT, -- JSON
                discount_percent REAL DEFAULT 0.0,
                additional_services TEXT, -- JSON
                
                -- VOLLSTÄNDIGE DATEN (JSON)
                complete_project_data TEXT, -- Vollständige project_data als JSON
                complete_analysis_results TEXT, -- Vollständige analysis_results als JSON
                
                -- ZEITSTEMPEL
                creation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (customer_id) REFERENCES crm_customers (id)
            )
        """
        )

        # 3. ANGEBOTE & PDFs
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                
                -- ANGEBOTS-DETAILS
                offer_number TEXT UNIQUE,
                offer_title TEXT,
                offer_status TEXT DEFAULT 'erstellt',
                offer_valid_until TEXT,
                
                -- PREISE
                gross_price_eur REAL,
                net_price_eur REAL,
                vat_amount_eur REAL,
                discount_amount_eur REAL DEFAULT 0.0,
                
                -- PDF DATEN
                pdf_data BLOB, -- PDF als Binärdaten
                pdf_filename TEXT,
                pdf_size_bytes INTEGER,
                pdf_pages INTEGER,
                
                -- ZUSÄTZLICHE INFOS
                offer_type TEXT DEFAULT 'standard',
                notes TEXT,
                
                -- ZEITSTEMPEL  
                creation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_date TEXT,
                accepted_date TEXT,
                
                FOREIGN KEY (customer_id) REFERENCES crm_customers (id),
                FOREIGN KEY (project_id) REFERENCES crm_projects (id)
            )
        """
        )

        # 4. AKTIVITÄTEN & KOMMUNIKATION
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                
                -- AKTIVITÄTS-DETAILS
                activity_type TEXT NOT NULL, -- 'bedarfsanalyse', 'angebot_erstelt', 'telefon', 'email', etc.
                title TEXT NOT NULL,
                description TEXT,
                
                -- ERGEBNIS/STATUS
                outcome TEXT,
                follow_up_required BOOLEAN DEFAULT 0,
                follow_up_date TEXT,
                
                -- ZEITSTEMPEL
                activity_date TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'System',
                
                FOREIGN KEY (customer_id) REFERENCES crm_customers (id),
                FOREIGN KEY (project_id) REFERENCES crm_projects (id)
            )
        """
        )

        # 5. DOKUMENTE & DATEIEN
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                offer_id INTEGER,
                
                -- DOKUMENT-DETAILS
                document_type TEXT NOT NULL, -- 'pdf_angebot', 'berechnung', 'foto', etc.
                filename TEXT NOT NULL,
                file_data BLOB,
                file_size_bytes INTEGER,
                mime_type TEXT,
                
                -- METADATEN
                description TEXT,
                tags TEXT, -- JSON Array
                is_public BOOLEAN DEFAULT 0,
                
                -- ZEITSTEMPEL
                upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (customer_id) REFERENCES crm_customers (id),
                FOREIGN KEY (project_id) REFERENCES crm_projects (id),
                FOREIGN KEY (offer_id) REFERENCES crm_offers (id)
            )
        """
        )

        conn.commit()
        print(" Erweiterte CRM-Tabellen erstellt")

    def create_fallback_database(self):
        """Erstellt eine lokale SQLite-Datenbank als Fallback."""
        try:
            import sqlite3

            db_path = os.path.join(os.getcwd(), "crm_database.db")
            conn = sqlite3.connect(db_path)
            print(f" Erstelle lokale CRM-Datenbank: {db_path}")

            self.create_extended_crm_tables(conn)
            conn.close()

            print(" Lokale CRM-Datenbank erfolgreich erstellt")

            # Aktualisiere get_db_connection für lokale DB
            global get_db_connection

            def local_db_connection():
                return sqlite3.connect(db_path)

            get_db_connection = local_db_connection

        except Exception as e:
            print(f" Fallback-Datenbank Fehler: {e}")

    def ensure_tables_exist(self):
        """Stellt sicher, dass alle CRM-Tabellen existieren."""
        try:
            conn = get_db_connection()
            if not conn:
                print(" Keine Datenbankverbindung verfügbar")
                return False

            cursor = conn.cursor()

            # Prüfe ob crm_customers Tabelle existiert
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='crm_customers'
            """
            )

            if not cursor.fetchone():
                print(" CRM-Tabellen fehlen - erstelle sie jetzt...")
                self.create_extended_crm_tables(conn)

            conn.close()
            return True

        except Exception as e:
            print(f" Fehler beim Prüfen der Tabellen: {e}")
            return False

    def save_complete_customer_data(
        self,
        project_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        pdf_bytes: Optional[bytes] = None,
        additional_notes: str = "",
    ) -> Tuple[int, int, int]:
        """
        Speichert ALLE Kundendaten aus der Bedarfsanalyse ins CRM.

        Returns:
            Tuple[customer_id, project_id, offer_id]
        """
        if not DATABASE_AVAILABLE:
            st.error(" Datenbank nicht verfügbar!")
            return None, None, None

        # Stelle sicher, dass Tabellen existieren
        if not self.ensure_tables_exist():
            st.error(" CRM-Tabellen konnten nicht erstellt werden!")
            return None, None, None

        try:
            conn = get_safe_db_connection()
            if not conn:
                st.error(" Keine Datenbankverbindung möglich!")
                return None, None, None

            cursor = conn.cursor()

            # 1. KUNDENDATEN EXTRAHIEREN UND SPEICHERN
            customer_id = self._save_customer_data(
                cursor, project_data, additional_notes
            )

            # 2. PROJEKTDATEN SPEICHERN
            project_id = self._save_project_data(
                cursor, customer_id, project_data, analysis_results
            )

            # 3. ANGEBOT SPEICHERN (wenn PDF vorhanden)
            offer_id = None
            if pdf_bytes:
                offer_id = self._save_offer_data(
                    cursor, customer_id, project_id, analysis_results, pdf_bytes
                )

            # 4. AKTIVITÄT PROTOKOLLIEREN
            self._log_activity(
                cursor,
                customer_id,
                project_id,
                "bedarfsanalyse_komplett",
                "Vollständige Bedarfsanalyse und Datenübernahme ins CRM",
            )

            conn.commit()
            conn.close()

            return customer_id, project_id, offer_id

        except Exception as e:
            st.error(f" Fehler beim Speichern: {e}")
            traceback.print_exc()
            return None, None, None

    def _save_customer_data(
        self, cursor: sqlite3.Cursor, project_data: Dict[str, Any], notes: str
    ) -> int:
        """Speichert/aktualisiert Kundendaten."""

        # Kundendaten aus project_data extrahieren
        customer_info = project_data.get("customer_data", {})
        address_info = customer_info.get("address", {})

        # E-Mail als eindeutiger Schlüssel
        email = customer_info.get("email", "").strip()

        if not email:
            raise ValueError("E-Mail-Adresse ist erforderlich für CRM-Speicherung!")

        # Prüfen ob Kunde bereits existiert
        cursor.execute("SELECT id FROM crm_customers WHERE email = ?", (email,))
        existing = cursor.fetchone()

        customer_data = {
            "salutation": customer_info.get("salutation", ""),
            "title": customer_info.get("title", ""),
            "first_name": customer_info.get("first_name", ""),
            "last_name": customer_info.get("last_name", ""),
            "company_name": customer_info.get("company_name", ""),
            "email": email,
            "phone_landline": customer_info.get("phone_landline", ""),
            "phone_mobile": customer_info.get("phone_mobile", ""),
            "street": address_info.get("street", ""),
            "house_number": address_info.get("house_number", ""),
            "zip_code": address_info.get("zip_code", ""),
            "city": address_info.get("city", ""),
            "state": address_info.get("state", ""),
            "income_tax_rate_percent": project_data.get(
                "income_tax_rate_percent", 42.0
            ),
            "notes": notes,
            "lead_source": "Bedarfsanalyse-Tool",
            "last_updated": datetime.now().isoformat(),
        }

        if existing:
            # UPDATE bestehender Kunde
            customer_id = existing[0]
            set_clause = ", ".join([f"{key} = ?" for key in customer_data.keys()])
            cursor.execute(
                f"UPDATE crm_customers SET {set_clause} WHERE id = ?",
                list(customer_data.values()) + [customer_id],
            )
        else:
            # INSERT neuer Kunde
            fields = ", ".join(customer_data.keys())
            placeholders = ", ".join(["?" for _ in customer_data])
            cursor.execute(
                f"INSERT INTO crm_customers ({fields}) VALUES ({placeholders})",
                list(customer_data.values()),
            )
            customer_id = cursor.lastrowid

        return customer_id

    def _save_project_data(
        self,
        cursor: sqlite3.Cursor,
        customer_id: int,
        project_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
    ) -> int:
        """Speichert vollständige Projektdaten."""

        building_data = project_data.get("building_data", {})
        consumption_data = project_data.get("consumption_data", {})

        project_info = {
            "customer_id": customer_id,
            "project_name": f"PV-Projekt {project_data.get('customer_data', {}).get('last_name', 'Kunde')}",
            "project_status": "Bedarfsanalyse abgeschlossen",
            # GEBÄUDEDATEN
            "building_type": building_data.get("building_type", ""),
            "roof_type": building_data.get("roof_type", ""),
            "roof_covering_type": building_data.get("roof_covering_type", ""),
            "roof_orientation": building_data.get("roof_orientation", ""),
            "roof_angle": building_data.get("roof_angle", 0),
            "free_roof_area_sqm": building_data.get("free_roof_area_sqm", 0),
            "building_age_years": building_data.get("building_age_years", 0),
            "heating_type": building_data.get("heating_type", ""),
            "has_heat_pump": 1 if building_data.get("has_heat_pump", False) else 0,
            "has_electric_car": (
                1 if building_data.get("has_electric_car", False) else 0
            ),
            # VERBRAUCHSDATEN
            "annual_consumption_kwh": consumption_data.get("annual_consumption_kwh", 0),
            "monthly_consumption_data": json.dumps(
                consumption_data.get("monthly_consumption", [])
            ),
            "electricity_price_ct_per_kwh": consumption_data.get(
                "electricity_price_ct_per_kwh", 30
            ),
            "feed_in_tariff_ct_per_kwh": consumption_data.get(
                "feed_in_tariff_ct_per_kwh", 8
            ),
            # TECHNISCHE KONFIGURATION
            "anlage_kwp": analysis_results.get("anlage_kwp", 0),
            "module_quantity": analysis_results.get("module_quantity", 0),
            "module_type": project_data.get("selected_modules", {}).get(
                "model_name", ""
            ),
            "inverter_type": project_data.get("selected_inverter", {}).get(
                "model_name", ""
            ),
            "battery_capacity_kwh": analysis_results.get("battery_capacity_kwh", 0),
            "battery_type": project_data.get("selected_battery", {}).get(
                "model_name", ""
            ),
            # FINANZIELLE DATEN
            "total_investment_eur": analysis_results.get("total_investment", 0),
            "final_cost_eur": analysis_results.get("final_cost", 0),
            "financing_type": project_data.get("financing_type", "Vollfinanzierung"),
            # BERECHNUNGSERGEBNISSE
            "annual_pv_production_kwh": analysis_results.get(
                "annual_pv_production_kwh", 0
            ),
            "self_consumption_percent": analysis_results.get(
                "self_consumption_percent", 0
            ),
            "independence_degree_percent": analysis_results.get(
                "independence_degree_percent", 0
            ),
            "payback_period_years": analysis_results.get("payback_period_years", 0),
            "total_savings_20_years_eur": analysis_results.get(
                "total_savings_20_years", 0
            ),
            "co2_savings_tons_20_years": analysis_results.get(
                "co2_savings_tons_20_years", 0
            ),
            # VOLLSTÄNDIGE DATEN ALS JSON
            "complete_project_data": json.dumps(
                project_data, ensure_ascii=False, indent=2
            ),
            "complete_analysis_results": json.dumps(
                analysis_results, ensure_ascii=False, indent=2
            ),
        }

        # INSERT Project
        fields = ", ".join(project_info.keys())
        placeholders = ", ".join(["?" for _ in project_info])
        cursor.execute(
            f"INSERT INTO crm_projects ({fields}) VALUES ({placeholders})",
            list(project_info.values()),
        )

        return cursor.lastrowid

    def _save_offer_data(
        self,
        cursor: sqlite3.Cursor,
        customer_id: int,
        project_id: int,
        analysis_results: Dict[str, Any],
        pdf_bytes: bytes,
    ) -> int:
        """Speichert Angebotsdaten und PDF."""

        offer_number = f"AN{datetime.now().strftime('%Y%m%d')}-{customer_id:04d}"

        offer_info = {
            "customer_id": customer_id,
            "project_id": project_id,
            "offer_number": offer_number,
            "offer_title": f"PV-Angebot {offer_number}",
            "offer_status": "erstellt",
            "gross_price_eur": analysis_results.get("final_cost", 0),
            "net_price_eur": analysis_results.get("final_cost_net", 0),
            "vat_amount_eur": analysis_results.get("vat_amount", 0),
            "pdf_data": pdf_bytes,
            "pdf_filename": f"{offer_number}.pdf",
            "pdf_size_bytes": len(pdf_bytes),
            "offer_type": "bedarfsanalyse",
        }

        fields = ", ".join(offer_info.keys())
        placeholders = ", ".join(["?" for _ in offer_info])
        cursor.execute(
            f"INSERT INTO crm_offers ({fields}) VALUES ({placeholders})",
            list(offer_info.values()),
        )

        return cursor.lastrowid

    def _log_activity(
        self,
        cursor: sqlite3.Cursor,
        customer_id: int,
        project_id: int,
        activity_type: str,
        description: str,
    ):
        """Protokolliert eine Aktivität."""

        cursor.execute(
            """
            INSERT INTO crm_activities (customer_id, project_id, activity_type, title, description)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                customer_id,
                project_id,
                activity_type,
                f"Automatisch: {activity_type.replace('_', ' ').title()}",
                description,
            ),
        )


def create_crm_save_button(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    pdf_bytes: Optional[bytes] = None,
) -> bool:
    """
    Erstellt einen 'Kunde ins CRM speichern' Button.

    Returns:
        bool: True wenn erfolgreich gespeichert
    """

    st.markdown("---")
    st.subheader(" CRM - Kundenmanagement")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            """
        **Alle Daten aus der Bedarfsanalyse ins CRM übernehmen:**
        -  Persönliche Kundendaten & Kontaktinfos
        -  Vollständige Gebäude- & Verbrauchsdaten  
        -  Alle Berechnungsergebnisse & Konfiguration
        -  Generierte PDF-Angebote
        -  Preise, Finanzierung & Sondervereinbarungen
        """
        )

        additional_notes = st.text_area(
            " Zusätzliche Notizen zum Kunden:",
            placeholder="z.B. Besondere Wünsche, Gesprächsnotizen, nächste Schritte...",
            height=100,
        )

    with col2:
        if st.button(
            " **KUNDE INS CRM SPEICHERN**", type="primary", use_container_width=True
        ):

            with st.spinner(" Speichere alle Daten ins CRM..."):
                crm_system = CompleteCRMSystem()

                customer_id, project_id, offer_id = (
                    crm_system.save_complete_customer_data(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        pdf_bytes=pdf_bytes,
                        additional_notes=additional_notes,
                    )
                )

                if customer_id:
                    st.success(
                        f"""
                     **ERFOLGREICH IM CRM GESPEICHERT!**
                    
                    -  **Kunde ID:** {customer_id}
                    -  **Projekt ID:** {project_id}  
                    -  **Angebot ID:** {offer_id if offer_id else 'Kein PDF verfügbar'}
                    
                    Alle Daten sind jetzt im CRM für die weitere Bearbeitung verfügbar!
                    """
                    )

                    # Erfolgs-Info in Session State speichern
                    st.session_state["crm_last_save"] = {
                        "timestamp": datetime.now().isoformat(),
                        "customer_id": customer_id,
                        "project_id": project_id,
                        "offer_id": offer_id,
                    }

                    return True
                else:
                    st.error(" Fehler beim Speichern ins CRM!")
                    return False

    # Zeige letzten Speichervorgang
    if "crm_last_save" in st.session_state:
        last_save = st.session_state["crm_last_save"]
        with st.expander(" Letzter CRM-Speichervorgang"):
            st.info(
                f"""
            **Zuletzt gespeichert:** {last_save['timestamp'][:19]}
            - Kunde ID: {last_save['customer_id']}
            - Projekt ID: {last_save['project_id']}
            - Angebot ID: {last_save.get('offer_id', 'N/A')}
            """
            )

    return False


def show_crm_customer_overview():
    """Zeigt eine Übersicht aller CRM-Kunden."""

    st.subheader(" CRM - Kundenübersicht")

    if not DATABASE_AVAILABLE:
        st.error(" Datenbank nicht verfügbar!")
        return

    # Initialisiere CRM-System und stelle sicher, dass Tabellen existieren
    crm_system = CompleteCRMSystem()
    if not crm_system.ensure_tables_exist():
        st.error(" CRM-Tabellen konnten nicht erstellt/überprüft werden!")
        return

    try:
        conn = get_safe_db_connection()
        if not conn:
            st.error(" Keine Datenbankverbindung möglich!")
            return

        # Lade Kundendaten - mit Fallback bei fehlenden Tabellen
        try:
            df_customers = pd.read_sql_query(
                """
                SELECT 
                    c.id,
                    COALESCE(c.first_name || ' ' || c.last_name, c.company_name, 'Unbekannt') as customer_name,
                    c.email,
                    c.phone_mobile,
                    c.city,
                    c.creation_date,
                    COUNT(DISTINCT p.id) as project_count,
                    COUNT(DISTINCT o.id) as offer_count
                FROM crm_customers c
                LEFT JOIN crm_projects p ON c.id = p.customer_id
                LEFT JOIN crm_offers o ON c.id = o.customer_id
                GROUP BY c.id, c.first_name, c.last_name, c.company_name, c.email, c.phone_mobile, c.city, c.creation_date
                ORDER BY c.creation_date DESC
            """,
                conn,
            )
        except Exception as sql_error:
            # Wenn Tabellen fehlen, erstelle sie
            st.warning(" CRM-Tabellen werden erstellt - bitte einen Moment...")
            crm_system.create_extended_crm_tables(conn)

            # Zeige Info, dass noch keine Daten vorhanden sind
            st.info(" CRM-System ist jetzt bereit! Noch keine Kunden gespeichert.")
            df_customers = pd.DataFrame(
                columns=[
                    "id",
                    "customer_name",
                    "email",
                    "phone_mobile",
                    "city",
                    "creation_date",
                    "project_count",
                    "offer_count",
                ]
            )

        if not df_customers.empty:
            st.dataframe(df_customers, use_container_width=True)

            # Kunde auswählen für Details
            selected_customer = st.selectbox(
                " Kunde für Details auswählen:",
                df_customers["customer_name"].tolist(),
            )

            if selected_customer:
                customer_id = df_customers[
                    df_customers["customer_name"] == selected_customer
                ]["id"].iloc[0]
                show_customer_details(conn, customer_id)
        else:
            st.info(" Noch keine Kunden im CRM vorhanden.")

        conn.close()

    except Exception as e:
        st.error(f" Fehler beim Laden der Kundendaten: {e}")


def show_customer_details(conn: sqlite3.Connection, customer_id: int):
    """Zeigt detaillierte Kundeninformationen."""

    with st.expander(f" Kunde Details (ID: {customer_id})", expanded=True):

        # Kundenstammdaten
        customer_data = pd.read_sql_query(
            "SELECT * FROM crm_customers WHERE id = ?", conn, params=(customer_id,)
        )

        if not customer_data.empty:
            customer = customer_data.iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("** Kontaktdaten:**")
                st.write(f"Name: {customer['first_name']} {customer['last_name']}")
                st.write(f"E-Mail: {customer['email']}")
                st.write(f"Telefon: {customer['phone_mobile']}")
                st.write(
                    f"Adresse: {customer['street']} {customer['house_number']}, {customer['zip_code']} {customer['city']}"
                )

            with col2:
                st.markdown("** Projekte:**")
                projects = pd.read_sql_query(
                    "SELECT * FROM crm_projects WHERE customer_id = ?",
                    conn,
                    params=(customer_id,),
                )

                if not projects.empty:
                    for _, project in projects.iterrows():
                        st.write(
                            f"• {project['project_name']} ({project['project_status']})"
                        )
                        st.write(f"  Anlage: {project['anlage_kwp']} kWp")
                        st.write(
                            f"  Investition: {project['total_investment_eur']:,.0f} €"
                        )

        # Angebote
        offers = pd.read_sql_query(
            "SELECT * FROM crm_offers WHERE customer_id = ?",
            conn,
            params=(customer_id,),
        )

        if not offers.empty:
            st.markdown("** Angebote:**")
            for _, offer in offers.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"• {offer['offer_number']} - {offer['offer_title']}")
                with col2:
                    st.write(f"{offer['gross_price_eur']:,.0f} €")
                with col3:
                    if offer["pdf_data"]:
                        st.download_button(
                            " PDF",
                            data=offer["pdf_data"],
                            file_name=offer["pdf_filename"],
                            mime="application/pdf",
                        )


# HAUPTFUNKTION FÜR INTEGRATION
def integrate_crm_into_main_app():
    """Integriert das CRM-System in die Hauptanwendung."""

    # Diese Funktion wird in der main GUI aufgerufen
    if "show_crm" not in st.session_state:
        st.session_state.show_crm = False

    if st.sidebar.button(" CRM Kundenübersicht"):
        st.session_state.show_crm = True

    if st.session_state.show_crm:
        show_crm_customer_overview()


def initialize_crm_system():
    """Initialisiert das CRM-System beim ersten Aufruf."""
    try:
        crm_system = CompleteCRMSystem()
        return True
    except Exception as e:
        print(f" CRM-Initialisierung fehlgeschlagen: {e}")
        return False


def get_safe_db_connection():
    """Sichere Datenbankverbindung mit Fallback."""
    try:
        if DATABASE_AVAILABLE:
            conn = get_db_connection()
            if conn:
                return conn

        # Fallback auf lokale SQLite
        import sqlite3

        db_path = os.path.join(os.getcwd(), "crm_database.db")
        return sqlite3.connect(db_path)

    except Exception as e:
        print(f" DB-Verbindung Fehler: {e}")
        return None


if __name__ == "__main__":
    st.set_page_config(page_title="CRM System Test", layout="wide")
    st.title(" Vollständiges CRM-System Test")

    # Test-Daten
    test_project_data = {
        "customer_data": {
            "salutation": "Herr",
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max.mustermann@email.de",
            "phone_mobile": "0171 1234567",
            "address": {
                "street": "Musterstraße",
                "house_number": "123",
                "zip_code": "12345",
                "city": "Musterstadt",
            },
        },
        "building_data": {
            "building_type": "Einfamilienhaus",
            "roof_type": "Satteldach",
            "roof_angle": 30,
            "free_roof_area_sqm": 50,
        },
        "consumption_data": {
            "annual_consumption_kwh": 4500,
            "electricity_price_ct_per_kwh": 32,
        },
    }

    test_analysis_results = {
        "anlage_kwp": 8.5,
        "final_cost": 25000,
        "annual_pv_production_kwh": 8500,
        "payback_period_years": 12,
    }

    # Test CRM Save Button
    create_crm_save_button(test_project_data, test_analysis_results)

    # Test Customer Overview
    show_crm_customer_overview()
