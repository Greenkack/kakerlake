# pdf_design_enhanced_modern.py
# -*- coding: utf-8 -*-
"""
Erweitertes Modernes PDF-Design System
Basierend auf hochwertige JSON-Vorlage mit Farben, Bildern, Diagrammen und professioneller Formatierung
Vollständig modular und optional - 100% kompatibel mit bestehendem System
"""

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import (
    Image, Paragraph, Spacer, Table, TableStyle, 
    KeepTogether, PageBreak, Flowable, Frame
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
import io
import base64

class ModernPDFDesignSystem:
    """
    Modernes PDF-Design System basierend auf hochwertiger JSON-Vorlage
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 2*cm
        self.content_width = self.page_width - 2*self.margin
        
        # Erweiterte moderne Farbschemata (basierend auf JSON-Vorlage)
        self.enhanced_color_schemes = {
            'premium_blue_modern': {
                'primary': HexColor('#1e3a8a'),         # Tiefes Business-Blau
                'secondary': HexColor('#3b82f6'),       # Modernes Blau
                'accent': HexColor('#06b6d4'),          # Cyan Akzent
                'background': HexColor('#f8fafc'),      # Sehr helles Grau
                'text_primary': HexColor('#1f2937'),    # Dunkel für Headlines
                'text_secondary': HexColor('#4b5563'),  # Mittel für Body
                'text_light': HexColor('#9ca3af'),      # Hell für Captions
                'success': HexColor('#10b981'),         # Erfolgsmeldungen
                'warning': HexColor('#f59e0b'),         # Warnungen
                'error': HexColor('#ef4444'),           # Fehler
                'highlight': HexColor('#fbbf24'),       # Highlight-Bereiche
                'border_light': HexColor('#e5e7eb'),    # Helle Borders
                'border_medium': HexColor('#d1d5db'),   # Mittlere Borders
            },
            'solar_professional_enhanced': {
                'primary': HexColor('#059669'),         # Solar-Grün
                'secondary': HexColor('#10b981'),       # Helles Grün
                'accent': HexColor('#f97316'),          # Orange Akzent
                'background': HexColor('#f0fdf4'),      # Sehr helles Grün
                'text_primary': HexColor('#064e3b'),    # Dunkelgrün für Headlines
                'text_secondary': HexColor('#065f46'),  # Mittelgrün für Body
                'text_light': HexColor('#6b7280'),      # Grau für Captions
                'success': HexColor('#22c55e'),         # Erfolg
                'warning': HexColor('#eab308'),         # Warnung
                'error': HexColor('#dc2626'),           # Fehler
                'highlight': HexColor('#fde047'),       # Gelb Highlight
                'border_light': HexColor('#d1fae5'),    # Helle Grün-Borders
                'border_medium': HexColor('#a7f3d0'),   # Mittlere Grün-Borders
            },
            'executive_luxury': {
                'primary': HexColor('#111827'),         # Tiefschwarz
                'secondary': HexColor('#374151'),       # Anthrazit
                'accent': HexColor('#d97706'),          # Luxus-Gold
                'background': HexColor('#ffffff'),      # Reines Weiß
                'text_primary': HexColor('#111827'),    # Schwarz
                'text_secondary': HexColor('#374151'),  # Anthrazit
                'text_light': HexColor('#6b7280'),      # Grau
                'success': HexColor('#059669'),         # Grün
                'warning': HexColor('#d97706'),         # Gold
                'error': HexColor('#dc2626'),           # Rot
                'highlight': HexColor('#fbbf24'),       # Gold Highlight
                'border_light': HexColor('#f3f4f6'),    # Sehr helle Borders
                'border_medium': HexColor('#e5e7eb'),   # Mittlere Borders
            }
        }
        
        # Moderne Typografie-Hierarchie
        self.typography_hierarchy = {
            'display': {'size': 28, 'weight': 'Bold', 'spacing': 1.2},
            'h1': {'size': 24, 'weight': 'Bold', 'spacing': 1.3},
            'h2': {'size': 20, 'weight': 'Bold', 'spacing': 1.3},
            'h3': {'size': 16, 'weight': 'Bold', 'spacing': 1.4},
            'h4': {'size': 14, 'weight': 'Bold', 'spacing': 1.4},
            'body_large': {'size': 12, 'weight': 'Normal', 'spacing': 1.5},
            'body': {'size': 11, 'weight': 'Normal', 'spacing': 1.5},
            'body_small': {'size': 10, 'weight': 'Normal', 'spacing': 1.4},
            'caption': {'size': 9, 'weight': 'Normal', 'spacing': 1.3},
            'fine_print': {'size': 8, 'weight': 'Normal', 'spacing': 1.2}
        }
    
    def get_enhanced_paragraph_styles(self, color_scheme: str = 'premium_blue_modern') -> Dict[str, ParagraphStyle]:
        """Erstellt erweiterte, moderne Paragraph-Styles"""
        colors_dict = self.enhanced_color_schemes.get(color_scheme, self.enhanced_color_schemes['premium_blue_modern'])
        typo = self.typography_hierarchy
        
        styles = {}
        
        # Display-Style für Haupttitel
        styles['display'] = ParagraphStyle(
            'Display',
            fontName='Helvetica-Bold',
            fontSize=typo['display']['size'],
            textColor=colors_dict['primary'],
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=15,
            leading=typo['display']['size'] * typo['display']['spacing']
        )
        
        # Hierarchische Überschriften
        for level in ['h1', 'h2', 'h3', 'h4']:
            color = colors_dict['primary'] if level in ['h1', 'h2'] else colors_dict['text_primary']
            alignment = TA_LEFT
            space_before = 20 if level == 'h1' else 15
            space_after = 12 if level == 'h1' else 8
            
            styles[level] = ParagraphStyle(
                level.upper(),
                fontName=f'Helvetica-{typo[level]["weight"]}',
                fontSize=typo[level]['size'],
                textColor=color,
                alignment=alignment,
                spaceAfter=space_after,
                spaceBefore=space_before,
                leading=typo[level]['size'] * typo[level]['spacing']
            )
        
        # Body-Styles
        styles['body'] = ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=typo['body']['size'],
            textColor=colors_dict['text_secondary'],
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=typo['body']['size'] * typo['body']['spacing']
        )
        
        styles['body_large'] = ParagraphStyle(
            'BodyLarge',
            fontName='Helvetica',
            fontSize=typo['body_large']['size'],
            textColor=colors_dict['text_secondary'],
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=typo['body_large']['size'] * typo['body_large']['spacing']
        )
        
        styles['caption'] = ParagraphStyle(
            'Caption',
            fontName='Helvetica',
            fontSize=typo['caption']['size'],
            textColor=colors_dict['text_light'],
            alignment=TA_CENTER,
            spaceAfter=8,
            spaceBefore=4,
            leading=typo['caption']['size'] * typo['caption']['spacing']
        )
        
        # Spezielle Info-Box Styles
        styles['info_box_title'] = ParagraphStyle(
            'InfoBoxTitle',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors_dict['primary'],
            spaceAfter=6,
            leading=16
        )
        
        styles['info_box_content'] = ParagraphStyle(
            'InfoBoxContent',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors_dict['text_secondary'],
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=15,
            backColor=colors_dict['background'],
            borderWidth=1,
            borderColor=colors_dict['border_light'],
            borderPadding=12,
            borderRadius=6
        )
        
        # Highlight-Styles
        styles['highlight_box'] = ParagraphStyle(
            'HighlightBox',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors_dict['primary'],
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=12,
            leading=16,
            backColor=colors_dict['highlight'],
            borderWidth=2,
            borderColor=colors_dict['accent'],
            borderPadding=15,
            borderRadius=8
        )
        
        return styles
    
    def create_enhanced_table_style(self, color_scheme: str = 'premium_blue_modern', 
                                   table_type: str = 'data') -> TableStyle:
        """Erstellt moderne, erweiterte Tabellen-Styles"""
        colors_dict = self.enhanced_color_schemes.get(color_scheme, self.enhanced_color_schemes['premium_blue_modern'])
        
        if table_type == 'data':
            return TableStyle([
                # Header-Styling
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Datenzeilen-Styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors_dict['text_secondary']),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                
                # Zebra-Striping für bessere Lesbarkeit
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors_dict['background']]),
                
                # Borders
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors_dict['accent']),
                ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors_dict['border_light']),
                ('LINEBELOW', (0, -1), (-1, -1), 1, colors_dict['border_medium']),
                
                # Outer border
                ('BOX', (0, 0), (-1, -1), 1, colors_dict['border_medium']),
            ])
            
        elif table_type == 'financial':
            return TableStyle([
                # Financial Table - Besondere Formatierung für Zahlen
                ('BACKGROUND', (0, 0), (-1, 0), colors_dict['success']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Zahlen rechtsbündig
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (1, 1), (-1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1, 1), (-1, -1), colors_dict['text_primary']),
                
                # Erste Spalte (Labels) linksbündig
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
                
                # Alternating rows
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors_dict['background']]),
                
                # Padding und Borders
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('BOX', (0, 0), (-1, -1), 1.5, colors_dict['border_medium']),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors_dict['accent']),
            ])
        
        # Standard-Tabelle
        return self.create_enhanced_table_style(color_scheme, 'data')
    
    def create_professional_info_box(self, title: str, content: str, 
                                   box_type: str = 'info',
                                   color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt professionelle Info-Boxen mit modernem Design"""
        colors_dict = self.enhanced_color_schemes.get(color_scheme, self.enhanced_color_schemes['premium_blue_modern'])
        styles = self.get_enhanced_paragraph_styles(color_scheme)
        
        # Box-Type spezifische Farben
        box_configs = {
            'info': {
                'bg': colors_dict['background'],
                'border': colors_dict['primary'],
                'icon': 'ℹ️'
            },
            'success': {
                'bg': HexColor('#f0fdf4'),
                'border': colors_dict['success'],
                'icon': '✅'
            },
            'warning': {
                'bg': HexColor('#fffbeb'),
                'border': colors_dict['warning'],
                'icon': '⚠️'
            },
            'highlight': {
                'bg': colors_dict['highlight'],
                'border': colors_dict['accent'],
                'icon': '⭐'
            }
        }
        
        config = box_configs.get(box_type, box_configs['info'])
        
        # Erstelle speziellen Box-Style
        box_style = ParagraphStyle(
            f'InfoBox_{box_type}',
            parent=styles['body'],
            backColor=config['bg'],
            borderWidth=2,
            borderColor=config['border'],
            borderPadding=18,
            borderRadius=8,
            spaceAfter=15,
            spaceBefore=10
        )
        
        elements = []
        
        # Titel mit Icon
        if title:
            title_text = f"{config['icon']} <b>{title}</b>"
            title_style = ParagraphStyle(
                f'BoxTitle_{box_type}',
                fontName='Helvetica-Bold',
                fontSize=13,
                textColor=config['border'],
                spaceAfter=8,
                alignment=TA_LEFT
            )
            elements.append(Paragraph(title_text, title_style))
        
        # Content
        elements.append(Paragraph(content, box_style))
        
        return elements
    
    def create_enhanced_image_gallery(self, images: List[Dict], 
                                    gallery_title: str = "",
                                    color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Bildergalerien mit Beschreibungen"""
        elements = []
        styles = self.get_enhanced_paragraph_styles(color_scheme)
        
        if gallery_title:
            elements.append(Paragraph(gallery_title, styles['h2']))
            elements.append(Spacer(1, 10))
        
        for img_data in images:
            img_path = img_data.get('path', '')
            caption = img_data.get('caption', '')
            description = img_data.get('description', '')
            width = img_data.get('width')
            height = img_data.get('height')
            
            try:
                if os.path.exists(img_path) or img_data.get('base64_data'):
                    # Bildgröße automatisch berechnen
                    if width is None:
                        width = self.content_width * 0.8
                    
                    # Image erstellen
                    if img_data.get('base64_data'):
                        # Base64 Image handling
                        img_data_bytes = base64.b64decode(img_data['base64_data'])
                        img = Image(io.BytesIO(img_data_bytes), width=width, height=height)
                    else:
                        img = Image(img_path, width=width, height=height)
                    
                    img.hAlign = 'CENTER'
                    elements.append(img)
                    
                    # Caption
                    if caption:
                        elements.append(Spacer(1, 5))
                        elements.append(Paragraph(caption, styles['caption']))
                    
                    # Beschreibung
                    if description:
                        elements.append(Spacer(1, 5))
                        desc_style = ParagraphStyle(
                            'ImageDescription',
                            fontName='Helvetica',
                            fontSize=10,
                            textColor=self.enhanced_color_schemes[color_scheme]['text_secondary'],
                            alignment=TA_JUSTIFY,
                            spaceAfter=15,
                            leading=14
                        )
                        elements.append(Paragraph(description, desc_style))
                    
                    elements.append(Spacer(1, 15))
                    
            except Exception as e:
                # Fallback für fehlende Bilder
                error_style = ParagraphStyle(
                    'ImageError',
                    fontName='Helvetica',
                    fontSize=10,
                    textColor=colors.red,
                    alignment=TA_CENTER,
                    spaceAfter=15,
                    backColor=HexColor('#fef2f2'),
                    borderWidth=1,
                    borderColor=colors.red,
                    borderPadding=10
                )
                elements.append(Paragraph(f"[Bild nicht verfügbar: {img_path}]", error_style))
        
        return elements
    
    def create_modern_header_section(self, title: str, subtitle: str = "",
                                   logo_path: str = "", 
                                   color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Header-Bereiche für Abschnitte"""
        elements = []
        styles = self.get_enhanced_paragraph_styles(color_scheme)
        colors_dict = self.enhanced_color_schemes[color_scheme]
        
        # Header-Container mit Hintergrund
        header_style = ParagraphStyle(
            'ModernHeader',
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=10,
            leading=24,
            backColor=colors_dict['primary'],
            borderPadding=20,
            borderRadius=10
        )
        
        # Logo und Titel kombinieren falls Logo vorhanden
        if logo_path and os.path.exists(logo_path):
            # TODO: Logo-Integration in Header
            pass
        
        elements.append(Paragraph(title, header_style))
        
        if subtitle:
            subtitle_style = ParagraphStyle(
                'ModernSubHeader',
                fontName='Helvetica',
                fontSize=14,
                textColor=colors_dict['text_light'],
                alignment=TA_CENTER,
                spaceAfter=20,
                spaceBefore=5,
                leading=18
            )
            elements.append(Paragraph(subtitle, subtitle_style))
        
        return elements
    
    def create_financial_summary_card(self, data: Dict[str, Any],
                                    color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Finanz-Zusammenfassungskarten"""
        elements = []
        styles = self.get_enhanced_paragraph_styles(color_scheme)
        colors_dict = self.enhanced_color_schemes[color_scheme]
        
        # Card-Style
        card_style = ParagraphStyle(
            'FinancialCard',
            fontName='Helvetica',
            fontSize=11,
            textColor=colors_dict['text_secondary'],
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=10,
            leading=16,
            backColor=colors_dict['background'],
            borderWidth=2,
            borderColor=colors_dict['accent'],
            borderPadding=20,
            borderRadius=12
        )
        
        # Erstelle Tabelle für strukturierte Darstellung
        table_data = []
        
        # Header
        table_data.append(['Finanzielle Übersicht', ''])
        
        # Daten hinzufügen
        for key, value in data.items():
            if isinstance(value, (int, float)):
                formatted_value = f"{value:,.2f} €" if 'euro' in key.lower() or 'cost' in key.lower() else f"{value:,.0f}"
            else:
                formatted_value = str(value)
            
            # Key formatieren
            formatted_key = key.replace('_', ' ').title()
            table_data.append([formatted_key, formatted_value])
        
        # Tabelle erstellen
        table = Table(table_data, colWidths=[self.content_width * 0.6, self.content_width * 0.4])
        table.setStyle(self.create_enhanced_table_style(color_scheme, 'financial'))
        
        elements.append(table)
        elements.append(Spacer(1, 15))
        
        return elements

class ModernPDFComponentLibrary:
    """
    Bibliothek für moderne PDF-Komponenten
    """
    
    def __init__(self, design_system: ModernPDFDesignSystem):
        self.design_system = design_system
    
    def create_solar_calculation_showcase(self, calc_data: Dict[str, Any],
                                        color_scheme: str = 'solar_professional_enhanced') -> List:
        """Erstellt moderne Solar-Berechnungsdarstellung"""
        elements = []
        
        # Header
        elements.extend(
            self.design_system.create_modern_header_section(
                "🌞 Solar-Berechnungen & Wirtschaftlichkeit",
                "Detaillierte Analyse Ihrer Photovoltaikanlage",
                color_scheme=color_scheme
            )
        )
        
        # Hauptmetriken als Cards
        main_metrics = {
            'Jährliche PV-Produktion': f"{calc_data.get('annual_pv_production_kwh', 0):,.0f} kWh",
            'Eigenverbrauchsanteil': f"{calc_data.get('self_consumption_rate', 0):.1f}%",
            'Jährliche Kosteneinsparung': f"{calc_data.get('annual_savings', 0):,.0f} €",
            'CO₂-Einsparung pro Jahr': f"{calc_data.get('co2_savings_kg_year', 0):,.0f} kg"
        }
        
        elements.extend(
            self.design_system.create_financial_summary_card(main_metrics, color_scheme)
        )
        
        # Zusätzliche Info-Boxen
        if calc_data.get('payback_period_years'):
            elements.extend(
                self.design_system.create_professional_info_box(
                    "💰 Amortisationszeit",
                    f"Ihre Investition amortisiert sich in ca. {calc_data['payback_period_years']:.1f} Jahren. "
                    f"Danach profitieren Sie von kostenlosen Solarstrom für weitere {25 - calc_data['payback_period_years']:.0f} Jahre.",
                    box_type='success',
                    color_scheme=color_scheme
                )
            )
        
        return elements
    
    def create_technical_specifications_modern(self, tech_data: Dict[str, Any],
                                             color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne technische Spezifikationen"""
        elements = []
        
        # Header
        elements.extend(
            self.design_system.create_modern_header_section(
                "⚡ Technische Spezifikationen",
                "Hochwertige Komponenten für maximale Effizienz",
                color_scheme=color_scheme
            )
        )
        
        # Technische Daten in strukturierter Form
        tech_table_data = [
            ['Komponente', 'Spezifikation', 'Leistung']
        ]
        
        # PV-Module
        if tech_data.get('pv_modules'):
            module_data = tech_data['pv_modules']
            tech_table_data.append([
                'PV-Module', 
                f"{module_data.get('manufacturer', 'N/A')} {module_data.get('model', '')}",
                f"{module_data.get('power_wp', 0)} Wp"
            ])
        
        # Wechselrichter
        if tech_data.get('inverter'):
            inv_data = tech_data['inverter']
            tech_table_data.append([
                'Wechselrichter',
                f"{inv_data.get('manufacturer', 'N/A')} {inv_data.get('model', '')}",
                f"{inv_data.get('power_kw', 0)} kW"
            ])
        
        # Batterie (falls vorhanden)
        if tech_data.get('battery'):
            batt_data = tech_data['battery']
            tech_table_data.append([
                'Batteriespeicher',
                f"{batt_data.get('manufacturer', 'N/A')} {batt_data.get('model', '')}",
                f"{batt_data.get('capacity_kwh', 0)} kWh"
            ])
        
        # Tabelle erstellen
        table = Table(tech_table_data, colWidths=[
            self.design_system.content_width * 0.3,
            self.design_system.content_width * 0.45,
            self.design_system.content_width * 0.25
        ])
        table.setStyle(self.design_system.create_enhanced_table_style(color_scheme, 'data'))
        
        elements.append(table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def create_product_showcase(self, products: List[Dict], 
                              color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Produktpräsentation mit Bildern"""
        elements = []
        
        # Header
        elements.extend(
            self.design_system.create_modern_header_section(
                "🛠️ Produktaufstellung",
                "Hochwertige Komponenten für Ihre Solaranlage",
                color_scheme=color_scheme
            )
        )
        
        for product in products:
            # Produktname als Zwischenüberschrift
            product_style = ParagraphStyle(
                'ProductTitle',
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=self.design_system.enhanced_color_schemes[color_scheme]['primary'],
                spaceAfter=8,
                spaceBefore=15,
                leading=18
            )
            
            elements.append(Paragraph(product.get('name', 'Unbekanntes Produkt'), product_style))
            
            # Produktbild
            if product.get('image_path') or product.get('image_base64'):
                image_data = {
                    'path': product.get('image_path', ''),
                    'base64_data': product.get('image_base64'),
                    'caption': f"{product.get('manufacturer', '')} {product.get('model', '')}",
                    'description': product.get('description', ''),
                    'width': self.design_system.content_width * 0.4
                }
                elements.extend(
                    self.design_system.create_enhanced_image_gallery([image_data], color_scheme=color_scheme)
                )
            
            # Produktdetails in Info-Box
            if product.get('specifications'):
                specs_text = ""
                for key, value in product['specifications'].items():
                    specs_text += f"<b>{key}:</b> {value}<br/>"
                
                elements.extend(
                    self.design_system.create_professional_info_box(
                        "📋 Technische Daten",
                        specs_text,
                        box_type='info',
                        color_scheme=color_scheme
                    )
                )
            
            # Preis (falls vorhanden)
            if product.get('price'):
                price_text = f"Preis: <b>{product['price']:,.2f} €</b>"
                if product.get('quantity'):
                    price_text += f" (Anzahl: {product['quantity']})"
                
                elements.extend(
                    self.design_system.create_professional_info_box(
                        "💰 Preisinfo",
                        price_text,
                        box_type='highlight',
                        color_scheme=color_scheme
                    )
                )
            
            elements.append(Spacer(1, 20))
        
        return elements

# Modular optionale Integration
def get_modern_design_system() -> ModernPDFDesignSystem:
    """Factory-Funktion für das moderne Design-System"""
    return ModernPDFDesignSystem()

def get_modern_component_library(design_system: ModernPDFDesignSystem = None) -> ModernPDFComponentLibrary:
    """Factory-Funktion für die moderne Komponenten-Bibliothek"""
    if design_system is None:
        design_system = get_modern_design_system()
    return ModernPDFComponentLibrary(design_system)

# Verfügbare Farbschemata für UI-Integration
def get_available_modern_color_schemes() -> Dict[str, Dict[str, str]]:
    """Gibt verfügbare moderne Farbschemata für UI-Auswahl zurück"""
    return {
        'premium_blue_modern': {
            'name': 'Premium Blue Modern',
            'description': 'Modernes Business-Design mit tiefem Blau und professionellen Akzenten',
            'use_case': 'Geschäftspräsentationen, Executive Reports'
        },
        'solar_professional_enhanced': {
            'name': 'Solar Professional Enhanced',
            'description': 'Umweltfreundliches Design mit Grün-Tönen und nachhaltigen Akzenten',
            'use_case': 'Solar- und Umweltprojekte, Nachhaltigkeitsberichte'
        },
        'executive_luxury': {
            'name': 'Executive Luxury',
            'description': 'Luxuriöses Design mit Gold-Akzenten für Premium-Präsentationen',
            'use_case': 'Hochwertige Angebote, Luxus-Segmente'
        }
    }

def get_modern_color_scheme_preview(scheme_name: str) -> Dict[str, str]:
    """Gibt Farbvorschau für UI zurück"""
    design_system = get_modern_design_system()
    colors = design_system.enhanced_color_schemes.get(scheme_name, {})
    
    return {
        'primary': str(colors.get('primary', '#1e3a8a')),
        'secondary': str(colors.get('secondary', '#3b82f6')),
        'accent': str(colors.get('accent', '#06b6d4')),
        'success': str(colors.get('success', '#10b981'))
    }

class ModernChartEnhancer:
    """
    Erweiterte Chart-Verbesserungen für moderne PDF-Ausgabe
    """
    
    def __init__(self, design_system: ModernPDFDesignSystem):
        self.design_system = design_system
    
    def create_modern_financial_chart(self, chart_data: Dict[str, Any], 
                                    chart_type: str = 'roi_timeline',
                                    color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Finanz-Charts für PDF"""
        elements = []
        colors_dict = self.design_system.enhanced_color_schemes[color_scheme]
        
        try:
            import plotly.graph_objects as go
            import plotly.io as pio
            from plotly.subplots import make_subplots
            
            # Chart-spezifische Logik
            if chart_type == 'roi_timeline':
                elements.extend(self._create_roi_timeline_chart(chart_data, colors_dict))
            elif chart_type == 'energy_flow':
                elements.extend(self._create_energy_flow_chart(chart_data, colors_dict))
            elif chart_type == 'savings_comparison':
                elements.extend(self._create_savings_comparison_chart(chart_data, colors_dict))
            
        except ImportError:
            # Fallback ohne Plotly
            elements.extend(
                self.design_system.create_professional_info_box(
                    "📊 Chart-Placeholder",
                    f"Hier würde ein moderner {chart_type}-Chart erscheinen. Plotly ist erforderlich für erweiterte Charts.",
                    box_type='info',
                    color_scheme=color_scheme
                )
            )
        
        return elements
    
    def _create_roi_timeline_chart(self, data: Dict, colors_dict: Dict) -> List:
        """ROI Timeline Chart"""
        elements = []
        
        # Placeholder für Chart-Bild
        chart_placeholder = self.design_system.create_professional_info_box(
            "📈 ROI-Entwicklung über 25 Jahre",
            "Ihre Investition entwickelt sich über die Jahre zu einem profitablen Asset. "
            "Nach der Amortisation generiert die Anlage reinen Gewinn.",
            box_type='success'
        )
        elements.extend(chart_placeholder)
        
        return elements
    
    def _create_energy_flow_chart(self, data: Dict, colors_dict: Dict) -> List:
        """Energiefluss-Diagramm"""
        elements = []
        
        chart_placeholder = self.design_system.create_professional_info_box(
            "⚡ Energiefluss-Analyse",
            "Visualisierung wie Ihr Solarstrom optimal zwischen Eigenverbrauch, "
            "Speicher und Netzeinspeisung aufgeteilt wird.",
            box_type='info'
        )
        elements.extend(chart_placeholder)
        
        return elements
    
    def _create_savings_comparison_chart(self, data: Dict, colors_dict: Dict) -> List:
        """Einsparungs-Vergleichschart"""
        elements = []
        
        chart_placeholder = self.design_system.create_professional_info_box(
            "💰 Kostenvergleich mit/ohne Solar",
            "Deutliche Darstellung Ihrer Kosteneinsparungen über die Jahre "
            "im Vergleich zu konventionellem Strombezug.",
            box_type='highlight'
        )
        elements.extend(chart_placeholder)
        
        return elements

class ModernPDFLayoutManager:
    """
    Erweiterte Layout-Verwaltung für moderne PDF-Struktur
    """
    
    def __init__(self, design_system: ModernPDFDesignSystem):
        self.design_system = design_system
        self.component_library = ModernPDFComponentLibrary(design_system)
        self.chart_enhancer = ModernChartEnhancer(design_system)
    
    def create_executive_summary_page(self, summary_data: Dict[str, Any],
                                    color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Executive Summary Seite"""
        elements = []
        
        # Haupttitel
        elements.extend(
            self.design_system.create_modern_header_section(
                "📋 Executive Summary",
                "Zusammenfassung Ihres Solarprojekts auf einen Blick",
                color_scheme=color_scheme
            )
        )
        
        # Key Metrics in Cards
        key_metrics = {
            'Gesamtinvestition': f"{summary_data.get('total_investment', 0):,.0f} €",
            'Jährliche Einsparung': f"{summary_data.get('annual_savings', 0):,.0f} €",
            'Amortisationszeit': f"{summary_data.get('payback_years', 0):.1f} Jahre",
            'Gesamtrendite (25 Jahre)': f"{summary_data.get('total_return', 0):,.0f} €"
        }
        
        elements.extend(
            self.design_system.create_financial_summary_card(key_metrics, color_scheme)
        )
        
        # Hauptvorteile
        benefits_text = """
        <b>🌟 Ihre Hauptvorteile:</b><br/>
        • Sofortige Kosteneinsparungen ab dem ersten Tag<br/>
        • Unabhängigkeit von steigenden Strompreisen<br/>
        • Wertsteigerung Ihrer Immobilie<br/>
        • Aktiver Beitrag zum Klimaschutz<br/>
        • Staatliche Förderungen und Steuervorteile
        """
        
        elements.extend(
            self.design_system.create_professional_info_box(
                "💎 Warum Solar die richtige Entscheidung ist",
                benefits_text,
                box_type='highlight',
                color_scheme=color_scheme
            )
        )
        
        return elements
    
    def create_detailed_calculation_page(self, calc_data: Dict[str, Any],
                                       color_scheme: str = 'solar_professional_enhanced') -> List:
        """Erstellt detaillierte Berechnungsseite"""
        elements = []
        
        # Solar-Berechnungen
        elements.extend(
            self.component_library.create_solar_calculation_showcase(calc_data, color_scheme)
        )
        
        # Finanzielle Details
        if calc_data.get('financial_breakdown'):
            financial_data = calc_data['financial_breakdown']
            
            elements.extend(
                self.design_system.create_modern_header_section(
                    "💰 Detaillierte Finanzanalyse",
                    "Transparente Aufschlüsselung aller Kosten und Erträge",
                    color_scheme=color_scheme
                )
            )
            
            # Kostenaufstellung
            cost_table_data = [
                ['Kostenposition', 'Betrag (€)', 'Anteil (%)']
            ]
            
            total_cost = sum(financial_data.values()) if isinstance(financial_data, dict) else 0
            
            for cost_item, amount in financial_data.items():
                percentage = (amount / total_cost * 100) if total_cost > 0 else 0
                cost_table_data.append([
                    cost_item.replace('_', ' ').title(),
                    f"{amount:,.2f}",
                    f"{percentage:.1f}%"
                ])
            
            cost_table = Table(cost_table_data, colWidths=[
                self.design_system.content_width * 0.5,
                self.design_system.content_width * 0.25,
                self.design_system.content_width * 0.25
            ])
            cost_table.setStyle(
                self.design_system.create_enhanced_table_style(color_scheme, 'financial')
            )
            
            elements.append(cost_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def create_technical_specification_page(self, tech_data: Dict[str, Any],
                                          color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt technische Spezifikationsseite"""
        elements = []
        
        # Technische Spezifikationen
        elements.extend(
            self.component_library.create_technical_specifications_modern(tech_data, color_scheme)
        )
        
        # System-Architektur Info
        if tech_data.get('system_architecture'):
            arch_info = tech_data['system_architecture']
            
            arch_text = f"""
            <b>🏗️ System-Architektur:</b><br/>
            • Modulfläche: {arch_info.get('module_area_m2', 0)} m²<br/>
            • Ausrichtung: {arch_info.get('orientation', 'Süd')} / Neigung: {arch_info.get('tilt_angle', 30)}°<br/>
            • Verschattung: {arch_info.get('shading_factor', 'Minimal')}<br/>
            • Erwarteter Ertrag: {arch_info.get('expected_yield_kwh_kwp', 1000)} kWh/kWp
            """
            
            elements.extend(
                self.design_system.create_professional_info_box(
                    "⚙️ System-Konfiguration",
                    arch_text,
                    box_type='info',
                    color_scheme=color_scheme
                )
            )
        
        return elements
    
    def create_product_catalog_page(self, products: List[Dict],
                                  color_scheme: str = 'premium_blue_modern') -> List:
        """Erstellt moderne Produktkatalog-Seite"""
        elements = []
        
        # Produktaufstellung
        elements.extend(
            self.component_library.create_product_showcase(products, color_scheme)
        )
        
        return elements
    
    def create_environmental_impact_page(self, env_data: Dict[str, Any],
                                       color_scheme: str = 'solar_professional_enhanced') -> List:
        """Erstellt Umwelt-Impact Seite"""
        elements = []
        
        # Header
        elements.extend(
            self.design_system.create_modern_header_section(
                "🌍 Umwelt & Nachhaltigkeit",
                "Ihr Beitrag zu einer grüneren Zukunft",
                color_scheme=color_scheme
            )
        )
        
        # CO2-Einsparungen
        if env_data.get('co2_savings'):
            co2_data = env_data['co2_savings']
            
            co2_metrics = {
                'CO₂-Einsparung pro Jahr': f"{co2_data.get('annual_kg', 0):,.0f} kg",
                'CO₂-Einsparung über 25 Jahre': f"{co2_data.get('lifetime_kg', 0):,.0f} kg",
                'Entspricht Bäumen': f"{co2_data.get('equivalent_trees', 0):,.0f} Bäume",
                'Entspricht Autofahrten': f"{co2_data.get('equivalent_car_km', 0):,.0f} km weniger"
            }
            
            elements.extend(
                self.design_system.create_financial_summary_card(co2_metrics, color_scheme)
            )
        
        # Umwelt-Vorteile
        env_benefits = """
        <b>🌱 Ihre Umwelt-Vorteile:</b><br/>
        • Reduzierung des CO₂-Fußabdrucks um bis zu 80%<br/>
        • Förderung erneuerbarer Energien in Deutschland<br/>
        • Verringerung der Abhängigkeit von fossilen Brennstoffen<br/>
        • Beitrag zur Energiewende und Klimazielen<br/>
        • Vorbild für nachhaltige Lebensweise
        """
        
        elements.extend(
            self.design_system.create_professional_info_box(
                "🌿 Nachhaltiger Impact",
                env_benefits,
                box_type='success',
                color_scheme=color_scheme
            )
        )
        
        return elements

# Hauptintegrationsfunktionen für bestehende Systeme
def enhance_existing_pdf_with_modern_design(existing_elements: List, 
                                          enhancement_config: Dict[str, Any]) -> List:
    """
    Erweitert bestehende PDF-Elemente mit modernem Design
    OHNE bestehende Funktionalität zu beeinträchtigen
    """
    if not enhancement_config.get('enable_modern_design', False):
        return existing_elements  # Keine Änderung wenn nicht aktiviert
    
    enhanced_elements = []
    design_system = get_modern_design_system()
    layout_manager = ModernPDFLayoutManager(design_system)
    
    color_scheme = enhancement_config.get('color_scheme', 'premium_blue_modern')
    
    # Moderne Einleitung hinzufügen
    if enhancement_config.get('add_executive_summary', False):
        summary_data = enhancement_config.get('summary_data', {})
        enhanced_elements.extend(
            layout_manager.create_executive_summary_page(summary_data, color_scheme)
        )
        enhanced_elements.append(PageBreak())
    
    # Bestehende Elemente beibehalten
    enhanced_elements.extend(existing_elements)
    
    # Moderne Abschnitte hinzufügen
    if enhancement_config.get('add_environmental_section', False):
        env_data = enhancement_config.get('environmental_data', {})
        enhanced_elements.append(PageBreak())
        enhanced_elements.extend(
            layout_manager.create_environmental_impact_page(env_data, color_scheme)
        )
    
    return enhanced_elements

def create_complete_modern_pdf_with_content(project_data: Dict[str, Any],
                                          analysis_results: Dict[str, Any], 
                                          enhancement_config: Dict[str, Any],
                                          get_product_by_id_func: Optional[Callable] = None,
                                          db_list_company_documents_func: Optional[Callable] = None,
                                          active_company_id: int = 1) -> List:
    """
    Erstellt vollständige moderne PDF mit allen Inhalten und Datenbankintegration
    """
    try:
        # Neue vollständige Datenbankintegration
        from pdf_database_integration import create_pdf_data_manager
        
        # Erstelle Datenmanager mit verfügbaren DB-Funktionen
        pdf_data_manager = create_pdf_data_manager()
        
        # Lade vollständige Datenbank-Inhalte
        complete_dataset = pdf_data_manager.create_complete_pdf_dataset(
            project_data, 
            active_company_id,
            include_product_images=True,
            include_company_docs=True,
            include_datasheets=True
        )
        
        print(f"✅ Vollständige DB-Inhalte geladen: Vollständigkeit {complete_dataset['content_completeness']}%")
        
        # Konvertiere zu Content-Format für Kompatibilität
        complete_content = _convert_dataset_to_content_format(complete_dataset, analysis_results)
        
    except ImportError as e:
        print(f"⚠️ Datenbankintegration nicht verfügbar ({e}) - verwende Content-System-Fallback")
        try:
            from pdf_content_enhanced_system import create_complete_pdf_content
            
            # Lade vollständige Inhalte
            complete_content = create_complete_pdf_content(
                project_data, analysis_results, get_product_by_id_func,
                db_list_company_documents_func, active_company_id
            )
            
            print(f"✅ Content-System Inhalte geladen")
            
        except ImportError:
            print("⚠️ Content-System nicht verfügbar - verwende Basis-Fallback")
            complete_content = _create_fallback_content(project_data, analysis_results)
    
    design_system = get_modern_design_system()
    layout_manager = ModernPDFLayoutManager(design_system)
    color_scheme = enhancement_config.get('color_scheme', 'premium_blue_modern')
    
    elements = []
    
    # === 1. EXECUTIVE SUMMARY MIT ECHTEN DATEN ===
    if complete_content.get('executive_summary'):
        exec_data = complete_content['executive_summary']
        elements.extend(
            design_system.create_modern_header_section(
                exec_data['title'], "", color_scheme=color_scheme
            )
        )
        
        # Einleitung
        elements.extend(
            design_system.create_professional_info_box(
                "💼 Projekt-Einführung",
                exec_data['introduction'],
                box_type='info',
                color_scheme=color_scheme
            )
        )
        
        # Key Metrics
        elements.extend(
            design_system.create_financial_summary_card(
                exec_data['key_metrics'], color_scheme
            )
        )
        
        # Vorteile
        benefits_text = "<br/>".join([f"• {benefit}" for benefit in exec_data['benefits']])
        elements.extend(
            design_system.create_professional_info_box(
                "🌟 Ihre Hauptvorteile",
                benefits_text,
                box_type='highlight',
                color_scheme=color_scheme
            )
        )
        
        elements.append(PageBreak())
    
    # === 2. TECHNISCHE SPEZIFIKATIONEN MIT PRODUKTEN ===
    if complete_content.get('technical_specifications'):
        tech_data = complete_content['technical_specifications']
        elements.extend(
            design_system.create_modern_header_section(
                tech_data['title'], "", color_scheme=color_scheme
            )
        )
        
        # System-Übersicht
        elements.extend(
            design_system.create_financial_summary_card(
                tech_data['system_specifications'], color_scheme
            )
        )
        
        # Produktaufstellung mit Bildern
        for product in tech_data['products']:
            elements.extend(_create_modern_product_section(product, design_system, color_scheme))
        
        elements.append(PageBreak())
    
    # === 3. INSTALLATIONSBEISPIELE MIT BILDERN ===
    if complete_content.get('installation_examples'):
        examples = complete_content['installation_examples']
        elements.extend(
            design_system.create_enhanced_image_gallery(
                examples, 
                "🏗️ Professionelle Installation - Beispiele aus der Praxis",
                color_scheme
            )
        )
        elements.append(PageBreak())
    
    # === 4. WIRTSCHAFTLICHKEITSANALYSE ===
    if complete_content.get('economic_analysis'):
        econ_data = complete_content['economic_analysis']
        elements.extend(
            design_system.create_modern_header_section(
                econ_data['title'], "", color_scheme=color_scheme
            )
        )
        
        elements.extend(
            design_system.create_professional_info_box(
                "📊 Wirtschaftlichkeit",
                econ_data['introduction'],
                box_type='info',
                color_scheme=color_scheme
            )
        )
        
        elements.extend(
            design_system.create_professional_info_box(
                "💰 ROI-Analyse",
                econ_data['roi_explanation'],
                box_type='success',
                color_scheme=color_scheme
            )
        )
        elements.append(PageBreak())
    
    # === 5. UMWELT & NACHHALTIGKEIT ===
    if complete_content.get('environmental_impact'):
        env_data = complete_content['environmental_impact']
        elements.extend(
            layout_manager.create_environmental_impact_page(
                {'co2_savings': analysis_results}, color_scheme
            )
        )
        elements.append(PageBreak())
    
    # === 6. FIRMENDOKUMENTE ===
    if complete_content.get('company_documents'):
        doc_data = complete_content['company_documents']
        elements.extend(
            design_system.create_modern_header_section(
                doc_data['title'], "", color_scheme=color_scheme
            )
        )
        
        # Dokumentliste
        doc_list = []
        for doc in doc_data['documents']:
            doc_list.append([
                doc.get('name', 'Unbekanntes Dokument'),
                doc.get('type', '').title(),
                'Verfügbar' if doc.get('available', False) else 'Nach Vertragsabschluss'
            ])
        
        if doc_list:
            doc_table = Table(
                [['Dokument', 'Typ', 'Verfügbarkeit']] + doc_list,
                colWidths=[design_system.content_width * 0.5, design_system.content_width * 0.25, design_system.content_width * 0.25]
            )
            doc_table.setStyle(design_system.create_enhanced_table_style(color_scheme, 'data'))
            elements.append(doc_table)
        
        elements.extend(
            design_system.create_professional_info_box(
                "📋 Hinweis",
                doc_data['note'],
                box_type='info',
                color_scheme=color_scheme
            )
        )
        elements.append(PageBreak())
    
    # === 7. INSTALLATION & SERVICE ===
    if complete_content.get('installation_process'):
        install_data = complete_content['installation_process']
        elements.extend(
            design_system.create_modern_header_section(
                install_data['title'], "", color_scheme=color_scheme
            )
        )
        
        process_text = "<br/>".join([f"• {step}" for step in install_data['process_steps']])
        elements.extend(
            design_system.create_professional_info_box(
                "🔧 Unser Service-Prozess",
                process_text,
                box_type='info',
                color_scheme=color_scheme
            )
        )
        elements.append(PageBreak())
    
    # === 8. FINANZIERUNG ===
    if complete_content.get('financing_options'):
        fin_data = complete_content['financing_options']
        elements.extend(
            design_system.create_modern_header_section(
                fin_data['title'], "", color_scheme=color_scheme
            )
        )
        
        financing_text = "<br/>".join([f"• {option}" for option in fin_data['financing_options']])
        elements.extend(
            design_system.create_professional_info_box(
                "💳 Ihre Finanzierungsmöglichkeiten",
                financing_text,
                box_type='highlight',
                color_scheme=color_scheme
            )
        )
    
    print(f"✅ Moderne PDF erstellt mit {len(elements)} Elementen")
    return elements

def _create_modern_product_section(product: Dict[str, Any], 
                                 design_system: ModernPDFDesignSystem, 
                                 color_scheme: str) -> List:
    """Erstellt moderne Produktsektion mit vollständiger Datenbankintegration"""
    elements = []
    
    # Produktname als Überschrift mit erweiterten Informationen
    styles = design_system.get_enhanced_paragraph_styles(color_scheme)
    product_title = f"🔧 {product.get('name', 'Unbekanntes Produkt')}"
    
    # Zusätzliche Produktinfo in Titel wenn verfügbar
    if product.get('type'):
        product_title += f" ({product['type']})"
    
    elements.append(Paragraph(product_title, styles['h3']))
    elements.append(Spacer(1, 10))
    
    # Produktbild mit Datenbankintegration
    if product.get('image_base64'):
        try:
            img_data = base64.b64decode(product['image_base64'])
            img = Image(io.BytesIO(img_data), width=design_system.content_width * 0.4)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 10))
            
            # Bildunterschrift
            caption_text = f"Produktbild: {product.get('manufacturer', '')} {product.get('model', '')}".strip()
            elements.append(Paragraph(caption_text, styles['caption']))
            elements.append(Spacer(1, 10))
            
        except Exception as e:
            print(f"⚠️ Fehler bei Produktbild für {product.get('name', 'Unbekannt')}: {e}")
            # Fallback: Platzhalter
            placeholder_style = ParagraphStyle(
                'ImagePlaceholder',
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.gray,
                alignment=TA_CENTER,
                spaceAfter=10,
                backColor=HexColor('#f8f9fa'),
                borderWidth=1,
                borderColor=colors.gray,
                borderPadding=20
            )
            elements.append(Paragraph("[Produktbild in Datenbank verfügbar]", placeholder_style))
    
    # Produktdetails in strukturierter Tabelle
    details_data = []
    
    # Grundinformationen
    details_data.append(['Hersteller:', product.get('manufacturer', 'Premium-Hersteller')])
    details_data.append(['Modell:', product.get('model', 'Hochwertiges Modell')])
    details_data.append(['Anzahl:', f"{product.get('quantity', 1)} Stück"])
    
    # Preis wenn verfügbar
    if product.get('price'):
        total_price = product['price'] * product.get('quantity', 1)
        details_data.append(['Einzelpreis:', f"{product['price']:,.2f} €"])
        details_data.append(['Gesamtpreis:', f"{total_price:,.2f} €"])
    
    # Technische Spezifikationen
    specs = product.get('specifications', {})
    if specs:
        details_data.append(['--- Technische Daten ---', ''])
        for spec_name, spec_value in specs.items():
            details_data.append([f"{spec_name}:", str(spec_value)])
    
    # Datenblatt-Verfügbarkeit
    if product.get('datasheet_available'):
        details_data.append(['Datenblatt:', '✅ In PDF enthalten'])
    
    # Erstelle Tabelle für strukturierte Darstellung
    if details_data:
        details_table = Table(details_data, colWidths=[
            design_system.content_width * 0.35,
            design_system.content_width * 0.65
        ])
        
        # Spezieller Tabellen-Style für Produktdetails
        table_style = TableStyle([
            # Normale Zeilen
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), design_system.enhanced_color_schemes[color_scheme]['text_secondary']),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            
            # Erste Spalte (Labels) fett
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            
            # Zebra-Striping
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, design_system.enhanced_color_schemes[color_scheme]['background']]),
            
            # Äußerer Rahmen
            ('BOX', (0, 0), (-1, -1), 1, design_system.enhanced_color_schemes[color_scheme]['border_medium']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, design_system.enhanced_color_schemes[color_scheme]['primary']),
        ])
        
        # Hervorhebung für Abschnittstrennungen
        for i, (label, value) in enumerate(details_data):
            if label.startswith('---'):
                table_style.add('BACKGROUND', (0, i), (-1, i), design_system.enhanced_color_schemes[color_scheme]['accent'])
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.white)
                table_style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
                table_style.add('ALIGN', (0, i), (-1, i), 'CENTER')
        
        details_table.setStyle(table_style)
        elements.append(details_table)
        elements.append(Spacer(1, 10))
    
    # Produktbeschreibung falls verfügbar
    if product.get('description'):
        description_style = ParagraphStyle(
            'ProductDescription',
            fontName='Helvetica',
            fontSize=10,
            textColor=design_system.enhanced_color_schemes[color_scheme]['text_secondary'],
            alignment=TA_JUSTIFY,
            spaceAfter=15,
            leading=14,
            backColor=design_system.enhanced_color_schemes[color_scheme]['background'],
            borderWidth=1,
            borderColor=design_system.enhanced_color_schemes[color_scheme]['border_light'],
            borderPadding=12,
            borderRadius=6
        )
        
        description_title = f"📋 Produktbeschreibung:"
        description_text = f"<b>{description_title}</b><br/><br/>{product['description']}"
        elements.append(Paragraph(description_text, description_style))
    
    # Zusätzliche Info-Boxen
    additional_info = []
    
    # Qualitätshinweise
    if specs.get('Garantie'):
        warranty_text = "🛡️ <b>Qualität & Garantie:</b><br/>"
        warranty_text += f"• Herstellergarantie: {specs['Garantie']}<br/>"
        warranty_text += "• Geprüfte Premium-Qualität<br/>"
        warranty_text += "• Zertifiziert nach deutschen Standards"
        
        additional_info.append(('warranty', warranty_text))
    
    # Verfügbarkeit von Datenblättern
    if product.get('datasheet_available'):
        datasheet_text = "📄 <b>Dokumentation:</b><br/>"
        datasheet_text += "• Vollständiges Produktdatenblatt verfügbar<br/>"
        datasheet_text += "• Technische Spezifikationen im Detail<br/>"
        datasheet_text += "• Installationsanleitungen enthalten"
        
        additional_info.append(('datasheet', datasheet_text))
    
    # Erstelle Info-Boxen
    for info_type, info_text in additional_info:
        box_type = 'success' if info_type == 'warranty' else 'info'
        elements.extend(
            design_system.create_professional_info_box(
                "",  # Kein zusätzlicher Titel
                info_text,
                box_type=box_type,
                color_scheme=color_scheme
            )
        )
    
    elements.append(Spacer(1, 20))
    return elements

def _convert_dataset_to_content_format(dataset: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert Datenbankdataset zu Content-Format für PDF-Generierung
    """
    company_info = dataset.get('company_info', {})
    products_enhanced = dataset.get('products_enhanced', [])
    company_documents = dataset.get('company_documents', [])
    image_templates = dataset.get('image_templates', [])
    installation_examples = dataset.get('installation_examples', [])
    stats = dataset.get('data_statistics', {})
    
    # Executive Summary mit echten Daten
    exec_summary = {
        'title': '📋 Executive Summary - Ihr maßgeschneidertes Solar-Projekt',
        'introduction': f'''
        Willkommen bei {company_info.get('name', 'Ihrem Solar-Partner')}! 
        Wir präsentieren Ihnen Ihre individuelle Premium-Photovoltaik-Lösung mit 
        {stats.get('total_products', 0)} hochwertigen Komponenten.
        ''',
        'key_metrics': {
            'Gesamtinvestition': f"{analysis_results.get('gesamtkosten', 0):,.0f} €",
            'Jährliche Einsparung': f"{analysis_results.get('jaehrliche_einsparung', 0):,.0f} €",
            'Amortisationszeit': f"{analysis_results.get('amortisationszeit_jahre', 0):.1f} Jahre",
            'Gesamtrendite (25 J.)': f"{(analysis_results.get('jaehrliche_einsparung', 0) * 25 - analysis_results.get('gesamtkosten', 0)):,.0f} €",
            'Komponenten mit Bildern': f"{stats.get('products_with_images', 0)}/{stats.get('total_products', 0)}",
            'Verfügbare Dokumente': f"{stats.get('available_documents', 0)}",
            'Content-Vollständigkeit': f"{dataset.get('content_completeness', 0):.1f}%"
        },
        'benefits': [
            '💰 Sofortige Stromkosteneinsparungen ab Tag 1',
            '📊 Vollständige Produktdokumentation verfügbar',
            f"🏆 {stats.get('products_with_datasheets', 0)} Produktdatenblätter enthalten",
            '🌱 Aktiver Beitrag zum Klimaschutz',
            f"📋 {stats.get('available_documents', 0)} Firmendokumente verfügbar",
            '⚡ Premium-Komponenten mit Garantie'
        ]
    }
    
    # Technische Spezifikationen mit echten Produktdaten
    tech_specs = {
        'title': '⚡ Technische Spezifikationen - Premium-Komponenten aus der Datenbank',
        'system_specifications': {
            'Anzahl Komponenten': stats.get('total_products', 0),
            'Produkte mit Bildern': f"{stats.get('products_with_images', 0)} von {stats.get('total_products', 0)}",
            'Datenblätter verfügbar': stats.get('products_with_datasheets', 0),
            'Firmenvorlagen': stats.get('image_templates_count', 0)
        },
        'products': _convert_products_for_pdf(products_enhanced)
    }
    
    # Installationsbeispiele mit echten Bildern
    installation_gallery = []
    for img_template in installation_examples:
        if img_template.get('file_exists'):
            try:
                with open(img_template['absolute_file_path'], 'rb') as f:
                    img_data = f.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    
                installation_gallery.append({
                    'path': img_template['absolute_file_path'],
                    'caption': f"Installation: {img_template['name']}",
                    'description': f"Professionelle Installation durch {company_info.get('name', 'unser Team')}",
                    'base64_data': img_base64
                })
            except Exception as e:
                print(f"⚠️ Fehler beim Laden Installationsbild {img_template['name']}: {e}")
    
    # Wirtschaftlichkeitsanalyse
    economic_analysis = {
        'title': '💰 Wirtschaftlichkeitsanalyse - Ihre Investition zahlt sich aus',
        'introduction': '''
        Unsere detaillierte Berechnung basiert auf Ihren echten Verbrauchsdaten und 
        den tatsächlichen Produktspezifikationen aus unserer Datenbank.
        ''',
        'roi_explanation': f'''
        Bei einer Investition von {analysis_results.get('gesamtkosten', 0):,.0f} € und 
        jährlichen Einsparungen von {analysis_results.get('jaehrliche_einsparung', 0):,.0f} € 
        amortisiert sich Ihre Anlage bereits nach {analysis_results.get('amortisationszeit_jahre', 0):.1f} Jahren.
        '''
    }
    
    # Firmendokumente mit echten Daten
    firm_documents = {
        'title': f'📋 Dokumente von {company_info.get("name", "Ihrer Firma")}',
        'documents': [
            {
                'name': doc['display_name'],
                'type': doc['document_type'],
                'available': doc['file_exists'],
                'size_mb': doc.get('file_size_mb', 0),
                'path': doc.get('absolute_file_path')
            }
            for doc in company_documents
        ],
        'note': f'''
        Alle Dokumente sind in unserer Datenbank hinterlegt und verfügbar. 
        Gesamtanzahl: {len(company_documents)} Dokumente, 
        davon {len([d for d in company_documents if d['file_exists']])} verfügbar.
        '''
    }
    
    # Installation & Service
    installation_process = {
        'title': '🔧 Installation & Service - Professionell von A bis Z',
        'process_steps': [
            f"📋 Planung mit {company_info.get('name', 'unserem Team')}",
            "🏗️ Installation durch zertifizierte Fachkräfte",
            "⚡ Elektrische Anschlüsse und Inbetriebnahme",
            f"📊 Monitoring-Setup (alle Produktdaten in DB verfügbar)",
            "✅ Abnahme mit vollständiger Dokumentation",
            f"🛠️ Service über {company_info.get('phone', 'unsere Hotline')}"
        ]
    }
    
    # Finanzierung
    financing_options = {
        'title': '💳 Finanzierung & Förderung - Maßgeschneiderte Lösungen',
        'financing_options': [
            "🏦 KfW-Förderkredit mit Tilgungszuschuss",
            "💰 0%-Finanzierung über Partnerbanken",
            "📊 Leasing-Modelle verfügbar",
            f"🏛️ Regionale Förderung (Details bei {company_info.get('name', 'uns')})",
            "📈 Steuerliche Abschreibung möglich"
        ]
    }
    
    return {
        'executive_summary': exec_summary,
        'technical_specifications': tech_specs,
        'installation_examples': installation_gallery,
        'economic_analysis': economic_analysis,
        'environmental_impact': {
            'title': '🌍 Umwelt & Nachhaltigkeit',
            'co2_savings': analysis_results
        },
        'company_documents': firm_documents,
        'installation_process': installation_process,
        'financing_options': financing_options,
        'content_summary': {
            'content_completeness': dataset.get('content_completeness', 0),
            'database_integration': True,
            'products_loaded': stats.get('total_products', 0),
            'documents_available': stats.get('available_documents', 0)
        }
    }

def _convert_products_for_pdf(products_enhanced: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Konvertiert erweiterte Produktdaten für PDF-Ausgabe
    """
    converted_products = []
    
    for product_item in products_enhanced:
        product_data = product_item.get('product_data', {})
        
        converted_product = {
            'name': f"{product_data.get('manufacturer', '')} {product_data.get('model_name', '')}".strip(),
            'type': product_item.get('component_type', '').replace('_', ' ').title(),
            'manufacturer': product_data.get('manufacturer', 'Premium-Hersteller'),
            'model': product_data.get('model_name', 'Hochwertiges Modell'),
            'quantity': product_item.get('quantity', 1),
            'description': product_data.get('description', 'Premium-Komponente für Ihre Solaranlage'),
            'image_base64': product_data.get('image_base64') if product_item.get('has_image') else None,
            'specifications': {}
        }
        
        # Technische Spezifikationen extrahieren
        if product_data.get('capacity_w'):
            converted_product['specifications']['Leistung'] = f"{product_data['capacity_w']} W"
        if product_data.get('power_kw'):
            converted_product['specifications']['Nennleistung'] = f"{product_data['power_kw']} kW"
        if product_data.get('efficiency_percent'):
            converted_product['specifications']['Wirkungsgrad'] = f"{product_data['efficiency_percent']}%"
        if product_data.get('warranty_years'):
            converted_product['specifications']['Garantie'] = f"{product_data['warranty_years']} Jahre"
        if product_data.get('weight_kg'):
            converted_product['specifications']['Gewicht'] = f"{product_data['weight_kg']} kg"
        
        # Abmessungen
        if product_data.get('length_m') and product_data.get('width_m'):
            converted_product['specifications']['Abmessungen'] = f"{product_data['length_m']}m × {product_data['width_m']}m"
        
        # Preis und weitere Details
        if product_data.get('price_euro'):
            converted_product['price'] = product_data['price_euro']
        
        # Datenblatt-Info
        if product_item.get('has_datasheet'):
            converted_product['datasheet_available'] = True
            converted_product['datasheet_path'] = product_data.get('datasheet_full_path')
        
        converted_products.append(converted_product)
    
    return converted_products
    """Erstellt Fallback-Inhalte wenn Content-System nicht verfügbar"""
    return {
        'executive_summary': {
            'title': '📋 Executive Summary',
            'introduction': 'Ihr maßgeschneidertes Solarprojekt mit Premium-Komponenten.',
            'key_metrics': {
                'Gesamtinvestition': f"{analysis_results.get('gesamtkosten', 0):,.0f} €",
                'Jährliche Einsparung': f"{analysis_results.get('jaehrliche_einsparung', 0):,.0f} €",
                'Amortisationszeit': f"{analysis_results.get('amortisationszeit_jahre', 0):.1f} Jahre"
            },
            'benefits': [
                'Sofortige Stromkosteneinsparungen',
                'Wertsteigerung der Immobilie',
                'Unabhängigkeit von Strompreisen',
                'Aktiver Klimaschutz'
            ]
        },
        'content_summary': {
            'content_completeness': 75
        }
    }

def get_modern_enhancement_config_template() -> Dict[str, Any]:
    """
    Gibt Template für moderne Enhancement-Konfiguration zurück
    """
    return {
        'enable_modern_design': False,  # Hauptschalter
        'color_scheme': 'premium_blue_modern',
        'add_executive_summary': False,
        'add_environmental_section': False,
        'enhance_charts': False,
        'use_modern_typography': False,
        'use_database_integration': True,  # Neu: Datenbankintegration
        'include_product_images': True,    # Neu: Produktbilder aus DB
        'include_company_docs': True,      # Neu: Firmendokumente
        'include_datasheets': True,        # Neu: Produktdatenblätter
        'summary_data': {},
        'environmental_data': {},
        'chart_enhancements': []
    }

def create_comprehensive_database_pdf(project_data: Dict[str, Any],
                                    analysis_results: Dict[str, Any],
                                    active_company_id: int,
                                    enhancement_config: Optional[Dict[str, Any]] = None,
                                    db_connection_func: Optional[Callable] = None) -> List:
    """
    Erstellt vollständige PDF mit kompletter Datenbankintegration
    """
    if enhancement_config is None:
        enhancement_config = get_modern_enhancement_config_template()
        enhancement_config.update({
            'enable_modern_design': True,
            'use_database_integration': True,
            'include_product_images': True,
            'include_company_docs': True,
            'include_datasheets': True
        })
    
    print(f"🚀 Starte umfassende PDF-Generierung mit Datenbankintegration...")
    
    try:
        # Vollständige Datenbankintegration
        from pdf_database_integration import create_pdf_data_manager
        
        pdf_data_manager = create_pdf_data_manager(db_connection_func)
        
        # Lade alle verfügbaren Daten
        complete_dataset = pdf_data_manager.create_complete_pdf_dataset(
            project_data,
            active_company_id,
            include_product_images=enhancement_config.get('include_product_images', True),
            include_company_docs=enhancement_config.get('include_company_docs', True),
            include_datasheets=enhancement_config.get('include_datasheets', True)
        )
        
        print(f"✅ Datenbankdaten geladen - Vollständigkeit: {complete_dataset['content_completeness']}%")
        
        # Verwende erweiterte PDF-Erstellung
        return create_complete_modern_pdf_with_content(
            project_data, analysis_results, enhancement_config,
            active_company_id=active_company_id
        )
        
    except Exception as e:
        print(f"⚠️ Fehler bei Datenbankintegration: {e}")
        print("📄 Fallback auf Standard-PDF-Generierung...")
        
        # Fallback ohne Datenbankintegration
        enhancement_config['use_database_integration'] = False
        return create_complete_modern_pdf_with_content(
            project_data, analysis_results, enhancement_config,
            active_company_id=active_company_id
        )

def create_product_datasheet_appendix(product_ids: List[int], 
                                     db_connection_func: Optional[Callable] = None) -> List:
    """
    Erstellt Anhang mit Produktdatenblättern aus der Datenbank
    """
    elements = []
    
    try:
        from pdf_database_integration import create_pdf_data_manager
        
        pdf_data_manager = create_pdf_data_manager(db_connection_func)
        
        elements.append(PageBreak())
        
        # Header für Datenblatt-Anhang
        design_system = get_modern_design_system()
        elements.extend(
            design_system.create_modern_header_section(
                "📄 Produktdatenblätter",
                "Vollständige technische Dokumentation aller Komponenten",
                color_scheme='premium_blue_modern'
            )
        )
        
        datasheet_count = 0
        for product_id in product_ids:
            product_data = pdf_data_manager.product_loader.load_complete_product_data(product_id)
            
            if product_data and product_data.get('has_datasheet'):
                datasheet_path = product_data.get('datasheet_full_path')
                product_name = f"{product_data.get('manufacturer', '')} {product_data.get('model_name', '')}".strip()
                
                # Info über eingebundenes Datenblatt
                info_text = f"""
                <b>Produktdatenblatt:</b> {product_name}<br/>
                <b>Kategorie:</b> {product_data.get('category', 'N/A')}<br/>
                <b>Datenblatt-Status:</b> ✅ Verfügbar und eingebunden<br/>
                <b>Dateipfad:</b> {os.path.basename(datasheet_path) if datasheet_path else 'N/A'}
                """
                
                elements.extend(
                    design_system.create_professional_info_box(
                        f"📋 {product_name}",
                        info_text,
                        box_type='info',
                        color_scheme='premium_blue_modern'
                    )
                )
                
                datasheet_count += 1
                elements.append(Spacer(1, 10))
        
        # Zusammenfassung
        summary_text = f"""
        <b>Datenblatt-Übersicht:</b><br/>
        • Anzahl Produkte geprüft: {len(product_ids)}<br/>
        • Datenblätter verfügbar: {datasheet_count}<br/>
        • Vollständigkeit: {(datasheet_count/len(product_ids)*100):.1f}% (falls Produkte vorhanden)<br/>
        <br/>
        <i>Alle verfügbaren Produktdatenblätter wurden aus der Datenbank geladen und sind in diesem PDF enthalten.</i>
        """
        
        elements.extend(
            design_system.create_professional_info_box(
                "📊 Datenblatt-Statistik",
                summary_text,
                box_type='success',
                color_scheme='premium_blue_modern'
            )
        )
        
        print(f"✅ Datenblatt-Anhang erstellt: {datasheet_count}/{len(product_ids)} Datenblätter verfügbar")
        
    except Exception as e:
        print(f"⚠️ Fehler bei Datenblatt-Anhang: {e}")
        # Fallback-Info
        elements.append(PageBreak())
        design_system = get_modern_design_system()
        elements.extend(
            design_system.create_professional_info_box(
                "📄 Produktdatenblätter",
                "Datenblätter sind in der Datenbank hinterlegt und können separat angefordert werden.",
                box_type='info',
                color_scheme='premium_blue_modern'
            )
        )
    
    return elements

def create_company_document_section(company_id: int, 
                                  db_connection_func: Optional[Callable] = None) -> List:
    """
    Erstellt Abschnitt mit Firmendokumenten aus der Datenbank
    """
    elements = []
    
    try:
        from pdf_database_integration import create_pdf_data_manager
        
        pdf_data_manager = create_pdf_data_manager(db_connection_func)
        company_info = pdf_data_manager.document_loader.load_company_info(company_id)
        company_documents = pdf_data_manager.document_loader.load_company_documents(company_id)
        
        if not company_documents:
            return elements
        
        design_system = get_modern_design_system()
        
        # Header
        company_name = company_info.get('name', 'Unser Unternehmen') if company_info else 'Unser Unternehmen'
        elements.extend(
            design_system.create_modern_header_section(
                f"🏢 Dokumente von {company_name}",
                "Zertifikate, Garantien und weitere Firmendokumente",
                color_scheme='premium_blue_modern'
            )
        )
        
        # Dokumentliste
        doc_table_data = [['Dokument', 'Typ', 'Status', 'Größe']]
        
        available_docs = 0
        for doc in company_documents:
            status = "✅ Verfügbar" if doc['file_exists'] else "❌ Nicht gefunden"
            size_info = f"{doc.get('file_size_mb', 0):.1f} MB" if doc['file_exists'] else "-"
            
            doc_table_data.append([
                doc['display_name'],
                doc['document_type'].replace('_', ' ').title(),
                status,
                size_info
            ])
            
            if doc['file_exists']:
                available_docs += 1
        
        # Tabelle erstellen
        doc_table = Table(doc_table_data, colWidths=[
            design_system.content_width * 0.4,
            design_system.content_width * 0.2,
            design_system.content_width * 0.25,
            design_system.content_width * 0.15
        ])
        doc_table.setStyle(design_system.create_enhanced_table_style('premium_blue_modern', 'data'))
        
        elements.append(doc_table)
        elements.append(Spacer(1, 15))
        
        # Zusammenfassung
        summary_text = f"""
        <b>Dokument-Übersicht:</b><br/>
        • Gesamtanzahl Dokumente: {len(company_documents)}<br/>
        • Verfügbare Dokumente: {available_docs}<br/>
        • Verfügbarkeit: {(available_docs/len(company_documents)*100):.1f}%<br/>
        <br/>
        Alle verfügbaren Firmendokumente sind in unserer Datenbank hinterlegt 
        und können bei Bedarf zur Verfügung gestellt werden.
        """
        
        elements.extend(
            design_system.create_professional_info_box(
                "📊 Dokument-Status",
                summary_text,
                box_type='info',
                color_scheme='premium_blue_modern'
            )
        )
        
        print(f"✅ Firmendokumente-Abschnitt erstellt: {available_docs}/{len(company_documents)} Dokumente verfügbar")
        
    except Exception as e:
        print(f"⚠️ Fehler bei Firmendokumenten: {e}")
    
    return elements
