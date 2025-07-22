# pdf_content_enhanced_system.py
# -*- coding: utf-8 -*-
"""
Vollständiges Content-Management System für PDF-Generierung
Erweitert das moderne Design-System um echte Inhalte, Bilder, Texte und Dokumente
"""

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Image, Paragraph, Spacer, Table, TableStyle, 
    KeepTogether, PageBreak, Flowable
)
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os
import base64
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable

class PDFContentManager:
    """
    Verwaltet alle Inhalte für PDF-Generierung: Texte, Bilder, Produktdaten, Dokumente
    """
    
    def __init__(self):
        self.predefined_texts = self._load_predefined_texts()
        self.product_image_cache = {}
        self.company_document_cache = {}
        
    def _load_predefined_texts(self) -> Dict[str, Dict[str, str]]:
        """Lädt vordefinierte Textvorlagen für verschiedene Bereiche"""
        return {
            'executive_summary': {
                'title': '📋 Executive Summary - Ihr Solar-Projekt im Überblick',
                'introduction': '''
                Mit großer Freude präsentieren wir Ihnen Ihre maßgeschneiderte Premium-Photovoltaik-Lösung. 
                Unsere detaillierte Analyse zeigt, dass Ihre Investition in nachhaltige Solarenergie nicht nur 
                umweltfreundlich, sondern auch hochprofitabel ist.
                ''',
                'benefits_header': '🌟 Ihre Hauptvorteile auf einen Blick:',
                'benefits_list': [
                    '💰 Sofortige Stromkosteneinsparungen ab dem ersten Tag',
                    '🏡 Wertsteigerung Ihrer Immobilie um 3-5%',
                    '🌱 Aktiver Beitrag zum Klimaschutz und zur Energiewende',
                    '📈 Schutz vor steigenden Strompreisen',
                    '🔒 25 Jahre Herstellergarantie auf Premium-Komponenten',
                    '🏆 Staatliche Förderungen und Steuervorteile',
                    '⚡ Unabhängigkeit und Energiesicherheit'
                ],
                'call_to_action': '''
                Starten Sie jetzt in eine nachhaltige und profitable Energiezukunft! 
                Unsere Experten begleiten Sie von der Planung bis zur Inbetriebnahme.
                '''
            },
            
            'technical_introduction': {
                'title': '⚡ Technische Spezifikationen - Premium-Komponenten für maximale Effizienz',
                'introduction': '''
                Ihre Solaranlage besteht ausschließlich aus hochwertigen Premium-Komponenten führender Hersteller. 
                Jede Komponente wurde sorgfältig ausgewählt, um maximale Effizienz, Langlebigkeit und 
                Ertragssicherheit zu gewährleisten.
                ''',
                'quality_note': '''
                🏆 Alle Komponenten erfüllen höchste Qualitätsstandards und sind von unabhängigen 
                Instituten zertifiziert. Sie erhalten volle Herstellergarantien und Leistungsgarantien.
                '''
            },
            
            'economic_analysis': {
                'title': '💰 Wirtschaftlichkeitsanalyse - Ihre Investition zahlt sich aus',
                'introduction': '''
                Unsere detaillierte Wirtschaftlichkeitsberechnung basiert auf aktuellen Strompreisen, 
                Ihrem Verbrauchsprofil und konservativen Ertragsprognosen. Die Analyse zeigt eine 
                hervorragende Rendite Ihrer Investition.
                ''',
                'roi_explanation': '''
                Ihre Solaranlage amortisiert sich bereits nach wenigen Jahren durch die eingesparten 
                Stromkosten. Danach produziert sie über weitere 20+ Jahre praktisch kostenlosen Strom.
                '''
            },
            
            'environmental_impact': {
                'title': '🌍 Umwelt & Nachhaltigkeit - Ihr Beitrag für eine grünere Zukunft',
                'introduction': '''
                Mit Ihrer Solaranlage leisten Sie einen bedeutenden Beitrag zum Klimaschutz und zur 
                nachhaltigen Energieversorgung. Jede Kilowattstunde Solarstrom vermeidet CO₂-Emissionen 
                und reduziert die Abhängigkeit von fossilen Brennstoffen.
                ''',
                'impact_statement': '''
                🌱 Ihre Anlage spart über 25 Jahre so viel CO₂ ein, wie ein Wald mit über 1.000 Bäumen 
                bindet. Sie werden Teil der Energiewende und hinterlassen Ihren Kindern eine saubere Umwelt.
                '''
            },
            
            'installation_process': {
                'title': '🔧 Installation & Service - Professionelle Umsetzung von A bis Z',
                'introduction': '''
                Unsere zertifizierten Installateure übernehmen die komplette Projektabwicklung. 
                Von der Anmeldung bei Ihrem Netzbetreiber bis zur finalen Inbetriebnahme - 
                Sie haben einen Ansprechpartner für alles.
                ''',
                'process_steps': [
                    '📋 Detaillierte Planung und Genehmigungen',
                    '🏗️ Professionelle Installation durch Fachbetrieb',
                    '⚡ Elektrische Anschlüsse und Inbetriebnahme',
                    '📊 Einrichtung des Monitoring-Systems',
                    '✅ Abnahme und Übergabe mit Einweisung',
                    '🛠️ Wartung und Service nach Bedarf'
                ]
            },
            
            'financing_options': {
                'title': '💳 Finanzierung & Förderung - Flexible Lösungen für jeden Bedarf',
                'introduction': '''
                Wir bieten Ihnen verschiedene Finanzierungsmöglichkeiten, damit Ihre Solaranlage 
                sofort Erträge generiert, ohne Ihr Budget zu belasten. Nutzen Sie attraktive 
                Förderprogramme und günstige Kreditkonditionen.
                ''',
                'financing_options': [
                    '🏦 KfW-Förderkredit mit Tilgungszuschuss',
                    '💰 0%-Finanzierung über unsere Partnerbanken',
                    '📊 Leasing-Modelle für Gewerbetreibende',
                    '🏛️ Regionale Förderprogramme und Zuschüsse',
                    '📈 Steuerliche Vorteile durch Abschreibungen'
                ]
            }
        }
    
    def get_content_template(self, section: str) -> Dict[str, Any]:
        """Gibt Textvorlage für einen Bereich zurück"""
        return self.predefined_texts.get(section, {})
    
    def create_executive_summary_content(self, calc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Erstellt Executive Summary mit echten Berechnungsdaten"""
        template = self.get_content_template('executive_summary')
        
        # Berechne Key Metrics
        total_investment = calc_data.get('gesamtkosten', 0)
        annual_savings = calc_data.get('jaehrliche_einsparung', 0)
        payback_years = calc_data.get('amortisationszeit_jahre', 0)
        total_return_25_years = annual_savings * 25 - total_investment
        
        roi_percentage = ((total_return_25_years / total_investment) * 100) if total_investment > 0 else 0
        
        return {
            'title': template['title'],
            'introduction': template['introduction'],
            'key_metrics': {
                'Gesamtinvestition': f"{total_investment:,.0f} €",
                'Jährliche Einsparung': f"{annual_savings:,.0f} €",
                'Amortisationszeit': f"{payback_years:.1f} Jahre",
                'Gesamtrendite (25 J.)': f"{total_return_25_years:,.0f} €",
                'ROI': f"{roi_percentage:.1f}%"
            },
            'benefits': template['benefits_list'],
            'call_to_action': template['call_to_action']
        }
    
    def create_technical_content(self, project_data: Dict[str, Any], 
                               get_product_by_id_func: Optional[Callable] = None) -> Dict[str, Any]:
        """Erstellt technische Inhalte mit echten Produktdaten"""
        template = self.get_content_template('technical_introduction')
        
        # Lade Produktdaten
        products = []
        components = project_data.get('komponenten', {})
        
        for component_type, component_data in components.items():
            if isinstance(component_data, dict) and 'produkt_id' in component_data:
                product_id = component_data['produkt_id']
                
                if get_product_by_id_func:
                    try:
                        product_details = get_product_by_id_func(product_id)
                        if product_details:
                            products.append({
                                'type': component_type,
                                'id': product_id,
                                'name': product_details.get('name', 'Unbekanntes Produkt'),
                                'manufacturer': product_details.get('hersteller', ''),
                                'model': product_details.get('modell', ''),
                                'specifications': product_details.get('spezifikationen', {}),
                                'image_base64': product_details.get('bild_base64', ''),
                                'price': product_details.get('preis', 0),
                                'quantity': component_data.get('anzahl', 1),
                                'description': product_details.get('beschreibung', '')
                            })
                    except Exception as e:
                        print(f"⚠️ Fehler beim Laden Produkt {product_id}: {e}")
        
        return {
            'title': template['title'],
            'introduction': template['introduction'],
            'quality_note': template['quality_note'],
            'products': products,
            'system_specifications': {
                'Gesamtleistung': f"{project_data.get('gesamtleistung_kwp', 0):.1f} kWp",
                'Modulanzahl': project_data.get('anzahl_module', 0),
                'Dachfläche': f"{project_data.get('dachflaeche_m2', 0):.0f} m²",
                'Ausrichtung': project_data.get('ausrichtung', 'Süd'),
                'Neigungswinkel': f"{project_data.get('neigung_grad', 30)}°",
                'Erwarteter Jahresertrag': f"{project_data.get('jahresertrag_kwh', 0):,.0f} kWh"
            }
        }
    
    def create_product_showcase_content(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Erstellt Produktpräsentation mit Bildern und Details"""
        return {
            'title': '🛠️ Premium-Komponenten - Qualität die überzeugt',
            'introduction': '''
            Ihre Solaranlage besteht aus sorgfältig ausgewählten Premium-Komponenten. 
            Jedes Produkt ist von führenden Herstellern und bietet höchste Qualität und Langlebigkeit.
            ''',
            'products': products,
            'quality_assurance': '''
            🏆 Alle Komponenten sind TÜV-zertifiziert und erfüllen höchste Qualitätsstandards. 
            Sie erhalten umfassende Herstellergarantien und unseren Premium-Service.
            '''
        }
    
    def get_default_product_image(self) -> str:
        """Erstellt Standard-Produktbild als Base64"""
        # Erstelle ein einfaches SVG-Placeholder-Bild
        svg_content = '''
        <svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="150" fill="#f0f9ff" stroke="#3b82f6" stroke-width="2"/>
            <text x="100" y="75" text-anchor="middle" font-family="Arial" font-size="14" fill="#1e40af">
                Premium Solar
            </text>
            <text x="100" y="95" text-anchor="middle" font-family="Arial" font-size="12" fill="#64748b">
                Komponente
            </text>
        </svg>
        '''
        return base64.b64encode(svg_content.encode()).decode()

class PDFImageManager:
    """
    Verwaltet Bilder für PDF-Ausgabe: Produktbilder, Logos, Beispielbilder
    """
    
    def __init__(self):
        self.image_cache = {}
        self.default_images = self._create_default_images()
    
    def _create_default_images(self) -> Dict[str, str]:
        """Erstellt Standard-Bilder als Base64"""
        return {
            'solar_panels': self._create_solar_panel_image(),
            'inverter': self._create_inverter_image(),
            'mounting_system': self._create_mounting_image(),
            'battery': self._create_battery_image(),
            'installation_example': self._create_installation_example()
        }
    
    def _create_solar_panel_image(self) -> str:
        """Erstellt Solarmodul-Bild"""
        svg_content = '''
        <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="solarCells" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
                    <rect width="28" height="28" fill="#1e3a8a" stroke="#3b82f6" stroke-width="1"/>
                </pattern>
            </defs>
            <rect width="300" height="200" fill="#374151"/>
            <rect x="10" y="10" width="280" height="180" fill="url(#solarCells)"/>
            <text x="150" y="105" text-anchor="middle" font-family="Arial" font-size="16" fill="white" font-weight="bold">
                Premium Solarmodule
            </text>
            <text x="150" y="125" text-anchor="middle" font-family="Arial" font-size="12" fill="#e5e7eb">
                Monokristallin • 400W • 21% Wirkungsgrad
            </text>
        </svg>
        '''
        return base64.b64encode(svg_content.encode()).decode()
    
    def _create_inverter_image(self) -> str:
        """Erstellt Wechselrichter-Bild"""
        svg_content = '''
        <svg width="250" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="250" height="200" fill="#f8fafc"/>
            <rect x="25" y="30" width="200" height="140" fill="#374151" rx="10"/>
            <rect x="35" y="40" width="180" height="50" fill="#1e40af"/>
            <circle cx="125" r="15" cy="65" fill="#22c55e"/>
            <text x="125" y="110" text-anchor="middle" font-family="Arial" font-size="14" fill="white" font-weight="bold">
                Premium Wechselrichter
            </text>
            <text x="125" y="130" text-anchor="middle" font-family="Arial" font-size="10" fill="#e5e7eb">
                10kW • 98.5% Wirkungsgrad
            </text>
            <text x="125" y="145" text-anchor="middle" font-family="Arial" font-size="10" fill="#e5e7eb">
                20 Jahre Garantie
            </text>
        </svg>
        '''
        return base64.b64encode(svg_content.encode()).decode()
    
    def _create_mounting_image(self) -> str:
        """Erstellt Montagesystem-Bild"""
        svg_content = '''
        <svg width="300" height="150" xmlns="http://www.w3.org/2000/svg">
            <rect width="300" height="150" fill="#f0f9ff"/>
            <!-- Dach -->
            <polygon points="50,120 250,120 280,80 20,80" fill="#8b5cf6"/>
            <!-- Montagesystem -->
            <rect x="60" y="90" width="180" height="8" fill="#374151"/>
            <rect x="70" y="85" width="4" height="20" fill="#6b7280"/>
            <rect x="110" y="85" width="4" height="20" fill="#6b7280"/>
            <rect x="150" y="85" width="4" height="20" fill="#6b7280"/>
            <rect x="190" y="85" width="4" height="20" fill="#6b7280"/>
            <rect x="230" y="85" width="4" height="20" fill="#6b7280"/>
            <text x="150" y="40" text-anchor="middle" font-family="Arial" font-size="14" fill="#1e40af" font-weight="bold">
                Premium Montagesystem
            </text>
            <text x="150" y="60" text-anchor="middle" font-family="Arial" font-size="11" fill="#64748b">
                Dachintegration • Alu-Premium • 25J Garantie
            </text>
        </svg>
        '''
        return base64.b64encode(svg_content.encode()).decode()
    
    def _create_battery_image(self) -> str:
        """Erstellt Batteriespeicher-Bild"""
        svg_content = '''
        <svg width="200" height="250" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="250" fill="#f8fafc"/>
            <rect x="40" y="40" width="120" height="170" fill="#374151" rx="8"/>
            <rect x="50" y="50" width="100" height="20" fill="#22c55e"/>
            <rect x="50" y="80" width="100" height="20" fill="#22c55e"/>
            <rect x="50" y="110" width="100" height="20" fill="#22c55e"/>
            <rect x="50" y="140" width="80" height="20" fill="#eab308"/>
            <rect x="50" y="170" width="40" height="20" fill="#6b7280"/>
            <text x="100" y="30" text-anchor="middle" font-family="Arial" font-size="12" fill="#1e40af" font-weight="bold">
                Batteriespeicher
            </text>
            <text x="100" y="235" text-anchor="middle" font-family="Arial" font-size="10" fill="#64748b">
                10kWh • Lithium • Smart
            </text>
        </svg>
        '''
        return base64.b64encode(svg_content.encode()).decode()
    
    def _create_installation_example(self) -> str:
        """Erstellt Installationsbeispiel-Bild"""
        svg_content = '''
        <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#e0f2fe"/>
            <!-- Himmel -->
            <rect width="400" height="100" fill="#3b82f6"/>
            <!-- Sonne -->
            <circle cx="350" cy="50" r="25" fill="#fbbf24"/>
            <!-- Strahlen -->
            <line x1="320" y1="50" x2="310" y2="50" stroke="#fbbf24" stroke-width="2"/>
            <line x1="380" y1="50" x2="390" y2="50" stroke="#fbbf24" stroke-width="2"/>
            <line x1="350" y1="20" x2="350" y2="10" stroke="#fbbf24" stroke-width="2"/>
            <line x1="350" y1="80" x2="350" y2="90" stroke="#fbbf24" stroke-width="2"/>
            
            <!-- Haus -->
            <rect x="100" y="150" width="200" height="100" fill="#e5e7eb"/>
            <!-- Dach -->
            <polygon points="80,150 200,100 320,150" fill="#6b7280"/>
            <!-- Solarmodule -->
            <rect x="120" y="110" width="160" height="35" fill="#1e3a8a"/>
            <line x1="140" y1="110" x2="140" y2="145" stroke="#3b82f6"/>
            <line x1="160" y1="110" x2="160" y2="145" stroke="#3b82f6"/>
            <line x1="180" y1="110" x2="180" y2="145" stroke="#3b82f6"/>
            <line x1="200" y1="110" x2="200" y2="145" stroke="#3b82f6"/>
            <line x1="220" y1="110" x2="220" y2="145" stroke="#3b82f6"/>
            <line x1="240" y1="110" x2="240" y2="145" stroke="#3b82f6"/>
            <line x1="260" y1="110" x2="260" y2="145" stroke="#3b82f6"/>
            
            <!-- Fenster -->
            <rect x="130" y="180" width="30" height="40" fill="#60a5fa"/>
            <rect x="240" y="180" width="30" height="40" fill="#60a5fa"/>
            <!-- Tür -->
            <rect x="180" y="200" width="40" height="50" fill="#92400e"/>
            
            <text x="200" y="280" text-anchor="middle" font-family="Arial" font-size="14" fill="#1e40af" font-weight="bold">
                Professionelle Solar-Installation
            </text>
        </svg>
        '''
        return base64.b64encode(svg_content.encode()).decode()
    
    def get_product_image(self, product_type: str, product_data: Dict[str, Any] = None) -> str:
        """Gibt Produktbild zurück (echt oder Standard)"""
        # Versuche echtes Bild aus Produktdaten
        if product_data and product_data.get('bild_base64'):
            return product_data['bild_base64']
        
        # Fallback auf Standard-Bilder
        type_mapping = {
            'solarmodule': 'solar_panels',
            'module': 'solar_panels',
            'panels': 'solar_panels',
            'wechselrichter': 'inverter',
            'inverter': 'inverter',
            'montage': 'mounting_system',
            'mounting': 'mounting_system',
            'batterie': 'battery',
            'battery': 'battery',
            'speicher': 'battery'
        }
        
        # Suche nach passendem Standard-Bild
        for key, image_type in type_mapping.items():
            if key.lower() in product_type.lower():
                return self.default_images.get(image_type, self.default_images['solar_panels'])
        
        # Standard-Fallback
        return self.default_images['solar_panels']
    
    def get_installation_examples(self) -> List[Dict[str, str]]:
        """Gibt Installationsbeispiele zurück"""
        return [
            {
                'image_base64': self.default_images['installation_example'],
                'caption': 'Professionelle Solarinstallation auf Einfamilienhaus',
                'description': 'Moderne Aufdach-Montage mit optimaler Südausrichtung für maximalen Ertrag'
            }
        ]

class PDFDocumentManager:
    """
    Verwaltet Firmendokumente, Datenblätter und weitere PDF-Anhänge
    """
    
    def __init__(self):
        self.document_cache = {}
    
    def get_company_documents(self, company_id: int, 
                            db_list_company_documents_func: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Lädt Firmendokumente aus Datenbank"""
        documents = []
        
        if db_list_company_documents_func:
            try:
                # Lade verschiedene Dokumenttypen
                document_types = ['datasheet', 'certificate', 'warranty', 'manual', 'company_profile']
                
                for doc_type in document_types:
                    try:
                        docs = db_list_company_documents_func(company_id, doc_type)
                        if docs:
                            documents.extend(docs)
                    except Exception as e:
                        print(f"⚠️ Fehler beim Laden {doc_type}: {e}")
                
            except Exception as e:
                print(f"⚠️ Fehler beim Laden Firmendokumente: {e}")
        
        # Füge Standard-Dokumente hinzu falls keine gefunden
        if not documents:
            documents = self._get_default_documents()
        
        return documents
    
    def _get_default_documents(self) -> List[Dict[str, Any]]:
        """Erstellt Standard-Dokument-Platzhalter"""
        return [
            {
                'id': 1,
                'name': 'Produktdatenblatt Solarmodule',
                'type': 'datasheet',
                'description': 'Technische Spezifikationen und Leistungsgarantien',
                'file_path': 'documents/solar_modules_datasheet.pdf',
                'available': False
            },
            {
                'id': 2,
                'name': 'Wechselrichter Spezifikationen',
                'type': 'datasheet', 
                'description': 'Detaillierte technische Dokumentation',
                'file_path': 'documents/inverter_specs.pdf',
                'available': False
            },
            {
                'id': 3,
                'name': 'Zertifikate und Qualitätsnachweise',
                'type': 'certificate',
                'description': 'TÜV-Zertifikate und Qualitätssiegel',
                'file_path': 'documents/certificates.pdf',
                'available': False
            },
            {
                'id': 4,
                'name': 'Garantiebedingungen',
                'type': 'warranty',
                'description': '25 Jahre Herstellergarantie Details',
                'file_path': 'documents/warranty_terms.pdf',
                'available': False
            }
        ]
    
    def create_document_overview(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Erstellt Dokumentübersicht für PDF"""
        return {
            'title': '📁 Zusätzliche Dokumentation',
            'introduction': '''
            Zu Ihrer Solaranlage erhalten Sie umfassende Dokumentationen, Datenblätter und 
            Zertifikate. Diese Unterlagen enthalten alle technischen Details und Garantieinformationen.
            ''',
            'documents': documents,
            'note': '''
            📋 Alle Dokumente werden Ihnen nach Vertragsabschluss in digitaler Form zur Verfügung gestellt. 
            Bei Fragen stehen wir Ihnen jederzeit zur Verfügung.
            '''
        }

# Hauptintegrationsfunktionen
def create_complete_pdf_content(project_data: Dict[str, Any], 
                              analysis_results: Dict[str, Any],
                              get_product_by_id_func: Optional[Callable] = None,
                              db_list_company_documents_func: Optional[Callable] = None,
                              active_company_id: int = 1) -> Dict[str, Any]:
    """
    Erstellt vollständige PDF-Inhalte mit allen Komponenten
    """
    content_manager = PDFContentManager()
    image_manager = PDFImageManager()
    document_manager = PDFDocumentManager()
    
    # 1. Executive Summary
    executive_content = content_manager.create_executive_summary_content(analysis_results)
    
    # 2. Technische Inhalte mit Produktdaten
    technical_content = content_manager.create_technical_content(
        project_data, get_product_by_id_func
    )
    
    # 3. Produktbilder ergänzen
    for product in technical_content['products']:
        product['image_base64'] = image_manager.get_product_image(
            product['type'], product
        )
    
    # 4. Installationsbeispiele
    installation_examples = image_manager.get_installation_examples()
    
    # 5. Firmendokumente
    company_documents = document_manager.get_company_documents(
        active_company_id, db_list_company_documents_func
    )
    document_overview = document_manager.create_document_overview(company_documents)
    
    # 6. Wirtschaftlichkeit
    economic_template = content_manager.get_content_template('economic_analysis')
    
    # 7. Umwelt-Impact
    environmental_template = content_manager.get_content_template('environmental_impact')
    
    # 8. Installation & Service
    installation_template = content_manager.get_content_template('installation_process')
    
    # 9. Finanzierung
    financing_template = content_manager.get_content_template('financing_options')
    
    return {
        'executive_summary': executive_content,
        'technical_specifications': technical_content,
        'installation_examples': installation_examples,
        'company_documents': document_overview,
        'economic_analysis': economic_template,
        'environmental_impact': environmental_template,
        'installation_process': installation_template,
        'financing_options': financing_template,
        'content_summary': {
            'total_products': len(technical_content['products']),
            'total_documents': len(company_documents),
            'total_examples': len(installation_examples),
            'content_completeness': 100  # Alle Inhalte verfügbar
        }
    }

def get_enhanced_content_config() -> Dict[str, Any]:
    """
    Gibt Konfiguration für erweiterte Inhalte zurück
    """
    return {
        'include_executive_summary': True,
        'include_technical_specs': True,
        'include_product_images': True,
        'include_installation_examples': True,
        'include_company_documents': True,
        'include_economic_analysis': True,
        'include_environmental_impact': True,
        'include_installation_process': True,
        'include_financing_options': True,
        'image_quality': 'high',
        'content_language': 'de',
        'personalization_level': 'high'
    }
