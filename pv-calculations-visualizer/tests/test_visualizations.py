import unittest
from src.calculations.mock_calculations import MockExtendedCalculations
from src.calculations.extended_calculations import ExtendedCalculations
from src.calculations.advanced_calculations import AdvancedCalculationsIntegrator
from src.visualizations.charts import create_chart
from src.visualizations.formatters import format_data_for_visualization

class TestVisualizations(unittest.TestCase):

    def setUp(self):
        self.mock_calculations = MockExtendedCalculations()
        self.extended_calculations = ExtendedCalculations()
        self.advanced_calculations_integrator = AdvancedCalculationsIntegrator()

    def test_mock_extended_calculations(self):
        results = self.mock_calculations.perform_calculations()
        self.assertIsNotNone(results)
        self.assertIn('mock_result', results)

    def test_extended_calculations(self):
        input_data = {
            'total_investment': 10000,
            'annual_savings': 1200,
            'annual_production_kwh': 8000,
            'pv_size_kwp': 10
        }
        results = self.extended_calculations.calculate(input_data)
        self.assertIsNotNone(results)
        self.assertIn('npv', results)
        self.assertIn('irr', results)

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
        self.assertIsNotNone(results)
        self.assertIn('degradation_analysis', results)
        self.assertIn('shading_analysis', results)

    def test_create_chart(self):
        data = [1, 2, 3, 4, 5]
        chart = create_chart(data)
        self.assertIsNotNone(chart)

    def test_format_data_for_visualization(self):
        data = {'value': 100, 'label': 'Test'}
        formatted_data = format_data_for_visualization(data)
        self.assertEqual(formatted_data['label'], 'Test')
        self.assertEqual(formatted_data['value'], 100)

if __name__ == '__main__':
    unittest.main()