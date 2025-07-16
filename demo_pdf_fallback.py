#!/usr/bin/env python3
"""
Demo der PDF-Fallback-Funktionalität bei fehlenden Daten
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_pdf_fallback_scenarios():
    """Demonstriert verschiedene Fallback-Szenarien"""
    
    print("Demo: PDF-Fallback bei verschiedenen Datenszenarien")
    print("=" * 60)
    
    from pdf_generator import generate_offer_pdf, _validate_pdf_data_availability, _create_no_data_fallback_pdf
    
    # Dummy-Funktionen für Demo
    def dummy_func(*args, **kwargs):
        return []
    
    texts = {
        'pdf_warning_no_customer_name': 'Kein Kundenname verfügbar - wird als "Kunde" angezeigt',
        'pdf_warning_no_modules': 'Keine PV-Module ausgewählt - Standardwerte werden verwendet',
        'pdf_error_no_analysis': 'Keine Analyseergebnisse verfügbar - PDF kann nicht erstellt werden',
        'pdf_warning_no_company': 'Keine Firmendaten verfügbar - Fallback wird verwendet',
        'pdf_no_data_title': 'Photovoltaik-Angebot - Datensammlung erforderlich',
        'pdf_no_data_customer': 'Für: {customer_name}',
        'pdf_no_data_main_text': '''Liebe Kundin, lieber Kunde,
        
für die Erstellung Ihres individuellen Photovoltaik-Angebots benötigen wir noch einige wichtige Informationen:

<b>Erforderliche Daten:</b>
• Ihre Kontaktdaten (vollständig)
• Gewünschte PV-Module und Komponenten
• Stromverbrauchsdaten Ihres Haushalts
• Technische Angaben zu Ihrem Dach/Standort

<b>Nächste Schritte:</b>
1. Vervollständigen Sie die Dateneingabe in der Anwendung
2. Führen Sie die Wirtschaftlichkeitsberechnung durch
3. Generieren Sie anschließend Ihr personalisiertes PDF-Angebot

Bei Fragen stehen wir Ihnen gerne zur Verfügung!''',
        'pdf_no_data_contact': 'Kontakt: Bitte wenden Sie sich an unser Beratungsteam für weitere Unterstützung.'
    }
    
    # Szenario 1: Komplett leere Daten
    print("\nSzenario 1: Komplett leere Daten")
    empty_data = {}
    empty_analysis = {}
    
    try:
        pdf_bytes = generate_offer_pdf(
            project_data=empty_data,
            analysis_results=empty_analysis,
            company_info={'name': 'Demo Firma'},
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text='Demo Angebot',
            selected_cover_letter_text='Demo Anschreiben',
            sections_to_include=['ProjectOverview'],
            inclusion_options={},
            load_admin_setting_func=dummy_func,
            save_admin_setting_func=dummy_func,
            list_products_func=dummy_func,
            get_product_by_id_func=dummy_func,
            db_list_company_documents_func=dummy_func,
            active_company_id=1,
            texts=texts
        )
        
        if pdf_bytes:
            print(f"Fallback-PDF erstellt: {len(pdf_bytes)} Bytes")
            
            # PDF speichern für Demo
            with open('demo_fallback_empty.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("Fallback-PDF gespeichert als: demo_fallback_empty.pdf")
        else:
            print("Keine PDF erstellt")
            
    except Exception as e:
        print(f"Fehler: {e}")
    
    # Szenario 2: Teilweise verfügbare Daten
    print("\nSzenario 2: Teilweise verfügbare Daten")
    partial_data = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'email': 'max.mustermann@example.com'
        },
        'pv_details': {
            'module_quantity': 20,
            'selected_modules': [1, 2]
        }
    }
    partial_analysis = {
        'anlage_kwp': 8.5,
        'annual_pv_production_kwh': 8500
    }
    
    validation = _validate_pdf_data_availability(partial_data, partial_analysis, texts)
    print(f"Validierung: Gültig={validation['is_valid']}, Warnungen={len(validation['warnings'])}")
    
    try:
        pdf_bytes = generate_offer_pdf(
            project_data=partial_data,
            analysis_results=partial_analysis,
            company_info={'name': 'Demo Solar GmbH', 'id': 1},
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text='Ihr Photovoltaik-Angebot',
            selected_cover_letter_text='Sehr geehrter Herr Mustermann,\n\nvielen Dank für Ihr Interesse an unserer Photovoltaikanlage.',
            sections_to_include=['ProjectOverview', 'CO2Savings'],
            inclusion_options={'include_product_images': False},
            load_admin_setting_func=dummy_func,
            save_admin_setting_func=dummy_func,
            list_products_func=dummy_func,
            get_product_by_id_func=dummy_func,
            db_list_company_documents_func=dummy_func,
            active_company_id=1,
            texts=texts
        )
        
        if pdf_bytes:
            print(f"Vollständige PDF erstellt: {len(pdf_bytes)} Bytes")
            
            # PDF speichern für Demo
            with open('demo_partial_data.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("Teilweise-Daten-PDF gespeichert als: demo_partial_data.pdf")
        else:
            print("Keine PDF erstellt")
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Demo abgeschlossen!")
    print("\n Das System erstellt automatisch:")
    print("   • Fallback-PDFs bei fehlenden kritischen Daten")
    print("   • Vollständige PDFs mit Warnhinweisen bei unvollständigen Daten")
    print("   • Detaillierte Validierungsberichte für Entwickler")

if __name__ == "__main__":
    demo_pdf_fallback_scenarios()
