import unittest
from src.calculations.mock_calculations import MockExtendedCalculations
from src.calculations.advanced_calculations import AdvancedCalculationsIntegrator
from src.pdf.generator import generate_offer_pdf

class TestPDFGeneration(unittest.TestCase):

    def setUp(self):
        self.mock_calculations = MockExtendedCalculations()
        self.advanced_calculator = AdvancedCalculationsIntegrator()
        self.project_data = {
            'project_details': {
                'include_storage': True,
                'selected_storage_storage_power_kw': 10
            }
        }
        self.analysis_results = {
            'anlage_kwp': 10,
            'annual_pv_production_kwh': 10000,
            'monthly_productions_sim': [800] * 12,
            'monthly_consumption_sim': [350] * 12,
            'total_consumption_kwh_yr': 4000,
            'total_investment_brutto': 20000,
            'annual_financial_benefit_year1': 1500,
            'self_supply_rate_percent': 60,
            'co2_savings_kg': 1200
        }
        self.company_info = {
            'name': 'Solar Solutions',
            'address': '123 Solar St, Sunnytown',
            'contact': 'info@solarsolutions.com'
        }
        self.texts = {
            "pdf_extended_analysis_intro": "Extended Analysis Introduction",
            "pdf_extended_analysis_note": "Note about extended analysis",
            "pdf_extended_analysis_error": "Error in extended analysis",
            "pdf_advanced_calculations_intro": "Advanced Calculations Introduction"
        }

    def test_generate_offer_pdf(self):
        pdf_output = generate_offer_pdf(
            project_data=self.project_data,
            analysis_results=self.analysis_results,
            company_info=self.company_info,
            company_logo_base64=None,
            selected_title_image_b64=None,
            selected_offer_title_text="Solar Offer",
            selected_cover_letter_text="Dear Customer,",
            sections_to_include=["ExtendedAnalysis", "AdvancedCalculations"],
            inclusion_options={},
            load_admin_setting_func=lambda: {},
            save_admin_setting_func=lambda x: None,
            list_products_func=lambda: [],
            get_product_by_id_func=lambda x: None,
            db_list_company_documents_func=lambda x, y: [],
            active_company_id=None,
            texts=self.texts,
            use_modern_design=True
        )
        self.assertIsNotNone(pdf_output)
        self.assertGreater(len(pdf_output), 0)

    def test_mock_extended_calculations(self):
        results = self.mock_calculations.perform_calculations()
        self.assertIn('net_present_value', results)
        self.assertIn('internal_rate_of_return', results)

    def test_advanced_calculations_integrator(self):
        calculations = [
            'degradation_analysis',
            'shading_analysis',
            'grid_interaction'
        ]
        results = self.advanced_calculator.execute_selected_calculations(calculations, self.analysis_results)
        self.assertTrue(all(key in results for key in calculations))

if __name__ == '__main__':
    unittest.main()