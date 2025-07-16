import sqlite3

def add_company_id_column():
    db_path = 'data/app_data.db'  # Pfad zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE;")
        conn.commit()
        print("Die Spalte 'company_id' wurde erfolgreich zur Tabelle 'products' hinzugefügt.")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Die Spalte 'company_id' existiert bereits in der Tabelle 'products'.")
        else:
            print(f"Fehler beim Hinzufügen der Spalte: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    add_company_id_column()
