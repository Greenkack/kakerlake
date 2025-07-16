#!/usr/bin/env python3
"""Test-Skript für Module-Imports"""

def test_imports():
    try:
        import calculations
        print("✅ calculations erfolgreich importiert")
    except Exception as e:
        print(f"❌ calculations Import-Fehler: {e}")
        return False

    try:
        import analysis
        print("✅ analysis erfolgreich importiert")
    except Exception as e:
        print(f"❌ analysis Import-Fehler: {e}")
        return False

    try:
        import multi_offer_generator
        print("✅ multi_offer_generator erfolgreich importiert")
    except Exception as e:
        print(f"❌ multi_offer_generator Import-Fehler: {e}")
        return False

    print("\n🎉 ALLE MODULE ERFOLGREICH IMPORTIERT!")
    return True

if __name__ == "__main__":
    test_imports()
