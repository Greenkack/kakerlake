#!/usr/bin/env python3
"""
Test-Skript um die Fixes in analysis.py zu prüfen
"""

print("=== Test der analysis.py Fixes ===")

# 1. Import-Test
try:
    import analysis
    print("✓ analysis.py Import erfolgreich")
except Exception as e:
    print(f"✗ Import-Fehler: {e}")
    exit(1)

# 2. Test der render_advanced_calculations_section Funktion
try:
    # Mock-Daten
    project_data = {"customer_data": {"name": "Test"}}
    calc_results = {"annual_pv_production_kwh": 8000}
    texts = {"test": "test"}
    
    # Funktion existiert?
    func = getattr(analysis, 'render_advanced_calculations_section', None)
    if func:
        print("✓ render_advanced_calculations_section Funktion gefunden")
        # Teste die Signatur
        import inspect
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        if 'calc_results' in params and 'analysis_results' not in params:
            print("✓ Funktionssignatur korrekt (calc_results statt analysis_results)")
        else:
            print(f"✗ Funktionssignatur falsch: {params}")
    else:
        print("✗ render_advanced_calculations_section nicht gefunden")
except Exception as e:
    print(f"✗ Funktions-Test fehler: {e}")

# 3. Test der AdvancedCalculationsIntegrator Methoden
try:
    from calculations import AdvancedCalculationsIntegrator
    integrator = AdvancedCalculationsIntegrator()
    
    # Teste die zuvor fehlenden Methoden
    methods_to_test = [
        'calculate_shading_analysis',
        'calculate_subsidy_scenarios', 
        'generate_optimization_suggestions',
        'calculate_detailed_co2_analysis'
    ]
    
    for method_name in methods_to_test:
        if hasattr(integrator, method_name):
            print(f"✓ {method_name} Methode verfügbar")
        else:
            print(f"✗ {method_name} Methode fehlt")
            
except Exception as e:
    print(f"✗ Integrator-Test fehler: {e}")

# 4. Test auf Emojis
try:
    with open('analysis.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    emoji_count = 0
    emojis = ['⚠️', '🔥', '💡', '📊', '🌟', '⚡', '🎯', '🔧', '🚀', '📈', '💰', '🏆', '✅', '❌', '📱', '💻', '🌍', '♻️', '🌱', '🏗️', '⭐', '💎', '🎉', '🔍', '🌞', '⚡️', '🏡', '🎆', '☀️', '🗓️', '⚖️', '☁️', '🛠️', '🏘️', '🌤️', '🌡️', '🏛️', '⚙️', '🎛️']
    
    for emoji in emojis:
        emoji_count += content.count(emoji)
    
    if emoji_count == 0:
        print("✓ Alle Emojis erfolgreich entfernt")
    else:
        print(f"✗ Noch {emoji_count} Emojis gefunden")
        
except Exception as e:
    print(f"✗ Emoji-Test fehler: {e}")

print("\n=== Test abgeschlossen ===")
