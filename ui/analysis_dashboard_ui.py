# ui/analysis_dashboard_ui.py
# -*- coding: utf-8 -*-
"""
Analysis Dashboard - Visualisiert detaillierte Berechnungen.

Author: Suratina Sicmislar
Version: 1.0 (AI-Generated & Interactive)
"""
import streamlit as st
from calculations import calculate_offer_details # Die Standard-Berechnungen
from calculations_extended import run_all_extended_analyses # Die neuen Berechnungen

def display_analysis_dashboard(offer_data: dict):
    st.header(f"Analyse für Angebot {offer_data.get('offer_id', '')}")

    # Führe die erweiterten Berechnungen durch
    try:
        extended_results = run_all_extended_analyses(offer_data)
    except Exception as e:
        st.error(f"Fehler bei der Durchführung der erweiterten Analysen: {e}")
        return

    # Darstellung der wichtigsten Kennzahlen (KPIs)
    st.subheader("Finanzielle Top-Kennzahlen")
    cols = st.columns(3)
    with cols[0]:
        st.metric(
            label="Amortisation (dynamisch, 5% p.a.)",
            value=f"{extended_results.get('dynamic_payback_5_percent', 0):.1f} Jahre"
        )
    with cols[1]:
        st.metric(
            label="Interner Zinsfuß (IRR)",
            value=f"{extended_results.get('irr_25_years', 0):.2f} %"
        )
    with cols[2]:
        # Annahme: 'roi_10_years' ist eine der 50 Berechnungen
        st.metric(
            label="Kapitalrendite (nach 10 J.)",
            value=f"{extended_results.get('roi_10_years', 0):.1f} %"
        )

    # Visualisierungen und Detail-Analysen
    st.subheader("Detaillierte Auswertungen")
    
    with st.expander("Kapitalfluss-Analyse (Cash-Flow)"):
        # Annahme: Eine Funktion generiert Cash-Flow-Daten für ein Diagramm
        # cash_flow_data = calculate_cash_flow_over_time(...)
        # st.line_chart(cash_flow_data)
        st.write("Hier würde ein detailliertes Cash-Flow-Diagramm über 25 Jahre angezeigt.")

    with st.expander("Ökologische Bilanz"):
        st.write("Details zur CO2-Einsparung, energetischen Amortisation etc.")
        # co2_payback = extended_results.get('co2_payback_time')
        # st.info(f"Die Anlage hat sich ökologisch nach {co2_payback:.2f} Jahren amortisiert.")

    # Hier können alle 50 Ergebnisse ansprechend visualisiert werden.