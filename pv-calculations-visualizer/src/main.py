from calculations.extended_calculations import ExtendedCalculations
from calculations.advanced_calculations import AdvancedCalculationsIntegrator
from calculations.mock_calculations import MockExtendedCalculations
from pdf.generator import generate_pdf
from visualizations.charts import create_charts
from visualizations.formatters import format_results

def main():
    # Initialize mock calculations for testing
    mock_calculator = MockExtendedCalculations()
    mock_results = mock_calculator.perform_calculations()

    # Initialize extended calculations
    extended_calculator = ExtendedCalculations()
    extended_results = extended_calculator.perform_extended_calculations(mock_results)

    # Initialize advanced calculations integrator
    advanced_calculator = AdvancedCalculationsIntegrator()
    advanced_results = advanced_calculator.execute_selected_calculations(extended_results)

    # Create visualizations
    charts = create_charts(advanced_results)

    # Generate PDF with results and visualizations
    pdf_output = generate_pdf(advanced_results, charts)

    # Save or display the PDF output
    with open("output/results.pdf", "wb") as pdf_file:
        pdf_file.write(pdf_output)

if __name__ == "__main__":
    main()