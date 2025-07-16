#!/usr/bin/env python3
"""
Einfache Datenbank-Initialisierung für die Solar-App
Erstellt die wichtigsten Tabellen und fügt Beispieldaten hinzu
"""
import sqlite3
import os
from datetime import datetime

def init_database_simple():
    """Initialisiere die Datenbank mit den wichtigsten Tabellen"""
    
    # Datenverzeichnis erstellen
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    DB_PATH = os.path.join(data_dir, 'database.db')
    print(f"Erstelle Datenbank: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Companies Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            street TEXT,
            zip_code TEXT,
            city TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            tax_id TEXT,
            commercial_register TEXT,
            bank_details TEXT,
            pdf_footer_text TEXT,
            logo_base64 TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Company Documents Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            display_name TEXT NOT NULL,
            file_name TEXT NOT NULL,
            absolute_file_path TEXT NOT NULL,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
        )
    ''')
    
    # Products Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            model_name TEXT NOT NULL UNIQUE,
            brand TEXT,
            price_euro REAL DEFAULT 0,
            capacity_w REAL,
            storage_power_kw REAL,
            power_kw REAL,
            max_cycles INTEGER,
            warranty_years INTEGER DEFAULT 0,
            length_m REAL,
            width_m REAL,
            weight_kg REAL,
            efficiency_percent REAL,
            origin_country TEXT,
            description TEXT,
            pros TEXT,
            cons TEXT,
            rating REAL,
            image_base64 TEXT,
            datasheet_link_db_path TEXT,
            additional_cost_netto REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Beispiel-Firma hinzufügen
    cursor.execute('''
        INSERT OR IGNORE INTO companies 
        (name, street, zip_code, city, phone, email, website, is_default) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Solar Solutions GmbH',
        'Musterstraße 123',
        '12345',
        'Berlin',
        '+49 30 12345678',
        'info@solar-solutions.de',
        'www.solar-solutions.de',
        1  # Als Standard setzen
    ))
    
    company_id = cursor.lastrowid
    
    # Weitere Beispiel-Firmen hinzufügen (für Multi-PDF)
    example_companies = [
        ('BTPV Deutschland Gmbh', 'Industriestr. 45', '80333', 'München', '+49 89 987654', 'info@btpv.de', 'www.btpv.de'),
        ('Deutsche Energie Werke Gmbh', 'Energieweg 12', '10115', 'Berlin', '+49 30 555444', 'kontakt@dew.de', 'www.deutsche-energie.de'),
        ('Energienetze Deutschland Gmbh', 'Netzstr. 88', '20095', 'Hamburg', '+49 40 333222', 'service@energienetze.de', 'www.energienetze-deutschland.de'),
        ('Energiewerke Nord GmbH', 'Nordweg 56', '24103', 'Kiel', '+49 431 111999', 'info@energiewerke-nord.de', 'www.energiewerke-nord.de'),
        ('s.Energy', 'Solarplatz 7', '70173', 'Stuttgart', '+49 711 777888', 'hello@s-energy.de', 'www.s-energy.de')
    ]
    
    for company_data in example_companies:
        cursor.execute('''
            INSERT OR IGNORE INTO companies 
            (name, street, zip_code, city, phone, email, website, is_default) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', company_data + (0,))  # is_default = 0
    
    # Beispiel-Produkte hinzufügen
    example_products = [
        ('Modul', 'JA Solar JAM72S30-545/MR', 'JA Solar', 250.00, 545, None, None, None, 25, 2.279, 1.134, 27.5, 21.0),
        ('Modul', 'Longi LR5-72HIH-545M', 'Longi Solar', 245.00, 545, None, None, None, 25, 2.256, 1.133, 27.8, 21.1),
        ('Wechselrichter', 'SMA Sunny Boy 6.0', 'SMA', 1200.00, None, None, 6.0, None, 10, None, None, 27.0, 97.1),
        ('Wechselrichter', 'Fronius Primo 8.2-1', 'Fronius', 1350.00, None, None, 8.2, None, 5, None, None, 31.5, 96.8),
        ('Batteriespeicher', 'BYD Battery-Box Premium HVS 7.68', 'BYD', 3500.00, None, 7.68, 3.0, 6000, 10, None, None, 75.0, None),
        ('Batteriespeicher', 'SENEC Home V3 hybrid 7.5', 'SENEC', 4200.00, None, 7.5, 5.0, 10000, 10, None, None, 85.0, None),
        ('Wallbox', 'go-eCharger HOMEfix 11kW', 'go-e', 599.00, None, None, 11.0, None, 3, None, None, 1.7, None),
        ('Wallbox', 'KEBA KeContact P30 c-series', 'KEBA', 899.00, None, None, 22.0, None, 3, None, None, 4.2, None)
    ]
    
    for product_data in example_products:
        cursor.execute('''
            INSERT OR IGNORE INTO products 
            (category, model_name, brand, price_euro, capacity_w, storage_power_kw, power_kw, max_cycles, warranty_years, length_m, width_m, weight_kg, efficiency_percent) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', product_data)
    
    conn.commit()
    conn.close()
    
    print("✅ Datenbank erfolgreich initialisiert!")
    print("✅ Beispiel-Firmen und -Produkte hinzugefügt!")
    print(f"✅ Datenbank gespeichert unter: {DB_PATH}")

if __name__ == "__main__":
    init_database_simple()
