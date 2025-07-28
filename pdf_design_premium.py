# pdf_design_premium.py
# -*- coding: utf-8 -*-
"""
Premium PDF Design System
Moderne, hochwertige PDF-Designs mit professioneller Bildintegration
"""

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm, inch
from reportlab.platypus import (
    Image, Paragraph, Spacer, Table, TableStyle, 
    KeepTogether, PageBreak, Flowable
)
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import io

class PremiumPDFDesigner:
    """
    Premium PDF Designer für hochwertige, moderne PDF-Ausgaben
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 2*cm
        self.content_width = self.page_width - 2*self.margin
        
        # Premium Color Schemes
        self.color_schemes = {
            'solar_professional': {
                'primary': HexColor('#1a365d'),      # Dunkelblau
                'secondary': HexColor('#2d7dd2'),    # Hellblau  
                'accent': HexColor('#f6ad55'),       # Orange
                'background': HexColor('#f7fafc'),   # Hellgrau
                'text_dark': HexColor('#2d3748'),    # Dunkelgrau
                'text_light': HexColor('#718096'),   # Mittelgrau
                'success': HexColor('#38a169'),      # Grün
                'warning': HexColor('#ed8936'),      # Orange-Rot
            },
            'modern_tech': {
                'primary': HexColor('#2b6cb0'),      # Tech-Blau
                'secondary': HexColor('#4299e1'),    # Helles Tech-Blau
                'accent': HexColor('#ed64a6'),       # Pink-Accent
                'background': HexColor('#f0fff4'),   # Mint-Hintergrund
                'text_dark': HexColor('#1a202c'),    # Schwarz
                'text_light': HexColor('#4a5568'),   # Grau
                'success': HexColor('#48bb78'),      # Hellgrün
                'warning': HexColor('#ed8936'),      # Orange
            },
            'executive_premium': {
                'primary': HexColor('#744210'),      # Goldbraun
                'secondary': HexColor('#d69e2e'),    # Gold
                'accent': HexColor('#e53e3e'),       # Rot-Accent
                'background': HexColor('#fffaf0'),   # Cremeweiß
                'text_dark': HexColor('#2d3748'),    # Dunkelgrau
                'text_light': HexColor('#718096'),   # Mittelgrau
                'success': HexColor('#38a169'),      # Grün
                'warning': HexColor('#dd6b20'),      # Orange
            }
        }
    
    def get_premium_styles(self, color_scheme: str = 'solar_professional') -> Dict:
        """Erstellt Premium-Paragraph-Styles"""
        colors = self.color_schemes.get(color_scheme, self.color_schemes['solar_professional'])
        
        styles = {
            'title_main': ParagraphStyle(
                'TitleMain',
                fontName='Helvetica-Bold',
                fontSize=28,
                textColor=colors['primary'],
                spaceAfter=20,
                alignment=TA_CENTER,
                leading=32
            ),
            'title_section': ParagraphStyle(
                'TitleSection', 
                fontName='Helvetica-Bold',
                fontSize=18,
                textColor=colors['primary'],
                spaceAfter=12,
                spaceBefore=20,
                leading=22,
                borderWidth=0,
                borderColor=colors['secondary'],
                borderPadding=8,
                backColor=colors['background']
            ),
            'subtitle': ParagraphStyle(
                'Subtitle',
                fontName='Helvetica',
                fontSize=14,
                textColor=colors['text_dark'],
                spaceAfter=8,
                leading=18
            ),
            'body_premium': ParagraphStyle(
                'BodyPremium',
                fontName='Helvetica',
                fontSize=11,
                textColor=colors['text_dark'],
                spaceAfter=6,
                leading=16,
                alignment=TA_JUSTIFY
            ),
            'highlight_box': ParagraphStyle(
                'HighlightBox',
                fontName='Helvetica-Bold',
                fontSize=12,
                textColor=colors['primary'],
                spaceAfter=8,
                spaceBefore=8,
                leading=16,
                backColor=colors['background'],
                borderWidth=1,
                borderColor=colors['secondary'],
                borderPadding=12,
                borderRadius=4
            ),
            'info_label': ParagraphStyle(
                'InfoLabel',
                fontName='Helvetica-Bold',
                fontSize=10,
                textColor=colors['text_light'],
                spaceAfter=2,
                leading=12
            ),
            'info_value': ParagraphStyle(
                'InfoValue',
                fontName='Helvetica',
                fontSize=11,
                textColor=colors['text_dark'],
                spaceAfter=6,
                leading=14
            )
        }
        
        return styles
    
    def create_premium_table_style(self, color_scheme: str = 'solar_professional') -> TableStyle:
        """Erstellt moderne Table-Styles"""
        colors_dict = self.color_schemes.get(color_scheme, self.color_schemes['solar_professional'])
        
        return TableStyle([
            # Header-Styling
            ('BACKGROUND', (0, 0), (-1, 0), colors_dict['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Content-Styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors_dict['text_dark']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            
            # Zebra-Streifen für bessere Lesbarkeit
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors_dict['background']]),
            
            # Borders und Linien
            ('GRID', (0, 0), (-1, -1), 0.5, colors_dict['text_light']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors_dict['primary']),
            
            # Padding für bessere Lesbarkeit
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    
    def create_info_box(self, title: str, content: str, box_type: str = 'info',
                       color_scheme: str = 'solar_professional') -> List:
        """Erstellt stilvolle Info-Boxen"""
        colors_dict = self.color_schemes.get(color_scheme, self.color_schemes['solar_professional'])
        styles = self.get_premium_styles(color_scheme)
        
        box_configs = {
            'info': {'bg': colors_dict['background'], 'border': colors_dict['secondary']},
            'success': {'bg': HexColor('#f0fff4'), 'border': colors_dict['success']},
            'warning': {'bg': HexColor('#fffaf0'), 'border': colors_dict['warning']},
            'highlight': {'bg': HexColor('#ebf8ff'), 'border': colors_dict['accent']}
        }
        
        config = box_configs.get(box_type, box_configs['info'])
        
        # Box-Style
        box_style = ParagraphStyle(
            f'Box_{box_type}',
            parent=styles['body_premium'],
            backColor=config['bg'],
            borderWidth=1,
            borderColor=config['border'],
            borderPadding=15,
            borderRadius=6,
            spaceAfter=15,
            spaceBefore=10
        )
        
        title_style = ParagraphStyle(
            f'BoxTitle_{box_type}',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=config['border'],
            spaceAfter=6
        )
        
        elements = []
        if title:
            elements.append(Paragraph(f"<b>{title}</b>", title_style))
        elements.append(Paragraph(content, box_style))
        
        return elements
    
    def create_image_with_caption(self, image_path: str, caption: str = "",
                                 width: float = None, height: float = None,
                                 color_scheme: str = 'solar_professional') -> List:
        """Erstellt Bilder mit professionellen Bildunterschriften"""
        elements = []
        styles = self.get_premium_styles(color_scheme)
        
        try:
            if os.path.exists(image_path):
                # Automatische Größenberechnung falls nicht angegeben
                if width is None:
                    width = self.content_width * 0.8  # 80% der verfügbaren Breite
                
                img = Image(image_path, width=width, height=height)
                img.hAlign = 'CENTER'
                elements.append(img)
                
                if caption:
                    caption_style = ParagraphStyle(
                        'ImageCaption',
                        fontName='Helvetica-Oblique',
                        fontSize=9,
                        textColor=self.color_schemes[color_scheme]['text_light'],
                        alignment=TA_CENTER,
                        spaceAfter=15,
                        spaceBefore=5
                    )
                    elements.append(Paragraph(caption, caption_style))
                
                elements.append(Spacer(1, 10))
                
        except Exception as e:
            # Fallback bei Bildproblemen
            error_style = ParagraphStyle(
                'ImageError',
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.red,
                alignment=TA_CENTER,
                spaceAfter=10
            )
            elements.append(Paragraph(f"[Bild konnte nicht geladen werden: {image_path}]", error_style))
        
        return elements
    
    def create_data_visualization_table(self, data: List[Dict], title: str = "",
                                      color_scheme: str = 'solar_professional') -> List:
        """Erstellt moderne Daten-Visualisierung Tables"""
        elements = []
        styles = self.get_premium_styles(color_scheme)
        
        if title:
            elements.append(Paragraph(title, styles['title_section']))
        
        if not data:
            return elements
        
        # Header aus den Keys des ersten Datenelements
        headers = list(data[0].keys())
        table_data = [headers]
        
        # Daten hinzufügen
        for row in data:
            table_data.append([str(row.get(key, '')) for key in headers])
        
        # Table mit angepassten Spaltenbreiten
        col_widths = [self.content_width / len(headers)] * len(headers)
        
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(self.create_premium_table_style(color_scheme))
        
        elements.append(table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def create_professional_header(self, title: str, subtitle: str = "",
                                 company_info: Dict = None, logo_path: str = "",
                                 color_scheme: str = 'solar_professional') -> List:
        """Erstellt professionelle Header mit Logo und Firmeninfo"""
        elements = []
        styles = self.get_premium_styles(color_scheme)
        colors_dict = self.color_schemes[color_scheme]
        
        # Header-Container
        header_data = []
        
        # Logo und Titel in einer Zeile
        if logo_path and os.path.exists(logo_path):
            try:
                logo_cell = [Image(logo_path, width=3*cm, height=2*cm)]
            except:
                logo_cell = ["[LOGO]"]
        else:
            logo_cell = [""]
        
        title_cell = [
            Paragraph(title, styles['title_main']),
            Paragraph(subtitle, styles['subtitle']) if subtitle else ""
        ]
        
        if company_info:
            company_text = f"""
            <b>{company_info.get('name', '')}</b><br/>
            {company_info.get('address', '')}<br/>
            Tel: {company_info.get('phone', '')} | Email: {company_info.get('email', '')}
            """
            company_cell = [Paragraph(company_text, styles['body_premium'])]
        else:
            company_cell = [""]
        
        header_data.append([logo_cell, title_cell, company_cell])
        
        header_table = Table(header_data, colWidths=[4*cm, None, 4*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Logo links
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Titel zentriert
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),   # Firmeninfo rechts
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(header_table)
        
        # Trennlinie
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(
            width="100%", 
            thickness=2, 
            color=colors_dict['primary'],
            spaceAfter=20
        ))
        
        return elements

class PremiumPDFComponentLibrary:
    """
    Bibliothek für wiederverwendbare Premium-PDF-Komponenten
    """
    
    @staticmethod
    def solar_calculation_summary(calculation_data: Dict, color_scheme: str = 'solar_professional') -> List:
        """Solar-Kalkulations-Zusammenfassung im Premium-Design"""
        designer = PremiumPDFDesigner()
        elements = []
        styles = designer.get_premium_styles(color_scheme)
        
        # Titel
        elements.append(Paragraph("☀ Solar-Kalkulation Übersicht", styles['title_section']))
        
        # Kernzahlen in Grid-Layout
        summary_data = [
            ['Anlagenleistung', f"{calculation_data.get('system_power', 0)} kWp"],
            ['Jährlicher Ertrag', f"{calculation_data.get('annual_yield', 0):,.0f} kWh"],
            ['Investitionskosten', f"{calculation_data.get('investment_cost', 0):,.2f} €"],
            ['Jährliche Einsparung', f"{calculation_data.get('annual_savings', 0):,.2f} €"],
            ['Amortisationszeit', f"{calculation_data.get('payback_time', 0):.1f} Jahre"],
            ['CO₂-Einsparung/Jahr', f"{calculation_data.get('co2_savings', 0):,.0f} kg"]
        ]
        
        summary_table = Table(summary_data, colWidths=[7*cm, 6*cm])
        summary_table.setStyle(designer.create_premium_table_style(color_scheme))
        elements.append(summary_table)
        
        return elements
    
    @staticmethod
    def financial_breakdown(financial_data: Dict, color_scheme: str = 'solar_professional') -> List:
        """Finanzielle Aufschlüsselung im Premium-Design"""
        designer = PremiumPDFDesigner()
        elements = []
        styles = designer.get_premium_styles(color_scheme)
        
        elements.append(Paragraph("💰 Finanzielle Aufschlüsselung", styles['title_section']))
        
        # Kostenaufschlüsselung
        cost_breakdown = financial_data.get('cost_breakdown', {})
        cost_data = [['Kostenposition', 'Betrag (€)', 'Anteil (%)']]
        
        total_cost = sum(cost_breakdown.values()) if cost_breakdown else 1
        
        for item, cost in cost_breakdown.items():
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            cost_data.append([
                item.replace('_', ' ').title(),
                f"{cost:,.2f}",
                f"{percentage:.1f}%"
            ])
        
        cost_table = Table(cost_data, colWidths=[6*cm, 4*cm, 3*cm])
        cost_table.setStyle(designer.create_premium_table_style(color_scheme))
        elements.append(cost_table)
        
        return elements
    
    @staticmethod
    def technical_specifications(tech_data: Dict, color_scheme: str = 'solar_professional') -> List:
        """Technische Spezifikationen im Premium-Design"""
        designer = PremiumPDFDesigner()
        elements = []
        styles = designer.get_premium_styles(color_scheme)
        
        elements.append(Paragraph("⚙ Technische Spezifikationen", styles['title_section']))
        
        # Info-Boxen für verschiedene technische Bereiche
        if 'modules' in tech_data:
            module_info = f"""
            <b>Solarmodule:</b> {tech_data['modules'].get('type', 'N/A')}<br/>
            <b>Leistung pro Modul:</b> {tech_data['modules'].get('power_per_module', 0)} Wp<br/>
            <b>Anzahl Module:</b> {tech_data['modules'].get('count', 0)} Stück<br/>
            <b>Wirkungsgrad:</b> {tech_data['modules'].get('efficiency', 0)}%
            """
            elements.extend(designer.create_info_box("Module", module_info, 'info', color_scheme))
        
        if 'inverter' in tech_data:
            inverter_info = f"""
            <b>Wechselrichter:</b> {tech_data['inverter'].get('type', 'N/A')}<br/>
            <b>Leistung:</b> {tech_data['inverter'].get('power', 0)} kW<br/>
            <b>Wirkungsgrad:</b> {tech_data['inverter'].get('efficiency', 0)}%
            """
            elements.extend(designer.create_info_box("Wechselrichter", inverter_info, 'highlight', color_scheme))
        
        return elements

def integrate_premium_design_system():
    """
    Integration des Premium-Design-Systems in den bestehenden PDF-Generator
    """
    return {
        'designer': PremiumPDFDesigner(),
        'components': PremiumPDFComponentLibrary(),
        'available': True,
        'version': '1.0-Premium'
    }
