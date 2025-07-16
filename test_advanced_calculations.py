#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testskript für die erweiterten Berechnungen der AdvancedCalculationsIntegrator-Klasse.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculations import AdvancedCalculationsIntegrator
import json

def test_advanced_calculations():
    """Testet alle erweiterten Berechnungen der AdvancedCalculationsIntegrator-Klasse"""
    
    print("🔧 Teste AdvancedCalculationsIntegrator...")
    
    # Initialisiere die Klasse
    integrator = AdvancedCalculationsIntegrator()
    
    # Basis-Testdaten
    base_data = {
        'anlage_kwp': 10.0,
        'annual_pv_production_kwh': 9500,
        'total_consumption_kwh_yr': 4500,
        'include_storage': True,
        'battery_capacity_kwh': 10.0,
        'monthly_production': [400, 600, 800, 900, 1100, 1200, 1150, 1000, 850, 650, 450, 350],
        'monthly_consumption': [450, 400, 380, 350, 320, 300, 310, 320, 350, 380, 420, 460]
    }
    
    print(f"📊 Basis-Testdaten: {base_data['anlage_kwp']} kWp, {base_data['annual_pv_production_kwh']} kWh/Jahr")
    
    # Teste verfügbare Berechnungen
    available_calculations = integrator.get_available_calculations()
    print(f"\n✅ Verfügbare Berechnungen: {len(available_calculations)}")
    for calc_id, meta in available_calculations.items():
        print(f"  - {calc_id}: {meta['name']} ({meta['category']})")
    
    # Teste einzelne Berechnungen
    print("\n🧮 Teste einzelne Berechnungen:")
    
    test_calculations = ['degradation_analysis', 'battery_cycles', 'carbon_footprint', 'peak_shaving']
    
    for calc_id in test_calculations:
        try:
            print(f"\n  📈 {calc_id}:")
            results = integrator.execute_selected_calculations([calc_id], base_data)
            
            if calc_id in results and 'data' in results[calc_id]:
                data = results[calc_id]['data']
                
                if calc_id == 'degradation_analysis':
                    print(f"    - Finale Leistung: {data.get('final_performance_percent', 0):.1f}%")
                    print(f"    - Gesamtenergie-Verlust: {data.get('total_energy_loss_kwh', 0):.0f} kWh")
                
                elif calc_id == 'battery_cycles':
                    print(f"    - Erwartete Lebensdauer: {data.get('expected_lifetime_years', 0):.1f} Jahre")
                    print(f"    - Jährliche Zyklen: {data.get('annual_cycles', 0):.0f}")
                
                elif calc_id == 'carbon_footprint':
                    print(f"    - Jährliche CO2-Einsparung: {data.get('annual_co2_savings_t', 0):.1f} t")
                    print(f"    - CO2-Amortisation: {data.get('co2_payback_years', 0):.1f} Jahre")
                    print(f"    - Baum-Äquivalent: {data.get('tree_equivalent', 0)} Bäume")
                
                elif calc_id == 'peak_shaving':
                    print(f"    - Lastspitzen-Reduktion: {data.get('total_reduction_kw', 0):.1f} kW")
                    print(f"    - Jährliche Einsparung: {data.get('annual_savings_eur', 0):.0f} €")
                    
            else:
                print(f"    ❌ Fehler: {results[calc_id].get('error', 'Unbekannter Fehler')}")
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
    
    # Teste alle Berechnungen auf einmal
    print("\n🔄 Teste alle Berechnungen gleichzeitig:")
    try:
        all_results = integrator.execute_all_calculations(base_data)
        
        successful_calcs = [calc_id for calc_id, result in all_results.items() if 'data' in result]
        failed_calcs = [calc_id for calc_id, result in all_results.items() if 'error' in result]
        
        print(f"  ✅ Erfolgreich: {len(successful_calcs)}/{len(all_results)}")
        print(f"  ❌ Fehlgeschlagen: {len(failed_calcs)}")
        
        if failed_calcs:
            print("  Fehlgeschlagene Berechnungen:")
            for calc_id in failed_calcs:
                print(f"    - {calc_id}: {all_results[calc_id]['error']}")
        
        # Zeige Zusammenfassung wichtiger Ergebnisse
        print("\n📋 Zusammenfassung wichtiger Ergebnisse:")
        
        for calc_id, result in all_results.items():
            if 'data' in result:
                data = result['data']
                meta = result['meta']
                print(f"  📊 {meta.get('name', calc_id)}:")
                
                # Zeige 2-3 wichtige Kennzahlen pro Berechnung
                if calc_id == 'degradation_analysis':
                    print(f"    → Leistung nach 25 Jahren: {data.get('final_performance_percent', 0):.1f}%")
                elif calc_id == 'grid_interaction':
                    print(f"    → Eigenverbrauchsrate: {data.get('self_consumption_rate', 0):.1f}%")
                elif calc_id == 'weather_impact':
                    print(f"    → Wetter-Effizienz: {data.get('efficiency_percent', 0):.1f}%")
                elif calc_id == 'maintenance_schedule':
                    print(f"    → Jährliche Wartungskosten: {data.get('average_annual_cost', 0):.0f} €")
                elif calc_id == 'energy_independence':
                    print(f"    → Energieunabhängigkeit: {data.get('independence_with_storage_percent', 0):.1f}%")
                elif calc_id == 'recycling_potential':
                    print(f"    → Recycling-Wert: {data.get('total_recycling_value_eur', 0):.0f} €")
                elif calc_id == 'dynamic_pricing':
                    print(f"    → Optimierungspotential: {data.get('optimization_potential_percent', 0):.1f}%")
        
    except Exception as e:
        print(f"  ❌ Fehler bei allen Berechnungen: {e}")
    
    print("\n✅ Test der erweiterten Berechnungen abgeschlossen!")

if __name__ == "__main__":
    test_advanced_calculations()
