import sqlite3
import os
import json
import streamlit as st

# Definiere den Pfad zur Datenbankdatei (muss derselbe sein wie in database.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'app_data.db')

st.write(f"Datenbankpfad, der geprüft wird: {DB_PATH}")

conn = None
try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Ermöglicht Zugriff über Spaltennamen
    cursor = conn.cursor()

    # Versuche, die Einspeisetarife zu laden
    cursor.execute("SELECT value FROM admin_settings WHERE key = ?", ('feed_in_tariffs',))
    row = cursor.fetchone()

    if row:
        value_str = row['value']
        st.write(f"\nGefundener Wert für 'feed_in_tariffs' (als String in DB):")
        st.write(value_str)

        # Versuche, den Wert als JSON zu parsen
        try:
            tariff_data = json.loads(value_str)
            st.write("\nGefundener Wert für 'feed_in_tariffs' (als Python Dictionary/Liste nach JSON Parse):")
            st.write(tariff_data)

            # Überprüfen Sie hier manuell, ob der Schlüssel '<10kWp_Teileinspeisung' enthalten ist
            expected_key = '<10kWp_Teileinspeisung'
            if isinstance(tariff_data, dict) and expected_key in tariff_data:
                st.write(f"\n✅ Der Schlüssel '{expected_key}' wurde im geladenen Dictionary gefunden!")
                st.write(f"Zuordnungswert: {tariff_data[expected_key]}")
            elif isinstance(tariff_data, dict):
                 st.write(f"\n❌ Der Schlüssel '{expected_key}' wurde NICHT im geladenen Dictionary gefunden.")
                 st.write("Vorhandene Schlüssel:", list(tariff_data.keys()))
            else:
                 st.write("\n❌ Der geladene Wert ist kein Dictionary.")


        except json.JSONDecodeError:
            st.write("\nFEHLER: Konnte den Datenbankwert nicht als JSON parsen. Datenstruktur in DB ist fehlerhaft.")
    else:
        st.write("\nEintrag für 'feed_in_tariffs' nicht in der admin_settings Tabelle gefunden.")

except Exception as e:
    st.write(f"\nEin Fehler ist beim Zugriff auf die Datenbank aufgetreten: {e}")
    import traceback
    traceback.print_exc()

finally:
    if conn:
        conn.close()

st.title("Feed-in Tariffs Viewer")
st.write("This app displays the feed-in tariffs stored in the database.")

# Button to reload the data
if st.button("Reload Data"):
    # Re-run the whole script to refresh the data
    os.execv(__file__, [''] + sys.argv)

st.write("App finished running.")