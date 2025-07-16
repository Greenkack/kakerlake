#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detaillierte Datenbank-Prüfung für Firmendokumente
"""

import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_database():
    print("🔍 DATENBANK DIREKT-ANALYSE")
    print("=" * 60)
    
    # Direkter DB-Zugriff
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'app_data.db')
    
    if not os.path.exists(db_path):
        print(f"✗ Datenbank nicht gefunden: {db_path}")
        return
    
    print(f"✓ Datenbank gefunden: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe Tabellen-Schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Verfügbare Tabellen: {[t[0] for t in tables]}")
        
        # Prüfe company_documents Tabelle
        cursor.execute("PRAGMA table_info(company_documents)")
        columns = cursor.fetchall()
        print(f"\n📄 company_documents Spalten:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Prüfe Daten in company_documents
        cursor.execute("SELECT COUNT(*) FROM company_documents")
        count = cursor.fetchone()[0]
        print(f"\n📊 Gesamt-Dokumente in DB: {count}")
        
        if count > 0:
            # Beispiel-Daten anzeigen
            cursor.execute("SELECT * FROM company_documents LIMIT 5")
            rows = cursor.fetchall()
            
            # Spaltennamen abrufen
            cursor.execute("PRAGMA table_info(company_documents)")
            col_info = cursor.fetchall()
            col_names = [col[1] for col in col_info]
            
            print(f"\n📋 Beispiel-Daten (erste 5 Einträge):")
            for i, row in enumerate(rows, 1):
                print(f"\n   Dokument {i}:")
                for j, value in enumerate(row):
                    if j < len(col_names):
                        col_name = col_names[j]
                        if col_name == 'file_path' and value:
                            # Prüfe ob Datei existiert
                            exists = "✓" if os.path.exists(value) else "✗"
                            print(f"     {col_name}: {value} {exists}")
                        else:
                            print(f"     {col_name}: {value}")
            
            # Statistiken
            cursor.execute("SELECT company_id, COUNT(*) FROM company_documents GROUP BY company_id")
            company_stats = cursor.fetchall()
            print(f"\n📊 Dokumente pro Firma:")
            for company_id, doc_count in company_stats:
                print(f"   Firma-ID {company_id}: {doc_count} Dokumente")
            
            # Prüfe Dokument-Typen
            cursor.execute("SELECT type, COUNT(*) FROM company_documents GROUP BY type")
            type_stats = cursor.fetchall()
            print(f"\n📊 Dokument-Typen:")
            for doc_type, type_count in type_stats:
                print(f"   '{doc_type}': {type_count} Dokumente")
            
            # Prüfe leere/null Werte
            cursor.execute("SELECT COUNT(*) FROM company_documents WHERE name IS NULL OR name = ''")
            empty_names = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM company_documents WHERE type IS NULL OR type = ''")
            empty_types = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM company_documents WHERE file_path IS NULL OR file_path = ''")
            empty_paths = cursor.fetchone()[0]
            
            print(f"\n⚠️  PROBLEME:")
            print(f"   Leere/null Namen: {empty_names}/{count}")
            print(f"   Leere/null Typen: {empty_types}/{count}")
            print(f"   Leere/null Pfade: {empty_paths}/{count}")
            
            # Prüfe existierende Dateien
            cursor.execute("SELECT file_path FROM company_documents WHERE file_path IS NOT NULL AND file_path != ''")
            file_paths = cursor.fetchall()
            
            existing_files = 0
            for (file_path,) in file_paths:
                if os.path.exists(file_path):
                    existing_files += 1
            
            print(f"   Existierende Dateien: {existing_files}/{len(file_paths)}")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Fehler bei DB-Analyse: {e}")
        import traceback
        traceback.print_exc()

def suggest_fixes():
    print(f"\n🔧 LÖSUNGSVORSCHLÄGE:")
    print("=" * 60)
    print("1. Die Dokumentenmetadaten (name, type) sind leer oder NULL")
    print("   → Metadaten müssen beim Upload korrekt gesetzt werden")
    print("2. Die Dateipfade zeigen auf nicht-existierende Dateien")
    print("   → Dateien wurden gelöscht oder nie korrekt gespeichert")
    print("3. Die Filterlogik funktioniert korrekt")
    print("   → Problem liegt in den Grunddaten, nicht im Code")
    print("\nSOFORTMASSNAHMEN:")
    print("a) Dokumente erneut hochladen mit korrekten Metadaten")
    print("b) Oder: Test-Dokumente mit gültigen Pfaden erstellen")
    print("c) Oder: Ungültige Dokumente aus DB entfernen")

if __name__ == "__main__":
    analyze_database()
    suggest_fixes()
