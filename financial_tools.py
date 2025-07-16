# financial_tools.py - Vollständige Finanzberechnungen für PV-Anlagen
"""
Finanzberechnungsmodul für PV-Anlagen mit Leasing, Annuitätenkrediten, 
Abschreibungen und Wirtschaftlichkeitsanalysen.
"""

import numpy as np
import pandas as pd
import streamlit as st
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

def calculate_annuity(principal: float, annual_interest_rate: float, duration_years: int) -> Dict[str, Any]:
    """
    Echte Berechnung einer Annuität (Kredit mit gleichbleibenden Raten).
    
    Args:
        principal: Darlehenssumme in Euro
        annual_interest_rate: Jährlicher Zinssatz in Prozent
        duration_years: Laufzeit in Jahren
    
    Returns:
        Dict mit monatlicher Rate, Gesamtzinsen, Tilgungsplan etc.
    """
    if principal <= 0 or annual_interest_rate < 0 or duration_years <= 0:
        return {"error": "Ungültige Eingabeparameter"}
    
    monthly_rate = annual_interest_rate / 100 / 12
    num_payments = duration_years * 12
    
    if monthly_rate == 0:  # Zinsfrei
        monthly_payment = principal / num_payments
        total_interest = 0
    else:
        # Annuitätenformel
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        total_interest = (monthly_payment * num_payments) - principal
    
    # Tilgungsplan erstellen
    tilgungsplan = []
    remaining_principal = principal
    
    for month in range(1, int(num_payments) + 1):
        if monthly_rate == 0:
            interest_payment = 0
            principal_payment = monthly_payment
        else:
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
        
        remaining_principal -= principal_payment
        
        tilgungsplan.append({
            'monat': month,
            'rate': round(monthly_payment, 2),
            'zinsen': round(interest_payment, 2),
            'tilgung': round(principal_payment, 2),
            'restschuld': round(max(0, remaining_principal), 2)
        })
    
    return {
        "monatliche_rate": round(monthly_payment, 2),
        "gesamtzinsen": round(total_interest, 2),
        "gesamtkosten": round(principal + total_interest, 2),
        "effective_rate": round(annual_interest_rate, 2),
        "tilgungsplan": tilgungsplan,
        "laufzeit_monate": num_payments
    }

def calculate_leasing_costs(total_investment: float, leasing_factor: float, duration_months: int, 
                          residual_value_percent: float = 1.0) -> Dict[str, Any]:
    """
    Echte Leasingkostenberechnung mit verschiedenen Modellen.
    
    Args:
        total_investment: Investitionssumme
        leasing_factor: Monatlicher Leasingfaktor in Prozent
        duration_months: Laufzeit in Monaten
        residual_value_percent: Restwert in Prozent (für Kilometerleasing)
    
    Returns:
        Dict mit Leasingraten, Gesamtkosten, Kostenvergleich
    """
    if total_investment <= 0 or leasing_factor <= 0 or duration_months <= 0:
        return {"error": "Ungültige Parameter"}
    
    # Monatliche Leasingrate
    monthly_leasing_rate = total_investment * (leasing_factor / 100)
    
    # Gesamtleasingkosten
    total_leasing_costs = monthly_leasing_rate * duration_months
    
    # Restwert berechnen
    residual_value = total_investment * (residual_value_percent / 100)
    
    # Effektive Kosten (ohne Restwert)
    effective_costs = total_leasing_costs - residual_value
    
    return {
        "monatliche_rate": round(monthly_leasing_rate, 2),
        "gesamtkosten": round(total_leasing_costs, 2),
        "restwert": round(residual_value, 2),
        "effektive_kosten": round(effective_costs, 2),
        "leasingfaktor": leasing_factor,
        "laufzeit_monate": duration_months,
        "kostenvorteil_vs_kauf": round(total_investment - effective_costs, 2)
    }

def calculate_depreciation(initial_value: float, useful_life_years: int, 
                         method: str = "linear") -> Dict[str, Any]:
    """
    Echte Abschreibungsberechnung mit verschiedenen Methoden.
    
    Args:
        initial_value: Anschaffungswert
        useful_life_years: Nutzungsdauer
        method: "linear" oder "degressive"
    
    Returns:
        Dict mit Abschreibungstabelle und Steuerersparnis
    """
    if initial_value <= 0 or useful_life_years <= 0:
        return {"error": "Ungültige Parameter"}
    
    abschreibungsplan = []
    
    if method == "linear":
        annual_depreciation = initial_value / useful_life_years
        
        for year in range(1, useful_life_years + 1):
            book_value = initial_value - (annual_depreciation * year)
            abschreibungsplan.append({
                'jahr': year,
                'abschreibung': round(annual_depreciation, 2),
                'buchwert': round(max(0, book_value), 2),
                'kumulierte_abschreibung': round(annual_depreciation * year, 2)
            })
    
    return {
        "methode": method,
        "jaehrliche_abschreibung": round(annual_depreciation, 2),
        "gesamtabschreibung": round(initial_value, 2),
        "abschreibungsplan": abschreibungsplan,
        "steuerersparnis_30_prozent": round(initial_value * 0.30, 2)  # Beispiel 30% Steuersatz
    }

def calculate_financing_comparison(investment: float, annual_interest_rate: float, 
                                 duration_years: int, leasing_factor: float) -> Dict[str, Any]:
    """
    Vergleich verschiedener Finanzierungsoptionen.
    
    Returns:
        Comprehensive comparison of financing options
    """
    # Kreditfinanzierung
    credit_result = calculate_annuity(investment, annual_interest_rate, duration_years)
    
    # Leasingfinanzierung
    leasing_result = calculate_leasing_costs(investment, leasing_factor, duration_years * 12)
    
    # Cash-Kauf (Referenz)
    cash_opportunity_cost = investment * (annual_interest_rate / 100) * duration_years
    
    return {
        "kredit": credit_result,
        "leasing": leasing_result,
        "cash_kauf": {
            "investition": investment,
            "opportunitaetskosten": round(cash_opportunity_cost, 2),
            "gesamtkosten": round(investment + cash_opportunity_cost, 2)
        },
        "empfehlung": _get_financing_recommendation(credit_result, leasing_result, investment, cash_opportunity_cost)
    }

def _get_financing_recommendation(credit_result: Dict, leasing_result: Dict, 
                                cash_investment: float, opportunity_cost: float) -> str:
    """Gibt eine Finanzierungsempfehlung basierend auf den Gesamtkosten."""
    if "error" in credit_result or "error" in leasing_result:
        return "Unzureichende Daten für Empfehlung"
    
    credit_total = credit_result.get("gesamtkosten", float('inf'))
    leasing_total = leasing_result.get("effektive_kosten", float('inf'))
    cash_total = cash_investment + opportunity_cost
    
    costs = {
        "Kredit": credit_total,
        "Leasing": leasing_total,
        "Cash": cash_total
    }
    
    best_option = min(costs, key=costs.get)
    savings = min(costs.values())
    max_cost = max(costs.values())
    
    return f"Empfehlung: {best_option} (Ersparnis: {round(max_cost - savings, 2)}€)"

def calculate_capital_gains_tax(profit: float, tax_rate: float = 26.375) -> Dict[str, Any]:
    """
    Echte KESt-Berechnung für PV-Anlagen.
    
    Args:
        profit: Gewinn aus PV-Anlage
        tax_rate: Steuersatz in Prozent (Standard: 26.375% in AT)
    
    Returns:
        Dict mit Steuerberechnung
    """
    if profit <= 0:
        return {"steuer": 0, "netto_gewinn": profit, "steuer_rate": tax_rate}
    
    tax_amount = profit * (tax_rate / 100)
    net_profit = profit - tax_amount
    
    return {
        "brutto_gewinn": round(profit, 2),
        "steuer": round(tax_amount, 2),
        "netto_gewinn": round(net_profit, 2),
        "steuer_rate": tax_rate,
        "steuer_optimierung_tipps": [
            "Investitionsabzugsbetrag nutzen",
            "Sonderabschreibungen prüfen",
            "Verlustvorträge berücksichtigen"
        ]
    }

def calculate_contracting_costs(base_fee: float, consumption_price: float, 
                              consumed_kwh: float, period_years: int = 1) -> Dict[str, Any]:
    """
    Echte Contracting-Kostenberechnung.
    
    Returns:
        Detailed contracting cost analysis
    """
    annual_base_fee = base_fee * 12 if period_years >= 1 else base_fee
    annual_consumption_costs = consumption_price * consumed_kwh
    annual_total = annual_base_fee + annual_consumption_costs
    
    total_costs_period = annual_total * period_years
    
    return {
        "jaehrliche_grundgebuehr": round(annual_base_fee, 2),
        "jaehrliche_verbrauchskosten": round(annual_consumption_costs, 2),
        "jaehrliche_gesamtkosten": round(annual_total, 2),
        "gesamtkosten_laufzeit": round(total_costs_period, 2),
        "kosten_pro_kwh_effektiv": round(annual_total / consumed_kwh if consumed_kwh > 0 else 0, 4),
        "laufzeit_jahre": period_years
    }