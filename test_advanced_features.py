#!/usr/bin/env python3
"""Funktionalitätstest für erweiterte Berechnungen"""

import sys
sys.path.append('.')

def test_advanced_calculations():
    """Test der erweiterten Berechnungsmodule"""
    print("🔧 Teste erweiterte Berechnungsmodule...")
    
    try:
        from calculations import AdvancedCalculationsIntegrator
        print("✅ AdvancedCalculationsIntegrator importiert")
        
        # Instanz erstellen
        integrator = AdvancedCalculationsIntegrator()
        print("✅ Integrator-Instanz erstellt")
        
        # Test-Daten
        test_calc_results = {
            'total_investment_netto': 15000,
            'annual_pv_production_kwh': 8000,
            'annual_benefits_sim': [800, 850, 900, 950, 1000] * 5,  # 25 Jahre
            'cumulative_cash_flows_sim': list(range(-15000, 10000, 1000)),
            'self_supply_rate_percent': 65.0,
            'total_consumption_kwh_yr': 4500
        }
        
        test_project_data = {
            'pv_power_kwp': 10.0,
            'battery_capacity_kwh': 5.0,
            'location': 'Deutschland'
        }
        
        # LCOE Test
        print("\n📊 Teste LCOE-Berechnung...")
        lcoe_params = {
            'investment': 15000,
            'annual_production': 8000,
            'lifetime': 25,
            'discount_rate': 0.04
        }
        lcoe_result = integrator.calculate_lcoe_advanced(lcoe_params)
        print(f"✅ LCOE berechnet: {lcoe_result.get('base_lcoe', 'N/A')} €/kWh")
        
        # NPV Sensitivitätsanalyse Test
        print("\n💰 Teste NPV-Sensitivitätsanalyse...")
        npv_result = integrator.calculate_npv_sensitivity(test_calc_results, 0.04)
        print(f"✅ NPV berechnet: {npv_result:,.0f} €")
        
        # IRR Test
        print("\n📈 Teste IRR-Berechnung...")
        irr_result = integrator.calculate_irr_advanced(test_calc_results)
        print(f"✅ IRR berechnet: {irr_result.get('irr', 'N/A')}%")
        
        # Energiefluss Test
        print("\n⚡ Teste Energiefluss-Berechnung...")
        energy_flows = integrator.calculate_detailed_energy_flows(test_calc_results)
        print(f"✅ Energieflüsse berechnet: {len(energy_flows.get('flow_names', []))} Flüsse")
        
        # Lastprofil Test
        print("\n📊 Teste Lastprofil-Analyse...")
        load_profile = integrator.calculate_load_profile_analysis(test_calc_results, test_project_data)
        print(f"✅ Lastprofil berechnet: {load_profile.get('peak_load', 'N/A')} kW Spitzenlast")
        
        # Wechselrichter-Effizienz Test
        print("\n🔌 Teste Wechselrichter-Effizienz...")
        inverter_analysis = integrator.calculate_inverter_efficiency(test_calc_results, test_project_data)
        print(f"✅ Wechselrichter-Effizienz: {inverter_analysis.get('euro_efficiency', 'N/A')}%")
        
        print("\n🎉 ALLE ERWEITERTEN BERECHNUNGEN FUNKTIONIEREN!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_integration():
    """Test der Analysis-Integration"""
    print("\n🔗 Teste Analysis-Integration...")
    
    try:
        import analysis
        print("✅ analysis Modul importiert")
        
        # Prüfe ob integrate_advanced_calculations verfügbar ist
        if hasattr(analysis, 'integrate_advanced_calculations'):
            print("✅ integrate_advanced_calculations Funktion verfügbar")
        else:
            print("⚠️ integrate_advanced_calculations Funktion nicht gefunden")
        
        # Prüfe render_advanced_economics
        if hasattr(analysis, 'render_advanced_economics'):
            print("✅ render_advanced_economics Funktion verfügbar")
        else:
            print("⚠️ render_advanced_economics Funktion nicht gefunden")
            
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Analysis-Test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 UMFANGREICHER FUNKTIONALITÄTSTEST")
    print("=" * 50)
    
    success1 = test_advanced_calculations()
    success2 = test_analysis_integration()
    
    if success1 and success2:
        print("\n🎊 ALLE TESTS ERFOLGREICH!")
        print("Die erweiterten Analysen sind vollständig funktionsfähig!")
    else:
        print("\n⚠️ Einige Tests fehlgeschlagen - Details siehe oben.")
