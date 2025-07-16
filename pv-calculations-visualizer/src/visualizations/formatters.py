from typing import Any, Dict, List

def format_extended_calculations(data: Dict[str, Any]) -> str:
    formatted = (
        f"Kapitalwert (NPV): {data.get('net_present_value', 'N/A')} €\n"
        f"Interner Zinsfuß (IRR): {data.get('internal_rate_of_return', 'N/A')} %\n"
        f"Stromgestehungskosten (LCOE): {data.get('lcoe', 'N/A')} €/kWh\n"
        f"Dynamische Amortisation (3%): {data.get('dynamic_payback_3_percent', 'N/A')} Jahre\n"
        f"Gesamtrendite (ROI): {data.get('total_roi_percent', 'N/A')} %\n"
        f"CO₂-Einsparung pro Jahr: {data.get('co2_avoidance_per_year_tons', 'N/A')} t"
    )
    return formatted

def format_advanced_calculations(data: Dict[str, Any]) -> str:
    formatted = (
        f"Degradation Analyse: {data.get('degradation_analysis', 'N/A')}\n"
        f"Verschattungsanalyse: {data.get('shading_analysis', 'N/A')}\n"
        f"Netzinteraktion: {data.get('grid_interaction', 'N/A')}\n"
        f"Kohlenstoff-Fußabdruck: {data.get('carbon_footprint', 'N/A')}\n"
        f"Peak Shaving: {data.get('peak_shaving', 'N/A')}\n"
        f"Batteriezyklen: {data.get('battery_cycles', 'N/A')}\n"
        f"Wetterauswirkungen: {data.get('weather_impact', 'N/A')}\n"
        f"Energieunabhängigkeit: {data.get('energy_independence', 'N/A')}"
    )
    return formatted

def format_multiple_calculations(calculation_results: List[Dict[str, Any]]) -> List[str]:
    formatted_results = []
    for result in calculation_results:
        formatted_results.append(format_extended_calculations(result))
    return formatted_results

def format_single_calculation(calculation_result: Dict[str, Any]) -> str:
    return format_extended_calculations(calculation_result)