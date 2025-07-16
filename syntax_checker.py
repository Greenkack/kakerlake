#!/usr/bin/env python3
"""
Multi-Offer Generator Syntax Checker und Fixer
"""
import ast

def check_and_fix_syntax():
    """Überprüft die Syntax und zeigt Probleme an"""
    
    try:
        with open('multi_offer_generator.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Versuche zu parsen
        ast.parse(content)
        print("✅ Syntax ist korrekt!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler gefunden:")
        print(f"Zeile {e.lineno}: {e.msg}")
        print(f"Text: {e.text.strip() if e.text else 'Nicht verfügbar'}")
        print(f"Position: {e.offset}")
        
        # Zeige Kontext um den Fehler
        lines = content.split('\n')
        start_line = max(0, e.lineno - 3)
        end_line = min(len(lines), e.lineno + 3)
        
        print(f"\nKontext um Zeile {e.lineno}:")
        for i in range(start_line, end_line):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:3d}: {lines[i]}")
        
        return False
    
    except Exception as e:
        print(f"❌ Unbekannter Fehler: {e}")
        return False

if __name__ == "__main__":
    check_and_fix_syntax()
