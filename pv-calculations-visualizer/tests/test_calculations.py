import unittest
from src.calculations.extended_calculations import ExtendedCalculations
from src.calculations.advanced_calculations import AdvancedCalculationsIntegrator
from src.calculations.mock_calculations import MockExtendedCalculations

class TestCalculations(unittest.TestCase):

    def setUp(self):
        self.extended_calculations = ExtendedCalculations()
        self.advanced_calculations_integrator = AdvancedCalculationsIntegrator()
        self.mock_calculations = MockExtendedCalculations()

    def test_extended_calculations(self):
        input_data = {
            'total_investment': 10000,
            'annual_savings': 1200,
            'annual_production_kwh': 8000,
            'pv_size_kwp': 10,
            'total_embodied_energy_kwh': 20000
        }
        results = self.extended_calculations.calculate(input_data)
        self.assertIn('net_present_value', results)
        self.assertIn('internal_rate_of_return', results)

    def test_advanced_calculations_integration(self):
        base_data = {
            'anlage_kwp': 10,
            'annual_pv_production_kwh': 8000,
            'monthly_production': [800] * 12,
            'monthly_consumption': [350] * 12,
            'total_consumption_kwh_yr': 4000,
            'system_lifetime_years': 25
        }
        selected_calculations = ['degradation_analysis', 'shading_analysis']
        results = self.advanced_calculations_integrator.execute_selected_calculations(selected_calculations, base_data)
        self.assertTrue(all(calc in results for calc in selected_calculations))

    def test_mock_extended_calculations(self):
        mock_data = {
            'total_investment': 10000,
            'annual_savings': 1200
        }
        results = self.mock_calculations.simulate(mock_data)
        self.assertEqual(results['mocked_npv'], 5000)

if __name__ == '__main__':
    unittest.main()