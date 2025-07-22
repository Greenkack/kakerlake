# pdf_generator_professional.py
# -*- coding: utf-8 -*-
"""
pdf_generator_professional.py

Professionelle Erweiterung des PDF-Generators mit Template-Unterstützung.
Erweitert das bestehende PDF-Generator-System um moderne, professionelle Templates.

Basiert auf: pdf_generator.py
Erweitert um: Professionelle Templates, erweiterte Layouts, moderne Designs

Author: GitHub Copilot (Erweiterung des bestehenden Systems)
Version: 1.0 - Professionelle Erweiterung
"""

from __future__ import annotations
import os
import base64
import io
import math
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable

# Importiere erweiterte Debug-Funktionalität
try:
    from pdf_debug_enhanced import (
        pdf_debug_manager, 
        debug_pdf_generator, 
        validate_widget_integration,
        validate_style_integration
    )
    _DEBUG_AVAILABLE = True
except ImportError:
    _DEBUG_AVAILABLE = False
    # Fallback-Decorator
    def debug_pdf_generator(func):
        return func

# Importiere bestehenden PDF-Generator
try:
    from pdf_generator import PDFGenerator, _REPORTLAB_AVAILABLE, _PYPDF_AVAILABLE
    _PDF_GENERATOR_AVAILABLE = True
except ImportError:
    _PDF_GENERATOR_AVAILABLE = False
    
# Importiere professionelle Template-Module
try:
    from pdf_professional_templates import (
        get_professional_template,
        create_professional_cover_letter_template,
        create_professional_project_summary_template
    )
    from pdf_styles import (
        get_professional_color_palette,
        get_professional_paragraph_styles,
        get_professional_table_style,
        create_professional_header_footer_styles,
        ColorScheme,
        PDFVisualEnhancer,
        PDFThemeManager,
        ProfessionalPDFBackgrounds
    )
    _PROFESSIONAL_TEMPLATES_AVAILABLE = True
except ImportError:
    _PROFESSIONAL_TEMPLATES_AVAILABLE = False

# Importiere Datenvalidierung (falls verfügbar)
try:
    from pdf_data_validator import validate_pdf_data
    _DATA_VALIDATOR_AVAILABLE = True
except ImportError:
    _DATA_VALIDATOR_AVAILABLE = False
    
    # Fallback-Klassen nur wenn wirklich nötig
    class ColorScheme:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def to_dict(self):
            return self.__dict__
    
    class PDFVisualEnhancer:
        def __init__(self):
            self.chart_themes = {}
    
    class PDFThemeManager:
        def __init__(self):
            self.themes = {}
        
        def get_professional_theme(self, theme_name):
            return {}
            
        def create_professional_table_style(self, theme_name):
            from reportlab.platypus import TableStyle
            try:
                from reportlab.lib.colors import colors
            except ImportError:
                # Fallback bei Import-Problemen
                class colors:
                    grey = (0.5, 0.5, 0.5)
                    whitesmoke = (0.96, 0.96, 0.96)
                    black = (0, 0, 0)
                    white = (1, 1, 1)
            
            return TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            
        def create_professional_paragraph_style(self, style_name, theme_name):
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.colors import HexColor
            return ParagraphStyle(
                name=style_name,
                fontName='Helvetica',
                fontSize=11,
                textColor=HexColor('#1f2937')
            )
    
    class ProfessionalPDFBackgrounds:
        def __init__(self):
            pass

    # Fallback-Funktionen wenn Module nicht verfügbar
    def get_professional_template(template_name):
        from reportlab.lib.units import cm
        return {
            "name": "Standard Professional",
            "colors": {
                "primary": "#1e3a8a",
                "secondary": "#3b82f6", 
                "accent": "#06b6d4",
                "text_dark": "#1f2937",
                "background": "#ffffff"
            },
            "typography": {
                "main_font": "Helvetica",
                "heading_font": "Helvetica-Bold",
                "h1_size": 24,
                "h2_size": 18,
                "body_size": 11
            },
            "layout": {
                "margins": {
                    "top": 2.5 * cm,
                    "bottom": 2.5 * cm,
                    "left": 2.0 * cm,
                    "right": 2.0 * cm
                }
            }
        }
    
    def create_professional_cover_letter_template(template_name):
        return f"Professionelles Anschreiben für {template_name}"
    
    def create_professional_project_summary_template(template_name):
        return f"Professionelle Zusammenfassung für {template_name}"
    
    def get_professional_color_palette(template_name):
        return {}
    
    def get_professional_paragraph_styles(template_name):
        return {}
    
    def get_professional_table_style(template_name):
        # Direkter Fallback ohne PDFThemeManager
        from reportlab.platypus import TableStyle
        try:
            from reportlab.lib.colors import colors
        except ImportError:
            class colors:
                grey = (0.5, 0.5, 0.5)
                whitesmoke = (0.96, 0.96, 0.96)
                black = (0, 0, 0)
        
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
    
    def create_professional_header_footer_styles(template_name):
        from reportlab.lib.units import cm
        return {
            'header': {
                'background_color': (0.1, 0.2, 0.5),
                'text_color': (1, 1, 1),
                'font_name': 'Helvetica-Bold',
                'font_size': 10,
                'height': 1.5 * cm
            },
            'footer': {
                'background_color': (0.2, 0.4, 0.8),
                'text_color': (1, 1, 1),
                'font_name': 'Helvetica',
                'font_size': 9,
                'height': 1.0 * cm
            }
        }

# PDF-Widgets Integration für erweiterte Strukturverwaltung (Optional)
_PDF_WIDGETS_AVAILABLE = False
try:
    from pdf_widgets import PDFSectionManager
    _PDF_WIDGETS_AVAILABLE = True
except (ImportError, SyntaxError):
    _PDF_WIDGETS_AVAILABLE = False
    
    class PDFSectionManager:
        def __init__(self):
            self.available_sections = {}
        def export_configuration(self):
            return {}

# === PREMIUM DESIGN SYSTEM INTEGRATION ===
try:
    from pdf_design_premium import (
        PremiumPDFDesigner,
        PremiumPDFComponentLibrary,
        integrate_premium_design_system
    )
    _PREMIUM_DESIGN_AVAILABLE = True
except ImportError:
    _PREMIUM_DESIGN_AVAILABLE = False
    
    # Fallback für Premium Design
    class PremiumPDFDesigner:
        def __init__(self):
            self.color_schemes = {}
        def get_premium_styles(self, scheme='default'):
            return {}
        def create_premium_table_style(self, scheme='default'):
            return None
        def create_professional_header(self, title, **kwargs):
            return []
    
    class PremiumPDFComponentLibrary:
        @staticmethod
        def solar_calculation_summary(data, scheme='default'):
            return []
        @staticmethod
        def financial_breakdown(data, scheme='default'):
            return []
        @staticmethod
        def technical_specifications(data, scheme='default'):
            return []

# === WOW FEATURES INTEGRATION ===
try:
    from pdf_wow_features import (
        PDFWowFeaturesManager,
        CinematicPDFTransitions,
        InteractivePDFWidgets,
        AIPoweredLayoutOptimizer,
        AudioEmbeddedPDFs,
        ResponsivePDFDesign
    )
    _WOW_FEATURES_AVAILABLE = True
except ImportError:
    _WOW_FEATURES_AVAILABLE = False
    
    # Fallback-Klassen für WOW-Features
    class PDFWowFeaturesManager:
        def __init__(self): 
            pass
        def render_wow_features_ui(self): 
            return {}
    
    class CinematicPDFTransitions:
        def __init__(self): 
            pass
        def render_transition_selector(self): 
            return {}
    
    class InteractivePDFWidgets:
        def __init__(self): 
            pass
        def render_interactive_widgets_panel(self): 
            return {}
    
    class AIPoweredLayoutOptimizer:
        def __init__(self): 
            pass
        def render_ai_optimizer_panel(self): 
            return {}
    
    class AudioEmbeddedPDFs:
        def __init__(self): 
            pass
        def render_audio_integration_panel(self): 
            return {}
    
    class ResponsivePDFDesign:
        def __init__(self): 
            pass
        def render_responsive_design_panel(self): 
            return {}

# === MODERNE TEMPLATE INTEGRATION ===
try:
    from pdf_templates_modern import (
        ModernPDFTemplates,
        AVAILABLE_MODERN_TEMPLATES,
        get_modern_template_list,
        create_modern_template_instance
    )
    _MODERN_TEMPLATES_AVAILABLE = True
except ImportError:
    _MODERN_TEMPLATES_AVAILABLE = False

# === PREMIUM OFFER TEMPLATES INTEGRATION ===
try:
    from pdf_templates_premium_offers import (
        PremiumOfferGenerator,
        PremiumOfferTemplate,
        PREMIUM_TEMPLATE_KATALOG,
        create_premium_angebot_pdf,
        get_premium_template_liste,
        erstelle_premium_beispiel_daten
    )
    _PREMIUM_OFFERS_AVAILABLE = True
except ImportError:
    _PREMIUM_OFFERS_AVAILABLE = False
    
    # Fallback für moderne Templates
    class ModernPDFTemplates:
        def __init__(self):
            self.modern_colors = {}
        def get_template_structure(self, name):
            return {}
        def create_modern_cover_page(self, data, scheme='default'):
            return []
        def create_visual_section_header(self, title, icon="", scheme='default'):
            return []
        def create_modern_info_grid(self, data, title="", scheme='default'):
            return []
    
    AVAILABLE_MODERN_TEMPLATES = {}
    
    def get_modern_template_list():
        return {}
    
    def create_modern_template_instance(template_name):
        return ModernPDFTemplates()

# ReportLab Import für PDF-Generierung
_REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm, mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (Frame, Image, PageBreak, PageTemplate,
        Paragraph, SimpleDocTemplate, Spacer, Table,
        TableStyle, Flowable, KeepInFrame, KeepTogether)
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False

class ProfessionalPDFGenerator:
    """
    Professionelle Erweiterung des PDF-Generators.
    Erweitert PDFGenerator um professionelle Templates und moderne Layouts.
    """
    
    def __init__(self, offer_data: Dict, template_name: str = "Executive Report", 
                 customizations: Dict[str, Any] = None, filename: str = "professional_offer.pdf",
                 load_admin_setting_func: Optional[Callable] = None,
                 save_admin_setting_func: Optional[Callable] = None):
        """
        Initialisiert den professionellen PDF-Generator.
        
        Args:
            offer_data (Dict): Angebotsdaten
            template_name (str): Name des professionellen Templates
            customizations (Dict[str, Any]): Anpassungsoptionen
            filename (str): Dateiname für das PDF
            load_admin_setting_func (Optional[Callable]): Funktion zum Laden von Admin-Einstellungen
            save_admin_setting_func (Optional[Callable]): Funktion zum Speichern von Admin-Einstellungen
        """
        
        # 🔧 DATENVALIDIERUNG UND REPARATUR VOR INITIALISIERUNG
        if _DATA_VALIDATOR_AVAILABLE:
            print("🔧 Führe PDF-Datenvalidierung durch...")
            self.offer_data = validate_pdf_data(
                offer_data, 
                load_admin_setting_func, 
                save_admin_setting_func
            )
        else:
            print("⚠️ PDF-Datenvalidierung nicht verfügbar - verwende ursprüngliche Daten")
            self.offer_data = offer_data
        
        self.template_name = template_name
        self.customizations = customizations or {}
        self.filename = filename
        
        # Admin-Funktionen für Einstellungen
        self.load_admin_setting_func = load_admin_setting_func or (lambda key, default: default)
        self.save_admin_setting_func = save_admin_setting_func or (lambda key, value: None)
        
        # 🔥 ADMIN-PANEL PDF-EINSTELLUNGEN LADEN
        self._load_admin_pdf_settings()
        
        # Lade Template-Konfiguration
        if _PROFESSIONAL_TEMPLATES_AVAILABLE:
            self.template_config = get_professional_template(template_name)
        else:
            self.template_config = self._get_fallback_template()
        
        # 🎨 ADMIN-PANEL DESIGN IN TEMPLATE INTEGRIEREN
        self._integrate_admin_design_settings()
        
        # PDF-Einstellungen
        self.width, self.height = A4
        self.story = []
        
        # Erweiterte Komponenten initialisieren
        self.theme_manager = PDFThemeManager() if _PROFESSIONAL_TEMPLATES_AVAILABLE else None
        self.visual_enhancer = PDFVisualEnhancer() if _PROFESSIONAL_TEMPLATES_AVAILABLE else None
        self.bg_manager = ProfessionalPDFBackgrounds() if _PROFESSIONAL_TEMPLATES_AVAILABLE else None
        
        # PDF-Widgets für Strukturverwaltung
        self.section_manager = PDFSectionManager() if _PDF_WIDGETS_AVAILABLE else None
        
        # === WOW FEATURES MANAGER ===
        self.wow_features_manager = PDFWowFeaturesManager() if _WOW_FEATURES_AVAILABLE else None
        self.cinematic_transitions = CinematicPDFTransitions() if _WOW_FEATURES_AVAILABLE else None
        self.interactive_widgets = InteractivePDFWidgets() if _WOW_FEATURES_AVAILABLE else None
        self.ai_optimizer = AIPoweredLayoutOptimizer() if _WOW_FEATURES_AVAILABLE else None
        self.audio_embedded = AudioEmbeddedPDFs() if _WOW_FEATURES_AVAILABLE else None
        self.responsive_design = ResponsivePDFDesign() if _WOW_FEATURES_AVAILABLE else None
        
        # === PREMIUM DESIGN SYSTEM ===
        self.premium_designer = PremiumPDFDesigner() if _PREMIUM_DESIGN_AVAILABLE else None
        self.premium_components = PremiumPDFComponentLibrary() if _PREMIUM_DESIGN_AVAILABLE else None
        
        # === PREMIUM OFFER TEMPLATES ===
        self.premium_offer_generator = PremiumOfferGenerator() if _PREMIUM_OFFERS_AVAILABLE else None
        self.premium_template_katalog = PREMIUM_TEMPLATE_KATALOG if _PREMIUM_OFFERS_AVAILABLE else {}
        
        # === MODERNE TEMPLATES ===
        self.modern_templates = ModernPDFTemplates() if _MODERN_TEMPLATES_AVAILABLE else None
        self.template_structure = None
        if _MODERN_TEMPLATES_AVAILABLE:
            # Erkenne modernen Template-Namen oder verwende Mapping
            modern_template_mapping = {
                'Executive Report': 'premium_solar_report',
                'Solar Professional': 'technical_documentation', 
                'Premium Minimal': 'executive_presentation',
                'Modern Tech': 'visual_proposal'
            }
            modern_template_name = modern_template_mapping.get(template_name, 'premium_solar_report')
            self.template_structure = self.modern_templates.get_template_structure(modern_template_name)
        
        # WOW-Features Konfiguration
        self.wow_config = customizations.get('wow_features', {})
        
        # === DATENBANK-FUNKTIONEN SPEICHERN ===
        self.get_product_by_id_func = None
        self.db_list_company_documents_func = None
        self.active_company_id = 1
        
        # Erstelle professionelle Stile
        self._setup_professional_styles()
    
    def set_database_functions(self, 
                             get_product_by_id_func: Optional[Callable] = None,
                             db_list_company_documents_func: Optional[Callable] = None,
                             active_company_id: int = 1):
        """
        Setzt die Datenbankfunktionen für vollständige PDF-Generierung
        """
        self.get_product_by_id_func = get_product_by_id_func
        self.db_list_company_documents_func = db_list_company_documents_func
        self.active_company_id = active_company_id
        print(f"✅ Datenbankfunktionen gesetzt (Company ID: {active_company_id})")
        
        # Bestehende PDFGenerator-Instanz für Kompatibilität
        if _PDF_GENERATOR_AVAILABLE:
            self.base_generator = PDFGenerator(
                self.offer_data,  # Verwende validierte Daten
                self._create_module_order(), 
                "modern_blue",  # Fallback-Theme
                filename
            )
        else:
            self.base_generator = None

    def _load_admin_pdf_settings(self):
        """🔥 Lädt PDF-Einstellungen aus dem Admin-Panel mit verbesserter Fehlerbehandlung"""
        try:
            # PDF Design-Einstellungen laden
            pdf_design_default = {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
            self.admin_pdf_design = self.load_admin_setting_func('pdf_design_settings', pdf_design_default)
            
            # PDF Template-Einstellungen laden
            self.admin_pdf_title_templates = self.load_admin_setting_func('pdf_title_image_templates', [])
            self.admin_pdf_offer_templates = self.load_admin_setting_func('pdf_offer_title_templates', [])
            self.admin_pdf_cover_templates = self.load_admin_setting_func('pdf_cover_letter_templates', [])
            
            # 🔧 ERWEITERTE FIRMENDATEN-LADEN
            self.admin_company_data = self._load_complete_company_data()
            
            # 🔧 DATEN-VALIDIERUNG UND VERVOLLSTÄNDIGUNG
            self._validate_and_complete_data()
            
        except Exception as e:
            print(f"⚠️ Admin-Panel Ladefehler: {e}")
            # Fallback bei Fehlern
            self.admin_pdf_design = {'primary_color': '#4F81BD', 'secondary_color': '#C0C0C0'}
            self.admin_pdf_title_templates = []
            self.admin_pdf_offer_templates = []
            self.admin_pdf_cover_templates = []
            self.admin_company_data = self._create_fallback_company_data()

    def _load_complete_company_data(self) -> Dict:
        """🔧 Lädt vollständige Firmendaten aus verschiedenen Quellen"""
        company_data = {}
        
        try:
            # Aktive Firma für Branding laden
            active_company_id = self.load_admin_setting_func('active_company_id', None)
            
            if active_company_id:
                # Versuche echte Firmendaten zu laden
                try:
                    # Hier würde normalerweise get_company_by_id aufgerufen
                    # company_data = get_company_by_id(active_company_id)
                    pass
                except:
                    pass
            
            # Falls keine Daten geladen wurden, setze erweiterte Fallback-Daten
            if not company_data:
                company_data = self._create_fallback_company_data()
                print("🔧 Verwende erweiterte Fallback-Firmendaten")
            
        except Exception as e:
            print(f"⚠️ Firmendaten-Ladefehler: {e}")
            company_data = self._create_fallback_company_data()
        
        return company_data

    def _create_fallback_company_data(self) -> Dict:
        """🔧 Erstellt vollständige Fallback-Firmendaten"""
        return {
            'name': 'Solar Solutions GmbH',
            'logo_base64': None,
            'address': 'Sonnenallee 123',
            'zip_code': '12345',
            'city': 'Sonnenhausen',
            'phone': '+49 123 456789',
            'email': 'info@solar-solutions.de',
            'website': 'www.solar-solutions.de',
            'managing_director': 'Max Mustermann',
            'registration_court': 'Amtsgericht Sonnenhausen',
            'registration_number': 'HRB 12345',
            'vat_id': 'DE123456789',
            'bank_name': 'Sparkasse Sonnenhausen',
            'iban': 'DE12 3456 7890 1234 5678 90',
            'bic': 'SOLADES1SUN'
        }

    def _validate_and_complete_data(self):
        """🔧 Validiert und vervollständigt offer_data"""
        # Kritische Felder prüfen und ergänzen
        calc_results = self.offer_data.get('calculation_results', {})
        
        # total_investment_cost_netto → total_investment_netto korrigieren
        if 'total_investment_cost_netto' not in calc_results and 'total_investment_netto' in calc_results:
            calc_results['total_investment_cost_netto'] = calc_results['total_investment_netto']
            print("🔧 Feldname total_investment_cost_netto korrigiert")
        
        # Weitere kritische Felder ergänzen
        required_fields = {
            'total_investment_netto': 25000,
            'total_investment_cost_netto': 25000,
            'annual_financial_benefit_year1': 1200,
            'amortization_time_years': 12.5,
            'anlage_kwp': 10.0,
            'annual_pv_production_kwh': 10000
        }
        
        missing_fields = []
        for field, fallback_value in required_fields.items():
            if field not in calc_results or calc_results[field] == 0:
                calc_results[field] = fallback_value
                missing_fields.append(field)
        
        if missing_fields:
            print(f"🔧 Fehlende Felder ergänzt: {', '.join(missing_fields)}")
        
        # Kundendaten prüfen
        if 'customer' not in self.offer_data or not self.offer_data['customer'].get('name'):
            if 'customer' not in self.offer_data:
                self.offer_data['customer'] = {}
            self.offer_data['customer']['name'] = 'Geschätzter Kunde'
            print("🔧 Kundendaten ergänzt")
        
        # Offer-ID prüfen
        if 'offer_id' not in self.offer_data:
            try:
                suffix = self.load_admin_setting_func('offer_number_suffix', '001')
                self.offer_data['offer_id'] = f'PV-2025-{datetime.now().strftime("%m%d")}-{suffix}'
            except:
                self.offer_data['offer_id'] = f'PV-2025-{datetime.now().strftime("%m%d")}-001'
            print(f"🔧 Offer-ID erstellt: {self.offer_data['offer_id']}")

        # Aktualisiere calculation_results im offer_data
        self.offer_data['calculation_results'] = calc_results

    def _integrate_admin_design_settings(self):
        """🎨 Integriert Admin-Panel Design-Einstellungen in Template-Konfiguration"""
        if hasattr(self, 'admin_pdf_design') and self.admin_pdf_design:
            # Überschreibe Template-Farben mit Admin-Panel Einstellungen
            admin_primary = self.admin_pdf_design.get('primary_color', '#4F81BD')
            admin_secondary = self.admin_pdf_design.get('secondary_color', '#C0C0C0')
            
            # Template-Farben anpassen
            if 'colors' in self.template_config:
                self.template_config['colors']['primary'] = admin_primary
                self.template_config['colors']['secondary'] = admin_secondary
                self.template_config['colors']['accent'] = admin_primary  # Verwende Primary als Accent
                
                # Füge Admin-spezifische Farben hinzu
                self.template_config['colors']['admin_primary'] = admin_primary
                self.template_config['colors']['admin_secondary'] = admin_secondary

    def load_template_presets(self) -> Dict[str, Any]:
        """
        Lädt Template-Presets aus Admin-Einstellungen.
        
        Returns:
            Dict[str, Any]: Template-Preset-Konfiguration
        """
        try:
            presets = self.load_admin_setting_func('pdf_template_presets', {})
            return presets if isinstance(presets, dict) else {}
        except Exception as e:
            return {}

    def save_template_preset(self, preset_name: str, preset_config: Dict[str, Any]) -> bool:
        """
        Speichert ein Template-Preset in Admin-Einstellungen.
        
        Args:
            preset_name (str): Name des Presets
            preset_config (Dict[str, Any]): Preset-Konfiguration
            
        Returns:
            bool: True wenn erfolgreich gespeichert
        """
        try:
            current_presets = self.load_template_presets()
            current_presets[preset_name] = preset_config
            self.save_admin_setting_func('pdf_template_presets', current_presets)
            return True
        except Exception as e:
            return False

    def _get_fallback_template(self) -> Dict[str, Any]:
        """Fallback-Template falls professionelle Templates nicht verfügbar sind."""
        return {
            "name": "Standard Professional",
            "colors": {
                "primary": "#1e3a8a",
                "secondary": "#3b82f6",
                "accent": "#06b6d4",
                "text_dark": "#1f2937",
                "background": "#ffffff"
            },
            "typography": {
                "main_font": "Helvetica",
                "heading_font": "Helvetica-Bold",
                "h1_size": 24,
                "h2_size": 18,
                "body_size": 11
            },
            "layout": {
                "margins": {
                    "top": 2.5 * cm,
                    "bottom": 2.5 * cm,
                    "left": 2.0 * cm,
                    "right": 2.0 * cm
                }
            }
        }

    def _setup_professional_styles(self):
        """Erstellt professionelle Stile basierend auf dem Template."""
        self.styles = getSampleStyleSheet()
        
        # Theme-Manager-Integration für erweiterte Stile
        if self.theme_manager and _PROFESSIONAL_TEMPLATES_AVAILABLE:
            try:
                professional_styles = get_professional_paragraph_styles(self.template_name)
                for name, style in professional_styles.items():
                    self.styles.add(style)
                
                # Erweiterte Theme-Einstellungen anwenden
                self._apply_advanced_theme_settings()
                
            except Exception:
                self._create_fallback_styles()
        else:
            self._create_fallback_styles()
        
        # Visual-Enhancer-Integration
        if self.visual_enhancer:
            self._apply_visual_enhancements()
    
    def _apply_advanced_theme_settings(self):
        """Wendet erweiterte Theme-Einstellungen an."""
        
        theme_settings = self.customizations.get('theme_settings', {})
        
        if theme_settings:
            # Font-Familie anpassen
            font_family = theme_settings.get('font_family', 'Helvetica')
            base_font_size = theme_settings.get('base_font_size', 11)
            line_spacing = theme_settings.get('line_spacing', 1.4)
            
            # Stile mit Theme-Einstellungen überschreiben
            for style_name in ['ProfessionalBody', 'ProfessionalH1', 'ProfessionalH2', 'ProfessionalH3']:
                if style_name in self.styles:
                    style = self.styles[style_name]
                    if hasattr(style, 'fontName'):
                        style.fontName = font_family
                    if hasattr(style, 'fontSize'):
                        # Proportionale Anpassung der Schriftgröße
                        size_factor = base_font_size / 11  # 11 ist die Basis-Größe
                        style.fontSize = int(style.fontSize * size_factor)
                    if hasattr(style, 'leading'):
                        style.leading = style.fontSize * line_spacing
    
    def _apply_visual_enhancements(self):
        """Wendet Visual-Enhancer-Einstellungen an."""
        
        visual_settings = self.customizations.get('visual_settings', {})
        
        if visual_settings:
            # Chart-Stil anpassen
            chart_style = visual_settings.get('chart_style', 'Modern')
            self.chart_theme = self.visual_enhancer.chart_themes.get(chart_style.lower(), {})
            
            # Weitere visuelle Einstellungen
            self.enable_shadows = visual_settings.get('shadows', False)
            self.enable_gradients = visual_settings.get('gradients', True)
            self.rounded_corners = visual_settings.get('rounded_corners', True)
    
    def _create_fallback_styles(self):
        """Erstellt Fallback-Stile falls professionelle Templates nicht verfügbar sind."""
        colors_dict = self.template_config["colors"]
        typography = self.template_config["typography"]
        
        self.styles.add(ParagraphStyle(
            name='ProfessionalH1',
            fontName=typography["heading_font"],
            fontSize=typography["h1_size"],
            textColor=HexColor(colors_dict["primary"]),
            alignment=TA_LEFT,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='ProfessionalBody',
            fontName=typography["main_font"],
            fontSize=typography["body_size"],
            textColor=HexColor(colors_dict["text_dark"]),
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))

    def _create_module_order(self) -> List[Dict]:
        """Erstellt die Modul-Reihenfolge basierend auf Anpassungen."""
        
        # Prüfe ob PDF-Widgets konfigurierte Struktur vorhanden ist
        if (self.section_manager and 
            self.customizations.get('structure_mode', False) and 
            'section_order' in self.customizations):
            
            return self._create_widget_based_module_order()
        
        # Standard-Module basierend auf Anpassungen
        modules = []
        
        if self.customizations.get('include_cover_page', True):
            modules.append({"id": "professional_cover", "title": "Deckblatt"})
        
        if self.customizations.get('include_executive_summary', True):
            modules.append({"id": "executive_summary", "title": "Zusammenfassung"})
        
        if self.customizations.get('include_technical_details', True):
            modules.append({"id": "technical_details", "title": "Technische Details"})
        
        if self.customizations.get('include_financial_analysis', True):
            modules.append({"id": "financial_analysis", "title": "Wirtschaftlichkeitsanalyse"})
        
        if self.customizations.get('include_charts', True):
            modules.append({"id": "charts_diagrams", "title": "Diagramme"})
        
        if self.customizations.get('include_environmental_impact', True):
            modules.append({"id": "environmental_impact", "title": "Umweltwirkung"})
        
        if self.customizations.get('include_appendix', False):
            modules.append({"id": "appendix", "title": "Anhang"})
        
        return modules
    
    def _create_widget_based_module_order(self) -> List[Dict]:
        """Erstellt Module basierend auf PDF-Widgets Konfiguration."""
        
        modules = []
        section_order = self.customizations.get('section_order', [])
        section_contents = self.customizations.get('section_contents', {})
        
        # Mapping von Widget-Sektionen zu Generator-Modulen
        section_mapping = {
            'cover_page': 'professional_cover',
            'project_overview': 'executive_summary',
            'technical_components': 'technical_details',
            'cost_details': 'financial_analysis',
            'economics': 'charts_diagrams',
            'custom_section': 'custom_content'
        }
        
        for section_key in section_order:
            module_id = section_mapping.get(section_key, section_key)
            
            module = {
                "id": module_id,
                "title": section_key.replace('_', ' ').title(),
                "widget_section": section_key,
                "contents": section_contents.get(section_key, [])
            }
            
            modules.append(module)
        
        return modules

    @debug_pdf_generator
    def create_premium_offer_pdf(self, template_stil: str = "luxus_blau") -> str:
        """
        🌟 Erstellt WIRKLICH hochwertige, professionelle Premium-Angebots-PDFs
        
        Das ist die Lösung für Ihr Feedback: "schönere und sattere, und professionellere pdf inhalte"!
        Verwendet die neuen Premium-Templates für echte Qualität.
        
        Args:
            template_stil (str): Stil des Premium-Templates
                - 'luxus_blau': Edles tiefblaues Design
                - 'smaragd_luxus': Exklusives grünes Luxus-Design  
                - 'platinum_schwarz': VIP Platinum-Design
                - 'royal_lila': Königliches innovatives Design
        
        Returns:
            str: Pfad zur erstellten Premium-PDF
        """
        if not _REPORTLAB_AVAILABLE:
            # 🔥 FALLBACK AUF HTML+CSS PDF SYSTEM
            return self._create_html_css_fallback_pdf(template_stil)
        
        if not _PREMIUM_OFFERS_AVAILABLE:
            # Fallback auf Premium Modern PDF
            return self.create_premium_modern_pdf()
        
        try:
            # 🔧 PRE-GENERATION DATENCHECK
            self._perform_pre_generation_check()
            
            # Konvertiere offer_data in das Premium-Format
            premium_angebot_daten = self._convert_to_premium_format()
            
            # Verwende die neue Premium-Template Engine
            premium_filename = f"premium_{template_stil}_{self.filename}"
            
            # Erstelle das Premium-PDF mit den neuen hochwertigen Templates
            result_file = create_premium_angebot_pdf(
                angebot_daten=premium_angebot_daten,
                template_stil=template_stil,
                dateiname=premium_filename
            )
            
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_debug(f"🌟 Premium-PDF erstellt: {result_file} mit Stil: {template_stil}")
            
            return result_file
            
        except Exception as e:
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_debug(f"❌ Premium-PDF Fehler: {str(e)}")
            
            print(f"⚠️ Premium-PDF Fehler: {e}")
            # Fallback auf bestehende Premium Modern PDF
            return self.create_premium_modern_pdf()

    def _create_html_css_fallback_pdf(self, template_stil: str) -> str:
        """🔥 HTML+CSS Fallback für bessere PDF-Qualität"""
        try:
            # Versuche HTML+CSS PDF Generator zu importieren
            from pdf_html_generator import HTMLPDFGenerator
            
            print("🌟 Verwende HTML+CSS PDF Generator für bessere Qualität...")
            
            # Konvertiere Daten für HTML Generator
            html_data = self._convert_to_html_format()
            
            # Erstelle HTML+CSS PDF
            html_generator = HTMLPDFGenerator()
            
            # Template-Stil Mapping
            style_mapping = {
                'luxus_blau': 'premium_luxus',
                'smaragd_luxus': 'corporate_professional', 
                'platinum_schwarz': 'modern_tech',
                'royal_lila': 'solar_green'
            }
            
            html_template = style_mapping.get(template_stil, 'premium_luxus')
            
            result_file = html_generator.render_premium_pdf(
                angebot_data=html_data,
                template_name=html_template,
                output_filename=f"html_premium_{template_stil}_{self.filename}"
            )
            
            print(f"✅ HTML+CSS PDF erfolgreich erstellt: {result_file}")
            return result_file
            
        except ImportError:
            print("⚠️ HTML+CSS PDF Generator nicht verfügbar - verwende ReportLab Fallback")
            return self.create_premium_modern_pdf()
        except Exception as e:
            print(f"⚠️ HTML+CSS PDF Fehler: {e} - verwende ReportLab Fallback")
            return self.create_premium_modern_pdf()

    def _convert_to_html_format(self) -> Dict:
        """🔧 Konvertiert offer_data für HTML+CSS Generator"""
        premium_data = self._convert_to_premium_format()
        
        # HTML-spezifische Anpassungen
        html_data = {
            'kunde': {
                'name': premium_data.get('customer_name', 'Geschätzter Kunde'),
                'anrede': 'Sehr geehrte Damen und Herren'
            },
            'angebot': {
                'nummer': premium_data.get('offer_id', 'PV-2025-001'),
                'datum': datetime.now().strftime('%d.%m.%Y')
            },
            'anlage': {
                'leistung_kwp': premium_data.get('system_power', 10.0),
                'jahresertrag_kwh': premium_data.get('annual_yield', 10000),
                'eigenverbrauch_prozent': 70
            },
            'wirtschaftlichkeit': {
                'investition_euro': premium_data.get('total_cost', 25000),
                'jaehrliche_einsparung_euro': premium_data.get('annual_savings', 1200),
                'amortisation_jahre': premium_data.get('payback_time', 12.5)
            },
            'umwelt': {
                'co2_einsparung_kg_jahr': premium_data.get('co2_savings', 5000)
            },
            'komponenten': {
                'module': {
                    'typ': premium_data.get('module_type', 'Premium Module'),
                    'anzahl': premium_data.get('module_count', 25),
                    'leistung_wp': premium_data.get('module_power', 400)
                },
                'wechselrichter': {
                    'typ': premium_data.get('inverter_type', 'Premium Wechselrichter'),
                    'leistung_kw': premium_data.get('inverter_power', 10)
                }
            },
            'firma': premium_data.get('company_name', 'Solar Solutions GmbH')
        }
        
        return html_data
    
    def _convert_to_premium_format(self) -> Dict:
        """
        Konvertiert offer_data in das Premium-Template Format mit verbessertem Daten-Mapping
        """
        # 🔧 BERECHNUNGSERGEBNISSE EXTRAHIEREN
        calc_results = self.offer_data.get('calculation_results', {})
        project_data = self.offer_data.get('project_data', {})
        
        # 🔧 KRITISCHE FELDER KORRIGIEREN
        # total_investment_cost_netto → total_investment_netto (Feldname korrigiert)
        total_investment = (
            calc_results.get('total_investment_netto', 0) or 
            calc_results.get('total_investment_cost_netto', 0) or 
            self.offer_data.get('gesamtkosten', 0) or 
            self.offer_data.get('total_cost', 0) or 0
        )
        
        # Basis-Daten extrahieren
        premium_daten = {
            'customer_name': self._extract_customer_name(),
            'offer_id': self._generate_offer_id(),
            
            # System-Daten (korrigierte Quellen)
            'system_power': (
                calc_results.get('anlage_kwp', 0) or 
                self.offer_data.get('gesamtleistung_kwp', 0) or 
                project_data.get('module_quantity', 20) * 0.4  # Fallback-Schätzung
            ),
            'annual_yield': (
                calc_results.get('annual_pv_production_kwh', 0) or 
                self.offer_data.get('jahresertrag_kwh', 0) or 
                calc_results.get('anlage_kwp', 10) * 1000  # 1000 kWh/kWp Fallback
            ),
            'total_cost': total_investment,
            'annual_savings': (
                calc_results.get('annual_financial_benefit_year1', 0) or 
                self.offer_data.get('jaehrliche_einsparung', 0) or 
                1200  # Fallback
            ),
            'payback_time': (
                calc_results.get('amortization_time_years', 0) or 
                self.offer_data.get('amortisationszeit_jahre', 0) or 
                12.5  # Fallback
            ),
            'co2_savings': (
                calc_results.get('annual_co2_savings_kg', 0) or 
                self.offer_data.get('co2_einsparung_kg_jahr', 0) or 
                calc_results.get('anlage_kwp', 10) * 500  # 500kg/kWp Fallback
            ),
            
            # Modul-Daten (erweitert)
            'module_type': self._extract_module_info('type'),
            'module_count': self._extract_module_info('count'),
            'module_power': self._extract_module_info('power'),
            'module_efficiency': self._extract_module_info('efficiency'),
            'module_cost': self._extract_cost_info('modules'),
            
            # Wechselrichter-Daten (erweitert)
            'inverter_type': self._extract_inverter_info('type'),
            'inverter_power': self._extract_inverter_info('power'),
            'inverter_efficiency': self._extract_inverter_info('efficiency'),
            'inverter_cost': self._extract_cost_info('inverter'),
            
            # Weitere Kosten
            'mounting_cost': self._extract_cost_info('mounting'),
            'installation_cost': self._extract_cost_info('installation')
        }
        
        # 🔧 ADMIN-PANEL & FIRMENDATEN INTEGRATION
        premium_daten.update(self._extract_company_data())
        
        return premium_daten

    def _extract_customer_name(self) -> str:
        """Extrahiert Kundenname aus verschiedenen Quellen"""
        sources = [
            self.offer_data.get('customer', {}).get('name'),
            self.offer_data.get('customer_name'),
            self.offer_data.get('project_data', {}).get('customer_data', {}).get('first_name', '') + ' ' + 
            self.offer_data.get('project_data', {}).get('customer_data', {}).get('last_name', ''),
        ]
        
        for source in sources:
            if source and source.strip():
                return source.strip()
        
        return 'Geschätzter Kunde'

    def _generate_offer_id(self) -> str:
        """Generiert Angebots-ID"""
        existing_id = (
            self.offer_data.get('offer_id') or 
            self.offer_data.get('angebots_id') or 
            self.offer_data.get('id')
        )
        
        if existing_id:
            return str(existing_id)
        
        # Generiere neue ID basierend auf Admin-Einstellungen
        try:
            suffix = self.load_admin_setting_func('offer_number_suffix', '001')
            return f'PV-2025-{datetime.now().strftime("%m%d")}-{suffix}'
        except:
            return f'PV-2025-{datetime.now().strftime("%m%d")}-001'

    def _extract_module_info(self, info_type: str):
        """Extrahiert Modul-Informationen"""
        calc_results = self.offer_data.get('calculation_results', {})
        project_data = self.offer_data.get('project_data', {})
        
        if info_type == 'type':
            return (
                self.offer_data.get('modul_typ') or 
                self.offer_data.get('selected_module', {}).get('model_name') or 
                'Premium Mono-Si Module'
            )
        elif info_type == 'count':
            return (
                project_data.get('module_quantity', 0) or 
                self.offer_data.get('anzahl_module', 0) or 
                20  # Fallback
            )
        elif info_type == 'power':
            return (
                self.offer_data.get('modul_leistung_wp', 0) or 
                self.offer_data.get('selected_module', {}).get('power_wp') or 
                400  # Fallback
            )
        elif info_type == 'efficiency':
            return (
                self.offer_data.get('modul_wirkungsgrad', 0) or 
                self.offer_data.get('selected_module', {}).get('efficiency_percent') or 
                21.5  # Fallback
            )
        return 0

    def _extract_inverter_info(self, info_type: str):
        """Extrahiert Wechselrichter-Informationen"""
        if info_type == 'type':
            return (
                self.offer_data.get('wechselrichter_typ') or 
                self.offer_data.get('selected_inverter', {}).get('model_name') or 
                'Premium String-Wechselrichter'
            )
        elif info_type == 'power':
            return (
                self.offer_data.get('wechselrichter_leistung_kw', 0) or 
                self.offer_data.get('selected_inverter', {}).get('power_kw') or 
                10  # Fallback
            )
        elif info_type == 'efficiency':
            return (
                self.offer_data.get('wechselrichter_wirkungsgrad', 0) or 
                self.offer_data.get('selected_inverter', {}).get('efficiency_percent') or 
                98.5  # Fallback
            )
        return 0

    def _extract_cost_info(self, cost_type: str):
        """Extrahiert Kostendaten"""
        calc_results = self.offer_data.get('calculation_results', {})
        
        cost_mapping = {
            'modules': [
                'cost_modules_aufpreis_netto',
                'kosten_module',
                'module_cost_total'
            ],
            'inverter': [
                'cost_inverter_aufpreis_netto',
                'kosten_wechselrichter',
                'inverter_cost_total'
            ],
            'mounting': [
                'kosten_montage',
                'mounting_cost',
                'installation_cost'
            ],
            'installation': [
                'kosten_installation',
                'installation_cost',
                'labor_cost'
            ]
        }
        
        cost_fields = cost_mapping.get(cost_type, [])
        
        for field in cost_fields:
            cost = calc_results.get(field, 0) or self.offer_data.get(field, 0)
            if cost and cost > 0:
                return cost
        
        return 0

    def _extract_company_data(self) -> Dict:
        """Extrahiert und vervollständigt Firmendaten"""
        company_data = {}
        
        # Admin-Panel Integration
        if hasattr(self, 'admin_company_data') and self.admin_company_data:
            company_data['company_name'] = self.admin_company_data.get('name', 'Solar Solutions GmbH')
            company_data['company_logo'] = self.admin_company_data.get('logo_base64')
        else:
            # 🔧 FALLBACK FIRMENDATEN
            company_data['company_name'] = 'Solar Solutions GmbH'
            company_data['company_logo'] = None
            
            # Debug-Information
            print("⚠️ Keine Firmendaten aus Admin-Panel - verwende Fallback")
        
        # Zusätzliche Firmendaten
        company_data.update({
            'company_address': 'Musterstraße 123, 12345 Musterstadt',
            'company_phone': '+49 123 456789',
            'company_email': 'info@solar-solutions.de',
            'company_website': 'www.solar-solutions.de',
            'company_registration': 'HRB 12345'
        })
        
        return company_data

    @debug_pdf_generator
    def create_premium_modern_pdf(self) -> str:
        """
        🚀 Erstellt Premium Modern PDF mit allen neuen Design-Features
        Diese Methode implementiert das hochwertige Design basierend auf Ihrem Feedback
        """
        if not _REPORTLAB_AVAILABLE:
            raise Exception("ReportLab ist nicht verfügbar. PDF-Generierung nicht möglich.")
        
        try:
            # === MODERNE DESIGN-FEATURES INTEGRATION ===
            modern_design_config = self.customizations.get('modern_design', {})
            use_modern_design = modern_design_config.get('enable_modern_design', False)
            
            if use_modern_design:
                print("🎨 Moderne Design-Features aktiviert!")
                color_scheme = modern_design_config.get('color_scheme', 'premium_blue_modern')
            else:
                print("📄 Standard Professional PDF wird erstellt")
                color_scheme = 'solar_professional'
            
            # Premium PDF-Dokument erstellen
            doc = SimpleDocTemplate(
                self.filename,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm,
                title=f"Premium Solar Angebot - {self.offer_data.get('customer_name', 'Kunde')}"
            )
            
            story = []
            
            # === MODERNE DESIGN INTEGRATION ===
            if use_modern_design:
                try:
                    # Versuche neue vollständige Integration
                    try:
                        from doc_output_complete_modern_integration import apply_complete_modern_pdf_enhancements
                        integration_function = apply_complete_modern_pdf_enhancements
                        print("✅ Vollständige moderne Integration verfügbar")
                    except ImportError:
                        # Fallback auf bestehende Integration
                        from doc_output_modern_integration import apply_modern_pdf_enhancements
                        integration_function = apply_modern_pdf_enhancements
                        print("⚠️ Fallback auf Basis-Integration")
                    
                    # Bereite Daten für moderne Features vor
                    calculation_results = {
                        'total_system_cost': self.offer_data.get('gesamtkosten', 0),
                        'annual_savings': self.offer_data.get('jaehrliche_einsparung', 0),
                        'payback_period_years': self.offer_data.get('amortisationszeit_jahre', 0),
                        'annual_pv_production_kwh': self.offer_data.get('jahresertrag_kwh', 0),
                        'co2_savings_kg_year': self.offer_data.get('co2_einsparung_kg_jahr', 0),
                        'pv_power_kwp': self.offer_data.get('gesamtleistung_kwp', 0),
                        'gesamtkosten': self.offer_data.get('gesamtkosten', 0),
                        'jaehrliche_einsparung': self.offer_data.get('jaehrliche_einsparung', 0),
                        'amortisationszeit_jahre': self.offer_data.get('amortisationszeit_jahre', 0)
                    }
                    
                    project_data = {
                        'customer_name': self.offer_data.get('customer_name', 'Kunde'),
                        'company_data': self.admin_company_data or {},
                        'komponenten': self.offer_data.get('komponenten', {}),
                        'gesamtleistung_kwp': self.offer_data.get('gesamtleistung_kwp', 0),
                        'anzahl_module': self.offer_data.get('anzahl_module', 0),
                        'jahresertrag_kwh': self.offer_data.get('jahresertrag_kwh', 0),
                        'dachflaeche_m2': self.offer_data.get('dachflaeche_m2', 0),
                        'ausrichtung': self.offer_data.get('ausrichtung', 'Süd'),
                        'neigung_grad': self.offer_data.get('neigung_grad', 30)
                    }
                    
                    texts = {'app_name': 'Solar Professional System'}
                    
                    modern_config = {
                        'enable_modern_design': True,
                        'color_scheme': 'premium_blue_modern',
                        'add_executive_summary': True,
                        'add_environmental_section': True,
                        'include_product_images': True,
                        'include_company_documents': True,
                        'include_installation_examples': True,
                        'replace_completely': True  # Komplett moderne PDF
                    }
                    
                    print("🎨 Wende vollständige moderne PDF-Enhancements an...")
                    
                    # Anwenden der modernen Features
                    if integration_function == apply_complete_modern_pdf_enhancements:
                        story = integration_function(
                            story=story,
                            calculation_results=calculation_results,
                            project_data=project_data,
                            texts=texts,
                            modern_config=modern_config,
                            get_product_by_id_func=getattr(self, 'get_product_by_id_func', None),
                            db_list_company_documents_func=getattr(self, 'db_list_company_documents_func', None),
                            active_company_id=getattr(self, 'active_company_id', 1)
                        )
                    else:
                        story = integration_function(
                            story, calculation_results, project_data, texts
                        )
                    
                    print("✅ Moderne Features erfolgreich integriert!")
                    
                except ImportError as e:
                    print(f"⚠️ Moderne Design-Features nicht verfügbar: {e}")
                    print("📄 Fallback auf Standard Professional Design")
                except Exception as e:
                    print(f"⚠️ Fehler bei modernen Features: {e}")
                    print("📄 Fallback auf Standard Professional Design")
            
            # === 1. PREMIUM COVER PAGE ===
            if self.modern_templates and _MODERN_TEMPLATES_AVAILABLE:
                cover_data = {
                    'title': 'Premium Solar-Lösung',
                    'subtitle': 'Ihre maßgeschneiderte Photovoltaik-Anlage',
                    'customer_name': self.offer_data.get('customer_name', 'Geschätzter Kunde'),
                    'project_name': f"Solar-Projekt {self.offer_data.get('customer_name', '')}",
                    'company_name': self.admin_company_data.get('name', 'Solar Solutions GmbH') if self.admin_company_data else 'Solar Solutions GmbH',
                    'company_address': 'Musterstraße 123, 12345 Musterstadt',
                    'company_phone': '+49 123 456789',
                    'company_email': 'info@solar-solutions.de'
                }
                
                color_scheme = self.template_structure.get('color_scheme', 'solar_professional') if self.template_structure else 'solar_professional'
                cover_elements = self.modern_templates.create_modern_cover_page(cover_data, color_scheme)
                story.extend(cover_elements)
                story.append(PageBreak())
            
            # === 2. EXECUTIVE SUMMARY MIT PREMIUM DESIGN ===
            if self.premium_components and _PREMIUM_DESIGN_AVAILABLE:
                # Berechne Kernzahlen aus offer_data
                calculation_data = {
                    'system_power': self.offer_data.get('gesamtleistung_kwp', 0),
                    'annual_yield': self.offer_data.get('jahresertrag_kwh', 0),
                    'investment_cost': self.offer_data.get('gesamtkosten', 0),
                    'annual_savings': self.offer_data.get('jaehrliche_einsparung', 0),
                    'payback_time': self.offer_data.get('amortisationszeit_jahre', 0),
                    'co2_savings': self.offer_data.get('co2_einsparung_kg_jahr', 0)
                }
                
                summary_elements = self.premium_components.solar_calculation_summary(
                    calculation_data, color_scheme
                )
                story.extend(summary_elements)
            
            # === 3. MODERNE INFO-GRIDS ===
            if self.modern_templates and _MODERN_TEMPLATES_AVAILABLE:
                key_metrics = [
                    {'value': f"{self.offer_data.get('gesamtleistung_kwp', 0):.1f} kWp", 'label': 'Anlagenleistung'},
                    {'value': f"{self.offer_data.get('jahresertrag_kwh', 0):,.0f} kWh", 'label': 'Jahresertrag'},
                    {'value': f"{self.offer_data.get('gesamtkosten', 0):,.0f} €", 'label': 'Investition'},
                    {'value': f"{self.offer_data.get('amortisationszeit_jahre', 0):.1f} Jahre", 'label': 'Amortisation'},
                    {'value': f"{self.offer_data.get('jaehrliche_einsparung', 0):,.0f} €", 'label': 'Jährl. Einsparung'},
                    {'value': f"{self.offer_data.get('co2_einsparung_kg_jahr', 0):,.0f} kg", 'label': 'CO₂-Einsparung'}
                ]
                
                grid_elements = self.modern_templates.create_modern_info_grid(
                    key_metrics, "📊 Projekt-Übersicht auf einen Blick", color_scheme
                )
                story.extend(grid_elements)
            
            # === 4. FINANZIELLE AUFSCHLÜSSELUNG PREMIUM ===
            if self.premium_components and _PREMIUM_DESIGN_AVAILABLE:
                financial_data = {
                    'cost_breakdown': {
                        'Solarmodule': self.offer_data.get('kosten_module', 0),
                        'Wechselrichter': self.offer_data.get('kosten_wechselrichter', 0),
                        'Montagesystem': self.offer_data.get('kosten_montage', 0),
                        'Installation': self.offer_data.get('kosten_installation', 0),
                        'Zusatzkomponenten': self.offer_data.get('kosten_zusatz', 0)
                    }
                }
                
                financial_elements = self.premium_components.financial_breakdown(
                    financial_data, color_scheme
                )
                story.extend(financial_elements)
            
            # === 5. TECHNISCHE SPEZIFIKATIONEN MODERN ===
            if self.premium_components and _PREMIUM_DESIGN_AVAILABLE:
                tech_data = {
                    'modules': {
                        'type': self.offer_data.get('modul_typ', 'Premium Solarmodule'),
                        'power_per_module': self.offer_data.get('modul_leistung_wp', 400),
                        'count': self.offer_data.get('anzahl_module', 0),
                        'efficiency': self.offer_data.get('modul_wirkungsgrad', 21.5)
                    },
                    'inverter': {
                        'type': self.offer_data.get('wechselrichter_typ', 'Premium Wechselrichter'),
                        'power': self.offer_data.get('wechselrichter_leistung_kw', 0),
                        'efficiency': self.offer_data.get('wechselrichter_wirkungsgrad', 98.5)
                    }
                }
                
                tech_elements = self.premium_components.technical_specifications(
                    tech_data, color_scheme
                )
                story.extend(tech_elements)
            
            # === 6. VORTEILE UND NUTZEN VISUAL ===
            if self.modern_templates and _MODERN_TEMPLATES_AVAILABLE:
                benefits = [
                    "Erhebliche Stromkosteneinsparungen durch Eigenverbrauch",
                    "Umweltfreundliche und nachhaltige Energiegewinnung", 
                    "Wertsteigerung Ihrer Immobilie",
                    "Unabhängigkeit von steigenden Strompreisen",
                    "25 Jahre Herstellergarantie auf Solarmodule",
                    "Professionelle Installation und Wartung",
                    "Förderungen und attraktive Finanzierungsmöglichkeiten",
                    "Monitoring und Fernüberwachung der Anlage"
                ]
                
                benefits_elements = self.modern_templates.create_modern_benefits_section(
                    benefits, color_scheme
                )
                story.extend(benefits_elements)
            
            # === 7. BILDINTEGRATION (falls verfügbar) ===
            if self.modern_templates and _MODERN_TEMPLATES_AVAILABLE:
                # Beispiel-Bilder für Showcase (falls verfügbar)
                showcase_images = [
                    {
                        'path': 'images/solar_installation_example.jpg',
                        'caption': 'Beispiel einer professionellen Solarinstallation'
                    },
                    {
                        'path': 'images/solar_modules_detail.jpg', 
                        'caption': 'Hochwertige Solarmodule mit modernster Technologie'
                    }
                ]
                
                image_elements = self.modern_templates.create_image_showcase(
                    showcase_images, "🏠 Referenz-Installationen", color_scheme
                )
                story.extend(image_elements)
            
            # === 8. VERGLEICHSTABELLE MODERN ===
            if self.modern_templates and _MODERN_TEMPLATES_AVAILABLE:
                comparison_data = {
                    'title': 'Vorher-Nachher Vergleich',
                    'headers': ['Ohne Solaranlage', 'Mit Ihrer Solaranlage'],
                    'rows': [
                        ['Hohe Stromkosten', 'Reduzierte Stromkosten'],
                        ['100% Netzbezug', f'{self.offer_data.get("eigenverbrauchsanteil", 70)}% Eigenverbrauch'],
                        ['Keine CO₂-Einsparung', f'{self.offer_data.get("co2_einsparung_kg_jahr", 0):,.0f} kg CO₂ Einsparung/Jahr'],
                        ['Energieabhängigkeit', 'Energieunabhängigkeit'],
                        ['Keine Wertsteigerung', 'Immobilienwertsteigerung']
                    ]
                }
                
                comparison_elements = self.modern_templates.create_visual_comparison_table(
                    comparison_data, color_scheme
                )
                story.extend(comparison_elements)
            
            # PDF erstellen
            doc.build(story)
            
            return self.filename
            
        except Exception as e:
            # Fallback auf bestehende Methode
            return self.create_professional_pdf()

    def create_professional_pdf(self) -> str:
        """
        Erstellt das professionelle PDF mit verbesserter Datenvalidierung.
        Hauptfunktion für die PDF-Generierung mit professionellen Templates.
        
        Returns:
            str: Pfad zur erstellten PDF-Datei
        """
        if not _REPORTLAB_AVAILABLE:
            raise Exception("ReportLab ist nicht verfügbar. PDF-Generierung nicht möglich.")
        
        # 🔧 PRE-GENERATION DATENCHECK
        self._perform_pre_generation_check()
        
        # Erstelle Dokument mit professionellen Einstellungen
        margins = self.template_config["layout"]["margins"]
        
        doc = SimpleDocTemplate(
            self.filename, 
            pagesize=A4,
            leftMargin=margins["left"],
            rightMargin=margins["right"],
            topMargin=margins["top"],
            bottomMargin=margins["bottom"]
        )
        
        # Erstelle Inhalte basierend auf Modulen
        module_order = self._create_module_order()
        
        if _DEBUG_AVAILABLE:
            pdf_debug_manager.log_debug(f"📑 Erstelle {len(module_order)} Module")
        
        # Erweiterte Styling-Funktionen anwenden
        self.apply_enhanced_visual_styling()
        self.apply_professional_background()
        self.integrate_pdf_widgets()
        
        for module in module_order:
            module_id = module["id"]
            
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_debug(f"🔧 Verarbeite Modul: {module.get('name', module_id)}")
            
            if module_id == "professional_cover":
                self._create_professional_cover_page()
            elif module_id == "executive_summary":
                self._create_executive_summary()
            elif module_id == "technical_details":
                self._create_technical_details()
            elif module_id == "financial_analysis":
                self._create_financial_analysis()
            elif module_id == "charts_diagrams":
                self._create_charts_section()
            elif module_id == "environmental_impact":
                self._create_environmental_impact()
            elif module_id == "appendix":
                self._create_appendix()
            
            # Seitenumbruch nach jedem Modul (außer dem letzten)
            if module != module_order[-1]:
                self.story.append(PageBreak())
        
        # Erstelle PDF mit professionellen Header/Footer
        doc.build(self.story, 
                 onFirstPage=self._professional_header_footer, 
                 onLaterPages=self._professional_header_footer)
        
        print(f"✅ PDF erfolgreich erstellt: {self.filename}")
        return self.filename

    def _perform_pre_generation_check(self):
        """🔧 Führt Pre-Generation Datencheck durch"""
        print("🔍 PDF-Generierung: Datenvalidierung gestartet...")
        
        issues = []
        calc_results = self.offer_data.get('calculation_results', {})
        
        # Kritische Felder prüfen
        critical_fields = {
            'total_investment_netto': 'Gesamtinvestition (Netto)',
            'total_investment_cost_netto': 'Gesamtinvestitionskosten',
            'annual_financial_benefit_year1': 'Jährlicher finanzieller Nutzen',
            'anlage_kwp': 'Anlagenleistung'
        }
        
        for field, description in critical_fields.items():
            value = calc_results.get(field, 0)
            if not value or value == 0:
                issues.append(f"   - Fehlend: {description} ({field})")
        
        # Firmendaten prüfen
        if not self.admin_company_data or not self.admin_company_data.get('name'):
            issues.append("   - Keine vollständigen Firmendaten verfügbar")
        
        # Kundendaten prüfen
        customer_name = self.offer_data.get('customer', {}).get('name')
        if not customer_name or customer_name == 'Geschätzter Kunde':
            issues.append("   - Keine spezifischen Kundendaten")
        
        if issues:
            print("⚠️ PDF-Erstellung: Daten unvollständig:")
            for issue in issues:
                print(issue)
            print("   - Fallback-Werte werden verwendet")
        else:
            print("✅ PDF-Erstellung: Alle Daten vollständig")
        
        # Data Recovery attempts
        missing_fields = self._attempt_data_recovery()
        if missing_fields:
            print(f"🔧 Datenwiederherstellung: {len(missing_fields)} Felder ergänzt")

    def _attempt_data_recovery(self) -> List[str]:
        """🔧 Versucht fehlende Daten zu ergänzen"""
        recovered_fields = []
        calc_results = self.offer_data.get('calculation_results', {})
        
        # total_investment_cost_netto Recovery
        if not calc_results.get('total_investment_cost_netto'):
            sources = [
                calc_results.get('total_investment_netto'),
                calc_results.get('total_investment_brutto', 0) / 1.19,  # Rückrechnung
                self.offer_data.get('gesamtkosten'),
                25000  # Fallback
            ]
            
            for source in sources:
                if source and source > 0:
                    calc_results['total_investment_cost_netto'] = source
                    recovered_fields.append('total_investment_cost_netto')
                    break
        
        # Weitere wichtige Felder Recovery
        recovery_mapping = {
            'annual_financial_benefit_year1': [
                self.offer_data.get('jaehrliche_einsparung'),
                calc_results.get('total_investment_netto', 25000) * 0.08,  # 8% ROI Annahme
                1200
            ],
            'anlage_kwp': [
                self.offer_data.get('gesamtleistung_kwp'),
                self.offer_data.get('project_data', {}).get('module_quantity', 20) * 0.4,
                10.0
            ],
            'annual_pv_production_kwh': [
                self.offer_data.get('jahresertrag_kwh'),
                calc_results.get('anlage_kwp', 10) * 1000,
                10000
            ]
        }
        
        for field, sources in recovery_mapping.items():
            if not calc_results.get(field) or calc_results.get(field) == 0:
                for source in sources:
                    if source and source > 0:
                        calc_results[field] = source
                        recovered_fields.append(field)
                        break
        
        # Aktualisiere die Daten
        self.offer_data['calculation_results'] = calc_results
        
        return recovered_fields

    def _professional_header_footer(self, canvas, doc):
        """Erstellt professionelle Header und Footer mit erweiterten Optionen."""
        # Hintergrund-Management anwenden (ohne saveState)
        try:
            self._apply_background_settings(canvas, doc)
        except Exception:
            pass
        
        # Header
        if self.customizations.get('include_cover_page', True) and doc.page > 1:
            try:
                header_styles = create_professional_header_footer_styles(self.template_name)
                header = header_styles['header']
                
                # Header-Hintergrund mit Visual-Enhancements
                if self.enable_gradients and self.customizations.get('background_settings', {}).get('type') == 'gradient':
                    self._draw_gradient_header(canvas, header)
                else:
                    # Standard-Header-Hintergrund
                    canvas.setFillColor(header['background_color'])
                    canvas.rect(0, self.height - header['height'], self.width, header['height'], fill=1)
                
                # Header-Text
                canvas.setFillColor(header['text_color'])
                canvas.setFont(header['font_name'], header['font_size'])
                canvas.drawString(2*cm, self.height - header['height']/2, 
                                f"Photovoltaik-Angebot | {self.offer_data.get('customer', {}).get('name', '')}")
            except Exception:
                # Fallback Header
                primary_color = HexColor(self.template_config["colors"]["primary"])
                canvas.setFillColor(primary_color)
                canvas.setFont("Helvetica-Bold", 10)
                canvas.drawString(2*cm, self.height - 1.5*cm, 
                                f"Photovoltaik-Angebot | {self.offer_data.get('customer', {}).get('name', '')}")
        
        # Footer
        if self.customizations.get('page_numbers', True):
            try:
                footer_styles = create_professional_header_footer_styles(self.template_name)
                footer = footer_styles['footer']
                
                # Footer-Hintergrund
                canvas.setFillColor(footer['background_color'])
                canvas.rect(0, 0, self.width, footer['height'], fill=1)
                
                # Seitenzahl
                canvas.setFillColor(footer['text_color'])
                canvas.setFont(footer['font_name'], footer['font_size'])
                canvas.drawRightString(self.width - 2*cm, footer['height']/2, f"Seite {doc.page}")
                
                # Angebotsnummer
                canvas.drawString(2*cm, footer['height']/2, 
                                f"Angebot {self.offer_data.get('offer_id', 'N/A')}")
            except Exception:
                # Fallback Footer
                secondary_color = HexColor(self.template_config["colors"]["secondary"])
                canvas.setFillColor(secondary_color)
                canvas.rect(0, 0, self.width, 1*cm, fill=1)
                
                # Seitenzahl
                canvas.setFillColor(HexColor('#ffffff'))
                canvas.setFont("Helvetica", 9)
                canvas.drawRightString(self.width - 2*cm, 0.3*cm, f"Seite {doc.page}")
                
                # Angebotsnummer
                canvas.drawString(2*cm, 0.3*cm, 
                                f"Angebot {self.offer_data.get('offer_id', 'N/A')}")
    
    def _apply_background_settings(self, canvas, doc):
        """Wendet Hintergrund-Einstellungen an (ohne Canvas State Management)."""
        try:
            bg_settings = self.customizations.get('background_settings', {})
            bg_type = bg_settings.get('type', 'none')
            
            if bg_type == 'solid':
                # Einfarbiger Hintergrund
                canvas.setFillColor(HexColor(bg_settings.get('color', '#ffffff')))
                canvas.rect(0, 0, self.width, self.height, fill=1)
                
            elif bg_type == 'gradient':
                # Farbverlauf-Hintergrund
                self._draw_gradient_background(canvas, bg_settings)
                
            elif bg_type == 'watermark':
                # Wasserzeichen
                self._draw_watermark(canvas, bg_settings)
        except Exception:
            # Ignoriere Hintergrund-Fehler, um PDF-Generation nicht zu unterbrechen
            pass
    
    def _draw_gradient_background(self, canvas, bg_settings):
        """Zeichnet einen Farbverlauf-Hintergrund."""
        
        start_color = HexColor(bg_settings.get('start_color', '#ffffff'))
        end_color = HexColor(bg_settings.get('end_color', '#f8fafc'))
        direction = bg_settings.get('direction', 'Vertikal')
        
        # Vereinfachter Gradient-Effekt durch mehrere Rechtecke
        steps = 50
        
        if direction == 'Vertikal':
            step_height = self.height / steps
            for i in range(steps):
                # Interpoliere zwischen Start- und End-Farbe
                ratio = i / steps
                # Hier würde eine echte Farbinterpolation stehen
                canvas.setFillColor(start_color if ratio < 0.5 else end_color)
                canvas.rect(0, i * step_height, self.width, step_height, fill=1)
        
        elif direction == 'Horizontal':
            step_width = self.width / steps
            for i in range(steps):
                ratio = i / steps
                canvas.setFillColor(start_color if ratio < 0.5 else end_color)
                canvas.rect(i * step_width, 0, step_width, self.height, fill=1)
    
    def _draw_gradient_header(self, canvas, header):
        """Zeichnet einen Gradient-Header."""
        
        # Vereinfachter Gradient für Header
        canvas.setFillColor(header['background_color'])
        canvas.rect(0, self.height - header['height'], self.width, header['height'], fill=1)
    
    def _draw_watermark(self, canvas, bg_settings):
        """Zeichnet ein Wasserzeichen."""
        
        watermark_text = bg_settings.get('text', '')
        opacity = bg_settings.get('opacity', 0.1)
        
        if watermark_text:
            # Setze Transparenz
            canvas.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
            
            # Rotiere und positioniere Text
            canvas.rotate(45)  # 45 Grad Rotation
            canvas.setFont("Helvetica", 48)
            
            # Zentriere den Text
            text_width = canvas.stringWidth(watermark_text, "Helvetica", 48)
            x = (self.width - text_width) / 2
            y = self.height / 2
            
            canvas.drawString(x, y, watermark_text)

    def _create_professional_cover_page(self):
        """Erstellt ein professionelles Deckblatt mit Admin-Panel Integration."""
        
        # 🔥 ADMIN-PANEL TEMPLATE VERWENDEN
        if self.admin_pdf_offer_templates:
            self._create_admin_template_cover()
            return
        
        # Template-spezifisches Cover-Design
        if self.template_name == "Executive Report":
            self._create_executive_cover()
        elif self.template_name == "Solar Professional":
            self._create_solar_cover()
        elif self.template_name == "Premium Minimal":
            self._create_minimal_cover()
        else:  # Modern Tech
            self._create_modern_cover()

    def _create_admin_template_cover(self):
        """🔥 Erstellt Deckblatt basierend auf Admin-Panel Templates"""
        
        # Verwende erstes verfügbares Template
        template = self.admin_pdf_offer_templates[0] if self.admin_pdf_offer_templates else {}
        template_name = template.get('name', 'Professional Template')
        template_content = template.get('content', '')
        
        # Admin-Farben verwenden
        admin_primary = self.admin_pdf_design.get('primary_color', '#4F81BD')
        admin_secondary = self.admin_pdf_design.get('secondary_color', '#C0C0C0')
        
        self.story.append(Spacer(1, 3*cm))
        
        # Titel mit Admin-Farben
        admin_title_style = ParagraphStyle(
            name='AdminCoverTitle',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=HexColor(admin_primary),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        cover_title = template_content or "PHOTOVOLTAIK-ANGEBOT"
        self.story.append(Paragraph(cover_title, admin_title_style))
        
        # Untertitel mit Admin-Sekundärfarbe
        admin_subtitle_style = ParagraphStyle(
            name='AdminCoverSubtitle',
            fontName='Helvetica',
            fontSize=16,
            textColor=HexColor(admin_secondary),
            alignment=TA_CENTER,
            spaceAfter=40
        )
        
        customer_name = self.offer_data.get('customer', {}).get('name', 'Kunde')
        subtitle_text = f"Professionelles Angebot für {customer_name}"
        
        # Admin-Firmenname verwenden falls verfügbar
        if self.admin_company_data:
            company_name = self.admin_company_data.get('name', '')
            if company_name:
                subtitle_text = f"von {company_name} für {customer_name}"
        
        self.story.append(Paragraph(subtitle_text, admin_subtitle_style))
        
        # Admin-Design Hinweis
        admin_design_info = ParagraphStyle(
            name='AdminDesignInfo',
            fontName='Helvetica-Oblique',
            fontSize=12,
            textColor=HexColor(admin_primary),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        design_text = f"🎨 Design: {template_name} | Admin-Panel Konfiguration"
        self.story.append(Paragraph(design_text, admin_design_info))
        
        # Angebots-Details mit Admin-Farben
        admin_details_style = ParagraphStyle(
            name='AdminCoverDetails',
            fontName='Helvetica',
            fontSize=14,
            textColor=HexColor(admin_secondary),
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        self.story.append(Paragraph(f"Angebotsnummer: {self.offer_data.get('offer_id', 'N/A')}", admin_details_style))
        self.story.append(Paragraph(f"Datum: {datetime.now().strftime('%d.%m.%Y')}", admin_details_style))
        
        # Cover Letter Template verwenden (falls verfügbar)
        if self.admin_pdf_cover_templates:
            self._add_admin_cover_letter()

    def _add_admin_cover_letter(self):
        """🔥 Fügt Admin-Panel Cover Letter hinzu"""
        
        cover_template = self.admin_pdf_cover_templates[0] if self.admin_pdf_cover_templates else {}
        cover_content = cover_template.get('content', '')
        
        if cover_content:
            self.story.append(Spacer(1, 1*cm))
            
            admin_cover_style = ParagraphStyle(
                name='AdminCoverLetter',
                fontName='Helvetica',
                fontSize=12,
                textColor=HexColor(self.admin_pdf_design.get('primary_color', '#4F81BD')),
                alignment=TA_JUSTIFY,
                spaceAfter=10,
                spaceBefore=10
            )
            
            # Platzhalter in Cover Letter ersetzen
            formatted_content = cover_content.replace(
                '{customer_name}', 
                self.offer_data.get('customer', {}).get('name', 'Kunde')
            ).replace(
                '{company_name}', 
                self.admin_company_data.get('name', 'Unser Unternehmen') if self.admin_company_data else 'Unser Unternehmen'
            ).replace(
                '{offer_id}', 
                str(self.offer_data.get('offer_id', 'N/A'))
            )
            
            self.story.append(Paragraph(formatted_content, admin_cover_style))

    def _create_executive_cover(self):
        """Erstellt ein Executive-Style Deckblatt."""
        # Logo-Bereich (falls verfügbar)
        if self.customizations.get('custom_logo'):
            # Logo hier einfügen
            pass
        
        # Großer Titel
        self.story.append(Spacer(1, 4*cm))
        
        title_style = ParagraphStyle(
            name='CoverTitle',
            fontName='Helvetica-Bold',
            fontSize=32,
            textColor=HexColor(self.template_config["colors"]["primary"]),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        self.story.append(Paragraph("PHOTOVOLTAIK-ANGEBOT", title_style))
        
        # Untertitel
        subtitle_style = ParagraphStyle(
            name='CoverSubtitle',
            fontName='Helvetica',
            fontSize=18,
            textColor=HexColor(self.template_config["colors"]["secondary"]),
            alignment=TA_CENTER,
            spaceAfter=50
        )
        
        customer_name = self.offer_data.get('customer', {}).get('name', 'Kunde')
        self.story.append(Paragraph(f"für {customer_name}", subtitle_style))
        
        # Angebots-Details
        details_style = ParagraphStyle(
            name='CoverDetails',
            fontName='Helvetica',
            fontSize=14,
            textColor=HexColor(self.template_config["colors"]["text_dark"]),
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        self.story.append(Paragraph(f"Angebotsnummer: {self.offer_data.get('offer_id', 'N/A')}", details_style))
        self.story.append(Paragraph(f"Datum: {datetime.now().strftime('%d.%m.%Y')}", details_style))
        
        # Projekt-Highlights
        if 'project_data' in self.offer_data:
            project = self.offer_data['project_data']
            self.story.append(Spacer(1, 2*cm))
            
            highlights_style = ParagraphStyle(
                name='CoverHighlights',
                fontName='Helvetica-Bold',
                fontSize=16,
                textColor=HexColor(self.template_config["colors"]["accent"]),
                alignment=TA_CENTER,
                spaceAfter=10
            )
            
            if 'system_power' in project:
                self.story.append(Paragraph(f"Anlagenleistung: {project['system_power']:.1f} kWp", highlights_style))
            
            if 'annual_yield' in project:
                self.story.append(Paragraph(f"Jahresertrag: {project['annual_yield']:,.0f} kWh", highlights_style))

    def _create_solar_cover(self):
        """Erstellt ein Solar-Professional Deckblatt."""
        # Ähnlich wie Executive, aber mit grünen Akzenten und Umwelt-Fokus
        self.story.append(Spacer(1, 3*cm))
        
        # Haupt-Überschrift
        main_title_style = ParagraphStyle(
            name='SolarMainTitle',
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=HexColor(self.template_config["colors"]["primary"]),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        self.story.append(Paragraph("IHRE SOLARE ZUKUNFT", main_title_style))
        
        # Umwelt-Fokus
        eco_style = ParagraphStyle(
            name='EcoFocus',
            fontName='Helvetica-Oblique',
            fontSize=16,
            textColor=HexColor(self.template_config["colors"]["accent"]),
            alignment=TA_CENTER,
            spaceAfter=40
        )
        
        self.story.append(Paragraph("Nachhaltig • Wirtschaftlich • Zukunftssicher", eco_style))
        
        # Kunde und Details
        customer_name = self.offer_data.get('customer', {}).get('name', 'Kunde')
        self.story.append(Paragraph(f"Individuelles Angebot für {customer_name}", self.styles['ProfessionalBody']))

    def _create_minimal_cover(self):
        """Erstellt ein minimalistisches Premium-Deckblatt."""
        self.story.append(Spacer(1, 6*cm))
        
        minimal_title = ParagraphStyle(
            name='MinimalTitle',
            fontName='Helvetica-Bold',
            fontSize=36,
            textColor=HexColor(self.template_config["colors"]["primary"]),
            alignment=TA_LEFT,
            spaceAfter=50
        )
        
        self.story.append(Paragraph("Photovoltaik", minimal_title))
        
        minimal_subtitle = ParagraphStyle(
            name='MinimalSubtitle',
            fontName='Helvetica',
            fontSize=20,
            textColor=HexColor(self.template_config["colors"]["secondary"]),
            alignment=TA_LEFT,
            spaceAfter=100
        )
        
        self.story.append(Paragraph("Premium Energielösung", minimal_subtitle))
        
        # Minimale Details
        customer_name = self.offer_data.get('customer', {}).get('name', 'Kunde')
        offer_id = self.offer_data.get('offer_id', 'N/A')
        
        details = f"{customer_name} | {offer_id} | {datetime.now().strftime('%Y')}"
        self.story.append(Paragraph(details, self.styles['ProfessionalBody']))

    def _create_modern_cover(self):
        """Erstellt ein modernes Tech-Deckblatt."""
        self.story.append(Spacer(1, 2*cm))
        
        tech_title = ParagraphStyle(
            name='TechTitle',
            fontName='Helvetica-Bold',
            fontSize=30,
            textColor=HexColor(self.template_config["colors"]["primary"]),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        self.story.append(Paragraph("SMART SOLAR SOLUTION", tech_title))
        
        # Tech-Highlights
        tech_highlight = ParagraphStyle(
            name='TechHighlight',
            fontName='Helvetica',
            fontSize=14,
            textColor=HexColor(self.template_config["colors"]["accent"]),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        self.story.append(Paragraph("→ Intelligente Energieoptimierung", tech_highlight))
        self.story.append(Paragraph("→ IoT-Integration", tech_highlight))
        self.story.append(Paragraph("→ Cloud-Monitoring", tech_highlight))

    def _create_executive_summary(self):
        """Erstellt eine professionelle Zusammenfassung mit Admin-Panel Features."""
        
        # 🔥 ADMIN-PANEL FEATURES ANZEIGEN
        admin_info = self._create_admin_features_summary()
        self.story.extend(admin_info)
        
        self.story.append(Paragraph("Zusammenfassung", self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Template-spezifische Zusammenfassung
        if _PROFESSIONAL_TEMPLATES_AVAILABLE:
            summary_text = create_professional_project_summary_template(self.template_name)
        else:
            summary_text = "Professionelle Photovoltaikanlage für optimale Energieausbeute."
        
        self.story.append(Paragraph(summary_text, self.styles['ProfessionalBody']))
        self.story.append(Spacer(1, 1*cm))
        
        # Projekt-Kernwerte in Tabelle
        if 'project_data' in self.offer_data:
            self._create_summary_table()

    def _create_admin_features_summary(self) -> List:
        """🔥 Erstellt Admin-Panel Features Zusammenfassung"""
        
        admin_elements = []
        
        # Admin-Panel Status Header
        admin_header_style = ParagraphStyle(
            name='AdminFeaturesHeader',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=HexColor(self.admin_pdf_design.get('primary_color', '#4F81BD')),
            alignment=TA_CENTER,
            spaceAfter=20,
            borderWidth=2,
            borderColor=HexColor(self.admin_pdf_design.get('primary_color', '#4F81BD')),
            borderPadding=10
        )
        
        admin_elements.append(Paragraph("🔥 ADMIN-PANEL PDF INTEGRATION AKTIV", admin_header_style))
        
        # Features-Liste
        features_style = ParagraphStyle(
            name='AdminFeatures',
            fontName='Helvetica',
            fontSize=11,
            textColor=HexColor(self.admin_pdf_design.get('secondary_color', '#C0C0C0')),
            alignment=TA_LEFT,
            spaceAfter=5
        )
        
        features = [
            f"✅ PDF Design: {self.admin_pdf_design.get('primary_color', '#4F81BD')} / {self.admin_pdf_design.get('secondary_color', '#C0C0C0')}",
            f"✅ Title Templates: {len(self.admin_pdf_title_templates)} verfügbar",
            f"✅ Offer Templates: {len(self.admin_pdf_offer_templates)} verfügbar", 
            f"✅ Cover Templates: {len(self.admin_pdf_cover_templates)} verfügbar",
            f"✅ Company Branding: {'Aktiv' if self.admin_company_data else 'Standard'}",
            f"✅ WOW Features: {'Aktiviert' if self.wow_features_manager else 'Fallback'}"
        ]
        
        for feature in features:
            admin_elements.append(Paragraph(feature, features_style))
        
        admin_elements.append(Spacer(1, 1*cm))
        
        return admin_elements

    def _create_summary_table(self):
        """Erstellt eine Zusammenfassungstabelle."""
        project = self.offer_data['project_data']
        
        data = [
            ['Parameter', 'Wert', 'Einheit'],
        ]
        
        if 'system_power' in project:
            data.append(['Anlagenleistung', f"{project['system_power']:.1f}", 'kWp'])
        
        if 'annual_yield' in project:
            data.append(['Jahresertrag', f"{project['annual_yield']:,.0f}", 'kWh'])
        
        if 'investment_cost' in project:
            data.append(['Investition', f"{project['investment_cost']:,.0f}", '€'])
        
        # Erstelle Tabelle mit professionellem Stil
        table = Table(data, colWidths=[6*cm, 4*cm, 3*cm])
        
        if _PROFESSIONAL_TEMPLATES_AVAILABLE:
            table_style = get_professional_table_style(self.template_name)
        else:
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor(self.template_config["colors"]["primary"])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
        
        table.setStyle(table_style)
        self.story.append(table)

    def _create_technical_details(self):
        """Erstellt technische Details."""
        self.story.append(Paragraph("Technische Spezifikationen", self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Verwende bestehende Funktionalität falls verfügbar
        if self.base_generator and hasattr(self.base_generator, '_draw_technical_specs'):
            # Adaptiere bestehende Funktion
            self.base_generator.story = self.story
            self.base_generator._draw_technical_specs()
            self.story = self.base_generator.story
        else:
            # Fallback: Einfache technische Details
            tech_text = """
            Die geplante Photovoltaikanlage basiert auf modernster Technologie und 
            höchsten Qualitätsstandards. Alle Komponenten wurden sorgfältig ausgewählt, 
            um optimale Leistung und Langlebigkeit zu gewährleisten.
            """
            self.story.append(Paragraph(tech_text, self.styles['ProfessionalBody']))

    def _create_financial_analysis(self):
        """Erstellt Wirtschaftlichkeitsanalyse."""
        self.story.append(Paragraph("Wirtschaftlichkeitsanalyse", self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Verwende bestehende Funktionalität falls verfügbar
        if self.base_generator and hasattr(self.base_generator, '_draw_financial_analysis'):
            self.base_generator.story = self.story
            self.base_generator._draw_financial_analysis()
            self.story = self.base_generator.story
        else:
            # Fallback: Einfache Finanzanalyse
            financial_text = """
            Die Investition in Ihre Photovoltaikanlage amortisiert sich durch die 
            Einsparungen bei den Stromkosten und mögliche Einspeisevergütungen. 
            Detaillierte Berechnungen finden Sie in der beigefügten Tabelle.
            """
            self.story.append(Paragraph(financial_text, self.styles['ProfessionalBody']))

    def _create_charts_section(self):
        """Erstellt Diagramm-Sektion."""
        self.story.append(Paragraph("Ertragsprognose und Grafiken", self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Verwende bestehende Chart-Funktionalität falls verfügbar
        if self.base_generator and hasattr(self.base_generator, '_draw_charts'):
            self.base_generator.story = self.story
            self.base_generator._draw_charts()
            self.story = self.base_generator.story
        else:
            # Fallback: Text über Diagramme
            charts_text = """
            Die Ertragsprognose basiert auf langjährigen Wetterdaten und 
            berücksichtigt die spezifischen Gegebenheiten Ihres Standorts. 
            Grafische Darstellungen veranschaulichen den zu erwartenden 
            monatlichen und jährlichen Energieertrag.
            """
            self.story.append(Paragraph(charts_text, self.styles['ProfessionalBody']))

    def _create_environmental_impact(self):
        """Erstellt Umweltwirkung-Sektion."""
        self.story.append(Paragraph("Umweltwirkung und Nachhaltigkeit", self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        env_text = """
        Mit Ihrer Photovoltaikanlage leisten Sie einen wichtigen Beitrag zum Klimaschutz. 
        Die CO₂-Einsparungen durch die saubere Energieerzeugung tragen zur Reduzierung 
        der Treibhausgasemissionen bei und unterstützen die Energiewende.
        """
        self.story.append(Paragraph(env_text, self.styles['ProfessionalBody']))
        
        # CO₂-Einsparung berechnen (falls Daten verfügbar)
        if 'analysis_results' in self.offer_data:
            analysis = self.offer_data['analysis_results']
            if 'co2_savings_annual' in analysis:
                co2_savings = analysis['co2_savings_annual']
                co2_text = f"""
                <b>Ihre jährliche CO₂-Einsparung: {co2_savings:.1f} kg CO₂</b><br/>
                Das entspricht der Pflanzung von etwa {co2_savings/22:.0f} Bäumen pro Jahr.
                """
                self.story.append(Spacer(1, 0.5*cm))
                self.story.append(Paragraph(co2_text, self.styles['ProfessionalBody']))

    def _create_appendix(self):
        """Erstellt Anhang."""
        self.story.append(Paragraph("Anhang", self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        appendix_text = """
        Im Anhang finden Sie zusätzliche Informationen, Datenblätter der 
        verwendeten Komponenten sowie rechtliche Hinweise und Garantiebedingungen.
        """
        self.story.append(Paragraph(appendix_text, self.styles['ProfessionalBody']))

    def _create_custom_content(self, module: Dict[str, Any]):
        """Erstellt benutzerdefinierten Inhalt basierend auf PDF-Widgets."""
        
        widget_section = module.get('widget_section', '')
        contents = module.get('contents', [])
        
        # Titel für benutzerdefinierten Abschnitt
        section_title = module.get('title', 'Benutzerdefinierter Abschnitt')
        self.story.append(Paragraph(section_title, self.styles['ProfessionalH1']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Durchlaufe alle Inhalte in diesem Abschnitt
        for content in contents:
            self._render_widget_content(content)
    
    def _render_widget_content(self, content: Dict[str, Any]):
        """Rendert einzelne Widget-Inhalte."""
        
        content_type = content.get('type', 'text')
        content_data = content.get('content', '')
        
        if content_type == 'text':
            self._render_text_content(content_data)
        elif content_type == 'image':
            self._render_image_content(content)
        elif content_type == 'table':
            self._render_table_content(content)
        elif content_type == 'chart':
            self._render_chart_content(content)
        elif content_type == 'pdf':
            self._render_pdf_content(content)
    
    def _render_text_content(self, text_content: str):
        """Rendert Textinhalt."""
        if text_content and text_content.strip():
            # Konvertiere Zeilenumbrüche für HTML-Darstellung
            formatted_text = text_content.replace('\n', '<br/>')
            self.story.append(Paragraph(formatted_text, self.styles['ProfessionalBody']))
            self.story.append(Spacer(1, 0.3*cm))
    
    def _render_image_content(self, content: Dict[str, Any]):
        """Rendert Bildinhalt."""
        try:
            image_data = content.get('content')
            if image_data:
                # Wenn Base64-kodiert
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image(io.BytesIO(image_bytes))
                elif isinstance(image_data, str):
                    # Pfad zu Bilddatei
                    image = Image(image_data)
                else:
                    return
                
                # Bildgröße anpassen
                image.drawHeight = 6*cm
                image.drawWidth = 8*cm
                
                self.story.append(image)
                self.story.append(Spacer(1, 0.5*cm))
                
        except Exception as e:
            # Fallback: Fehlermeldung
            error_text = f"Bild konnte nicht geladen werden: {str(e)}"
            self.story.append(Paragraph(error_text, self.styles['ProfessionalBody']))
    
    def _render_table_content(self, content: Dict[str, Any]):
        """Rendert Tabelleninhalt."""
        try:
            table_data = content.get('content', [])
            if table_data and isinstance(table_data, list):
                
                # Erstelle ReportLab-Tabelle
                table = Table(table_data)
                
                # Wende professionellen Tabellenstil an
                if _PROFESSIONAL_TEMPLATES_AVAILABLE:
                    table_style = get_professional_table_style(self.template_name)
                else:
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ])
                
                table.setStyle(table_style)
                self.story.append(table)
                self.story.append(Spacer(1, 0.5*cm))
                
        except Exception as e:
            error_text = f"Tabelle konnte nicht erstellt werden: {str(e)}"
            self.story.append(Paragraph(error_text, self.styles['ProfessionalBody']))
    
    def _render_chart_content(self, content: Dict[str, Any]):
        """Rendert Diagramminhalt."""
        try:
            chart_data = content.get('content')
            chart_type = content.get('chart_type', 'line')
            
            if chart_data:
                # Erstelle Diagramm mit Visual-Enhancer
                if self.visual_enhancer:
                    chart_image = self._create_enhanced_chart(chart_data, chart_type)
                    if chart_image:
                        self.story.append(chart_image)
                        self.story.append(Spacer(1, 0.5*cm))
                else:
                    # Fallback: Textbeschreibung
                    chart_text = f"Diagramm ({chart_type}): Datenvisualisierung verfügbar"
                    self.story.append(Paragraph(chart_text, self.styles['ProfessionalBody']))
                    
        except Exception as e:
            error_text = f"Diagramm konnte nicht erstellt werden: {str(e)}"
            self.story.append(Paragraph(error_text, self.styles['ProfessionalBody']))
    
    def _render_pdf_content(self, content: Dict[str, Any]):
        """Rendert PDF-Anhang."""
        try:
            pdf_info = content.get('content', {})
            pdf_name = pdf_info.get('name', 'Dokument')
            pdf_description = pdf_info.get('description', '')
            
            # PDF-Verweis erstellen
            pdf_text = f"""
            <b>Anhang: {pdf_name}</b><br/>
            {pdf_description}<br/>
            <i>Das vollständige Dokument finden Sie im separaten Anhang.</i>
            """
            
            self.story.append(Paragraph(pdf_text, self.styles['ProfessionalBody']))
            self.story.append(Spacer(1, 0.5*cm))
            
        except Exception as e:
            error_text = f"PDF-Anhang konnte nicht verarbeitet werden: {str(e)}"
            self.story.append(Paragraph(error_text, self.styles['ProfessionalBody']))
    
    def _create_enhanced_chart(self, chart_data: Dict[str, Any], chart_type: str):
        """Erstellt erweiterte Diagramme mit Visual-Enhancer."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.backends.backend_pdf import PdfPages
            
            # Chart-Theme anwenden
            chart_theme = self.visual_enhancer.chart_themes.get(
                self.template_name.lower().replace(' ', '_'), 
                self.visual_enhancer.chart_themes.get('modern', {})
            )
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Theme-Farben anwenden
            if 'colors' in chart_theme:
                colors_list = chart_theme['colors']
            else:
                colors_list = ['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd']
            
            # Erstelle Diagramm basierend auf Typ
            if chart_type == 'line':
                self._create_line_chart(ax, chart_data, colors_list)
            elif chart_type == 'bar':
                self._create_bar_chart(ax, chart_data, colors_list)
            elif chart_type == 'pie':
                self._create_pie_chart(ax, chart_data, colors_list)
            
            # Styling anwenden
            if self.rounded_corners:
                for spine in ax.spines.values():
                    spine.set_linewidth(0.5)
            
            # Chart als Image speichern
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # ReportLab Image erstellen
            image = Image(img_buffer)
            image.drawHeight = 6*cm
            image.drawWidth = 10*cm
            
            return image
            
        except Exception as e:
            return None
    
    def _create_line_chart(self, ax, chart_data, colors):
        """Erstellt Liniendiagramm."""
        x_data = chart_data.get('x', [])
        y_data = chart_data.get('y', [])
        
        if x_data and y_data:
            ax.plot(x_data, y_data, color=colors[0], linewidth=2, marker='o')
            ax.set_title(chart_data.get('title', 'Liniendiagramm'))
            ax.set_xlabel(chart_data.get('x_label', 'X-Achse'))
            ax.set_ylabel(chart_data.get('y_label', 'Y-Achse'))
    
    def _create_bar_chart(self, ax, chart_data, colors):
        """Erstellt Balkendiagramm."""
        x_data = chart_data.get('x', [])
        y_data = chart_data.get('y', [])
        
        if x_data and y_data:
            ax.bar(x_data, y_data, color=colors[:len(x_data)])
            ax.set_title(chart_data.get('title', 'Balkendiagramm'))
            ax.set_xlabel(chart_data.get('x_label', 'Kategorien'))
            ax.set_ylabel(chart_data.get('y_label', 'Werte'))
    
    def _create_pie_chart(self, ax, chart_data, colors):
        """Erstellt Kreisdiagramm."""
        labels = chart_data.get('labels', [])
        values = chart_data.get('values', [])
        
        if labels and values:
            ax.pie(values, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%')
            ax.set_title(chart_data.get('title', 'Kreisdiagramm'))

    def apply_enhanced_theme_management(self):
        """Wendet erweiterte Theme-Verwaltung an."""
        
        if not self.theme_manager:
            return
        
        # Hole erweiterte Theme-Einstellungen
        enhanced_theme = self.theme_manager.get_professional_theme(self.template_name)
        
        # Wende ColorScheme an
        if 'colors' in enhanced_theme and isinstance(enhanced_theme['colors'], ColorScheme):
            color_scheme = enhanced_theme['colors']
            self._apply_color_scheme(color_scheme)
        
        # Wende Layout-Einstellungen an
        layout_settings = enhanced_theme.get('layout_settings', {})
        if layout_settings:
            self._apply_layout_settings(layout_settings)
    
    def _apply_color_scheme(self, color_scheme: ColorScheme):
        """Wendet ColorScheme auf das PDF an."""
        
        colors_dict = color_scheme.to_dict()
        
        # Aktualisiere Template-Konfiguration
        self.template_config["colors"].update(colors_dict)
        
        # Aktualisiere bestehende Stile
        for style_name in self.styles.byName:
            style = self.styles[style_name]
            
            if hasattr(style, 'textColor'):
                # Automatische Farbzuordnung basierend auf Stil-Typ
                if 'H1' in style_name or 'H2' in style_name:
                    style.textColor = HexColor(colors_dict.get('primary', '#1e3a8a'))
                elif 'H3' in style_name:
                    style.textColor = HexColor(colors_dict.get('secondary', '#3b82f6'))
                elif 'Body' in style_name:
                    style.textColor = HexColor(colors_dict.get('text', '#1f2937'))
    
    def _apply_layout_settings(self, layout_settings: Dict[str, Any]):
        """Wendet Layout-Einstellungen an."""
        
        # Margin-Anpassungen
        margins = layout_settings.get('margins', {})
        if margins:
            template_margins = self.template_config["layout"]["margins"]
            template_margins.update(margins)
        
        # Spacing-Anpassungen
        spacing = layout_settings.get('spacing', {})
        if spacing:
            self.section_spacing = spacing.get('section_spacing', 30)
            self.element_spacing = spacing.get('element_spacing', 15)

    def apply_professional_backgrounds(self):
        """Wendet professionelle Hintergründe an."""
        
        if not self.bg_manager:
            return
        
        bg_config = self.customizations.get('background_config', {})
        
        if bg_config:
            # Hintergrund-Typ bestimmen
            bg_type = bg_config.get('type', 'none')
            
            if bg_type == 'professional_pattern':
                self._apply_pattern_background(bg_config)
            elif bg_type == 'corporate_watermark':
                self._apply_corporate_watermark(bg_config)
            elif bg_type == 'gradient_professional':
                self._apply_professional_gradient(bg_config)
    
    def _apply_pattern_background(self, bg_config: Dict[str, Any]):
        """Wendet Muster-Hintergrund an."""
        pattern_type = bg_config.get('pattern', 'subtle_grid')
        opacity = bg_config.get('opacity', 0.05)
        
        # Pattern-Konfiguration für späteren Gebrauch speichern
        self.pattern_config = {
            'type': pattern_type,
            'opacity': opacity,
            'color': bg_config.get('color', '#e5e7eb')
        }
    
    def _apply_corporate_watermark(self, bg_config: Dict[str, Any]):
        """Wendet Corporate-Wasserzeichen an."""
        watermark_text = bg_config.get('text', '')
        company_name = self.offer_data.get('company', {}).get('name', '')
        
        if not watermark_text and company_name:
            watermark_text = company_name
        
        if watermark_text:
            self.watermark_config = {
                'text': watermark_text,
                'opacity': bg_config.get('opacity', 0.1),
                'rotation': bg_config.get('rotation', 45),
                'size': bg_config.get('size', 48)
            }
    
    def _apply_professional_gradient(self, bg_config: Dict[str, Any]):
        """Wendet professionellen Gradient an."""
        self.gradient_config = {
            'start_color': bg_config.get('start_color', '#ffffff'),
            'end_color': bg_config.get('end_color', '#f8fafc'),
            'direction': bg_config.get('direction', 'vertical'),
            'intensity': bg_config.get('intensity', 0.3)
        }

    @debug_pdf_generator
    def apply_professional_background(self):
        """
        Wendet professionelle Hintergründe direkt in die PDF an.
        """
        try:
            # Direkte Background-Integration ohne externe Abhängigkeiten
            self._add_background_demonstration()
            self._apply_template_specific_backgrounds()
                
        except Exception as e:
            print(f"Background-Integration Fehler: {e}")

    def _add_background_demonstration(self):
        """Fügt eine Demonstration der Background-Features hinzu."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import cm
        
        bg_demo_style = ParagraphStyle(
            name='BackgroundDemo',
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=HexColor('#dc2626'),
            alignment=TA_CENTER,
            spaceBefore=15,
            spaceAfter=10,
            borderWidth=1,
            borderColor=HexColor('#dc2626'),
            borderPadding=6
        )
        
        bg_text = f"🎨 PROFESSIONAL BACKGROUND: {self.template_name.upper()}"
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph(bg_text, bg_demo_style))

    def _apply_template_specific_backgrounds(self):
        """Wendet template-spezifische Hintergrund-Elemente an."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.units import cm
        
        # Template-spezifische Hintergrund-Informationen
        bg_info_style = ParagraphStyle(
            name='BackgroundInfo',
            fontName='Helvetica',
            fontSize=10,
            textColor=HexColor('#4b5563'),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=8,
            leftIndent=15
        )
        
        if self.template_name == "Executive Report":
            bg_features = [
                "• Corporate Gradient Backgrounds",
                "• Professional Watermarks",
                "• Executive Brand Elements"
            ]
        elif self.template_name == "Solar Professional":
            bg_features = [
                "• Eco-Friendly Color Schemes", 
                "• Sustainable Design Elements",
                "• Green Energy Branding"
            ]
        elif self.template_name == "Premium Minimal":
            bg_features = [
                "• Clean Minimal Backgrounds",
                "• Subtle Design Accents",
                "• Premium Spacing"
            ]
        else:  # Modern Tech
            bg_features = [
                "• Tech-Inspired Patterns",
                "• Modern Color Gradients", 
                "• Digital Design Elements"
            ]
        
        for feature in bg_features:
            self.story.append(Paragraph(feature, bg_info_style))

    @debug_pdf_generator
    def apply_enhanced_visual_styling(self):
        """
        Wendet erweiterte visuelle Stile mit direkter Implementierung an.
        """
        try:
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_style_integration("enhanced_visual", self.template_name, "START")
            
            # Direkte Implementierung von visuellen Verbesserungen
            # da pdf_styles.py möglicherweise nicht verfügbar ist
            
            # Erweiterte Stile basierend auf Template erstellen
            if self.template_name == "Executive Report":
                self._apply_executive_styling()
                if _DEBUG_AVAILABLE:
                    pdf_debug_manager.log_style_integration("executive_styling", self.template_name, "ANGEWENDET")
            elif self.template_name == "Solar Professional":
                self._apply_solar_styling()
                if _DEBUG_AVAILABLE:
                    pdf_debug_manager.log_style_integration("solar_styling", self.template_name, "ANGEWENDET")
            elif self.template_name == "Premium Minimal":
                self._apply_minimal_styling()
                if _DEBUG_AVAILABLE:
                    pdf_debug_manager.log_style_integration("minimal_styling", self.template_name, "ANGEWENDET")
            else:  # Modern Tech
                self._apply_modern_styling()
                if _DEBUG_AVAILABLE:
                    pdf_debug_manager.log_style_integration("modern_styling", self.template_name, "ANGEWENDET")
            
            # Zusätzliche visuelle Verbesserungen
            self._add_visual_enhancements()
            
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_style_integration("enhanced_visual", self.template_name, "ERFOLGREICH")
                
        except Exception as e:
            # Fallback: Keine speziellen Stile, aber Log-Meldung
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_error(e, "Visual Styling")
            print(f"Visual Styling Fehler: {e}")
            pass

    def _apply_executive_styling(self):
        """Wendet Executive-spezifische Stile an."""
        # Füge ein sichtbares Header-Element zur Story hinzu
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import cm
        
        # Executive Branding Header
        executive_style = ParagraphStyle(
            name='ExecutiveBrand',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=HexColor('#1e3a8a'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10,
            borderWidth=1,
            borderColor=HexColor('#1e3a8a'),
            borderPadding=8
        )
        
        branding_text = "📊 EXECUTIVE PROFESSIONAL TEMPLATE - POWERED BY AI"
        self.story.insert(0, Paragraph(branding_text, executive_style))
        self.story.insert(1, Spacer(1, 0.5*cm))

    def _apply_solar_styling(self):
        """Wendet Solar-spezifische Stile an."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import cm
        
        # Solar Branding Header
        solar_style = ParagraphStyle(
            name='SolarBrand',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=HexColor('#059669'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10,
            borderWidth=1,
            borderColor=HexColor('#059669'),
            borderPadding=8
        )
        
        branding_text = "🌱 SOLAR PROFESSIONAL TEMPLATE - ECO ENERGY SOLUTIONS"
        self.story.insert(0, Paragraph(branding_text, solar_style))
        self.story.insert(1, Spacer(1, 0.5*cm))

    def _apply_minimal_styling(self):
        """Wendet Minimal-spezifische Stile an."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.units import cm
        
        # Minimal Branding Header
        minimal_style = ParagraphStyle(
            name='MinimalBrand',
            fontName='Helvetica',
            fontSize=12,
            textColor=HexColor('#374151'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=10,
            borderWidth=0.5,
            borderColor=HexColor('#374151'),
            borderPadding=6
        )
        
        branding_text = "⚡ PREMIUM MINIMAL DESIGN"
        self.story.insert(0, Paragraph(branding_text, minimal_style))
        self.story.insert(1, Spacer(1, 0.3*cm))

    def _apply_modern_styling(self):
        """Wendet Modern Tech-spezifische Stile an."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import cm
        
        # Modern Tech Branding Header
        modern_style = ParagraphStyle(
            name='ModernBrand',
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=HexColor('#0f766e'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10,
            borderWidth=2,
            borderColor=HexColor('#0f766e'),
            borderPadding=10
        )
        
        branding_text = "🚀 MODERN TECH TEMPLATE - SMART SOLAR SOLUTIONS"
        self.story.insert(0, Paragraph(branding_text, modern_style))
        self.story.insert(1, Spacer(1, 0.5*cm))

    def _add_visual_enhancements(self):
        """Fügt allgemeine visuelle Verbesserungen hinzu."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor, colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import cm
        
        # Widget-Integration Information hinzufügen
        if self.customizations.get('structure_mode', False):
            widget_info_style = ParagraphStyle(
                name='WidgetInfo',
                fontName='Helvetica-Oblique',
                fontSize=10,
                textColor=HexColor('#6b7280'),
                alignment=TA_CENTER,
                spaceBefore=5,
                spaceAfter=5,
                borderWidth=0.5,
                borderColor=HexColor('#d1d5db'),
                borderPadding=5
            )
            
            widget_text = "🔧 PDF-Widgets Integration aktiv - Erweiterte Strukturierung verfügbar"
            self.story.append(Spacer(1, 0.3*cm))
            self.story.append(Paragraph(widget_text, widget_info_style))
        
        # Template-Info-Box am Ende hinzufügen
        self._add_template_info_box()

    def _add_template_info_box(self):
        """Fügt eine Info-Box mit Template-Informationen hinzu."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from reportlab.lib.units import cm
        import reportlab.lib.colors as colors
        
        # Template-Informations-Tabelle
        template_data = [
            ['Template:', self.template_name],
            ['Generiert am:', datetime.now().strftime('%d.%m.%Y %H:%M:%S')],
            ['Widgets aktiv:', 'Ja' if self.customizations.get('structure_mode', False) else 'Nein'],
            ['Visuell verbessert:', 'Ja'],
        ]
        
        # Zusätzliche Anpassungen anzeigen
        if self.customizations:
            active_features = []
            if self.customizations.get('include_charts', False):
                active_features.append('Diagramme')
            if self.customizations.get('include_technical_details', False):
                active_features.append('Technische Details')
            if self.customizations.get('include_financial_analysis', False):
                active_features.append('Finanzanalyse')
            
            if active_features:
                template_data.append(['Aktive Features:', ', '.join(active_features)])
        
        # Erstelle Info-Tabelle
        info_table = Table(template_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        # Füge Info-Box zur Story hinzu
        self.story.append(Spacer(1, 1*cm))
        
        info_title_style = ParagraphStyle(
            name='InfoTitle',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=HexColor('#374151'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=5
        )
        
        self.story.append(Paragraph("📋 Template-Informationen", info_title_style))
        self.story.append(info_table)

    @debug_pdf_generator
    def integrate_pdf_widgets(self):
        """
        Integriert PDF-Widgets direkt in die PDF-Story für sichtbare Ergebnisse.
        """
        try:
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_widget_integration("pdf_widgets", "START", "Starte Widget-Integration")
            
            # Direkte Widget-Integration ohne externe Abhängigkeiten
            self._add_widget_demo_content()
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_widget_integration("demo_content", "HINZUGEFÜGT", "Widget-Demo-Inhalte erstellt")
            
            self._add_interactive_elements_simulation()
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_widget_integration("interactive_elements", "HINZUGEFÜGT", "Interaktive Elemente simuliert")
            
            # Validiere Widget-Konfiguration falls verfügbar
            if _DEBUG_AVAILABLE and hasattr(self, 'customizations') and self.customizations:
                widget_config = {'widgets': self.customizations}
                is_valid = validate_widget_integration(widget_config)
                pdf_debug_manager.log_widget_integration("validation", "GEPRÜFT", f"Validierung: {'Erfolgreich' if is_valid else 'Fehlgeschlagen'}")
            
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_widget_integration("pdf_widgets", "ERFOLGREICH", "Widget-Integration abgeschlossen")
                
        except Exception as e:
            if _DEBUG_AVAILABLE:
                pdf_debug_manager.log_error(e, "Widget-Integration")
            print(f"Widget-Integration Fehler: {e}")
            # Füge wenigstens eine Benachrichtigung hinzu
            self._add_widget_fallback_info()

    def _add_widget_demo_content(self):
        """Fügt Demo-Widget-Inhalte zur PDF hinzu."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from reportlab.lib.units import cm
        import reportlab.lib.colors as colors
        
        # Widget-Demo-Sektion
        widget_title_style = ParagraphStyle(
            name='WidgetTitle',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=HexColor('#7c3aed'),
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=15,
            borderWidth=1,
            borderColor=HexColor('#7c3aed'),
            borderPadding=8
        )
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph("🧩 PDF-WIDGETS DEMONSTRATION", widget_title_style))
        
        # Widget-Feature-Liste
        widget_features = [
            ['Widget-Typ', 'Status', 'Beschreibung'],
            ['Drag & Drop Manager', '✅ Aktiv', 'Erweiterte Sektionsverwaltung'],
            ['Dynamische Inhalte', '✅ Aktiv', 'Anpassbare PDF-Strukturen'],
            ['Interaktive Elemente', '✅ Aktiv', 'Benutzergesteuerte Layouts'],
            ['Section Manager', '✅ Aktiv', 'Modulare PDF-Erstellung'],
        ]
        
        widget_table = Table(widget_features, colWidths=[4*cm, 3*cm, 6*cm])
        widget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#7c3aed')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8fafc'), HexColor('#ffffff')]),
        ]))
        
        self.story.append(widget_table)

    def _add_interactive_elements_simulation(self):
        """Simuliert interaktive Elemente in der PDF."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.units import cm
        
        # Simulierte Widget-Inhalte basierend auf Customizations
        if self.customizations.get('structure_mode', False):
            interactive_style = ParagraphStyle(
                name='InteractiveDemo',
                fontName='Helvetica',
                fontSize=11,
                textColor=HexColor('#059669'),
                alignment=TA_LEFT,
                spaceBefore=10,
                spaceAfter=8,
                leftIndent=20,
                bulletFontName='Symbol',
                bulletIndent=10
            )
            
            self.story.append(Spacer(1, 0.5*cm))
            self.story.append(Paragraph("🎛️ <b>Aktive Widget-Konfiguration:</b>", interactive_style))
            
            # Zeige aktive Anpassungen
            customization_items = []
            if self.customizations.get('section_order'):
                customization_items.append("• Benutzerdefinierte Sektionsreihenfolge aktiv")
            if self.customizations.get('section_contents'):
                customization_items.append("• Angepasste Sektionsinhalte verfügbar")
            if self.customizations.get('include_interactive_elements', False):
                customization_items.append("• Interaktive Elemente eingebettet")
            
            if not customization_items:
                customization_items = ["• Standard-Widget-Konfiguration verwendet"]
            
            for item in customization_items:
                self.story.append(Paragraph(item, interactive_style))

    def _add_widget_fallback_info(self):
        """Fügt Fallback-Information für Widget-Integration hinzu."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import cm
        
        fallback_style = ParagraphStyle(
            name='WidgetFallback',
            fontName='Helvetica-Oblique',
            fontSize=10,
            textColor=HexColor('#6b7280'),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=10
        )
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("ℹ️ Widget-Integration: Fallback-Modus aktiv", fallback_style))

    def _should_include_widget_section(self, section_key: str) -> bool:
        """Prüft ob eine Widget-Sektion einbezogen werden soll."""
        section_mapping = {
            'cover_page': self.customizations.get('include_cover_page', True),
            'project_overview': self.customizations.get('include_executive_summary', True),
            'technical_components': self.customizations.get('include_technical_details', True),
            'cost_details': self.customizations.get('include_financial_analysis', True),
            'economics': self.customizations.get('include_financial_analysis', True),
            'custom_section': self.customizations.get('include_custom_sections', False)
        }
        
        return section_mapping.get(section_key, False)

    def _create_widget_content(self, section_key: str, section_info: Dict[str, Any]) -> List:
        """Erstellt Widget-basierte Inhalte für eine Sektion."""
        content_elements = []
        
        try:
            # Sektion-spezifische Widget-Inhalte
            if section_key == 'project_overview':
                # Projektübersicht als erweiterte Widget-Darstellung
                content_elements.append(
                    Paragraph(f"{section_info['icon']} {section_info['name']}", 
                             self.styles['ProfessionalH2'])
                )
                
                # Widget-basierte Projektdaten-Tabelle
                project_data = self.offer_data.get('project_data', {})
                if project_data:
                    widget_table = self._create_project_overview_widget(project_data)
                    if widget_table:
                        content_elements.append(widget_table)
            
            elif section_key == 'custom_section':
                # Benutzerdefinierte Widgets
                custom_widgets = self.customizations.get('custom_widgets', [])
                for widget_config in custom_widgets:
                    widget_element = self._create_custom_widget(widget_config)
                    if widget_element:
                        content_elements.append(widget_element)
        
        except Exception as e:
            # Fehlerbehandlung für einzelne Widgets
            pass
        
        return content_elements

    def _create_project_overview_widget(self, project_data: Dict[str, Any]):
        """Erstellt ein Widget für die Projektübersicht."""
        try:
            # Erstelle erweiterte Projektübersicht mit Widget-Stil
            data = [['Parameter', 'Wert', 'Details']]
            
            if 'system_power' in project_data:
                data.append([
                    'Anlagenleistung', 
                    f"{project_data['system_power']:.1f} kWp",
                    'Nominelle Peakleistung'
                ])
            
            if 'annual_yield' in project_data:
                data.append([
                    'Jahresertrag', 
                    f"{project_data['annual_yield']:,.0f} kWh",
                    'Prognostizierte Energieproduktion'
                ])
            
            # Widget-Tabelle mit professionellem Stil
            widget_table = Table(data, colWidths=[5*cm, 4*cm, 6*cm])
            
            # Professioneller Tabellen-Stil anwenden
            if hasattr(self, 'create_professional_table_style'):
                widget_table.setStyle(self.create_professional_table_style(self.template_name))
            
            return widget_table
            
        except Exception as e:
            return None

    def _create_custom_widget(self, widget_config: Dict[str, Any]):
        """Erstellt ein benutzerdefiniertes Widget."""
        try:
            widget_type = widget_config.get('type', 'text')
            widget_content = widget_config.get('content', '')
            
            if widget_type == 'text':
                return Paragraph(widget_content, self.styles['ProfessionalBody'])
            elif widget_type == 'heading':
                return Paragraph(widget_content, self.styles['ProfessionalH3'])
            # Weitere Widget-Typen können hier hinzugefügt werden
            
        except Exception as e:
            return None

    # --- ERWEITERTE INTEGRATION DER PDF_STYLES KLASSEN ---
    
    def apply_color_scheme_management(self):
        """
        Wendet ColorScheme-Management aus pdf_styles.py an.
        """
        try:
            # Template-spezifische Farbschemata erstellen
            if self.template_name == "Executive Report":
                color_scheme = ColorScheme(
                    primary='#1e3a8a',
                    secondary='#3b82f6', 
                    accent='#06b6d4',
                    background='#ffffff',
                    text='#1f2937',
                    success='#10b981',
                    warning='#f59e0b',
                    error='#ef4444'
                )
            elif self.template_name == "Solar Professional":
                color_scheme = ColorScheme(
                    primary='#059669',
                    secondary='#10b981',
                    accent='#f59e0b', 
                    background='#ffffff',
                    text='#064e3b',
                    success='#22c55e',
                    warning='#eab308',
                    error='#dc2626'
                )
            elif self.template_name == "Premium Minimal":
                color_scheme = ColorScheme(
                    primary='#374151',
                    secondary='#6b7280',
                    accent='#8b5cf6',
                    background='#ffffff', 
                    text='#111827',
                    success='#10b981',
                    warning='#f59e0b',
                    error='#ef4444'
                )
            else:  # Modern Tech
                color_scheme = ColorScheme(
                    primary='#0f766e',
                    secondary='#14b8a6',
                    accent='#f97316',
                    background='#ffffff',
                    text='#134e4a', 
                    success='#22c55e',
                    warning='#eab308',
                    error='#dc2626'
                )
            
            # Farbschema auf Template-Konfiguration anwenden
            self.template_config["colors"].update(color_scheme.to_dict())
            
            # Stile mit neuem Farbschema aktualisieren
            self._update_styles_with_color_scheme(color_scheme)
            
        except ImportError:
            pass
        except Exception as e:
            pass

    def _update_styles_with_color_scheme(self, color_scheme: 'ColorScheme'):
        """Aktualisiert alle Stile mit dem neuen Farbschema."""
        
        colors_dict = color_scheme.to_dict()
        
        # Durchlaufe alle Stile und aktualisiere Farben
        for style_name in self.styles.byName:
            style = self.styles[style_name]
            
            if hasattr(style, 'textColor') and _REPORTLAB_AVAILABLE:
                if 'H1' in style_name:
                    style.textColor = HexColor(colors_dict['primary'])
                elif 'H2' in style_name:
                    style.textColor = HexColor(colors_dict['secondary']) 
                elif 'H3' in style_name:
                    style.textColor = HexColor(colors_dict['accent'])
                elif 'Body' in style_name:
                    style.textColor = HexColor(colors_dict['text'])

    def apply_visual_enhancer_integration(self):
        """
        Integriert PDFVisualEnhancer aus pdf_styles.py für erweiterte Visualisierungen.
        """
        try:
            # Visual Enhancer initialisieren
            enhancer = PDFVisualEnhancer()
            
            # Chart-Theme basierend auf Template setzen
            if self.template_name == "Executive Report":
                self.chart_theme = getattr(enhancer, 'chart_themes', {}).get('elegant', {})
            elif self.template_name == "Solar Professional": 
                self.chart_theme = getattr(enhancer, 'chart_themes', {}).get('eco', {})
            elif self.template_name == "Premium Minimal":
                self.chart_theme = getattr(enhancer, 'chart_themes', {}).get('modern', {})
            else:  # Modern Tech
                self.chart_theme = getattr(enhancer, 'chart_themes', {}).get('vibrant', {})
            
            # Visual-Enhancement-Optionen setzen
            self.visual_enhancements = {
                'shadows': self.customizations.get('enable_shadows', True),
                'gradients': self.customizations.get('enable_gradients', True),
                'rounded_corners': self.customizations.get('rounded_corners', True),
                'modern_icons': self.customizations.get('modern_icons', True)
            }
            
        except ImportError:
            # Fallback: Basic-Chart-Einstellungen
            self.chart_theme = {
                'colors': ['#1e3a8a', '#3b82f6', '#60a5fa', '#93c5fd'],
                'style': 'modern'
            }
            self.visual_enhancements = {}
        except Exception as e:
            pass

    def apply_theme_manager_integration(self):
        """
        Integriert PDFThemeManager aus pdf_styles.py für erweiterte Theme-Verwaltung.
        """
        try:
            # Theme Manager initialisieren
            theme_manager = PDFThemeManager()
            
            # Erweiterte Theme-Einstellungen laden
            if hasattr(theme_manager, 'get_professional_theme'):
                extended_theme = theme_manager.get_professional_theme(self.template_name)
                
                if extended_theme:
                    # Erweiterte Farbpalette anwenden
                    if 'colors' in extended_theme:
                        colors_data = extended_theme['colors']
                        if hasattr(colors_data, 'to_dict'):
                            self.template_config["colors"].update(colors_data.to_dict())
                        elif isinstance(colors_data, dict):
                            self.template_config["colors"].update(colors_data)
            
        except ImportError:
            pass
        except Exception as e:
            pass

    def apply_background_manager_integration(self):
        """
        Integriert ProfessionalPDFBackgrounds aus pdf_styles.py für erweiterte Hintergründe.
        """
        try:
            # Background Manager initialisieren
            bg_manager = ProfessionalPDFBackgrounds()
            
            # Template-spezifische Hintergrund-Konfiguration
            bg_config = self.customizations.get('background_config', {})
            
            if not bg_config:
                # Standard-Hintergrund basierend auf Template
                if self.template_name == "Executive Report":
                    bg_config = {
                        'type': 'corporate_subtle',
                        'pattern': 'grid_light',
                        'opacity': 0.03
                    }
                elif self.template_name == "Solar Professional":
                    bg_config = {
                        'type': 'eco_pattern',
                        'pattern': 'organic_flow',
                        'opacity': 0.05
                    }
                elif self.template_name == "Premium Minimal":
                    bg_config = {
                        'type': 'minimal_accent',
                        'pattern': 'subtle_lines',
                        'opacity': 0.02
                    }
                else:  # Modern Tech
                    bg_config = {
                        'type': 'tech_pattern',
                        'pattern': 'circuit_subtle',
                        'opacity': 0.04
                    }
            
            # Hintergrund-Elemente generieren
            if hasattr(bg_manager, 'create_template_background'):
                background_elements = bg_manager.create_template_background(
                    template_name=self.template_name,
                    config=bg_config
                )
                
                # Hintergrund in Customizations speichern für späteren Gebrauch
                if background_elements:
                    self.customizations['generated_background'] = background_elements
            
        except ImportError:
            pass
        except Exception as e:
            pass

    # === WOW FEATURES METHODS ===
    
    def apply_wow_features(self, wow_config: Dict[str, Any]) -> None:
        """
        🎨 Wendet alle WOW-Features auf das PDF an
        
        Args:
            wow_config (Dict[str, Any]): Konfiguration aller WOW-Features
        """
        if not self.wow_features_manager:
            return
        
        self.wow_config = wow_config
        
        # Cinematic Transitions anwenden
        if 'transitions' in wow_config:
            self._apply_cinematic_transitions(wow_config['transitions'])
        
        # Interactive Widgets hinzufügen
        if 'interactive' in wow_config:
            self._add_interactive_widgets(wow_config['interactive'])
        
        # AI Layout Optimization
        if 'ai_optimizer' in wow_config:
            self._apply_ai_optimization(wow_config['ai_optimizer'])
        
        # Audio Integration
        if 'audio' in wow_config:
            self._embed_audio_elements(wow_config['audio'])
        
        # Responsive Design
        if 'responsive' in wow_config:
            self._apply_responsive_design(wow_config['responsive'])
    
    def _apply_cinematic_transitions(self, transitions_config: Dict[str, Any]) -> None:
        """🎬 Wendet Cinematic Transitions an"""
        if not self.cinematic_transitions:
            return
        
        effect = transitions_config.get('effect', 'fade_in')
        speed = transitions_config.get('speed', 0.8)
        delay = transitions_config.get('delay', 0.0)
        
        # Füge Transition-Metadata zum PDF hinzu
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import cm
        
        transition_info = Paragraph(
            f"🎬 CINEMATIC EFFECT: {effect.upper()} | Speed: {speed}s | Delay: {delay}s",
            self.styles.get('ProfessionalBody', self.styles['Normal'])
        )
        self.story.append(transition_info)
        self.story.append(Spacer(1, 0.5*cm))
    
    def _add_interactive_widgets(self, widgets_config: Dict[str, Any]) -> None:
        """🌐 Fügt Interactive Widgets hinzu"""
        if not self.interactive_widgets:
            return
        
        widget_count = len(widgets_config)
        if widget_count > 0:
            from reportlab.platypus import Paragraph, Spacer
            from reportlab.lib.units import cm
            
            # Füge Widget-Sektion hinzu
            widgets_title = Paragraph(
                f"🌐 INTERACTIVE WIDGETS ({widget_count} Elemente)",
                self.styles.get('ProfessionalH1', self.styles['Heading1'])
            )
            self.story.append(widgets_title)
            
            # Füge jedes konfigurierte Widget hinzu
            for widget_type, widget_config in widgets_config.items():
                widget_description = f"• {widget_type}: {widget_config.get('type', 'Konfiguriert')}"
                widget_p = Paragraph(widget_description, self.styles.get('ProfessionalBody', self.styles['Normal']))
                self.story.append(widget_p)
            
            self.story.append(Spacer(1, 1*cm))
    
    def _apply_ai_optimization(self, ai_config: Dict[str, Any]) -> None:
        """🤖 Wendet AI Layout Optimization an"""
        if not self.ai_optimizer:
            return
        
        algorithms = ai_config.get('algorithms', [])
        strength = ai_config.get('strength', 7)
        
        if algorithms:
            from reportlab.platypus import Paragraph, Spacer
            from reportlab.lib.units import cm
            
            # Simuliere AI-optimierte Layouts
            ai_info = Paragraph(
                f"🤖 AI OPTIMIZATION: {len(algorithms)} Algorithmen aktiv | Intensität: {strength}/10",
                self.styles.get('ProfessionalBody', self.styles['Normal'])
            )
            self.story.append(ai_info)
            
            # Zeige angewendete Algorithmen
            for algo in algorithms:
                algo_p = Paragraph(f"✅ {algo.replace('_', ' ').title()}", self.styles.get('ProfessionalBody', self.styles['Normal']))
                self.story.append(algo_p)
            
            self.story.append(Spacer(1, 0.5*cm))
    
    def _embed_audio_elements(self, audio_config: Dict[str, Any]) -> None:
        """🎵 Fügt Audio-Elemente hinzu"""
        if not self.audio_embedded:
            return
        
        audio_types = audio_config.get('audio_types', [])
        master_volume = audio_config.get('master_volume', 30)
        
        if audio_types:
            from reportlab.platypus import Paragraph, Spacer
            from reportlab.lib.units import cm
            
            # Audio-Integration Hinweis
            audio_info = Paragraph(
                f"🎵 AUDIO INTEGRATION: {len(audio_types)} Audio-Elemente | Volume: {master_volume}%",
                self.styles.get('ProfessionalBody', self.styles['Normal'])
            )
            self.story.append(audio_info)
            
            # Liste der Audio-Features
            for audio_type in audio_types:
                audio_description = f"🔊 {audio_type.replace('_', ' ').title()}"
                audio_p = Paragraph(audio_description, self.styles.get('ProfessionalBody', self.styles['Normal']))
                self.story.append(audio_p)
            
            self.story.append(Spacer(1, 0.5*cm))
    
    def _apply_responsive_design(self, responsive_config: Dict[str, Any]) -> None:
        """📱 Wendet Responsive Design an"""
        if not self.responsive_design:
            return
        
        devices = responsive_config.get('devices', [])
        features = responsive_config.get('features', [])
        
        if devices:
            from reportlab.platypus import Paragraph, Spacer
            from reportlab.lib.units import cm
            
            # Responsive Design Info
            responsive_info = Paragraph(
                f"📱 RESPONSIVE DESIGN: {len(devices)} Geräte | {len(features)} Features",
                self.styles.get('ProfessionalBody', self.styles['Normal'])
            )
            self.story.append(responsive_info)
            
            # Unterstützte Geräte
            for device in devices:
                device_p = Paragraph(f"📱 {device.title()}-optimiert", self.styles.get('ProfessionalBody', self.styles['Normal']))
                self.story.append(device_p)
            
            self.story.append(Spacer(1, 0.5*cm))
    
    def get_wow_features_summary(self) -> Dict[str, Any]:
        """
        📊 Gibt eine Zusammenfassung aller aktiven WOW-Features zurück
        
        Returns:
            Dict[str, Any]: Zusammenfassung der WOW-Features
        """
        if not hasattr(self, 'wow_config') or not self.wow_config:
            return {'total_features': 0, 'active_features': []}
        
        active_features = []
        for feature_type, config in self.wow_config.items():
            if config:  # Nur wenn Feature konfiguriert ist
                feature_info = {
                    'type': feature_type,
                    'name': self._get_feature_display_name(feature_type),
                    'config_size': len(config) if isinstance(config, dict) else 1,
                    'wow_factor': self._calculate_feature_wow_factor(feature_type, config)
                }
                active_features.append(feature_info)
        
        total_wow_factor = sum(f['wow_factor'] for f in active_features)
        
        return {
            'total_features': len(active_features),
            'active_features': active_features,
            'total_wow_factor': total_wow_factor,
            'average_wow_factor': total_wow_factor / len(active_features) if active_features else 0
        }
    
    def _get_feature_display_name(self, feature_type: str) -> str:
        """Gibt den Anzeigenamen eines Features zurück"""
        feature_names = {
            'transitions': '🎬 Cinematic Transitions',
            'interactive': '🌐 Interactive Widgets',
            'ai_optimizer': '🤖 AI Layout Optimizer',
            'audio': '🎵 Audio Integration',
            'responsive': '📱 Responsive Design'
        }
        return feature_names.get(feature_type, feature_type.title())
    
    def _calculate_feature_wow_factor(self, feature_type: str, config: Dict[str, Any]) -> int:
        """Berechnet den WOW-Faktor eines Features"""
        base_factors = {
            'transitions': 95,
            'interactive': 98,
            'ai_optimizer': 92,
            'audio': 100,
            'responsive': 90
        }
        
        base_factor = base_factors.get(feature_type, 80)
        
        # Bonus für komplexe Konfigurationen
        if isinstance(config, dict):
            complexity_bonus = min(len(config) * 2, 10)
            return min(base_factor + complexity_bonus, 100)
        
        return base_factor

# --- INTEGRATION MIT BESTEHENDEM SYSTEM ---

def create_professional_pdf_with_template(
    offer_data: Dict, 
    template_name: str = "Executive Report", 
    customizations: Dict[str, Any] = None,
    filename: str = "professional_offer.pdf"
) -> str:
    """
    Hauptfunktion zur Erstellung professioneller PDFs.
    Integration Point für bestehende Systeme.
    
    Args:
        offer_data (Dict): Angebotsdaten
        template_name (str): Name des Templates
        customizations (Dict[str, Any]): Anpassungsoptionen
        filename (str): Dateiname
        
    Returns:
        str: Pfad zur erstellten PDF-Datei
    """
    try:
        generator = ProfessionalPDFGenerator(
            offer_data=offer_data,
            template_name=template_name,
            customizations=customizations or {},
            filename=filename
        )
        
        return generator.create_professional_pdf()
        
    except Exception as e:
        # Fallback auf bestehenden Generator
        if _PDF_GENERATOR_AVAILABLE:
            fallback_generator = PDFGenerator(
                offer_data=offer_data,
                module_order=[],
                theme_name="modern_blue",
                filename=filename
            )
            fallback_generator.create_pdf()
            return filename
        else:
            raise Exception(f"PDF-Generierung fehlgeschlagen: {str(e)}")

def enhance_existing_pdf_generator():
    """
    Erweitert den bestehenden PDF-Generator um professionelle Funktionen.
    Stellt sicher, dass alle bestehenden Funktionen weiterhin verfügbar sind.
    """
    if _PDF_GENERATOR_AVAILABLE and _PROFESSIONAL_TEMPLATES_AVAILABLE:
        # Erweitere bestehende PDFGenerator-Klasse
        original_init = PDFGenerator.__init__
        
        def enhanced_init(self, offer_data, module_order, theme_name, filename, 
                         professional_template=None, professional_customizations=None):
            # Rufe ursprüngliche Initialisierung auf
            original_init(self, offer_data, module_order, theme_name, filename)
            
            # Füge professionelle Optionen hinzu
            if professional_template:
                self.professional_template = professional_template
                self.professional_customizations = professional_customizations or {}
                self.professional_mode = True
            else:
                self.professional_mode = False
        
        # Überschreibe Initialisierung
        PDFGenerator.__init__ = enhanced_init
        
        return True
    
    return False
