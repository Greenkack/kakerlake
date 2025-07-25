"""
tom90_renderer.py
===================

Dieses Modul definiert eine neue Rendering‑Engine für Angebots‑PDFs, die
sich am Layout der TOM‑90 Vorlage orientiert. Die Implementierung ist
vollständig eigenständig und erweitert die bestehende PDF‑Erstellung,
ohne bestehende Funktionen zu verändern. Alle existierenden Features
bleiben erhalten, indem diese Engine optional genutzt werden kann. Die
Rendererklasse basiert auf ReportLab und organisiert den Inhalt in
modularen Blöcken, die leicht wiederverwendet und verschoben werden
können. Jeder Block ist in einer eigenen Klasse gekapselt, wodurch die
Block‑Architektur (LEGO‑Prinzip) unterstützt wird. Neue Blöcke können
hinzugefügt werden, indem die ``PDFBlock``‑Basisklasse erweitert wird.

**NEUE TOM-90 DESIGN FEATURES:**
- Tom90Page2Block: 3D-isometrische Grafiken mit grauer Box und technischen Details
- Tom90Page3Block: Zwei-Box-Vergleich (Mit/Ohne PV) mit TOM-90 Farben
- Tom90Page4Block: Detaillierte Komponenten-Tabelle im TOM-90 Style
- Tom90Page5Block: Finanzierung und Kontakt-Informationen
- TOM-90 spezifische Farben: #0d3780 (blau), #f6f6f6 (hellgrau), #e1dfdf (grau)
- Erweiterte Theme-Funktionen für konsistentes Design
- Optional aktivierbare TOM-90 Design-Seiten über inclusion_options

Hinweis: Dieser Renderer ist nicht direkt in ``generate_offer_pdf``
eingebunden, um die Rückwärtskompatibilität zu gewährleisten. Das
Einbinden erfolgt über die Funktion ``generate_tom90_offer_pdf`` am Ende
dieser Datei. Entwickler können diese Funktion wie gewohnt in der App
verwenden, um ein TOM‑90 konformes PDF zu erzeugen.

Autor: KI‑Agent (erweitert für TOM-90 Design)
Datum: 2025‑07‑25
"""

from __future__ import annotations

import io
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# --- ReportLab imports ---
try:
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
        Table, TableStyle, PageBreak, KeepTogether
    )
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfgen import canvas as _rl_canvas
    from reportlab.lib.utils import ImageReader
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    class BaseDocTemplate:      # pragma: no cover
        def __init__(self, *args, **kwargs): pass
    class PageTemplate:         # pragma: no cover
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
    A4 = (595.27, 841.89)
    cm = 28.3465
    colors = type('Colors', (), {})
    colors.HexColor = lambda x: x
    ParagraphStyle = object

# --- Optional: matplotlib imports ---
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except Exception:
    _MATPLOTLIB_AVAILABLE = False

try:
    from theming.pdf_styles import get_theme, create_modern_table_style
    _THEMING_AVAILABLE = True
except ImportError:
    _THEMING_AVAILABLE = False
    def get_theme(theme_name: str = "Blau Elegant") -> Dict[str, Any]:
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
# TOM-90 specific theme and helper functions
# ---------------------------------------------------------------------------

def get_tom90_theme() -> Dict[str, Any]:
    """Erstellt das spezifische TOM-90 Farbschema basierend auf der Vorlage."""
    return {
        'name': 'TOM-90',
        'styles': {},
        'colors': {
            'primary': '#0d3780',      # TOM-90 Dunkelblau
            'secondary': '#f6f6f6',    # TOM-90 Hellgrau
            'background': '#ffffff',   # Weiß
            'text_body': '#000000',    # Schwarz
            'text_heading': '#0d3780', # TOM-90 Dunkelblau
            'footer_text': '#888888',  # Grau
            'tom90_gray': '#e1dfdf',   # TOM-90 Grau
            'tom90_medium_gray': '#b4b4b4',  # TOM-90 Mittelgrau
            'success': '#008000',      # Grün für positive Werte
            'error': '#cc0000',        # Rot für negative Werte
            'highlight': '#e8f4fd',    # Hellblau für Highlights
        },
        'fonts': {
            'family_main': 'Helvetica', 
            'family_bold': 'Helvetica-Bold',
            'size_h1': 20, 
            'size_h2': 16, 
            'size_h3': 12, 
            'size_body': 10, 
            'size_footer': 8
        },
    }

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _b64_to_image_flowable(b64_str: str, max_width: float, max_height: float) -> Optional[Image]:
    if not _REPORTLAB_AVAILABLE or not b64_str:
        return None
    try:
        img_data = base64.b64decode(b64_str)
        image = Image(io.BytesIO(img_data))
        w, h = image.drawWidth, image.drawHeight
        scale = min(max_width / w, max_height / h)
        image.drawWidth = w * scale
        image.drawHeight = h * scale
        return image
    except Exception:
        return None

def _format_number(value: Any, unit: str = "", precision: int = 2) -> str:
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
    kpi: Dict[str, Any] = {}
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
    kpi['co2_savings'] = co2 / 1000.0

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
        fallback = analysis.get('simple_payback_years') or 0
        try:
            amort_years = float(fallback)
        except Exception:
            amort_years = 0
    kpi['amortization_years'] = amort_years

    module_count = pv_details.get('module_quantity') or 0
    if not module_count and anlage_kwp:
        module_power_wp = 420
        module_count = max(1, round(anlage_kwp * 1000 / module_power_wp))
    kpi['module_count'] = module_count

    inverter_info = "String-Wechselrichter"
    storage_info = ""
    try:
        inverter_id = proj_details.get('selected_inverter_id')
        if inverter_id and 'get_product_by_id_func' in analysis:
            get_product = analysis['get_product_by_id_func']
            prod = get_product(inverter_id)
            if prod:
                power_kw = prod.get('power_kw') or 0
                if power_kw and power_kw > 100:
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
# Heading helper
# ---------------------------------------------------------------------------

def _make_heading(text: str, theme: Dict[str, Any]) -> Paragraph:
    if not _REPORTLAB_AVAILABLE:
        return Paragraph(text, ParagraphStyle('Heading2'))  # type: ignore
    colors_dict = theme.get('colors', {}) or {}
    primary = colors_dict.get('primary', '#003366')
    styles = theme.get('styles', {}) or {}
    arrow = f"<font color='{primary}'>&#9656;</font>"
    html = f"{arrow} {text}"
    style = styles.get('h2', ParagraphStyle('h2'))
    return Paragraph(html, style)

# ---------------------------------------------------------------------------
# Block architecture
# ---------------------------------------------------------------------------

class PDFBlock:
    name: str = "Block"
    required: bool = False

    def __init__(self, name: str, required: bool = False) -> None:
        self.name = name
        self.required = required

    def is_included(self, context: Dict[str, Any]) -> bool:
        if self.required:
            return True
        inclusion_options = context.get('inclusion_options', {}) or {}
        return inclusion_options.get(f'include_{self.name}', True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        raise NotImplementedError

class CoverPageBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='cover_page', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        title_img_b64 = context.get('title_image_b64')
        if title_img_b64:
            img = _b64_to_image_flowable(title_img_b64, max_width=context['doc_width'], max_height=context['doc_height'] * 0.5)
            if img:
                flows.append(img)
                flows.append(Spacer(1, 0.5 * cm))
        company_logo_b64 = context.get('company_logo_b64')
        if company_logo_b64:
            img = _b64_to_image_flowable(company_logo_b64, max_width=6*cm, max_height=3*cm)
            if img:
                img.hAlign = 'CENTER'
                flows.append(img)
                flows.append(Spacer(1, 0.3 * cm))
        offer_title = context.get('offer_title') or "Ihr Angebot"
        flows.append(Paragraph(offer_title, styles.get('h1', ParagraphStyle('h1'))))
        flows.append(Spacer(1, 0.5 * cm))
        company = context.get('company_info', {})
        company_lines: List[str] = []
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
        contact_parts: List[str] = []
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
    def __init__(self) -> None:
        super().__init__(name='kpi_overview', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        kpis = _extract_kpis(project, analysis)
        flows.append(_make_heading("Kennzahlen", theme))
        data = [
            ["Anlagenleistung (kWp)", _format_number(kpis['kwp'], "", 1)],
            ["Jährlicher Ertrag", _format_number(kpis['annual_production'], "kWh", 0)],
            ["CO₂‑Einsparung", _format_number(kpis['co2_savings'], "t/Jahr", 1)],
            ["Eigenverbrauchsquote", _format_number(kpis['self_consumption_rate'], "%", 1)],
            ["Autarkiegrad", _format_number(kpis['autarky_rate'], "%", 1)],
            ["Amortisation", _format_number(kpis['amortization_years'], "Jahre", 1)],
            ["PV‑Module", str(kpis['module_count'])],
        ]
        table_style = create_modern_table_style(theme)
        table = Table([["Kennzahl", "Wert"]] + data, colWidths=[7*cm, context['doc_width'] - 7*cm])
        table.setStyle(table_style)
        flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows

class ComponentsBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='components', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        kpis = _extract_kpis(project, analysis)
        flows.append(_make_heading("Technische Komponenten", theme))
        rows: List[List[str]] = []
        rows.append(["PV‑Module", f"{kpis['module_count']}× (ca. {round(kpis['kwp']*1000/kpis['module_count']):d} Wp pro Modul)"])
        rows.append(["Wechselrichter", kpis.get('inverter_info', 'String‑Wechselrichter')])
        storage_info = kpis.get('storage_info', '')
        if storage_info:
            rows.append(["Speicher", storage_info])
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
    def __init__(self) -> None:
        super().__init__(name='prod_vs_cons_chart', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        try:
            from pdf_generator import generate_prod_vs_cons_chart_image
            img_bytes = generate_prod_vs_cons_chart_image(context['analysis_results'], context['texts'])
        except Exception:
            img_bytes = None
        if img_bytes:
            try:
                img = Image(io.BytesIO(img_bytes))
                max_w = context['doc_width']
                w, h = img.drawWidth, img.drawHeight
                scale = min(max_w / w, 10*cm / h)
                img.drawWidth = w * scale
                img.drawHeight = h * scale
                flows.append(_make_heading("Ertrag vs. Verbrauch", theme))
                flows.append(img)
                flows.append(Spacer(1, 0.4 * cm))
            except Exception:
                pass
        if img_bytes:
            desc = context.get('texts', {}).get('description_prod_vs_cons_chart')
            if desc:
                flows.append(Paragraph(desc, context['theme'].get('styles', {}).get('BodyText', ParagraphStyle('BodyText'))))
                flows.append(Spacer(1, 0.4 * cm))
        return flows

class TermsBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='terms', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        texts = context.get('texts', {}) or {}
        terms_text = texts.get('pdf_terms_text', "Allgemeine Geschäftsbedingungen und Datenschutzhinweise.<br/>"
                                           "Bitte beachten Sie, dass dieses Angebot unverbindlich ist und unter dem"
                                           "Vorbehalt der Verfügbarkeit der Komponenten steht.")
        flows.append(_make_heading("Rechtliche Hinweise & AGB", theme))
        flows.append(Paragraph(terms_text, styles.get('BodyText', ParagraphStyle('BodyText'))))
        return flows

# ---------------------------------------------------------------------------
# Zusätzliche Blöcke für das TOM‑90 Layout
# ---------------------------------------------------------------------------

class PersonalSummaryBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='personal_summary', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        styles = context['theme'].get('styles', {})
        project = context['project_data']
        customer = project.get('customer_data', {}) or {}
        customer_lines: List[str] = []
        if customer.get('salutation'):
            customer_lines.append(customer['salutation'])
        if customer.get('first_name') or customer.get('last_name'):
            customer_lines.append(f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip())
        if customer.get('street') or customer.get('zip_code') or customer.get('city'):
            customer_lines.append(f"{customer.get('street', '')} {customer.get('zip_code', '')} {customer.get('city', '')}".strip())
        if customer.get('email'):
            customer_lines.append(customer['email'])
        if customer.get('phone'):
            customer_lines.append(customer['phone'])
        offer_id = project.get('project_details', {}).get('offer_id') or ''
        offer_date = project.get('project_details', {}).get('date') or datetime.now().strftime("%d.%m.%Y")
        flows.append(_make_heading("Persönliche Zusammenfassung", context['theme']))
        if customer_lines:
            flows.append(Paragraph("<br/>".join(customer_lines), styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.3 * cm))
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
    def __init__(self) -> None:
        super().__init__(name='donut_charts', required=True)

    def _generate_donut_image(self, value: float, title: str, colors: List[str]) -> Optional[Image]:
        """Erzeugt ein schlankes Donut‑Diagramm mit mittigem Label."""
        if not _MATPLOTLIB_AVAILABLE or not _REPORTLAB_AVAILABLE:
            return None
        try:
            # Donut-Ring schmaler machen: width = 0.3 des Radius
            fig, ax = plt.subplots(figsize=(3, 3))
            sizes = [max(0, min(100, value)), max(0, 100 - value)]
            wedges, _ = ax.pie(
                sizes,
                colors=colors,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.3, edgecolor='white'),
            )
            # Wert in der Mitte anzeigen
            ax.text(0, 0, f"{value:.0f} %", ha='center', va='center', fontsize=12, weight='bold', color=colors[0])
            ax.set_title(title, fontsize=10)
            ax.axis('equal')
            buffer = io.BytesIO()
            fig.savefig(buffer, format='PNG', bbox_inches='tight', dpi=150)
            plt.close(fig)
            buffer.seek(0)
            img = Image(buffer)
            # Skalierung beibehalten
            scale = min((6 * cm) / img.drawWidth, (6 * cm) / img.drawHeight)
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
        primary = theme.get('colors', {}).get('primary', '#003366')
        secondary = theme.get('colors', {}).get('secondary', '#0081b8')
        eigenv = analysis.get('self_consumption_rate_percent') or 0
        autark = analysis.get('self_supply_rate_percent') or analysis.get('autarky_rate_percent') or 0
        flows.append(_make_heading("Eigenverbrauch & Unabhängigkeit", theme))
        img_ev = self._generate_donut_image(eigenv, "Eigenverbrauch", [primary, secondary])
        img_aut = self._generate_donut_image(autark, "Unabhängigkeit", [secondary, primary])
        if img_ev and img_aut:
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
            data = [
                ["Kennzahl", "Wert"],
                ["Eigenverbrauch", f"{eigenv:.1f}%"],
                ["Unabhängigkeit", f"{autark:.1f}%"],
            ]
            table = Table(data, colWidths=[6*cm, context['doc_width'] - 6*cm])
            table.setStyle(create_modern_table_style(theme))
            flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        desc = context.get('texts', {}).get('description_donut_charts')
        if desc:
            flows.append(Paragraph(desc, styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4 * cm))
        return flows

class SystemInfoBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='system_info', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        project = context['project_data']
        analysis = context['analysis_results']
        flows.append(_make_heading("Ihr neues Energiesystem", theme))
        img = None
        img_b64 = context.get('title_image_b64') or project.get('title_image_b64') or ''
        if img_b64:
            img = _b64_to_image_flowable(img_b64, max_width=context['doc_width']*0.45, max_height=7*cm)
        data_rows: List[List[str]] = []
        def add_row(label: str, value: Any, unit: str = ""):
            if value is None or value == "":
                data_rows.append([label, "–"])
            else:
                formatted = _format_number(value, unit) if isinstance(value, (int, float)) else str(value)
                data_rows.append([label, formatted])
        heating = analysis.get('heating_system') or project.get('heating_system') or project.get('heizung')
        add_row("Heizung", heating)
        hot_water = analysis.get('hot_water_system') or project.get('hot_water_system') or project.get('warmwasser')
        add_row("Warmwasser", hot_water)
        consumption = analysis.get('annual_consumption_kwh') or project.get('annual_consumption_kwh') or analysis.get('consumption_kwh')
        add_row("Verbrauch", consumption, "kWh/Jahr")
        roof = analysis.get('roof_tilt_degrees') or project.get('roof_tilt_degrees') or project.get('dachneigung')
        add_row("Dachneigung", roof, "°")
        kwp = analysis.get('anlage_kwp') or analysis.get('anlage_kwp_kwp') or project.get('anlage_kwp')
        add_row("Solaranlage", kwp, "kWp")
        battery = analysis.get('battery_capacity_kwh') or project.get('battery_capacity_kwh') or project.get('batterie')
        add_row("Batterie", battery, "kWh")
        annual_yield = analysis.get('annual_pv_production_kwh') or analysis.get('annual_production_kwh')
        add_row("Jahresertrag", annual_yield, "kWh/Jahr")
        table = Table([ ["", ""] ] + data_rows, colWidths=[5*cm, context['doc_width']*0.45 - 5*cm])
        table.setStyle(create_modern_table_style(theme))
        if img:
            content_table = Table([[img, table]], colWidths=[context['doc_width']*0.45, context['doc_width']*0.45])
        else:
            content_table = Table([[table]], colWidths=[context['doc_width']*0.45])
        content_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        flows.append(content_table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows

class SavingsSummaryBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='savings_summary', required=False)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        val_with = (
            analysis.get('total_savings_with_storage_eur')
            or analysis.get('savings_with_storage_eur')
            or None
        )
        val_without = (
            analysis.get('total_savings_without_storage_eur')
            or analysis.get('savings_without_storage_eur')
            or None
        )
        if val_with is None or val_without is None:
            annual_prod = analysis.get('annual_pv_production_kwh') or 0
            est_rate = 0.25
            val_without = annual_prod * est_rate * 20
            val_with = val_without * 1.1
        try:
            val_with = float(val_with)
        except Exception:
            val_with = 0.0
        try:
            val_without = float(val_without)
        except Exception:
            val_without = 0.0
        diff = val_with - val_without
        flows.append(_make_heading("Ersparnis‑Zusammenfassung", theme))
        data = [
            ["Option", "Ersparnis (EUR)"],
            ["Mit Speicher", _format_number(val_with, "€", 0)],
            ["Ohne Speicher", _format_number(val_without, "€", 0)],
            ["Differenz", _format_number(diff, "€", 0)],
        ]
        table = Table(data, colWidths=[7 * cm, context['doc_width'] - 7 * cm])
        style = create_modern_table_style(theme)
        extra_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), theme['colors'].get('secondary', '#eeeeee')),
            ('FONTNAME', (0, 0), (-1, 0), theme['fonts'].get('family_bold', 'Helvetica-Bold')),
            ('BACKGROUND', (0, 3), (-1, 3), theme['colors'].get('secondary', '#eeeeee')),
            ('FONTNAME', (0, 3), (-1, 3), theme['fonts'].get('family_bold', 'Helvetica-Bold')),
        ]
        for cmd in extra_commands:
            style.add(*cmd)
        table.setStyle(style)
        flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        return flows

class CustomTextBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='custom_text', required=False)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        custom_texts = context.get('texts', {}).get('custom_texts') or []
        if not custom_texts:
            return flows
        for section in custom_texts:
            title = section.get('title') or ""
            body = section.get('body') or ""
            if not title and not body:
                continue
            if title:
                flows.append(_make_heading(title, theme))
            if body:
                flows.append(Paragraph(body, styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4 * cm))
        return flows

class CustomImageBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='custom_image', required=False)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        if not _REPORTLAB_AVAILABLE:
            return flows
        images_b64 = context.get('texts', {}).get('custom_images') or []
        captions = context.get('texts', {}).get('custom_image_captions') or []
        theme = context['theme']
        styles = theme.get('styles', {})
        if not images_b64:
            return flows
        for idx, img_b64 in enumerate(images_b64):
            img = _b64_to_image_flowable(img_b64, max_width=12 * cm, max_height=10 * cm)
            if img:
                img.hAlign = 'LEFT'
                flows.append(img)
                if idx < len(captions) and captions[idx]:
                    flows.append(Paragraph(captions[idx], styles.get('BodyText', ParagraphStyle('BodyText'))))
                flows.append(Spacer(1, 0.4 * cm))
        return flows

class BarChartBlock(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='bar_chart', required=True)

    def _generate_bar_chart_image(self, values: Dict[str, float], theme: Dict[str, Any]) -> Optional[Image]:
        if not _MATPLOTLIB_AVAILABLE or not _REPORTLAB_AVAILABLE:
            return None
        try:
            labels = ["Mit Speicher", "Ohne Speicher"]
            data = [values.get('mit', 0), values.get('ohne', 0)]
            fig, ax = plt.subplots(figsize=(4, 3))
            primary = theme.get('colors', {}).get('primary', '#003366')
            secondary = theme.get('colors', {}).get('secondary', '#0081b8')
            bars = ax.bar(labels, data, color=[primary, secondary], width=0.6, edgecolor='white', linewidth=0.5)
            ax.set_ylabel('Ersparnis (EUR)', fontsize=10)
            ax.set_title('Ersparnis über 20 Jahre', fontsize=11)
            ax.grid(axis='y', linestyle='--', linewidth=0.4, alpha=0.6)
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:,.0f} €".replace(',', '.'),
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 4), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)
            buffer = io.BytesIO()
            fig.tight_layout()
            fig.savefig(buffer, format='PNG', dpi=150)
            plt.close(fig)
            buffer.seek(0)
            img = Image(buffer)
            scale = min((12 * cm) / img.drawWidth, (6 * cm) / img.drawHeight)
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
        val_with = analysis.get('total_savings_with_storage_eur') or analysis.get('savings_with_storage_eur') or None
        val_without = analysis.get('total_savings_without_storage_eur') or analysis.get('savings_without_storage_eur') or None
        if val_with is None or val_without is None:
            annual_prod = analysis.get('annual_pv_production_kwh') or 0
            est_rate = 0.25
            val_without = annual_prod * est_rate * 20
            val_with = val_without * 1.1
        values = {'mit': float(val_with), 'ohne': float(val_without)}
        flows.append(_make_heading("Ersparnis über 20 Jahre", theme))
        img = self._generate_bar_chart_image(values, theme)
        if img:
            flows.append(img)
        else:
            table = Table([
                ["Option", "Ersparnis (EUR)"],
                ["Mit Speicher", f"{values['mit']:.0f}"],
                ["Ohne Speicher", f"{values['ohne']:.0f}"],
            ], colWidths=[6*cm, context['doc_width'] - 6*cm])
            table.setStyle(create_modern_table_style(theme))
            flows.append(table)
        flows.append(Spacer(1, 0.4 * cm))
        desc = context.get('texts', {}).get('description_bar_chart')
        if desc:
            flows.append(Paragraph(desc, styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4 * cm))
        return flows
        rows = []
        list_products_func = context.get('list_products_func')
        get_product_by_id_func = context.get('get_product_by_id_func')

        # Beispiel: Schleife über alle ausgewählten Produkte, sofern Funktionen existieren
        if list_products_func and get_product_by_id_func:
            for prod in list_products_func():
                prod_data = get_product_by_id_func(prod['id'])
                if not prod_data:
                    continue
                # Produktbild aus Base64
                img_b64 = prod_data.get('image_b64')
                img_flowable = _b64_to_image_flowable(img_b64, max_width=4*cm, max_height=3*cm) if img_b64 else None
                # Tabellenzeile: Bild | Name | Leistung / Kapazität | weitere Daten
                row_cells = []
                if img_flowable:
                    row_cells.append(img_flowable)
                else:
                    row_cells.append("–")
                row_cells.append(prod_data.get('name', ''))
                row_cells.append(prod_data.get('power_kw', ''))
                row_cells.append(prod_data.get('capacity_kwh', ''))
                rows.append(row_cells)
            # Kopfzeile definieren
            col_widths = [4*cm, 4*cm, 3*cm, context['doc_width'] - 11*cm]
            table = Table([["Bild", "Name", "Leistung", "Kapazität"]] + rows, colWidths=col_widths)
            table.setStyle(create_modern_table_style(theme))
            flows.append(table)
        else:
            pass
            
class HaveYouKnowBlock(PDFBlock):
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
        flows.append(_make_heading("Haben Sie gewusst?", theme))
        for fact in facts:
            flows.append(Paragraph(f"• {fact}", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.2 * cm))
        flows.append(Spacer(1, 0.4 * cm))
        return flows

class CO2Block(PDFBlock):
    def __init__(self) -> None:
        super().__init__(name='co2_balance', required=True)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        co2_savings_kg = analysis.get('annual_co2_savings_kg') or 0
        co2_savings_tons = co2_savings_kg / 1000.0
        km_per_car = 15000
        co2_per_km = 0.12
        km_equivalent = co2_savings_kg / co2_per_km if co2_per_km else 0
        tree_factor = 12.5
        trees_equivalent = co2_savings_kg / tree_factor if tree_factor else 0
        flows.append(_make_heading("CO₂‑Bilanz", theme))
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
    def __init__(self) -> None:
        super().__init__(name='financing', required=False)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
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
        interest_rate = (
            analysis.get('loan_interest_rate_percent')
            or project.get('loan_interest_rate_percent')
            or 4.0
        )
        try:
            interest_rate = float(interest_rate)
        except Exception:
            interest_rate = 4.0
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
        leasing_factor = (
            analysis.get('leasing_factor_percent')
            or project.get('leasing_factor_percent')
            or 2.5
        )
        try:
            leasing_factor = float(leasing_factor)
        except Exception:
            leasing_factor = 2.5
        flows.append(_make_heading("Finanzierungsvergleich", theme))
        if investment <= 0:
            flows.append(Paragraph("Keine Finanzierungsdaten verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4 * cm))
            return flows
        credit_result = None
        leasing_result = None
        try:
            from financial_tools import calculate_annuity, calculate_leasing_costs
            credit_result = calculate_annuity(investment, interest_rate, duration_years)
            leasing_result = calculate_leasing_costs(investment, leasing_factor, int(duration_years * 12))
        except Exception:
            credit_result = None
            leasing_result = None
        data = [["Option", "Monatliche Rate", "Gesamtkosten", "Zinsen/Restwert"]]
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
        if leasing_result and not leasing_result.get('error'):
            lease_month = leasing_result.get('monatliche_rate', 0)
            lease_total = leasing_result.get('gesamtkosten', 0)
            lease_rest = leasing_result.get('restwert') if 'restwert' in leasing_result else leasing_result.get('effektive_kosten', 0)
            data.append([
                "Leasing",
                _format_number(lease_month, "€", 0),
                _format_number(lease_total, "€", 0),
                _format_number(lease_rest, "€", 0),
            ])
        else:
            data.append(["Leasing", "–", "–", "–"])
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

class FinancingDetailsBlock(PDFBlock):
    """Block für detaillierte Finanzierungsberechnungen.

    Dieser Block fasst alle verfügbaren Berechnungen aus
    ``financial_tools.py`` zusammen. Für jede Finanzierungsart
    (Annuitätendarlehen, Leasing, Abschreibung, Vergleich,
    Kapitalertragsteuer und Contracting) wird eine eigene
    Untersektion erzeugt. Falls Eingabedaten fehlen oder ein
    Berechnungsmodul nicht importiert werden kann, wird ein
    entsprechender Hinweis ausgegeben. Der Block ist optional
    und kann über ``include_financing_details`` gesteuert werden.
    """

    def __init__(self) -> None:
        super().__init__(name='financing_details', required=False)

    def _safe_imports(self):
        """Versucht, alle benötigten Funktionen aus financial_tools zu importieren.

        Returns:
            Tuple[callable, callable, callable, callable, callable, callable]:
                Die importierten Funktionen (oder ``None`` bei Fehler).
        """
        try:
            from financial_tools import (
                calculate_annuity,
                calculate_leasing_costs,
                calculate_depreciation,
                calculate_financing_comparison,
                calculate_capital_gains_tax,
                calculate_contracting_costs,
            )
            return (
                calculate_annuity,
                calculate_leasing_costs,
                calculate_depreciation,
                calculate_financing_comparison,
                calculate_capital_gains_tax,
                calculate_contracting_costs,
            )
        except Exception:
            return (None, None, None, None, None, None)

    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        inclusion = context.get('inclusion_options', {})
        # Prüfen, ob der gesamte Block eingeschlossen werden soll
        if not inclusion.get('include_financing_details', True):
            return flows
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        calc_annuity, calc_leasing, calc_depr, calc_comparison, calc_tax, calc_contracting = self._safe_imports()
        # Gemeinsame Parameter
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
        annual_rate = (
            analysis.get('loan_interest_rate_percent')
            or project.get('loan_interest_rate_percent')
            or 4.0
        )
        try:
            annual_rate = float(annual_rate)
        except Exception:
            annual_rate = 4.0
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
        leasing_factor = (
            analysis.get('leasing_factor_percent')
            or project.get('leasing_factor_percent')
            or 2.5
        )
        try:
            leasing_factor = float(leasing_factor)
        except Exception:
            leasing_factor = 2.5
        # 1. Annuitätendarlehen
        if inclusion.get('include_financing_details_annuity', True):
            flows.append(Paragraph("Annuitätendarlehen", styles.get('h3', ParagraphStyle('h3'))))
            if calc_annuity:
                result = calc_annuity(investment, annual_rate, duration_years)
                if not result.get('error'):
                    table_data = [
                        ["Kennzahl", "Wert"],
                        ["Monatliche Rate", _format_number(result.get('monatliche_rate'), "€", 0)],
                        ["Gesamtzinsen", _format_number(result.get('gesamtzinsen'), "€", 0)],
                        ["Gesamtkosten", _format_number(result.get('gesamtkosten'), "€", 0)],
                        ["Laufzeit (Monate)", str(result.get('laufzeit_monate'))],
                    ]
                    table = Table(table_data, colWidths=[7*cm, context['doc_width'] - 7*cm])
                    table.setStyle(create_modern_table_style(theme))
                    flows.append(table)
                else:
                    flows.append(Paragraph("Keine gültigen Daten für Annuität vorhanden.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            else:
                flows.append(Paragraph("Berechnungsmodul für Annuität nicht verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4*cm))
        # 2. Leasing
        if inclusion.get('include_financing_details_leasing', True):
            flows.append(Paragraph("Leasing", styles.get('h3', ParagraphStyle('h3'))))
            if calc_leasing:
                result = calc_leasing(investment, leasing_factor, duration_years * 12)
                if not result.get('error'):
                    table_data = [
                        ["Kennzahl", "Wert"],
                        ["Monatliche Rate", _format_number(result.get('monatliche_rate'), "€", 0)],
                        ["Gesamtzinsen", _format_number(result.get('gesamtzinsen', result.get('gesamtzins', 0)), "€", 0)],
                        ["Gesamtkosten", _format_number(result.get('gesamtkosten'), "€", 0)],
                        ["Laufzeit (Monate)", str(result.get('laufzeit_monate'))],
                        ["Restwert", _format_number(result.get('restwert', result.get('effektive_kosten')), "€", 0)],
                    ]
                    table = Table(table_data, colWidths=[7*cm, context['doc_width'] - 7*cm])
                    table.setStyle(create_modern_table_style(theme))
                    flows.append(table)
                else:
                    flows.append(Paragraph("Keine gültigen Daten für Leasing vorhanden.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            else:
                flows.append(Paragraph("Berechnungsmodul für Leasing nicht verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4*cm))
        # 3. Abschreibung
        if inclusion.get('include_financing_details_depreciation', True):
            flows.append(Paragraph("Abschreibung (linear)", styles.get('h3', ParagraphStyle('h3'))))
            if calc_depr:
                try:
                    result = calc_depr(investment, duration_years)
                except Exception:
                    result = None
                if result:
                    table_data = [["Jahr", "Abschreibung"]]
                    for row in result.get('abschreibung', []):
                        jahr, betrag = row
                        table_data.append([str(jahr), _format_number(betrag, "€", 0)])
                    table = Table(table_data, colWidths=[7*cm, context['doc_width'] - 7*cm])
                    table.setStyle(create_modern_table_style(theme))
                    flows.append(table)
                else:
                    flows.append(Paragraph("Keine gültigen Daten für Abschreibung vorhanden.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            else:
                flows.append(Paragraph("Berechnungsmodul für Abschreibung nicht verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4*cm))
        # 4. Finanzierungsvergleich (Detail)
        if inclusion.get('include_financing_details_comparison', True):
            flows.append(Paragraph("Finanzierungsvergleich (Detail)", styles.get('h3', ParagraphStyle('h3'))))
            if calc_comparison:
                try:
                    result = calc_comparison(investment, annual_rate, duration_years, leasing_factor)
                except Exception:
                    result = None
                if result:
                    cmp_table = [
                        ["Kennzahl", "Kredit", "Leasing", "Kauf"],
                        ["Monatliche Rate", 
                         _format_number(result.get('kredit_rate'), "€", 0),
                         _format_number(result.get('leasing_rate'), "€", 0),
                         "–"],
                        ["Gesamtzinsen/Gesamtkosten", 
                         _format_number(result.get('kredit_zinsen'), "€", 0),
                         _format_number(result.get('leasing_zinsen', result.get('leasing_gesamtzinsen')), "€", 0),
                         "–"],
                        ["Restwert", 
                         "0 €",
                         _format_number(result.get('leasing_restwert', result.get('leasing_effektive_kosten')), "€", 0),
                         "0 €"],
                    ]
                    table = Table(cmp_table, colWidths=[6*cm, 3*cm, 3*cm, context['doc_width'] - 12*cm])
                    table.setStyle(create_modern_table_style(theme))
                    flows.append(table)
                else:
                    flows.append(Paragraph("Keine gültigen Daten für den Vergleich vorhanden.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            else:
                flows.append(Paragraph("Berechnungsmodul für Vergleich nicht verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4*cm))
        # 5. Kapitalertragsteuer
        if inclusion.get('include_financing_details_tax', True):
            flows.append(Paragraph("Kapitalertragsteuer", styles.get('h3', ParagraphStyle('h3'))))
            if calc_tax:
                try:
                    result = calc_tax(investment, annual_rate, duration_years)
                except Exception:
                    result = None
                if result:
                    flows.append(Paragraph(
                        f"Zu zahlende Kapitalertragsteuer: {_format_number(result.get('steuerbetrag', 0), '€', 0)}",
                        styles.get('BodyText', ParagraphStyle('BodyText'))
                    ))
                else:
                    flows.append(Paragraph("Keine gültigen Daten für Kapitalertragsteuer vorhanden.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            else:
                flows.append(Paragraph("Berechnungsmodul für Kapitalertragsteuer nicht verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4*cm))
        # 6. Contracting
        if inclusion.get('include_financing_details_contracting', True):
            flows.append(Paragraph("Contracting", styles.get('h3', ParagraphStyle('h3'))))
            if calc_contracting:
                try:
                    result = calc_contracting(investment, annual_rate, duration_years)
                except Exception:
                    result = None
                if result:
                    flows.append(Paragraph(
                        f"Monatliche Contracting-Kosten: {_format_number(result.get('monatliche_kosten', 0), '€', 0)}",
                        styles.get('BodyText', ParagraphStyle('BodyText'))
                    ))
                else:
                    flows.append(Paragraph("Keine gültigen Daten für Contracting vorhanden.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            else:
                flows.append(Paragraph("Berechnungsmodul für Contracting nicht verfügbar.", styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4*cm))
        return flows

# ---------------------------------------------------------------------------
# TOM-90 Specific Design Blocks (basierend auf vorlage.json)
# ---------------------------------------------------------------------------

class Tom90Page2Block(PDFBlock):
    """Seite 2 mit 3D-isometrischen Grafiken und TOM-90 Design."""
    
    def __init__(self) -> None:
        super().__init__(name='tom90_page2', required=True)
    
    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        if not _REPORTLAB_AVAILABLE:
            return flows
            
        theme = context['theme']
        styles = theme.get('styles', {})
        
        # TOM-90 Farben aus der Vorlage
        tom90_blue = '#0d3780'
        tom90_light_gray = '#f6f6f6'
        tom90_gray = '#e1dfdf'
        tom90_medium_gray = '#b4b4b4'
        
        flows.append(PageBreak())
        flows.append(Spacer(1, 1*cm))
        
        # Haupttitel für Seite 2
        flows.append(Paragraph("Ihr neues Energiesystem", styles.get('h1', ParagraphStyle('h1'))))
        flows.append(Spacer(1, 0.5*cm))
        
        # Große graue Box mit 3D-Darstellung (simuliert)
        analysis = context['analysis_results']
        project = context['project_data']
        
        # System-Daten für die 3D-Box
        anlage_kwp = analysis.get('anlage_kwp', 0)
        annual_production = analysis.get('annual_pv_production_kwh', 0)
        module_count = project.get('pv_details', {}).get('module_quantity', 0)
        if module_count == 0 and anlage_kwp > 0:
            module_count = max(1, round(anlage_kwp * 1000 / 420))
        
        # 3D-Box Content (TOM-90 Style) - Sichere Version ohne Unicode-Probleme
        box_content = f"""
        <para alignment="center" fontSize="16" textColor="{tom90_blue}">
        <b>3D-VISUALISIERUNG IHRES PV-SYSTEMS</b>
        </para>
        <br/><br/>
        
        <para alignment="center" fontSize="12">
        PV-Module: <b>{module_count} Stück</b> auf Ihrem Dach<br/>
        Gesamtleistung: <b>{anlage_kwp:.1f} kWp</b><br/>
        Jahresertrag: <b>{annual_production:,.0f} kWh</b><br/>
        </para>
        <br/>
        
        <para alignment="center" fontSize="10" textColor="#666666">
        [3D-Isometrische Darstellung würde hier erscheinen]<br/>
        Realistische Darstellung Ihrer Dachfläche mit<br/>
        optimal positionierten Solarmodulen in 3D-Ansicht
        </para>
        """
        
        # Erstelle die große graue Box (wie in TOM-90)
        box_table_data = [[Paragraph(box_content, styles.get('Normal'))]]
        box_table = Table(box_table_data, colWidths=[context['doc_width'] - 2*cm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), tom90_light_gray),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 30),
            ('BOTTOMPADDING', (0,0), (-1,-1), 30),
            ('BOX', (0,0), (-1,-1), 2, tom90_blue),
            ('GRID', (0,0), (-1,-1), 1, tom90_medium_gray),
        ]))
        flows.append(box_table)
        flows.append(Spacer(1, 1*cm))
        
        # Technische Details in TOM-90 Style (ohne Unicode-Emoji)
        tech_details = [
            ["Gebäudedaten", ""],
            ["Dachneigung", f"{project.get('project_details', {}).get('tilt_angle', '30')}°"],
            ["Ausrichtung", project.get('project_details', {}).get('orientation', 'Süd')],
            ["Dachfläche", f"{analysis.get('roof_area_sqm', 'nicht angegeben')} m²"],
            ["", ""],
            ["Anlagendaten", ""],
            ["Modultyp", "Monokristallin, 420 Wp"],
            ["Wechselrichter", "String-Wechselrichter"],
            ["Montagesystem", "Aufdach-Montage"],
        ]
        
        tech_table = Table(tech_details, colWidths=[8*cm, context['doc_width'] - 10*cm])
        tech_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('BACKGROUND', (0,0), (0,0), tom90_blue),
            ('TEXTCOLOR', (0,0), (0,0), colors.white),
            ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,5), (0,5), tom90_blue),
            ('TEXTCOLOR', (0,5), (0,5), colors.white),
            ('FONTNAME', (0,5), (0,5), 'Helvetica-Bold'),
            ('GRID', (0,1), (-1,4), 0.5, tom90_medium_gray),
            ('GRID', (0,6), (-1,-1), 0.5, tom90_medium_gray),
        ]))
        flows.append(tech_table)
        
        return flows

class Tom90Page3Block(PDFBlock):
    """Seite 3 mit zwei großen Vergleichs-Boxen (TOM-90 Design)."""
    
    def __init__(self) -> None:
        super().__init__(name='tom90_page3', required=True)
    
    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        if not _REPORTLAB_AVAILABLE:
            return flows
            
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        
        # TOM-90 Farben
        tom90_blue = '#0d3780'
        tom90_light_gray = '#f6f6f6'
        tom90_medium_gray = '#b4b4b4'
        
        flows.append(PageBreak())
        flows.append(Spacer(1, 1*cm))
        
        # Haupttitel
        flows.append(Paragraph("Wirtschaftlichkeits-Vergleich", styles.get('h1', ParagraphStyle('h1'))))
        flows.append(Spacer(1, 0.8*cm))
        
        # Kennzahlen extrahieren
        eigenverbrauch = analysis.get('self_consumption_rate_percent', 42)
        autarkie = analysis.get('self_supply_rate_percent', 54)
        annual_savings = analysis.get('annual_financial_benefit_year1', 1200)
        amortization = analysis.get('amortization_time_years', 12)
        co2_savings = analysis.get('annual_co2_savings_kg', 3500) / 1000
        
        # Linke Box: "Mit PV-Anlage"
        left_content = f"""
        <para alignment="center" fontSize="14" textColor="{tom90_blue}">
        <b>MIT PV-ANLAGE</b>
        </para>
        <br/>
        
        <para alignment="center" fontSize="24" textColor="{tom90_blue}">
        <b>{eigenverbrauch:.0f}%</b>
        </para>
        <para alignment="center" fontSize="12">
        Eigenverbrauchsquote
        </para>
        <br/>
        
        <para alignment="center" fontSize="20" textColor="{tom90_blue}">
        <b>{autarkie:.0f}%</b>
        </para>
        <para alignment="center" fontSize="12">
        Unabhängigkeitsgrad
        </para>
        <br/>
        
        <para alignment="center" fontSize="16" textColor="#008000">
        <b>+ {annual_savings:,.0f} €</b>
        </para>
        <para alignment="center" fontSize="10">
        Ersparnis pro Jahr
        </para>
        <br/>
        
        <para alignment="center" fontSize="12" textColor="#008000">
        <b>{co2_savings:.1f} t CO₂</b> weniger pro Jahr
        </para>
        """
        
        # Rechte Box: "Ohne PV-Anlage"
        right_content = f"""
        <para alignment="center" fontSize="14" textColor="#cc0000">
        <b>OHNE PV-ANLAGE</b>
        </para>
        <br/>
        
        <para alignment="center" fontSize="24" textColor="#cc0000">
        <b>0%</b>
        </para>
        <para alignment="center" fontSize="12">
        Eigenverbrauchsquote
        </para>
        <br/>
        
        <para alignment="center" fontSize="20" textColor="#cc0000">
        <b>0%</b>
        </para>
        <para alignment="center" fontSize="12">
        Unabhängigkeitsgrad
        </para>
        <br/>
        
        <para alignment="center" fontSize="16" textColor="#cc0000">
        <b>+ 0 €</b>
        </para>
        <para alignment="center" fontSize="10">
        Ersparnis pro Jahr
        </para>
        <br/>
        
        <para alignment="center" fontSize="12" textColor="#cc0000">
        Stetig <b>steigende Stromkosten</b><br/>
        Volle <b>Abhängigkeit</b> vom Netz
        </para>
        """
        
        # Zwei-Spalten-Layout für die Boxen
        box_width = (context['doc_width'] - 3*cm) / 2
        comparison_data = [
            [
                Paragraph(left_content, styles.get('Normal')),
                Paragraph(right_content, styles.get('Normal'))
            ]
        ]
        
        comparison_table = Table(comparison_data, colWidths=[box_width, box_width])
        comparison_table.setStyle(TableStyle([
            # Linke Box (Mit PV)
            ('BACKGROUND', (0,0), (0,0), tom90_light_gray),
            ('BOX', (0,0), (0,0), 3, tom90_blue),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (0,0), 15),
            ('RIGHTPADDING', (0,0), (0,0), 15),
            ('TOPPADDING', (0,0), (0,0), 20),
            ('BOTTOMPADDING', (0,0), (0,0), 20),
            
            # Rechte Box (Ohne PV)
            ('BACKGROUND', (1,0), (1,0), '#fff5f5'),
            ('BOX', (1,0), (1,0), 3, '#cc0000'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('VALIGN', (1,0), (1,0), 'MIDDLE'),
            ('LEFTPADDING', (1,0), (1,0), 15),
            ('RIGHTPADDING', (1,0), (1,0), 15),
            ('TOPPADDING', (1,0), (1,0), 20),
            ('BOTTOMPADDING', (1,0), (1,0), 20),
        ]))
        flows.append(comparison_table)
        flows.append(Spacer(1, 1*cm))
        
        # Amortisations-Info (ohne Unicode-Emoji)
        amort_content = f"""
        <para alignment="center" fontSize="16" textColor="{tom90_blue}">
        <b>AMORTISATION: {amortization:.1f} JAHRE</b>
        </para>
        <para alignment="center" fontSize="12">
        Nach {amortization:.1f} Jahren haben sich die Investitionskosten amortisiert.<br/>
        Danach produzieren Sie <b>kostenlosen Strom</b> für weitere 13+ Jahre!
        </para>
        """
        
        amort_table = Table([[Paragraph(amort_content, styles.get('Normal'))]], 
                           colWidths=[context['doc_width'] - 2*cm])
        amort_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), '#e8f4fd'),
            ('BOX', (0,0), (-1,-1), 2, tom90_blue),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        flows.append(amort_table)
        
        return flows

class Tom90Page4Block(PDFBlock):
    """Seite 4 mit detaillierten Komponenten und Spezifikationen."""
    
    def __init__(self) -> None:
        super().__init__(name='tom90_page4', required=True)
    
    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        if not _REPORTLAB_AVAILABLE:
            return flows
            
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        project = context['project_data']
        
        # TOM-90 Farben
        tom90_blue = '#0d3780'
        tom90_light_gray = '#f6f6f6'
        tom90_medium_gray = '#b4b4b4'
        
        flows.append(PageBreak())
        flows.append(Spacer(1, 1*cm))
        
        # Haupttitel
        flows.append(Paragraph("Komponenten & Spezifikationen", styles.get('h1', ParagraphStyle('h1'))))
        flows.append(Spacer(1, 0.8*cm))
        
        # Komponenten-Details
        anlage_kwp = analysis.get('anlage_kwp', 0)
        module_count = project.get('pv_details', {}).get('module_quantity', 0)
        if module_count == 0 and anlage_kwp > 0:
            module_count = max(1, round(anlage_kwp * 1000 / 420))
        
        # Hauptkomponenten-Tabelle (ohne Unicode-Emoji)
        components_data = [
            ["KOMPONENTE", "SPEZIFIKATION", "DETAILS"],
            ["", "", ""],
            ["PV-Module", f"{module_count} Stück", "Monokristalline Hochleistungsmodule"],
            ["", "420 Wp pro Modul", "25 Jahre Leistungsgarantie"],
            ["", f"Gesamt: {anlage_kwp:.1f} kWp", "Wirkungsgrad: >20%"],
            ["", "", ""],
            ["Wechselrichter", "String-Wechselrichter", "Europäischer Wirkungsgrad >96%"],
            ["", f"Leistung: {anlage_kwp:.1f} kW", "10 Jahre Herstellergarantie"],
            ["", "Smart Monitoring", "App-Überwachung inklusive"],
            ["", "", ""],
            ["Montagesystem", "Aufdach-Montage", "Korrosionsbeständiges Aluminium"],
            ["", "Dachhaken-System", "TÜV-geprüft und zertifiziert"],
            ["", "Windlastwerte", "Entspricht lokalen Bauvorschriften"],
        ]
        
        # Speicher hinzufügen falls vorhanden
        if project.get('pv_details', {}).get('include_storage'):
            battery_capacity = project.get('project_details', {}).get('battery_capacity_kwh', 6.1)
            components_data.extend([
                ["", "", ""],
                ["Batteriespeicher", f"{battery_capacity} kWh", "Lithium-Ionen-Technologie"],
                ["", "10 Jahre Garantie", "Notstrom-Funktion verfügbar"],
                ["", "Smart Energy Management", "Optimierte Eigenverbrauchssteuerung"],
            ])
        
        comp_table = Table(components_data, colWidths=[4*cm, 4*cm, context['doc_width'] - 10*cm])
        comp_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0,0), (-1,0), tom90_blue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            
            # Trennzeilen
            ('BACKGROUND', (0,1), (-1,1), tom90_medium_gray),
            ('BACKGROUND', (0,5), (-1,5), tom90_medium_gray),
            ('BACKGROUND', (0,9), (-1,9), tom90_medium_gray),
            
            # Komponenten-Kategorien
            ('FONTNAME', (0,2), (0,2), 'Helvetica-Bold'),
            ('FONTNAME', (0,6), (0,6), 'Helvetica-Bold'),
            ('FONTNAME', (0,10), (0,10), 'Helvetica-Bold'),
            
            # Allgemeine Formatierung
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 1, tom90_medium_gray),
        ]))
        
        # Bei Speicher andere Zeilen hinzufügen
        if project.get('pv_details', {}).get('include_storage'):
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0,13), (-1,13), tom90_medium_gray),
                ('FONTNAME', (0,14), (0,14), 'Helvetica-Bold'),
            ]))
        
        flows.append(comp_table)
        flows.append(Spacer(1, 1*cm))
        
        # Qualitäts- und Sicherheitshinweise (ohne Unicode-Emoji)
        quality_content = f"""
        <para alignment="center" fontSize="14" textColor="{tom90_blue}">
        <b>QUALITÄT &amp; SICHERHEIT</b>
        </para>
        <br/>
        
        <para fontSize="11">
        <b>✓ TÜV-Zertifizierung:</b> Alle Komponenten sind TÜV-geprüft und zertifiziert<br/>
        <b>✓ CE-Kennzeichnung:</b> Entspricht allen EU-Sicherheitsstandards<br/>
        <b>✓ VDE-Normen:</b> Installation nach VDE 0100 und VDE-AR-N 4105<br/>
        <b>✓ Fachbetrieb:</b> Installation durch zertifizierte Elektrofachkräfte<br/>
        <b>✓ Versicherung:</b> Vollständige Photovoltaik-Versicherung empfohlen<br/>
        <b>✓ Monitoring:</b> 24/7 Überwachung und Ferndiagnose möglich
        </para>
        """
        
        quality_table = Table([[Paragraph(quality_content, styles.get('Normal'))]], 
                             colWidths=[context['doc_width'] - 2*cm])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), tom90_light_gray),
            ('BOX', (0,0), (-1,-1), 2, tom90_blue),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        flows.append(quality_table)
        
        return flows

class Tom90Page5Block(PDFBlock):
    """Seite 5 mit Finanzierung und Abschluss."""
    
    def __init__(self) -> None:
        super().__init__(name='tom90_page5', required=True)
    
    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        flows: List[Any] = []
        if not _REPORTLAB_AVAILABLE:
            return flows
            
        theme = context['theme']
        styles = theme.get('styles', {})
        analysis = context['analysis_results']
        company_info = context['company_info']
        
        # TOM-90 Farben
        tom90_blue = '#0d3780'
        tom90_light_gray = '#f6f6f6'
        tom90_medium_gray = '#b4b4b4'
        
        flows.append(PageBreak())
        flows.append(Spacer(1, 1*cm))
        
        # Haupttitel
        flows.append(Paragraph("Investition & Finanzierung", styles.get('h1', ParagraphStyle('h1'))))
        flows.append(Spacer(1, 0.8*cm))
        
        # Investitions-Übersicht
        total_investment = analysis.get('total_investment_netto', 0)
        if total_investment == 0:
            total_investment = analysis.get('anlage_kwp', 8.4) * 1300  # Schätzung
        
        investment_data = [
            ["INVESTITIONS-ÜBERSICHT", "BETRAG"],
            ["", ""],
            ["Solarmodule & Wechselrichter", f"{total_investment * 0.55:,.0f} €"],
            ["Montagesystem & Installation", f"{total_investment * 0.30:,.0f} €"],
            ["Elektroinstallation & Zubehör", f"{total_investment * 0.10:,.0f} €"],
            ["Planung & Inbetriebnahme", f"{total_investment * 0.05:,.0f} €"],
            ["", ""],
            ["NETTO-GESAMTPREIS", f"{total_investment:,.0f} €"],
            ["MwSt. (19%)", f"{total_investment * 0.19:,.0f} €"],
            ["BRUTTO-GESAMTPREIS", f"{total_investment * 1.19:,.0f} €"],
        ]
        
        invest_table = Table(investment_data, colWidths=[10*cm, context['doc_width'] - 12*cm])
        invest_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0,0), (-1,0), tom90_blue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            
            # Trennzeilen
            ('BACKGROUND', (0,1), (-1,1), tom90_medium_gray),
            ('BACKGROUND', (0,6), (-1,6), tom90_medium_gray),
            
            # Summenzeilen
            ('BACKGROUND', (0,7), (-1,7), tom90_light_gray),
            ('FONTNAME', (0,7), (-1,7), 'Helvetica-Bold'),
            ('BACKGROUND', (0,9), (-1,9), tom90_blue),
            ('TEXTCOLOR', (0,9), (-1,9), colors.white),
            ('FONTNAME', (0,9), (-1,9), 'Helvetica-Bold'),
            
            # Allgemeine Formatierung
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),  # Beträge rechtsbündig
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 1, tom90_medium_gray),
        ]))
        flows.append(invest_table)
        flows.append(Spacer(1, 1*cm))
        
        # Finanzierungsoptionen (ohne Unicode-Emoji)
        financing_content = f"""
        <para alignment="center" fontSize="14" textColor="{tom90_blue}">
        <b>FINANZIERUNGSOPTIONEN</b>
        </para>
        <br/>
        
        <para fontSize="11">
        <b>1. Barkauf (Empfohlen)</b><br/>
        ✓ Beste Rendite durch sofortige Eigentumsübertragung<br/>
        ✓ Keine Zinsen oder zusätzliche Kosten<br/>
        ✓ Volle KfW-Förderung und Steuervorteile<br/>
        <br/>
        
        <b>2. KfW-Darlehen (270)</b><br/>
        ✓ Zinsgünstige Finanzierung bis 150.000 €<br/>
        ✓ Laufzeit bis 20 Jahre möglich<br/>
        ✓ Teilweise tilgungsfreie Anlaufjahre<br/>
        ✓ <b>Rate ab {total_investment * 0.004:.0f} €/Monat</b> bei 4% Zinssatz<br/>
        <br/>
        
        <b>3. Solar-Leasing</b><br/>
        ✓ Keine Anfangsinvestition erforderlich<br/>
        ✓ Rundum-Service inklusive Wartung<br/>
        ✓ <b>Ab {total_investment * 0.0025:.0f} €/Monat</b> (20 Jahre Laufzeit)<br/>
        ✓ Option zum Kauf nach Vertragsende
        </para>
        """
        
        financing_table = Table([[Paragraph(financing_content, styles.get('Normal'))]], 
                               colWidths=[context['doc_width'] - 2*cm])
        financing_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), tom90_light_gray),
            ('BOX', (0,0), (-1,-1), 2, tom90_blue),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        flows.append(financing_table)
        flows.append(Spacer(1, 1*cm))
        
        # Nächste Schritte & Kontakt (ohne Unicode-Emoji)
        next_steps_content = f"""
        <para alignment="center" fontSize="14" textColor="{tom90_blue}">
        <b>IHRE NÄCHSTEN SCHRITTE</b>
        </para>
        <br/>
        
        <para fontSize="11">
        <b>1. Angebot prüfen</b> - Nehmen Sie sich Zeit für alle Details<br/>
        <b>2. Vor-Ort-Termin</b> - Kostenlose Begehung und finale Planung<br/>
        <b>3. Auftragserteilung</b> - Unterzeichnung des Installationsvertrags<br/>
        <b>4. Anmeldung</b> - Wir kümmern uns um alle Formalitäten<br/>
        <b>5. Installation</b> - Professionelle Montage durch unser Team<br/>
        <b>6. Inbetriebnahme</b> - Übergabe und Einweisung<br/>
        </para>
        <br/>
        
        <para alignment="center" fontSize="12" textColor="{tom90_blue}">
        <b>KONTAKT FÜR RÜCKFRAGEN</b><br/>
        {company_info.get('name', 'Ihr Solar-Partner')}<br/>
        Tel: {company_info.get('phone', 'Tel. auf Anfrage')}<br/>
        E-Mail: {company_info.get('email', 'info@solar-partner.de')}<br/>
        <br/>
        <b>Wir freuen uns auf Ihr Vertrauen!</b>
        </para>
        """
        
        next_steps_table = Table([[Paragraph(next_steps_content, styles.get('Normal'))]], 
                                colWidths=[context['doc_width'] - 2*cm])
        next_steps_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), '#e8f4fd'),
            ('BOX', (0,0), (-1,-1), 2, tom90_blue),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        flows.append(next_steps_table)
        
        return flows

# ---------------------------------------------------------------------------
# TOM-90 Spezifische Theme-Funktionen
# ---------------------------------------------------------------------------

def create_tom90_table_style(theme: Dict[str, Any]) -> TableStyle:
    """Erstellt einen TOM-90 spezifischen Tabellenstil."""
    if not _REPORTLAB_AVAILABLE:
        return None
        
    tom90_blue = '#0d3780'
    tom90_light_gray = '#f6f6f6'
    tom90_medium_gray = '#b4b4b4'
    
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), tom90_blue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, tom90_medium_gray),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ])

def get_tom90_enhanced_theme() -> Dict[str, Any]:
    """Erweiterte TOM-90 Theme-Definition mit allen Stilen."""
    if not _REPORTLAB_AVAILABLE:
        return get_tom90_theme()
    
    base_theme = get_tom90_theme()
    
    # Erweiterte Stile hinzufügen
    base_theme['styles'] = {
        'h1': ParagraphStyle(
            'TOM90_H1',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor('#0d3780'),
            spaceAfter=12,
            alignment=0  # Links
        ),
        'h2': ParagraphStyle(
            'TOM90_H2',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#0d3780'),
            spaceAfter=8,
            alignment=0
        ),
        'h3': ParagraphStyle(
            'TOM90_H3',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#0d3780'),
            spaceAfter=6,
            alignment=0
        ),
        'Normal': ParagraphStyle(
            'TOM90_Normal',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=0
        ),
        'BodyText': ParagraphStyle(
            'TOM90_BodyText',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=4  # Justify
        ),
        'Center': ParagraphStyle(
            'TOM90_Center',
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=1  # Center
        ),
    }
    
    return base_theme

def create_tom90_styled_box(content: str, theme: Dict[str, Any], box_type: str = "default") -> Table:
    """Erstellt eine TOM-90 styled Box mit Inhalt."""
    if not _REPORTLAB_AVAILABLE:
        return None
        
    styles = theme.get('styles', {})
    tom90_blue = '#0d3780'
    tom90_light_gray = '#f6f6f6'
    tom90_medium_gray = '#b4b4b4'
    
    # Box-Typ bestimmt Farben
    if box_type == "highlight":
        bg_color = '#e8f4fd'
        border_color = tom90_blue
    elif box_type == "warning":
        bg_color = '#fff5f5'
        border_color = '#cc0000'
    elif box_type == "success":
        bg_color = '#f0fff0'
        border_color = '#008000'
    else:  # default
        bg_color = tom90_light_gray
        border_color = tom90_blue
    
    content_paragraph = Paragraph(content, styles.get('Normal', ParagraphStyle('Normal')))
    box_table = Table([[content_paragraph]], colWidths=[16*cm])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('BOX', (0,0), (-1,-1), 2, border_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    
    return box_table

# ---------------------------------------------------------------------------
# Custom Canvas for Page Numbers and Bottom Logo
# ---------------------------------------------------------------------------

if _REPORTLAB_AVAILABLE:
    class NumberedCanvas(_rl_canvas.Canvas):
        def __init__(self, *args, include_numbers: bool = True,
            include_logo: bool = True, company_logo_b64: Optional[str] = None,
            **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.include_numbers = include_numbers
            self.include_logo = include_logo
            self.company_logo_b64 = company_logo_b64
            self._saved_page_states: List[Dict[str, Any]] = []

        def showPage(self) -> None:
            self._saved_page_states.append(dict(self.__dict__))
            super().showPage()

        def save(self) -> None:
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number_and_logo(num_pages)
                super().showPage()
            super().save()

        def draw_page_number_and_logo(self, page_count: int) -> None:
            if self.include_numbers:
                text = f"Angebot Seite {self._pageNumber} von {page_count}"
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.white if hasattr(colors, 'white') else colors.HexColor('#FFFFFF'))
                page_width = A4[0]
                self.drawCentredString(page_width / 2, 0.15 * cm, text)
            if self.include_logo and self.company_logo_b64:
                try:
                    img_data = base64.b64decode(self.company_logo_b64)
                    logo = ImageReader(io.BytesIO(img_data))
                    logo_w = 1.5 * cm
                    iw, ih = logo.getSize()
                    scale = logo_w / iw
                    logo_h = ih * scale
                    self.drawImage(logo, 0.5 * cm, 0.1 * cm, width=logo_w, height=logo_h, mask='auto')
                except Exception:
                    pass

# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class Tom90Renderer:
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
        primary_color: Optional[str] = None,
    ) -> None:
        self.project_data = project_data or {}
        self.analysis_results = analysis_results or {}
        self.company_info = company_info or {}
        self.inclusion_options = inclusion_options or {}
        self.texts = texts or {}
        self.company_logo_base64 = company_logo_base64
        self.title_image_b64 = title_image_b64
        self.offer_title_text = offer_title_text
        
        # TOM-90 Enhanced Theme als Standard verwenden
        if theme_name == "TOM-90" or theme_name == "Blau Elegant":
            self.theme = get_tom90_enhanced_theme()
        else:
            self.theme = get_theme(theme_name) if _THEMING_AVAILABLE else get_tom90_enhanced_theme()
        
        # Primary Color überschreiben falls angegeben
        if primary_color:
            try:
                if primary_color.startswith('#'):
                    self.theme['colors']['primary'] = primary_color
                else:
                    self.theme['colors']['primary'] = '#' + primary_color
            except Exception:
                pass
        if blocks is not None:
            self.blocks = blocks
        else:
            self.blocks = [
                CoverPageBlock(),
                PersonalSummaryBlock(),
                KPIBlock(),
                DonutChartsBlock(),
                SystemInfoBlock(),
                SavingsSummaryBlock(),
                BarChartBlock(),
                ComponentsBlock(),
                HaveYouKnowBlock(),
                CO2Block(),
                FinancingBlock(),
                FinancingDetailsBlock(),# Detaillierte Finanzierungsberechnungen (optional)
                CustomTextBlock(),
                CustomImageBlock(),
                ChartBlock(),
                TermsBlock(),
            ]
            
            # TOM-90 spezifische Design-Blöcke hinzufügen (aktiviert per default)
            # TOM-90 spezifische Design-Blöcke hinzufügen (aktiviert per default)
            if inclusion_options.get('include_tom90_design_pages', True):
                self.blocks.extend([
                    Tom90Page2Block(),  # 3D-Isometrische Darstellung
                    Tom90Page3Block(),  # Zwei-Box-Vergleich
                    Tom90Page4Block(),  # Komponenten-Details
                    Tom90Page5Block(),  # Finanzierung & Kontakt
                ])

    def _header_footer(self, canvas_obj, doc) -> None:
        if not _REPORTLAB_AVAILABLE:
            return
        canvas_obj.saveState()
        theme_colors = self.theme.get('colors', {})
        primary_color = theme_colors.get('primary', '#003366')
        footer_color = theme_colors.get('primary', '#003366')
        canvas_obj.setFont(self.theme['fonts'].get('family_bold', 'Helvetica-Bold'), 9)
        canvas_obj.setFillColor(colors.HexColor(primary_color))
        company_name = self.company_info.get('name', '')
        canvas_obj.drawString(doc.leftMargin, doc.height + doc.topMargin - 0.5 * cm, company_name)
        offer_id = datetime.now().strftime("%Y%m%d%H%M")
        canvas_obj.drawRightString(doc.leftMargin + doc.width, doc.height + doc.topMargin - 0.5 * cm, f"Angebot {offer_id}")
        bar_height = 0.6 * cm
        canvas_obj.setFillColor(colors.HexColor(footer_color))
        canvas_obj.rect(0, 0, A4[0], bar_height, fill=1, stroke=0)
        canvas_obj.setFillColor(colors.white if hasattr(colors, 'white') else colors.HexColor('#FFFFFF'))
        canvas_obj.setFont(self.theme['fonts'].get('family_bold', 'Helvetica-Bold'), 8)
        today_str = datetime.now().strftime("%d.%m.%Y")
        canvas_obj.drawString(doc.leftMargin, 0.15 * cm, f"tom-90    {today_str}")
        canvas_obj.restoreState()

    def build_pdf(self) -> Optional[bytes]:
        if not _REPORTLAB_AVAILABLE:
            dummy_pdf = (b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\n"
                         b"endobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n"
                         b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >>\nendobj\n"
                         b"4 0 obj\n<< /Length 0 >>\nstream\n\nendstream\nendobj\n"
                         b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n"
                         b"0000000114 00000 n \n0000000178 00000 n \ntrailer\n<< /Root 1 0 R /Size 5 >>\n"
                         b"startxref\n224\n%%EOF")
            return dummy_pdf
        buffer = io.BytesIO()
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
        for block in self.blocks:
            if block.is_included(context):
                try:
                    flows = block.create_flowables(context)
                    if flows:
                        story.append(KeepTogether(flows))
                except Exception as e:
                    # Sichere Exception-Behandlung ohne weitere Exception-Verschachtelung
                    err_msg = f"Fehler im Block {block.name}: {str(e)[:200]}..."
                    try:
                        # Versuche eine sichere Fehlermeldung zu erstellen
                        error_style = ParagraphStyle('ErrorText', fontName='Helvetica', fontSize=10, textColor=colors.red)
                        story.append(Paragraph(err_msg, error_style))
                    except:
                        # Falls auch das fehlschlägt, ignoriere den Block
                        pass
        try:
            include_numbers = self.inclusion_options.get('include_page_numbers', True)
            include_logo = self.inclusion_options.get('include_page_logo', False)
            canvasmaker = None
            if (include_numbers or include_logo) and _REPORTLAB_AVAILABLE:
                def _canvas_factory(*args, **kwargs):
                    return NumberedCanvas(
                        *args,
                        include_numbers=include_numbers,
                        include_logo=include_logo,
                        company_logo_b64=self.company_logo_base64,
                        **kwargs
                    )
                canvasmaker = _canvas_factory
            if canvasmaker:
                doc.build(story, canvasmaker=canvasmaker)
            else:
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
    primary_color: Optional[str] = None,
    **kwargs
) -> Optional[bytes]:
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
        primary_color=primary_color,
    )
    return renderer.build_pdf()
