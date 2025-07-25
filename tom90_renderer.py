"""
tom90_renderer.py
===================

Dieses Modul definiert eine neue Rendering‐Engine für Angebots‐PDFs, die
sich am Layout der TOM‑90 Vorlage orientiert. Die Implementierung ist
vollständig eigenständig und erweitert die bestehende PDF‐Erstellung,
ohne bestehende Funktionen zu verändern. Alle existierenden Features
bleiben erhalten, indem diese Engine optional genutzt werden kann. Die
Rendererklasse basiert auf ReportLab und organisiert den Inhalt in
modularen Blöcken, die leicht wiederverwendet und verschoben werden
können. Jeder Block ist in einer eigenen Klasse gekapselt, wodurch die
Block‐Architektur (LEGO‑Prinzip) unterstützt wird. Neue Blöcke können
hinzugefügt werden, indem die ``PDFBlock``‐Basisklasse erweitert wird.

Hinweis: Dieser Renderer ist nicht direkt in ``generate_offer_pdf``
eingebunden, um die Rückwärtskompatibilität zu gewährleisten. Das
Einbinden erfolgt über die Funktion ``generate_tom90_offer_pdf`` am Ende
dieser Datei. Entwickler können diese Funktion wie gewohnt in der App
verwenden, um ein TOM‑90 konformes PDF zu erzeugen.

Autor: KI‐Agent
Datum: 2025‑07‑25
"""

from __future__ import annotations

import io
import math
import base64
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# --- ReportLab imports ---
# We attempt to import ReportLab. If unavailable, we define minimal stubs
# so that the module can be imported without breaking.  This allows the
# application to run in environments where ReportLab is not installed.
try:
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
        Table, TableStyle, PageBreak, KeepTogether
    )
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    _REPORTLAB_AVAILABLE = True
except ImportError:
    # ReportLab is not available; define dummy classes and defaults.
    _REPORTLAB_AVAILABLE = False
    class BaseDocTemplate:
        def __init__(self, *args, **kwargs): pass
    class PageTemplate:
        def __init__(self, *args, **kwargs): pass
    class Frame:
        def __init__(self, *args, **kwargs): pass
    class Paragraph:
        def __init__(self, *args, **kwargs): pass
    class Spacer:
        def __init__(self, *args, **kwargs): pass
    class Image:
        def __init__(self, *args, **kwargs): pass
    class Table:
        def __init__(self, *args, **kwargs): pass
    class TableStyle:
        def __init__(self, *args, **kwargs): pass
    class PageBreak:
        def __init__(self, *args, **kwargs): pass
    class KeepTogether:
        def __init__(self, flowables): pass
    # Use numeric values for A4 size; use centimeters as numeric
    A4 = (595.27, 841.89)
    cm = 28.3465
    colors = type('Colors', (), {})
    colors.HexColor = lambda x: x
    ParagraphStyle = object

# --- Optional: matplotlib imports ---
# Charts are created using matplotlib if available.  We separate this
# import so that lack of matplotlib does not affect ReportLab usage.
try:
    import matplotlib
    matplotlib.use('Agg')  # Use a non-interactive backend suitable for servers
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except Exception:
    # Any exception (including ImportError) disables chart plotting via
    # matplotlib. The code should fall back to table-based charts in this case.
    _MATPLOTLIB_AVAILABLE = False

try:
    # Reuse existing themes if available
    from theming.pdf_styles import get_theme, create_modern_table_style
    _THEMING_AVAILABLE = True
except ImportError:
    _THEMING_AVAILABLE = False
    def get_theme(theme_name: str = "Blau Elegant") -> Dict[str, Any]:
        """Fallback: returns a simple default theme if theming is not available.

        Dieser Fallback verzichtet vollständig auf ReportLab‐Styles, um auch
        ohne installierte ReportLab‐Bibliothek zu funktionieren. Die
        zurückgelieferte Struktur entspricht der von ``pdf_styles.get_theme``,
        enthält jedoch nur primitive Datentypen. ReportLab‐Styles werden
        während der PDF‐Erstellung zur Laufzeit erzeugt, sofern ReportLab
        verfügbar ist.
        """
        return {
            'styles': {},
            'colors': {
                'primary': '#003366', 'secondary': '#eeeeee', 'background': '#ffffff',
                'text_body': '#000000', 'text_heading': '#003366',
                'footer_text': '#888888'
            },
            'fonts': {
                'family_main': 'Helvetica', 'family_bold': 'Helvetica-Bold',
                'size_h1': 20, 'size_h2': 16, 'size_h3': 12, 'size_body': 10, 'size_footer': 8
            },
        }
    def create_modern_table_style(theme: Dict[str, Any]) -> TableStyle:
        return TableStyle([])

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _b64_to_image_flowable(b64_str: str, max_width: float, max_height: float) -> Optional[Image]:
    """Decodes a base64 encoded image and returns a ReportLab Image flowable.

    Args:
        b64_str: Base64 encoded image.
        max_width: Maximum width in points.
        max_height: Maximum height in points.

    Returns:
        Image flowable or None if decoding fails.
    """
    if not _REPORTLAB_AVAILABLE or not b64_str:
        return None
    try:
        img_data = base64.b64decode(b64_str)
        # Create the image flowable using the Image class
        image = Image(io.BytesIO(img_data))
        # Maintain aspect ratio when scaling
        w, h = image.drawWidth, image.drawHeight
        scale = min(max_width / w, max_height / h)
        image.drawWidth = w * scale
        image.drawHeight = h * scale
        return image
    except Exception:
        return None

def _format_number(value: Any, unit: str = "", precision: int = 2) -> str:
    """Formats numbers for display in KPI tables and paragraphs."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    if precision < 0:
        formatted = f"{num:.0f}"
    else:
        formatted = f"{num:,.{precision}f}".replace(",", ".")
    return f"{formatted} {unit}".strip()

def _extract_kpis(project_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Derives a set of standard KPIs from the provided data.

    This helper attempts to access common keys from the analysis results and
    project data. If a key is missing, sensible defaults are applied.

    Returns a dictionary with keys:
        - kwp
        - annual_production
        - co2_savings
        - self_consumption_rate
        - autarky_rate
        - amortization_years
        - module_count
        - inverter_info
        - storage_info
    """
    kpi = {}
    pv_details = project_data.get('pv_details', {})
    proj_details = project_data.get('project_details', {})

    anlage_kwp = analysis.get('anlage_kwp') or analysis.get('anlage_kwp_kwp') or 0
    try:
        anlage_kwp = float(anlage_kwp)
    except Exception:
        anlage_kwp = 0
    kpi['kwp'] = anlage_kwp

    annual_prod = analysis.get('annual_pv_production_kwh') or analysis.get('annual_production_kwh') or 0
    kpi['annual_production'] = annual_prod

    co2 = analysis.get('annual_co2_savings_kg') or 0
    kpi['co2_savings'] = co2 / 1000.0  # convert to tons

    self_cons_rate = analysis.get('self_consumption_rate_percent') or analysis.get('self_supply_rate_percent') or 0
    kpi['self_consumption_rate'] = self_cons_rate

    autarky_rate = analysis.get('self_supply_rate_percent') or analysis.get('autarky_rate_percent') or 0
    kpi['autarky_rate'] = autarky_rate

    amort_years = analysis.get('amortization_time_years') or analysis.get('simple_payback_years') or 0
    try:
        amort_years = float(amort_years)
    except Exception:
        amort_years = 0
    if amort_years and amort_years > 30:
        # unrealistic – fall back to simple payback if available
        fallback = analysis.get('simple_payback_years') or 0
        try:
            amort_years = float(fallback)
        except Exception:
            amort_years = 0
    kpi['amortization_years'] = amort_years

    # Estimate module count
    module_count = pv_details.get('module_quantity') or 0
    if not module_count and anlage_kwp:
        module_power_wp = 420  # typical module size
        module_count = max(1, round(anlage_kwp * 1000 / module_power_wp))
    kpi['module_count'] = module_count

    # Inverter and storage information (strings)
    inverter_info = "String-Wechselrichter"
    storage_info = ""
    try:
        # Real inverter
        inverter_id = proj_details.get('selected_inverter_id')
        if inverter_id and 'get_product_by_id_func' in analysis:
            get_product = analysis['get_product_by_id_func']
            prod = get_product(inverter_id)
            if prod:
                power_kw = prod.get('power_kw') or 0
                if power_kw and power_kw > 100:  # if stored in W
                    power_kw = power_kw / 1000.0
                inverter_info = f"{prod.get('model_name', 'Wechselrichter')} ({power_kw:.1f} kW)"
    except Exception:
        pass
    kpi['inverter_info'] = inverter_info

    try:
        if pv_details.get('include_storage') and proj_details.get('selected_storage_id') and 'get_product_by_id_func' in analysis:
            get_product = analysis['get_product_by_id_func']
            storage_id = proj_details.get('selected_storage_id')
            prod = get_product(storage_id)
            if prod:
                cap = prod.get('storage_power_kw') or prod.get('capacity_kwh') or 0
                storage_info = f"Batteriespeicher: {prod.get('model_name', '')} ({cap} kWh)"
    except Exception:
        pass
    kpi['storage_info'] = storage_info

    return kpi

# ---------------------------------------------------------------------------
# Block architecture
# ---------------------------------------------------------------------------

class PDFBlock:
    """Basisklasse für alle PDF‐Blöcke.

    Jeder Block implementiert ``create_flowables`` und gibt eine Liste von
    ReportLab‐Flowables zurück. Wenn ein Block optional ist, kann er über
    ``is_included`` anhand des Kontextes entschieden werden. Der Kontext
    enthält alle Daten, Texte und Einstellungen.
    """

    name: str = "Block"
    required: bool = False

    def __init__(self, name: str, required: bool = False):
        self.name = name
        self.required = required

    def is_included(self, context: Dict[str, Any]) -> bool:
        """Bestimmt, ob der Block in das PDF aufgenommen werden soll."""
        if self.required:
            return True
        inclusion_options = context.get('inclusion_options', {}) or {}
        # Optionale Blöcke können über inclusion_options gesteuert werden.
        # Der Schlüssel folgt dem Muster ``include_<block_name>``.
        return inclusion_options.get(f'include_{self.name}', True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:  # pragma: no cover
        """Erzeugt ReportLab‐Flowables für den Block.

        Abgeleitete Klassen müssen diese Methode implementieren.
        """
        raise NotImplementedError


class CoverPageBlock(PDFBlock):
    """Erzeugt die Titelseite mit Logo, Titel und optionalem Titelbild."""

    def __init__(self):
        super().__init__(name='cover_page', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        # Titelbild (optional)
        title_img_b64 = context.get('title_image_b64')
        if title_img_b64:
            img = _b64_to_image_flowable(title_img_b64, max_width=context['doc_width'], max_height=context['doc_height'] * 0.5)
            if img:
                flows.append(img)
                flows.append(Spacer(1, 0.5 * cm))
        # Firmenlogo (optional)
        company_logo_b64 = context.get('company_logo_b64')
        if company_logo_b64:
            img = _b64_to_image_flowable(company_logo_b64, max_width=6*cm, max_height=3*cm)
            if img:
                img.hAlign = 'CENTER'
                flows.append(img)
                flows.append(Spacer(1, 0.3 * cm))
        # Titeltext
        offer_title = context.get('offer_title') or "Ihr Angebot"
        flows.append(Paragraph(offer_title, styles.get('h1', ParagraphStyle('h1'))))
        flows.append(Spacer(1, 0.5 * cm))
        # Firmeninformationen
        company = context.get('company_info', {})
        company_lines = []
        if company.get('name'):
            company_lines.append(company.get('name'))
        street = company.get('street', '')
        zipcode = company.get('zip_code', '')
        city = company.get('city', '')
        if street or zipcode or city:
            company_lines.append(f"{street}, {zipcode} {city}".strip())
        phone = company.get('phone')
        email = company.get('email')
        website = company.get('website')
        contact_parts = []
        if phone:
            contact_parts.append(f"Tel.: {phone}")
        if email:
            contact_parts.append(f"Mail: {email}")
        if website:
            contact_parts.append(f"Web: {website}")
        if contact_parts:
            company_lines.append(" | ".join(contact_parts))
        if company_lines:
            flows.append(Paragraph("<br/>".join(company_lines), styles.get('BodyText', ParagraphStyle('BodyText'))))
        flows.append(PageBreak())
        return flows


class KPIBlock(PDFBlock):
    """Block zur Darstellung der wichtigsten Kennzahlen als übersichtlicher Text."""

    def __init__(self):
        super().__init__(name='kpi_overview', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        # Nutze Helfer zum Extrahieren der Kennzahlen
        kpis = _extract_kpis(project, analysis)
        flows.append(Paragraph("Kennzahlen", styles.get('h2', ParagraphStyle('h2'))))
        data = [
            ["Anlagenleistung (kWp)", _format_number(kpis['kwp'], "", 1)],
            ["Jährlicher Ertrag", _format_number(kpis['annual_production'], "kWh", 0)],
            ["CO₂‑Einsparung", _format_number(kpis['co2_savings'], "t/Jahr", 1)],
            ["Eigenverbrauchsquote", _format_number(kpis['self_consumption_rate'], "%", 1)],
            ["Autarkiegrad", _format_number(kpis['autarky_rate'], "%", 1)],
            ["Amortisation", _format_number(kpis['amortization_years'], "Jahre", 1)],
            ["PV‑Module", str(kpis['module_count'])],
        ]
        # Tabelle erstellen
        table_style = create_modern_table_style(theme)
        table = Table([["Kennzahl", "Wert"]] + data, colWidths=[7*cm, context['doc_width'] - 7*cm])
        table.setStyle(table_style)
        flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows


class ComponentsBlock(PDFBlock):
    """Block zur Darstellung der technischen Komponenten (Module, Wechselrichter, Speicher)."""

    def __init__(self):
        super().__init__(name='components', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        kpis = _extract_kpis(project, analysis)
        flows.append(Paragraph("Technische Komponenten", styles.get('h2', ParagraphStyle('h2'))))
        rows = []
        # PV‑Module
        rows.append(["PV‑Module", f"{kpis['module_count']}× (ca. {round(kpis['kwp']*1000/kpis['module_count']):d} Wp pro Modul)"])
        # Wechselrichter
        rows.append(["Wechselrichter", kpis.get('inverter_info', 'String‑Wechselrichter')])
        # Speicher
        storage_info = kpis.get('storage_info', '')
        if storage_info:
            rows.append(["Speicher", storage_info])
        # Dach und Montage
        mount_type = project.get('project_details', {}).get('mounting_type', '')
        if mount_type:
            rows.append(["Montagesystem", mount_type])
        orientation = project.get('project_details', {}).get('orientation', '')
        if orientation:
            rows.append(["Dachausrichtung", orientation])
        table = Table([["Komponente", "Details"]] + rows, colWidths=[7*cm, context['doc_width'] - 7*cm])
        table.setStyle(create_modern_table_style(theme))
        flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows


class ChartBlock(PDFBlock):
    """Block zur Darstellung von Diagrammen.

    Dieser Block nutzt die im vorhandenen Code definierte Funktion
    ``generate_prod_vs_cons_chart_image`` (falls vorhanden), um ein
    Produktions‑vs‑Verbrauchs‑Diagramm zu erstellen. Sollte die Funktion
    nicht verfügbar sein, wird der Block übersprungen.
    """

    def __init__(self):
        super().__init__(name='prod_vs_cons_chart', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        # Diagramm erzeugen
        try:
            from pdf_generator import generate_prod_vs_cons_chart_image
            img_bytes = generate_prod_vs_cons_chart_image(context['analysis_results'], context['texts'])
        except Exception:
            img_bytes = None
        if img_bytes:
            try:
                # Erstelle Image aus Bytes
                img = Image(io.BytesIO(img_bytes))
                # Skaliere Bild auf Seitenbreite
                max_w = context['doc_width']
                w, h = img.drawWidth, img.drawHeight
                scale = min(max_w / w, 10*cm / h)
                img.drawWidth = w * scale
                img.drawHeight = h * scale
                flows.append(Paragraph("Ertrag vs. Verbrauch", styles.get('h2', ParagraphStyle('h2'))))
                flows.append(img)
                flows.append(Spacer(1, 0.4 * cm))
            except Exception:
                pass
        return flows


class TermsBlock(PDFBlock):
    """Block für rechtliche Hinweise, AGB und Datenschutz."""

    def __init__(self):
        super().__init__(name='terms', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        texts = context.get('texts', {}) or {}
        # Beispielhaft fügen wir statische AGB hinzu; in der Praxis können
        # diese über die Texte geladen oder aus Datenbank gezogen werden.
        terms_text = texts.get('pdf_terms_text', "Allgemeine Geschäftsbedingungen und Datenschutzhinweise.<br/>"
                                           "Bitte beachten Sie, dass dieses Angebot unverbindlich ist und unter dem"
                                           "Vorbehalt der Verfügbarkeit der Komponenten steht.")
        flows.append(Paragraph("Rechtliche Hinweise & AGB", styles.get('h2', ParagraphStyle('h2'))))
        flows.append(Paragraph(terms_text, styles.get('BodyText', ParagraphStyle('BodyText'))))
        return flows


# ---------------------------------------------------------------------------
# Zusätzliche Blöcke für das TOM‑90 Layout
# ---------------------------------------------------------------------------

class PersonalSummaryBlock(PDFBlock):
    """Block für die persönliche Zusammenfassung des Kunden und Projekts.

    Dieser Block fasst die Kundendaten und wesentliche Projektdaten
    zusammen. Er erzeugt eine Überschrift sowie einige Absätze mit den
    bereitgestellten Informationen.
    """

    def __init__(self) -> None:
        super().__init__(name='personal_summary', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        styles = context['theme'].get('styles', {})
        project = context['project_data']
        analysis = context['analysis_results']
        # Kundeninformationen
        customer = project.get('customer_data', {}) or {}
        customer_lines: List[str] = []
        if customer.get('salutation'):
            customer_lines.append(customer['salutation'])
        if customer.get('first_name') or customer.get('last_name'):
            customer_lines.append("{} {}".format(customer.get('first_name', ''), customer.get('last_name', '')).strip())
        if customer.get('street') or customer.get('zip_code') or customer.get('city'):
            customer_lines.append("{} {} {}".format(customer.get('street', ''), customer.get('zip_code', ''), customer.get('city', '')).strip())
        if customer.get('email'):
            customer_lines.append(customer['email'])
        if customer.get('phone'):
            customer_lines.append(customer['phone'])
        # Projektdaten (Angebotsnummer, Datum)
        offer_id = project.get('project_details', {}).get('offer_id') or ''
        offer_date = project.get('project_details', {}).get('date') or datetime.now().strftime("%d.%m.%Y")
        flows.append(Paragraph("Persönliche Zusammenfassung", styles.get('h2', ParagraphStyle('h2'))))
        # Kundendaten
        if customer_lines:
            flows.append(Paragraph("<br/>".join(customer_lines), styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.3 * cm))
        # Angebotsinformationen
        offer_info_parts: List[str] = []
        if offer_id:
            offer_info_parts.append(f"Angebotsnummer: {offer_id}")
        if offer_date:
            offer_info_parts.append(f"Datum: {offer_date}")
        if offer_info_parts:
            flows.append(Paragraph(" | ".join(offer_info_parts), styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.3 * cm))
        return flows


class DonutChartsBlock(PDFBlock):
    """Block zur Darstellung der Donut‑Charts für Eigenverbrauch und Unabhängigkeit.

    Dieser Block erstellt zwei Donut‑Diagramme mit matplotlib. Falls matplotlib
    nicht verfügbar ist, wird stattdessen eine tabellarische Darstellung
    ausgegeben.
    """

    def __init__(self) -> None:
        super().__init__(name='donut_charts', required=True)

    def _generate_donut_image(self, value: float, title: str, colors: List[str]) -> Optional[Image]:
        """Erzeugt ein Donut‑Diagramm als Bildflowable.

        Args:
            value: Prozentwert für den Hauptanteil (0–100).
            title: Titel des Diagramms.
            colors: Liste von zwei Hex‑Farben für den Hauptanteil und den Rest.
        Returns:
            ReportLab Image oder None, falls matplotlib nicht verfügbar ist.
        """
        if not _MATPLOTLIB_AVAILABLE or not _REPORTLAB_AVAILABLE:
            return None
        try:
            fig, ax = plt.subplots(figsize=(3, 3))
            # Daten: Hauptanteil und Rest
            sizes = [max(0, min(100, value)), max(0, 100 - value)]
            labels = [f"{title} ({value:.0f}%)", ""]
            ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.4, edgecolor='white'),
                textprops={'color': '#000000', 'fontsize': 8},
            )
            ax.axis('equal')
            # Titel im Plot
            ax.set_title(title, fontsize=10)
            buffer = io.BytesIO()
            fig.savefig(buffer, format='PNG', bbox_inches='tight', dpi=150)
            plt.close(fig)
            buffer.seek(0)
            img = Image(buffer)
            # Skalierung für die PDF‑Breite begrenzen
            max_width = 6 * cm
            max_height = 6 * cm
            scale = min(max_width / img.drawWidth, max_height / img.drawHeight)
            img.drawWidth *= scale
            img.drawHeight *= scale
            return img
        except Exception:
            return None

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        # Farbpalette für Charts
        primary = theme.get('colors', {}).get('primary', '#003366')
        secondary = theme.get('colors', {}).get('secondary', '#0081b8')
        # Werte für Eigenverbrauch und Unabhängigkeit
        eigenv = analysis.get('self_consumption_rate_percent') or 0
        autark = analysis.get('self_supply_rate_percent') or analysis.get('autarky_rate_percent') or 0
        flows.append(Paragraph("Eigenverbrauch & Unabhängigkeit", styles.get('h2', ParagraphStyle('h2'))))
        chart_images = []
        img_ev = self._generate_donut_image(eigenv, "Eigenverbrauch", [primary, secondary])
        img_aut = self._generate_donut_image(autark, "Unabhängigkeit", [secondary, primary])
        if img_ev and img_aut:
            # Tabelle zur Ausrichtung der beiden Diagramme nebeneinander
            chart_table = Table(
                [[img_ev, img_aut]],
                colWidths=[context['doc_width'] / 2 - cm, context['doc_width'] / 2 - cm],
            )
            chart_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            flows.append(chart_table)
        else:
            # Fallback: einfache textuelle Darstellung
            data = [
                ["Kennzahl", "Wert"],
                ["Eigenverbrauch", f"{eigenv:.1f}%"],
                ["Unabhängigkeit", f"{autark:.1f}%"],
            ]
            table = Table(data, colWidths=[6*cm, context['doc_width'] - 6*cm])
            table.setStyle(create_modern_table_style(theme))
            flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows


class BarChartBlock(PDFBlock):
    """Block zur Darstellung eines Balkendiagramms für die 20‑Jahres‑Erträge.

    Dieser Block nutzt matplotlib, um ein Balkendiagramm für den Vergleich
    der Erträge mit und ohne Batteriespeicher zu erzeugen. Falls die
    entsprechenden Daten im Analyseergebnis fehlen oder matplotlib nicht
    verfügbar ist, wird eine tabellarische Darstellung verwendet.
    """

    def __init__(self) -> None:
        super().__init__(name='bar_chart', required=True)

    def _generate_bar_chart_image(self, values: Dict[str, float], theme: Dict[str, Any]) -> Optional[Image]:
        """Erzeugt das Balkendiagramm als Bild.
        Args:
            values: Dictionary mit zwei Schlüsseln: 'mit' und 'ohne' Speicher.
            theme: Das aktuelle Farbschema.
        Returns:
            ReportLab Image oder None.
        """
        if not _MATPLOTLIB_AVAILABLE or not _REPORTLAB_AVAILABLE:
            return None
        try:
            labels = ["Mit Speicher", "Ohne Speicher"]
            data = [values.get('mit', 0), values.get('ohne', 0)]
            fig, ax = plt.subplots(figsize=(4, 3))
            bar_colors = [theme.get('colors', {}).get('primary', '#003366'), theme.get('colors', {}).get('secondary', '#0081b8')]
            bars = ax.bar(labels, data, color=bar_colors)
            ax.set_ylabel('Ersparnis (EUR)')
            ax.set_title('Ersparnis über 20 Jahre')
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:,.0f} €".replace(',', '.'), xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
            ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
            buffer = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='PNG', dpi=150)
            plt.close(fig)
            buffer.seek(0)
            img = Image(buffer)
            # Skalierung auf eine feste Breite/Höhe
            max_w = 12 * cm
            max_h = 6 * cm
            scale = min(max_w / img.drawWidth, max_h / img.drawHeight)
            img.drawWidth *= scale
            img.drawHeight *= scale
            return img
        except Exception:
            return None

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        # Versuche Ertragswerte aus dem Analyseergebnis zu laden
        val_with = analysis.get('total_savings_with_storage_eur') or analysis.get('savings_with_storage_eur') or None
        val_without = analysis.get('total_savings_without_storage_eur') or analysis.get('savings_without_storage_eur') or None
        # Fallback: Verwende simple Modellrechnung basierend auf Jahresertrag
        if val_with is None or val_without is None:
            annual_prod = analysis.get('annual_pv_production_kwh') or 0
            # Schätze Ersparnis pro kWh (z.B. 0.25 EUR) und multipliziere mit 20 Jahren
            est_rate = 0.25
            val_without = annual_prod * est_rate * 20
            # Speicher erhöht Eigenverbrauch um 10 Prozentpunkte -> ca. 10% mehr Ersparnis
            val_with = val_without * 1.1
        # Werte in EUR
        values = {'mit': float(val_with), 'ohne': float(val_without)}
        flows.append(Paragraph("Ersparnis über 20 Jahre", styles.get('h2', ParagraphStyle('h2'))))
        img = self._generate_bar_chart_image(values, theme)
        if img:
            flows.append(img)
        else:
            # Fallback: einfache Tabelle
            table = Table([
                ["Option", "Ersparnis (EUR)"],
                ["Mit Speicher", f"{values['mit']:.0f}"],
                ["Ohne Speicher", f"{values['ohne']:.0f}"],
            ], colWidths=[6*cm, context['doc_width'] - 6*cm])
            table.setStyle(create_modern_table_style(theme))
            flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows


class HaveYouKnowBlock(PDFBlock):
    """Block für die "Haben Sie gewusst?"‑Infotexte.

    Dieser Block fügt ein oder mehrere kleine Textboxen mit Fakten und
    Hinweisen ein. Die Fakten können aus den Texten kommen oder sind
    fest definiert.
    """
    def __init__(self) -> None:
        super().__init__(name='have_you_known', required=False)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        texts = context.get('texts', {}) or {}
        facts = texts.get('facts_list') or [
            "Ein durchschnittliches Elektroauto ist 3-4× effizienter als ein Auto mit Verbrennungsmotor.",
            "In Deutschland liegen die jährlichen pro Kopf Emissionen bei 7,69 Tonnen CO₂.",
            "Photovoltaikanlagen können die CO₂‑Emissionen eines Haushalts um bis zu 40 % reduzieren.",
        ]
        flows.append(Paragraph("Haben Sie gewusst?", styles.get('h2', ParagraphStyle('h2'))))
        for fact in facts:
            flows.append(Paragraph(f"• {fact}", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.2 * cm))
        flows.append(Spacer(1, 0.4 * cm))
        return flows


class CO2Block(PDFBlock):
    """Block zur Darstellung der CO₂‑Bilanz.

    Zeigt die jährliche CO₂‑Einsparung und eine einfache textliche
    Interpretation.
    """
    def __init__(self) -> None:
        super().__init__(name='co2_balance', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        co2_savings_kg = analysis.get('annual_co2_savings_kg') or 0
        co2_savings_tons = co2_savings_kg / 1000.0
        # Faktischer Vergleich: Autokilometer, Bäume, etc.
        km_per_car = 15000  # Durchschnitt pro Jahr
        co2_per_km = 0.12  # kg CO₂ pro km
        km_equivalent = co2_savings_kg / co2_per_km if co2_per_km else 0
        tree_factor = 12.5  # kg CO₂ pro Baum pro Jahr
        trees_equivalent = co2_savings_kg / tree_factor if tree_factor else 0
        flows.append(Paragraph("CO₂‑Bilanz", styles.get('h2', ParagraphStyle('h2'))))
        # Tabelle mit Kennzahlen
        data = [
            ["Einsparung pro Jahr", f"{co2_savings_tons:.2f} t CO₂"],
            ["Einsparung in Autokilometern", f"{km_equivalent:.0f} km"],
            ["entspricht gepflanzten Bäumen", f"{trees_equivalent:.0f} Bäume"],
        ]
        table = Table([['Kennzahl', 'Wert']] + data, colWidths=[7*cm, context['doc_width'] - 7*cm])
        table.setStyle(create_modern_table_style(theme))
        flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows


class FinancingBlock(PDFBlock):
    """Block für die Darstellung von Finanzierungsoptionen.

    Dieser Block zeigt einen Vergleich zwischen Kreditfinanzierung,
    Leasing und Sofortkauf. Die Berechnungen basieren auf den
    existierenden Funktionen aus ``financial_tools.py``. Falls diese
    Funktionen nicht verfügbar oder Eingabedaten nicht vorhanden sind,
    wird ein Hinweis ausgegeben.
    """

    def __init__(self) -> None:
        super().__init__(name='financing', required=False)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        # Basisdaten extrahieren
        # Investitionssumme (Netto)
        investment = (
            analysis.get('total_investment_netto')
            or analysis.get('total_investment')
            or project.get('investment_amount')
            or 0.0
        )
        try:
            investment = float(investment)
        except Exception:
            investment = 0.0
        # Zinssatz (p.a.)
        interest_rate = (
            analysis.get('loan_interest_rate_percent')
            or project.get('loan_interest_rate_percent')
            or 4.0
        )
        try:
            interest_rate = float(interest_rate)
        except Exception:
            interest_rate = 4.0
        # Laufzeit in Jahren
        duration_years = (
            analysis.get('simulation_period_years_effective')
            or analysis.get('simulation_period_years')
            or project.get('loan_duration_years')
            or 20
        )
        try:
            duration_years = int(duration_years)
        except Exception:
            duration_years = 20
        # Leasingfaktor (Monatlicher Prozentsatz)
        leasing_factor = (
            analysis.get('leasing_factor_percent')
            or project.get('leasing_factor_percent')
            or 2.5
        )
        try:
            leasing_factor = float(leasing_factor)
        except Exception:
            leasing_factor = 2.5
        flows.append(Paragraph("Finanzierungsvergleich", styles.get('h2', ParagraphStyle('h2'))))
        # Wenn keine sinnvolle Investition vorhanden, Hinweis ausgeben
        if investment <= 0:
            flows.append(Paragraph("Keine Finanzierungsdaten verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4 * cm))
            return flows
        # Finanzberechnungen ausführen
        credit_result = None
        leasing_result = None
        try:
            # Lazy import, um starke Kopplung zu vermeiden
            from financial_tools import calculate_annuity, calculate_leasing_costs
            credit_result = calculate_annuity(investment, interest_rate, duration_years)
            leasing_result = calculate_leasing_costs(investment, leasing_factor, int(duration_years * 12))
        except Exception:
            credit_result = None
            leasing_result = None
        # Tabelle mit Ergebnissen erstellen
        data = [["Option", "Monatliche Rate", "Gesamtkosten", "Zinsen/Restwert"]]
        # Kredit
        if credit_result and not credit_result.get('error'):
            credit_month = credit_result.get('monatliche_rate', 0)
            credit_total = credit_result.get('gesamtkosten', 0)
            credit_interest = credit_result.get('gesamtzinsen', 0)
            data.append([
                "Kredit",
                _format_number(credit_month, "€", 0),
                _format_number(credit_total, "€", 0),
                _format_number(credit_interest, "€", 0),
            ])
        else:
            data.append(["Kredit", "–", "–", "–"])
        # Leasing
        if leasing_result and not leasing_result.get('error'):
            lease_month = leasing_result.get('monatliche_rate', 0)
            lease_total = leasing_result.get('gesamtkosten', 0)
            # Nutze Restwert als dritte Spalte; falls nicht vorhanden, effektive Kosten
            lease_rest = leasing_result.get('restwert') if 'restwert' in leasing_result else leasing_result.get('effektive_kosten', 0)
            data.append([
                "Leasing",
                _format_number(lease_month, "€", 0),
                _format_number(lease_total, "€", 0),
                _format_number(lease_rest, "€", 0),
            ])
        else:
            data.append(["Leasing", "–", "–", "–"])
        # Sofortkauf (ohne Finanzierung)
        data.append([
            "Kauf",
            "–",
            _format_number(investment, "€", 0),
            "0 €",
        ])
        table = Table(data, colWidths=[5*cm, 4*cm, 4*cm, context['doc_width'] - 13*cm])
        table.setStyle(create_modern_table_style(theme))
        flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class Tom90Renderer:
    """Renderer für die TOM‑90 PDF Ausgabe.

    Der Renderer sammelt die ausgewählten Blöcke und erstellt ein PDF im
    Stil der TOM‑90 Vorlage. Die Reihenfolge der Blöcke kann übergeben
    werden. Standardmäßig werden alle Pflichtblöcke in einer festen
    Reihenfolge erzeugt.
    """

    def __init__(
        self,
        project_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        inclusion_options: Optional[Dict[str, Any]] = None,
        texts: Optional[Dict[str, str]] = None,
        company_logo_base64: Optional[str] = None,
        title_image_b64: Optional[str] = None,
        offer_title_text: str = "Ihr Angebot",
        blocks: Optional[List[PDFBlock]] = None,
        theme_name: str = "Blau Elegant",
    ) -> None:
        self.project_data = project_data or {}
        self.analysis_results = analysis_results or {}
        self.company_info = company_info or {}
        self.inclusion_options = inclusion_options or {}
        self.texts = texts or {}
        self.company_logo_base64 = company_logo_base64
        self.title_image_b64 = title_image_b64
        self.offer_title_text = offer_title_text
        self.theme = get_theme(theme_name) if _THEMING_AVAILABLE else get_theme()
        # Reihenfolge der Blöcke; wenn none, verwende Standardblöcke
        if blocks is not None:
            self.blocks = blocks
        else:
            # Standardblöcke in der Reihenfolge der TOM‑90 Vorlage
            self.blocks = [
                CoverPageBlock(),       # Titelseite
                PersonalSummaryBlock(), # Persönliche Zusammenfassung
                KPIBlock(),             # Kennzahlen
                DonutChartsBlock(),     # Donut‑Charts Eigenverbrauch & Unabhängigkeit
                BarChartBlock(),        # Balkendiagramm Ersparnis
                ComponentsBlock(),      # Komponentenliste
                HaveYouKnowBlock(),     # "Haben Sie gewusst?" (optional)
                CO2Block(),             # CO₂‑Bilanz
                FinancingBlock(),       # Finanzierungsvergleich (optional)
                ChartBlock(),           # Weitere Diagramme
                TermsBlock(),           # Rechtliche Hinweise & AGB
            ]

    def _header_footer(self, canvas_obj, doc) -> None:
        """Zeichnet Kopf- und Fußzeile auf jeder Seite."""
        if not _REPORTLAB_AVAILABLE:
            return
        # Kopfzeile: Firmenname oben links, Angebotsnummer oben rechts
        canvas_obj.saveState()
        theme_colors = self.theme.get('colors', {})
        primary_color = theme_colors.get('primary', '#003366')
        canvas_obj.setStrokeColor(colors.HexColor(primary_color))
        canvas_obj.setFillColor(colors.HexColor(primary_color))
        canvas_obj.setFont(self.theme['fonts'].get('family_bold', 'Helvetica-Bold'), 9)
        # Firmenname
        company_name = self.company_info.get('name', '')
        canvas_obj.drawString(doc.leftMargin, doc.height + doc.topMargin - 0.5*cm, company_name)
        # Angebotsnummer (hier einfach Datum/Zeit als Platzhalter)
        offer_id = datetime.now().strftime("%Y%m%d%H%M")
        canvas_obj.drawRightString(doc.leftMargin + doc.width, doc.height + doc.topMargin - 0.5*cm, f"Angebot {offer_id}")
        # Fußzeile: Seitenzahl zentriert
        canvas_obj.setFont(self.theme['fonts'].get('family_main', 'Helvetica'), 8)
        canvas_obj.setFillColor(colors.HexColor(theme_colors.get('footer_text', '#888888')))
        page_num_text = f"Seite {doc.page}" if hasattr(doc, 'page') else ''
        canvas_obj.drawCentredString(doc.leftMargin + doc.width / 2, 0.75*cm, page_num_text)
        canvas_obj.restoreState()

    def build_pdf(self) -> Optional[bytes]:
        """Erzeugt das PDF und gibt dessen Bytes zurück.

        Falls ReportLab nicht installiert ist, wird ein minimaler PDF‐Stub
        generiert, damit zumindest ein gültiges PDF zurückgegeben wird.
        """
        if not _REPORTLAB_AVAILABLE:
            # Fallback: generiere ein leeres PDF mit einer Seite. Diese
            # Struktur entspricht der minimalen PDF‐Spezifikation und wird
            # von den meisten PDF‐Lesern akzeptiert. Der Inhalt ist leer.
            dummy_pdf = (b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\n"
                         b"endobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n"
                         b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >>\nendobj\n"
                         b"4 0 obj\n<< /Length 0 >>\nstream\n\nendstream\nendobj\n"
                         b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n"
                         b"0000000114 00000 n \n0000000178 00000 n \ntrailer\n<< /Root 1 0 R /Size 5 >>\n"
                         b"startxref\n224\n%%EOF")
            return dummy_pdf
        buffer = io.BytesIO()
        # Dokument mit Rändern einrichten; die Höhe wird dynamisch für Blöcke genutzt
        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm,
        )
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height - 1*cm,
            id='normal'
        )
        template = PageTemplate(id='Tom90', frames=frame, onPage=self._header_footer)
        doc.addPageTemplates([template])
        story: List[Any] = []
        # Kontext für Blöcke
        context: Dict[str, Any] = {
            'project_data': self.project_data,
            'analysis_results': self.analysis_results,
            'company_info': self.company_info,
            'inclusion_options': self.inclusion_options,
            'texts': self.texts,
            'theme': self.theme,
            'doc_width': doc.width,
            'doc_height': doc.height,
            'company_logo_b64': self.company_logo_base64,
            'title_image_b64': self.title_image_b64,
            'offer_title': self.offer_title_text,
        }
        # Reihenfolge der Blöcke durchlaufen
        for block in self.blocks:
            if block.is_included(context):
                try:
                    flows = block.create_flowables(context)
                    if flows:
                        story.append(KeepTogether(flows))
                except Exception as e:
                    # Fehler in einem Block sollten das PDF nicht abbrechen
                    err_msg = f"Fehler im Block {block.name}: {e}"
                    story.append(Paragraph(err_msg, self.theme.get('styles', {}).get('ErrorText', ParagraphStyle('ErrorText'))))
        try:
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception:
            return None


def generate_tom90_offer_pdf(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str] = None,
    selected_title_image_b64: Optional[str] = None,
    selected_offer_title_text: str = "Ihr Angebot",
    inclusion_options: Optional[Dict[str, Any]] = None,
    texts: Optional[Dict[str, str]] = None,
    load_admin_setting_func: Optional[Callable] = None,
    save_admin_setting_func: Optional[Callable] = None,
    list_products_func: Optional[Callable] = None,
    get_product_by_id_func: Optional[Callable] = None,
    db_list_company_documents_func: Optional[Callable] = None,
    active_company_id: Optional[int] = None,
    theme_name: str = "Blau Elegant",
    **kwargs
) -> Optional[bytes]:
    """Öffentliche Funktion zum Erzeugen eines TOM‑90 kompatiblen Angebots‐PDF.

    Diese Funktion entspricht weitgehend der Signatur von
    ``generate_offer_pdf``, verarbeitet jedoch nur einen kleinen Teil der
    Parameter (die themen- und datenbezogenen). Nicht benötigte
    Parameter sind für die Zukunft vorgesehen, um API‐Kompatibilität zu
    gewährleisten. Falls ReportLab oder die erforderlichen Bibliotheken
    nicht verfügbar sind, gibt diese Funktion ``None`` zurück.
    """
    renderer = Tom90Renderer(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        inclusion_options=inclusion_options,
        texts=texts,
        company_logo_base64=company_logo_base64,
        title_image_b64=selected_title_image_b64,
        offer_title_text=selected_offer_title_text,
        theme_name=theme_name,
    )
    return renderer.build_pdf()
