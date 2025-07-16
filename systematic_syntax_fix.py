"""
Systematische Reparatur aller Syntax-Fehler in analysis.py
"""

def fix_analysis_syntax():
    print("🔧 Starte systematische Syntax-Reparatur...")
    
    # Backup erstellen
    import shutil
    shutil.copy('analysis.py', 'analysis.py.backup_before_syntax_fix')
    print("✅ Backup erstellt: analysis.py.backup_before_syntax_fix")
    
    # Datei lesen
    with open('analysis.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Datei gelesen: {len(lines)} Zeilen")
    
    # Listen für reparierte Zeilen
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Problem 1: Zusammengeführte Zeilen reparieren  
        if '))    ' in line and 'fig.update_layout(' in line:
            # Zeile trennen
            parts = line.split('    fig.update_layout(')
            fixed_lines.append(parts[0] + '))\n')
            fixed_lines.append('    \n')
            fixed_lines.append('    fig.update_layout(\n')
            print(f"🔧 Zeile {i+1}: Zusammengeführte Zeile getrennt")
            
        # Problem 2: Falsche fig.update_layout Struktur 
        elif 'font=dict(family="Arial, sans-serif"),' in line and '"viz_' in line:
            # Diese Zeile komplett ersetzen durch korrekte Struktur
            # Extrahiere Text-Key und Fallback
            import re
            match = re.search(r'font=dict\(family="Arial, sans-serif"\),("[^"]*"),([^)]*)\)', line)
            if match:
                text_key = match.group(1)
                fallback = match.group(2)
                
                # Korrekte Struktur generieren
                indent = '        '
                fixed_lines.append(f'{indent}font=dict(family="Arial, sans-serif")\n')
                fixed_lines.append(f'{indent}),\n')
                fixed_lines.append(f'{indent}title=dict(\n')
                fixed_lines.append(f'{indent}    text=get_text(texts, {text_key}, {fallback}),\n')
                fixed_lines.append(f'{indent}    x=0.5,\n')
                fixed_lines.append(f'{indent}    font=dict(size=16)\n')
                print(f"🔧 Zeile {i+1}: fig.update_layout Struktur korrigiert")
            else:
                fixed_lines.append(line)
        
        # Problem 3: Falsche title=dict Struktur
        elif 'title=dict(text=get_text(texts, x=0.5, font=dict(size=16)),' in line:
            # Diese komplett falsche Struktur reparieren
            # Nächste Zeilen auch prüfen für vollständigen Kontext
            j = i + 1
            full_block = line
            while j < len(lines) and ('showlegend=True' in lines[j] or 'hovermode=' in lines[j] or 'plot_bgcolor=' in lines[j] or 'font=dict(' in lines[j]):
                full_block += lines[j]
                j += 1
            
            # Text-Key aus dem Block extrahieren
            import re
            match = re.search(r'"(viz_[^"]*)"', full_block)
            text_key = match.group(1) if match else "chart_title"
            
            # Korrekte Struktur erstellen
            indent = '        '
            fixed_lines.append(f'{indent}title=dict(\n')
            fixed_lines.append(f'{indent}    text=get_text(texts, "{text_key}", "Chart Title"),\n')
            fixed_lines.append(f'{indent}    x=0.5,\n')
            fixed_lines.append(f'{indent}    font=dict(size=16)\n')
            fixed_lines.append(f'{indent}),\n')
            fixed_lines.append(f'{indent}showlegend=True,\n')
            fixed_lines.append(f'{indent}hovermode="x unified",\n')
            fixed_lines.append(f'{indent}plot_bgcolor="rgba(0,0,0,0)",\n')
            fixed_lines.append(f'{indent}font=dict(family="Arial, sans-serif"),\n')
            
            # Überspringe die fehlerhaften Zeilen
            i = j - 1
            print(f"🔧 Zeile {i+1}: title=dict Struktur komplett repariert")
        
        # Problem 4: Falsche Einrückung von fig.update_layout
        elif line.strip().startswith('  fig.update_layout('):
            fixed_line = line.replace('  fig.update_layout(', '    fig.update_layout(')
            fixed_lines.append(fixed_line)
            print(f"🔧 Zeile {i+1}: Einrückung korrigiert")
        
        # Problem 5: Doppelte Klammern in st.metric
        elif 'st.metric(' in line and '))' in line and line.count(')') > line.count('('):
            # Entferne eine schließende Klammer
            fixed_line = line.replace('))', ')')
            fixed_lines.append(fixed_line)
            print(f"🔧 Zeile {i+1}: Doppelte Klammer entfernt")
        
        else:
            # Zeile unverändert übernehmen
            fixed_lines.append(line)
        
        i += 1
    
    # Reparierte Datei schreiben
    with open('analysis.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ {len(fixed_lines)} Zeilen geschrieben")
    print("🎉 Syntax-Reparatur abgeschlossen!")

if __name__ == "__main__":
    fix_analysis_syntax()
