#!/usr/bin/env python3
"""
Finaler Test für analysis.py nach Behebung aller Fehler
"""

def test_import():
    """Test ob analysis.py importiert werden kann"""
    try:
        import analysis
        print("✓ Import von analysis.py erfolgreich")
        return True
    except Exception as e:
        print(f"✗ Import-Fehler: {e}")
        return False

def test_main_functions():
    """Test der Hauptfunktionen von analysis.py"""
    try:
        import analysis
        
        # Test ob render_analysis verfügbar ist
        if hasattr(analysis, 'render_analysis'):
            print("✓ render_analysis Funktion gefunden")
        else:
            print("✗ render_analysis Funktion nicht gefunden")
            return False
            
        # Test ob MockExtendedCalculations verfügbar ist
        if hasattr(analysis, 'MockExtendedCalculations'):
            print("✓ MockExtendedCalculations Klasse gefunden")
            
            # Test der Mock-Klasse
            mock = analysis.MockExtendedCalculations()
            test_data = {'annual_pv_production_kwh': 10000, 'total_investment': 25000}
            
            # Test aller Mock-Methoden
            methods_to_test = [
                'calculate_degradation_analysis',
                'calculate_financial_scenarios', 
                'calculate_environmental_impact',
                'calculate_battery_optimization'
            ]
            
            for method_name in methods_to_test:
                if hasattr(mock, method_name):
                    method = getattr(mock, method_name)
                    result = method(test_data)
                    print(f"✓ {method_name} funktioniert, Rückgabe: {type(result)}")
                else:
                    print(f"✗ {method_name} nicht gefunden")
                    return False
        else:
            print("✗ MockExtendedCalculations Klasse nicht gefunden")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Funktionstest-Fehler: {e}")
        return False

def test_dependencies():
    """Test der Abhängigkeits-Checks"""
    try:
        import analysis
        
        # Test ob _ANALYSIS_DEPENDENCIES_AVAILABLE korrekt gesetzt wird
        if hasattr(analysis, '_ANALYSIS_DEPENDENCIES_AVAILABLE'):
            print(f"✓ _ANALYSIS_DEPENDENCIES_AVAILABLE = {analysis._ANALYSIS_DEPENDENCIES_AVAILABLE}")
        else:
            print("✗ _ANALYSIS_DEPENDENCIES_AVAILABLE nicht gefunden")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Abhängigkeits-Test-Fehler: {e}")
        return False

if __name__ == "__main__":
    print("=== Finaler Test für analysis.py ===")
    
    success = True
    
    print("\n1. Import-Test:")
    success &= test_import()
    
    print("\n2. Funktions-Test:")
    success &= test_main_functions()
    
    print("\n3. Abhängigkeits-Test:")
    success &= test_dependencies()
    
    print(f"\n=== Gesamtergebnis: {'✓ ALLE TESTS ERFOLGREICH' if success else '✗ FEHLER GEFUNDEN'} ===")
