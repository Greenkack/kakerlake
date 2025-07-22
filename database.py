# database.py (Schema Version 13 - Spaltennamen und last_modified korrigiert)
import sqlite3
import os
import traceback
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import io

DB_SCHEMA_VERSION = 14
print(f"DATABASE.PY TOP LEVEL: DB_SCHEMA_VERSION ist auf {DB_SCHEMA_VERSION} gesetzt.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'app_data.db')

if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        print(f"DB: Datenverzeichnis '{DATA_DIR}' erstellt.")
    except OSError as e:
        print(f"DB: FEHLER beim Erstellen des Datenverzeichnisses '{DATA_DIR}': {e}")

INITIAL_ADMIN_SETTINGS: Dict[str, Any] = {
    "price_matrix_csv_data": None,
    "feed_in_tariffs": {
        "parts": [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 7.94},
            {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 6.88},
            {"kwp_min": 40.01, "kwp_max": 100.0, "ct_per_kwh": 5.62}
        ],
        "full": [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.60},
            {"kwp_min": 10.01, "kwp_max": 100.0, "ct_per_kwh": 10.56}
        ]
    },
    "global_constants": {
        'vat_rate_percent': 0.0, 'electricity_price_increase_annual_percent': 3.0,
        'simulation_period_years': 20, 'inflation_rate_percent': 2.0,
        'loan_interest_rate_percent': 4.0, 'capital_gains_tax_kest_percent': 26.375,
        'alternative_investment_interest_rate_percent': 5.0,
        'co2_emission_factor_kg_per_kwh': 0.474, 'maintenance_costs_base_percent': 1.5,
        'einspeiseverguetung_period_years': 20, 'marktwert_strom_eur_per_kwh_after_eeg': 0.03,
        'storage_cycles_per_year': 250, 'storage_efficiency': 0.90,
        'eauto_annual_km': 10000, 'eauto_consumption_kwh_per_100km': 18.0,
        'eauto_pv_share_percent': 30.0, 'heatpump_cop_factor': 3.5,
        'heatpump_pv_share_percent': 40.0, 'afa_period_years': 20,
        'pvgis_system_loss_default_percent': 14.0, 'annual_module_degradation_percent': 0.5,
        'maintenance_fixed_eur_pa': 50.0, 'maintenance_variable_eur_per_kwp_pa': 5.0,
        'maintenance_increase_percent_pa': 2.0, 'one_time_bonus_eur': 0.0,
        'global_yield_adjustment_percent': 0.0, 'default_specific_yield_kwh_kwp': 950.0,
        'reference_specific_yield_pr': 1100.0,
        'monthly_production_distribution': [0.03,0.05,0.08,0.11,0.13,0.14,0.13,0.12,0.09,0.06,0.04,0.02],
        'monthly_consumption_distribution': [0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0837],
        'direct_self_consumption_factor_of_production': 0.25, 'app_debug_mode_enabled': False,
        "visualization_settings": {
        "cost_overview_chart": { # Beispiel für das Kostenübersichtsdiagramm
            "chart_type": "bar",  # Mögliche Werte: "bar", "pie"
            "color_palette": "Plotly Standard", # Später erweiterbar auf Palettennamen oder spezifische Farben
            "primary_color_bar": "#1f77b4", # Beispiel für Balkendiagramm
            "show_values_on_chart": True
        },
        "consumption_coverage_chart": {
            "chart_type": "pie", # Mögliche Werte: "pie", "bar" (ggf. donut)
            "color_palette": "Pastel",
            "show_percentage": True,
            "show_labels": True
        },
        "pv_usage_chart": {
            "chart_type": "pie",
            "color_palette": "Grün-Variationen",
            "show_percentage": True
        },
        "monthly_prod_cons_chart": {
            "chart_type": "line", # Mögliche Werte: "line", "bar"
            "line_color_production": "#2ca02c", # Grün
            "line_color_consumption": "#d62728", # Rot
            "show_markers": True
        },
        "cumulative_cashflow_chart": {
            "chart_type": "line",
            "line_color": "#17becf", # Cyan
            "show_zero_line": True
        }
        # Hier können später Einstellungen für weitere Diagramme hinzugefügt werden
    },
    "pdf_design_settings": {"primary_color": "#003366", "secondary_color": "#808080"},
    "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],
        
    },
    "pdf_design_settings": {"primary_color": "#003366", "secondary_color": "#808080"},
    "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],
    "title_options": ['Dr.', 'Prof.', 'Mag.', 'Ing.', ''],
    'active_company_id': None
}

def get_db_connection() -> Optional[sqlite3.Connection]:
    try:
        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e: print(f"FATAL DB Error: {e}"); traceback.print_exc(); return None


def get_pdf_template_by_name(template_type: str, name: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: 
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pdf_templates WHERE template_type = ? AND name = ?", (template_type, name))
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"DB Fehler get_pdf_template_by_name: {e}")
        return None
    finally:
        if conn: 
            conn.close()

def backup_database(backup_path: str) -> bool:
    try:
        import shutil
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, backup_path)
            print(f"DB: Backup erfolgreich erstellt: {backup_path}")
            return True
        else:
            print(f"DB: Quelldatei {DB_PATH} existiert nicht für Backup.")
            return False
    except Exception as e:
        print(f"DB Fehler backup_database: {e}")
        return False

def restore_database(backup_path: str) -> bool:
    try:
        import shutil
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, DB_PATH)
            print(f"DB: Wiederherstellung erfolgreich von: {backup_path}")
            return True
        else:
            print(f"DB: Backup-Datei {backup_path} existiert nicht.")
            return False
    except Exception as e:
        print(f"DB Fehler restore_database: {e}")
        return False

def export_admin_settings() -> Dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM admin_settings")
        settings = {}
        for row in cursor.fetchall():
            key = row['key']
            value = row['value']
            if value and isinstance(value, str) and value.strip().startswith(('[', '{')) and value.strip().endswith((']', '}')):
                try:
                    settings[key] = json.loads(value)
                except json.JSONDecodeError:
                    settings[key] = value
            else:
                settings[key] = value
        return settings
    except Exception as e:
        print(f"DB Fehler export_admin_settings: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def import_admin_settings(settings: Dict[str, Any]) -> bool:
    success_count = 0
    total_count = len(settings)
    
    for key, value in settings.items():
        if save_admin_setting(key, value):
            success_count += 1
        else:
            print(f"DB: Fehler beim Importieren der Einstellung '{key}'")
    
    print(f"DB: Import abgeschlossen. {success_count}/{total_count} Einstellungen erfolgreich importiert.")
    return success_count == total_count

def get_database_statistics() -> Dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        return {}
    
    stats = {}
    try:
        cursor = conn.cursor()
        
        # Admin Settings Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM admin_settings")
        stats['admin_settings_count'] = cursor.fetchone()['count']
        
        # Products Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM products")
        stats['products_count'] = cursor.fetchone()['count']
        
        # Companies Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM companies")
        stats['companies_count'] = cursor.fetchone()['count']
        
        # Company Documents Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM company_documents")
        stats['company_documents_count'] = cursor.fetchone()['count']
        
        # PDF Templates Anzahl
        cursor.execute("SELECT COUNT(*) as count FROM pdf_templates")
        stats['pdf_templates_count'] = cursor.fetchone()['count']
        
        # Datenbankgröße
        if os.path.exists(DB_PATH):
            stats['database_size_mb'] = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)
        else:
            stats['database_size_mb'] = 0
        
        # Schema Version
        cursor.execute("PRAGMA user_version")
        stats['schema_version'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        print(f"DB Fehler get_database_statistics: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def validate_database_integrity() -> Dict[str, Any]:
    conn = get_db_connection()
    if not conn:
        return {"status": "error", "message": "Keine Datenbankverbindung möglich"}
    
    validation_results = {
        "status": "success",
        "errors": [],
        "warnings": [],
        "checks_performed": []
    }
    
    try:
        cursor = conn.cursor()
        
        # Check 1: PRAGMA integrity_check
        validation_results["checks_performed"].append("SQLite Integritätsprüfung")
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()
        if integrity_result[0] != "ok":
            validation_results["errors"].append(f"SQLite Integritätsprüfung fehlgeschlagen: {integrity_result[0]}")
            validation_results["status"] = "error"
        
        # Check 2: Überprüfung Foreign Key Constraints
        validation_results["checks_performed"].append("Foreign Key Constraints")
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            for violation in fk_violations:
                validation_results["errors"].append(f"Foreign Key Verletzung: {violation}")
            validation_results["status"] = "error"
        
        # Check 3: Verwaiste Company Documents
        validation_results["checks_performed"].append("Verwaiste Company Documents")
        cursor.execute("""
            SELECT cd.id, cd.display_name 
            FROM company_documents cd 
            LEFT JOIN companies c ON cd.company_id = c.id 
            WHERE c.id IS NULL
        """)
        orphaned_docs = cursor.fetchall()
        if orphaned_docs:
            for doc in orphaned_docs:
                validation_results["warnings"].append(f"Verwaistes Dokument: ID {doc['id']}, Name '{doc['display_name']}'")
        
        # Check 4: Duplikate in Produktnamen
        validation_results["checks_performed"].append("Produkt-Duplikate")
        cursor.execute("""
            SELECT model_name, COUNT(*) as count 
            FROM products 
            GROUP BY model_name 
            HAVING COUNT(*) > 1
        """)
        duplicate_products = cursor.fetchall()
        if duplicate_products:
            for dup in duplicate_products:
                validation_results["warnings"].append(f"Doppelter Produktname: '{dup['model_name']}' ({dup['count']}x)")
        
        # Check 5: Fehlende Standardfirma
        validation_results["checks_performed"].append("Standard-Firma")
        cursor.execute("SELECT COUNT(*) as count FROM companies WHERE is_default = 1")
        default_company_count = cursor.fetchone()['count']
        if default_company_count == 0:
            validation_results["warnings"].append("Keine Standard-Firma definiert")
        elif default_company_count > 1:
            validation_results["warnings"].append(f"Mehrere Standard-Firmen ({default_company_count}) definiert")
        
        if validation_results["errors"]:
            validation_results["status"] = "error"
        elif validation_results["warnings"]:
            validation_results["status"] = "warning"
        
        return validation_results
        
    except Exception as e:
        print(f"DB Fehler validate_database_integrity: {e}")
        return {
            "status": "error", 
            "message": f"Fehler bei der Validierung: {str(e)}",
            "errors": [str(e)],
            "warnings": [],
            "checks_performed": []
        }
    finally:
        if conn:
            conn.close()

# Hinzufügen zu database.py

def create_heat_pumps_table(conn):
    """Erstellt die Tabelle für Wärmepumpen, falls sie nicht existiert."""
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS heat_pumps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL UNIQUE,
                manufacturer TEXT,
                heating_output_kw REAL,
                power_consumption_kw REAL,
                scop REAL, -- Seasonal Coefficient of Performance
                price REAL
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Fehler beim Erstellen der heat_pumps-Tabelle: {e}")

def get_all_heat_pumps(conn):
    """Holt alle Wärmepumpen aus der Datenbank."""
    c = conn.cursor()
    c.execute("SELECT * FROM heat_pumps ORDER BY heating_output_kw")
    return c.fetchall()

def add_heat_pump(conn, data):
    """Fügt eine neue Wärmepumpe hinzu."""
    sql = ''' INSERT INTO heat_pumps(model_name, manufacturer, heating_output_kw, power_consumption_kw, scop, price)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid

def update_heat_pump(conn, data):
    """Aktualisiert eine Wärmepumpe."""
    sql = ''' UPDATE heat_pumps
              SET model_name = ?, manufacturer = ?, heating_output_kw = ?, power_consumption_kw = ?, scop = ?, price = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()

def delete_heat_pump(conn, id):
    """Löscht eine Wärmepumpe."""
    sql = 'DELETE FROM heat_pumps WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

# Stellen Sie sicher, dass create_heat_pumps_table() beim Initialisieren der DB aufgerufen wird.
# Beispiel im Haupt-DB-Initialisierungsblock:
# conn = create_connection(database_file)
# if conn is not None:
#     create_products_table(conn)
#     create_heat_pumps_table(conn) # HIER HINZUFÜGEN
#     ...

def cleanup_orphaned_files() -> Dict[str, Any]:
    cleanup_results = {
        "files_checked": 0,
        "files_removed": 0,
        "errors": [],
        "removed_files": []
    }
    
    try:
        # Company Documents Verzeichnis prüfen
        if not os.path.exists(COMPANY_DOCS_BASE_DIR):
            return cleanup_results
        
        # Alle Dateien in DB abrufen
        conn = get_db_connection()
        if not conn:
            cleanup_results["errors"].append("Keine Datenbankverbindung")
            return cleanup_results
        
        cursor = conn.cursor()
        cursor.execute("SELECT absolute_file_path FROM company_documents")
        db_files = set(row['absolute_file_path'] for row in cursor.fetchall())
        conn.close()
        
        # Alle physischen Dateien durchgehen
        for root, dirs, files in os.walk(COMPANY_DOCS_BASE_DIR):
            for file in files:
                cleanup_results["files_checked"] += 1
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, COMPANY_DOCS_BASE_DIR)
                
                if relative_path not in db_files:
                    try:
                        os.remove(full_path)
                        cleanup_results["files_removed"] += 1
                        cleanup_results["removed_files"].append(relative_path)
                        print(f"DB Cleanup: Verwaiste Datei entfernt: {relative_path}")
                    except Exception as e:
                        cleanup_results["errors"].append(f"Fehler beim Löschen von {relative_path}: {str(e)}")
        
        # Leere Verzeichnisse entfernen
        for root, dirs, files in os.walk(COMPANY_DOCS_BASE_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(f"DB Cleanup: Leeres Verzeichnis entfernt: {dir_path}")
                except Exception as e:
                    cleanup_results["errors"].append(f"Fehler beim Entfernen des Verzeichnisses {dir_path}: {str(e)}")
        
        return cleanup_results
        
    except Exception as e:
        cleanup_results["errors"].append(f"Allgemeiner Fehler beim Cleanup: {str(e)}")
        return cleanup_results

def reset_database() -> bool:
    try:
        # Datenbankdatei löschen
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"DB: Datenbankdatei {DB_PATH} gelöscht")
        
        # Company Documents Verzeichnis löschen
        if os.path.exists(COMPANY_DOCS_BASE_DIR):
            import shutil
            shutil.rmtree(COMPANY_DOCS_BASE_DIR)
            print(f"DB: Company Documents Verzeichnis {COMPANY_DOCS_BASE_DIR} gelöscht")
        
        # Datenbank neu initialisieren
        init_db()
        print("DB: Datenbank erfolgreich zurückgesetzt und neu initialisiert")
        return True
        
    except Exception as e:
        print(f"DB Fehler reset_database: {e}")
        return False# database.py (Schema Version 13 - Spaltennamen und last_modified korrigiert)
import sqlite3
import os
import traceback
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import io

DB_SCHEMA_VERSION = 13
print(f"DATABASE.PY TOP LEVEL: DB_SCHEMA_VERSION ist auf {DB_SCHEMA_VERSION} gesetzt.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'app_data.db')

if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
        print(f"DB: Datenverzeichnis '{DATA_DIR}' erstellt.")
    except OSError as e:
        print(f"DB: FEHLER beim Erstellen des Datenverzeichnisses '{DATA_DIR}': {e}")

INITIAL_ADMIN_SETTINGS: Dict[str, Any] = {
    "price_matrix_csv_data": None,
    "feed_in_tariffs": {
        "parts": [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 8.1},
            {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 7.0},
            {"kwp_min": 40.01, "kwp_max": 1000.0, "ct_per_kwh": 5.7}
        ],
        "full": [
            {"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.9},
            {"kwp_min": 10.01, "kwp_max": 100.0, "ct_per_kwh": 10.8}
        ]
    },
    "global_constants": {
        'vat_rate_percent': 0.0, 'electricity_price_increase_annual_percent': 3.0,
        'simulation_period_years': 20, 'inflation_rate_percent': 2.0,
        'loan_interest_rate_percent': 4.0, 'capital_gains_tax_kest_percent': 26.375,
        'alternative_investment_interest_rate_percent': 5.0,
        'co2_emission_factor_kg_per_kwh': 0.474, 'maintenance_costs_base_percent': 1.5,
        'einspeiseverguetung_period_years': 20, 'marktwert_strom_eur_per_kwh_after_eeg': 0.03,
        'storage_cycles_per_year': 250, 'storage_efficiency': 0.90,
        'eauto_annual_km': 10000, 'eauto_consumption_kwh_per_100km': 18.0,
        'eauto_pv_share_percent': 30.0, 'heatpump_cop_factor': 3.5,
        'heatpump_pv_share_percent': 40.0, 'afa_period_years': 20,
        'pvgis_system_loss_default_percent': 14.0, 'annual_module_degradation_percent': 0.5,
        'maintenance_fixed_eur_pa': 50.0, 'maintenance_variable_eur_per_kwp_pa': 5.0,
        'maintenance_increase_percent_pa': 2.0, 'one_time_bonus_eur': 0.0,
        'global_yield_adjustment_percent': 0.0, 'default_specific_yield_kwh_kwp': 950.0,
        'reference_specific_yield_pr': 1100.0,
        'monthly_production_distribution': [0.03,0.05,0.08,0.11,0.13,0.14,0.13,0.12,0.09,0.06,0.04,0.02],
        'monthly_consumption_distribution': [0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0837],
        'direct_self_consumption_factor_of_production': 0.25, 'app_debug_mode_enabled': False,
        "visualization_settings": {
        "cost_overview_chart": { # Beispiel für das Kostenübersichtsdiagramm
            "chart_type": "bar",  # Mögliche Werte: "bar", "pie"
            "color_palette": "Plotly Standard", # Später erweiterbar auf Palettennamen oder spezifische Farben
            "primary_color_bar": "#1f77b4", # Beispiel für Balkendiagramm
            "show_values_on_chart": True
        },
        "consumption_coverage_chart": {
            "chart_type": "pie", # Mögliche Werte: "pie", "bar" (ggf. donut)
            "color_palette": "Pastel",
            "show_percentage": True,
            "show_labels": True
        },
        "pv_usage_chart": {
            "chart_type": "pie",
            "color_palette": "Grün-Variationen",
            "show_percentage": True
        },
        "monthly_prod_cons_chart": {
            "chart_type": "line", # Mögliche Werte: "line", "bar"
            "line_color_production": "#2ca02c", # Grün
            "line_color_consumption": "#d62728", # Rot
            "show_markers": True
        },
        "cumulative_cashflow_chart": {
            "chart_type": "line",
            "line_color": "#17becf", # Cyan
            "show_zero_line": True
        }
        # Hier können später Einstellungen für weitere Diagramme hinzugefügt werden
    },
    "pdf_design_settings": {"primary_color": "#003366", "secondary_color": "#808080"},
    "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],
        
    },
    "pdf_design_settings": {"primary_color": "#003366", "secondary_color": "#808080"},
    "salutation_options": ['Herr', 'Frau', 'Familie', 'Firma', 'Divers'],
    "title_options": ['Dr.', 'Prof.', 'Mag.', 'Ing.', ''],
    'active_company_id': None
}

def _create_admin_settings_table_v1(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            last_modified TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("DB Schema: Tabelle 'admin_settings' v1 (mit last_modified) durch CREATE IF NOT EXISTS sichergestellt.")

def _create_products_table_v2(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, manufacturer TEXT,
            model_name TEXT NOT NULL UNIQUE, price_euro REAL, datasheet_link TEXT,
            description TEXT, technical_data TEXT, image_base64 TEXT,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP, last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            capacity_w REAL, storage_power_kw REAL, power_kw REAL, warranty_years INTEGER,
            length_m REAL, width_m REAL, weight_kg REAL, efficiency_percent REAL,
            origin_country TEXT, pros TEXT, cons TEXT, rating REAL,
            additional_cost_netto REAL DEFAULT 0.0, max_cycles INTEGER
        );""")
    print("DB Schema v2: Tabelle 'products' OK.")

def _create_companies_table_v12(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, logo_base64 TEXT,
            street TEXT, zip_code TEXT, city TEXT, phone TEXT, email TEXT, website TEXT,
            tax_id TEXT, commercial_register TEXT, bank_details TEXT, pdf_footer_text TEXT,
            is_default INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );""")
    print("DB Schema v12: Basisstruktur für Tabelle 'companies' OK (CREATE IF NOT EXISTS).")

def _create_company_documents_table_v12(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        document_type TEXT NOT NULL,
        display_name TEXT NOT NULL,
        file_name TEXT,
        absolute_file_path TEXT NOT NULL UNIQUE,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );
    """)
    print("DB Schema v12: Basisstruktur für Tabelle 'company_documents' OK (CREATE IF NOT EXISTS).")

def _create_pdf_templates_table_v13(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, template_type TEXT NOT NULL, name TEXT NOT NULL,
            content TEXT, image_data BLOB, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );""")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pdf_templates_type ON pdf_templates (template_type);")
    print("DB Schema v13: Tabelle 'pdf_templates' OK.")

def _create_company_templates_tables_v14(conn: sqlite3.Connection):
    """Erstellt Tabellen für firmenspezifische Angebotsvorlagen"""
    cursor = conn.cursor()
    
    # Tabelle für firmenspezifische Textvorlagen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_text_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            content TEXT,
            template_type TEXT NOT NULL DEFAULT 'offer_text',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_text_templates_company_id ON company_text_templates (company_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_text_templates_type ON company_text_templates (template_type);")
    
    # Tabelle für firmenspezifische Bildvorlagen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_image_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            template_type TEXT NOT NULL DEFAULT 'title_image',
            file_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_image_templates_company_id ON company_image_templates (company_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_image_templates_type ON company_image_templates (template_type);")
    
    print("DB Schema v14: Tabellen für firmenspezifische Vorlagen erstellt.")

def _ensure_column_exists(conn: sqlite3.Connection, table_name: str, column_name: str, column_type_for_alter: str, 
                          is_not_null_with_default_for_alter: bool = False, default_value_for_alter: str = "''"):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if column_name not in existing_columns:
        final_column_definition_for_alter = column_type_for_alter
        if is_not_null_with_default_for_alter:
            simple_type = column_type_for_alter.split()[0] 
            final_column_definition_for_alter = f"{simple_type} DEFAULT {default_value_for_alter}"
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {final_column_definition_for_alter};")
            print(f"DB: Spalte '{column_name}' ({final_column_definition_for_alter}) zu Tabelle '{table_name}' hinzugefügt via ALTER TABLE.")
            conn.commit()
        except sqlite3.OperationalError as e_alter:
            if "duplicate column name" in str(e_alter).lower():
                print(f"DB: Spalte '{column_name}' in '{table_name}' existiert bereits.")
            else:
                print(f"DB FEHLER beim Hinzufügen von Spalte '{column_name}' zu '{table_name}': {e_alter}")

def _add_company_id_to_products_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE;")
        print("DB Schema Update: Spalte 'company_id' zur Tabelle 'products' hinzugefügt.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Spalte 'company_id' existiert bereits in der Tabelle 'products'.")
        else:
            raise

def init_db():
    conn = get_db_connection()
    if conn is None: print("DB FEHLER: init_db() kann DB-Verbindung nicht herstellen."); return
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version;")
        current_db_version_row = cursor.fetchone()
        current_db_version = current_db_version_row[0] if current_db_version_row else 0
        print(f"DB: Aktuelle user_version: {current_db_version}, Ziel-Schema-Version: {DB_SCHEMA_VERSION}")

        if current_db_version < 1:
            _create_admin_settings_table_v1(conn)
            _ensure_column_exists(conn, "admin_settings", "last_modified", "TEXT")
            cursor.execute("UPDATE admin_settings SET value = '1' WHERE key = 'schema_version' OR key IS NULL;") 
            conn.commit() 
            current_db_version = 1; print("DB: Schema v1 angewendet.")
        elif current_db_version == 1:
             _ensure_column_exists(conn, "admin_settings", "last_modified", "TEXT")
        
        if current_db_version < 2:
            _create_products_table_v2(conn)
            cursor.execute("UPDATE admin_settings SET value = '2' WHERE key = 'schema_version';")
            conn.commit()
            current_db_version = 2; print("DB: Schema v2 angewendet.")

        if current_db_version < 12:
            _create_companies_table_v12(conn) 
            _create_company_documents_table_v12(conn)

            # --- Migration für 'companies' ---
            cursor.execute("PRAGMA table_info(companies);")
            companies_cols_info = {row[1]: row for row in cursor.fetchall()}

            if 'company_name' in companies_cols_info and 'name' not in companies_cols_info:
                try:
                    print("DB: Alte Spalte 'company_name' in 'companies' gefunden, 'name' fehlt. Versuche Umbenennung zu 'name'...")
                    cursor.execute("ALTER TABLE companies RENAME COLUMN company_name TO name;")
                    conn.commit() 
                    print("DB: Spalte 'company_name' erfolgreich zu 'name' in 'companies' umbenannt.")
                    cursor.execute("PRAGMA table_info(companies);") # Refresh
                    companies_cols_info = {row[1]: row for row in cursor.fetchall()}
                except sqlite3.OperationalError as e_rename_comp:
                    print(f"DB HINWEIS: Umbenennung von 'company_name' zu 'name' in 'companies' fehlgeschlagen: {e_rename_comp}.")
            
            _ensure_column_exists(conn, "companies", "name", "TEXT", is_not_null_with_default_for_alter=True, default_value_for_alter="''") # Sicherstellen, dass 'name' existiert
            _ensure_column_exists(conn, "companies", "is_default", "INTEGER", is_not_null_with_default_for_alter=True, default_value_for_alter="0")
            other_company_cols = ["logo_base64", "street", "zip_code", "city", "phone", "email", "website", "tax_id", "commercial_register", "bank_details", "pdf_footer_text", "created_at", "updated_at"]
            for col in other_company_cols:
                _ensure_column_exists(conn, "companies", col, "TEXT")
            
            # --- Migration für 'company_documents' ---
            cursor.execute("PRAGMA table_info(company_documents);")
            company_doc_cols_info = {row[1]: row for row in cursor.fetchall()}
            
            if 'document_name' in company_doc_cols_info and 'display_name' not in company_doc_cols_info:
                try:
                    print("DB: Alte Spalte 'document_name' in 'company_documents' gefunden, 'display_name' fehlt. Versuche Umbenennung...")
                    cursor.execute("ALTER TABLE company_documents RENAME COLUMN document_name TO display_name;")
                    conn.commit() 
                    print("DB: Spalte 'document_name' erfolgreich zu 'display_name' umbenannt.")
                    cursor.execute("PRAGMA table_info(company_documents);")
                    company_doc_cols_info = {row[1]: row for row in cursor.fetchall()}
                except sqlite3.OperationalError as e_rename_doc:
                    print(f"DB HINWEIS: Umbenennung von 'document_name' zu 'display_name' in 'company_documents' fehlgeschlagen: {e_rename_doc}.")
            
            _ensure_column_exists(conn, "company_documents", "display_name", "TEXT", is_not_null_with_default_for_alter=True, default_value_for_alter="''")
            _ensure_column_exists(conn, "company_documents", "file_name", "TEXT")
            _ensure_column_exists(conn, "company_documents", "absolute_file_path", "TEXT", is_not_null_with_default_for_alter=True, default_value_for_alter="''")

            cursor.execute("UPDATE admin_settings SET value = '12' WHERE key = 'schema_version';")
            conn.commit()
            current_db_version = 12
            print("DB: Schema v12 angewendet (inkl. spezifischer Migration für 'companies' & 'company_documents').")

        if current_db_version < 13:
            _create_pdf_templates_table_v13(conn)
            cursor.execute("UPDATE admin_settings SET value = '13' WHERE key = 'schema_version';")
            conn.commit()
            current_db_version = 13; print("DB: Schema v13 angewendet.")

        if current_db_version < 14:
            _create_company_templates_tables_v14(conn)
            cursor.execute("UPDATE admin_settings SET value = '14' WHERE key = 'schema_version';")
            conn.commit()
            current_db_version = 14; print("DB: Schema v14 angewendet (Firmenspezifische Angebotsvorlagen).")

        if current_db_version == DB_SCHEMA_VERSION: print("DB: Schema ist aktuell.")
        else: print(f"DB WARNUNG: Diskrepanz user_version ({current_db_version}) vs Code ({DB_SCHEMA_VERSION}).")

        for key, default_value in INITIAL_ADMIN_SETTINGS.items():
            cursor.execute("SELECT value FROM admin_settings WHERE key = ?", (key,))
            if cursor.fetchone() is None:
                value_insert = json.dumps(default_value) if isinstance(default_value, (dict, list)) else int(default_value) if isinstance(default_value, bool) else default_value
                if value_insert is None and key in ['price_matrix_csv_data', 'active_company_id']:
                     cursor.execute("INSERT INTO admin_settings (key, value, last_modified) VALUES (?, NULL, CURRENT_TIMESTAMP)", (key,))
                elif value_insert is not None:
                     cursor.execute("INSERT INTO admin_settings (key, value, last_modified) VALUES (?, ?, CURRENT_TIMESTAMP)", (key, value_insert))
                print(f"DB: Initiale Admin-Einstellung '{key}' hinzugefügt.")
        conn.commit(); print("DB: Initialisierung abgeschlossen.")
    except Exception as e: print(f"DB KRITISCHER FEHLER init_db: {e}"); traceback.print_exc(); conn.rollback()
    finally:
        if conn: conn.close()

def load_admin_setting(key: str, default: Any = None) -> Any:
    conn = get_db_connection()
    if conn is None: return default
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM admin_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row and row['value'] is not None:
            value_str = row['value']
            if isinstance(value_str, str) and value_str.strip().startswith(('[', '{')) and value_str.strip().endswith((']', '}')):
                try: return json.loads(value_str)
                except json.JSONDecodeError: pass
            if key in INITIAL_ADMIN_SETTINGS and isinstance(INITIAL_ADMIN_SETTINGS.get(key), bool):
                try: return bool(int(value_str))
                except: pass
            if key == 'active_company_id':
                try: return int(value_str) if value_str is not None else None
                except: return default
            return value_str
        if key == 'active_company_id' and row and row['value'] is None: return None
        return default
    except Exception as e: print(f"DB Fehler load_admin_setting '{key}': {e}"); return default
    finally:
        if conn: conn.close()

def save_admin_setting(key: str, value: Any) -> bool:
    conn = get_db_connection()
    if conn is None:
        print(f"DB FEHLER: save_admin_setting '{key}' - Keine DB-Verbindung.")
        return False
    try:
        cursor = conn.cursor()
        value_to_save = json.dumps(value) if isinstance(value, (dict, list)) else value
        if isinstance(value, bool):
            value_to_save = 1 if value else 0
        
        if key == 'price_matrix_csv_data' and value_to_save is not None:
            print(f"DB DEBUG: save_admin_setting - Länge von value_to_save für '{key}': {len(str(value_to_save))} Zeichen.")
            # print(f"DB DEBUG: save_admin_setting - Inhalt für '{key}' (erste 200 Zeichen): {str(value_to_save)[:200]}") # Bei Bedarf einkommentieren

        sql_query = """
        INSERT INTO admin_settings (key, value, last_modified) 
        VALUES (?, ?, CURRENT_TIMESTAMP) 
        ON CONFLICT(key) DO UPDATE SET 
        value=excluded.value, 
        last_modified=CURRENT_TIMESTAMP 
        """
        # Standardisierung der Einrückung, um mögliche Probleme zu beheben
        params_for_sql = (key, None if (value_to_save is None and key in ['active_company_id', 'price_matrix_csv_data']) else value_to_save)
        print(f"DB DEBUG: save_admin_setting - Versuche SQL auszuführen für Key '{key}'. Wert None? {params_for_sql[1] is None}")
        cursor.execute(sql_query, params_for_sql)
        conn.commit()
        print(f"DB ERFOLG: save_admin_setting - Einstellung '{key}' erfolgreich gespeichert.")
        return True
    except Exception as e: 
        print(f"DB FEHLER: save_admin_setting '{key}' - Exception: {e}")
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def add_pdf_template(template_type: str, name: str, content: Optional[str]=None, image_data: Optional[bytes]=None) -> Optional[int]:
    conn = get_db_connection()
    if not conn: return None
    now = datetime.now().isoformat()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pdf_templates (template_type, name, content, image_data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                       (template_type, name, content, image_data, now, now))
        conn.commit(); return cursor.lastrowid
    except Exception as e: print(f"DB Fehler add_pdf_template: {e}"); conn.rollback(); return None
    finally:
        if conn: conn.close()

def list_pdf_templates(template_type: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        if template_type:
            cursor.execute("SELECT * FROM pdf_templates WHERE template_type = ? ORDER BY name COLLATE NOCASE", (template_type,))
        else:
            cursor.execute("SELECT * FROM pdf_templates ORDER BY template_type, name COLLATE NOCASE")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e: print(f"DB Fehler list_pdf_templates: {e}"); return []
    finally:
        if conn: conn.close()

def get_pdf_template(template_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pdf_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone(); return dict(row) if row else None
    except Exception as e: print(f"DB Fehler get_pdf_template: {e}"); return None
    finally:
        if conn: conn.close()

def update_pdf_template(template_id: int, name: str, content: Optional[str]=None, image_data: Optional[bytes]=None) -> bool:
    conn = get_db_connection()
    if not conn: return False
    now = datetime.now().isoformat()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE pdf_templates SET name=?, content=?, image_data=?, updated_at=? WHERE id=?",
                       (name, content, image_data, now, template_id))
        conn.commit(); return cursor.rowcount > 0
    except Exception as e: print(f"DB Fehler update_pdf_template: {e}"); conn.rollback(); return False
    finally:
        if conn: conn.close()

def delete_pdf_template(template_id: int) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pdf_templates WHERE id = ?", (template_id,))
        conn.commit(); return cursor.rowcount > 0
    except Exception as e: print(f"DB Fehler delete_pdf_template: {e}"); conn.rollback(); return False
    finally:
        if conn: conn.close()

COMPANY_DOCS_BASE_DIR = os.path.join(DATA_DIR, "company_docs")
if not os.path.exists(COMPANY_DOCS_BASE_DIR):
    try: os.makedirs(COMPANY_DOCS_BASE_DIR)
    except OSError as e: print(f"DB FEHLER Erstellen Firmen-Doc-Verzeichnis: {e}")

def add_company(company_data: Dict[str, Any]) -> Optional[int]:
    conn = get_db_connection()
    if not conn: 
        print("DB FEHLER: add_company - Keine DB-Verbindung.")
        return None
    
    company_name_to_add = company_data.get("name")
    # print(f"DB DEBUG: add_company - Empfangene company_data['name']: '{company_name_to_add}'") # Bereits im Log

    if not company_name_to_add or not str(company_name_to_add).strip():
        print(f"DB FEHLER: Firmenname ist Pflicht und darf nicht leer sein. Empfangen: '{company_name_to_add}'")
        if conn: conn.close()
        return None

    company_name_to_add_stripped = str(company_name_to_add).strip()
    # print(f"DB DEBUG: add_company - Name nach strip(): '{company_name_to_add_stripped}'") # Bereits im Log

    cursor = conn.cursor() 

    try:
        # print(f"DB DEBUG: add_company - Führe case-insensitive Vorab-Prüfung für '{company_name_to_add_stripped}' aus...") # Bereits im Log
        cursor.execute("SELECT id, name FROM companies WHERE name = ? COLLATE NOCASE", (company_name_to_add_stripped,))
        existing_company_by_name_nocase = cursor.fetchone()
        
        if existing_company_by_name_nocase:
            print(f"DB HINWEIS (Vorab-Prüfung): Firma ähnlich zu '{company_name_to_add_stripped}' (case-insensitive) existiert: ID {existing_company_by_name_nocase['id']}, Name '{existing_company_by_name_nocase['name']}'. Anlage abgebrochen.")
            if conn: conn.close() # Schließe Verbindung hier, da Funktion beendet wird
            return None
        # else: # Bereits im Log
            # print(f"DB INFO (Vorab-Prüfung): Kein case-insensitives Duplikat für '{company_name_to_add_stripped}' gefunden.")
    except Exception as e_check:
        print(f"DB FEHLER bei Vorab-Prüfung in add_company: {e_check}")
        if conn: conn.close()
        return None

    # try: # Bereits im Log
    #     cursor.execute("SELECT name FROM companies")
    #     all_current_names = [row['name'] for row in cursor.fetchall()]
    #     print(f"DB DEBUG: add_company - Aktuell in DB gespeicherte Firmennamen (vor INSERT): {all_current_names}")
    # except Exception as e_list:
    #     print(f"DB FEHLER beim Auflisten aktueller Namen vor INSERT in add_company: {e_list}")


    now = datetime.now().isoformat()
    fields = ["name", "logo_base64", "street", "zip_code", "city", "phone", "email", "website",
              "tax_id", "commercial_register", "bank_details", "pdf_footer_text",
              "is_default", "created_at", "updated_at"]
    
    values_to_insert = []
    for field_name in fields:
        if field_name == "name":
            values_to_insert.append(company_name_to_add_stripped)
        elif field_name == "created_at" or field_name == "updated_at":
            values_to_insert.append(now)
        elif field_name == "is_default":
            values_to_insert.append(int(company_data.get(field_name, 0)))
        else:
            val = company_data.get(field_name)
            if isinstance(val, str):
                values_to_insert.append(val.strip() if val else None)
            else:
                values_to_insert.append(val)

    placeholders = ",".join(["?"]*len(fields))
    
    # print(f"DB DEBUG: add_company - Versuche INSERT mit Name: '{company_name_to_add_stripped}' und Werten: {values_to_insert}") # Bereits im Log
    try:
        # Erneuten Cursor holen, falls der vorherige durch Fehler geschlossen wurde (obwohl conn.close() besser ist)
        # Besser: Cursor am Anfang der Funktion erstellen und durchgehend verwenden.
        # Dieser Cursor wurde bereits oben erstellt.
        cursor.execute(f"INSERT INTO companies ({','.join(fields)}) VALUES ({placeholders})", values_to_insert)
        conn.commit()
        new_id = cursor.lastrowid
        print(f"DB ERFOLG: Firma '{company_name_to_add_stripped}' mit ID {new_id} hinzugefügt.")
        if new_id and company_data.get("is_default"):
            cursor.execute("UPDATE companies SET is_default = 0 WHERE id != ?", (new_id,))
            save_admin_setting('active_company_id', new_id) 
            conn.commit() 
        # Nach dem Hinzufügen der Firma Standardtechnik einfügen
        if new_id:
            add_default_technique_for_company(new_id)
        return new_id
    except sqlite3.IntegrityError as e_int: 
        print(f"DB FEHLER (IntegrityError) beim INSERT: Firma '{company_name_to_add_stripped}' existiert bereits oder anderer UNIQUE Constraint verletzt. Fehler: {e_int}")
        return None
    except Exception as e: 
        print(f"DB FEHLER (Allgemein) beim INSERT in add_company: {e}")
        traceback.print_exc()
        conn.rollback()
        return None
    finally:
        if conn: conn.close() # Sicherstellen, dass die Verbindung immer geschlossen wird

def list_companies() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies ORDER BY name COLLATE NOCASE")
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e: print(f"DB Fehler list_companies: {e}"); return []
    finally:
        if conn: conn.close()

def get_company(company_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone(); return dict(row) if row else None
    except Exception as e: print(f"DB Fehler get_company (ID: {company_id}): {e}"); return None
    finally:
        if conn: conn.close()

def update_company(company_id: int, company_data: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    if not conn: return False
    now_iso = datetime.now().isoformat()
    
    update_data_db = company_data.copy()
    update_data_db["updated_at"] = now_iso
    
    allowed_fields_for_update = ["name", "logo_base64", "street", "zip_code", "city", "phone",
                                 "email", "website", "tax_id", "commercial_register",
                                 "bank_details", "pdf_footer_text", "is_default", "updated_at"]
    fields_to_set_parts = []
    values_for_set = []
    
    for key, val in update_data_db.items():
        if key in allowed_fields_for_update:
            fields_to_set_parts.append(f"{key} = ?")
            if key == "is_default": values_for_set.append(int(val) if val is not None else 0)
            elif isinstance(val, str): values_for_set.append(val.strip() if val else None)
            else: values_for_set.append(val)

    if not fields_to_set_parts: return False
    values_for_set.append(company_id)
    stmt = f"UPDATE companies SET {', '.join(fields_to_set_parts)} WHERE id = ?"
    
    try:
        cursor = conn.cursor()
        if update_data_db.get("is_default"):
            cursor.execute("UPDATE companies SET is_default = 0 WHERE id != ?", (company_id,))
            save_admin_setting('active_company_id', company_id)

        cursor.execute(stmt, values_for_set)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError as e_int: print(f"DB Integritätsfehler update_company (ID {company_id}): {e_int}"); conn.rollback(); return False
    except Exception as e: print(f"DB Fehler update_company (ID {company_id}): {e}"); conn.rollback(); return False
    finally:
        if conn: conn.close()

def delete_company(company_id: int) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        docs_to_delete = list_company_documents(company_id)
        for doc in docs_to_delete: delete_company_document(doc['id'])
        cursor = conn.cursor()
        cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            active_id_str = load_admin_setting('active_company_id')
            active_id = None
            if active_id_str is not None:
                try: active_id = int(active_id_str)
                except ValueError: pass

            if active_id == company_id: save_admin_setting('active_company_id', None)
            return True
        return False
    except Exception as e: print(f"DB Fehler delete_company (ID: {company_id}): {e}"); conn.rollback(); return False
    finally:
        if conn: conn.close()

def set_default_company(company_id: int) -> bool:
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE companies SET is_default = 0 WHERE id != ?", (company_id,))
        cursor.execute("UPDATE companies SET is_default = 1 WHERE id = ?", (company_id,))
        conn.commit()
        if cursor.rowcount > 0: return save_admin_setting('active_company_id', company_id)
        return False
    except Exception as e: print(f"DB Fehler set_default_company (ID: {company_id}): {e}"); conn.rollback(); return False
    finally:
        if conn: conn.close()

def get_active_company() -> Optional[Dict[str, Any]]:
    active_id_str = load_admin_setting('active_company_id')
    active_id = None
    if active_id_str is not None:
        try: active_id = int(active_id_str)
        except (ValueError, TypeError): print(f"DB Warnung: Ungültiger active_company_id Wert '{active_id_str}'."); active_id = None
    if active_id is not None:
        company_details = get_company(active_id)
        if company_details: return company_details
        else: print(f"DB Warnung: Aktive Firma ID {active_id} nicht in DB gefunden."); save_admin_setting('active_company_id', None); return None
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE is_default = 1 LIMIT 1")
        row = cursor.fetchone()
        if row:
            default_company = dict(row)
            save_admin_setting('active_company_id', default_company['id']) 
            return default_company
    except Exception as e: print(f"DB Fehler get_active_company (Fallback): {e}")
    finally:
        if conn: conn.close()
    return None

def add_company_document(company_id: int, display_name: str, document_type: str, original_filename: str, file_content_bytes: bytes) -> Optional[int]:
    conn = get_db_connection()
    if not conn: return None
    if not display_name or not display_name.strip():
        print("DB FEHLER: display_name für add_company_document darf nicht leer sein.")
        return None
    company_specific_docs_dir = os.path.join(COMPANY_DOCS_BASE_DIR, str(company_id))
    if not os.path.exists(company_specific_docs_dir):
        try: os.makedirs(company_specific_docs_dir)
        except OSError as e_mkdir: print(f"DB: FEHLER Erstellen Verzeichnis {company_specific_docs_dir}: {e_mkdir}"); return None
    safe_filename_base = "".join(c if c.isalnum() else "_" for c in os.path.splitext(original_filename)[0])
    file_extension = os.path.splitext(original_filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    final_safe_filename = f"{safe_filename_base}_{timestamp}{file_extension}"
    relative_path_for_db = os.path.join(str(company_id), final_safe_filename)
    absolute_path_on_disk = os.path.join(company_specific_docs_dir, final_safe_filename)
    try:
        with open(absolute_path_on_disk, "wb") as f: f.write(file_content_bytes)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO company_documents (company_id, document_type, display_name, file_name, absolute_file_path, uploaded_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (company_id, document_type, display_name.strip(), final_safe_filename, relative_path_for_db))
        conn.commit(); return cursor.lastrowid
    except IOError as e_io: print(f"DB: IOError beim Schreiben der Dokumentdatei {absolute_path_on_disk}: {e_io}"); return None
    except sqlite3.Error as e_sql: print(f"DB: SQLite Fehler add_company_document: {e_sql}"); conn.rollback(); return None
    finally:
        if conn: conn.close()

# === NEUE FUNKTIONEN FÜR FIRMENSPEZIFISCHE ANGEBOTSVORLAGEN ===

def add_company_text_template(company_id: int, name: str, content: str, template_type: str = "offer_text") -> Optional[int]:
    """Fügt eine firmenspezifische Textvorlage hinzu"""
    conn = get_db_connection()
    if not conn: return None
    if not name or not name.strip():
        print("DB FEHLER: name für add_company_text_template darf nicht leer sein.")
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO company_text_templates (company_id, name, content, template_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (company_id, name.strip(), content or "", template_type))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e_sql:
        print(f"DB: SQLite Fehler add_company_text_template: {e_sql}")
        conn.rollback()
        return None
    finally:
        if conn: conn.close()

def add_company_image_template(company_id: int, name: str, image_data: bytes, template_type: str = "title_image", original_filename: Optional[str] = None) -> Optional[int]:
    """Fügt eine firmenspezifische Bildvorlage hinzu"""
    conn = get_db_connection()
    if not conn: return None
    if not name or not name.strip():
        print("DB FEHLER: name für add_company_image_template darf nicht leer sein.")
        return None
    
    # Verzeichnis für firmenspezifische Bilder erstellen
    company_images_dir = os.path.join(COMPANY_DOCS_BASE_DIR, str(company_id), "images")
    if not os.path.exists(company_images_dir):
        try: 
            os.makedirs(company_images_dir)
        except OSError as e_mkdir: 
            print(f"DB: FEHLER Erstellen Verzeichnis {company_images_dir}: {e_mkdir}")
            return None
    
    # Dateiname generieren
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if original_filename:
        safe_filename_base = "".join(c if c.isalnum() else "_" for c in os.path.splitext(original_filename)[0])
        file_extension = os.path.splitext(original_filename)[1]
    else:
        safe_filename_base = "image"
        file_extension = ".png"  # Default
    
    final_safe_filename = f"{safe_filename_base}_{timestamp}{file_extension}"
    relative_path_for_db = os.path.join(str(company_id), "images", final_safe_filename)
    absolute_path_on_disk = os.path.join(company_images_dir, final_safe_filename)
    
    try:
        # Bild auf Festplatte speichern
        with open(absolute_path_on_disk, "wb") as f:
            f.write(image_data)
        
        # Datenbankeneintrag
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO company_image_templates (company_id, name, template_type, file_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (company_id, name.strip(), template_type, relative_path_for_db))
        conn.commit()
        return cursor.lastrowid
    except IOError as e_io:
        print(f"DB: IOError beim Schreiben der Bilddatei {absolute_path_on_disk}: {e_io}")
        return None
    except sqlite3.Error as e_sql:
        print(f"DB: SQLite Fehler add_company_image_template: {e_sql}")
        conn.rollback()
        return None
    finally:
        if conn: conn.close()

def list_company_text_templates(company_id: int, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Listet alle firmenspezifischen Textvorlagen auf"""
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        if template_type:
            cursor.execute("""
                SELECT id, company_id, name, content, template_type, created_at, updated_at 
                FROM company_text_templates 
                WHERE company_id = ? AND template_type = ?
                ORDER BY name COLLATE NOCASE
            """, (company_id, template_type))
        else:
            cursor.execute("""
                SELECT id, company_id, name, content, template_type, created_at, updated_at 
                FROM company_text_templates 
                WHERE company_id = ?
                ORDER BY template_type, name COLLATE NOCASE
            """, (company_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"DB Fehler list_company_text_templates: {e}")
        return []
    finally:
        if conn: conn.close()

def list_company_image_templates(company_id: int, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Listet alle firmenspezifischen Bildvorlagen auf"""
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        if template_type:
            cursor.execute("""
                SELECT id, company_id, name, template_type, file_path, created_at, updated_at 
                FROM company_image_templates 
                WHERE company_id = ? AND template_type = ?
                ORDER BY name COLLATE NOCASE
            """, (company_id, template_type))
        else:
            cursor.execute("""
                SELECT id, company_id, name, template_type, file_path, created_at, updated_at 
                FROM company_image_templates 
                WHERE company_id = ?
                ORDER BY template_type, name COLLATE NOCASE
            """, (company_id,))
        
        results = []
        for row in cursor.fetchall():
            template_dict = dict(row)
            # Vollständigen Pfad hinzufügen
            template_dict['absolute_file_path'] = os.path.join(COMPANY_DOCS_BASE_DIR, template_dict['file_path'])
            results.append(template_dict)
        return results
    except Exception as e:
        print(f"DB Fehler list_company_image_templates: {e}")
        return []
    finally:
        if conn: conn.close()

def get_company_image_template_data(template_id: int) -> Optional[bytes]:
    """Lädt die Bilddaten einer firmenspezifischen Vorlage"""
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM company_image_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        file_path = os.path.join(COMPANY_DOCS_BASE_DIR, row['file_path'])
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        else:
            print(f"DB WARNUNG: Bilddatei nicht gefunden: {file_path}")
            return None
    except Exception as e:
        print(f"DB Fehler get_company_image_template_data: {e}")
        return None
    finally:
        if conn: conn.close()

def delete_company_text_template(template_id: int) -> bool:
    """Löscht eine firmenspezifische Textvorlage"""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM company_text_templates WHERE id = ?", (template_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Fehler delete_company_text_template: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def delete_company_image_template(template_id: int) -> bool:
    """Löscht eine firmenspezifische Bildvorlage (inkl. Datei)"""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # Dateipfad abrufen
        cursor.execute("SELECT file_path FROM company_image_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        if row:
            file_path = os.path.join(COMPANY_DOCS_BASE_DIR, row['file_path'])
            # Datei löschen
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e_os:
                    print(f"DB Fehler beim Löschen der Bilddatei {file_path}: {e_os}")
        
        # Datenbankeintrag löschen
        cursor.execute("DELETE FROM company_image_templates WHERE id = ?", (template_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Fehler delete_company_image_template: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def update_company_text_template(template_id: int, name: str, content: str) -> bool:
    """Aktualisiert eine firmenspezifische Textvorlage"""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE company_text_templates 
            SET name = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (name.strip() if name else "", content or "", template_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Fehler update_company_text_template: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def update_company_image_template(template_id: int, name: str) -> bool:
    """Aktualisiert den Namen einer firmenspezifischen Bildvorlage"""
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE company_image_templates 
            SET name = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (name.strip() if name else "", template_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Fehler update_company_image_template: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def list_company_documents(company_id: int, doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        sql_query = "SELECT id, company_id, document_type, display_name, file_name, absolute_file_path as relative_db_path, uploaded_at FROM company_documents WHERE company_id = ?"
        params: Tuple = (company_id,)    # <- Typisierung über `Tuple`, nicht `Tuple`
        if doc_type:
            sql_query += " AND document_type = ?"
            params += (doc_type,)
        sql_query += " ORDER BY document_type, display_name COLLATE NOCASE"
        cursor.execute(sql_query, params)
        rows = cursor.fetchall()
        return [{**dict(row), 'absolute_file_path': os.path.join(COMPANY_DOCS_BASE_DIR, row['relative_db_path'])} for row in rows]
    except Exception as e: print(f"DB Fehler list_company_documents (ID: {company_id}): {e}"); return []
    finally:
        if conn: conn.close()

def delete_company_document(document_id: int) -> bool:
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    cursor.execute("SELECT absolute_file_path as relative_db_path FROM company_documents WHERE id = ?", (document_id,))
    row = cursor.fetchone()
    if not row: return False
    relative_path_from_db = row['relative_db_path']
    actual_absolute_path_to_delete_on_disk = os.path.join(COMPANY_DOCS_BASE_DIR, relative_path_from_db)
    try:
        cursor.execute("DELETE FROM company_documents WHERE id = ?", (document_id,))
        if os.path.exists(actual_absolute_path_to_delete_on_disk):
            try:
                os.remove(actual_absolute_path_to_delete_on_disk)
                parent_dir = os.path.dirname(actual_absolute_path_to_delete_on_disk)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir): os.rmdir(parent_dir)
            except OSError as e_os: print(f"DB Fehler Löschen Datei {actual_absolute_path_to_delete_on_disk}: {e_os}")
        conn.commit(); return cursor.rowcount > 0
    except Exception as e: print(f"DB Fehler delete_company_document (ID: {document_id}): {e}"); conn.rollback(); return False
    finally:
        if conn: conn.close()

def add_default_technique_for_company(company_id: int):
    """Fügt Standardtechnik für eine neue Firma hinzu."""
    conn = get_db_connection()
    if conn is None:
        print("DB FEHLER: Keine Verbindung zur Datenbank.")
        return False

    try:
        cursor = conn.cursor()
        default_technique = [
            (company_id, 'PV Module', 'Vitovolt 300-DG M440HC', 440, 20),
            (company_id, 'Wechselrichter', 'BT Serie GW5K-BT 5 kW Batteriewechselrichter', 5000, 1),
            (company_id, 'Speicher', 'Vitocharge VX3 A10 10,0 kWh Speicherturm', 10, 5)
        ]

        cursor.executemany(
            """
            INSERT INTO company_technique (company_id, type, model, capacity, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
            default_technique
        )
        conn.commit()
        print(f"Standardtechnik für Firma {company_id} erfolgreich hinzugefügt.")
        return True

    except sqlite3.Error as e:
        print(f"DB FEHLER: Fehler beim Hinzufügen der Standardtechnik für Firma {company_id}: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def get_company_documents(company_id: int, doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lädt alle Dokumente einer Firma aus der Datenbank.
    
    Args:
        company_id (int): ID der Firma
        doc_type (str, optional): Dokumenttyp Filter
    
    Returns:
        List[Dict[str, Any]]: Liste der Dokumente
    """
    return list_company_documents(company_id, doc_type)

def get_all_active_customers() -> List[Dict[str, Any]]:
    """Gibt alle aktiven Kunden aus der CRM-Datenbank zurück"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Versuche zuerst die Tabelle zu erstellen falls sie nicht existiert
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crm_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                project_data TEXT
            )
        ''')
        
        cursor.execute('''
            SELECT id, first_name, last_name, email, phone, address, status, 
                   created_at, updated_at, notes, project_data
            FROM crm_customers 
            WHERE status = 'active' OR status IS NULL
            ORDER BY last_name, first_name
        ''')
        
        rows = cursor.fetchall()
        customers = []
        
        for row in rows:
            customer = {
                'id': row[0],
                'first_name': row[1] or '',
                'last_name': row[2] or '',
                'email': row[3] or '',
                'phone': row[4] or '',
                'address': row[5] or '',
                'status': row[6] or 'active',
                'created_at': row[7],
                'updated_at': row[8],
                'notes': row[9] or '',
                'project_data': json.loads(row[10]) if row[10] else {}
            }
            customers.append(customer)
        
        conn.close()
        return customers
        
    except Exception as e:
        print(f"Fehler beim Abrufen der aktiven Kunden: {e}")
        return []

def create_customer(customer_data: Dict[str, Any]) -> bool:
    """Erstellt einen neuen Kunden in der CRM-Datenbank"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabelle erstellen falls sie nicht existiert
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crm_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                project_data TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT INTO crm_customers (first_name, last_name, email, phone, address, notes, project_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data.get('first_name', ''),
            customer_data.get('last_name', ''),
            customer_data.get('email', ''),
            customer_data.get('phone', ''),
            customer_data.get('address', ''),
            customer_data.get('notes', ''),
            json.dumps(customer_data.get('project_data', {}))
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Kunden: {e}")
        return False

def update_customer(customer_id: int, customer_data: Dict[str, Any]) -> bool:
    """
    Aktualisiert einen Kunden in der Datenbank.
    
    Args:
        customer_id (int): ID des Kunden
        customer_data (Dict[str, Any]): Neue Kundendaten
    
    Returns:
        bool: True wenn erfolgreich
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customers 
            SET salutation = ?, title = ?, first_name = ?, last_name = ?, company_name = ?,
                address = ?, house_number = ?, zip_code = ?, city = ?, state = ?, region = ?,
                email = ?, phone_landline = ?, phone_mobile = ?, income_tax_rate_percent = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            customer_data.get('salutation', ''),
            customer_data.get('title', ''),
            customer_data.get('first_name', ''),
            customer_data.get('last_name', ''),
            customer_data.get('company_name', ''),
            customer_data.get('address', ''),
            customer_data.get('house_number', ''),
            customer_data.get('zip_code', ''),
            customer_data.get('city', ''),
            customer_data.get('state', ''),
            customer_data.get('region', ''),
            customer_data.get('email', ''),
            customer_data.get('phone_landline', ''),
            customer_data.get('phone_mobile', ''),
            customer_data.get('income_tax_rate_percent', 0.0),
            customer_id
        ))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Kunden {customer_id}: {e}")
        return False

def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    """Gibt einen spezifischen Kunden basierend auf der ID zurück"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Versuche zuerst die Tabelle zu erstellen falls sie nicht existiert
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crm_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                project_data TEXT
            )
        ''')
        
        cursor.execute('''
            SELECT id, first_name, last_name, email, phone, address, status, 
                   created_at, updated_at, notes, project_data
            FROM crm_customers 
            WHERE id = ?
        ''', (customer_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            customer = {
                'id': row[0],
                'first_name': row[1] or '',
                'last_name': row[2] or '',
                'email': row[3] or '',
                'phone': row[4] or '',
                'address': row[5] or '',
                'status': row[6] or 'active',
                'created_at': row[7],
                'updated_at': row[8],
                'notes': row[9] or '',
                'project_data': json.loads(row[10]) if row[10] else {}
            }
            return customer
        
        return None
        
    except Exception as e:
        print(f"Fehler beim Abrufen des Kunden mit ID {customer_id}: {e}")
        return None
