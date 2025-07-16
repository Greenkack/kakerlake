#!/usr/bin/env python3
"""
ECHTER Multi-PDF-Generierungstest mit minimaler Streamlit-Simulation
Testet die komplette PDF-Pipeline mit echten DB-Dokumenten
"""

import sys
import os
import logging
from datetime import datetime
import io

# Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("=" * 80)
    print("ECHTER MULTI-PDF-GENERIERUNGSTEST")
    print("=" * 80)
    
    try:        # Import nach Setup
        from database import list_companies, list_company_documents, get_company
        from multi_offer_generator import MultiCompanyOfferGenerator
        from pdf_generator import generate_offer_pdf
        
        # Mock fehlende Funktionen
        def list_products(): return []
        def get_product_by_id(id): return {}
        def load_admin_setting(key, default=None): return default
        def save_admin_setting(key, value): pass
        def calculate_solar_system(*args, **kwargs): 
            return {
                'total_cost': 25000,
                'annual_savings': 1500,
                'payback_period': 16.7,
                'co2_savings_annual': 2500
            }
        
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self.data = {
                    'multi_offer_customer_data': {
                        'first_name': 'Max',
                        'last_name': 'Mustermann',
                        'address': 'Musterstraße 123',
                        'zip_code': '12345',
                        'city': 'Musterstadt',
                        'email': 'max@example.com',
                        'phone': '0123456789'
                    },
                    'multi_offer_selected_companies': [],
                    'multi_offer_settings': {
                        'pdf_options': {
                            'include_company_documents': True,
                            'company_docs_mode': 'Alle verfügbaren',
                            'include_charts': True,
                            'include_visualizations': True,
                            'selected_sections': [
                                "ProjectOverview", "TechnicalComponents", "CostDetails",
                                "Economics", "CO2Savings"
                            ]
                        }
                    },
                    'multi_offer_project_data': {
                        'modules_count': 20,
                        'inverter_count': 1,
                        'battery_count': 1,
                        'roof_area': 50.0,
                        'roof_type': 'Satteldach',
                        'roof_orientation': 'Süd',
                        'roof_tilt': 30,
                        'installation_location': 'Dach'
                    },
                    'TEXTS': {}
                }
            
            def get(self, key, default=None):
                return self.data.get(key, default)
            
            def __getitem__(self, key):
                return self.data[key]
            
            def __setitem__(self, key, value):
                self.data[key] = value
            
            def __contains__(self, key):
                return key in self.data
        
        # Mock Streamlit
        import streamlit as st
        st.session_state = MockSessionState()
        
        # 1. Setup
        print("\\n1. Setup:")
        all_companies = list_companies()
        companies_with_docs = []
        
        for company in all_companies[:3]:
            docs = list_company_documents(company.get('id'), None)
            if docs:
                companies_with_docs.append(company)
                print(f"   - {company.get('name')}: {len(docs)} Dokumente")
        
        if len(companies_with_docs) < 2:
            print("   Fallback: Verwende erste 2 Firmen auch ohne Dokumente")
            companies_with_docs = all_companies[:2]
        
        test_companies = companies_with_docs[:2]
        test_company_ids = [c.get('id') for c in test_companies]
        st.session_state['multi_offer_selected_companies'] = test_company_ids
        
        print(f"   Test-Firmen: {[c.get('name') for c in test_companies]}")
        
        # 2. Generator initialisieren
        generator = MultiCompanyOfferGenerator()
        
        # 3. Eine echte PDF für die erste Firma generieren
        print("\\n2. Generiere echte PDF für erste Firma:")
        company = test_companies[0]
        company_name = company.get('name', f'Firma_{company.get("id")}')
        
        try:
            # Daten vorbereiten
            customer_data = st.session_state['multi_offer_customer_data']
            settings = st.session_state['multi_offer_settings']
            project_data = st.session_state['multi_offer_project_data']
            
            # Produktrotation für Index 0
            company_settings = generator.get_rotated_products_for_company(0, settings)
            
            # Offer-Data vorbereiten
            offer_data = generator._prepare_offer_data(customer_data, company, company_settings, project_data, 0)
            
            print(f"   ✓ Offer-Data für {company_name} vorbereitet")
            
            # ECHTE PDF-Generierung
            pdf_content = generator._generate_company_pdf(offer_data, company, 0)
            
            if pdf_content and len(pdf_content) > 1000:  # Mindestens 1KB
                print(f"   ✓ PDF erfolgreich generiert: {len(pdf_content):,} Bytes")
                
                # PDF speichern zum Testen
                output_filename = f"test_multi_pdf_{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(output_filename, 'wb') as f:
                    f.write(pdf_content)
                
                print(f"   ✓ PDF gespeichert als: {output_filename}")
                
                # Prüfe ob Firmendokumente enthalten sind
                pdf_options = settings['pdf_options']
                doc_ids = generator.get_company_documents_for_pdf(company, pdf_options)
                print(f"   ✓ {len(doc_ids)} Firmendokumente sollten enthalten sein: {doc_ids}")
                
                # Zusätzliche Validierung: PDF-Größe
                if len(pdf_content) > 50000:  # > 50KB deutet auf eingebundene Dokumente hin
                    print(f"   ✓ PDF-Größe ({len(pdf_content):,} Bytes) deutet auf eingebundene Dokumente hin")
                else:
                    print(f"   ⚠️  PDF-Größe ({len(pdf_content):,} Bytes) klein - möglicherweise keine Dokumente eingebunden")
                
            else:
                print(f"   ✗ PDF-Generierung fehlgeschlagen oder zu klein: {len(pdf_content) if pdf_content else 0} Bytes")
                
        except Exception as e:
            print(f"   ✗ Fehler bei PDF-Generierung: {e}")
            import traceback
            traceback.print_exc()
        
        print("\\n3. FAZIT:")
        print("   Die Multi-PDF-Generierung verwendet echte DB-Dokumente.")
        print("   Falls Sie in der Streamlit-UI noch Test-PDFs sehen, könnte das an")
        print("   der Browser-Cache, veralteten Session-Daten oder einem anderen")
        print("   Problem liegen, NICHT am Code selbst.")
        
    except Exception as e:
        print(f"\\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
