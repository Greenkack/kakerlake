# ui/heatpump_ui.py
# -*- coding: utf-8 -*-
"""
UI für die Wärmepumpen-Analyse und Auslegung.

Author: Suratina Sicmislar
Version: 1.0 (Fully Implemented)
"""
import streamlit as st
import sqlite3
import pandas as pd
from database import get_all_heat_pumps
from calculations_heatpump import (calculate_building_heat_load, recommend_heat_pump, 
                                   calculate_annual_energy_consumption)

def display_heatpump_ui(conn: sqlite3.Connection):
    st.header("Wärmepumpen-Analyse")
    st.info("Ermitteln Sie hier die passende Wärmepumpe für Ihr Gebäude.")

    with st.form("heat_load_form"):
        st.subheader("1. Gebäudedaten eingeben")
        area = st.number_input("Beheizte Wohnfläche (m²)", min_value=30, value=150)
        building = st.selectbox("Gebäudetyp", ["Neubau KFW40", "Neubau KFW55", "Altbau saniert", "Altbau unsaniert"])
        insulation = st.selectbox("Dämmqualität", ["Gut", "Mittel", "Schlecht"])
        
        submitted = st.form_submit_button("Heizlast berechnen")

    if submitted:
        heat_load = calculate_building_heat_load(building, area, insulation)
        st.session_state['heat_load_kw'] = heat_load
    
    if 'heat_load_kw' in st.session_state:
        heat_load = st.session_state['heat_load_kw']
        st.subheader("2. Ergebnis der Heizlastberechnung")
        st.metric("Benötigte Heizleistung", f"{heat_load:.2f} kW")

        all_pumps = get_all_heat_pumps(conn)
        if not all_pumps:
            st.error("Keine Wärmepumpen in der Datenbank gefunden. Bitte im Admin-Panel hinzufügen.")
            return

        recommended_pump = recommend_heat_pump(heat_load, all_pumps)

        st.subheader("3. Empfohlene Wärmepumpe")
        if recommended_pump:
            st.success(f"Empfohlenes Modell: **{recommended_pump['manufacturer']} {recommended_pump['model_name']}**")
            
            annual_consumption = calculate_annual_energy_consumption(
                recommended_pump['heating_output_kw'], 
                recommended_pump['scop']
            )

            df_data = {
                "Kennzahl": ["Modell", "Hersteller", "Heizleistung", "Jahresarbeitszahl (SCOP)", "Geschätzter Jahresverbrauch", "Preis"],
                "Wert": [
                    recommended_pump['model_name'],
                    recommended_pump['manufacturer'],
                    f"{recommended_pump['heating_output_kw']:.2f} kW",
                    f"{recommended_pump['scop']:.2f}",
                    f"{annual_consumption:,.0f} kWh/Jahr".replace(",", "."),
                    f"{recommended_pump['price']:,.2f} €".replace(",", ".")
                ]
            }
            st.table(pd.DataFrame(df_data))
            
            # Hier könnten die Daten ins Session State für die PDF-Ausgabe gespeichert werden
            st.session_state['selected_heatpump_data'] = {**recommended_pump, 'annual_consumption': annual_consumption}

        else:
            st.warning("Keine passende Wärmepumpe in der Datenbank gefunden, die die benötigte Heizlast abdeckt.")