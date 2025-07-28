"""
BUSINESS SECTIONS PDF GENERATOR
===============================
Erstellt spezielle Business-Sektionen für TOM-90 PDFs

Diese Datei generiert die 8 Business-Sektionen als separate PDF-Seiten,
die dann an das TOM-90 PDF angehängt werden können.

Sektionen:
1. 📋 Firmenprofil
2. 🏆 Zertifizierungen  
3. ⭐ Kundenreferenzen
4. 🔧 Installationsservice
5. 🛠️ Wartungsservice
6. 💰 Finanzierungsberatung
7. 🛡️ Versicherungsberatung
8. 🔒 Garantieleistungen

Autor: GitHub Copilot
Datum: 2025-07-27
"""

import io
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
        Table, TableStyle, PageBreak, KeepTogether
    )
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import Color, black, white, blue
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.platypus.flowables import HRFlowable
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class BusinessSectionsPDFGenerator:
    """Generiert Business-Sektionen als PDF-Seiten"""
    
    def __init__(self, company_info: Dict[str, Any]):
        self.company_info = company_info
        self.company_name = company_info.get('name', 'Unser Unternehmen')
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Erstellt benutzerdefinierte Styles"""
        if not self.styles:
            return
            
        # Business-Section Haupttitel
        self.styles.add(ParagraphStyle(
            name='BusinessTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            textColor=Color(0.05, 0.22, 0.5),  # TOM-90 Blau #0d3780
            alignment=TA_CENTER
        ))
        
        # Business-Section Untertitel
        self.styles.add(ParagraphStyle(
            name='BusinessSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=Color(0.3, 0.3, 0.3),
            alignment=TA_LEFT
        ))
        
        # Business-Section Text
        self.styles.add(ParagraphStyle(
            name='BusinessText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Business-Section Highlights
        self.styles.add(ParagraphStyle(
            name='BusinessHighlight',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=Color(0.05, 0.22, 0.5),
            alignment=TA_LEFT,
            leftIndent=20
        ))

    def generate_business_sections_pdf(self, 
                                     include_company_profile: bool = False,
                                     include_certifications: bool = False,
                                     include_references: bool = False,
                                     include_installation: bool = False,
                                     include_maintenance: bool = False,
                                     include_financing: bool = False,
                                     include_insurance: bool = False,
                                     include_warranty: bool = False) -> Optional[bytes]:
        """
        Generiert PDF mit ausgewählten Business-Sektionen
        
        Returns:
            PDF als bytes oder None wenn keine Sektionen ausgewählt
        """
        
        if not REPORTLAB_AVAILABLE:
            print("❌ ReportLab nicht verfügbar - Business-Sektionen können nicht erstellt werden")
            return None
        
        # Prüfe ob mindestens eine Sektion ausgewählt ist
        selected_sections = [
            include_company_profile, include_certifications, include_references,
            include_installation, include_maintenance, include_financing,
            include_insurance, include_warranty
        ]
        
        if not any(selected_sections):
            print("ℹ️ Keine Business-Sektionen ausgewählt")
            return None
        
        # PDF erstellen
        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=A4)
        
        # Frame für den Inhalt
        frame = Frame(2*cm, 2*cm, A4[0]-4*cm, A4[1]-4*cm)
        template = PageTemplate(id='business', frames=frame)
        doc.addPageTemplates([template])
        
        # Story (Inhalt) sammeln
        story = []
        
        # Business-Sektionen erstellen
        if include_company_profile:
            story.extend(self._create_company_profile_section())
            story.append(PageBreak())
        
        if include_certifications:
            story.extend(self._create_certifications_section())
            story.append(PageBreak())
        
        if include_references:
            story.extend(self._create_references_section())
            story.append(PageBreak())
        
        if include_installation:
            story.extend(self._create_installation_section())
            story.append(PageBreak())
        
        if include_maintenance:
            story.extend(self._create_maintenance_section())
            story.append(PageBreak())
        
        if include_financing:
            story.extend(self._create_financing_section())
            story.append(PageBreak())
        
        if include_insurance:
            story.extend(self._create_insurance_section())
            story.append(PageBreak())
        
        if include_warranty:
            story.extend(self._create_warranty_section())
        
        # Letzten PageBreak entfernen falls vorhanden
        if story and isinstance(story[-1], PageBreak):
            story.pop()
        
        # PDF erstellen
        try:
            doc.build(story)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            sections_count = sum(selected_sections)
            print(f"✅ Business-Sektionen PDF erstellt: {sections_count} Seiten")
            return pdf_bytes
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Business-Sektionen: {e}")
            return None

    def _create_company_profile_section(self) -> List:
        """Erstellt die Firmenprofil-Sektion"""
        story = []
        
        story.append(Paragraph("📋 Firmenprofil", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph(f"Über {self.company_name}", self.styles['BusinessSubtitle']))
        
        company_description = f"""
        {self.company_name} ist Ihr vertrauensvoller Partner für nachhaltige Energielösungen. 
        Mit langjähriger Erfahrung und einem Team aus qualifizierten Fachkräften bieten wir 
        Ihnen maßgeschneiderte Photovoltaik-Lösungen für Ihr Zuhause oder Ihr Unternehmen.
        
        Unser Fokus liegt auf höchster Qualität, zuverlässigem Service und langfristigen 
        Kundenbeziehungen. Von der ersten Beratung bis zur finalen Installation und darüber 
        hinaus stehen wir Ihnen mit Expertise und Engagement zur Seite.
        """
        story.append(Paragraph(company_description, self.styles['BusinessText']))
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Unsere Stärken:", self.styles['BusinessSubtitle']))
        
        strengths = [
            "✓ Individuelle Beratung und Planung",
            "✓ Hochwertige Komponenten und Materialien", 
            "✓ Professionelle Installation durch Fachkräfte",
            "✓ Umfassender Service und Wartung",
            "✓ Langfristige Betreuung und Support"
        ]
        
        for strength in strengths:
            story.append(Paragraph(strength, self.styles['BusinessHighlight']))
        
        return story

    def _create_certifications_section(self) -> List:
        """Erstellt die Zertifizierungen-Sektion"""
        story = []
        
        story.append(Paragraph("🏆 Zertifizierungen & Qualifikationen", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Qualitätsstandards und Zertifikate", self.styles['BusinessSubtitle']))
        
        cert_text = """
        Unsere Qualifikationen und Zertifizierungen garantieren Ihnen höchste Standards 
        bei der Planung und Installation Ihrer Photovoltaik-Anlage. Wir arbeiten 
        ausschließlich nach geltenden Normen und Richtlinien.
        """
        story.append(Paragraph(cert_text, self.styles['BusinessText']))
        
        certifications = [
            "🔹 VDE-Zertifizierung für Elektroinstallationen",
            "🔹 ISO 9001 Qualitätsmanagementsystem",
            "🔹 Meisterbetrieb im Elektrohandwerk",
            "🔹 Fachbetrieb für Photovoltaik-Anlagen",
            "🔹 Weiterbildungszertifikate der Hersteller",
            "🔹 Sachkundenachweis für Energiespeicher"
        ]
        
        for cert in certifications:
            story.append(Paragraph(cert, self.styles['BusinessHighlight']))
        
        return story

    def _create_references_section(self) -> List:
        """Erstellt die Referenzen-Sektion"""
        story = []
        
        story.append(Paragraph("⭐ Kundenreferenzen", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Was unsere Kunden sagen", self.styles['BusinessSubtitle']))
        
        references = [
            {
                'name': 'Familie Müller, Einfamilienhaus',
                'text': 'Hervorragende Beratung und professionelle Installation. Die Anlage läuft seit 2 Jahren einwandfrei und die Erträge übertreffen sogar die Prognose.',
                'rating': '⭐⭐⭐⭐⭐'
            },
            {
                'name': 'GmbH Metallbau Schmidt',
                'text': 'Perfekte Lösung für unser Gewerbedach. Trotz komplexer Dachstruktur wurde eine optimale Anlage realisiert. Sehr zu empfehlen!',
                'rating': '⭐⭐⭐⭐⭐'
            },
            {
                'name': 'Familie Weber, Doppelhaushälfte',
                'text': 'Von der Planung bis zur Inbetriebnahme alles perfekt organisiert. Besonders die Erklärung der Anlage war sehr verständlich.',
                'rating': '⭐⭐⭐⭐⭐'
            }
        ]
        
        for ref in references:
            story.append(Paragraph(f"<b>{ref['name']}</b>", self.styles['BusinessHighlight']))
            story.append(Paragraph(f'"{ref["text"]}"', self.styles['BusinessText']))
            story.append(Paragraph(ref['rating'], self.styles['BusinessText']))
            story.append(Spacer(1, 0.2*cm))
        
        return story

    def _create_installation_section(self) -> List:
        """Erstellt die Installation-Sektion"""
        story = []
        
        story.append(Paragraph("🔧 Professioneller Installationsservice", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Ihr Weg zur eigenen Solaranlage", self.styles['BusinessSubtitle']))
        
        installation_text = """
        Unsere erfahrenen Installateure sorgen für eine fachgerechte und sichere 
        Installation Ihrer Photovoltaik-Anlage. Wir koordinieren alle Gewerke 
        und übernehmen die komplette Projektabwicklung.
        """
        story.append(Paragraph(installation_text, self.styles['BusinessText']))
        
        installation_steps = [
            "1️⃣ Terminkoordination und Vorbereitung",
            "2️⃣ Gerüstaufbau und Sicherheitsmaßnahmen",
            "3️⃣ Montage der Unterkonstruktion",
            "4️⃣ Installation der PV-Module",
            "5️⃣ Elektrische Verkabelung und Wechselrichter",
            "6️⃣ Inbetriebnahme und Funktionsprüfung",
            "7️⃣ Einweisung und Übergabe"
        ]
        
        for step in installation_steps:
            story.append(Paragraph(step, self.styles['BusinessHighlight']))
        
        return story

    def _create_maintenance_section(self) -> List:
        """Erstellt die Wartung-Sektion"""
        story = []
        
        story.append(Paragraph("🛠️ Wartung & Langzeitservice", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Dauerhafte Leistung durch professionelle Betreuung", self.styles['BusinessSubtitle']))
        
        maintenance_text = """
        Eine regelmäßige Wartung Ihrer Photovoltaik-Anlage sichert optimale Erträge 
        und verlängert die Lebensdauer der Komponenten. Unser Service-Team steht 
        Ihnen auch nach der Installation jederzeit zur Verfügung.
        """
        story.append(Paragraph(maintenance_text, self.styles['BusinessText']))
        
        services = [
            "🔸 24/7 Monitoring und Fernüberwachung",
            "🔸 Regelmäßige Inspektionen und Wartung", 
            "🔸 Reinigung der PV-Module",
            "🔸 Funktionsprüfung aller Komponenten",
            "🔸 Software-Updates und Optimierungen",
            "🔸 Schnelle Reaktion bei Störungen",
            "🔸 Ersatzteilservice und Reparaturen"
        ]
        
        for service in services:
            story.append(Paragraph(service, self.styles['BusinessHighlight']))
        
        return story

    def _create_financing_section(self) -> List:
        """Erstellt die Finanzierung-Sektion"""
        story = []
        
        story.append(Paragraph("💰 Finanzierung & Förderung", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Individuelle Finanzierungslösungen", self.styles['BusinessSubtitle']))
        
        financing_text = """
        Wir unterstützen Sie bei der optimalen Finanzierung Ihrer Photovoltaik-Anlage. 
        Von staatlichen Förderprogrammen bis zu günstigen Krediten - wir finden 
        die beste Lösung für Ihr Budget.
        """
        story.append(Paragraph(financing_text, self.styles['BusinessText']))
        
        options = [
            "💡 KfW-Förderung 270 - Bis zu 100% Finanzierung",
            "💡 BAFA-Zuschüsse für Energiespeicher",
            "💡 Regionale Förderprogramme",
            "💡 Bankfinanzierung mit günstigen Konditionen",
            "💡 Leasing-Modelle für Gewerbebetriebe",
            "💡 Contracting-Lösungen ohne Eigenkapital"
        ]
        
        for option in options:
            story.append(Paragraph(option, self.styles['BusinessHighlight']))
        
        return story

    def _create_insurance_section(self) -> List:
        """Erstellt die Versicherung-Sektion"""
        story = []
        
        story.append(Paragraph("🛡️ Versicherungsschutz", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Umfassender Schutz für Ihre Investition", self.styles['BusinessSubtitle']))
        
        insurance_text = """
        Ihre Photovoltaik-Anlage ist eine wertvolle Investition, die optimal 
        abgesichert werden sollte. Wir beraten Sie zu allen Versicherungsoptionen 
        und unterstützen bei der Abwicklung.
        """
        story.append(Paragraph(insurance_text, self.styles['BusinessText']))
        
        coverage = [
            "🔒 Elektronikversicherung für alle Komponenten",
            "🔒 Ertragsausfallversicherung",
            "🔒 Sturm- und Hagelschäden",
            "🔒 Diebstahl und Vandalismus",
            "🔒 Betreiberhaftpflicht",
            "🔒 Montageversicherung während Installation"
        ]
        
        for item in coverage:
            story.append(Paragraph(item, self.styles['BusinessHighlight']))
        
        return story

    def _create_warranty_section(self) -> List:
        """Erstellt die Garantie-Sektion"""
        story = []
        
        story.append(Paragraph("🔒 Garantieleistungen", self.styles['BusinessTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("Langfristige Sicherheit für Ihre Anlage", self.styles['BusinessSubtitle']))
        
        warranty_text = """
        Unsere umfassenden Garantieleistungen geben Ihnen die Sicherheit, 
        dass Ihre Photovoltaik-Anlage über viele Jahre zuverlässig funktioniert. 
        Wir stehen für die Qualität unserer Arbeit ein.
        """
        story.append(Paragraph(warranty_text, self.styles['BusinessText']))
        
        warranties = [
            "✅ 25 Jahre Leistungsgarantie auf PV-Module",
            "✅ 10-20 Jahre Produktgarantie je nach Hersteller",  
            "✅ 5-15 Jahre Garantie auf Wechselrichter",
            "✅ 10 Jahre Garantie auf Energiespeicher",
            "✅ 2 Jahre Gewährleistung auf Installation",
            "✅ Erweiterte Garantieoptionen verfügbar"
        ]
        
        for warranty in warranties:
            story.append(Paragraph(warranty, self.styles['BusinessHighlight']))
        
        return story


def generate_business_sections_pdf(company_info: Dict[str, Any], **section_options) -> Optional[bytes]:
    """
    Factory-Funktion zum Erstellen von Business-Sektionen PDF
    
    Args:
        company_info: Firmeninformationen
        **section_options: Business-Section Parameter (include_business_*)
        
    Returns:
        PDF als bytes oder None
    """
    
    generator = BusinessSectionsPDFGenerator(company_info)
    
    return generator.generate_business_sections_pdf(
        include_company_profile=section_options.get('include_business_company_profile', False),
        include_certifications=section_options.get('include_business_certifications', False),
        include_references=section_options.get('include_business_references', False),
        include_installation=section_options.get('include_business_installation', False),
        include_maintenance=section_options.get('include_business_maintenance', False),
        include_financing=section_options.get('include_business_financing', False),
        include_insurance=section_options.get('include_business_insurance', False),
        include_warranty=section_options.get('include_business_warranty', False)
    )
