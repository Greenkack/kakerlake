"""
Datei: analysis.py
Zweck: Modul für den Analyse Tab / Dashboard (A.5) - Vollständig mit allen Switcher-Diagrammdefinitionen, Diagramm-Typ-Switcher und Farbanpassung.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-02
"""
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
    from calculations import perform_calculations as real_perform_calculations # type: ignore
    if not callable(real_perform_calculations):
        raise ImportError("Imported perform_calculations from calculations.py is not callable.")
    _CALCULATIONS_PERFORM_CALCULATIONS_AVAILABLE = True
    perform_calculations = real_perform_calculations
except ImportError:
    def perform_calculations(project_data, texts=None, errors_list=None, simulation_duration_user=None, electricity_price_increase_user=None): # type: ignore
        if errors_list is not None: errors_list.append("FEHLER: Berechnungsmodul nicht geladen.")
        return {"calculation_errors": ["Berechnungsmodul nicht geladen."]}

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
    st.subheader(get_text(texts, "viz_daily_prod_subheader_switcher", "☀️ Tagesproduktion – 3D-Stundenbalken (simuliert)"))
    hours = list(range(24)); anlage_kwp_val = analysis_results.get('anlage_kwp', 0.0)
    if not isinstance(anlage_kwp_val, (int, float)) or anlage_kwp_val <=0: anlage_kwp_val = 5.0
    power = [round(p,2) for p in np.maximum(0, np.sin((np.array(hours)-6)/12 * np.pi)) * (anlage_kwp_val * 1.3)]
    fig_daily = go.Figure()
    primary_color_hex = viz_settings.get("primary_chart_color", "#1f77b4")
    try:
        rgb_primary_norm = colors.HexColor(primary_color_hex).rgb()
        base_h, base_l, base_s = colorsys.rgb_to_hls(rgb_primary_norm[0], rgb_primary_norm[1], rgb_primary_norm[2])
    except Exception:
        r_fb, g_fb, b_fb = (0.121, 0.466, 0.705); base_h, base_l, base_s = colorsys.rgb_to_hls(r_fb, g_fb, b_fb)
    for i, p_val in enumerate(power):
        current_hue = (base_h + (i / 48.0)) % 1.0
        r_bar, g_bar, b_bar = colorsys.hls_to_rgb(current_hue, base_l, base_s)
        bar_color_plotly = f'rgb({int(r_bar*255)}, {int(g_bar*255)}, {int(b_bar*255)})'
        r_marker, g_marker, b_marker = colorsys.hls_to_rgb(current_hue, max(0, base_l * 0.6), base_s)
        marker_color_plotly = f'rgb({int(r_marker*255)}, {int(g_marker*255)}, {int(b_marker*255)})'
        fig_daily.add_trace(go.Scatter3d(x=[i,i],y=[0,0],z=[0,p_val],mode='lines',line=dict(width=20,color=bar_color_plotly),name=f'Std. {i}',text=f"Std. {i}:{p_val:.2f} kWh",hoverinfo='text'))
        fig_daily.add_trace(go.Scatter3d(x=[i],y=[0],z=[p_val],mode='markers',marker=dict(size=3,color=marker_color_plotly),hoverinfo='skip'))
    fig_daily.update_layout(title=get_text(texts,"viz_daily_prod_title_switcher","Simulierte Tagesproduktion"),scene=dict(xaxis_title='Stunde',yaxis_title='',zaxis_title='kWh',xaxis=dict(tickvals=list(range(0,24,2)))),margin=dict(l=10,r=10,t=50,b=10))
    _apply_custom_style_to_fig(fig_daily,viz_settings,"daily_production_switcher")
    st.plotly_chart(fig_daily,use_container_width=True,key="analysis_daily_prod_switcher_key_v6_final")
    analysis_results['daily_production_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig_daily,texts)

def render_weekly_production_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_weekly_prod_subheader_switcher", "📅 Wochenproduktion – 3D-Fläche (simuliert)"))
    days = get_text(texts,"day_names_short_list_switcher","Mo,Di,Mi,Do,Fr,Sa,So").split(',')
    if len(days)!=7: days=["Mo","Di","Mi","Do","Fr","Sa","So"]
    hours=list(range(24)); anlage_kwp_val=analysis_results.get('anlage_kwp',0.0)
    if not isinstance(anlage_kwp_val,(int,float)) or anlage_kwp_val <=0: anlage_kwp_val=5.0
    Z_weekly = np.maximum(0, np.random.rand(7,24)*np.sin((np.array(hours)-6)/12*np.pi)*(anlage_kwp_val*1.2))
    selected_palette = viz_settings.get("default_color_palette","Viridis")
    valid_continuous_scales = ['aggrnyl','agsunset','algae','amp','armyrose','balance','blackbody','bluered','blues','blugrn','bluyl','brbg','brwnyl','bugn','bupu','burg','burgyl','cividis','curl','darkmint','deep','delta','dense','earth','edge','electric','emrld','fall','geyser','gnbu','gray','greens','greys','haline','hot','hsv','ice','icefire','inferno','jet','magenta','magma','matter','mint','mrybm','mygbm','oranges','orrd','oryel','oxy','peach','phase','picnic','pinkyl','piyg','plasma','plotly3','portland','prgn','pubu','pubugn','puor','purd','purp','purples','purpor','rainbow','rdbu','rdgy','rdpu','rdylbu','rdylgn','redor','reds','solar','spectral','speed','sunset','sunsetdark','teal','tealgrn','tealrose','tempo','temps','thermal','tropic','turbid','turbo','twilight','viridis','ylgn','ylgnbu','ylorbr','ylorrd']
    color_scale_name = selected_palette if selected_palette in valid_continuous_scales else "Viridis"
    fig=go.Figure(data=[go.Surface(z=Z_weekly,x=hours,y=days,colorscale=color_scale_name)])
    fig.update_layout(title=get_text(texts,"viz_weekly_prod_title_switcher","Simulierte Wochenproduktion"),scene=dict(xaxis_title='Stunde',yaxis_title='Tag',zaxis_title='kWh'),margin=dict(l=10,r=10,t=50,b=10))
    _apply_custom_style_to_fig(fig,viz_settings,"weekly_production_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_weekly_prod_switcher_key_v6_final")
    analysis_results['weekly_production_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_yearly_production_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_yearly_prod_bar3d_subheader_switcher", "🗓️ Jahresproduktion – Simulierte 3D-Balken"))
    month_labels=get_text(texts,"month_names_short_list","Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels)!=12: month_labels=["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
    production_data_raw=analysis_results.get('monthly_productions_sim',[])
    if not isinstance(production_data_raw,list) or len(production_data_raw)!=12:
        st.warning(get_text(texts,"viz_data_missing_monthly_prod_switcher","Monatliche Produktionsdaten für Jahresdiagramm nicht verfügbar."))
        analysis_results['yearly_production_switcher_chart_bytes']=None; fig_empty=go.Figure(); fig_empty.update_layout(title=get_text(texts,"viz_data_unavailable_title","Daten nicht verfügbar")); _apply_custom_style_to_fig(fig_empty,viz_settings,"fallback_chart"); st.plotly_chart(fig_empty,use_container_width=True,key="analysis_yearly_prod_switcher_fallback_key_v6_final"); return
    production_data=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in production_data_raw]
    fig=go.Figure()
    primary_color_hex=viz_settings.get("primary_chart_color","#1f77b4")
    try:
        rgb_primary_norm = colors.HexColor(primary_color_hex).rgb()
        base_h,base_l,base_s=colorsys.rgb_to_hls(rgb_primary_norm[0], rgb_primary_norm[1], rgb_primary_norm[2])
    except:
        r_fb, g_fb, b_fb = (0.121, 0.466, 0.705); base_h,base_l,base_s=colorsys.rgb_to_hls(r_fb, g_fb, b_fb)
    for i,p_val in enumerate(production_data):
        current_hue=(base_h+(i/12.0)*0.3)%1.0
        r_bar,g_bar,b_bar=colorsys.hls_to_rgb(current_hue,base_l,base_s)
        bar_color_plotly = f'rgb({int(r_bar*255)}, {int(g_bar*255)}, {int(b_bar*255)})'
        r_marker,g_marker,b_marker=colorsys.hls_to_rgb(current_hue,max(0,base_l*0.6),base_s)
        marker_color_plotly = f'rgb({int(r_marker*255)}, {int(g_marker*255)}, {int(b_marker*255)})'
        fig.add_trace(go.Scatter3d(x=[i,i],y=[0,0],z=[0,p_val],mode='lines',line=dict(width=25,color=bar_color_plotly),name=month_labels[i],text=f"{month_labels[i]}: {p_val:.0f} kWh",hoverinfo='text'))
        fig.add_trace(go.Scatter3d(x=[i],y=[0],z=[p_val],mode='markers',marker=dict(size=4,color=marker_color_plotly),hoverinfo='skip'))
    fig.update_layout(title=get_text(texts,"viz_yearly_prod_bar3d_title_switcher","Jährliche PV-Produktion nach Monaten (sim. 3D-Balken)"),scene=dict(xaxis=dict(title='Monat',tickvals=list(range(12)),ticktext=month_labels),yaxis=dict(title='',showticklabels=False,range=[-0.5,0.5]),zaxis=dict(title='kWh')),margin=dict(l=10,r=10,t=50,b=10),showlegend=True)
    _apply_custom_style_to_fig(fig,viz_settings,"yearly_production_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_yearly_prod_switcher_key_v6_final")
    analysis_results['yearly_production_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_project_roi_matrix_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_project_roi_matrix_switcher", "📈 Projektrendite – Matrixdarstellung (Illustrativ)"))
    total_investment_netto_val = analysis_results.get('total_investment_netto', 0.0)
    if not isinstance(total_investment_netto_val, (int,float)) or total_investment_netto_val <= 0: total_investment_netto_val = 10000.0
    invest_options = np.array([val for val in [total_investment_netto_val * f for f in [0.8, 1.0, 1.2]] if val is not None and val > 0])
    if len(invest_options) == 0: invest_options = np.array([8000, 10000, 12000])
    sim_period_eff_val = analysis_results.get('simulation_period_years_effective', 0)
    if not isinstance(sim_period_eff_val, int) or sim_period_eff_val <=0: sim_period_eff_val = 20
    laufzeit_options = np.array([max(5, val) for val in [sim_period_eff_val - 5, sim_period_eff_val, sim_period_eff_val + 5] if val is not None])
    if len(laufzeit_options) == 0 : laufzeit_options = np.array([15,20,25])
    annual_financial_benefit_year1_val = analysis_results.get('annual_financial_benefit_year1', 0.0)
    if not isinstance(annual_financial_benefit_year1_val, (int,float)) or annual_financial_benefit_year1_val <=0: annual_financial_benefit_year1_val = 700.0
    ROI_matrix = np.array([ [((annual_financial_benefit_year1_val * t - i) / i) * 100 if i > 0 else 0 for i in invest_options] for t in laufzeit_options ])
    selected_palette = viz_settings.get("default_color_palette","Viridis"); valid_continuous_scales = ['Viridis','Blues','Cividis','Earth','Electric','Greens','Greys','Hot','Jet','Plotly3','RdBu','Solar','Turbo']
    color_scale_name = selected_palette if selected_palette in valid_continuous_scales else "Viridis"
    fig = go.Figure(data=[go.Surface(z=ROI_matrix, x=invest_options, y=laufzeit_options, colorscale=color_scale_name)])
    fig.update_layout(title=get_text(texts, "viz_project_roi_matrix_title_switcher", "Illustrative Projektrendite-Matrix"), scene=dict(xaxis_title='Investitionssumme (€)', yaxis_title='Laufzeit (Jahre)', zaxis_title='Gesamtrendite (%)'), margin=dict(l=0,r=0,b=0,t=50))
    _apply_custom_style_to_fig(fig, viz_settings, "project_roi_matrix_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_project_roi_matrix_switcher_key_v6_final")
    analysis_results['project_roi_matrix_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

def render_feed_in_revenue_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_feed_in_revenue_switcher", "💰 Einnahmen aus Einspeisung – Monatsverlauf (Jahr 1)"))
    month_labels = get_text(texts,"month_names_short_list","Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels)!=12: month_labels=["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
    monthly_feed_in_kwh_raw=analysis_results.get('monthly_feed_in_kwh',[])
    feed_in_tariff_eur_kwh_raw=analysis_results.get('einspeiseverguetung_eur_per_kwh', 0.081)
    if not isinstance(monthly_feed_in_kwh_raw,list) or len(monthly_feed_in_kwh_raw)!=12:
        st.warning(get_text(texts,"viz_data_missing_feed_in_revenue_switcher","Monatliche Einspeisedaten nicht verfügbar.")); analysis_results['feed_in_revenue_switcher_chart_bytes']=None; return
    monthly_feed_in_kwh=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in monthly_feed_in_kwh_raw]
    feed_in_tariff_eur_kwh=float(feed_in_tariff_eur_kwh_raw) if isinstance(feed_in_tariff_eur_kwh_raw,(int,float)) and not math.isnan(feed_in_tariff_eur_kwh_raw) and not math.isinf(feed_in_tariff_eur_kwh_raw) else 0.081
    einnahmen=[kwh*feed_in_tariff_eur_kwh for kwh in monthly_feed_in_kwh]
    fig=go.Figure()
    line_color = viz_settings.get("primary_chart_color", "dodgerblue")
    fig.add_trace(go.Scatter3d(x=month_labels,y=[feed_in_tariff_eur_kwh*100]*12,z=einnahmen,mode='lines+markers',name=f"Tarif {feed_in_tariff_eur_kwh*100:.1f} ct/kWh",line=dict(color=line_color),marker=dict(size=5, color=line_color)))
    fig.update_layout(title=get_text(texts,"viz_feed_in_revenue_title_switcher","Monatliche Einspeisevergütung (Jahr 1)"),scene=dict(xaxis_title='Monat',yaxis_title='Tarif (ct/kWh)',zaxis_title='Einnahmen (€)'),margin=dict(l=0,r=0,b=0,t=50))
    _apply_custom_style_to_fig(fig,viz_settings,"feed_in_revenue_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_feed_in_revenue_switcher_key_v6_final")
    analysis_results['feed_in_revenue_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_production_vs_consumption_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_prod_vs_cons_switcher", "🔄 Verbrauch vs. Produktion – 3D-Overlay (Jahr 1)"))
    month_labels = get_text(texts,"month_names_short_list","Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    if len(month_labels)!=12: month_labels=["Jan","Feb","Mrz","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
    verbrauch_raw=analysis_results.get('monthly_consumption_sim',[]); produktion_raw=analysis_results.get('monthly_productions_sim',[])
    if not (isinstance(verbrauch_raw,list) and len(verbrauch_raw)==12 and isinstance(produktion_raw,list) and len(produktion_raw)==12):
        st.warning(get_text(texts,"viz_data_missing_prod_cons_switcher","Monatliche Verbrauchs- oder Produktionsdaten nicht verfügbar.")); analysis_results['prod_vs_cons_switcher_chart_bytes']=None; return
    verbrauch=[float(v) if isinstance(v,(int,float)) and not math.isnan(v) and not math.isinf(v) else 0.0 for v in verbrauch_raw]
    produktion=[float(p) if isinstance(p,(int,float)) and not math.isnan(p) and not math.isinf(p) else 0.0 for p in produktion_raw]
    fig=go.Figure()
    cons_color = viz_settings.get("secondary_chart_color", "red")
    prod_color = viz_settings.get("primary_chart_color", "green")
    fig.add_trace(go.Scatter3d(x=month_labels,y=[0]*12,z=verbrauch,mode='lines+markers',name='Verbrauch (kWh)',line=dict(color=cons_color)))
    fig.add_trace(go.Scatter3d(x=month_labels,y=[0.1]*12,z=produktion,mode='lines+markers',name='Produktion (kWh)',line=dict(color=prod_color)))
    fig.update_layout(title=get_text(texts,"viz_prod_vs_cons_title_switcher","Monatlicher Verbrauch vs. Produktion (Jahr 1)"),scene=dict(xaxis_title='Monat',yaxis=dict(title='',showticklabels=False,range=[-0.5,0.5]),zaxis_title='kWh'),margin=dict(l=0,r=0,b=0,t=50))
    _apply_custom_style_to_fig(fig,viz_settings,"prod_vs_cons_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_prod_vs_cons_switcher_key_v6_final")
    analysis_results['prod_vs_cons_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_tariff_cube_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_tariff_cube_switcher", "⚖️ Tarifvergleich – Anbieter als 3D-Balken (Illustrativ)"))
    anbieter=['Aktuell','PV-Strom','Alternativ A','Alternativ B']
    aktueller_preis_kwh=float(analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh',0.30))
    lcoe_raw=analysis_results.get('lcoe_euro_per_kwh',0.12)
    lcoe = float(lcoe_raw) if isinstance(lcoe_raw, (int,float)) and not math.isinf(lcoe_raw) and not math.isnan(lcoe_raw) else 0.12
    jahresverbrauch=float(analysis_results.get('total_consumption_kwh_yr',3500.0))
    if jahresverbrauch <= 0: jahresverbrauch = 3500.0
    grundgebuehr=[60,0,80,70]
    arbeitspreis=[aktueller_preis_kwh,lcoe,aktueller_preis_kwh*0.95,aktueller_preis_kwh*1.05]
    gesamt=[g+a*jahresverbrauch for g,a in zip(grundgebuehr,arbeitspreis)]
    fig=go.Figure()
    color_sequence = viz_settings.get("colorway", px.colors.qualitative.Plotly)
    if not color_sequence or len(color_sequence) < len(anbieter):
        color_sequence = px.colors.qualitative.Plotly
    for i,(anbieter_name,cost) in enumerate(zip(anbieter,gesamt)):
        fig.add_trace(go.Scatter3d(x=[i,i],y=[0,0],z=[0,cost],mode='lines',line=dict(width=30,color=color_sequence[i%len(color_sequence)]),name=f"{anbieter_name} ({arbeitspreis[i]:.2f}€/kWh + {grundgebuehr[i]}€ GG)"))
    fig.update_layout(
        title=get_text(texts,"viz_tariff_cube_title_switcher",f"Illustrativer Tarifvergleich bei {jahresverbrauch:.0f} kWh/Jahr"),
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
                          "🌍 CO₂-Ersparnis vs. Monetärer Wert (Simuliert)"))

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

    # ─── 3D-Balkendiagramm als Scatter3d ────────────────────────────────────────
    import plotly.graph_objects as go
    import plotly.express as px

    selected_palette = viz_settings.get("default_color_palette", "Viridis")
    valid_scales = ['Greens', 'Blues', 'Viridis', 'Plotly3', 'Solar', 'Hot']
    scale_co2 = selected_palette if selected_palette in valid_scales else "Greens"
    scale_value = "Blues"

    fig = go.Figure()

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
                          "CO₂-Einsparnis und simulierter monetärer Wert über Zeit"),
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
    # ───────────────────────────────────────────────────────────────────────────

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

def render_co2_savings_value_switcher(analysis_results: Dict[str, Any],
                                        texts: Dict[str, str],
                                        viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts,
                          "viz_co2_savings_value_switcher",
                          "🌍 CO₂-Ersparnis vs. Monetärer Wert (Simuliert)"))

    try:
        from pv_visuals import render_co2_savings_visualization
        render_co2_savings_visualization(analysis_results, texts)
        st.markdown("---")
    except ImportError as e:
        st.warning(f"CO₂-Visualisierung konnte nicht geladen werden: {e}")

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

    import plotly.graph_objects as go
    import plotly.express as px

    selected_palette = viz_settings.get("default_color_palette", "Viridis")
    valid_scales = ['Greens', 'Blues', 'Viridis', 'Plotly3', 'Solar', 'Hot']
    scale_co2 = selected_palette if selected_palette in valid_scales else "Greens"
    scale_value = "Blues"

    fig = go.Figure()

    for xi, zi in zip(jahre_axis, co2_savings_tonnes_per_year):
        fig.add_trace(go.Scatter3d(
            x=[xi, xi], y=[0, 0], z=[0, zi], mode='lines',
            line=dict(color=px.colors.sequential.__getattribute__(scale_co2)[-1], width=12),
            showlegend=False
        ))
    fig.add_trace(go.Scatter3d(
        x=jahre_axis, y=[0] * years_effective, z=co2_savings_tonnes_per_year,
        mode='markers',
        marker=dict(color=co2_savings_tonnes_per_year, colorscale=scale_co2, size=6, showscale=False),
        name='CO₂-Einsparung (t)'
    ))

    for xi, zi in zip(jahre_axis, wert_co2_eur_per_year):
        fig.add_trace(go.Scatter3d(
            x=[xi, xi], y=[1, 1], z=[0, zi], mode='lines',
            line=dict(color=px.colors.sequential.__getattribute__(scale_value)[-1], width=12),
            showlegend=False
        ))
    fig.add_trace(go.Scatter3d(
        x=jahre_axis, y=[1] * years_effective, z=wert_co2_eur_per_year,
        mode='markers',
        marker=dict(color=wert_co2_eur_per_year, colorscale=scale_value, size=6, showscale=True, colorbar=dict(title='Wert (€)')),
        name='Monetärer Wert (€)'
    ))

    fig.update_layout(
        title=dict(text=get_text(texts, "viz_co2_savings_value_title_switcher", "CO₂-Ersparnis und simulierter monetärer Wert über Zeit"), font=dict(size=16)),
        scene=dict(
            xaxis=dict(title='Jahr'),
            yaxis=dict(title='Kategorie', tickvals=[0, 1], ticktext=['CO₂-Ersparnis', 'Monetärer Wert']),
            zaxis=dict(title='Menge'),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        margin=dict(l=0, r=0, b=0, t=60),
        legend=dict(orientation='h', yanchor='bottom', y=0.02, xanchor='center', x=0.5),
        template='plotly_white'
    )

    _apply_custom_style_to_fig(fig, viz_settings, "co2_savings_value_switcher")
    st.plotly_chart(fig, use_container_width=True, key="analysis_co2_savings_value_switcher_key_v6_final")
    analysis_results['co2_savings_value_switcher_chart_bytes'] = _export_plotly_fig_to_bytes(fig, texts)

    col1, col2, col3 = st.columns(3)
    with col1:
        total_co2_savings = sum(co2_savings_tonnes_per_year)
        st.metric(label="Gesamte CO₂-Einsparung", value=f"{total_co2_savings:.1f} Tonnen", help=f"Über {years_effective} Jahre hinweg")
    with col2:
        total_co2_value = sum(wert_co2_eur_per_year)
        st.metric(label="Gesamtwert CO₂-Einsparung", value=f"{total_co2_value:.0f} €", help="Basierend auf prognostizierter CO₂-Preisentwicklung")
    with col3:
        avg_annual_co2 = total_co2_savings / years_effective if years_effective > 0 else 0
        st.metric(label="Durchschnitt pro Jahr", value=f"{avg_annual_co2:.2f} Tonnen", help="Durchschnittliche jährliche CO₂-Einsparung")

def render_investment_value_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_investment_value_subheader_switcher", "🛠️ Investitionsnutzwert – Wirkung von Maßnahmen (Illustrativ)"))
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
    fig=go.Figure()
    selected_palette = viz_settings.get("default_color_palette","Viridis"); valid_continuous_scales = ['Viridis','Blues','Plotly3','Solar','Hot']
    marker_colorscale = selected_palette if selected_palette in valid_continuous_scales else "Viridis"
    fig.add_trace(go.Scatter3d(x=massnahmen_labels,y=kosten_abs,z=effizienz_roi,mode='markers+text',marker=dict(size=12,color=effizienz_roi,colorscale=marker_colorscale,showscale=True,colorbar_title_text='Gesamtrendite (%)'),text=[f"{eff:.0f}%" for eff in effizienz_roi],textposition='middle right',customdata=np.transpose([kosten_abs,nutzwert_simuliert_abs,effizienz_roi]),hovertemplate="<b>Maßnahme:</b> %{x}<br><b>Kosten:</b> %{customdata[0]:.0f} €<br><b>Nutzen:</b> %{customdata[1]:.0f} €<br><b>Rendite:</b> %{customdata[2]:.0f}%<extra></extra>"))
    fig.update_layout(title=get_text(texts,"viz_investment_value_title_switcher","Illustrativer Investitionsnutzwert"),scene=dict(xaxis_title='Maßnahme',yaxis_title='Kosten (€)',zaxis_title='Gesamtrendite (%)'),margin=dict(l=0,r=0,b=0,t=60))
    _apply_custom_style_to_fig(fig,viz_settings,"investment_value_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_investment_value_switcher_key_v6_final")
    analysis_results['investment_value_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_storage_effect_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_storage_effect_subheader_switcher", "🔋 Speicherwirkung – Kapazität vs. Nutzen (Illustrativ)"))
    current_storage_cap_kwh_raw = analysis_results.get('selected_storage_storage_power_kw'); include_storage_flag = analysis_results.get('include_storage', False)
    current_storage_cap_kwh = float(current_storage_cap_kwh_raw if isinstance(current_storage_cap_kwh_raw,(int,float)) else 0.0) if include_storage_flag else 0.0
    total_consumption_kwh_yr_raw = analysis_results.get('total_consumption_kwh_yr'); aktueller_strompreis_raw = analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh')
    stromkosten_ohne_pv_jahr1_val = (float(total_consumption_kwh_yr_raw if isinstance(total_consumption_kwh_yr_raw,(int,float)) else 3500.0) * float(aktueller_strompreis_raw if isinstance(aktueller_strompreis_raw,(int,float)) else 0.30))
    max_potential_storage_benefit_eur = stromkosten_ohne_pv_jahr1_val * 0.4; denominator_heuristic = (10*(1-np.exp(-0.3*10)))
    scaling_factor_heuristic = (max_potential_storage_benefit_eur/denominator_heuristic) if max_potential_storage_benefit_eur > 0 and denominator_heuristic != 0 else 150.0
    kapazitaet_range_kwh = np.linspace(0,20,30); nutzwert_illustrativ_eur = kapazitaet_range_kwh*(1-np.exp(-0.3*kapazitaet_range_kwh))*scaling_factor_heuristic
    nutzwert_illustrativ_eur = np.nan_to_num(nutzwert_illustrativ_eur,nan=0.0,posinf=0.0,neginf=0.0)
    fig=go.Figure()
    line_color = viz_settings.get("primary_chart_color", "purple")
    marker_color = viz_settings.get("secondary_chart_color", "red")
    fig.add_trace(go.Scatter3d(x=kapazitaet_range_kwh,y=[0]*len(kapazitaet_range_kwh),z=nutzwert_illustrativ_eur,mode='lines+markers',line=dict(color=line_color,width=4),name='Simulierter Nutzenverlauf'))
    if current_storage_cap_kwh > 0:
        current_nutzwert_on_curve_raw = current_storage_cap_kwh*(1-np.exp(-0.3*current_storage_cap_kwh))*scaling_factor_heuristic
        current_nutzwert_on_curve = np.nan_to_num(current_nutzwert_on_curve_raw,nan=0.0,posinf=0.0,neginf=0.0)
        fig.add_trace(go.Scatter3d(x=[current_storage_cap_kwh],y=[0],z=[current_nutzwert_on_curve],mode='markers',marker=dict(color=marker_color,size=10,symbol='x'),name=f'Ausgew. Speicher ({current_storage_cap_kwh:.1f} kWh)'))
    fig.update_layout(title=get_text(texts,"viz_storage_effect_title_switcher","Illustrative Speicherwirkung"),scene=dict(xaxis_title='Speicherkapazität (kWh)',yaxis_title='',zaxis_title='Jährl. Einsparpotenzial (€, illustrativ)'),margin=dict(l=0,r=0,b=0,t=50))
    _apply_custom_style_to_fig(fig,viz_settings,"storage_effect_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_storage_effect_switcher_key_v6_final")
    analysis_results['storage_effect_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_selfuse_stack_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_selfuse_stack_subheader_switcher", "🏘️ Eigenverbrauch vs. Einspeisung – Jährlicher 3D Stack"))
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
    fig=go.Figure()
    bar_width_yz=0.4; color_ev = viz_settings.get("primary_chart_color", "blue"); color_feedin = viz_settings.get("secondary_chart_color", "orange")
    for i,year_label in enumerate(jahre_sim_labels):
        fig.add_trace(go.Scatter3d(x=[year_label,year_label],y=[0,0],z=[0,eigen_sim_kwh[i]],mode='lines',line=dict(width=15,color=color_ev),name='Eigenverbrauch (kWh)' if i==0 else None,legendgroup='Eigenverbrauch',showlegend=(i==0),hoverinfo="x+z"))
        fig.add_trace(go.Scatter3d(x=[year_label,year_label],y=[bar_width_yz*1.5,bar_width_yz*1.5],z=[0,einspeisung_sim_kwh[i]],mode='lines',line=dict(width=15,color=color_feedin),name='Einspeisung (kWh)' if i==0 else None,legendgroup='Einspeisung',showlegend=(i==0),hoverinfo="x+z"))
    fig.update_layout(title=get_text(texts,"viz_selfuse_stack_title_switcher","Jährlicher Eigenverbrauch vs. Einspeisung (Simuliert)"),scene=dict(xaxis_title='Simulationsjahr',yaxis_title='Kategorie',yaxis=dict(tickvals=[0,bar_width_yz*1.5],ticktext=['Eigenverbrauch','Einspeisung'],range=[-0.5,bar_width_yz*1.5+0.5]),zaxis_title='Energie (kWh)'),margin=dict(l=0,r=0,b=0,t=60),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    _apply_custom_style_to_fig(fig,viz_settings,"selfuse_stack_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_selfuse_stack_switcher_key_v6_final")
    analysis_results['selfuse_stack_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_cost_growth_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_cost_growth_subheader_switcher", "📈 Stromkostensteigerung – 3D Fläche"))
    years_effective=int(analysis_results.get('simulation_period_years_effective',0))
    if years_effective<=0: st.info(get_text(texts,"viz_data_insufficient_cost_growth","Simulationsdauer 0.")); analysis_results['cost_growth_switcher_chart_bytes']=None; return
    jahre_axis=np.arange(1,years_effective+1)
    basispreis_kwh=float(analysis_results.get('aktueller_strompreis_fuer_hochrechnung_euro_kwh',0.30))
    current_increase_rate_percent=float(analysis_results.get('electricity_price_increase_rate_effective_percent',3.0))
    szenarien_prozent_vals=sorted(list(set(round(s,1) for s in [max(0,current_increase_rate_percent-1.5),current_increase_rate_percent,current_increase_rate_percent+1.5])))
    fig=go.Figure(); z_surface=[]
    color_sequence = viz_settings.get("colorway", px.colors.qualitative.Plotly)
    if not color_sequence or len(color_sequence) < len(szenarien_prozent_vals) : color_sequence = px.colors.qualitative.Plotly
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
    fig.update_layout(title=get_text(texts,"viz_cost_growth_title_switcher","Entwicklung Strompreis pro kWh (Szenarien)"),scene=dict(xaxis_title='Simulationsjahr',yaxis_title='Jährliche Steigerung (%)',zaxis_title='Strompreis (€/kWh)',yaxis=dict(tickvals=szenarien_prozent_vals,ticktext=[f"{s:.1f}%" for s in szenarien_prozent_vals])),margin=dict(l=0,r=0,b=0,t=60))
    _apply_custom_style_to_fig(fig,viz_settings,"cost_growth_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_cost_growth_switcher_key_v6_final")
    analysis_results['cost_growth_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_selfuse_ratio_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_selfuse_ratio_subheader_switcher", "🎯 Eigenverbrauchsgrad – Monatliche Bubble View (Jahr 1)"))
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
    fig=go.Figure()
    color_scale_name = viz_settings.get("default_color_palette","YlGnBu"); valid_continuous_scales = ['YlGnBu','Blues','Greens','Viridis','Plotly3']
    marker_colorscale = color_scale_name if color_scale_name in valid_continuous_scales else "YlGnBu"
    fig.add_trace(go.Scatter3d(x=month_labels,y=[0]*12,z=ev_monat_grad,mode='markers+text',marker=dict(size=bubble_sizes,color=ev_monat_grad,colorscale=marker_colorscale,showscale=True,colorbar_title_text='Anteil (%)'),text=[f"{v:.0f}%" for v in ev_monat_grad],textposition='top center',customdata=ev_monat_kwh,hovertemplate="<b>Monat:</b> %{x}<br><b>Eigenversorgungsgrad:</b> %{z:.0f}%<br><b>Abs. Eigenverbrauch:</b> %{customdata:.0f} kWh<extra></extra>"))
    fig.update_layout(title=get_text(texts,"viz_selfuse_ratio_title_switcher","Monatlicher Eigenversorgungsgrad (Autarkiegrad des Monats) - Jahr 1"),scene=dict(xaxis_title='Monat',yaxis_title='',zaxis_title='Eigenversorgungsgrad des Monats (%)'),margin=dict(l=0,r=0,b=0,t=60))
    _apply_custom_style_to_fig(fig,viz_settings,"selfuse_ratio_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_selfuse_ratio_switcher_key_v6_final")
    analysis_results['selfuse_ratio_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_roi_comparison_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_roi_comparison_subheader_switcher", "🏆 ROI-Vergleich – Investitionen in 3D (Illustrativ)"))
    curr_proj_name=get_text(texts,"current_project_label_switcher","Aktuelles Projekt"); curr_invest_raw=analysis_results.get('total_investment_netto'); curr_benefit_raw=analysis_results.get('annual_financial_benefit_year1')
    curr_invest=float(curr_invest_raw if isinstance(curr_invest_raw,(int,float)) and curr_invest_raw>0 else 12000.0)
    curr_benefit=float(curr_benefit_raw if isinstance(curr_benefit_raw,(int,float)) else 800.0)
    labels=[curr_proj_name,'Alternativ A (Günstiger)','Alternativ B (Premium)']; invest_opts=[curr_invest,curr_invest*0.8,curr_invest*1.3]
    benefit_opts=[curr_benefit,curr_benefit*0.75,curr_benefit*1.2]; roi_opts=[(b/i*100) if i>0 else 0 for i,b in zip(invest_opts,benefit_opts)]
    fig=go.Figure()
    color_scale_name = viz_settings.get("default_color_palette","RdYlGn"); valid_continuous_scales = ['RdYlGn','Viridis','Plotly3','Solar','Hot']
    marker_colorscale = color_scale_name if color_scale_name in valid_continuous_scales else "RdYlGn"
    fig.add_trace(go.Scatter3d(x=labels,y=invest_opts,z=roi_opts,mode='markers+text',marker=dict(size=12,color=roi_opts,colorscale=marker_colorscale,showscale=True,colorbar_title_text='Jährl. ROI (%)'),text=[f"{r:.1f}%" for r in roi_opts],textposition="middle right",customdata=np.transpose([invest_opts,benefit_opts,roi_opts]),hovertemplate="<b>Projekt:</b> %{x}<br><b>Investition:</b> %{customdata[0]:.0f} €<br><b>Jährl. Nutzen:</b> %{customdata[1]:.0f} €<br><b>Jährl. ROI:</b> %{customdata[2]:.1f}%<extra></extra>"))
    fig.update_layout(title=get_text(texts,"viz_roi_comparison_title_switcher","Illustrativer ROI-Vergleich von PV-Anlagen-Szenarien"),scene=dict(xaxis_title="Projekt-Szenario",yaxis_title="Investition (€)",zaxis_title="Jährlicher ROI (%)"),margin=dict(l=0,r=0,b=0,t=60))
    _apply_custom_style_to_fig(fig,viz_settings,"roi_comparison_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_roi_comparison_switcher_key_v6_final")
    analysis_results['roi_comparison_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_scenario_comparison_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_scenario_comp_subheader_switcher", "⚖️ Szenarienvergleich – Invest/Ertrag/Bonus (Illustrativ)"))
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
    fig=go.Figure()
    for i,cat_name in enumerate(cat_names):
        cat_vals=cat_data[cat_name]
        for j,szenario_label in enumerate(labels):
            fig.add_trace(go.Scatter3d(x=[szenario_label,szenario_label],y=[i,i],z=[0,cat_vals[j]],mode='lines',line=dict(width=25,color=color_sequence[i%len(color_sequence)]),name=cat_name if j==0 else None,legendgroup=cat_name,showlegend=(j==0),hoverinfo='text',text=f"{szenario_label}<br>{cat_name}: {cat_vals[j]:.0f} €"))
    fig.update_layout(title=get_text(texts,"viz_scenario_comp_title_switcher","Illustrativer Szenarienvergleich"),scene=dict(xaxis_title='Szenario',yaxis_title='Kategorie',yaxis=dict(tickvals=list(range(len(cat_names))),ticktext=cat_names,range=[-0.5,len(cat_names)-0.5]),zaxis_title='Betrag (€)'),margin=dict(l=0,r=0,b=0,t=60),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    _apply_custom_style_to_fig(fig,viz_settings,"scenario_comparison_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_scenario_comp_switcher_key_v6_final")
    analysis_results['scenario_comparison_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_tariff_comparison_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_tariff_comp_subheader_switcher", "💡 Vorher/Nachher – Monatliche Stromkosten (Jahr 1)"))
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
    fig=go.Figure(); bar_width_yz=0.4
    color_vorher = viz_settings.get("secondary_chart_color_rgba", "rgba(230,50,50,0.8)")
    color_nachher = viz_settings.get("primary_chart_color_rgba", "rgba(50,200,50,0.8)")
    for i,month_label in enumerate(month_labels):
        fig.add_trace(go.Scatter3d(x=[month_label,month_label],y=[0,0],z=[0,kosten_vorher[i]],mode='lines',line=dict(width=20,color=color_vorher),name='Kosten Vorher' if i==0 else None,legendgroup='Vorher',showlegend=(i==0),hoverinfo='text',text=f"{month_label} Vorher: {kosten_vorher[i]:.2f} €"))
        fig.add_trace(go.Scatter3d(x=[month_label,month_label],y=[bar_width_yz,bar_width_yz],z=[0,kosten_nachher[i]],mode='lines',line=dict(width=20,color=color_nachher),name='Kosten Nachher' if i==0 else None,legendgroup='Nachher',showlegend=(i==0),hoverinfo='text',text=f"{month_label} Nachher: {kosten_nachher[i]:.2f} €"))
    fig.update_layout(title=get_text(texts,"viz_tariff_comp_title_switcher","Monatliche Stromkosten: Vorher vs. Nachher (Jahr 1)"),scene=dict(xaxis_title='Monat',yaxis_title='Szenario',yaxis=dict(tickvals=[0,bar_width_yz],ticktext=['Ohne PV','Mit PV (Netzbezug)'],range=[-0.5,bar_width_yz+0.5]),zaxis_title='Stromkosten (€)'),margin=dict(l=0,r=0,b=0,t=60),legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01))
    _apply_custom_style_to_fig(fig,viz_settings,"tariff_comparison_switcher")
    st.plotly_chart(fig,use_container_width=True,key="analysis_tariff_comp_switcher_key_v6_final")
    analysis_results['tariff_comparison_switcher_chart_bytes']=_export_plotly_fig_to_bytes(fig,texts)

def render_income_projection_switcher(analysis_results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    st.subheader(get_text(texts, "viz_income_proj_subheader_switcher", "💸 Einnahmen/Ersparnisprognose – Dynamischer Verlauf"))
    years_effective=int(analysis_results.get('simulation_period_years_effective',0))
    if years_effective<=0: st.info(get_text(texts,"viz_data_insufficient_income_proj","Simulationsdauer 0.")); analysis_results['income_projection_switcher_chart_bytes']=None; return
    jahre_axis=np.arange(0,years_effective+1); annual_benefits_raw=analysis_results.get('annual_benefits_sim',[])
    annual_benefits=[float(b) for b in annual_benefits_raw if isinstance(b,(int,float)) and not math.isnan(b) and not math.isinf(b)]
    if not (annual_benefits and len(annual_benefits)==years_effective):
        st.info(get_text(texts,"viz_data_insufficient_income_proj_benefits",f"Daten für 'annual_benefits_sim' unvollständig.")); analysis_results['income_projection_switcher_chart_bytes']=None; return
    kum_vorteile=[0.0]+list(np.cumsum([val or 0 for val in annual_benefits]))
    fig=go.Figure()
    line_color = viz_settings.get("primary_chart_color", "mediumseagreen")
    fig.add_trace(go.Scatter3d(x=jahre_axis,y=[0]*len(jahre_axis),z=kum_vorteile,mode='lines+markers',line=dict(color=line_color,width=4),marker=dict(size=4, color=line_color),name='Kumulierte Vorteile'))
    fig.update_layout(title=get_text(texts,"viz_income_proj_title_switcher","Prognose: Kumulierte Einnahmen & Ersparnisse"),scene=dict(xaxis_title='Simulationsjahr',yaxis_title='',zaxis_title='Kumulierte Vorteile (€)'),margin=dict(l=0,r=0,b=0,t=50))
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
            try:
                dynamic_color_list = getattr(px.colors.qualitative, palette_name, None)
            except AttributeError:
                pass
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

def render_pricing_modifications_ui():
    st.markdown("## Preisänderungen (Rabatte, Zuschläge, Sondervereinbarungen)")
    if 'pricing_modifications' not in st.session_state:
        st.session_state.pricing_modifications = {
            "discount": 0.0, "surcharge": 0.0, "special_agreements": "",
            "rebates": 0.0, "special_costs": 0.0, "miscellaneous": 0.0,
            "descriptions": {"discount": "", "surcharge": "", "rebates": "", "special_costs": "", "miscellaneous": ""}
        }
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.slider("Rabatt (%)", 0.0, 100.0, key="pricing_modifications_discount_slider", step=0.1, help="Prozentualer Rabatt auf den Gesamtpreis.")
        st.text_area("Beschreibung für Rabatt", key="pricing_modifications_descriptions_discount_text", help="Beschreibung oder Details zum Rabatt.")
    with col2:
        st.slider("Nachlässe (€)", 0.0, 10000.0, key="pricing_modifications_rebates_slider", step=10.0, help="Feste Nachlässe in Euro.")
        st.text_area("Beschreibung für Nachlässe", key="pricing_modifications_descriptions_rebates_text", help="Beschreibung oder Details zu den Nachlässen.")
    with col3:
        st.slider("Zuschlag (%)", 0.0, 100.0, key="pricing_modifications_surcharge_slider", step=0.1, help="Prozentualer Zuschlag auf den Gesamtpreis.")
        st.text_area("Beschreibung für Zuschlag", key="pricing_modifications_descriptions_surcharge_text", help="Beschreibung oder Details zum Zuschlag.")
    with col4:
        st.slider("Sonderkosten (€)", 0.0, 10000.0, key="pricing_modifications_special_costs_slider", step=10.0, help="Zusätzliche Sonderkosten in Euro.")
        st.text_area("Beschreibung für Sonderkosten", key="pricing_modifications_descriptions_special_costs_text", help="Beschreibung oder Details zu den Sonderkosten.")
    st.slider("Sonstiges (€)", 0.0, 10000.0, key="pricing_modifications_miscellaneous_slider", step=10.0, help="Sonstige Kosten oder Abzüge in Euro.")
    st.text_area("Beschreibung für Sonstiges", key="pricing_modifications_descriptions_miscellaneous_text", help="Beschreibung oder Details zu Sonstigem.")
    st.text_area("Sondervereinbarungen", key="pricing_modifications_special_agreements_text", help="Zusätzliche Informationen oder Vereinbarungen, die im Angebot berücksichtigt werden sollen.")
    st.markdown("### Live-Kosten-Vorschau")
    calc_results = st.session_state.get('calculation_results', {})
    base_cost = calc_results.get('base_matrix_price_netto', 0.0)
    if base_cost == 0.0: base_cost = st.session_state.get('base_matrix_price_netto', 0.0)
    discount_percent = st.session_state.get('pricing_modifications_discount_slider', 0.0)
    rebates_eur = st.session_state.get('pricing_modifications_rebates_slider', 0.0)
    surcharge_percent = st.session_state.get('pricing_modifications_surcharge_slider', 0.0)
    special_costs_eur = st.session_state.get('pricing_modifications_special_costs_slider', 0.0)
    miscellaneous_eur = st.session_state.get('pricing_modifications_miscellaneous_slider', 0.0)
    discount_amount = base_cost * (discount_percent / 100.0)
    total_rabatte_nachlaesse = discount_amount + rebates_eur
    price_after_discounts = base_cost - total_rabatte_nachlaesse
    surcharge_amount = price_after_discounts * (surcharge_percent / 100.0)
    total_aufpreise_zuschlaege = surcharge_amount + special_costs_eur + miscellaneous_eur
    final_price = price_after_discounts + total_aufpreise_zuschlaege
    st.write(f"**Grundpreis:** {base_cost:,.2f} €")
    st.write(f"**Summe Rabatte / Nachlässe:** -{total_rabatte_nachlaesse:,.2f} €")
    st.write(f"**Summe Aufpreise / Zuschläge:** +{total_aufpreise_zuschlaege:,.2f} €")
    st.write(f"**Endpreis (inkl. Zuschläge, Rabatte, usw.):** {final_price:,.2f} €")
    st.session_state['live_pricing_calculations'] = {
        'base_cost': base_cost, 'total_rabatte_nachlaesse': total_rabatte_nachlaesse,
        'total_aufpreise_zuschlaege': total_aufpreise_zuschlaege, 'final_price': final_price,
        'discount_amount': discount_amount, 'surcharge_amount': surcharge_amount, 'price_after_discounts': price_after_discounts
    }

# --- Haupt-Render-Funktion ---
def render_analysis(texts: Dict[str, str], results: Optional[Dict[str, Any]] = None) -> None:
    if not _ANALYSIS_DEPENDENCIES_AVAILABLE:
        st.error(get_text(texts,"analysis_module_critical_error"))
        return
    st.header(get_text(texts,"dashboard_header","Ergebnisse und Dashboard"))
    project_inputs = st.session_state.get("project_data",{})
    viz_settings = _get_visualization_settings()

    st.sidebar.subheader(get_text(texts, "analysis_interactive_settings_header", "Analyse-Parameter"))
    admin_defaults_gc = load_admin_setting('global_constants', {'simulation_period_years': 20, 'electricity_price_increase_annual_percent': 3.0})
    admin_default_sim_years = int(admin_defaults_gc.get('simulation_period_years', 20) or 20)
    admin_default_price_increase = float(admin_defaults_gc.get('electricity_price_increase_annual_percent', 3.0) or 3.0)
    current_sim_years_for_ui = admin_default_sim_years; current_price_increase_for_ui = admin_default_price_increase
    previous_calc_results = st.session_state.get("calculation_results", {})
    if results and isinstance(results, dict) and results.get('simulation_period_years_effective') is not None :
        current_sim_years_for_ui = int(results['simulation_period_years_effective'])
        current_price_increase_for_ui = float(results.get('electricity_price_increase_rate_effective_percent', admin_default_price_increase))
    elif previous_calc_results and previous_calc_results.get('simulation_period_years_effective') is not None:
        current_sim_years_for_ui = int(previous_calc_results['simulation_period_years_effective'])
        current_price_increase_for_ui = float(previous_calc_results.get('electricity_price_increase_rate_effective_percent', admin_default_price_increase))
    sim_duration_user_input = st.sidebar.number_input(get_text(texts,"analysis_sim_duration_label","Simulationsdauer (Jahre)"),min_value=1,max_value=50,value=current_sim_years_for_ui,step=1,key="analysis_sim_duration_input_v22_final_corrected")
    sim_price_increase_user_input = st.sidebar.number_input(get_text(texts,"analysis_sim_price_increase_label","Strompreissteigerung p.a. (%)"),min_value=0.0,max_value=20.0,value=current_price_increase_for_ui,step=0.1,format="%.1f",key="analysis_price_increase_input_v22_final_corrected")

    st.markdown("---")
    render_pricing_modifications_ui()
    st.markdown("---")

    if not project_inputs:
        st.info(get_text(texts, "analysis_no_project_data"));
        if 'st' in globals() and hasattr(st, 'session_state'): st.session_state["calculation_results"] = {}
        return
    calculation_errors_for_current_run: List[str] = []
    results_for_display = perform_calculations(project_inputs, texts, calculation_errors_for_current_run, simulation_duration_user=sim_duration_user_input, electricity_price_increase_user=sim_price_increase_user_input)
    if not results_for_display or not isinstance(results_for_display, dict):
        st.error(get_text(texts, 'calculation_no_result_info'));
        if 'st' in globals() and hasattr(st, 'session_state'): st.session_state["calculation_results"] = {}
        return
    chart_byte_keys = ['consumption_coverage_pie_chart_bytes','pv_usage_pie_chart_bytes','daily_production_switcher_chart_bytes','weekly_production_switcher_chart_bytes','yearly_production_switcher_chart_bytes','project_roi_matrix_switcher_chart_bytes','feed_in_revenue_switcher_chart_bytes','prod_vs_cons_switcher_chart_bytes','tariff_cube_switcher_chart_bytes','co2_savings_value_switcher_chart_bytes','investment_value_switcher_chart_bytes','storage_effect_switcher_chart_bytes','selfuse_stack_switcher_chart_bytes','cost_growth_switcher_chart_bytes','selfuse_ratio_switcher_chart_bytes','roi_comparison_switcher_chart_bytes','scenario_comparison_switcher_chart_bytes','tariff_comparison_switcher_chart_bytes','income_projection_switcher_chart_bytes','monthly_prod_cons_chart_bytes','cost_projection_chart_bytes','cumulative_cashflow_chart_bytes','yearly_production_chart_bytes','break-even_chart_bytes','amortisation_chart_bytes']
    for chart_key_init in chart_byte_keys: results_for_display.setdefault(chart_key_init, None)
    calc_errors_list=[err for err in results_for_display.get('calculation_errors',[]) if err];all_display_errors=list(set(calc_errors_list + calculation_errors_for_current_run))
    if all_display_errors:
        st.error(get_text(texts,'calculation_errors_header',""))
        for err_item in all_display_errors: st.warning(f"- {err_item}")
    else: st.success(get_text(texts,'calculation_no_errors_info',""))
    st.markdown("---")
    st.subheader(get_text(texts,"main_kpi_header","Wichtige Kennzahlen"))
    kpi_cols_row1=st.columns(3);kpi_cols_row2=st.columns(3)
    kpi_cols_row1[0].metric(label=get_text(texts,'total_investment_brutto'),value=format_kpi_value(results_for_display.get('total_investment_brutto'),"€",texts_dict=texts))
    kpi_cols_row1[1].metric(label=get_text(texts,'anlage_size_label'),value=format_kpi_value(results_for_display.get('anlage_kwp'),"kWp",texts_dict=texts))
    kpi_cols_row1[2].metric(label=get_text(texts,'annual_pv_production_kwh'),value=format_kpi_value(results_for_display.get('annual_pv_production_kwh'),"kWh",precision=0,texts_dict=texts))
    kpi_cols_row2[0].metric(label=get_text(texts,'self_supply_rate_percent','Autarkiegrad (%)'),value=format_kpi_value(results_for_display.get('self_supply_rate_percent'),"%",precision=1,texts_dict=texts))
    kpi_cols_row2[1].metric(label=get_text(texts,'annual_financial_benefit'),value=format_kpi_value(results_for_display.get('annual_financial_benefit_year1'),"€",texts_dict=texts))
    kpi_cols_row2[2].metric(label=get_text(texts,'amortization_time_years'),value=format_kpi_value(results_for_display.get("amortization_time_years"),"Jahre",texts_dict=texts))
    st.markdown("---")

    st.subheader(get_text(texts, "analysis_standard_charts_header", "Standard Analysediagramme"))
    _add_chart_controls("monthly_compare", texts, default_type="bar", supported_types=["bar", "line", "area"], viz_settings=viz_settings)
    fig_monthly_comp = _create_monthly_production_consumption_chart(results_for_display, texts, viz_settings, "monthly_compare")
    if fig_monthly_comp:
        st.plotly_chart(fig_monthly_comp, use_container_width=True, key="analysis_monthly_comp_chart_final_v8_corrected")
        results_for_display['monthly_prod_cons_chart_bytes'] = _export_plotly_fig_to_bytes(fig_monthly_comp, texts)
    else: st.info(get_text(texts, "no_data_for_monthly_comparison_chart_v3", "Daten für Monatsvergleich (Prod/Verbr) unvollständig."))

    _add_chart_controls("cost_projection", texts, default_type="line", supported_types=["line", "bar"], viz_settings=viz_settings)
    fig_cost_projection = _create_electricity_cost_projection_chart(results_for_display, texts, viz_settings, "cost_projection")
    if fig_cost_projection:
        st.plotly_chart(fig_cost_projection, use_container_width=True, key="analysis_cost_proj_chart_final_v8_corrected")
        results_for_display['cost_projection_chart_bytes'] = _export_plotly_fig_to_bytes(fig_cost_projection, texts)
    else: st.info(get_text(texts, "no_data_for_cost_projection_chart_v3", "Daten für Kostenhochrechnung unvollständig."))

    _add_chart_controls("cum_cashflow", texts, default_type="area", supported_types=["area", "line", "bar"], viz_settings=viz_settings)
    fig_cum_cf = _create_cumulative_cashflow_chart(results_for_display, texts, viz_settings, "cum_cashflow")
    if fig_cum_cf:
        st.plotly_chart(fig_cum_cf, use_container_width=True, key="analysis_cum_cashflow_chart_final_v8_corrected")
        results_for_display['cumulative_cashflow_chart_bytes'] = _export_plotly_fig_to_bytes(fig_cum_cf, texts)
    else: st.info(get_text(texts, "no_data_for_cumulative_cashflow_chart_v3", "Daten für kum. Cashflow unvollständig."))
    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        _render_consumption_coverage_pie(results_for_display, texts, viz_settings, "consumption_coverage_pie")
    with col_chart2:
        _render_pv_usage_pie(results_for_display, texts, viz_settings, "pv_usage_pie")
    st.markdown("---")

    st.subheader(get_text(texts,"analysis_switcher_charts_header_updated","Zusätzliche Visualisierungen (3D)"))
    render_daily_production_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_weekly_production_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_yearly_production_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_project_roi_matrix_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_feed_in_revenue_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_production_vs_consumption_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_tariff_cube_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_co2_savings_value_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_investment_value_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_storage_effect_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_selfuse_stack_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_cost_growth_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_selfuse_ratio_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_roi_comparison_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_scenario_comparison_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_tariff_comparison_switcher(results_for_display, texts, viz_settings); st.markdown("---")
    render_income_projection_switcher(results_for_display, texts, viz_settings); st.markdown("---")


    global pv_visuals_module
    if pv_visuals_module:
        if hasattr(pv_visuals_module, 'render_yearly_production_pv_data'): pv_visuals_module.render_yearly_production_pv_data(results_for_display, texts); st.markdown("---")
        if hasattr(pv_visuals_module, 'render_break_even_pv_data'): pv_visuals_module.render_break_even_pv_data(results_for_display, texts); st.markdown("---")
        if hasattr(pv_visuals_module, 'render_amortisation_pv_data'): pv_visuals_module.render_amortisation_pv_data(results_for_display, texts); st.markdown("---")

    st.subheader(get_text(texts, "simulation_details_header", "Simulationsdetails (Jährlich)"))
    sim_years_eff_econ_table_raw = results_for_display.get('simulation_period_years_effective')
    sim_years_eff_econ_table = int(sim_years_eff_econ_table_raw) if isinstance(sim_years_eff_econ_table_raw, int) and sim_years_eff_econ_table_raw >0 else 0
    if sim_years_eff_econ_table > 0:
        sim_table_data = {'Jahr': list(range(1, sim_years_eff_econ_table + 1))}
        data_keys_for_table = {
            'annual_productions_sim': get_text(texts, "annual_pv_production_kwh"),
            'annual_elec_prices_sim': get_text(texts, "electricity_price_label"),
            'annual_feed_in_tariffs_sim': get_text(texts, 'feed_in_tariff_euro_kwh'),
            'annual_benefits_sim': get_text(texts, "annual_financial_benefit"),
            'annual_maintenance_costs_sim': get_text(texts, "annual_maintenance_cost_sim"),
            'annual_cash_flows_sim': get_text(texts, "analysis_table_annual_cf_header"),
            'cumulative_cash_flows_sim': get_text(texts, "analysis_table_cumulative_cf_header")
        }
        for key, col_name in data_keys_for_table.items():
            data_list_raw = results_for_display.get(key); data_list_processed = []
            if isinstance(data_list_raw, list):
                data_list_processed = [float(val) if isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val) else 0.0 for val in data_list_raw]
            expected_len = sim_years_eff_econ_table
            if key == 'cumulative_cash_flows_sim':
                if len(data_list_processed) >= expected_len + 1: sim_table_data[col_name] = data_list_processed[1:]
                else: sim_table_data[col_name] = [None] * expected_len
            else:
                if len(data_list_processed) >= expected_len: sim_table_data[col_name] = data_list_processed[:expected_len]
                else: sim_table_data[col_name] = [None] * expected_len
        try:
            df_sim_table = pd.DataFrame(sim_table_data)
            if not df_sim_table.empty:
                formatted_df_sim_table = df_sim_table.copy()
                for col_sim_fmt_key, col_sim_fmt_display_name in data_keys_for_table.items():
                    if col_sim_fmt_display_name in formatted_df_sim_table.columns:
                        unit_in_table = ""; precision_in_table = 2
                        if "kWh" in col_sim_fmt_display_name: unit_in_table = "kWh"; precision_in_table = 0
                        elif "€" in col_sim_fmt_display_name or "benefit" in col_sim_fmt_key or "cost" in col_sim_fmt_key or "cash_flow" in col_sim_fmt_key:
                            unit_in_table = "€"; precision_in_table = 2
                            if "tariff" in col_sim_fmt_key or "price" in col_sim_fmt_key : precision_in_table = 4
                        formatted_df_sim_table[col_sim_fmt_display_name] = formatted_df_sim_table[col_sim_fmt_display_name].apply(
                            lambda x: format_kpi_value(x, unit=unit_in_table, precision=precision_in_table, texts_dict=texts) if pd.notnull(x) else get_text(texts, "not_applicable_short", "k.A.")
                        )
                st.dataframe(formatted_df_sim_table.set_index('Jahr'), use_container_width=True, height=min(350, (sim_years_eff_econ_table + 1) * 35 + 3), key="analysis_simulation_details_dataframe_v8_corrected")
            else: st.info(get_text(texts, "simulation_details_no_data_after_df", "Simulationsdetails-DataFrame ist leer."))
        except Exception as e_df_sim: st.error(f"Fehler bei Erstellung/Formatierung der Simulationstabelle: {e_df_sim}")
    else:
        st.info(get_text(texts, "simulation_details_no_data", "Simulationsdetails nicht verfügbar (Simulationsdauer 0 oder Daten fehlen)."))
        st.markdown("---")
    # ═══════════════════════════════════════════════════════════════
    # 💰 FINANZIERUNGSANALYSE - Integration der Financial Tools
    # ═══════════════════════════════════════════════════════════════
    render_financing_analysis(results_for_display, texts, viz_settings)

    if 'st' in globals() and hasattr(st, 'session_state') and 'results_for_display' in locals():
        st.session_state["calculation_results"] = results_for_display.copy()

def render_financing_analysis(results: Dict[str, Any], texts: Dict[str, str], viz_settings: Dict[str, Any]):
    """
    Rendert eine umfassende Finanzierungsanalyse mit verschiedenen Finanzierungsoptionen.
    """
    st.subheader("💰 Finanzierungsanalyse")
    
    # Prüfen ob Finanzierung gewünscht ist
    financing_requested = False
    if 'st' in globals() and hasattr(st, 'session_state'):
        project_data = st.session_state.get('project_data', {})
        customer_data = project_data.get('customer_data', {})
        financing_requested = customer_data.get('financing_requested', False)
    
    if not financing_requested:
        st.info("💡 Aktivieren Sie 'Finanzierung gewünscht' in der Dateneingabe für eine detaillierte Finanzierungsanalyse.")
        return
    
    # Investitionssumme aus den Berechnungsergebnissen
    total_investment = results.get('total_investment_netto', 25000.0)
    
    # Finanzierungsparameter aus Session State
    customer_data = st.session_state.get('project_data', {}).get('customer_data', {})
    financing_type = customer_data.get('financing_type', 'Bankkredit (Annuität)')
    
    st.markdown(f"**Gesamtinvestition:** {total_investment:,.2f} € (netto)")
    st.markdown(f"**Gewählte Finanzierungsart:** {financing_type}")
    
    # Interaktive Finanzierungsparameter
    with st.expander("🔧 **Finanzierungsparameter anpassen**", expanded=True):
        col_param1, col_param2, col_param3 = st.columns(3)
        
        with col_param1:
            financing_amount = st.number_input(
                "Finanzierungsbetrag (€)",
                min_value=1000.0,
                max_value=total_investment,
                value=customer_data.get('desired_financing_amount', total_investment * 0.8),
                step=500.0,
                key='financing_amount_analysis'
            )
            
        with col_param2:
            if financing_type == "Bankkredit (Annuität)":
                interest_rate = st.slider(
                    "Zinssatz (% p.a.)",
                    min_value=1.0,
                    max_value=12.0,
                    value=customer_data.get('interest_rate_percent', 4.5),
                    step=0.1,
                    key='interest_rate_analysis'
                )
            else:
                leasing_factor = st.slider(
                    "Leasingfaktor (% pro Monat)",
                    min_value=0.5,
                    max_value=3.0,
                    value=customer_data.get('leasing_factor_percent', 1.2),
                    step=0.1,
                    key='leasing_factor_analysis'
                )
                
        with col_param3:
            if financing_type == "Bankkredit (Annuität)":
                loan_term = st.slider(
                    "Laufzeit (Jahre)",
                    min_value=5,
                    max_value=25,
                    value=customer_data.get('loan_term_years', 15),
                    key='loan_term_analysis'
                )
            else:
                leasing_term = st.slider(
                    "Leasinglaufzeit (Monate)",
                    min_value=24,
                    max_value=180,
                    value=customer_data.get('leasing_term_months', 120),
                    step=12,
                    key='leasing_term_analysis'
                )
    
    # Finanzierungsberechnungen durchführen
    if financing_type == "Bankkredit (Annuität)":
        loan_result = calculate_annuity(financing_amount, interest_rate, loan_term)
        
        if "error" not in loan_result:
            col_result1, col_result2, col_result3 = st.columns(3)
            
            with col_result1:
                st.metric(
                    "Monatliche Rate",
                    f"{loan_result['monatliche_rate']:,.2f} €"
                )
                
            with col_result2:
                st.metric(
                    "Gesamtzinsen",
                    f"{loan_result['gesamtzinsen']:,.2f} €"
                )
                
            with col_result3:
                st.metric(
                    "Gesamtkosten",
                    f"{loan_result['gesamtkosten']:,.2f} €"
                )
            
            # Tilgungsplan anzeigen
            if st.checkbox("📊 Tilgungsplan anzeigen", key='show_amortization_schedule'):
                tilgungsplan_df = pd.DataFrame(loan_result['tilgungsplan'])
                st.dataframe(
                    tilgungsplan_df.head(24),  # Erste 2 Jahre anzeigen
                    use_container_width=True,
                    key='tilgungsplan_dataframe'
                )
                
                # Tilgungsplan-Visualisierung
                fig_tilgung = go.Figure()
                fig_tilgung.add_trace(go.Scatter(
                    x=tilgungsplan_df['monat'],
                    y=tilgungsplan_df['zinsen'],
                    mode='lines',
                    name='Zinsen',
                    fill='tozeroy'
                ))
                fig_tilgung.add_trace(go.Scatter(
                    x=tilgungsplan_df['monat'],
                    y=tilgungsplan_df['tilgung'],
                    mode='lines',
                    name='Tilgung',
                    fill='tonexty'
                ))
                fig_tilgung.update_layout(
                    title="Tilgungsplan-Visualisierung",
                    xaxis_title="Monat",
                    yaxis_title="Betrag (€)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_tilgung, use_container_width=True, key='tilgungsplan_chart')
    
    elif financing_type == "Leasing":
        leasing_result = calculate_leasing_costs(financing_amount, leasing_factor, leasing_term)
        
        if "error" not in leasing_result:
            col_result1, col_result2, col_result3 = st.columns(3)
            
            with col_result1:
                st.metric(
                    "Monatliche Leasingrate",
                    f"{leasing_result['monatliche_rate']:,.2f} €"
                )
                
            with col_result2:
                st.metric(
                    "Gesamtleasingkosten",
                    f"{leasing_result['gesamtkosten']:,.2f} €"
                )
                
            with col_result3:
                st.metric(
                    "Effektive Kosten",
                    f"{leasing_result['effektive_kosten']:,.2f} €"
                )
    
    # Finanzierungsvergleich
    st.markdown("---")
    st.subheader("📊 Finanzierungsvergleich")
    
    comparison_result = calculate_financing_comparison(
        financing_amount,
        interest_rate if financing_type == "Bankkredit (Annuität)" else 4.5,
        loan_term if financing_type == "Bankkredit (Annuität)" else 15,
        leasing_factor if financing_type == "Leasing" else 1.2
    )
    
    if comparison_result:
        col_comp1, col_comp2, col_comp3 = st.columns(3)
        
        with col_comp1:
            st.markdown("**💳 Kreditfinanzierung**")
            if "error" not in comparison_result.get("kredit", {}):
                credit = comparison_result["kredit"]
                st.metric("Monatliche Rate", f"{credit.get('monatliche_rate', 0):,.2f} €")
                st.metric("Gesamtkosten", f"{credit.get('gesamtkosten', 0):,.2f} €")
        
        with col_comp2:
            st.markdown("**🚗 Leasing**")
            if "error" not in comparison_result.get("leasing", {}):
                leasing = comparison_result["leasing"]
                st.metric("Monatliche Rate", f"{leasing.get('monatliche_rate', 0):,.2f} €")
                st.metric("Effektive Kosten", f"{leasing.get('effektive_kosten', 0):,.2f} €")
        
        with col_comp3:
            st.markdown("**💰 Barkauf**")
            cash = comparison_result.get("cash_kauf", {})
            st.metric("Investition", f"{cash.get('investition', 0):,.2f} €")
            st.metric("Opportunitätskosten", f"{cash.get('opportunitaetskosten', 0):,.2f} €")
        
        # Empfehlung anzeigen
        recommendation = comparison_result.get("empfehlung", "Keine Empfehlung verfügbar")
        st.info(f"💡 **{recommendation}**")
    
    # Steuerliche Aspekte
    st.markdown("---")
    st.subheader("🏛️ Steuerliche Aspekte")
    
    # Abschreibung berechnen
    depreciation_result = calculate_depreciation(total_investment, 20, "linear")
    
    if "error" not in depreciation_result:
        col_tax1, col_tax2 = st.columns(2)
        
        with col_tax1:
            st.metric(
                "Jährliche Abschreibung",
                f"{depreciation_result['jaehrliche_abschreibung']:,.2f} €"
            )
            
        with col_tax2:
            st.metric(
                "Steuerersparnis (30%)",
                f"{depreciation_result['steuerersparnis_30_prozent']:,.2f} €"
            )
    
    # PV-Ertrag und Steueroptimierung
    annual_pv_revenue = results.get('annual_revenue_feed_in_eur', 0) + results.get('annual_savings_consumption_eur', 0)
    if annual_pv_revenue > 0:
        tax_result = calculate_capital_gains_tax(annual_pv_revenue, 26.375)
        
        col_tax3, col_tax4 = st.columns(2)
        with col_tax3:
            st.metric(
                "Jährlicher PV-Ertrag",
                f"{annual_pv_revenue:,.2f} €"
            )
        with col_tax4:
            st.metric(
                "Steuer (KESt 26,375%)",
                f"{tax_result['steuer']:,.2f} €"
            )
    
    # Wirtschaftlichkeitsvergleich mit/ohne Finanzierung
    st.markdown("---")
    st.subheader("📈 Rentabilitätsvergleich")
    
    # Hier könnten weitere Berechnungen zur Wirtschaftlichkeit eingefügt werden
    cash_flow_20_years = results.get('cumulative_cash_flows_sim', [0] * 21)
    if len(cash_flow_20_years) > 20:
        final_cash_flow = cash_flow_20_years[20]
        
        col_profit1, col_profit2 = st.columns(2)
        with col_profit1:
            st.metric(
                "Gewinn nach 20 Jahren (Barkauf)",
                f"{final_cash_flow:,.2f} €",
                delta=None
            )
        
        # Vereinfachte Finanzierungsrendite
        if financing_type == "Bankkredit (Annuität)" and "error" not in loan_result:
            total_financing_cost = loan_result.get('gesamtkosten', 0)
            equity_used = total_investment - financing_amount
            financing_profit = final_cash_flow - (total_financing_cost - financing_amount) - equity_used
            
            with col_profit2:
                st.metric(
                    f"Gewinn nach 20 Jahren ({financing_type})",
                    f"{financing_profit:,.2f} €",
                    delta=f"{financing_profit - final_cash_flow:,.2f} €"
                )

    st.markdown("---")

pv_visuals_module = None
try:
    import pv_visuals # type: ignore
    pv_visuals_module = pv_visuals
except ImportError:
    pass

# Änderungshistorie
# ... (vorherige Einträge)