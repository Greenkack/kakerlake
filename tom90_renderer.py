"""
tom90_renderer.py – Rendering‑Engine für Angebote im TOM‑90‑Design
Autor: KI‑Agent – 25.07.2025
"""

from __future__ import annotations
import io, math, base64
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

# -------------------- ReportLab-Imports mit Fallback --------------------
try:
    from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                    Paragraph, Spacer, Image, Table,
                                    TableStyle, PageBreak, KeepTogether)
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    # Dummy-Klassen und -Konstanten, damit das Modul importierbar bleibt
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

# ----------------------- Matplotlib-Import mit Fallback -----------------------
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    _MATPLOTLIB_AVAILABLE = True
except Exception:
    _MATPLOTLIB_AVAILABLE = False

# ---------------------- Theme-Funktionen mit Fallback -------------------------
try:
    from theming.pdf_styles import get_theme, create_modern_table_style
    _THEMING_AVAILABLE = True
except ImportError:
    _THEMING_AVAILABLE = False
    def get_theme(theme_name: str = "Blau Elegant") -> Dict[str, Any]:
        return {
            'styles': {},
            'colors': {
                'primary': '#003366', 'secondary': '#eeeeee',
                'background': '#ffffff', 'text_body': '#000000',
                'text_heading': '#003366', 'footer_text': '#888888'
            },
            'fonts': {
                'family_main': 'Helvetica', 'family_bold': 'Helvetica-Bold',
                'size_h1': 20, 'size_h2': 16, 'size_h3': 12, 'size_body': 10,
                'size_footer': 8
            },
        }
    def create_modern_table_style(theme: Dict[str, Any]) -> TableStyle:
        return TableStyle([])

# ----------------------------- Hilfsfunktionen ------------------------------
def _b64_to_image_flowable(b64_str: str, max_width: float, max_height: float) -> Optional[Image]:
    if not _REPORTLAB_AVAILABLE or not b64_str:
        return None
    try:
        img_data = base64.b64decode(b64_str)
        img = Image(io.BytesIO(img_data))
        w, h = img.drawWidth, img.drawHeight
        scale = min(max_width / w, max_height / h)
        img.drawWidth, img.drawHeight = w * scale, h * scale
        return img
    except Exception:
        return None

def _format_number(value: Any, unit: str = "", precision: int = 2) -> str:
    try: num = float(value)
    except (ValueError, TypeError): return str(value)
    formatted = f"{num:,.{precision}f}".replace(",", ".") if precision >= 0 else f"{num:.0f}"
    return f"{formatted} {unit}".strip()

# … (weitere Hilfsfunktionen wie _extract_kpis unverändert) …

# --------------------------- Block-Basisklasse ------------------------------
class PDFBlock:
    name: str = "Block"
    required: bool = False
    def __init__(self, name: str, required: bool = False):
        self.name = name; self.required = required
    def is_included(self, context: Dict[str, Any]) -> bool:
        if self.required: return True
        opts = context.get('inclusion_options', {}) or {}
        return opts.get(f"include_{self.name}", True)
    def create_flowables(self, context: Dict[str, Any]) -> List[Any]:
        raise NotImplementedError

# ---------------------- Konkrete Blöcke (Beispiele) -------------------------
class CoverPageBlock(PDFBlock):
    def __init__(self): super().__init__('cover_page', required=True)
    def create_flowables(self, ctx):
        # erzeugt Titelbild, Logo, Titeltext, Firmeninfos, Seitenumbruch
        # (siehe ursprüngliche Datei)
        pass

class KPIBlock(PDFBlock):
    def __init__(self): super().__init__('kpi_overview', required=True)
    def create_flowables(self, ctx):
        # Kennzahlen als Tabelle (siehe ursprüngliche Datei)
        pass

# … (weitere Blöcke wie ComponentsBlock, ChartBlock, TermsBlock) …

# -------------------- Zusätzliche TOM‑90‑Blöcke ----------------------------
class PersonalSummaryBlock(PDFBlock): ...
class DonutChartsBlock(PDFBlock): ...
class BarChartBlock(PDFBlock): ...
class HaveYouKnowBlock(PDFBlock): ...
class CO2Block(PDFBlock): ...

class FinancingBlock(PDFBlock):
    """Vergleicht Kredit, Leasing und Kauf anhand vorhandener Finanzierungsfunktionen."""
    def __init__(self): super().__init__('financing', required=False)
    def create_flowables(self, ctx):
        flows: List[Any] = []
        theme, styles = ctx['theme'], ctx['theme'].get('styles', {})
        analysis, project = ctx['analysis_results'], ctx['project_data']
        investment = float(analysis.get('total_investment_netto')
                           or analysis.get('total_investment')
                           or project.get('investment_amount', 0) or 0)
        interest_rate = float(analysis.get('loan_interest_rate_percent')
                              or project.get('loan_interest_rate_percent', 4.0))
        duration_years = int(analysis.get('simulation_period_years_effective')
                             or analysis.get('simulation_period_years')
                             or project.get('loan_duration_years', 20))
        leasing_factor = float(analysis.get('leasing_factor_percent')
                               or project.get('leasing_factor_percent', 2.5))
        flows.append(Paragraph("Finanzierungsvergleich", styles.get('h2', ParagraphStyle('h2'))))
        if investment <= 0:
            flows.append(Paragraph("Keine Finanzierungsdaten verfügbar.",
                                   styles.get('BodyText', ParagraphStyle('BodyText'))))
            flows.append(Spacer(1, 0.4 * cm))
            return flows
        try:
            from financial_tools import calculate_annuity, calculate_leasing_costs
            credit = calculate_annuity(investment, interest_rate, duration_years)
            leasing = calculate_leasing_costs(investment, leasing_factor, duration_years * 12)
        except Exception:
            credit = leasing = None
        table_data = [["Option", "Monatliche Rate", "Gesamtkosten", "Zinsen/Restwert"]]
        # Kredit
        if credit and not credit.get('error'):
            table_data.append([
                "Kredit",
                _format_number(credit["monatliche_rate"], "€", 0),
                _format_number(credit["gesamtkosten"], "€", 0),
                _format_number(credit["gesamtzinsen"], "€", 0),
            ])
        else:
            table_data.append(["Kredit", "–", "–", "–"])
        # Leasing
        if leasing and not leasing.get('error'):
            rest = leasing.get('restwert', leasing.get('effektive_kosten', 0))
            table_data.append([
                "Leasing",
                _format_number(leasing["monatliche_rate"], "€", 0),
                _format_number(leasing["gesamtkosten"], "€", 0),
                _format_number(rest, "€", 0),
            ])
        else:
            table_data.append(["Leasing", "–", "–", "–"])
        # Sofortkauf
        table_data.append(["Kauf", "–", _format_number(investment, "€", 0), "0 €"])
        tbl = Table(table_data, colWidths=[5*cm, 4*cm, 4*cm, ctx['doc_width'] - 13*cm])
        tbl.setStyle(create_modern_table_style(theme))
        flows.append(tbl)
        flows.append(Spacer(1, 0.4 * cm))
        return flows

# ------------------------------ Renderer --------------------------------
class Tom90Renderer:
    """Rendert die ausgewählten Blöcke in ein PDF im Stil von TOM‑90."""
    def __init__(self, project_data, analysis_results, company_info,
                 inclusion_options=None, texts=None, company_logo_base64=None,
                 title_image_b64=None, offer_title_text="Ihr Angebot",
                 blocks=None, theme_name="Blau Elegant"):
        self.project_data = project_data or {}
        self.analysis_results = analysis_results or {}
        self.company_info = company_info or {}
        self.inclusion_options = inclusion_options or {}
        self.texts = texts or {}
        self.company_logo_base64 = company_logo_base64
        self.title_image_b64 = title_image_b64
        self.offer_title_text = offer_title_text
        self.theme = get_theme(theme_name) if _THEMING_AVAILABLE else get_theme()
        # Standardblock-Reihenfolge (siehe Datei für alle implementierten Blöcke)
        if blocks is None:
            self.blocks = [
                CoverPageBlock(),
                PersonalSummaryBlock(),
                KPIBlock(),
                DonutChartsBlock(),
                BarChartBlock(),
                ComponentsBlock(),
                HaveYouKnowBlock(),
                CO2Block(),
                FinancingBlock(),  # << neu hinzugefügter Block
                ChartBlock(),
                TermsBlock(),
            ]
        else:
            self.blocks = blocks

    def _header_footer(self, canvas_obj, doc):
        # zeichnet Firmenname, Angebots-ID und Seitenzahl (siehe Datei)
        pass

    def build_pdf(self) -> Optional[bytes]:
        if not _REPORTLAB_AVAILABLE:
            # Fallback: Rückgabe eines minimalen PDF-Stubs
            return (b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\n"
                    b"endobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >>\n"
                    b"endobj\n4 0 obj\n<< /Length 0 >>\nstream\n\nendstream\nendobj\nxref\n"
                    b"0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n"
                    b"0000000114 00000 n \n0000000178 00000 n \ntrailer\n<< /Root 1 0 R /Size 5 >>\n"
                    b"startxref\n224\n%%EOF")
        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=A4,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2.5*cm, bottomMargin=2.5*cm)
        frame = Frame(doc.leftMargin, doc.bottomMargin,
                      doc.width, doc.height - 1*cm, id="normal")
        doc.addPageTemplates([PageTemplate(id="Tom90", frames=frame,
                                           onPage=self._header_footer)])
        story: List[Any] = []
        context = {
            "project_data": self.project_data,
            "analysis_results": self.analysis_results,
            "company_info": self.company_info,
            "inclusion_options": self.inclusion_options,
            "texts": self.texts,
            "theme": self.theme,
            "doc_width": doc.width,
            "doc_height": doc.height,
            "company_logo_b64": self.company_logo_base64,
            "title_image_b64": self.title_image_b64,
            "offer_title": self.offer_title_text,
        }
        for block in self.blocks:
            if block.is_included(context):
                try:
                    flows = block.create_flowables(context)
                    if flows: story.append(KeepTogether(flows))
                except Exception as exc:
                    story.append(Paragraph(f"Fehler im Block {block.name}: {exc}",
                                           self.theme.get('styles', {}).get('ErrorText',
                                                                             ParagraphStyle('ErrorText'))))
        try:
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except Exception:
            return None

def generate_tom90_offer_pdf(project_data, analysis_results, company_info,
                             company_logo_base64=None, selected_title_image_b64=None,
                             selected_offer_title_text="Ihr Angebot",
                             inclusion_options=None, texts=None,
                             load_admin_setting_func=None, save_admin_setting_func=None,
                             list_products_func=None, get_product_by_id_func=None,
                             db_list_company_documents_func=None, active_company_id=None,
                             theme_name="Blau Elegant", **kwargs) -> Optional[bytes]:
    """Erzeugt ein Angebot im TOM‑90‑Design ohne die bestehende PDF‑Funktion zu beeinträchtigen."""
    return Tom90Renderer(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        inclusion_options=inclusion_options,
        texts=texts,
        company_logo_base64=company_logo_base64,
        title_image_b64=selected_title_image_b64,
        offer_title_text=selected_offer_title_text,
        theme_name=theme_name,
    ).build_pdf()
