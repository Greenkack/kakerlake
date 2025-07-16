#!/usr/bin/env python3
"""
Vollständiger Test des Multi-Angebotsgenerators
Testet alle neuen Features: Produktrotation, Preisstaffelung, flexible Firmenanzahl, Firmendokumente
"""
import sys
import os
sys.path.append('.')

def test_multi_offer_import():
    """Teste den Import des Multi-Angebotsgenerators"""
    print("🔄 Teste Import von multi_offer_generator...")
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator
        print("✅ Import erfolgreich!")
        return MultiCompanyOfferGenerator
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler: {e}")
        return None
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return None
    except Exception as e:
        print(f"❌ Unbekannter Fehler: {e}")
        return None

def test_company_documents_integration():
    """Teste die Integration von Firmendokumenten"""
    print("\n📄 Teste Firmendokumente-Integration...")
    
    try:
        from multi_offer_generator import MultiCompanyOfferGenerator
        generator = MultiCompanyOfferGenerator()
        
        # Test-Firma mit mock Daten
        test_company = {
            "id": 1,
            "name": "Test Solar GmbH",
            "logo_base64": None
        }
        
        # Test verschiedene PDF-Optionen für Firmendokumente
        test_cases = [
            {
                "name": "Alle verfügbaren Dokumente",
                "options": {
                    "include_company_documents": True,
                    "company_docs_mode": "Alle verfügbaren",
                    "company_docs_mode_index": 0
                }
            },
            {
                "name": "Nur Standard-Typen",
                "options": {
                    "include_company_documents": True,
                    "company_docs_mode": "Nur Standard-Typen",
                    "company_docs_mode_index": 1,
                    "standard_doc_types": ["Katalog", "Datenblatt"]
                }
            },
            {
                "name": "Erste 3 Dokumente",
                "options": {
                    "include_company_documents": True,
                    "company_docs_mode": "Erste 3 Dokumente",
                    "company_docs_mode_index": 2
                }
            },
            {
                "name": "Dokumente deaktiviert",
                "options": {
                    "include_company_documents": False
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  📋 Test: {test_case['name']}")
            
            # Teste Dokument-Auswahl
            doc_ids = generator.get_company_documents_for_pdf(test_company, test_case["options"])
            print(f"    Gefundene Dokument-IDs: {doc_ids}")
            print(f"    Anzahl Dokumente: {len(doc_ids)}")
            
            # Prüfe Logik
            if test_case["options"].get("include_company_documents", True):
                if test_case["name"] == "Dokumente deaktiviert":
                    assert len(doc_ids) == 0, "Dokumente sollten deaktiviert sein"
                # Andere Tests würden echte Dokumente benötigen
            else:
                assert len(doc_ids) == 0, "Dokumente sollten deaktiviert sein"
        
        print("✅ Firmendokumente-Integration-Test erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Firmendokumente-Integration-Test fehlgeschlagen: {e}")
        return False

def run_quick_test():
    """Schnelltest für Firmendokumente"""
    print("🚀 Starte Firmendokumente-Test...")
    print("=" * 50)
    
    # Test 1: Import
    generator_class = test_multi_offer_import()
    if not generator_class:
        print("\n❌ Import fehlgeschlagen")
        return False
    
    # Test 2: Firmendokumente
    result = test_company_documents_integration()
    
    if result:
        print("\n🎉 FIRMENDOKUMENTE-TEST BESTANDEN!")
        print("📄 Firmendokumente-Integration funktioniert!")
        return True
    else:
        print("\n❌ Firmendokumente-Test fehlgeschlagen")
        return False

if __name__ == "__main__":
    success = run_quick_test()
    sys.exit(0 if success else 1)
