"""
MEGA TOM-90 HYBRID PDF GENERATOR
================================

Diese Klasse fusioniert:
1. Die perfekten TOM-90 Seiten 1-5 (exakte Pixel-Reproduktion)
2. ALLE bestehenden PDF-Konfigurationsoptionen als zusätzliche Seiten
3. Vollständige Kommunikation zwischen beiden Systemen
4. MODERN DESIGN SYSTEM für professionelle Seiten 6-18

BOMBE! 🚀💎
"""

import fitz
import os
import io
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime
import base64
import copy

# TOM-90 Exact Renderer Import
try:
    from tom90_exact_renderer import TOM90ExactRenderer
    TOM90_EXACT_AVAILABLE = True
except ImportError:
    TOM90_EXACT_AVAILABLE = False
    print("⚠️ TOM90ExactRenderer nicht verfügbar - verwende Fallback")

# Standard PDF Generator Import  
try:
    from pdf_generator import PDFGenerator
    STANDARD_PDF_AVAILABLE = True
except ImportError:
    STANDARD_PDF_AVAILABLE = False
    print("⚠️ PDFGenerator nicht verfügbar")

# Modern Design System Import
try:
    from modern_pdf_design_system import MODERN_DESIGNER
    MODERN_DESIGN_AVAILABLE = True
    print("✅ Modern Design System geladen")
except ImportError:
    MODERN_DESIGN_AVAILABLE = False
    print("⚠️ Modern Design System nicht verfügbar - verwende Standard-Design")

# Import der beiden Basis-Systeme
from tom90_exact_renderer import TOM90ExactRenderer
from pdf_generator import PDFGenerator


class MegaTOM90HybridPDFGenerator:
    """
    Mega-Hybrid-PDF-Generator: TOM-90 exakte Seiten 1-5 + vollständige PDF-Funktionen
    
    FEATURES:
    - Seiten 1-5: Exakte TOM-90 Reproduktion mit dynamischen Keys
    - Seiten 6+: Alle bestehenden PDF-Funktionen (Vorlagen, Diagramme, etc.)
    - 100% Kompatibilität zu bestehenden PDF-Konfigurationen
    - Optionale Aktivierung aller Funktionen
    """
    
    def __init__(
        self,
        project_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        inclusion_options: Optional[Dict[str, Any]] = None,
        sections_to_include: Optional[List[str]] = None,
        texts: Optional[Dict[str, str]] = None,
        # TOM-90 spezifische Parameter
        company_logo_base64: Optional[str] = None,
        # PDF-System spezifische Parameter
        selected_title_image_b64: Optional[str] = None,
        selected_offer_title_text: Optional[str] = None,
        selected_cover_letter_text: Optional[str] = None,
        # Callback-Funktionen für erweiterte Funktionen
        load_admin_setting_func: Optional[Callable] = None,
        save_admin_setting_func: Optional[Callable] = None,
        list_products_func: Optional[Callable] = None,
        get_product_by_id_func: Optional[Callable] = None,
        db_list_company_documents_func: Optional[Callable] = None,
        active_company_id: Optional[int] = None,
        # Zusätzliche Optionen
        pdf_config_options: Optional[Dict[str, Any]] = None,
        custom_sections: Optional[List[Dict[str, Any]]] = None,
        custom_text_areas: Optional[List[Dict[str, Any]]] = None,
        custom_images: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialisiert den Mega-Hybrid-Generator"""
        
        # Basis Daten
        self.project_data = project_data or {}
        self.analysis_results = analysis_results or {}
        self.company_info = company_info or {}
        self.inclusion_options = inclusion_options or {}
        self.sections_to_include = sections_to_include or []
        self.texts = texts or {}
        
        # TOM-90 Renderer - verwende standalone Funktion statt Klasse
        self.tom90_project_data = project_data
        self.tom90_analysis_results = analysis_results
        self.tom90_company_info = company_info
        self.tom90_inclusion_options = inclusion_options
        self.tom90_texts = texts
        self.tom90_company_logo_base64 = company_logo_base64
        
        # Standard PDF Generator für zusätzliche Seiten (falls benötigt)
        self.pdf_generator = None
        try:
            # Versuche PDFGenerator zu initialisieren mit Minimum-Parametern
            self.pdf_generator = PDFGenerator(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                texts=texts,
                theme_name="modern",
                inclusion_options=inclusion_options or {},
                section_order_df=None,
                custom_images_list=[],
                custom_text_blocks_list=[],
                side_by_side_sim_keys=[],
                highlight_box_data={},
                get_product_by_id_func=get_product_by_id_func,
                db_list_company_documents_func=db_list_company_documents_func,
                active_company_id=active_company_id,
                selected_title_image_b64=selected_title_image_b64,
                selected_offer_title_text=selected_offer_title_text,
                selected_cover_letter_text=selected_cover_letter_text
            )
        except Exception as e:
            print(f"⚠️ PDF-Generator konnte nicht initialisiert werden: {e}")
            # Fallback ohne PDF-Generator
            self.pdf_generator = None
        
        # Erweiterte Parameter
        self.selected_title_image_b64 = selected_title_image_b64
        self.selected_offer_title_text = selected_offer_title_text
        self.selected_cover_letter_text = selected_cover_letter_text
        
        # Callback-Funktionen
        self.load_admin_setting_func = load_admin_setting_func
        self.save_admin_setting_func = save_admin_setting_func
        self.list_products_func = list_products_func
        self.get_product_by_id_func = get_product_by_id_func
        self.db_list_company_documents_func = db_list_company_documents_func
        self.active_company_id = active_company_id
        
        # PDF-Konfiguration
        self.pdf_config_options = pdf_config_options or {}
        
        # Benutzerdefinierte Inhalte
        self.custom_sections = custom_sections or []
        self.custom_text_areas = custom_text_areas or []
        self.custom_images = custom_images or []
        
        # Initialisiere Standard-Optionen
        self._init_default_options()
    
    def _init_default_options(self):
        """Initialisiert Standard-Konfigurationsoptionen"""
        
        # Standard PDF-Optionen falls nicht angegeben
        if not self.pdf_config_options:
            self.pdf_config_options = {}
        
        # Übertrage inclusion_options in pdf_config_options für Kompatibilität
        if self.inclusion_options:
            self.pdf_config_options.update(self.inclusion_options)
        
        # Standard-Optionen setzen (nur falls nicht bereits gesetzt)
        default_options = {
            # Vorlagen
            'include_title_image': True,
            'include_offer_title': True,
            'include_cover_letter': True,
            
            # Hauptsektionen
            'include_company_info': True,
            'include_project_overview': True,
            'include_technical_specs': True,
            'include_financial_analysis': True,
            'include_environmental_impact': True,
            'include_recommendations': True,
            
            # Features & Highlights
            'include_feature_highlights': True,
            'include_roi_calculations': True,
            'include_comparison_tables': True,
            
            # Diagramme & Visualisierungen
            'include_monthly_production_chart': True,
            'include_savings_chart': True,
            'include_roi_chart': True,
            'include_co2_chart': True,
            'include_comparison_chart': True,
            
            # Firmenspezifische Inhalte
            'include_company_logo': True,
            'include_company_documents': True,
            'include_product_datasheets': True,
            
            # Zusätzliche Inhalte
            'include_custom_text_areas': True,
            'include_custom_images': True,
            'include_financing_calculations': True,  # NEU: Finanzierungsberechnungen
            'include_appendices': True,
        }
        
        # Füge nur fehlende Standard-Optionen hinzu
        for key, value in default_options.items():
            if key not in self.pdf_config_options:
                self.pdf_config_options[key] = value
        
        # Standard-Sektionen falls nicht angegeben
        if not self.sections_to_include:
            self.sections_to_include = [
                'project_overview',
                'technical_specifications',
                'financial_analysis',
                'environmental_impact',
                'product_details',
                'recommendations',
                'appendices'
            ]
    
    def generate_hybrid_pdf(self) -> bytes:
        """
        Generiert das Mega-Hybrid-PDF mit verbessertem Error-Handling
        
        Returns:
            PDF als Bytes
        """
        
        try:
            # 1. TOM-90 Seiten 1-5 generieren
            print("🎨 Generiere TOM-90 Basis-Seiten (1-5)...")
            try:
                from tom90_exact_renderer import generate_tom90_exact_pdf
                
                tom90_pdf_bytes = generate_tom90_exact_pdf(
                    project_data=self.tom90_project_data,
                    analysis_results=self.tom90_analysis_results,
                    company_info=self.tom90_company_info,
                    inclusion_options=self.tom90_inclusion_options,
                    texts=self.tom90_texts,
                    company_logo_base64=self.tom90_company_logo_base64
                )
                print("✅ TOM-90 Basis-Seiten erfolgreich generiert")
            except Exception as e:
                print(f"❌ TOM-90 Generierung fehlgeschlagen: {e}")
                # Fallback: Erstelle leere TOM-90 Seiten
                tom90_pdf_bytes = self._create_fallback_tom90_pages()
            
            # 2. Zusätzliche Seiten basierend auf Konfiguration generieren
            print("📊 Generiere erweiterte PDF-Seiten (6+)...")
            additional_pages = self._generate_additional_pages()
            
            # 3. PDFs zusammenführen
            print("🔗 Führe PDFs zusammen...")
            final_pdf_bytes = self._merge_pdfs(tom90_pdf_bytes, additional_pages)
            
            return final_pdf_bytes
            
        except Exception as pdf_error:
            print(f"❌ Kritischer Fehler bei Mega Hybrid PDF-Generierung: {pdf_error}")
            
            # Notfall-Fallback: Erstelle einfaches PDF mit ReportLab
            try:
                print("🚑 Verwende Notfall-PDF-Generierung...")
                return self._create_emergency_pdf()
            except Exception as emergency_error:
                print(f"❌ Auch Notfall-PDF fehlgeschlagen: {emergency_error}")
                raise Exception(f"Alle PDF-Generierungsversuche fehlgeschlagen: {pdf_error}, {emergency_error}")
        
        print("✅ Mega-Hybrid-PDF erfolgreich generiert!")
        return final_pdf_bytes
    
    def _generate_additional_pages(self) -> bytes:
        """Generiert alle zusätzlichen PDF-Seiten basierend auf Konfiguration"""
        
        print(f"🔍 DEBUG: pdf_config_options: {list(self.pdf_config_options.keys())}")
        print(f"🔍 DEBUG: include_project_overview = {self.pdf_config_options.get('include_project_overview', 'NOT SET')}")
        print(f"🔍 DEBUG: include_technical_specs = {self.pdf_config_options.get('include_technical_specs', 'NOT SET')}")
        
        # Neues PDF-Dokument für zusätzliche Seiten
        doc = fitz.open()
        
        pages_added = 0
        
        # Seite 6: Erweiterte Projektübersicht (IMMER hinzufügen)
        print("📄 Füge Seite 6: Erweiterte Projektübersicht hinzu...")
        self._add_extended_project_overview(doc)
        pages_added += 1
        
        # Seite 7: Detaillierte technische Spezifikationen (IMMER hinzufügen)
        print("📄 Füge Seite 7: Technische Spezifikationen hinzu...")
        self._add_detailed_technical_specs(doc)
        pages_added += 1
        
        # Seite 8: Finanzanalyse & ROI-Berechnungen (IMMER hinzufügen)
        print("📄 Füge Seite 8: Finanzanalyse hinzu...")
        self._add_financial_analysis_page(doc)
        pages_added += 1
        
        # Seite 9: Diagramme & Visualisierungen (IMMER hinzufügen)
        print("📄 Füge Seite 9: Diagramme & Visualisierungen hinzu...")
        self._add_charts_visualization_page(doc)
        pages_added += 1
        
        # Seite 10: Umweltauswirkungen & CO2-Bilanz (IMMER hinzufügen)
        print("📄 Füge Seite 10: Umweltauswirkungen hinzu...")
        self._add_environmental_impact_page(doc)
        pages_added += 1
        
        # Seite 11: Features & Highlights (falls aktiviert)
        if self.pdf_config_options.get('include_feature_highlights', True):
            print("📄 Füge Seite 11: Features & Highlights hinzu...")
            self._add_features_highlights_page(doc)
            pages_added += 1
        
        # Seite 12: Vergleichstabellen (falls aktiviert)
        if self.pdf_config_options.get('include_comparison_tables', True):
            print("📄 Füge Seite 12: Vergleichstabellen hinzu...")
            self._add_comparison_tables_page(doc)
            pages_added += 1
        
        # Seite 13+: Benutzerdefinierte Textbereiche
        if self.pdf_config_options.get('include_custom_text_areas', True) and self.custom_text_areas:
            print(f"📄 Füge {len(self.custom_text_areas)} benutzerdefinierte Textbereiche hinzu...")
            self._add_custom_text_areas(doc)
            pages_added += len(self.custom_text_areas)
        
        # Unterstützung für custom_content_items vom zentralen PDF-System
        custom_content_items = self.inclusion_options.get('custom_content_items', [])
        if custom_content_items:
            print(f"📝 {len(custom_content_items)} individuelle Inhalte gefunden")
            enabled_items = [item for item in custom_content_items if item.get('enabled', True)]
            print(f"✅ {len(enabled_items)} davon aktiviert")
            
            for item in enabled_items:
                item_type = item.get('type', 'unbekannt')
                item_title = item.get('title', 'Ohne Titel')
                print(f"   - {item_type.title()}: {item_title}")
                
                if item_type == 'text':
                    self._add_custom_content_text_item(doc, item)
                    pages_added += 1
                elif item_type == 'image':
                    self._add_custom_content_image_item(doc, item)
                    pages_added += 1
        else:
            print("ℹ️ Keine individuellen Inhalte konfiguriert")
        
        # Seite N: Benutzerdefinierte Bilder
        if self.pdf_config_options.get('include_custom_images', True) and self.custom_images:
            print(f"📄 Füge {len(self.custom_images)} benutzerdefinierte Bilder hinzu...")
            self._add_custom_images(doc)
            pages_added += len(self.custom_images)
        
        # Seite N+1: Produktdatenblätter
        if self.pdf_config_options.get('include_product_datasheets', True):
            print("📄 Füge Produktdatenblätter hinzu...")
            self._add_product_datasheets(doc)
            pages_added += 1
        
        # Seite N+2: Firmendokumente
        if self.pdf_config_options.get('include_company_documents', True):
            print("📄 Füge Firmendokumente hinzu...")
            self._add_company_documents(doc)
            pages_added += 1
        
        # Seite N+4: Finanzierungsberechnungen (NEU!)
        if self.pdf_config_options.get('include_financing_calculations', True):
            print("📄 Füge Finanzierungsberechnungen hinzu...")
            self._add_financing_calculations_page(doc)
            pages_added += 1
        
        # Seite N+5: Anhänge
        if self.pdf_config_options.get('include_appendices', True):
            print("📄 Füge Anhänge hinzu...")
            self._add_appendices(doc)
            pages_added += 1
        
        # Fallback: Falls keine Seiten hinzugefügt wurden, füge zumindest eine Zusammenfassungsseite hinzu
        if pages_added == 0:
            print("⚠️ Keine zusätzlichen Seiten konfiguriert - füge Standard-Zusammenfassung hinzu")
            self._add_fallback_summary_page(doc)
            pages_added += 1
        
        print(f"📄 {pages_added} zusätzliche Seiten generiert")
        
        # Zu Bytes konvertieren
        pdf_bytes = doc.tobytes()
        doc.close()
        
        return pdf_bytes
    
    def _add_extended_project_overview(self, doc: fitz.Document):
        """Moderne erweiterte Projektübersicht - Seite 6"""
        page = doc.new_page(width=595, height=842)  # A4
        
        if MODERN_DESIGN_AVAILABLE:
            # Moderner Header
            y_pos = MODERN_DESIGNER.add_modern_header(
                page, 
                "Erweiterte Projektübersicht", 
                "Detaillierte Analyse Ihrer Photovoltaikanlage",
                6
            )
            
            # Projekt-Status Karten (3 Spalten)
            card_width = 150
            card_height = 80
            spacing = 15
            
            # Karte 1: Gesamtleistung
            total_power = self.analysis_results.get('anlage_kwp', 8.4)
            MODERN_DESIGNER.add_metric_card(
                page, 50, y_pos, card_width, card_height,
                "Anlagenleistung", f"{total_power:.1f}", "kWp", "positive"
            )
            
            # Karte 2: Jährliche Produktion
            annual_production = self.analysis_results.get('annual_pv_production_kwh', 8251.92)
            MODERN_DESIGNER.add_metric_card(
                page, 50 + card_width + spacing, y_pos, card_width, card_height,
                "Jahresproduktion", f"{annual_production:,.0f}".replace(',', '.'), "kWh", "positive"
            )
            
            # Karte 3: CO2-Einsparung
            co2_savings = annual_production * 0.5  # ca. 0.5kg CO2 pro kWh
            MODERN_DESIGNER.add_metric_card(
                page, 50 + 2 * (card_width + spacing), y_pos, card_width, card_height,
                "CO₂-Einsparung/Jahr", f"{co2_savings:,.0f}".replace(',', '.'), "kg", "positive"
            )
            
            y_pos += card_height + 30
            
            # Eigenverbrauchsanalyse
            battery_capacity = self.project_data.get('battery_details', {}).get('capacity_kwh', 6.1)
            MODERN_DESIGNER.add_info_box(
                page, 50, y_pos, 495, 80,
                "🔋 Eigenverbrauchsoptimierung",
                f"Mit dem integrierten {battery_capacity}kWh Batteriespeicher erreichen Sie einen optimalen Eigenverbrauchsanteil und maximale Energieunabhängigkeit. Die Anlage produziert jährlich ca. {annual_production:,.0f}kWh sauberen Strom für Ihren Haushalt.".replace(',', '.'),
                "success"
            )
            
            y_pos += 100
            
            # Kundendaten Übersicht
            customer_name = self.project_data.get('customer_name', 'Kunde')
            address = self.project_data.get('customer_address', {})
            if isinstance(address, dict):
                street = address.get('street', 'Musterstraße 1')
                city = address.get('city', '12345 Musterstadt')
                customer_address = f"{street}, {city}"
            else:
                customer_address = "Adresse nicht verfügbar"
            
            MODERN_DESIGNER.add_info_box(
                page, 50, y_pos, 240, 80,
                "👤 Kundeninformationen",
                f"Kunde: {customer_name}\nAdresse: {customer_address}\nAngebotsdatum: {datetime.now().strftime('%d.%m.%Y')}",
                "info"
            )
            
            # Technische Details
            module_count = self.project_data.get('pv_details', {}).get('module_quantity', 21)
            MODERN_DESIGNER.add_info_box(
                page, 255, y_pos, 240, 80,
                "⚡ Technische Eckdaten",
                f"Module: {module_count} Stück\nBatterie: {battery_capacity}kWh LiFePO4\nGarantie: 25 Jahre Leistungsgarantie",
                "info"
            )
            
            # Moderner Footer
            MODERN_DESIGNER.add_modern_footer(page, self.company_info.get('name', 'Ihr Photovoltaik-Partner'))
            
        else:
            # Fallback auf altes Design
            # Überschrift
            self._add_header(page, "Erweiterte Projektübersicht")
            
            # Projektdetails in strukturierter Form
            y_pos = 100
            
            # Kunde
            customer_name = self.project_data.get('customer_name', 'Kunde')
            page.insert_text((50, y_pos), f"Kunde: {customer_name}", fontsize=12)
            y_pos += 25
            
            # Adresse
            address = self.project_data.get('customer_address', {})
            if isinstance(address, dict):
                street = address.get('street', 'Musterstraße 1')
                city = address.get('city', '12345 Musterstadt')
                page.insert_text((50, y_pos), f"Adresse: {street}, {city}", fontsize=10)
                y_pos += 20
            
            # Projekt-ID
            project_id = self.project_data.get('project_id', 'TOM-90')
            page.insert_text((50, y_pos), f"Projekt-ID: {project_id}", fontsize=10)
            y_pos += 20
            
            # Datum
            current_date = datetime.now().strftime("%d.%m.%Y")
            page.insert_text((50, y_pos), f"Angebotsdatum: {current_date}", fontsize=10)
            y_pos += 30
            
            # Anlagenübersicht
            page.insert_text((50, y_pos), "Anlagenübersicht:", fontsize=12)
            y_pos += 25
            
            # Technische Daten
            anlage_kwp = self.analysis_results.get('anlage_kwp', 8.4)
            page.insert_text((70, y_pos), f"• Anlagengröße: {anlage_kwp} kWp", fontsize=10)
            y_pos += 20
            
            battery_capacity = self.project_data.get('battery_details', {}).get('capacity_kwh', 6.1)
            page.insert_text((70, y_pos), f"• Batteriekapazität: {battery_capacity} kWh", fontsize=10)
            y_pos += 20
            
            module_count = self.project_data.get('pv_details', {}).get('module_quantity', 21)
            page.insert_text((70, y_pos), f"• Anzahl Module: {module_count} Stück", fontsize=10)
            y_pos += 20
            
            # Erwartete Erträge
            annual_production = self.analysis_results.get('annual_pv_production_kwh', 8251.92)
        page.insert_text((70, y_pos), f"• Erwartete Jahresproduktion: {annual_production:,.0f} kWh", fontsize=10)
        y_pos += 20
        
        # Zusätzliche Details falls in den benutzerdefinierten Bereichen angegeben
        if self.selected_offer_title_text:
            y_pos += 20
            page.insert_text((50, y_pos), "Angebots-Titel:", fontsize=12)
            y_pos += 20
            page.insert_text((70, y_pos), self.selected_offer_title_text[:200] + "...", fontsize=10)
    
    def _add_detailed_technical_specs(self, doc: fitz.Document):
        """Moderne detaillierte technische Spezifikationen - Seite 7"""
        page = doc.new_page(width=595, height=842)
        
        if MODERN_DESIGN_AVAILABLE:
            # Moderner Header
            y_pos = MODERN_DESIGNER.add_modern_header(
                page, 
                "Technische Spezifikationen", 
                "Detaillierte Komponentenübersicht",
                7
            )
            
            # PV-Module Spezifikationen
            MODERN_DESIGNER.add_info_box(
                page, 50, y_pos, 495, 60,
                "☀️ Photovoltaik-Module",
                f"Hochleistungsmodule mit {self.analysis_results.get('anlage_kwp', 8.4)}kWp Gesamtleistung für maximale Energieausbeute bei optimaler Flächennutzung.",
                "info"
            )
            
            y_pos += 80
            
            # Technische Daten Tabelle - PV Module
            pv_headers = ["Eigenschaft", "Spezifikation", "Wert", "Einheit"]
            pv_data = [
                ["Modultyp", "Monokristallin", "Hochleistung", "-"],
                ["Modulleistung", "400Wp", "Premium-Qualität", "Wp"],
                ["Anzahl Module", str(self.project_data.get('pv_details', {}).get('module_quantity', 21)), "Optimiert", "Stück"],
                ["Gesamtleistung", f"{self.analysis_results.get('anlage_kwp', 8.4)}", "Maximale Ausbeute", "kWp"],
                ["Wirkungsgrad", ">21%", "Hohe Effizienz", "%"],
                ["Garantie", "25 Jahre", "Leistungsgarantie", "Jahre"]
            ]
            
            MODERN_DESIGNER.add_data_table(
                page, 50, y_pos, 495, pv_headers, pv_data, True
            )
            
            y_pos += len(pv_data) * 25 + 50
            
            # Batteriespeicher Spezifikationen
            battery_capacity = self.project_data.get('battery_details', {}).get('capacity_kwh', 6.1)
            
            # Progress Bar für Batteriekapazität (als Anteil der Tagesproduktion)
            daily_production = self.analysis_results.get('annual_pv_production_kwh', 8251.92) / 365
            battery_ratio = (battery_capacity / daily_production) * 100 if daily_production > 0 else 50
            battery_ratio = min(battery_ratio, 100)  # Max 100%
            
            MODERN_DESIGNER.add_info_box(
                page, 50, y_pos, 240, 80,
                "🔋 Batteriespeicher",
                f"Lithium-Eisenphosphat (LiFePO4) Technologie mit {battery_capacity}kWh Kapazität für optimale Eigenverbrauchsquote.",
                "success"
            )
            
            MODERN_DESIGNER.add_info_box(
                page, 255, y_pos, 240, 80,
                "⚡ Wechselrichter",
                "Hybrid-Wechselrichter mit intelligenter Batterieverwaltung und Netzeinspeisung für maximale Flexibilität.",
                "info"
            )
            
            y_pos += 100
            
            # Batteriekapazität Visualisierung
            page.insert_text((50, y_pos), "Speicherkapazität im Verhältnis zur Tagesproduktion:", 
                           fontsize=MODERN_DESIGNER.fonts['body'], 
                           color=MODERN_DESIGNER.colors['dark_gray'], fontname="helv")
            y_pos += 20
            
            MODERN_DESIGNER.add_progress_bar(
                page, 50, y_pos, 400, battery_ratio, 
                f"Batteriekapazität: {battery_capacity}kWh", "accent_green"
            )
            
            # Moderner Footer
            MODERN_DESIGNER.add_modern_footer(page, self.company_info.get('name', 'Ihr Photovoltaik-Partner'))
            
        else:
            # Fallback auf altes Design
            self._add_header(page, "Detaillierte technische Spezifikationen")
            
            y_pos = 100
            
            # PV-Module
            page.insert_text((50, y_pos), "Photovoltaik-Module:", fontsize=12)
            y_pos += 25
        
        pv_details = self.project_data.get('pv_details', {})
        if pv_details:
            module_power = pv_details.get('module_power_wp', 400)
            page.insert_text((70, y_pos), f"• Modulleistung: {module_power} Wp", fontsize=10)
            y_pos += 20
            
            module_type = pv_details.get('module_type', 'Monokristallin')
            page.insert_text((70, y_pos), f"• Modultyp: {module_type}", fontsize=10)
            y_pos += 20
        
        # Wechselrichter
        y_pos += 20
        page.insert_text((50, y_pos), "Wechselrichter:", fontsize=12)
        y_pos += 25
        
        inverter_details = self.project_data.get('inverter_details', {})
        if inverter_details:
            inverter_power = inverter_details.get('power_kw', 8.0)
            page.insert_text((70, y_pos), f"• Leistung: {inverter_power} kW", fontsize=10)
            y_pos += 20
            
            inverter_type = inverter_details.get('type', 'String-Wechselrichter')
            page.insert_text((70, y_pos), f"• Typ: {inverter_type}", fontsize=10)
            y_pos += 20
        
        # Batteriespeicher
        y_pos += 20
        page.insert_text((50, y_pos), "Batteriespeicher:", fontsize=12)
        y_pos += 25
        
        battery_details = self.project_data.get('battery_details', {})
        if battery_details:
            battery_capacity = battery_details.get('capacity_kwh', 6.1)
            page.insert_text((70, y_pos), f"• Speicherkapazität: {battery_capacity} kWh", fontsize=10)
            y_pos += 20
            
            battery_type = battery_details.get('type', 'Lithium-Ionen')
            page.insert_text((70, y_pos), f"• Batterietyp: {battery_type}", fontsize=10)
            y_pos += 20
        
        # Dachdetails
        y_pos += 20
        page.insert_text((50, y_pos), "Dach-Spezifikationen:", fontsize=12)
        y_pos += 25
        
        roof_details = self.project_data.get('roof_details', {})
        if roof_details:
            roof_angle = roof_details.get('angle', 30)
            page.insert_text((70, y_pos), f"• Dachneigung: {roof_angle}°", fontsize=10)
            y_pos += 20
            
            roof_orientation = roof_details.get('orientation', 'Süd')
            page.insert_text((70, y_pos), f"• Ausrichtung: {roof_orientation}", fontsize=10)
            y_pos += 20
    
    def _add_financial_analysis_page(self, doc: fitz.Document):
        """Moderne detaillierte Finanzanalyse - Seite 8"""
        page = doc.new_page(width=595, height=842)
        
        if MODERN_DESIGN_AVAILABLE:
            # Moderner Header
            y_pos = MODERN_DESIGNER.add_modern_header(
                page, 
                "Finanzanalyse & ROI", 
                "Wirtschaftlichkeitsberechnung über 25 Jahre",
                8
            )
            
            # Kosten-Übersicht Karten
            card_width = 150
            card_height = 80
            spacing = 15
            
            total_costs = self.analysis_results.get('total_system_cost_eur', 25000)
            subsidies = self.analysis_results.get('total_subsidies_eur', 0)
            net_costs = total_costs - subsidies
            
            # Karte 1: Investitionskosten
            MODERN_DESIGNER.add_metric_card(
                page, 50, y_pos, card_width, card_height,
                "Investitionskosten", f"{total_costs:,.0f}".replace(',', '.'), "EUR", "neutral"
            )
            
            # Karte 2: Förderungen
            MODERN_DESIGNER.add_metric_card(
                page, 50 + card_width + spacing, y_pos, card_width, card_height,
                "Förderungen", f"-{subsidies:,.0f}".replace(',', '.'), "EUR", "positive" if subsidies > 0 else "neutral"
            )
            
            # Karte 3: Netto-Investition
            MODERN_DESIGNER.add_metric_card(
                page, 50 + 2 * (card_width + spacing), y_pos, card_width, card_height,
                "Netto-Investition", f"{net_costs:,.0f}".replace(',', '.'), "EUR", "neutral"
            )
            
            y_pos += card_height + 30
            
            # Ersparnis-Berechnung über 25 Jahre
            savings_with = self.analysis_results.get('total_savings_with_storage_eur', 36958)
            savings_without = self.analysis_results.get('total_savings_without_storage_eur', 29150)
            annual_savings = self.analysis_results.get('annual_savings_eur', 1500)
            
            MODERN_DESIGNER.add_info_box(
                page, 50, y_pos, 495, 80,
                "💰 Gesamtersparnis (25 Jahre)",
                f"Mit Batteriespeicher: {savings_with:,.0f} EUR | Ohne Speicher: {savings_without:,.0f} EUR\nVorteil mit Speicher: +{savings_with - savings_without:,.0f} EUR | Jährliche Ersparnis: ca. {annual_savings:,.0f} EUR".replace(',', '.'),
                "success"
            )
            
            y_pos += 100
            
            # ROI-Berechnung
            roi_years = self.analysis_results.get('payback_period_years', 12.5)
            roi_percentage = (25 - roi_years) / 25 * 100 if roi_years < 25 else 0
            
            # ROI Visualisierung
            page.insert_text((50, y_pos), "Return on Investment (ROI):", 
                           fontsize=MODERN_DESIGNER.fonts['heading_3'], 
                           color=MODERN_DESIGNER.colors['dark_gray'], fontname="hebo")
            y_pos += 25
            
            MODERN_DESIGNER.add_progress_bar(
                page, 50, y_pos, 400, roi_percentage, 
                f"Amortisation nach {roi_years:.1f} Jahren", "accent_green"
            )
            
            y_pos += 40
            
            # Detaillierte ROI-Tabelle
            roi_headers = ["Jahr", "Ersparnis", "Kumuliert", "ROI-Status"]
            roi_data = []
            
            cumulative_savings = 0
            for year in [5, 10, 15, 20, 25]:
                year_savings = annual_savings * year
                cumulative_savings = year_savings
                roi_status = "✅ Amortisiert" if year >= roi_years else "⏳ In Arbeit"
                
                roi_data.append([
                    f"{year}",
                    f"{year_savings:,.0f} €".replace(',', '.'),
                    f"{cumulative_savings:,.0f} €".replace(',', '.'),
                    roi_status
                ])
            
            MODERN_DESIGNER.add_data_table(
                page, 50, y_pos, 495, roi_headers, roi_data, True
            )
            
            # Moderner Footer
            MODERN_DESIGNER.add_modern_footer(page, self.company_info.get('name', 'Ihr Photovoltaik-Partner'))
            
        else:
            # Fallback auf altes Design
            self._add_header(page, "Finanzielle Analyse & ROI-Berechnung")
            
            y_pos = 100
            
            # Investitionskosten
            page.insert_text((50, y_pos), "Investitionskosten:", fontsize=12)
            y_pos += 25
            
            total_costs = self.analysis_results.get('total_system_cost_eur', 25000)
            page.insert_text((70, y_pos), f"• Gesamtkosten: {total_costs:,.0f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 20
            
            # Förderungen (falls verfügbar)
            subsidies = self.analysis_results.get('total_subsidies_eur', 0)
        if subsidies > 0:
            page.insert_text((70, y_pos), f"• Förderungen: -{subsidies:,.0f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 20
            net_costs = total_costs - subsidies
            page.insert_text((70, y_pos), f"• Netto-Investition: {net_costs:,.0f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 20
        
        # Ersparnis-Berechnungen
        y_pos += 20
        page.insert_text((50, y_pos), "Ersparnis-Berechnungen (25 Jahre):", fontsize=12)
        y_pos += 25
        
        savings_with = self.analysis_results.get('total_savings_with_storage_eur', 36958)
        page.insert_text((70, y_pos), f"• Mit Speicher: {savings_with:,.0f} EUR".replace(',', '.'), fontsize=10)
        y_pos += 20
        
        savings_without = self.analysis_results.get('total_savings_without_storage_eur', 29150)
        page.insert_text((70, y_pos), f"• Ohne Speicher: {savings_without:,.0f} EUR".replace(',', '.'), fontsize=10)
        y_pos += 20
        
        # ROI-Berechnung
        y_pos += 20
        page.insert_text((50, y_pos), "Return on Investment (ROI):", fontsize=12)
        y_pos += 25
        
        roi_years = self.analysis_results.get('payback_period_years', 12.5)
        page.insert_text((70, y_pos), f"• Amortisationsdauer: {roi_years:.1f} Jahre", fontsize=10)
        y_pos += 20
        
        # Jährliche Einsparungen
        annual_savings = self.analysis_results.get('annual_savings_eur', 1500)
        page.insert_text((70, y_pos), f"• Jährliche Einsparungen: {annual_savings:,.0f} EUR".replace(',', '.'), fontsize=10)
        y_pos += 20
    
    def _add_charts_visualization_page(self, doc: fitz.Document):
        """Moderne Diagramme und Visualisierungen - Seite 9"""
        page = doc.new_page(width=595, height=842)
        
        if MODERN_DESIGN_AVAILABLE:
            # Moderner Header
            y_pos = MODERN_DESIGNER.add_modern_header(
                page, 
                "Visualisierungen & Diagramme", 
                "Grafische Darstellung Ihrer Energieanalysis",
                9
            )
            
            # Chart-Container 1: Monatliche Produktion
            MODERN_DESIGNER.create_modern_chart_placeholder(
                page, 50, y_pos, 495, 160,
                "📈 Monatliche Produktion vs. Verbrauch"
            )
            
            y_pos += 180
            
            # Kennzahlen zur Produktion
            annual_production = self.analysis_results.get('annual_pv_production_kwh', 8251.92)
            monthly_avg = annual_production / 12
            
            card_width = 240
            spacing = 15
            
            # Performance-Karten
            MODERN_DESIGNER.add_metric_card(
                page, 50, y_pos, card_width, 60,
                "Durchschnittliche Monatsproduktion", f"{monthly_avg:,.0f}".replace(',', '.'), "kWh", "positive"
            )
            
            MODERN_DESIGNER.add_metric_card(
                page, 50 + card_width + spacing, y_pos, card_width, 60,
                "Beste Produktionsmonate", "Mai - Juli", "", "positive"
            )
            
            y_pos += 80
            
            # Chart-Container 2: Ersparnis-Entwicklung
            MODERN_DESIGNER.create_modern_chart_placeholder(
                page, 50, y_pos, 495, 160,
                "💰 Kumulative Ersparnis-Entwicklung (25 Jahre)"
            )
            
            y_pos += 180
            
            # Prognose-Info
            savings_total = self.analysis_results.get('total_savings_with_storage_eur', 36958)
            MODERN_DESIGNER.add_info_box(
                page, 50, y_pos, 495, 60,
                "📊 Prognose-Hinweis",
                f"Die Berechnungen basieren auf aktuellen Strompreisen und einer jährlichen Preissteigerung von 3%. Gesamtersparnis über 25 Jahre: {savings_total:,.0f} EUR".replace(',', '.'),
                "info"
            )
            
            # Moderner Footer
            MODERN_DESIGNER.add_modern_footer(page, self.company_info.get('name', 'Ihr Photovoltaik-Partner'))
            
        else:
            # Fallback auf altes Design
            self._add_header(page, "Diagramme & Visualisierungen")
            
            y_pos = 100
            
            # Hier würden die tatsächlichen Diagramme aus analysis_results eingefügt
            # Für jetzt als Platzhalter
            
            page.insert_text((50, y_pos), "Monatliche Produktion & Verbrauch:", fontsize=12)
            y_pos += 25
            
            # Platzhalter für Diagramm
            rect = fitz.Rect(50, y_pos, 545, y_pos + 150)
            page.draw_rect(rect, color=0.8, width=1)
            page.insert_text((250, y_pos + 75), "[Diagramm: Monatliche Werte]", fontsize=10)
            y_pos += 170
            
            page.insert_text((50, y_pos), "Ersparnis-Entwicklung:", fontsize=12)
            y_pos += 25
            
            # Platzhalter für zweites Diagramm
            rect = fitz.Rect(50, y_pos, 545, y_pos + 150)
            page.draw_rect(rect, color=0.8, width=1)
            page.insert_text((250, y_pos + 75), "[Diagramm: Ersparnis über Zeit]", fontsize=10)
            
            # TODO: Hier echte Diagramme aus den analysis_results einfügen
            # if 'monthly_production_chart_bytes' in self.analysis_results:
            #     chart_bytes = self.analysis_results['monthly_production_chart_bytes']
            #     # Chart einfügen
    
    def _add_environmental_impact_page(self, doc: fitz.Document):
        """Fügt Umweltauswirkungen hinzu"""
        page = doc.new_page(width=595, height=842)
        
        self._add_header(page, "Umweltauswirkungen & CO2-Bilanz")
        
        y_pos = 100
        
        # CO2-Einsparungen
        page.insert_text((50, y_pos), "CO2-Einsparungen:", fontsize=12)
        y_pos += 25
        
        co2_savings_kg = self.analysis_results.get('annual_co2_savings_kg', 3500)
        page.insert_text((70, y_pos), f"• Jährlich: {co2_savings_kg:,.0f} kg CO2".replace(',', '.'), fontsize=10)
        y_pos += 20
        
        co2_savings_25_years = co2_savings_kg * 25
        page.insert_text((70, y_pos), f"• Über 25 Jahre: {co2_savings_25_years:,.0f} kg CO2".replace(',', '.'), fontsize=10)
        y_pos += 30
        
        # Äquivalente
        page.insert_text((50, y_pos), "Das entspricht:", fontsize=12)
        y_pos += 25
        
        # Kilometer mit Auto
        km_equivalent = co2_savings_kg / 0.12 if co2_savings_kg else 15266
        page.insert_text((70, y_pos), f"• {km_equivalent:,.0f} km Autofahrt (jährlich)".replace(',', '.'), fontsize=10)
        y_pos += 20
        
        # Bäume
        trees_equivalent = co2_savings_kg / 22 if co2_savings_kg else 159
        page.insert_text((70, y_pos), f"• {trees_equivalent:.0f} gepflanzte Bäume (jährlich)", fontsize=10)
        y_pos += 30
        
        # Energieerzeugung aus erneuerbaren Quellen
        page.insert_text((50, y_pos), "Erneuerbare Energieerzeugung:", fontsize=12)
        y_pos += 25
        
        annual_production = self.analysis_results.get('annual_pv_production_kwh', 8251.92)
        page.insert_text((70, y_pos), f"• Jährliche saubere Energie: {annual_production:,.0f} kWh".replace(',', '.'), fontsize=10)
        y_pos += 20
        
        total_25_years = annual_production * 25
        page.insert_text((70, y_pos), f"• Über 25 Jahre: {total_25_years:,.0f} kWh".replace(',', '.'), fontsize=10)
    
    def _add_features_highlights_page(self, doc: fitz.Document):
        """Fügt Features & Highlights hinzu"""
        page = doc.new_page(width=595, height=842)
        
        self._add_header(page, "Features & Highlights")
        
        y_pos = 100
        
        # Hauptvorteile
        page.insert_text((50, y_pos), "Hauptvorteile Ihrer Solaranlage:", fontsize=12)
        y_pos += 30
        
        # Unabhängigkeitsgrad
        independence = self.analysis_results.get('independence_degree_percent', 54)
        page.insert_text((70, y_pos), f"🏠 {independence}% Energieunabhängigkeit", fontsize=11)
        y_pos += 25
        
        # Eigenverbrauch
        self_consumption = self.analysis_results.get('self_consumption_percent', 42)
        page.insert_text((70, y_pos), f"⚡ {self_consumption}% Eigenverbrauchsanteil", fontsize=11)
        y_pos += 25
        
        # Rendite
        roi_years = self.analysis_results.get('payback_period_years', 12.5)
        page.insert_text((70, y_pos), f"💰 Amortisation in {roi_years:.1f} Jahren", fontsize=11)
        y_pos += 25
        
        # Umweltschutz
        co2_savings_kg = self.analysis_results.get('annual_co2_savings_kg', 3500)
        page.insert_text((70, y_pos), f"🌱 {co2_savings_kg:,.0f} kg CO2 Einsparung pro Jahr".replace(',', '.'), fontsize=11)
        y_pos += 35
        
        # Technische Highlights
        page.insert_text((50, y_pos), "Technische Highlights:", fontsize=12)
        y_pos += 30
        
        anlage_kwp = self.analysis_results.get('anlage_kwp', 8.4)
        page.insert_text((70, y_pos), f"🔧 Hochwertige {anlage_kwp} kWp Anlage", fontsize=11)
        y_pos += 25
        
        battery_capacity = self.project_data.get('battery_details', {}).get('capacity_kwh', 6.1)
        page.insert_text((70, y_pos), f"🔋 Intelligenter {battery_capacity} kWh Batteriespeicher", fontsize=11)
        y_pos += 25
        
        page.insert_text((70, y_pos), "📱 App-basierte Überwachung & Steuerung", fontsize=11)
        y_pos += 25
        
        page.insert_text((70, y_pos), "🛡️ 25 Jahre Herstellergarantie", fontsize=11)
        y_pos += 35
        
        # Service & Support
        page.insert_text((50, y_pos), "Service & Support:", fontsize=12)
        y_pos += 30
        
        page.insert_text((70, y_pos), "🔧 Professionelle Installation durch zertifizierte Techniker", fontsize=11)
        y_pos += 25
        
        page.insert_text((70, y_pos), "📞 24/7 Kundenservice & Remote-Monitoring", fontsize=11)
        y_pos += 25
        
        page.insert_text((70, y_pos), "🔄 Regelmäßige Wartung & Performance-Checks", fontsize=11)
    
    def _add_comparison_tables_page(self, doc: fitz.Document):
        """Fügt Vergleichstabellen hinzu"""
        page = doc.new_page(width=595, height=842)
        
        self._add_header(page, "Vergleichstabellen")
        
        y_pos = 100
        
        # Vergleich mit/ohne Speicher
        page.insert_text((50, y_pos), "Vergleich: Mit vs. Ohne Batteriespeicher", fontsize=12)
        y_pos += 30
        
        # Tabellenkopf
        headers = ["", "Ohne Speicher", "Mit Speicher", "Vorteil"]
        col_widths = [150, 120, 120, 100]
        x_positions = [50, 200, 320, 440]
        
        # Header zeichnen
        for i, header in enumerate(headers):
            page.insert_text((x_positions[i], y_pos), header, fontsize=10)
        
        y_pos += 20
        
        # Trennlinie
        page.draw_line(fitz.Point(50, y_pos), fitz.Point(540, y_pos), color=0.5, width=1)
        y_pos += 15
        
        # Datenzeilen
        savings_without = self.analysis_results.get('total_savings_without_storage_eur', 29150)
        savings_with = self.analysis_results.get('total_savings_with_storage_eur', 36958)
        difference = savings_with - savings_without
        
        page.insert_text((x_positions[0], y_pos), "Ersparnis (25 Jahre)", fontsize=10)
        page.insert_text((x_positions[1], y_pos), f"{savings_without:,.0f} EUR".replace(',', '.'), fontsize=10)
        page.insert_text((x_positions[2], y_pos), f"{savings_with:,.0f} EUR".replace(',', '.'), fontsize=10)
        page.insert_text((x_positions[3], y_pos), f"+{difference:,.0f} EUR".replace(',', '.'), fontsize=10, color=(0, 0.6, 0))
        y_pos += 20
        
        # Eigenverbrauch
        eigenverbrauch_ohne = 35
        eigenverbrauch_mit = self.analysis_results.get('self_consumption_percent', 42)
        
        page.insert_text((x_positions[0], y_pos), "Eigenverbrauch", fontsize=10)
        page.insert_text((x_positions[1], y_pos), f"{eigenverbrauch_ohne}%", fontsize=10)
        page.insert_text((x_positions[2], y_pos), f"{eigenverbrauch_mit}%", fontsize=10)
        page.insert_text((x_positions[3], y_pos), f"+{eigenverbrauch_mit - eigenverbrauch_ohne}%", fontsize=10, color=(0, 0.6, 0))
        y_pos += 20
        
        # Unabhängigkeit
        unabhaengigkeit_ohne = 30
        unabhaengigkeit_mit = self.analysis_results.get('independence_degree_percent', 54)
        
        page.insert_text((x_positions[0], y_pos), "Energieunabhängigkeit", fontsize=10)
        page.insert_text((x_positions[1], y_pos), f"{unabhaengigkeit_ohne}%", fontsize=10)
        page.insert_text((x_positions[2], y_pos), f"{unabhaengigkeit_mit}%", fontsize=10)
        page.insert_text((x_positions[3], y_pos), f"+{unabhaengigkeit_mit - unabhaengigkeit_ohne}%", fontsize=10, color=(0, 0.6, 0))
    
    def _add_custom_text_areas(self, doc: fitz.Document):
        """Fügt benutzerdefinierte Textbereiche hinzu"""
        if not self.custom_text_areas:
            return
        
        for i, text_area in enumerate(self.custom_text_areas):
            page = doc.new_page(width=595, height=842)
            
            title = text_area.get('title', f'Benutzerdefinierter Bereich {i+1}')
            content = text_area.get('content', '')
            
            self._add_header(page, title)
            
            y_pos = 100
            
            # Text umbrechen und einfügen
            lines = content.split('\n')
            for line in lines:
                if y_pos > 780:  # Neue Seite bei Bedarf
                    page = doc.new_page(width=595, height=842)
                    y_pos = 50
                
                page.insert_text((50, y_pos), line, fontsize=11)
                y_pos += 15
    
    def _add_custom_images(self, doc: fitz.Document):
        """Fügt benutzerdefinierte Bilder hinzu"""
        if not self.custom_images:
            return
        
        for i, image_data in enumerate(self.custom_images):
            page = doc.new_page(width=595, height=842)
            
            title = image_data.get('title', f'Bild {i+1}')
            image_bytes = image_data.get('image_bytes')
            description = image_data.get('description', '')
            
            self._add_header(page, title)
            
            if image_bytes:
                try:
                    # Bild einfügen - mit sicherer Bildverarbeitung
                    processed_image = self._process_image_data(image_bytes)
                    if processed_image:
                        img_rect = fitz.Rect(50, 100, 545, 400)
                        page.insert_image(img_rect, stream=processed_image)
                        print(f"✅ Bild {title} erfolgreich hinzugefügt")
                    else:
                        page.insert_text((50, 100), f"⚠️ Bild konnte nicht verarbeitet werden: {title}", fontsize=11)
                        print(f"⚠️ Bild konnte nicht verarbeitet werden: {title}")
                    
                    # Beschreibung
                    if description:
                        page.insert_text((50, 420), description, fontsize=11)
                except Exception as e:
                    error_msg = f"Bild konnte nicht geladen werden: {title}\n Fehler: {str(e)}"
                    page.insert_text((50, 100), error_msg, fontsize=11)
                    print(f"❌ {error_msg}")
            else:
                page.insert_text((50, 100), f"⚠️ Keine Bilddaten verfügbar für: {title}", fontsize=11)
    
    def _add_product_datasheets(self, doc: fitz.Document):
        """Fügt Produktdatenblätter hinzu"""
        if not self.list_products_func:
            return
        
        page = doc.new_page(width=595, height=842)
        self._add_header(page, "Produktdatenblätter")
        
        y_pos = 100
        
        # Liste der verwendeten Produkte
        page.insert_text((50, y_pos), "Verwendete Produkte in diesem Angebot:", fontsize=12)
        y_pos += 30
        
        # Hier würden die tatsächlichen Produktdatenblätter eingefügt
        # Für jetzt als Platzhalter
        products = ["PV-Module", "Wechselrichter", "Batteriespeicher", "Montagesystem"]
        
        for product in products:
            page.insert_text((70, y_pos), f"• {product}", fontsize=11)
            y_pos += 20
        
        y_pos += 20
        page.insert_text((50, y_pos), "Detaillierte Datenblätter siehe Anhang.", fontsize=10)
    
    def _add_company_documents(self, doc: fitz.Document):
        """Fügt Firmendokumente hinzu"""
        if not self.db_list_company_documents_func or not self.active_company_id:
            return
        
        try:
            documents = self.db_list_company_documents_func(self.active_company_id, None)
            
            if documents:
                page = doc.new_page(width=595, height=842)
                self._add_header(page, "Firmendokumente")
                
                y_pos = 100
                
                page.insert_text((50, y_pos), "Weitere Informationen zu unserem Unternehmen:", fontsize=12)
                y_pos += 30
                
                for doc_info in documents:
                    if isinstance(doc_info, dict):
                        doc_name = doc_info.get('display_name', doc_info.get('file_name', 'Dokument'))
                        doc_type = doc_info.get('document_type', 'Unbekannt')
                        
                        page.insert_text((70, y_pos), f"• {doc_name} ({doc_type})", fontsize=11)
                        y_pos += 20
                        
                        if y_pos > 780:  # Neue Seite bei Bedarf
                            page = doc.new_page(width=595, height=842)
                            y_pos = 50
        except Exception as e:
            # Fehler ignorieren, da es sich um zusätzliche Funktionen handelt
            pass
    
    def _add_financing_calculations_page(self, doc: fitz.Document):
        """Fügt detaillierte Finanzierungsberechnungen hinzu"""
        page = doc.new_page(width=595, height=842)
        
        self._add_header(page, "Finanzierungsberechnungen & Vergleich")
        
        y_pos = 100
        
        # Einführungstext
        page.insert_text((50, y_pos), "Flexible Finanzierungslösungen für Ihre Solaranlage:", fontsize=12)
        y_pos += 30
        
        # Kreditfinanzierung
        page.insert_text((50, y_pos), "💳 Kreditfinanzierung (Hausbank):", fontsize=11)
        y_pos += 25
        
        # Versuche Finanzierungsberechnungen aus Session State zu holen
        loan_calc = None
        kfw_calc = None
        leasing_calc = None
        
        try:
            import streamlit as st
            loan_calc = st.session_state.get('central_pdf_loan_calculation')
            kfw_calc = st.session_state.get('central_pdf_kfw_calculation')
            leasing_calc = st.session_state.get('central_pdf_leasing_calculation')
        except:
            pass
        
        if loan_calc:
            # Echte Berechnungsdaten verwenden
            page.insert_text((70, y_pos), f"• Darlehenssumme: {loan_calc.get('darlehenssumme', 25000):,.0f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Monatliche Rate: {loan_calc.get('monatliche_rate', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Gesamtzinsen: {loan_calc.get('gesamtzinsen', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Gesamtkosten: {loan_calc.get('gesamtkosten', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 25
        else:
            # Fallback mit Beispieldaten
            total_costs = self.analysis_results.get('total_system_cost_eur', 25000)
            try:
                from financial_tools import calculate_annuity
                fallback_calc = calculate_annuity(total_costs, 3.5, 15)
                if "error" not in fallback_calc:
                    page.insert_text((70, y_pos), f"• Darlehenssumme: {total_costs:,.0f} EUR".replace(',', '.'), fontsize=10)
                    y_pos += 18
                    page.insert_text((70, y_pos), f"• Monatliche Rate: {fallback_calc['monatliche_rate']:,.2f} EUR".replace(',', '.'), fontsize=10)
                    y_pos += 18
                    page.insert_text((70, y_pos), f"• Zinssatz: 3,5% p.a. (15 Jahre Laufzeit)", fontsize=10)
                    y_pos += 18
                    page.insert_text((70, y_pos), f"• Gesamtkosten: {fallback_calc['gesamtkosten']:,.2f} EUR".replace(',', '.'), fontsize=10)
                    y_pos += 25
                else:
                    page.insert_text((70, y_pos), "• Individuelle Berechnung auf Anfrage", fontsize=10)
                    y_pos += 25
            except:
                page.insert_text((70, y_pos), "• Individuelle Berechnung auf Anfrage", fontsize=10)
                y_pos += 25
        
        # KfW-Förderkredit
        page.insert_text((50, y_pos), "🏦 KfW-Förderkredit (Programm 270):", fontsize=11)
        y_pos += 25
        
        if kfw_calc:
            # Echte KfW-Berechnungsdaten
            page.insert_text((70, y_pos), f"• Förderfähiger Betrag: bis 150.000 EUR", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Tilgungszuschuss: {kfw_calc.get('tilgungszuschuss', 0):,.0f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Monatliche Rate: {kfw_calc.get('monatliche_rate', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Effektive Kosten: {kfw_calc.get('effektive_kreditkosten', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 25
        else:
            # Standard KfW-Informationen
            page.insert_text((70, y_pos), "• Zinsgünstige Darlehen bis 150.000 EUR", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), "• Tilgungszuschüsse bis zu 10.500 EUR möglich", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), "• Zinssätze ab 1,5% p.a. (abhängig von Bonität)", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), "• Wir unterstützen bei der Antragstellung", fontsize=10)
            y_pos += 25
        
        # Leasing-Alternative
        page.insert_text((50, y_pos), "🚗 Leasing-Alternative:", fontsize=11)
        y_pos += 25
        
        if leasing_calc:
            # Echte Leasing-Daten
            page.insert_text((70, y_pos), f"• Monatliche Rate: {leasing_calc.get('monatliche_rate', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Laufzeit: {leasing_calc.get('laufzeit_jahre', 15)} Jahre", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Keine Anfangsinvestition erforderlich", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), f"• Gesamtkosten: {leasing_calc.get('gesamtkosten', 0):,.2f} EUR".replace(',', '.'), fontsize=10)
            y_pos += 25
        else:
            # Standard Leasing-Informationen
            page.insert_text((70, y_pos), "• Monatliche Raten ab 149 EUR", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), "• Keine Anfangsinvestition erforderlich", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), "• Wartung und Service inklusive", fontsize=10)
            y_pos += 18
            page.insert_text((70, y_pos), "• Rundum-Sorglos-Paket", fontsize=10)
            y_pos += 25
        
        # Vergleichstabelle
        y_pos += 10
        page.insert_text((50, y_pos), "📊 Finanzierungsvergleich:", fontsize=11)
        y_pos += 25
        
        # Tabelle zeichnen
        table_x = 50
        table_y = y_pos
        table_width = 495
        table_height = 120
        
        # Tabellenrahmen
        table_rect = fitz.Rect(table_x, table_y, table_x + table_width, table_y + table_height)
        page.draw_rect(table_rect, width=1, color=0.3)
        
        # Spaltenbreiten
        col_widths = [150, 115, 115, 115]
        
        # Header
        headers = ["Finanzierungsart", "Monatliche Rate", "Laufzeit", "Gesamtkosten"]
        x_pos = table_x + 5
        y_pos = table_y + 15
        
        for i, header in enumerate(headers):
            page.insert_text((x_pos, y_pos), header, fontsize=9)
            x_pos += col_widths[i]
        
        # Trennlinie nach Header
        y_pos += 5
        page.draw_line(fitz.Point(table_x, y_pos), fitz.Point(table_x + table_width, y_pos), width=0.5, color=0.5)
        
        # Datenzeilen
        financing_data = []
        
        if loan_calc:
            financing_data.append([
                "Hausbank-Kredit",
                f"{loan_calc.get('monatliche_rate', 0):,.0f} EUR".replace(',', '.'),
                f"{loan_calc.get('laufzeit_jahre', 15)} Jahre",
                f"{loan_calc.get('gesamtkosten', 0):,.0f} EUR".replace(',', '.')
            ])
        
        if kfw_calc:
            financing_data.append([
                "KfW-Förderkredit",
                f"{kfw_calc.get('monatliche_rate', 0):,.0f} EUR".replace(',', '.'),
                f"{kfw_calc.get('laufzeit_jahre', 15)} Jahre",
                f"{kfw_calc.get('effektive_kreditkosten', 0):,.0f} EUR".replace(',', '.')
            ])
        
        if leasing_calc:
            financing_data.append([
                "Leasing",
                f"{leasing_calc.get('monatliche_rate', 0):,.0f} EUR".replace(',', '.'),
                f"{leasing_calc.get('laufzeit_jahre', 15)} Jahre",
                f"{leasing_calc.get('gesamtkosten', 0):,.0f} EUR".replace(',', '.')
            ])
        
        # Fallback-Daten wenn keine Berechnungen vorhanden
        if not financing_data:
            financing_data = [
                ["Hausbank-Kredit", "189 EUR", "15 Jahre", "34.020 EUR"],
                ["KfW-Förderkredit", "165 EUR", "15 Jahre", "29.700 EUR"],
                ["Leasing", "149 EUR", "15 Jahre", "26.820 EUR"]
            ]
        
        # Daten in Tabelle einfügen
        y_pos += 10
        for row_data in financing_data:
            x_pos = table_x + 5
            for i, cell_data in enumerate(row_data):
                page.insert_text((x_pos, y_pos), cell_data, fontsize=9)
                x_pos += col_widths[i]
            y_pos += 15
        
        # Empfehlung
        y_pos = table_y + table_height + 20
        page.insert_text((50, y_pos), "💡 Unsere Empfehlung:", fontsize=11)
        y_pos += 20
        
        if kfw_calc and loan_calc and kfw_calc.get('effektive_kreditkosten', 999999) < loan_calc.get('gesamtkosten', 0):
            page.insert_text((70, y_pos), "KfW-Förderkredit bietet die beste Gesamtkondition durch Tilgungszuschuss!", fontsize=10, color=(0, 0.6, 0))
        elif leasing_calc and loan_calc and leasing_calc.get('monatliche_rate', 999) < loan_calc.get('monatliche_rate', 0):
            page.insert_text((70, y_pos), "Leasing für niedrige monatliche Belastung ohne Eigenkapital!", fontsize=10, color=(0, 0.6, 0))
        else:
            page.insert_text((70, y_pos), "Gerne erstellen wir Ihnen ein individuelles Finanzierungskonzept!", fontsize=10, color=(0, 0.6, 0))
        
        y_pos += 25
        
        # Kontaktinformationen
        page.insert_text((50, y_pos), "📞 Beratung:", fontsize=10)
        y_pos += 18
        page.insert_text((70, y_pos), "• Kostenlose Finanzierungsberatung", fontsize=9)
        y_pos += 15
        page.insert_text((70, y_pos), "• Unterstützung bei Förderanträgen", fontsize=9)
        y_pos += 15
        page.insert_text((70, y_pos), "• Vergleich aller Finanzierungsoptionen", fontsize=9)
    
    def _add_appendices(self, doc: fitz.Document):
        """Fügt Anhänge hinzu"""
        page = doc.new_page(width=595, height=842)
        self._add_header(page, "Anhänge")
        
        y_pos = 100
        
        # Technische Unterlagen
        page.insert_text((50, y_pos), "Technische Unterlagen:", fontsize=12)
        y_pos += 25
        
        appendices = [
            "Datenblätter PV-Module",
            "Datenblätter Wechselrichter", 
            "Datenblätter Batteriespeicher",
            "Montage- und Installationsrichtlinien",
            "Garantiebedingungen",
            "Wartungsempfehlungen"
        ]
        
        for appendix in appendices:
            page.insert_text((70, y_pos), f"• {appendix}", fontsize=11)
            y_pos += 20
    
    def _add_fallback_summary_page(self, doc: fitz.Document):
        """Fügt eine Standard-Zusammenfassungsseite hinzu als Fallback"""
        page = doc.new_page(width=595, height=842)  # A4
        
        # Überschrift
        self._add_header(page, "Angebotszusammenfassung")
        
        y_pos = 100
        
        # Projekt-Grunddaten
        page.insert_text((50, y_pos), "Projekt-Grunddaten:", fontsize=14)
        y_pos += 30
        
        # PV-Kapazität
        pv_capacity = self.project_data.get('pv_capacity_kwp', 'N/A')
        page.insert_text((70, y_pos), f"• PV-Anlagenleistung: {pv_capacity} kWp", fontsize=11)
        y_pos += 20
        
        # Batteriekapazität
        battery_capacity = self.project_data.get('battery_capacity_kwh', 'N/A')
        page.insert_text((70, y_pos), f"• Batteriekapazität: {battery_capacity} kWh", fontsize=11)
        y_pos += 20
        
        # Wirtschaftlichkeit
        y_pos += 30
        page.insert_text((50, y_pos), "Wirtschaftlichkeit:", fontsize=14)
        y_pos += 30
        
        # Gesamtinvestition
        total_investment = self.analysis_results.get('total_investment', 'N/A')
        page.insert_text((70, y_pos), f"• Gesamtinvestition: {total_investment} €", fontsize=11)
        y_pos += 20
        
        # Amortisationszeit
        payback_period = self.analysis_results.get('payback_period', 'N/A')
        page.insert_text((70, y_pos), f"• Amortisationszeit: {payback_period} Jahre", fontsize=11)
        y_pos += 20
        
        # Jährliche Einsparung
        annual_savings = self.analysis_results.get('annual_savings', 'N/A')
        page.insert_text((70, y_pos), f"• Jährliche Einsparung: {annual_savings} €", fontsize=11)
        y_pos += 30
        
        # Hinweis
        y_pos += 50
        page.insert_text((50, y_pos), "Hinweis:", fontsize=12)
        y_pos += 25
        page.insert_text((50, y_pos), "Diese Zusammenfassung wurde automatisch generiert.", fontsize=10)
        y_pos += 15
        page.insert_text((50, y_pos), "Für detaillierte Informationen siehe die ersten 5 Seiten.", fontsize=10)
    
    def _create_fallback_tom90_pages(self) -> bytes:
        """Erstellt Fallback TOM-90 Seiten falls der TOM-90 Exact Renderer fehlschlägt"""
        import fitz
        
        doc = fitz.open()
        
        # Erstelle 5 Basis-Seiten als TOM-90 Fallback
        for page_num in range(1, 6):
            page = doc.new_page(width=595, height=842)  # A4
            
            # Header
            self._add_header(page, f"TOM-90 Fallback - Seite {page_num}")
            
            y_pos = 120
            
            if page_num == 1:
                # Seite 1: Deckblatt
                company_name = self.tom90_company_info.get('name', 'Firma')
                page.insert_text((50, y_pos), f"🏢 {company_name}", fontsize=18)
                y_pos += 40
                
                page.insert_text((50, y_pos), "📋 Photovoltaik-Angebot", fontsize=16)
                y_pos += 60
                
                # Projekt-Grunddaten
                pv_capacity = self.tom90_project_data.get('pv_capacity_kwp', 'N/A')
                battery_capacity = self.tom90_project_data.get('battery_capacity_kwh', 'N/A')
                
                page.insert_text((50, y_pos), f"⚡ PV-Leistung: {pv_capacity} kWp", fontsize=14)
                y_pos += 25
                page.insert_text((50, y_pos), f"🔋 Batteriekapazität: {battery_capacity} kWh", fontsize=14)
                
            elif page_num == 2:
                # Seite 2: Wirtschaftlichkeit
                page.insert_text((50, y_pos), "💰 Wirtschaftlichkeit", fontsize=16)
                y_pos += 40
                
                total_investment = self.tom90_analysis_results.get('total_investment', 'N/A')
                payback_period = self.tom90_analysis_results.get('payback_period', 'N/A')
                annual_savings = self.tom90_analysis_results.get('annual_savings', 'N/A')
                
                page.insert_text((50, y_pos), f"💸 Gesamtinvestition: {total_investment} €", fontsize=12)
                y_pos += 25
                page.insert_text((50, y_pos), f"⏰ Amortisationszeit: {payback_period} Jahre", fontsize=12)
                y_pos += 25
                page.insert_text((50, y_pos), f"💰 Jährliche Einsparung: {annual_savings} €", fontsize=12)
                
            elif page_num == 3:
                # Seite 3: Technische Details
                page.insert_text((50, y_pos), "🔧 Technische Spezifikation", fontsize=16)
                y_pos += 40
                
                page.insert_text((50, y_pos), "• Hochleistungs-PV-Module", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• Intelligenter Wechselrichter", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• Lithium-Batteriespeicher", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• Professionelles Montagesystem", fontsize=12)
                
            elif page_num == 4:
                # Seite 4: Umwelt & CO₂
                page.insert_text((50, y_pos), "🌱 Umwelt & CO₂-Bilanz", fontsize=16)
                y_pos += 40
                
                page.insert_text((50, y_pos), "• Reduzierung der CO₂-Emissionen", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• Nachhaltige Energiegewinnung", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• Beitrag zur Energiewende", fontsize=12)
                
            elif page_num == 5:
                # Seite 5: Service & Garantie
                page.insert_text((50, y_pos), "🛡️ Service & Garantie", fontsize=16)
                y_pos += 40
                
                page.insert_text((50, y_pos), "• 25 Jahre Modulgarantie", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• 10 Jahre Wechselrichtergarantie", fontsize=12)
                y_pos += 20
                page.insert_text((50, y_pos), "• Professioneller Service", fontsize=12)
            
            # Fußnote
            page.insert_text((50, 800), f"⚠️ TOM-90 Fallback-Seite {page_num} | Vollständige Daten nach Reparatur verfügbar", fontsize=8, color=(0.5, 0.5, 0.5))
        
        # PDF zu Bytes konvertieren
        pdf_bytes = doc.tobytes()
        doc.close()
        
        return pdf_bytes
    
    def _add_custom_content_text_item(self, doc: fitz.Document, item: Dict[str, Any]):
        """Fügt einen individuellen Text-Inhalt hinzu"""
        page = doc.new_page(width=595, height=842)  # A4
        
        # Titel
        title = item.get('title', 'Individueller Inhalt')
        self._add_header(page, title)
        
        y_pos = 100
        
        # Content
        content = item.get('content', 'Kein Inhalt verfügbar')
        
        # Text in Abschnitte aufteilen (einfache Zeilenumbrüche)
        lines = content.split('\n')
        
        for line in lines:
            if y_pos > 800:  # Neue Seite falls nötig
                page = doc.new_page(width=595, height=842)
                y_pos = 50
            
            if line.strip():  # Nicht-leere Zeilen
                page.insert_text((50, y_pos), line, fontsize=11)
            y_pos += 20
    
    def _add_custom_content_image_item(self, doc: fitz.Document, item: Dict[str, Any]):
        """Fügt einen individuellen Bild-Inhalt hinzu"""
        page = doc.new_page(width=595, height=842)  # A4
        
        # Titel
        title = item.get('title', 'Individuelles Bild')
        self._add_header(page, title)
        
        y_pos = 100
        
        # Bild-Daten
        image_data = item.get('data')
        filename = item.get('filename', 'Unbekannt')
        
        if image_data:
            try:
                # Bild einfügen - mit sicherer Bildverarbeitung
                processed_image = self._process_image_data(image_data)
                if processed_image:
                    import io
                    image_rect = fitz.Rect(50, y_pos, 545, y_pos + 400)  # Maximale Bildgröße
                    page.insert_image(image_rect, stream=processed_image)
                    y_pos += 420
                    print(f"✅ Individuelles Bild {title} erfolgreich hinzugefügt")
                else:
                    page.insert_text((50, y_pos), f"⚠️ Bild konnte nicht verarbeitet werden: {title}", fontsize=11)
                    y_pos += 25
                    print(f"⚠️ Bild konnte nicht verarbeitet werden: {title}")
                
                # Dateiname unter dem Bild
                page.insert_text((50, y_pos), f"Datei: {filename}", fontsize=10, color=(0.5, 0.5, 0.5))
                
            except Exception as e:
                error_msg = f"Bild konnte nicht geladen werden: {filename}\n Fehler: {str(e)}"
                page.insert_text((50, y_pos), error_msg, fontsize=11)
                print(f"❌ {error_msg}")
        else:
            # Kein Bild verfügbar
            page.insert_text((50, y_pos), "❌ Kein Bildinhalt verfügbar", fontsize=11)
            y_pos += 20
            page.insert_text((50, y_pos), f"Datei: {filename}", fontsize=10, color=(0.5, 0.5, 0.5))
        
        y_pos += 30
        
        # Rechtliche Hinweise
        page.insert_text((50, y_pos), "Rechtliche Hinweise:", fontsize=12)
        y_pos += 25
        
        legal_docs = [
            "Allgemeine Geschäftsbedingungen",
            "Datenschutzerklärung",
            "Widerrufsbelehrung",
            "Impressum"
        ]
        
        for legal_doc in legal_docs:
            page.insert_text((70, y_pos), f"• {legal_doc}", fontsize=11)
            y_pos += 20
    
    def _process_image_data(self, image_data) -> bytes:
        """
        Verarbeitet Bilddaten und stellt sicher, dass sie als Bytes-Stream vorliegen
        
        Args:
            image_data: Bilddaten in verschiedenen Formaten (bytes, base64, file path, etc.)
            
        Returns:
            bytes: Bilddaten als Bytes-Stream oder None bei Fehlern
        """
        try:
            # Fall 1: Bereits Bytes
            if isinstance(image_data, bytes):
                return image_data
            
            # Fall 2: Base64-String
            if isinstance(image_data, str):
                # Prüfe ob es base64 ist (enthält "data:image" oder ist base64-ähnlich)
                if image_data.startswith('data:image'):
                    # Data URL format: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
                    base64_data = image_data.split(',')[1]
                    return base64.b64decode(base64_data)
                elif len(image_data) > 100 and '/' not in image_data and '\\' not in image_data:
                    # Wahrscheinlich reiner base64
                    return base64.b64decode(image_data)
                else:
                    # Wahrscheinlich ein Dateipfad
                    if os.path.exists(image_data):
                        with open(image_data, 'rb') as f:
                            return f.read()
                    else:
                        print(f"⚠️ Bilddatei nicht gefunden: {image_data}")
                        return None
            
            # Fall 3: BytesIO-Objekt
            if hasattr(image_data, 'read'):
                image_data.seek(0)  # Cursor zum Anfang
                return image_data.read()
            
            # Fall 4: Streamlit UploadedFile
            if hasattr(image_data, 'getvalue'):
                return image_data.getvalue()
            
            # Fall 5: Dictionary mit image_bytes
            if isinstance(image_data, dict) and 'image_bytes' in image_data:
                return self._process_image_data(image_data['image_bytes'])
            
            print(f"⚠️ Unbekanntes Bilddatenformat: {type(image_data)}")
            return None
            
        except Exception as e:
            print(f"❌ Fehler bei Bildverarbeitung: {e}")
            return None
    
    def _add_header(self, page: fitz.Page, title: str):
        """Fügt eine Kopfzeile zu einer Seite hinzu"""
        # Firmenlogo (falls vorhanden)
        if self.tom90_company_logo_base64:
            try:
                # Verwende sichere Bildverarbeitung
                processed_logo = self._process_image_data(self.tom90_company_logo_base64)
                if processed_logo:
                    logo_rect = fitz.Rect(450, 20, 540, 60)
                    page.insert_image(logo_rect, stream=processed_logo)
                    print("✅ Firmenlogo erfolgreich hinzugefügt")
                else:
                    print("⚠️ Firmenlogo konnte nicht verarbeitet werden")
            except Exception as e:
                print(f"❌ Fehler beim Laden des Firmenlogos: {e}")

        # Titel
        page.insert_text((50, 50), title, fontsize=16, color=(0.2, 0.2, 0.6))

        # Trennlinie
        page.draw_line(fitz.Point(50, 70), fitz.Point(545, 70), color=0.7, width=1)
    
    def _add_footer(self, page: fitz.Page, current_page: int, total_pages: int):
        """Fügt professionelle Fußzeile mit Seitennummer hinzu"""
        # Trennlinie vor Footer
        page.draw_line(fitz.Point(50, 800), fitz.Point(545, 800), color=0.7, width=1)
        
        # Extrahiere Kundennachname aus project_data
        customer_name = self.project_data.get('customer_name', 'Unbekannt')
        if customer_name and customer_name != 'Unbekannt':
            # Versuche Nachname zu extrahieren (letztes Wort)
            customer_key = customer_name.split()[-1] if ' ' in customer_name else customer_name
        else:
            customer_key = 'KUNDE'
        
        # Aktuelles Datum
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        # Footer-Text zusammenstellen
        footer_text = f"Angebot {customer_key} {current_date} Seite {current_page} von {total_pages}"
        
        # Footer-Text zentriert positionieren
        text_width = len(footer_text) * 3  # Ungefähre Breite
        x_center = (595 - text_width) / 2  # A4 Breite = 595 Punkte
        
        # Footer-Text einfügen (klein und grau)
        page.insert_text((x_center, 820), footer_text, fontsize=8, color=(0.5, 0.5, 0.5))
    
    def _merge_pdfs(self, tom90_pdf_bytes: bytes, additional_pdf_bytes: bytes) -> bytes:
        """Führt TOM-90 PDF mit zusätzlichen Seiten zusammen und fügt Seitennummern hinzu"""
        
        print(f"🔍 DEBUG: TOM-90 PDF Größe: {len(tom90_pdf_bytes) if tom90_pdf_bytes else 0} bytes")
        print(f"🔍 DEBUG: Zusätzliche PDF Größe: {len(additional_pdf_bytes) if additional_pdf_bytes else 0} bytes")
        
        # TOM-90 PDF öffnen
        tom90_doc = fitz.open(stream=tom90_pdf_bytes, filetype="pdf")
        print(f"🔍 DEBUG: TOM-90 PDF hat {tom90_doc.page_count} Seiten")
        
        # Zusätzliche Seiten PDF öffnen (falls vorhanden)
        if additional_pdf_bytes:
            additional_doc = fitz.open(stream=additional_pdf_bytes, filetype="pdf")
            print(f"🔍 DEBUG: Zusätzliche PDF hat {additional_doc.page_count} Seiten")
            
            # Zusätzliche Seiten anhängen
            tom90_doc.insert_pdf(additional_doc)
            additional_doc.close()
        else:
            print("⚠️ DEBUG: Keine zusätzlichen Seiten zum Anhängen!")
        
        # Gesamtseitenzahl ermitteln
        total_pages = tom90_doc.page_count
        print(f"🔍 DEBUG: Finale PDF hat {total_pages} Seiten")
        
        # Seitennummern zu allen Seiten hinzufügen
        print(f"📄 Füge Seitennummern zu {total_pages} Seiten hinzu...")
        for page_num in range(total_pages):
            page = tom90_doc[page_num]
            current_page = page_num + 1
            
            # Footer mit Seitennummer hinzufügen
            self._add_footer(page, current_page, total_pages)
        
        # Zu Bytes konvertieren
        final_pdf_bytes = tom90_doc.tobytes()
        tom90_doc.close()
        
        print(f"✅ DEBUG: Finale PDF-Größe: {len(final_pdf_bytes)} bytes")
        return final_pdf_bytes
    
    def _create_emergency_pdf(self) -> bytes:
        """
        Notfall-PDF mit ReportLab erstellen (sehr zuverlässig) - mit professionellen Footern
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Daten extrahieren
        company_name = self.company_info.get('name', 'Unbekannte Firma')
        project_data = self.project_data
        analysis_results = self.analysis_results
        
        # Kundennachname für Footer extrahieren
        customer_name = self.project_data.get('customer_name', 'Unbekannt')
        if customer_name and customer_name != 'Unbekannt':
            customer_key = customer_name.split()[-1] if ' ' in customer_name else customer_name
        else:
            customer_key = 'KUNDE'
        
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        # PDF erstellen
        y_position = 750
        
        # Header
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, y_position, "🚀 PV-Angebot (Mega Hybrid Notfall)")
        
        y_position -= 50
        p.setFont("Helvetica", 14)
        p.drawString(50, y_position, f"🏢 Firma: {company_name}")
        
        y_position -= 25
        p.drawString(50, y_position, f"📅 Erstellt am: {current_date}")
        
        # Projektdaten
        if project_data:
            y_position -= 40
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, "⚡ Projektdaten:")
            
            y_position -= 25
            p.setFont("Helvetica", 12)
            
            pv_capacity = project_data.get('pv_capacity_kwp', 'N/A')
            battery_capacity = project_data.get('battery_capacity_kwh', 'N/A')
            
            p.drawString(70, y_position, f"• PV-Leistung: {pv_capacity} kWp")
            y_position -= 20
            p.drawString(70, y_position, f"• Batteriekapazität: {battery_capacity} kWh")
        
        # Analyseergebnisse
        if analysis_results:
            y_position -= 40
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y_position, "📊 Wirtschaftlichkeit:")
            
            y_position -= 25
            p.setFont("Helvetica", 12)
            
            total_investment = analysis_results.get('total_investment', 'N/A')
            payback_period = analysis_results.get('payback_period', 'N/A')
            annual_savings = analysis_results.get('annual_savings', 'N/A')
            
            p.drawString(70, y_position, f"• Gesamtinvestition: {total_investment} €")
            y_position -= 20
            p.drawString(70, y_position, f"• Amortisationszeit: {payback_period} Jahre")
            y_position -= 20
            p.drawString(70, y_position, f"• Jährliche Einsparung: {annual_savings} €")
        
        # Hinweis
        y_position -= 60
        p.setFont("Helvetica-Bold", 12)
        p.setFillColorRGB(0.2, 0.6, 0.9)  # Blau
        p.drawString(50, y_position, "💡 HINWEIS:")
        
        y_position -= 25
        p.setFont("Helvetica", 10)
        p.setFillColorRGB(0, 0, 0)  # Schwarz
        p.drawString(50, y_position, "Dieses PDF wurde mit dem Mega Hybrid Notfall-System erstellt.")
        y_position -= 15
        p.drawString(50, y_position, "Alle wichtigen Daten sind enthalten - für Details siehe Hauptsysteme.")
        
        # Professioneller Footer mit Trennlinie und Seitennummer
        p.setStrokeColorRGB(0.7, 0.7, 0.7)  # Grau
        p.line(50, 100, 545, 100)  # Trennlinie
        
        # Footer-Text (Seite 1 von 1 für Notfall-PDF)
        footer_text = f"Angebot {customer_key} {current_date} Seite 1 von 1"
        
        # Footer-Text zentriert positionieren
        text_width = len(footer_text) * 3  # Ungefähre Breite
        x_center = (595 - text_width) / 2  # A4 Breite = 595 Punkte
        
        p.setFont("Helvetica", 8)
        p.setFillColorRGB(0.5, 0.5, 0.5)  # Grau
        p.drawString(x_center, 80, footer_text)
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()


def generate_mega_hybrid_pdf(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    inclusion_options: Optional[Dict[str, Any]] = None,
    sections_to_include: Optional[List[str]] = None,
    texts: Optional[Dict[str, str]] = None,
    **kwargs
) -> bytes:
    """
    Haupt-Funktion zum Generieren des Mega-Hybrid-PDFs
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse  
        company_info: Firmeninformationen
        inclusion_options: PDF-Konfigurationsoptionen
        sections_to_include: Zu inkludierende Sektionen
        texts: Übersetzungstexte
        **kwargs: Weitere Parameter (werden in inclusion_options eingebettet)
    
    Returns:
        PDF als Bytes
    """
    
    # Kombiniere inclusion_options mit kwargs
    if inclusion_options is None:
        inclusion_options = {}
    
    # Füge alle kwargs zu inclusion_options hinzu
    combined_inclusion_options = inclusion_options.copy()
    combined_inclusion_options.update(kwargs)
    
    # Extrahiere bekannte Konstruktor-Parameter aus kwargs
    constructor_params = {
        'company_logo_base64': kwargs.get('company_logo_base64'),
        'selected_title_image_b64': kwargs.get('selected_title_image_b64'),
        'selected_offer_title_text': kwargs.get('selected_offer_title_text'),
        'selected_cover_letter_text': kwargs.get('selected_cover_letter_text'),
        'load_admin_setting_func': kwargs.get('load_admin_setting_func'),
        'save_admin_setting_func': kwargs.get('save_admin_setting_func'),
        'list_products_func': kwargs.get('list_products_func'),
        'get_product_by_id_func': kwargs.get('get_product_by_id_func'),
        'db_list_company_documents_func': kwargs.get('db_list_company_documents_func'),
        'active_company_id': kwargs.get('active_company_id'),
        'pdf_config_options': kwargs.get('pdf_config_options'),
        'custom_sections': kwargs.get('custom_sections'),
        'custom_text_areas': kwargs.get('custom_text_areas'),
        'custom_images': kwargs.get('custom_images')
    }
    
    # Entferne None-Werte
    constructor_params = {k: v for k, v in constructor_params.items() if v is not None}
    
    # Mega-Generator initialisieren
    generator = MegaTOM90HybridPDFGenerator(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        inclusion_options=combined_inclusion_options,
        sections_to_include=sections_to_include,
        texts=texts,
        **constructor_params
    )
    
    # PDF generieren
    return generator.generate_hybrid_pdf()
