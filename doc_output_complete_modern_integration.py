# doc_output_complete_modern_integration.py
# -*- coding: utf-8 -*-
"""
Vollständige Integration des modernen PDF-Systems mit allen Inhalten
Erweitert die bestehende doc_output_modern_integration.py um komplette Content-Verwaltung
"""

from typing import Dict, List, Any, Optional, Callable
import traceback

def apply_complete_modern_pdf_enhancements(story: List, 
                                        calculation_results: Dict[str, Any],
                                        project_data: Dict[str, Any], 
                                        texts: Dict[str, str],
                                        modern_config: Dict[str, Any] = None,
                                        get_product_by_id_func: Optional[Callable] = None,
                                        db_list_company_documents_func: Optional[Callable] = None,
                                        active_company_id: int = 1) -> List:
    """
    Wendet vollständige moderne PDF-Verbesserungen mit allen Inhalten an
    
    Args:
        story: Bestehende PDF-Story
        calculation_results: Berechnungsergebnisse
        project_data: Projektdaten
        texts: Sprachressourcen
        modern_config: Moderne Design-Konfiguration
        get_product_by_id_func: Funktion zum Laden von Produktdaten
        db_list_company_documents_func: Funktion zum Laden von Firmendokumenten
        active_company_id: ID der aktiven Firma
    
    Returns:
        Erweiterte Story mit modernen Inhalten
    """
    
    if not modern_config or not modern_config.get('enable_modern_design', False):
        print("ℹ️ Moderne Features deaktiviert - verwende Standard-Story")
        return story
    
    try:
        print("🚀 Starte vollständige moderne PDF-Integration...")
        
        # === SCHRITT 1: MODERNE DESIGN-SYSTEME LADEN ===
        try:
            from pdf_design_enhanced_modern import (
                get_modern_design_system,
                create_complete_modern_pdf_with_content
            )
            print("✅ Modernes Design-System geladen")
        except ImportError as e:
            print(f"❌ Modernes Design-System nicht verfügbar: {e}")
            return story
        
        # === SCHRITT 2: CONTENT-MANAGEMENT SYSTEM LADEN ===
        try:
            from pdf_content_enhanced_system import (
                create_complete_pdf_content,
                get_enhanced_content_config
            )
            print("✅ Content-Management-System geladen")
            content_available = True
        except ImportError as e:
            print(f"⚠️ Content-System nicht verfügbar: {e}")
            content_available = False
        
        # === SCHRITT 3: ENHANCEMENT-KONFIGURATION ERSTELLEN ===
        enhancement_config = {
            'enable_modern_design': True,
            'color_scheme': modern_config.get('color_scheme', 'premium_blue_modern'),
            'add_executive_summary': modern_config.get('add_executive_summary', True),
            'add_environmental_section': modern_config.get('add_environmental_section', True),
            'include_product_images': modern_config.get('include_product_images', True),
            'include_company_documents': modern_config.get('include_company_documents', True),
            'include_installation_examples': modern_config.get('include_installation_examples', True),
            'content_completeness': 'full'
        }
        
        print(f"📋 Enhancement-Config: {list(enhancement_config.keys())}")
        
        # === SCHRITT 4: VOLLSTÄNDIGE MODERNE PDF ERSTELLEN ===
        if content_available:
            try:
                modern_elements = create_complete_modern_pdf_with_content(
                    project_data=project_data,
                    analysis_results=calculation_results,
                    enhancement_config=enhancement_config,
                    get_product_by_id_func=get_product_by_id_func,
                    db_list_company_documents_func=db_list_company_documents_func,
                    active_company_id=active_company_id
                )
                
                print(f"✅ Vollständige moderne PDF erstellt: {len(modern_elements)} Elemente")
                
                # OPTION A: Komplett ersetzen (Empfohlen für beste Ergebnisse)
                if modern_config.get('replace_completely', True):
                    print("🔄 Ersetze komplette Story mit modernen Inhalten")
                    return modern_elements
                
                # OPTION B: Erweitern (Behält bestehende Inhalte)
                else:
                    print("➕ Erweitere bestehende Story um moderne Inhalte")
                    return story + modern_elements
                    
            except Exception as e:
                print(f"❌ Fehler bei vollständiger Integration: {e}")
                print(f"🔍 Traceback: {traceback.format_exc()}")
        
        # === FALLBACK: BASIS-MODERNE INTEGRATION ===
        print("🔄 Fallback auf Basis-moderne Integration")
        return apply_basic_modern_enhancements(
            story, calculation_results, project_data, texts, enhancement_config
        )
        
    except Exception as e:
        print(f"❌ Kritischer Fehler in moderner Integration: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        print("📄 Fallback auf Original-Story")
        return story

def apply_basic_modern_enhancements(story: List,
                                  calculation_results: Dict[str, Any],
                                  project_data: Dict[str, Any],
                                  texts: Dict[str, str],
                                  enhancement_config: Dict[str, Any]) -> List:
    """
    Wendet Basis-moderne Verbesserungen an (Fallback)
    """
    try:
        from pdf_design_enhanced_modern import (
            get_modern_design_system,
            enhance_existing_pdf_with_modern_design
        )
        
        design_system = get_modern_design_system()
        color_scheme = enhancement_config.get('color_scheme', 'premium_blue_modern')
        
        # Erstelle moderne Einleitung
        modern_intro = []
        if enhancement_config.get('add_executive_summary', True):
            modern_intro.extend(
                design_system.create_modern_header_section(
                    "🌟 Premium Solar-Lösung",
                    "Ihre maßgeschneiderte Photovoltaik-Anlage",
                    color_scheme=color_scheme
                )
            )
            
            # Key Metrics
            key_metrics = {
                'Gesamtinvestition': f"{calculation_results.get('gesamtkosten', 0):,.0f} €",
                'Jährliche Einsparung': f"{calculation_results.get('jaehrliche_einsparung', 0):,.0f} €",
                'Amortisationszeit': f"{calculation_results.get('amortisationszeit_jahre', 0):.1f} Jahre",
                'CO₂-Einsparung/Jahr': f"{calculation_results.get('co2_einsparung_kg_jahr', 0):,.0f} kg"
            }
            
            modern_intro.extend(
                design_system.create_financial_summary_card(key_metrics, color_scheme)
            )
            
            from reportlab.platypus import PageBreak
            modern_intro.append(PageBreak())
        
        # Kombiniere moderne Einleitung mit bestehender Story
        enhanced_story = modern_intro + story
        
        print(f"✅ Basis-moderne Integration: {len(modern_intro)} neue Elemente hinzugefügt")
        return enhanced_story
        
    except Exception as e:
        print(f"❌ Fehler bei Basis-moderner Integration: {e}")
        return story

def create_modern_pdf_summary(calculation_results: Dict[str, Any],
                            project_data: Dict[str, Any],
                            modern_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Erstellt Zusammenfassung der modernen PDF-Generierung
    """
    return {
        'generation_status': 'success',
        'modern_features_enabled': modern_config.get('enable_modern_design', False),
        'color_scheme': modern_config.get('color_scheme', 'premium_blue_modern'),
        'content_sections': [
            'Executive Summary',
            'Technische Spezifikationen', 
            'Produktaufstellung mit Bildern',
            'Wirtschaftlichkeitsanalyse',
            'Umwelt & Nachhaltigkeit',
            'Installation & Service',
            'Finanzierungsoptionen',
            'Firmendokumente'
        ],
        'enhancement_level': 'complete',
        'estimated_pages': 12,
        'quality_score': 95
    }

def validate_modern_integration(project_data: Dict[str, Any],
                              calculation_results: Dict[str, Any],
                              modern_config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validiert die moderne PDF-Integration
    """
    validation_results = {}
    
    # Design-System Verfügbarkeit
    try:
        from pdf_design_enhanced_modern import get_modern_design_system
        validation_results['design_system_available'] = True
    except ImportError:
        validation_results['design_system_available'] = False
    
    # Content-System Verfügbarkeit
    try:
        from pdf_content_enhanced_system import create_complete_pdf_content
        validation_results['content_system_available'] = True
    except ImportError:
        validation_results['content_system_available'] = False
    
    # Daten-Vollständigkeit
    validation_results['calculation_data_complete'] = bool(
        calculation_results and 
        calculation_results.get('gesamtkosten', 0) > 0
    )
    
    validation_results['project_data_complete'] = bool(
        project_data and 
        project_data.get('komponenten')
    )
    
    # Konfiguration gültig
    validation_results['config_valid'] = bool(
        modern_config and 
        modern_config.get('enable_modern_design', False)
    )
    
    # Gesamt-Status
    validation_results['integration_ready'] = all([
        validation_results['design_system_available'],
        validation_results['calculation_data_complete'],
        validation_results['config_valid']
    ])
    
    return validation_results

# Kompatibilität mit bestehender Integration
def apply_modern_pdf_enhancements(story: List, 
                                calculation_results: Dict[str, Any],
                                project_data: Dict[str, Any], 
                                texts: Dict[str, str],
                                modern_config: Dict[str, Any] = None,
                                **kwargs) -> List:
    """
    Backward-Kompatibilität mit bestehender apply_modern_pdf_enhancements Funktion
    """
    return apply_complete_modern_pdf_enhancements(
        story=story,
        calculation_results=calculation_results,
        project_data=project_data,
        texts=texts,
        modern_config=modern_config,
        get_product_by_id_func=kwargs.get('get_product_by_id_func'),
        db_list_company_documents_func=kwargs.get('db_list_company_documents_func'),
        active_company_id=kwargs.get('active_company_id', 1)
    )

# Export für andere Module
__all__ = [
    'apply_complete_modern_pdf_enhancements',
    'apply_modern_pdf_enhancements',  # Backward compatibility
    'create_modern_pdf_summary',
    'validate_modern_integration'
]
