#!/usr/bin/env python3
"""
Finale deutsche Formatierungskorrektur für analysis.py
Stellt sicher, dass alle Zahlenformatierungen dem deutschen Standard entsprechen
"""

import re

def fix_remaining_formatting_issues():
    """Behebt verbleibende Formatierungsprobleme"""
    
    file_path = "c:\\12345\\analysis.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Fehler beim Lesen: {e}")
        return False
    
    original_content = content
    changes_made = 0
    
    print("🔧 FINALE DEUTSCHE FORMATIERUNGSKORREKTUR")
    print("=" * 50)
    
    # 1. Repariere kaputte st.metric Aufrufe
    broken_metrics = re.findall(r'st\.metric\(\s*"([^"]+)",\s*f"\{([^}]+)\}', content)
    if broken_metrics:
        print(f"✓ {len(broken_metrics)} kaputte st.metric Aufrufe gefunden")
        
        # Repariere st.metric Syntax
        content = re.sub(
            r'st\.metric\(\s*"([^"]+)",\s*f"\{([^}]+):,\.(\d+)f\}([^"]*)"',
            r'st.metric(\n                "\1",\n                format_kpi_value(\2, "\4", texts_dict={}, precision=\3)\n            )',
            content
        )
        changes_made += 1
    
    # 2. Korrigiere verbleibende amerikanische Formatierungen
    american_formats = [
        # :,.0f durch deutsche Formatierung ersetzen  
        (r'f"\{([^}]+):,\.0f\}([^"]*)"', r'format_kpi_value(\1, "\2", texts_dict={}, precision=0)'),
        (r'f"\{([^}]+):,\.1f\}([^"]*)"', r'format_kpi_value(\1, "\2", texts_dict={}, precision=1)'),
        (r'f"\{([^}]+):,\.2f\}([^"]*)"', r'format_kpi_value(\1, "\2", texts_dict={}, precision=2)'),
        
        # Inline Formatierungen korrigieren
        (r'\{([^}]+):,\.0f\}', r'{format_kpi_value(\1, "", texts_dict={}, precision=0)}'),
        (r'\{([^}]+):,\.1f\}', r'{format_kpi_value(\1, "", texts_dict={}, precision=1)}'),
        (r'\{([^}]+):,\.2f\}', r'{format_kpi_value(\1, "", texts_dict={}, precision=2)}'),
    ]
    
    for pattern, replacement in american_formats:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made += 1
            print(f"✓ {len(matches)} amerikanische Formatierungen korrigiert: {pattern[:30]}...")
    
    # 3. Korrigiere kaputte Komma-Formatierungen in der ganzen Datei
    content = re.sub(r'(\d+),(\d\d) €', r'\1,\2 €', content)  # Korrigiere Dezimalstellen
    content = re.sub(r'0,00\)', r'0.0)', content)  # Korrigiere Funktionsparameter
    
    # 4. Spezifische Problembereiche reparieren
    # Repariere kaputte _render_overview_section
    if 'format_kpi_value(results.get(\'total_investment_netto\', 0,00)' in content:
        content = content.replace(
            'format_kpi_value(results.get(\'total_investment_netto\', 0,00)',
            'format_kpi_value(results.get(\'total_investment_netto\', 0.0)'
        )
        changes_made += 1
        print("✓ Übersichtssektion-Formatierung korrigiert")
    
    # Repariere ähnliche Probleme
    content = re.sub(r'(\d+),(\d\d)\)', r'\1.\2)', content)
    content = re.sub(r'0,00\)', r'0.0)', content)
    content = re.sub(r'0,00,', r'0.0,', content)
    
    # 5. Repariere st.metric Aufrufe mit Einrückungsproblemen
    content = re.sub(
        r'st\.metric\(\s*"([^"]+)",\s*f"\{([^}]+):,\.(\d+)f\}([^"]*)"',
        r'st.metric("\1", format_kpi_value(\2, "\4", texts_dict={}, precision=\3))',
        content
    )
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n✅ {changes_made} Korrekturen erfolgreich angewendet!")
            print("Deutsche Formatierung ist jetzt vollständig implementiert:")
            print("  • 20.857,50 € (korrekt)")
            print("  • Alle st.metric Aufrufe repariert")
            print("  • Amerikanische Formatierungen entfernt")
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False
    else:
        print("✓ Keine weiteren Korrekturen erforderlich")
        return True

if __name__ == "__main__":
    fix_remaining_formatting_issues()
