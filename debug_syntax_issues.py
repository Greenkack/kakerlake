#!/usr/bin/env python3
"""
Debug-Tool zur Identifikation des exact Syntax-Problems in TXT-Dateien.
"""
import os
import ast


def debug_syntax_errors():
    """
    Testet jede TXT-Datei auf Syntax-Probleme bei Position-Parsing.
    """

    input_dir = "input"
    if not os.path.exists(input_dir):
        print(f" Ordner '{input_dir}' nicht gefunden!")
        return

    print(" Suche nach Syntax-Problemen in TXT-Dateien...")
    print("=" * 60)

    for i in range(1, 21):
        filename = f"seite_{i}_texte.txt"
        filepath = os.path.join(input_dir, filename)

        if not os.path.exists(filepath):
            continue

        print(f"\n Teste {filename}...")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        block_num = 0
        for block in content.split("-" * 40):
            lines = [l for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            block_num += 1

            for line_num, line in enumerate(lines):
                line = line.strip()

                # Position-Test
                if line.startswith("Position:"):
                    position_text = line.split("Position:", 1)[1].strip()
                    try:
                        # Test der Position-Parsing
                        position_tuple = ast.literal_eval(position_text)
                        # Zusätzlicher Test: sind alle Werte numerisch?
                        for val in position_tuple:
                            float(val)  # Test auf Konvertierbarkeit zu float
                    except Exception as e:
                        print(f" FEHLER in Block {block_num}, Zeile {line_num + 1}:")
                        print(f"   Position: {position_text}")
                        print(f"   Fehler: {e}")
                        return False

                # Farb-Test
                elif line.startswith("Farbe:"):
                    color_text = line.split("Farbe:", 1)[1].strip()
                    try:
                        color_int = int(color_text)
                    except Exception as e:
                        print(f" FEHLER in Block {block_num}, Zeile {line_num + 1}:")
                        print(f"   Farbe: {color_text}")
                        print(f"   Fehler: {e}")
                        return False

                # Schriftgröße-Test
                elif line.startswith("Schriftgröße:"):
                    size_text = line.split("Schriftgröße:", 1)[1].strip()
                    try:
                        size_float = float(size_text)
                    except Exception as e:
                        print(f" FEHLER in Block {block_num}, Zeile {line_num + 1}:")
                        print(f"   Schriftgröße: {size_text}")
                        print(f"   Fehler: {e}")
                        return False

        print(f" {filename}: Alle Syntax-Tests bestanden")

    print(f"\n Alle TXT-Dateien haben gültige Syntax!")
    return True


if __name__ == "__main__":
    success = debug_syntax_errors()

    if success:
        print("\n Keine Syntax-Probleme gefunden!")
        print(" Das Problem liegt wahrscheinlich woanders...")
    else:
        print("\n  Syntax-Probleme identifiziert und angezeigt")
