import sqlite3

conn = sqlite3.connect('solar_db.sqlite')
cursor = conn.cursor()

# Verfügbare Tabellen anzeigen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Verfügbare Tabellen:')
for table in tables:
    print(f'  - {table[0]}')

# Prüfen ob company_documents existiert
try:
    cursor.execute("SELECT COUNT(*) FROM company_documents")
    count = cursor.fetchone()[0]
    print(f'\nAnzahl Company-Dokumente: {count}')
except sqlite3.OperationalError as e:
    print(f'\nFehler bei company_documents: {e}')

conn.close()
