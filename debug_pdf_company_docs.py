#!/usr/bin/env python3
"""
Debug-Test: PDF-Generator mit detailliertem Logging
"""

import sys
import os
import logging
from datetime import datetime
import io

# Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("=" * 80)
    print("DEBUG-TEST: PDF-Generator Firmendokumente")
    print("=" * 80)
    
    try:
        from database import list_companies, list_company_documents, get_company
        from pdf_generator import generate_offer_pdf
        
        # Mock Funktionen
        def list_products(): return []
        def get_product_by_id(id): return {}
        def load_admin_setting(key, default=None): 
            print(f"DEBUG load_admin_setting: {key} -> {default}")
            return default
        def save_admin_setting(key, value): 
            print(f"DEBUG save_admin_setting: {key} = {value}")
        
        # 1. Erste Firma mit Dokumenten finden
        all_companies = list_companies()
        test_company = None
        for company in all_companies:
            docs = list_company_documents(company.get('id'), None)
            if docs and len(docs) >= 1:
                test_company = company
                print(f"\\nVerwendete Test-Firma: {company.get('name')} (ID: {company.get('id')})")
                print(f"Verfügbare Dokumente: {len(docs)}")
                for doc in docs:
                    doc_path = doc.get('absolute_file_path')
                    exists = os.path.exists(doc_path) if doc_path else False
                    print(f"  - {doc.get('display_name')} (ID: {doc.get('id')}) -> {exists}")
                break
        
        if not test_company:
            print("Keine Firma mit Dokumenten gefunden!")
            return
        
        # 2. Test-Daten vorbereiten
        company_id = test_company.get('id')
        all_docs = list_company_documents(company_id, None)
        test_doc_ids = [doc.get('id') for doc in all_docs[:2]]  # Erste 2 Dokumente
        
        print(f"\\nTest-Dokument-IDs: {test_doc_ids}")
        
        # 3. Minimale PDF-Daten
        project_data = {
            'customer_name': 'Max Mustermann',
            'customer_address': 'Musterstraße 123',
            'customer_city': '12345 Musterstadt',
            'project_details': {
                'module_quantity': 20,
                'include_storage': True,
                'include_additional_components': True
            }
        }
        
        analysis_results = {
            'total_cost': 25000,
            'annual_savings': 1500,
            'payback_period': 16.7,
            'co2_savings_annual': 2500
        }
        
        # 4. PDF-Generierung mit Debug
        print("\\n=== PDF-GENERIERUNG START ===")
        
        # Füge detailliertes Logging zur PDF-Generator-Funktion hinzu
        inclusion_options = {
            "include_company_logo": True,
            "include_product_images": True,
            "include_all_documents": False,
            "company_document_ids_to_include": test_doc_ids,  # ECHTE IDs!
            "include_optional_component_details": True,
        }
        
        print(f"inclusion_options: {inclusion_options}")
        
        pdf_content = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=test_company,
            company_logo_base64=test_company.get("logo_base64"),
            selected_title_image_b64=None,
            selected_offer_title_text=f"Test-Angebot von {test_company.get('name')}",
            selected_cover_letter_text="Test-Anschreiben",
            sections_to_include=["ProjectOverview", "TechnicalComponents"],
            inclusion_options=inclusion_options,
            texts={},
            list_products_func=list_products,
            get_product_by_id_func=get_product_by_id,
            load_admin_setting_func=load_admin_setting,
            save_admin_setting_func=save_admin_setting,
            db_list_company_documents_func=list_company_documents,  # ECHTE FUNKTION!
            active_company_id=company_id  # ECHTE COMPANY-ID!
        )
        
        print("\\n=== PDF-GENERIERUNG ENDE ===")
        
        if pdf_content and len(pdf_content) > 1000:
            pdf_size = len(pdf_content)
            print(f"\\n✓ PDF generiert: {pdf_size:,} Bytes")
            
            # PDF speichern
            output_filename = f"debug_pdf_with_company_docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(output_filename, 'wb') as f:
                f.write(pdf_content)
            print(f"✓ Gespeichert als: {output_filename}")
            
            # Größe bewerten
            if pdf_size > 50000:  # > 50KB
                print("✓ PDF-Größe deutet auf eingebundene Dokumente hin")
            else:
                print("⚠️ PDF-Größe klein - möglicherweise keine Dokumente eingebunden")
                
            # Validierung: Prüfe ob die Funktion korrekt aufgerufen wurde
            print("\\n=== VALIDIERUNG ===")
            print(f"✓ active_company_id übergeben: {company_id}")
            print(f"✓ company_document_ids_to_include: {test_doc_ids}")
            print(f"✓ db_list_company_documents_func: {callable(list_company_documents)}")
            
            # Teste nochmal direkt die Funktion
            print("\\n=== DIREKTE FUNKTIONSTEST ===")
            direct_docs = list_company_documents(company_id, None)
            print(f"Direkte DB-Abfrage: {len(direct_docs)} Dokumente")
            for doc in direct_docs:
                if doc.get('id') in test_doc_ids:
                    doc_path = doc.get('absolute_file_path')
                    exists = os.path.exists(doc_path) if doc_path else False
                    print(f"  - Zu inkludieren: {doc.get('display_name')} -> Datei existiert: {exists}")
                    
        else:
            print(f"✗ PDF-Generierung fehlgeschlagen: {len(pdf_content) if pdf_content else 0} Bytes")
        
    except Exception as e:
        print(f"\\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
