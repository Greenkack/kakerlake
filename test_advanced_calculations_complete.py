#!/usr/bin/env python3
"""
Testskript für die erweiterten Berechnungen (AdvancedCalculationsIntegrator)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculations import AdvancedCalculationsIntegrator

def test_advanced_calculations():
    """Testet alle erweiterten Berechnungen"""
    print("=== TEST: Erweiterte Berechnungen (AdvancedCalculationsIntegrator) ===\n")
    
    # Initialisiere den Integrator
    integrator = AdvancedCalculationsIntegrator()
    
    # Test-Daten (Basis-Berechnungsdaten)
    base_data = {
        'anlage_kwp': 12.5,
        'annual_pv_production_kwh': 11500,
        'total_consumption_kwh_yr': 4200,
        'include_storage': True,
        'battery_capacity_kwh': 10.0,
        'monthly_production': [500, 700, 900, 1200, 1400, 1500, 1450, 1300, 1000, 700, 500, 400],
        'monthly_consumption': [400, 380, 350, 320, 300, 280, 290, 310, 330, 360, 380, 400]
    }
    
    print("Test-Daten:")
    print(f"- Anlagengröße: {base_data['anlage_kwp']} kWp")
    print(f"- Jahresproduktion: {base_data['annual_pv_production_kwh']:,} kWh")
    print(f"- Jahresverbrauch: {base_data['total_consumption_kwh_yr']:,} kWh")
    print(f"- Speicher: {base_data['battery_capacity_kwh']} kWh")
    print()
    
    # Teste alle verfügbaren Berechnungen
    print("Verfügbare Berechnungen:")
    available_calcs = integrator.get_available_calculations()
    for calc_id, meta in available_calcs.items():
        print(f"- {calc_id}: {meta['name']} ({meta['category']})")
    print()
    
    # Führe alle Berechnungen durch
    print("Führe alle erweiterten Berechnungen durch...")
    results = integrator.execute_all_calculations(base_data)
    
    print(f"\nErgebnisse für {len(results)} Berechnungen:")
    print("=" * 60)
    
    for calc_id, result in results.items():
        meta = result.get('meta', {})
        print(f"\n{meta.get('name', calc_id)} ({calc_id})")
        print(f"Kategorie: {meta.get('category', 'Unbekannt')}")
        print(f"Beschreibung: {meta.get('description', 'Keine Beschreibung')}")
        
        if 'error' in result:
            print(f"❌ FEHLER: {result['error']}")
        elif 'data' in result:
            data = result['data']
            print("✅ Erfolgreich berechnet")
            
            # Zeige einige Key-Resultate an
            if calc_id == 'degradation_analysis':
                print(f"   - Finale Leistung: {data.get('final_performance_percent', 0):.1f}%")
                print(f"   - Energieverlust über 25 Jahre: {data.get('total_energy_loss_kwh', 0):,.0f} kWh")
                
            elif calc_id == 'carbon_footprint':
                print(f"   - Jährliche CO₂-Einsparung: {data.get('annual_co2_savings_t', 0):.1f} Tonnen")
                print(f"   - CO₂-Amortisation: {data.get('co2_payback_years', 0):.1f} Jahre")
                
            elif calc_id == 'grid_interaction':
                print(f"   - Eigenverbrauchsrate: {data.get('self_consumption_rate', 0):.1f}%")
                print(f"   - Netzunabhängigkeit: {data.get('grid_independence_rate', 0):.1f}%")
                
            elif calc_id == 'battery_cycles':
                print(f"   - Erwartete Lebensdauer: {data.get('expected_lifetime_years', 0):.0f} Jahre")
                print(f"   - Jährliche Zyklen: {data.get('annual_cycles', 0):.0f}")
                
            elif calc_id == 'peak_shaving':
                print(f"   - Lastspitzenreduzierung: {data.get('reduction_percent', 0):.1f}%")
                print(f"   - Jährliche Einsparung: {data.get('annual_savings_eur', 0):.0f} €")
                
            elif calc_id == 'energy_independence':
                print(f"   - Unabhängigkeit mit Speicher: {data.get('independence_with_storage_percent', 0):.1f}%")
                print(f"   - Durchschnitt über 25 Jahre: {data.get('average_independence_25_years', 0):.1f}%")
                
            elif calc_id == 'dynamic_pricing':
                print(f"   - Optimierungspotenzial: {data.get('optimization_potential_percent', 0):.1f}%")
                print(f"   - Jährliche Einsparung: {data.get('annual_savings_eur', 0):.0f} €")
                
            elif calc_id == 'maintenance_schedule':
                print(f"   - Durchschnittliche Jahreskosten: {data.get('average_annual_cost', 0):.0f} €")
                print(f"   - Kosten pro kWp/Jahr: {data.get('cost_per_kwp_per_year', 0):.0f} €")
                
            elif calc_id == 'weather_impact':
                print(f"   - Wetterbedingte Effizienz: {data.get('efficiency_percent', 0):.1f}%")
                print(f"   - Produktionsverlust: {data.get('production_loss_kwh', 0):,.0f} kWh")
                
            elif calc_id == 'shading_analysis':
                print(f"   - Durchschnittliche Verschattung: {data.get('average_shading_percent', 0):.1f}%")
                print(f"   - Energieverlust: {data.get('annual_shading_loss_kwh', 0):,.0f} kWh")
        
        print("-" * 60)
    
    # Teste ausgewählte Berechnungen
    print("\n\nTeste ausgewählte Berechnungen:")
    selected_calcs = ['degradation_analysis', 'carbon_footprint', 'battery_cycles']
    selected_results = integrator.execute_selected_calculations(selected_calcs, base_data)
    
    print(f"Ausgewählte Berechnungen: {', '.join(selected_calcs)}")
    print(f"Ergebnisse erhalten: {len(selected_results)}")
    
    for calc_id in selected_calcs:
        if calc_id in selected_results:
            result = selected_results[calc_id]
            if 'error' in result:
                print(f"❌ {calc_id}: {result['error']}")
            else:
                print(f"✅ {calc_id}: Erfolgreich")
        else:
            print(f"❌ {calc_id}: Nicht gefunden")
    
    print("\n=== TEST ABGESCHLOSSEN ===")
    return results

if __name__ == "__main__":
    test_advanced_calculations()
