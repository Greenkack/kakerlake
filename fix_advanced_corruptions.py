#!/usr/bin/env python3
"""
Erweiterte Wiederherstellung aller numerischen Werte in TXT-Dateien.
Repariert Position-Koordinaten, die noch Keys enthalten.
"""
import os
import re

def advanced_numeric_restoration():
    """
    Repariert alle numerischen Korruptionen in den TXT-Dateien.
    """
    
    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f"❌ Ordner '{input_dir}' nicht gefunden!")
        return
    
    total_fixes = 0
    
    # Alle TXT-Dateien durchgehen
    for i in range(1, 21):
        filename = f"seite_{i}_texte.txt"
        filepath = os.path.join(input_dir, filename)
        
        if not os.path.exists(filepath):
            continue
        
        # Datei einlesen
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_fixes = 0
        
        # Position-Zeilen mit Keys reparieren
        position_lines = re.findall(r'Position: \([^)]+\)', content)
        for pos_line in position_lines:
            if '{' in pos_line:
                # Korrupte Position-Zeile gefunden
                print(f"   🔧 {filename}: Korrupte Position gefunden: {pos_line}")
                
                # Keys in Koordinaten entfernen und durch plausible Werte ersetzen
                repaired_line = pos_line
                
                # module_quantity (21) Ersetzungen in Koordinaten
                repaired_line = re.sub(r'(\d+)\.?\{module_quantity\}(\d*)', lambda m: f"{m.group(1)}.21{m.group(2)}", repaired_line)
                repaired_line = re.sub(r'\{module_quantity\}(\d+)', r'21\1', repaired_line)
                
                # roof_angle (30) Ersetzungen in Koordinaten  
                repaired_line = re.sub(r'(\d+)\.?\{roof_angle\}(\d*)', lambda m: f"{m.group(1)}.30{m.group(2)}", repaired_line)
                repaired_line = re.sub(r'\{roof_angle\}(\d+)', r'30\1', repaired_line)
                
                if repaired_line != pos_line:
                    content = content.replace(pos_line, repaired_line)
                    file_fixes += 1
                    print(f"   ✅ Repariert zu: {repaired_line}")
        
        # Farb-Zeilen mit Keys reparieren
        color_lines = re.findall(r'Farbe: [^\n]+', content)
        for color_line in color_lines:
            if '{' in color_line:
                print(f"   🔧 {filename}: Korrupte Farbe gefunden: {color_line}")
                
                repaired_line = color_line
                repaired_line = re.sub(r'(\d+)\{module_quantity\}(\d*)', r'\g<1>21\g<2>', repaired_line)
                repaired_line = re.sub(r'\{module_quantity\}(\d+)', r'21\1', repaired_line)
                repaired_line = re.sub(r'(\d+)\{roof_angle\}(\d*)', r'\g<1>30\g<2>', repaired_line)
                repaired_line = re.sub(r'\{roof_angle\}(\d+)', r'30\1', repaired_line)
                
                if repaired_line != color_line:
                    content = content.replace(color_line, repaired_line)
                    file_fixes += 1
                    print(f"   ✅ Repariert zu: {repaired_line}")
        
        # Schriftgröße-Zeilen mit Keys reparieren
        size_lines = re.findall(r'Schriftgröße: [^\n]+', content)
        for size_line in size_lines:
            if '{' in size_line:
                print(f"   🔧 {filename}: Korrupte Schriftgröße gefunden: {size_line}")
                
                repaired_line = size_line
                repaired_line = re.sub(r'(\d+)\.?\{module_quantity\}(\d*)', r'\g<1>.21\g<2>', repaired_line)
                repaired_line = re.sub(r'\{module_quantity\}(\d+)', r'21\1', repaired_line)
                repaired_line = re.sub(r'(\d+)\.?\{roof_angle\}(\d*)', r'\g<1>.30\g<2>', repaired_line)
                repaired_line = re.sub(r'\{roof_angle\}(\d+)', r'30\1', repaired_line)
                
                if repaired_line != size_line:
                    content = content.replace(size_line, repaired_line)
                    file_fixes += 1
                    print(f"   ✅ Repariert zu: {repaired_line}")
        
        # Datei zurückschreiben wenn Änderungen gemacht wurden
        if file_fixes > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filename}: {file_fixes} Korrekturen gespeichert")
            total_fixes += file_fixes
        else:
            print(f"ℹ️  {filename}: Keine zusätzlichen Korrekturen nötig")
    
    print(f"\n🎯 Erweiterte Wiederherstellung abgeschlossen: {total_fixes} Korrekturen insgesamt")
    return total_fixes > 0

if __name__ == "__main__":
    print("🚑 Starte erweiterte Wiederherstellung numerischer Werte...")
    print("=" * 60)
    
    success = advanced_numeric_restoration()
    
    if success:
        print("\n✅ Erweiterte Wiederherstellung erfolgreich!")
        print("💡 Tipp: Führe jetzt 'python test_dynamic_keys.py' aus zum Testen")
    else:
        print("\n⚠️  Keine zusätzlichen Korruptionen gefunden")
