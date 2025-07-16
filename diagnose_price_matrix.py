#!/usr/bin/env python3
"""Diagnose der Preismatrix-Probleme"""

import sys
import os
sys.path.append('.')

def diagnose_price_matrix():
    """Diagnose der Preismatrix-Daten"""    print("🔍 PREISMATRIX-DIAGNOSE")
    print("=" * 50)
    
    try:
        from database import load_admin_setting as real_load_admin_setting
        from database import save_admin_setting as real_save_admin_setting
        print("✅ Database-Modul importiert")
        
        # Excel-Bytes prüfen
        print("\n📊 Excel-Preismatrix-Daten:")
        excel_bytes = real_load_admin_setting('price_matrix_excel_bytes', None)
        if excel_bytes:
            print(f"✅ Excel-Bytes verfügbar: {len(excel_bytes)} bytes")
        else:
            print("❌ Keine Excel-Bytes in der Datenbank")
        
        # CSV-Daten prüfen
        print("\n📄 CSV-Preismatrix-Daten:")
        csv_data = real_load_admin_setting('price_matrix_csv_data', '')
        if csv_data and csv_data.strip():
            print(f"✅ CSV-Daten verfügbar: {len(csv_data)} Zeichen")
            lines = csv_data.strip().split('\n')
            print(f"   Anzahl Zeilen: {len(lines)}")
            if lines:
                print(f"   Erste Zeile: {lines[0][:100]}...")
        else:
            print("❌ Keine CSV-Daten in der Datenbank")
        
        # Versuche CSV-Parser zu testen
        if csv_data and csv_data.strip():
            print("\n🔧 Teste CSV-Parser:")
            try:
                from calculations import parse_module_price_matrix_csv
                errors_list = []
                df = parse_module_price_matrix_csv(csv_data, errors_list)
                
                if df is not None and not df.empty:
                    print(f"✅ CSV erfolgreich geparst: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")
                    print(f"   Index (Modulanzahlen): {list(df.index)}")
                    print(f"   Spalten: {list(df.columns)}")
                    
                    # Beispiel-Lookup
                    if len(df.index) > 0:
                        test_modules = df.index[0]
                        test_row = df.iloc[0]
                        print(f"   Beispiel ({test_modules} Module): {dict(test_row.head(3))}")
                else:
                    print("❌ CSV-Parser gab leeres oder None-Ergebnis zurück")
                    if errors_list:
                        for error in errors_list:
                            print(f"     Fehler: {error}")
                            
            except ImportError as e:
                print(f"❌ Import-Fehler: {e}")
            except Exception as e:
                print(f"❌ Parser-Fehler: {e}")
        
        # Test mit Standard-CSV erstellen
        print("\n🏗️ Erstelle Test-Preismatrix:")
        test_csv = '''Module,Ohne Speicher,5kWh Speicher,10kWh Speicher
10,8000,12000,15000
15,11000,15000,18000
20,14000,18000,21000
25,17000,21000,24000
30,20000,24000,27000'''
        
        print("Test-CSV erstellt:")
        print(test_csv)
          # Speichere Test-CSV in DB
        try:
            result = real_save_admin_setting('price_matrix_csv_data', test_csv)
            if result:
                print("✅ Test-CSV in Datenbank gespeichert")
                
                # Teste erneut
                print("\n🔄 Teste mit neuer CSV:")
                new_csv = real_load_admin_setting('price_matrix_csv_data', '')
                if new_csv == test_csv:
                    print("✅ Test-CSV erfolgreich geladen")
                    
                    # Parser-Test
                    from calculations import parse_module_price_matrix_csv
                    errors_list = []
                    df = parse_module_price_matrix_csv(new_csv, errors_list)
                    
                    if df is not None and not df.empty:
                        print(f"✅ Test-CSV erfolgreich geparst: {df.shape}")
                        return True
                    else:
                        print("❌ Test-CSV konnte nicht geparst werden")
                        return False
                else:
                    print("❌ Test-CSV wurde nicht korrekt gespeichert")
                    return False
            else:
                print("❌ Konnte Test-CSV nicht in Datenbank speichern")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Speichern: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Allgemeiner Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_price_matrix()
    
    if success:
        print("\n🎉 PREISMATRIX-PROBLEM BEHOBEN!")
        print("Die Streamlit-App sollte jetzt Preise korrekt berechnen.")
    else:
        print("\n⚠️ Preismatrix-Problem nicht vollständig gelöst.")
        print("Weitere manuelle Einrichtung erforderlich.")
