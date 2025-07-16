"""
Datei: pdf_generator_cleaned.py
Zweck: Erzeugt Angebots-PDFs für die Solar-App.
Autor: Gemini Ultra (maximale KI-Performance)
Datum: 2025-06-21
"""

from __future__ import annotations
import base64
import io
import math
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
import os
from io import BytesIO

_REPORTLAB_AVAILABLE = False
_PYPDF_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (Frame, Image, PageBreak, PageTemplate,
        Paragraph, SimpleDocTemplate, Spacer, Table,
        TableStyle, Flowable, KeepInFrame, KeepTogether)
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

# Pfade für Produktdatenblätter und Firmendokumente
_PDF_GENERATOR_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "product_datasheets")
COMPANY_DOCS_BASE_DIR_PDF_GEN = os.path.join(_PDF_GENERATOR_BASE_DIR, "data", "company_docs")


def get_text(texts_dict: Dict[str, str], key: str, fallback_text_value: Optional[str] = None) -> str:
    """Hilfsfunktion zum Abrufen von Texten mit Fallback"""
    if not isinstance(texts_dict, dict): 
        return fallback_text_value if fallback_text_value is not None else key
    if fallback_text_value is None: 
        fallback_text_value = key.replace("_", " ").title() + " (PDF-Text fehlt)"
    retrieved = texts_dict.get(key, fallback_text_value)
    return str(retrieved)


# Farbkonstanten
PRIMARY_COLOR_HEX = "#1B365D"    # Dunkelblau
SECONDARY_COLOR_HEX = "#2E8B57"  # Solargrün
ACCENT_COLOR_HEX = "#FFB347"     # Sonnenorange
TEXT_COLOR_HEX = "#2C3E50"       # Anthrazit
BACKGROUND_COLOR_HEX = "#F8F9FA" # Hellgrau
SEPARATOR_LINE_COLOR_HEX = "#E9ECEF" # Subtile Linienfarbe

# Schriftarten
FONT_NORMAL = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"

# Styles initialisieren
STYLES: Any = {}

if _REPORTLAB_AVAILABLE:
    STYLES = getSampleStyleSheet()
    STYLES.add(ParagraphStyle(
        name='NormalLeft', 
        alignment=TA_LEFT, 
        fontName=FONT_NORMAL, 
        fontSize=10, 
        leading=12, 
        textColor=colors.HexColor(TEXT_COLOR_HEX)
    ))
    STYLES.add(ParagraphStyle(
        name='NormalRight', 
        alignment=TA_RIGHT, 
        fontName=FONT_NORMAL, 
        fontSize=10, 
        leading=12, 
        textColor=colors.HexColor(TEXT_COLOR_HEX)
    ))
    STYLES.add(ParagraphStyle(
        name='NormalCenter', 
        alignment=TA_CENTER, 
        fontName=FONT_NORMAL, 
        fontSize=10, 
        leading=12, 
        textColor=colors.HexColor(TEXT_COLOR_HEX)
    ))
    STYLES.add(ParagraphStyle(
        name='OfferTitle', 
        parent=STYLES['h1'], 
        fontName=FONT_BOLD, 
        fontSize=24, 
        alignment=TA_CENTER, 
        spaceBefore=1.5*cm, 
        spaceAfter=1.5*cm, 
        textColor=colors.HexColor(PRIMARY_COLOR_HEX), 
        leading=28
    ))
    STYLES.add(ParagraphStyle(
        name='SectionTitle', 
        parent=STYLES['h2'], 
        fontName=FONT_BOLD, 
        fontSize=16, 
        spaceBefore=1.2*cm, 
        spaceAfter=0.8*cm, 
        keepWithNext=1, 
        textColor=colors.HexColor(PRIMARY_COLOR_HEX), 
        leading=20
    ))


def _update_styles_with_dynamic_colors(design_settings: Dict[str, str]):
    """Aktualisiert die Styles mit dynamischen Farben"""
    if not _REPORTLAB_AVAILABLE:
        return
    
    primary_color = design_settings.get('primary_color', PRIMARY_COLOR_HEX)
    secondary_color = design_settings.get('secondary_color', SECONDARY_COLOR_HEX)
    
    # Styles mit neuen Farben aktualisieren
    STYLES['OfferTitle'].textColor = colors.HexColor(primary_color)
    STYLES['SectionTitle'].textColor = colors.HexColor(primary_color)


def _get_next_offer_number(texts: Dict[str,str], load_admin_setting_func: Callable, save_admin_setting_func: Callable) -> str:
    """Generiert die nächste Angebotsnummer"""
    try:
        current_number = load_admin_setting_func('last_offer_number', 0)
        next_number = current_number + 1
        save_admin_setting_func('last_offer_number', next_number)
        return f"A{next_number:05d}"
    except Exception:
        return f"A{datetime.now().strftime('%Y%m%d')}-001"


def _get_image_flowable(image_data_input: Optional[Union[str, bytes]], desired_width: float, texts: Dict[str, str], caption_text_key: Optional[str] = None, max_height: Optional[float] = None, align: str = 'CENTER') -> List[Any]:
    """Erstellt ein Image-Flowable aus Base64-Daten"""
    if not _REPORTLAB_AVAILABLE or not image_data_input:
        return []
    
    try:
        if isinstance(image_data_input, str):
            image_bytes = base64.b64decode(image_data_input)
        else:
            image_bytes = image_data_input
        
        image_reader = ImageReader(io.BytesIO(image_bytes))
        
        # Aspect Ratio berechnen
        img_width, img_height = image_reader.getSize()
        aspect_ratio = img_height / img_width
        
        # Höhe basierend auf gewünschter Breite berechnen
        calculated_height = desired_width * aspect_ratio
        
        # Max-Höhe prüfen
        if max_height and calculated_height > max_height:
            calculated_height = max_height
            desired_width = calculated_height / aspect_ratio
        
        image = Image(image_reader, width=desired_width, height=calculated_height)
        
        return [image]
        
    except Exception as e:
        return [Paragraph(
            get_text(texts, "image_not_available", "Bild nicht verfügbar"), 
            STYLES.get('NormalCenter')
        )]


def generate_offer_pdf(
    project_data: Dict[str, Any],
    analysis_results: Optional[Dict[str, Any]],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    sections_to_include: Optional[List[str]],
    inclusion_options: Dict[str, Any],
    load_admin_setting_func: Callable, 
    save_admin_setting_func: Callable, 
    list_products_func: Callable, 
    get_product_by_id_func: Callable, 
    db_list_company_documents_func: Callable[[int, Optional[str]], List[Dict[str, Any]]],
    active_company_id: Optional[int],
    texts: Dict[str, str],
    use_modern_design: bool = True,
    **kwargs
) -> Optional[bytes]:
    """
    Erzeugt ein PDF-Angebot für Photovoltaik-Projekte.
    
    Args:
        project_data: Projektdaten mit Kunden- und Komponenteninformationen
        analysis_results: Ergebnisse der Wirtschaftlichkeitsanalyse
        company_info: Firmeninformationen
        company_logo_base64: Base64-kodiertes Firmenlogo
        selected_title_image_b64: Base64-kodiertes Titelbild
        selected_offer_title_text: Titel des Angebots
        selected_cover_letter_text: Anschreiben-Text
        sections_to_include: Liste der einzuschließenden Sektionen
        inclusion_options: Optionen für zusätzliche Inhalte
        load_admin_setting_func: Funktion zum Laden von Admin-Einstellungen
        save_admin_setting_func: Funktion zum Speichern von Admin-Einstellungen
        list_products_func: Funktion zum Auflisten von Produkten
        get_product_by_id_func: Funktion zum Abrufen von Produkten nach ID
        db_list_company_documents_func: Funktion zum Abrufen von Firmendokumenten
        active_company_id: ID der aktiven Firma
        texts: Übersetzungstexte
        use_modern_design: Ob modernes Design verwendet werden soll
        **kwargs: Zusätzliche Parameter
        
    Returns:
        PDF-Bytes oder None bei Fehlern
    """
    
    if not _REPORTLAB_AVAILABLE:
        print("⚠️ ReportLab nicht verfügbar - kann kein PDF erstellen")
        return _create_no_data_fallback_pdf(texts, project_data.get('customer_data', {}) if project_data else {})
   
    # DATENVALIDIERUNG: Prüfe Verfügbarkeit der erforderlichen Daten
    validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
    
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
    
    try:
        # Design-Einstellungen laden
        design_settings = load_admin_setting_func('pdf_design_settings', {
            'primary_color': PRIMARY_COLOR_HEX, 
            'secondary_color': SECONDARY_COLOR_HEX
        })
        if isinstance(design_settings, dict):
            _update_styles_with_dynamic_colors(design_settings)
        
        # PDF-Konfiguration
        buffer = BytesIO()
        offer_number = _get_next_offer_number(texts, load_admin_setting_func, save_admin_setting_func)
        
        # Angebotsnummer optional aus inclusion_options überschreiben
        if inclusion_options.get('custom_offer_number'):
            offer_number = inclusion_options['custom_offer_number']
        
        # PDF-Dokument erstellen
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=pagesizes.A4,
            topMargin=2*cm, 
            bottomMargin=2*cm, 
            leftMargin=2*cm, 
            rightMargin=2*cm
        )
        
        # Story-Elemente sammeln
        story = []
        
        # Deckblatt
        story.extend(_create_cover_page(
            project_data, company_info, company_logo_base64, 
            selected_title_image_b64, selected_offer_title_text,
            selected_cover_letter_text, offer_number, texts
        ))
        
        # Seitenumbruch nach Deckblatt
        story.append(PageBreak())
        
        # Inhaltssektionen
        if sections_to_include:
            if 'project_overview' in sections_to_include:
                story.extend(_create_project_overview_section(project_data, texts))
            
            if 'components' in sections_to_include and project_data:
                story.extend(_create_components_section(
                    project_data, list_products_func, get_product_by_id_func, texts
                ))
            
            if 'analysis' in sections_to_include and analysis_results:
                story.extend(_create_analysis_section(analysis_results, texts))
            
            if 'costs' in sections_to_include and analysis_results:
                story.extend(_create_costs_section(analysis_results, texts))
            
            if 'financing' in sections_to_include and analysis_results:
                story.extend(_create_financing_section(analysis_results, texts))
        
        # Footer-Informationen
        story.extend(_create_footer_section(company_info, texts))
        
        # PDF erstellen
        doc.build(story)
        main_pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Anhänge hinzufügen, falls gewünscht
        if inclusion_options.get('include_all_documents') and _PYPDF_AVAILABLE:
            return _append_additional_documents(
                main_pdf_bytes, inclusion_options, project_data,
                get_product_by_id_func, db_list_company_documents_func,
                active_company_id
            )
        
        return main_pdf_bytes
        
    except Exception as e:
        print(f"❌ Fehler bei PDF-Erstellung: {e}")
        traceback.print_exc()
        # Fallback-PDF erstellen
        customer_data = project_data.get('customer_data', {}) if project_data else {}
        return _create_no_data_fallback_pdf(texts, customer_data)


def _create_cover_page(
    project_data: Dict[str, Any], 
    company_info: Dict[str, Any], 
    company_logo_base64: Optional[str],
    selected_title_image_b64: Optional[str],
    selected_offer_title_text: str,
    selected_cover_letter_text: str,
    offer_number: str,
    texts: Dict[str, str]
) -> List[Any]:
    """Erstellt das Deckblatt für das PDF"""
    elements = []
    
    # Titel
    elements.append(Paragraph(selected_offer_title_text, STYLES.get('OfferTitle')))
    elements.append(Spacer(1, 1*cm))
    
    # Angebotsnummer
    elements.append(Paragraph(
        f"{get_text(texts, 'offer_number', 'Angebots-Nr.')}: {offer_number}",
        STYLES.get('SectionTitle')
    ))
    elements.append(Spacer(1, 1*cm))
    
    # Firmenlogo falls vorhanden
    if company_logo_base64:
        try:
            logo_image = _get_image_flowable(company_logo_base64, 4*cm, texts)
            if logo_image:
                elements.extend(logo_image)
                elements.append(Spacer(1, 1*cm))
        except Exception:
            pass
    
    # Firmeninformationen
    company_text = f"""
    <b>{company_info.get('name', '')}</b><br/>
    {company_info.get('street', '')}<br/>
    {company_info.get('zip_code', '')} {company_info.get('city', '')}<br/>
    """
    elements.append(Paragraph(company_text, STYLES.get('NormalCenter')))
    elements.append(Spacer(1, 2*cm))
    
    # Kundendaten falls verfügbar
    if project_data and project_data.get('customer_data'):
        customer = project_data['customer_data']
        customer_text = f"""
        <b>{get_text(texts, 'customer_info', 'Kunde')}:</b><br/>
        {customer.get('first_name', '')} {customer.get('last_name', '')}<br/>
        {customer.get('street', '')}<br/>
        {customer.get('zip_code', '')} {customer.get('city', '')}
        """
        elements.append(Paragraph(customer_text, STYLES.get('NormalLeft')))
    
    return elements


def _create_project_overview_section(project_data: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Projektübersicht"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'project_overview_title', 'Projektübersicht'),
        STYLES.get('SectionTitle')
    ))
    
    if project_data and project_data.get('project_details'):
        details = project_data['project_details']
        
        # Grunddaten
        data = []
        if details.get('module_quantity'):
            data.append([
                get_text(texts, 'module_count', 'Anzahl Module'),
                str(details['module_quantity'])
            ])
        
        if details.get('peak_power'):
            data.append([
                get_text(texts, 'peak_power', 'Spitzenleistung'),
                f"{details['peak_power']} kWp"
            ])
        
        if data:
            table = Table(data)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(table)
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_components_section(
    project_data: Dict[str, Any], 
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    texts: Dict[str, str]
) -> List[Any]:
    """Erstellt die Komponenten-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'components_title', 'Systemkomponenten'),
        STYLES.get('SectionTitle')
    ))
    
    if project_data and project_data.get('project_details'):
        details = project_data['project_details']
        
        # Module
        if details.get('selected_module_id'):
            try:
                module = get_product_by_id_func(details['selected_module_id'])
                if module:
                    elements.append(Paragraph(
                        f"<b>{get_text(texts, 'solar_module', 'Solarmodul')}:</b> {module.get('model_name', 'Unbekannt')}",
                        STYLES.get('NormalLeft')
                    ))
            except Exception:
                pass
        
        # Wechselrichter
        if details.get('selected_inverter_id'):
            try:
                inverter = get_product_by_id_func(details['selected_inverter_id'])
                if inverter:
                    elements.append(Paragraph(
                        f"<b>{get_text(texts, 'inverter', 'Wechselrichter')}:</b> {inverter.get('model_name', 'Unbekannt')}",
                        STYLES.get('NormalLeft')
                    ))
            except Exception:
                pass
        
        # Speicher
        if details.get('include_storage') and details.get('selected_storage_id'):
            try:
                storage = get_product_by_id_func(details['selected_storage_id'])
                if storage:
                    elements.append(Paragraph(
                        f"<b>{get_text(texts, 'battery_storage', 'Batteriespeicher')}:</b> {storage.get('model_name', 'Unbekannt')}",
                        STYLES.get('NormalLeft')
                    ))
            except Exception:
                pass
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_analysis_section(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Analyse-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'analysis_title', 'Wirtschaftlichkeitsanalyse'),
        STYLES.get('SectionTitle')
    ))
    
    # Wirtschaftlichkeits-KPIs
    data = []
    
    if analysis_results.get('annual_yield_kwh'):
        data.append([
            get_text(texts, 'annual_yield', 'Jährlicher Ertrag'),
            f"{analysis_results['annual_yield_kwh']:,.0f} kWh".replace(',', '.')
        ])
    
    if analysis_results.get('autarkie_grad_percent'):
        data.append([
            get_text(texts, 'self_sufficiency', 'Autarkiegrad'),
            f"{analysis_results['autarkie_grad_percent']:.1f}%"
        ])
    
    if analysis_results.get('eigenverbrauch_percent'):
        data.append([
            get_text(texts, 'self_consumption', 'Eigenverbrauch'),
            f"{analysis_results['eigenverbrauch_percent']:.1f}%"
        ])
    
    if analysis_results.get('payback_years'):
        data.append([
            get_text(texts, 'payback_period', 'Amortisationszeit'),
            f"{analysis_results['payback_years']:.1f} Jahre"
        ])
    
    if data:
        table = Table(data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table)
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_costs_section(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Kosten-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'costs_title', 'Kostenübersicht'),
        STYLES.get('SectionTitle')
    ))
    
    data = []
    
    # Investitionskosten
    if analysis_results.get('total_investment_cost'):
        data.append([
            get_text(texts, 'investment_cost', 'Investitionskosten'),
            f"{analysis_results['total_investment_cost']:,.2f} €".replace(',', '.')
        ])
    
    # Jährliche Einsparungen
    if analysis_results.get('annual_savings'):
        data.append([
            get_text(texts, 'annual_savings', 'Jährliche Einsparungen'),
            f"{analysis_results['annual_savings']:,.2f} €".replace(',', '.')
        ])
    
    # 20-Jahre Gewinn
    if analysis_results.get('total_profit_20_years'):
        data.append([
            get_text(texts, 'total_profit_20y', 'Gewinn nach 20 Jahren'),
            f"{analysis_results['total_profit_20_years']:,.2f} €".replace(',', '.')
        ])
    
    if data:
        table = Table(data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NORMAL),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table)
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_financing_section(analysis_results: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt die Finanzierungs-Sektion"""
    elements = []
    
    elements.append(Paragraph(
        get_text(texts, 'financing_title', 'Finanzierungsmöglichkeiten'),
        STYLES.get('SectionTitle')
    ))
    
    elements.append(Paragraph(
        get_text(texts, 'financing_info', 'Sprechen Sie uns auf individuelle Finanzierungslösungen an.'),
        STYLES.get('NormalLeft')
    ))
    
    elements.append(Spacer(1, 1*cm))
    return elements


def _create_footer_section(company_info: Dict[str, Any], texts: Dict[str, str]) -> List[Any]:
    """Erstellt den Footer-Bereich"""
    elements = []
    
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph(
        get_text(texts, 'contact_info', 'Kontaktinformationen'),
        STYLES.get('SectionTitle')
    ))
    
    contact_text = f"""
    <b>{company_info.get('name', '')}</b><br/>
    {company_info.get('street', '')}<br/>
    {company_info.get('zip_code', '')} {company_info.get('city', '')}<br/>
    """
    
    if company_info.get('phone'):
        contact_text += f"Tel.: {company_info['phone']}<br/>"
    
    if company_info.get('email'):
        contact_text += f"E-Mail: {company_info['email']}<br/>"
    
    elements.append(Paragraph(contact_text, STYLES.get('NormalLeft')))
    
    return elements


def _append_additional_documents(
    main_pdf_bytes: bytes,
    inclusion_options: Dict[str, Any],
    project_data: Dict[str, Any],
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int]
) -> bytes:
    """Fügt zusätzliche Dokumente an das Haupt-PDF an"""
    
    if not _PYPDF_AVAILABLE:
        return main_pdf_bytes
    
    try:
        pdf_writer = PdfWriter()
        
        # Haupt-PDF hinzufügen
        main_reader = PdfReader(BytesIO(main_pdf_bytes))
        for page in main_reader.pages:
            pdf_writer.add_page(page)
        
        # Produktdatenblätter hinzufügen
        if project_data and project_data.get('project_details'):
            details = project_data['project_details']
            product_ids = []
            
            for key in ['selected_module_id', 'selected_inverter_id', 'selected_storage_id']:
                if details.get(key):
                    product_ids.append(details[key])
            
            for product_id in product_ids:
                try:
                    product = get_product_by_id_func(product_id)
                    if product and product.get('datasheet_link_db_path'):
                        datasheet_path = os.path.join(
                            PRODUCT_DATASHEETS_BASE_DIR_PDF_GEN, 
                            product['datasheet_link_db_path']
                        )
                        if os.path.exists(datasheet_path):
                            datasheet_reader = PdfReader(datasheet_path)
                            for page in datasheet_reader.pages:
                                pdf_writer.add_page(page)
                except Exception:
                    pass
        
        # Firmendokumente hinzufügen
        if (inclusion_options.get('company_document_ids_to_include') and 
            active_company_id and callable(db_list_company_documents_func)):
            
            try:
                company_docs = db_list_company_documents_func(active_company_id, None)
                for doc_info in company_docs:
                    if doc_info.get('id') in inclusion_options['company_document_ids_to_include']:
                        if doc_info.get('relative_db_path'):
                            doc_path = os.path.join(
                                COMPANY_DOCS_BASE_DIR_PDF_GEN,
                                doc_info['relative_db_path']
                            )
                            if os.path.exists(doc_path):
                                doc_reader = PdfReader(doc_path)
                                for page in doc_reader.pages:
                                    pdf_writer.add_page(page)
            except Exception:
                pass
        
        # Zusammengebautes PDF zurückgeben
        final_buffer = BytesIO()
        pdf_writer.write(final_buffer)
        final_pdf_bytes = final_buffer.getvalue()
        final_buffer.close()
        
        return final_pdf_bytes
        
    except Exception:
        # Bei Fehlern das Original-PDF zurückgeben
        return main_pdf_bytes


def _validate_pdf_data_availability(
    project_data: Dict[str, Any], 
    analysis_results: Dict[str, Any], 
    texts: Dict[str, str]
) -> Dict[str, Any]:
    """
    Validiert die verfügbaren Daten für die PDF-Erstellung.
    
    Returns:
        Dict mit is_valid, warnings, critical_errors, missing_data_summary
    """
    
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'critical_errors': [],
        'missing_data_summary': []
    }
    
    # Kritische Prüfungen (führen zu is_valid=False)
    if not texts or not isinstance(texts, dict):
        validation_result['critical_errors'].append('Keine Texte verfügbar')
        validation_result['is_valid'] = False
    
    # Warnungen (führen nicht zu is_valid=False)
    if not project_data or not isinstance(project_data, dict):
        validation_result['warnings'].append('Keine Projektdaten verfügbar')
        validation_result['missing_data_summary'].append('Projektdaten')
    else:
        if not project_data.get('customer_data', {}).get('last_name'):
            validation_result['warnings'].append('Kein Kundenname verfügbar')
            validation_result['missing_data_summary'].append('Kundendaten')
        
        if not project_data.get('project_details', {}).get('module_quantity'):
            validation_result['warnings'].append('Keine Modulanzahl verfügbar')
            validation_result['missing_data_summary'].append('Komponentendaten')
    
    if not analysis_results or not isinstance(analysis_results, dict):
        validation_result['warnings'].append('Keine Analyseergebnisse verfügbar')
        validation_result['missing_data_summary'].append('Wirtschaftlichkeitsdaten')
    
    return validation_result


def _create_no_data_fallback_pdf(texts: Dict[str, str], customer_data: Dict[str, Any] = None) -> bytes:
    """
    Erstellt ein Fallback-PDF wenn nicht genügend Daten vorhanden sind.
    
    Args:
        texts: Text-Dictionary
        customer_data: Optionale Kundendaten
        
    Returns:
        PDF-Bytes
    """
    
    if not _REPORTLAB_AVAILABLE:
        # Text-basiertes Fallback
        return b"PDF-Erstellung nicht verfuegbar. ReportLab nicht installiert."
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    # Titel
    title = get_text(texts, 'pdf_no_data_title', 'Photovoltaik-Angebot - Daten unvollständig')
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 1*cm))
    
    # Kundenanrede falls verfügbar
    if customer_data and customer_data.get('last_name'):
        customer_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        customer_text = get_text(texts, 'pdf_no_data_customer', f'Für: {customer_name}')
        story.append(Paragraph(customer_text, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # Haupttext
    main_text = get_text(texts, 'pdf_no_data_message', 
        '''Liebe Kundin, lieber Kunde,

        für die Erstellung Ihres individuellen Photovoltaik-Angebots benötigen wir noch einige wichtige Informationen:

        <b>Erforderliche Daten:</b>
        • Gewünschte PV-Module und Komponenten
        • Technische Angaben zu Ihrem Dach/Standort
        • Verbrauchsdaten für die Wirtschaftlichkeitsberechnung

        <b>Nächste Schritte:</b>
        1. Vervollständigen Sie die Komponentenauswahl
        2. Führen Sie die Wirtschaftlichkeitsberechnung durch
        3. Erstellen Sie das finale Angebot

        Vielen Dank für Ihr Verständnis.''')
    
    story.append(Paragraph(main_text, styles['Normal']))
    story.append(Spacer(1, 1*cm))
    
    # Kontaktinformationen
    contact_text = get_text(texts, 'pdf_no_data_contact', 
        'Kontakt: Bitte wenden Sie sich an unser Beratungsteam für weitere Unterstützung.')
    story.append(Paragraph(contact_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
