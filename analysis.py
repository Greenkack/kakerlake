
# analysis.py
# Modul für den Analyse Tab / Dashboard (A.5)

import traceback
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
import os
from reportlab.lib import colors # Für HexColor Zugriff
import colorsys # Für HLS/RGB Konvertierungen
from datetime import datetime, timedelta
from calculations import AdvancedCalculationsIntegrator
# HINZUGEFÜGT: Import der kompletten Finanz-Tools
from financial_tools import (
    calculate_annuity, 
    calculate_depreciation, 
    calculate_leasing_costs,
    calculate_financing_comparison,
    calculate_capital_gains_tax,
    calculate_contracting_costs
)

try:
    from app_status import import_errors as global_import_errors_analysis
except ImportError:
    global_import_errors_analysis: List[str] = []


_CALCULATIONS_PERFORM_CALCULATIONS_AVAILABLE = False
_DATABASE_LOAD_ADMIN_SETTING_AVAILABLE = False

try:
    from calculations import perform_calculations as real_perform_calculations  # type: ignore
    if not callable(real_perform_calculations):
        raise ImportError("Imported perform_calculations from calculations.py is not callable.")
    _CALCULATIONS_PERFORM_CALCULATIONS_AVAILABLE = True
    perform_calculations = real_perform_calculations
except ImportError:
    def perform_calculations(project_data, texts=None, errors_list=None, simulation_duration_user=None, electricity_price_increase_user=None):  # type: ignore
        if errors_list is not None: errors_list.append("FEHLER: Berechnungsmodul nicht geladen.")
        return {"calculation_errors": ["Berechnungsmodul nicht geladen."]}
    
    class ExtendedCalculations:  # Dummy-Klasse für Notfall
        def __getattr__(self, name):
            def dummy(*args, **kwargs):
                return {"error": "ExtendedCalculations-Modul nicht geladen."}
            return dummy


try:
    from database import load_admin_setting as real_load_admin_setting # type: ignore
    if not callable(real_load_admin_setting):
        raise ImportError("Imported load_admin_setting from database.py is not callable.")
    _DATABASE_LOAD_ADMIN_SETTING_AVAILABLE = True
    load_admin_setting = real_load_admin_setting
except ImportError:
    def load_admin_setting(key, default=None): # type: ignore
        if key == 'global_constants':
            return {'visualization_settings': {
                        "default_color_palette": "Plotly", "primary_chart_color": "#1f77b4",
                        "secondary_chart_color": "#ff7f0e", "chart_font_family": "Arial, sans-serif",
                        "chart_font_size_title": 16, "chart_font_size_axis_label": 12,
                        "chart_font_size_tick_label": 10
                    }}
        if key == 'economic_settings': return {'reference_specific_yield_for_pr_kwh_per_kwp': 1100.0}
        return default

_ANALYSIS_DEPENDENCIES_AVAILABLE = _CALCULATIONS_PERFORM_CALCULATIONS_AVAILABLE and _DATABASE_LOAD_ADMIN_SETTING_AVAILABLE


# --- Hilfsfunktionen ---
def get_text(texts_dict: Dict[str, str], key: str, fallback_text: Optional[str] = None) -> str:
    if fallback_text is None:
        fallback_text = key.replace("_", " ").title() + " (Text-Key fehlt)"
    return texts_dict.get(key, fallback_text)

def format_kpi_value(value: Any, unit: str = "", na_text_key: str = "not_applicable_short", precision: int = 2, texts_dict: Optional[Dict[str,str]] = None) -> str:
    current_texts = texts_dict if texts_dict is not None else {}
    na_text = get_text(current_texts, na_text_key, "k.A.")
    if value is None: return na_text
    if isinstance(value, (float, int)) and math.isnan(value): return na_text
    if isinstance(value, str) and value == na_text: return value
    if isinstance(value, str):
        try: value = float(value.replace(",", "."))
        except (ValueError, AttributeError): return value
    if isinstance(value, (int, float)):
        if math.isinf(value): return get_text(current_texts, "value_infinite", "Nicht berechenbar")
        if unit == "Jahre": return get_text(current_texts, "years_format_string", "{val:.1f} Jahre").format(val=value)
        formatted_num_str = f"{value:,.{precision}f}"
        if precision > 0:
            parts = formatted_num_str.split('.')
            if len(parts) == 2:
                ganzzahl_teil, dezi_teil = parts; formatted_num_str = ganzzahl_teil.replace(',', '.') + ',' + dezi_teil
            else: formatted_num_str = formatted_num_str.replace(',', '.')
        else: formatted_num_str = formatted_num_str.replace(',', '.')
        return f"{formatted_num_str} {unit}".strip()
    return str(value)

VIZ_DEFAULTS = {
    'color_pv_gen': 'rgba(255, 193, 7, 0.8)',
    'color_self_use': 'rgba(76, 175, 80, 0.8)',
    'color_feed_in': 'rgba(255, 87, 34, 0.8)',
    'color_grid_purchase': 'rgba(33, 150, 243, 0.8)',
    'color_storage_charge': 'rgba(156, 39, 176, 0.7)',
    'color_storage_discharge': 'rgba(124, 77, 255, 0.7)',
    'color_direct_use': 'rgba(0, 150, 136, 0.7)',
    'color_revenue': 'rgba(0, 150, 136, 1)',
    'color_costs': 'rgba(211, 47, 47, 1)',
    'color_savings': 'rgba(76, 175, 80, 1)',
    'color_investment': 'rgba(255, 152, 0, 1)',
    'height_stromfluss': 500,
    'height_sankey': 600,
    'height_cashflow': 500,
    'height_autarkie': 450,
    'font_size': 14,
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(240, 242, 246, 0.8)'
}
def load_viz_settings(db_load_func: Optional[callable] = None) -> Dict[str, Any]:
    """Lädt Visualisierungseinstellungen aus der DB oder verwendet Defaults."""
    settings = VIZ_DEFAULTS.copy()
    if db_load_func:
        try:
            db_settings = db_load_func('visualization_settings')
            if db_settings and isinstance(db_settings, dict):
                settings.update(db_settings)
        except Exception:
            pass
    return settings

def _get_visualization_settings() -> Dict[str, Any]:
    gc = load_admin_setting('global_constants', {})
    default_viz_settings = {
        "default_color_palette": "Plotly", "primary_chart_color": "#1f77b4",
        "secondary_chart_color": "#ff7f0e", "chart_font_family": "Arial, sans-serif",
        "chart_font_size_title": 16, "chart_font_size_axis_label": 12,
        "chart_font_size_tick_label": 10
    }
    loaded_viz_settings = gc.get('visualization_settings') if isinstance(gc, dict) else None
    if isinstance(loaded_viz_settings, dict):
        final_settings = default_viz_settings.copy()
        final_settings.update(loaded_viz_settings)
        return final_settings
    return default_viz_settings.copy()

def _apply_custom_style_to_fig(fig: go.Figure, viz_settings: Dict[str, Any], chart_specific_key: Optional[str] = None, dynamic_colors: Optional[List[str]] = None):
    if not fig: return
    specific_settings = viz_settings.get(chart_specific_key, {}) if chart_specific_key and isinstance(viz_settings.get(chart_specific_key), dict) else {}
    font_family = specific_settings.get("chart_font_family", viz_settings.get("chart_font_family", "Arial, sans-serif"))
    font_size_title = int(specific_settings.get("chart_font_size_title", viz_settings.get("chart_font_size_title", 16)))
    font_size_axis_label = int(specific_settings.get("chart_font_size_axis_label", viz_settings.get("chart_font_size_axis_label", 12)))
    font_size_tick_label = int(specific_settings.get("chart_font_size_tick_label", viz_settings.get("chart_font_size_tick_label", 10)))
    fig.update_layout(font=dict(family=font_family), title_font_size=font_size_title, legend_font_size=font_size_tick_label)
    if hasattr(fig.layout, 'scene') and fig.layout.scene:
         fig.update_scenes(
              xaxis_title_font_size=font_size_axis_label, yaxis_title_font_size=font_size_axis_label, zaxis_title_font_size=font_size_axis_label,
              xaxis_tickfont_size=font_size_tick_label, yaxis_tickfont_size=font_size_tick_label, zaxis_tickfont_size=font_size_tick_label
         )
    else:
        fig.update_xaxes(title_font_size=font_size_axis_label, tickfont_size=font_size_tick_label)
        fig.update_yaxes(title_font_size=font_size_axis_label, tickfont_size=font_size_tick_label)
    final_colorway = None
    if dynamic_colors and isinstance(dynamic_colors, list) and all(isinstance(c, str) for c in dynamic_colors):
        final_colorway = dynamic_colors
    else:
        primary_color = specific_settings.get("primary_chart_color", viz_settings.get("primary_chart_color"))
        secondary_color = specific_settings.get("secondary_chart_color", viz_settings.get("secondary_chart_color"))
        color_discrete_sequence = specific_settings.get("color_discrete_sequence")
        if not color_discrete_sequence and (primary_color or secondary_color):
             color_discrete_sequence = [c for c in [primary_color, secondary_color] if c]
        if color_discrete_sequence:
            final_colorway = color_discrete_sequence
        else:
            default_color_palette_name = viz_settings.get("default_color_palette", "Plotly")
            if default_color_palette_name != "Plotly":
                try:
                    px_color_sequence = getattr(px.colors.qualitative, default_color_palette_name, None)
                    if px_color_sequence: final_colorway = px_color_sequence
                except AttributeError: pass
    if final_colorway:
        fig.update_layout(colorway=final_colorway)

def _export_plotly_fig_to_bytes(fig: Optional[go.Figure], texts: Dict[str,str]) -> Optional[bytes]:
    if fig is None: return None
    try:
        return fig.to_image(format="png", scale=2, width=900, height=550)
    except Exception as e:
        if "kaleido" in str(e).lower() and 'st' in globals() and hasattr(st, 'warning'):
             st.warning(get_text(texts, "analysis_chart_export_error_kaleido_v4", "Hinweis: Diagramm-Export für PDF fehlgeschlagen (Kaleido?). Details: {error_details}").format(error_details=str(e)))
        return None

AVAILABLE_CHART_TYPES = {
    "bar": "Balkendiagramm", "line": "Liniendiagramm",
    "area": "Flächendiagramm", "pie": "Kreisdiagramm",
}
PLOTLY_COLOR_PALETTES = ["Plotly", "D3", "G10", "T10", "Alphabet", "Dark24", "Light24", "Set1", "Set2", "Set3", "Pastel", "Pastel1", "Pastel2", "Antique", "Bold", "Safe", "Vivid"]

def _add_chart_controls(chart_key_prefix: str, texts: Dict[str,str], default_type: str, supported_types: List[str], viz_settings: Dict[str,Any]):
    key_type = f"{chart_key_prefix}_type"
    key_color_palette = f"{chart_key_prefix}_color_palette"
    key_primary_color = f"{chart_key_prefix}_primary_color"
    key_secondary_color = f"{chart_key_prefix}_secondary_color"
    key_color_method = f"color_method_{chart_key_prefix}"

    type_options_display = {key: get_text(texts, f"chart_type_{key}", AVAILABLE_CHART_TYPES.get(key, key.title())) for key in supported_types}
    current_type = st.session_state.get(key_type, default_type)
    current_color_method_is_manual = st.session_state.get(f"color_method_is_manual_{chart_key_prefix}", False)

    default_primary_from_viz = viz_settings.get(chart_key_prefix, {}).get("primary_chart_color", viz_settings.get("primary_chart_color", "#1f77b4"))
    default_secondary_from_viz = viz_settings.get(chart_key_prefix, {}).get("secondary_chart_color", viz_settings.get("secondary_chart_color", "#ff7f0e"))

    if key_primary_color not in st.session_state: st.session_state[key_primary_color] = default_primary_from_viz
    if key_secondary_color not in st.session_state: st.session_state[key_secondary_color] = default_secondary_from_viz
    if key_color_palette not in st.session_state: st.session_state[key_color_palette] = viz_settings.get("default_color_palette", "Plotly")

    col1, col2 = st.columns(2)
    with col1:
        new_type = st.selectbox(
            get_text(texts, "chart_select_type_label", "Diagrammtyp wählen"),
            options=list(type_options_display.keys()),
            format_func=lambda x: type_options_display[x],
            index=list(type_options_display.keys()).index(current_type) if current_type in type_options_display else 0,
            key=f"sb_{key_type}"
        )
        st.session_state[key_type] = new_type
    with col2:
        selected_color_method = st.radio(
            get_text(texts, "chart_select_color_method_label", "Farbwahl"),
            options=["Palette", "Manuell"], key=f"radio_{key_color_method}", horizontal=True,
            index=1 if current_color_method_is_manual else 0
        )
        st.session_state[f"color_method_is_manual_{chart_key_prefix}"] = (selected_color_method == "Manuell")
        if selected_color_method == "Palette":
            new_palette = st.selectbox(
                get_text(texts, "chart_select_palette_label", "Farbpalette wählen"), options=PLOTLY_COLOR_PALETTES,
                index=PLOTLY_COLOR_PALETTES.index(st.session_state.get(key_color_palette)) if st.session_state.get(key_color_palette) in PLOTLY_COLOR_PALETTES else 0,
                key=f"sb_{key_color_palette}"
            )
            st.session_state[key_color_palette] = new_palette
        else:
            new_primary_color = st.color_picker(get_text(texts, "chart_primary_color_label", "Primärfarbe"), value=st.session_state.get(key_primary_color), key=f"cp_{key_primary_color}")
            new_secondary_color = st.color_picker(get_text(texts, "chart_secondary_color_label", "Sekundärfarbe (optional)"), value=st.session_state.get(key_secondaryColor), key=f"cp_{key_secondary_color}")
            st.session_state[key_primary_color] = new_primary_color
            st.session_state[key_secondary_color] = new_secondary_color
    st.markdown("---")

def render_daily_production_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_daily_prod_subheader_switcher", "Tagesproduktion – Stundenbalken (simuliert)"))
    hours = list(range(24))
    anlage_kwp_val = analysis_results.get('anlage_kwp', 0.0)
    if not isinstance(anlage_kwp_val, (int, float)) or anlage_kwp_val <= 0: 
        anlage_kwp_val = 5.0
    
    # Berechne simulierte Stundenproduktion
    power = [round(p, 2) for p in np.maximum(0, np.sin((np.array(hours) - 6) / 12 * np.pi)) * (anlage_kwp_val * 1.3)]
    
    # Erstelle modernes 2D-Balkendiagramm
    fig_daily = go.Figure()
    primary_color = viz_settings.get("primary_chart_color", "#3b82f6")
    
    fig_daily.add_trace(go.Bar(
        x=hours,
        y=power,
        name='Stundenproduktion',
        marker=dict(
            color=power,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="kWh")
        ),
        text=[f"{p:.1f} kWh" for p in power],
        textposition='outside',
        hovertemplate="<b>%{x}:00 Uhr</b><br>Produktion: %{y:.1f} kWh<extra></extra>"
    ))
    
    fig_daily.update_layout(
        title=get_text(texts, "viz_daily_prod_title_switcher", "Simulierte Tagesproduktion"),
        xaxis_title="Stunde",
        yaxis_title="Leistung (kWh)",
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=2,
            ticksuffix=":00"
        ),
        showlegend=False,
        template='plotly_white',
        margin=dict(l=10, r=10, t=50, b=10),
        height=400
    )
    
    _apply_custom_style_to_fig(fig_daily, viz_settings, "daily_production_switcher")
    st.plotly_chart(fig_daily, use_container_width=True, key="analysis_daily_prod_switcher_key_v6_final")
    analysis_results['daily_production_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig_daily, texts)

def render_weekly_production_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_weekly_prod_subheader_switcher", "Wochenproduktion – Heatmap (simuliert)"))
    days = get_text(texts, "day_names_short_list_switcher", "Mo,Di,Mi,Do,Fr,Sa,So").split(',')
    if len(days) != 7: 
        days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    
    hours = list(range(24))
    anlage_kwp_val = analysis_results.get('anlage_kwp', 0.0)
    if not isinstance(anlage_kwp_val, (int, float)) or anlage_kwp_val <= 0: 
        anlage_kwp_val = 5.0
    
    # Erstelle Wochendaten
    Z_weekly = np.maximum(0, np.random.rand(7, 24) * np.sin((np.array(hours) - 6) / 12 * np.pi) * (anlage_kwp_val * 1.2))
    
    # Moderne Heatmap statt 3D-Surface
    fig = go.Figure(data=go.Heatmap(
        z=Z_weekly,
        x=hours,
        y=days,
        colorscale='Blues',
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>Stunde: %{x}:00<br>Produktion: %{z:.1f} kWh<extra></extra>",
        colorbar=dict(title="kWh")
    ))
    
    fig.update_layout(
        title=get_text(texts, "viz_weekly_prod_title_switcher", "Simulierte Wochenproduktion"),
        xaxis=dict(
            title="Stunde",
            tickmode='linear',
            tick0=0,
            dtick=2,
            ticksuffix=":00"
        ),
        yaxis_title="Wochentag",
        template='plotly_white',
        margin=dict(l=10, r=10, t=50, b=10),
        height=400
    )
    
    _apply_custom_style_to_fig(fig, viz_settings, "weekly_production_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_weekly_prod_switcher_key_v6_final")
    analysis_results['weekly_production_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

def render_yearly_production_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_yearly_prod_bar3d_subheader_switcher", "Jahresproduktion – Monatsbalken"))
    month_labels = get_text(texts, "month_names_short_list", "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels) != 12: 
        month_labels = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    production_data_raw = analysis_results.get('monthly_productions_sim', [])
    if not isinstance(production_data_raw, list) or len(production_data_raw) != 12:
        st.warning(get_text(texts, "viz_data_missing_monthly_prod_switcher", "Monatliche Produktionsdaten für Jahresdiagramm nicht verfügbar."))
        analysis_results['yearly_production_switcher_chart_bytes'] = None
        return
    
    production_data = [float(v) if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in production_data_raw]
    
    # Moderne Balkendiagramm mit Farbverlauf
    fig = go.Figure()
    
    # Farben basierend auf Werten (niedrig = blau, hoch = grün)
    colors = []
    max_prod = max(production_data) if production_data else 1
    for prod in production_data:
        intensity = prod / max_prod if max_prod > 0 else 0
        # Gradient von hellblau zu dunkelgrün
        color = f'rgba({int(70 + intensity * 50)}, {int(130 + intensity * 125)}, {int(180 - intensity * 50)}, 0.8)'
        colors.append(color)
    
    fig.add_trace(go.Bar(
        x=month_labels,
        y=production_data,
        name='Monatsproduktion',
        marker=dict(
            color=colors,
            line=dict(color='rgba(50,50,50,0.8)', width=1)
        ),
        text=[f"{p:.0f} kWh" for p in production_data],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Produktion: %{y:.0f} kWh<extra></extra>"
    ))
    
    fig.update_layout(
        title=get_text(texts, "viz_yearly_prod_bar3d_title_switcher", "Jährliche PV-Produktion nach Monaten"),
        xaxis_title="Monat",
        yaxis_title="Produktion (kWh)",
        showlegend=False,
        template='plotly_white',
        margin=dict(l=10, r=10, t=50, b=10),
        height=400
    )
    
    _apply_custom_style_to_fig(fig, viz_settings, "yearly_production_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_yearly_prod_switcher_key_v6_final")
    analysis_results['yearly_production_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

def render_project_roi_matrix_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_project_roi_matrix_switcher", "Projektrendite – Matrixdarstellung (Illustrativ)"))
    total_investment_netto_val = analysis_results.get('total_investment_netto', 0.0)
    if not isinstance(total_investment_netto_val, (int, float)) or total_investment_netto_val <= 0: 
        total_investment_netto_val = 10000.0
    
    invest_options = np.array([val for val in [total_investment_netto_val * f for f in [0.8, 1.0, 1.2]] if val is not None and val > 0])
    if len(invest_options) == 0: 
        invest_options = np.array([8000, 10000, 12000])
    
    sim_period_eff_val = analysis_results.get('simulation_period_years_effective', 0)
    if not isinstance(sim_period_eff_val, int) or sim_period_eff_val <= 0: 
        sim_period_eff_val = 20
    
    laufzeit_options = np.array([max(5, val) for val in [sim_period_eff_val - 5, sim_period_eff_val, sim_period_eff_val + 5] if val is not None])
    if len(laufzeit_options) == 0: 
        laufzeit_options = np.array([15, 20, 25])
    
    annual_financial_benefit_year1_val = analysis_results.get('annual_financial_benefit_year1', 0.0)
    if not isinstance(annual_financial_benefit_year1_val, (int, float)) or annual_financial_benefit_year1_val <= 0: 
        annual_financial_benefit_year1_val = 700.0
    
    ROI_matrix = np.array([
        [((annual_financial_benefit_year1_val * t - i) / i) * 100 if i > 0 else 0 for i in invest_options] 
        for t in laufzeit_options
    ])
    
    # Moderne Heatmap statt 3D-Surface
    fig = go.Figure(data=go.Heatmap(
        z=ROI_matrix,
        x=[f"{int(inv/1000)}k €" for inv in invest_options],
        y=[f"{int(years)} Jahre" for years in laufzeit_options],
        colorscale='RdYlGn',
        hoverongaps=False,
        hovertemplate="<b>Investition:</b> %{x}<br><b>Laufzeit:</b> %{y}<br><b>ROI:</b> %{z:.1f}%<extra></extra>",
        colorbar=dict(title="ROI (%)")
    ))
    
    fig.update_layout(
        title=get_text(texts, "viz_project_roi_matrix_title_switcher", "Illustrative Projektrendite-Matrix"),
        xaxis_title="Investitionssumme",
        yaxis_title="Laufzeit",
        template='plotly_white',
        margin=dict(l=0, r=0, b=0, t=50),
        height=400
    )
    
    _apply_custom_style_to_fig(fig, viz_settings, "project_roi_matrix_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_project_roi_matrix_switcher_key_v6_final")
    analysis_results['project_roi_matrix_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

def render_feed_in_revenue_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_feed_in_revenue_switcher", "Einnahmen aus Einspeisung – Monatsverlauf (Jahr 1)"))
    month_labels = get_text(texts, "month_names_short_list", "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels) != 12: 
        month_labels = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    monthly_feed_in_kwh_raw = analysis_results.get('monthly_feed_in_kwh', [])
    feed_in_tariff_eur_kwh_raw = analysis_results.get('einspeiseverguetung_eur_per_kwh', 0.081)
    
    if not isinstance(monthly_feed_in_kwh_raw, list) or len(monthly_feed_in_kwh_raw) != 12:
        st.warning(get_text(texts, "viz_data_missing_feed_in_revenue_switcher", "Monatliche Einspeisedaten nicht verfügbar."))
        analysis_results['feed_in_revenue_switcher_chart_bytes'] = None
        return
    
    monthly_feed_in_kwh = [float(v) if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in monthly_feed_in_kwh_raw]
    feed_in_tariff_eur_kwh = float(feed_in_tariff_eur_kwh_raw) if isinstance(feed_in_tariff_eur_kwh_raw, (int, float)) and not math.isnan(feed_in_tariff_eur_kwh_raw) and not math.isinf(feed_in_tariff_eur_kwh_raw) else 0.081
    einnahmen = [kwh * feed_in_tariff_eur_kwh for kwh in monthly_feed_in_kwh]
    
    # Kombiniertes Diagramm: Balken für Einnahmen + Linie für kWh
    fig = go.Figure()
    
    # Einnahmen als Balken
    fig.add_trace(go.Bar(
        x=month_labels,
        y=einnahmen,
        name=f'Einnahmen (Tarif: {feed_in_tariff_eur_kwh*100:.1f} ct/kWh)',
        marker_color='rgba(34, 139, 34, 0.7)',
        yaxis='y1',
        hovertemplate="<b>%{x}</b><br>Einnahmen: %{y:.2f} €<extra></extra>"
    ))
    
    # Eingespeiste kWh als Linie (sekundäre y-Achse)
    fig.add_trace(go.Scatter(
        x=month_labels,
        y=monthly_feed_in_kwh,
        mode='lines+markers',
        name='Einspeisung (kWh)',
        line=dict(color='rgba(255, 140, 0, 0.8)', width=3),
        marker=dict(size=8),
        yaxis='y2',
        hovertemplate="<b>%{x}</b><br>Einspeisung: %{y:.0f} kWh<extra></extra>"
    ))
    
    fig.update_layout(
        title=get_text(texts, "viz_feed_in_revenue_title_switcher", "Monatliche Einspeisevergütung (Jahr 1)"),
        xaxis_title="Monat",
        yaxis=dict(
            title="Einnahmen (€)",
            side="left"
        ),
        yaxis2=dict(
            title="Einspeisung (kWh)",
            side="right",
            overlaying="y"
        ),
        template='plotly_white',
        margin=dict(l=0, r=0, b=0, t=50),
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    _apply_custom_style_to_fig(fig, viz_settings, "feed_in_revenue_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_feed_in_revenue_switcher_key_v6_final")
    analysis_results['feed_in_revenue_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

def render_production_vs_consumption_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_prod_vs_cons_switcher", "Verbrauch vs. Produktion – Vergleichsdiagramm (Jahr 1)"))
    month_labels = get_text(texts, "month_names_short_list", "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels) != 12: 
        month_labels = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    verbrauch_raw = analysis_results.get('monthly_consumption_sim', [])
    produktion_raw = analysis_results.get('monthly_productions_sim', [])
    
    if not (isinstance(verbrauch_raw, list) and len(verbrauch_raw) == 12 and isinstance(produktion_raw, list) and len(produktion_raw) == 12):
        st.warning(get_text(texts, "viz_data_missing_prod_cons_switcher", "Monatliche Verbrauchs- oder Produktionsdaten nicht verfügbar."))
        analysis_results['prod_vs_cons_switcher_chart_bytes'] = None
        return
    
    verbrauch = [float(v) if isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in verbrauch_raw]
    produktion = [float(p) if isinstance(p, (int, float)) and not math.isnan(p) and not math.isinf(p) else 0.0 for p in produktion_raw]
    
    # Berechne Differenz und Autarkiegrad
    differenz = [p - v for p, v in zip(produktion, verbrauch)]
    autarkie = [(min(p, v) / v * 100) if v > 0 else 0 for p, v in zip(produktion, verbrauch)]
    
    # Modernes gestapeltes Flächendiagramm
    fig = go.Figure()
    
    # Verbrauch als gefüllte Fläche
    fig.add_trace(go.Scatter(
        x=month_labels,
        y=verbrauch,
        mode='lines',
        name='Verbrauch',
        fill='tozeroy',
        fillcolor='rgba(255, 99, 132, 0.3)',
        line=dict(color='rgba(255, 99, 132, 1)', width=2),
        hovertemplate="<b>%{x}</b><br>Verbrauch: %{y:.0f} kWh<extra></extra>"
    ))
    
    # Produktion als Linie
    fig.add_trace(go.Scatter(
        x=month_labels,
        y=produktion,
        mode='lines+markers',
        name='Produktion',
        line=dict(color='rgba(54, 162, 235, 1)', width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{x}</b><br>Produktion: %{y:.0f} kWh<extra></extra>"
    ))
    
    # Überschuss/Defizit als Balken (sekundäre y-Achse)
    colors = ['rgba(34, 139, 34, 0.6)' if d >= 0 else 'rgba(220, 20, 60, 0.6)' for d in differenz]
    fig.add_trace(go.Bar(
        x=month_labels,
        y=differenz,
        name='Überschuss/Defizit',
        marker_color=colors,
        yaxis='y2',
        hovertemplate="<b>%{x}</b><br>Differenz: %{y:.0f} kWh<extra></extra>"
    ))
    
    fig.update_layout(
        title=get_text(texts, "viz_prod_vs_cons_title_switcher", "Monatlicher Verbrauch vs. Produktion (Jahr 1)"),
        xaxis_title="Monat",
        yaxis=dict(
            title="Verbrauch/Produktion (kWh)",
            side="left"
        ),
        yaxis2=dict(
            title="Überschuss/Defizit (kWh)",
            side="right",
            overlaying="y"
        ),
        template='plotly_white',
        margin=dict(l=0, r=0, b=0, t=50),
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    _apply_custom_style_to_fig(fig, viz_settings, "prod_vs_cons_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_prod_vs_cons_switcher_key_v6_final")
    analysis_results['prod_vs_cons_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)
    
    # Zusätzliche Kennzahlen anzeigen
    col1, col2, col3 = st.columns(3)
    with col1:
        total_production = sum(produktion)
        st.metric("Jahresproduktion", f"{total_production:,.0f} kWh")
    with col2:
        total_consumption = sum(verbrauch)
        st.metric("Jahresverbrauch", f"{total_consumption:,.0f} kWh")
    with col3:
        avg_autarkie = sum(autarkie) / len(autarkie) if autarkie else 0
        st.metric("Ø Autarkiegrad", f"{avg_autarkie:.1f}%")

def render_tariff_cube_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_tariff_cube_switcher", "Tarifvergleich – Anbieter Visualisierung"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("tariff_cube_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    anbieter=['Aktuell','PV-Strom','Alternativ A','Alternativ B']
    aktueller_preis_kwh=float(analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh',0.30))
    lcoe_raw=analysis_results.get('lcoe_euro_per_kwh',0.12)
    lcoe = float(lcoe_raw) if isinstance(lcoe_raw, (int,float)) and not math.isinf(lcoe_raw) and not math.isnan(lcoe_raw) else 0.12
    jahresverbrauch=float(analysis_results.get('total_consumption_kwh_yr',3500.0))
    if jahresverbrauch <= 0: jahresverbrauch = 3500.0
    grundgebuehr=[60,0,80,70]
    arbeitspreis=[aktueller_preis_kwh,lcoe,aktueller_preis_kwh*0.95,aktueller_preis_kwh*1.05]
    gesamt=[g+a*jahresverbrauch for g,a in zip(grundgebuehr,arbeitspreis)]
    
    # 2D/3D Switcher Logic
    chart_type = st.session_state.get("tariff_cube_switcher_type", "2d")
    fig=go.Figure()
    color_sequence = viz_settings.get("colorway", px.colors.qualitative.Plotly)
    if not color_sequence or len(color_sequence) < len(anbieter):
        color_sequence = px.colors.qualitative.Plotly
    
    if chart_type == "2d":
        # 2D Bar Chart
        fig.add_trace(go.Bar(
            x=anbieter,
            y=gesamt,
            text=[f"{cost:.0f}€" for cost in gesamt],
            textposition='outside',
            marker_color=[color_sequence[i%len(color_sequence)] for i in range(len(anbieter))],
            name="Tarifkosten"
        ))
        fig.update_layout(
            title=get_text(texts,"viz_tariff_cube_title_switcher",f"Tarifvergleich bei {jahresverbrauch:.0f} kWh/Jahr"),
            xaxis_title="Anbieter",
            yaxis_title="Gesamtkosten €/Jahr",
            margin=dict(l=0,r=0,b=0,t=60),
            showlegend=False
        )
    else:
        # 3D Visualization (original)
        for i,(anbieter_name,cost) in enumerate(zip(anbieter,gesamt)):
            fig.add_trace(go.Scatter3d(x=[i,i],y=[0,0],z=[0,cost],mode='lines',line=dict(width=30,color=color_sequence[i%len(color_sequence)]),name=f"{anbieter_name} ({arbeitspreis[i]:.2f}€/kWh + {grundgebuehr[i]}€ GG)"))
        fig.update_layout(
            title=get_text(texts,"viz_tariff_cube_title_switcher",f"3D Tarifvergleich bei {jahresverbrauch:.0f} kWh/Jahr"),
            scene=dict(xaxis=dict(title='Anbieter',tickvals=list(range(len(anbieter))),ticktext=anbieter),yaxis=dict(title=''),zaxis=dict(title='Gesamtkosten €/Jahr')),
            margin=dict(l=0,r=0,b=0,t=60),showlegend=True
        )
    
    _apply_custom_style_to_fig(fig,viz_settings,"tariff_cube_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_tariff_cube_switcher_key_v6_final")
    analysis_results['tariff_cube_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_co2_savings_value_switcher(analysis_results: Dict[str, Any],
                                      texts: Dict[str, str],
                                      viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts,
                          "viz_co2_savings_value_switcher",
                          "CO₂-Ersparnis vs. Monetärer Wert"))

    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("co2_savings_value_switcher", texts, "2d", ["2d", "3d"], viz_settings)

    # Import der neuen CO₂-Visualisierung
    try:
        from pv_visuals import render_co2_savings_visualization
        render_co2_savings_visualization(analysis_results, texts)
        st.markdown("---")
    except ImportError as e:
        st.warning(f"CO₂-Visualisierung konnte nicht geladen werden: {e}")

    # Originale monetäre CO₂-Analyse beibehalten
    years_effective = int(analysis_results.get('simulation_period_years_effective', 0))
    if years_effective <= 0:
        st.warning(get_text(texts,
                            "viz_data_invalid_years_co2_switcher_v2",
                            "Ungültige Simulationsdauer für CO2-Diagramm."))
        analysis_results['co2_savings_value_switcher_chart_bytes'] = None
        return

    jahre_axis = np.arange(1, years_effective + 1)
    annual_prod_sim_raw = analysis_results.get('annual_productions_sim', [])
    if not (isinstance(annual_prod_sim_raw, list)
            and len(annual_prod_sim_raw) == years_effective):
        st.warning(get_text(texts,
                            "viz_data_missing_co2_prod_switcher_v2",
                            "CO2: Jährl. Produktionsdaten unvollständig."))
        analysis_results['co2_savings_value_switcher_chart_bytes'] = None
        return

    annual_prod_sim = [
        float(p) if isinstance(p, (int, float))
        and not math.isnan(p)
        and not math.isinf(p) else 0.0
        for p in annual_prod_sim_raw
    ]
    gc = load_admin_setting('global_constants', {})
    co2_factor = float(gc.get('co2_emission_factor_kg_per_kwh', 0.474))
    co2_savings_tonnes_per_year = [
        prod * co2_factor / 1000.0 for prod in annual_prod_sim
    ]

    co2_price_eur = 55
    co2_price_increase = 0.08
    wert_co2_eur_per_year = [
        s * (co2_price_eur * ((1 + co2_price_increase) ** (y - 1)))
        for y, s in enumerate(co2_savings_tonnes_per_year, 1)
    ]

    if any(math.isnan(v) or math.isinf(v) for v in wert_co2_eur_per_year):
        st.warning(get_text(texts,
                            "viz_data_nan_inf_co2_switcher_v2",
                            "CO2: Ungültige Werte (NaN/Inf) in Diagrammdaten."))
        analysis_results['co2_savings_value_switcher_chart_bytes'] = None
        return

    # Chart Type Logic
    chart_type = st.session_state.get("co2_savings_value_switcher_type", "2d")
    
    import plotly.graph_objects as go
    import plotly.express as px

    selected_palette = viz_settings.get("default_color_palette", "Viridis")
    valid_scales = ['Greens', 'Blues', 'Viridis', 'Plotly3', 'Solar', 'Hot']
    scale_co2 = selected_palette if selected_palette in valid_scales else "Greens"
    scale_value = "Blues"

    fig = go.Figure()

    if chart_type == "2d":
        # 2D Side-by-side Bar Chart
        fig.add_trace(go.Bar(
            x=[f"Jahr {y}" for y in jahre_axis],
            y=co2_savings_tonnes_per_year,
            name='CO₂-Einsparung (t)',
            text=[f"{x:.1f}t" for x in co2_savings_tonnes_per_year],
            textposition='outside',
            yaxis='y',
            offsetgroup=1,
            marker_color=px.colors.sequential.__getattribute__(scale_co2)[-3]
        ))
        
        fig.add_trace(go.Bar(
            x=[f"Jahr {y}" for y in jahre_axis],
            y=wert_co2_eur_per_year,
            name='Monetärer Wert (€)',
            text=[f"{x:.0f}€" for x in wert_co2_eur_per_year],
            textposition='outside',
            yaxis='y2',
            offsetgroup=2,
            marker_color=px.colors.sequential.__getattribute__(scale_value)[-3]
        ))
        
        fig.update_layout(
            title=get_text(texts,
                          "viz_co2_savings_value_title_switcher",
                          "CO₂-Einsparnis und monetärer Wert über Zeit"),
            xaxis_title='Jahr',
            yaxis=dict(title='CO₂-Einsparung (Tonnen)', side='left'),
            yaxis2=dict(title='Monetärer Wert (€)', side='right', overlaying='y'),
            barmode='group',
            margin=dict(l=0, r=0, b=0, t=60),
            legend=dict(orientation='h', yanchor='bottom', y=0.02, xanchor='center', x=0.5)
        )
    else:
        # Original 3D Visualization
        # CO₂-Einsparung: vertikale Linien (Bars) bei y=0
        for xi, zi in zip(jahre_axis, co2_savings_tonnes_per_year):
            fig.add_trace(go.Scatter3d(
                x=[xi, xi],
                y=[0, 0],
                z=[0, zi],
                mode='lines',
                line=dict(color=px.colors.sequential.__getattribute__(scale_co2)[-1],
                          width=12),
                showlegend=False
            ))
        # Marker oben auf jedem CO₂-Bar
        fig.add_trace(go.Scatter3d(
            x=jahre_axis,
            y=[0] * years_effective,
            z=co2_savings_tonnes_per_year,
            mode='markers',
            marker=dict(color=co2_savings_tonnes_per_year,
                        colorscale=scale_co2,
                        size=6,
                        showscale=False),
            name='CO₂-Einsparung (t)'
        ))

        # Monetärer Wert: vertikale Linien (Bars) bei y=1
        for xi, zi in zip(jahre_axis, wert_co2_eur_per_year):
            fig.add_trace(go.Scatter3d(
                x=[xi, xi],
                y=[1, 1],
                z=[0, zi],
                mode='lines',
                line=dict(color=px.colors.sequential.__getattribute__(scale_value)[-1],
                          width=12),
                showlegend=False
            ))
        # Marker oben auf jedem Wert-Bar
        fig.add_trace(go.Scatter3d(
            x=jahre_axis,
            y=[1] * years_effective,
            z=wert_co2_eur_per_year,
            mode='markers',
            marker=dict(color=wert_co2_eur_per_year,
                        colorscale=scale_value,
                        size=6,
                        showscale=True,
                        colorbar=dict(title='Wert (€)')),
            name='Monetärer Wert (€)'
        ))

        fig.update_layout(
            title=dict(
                text=get_text(texts,
                              "viz_co2_savings_value_title_switcher",
                              "CO₂-Einsparnis und monetärer Wert über Zeit (3D)"),
                font=dict(size=16)
            ),
            scene=dict(
                xaxis=dict(title='Jahr'),
                yaxis=dict(
                    title='Kategorie',
                    tickvals=[0, 1],
                    ticktext=['CO₂-Ersparnis', 'Monetärer Wert']
                ),
                zaxis=dict(title='Menge'),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            margin=dict(l=0, r=0, b=0, t=60),
            legend=dict(orientation='h',
                        yanchor='bottom',
                        y=0.02,
                        xanchor='center',
                        x=0.5),
            template='plotly_white'
        )

    _apply_custom_style_to_fig(fig, viz_settings, "co2_savings_value_switcher")
    st.plotly_chart(fig,
                    use_container_width=True,
                    key="analysis_co2_savings_value_switcher_key_v6_final")
    analysis_results['co2_savings_value_switcher_chart_bytes'] = \
        _export_plotly_fig_to_bytes(fig, texts)

    # Zusätzliche Metriken anzeigen
    col1, col2, col3 = st.columns(3)

    with col1:
        total_co2_savings = sum(co2_savings_tonnes_per_year)
        st.metric(
            label="Gesamte CO₂-Einsparung",
            value=f"{total_co2_savings:.1f} Tonnen",
            help=f"Über {years_effective} Jahre hinweg"
        )

    with col2:
        total_co2_value = sum(wert_co2_eur_per_year)
        st.metric(
            label="Gesamtwert CO₂-Einsparung",
            value=f"{total_co2_value:.0f} €",
            help="Basierend auf prognostizierter CO₂-Preisentwicklung"
        )

    with col3:
        avg_annual_co2 = total_co2_savings / years_effective if years_effective > 0 else 0
        st.metric(
            label="Durchschnitt pro Jahr",
            value=f"{avg_annual_co2:.2f} Tonnen",
            help="Durchschnittliche jährliche CO₂-Einsparung"
        )

def render_investment_value_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_investment_value_subheader_switcher", "Investitionsnutzwert – Wirkung von Maßnahmen"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("investment_value_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    base_investment_raw = analysis_results.get('total_investment_netto'); annual_benefits_sim_raw = analysis_results.get('annual_benefits_sim')
    simulation_period_raw = analysis_results.get('simulation_period_years_effective'); storage_cost_aufpreis_raw = analysis_results.get('cost_storage_aufpreis_product_db_netto')
    if not isinstance(base_investment_raw, (int, float)) or base_investment_raw <= 0:
        st.info(f"Investitionsnutzwert: Ungültige Basisinvestition ({base_investment_raw})."); analysis_results['investment_value_switcher_chart_bytes']=None; return
    base_investment = float(base_investment_raw)
    if not isinstance(annual_benefits_sim_raw, list) or not annual_benefits_sim_raw:
        simulation_period = int(simulation_period_raw if isinstance(simulation_period_raw,int) and simulation_period_raw > 0 else 20)
        base_benefit_total_sim = base_investment * 0.07 * simulation_period
    else: base_benefit_total_sim = sum(float(b) for b in annual_benefits_sim_raw if b is not None and not math.isnan(b) and not math.isinf(b))
    massnahmen_labels = [get_text(texts,"measure_base_pv_switcher","Basis-Anlage"),get_text(texts,"measure_optimized_orientation_switcher","Optimierte Ausrichtung"),get_text(texts,"measure_with_storage_switcher","Mit Speicher"),get_text(texts,"measure_pv_heatpump_switcher","PV + Wärmepumpe")]
    storage_cost_input = float(storage_cost_aufpreis_raw if isinstance(storage_cost_aufpreis_raw,(int,float)) else 0.0)
    storage_cost_factor = (storage_cost_input/base_investment) if base_investment > 0 and storage_cost_input > 0 else 0.3
    kosten_faktoren=[1.0,1.02,1.0+storage_cost_factor,1.0+storage_cost_factor+0.4]; nutzen_faktoren=[1.0,1.05,1.10,1.20]
    kosten_abs=[base_investment*f for f in kosten_faktoren]; nutzwert_simuliert_abs=[base_benefit_total_sim*f for f in nutzen_faktoren]
    effizienz_roi=[(n-k)/k*100 if k!=0 else 0 for k,n in zip(kosten_abs,nutzwert_simuliert_abs)]
    
    # Chart Type Logic
    chart_type = st.session_state.get("investment_value_switcher_type", "2d")
    fig=go.Figure()
    selected_palette = viz_settings.get("default_color_palette","Viridis"); valid_continuous_scales = ['Viridis','Blues','Plotly3','Solar','Hot']
    marker_colorscale = selected_palette if selected_palette in valid_continuous_scales else "Viridis"
    
    if chart_type == "2d":
        # 2D Bubble Chart
        fig.add_trace(go.Scatter(
            x=kosten_abs,
            y=effizienz_roi,
            mode='markers+text',
            marker=dict(
                size=[15 + (roi/10) for roi in effizienz_roi],  # Variable bubble size
                color=effizienz_roi,
                colorscale=marker_colorscale,
                showscale=True,
                colorbar=dict(title='ROI (%)')
            ),
            text=massnahmen_labels,
            textposition='top center',
            customdata=np.transpose([kosten_abs,nutzwert_simuliert_abs,effizienz_roi]),
            hovertemplate="<b>Maßnahme:</b> %{text}<br><b>Kosten:</b> %{customdata[0]:.0f} €<br><b>Nutzen:</b> %{customdata[1]:.0f} €<br><b>Rendite:</b> %{customdata[2]:.0f}%<extra></extra>",
            name="Maßnahmen"
        ))
        fig.update_layout(
            title=get_text(texts,"viz_investment_value_title_switcher","Investitionsnutzwert Vergleich"),
            xaxis_title='Kosten (€)',
            yaxis_title='Gesamtrendite (%)',
            margin=dict(l=0,r=0,b=0,t=60),
            showlegend=False
        )
    else:
        # Original 3D Version
        fig.add_trace(go.Scatter3d(x=massnahmen_labels,y=kosten_abs,z=effizienz_roi,mode='markers+text',marker=dict(size=12,color=effizienz_roi,colorscale=marker_colorscale,showscale=True,colorbar_title_text='Gesamtrendite (%)'),text=[f"{eff:.0f}%" for eff in effizienz_roi],textposition='middle right',customdata=np.transpose([kosten_abs,nutzwert_simuliert_abs,effizienz_roi]),hovertemplate="<b>Maßnahme:</b> %{x}<br><b>Kosten:</b> %{customdata[0]:.0f} €<br><b>Nutzen:</b> %{customdata[1]:.0f} €<br><b>Rendite:</b> %{customdata[2]:.0f}%<extra></extra>"))
        fig.update_layout(title=get_text(texts,"viz_investment_value_title_switcher","3D Investitionsnutzwert"),scene=dict(xaxis_title='Maßnahme',yaxis_title='Kosten (€)',zaxis_title='Gesamtrendite (%)'),margin=dict(l=0,r=0,b=0,t=60))
    
    _apply_custom_style_to_fig(fig,viz_settings,"investment_value_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_investment_value_switcher_key_v6_final")
    analysis_results['investment_value_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_storage_effect_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_storage_effect_subheader_switcher", "Speicherwirkung – Kapazität vs. Nutzen"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("storage_effect_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    current_storage_cap_kwh_raw = analysis_results.get('selected_storage_storage_power_kw'); include_storage_flag = analysis_results.get('include_storage', False)
    current_storage_cap_kwh = float(current_storage_cap_kwh_raw if isinstance(current_storage_cap_kwh_raw,(int,float)) else 0.0) if include_storage_flag else 0.0
    total_consumption_kwh_yr_raw = analysis_results.get('total_consumption_kwh_yr'); aktueller_strompreis_raw = analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh')
    stromkosten_ohne_pv_jahr1_val = (float(total_consumption_kwh_yr_raw if isinstance(total_consumption_kwh_yr_raw,(int,float)) else 3500.0) * float(aktueller_strompreis_raw if isinstance(aktueller_strompreis_raw,(int,float)) else 0.30))
    max_potential_storage_benefit_eur = stromkosten_ohne_pv_jahr1_val * 0.4; denominator_heuristic = (10*(1-np.exp(-0.3*10)))
    scaling_factor_heuristic = (max_potential_storage_benefit_eur/denominator_heuristic) if max_potential_storage_benefit_eur > 0 and denominator_heuristic != 0 else 150.0
    kapazitaet_range_kwh = np.linspace(0,20,30); nutzwert_illustrativ_eur = kapazitaet_range_kwh*(1-np.exp(-0.3*kapazitaet_range_kwh))*scaling_factor_heuristic
    nutzwert_illustrativ_eur = np.nan_to_num(nutzwert_illustrativ_eur,nan=0.0,posinf=0.0,neginf=0.0)
    
    # Chart Type Logic
    chart_type = st.session_state.get("storage_effect_switcher_type", "2d")
    fig=go.Figure()
    line_color = viz_settings.get("primary_chart_color", "purple")
    marker_color = viz_settings.get("secondary_chart_color", "red")
    
    if chart_type == "2d":
        # 2D Line Chart
        fig.add_trace(go.Scatter(
            x=kapazitaet_range_kwh,
            y=nutzwert_illustrativ_eur,
            mode='lines+markers',
            line=dict(color=line_color, width=3),
            marker=dict(color=line_color, size=4),
            name='Nutzenverlauf'
        ))
        if current_storage_cap_kwh > 0:
            current_nutzwert_on_curve_raw = current_storage_cap_kwh*(1-np.exp(-0.3*current_storage_cap_kwh))*scaling_factor_heuristic
            current_nutzwert_on_curve = np.nan_to_num(current_nutzwert_on_curve_raw,nan=0.0,posinf=0.0,neginf=0.0)
            fig.add_trace(go.Scatter(
                x=[current_storage_cap_kwh],
                y=[current_nutzwert_on_curve],
                mode='markers',
                marker=dict(color=marker_color, size=12, symbol='x'),
                name=f'Gewählter Speicher ({current_storage_cap_kwh:.1f} kWh)'
            ))
        fig.update_layout(
            title=get_text(texts,"viz_storage_effect_title_switcher","Speicherwirkung"),
            xaxis_title='Speicherkapazität (kWh)',
            yaxis_title='Jährl. Einsparpotenzial (€)',
            margin=dict(l=0,r=0,b=0,t=50)
        )
    else:
        # Original 3D Version
        fig.add_trace(go.Scatter3d(x=kapazitaet_range_kwh,y=[0]*len(kapazitaet_range_kwh),z=nutzwert_illustrativ_eur,mode='lines+markers',line=dict(color=line_color,width=4),name='Simulierter Nutzenverlauf'))
        if current_storage_cap_kwh > 0:
            current_nutzwert_on_curve_raw = current_storage_cap_kwh*(1-np.exp(-0.3*current_storage_cap_kwh))*scaling_factor_heuristic
            current_nutzwert_on_curve = np.nan_to_num(current_nutzwert_on_curve_raw,nan=0.0,posinf=0.0,neginf=0.0)
            fig.add_trace(go.Scatter3d(x=[current_storage_cap_kwh],y=[0],z=[current_nutzwert_on_curve],mode='markers',marker=dict(color=marker_color,size=10,symbol='x'),name=f'Ausgew. Speicher ({current_storage_cap_kwh:.1f} kWh)'))
        fig.update_layout(title=get_text(texts,"viz_storage_effect_title_switcher","3D Speicherwirkung"),scene=dict(xaxis_title='Speicherkapazität (kWh)',yaxis_title='',zaxis_title='Jährl. Einsparpotenzial (€, illustrativ)'),margin=dict(l=0,r=0,b=0,t=50))
    
    _apply_custom_style_to_fig(fig,viz_settings,"storage_effect_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_storage_effect_switcher_key_v6_final")
    analysis_results['storage_effect_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_selfuse_stack_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_selfuse_stack_subheader_switcher", "Eigenverbrauch vs. Einspeisung – Jährlicher Stack"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("selfuse_stack_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    years_effective=int(analysis_results.get('simulation_period_years_effective',0))
    if years_effective <= 0: st.info(get_text(texts,"viz_data_insufficient_selfuse_stack","Simulationsdauer 0, Eigenverbrauchs-Stack nicht anzeigbar.")); analysis_results['selfuse_stack_switcher_chart_bytes']=None; return
    jahre_sim_labels=[f"Jahr {i}" for i in range(1,years_effective+1)]; annual_prod_sim_raw=analysis_results.get('annual_productions_sim',[])
    annual_prod_sim=[float(p) for p in annual_prod_sim_raw if isinstance(p,(int,float)) and not math.isnan(p) and not math.isinf(p)]
    if not (annual_prod_sim and len(annual_prod_sim)==years_effective):
        st.info(get_text(texts,"viz_data_insufficient_selfuse_stack_prod",f"Daten für 'annual_productions_sim' unvollständig.")); analysis_results['selfuse_stack_switcher_chart_bytes']=None; return
    monthly_direct_sc_yr1_sum=sum(float(v) for v in analysis_results.get('monthly_direct_self_consumption_kwh',[]) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v))
    monthly_storage_discharge_sc_yr1_sum=sum(float(v) for v in analysis_results.get('monthly_storage_discharge_for_sc_kwh',[]) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v))
    eigenverbrauch_yr1_kwh=monthly_direct_sc_yr1_sum+monthly_storage_discharge_sc_yr1_sum
    einspeisung_yr1_kwh=sum(float(v) for v in analysis_results.get('monthly_feed_in_kwh',[]) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v))
    produktion_yr1_kwh_raw = analysis_results.get('annual_pv_production_kwh')
    produktion_yr1_kwh = float(produktion_yr1_kwh_raw if isinstance(produktion_yr1_kwh_raw, (int,float)) and produktion_yr1_kwh_raw > 0 else 1.0)
    anteil_eigenverbrauch_yr1=eigenverbrauch_yr1_kwh/produktion_yr1_kwh; anteil_einspeisung_yr1=einspeisung_yr1_kwh/produktion_yr1_kwh
    eigen_sim_kwh=[prod*anteil_eigenverbrauch_yr1 for prod in annual_prod_sim]; einspeisung_sim_kwh=[prod*anteil_einspeisung_yr1 for prod in annual_prod_sim]
    
    # Chart Type Logic
    chart_type = st.session_state.get("selfuse_stack_switcher_type", "2d")
    fig=go.Figure()
    color_ev = viz_settings.get("primary_chart_color", "blue"); color_feedin = viz_settings.get("secondary_chart_color", "orange")
    
    if chart_type == "2d":
        # 2D Stacked Bar Chart
        fig.add_trace(go.Bar(
            x=jahre_sim_labels,
            y=eigen_sim_kwh,
            name='Eigenverbrauch (kWh)',
            marker_color=color_ev,
            text=[f"{val:.0f}" for val in eigen_sim_kwh],
            textposition='inside'
        ))
        fig.add_trace(go.Bar(
            x=jahre_sim_labels,
            y=einspeisung_sim_kwh,
            name='Einspeisung (kWh)',
            marker_color=color_feedin,
            text=[f"{val:.0f}" for val in einspeisung_sim_kwh],
            textposition='inside'
        ))
        fig.update_layout(
            title=get_text(texts,"viz_selfuse_stack_title_switcher","Eigenverbrauch vs. Einspeisung"),
            xaxis_title='Simulationsjahr',
            yaxis_title='Energie (kWh)',
            barmode='stack',
            margin=dict(l=0,r=0,b=0,t=60),
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01)
        )
    else:
        # Original 3D Version
        bar_width_yz=0.4
        for i,year_label in enumerate(jahre_sim_labels):
            fig.add_trace(go.Scatter3d(x=[year_label,year_label],y=[0,0],z=[0,eigen_sim_kwh[i]],mode='lines',line=dict(width=15,color=color_ev),name='Eigenverbrauch (kWh)' if i==0 else None,legendgroup='Eigenverbrauch',showlegend=(i==0),hoverinfo="x+z"))
            fig.add_trace(go.Scatter3d(x=[year_label,year_label],y=[bar_width_yz,bar_width_yz],z=[0,einspeisung_sim_kwh[i]],mode='lines',line=dict(width=15,color=color_feedin),name='Einspeisung (kWh)' if i==0 else None,legendgroup='Einspeisung',showlegend=(i==0),hoverinfo="x+z"))
        fig.update_layout(title=get_text(texts,"viz_selfuse_stack_title_switcher","3D Eigenverbrauch vs. Einspeisung"),scene=dict(xaxis_title='Simulationsjahr',yaxis_title='Kategorie',yaxis=dict(tickvals=[0,bar_width_yz],ticktext=['Eigenverbrauch','Einspeisung'],range=[-0.5,bar_width_yz+0.5]),zaxis_title='Energie (kWh)'),margin=dict(l=0,r=0,b=0,t=60),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    
    _apply_custom_style_to_fig(fig,viz_settings,"selfuse_stack_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_selfuse_stack_switcher_key_v6_final")
    analysis_results['selfuse_stack_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_cost_growth_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_cost_growth_subheader_switcher", "Stromkostensteigerung – Szenarien"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("cost_growth_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    years_effective=int(analysis_results.get('simulation_period_years_effective',0))
    if years_effective<=0: st.info(get_text(texts,"viz_data_insufficient_cost_growth","Simulationsdauer 0.")); analysis_results['cost_growth_switcher_chart_bytes']=None; return
    jahre_axis=np.arange(1,years_effective+1)
    basispreis_kwh=float(analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh',0.30))
    current_increase_rate_percent=float(analysis_results.get('electricity_price_increase_rate_effective_percent',3.0))
    szenarien_prozent_vals=sorted(list(set(round(s,1) for s in [max(0,current_increase_rate_percent-1.5),current_increase_rate_percent,current_increase_rate_percent+1.5])))
    
    # Chart Type Logic
    chart_type = st.session_state.get("cost_growth_switcher_type", "2d")
    fig=go.Figure(); z_surface=[]
    color_sequence = viz_settings.get("colorway", px.colors.qualitative.Plotly)
    if not color_sequence or len(color_sequence) < len(szenarien_prozent_vals) : color_sequence = px.colors.qualitative.Plotly
    
    if chart_type == "2d":
        # 2D Line Chart for different scenarios
        for idx_s, s_percent in enumerate(szenarien_prozent_vals):
            s_rate=s_percent/100.0
            kosten_kwh_pro_jahr=[basispreis_kwh*((1+s_rate)**(jahr-1)) for jahr in jahre_axis]
            z_surface.append(kosten_kwh_pro_jahr)
            fig.add_trace(go.Scatter(
                x=jahre_axis,
                y=kosten_kwh_pro_jahr,
                mode='lines+markers',
                name=f"{s_percent:.1f}% p.a.",
                line=dict(width=3, color=color_sequence[idx_s % len(color_sequence)]),
                marker=dict(size=4)
            ))
        fig.update_layout(
            title=get_text(texts,"viz_cost_growth_title_switcher","Strompreisentwicklung (Szenarien)"),
            xaxis_title='Simulationsjahr',
            yaxis_title='Strompreis (€/kWh)',
            margin=dict(l=0,r=0,b=0,t=60)
        )
    else:
        # Original 3D Version with Surface
        for idx_s, s_percent in enumerate(szenarien_prozent_vals):
            s_rate=s_percent/100.0; kosten_kwh_pro_jahr=[basispreis_kwh*((1+s_rate)**(jahr-1)) for jahr in jahre_axis]
            z_surface.append(kosten_kwh_pro_jahr)
            fig.add_trace(go.Scatter3d(x=jahre_axis,y=[s_percent]*len(jahre_axis),z=kosten_kwh_pro_jahr,mode='lines',name=f"{s_percent:.1f}% p.a.",line=dict(width=4, color=color_sequence[idx_s % len(color_sequence)])))
        if len(szenarien_prozent_vals)>1 and len(jahre_axis)>1:
            try:
                surface_palette = viz_settings.get("default_color_palette", "Blues")
                valid_continuous_scales = ['Blues','Greens','Viridis','Plotly3','Solar','Hot', 'Cividis']
                surface_colorscale = surface_palette if surface_palette in valid_continuous_scales else "Blues"
                fig.add_trace(go.Surface(x=jahre_axis,y=szenarien_prozent_vals,z=np.array(z_surface),colorscale=surface_colorscale,opacity=0.7,showscale=False,name='Kostenfläche'))
            except Exception as e_surface: st.warning(f"Oberfläche Kostenwachstum: {e_surface}")
        fig.update_layout(title=get_text(texts,"viz_cost_growth_title_switcher","3D Strompreisentwicklung"),scene=dict(xaxis_title='Simulationsjahr',yaxis_title='Jährliche Steigerung (%)',zaxis_title='Strompreis (€/kWh)',yaxis=dict(tickvals=szenarien_prozent_vals,ticktext=[f"{s:.1f}%" for s in szenarien_prozent_vals])),margin=dict(l=0,r=0,b=0,t=60))
    
    _apply_custom_style_to_fig(fig,viz_settings,"cost_growth_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_cost_growth_switcher_key_v6_final")
    analysis_results['cost_growth_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)


def render_selfuse_ratio_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_selfuse_ratio_subheader_switcher", "Eigenverbrauchsgrad – Monatliche Übersicht"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("selfuse_ratio_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    month_labels = get_text(texts,"month_names_short_list","Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels)!=12: month_labels = ["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
    m_total_cons_raw=analysis_results.get('monthly_consumption_sim',[]); m_direct_sc_raw=analysis_results.get('monthly_direct_self_consumption_kwh',[]); m_storage_sc_raw=analysis_results.get('monthly_storage_discharge_for_sc_kwh',[])
    m_total_cons=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in m_total_cons_raw]
    m_direct_sc=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in m_direct_sc_raw]
    m_storage_sc=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in m_storage_sc_raw]
    if not (len(m_total_cons)==12 and len(m_direct_sc)==12 and len(m_storage_sc)==12):
        st.info(get_text(texts,"viz_data_insufficient_selfuse_ratio","Daten für monatl. Eigenverbrauchsgrad unvollständig.")); analysis_results['selfuse_ratio_switcher_chart_bytes']=None; return
    ev_monat_kwh=[(d or 0)+(s or 0) for d,s in zip(m_direct_sc,m_storage_sc)]
    ev_monat_grad=[(ekwh/(c_tot if c_tot>0 else 1)*100) for ekwh,c_tot in zip(ev_monat_kwh,m_total_cons)]
    max_ev_kwh=max(ev_monat_kwh) if any(ev_monat_kwh) else 1.0
    bubble_sizes=[(v/max_ev_kwh*30)+10 for v in ev_monat_kwh]
    
    # Chart Type Logic
    chart_type = st.session_state.get("selfuse_ratio_switcher_type", "2d")
    fig=go.Figure()
    color_scale_name = viz_settings.get("default_color_palette","YlGnBu"); valid_continuous_scales = ['YlGnBu','Blues','Greens','Viridis','Plotly3']
    marker_colorscale = color_scale_name if color_scale_name in valid_continuous_scales else "YlGnBu"
    
    if chart_type == "2d":
        # 2D Bubble Chart
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=ev_monat_grad,
            mode='markers+text',
            marker=dict(
                size=bubble_sizes,
                color=ev_monat_grad,
                colorscale=marker_colorscale,
                showscale=True,
                colorbar=dict(title='Anteil (%)')
            ),
            text=[f"{v:.0f}%" for v in ev_monat_grad],
            textposition='top center',
            customdata=ev_monat_kwh,
            hovertemplate="<b>Monat:</b> %{x}<br><b>Eigenversorgungsgrad:</b> %{y:.0f}%<br><b>Abs. Eigenverbrauch:</b> %{customdata:.0f} kWh<extra></extra>",
            name="Eigenverbrauchsgrad"
        ))
        fig.update_layout(
            title=get_text(texts,"viz_selfuse_ratio_title_switcher","Monatlicher Eigenversorgungsgrad (Jahr 1)"),
            xaxis_title='Monat',
            yaxis_title='Eigenversorgungsgrad (%)',
            margin=dict(l=0,r=0,b=0,t=60),
            showlegend=False
        )
    else:
        # Original 3D Version
        fig.add_trace(go.Scatter3d(x=month_labels,y=[0]*12,z=ev_monat_grad,mode='markers+text',marker=dict(size=bubble_sizes,color=ev_monat_grad,colorscale=marker_colorscale,showscale=True,colorbar_title_text='Anteil (%)'),text=[f"{v:.0f}%" for v in ev_monat_grad],textposition='top center',customdata=ev_monat_kwh,hovertemplate="<b>Monat:</b> %{x}<br><b>Eigenversorgungsgrad:</b> %{z:.0f}%<br><b>Abs. Eigenverbrauch:</b> %{customdata:.0f} kWh<extra></extra>"))
        fig.update_layout(title=get_text(texts,"viz_selfuse_ratio_title_switcher","3D Eigenversorgungsgrad"),scene=dict(xaxis_title='Monat',yaxis_title='',zaxis_title='Eigenversorgungsgrad (%)'),margin=dict(l=0,r=0,b=0,t=60))
    
    _apply_custom_style_to_fig(fig,viz_settings,"selfuse_ratio_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_selfuse_ratio_switcher_key_v6_final")
    analysis_results['selfuse_ratio_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_roi_comparison_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_roi_comparison_subheader_switcher", "ROI-Vergleich – Investitionen"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("roi_comparison_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    curr_proj_name=get_text(texts,"current_project_label_switcher","Aktuelles Projekt"); curr_invest_raw=analysis_results.get('total_investment_netto'); curr_benefit_raw=analysis_results.get('annual_financial_benefit_year1')
    curr_invest=float(curr_invest_raw if isinstance(curr_invest_raw,(int,float)) and curr_invest_raw>0 else 12000.0)
    curr_benefit=float(curr_benefit_raw if isinstance(curr_benefit_raw,(int,float)) else 800.0)
    labels=[curr_proj_name,'Alternativ A (Günstiger)','Alternativ B (Premium)']; invest_opts=[curr_invest,curr_invest*0.8,curr_invest*1.3]
    benefit_opts=[curr_benefit,curr_benefit*0.75,curr_benefit*1.2]; roi_opts=[(b/i*100) if i>0 else 0 for i,b in zip(invest_opts,benefit_opts)]
    
    # Chart Type Logic
    chart_type = st.session_state.get("roi_comparison_switcher_type", "2d")
    fig=go.Figure()
    color_scale_name = viz_settings.get("default_color_palette","RdYlGn"); valid_continuous_scales = ['RdYlGn','Viridis','Plotly3','Solar','Hot']
    marker_colorscale = color_scale_name if color_scale_name in valid_continuous_scales else "RdYlGn"
    
    if chart_type == "2d":
        # 2D Bubble Chart
        fig.add_trace(go.Scatter(
            x=invest_opts,
            y=roi_opts,
            mode='markers+text',
            marker=dict(
                size=[15 + (roi/5) for roi in roi_opts],  # Variable bubble size based on ROI
                color=roi_opts,
                colorscale=marker_colorscale,
                showscale=True,
                colorbar=dict(title='ROI (%)')
            ),
            text=labels,
            textposition='top center',
            customdata=np.transpose([invest_opts,benefit_opts,roi_opts]),
            hovertemplate="<b>Projekt:</b> %{text}<br><b>Investition:</b> %{customdata[0]:.0f} €<br><b>Jährl. Nutzen:</b> %{customdata[1]:.0f} €<br><b>Jährl. ROI:</b> %{customdata[2]:.1f}%<extra></extra>",
            name="ROI Vergleich"
        ))
        fig.update_layout(
            title=get_text(texts,"viz_roi_comparison_title_switcher","ROI-Vergleich von PV-Anlagen-Szenarien"),
            xaxis_title="Investition (€)",
            yaxis_title="Jährlicher ROI (%)",
            margin=dict(l=0,r=0,b=0,t=60),
            showlegend=False
        )
    else:
        # Original 3D Version
        fig.add_trace(go.Scatter3d(x=labels,y=invest_opts,z=roi_opts,mode='markers+text',marker=dict(size=12,color=roi_opts,colorscale=marker_colorscale,showscale=True,colorbar_title_text='Jährl. ROI (%)'),text=[f"{r:.1f}%" for r in roi_opts],textposition="middle right",customdata=np.transpose([invest_opts,benefit_opts,roi_opts]),hovertemplate="<b>Projekt:</b> %{x}<br><b>Investition:</b> %{customdata[0]:.0f} €<br><b>Jährl. Nutzen:</b> %{customdata[1]:.0f} €<br><b>Jährl. ROI:</b> %{customdata[2]:.1f}%<extra></extra>"))
        fig.update_layout(title=get_text(texts,"viz_roi_comparison_title_switcher","3D ROI-Vergleich"),scene=dict(xaxis_title="Projekt-Szenario",yaxis_title="Investition (€)",zaxis_title="Jährlicher ROI (%)"),margin=dict(l=0,r=0,b=0,t=60))
    
    _apply_custom_style_to_fig(fig,viz_settings,"roi_comparison_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_roi_comparison_switcher_key_v6_final")
    analysis_results['roi_comparison_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

def render_scenario_comparison_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_scenario_comp_subheader_switcher", "Szenarienvergleich – Invest/Ertrag/Bonus"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("scenario_comparison_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    base_invest_raw=analysis_results.get('total_investment_netto'); benefits_raw=analysis_results.get('annual_benefits_sim',[]); bonus_raw=analysis_results.get('one_time_bonus_eur')
    base_invest=float(base_invest_raw if isinstance(base_invest_raw,(int,float)) and base_invest_raw>0 else 10000.0)
    base_ertrag_total=sum(float(b) for b in benefits_raw if isinstance(b,(int,float)) and not math.isnan(b) and not math.isinf(b)) if isinstance(benefits_raw,list) and benefits_raw else base_invest*0.07*20
    base_bonus=float(bonus_raw if isinstance(bonus_raw,(int,float)) else 0.0)
    labels=[get_text(texts,"scenario_base_switcher","Basis"),get_text(texts,"scenario_optimistic_switcher","Optimistisch"),get_text(texts,"scenario_pessimistic_switcher","Pessimistisch")]
    invest_opts=[base_invest,base_invest*0.9,base_invest*1.1]; ertrag_opts=[base_ertrag_total,base_ertrag_total*1.15,base_ertrag_total*0.85]
    bonus_opts=[base_bonus,base_bonus+500,max(0,base_bonus-500)]
    cat_data={get_text(texts,"investment_label_switcher","Investition"):invest_opts,get_text(texts,"total_yield_label_switcher","Gesamtertrag"):ertrag_opts,get_text(texts,"bonus_subsidy_label_switcher","Bonus"):bonus_opts}
    cat_names=list(cat_data.keys())
    color_sequence = viz_settings.get("colorway", px.colors.qualitative.Plotly)
    if not color_sequence or len(color_sequence) < len(cat_names): color_sequence = px.colors.qualitative.Plotly
    
    # Chart Type Logic
    chart_type = st.session_state.get("scenario_comparison_switcher_type", "2d")
    fig=go.Figure()
    
    if chart_type == "2d":
        # 2D Grouped Bar Chart
        for i, cat_name in enumerate(cat_names):
            cat_vals = cat_data[cat_name]
            fig.add_trace(go.Bar(
                x=labels,
                y=cat_vals,
                name=cat_name,
                text=[f"{val:.0f}€" for val in cat_vals],
                textposition='outside',
                marker_color=color_sequence[i % len(color_sequence)]
            ))
        fig.update_layout(
            title=get_text(texts,"viz_scenario_comp_title_switcher","Szenarienvergleich"),
            xaxis_title='Szenario',
            yaxis_title='Betrag (€)',
            barmode='group',
            margin=dict(l=0,r=0,b=0,t=60),
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01)
        )
    else:
        # Original 3D Version
        for i,cat_name in enumerate(cat_names):
            cat_vals=cat_data[cat_name]
            for j,szenario_label in enumerate(labels):
                fig.add_trace(go.Scatter3d(x=[szenario_label,szenario_label],y=[i,i],z=[0,cat_vals[j]],mode='lines',line=dict(width=25,color=color_sequence[i%len(color_sequence)]),name=cat_name if j==0 else None,legendgroup=cat_name,showlegend=(j==0),hoverinfo='text',text=f"{szenario_label}<br>{cat_name}: {cat_vals[j]:.0f} €"))
        fig.update_layout(title=get_text(texts,"viz_scenario_comp_title_switcher","3D Szenarienvergleich"),scene=dict(xaxis_title='Szenario',yaxis_title='Kategorie',yaxis=dict(tickvals=list(range(len(cat_names))),ticktext=cat_names,range=[-0.5,len(cat_names)-0.5]),zaxis_title='Betrag (€)'),margin=dict(l=0,r=0,b=0,t=60),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    
    _apply_custom_style_to_fig(fig,viz_settings,"scenario_comparison_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_scenario_comp_switcher_key_v6_final")
    analysis_results['scenario_comparison_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_tariff_comparison_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_tariff_comp_subheader_switcher", "Vorher/Nachher – Monatliche Stromkosten"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("tariff_comparison_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    month_labels = get_text(texts,"month_names_short_list","Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels)!=12: month_labels=["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
    m_total_cons_raw=analysis_results.get('monthly_consumption_sim',[]); m_grid_draw_raw=analysis_results.get('monthly_grid_bezug_kwh',[])
    elec_price_raw=analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh')
    m_total_cons=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in m_total_cons_raw]
    m_grid_draw=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in m_grid_draw_raw]
    elec_price=float(elec_price_raw if isinstance(elec_price_raw,(int,float)) and not math.isnan(elec_price_raw) and not math.isinf(elec_price_raw) else 0.30)
    if not (len(m_total_cons)==12 and len(m_grid_draw)==12):
        st.info(get_text(texts,"viz_data_insufficient_tariff_comp","Daten für Vorher/Nachher-Stromkosten unvollständig.")); analysis_results['tariff_comparison_switcher_chart_bytes']=None; return
    kosten_vorher=[(c or 0)*elec_price for c in m_total_cons]; kosten_nachher=[(g or 0)*elec_price for g in m_grid_draw]
    
    # Chart Type Logic
    chart_type = st.session_state.get("tariff_comparison_switcher_type", "2d")
    fig=go.Figure()
    color_vorher = viz_settings.get("secondary_chart_color", "#ff7f0e")
    color_nachher = viz_settings.get("primary_chart_color", "#1f77b4")
    
    if chart_type == "2d":
        # 2D Grouped Bar Chart
        fig.add_trace(go.Bar(
            x=month_labels,
            y=kosten_vorher,
            name='Kosten Vorher (ohne PV)',
            text=[f"{cost:.2f}€" for cost in kosten_vorher],
            textposition='outside',
            marker_color=color_vorher
        ))
        fig.add_trace(go.Bar(
            x=month_labels,
            y=kosten_nachher,
            name='Kosten Nachher (mit PV)',
            text=[f"{cost:.2f}€" for cost in kosten_nachher],
            textposition='outside',
            marker_color=color_nachher
        ))
        fig.update_layout(
            title=get_text(texts,"viz_tariff_comp_title_switcher","Monatliche Stromkosten: Vorher vs. Nachher (Jahr 1)"),
            xaxis_title='Monat',
            yaxis_title='Stromkosten (€)',
            barmode='group',
            margin=dict(l=0,r=0,b=0,t=60),
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01)
        )
    else:
        # Original 3D Version
        bar_width_yz=0.4
        for i,month_label in enumerate(month_labels):
            fig.add_trace(go.Scatter3d(x=[month_label,month_label],y=[0,0],z=[0,kosten_vorher[i]],mode='lines',line=dict(width=20,color=color_vorher),name='Kosten Vorher' if i==0 else None,legendgroup='Vorher',showlegend=(i==0),hoverinfo='text',text=f"{month_label} Vorher: {kosten_vorher[i]:.2f} €"))
            fig.add_trace(go.Scatter3d(x=[month_label,month_label],y=[bar_width_yz,bar_width_yz],z=[0,kosten_nachher[i]],mode='lines',line=dict(width=20,color=color_nachher),name='Kosten Nachher' if i==0 else None,legendgroup='Nachher',showlegend=(i==0),hoverinfo='text',text=f"{month_label} Nachher: {kosten_nachher[i]:.2f} €"))
        fig.update_layout(title=get_text(texts,"viz_tariff_comp_title_switcher","3D Monatliche Stromkosten: Vorher vs. Nachher"),scene=dict(xaxis_title='Monat',yaxis_title='Szenario',yaxis=dict(tickvals=[0,bar_width_yz],ticktext=['Ohne PV','Mit PV (Netzbezug)'],range=[-0.5,bar_width_yz+0.5]),zaxis_title='Stromkosten (€)'),margin=dict(l=0,r=0,b=0,t=60),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    
    _apply_custom_style_to_fig(fig,viz_settings,"tariff_comparison_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_tariff_comp_switcher_key_v6_final")
    analysis_results['tariff_comparison_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_income_projection_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_income_proj_subheader_switcher", "💸 Einnahmen/Ersparnisprognose – Dynamischer Verlauf"))
    
    # Chart Controls mit 2D/3D Switcher
    _add_chart_controls("income_projection_switcher", texts, "2d", ["2d", "3d"], viz_settings)
    
    years_effective=int(analysis_results.get('simulation_period_years_effective',0))
    if years_effective<=0: st.info(get_text(texts,"viz_data_insufficient_income_proj","Simulationsdauer 0.")); analysis_results['income_projection_switcher_chart_bytes']=None; return
    jahre_axis=np.arange(0,years_effective+1); annual_benefits_raw=analysis_results.get('annual_benefits_sim',[])
    annual_benefits=[float(b) for b in annual_benefits_raw if isinstance(b,(int,float)) and not math.isnan(b) and not math.isinf(b)]
    if not (annual_benefits and len(annual_benefits)==years_effective):
        st.info(get_text(texts,"viz_data_insufficient_income_proj_benefits",f"Daten für 'annual_benefits_sim' unvollständig.")); analysis_results['income_projection_switcher_chart_bytes']=None; return
    kum_vorteile=[0.0]+list(np.cumsum([val or 0 for val in annual_benefits]))
    
    # Chart Type Logic
    chart_type = st.session_state.get("income_projection_switcher_type", "2d")
    fig=go.Figure()
    line_color = viz_settings.get("primary_chart_color", "mediumseagreen")
    
    if chart_type == "2d":
        # 2D Line Chart
        fig.add_trace(go.Scatter(
            x=jahre_axis,
            y=kum_vorteile,
            mode='lines+markers',
            line=dict(color=line_color, width=3),
            marker=dict(size=6, color=line_color),
            name='Kumulierte Vorteile',
            text=[f"{val:.0f}€" for val in kum_vorteile],
            hovertemplate="<b>Jahr:</b> %{x}<br><b>Kumulierte Vorteile:</b> %{y:.0f} €<extra></extra>"
        ))
        fig.update_layout(
            title=get_text(texts,"viz_income_proj_title_switcher","Kumulierte Einnahmen & Ersparnisse"),
            xaxis_title='Simulationsjahr',
            yaxis_title='Kumulierte Vorteile (€)',
            margin=dict(l=0,r=0,b=0,t=50),
            showlegend=False
        )
    else:
        # Original 3D Version
        fig.add_trace(go.Scatter3d(x=jahre_axis,y=[0]*len(jahre_axis),z=kum_vorteile,mode='lines+markers',line=dict(color=line_color,width=4),marker=dict(size=4, color=line_color),name='Kumulierte Vorteile'))
        fig.update_layout(title=get_text(texts,"viz_income_proj_title_switcher","3D Kumulierte Einnahmen & Ersparnisse"),scene=dict(xaxis_title='Simulationsjahr',yaxis_title='',zaxis_title='Kumulierte Vorteile (€)'),margin=dict(l=0,r=0,b=0,t=50))
    
    _apply_custom_style_to_fig(fig,viz_settings,"income_projection_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_income_proj_switcher_key_v6_final")
    analysis_results['income_projection_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def _create_monthly_production_consumption_chart(analysis_results_local: Dict, texts_local: Dict, viz_settings: Dict[str, Any], chart_key_prefix: str) -> Optional[go.Figure]:
    monthly_prod_raw = analysis_results_local.get('monthly_productions_sim', [])
    monthly_cons_raw = analysis_results_local.get('monthly_consumption_sim', [])
    if not (isinstance(monthly_prod_raw, list) and len(monthly_prod_raw) == 12 and
            isinstance(monthly_cons_raw, list) and len(monthly_cons_raw) == 12):
        return None
    monthly_prod = [float(v) if isinstance(v, (int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in monthly_prod_raw]
    monthly_cons = [float(v) if isinstance(v, (int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in monthly_cons_raw]
    month_labels_chart = get_text(texts_local, "month_names_short_list_chart", "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels_chart) != 12: month_labels_chart = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    df_monthly = pd.DataFrame({'Monat': month_labels_chart, get_text(texts_local,'pv_production_chart_label',"PV Produktion (kWh)"): monthly_prod, get_text(texts_local,'consumption_chart_label',"Verbrauch (kWh)"): monthly_cons})
    selected_chart_type = st.session_state.get(f"{chart_key_prefix}_type", "bar")
    is_manual_color = st.session_state.get(f"color_method_is_manual_{chart_key_prefix}", False)
    dynamic_color_list = None
    if is_manual_color:
        primary = st.session_state.get(f"{chart_key_prefix}_primary_color", viz_settings.get("primary_chart_color"))
        secondary = st.session_state.get(f"{chart_key_prefix}_secondary_color", viz_settings.get("secondary_chart_color"))
        dynamic_color_list = [primary, secondary] if primary and secondary else ([primary] if primary else ([secondary] if secondary else None))
    else:
        palette_name = st.session_state.get(f"{chart_key_prefix}_color_palette", viz_settings.get("default_color_palette"))
        if palette_name != "Plotly":
            try: dynamic_color_list = getattr(px.colors.qualitative, palette_name, None)
            except AttributeError: pass
    fig = go.Figure()
    prod_label_fig = get_text(texts_local,'pv_production_chart_label',"PV Produktion (kWh)")
    cons_label_fig = get_text(texts_local,'consumption_chart_label',"Verbrauch (kWh)")
    if selected_chart_type == "bar":
        fig.add_trace(go.Bar(x=df_monthly['Monat'], y=df_monthly[prod_label_fig], name=get_text(texts_local,'pv_production_chart_label',"PV Produktion"), text=[f"{x:.0f}" for x in monthly_prod], texttemplate='%{text}', textposition='outside'))
        fig.add_trace(go.Bar(x=df_monthly['Monat'], y=df_monthly[cons_label_fig], name=get_text(texts_local,'consumption_chart_label',"Verbrauch"), text=[f"{x:.0f}" for x in monthly_cons], texttemplate='%{text}', textposition='outside'))
        fig.update_layout(barmode='group')
    elif selected_chart_type == "line":
        fig.add_trace(go.Scatter(x=df_monthly['Monat'], y=df_monthly[prod_label_fig], mode='lines+markers', name=get_text(texts_local,'pv_production_chart_label',"PV Produktion")))
        fig.add_trace(go.Scatter(x=df_monthly['Monat'], y=df_monthly[cons_label_fig], mode='lines+markers', name=get_text(texts_local,'consumption_chart_label',"Verbrauch")))
    elif selected_chart_type == "area":
        fig.add_trace(go.Scatter(x=df_monthly['Monat'], y=df_monthly[prod_label_fig], mode='lines', fill='tozeroy', name=get_text(texts_local,'pv_production_chart_label',"PV Produktion")))
        fig.add_trace(go.Scatter(x=df_monthly['Monat'], y=df_monthly[cons_label_fig], mode='lines', fill='tozeroy', name=get_text(texts_local,'consumption_chart_label',"Verbrauch")))
    fig.update_layout(title=get_text(texts_local,"chart_title_monthly_comparison","Monatlicher Vergleich: Produktion vs. Verbrauch (Jahr 1)"), xaxis_title=get_text(texts_local,"month_axis_label_chart","Monat"), yaxis_title=get_text(texts_local,"kwh_axis_label_chart","Energie (kWh)"), legend_title_text=get_text(texts_local,"legend_title_monthly_chart","Legende"))
    _apply_custom_style_to_fig(fig, viz_settings, "monthly_prod_cons_chart", dynamic_colors=dynamic_color_list)
    return fig

def _create_electricity_cost_projection_chart(analysis_results_local: Dict, texts_local: Dict, viz_settings: Dict[str, Any], chart_key_prefix: str) -> Optional[go.Figure]:
    projected_costs_raw=analysis_results_local.get('annual_costs_hochrechnung_values',[])
    sim_years_proj_raw=analysis_results_local.get('annual_costs_hochrechnung_jahre_effektiv')
    price_increase_proj_raw=analysis_results_local.get('annual_costs_hochrechnung_steigerung_effektiv_prozent')

    if not (projected_costs_raw and isinstance(projected_costs_raw, list) and
            sim_years_proj_raw and isinstance(sim_years_proj_raw, int) and sim_years_proj_raw > 0 and
            len(projected_costs_raw) == sim_years_proj_raw and
            price_increase_proj_raw is not None):
        return None

    projected_costs=[float(c) if isinstance(c,(int,float)) and not math.isnan(c) and not math.isinf(c) else 0.0 for c in projected_costs_raw]
    sim_years_proj = sim_years_proj_raw
    price_increase_proj=float(price_increase_proj_raw)

    years_axis_proj=list(range(1,sim_years_proj + 1))
    df_proj=pd.DataFrame({'Jahr':years_axis_proj, get_text(texts_local,'projected_annual_cost_label',"Jährliche Stromkosten ohne PV (€)"):projected_costs})
    title_text_proj=get_text(texts_local,"chart_title_cost_projection_with_increase","Stromkosten-Hochrechnung ohne PV (mit {steigerung}% p.a. Steigerung)").format(steigerung=f"{price_increase_proj:.1f}")

    selected_chart_type = st.session_state.get(f"{chart_key_prefix}_type", "line")
    is_manual_color = st.session_state.get(f"color_method_is_manual_{chart_key_prefix}", False)
    dynamic_color_list = None

    if is_manual_color:
        primary = st.session_state.get(f"{chart_key_prefix}_primary_color", viz_settings.get("primary_chart_color"))
        dynamic_color_list = [primary] if primary else None
    else:
        palette_name = st.session_state.get(f"{chart_key_prefix}_color_palette", viz_settings.get("default_color_palette"))
        if palette_name != "Plotly":
            try:
                dynamic_color_list = getattr(px.colors.qualitative, palette_name, None)
            except AttributeError:
                pass

    if selected_chart_type == "line":
        fig=px.line(df_proj,x='Jahr',y=get_text(texts_local,'projected_annual_cost_label',"Jährliche Stromkosten ohne PV (€)"),title=title_text_proj,markers=True)
    elif selected_chart_type == "bar":
        fig=px.bar(df_proj,x='Jahr',y=get_text(texts_local,'projected_annual_cost_label',"Jährliche Stromkosten ohne PV (€)"),title=title_text_proj,text_auto=True)
    else: # Fallback zu Linie
        fig=px.line(df_proj,x='Jahr',y=get_text(texts_local,'projected_annual_cost_label',"Jährliche Stromkosten ohne PV (€)"),title=title_text_proj,markers=True)

    fig.update_yaxes(rangemode="tozero")
    _apply_custom_style_to_fig(fig,viz_settings,"cost_projection_chart", dynamic_colors=dynamic_color_list)
    return fig

def _create_cumulative_cashflow_chart(analysis_results_local: Dict, texts_local: Dict, viz_settings: Dict[str, Any], chart_key_prefix:str) -> Optional[go.Figure]:
    cumulative_cf_raw=analysis_results_local.get('cumulative_cash_flows_sim',[])
    if not (cumulative_cf_raw and isinstance(cumulative_cf_raw, list)):
        return None
    cumulative_cf=[float(cf) if isinstance(cf,(int,float)) and not math.isnan(cf) and not math.isinf(cf) else 0.0 for cf in cumulative_cf_raw]

    years_axis_cf=list(range(len(cumulative_cf)))
    df_cf=pd.DataFrame({'Jahr':years_axis_cf,get_text(texts_local,'cumulative_cashflow_label',"Kumulierter Cashflow (€)"):cumulative_cf})

    selected_chart_type = st.session_state.get(f"{chart_key_prefix}_type", "area")
    is_manual_color = st.session_state.get(f"color_method_is_manual_{chart_key_prefix}", False)
    dynamic_color_list = None

    if is_manual_color:
        primary = st.session_state.get(f"{chart_key_prefix}_primary_color", viz_settings.get("primary_chart_color"))
        dynamic_color_list = [primary] if primary else None
    else:
        palette_name = st.session_state.get(f"{chart_key_prefix}_color_palette", viz_settings.get("default_color_palette"))
        if palette_name != "Plotly":
            try:
                dynamic_color_list = getattr(px.colors.qualitative, palette_name, None)
            except AttributeError:
                pass

    if selected_chart_type == "area":
        fig=px.area(df_cf,x='Jahr',y=get_text(texts_local,'cumulative_cashflow_label',"Kumulierter Cashflow (€)"),title=get_text(texts_local,"chart_title_cumulative_cashflow","Kumulierter Cashflow über die Laufzeit (2D)"),markers=True)
    elif selected_chart_type == "line":
        fig=px.line(df_cf,x='Jahr',y=get_text(texts_local,'cumulative_cashflow_label',"Kumulierter Cashflow (€)"),title=get_text(texts_local,"chart_title_cumulative_cashflow","Kumulierter Cashflow über die Laufzeit (2D)"),markers=True)
    elif selected_chart_type == "bar":
        fig=px.bar(df_cf,x='Jahr',y=get_text(texts_local,'cumulative_cashflow_label',"Kumulierter Cashflow (€)"),title=get_text(texts_local,"chart_title_cumulative_cashflow","Kumulierter Cashflow über die Laufzeit (2D)"),text_auto=True)
    else: # Fallback
        fig=px.area(df_cf,x='Jahr',y=get_text(texts_local,'cumulative_cashflow_label',"Kumulierter Cashflow (€)"),title=get_text(texts_local,"chart_title_cumulative_cashflow","Kumulierter Cashflow über die Laufzeit (2D)"),markers=True)

    fig.add_hline(y=0,line_dash="dash",line_color="red")
    fig.update_yaxes(rangemode="normal")
    _apply_custom_style_to_fig(fig,viz_settings,"cumulative_cashflow_chart", dynamic_colors=dynamic_color_list)
    return fig

def _render_consumption_coverage_pie(analysis_results_local: Dict, texts_local: Dict, viz_settings: Dict[str, Any], chart_key_prefix: str) -> None:
    st.subheader(get_text(texts_local, "self_consumption_grid_header", "Eigenverbrauch & Netzbezug (Jahr 1)"))
    _add_chart_controls(chart_key_prefix, texts_local, "pie", ["pie"], viz_settings)

    total_cons_raw=analysis_results_local.get('total_consumption_kwh_yr')
    self_supply_val_raw=analysis_results_local.get('self_supply_rate_percent')
    if total_cons_raw is None or self_supply_val_raw is None:
        st.info(get_text(texts_local,"no_data_for_consumption_pie_chart","Daten für Verbrauchsdeckungsdiagramm nicht verfügbar."))
        analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = None
        return

    total_cons=float(total_cons_raw) if isinstance(total_cons_raw,(int,float)) and total_cons_raw > 0 and not math.isnan(total_cons_raw) and not math.isinf(total_cons_raw) else 0.0
    self_supply_float=float(self_supply_val_raw) if isinstance(self_supply_val_raw,(int,float)) and not math.isnan(self_supply_val_raw) and not math.isinf(self_supply_val_raw) else 0.0
    grid_cons_float=max(0.0, 100.0 - self_supply_float)

    is_manual_color = st.session_state.get(f"color_method_is_manual_{chart_key_prefix}", False)
    dynamic_color_list = None
    if is_manual_color:
        primary = st.session_state.get(f"{chart_key_prefix}_primary_color", viz_settings.get("primary_chart_color"))
        secondary = st.session_state.get(f"{chart_key_prefix}_secondary_color", viz_settings.get("secondary_chart_color"))
        dynamic_color_list = [primary, secondary] if primary and secondary else ([primary] if primary else ([secondary] if secondary else None))
    else:
        palette_name = st.session_state.get(f"{chart_key_prefix}_color_palette", viz_settings.get("default_color_palette"))
        if palette_name != "Plotly":
            try: dynamic_color_list = getattr(px.colors.qualitative, palette_name, None)
            except AttributeError: pass
    if not dynamic_color_list:
        default_color_1 = viz_settings.get("consumption_coverage_chart", {}).get("color_self_supply", viz_settings.get("primary_chart_color","green"))
        default_color_2 = viz_settings.get("consumption_coverage_chart", {}).get("color_grid_draw", viz_settings.get("secondary_chart_color","red"))
        dynamic_color_list = [default_color_1, default_color_2]

    if total_cons > 0:
        df_pie_data = {
            'Kategorie': [
                get_text(texts_local,'self_supply_rate_pie_label',"Eigenversorgung"),
                get_text(texts_local,'grid_consumption_rate_pie_label',"Netzbezug")
            ],
            'Anteil (%)': [self_supply_float, grid_cons_float]
        }
        df_pie=pd.DataFrame(df_pie_data)
        df_pie=df_pie[df_pie['Anteil (%)'] >= 0.01]

        if not df_pie.empty:
            fig=px.pie(df_pie,values='Anteil (%)',names='Kategorie',
                       title=get_text(texts_local,"pie_chart_consumption_coverage_title","Deckung Gesamtverbrauch"),
                       hole=0.3,color_discrete_sequence=dynamic_color_list)
            _apply_custom_style_to_fig(fig,viz_settings,"consumption_coverage_chart")
            st.plotly_chart(fig,use_container_width=True,key=f"{chart_key_prefix}_final_pie_chart_key_v7_corrected")
            analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = _export_plotly_fig_to_bytes(fig,texts_local)
        else:
            st.info(get_text(texts_local,"no_data_for_consumption_pie_chart_filtered","Keine signifikanten Anteile für Verbrauchsdeckungsdiagramm."))
            analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = None
    else:
        st.info(get_text(texts_local,"no_data_for_consumption_pie_chart","Keine Daten für Verbrauchsdeckungsdiagramm (Gesamtverbrauch ist 0)."))
        analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = None

def _render_pv_usage_pie(analysis_results_local: Dict, texts_local: Dict, viz_settings: Dict[str, Any], chart_key_prefix: str) -> None:
    st.subheader(get_text(texts_local,"pv_usage_header","Nutzung des PV-Stroms (Jahr 1)"))
    _add_chart_controls(chart_key_prefix, texts_local, "pie", ["pie"], viz_settings)

    direct_cons_prod_perc_raw=analysis_results_local.get('direktverbrauch_anteil_pv_produktion_pct')
    storage_cons_prod_perc_raw=analysis_results_local.get('speichernutzung_anteil_pv_produktion_pct')
    annual_pv_prod_kwh_val_raw=analysis_results_local.get('annual_pv_production_kwh')

    if direct_cons_prod_perc_raw is None or storage_cons_prod_perc_raw is None or annual_pv_prod_kwh_val_raw is None:
        st.info(get_text(texts_local,"no_data_for_pv_usage_pie_chart","Daten für PV-Nutzungsdiagramm nicht verfügbar."))
        analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = None
        return

    direct_cons_float=float(direct_cons_prod_perc_raw) if isinstance(direct_cons_prod_perc_raw,(int,float)) and not math.isnan(direct_cons_prod_perc_raw) and not math.isinf(direct_cons_prod_perc_raw) else 0.0
    storage_cons_float=float(storage_cons_prod_perc_raw) if isinstance(storage_cons_prod_perc_raw,(int,float)) and not math.isnan(storage_cons_prod_perc_raw) and not math.isinf(storage_cons_prod_perc_raw) else 0.0
    annual_pv_prod_kwh_val=float(annual_pv_prod_kwh_val_raw) if isinstance(annual_pv_prod_kwh_val_raw,(int,float)) and annual_pv_prod_kwh_val_raw > 0 and not math.isnan(annual_pv_prod_kwh_val_raw) and not math.isinf(annual_pv_prod_kwh_val_raw) else 0.0

    is_manual_color = st.session_state.get(f"color_method_is_manual_{chart_key_prefix}", False)
    dynamic_color_list = None
    if is_manual_color:
        c1 = st.session_state.get(f"{chart_key_prefix}_primary_color", viz_settings.get("primary_chart_color"))
        c2 = st.session_state.get(f"{chart_key_prefix}_secondary_color", viz_settings.get("secondary_chart_color"))
        c3 = st.session_state.get(f"{chart_key_prefix}_tertiary_color", "#cccccc")
        dynamic_color_list = [color for color in [c1, c2, c3] if color]
    else:
        palette_name = st.session_state.get(f"{chart_key_prefix}_color_palette", viz_settings.get("default_color_palette"))
        if palette_name != "Plotly":
            try:
                dynamic_color_list = getattr(px.colors.qualitative, palette_name, None)
            except AttributeError:
                pass

    if not dynamic_color_list or len(dynamic_color_list) < 3:
        default_color_direct = viz_settings.get("pv_usage_chart", {}).get("color_direct_use", viz_settings.get("primary_chart_color","blue"))
        default_color_storage = viz_settings.get("pv_usage_chart", {}).get("color_storage_use", viz_settings.get("secondary_chart_color","orange"))
        default_color_feed_in = viz_settings.get("pv_usage_chart", {}).get("color_feed_in", "#dddddd")
        dynamic_color_list = [default_color_direct, default_color_storage, default_color_feed_in]

    if annual_pv_prod_kwh_val > 0:
        feed_in_prod_perc=max(0.0,100.0 - direct_cons_float - storage_cons_float)
        pie_labels_pv=[
            get_text(texts_local,'direct_consumption_pie_label',"Direktverbrauch"),
            get_text(texts_local,'storage_usage_pie_label',"Speichernutzung"),
            get_text(texts_local,'feed_in_pie_label',"Einspeisung")
        ]
        pie_values_pv=[direct_cons_float,storage_cons_float,feed_in_prod_perc]
        df_pie_data = {'Nutzungsart': pie_labels_pv, 'Anteil an PV-Produktion (%)': pie_values_pv}
        df_pie_pv=pd.DataFrame(df_pie_data)
        df_pie_pv=df_pie_pv[df_pie_pv['Anteil an PV-Produktion (%)'] >= 0.01]

        if not df_pie_pv.empty:
            fig=px.pie(df_pie_pv,values='Anteil an PV-Produktion (%)',names='Nutzungsart',
                       title=get_text(texts_local,"pie_chart_pv_usage_title","Aufteilung PV-Produktion"),
                       hole=0.3,color_discrete_sequence=dynamic_color_list)
            _apply_custom_style_to_fig(fig,viz_settings,"pv_usage_chart")
            st.plotly_chart(fig,use_container_width=True,key=f"{chart_key_prefix}_final_pie_chart_key_v7_corrected")
            analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = _export_plotly_fig_to_bytes(fig,texts_local)
        else:
            st.info(get_text(texts_local,"no_data_for_pv_usage_pie_chart_filtered","Keine signifikanten Anteile für PV-Nutzungsdiagramm."))
            analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = None
    else:
        st.info(get_text(texts_local,"no_data_for_pv_usage_pie_chart_prod_zero","Keine PV-Produktion für Nutzungsdiagramm vorhanden."))
        analysis_results_local[f'{chart_key_prefix}_chart_bytes'] = None

def get_pricing_modifications_data():
    """
    Gibt die aktuellen Preisänderungsdaten und Berechnungen zurück.
    Diese Funktion kann von anderen Modulen (z.B. PDF-Generierung) verwendet werden.
    """
    live_calc = st.session_state.get('live_pricing_calculations', {})
    discount_percent = st.session_state.get('pricing_modifications_discount_slider', 0.0)
    rebates_eur = st.session_state.get('pricing_modifications_rebates_slider', 0.0)
    surcharge_percent = st.session_state.get('pricing_modifications_surcharge_slider', 0.0)
    special_costs_eur = st.session_state.get('pricing_modifications_special_costs_slider', 0.0)
    miscellaneous_eur = st.session_state.get('pricing_modifications_miscellaneous_slider', 0.0)
    descriptions = {
        'discount': st.session_state.get('pricing_modifications_descriptions_discount_text', ''),
        'rebates': st.session_state.get('pricing_modifications_descriptions_rebates_text', ''),
        'surcharge': st.session_state.get('pricing_modifications_descriptions_surcharge_text', ''),
        'special_costs': st.session_state.get('pricing_modifications_descriptions_special_costs_text_unique', ''),
        'miscellaneous': st.session_state.get('pricing_modifications_descriptions_miscellaneous_text', ''),
        'special_agreements': st.session_state.get('pricing_modifications_special_agreements_text', '')
    }
    return {
        'values': {
            'discount_percent': discount_percent, 'rebates_eur': rebates_eur,
            'surcharge_percent': surcharge_percent, 'special_costs_eur': special_costs_eur,
            'miscellaneous_eur': miscellaneous_eur
        },
        'descriptions': descriptions, 'calculations': live_calc,
        'has_modifications': any([
            discount_percent > 0, rebates_eur > 0, surcharge_percent > 0,
            special_costs_eur > 0, miscellaneous_eur > 0,
            any(descriptions.values())
        ])
    }

def integrate_advanced_calculations(texts: Dict[str, str]):
    """Haupt-Integration der erweiterten Berechnungen"""
    
    # Integrator initialisieren
    if 'calculations_integrator' not in st.session_state:
        st.session_state.calculations_integrator = AdvancedCalculationsIntegrator()
    
    integrator = st.session_state.calculations_integrator
    
    # System-Daten aus Session State holen
    calculation_results = st.session_state.get('calculation_results', {})
    project_data = st.session_state.get('project_data', {})
    
    if not calculation_results:
        st.warning("Keine Berechnungsergebnisse verfügbar. Bitte führen Sie zuerst die Basis-Berechnungen durch.")
        return
    
    # Erweiterte Berechnungen durchführen
    st.header("Erweiterte Berechnungs-Module")
    
    # Tabs für verschiedene Berechnungskategorien
    tabs = st.tabs([
        "Erweiterte Wirtschaftlichkeit",
        "Detaillierte Energieanalyse", 
        "Technische Berechnungen",
        "Finanzielle Szenarien",
        "Umwelt & Nachhaltigkeit",
        "Optimierungsvorschläge"
    ])
    
    with tabs[0]:  # Erweiterte Wirtschaftlichkeit
        render_advanced_economics(integrator, calculation_results, project_data, texts)
    
    with tabs[1]:  # Detaillierte Energieanalyse
        render_detailed_energy_analysis(integrator, calculation_results, project_data, texts)
    
    with tabs[2]:  # Technische Berechnungen
        render_technical_calculations(integrator, calculation_results, project_data, texts)
    
    with tabs[3]:  # Finanzielle Szenarien
        render_financial_scenarios(integrator, calculation_results, project_data, texts)
    
    with tabs[4]:  # Umwelt & Nachhaltigkeit
        render_environmental_calculations(integrator, calculation_results, project_data, texts)
    
    with tabs[5]:  # Optimierungsvorschläge
        render_optimization_suggestions(integrator, calculation_results, project_data, texts)

def render_advanced_economics(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Erweiterte Wirtschaftlichkeitsberechnungen"""
    st.subheader("Erweiterte Wirtschaftlichkeitsanalyse")
    
    # LCOE (Levelized Cost of Energy) Berechnung
    with st.expander("LCOE - Stromgestehungskosten", expanded=True):
        lcoe_params = {
            'investment': calc_results.get('total_investment_netto', 20000),
            'annual_production': calc_results.get('annual_pv_production_kwh', 10000),
            'lifetime': 25,
            'discount_rate': 0.04,
            'opex_rate': 0.01,
            'degradation_rate': 0.005
        }
        
        lcoe_result = integrator.calculate_lcoe_advanced(lcoe_params)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "LCOE (Standard)",
                f"{lcoe_result['lcoe_simple']:.3f} €/kWh",
                help="Einfache Stromgestehungskosten"
            )
        with col2:
            st.metric(
                "LCOE (Diskontiert)",
                f"{lcoe_result['lcoe_discounted']:.3f} €/kWh",
                help="Mit Diskontierung und Degradation"
            )
        with col3:
            st.metric(
                "Vergleich Netzstrom",
                f"{(lcoe_result['grid_comparison'] - 1) * 100:.1f}%",
                delta=f"{lcoe_result['savings_potential']:.2f} €/kWh",
                help="Ersparnis gegenüber Netzstrom"
            )
        
        # LCOE-Entwicklung visualisieren
        years = list(range(1, 26))
        lcoe_evolution = lcoe_result['yearly_lcoe']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years,
            y=lcoe_evolution,
            mode='lines+markers',
            name='LCOE',
            line=dict(color='#1E3A8A', width=3)
        ))
        
        # Netzstrompreis als Referenz
            mode='lines',
            name='Netzstrompreis',
            line=dict(color='#DC2626', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="LCOE-Entwicklung über Anlagenlebensdauer",
            xaxis_title="Jahr",
            yaxis_title="Kosten (€/kWh)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # NPV mit verschiedenen Diskontierungsraten
    with st.expander("NPV-Sensitivitätsanalyse", expanded=True):
        discount_rates = np.arange(0.01, 0.10, 0.01)
        npv_values = []
        
        for rate in discount_rates:
            npv = integrator.calculate_npv_sensitivity(calc_results, rate)
            npv_values.append(npv)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=discount_rates * 100,
            y=npv_values,
            mode='lines+markers',
            fill='tozeroy',
            name='NPV',
            line=dict(color='#10B981', width=3)
        ))
        
        # Break-even Linie
        fig.add_hline(y=0, line_dash="dash", line_color="red", 
                     annotation_text="Break-even")
        
        fig.update_layout(
            title="NPV-Sensitivität gegenüber Diskontierungsrate",
            xaxis_title="Diskontierungsrate (%)",
            yaxis_title="Net Present Value (€)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Optimaler Diskontierungssatz
        optimal_rate_idx = np.argmax(npv_values)
        st.info(f
        **Analyse-Ergebnisse:**
        # Optimaler Diskontierungssatz
        optimal_rate_idx = np.argmax(npv_values)
        st.info(f
       # **Analyse-Ergebnisse:**
     #   - Optimaler Diskontierungssatz: 
        {discount_rates[optimal_rate_idx]*100:.1f}%
      #  - Maximaler NPV: 
        {npv_values[optimal_rate_idx]:,.0f} €
       # - NPV bei 4% Diskontierung: 
        {npv_values[3]:,.0f} €
        )
    
    # IRR (Internal Rate of Return) Berechnung
    with st.expander("Renditeberechnung (IRR & MIRR)", expanded=True):
        irr_result = integrator.calculate_irr_advanced(calc_results)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "IRR (Internal Rate of Return)",
                f"{irr_result['irr']:.1f}%",
                help="Interner Zinsfuß"
            )
        with col2:
            st.metric(
                "MIRR (Modified IRR)",
                f"{irr_result['mirr']:.1f}%",
                help="Modifizierter interner Zinsfuß"
            )
        with col3:
            st.metric(
                "Profitability Index",
                f"{irr_result['profitability_index']:.2f}",
                help="Rentabilitätsindex (>1 = profitabel)"
            )

def render_detailed_energy_analysis(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Detaillierte Energieanalyse"""
    st.subheader("Detaillierte Energieflussanalyse")
    
    # Energiefluss-Sankey-Diagramm
    with st.expander("Energiefluss-Visualisierung", expanded=True):
        energy_flows = integrator.calculate_detailed_energy_flows(calc_results)
        
        # Sankey-Diagramm erstellen
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[
                    "PV-Erzeugung",
                    "Direktverbrauch",
                    "Batterieladung",
                    "Netzeinspeisung",
                    "Batterieentladung",
                    "Netzbezug",
                    "Hausverbrauch",
                    "Verluste"
                ],
                color=[
                    "#F59E0B",  # PV-Erzeugung
                    "#10B981",  # Direktverbrauch
                    "#3B82F6",  # Batterieladung
                    "#6366F1",  # Netzeinspeisung
                    "#8B5CF6",  # Batterieentladung
                    "#EF4444",  # Netzbezug
                    "#6B7280",  # Hausverbrauch
                    "#DC2626"   # Verluste
                ]
            ),
            link=dict(
                source=energy_flows['sources'],
                target=energy_flows['targets'],
                value=energy_flows['values'],
                color=energy_flows['colors']
            )
        )])
        
        fig.update_layout(
            title="Detaillierter Energiefluss (Jahreswerte)",
            xaxis_title="Tagesstunde",
            yaxis_title="Monat",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Energiebilanz-Tabelle
        st.markdown("### Energiebilanz")
        
        energy_balance = pd.DataFrame({
            'Energiefluss': energy_flows['flow_names'],
            'Menge (kWh)': energy_flows['flow_values'],
            'Anteil (%)': energy_flows['flow_percentages']
        })
        
        st.dataframe(
            energy_balance.style.format({
                'Menge (kWh)': '{:,.0f}',
                'Anteil (%)': '{:.1f}%'
            }),
            use_container_width=True
        )
    
    # Lastprofilanalyse
    with st.expander("Lastprofilanalyse", expanded=True):
        load_profile = integrator.calculate_load_profile_analysis(calc_results, project_data)
        
        # Tageslastgang visualisieren
        hours = list(range(24))
        
        fig = go.Figure()
        
        # Verbrauchslast
        fig.add_trace(go.Scatter(
            x=hours,
            y=load_profile['consumption_profile'],
            mode='lines',
            name='Verbrauch',
            fill='tozeroy',
            line=dict(color='#EF4444', width=2)
        ))
        
        # PV-Erzeugung
        fig.add_trace(go.Scatter(
            x=hours,
            y=load_profile['pv_generation_profile'],
            mode='lines',
            name='PV-Erzeugung',
            fill='tozeroy',
            line=dict(color='#F59E0B', width=2)
        ))
        
        # Batterieladung/-entladung
        fig.add_trace(go.Bar(
            x=hours,
            y=load_profile['battery_profile'],
            name='Batterie',
            marker_color=np.where(np.array(load_profile['battery_profile']) > 0, '#10B981', '#3B82F6')
        ))
        
        fig.update_layout(
            title="Typischer Tageslastgang",
            xaxis_title="Stunde",
            yaxis_title="Leistung (kW)",
            hovermode='x unified',
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Kennzahlen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Spitzenlast",
                f"{load_profile['peak_load']:.1f} kW",
                help="Maximale Verbrauchsleistung"
            )
        with col2:
            st.metric(
                "Gleichzeitigkeitsfaktor",
                f"{load_profile['simultaneity_factor']:.2f}",
                help="Verhältnis Spitzenlast zu installierter Leistung"
            )
        with col3:
            st.metric(
                "Lastdeckungsgrad",
                f"{load_profile['load_coverage']:.1f}%",
                help="Anteil der durch PV gedeckten Last"
            )
        with col4:
            st.metric(
                "Netzbelastung reduziert um",
                f"{load_profile['grid_relief']:.1f}%",
                help="Reduktion der Netzbelastung"
            )
    
    # Wechselrichter-Effizienz
    with st.expander("Wechselrichter-Effizienzanalyse", expanded=True):
        inverter_analysis = integrator.calculate_inverter_efficiency(calc_results, project_data)
        
        # Effizienzkurve
        load_percentages = list(range(0, 101, 5))
        
        fig = go.Figure()
        
        # Europäischer Wirkungsgrad
        fig.add_trace(go.Scatter(
            x=load_percentages,
            y=inverter_analysis['efficiency_curve'],
            mode='lines+markers',
            name='Wirkungsgrad',
            line=dict(color='#10B981', width=3)
        ))
        
        # Betriebspunkte markieren
        fig.add_trace(go.Scatter(
            x=inverter_analysis['operating_points'],
            y=inverter_analysis['operating_efficiencies'],
            mode='markers',
            name='Häufige Betriebspunkte',
            marker=dict(size=10, color='#EF4444')
        ))
        
        fig.update_layout(
            title="Wechselrichter-Wirkungsgradkurve",
            xaxis_title="Auslastung (%)",
            yaxis_title="Wirkungsgrad (%)",
            yaxis=dict(range=[90, 100]),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Kennzahlen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Euro-Wirkungsgrad",
                f"{inverter_analysis['euro_efficiency']:.1f}%",
                help="Gewichteter Wirkungsgrad"
            )
        with col2:
            st.metric(
                "CEC-Wirkungsgrad",
                f"{inverter_analysis['cec_efficiency']:.1f}%",
                help="California Energy Commission Standard"
            )
        with col3:
            st.metric(
                "Verluste",
                f"{inverter_analysis['annual_losses']:.0f} kWh",
                delta=f"-{inverter_analysis['loss_percentage']:.1f}%"
            )
        with col4:
            st.metric(
                "Dimensionierung",
                f"{inverter_analysis['sizing_factor']:.0f}%",
                help="DC/AC Verhältnis"
            )

def render_optimization_suggestions(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Optimierungsvorschläge für das PV-System"""
    st.subheader("Optimierungsvorschläge")
    
    # Simuliere Optimierungsanalyse
    optimization_results = integrator.generate_optimization_suggestions(calc_results, project_data)
    
    # Quick Wins
    with st.expander("Sofort umsetzbare Verbesserungen", expanded=True):
        quick_wins = [
            {
                'title': 'Optimierung der Ausrichtung',
                'description': 'Feinabstimmung der Modulausrichtung für maximalen Ertrag',
                'potential': '+3-5% Ertrag',
                'cost': 'Gering',
                'effort': 'Niedrig'
            },
            {
                'title': 'Verschattungsoptimierung',
                'description': 'Beseitigung oder Minimierung von Verschattungsquellen',
                'potential': '+2-8% Ertrag',
                'cost': 'Variabel',
                'effort': 'Mittel'
            },
            {
                'title': 'Batteriemanagement-Optimierung',
                'description': 'Anpassung der Lade-/Entladezyklen',
                'potential': '+10-15% Eigenverbrauch',
                'cost': 'Keine',
                'effort': 'Niedrig'
            }
        ]
        
        for i, win in enumerate(quick_wins, 1):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"**{i}. {win['title']}**")
                    st.caption(win['description'])
                
                with col2:
                    st.metric("Potenzial", win['potential'])
                
                with col3:
                    st.metric("Aufwand", f"{win['effort']} / {win['cost']}")
                
                if i < len(quick_wins):
                    st.markdown("---")
    
    # Langfristige Optimierungen
    with st.expander("Langfristige Optimierungen", expanded=False):
        long_term = [
            {
                'title': 'Systemerweiterung',
                'description': 'Ausbau der PV-Anlage oder Batteriekapazität',
                'investment': '5.000-15.000 €',
                'roi': '8-12 Jahre'
            },
            {
                'title': 'Smart-Home Integration',
                'description': 'Intelligente Verbrauchssteuerung',
                'investment': '1.000-3.000 €',
                'roi': '3-5 Jahre'
            },
            {
                'title': 'E-Mobilität Integration',
                'description': 'Wallbox für Elektrofahrzeuge',
                'investment': '800-2.500 €',
                'roi': '4-7 Jahre'
            }
        ]
        
        for opt in long_term:
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"**{opt['title']}**")
                st.caption(opt['description'])
            
            with col2:
                st.metric("Investition", opt['investment'])
            
            with col3:
                st.metric("ROI", opt['roi'])

def render_financial_scenarios(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Finanzielle Szenarien"""
    st.subheader("Finanzielle Szenarioanalyse")
    
    # Monte-Carlo-Simulation
    with st.expander("Monte-Carlo-Risikoanalyse", expanded=True):
        # Simulationsparameter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            n_simulations = st.number_input(
                "Anzahl Simulationen",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100
            )
        
        with col2:
            confidence_level = st.slider(
                "Konfidenzintervall (%)",
                min_value=80,
                max_value=99,
                value=95
            )
        
        with col3:
            if st.button("Simulation starten"):
                with st.spinner("Führe Monte-Carlo-Simulation durch..."):
                    mc_results = integrator.run_monte_carlo_simulation(
                        calc_results, 
                        n_simulations,
                        confidence_level
                    )
                    st.session_state['mc_results'] = mc_results
        
        # Ergebnisse anzeigen
        if 'mc_results' in st.session_state:
            mc_results = st.session_state['mc_results']
            
            # NPV-Verteilung
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=mc_results['npv_distribution'],
                nbinsx=50,
                name='NPV-Verteilung',
                marker_color='#3B82F6',
                opacity=0.7
            ))
            
            # Konfidenzintervall markieren
            fig.add_vline(x=mc_results['npv_lower_bound'], 
                         line_dash="dash", line_color="red",
                         annotation_text=f"{(100-confidence_level)/2}%")
            fig.add_vline(x=mc_results['npv_upper_bound'], 
                         line_dash="dash", line_color="red",
                         annotation_text=f"{100-(100-confidence_level)/2}%")
            fig.add_vline(x=mc_results['npv_mean'], 
                         line_dash="solid", line_color="green",
                         annotation_text="Erwartungswert")
            
            fig.update_layout(
                title="NPV-Verteilung (Monte-Carlo-Simulation)",
                xaxis_title="Net Present Value (€)",
                yaxis_title="Häufigkeit",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Risikokennzahlen
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Erwarteter NPV",
                    format_kpi_value(mc_results['npv_mean'], "€", texts_dict={}, precision=0),
                    delta=f"σ = {mc_results['npv_std']:,.0f} €"
                )
            with col2:
                st.metric(
                    "Value at Risk (5%)",
                    format_kpi_value(mc_results['var_5'], "€", texts_dict={}, precision=0),
                    help="5% Wahrscheinlichkeit für schlechteren Wert"
                )
            with col3:
                st.metric(
                    "Erfolgswahrscheinlichkeit",
                    f"{mc_results['success_probability']:.1f}%",
                    help="Wahrscheinlichkeit für positiven NPV"
                )
            with col4:
                st.metric(
                    f"{confidence_level}% Konfidenzintervall",
                    f"{mc_results['npv_lower_bound']:,.0f} - {mc_results['npv_upper_bound']:,.0f} €"
                )
            
            # Sensitivitätsanalyse
            st.markdown("### Sensitivitätsanalyse")
            
            sensitivity_df = pd.DataFrame(mc_results['sensitivity_analysis'])
            
            fig = px.bar(
                sensitivity_df,
                x='impact',
                y='parameter',
                orientation='h',
                color='impact',
                color_continuous_scale='RdBu_r',
                title="Einfluss der Parameter auf NPV"
            )
            
            fig.update_layout(
                xaxis_title="Relativer Einfluss auf NPV",
                yaxis_title="Parameter"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Förderszenarien
    with st.expander("Förderszenarien", expanded=True):
        subsidy_scenarios = integrator.calculate_subsidy_scenarios(calc_results)
        
        # Szenario-Vergleich
        scenarios_df = pd.DataFrame(subsidy_scenarios['scenarios'])
        
        fig = go.Figure()
        
        for scenario in scenarios_df.columns[1:]:  # Skip 'Jahr' column
            fig.add_trace(go.Scatter(
                x=scenarios_df['Jahr'],
                y=scenarios_df[scenario],
                mode='lines+markers',
                name=scenario,
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title="Kumulierter Cashflow - Förderszenarien",
            xaxis_title="Jahr",
            yaxis_title="Kumulierter Cashflow (€)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Szenario-Vergleich Tabelle
        comparison_df = pd.DataFrame(subsidy_scenarios['comparison'])
        
        st.dataframe(
            comparison_df.style.format({
                'NPV': '{:,.0f} €',
                'IRR': '{:.1f}%',
                'Amortisation': '{:.1f} Jahre',
                'Förderung': '{:,.0f} €'
            }).background_gradient(subset=['NPV'], cmap='Greens'),
            use_container_width=True
        )

def render_analysis(texts: Dict[str, str], results: Optional[Dict[str, Any]] = None) -> None:
    """Hauptfunktion für das Analyse-Dashboard"""
    if not _ANALYSIS_DEPENDENCIES_AVAILABLE:
        st.error(get_text(texts,"analysis_module_critical_error", "Kritischer Fehler: Analyse-Modul-Abhängigkeiten nicht verfügbar"))
        return
    
    st.header(get_text(texts,"dashboard_header","Ergebnisse und Dashboard"))
    project_inputs = st.session_state.get("project_data", {})
    viz_settings = _get_visualization_settings()

    # Seitenleiste für Analyse-Parameter
    st.sidebar.subheader(get_text(texts, "analysis_interactive_settings_header", "Analyse-Parameter"))
    admin_defaults_gc = load_admin_setting('global_constants', {'simulation_period_years': 20, 'electricity_price_increase_annual_percent': 3.0})
    admin_default_sim_years = int(admin_defaults_gc.get('simulation_period_years', 20) or 20)
    admin_default_price_increase = float(admin_defaults_gc.get('electricity_price_increase_annual_percent', 3.0) or 3.0)
    
    current_sim_years_for_ui = admin_default_sim_years
    current_price_increase_for_ui = admin_default_price_increase
    
    # Aktuelle Berechnungsergebnisse verwenden, falls vorhanden
    previous_calc_results = st.session_state.get("calculation_results", {})
    if results and isinstance(results, dict) and results.get('simulation_period_years_effective') is not None:
        current_sim_years_for_ui = int(results['simulation_period_years_effective'])
        current_price_increase_for_ui = float(results.get('electricity_price_increase_rate_effective_percent', admin_default_price_increase))
    elif previous_calc_results and previous_calc_results.get('simulation_period_years_effective') is not None:
        current_sim_years_for_ui = int(previous_calc_results['simulation_period_years_effective'])
        current_price_increase_for_ui = float(previous_calc_results.get('electricity_price_increase_rate_effective_percent', admin_default_price_increase))
    
    # UI-Eingabefelder
    sim_duration_user_input = st.sidebar.number_input(
        get_text(texts,"analysis_sim_duration_label","Simulationsdauer (Jahre)"),
        min_value=1, max_value=50, value=current_sim_years_for_ui, step=1,
        key="analysis_sim_duration_input_v22_final_corrected"
    )
    sim_price_increase_user_input = st.sidebar.number_input(
        get_text(texts,"analysis_sim_price_increase_label","Strompreissteigerung p.a. (%)"),
        min_value=0.0, max_value=20.0, value=current_price_increase_for_ui, step=0.1, format="%.1f",
        key="analysis_price_increase_input_v22_final_corrected"
    )

    st.markdown("---")
    render_pricing_modifications_ui()
    st.markdown("---")

    # Berechnungslogik
    if st.button(get_text(texts,"analysis_calculate_button","Berechnung aktualisieren"), type="primary"):
        with st.spinner(get_text(texts,"analysis_calculating_status","Führe Berechnungen durch...")):
            errors_list = []
            results_for_display = perform_calculations(
                project_inputs,
                texts=texts,
                errors_list=errors_list,
                simulation_duration_user=sim_duration_user_input,
                electricity_price_increase_user=sim_price_increase_user_input
            )
            
            if errors_list:
                for error in errors_list:
                    st.error(error)
            
            if results_for_display and isinstance(results_for_display, dict):
                st.session_state['calculation_results'] = results_for_display
                st.success(get_text(texts,"analysis_calculation_complete","Berechnungen abgeschlossen"))
                st.rerun()
            else:
                st.error(get_text(texts,"analysis_calculation_failed","Berechnungen fehlgeschlagen"))

def render_environmental_calculations(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Umwelt- und Nachhaltigkeitsberechnungen"""
    st.subheader("Umwelt & Nachhaltigkeit")
    
    # CO2-Bilanz
    with st.expander("Detaillierte CO₂-Bilanz", expanded=True):
        co2_analysis = integrator.calculate_detailed_co2_analysis(calc_results)
        
        # CO2-Bilanz über Lebenszyklus
        fig = go.Figure()
        
        # Kumulative CO2-Einsparung
        fig.add_trace(go.Scatter(
            x=co2_analysis['years'],
            y=co2_analysis['cumulative_savings'],
            mode='lines',
            name='Kumulative CO₂-Einsparung',
            fill='tozeroy',
            line=dict(color='#10B981', width=3)
        ))
        
        # CO2-Rückzahlung (Herstellung)
        fig.add_hline(
            y=co2_analysis['production_emissions'],
            line_dash="dash",
            line_color="red",
            annotation_text="CO₂ aus Herstellung"
        )
        
        # Energy Payback Time
        fig.add_vline(
            x=co2_analysis['carbon_payback_time'],
            line_dash="dot",
            line_color="blue",
            annotation_text=f"CO₂-Amortisation: {co2_analysis['carbon_payback_time']:.1f} Jahre"
        )
        
        fig.update_layout(
            title="CO₂-Bilanz über Anlagenlebensdauer",
            xaxis_title="Jahr",
            yaxis_title="CO₂ (Tonnen)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Umwelt-Kennzahlen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Gesamte CO₂-Einsparung",
                f"{co2_analysis['total_co2_savings']:.1f} t",
                help="Über 25 Jahre"
            )
        with col2:
            st.metric(
                "CO₂-Amortisation",
                f"{co2_analysis['carbon_payback_time']:.1f} Jahre",
                help="Zeit bis Herstellungs-CO₂ kompensiert"
            )
        with col3:
            st.metric(
                "Äquivalent Bäume",
                f"{co2_analysis['tree_equivalent']:,.0f} Bäume",
                help="Entspricht der CO₂-Bindung von Bäumen"
            )
        with col4:
            st.metric(
                "Vermiedene Autokilometer",
                f"{co2_analysis['car_km_equivalent']:,.0f} km",
                help="Entspricht CO₂-Emissionen eines PKW"
            )
        
        # Weitere Umweltaspekte
        st.markdown("### Weitere Umweltauswirkungen")
        
        environmental_impacts = pd.DataFrame({
            'Umweltaspekt': [
                'Primärenergieeinsparung',
                'Wasserverbrauch vermieden',
                'SO₂-Emissionen vermieden',
                'NOₓ-Emissionen vermieden',
                'Feinstaub vermieden'
            ],
            'Menge': [
                f"{co2_analysis['primary_energy_saved']:,.0f} kWh",
                f"{co2_analysis['water_saved']:,.0f} Liter",
                f"{co2_analysis['so2_avoided']:.1f} kg",
                f"{co2_analysis['nox_avoided']:.1f} kg",
                f"{co2_analysis['particulates_avoided']:.2f} kg"
            ],
            'Beschreibung': [
                'Eingesparte fossile Primärenergie',
                'Wasserverbrauch in Kraftwerken vermieden',
                'Schwefeldioxid-Emissionen verhindert',
                'Stickoxid-Emissionen verhindert',
                'Feinstaubemissionen verhindert'
            ]
        })
        
        st.dataframe(environmental_impacts, use_container_width=True)
    
    # Kreislaufwirtschaft
    with st.expander("Kreislaufwirtschaft & Recycling", expanded=True):
        recycling_analysis = integrator.calculate_recycling_potential(calc_results, project_data)
        
        # Materialzusammensetzung
        materials_df = pd.DataFrame(recycling_analysis['material_composition'])
        
        fig = px.pie(
            materials_df,
            values='weight_kg',
            names='material',
            title="Materialzusammensetzung der PV-Anlage",
            color_discrete_map={
                'Silizium': '#3B82F6',
                'Aluminium': '#6B7280',
                'Glas': '#10B981',
                'Kupfer': '#F59E0B',
                'Kunststoff': '#EF4444',
                'Sonstiges': '#8B5CF6'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recycling-Potenzial
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Recyclingquote",
                f"{recycling_analysis['recycling_rate']:.0f}%",
                help="Anteil recycelbarer Materialien"
            )
        with col2:
            st.metric(
                "Materialwert",
                format_kpi_value(recycling_analysis['material_value'], "€", texts_dict={}, precision=0),
                help="Geschätzter Restwert der Materialien"
            )
        with col3:
            st.metric(
                "CO₂-Einsparung durch Recycling",
                f"{recycling_analysis['co2_savings_recycling']:.1f} t",
                help="Vermiedene Emissionen durch Recycling"
            )

def render_optimization_suggestions(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Optimierungsvorschläge für das PV-System"""
    st.subheader("Optimierungsvorschläge")
    
    # Simuliere Optimierungsanalyse
    optimization_results = integrator.generate_optimization_suggestions(calc_results, project_data)
    
    # Quick Wins
    with st.expander("Sofort umsetzbare Verbesserungen", expanded=True):
        quick_wins = [
            {
                'title': 'Optimierung der Ausrichtung',
                'description': 'Feinabstimmung der Modulausrichtung für maximalen Ertrag',
                'potential': '+3-5% Ertrag',
                'cost': 'Gering',
                'effort': 'Niedrig'
            },
            {
                'title': 'Verschattungsoptimierung',
                'description': 'Beseitigung oder Minimierung von Verschattungsquellen',
                'potential': '+2-8% Ertrag',
                'cost': 'Variabel',
                'effort': 'Mittel'
            },
            {
                'title': 'Batteriemanagement-Optimierung',
                'description': 'Anpassung der Lade-/Entladezyklen',
                'potential': '+10-15% Eigenverbrauch',
                'cost': 'Keine',
                'effort': 'Niedrig'
            }
        ]
        
        for i, win in enumerate(quick_wins, 1):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                
                with col1:
                    st.markdown(f"**{i}. {win['title']}**")
                    st.caption(win['description'])
                
                with col2:
                    st.metric("Potenzial", win['potential'])
                
                with col3:
                    st.metric("Aufwand", f"{win['effort']} / {win['cost']}")
                
                if i < len(quick_wins):
                    st.markdown("---")
    
    # Langfristige Optimierungen
    with st.expander("Langfristige Optimierungen", expanded=False):
        long_term = [
            {
                'title': 'Systemerweiterung',
                'description': 'Ausbau der PV-Anlage oder Batteriekapazität',
                'investment': '5.000-15.000 €',
                'roi': '8-12 Jahre'
            },
            {
                'title': 'Smart-Home Integration',
                'description': 'Intelligente Verbrauchssteuerung',
                'investment': '1.000-3.000 €',
                'roi': '3-5 Jahre'
            },
            {
                'title': 'E-Mobilität Integration',
                'description': 'Wallbox für Elektrofahrzeuge',
                'investment': '800-2.500 €',
                'roi': '4-7 Jahre'
            }
        ]
        
        for opt in long_term:
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                st.markdown(f"**{opt['title']}**")
                st.caption(opt['description'])
            
            with col2:
                st.metric("Investition", opt['investment'])
            
            with col3:
                st.metric("ROI", opt['roi'])

def render_financial_scenarios(integrator, calc_results: Dict[str, Any], project_data: Dict[str, Any], texts: Dict[str, str]):
    """Finanzielle Szenarien"""
    st.subheader("Finanzielle Szenarioanalyse")
    
    # Monte-Carlo-Simulation
    with st.expander("Monte-Carlo-Risikoanalyse", expanded=True):
        # Simulationsparameter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            n_simulations = st.number_input(
                "Anzahl Simulationen",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100
            )
        
        with col2:
            confidence_level = st.slider(
                "Konfidenzintervall (%)",
                min_value=80,
                max_value=99,
                value=95
            )
        
        with col3:
            if st.button("Simulation starten"):
                with st.spinner("Führe Monte-Carlo-Simulation durch..."):
                    mc_results = integrator.run_monte_carlo_simulation(
                        calc_results, 
                        n_simulations,
                        confidence_level
                    )
                    st.session_state['mc_results'] = mc_results
        
        # Ergebnisse anzeigen
        if 'mc_results' in st.session_state:
            mc_results = st.session_state['mc_results']
            
            # NPV-Verteilung
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=mc_results['npv_distribution'],
                nbinsx=50,
                name='NPV-Verteilung',
                marker_color='#3B82F6',
                opacity=0.7
            ))
            
            # Konfidenzintervall markieren
            fig.add_vline(x=mc_results['npv_lower_bound'], 
                         line_dash="dash", line_color="red",
                         annotation_text=f"{(100-confidence_level)/2}%")
            fig.add_vline(x=mc_results['npv_upper_bound'], 
                         line_dash="dash", line_color="red",
                         annotation_text=f"{100-(100-confidence_level)/2}%")
            fig.add_vline(x=mc_results['npv_mean'], 
                         line_dash="solid", line_color="green",
                         annotation_text="Erwartungswert")
            
            fig.update_layout(
                title="NPV-Verteilung (Monte-Carlo-Simulation)",
                xaxis_title="Net Present Value (€)",
                yaxis_title="Häufigkeit",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Risikokennzahlen
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Erwarteter NPV",
                    format_kpi_value(mc_results['npv_mean'], "€", texts_dict={}, precision=0),
                    delta=f"σ = {mc_results['npv_std']:,.0f} €"
                )
            with col2:
                st.metric(
                    "Value at Risk (5%)",
                    format_kpi_value(mc_results['var_5'], "€", texts_dict={}, precision=0),
                    help="5% Wahrscheinlichkeit für schlechteren Wert"
                )
            with col3:
                st.metric(
                    "Erfolgswahrscheinlichkeit",
                    f"{mc_results['success_probability']:.1f}%",
                    help="Wahrscheinlichkeit für positiven NPV"
                )
            with col4:
                st.metric(
                    f"{confidence_level}% Konfidenzintervall",
                    f"{mc_results['npv_lower_bound']:,.0f} - {mc_results['npv_upper_bound']:,.0f} €"
                )
            
            # Sensitivitätsanalyse
            st.markdown("### Sensitivitätsanalyse")
            
            sensitivity_df = pd.DataFrame(mc_results['sensitivity_analysis'])
            
            fig = px.bar(
                sensitivity_df,
                x='impact',
                y='parameter',
                orientation='h',
                color='impact',
                color_continuous_scale='RdBu_r',
                title="Einfluss der Parameter auf NPV"
            )
            
            fig.update_layout(
                xaxis_title="Relativer Einfluss auf NPV",
                yaxis_title="Parameter"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Förderszenarien
    with st.expander("Förderszenarien", expanded=True):
        subsidy_scenarios = integrator.calculate_subsidy_scenarios(calc_results)
        
        # Szenario-Vergleich
        scenarios_df = pd.DataFrame(subsidy_scenarios['scenarios'])
        
        fig = go.Figure()
        
        for scenario in scenarios_df.columns[1:]:  # Skip 'Jahr' column
            fig.add_trace(go.Scatter(
                x=scenarios_df['Jahr'],
                y=scenarios_df[scenario],
                mode='lines+markers',
                name=scenario,
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title="Kumulierter Cashflow - Förderszenarien",
            xaxis_title="Jahr",
            yaxis_title="Kumulierter Cashflow (€)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Szenario-Vergleich Tabelle
        comparison_df = pd.DataFrame(subsidy_scenarios['comparison'])
        
        st.dataframe(
            comparison_df.style.format({
                'NPV': '{:,.0f} €',
                'IRR': '{:.1f}%',
                'Amortisation': '{:.1f} Jahre',
                'Förderung': '{:,.0f} €'
            }).background_gradient(subset=['NPV'], cmap='Greens'),
            use_container_width=True
        )

def _calculate_amortization_time(investment, annual_savings):
    """
    Berechnet die Amortisationszeit eines Investments basierend auf den jährlichen Einsparungen.
    
    Args:
        investment: Gesamtinvestition in Euro
        annual_savings: Jährliche Einsparungen in Euro
    
    Returns:
        float: Amortisationszeit in Jahren oder 0.0 bei ungültigen Werten
    """
    if not isinstance(investment, (int, float)) or not isinstance(annual_savings, (int, float)):
        return 0.0
    
    if annual_savings <= 0 or investment <= 0:
        return 0.0
    
    return investment / annual_savings

def _calculate_electricity_costs_projection(results, years, price_increase_percent):
    """Berechnet prognostizierte Stromkosten über x Jahre mit Preissteigerung"""
    # Hole die tatsächlichen jährlichen Stromkosten aus der Bedarfsanalyse
    project_data = st.session_state.get('project_data', {})
    household_costs = project_data.get('stromkosten_haushalt_euro_jahr', 0.0)
    heating_costs = project_data.get('stromkosten_heizung_euro_jahr', 0.0)
    
    # Fallback: aus results berechnen wenn Eingabedaten nicht vorhanden
    if household_costs <= 0 and heating_costs <= 0:
        annual_consumption = results.get('annual_consumption_kwh', 0.0)
        current_price = results.get('electricity_price_euro_per_kwh', 0.35)
        annual_total_costs = annual_consumption * current_price
    else:
        annual_total_costs = household_costs + heating_costs
    
    if annual_total_costs <= 0:
        return 0.0
    
    total_costs = 0.0
    for year in range(1, years + 1):
        yearly_costs = annual_total_costs * ((1 + price_increase_percent / 100) ** (year - 1))
        total_costs += yearly_costs
    
    return total_costs

def format_kpi_value(value, unit, texts_dict, precision=2):
    """Formatiert KPI-Werte im deutschen Format"""
    if not isinstance(value, (int, float)) or value == 0:
        return f"0{unit}"
    
    if precision == 0:
        formatted = f"{value:,.0f}"
    else:
        formatted = f"{value:,.{precision}f}"
    
    # Deutsche Formatierung: Punkt als Tausendertrennzeichen, Komma als Dezimaltrennzeichen
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return f"{formatted}{unit}"

def _calculate_final_price_with_modifications(netto_betrag, pricing_modifications):
    """Berechnet final_price, total_rebates und total_surcharges aus Nettobetrag und Modifikationsdaten."""
    discount_percent = pricing_modifications.get('discount_percent', 0.0)
    rebates_eur = pricing_modifications.get('rebates_eur', 0.0)
    surcharge_percent = pricing_modifications.get('surcharge_percent', 0.0)
    special_costs_eur = pricing_modifications.get('special_costs_eur', 0.0)
    miscellaneous_eur = pricing_modifications.get('miscellaneous_eur', 0.0)
    discount_amount = netto_betrag * (discount_percent / 100)
    total_rebates = discount_amount + rebates_eur
    surcharge_amount = netto_betrag * (surcharge_percent / 100)
    total_surcharges = surcharge_amount + special_costs_eur + miscellaneous_eur
    final_price = netto_betrag - total_rebates + total_surcharges
    return final_price, total_rebates, total_surcharges
    
def _get_pricing_modifications_from_session():
    """Liefert die aktuellen Preismodifikationswerte aus dem Session State (Rabatte, Aufschläge etc.)"""
    return {
        'discount_percent': st.session_state.get('pricing_modifications_discount_slider', 0.0),
        'rebates_eur': st.session_state.get('pricing_modifications_rebates_slider', 0.0),
        'surcharge_percent': st.session_state.get('pricing_modifications_surcharge_slider', 0.0),
        'special_costs_eur': st.session_state.get('pricing_modifications_special_costs_slider', 0.0),
        'miscellaneous_eur': st.session_state.get('pricing_modifications_miscellaneous_slider', 0.0)
    }


def render_analysis(texts: Dict[str, str], results: Optional[Dict[str, Any]] = None) -> None:
    """Hauptfunktion für das Analyse-Dashboard"""
    if not _ANALYSIS_DEPENDENCIES_AVAILABLE:
        st.error(get_text(texts,"analysis_module_critical_error", "Kritischer Fehler: Analyse-Modul-Abhängigkeiten nicht verfügbar"))
        return
    
    st.header(get_text(texts,"dashboard_header","Ergebnisse und Dashboard"))
    project_inputs = st.session_state.get("project_data",{})
    viz_settings = _get_visualization_settings()

    # Seitenleiste für Analyse-Parameter
    st.sidebar.subheader(get_text(texts, "analysis_interactive_settings_header", "Analyse-Parameter"))
    admin_defaults_gc = load_admin_setting('global_constants', {'simulation_period_years': 20, 'electricity_price_increase_annual_percent': 3.0})
    admin_default_sim_years = int(admin_defaults_gc.get('simulation_period_years', 20) or 20)
    admin_default_price_increase = float(admin_defaults_gc.get('electricity_price_increase_annual_percent', 3.0) or 3.0)
    
    current_sim_years_for_ui = admin_default_sim_years
    current_price_increase_for_ui = admin_default_price_increase
    
    # Aktuelle Berechnungsergebnisse verwenden, falls vorhanden
    previous_calc_results = st.session_state.get("calculation_results", {})
    if results and isinstance(results, dict) and results.get('simulation_period_years_effective') is not None:
        current_sim_years_for_ui = int(results['simulation_period_years_effective'])
        current_price_increase_for_ui = float(results.get('electricity_price_increase_rate_effective_percent', admin_default_price_increase))
    elif previous_calc_results and previous_calc_results.get('simulation_period_years_effective') is not None:
        current_sim_years_for_ui = int(previous_calc_results['simulation_period_years_effective'])
        current_price_increase_for_ui = float(previous_calc_results.get('electricity_price_increase_rate_effective_percent', admin_default_price_increase))
    
    # UI-Eingabefelder
    sim_duration_user_input = st.sidebar.number_input(
        get_text(texts,"analysis_sim_duration_label","Simulationsdauer (Jahre)"),
        min_value=1, max_value=50, value=current_sim_years_for_ui, step=1,
        key="analysis_sim_duration_input_v22_final_corrected"
    )
    sim_price_increase_user_input = st.sidebar.number_input(
        get_text(texts,"analysis_sim_price_increase_label","Strompreissteigerung p.a. (%)"),
        min_value=0.0, max_value=20.0, value=current_price_increase_for_ui, step=0.1, format="%.1f",
        key="analysis_price_increase_input_v22_final_corrected"
    )

    st.markdown("---")
    render_pricing_modifications_ui()
    st.markdown("---")

    # Berechnungslogik
    if st.button(get_text(texts,"analysis_calculate_button","Berechnung aktualisieren"), type="primary"):
        with st.spinner(get_text(texts,"analysis_calculating_status","Führe Berechnungen durch...")):
            errors_list = []
            results_for_display = perform_calculations(
                project_inputs,
                texts=texts,
                errors_list=errors_list,
                simulation_duration_user=sim_duration_user_input,
                electricity_price_increase_user=sim_price_increase_user_input
            )
            
            if errors_list:
                for error in errors_list:
                    st.error(error)
            
            if results_for_display and isinstance(results_for_display, dict):
                st.session_state['calculation_results'] = results_for_display
                st.success(get_text(texts,"analysis_calculation_complete","Berechnungen abgeschlossen"))
                st.rerun()
            else:
                st.error(get_text(texts,"analysis_calculation_failed","Berechnungen fehlgeschlagen"))

    # Ergebnisse anzeigen
    results_for_display = results or st.session_state.get('calculation_results', {})
    
    if not results_for_display:
        st.info(get_text(texts,"analysis_no_results","Keine Berechnungsergebnisse verfügbar. Bitte führen Sie zuerst eine Berechnung durch."))
        return

    # Hauptanalyse-Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([get_text(texts,"analysis_tab_overview","Übersicht"),
        get_text(texts,"analysis_tab_financial","Wirtschaftlichkeit"),
        get_text(texts,"analysis_tab_energy","Energieanalyse"),
        get_text(texts,"analysis_tab_technical","Technik"),
        get_text(texts,"analysis_tab_environment","Umwelt"),
        get_text(texts,"analysis_tab_advanced","Erweiterte Analysen")
    ])

    with tab1:  # Übersicht
        st.subheader(get_text(texts,"analysis_overview_header","Projekt-Übersicht"))
        _render_overview_section(results_for_display, texts, viz_settings)

    with tab2:  # Wirtschaftlichkeit
        st.subheader(get_text(texts,"analysis_financial_header","Wirtschaftlichkeitsanalyse"))
        _render_financial_section(results_for_display, texts, viz_settings)

    with tab3:  # Energieanalyse
        st.subheader(get_text(texts,"analysis_energy_header","Energieanalyse"))
        _render_energy_section(results_for_display, texts, viz_settings)

    with tab4:  # Technische Analyse
        st.subheader(get_text(texts,"analysis_technical_header","Technische Analyse"))
        _render_technical_section(results_for_display, texts, viz_settings)

    with tab5:  # Umweltanalyse
        st.subheader(get_text(texts,"analysis_environment_header","Umweltanalyse"))
        _render_environment_section(results_for_display, texts, viz_settings)

    with tab6:  # Erweiterte Analysen
        integrate_advanced_calculations(texts)

def _render_overview_section(results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    """Übersichts-Sektion mit umfassenden KPIs rendern"""
    
    # Preismodifikationen aus Session State abrufen
    pricing_modifications = _get_pricing_modifications_from_session()
    
    # Preis-KPIs berechnen
    netto_betrag = results.get('total_investment_netto', 0.0)
    brutto_betrag = results.get('total_investment_brutto', 0.0)
    
    # Live-Vorschau der Preismodifikationen berechnen
    final_price, total_rebates, total_surcharges = _calculate_final_price_with_modifications(
        netto_betrag, pricing_modifications
    )
    
    # MwSt-Ersparnis berechnen (nur für Privatpersonen)
    customer_type = st.session_state.get('project_data', {}).get('customer_data', {}).get('type', '')
    is_private = customer_type.lower() in ['privat', 'private', 'privatperson']
    mwst_ersparnis = (brutto_betrag - netto_betrag) if is_private else 0.0
    
    # Amortisationszeit korrekt berechnen
    annual_savings = results.get('annual_total_savings_euro', 0.0)
    amortisation_years = _calculate_amortization_time(final_price, annual_savings)
    
    # Hauptmetriken in 6 Spalten
    st.subheader("🔑 Haupt-KPIs")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            get_text(texts,"kpi_net_amount","Nettobetrag"),
            format_kpi_value(netto_betrag, "€", texts_dict=texts, precision=2)
        )
    
    with col2:
        rebate_color = "🟢" if total_rebates > 0 else ""
        st.metric(
            f"{rebate_color} " + get_text(texts,"kpi_rebates","Rabatte"),
            format_kpi_value(total_rebates, "€", texts_dict=texts, precision=2)
        )
    
    with col3:
        surcharge_color = "🔴" if total_surcharges > 0 else ""
        st.metric(
            f"{surcharge_color} " + get_text(texts,"kpi_surcharges","Aufpreise"),
            format_kpi_value(total_surcharges, "€", texts_dict=texts, precision=2)
        )
    
    with col4:
        st.metric(
            get_text(texts,"kpi_final_price","Finaler Angebotspreis"),
            format_kpi_value(final_price, "€", texts_dict=texts, precision=2)
        )
    
    with col5:
        if is_private:
            st.metric(
                get_text(texts,"kpi_vat_savings","Ersparte MwSt"),
                format_kpi_value(mwst_ersparnis, "€", texts_dict=texts, precision=2)
            )
        else:
            st.metric(
                get_text(texts,"kpi_vat_savings","MwSt-Status"),
                "Geschäftskunde"
            )
    
    with col6:
        amortization_color = "🟢" if amortisation_years <= 10 else "🟡" if amortisation_years <= 15 else "🔴"
        st.metric(
            f"{amortization_color} " + get_text(texts,"kpi_payback_time","Amortisationszeit"),
            format_kpi_value(amortisation_years, "Jahre", texts_dict=texts, precision=1) if amortisation_years > 0 else "Nicht berechenbar"
        )
    
    st.markdown("---")
    
    # Energie-KPIs in 4 Spalten
    st.subheader("⚡ Energie-KPIs")
    ecol1, ecol2, ecol3, ecol4 = st.columns(4)
    
    with ecol1:
        st.metric(
            get_text(texts,"kpi_annual_yield","Jährliche Stromproduktion"),
            format_kpi_value(results.get('annual_pv_production_kwh', 0.0), "kWh", texts_dict=texts, precision=0)
        )
    
    with ecol2:
        st.metric(
            get_text(texts,"kpi_self_sufficiency","Autarkiegrad"),
            f"{results.get('self_supply_rate_percent', 0.0):.1f}%"
        )
    
    with ecol3:
        eigenverbrauch = results.get('annual_selfuse_kwh', 0.0)
        st.metric(
            get_text(texts,"kpi_self_consumption","Eigenverbrauch"),
            format_kpi_value(eigenverbrauch, "kWh", texts_dict=texts, precision=0)
        )
    
    with ecol4:
        einspeisung = results.get('annual_feedin_kwh', 0.0)
        st.metric(
            get_text(texts,"kpi_feed_in","Einspeisung"),
            format_kpi_value(einspeisung, "kWh", texts_dict=texts, precision=0)
        )
    
    st.markdown("---")
    
    # Langzeit-Stromkosten in 3 Spalten
    st.subheader("📊 Stromkosten-Prognose")
    simulation_years = results.get('simulation_period_years_effective', 20)
    electricity_price_increase = results.get('electricity_price_increase_rate_effective_percent', 3.0)
    
    fcol1, fcol2, fcol3 = st.columns(3)
    
    with fcol1:
        costs_10_years = _calculate_electricity_costs_projection(results, 10, electricity_price_increase)
        st.metric(
            "💡 Stromkosten (10 Jahre)",
            format_kpi_value(costs_10_years, "€", texts_dict=texts, precision=0)
        )
    
    with fcol2:
        costs_20_years = _calculate_electricity_costs_projection(results, 20, electricity_price_increase)
        st.metric(
            "💡 Stromkosten (20 Jahre)",
            format_kpi_value(costs_20_years, "€", texts_dict=texts, precision=0)
        )
    
    with fcol3:
        costs_30_years = _calculate_electricity_costs_projection(results, 30, electricity_price_increase)
        st.metric(
            "💡 Stromkosten (30 Jahre)",
            format_kpi_value(costs_30_years, "€", texts_dict=texts, precision=0)
        )
    
    st.markdown("---")
    
    # Einspeisevergütung und Netzbezug
    st.subheader("🔄 Energie-Bilanz")
    bcol1, bcol2, bcol3 = st.columns(3)
    
    with bcol1:
        netzbezug = results.get('annual_grid_purchase_kwh', 0.0)
        st.metric(
            get_text(texts,"kpi_grid_purchase","Netzbezug"),
            format_kpi_value(netzbezug, "kWh", texts_dict=texts, precision=0)
        )
    
    with bcol2:
        einspeisung_verguetung = results.get('annual_feedin_revenue_euro', 0.0)
        st.metric(
            get_text(texts,"kpi_feed_in_revenue","Einspeisevergütung"),
            format_kpi_value(einspeisung_verguetung, "€", texts_dict=texts, precision=2)
        )
    
    with bcol3:
        gesamt_einsparung = results.get('annual_total_savings_euro', 0.0)
        st.metric(
            get_text(texts,"kpi_total_savings","Gesamteinsparung/Jahr"),
            format_kpi_value(gesamt_einsparung, "€", texts_dict=texts, precision=2)
        )

def _render_financial_section(results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    """Finanzielle Analyse-Sektion"""
    render_income_projection_switcher(results, texts, viz_settings)
    render_roi_comparison_switcher(results, texts, viz_settings)
    render_scenario_comparison_switcher(results, texts, viz_settings)

def _render_energy_section(results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    """Energie-Analyse-Sektion"""
    render_production_vs_consumption_switcher(results, texts, viz_settings)
    render_selfuse_ratio_switcher(results, texts, viz_settings)
    _render_consumption_coverage_pie(results, texts, viz_settings, "consumption_coverage")
    _render_pv_usage_pie(results, texts, viz_settings, "pv_usage")

def _render_technical_section(results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    """Technische Analyse-Sektion"""
    render_daily_production_switcher(results, texts, viz_settings)
    render_weekly_production_switcher(results, texts, viz_settings)
    render_yearly_production_switcher(results, texts, viz_settings)

def _render_environment_section(results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    """Umwelt-Analyse-Sektion"""
    render_co2_savings_value_switcher(results, texts, viz_settings)

def render_pricing_modifications_ui():
    """Erweiterte UI für Preismodifikationen mit Live-Vorschau"""
    st.subheader("Preisanpassungen & Sondervereinbarungen")
    
    # Live-Vorschau in der Sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("#### 🎯 Live-Kalkulation")
        
        # Hole alle relevanten Daten
        project_data = st.session_state.get('project_data', {})
        calc_results = st.session_state.get('calculation_results', {})
        
        # Basispreis ermitteln
        base_investment = project_data.get('total_investment_brutto', 0)
        netto_betrag = calc_results.get('total_investment_netto', 0)
        if base_investment <= 0:
            base_investment = netto_betrag if netto_betrag > 0 else 15000.0
        
        # Hole aktuelle Modifikationswerte (korrigierte Session State Keys)
        discount_percent = st.session_state.get('pricing_modifications_discount_slider', 0.0)
        rebates_eur = st.session_state.get('pricing_modifications_rebates_slider', 0.0)
        surcharge_percent = st.session_state.get('pricing_modifications_surcharge_slider', 0.0)
        special_costs_eur = st.session_state.get('pricing_modifications_special_costs_slider', 0.0)
        miscellaneous_eur = st.session_state.get('pricing_modifications_miscellaneous_slider', 0.0)
        
        # Berechnungen für Preismodifikationen
        discount_amount = base_investment * (discount_percent / 100)
        total_rebates = discount_amount + rebates_eur
        surcharge_amount = base_investment * (surcharge_percent / 100)
        total_surcharges = surcharge_amount + special_costs_eur + miscellaneous_eur
        final_price = base_investment - total_rebates + total_surcharges
        
        # Zusätzliche KPIs aus calc_results (korrigierte Datenquellen)
        annual_pv_production = calc_results.get('annual_pv_production_kwh', 0.0)
        autarkiegrad = calc_results.get('self_supply_rate_percent', 0.0)
        
        # Korrigierte Berechnung von Eigenverbrauch und Einspeisung
        total_consumption = calc_results.get('annual_consumption_kwh', 0.0)
        grid_purchase = calc_results.get('annual_grid_purchase_kwh', 0.0)
        eigenverbrauch = total_consumption - grid_purchase if total_consumption > grid_purchase else annual_pv_production * (autarkiegrad / 100.0) if autarkiegrad > 0 else 0.0
        einspeisung = annual_pv_production - eigenverbrauch if annual_pv_production > eigenverbrauch else 0.0
        
        # Korrekte Berechnung der Einspeisevergütung und Gesamteinsparung
        feedin_rate = calc_results.get('feedin_tariff_euro_per_kwh', 0.0792)  # Fallback 8 Cent
        einspeiseverguetung = einspeisung * feedin_rate
        
        # Stromkosteneinsparung durch Eigenverbrauch
        electricity_price = calc_results.get('electricity_price_euro_per_kwh', 0.35)  # Fallback 30 Cent
        eigenverbrauch_einsparung = eigenverbrauch * electricity_price
        gesamteinsparung = eigenverbrauch_einsparung + einspeiseverguetung
        
        # MwSt-Ersparnis korrekt berechnen (19% auf Nettobetrag für Privatpersonen durch Förderung)
        customer_type = project_data.get('customer_data', {}).get('type', '')
        is_private = customer_type.lower() in ['privat', 'private', 'privatperson']
        # MwSt-Ersparnis nur für Privatpersonen: 19% auf den Nettobetrag
        mwst_ersparnis = netto_betrag * 0.19 if is_private and netto_betrag > 0 else 0.0
        
        # Amortisationszeit korrekt berechnen
        amortisation_years = final_price / gesamteinsparung if gesamteinsparung > 0 else float('inf')
        
        # Amortisationszeit-Farbe und Anzeige
        if amortisation_years == float('inf'):
            amortization_color = "�"
            amortization_display = "Nicht rentabel"
        elif amortisation_years <= 10:
            amortization_color = "🟢"
            amortization_display = f"{amortisation_years:.1f} Jahre"
        elif amortisation_years <= 15:
            amortization_color = "🟡" 
            amortization_display = f"{amortisation_years:.1f} Jahre"
        else:
            amortization_color = "🔴"
            amortization_display = f"{amortisation_years:.1f} Jahre"
        
        # CSS für kleinere, fettere Ergebnisse mit deutscher Formatierung
        st.markdown("""
        <style>
        .stMetric > div > div > div > div {
            font-size: 0.45rem !important;
            font-weight: bold !important;
        }
        .stMetric > div > div > div > div:first-child {
            font-size: 0.45rem !important;
            font-weight: normal !important;
        }
        .sidebar .stMetric > div > div > div > div {
            font-size: 0.45rem !important;
            font-weight: bold !important;
        }
        .sidebar .stMetric > div > div > div > div:first-child {
            font-size: 0.45rem !important;
            font-weight: normal !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Preis-KPIs in 3er-Gruppen mit deutscher Formatierung
        st.markdown("**💰 Preise & Kosten**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Grundpreis", f"{base_investment:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'), label_visibility="visible")
        with col2:
            if total_rebates > 0:
                st.metric("Summe Rabatte", f"-{total_rebates:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'), 
                         delta=f"-{total_rebates/base_investment*100:.1f}%".replace('.', ',') if base_investment > 0 else "")
            else:
                st.metric("Summe Rabatte", "0,00€")
        with col3:
            if total_surcharges > 0:
                st.metric("Summe Aufschläge", f"+{total_surcharges:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'),
                         delta=f"+{total_surcharges/base_investment*100:.1f}%".replace('.', ',') if base_investment > 0 else "")
            else:
                st.metric("Summe Aufschläge", "0,00€")
        
        # Finaler Preis und wichtige Finanz-KPIs mit deutscher Formatierung
        col1, col2, col3 = st.columns(3)
        with col1:
            price_change = final_price - base_investment
            st.metric("Finaler Angebotspreis", f"{final_price:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'),
                     delta=f"{price_change:+,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.') if price_change != 0 else None)
        with col2:
            if is_private:
                st.metric("MwSt-Ersparnis", f"{mwst_ersparnis:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'))
            else:
                st.metric("Kundentyp", "Gewerbe")
        with col3:
            st.metric(f"{amortization_color} Amortisation", amortization_display)
        
        st.markdown("---")
        
        # Energie-KPIs mit deutscher Formatierung
        st.markdown("**⚡ Energie & Leistung**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("jährliche Stromproduktion", f"{annual_pv_production:,.0f}kWh".replace(',', 'X').replace('.', ',').replace('X', '.'))
        with col2:
            st.metric("Autarkiegrad", f"{autarkiegrad:.1f}%".replace(',', 'X').replace('.', ',').replace('X', '.'))
        with col3:
            st.metric("direkter Eigenverbrauch", f"{eigenverbrauch:,.0f}kWh".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Einspeisung", f"{einspeisung:,.0f}kWh".replace(',', 'X').replace('.', ',').replace('X', '.'))
        with col2:
            st.metric("jährliche Vergütung", f"{einspeiseverguetung:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'))
        with col3:
            st.metric("Einsparung/Jahr", f"{gesamteinsparung:,.2f}€".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # Speichere erweiterte Live-Kalkulation mit korrigierten Werten
        st.session_state['live_pricing_calculations'] = {
            'base_price': base_investment,
            'total_rebates': total_rebates,
            'total_surcharges': total_surcharges,
            'final_price': final_price,
            'amortisation_years': amortisation_years if amortisation_years != float('inf') else 0.0,
            'mwst_ersparnis': mwst_ersparnis,
            'annual_pv_production': annual_pv_production,
            'autarkiegrad': autarkiegrad,
            'eigenverbrauch': eigenverbrauch,
            'einspeisung': einspeisung,
            'einspeiseverguetung': einspeiseverguetung,
            'gesamteinsparung': gesamteinsparung,
            'eigenverbrauch_einsparung': eigenverbrauch_einsparung
        }
    
    # Basis-Projektdaten für Hauptbereich holen
    project_data = st.session_state.get('project_data', {})
    base_investment = project_data.get('total_investment_brutto', 2)
    
    # Sicherstellen, dass base_price nicht 0 ist
    if base_investment <= 0:
        # Fallback-Wert aus session_state.calculation_results verwenden
        calc_results = st.session_state.get('calculation_results', {})
        base_investment = calc_results.get('total_investment_netto', 2)
        if base_investment <= 0:
            base_investment = 15000.0  # Standard-Fallback-Wert
      # Tabs für verschiedene Modifikationstypen
    tab1, tab2 = st.tabs(["Rabatte & Aufschläge", "Sondervereinbarungen"])
    
    with tab1:
        st.subheader("Standardanpassungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Rabatte")
            discount_percent = st.slider(
                "Rabatt (%)", 
                min_value=0.0, max_value=50.0, value=0.0, step=0.1,
                key="pricing_modifications_discount_slider"
            )
            
            rebates_eur = st.number_input(
                "Zusätzliche Rabatte (€)",
                min_value=0.0, max_value=50000.0, value=0.0, step=100.0,
                key="pricing_modifications_rebates_slider"
            )
            
            # Beschreibungsfelder für Rabatte
            discount_description = st.text_area(
                "Beschreibung Rabatt",
                placeholder="z.B. Frühbucherrabatt, Mengenrabatt...",
                key="pricing_modifications_descriptions_discount_text"
            )
            
            rebates_description = st.text_area(
                "Beschreibung zusätzliche Rabatte",
                placeholder="z.B. Kundenbindungsrabatt, Weiterempfehlungsrabatt...",
                key="pricing_modifications_descriptions_rebates_text"
            )
        
        with col2:
            st.markdown("#### Aufschläge")
            surcharge_percent = st.slider(
                "Aufschlag (%)",
                min_value=0.0, max_value=30.0, value=0.0, step=0.1,
                key="pricing_modifications_surcharge_slider"
            )
            
            special_costs_eur = st.number_input(
                "Sonderkosten (€)",
                min_value=0.0, max_value=20000.0, value=0.0, step=50.0,
                key="pricing_modifications_special_costs_slider"
            )
            
            # Beschreibungsfelder für Aufschläge
            surcharge_description = st.text_area(
                "Beschreibung Aufschlag",
                placeholder="z.B. Express-Service, Premium-Komponenten...",
                key="pricing_modifications_descriptions_surcharge_text"
            )
            
            special_costs_description = st.text_area(
                "Beschreibung Sonderkosten",
                placeholder="z.B. Gerüst, Sondermontage, Zusatzarbeiten...",
                key="pricing_modifications_descriptions_special_costs_text_unique"
            )
    
    with tab2:
        st.subheader("Individuelle Sondervereinbarungen")
        
        # Flexible Eingabe für beliebige Anpassungen
        st.markdown("#### Freie Preisanpassungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            miscellaneous_eur = st.number_input(
                "Sonstige Anpassungen (€)",
                min_value=-10000.0, max_value=10000.0, value=0.0, step=50.0,
                help="Positive Werte = Aufschlag, Negative Werte = Rabatt",
                key="pricing_modifications_miscellaneous_slider"
            )
            
            miscellaneous_description = st.text_area(
                "Beschreibung sonstige Anpassungen",
                placeholder="z.B. Individuelle Vereinbarung, Kulanz...",
                key="pricing_modifications_descriptions_miscellaneous_text"
            )
        
        with col2:
            # Spezielle Vereinbarungen als Freitext
            special_agreements = st.text_area(
                "Spezielle Vereinbarungen",
                placeholder="Beschreibung besonderer Konditionen, Zahlungsmodalitäten, etc.",
                height=100,
                key="pricing_modifications_special_agreements_text"
            )
            
            # Zahlungsmodalitäten
            st.markdown("#### 💳 Zahlungsoptionen")
            payment_terms = st.selectbox(
                "Zahlungsweise",
                ["Standard (bei Lieferung)", "30 Tage Zahlungsziel", "Anzahlung + Rest bei Fertigstellung", 
                 "Ratenzahlung", "Sondervereinbarung"],
                key="pricing_modifications_payment_terms"
            )    
    st.markdown("---")
