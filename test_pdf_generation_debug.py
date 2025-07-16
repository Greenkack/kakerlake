# test_pdf_generation_debug.py
"""
Test der PDF-Generierung mit dem Multi-Offer-Generator
"""
import os
import sys
from datetime import datetime

# Streamlit Session State Mock für Tests
class MockSessionState:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __contains__(self, key):
        return key in self.data

# Mock Streamlit für Tests
import streamlit as st
if not hasattr(st, 'session_state'):
    st.session_state = MockSessionState()

try:
    print("🔄 Teste PDF-Generierung...")
    
    # Imports
    from multi_offer_generator import MultiCompanyOfferGenerator
    from database import get_db_connection, list_companies, get_company
    from product_db import list_products, get_product_by_id
    from calculations import perform_calculations
    
    print("✅ Imports erfolgreich")
    
    # Generator initialisieren
    generator = MultiCompanyOfferGenerator()
    
    # Testdaten vorbereiten
    customer_data = {
        'customer_name': 'Test Kunde',
        'customer_address': 'Teststraße 123',
        'customer_city': '12345 Teststadt',
        'customer_phone': '+49 123 456789',
        'customer_email': 'test@example.com'
    }
    
    project_data = {
        'customer_data': customer_data,
        'roof_area': 100,
        'yearly_consumption': 4000,
        'roof_orientation': 'South',
        'roof_tilt': 30
    }
    
    # Firmen laden
    companies = list_companies()
    if not companies:
        print("❌ Keine Firmen in der Datenbank gefunden")
        sys.exit(1)
    
    test_company = companies[0]
    print(f"✅ Test-Firma: {test_company['name']}")
      # Berechnungen durchführen
    texts = {
        'kwp_unit': 'kWp',
        'kwh_unit': 'kWh',
        'euro_unit': '€'
    }
    errors_list = []
    calc_results = perform_calculations(project_data, texts, errors_list)
    print("✅ Berechnungen abgeschlossen")
    
    # PDF-Optionen
    pdf_options = {
        'include_charts': True,
        'include_company_logo': True,
        'include_product_images': True,
        'chart_types': ['monthly_generation', 'yearly_comparison']
    }
    
    # Test: Ein einzelnes PDF generieren
    print("🔄 Teste PDF-Generierung für eine Firma...")
    
    try:
        # Angebotsdaten vorbereiten
        offer_data = generator._prepare_offer_data(
            customer_data=customer_data,
            company=test_company,
            settings=pdf_options,
            project_data=project_data,
            company_index=0
        )
        print("✅ Angebotsdaten vorbereitet")        # PDF generieren
        try:
            pdf_bytes = generator._generate_company_pdf(
                offer_data=offer_data,
                company=test_company,
                company_index=0
            )
        except Exception as e:
            print(f"❌ Detaillierter Fehler bei PDF-Generierung: {e}")
            import traceback
            print("🔍 Vollständiger Stacktrace:")
            traceback.print_exc()
            pdf_bytes = None
        
        if pdf_bytes is None:
            print("❌ PDF-Generierung gab None zurück")
        else:
            print("✅ PDF erfolgreich generiert!")
            print(f"📄 PDF-Größe: {len(pdf_bytes)} Bytes")
        
        # PDF speichern
        output_path = f"test_multi_offer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"💾 PDF gespeichert als: {output_path}")
        
    except Exception as e:
        print(f"❌ Fehler bei PDF-Generierung: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
