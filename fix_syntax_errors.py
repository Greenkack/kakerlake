#!/usr/bin/env python3
"""
Skript zur Behebung der Syntax-Fehler in analysis.py
Hauptsächlich fig.update_layout Probleme
"""

import re

def fix_syntax_errors():
    """Behebt die Syntax-Fehler in analysis.py"""
    
    # Datei lesen
    with open('analysis.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Beginne Syntax-Reparatur...")
    
    # Pattern 1: Fehlerhafte fig.update_layout mit font=dict(family="Arial, sans-serif"),"text","fallback")
    pattern1 = r'font=dict\(family="Arial, sans-serif"\),("[^"]*"),("[^"]*")\)'
    
    def fix_pattern1(match):
        text_key = match.group(1)
        fallback_text = match.group(2)
        return f'font=dict(family="Arial, sans-serif")\n        ),\n        title=dict(\n            text=get_text(texts, {text_key}, {fallback_text}),\n            x=0.5,\n            font=dict(size=16)\n        )'
    
    # Suche und ersetze alle Vorkommen
    matches = re.findall(pattern1, content)
    print(f"Gefunden {len(matches)} Pattern 1 Fehler")
    
    if matches:
        content = re.sub(pattern1, fix_pattern1, content)
    
    # Pattern 2: Fehlerhafte fig.update_layout mit title=dict(text=get_text(texts, x=0.5, font=dict(size=16)),
    pattern2 = r'title=dict\(text=get_text\(texts, x=0\.5, font=dict\(size=16\)\),\s*showlegend=True,\s*hovermode=\'x unified\',\s*plot_bgcolor=\'rgba\(0,0,0,0\)\',\s*font=dict\(family="Arial, sans-serif"\),\s*("[^"]*"),\s*("[^"]*")\)'
    
    def fix_pattern2(match):
        text_key = match.group(1)
        fallback_text = match.group(2)
        return f'''title=dict(
            text=get_text(texts, {text_key}, {fallback_text}),
            x=0.5,
            font=dict(size=16)
        ),
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif")'''
    
    matches2 = re.findall(pattern2, content)
    print(f"Gefunden {len(matches2)} Pattern 2 Fehler")
    
    if matches2:
        content = re.sub(pattern2, fix_pattern2, content)
    
    # Spezielle Behandlung für die verbleibenden fehlerhaften Strukturen
    # Suche nach fehlerhaften fig.update_layout Blöcken
    broken_layouts = [
        (r'font=dict\(family="Arial, sans-serif"\),"viz_tariff_cube_title_switcher",f"Illustrativer Tarifvergleich bei \{jahresverbrauch:\.0f\} kWh/Jahr"\)', 
         'font=dict(family="Arial, sans-serif")\n        ),\n        title=dict(\n            text=get_text(texts, "viz_tariff_cube_title_switcher", f"Illustrativer Tarifvergleich bei {jahresverbrauch:.0f} kWh/Jahr"),\n            x=0.5,\n            font=dict(size=16)\n        )'),
        
        (r'font=dict\(family="Arial, sans-serif"\),"([^"]*)",("[^"]*")\),scene=dict\([^)]*\),margin=dict\([^)]*\)\)',
         lambda m: f'font=dict(family="Arial, sans-serif")\n        ),\n        title=dict(\n            text=get_text(texts, {m.group(1)}, {m.group(2)}),\n            x=0.5,\n            font=dict(size=16)\n        )')
    ]
    
    for pattern, replacement in broken_layouts:
        if isinstance(replacement, str):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    # Weitere spezifische Korrekturen
    specific_fixes = [
        # Korrigiere zusammengeführte Zeilen
        (r'(\w+)\s+(\w+\s*=)', r'\1\n    \2'),
        
        # Korrigiere falsche Einrückungen von fig.update_layout
        (r'^\s{6}fig\.update_layout\(', r'    fig.update_layout('),
        
        # Korrigiere doppelte Klammern in st.metric
        (r'st\.metric\(\s*"([^"]*)",\s*([^)]*)\)\)', r'st.metric(\n                "\1",\n                \2\n            )'),
    ]
    
    for pattern, replacement in specific_fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    print("Schreibe reparierte Datei...")
    
    # Sicherungskopie erstellen
    with open('analysis.py.backup_syntax_fix', 'w', encoding='utf-8') as f:
        with open('analysis.py', 'r', encoding='utf-8') as orig:
            f.write(orig.read())
    
    # Reparierte Datei schreiben
    with open('analysis.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Syntax-Reparatur abgeschlossen!")
    print("Backup erstellt: analysis.py.backup_syntax_fix")

if __name__ == "__main__":
    fix_syntax_errors()
