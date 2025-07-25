"""
Datei: pdf_generator.py
Zweck: Erzeugt Angebots-PDFs für die Solar-App.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-03
"""
from __future__ import annotations

# pdf_generator.py
import os
import io
import plotly.graph_objects as go
import pandas as pd
import base64
import io
import math
import traceback
import math
import traceback
from calculations_extended import run_all_extended_analyses
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from theming.pdf_styles import get_theme
from theming.pdf_styles import create_modern_table_style

# Optional PDF Templates import
try:
    from pdf_templates import get_cover_letter_template, get_project_summary_template
    _PDF_TEMPLATES_AVAILABLE = True
except ImportError:
    _PDF_TEMPLATES_AVAILABLE = False
    # Fallback functions
    def get_cover_letter_template(*args, **kwargs):
        return None
    def get_project_summary_template(*args, **kwargs):
        return None
_REPORTLAB_AVAILABLE = False
_PYPDF_AVAILABLE = False

try:
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
        Table, TableStyle, PageBreak, KeepTogether, Flowable, SimpleDocTemplate
    )
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    
    from reportlab.lib import pagesizes
    _REPORTLAB_AVAILABLE = True
except ImportError:
    pass
except Exception as e_reportlab_import:
    pass

try:
    from pypdf import PdfReader, PdfWriter
    _PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        _PYPDF_AVAILABLE = True
    except ImportError:
        class PdfReader: # type: ignore
            def __init__(self, *args, **kwargs): pass
            @property
            def pages(self): return []
        class PdfWriter: # type: ignore
            def __init__(self, *args, **kwargs): pass
            def add_page(self, page): pass
            def write(self, stream): pass
        _PYPDF_AVAILABLE = False
except Exception as e_pypdf_import:
    class PdfReader: # type: ignore
        def __init__(self, *args, **kwargs): pass
        @property
        def pages(self): return []
    class PdfWriter: # type: ignore
        def __init__(self, *args, **kwargs): pass
        def add_page(self, page): pass
        def write(self, stream): pass
    _PYPDF_AVAILABLE = False
try:
    from theming.pdf_styles import get_theme, create_modern_table_style
except ImportError:
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import TableStyle

    def get_theme(theme_name=""):
        return {
            "styles": getSampleStyleSheet(),
            "colors": {
                "primary": colors.HexColor("#0d3780"),      # Moderne Farbe aus JSON-Vorlage
                "secondary": colors.HexColor("#0081b8"),    # Hellblau aus JSON-Vorlage
                "accent": colors.HexColor("#f6f6f6"),       # Hellgrau für Boxen aus JSON-Vorlage
                "text": colors.HexColor("#333333"),         # Dunkles Grau für Text aus JSON-Vorlage
                "light_gray": colors.HexColor("#e8e8e8"),   # Helle Linien aus JSON-Vorlage
                "white": colors.white,                      # Weiß
                # Ihre ursprünglichen Farben als Fallback
                "original_primary": colors.HexColor("#003366"),
                "original_text": colors.HexColor("#2C2C2C"),
                "original_secondary": colors.HexColor("#EFEFEF")
            },
            "fonts": {
                "family_bold": "Helvetica-Bold",
                "family_main": "Helvetica",
                "size_h1": 18,
                "size_body": 10
            }
        }

    def create_modern_table_style(theme):
        return TableStyle([])    

# MODERNE HILFSFUNKTIONEN für JSON-Vorlage Design (Ergänzung zu Ihrem bestehenden Code)
def create_modern_kennzahl_card(percentage: int, label: str, width: float, theme):
    """Erstellt eine moderne Kennzahl-Karte wie in Ihrer JSON-Vorlage"""
    if not _REPORTLAB_AVAILABLE:
        return None
        
    card_data = [[f"<b><font size='24'>{percentage}%</font></b><br/>{label}"]]
    
    card_table = Table(card_data, colWidths=[width])
    card_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), theme["colors"]["secondary"]),
        ('TEXTCOLOR', (0, 0), (-1, -1), theme["colors"]["white"]),
        ('FONTNAME', (0, 0), (-1, -1), theme["fonts"]["family_bold"]),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('BOX', (0, 0), (-1, -1), 2, theme["colors"]["primary"])
    ]))
    
    return card_table

def create_modern_system_data_box(data: list, width: float, theme):
    """Erstellt eine moderne Systemdaten-Box wie in Ihrer JSON-Vorlage"""
    if not _REPORTLAB_AVAILABLE:
        return None
        
    system_table = Table(data, colWidths=[width * 0.4, width * 0.6])
    system_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), theme["fonts"]["family_bold"]),
        ('FONTNAME', (1, 0), (1, -1), theme["fonts"]["family_main"]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), theme["colors"]["text"]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, theme["colors"]["light_gray"])
    ]))
    
    return system_table    
    
class PDFGenerator:
    """Kapselt die gesamte PDF-Erstellungslogik."""

    def __init__(self, project_data, analysis_results, company_info, texts, theme_name, inclusion_options, section_order_df, custom_images_list, custom_text_blocks_list, side_by_side_sim_keys, highlight_box_data, get_product_by_id_func, db_list_company_documents_func, active_company_id, selected_title_image_b64, selected_offer_title_text, selected_cover_letter_text):
        self.project_data = project_data
        self.analysis_results = analysis_results
        self.company_info = company_info
        self.texts = texts
        self.theme = get_theme(theme_name)
        self.styles = self.theme['styles']
        self.inclusion_options = inclusion_options
        self.section_order_df = section_order_df
        self.custom_images_list = custom_images_list
        self.custom_text_blocks_list = custom_text_blocks_list
        self.side_by_side_sim_keys = side_by_side_sim_keys
        self.highlight_box_data = highlight_box_data
        self.get_product_by_id_func = get_product_by_id_func
        self.db_list_company_documents_func = db_list_company_documents_func
        self.active_company_id = active_company_id
        self.selected_title_image_b64 = selected_title_image_b64
        self.selected_offer_title_text = selected_offer_title_text
        self.selected_cover_letter_text = selected_cover_letter_text
        self.story = []

        # Eigene Stile basierend auf dem Theme erstellen - mit Fallbacks
        try:
            self.styles.add(ParagraphStyle(name='H1', fontName=self.theme["fonts"]["family_bold"],
                                            fontSize=self.theme["fonts"]["size_h1"],
                                            textColor=self.theme["colors"]["primary"]))
            self.styles.add(ParagraphStyle(name='Body', fontName=self.theme["fonts"]["family_main"],
                                            fontSize=self.theme["fonts"]["size_body"],
                                            textColor=self.theme["colors"]["text"]))
            
            # Zusätzliche Stile für PDF-Generierung
            self.styles.add(ParagraphStyle(name='Title', fontName=self.theme["fonts"]["family_bold"],
                                            fontSize=24, textColor=self.theme["colors"]["primary"],
                                            alignment=TA_CENTER, spaceAfter=20))
            self.styles.add(ParagraphStyle(name='OfferTitle', fontName=self.theme["fonts"]["family_bold"],
                                            fontSize=22, textColor=self.theme["colors"]["primary"],
                                            alignment=TA_CENTER, spaceAfter=15))
            self.styles.add(ParagraphStyle(name='Heading2', fontName=self.theme["fonts"]["family_bold"],
                                            fontSize=16, textColor=self.theme["colors"]["text"],
                                            spaceBefore=10, spaceAfter=8))
            self.styles.add(ParagraphStyle(name='SectionTitle', fontName=self.theme["fonts"]["family_bold"],
                                            fontSize=18, textColor=self.theme["colors"]["primary"],
                                            spaceBefore=15, spaceAfter=10))
            self.styles.add(ParagraphStyle(name='Normal', fontName=self.theme["fonts"]["family_main"],
                                            fontSize=12, textColor=self.theme["colors"]["text"],
                                            leading=14))
            self.styles.add(ParagraphStyle(name='CoverLetter', fontName=self.theme["fonts"]["family_main"],
                                            fontSize=11, textColor=self.theme["colors"]["text"],
                                            leading=16, alignment=TA_JUSTIFY))
        except Exception as e:
            print(f"Warnung: Fehler beim Erstellen der PDF-Stile: {e}")
            # Fallback zu Standard-Stilen
            pass

    def _header_footer(self, canvas, doc):
        """Erstellt die Kopf- und Fußzeile für jede Seite."""
        canvas.saveState()
        # Footer
        canvas.setFont(self.theme["fonts"]["family_main"], self.theme["fonts"]["size_footer"])
        canvas.setFillColor(HexColor(self.theme["colors"]["footer_text"]))
        footer_text = f"Angebot {self.offer_data.get('offer_id', '')} | Seite {doc.page}"
        canvas.drawRightString(self.width - 2*cm, 1.5*cm, footer_text)
        canvas.restoreState()

    def create_pdf(self):
        """Hauptfunktion, die alle Module zusammensetzt und das PDF speichert."""
        doc = SimpleDocTemplate(self.filename, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        module_map = self._get_module_map()

        for module_spec in self.module_order:
            module_id = module_spec["id"]
            draw_function = module_map.get(module_id)
            if draw_function:
                if module_id == "benutzerdefiniert":
                    draw_function(module_spec.get("content", {}))
                else:
                    draw_function()
                self.story.append(PageBreak())
        
        # Entferne den letzten PageBreak, um keine leere Seite zu erzeugen
        if self.story and isinstance(self.story[-1], PageBreak):
            self.story.pop()
            
        doc.build(self.story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)

    def _draw_cover_page(self):
        self.story.append(Spacer(1, 8*cm))
        self.story.append(Paragraph("Angebot", self.styles['H1']))
        self.story.append(Spacer(1, 0.5*cm))
        customer = self.offer_data.get("customer", {})
        self.story.append(Paragraph(f"für {customer.get('name', 'N/A')}", self.styles['Body']))
        self.story.append(Paragraph(f"Datum: {self.offer_data.get('date', 'N/A')}", self.styles['Body']))
        
    def _draw_cover_letter(self):
        text = get_cover_letter_template(
            customer_name=self.offer_data.get("customer", {}).get("name", "N/A"),
            offer_id=self.offer_data.get("offer_id", "N/A")
        ).replace('\n', '<br/>')
        self.story.append(Paragraph("Ihr persönliches Angebot", self.styles['H1']))
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph(text, self.styles['Body']))

    def _draw_offer_table(self):
        self.story.append(Paragraph("Angebotspositionen", self.styles['H1']))
        self.story.append(Spacer(1, 1*cm))

        data = [["Pos", "Beschreibung", "Menge", "Einzelpreis", "Gesamtpreis"]]
        items = self.offer_data.get("items", [])
        for i, item in enumerate(items):
            data.append([
                str(i + 1),
                item.get("name", "N/A"),
                str(item.get("quantity", 0)),
                f"{item.get('unit_price', 0):.2f} €",
                f"{item.get('total_price', 0):.2f} €"
            ])
        
        data.append(["", "", "", "Netto:", f"{self.offer_data.get('net_total', 0):.2f} €"])
        data.append(["", "", "", "MwSt. 19%:", f"{self.offer_data.get('vat', 0):.2f} €"])
        data.append(["", "", "", Paragraph("<b>Gesamt</b>", self.styles['Body']), f"{self.offer_data.get('grand_total', 0):.2f} €"])

        table = Table(data, colWidths=[1.5*cm, 8*cm, 2*cm, 2.5*cm, 3*cm])
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(self.theme["colors"]["table_header_bg"])),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(self.theme["colors"]["header_text"])),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.theme["fonts"]["family_bold"]),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), HexColor(self.theme["colors"]["table_row_bg_odd"])),
            ('GRID', (0,0), (-1,-3), 1, HexColor(self.theme["colors"]["primary"])),
            ('ALIGN', (1,1), (1,-1), 'LEFT'), # Beschreibung linksbündig
        ])
        table.setStyle(style)
        self.story.append(table)

    # In pdf_generator.py, innerhalb der Klasse PDFGenerator

    # ... zu den anderen draw-Methoden hinzufügen
    def _draw_heatpump_section(self):
        if 'selected_heatpump_data' not in self.offer_data:
            return # Modul überspringen, wenn keine Daten vorhanden

        data = self.offer_data['selected_heatpump_data']
        
        self.story.append(Paragraph("Analyse Wärmepumpe", self.styles['H1']))
        self.story.append(Spacer(1, 1*cm))
        
        text = f"""
        Basierend auf Ihren Gebäudedaten wurde eine Heizlast von <b>{self.offer_data.get('heat_load_kw', 0):.2f} kW</b> ermittelt.
        Wir empfehlen folgendes Modell:
        <br/><br/>
        <b>Hersteller:</b> {data['manufacturer']}<br/>
        <b>Modell:</b> {data['model_name']}<br/>
        <b>Heizleistung:</b> {data['heating_output_kw']:.2f} kW<br/>
        <b>Jahresarbeitszahl (SCOP):</b> {data['scop']:.2f}<br/>
        <b>Geschätzter jährl. Stromverbrauch:</b> {data.get('annual_consumption', 0):.0f} kWh
        """
        self.story.append(Paragraph(text, self.styles['Body']))

    def _draw_modern_kennzahlen_section(self):
        """Erstellt moderne Kennzahlen-Karten im Stil Ihrer JSON-Vorlage (Erweiterung zu Ihrem bestehenden System)"""
        if not _REPORTLAB_AVAILABLE:
            return
            
        # Berechne Kennzahlen aus Ihren bestehenden Daten
        analysis = self.analysis_results or {}
        annual_production = float(analysis.get("annual_pv_production_kwh", 8251))
        annual_consumption = float(analysis.get("annual_consumption_kwh", 6000))
        self_consumption_kwh = float(analysis.get("self_consumption_kwh", annual_production * 0.42))
        
        eigenverbrauch_prozent = int((self_consumption_kwh / annual_production) * 100) if annual_production > 0 else 42
        unabhaengigkeit_prozent = int((self_consumption_kwh / annual_consumption) * 100) if annual_consumption > 0 else 54
        
        # Titel für die moderne Sektion
        self.story.append(Paragraph("<b>KENNZAHLEN IHRES PV-SYSTEMS</b> (Moderne Darstellung)", self.styles['H1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Erstelle moderne Kennzahl-Karten
        kennzahl_table_data = [[
            f"<b><font size='20'>{unabhaengigkeit_prozent}%</font></b><br/>Unabhängigkeitsgrad",
            f"<b><font size='20'>{eigenverbrauch_prozent}%</font></b><br/>Eigenverbrauch"
        ]]
        
        kennzahl_table = Table(kennzahl_table_data, colWidths=[9*cm, 9*cm])
        kennzahl_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), self.theme["colors"]["secondary"]),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.theme["colors"]["white"]),
            ('FONTNAME', (0, 0), (-1, -1), self.theme["fonts"]["family_bold"]),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, self.theme["colors"]["primary"])
        ]))
        
        self.story.append(kennzahl_table)
        self.story.append(Spacer(1, 1*cm))
        
        # Systemdaten in moderner Box
        project_details = self.project_data.get("project_details", {}) if self.project_data else {}
        anlage_kwp = float(analysis.get("anlage_kwp", 8.4))
        battery_capacity = float(project_details.get("battery_capacity_kwh", 6.1))
        
        system_data = [
            ["Verbrauch:", f"{annual_consumption:,.0f} kWh/Jahr"],
            ["Dachneigung:", "30°"],
            ["Solaranlage:", f"{anlage_kwp:.1f} kWp"],
            ["Batterie:", f"{battery_capacity:.1f} kWh"],
            ["Jahresertrag:", f"{annual_production:,.0f} kWh/Jahr"]
        ]
        
        system_table = create_modern_system_data_box(system_data, 16*cm, self.theme)
        if system_table:
            self.story.append(Paragraph("<b>IHR NEUES ENERGIESYSTEM</b> (Moderne Darstellung)", self.styles['H2']))
            self.story.append(Spacer(1, 0.5*cm))
            self.story.append(system_table)
            self.story.append(Spacer(1, 1*cm))

    def _get_module_map(self):
        """Gibt die Mapping-Funktion für PDF-Module zurück."""
        return {
            "deckblatt": self._draw_cover_page,
            "anschreiben": self._draw_cover_letter,
            "angebotstabelle": self._draw_offer_table,
            "benutzerdefiniert": self._draw_custom_content,
            "waermepumpe": self._draw_heatpump_section,
            "moderne_kennzahlen": self._draw_modern_kennzahlen_section,  # Neue moderne Sektion hinzugefügt
        }

    def _draw_custom_content(self, content: Dict):
        content_type = content.get("type", "text")
        data = content.get("data")
        if not data: return

        if content_type == "image":
            try:
                self.story.append(Image(data, width=self.width - 4*cm, height=self.height/3, preserveAspectRatio=True))
            except Exception as e:
                self.story.append(Paragraph(f"Fehler beim Laden des Bildes: {e}", self.styles['Body']))
    
    def merge_pdfs(self, pdf_files: List[Union[str, bytes, io.BytesIO]]) -> bytes:
        """
        Führt mehrere PDF-Dateien zu einer einzigen zusammen.
        
        Args:
            pdf_files: Liste von PDF-Dateien (Pfade, Bytes oder BytesIO-Objekte)
            
        Returns:
            bytes: Die zusammengeführte PDF als Bytes
        """
        if not _PYPDF_AVAILABLE:
            raise RuntimeError("PyPDF ist nicht verfügbar für das Zusammenführen von PDFs")
            
        if not pdf_files:
            return b""
            
        merger = PdfWriter()
        
        try:
            for pdf_file in pdf_files:
                if isinstance(pdf_file, str):
                    # Pfad zu PDF-Datei
                    if os.path.exists(pdf_file):
                        with open(pdf_file, 'rb') as f:
                            reader = PdfReader(f)
                            for page in reader.pages:
                                merger.add_page(page)
                elif isinstance(pdf_file, bytes):
                    # PDF als Bytes
                    reader = PdfReader(io.BytesIO(pdf_file))
                    for page in reader.pages:
                        merger.add_page(page)
                elif isinstance(pdf_file, io.BytesIO):
                    # PDF als BytesIO
                    pdf_file.seek(0)  # Sicherstellung, dass wir am Anfang sind
                    reader = PdfReader(pdf_file)
                    for page in reader.pages:
                        merger.add_page(page)
                        
            # Zusammengeführte PDF in BytesIO schreiben
            output = io.BytesIO()
            merger.write(output)
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            # Fallback: Erste PDF zurückgeben wenn verfügbar
            if pdf_files:
                first_pdf = pdf_files[0]
                if isinstance(first_pdf, str) and os.path.exists(first_pdf):
                    with open(first_pdf, 'rb') as f:
                        return f.read()
                elif isinstance(first_pdf, bytes):
                    return first_pdf
                elif isinstance(first_pdf, io.BytesIO):
                    first_pdf.seek(0)
                    return first_pdf.getvalue()
            return b""

    def generate_pdf(self) -> Optional[bytes]:
        if not _REPORTLAB_AVAILABLE: return None

        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
        
        # PageTemplate hinzufügen (erforderlich für BaseDocTemplate)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='normal', frames=[frame])
        doc.addPageTemplates([template])
        
        doc.onFirstPage = lambda canvas, doc: _draw_page_statics(canvas, doc, self.theme)
        doc.onLaterPages = lambda canvas, doc: _draw_page_statics(canvas, doc, self.theme)

        # --- Story-Aufbau ---
        if self.theme.get('name') == "Salt & Pepper":
            self._build_salt_and_pepper_story()
        else:
            self._build_dynamic_story()

        try:
            doc.build(self.story)
            main_pdf_bytes = buffer.getvalue()
        except Exception as e:
            print(f"FATALER FEHLER bei doc.build: {e}"); traceback.print_exc(); return None
        finally:
            buffer.close()

        # --- Anhänge verwalten ---
        final_pdf_bytes = self._handle_attachments(main_pdf_bytes)
        return final_pdf_bytes

    def _build_dynamic_story(self):
        # Story initialisieren
        if not hasattr(self, 'story') or self.story is None:
            self.story = []
        
        # Dynamische Story basierend auf Nutzer-Reihenfolge
        # Unterstützung für sowohl DataFrame als auch Liste
        if hasattr(self.section_order_df, 'iterrows'):
            # DataFrame
            for index, row in self.section_order_df.iterrows():
                if not row.get('Aktiv', True): continue
                section_name_friendly = row['Sektion']
                self._process_section(section_name_friendly)
        else:
            # Liste - kann Strings oder Dictionaries enthalten
            for row in self.section_order_df:
                if isinstance(row, str):
                    # Direkt String verwenden
                    section_name_friendly = row
                    self._process_section(section_name_friendly)
                elif isinstance(row, dict):
                    # Dictionary - prüfe Aktiv-Status
                    if not row.get('Aktiv', True): continue
                    section_name_friendly = row.get('Sektion', '')
                    self._process_section(section_name_friendly)
                else:
                    # Unbekannter Typ - überspringen
                    continue
        
        # Fallback: Wenn keine Story erstellt wurde, füge Standard-Inhalt hinzu
        if not self.story:
            self._add_fallback_content()
    
    def _process_section(self, section_name_friendly):
        """Verarbeitet eine einzelne Sektion basierend auf dem Namen"""
        # Debugging: Zeige verarbeitete Sektion an
        print(f"Verarbeite Sektion: '{section_name_friendly}'")
        
        # Unterstützung für all_sections_map Namen
        if section_name_friendly == "Titel & Anschreiben" or section_name_friendly == "TitlePageCoverLetter":
            self._add_title_page()
            self._add_cover_letter_section()
        elif section_name_friendly == "Kennzahlen-Übersicht (Donuts)" or section_name_friendly == "KeyVisuals":
            self._add_key_visuals_section()
        elif section_name_friendly == "Technische Komponenten" or section_name_friendly == "TechnicalComponents":
            self._add_technical_components_section()
        elif section_name_friendly == "Wirtschaftlichkeits-Analyse" or section_name_friendly == "MainCharts":
            self._add_economics_section()
        elif section_name_friendly == "Kosten & Tabellen" or section_name_friendly == "CostsAndEconomics":
            self._add_costs_section()
        elif section_name_friendly == "Weitere Diagramme" or section_name_friendly == "OptionalCharts":
            self._add_charts_section()
        
        # Unterstützung für default_pdf_sections_map Namen
        elif section_name_friendly == "1. Projektübersicht" or section_name_friendly == "ProjectOverview":
            self._add_project_overview_section()
        elif section_name_friendly == "2. Systemkomponenten":
            self._add_technical_components_section()
        elif section_name_friendly == "3. Kostenaufstellung" or section_name_friendly == "CostDetails":
            self._add_costs_section()
        elif section_name_friendly == "4. Wirtschaftlichkeit" or section_name_friendly == "Economics":
            self._add_economics_section()
        elif section_name_friendly == "5. Simulation" or section_name_friendly == "SimulationDetails":
            self._add_simulation_section()
        elif section_name_friendly == "6. CO₂-Einsparung" or section_name_friendly == "CO2Savings":
            self._add_co2_section()
        elif section_name_friendly == "7. Grafiken" or section_name_friendly == "Visualizations":
            self._add_charts_section()
        elif section_name_friendly == "8. Zukunftsaspekte" or section_name_friendly == "FutureAspects":
            self._add_future_aspects_section()
        
        # Neue optionale Business-Sektionen (wie in pdf_generator.py definiert)
        elif section_name_friendly == "9. Unser Unternehmen" or section_name_friendly == "CompanyProfile":
            self._add_company_profile_section()
        elif section_name_friendly == "10. Zertifizierungen & Qualitätsstandards" or section_name_friendly == "Certifications":
            self._add_certifications_section()
        elif section_name_friendly == "11. Referenzen & Kundenerfahrungen" or section_name_friendly == "References":
            self._add_references_section()
        elif section_name_friendly == "12. Professionelle Installation" or section_name_friendly == "Installation":
            self._add_installation_section()
        elif section_name_friendly == "13. Wartung & Langzeitservice" or section_name_friendly == "Maintenance":
            self._add_maintenance_section()
        elif section_name_friendly == "14. Flexible Finanzierungslösungen" or section_name_friendly == "Financing":
            self._add_financing_section()
        elif section_name_friendly == "15. Umfassender Versicherungsschutz" or section_name_friendly == "Insurance":
            self._add_insurance_section()
        elif section_name_friendly == "16. Herstellergarantie & Gewährleistung" or section_name_friendly == "Warranty":
            self._add_warranty_section()
        else:
            # Fallback für unbekannte Sektionen
            print(f"Unbekannte Sektion: '{section_name_friendly}' - verwende Fallback")
            self._add_generic_section(section_name_friendly)

    def _add_title_page(self):
        """Fügt die Titelseite hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
        
        # Titel-Bild oder Standard-Titel
        if hasattr(self, 'selected_title_image_b64') and self.selected_title_image_b64:
            try:
                import base64
                import io
                from reportlab.platypus import Image
                image_data = base64.b64decode(self.selected_title_image_b64)
                img = Image(io.BytesIO(image_data), width=15*cm, height=10*cm)
                self.story.append(img)
            except Exception as e:
                # Fallback zu Text-Titel
                from reportlab.platypus import Paragraph, Spacer
                from reportlab.lib.units import cm
                self.story.append(Spacer(1, 5*cm))
                if hasattr(self, 'selected_offer_title_text'):
                    title_text = self.selected_offer_title_text or "Solar-Angebot"
                else:
                    title_text = "Solar-Angebot"
                self.story.append(Paragraph(title_text, self.styles.get('OfferTitle', self.styles.get('Title'))))
        else:
            from reportlab.platypus import Paragraph, Spacer
            from reportlab.lib.units import cm
            self.story.append(Spacer(1, 5*cm))
            if hasattr(self, 'selected_offer_title_text'):
                title_text = self.selected_offer_title_text or "Solar-Angebot"
            else:
                title_text = "Solar-Angebot"
            self.story.append(Paragraph(title_text, self.styles.get('OfferTitle', self.styles.get('Title'))))

    def _add_cover_letter_section(self):
        """Fügt das Anschreiben hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer, PageBreak
        from reportlab.lib.units import cm
        
        self.story.append(PageBreak())
        self.story.append(Paragraph("Anschreiben", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Kundenadresse aus den Daten
        customer_data = self.project_data.get('customer_data', {})
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        customer_address = f"{customer_data.get('address', '')}, {customer_data.get('zip_code', '')} {customer_data.get('city', '')}".strip()
        
        # Personalisiertes Anschreiben mit echten Daten
        analysis = self.analysis_results
        anlage_kwp = analysis.get('anlage_kwp', 0)
        annual_savings = analysis.get('annual_financial_benefit_year1', 0)
        co2_savings = analysis.get('annual_co2_savings_kg', 0) / 1000
        total_investment = analysis.get('total_investment_netto', 0)
        
        # Berechne geschätzte Amortisation realistisch
        amortization_years = analysis.get('amortization_time_years', 0)
        if amortization_years > 25 or amortization_years <= 0:
            amortization_years = analysis.get('simple_payback_years', 
                                            total_investment / max(annual_savings, 1000) if annual_savings > 0 else 12)
        
        if hasattr(self, 'selected_cover_letter_text') and self.selected_cover_letter_text:
            cover_text = self.selected_cover_letter_text
        else:
            cover_text = f"""
            Sehr geehrte/r {customer_name or 'Damen und Herren'},<br/><br/>
            
            vielen Dank für Ihr Interesse an einer Photovoltaikanlage. Nach eingehender Analyse Ihrer 
            Gegebenheiten unterbreiten wir Ihnen hiermit unser maßgeschneidertes Angebot für eine 
            hochwertige Solarlösung an Ihrem Standort {customer_address or 'in Ihrer Region'}.<br/><br/>
            
            <b>🌟 Ihre Vorteile im Überblick:</b><br/>
            • <b>💡 Anlagenleistung:</b> {anlage_kwp:.1f} kWp - optimal dimensioniert für Ihren Energiebedarf<br/>
            • <b>💰 Jährliche Ersparnis:</b> ca. {annual_savings:,.0f} € ab dem ersten Jahr<br/>
            • <b>🌱 Umweltbeitrag:</b> {co2_savings:.1f} Tonnen CO₂-Einsparung pro Jahr<br/>
            • <b>⏱️ Amortisation:</b> Ihre Investition amortisiert sich in ca. {amortization_years:.1f} Jahren<br/>
            • <b>🏠 Wertsteigerung:</b> Nachhaltige Erhöhung Ihres Immobilienwerts<br/>
            • <b>🔋 Energieunabhängigkeit:</b> Reduzierung Ihrer Abhängigkeit von Strompreiserhöhungen<br/><br/>
            
            <b>📋 Unser Service für Sie:</b><br/>
            ✓ Komplettlösung aus einer Hand - von der Planung bis zur Inbetriebnahme<br/>
            ✓ Hochwertige Komponenten mit Langzeitgarantie<br/>
            ✓ Professionelle Installation durch zertifizierte Fachkräfte<br/>
            ✓ Umfassende Beratung zu Förderungen und Finanzierungsmöglichkeiten<br/><br/>
            
            Das vorliegende Angebot basiert auf Ihren Angaben und unserer jahrelangen Expertise 
            im Bereich erneuerbarer Energien. Gerne besprechen wir alle Details persönlich mit 
            Ihnen und beantworten Ihre Fragen in einem unverbindlichen Beratungsgespräch.<br/><br/>
            
            Wir freuen uns darauf, Sie auf Ihrem Weg zur eigenen, sauberen Energie zu begleiten!<br/><br/>
            
            Mit freundlichen Grüßen<br/>
            <b>Ihr Solar-Experten-Team</b>
            """
        
        self.story.append(Paragraph(cover_text, self.styles.get('CoverLetter', self.styles.get('Normal'))))

    def _add_key_visuals_section(self):
        """Fügt die Kennzahlen-Übersicht hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Kennzahlen-Übersicht", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Echte Kennzahlen aus den aktuellen Daten
        analysis = self.analysis_results
        pv_details = self.project_data.get('pv_details', {})
        
        anlage_kwp = analysis.get('anlage_kwp', 0)
        annual_production = analysis.get('annual_pv_production_kwh', 0)
        co2_savings = analysis.get('annual_co2_savings_kg', 0) / 1000  # in Tonnen
        
        # Verwende konsistente Eigenverbrauchsquote
        self_consumption_rate = analysis.get('self_consumption_rate_percent', 
                                           analysis.get('self_supply_rate_percent', 0))
        
        # Berechne oder schätze Modul-Anzahl
        module_count = pv_details.get('module_quantity', 0)
        if module_count == 0 and anlage_kwp > 0:
            # Schätze basierend auf typischer Modulgröße (420 Wp)
            module_count = max(1, round(anlage_kwp * 1000 / 420))
        
        # Amortisation mit Plausibilitätsprüfung
        amortization_years = analysis.get('amortization_time_years', 0)
        if amortization_years > 25:  # Unrealistisch hoch
            amortization_years = analysis.get('simple_payback_years', 12)
        
        kpi_text = f"""
        <b>🔋 Anlagenleistung:</b> {anlage_kwp:.1f} kWp<br/>
        <b>⚡ Jährlicher Ertrag:</b> {annual_production:,.0f} kWh<br/>
        <b>🌱 CO₂-Einsparung:</b> {co2_savings:.1f} t/Jahr<br/>
        <b>🏠 Eigenverbrauchsquote:</b> {self_consumption_rate:.1f}%<br/>
        <b>📦 PV-Module:</b> {module_count} Stück<br/>
        <b>💰 Amortisation:</b> {amortization_years:.1f} Jahre<br/>
        <b>📈 Autarkiegrad:</b> {analysis.get('self_supply_rate_percent', 0):.1f}%
        """
        self.story.append(Paragraph(kpi_text, self.styles.get('Normal')))

    def _add_technical_components_section(self):
        """Fügt die technischen Komponenten hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Technische Komponenten", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Echte Komponenten-Daten
        pv_details = self.project_data.get('pv_details', {})
        project_details = self.project_data.get('project_details', {})
        
        # Berechne Modul-Anzahl aus Anlagenleistung falls nicht direkt verfügbar
        anlage_kwp = self.analysis_results.get('anlage_kwp', 0)
        module_count = pv_details.get('module_quantity', 0)
        
        # Fallback: Schätze Modul-Anzahl wenn 0
        if module_count == 0 and anlage_kwp > 0:
            # Annahme: Durchschnittliches Modul hat ~400-450 Wp
            estimated_module_power = 420  # Wp
            module_count = max(1, round(anlage_kwp * 1000 / estimated_module_power))
        
        # Versuche Produktdaten über die get_product_by_id_func zu holen
        module_info = "Hochleistungsmodule (420 Wp)"
        inverter_info = "String-Wechselrichter"
        storage_info = ""
        
        try:
            if hasattr(self, 'get_product_by_id_func') and self.get_product_by_id_func:
                # Modul-Informationen
                module_id = project_details.get('selected_module_id')
                if module_id:
                    module_product = self.get_product_by_id_func(module_id)
                    if module_product:
                        module_power = module_product.get('power_wp', 400)
                        module_info = f"{module_product.get('model_name', 'Modul')} ({module_power} Wp)"
                        # Korrigiere Modul-Anzahl basierend auf echten Produktdaten
                        if module_count == 0 and anlage_kwp > 0:
                            module_count = max(1, round(anlage_kwp * 1000 / module_power))
                
                # Wechselrichter-Informationen
                inverter_id = project_details.get('selected_inverter_id')
                if inverter_id:
                    inverter_product = self.get_product_by_id_func(inverter_id)
                    if inverter_product:
                        # Korrigiere kW-Wert (oft falsch als W gespeichert)
                        power_kw = inverter_product.get('power_kw', 0)
                        if power_kw > 100:  # Wahrscheinlich in Watt statt kW
                            power_kw = power_kw / 1000
                        inverter_info = f"{inverter_product.get('model_name', 'Wechselrichter')} ({power_kw:.1f} kW)"
                
                # Speicher-Informationen
                if pv_details.get('include_storage') and project_details.get('selected_storage_id'):
                    storage_id = project_details.get('selected_storage_id')
                    storage_product = self.get_product_by_id_func(storage_id)
                    if storage_product:
                        storage_capacity = storage_product.get('storage_power_kw', storage_product.get('capacity_kwh', 0))
                        storage_info = f"<b>Batteriespeicher:</b> {storage_product.get('model_name', 'Speicher')} ({storage_capacity} kWh)<br/>"
        except Exception as e:
            print(f"Fehler beim Laden der Produktdaten: {e}")
            pass  # Fallback zu Standard-Texten
        
        # Geschätze Werte für realistische Darstellung
        if anlage_kwp > 0:
            estimated_modules = max(module_count, round(anlage_kwp * 1000 / 420))
        else:
            estimated_modules = module_count
            
        components_text = f"""
        <b>PV-Module:</b> {estimated_modules}x {module_info}<br/>
        <b>Gesamtleistung:</b> {anlage_kwp:.1f} kWp<br/>
        <b>Wechselrichter:</b> {inverter_info}<br/>
        {storage_info}<b>Montagesystem:</b> {project_details.get('mounting_type', 'Aufdach-Montage')}<br/>
        <b>Dachausrichtung:</b> {project_details.get('orientation', 'Süd')}<br/>
        <b>Dachneigung:</b> {project_details.get('tilt_angle', '30')}°<br/>
        <b>Überwachung:</b> Smart Monitoring System inkl. App<br/>
        <b>Garantie:</b> 25 Jahre Leistungsgarantie auf Module, 10 Jahre Produktgarantie
        """
        self.story.append(Paragraph(components_text, self.styles.get('Normal')))
    
    def _add_project_overview_section(self):
        """Fügt die Projektübersicht hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Projektübersicht", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Projekt-Informationen
        project_details = self.project_data.get('project_details', {})
        customer_data = self.project_data.get('customer_data', {})
        
        overview_text = f"""
        <b>Kunde:</b> {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}<br/>
        <b>Adresse:</b> {customer_data.get('address', '')}, {customer_data.get('zip_code', '')} {customer_data.get('city', '')}<br/>
        <b>Haustyp:</b> {project_details.get('house_type', 'Nicht angegeben')}<br/>
        <b>Dachtyp:</b> {project_details.get('roof_type', 'Nicht angegeben')}<br/>
        <b>Ausrichtung:</b> {project_details.get('orientation', 'Nicht angegeben')}
        """
        self.story.append(Paragraph(overview_text, self.styles.get('Normal')))

    def _append_documents_to_pdf(self, main_pdf_bytes, document_paths_to_append):
        """Hängt externe PDFs an ein PDF in Bytes an."""
        if not _PYPDF_AVAILABLE or not document_paths_to_append: 
            return main_pdf_bytes
        writer = PdfWriter()
        try:
            writer.append(io.BytesIO(main_pdf_bytes))
            for doc_path in document_paths_to_append:
                if os.path.exists(doc_path):
                    writer.append(doc_path)
            output_buffer = io.BytesIO()
            writer.write(output_buffer)
            return output_buffer.getvalue()
        except Exception as e:
            print(f"Fehler beim Zusammenfügen der PDFs: {e}")
            return main_pdf_bytes
        
    def _add_economics_section(self):
        """Fügt die Wirtschaftlichkeits-Analyse hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Wirtschaftlichkeit", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Wirtschaftlichkeits-Kennzahlen
        analysis = self.analysis_results
        economics_text = f"""
        <b>Gesamtinvestition:</b> {analysis.get('total_investment_netto', 0):,.0f} €<br/>
        <b>Amortisationszeit:</b> {analysis.get('amortization_time_years', 0):.1f} Jahre<br/>
        <b>Eigenverbrauchsquote:</b> {analysis.get('self_supply_rate_percent', 0):.1f}%<br/>
        <b>Jährlicher Nutzen (Jahr 1):</b> {analysis.get('annual_financial_benefit_year1', 0):,.0f} €
        """
        self.story.append(Paragraph(economics_text, self.styles.get('Normal')))

    def _add_costs_section(self):
        """Fügt die Kostenaufstellung hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Kostenaufstellung", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Kosten-Details
        analysis = self.analysis_results
        pv_details = self.project_data.get('pv_details', {})
        
        # Berechne Einzelpreise
        total_investment = analysis.get('total_investment_netto', 0)
        anlage_kwp = analysis.get('anlage_kwp', 0)
        
        # Berechne oder schätze Modul-Anzahl
        module_count = pv_details.get('module_quantity', 0)
        if module_count == 0 and anlage_kwp > 0:
            module_count = max(1, round(anlage_kwp * 1000 / 420))  # 420 Wp pro Modul
        
        # Realistische Kostenverteilung basierend auf aktuellen Marktpreisen
        module_cost_pct = 0.40  # ~40% Module
        inverter_cost_pct = 0.15  # ~15% Wechselrichter
        installation_cost_pct = 0.30  # ~30% Installation & Montage
        other_cost_pct = 0.15  # ~15% Sonstiges (Kabel, Überwachung, etc.)
        
        module_costs = total_investment * module_cost_pct
        inverter_costs = total_investment * inverter_cost_pct
        installation_costs = total_investment * installation_cost_pct
        other_costs = total_investment * other_cost_pct
        
        # Berechne Preis pro Modul realistisch
        price_per_module = module_costs / max(module_count, 1)
        
        costs_text = f"""
        <b>📋 Detaillierte Kostenaufstellung:</b><br/><br/>
        
        <b>🔸 PV-Module:</b> {module_count} Stück à {price_per_module:,.0f} € = {module_costs:,.0f} €<br/>
        <b>🔸 Wechselrichter:</b> {inverter_costs:,.0f} €<br/>
        <b>🔸 Installation & Montage:</b> {installation_costs:,.0f} €<br/>
        <b>🔸 Anschluss & Zubehör:</b> {other_costs:,.0f} €<br/>
        
        <br/>
        <b>💶 Gesamtpreis (netto):</b> {total_investment:,.0f} €<br/>
        <b>💶 MwSt. (19%):</b> {total_investment * 0.19:,.0f} €<br/>
        <b>💰 Gesamtpreis (brutto):</b> {total_investment * 1.19:,.0f} €<br/>
        <br/>
        <b>📊 Preis pro kWp:</b> {total_investment/max(anlage_kwp,0.1):,.0f} € (netto)<br/>
        <br/>
        <b>⏱️ Zahlungsbedingungen:</b><br/>
        • 20% Anzahlung bei Auftragserteilung<br/>
        • 60% bei Lieferung der Komponenten<br/>
        • 20% nach erfolgreicher Inbetriebnahme<br/><br/>
        
        <i>✅ Alle Preise sind Festpreise und gelten für 30 Tage ab Angebotsdatum.<br/>
        ✅ Förderung und Finanzierungsoptionen auf Anfrage verfügbar.</i>
        """
        self.story.append(Paragraph(costs_text, self.styles.get('Normal')))

    def _add_simulation_section(self):
        """Fügt die Simulations-Details hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Simulations-Details", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Simulations-Informationen
        analysis = self.analysis_results
        simulation_text = f"""
        <b>Jährliche PV-Produktion:</b> {analysis.get('annual_pv_production_kwh', 0):,.0f} kWh<br/>
        <b>Eigenverbrauch:</b> {analysis.get('self_consumption_kwh', 0):,.0f} kWh<br/>
        <b>Netzeinspeisung:</b> {analysis.get('grid_feed_in_kwh', 0):,.0f} kWh<br/>
        <b>Autarkiegrad:</b> {analysis.get('self_supply_rate_percent', 0):.1f}%
        """
        self.story.append(Paragraph(simulation_text, self.styles.get('Normal')))

    def _add_co2_section(self):
        """Fügt die CO₂-Einsparung hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("CO₂-Einsparung", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # CO₂-Kennzahlen
        analysis = self.analysis_results
        co2_text = f"""
        <b>Jährliche CO₂-Einsparung:</b> {analysis.get('annual_co2_savings_kg', 0):,.0f} kg<br/>
        <b>Entspricht Bäumen:</b> {analysis.get('co2_equivalent_trees_per_year', 0):.0f} Bäume/Jahr<br/>
        <b>Entspricht Auto-km:</b> {analysis.get('co2_equivalent_car_km_per_year', 0):,.0f} km/Jahr<br/>
        <b>25-jährige CO₂-Einsparung:</b> {analysis.get('annual_co2_savings_kg', 0) * 25:,.0f} kg
        """
        self.story.append(Paragraph(co2_text, self.styles.get('Normal')))

    def _add_charts_section(self):
        """Fügt die Diagramme/Visualisierungen hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Diagramme & Visualisierungen", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Prüfe, ob Diagramme in analysis_results verfügbar sind
        charts_available = []
        if self.analysis_results:
            chart_keys = [k for k in self.analysis_results.keys() if k.endswith('_chart_bytes')]
            # Verbessere die Chart-Namen für bessere Lesbarkeit
            chart_names_map = {
                'monthly_prod_cons': 'Monatliche Produktion vs. Verbrauch',
                'cumulative_cashflow': 'Kumulativer Cashflow (25 Jahre)',
                'pv_usage': 'PV-Nutzung und Eigenverbrauch',
                'consumption_coverage': 'Verbrauchsdeckung durch PV',
                'cost_overview': 'Kostenübersicht und Einsparungen',
                'cost_projection': 'Kostenentwicklung (mit/ohne PV)',
                'monthly_savings': 'Monatliche Einsparungen',
                'payback_analysis': 'Amortisationsanalyse',
                'environmental_impact': 'Umweltauswirkungen',
                'system_performance': 'Anlagenleistung'
            }
            
            for key in chart_keys:
                chart_base = key.replace('_chart_bytes', '')
                friendly_name = chart_names_map.get(chart_base, 
                    chart_base.replace('_', ' ').title())
                charts_available.append(friendly_name)
        
        if charts_available and len(charts_available) > 0:
            # Zeige die ersten 8 Charts detailliert
            main_charts = charts_available[:8]
            additional_count = max(0, len(charts_available) - 8)
            
            charts_text = f"""
            <b>📊 Verfügbare Visualisierungen für Ihr Projekt:</b><br/><br/>
            
            <b>🔍 Hauptdiagramme:</b><br/>
            {chr(10).join([f"• <b>{chart}</b>" for chart in main_charts])}
            
            {f"<br/><b>📈 Zusätzliche Analysen:</b> {additional_count} weitere Diagramme verfügbar<br/>" if additional_count > 0 else ""}
            
            <br/>
            <b>💡 Verfügbare Chart-Kategorien:</b><br/>
            • <b>Wirtschaftlichkeit:</b> Cashflow, Amortisation, Kosteneinsparungen<br/>
            • <b>Technische Analyse:</b> Systemleistung, Eigenverbrauch, Autarkie<br/>
            • <b>Umweltaspekte:</b> CO₂-Einsparung, Nachhaltigkeit<br/>
            • <b>Monatliche Übersichten:</b> Produktion, Verbrauch, Ersparnisse<br/>
            
            <br/>
            <i>📱 Die interaktiven Diagramme sind in der Web-Anwendung verfügbar.<br/>
            📄 Ausgewählte Charts können in die finale PDF-Version integriert werden.</i>
            """
        else:
            charts_text = """
            <b>📊 Geplante Visualisierungen für Ihr Projekt:</b><br/><br/>
            
            <b>🔹 Wirtschaftlichkeits-Diagramme:</b><br/>
            • <b>Monatliche Erträge:</b> Visualisierung der erwarteten Stromproduktion<br/>
            • <b>Kostenentwicklung:</b> Stromkosten mit und ohne PV-Anlage<br/>
            • <b>Amortisationsdiagramm:</b> Zeitpunkt der Kostendeckung<br/>
            
            <b>🔹 Technische Analysen:</b><br/>
            • <b>Eigenverbrauch vs. Einspeisung:</b> Optimale Nutzung der Energie<br/>
            • <b>Systemleistung:</b> Anlagenperformance über das Jahr<br/>
            • <b>Verbrauchsdeckung:</b> Deckung des Haushaltsverbrauchs<br/>
            
            <b>🔹 Umwelt & Nachhaltigkeit:</b><br/>
            • <b>CO₂-Einsparung:</b> Umweltbeitrag über die Anlagenlaufzeit<br/>
            • <b>Nachhaltigkeit:</b> Langfristige Umweltwirkung<br/>
            
            <br/>
            <i>📊 Detaillierte Diagramme werden nach der finalen Projektkonfiguration erstellt.<br/>
            🎯 Alle Visualisierungen basieren auf Ihren spezifischen Projektdaten.</i>
            """
        
        self.story.append(Paragraph(charts_text, self.styles.get('Normal')))

    def _add_future_aspects_section(self):
        """Fügt die Zukunftsaspekte hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Zukunftsaspekte", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Zukunftsaspekte
        future_text = """
        <b>Erweiterungsmöglichkeiten:</b> Speichersystem, Wallbox für E-Fahrzeuge<br/>
        <b>Wartung:</b> Regelmäßige Reinigung und Inspektion empfohlen<br/>
        <b>Garantie:</b> 25 Jahre Leistungsgarantie auf Module<br/>
        <b>Monitoring:</b> Online-Überwachung der Anlagenleistung
        """
        self.story.append(Paragraph(future_text, self.styles.get('Normal')))

    def _add_generic_section(self, section_name):
        """Fügt eine generische Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph(section_name, self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Spezielle Inhalte je nach Sektion
        if section_name == "SideBySideSims" or section_name == "Simulations-Vergleich":
            generic_text = """
            <b>Szenario-Vergleich:</b><br/>
            • <b>Ohne PV-Anlage:</b> Kontinuierlich steigende Stromkosten<br/>
            • <b>Mit PV-Anlage:</b> Drastische Reduzierung der Stromkosten<br/>
            • <b>Unabhängigkeit:</b> Weniger abhängig von Strompreiserhöhungen<br/>
            • <b>Wertsteigerung:</b> Erhöhung des Immobilienwerts
            """
        elif section_name == "CustomImages" or section_name == "Individuelle Bilder":
            generic_text = """
            <b>Visualisierung Ihres Projekts:</b><br/>
            • Dach-Aufnahmen und Planungsbilder<br/>
            • 3D-Renderings der geplanten Anlage<br/>
            • Installationsdetails und Komponenten<br/>
            <i>Individuelle Bilder werden nach der Vor-Ort-Begehung hinzugefügt.</i>
            """
        elif section_name == "CustomTexts" or section_name == "Individuelle Texte":
            generic_text = """
            <b>Projektspezifische Informationen:</b><br/>
            • Individuelle Beratungsergebnisse<br/>
            • Spezielle Anforderungen und Lösungen<br/>
            • Lokale Gegebenheiten und Besonderheiten<br/>
            <i>Projektspezifische Details werden nach der Beratung ergänzt.</i>
            """
        elif section_name == "HighlightBox" or section_name == "Highlight-Box":
            generic_text = """
            <b>🌟 Ihre Vorteile auf einen Blick:</b><br/>
            ✓ <b>Sofortige Kosteneinsparungen</b> ab der ersten Kilowattstunde<br/>
            ✓ <b>Umweltfreundlich</b> - Aktiver Beitrag zum Klimaschutz<br/>
            ✓ <b>Wertsteigerung</b> Ihrer Immobilie<br/>
            ✓ <b>25 Jahre Garantie</b> auf die Solarmodule<br/>
            ✓ <b>Staatliche Förderung</b> und Einspeisevergütung
            """
        else:
            generic_text = f"""
            <b>Weitere Informationen zu {section_name}:</b><br/>
            Diese Sektion wird basierend auf Ihren spezifischen Anforderungen 
            und nach der detaillierten Projektplanung vervollständigt.<br/>
            <i>Individuelle Inhalte werden in der finalen Version ergänzt.</i>
            """
        
        self.story.append(Paragraph(generic_text, self.styles.get('Normal')))
    
    def _add_fallback_content(self):
        """Fügt Standard-Inhalt hinzu, falls keine Sektionen verarbeitet wurden"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        # Standard-Titel
        self.story.append(Spacer(1, 5*cm))
        self.story.append(Paragraph("Solar-Angebot", self.styles.get('OfferTitle', self.styles.get('Title'))))
        
        # Standard-Inhalt
        self.story.append(Spacer(1, 2*cm))
        self.story.append(Paragraph("Angebot für Photovoltaikanlage", self.styles.get('Heading2')))
        
        standard_text = """
        Vielen Dank für Ihr Interesse an einer Photovoltaikanlage. 
        Gerne unterbreiten wir Ihnen unser Angebot für eine maßgeschneiderte Solarlösung.
        """
        self.story.append(Paragraph(standard_text, self.styles.get('Normal')))
        self.story.append(Paragraph("Technische Komponenten", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        # Beispiel-Komponenten
        components_text = """
        <b>Solarmodule:</b> Hocheffiziente Monokristalline Module<br/>
        <b>Wechselrichter:</b> String-Wechselrichter mit Optimierern<br/>
        <b>Montagesystem:</b> Aufdach-Montage mit Dachhaken<br/>
        <b>Überwachung:</b> App-basiertes Monitoring-System
        """
        self.story.append(Paragraph(components_text, self.styles.get('Normal')))

    def _add_two_column_layout(self, content_left, content_right):
        if self.selected_title_image_b64:
            try:
                image_data = base64.b64decode(self.selected_title_image_b64)
                self.story.append(Image(io.BytesIO(image_data), width=21*cm, height=29.7*cm))
            except Exception as e:
                self.story.append(Paragraph(f"[Fehler: Titelbild: {e}]", self.styles['ErrorText']))
        else:
            self.story.append(Spacer(1, 5 * cm))
            self.story.append(Paragraph(self.selected_offer_title_text, self.styles['h1']))
        self.story.append(PageBreak())
        
    def _build_salt_and_pepper_story(self):
        # Reduzierte, minimalistische Story
        self.story.append(Paragraph("Firmeninfos", self.styles['h2']))
        # ... (weitere minimalistische Inhalte)
        self.story.append(Paragraph("Leistungen und Komponenten", self.styles['h2']))
        self.story.append(Paragraph("Preis", self.styles['h2']))
        self.story.append(Paragraph("Unterschriftenfeld", self.styles['h2']))
        self.story.append(Paragraph("Schlusswort", self.styles['h2']))

    def _handle_attachments(self, main_pdf_bytes):
        paths_to_append = []
        # Logik zum Sammeln der Dokumentenpfade...
        # ...
        return _append_documents_to_pdf(main_pdf_bytes, paths_to_append)

    # === NEUE OPTIONALE BUSINESS-SEKTIONEN ===
    
    def _add_company_profile_section(self):
        """Fügt die Unternehmensprofil-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Unser Unternehmen", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        company_profile_text = f"""
        <b>{self.company_info.get('name', 'Unser Unternehmen')}</b><br/><br/>
        Mit langjähriger Erfahrung im Bereich Photovoltaik sind wir Ihr zuverlässiger Partner für nachhaltige Energielösungen. 
        Unser engagiertes Team begleitet Sie von der ersten Beratung bis zur finalen Inbetriebnahme Ihrer Anlage.<br/><br/>
        <b>Kontakt:</b><br/>
        📍 {self.company_info.get('street', '')}, {self.company_info.get('zip_code', '')} {self.company_info.get('city', '')}<br/>
        📞 {self.company_info.get('phone', '')}<br/>
        📧 {self.company_info.get('email', '')}
        """
        self.story.append(Paragraph(company_profile_text, self.styles.get('Normal')))

    def _add_certifications_section(self):
        """Fügt die Zertifizierungen-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Zertifizierungen & Qualitätsstandards", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        cert_text = """
        <b>Unsere Zertifizierungen & Qualitätsstandards:</b><br/><br/>
        ✓ <b>VDE-Zertifizierung</b> - Elektrotechnische Sicherheit<br/>
        ✓ <b>Meisterbetrieb</b> - Handwerkliche Qualität<br/>
        ✓ <b>IHK-Sachverständiger</b> - Technische Expertise<br/>
        ✓ <b>ISO 9001</b> - Qualitätsmanagementsystem<br/>
        ✓ <b>Fachbetrieb für Photovoltaik</b> - Spezialisierung<br/><br/>
        Alle Komponenten entsprechen den aktuellen DIN- und VDE-Normen.
        """
        self.story.append(Paragraph(cert_text, self.styles.get('Normal')))

    def _add_references_section(self):
        """Fügt die Referenzen-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Referenzen & Kundenerfahrungen", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        ref_text = """
        <b>Referenzen & Kundenerfahrungen:</b><br/><br/>
        ⭐⭐⭐⭐⭐ <i>"Professionelle Beratung und saubere Montage. Unsere Anlage läuft seit 2 Jahren perfekt!"</i><br/>
        - Familie Müller, 8,5 kWp Anlage<br/><br/>
        ⭐⭐⭐⭐⭐ <i>"Von der Planung bis zur Inbetriebnahme - alles aus einer Hand und termingerecht."</i><br/>
        - Herr Schmidt, 12 kWp mit Speicher<br/><br/>
        ⭐⭐⭐⭐⭐ <i>"Kompetente Beratung, faire Preise, einwandfreie Ausführung. Sehr empfehlenswert!"</i><br/>
        - Frau Weber, 6,2 kWp Anlage<br/><br/>
        <b>Über 500 zufriedene Kunden</b> vertrauen auf unsere Expertise.
        """
        self.story.append(Paragraph(ref_text, self.styles.get('Normal')))

    def _add_installation_section(self):
        """Fügt die Installation-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Professionelle Installation", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        install_text = """
        <b>Professionelle Installation - Ihr Weg zur eigenen Solaranlage:</b><br/><br/>
        <b>1. Terminplanung & Vorbereitung</b><br/>
        • Detaillierte Terminabsprache<br/>
        • Anmeldung beim Netzbetreiber<br/>
        • Bereitstellung aller Komponenten<br/><br/>
        <b>2. Montage (1-2 Tage)</b><br/>
        • Dachmontage durch zertifizierte Dachdecker<br/>
        • Elektrische Installation durch Elektromeister<br/>
        • Sicherheitsprüfung nach VDE-Norm<br/><br/>
        <b>3. Inbetriebnahme & Übergabe</b><br/>
        • Funktionstest und Messung<br/>
        • Einweisung in die Bedienung<br/>
        • Übergabe aller Unterlagen
        """
        self.story.append(Paragraph(install_text, self.styles.get('Normal')))

    def _add_maintenance_section(self):
        """Fügt die Wartung-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Wartung & Langzeitservice", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        maint_text = """
        <b>Wartung & Langzeitservice für maximale Erträge:</b><br/><br/>
        <b>Wartungsleistungen:</b><br/>
        • Jährliche Sichtprüfung der Module<br/>
        • Überprüfung der elektrischen Verbindungen<br/>
        • Funktionstest des Wechselrichters<br/>
        • Reinigung bei Bedarf<br/>
        • Ertragskontrolle und Optimierung<br/><br/>
        <b>24/7 Monitoring:</b><br/>
        • Online-Überwachung der Anlagenleistung<br/>
        • Automatische Störungsmeldung<br/>
        • Ferndiagnose und schnelle Hilfe<br/><br/>
        <b>Wartungsvertrag verfügbar</b> - Sprechen Sie uns an!
        """
        self.story.append(Paragraph(maint_text, self.styles.get('Normal')))

    def _add_financing_section(self):
        """Fügt die Finanzierung-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Flexible Finanzierungslösungen", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        fin_text = """
        <b>Flexible Finanzierungsmöglichkeiten:</b><br/><br/>
        💰 <b>KfW-Förderung</b><br/>
        • Zinsgünstige Darlehen bis 150.000€<br/>
        • Tilgungszuschüsse möglich<br/>
        • Wir unterstützen bei der Antragstellung<br/><br/>
        🏦 <b>Bankfinanzierung</b><br/>
        • Partnerschaften mit regionalen Banken<br/>
        • Attraktive Konditionen für Solaranlagen<br/>
        • Laufzeiten bis 20 Jahre<br/><br/>
        📊 <b>Leasing & Pacht</b><br/>
        • Keine Anfangsinvestition<br/>
        • Monatliche Raten ab 89€<br/>
        • Rundum-Sorglos-Paket inklusive<br/><br/>
        Gerne erstellen wir Ihnen ein individuelles Finanzierungskonzept!
        """
        self.story.append(Paragraph(fin_text, self.styles.get('Normal')))

    def _add_insurance_section(self):
        """Fügt die Versicherung-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Umfassender Versicherungsschutz", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        ins_text = """
        <b>Umfassender Versicherungsschutz für Ihre Investition:</b><br/><br/>
        🛡️ <b>Photovoltaik-Versicherung</b><br/>
        • Schutz vor Sturm, Hagel, Blitzschlag<br/>
        • Diebstahl- und Vandalismus-Schutz<br/>
        • Elektronikversicherung für Wechselrichter<br/><br/>
        ⚡ <b>Ertragsausfallversicherung</b><br/>
        • Absicherung bei Produktionsausfall<br/>
        • Ersatz entgangener EEG-Vergütung<br/>
        • Mehrkosten bei Reparaturen<br/><br/>
        🏠 <b>Integration in bestehende Versicherungen</b><br/>
        • Prüfung der Wohngebäudeversicherung<br/>
        • Anpassung bestehender Policen<br/>
        • Kostengünstige Ergänzungen<br/><br/>
        Wir beraten Sie gerne zu optimalen Versicherungslösungen!
        """
        self.story.append(Paragraph(ins_text, self.styles.get('Normal')))

    def _add_warranty_section(self):
        """Fügt die Garantie-Sektion hinzu"""
        if not hasattr(self, 'story'):
            self.story = []
            
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("Herstellergarantie & Gewährleistung", self.styles.get('SectionTitle', self.styles.get('Heading2'))))
        
        warr_text = """
        <b>Garantie & Gewährleistung - Ihre Sicherheit:</b><br/><br/>
        🔧 <b>Herstellergarantien:</b><br/>
        • <b>Module:</b> 25 Jahre Leistungsgarantie<br/>
        • <b>Wechselrichter:</b> 10-20 Jahre Herstellergarantie<br/>
        • <b>Speichersystem:</b> 10 Jahre Garantie<br/>
        • <b>Montagesystem:</b> 15 Jahre Material-/Korrosionsschutz<br/><br/>
        ⚙️ <b>Handwerkergewährleistung:</b><br/>
        • 2 Jahre auf Montage und Installation<br/>
        • 5 Jahre erweiterte Gewährleistung möglich<br/>
        • Schnelle Reaktionszeiten bei Problemen<br/><br/>
        📞 <b>Service-Hotline:</b><br/>
        • Kostenlose Beratung bei Fragen<br/>
        • Ferndiagnose und Support<br/>
        • Vor-Ort-Service innerhalb 48h<br/><br/>
        <b>Ihr Vertrauen ist unsere Verpflichtung!</b>
        """
        self.story.append(Paragraph(warr_text, self.styles.get('Normal')))

_PDF_GENERATOR_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Da pdf_generator.py im selben Verzeichnis wie der data/ Ordner liegt, ist der Basis-Pfad korrekt
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "product_datasheets")
COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "company_docs")


def get_text(texts_dict: Dict[str, str], key: str, fallback_text_value: Optional[str] = None) -> str:
    if not isinstance(texts_dict, dict): return fallback_text_value if fallback_text_value is not None else key
    if fallback_text_value is None: fallback_text_value = key.replace("_", " ").title() + " (PDF-Text fehlt)"
    retrieved = texts_dict.get(key, fallback_text_value)
    return str(retrieved)

def format_kpi_value(value: Any, unit: str = "", na_text_key: str = "not_applicable_short", precision: int = 2, texts_dict: Optional[Dict[str,str]] = None) -> str:
    current_texts = texts_dict if texts_dict is not None else {}
    na_text = get_text(current_texts, na_text_key, "k.A.")
    if value is None or (isinstance(value, (float, int)) and math.isnan(value)): return na_text
    if isinstance(value, str) and value == na_text: return value
    if isinstance(value, str):
        try:
            cleaned_value_str = value
            if '.' in value and ',' in value:
                 if value.rfind('.') > value.rfind(','): cleaned_value_str = value.replace(',', '')
                 elif value.rfind(',') > value.rfind('.'): cleaned_value_str = value.replace('.', '')
            cleaned_value_str = cleaned_value_str.replace(',', '.')
            value = float(cleaned_value_str)
        except ValueError: return value

    if isinstance(value, (int, float)):
        if math.isinf(value): return get_text(current_texts, "value_infinite", "Nicht berechenbar")
        if unit == "Jahre": return get_text(current_texts, "years_format_string_pdf", "{val:.1f} Jahre").format(val=value)
        
        formatted_num_en = f"{value:,.{precision}f}"
        formatted_num_de = formatted_num_en.replace(",", "#TEMP#").replace(".", ",").replace("#TEMP#", ".")
        return f"{formatted_num_de} {unit}".strip()
    return str(value)

STYLES: Any = {}
FONT_NORMAL = "Helvetica"; FONT_BOLD = "Helvetica-Bold"; FONT_ITALIC = "Helvetica-Oblique"
# KORREKTUR: Standardfarben gemäß neuen Designrichtlinien
PRIMARY_COLOR_HEX = "#1B365D"  # Dunkelblau - Professionell und vertrauensvoll 
SECONDARY_COLOR_HEX = "#2E8B57" # Solargrün - Nachhaltigkeit und Energie
ACCENT_COLOR_HEX = "#FFB347"       # Sonnenorange - Wärme und Optimismus
TEXT_COLOR_HEX = "#2C3E50"         # Anthrazit - Optimale Lesbarkeit
BACKGROUND_COLOR_HEX = "#F8F9FA"   # Hellgrau - Modern und Clean
TEXT_COLOR_HEX = "#333333"
SEPARATOR_LINE_COLOR_HEX = "#E9ECEF" # Subtile, moderne Linienfarbe

# Moderne Farbpalette als Dictionary für bessere Zugänglichkeit
COLORS = {
    'accent_primary': PRIMARY_COLOR_HEX,
    'accent_secondary': SECONDARY_COLOR_HEX,
    'accent_orange': ACCENT_COLOR_HEX,
    'text_dark': TEXT_COLOR_HEX,
    'background_light': BACKGROUND_COLOR_HEX,
    'separator_line': SEPARATOR_LINE_COLOR_HEX,
    'table_header_bg': PRIMARY_COLOR_HEX,
    'table_header_text': '#FFFFFF',
    'table_row_bg': '#FAFBFC',
    'table_alt_row_bg': '#F1F3F4',
    'table_border': '#E1E5E9',
    'success_green': '#28A745',
    'warning_orange': '#FFC107',
    'error_red': '#DC3545',
    'info_blue': '#17A2B8'
}

if _REPORTLAB_AVAILABLE:
    STYLES = getSampleStyleSheet()
    STYLES.add(ParagraphStyle(name='NormalLeft', alignment=TA_LEFT, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='NormalRight', alignment=TA_RIGHT, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='NormalCenter', alignment=TA_CENTER, fontName=FONT_NORMAL, fontSize=10, leading=12, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='Footer', parent=STYLES['NormalCenter'], fontName=FONT_ITALIC, fontSize=8, textColor=colors.darkgrey)) # Dunkleres Grau für Footer
    STYLES.add(ParagraphStyle(name='OfferTitle', parent=STYLES['h1'], fontName=FONT_BOLD, fontSize=24, alignment=TA_CENTER, spaceBefore=1.5*cm, spaceAfter=1.5*cm, textColor=colors.HexColor(PRIMARY_COLOR_HEX), leading=28)) # Größer und eleganter
    STYLES.add(ParagraphStyle(name='SectionTitle', parent=STYLES['h2'], fontName=FONT_BOLD, fontSize=16, spaceBefore=1.2*cm, spaceAfter=0.8*cm, keepWithNext=1, textColor=colors.HexColor(PRIMARY_COLOR_HEX), leading=20)) # Moderner
    STYLES.add(ParagraphStyle(name='SubSectionTitle', parent=STYLES['h3'], fontName=FONT_BOLD, fontSize=13, spaceBefore=1*cm, spaceAfter=0.5*cm, keepWithNext=1, textColor=colors.HexColor(SECONDARY_COLOR_HEX), leading=16)) # Sekundärfarbe für Abwechslung
    STYLES.add(ParagraphStyle(name='ComponentTitle', parent=STYLES['SubSectionTitle'], fontSize=11, spaceBefore=0.5*cm, spaceAfter=0.2*cm, alignment=TA_LEFT, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CompanyInfoDeckblatt', parent=STYLES['NormalCenter'], fontName=FONT_NORMAL, fontSize=9, leading=11, spaceAfter=0.5*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CoverLetter', parent=STYLES['NormalLeft'], fontSize=11, leading=15, spaceBefore=0.5*cm, spaceAfter=0.5*cm, alignment=TA_JUSTIFY, firstLineIndent=0, leftIndent=0, rightIndent=0, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Etwas mehr Zeilenabstand    # Neuer Stil für rechtsbündige Kundenadresse auf Deckblatt
    STYLES.add(ParagraphStyle(name='CustomerAddressDeckblattRight', parent=STYLES['NormalRight'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='CustomerAddressInner', parent=STYLES['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Für Anschreiben etc.
    # FEHLENDER STYLE - CustomerAddress (allgemein)
    STYLES.add(ParagraphStyle(name='CustomerAddress', parent=STYLES['NormalLeft'], fontSize=10, leading=12, spaceBefore=0.5*cm, spaceAfter=0.8*cm, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    
    STYLES.add(ParagraphStyle(name='TableText', parent=STYLES['NormalLeft'], fontName=FONT_NORMAL, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX))) # Helvetica für Tabellentext
    STYLES.add(ParagraphStyle(name='TableTextSmall', parent=STYLES['NormalLeft'], fontName=FONT_NORMAL, fontSize=8, leading=10, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableNumber', parent=STYLES['NormalRight'], fontName=FONT_NORMAL, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableLabel', parent=STYLES['NormalLeft'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    # KORREKTUR: Tabellenheader Farbe und Textfarbe
    STYLES.add(ParagraphStyle(name='TableHeader', parent=STYLES['NormalCenter'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.white, backColor=colors.HexColor(PRIMARY_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='TableBoldRight', parent=STYLES['NormalRight'], fontName=FONT_BOLD, fontSize=9, leading=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='ImageCaption', parent=STYLES['NormalCenter'], fontName=FONT_ITALIC, fontSize=8, spaceBefore=0.1*cm, textColor=colors.grey))
    STYLES.add(ParagraphStyle(name='ChartTitle', parent=STYLES['SubSectionTitle'], alignment=TA_CENTER, spaceBefore=0.6*cm, spaceAfter=0.2*cm, fontSize=11, textColor=colors.HexColor(TEXT_COLOR_HEX)))
    STYLES.add(ParagraphStyle(name='ChapterHeader', parent=STYLES['NormalRight'], fontName=FONT_NORMAL, fontSize=9, textColor=colors.grey, alignment=TA_RIGHT))

    TABLE_STYLE_DEFAULT = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL),('ALIGN',(1,0),(1,-1),'LEFT'), # Werte linksbündig für Standardtabelle
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)), # Dezente Gridlinien
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),3*mm), ('RIGHTPADDING',(0,0),(-1,-1),3*mm),
        ('TOPPADDING',(0,0),(-1,-1),2*mm), ('BOTTOMPADDING',(0,0),(-1,-1),2*mm)
    ])
    # KORREKTUR: DATA_TABLE_STYLE für Konsistenz
    DATA_TABLE_STYLE = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PRIMARY_COLOR_HEX)), # Kopfzeile Primärfarbe
        ('TEXTCOLOR',(0,0),(-1,0),colors.white), # Kopfzeile Text weiß
        ('FONTNAME',(0,0),(-1,0),FONT_BOLD),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL), # Datenzellen Helvetica
        ('ALIGN',(0,1),(0,-1),'LEFT'), # Erste Datenspalte links
        ('ALIGN',(1,1),(-1,-1),'RIGHT'), # Andere Datenspalten rechts (für Zahlen)
        ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm), 
        ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)) # Textfarbe Datenzellen
    ])
    PRODUCT_TABLE_STYLE = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL), ('ALIGN',(1,0),(1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
        ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm)
    ])
    PRODUCT_MAIN_TABLE_STYLE = TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)])

def _draw_page_statics(canvas, doc, theme):
    """Zeichnet Kopf- und Fußzeile basierend auf den Theme-Optionen."""
    canvas.saveState()
    
    logo_placement = theme.get('logo_placement', 'none')
    is_title_page = (doc.page == 1)

    if (logo_placement == 'every_page') or (logo_placement == 'title_only' and is_title_page):
        logo_path = theme.get('logo_path')
        if logo_path and os.path.exists(logo_path):
            logo_pos_cm = theme.get('logo_pos', (17, 27))
            logo_size_cm = theme.get('logo_size', (3, 1.5))
            canvas.drawImage(logo_path, logo_pos_cm[0] * cm, logo_pos_cm[1] * cm, width=logo_size_cm[0] * cm, height=logo_size_cm[1] * cm, preserveAspectRatio=True, mask='auto')

    if theme.get('show_page_numbers', True) and not is_title_page:
        page_num_text = f"Seite {doc.page}"
        fonts = theme.get('fonts', {})
        colors_map = theme.get('colors', {})
        canvas.setFont(fonts.get('family_main', 'Helvetica'), fonts.get('size_footer', 8))
        canvas.setFillColor(colors.HexColor(colors_map.get('footer_text', '#7f8c8d')))
        canvas.drawRightString(20 * cm, 1.5 * cm, page_num_text)
        
    canvas.restoreState()    
    # MODERNE TABELLENSTYLES mit Zebra-Streifen
    def create_zebra_table_style(num_rows, header_bg=PRIMARY_COLOR_HEX, alt_bg=BACKGROUND_COLOR_HEX):
        """Erstellt einen modernen Tabellenstil mit Zebra-Streifen"""
        style = [
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(header_bg)), # Header
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),FONT_BOLD),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL),
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
            ('LEFTPADDING',(0,0),(-1,-1),3*mm),
            ('RIGHTPADDING',(0,0),(-1,-1),3*mm),
            ('TOPPADDING',(0,0),(-1,-1),2.5*mm),
            ('BOTTOMPADDING',(0,0),(-1,-1),2.5*mm),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ]
        # Zebra-Streifen für ungerade Zeilen
        for row in range(1, num_rows):
            if row % 2 == 0:  # Jede zweite Zeile
                style.append(('BACKGROUND',(0,row),(-1,row),colors.HexColor(alt_bg)))
        return TableStyle(style)
        
    # MODERNE PRODUKT-TABELLE mit Schatten-Effekt
    MODERN_PRODUCT_TABLE_STYLE = TableStyle([
        ('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(TEXT_COLOR_HEX)),
        ('FONTNAME',(0,0),(0,-1),FONT_BOLD), 
        ('FONTNAME',(1,0),(1,-1),FONT_NORMAL),
        ('ALIGN',(0,0),(0,-1),'LEFT'),
        ('ALIGN',(1,0),(1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),4*mm),
        ('RIGHTPADDING',(0,0),(-1,-1),4*mm),
        ('TOPPADDING',(0,0),(-1,-1),3*mm),
        ('BOTTOMPADDING',(0,0),(-1,-1),3*mm),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#FFFFFF")),
        ('BOX',(0,0),(-1,-1),1,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
        ('LINEBELOW',(0,0),(-1,0),2,colors.HexColor(PRIMARY_COLOR_HEX)), # Elegante Unterstreichung
    ])

    def _append_documents_to_pdf(main_pdf_bytes, document_paths_to_append):
        """Hängt externe PDFs an ein PDF in Bytes an."""
        if not _PYPDF_AVAILABLE or not document_paths_to_append: return main_pdf_bytes
        writer = PdfWriter()
        try:
            writer.append(io.BytesIO(main_pdf_bytes))
            for doc_path in document_paths_to_append:
                if os.path.exists(doc_path):
                    try:
                        writer.append(doc_path)
                    except Exception as e:
                        print(f"WARNUNG: PDF-Anhang '{doc_path}' fehlerhaft: {e}")
            output_buffer = io.BytesIO()
            writer.write(output_buffer)
            return output_buffer.getvalue()
        except Exception as e:
            print(f"Fehler beim Zusammenfügen der PDFs: {e}")
            return main_pdf_bytes

        
class PageNumCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._page_layout_callback = kwargs.pop('onPage_callback', None)
        self._callback_kwargs = kwargs.pop('callback_kwargs', {})
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.total_pages = 0 
        self.current_chapter_title_for_header = '' 
    def showPage(self): 
        self._saved_page_states.append(dict(self.__dict__))
        super().showPage()
    
    def save(self):
        self.total_pages = len(self._saved_page_states)
        for state_idx, state in enumerate(self._saved_page_states):
            self.__dict__.update(state) 
            self._pageNumber = state_idx + 1 
            if self._page_layout_callback:
                self._page_layout_callback(canvas_obj=self, doc_template=self._doc, **self._callback_kwargs)
        super().save()

class SetCurrentChapterTitle(Flowable):
    def __init__(self, title): Flowable.__init__(self); self.title = title
    def wrap(self, availWidth, availHeight): return 0,0
    def draw(self):
        if hasattr(self, 'canv'): self.canv.current_chapter_title_for_header = self.title

# Einfache HRFlowable für Trennlinien, falls die ReportLab Version sie nicht direkt hat
class SimpleHRFlowable(Flowable):
    def __init__(self, width="100%", thickness=0.5, color=colors.HexColor(SEPARATOR_LINE_COLOR_HEX), spaceBefore=0.2*cm, spaceAfter=0.2*cm, vAlign='BOTTOM'):
        Flowable.__init__(self)
        self.width_spec = width
        self.thickness = thickness
        self.color = color
        self.spaceBefore = spaceBefore
        self.spaceAfter = spaceAfter
        self.vAlign = vAlign # Kann 'TOP', 'MIDDLE', 'BOTTOM' sein

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        # y-Position anpassen basierend auf vAlign und Höhe des Flowables (nur thickness)
        y_pos = 0
        if self.vAlign == 'TOP':
            y_pos = -self.thickness 
        elif self.vAlign == 'MIDDLE':
            y_pos = -self.thickness / 2.0
        # Für 'BOTTOM' ist y_pos = 0 korrekt

        self.canv.line(0, y_pos, self.drawWidth, y_pos) # drawWidth wird von ReportLab gesetzt
        self.canv.restoreState()

    def wrap(self, availWidth, availHeight):
        self.drawWidth = availWidth # Nutze die verfügbare Breite
        if isinstance(self.width_spec, str) and self.width_spec.endswith('%'):
            self.drawWidth = availWidth * (float(self.width_spec[:-1]) / 100.0)
        elif isinstance(self.width_spec, (int, float)):
            self.drawWidth = self.width_spec
        return self.drawWidth, self.thickness + self.spaceBefore + self.spaceAfter

    def getSpaceBefore(self):
        return self.spaceBefore

    def getSpaceAfter(self):
        return self.spaceAfter

class SetCurrentChapterTitle(Flowable):
    def __init__(self, title): Flowable.__init__(self); self.title = title
    def wrap(self, availWidth, availHeight): return 0,0
    def draw(self):
        if hasattr(self, 'canv'): self.canv.current_chapter_title_for_header = self.title

def _update_styles_with_dynamic_colors(design_settings: Dict[str, str]):
    global PRIMARY_COLOR_HEX, SECONDARY_COLOR_HEX, SEPARATOR_LINE_COLOR_HEX, STYLES, DATA_TABLE_STYLE
    if not _REPORTLAB_AVAILABLE: return

    PRIMARY_COLOR_HEX = design_settings.get('primary_color', "#0055A4")
    # SECONDARY_COLOR_HEX wird aktuell nicht stark verwendet, da #F2F2F2 sehr hell ist.
    # Für Hintergründe etc. können wir es definieren, aber Tabellenheader nutzen Primärfarbe.
    SECONDARY_COLOR_HEX = design_settings.get('secondary_color', "#F2F2F2") 
    SEPARATOR_LINE_COLOR_HEX = design_settings.get('separator_color', "#CCCCCC") # Eigene Farbe für Trennlinien

    if STYLES: # Nur wenn STYLES initialisiert wurde
        STYLES['OfferTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['SectionTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['SubSectionTitle'].textColor = colors.HexColor(PRIMARY_COLOR_HEX) # Subsektionen auch in Primärfarbe
        
        # Tabellenheader explizit mit Primärfarbe und weißem Text
        STYLES['TableHeader'].backColor = colors.HexColor(PRIMARY_COLOR_HEX)
        STYLES['TableHeader'].textColor = colors.white
        
        DATA_TABLE_STYLE = TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PRIMARY_COLOR_HEX)), 
            ('TEXTCOLOR',(0,0),(-1,0),colors.white), 
            ('FONTNAME',(0,0),(-1,0),FONT_BOLD), ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor(SEPARATOR_LINE_COLOR_HEX)),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'), ('FONTNAME',(0,1),(-1,-1),FONT_NORMAL),
            ('ALIGN',(0,1),(0,-1),'LEFT'), ('ALIGN',(1,1),(-1,-1),'RIGHT'),
            ('LEFTPADDING',(0,0),(-1,-1),2*mm), ('RIGHTPADDING',(0,0),(-1,-1),2*mm),
            ('TOPPADDING',(0,0),(-1,-1),1.5*mm), ('BOTTOMPADDING',(0,0),(-1,-1),1.5*mm), 
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor(TEXT_COLOR_HEX))
        ])


def _get_image_flowable(image_data_input: Optional[Union[str, bytes]], desired_width: float, texts: Dict[str, str], caption_text_key: Optional[str] = None, max_height: Optional[float] = None, align: str = 'CENTER') -> List[Any]:
    flowables: List[Any] = []
    if not _REPORTLAB_AVAILABLE: return flowables
    img_data_bytes: Optional[bytes] = None

    if isinstance(image_data_input, str) and image_data_input.strip().lower() not in ["", "none", "null", "nan"]:
        try:
            if image_data_input.startswith('data:image'): image_data_input = image_data_input.split(',', 1)[1]
            img_data_bytes = base64.b64decode(image_data_input)
        except Exception: img_data_bytes = None 
    elif isinstance(image_data_input, bytes): img_data_bytes = image_data_input
    
    if img_data_bytes:
        try:
            if not img_data_bytes: raise ValueError("Bilddaten sind leer nach Verarbeitung.")
            img_file_like = io.BytesIO(img_data_bytes)
            img_reader = ImageReader(img_file_like)
            iw, ih = img_reader.getSize()
            if iw <= 0 or ih <= 0: raise ValueError(f"Ungültige Bilddimensionen: w={iw}, h={ih}")
            aspect = ih / float(iw) if iw > 0 else 1.0
            img_h_calc = desired_width * aspect; img_w_final, img_h_final = desired_width, img_h_calc
            if max_height and img_h_calc > max_height: img_h_final = max_height; img_w_final = img_h_final / aspect if aspect > 0 else desired_width
            
            # KORREKTUR: Stelle sicher, dass img_w_final und img_h_final positiv sind
            if img_w_final <=0 or img_h_final <=0:
                raise ValueError(f"Finale Bilddimensionen ungültig: w={img_w_final}, h={img_h_final}")

            img = Image(io.BytesIO(img_data_bytes), width=img_w_final, height=img_h_final)
            img.hAlign = align.upper(); flowables.append(img)
            if caption_text_key:
                caption_text = get_text(texts, caption_text_key, "")
                if caption_text and not caption_text.startswith(caption_text_key) and not caption_text.endswith("(PDF-Text fehlt)"):
                    flowables.append(Spacer(1, 0.1*cm)); flowables.append(Paragraph(caption_text, STYLES['ImageCaption']))
        except Exception: 
            if caption_text_key :
                caption_text_fb = get_text(texts, caption_text_key, "")
                if caption_text_fb and not caption_text_fb.startswith(caption_text_key):
                     flowables.append(Paragraph(f"<i>({caption_text_fb}: {get_text(texts, 'image_not_available_pdf', 'Bild nicht verfügbar')})</i>", STYLES['ImageCaption']))
    elif caption_text_key:
        caption_text_fb = get_text(texts, caption_text_key, "")
        if caption_text_fb and not caption_text_fb.startswith(caption_text_key):
            flowables.append(Paragraph(f"<i>({caption_text_fb}: {get_text(texts, 'image_not_available_pdf', 'Bild nicht verfügbar')})</i>", STYLES['ImageCaption']))
    return flowables

def _draw_cover_page(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    c.setFont(theme["fonts"]["family_main"], 40)
    c.setFillColor(theme["colors"]["primary"])
    c.drawCentredString(A4[0] / 2, A4[1] / 2 + 5*cm, "Angebot")
    # ... weitere Details für das Deckblatt ...
    c.showPage()

def _draw_cover_letter(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    text_content = get_cover_letter_template(
        customer_name=offer_data["customer"]["name"],
        offer_id=offer_data["offer_id"]
    )
    # ... Logik zum Rendern des Textes auf der Seite ...
    c.showPage()

def _draw_offer_table(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    # ... Logik zum Zeichnen der Angebotstabelle mit Positionen und Preisen ...
    c.showPage()
    
def _draw_custom_content(c: canvas.Canvas, theme: Dict, content: Dict):
    # Diese Funktion verarbeitet die vom Benutzer hochgeladenen Inhalte
    if content.get("type") == "text":
        # Rendere Text
        pass
    elif content.get("type") == "image":
        # Platziere Bild
        image_path = content.get("data")
        c.drawImage(image_path, 1*cm, 1*cm, width=18*cm, preserveAspectRatio=True)
    c.showPage()

def _append_documents_to_pdf(main_pdf_bytes, document_paths_to_append):
    """Hängt externe PDFs an ein PDF in Bytes an."""
    if not _PYPDF_AVAILABLE or not document_paths_to_append: return main_pdf_bytes
    writer = PdfWriter()
    try:
        writer.append(io.BytesIO(main_pdf_bytes))
        for doc_path in document_paths_to_append:
            if os.path.exists(doc_path):
                try:
                    writer.append(doc_path)
                except Exception as e:
                    print(f"WARNUNG: PDF-Anhang '{doc_path}' fehlerhaft: {e}")
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        return output_buffer.getvalue()
    except Exception as e:
        print(f"Fehler beim Zusammenfügen der PDFs: {e}")
        return main_pdf_bytes
        # Mapping von Modul-Namen (aus der UI) zu den Zeichenfunktionen
MODULE_MAP = {
    "deckblatt": _draw_cover_page,
    "anschreiben": _draw_cover_letter,
    "angebotstabelle": _draw_offer_table,
    "benutzerdefiniert": _draw_custom_content,
    # Weitere Module hier hinzufügen (z.B. für Analysen, Datenblätter etc.)
}

def _draw_extended_analysis(c: canvas.Canvas, theme: Dict, offer_data: Dict):
    """Zeichnet die Seite mit den erweiterten Wirtschaftlichkeitsanalysen."""
    c.setFont(theme["fonts"]["family_main"], theme["fonts"]["size_h2"])
    c.setFillColor(theme["colors"]["primary"])
    c.drawString(2*cm, A4[1] - 2*cm, "Detaillierte Wirtschaftlichkeitsanalyse")
    
    results = run_all_extended_analyses(offer_data)
    
    # Hier folgt die Logik, um die 'results' formatiert auf der PDF-Seite auszugeben.
    # z.B. Amortisation, IRR, LCOE etc. als Text oder kleine Tabelle.
    
    c.showPage()

# ... (in der MODULE_MAP)
MODULE_MAP = {
    "deckblatt": _draw_cover_page,
    "anschreiben": _draw_cover_letter,
    "angebotstabelle": _draw_offer_table,
    "benutzerdefiniert": _draw_custom_content,
    "wirtschaftlichkeitsanalyse": _draw_extended_analysis, # NEU
}

def create_offer_pdf(
    offer_data: Dict[str, Any],
    output_filename: str,
    module_order: List[Dict[str, Any]], # NEU: Liste der zu rendernden Module
    theme_name: str,
):
    """
    Erstellt ein PDF-Dokument, indem es die Module in der festgelegten Reihenfolge aufruft.

    Args:
        offer_data (Dict): Die Daten für das Angebot.
        output_filename (str): Der Speicherpfad für das PDF.
        module_order (List[Dict]): Eine geordnete Liste von Modulen, die gezeichnet werden sollen.
                                   Jedes Element ist ein Dict, z.B. {'id': 'anschreiben'} oder
                                   {'id': 'benutzerdefiniert', 'content': {...}}.
        theme_name (str): Der Name des zu verwendenden Designs.
    """
    c = canvas.Canvas(output_filename, pagesize=A4)
    theme = get_theme(theme_name)

    # Setze den Titel des PDF-Dokuments
    c.setTitle(f"Angebot {offer_data.get('offer_id', '')} für {offer_data.get('customer', {}).get('name', '')}")

    # Iteriere durch die vom Benutzer definierte Reihenfolge und rufe die Funktionen auf
    for module_spec in module_order:
        module_id = module_spec["id"]
        draw_function = MODULE_MAP.get(module_id)
        
        if draw_function:
            # Für benutzerdefinierte Module übergeben wir den spezifischen Inhalt
            if module_id == "benutzerdefiniert":
                draw_function(c, theme, module_spec.get("content", {}))
            else:
                draw_function(c, theme, offer_data)
        else:
            print(f"Warnung: PDF-Modul '{module_id}' wurde nicht gefunden.")

    c.save()
    print(f"PDF erfolgreich erstellt: {output_filename}")

def page_layout_handler(canvas_obj: canvas.Canvas, doc_template: SimpleDocTemplate, texts_ref: Dict[str, str], company_info_ref: Dict, company_logo_base64_ref: Optional[str], offer_number_ref: str, page_width_ref: float, page_height_ref: float, margin_left_ref: float, margin_right_ref: float, margin_top_ref: float, margin_bottom_ref: float, doc_width_ref: float, doc_height_ref: float, include_custom_footer_ref: bool = True, include_header_logo_ref: bool = True):
    canvas_obj.saveState()
    current_chapter_title = getattr(canvas_obj, 'current_chapter_title_for_header', '')
    page_num = canvas_obj.getPageNumber()

    # MODERNER HEADER für alle Seiten außer Deckblatt
    if page_num > 1:
        # Elegante Header-Linie in Primärfarbe
        canvas_obj.setStrokeColor(colors.HexColor(PRIMARY_COLOR_HEX))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(margin_left_ref, page_height_ref - margin_top_ref + 0.3*cm, 
                       page_width_ref - margin_right_ref, page_height_ref - margin_top_ref + 0.3*cm)
        
        # Header-Text in moderner Typografie
        canvas_obj.setFont(FONT_NORMAL, 9)
        canvas_obj.setFillColor(colors.HexColor(TEXT_COLOR_HEX))
        header_text = f"Photovoltaik-Angebot • {company_info_ref.get('name', '')}"
        canvas_obj.drawString(margin_left_ref, page_height_ref - margin_top_ref + 0.7*cm, header_text)
          # Seitenzahl elegant rechts
        canvas_obj.setFont(FONT_NORMAL, 9)
        canvas_obj.setFillColor(colors.HexColor(SECONDARY_COLOR_HEX))
        page_text = f"Seite {page_num}"
        canvas_obj.drawRightString(page_width_ref - margin_right_ref, page_height_ref - margin_top_ref + 0.7*cm, page_text)    # FIRMENLOGO RECHTS OBEN auf jeder Seite (NEU wie gewünscht) - OPTIONAL
    if company_logo_base64_ref and include_header_logo_ref:
        try:
            logo_width, logo_height = 3*cm, 2*cm  # Größe für Header-Logo
            if not company_logo_base64_ref:
                raise ValueError("Kein gültiges Logo bereitgestellt.")
            logo_bytes_header = base64.b64decode(company_logo_base64_ref.split(',',1)[1]) if ',' in company_logo_base64_ref and len(company_logo_base64_ref.split(',',1)) > 1 else base64.b64decode(company_logo_base64_ref)
            img_reader_header = ImageReader(io.BytesIO(logo_bytes_header))
            iw, ih = img_reader_header.getSize()
            aspect = ih / float(iw) if iw > 0 else 1.0
            
            final_w_header, final_h_header = logo_width, logo_width * aspect
            if final_h_header > logo_height:
                final_h_header = logo_height
                final_w_header = final_h_header / aspect if aspect > 0 else logo_width
            
            # Rechts oben positionieren
            logo_x = page_width_ref - margin_right_ref - final_w_header
            logo_y = page_height_ref - margin_top_ref - final_h_header
            
            canvas_obj.drawImage(img_reader_header, logo_x, logo_y, 
                                 width=final_w_header, height=final_h_header, mask='auto', preserveAspectRatio=True)
        except Exception as e:
            print(f"Fehler beim Zeichnen des Logos im Header: {e}")

    # MODERNER FOOTER für alle Seiten
    footer_y = margin_bottom_ref - 0.8*cm    
    # Footer-Linie in Sekundärfarbe
    canvas_obj.setStrokeColor(colors.HexColor(SEPARATOR_LINE_COLOR_HEX))
    canvas_obj.setLineWidth(1)
    canvas_obj.line(margin_left_ref, footer_y + 0.5*cm, 
                   page_width_ref - margin_right_ref, footer_y + 0.5*cm)
    
    # Firmenlogo in Fußzeile (links)
    if company_logo_base64_ref:
        try:
            # Logik zum Zeichnen des Logos im Footer (wie zuvor)
            # _get_image_flowable ist für die Story, hier direkter Canvas-Draw:
            logo_width, logo_height = 1.8*cm, 1.0*cm # Zielgröße
            logo_bytes_for_draw = base64.b64decode(company_logo_base64_ref.split(',',1)[1]) if ',' in company_logo_base64_ref and len(company_logo_base64_ref.split(',',1)) > 1 else base64.b64decode(company_logo_base64_ref)
            img_reader_logo = ImageReader(io.BytesIO(logo_bytes_for_draw))
            iw, ih = img_reader_logo.getSize()
            aspect = ih / float(iw) if iw > 0 else 1.0
            
            final_w, final_h = logo_width, logo_width * aspect
            if final_h > logo_height:
                final_h = logo_height
                final_w = final_h / aspect if aspect > 0 else logo_width
            
            canvas_obj.drawImage(img_reader_logo, margin_left_ref, margin_bottom_ref * 0.30, 
                                 width=final_w, height=final_h, mask='auto', preserveAspectRatio=True)
        except Exception: pass
          # Kapitelüberschrift in Kopfzeile (rechts)
        if current_chapter_title:
            p_chapter = Paragraph(current_chapter_title, STYLES['ChapterHeader'])
            p_w, p_h = p_chapter.wrapOn(canvas_obj, doc_width_ref - (2.5*cm), margin_top_ref) 
            p_chapter.drawOn(canvas_obj, page_width_ref - margin_right_ref - p_w, page_height_ref - margin_top_ref + 0.3*cm)
        
    # CUSTOM FOOTER (OPTIONAL wie gewünscht)
    if include_custom_footer_ref:
        # Seitennummer und Angebotsinfo in Fußzeile (MITTIG wie gewünscht)
        page_info_text = get_text(texts_ref, "pdf_page_x_of_y", "Seite {current} von {total}").format(current=str(page_num), total=str(getattr(canvas_obj, 'total_pages', '??')))
        
        # NEUES FORMAT: "| Angebot TT.MMM.JJJJ | Seite xx von xxx |"
        offer_date = datetime.now().strftime('%d.%b.%Y')  # TT.MMM.JJJJ Format (z.B. 17.Jun.2025)
        footer_text = f"| Angebot {offer_date} | {page_info_text} |"
        
        # Footer mittig positionieren (wie gewünscht)
        canvas_obj.setFont(FONT_ITALIC, 8)
        text_width = canvas_obj.stringWidth(footer_text, FONT_ITALIC, 8)
        center_x = page_width_ref / 2
        canvas_obj.drawString(center_x - text_width/2, margin_bottom_ref * 0.45, footer_text)

        # Firmen-Fußzeilentext (linksbündig, nicht zentriert, gemäß neuer Anforderung)
        # "links die Firmendaten („Ömer’s Solar-Ding GmbH, Musterstraße 12, 12345 Musterstadt“)"
        company_footer_address_parts = [
            company_info_ref.get('name', ''),
            company_info_ref.get('street', ''),
            f"{company_info_ref.get('zip_code', '')} {company_info_ref.get('city', '')}".strip()
        ]
        company_footer_address = " | ".join(filter(None, company_footer_address_parts))
        if company_footer_address: # Nur zeichnen, wenn Text vorhanden ist
            canvas_obj.setFont(FONT_NORMAL, 7)
            # Positionierung direkt über dem Logo im Footer, falls vorhanden, oder etwas höher
            footer_text_y_pos = margin_bottom_ref * 0.85 if company_logo_base64_ref else margin_bottom_ref * 0.45
            canvas_obj.drawString(margin_left_ref, footer_text_y_pos, company_footer_address)

    canvas_obj.restoreState()

def _generate_complete_salutation_line(customer_data: Dict, texts: Dict[str, str]) -> str:
    salutation_value = customer_data.get("salutation") 
    title = customer_data.get("title", "")
    first_name = customer_data.get("first_name", "")
    last_name = customer_data.get("last_name", "")

    name_parts = [p for p in [title, first_name, last_name] if p and str(p).strip()]
    customer_full_name_for_salutation = " ".join(name_parts).strip()

    salutation_key_base = "salutation_polite"
    if isinstance(salutation_value, str):
        sl_lower = salutation_value.lower().strip()
        if sl_lower == "herr": salutation_key_base = "salutation_male_polite"
        elif sl_lower == "frau": salutation_key_base = "salutation_female_polite"
        elif sl_lower == "familie":
            fam_name = last_name if last_name and str(last_name).strip() else customer_data.get("company_name", get_text(texts, "family_default_name_pdf", "Familie"))
            return f"{get_text(texts, 'salutation_family_polite', 'Sehr geehrte Familie')} {str(fam_name).strip()},"
        elif sl_lower == "firma": 
            company_name_val = customer_data.get("company_name", "") or last_name 
            if company_name_val: return f"{get_text(texts, 'salutation_company_polite', 'Sehr geehrte Damen und Herren der Firma')} {str(company_name_val).strip()},"
            else: return get_text(texts, 'salutation_generic_fallback', 'Sehr geehrte Damen und Herren,')
    
    default_salutation_text = get_text(texts, salutation_key_base, "Sehr geehrte/r")
    
    if customer_full_name_for_salutation:
        return f"{default_salutation_text} {customer_full_name_for_salutation},"
    else: 
        return get_text(texts, 'salutation_generic_fallback', 'Sehr geehrte Damen und Herren,')


def _replace_placeholders(text_template: str, customer_data: Dict, company_info: Dict, offer_number: str, texts_dict: Dict[str, str], analysis_results_for_placeholder: Optional[Dict[str, Any]] = None) -> str:
    if text_template is None: text_template = ""
    processed_text = str(text_template)
    now_date_str = datetime.now().strftime('%d.%m.%Y')
    complete_salutation_line = _generate_complete_salutation_line(customer_data, texts_dict)
    
    ersatz_dict = {
        "[VollständigeAnrede]": complete_salutation_line,
        "[Ihr Name/Firmenname]": str(company_info.get("name", get_text(texts_dict, "company_name_default_placeholder_pdf", "Ihr Solarexperte"))),
        "[Angebotsnummer]": str(offer_number),
        "[Datum]": now_date_str,
        "[KundenNachname]": str(customer_data.get("last_name", "")),
        "[Nachname]": str(customer_data.get("last_name", "")),  # NEUER PLATZHALTER wie gewünscht
        "[KundenVorname]": str(customer_data.get("first_name", "")),
        "[KundenAnredeFormell]": str(customer_data.get("salutation", "")),
        "[KundenTitel]": str(customer_data.get("title", "")),
        "[KundenStrasseNr]": f"{customer_data.get('address','')} {customer_data.get('house_number','',)}".strip(),
        "[KundenPLZOrt]": f"{customer_data.get('zip_code','')} {customer_data.get('city','',)}".strip(),
        "[KundenFirmenname]": str(customer_data.get("company_name", "")),
    }
    if analysis_results_for_placeholder and isinstance(analysis_results_for_placeholder, dict):
        anlage_kwp_val = analysis_results_for_placeholder.get('anlage_kwp')
        ersatz_dict["[AnlagenleistungkWp]"] = format_kpi_value(anlage_kwp_val, "kWp", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if anlage_kwp_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")
        
        total_invest_brutto_val = analysis_results_for_placeholder.get('total_investment_brutto')
        ersatz_dict["[GesamtinvestitionBrutto]"] = format_kpi_value(total_invest_brutto_val, "€", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if total_invest_brutto_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")

        annual_benefit_yr1_val = analysis_results_for_placeholder.get('annual_financial_benefit_year1')
        ersatz_dict["[FinanziellerVorteilJahr1]"] = format_kpi_value(annual_benefit_yr1_val, "€", texts_dict=texts_dict, na_text_key="value_not_calculated_short") if annual_benefit_yr1_val is not None else get_text(texts_dict, "value_not_calculated_short", "k.B.")

    for placeholder, value_repl in ersatz_dict.items():
        processed_text = processed_text.replace(placeholder, str(value_repl))
    return processed_text

def _get_next_offer_number(texts: Dict[str,str], load_admin_setting_func: Callable, save_admin_setting_func: Callable) -> str:
    try:
        current_suffix_obj = load_admin_setting_func('offer_number_suffix', 1000)
        current_suffix = int(str(current_suffix_obj)) if current_suffix_obj is not None else 1000
        next_suffix = current_suffix + 1
        save_admin_setting_func('offer_number_suffix', next_suffix)
        return f"AN{datetime.now().year}-{next_suffix:04d}"
    except Exception: 
        return f"AN{datetime.now().strftime('%Y%m%d-%H%M%S')}"

def _prepare_cost_table_for_pdf(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[List[Any]]:
    cost_data_pdf = []
    cost_items_ordered_pdf = [
        ('base_matrix_price_netto', 'base_matrix_price_netto', True, 'TableText'),
        ('cost_modules_aufpreis_netto', 'cost_modules', True, 'TableText'),
        ('cost_inverter_aufpreis_netto', 'cost_inverter', True, 'TableText'),
        ('cost_storage_aufpreis_product_db_netto', 'cost_storage', True, 'TableText'),
        ('total_optional_components_cost_netto', 'total_optional_components_cost_netto_label', True, 'TableText'),
        ('cost_accessories_aufpreis_netto', 'cost_accessories_aufpreis_netto', True, 'TableText'),
        ('cost_scaffolding_netto', 'cost_scaffolding_netto', True, 'TableText'),
        ('cost_misc_netto', 'cost_misc_netto', True, 'TableText'),
        ('cost_custom_netto', 'cost_custom_netto', True, 'TableText'),
        ('subtotal_netto', 'subtotal_netto', True, 'TableBoldRight'),
        ('one_time_bonus_eur', 'one_time_bonus_eur_label', True, 'TableText'),
        ('total_investment_netto', 'total_investment_netto', True, 'TableBoldRight'),
        ('vat_rate_percent', 'vat_rate_percent', True, 'TableText'),
        ('total_investment_brutto', 'total_investment_brutto', True, 'TableBoldRight'),
    ]
    for result_key, label_key, is_euro_val, base_style_name in cost_items_ordered_pdf:
        value_cost = analysis_results.get(result_key)
        if value_cost is not None:
            if value_cost == 0.0 and result_key not in ['total_investment_netto', 'total_investment_brutto', 'subtotal_netto', 'vat_rate_percent', 'base_matrix_price_netto', 'one_time_bonus_eur']:
                continue
            label_text_pdf = get_text(texts, label_key, label_key.replace("_", " ").title())
            unit_pdf = "€" if is_euro_val else "%" if label_key == 'vat_rate_percent' else ""
            precision_pdf = 1 if label_key == 'vat_rate_percent' else 2
            formatted_value_str_pdf = format_kpi_value(value_cost, unit=unit_pdf, precision=precision_pdf, texts_dict=texts)
            value_style_name = base_style_name
            if result_key in ['total_investment_netto', 'total_investment_brutto', 'subtotal_netto']: value_style_name = 'TableBoldRight'
            elif is_euro_val or unit_pdf == "%": value_style_name = 'TableNumber'
            value_style = STYLES.get(value_style_name, STYLES['TableText'])
            cost_data_pdf.append([Paragraph(str(label_text_pdf), STYLES.get('TableLabel')), Paragraph(str(formatted_value_str_pdf), value_style)])
    return cost_data_pdf

def _prepare_simulation_table_for_pdf(analysis_results: Dict[str, Any], texts: Dict[str, str], num_years_to_show: int = 10) -> List[List[Any]]:
    sim_data_for_pdf_final: List[List[Any]] = []
    header_config_pdf = [
        (get_text(texts,"analysis_table_year_header","Jahr"), None, "", 0, 'TableText'),
        (get_text(texts,"annual_pv_production_kwh","PV Prod."), 'annual_productions_sim', "kWh", 0, 'TableNumber'),
        (get_text(texts,"annual_financial_benefit","Jährl. Vorteil"), 'annual_benefits_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"annual_maintenance_cost_sim","Wartung"), 'annual_maintenance_costs_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"analysis_table_annual_cf_header","Jährl. CF"), 'annual_cash_flows_sim', "€", 2, 'TableNumber'),
        (get_text(texts,"analysis_table_cumulative_cf_header","Kum. CF"), 'cumulative_cash_flows_sim_display', "€", 2, 'TableBoldRight')
    ]
    header_row_pdf = [Paragraph(hc[0], STYLES['TableHeader']) for hc in header_config_pdf]
    sim_data_for_pdf_final.append(header_row_pdf)

    sim_period_eff_pdf = int(analysis_results.get('simulation_period_years_effective', 0))
    if sim_period_eff_pdf == 0: return sim_data_for_pdf_final

    actual_years_to_display_pdf = min(sim_period_eff_pdf, num_years_to_show)
    cumulative_cash_flows_base_sim = analysis_results.get('cumulative_cash_flows_sim', [])
    if cumulative_cash_flows_base_sim and len(cumulative_cash_flows_base_sim) == (sim_period_eff_pdf + 1) :
        analysis_results['cumulative_cash_flows_sim_display'] = cumulative_cash_flows_base_sim[1:]
    else: 
        analysis_results['cumulative_cash_flows_sim_display'] = [None] * sim_period_eff_pdf

    for i_pdf in range(actual_years_to_display_pdf):
        row_items_formatted_pdf = [Paragraph(str(i_pdf + 1), STYLES.get(header_config_pdf[0][4]))]
        for j_pdf, header_conf_item in enumerate(header_config_pdf[1:]):
            result_key_pdf, unit_pdf, precision_pdf, style_name_data_pdf = header_conf_item[1], header_conf_item[2], header_conf_item[3], header_conf_item[4]
            current_list_pdf = analysis_results.get(str(result_key_pdf), [])
            value_to_format_pdf = current_list_pdf[i_pdf] if isinstance(current_list_pdf, list) and i_pdf < len(current_list_pdf) else None
            formatted_str_pdf = format_kpi_value(value_to_format_pdf, unit=unit_pdf, precision=precision_pdf, texts_dict=texts, na_text_key="value_not_available_short_pdf")
            row_items_formatted_pdf.append(Paragraph(str(formatted_str_pdf), STYLES.get(style_name_data_pdf, STYLES['TableText'])))
        sim_data_for_pdf_final.append(row_items_formatted_pdf)

    if sim_period_eff_pdf > num_years_to_show:
        ellipsis_row_pdf = [Paragraph("...", STYLES['TableText']) for _ in header_config_pdf]
        for cell_para_pdf in ellipsis_row_pdf: cell_para_pdf.style.alignment = TA_CENTER
        sim_data_for_pdf_final.append(ellipsis_row_pdf)
    return sim_data_for_pdf_final

def _create_product_table_with_image(details_data_prod: List[List[Any]], product_image_flowables_prod: List[Any], available_width: float) -> List[Any]:
    if not _REPORTLAB_AVAILABLE: return []
    story_elements: List[Any] = []
    if details_data_prod and product_image_flowables_prod:
        text_table_width = available_width * 0.62
        image_cell_width = available_width * 0.35
        text_table = Table(details_data_prod, colWidths=[text_table_width * 0.4, text_table_width * 0.6])
        text_table.setStyle(PRODUCT_TABLE_STYLE)
        image_cell_content = [Spacer(1, 0.1*cm)] + product_image_flowables_prod
        image_frame = KeepInFrame(image_cell_width, 6*cm, image_cell_content)
        combined_table_data = [[text_table, image_frame]]
        combined_table = Table(combined_table_data, colWidths=[text_table_width + 0.03*available_width, image_cell_width])
        combined_table.setStyle(PRODUCT_MAIN_TABLE_STYLE)
        story_elements.append(combined_table)
    elif details_data_prod:
        text_only_table = Table(details_data_prod, colWidths=[available_width * 0.4, available_width * 0.6])
        text_only_table.setStyle(PRODUCT_TABLE_STYLE)
        story_elements.append(text_only_table)
    elif product_image_flowables_prod:
        story_elements.extend(product_image_flowables_prod)
    return story_elements

def _add_product_details_to_story(
    story: List[Any], product_id: Optional[Union[int, float]],
    component_name_text: str, texts: Dict[str,str],
    available_width: float, get_product_by_id_func_param: Callable,
    include_product_images: bool
):
    """
    VERBESSERTE Produktdetails mit korrekten Bezeichnungen und Seitenumbruch-Schutz
    """
    if not _REPORTLAB_AVAILABLE: return
    
    # SEITENUMBRUCH-SCHUTZ: Sammle alle Elemente in einer Liste
    protected_elements: List[Any] = []
    
    product_details: Optional[Dict[str, Any]] = None
    if product_id is not None and callable(get_product_by_id_func_param):
        product_details = get_product_by_id_func_param(product_id)

    if not product_details:
        protected_elements.append(Paragraph(f"{component_name_text}: {get_text(texts,'details_not_available_pdf', 'Details nicht verfügbar')}", STYLES.get('NormalLeft')))
        protected_elements.append(Spacer(1, 0.3*cm))
        
        # SEITENUMBRUCH-SCHUTZ anwenden
        story.append(KeepTogether(protected_elements))
        return

    # VERBESSERTE PRODUKTBEZEICHNUNG
    brand = product_details.get('brand', '').strip()
    model = product_details.get('model_name', '').strip()
    
    # Korrekte Darstellung: "Marke Modell" oder fallback zu ursprünglichem Namen
    if brand and model:
        full_product_name = f"{brand} {model}"
    elif brand:
        full_product_name = brand
    elif model:
        full_product_name = model
    else:
        full_product_name = component_name_text
    
    # Titel mit vollständiger Produktbezeichnung
    protected_elements.append(Paragraph(f"{component_name_text}: {full_product_name}", STYLES.get('ComponentTitle')))
    
    details_data_prod: List[List[Any]] = []

    default_fields_prod = [
        ('brand', 'product_brand'), ('model_name', 'product_model'),
        ('warranty_years', 'product_warranty')
    ]
    component_specific_fields_prod: List[Tuple[str,str]] = []
    cat_lower_prod = str(product_details.get('category', "")).lower()

    if cat_lower_prod == 'modul':
        component_specific_fields_prod = [('capacity_w', 'product_capacity_wp'), ('efficiency_percent', 'product_efficiency'), ('length_m', 'product_length_m'), ('width_m', 'product_width_m'), ('weight_kg', 'product_weight_kg')]
    elif cat_lower_prod == 'wechselrichter':
        component_specific_fields_prod = [('power_kw', 'product_power_kw'), ('efficiency_percent', 'product_efficiency_inverter')]
    elif cat_lower_prod == 'batteriespeicher':
        component_specific_fields_prod = [('storage_power_kw', 'product_capacity_kwh'), ('power_kw', 'product_power_storage_kw'), ('max_cycles', 'product_max_cycles_label')]
    elif cat_lower_prod == 'wallbox':
        component_specific_fields_prod = [('power_kw', 'product_power_wallbox_kw')]
    elif cat_lower_prod == 'energiemanagementsystem': # HINZUGEFÜGT: EMS
        component_specific_fields_prod = [('description', 'product_description_short')] # Beispiel, anpassen!
    elif cat_lower_prod == 'leistungsoptimierer': # HINZUGEFÜGT: Optimierer
        component_specific_fields_prod = [('efficiency_percent', 'product_optimizer_efficiency')] # Beispiel
    elif cat_lower_prod == 'carport': # HINZUGEFÜGT: Carport
        component_specific_fields_prod = [('length_m', 'product_length_m'), ('width_m', 'product_width_m')] # Beispiel
    # Notstrom und Tierabwehr könnten generische Felder wie Beschreibung verwenden oder spezifische, falls vorhanden
    elif cat_lower_prod == 'notstromversorgung':
        component_specific_fields_prod = [('power_kw', 'product_emergency_power_kw')] # Beispiel
    elif cat_lower_prod == 'tierabwehrschutz':
        component_specific_fields_prod = [('description', 'product_description_short')] # Beispiel
    
    all_fields_to_display_prod = default_fields_prod + component_specific_fields_prod
    for key_prod, label_text_key_prod in all_fields_to_display_prod:
        value_prod = product_details.get(key_prod)
        label_prod = get_text(texts, label_text_key_prod, key_prod.replace("_", " ").title())
        
        if value_prod is not None and str(value_prod).strip() != "":
            unit_prod, prec_prod = "", 2
            if key_prod == 'capacity_w': unit_prod, prec_prod = "Wp", 0
            elif key_prod == 'power_kw': unit_prod, prec_prod = "kW", 1 # Für WR, Speicher, Wallbox etc.
            elif key_prod == 'storage_power_kw': unit_prod, prec_prod = "kWh", 1
            elif key_prod.endswith('_percent'): unit_prod, prec_prod = "%", 1
            elif key_prod == 'warranty_years': unit_prod, prec_prod = "Jahre", 0
            elif key_prod == 'max_cycles': unit_prod, prec_prod = "Zyklen", 0
            elif key_prod.endswith('_m'): unit_prod, prec_prod = "m", 3
            elif key_prod == 'weight_kg': unit_prod, prec_prod = "kg", 1
            
            value_str_prod = format_kpi_value(value_prod, unit=unit_prod, precision=prec_prod, texts_dict=texts, na_text_key="value_not_available_short_pdf")
            details_data_prod.append([Paragraph(str(label_prod), STYLES.get('TableLabel')), Paragraph(str(value_str_prod), STYLES.get('TableText'))])

    product_image_flowables_prod: List[Any] = []
    if include_product_images:
        product_image_base64_prod = product_details.get('image_base64')
        if product_image_base64_prod:
            img_w_prod = min(available_width * 0.30, 5*cm); img_h_max_prod = 5*cm
            product_image_flowables_prod = _get_image_flowable(product_image_base64_prod, img_w_prod, texts, None, img_h_max_prod, align='CENTER')
    
    # Tabelle zu geschützten Elementen hinzufügen
    table_elements = _create_product_table_with_image(details_data_prod, product_image_flowables_prod, available_width)
    protected_elements.extend(table_elements)
    
    # Beschreibung hinzufügen
    description_prod_val = product_details.get('description')
    if description_prod_val and str(description_prod_val).strip():
        protected_elements.append(Spacer(1, 0.2*cm))
        protected_elements.append(Paragraph(f"<i>{str(description_prod_val).strip()}</i>", STYLES.get('TableTextSmall')))
    
    protected_elements.append(Spacer(1, 0.5*cm))

    # SEITENUMBRUCH-SCHUTZ: Gesamtes Produktmodul zusammenhalten
    story.append(KeepTogether(protected_elements))


def generate_offer_pdf(
    project_data: Dict, analysis_results: Dict, company_info: Dict, 
    company_logo_base64: Optional[str] = None,
    selected_title_image_b64: Optional[str] = None,
    selected_offer_title_text: str = "Ihr Angebot",
    selected_cover_letter_text: str = "",
    sections_to_include: Optional[List[str]] = None,
    inclusion_options: Optional[Dict[str, Any]] = None,
    load_admin_setting_func: Optional[Callable] = None,
    save_admin_setting_func: Optional[Callable] = None,
    list_products_func: Optional[Callable] = None,
    get_product_by_id_func: Optional[Callable] = None,
    db_list_company_documents_func: Optional[Callable] = None,
    active_company_id: Optional[int] = None,
    texts: Optional[Dict[str, str]] = None,
    **kwargs
) -> Optional[bytes]:
    
    # Fallback-Funktionen wenn nicht bereitgestellt
    if not load_admin_setting_func:
        load_admin_setting_func = lambda key, default: default
    if not save_admin_setting_func:
        save_admin_setting_func = lambda key, value: True
    
    # Validierung der erforderlichen Parameter
    if not texts:
        texts = {}
    if not inclusion_options:
        inclusion_options = {}
    if not sections_to_include:
        sections_to_include = ["ProjectOverview", "TechnicalComponents", "CostDetails", "Economics", "SimulationDetails", "CO2Savings", "Visualizations", "FutureAspects"]
        
    if not _REPORTLAB_AVAILABLE:
        if project_data and texts and company_info:
            return _create_plaintext_pdf_fallback(project_data, analysis_results, texts, company_info, selected_offer_title_text, selected_cover_letter_text)
        return None

    # DATENVALIDIERUNG: Prüfe Verfügbarkeit der erforderlichen Daten
    validation_result = {'is_valid': True, 'warnings': [], 'critical_errors': [], 'missing_data_summary': []}
    # validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
    
    # Wenn kritische Daten fehlen, erstelle Fallback-PDF
    if not validation_result['is_valid']:
        print(f"⚠️ PDF-Erstellung: Kritische Daten fehlen: {', '.join(validation_result['critical_errors'])}")
        customer_data = project_data.get('customer_data', {}) if project_data else {}
        return _create_no_data_fallback_pdf(texts, customer_data)
    
    # Warnungen ausgeben, wenn Daten unvollständig sind
    if validation_result['warnings']:
        print(f"⚠️ PDF-Erstellung: Daten unvollständig: {', '.join(validation_result['missing_data_summary'])}")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")

    design_settings = {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
    # design_settings = load_admin_setting_func('pdf_design_settings', {'primary_color': PRIMARY_COLOR_HEX, 'secondary_color': SECONDARY_COLOR_HEX})
    if isinstance(design_settings, dict):
        _update_styles_with_dynamic_colors(design_settings)
    
    main_offer_buffer = io.BytesIO()
    offer_number_final = _get_next_offer_number(texts, load_admin_setting_func, save_admin_setting_func)
    
    include_company_logo_opt = inclusion_options.get("include_company_logo", True)
    include_product_images_opt = inclusion_options.get("include_product_images", True)
    include_all_documents_opt = inclusion_options.get("include_all_documents", True) # Korrigierter Key
    company_document_ids_to_include_opt = inclusion_options.get("company_document_ids_to_include", [])
    include_optional_component_details_opt = inclusion_options.get("include_optional_component_details", True) # NEUE Option
    
    # NEUE OPTIONEN für Footer und Header-Logo (wie gewünscht)
    include_custom_footer_opt = inclusion_options.get("include_custom_footer", True)  
    include_header_logo_opt = inclusion_options.get("include_header_logo", True)

    doc = SimpleDocTemplate(main_offer_buffer, title=get_text(texts, "pdf_offer_title_doc_param", "Angebot: Photovoltaikanlage").format(offer_number=offer_number_final),
                            author=company_info.get("name", "SolarFirma"), pagesize=pagesizes.A4,
                            leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)

    story: List[Any] = []
    
    current_project_data_pdf = project_data if isinstance(project_data, dict) else {}
    current_analysis_results_pdf = analysis_results if isinstance(analysis_results, dict) else {}
    customer_pdf = current_project_data_pdf.get("customer_data", {})
    pv_details_pdf = current_project_data_pdf.get("project_details", {})
    available_width_content = doc.width

    # --- Deckblatt ---
    try:
        if selected_title_image_b64:
            img_flowables_title = _get_image_flowable(selected_title_image_b64, doc.width, texts, max_height=doc.height / 1.8, align='CENTER')
            if img_flowables_title: story.extend(img_flowables_title); story.append(Spacer(1, 0.5 * cm))

        if include_company_logo_opt and company_logo_base64:
            logo_flowables_deckblatt = _get_image_flowable(company_logo_base64, 6*cm, texts, max_height=3*cm, align='CENTER')
            if logo_flowables_deckblatt: story.extend(logo_flowables_deckblatt); story.append(Spacer(1, 0.5 * cm))

        offer_title_processed_pdf = _replace_placeholders(selected_offer_title_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
        story.append(Paragraph(offer_title_processed_pdf, STYLES.get('OfferTitle')))
        
        company_info_html_pdf = "<br/>".join(filter(None, [
            f"<b>{company_info.get('name', '')}</b>", company_info.get("street", ""),
            f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip(),
            (f"{get_text(texts, 'pdf_phone_label_short', 'Tel.')}: {company_info.get('phone', '')}" if company_info.get('phone') else None),
            (f"{get_text(texts, 'pdf_email_label_short', 'Mail')}: {company_info.get('email', '')}" if company_info.get('email') else None),
            (f"{get_text(texts, 'pdf_website_label_short', 'Web')}: {company_info.get('website', '')}" if company_info.get('website') else None),
            (f"{get_text(texts, 'pdf_taxid_label', 'StNr/USt-ID')}: {company_info.get('tax_id', '')}" if company_info.get('tax_id') else None),
        ]))
        story.append(Paragraph(company_info_html_pdf, STYLES.get('CompanyInfoDeckblatt')))
          # KORRIGIERTES 4-ZEILEN-FORMAT wie gewünscht:
        # [Anrede] [Titel]
        # [Nachname] [Vorname]  
        # [Strasse] [Hausnummer]
        # [Postleitzahl] [Ort]
        line1 = f"{customer_pdf.get('salutation','')} {customer_pdf.get('title','')}".strip()
        line2 = f"{customer_pdf.get('last_name','')} {customer_pdf.get('first_name','')}".strip()
        line3 = f"{customer_pdf.get('address','')} {customer_pdf.get('house_number','')}".strip()
        line4 = f"{customer_pdf.get('zip_code','')} {customer_pdf.get('city','')}".strip()
        
        customer_address_block_pdf_lines = [line1, line2, line3, line4]
        # Firmenname falls vorhanden zusätzlich einfügen
        if customer_pdf.get("company_name"):
            customer_address_block_pdf_lines.insert(1, str(customer_pdf.get("company_name")))
            
        customer_address_block_pdf = "<br/>".join(filter(None, customer_address_block_pdf_lines))
        story.append(Paragraph(customer_address_block_pdf, STYLES.get("CustomerAddress")))
        
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"{get_text(texts, 'pdf_offer_number_label', 'Angebotsnummer')}: <b>{offer_number_final}</b>", STYLES.get('NormalRight')))
        story.append(Paragraph(f"{get_text(texts, 'pdf_offer_date_label', 'Datum')}: {datetime.now().strftime('%d.%m.%Y')}", STYLES.get('NormalRight')))
        story.append(PageBreak())
    except Exception as e_cover:
        story.append(Paragraph(f"Fehler bei Erstellung des Deckblatts: {e_cover}", STYLES.get('NormalLeft')))
        story.append(PageBreak())
    
    if not _REPORTLAB_AVAILABLE:
        if project_data and texts and company_info:
            return _create_plaintext_pdf_fallback(project_data, analysis_results, texts, company_info, selected_offer_title_text, selected_cover_letter_text)
        return None
    
    # DATENVALIDIERUNG: Prüfe Verfügbarkeit der erforderlichen Daten
    validation_result = {'is_valid': True, 'warnings': [], 'critical_errors': [], 'missing_data_summary': []}
    # validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
    
    # Wenn kritische Daten fehlen, erstelle Fallback-PDF
    if not validation_result['is_valid']:
        print(f"⚠️ PDF-Erstellung: Kritische Daten fehlen: {', '.join(validation_result['critical_errors'])}")
        customer_data = project_data.get('customer_data', {}) if project_data else {}
        return _create_no_data_fallback_pdf(texts, customer_data)
    
    # Warnungen ausgeben, wenn Daten unvollständig sind
    if validation_result['warnings']:
        print(f"⚠️ PDF-Erstellung: Daten unvollständig: {', '.join(validation_result['missing_data_summary'])}")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")
    
    design_settings = {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
    # design_settings = load_admin_setting_func('pdf_design_settings', {'primary_color': PRIMARY_COLOR_HEX, 'secondary_color': SECONDARY_COLOR_HEX})
    if isinstance(design_settings, dict):
        _update_styles_with_dynamic_colors(design_settings)
    
    main_offer_buffer = io.BytesIO()
    offer_number_final = _get_next_offer_number(texts, load_admin_setting_func, save_admin_setting_func)
    
    include_company_logo_opt = inclusion_options.get("include_company_logo", True)
    include_product_images_opt = inclusion_options.get("include_product_images", True)
    include_all_documents_opt = inclusion_options.get("include_all_documents", True) # Korrigierter Key
    company_document_ids_to_include_opt = inclusion_options.get("company_document_ids_to_include", [])
    include_optional_component_details_opt = inclusion_options.get("include_optional_component_details", True) # NEUE Option
    
    # NEUE OPTIONEN für Footer und Header-Logo (wie gewünscht)
    include_custom_footer_opt = inclusion_options.get("include_custom_footer", True)  
    include_header_logo_opt = inclusion_options.get("include_header_logo", True)

    doc = SimpleDocTemplate(main_offer_buffer, title=get_text(texts, "pdf_offer_title_doc_param", "Angebot: Photovoltaikanlage").format(offer_number=offer_number_final),
                            author=company_info.get("name", "SolarFirma"), pagesize=pagesizes.A4,
                            leftMargin=2*cm, rightMargin=2*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)

    story: List[Any] = []
    
    current_project_data_pdf = project_data if isinstance(project_data, dict) else {}
    current_analysis_results_pdf = analysis_results if isinstance(analysis_results, dict) else {}
    customer_pdf = current_project_data_pdf.get("customer_data", {})
    pv_details_pdf = current_project_data_pdf.get("project_details", {})
    available_width_content = doc.width

    # --- Deckblatt ---
    try:
        if selected_title_image_b64:
            img_flowables_title = _get_image_flowable(selected_title_image_b64, doc.width, texts, max_height=doc.height / 1.8, align='CENTER')
            if img_flowables_title: story.extend(img_flowables_title); story.append(Spacer(1, 0.5 * cm))

        if include_company_logo_opt and company_logo_base64:
            logo_flowables_deckblatt = _get_image_flowable(company_logo_base64, 6*cm, texts, max_height=3*cm, align='CENTER')
            if logo_flowables_deckblatt: story.extend(logo_flowables_deckblatt); story.append(Spacer(1, 0.5 * cm))

        offer_title_processed_pdf = _replace_placeholders(selected_offer_title_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
        story.append(Paragraph(offer_title_processed_pdf, STYLES.get('OfferTitle')))
        
        company_info_html_pdf = "<br/>".join(filter(None, [
            f"<b>{company_info.get('name', '')}</b>", company_info.get("street", ""),
            f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip(),
            (f"{get_text(texts, 'pdf_phone_label_short', 'Tel.')}: {company_info.get('phone', '')}" if company_info.get('phone') else None),
            (f"{get_text(texts, 'pdf_email_label_short', 'Mail')}: {company_info.get('email', '')}" if company_info.get('email') else None),
            (f"{get_text(texts, 'pdf_website_label_short', 'Web')}: {company_info.get('website', '')}" if company_info.get('website') else None),
            (f"{get_text(texts, 'pdf_taxid_label', 'StNr/USt-ID')}: {company_info.get('tax_id', '')}" if company_info.get('tax_id') else None),
        ]))
        story.append(Paragraph(company_info_html_pdf, STYLES.get('CompanyInfoDeckblatt')))
          # KORRIGIERTES 4-ZEILEN-FORMAT wie gewünscht:
        # [Anrede] [Titel]
        # [Nachname] [Vorname]  
        # [Strasse] [Hausnummer]
        # [Postleitzahl] [Ort]
        line1 = f"{customer_pdf.get('salutation','')} {customer_pdf.get('title','')}".strip()
        line2 = f"{customer_pdf.get('last_name','')} {customer_pdf.get('first_name','')}".strip()
        line3 = f"{customer_pdf.get('address','')} {customer_pdf.get('house_number','')}".strip()
        line4 = f"{customer_pdf.get('zip_code','')} {customer_pdf.get('city','')}".strip()
        
        customer_address_block_pdf_lines = [line1, line2, line3, line4]
        # Firmenname falls vorhanden zusätzlich einfügen
        if customer_pdf.get("company_name"):
            customer_address_block_pdf_lines.insert(1, str(customer_pdf.get("company_name")))
            
        customer_address_block_pdf = "<br/>".join(filter(None, customer_address_block_pdf_lines))
        story.append(Paragraph(customer_address_block_pdf, STYLES.get("CustomerAddress")))
        
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"{get_text(texts, 'pdf_offer_number_label', 'Angebotsnummer')}: <b>{offer_number_final}</b>", STYLES.get('NormalRight')))
        story.append(Paragraph(f"{get_text(texts, 'pdf_offer_date_label', 'Datum')}: {datetime.now().strftime('%d.%m.%Y')}", STYLES.get('NormalRight')))
        story.append(PageBreak())
    except Exception as e_cover:
        story.append(Paragraph(f"Fehler bei Erstellung des Deckblatts: {e_cover}", STYLES.get('NormalLeft')))
        story.append(PageBreak())

    # --- Anschreiben ---
    try:
        story.append(SetCurrentChapterTitle(get_text(texts, "pdf_chapter_title_cover_letter", "Anschreiben")))
        company_sender_address_lines = [company_info.get("name", ""), company_info.get("street", ""), f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip()]
        story.append(Paragraph("<br/>".join(filter(None,company_sender_address_lines)), STYLES.get('NormalLeft'))) 
        story.append(Spacer(1, 1.5*cm))
        story.append(Paragraph(customer_address_block_pdf, STYLES.get('NormalLeft')))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(datetime.now().strftime('%d.%m.%Y'), STYLES.get('NormalRight')))
        story.append(Spacer(1, 0.5*cm))
        offer_subject_text = get_text(texts, "pdf_offer_subject_line_param", "Ihr persönliches Angebot für eine Photovoltaikanlage, Nr. {offer_number}").format(offer_number=offer_number_final)
        story.append(Paragraph(f"<b>{offer_subject_text}</b>", STYLES.get('NormalLeft')))
        story.append(Spacer(1, 0.5*cm))

        cover_letter_processed_pdf = _replace_placeholders(selected_cover_letter_text, customer_pdf, company_info, offer_number_final, texts, current_analysis_results_pdf)
        cover_letter_paragraphs = cover_letter_processed_pdf.split('\n') 
        for para_text in cover_letter_paragraphs:
            if para_text.strip(): 
                story.append(Paragraph(para_text.replace('\r',''), STYLES.get('CoverLetter'))) 
            else: 
                story.append(Spacer(1, 0.2*cm)) 
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(get_text(texts, "pdf_closing_greeting", "Mit freundlichen Grüßen"), STYLES.get('NormalLeft')))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(str(company_info.get("name", "")), STYLES.get('NormalLeft')))
        story.append(PageBreak())
    except Exception as e_letter:
        story.append(Paragraph(f"Fehler bei Erstellung des Anschreibens: {e_letter}", STYLES.get('NormalLeft')))
        story.append(PageBreak())    # --- Dynamische Sektionen ---
    active_sections_set_pdf = set(sections_to_include or [])
    
    section_chapter_titles_map = {
        "ProjectOverview": get_text(texts, "pdf_chapter_title_overview", "Projektübersicht"),
        "TechnicalComponents": get_text(texts, "pdf_chapter_title_components", "Komponenten"),
        "CostDetails": get_text(texts, "pdf_chapter_title_cost_details", "Kosten"),
        "Economics": get_text(texts, "pdf_chapter_title_economics", "Wirtschaftlichkeit"),
        "SimulationDetails": get_text(texts, "pdf_chapter_title_simulation", "Simulation"),
        "CO2Savings": get_text(texts, "pdf_chapter_title_co2", "CO₂-Einsparung"),
        "Visualizations": get_text(texts, "pdf_chapter_title_visualizations", "Visualisierungen"),
        "FutureAspects": get_text(texts, "pdf_chapter_title_future_aspects", "Zukunftsaspekte"),
        
        # NEUE OPTIONALE SEITENVORLAGEN (5+ wie gewünscht)
        "CompanyProfile": get_text(texts, "pdf_chapter_title_company_profile", "Unternehmensprofil"),
        "Certifications": get_text(texts, "pdf_chapter_title_certifications", "Zertifizierungen & Qualität"),
        "References": get_text(texts, "pdf_chapter_title_references", "Referenzen & Kundenstimmen"), 
        "Installation": get_text(texts, "pdf_chapter_title_installation", "Installation & Montage"),
        "Maintenance": get_text(texts, "pdf_chapter_title_maintenance", "Wartung & Service"),        "Financing": get_text(texts, "pdf_chapter_title_financing", "Finanzierungsmöglichkeiten"),
        "Insurance": get_text(texts, "pdf_chapter_title_insurance", "Versicherungsschutz"),
        "Warranty": get_text(texts, "pdf_chapter_title_warranty", "Garantie & Gewährleistung")
    }
    
    ordered_section_definitions_pdf = [
        ("ProjectOverview", "pdf_section_title_overview", "1. Projektübersicht & Eckdaten"),
        ("TechnicalComponents", "pdf_section_title_components", "2. Angebotene Systemkomponenten"),
        ("CostDetails", "pdf_section_title_cost_details", "3. Detaillierte Kostenaufstellung"),
        ("Economics", "pdf_section_title_economics", "4. Wirtschaftlichkeit im Überblick"),
        ("SimulationDetails", "pdf_section_title_simulation", "5. Simulationsübersicht (Auszug)"),
        ("CO2Savings", "pdf_section_title_co2", "6. Ihre CO₂-Einsparung"),
        ("Visualizations", "pdf_section_title_visualizations", "7. Grafische Auswertungen"),
        ("FutureAspects", "pdf_chapter_title_future_aspects", "8. Zukunftsaspekte & Erweiterungen"),
        
        # NEUE OPTIONALE SEITENVORLAGEN (individuell gestaltbar)
        ("CompanyProfile", "pdf_section_title_company_profile", "9. Unser Unternehmen"),
        ("Certifications", "pdf_section_title_certifications", "10. Zertifizierungen & Qualitätsstandards"),
        ("References", "pdf_section_title_references", "11. Referenzen & Kundenerfahrungen"),
        ("Installation", "pdf_section_title_installation", "12. Professionelle Installation"),
        ("Maintenance", "pdf_section_title_maintenance", "13. Wartung & Langzeitservice"),
        ("Financing", "pdf_section_title_financing", "14. Flexible Finanzierungslösungen"),
        ("Insurance", "pdf_section_title_insurance", "15. Umfassender Versicherungsschutz"),        ("Warranty", "pdf_section_title_warranty", "16. Herstellergarantie & Gewährleistung")
    ]
    current_section_counter_pdf = 1
    for section_key_current, title_text_key_current, default_title_current in ordered_section_definitions_pdf:
        if section_key_current in active_sections_set_pdf:
            try:
                chapter_title_for_header_current = section_chapter_titles_map.get(section_key_current, default_title_current.split('. ',1)[-1] if '. ' in default_title_current else default_title_current)
                story.append(SetCurrentChapterTitle(chapter_title_for_header_current))
                numbered_title_current = f"{current_section_counter_pdf}. {get_text(texts, title_text_key_current, default_title_current.split('. ',1)[-1] if '. ' in default_title_current else default_title_current)}"
                story.append(Paragraph(numbered_title_current, STYLES.get('SectionTitle')))
                story.append(Spacer(1, 0.2 * cm))

                if section_key_current == "ProjectOverview":
                    if pv_details_pdf.get('visualize_roof_in_pdf_satellite', False) and pv_details_pdf.get('satellite_image_base64_data'):
                        story.append(Paragraph(get_text(texts,"satellite_image_header_pdf","Satellitenansicht Objekt"), STYLES.get('SubSectionTitle')))
                        sat_img_flowables = _get_image_flowable(pv_details_pdf['satellite_image_base64_data'], available_width_content * 0.8, texts, caption_text_key="satellite_image_caption_pdf", max_height=10*cm)
                        if sat_img_flowables: story.extend(sat_img_flowables); story.append(Spacer(1, 0.5*cm))
                    
                    overview_data_content_pdf = [
                        [get_text(texts,"anlage_size_label_pdf", "Anlagengröße"),format_kpi_value(current_analysis_results_pdf.get('anlage_kwp'),"kWp",texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                        [get_text(texts,"module_quantity_label_pdf","Anzahl Module"),str(pv_details_pdf.get('module_quantity', get_text(texts, "value_not_available_short_pdf")))],
                        [get_text(texts,"annual_pv_production_kwh_pdf", "Jährliche PV-Produktion (ca.)"),format_kpi_value(current_analysis_results_pdf.get('annual_pv_production_kwh'),"kWh",precision=0,texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                        [get_text(texts,"self_supply_rate_percent_pdf", "Autarkiegrad (ca.)"),format_kpi_value(current_analysis_results_pdf.get('self_supply_rate_percent'),"%",precision=1,texts_dict=texts, na_text_key="value_not_available_short_pdf")],
                    ]
                    if pv_details_pdf.get('include_storage'):
                         overview_data_content_pdf.extend([[get_text(texts,"selected_storage_capacity_label_pdf", "Speicherkapazität"),format_kpi_value(pv_details_pdf.get('selected_storage_storage_power_kw'),"kWh",texts_dict=texts, na_text_key="value_not_available_short_pdf")]])
                    if overview_data_content_pdf:
                        overview_table_data_styled_content_pdf = [[Paragraph(str(cell[0]),STYLES.get('TableLabel')),Paragraph(str(cell[1]),STYLES.get('TableText'))] for cell in overview_data_content_pdf]
                        overview_table_content_pdf = Table(overview_table_data_styled_content_pdf,colWidths=[available_width_content*0.5,available_width_content*0.5])
                        overview_table_content_pdf.setStyle(TABLE_STYLE_DEFAULT)
                        
                        # SEITENUMBRUCH-SCHUTZ für Übersichtstabelle
                        story.append(KeepTogether([overview_table_content_pdf]))

                elif section_key_current == "TechnicalComponents":
                    story.append(Paragraph(get_text(texts, "pdf_components_intro", "Nachfolgend die Details zu den Kernkomponenten Ihrer Anlage:"), STYLES.get('NormalLeft')))
                   
                    story.append(Spacer(1, 0.3*cm))
                    
                    main_components = [
                        (pv_details_pdf.get("selected_module_id"), get_text(texts, "pdf_component_module_title", "PV-Module")),
                        (pv_details_pdf.get("selected_inverter_id"), get_text(texts, "pdf_component_inverter_title", "Wechselrichter")),
                    ]
                    if pv_details_pdf.get("include_storage"):
                        main_components.append((pv_details_pdf.get("selected_storage_id"), get_text(texts, "pdf_component_storage_title", "Batteriespeicher")))
                    
                    for comp_id, comp_title in main_components:
                        if comp_id: _add_product_details_to_story(story, comp_id, comp_title, texts, available_width_content, get_product_by_id_func, include_product_images_opt)

                    # ERWEITERUNG: Optionale Komponenten / Zubehör
                    if pv_details_pdf.get('include_additional_components', True) and include_optional_component_details_opt:
                        story.append(Paragraph(get_text(texts, "pdf_additional_components_header_pdf", "Optionale Komponenten"), STYLES.get('SubSectionTitle')))
                        optional_comps_map = {
                            'selected_wallbox_id': get_text(texts, "pdf_component_wallbox_title", "Wallbox"),
                            'selected_ems_id': get_text(texts, "pdf_component_ems_title", "Energiemanagementsystem"),
                            'selected_optimizer_id': get_text(texts, "pdf_component_optimizer_title", "Leistungsoptimierer"),
                            'selected_carport_id': get_text(texts, "pdf_component_carport_title", "Solarcarport"),
                            'selected_notstrom_id': get_text(texts, "pdf_component_emergency_power_title", "Notstromversorgung"),
                            'selected_tierabwehr_id': get_text(texts, "pdf_component_animal_defense_title", "Tierabwehrschutz")
                        }
                        any_optional_component_rendered = True
                        for key, title in optional_comps_map.items():
                            opt_comp_id = pv_details_pdf.get(key)
                            if opt_comp_id: 
                                _add_product_details_to_story(story, opt_comp_id, title, texts, available_width_content, get_product_by_id_func, include_product_images_opt)
                                any_optional_component_rendered = True
                        if not any_optional_component_rendered:
                            story.append(Paragraph(get_text(texts, "pdf_no_optional_components_selected_for_details", "Keine optionalen Komponenten für Detailanzeige ausgewählt."), STYLES.get('NormalLeft')))
                        
                elif section_key_current == "CostDetails":
                    cost_table_data_final_pdf = _prepare_cost_table_for_pdf(current_analysis_results_pdf, texts)
                    if cost_table_data_final_pdf:
                        cost_table_obj_final_pdf = Table(cost_table_data_final_pdf, colWidths=[available_width_content*0.6, available_width_content*0.4])
                        cost_table_obj_final_pdf.setStyle(TABLE_STYLE_DEFAULT)
                        
                        # SEITENUMBRUCH-SCHUTZ für Kostentabelle
                        cost_elements = [cost_table_obj_final_pdf]
                        
                        if current_analysis_results_pdf.get('base_matrix_price_netto', 0.0) == 0 and current_analysis_results_pdf.get('cost_storage_aufpreis_product_db_netto', 0.0) > 0: 
                            cost_elements.extend([Spacer(1,0.2*cm), Paragraph(get_text(texts, "analysis_storage_cost_note_single_price_pdf", "<i>Hinweis: Speicherkosten als Einzelposten, da kein Matrix-Pauschalpreis.</i>"), STYLES.get('TableTextSmall'))])
                        elif current_analysis_results_pdf.get('base_matrix_price_netto', 0.0) > 0 and current_analysis_results_pdf.get('cost_storage_aufpreis_product_db_netto', 0.0) > 0:
                            cost_elements.extend([Spacer(1,0.2*cm), Paragraph(get_text(texts, "analysis_storage_cost_note_matrix_pdf", "<i>Hinweis: Speicherkosten als Aufpreis, da Matrixpreis 'Ohne Speicher' verwendet wurde.</i>"), STYLES.get('TableTextSmall'))])
                        
                        story.append(KeepTogether(cost_elements))

                elif section_key_current == "Economics":
                    eco_kpi_data_for_pdf_table = [
                        [get_text(texts, "total_investment_brutto_pdf", "Gesamtinvestition (Brutto)"), format_kpi_value(current_analysis_results_pdf.get('total_investment_brutto'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "annual_financial_benefit_pdf", "Finanzieller Vorteil (Jahr 1, ca.)"), format_kpi_value(current_analysis_results_pdf.get('annual_financial_benefit_year1'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "amortization_time_years_pdf", "Amortisationszeit (ca.)"), format_kpi_value(current_analysis_results_pdf.get('amortization_time_years'), "Jahre", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "simple_roi_percent_label_pdf", "Einfache Rendite (Jahr 1, ca.)"), format_kpi_value(current_analysis_results_pdf.get('simple_roi_percent'), "%", precision=1, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "lcoe_euro_per_kwh_label_pdf", "Stromgestehungskosten (LCOE, ca.)"), format_kpi_value(current_analysis_results_pdf.get('lcoe_euro_per_kwh'), "€/kWh", precision=3, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "npv_over_years_pdf", "Kapitalwert über Laufzeit (NPV, ca.)"), format_kpi_value(current_analysis_results_pdf.get('npv_value'), "€", texts_dict=texts, na_text_key="value_not_calculated_short_pdf")],
                        [get_text(texts, "irr_percent_pdf", "Interner Zinsfuß (IRR, ca.)"), format_kpi_value(current_analysis_results_pdf.get('irr_percent'), "%", precision=1, texts_dict=texts, na_text_key="value_not_calculated_short_pdf")]                    ]
                    if eco_kpi_data_for_pdf_table:
                        eco_kpi_table_styled_content = [[Paragraph(str(cell[0]), STYLES.get('TableLabel')), Paragraph(str(cell[1]), STYLES.get('TableNumber'))] for cell in eco_kpi_data_for_pdf_table]
                        eco_table_object = Table(eco_kpi_table_styled_content, colWidths=[available_width_content*0.6, available_width_content*0.4])
                        eco_table_object.setStyle(TABLE_STYLE_DEFAULT)
                          # SEITENUMBRUCH-SCHUTZ für Wirtschaftlichkeitstabelle
                        story.append(KeepTogether([eco_table_object]))
                        
                elif section_key_current == "SimulationDetails":
                    sim_table_data_content_pdf = _prepare_simulation_table_for_pdf(current_analysis_results_pdf, texts, num_years_to_show=10)
                    if len(sim_table_data_content_pdf) > 1:
                        sim_table_obj_final_pdf = Table(sim_table_data_content_pdf, colWidths=None)
                        sim_table_obj_final_pdf.setStyle(DATA_TABLE_STYLE)
                        
                        # SEITENUMBRUCH-SCHUTZ für Simulationstabelle
                        story.append(KeepTogether([sim_table_obj_final_pdf]))
                    else: 
                        story.append(Paragraph(get_text(texts, "pdf_simulation_data_not_available", "Simulationsdetails nicht ausreichend für Tabellendarstellung."), STYLES.get('NormalLeft')))

                elif section_key_current == "CO2Savings":
                    co2_savings_val = current_analysis_results_pdf.get('annual_co2_savings_kg', 0.0)
                    trees_equiv = current_analysis_results_pdf.get('co2_equivalent_trees_per_year', 0.0)
                    car_km_equiv = current_analysis_results_pdf.get('co2_equivalent_car_km_per_year', 0.0)
                    airplane_km_equiv = co2_savings_val / 0.23 if co2_savings_val > 0 else 0.0
                    
                    # Verbesserter CO₂-Text mit mehr Details und professioneller Formatierung
                    co2_intro = get_text(texts, "pdf_co2_intro", "Mit Ihrer neuen Photovoltaikanlage leisten Sie einen wertvollen Beitrag zum Klimaschutz:")
                    story.append(Paragraph(co2_intro, STYLES.get('NormalLeft')))
                    story.append(Spacer(1, 0.2 * cm))
                    
                    # Haupteinsparung hervorheben
                    co2_main = get_text(texts, "pdf_annual_co2_main", "🌱 <b>Jährliche CO₂-Einsparung: {co2_savings_kg_formatted} kg</b>").format(
                        co2_savings_kg_formatted=format_kpi_value(co2_savings_val, "", precision=0, texts_dict=texts)
                    )
                    story.append(Paragraph(co2_main, STYLES.get('HeadingCenter')))
                    story.append(Spacer(1, 0.3 * cm))
                    
                    # Anschauliche Vergleiche in einer schönen Tabelle
                    co2_data = [
                        [get_text(texts, "pdf_co2_comparison_header", "Vergleich"), get_text(texts, "pdf_co2_equivalent_header", "Entspricht")],
                        ["🌳 Bäume (CO₂-Bindung)", f"{trees_equiv:.0f} Bäume pro Jahr"],
                        ["🚗 Autofahrten", f"{car_km_equiv:,.0f} km weniger pro Jahr"],
                        ["✈️ Flugreisen", f"{airplane_km_equiv:,.0f} km weniger pro Jahr"],
                        ["📊 CO₂-Fußabdruck", get_text(texts, "pdf_co2_footprint_reduction", "Deutliche Reduktion Ihres persönlichen CO₂-Fußabdrucks")]
                    ]
                    
                    co2_table = Table(co2_data, colWidths=[8*cm, 8*cm])
                    co2_table.setStyle(TableStyle([
                        # Header-Stil
                        ('BACKGROUND', (0, 0), (-1, 0), COLORS['table_header_bg']),
                        ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['table_header_text']),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        
                        # Datenzeilen
                        ('BACKGROUND', (0, 1), (-1, -1), COLORS['table_row_bg']),
                        ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_dark']),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                        
                        # Rahmen und Linien
                        ('GRID', (0, 0), (-1, -1), 1, COLORS['table_border']),
                        ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['accent_primary']),
                        
                        # Zebra-Streifen für bessere Lesbarkeit
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COLORS['table_row_bg'], COLORS['table_alt_row_bg']]),
                        
                        # Padding
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ]))
                    
                    story.append(co2_table)
                    story.append(Spacer(1, 0.3 * cm))
                    
                    # CO₂-Grafik einfügen, falls verfügbar
                    co2_chart_bytes = current_analysis_results_pdf.get('co2_savings_chart_bytes')
                    if co2_chart_bytes:
                        try:
                            co2_img = ImageReader(io.BytesIO(co2_chart_bytes))
                            co2_image = Image(co2_img, width=16*cm, height=10*cm)
                            story.append(co2_image)
                            story.append(Spacer(1, 0.2 * cm))
                        except Exception as e:
                            print(f"Fehler beim Einfügen der CO₂-Grafik: {e}")
                    
                    # Abschließender motivierender Text
                    co2_conclusion = get_text(texts, "pdf_co2_conclusion", "Diese Zahlen verdeutlichen den positiven Umweltbeitrag Ihrer Photovoltaikanlage. Über die gesamte Betriebsdauer von 25+ Jahren summiert sich die CO₂-Einsparung auf mehrere Tonnen – ein wichtiger Schritt für den Klimaschutz und nachfolgende Generationen.")
                    story.append(Paragraph(co2_conclusion, STYLES.get('NormalLeft')))

                elif section_key_current == "Visualizations":
                    story.append(Paragraph(get_text(texts, "pdf_visualizations_intro", "Die folgenden Diagramme visualisieren die Ergebnisse Ihrer Photovoltaikanlage und deren Wirtschaftlichkeit:"), STYLES.get('NormalLeft')))
                    story.append(Spacer(1, 0.3 * cm))
                      # ERWEITERUNG: Vollständige Liste der Diagramme für PDF-Auswahl
                    # Diese Map sollte idealerweise mit `chart_key_to_friendly_name_map` aus `pdf_ui.py` synchronisiert werden.
                    charts_config_for_pdf_generator = {
                        'monthly_prod_cons_chart_bytes': {"title_key": "pdf_chart_title_monthly_comp_pdf", "default_title": "Monatl. Produktion/Verbrauch (2D)"},
                        'cost_projection_chart_bytes': {"title_key": "pdf_chart_label_cost_projection", "default_title": "Stromkosten-Hochrechnung (2D)"},
                        'cumulative_cashflow_chart_bytes': {"title_key": "pdf_chart_label_cum_cashflow", "default_title": "Kumulierter Cashflow (2D)"},
                        'consumption_coverage_pie_chart_bytes': {"title_key": "pdf_chart_title_consumption_coverage_pdf", "default_title": "Deckung Gesamtverbrauch (Jahr 1)"},
                        'pv_usage_pie_chart_bytes': {"title_key": "pdf_chart_title_pv_usage_pdf", "default_title": "Nutzung PV-Strom (Jahr 1)"},
                        'daily_production_switcher_chart_bytes': {"title_key": "pdf_chart_label_daily_3d", "default_title": "Tagesproduktion (3D)"},
                        'weekly_production_switcher_chart_bytes': {"title_key": "pdf_chart_label_weekly_3d", "default_title": "Wochenproduktion (3D)"},
                        'yearly_production_switcher_chart_bytes': {"title_key": "pdf_chart_label_yearly_3d_bar", "default_title": "Jahresproduktion (3D-Balken)"},
                        'project_roi_matrix_switcher_chart_bytes': {"title_key": "pdf_chart_label_roi_matrix_3d", "default_title": "Projektrendite-Matrix (3D)"},
                        'feed_in_revenue_switcher_chart_bytes': {"title_key": "pdf_chart_label_feedin_3d", "default_title": "Einspeisevergütung (3D)"},
                        'prod_vs_cons_switcher_chart_bytes': {"title_key": "pdf_chart_label_prodcons_3d", "default_title": "Verbr. vs. Prod. (3D)"},
                        'tariff_cube_switcher_chart_bytes': {"title_key": "pdf_chart_label_tariffcube_3d", "default_title": "Tarifvergleich (3D)"},
                        'co2_savings_value_switcher_chart_bytes': {"title_key": "pdf_chart_label_co2value_3d", "default_title": "CO2-Ersparnis vs. Wert (3D)"},
                        'co2_savings_chart_bytes': {"title_key": "pdf_chart_label_co2_realistic", "default_title": "CO₂-Einsparung (Realistische Darstellung)"},
                        'investment_value_switcher_chart_bytes': {"title_key": "pdf_chart_label_investval_3D", "default_title": "Investitionsnutzwert (3D)"},
                        'storage_effect_switcher_chart_bytes': {"title_key": "pdf_chart_label_storageeff_3d", "default_title": "Speicherwirkung (3D)"},
                        'selfuse_stack_switcher_chart_bytes': {"title_key": "pdf_chart_label_selfusestack_3d", "default_title": "Eigenverbr. vs. Einspeis. (3D)"},
                        'cost_growth_switcher_chart_bytes': {"title_key": "pdf_chart_label_costgrowth_3d", "default_title": "Stromkostensteigerung (3D)"},
                        'selfuse_ratio_switcher_chart_bytes': {"title_key": "pdf_chart_label_selfuseratio_3d", "default_title": "Eigenverbrauchsgrad (3D)"},
                        'roi_comparison_switcher_chart_bytes': {"title_key": "pdf_chart_label_roicompare_3d", "default_title": "ROI-Vergleich (3D)"},
                        'scenario_comparison_switcher_chart_bytes': {"title_key": "pdf_chart_label_scenariocomp_3d", "default_title": "Szenarienvergleich (3D)"},
                        'tariff_comparison_switcher_chart_bytes': {"title_key": "pdf_chart_label_tariffcomp_3d", "default_title": "Vorher/Nachher Stromkosten (3D)"},
                        'income_projection_switcher_chart_bytes': {"title_key": "pdf_chart_label_incomeproj_3d", "default_title": "Einnahmenprognose (3D)"},
                        'yearly_production_chart_bytes': {"title_key": "pdf_chart_label_pvvis_yearly", "default_title": "PV Visuals: Jahresproduktion"},
                        'break_even_chart_bytes': {"title_key": "pdf_chart_label_pvvis_breakeven", "default_title": "PV Visuals: Break-Even"},
                        'amortisation_chart_bytes': {"title_key": "pdf_chart_label_pvvis_amort", "default_title": "PV Visuals: Amortisation"},
                    }
                    charts_added_count = 0
                    selected_charts_for_pdf_opt = inclusion_options.get("selected_charts_for_pdf", [])
                    
                    for chart_key, config in charts_config_for_pdf_generator.items():
                        if chart_key not in selected_charts_for_pdf_opt:
                            continue # Überspringe dieses Diagramm, wenn nicht vom Nutzer ausgewählt

                        chart_image_bytes = current_analysis_results_pdf.get(chart_key)
                        if chart_image_bytes and isinstance(chart_image_bytes, bytes):
                            chart_display_title = get_text(texts, config["title_key"], config["default_title"])
                            story.append(Paragraph(chart_display_title, STYLES.get('ChartTitle')))
                            img_flowables_chart = _get_image_flowable(chart_image_bytes, available_width_content * 0.9, texts, max_height=12*cm, align='CENTER')
                            if img_flowables_chart: story.extend(img_flowables_chart); story.append(Spacer(1, 0.7*cm)); charts_added_count += 1
                            else: story.append(Paragraph(get_text(texts, "pdf_chart_load_error_placeholder_param", f"(Fehler beim Laden: {chart_display_title})"), STYLES.get('NormalCenter'))); story.append(Spacer(1, 0.5*cm))
                    
                    if charts_added_count == 0 and selected_charts_for_pdf_opt : # Wenn Charts ausgewählt wurden, aber keine gerendert werden konnten
                         story.append(Paragraph(get_text(texts, "pdf_selected_charts_not_renderable", "Ausgewählte Diagramme konnten nicht geladen/angezeigt werden."), STYLES.get('NormalCenter')))
                    elif not selected_charts_for_pdf_opt : # Wenn gar keine Charts ausgewählt wurden
                         story.append(Paragraph(get_text(texts, "pdf_no_charts_selected_for_section", "Keine Diagramme für diese Sektion ausgewählt."), STYLES.get('NormalCenter')))

                elif section_key_current == "FutureAspects":
                    future_aspects_text = ""
                    if pv_details_pdf.get('future_ev'):
                        future_aspects_text += get_text(texts, "pdf_future_ev_text_param", "<b>E-Mobilität:</b> Die Anlage ist auf eine zukünftige Erweiterung um ein Elektrofahrzeug vorbereitet. Der prognostizierte PV-Anteil an der Fahrzeugladung beträgt ca. {eauto_pv_coverage_kwh:.0f} kWh/Jahr.").format(eauto_pv_coverage_kwh=current_analysis_results_pdf.get('eauto_ladung_durch_pv_kwh',0.0)) + "<br/>"
                    if pv_details_pdf.get('future_hp'):
                        future_aspects_text += get_text(texts, "pdf_future_hp_text_param", "<b>Wärmepumpe:</b> Die Anlage kann zur Unterstützung einer zukünftigen Wärmepumpe beitragen. Der geschätzte PV-Deckungsgrad für die Wärmepumpe liegt bei ca. {hp_pv_coverage_pct:.0f}%. ").format(hp_pv_coverage_pct=current_analysis_results_pdf.get('pv_deckungsgrad_wp_pct',0.0)) + "<br/>"
                    if not future_aspects_text: future_aspects_text = get_text(texts, "pdf_no_future_aspects_selected", "Keine spezifischen Zukunftsaspekte für dieses Angebot ausgewählt.")
                    story.append(Paragraph(future_aspects_text, STYLES.get('NormalLeft')))
                
                # NEUE OPTIONALE SEITENVORLAGEN (individuell gestaltbar, wie gewünscht)
                elif section_key_current == "CompanyProfile":
                    company_profile_text = get_text(texts, "pdf_company_profile_content", 
                        f"<b>{company_info.get('name', 'Unser Unternehmen')}</b><br/><br/>"
                        f"Mit langjähriger Erfahrung im Bereich Photovoltaik sind wir Ihr zuverlässiger Partner für nachhaltige Energielösungen. "
                        f"Unser engagiertes Team begleitet Sie von der ersten Beratung bis zur finalen Inbetriebnahme Ihrer Anlage.<br/><br/>"
                        f"<b>Kontakt:</b><br/>"
                        f"📍 {company_info.get('street', '')}, {company_info.get('zip_code', '')} {company_info.get('city', '')}<br/>"
                        f"📞 {company_info.get('phone', '')}<br/>"
                        f"📧 {company_info.get('email', '')}")
                    story.append(Paragraph(company_profile_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "Certifications":
                    cert_text = get_text(texts, "pdf_certifications_content",
                        "<b>Unsere Zertifizierungen & Qualitätsstandards:</b><br/><br/>"
                        "✓ <b>VDE-Zertifizierung</b> - Elektrotechnische Sicherheit<br/>"
                        "✓ <b>Meisterbetrieb</b> - Handwerkliche Qualität<br/>"
                        "✓ <b>IHK-Sachverständiger</b> - Technische Expertise<br/>"
                        "✓ <b>ISO 9001</b> - Qualitätsmanagementsystem<br/>"
                        "✓ <b>Fachbetrieb für Photovoltaik</b> - Spezialisierung<br/><br/>"
                        "Alle Komponenten entsprechen den aktuellen DIN- und VDE-Normen.")
                    story.append(Paragraph(cert_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "References":
                    ref_text = get_text(texts, "pdf_references_content",
                        "<b>Referenzen & Kundenerfahrungen:</b><br/><br/>"
                        "⭐⭐⭐⭐⭐ <i>\"Professionelle Beratung und saubere Montage. Unsere Anlage läuft seit 2 Jahren perfekt!\"</i><br/>"
                        "- Familie Müller, 8,5 kWp Anlage<br/><br/>"
                        "⭐⭐⭐⭐⭐ <i>\"Von der Planung bis zur Inbetriebnahme - alles aus einer Hand und termingerecht.\"</i><br/>"
                        "- Herr Schmidt, 12 kWp mit Speicher<br/><br/>"
                        "⭐⭐⭐⭐⭐ <i>\"Kompetente Beratung, faire Preise, einwandfreie Ausführung. Sehr empfehlenswert!\"</i><br/>"
                        "- Frau Weber, 6,2 kWp Anlage<br/><br/>"
                        "<b>Über 500 zufriedene Kunden</b> vertrauen auf unsere Expertise.")
                    story.append(Paragraph(ref_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "Installation":
                    install_text = get_text(texts, "pdf_installation_content",
                        "<b>Professionelle Installation - Ihr Weg zur eigenen Solaranlage:</b><br/><br/>"
                        "<b>1. Terminplanung & Vorbereitung</b><br/>"
                        "• Detaillierte Terminabsprache<br/>"
                        "• Anmeldung beim Netzbetreiber<br/>"
                        "• Bereitstellung aller Komponenten<br/><br/>"
                        "<b>2. Montage (1-2 Tage)</b><br/>"
                        "• Dachmontage durch zertifizierte Dachdecker<br/>"
                        "• Elektrische Installation durch Elektromeister<br/>"
                        "• Sicherheitsprüfung nach VDE-Norm<br/><br/>"
                        "<b>3. Inbetriebnahme & Übergabe</b><br/>"
                        "• Funktionstest und Messung<br/>"
                        "• Einweisung in die Bedienung<br/>"
                        "• Übergabe aller Unterlagen")
                    story.append(Paragraph(install_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "Maintenance":
                    maint_text = get_text(texts, "pdf_maintenance_content",
                        "<b>Wartung & Langzeitservice für maximale Erträge:</b><br/><br/>"
                        "<b>Wartungsleistungen:</b><br/>"
                        "• Jährliche Sichtprüfung der Module<br/>"
                        "• Überprüfung der elektrischen Verbindungen<br/>"
                        "• Funktionstest des Wechselrichters<br/>"
                        "• Reinigung bei Bedarf<br/>"
                        "• Ertragskontrolle und Optimierung<br/><br/>"
                        "<b>24/7 Monitoring:</b><br/>"
                        "• Online-Überwachung der Anlagenleistung<br/>"
                        "• Automatische Störungsmeldung<br/>"
                        "• Ferndiagnose und schnelle Hilfe<br/><br/>"
                        "<b>Wartungsvertrag verfügbar</b> - Sprechen Sie uns an!")
                    story.append(Paragraph(maint_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "Financing":
                    fin_text = get_text(texts, "pdf_financing_content",
                        "<b>Flexible Finanzierungsmöglichkeiten:</b><br/><br/>"
                        "💰 <b>KfW-Förderung</b><br/>"
                        "• Zinsgünstige Darlehen bis 150.000€<br/>"
                        "• Tilgungszuschüsse möglich<br/>"
                        "• Wir unterstützen bei der Antragstellung<br/><br/>"
                        "🏦 <b>Bankfinanzierung</b><br/>"
                        "• Partnerschaften mit regionalen Banken<br/>"
                        "• Attraktive Konditionen für Solaranlagen<br/>"
                        "• Laufzeiten bis 20 Jahre<br/><br/>"
                        "📊 <b>Leasing & Pacht</b><br/>"
                        "• Keine Anfangsinvestition<br/>"
                        "• Monatliche Raten ab 89€<br/>"
                        "• Rundum-Sorglos-Paket inklusive<br/><br/>"
                        "Gerne erstellen wir Ihnen ein individuelles Finanzierungskonzept!")
                    story.append(Paragraph(fin_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "Insurance":
                    ins_text = get_text(texts, "pdf_insurance_content",
                        "<b>Umfassender Versicherungsschutz für Ihre Investition:</b><br/><br/>"
                        "🛡️ <b>Photovoltaik-Versicherung</b><br/>"
                        "• Schutz vor Sturm, Hagel, Blitzschlag<br/>"
                        "• Diebstahl- und Vandalismus-Schutz<br/>"
                        "• Elektronikversicherung für Wechselrichter<br/><br/>"
                        "⚡ <b>Ertragsausfallversicherung</b><br/>"
                        "• Absicherung bei Produktionsausfall<br/>"
                        "• Ersatz entgangener EEG-Vergütung<br/>"
                        "• Mehrkosten bei Reparaturen<br/><br/>"
                        "🏠 <b>Integration in bestehende Versicherungen</b><br/>"
                        "• Prüfung der Wohngebäudeversicherung<br/>"
                        "• Anpassung bestehender Policen<br/>"
                        "• Kostengünstige Ergänzungen<br/><br/>"
                        "Wir beraten Sie gerne zu optimalen Versicherungslösungen!")
                    story.append(Paragraph(ins_text, STYLES.get('NormalLeft')))
                
                elif section_key_current == "Warranty":
                    warr_text = get_text(texts, "pdf_warranty_content",
                        "<b>Garantie & Gewährleistung - Ihre Sicherheit:</b><br/><br/>"
                        "🔧 <b>Herstellergarantien:</b><br/>"
                        "• <b>Module:</b> 25 Jahre Leistungsgarantie<br/>"
                        "• <b>Wechselrichter:</b> 10-20 Jahre Herstellergarantie<br/>"
                        "• <b>Speichersystem:</b> 10 Jahre Garantie<br/>"
                        "• <b>Montagesystem:</b> 15 Jahre Material-/Korrosionsschutz<br/><br/>"
                        "⚙️ <b>Handwerkergewährleistung:</b><br/>"
                        "• 2 Jahre auf Montage und Installation<br/>"
                        "• 5 Jahre erweiterte Gewährleistung möglich<br/>"
                        "• Schnelle Reaktionszeiten bei Problemen<br/><br/>"
                        "📞 <b>Service-Hotline:</b><br/>"
                        "• Kostenlose Beratung bei Fragen<br/>"
                        "• Ferndiagnose und Support<br/>"
                        "• Vor-Ort-Service innerhalb 48h<br/><br/>"
                        "<b>Ihr Vertrauen ist unsere Verpflichtung!</b>")
                    story.append(Paragraph(warr_text, STYLES.get('NormalLeft')))
                    story.append(Spacer(1, 0.5*cm)); current_section_counter_pdf +=1
            except Exception as e_section:
                story.append(Paragraph(f"Fehler in Sektion '{default_title_current}': {e_section}", STYLES.get('NormalLeft')))
                story.append(Spacer(1, 0.5*cm)); current_section_counter_pdf +=1
    
    main_pdf_bytes: Optional[bytes] = None
    try:
        layout_callback_kwargs_build = {
            'texts_ref': texts, 'company_info_ref': company_info,
            'company_logo_base64_ref': company_logo_base64 if include_company_logo_opt else None,
            'offer_number_ref': offer_number_final, 'page_width_ref': doc.pagesize[0], 
            'page_height_ref': doc.pagesize[1],'margin_left_ref': doc.leftMargin, 
            'margin_right_ref': doc.rightMargin,'margin_top_ref': doc.topMargin, 
            'margin_bottom_ref': doc.bottomMargin,'doc_width_ref': doc.width, 'doc_height_ref': doc.height,
            # NEUE OPTIONEN (wie gewünscht)
            'include_custom_footer_ref': include_custom_footer_opt,
            'include_header_logo_ref': include_header_logo_opt
        }
        doc.build(story, canvasmaker=lambda *args, **kwargs_c: PageNumCanvas(*args, onPage_callback=page_layout_handler, callback_kwargs=layout_callback_kwargs_build, **kwargs_c))
        main_pdf_bytes = main_offer_buffer.getvalue()
    except Exception as e_build_pdf:
        return _create_plaintext_pdf_fallback(project_data, analysis_results, texts, company_info, selected_offer_title_text, selected_cover_letter_text)
    finally:
        main_offer_buffer.close()
    
    if not main_pdf_bytes: 
        return None
    
    # PDF-Anhänge nur wenn beide Bedingungen erfüllt sind
    if not (include_all_documents_opt and _PYPDF_AVAILABLE):
        return main_pdf_bytes

    paths_to_append: List[str] = []
    debug_info = {
        'product_datasheets_found': [],
        'product_datasheets_missing': [],
        'company_docs_found': [],
        'company_docs_missing': [],
        'total_paths_to_append': 0
    }
    
    # Produktdatenblätter (Hauptkomponenten UND Zubehör)
    product_ids_for_datasheets = list(filter(None, [
        pv_details_pdf.get("selected_module_id"),
        pv_details_pdf.get("selected_inverter_id"),
        pv_details_pdf.get("selected_storage_id") if pv_details_pdf.get("include_storage") else None
    ]))
    if pv_details_pdf.get('include_additional_components', True): # Nur wenn Zubehör überhaupt aktiv ist
        for opt_id_key in ['selected_wallbox_id', 'selected_ems_id', 'selected_optimizer_id', 'selected_carport_id', 'selected_notstrom_id', 'selected_tierabwehr_id']:
            comp_id_val = pv_details_pdf.get(opt_id_key)
            if comp_id_val: product_ids_for_datasheets.append(comp_id_val)
    
    # Duplikate entfernen, falls ein Produkt mehrfach auftaucht (unwahrscheinlich, aber sicher)
    product_ids_for_datasheets = list(set(product_ids_for_datasheets))

    for prod_id in product_ids_for_datasheets:
        try:
            product_info = get_product_by_id_func(prod_id) 
            if product_info:
                datasheet_path_from_db = product_info.get("datasheet_link_db_path")
                if datasheet_path_from_db:
                    full_datasheet_path = os.path.join(PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, datasheet_path_from_db)
                    if os.path.exists(full_datasheet_path):
                        paths_to_append.append(full_datasheet_path)
                        debug_info['product_datasheets_found'].append({'id': prod_id, 'model': product_info.get('model_name'), 'path': full_datasheet_path})
                    else:
                        debug_info['product_datasheets_missing'].append({'id': prod_id, 'model': product_info.get('model_name'), 'path': full_datasheet_path})
                else:
                    debug_info['product_datasheets_missing'].append({'id': prod_id, 'model': product_info.get('model_name'), 'reason': 'Kein Datenblatt-Pfad in DB'})
            else:
                debug_info['product_datasheets_missing'].append({'id': prod_id, 'reason': 'Produkt nicht in DB gefunden'})
        except Exception as e_prod:
            # Fehler beim Laden von Produktinformationen - wird still behandelt
            pass
            
    # Firmendokumente
    if company_document_ids_to_include_opt and active_company_id is not None and callable(db_list_company_documents_func):
        try:
            all_company_docs_for_active_co = db_list_company_documents_func(active_company_id, None) # doc_type=None für alle
            for doc_info in all_company_docs_for_active_co:
                if doc_info.get('id') in company_document_ids_to_include_opt:
                    relative_doc_path = doc_info.get("relative_db_path") 
                    if relative_doc_path: 
                        full_doc_path = os.path.join(COMPANY_DOCS_BASE_DIR_PDF_GEN, relative_doc_path)
                        if os.path.exists(full_doc_path):
                            paths_to_append.append(full_doc_path)
                            debug_info['company_docs_found'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'path': full_doc_path})
                        else:
                            debug_info['company_docs_missing'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'path': full_doc_path})
                    else:
                        debug_info['company_docs_missing'].append({'id': doc_info.get('id'), 'name': doc_info.get('display_name'), 'reason': 'Kein relativer Pfad in DB'})
        except Exception as e_company_docs:
            # Fehler beim Laden der Firmendokumente - wird still behandelt
            pass
    
    debug_info['total_paths_to_append'] = len(paths_to_append)
    
    if not paths_to_append: 
        return main_pdf_bytes
    
    pdf_writer = PdfWriter()
    try:
        main_offer_reader = PdfReader(io.BytesIO(main_pdf_bytes))
        for page in main_offer_reader.pages: 
            pdf_writer.add_page(page)
    except Exception as e_read_main:
        return main_pdf_bytes 

    successfully_appended = 0
    for pdf_path in paths_to_append:
        try:
            datasheet_reader = PdfReader(pdf_path)
            for page in datasheet_reader.pages: 
                pdf_writer.add_page(page)
            successfully_appended += 1
        except Exception as e_append_ds:
            pass  # Fehler beim Anhängen werden still behandelt
    
    final_buffer = io.BytesIO()
    try:
        pdf_writer.write(final_buffer)
        final_pdf_bytes = final_buffer.getvalue()
        return final_pdf_bytes
    except Exception as e_write_final:
        return main_pdf_bytes 
    finally:
        final_buffer.close()

def merge_pdfs(pdf_files: List[Union[str, bytes, io.BytesIO]]) -> bytes:
    """
    Standalone-Funktion zum Zusammenführen mehrerer PDF-Dateien.
    
    Args:
        pdf_files: Liste von PDF-Dateien (Pfade, Bytes oder BytesIO-Objekte)
        
    Returns:
        bytes: Die zusammengeführte PDF als Bytes
    """
    if not _PYPDF_AVAILABLE:
        raise RuntimeError("PyPDF ist nicht verfügbar für das Zusammenführen von PDFs")
        
    if not pdf_files:
        return b""
        
    merger = PdfWriter()
    
    try:
        for pdf_file in pdf_files:
            if isinstance(pdf_file, str):
                # Pfad zu PDF-Datei
                if os.path.exists(pdf_file):
                    with open(pdf_file, 'rb') as f:
                        reader = PdfReader(f)
                        for page in reader.pages:
                            merger.add_page(page)
            elif isinstance(pdf_file, bytes):
                # PDF als Bytes
                reader = PdfReader(io.BytesIO(pdf_file))
                for page in reader.pages:
                    merger.add_page(page)
            elif isinstance(pdf_file, io.BytesIO):
                # PDF als BytesIO
                pdf_file.seek(0)  # Sicherstellung, dass wir am Anfang sind
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    merger.add_page(page)
                    
        # Zusammengeführte PDF in BytesIO schreiben
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        # Fallback: Erste PDF zurückgeben wenn verfügbar
        if pdf_files:
            first_pdf = pdf_files[0]
            if isinstance(first_pdf, str) and os.path.exists(first_pdf):
                with open(first_pdf, 'rb') as f:
                    return f.read()
            elif isinstance(first_pdf, bytes):
                return first_pdf
            elif isinstance(first_pdf, io.BytesIO):
                first_pdf.seek(0)
                return first_pdf.getvalue()
        return b""

def _validate_pdf_data_availability(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]) -> Dict[str, Any]:
    """
    Validiert die Verfügbarkeit von Daten für die PDF-Erstellung und gibt Warnmeldungen zurück.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        texts: Text-Dictionary
        
    Returns:
        Dict mit Validierungsergebnissen und Warnmeldungen
    """
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'critical_errors': [],
        'missing_data_summary': []
    }
    
    # Kundendaten prüfen (nicht kritisch)
    customer_data = project_data.get('customer_data', {})
    if not customer_data or not customer_data.get('last_name'):
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_customer_name', 'Kein Kundenname verfügbar - wird als "Kunde" angezeigt')
        )
        validation_result['missing_data_summary'].append('Kundenname')
    
    # PV-Details prüfen
    pv_details = project_data.get('pv_details', {})
    project_details = project_data.get('project_details', {})
    
    # Entweder module in pv_details ODER module_quantity in project_details ist ausreichend
    modules_present = True
    if pv_details and pv_details.get('selected_modules'):
        modules_present = True
    elif project_details and project_details.get('module_quantity', 0) > 0:
        modules_present = True
    
    if not modules_present:
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_modules', 'Keine PV-Module ausgewählt - Standardwerte werden verwendet')
        )
        validation_result['missing_data_summary'].append('PV-Module')
        # Nur als Warnung, nicht als kritischer Fehler
    
    # Analyseergebnisse prüfen - mit mehr Toleranz
    if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
        # Wirklich leere oder sehr minimale Analyse ist ein kritischer Fehler
        validation_result['critical_errors'].append(
            get_text(texts, 'pdf_error_no_analysis', 'Keine Analyseergebnisse verfügbar - PDF kann nicht erstellt werden')
        )
        validation_result['is_valid'] = True
        validation_result['missing_data_summary'].append('Analyseergebnisse')
    else:
        # Wenn die Analyse mindestens einige Werte enthält, betrachten wir es als gültig
        # und geben nur Warnungen aus, wenn wichtige KPIs fehlen
        important_kpis = ['anlage_kwp', 'annual_pv_production_kwh', 'total_investment_cost_netto']
        missing_kpis = []
        for kpi in important_kpis:
            if not analysis_results.get(kpi):
                missing_kpis.append(kpi)
                
        if missing_kpis:
            missing_kpi_names = ', '.join(missing_kpis)
            validation_result['warnings'].append(
                get_text(texts, 'pdf_warning_missing_kpis', f'Fehlende wichtige Kennzahlen: {missing_kpi_names}')
            )
            validation_result['missing_data_summary'].extend(missing_kpis)
            # Fehlende KPIs sind kein kritischer Fehler mehr
    
    # Firmendaten prüfen (nicht kritisch)
    if not project_data.get('company_information', {}).get('name'):
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_company', 'Keine Firmendaten verfügbar - Fallback wird verwendet')
        )
        validation_result['missing_data_summary'].append('Firmendaten')
    
    # Debug-Ausgabe
    print(f"PDF Validierung: is_valid={validation_result['is_valid']}, "
          f"Warnungen={len(validation_result['warnings'])}, "
          f"Kritische Fehler={len(validation_result['critical_errors'])}")
    
    return validation_result
def _create_no_data_fallback_pdf(texts: Dict[str, str], customer_data: Dict[str, Any] = None) -> bytes:
    """
    Erstellt eine Fallback-PDF mit Informationstext, wenn keine ausreichenden Daten verfügbar sind.
    
    Args:
        texts: Text-Dictionary
        customer_data: Optionale Kundendaten
        
    Returns:
        PDF als Bytes
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    title = get_text(texts, 'pdf_no_data_title', 'Photovoltaik-Angebot - Datensammlung erforderlich')
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 1*cm))
    
    # Kunde falls verfügbar
    if customer_data and customer_data.get('last_name'):
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        customer_text = get_text(texts, 'pdf_no_data_customer', f'Für: {customer_name}')
        story.append(Paragraph(customer_text, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # Haupttext
    main_text = get_text(texts, 'pdf_no_data_main_text', 
        '''Liebe Kundin, lieber Kunde,
        
        für die Erstellung Ihres individuellen Photovoltaik-Angebots benötigen wir noch einige wichtige Informationen:
        
        <b>Erforderliche Daten:</b>
        • Ihre Kontaktdaten (vollständig)
        • Gewünschte PV-Module und Komponenten
        • Stromverbrauchsdaten Ihres Haushalts
        • Technische Angaben zu Ihrem Dach/Standort
        
        <b>Nächste Schritte:</b>
        1. Vervollständigen Sie die Dateneingabe in der Anwendung
        2. Führen Sie die Wirtschaftlichkeitsberechnung durch
        3. Generieren Sie anschließend Ihr personalisiertes PDF-Angebot
        
        Bei Fragen stehen wir Ihnen gerne zur Verfügung!''')
    
    story.append(Paragraph(main_text, styles['Normal']))
    story.append(Spacer(1, 1*cm))
    
    # Kontaktinformationen
    contact_text = get_text(texts, 'pdf_no_data_contact', 
        'Kontakt: Bitte wenden Sie sich an unser Beratungsteam für weitere Unterstützung.')
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
    
    # HINZUGEFÜGT VON SEGGELI ULTRA ZU pdf_generator.py
# Zeile: ~2001 (am Ende der Datei einfügen)

# BENÖTIGTE IMPORTE (stellen Sie sicher, dass diese am Anfang der Datei vorhanden sind)
import plotly.graph_objects as go
import pandas as pd
import math
from typing import Dict, Any

# HILFSFUNKTION (falls _export_plotly_fig_to_bytes nicht existiert, bitte diese einfügen)
def _export_plotly_fig_to_bytes(fig, texts, format='png'):
    """Exportiert eine Plotly-Figur in Bytes."""
    try:
        return fig.to_image(format=format)
    except Exception as e:
        print(f"Fehler beim Exportieren der Plotly-Figur: {e}")
        return None

def generate_prod_vs_cons_chart_image(analysis_results: Dict[str, Any], texts: Dict[str, str]):
    """
    Erstellt das "Verbrauch vs. Produktion"-Diagramm und gibt es als Bild-Bytes zurück.
    Diese Funktion ist eine Modifikation von 'render_production_vs_consumption_switcher'
    und enthält keine Streamlit-UI-Elemente. Sie ist für den PDF-Export optimiert.
    """
    month_labels = texts.get("month_names_short_list", "Jan,Feb,Mrz,Apr,Mai,Jun,Jul,Aug,Sep,Okt,Nov,Dez").split(',')
    verbrauch_raw = analysis_results.get('monthly_consumption_sim', [100 + 10 * i for i in range(12)]) # Fallback-Daten
    produktion_raw = analysis_results.get('monthly_productions_sim', [80 + 20 * i for i in range(12)]) # Fallback-Daten

    verbrauch = [float(v) if isinstance(v, (int, float)) and not math.isnan(v) else 0.0 for v in verbrauch_raw]
    produktion = [float(p) if isinstance(p, (int, float)) and not math.isnan(p) else 0.0 for p in produktion_raw]

    # Feste Konfigurationen für das PDF (keine UI-Auswahl)
    chart_type = "Säulen" # Festgelegt für das PDF
    colors = ["#1f77b4", "#ff7f0e"] # Standardfarben

    # Diagramm erstellen
    fig = go.Figure()
    if chart_type == "Säulen":
        fig.add_trace(go.Bar(x=month_labels, y=verbrauch, name='Verbrauch (kWh)', marker_color=colors[0]))
        fig.add_trace(go.Bar(x=month_labels, y=produktion, name='Produktion (kWh)', marker_color=colors[1]))
    # Hier könnten weitere Diagrammtypen als 'elif' implementiert werden

    fig.update_layout(
        title="Monatlicher Verbrauch vs. Produktion (Jahr 1)",
        xaxis_title="Monat",
        yaxis_title="kWh",
        plot_bgcolor='rgba(255, 255, 255, 1)', # Weißer Hintergrund für PDF
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        barmode='group'
    )
    
    # Diagramm als Bild-Daten (Bytes) exportieren und zurückgeben
    image_bytes = _export_plotly_fig_to_bytes(fig, texts)
    return image_bytes
    
# Änderungshistorie
# 2025-06-03, Gemini Ultra: PageNumCanvas.save() korrigiert, um Duplizierung des PDF-Inhalts zu verhindern.
#                           Schlüssel für `include_all_documents_opt` in `generate_offer_pdf` korrigiert.
#                           Aufruf von `db_list_company_documents_func` mit `doc_type=None` versehen.
#                           Anpassung von _update_styles_with_dynamic_colors für DATA_TABLE_STYLE.
#                           Sicherstellung, dass ausgewählte Diagramme für PDF-Visualisierungen berücksichtigt werden.
#                           Korrekter Key 'relative_db_path' für Firmendokumente verwendet.
# 2025-06-03, Gemini Ultra: `charts_config_for_pdf_generator` erweitert, um alle Diagramme aus `pdf_ui.py` abzudecken.
#                           Logik zur Einbindung optionaler Komponenten (Zubehör) in Sektion "Technische Komponenten" hinzugefügt, gesteuert durch `include_optional_component_details_opt`.
#                           Logik zum Anhängen von Produktdatenblättern erweitert, um auch Zubehör-Datenblätter zu berücksichtigen.
#                           Definition von ReportLab-Styles nur ausgeführt, wenn _REPORTLAB_AVAILABLE True ist.
# 2025-06-03, Gemini Ultra: Validierungs- und Fallback-Funktionen für PDF-Erstellung ohne ausreichende Daten hinzugefügt.
