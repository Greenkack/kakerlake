from calculations import AdvancedCalculationsIntegrator

integrator = AdvancedCalculationsIntegrator()
lcoe_params = {'investment': 15000, 'annual_production': 8000}
result = integrator.calculate_lcoe_advanced(lcoe_params)

required_keys = ['lcoe_simple', 'lcoe_discounted', 'grid_comparison', 'savings_potential']
print('LCOE-Test:')
for key in required_keys:
    if key in result:
        print(f'✅ {key}: {result[key]}')
    else:
        print(f'❌ {key}: FEHLT')
        
print(f'\nAlle verfügbaren Keys: {list(result.keys())}')
