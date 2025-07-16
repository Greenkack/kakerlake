"""
Repariert fehlende schließende Klammern in fig.update_layout Blöcken
"""

def fix_missing_closing_parentheses():
    print("🔧 Repariere fehlende schließende Klammern...")
    
    with open('analysis.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'font=dict(family="Arial, sans-serif"),' in line:
            # Prüfe nächste Zeile
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('_apply_custom_style_to_fig'):
                # Entferne das Komma und füge schließende Klammer hinzu
                fixed_line = line.replace('font=dict(family="Arial, sans-serif"),', 'font=dict(family="Arial, sans-serif")')
                fixed_lines.append(fixed_line)
                fixed_lines.append('    )\n')  # Schließende Klammer für update_layout
                fixed_lines.append('    \n')   # Leerzeile
                print(f"🔧 Zeile {i+1}: Schließende Klammer hinzugefügt")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Datei schreiben
    with open('analysis.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Reparatur abgeschlossen!")

if __name__ == "__main__":
    fix_missing_closing_parentheses()
