"""
Datei: pv_visuals.py
Zweck: Stellt spezialisierte 3D-Visualisierungsfunktionen für PV-Analysedaten bereit.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-02
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, Optional
import math # <--- KORREKTUR: Fehlender Import hinzugefügt

# Hilfsfunktion für Texte innerhalb dieses Moduls
def get_text_pv_viz(texts: Dict[str, str], key: str, fallback_text: Optional[str] = None) -> str:
    """
    Holt einen Text aus dem übergebenen Dictionary oder gibt einen Fallback-Text zurück.

    Args:
        texts (Dict[str, str]): Das Dictionary mit den Texten.
        key (str): Der Schlüssel für den gewünschten Text.
        fallback_text (Optional[str]): Ein optionaler Text, der zurückgegeben wird, wenn der Schlüssel nicht gefunden wird.
                                       Standardmäßig wird ein generischer Fallback basierend auf dem Schlüssel erzeugt.

    Returns:
        str: Der angeforderte Text oder der Fallback-Text.
    """
    if fallback_text is None:
        fallback_text = key.replace("_", " ").title() + " (PV Viz Text fehlt)"
    return texts.get(key, fallback_text)

# Hilfsfunktion für den Export von Plotly-Figuren
def _export_plotly_fig_to_bytes_pv_viz(fig: Optional[go.Figure], texts: Dict[str, str]) -> Optional[bytes]:
    """
    Exportiert eine Plotly-Figur als PNG-Bild-Bytes.

    Args:
        fig (Optional[go.Figure]): Die zu exportierende Plotly-Figur.
        texts (Dict[str,str]): Das Text-Dictionary für Fehlermeldungen.

    Returns:
        Optional[bytes]: Die Bild-Bytes im PNG-Format oder None bei einem Fehler.
    """
    if fig is None:
        return None
    try:
        # Erhöhe die Skalierung und definiere eine Standardgröße für bessere Qualität im PDF
        img_bytes = fig.to_image(format="png", scale=2, width=900, height=550)
        return img_bytes
    except Exception as e:
        # Fehlerbehandlung wurde aus der Originaldatei übernommen
        # Im Idealfall würde dieser Fehler an eine zentrale Logging-Stelle gemeldet
        # und nicht direkt in die Konsole geschrieben, es sei denn, es ist ein Debug-Modus aktiv.
        # print(f"pv_visuals.py: Fehler beim Exportieren der Plotly Figur: {e}")
        # Eine UI-Warnung in Streamlit ist hier nicht angebracht, da dies eine Backend-Funktion ist.
        # Der Fehler sollte vom aufrufenden Modul (analysis.py) behandelt werden, falls nötig.
        # Für jetzt bleibt der Print-Befehl auskommentiert, um Konsolen-Spam zu vermeiden.
        # Der Nutzer wird den Fehler durch ein fehlendes Bild im PDF bemerken.
        return None

def render_yearly_production_pv_data(analysis_results: Dict[str, Any], texts: Dict[str, str]):
    """
    Rendert ein 3D-Balkendiagramm der monatlichen PV-Produktion für das erste Jahr.
    Die Visualisierung wird mit Plotly erstellt und in Streamlit angezeigt.
    Die resultierende Grafik wird als Byte-String im `analysis_results` Dictionary für den PDF-Export gespeichert.

    Args:
        analysis_results (Dict[str, Any]): Dictionary mit den Analyseergebnissen,
                                           erwartet `monthly_productions_sim` (Liste von 12 Floats).
                                           Wird modifiziert, um `yearly_production_chart_bytes` hinzuzufügen.
        texts (Dict[str, str]): Dictionary für die Lokalisierung von Titeln und Beschriftungen.
    """
    st.subheader(get_text_pv_viz(texts, "viz_yearly_prod_3d_subheader", "Jahresproduktion – 3D-Monatsbalken"))

    month_labels_str = get_text_pv_viz(texts, "month_names_short_list", "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez")
    month_labels = month_labels_str.split(',')
    if len(month_labels) != 12: # Fallback
        month_labels = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

    production_data = analysis_results.get('monthly_productions_sim')

    if not production_data or not isinstance(production_data, list) or len(production_data) != 12:
        st.warning(get_text_pv_viz(texts, "viz_data_missing_monthly_prod", "Monatliche Produktionsdaten für 3D-Jahresdiagramm nicht verfügbar oder unvollständig."))
        fig_fallback_yearly = go.Figure()
        fig_fallback_yearly.update_layout(title=get_text_pv_viz(texts, "viz_data_unavailable_title", "Daten nicht verfügbar"))
        st.plotly_chart(fig_fallback_yearly, use_container_width=True, key="pv_visuals_yearly_prod_fallback")
        analysis_results['yearly_production_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_fallback_yearly, texts)
        return

    fig_yearly_prod = go.Figure()
    for i, p_val_raw in enumerate(production_data):
        p_val = float(p_val_raw) if isinstance(p_val_raw, (int, float)) and not (math.isnan(p_val_raw) or math.isinf(p_val_raw)) else 0.0
        fig_yearly_prod.add_trace(go.Scatter3d(
            x=[i, i], y=[0, 0], z=[0, p_val],
            mode='lines',
            line=dict(width=20, color=f'hsl({(i/12*300)}, 70%, 60%)'),
            name=month_labels[i],
            hoverinfo='text', text=f"{month_labels[i]}: {p_val:.0f} kWh"
        ))
        fig_yearly_prod.add_trace(go.Scatter3d(
            x=[i], y=[0], z=[p_val], mode='markers',
            marker=dict(size=3, color=f'hsl({(i/12*300)}, 70%, 40%)'),
            hoverinfo='skip'
        ))

    fig_yearly_prod.update_layout(
        title=get_text_pv_viz(texts, "viz_yearly_prod_3d_title", "Jährliche PV-Produktion nach Monaten"),
        scene=dict(
            xaxis=dict(title=get_text_pv_viz(texts, "viz_month_axis_label", "Monat"), tickvals=list(range(12)), ticktext=month_labels),
            yaxis=dict(title='', showticklabels=False, range=[-1, 1]),
            zaxis=dict(title=get_text_pv_viz(texts, "viz_kwh_axis_label", "Produktion (kWh)"))
        ),
        margin=dict(l=10, r=10, t=50, b=10), showlegend=True
    )
    st.plotly_chart(fig_yearly_prod, use_container_width=True, key="pv_visuals_yearly_prod")
    analysis_results['yearly_production_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_yearly_prod, texts)


def render_break_even_pv_data(analysis_results: Dict[str, Any], texts: Dict[str, str]):
    """
    Rendert ein 3D-Liniendiagramm des kumulierten Kapitalflusses, um den Break-Even-Punkt zu visualisieren.
    Die Visualisierung wird mit Plotly erstellt und in Streamlit angezeigt.
    Die resultierende Grafik wird als Byte-String im `analysis_results` Dictionary für den PDF-Export gespeichert.

    Args:
        analysis_results (Dict[str, Any]): Dictionary mit den Analyseergebnissen,
                                           erwartet `simulation_period_years_effective` (int) und
                                           `cumulative_cash_flows_sim` (Liste von Floats, Länge N+1).
                                           Wird modifiziert, um `break_even_chart_bytes` hinzuzufügen.
        texts (Dict[str, str]): Dictionary für die Lokalisierung von Titeln und Beschriftungen.
    """
    st.subheader(get_text_pv_viz(texts, "viz_break_even_3d_subheader", "Break-Even Punkt – Kapitalfluss in 3D"))
    simulation_years = analysis_results.get('simulation_period_years_effective', 0)
    cashflow_data_raw = analysis_results.get('cumulative_cash_flows_sim')

    if not isinstance(simulation_years, int) or simulation_years <= 0 or \
       not cashflow_data_raw or not isinstance(cashflow_data_raw, list) or len(cashflow_data_raw) != (simulation_years + 1):
        st.warning(get_text_pv_viz(texts, "viz_data_missing_cashflow", "Kumulierte Cashflow-Daten für Break-Even-Diagramm nicht verfügbar oder unvollständig."))
        fig_fallback_break_even = go.Figure()
        fig_fallback_break_even.update_layout(title=get_text_pv_viz(texts, "viz_data_unavailable_title", "Daten nicht verfügbar"))
        st.plotly_chart(fig_fallback_break_even, use_container_width=True, key="pv_visuals_break_even_fallback")
        analysis_results['break_even_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_fallback_break_even, texts)
        return

    cashflow_data = [float(cf) if isinstance(cf, (int,float)) and not (math.isnan(cf) or math.isinf(cf)) else 0.0 for cf in cashflow_data_raw]
    years_axis = list(range(simulation_years + 1))

    fig_break_even = go.Figure()
    fig_break_even.add_trace(go.Scatter3d(
        x=years_axis, y=[0]*len(years_axis), z=cashflow_data, mode='lines+markers',
        name=get_text_pv_viz(texts, "viz_cashflow_label", "Kumulierter Kapitalfluss"),
        line=dict(color='green', width=4), marker=dict(size=4)
    ))
    fig_break_even.add_trace(go.Scatter3d(
        x=[years_axis[0], years_axis[-1]], y=[0,0], z=[0,0], mode='lines',
        name='Break-Even Linie', line=dict(color='red', width=2, dash='dash')
    ))
    fig_break_even.update_layout(
        title=get_text_pv_viz(texts, "viz_break_even_3d_title", "Kumulierter Kapitalfluss über die Laufzeit"),
        scene=dict(
            xaxis_title=get_text_pv_viz(texts, "viz_year_axis_label", "Jahr"),
            yaxis_title='', yaxis=dict(showticklabels=False, range=[-1,1]),
            zaxis_title=get_text_pv_viz(texts, "viz_eur_axis_label", "Kapitalfluss (€)")
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )
    st.plotly_chart(fig_break_even, use_container_width=True, key="pv_visuals_break_even")
    analysis_results['break_even_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_break_even, texts)

def render_amortisation_pv_data(analysis_results: Dict[str, Any], texts: Dict[str, str]):
    """
    Rendert ein 3D-Liniendiagramm des Amortisationsverlaufs (Investition vs. kumulierte Rückflüsse).
    Die Visualisierung wird mit Plotly erstellt und in Streamlit angezeigt.
    Die resultierende Grafik wird als Byte-String im `analysis_results` Dictionary für den PDF-Export gespeichert.

    Args:
        analysis_results (Dict[str, Any]): Dictionary mit den Analyseergebnissen, erwartet
                                           `simulation_period_years_effective` (int),
                                           `total_investment_netto` (float), und
                                           `annual_benefits_sim` (Liste von Floats, Länge N).
                                           Wird modifiziert, um `amortisation_chart_bytes` hinzuzufügen.
        texts (Dict[str, str): Dictionary für die Lokalisierung von Titeln und Beschriftungen.
    """
    st.subheader(get_text_pv_viz(texts, "viz_amortisation_3d_subheader", "Amortisation – Rückflusskurve in 3D"))
    simulation_years = analysis_results.get('simulation_period_years_effective', 0)
    total_investment_raw = analysis_results.get('total_investment_netto', 0)
    annual_benefits_raw = analysis_results.get('annual_benefits_sim', [])

    total_investment = float(total_investment_raw) if isinstance(total_investment_raw, (int, float)) and not (math.isnan(total_investment_raw) or math.isinf(total_investment_raw)) else 0.0

    if not isinstance(simulation_years, int) or simulation_years <= 0 or \
       total_investment <= 0 or \
       not annual_benefits_raw or not isinstance(annual_benefits_raw, list) or len(annual_benefits_raw) != simulation_years:
        st.warning(get_text_pv_viz(texts, "viz_data_missing_amortisation", "Daten für Amortisationsdiagramm (Investition, jährl. Vorteile) nicht verfügbar oder unvollständig."))
        fig_fallback_amort = go.Figure()
        fig_fallback_amort.update_layout(title=get_text_pv_viz(texts, "viz_data_unavailable_title", "Daten nicht verfügbar"))
        st.plotly_chart(fig_fallback_amort, use_container_width=True, key="pv_visuals_amortisation_fallback")
        analysis_results['amortisation_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_fallback_amort, texts)
        return

    annual_benefits = [float(b) if isinstance(b, (int, float)) and not (math.isnan(b) or math.isinf(b)) else 0.0 for b in annual_benefits_raw]
    years_axis = list(range(simulation_years + 1))
    kosten_linie = [total_investment] * (simulation_years + 1)

    kumulierte_rueckfluesse = [0.0]
    current_sum_rueckfluss = 0.0
    for benefit_val in annual_benefits:
        current_sum_rueckfluss += benefit_val
        kumulierte_rueckfluesse.append(current_sum_rueckfluss)

    fig_amort = go.Figure()
    fig_amort.add_trace(go.Scatter3d(
        x=years_axis, y=[0]*len(years_axis), z=kosten_linie, mode='lines',
        name=get_text_pv_viz(texts, "viz_cost_label", "Investitionskosten (Netto)"),
        line=dict(color='red', width=3)
    ))
    fig_amort.add_trace(go.Scatter3d(
        x=years_axis, y=[0.1]*len(years_axis), z=kumulierte_rueckfluesse, mode='lines+markers',
        name=get_text_pv_viz(texts, "viz_cumulative_return_label", "Kumulierter Rückfluss"),
        line=dict(color='blue', width=4), marker=dict(size=4)
    ))
    fig_amort.update_layout(
        title=get_text_pv_viz(texts, "viz_amortisation_3d_title", "Amortisationsverlauf: Investition vs. Kumulierter Rückfluss"),
        scene=dict(
            xaxis_title=get_text_pv_viz(texts, "viz_year_axis_label", "Jahr"),
            yaxis_title='', yaxis=dict(showticklabels=False, range=[-0.5, 0.5]),
            zaxis_title=get_text_pv_viz(texts, "viz_eur_axis_label", "Betrag (€)")
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )
    st.plotly_chart(fig_amort, use_container_width=True, key="pv_visuals_amortisation")
    analysis_results['amortisation_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_amort, texts)

def render_co2_savings_visualization(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> None:
    """
    Erstellt eine ansprechende 3D-Visualisierung der CO₂-Einsparungen mit realistischen Grafiken
    für Auto, Flugzeug und Bäume.
    
    Args:
        analysis_results (Dict[str, Any]): Die Analyseergebnisse mit CO₂-Daten.
        texts (Dict[str, str]): Das Text-Dictionary für Labels.
    """
    co2_savings = analysis_results.get('annual_co2_savings_kg', 0.0)
    trees_equiv = analysis_results.get('co2_equivalent_trees_per_year', 0.0)
    car_km_equiv = analysis_results.get('co2_equivalent_car_km_per_year', 0.0)
    
    # Berechnung der Flugzeug-Äquivalente (ca. 230g CO₂ pro km)
    airplane_km_equiv = co2_savings / 0.23 if co2_savings > 0 else 0.0
    
    if co2_savings <= 0:
        st.info(get_text_pv_viz(texts, "co2_no_data", "Keine CO₂-Daten verfügbar für Visualisierung."))
        return
    
    # 3D-Szene mit realistischen Symbolen erstellen
    fig_co2 = go.Figure()
    
    # Bäume (grüne 3D-Kegel als stilisierte Bäume)
    if trees_equiv > 0:
        # Mehrere Bäume in einer Reihe darstellen
        tree_count = min(int(trees_equiv), 20)  # Max 20 Bäume für Übersichtlichkeit
        tree_positions = np.linspace(-5, 5, tree_count)
        
        for i, x_pos in enumerate(tree_positions):
            # Baumstamm (Zylinder)
            fig_co2.add_trace(go.Scatter3d(
                x=[x_pos, x_pos], y=[0, 0], z=[0, 2],
                mode='lines',
                line=dict(color='brown', width=8),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Baumkrone (Kegel)
            theta = np.linspace(0, 2*np.pi, 20)
            cone_x = x_pos + 0.8 * np.cos(theta)
            cone_y = 0.8 * np.sin(theta)
            cone_z = np.full_like(theta, 2)
            
            fig_co2.add_trace(go.Scatter3d(
                x=cone_x, y=cone_y, z=cone_z,
                mode='markers',
                marker=dict(size=12, color='darkgreen', symbol='diamond'),
                showlegend=True if i == 0 else False,
                name=f'{trees_equiv:.0f} Bäume',
                hovertemplate=f'CO₂-Bindung: {trees_equiv:.0f} Bäume<extra></extra>'
            ))
    
    # Auto (3D-Box als stilisiertes Auto)
    if car_km_equiv > 0:
        # Autokarosserie
        car_x = [8, 10, 10, 8, 8, 10, 10, 8]
        car_y = [-1, -1, 1, 1, -1, -1, 1, 1]
        car_z = [0, 0, 0, 0, 1.5, 1.5, 1.5, 1.5]
        
        fig_co2.add_trace(go.Scatter3d(
            x=car_x, y=car_y, z=car_z,
            mode='markers',
            marker=dict(size=8, color='red', symbol='square'),
            name=f'{car_km_equiv:.0f} km Autofahrt',
            hovertemplate=f'Vermiedene Autokilometer: {car_km_equiv:.0f} km<extra></extra>'
        ))
        
        # Räder
        wheel_positions = [(8.2, -1.2, 0.3), (8.2, 1.2, 0.3), (9.8, -1.2, 0.3), (9.8, 1.2, 0.3)]
        for wx, wy, wz in wheel_positions:
            fig_co2.add_trace(go.Scatter3d(
                x=[wx], y=[wy], z=[wz],
                mode='markers',
                marker=dict(size=6, color='black', symbol='circle'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Flugzeug (3D-Form als stilisiertes Flugzeug)
    if airplane_km_equiv > 0:
        # Flugzeugrumpf
        plane_x = [12, 16, 16, 12]
        plane_y = [0, 0, 0, 0]
        plane_z = [2, 2.5, 2.5, 2]
        
        fig_co2.add_trace(go.Scatter3d(
            x=plane_x, y=plane_y, z=plane_z,
            mode='lines+markers',
            line=dict(color='blue', width=6),
            marker=dict(size=6, color='lightblue', symbol='diamond'),
            name=f'{airplane_km_equiv:.0f} km Flugzeug',
            hovertemplate=f'Vermiedene Flugkilometer: {airplane_km_equiv:.0f} km<extra></extra>'
        ))
        
        # Flügel
        wing_x = [14, 12, 16, 14]
        wing_y = [-2, 0, 0, 2]
        wing_z = [2.2, 2.2, 2.2, 2.2]
        
        fig_co2.add_trace(go.Scatter3d(
            x=wing_x, y=wing_y, z=wing_z,
            mode='lines',
            line=dict(color='lightblue', width=4),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # CO₂-Einsparung als zentraler Text-Marker
    fig_co2.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[5],
        mode='markers+text',
        marker=dict(size=20, color='green', symbol='circle'),
        text=[f'{co2_savings:.0f} kg CO₂'],
        textfont=dict(size=16, color='white'),
        textposition='middle center',
        name='Jährliche CO₂-Einsparung',
        hovertemplate=f'Jährliche CO₂-Einsparung: {co2_savings:.0f} kg<extra></extra>'
    ))
    
    # Layout anpassen
    fig_co2.update_layout(
        title=dict(
            text=get_text_pv_viz(texts, "co2_3d_title", "Ihre CO₂-Einsparung in anschaulichen Vergleichen"),
            font=dict(size=18, color='darkgreen')
        ),
        scene=dict(
            xaxis=dict(title='', showticklabels=False, showgrid=False),
            yaxis=dict(title='', showticklabels=False, showgrid=False),
            zaxis=dict(title='', showticklabels=False, showgrid=False),
            bgcolor='lightcyan',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=0.02,
            xanchor='center',
            x=0.5
        )
    )
    
    st.plotly_chart(fig_co2, use_container_width=True, key="co2_savings_3d_viz")
    
    # Export für PDF
    analysis_results['co2_savings_chart_bytes'] = _export_plotly_fig_to_bytes_pv_viz(fig_co2, texts)
    
    # Zusätzliche Info-Boxen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌳 Bäume (CO₂-Bindung)",
            value=f"{trees_equiv:.0f}",
            help="Anzahl Bäume, die dieselbe Menge CO₂ binden würden"
        )
    
    with col2:
        st.metric(
            label="🚗 Vermiedene Autokilometer", 
            value=f"{car_km_equiv:.0f} km",
            help="Entspricht der CO₂-Emission dieser Autokilometer"
        )
    
    with col3:
        st.metric(
            label="✈️ Vermiedene Flugkilometer",
            value=f"{airplane_km_equiv:.0f} km", 
            help="Entspricht der CO₂-Emission dieser Flugkilometer"
        )

# Änderungshistorie
# 2025-06-02, Gemini Ultra: Modul bereinigt, redundanten Code aus analysis.py entfernt. Fokus auf Kernfunktionen von pv_visuals.py.
#                           Keys für st.plotly_chart eindeutig gemacht. Fallback-Figuren bei fehlenden Daten implementiert.
#                           Robuste Datenvalidierung und -konvertierung in allen Rendering-Funktionen hinzugefügt.
#                           Funktion _apply_custom_style_to_fig aus analysis.py entfernt, da pv_visuals seine Styles selbst handhaben oder keine globalen Styles benötigt.
#                           Exportfunktion _export_plotly_fig_to_bytes_pv_viz beibehalten und für Fallback-Figuren genutzt.
# 2025-06-02, Gemini Ultra: Fehlenden `import math` hinzugefügt.