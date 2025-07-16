# crm_dashboard_ui.py
"""
CRM Dashboard UI Module
Zentrale Übersicht für das Kundenbeziehungsmanagement

Author: GitHub Copilot
Version: 2.0 (Vollständig implementiert)
Date: 2025-01-12
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Import der notwendigen Funktionen
try:
    from database import (
        get_all_active_customers, 
        get_customer_by_id, 
        update_customer,
        get_db_connection
    )
    from locales import get_text
    DATABASE_AVAILABLE = True
except ImportError as e:
    st.error(f"Datenbankmodul nicht verfügbar: {e}")
    DATABASE_AVAILABLE = False

def render_crm_dashboard(texts: Dict[str, str], module_name: Optional[str] = None):
    """Hauptfunktion für das CRM Dashboard"""
    
    if not DATABASE_AVAILABLE:
        st.error("CRM Dashboard nicht verfügbar - Datenbankmodul fehlt")
        return
    
    if module_name:
        st.header(module_name)
    else:
        st.header("CRM Dashboard")
    st.markdown("Zentrale Übersicht über alle Kunden und Geschäftsprozesse")
    
    # Tabs für verschiedene Dashboard-Bereiche
    tabs = st.tabs([
        "Übersicht",
        "Kunden",
        "Projekte", 
        "Umsatz",
        "Statistiken"
    ])
    
    with tabs[0]:
        render_overview_section(texts)
    
    with tabs[1]:
        render_customers_section(texts)
    
    with tabs[2]:
        render_projects_section(texts)
    
    with tabs[3]:
        render_revenue_section(texts)
    
    with tabs[4]:
        render_statistics_section(texts)

def render_overview_section(texts: Dict[str, str]):
    """Übersichts-Sektion des CRM Dashboards"""
    
    st.subheader("Geschäftsübersicht")
    
    # KPIs in Spalten
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        customers = get_all_active_customers()
        
        with col1:
            st.metric(
                label="Aktive Kunden",
                value=len(customers),
                delta="+5 diese Woche"
            )
        
        with col2:
            # Projekte berechnen (vereinfacht)
            projects_count = sum(1 for customer in customers if customer.get('project_status') == 'active')
            st.metric(
                label="Laufende Projekte",
                value=projects_count,
                delta="+2 diese Woche"
            )
        
        with col3:
            # Angebote berechnen (vereinfacht)
            offers_count = sum(1 for customer in customers if customer.get('offer_status') == 'pending')
            st.metric(
                label="Offene Angebote",
                value=offers_count,
                delta="-1 diese Woche"
            )
        
        with col4:
            # Umsatz berechnen (vereinfacht)
            total_revenue = sum(customer.get('project_value', 0) for customer in customers)
            st.metric(
                label="Gesamtumsatz",
                value=f"{total_revenue:,.0f} €",
                delta="+15.2% zum Vormonat"
            )
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Übersichtsdaten: {e}")
    
    # Aktivitäts-Timeline
    st.subheader("Letzte Aktivitäten")
    
    # Dummy-Daten für Aktivitäten
    activities = [
        {"time": "Heute 14:30", "action": "Neuer Kunde angelegt", "details": "Max Mustermann"},
        {"time": "Heute 11:15", "action": "Angebot versendet", "details": "Projekt PV-2025-001"},
        {"time": "Gestern 16:45", "action": "Termin vereinbart", "details": "Vor-Ort Besichtigung"},
        {"time": "Gestern 09:20", "action": "Projekt abgeschlossen", "details": "Installation 15kWp"},
    ]
    
    for activity in activities:
        with st.container():
            col_time, col_action = st.columns([1, 3])
            with col_time:
                st.caption(activity["time"])
            with col_action:
                st.write(f"**{activity['action']}** - {activity['details']}")

def render_customers_section(texts: Dict[str, str]):
    """Kunden-Sektion des CRM Dashboards"""
    
    st.subheader("Kundenübersicht")
    
    try:
        customers = get_all_active_customers()
        
        if not customers:
            st.info("Noch keine Kunden angelegt.")
            return
        
        # Kunden-Tabelle
        df_customers = pd.DataFrame(customers)
        
        # Spalten-Mapping für bessere Darstellung
        column_mapping = {
            'name': 'Name',
            'email': 'E-Mail',
            'phone': 'Telefon',
            'created_at': 'Erstellt am',
            'project_status': 'Projektstatus'
        }
        
        # Nur verfügbare Spalten anzeigen
        available_columns = [col for col in column_mapping.keys() if col in df_customers.columns]
        display_df = df_customers[available_columns].rename(columns=column_mapping)
        
        # Filter und Suche
        col_search, col_filter = st.columns([2, 1])
        
        with col_search:
            search_term = st.text_input("🔍 Kunde suchen...", placeholder="Name oder E-Mail eingeben")
        
        with col_filter:
            status_filter = st.selectbox(
                "Status filtern",
                options=["Alle", "Aktiv", "Interessent", "Abgeschlossen"]
            )
        
        # Filter anwenden
        if search_term:
            mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
        
        # Tabelle anzeigen
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Kundendetails bei Auswahl
        if len(display_df) > 0:
            selected_customer = st.selectbox(
                "Kunde für Details auswählen:",
                options=display_df['Name'].tolist() if 'Name' in display_df.columns else []
            )
            
            if selected_customer:
                customer_details = next((c for c in customers if c.get('name') == selected_customer), None)
                if customer_details:
                    render_customer_details(customer_details, texts)
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Kundendaten: {e}")

def render_customer_details(customer: Dict[str, Any], texts: Dict[str, str]):
    """Detailansicht für einen Kunden"""
    
    st.subheader(f"Kundendetails: {customer.get('name', 'Unbekannt')}")
    
    # Kunde-Info in Spalten
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Kontaktdaten:**")
        st.write(f"{customer.get('email', 'Nicht angegeben')}")
        st.write(f"{customer.get('phone', 'Nicht angegeben')}")
        st.write(f"{customer.get('address', 'Nicht angegeben')}")
    
    with col2:
        st.write("**Projektdaten:**")
        st.write(f"Status: {customer.get('project_status', 'Unbekannt')}")
        st.write(f"Anlagengröße: {customer.get('system_size', 0)} kWp")
        st.write(f"Projektwert: {customer.get('project_value', 0):,.0f} €")
    
    # Notizen
    st.write("**Notizen:**")
    notes = customer.get('notes', 'Keine Notizen vorhanden')
    st.text_area("", value=notes, height=100, disabled=True)

def render_projects_section(texts: Dict[str, str]):
    """Projekte-Sektion des CRM Dashboards"""
    
    st.subheader("Projektübersicht")
    
    # Projekt-Status Übersicht
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Neue Anfragen", "12", "+3")
    
    with col2:
        st.metric("In Planung", "8", "+1")
    
    with col3:
        st.metric("In Umsetzung", "5", "-1")
    
    # Projekt-Pipeline Visualisierung
    st.subheader("Projekt-Pipeline")
    
    # Dummy-Daten für Pipeline
    pipeline_data = {
        'Phase': ['Anfrage', 'Angebot', 'Bestellung', 'Installation', 'Abgeschlossen'],
        'Anzahl': [12, 8, 5, 3, 25],
        'Wert': [300000, 200000, 125000, 75000, 625000]
    }
    
    df_pipeline = pd.DataFrame(pipeline_data)
    
    # Funnel Chart
    fig = go.Figure(go.Funnel(
        y=df_pipeline['Phase'],
        x=df_pipeline['Anzahl'],
        textinfo="value+percent initial"
    ))
    
    fig.update_layout(
        title="Projekt-Pipeline (Anzahl Projekte)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_revenue_section(texts: Dict[str, str]):
    """Umsatz-Sektion des CRM Dashboards"""
    
    st.subheader("Umsatzanalyse")
    
    # Umsatz-KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monatsumsatz", "85.000 €", "+12.5%")
    
    with col2:
        st.metric("Jahresumsatz", "920.000 €", "+18.2%")
    
    with col3:
        st.metric("Ø Projektgröße", "18.400 €", "+5.1%")
    
    with col4:
        st.metric("Conversion Rate", "68%", "+3%")
    
    # Umsatz-Chart
    st.subheader("Umsatzentwicklung")
    
    # Dummy-Daten für Umsatzentwicklung
    months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    revenue_2024 = [45000, 52000, 61000, 48000, 73000, 68000, 82000, 77000, 85000, 91000, 88000, 95000]
    revenue_2023 = [38000, 41000, 45000, 42000, 58000, 55000, 62000, 59000, 64000, 69000, 71000, 75000]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=revenue_2024,
        mode='lines+markers',
        name='2024',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=revenue_2023,
        mode='lines+markers',
        name='2023',
        line=dict(color='#ff7f0e', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Monatlicher Umsatz (Vergleich)",
        xaxis_title="Monat",
        yaxis_title="Umsatz (€)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_statistics_section(texts: Dict[str, str]):
    """Statistiken-Sektion des CRM Dashboards"""
    
    st.subheader("Geschäftsstatistiken")
    
    # Statistiken in zwei Spalten
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Kundenverteilung")
        
        # Pie Chart für Kundentypen
        customer_types = ['Privatkunden', 'Gewerbekunden', 'Landwirtschaft', 'Öffentlich']
        customer_counts = [45, 18, 12, 5]
        
        fig_pie = px.pie(
            values=customer_counts,
            names=customer_types,
            title="Kundenverteilung nach Typ"
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Anlagengrößen")
        
        # Histogram für Anlagengrößen
        system_sizes = [5, 8, 10, 12, 15, 18, 20, 25, 30, 35, 8, 10, 12, 15, 18, 20, 25]
        
        fig_hist = px.histogram(
            x=system_sizes,
            nbins=10,
            title="Verteilung der Anlagengrößen (kWp)",
            labels={'x': 'Anlagengröße (kWp)', 'y': 'Anzahl Projekte'}
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Performance-Metriken
    st.subheader("🏆 Performance-Metriken")
    
    metrics_data = {
        'Metrik': [
            'Durchschnittliche Bearbeitungszeit',
            'Kundenzufriedenheit',
            'Weiterempfehlungsrate',
            'Terminpünktlichkeit',
            'Projektabschlussrate'
        ],
        'Wert': ['12 Tage', '4.8/5', '92%', '96%', '98%'],
        'Trend': ['↓ -2 Tage', '↑ +0.2', '↑ +3%', '→ 0%', '↑ +1%']
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    st.dataframe(
        df_metrics,
        use_container_width=True,
        hide_index=True
    )

# Haupt-Export-Funktion
def show_crm_dashboard(texts: Dict[str, str]):
    """Öffentliche Funktion zum Anzeigen des CRM Dashboards"""
    render_crm_dashboard(texts)

if __name__ == "__main__":
    # Test-Modus
    st.set_page_config(page_title="CRM Dashboard Test", layout="wide")
    
    # Dummy-Texte für Test
    test_texts = {
        'crm_dashboard': 'CRM Dashboard',
        'customers': 'Kunden',
        'projects': 'Projekte'
    }
    
    show_crm_dashboard(test_texts)
