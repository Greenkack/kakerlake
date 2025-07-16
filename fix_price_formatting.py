#!/usr/bin/env python3
"""
Automatische Korrektur der Preisformatierung in analysis.py
Ersetzt amerikanische Formatierung durch deutsche format_kpi_value Aufrufe
"""

import re
import sys

def fix_price_formatting_in_analysis():
    """Korrigiert die Preisformatierung in analysis.py"""
    
    file_path = "c:\\12345\\analysis.py"
    
    # Datei einlesen
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        return False
    
    original_content = content
    replacements_made = 0
    
    # Muster für amerikanische Euro-Formatierung erkennen
    patterns = [
        # f"{value:,.0f} €" -> format_kpi_value(value, "€", precision=0)
        (r'f"\{([^}]+):,\.0f\} €"', r'format_kpi_value(\1, "€", texts_dict={}, precision=0)'),
        
        # f"{value:,.2f} €" -> format_kpi_value(value, "€", precision=2)
        (r'f"\{([^}]+):,\.2f\} €"', r'format_kpi_value(\1, "€", texts_dict={}, precision=2)'),
        
        # f"{value:,.1f} €" -> format_kpi_value(value, "€", precision=1)
        (r'f"\{([^}]+):,\.1f\} €"', r'format_kpi_value(\1, "€", texts_dict={}, precision=1)'),
        
        # Allgemeineres Muster: f"{value:,.<precision>f} €"
        (r'f"\{([^}]+):,\.(\d+)f\} €"', r'format_kpi_value(\1, "€", texts_dict={}, precision=\2)'),
    ]
    
    print("Starte Korrektur der Preisformatierung...")
    print("=" * 60)
    
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"Gefunden: {len(matches)} Vorkommen von '{pattern}'")
            content = re.sub(pattern, replacement, content)
            replacements_made += len(matches)
    
    # Spezifische Korrekturen für komplexere Fälle
    specific_replacements = [
        # Konfidenzintervall-Formatierung
        (r'f"\{mc_results\[\'npv_lower_bound\'\]:,\.0f\} - \{mc_results\[\'npv_upper_bound\'\]:,\.0f\} €"',
         'f"{format_kpi_value(mc_results[\'npv_lower_bound\'], \'\', texts_dict={}, precision=0)} - {format_kpi_value(mc_results[\'npv_upper_bound\'], \'€\', texts_dict={}, precision=0)}"'),
        
        # Delta-Formatierung in st.metric
        (r'delta=f"σ = \{mc_results\[\'npv_std\'\]:,\.0f\} €"',
         'delta=f"σ = {format_kpi_value(mc_results[\'npv_std\'], \'€\', texts_dict={}, precision=0)}"'),
    ]
    
    for old_pattern, new_pattern in specific_replacements:
        if old_pattern in content:
            print(f"Spezielle Korrektur: {old_pattern[:50]}...")
            content = content.replace(old_pattern, new_pattern)
            replacements_made += 1
    
    # Überprüfe, ob Änderungen vorgenommen wurden
    if content != original_content:
        print(f"\n✓ {replacements_made} Ersetzungen vorgenommen.")
        
        # Backup der ursprünglichen Datei erstellen
        backup_path = file_path + ".backup_price_formatting"
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"✓ Backup erstellt: {backup_path}")
        except Exception as e:
            print(f"✗ Backup konnte nicht erstellt werden: {e}")
        
        # Korrigierte Datei speichern
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Korrigierte Datei gespeichert: {file_path}")
            return True
        except Exception as e:
            print(f"✗ Fehler beim Speichern: {e}")
            return False
    else:
        print("Keine Änderungen erforderlich.")
        return True

def preview_changes():
    """Zeigt eine Vorschau der geplanten Änderungen"""
    file_path = "c:\\12345\\analysis.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Fehler beim Lesen: {e}")
        return
    
    # Suche nach amerikanischen Formatierungen
    euro_patterns = re.findall(r'f"\{[^}]+:,\.\d+f\} €"', content)
    
    print("VORSCHAU: Gefundene amerikanische Euro-Formatierungen")
    print("=" * 60)
    
    for i, pattern in enumerate(euro_patterns, 1):
        print(f"{i:2d}. {pattern}")
    
    print(f"\nGesamt: {len(euro_patterns)} Formatierungen gefunden")

if __name__ == "__main__":
    print("DEUTSCHE PREISFORMATIERUNG - AUTOMATISCHE KORREKTUR")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview_changes()
    else:
        success = fix_price_formatting_in_analysis()
        if success:
            print("\n✓ Korrektur erfolgreich abgeschlossen!")
            print("Die App verwendet jetzt deutsche Preisformatierung (20.857,50 €)")
        else:
            print("\n✗ Korrektur fehlgeschlagen!")
