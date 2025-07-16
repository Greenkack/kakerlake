import sqlite3
import os
import json
import traceback

# Definiere den Pfad zur Datenbankdatei (muss derselbe sein wie in database.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'app_data.db')

print(f"Datenbankpfad, der aktualisiert wird: {DB_PATH}")

# Definiere die KORREKTEN und VOLLSTÄNDIGEN Einspeisetarif-Schlüssel und Standardwerte
# Diese müssen exakt mit der Logik in calculations.py (Source 190-194) übereinstimmen.
# Die Werte (0.081 etc.) sind die Standardwerte aus database.py initial_settings (Stand Jan 2025)
# Sie können diese Werte hier anpassen, wenn Sie aktuellere Tarife nutzen möchten.
correct_feed_in_tariffs = {
     '<10kWp_Teileinspeisung': 0.081, # 8.1 ct/kWh
     '>10kWp<=40kWp_Teileinspeisung': 0.070, # 7.0 ct/kWh
     '>40kWp<=100kWp_Teileinspeisung': 0.058, # 5.8 ct/kWh
     '>100kWp_Teileinspeisung': 0.058, # Annahme: gleicher Tarif wie >40-100 für über 100 kWp Teil
     '<10kWp_Voll': 0.129, # 12.9 ct/kWh
     '>10kWp<=40kWp_Voll': 0.108, # 10.8 ct/kWh
     '>40kWp<=100kWp_Voll': 0.086, # 8.6 ct/kWh
     '>100kWp_Voll': 0.086 # Annahme: gleicher Tarif wie >40-100 für über 100 kWp Voll
}

conn = None
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Den korrekten Tarif-Dictionary als JSON-String speichern
    tariff_value_json = json.dumps(correct_feed_in_tariffs)

    # Verwenden Sie INSERT OR REPLACE, um den Eintrag für 'feed_in_tariffs' zu erstellen oder zu aktualisieren
    cursor.execute("""
        INSERT OR REPLACE INTO admin_settings (key, value)
        VALUES (?, ?)
    """, ('feed_in_tariffs', tariff_value_json))

    conn.commit()
    print("\n✅ Datenbankeintrag für 'feed_in_tariffs' erfolgreich aktualisiert!")
    print("Neue Schlüssel in der Datenbank sollten nun enthalten sein:")
    print(list(correct_feed_in_tariffs.keys()))


except Exception as e:
    print(f"\n❌ Ein Fehler ist beim Aktualisieren der Datenbank aufgetreten: {e}")
    traceback.print_exc()
    if conn:
        conn.rollback() # Änderungen rückgängig machen bei Fehler

finally:
    if conn:
        conn.close()