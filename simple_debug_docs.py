#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfache Debug-Analyse für Firmendokumente-Problem
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🔍 FIRMENDOKUMENTE DEBUG-ANALYSE")
    print("=" * 60)
    
    try:
        import database
        print("✓ database.py importiert")
    except Exception as e:
        print(f"✗ database.py Import-Fehler: {e}")
        return
    
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator
        print("✓ MultiCompanyOfferGenerator importiert")
    except Exception as e:
        print(f"✗ MultiCompanyOfferGenerator Import-Fehler: {e}")
        return
    
    # Alle Firmen abrufen
    print("\n📋 FIRMEN IN DATENBANK:")
    try:
        companies = database.list_companies()
        print(f"Gefundene Firmen: {len(companies)}")
        
        for i, company in enumerate(companies, 1):
            company_id = company.get('id')
            company_name = company.get('name', 'UNBEKANNT')
            print(f"{i:2d}. {company_name} (ID: {company_id})")
            
            # Dokumente für diese Firma prüfen
            try:
                documents = database.list_company_documents(company_id)
                print(f"    📄 Dokumente: {len(documents)}")
                
                if documents:
                    valid_files = 0
                    for doc in documents:
                        file_path = doc.get('file_path', '')
                        doc_type = doc.get('type', 'UNBEKANNT')
                        doc_name = doc.get('name', 'UNBEKANNT')
                        
                        if file_path and Path(file_path).exists():
                            valid_files += 1
                            status = "✓"
                        else:
                            status = "✗"
                        
                        print(f"       {status} [{doc_type}] {doc_name}")
                        if not Path(file_path).exists():
                            print(f"           Pfad: {file_path}")
                    
                    print(f"    ✅ Gültige Dateien: {valid_files}/{len(documents)}")
                else:
                    print("    ⚠️  Keine Dokumente in DB")
                    
            except Exception as e:
                print(f"    ✗ Fehler beim Abrufen der Dokumente: {e}")
                
    except Exception as e:
        print(f"✗ Fehler beim Abrufen der Firmen: {e}")
        return
    
    # Test der MultiCompanyOfferGenerator Filterlogik
    print("\n🔍 FILTERLOGIK TEST:")
    try:
        generator = MultiCompanyOfferGenerator()
        print("✓ Generator initialisiert")
        
        # Test mit einer Firma die Dokumente hat
        test_company = None
        for company in companies:
            company_id = company.get('id')
            documents = database.list_company_documents(company_id)
            if documents:
                test_company = company
                break
        
        if test_company:
            company_id = test_company.get('id')
            company_name = test_company.get('name')
            print(f"\n🧪 Test-Firma: {company_name} (ID: {company_id})")
            
            # Standard PDF-Optionen
            pdf_options = {
                'include_company_documents': True,
                'company_docs_mode': 'Alle verfügbaren',
                'company_docs_mode_index': 0
            }
            
            # Test get_company_documents_for_pdf
            try:
                doc_ids = generator.get_company_documents_for_pdf(test_company, pdf_options)
                print(f"📄 Gefilterte Dokument-IDs: {doc_ids}")
                print(f"✅ Anzahl gefilterte Dokumente: {len(doc_ids)}")
                
                if len(doc_ids) == 0:
                    print("⚠️  PROBLEM: Keine Dokumente gefiltert obwohl welche vorhanden sind!")
                    
                    # Alternative Filteroptionen testen
                    alt_options = {
                        'include_company_documents': True,
                        'company_docs_mode': 'Nur Standard-Typen',
                        'company_docs_mode_index': 1,
                        'standard_doc_types': ['Datenblatt', 'Garantie', 'Zertifikat', 'Katalog']
                    }
                    
                    doc_ids_alt = generator.get_company_documents_for_pdf(test_company, alt_options)
                    print(f"📄 Alternative Filter - Dokument-IDs: {doc_ids_alt}")
                    print(f"✅ Alternative Filter - Anzahl: {len(doc_ids_alt)}")
                
            except Exception as e:
                print(f"✗ Fehler bei get_company_documents_for_pdf: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️  Keine Firma mit Dokumenten für Test gefunden")
            
    except Exception as e:
        print(f"✗ Fehler bei Filterlogik-Test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 ANALYSE ABGESCHLOSSEN")
    print("Falls bei manchen Firmen Dokumente fehlen:")
    print("1. Prüfen Sie die Dateipfade (✗ markierte Dokumente)")
    print("2. Überprüfen Sie die PDF-Optionen beim Multi-Generator")
    print("3. Testen Sie verschiedene Filter-Modi")

if __name__ == "__main__":
    main()
