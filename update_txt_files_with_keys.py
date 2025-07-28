#!/usr/bin/env python3
"""
TXT-Dateien Key-Replacer
========================

Ersetzt statische Werte in den input/*.txt Dateien durch dynamische Keys,
damit die PDF vollständig dynamisch wird.
"""

import os
import re
import glob

def update_txt_files_with_keys():
    """Ersetzt statische Werte in TXT-Dateien durch KONTEXTSPEZIFISCHE dynamische Keys."""
    
    input_dir = os.path.join(os.getcwd(), "input")
    
    print("🔍 Analysiere TXT-Dateien für kontextspezifische Key-Zuordnung...")
    
    # INTELLIGENTE CONTEXT-AWARE REPLACEMENTS
    # Verschiedene Keys je nach Kontext und Position
    
    def get_smart_replacements():
        """Generiert kontextspezifische Ersetzungen basierend auf Analyse."""
        return {
            # === KUNDENDATEN VARIATIONEN ===
            "Meierhofer Hans Peter": "{customer_name}",
            "Herr Prof.": "{customer_name}",  # Anrede-Kontext
            "Brunnenäcker 46": "{customer_address_street}",
            "79793 Wutöschingen": "{customer_address_city}",
            
            # === FIRMENDATEN KONTEXTABHÄNGIG ===
            "BTPV Deutschland Gmbh": "{company_name}",
            "TommaTech": "{company_name}",
            "info@btpv-deutschland.de": "{company_email}",  
            "mail@tommatech.de": "{company_email}",
            "Mail: info@btpv-deutschland.de": "Mail: {company_email}",
            "Web: www.btpv-deutschland.de": "Web: {company_website}",
            "089244186540": "{company_phone}",
            "Tel.: 089244186540": "Tel.: {company_phone}",
            
            # === FINANZWERTE - SPEZIFISCHE KONTEXTE ===
            "36.958,00 EUR*": "{total_savings_with_storage_eur_formatted}*",  # Mit Währung + Stern
            "36.958": "{total_savings_with_storage_eur}",  # Nur Zahl
            "29.150,00 EUR*": "{total_savings_without_storage_eur_formatted}*",  # Mit Währung + Stern  
            "29.150": "{total_savings_without_storage_eur}",  # Nur Zahl
            
            # === TECHNISCHE DATEN - EINHEIT-SPEZIFISCH ===
            "8,4 kWp": "{anlage_kwp} kWp",  # Mit kWp-Einheit
            "8,4": "{anlage_kwp}",  # Nur Zahl für Berechnungen
            "6,1 kWh": "{battery_capacity_kwh} kWh",  # Batterie mit kWh
            "6,1": "{battery_capacity_kwh}",  # Nur Batterie-Zahl
            " 6,1 kWh": " {battery_capacity_kwh} kWh",  # Mit Leerzeichen
            
            # === VERBRAUCH VERSCHIEDENE KONTEXTE ===
            "6.000 kWh/Jahr": "{annual_consumption_kwh} kWh/Jahr",  # Volltext mit Einheit
            "6.000 kWh": "{annual_consumption_kwh} kWh",  # Ohne /Jahr
            "6.000": "{annual_consumption_kwh}",  # Nur Zahl
            
            # === PRODUKTION VERSCHIEDENE KONTEXTE ===
            "8.251,92 kWh/Jahr": "{annual_pv_production_kwh} kWh/Jahr",  # Volltext
            "8.251,92": "{annual_pv_production_kwh}",  # Nur Zahl
            
            # === MODULE UND HARDWARE - VORSICHTIG! ===
            "21 PV-Module": "{module_quantity} PV-Module",  # Volltext
            "21 Module": "{module_quantity} Module",  # Kurz
            "30° Dachneigung": "{roof_angle}° Dachneigung",  # Mit Kontext
            "30°": "{roof_angle}°",  # Dachneigung mit Grad-Symbol
            
            # === PROZENT-WERTE KONTEXTSPEZIFISCH ===
            "54% Unabhängigkeit": "{independence_degree_percent} Unabhängigkeit",
            "54%": "{independence_degree_percent}",  # Unabhängigkeitsgrad
            "42% Eigenverbrauch": "{self_consumption_percent} Eigenverbrauch", 
            "42%": "{self_consumption_percent}",  # Eigenverbrauch
            
            # === UMWELT-DATEN ===
            "15.266 km": "{co2_savings_km_equivalent} km",  # KM-Äquivalent
            "15.266": "{co2_savings_km_equivalent}",  # Nur KM-Zahl
            
            # === DATUM VARIATIONEN ===
            "26.07.2025": "{current_date}",  # Deutsche Datumsformat
            "29.11.2024": "{current_date}",  # Andere Datum
            "Datum: 26.07.2025": "Datum: {current_date}",  # Mit Präfix
            
            # === PROJEKT-IDs ===
            "AN2025-1454": "{project_id}",  # Angebots-Nummer
            "tom-90": "{project_id}",  # Projekt-Code
            "Angebot 202507261219": "Angebot {project_id}",  # Mit Präfix
            
            # === SPEZIFISCHE ANREDE-KONTEXTE ===
            "Ihr individuelles Solaranlagen-Angebot": "Angebot für {customer_name}",
            "Sehr geehrte Damen und Herren": "Sehr geehrter {customer_name}",
            
            # === FIRMENADRESSE KONTEXTABHÄNGIG ===
            "Augsburger Str. 3a": "{company_address_street}",
            "82178 Puchheim": "{company_address_city}", 
            "Maximilianstraße 35": "{company_address_street}",
            "80539 München": "{company_address_city}",
            
            # === ZUSÄTZLICHE NEUE KEYS ===
            "StNr/USt-ID: DE354973606 117/122/82217": "StNr/USt-ID: {company_tax_id}",
            "DE354973606": "{company_tax_id}",
        }
    
    replacements = get_smart_replacements()
    
    print("🔄 Aktualisiere TXT-Dateien mit dynamischen Keys...")
    
    # Durchlaufe alle TXT-Dateien
    txt_files = glob.glob(os.path.join(input_dir, "seite_*_texte.txt"))
    
    updated_files = 0
    total_replacements = 0
    
    for txt_file in sorted(txt_files):
        print(f"📄 Bearbeite: {os.path.basename(txt_file)}")
        
        # Datei lesen
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_replacements = 0
        
        # Ersetzungen durchführen
        for old_value, new_key in replacements.items():
            if old_value in content:
                content = content.replace(old_value, new_key)
                file_replacements += content.count(new_key) - original_content.count(new_key)
                print(f"  ✅ '{old_value}' -> '{new_key}'")
        
        # Datei zurückschreiben wenn geändert
        if content != original_content:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            updated_files += 1
            total_replacements += file_replacements
            print(f"  💾 {file_replacements} Ersetzungen gespeichert")
        else:
            print("  ℹ️ Keine Änderungen nötig")
    
    print(f"\n🎉 Fertig! {updated_files} Dateien aktualisiert, {total_replacements} Ersetzungen insgesamt")
    
    # Backup-Info
    print("\n📝 WICHTIG: Originale sind in den Dateien überschrieben!")
    print("   Falls nötig, können Sie aus dem Git-Verlauf wiederherstellen.")
    
    return updated_files, total_replacements

if __name__ == "__main__":
    update_txt_files_with_keys()
