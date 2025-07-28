#!/usr/bin/env python3
"""
Test der dynamischen Keys im TOM90 System
"""

from tom90_exact_renderer import TOM90ExactRenderer

# ERWEITERTE Test-Daten mit ALLEN neuen Keys
project_data = {
    'customer_name': 'Max Mustermann',
    'customer_address': {'street': 'Musterstraße 123', 'city': '12345 Musterstadt'},
    'annual_consumption_kwh': 7500,  # Geändert!
    'project_id': 'SUPER-SOLAR-2025',  # Neu!
    'pv_details': {'module_quantity': 25},  # Geändert!
    'roof_details': {'angle': 35},  # Geändert!
    'battery_details': {'capacity_kwh': 8.5}  # Geändert!
}

analysis_results = {
    'total_savings_with_storage_eur': 45000.0,  # Geändert!
    'total_savings_without_storage_eur': 35000.0,  # Geändert!
    'anlage_kwp': 10.5,  # Geändert!
    'annual_pv_production_kwh': 11250.0,  # Geändert!
    'independence_degree_percent': 68,  # Geändert!
    'self_consumption_percent': 55,  # Geändert!
    'annual_co2_savings_kg': 4500,  # Geändert!
}

company_info = {
    'name': 'SuperSolar GmbH',  # Geändert!
    'email': 'kontakt@supersolar.de',  # Geändert!
    'phone': '+49 30 12345678',  # Geändert!
    'website': 'www.supersolar.de',  # Neu!
    'tax_id': 'DE123456789',  # Neu!
    'address': {'street': 'Solarstraße 42', 'city': '10115 Berlin'}  # Neu!
}

print('🧪 Teste TOM90 mit dynamischen Keys...')
renderer = TOM90ExactRenderer(project_data, analysis_results, company_info)
pdf_bytes = renderer.build_pdf()

if pdf_bytes:
    with open('tom90_dynamisch_test.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print(f'✅ DYNAMISCHE 20-Seiten PDF erstellt: {len(pdf_bytes):,} bytes')
    print('🎯 ALLE neuen Werte sollten jetzt dynamisch sein!')
    print('   👤 Kunde:', project_data['customer_name'])
    print('   🏢 Firma:', company_info['name'])
    print('   ⚡ Anlage:', analysis_results['anlage_kwp'], 'kWp')
    print('   🔋 Batterie:', project_data['battery_details']['capacity_kwh'], 'kWh')
    print('   💰 Ersparnis:', f"{analysis_results['total_savings_with_storage_eur']:,}", 'EUR')
else:
    print('❌ PDF-Erstellung fehlgeschlagen')
