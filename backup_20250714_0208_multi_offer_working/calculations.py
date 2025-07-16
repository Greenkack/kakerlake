# calculations.py
"""
Hauptmodul für die Berechnung von Photovoltaikanlagen und Wirtschaftlichkeitsanalysen.
"""

from __future__ import annotations

import io
import pandas as pd
import numpy as np
import json
import math
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import traceback
import requests # Für HTTP-Anfragen an PVGIS

_global_import_errors_calc: List[str] = []

# --- DUMMY FUNKTIONEN UND FALLBACKS ---
def Dummy_load_admin_setting_calc(key, default=None):
    if key == 'price_matrix_csv_data': return ""
    if key == 'price_matrix_excel_bytes': return None
    if key == 'feed_in_tariffs':
        return {
            "parts": [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 8.1},
                      {"kwp_min": 10.01, "kwp_max": 40.0, "ct_per_kwh": 7.0},
                      {"kwp_min": 40.01, "kwp_max": 1000.0, "ct_per_kwh": 5.7}],
            "full": [{"kwp_min": 0.0, "kwp_max": 10.0, "ct_per_kwh": 12.9},
                     {"kwp_min": 10.01, "kwp_max": 100.0, "ct_per_kwh": 10.8}]
        }
    if key == 'global_constants':
        return {
            'vat_rate_percent': 0.0, 'electricity_price_increase_annual_percent': 3.0,
            'simulation_period_years': 20, 'inflation_rate_percent': 2.0,
            'loan_interest_rate_percent': 4.0, 'capital_gains_tax_kest_percent': 26.375,
            'alternative_investment_interest_rate_percent': 5.0,
            'co2_emission_factor_kg_per_kwh': 0.474,
            'maintenance_costs_base_percent': 1.5,
            'einspeiseverguetung_period_years': 20,
            'marktwert_strom_eur_per_kwh_after_eeg': 0.03,
            'storage_cycles_per_year': 250, 'storage_efficiency': 0.9,
            'eauto_annual_km': 10000, 'eauto_consumption_kwh_per_100km': 18.0,
            'eauto_pv_share_percent': 30.0, 'heatpump_cop_factor': 3.5,
            'heatpump_pv_share_percent': 40.0, 'afa_period_years': 20,
            'pvgis_system_loss_default_percent': 14.0,
            'annual_module_degradation_percent': 0.5,
            'maintenance_fixed_eur_pa': 50.0,
            'maintenance_variable_eur_per_kwp_pa': 5.0,
            'maintenance_increase_percent_pa': 2.0,
            'one_time_bonus_eur': 0.0,
            'global_yield_adjustment_percent': 0.0,
            'default_specific_yield_kwh_kwp': 950.0,
            'reference_specific_yield_pr': 1100.0,
            'specific_yields_by_orientation_tilt': {
                "Süd_0":950.0, "Süd_15":980.0, "Süd_30":1000.0, "Süd_45":980.0, "Süd_60":950.0,
                "Südost_0":900.0, "Südost_15":930.0, "Südost_30":950.0, "Südost_45":930.0, "Südost_60":900.0,
                "Südwest_0":900.0, "Südwest_15":930.0, "Südwest_30":950.0, "Südwest_45":930.0, "Südwest_60":900.0,
                "Ost_0":850.0, "Ost_15":880.0, "Ost_30":900.0, "Ost_45":880.0, "Ost_60":850.0,
                "West_0":850.0, "West_15":880.0, "West_30":900.0, "West_45":880.0, "West_60":850.0,
                "Nord_0":700.0, "Nord_15":720.0, "Nord_30":750.0, "Nord_45":720.0, "Nord_60":700.0,
                "Nordost_0":750.0, "Nordost_15":770.0, "Nordost_30":800.0, "Nordost_45":770.0, "Nordost_60":750.0,
                "Nordwest_0":750.0, "Nordwest_15":770.0, "Nordwest_30":800.0, "Nordwest_45":770.0, "Nordwest_60":750.0,
                "Flachdach_0":900.0, "Flachdach_15":920.0,
                "Sonstige_0":800.0, "Sonstige_15":820.0, "Sonstige_30":850.0, "Sonstige_45":820.0, "Sonstige_60":800.0
            },
            'monthly_production_distribution': [0.03,0.05,0.08,0.11,0.13,0.14,0.13,0.12,0.09,0.06,0.04,0.02],
            'monthly_consumption_distribution': [0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0833,0.0837], # Summe ca. 1
            'direct_self_consumption_factor_of_production': 0.25,
            'co2_per_tree_kg_pa': 12.5, 'co2_per_car_km_kg': 0.12,
            'co2_per_flight_muc_pmi_kg': 180.0,
            'economic_settings': {'reference_specific_yield_for_pr_kwh_per_kwp': 1100.0},
            'default_performance_ratio_percent': 78.0,
            'peak_shaving_effect_kw_estimate': 0.0, 'optimal_storage_factor': 1.0,
            'app_debug_mode_enabled': False
        }
    return default

def Dummy_list_products_calc(category=None): return []
def Dummy_get_product_by_id_calc(product_id): return None
def Dummy_get_product_by_model_name_calc(model_name): return None

_DATABASE_AVAILABLE = False
try:
    from database import load_admin_setting as real_load_admin_setting
    if not callable(real_load_admin_setting): raise ImportError("real_load_admin_setting nicht aufrufbar.")
    _DATABASE_AVAILABLE = True
except ImportError: real_load_admin_setting = Dummy_load_admin_setting_calc
except Exception: real_load_admin_setting = Dummy_load_admin_setting_calc

_PRODUCT_DB_AVAILABLE = False
try:
    from product_db import list_products as real_list_products, get_product_by_id as real_get_product_by_id, get_product_by_model_name as real_get_product_by_model_name
    if not callable(real_list_products) or not callable(real_get_product_by_id) or not callable(real_get_product_by_model_name):
        raise ImportError("Eine oder mehrere Produkt-DB Funktionen sind nicht aufrufbar.")
    _PRODUCT_DB_AVAILABLE = True
except ImportError:
    real_list_products,real_get_product_by_id,real_get_product_by_model_name = Dummy_list_products_calc,Dummy_get_product_by_id_calc,Dummy_get_product_by_model_name_calc
except Exception:
    real_list_products,real_get_product_by_id,real_get_product_by_model_name = Dummy_list_products_calc,Dummy_get_product_by_id_calc,Dummy_get_product_by_model_name_calc

def parse_module_price_matrix_csv(csv_data: Union[str, io.StringIO], errors_list: List[str]) -> Optional[pd.DataFrame]:
    if not csv_data:
        errors_list.append("Preis-Matrix-CSV-Daten sind leer.")
        return None
    try:
        if isinstance(csv_data, str):
            csv_file_like = io.StringIO(csv_data)
        else:
            csv_file_like = csv_data
            csv_file_like.seek(0)

        df = pd.read_csv(csv_file_like, sep=';', decimal=',', index_col=0, thousands='.', comment='#')

        if df.empty and not (df.index.name is None or str(df.index.name).strip().lower() not in ['anzahl module', 'anzahl_module']):
            errors_list.append("Preis-Matrix-CSV: DataFrame ist leer, aber Indexname ist nicht 'Anzahl Module'. Formatproblem?")
            return None

        if df.index.name is None or str(df.index.name).strip().lower() not in ['anzahl module', 'anzahl_module']:
            potential_index_cols = [col for col in df.columns if str(col).strip().lower() in ['anzahl module', 'anzahl_module']]
            if potential_index_cols:
                df = df.set_index(potential_index_cols[0])
            else:
                csv_file_like.seek(0)
                try:
                    temp_df_check = pd.read_csv(csv_file_like, sep=';', decimal=',', thousands='.', comment='#')
                    if not temp_df_check.empty and pd.api.types.is_numeric_dtype(temp_df_check.iloc[:, 0]):
                        csv_file_like.seek(0)
                        df = pd.read_csv(csv_file_like, sep=';', decimal=',', index_col=0, thousands='.', comment='#')
                    else:
                        errors_list.append("Preis-Matrix-CSV: Indexspalte 'Anzahl Module' nicht gefunden und erste Spalte ist nicht als Index geeignet.")
                        return None
                except Exception:
                    errors_list.append("Preis-Matrix-CSV: Indexspalte 'Anzahl Module' nicht gefunden und alternativer Versuch fehlgeschlagen.")
                    return None

        df.index.name = 'Anzahl Module'
        df.index = pd.to_numeric(df.index, errors='coerce')
        df = df[df.index.notna()]

        if df.empty:
            errors_list.append("Preis-Matrix-CSV: Index 'Anzahl Module' enthält keine gültigen Zahlen oder alle Zeilen hatten ungültige Indexwerte.")
            return None

        df.index = df.index.astype(int)

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df.dropna(axis=0, how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        if df.empty:
            errors_list.append("Preis-Matrix nach Bereinigung leer. Bitte Format und Inhalt prüfen.")
            return None
        return df
    except pd.errors.EmptyDataError:
        errors_list.append("Preis-Matrix-CSV: Die Datei ist leer.")
        return None
    except ValueError as ve:
        errors_list.append(f"Preis-Matrix-CSV: Wert-Konvertierungsfehler: {ve}. Prüfen Sie Dezimal- und Tausendertrennzeichen.")
        return None
    except Exception as e:
        errors_list.append(f"Fehler beim Parsen der Preis-Matrix-CSV: {e}. Bitte Format und Inhalt prüfen (Trenner Semikolon ';', Dezimal Komma ',', Index 'Anzahl Module').")
        # traceback.print_exc() # Auskommentiert für produktiven Code, bei Bedarf für Entwicklung aktivieren
        return None

def parse_module_price_matrix_excel(excel_bytes: Optional[bytes], errors_list: List[str]) -> Optional[pd.DataFrame]:
    if not excel_bytes:
        errors_list.append("Preis-Matrix (Excel): Daten sind leer.")
        return None
    try:
        excel_file_like = io.BytesIO(excel_bytes)
        df = pd.read_excel(excel_file_like, index_col=0, header=0)
        if df.empty:
            errors_list.append("Preis-Matrix (Excel): Datei ist leer oder erste Spalte ('Anzahl Module') fehlt/ist leer.")
            return None
        df.index.name = 'Anzahl Module'
        df.index = pd.to_numeric(df.index, errors='coerce')
        df = df[df.index.notna()]
        if df.empty:
            errors_list.append("Preis-Matrix (Excel): Index enthält keine gültigen Zahlen oder ist leer.")
            return None
        df.index = df.index.astype(int)
        for col in df.columns:
            if df[col].dtype == 'object': # String-Spalten vor Konvertierung bereinigen
                # Entferne Tausendertrennzeichen (Punkte), ersetze Dezimalkomma durch Punkt
                df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce') # 'coerce' setzt ungültige Werte auf NaT/NaN
        df.dropna(axis=0, how='all', inplace=True) # Entferne Zeilen, die nur NaN enthalten
        df.dropna(axis=1, how='all', inplace=True) # Entferne Spalten, die nur NaN enthalten
        if df.empty:
            errors_list.append("Preis-Matrix (Excel): Nach Verarbeitung (Entfernung leerer Zeilen/Spalten und Typkonvertierung) ist die Matrix leer.")
            return None
        # print(f"CALCULATIONS: Preis-Matrix erfolgreich aus Excel-Bytes geparst. Shape: {df.shape}") # Bereinigt
        return df
    except ValueError as ve: errors_list.append(f"Preis-Matrix (Excel): Wert-Fehler beim Parsen: {ve}"); return None
    except Exception as e: errors_list.append(f"Preis-Matrix (Excel): Unbekannter Fehler beim Parsen: {e}"); traceback.print_exc(); return None

class AdvancedCalculationsIntegrator:
    """Integriert erweiterte Berechnungen in Dashboard und PDF"""
    
    def __init__(self):
        # Liste der erweiterten Berechnungen aus calculations.py
        self.advanced_calculations = {
            'degradation_analysis': {
                'name': 'Degradationsanalyse',
                'description': 'Berechnet die Leistungsabnahme über 25 Jahre',
                'category': 'technical'
            },
            'shading_analysis': {
                'name': 'Verschattungsanalyse',
                'description': 'Detaillierte Verschattungsberechnung',
                'category': 'technical'
            },
            'grid_interaction': {
                'name': 'Netzinteraktion',
                'description': 'Analyse der Netzeinspeisung und -bezug',
                'category': 'economic'
            },
            'battery_cycles': {
                'name': 'Batteriezyklen',
                'description': 'Berechnung der Ladezyklen und Lebensdauer',
                'category': 'storage'
            },
            'weather_impact': {
                'name': 'Wettereinfluss',
                'description': 'Einfluss von Wetterbedingungen auf Ertrag',
                'category': 'environmental'
            },
            'maintenance_schedule': {
                'name': 'Wartungsplan',
                'description': 'Optimaler Wartungsplan und Kosten',
                'category': 'operational'
            },
            'carbon_footprint': {
                'name': 'CO2-Bilanz',
                'description': 'Detaillierte CO2-Einsparungsberechnung',
                'category': 'environmental'
            },
            'peak_shaving': {
                'name': 'Lastspitzenkappung',
                'description': 'Potenzial zur Reduzierung von Lastspitzen',
                'category': 'optimization'
            },
            'dynamic_pricing': {
                'name': 'Dynamische Preise',
                'description': 'Optimierung bei variablen Strompreisen',
                'category': 'economic'
            },
            'energy_independence': {
                'name': 'Energieunabhängigkeit',
                'description': 'Analyse der Autarkie über Zeit',
                'category': 'strategic'
            },
            'recycling_potential': {
                'name': 'Recycling-Potenzial',
                'description': 'Analyse des Recyclingpotenzials der Anlagenteile',
                'category': 'environmental'
            }
        }
        
        # Berechnungsfunktionen mapping
        self.calculation_functions = {
            'degradation_analysis': self._calculate_degradation,
            'shading_analysis': self._calculate_shading,
            'grid_interaction': self._calculate_grid_interaction,
            'battery_cycles': self._calculate_battery_cycles,
            'weather_impact': self._calculate_weather_impact,
            'maintenance_schedule': self._calculate_maintenance,
            'carbon_footprint': self._calculate_carbon_footprint,
            'peak_shaving': self._calculate_peak_shaving,
            'dynamic_pricing': self._calculate_dynamic_pricing,
            'energy_independence': self._calculate_energy_independence,
            'recycling_potential': self.calculate_recycling_potential
        }
    
    def _calculate_degradation(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet die Degradation über 25 Jahre"""
        years = 25
        initial_power = base_data.get('anlage_kwp', 10) * 1000  # in Watt
        degradation_rate = 0.005  # 0.5% pro Jahr
        
        power_over_time = []
        energy_loss = []
        
        for year in range(years + 1):
            current_power = initial_power * (1 - degradation_rate) ** year
            power_over_time.append(current_power)
            
            if year > 0:
                annual_loss = (initial_power - current_power) * 1700  # kWh
                energy_loss.append(annual_loss)
        
        return {
            'years': list(range(years + 1)),
            'power_kw': [p / 1000 for p in power_over_time],
            'total_energy_loss_kwh': sum(energy_loss),
            'final_performance_percent': (power_over_time[-1] / initial_power) * 100,
            'average_degradation_rate': degradation_rate * 100
        }
    
    def _calculate_shading(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet detaillierte Verschattungsverluste"""
        # Beispielhafte Verschattungsanalyse
        hours_of_day = list(range(6, 20))  # 6:00 bis 19:00
        months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        
        shading_matrix = []
        for month_idx in range(12):
            month_shading = []
            for hour in hours_of_day:
                # Simulierte Verschattung basierend auf Sonnenstand
                base_shading = 0.1  # 10% Basis-Verschattung
                
                # Morgens und abends mehr Verschattung
                if hour < 9 or hour > 17:
                    base_shading += 0.2
                
                # Winter mehr Verschattung
                if month_idx in [0, 1, 10, 11]:
                    base_shading += 0.15
                
                month_shading.append(min(base_shading, 0.9))
            
            shading_matrix.append(month_shading)
        
        # Jährlicher Verschattungsverlust
        avg_shading = np.mean(shading_matrix)
        annual_loss_kwh = base_data.get('annual_pv_production_kwh', 10000) * avg_shading
        
        return {
            'hours': hours_of_day,
            'months': months,
            'shading_matrix': shading_matrix,
            'average_shading_percent': avg_shading * 100,
            'annual_shading_loss_kwh': annual_loss_kwh,
            'optimal_hours': [h for h in hours_of_day if 10 <= h <= 15]
        }
    
    def _calculate_grid_interaction(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert die Netzinteraktion"""
        monthly_production = base_data.get('monthly_production', [500] * 12)
        monthly_consumption = base_data.get('monthly_consumption', [400] * 12)
        
        grid_feed_in = []
        grid_purchase = []
        self_consumption = []
        
        for prod, cons in zip(monthly_production, monthly_consumption):
            if prod > cons:
                grid_feed_in.append(prod - cons)
                grid_purchase.append(0)
                self_consumption.append(cons)
            else:
                grid_feed_in.append(0)
                grid_purchase.append(cons - prod)
                self_consumption.append(prod)
        
        return {
            'months': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
            'grid_feed_in_kwh': grid_feed_in,
            'grid_purchase_kwh': grid_purchase,
            'self_consumption_kwh': self_consumption,
            'total_feed_in_kwh': sum(grid_feed_in),
            'total_purchase_kwh': sum(grid_purchase),
            'self_consumption_rate': sum(self_consumption) / sum(monthly_consumption) * 100,
            'grid_independence_rate': (1 - sum(grid_purchase) / sum(monthly_consumption)) * 100
        }
    
    def _calculate_battery_cycles(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Batteriezyklen und Lebensdauer"""
        battery_capacity = base_data.get('battery_capacity_kwh', 10)
        daily_cycles = 1.2  # Durchschnittliche Zyklen pro Tag
        
        annual_cycles = daily_cycles * 365
        cycle_life = 6000  # Typische Zyklenlebensdauer
        
        expected_lifetime_years = cycle_life / annual_cycles
        
        # Degradation über Zeit
        years = list(range(int(expected_lifetime_years) + 1))
        capacity_over_time = []
        
        for year in years:
            # 80% Kapazität nach Zyklenlebensdauer
            remaining_capacity = 100 - (20 * year / expected_lifetime_years)
            capacity_over_time.append(max(80, remaining_capacity))
        
        return {
            'battery_capacity_kwh': battery_capacity,
            'daily_cycles': daily_cycles,
            'annual_cycles': annual_cycles,
            'expected_lifetime_years': expected_lifetime_years,
            'years': years,
            'capacity_percent': capacity_over_time,
            'replacement_year': int(expected_lifetime_years),
            'total_energy_throughput_mwh': battery_capacity * cycle_life / 1000
        }
    
    def _calculate_weather_impact(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet den Einfluss von Wetterbedingungen"""
        # Wetter-Faktoren für verschiedene Bedingungen
        weather_factors = {
            'sunny': 1.0,
            'partly_cloudy': 0.75,
            'cloudy': 0.4,
            'rainy': 0.25,
            'snowy': 0.1
        }
        
        # Typische Wetterverteilung (Tage pro Jahr)
        weather_distribution = {
            'sunny': 90,
            'partly_cloudy': 120,
            'cloudy': 80,
            'rainy': 60,
            'snowy': 15
        }
        
        # Berechnung des gewichteten Durchschnitts
        total_days = sum(weather_distribution.values())
        weighted_factor = sum(
            days * weather_factors[weather] 
            for weather, days in weather_distribution.items()
        ) / total_days
        
        # Einfluss auf Jahresertrag
        ideal_production = base_data.get('annual_pv_production_kwh', 10000)
        actual_production = ideal_production * weighted_factor
        
        return {
            'weather_types': list(weather_factors.keys()),
            'production_factors': list(weather_factors.values()),
            'days_per_year': list(weather_distribution.values()),
            'weighted_average_factor': weighted_factor,
            'ideal_production_kwh': ideal_production,
            'weather_adjusted_production_kwh': actual_production,
            'production_loss_kwh': ideal_production - actual_production,
            'efficiency_percent': weighted_factor * 100
        }
    
    def _calculate_maintenance(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt einen Wartungsplan mit Kosten"""
        system_size_kwp = base_data.get('anlage_kwp', 10)
        
        # Wartungsaktivitäten
        maintenance_tasks = {
            'visual_inspection': {
                'interval_months': 6,
                'cost_per_kwp': 5,
                'duration_hours': 1
            },
            'cleaning': {
                'interval_months': 12,
                'cost_per_kwp': 10,
                'duration_hours': 2
            },
            'electrical_check': {
                'interval_months': 12,
                'cost_per_kwp': 15,
                'duration_hours': 3
            },
            'inverter_service': {
                'interval_months': 24,
                'cost_per_kwp': 20,
                'duration_hours': 4
            },
            'full_system_check': {
                'interval_months': 60,
                'cost_per_kwp': 50,
                'duration_hours': 8
            }
        }
        
        # 10-Jahres-Plan erstellen
        maintenance_schedule = []
        total_cost = 0
        
        for month in range(1, 121):  # 10 Jahre
            for task, details in maintenance_tasks.items():
                if month % details['interval_months'] == 0:
                    cost = details['cost_per_kwp'] * system_size_kwp
                    maintenance_schedule.append({
                        'month': month,
                        'year': (month - 1) // 12 + 1,
                        'task': task,
                        'cost': cost,
                        'duration_hours': details['duration_hours']
                    })
                    total_cost += cost
        
        # Jahreskosten
        annual_costs = {}
        for item in maintenance_schedule:
            year = item['year']
            if year not in annual_costs:
                annual_costs[year] = 0
            annual_costs[year] += item['cost']
        
        return {
            'schedule': maintenance_schedule,
            'total_cost_10_years': total_cost,
            'average_annual_cost': total_cost / 10,
            'annual_costs': annual_costs,
            'cost_per_kwp_per_year': (total_cost / 10) / system_size_kwp
        }
    
    def _calculate_carbon_footprint(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet detaillierte CO2-Bilanz"""
        annual_production = base_data.get('annual_pv_production_kwh', 10000)
        
        # CO2-Faktoren
        grid_co2_per_kwh = 0.4  # kg CO2/kWh für Strommix
        pv_production_co2 = 40  # g CO2/kWh für PV-Produktion
        
        # Herstellung
        system_size_kwp = base_data.get('anlage_kwp', 10)
        manufacturing_co2 = system_size_kwp * 1500  # kg CO2 pro kWp
        
        # Jährliche Einsparung
        annual_co2_saved = annual_production * grid_co2_per_kwh
        annual_co2_pv = annual_production * pv_production_co2 / 1000
        net_annual_saving = annual_co2_saved - annual_co2_pv
        
        # Amortisation der Herstellungs-CO2
        co2_payback_years = manufacturing_co2 / net_annual_saving
        
        # 25-Jahres-Bilanz
        lifetime_co2_saved = net_annual_saving * 25 - manufacturing_co2
        
        return {
            'manufacturing_co2_kg': manufacturing_co2,
            'annual_grid_co2_saved_kg': annual_co2_saved,
            'annual_pv_co2_kg': annual_co2_pv,
            'net_annual_co2_saved_kg': net_annual_saving,
            'co2_payback_years': co2_payback_years,
            'lifetime_co2_saved_tons': lifetime_co2_saved / 1000,
            'equivalent_trees_planted': int(lifetime_co2_saved / 20),  # 20kg CO2/Baum/Jahr
            'equivalent_car_km_saved': int(lifetime_co2_saved / 0.12)  # 120g CO2/km
        }
    
    def _calculate_peak_shaving(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Lastspitzenkappung"""
        # Beispielhafte Lastprofile
        hours = list(range(24))
        base_load = [0.3, 0.25, 0.2, 0.2, 0.25, 0.4, 0.7, 0.9,
                    1.0, 0.9, 0.8, 0.7, 0.8, 0.7, 0.6, 0.7,
                    0.9, 1.2, 1.0, 0.8, 0.6, 0.5, 0.4, 0.35]
        
        peak_power_kw = base_data.get('peak_power_kw', 5)
        battery_power_kw = base_data.get('battery_power_kw', 3)
        
        # Lastspitzen identifizieren
        peak_threshold = 0.8  # 80% der Maximallast
        peaks = [load for load in base_load if load > peak_threshold]
        
        # Potenzielle Einsparung
        shaved_load = []
        for load in base_load:
            if load > peak_threshold:
                shaved = min(load - peak_threshold, battery_power_kw / peak_power_kw)
                shaved_load.append(load - shaved)
            else:
                shaved_load.append(load)
        
        # Kostenersparnis (Leistungspreis)
        power_price_per_kw = 100  # EUR/kW/Jahr
        peak_reduction_kw = peak_power_kw * (max(base_load) - max(shaved_load))
        annual_savings = peak_reduction_kw * power_price_per_kw
        
        return {
            'hours': hours,
            'original_load_profile': base_load,
            'shaved_load_profile': shaved_load,
            'peak_reduction_kw': peak_reduction_kw,
            'peak_reduction_percent': (1 - max(shaved_load) / max(base_load)) * 100,
            'annual_cost_savings_eur': annual_savings,
            'battery_utilization_hours': len(peaks)
        }
    
    def _calculate_dynamic_pricing(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimierung bei dynamischen Strompreisen"""
        # Beispielhafte Strompreise über 24h
        hours = list(range(24))
        base_price = 0.30  # EUR/kWh
        
        # Preiskurve (niedrig nachts, hoch tagsüber)
        price_factors = []
        for hour in hours:
            if 0 <= hour < 6:
                factor = 0.6
            elif 6 <= hour < 9:
                factor = 1.2
            elif 9 <= hour < 17:
                factor = 0.9
            elif 17 <= hour < 21:
                factor = 1.4
            else:
                factor = 0.8
            price_factors.append(factor)
        
        hourly_prices = [base_price * factor for factor in price_factors]
        
        # Optimierungspotenzial mit Batterie
        battery_capacity = base_data.get('battery_capacity_kwh', 10)
        
        # Lade in günstigen Zeiten, entlade in teuren Zeiten
        charge_hours = [h for h, p in enumerate(hourly_prices) if p < base_price * 0.8]
        discharge_hours = [h for h, p in enumerate(hourly_prices) if p > base_price * 1.2]
        
        # Potenzielle Ersparnis
        avg_charge_price = np.mean([hourly_prices[h] for h in charge_hours])
        avg_discharge_price = np.mean([hourly_prices[h] for h in discharge_hours])
        
        daily_arbitrage = battery_capacity * 0.8 * (avg_discharge_price - avg_charge_price)
        annual_arbitrage = daily_arbitrage * 365
        
        return {
            'hours': hours,
            'hourly_prices_eur': hourly_prices,
            'average_price_eur': base_price,
            'charge_hours': charge_hours,
            'discharge_hours': discharge_hours,
            'daily_arbitrage_eur': daily_arbitrage,
            'annual_arbitrage_eur': annual_arbitrage,
            'price_spread_percent': ((avg_discharge_price - avg_charge_price) / base_price) * 100
        }
    
    def _calculate_energy_independence(self, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert Energieunabhängigkeit über Zeit"""
        years = list(range(1, 26))  # 25 Jahre
        
        # Basis-Parameter
        initial_self_consumption = base_data.get('self_supply_rate_percent', 30)
        battery_capacity = base_data.get('battery_capacity_kwh', 0)
        
        # Entwicklung über Zeit
        self_consumption_rates = []
        grid_dependency = []
        
        for year in years:
            # Mit Batterie steigt Eigenverbrauch
            if battery_capacity > 0:
                # Annahme: 2% Steigerung pro Jahr bis max 85%
                rate = min(85, initial_self_consumption + year * 2)
            else:
                # Ohne Batterie langsamer Anstieg
                rate = min(50, initial_self_consumption + year * 0.5)
            
            self_consumption_rates.append(rate)
            grid_dependency.append(100 - rate)
        
        # Wirtschaftliche Unabhängigkeit
        electricity_price_increase = 0.03  # 3% pro Jahr
        cost_without_pv = []
        cost_with_pv = []
        
        annual_consumption = base_data.get('annual_consumption_kwh', 5000)
        base_price = 0.30  # EUR/kWh
        
        for year in years:
            price = base_price * (1 + electricity_price_increase) ** year
            cost_without = annual_consumption * price
            cost_with = annual_consumption * (1 - self_consumption_rates[year-1]/100) * price
            
            cost_without_pv.append(cost_without)
            cost_with_pv.append(cost_with)
        
        return {
            'years': years,
            'self_consumption_rates': self_consumption_rates,
            'grid_dependency_rates': grid_dependency,
            'annual_costs_without_pv': cost_without_pv,
            'annual_costs_with_pv': cost_with_pv,
            'cumulative_savings': np.cumsum(np.array(cost_without_pv) - np.array(cost_with_pv)).tolist(),            'average_independence_rate': np.mean(self_consumption_rates),
            'final_independence_rate': self_consumption_rates[-1]
        }
    
    def calculate_shading_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub für Verschattungsanalyse - noch nicht implementiert"""
        # Simulierte Werte für Testing
        annual_production = project_data.get('expected_annual_production', 10000)
        shading_loss_percent = 5.2
        energy_loss_kwh = annual_production * (shading_loss_percent / 100)
        
        return {
            'shading_matrix': [[10, 15, 20] * 4 for _ in range(12)],  # Dummy 12x12 Matrix
            'annual_shading_loss': shading_loss_percent,
            'energy_loss_kwh': energy_loss_kwh,  # Fehlender Key hinzugefügt
            'seasonal_variations': {'winter': 8.1, 'summer': 3.4},
            'worst_case_month': 'Dezember',
            'worst_month': 'Dezember',  # Alias für worst_case_month
            'worst_month_loss': 8.1,  # Verlust im schlechtesten Monat
            'optimization_potential': energy_loss_kwh * 0.3  # 30% des Verlustes könnte optimiert werden
        }
    
    def calculate_subsidy_scenarios(self, calc_results: Dict[str, Any]) -> Dict[str, Any]:
        """Stub für Förderszenarien - noch nicht implementiert"""
        return {
            'scenarios': {
                'Jahr': list(range(1, 21)),
                'Ohne Förderung': [i * 1000 for i in range(1, 21)],
                'Mit KfW-Förderung': [i * 1200 for i in range(1, 21)],
                'Mit regionaler Förderung': [i * 1100 for i in range(1, 21)]
            },            'comparison': [
                {'Szenario': 'Ohne Förderung', 'NPV': 25000, 'IRR': 6.2, 'Amortisation': 12.5, 'Förderung': 0},
                {'Szenario': 'Mit KfW-Förderung', 'NPV': 35000, 'IRR': 8.1, 'Amortisation': 10.2, 'Förderung': 5000},
                {'Szenario': 'Mit regionaler Förderung', 'NPV': 30000, 'IRR': 7.3, 'Amortisation': 11.1, 'Förderung': 2500}
            ]
        }
    
    def generate_optimization_suggestions(self, calc_results: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub für Optimierungsvorschläge - noch nicht implementiert"""
        return {
            'optimization_potentials': [
                {
                    'category': 'Technisch',
                    'description': 'Optimale Modulausrichtung',
                    'implementation_effort': 30,
                    'benefit_potential': 800,
                    'roi_improvement': 1.2,
                    'cost_estimate': 500
                },
                {
                    'category': 'Wirtschaftlich',
                    'description': 'Batteriespeicher optimieren',
                    'implementation_effort': 70,
                    'benefit_potential': 1200,
                    'roi_improvement': 2.1,
                    'cost_estimate': 3000
                }
            ],            'top_recommendations': [
                {
                    'priority': 1,
                    'title': 'Modulausrichtung optimieren',
                    'description': 'Anpassung der Neigung für höhere Erträge',
                    'annual_benefit': 800,  # Key korrigiert von 'potential_benefit'
                    'investment': 500,      # Key korrigiert von 'implementation_cost'
                    'payback': 0.6,         # Key korrigiert von 'payback_time' (Jahre statt Monate)
                    'roi_improvement': 12.5, # Prozent ROI-Verbesserung
                    'difficulty': 'Einfach'  # Neuer Key für Schwierigkeitsgrad
                },
                {
                    'priority': 2,
                    'title': 'Batteriespeicher erweitern',
                    'description': 'Erhöhung der Speicherkapazität für bessere Eigennutzung',
                    'annual_benefit': 1200,
                    'investment': 3000,
                    'payback': 2.5,
                    'roi_improvement': 8.3,
                    'difficulty': 'Mittel'  # Neuer Key für Schwierigkeitsgrad
                },                {
                    'priority': 3,
                    'title': 'Optimiertes Energiemanagement',
                    'description': 'Intelligente Steuerung für Verbrauchsoptimierung',
                    'annual_benefit': 600,
                    'investment': 1500,
                    'payback': 2.5,
                    'roi_improvement': 5.2,
                    'difficulty': 'Komplex'  # Neuer Key für Schwierigkeitsgrad
                }
            ],
            'system_optimization': {
                'optimal_tilt': 35,
                'optimal_azimuth': 0,
                'optimal_battery_size': 8.5,
                'optimal_dc_ac_ratio': 1.25
            }
        }
    
    def calculate_detailed_co2_analysis(self, calc_results: Dict[str, Any]) -> Dict[str, Any]:
        """Stub für detaillierte CO2-Analyse - noch nicht implementiert"""
        annual_production = calc_results.get('annual_pv_production_kwh', 8000)
        years = list(range(1, 26))
        
        return {
            'years': years,
            'cumulative_savings': [i * annual_production * 0.474 / 1000 for i in years],  # t CO2
            'production_emissions': 2.5,  # t CO2 für Herstellung
            'carbon_payback_time': 2.3,
            'total_co2_savings': annual_production * 25 * 0.474 / 1000,
            'tree_equivalent': int(annual_production * 25 * 0.474 / 22),  # 22kg CO2 pro Baum/Jahr
            'car_km_equivalent': int(annual_production * 25 * 0.474 / 0.12),  # 120g CO2/km
            'primary_energy_saved': annual_production * 25 * 2.5,  # kWh
            'water_saved': annual_production * 25 * 1.2,  # Liter
            'so2_avoided': annual_production * 25 * 0.474 * 0.001,  # kg
            'nox_avoided': annual_production * 25 * 0.474 * 0.0008,  # kg
            'particulates_avoided': annual_production * 25 * 0.474 * 0.00005  # kg
        }
    
    def calculate_recycling_potential(self, calc_results: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stub für Recycling-Potenzial - noch nicht implementiert"""
        system_kwp = calc_results.get('anlage_kwp', 10.0)
        
        # Beispiel-Materialzusammensetzung basierend auf Anlagengröße
        silicon_weight = system_kwp * 15  # kg Silizium pro kWp
        aluminum_weight = system_kwp * 25  # kg Aluminium pro kWp
        glass_weight = system_kwp * 50    # kg Glas pro kWp
        plastic_weight = system_kwp * 8   # kg Kunststoff pro kWp
        
        return {
            'material_composition': [
                {'material': 'Silizium', 'weight_kg': silicon_weight, 'recyclable': True, 'value_per_kg': 15.0},
                {'material': 'Aluminium', 'weight_kg': aluminum_weight, 'recyclable': True, 'value_per_kg': 2.5},
                {'material': 'Glas', 'weight_kg': glass_weight, 'recyclable': True, 'value_per_kg': 0.1},
                {'material': 'Kunststoff', 'weight_kg': plastic_weight, 'recyclable': False, 'value_per_kg': 0.0}
            ],
            'recycling_rate': 85.0,  # Prozent recycelbar
            'material_value': (silicon_weight * 15.0 + aluminum_weight * 2.5 + glass_weight * 0.1),
            'co2_savings_recycling': system_kwp * 0.5,  # Tonnen CO2-Einsparung durch Recycling
            'end_of_life_cost': system_kwp * 50,  # Kosten für Entsorgung
            'recycling_revenue': system_kwp * 75   # Erlös aus Recycling
        }

    # ...existing code...
def format_kpi_value(value: Any, unit: str = "", na_text_key: str = "data_not_available_short", precision: int = 2, texts_dict: Optional[Dict[str,str]] = None) -> str:
    current_texts = texts_dict if texts_dict is not None else {}
    na_text = current_texts.get(na_text_key, "N/A")

    if value is None: return na_text
    if isinstance(value, (float, int)) and math.isnan(value): return na_text # Expliziter NaN-Check

    if isinstance(value, str):
        try:
            # Bereinigung für Zahlen im String-Format (z.B. "1.234,56" oder "1,234.56")
            cleaned_value_str = value
            if '.' in value and ',' in value: # Enthält sowohl Punkt als auch Komma
                 # Annahme: Punkt ist Tausendertrenner, Komma ist Dezimaltrennzeichen (deutsche Notation)
                 # oder Komma ist Tausendertrenner, Punkt ist Dezimaltrennzeichen (englische Notation)
                 if value.rfind('.') > value.rfind(','): # Punkt ist weiter rechts -> Punkt ist Dezimaltrennzeichen (englisch)
                    cleaned_value_str = value.replace(',', '') # Entferne Kommas (Tausendertrenner)
                 elif value.rfind(',') > value.rfind('.'): # Komma ist weiter rechts -> Komma ist Dezimaltrennzeichen (deutsch)
                    cleaned_value_str = value.replace('.', '') # Entferne Punkte (Tausendertrenner)
            # Ersetze verbleibendes Komma (falls deutsch) durch Punkt für float()
            cleaned_value_str = cleaned_value_str.replace(',', '.')
            value_float = float(cleaned_value_str)
            value = value_float # Konvertiere zu float für die weitere Formatierung
        except ValueError:
            return value # Wenn Konvertierung fehlschlägt, Originalstring zurückgeben

    if isinstance(value, (int, float)):
        if math.isinf(value): return current_texts.get("value_infinite", "Nicht berechenbar")
        if unit == "Jahre":
            return (current_texts.get("years_format_string", "{val:.1f} Jahre") or "{val:.1f} Jahre").format(val=value)

        # Formatierung für deutsche Zahlen (Punkt als Tausendertrenner, Komma als Dezimal)
        formatted_num_en = f"{value:,.{precision}f}" # Standard englische Formatierung
        # Konvertiere zu deutscher Notation
        formatted_num_de = formatted_num_en.replace(",", "#TEMP#").replace(".", ",").replace("#TEMP#", ".")
        return f"{formatted_num_de} {unit}".strip()
    return str(value)

def convert_orientation_to_pvgis_azimuth(orientation_text: Optional[str]) -> int:
    """Konvertiert Text-Ausrichtung (z.B. 'Süd', 'Ost-West') in PVGIS Azimut-Werte."""
    if orientation_text is None or not str(orientation_text).strip():
        return 0 # Standardmäßig Süd

    ot_lower = str(orientation_text).lower().strip()

    # Exakte und gängige Abkürzungen zuerst
    mapping = {
        "süd": 0, "s": 0,
        "nord": 180, "n": 180,
        "ost": -90, "o": -90,
        "west": 90, "w": 90,
        "südost": -45, "süd-ost": -45, "so": -45,
        "südwest": 45, "süd-west": 45, "sw": 45,
        "nordost": -135, "nord-ost": -135, "no": -135,
        "nordwest": 135, "nord-west": 135, "nw": 135,
        "flachdach (ost-west)": -90, # Spezifisch für O-W Ausrichtung auf Flachdach
        "flachdach (o-w)": -90,
        "flachdach": 0 # Standard Flachdach oft leicht nach Süden ausgerichtet oder optimal
    }
    for key, val in mapping.items():
        if key in ot_lower:
            return val
    return 0 # Fallback auf Süd

def get_pvgis_data(
    latitude: float, longitude: float, peak_power_kwp: float,
    tilt: int, azimuth: int, system_loss_percent: float = 14.0,
    texts: Optional[Dict[str,str]] = None, errors_list: Optional[List[str]] = None,
    debug_mode_enabled: bool = False
) -> Optional[Dict[str, Any]]:
    """Holt PV-Produktionsdaten von der PVGIS API."""
    local_errors: List[str] = [] # Für interne Fehler dieser Funktion
    texts = texts if texts is not None else {} # Sicherstellen, dass texts ein Dict ist
    effective_errors_list = errors_list if errors_list is not None else local_errors

    # Validierung der Eingabeparameter
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        actual_error_msg = (texts.get("pvgis_invalid_lat_lon", "PVGIS: Ungültige Breiten- oder Längengrade.") or "") + f" (Lat: {latitude}, Lon: {longitude})"
        effective_errors_list.append(actual_error_msg)
        # if debug_mode_enabled: print(f"PVGIS Error: {actual_error_msg}") # Bereinigt
        return None
    if peak_power_kwp <= 0:
        actual_error_msg = texts.get("pvgis_invalid_peak_power", "PVGIS: Installierte Leistung muss positiv sein.") or ""
        effective_errors_list.append(actual_error_msg)
        # if debug_mode_enabled: print(f"PVGIS Error: {actual_error_msg}") # Bereinigt
        return None

    base_url = "https://re.jrc.ec.europa.eu/api/seriescalc"
    params = {
        "lat": latitude, "lon": longitude, "peakpower": peak_power_kwp, "loss": system_loss_percent,
        "pvtechchoice": "crystSi", "mountingplace": "building", "angle": tilt, "aspect": azimuth,
        "outputformat": "json", "browser": 0 # Wichtig, um HTML-Antworten zu vermeiden
    }

    # if debug_mode_enabled: # Bereinigt
    #     try:
    #         prepared_request = requests.Request('GET', base_url, params=params).prepare()
    #         print(f"PVGIS Anfrage URL: {prepared_request.url}")
    #     except Exception as e_prep:
    #         print(f"PVGIS: Fehler Vorbereitung Request-URL: {e_prep}")

    error_msg_pvgis = "" # Initialisiere Fehlermeldung

    try:
        response = requests.get(base_url, params=params, timeout=25) # Timeout von 25 Sekunden

        # if debug_mode_enabled: print(f"PVGIS Response Status Code: {response.status_code}") # Bereinigt

        response.raise_for_status() # Löst HTTPError für 4xx/5xx Status Codes
        data = response.json()

        # if debug_mode_enabled: # Bereinigt
        #     try:
        #         print(f"PVGIS JSON Antwort (Auszug): {json.dumps(data.get('outputs', {}).get('totals', {}), indent=2, ensure_ascii=False)}")
        #     except Exception as e_json_debug:
        #         print(f"PVGIS: Fehler Ausgabe JSON-Antwort: {e_json_debug}")

        monthly_production_kwh = [m.get("E_m", 0.0) for m in data.get("outputs", {}).get("monthly", [])]
        annual_production_kwh = data.get("outputs", {}).get("totals", {}).get("fixed", {}).get("E_y", 0.0)
        specific_yield_kwh_kwp_pa = data.get("outputs", {}).get("totals", {}).get("fixed", {}).get("Yield_y", 0.0) # Korrigierter Key 'Yield_y'

        if not monthly_production_kwh or len(monthly_production_kwh) != 12 or (annual_production_kwh == 0.0 and peak_power_kwp > 0) :
            error_msg_pvgis = texts.get("pvgis_incomplete_data", "PVGIS: Antwort erhalten, aber Daten scheinen unvollständig oder null.") or ""
            # if debug_mode_enabled: print(f"PVGIS: Unvollständige Daten: monthly_empty={not monthly_production_kwh}, len_monthly={len(monthly_production_kwh)}, annual_zero={annual_production_kwh == 0 and peak_power_kwp > 0}") # Bereinigt
            effective_errors_list.append(error_msg_pvgis)
            return None

        return {
            "monthly_production_kwh": monthly_production_kwh,
            "annual_production_kwh": annual_production_kwh,
            "specific_yield_kwh_kwp_pa": specific_yield_kwh_kwp_pa,
            "pvgis_source": data.get("meta", {}).get("source", "PVGIS-TMY") # Quelle der Daten (z.B. TMY, ERA5)
        }

    except requests.exceptions.HTTPError as e_http:
        status_code_val = e_http.response.status_code if e_http.response is not None else "N/A"
        error_msg_pvgis = (texts.get("pvgis_http_error", "PVGIS API HTTP-Fehler") or "") + f": Status {status_code_val}"
        response_text_detail = ""
        if e_http.response is not None: # Response-Objekt könnte None sein
            try: response_text_detail = e_http.response.json().get('message', e_http.response.text)
            except json.JSONDecodeError: response_text_detail = e_http.response.text
            except Exception: response_text_detail = "Konnte Fehlerdetails nicht extrahieren."
        error_msg_pvgis += f" - Details: {response_text_detail[:200]}" # Begrenze Länge
    except requests.exceptions.Timeout:
        error_msg_pvgis = texts.get("pvgis_timeout_error", "PVGIS API Zeitüberschreitung (Timeout nach 25s). Bitte Netzwerkverbindung prüfen.") or ""
    except requests.exceptions.ConnectionError as e_conn:
        error_msg_pvgis = (texts.get("pvgis_connection_error", "PVGIS API Verbindungsfehler. Ist das Internet verfügbar und die API erreichbar?") or "") + f" Details: {e_conn}"
    except requests.exceptions.RequestException as e_req: # Allgemeinerer Request-Fehler
        error_msg_pvgis = (texts.get("pvgis_request_error", "PVGIS API Allgemeiner Anfragefehler.") or "") + f" Details: {e_req}"
    except json.JSONDecodeError:
        error_msg_pvgis = texts.get("pvgis_json_decode_error", "PVGIS API: Fehler beim Lesen der JSON-Antwort. Möglicherweise temporäres API-Problem.") or ""
    except Exception as e_pvgis_unknown:
        error_msg_pvgis = (texts.get("pvgis_unknown_error", "PVGIS API: Unbekannter Fehler.") or "") + f" Details: {e_pvgis_unknown}"
        # if debug_mode_enabled: traceback.print_exc() # Bereinigt

    if error_msg_pvgis: # Nur wenn ein Fehler aufgetreten ist
        effective_errors_list.append(error_msg_pvgis)
        # if debug_mode_enabled: print(f"PVGIS Fehler: {error_msg_pvgis}") # Bereinigt
    return None

def perform_calculations(
    project_data: Dict[str, Any], texts: Dict[str, str], errors_list: List[str],
    simulation_duration_user: Optional[int] = None, electricity_price_increase_user: Optional[float] = None
) -> Dict[str, Any]:
    results: Dict[str, Any] = {"calculation_errors": errors_list}
    customer_data = project_data.get('customer_data', {})
    project_details = project_data.get('project_details', {})
    economic_data = project_data.get('economic_data', {})

    # KORREKTUR: Definition von module_quantity an den Anfang verschieben
    # Anlagengröße (Modulanzahl wird früh benötigt)
    module_quantity = int(project_details.get('module_quantity', 0) or 0)
    # selected_module_id wird später für die Kapazität benötigt, aber die Anzahl ist jetzt schon da.

    global_constants = real_load_admin_setting('global_constants')
    if not isinstance(global_constants, dict) or not global_constants:
        global_constants = Dummy_load_admin_setting_calc('global_constants')
        errors_list.append(texts.get("warn_global_constants_fallback", "Warnung: Fallback für globale Konstanten verwendet."))

    app_debug_mode_is_enabled = global_constants.get('app_debug_mode_enabled', False)
    if not isinstance(app_debug_mode_is_enabled, bool): 
        app_debug_mode_is_enabled = False
    # --- Preis-Matrix laden ---
    price_matrix_df_for_lookup: Optional[pd.DataFrame] = None
    price_matrix_excel_bytes = real_load_admin_setting('price_matrix_excel_bytes', None) # Aus DB laden (Bytes)
    price_matrix_csv_content = real_load_admin_setting('price_matrix_csv_data', "") # Aus DB laden (String)
    results['price_matrix_source_type'] = "Keine"

    if price_matrix_excel_bytes and isinstance(price_matrix_excel_bytes, bytes):
        # if app_debug_mode_is_enabled: print("CALC: Versuche, Preis-Matrix aus Excel-Bytes zu parsen.") # Bereinigt
        price_matrix_df_for_lookup = parse_module_price_matrix_excel(price_matrix_excel_bytes, errors_list)
        if price_matrix_df_for_lookup is not None and not price_matrix_df_for_lookup.empty:
            # if app_debug_mode_is_enabled: print("CALC: Preis-Matrix erfolgreich aus Excel-Bytes geladen.") # Bereinigt
            results['price_matrix_source_type'] = "Excel"
        else:
            # if app_debug_mode_is_enabled: errors_list.append("CALC: Parsen der Excel-Preis-Matrix fehlgeschlagen oder Ergebnis leer. Versuche CSV...") # Bereinigt
            price_matrix_df_for_lookup = None # Explizit zurücksetzen, falls Excel-Versuch fehlschlägt
    
    if price_matrix_df_for_lookup is None: # Nur wenn Excel nicht erfolgreich war oder nicht vorhanden
        if price_matrix_csv_content and isinstance(price_matrix_csv_content, str) and price_matrix_csv_content.strip():
            # if app_debug_mode_is_enabled: print("CALC: Kein Excel-Matrix oder Fehler, versuche Preis-Matrix aus CSV-Daten zu parsen.") # Bereinigt
            price_matrix_df_for_lookup = parse_module_price_matrix_csv(price_matrix_csv_content, errors_list)
            if price_matrix_df_for_lookup is not None and not price_matrix_df_for_lookup.empty:
                # if app_debug_mode_is_enabled: print("CALC: Preis-Matrix erfolgreich aus CSV-Daten geladen.") # Bereinigt
                results['price_matrix_source_type'] = "CSV"
            else:
                # if app_debug_mode_is_enabled: errors_list.append("CALC: Parsen der CSV-Preis-Matrix fehlgeschlagen oder Ergebnis leer.") # Bereinigt
                price_matrix_df_for_lookup = None # Sicherstellen, dass es None ist bei Fehlschlag
        # elif app_debug_mode_is_enabled and price_matrix_excel_bytes is None : # Bereinigt
             # print("CALC: Weder Excel- noch CSV-Preis-Matrix-Daten in Admin-Settings gefunden.")

    results['price_matrix_loaded_successfully'] = price_matrix_df_for_lookup is not None and not price_matrix_df_for_lookup.empty
    # if app_debug_mode_is_enabled: print(f"CALC: Preis-Matrix für Lookup geladen: {results['price_matrix_loaded_successfully']} (Quelle: {results.get('price_matrix_source_type', 'Keine')})") # Bereinigt

    # Einspeisevergütungen laden
    feed_in_tariffs_block = real_load_admin_setting('feed_in_tariffs', Dummy_load_admin_setting_calc('feed_in_tariffs'))
    einspeiseverguetung_parts_data = feed_in_tariffs_block.get('parts', []) if isinstance(feed_in_tariffs_block, dict) else []
    einspeiseverguetung_full_data = feed_in_tariffs_block.get('full', []) if isinstance(feed_in_tariffs_block, dict) else []

    # Globale Konstanten extrahieren mit robusten Fallbacks
    DEFAULT_YIELD_KWH_PER_KWP_ANNUAL = float(global_constants.get('default_specific_yield_kwh_kwp', 950.0) or 950.0)
    simulation_period_years_default = int(global_constants.get('simulation_period_years', 20) or 20)
    results['simulation_period_years_effective'] = simulation_duration_user if simulation_duration_user is not None else int(economic_data.get('simulation_period_years', simulation_period_years_default) or simulation_period_years_default)
    electricity_price_increase_default_percent = float(global_constants.get('electricity_price_increase_annual_percent', 3.0) or 3.0)
    results['electricity_price_increase_rate_effective_percent'] = electricity_price_increase_user if electricity_price_increase_user is not None else float(economic_data.get('electricity_price_increase_annual_percent', electricity_price_increase_default_percent) or electricity_price_increase_default_percent)
    vat_rate_percent = float(global_constants.get('vat_rate_percent', 0.0) or 0.0)
    inflation_rate_percent = float(global_constants.get('inflation_rate_percent', 2.0) or 2.0)
    loan_interest_rate_percent = float(global_constants.get('loan_interest_rate_percent', 4.0) or 4.0)
    annual_module_degradation_percent = float(global_constants.get('annual_module_degradation_percent', 0.5) or 0.5)
    annual_degredation_factor = 1.0 - (annual_module_degradation_percent / 100.0)
    specific_yields_by_orientation_tilt = global_constants.get('specific_yields_by_orientation_tilt', {})
    if not isinstance(specific_yields_by_orientation_tilt, dict): # Fallback, falls Typ nicht stimmt
        specific_yields_by_orientation_tilt = Dummy_load_admin_setting_calc('global_constants')['specific_yields_by_orientation_tilt']
    global_yield_adjustment_percent = float(global_constants.get('global_yield_adjustment_percent', 0.0) or 0.0)

    # Projektdaten für Verbrauch und Strompreis
    jahresverbrauch_haushalt = float(project_details.get('annual_consumption_kwh_yr', 0.0) or 0.0)
    jahresverbrauch_heizung = float(project_details.get('consumption_heating_kwh_yr', 0.0) or 0.0)
    annual_consumption_kwh_yr = jahresverbrauch_haushalt + jahresverbrauch_heizung
    electricity_price_kwh = float(project_details.get('electricity_price_kwh', 0.30) or 0.30)
    results['total_consumption_kwh_yr'] = annual_consumption_kwh_yr # Für Diagramme oft benötigt
    results['jahresstromverbrauch_fuer_hochrechnung_kwh'], results['aktueller_strompreis_fuer_hochrechnung_euro_kwh'] = annual_consumption_kwh_yr, electricity_price_kwh

    # Anlagengröße
    selected_module_id = project_details.get('selected_module_id')
    module_details = real_get_product_by_id(selected_module_id) if selected_module_id else None
    module_capacity_w = float(module_details.get('capacity_w', 0.0) or 0.0) if module_details else 0.0
    results['anlage_kwp'] = (module_quantity * module_capacity_w) / 1000.0
    
        # Fallback: Neuberechnung, falls 'anlage_kwp' aus project_details fehlt oder 0 ist.
        # Dies ist die ursprüngliche Logik, die nun als Fallback dient.
       
        # Hinzufügen von Fehlermeldungen/Warnungen, wenn der Fallback verwendet wird oder null ergibt
       
    # PVGIS-Datenabruf oder manuelle Ertragsberechnung
    pvgis_results_data = None
    if project_details.get('latitude') is not None and project_details.get('longitude') is not None and results['anlage_kwp'] > 0:
        try:
            lat = float(project_details['latitude'])
            lon = float(project_details['longitude'])
            if abs(lat) < 1e-5 and abs(lon) < 1e-5: # Standardkoordinaten (0,0) sind meist ungültig für PVGIS
                 errors_list.append(texts.get("warn_pvgis_zero_coords", "PVGIS: Ungültige Standardkoordinaten (0,0) erhalten. Nutze manuelle Ertragsberechnung."))
            elif not (-90 <= lat <= 90 and -180 <= lon <= 180): # Gültigkeitsbereich prüfen
                 errors_list.append(texts.get("pvgis_invalid_lat_lon_range", "PVGIS: Breiten- oder Längengrade außerhalb des gültigen Bereichs."))
            else:
                tilt_val = int(project_details.get('roof_inclination_deg', 30) or 30)
                orientation_text_val = project_details.get('roof_orientation', 'Süd')
                azimuth_val = convert_orientation_to_pvgis_azimuth(orientation_text_val)
                SYSTEM_LOSS_PVGIS = float(global_constants.get('pvgis_system_loss_default_percent', 14.0) or 14.0)
                pvgis_results_data = get_pvgis_data(lat, lon, results['anlage_kwp'], tilt_val, azimuth_val, SYSTEM_LOSS_PVGIS, texts, errors_list, debug_mode_enabled=app_debug_mode_is_enabled)
        except (ValueError, TypeError) as e_coords:
            errors_list.append((texts.get("error_geocoding_conversion_calc", "Fehler Konvertierung Geodaten für PVGIS.") or "") + f" Details: {e_coords}")
            pvgis_results_data = None # Sicherstellen, dass es None ist bei Fehler

    annual_pv_production_kwh_base, monthly_pv_production_kwh_base = 0.0, [0.0]*12
    results['pvgis_data_used'] = False # Standardmäßig auf False setzen

    if pvgis_results_data and isinstance(pvgis_results_data, dict):
        annual_prod_pvgis = pvgis_results_data.get("annual_production_kwh")
        monthly_prod_pvgis = pvgis_results_data.get("monthly_production_kwh")
        if isinstance(annual_prod_pvgis, (int,float)) and isinstance(monthly_prod_pvgis, list) and len(monthly_prod_pvgis) == 12:
            if annual_prod_pvgis == 0.0 and results['anlage_kwp'] > 0: # Wenn PVGIS 0 liefert trotz Anlage
                # if app_debug_mode_is_enabled and not any("PVGIS" in err for err in errors_list): # Bereinigt
                     # errors_list.append(texts.get("warn_pvgis_returned_zero_yield_fallback", "PVGIS lieferte 0 kWh Ertrag. Nutze manuelle Ertragsberechnung."))
                pass # Fehler wurde bereits in get_pvgis_data behandelt oder es wird der manuelle Fallback genutzt
            else:
                annual_pv_production_kwh_base = annual_prod_pvgis
                monthly_pv_production_kwh_base = monthly_prod_pvgis
                results['specific_annual_yield_kwh_per_kwp'] = pvgis_results_data.get("specific_yield_kwh_kwp_pa", 0.0)
                results['pvgis_source'] = pvgis_results_data.get("pvgis_source", "PVGIS")
                results['pvgis_data_used'] = True
        # else: # Bereinigt
            # if app_debug_mode_is_enabled:
                # errors_list.append(texts.get("warn_pvgis_incomplete_data_fallback", "PVGIS-Antwort unvollständig/fehlerhaft. Nutze manuelle Ertragsberechnung."))

    if not results['pvgis_data_used'] and results['anlage_kwp'] > 0: # Fallback zur manuellen Berechnung
        # if project_details.get('latitude') is not None and app_debug_mode_is_enabled and not any("PVGIS" in err for err in errors_list): # Bereinigt
            # errors_list.append(texts.get("info_pvgis_unavailable_manual_fallback", "PVGIS nicht verfügbar/genutzt. Nutze manuelle Ertragsberechnung."))
        orientation_key = project_details.get('roof_orientation', 'Sonstige') # Default auf 'Sonstige'
        tilt_val_manual = project_details.get('roof_inclination_deg', 30) # Default auf 30 Grad
        tilt_key_manual = int(tilt_val_manual or 30) # Sicherstellen, dass es ein Int ist
        lookup_key = f"{orientation_key}_{tilt_key_manual}"
        specific_yields_map = global_constants.get('specific_yields_by_orientation_tilt', {})
        if not isinstance(specific_yields_map, dict): # Fallback, falls Typ nicht stimmt
            specific_yields_map = Dummy_load_admin_setting_calc('global_constants')['specific_yields_by_orientation_tilt']
        specific_annual_yield_kwh_per_kwp_manual = float(specific_yields_map.get(lookup_key, DEFAULT_YIELD_KWH_PER_KWP_ANNUAL) or DEFAULT_YIELD_KWH_PER_KWP_ANNUAL)
        annual_pv_production_kwh_base = results['anlage_kwp'] * specific_annual_yield_kwh_per_kwp_manual
        results['specific_annual_yield_kwh_per_kwp'] = specific_annual_yield_kwh_per_kwp_manual
        monthly_distribution_factors = global_constants.get('monthly_production_distribution', [1/12]*12)
        if not isinstance(monthly_distribution_factors, list) or len(monthly_distribution_factors) != 12 or not all(isinstance(x, (int, float)) for x in monthly_distribution_factors):
            monthly_distribution_factors = [1/12]*12 # Robuster Fallback
            errors_list.append(texts.get("warn_invalid_monthly_distribution", "Ungültige monatliche Produktionsverteilung in Konstanten, nutze gleichmäßige Verteilung."))
        sum_factors = sum(monthly_distribution_factors) # Normierung, falls Summe nicht 1
        normalized_monthly_distribution = [f / sum_factors for f in monthly_distribution_factors] if sum_factors > 0 else [1/12]*12
        monthly_pv_production_kwh_base = [annual_pv_production_kwh_base * factor for factor in normalized_monthly_distribution]
        results['pvgis_source'] = "Manuelle Berechnung" # Quelle klarstellen
        # if app_debug_mode_is_enabled: # Bereinigt
            # print(f"CALC: Manuelle Ertragsberechnung: lookup_key='{lookup_key}', specific_yield={specific_annual_yield_kwh_per_kwp_manual} kWh/kWp/a")
    elif results['anlage_kwp'] == 0: # Keine Anlage, keine Produktion
        annual_pv_production_kwh_base = 0.0
        monthly_pv_production_kwh_base = [0.0] * 12
        results['specific_annual_yield_kwh_per_kwp'] = 0.0
        results['pvgis_source'] = "Keine Anlage"
        # if app_debug_mode_is_enabled: print("CALC: Keine Anlagenleistung (0 kWp), daher keine Ertragsberechnung.") # Bereinigt

    # Globale Ertragsanpassung anwenden
    annual_pv_production_kwh = annual_pv_production_kwh_base * (1 + global_yield_adjustment_percent / 100.0)
    monthly_pv_production_kwh = [m_prod * (1 + global_yield_adjustment_percent / 100.0) for m_prod in monthly_pv_production_kwh_base]

    # if global_yield_adjustment_percent != 0.0 and app_debug_mode_is_enabled: # Bereinigt
        # errors_list.append((texts.get("info_global_yield_adjustment_applied", "Globale Ertragsanpassung von {percent}% wurde angewendet.") or "").format(percent=global_yield_adjustment_percent))

    results['annual_pv_production_kwh'] = annual_pv_production_kwh
    results['monthly_productions_sim'] = monthly_pv_production_kwh # Dies sind die Produktionsdaten für Jahr 1

    # if app_debug_mode_is_enabled: print(f"CALC: Jährliche PV Produktion (nach Anpassung, Jahr 1): {annual_pv_production_kwh:.2f} kWh") # Bereinigt

    # Monatlicher Verbrauch
    monthly_distribution_factors_consumption = global_constants.get('monthly_consumption_distribution', [1/12]*12)
    if not isinstance(monthly_distribution_factors_consumption, list) or len(monthly_distribution_factors_consumption) != 12 or not all(isinstance(x, (int, float)) for x in monthly_distribution_factors_consumption):
        monthly_distribution_factors_consumption = [1/12]*12 # Fallback
        errors_list.append(texts.get("warn_invalid_monthly_consumption_distribution", "Ungültige monatliche Verbrauchsverteilung, nutze gleichmäßige Verteilung."))
    sum_factors_cons = sum(monthly_distribution_factors_consumption)
    normalized_monthly_consumption_distribution = [f / sum_factors_cons for f in monthly_distribution_factors_consumption] if sum_factors_cons > 0 else [1/12]*12
    monthly_total_consumption_kwh = [annual_consumption_kwh_yr * factor for factor in normalized_monthly_consumption_distribution]
    results['monthly_consumption_sim'] = monthly_total_consumption_kwh # Monatlicher Verbrauch für Jahr 1

    # Eigenverbrauchsberechnung (vereinfacht, kann detaillierter werden)
    direct_sc_from_production_factor = float(global_constants.get('direct_self_consumption_factor_of_production', 0.25) or 0.25)
    include_storage = project_details.get('include_storage', False)
    selected_storage_id = project_details.get('selected_storage_id') if include_storage else None
    # Nutze die explizit im Projekt ausgewählte Kapazität, nicht die aus den Produktdetails für diese Logik
    selected_storage_capacity_kwh = float(project_details.get('selected_storage_storage_power_kw', 0.0) or 0.0) if include_storage else 0.0
    storage_efficiency = float(global_constants.get('storage_efficiency', 0.9) or 0.9) # Speicherwirkungsgrad

    monthly_direct_self_consumption_kwh = [0.0] * 12
    monthly_storage_charge_kwh = [0.0] * 12          # Wie viel in den Speicher geladen wird (Netto nach Ladeverlust)
    monthly_storage_discharge_for_sc_kwh = [0.0] * 12 # Wie viel aus dem Speicher für Eigenverbrauch entladen wird
    monthly_feed_in_kwh = [0.0] * 12
    monthly_grid_bezug_kwh = [0.0] * 12

    for i in range(12):
        prod_month = monthly_pv_production_kwh[i]
        cons_month = monthly_total_consumption_kwh[i]

        # Direkter Eigenverbrauch
        direct_sc = min(prod_month * direct_sc_from_production_factor, cons_month)
        monthly_direct_self_consumption_kwh[i] = direct_sc

        rem_prod_after_direct_sc = prod_month - direct_sc
        rem_cons_after_direct_sc = cons_month - direct_sc

        # Speicherlogik (vereinfacht: Speicher wird geladen, wenn Überschuss, und entladen, wenn Bedarf)
        if include_storage and selected_storage_capacity_kwh > 0:
            storage_cycles_per_year_val = float(global_constants.get('storage_cycles_per_year', 250) or 250)
            # Max. mögliche Ladung/Entladung pro Monat basierend auf Kapazität und Zyklen (vereinfacht)
            monthly_storage_charge_potential_effective = selected_storage_capacity_kwh * (storage_cycles_per_year_val / 12.0) # Max kWh die pro Monat theoretisch geladen/entladen werden könnten

            # Laden des Speichers
            # Wie viel kann *vor* Ladeverlusten in den Speicher?
            potential_charge_to_storage_brutto = min(rem_prod_after_direct_sc, monthly_storage_charge_potential_effective / storage_efficiency if storage_efficiency > 0 else float('inf'))
            # Tatsächliche Nettoladung unter Berücksichtigung des Wirkungsgrads
            actual_charge_into_storage_netto = potential_charge_to_storage_brutto * storage_efficiency
            monthly_storage_charge_kwh[i] = actual_charge_into_storage_netto # Gespeichert: wie viel *im* Speicher ankommt
            rem_prod_after_direct_sc -= potential_charge_to_storage_brutto # Vom Überschuss abziehen, was zum Laden verwendet wurde (brutto)

            # Entladen des Speichers für Eigenverbrauch
            discharge_from_storage_for_sc = min(actual_charge_into_storage_netto, rem_cons_after_direct_sc) # Kann max. das entladen, was geladen wurde und was gebraucht wird
            monthly_storage_discharge_for_sc_kwh[i] = discharge_from_storage_for_sc
            rem_cons_after_direct_sc -= discharge_from_storage_for_sc

        # Verbleibender Überschuss geht ins Netz, verbleibender Bedarf aus dem Netz
        monthly_feed_in_kwh[i] = max(0, rem_prod_after_direct_sc)
        monthly_grid_bezug_kwh[i] = max(0, rem_cons_after_direct_sc)

    eigenverbrauch_pro_jahr_kwh = sum(monthly_direct_self_consumption_kwh) + sum(monthly_storage_discharge_for_sc_kwh)
    netzeinspeisung_kwh = sum(monthly_feed_in_kwh)
    grid_bezug_kwh = sum(monthly_grid_bezug_kwh) # Netzbezug (kWh)
    results.update({
        'monthly_direct_self_consumption_kwh': monthly_direct_self_consumption_kwh,
        'monthly_storage_charge_kwh': monthly_storage_charge_kwh,
        'monthly_storage_discharge_for_sc_kwh': monthly_storage_discharge_for_sc_kwh,
        'monthly_feed_in_kwh': monthly_feed_in_kwh,
        'monthly_grid_bezug_kwh': monthly_grid_bezug_kwh,
        'eigenverbrauch_pro_jahr_kwh': eigenverbrauch_pro_jahr_kwh,
        'netzeinspeisung_kwh': netzeinspeisung_kwh, # Netzeinspeisung (kWh)
        'grid_bezug_kwh': grid_bezug_kwh
    })

    selected_inverter_id = project_details.get('selected_inverter_id')
    inverter_details = real_get_product_by_id(selected_inverter_id) if selected_inverter_id else None
    free_roof_area_sqm = float(project_details.get('free_roof_area_sqm', 0.0) or 0.0)

    # --- Kostenberechnung ---
    storage_details_from_db = real_get_product_by_id(selected_storage_id) if selected_storage_id and include_storage else None
    storage_name_for_matrix_lookup = texts.get("no_storage_option_for_matrix", "Ohne Speicher")
    if include_storage and storage_details_from_db and storage_details_from_db.get('model_name'):
        storage_name_for_matrix_lookup = storage_details_from_db.get('model_name')
    # elif include_storage and not storage_details_from_db and app_debug_mode_is_enabled and selected_storage_id: # Bereinigt
        # errors_list.append(f"CALC: Speicher (ID: {selected_storage_id}) ausgewählt, aber Details nicht in product_db gefunden. Matrix-Preis nutzt '{storage_name_for_matrix_lookup}'.")

    base_matrix_price_netto, matrix_column_used_for_price = 0.0, None
    if price_matrix_df_for_lookup is not None and not price_matrix_df_for_lookup.empty and module_quantity > 0:
        # Finde die passende Zeile in der Matrix (genau oder nächstkleinere Modulanzahl)
        relevant_rows_matrix = price_matrix_df_for_lookup[price_matrix_df_for_lookup.index <= module_quantity]
        if not relevant_rows_matrix.empty:
            selected_row_from_matrix = relevant_rows_matrix.iloc[-1] # Letzte Zeile, die Bedingung erfüllt
            actual_module_count_in_matrix = selected_row_from_matrix.name # Indexwert der Zeile (Modulanzahl)
            # if module_quantity != actual_module_count_in_matrix and app_debug_mode_is_enabled: # Bereinigt
                # errors_list.append(f"CALC: Für {module_quantity} Module wurde Matrix-Stufe '{actual_module_count_in_matrix}' Module verwendet.")

            # Spaltennamen normalisieren für robusten Zugriff
            normalized_matrix_columns_map = {str(col).strip().lower(): str(col) for col in selected_row_from_matrix.index}
            normalized_storage_name_lookup = str(storage_name_for_matrix_lookup).strip().lower()
            no_storage_text_normalized_lookup = texts.get("no_storage_option_for_matrix", "Ohne Speicher").strip().lower()

            # Original Spaltennamen aus der Map holen
            original_no_storage_column_name = normalized_matrix_columns_map.get(no_storage_text_normalized_lookup)
            original_price_col_key_for_df_access = normalized_matrix_columns_map.get(normalized_storage_name_lookup)
            price_value_from_matrix = None

            # Versuche Preis für spezifischen Speicher zu finden
            if original_price_col_key_for_df_access and original_price_col_key_for_df_access in selected_row_from_matrix.index and pd.notna(selected_row_from_matrix[original_price_col_key_for_df_access]):
                price_value_from_matrix = selected_row_from_matrix[original_price_col_key_for_df_access]
                matrix_column_used_for_price = original_price_col_key_for_df_access # Speichere den verwendeten Spaltennamen
            
            # Fallback auf "Ohne Speicher", wenn spezifischer Speicher nicht gefunden oder Preis ungültig
            if price_value_from_matrix is None or not pd.notna(price_value_from_matrix):
                # if normalized_storage_name_lookup != no_storage_text_normalized_lookup and include_storage : # Bereinigt (Fehlermeldung bereits informativ genug)
                     # errors_list.append((texts.get("warn_specific_storage_not_in_matrix_fallback_no_storage", "Preis für Speichermodell '{selected_storage_name}' bei {module_count} Modulen nicht in Matrix oder Wert ungültig. Versuche Fallback auf '{no_storage_option_text}'.") or "").format(selected_storage_name=storage_name_for_matrix_lookup, module_count=actual_module_count_in_matrix, no_storage_option_text=texts.get("no_storage_option_for_matrix", "Ohne Speicher")))
                if original_no_storage_column_name and original_no_storage_column_name in selected_row_from_matrix.index and pd.notna(selected_row_from_matrix[original_no_storage_column_name]):
                    price_value_from_matrix = selected_row_from_matrix[original_no_storage_column_name]
                    matrix_column_used_for_price = original_no_storage_column_name # Speichere "Ohne Speicher" als verwendeten Spaltennamen
                else: # Auch "Ohne Speicher" nicht gefunden oder ungültig
                    price_value_from_matrix = 0.0 # Sicherer Fallback
                    errors_list.append((texts.get("error_no_storage_column_or_price_not_found_in_matrix", "Fehler: Weder Preis für '{selected_storage_name}' noch für '{no_storage_option_text}' bei {module_count} Modulen in Matrix. Grundpreis 0€.") or "").format(selected_storage_name=storage_name_for_matrix_lookup, no_storage_option_text=texts.get("no_storage_option_for_matrix", "Ohne Speicher"), module_count=actual_module_count_in_matrix))
            
            try: # Konvertiere den gefundenen Preiswert sicher zu float
                base_matrix_price_netto = float(price_value_from_matrix if pd.notna(price_value_from_matrix) else 0.0)
            except (ValueError, TypeError):
                errors_list.append((texts.get("error_invalid_price_in_matrix_conversion", "Konnte Matrixpreis '{matrix_price_value}' nicht in Zahl umwandeln. Grundpreis 0€.") or "").format(matrix_price_value=price_value_from_matrix))
                base_matrix_price_netto = 0.0
        else: # Keine passende Modulanzahl in Matrix gefunden
            errors_list.append((texts.get("error_module_count_not_in_matrix", "Keine passende Modulanzahl (<= {module_quantity}) in Preis-Matrix gefunden. Grundpreis 0€.") or "").format(module_quantity=module_quantity))
    elif module_quantity > 0: # Matrix nicht geladen oder leer, aber Module vorhanden
        errors_list.append(texts.get("error_price_matrix_not_loaded_or_empty", "Preis-Matrix nicht geladen/leer oder ungültig. Grundpreis 0€."))

    results['base_matrix_price_netto'] = max(0.0, base_matrix_price_netto) # Sicherstellen, dass Preis nicht negativ ist
    # if app_debug_mode_is_enabled: print(f"CALC: Ermittelter base_matrix_price_netto: {results['base_matrix_price_netto']:.2f} € (verwendete Matrix-Spalte: '{matrix_column_used_for_price}')") # Bereinigt

    # Logik für Zusatzkosten, abhängig davon, ob ein Pauschalpreis aus der Matrix verwendet wurde
    matrix_price_is_pauschal = results['base_matrix_price_netto'] > 0 and matrix_column_used_for_price is not None
    # if app_debug_mode_is_enabled: print(f"CALC: matrix_price_is_pauschal: {matrix_price_is_pauschal}") # Bereinigt

    cost_modules_aufpreis_netto = 0.0
    cost_inverter_aufpreis_netto = 0.0
    cost_accessories_aufpreis_netto = 0.0
    cost_misc_netto = 0.0 # Sonstige Kosten

    if not matrix_price_is_pauschal: # Nur wenn KEIN Pauschalpreis aus der Matrix gilt
        cost_modules_aufpreis_netto = float(module_details.get('additional_cost_netto', 0.0) or 0.0) * module_quantity if module_details else 0.0
        cost_inverter_aufpreis_netto = float(inverter_details.get('additional_cost_netto', 0.0) or 0.0) if inverter_details else 0.0
        # Standard-Zusatzkosten, wenn nicht in Matrix enthalten
        cost_accessories_aufpreis_netto = float(global_constants.get('additional_components_flat_rate_netto', 500.0)or 500.0) # Zubehörpauschale
        cost_misc_netto = float(global_constants.get('misc_costs_flat_rate_netto', 200.0) or 200.0) # Sonstige Kosten Pauschale
    # elif app_debug_mode_is_enabled: # Bereinigt
        # errors_list.append("CALC: Gültiger Matrix-Pauschalpreis. Zusatzkosten Module, WR, Zubehör, Sonstige auf 0 (da im Pauschalpreis enthalten).")

    # Speicher-Zusatzkosten: Nur wenn Matrix "Ohne Speicher" verwendet wurde oder kein Matrixpreis UND Speicher gewünscht
    cost_storage_aufpreis_product_db_netto = 0.0
    if include_storage and storage_details_from_db:
        no_storage_text_for_check_lc_again = texts.get("no_storage_option_for_matrix", "Ohne Speicher").strip().lower()
        # Bedingung: Speicher ist gewünscht UND (Matrix-Spalte war "Ohne Speicher" ODER es gab gar keinen Matrixpreis)
        should_add_storage_db_cost_cond = (matrix_column_used_for_price and str(matrix_column_used_for_price).strip().lower() == no_storage_text_for_check_lc_again) or \
                                     (results['base_matrix_price_netto'] == 0.0 and matrix_column_used_for_price is None)
        if should_add_storage_db_cost_cond:
            cost_storage_aufpreis_product_db_netto = float(storage_details_from_db.get('additional_cost_netto', 0.0) or 0.0)
            # if app_debug_mode_is_enabled and cost_storage_aufpreis_product_db_netto > 0: # Bereinigt
                # errors_list.append(f"CALC: Zusatzkosten Speicher '{storage_details_from_db.get('model_name')}' aus DB ({cost_storage_aufpreis_product_db_netto:.2f}€) addiert (Matrix='Ohne Speicher' oder kein Matrixpreis).")
        # elif app_debug_mode_is_enabled and matrix_column_used_for_price and include_storage : # Bereinigt
            # errors_list.append(f"CALC: Matrixpreis für spezifischen Speicher '{matrix_column_used_for_price}' verwendet. KEINE separaten Speicherkosten aus DB addiert.")
    results['cost_storage_aufpreis_product_db_netto'] = cost_storage_aufpreis_product_db_netto
    # if app_debug_mode_is_enabled: print(f"CALC: cost_storage_aufpreis_product_db_netto={cost_storage_aufpreis_product_db_netto:.2f}") # Bereinigt

    # Weitere Kosten
    cost_scaffolding_netto = free_roof_area_sqm * float(global_constants.get('scaffolding_cost_per_sqm_gt_7m_netto', 20.0) or 20.0) if project_details.get('building_height_gt_7m', False) else 0.0
    cost_custom_netto = float(economic_data.get('custom_costs_netto', 0.0) or 0.0) # Manuelle Zusatzkosten

    # Optionale Komponenten
    total_optional_components_cost_netto = 0.0
    optional_component_keys_map_calc = {
        'selected_wallbox_id': 'cost_wallbox_aufpreis_netto',
        'selected_ems_id': 'cost_ems_aufpreis_netto',
        'selected_optimizer_id': 'cost_optimizer_aufpreis_netto', # Annahme: pauschal oder pro Modul * Menge? Hier pauschal.
        'selected_carport_id': 'cost_carport_aufpreis_netto',
        'selected_notstrom_id': 'cost_notstrom_aufpreis_netto',
        'selected_tierabwehr_id': 'cost_tierabwehr_aufpreis_netto'
    }
    if project_details.get('include_additional_components', False):
        for pd_key, res_key in optional_component_keys_map_calc.items():
            component_id = project_details.get(pd_key)
            cost_val = 0.0
            if component_id:
                component_details_db = real_get_product_by_id(component_id)
                cost_val = float(component_details_db.get('additional_cost_netto', 0.0) or 0.0) if component_details_db else 0.0
                # Spezifische Logik für Optimierer (Menge?) könnte hierhin
                # if pd_key == 'selected_optimizer_id' and module_quantity > 0: cost_val *= module_quantity # Beispiel
                total_optional_components_cost_netto += cost_val
            results[res_key] = cost_val # Speichere individuelle Kosten im Ergebnis
    # if app_debug_mode_is_enabled: print(f"CALC: total_optional_components_cost_netto={total_optional_components_cost_netto:.2f}") # Bereinigt

    # Summe aller Zusatzkosten (die nicht im Matrix-Pauschalpreis sind)
    total_additional_costs_netto = sum(filter(None, [
        cost_modules_aufpreis_netto, cost_inverter_aufpreis_netto,
        cost_storage_aufpreis_product_db_netto, # Diese werden nur addiert, wenn sie nicht im Matrixpreis sind
        cost_accessories_aufpreis_netto, cost_misc_netto,
        cost_scaffolding_netto, cost_custom_netto,
        total_optional_components_cost_netto
    ]))
    results.update({
        'cost_modules_aufpreis_netto': cost_modules_aufpreis_netto,
        'cost_inverter_aufpreis_netto': cost_inverter_aufpreis_netto,
        'cost_accessories_aufpreis_netto': cost_accessories_aufpreis_netto,
        'cost_misc_netto': cost_misc_netto,
        'cost_scaffolding_netto': cost_scaffolding_netto,
        'cost_custom_netto': cost_custom_netto,
        'total_optional_components_cost_netto': total_optional_components_cost_netto,
        'total_additional_costs_netto': total_additional_costs_netto
    })
    # if app_debug_mode_is_enabled: print(f"CALC: total_additional_costs_netto={total_additional_costs_netto:.2f}") # Bereinigt

    subtotal_netto = results['base_matrix_price_netto'] + total_additional_costs_netto
    results['subtotal_netto'] = subtotal_netto
    # if app_debug_mode_is_enabled: print(f"CALC: subtotal_netto (base_matrix + total_additional): {subtotal_netto:.2f}") # Bereinigt

    one_time_bonus_eur = float(global_constants.get('one_time_bonus_eur', 0.0) or 0.0)
    total_investment_netto = subtotal_netto - one_time_bonus_eur
    # if one_time_bonus_eur > 0 and app_debug_mode_is_enabled: # Bereinigt
        # errors_list.append((texts.get("info_one_time_bonus_applied", "Einmaliger Bonus von {bonus:.2f} € wurde von Nettoinvestition abgezogen.") or "").format(bonus=one_time_bonus_eur))

    results['total_investment_netto'] = total_investment_netto
    results['vat_rate_percent'] = vat_rate_percent # MwSt.-Satz
    results['total_investment_brutto'] = total_investment_netto * (1 + vat_rate_percent / 100.0)
    # if app_debug_mode_is_enabled: print(f"CALC: Endgültige Kosten: base_matrix={results['base_matrix_price_netto']:.2f}, total_additional={total_additional_costs_netto:.2f}, subtotal_netto={subtotal_netto:.2f}, total_investment_netto={total_investment_netto:.2f}, c={results['total_investment_brutto']:.2f}") # Bereinigt

    # --- Wirtschaftlichkeitsberechnung (Jahr 1) ---
    annual_electricity_cost_savings_self_consumption_year1 = eigenverbrauch_pro_jahr_kwh * electricity_price_kwh
    results['annual_electricity_cost_savings_self_consumption_year1'] = annual_electricity_cost_savings_self_consumption_year1

    # Einspeisevergütung bestimmen
    einspeiseverguetung_ct_per_kwh = 0.0
    feed_in_type_str = project_details.get('feed_in_type', 'Teileinspeisung') # Default auf Teileinspeisung
    einspeiseverguetung_data_to_use = einspeiseverguetung_parts_data if feed_in_type_str == 'Teileinspeisung' else einspeiseverguetung_full_data
    if results['anlage_kwp'] > 0 and einspeiseverguetung_data_to_use and isinstance(einspeiseverguetung_data_to_use, list):
        for entry in sorted(einspeiseverguetung_data_to_use, key=lambda x: float(x.get('kwp_max', 0.0) or 0.0)): # Sicherstellen, dass kwp_max ein Float ist
            if results['anlage_kwp'] <= float(entry.get('kwp_max', float('inf')) or float('inf')): # Sicherstellen, dass kwp_max ein Float ist
                einspeiseverguetung_ct_per_kwh = float(entry.get('ct_per_kwh', 0.0) or 0.0) # Sicherstellen, dass ct_per_kwh ein Float ist
                break
        if einspeiseverguetung_ct_per_kwh == 0.0 and einspeiseverguetung_data_to_use: # Wenn kein passender Tarif gefunden wurde, nimm den letzten
             einspeiseverguetung_ct_per_kwh = float(einspeiseverguetung_data_to_use[-1].get('ct_per_kwh',0.0) or 0.0)
    # elif not einspeiseverguetung_data_to_use and results['anlage_kwp'] > 0 and app_debug_mode_is_enabled: # Bereinigt
        # errors_list.append((texts.get("warn_no_feed_in_tariffs_defined", "Keine Einspeisevergütungen für Typ '{feed_in_type}' definiert.") or "").format(feed_in_type=feed_in_type_str))

    results['einspeiseverguetung_ct_per_kwh'] = einspeiseverguetung_ct_per_kwh
    results['einspeiseverguetung_eur_per_kwh'] = einspeiseverguetung_ct_per_kwh / 100.0
    annual_feed_in_revenue_year1 = netzeinspeisung_kwh * results['einspeiseverguetung_eur_per_kwh']
    results['annual_feed_in_revenue_year1'] = annual_feed_in_revenue_year1

    # Steuerlicher Vorteil (optional, falls gewerblich)
    tax_benefit_feed_in_year1 = 0.0
    income_tax_rate_percent = float(customer_data.get('income_tax_rate_percent', 0.0) or 0.0)
    if customer_data.get('type', 'Privat').lower() == 'gewerblich' and income_tax_rate_percent > 0:
        tax_benefit_feed_in_year1 = annual_feed_in_revenue_year1 * (income_tax_rate_percent / 100.0) # Vereinfachte Annahme
    results['tax_benefit_feed_in_year1'] = tax_benefit_feed_in_year1

    annual_financial_benefit_year1 = annual_electricity_cost_savings_self_consumption_year1 + annual_feed_in_revenue_year1 + tax_benefit_feed_in_year1
    results['annual_financial_benefit_year1'] = annual_financial_benefit_year1
    results['amortization_time_years'] = total_investment_netto / annual_financial_benefit_year1 if annual_financial_benefit_year1 > 0 else float('inf')

    # --- Simulation über die Jahre ---
    cash_flows_initial_investment = [-total_investment_netto] # Jahr 0 ist die Investition
    annual_productions_sim_list, annual_benefits_sim_list, annual_maintenance_costs_sim_list = [],[],[]
    annual_cash_flows_yearly_list, annual_elec_prices_sim_list, annual_feed_in_tariffs_sim_list = [],[],[]
    annual_revenue_from_feed_in_sim_list = [] # Für detailliertere Analyse

    # Wartungskosten
    maintenance_fixed_pa = float(global_constants.get('maintenance_fixed_eur_pa', 0.0) or 0.0)
    maintenance_variable_pa_kwp = float(global_constants.get('maintenance_variable_eur_per_kwp_pa', 0.0) or 0.0)
    maintenance_increase_pa_rate = float(global_constants.get('maintenance_increase_percent_pa', inflation_rate_percent) or inflation_rate_percent) / 100.0 # Kopplung an Inflation als Default
    maintenance_base_percent_of_invest = float(global_constants.get('maintenance_costs_base_percent', 1.5) or 1.5) / 100.0

    annual_maintenance_costs_eur_year1_calc = 0.0
    if maintenance_fixed_pa > 0 or maintenance_variable_pa_kwp > 0: # Wenn spezifische Werte da sind
        annual_maintenance_costs_eur_year1_calc = maintenance_fixed_pa + (maintenance_variable_pa_kwp * results['anlage_kwp'])
    else: # Fallback auf Prozentsatz der Investition
        annual_maintenance_costs_eur_year1_calc = total_investment_netto * maintenance_base_percent_of_invest
        # if app_debug_mode_is_enabled: # Bereinigt
            # if (maintenance_increase_pa_rate * 100) == inflation_rate_percent: errors_list.append(texts.get("info_maintenance_increase_uses_inflation", "Info: Steigerung Wartungskosten an Inflationsrate gekoppelt."))
            # if maintenance_base_percent_of_invest * 100 > 0 : errors_list.append(texts.get("info_maintenance_fallback_used", "Info: Detaillierte Wartungskosten nicht gesetzt, Fallback auf % der Investition."))
    results['annual_maintenance_costs_eur_year1'] = annual_maintenance_costs_eur_year1_calc

    for year_idx in range(1, results['simulation_period_years_effective'] + 1):
        current_year_production = annual_pv_production_kwh * (annual_degredation_factor**(year_idx - 1))
        annual_productions_sim_list.append(current_year_production)

        # Annahme: Anteile von EV und Einspeisung bleiben über die Jahre relativ konstant zur Produktion
        ev_anteil_an_prod_j1 = eigenverbrauch_pro_jahr_kwh / annual_pv_production_kwh if annual_pv_production_kwh > 0 else 0
        einspeisung_anteil_an_prod_j1 = netzeinspeisung_kwh / annual_pv_production_kwh if annual_pv_production_kwh > 0 else 0

        current_year_ev = current_year_production * ev_anteil_an_prod_j1
        current_year_einspeisung = current_year_production * einspeisung_anteil_an_prod_j1

        elec_price_sim = electricity_price_kwh * ((1 + results['electricity_price_increase_rate_effective_percent'] / 100.0)**(year_idx - 1))
        annual_elec_prices_sim_list.append(elec_price_sim)

        feed_in_tariff_sim = results['einspeiseverguetung_eur_per_kwh'] # Annahme: fester Tarif für EEG-Zeitraum
        if year_idx > int(global_constants.get('einspeiseverguetung_period_years', 20) or 20): # Nach EEG-Vergütungszeitraum
            feed_in_tariff_sim = float(global_constants.get('marktwert_strom_eur_per_kwh_after_eeg', 0.03) or 0.03) # Marktwert
        annual_feed_in_tariffs_sim_list.append(feed_in_tariff_sim)

        cost_savings_sim = current_year_ev * elec_price_sim
        feed_in_rev_sim = current_year_einspeisung * feed_in_tariff_sim
        annual_revenue_from_feed_in_sim_list.append(feed_in_rev_sim) # Speichern für Details

        tax_benefit_sim = feed_in_rev_sim * (income_tax_rate_percent / 100.0) if customer_data.get('type', 'Privat').lower() == 'gewerblich' else 0.0
        maint_costs_sim = annual_maintenance_costs_eur_year1_calc * ((1 + maintenance_increase_pa_rate)**(year_idx - 1))
        annual_maintenance_costs_sim_list.append(maint_costs_sim)

        annual_benefit_this_year = cost_savings_sim + feed_in_rev_sim + tax_benefit_sim
        annual_benefits_sim_list.append(annual_benefit_this_year)

        cash_flow_this_year = annual_benefit_this_year - maint_costs_sim
        cash_flows_initial_investment.append(cash_flow_this_year) # Für IRR und NPV
        annual_cash_flows_yearly_list.append(cash_flow_this_year) # Nur die jährlichen CFs

    results.update({
        'annual_productions_sim': annual_productions_sim_list,
        'annual_benefits_sim': annual_benefits_sim_list,
        'annual_maintenance_costs_sim': annual_maintenance_costs_sim_list,
        'annual_cash_flows_sim': annual_cash_flows_yearly_list, # Jährliche CFs (ohne Jahr 0)
        'cumulative_cash_flows_sim': np.cumsum(cash_flows_initial_investment).tolist(), # Kumulierte CFs (inkl. Jahr 0)
        'annual_elec_prices_sim': annual_elec_prices_sim_list, # Strompreise pro Jahr
        'annual_feed_in_tariffs_sim': annual_feed_in_tariffs_sim_list, # Einspeisevergütung pro Jahr
        'annual_revenue_from_feed_in_sim': annual_revenue_from_feed_in_sim_list # Jährliche Einnahmen aus Einspeisung
    })

    # --- Weitere Kennzahlen ---
    # Nettobarwert (NPV)
    npv_value = -cash_flows_initial_investment[0] # Investition in Jahr 0
    discount_rate_npv = loan_interest_rate_percent / 100.0 # Kalkulatorischer Zinssatz
    for i_npv, cf_val in enumerate(cash_flows_initial_investment[1:], 1): # Ab Jahr 1
        npv_value += cf_val / ((1 + discount_rate_npv)**i_npv)
    results['npv_value'] = npv_value
    results['npv_per_kwp'] = npv_value / results['anlage_kwp'] if results['anlage_kwp'] > 0 else float('nan')

    # Interner Zinsfuß (IRR)
    try:
        import numpy_financial as npf
        irr_val = npf.irr(cash_flows_initial_investment) # Benötigt Cashflows inkl. initialer Investition
        results['irr_percent'] = irr_val * 100 if irr_val is not None and not (math.isnan(irr_val) or math.isinf(irr_val)) else float('nan')
    except ImportError:
        results['irr_percent'] = float('nan')
        errors_list.append(texts.get("warn_numpy_financial_missing_for_irr", "Hinweis: numpy_financial nicht installiert, IRR kann nicht berechnet werden."))
    except Exception as e_irr_calc: # Fängt auch ValueError von npf.irr ab, wenn keine Lösung gefunden
        results['irr_percent'] = float('nan')
        errors_list.append((texts.get("error_irr_calculation", "Fehler bei IRR-Berechnung: {error_details}") or "").format(error_details=str(e_irr_calc)))

    # Stromgestehungskosten (LCOE)
    total_discounted_costs_lcoe = total_investment_netto # Kosten in Jahr 0
    total_discounted_production_lcoe = 0.0
    discount_rate_lcoe = loan_interest_rate_percent / 100.0 # Gleicher Diskontsatz wie NPV
    if annual_productions_sim_list and annual_maintenance_costs_sim_list:
        for y_idx in range(min(len(annual_productions_sim_list), len(annual_maintenance_costs_sim_list), results['simulation_period_years_effective'])):
            total_discounted_production_lcoe += annual_productions_sim_list[y_idx]/((1+discount_rate_lcoe)**(y_idx+1))
            total_discounted_costs_lcoe += annual_maintenance_costs_sim_list[y_idx]/((1+discount_rate_lcoe)**(y_idx+1)) # Diskontierte Wartungskosten addieren
    results['lcoe_euro_per_kwh'] = total_discounted_costs_lcoe/total_discounted_production_lcoe if total_discounted_production_lcoe > 0 else float('inf')
    results['effektiver_pv_strompreis_ct_kwh'] = results['lcoe_euro_per_kwh']*100 if results['lcoe_euro_per_kwh'] != float('inf') else float('inf')

    # Einfache Rentabilität (ROI) für Jahr 1
    results['simple_roi_percent'] = (annual_financial_benefit_year1 / total_investment_netto * 100) if total_investment_netto > 0 else float('inf')

    # Performance Ratio (PR) - Annahme: Referenzwert aus global_constants
    ref_specific_yield_for_pr = float(global_constants.get('reference_specific_yield_pr',1100.0) or 1100.0)
    current_specific_yield = results.get('specific_annual_yield_kwh_per_kwp',0.0) or 0.0
    if current_specific_yield > 0 and ref_specific_yield_for_pr > 0:
        pr_calculated = (current_specific_yield/ref_specific_yield_for_pr)*100
        results['performance_ratio_percent'] = min(max(pr_calculated,50.0),95.0) # Begrenzung auf plausiblen Bereich
    else:
        results['performance_ratio_percent'] = float(global_constants.get('default_performance_ratio_percent',78.0) or 78.0) # Fallback auf Default PR

    # AfA und Restwert
    afa_period_years = int(global_constants.get('afa_period_years',20) or 20)
    results['afa_linear_pa_eur'] = total_investment_netto / afa_period_years if afa_period_years > 0 else 0.0
    results['restwert_anlage_eur_nach_laufzeit'] = max(0.0, total_investment_netto - (results['afa_linear_pa_eur'] * results['simulation_period_years_effective']))

    # Eigenkapitalrendite (ROE) - hier vereinfacht als IRR, da keine Fremdfinanzierung modelliert
    results['eigenkapitalrendite_roe_pct'] = results['irr_percent']

    # Alternativanlage
    alternative_investment_interest_rate_percent = float(global_constants.get('alternative_investment_interest_rate_percent',5.0) or 5.0)
    results['alternativanlage_kapitalwert_eur'] = total_investment_netto * ((1 + alternative_investment_interest_rate_percent / 100.0)**results['simulation_period_years_effective'])

    # CO2-Einsparungen
    co2_emission_factor_kg_per_kwh = float(global_constants.get('co2_emission_factor_kg_per_kwh',0.474) or 0.474)
    annual_co2_savings_kg = annual_pv_production_kwh * co2_emission_factor_kg_per_kwh # Für Jahr 1
    results['annual_co2_savings_kg'] = annual_co2_savings_kg
    co2_per_tree = float(global_constants.get('co2_per_tree_kg_pa',12.5) or 12.5); results['co2_equivalent_trees_per_year'] = annual_co2_savings_kg / co2_per_tree if co2_per_tree > 0 else 0.0
    co2_per_car = float(global_constants.get('co2_per_car_km_kg',0.12) or 0.12); results['co2_equivalent_car_km_per_year'] = annual_co2_savings_kg / co2_per_car if co2_per_car > 0 else 0.0
    co2_per_flight = float(global_constants.get('co2_per_flight_muc_pmi_kg',180.0) or 180.0); results['co2_equivalent_flights_muc_pmi_per_year'] = annual_co2_savings_kg / co2_per_flight if co2_per_flight > 0 else 0.0
    total_co2_savings_over_lifetime_kg = (sum(annual_productions_sim_list) if annual_productions_sim_list else 0) * co2_emission_factor_kg_per_kwh
    results['co2_avoidance_cost_euro_per_tonne'] = (total_investment_netto / (total_co2_savings_over_lifetime_kg / 1000.0)) if total_co2_savings_over_lifetime_kg > 0 else float('inf')


    # E-Auto und Wärmepumpe (vereinfachte Betrachtung)
    if project_details.get('future_ev',False): # Wenn E-Auto geplant ist
        eauto_annual_km_calc = float(global_constants.get('eauto_annual_km',10000) or 10000)
        eauto_consumption_kwh_per_100km_calc = float(global_constants.get('eauto_consumption_kwh_per_100km',18) or 18)
        future_ev_consump_kwh_calc = (eauto_annual_km_calc/100.0)*eauto_consumption_kwh_per_100km_calc
        eauto_pv_share_percent_calc = float(global_constants.get('eauto_pv_share_percent',30) or 30)
        # Max. was PV für EV liefern kann, ist der geringere Wert aus PV-Anteil am EV-Verbrauch und der gesamten PV-Produktion (die nicht schon für Haushalt weg ist)
        results['eauto_ladung_durch_pv_kwh'] = min(future_ev_consump_kwh_calc * (eauto_pv_share_percent_calc/100.0), annual_pv_production_kwh) # Vereinfacht: nimmt von Gesamtproduktion
    else: results['eauto_ladung_durch_pv_kwh'] = 0.0

    if project_details.get('future_hp',False): # Wenn Wärmepumpe geplant ist
        waermebedarf_heizung_kwh_calc = float(project_details.get('consumption_heating_kwh_yr',0) or 0) # Wärmebedarf = Verbrauch Heizung
        hp_cop_calc = float(global_constants.get('heatpump_cop_factor',3.5) or 3.5)
        future_hp_consump_kwh_calc = waermebedarf_heizung_kwh_calc / hp_cop_calc if hp_cop_calc > 0 else 0 # Stromverbrauch der WP
        hp_pv_share_percent_calc = float(global_constants.get('heatpump_pv_share_percent',40) or 40)
        potential_hp_coverage_by_pv_kwh_calc = future_hp_consump_kwh_calc * (hp_pv_share_percent_calc/100.0)
        # PV-Deckungsgrad für WP: Wie viel vom WP-Strombedarf kann die PV decken?
        results['pv_deckungsgrad_wp_pct'] = (min(potential_hp_coverage_by_pv_kwh_calc, annual_pv_production_kwh)/future_hp_consump_kwh_calc*100) if future_hp_consump_kwh_calc > 0 else 0.0
    else: results['pv_deckungsgrad_wp_pct'] = 0.0

    # Kostenhochrechnung ohne PV
    annual_costs_hochrechnung_values_calc = []
    total_projected_costs_with_increase_calc = 0.0
    total_projected_costs_without_increase_calc = 0.0
    base_consumption_for_projection_calc = (project_details.get('annual_consumption_kwh_yr',0.0) or 0.0) + (project_details.get('consumption_heating_kwh_yr',0.0) or 0.0)
    base_price_for_projection_calc = float(project_details.get('electricity_price_kwh',0.30) or 0.30)
    # if base_consumption_for_projection_calc==0 and results['anlage_kwp']>0 and app_debug_mode_is_enabled: errors_list.append(texts.get("warn_zero_consumption_for_projection","Warnung: Gesamtjahresverbrauch für Kostenhochrechnung ist 0 kWh.")) # Bereinigt
    # if base_price_for_projection_calc==0 and results['anlage_kwp']>0 and base_consumption_for_projection_calc > 0 and app_debug_mode_is_enabled: errors_list.append(texts.get("warn_zero_price_for_projection","Warnung: Strompreis für Kostenhochrechnung ist 0 €/kWh.")) # Bereinigt
    for year_proj_calc in range(results['simulation_period_years_effective']):
        cost_this_year_proj_calc = base_consumption_for_projection_calc * base_price_for_projection_calc * ((1 + results['electricity_price_increase_rate_effective_percent'] / 100.0)**year_proj_calc)
        annual_costs_hochrechnung_values_calc.append(cost_this_year_proj_calc)
        total_projected_costs_with_increase_calc += cost_this_year_proj_calc
        total_projected_costs_without_increase_calc += base_consumption_for_projection_calc * base_price_for_projection_calc
    results['annual_costs_hochrechnung_values'] = annual_costs_hochrechnung_values_calc
    results['annual_costs_hochrechnung_jahre_effektiv'] = results['simulation_period_years_effective']
    results['annual_costs_hochrechnung_steigerung_effektiv_prozent'] = results['electricity_price_increase_rate_effective_percent']
    results['total_projected_costs_with_increase'] = total_projected_costs_with_increase_calc
    results['total_projected_costs_without_increase'] = total_projected_costs_without_increase_calc

    # Break-Even Analyse
    try:
        break_even_analyzer = BreakEvenAnalysis(
            investment=total_investment_brutto,
            annual_savings=annual_financial_benefit_year1,
            inflation_rate=inflation_rate_percent,
            electricity_price_increase=results['electricity_price_increase_rate_effective_percent']
        )
        results['break_even_scenarios'] = break_even_analyzer.calculate_scenarios()
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Break-Even Analyse: {str(e)}")
    
    # Energiepreisvergleich
    try:
        energy_price_comparator = EnergyPriceComparison(
            current_consumption=annual_consumption_kwh_yr,
            current_price=electricity_price_kwh,
            pv_production=annual_pv_production_kwh,
            self_consumption=eigenverbrauch_pro_jahr_kwh,
            feed_in_rate=feed_in_tariff_effective
        )
        sample_tariffs = [
            {"name": "Aktueller Tarif", "price_per_kwh": electricity_price_kwh},
            {"name": "Ökostromtarif", "price_per_kwh": electricity_price_kwh * 1.1},
            {"name": "Grundversorgung", "price_per_kwh": electricity_price_kwh * 0.95}
        ]
        results['energy_price_comparison'] = energy_price_comparator.compare_tariffs(sample_tariffs)
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Energiepreisvergleich: {str(e)}")
    
    # Technische Degradation
    try:
        degradation_analyzer = TechnicalDegradation(
            initial_power=anlage_kwp * 1000,  # Umrechnung in Watt
            annual_degradation=annual_module_degradation_percent,
            warranty_years=25,  # Standard 25 Jahre
            warranty_power=80  # Standard 80% nach Garantiezeit
        )
        results['degradation_analysis'] = degradation_analyzer.calculate_degradation(
            years=results['simulation_period_years_effective']
        )
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Degradationsanalyse: {str(e)}")
    
    # Wartungsplan
    try:
        components = [
            {
                "name": "Wechselrichter",
                "maintenance_interval_months": 12,
                "maintenance_cost": maintenance_cost_fixed_pa / 2,  # Hälfte der jährlichen Wartungskosten
                "last_maintenance_date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "name": "PV-Module",
                "maintenance_interval_months": 6,
                "maintenance_cost": maintenance_cost_fixed_pa / 2,  # Andere Hälfte der jährlichen Wartungskosten
                "last_maintenance_date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        # Speicherkomponente nur hinzufügen, wenn ein Speicher vorhanden ist
        if include_storage and selected_storage_capacity_kwh > 0:
            components.append({
                "name": "Speichersystem",
                "maintenance_interval_months": 12,
                "maintenance_cost": maintenance_cost_fixed_pa * 0.2,  # 20% der jährlichen Wartungskosten
                "last_maintenance_date": datetime.now().strftime("%Y-%m-%d")
            })
            
        maintenance_monitor = MaintenanceMonitoring(
            components=components,
            installation_date=datetime.now().strftime("%Y-%m-%d")
        )
        results['maintenance_schedule'] = maintenance_monitor.generate_maintenance_schedule()
    except Exception as e:
        if errors_list is not None:
            errors_list.append(f"Fehler bei Wartungsplanerstellung: {str(e)}")

    # Standardwerte für Diagrammdaten-Keys setzen, falls sie nicht explizit berechnet wurden
    # Dies ist wichtig, damit analysis.py nicht auf nicht existierende Keys zugreift.
    chart_data_keys_to_ensure = [
        'monthly_prod_cons_chart_bytes','cumulative_cashflow_chart_bytes',
        'pv_usage_chart_bytes','consumption_coverage_chart_bytes',
        'cost_overview_chart_bytes','cost_projection_chart_bytes',
        'break_even_scenarios_chart_bytes', 'technical_degradation_chart_bytes',
        'maintenance_schedule_chart_bytes', 'energy_price_comparison_chart_bytes'
    ]
    for chart_key_init_final in chart_data_keys_to_ensure:
        results.setdefault(chart_key_init_final, None)


    # Finale Kennzahlen für die Darstellung
    results['self_supply_rate_percent'] = (eigenverbrauch_pro_jahr_kwh / annual_consumption_kwh_yr * 100) if annual_consumption_kwh_yr > 0 else 0.0
    results['grid_consumption_rate_percent'] = 100.0 - results['self_supply_rate_percent'] # Anteil Netzbezug am Gesamtverbrauch
    results['direktverbrauch_anteil_pv_produktion_pct'] = (sum(monthly_direct_self_consumption_kwh) / annual_pv_production_kwh * 100) if annual_pv_production_kwh > 0 else 0.0
    results['speichernutzung_anteil_pv_produktion_pct'] = (sum(monthly_storage_discharge_for_sc_kwh) / annual_pv_production_kwh * 100) if annual_pv_production_kwh > 0 else 0.0 # Anteil Speichernutzung an PV-Produktion

    # Speicherbezogene Kennzahlen
    if include_storage and selected_storage_capacity_kwh > 0:
        # Speichergrad / Deckungsgrad durch Speicher (Anteil des Gesamtverbrauchs, der aus dem Speicher gedeckt wird)
        results['speichergrad_deckungsgrad_speicher_pct'] = (sum(monthly_storage_discharge_for_sc_kwh)/annual_consumption_kwh_yr*100) if annual_consumption_kwh_yr > 0 else 0.0
        # Optimale Speichergröße (Heuristik)
        optimal_storage_factor_calc = float(global_constants.get('optimal_storage_factor',1.0) or 1.0) # z.B. 1 kWh Speicher pro 1000 kWh Jahresverbrauch
        results['optimale_speichergröße_kwh_geschaetzt'] = (annual_consumption_kwh_yr/1000.0)*optimal_storage_factor_calc if annual_consumption_kwh_yr > 0 else 0.0
        # Notstromkapazität (vereinfacht als Speicherkapazität)
        results['notstromkapazitaet_kwh_pro_tag'] = selected_storage_capacity_kwh # Annahme: gesamter Speicher für Notstrom nutzbar
        # Batterielebensdauer
        storage_max_cycles_calc = 0.0
        if storage_details_from_db:
            storage_max_cycles_raw_val = storage_details_from_db.get('max_cycles') # Aus Produktdatenbank
            # Fallback, falls 'max_cycles' nicht in DB ist oder 0
            default_cycles_from_product_db_val = 6000 # Ein typischer Wert
            cycles_per_year_for_default_from_constants_val = float(global_constants.get('storage_cycles_per_year',250) or 250)
            calculated_default_max_cycles_val = default_cycles_from_product_db_val
            if cycles_per_year_for_default_from_constants_val > 0 and results['simulation_period_years_effective'] > 0: # Sicherstellen, dass Divisor > 0
                calculated_default_max_cycles_val = cycles_per_year_for_default_from_constants_val * results['simulation_period_years_effective'] # Alternative: Zyklen über Lebensdauer

            if storage_max_cycles_raw_val is None: # Kein Wert in DB
                storage_max_cycles_calc = calculated_default_max_cycles_val
            else:
                try:
                    storage_max_cycles_val_conv = float(storage_max_cycles_raw_val)
                    storage_max_cycles_calc = storage_max_cycles_val_conv if storage_max_cycles_val_conv > 0 else calculated_default_max_cycles_val
                except (ValueError,TypeError): # Wenn Konvertierung fehlschlägt
                    storage_max_cycles_calc = calculated_default_max_cycles_val

        storage_cycles_per_year_val_calc = float(global_constants.get('storage_cycles_per_year',250) or 250) # Zyklen pro Jahr
        if storage_max_cycles_calc > 0 and storage_cycles_per_year_val_calc > 0 :
            results['batterie_lebensdauer_geschaetzt_jahre'] = storage_max_cycles_calc / storage_cycles_per_year_val_calc
        else:
            results['batterie_lebensdauer_geschaetzt_jahre'] = float('inf') # Wenn keine Zyklenangabe oder keine Nutzung
    else: # Keine Speicherlogik
        results['speichergrad_deckungsgrad_speicher_pct'], results['optimale_speichergröße_kwh_geschaetzt'], results['notstromkapazitaet_kwh_pro_tag'], results['batterie_lebensdauer_geschaetzt_jahre'] = 0.0,0.0,0.0,0.0

    # Verschattungsverlust (aus Eingabe übernehmen)
    results['verschattungsverlust_pct'] = float(project_details.get('verschattungsverlust_pct', 0.0) or 0.0)

    # if app_debug_mode_is_enabled: print(f"--- CALCULATIONS.PY: Berechnungen abgeschlossen. Ergebnisse (Auszug): {json.dumps({k: v for k,v in results.items() if not isinstance(v, list) or len(v) < 5}, indent=2, ensure_ascii=False)}") # Bereinigt
    # if app_debug_mode_is_enabled and errors_list: print(f"CALC: Gesammelte Fehler/Hinweise: {errors_list}") # Bereinigt

    return results

# --- Testlauf für calculations.py (optional, nur für direkte Ausführung) ---
if __name__ == "__main__":
    print("--- Testlauf für calculations.py (minimal) ---")
    test_project_data = {
        'customer_data': {'income_tax_rate_percent': 25, 'type': 'Privat'},
        'project_details': {
            'annual_consumption_kwh_yr': 4500, 'electricity_price_kwh': 0.35,
            'module_quantity': 20, 'selected_module_id': 1, 'selected_inverter_id': 1,
            'include_storage': True, 'selected_storage_id': 1, 'selected_storage_storage_power_kw': 5.0,
            'selected_storage_name': 'TestSpeicher 5kWh', 
            'roof_orientation': 'Süd', 'roof_inclination_deg': 35, 'latitude': 48.13, 'longitude': 11.57, 
            'feed_in_type': 'Teileinspeisung'
        },
        'economic_data': { 
            'simulation_period_years': 20,
            'electricity_price_increase_annual_percent': 2.5
        }
    }
    def mock_get_prod_by_id_calc_main(pid):
        if pid == 1: return {'id':1, 'capacity_w': 400, 'power_kw': 5, 'storage_power_kw': 5, 'additional_cost_netto':0, 'model_name': 'TestSpeicher 5kWh'}
        return None
    _original_real_get_product_by_id_calc_main = real_get_product_by_id
    real_get_product_by_id = mock_get_prod_by_id_calc_main
    test_texts_calc_main = {"pvgis_invalid_lat_lon": "PVGIS ungültige Koordinaten.", "no_storage_option_for_matrix": "Ohne Speicher"}
    test_errors_calc_main: List[str] = []
    results_calc_main = perform_calculations(test_project_data, test_texts_calc_main, test_errors_calc_main)
    print("\nBerechnungsergebnisse (Auszug):")
    for k_res_main, v_res_main in results_calc_main.items():
        if not isinstance(v_res_main, list) or len(v_res_main) < 5 : 
            print(f"  {k_res_main}: {v_res_main}")
    if test_errors_calc_main:
        print("\nFehler/Warnungen während des Testlaufs:")
        for err_main in test_errors_calc_main:
            print(f"  - {err_main}")
    real_get_product_by_id = _original_real_get_product_by_id_calc_main
    print("\n--- Testlauf calculations.py beendet ---")

class BreakEvenAnalysis:
    """Erweiterte Break-Even-Analyse mit verschiedenen Szenarien"""
    def __init__(self, investment: float, annual_savings: float, 
                 inflation_rate: float, electricity_price_increase: float):
        self.investment = investment
        self.annual_savings = annual_savings
        self.inflation_rate = inflation_rate
        self.electricity_price_increase = electricity_price_increase

    def calculate_scenarios(self) -> Dict[str, Dict[str, float]]:
        scenarios = {
            "Konservativ": {
                "electricity_price_increase": max(0, self.electricity_price_increase - 1),
                "savings_factor": 0.9
            },
            "Basis": {
                "electricity_price_increase": self.electricity_price_increase,
                "savings_factor": 1.0
            },
            "Optimistisch": {
                "electricity_price_increase": self.electricity_price_increase + 1,
                "savings_factor": 1.1
            }
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            annual_savings_adj = self.annual_savings * params["savings_factor"]
            cumulative_savings = 0
            years_to_break_even = float('inf')
            
            for year in range(1, 31):  # Max 30 Jahre
                price_factor = (1 + params["electricity_price_increase"] / 100) ** year
                inflation_factor = (1 + self.inflation_rate / 100) ** year
                
                annual_savings_this_year = annual_savings_adj * price_factor / inflation_factor
                cumulative_savings += annual_savings_this_year
                
                if cumulative_savings >= self.investment and years_to_break_even == float('inf'):
                    years_to_break_even = year + (self.investment - (cumulative_savings - annual_savings_this_year)) / annual_savings_this_year
            
            annual_roi = (annual_savings_adj / self.investment) * 100
            
            results[scenario_name] = {
                "years_to_break_even": years_to_break_even,
                "total_savings_at_break_even": cumulative_savings,
                "annual_roi_percent": annual_roi
            }
        
        return results

class EnergyPriceComparison:
    """Energiepreisvergleichstool"""
    def __init__(self, current_consumption: float, current_price: float,
                 pv_production: float, self_consumption: float,
                 feed_in_rate: float):
        self.current_consumption = current_consumption
        self.current_price = current_price
        self.pv_production = pv_production
        self.self_consumption = self_consumption
        self.feed_in_rate = feed_in_rate

    def compare_tariffs(self, tariffs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, float]]]:
        base_cost = self.current_consumption * self.current_price
        pv_savings = self.self_consumption * self.current_price
        feed_in_revenue = (self.pv_production - self.self_consumption) * self.feed_in_rate
        
        comparisons = []
        for tariff in tariffs:
            new_cost = (self.current_consumption - self.self_consumption) * tariff["price_per_kwh"]
            total_cost = new_cost - feed_in_revenue
            savings = base_cost - total_cost
            savings_percent = (savings / base_cost) * 100 if base_cost > 0 else 0
            
            comparisons.append({
                "tariff_name": tariff["name"],
                "total_cost_yearly": total_cost,
                "savings_yearly": savings,
                "savings_percent": savings_percent
            })
        
        return {"comparisons": comparisons}

class TechnicalDegradation:
    """Detaillierte Degradationsanalyse"""
    def __init__(self, initial_power: float, annual_degradation: float,
                 warranty_years: int, warranty_power: float):
        self.initial_power = initial_power
        self.annual_degradation = annual_degradation
        self.warranty_years = warranty_years
        self.warranty_power = warranty_power

    def calculate_degradation(self, years: int = 25) -> Dict[str, Any]:
        efficiency_by_year = []
        degradation_rate_by_year = []
        current_power = self.initial_power
        
        for year in range(years):
            efficiency = (current_power / self.initial_power) * 100
            efficiency_by_year.append(efficiency)
            
            if year < years - 1:
                next_power = current_power * (1 - self.annual_degradation / 100)
                degradation_rate = ((current_power - next_power) / current_power) * 100
                degradation_rate_by_year.append(degradation_rate)
                current_power = next_power
            else:
                degradation_rate_by_year.append(self.annual_degradation)
        
        total_degradation = ((self.initial_power - current_power) / self.initial_power) * 100
        warranty_compliance = current_power >= (self.warranty_power * self.initial_power / 100)
        
        return {
            "efficiency_by_year": efficiency_by_year,
            "degradation_rate_by_year": degradation_rate_by_year,
            "total_degradation_percent": total_degradation,
            "warranty_compliance": warranty_compliance
        }

class MaintenanceMonitoring:
    """Wartungs- und Überwachungsmodul"""
    def __init__(self, components: List[Dict[str, Any]], installation_date: str):
        self.components = components
        self.installation_date = datetime.strptime(installation_date, "%Y-%m-%d")

    def generate_maintenance_schedule(self) -> Dict[str, Any]:
        maintenance_schedule = []
        total_annual_cost = 0
        
        for component in self.components:
            interval_months = component.get("maintenance_interval_months", 12)
            last_maintenance = component.get("last_maintenance_date")
            if last_maintenance:
                last_maintenance = datetime.strptime(last_maintenance, "%Y-%m-%d")
            else:
                last_maintenance = self.installation_date
            
            next_maintenance = last_maintenance
            while next_maintenance < datetime.now():
                next_maintenance = datetime.fromtimestamp(
                    next_maintenance.timestamp() + (interval_months * 30 * 24 * 3600)
                )
            
            estimated_cost = component.get("maintenance_cost", 0)
            total_annual_cost += estimated_cost * (12 / interval_months)
            
            maintenance_schedule.append({
                "component": component["name"],
                "last_maintenance": last_maintenance,
                "next_maintenance": next_maintenance,
                "interval_months": interval_months,
                "priority": "Hoch" if interval_months <= 6 else "Mittel" if interval_months <= 12 else "Niedrig",
                "estimated_cost": estimated_cost
            })
        
        return {
            "maintenance_schedule": sorted(maintenance_schedule, key=lambda x: x["next_maintenance"]),
            "total_annual_cost": total_annual_cost
        }

def calculate_offer_details(customer_id: Optional[int] = None, project_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Berechnet detaillierte Angebotsdaten für einen Kunden.
    
    Args:
        customer_id: Optional - ID des Kunden
        project_data: Optional - Projektdaten für die Berechnung
        
    Returns:
        Dict mit Angebotsdaten
    """
    try:
        # Fallback-Projektdaten wenn nicht übergeben
        if not project_data:
            project_data = {
                'anlage_kwp': 10.0,
                'electricity_price_eur_per_kwh': 0.30,
                'annual_consumption_kwh': 4000,
                'storage_kwh': 10.0,
                'location': {'latitude': 50.0, 'longitude': 10.0}
            }
        
        # Basis-Berechnungen durchführen
        calculation_errors = []
        results = perform_calculations(
            project_data, 
            {}, # texts
            calculation_errors
        )
        
        # Zusätzliche Angebotsdaten erstellen
        offer_details = {
            'customer_id': customer_id,
            'calculation_results': results,
            'project_data': project_data,
            'calculation_errors': calculation_errors,
            'generated_at': datetime.now().isoformat(),
            
            # Wichtige Kennzahlen für Angebot
            'total_investment': results.get('total_investment_brutto', 0),
            'annual_savings': results.get('annual_financial_benefit_year1', 0),
            'payback_time': results.get('amortization_time_years', 0),
            'annual_production': results.get('annual_pv_production_kwh', 0),
            'self_consumption_rate': results.get('self_supply_rate_percent', 0),
            'co2_savings_annual': results.get('co2_emission_avoided_kg_per_year', 0),
            
            # Finanzielle Details
            'financing_options': {
                'cash_payment': results.get('total_investment_brutto', 0),
                'financing_available': True,
                'monthly_rate_estimate': results.get('total_investment_brutto', 0) / 240 if results.get('total_investment_brutto', 0) > 0 else 0
            },
            
            # Komponenten
            'system_components': {
                'modules': f"{results.get('anlage_kwp', 0)} kWp PV-Module",
                'inverter': "Wechselrichter",
                'storage': f"{project_data.get('storage_kwh', 0)} kWh Batteriespeicher" if project_data.get('storage_kwh', 0) > 0 else None,
                'installation': "Montage und Installation"
            }
        }
        
        return offer_details
        
    except Exception as e:
        return {
            'error': f"Fehler bei Angebotserstellung: {str(e)}",
            'customer_id': customer_id,
            'generated_at': datetime.now().isoformat()
        }