import sqlite3

def check_column_exists():
    db_path = 'data/app_data.db'  # Pfad zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]  # Spaltennamen extrahieren

        if 'company_id' in column_names:
            print("Die Spalte 'company_id' existiert in der Tabelle 'products'.")
        else:
            print("Die Spalte 'company_id' fehlt in der Tabelle 'products'.")

    except Exception as e:
        print(f"Fehler beim Überprüfen der Spalte: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    check_column_exists()
