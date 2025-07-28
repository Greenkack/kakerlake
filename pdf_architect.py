# Datei: pdf_architect.py
# FINALE KORRIGIERTE VERSION

# Benötigte Bibliotheken importieren
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import io
from reportlab.lib.utils import ImageReader

# --- ERWEITERTE STYLESHEET KLASSE ---
class Stylesheet:
    """
    Verwaltet alle globalen Design-Aspekte und macht das PDF "skinbar".
    """
    def __init__(self, theme_name="Default", **kwargs):
        self.theme_name = theme_name
        self.width, self.height = A4

        defaults = {
            "logo_path": None,
            "logo_pos": (self.width - 4*cm, self.height - 2.5*cm),
            "logo_size": (3*cm, 1.5*cm),
            "font_main": "Helvetica",
            "font_heading": "Helvetica-Bold",
            "font_size_title": 18,
            "font_size_heading": 14,
            "font_size_body": 10,
            "font_size_footer": 8,
            "color_primary": "#00008B",
            "color_text": "#333333",
            "color_heading": "#000000",
            "page_margin_x": 2*cm,
            "page_margin_y": 2*cm,
            "footer_text": f"© {datetime.now().year} Ihr Unternehmen",
            "company_details": "Firmenname | Straße 1 | 12345 Stadt"
        }
        self.config = {**defaults, **kwargs}

    def get(self, key):
        return self.config.get(key)

    def draw_static_elements(self, pdf_canvas, page_number): # <--- KORREKTUR HIER
        """Zeichnet auf jeder Seite wiederkehrende Elemente (Header, Footer, Logo)."""
        pdf_canvas.saveState()
        if self.get("logo_path"):
            try:
                logo_x, logo_y = self.get("logo_pos")
                logo_w, logo_h = self.get("logo_size")
                pdf_canvas.drawImage(self.get("logo_path"), logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Warnung: Logo konnte nicht gezeichnet werden. {e}")
        
        pdf_canvas.setFont(self.get("font_main"), self.get("font_size_body"))
        pdf_canvas.setFillColor(HexColor(self.get("color_text")))
        pdf_canvas.drawString(self.get("page_margin_x"), self.height - 2*cm, self.get("company_details"))
        
        pdf_canvas.setFont(self.get("font_main"), self.get("font_size_footer"))
        pdf_canvas.setFillColor(HexColor(self.get("color_text")))
        pdf_canvas.drawString(self.get("page_margin_x"), self.get("page_margin_y"), self.get("footer_text"))
        pdf_canvas.drawRightString(self.width - self.get("page_margin_x"), self.get("page_margin_y"), f"Seite {page_number}")
        pdf_canvas.restoreState()

# --- CONTENT BLOCK KLASSEN ---
class ContentBlock:
    def __init__(self, title):
        if not title: raise ValueError("Jeder ContentBlock muss einen Titel haben.")
        self.title = title
    def render(self, pdf_architect, pdf_canvas):
        raise NotImplementedError("Render-Methode muss implementiert werden.")

class TextBlock(ContentBlock):
    def __init__(self, title, text_content):
        super().__init__(title)
        self.text_content = text_content
    def render(self, pdf_architect, pdf_canvas):
        styles = getSampleStyleSheet()
        p = Paragraph(self.text_content, styles['BodyText'])
        pdf_canvas.setFont(pdf_architect.stylesheet.get("font_heading"), pdf_architect.stylesheet.get("font_size_heading"))
        # Position des Titels an die Seitenränder angepasst
        title_x = pdf_architect.stylesheet.get("page_margin_x")
        title_y = pdf_architect.stylesheet.height - pdf_architect.stylesheet.get("page_margin_y") - 2*cm
        pdf_canvas.drawString(title_x, title_y, self.title)
        # Position des Textes angepasst
        p.wrapOn(pdf_canvas, pdf_architect.stylesheet.width - 2*pdf_architect.stylesheet.get("page_margin_x"), pdf_architect.stylesheet.height)
        p.drawOn(pdf_canvas, title_x, title_y - 1*cm)

class ImageBlock(ContentBlock):
    def __init__(self, title, image_path):
        super().__init__(title)
        self.image_path = image_path
    def render(self, pdf_architect, pdf_canvas):
        try:
            pdf_canvas.drawImage(self.image_path, 0, 0, width=pdf_architect.stylesheet.width, height=pdf_architect.stylesheet.height, preserveAspectRatio=True)
        except Exception as e:
            print(f"WARNUNG: Bild konnte nicht geladen werden: {self.image_path}. Fehler: {e}")

class ProductionConsumptionChartBlock(ContentBlock):
    def __init__(self, title, analysis_results, texts):
        super().__init__(title)
        self.analysis_results = analysis_results
        self.texts = texts
    def render(self, pdf_architect, pdf_canvas):
        try:
            # Annahme: Ihre alte Datei heißt jetzt wirklich so
            from pdf_generator import generate_prod_vs_cons_chart_image
        except ImportError:
            print("FEHLER: 'pdf_generator.py' konnte nicht gefunden werden.")
            return
        image_bytes = generate_prod_vs_cons_chart_image(self.analysis_results, self.texts)
        if image_bytes:
            pdf_canvas.setFont(pdf_architect.stylesheet.get("font_heading"), pdf_architect.stylesheet.get("font_size_heading"))
            title_x = pdf_architect.stylesheet.get("page_margin_x")
            title_y = pdf_architect.stylesheet.height - pdf_architect.stylesheet.get("page_margin_y") - 2*cm
            pdf_canvas.drawString(title_x, title_y, self.title)
            
            image_reader = ImageReader(io.BytesIO(image_bytes))
            # Positionierung des Diagramms auf der Seite
            img_width = pdf_architect.stylesheet.width - 2 * title_x
            img_x = title_x
            img_y = 5*cm 
            pdf_canvas.drawImage(image_reader, img_x, img_y, width=img_width, preserveAspectRatio=True)
        else:
            pdf_canvas.drawString(2*cm, 15*cm, f"Diagramm '{self.title}' konnte nicht erstellt werden.")

class TableBlock(ContentBlock):
    """Ein Block zur Darstellung von Daten in einer Tabelle."""
    def __init__(self, title, table_data, col_widths=None):
        super().__init__(title)
        # Stellt sicher, dass table_data eine Liste von Listen ist
        if not all(isinstance(row, list) for row in table_data):
            raise ValueError("table_data muss eine Liste von Listen sein (z.B. [['a', 'b'], ['c', 'd']])")
        self.table_data = table_data
        self.col_widths = col_widths

    def render(self, pdf_architect, pdf_canvas):
        # Titel zeichnen
        pdf_canvas.setFont(pdf_architect.stylesheet.get("font_heading"), pdf_architect.stylesheet.get("font_size_heading"))
        title_x = pdf_architect.stylesheet.get("page_margin_x")
        title_y = pdf_architect.stylesheet.height - pdf_architect.stylesheet.get("page_margin_y") - 2*cm
        pdf_canvas.drawString(title_x, title_y, self.title)

        # Tabelle erstellen
        table = Table(self.table_data, colWidths=self.col_widths)

        # Modernes Tabellen-Styling anwenden
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_architect.stylesheet.get("color_primary")), # Header-Hintergrund
            ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'), # Header-Textfarbe
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), pdf_architect.stylesheet.get("font_heading")), # Header-Schriftart
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#F0F0F0'), # Zellen-Hintergrund (Zebrastreifen)
            ('GRID', (0, 0), (-1, -1), 1, '#DDDDDD'), # Gitterlinien
            ('FONTNAME', (0, 1), (-1, -1), pdf_architect.stylesheet.get("font_main")), # Body-Schriftart
        ])
        table.setStyle(style)

        # Position der Tabelle auf der Seite bestimmen und zeichnen
        table.wrapOn(pdf_canvas, pdf_architect.stylesheet.width - 2*title_x, pdf_architect.stylesheet.height)
        table.drawOn(pdf_canvas, title_x, title_y - table._height - 1*cm)
        
# --- PDF_ARCHITECT KLASSE ---
class PDF_Architect:
    def __init__(self, stylesheet):
        self.stylesheet = stylesheet
    def generate_pdf(self, file_name, blocks):
        c = canvas.Canvas(file_name, pagesize=A4)
        page_number = 1
        for block in blocks:
            self.stylesheet.draw_static_elements(c, page_number)
            block.render(self, c)
            c.showPage()
            page_number += 1
        c.save()
        print(f"PDF-Architekt hat '{file_name}' mit {len(blocks)} modularen Blöcken erfolgreich konstruiert.")

class DashboardBlock(ContentBlock):
    """
    Ein fortschrittlicher Block zum Arrangieren von mehreren Kennzahlen (Widgets)
    auf einer einzigen Seite, ähnlich einem Dashboard.
    """
    def __init__(self, title, widgets):
        super().__init__(title)
        # Stellt sicher, dass widgets eine Liste von Dictionaries ist
        if not all(isinstance(w, dict) and 'label' in w and 'value' in w for w in widgets):
            raise ValueError("Widgets müssen eine Liste von Dictionaries sein, jedes mit 'label' und 'value'.")
        self.widgets = widgets

    def render(self, pdf_architect, pdf_canvas):
        # Seitentitel zeichnen
        pdf_canvas.setFont(pdf_architect.stylesheet.get("font_heading"), pdf_architect.stylesheet.get("font_size_title"))
        pdf_canvas.setFillColor(HexColor(pdf_architect.stylesheet.get("color_heading")))
        pdf_canvas.drawCentredString(pdf_architect.stylesheet.width / 2, pdf_architect.stylesheet.height - 3*cm, self.title)

        # Layout-Parameter für die Widgets
        num_widgets = len(self.widgets)
        num_cols = 2  # Wir definieren ein 2-spaltiges Layout
        num_rows = (num_widgets + num_cols - 1) // num_cols
        col_width = pdf_architect.stylesheet.width / (num_cols + 1)
        row_height = 10*cm
        
        start_x = pdf_architect.stylesheet.get("page_margin_x") + 1*cm
        start_y = pdf_architect.stylesheet.height - 6*cm

        # Widgets im Raster zeichnen
        for i, widget in enumerate(self.widgets):
            row = i // num_cols
            col = i % num_cols
            
            x = start_x + col * col_width
            y = start_y - row * row_height

            # Hintergrund-Box für das Widget zeichnen (optional, für besseres Design)
            pdf_canvas.setFillColor(HexColor("#F0F8FF")) # AliceBlue
            pdf_canvas.roundRect(x - 1*cm, y - 2*cm, 8*cm, 4*cm, 5, stroke=0, fill=1)

            # Widget-Wert zeichnen (groß)
            pdf_canvas.setFont(pdf_architect.stylesheet.get("font_heading"), 36)
            pdf_canvas.setFillColor(HexColor(pdf_architect.stylesheet.get("color_primary")))
            pdf_canvas.drawCentredString(x + 3*cm, y, widget['value'])

            # Widget-Label zeichnen (klein darunter)
            pdf_canvas.setFont(pdf_architect.stylesheet.get("font_main"), 12)
            pdf_canvas.setFillColor(HexColor(pdf_architect.stylesheet.get("color_text")))
            pdf_canvas.drawCentredString(x + 3*cm, y - 1*cm, widget['label'])


# --- BEISPIEL-CODE ZUM TESTEN ---
# Datei: pdf_architect.py
# Aktion: den if __name__ == '__main__': Block am Ende ersetzen

if __name__ == '__main__':
    tommatech_inspired_theme = {
        "theme_name": "TommaTech Inspired",
        "logo_path": None,
        "color_primary": "#005A9C",
        "company_details": "TommaTech GmbH | Zeppelinstraße 14 | 85748 Garching b. München"
    }
    
    my_style = Stylesheet(**tommatech_inspired_theme)
    pdf_builder = PDF_Architect(stylesheet=my_style)

    # --- Beispiel-Daten für die Tabelle ---
    wirtschaftlichkeit_data = [
        ['Kennzahl', 'Wert', 'Einheit'],
        ['Gesamtinvestition (Brutto)', '20.856,80', '€'],
        ['Amortisationszeit (ca.)', '16.9', 'Jahre'],
        ['Interne Zinsfuß (IRR, ca.)', '-11,2', '%'],
        ['Stromgestehungskosten (LCOE)', '0,338', '€/kWh']
    ]

    # --- Beispiel-Daten für das Diagramm ---
    sample_analysis_results = {
        'monthly_consumption_sim': [292, 292, 292, 292, 292, 292, 292, 292, 292, 292, 292, 292],
        'monthly_productions_sim': [263, 439, 702, 966, 1141, 1229, 1141, 1063, 790, 527, 351, 176]
    }
    sample_texts = { "month_names_short_list": "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez" }

    # --- Vom Nutzer ausgewählte Inhaltsblöcke ---
    user_selected_content = [
        TextBlock(
            title="Persönliche Zusammenfassung Ihrer PV-Anlage", 
            text_content="Sehr geehrter Kunde, basierend auf Ihren Angaben haben wir die folgende Analyse für Ihr Projekt erstellt. Diese Übersicht zeigt Ihnen die zentralen Kennzahlen und das Potenzial Ihrer zukünftigen Photovoltaikanlage."
        ),
        TableBlock(
            title="Wirtschaftlichkeit im Überblick",
            table_data=wirtschaftlichkeit_data,
            col_widths=[8*cm, 4*cm, 4*cm] # Optionale Spaltenbreiten
        ),
        ProductionConsumptionChartBlock(
            title="Ihre Energiebilanz im Jahresverlauf",
            analysis_results=sample_analysis_results,
            texts=sample_texts
        )
    ]

    # --- Beispiel-Daten für das Dashboard ---
    dashboard_widgets = [
        {'label': 'Unabhängigkeitsgrad', 'value': '54%'},
        {'label': 'Eigenverbrauch', 'value': '42%'},
        {'label': 'Jahresertrag', 'value': '8.251 kWh'},
        {'label': 'Anlagengröße', 'value': '8,4 kWp'}
    ]
    
    # --- Beispiel-Daten für die Tabelle ---
    wirtschaftlichkeit_data = [
        ['Kennzahl', 'Wert', 'Einheit'],
        ['Ersparnis (20J. mit Speicher)', '36.958,00', 'EUR*'],
        ['Ersparnis (20J. ohne Speicher)', '29.150,00', 'EUR*'],
    ]

    # --- Vom Nutzer ausgewählte Inhaltsblöcke ---
    user_selected_content = [
        DashboardBlock(
            title="KENNZAHLEN IHRES PV-SYSTEMS",
            widgets=dashboard_widgets
        ),
        TableBlock(
            title="Wirtschaftlichkeit im Überblick",
            table_data=wirtschaftlichkeit_data,
            col_widths=[8*cm, 4*cm, 4*cm]
        )
    ]

    pdf_builder.generate_pdf("Architekt_Mit_Dashboard_Angebot.pdf", user_selected_content)
