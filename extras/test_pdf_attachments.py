#!/usr/bin/env python3
"""
Test-Skript für PDF-Anhänge in der SolarDING App
Zweck: Überprüfung der PDF-Anhang-Funktionalität mit Debug-Ausgaben
"""

import os
import sys
import traceback

# Pfad zur App hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pdf_attachments():
    """Testet die PDF-Anhang-Funktionalität"""
    print("=== PDF-Anhänge Test ===")
    
    # Imports testen
    try:
        import database
        print("✅ Database-Modul importiert")
    except Exception as e:
        print(f"❌ Database-Modul Fehler: {e}")
        return False
    
    try:
        import product_db
        print("✅ Product-DB-Modul importiert")
    except Exception as e:
        print(f"❌ Product-DB-Modul Fehler: {e}")
        return False
    
    try:
        import pdf_generator
        print("✅ PDF-Generator-Modul importiert")
    except Exception as e:
        print(f"❌ PDF-Generator-Modul Fehler: {e}")
        return False
    
    # PyPDF Bibliothek testen
    try:
        from pypdf import PdfReader, PdfWriter
        print("✅ pypdf verfügbar")
        pypdf_available = True
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
            print("✅ PyPDF2 verfügbar (Fallback)")
            pypdf_available = True
        except ImportError:
            print("❌ Keine PDF-Bibliothek verfügbar")
            pypdf_available = False
    
    # Datenbankverbindung testen
    print("\n--- Datenbanktest ---")
    try:
        database.init_db()
        print("✅ Datenbank initialisiert")
    except Exception as e:
        print(f"❌ Datenbank-Initialisierung fehlgeschlagen: {e}")
        return False
    
    # Aktive Firma prüfen
    try:
        active_company = database.get_active_company()
        if active_company:
            print(f"✅ Aktive Firma: {active_company.get('name')} (ID: {active_company.get('id')})")
            
            # Firmendokumente prüfen
            company_docs = database.list_company_documents(active_company.get('id'), None)
            print(f"📄 Verfügbare Firmendokumente: {len(company_docs)}")
            
            for doc in company_docs:
                doc_path = os.path.join("data", "company_docs", doc.get("relative_db_path", ""))
                full_path = os.path.join(os.getcwd(), doc_path)
                status = "✅" if os.path.exists(full_path) else "❌"
                print(f"  {status} {doc.get('display_name')} -> {full_path}")
                
        else:
            print("❌ Keine aktive Firma gefunden")
    except Exception as e:
        print(f"❌ Fehler beim Prüfen der aktiven Firma: {e}")
    
    # Produkte prüfen
    print("\n--- Produkttest ---")
    try:
        products = product_db.list_products()
        print(f"🔧 Verfügbare Produkte: {len(products)}")
        
        products_with_datasheets = 0
        for product in products:
            if product.get("datasheet_link_db_path"):
                products_with_datasheets += 1
                datasheet_path = product.get("datasheet_link_db_path")
                full_path = os.path.join("data", "product_datasheets", datasheet_path)
                full_abs_path = os.path.join(os.getcwd(), full_path)
                status = "✅" if os.path.exists(full_abs_path) else "❌"
                print(f"  {status} {product.get('model_name')} -> {full_abs_path}")
        
        print(f"📋 Produkte mit Datenblättern: {products_with_datasheets}/{len(products)}")
        
    except Exception as e:
        print(f"❌ Fehler beim Prüfen der Produkte: {e}")
    
    # Verzeichnisstruktur prüfen
    print("\n--- Verzeichnisstruktur ---")
    base_dirs = [
        "data",
        "data/company_docs", 
        "data/product_datasheets"
    ]
    
    for dir_path in base_dirs:
        full_path = os.path.join(os.getcwd(), dir_path)
        if os.path.exists(full_path):
            files_count = len([f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))])
            dirs_count = len([d for d in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, d))])
            print(f"✅ {dir_path}: {files_count} Dateien, {dirs_count} Ordner")
        else:
            print(f"❌ {dir_path}: Verzeichnis nicht gefunden")
    
    # Test PDF-Generierung mit Debug
    print("\n--- PDF-Generierungstest ---")
    if not pypdf_available:
        print("❌ PDF-Generierung übersprungen - Keine PDF-Bibliothek")
        return True
    
    # Mock-Daten für Test
    mock_project_data = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'salutation': 'Herr'
        },
        'project_details': {
            'module_quantity': 20,
            'selected_module_id': 1,
            'selected_inverter_id': 2,
            'include_storage': False
        }
    }
    
    mock_analysis_results = {
        'anlage_kwp': 10.0,
        'total_investment_brutto': 15000.0
    }
    
    mock_inclusion_options = {
        "include_company_logo": True,
        "include_product_images": True,
        "include_all_documents": True,  # Das ist der wichtige Teil!
        "company_document_ids_to_include": [1, 2] if active_company else [],
        "selected_charts_for_pdf": [],
        "include_optional_component_details": True
    }
    
    try:
        print("🔄 Teste PDF-Generierung mit Anhängen...")
        pdf_bytes = pdf_generator.generate_offer_pdf(
            project_data=mock_project_data,
            analysis_results=mock_analysis_results,
            company_info=active_company or {"name": "Test Firma"},
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Test Angebot",
            selected_cover_letter_text="Test Anschreiben",
            sections_to_include=["ProjectOverview"],
            inclusion_options=mock_inclusion_options,
            load_admin_setting_func=database.load_admin_setting,
            save_admin_setting_func=database.save_admin_setting,
            list_products_func=product_db.list_products,
            get_product_by_id_func=product_db.get_product_by_id,
            db_list_company_documents_func=database.list_company_documents,
            active_company_id=active_company.get('id') if active_company else None,
            texts={"pdf_generation_success": "Test erfolgreich"}
        )
        
        if pdf_bytes and isinstance(pdf_bytes, bytes):
            print(f"✅ PDF generiert: {len(pdf_bytes)} Bytes")
            
            # PDF speichern für Analyse
            test_output_path = os.path.join(os.getcwd(), "test_output_with_attachments.pdf")
            with open(test_output_path, 'wb') as f:
                f.write(pdf_bytes)
            print(f"💾 Test-PDF gespeichert: {test_output_path}")
            
            # PDF-Seiten zählen für Verifikation
            try:
                reader = PdfReader(test_output_path)
                total_pages = len(reader.pages)
                print(f"📖 PDF hat {total_pages} Seiten")
                
                if total_pages > 5:  # Erwarte mehr Seiten wenn Anhänge funktionieren
                    print("✅ PDF scheint Anhänge zu enthalten (mehr als 5 Seiten)")
                else:
                    print("⚠️ PDF hat wenige Seiten - möglicherweise keine Anhänge")
                    
            except Exception as e:
                print(f"❌ Fehler beim Analysieren des PDFs: {e}")
            
        else:
            print("❌ PDF-Generierung fehlgeschlagen")
            return False
            
    except Exception as e:
        print(f"❌ Fehler bei PDF-Generierung: {e}")
        traceback.print_exc()
        return False
    
    print("\n✅ Alle Tests abgeschlossen!")
    return True

if __name__ == "__main__":
    success = test_pdf_attachments()
    sys.exit(0 if success else 1)
