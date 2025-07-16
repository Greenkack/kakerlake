# check_matrix_db.py
import sqlite3
import os
import json # json wird hier nicht direkt für den Parse-Teil benötigt, aber ok
import traceback
import io # Für StringIO

# Stelle sicher, dass calculations.py importiert werden kann
try:
    from calculations import parse_price_matrix_csv # Die Funktion, die jetzt 2 Argumente braucht
    CALCULATIONS_MODULE_AVAILABLE = True
except ImportError:
    CALCULATIONS_MODULE_AVAILABLE = False
    print("FEHLER: check_matrix_db.py - Modul 'calculations.py' nicht gefunden.")
    def parse_price_matrix_csv(csv_input: any, calculation_errors: list) -> None: # Dummy mit korrekter Signatur
        print("WARNUNG: Dummy parse_price_matrix_csv in check_matrix_db.py verwendet.")
        calculation_errors.append("Dummy parser in check_matrix_db.py.")
        return None

# Definiere den Pfad zur Datenbankdatei
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'app_data.db')

print(f"Datenbankpfad, der geprüft wird: {DB_PATH}")

conn = None
try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM admin_settings WHERE key = ?", ('price_matrix_csv_data',))
    row = cursor.fetchone()

    if row:
        value_str = row['value']
        # ... (Ausgabe des Strings bleibt gleich) ...
        print(f"\nGefundener Wert für 'price_matrix_csv_data' in der Datenbank:")
        print("-" * 30)
        if value_str:
            print(value_str[:500] + ("..." if len(value_str) > 1000 else ""))
            if len(value_str) > 1000:
                 print("...")
                 print(value_str[-500:])
            print("-" * 30)
            print(f"Gesamtlänge des gespeicherten Strings: {len(value_str)} Zeichen.")

            if CALCULATIONS_MODULE_AVAILABLE:
                print("\nVersuche, den gespeicherten String mit parse_price_matrix_csv zu parsen...")
                parser_errors_check_db: list[str] = [] # Fehlerliste für diesen Aufruf
                parsed_df = parse_price_matrix_csv(io.StringIO(value_str), parser_errors_check_db) # KORRIGIERTER AUFRUF

                if parser_errors_check_db:
                    print("--- Parser-Meldungen von check_matrix_db.py ---")
                    for err in parser_errors_check_db:
                        print(err)
                
                if parsed_df is not None and not parsed_df.empty: # Prüfe auch auf nicht leer
                    print("✅ Parsen erfolgreich!")
                    print(f"Shape des geparsten DataFrames: {parsed_df.shape[0]} Zeilen, {parsed_df.shape[1]} Spalten.")
                    print("Erste 5 Zeilen des geparsten DataFrames:")
                    print(parsed_df.head())
                elif parsed_df is not None and parsed_df.empty:
                    print("⚠️ Parsen ergab eine leere Matrix.")
                else: # parsed_df is None
                    print("❌ Parsen fehlgeschlagen (parse_price_matrix_csv gab None zurück oder ein Fehler trat auf).")
            else:
                print("\nparse_price_matrix_csv Funktion nicht verfügbar. Parsen kann nicht geprüft werden.")
        else:
            print("Kein String-Wert für 'price_matrix_csv_data' gefunden (Wert ist leer oder NULL).")
    else:
        print("\nEintrag für 'price_matrix_csv_data' nicht in der admin_settings Tabelle gefunden.")

except Exception as e:
    print(f"\nEin Fehler ist beim Zugriff auf die Datenbank aufgetreten: {e}")
    traceback.print_exc()
finally:
    if conn:
        conn.close()