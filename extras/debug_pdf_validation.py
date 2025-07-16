"""
Debug-Skript um das Problem mit der PDF-Generierung zu identifizieren.
"""
import sys
import traceback
from typing import Dict, Any
import json

def print_separator(title: str):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def load_local_data():
    """Lädt lokale Daten aus Dateien"""
    try:
        # Dummy-Daten, wenn keine echten vorhanden sind
        project_data = {
            'customer_data': {
                'first_name': 'Max',
                'last_name': 'Mustermann'
            },
            'pv_details': {
                'selected_modules': [{'id': 123, 'name': 'Test Modul', 'power_wp': 380}],
                'module_quantity': 20
            },
            'project_details': {
                'selected_inverter_id': 456,
                'selected_inverter_name': 'Test Wechselrichter'
            },
            'company_information': {
                'name': 'SolarDING GmbH'
            }
        }
        
        analysis_results = {
            'anlage_kwp': 7.6,
            'annual_pv_production_kwh': 7500,
            'total_investment_cost_netto': 12000,
            'autarkie_anteil_prozent': 60,
            'eigenverbrauchs_anteil_prozent': 40
        }
        
        texts = {
            'pdf_warning_no_customer_name': 'Kein Kundenname verfügbar',
            'pdf_warning_no_modules': 'Keine PV-Module ausgewählt',
            'pdf_error_no_analysis': 'Keine Analyseergebnisse verfügbar',
            'pdf_warning_no_company': 'Keine Firmendaten verfügbar',
            'not_applicable_short': 'k.A.'
        }
        
        return project_data, analysis_results, texts
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        traceback.print_exc()
        return {}, {}, {}

def debug_validation_result(validation_result: Dict[str, Any]):
    """Zeigt detaillierte Informationen zum Validierungsergebnis an"""
    print_separator("VALIDIERUNGSERGEBNIS")
    print(f"Ist gültig: {'JA' if validation_result.get('is_valid', False) else 'NEIN'}")
    
    print("\nWarnungen:")
    for warning in validation_result.get('warnings', []):
        print(f" - {warning}")
    
    print("\nKritische Fehler:")
    for error in validation_result.get('critical_errors', []):
        print(f" - {error}")
    
    print("\nFehlende Daten:")
    for missing in validation_result.get('missing_data_summary', []):
        print(f" - {missing}")

def main():
    print_separator("PDF VALIDIERUNG DEBUG")
    
    try:
        # Daten laden
        project_data, analysis_results, texts = load_local_data()
        print_separator("PROJEKTDATEN")
        print(json.dumps(project_data, indent=2, ensure_ascii=False))
        
        print_separator("ANALYSEERGEBNISSE")
        print(json.dumps(analysis_results, indent=2, ensure_ascii=False))
        
        # PDF-Generator Funktionen importieren
        print_separator("IMPORT PDF GENERATOR")
        try:
            from pdf_generator import _validate_pdf_data_availability, _create_no_data_fallback_pdf
            print("PDF Generator Module erfolgreich importiert.")
        except ImportError as e:
            print(f"Fehler beim Import der PDF Generator Module: {e}")
            sys.exit(1)
        
        # Datenvalidierung durchführen
        print_separator("VALIDIERUNG DURCHFÜHREN")
        validation_result = _validate_pdf_data_availability(project_data, analysis_results, texts)
        debug_validation_result(validation_result)
        
        # Testen mit leeren Daten
        print_separator("TEST MIT LEEREN DATEN")
        empty_validation = _validate_pdf_data_availability({}, {}, texts)
        debug_validation_result(empty_validation)
        
        # Testen ob PDF generiert werden kann
        print_separator("PDF GENERIERUNGSTEST")
        try:
            from pdf_generator import generate_offer_pdf
            
            # Minimal benötigte Parameter für generate_offer_pdf
            pdf_bytes = generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=project_data.get('company_information', {}),
                company_logo_base64=None,
                selected_title_image_b64=None,
                selected_offer_title_text=None,
                selected_cover_letter_text=None,
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
                print("PDF wurde erfolgreich generiert!")
                # PDF-Bytes in Datei speichern
                with open("debug_pdf_output.pdf", "wb") as f:
                    f.write(pdf_bytes)
                print("PDF wurde als 'debug_pdf_output.pdf' gespeichert")
            else:
                print("PDF-Generierung fehlgeschlagen, keine Bytes zurückgegeben")
        except Exception as e:
            print(f"Fehler bei der PDF-Generierung: {e}")
            traceback.print_exc()
    
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
