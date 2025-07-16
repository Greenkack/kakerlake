"""
Testskript für die PDF-Generierung nach dem Bugfix.
Dieses Skript generiert eine PDF mit Testdaten, um zu prüfen, 
ob die Fallback-Logik korrekt funktioniert.
"""
import os
import traceback
import base64
from typing import Dict, Any

# Demo-Daten für die PDF-Generierung
def get_test_data():
    # Minimale Daten, die für die PDF-Generierung ausreichen sollten
    project_data = {
        'customer_data': {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'address': 'Teststraße 123',
            'zip': '12345',
            'city': 'Teststadt',
            'email': 'max.mustermann@example.com'
        },
        'pv_details': {
            'selected_modules': [{'id': 123, 'name': 'Test-Modul 380W', 'power_wp': 380}],
            'module_quantity': 20
        },
        'project_details': {
            'selected_inverter_id': 456,
            'selected_inverter_name': 'Test-Wechselrichter 5kW',
            'house_type': 'Einfamilienhaus',
            'roof_type': 'Satteldach',
            'orientation': 'Süd'
        },
        'company_information': {
            'name': 'SolarDING Test-GmbH',
            'street': 'Firmenstraße 1',
            'zip': '54321',
            'city': 'Firmenstadt',
            'phone': '+49 123 4567890',
            'email': 'info@solarding-test.de',
            'website': 'www.solarding-test.de'
        }
    }
    
    analysis_results = {
        'anlage_kwp': 7.6,
        'annual_pv_production_kwh': 7500,
        'total_investment_cost_netto': 12000,
        'autarkie_anteil_prozent': 60,
        'eigenverbrauchs_anteil_prozent': 40,
        'yearly_co2_saved_kg': 3500,
        'amortization_years': 10.5,
        'stromkosten_alt_jahr': 2000,
        'stromkosten_neu_jahr': 800
    }
    
    # Basistexte für die PDF-Generierung
    texts = {
        'pdf_title': 'Photovoltaik-Angebot',
        'pdf_warning_no_customer_name': 'Kein Kundenname verfügbar',
        'pdf_warning_no_modules': 'Keine PV-Module ausgewählt',
        'pdf_error_no_analysis': 'Keine Analyseergebnisse verfügbar',
        'pdf_warning_no_company': 'Keine Firmendaten verfügbar',
        'not_applicable_short': 'k.A.',
        'pdf_cover_letter_default': 'Sehr geehrte(r) [Anrede] [Nachname],\n\nvielen Dank für Ihr Interesse an einer Photovoltaikanlage. Anbei finden Sie unser Angebot.'
    }
    
    return project_data, analysis_results, texts

def test_pdf_generation():
    try:
        print("\n=== TEST: PDF-GENERIERUNG ===")
        
        from pdf_generator import generate_offer_pdf
        
        # Testdaten laden
        project_data, analysis_results, texts = get_test_data()
        
        print("1. PDF mit vollständigen Daten generieren...")
        pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=project_data.get('company_information', {}),
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Photovoltaik-Angebot",
            selected_cover_letter_text="Sehr geehrte(r) [Anrede] [Nachname],\n\nvielen Dank für Ihr Interesse.",
            sections_to_include=["overview", "products", "economics"],
            inclusion_options={
                'include_company_logo': False,
                'include_product_images': True,
                'include_all_documents': False,
                'company_document_ids_to_include': [],
                'include_optional_component_details': True,
                'include_custom_footer': True,
                'include_header_logo': False
            },
            load_admin_setting_func=lambda key, default: default,
            save_admin_setting_func=lambda key, value: None,
            list_products_func=lambda: [],
            get_product_by_id_func=lambda id: None,
            db_list_company_documents_func=lambda company_id, doc_type=None: [],
            active_company_id=1,
            texts=texts
        )
        
        if pdf_bytes:
            with open("test_pdf_with_data.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("✅ PDF mit vollständigen Daten erfolgreich generiert: test_pdf_with_data.pdf")
        else:
            print("❌ PDF-Generierung fehlgeschlagen, keine Bytes zurückgegeben")
            return False
        
        print("\n2. Validierung der Daten testen...")
        from pdf_generator import _validate_pdf_data_availability
        
        validation_result = _validate_pdf_data_availability(project_data, analysis_results, texts)
        print(f"Validierungsergebnis: gültig={validation_result['is_valid']}")
        print(f"Warnungen: {len(validation_result['warnings'])}")
        print(f"Kritische Fehler: {len(validation_result['critical_errors'])}")
        
        if not validation_result['is_valid']:
            print("❌ Validierung fehlgeschlagen, obwohl Daten vollständig sind")
            return False
        
        print("\n3. PDF mit unvollständigen Daten (Fallback testen)...")
        
        # Leere Analyseergebnisse für Fallback-Test
        empty_analysis = {}
        
        fallback_pdf_bytes = generate_offer_pdf(
            project_data=project_data,
            analysis_results=empty_analysis,  # Leere Analyseergebnisse sollten zum Fallback führen
            company_info=project_data.get('company_information', {}),
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Photovoltaik-Angebot",
            selected_cover_letter_text="Sehr geehrte(r) [Anrede] [Nachname],\n\nvielen Dank für Ihr Interesse.",
            sections_to_include=["overview", "products", "economics"],
            inclusion_options={
                'include_company_logo': False,
                'include_product_images': True,
                'include_all_documents': False,
                'company_document_ids_to_include': [],
                'include_optional_component_details': True,
                'include_custom_footer': True,
                'include_header_logo': False
            },
            load_admin_setting_func=lambda key, default: default,
            save_admin_setting_func=lambda key, value: None,
            list_products_func=lambda: [],
            get_product_by_id_func=lambda id: None,
            db_list_company_documents_func=lambda company_id, doc_type=None: [],
            active_company_id=1,
            texts=texts
        )
        
        if fallback_pdf_bytes:
            with open("test_fallback_pdf.pdf", "wb") as f:
                f.write(fallback_pdf_bytes)
            print("✅ Fallback-PDF erfolgreich generiert: test_fallback_pdf.pdf")
        else:
            print("❌ Fallback-PDF-Generierung fehlgeschlagen")
            return False
        
        # Validierung der leeren Daten sollte false zurückgeben
        fallback_validation = _validate_pdf_data_availability(project_data, empty_analysis, texts)
        if not fallback_validation['is_valid']:
            print("✅ Validierung mit leeren Analysedaten korrekt als ungültig erkannt")
        else:
            print("❌ Fehlerhaftes Validierungsergebnis bei leeren Analysedaten")
        
        print("\n=== PDF-GENERIERUNG ERFOLGREICH GETESTET ===")
        return True
    except Exception as e:
        print(f"❌ Fehler bei der PDF-Generierung: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_pdf_generation():
        print("\n✅✅✅ TEST ERFOLGREICH: Die PDF-Generierung funktioniert korrekt!")
    else:
        print("\n❌❌❌ TEST FEHLGESCHLAGEN: Es gibt noch Probleme mit der PDF-Generierung.")
