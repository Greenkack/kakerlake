# doc_output_modern_integration.py
# -*- coding: utf-8 -*-
"""
Moderne PDF-Design Integration für das bestehende doc_output.py System
Vollständig optional und modular - ändert NICHTS am bestehenden Code
"""

from typing import Dict, Any, List, Optional
import os
from datetime import datetime

# Sichere Imports für optionale moderne Features
try:
    from pdf_design_enhanced_modern import (
        get_modern_design_system,
        get_modern_component_library,
        ModernPDFLayoutManager,
        enhance_existing_pdf_with_modern_design,
        get_modern_enhancement_config_template
    )
    MODERN_DESIGN_AVAILABLE = True
except ImportError:
    MODERN_DESIGN_AVAILABLE = False

try:
    from pdf_ui_design_enhancement import get_modern_design_configuration
    UI_ENHANCEMENT_AVAILABLE = True
except ImportError:
    UI_ENHANCEMENT_AVAILABLE = False

def apply_modern_pdf_enhancements(existing_story: List, 
                                calculation_results: Dict[str, Any],
                                project_data: Dict[str, Any],
                                texts: Dict[str, str]) -> List:
    """
    Wendet moderne PDF-Enhancements auf bestehende Story an
    OHNE den bestehenden Code zu ändern
    """
    
    # Prüfe Verfügbarkeit der modernen Features
    if not MODERN_DESIGN_AVAILABLE:
        return existing_story  # Keine Änderung
    
    try:
        # Hole moderne Design-Konfiguration
        if UI_ENHANCEMENT_AVAILABLE:
            try:
                enhancement_config = get_modern_design_configuration()
            except:
                enhancement_config = get_modern_enhancement_config_template()
        else:
            enhancement_config = get_modern_enhancement_config_template()
        
        # Nur anwenden wenn explizit aktiviert
        if not enhancement_config.get('enable_modern_design', False):
            return existing_story
        
        # Bereite Enhancement-Daten vor
        enhancement_config = prepare_enhancement_data(
            enhancement_config, calculation_results, project_data
        )
        
        # Erweitere bestehende Story mit modernen Features
        enhanced_story = enhance_existing_pdf_with_modern_design(
            existing_story, enhancement_config
        )
        
        return enhanced_story
        
    except Exception as e:
        # Bei Fehlern: Originale Story zurückgeben
        print(f"Fehler bei modernen PDF-Enhancements: {e}")
        return existing_story

def prepare_enhancement_data(config: Dict[str, Any], 
                           calculation_results: Dict[str, Any],
                           project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bereitet Daten für moderne Enhancements vor
    """
    
    # Summary-Daten für Executive Summary
    if config.get('add_executive_summary'):
        summary_data = {
            'total_investment': calculation_results.get('total_system_cost', 0),
            'annual_savings': calculation_results.get('annual_savings', 0),
            'payback_years': calculation_results.get('payback_period_years', 0),
            'total_return': calculation_results.get('total_profit_25_years', 0),
            'pv_power_kwp': calculation_results.get('pv_power_kwp', 0),
            'annual_production': calculation_results.get('annual_pv_production_kwh', 0),
            'self_consumption_rate': calculation_results.get('self_consumption_rate', 0)
        }
        config['summary_data'] = summary_data
    
    # Umwelt-Daten
    if config.get('add_environmental_section'):
        co2_annual = calculation_results.get('co2_savings_kg_year', 0)
        environmental_data = {
            'co2_savings': {
                'annual_kg': co2_annual,
                'lifetime_kg': co2_annual * 25,
                'equivalent_trees': (co2_annual * 25) / 22,  # ~22kg CO2/Baum/Jahr
                'equivalent_car_km': (co2_annual * 25) / 0.12  # ~120g CO2/km
            }
        }
        config['environmental_data'] = environmental_data
    
    # Finanzielle Aufschlüsselung
    if config.get('use_financial_breakdown'):
        financial_breakdown = {}
        
        # Versuche verschiedene Kostenkomponenten zu extrahieren
        cost_mapping = {
            'PV-Module': ['pv_modules_cost', 'modules_cost', 'pv_cost'],
            'Wechselrichter': ['inverter_cost', 'inverters_cost'],
            'Montagesystem': ['mounting_cost', 'mounting_system_cost'],
            'Installation': ['installation_cost', 'labor_cost'],
            'Planung': ['planning_cost', 'design_cost'],
            'Anmeldung': ['registration_cost', 'permit_cost'],
            'Sonstiges': ['misc_cost', 'other_cost']
        }
        
        for category, possible_keys in cost_mapping.items():
            for key in possible_keys:
                if calculation_results.get(key):
                    financial_breakdown[category] = calculation_results[key]
                    break
            else:
                # Schätzung basierend auf Gesamtkosten
                total_cost = calculation_results.get('total_system_cost', 0)
                if total_cost > 0:
                    if category == 'PV-Module':
                        financial_breakdown[category] = total_cost * 0.40  # ~40% für Module
                    elif category == 'Wechselrichter':
                        financial_breakdown[category] = total_cost * 0.15  # ~15% für WR
                    elif category == 'Montagesystem':
                        financial_breakdown[category] = total_cost * 0.10  # ~10% für Montage
                    elif category == 'Installation':
                        financial_breakdown[category] = total_cost * 0.20  # ~20% für Installation
                    elif category == 'Planung':
                        financial_breakdown[category] = total_cost * 0.10  # ~10% für Planung
                    elif category == 'Anmeldung':
                        financial_breakdown[category] = total_cost * 0.05  # ~5% für Anmeldung
        
        config['financial_breakdown'] = financial_breakdown
    
    # Technische Daten
    if config.get('use_technical_details'):
        technical_data = {
            'pv_modules': {
                'manufacturer': project_data.get('pv_module_manufacturer', 'Hochwertige Marke'),
                'model': project_data.get('pv_module_model', 'Premium-Modul'),
                'power_wp': project_data.get('pv_module_power', calculation_results.get('pv_power_kwp', 0) * 1000)
            },
            'inverter': {
                'manufacturer': project_data.get('inverter_manufacturer', 'Qualitäts-Hersteller'),
                'model': project_data.get('inverter_model', 'Effizienz-Wechselrichter'),
                'power_kw': project_data.get('inverter_power', calculation_results.get('pv_power_kwp', 0))
            },
            'system_architecture': {
                'module_area_m2': calculation_results.get('total_module_area_m2', 0),
                'orientation': project_data.get('roof_orientation', 'Süd'),
                'tilt_angle': project_data.get('roof_tilt', 30),
                'shading_factor': project_data.get('shading_factor', 'Minimal'),
                'expected_yield_kwh_kwp': calculation_results.get('specific_yield_kwh_kwp', 1000)
            }
        }
        
        # Batterie-Daten falls vorhanden
        if calculation_results.get('battery_capacity_kwh', 0) > 0:
            technical_data['battery'] = {
                'manufacturer': project_data.get('battery_manufacturer', 'Premium-Batterie'),
                'model': project_data.get('battery_model', 'Lithium-Speicher'),
                'capacity_kwh': calculation_results.get('battery_capacity_kwh', 0)
            }
        
        config['technical_data'] = technical_data
    
    # Produktdaten für Showcase
    if config.get('use_product_showcase'):
        products = []
        
        # PV-Module
        if calculation_results.get('pv_power_kwp', 0) > 0:
            module_count = calculation_results.get('pv_module_count', 
                                                 int(calculation_results.get('pv_power_kwp', 0) * 1000 / 400))  # ~400W pro Modul
            products.append({
                'name': f"PV-Module ({module_count} Stück)",
                'manufacturer': project_data.get('pv_module_manufacturer', 'Premium-Hersteller'),
                'model': project_data.get('pv_module_model', 'Hochleistungsmodul'),
                'description': f"Monokristalline Solarmodule mit höchster Effizienz für maximalen Ertrag.",
                'specifications': {
                    'Leistung': f"{project_data.get('pv_module_power', 400)} Wp",
                    'Effizienz': f"{project_data.get('pv_module_efficiency', 21)}%",
                    'Garantie': "25 Jahre Leistungsgarantie",
                    'Technologie': "Monokristallin"
                },
                'quantity': module_count,
                'price': calculation_results.get('pv_modules_cost', 0)
            })
        
        # Wechselrichter
        if calculation_results.get('pv_power_kwp', 0) > 0:
            products.append({
                'name': "Wechselrichter",
                'manufacturer': project_data.get('inverter_manufacturer', 'Qualitäts-Marke'),
                'model': project_data.get('inverter_model', 'String-Wechselrichter'),
                'description': "Hocheffizienter Wechselrichter für optimale Energieumwandlung.",
                'specifications': {
                    'Leistung': f"{calculation_results.get('pv_power_kwp', 0)} kW",
                    'Wirkungsgrad': f"{project_data.get('inverter_efficiency', 98)}%",
                    'Garantie': "12 Jahre Herstellergarantie",
                    'Schutzart': "IP65"
                },
                'quantity': 1,
                'price': calculation_results.get('inverter_cost', 0)
            })
        
        # Batterie falls vorhanden
        if calculation_results.get('battery_capacity_kwh', 0) > 0:
            products.append({
                'name': "Batteriespeicher",
                'manufacturer': project_data.get('battery_manufacturer', 'Speicher-Spezialist'),
                'model': project_data.get('battery_model', 'Lithium-Ionen Speicher'),
                'description': "Hochkapazitäts-Batteriespeicher für maximale Eigennutzung.",
                'specifications': {
                    'Kapazität': f"{calculation_results.get('battery_capacity_kwh', 0)} kWh",
                    'Entladetiefe': "95%",
                    'Zyklen': "6.000+ Ladezyklen",
                    'Garantie': "10 Jahre"
                },
                'quantity': 1,
                'price': calculation_results.get('battery_cost', 0)
            })
        
        config['products'] = products
    
    return config

def get_modern_pdf_integration_status() -> Dict[str, bool]:
    """
    Gibt den Status der modernen PDF-Integration zurück
    """
    return {
        'modern_design_available': MODERN_DESIGN_AVAILABLE,
        'ui_enhancement_available': UI_ENHANCEMENT_AVAILABLE,
        'integration_ready': MODERN_DESIGN_AVAILABLE and UI_ENHANCEMENT_AVAILABLE
    }

def create_modern_pdf_fallback_message() -> str:
    """
    Erstellt Fallback-Nachricht wenn moderne Features nicht verfügbar sind
    """
    status = get_modern_pdf_integration_status()
    
    if status['integration_ready']:
        return ""
    
    messages = []
    if not status['modern_design_available']:
        messages.append("• Moderne Design-Module nicht gefunden")
    if not status['ui_enhancement_available']:
        messages.append("• UI-Enhancement-Module nicht gefunden")
    
    return f"Moderne PDF-Features nicht verfügbar:\n" + "\n".join(messages)

# Beispiel-Integration für bestehende Systeme
def integrate_with_existing_doc_output(original_story_function):
    """
    Decorator für Integration mit bestehender doc_output Funktion
    """
    def wrapper(*args, **kwargs):
        # Originale Story erstellen
        original_story = original_story_function(*args, **kwargs)
        
        # Moderne Enhancements anwenden falls verfügbar und aktiviert
        try:
            # Hole relevante Daten aus den Argumenten
            calculation_results = kwargs.get('calculation_results', {})
            project_data = kwargs.get('project_data', {})
            texts = kwargs.get('texts', {})
            
            enhanced_story = apply_modern_pdf_enhancements(
                original_story, calculation_results, project_data, texts
            )
            
            return enhanced_story
            
        except Exception as e:
            print(f"Moderne PDF-Enhancements konnten nicht angewendet werden: {e}")
            return original_story
    
    return wrapper
