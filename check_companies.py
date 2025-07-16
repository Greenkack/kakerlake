#!/usr/bin/env python3
import sqlite3
import os

# Datenbank-Pfad bestimmen
DB_PATH = os.path.join(os.getcwd(), 'data', 'app_data.db')
print(f'Datenbank-Pfad: {DB_PATH}')
print(f'Datei existiert: {os.path.exists(DB_PATH)}')

if os.path.exists(DB_PATH):
    print(f'Dateigröße: {os.path.getsize(DB_PATH)} Bytes')
    
    # Tabellen auflisten
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f'Vorhandene Tabellen: {[table[0] for table in tables]}')
        
        # Companies prüfen
        if 'companies' in [table[0] for table in tables]:
            cursor.execute('SELECT COUNT(*) FROM companies')
            count = cursor.fetchone()[0]
            print(f'Anzahl Firmen: {count}')
            
            if count > 0:
                cursor.execute('SELECT id, name FROM companies LIMIT 3')
                companies = cursor.fetchall()
                print(f'Beispiel-Firmen: {companies}')
        else:
            print('Companies-Tabelle existiert nicht!')
        
        # Company Documents prüfen
        if 'company_documents' in [table[0] for table in tables]:
            cursor.execute('SELECT COUNT(*) FROM company_documents')
            doc_count = cursor.fetchone()[0]
            print(f'Anzahl Company-Dokumente: {doc_count}')
            
            if doc_count > 0:
                cursor.execute('SELECT company_id, document_type, display_name FROM company_documents LIMIT 5')
                docs = cursor.fetchall()
                print(f'Beispiel-Dokumente: {docs}')
            else:
                print('Keine Company-Dokumente vorhanden!')
        else:
            print('Company_documents-Tabelle existiert nicht!')
        
        # PDF Templates prüfen
        if 'pdf_templates' in [table[0] for table in tables]:
            cursor.execute('SELECT COUNT(*) FROM pdf_templates')
            template_count = cursor.fetchone()[0]
            print(f'Anzahl PDF-Templates: {template_count}')
            
            if template_count > 0:
                cursor.execute('SELECT template_type, name FROM pdf_templates LIMIT 5')
                templates = cursor.fetchall()
                print(f'Beispiel-Templates: {templates}')
            else:
                print('Keine PDF-Templates vorhanden!')
        else:
            print('PDF_templates-Tabelle existiert nicht!')
        
        # Admin Settings Templates prüfen
        cursor.execute('SELECT COUNT(*) FROM admin_settings')
        settings_count = cursor.fetchone()[0]
        print(f'Anzahl Admin-Einstellungen: {settings_count}')
        
        if settings_count > 0:
            cursor.execute("SELECT key FROM admin_settings WHERE key LIKE '%template%'")
            template_keys = cursor.fetchall()
            print(f'Template-Keys: {[key[0] for key in template_keys]}')
            
            # Spezifische Template-Keys prüfen
            template_checks = [
                'pdf_title_image_templates',
                'pdf_offer_title_templates', 
                'pdf_cover_letter_templates'
            ]
            
            for template_key in template_checks:
                cursor.execute("SELECT value FROM admin_settings WHERE key = ?", (template_key,))
                result = cursor.fetchone()
                if result:
                    import json
                    try:
                        templates = json.loads(result[0])
                        print(f'{template_key}: {len(templates)} Templates')
                    except:
                        print(f'{template_key}: Fehler beim Parsen')
                else:
                    print(f'{template_key}: Nicht gefunden')
        
        conn.close()
    except Exception as e:
        print(f'Fehler beim Datenbankzugriff: {e}')
else:
    print('Datenbank existiert nicht!')
