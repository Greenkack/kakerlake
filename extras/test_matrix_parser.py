# test_matrix_parser.py
from typing import List, Optional # Import für Typ-Hints hinzugefügt
import io
import pandas as pd
import traceback
# Stellen Sie sicher, dass calculations.py im PYTHONPATH ist oder im selben Verzeichnis liegt
# oder passen Sie den Importpfad entsprechend an, wenn calculations.py woanders liegt.
# Für diesen Test gehen wir davon aus, dass es im selben Verzeichnis ist oder im PYTHONPATH.
try:
    from calculations import parse_price_matrix_csv
    CALCULATIONS_MODULE_AVAILABLE = True
except ImportError:
    CALCULATIONS_MODULE_AVAILABLE = False
    print("FEHLER: Modul 'calculations.py' nicht gefunden. Stellen Sie sicher, dass es im PYTHONPATH ist.")
    print("Die Funktion 'parse_price_matrix_csv' kann nicht getestet werden.")
    # Definieren Sie eine Dummy-Funktion, damit der Rest des Skripts nicht sofort abbricht,
    # aber es wird nicht wirklich testen.
    def parse_price_matrix_csv(csv_input: any, calculation_errors: List[str]) -> Optional[pd.DataFrame]: # type: ignore
        print("WARNUNG: Dummy parse_price_matrix_csv wird verwendet, da calculations.py nicht geladen werden konnte.")
        calculation_errors.append("Dummy parser used for testing.")
        return None

# Pfad zu Ihrer CSV-Datei (korrigiert)
PRICE_MATRIX_FILE_PATH = 'data/price_matrix.csv'

print(f"Versuche, '{PRICE_MATRIX_FILE_PATH}' zu parsen...")

if not CALCULATIONS_MODULE_AVAILABLE:
    print("Test kann nicht fortgesetzt werden, da 'parse_price_matrix_csv' nicht importiert werden konnte.")
else:
    try:
        with open(PRICE_MATRIX_FILE_PATH, 'r', encoding='utf-8') as f:
            csv_content_str = f.read()

        if not csv_content_str.strip():
            print("FEHLER: CSV-Datei ist leer oder enthält nur Leerzeichen.")
        else:
            parser_errors_test: List[str] = [] # Fehlerliste für den Test, Typ-Hint korrigiert
            df_parsed = parse_price_matrix_csv(csv_content_str, parser_errors_test) # KORRIGIERTER AUFRUF

            if parser_errors_test:
                print("\n--- Parser-Meldungen während des Tests: ---")
                for err in parser_errors_test:
                    print(err)

            if df_parsed is not None and not df_parsed.empty:
                print("\n--- CSV erfolgreich geparst! ---")
                print("Info zum DataFrame:")
                df_parsed.info()
                print("\nErste 5 Zeilen des DataFrames:")
                print(df_parsed.head())
                print("\nLetzte 5 Zeilen des DataFrames:")
                print(df_parsed.tail())
                print("\nIndex:")
                print(df_parsed.index)
                print("\nSpalten:")
                print(df_parsed.columns.tolist())

                # Test: Versuchen, auf einen Wert zuzugreifen (Beispiel)
                try:
                    test_index_val = 20
                    test_column_name = "Ohne Speicher" # Passen Sie dies an Ihre CSV an!

                    if test_index_val in df_parsed.index and test_column_name in df_parsed.columns:
                        value = df_parsed.loc[test_index_val, test_column_name]
                        print(f"\nTestzugriff (Zeile {test_index_val}, Spalte '{test_column_name}'): {value} (Typ: {type(value)})")
                    else:
                        missing_info = []
                        if test_index_val not in df_parsed.index:
                            missing_info.append(f"Index {test_index_val} nicht gefunden.")
                        if test_column_name not in df_parsed.columns:
                            missing_info.append(f"Spalte '{test_column_name}' nicht gefunden.")
                        print(f"\nTestzugriff nicht möglich: {', '.join(missing_info)}")
                        if test_column_name not in df_parsed.columns:
                             print(f"Verfügbare Spalten sind: {df_parsed.columns.tolist()}")
                except Exception as e_access:
                    print(f"\nFehler beim Testzugriff auf Matrixdaten: {e_access}")

            elif df_parsed is None:
                print("\nFEHLER: Parsen der CSV gab None zurück (möglicherweise interner Fehler in parse_price_matrix_csv oder die Datei konnte nicht korrekt verarbeitet werden).")
            else: # df_parsed ist leeres DataFrame
                print("\nWARNUNG: CSV geparst, aber das Ergebnis-DataFrame ist leer.")

    except FileNotFoundError:
        print(f"FEHLER: Datei '{PRICE_MATRIX_FILE_PATH}' nicht gefunden. Bitte Pfad prüfen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler beim Testen des CSV-Parsers ist aufgetreten: {e}")
        traceback.print_exc()