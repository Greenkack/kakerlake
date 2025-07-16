#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Analyse für Firmendokumente-Integration
Prüft systematisch für jede Firma:
- Welche Dokumente sind in der DB vorhanden?
- Werden sie korrekt gefiltert und eingebunden?
- Sind die Dateipfade gültig?
- Funktioniert die PDF-Integration?
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

# Stelle sicher, dass wir die lokalen Module importieren können
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import database
    from multi_offer_generator import MultiOfferGenerator
    print("✓ Module erfolgreich importiert")
except ImportError as e:
    print(f"✗ Fehler beim Importieren der Module: {e}")
    sys.exit(1)

def check_file_exists(file_path):
    """Prüft ob eine Datei existiert und gibt Details zurück"""
    if not file_path:
        return False, "Kein Pfad angegeben"
    
    try:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                return True, f"Datei existiert ({size} Bytes)"
            else:
                return False, "Pfad ist kein Datei"
        else:
            return False, "Datei existiert nicht"
    except Exception as e:
        return False, f"Fehler beim Prüfen: {e}"

def analyze_company_documents():
    """Analysiert Firmendokumente für alle Firmen"""
    print("=" * 80)
    print("FIRMENDOKUMENTE-ANALYSE")
    print("=" * 80)
      # Datenbank-Funktionen verwenden
    try:
        print("✓ Datenbank-Funktionen verfügbar")
    except Exception as e:
        print(f"✗ Fehler bei Datenbank-Zugriff: {e}")
        return
    
    # Multi-Offer-Generator initialisieren
    try:
        generator = MultiOfferGenerator()
        print("✓ Multi-Offer-Generator initialisiert")
    except Exception as e:
        print(f"✗ Fehler bei Generator-Initialisierung: {e}")
        return
    
    print("\n" + "=" * 60)
    print("1. ALLE FIRMEN IN DER DATENBANK")
    print("=" * 60)
      # Alle Firmen abrufen
    try:
        companies = database.list_companies()
        print(f"Gefundene Firmen: {len(companies)}")
        
        for i, company in enumerate(companies, 1):
            print(f"{i:2d}. {company.get('name', 'UNBEKANNT')} (ID: {company.get('id', 'N/A')})")
    except Exception as e:
        print(f"✗ Fehler beim Abrufen der Firmen: {e}")
        return
    
    print("\n" + "=" * 60)
    print("2. DOKUMENTE PRO FIRMA (DATENBANK)")
    print("=" * 60)
    
    # Für jede Firma die Dokumente analysieren
    company_docs_summary = {}
      for company in companies:
        company_id = company.get('id')
        company_name = company.get('name', 'UNBEKANNT')
        
        print(f"\n🏢 FIRMA: {company_name} (ID: {company_id})")
        print("-" * 50)
        
        try:
            # Alle Dokumente dieser Firma aus der DB abrufen
            documents = database.list_company_documents(company_id)
            
            if not documents:
                print("   ⚠️  Keine Dokumente in der Datenbank gefunden")
                company_docs_summary[company_name] = {
                    'total_docs': 0,
                    'valid_files': 0,
                    'error': 'Keine Dokumente in DB'
                }
                continue
            
            print(f"   📄 Gesamt-Dokumente in DB: {len(documents)}")
            
            valid_files = 0
            doc_types = {}
            
            for doc in documents:
                doc_id = doc.get('id', 'N/A')
                doc_name = doc.get('name', 'UNBEKANNT')
                doc_type = doc.get('type', 'UNBEKANNT')
                file_path = doc.get('file_path', '')
                
                # Datei-Existenz prüfen
                exists, status = check_file_exists(file_path)
                if exists:
                    valid_files += 1
                
                # Dokument-Typ zählen
                if doc_type in doc_types:
                    doc_types[doc_type] += 1
                else:
                    doc_types[doc_type] = 1
                
                status_icon = "✓" if exists else "✗"
                print(f"   {status_icon} [{doc_type}] {doc_name} (ID: {doc_id})")
                print(f"      Pfad: {file_path}")
                print(f"      Status: {status}")
            
            print(f"   📊 Dokument-Typen: {dict(doc_types)}")
            print(f"   ✅ Gültige Dateien: {valid_files}/{len(documents)}")
            
            company_docs_summary[company_name] = {
                'total_docs': len(documents),
                'valid_files': valid_files,
                'doc_types': doc_types,
                'error': None
            }
            
        except Exception as e:
            print(f"   ✗ Fehler beim Abrufen der Dokumente: {e}")
            company_docs_summary[company_name] = {
                'total_docs': 0,
                'valid_files': 0,
                'error': str(e)
            }
    
    print("\n" + "=" * 60)
    print("3. MULTI-OFFER GENERATOR FILTERLOGIK")
    print("=" * 60)
    
    # Test der get_company_documents_for_pdf Methode
    for company in companies:
        company_id = company.get('id')
        company_name = company.get('name', 'UNBEKANNT')
        
        print(f"\n🔍 FILTER-TEST: {company_name}")
        print("-" * 40)
        
        try:
            # Standard-PDF-Optionen simulieren
            pdf_options = {
                'company_documents_active': True,
                'company_documents_mode': 'standard_types',  # oder 'all', 'first_3'
                'company_documents_standard_types': ['Datenblatt', 'Garantie', 'Zertifikat']
            }
            
            # get_company_documents_for_pdf testen
            filtered_doc_ids = generator.get_company_documents_for_pdf(company_id, pdf_options)
            
            if filtered_doc_ids:
                print(f"   ✅ Gefilterte Dokument-IDs: {filtered_doc_ids}")
                  # Details zu den gefilterten Dokumenten abrufen
                for doc_id in filtered_doc_ids:
                    try:
                        all_docs = database.list_company_documents(company_id)
                        doc = next((d for d in all_docs if d.get('id') == doc_id), None)
                        if doc:
                            print(f"      - ID {doc_id}: [{doc.get('type')}] {doc.get('name')}")
                        else:
                            print(f"      - ID {doc_id}: ⚠️ Dokument nicht gefunden!")
                    except Exception as e:
                        print(f"      - ID {doc_id}: ✗ Fehler beim Abrufen: {e}")
            else:
                print("   ⚠️  Keine Dokumente nach Filterung übrig")
                
        except Exception as e:
            print(f"   ✗ Fehler bei Filter-Test: {e}")
    
    print("\n" + "=" * 60)
    print("4. ZUSAMMENFASSUNG")
    print("=" * 60)
    
    total_companies = len(companies)
    companies_with_docs = sum(1 for info in company_docs_summary.values() if info['total_docs'] > 0)
    companies_with_valid_files = sum(1 for info in company_docs_summary.values() if info['valid_files'] > 0)
    
    print(f"📊 Gesamt-Firmen: {total_companies}")
    print(f"📄 Firmen mit Dokumenten in DB: {companies_with_docs}")
    print(f"✅ Firmen mit gültigen Dateien: {companies_with_valid_files}")
    
    print(f"\n📋 Detaillierte Übersicht:")
    for company_name, info in company_docs_summary.items():
        if info['error']:
            print(f"   ✗ {company_name}: {info['error']}")
        elif info['total_docs'] == 0:
            print(f"   ⚠️  {company_name}: Keine Dokumente")
        else:
            print(f"   ✅ {company_name}: {info['valid_files']}/{info['total_docs']} gültige Dateien")
    
    # Problematische Firmen identifizieren
    print(f"\n🚨 PROBLEMATISCHE FIRMEN:")
    problem_companies = []
    for company_name, info in company_docs_summary.items():
        if info['error'] or (info['total_docs'] > 0 and info['valid_files'] == 0):
            problem_companies.append(company_name)
            if info['error']:
                print(f"   ✗ {company_name}: {info['error']}")
            else:
                print(f"   ✗ {company_name}: Dokumente in DB, aber keine gültigen Dateien")
    
    if not problem_companies:
        print("   ✅ Keine problematischen Firmen gefunden!")
    
    print(f"\n{'='*60}")
    print("ANALYSE ABGESCHLOSSEN")
    print(f"{'='*60}")

def test_pdf_integration():
    """Testet die PDF-Integration mit Debug-Ausgaben"""
    print("\n" + "=" * 60)
    print("5. PDF-INTEGRATION TEST")
    print("=" * 60)
      try:
        generator = MultiOfferGenerator()
        
        # Eine Firma mit Dokumenten auswählen
        companies = database.list_companies()
        test_company = None
        
        for company in companies:
            company_id = company.get('id')
            documents = database.list_company_documents(company_id)
            if documents:
                test_company = company
                break
        
        if not test_company:
            print("⚠️  Keine Firma mit Dokumenten für PDF-Test gefunden")
            return
        
        company_name = test_company.get('name')
        company_id = test_company.get('id')
        
        print(f"🧪 Test-Firma: {company_name} (ID: {company_id})")
        
        # PDF-Optionen mit Firmendokumenten
        pdf_options = {
            'company_documents_active': True,
            'company_documents_mode': 'standard_types',
            'company_documents_standard_types': ['Datenblatt', 'Garantie', 'Zertifikat'],
            'include_diagrams': True,
            'include_images': True,
            'document_style': 'modern'
        }
        
        # Dokumente für diese Firma abrufen
        doc_ids = generator.get_company_documents_for_pdf(company_id, pdf_options)
        print(f"📄 Dokument-IDs für PDF: {doc_ids}")
        
        if doc_ids:
            print("✅ Dokumente gefunden - PDF-Integration sollte funktionieren")
        else:
            print("⚠️  Keine Dokumente gefunden - PDF wird ohne Firmendokumente erstellt")
            
    except Exception as e:
        print(f"✗ Fehler beim PDF-Integration Test: {e}")

if __name__ == "__main__":
    print("Starte Firmendokumente-Debug-Analyse...")
    
    try:
        analyze_company_documents()
        test_pdf_integration()
        
        print(f"\n🎯 EMPFEHLUNGEN:")
        print("1. Prüfen Sie die Dateipfade für Dokumente mit Status 'Datei existiert nicht'")
        print("2. Überprüfen Sie die Filterlogik in get_company_documents_for_pdf")
        print("3. Stellen Sie sicher, dass alle PDF-Optionen korrekt übergeben werden")
        print("4. Testen Sie die PDF-Generierung mit Debug-Ausgaben für problematische Firmen")
        
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
