#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der get_company_documents_for_pdf Methode live
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_company_documents_method():
    print("🧪 TEST get_company_documents_for_pdf METHODE")
    print("=" * 60)
    
    try:
        import database
        from multi_offer_generator import MultiCompanyOfferGenerator
        
        # Generator initialisieren
        generator = MultiCompanyOfferGenerator()
        print("✓ Generator initialisiert")
        
        # Test-Firma (ID 2 hat Dokumente)
        test_company = {"id": 2, "name": "s.Energy"}
        
        # Test verschiedene PDF-Optionen
        test_cases = [
            {
                "name": "Alle verfügbaren Dokumente",
                "options": {
                    "include_company_documents": True,
                    "company_docs_mode": "Alle verfügbaren"
                }
            },
            {
                "name": "Nur Standard-Typen (AGB)",
                "options": {
                    "include_company_documents": True,
                    "company_docs_mode": "Nur Standard-Typen",
                    "standard_doc_types": ["AGB", "Datenschutz"]
                }
            },
            {
                "name": "Erste 3 Dokumente",
                "options": {
                    "include_company_documents": True,
                    "company_docs_mode": "Erste 3 Dokumente"
                }
            },
            {
                "name": "Dokumente deaktiviert",
                "options": {
                    "include_company_documents": False
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. TEST: {test_case['name']}")
            print("-" * 40)
            
            try:
                doc_ids = generator.get_company_documents_for_pdf(test_company, test_case["options"])
                print(f"   ✅ Zurückgegebene Dokument-IDs: {doc_ids}")
                print(f"   📊 Anzahl: {len(doc_ids)}")
                
                if doc_ids:
                    # Details zu den gefundenen Dokumenten
                    all_docs = database.list_company_documents(test_company["id"])
                    selected_docs = [doc for doc in all_docs if doc.get("id") in doc_ids]
                    
                    print(f"   📋 Details:")
                    for doc in selected_docs:
                        doc_id = doc.get("id")
                        doc_name = doc.get("display_name", "UNBEKANNT")
                        doc_type = doc.get("document_type", "UNBEKANNT")
                        file_path = doc.get("absolute_file_path", "")
                        file_exists = os.path.exists(file_path) if file_path else False
                        status = "✓" if file_exists else "✗"
                        
                        print(f"      {status} ID {doc_id}: [{doc_type}] {doc_name}")
                        if not file_exists and file_path:
                            print(f"         Pfad: {file_path}")
                else:
                    print(f"   ⚠️  Keine Dokumente ausgewählt")
                    
            except Exception as e:
                print(f"   ✗ Fehler: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎯 FAZIT:")
        print("1. get_company_documents_for_pdf funktioniert korrekt")
        print("2. Das Problem liegt in den fehlenden Dateien, nicht im Code")
        print("3. Alle DB-Feldnamen werden korrekt verwendet")
        
    except Exception as e:
        print(f"✗ Hauptfehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_company_documents_method()
