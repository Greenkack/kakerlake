from calculations.extended_calculations import ExtendedCalculations
from calculations.advanced_calculations import AdvancedCalculationsIntegrator
from calculations.mock_calculations import MockExtendedCalculations
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class PDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.styles = getSampleStyleSheet()
        self.story = []

    def add_paragraph(self, text, style_name='Normal'):
        paragraph = Paragraph(text, self.styles[style_name])
        self.story.append(paragraph)

    def add_table(self, data, col_widths):
        table = Table(data, colWidths=col_widths)
        table.setStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        self.story.append(table)

    def generate_pdf(self):
        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        doc.build(self.story)

    def visualize_calculations(self):
        mock_calculator = MockExtendedCalculations()
        extended_calculator = ExtendedCalculations()
        advanced_integrator = AdvancedCalculationsIntegrator()

        # Example of adding mock calculation results
        mock_results = mock_calculator.get_mock_results()
        self.add_paragraph("Mock Extended Calculations Results:")
        self.add_table(mock_results['data'], mock_results['col_widths'])

        # Example of adding extended calculations results
        extended_results = extended_calculator.perform_calculations()
        self.add_paragraph("Extended Calculations Results:")
        self.add_table(extended_results['data'], extended_results['col_widths'])

        # Example of adding advanced calculations results
        advanced_results = advanced_integrator.execute_selected_calculations()
        self.add_paragraph("Advanced Calculations Results:")
        self.add_table(advanced_results['data'], advanced_results['col_widths'])

# Usage example
if __name__ == "__main__":
    pdf_generator = PDFGenerator("output/calculation_results.pdf")
    pdf_generator.visualize_calculations()
    pdf_generator.generate_pdf()