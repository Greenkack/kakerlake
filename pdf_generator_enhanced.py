"""
Datei: pdf_generator_enhanced.py
Zweck: Erweiterte PDF-Generierung mit modernen Design-Features
       Ergänzt die bestehende pdf_generator.py ohne Überschreibung
Autor: GitHub Copilot
Datum: 2025-07-18

Diese Datei erweitert die bestehende PDF-Funktionalität mit modernen Design-Features,
ähnlich den professionellen PDFs, die Sie als Beispiel gezeigt haben.
"""

import os
import io
import base64
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from pdf_styles import ProfessionalPDFBackgrounds, get_professional_theme

# Import der bestehenden PDF-Generator Funktionen
try:
    from pdf_generator import (
        _REPORTLAB_AVAILABLE, PRIMARY_COLOR_HEX, SECONDARY_COLOR_HEX, 
        TEXT_COLOR_HEX, SEPARATOR_LINE_COLOR_HEX, STYLES, 
        get_text, _get_image_flowable,
        page_layout_handler
    )
    from pdf_design_enhanced import (
        ModernColorSchemes, EnhancedPDFStyles, ModernPDFComponents,
        create_enhanced_style_preset
    )
    _ENHANCED_AVAILABLE = True
except ImportError as e:
    print(f"Erweiterte PDF-Features nicht verfügbar: {e}")
    _ENHANCED_AVAILABLE = False
    
    # Fallback-Funktionen
    def create_enhanced_style_preset(scheme_name='PROFESSIONAL_BLUE'):
        return {
            'color_scheme': {},
            'paragraph_styles': {},
            'table_styles': {},
            'components': None
        }

if _REPORTLAB_AVAILABLE:
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        Image, PageBreak, Flowable, KeepTogether, Frame
    )

class EnhancedPDFGenerator:
    """
    Erweiterte PDF-Generator-Klasse mit modernen Design-Features
    Behält alle bestehenden Funktionen bei und fügt neue hinzu
    """
    
    def __init__(self, color_scheme: Union[str, Dict[str, str]] = 'PROFESSIONAL_BLUE',
                 enhanced_styles: Optional[Dict[str, Any]] = None,
                 table_styles: Optional[Dict[str, Any]] = None,
                 components: Optional[Any] = None):
        if not _REPORTLAB_AVAILABLE or not _ENHANCED_AVAILABLE:
            raise ImportError("ReportLab oder erweiterte Features nicht verfügbar")
            
        # Lade das gewünschte Farbschema
        if isinstance(color_scheme, str):
            self.style_preset = create_enhanced_style_preset(color_scheme)
            self.colors = self.style_preset['color_scheme']
            self.enhanced_styles = enhanced_styles or self.style_preset['paragraph_styles']
            self.table_styles = table_styles or self.style_preset['table_styles']
            self.components = components or self.style_preset['components']
        else:
            # Direkte Übergabe der Stile
            self.colors = color_scheme
            self.enhanced_styles = enhanced_styles or {}
            self.table_styles = table_styles or {}
            self.components = components

        # Page-Hook-Callback erzeugen
    def build_pdf(self, story, filename="angebot.pdf", use_professional_theme=True, accent_color="#FFD600"):
        """
        Baut das PDF-Dokument mit optional professionellem Theme und Seitenhintergrund.
        use_professional_theme: Wenn True, wird das zentrale Theme (Design/Hintergrund) verwendet.
        accent_color: Akzentfarbe für die Leiste (UI-wählbar).
        """
        from reportlab.platypus import SimpleDocTemplate
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm

        doc = SimpleDocTemplate(filename, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        if use_professional_theme:
            theme = get_professional_theme(selected_accent=accent_color)
            def page_background(canvas, doc):
                
        ProfessionalPDFBackgrounds(theme).draw_background(canvas, doc)
        doc.build(story, onFirstPage=page_background, onLaterPages=page_background)
    else:
        if hasattr(self, '_header_footer'):
            doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        else:
            doc.build(story)
            
        def create_enhanced_cover_page(self, 
            project_data: Dict[str, Any],
            company_info: Dict[str, Any],
            texts: Dict[str, str],
            company_logo_base64: Optional[str] = None,
            title_image_b64: Optional[str] = None,
            offer_title: str = None,
            offer_number: str = None) -> List[Any]:
        """
        Erstellt ein modernes, professionelles Deckblatt
        ähnlich den bereitgestellten PDF-Beispielen
        """
        story = []
        
        # === LOGO BEREICH ===
        if company_logo_base64:
            logo_flowables = _get_image_flowable(
                company_logo_base64, 
                desired_width=8*cm, 
                texts=texts, 
                max_height=3*cm, 
                align='CENTER'
            )
            if logo_flowables:
                story.extend(logo_flowables)
                story.append(Spacer(1, 1.5*cm))
        
        # === TITEL-BEREICH ===
        # Haupttitel
        title_text = offer_title or get_text(texts, 'pdf_default_title', 
                                           'Ihr individuelles Photovoltaik-Angebot')
        story.append(Paragraph(title_text, self.enhanced_styles['DocumentTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Untertitel mit Angebotsnummer
        if offer_number:
            subtitle = get_text(texts, 'pdf_offer_number_label', 'Angebotsnummer: {number}').format(number=offer_number)
            subtitle_style = ParagraphStyle(
                'CoverSubtitle',
                parent=self.enhanced_styles['BodyText'],
                fontSize=14,
                leading=18,
                textColor=HexColor(self.colors['text_secondary']),
                alignment=TA_CENTER,
                spaceBefore=0,
                spaceAfter=20
            )
            story.append(Paragraph(subtitle, subtitle_style))
        
        # === TITEL-BILD ===
        if title_image_b64:
            title_img_flowables = _get_image_flowable(
                title_image_b64, 
                desired_width=15*cm, 
                texts=texts, 
                max_height=8*cm, 
                align='CENTER'
            )
            if title_img_flowables:
                story.append(Spacer(1, 1*cm))
                story.extend(title_img_flowables)
                story.append(Spacer(1, 1*cm))
        
        # === KUNDEN-INFORMATION ===
        customer_data = project_data.get('customer_data', {})
        if customer_data:
            # Erstelle eine elegante Kunden-Info-Box
            customer_info = self._create_customer_info_section(customer_data, texts)
            story.extend(customer_info)
        
        # === FIRMEN-INFORMATION ===
        company_info_section = self._create_company_info_section(company_info, texts)
        story.extend(company_info_section)
        
        # === DATUM ===
        date_text = datetime.now().strftime('%d. %B %Y')
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.enhanced_styles['BodyText'],
            fontSize=11,
            textColor=HexColor(self.colors['text_secondary']),
            alignment=TA_CENTER,
            spaceBefore=20
        )
        story.append(Paragraph(f"Datum: {date_text}", date_style))
        
        return story

    def _create_cover_letter_section(self, cover_letter_text: str, texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine moderne Anschreiben-Sektion"""
        story = []
        
        # Überschrift
        story.append(Paragraph(
            get_text(texts, 'pdf_cover_letter_title', 'Anschreiben'), 
            self.enhanced_styles['SectionHeader']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # Anschreiben-Text
        story.append(Paragraph(cover_letter_text, self.enhanced_styles['BodyText']))
        
        return story

    def _create_customer_info_section(self, customer_data: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine moderne Kunden-Info-Sektion"""
        story = []
        
        # Kunden-Info-Box
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        address_parts = []
        if customer_data.get('street'): address_parts.append(customer_data['street'])
        if customer_data.get('zip_code') and customer_data.get('city'):
            address_parts.append(f"{customer_data['zip_code']} {customer_data['city']}")
        
        address_text = "<br/>".join(address_parts)
        
        if customer_name or address_text:
            customer_info = f"<b>{customer_name}</b><br/>{address_text}"
            
            # Erstelle Info-Box mit moderner Formatierung
            info_box = self.components.create_info_box(
                customer_info, 
                'info', 
                get_text(texts, 'pdf_customer_info_title', 'Angebot für')
            )
            story.extend(info_box)
        
        return story

    def _create_company_info_section(self, company_info: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine moderne Firmen-Info-Sektion"""
        story = []
        
        if company_info and company_info.get('name'):
            company_text = f"<b>{company_info['name']}</b>"
            
            # Weitere Firmen-Details falls vorhanden
            if company_info.get('address'):
                company_text += f"<br/>{company_info['address']}"
            if company_info.get('phone'):
                company_text += f"<br/>Tel: {company_info['phone']}"
            if company_info.get('email'):
                company_text += f"<br/>E-Mail: {company_info['email']}"
            
            # Erstelle Firmen-Info-Box
            company_box = self.components.create_info_box(
                company_text, 
                'info', 
                get_text(texts, 'pdf_company_info_title', 'Ihr Ansprechpartner')
            )
            story.extend(company_box)
        
        return story
    
    def _create_customer_info_section(self, customer_data: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine elegante Kunden-Informationssektion"""
        flowables = []
        
        # Sammle Kundeninformationen
        customer_lines = []
        
        # Name (Anrede + Titel + Vor- + Nachname)
        name_parts = []
        if customer_data.get('salutation'):
            name_parts.append(customer_data['salutation'])
        if customer_data.get('title'):
            name_parts.append(customer_data['title'])
        if customer_data.get('first_name'):
            name_parts.append(customer_data['first_name'])
        if customer_data.get('last_name'):
            name_parts.append(customer_data['last_name'])
        
        if name_parts:
            customer_lines.append(' '.join(name_parts))
        
        # Adresse
        address_parts = []
        if customer_data.get('address'):
            address_line = customer_data['address']
            if customer_data.get('house_number'):
                address_line += ' ' + str(customer_data['house_number'])
            address_parts.append(address_line)
        
        if customer_data.get('zip_code') or customer_data.get('city'):
            zip_city = f"{customer_data.get('zip_code', '')} {customer_data.get('city', '')}".strip()
            if zip_city:
                address_parts.append(zip_city)
        
        customer_lines.extend(address_parts)
        
        # Kontaktdaten
        contact_parts = []
        if customer_data.get('phone'):
            contact_parts.append(f"Tel.: {customer_data['phone']}")
        if customer_data.get('email'):
            contact_parts.append(f"E-Mail: {customer_data['email']}")
        
        customer_lines.extend(contact_parts)
        
        if customer_lines:
            # Erstelle Info-Box für Kundendaten
            customer_text = '<br/>'.join(customer_lines)
            
            # Tabelle für elegante Darstellung
            table_data = [[customer_text]]
            customer_table = Table(table_data, colWidths=[12*cm])
            
            customer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor(self.colors['background_light'])),
                ('BOX', (0, 0), (-1, -1), 1, HexColor(self.colors['border_medium'])),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor(self.colors['text_primary']))
            ]))
            
            # Header für die Kunden-Sektion
            header_text = get_text(texts, 'pdf_customer_info_header', 'Kunde')
            header_style = ParagraphStyle(
                'CustomerHeader',
                parent=self.enhanced_styles['SubSectionHeader'],
                alignment=TA_LEFT,
                spaceBefore=30,
                spaceAfter=10
            )
            
            flowables.extend([
                Paragraph(header_text, header_style),
                customer_table,
                Spacer(1, 20)
            ])
        
        return flowables
    
    def _create_company_info_section(self, company_info: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine elegante Firmen-Informationssektion"""
        flowables = []
        
        # Sammle Firmeninformationen
        company_lines = []
        
        if company_info.get('name'):
            company_lines.append(f"<b>{company_info['name']}</b>")
        
        if company_info.get('street'):
            company_lines.append(company_info['street'])
        
        if company_info.get('zip_code') or company_info.get('city'):
            zip_city = f"{company_info.get('zip_code', '')} {company_info.get('city', '')}".strip()
            if zip_city:
                company_lines.append(zip_city)
        
        # Kontaktdaten
        contact_lines = []
        if company_info.get('phone'):
            contact_lines.append(f"Tel.: {company_info['phone']}")
        if company_info.get('email'):
            contact_lines.append(f"E-Mail: {company_info['email']}")
        if company_info.get('website'):
            contact_lines.append(f"Web: {company_info['website']}")
        
        company_lines.extend(contact_lines)
        
        # Steuerliche Informationen
        if company_info.get('tax_id'):
            company_lines.append(f"USt-ID: {company_info['tax_id']}")
        
        if company_lines:
            company_text = '<br/>'.join(company_lines)
            
            # Erstelle zweispaltige Anordnung
            table_data = [['', company_text]]
            company_table = Table(table_data, colWidths=[8*cm, 10*cm])
            
            company_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (1, 0), (1, -1), 10),
                ('TEXTCOLOR', (1, 0), (1, -1), HexColor(self.colors['text_secondary'])),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
            ]))
            
            flowables.extend([
                Spacer(1, 40),
                company_table
            ])
        
        return flowables
    
    def create_enhanced_section_header(self, title: str, subtitle: str = None) -> List[Any]:
        """Erstellt einen modernen Abschnittsheader"""
        flowables = []
        
        # Haupttitel
        flowables.append(Paragraph(title, self.enhanced_styles['SectionHeader']))
        
        # Untertitel falls vorhanden
        if subtitle:
            flowables.append(Paragraph(subtitle, self.enhanced_styles['SubSectionHeader']))
        
        # Trennlinie
        divider = self.components.create_section_divider(
            thickness=1,
            spacing_before=5,
            spacing_after=15
        )
        flowables.append(divider)
        
        return flowables
    
    def create_enhanced_data_table(self, 
                                 data: List[List[str]], 
                                 headers: List[str] = None,
                                 table_type: str = 'standard',
                                 col_widths: List[float] = None) -> Table:
        """
        Erstellt eine moderne Datentabelle
        
        Args:
            data: Tabellendaten
            headers: Spaltenüberschriften
            table_type: Typ der Tabelle ('standard', 'financial', 'component')
            col_widths: Spaltenbreiten
        """
        # Füge Header hinzu falls vorhanden
        if headers:
            table_data = [headers] + data
        else:
            table_data = data
        
        # Erstelle Tabelle
        table = Table(table_data, colWidths=col_widths)
        
        # Wähle passenden Stil
        style_map = {
            'standard': 'StandardTable',
            'financial': 'FinancialTable',
            'component': 'ComponentTable'
        }
        
        style_name = style_map.get(table_type, 'StandardTable')
        table.setStyle(self.table_styles[style_name])
        
        return table
    
    def create_enhanced_info_box(self, content: str, box_type: str = 'info', title: str = None) -> List[Any]:
        """Erstellt eine moderne Info-Box"""
        return self.components.create_info_box(content, box_type, title)
    
    def create_financial_summary_section(self, 
                                       analysis_results: Dict[str, Any], 
                                       texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine moderne Finanzübersicht"""
        flowables = []
        
        # Sektion Header
        header = self.create_enhanced_section_header(
            get_text(texts, 'pdf_financial_summary_title', 'Finanzübersicht'),
            get_text(texts, 'pdf_financial_summary_subtitle', 'Kosten und Einsparungen im Überblick')
        )
        flowables.extend(header)
        
        # Finanzielle Hauptkennzahlen
        financial_data = []
        
        # Sammle Finanzdaten aus analysis_results
        total_cost = analysis_results.get('total_system_cost', 0)
        annual_savings = analysis_results.get('annual_savings', 0)
        payback_period = analysis_results.get('payback_period_years', 0)
        
        if total_cost:
            financial_data.append([
                'Gesamtinvestition',
                format_german_number(total_cost, '€', precision=0)
            ])
        
        if annual_savings:
            financial_data.append([
                'Jährliche Einsparung',
                format_german_number(annual_savings, '€', precision=0)
            ])
        
        if payback_period:
            financial_data.append([
                'Amortisationszeit',
                format_german_number(payback_period, 'Jahre', precision=1)
            ])
        
        # 25-Jahres-Gewinn
        total_25_year_gain = analysis_results.get('total_25_year_gain', 0)
        if total_25_year_gain:
            financial_data.append([
                'Gewinn über 25 Jahre',
                format_german_number(total_25_year_gain, '€', precision=0)
            ])
        
        if financial_data:
            # Erstelle moderne Finanztabelle
            financial_table = self.create_enhanced_data_table(
                data=financial_data,
                table_type='financial',
                col_widths=[8*cm, 6*cm]
            )
            flowables.append(financial_table)
            flowables.append(Spacer(1, 20))
        
        # Zusätzliche Info-Box mit wichtigen Hinweisen
        info_content = get_text(texts, 'pdf_financial_info_box', 
                              'Alle Berechnungen basieren auf aktuellen Strompreisen und gesetzlichen Bestimmungen. '
                              'Individuelle Abweichungen sind möglich.')
        info_box = self.create_enhanced_info_box(
            content=info_content,
            box_type='info',
            title='Wichtiger Hinweis'
        )
        flowables.extend(info_box)
        
        return flowables
    
    def create_technical_overview_section(self, 
                                        project_data: Dict[str, Any], 
                                        texts: Dict[str, str]) -> List[Any]:
        """Erstellt eine moderne technische Übersicht"""
        flowables = []
        
        # Sektion Header
        header = self.create_enhanced_section_header(
            get_text(texts, 'pdf_technical_overview_title', 'Technische Übersicht'),
            get_text(texts, 'pdf_technical_overview_subtitle', 'Ihr Photovoltaiksystem im Detail')
        )
        flowables.extend(header)
        
        # Technische Daten sammeln
        project_details = project_data.get('project_details', {})
        
        technical_data = []
        
        # PV-Leistung
        pv_power = project_details.get('pv_peak_power_kw', 0)
        if pv_power:
            technical_data.append([
                'PV-Spitzenleistung',
                format_german_number(pv_power, 'kWp', precision=2)
            ])
        
        # Jahresertrag
        annual_yield = project_details.get('annual_yield_kwh', 0)
        if annual_yield:
            technical_data.append([
                'Erwarteter Jahresertrag',
                format_german_number(annual_yield, 'kWh', precision=0)
            ])
        
        # Anzahl Module
        module_count = project_details.get('module_count', 0)
        if module_count:
            technical_data.append([
                'Anzahl PV-Module',
                str(module_count)
            ])
        
        # Dachfläche
        roof_area = project_details.get('roof_area_m2', 0)
        if roof_area:
            technical_data.append([
                'Benötigte Dachfläche',
                format_german_number(roof_area, 'm²', precision=1)
            ])
        
        if technical_data:
            # Erstelle technische Übersichtstabelle
            technical_table = self.create_enhanced_data_table(
                data=technical_data,
                table_type='component',
                col_widths=[10*cm, 6*cm]
            )
            flowables.append(technical_table)
            flowables.append(Spacer(1, 20))
        
        return flowables

def integrate_enhanced_pdf_with_existing(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    sections_to_include: Optional[List[str]],
    inclusion_options: Dict[str, Any],
    texts: Dict[str, str],
    color_scheme: str = 'PROFESSIONAL_BLUE',
    **kwargs
) -> Optional[bytes]:
    """
    Hauptfunktion zur Integration der erweiterten PDF-Features
    mit dem bestehenden PDF-Generator
    
    Diese Funktion kann anstelle der bestehenden generate_offer_pdf
    verwendet werden, um moderne PDF-Features zu nutzen
    """
    
    if not _REPORTLAB_AVAILABLE or not _ENHANCED_AVAILABLE:
        print("Erweiterte PDF-Features nicht verfügbar, verwende Standard-Generator")
        # Fallback auf bestehenden Generator
        try:
            from pdf_generator import generate_offer_pdf
            return generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=company_logo_base64,
                selected_title_image_b64=selected_title_image_b64,
                selected_offer_title_text=selected_offer_title_text,
                selected_cover_letter_text=selected_cover_letter_text,
                sections_to_include=sections_to_include,
                inclusion_options=inclusion_options,
                texts=texts,
                **kwargs
            )
        except Exception as e:
            print(f"Fallback auf Standard-Generator fehlgeschlagen: {e}")
            return None
    
    try:
        # Erstelle erweiterten PDF-Generator
        enhanced_generator = EnhancedPDFGenerator(color_scheme=color_scheme)
        
        # PDF-Ausgabe erstellen
        output_buffer = io.BytesIO()
        
        # Verwende die bestehende page_layout_handler Funktion für Konsistenz
        doc = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )
        
        story = []
        
        # === DECKBLATT ===
        if 'cover_page' in sections_to_include or not sections_to_include:
            cover_page = enhanced_generator.create_enhanced_cover_page(
                project_data=project_data,
                company_info=company_info,
                texts=texts,
                company_logo_base64=company_logo_base64,
                title_image_b64=selected_title_image_b64,
                offer_title=selected_offer_title_text,
                offer_number=kwargs.get('offer_number', 'AN-2025-001')
            )
            story.extend(cover_page)
            story.append(PageBreak())
        
        # === ANSCHREIBEN ===
        if selected_cover_letter_text and selected_cover_letter_text.strip():
            story.extend([
                Paragraph("Anschreiben", enhanced_generator.enhanced_styles['SectionHeader']),
                Spacer(1, 1*cm),
                Paragraph(selected_cover_letter_text, enhanced_generator.enhanced_styles['BodyText']),
                PageBreak()
            ])
        
        # === TECHNISCHE ÜBERSICHT ===
        if 'TechnicalComponents' in sections_to_include or not sections_to_include:
            technical_section = enhanced_generator.create_technical_overview_section(
                project_data=project_data,
                texts=texts
            )
            story.extend(technical_section)
        
        # === FINANZÜBERSICHT ===
        if analysis_results and ('CostDetails' in sections_to_include or not sections_to_include):
            financial_section = enhanced_generator.create_financial_summary_section(
                analysis_results=analysis_results,
                texts=texts
            )
            story.extend(financial_section)
        
        # PDF erstellen
        doc.build(story)
        
        # Rückgabe der PDF-Bytes
        output_buffer.seek(0)
        return output_buffer.getvalue()
        
    except Exception as e:
        print(f"Fehler bei erweiterter PDF-Generierung: {e}")
        traceback.print_exc()
        return None

    def generate_enhanced_pdf(self,
                            project_data: Dict[str, Any],
                            analysis_results: Dict[str, Any],
                            company_info: Dict[str, Any],
                            company_logo_base64: Optional[str] = None,
                            selected_title_image_b64: Optional[str] = None,
                            selected_offer_title_text: Optional[str] = None,
                            selected_cover_letter_text: Optional[str] = None,
                            sections_to_include: Optional[List[str]] = None,
                            inclusion_options: Optional[Dict[str, Any]] = None,
                            load_admin_setting_func: Optional[Callable] = None,
                            save_admin_setting_func: Optional[Callable] = None,
                            list_products_func: Optional[Callable] = None,
                            get_product_by_id_func: Optional[Callable] = None,
                            db_list_company_documents_func: Optional[Callable] = None,
                            active_company_id: Optional[int] = None,
                            texts: Optional[Dict[str, str]] = None,
                            **kwargs) -> Optional[bytes]:
        """
        Hauptfunktion für die erweiterte PDF-Generierung
        Verwendet moderne Design-Features und behält alle ursprünglichen Funktionen bei
        """
        if not _REPORTLAB_AVAILABLE:
            return None
            
        try:
            print("🎨 Generiere erweiterte PDF mit modernen Design-Features...")
            
            # Erstelle PDF-Buffer
            buffer = io.BytesIO()
            
            # Erstelle PDF-Dokument mit erweiterten Stilen
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  leftMargin=2*cm, rightMargin=2*cm,
                                  topMargin=2*cm, bottomMargin=2*cm)
            
            # Erstelle PDF-Story mit erweiterten Komponenten
            story = []
            
            # === DECKBLATT ===
            print("📄 Erstelle modernes Deckblatt...")
            cover_page = self.create_enhanced_cover_page(
                project_data=project_data,
                company_info=company_info,
                texts=texts or {},
                company_logo_base64=company_logo_base64,
                title_image_b64=selected_title_image_b64,
                offer_title=selected_offer_title_text,
                offer_number=analysis_results.get('offer_number', 'ANG-2025-001')
            )
            story.extend(cover_page)
            story.append(PageBreak())
            
            # === ANSCHREIBEN ===
            if selected_cover_letter_text:
                print("📝 Erstelle Anschreiben...")
                cover_letter = self._create_cover_letter_section(
                    selected_cover_letter_text, texts or {}
                )
                story.extend(cover_letter)
                story.append(PageBreak())
            
            # === PROJEKTÜBERSICHT ===
            if sections_to_include and 'project_overview' in sections_to_include:
                print("📊 Erstelle Projektübersicht...")
                project_overview = self.create_enhanced_project_overview(
                    project_data, analysis_results, texts or {}
                )
                story.extend(project_overview)
                story.append(PageBreak())
            
            # === FINANZEN ===
            if sections_to_include and 'financial_analysis' in sections_to_include:
                print("💰 Erstelle Finanzanalyse...")
                financial_section = self.create_enhanced_financial_overview(
                    analysis_results, texts or {}
                )
                story.extend(financial_section)
                story.append(PageBreak())
            
            # === KOMPONENTEN ===
            if sections_to_include and 'components' in sections_to_include:
                print("🔧 Erstelle Komponentenübersicht...")
                components_section = self.create_enhanced_components_section(
                    project_data, analysis_results, texts or {}, 
                    list_products_func, get_product_by_id_func
                )
                story.extend(components_section)
            
            # === ERWEITERTE VISUALISIERUNGEN ===
            if inclusion_options and inclusion_options.get('include_charts', True):
                print("📈 Erstelle erweiterte Diagramme...")
                charts_section = self.create_enhanced_charts_section(
                    analysis_results, texts or {}
                )
                story.extend(charts_section)
            
            # === FALLBACK AUF STANDARD-PDF-GENERATOR ===
            # Wenn die erweiterte Generierung fehlschlägt, versuche Standard-Methoden
            if not story:
                print("⚠️ Erweiterte Story ist leer - versuche Standard-PDF-Generator...")
                try:
                    from pdf_generator import generate_offer_pdf
                    return generate_offer_pdf(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        company_info=company_info,
                        company_logo_base64=company_logo_base64,
                        selected_title_image_b64=selected_title_image_b64,
                        selected_offer_title_text=selected_offer_title_text,
                        selected_cover_letter_text=selected_cover_letter_text,
                        sections_to_include=sections_to_include,
                        inclusion_options=inclusion_options,
                        load_admin_setting_func=load_admin_setting_func,
                        save_admin_setting_func=save_admin_setting_func,
                        list_products_func=list_products_func,
                        get_product_by_id_func=get_product_by_id_func,
                        db_list_company_documents_func=db_list_company_documents_func,
                        active_company_id=active_company_id,
                        texts=texts,
                        **kwargs
                    )
                except Exception as fallback_error:
                    print(f"❌ Fallback auf Standard-PDF-Generator fehlgeschlagen: {fallback_error}")
                    return None
            
            # === PDF ERSTELLEN ===
            print("🔨 Erstelle PDF-Dokument...")
            doc.build(story)
            
            # PDF-Bytes zurückgeben
            buffer.seek(0)
            pdf_bytes = buffer.read()
            buffer.close()
            
            print(f"✅ Erweiterte PDF erfolgreich erstellt ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            print(f"❌ Fehler bei erweiterter PDF-Generierung: {e}")
            traceback.print_exc()
            
            # Fallback auf Standard-PDF-Generator
            try:
                print("🔄 Versuche Fallback auf Standard-PDF-Generator...")
                from pdf_generator import generate_offer_pdf
                return generate_offer_pdf(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info,
                    company_logo_base64=company_logo_base64,
                    selected_title_image_b64=selected_title_image_b64,
                    selected_offer_title_text=selected_offer_title_text,
                    selected_cover_letter_text=selected_cover_letter_text,
                    sections_to_include=sections_to_include,
                    inclusion_options=inclusion_options,
                    load_admin_setting_func=load_admin_setting_func,
                    save_admin_setting_func=save_admin_setting_func,
                    list_products_func=list_products_func,
                    get_product_by_id_func=get_product_by_id_func,
                    db_list_company_documents_func=db_list_company_documents_func,
                    active_company_id=active_company_id,
                    texts=texts,
                    **kwargs
                )
            except Exception as fallback_error:
                print(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")
                return None

# === KOMPATIBILITÄTSFUNKTIONEN ===

def upgrade_existing_pdf_styles():
    """
    Funktion zum Upgrade der bestehenden PDF-Stile
    ohne Überschreibung der ursprünglichen Funktionen
    """
    if not _ENHANCED_AVAILABLE:
        return False
    
    try:
        # Erweitere die globalen STYLES mit modernen Versionen
        enhanced_styles = EnhancedPDFStyles()
        new_styles = enhanced_styles.create_enhanced_styles()
        
        # Füge neue Stile hinzu, ohne bestehende zu überschreiben
        for style_name, style_obj in new_styles.items():
            if style_name not in STYLES:
                STYLES.add(style_obj)
        
        return True
    except Exception as e:
        print(f"Fehler beim Upgrade der PDF-Stile: {e}")
        return False

# === HAUPT-FUNKTION FÜR DROP-IN-REPLACEMENT ===

def generate_offer_pdf_enhanced(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str] = None,
    selected_title_image_b64: Optional[str] = None,
    selected_offer_title_text: Optional[str] = None,
    selected_cover_letter_text: Optional[str] = None,
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
    """
    Erweiterte PDF-Generierung mit modernen Designs
    
    Diese Funktion ist ein Drop-in-Replacement für generate_offer_pdf aus pdf_generator.py
    und fügt moderne, professionelle Designs hinzu.
    """
    
    if not _REPORTLAB_AVAILABLE:
        print("⚠️ ReportLab nicht verfügbar - Fallback auf Standard-PDF-Generator")
        try:
            from pdf_generator import generate_offer_pdf
            return generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=company_logo_base64,
                selected_title_image_b64=selected_title_image_b64,
                selected_offer_title_text=selected_offer_title_text,
                selected_cover_letter_text=selected_cover_letter_text,
                sections_to_include=sections_to_include,
                inclusion_options=inclusion_options,
                load_admin_setting_func=load_admin_setting_func,
                save_admin_setting_func=save_admin_setting_func,
                list_products_func=list_products_func,
                get_product_by_id_func=get_product_by_id_func,
                db_list_company_documents_func=db_list_company_documents_func,
                active_company_id=active_company_id,
                texts=texts,
                **kwargs
            )
        except Exception as e:
            print(f"❌ Fehler beim Fallback auf Standard-Generator: {e}")
            return None
    
    try:
        print("🎨 Starte erweiterte PDF-Generierung mit modernen Designs...")
        
        # Erstelle erweiterte Design-Preset
        if _ENHANCED_AVAILABLE:
            style_preset = create_enhanced_style_preset('PROFESSIONAL_BLUE')
        else:
            # Fallback
            style_preset = {
                'color_scheme': {},
                'paragraph_styles': {},
                'table_styles': {},
                'components': None
            }
        
        # Initialisiere den erweiterten PDF-Generator
        generator = EnhancedPDFGenerator(
            color_scheme=style_preset['color_scheme'],
            enhanced_styles=style_preset['paragraph_styles'],
            table_styles=style_preset['table_styles'],
            components=style_preset['components']
        )
        
        # Generiere PDF mit erweiterten Features
        pdf_bytes = generator.generate_enhanced_pdf(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info,
            company_logo_base64=company_logo_base64,
            selected_title_image_b64=selected_title_image_b64,
            selected_offer_title_text=selected_offer_title_text,
            selected_cover_letter_text=selected_cover_letter_text,
            sections_to_include=sections_to_include,
            inclusion_options=inclusion_options,
            load_admin_setting_func=load_admin_setting_func,
            save_admin_setting_func=save_admin_setting_func,
            list_products_func=list_products_func,
            get_product_by_id_func=get_product_by_id_func,
            db_list_company_documents_func=db_list_company_documents_func,
            active_company_id=active_company_id,
            texts=texts,
            **kwargs
        )
        
        print("✅ Erweiterte PDF-Generierung erfolgreich abgeschlossen!")
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ Fehler in der erweiterten PDF-Generierung: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        
        # Fallback auf Standard-PDF-Generator
        try:
            print("🔄 Versuche Fallback auf Standard-PDF-Generator...")
            from pdf_generator import generate_offer_pdf
            return generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                company_logo_base64=company_logo_base64,
                selected_title_image_b64=selected_title_image_b64,
                selected_offer_title_text=selected_offer_title_text,
                selected_cover_letter_text=selected_cover_letter_text,
                sections_to_include=sections_to_include,
                inclusion_options=inclusion_options,
                load_admin_setting_func=load_admin_setting_func,
                save_admin_setting_func=save_admin_setting_func,
                list_products_func=list_products_func,
                get_product_by_id_func=get_product_by_id_func,
                db_list_company_documents_func=db_list_company_documents_func,
                active_company_id=active_company_id,
                texts=texts,
                **kwargs
            )
        except Exception as fallback_error:
            print(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")
            return None
