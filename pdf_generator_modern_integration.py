# pdf_generator_modern_integration.py
# -*- coding: utf-8 -*-
"""
Modular optionale Integration des modernen Design-Systems in bestehende PDF-Generatoren
Erweitert bestehende Funktionalität ohne sie zu ersetzen oder zu verändern
"""

from typing import Dict, Any, Optional, List, Union
import traceback

# Sichere Imports für bestehende PDF-Generatoren
try:
    from pdf_generator_professional import ProfessionalPDFGenerator
    PROFESSIONAL_PDF_AVAILABLE = True
except ImportError:
    PROFESSIONAL_PDF_AVAILABLE = False

try:
    from pdf_generator_enhanced import EnhancedPDFGenerator
    ENHANCED_PDF_AVAILABLE = True
except ImportError:
    ENHANCED_PDF_AVAILABLE = False

# Sichere Imports für moderne Design-Features
try:
    from pdf_design_enhanced_modern import (
        ModernPDFDesignSystem,
        ModernPDFComponentLibrary,
        get_modern_design_system,
        get_modern_component_library
    )
    from pdf_ui_design_enhancement import (
        create_modern_pdf_content_enhancer,
        get_modern_design_integration_config
    )
    MODERN_DESIGN_AVAILABLE = True
except ImportError:
    MODERN_DESIGN_AVAILABLE = False

class ModernPDFGeneratorMixin:
    """
    Mixin-Klasse die bestehende PDF-Generatoren um moderne Design-Features erweitert
    Vollständig optional und backward-kompatibel
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modern_design_system = None
        self.modern_component_library = None
        self.modern_content_enhancer = None
        self.modern_design_config = {}
        self._initialize_modern_features()
    
    def _initialize_modern_features(self):
        """Initialisiert moderne Design-Features falls verfügbar"""
        if not MODERN_DESIGN_AVAILABLE:
            return
        
        try:
            # Design-Konfiguration von UI holen
            self.modern_design_config = get_modern_design_integration_config()
            
            if self.modern_design_config.get('enabled', False):
                self.modern_design_system = get_modern_design_system()
                self.modern_component_library = get_modern_component_library(self.modern_design_system)
                
                # Content-Enhancer erstellen (falls project_data und analysis_results verfügbar)
                if hasattr(self, 'offer_data'):
                    project_data = getattr(self, 'offer_data', {})
                    analysis_results = project_data.get('analysis_results', {})
                    self.modern_content_enhancer = create_modern_pdf_content_enhancer(
                        self.modern_design_config, project_data, analysis_results
                    )
                    
        except Exception as e:
            print(f"Warnung: Moderne Design-Features konnten nicht initialisiert werden: {e}")
            self.modern_design_config = {'enabled': False}
    
    def apply_modern_styling_if_enabled(self):
        """Wendet moderne Styles an falls aktiviert"""
        if not self._is_modern_design_enabled():
            return
        
        try:
            # Erweiterte Styles zu bestehenden Styles hinzufügen
            if hasattr(self, 'styles') and self.modern_design_system:
                modern_styles = self.modern_design_system.get_enhanced_paragraph_styles(
                    self._get_current_color_scheme()
                )
                
                # Moderne Styles zu bestehenden hinzufügen (ohne Überschreibung)
                for style_name, style in modern_styles.items():
                    modern_style_name = f"Modern_{style_name}"
                    if hasattr(self.styles, 'add'):
                        self.styles.add(style, name=modern_style_name)
                    
        except Exception as e:
            print(f"Warnung: Moderne Styles konnten nicht angewendet werden: {e}")
    
    def enhance_financial_section_if_enabled(self, financial_data: Dict[str, Any]) -> List:
        """Erweitert Finanzbereich mit modernen Features falls aktiviert"""
        if not self._is_modern_design_enabled() or not self.modern_content_enhancer:
            return []
        
        try:
            return self.modern_content_enhancer.enhance_financial_content(financial_data)
        except Exception as e:
            print(f"Warnung: Finanzbereich konnte nicht erweitert werden: {e}")
            return []
    
    def enhance_technical_section_if_enabled(self, tech_data: Dict[str, Any]) -> List:
        """Erweitert technischen Bereich mit modernen Features falls aktiviert"""
        if not self._is_modern_design_enabled() or not self.modern_content_enhancer:
            return []
        
        try:
            return self.modern_content_enhancer.enhance_technical_content(tech_data)
        except Exception as e:
            print(f"Warnung: Technischer Bereich konnte nicht erweitert werden: {e}")
            return []
    
    def enhance_product_section_if_enabled(self, products: List[Dict]) -> List:
        """Erweitert Produktbereich mit modernen Features falls aktiviert"""
        if not self._is_modern_design_enabled() or not self.modern_content_enhancer:
            return []
        
        try:
            return self.modern_content_enhancer.enhance_product_content(products)
        except Exception as e:
            print(f"Warnung: Produktbereich konnte nicht erweitert werden: {e}")
            return []
    
    def create_modern_info_box_if_enabled(self, title: str, content: str, 
                                        box_type: str = 'info') -> List:
        """Erstellt moderne Info-Box falls aktiviert"""
        if not self._is_modern_design_enabled() or not self.modern_content_enhancer:
            return []
        
        try:
            return self.modern_content_enhancer.create_info_box(title, content, box_type)
        except Exception as e:
            print(f"Warnung: Info-Box konnte nicht erstellt werden: {e}")
            return []
    
    def create_modern_section_header_if_enabled(self, title: str, subtitle: str = "") -> List:
        """Erstellt modernen Abschnitt-Header falls aktiviert"""
        if not self._is_modern_design_enabled() or not self.modern_content_enhancer:
            return []
        
        try:
            return self.modern_content_enhancer.create_section_header(title, subtitle)
        except Exception as e:
            print(f"Warnung: Abschnitt-Header konnte nicht erstellt werden: {e}")
            return []
    
    def get_modern_table_style_if_enabled(self, table_type: str = 'data'):
        """Gibt modernen Tabellen-Style zurück falls aktiviert"""
        if not self._is_modern_design_enabled() or not self.modern_content_enhancer:
            return None
        
        try:
            return self.modern_content_enhancer.get_enhanced_table_style(table_type)
        except Exception as e:
            print(f"Warnung: Moderner Tabellen-Style konnte nicht erstellt werden: {e}")
            return None
    
    def _is_modern_design_enabled(self) -> bool:
        """Prüft ob moderne Design-Features aktiviert sind"""
        return (MODERN_DESIGN_AVAILABLE and 
                self.modern_design_config.get('enabled', False) and
                self.modern_design_system is not None)
    
    def _get_current_color_scheme(self) -> str:
        """Gibt das aktuelle Farbschema zurück"""
        if not self._is_modern_design_enabled():
            return 'premium_blue_modern'
        
        return self.modern_design_config.get('color_scheme_name', 'premium_blue_modern')

# Erweiterte Versionen der bestehenden PDF-Generatoren
class ModernEnhancedProfessionalPDFGenerator(ModernPDFGeneratorMixin, ProfessionalPDFGenerator):
    """
    Erweiterte Version des ProfessionalPDFGenerator mit modernen Design-Features
    Vollständig backward-kompatibel
    """
    
    def __init__(self, *args, **kwargs):
        # Prüfe ob ProfessionalPDFGenerator verfügbar ist
        if not PROFESSIONAL_PDF_AVAILABLE:
            raise ImportError("ProfessionalPDFGenerator nicht verfügbar")
        
        super().__init__(*args, **kwargs)
    
    def apply_enhanced_visual_styling(self):
        """Erweitert die bestehende Visual Styling Methode"""
        # Bestehende Funktionalität beibehalten
        try:
            super().apply_enhanced_visual_styling()
        except:
            pass
        
        # Moderne Styles hinzufügen
        self.apply_modern_styling_if_enabled()
    
    def create_financial_section_enhanced(self, financial_data: Dict[str, Any]) -> List:
        """Erstellt erweiterten Finanzbereich"""
        elements = []
        
        # Moderne Header falls aktiviert
        modern_header = self.create_modern_section_header_if_enabled(
            "💰 Finanzielle Analyse", 
            "Detaillierte Wirtschaftlichkeitsbetrachtung Ihrer Investition"
        )
        elements.extend(modern_header)
        
        # Moderne Finanz-Widgets falls aktiviert
        modern_financial = self.enhance_financial_section_if_enabled(financial_data)
        elements.extend(modern_financial)
        
        return elements
    
    def create_technical_section_enhanced(self, tech_data: Dict[str, Any]) -> List:
        """Erstellt erweiterten technischen Bereich"""
        elements = []
        
        # Moderne Header falls aktiviert
        modern_header = self.create_modern_section_header_if_enabled(
            "⚡ Technische Spezifikationen",
            "Hochwertige Komponenten für maximale Effizienz"
        )
        elements.extend(modern_header)
        
        # Moderne technische Darstellung falls aktiviert
        modern_tech = self.enhance_technical_section_if_enabled(tech_data)
        elements.extend(modern_tech)
        
        return elements

# Factory-Funktionen für einfache Integration
def create_enhanced_pdf_generator_with_modern_design(generator_type: str = "professional", 
                                                   *args, **kwargs):
    """
    Factory-Funktion für erweiterte PDF-Generatoren mit modernem Design
    """
    if generator_type == "professional" and PROFESSIONAL_PDF_AVAILABLE:
        return ModernEnhancedProfessionalPDFGenerator(*args, **kwargs)
    elif generator_type == "enhanced" and ENHANCED_PDF_AVAILABLE:
        # TODO: Implementierung für EnhancedPDFGenerator
        pass
    else:
        # Fallback auf Standard-Generator falls verfügbar
        if PROFESSIONAL_PDF_AVAILABLE:
            return ProfessionalPDFGenerator(*args, **kwargs)
        else:
            raise ImportError("Kein PDF-Generator verfügbar")

def integrate_modern_design_into_existing_pdf_generation(offer_data: Dict[str, Any],
                                                       texts: Dict[str, str],
                                                       template_name: str = "Professional",
                                                       *args, **kwargs) -> Optional[str]:
    """
    Integriert moderne Design-Features in bestehende PDF-Generierung
    Fallback auf Standard-Generierung falls moderne Features nicht verfügbar
    """
    try:
        # Versuche erweiterten Generator zu erstellen
        generator = create_enhanced_pdf_generator_with_modern_design(
            generator_type="professional",
            offer_data=offer_data,
            template_name=template_name,
            *args, **kwargs
        )
        
        # PDF generieren mit erweiterten Features
        if hasattr(generator, 'create_premium_modern_pdf'):
            return generator.create_premium_modern_pdf()
        else:
            # Fallback auf Standard-Methode
            return generator.create_pdf()
            
    except Exception as e:
        print(f"Warnung: Erweiterte PDF-Generierung fehlgeschlagen: {e}")
        
        # Fallback auf Standard-PDF-Generierung
        try:
            if PROFESSIONAL_PDF_AVAILABLE:
                standard_generator = ProfessionalPDFGenerator(
                    offer_data=offer_data,
                    template_name=template_name,
                    *args, **kwargs
                )
                return standard_generator.create_pdf()
        except Exception as fallback_error:
            print(f"Fehler auch bei Standard-PDF-Generierung: {fallback_error}")
            return None

# Hilfsfunktionen für Integration
def check_modern_design_availability() -> Dict[str, bool]:
    """Prüft Verfügbarkeit aller Design-Komponenten"""
    return {
        'modern_design_system': MODERN_DESIGN_AVAILABLE,
        'professional_pdf_generator': PROFESSIONAL_PDF_AVAILABLE,
        'enhanced_pdf_generator': ENHANCED_PDF_AVAILABLE,
        'full_integration_possible': (MODERN_DESIGN_AVAILABLE and 
                                    (PROFESSIONAL_PDF_AVAILABLE or ENHANCED_PDF_AVAILABLE))
    }

def get_integration_status_info() -> str:
    """Gibt Informationen über den Integrationsstatus zurück"""
    status = check_modern_design_availability()
    
    info_parts = []
    
    if status['full_integration_possible']:
        info_parts.append("✅ Vollständige moderne Design-Integration verfügbar")
    elif status['modern_design_system']:
        info_parts.append("⚠️ Moderne Design-Features verfügbar, aber kein kompatibler PDF-Generator")
    elif status['professional_pdf_generator'] or status['enhanced_pdf_generator']:
        info_parts.append("⚠️ PDF-Generatoren verfügbar, aber moderne Design-Features fehlen")
    else:
        info_parts.append("❌ Weder moderne Design-Features noch PDF-Generatoren verfügbar")
    
    info_parts.append(f"Modern Design System: {'✅' if status['modern_design_system'] else '❌'}")
    info_parts.append(f"Professional PDF Generator: {'✅' if status['professional_pdf_generator'] else '❌'}")
    info_parts.append(f"Enhanced PDF Generator: {'✅' if status['enhanced_pdf_generator'] else '❌'}")
    
    return "\n".join(info_parts)
