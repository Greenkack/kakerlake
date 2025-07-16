import sqlite3

def check_products_for_company(company_id):
    db_path = 'data/app_data.db'  # Pfad zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM products WHERE company_id = ?", (company_id,))
        products = cursor.fetchall()

        if products:
            print(f"Produkte für Firma mit ID {company_id}:")
            for product in products:
                print(product)
        else:
            print(f"Keine Produkte für Firma mit ID {company_id} gefunden.")

    except Exception as e:
        print(f"Fehler beim Überprüfen der Produkte: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    company_id = int(input("Geben Sie die company_id ein: "))
    check_products_for_company(company_id)
