#!/usr/bin/env python3
"""
Angepasster finaler Test für analysis.py 
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

def test_render_function():
    """Test der render_analysis Funktion"""
    try:
        import analysis
        
        # Test ob render_analysis verfügbar ist
        if hasattr(analysis, 'render_analysis'):
            print("✓ render_analysis Funktion gefunden")
        else:
            print("✗ render_analysis Funktion nicht gefunden")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Render-Funktions-Test-Fehler: {e}")
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

def test_emoji_removal():
    """Test ob alle Emojis entfernt wurden"""
    try:
        with open('analysis.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Häufige Emojis suchen
        emojis = ['📊', '📈', '💡', '⚡', '🔋', '🌟', '💰', '🏠', '🌱', '📋', '🔍', '⚙️', '📱', '💯', '🎯']
        found_emojis = []
        
        for emoji in emojis:
            if emoji in content:
                found_emojis.append(emoji)
        
        if found_emojis:
            print(f"✗ Emojis gefunden: {found_emojis}")
            return False
        else:
            print("✓ Keine Emojis in analysis.py gefunden")
            return True
            
    except Exception as e:
        print(f"✗ Emoji-Test-Fehler: {e}")
        return False

def test_key_functions():
    """Test wichtiger Funktionen in analysis.py"""
    try:
        import analysis
          # Test wichtiger Funktionen
        key_functions = [
            'render_analysis',
            'render_advanced_calculations_section'
        ]
        
        missing_functions = []
        for func_name in key_functions:
            if not hasattr(analysis, func_name):
                missing_functions.append(func_name)
            else:
                print(f"✓ {func_name} gefunden")
        
        if missing_functions:
            print(f"✗ Fehlende Funktionen: {missing_functions}")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Funktions-Test-Fehler: {e}")
        return False

if __name__ == "__main__":
    print("=== Finaler Test für analysis.py (Angepasst) ===")
    
    success = True
    
    print("\n1. Import-Test:")
    success &= test_import()
    
    print("\n2. Render-Funktions-Test:")
    success &= test_render_function()
    
    print("\n3. Abhängigkeits-Test:")
    success &= test_dependencies()
    
    print("\n4. Emoji-Entfernungs-Test:")
    success &= test_emoji_removal()
    
    print("\n5. Schlüssel-Funktions-Test:")
    success &= test_key_functions()
    
    print(f"\n=== Gesamtergebnis: {'✓ ALLE TESTS ERFOLGREICH' if success else '✗ FEHLER GEFUNDEN'} ===")
