# ui/admin_heatpumps_ui.py
# -*- coding: utf-8 -*-
"""
Admin-UI zur Verwaltung der Wärmepumpen-Produktdatenbank.

Author: Suratina Sicmislar
Version: 1.0 (Fully Implemented)
"""
import streamlit as st
import sqlite3
from database import (get_all_heat_pumps, add_heat_pump, update_heat_pump, delete_heat_pump)

def display_admin_heatpumps_ui(conn: sqlite3.Connection):
    st.subheader("Wärmepumpen-Produktdatenbank verwalten")

    pumps = get_all_heat_pumps(conn)
    
    if pumps:
        for pump in pumps:
            with st.expander(f"{pump['manufacturer']} - {pump['model_name']} ({pump['heating_output_kw']} kW)"):
                new_model = st.text_input("Modellname", pump['model_name'], key=f"model_{pump['id']}")
                new_manu = st.text_input("Hersteller", pump['manufacturer'], key=f"manu_{pump['id']}")
                new_heat_kw = st.number_input("Heizleistung (kW)", value=pump['heating_output_kw'], key=f"heat_{pump['id']}")
                new_power_kw = st.number_input("Leistungsaufnahme (kW)", value=pump['power_consumption_kw'], key=f"power_{pump['id']}")
                new_scop = st.number_input("JAZ/SCOP", value=pump['scop'], key=f"scop_{pump['id']}")
                new_price = st.number_input("Preis (€)", value=pump['price'], key=f"price_{pump['id']}")

                col1, col2 = st.columns([1, 0.2])
                with col1:
                    if st.button("Aktualisieren", key=f"update_{pump['id']}"):
                        data = (new_model, new_manu, new_heat_kw, new_power_kw, new_scop, new_price, pump['id'])
                        update_heat_pump(conn, data)
                        st.success("Aktualisiert!")
                        st.experimental_rerun()
                with col2:
                    if st.button("Löschen", key=f"delete_{pump['id']}"):
                        delete_heat_pump(conn, pump['id'])
                        st.success("Gelöscht!")
                        st.experimental_rerun()

    st.markdown("---")
    st.subheader("Neue Wärmepumpe hinzufügen")
    with st.form("new_pump_form"):
        model = st.text_input("Modellname")
        manu = st.text_input("Hersteller")
        heat_kw = st.number_input("Heizleistung (kW)", min_value=0.1)
        power_kw = st.number_input("Leistungsaufnahme (kW)", min_value=0.1)
        scop = st.number_input("JAZ/SCOP", min_value=1.0, step=0.1)
        price = st.number_input("Preis (€)", min_value=0.0)
        
        submitted = st.form_submit_button("Hinzufügen")
        if submitted:
            data = (model, manu, heat_kw, power_kw, scop, price)
            add_heat_pump(conn, data)
            st.success(f"Wärmepumpe '{model}' hinzugefügt.")