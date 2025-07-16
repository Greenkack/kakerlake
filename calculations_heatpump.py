# calculations_heatpump.py
# -*- coding: utf-8 -*-
"""
Berechnungen für die Auslegung und Analyse von Wärmepumpensystemen.

Author: Suratina Sicmislar
Version: 1.0 (Fully Implemented)
"""
from typing import Dict, List, Any

def calculate_building_heat_load(
    building_type: str, living_area_m2: float, insulation_quality: str
) -> float:
    """
    Vereinfachte Berechnung der Heizlast eines Gebäudes in kW.

    Args:
        building_type (str): z.B. "Neubau KFW40", "Altbau saniert".
        living_area_m2 (float): Wohnfläche in Quadratmetern.
        insulation_quality (str): z.B. "Gut", "Mittel", "Schlecht".

    Returns:
        float: Die geschätzte maximale Heizlast in kW.
    """
    base_load_w_per_m2 = {
        "Neubau KFW40": 40.0,
        "Neubau KFW55": 55.0,
        "Altbau saniert": 70.0,
        "Altbau unsaniert": 120.0,
    }
    
    insulation_factor = {
        "Gut": 0.9,
        "Mittel": 1.0,
        "Schlecht": 1.2,
    }
    
    base_w_m2 = base_load_w_per_m2.get(building_type, 100.0)
    factor = insulation_factor.get(insulation_quality, 1.0)
    
    heat_load_watts = living_area_m2 * base_w_m2 * factor
    return heat_load_watts / 1000  # Umrechnung in kW

def recommend_heat_pump(heat_load_kw: float, available_pumps: List[Dict]) -> Dict:
    """
    Empfiehlt die kleinste passende Wärmepumpe aus einer Liste.
    
    Args:
        heat_load_kw (float): Die benötigte Heizlast.
        available_pumps (List[Dict]): Liste der verfügbaren Pumpen aus der DB.

    Returns:
        Dict: Die Daten der empfohlenen Wärmepumpe oder None.
    """
    suitable_pumps = [p for p in available_pumps if p['heating_output_kw'] >= heat_load_kw]
    if not suitable_pumps:
        return None
    # Sortiere nach Leistung und wähle die kleinste, die passt
    return sorted(suitable_pumps, key=lambda p: p['heating_output_kw'])[0]

def calculate_annual_energy_consumption(heat_load_kw: float, scop: float, heating_hours: int = 1800) -> float:
    """
    Berechnet den jährlichen Stromverbrauch der Wärmepumpe.

    Args:
        heat_load_kw (float): Die Heizlast des Gebäudes.
        scop (float): Die Jahresarbeitszahl der Pumpe.
        heating_hours (int): Angenommene jährliche Volllaststunden.

    Returns:
        float: Der geschätzte jährliche Stromverbrauch in kWh.
    """
    if scop == 0:
        return 0.0
    annual_heat_demand_kwh = heat_load_kw * heating_hours
    annual_electricity_consumption_kwh = annual_heat_demand_kwh / scop
    return annual_electricity_consumption_kwh

def calculate_heatpump_economics(heatpump_data: Dict[str, Any], building_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Berechnet die Wirtschaftlichkeit einer Wärmepumpe.
    
    Args:
        heatpump_data (Dict[str, Any]): Wärmepumpendaten
        building_data (Dict[str, Any], optional): Gebäudedaten
    
    Returns:
        Dict[str, Any]: Wirtschaftlichkeitsberechnung
    """
    # Standardwerte setzen
    if building_data is None:
        building_data = {}
    
    # Extrahiere Daten
    heating_demand = heatpump_data.get('heating_demand', building_data.get('heating_demand', 15000))  # kWh/Jahr
    heatpump_power = heatpump_data.get('heatpump_power', heatpump_data.get('heating_power_kw', 10.0))  # kW
    cop = heatpump_data.get('cop', heatpump_data.get('cop_rating', 3.5))
    electricity_price = heatpump_data.get('electricity_price', 0.30)  # €/kWh
    investment_cost = heatpump_data.get('investment_cost', heatpump_data.get('price', 15000))  # €
    
    # Alternative Heizkosten (z.B. Gas/Öl)
    alternative_fuel_price = heatpump_data.get('alternative_fuel_price', 0.08)  # €/kWh
    alternative_efficiency = heatpump_data.get('alternative_efficiency', 0.9)
    
    # Berechnungen
    electricity_consumption = heating_demand / cop  # kWh/Jahr
    annual_electricity_cost = electricity_consumption * electricity_price  # €/Jahr
    
    # Alternative Heizkosten
    alternative_fuel_consumption = heating_demand / alternative_efficiency
    annual_alternative_cost = alternative_fuel_consumption * alternative_fuel_price
    
    # Einsparungen
    annual_savings = annual_alternative_cost - annual_electricity_cost
    
    # Amortisation
    if annual_savings > 0:
        payback_period_years = investment_cost / annual_savings
    else:
        payback_period_years = float('inf')
    
    # 20-Jahres-Bilanz
    total_savings_20y = annual_savings * 20 - investment_cost
    
    return {
        'heating_demand_kwh': heating_demand,
        'electricity_consumption_kwh': electricity_consumption,
        'annual_electricity_cost': round(annual_electricity_cost, 2),
        'annual_alternative_cost': round(annual_alternative_cost, 2),
        'annual_savings': round(annual_savings, 2),
        'payback_period_years': round(payback_period_years, 1) if payback_period_years != float('inf') else None,
        'total_savings_20y': round(total_savings_20y, 2),
        'investment_cost': investment_cost,
        'cop': cop,
        'recommendation': 'Wirtschaftlich' if payback_period_years <= 15 else 'Bedingt wirtschaftlich' if payback_period_years <= 25 else 'Nicht wirtschaftlich'
    }

def calculate_heatpump_sizing(building_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Berechnet die optimale Wärmepumpengröße für ein Gebäude.
    
    Args:
        building_data (Dict[str, Any]): Gebäudedaten
    
    Returns:
        Dict[str, Any]: Auslegungsempfehlung
    """
    # Gebäudedaten extrahieren
    building_type = building_data.get('building_type', 'Altbau saniert')
    living_area_m2 = building_data.get('living_area_m2', 150)
    insulation_quality = building_data.get('insulation_quality', 'Mittel')
    
    # Heizlast berechnen
    heat_load_kw = calculate_building_heat_load(building_type, living_area_m2, insulation_quality)
    
    # Warmwasser-Anteil hinzufügen (ca. 15-25% der Heizlast)
    hot_water_factor = building_data.get('hot_water_factor', 0.2)
    total_load_kw = heat_load_kw * (1 + hot_water_factor)
    
    # Empfohlene Wärmepumpenleistung (etwas überdimensioniert für Komfort)
    recommended_power_kw = total_load_kw * 1.1
    
    # Jährlicher Wärmebedarf schätzen
    heating_hours = building_data.get('heating_hours', 1800)
    annual_heat_demand = heat_load_kw * heating_hours
    
    return {
        'heat_load_kw': round(heat_load_kw, 2),
        'total_load_kw': round(total_load_kw, 2),
        'recommended_power_kw': round(recommended_power_kw, 2),
        'annual_heat_demand_kwh': round(annual_heat_demand, 0),
        'building_type': building_type,
        'living_area_m2': living_area_m2,
        'insulation_quality': insulation_quality
    }

# Test-Funktion
if __name__ == "__main__":
    # Test der Berechnungen
    test_building = {
        'building_type': 'Neubau KFW55',
        'living_area_m2': 180,
        'insulation_quality': 'Gut'
    }
    
    test_heatpump = {
        'heating_power_kw': 12.0,
        'cop_rating': 4.2,
        'price': 18000,
        'electricity_price': 0.32,
        'heating_demand': 12000
    }
    
    sizing = calculate_heatpump_sizing(test_building)
    economics = calculate_heatpump_economics(test_heatpump, test_building)
    
    print("Wärmepumpen-Auslegung:")
    print(f"  Heizlast: {sizing['heat_load_kw']} kW")
    print(f"  Empfohlene Leistung: {sizing['recommended_power_kw']} kW")
    
    print("\nWirtschaftlichkeit:")
    print(f"  Jährliche Stromkosten: {economics['annual_electricity_cost']} €")
    print(f"  Jährliche Einsparungen: {economics['annual_savings']} €")
    print(f"  Amortisation: {economics['payback_period_years']} Jahre")
    print(f"  Bewertung: {economics['recommendation']}")