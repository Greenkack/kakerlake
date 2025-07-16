#!/usr/bin/env python3
"""
PDF Data Status Widget
Zeigt den Status der Daten für die PDF-Erstellung an
"""

import streamlit as st
from typing import Dict, Any, Optional


def display_pdf_data_status(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    texts: Dict[str, str]
) -> None:
    """
    Zeigt den Status der verfügbaren Daten für die PDF-Erstellung an.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        company_info: Firmendaten
        texts: Text-Dictionary
    """
    
    try:
        from pdf_generator import validate_pdf_data
        
        validation_result = validate_pdf_data(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info
        )
        
        # Status-Container
        status_container = st.container()
        
        with status_container:
            st.markdown("### 📊 Datenstatus für PDF-Erstellung")
            
            # Gesamtstatus
            if validation_result['is_valid']:
                st.success("✅ Alle erforderlichen Daten sind verfügbar!")
            else:
                st.warning("⚠️ Einige Daten fehlen oder sind unvollständig")
            
            # Metriken
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Vollständigkeit",
                    value=f"{validation_result.get('completeness_score', 0):.0f}%",
                    delta=None,
                    help="Prozentsatz der verfügbaren Daten"
                )
            
            with col2:
                st.metric(
                    label="Warnungen",
                    value=validation_result['warnings'],
                    delta=None,
                    help="Anzahl der Datenwarnungen"
                )
            
            with col3:
                st.metric(
                    label="Kritische Fehler",
                    value=validation_result['critical_errors'],
                    delta=None,
                    help="Anzahl kritischer Datenfehler"
                )
            
            # Detaillierte Liste der fehlenden Daten
            if validation_result['missing_data']:
                with st.expander("🔍 Details zu fehlenden Daten"):
                    for missing_item in validation_result['missing_data']:
                        st.write(f"• {missing_item}")
            
            # Empfehlungen
            if not validation_result['is_valid']:
                st.info(
                    "💡 **Empfehlung:** "
                    "Vervollständigen Sie die fehlenden Daten für eine optimale PDF-Qualität. "
                    "Alternativ wird ein Fallback-PDF mit verfügbaren Daten erstellt."
                )
                
    except ImportError:
        st.warning("PDF-Datenvalidierung nicht verfügbar")
    except Exception as e:
        st.error(f"Fehler beim Laden des Datenstatus: {e}")


def display_compact_pdf_data_status(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    texts: Dict[str, str]
) -> Optional[Dict[str, Any]]:
    """
    Zeigt eine kompakte Version des PDF-Datenstatus an.
    
    Returns:
        Validierungsergebnis oder None bei Fehlern
    """
    
    try:
        from pdf_generator import validate_pdf_data
        
        validation_result = validate_pdf_data(
            project_data=project_data,
            analysis_results=analysis_results,
            company_info=company_info
        )
        
        # Kompakte Statusanzeige
        if validation_result['is_valid']:
            st.success("✅ PDF-Daten vollständig")
        elif validation_result['critical_errors'] > 0:
            st.error(f"❌ {validation_result['critical_errors']} kritische Fehler")
        else:
            st.warning(f"⚠️ {validation_result['warnings']} Warnungen")
            
        return validation_result
        
    except ImportError:
        st.info("ℹ️ Datenvalidierung nicht verfügbar")
        return None
    except Exception as e:
        st.error(f"Fehler: {e}")
        return None


def get_pdf_readiness_color(validation_result: Dict[str, Any]) -> str:
    """
    Gibt die Farbe für den PDF-Readiness-Status zurück.
    
    Returns:
        Farbcode als String
    """
    if validation_result['is_valid']:
        return "#28a745"  # Grün
    elif validation_result['critical_errors'] > 0:
        return "#dc3545"  # Rot
    else:
        return "#ffc107"  # Gelb


def create_pdf_status_badge(validation_result: Dict[str, Any]) -> str:
    """
    Erstellt ein HTML-Badge für den PDF-Status.
    
    Returns:
        HTML-String für das Badge
    """
    if validation_result['is_valid']:
        return '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">✅ Bereit</span>'
    elif validation_result['critical_errors'] > 0:
        return '<span style="background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">❌ Fehler</span>'
    else:
        return '<span style="background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 12px; font-size: 12px;">⚠️ Warnung</span>'
