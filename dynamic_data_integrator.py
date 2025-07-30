#!/usr/bin/env python3
"""
DYNAMIC DATA INTEGRATION FOR TOM-90 PDF
=======================================
Integriert echte Daten aus der Bedarfsanalyse in das PDF-Rendering
"""

import os
import re
from typing import Dict, Any, Optional

class DynamicDataIntegrator:
    """Integriert echte Kundendaten in das PDF-System"""
    
    def __init__(self):
        self.data_mappings = {}
        
    def prepare_dynamic_data(self, 
                           project_data: Dict[str, Any],
                           analysis_results: Dict[str, Any], 
                           company_info: Dict[str, Any],
                           customer_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Bereitet alle dynamischen Daten für das PDF vor"""
        
        print("🔄 Bereite dynamische Daten für PDF vor...")
        
        # Extrahiere Kundendaten
        customer_name = self._extract_customer_name(project_data, customer_data)
        customer_address = self._extract_customer_address(project_data, customer_data)
        
        # Extrahiere technische Daten
        technical_data = self._extract_technical_data(analysis_results)
        
        # Extrahiere Finanzdaten
        financial_data = self._extract_financial_data(analysis_results)
        
        # Extrahiere Firmendaten
        company_data = self._extract_company_data(company_info)
        
        # Kombiniere alle Daten
        dynamic_data = {
            # === KUNDENDATEN ===
            'customer_name': customer_name,
            'customer_address_street': customer_address.get('street', 'Musterstraße 1'),
            'customer_address_city': customer_address.get('city', '12345 Musterstadt'),
            
            # === TECHNISCHE DATEN ===
            'anlage_kwp': technical_data.get('anlage_kwp', '8,4'),
            'battery_capacity_kwh': technical_data.get('battery_capacity', '6,1'),
            'annual_consumption_kwh': technical_data.get('annual_consumption', '6.000'),
            'annual_pv_production_kwh': technical_data.get('annual_production', '8.251,92'),
            'module_quantity': technical_data.get('module_count', '21'),
            'roof_angle': technical_data.get('roof_angle', '30'),
            'independence_degree_percent': technical_data.get('independence', '54%'),
            'self_consumption_percent': technical_data.get('self_consumption', '42%'),
            
            # === FINANZDATEN ===
            'total_savings_with_storage_eur': financial_data.get('savings_with_storage', '36.958'),
            'total_savings_with_storage_eur_formatted': financial_data.get('savings_with_storage_formatted', '36.958,00 EUR'),
            'total_savings_without_storage_eur': financial_data.get('savings_without_storage', '29.150'),
            'total_savings_without_storage_eur_formatted': financial_data.get('savings_without_storage_formatted', '29.150,00 EUR'),
            
            # === UMWELTDATEN ===
            'co2_savings_km_equivalent': financial_data.get('co2_savings_km', '15.266'),
            
            # === FIRMENDATEN ===
            'company_name': company_data.get('name', 'Ihre Solar-Firma'),
            'company_email': company_data.get('email', 'info@solar-firma.de'),
            'company_website': company_data.get('website', 'www.solar-firma.de'),
            'company_phone': company_data.get('phone', '0123456789'),
            'company_address_street': company_data.get('street', 'Firmenstraße 1'),
            'company_address_city': company_data.get('city', '12345 Firmenstadt'),
            'company_tax_id': company_data.get('tax_id', 'DE123456789'),
            
            # === PROJEKT-DATEN ===
            'project_id': self._generate_project_id(),
            'current_date': self._get_current_date(),
        }
        
        print(f"✅ {len(dynamic_data)} dynamische Werte vorbereitet")
        return dynamic_data
    
    def _extract_customer_name(self, project_data: Dict, customer_data: Optional[Dict]) -> str:
        """Extrahiert Kundenname aus den verfügbaren Daten"""
        
        # Verschiedene Quellen prüfen
        sources = [
            customer_data.get('name') if customer_data else None,
            customer_data.get('customer_name') if customer_data else None,
            project_data.get('customer_name'),
            project_data.get('kunde_name'),
            project_data.get('project_details', {}).get('customer_name'),
            project_data.get('project_details', {}).get('kunde_name'),
            "Geschätzter Kunde"  # Fallback
        ]
        
        for source in sources:
            if source and isinstance(source, str) and source.strip():
                return source.strip()
        
        return "Geschätzter Kunde"
    
    def _extract_customer_address(self, project_data: Dict, customer_data: Optional[Dict]) -> Dict[str, str]:
        """Extrahiert Kundenadresse"""
        
        address = {}
        
        # Straße
        street_sources = [
            customer_data.get('address_street') if customer_data else None,
            customer_data.get('street') if customer_data else None,
            project_data.get('customer_address'),
            project_data.get('address'),
        ]
        
        for street in street_sources:
            if street and isinstance(street, str) and street.strip():
                address['street'] = street.strip()
                break
        
        # Stadt
        city_sources = [
            customer_data.get('address_city') if customer_data else None,
            customer_data.get('city') if customer_data else None,
            project_data.get('customer_city'),
            project_data.get('city'),
        ]
        
        for city in city_sources:
            if city and isinstance(city, str) and city.strip():
                address['city'] = city.strip()
                break
        
        return address
    
    def _extract_technical_data(self, analysis_results: Dict) -> Dict[str, Any]:
        """Extrahiert technische Daten"""
        
        technical = {}
        
        # Anlagengröße kWp
        anlage_kwp = analysis_results.get('anlage_kwp') or analysis_results.get('peak_power_kw') or 8.4
        try:
            technical['anlage_kwp'] = f"{float(anlage_kwp):,.1f}".replace(',', '.')
        except:
            technical['anlage_kwp'] = '8,4'
        
        # Batteriekapazität
        battery = analysis_results.get('battery_capacity_kwh') or analysis_results.get('speicher_kwh') or 6.1
        try:
            technical['battery_capacity'] = f"{float(battery):,.1f}".replace(',', '.')
        except:
            technical['battery_capacity'] = '6,1'
        
        # Jahresverbrauch
        consumption = analysis_results.get('annual_consumption_kwh') or analysis_results.get('jahresverbrauch_kwh') or 6000
        try:
            technical['annual_consumption'] = f"{int(consumption):,}".replace(',', '.')
        except:
            technical['annual_consumption'] = '6.000'
        
        # PV-Produktion
        production = analysis_results.get('annual_pv_production_kwh') or analysis_results.get('jahresertrag_kwh') or 8251.92
        try:
            technical['annual_production'] = f"{float(production):,.2f}".replace(',', '.')
        except:
            technical['annual_production'] = '8.251,92'
        
        # Module
        modules = analysis_results.get('module_quantity') or analysis_results.get('anzahl_module') or 21
        try:
            technical['module_count'] = str(int(modules))
        except:
            technical['module_count'] = '21'
        
        # Dachneigung
        angle = analysis_results.get('roof_angle') or analysis_results.get('dachneigung') or 30
        try:
            technical['roof_angle'] = str(int(angle))
        except:
            technical['roof_angle'] = '30'
        
        # Unabhängigkeitsgrad
        independence = analysis_results.get('independence_degree_percent') or analysis_results.get('autarkie_prozent') or 54
        try:
            technical['independence'] = f"{int(independence)}%"
        except:
            technical['independence'] = '54%'
        
        # Eigenverbrauch
        self_consumption = analysis_results.get('self_consumption_percent') or analysis_results.get('eigenverbrauch_prozent') or 42
        try:
            technical['self_consumption'] = f"{int(self_consumption)}%"
        except:
            technical['self_consumption'] = '42%'
        
        return technical
    
    def _extract_financial_data(self, analysis_results: Dict) -> Dict[str, Any]:
        """Extrahiert Finanzdaten"""
        
        financial = {}
        
        # Ersparnisse mit Speicher
        savings_with = analysis_results.get('total_savings_with_storage_eur') or analysis_results.get('ersparnis_mit_speicher') or 36958
        try:
            savings_val = float(savings_with)
            financial['savings_with_storage'] = f"{int(savings_val):,}".replace(',', '.')
            financial['savings_with_storage_formatted'] = f"{savings_val:,.2f} EUR".replace(',', '.')
        except:
            financial['savings_with_storage'] = '36.958'
            financial['savings_with_storage_formatted'] = '36.958,00 EUR'
        
        # Ersparnisse ohne Speicher
        savings_without = analysis_results.get('total_savings_without_storage_eur') or analysis_results.get('ersparnis_ohne_speicher') or 29150
        try:
            savings_val = float(savings_without)
            financial['savings_without_storage'] = f"{int(savings_val):,}".replace(',', '.')
            financial['savings_without_storage_formatted'] = f"{savings_val:,.2f} EUR".replace(',', '.')
        except:
            financial['savings_without_storage'] = '29.150'
            financial['savings_without_storage_formatted'] = '29.150,00 EUR'
        
        # CO2-Einsparung in km
        co2_km = analysis_results.get('co2_savings_km_equivalent') or analysis_results.get('co2_km_aequivalent') or 15266
        try:
            financial['co2_savings_km'] = f"{int(co2_km):,}".replace(',', '.')
        except:
            financial['co2_savings_km'] = '15.266'
        
        return financial
    
    def _extract_company_data(self, company_info: Dict) -> Dict[str, str]:
        """Extrahiert Firmendaten"""
        
        company = {}
        
        # Firmenname
        company['name'] = company_info.get('name') or company_info.get('company_name') or 'Ihre Solar-Firma'
        
        # Email
        company['email'] = company_info.get('email') or company_info.get('contact_email') or 'info@solar-firma.de'
        
        # Website
        website = company_info.get('website') or company_info.get('web') or 'www.solar-firma.de'
        if not website.startswith('www.'):
            website = f"www.{website}"
        company['website'] = website
        
        # Telefon
        company['phone'] = company_info.get('phone') or company_info.get('tel') or company_info.get('telefon') or '0123456789'
        
        # Adresse
        company['street'] = company_info.get('address') or company_info.get('street') or 'Firmenstraße 1'
        company['city'] = company_info.get('city') or company_info.get('plz_ort') or '12345 Firmenstadt'
        
        # Steuernummer
        company['tax_id'] = company_info.get('tax_id') or company_info.get('steuernummer') or 'DE123456789'
        
        return company
    
    def _generate_project_id(self) -> str:
        """Generiert Project-ID"""
        from datetime import datetime
        return f"AN{datetime.now().strftime('%Y')}-{datetime.now().strftime('%m%d%H%M')}"
    
    def _get_current_date(self) -> str:
        """Aktuelles Datum im deutschen Format"""
        from datetime import datetime
        return datetime.now().strftime('%d.%m.%Y')
    
    def replace_placeholders_in_text(self, text: str, dynamic_data: Dict[str, Any]) -> str:
        """Ersetzt Platzhalter in Text durch echte Daten"""
        
        if not text or not isinstance(text, str):
            return text
        
        result_text = text
        
        # Ersetze alle {key} Platzhalter
        for key, value in dynamic_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in result_text:
                result_text = result_text.replace(placeholder, str(value))
        
        return result_text

if __name__ == "__main__":
    # Test der Datenintegration
    integrator = DynamicDataIntegrator()
    
    # Test-Daten
    test_project_data = {
        'customer_name': 'Max Mustermann',
        'customer_address': 'Musterstraße 123',
        'customer_city': '12345 Musterstadt'
    }
    
    test_analysis = {
        'anlage_kwp': 9.6,
        'battery_capacity_kwh': 7.2,
        'annual_consumption_kwh': 7500,
        'total_savings_with_storage_eur': 42500
    }
    
    test_company = {
        'name': 'Solar Excellence GmbH',
        'email': 'info@solar-excellence.de',
        'phone': '0123456789'
    }
    
    # Bereite Daten vor
    dynamic_data = integrator.prepare_dynamic_data(
        test_project_data, 
        test_analysis, 
        test_company
    )
    
    print("\n📊 GENERIERTE DYNAMISCHE DATEN:")
    for key, value in dynamic_data.items():
        print(f"  {key}: {value}")
    
    # Test Text-Replacement
    test_text = "Kunde: {customer_name}, Anlage: {anlage_kwp} kWp, Ersparnis: {total_savings_with_storage_eur_formatted}"
    replaced_text = integrator.replace_placeholders_in_text(test_text, dynamic_data)
    
    print(f"\n🔄 TEXT-REPLACEMENT TEST:")
    print(f"  Original: {test_text}")
    print(f"  Ersetzt:  {replaced_text}")
