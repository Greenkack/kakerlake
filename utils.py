# utils.py
# Enthält diverse Hilfsfunktionen

import streamlit as st # Import für st.warning, falls benötigt (eher für UI-Module)
import math

# Bestehende Platzhalter-Funktionen bleiben erhalten
def is_valid_email(email: str) -> bool:
    """Placeholder Funktion zur Validierung einer E-Mail-Adresse."""
    # Hier kommt die echte Regex-Validierung
    return True

def format_euro(amount: float) -> str:
    """Placeholder Funktion zur Formatierung eines Betrags als Euro."""
    return f"{amount:.2f} € (Placeholder)"

# NEUE Funktionen für CO2-Äquivalente
# Diese Funktionen nehmen die eingesparten kWh (durch PV-Produktion),
# die relevanten Umrechnungsfaktoren und den CO2-Faktor des Netzstroms als Input.

def kwh_to_trees_equivalent(
    kwh_savings: float,
    tree_absorption_kg_co2_per_year: float,
    grid_co2_g_per_kwh: float
) -> float:
    """
    Berechnet die Anzahl der Bäume, die äquivalent zur CO2-Einsparung durch
    die eingesparten kWh sind.
    """
    if tree_absorption_kg_co2_per_year <= 0 or grid_co2_g_per_kwh <= 0:
        return 0.0
    
    # CO2-Einsparung in kg durch PV
    co2_saved_kg = (kwh_savings * grid_co2_g_per_kwh) / 1000.0
    
    # Anzahl äquivalenter Bäume
    equivalent_trees = co2_saved_kg / tree_absorption_kg_co2_per_year
    return equivalent_trees

def kwh_to_car_km_equivalent(
    kwh_savings: float,
    car_co2_g_per_km: float,
    grid_co2_g_per_kwh: float
) -> float:
    """
    Berechnet die äquivalenten Autofahrkilometer (PKW) zur CO2-Einsparung.
    """
    if car_co2_g_per_km <= 0 or grid_co2_g_per_kwh <= 0:
        return 0.0
        
    # CO2-Einsparung in Gramm durch PV
    co2_saved_g = kwh_savings * grid_co2_g_per_kwh
    
    # Äquivalente Autokilometer
    equivalent_km = co2_saved_g / car_co2_g_per_km
    return equivalent_km

def kwh_to_flights_equivalent(
    kwh_savings: float,
    flight_co2_kg_per_person: float, # z.B. für eine bestimmte Strecke wie MUC-PMI und zurück
    grid_co2_g_per_kwh: float
) -> float:
    """
    Berechnet die Anzahl äquivalenter Flüge (für eine definierte Strecke)
    zur CO2-Einsparung.
    """
    if flight_co2_kg_per_person <= 0 or grid_co2_g_per_kwh <= 0:
        return 0.0
        
    # CO2-Einsparung in kg durch PV
    co2_saved_kg = (kwh_savings * grid_co2_g_per_kwh) / 1000.0
    
    # Anzahl äquivalenter Flüge
    equivalent_flights = co2_saved_kg / flight_co2_kg_per_person
    return equivalent_flights

# Platzhalterfunktion `kwh_to_trees` wird durch die spezifischere `kwh_to_trees_equivalent` ersetzt.
# Falls die alte `kwh_to_trees` irgendwo direkt aufgerufen wurde (was unwahrscheinlich ist, da es nur ein Print-Placeholder war),
# müsste dieser Aufruf angepasst werden. Da wir jetzt von `calculations.py` aus aufrufen,
# verwenden wir die neuen, präziseren Funktionsnamen.

if __name__ == '__main__':
    # Testaufrufe für die neuen Funktionen
    test_kwh_savings = 5000 # Beispiel: 5000 kWh eingespart pro Jahr
    
    # Beispielhafte Admin-Parameter (diese würden in calculations.py geladen)
    test_tree_absorption = 22.0 # kg CO2 / Baum / Jahr
    test_car_emission = 120.0   # g CO2 / km
    test_flight_emission = 180.0 # kg CO2 / Flug MUC-PMI-MUC
    test_grid_co2_factor = 388.0 # g CO2 / kWh Netzstrom

    trees = kwh_to_trees_equivalent(test_kwh_savings, test_tree_absorption, test_grid_co2_factor)
    car_km = kwh_to_car_km_equivalent(test_kwh_savings, test_car_emission, test_grid_co2_factor)
    flights = kwh_to_flights_equivalent(test_kwh_savings, test_flight_emission, test_grid_co2_factor)

    print(f"{test_kwh_savings} kWh Einsparung entspricht ca.:")
    print(f"- {trees:.2f} Bäumen (die diese CO2-Menge pro Jahr binden)")
    print(f"- {car_km:.0f} Autokilometern (vermieden)")
    print(f"- {flights:.2f} Flügen München-Mallorca (Hin- und Rückflug, vermieden)")