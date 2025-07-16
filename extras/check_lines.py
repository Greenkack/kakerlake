# check_lines.py
# Temporäres Skript zur Diagnose von Zeileninhalten mit repr()

import io
import sys
import os
import traceback

file_path = 'calculations.py'
target_line = 758 # <<< PASSEN SIE DIESE ZAHL AN DIE AKTUELL GEPOSTETE FEHLERZEILE IN calculations.py AN!
start_line = max(1, target_line - 3) # Beginn des Ausgabebereichs (3 Zeilen vor der Zielzeile)
end_line = target_line + 5 # Ende des Ausgabebereichs (5 Zeilen nach der Zielzeile)
lines_to_show = end_line - start_line + 1


print(f"--- Start der Zeilenanalyse für {file_path} ---")
print(f"Analysiere Zeilen von {start_line} bis {end_line} (oder Ende der Datei)")

try:
    # Verwenden Sie io.open mit expliziter Codierung für konsistentes Lesen
    with io.open(file_path, mode='r', encoding='utf-8') as f:
        all_lines = f.readlines() # Lesen Sie alle Zeilen in eine Liste

    total_lines = len(all_lines)
    print(f"Gesamtzahl der Zeilen in {file_path}: {total_lines}")
    print("-" * 30) # Trennlinie

    if total_lines == 0:
         print(f"Die Datei {file_path} ist leer.")
    elif total_lines < target_line:
         print(f"Datei ist kürzer als die Zielzeile {target_line}.")
         # Trotzdem die letzten paar Zeilen anzeigen, falls relevant
         start_index = max(0, total_lines - 10) # zeige letzte 10 Zeilen
         print(f"Anzeige der letzten {total_lines - start_index} Zeilen:")
         for i in range(start_index, total_lines):
             current_line_number = i + 1
             line_content = all_lines[i]
             print(f'Line {current_line_number}: {repr(line_content)}')

    else: # Datei hat mindestens die Zielzeile
        # Bestimmen Sie die tatsächlichen Start- und Endindizes für die Ausgabe
        start_index = start_line - 1 # Konvertiere 1-basierte Startzeile zu 0-basiertem Index
        end_index = min(end_line, total_lines) - 1 # Konvertiere 1-basierte Endzeile zu 0-basiertem Index


        # Iterieren Sie durch die relevanten Zeilenindizes und geben Sie die repr() Darstellung aus
        for i in range(start_index, end_index + 1):
             current_line_number = i + 1 # Konvertiere Index zurück zur 1-basierten Zeilennummer
             line_content = all_lines[i]
             print(f'Line {current_line_number}: {repr(line_content)}')

        if total_lines > end_line:
             print("...") # Zeigen Sie an, dass weitere Zeilen existieren

    print("-" * 30) # Trennlinie
    print(f"--- Ende der Zeilenanalyse für {file_path} ---")


except FileNotFoundError:
    print(f'\nFehler: Datei "{file_path}" nicht gefunden unter "{os.path.abspath(file_path)}"')
    sys.exit(1) # Skript mit Fehler beenden
except Exception as e:
    print(f'\nEin unerwarteter Fehler ist während der Analyse aufgetreten: {e}')
    traceback.print_exc() # Zeige detaillierten Fehler im Terminal
    sys.exit(1) # Skript mit Fehler beenden