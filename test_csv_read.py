import pandas as pd
import io
import traceback

# Eine einfache CSV-Struktur als String (Semikolon Trenner, Komma Dezimal)
csv_string_simple = """IndexSpalte;Spalte A;Spalte B
1;10,5;20
2;11,2;21
3;12,8;22
"""

print("Teste pd.read_csv mit hartkodiertem String...")
try:
    # Versuche, den String mit den erwarteten Parametern zu parsen
    df_test = pd.read_csv(
        io.StringIO(csv_string_simple),
        header=0,
        index_col=0,
        sep=';',
        decimal=',',
        encoding='utf-8',
        engine='python', # Verwende die robuste Engine
        skipinitialspace=True # Leerzeichen nach Trenner ignorieren
    )

    print("✅ pd.read_csv Test erfolgreich!")
    print("Gelesener DataFrame:")
    print(df_test)
    print(f"Shape: {df_test.shape}")
    print(f"Columns: {df_test.columns.tolist()}")
    print(f"Index: {df_test.index.tolist()}")
    print(f"Dtypes: {df_test.dtypes}")

except Exception as e:
    print(f"❌ pd.read_csv Test fehlgeschlagen: {e}")
    traceback.print_exc()

print("\nTest abgeschlossen.")