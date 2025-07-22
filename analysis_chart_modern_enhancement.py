# analysis_chart_modern_enhancement.py
# -*- coding: utf-8 -*-
"""
Moderne Erweiterung für Analysis-Charts mit professionellem Design
Erweitert bestehende Visualisierungen um moderne Farbschemata und Layouts
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

# Sichere Imports
try:
    from pdf_design_enhanced_modern import get_modern_design_system, get_available_modern_color_schemes
    MODERN_DESIGN_AVAILABLE = True
except ImportError:
    MODERN_DESIGN_AVAILABLE = False

class ModernChartEnhancer:
    """
    Erweitert bestehende Charts um moderne Design-Features
    """
    
    def __init__(self):
        self.modern_design_system = None
        self.color_schemes = {}
        self._initialize_design_system()
    
    def _initialize_design_system(self):
        """Initialisiert das moderne Design-System"""
        if not MODERN_DESIGN_AVAILABLE:
            return
        
        try:
            self.modern_design_system = get_modern_design_system()
            self.color_schemes = get_available_modern_color_schemes()
        except Exception:
            pass
    
    def get_modern_color_palette(self, scheme_name: str = 'premium_blue_modern') -> List[str]:
        """Gibt moderne Farbpalette für Charts zurück"""
        if not self.modern_design_system:
            return px.colors.qualitative.Set3
        
        try:
            scheme_colors = self.modern_design_system.enhanced_color_schemes.get(
                scheme_name, 
                self.modern_design_system.enhanced_color_schemes['premium_blue_modern']
            )
            
            return [
                str(scheme_colors['primary']),
                str(scheme_colors['secondary']),
                str(scheme_colors['accent']),
                str(scheme_colors['success']),
                str(scheme_colors['warning']),
                str(scheme_colors['highlight']),
                str(scheme_colors['text_primary']),
                str(scheme_colors['text_secondary'])
            ]
        except Exception:
            return px.colors.qualitative.Set3
    
    def enhance_chart_layout(self, fig: go.Figure, 
                           scheme_name: str = 'premium_blue_modern',
                           title: str = None) -> go.Figure:
        """Erweitert Chart-Layout mit modernem Design"""
        if not self.modern_design_system:
            return fig
        
        try:
            scheme_colors = self.modern_design_system.enhanced_color_schemes.get(
                scheme_name,
                self.modern_design_system.enhanced_color_schemes['premium_blue_modern']
            )
            
            # Moderne Layout-Updates
            fig.update_layout(
                # Hintergrund
                plot_bgcolor='white',
                paper_bgcolor='white',
                
                # Titel-Styling
                title=dict(
                    text=title if title else fig.layout.title.text,
                    font=dict(
                        size=18,
                        color=str(scheme_colors['text_primary']),
                        family='Arial, sans-serif'
                    ),
                    x=0.5,
                    xanchor='center'
                ),
                
                # Achsen-Styling
                xaxis=dict(
                    gridcolor=str(scheme_colors['border_light']),
                    linecolor=str(scheme_colors['border_medium']),
                    tickcolor=str(scheme_colors['text_secondary']),
                    tickfont=dict(
                        color=str(scheme_colors['text_secondary']),
                        size=11
                    ),
                    title_font=dict(
                        color=str(scheme_colors['text_primary']),
                        size=13
                    )
                ),
                yaxis=dict(
                    gridcolor=str(scheme_colors['border_light']),
                    linecolor=str(scheme_colors['border_medium']),
                    tickcolor=str(scheme_colors['text_secondary']),
                    tickfont=dict(
                        color=str(scheme_colors['text_secondary']),
                        size=11
                    ),
                    title_font=dict(
                        color=str(scheme_colors['text_primary']),
                        size=13
                    )
                ),
                
                # Legende
                legend=dict(
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor=str(scheme_colors['border_medium']),
                    borderwidth=1,
                    font=dict(
                        color=str(scheme_colors['text_secondary']),
                        size=11
                    )
                ),
                
                # Margins
                margin=dict(l=60, r=20, t=60, b=60),
                
                # Hover
                hoverlabel=dict(
                    bgcolor=str(scheme_colors['background']),
                    bordercolor=str(scheme_colors['border_medium']),
                    font_color=str(scheme_colors['text_primary'])
                )
            )
            
            return fig
            
        except Exception:
            return fig
    
    def create_modern_financial_chart(self, financial_data: Dict[str, Any],
                                    scheme_name: str = 'premium_blue_modern') -> go.Figure:
        """Erstellt moderne Finanzcharts"""
        colors = self.get_modern_color_palette(scheme_name)
        
        # Beispiel: Cashflow-Chart mit modernem Design
        years = list(range(1, 26))
        investment = financial_data.get('total_investment', 20000)
        annual_savings = financial_data.get('annual_savings', 1500)
        
        # Cumulative Cashflow berechnen
        cumulative_cashflow = [-investment]
        for year in range(1, 26):
            cumulative_cashflow.append(cumulative_cashflow[-1] + annual_savings)
        
        fig = go.Figure()
        
        # Negativ/Positiv-Bereiche unterschiedlich färben
        neg_values = [min(0, val) for val in cumulative_cashflow]
        pos_values = [max(0, val) for val in cumulative_cashflow]
        
        fig.add_trace(go.Scatter(
            x=list(range(0, 26)),
            y=neg_values,
            fill='tozeroy',
            fillcolor=f'rgba({",".join([str(int(colors[4][1:3], 16)), str(int(colors[4][3:5], 16)), str(int(colors[4][5:7], 16))])}, 0.3)',
            line=dict(color=colors[4], width=0),
            name='Investitionsphase',
            hovertemplate='Jahr %{x}<br>Cashflow: %{y:,.0f} €<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=list(range(0, 26)),
            y=pos_values,
            fill='tozeroy',
            fillcolor=f'rgba({",".join([str(int(colors[3][1:3], 16)), str(int(colors[3][3:5], 16)), str(int(colors[3][5:7], 16))])}, 0.3)',
            line=dict(color=colors[3], width=0),
            name='Gewinnphase',
            hovertemplate='Jahr %{x}<br>Cashflow: %{y:,.0f} €<extra></extra>'
        ))
        
        # Hauptlinie
        fig.add_trace(go.Scatter(
            x=list(range(0, 26)),
            y=cumulative_cashflow,
            mode='lines+markers',
            line=dict(color=colors[0], width=3),
            marker=dict(size=6),
            name='Kumulierter Cashflow',
            hovertemplate='Jahr %{x}<br>Cashflow: %{y:,.0f} €<extra></extra>'
        ))
        
        # Break-Even Linie
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color=colors[6],
            annotation_text="Break-Even",
            annotation_position="right"
        )
        
        fig = self.enhance_chart_layout(
            fig, 
            scheme_name, 
            "💰 Kumulierter Cashflow über 25 Jahre"
        )
        
        fig.update_layout(
            xaxis_title="Jahre",
            yaxis_title="Kumulierter Cashflow (€)",
            showlegend=True
        )
        
        return fig
    
    def create_modern_energy_production_chart(self, production_data: List[float],
                                            consumption_data: List[float],
                                            scheme_name: str = 'solar_professional_enhanced') -> go.Figure:
        """Erstellt moderne Energieproduktionscharts"""
        colors = self.get_modern_color_palette(scheme_name)
        
        months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        
        fig = go.Figure()
        
        # Produktion
        fig.add_trace(go.Bar(
            x=months,
            y=production_data,
            name='PV-Produktion',
            marker_color=colors[0],
            opacity=0.8,
            hovertemplate='%{x}<br>Produktion: %{y:,.0f} kWh<extra></extra>'
        ))
        
        # Verbrauch
        fig.add_trace(go.Scatter(
            x=months,
            y=consumption_data,
            mode='lines+markers',
            name='Verbrauch',
            line=dict(color=colors[1], width=3),
            marker=dict(size=8, color=colors[1]),
            hovertemplate='%{x}<br>Verbrauch: %{y:,.0f} kWh<extra></extra>'
        ))
        
        fig = self.enhance_chart_layout(
            fig,
            scheme_name,
            "🌞 Monatliche PV-Produktion vs. Verbrauch"
        )
        
        fig.update_layout(
            xaxis_title="Monat",
            yaxis_title="Energie (kWh)",
            barmode='group'
        )
        
        return fig
    
    def create_modern_roi_chart(self, investment_scenarios: Dict[str, float],
                              scheme_name: str = 'executive_luxury') -> go.Figure:
        """Erstellt moderne ROI-Vergleichscharts"""
        colors = self.get_modern_color_palette(scheme_name)
        
        scenarios = list(investment_scenarios.keys())
        values = list(investment_scenarios.values())
        
        # Farbcodierung nach ROI-Wert
        colors_mapped = []
        for val in values:
            if val >= 15:
                colors_mapped.append(colors[3])  # Erfolg
            elif val >= 10:
                colors_mapped.append(colors[2])  # Accent
            elif val >= 5:
                colors_mapped.append(colors[4])  # Warning
            else:
                colors_mapped.append(colors[6])  # Niedrig
        
        fig = go.Figure(data=[
            go.Bar(
                x=scenarios,
                y=values,
                marker_color=colors_mapped,
                text=[f'{val:.1f}%' for val in values],
                textposition='auto',
                textfont=dict(size=12, color='white'),
                hovertemplate='%{x}<br>ROI: %{y:.1f}%<extra></extra>'
            )
        ])
        
        fig = self.enhance_chart_layout(
            fig,
            scheme_name,
            "📈 Return on Investment (ROI) Vergleich"
        )
        
        fig.update_layout(
            xaxis_title="Investitionsszenarien",
            yaxis_title="ROI (%)",
            yaxis=dict(ticksuffix='%')
        )
        
        return fig

def enhance_existing_chart_with_modern_design(fig: go.Figure, 
                                            chart_type: str = 'general',
                                            scheme_name: str = 'premium_blue_modern') -> go.Figure:
    """
    Erweitert bestehende Charts um moderne Design-Features
    Kann direkt auf bestehende Plotly-Figures angewendet werden
    """
    if not MODERN_DESIGN_AVAILABLE:
        return fig
    
    try:
        enhancer = ModernChartEnhancer()
        return enhancer.enhance_chart_layout(fig, scheme_name)
    except Exception:
        return fig

def get_modern_chart_color_sequence(scheme_name: str = 'premium_blue_modern') -> List[str]:
    """
    Gibt moderne Farbsequenz für Charts zurück
    Kann für bestehende Chart-Erstellung verwendet werden
    """
    if not MODERN_DESIGN_AVAILABLE:
        return px.colors.qualitative.Set3
    
    try:
        enhancer = ModernChartEnhancer()
        return enhancer.get_modern_color_palette(scheme_name)
    except Exception:
        return px.colors.qualitative.Set3

def create_sample_modern_charts_for_analysis(analysis_results: Dict[str, Any],
                                           scheme_name: str = 'premium_blue_modern') -> Dict[str, go.Figure]:
    """
    Erstellt Beispiel-Charts mit modernem Design basierend auf Analysis-Daten
    """
    if not MODERN_DESIGN_AVAILABLE:
        return {}
    
    try:
        enhancer = ModernChartEnhancer()
        charts = {}
        
        # Finanz-Chart
        if analysis_results.get('total_investment_netto') and analysis_results.get('annual_benefits_sim'):
            financial_data = {
                'total_investment': analysis_results.get('total_investment_netto', 20000),
                'annual_savings': analysis_results.get('annual_benefits_sim', [1500])[0] if analysis_results.get('annual_benefits_sim') else 1500
            }
            charts['modern_financial'] = enhancer.create_modern_financial_chart(financial_data, scheme_name)
        
        # Energieproduktion-Chart
        if analysis_results.get('monthly_productions_sim') and analysis_results.get('monthly_consumption_sim'):
            production_data = analysis_results['monthly_productions_sim']
            consumption_data = analysis_results['monthly_consumption_sim']
            if len(production_data) >= 12 and len(consumption_data) >= 12:
                charts['modern_energy'] = enhancer.create_modern_energy_production_chart(
                    production_data[:12], consumption_data[:12], scheme_name
                )
        
        # ROI-Chart
        roi_scenarios = {
            'Pessimistisch': 8.5,
            'Realistisch': 12.3,
            'Optimistisch': 15.8
        }
        charts['modern_roi'] = enhancer.create_modern_roi_chart(roi_scenarios, scheme_name)
        
        return charts
        
    except Exception as e:
        print(f"Fehler beim Erstellen moderner Charts: {e}")
        return {}

# Integration in bestehende Analysis-Funktionen
def apply_modern_design_to_analysis_charts(chart_bytes_dict: Dict[str, bytes],
                                         scheme_name: str = 'premium_blue_modern') -> Dict[str, bytes]:
    """
    Wendet moderne Design-Features auf bestehende Analysis-Charts an
    Kann in bestehende render_* Funktionen integriert werden
    """
    if not MODERN_DESIGN_AVAILABLE or not chart_bytes_dict:
        return chart_bytes_dict
    
    # TODO: Implementierung für Modifikation bestehender Chart-Bytes
    # Derzeit nur Durchleitung, da Byte-Modifikation komplex ist
    return chart_bytes_dict

def enhance_streamlit_chart_display(fig: go.Figure, 
                                  chart_key: str,
                                  scheme_name: str = 'premium_blue_modern') -> None:
    """
    Erweitert Streamlit Chart-Anzeige mit modernen Features
    """
    if MODERN_DESIGN_AVAILABLE:
        fig = enhance_existing_chart_with_modern_design(fig, 'general', scheme_name)
    
    # Erweiterte Display-Optionen
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"modern_enhanced_{chart_key}",
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'chart_{chart_key}',
                'height': 600,
                'width': 1000,
                'scale': 2
            }
        }
    )

def create_sample_modern_charts_for_analysis(calculation_results: Dict[str, Any],
                                           color_scheme: str = 'premium_blue_modern') -> Dict[str, go.Figure]:
    """
    Erstellt Sammlung moderner Charts für Analysis-Sektion
    """
    charts = {}
    
    if not calculation_results:
        return charts
    
    try:
        enhancer = ModernChartEnhancer()
        
        # Finanz-Timeline Chart
        financial_chart = create_modern_financial_timeline_chart(calculation_results, color_scheme)
        if financial_chart:
            charts['financial_timeline'] = financial_chart
        
        # Energiefluss-Chart
        energy_chart = create_modern_energy_flow_chart(calculation_results, color_scheme)
        if energy_chart:
            charts['energy_flow'] = energy_chart
        
        # Monatlicher Vergleich
        monthly_chart = create_modern_monthly_comparison_chart(calculation_results, color_scheme)
        if monthly_chart:
            charts['monthly_comparison'] = monthly_chart
        
        # ROI-Vergleich
        roi_chart = create_modern_roi_comparison_chart(calculation_results, color_scheme)
        if roi_chart:
            charts['roi_comparison'] = roi_chart
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen der modernen Charts: {e}")
    
    return charts

def create_modern_financial_timeline_chart(calculation_results: Dict[str, Any], 
                                         color_scheme: str = 'premium_blue_modern') -> Optional[go.Figure]:
    """
    Erstellt moderne Finanz-Timeline mit ROI-Darstellung
    """
    try:
        # Daten extrahieren
        total_cost = calculation_results.get('total_system_cost', 0)
        annual_savings = calculation_results.get('annual_savings', 0)
        payback_years = calculation_results.get('payback_period_years', 0)
        
        if not all([total_cost, annual_savings, payback_years]):
            return None
        
        enhancer = ModernChartEnhancer()
        colors = enhancer.get_modern_color_palette(color_scheme)
        
        # 25 Jahre Timeline erstellen
        years = list(range(0, 26))
        cumulative_savings = []
        net_profit = []
        
        for year in years:
            savings = annual_savings * year
            profit = savings - total_cost
            cumulative_savings.append(savings)
            net_profit.append(max(profit, -total_cost))
        
        fig = go.Figure()
        
        # Kumulative Einsparungen
        fig.add_trace(go.Scatter(
            x=years,
            y=cumulative_savings,
            mode='lines+markers',
            name='Kumulative Einsparungen',
            line=dict(color=colors[1], width=3),
            marker=dict(size=6),
            hovertemplate='Jahr %{x}<br>Einsparungen: %{y:,.0f} €<extra></extra>'
        ))
        
        # Netto-Gewinn
        fig.add_trace(go.Scatter(
            x=years,
            y=net_profit,
            mode='lines+markers',
            name='Netto-Gewinn',
            line=dict(color=colors[3], width=3),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)',
            hovertemplate='Jahr %{x}<br>Netto-Gewinn: %{y:,.0f} €<extra></extra>'
        ))
        
        # Break-Even Linie
        fig.add_hline(
            y=0, 
            line_dash="dash", 
            line_color=colors[0],
            annotation_text="Break-Even",
            annotation_position="left"
        )
        
        # Amortisation markieren
        if payback_years <= 25:
            fig.add_vline(
                x=payback_years,
                line_dash="dot",
                line_color=colors[4],
                annotation_text=f"Amortisation<br>Jahr {payback_years:.1f}",
                annotation_position="top"
            )
        
        fig.update_layout(
            title={
                'text': '💰 Finanzielle Entwicklung über 25 Jahre',
                'x': 0.5,
                'font': {'size': 18, 'color': colors[0]}
            },
            xaxis_title='Jahre',
            yaxis_title='Euro (€)',
            template='plotly_white',
            showlegend=True,
            height=500,
            hovermode='x unified'
        )
        
        # Achsen formatieren
        fig.update_xaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxis(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        return fig
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Finanz-Charts: {e}")
        return None

def create_modern_energy_flow_chart(calculation_results: Dict[str, Any],
                                  color_scheme: str = 'solar_professional_enhanced') -> Optional[go.Figure]:
    """
    Erstellt moderne Energiefluss-Visualisierung als Sankey-Diagramm
    """
    try:
        # Energiedaten extrahieren
        pv_production = calculation_results.get('annual_pv_production_kwh', 0)
        direct_consumption = calculation_results.get('direct_consumption_kwh', pv_production * 0.3)
        battery_storage = calculation_results.get('battery_storage_kwh', pv_production * 0.2)
        grid_feed_in = calculation_results.get('grid_feed_in_kwh', pv_production * 0.5)
        grid_consumption = calculation_results.get('grid_consumption_kwh', 
                                                  calculation_results.get('annual_consumption_kwh', 0) - direct_consumption)
        
        if not pv_production:
            return None
        
        enhancer = ModernChartEnhancer()
        colors = enhancer.get_modern_color_palette(color_scheme)
        
        # Sankey-Diagramm für Energiefluss
        fig = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = [
                    "☀️ PV-Produktion",
                    "🏠 Direktverbrauch", 
                    "🔋 Batteriespeicher",
                    "⚡ Netzeinspeisung",
                    "🏠 Hausverbrauch",
                    "🔌 Netzbezug"
                ],
                color = colors[:6]
            ),
            link = dict(
                source = [0, 0, 0, 2, 5],
                target = [1, 2, 3, 4, 4], 
                value = [
                    direct_consumption,
                    battery_storage, 
                    grid_feed_in,
                    battery_storage,
                    grid_consumption
                ],
                color = [
                    'rgba(59, 130, 246, 0.4)',
                    'rgba(16, 185, 129, 0.4)', 
                    'rgba(251, 191, 36, 0.4)',
                    'rgba(16, 185, 129, 0.4)',
                    'rgba(239, 68, 68, 0.4)'
                ]
            )
        )])
        
        fig.update_layout(
            title={
                'text': '⚡ Energiefluss-Analyse',
                'x': 0.5,
                'font': {'size': 18, 'color': colors[0]}
            },
            font_size=12,
            height=400
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Energiefluss-Charts: {e}")
        return None

def create_modern_monthly_comparison_chart(calculation_results: Dict[str, Any],
                                         color_scheme: str = 'premium_blue_modern') -> Optional[go.Figure]:
    """
    Erstellt modernen monatlichen Vergleich
    """
    try:
        # Monatliche Daten
        months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        
        # Jährliche Daten
        annual_production = calculation_results.get('annual_pv_production_kwh', 0)
        annual_consumption = calculation_results.get('annual_consumption_kwh', 0)
        
        if not annual_production:
            return None
        
        # Typische monatliche Verteilung für Deutschland
        monthly_factors = [0.04, 0.06, 0.09, 0.12, 0.14, 0.15, 
                          0.15, 0.13, 0.10, 0.07, 0.04, 0.03]
        
        monthly_production = [annual_production * factor for factor in monthly_factors]
        monthly_consumption_val = annual_consumption / 12 if annual_consumption else annual_production / 12
        monthly_consumption_list = [monthly_consumption_val] * 12
        
        enhancer = ModernChartEnhancer()
        colors = enhancer.get_modern_color_palette(color_scheme)
        
        fig = go.Figure()
        
        # PV-Produktion
        fig.add_trace(go.Bar(
            x=months,
            y=monthly_production,
            name='PV-Produktion',
            marker_color=colors[1],
            hovertemplate='%{x}<br>Produktion: %{y:,.0f} kWh<extra></extra>'
        ))
        
        # Verbrauch
        fig.add_trace(go.Scatter(
            x=months,
            y=monthly_consumption_list,
            mode='lines+markers',
            name='Verbrauch',
            line=dict(color=colors[4], width=3),
            marker=dict(size=8),
            hovertemplate='%{x}<br>Verbrauch: %{y:,.0f} kWh<extra></extra>'
        ))
        
        # Überschuss/Defizit
        surplus_deficit = [prod - monthly_consumption_val for prod in monthly_production]
        fig.add_trace(go.Bar(
            x=months,
            y=surplus_deficit,
            name='Überschuss/Defizit',
            marker_color=[colors[3] if val > 0 else colors[4] for val in surplus_deficit],
            opacity=0.7,
            hovertemplate='%{x}<br>%{y:,.0f} kWh<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '📊 Monatliche Energie-Bilanz',
                'x': 0.5,
                'font': {'size': 18, 'color': colors[0]}
            },
            xaxis_title='Monat',
            yaxis_title='Energie (kWh)',
            template='plotly_white',
            showlegend=True,
            height=450,
            barmode='overlay'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Monats-Charts: {e}")
        return None

def create_modern_roi_comparison_chart(calculation_results: Dict[str, Any],
                                     color_scheme: str = 'premium_blue_modern') -> Optional[go.Figure]:
    """
    Erstellt modernen ROI-Vergleich verschiedener Szenarien
    """
    try:
        enhancer = ModernChartEnhancer()
        colors = enhancer.get_modern_color_palette(color_scheme)
        
        # Verschiedene Szenarien
        scenarios = ['Ohne Solar', 'Mit Solar', 'Mit Solar + Speicher']
        
        # 25-Jahre Kosten berechnen
        annual_grid_cost = calculation_results.get('annual_electricity_cost_without_pv', 0)
        total_system_cost = calculation_results.get('total_system_cost', 0)
        annual_savings = calculation_results.get('annual_savings', 0)
        battery_cost = calculation_results.get('battery_cost', 0)
        
        if not all([annual_grid_cost, total_system_cost, annual_savings]):
            return None
        
        # Vereinfachte Berechnung für Demo
        costs_25_years = [
            annual_grid_cost * 25,  # Ohne Solar
            total_system_cost + (annual_grid_cost - annual_savings) * 25,  # Mit Solar
            total_system_cost + battery_cost + (annual_grid_cost - annual_savings * 1.2) * 25  # Mit Speicher
        ]
        
        savings_25_years = [
            0,  # Ohne Solar
            annual_savings * 25 - total_system_cost,  # Mit Solar
            annual_savings * 1.2 * 25 - total_system_cost - battery_cost  # Mit Speicher
        ]
        
        fig = go.Figure()
        
        # Kosten
        fig.add_trace(go.Bar(
            x=scenarios,
            y=costs_25_years,
            name='Gesamtkosten (25 Jahre)',
            marker_color=colors[4],
            hovertemplate='%{x}<br>Kosten: %{y:,.0f} €<extra></extra>'
        ))
        
        # Einsparungen
        fig.add_trace(go.Bar(
            x=scenarios,
            y=savings_25_years,
            name='Netto-Einsparungen',
            marker_color=colors[3],
            hovertemplate='%{x}<br>Einsparungen: %{y:,.0f} €<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': '💡 ROI-Vergleich verschiedener Szenarien',
                'x': 0.5,
                'font': {'size': 18, 'color': colors[0]}
            },
            xaxis_title='Szenario',
            yaxis_title='Euro (€)',
            template='plotly_white',
            showlegend=True,
            height=450,
            barmode='group'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des ROI-Charts: {e}")
        return None

def get_modern_chart_color_sequence(color_scheme: str = 'premium_blue_modern') -> List[str]:
    """
    Gibt moderne Farbsequenz für Charts zurück
    """
    enhancer = ModernChartEnhancer()
    return enhancer.get_modern_color_palette(color_scheme)

def get_current_modern_color_scheme_name() -> str:
    """Gibt den aktuell gewählten Farbschema-Namen zurück"""
    import streamlit as st
    return st.session_state.get('modern_pdf_color_scheme', 'premium_blue_modern')
