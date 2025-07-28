"""
ENHANCED CENTRAL PDF SYSTEM
===========================
Erweitert das zentrale PDF-System um ALLE ursprünglichen Features
ohne etwas zu löschen! Macht alles zentral verfügbar.

ALLE FEATURES BLEIBEN ERHALTEN:
- ✍️ Gestaltbare Textbereiche hinzufügen
- 🖼️ Zusätzliche Bilder / Fotos hinzufügen  
- ⭐ Features / Highlights auswählen
- 📑 Reihenfolge & Inhalte der Sektionen
- 📋 Erweiterte PDF-Abschnitte
- 🚀 WOW Features (Experimental)
- 📊 Datenstatus für PDF-Erstellung
- 🔧 System-Status & verfügbare Features
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import base64
import time
import traceback
import os
from datetime import datetime
import io
import pandas as pd

# Import des ursprünglichen zentralen Systems
from central_pdf_system import PDF_MANAGER, CENTRAL_PDF_UI

def generate_unique_key(base_key: str) -> str:
    """Generiert einen eindeutigen Key mit Zeitstempel"""
    timestamp = int(time.time() * 1000000) % 1000000
    return f"{base_key}_{timestamp}"

def _show_enhanced_system_status():
    """Zeigt den erweiterten System-Status an"""
    st.markdown("#### 🔧 System-Status & verfügbare Features")
    
    # Originaler System-Status aus central_pdf_system
    status = PDF_MANAGER.get_system_status()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        icon = "✅" if status.get('standard', False) else "❌"
        st.markdown(f"**{icon} STANDARD**")
        if status.get('standard', False):
            st.caption("Klassisches PDF-Layout")
        else:
            st.caption("Nicht verfügbar")
    
    with col2:
        icon = "✅" if status.get('tom90', False) else "❌"
        st.markdown(f"**{icon} TOM90**")
        if status.get('tom90', False):
            st.caption("Moderne 5-Seiten Version")
        else:
            st.caption("Import-Fehler")
    
    with col3:
        icon = "✅" if status.get('mega_hybrid', False) else "❌"
        st.markdown(f"**{icon} MEGA_HYBRID**")
        if status.get('mega_hybrid', False):
            st.caption("TOM-90 + Standard kombiniert")
        else:
            st.caption("Nicht verfügbar")
    
    with col4:
        icon = "✅" if status.get('preview', False) else "❌"
        st.markdown(f"**{icon} PREVIEW**")
        if status.get('preview', False):
            st.caption("Interaktive Vorschau")
        else:
            st.caption("Nicht verfügbar")

def _show_original_data_status(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]):
    """Zeigt den originalen Datenstatus für PDF-Erstellung an"""
    
    # Basisdaten prüfen
    customer_data_ok = bool(project_data.get('customer_data'))
    pv_data_ok = bool(project_data.get('pv_details') or project_data.get('pv_modules'))
    inverter_data_ok = bool(project_data.get('inverter_details') or project_data.get('wechselrichter'))
    calculation_ok = bool(analysis_results and len(analysis_results) > 3)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        icon = "✅" if customer_data_ok else "❌"
        st.markdown(f"{icon} **Kundendaten**")
    
    with col2:
        icon = "✅" if pv_data_ok else "❌"
        st.markdown(f"{icon} **PV-Module**")
    
    with col3:
        icon = "✅" if inverter_data_ok else "❌"
        st.markdown(f"{icon} **Wechselrichter**")
    
    with col4:
        icon = "✅" if calculation_ok else "❌"
        st.markdown(f"{icon} **Berechnung**")
    
    # Gesamtstatus
    all_ok = customer_data_ok and pv_data_ok and inverter_data_ok and calculation_ok
    
    if all_ok:
        st.success("✅ Alle Daten vollständig - PDF kann mit allen Features erstellt werden")
    else:
        st.warning("⚠️ PDF kann erstellt werden, enthält aber möglicherweise nicht alle gewünschten Informationen.")
        st.info("Bei unvollständigen Daten wird ein vereinfachtes PDF mit den verfügbaren Informationen erstellt.")

def _render_title_image_selection(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    """Rendert die Titelbild-Auswahl"""
    try:
        title_templates = load_admin_setting_func('pdf_title_image_templates', [])
        if title_templates:
            selected_template = st.selectbox(
                "Vorlage:",
                options=[t.get('name', f'Template {i+1}') for i, t in enumerate(title_templates)],
                key="enhanced_title_image_selection"
            )
            
            # Finde das ausgewählte Template
            for template in title_templates:
                if template.get('name') == selected_template:
                    st.session_state['central_pdf_selected_title_image_b64'] = template.get('data')
                    break
        else:
            st.info("Keine Titelbilder verfügbar")
            st.session_state['central_pdf_selected_title_image_b64'] = None
    except Exception as e:
        st.error(f"Fehler beim Laden der Titelbilder: {e}")

def _render_offer_title_selection(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    """Rendert die Angebots-Titel-Auswahl"""
    try:
        offer_templates = load_admin_setting_func('pdf_offer_title_templates', [])
        if offer_templates:
            selected_template = st.selectbox(
                "Vorlage:",
                options=[t.get('name', f'Titel {i+1}') for i, t in enumerate(offer_templates)],
                key="enhanced_offer_title_selection"
            )
            
            # Finde das ausgewählte Template
            for template in offer_templates:
                if template.get('name') == selected_template:
                    st.session_state['central_pdf_selected_offer_title_text'] = template.get('content', 'Angebot für Ihre Photovoltaikanlage')
                    break
        else:
            st.info("Keine Titel-Templates verfügbar")
            st.session_state['central_pdf_selected_offer_title_text'] = "Angebot für Ihre Photovoltaikanlage"
    except Exception as e:
        st.error(f"Fehler beim Laden der Titel: {e}")

def _render_cover_letter_selection(load_admin_setting_func: Callable, save_admin_setting_func: Callable):
    """Rendert die Anschreiben-Auswahl"""
    try:
        letter_templates = load_admin_setting_func('pdf_cover_letter_templates', [])
        if letter_templates:
            selected_template = st.selectbox(
                "Vorlage:",
                options=[t.get('name', f'Anschreiben {i+1}') for i, t in enumerate(letter_templates)],
                key="enhanced_cover_letter_selection"
            )
            
            # Finde das ausgewählte Template  
            for template in letter_templates:
                if template.get('name') == selected_template:
                    st.session_state['central_pdf_selected_cover_letter_text'] = template.get('content', 'Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse.')
                    break
        else:
            st.info("Keine Anschreiben-Templates verfügbar")
            st.session_state['central_pdf_selected_cover_letter_text'] = "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse."
    except Exception as e:
        st.error(f"Fehler beim Laden der Anschreiben: {e}")

def _render_template_preview():
    """Rendert die Template-Vorschau"""
    st.markdown("**Aktuelle Auswahl:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Titelbild-Vorschau
        title_image_b64 = st.session_state.get('central_pdf_selected_title_image_b64')
        if title_image_b64:
            try:
                st.image(base64.b64decode(title_image_b64), caption="Titelbild-Vorschau", width=200)
            except:
                st.info("Titelbild-Vorschau nicht verfügbar")
        else:
            st.info("Kein Titelbild ausgewählt")
    
    with col2:
        # Text-Vorschau
        offer_title = st.session_state.get('central_pdf_selected_offer_title_text', 'Kein Titel')
        cover_letter = st.session_state.get('central_pdf_selected_cover_letter_text', 'Kein Anschreiben')
        
        st.markdown("**Titel:**")
        st.info(offer_title[:100] + "..." if len(offer_title) > 100 else offer_title)
        
        st.markdown("**Anschreiben:**")
        st.info(cover_letter[:100] + "..." if len(cover_letter) > 100 else cover_letter)

def _render_branding_documents_section(company_info: Dict[str, Any], active_company_id: Optional[int], db_list_company_documents_func: Callable):
    """Rendert die Branding & Dokumente Sektion"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Firmenbranding**")
        include_logo = st.checkbox("Firmenlogo einbinden", value=True, key="enhanced_include_logo")
        include_company_info = st.checkbox("Firmeninformationen", value=True, key="enhanced_include_company_info")
        
        if company_info.get('logo_base64'):
            st.success("✅ Firmenlogo verfügbar")
        else:
            st.warning("⚠️ Kein Firmenlogo vorhanden")
    
    with col2:
        st.markdown("**Zusätzliche Firmendokumente**")
        
        selected_doc_ids = []
        if active_company_id and callable(db_list_company_documents_func):
            try:
                company_docs = db_list_company_documents_func(active_company_id, None)
                if company_docs:
                    for doc in company_docs:
                        doc_name = doc.get('display_name', f"Dokument {doc.get('id')}")
                        if st.checkbox(doc_name, key=f"enhanced_doc_{doc.get('id')}"):
                            selected_doc_ids.append(doc.get('id'))
                    
                    if selected_doc_ids:
                        st.success(f"✅ {len(selected_doc_ids)} Dokument(e) ausgewählt")
                else:
                    st.info("Keine Firmendokumente verfügbar")
            except Exception as e:
                st.error(f"Fehler beim Laden der Dokumente: {e}")
        else:
            st.info("Dokumentenzugriff nicht verfügbar")
    
    # Session State aktualisieren
    st.session_state['central_pdf_branding'] = {
        'include_logo': include_logo,
        'include_company_info': include_company_info,
        'selected_doc_ids': selected_doc_ids
    }

def _render_main_sections_selection():
    """Rendert die Hauptsektionen-Auswahl"""
    
    sections = {
        "ProjectOverview": "📋 Projektübersicht",
        "TechnicalComponents": "🔧 Technische Komponenten", 
        "CostDetails": "💰 Kostenaufstellung",
        "Economics": "📊 Wirtschaftlichkeit",
        "SimulationDetails": "⚡ Simulationsdetails",
        "CO2Savings": "🌱 CO₂-Einsparung",
        "Visualizations": "📈 Visualisierungen",
        "FutureAspects": "🚀 Zukunftsaspekte"
    }
    
    selected_sections = []
    
    cols = st.columns(4)
    for i, (section_key, section_name) in enumerate(sections.items()):
        with cols[i % 4]:
            if st.checkbox(section_name, value=True, key=f"enhanced_section_{section_key}"):
                selected_sections.append(section_key)
    
    st.session_state['central_pdf_selected_sections'] = selected_sections
    return selected_sections

def _render_charts_visualization_selection(analysis_results: Dict[str, Any]):
    """Rendert die Diagramm- und Visualisierungs-Auswahl"""
    
    charts = {
        'monthly_prod_cons_chart_bytes': '📊 Monatliche Produktion/Verbrauch',
        'cost_projection_chart_bytes': '💰 Kostenprojektion',
        'cumulative_cashflow_chart_bytes': '💹 Kumulativer Cashflow',
        'consumption_coverage_pie_chart_bytes': '🥧 Verbrauchsdeckung',
        'pv_usage_pie_chart_bytes': '⚡ PV-Nutzung',
        'annual_savings_chart_bytes': '💵 Jährliche Einsparungen',
        'roi_development_chart_bytes': '📈 ROI-Entwicklung',
        'co2_savings_chart_bytes': '🌱 CO₂-Einsparungen',
        'battery_usage_chart_bytes': '🔋 Batterienuntzung',
        'energy_flow_chart_bytes': '⚡ Energiefluss',
        'seasonal_analysis_chart_bytes': '🌤️ Saisonale Analyse',
        'grid_interaction_chart_bytes': '🔌 Netzinteraktion',
        'efficiency_comparison_chart_bytes': '⚖️ Effizienzvergleich',
        'maintenance_schedule_chart_bytes': '🔧 Wartungsplan',
        'weather_impact_chart_bytes': '🌦️ Wettereinfluss',
        'load_profile_chart_bytes': '📊 Lastprofil',
        'generation_forecast_chart_bytes': '🔮 Erzeugungsprognose',
        'financial_summary_chart_bytes': '💰 Finanzübersicht',
        'performance_monitoring_chart_bytes': '📈 Performance-Monitoring',
        'system_comparison_chart_bytes': '⚖️ Systemvergleich',
        'investment_timeline_chart_bytes': '⏱️ Investment-Zeitlinie',
        'payback_analysis_chart_bytes': '💎 Amortisationsanalyse'
    }
    
    selected_charts = []
    available_charts = []
    
    # Prüfe verfügbare Charts
    if analysis_results:
        for chart_key in charts.keys():
            if chart_key in analysis_results and analysis_results[chart_key]:
                available_charts.append(chart_key)
    
    if available_charts:
        st.info(f"📊 {len(available_charts)} Diagramme verfügbar")
        
        # Schnellauswahl-Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Alle auswählen", key="select_all_charts_enhanced"):
                for chart_key in available_charts:
                    st.session_state[f"enhanced_chart_{chart_key}"] = True
                st.rerun()
        
        with col2: 
            if st.button("Wichtigste auswählen", key="select_essential_charts_enhanced"):
                essential_charts = [
                    'monthly_prod_cons_chart_bytes',
                    'cost_projection_chart_bytes', 
                    'cumulative_cashflow_chart_bytes',
                    'consumption_coverage_pie_chart_bytes',
                    'annual_savings_chart_bytes'
                ]
                for chart_key in available_charts:
                    st.session_state[f"enhanced_chart_{chart_key}"] = chart_key in essential_charts
                st.rerun()
        
        with col3:
            if st.button("Alle abwählen", key="deselect_all_charts_enhanced"):
                for chart_key in available_charts:
                    st.session_state[f"enhanced_chart_{chart_key}"] = False
                st.rerun()
        
        # Checkbox-Grid für alle verfügbaren Charts
        cols = st.columns(3)
        for i, chart_key in enumerate(available_charts):
            with cols[i % 3]:
                chart_name = charts.get(chart_key, chart_key)
                if st.checkbox(chart_name, key=f"enhanced_chart_{chart_key}"):
                    selected_charts.append(chart_key)
    else:
        st.warning("⚠️ Keine Diagramme in den Analysedaten gefunden")
    
    st.session_state['central_pdf_selected_charts'] = selected_charts
    return selected_charts

def _render_financing_calculations_section():
    """Rendert die Finanzierungsberechnungen-Sektion"""
    st.markdown("### 💰 Finanzierungsberechnungen")
    
    # Finanzierungsoptionen
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💳 Kreditfinanzierung**")
        
        # Kreditparameter
        loan_amount = st.number_input(
            "Kreditbetrag (€):",
            min_value=1000,
            max_value=500000,
            value=25000,
            step=1000,
            key="enhanced_loan_amount"
        )
        
        interest_rate = st.slider(
            "Zinssatz (% p.a.):",
            min_value=0.5,
            max_value=8.0,
            value=3.5,
            step=0.1,
            key="enhanced_interest_rate"
        )
        
        loan_term = st.selectbox(
            "Laufzeit:",
            options=[5, 10, 15, 20, 25],
            index=2,  # 15 Jahre
            key="enhanced_loan_term"
        )
        
        # Kreditberechnung durchführen
        if st.button("🧮 Kredit berechnen", key="calculate_loan"):
            try:
                from financial_tools import calculate_annuity
                
                loan_result = calculate_annuity(
                    principal=loan_amount,
                    annual_interest_rate=interest_rate,
                    duration_years=loan_term
                )
                
                if "error" not in loan_result:
                    st.success("✅ Kreditberechnung erfolgreich!")
                    
                    # Ergebnisse speichern
                    st.session_state['central_pdf_loan_calculation'] = loan_result
                    
                    # Ergebnisse anzeigen
                    st.markdown("**📊 Kreditdetails:**")
                    st.write(f"💰 Monatliche Rate: {loan_result['monatliche_rate']:,.2f} €".replace(',', '.'))
                    st.write(f"💸 Gesamtzinsen: {loan_result['gesamtzinsen']:,.2f} €".replace(',', '.'))
                    st.write(f"📈 Gesamtkosten: {loan_result['gesamtkosten']:,.2f} €".replace(',', '.'))
                    
                else:
                    st.error(f"❌ Fehler bei der Berechnung: {loan_result['error']}")
                    
            except ImportError:
                st.error("❌ Finanzierungsmodul nicht verfügbar!")
            except Exception as e:
                st.error(f"❌ Fehler bei der Berechnung: {e}")
    
    with col2:
        st.markdown("**🏦 KfW-Förderung**")
        
        # KfW-Parameter
        kfw_eligible = st.checkbox(
            "KfW-förderfähig",
            value=True,
            key="enhanced_kfw_eligible",
            help="Ist die Anlage für KfW-Förderung geeignet?"
        )
        
        if kfw_eligible:
            kfw_program = st.selectbox(
                "KfW-Programm:",
                options=["KfW 270 (Erneuerbare Energien)", "KfW 261 (Wohngebäude)", "KfW 262 (Klimafreundlicher Neubau)"],
                key="enhanced_kfw_program"
            )
            
            subsidy_rate = st.slider(
                "Tilgungszuschuss (%):",
                min_value=0,
                max_value=40,
                value=10,
                step=5,
                key="enhanced_subsidy_rate"
            )
            
            kfw_interest = st.slider(
                "KfW-Zinssatz (% p.a.):",
                min_value=0.1,
                max_value=3.0,  
                value=1.5,
                step=0.1,
                key="enhanced_kfw_interest"
            )
            
            # KfW-Berechnung
            if st.button("🏦 KfW-Finanzierung berechnen", key="calculate_kfw"):
                try:
                    from financial_tools import calculate_annuity
                    
                    # KfW kann bis zu 150.000€ finanzieren
                    kfw_max_amount = min(loan_amount, 150000)
                    subsidy_amount = kfw_max_amount * (subsidy_rate / 100)
                    net_loan_amount = kfw_max_amount - subsidy_amount
                    
                    kfw_result = calculate_annuity(
                        principal=net_loan_amount,
                        annual_interest_rate=kfw_interest,
                        duration_years=loan_term
                    )
                    
                    if "error" not in kfw_result:
                        st.success("✅ KfW-Berechnung erfolgreich!")
                        
                        # KfW-spezifische Anpassungen
                        kfw_result['tilgungszuschuss'] = subsidy_amount
                        kfw_result['effektive_kreditkosten'] = kfw_result['gesamtkosten'] - subsidy_amount
                        
                        # Ergebnisse speichern
                        st.session_state['central_pdf_kfw_calculation'] = kfw_result
                        
                        # Ergebnisse anzeigen
                        st.markdown("**🏦 KfW-Details:**")
                        st.write(f"💰 Kreditbetrag: {kfw_max_amount:,.2f} €".replace(',', '.'))
                        st.write(f"🎁 Tilgungszuschuss: {subsidy_amount:,.2f} €".replace(',', '.'))
                        st.write(f"💸 Netto-Kredit: {net_loan_amount:,.2f} €".replace(',', '.'))
                        st.write(f"📈 Monatliche Rate: {kfw_result['monatliche_rate']:,.2f} €".replace(',', '.'))
                        st.write(f"✨ Ersparnis ggü. Hausbank: {st.session_state.get('central_pdf_loan_calculation', {}).get('gesamtkosten', 0) - kfw_result['effektive_kreditkosten']:,.2f} €".replace(',', '.'))
                        
                    else:
                        st.error(f"❌ Fehler bei der KfW-Berechnung: {kfw_result['error']}")
                        
                except ImportError:
                    st.error("❌ Finanzierungsmodul nicht verfügbar!")
                except Exception as e:
                    st.error(f"❌ Fehler bei der KfW-Berechnung: {e}")
        else:
            st.info("ℹ️ Keine KfW-Förderung ausgewählt")
    
    # Leasing-Option
    st.markdown("---")
    st.markdown("**🚗 Leasing-Alternative**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        leasing_rate = st.number_input(
            "Monatliche Leasingrate (€):",
            min_value=50,
            max_value=2000,
            value=150,
            step=10,
            key="enhanced_leasing_rate"
        )
        
        leasing_term = st.selectbox(
            "Leasinglaufzeit (Jahre):",
            options=[10, 15, 20, 25],
            index=1,  # 15 Jahre
            key="enhanced_leasing_term"
        )
    
    with col2:
        if st.button("🚗 Leasing berechnen", key="calculate_leasing"):
            try:
                from financial_tools import calculate_leasing_costs
                
                # Leasingfaktor berechnen: monatliche Rate / Investitionssumme * 100
                leasing_factor = (leasing_rate / loan_amount) * 100 if loan_amount > 0 else 2.5
                duration_months = int(leasing_term * 12)
                
                leasing_result = calculate_leasing_costs(
                    total_investment=loan_amount,
                    leasing_factor=leasing_factor,
                    duration_months=duration_months
                )
                
                # Ergebnisse speichern
                st.session_state['central_pdf_leasing_calculation'] = leasing_result
                
                st.success("✅ Leasing-Berechnung erfolgreich!")
                st.write(f"💰 Gesamtkosten: {leasing_result.get('gesamtkosten', leasing_rate * leasing_term * 12):,.2f} €".replace(',', '.'))
                
            except ImportError:
                # Fallback-Berechnung
                total_leasing_cost = leasing_rate * leasing_term * 12
                leasing_result = {
                    'monatliche_rate': leasing_rate,
                    'gesamtkosten': total_leasing_cost,
                    'laufzeit_jahre': leasing_term
                }
                st.session_state['central_pdf_leasing_calculation'] = leasing_result
                st.success("✅ Leasing-Berechnung (vereinfacht) erfolgreich!")
                st.write(f"💰 Gesamtkosten: {total_leasing_cost:,.2f} €".replace(',', '.'))
            except Exception as e:
                st.error(f"❌ Fehler bei der Leasing-Berechnung: {e}")
    
    # Finanzierungsvergleich
    if (st.session_state.get('central_pdf_loan_calculation') and 
        st.session_state.get('central_pdf_leasing_calculation')):
        
        st.markdown("---")
        st.markdown("### 📊 Finanzierungsvergleich")
        
        loan_calc = st.session_state['central_pdf_loan_calculation']
        leasing_calc = st.session_state['central_pdf_leasing_calculation']
        kfw_calc = st.session_state.get('central_pdf_kfw_calculation')
        
        comparison_data = {
            "Finanzierungsart": ["Hausbank-Kredit", "Leasing"],
            "Monatliche Rate (€)": [
                f"{loan_calc['monatliche_rate']:,.2f}".replace(',', '.'),
                f"{leasing_calc['monatliche_rate']:,.2f}".replace(',', '.')
            ],
            "Gesamtkosten (€)": [
                f"{loan_calc['gesamtkosten']:,.2f}".replace(',', '.'),
                f"{leasing_calc['gesamtkosten']:,.2f}".replace(',', '.')
            ]
        }
        
        if kfw_calc:
            comparison_data["Finanzierungsart"].append("KfW-Förderkredit")
            comparison_data["Monatliche Rate (€)"].append(f"{kfw_calc['monatliche_rate']:,.2f}".replace(',', '.'))
            comparison_data["Gesamtkosten (€)"].append(f"{kfw_calc['effektive_kreditkosten']:,.2f}".replace(',', '.'))
        
        comparison_df = pd.DataFrame(comparison_data)
        st.table(comparison_df)
        
        # Empfehlung
        if kfw_calc and kfw_calc['effektive_kreditkosten'] < loan_calc['gesamtkosten']:
            st.success("🏆 **Empfehlung: KfW-Förderkredit** - Beste Konditionen durch Tilgungszuschuss!")
        elif loan_calc['gesamtkosten'] < leasing_calc['gesamtkosten']:
            st.success("🏆 **Empfehlung: Hausbank-Kredit** - Niedrigste Gesamtkosten!")
        else:
            st.success("🏆 **Empfehlung: Leasing** - Flexibel ohne Eigenkapital!")

def _render_financing_ui_integration():
    """Integriert Finanzierungsberechnungen in die Enhanced UI"""
    
    # Finanzierungsberechnungen als eigene Sektion
    with st.expander("💰 Finanzierungsberechnungen & Vergleich", expanded=False):
        _render_financing_calculations_section()
    
    # Finanzierungsstatus anzeigen
    financing_configured = (
        st.session_state.get('central_pdf_loan_calculation') or
        st.session_state.get('central_pdf_kfw_calculation') or  
        st.session_state.get('central_pdf_leasing_calculation')
    )
    
    if financing_configured:
        st.success("✅ Finanzierungsberechnungen konfiguriert und werden in PDF integriert!")
    else:
        st.info("ℹ️ Finanzierungsberechnungen optional - können für PDF konfiguriert werden")
    """Rendert die gestaltbaren Textbereiche"""
    st.markdown("**Benutzerdefinierte Textbereiche für das PDF:**")
    
    # Anzahl der Textbereiche
    num_text_areas = st.number_input(
        "Anzahl der Textbereiche:",
        min_value=0,
        max_value=10,
        value=st.session_state.get('central_pdf_num_text_areas', 0),
        key=f"enhanced_num_text_areas_main_{int(time.time() * 1000000) % 1000000}"  # Eindeutiger Key für Hauptbereich
    )
    
    custom_text_areas = []
    
    for i in range(num_text_areas):
        with st.expander(f"Textbereich {i+1}", expanded=i == 0):
            title = st.text_input(
                f"Titel für Textbereich {i+1}:",
                value=f"Zusätzliche Informationen {i+1}",
                key=f"enhanced_text_area_title_{i}"
            )
            
            content = st.text_area(
                f"Inhalt für Textbereich {i+1}:",
                value="",
                height=150,
                key=f"enhanced_text_area_content_{i}",
                help="Hier können Sie zusätzliche Informationen eingeben, die im PDF erscheinen sollen."
            )
            
            position = st.selectbox(
                f"Position im PDF:",
                ["Nach Projektübersicht", "Nach technischen Details", "Nach Wirtschaftlichkeit", "Am Ende"],
                key=f"enhanced_text_area_position_{i}"
            )
            
            if title and content:
                custom_text_areas.append({
                    'title': title,
                    'content': content,
                    'position': position
                })
    
    st.session_state['central_pdf_custom_text_areas'] = custom_text_areas
    st.session_state['central_pdf_num_text_areas'] = num_text_areas
    
    if custom_text_areas:
        st.success(f"✅ {len(custom_text_areas)} Textbereich(e) konfiguriert")

def _render_custom_images_section():
    """Rendert die zusätzliche Bilder/Fotos Sektion"""
    st.markdown("**Zusätzliche Bilder und Fotos für das PDF:**")
    
    # Anzahl der Bilder
    num_images = st.number_input(
        "Anzahl der zusätzlichen Bilder:",
        min_value=0,
        max_value=10,
        value=st.session_state.get('central_pdf_num_images', 0),
        key="enhanced_num_images"
    )
    
    custom_images = []
    
    for i in range(num_images):
        with st.expander(f"Bild {i+1}", expanded=i == 0):
            title = st.text_input(
                f"Titel für Bild {i+1}:",
                value=f"Zusätzliches Bild {i+1}",
                key=f"enhanced_image_title_{i}"
            )
            
            uploaded_file = st.file_uploader(
                f"Bild {i+1} hochladen:",
                type=['png', 'jpg', 'jpeg'],
                key=f"enhanced_image_upload_{i}"
            )
            
            description = st.text_area(
                f"Beschreibung für Bild {i+1}:",
                value="",
                height=100,
                key=f"enhanced_image_description_{i}"
            )
            
            position = st.selectbox(
                f"Position im PDF:",
                ["Nach Projektübersicht", "Nach technischen Details", "Bei Visualisierungen", "Am Ende"],
                key=f"enhanced_image_position_{i}"
            )
            
            if uploaded_file and title:
                try:
                    image_bytes = uploaded_file.read()
                    image_b64 = base64.b64encode(image_bytes).decode()
                    
                    custom_images.append({
                        'title': title,
                        'image_bytes': image_bytes,
                        'image_b64': image_b64,
                        'description': description,
                        'position': position,
                        'filename': uploaded_file.name
                    })
                    
                    # Vorschau anzeigen
                    st.image(image_bytes, caption=f"Vorschau: {title}", width=200)
                    
                except Exception as e:
                    st.error(f"Fehler beim Verarbeiten von Bild {i+1}: {e}")
    
    st.session_state['central_pdf_custom_images'] = custom_images
    st.session_state['central_pdf_num_images'] = num_images
    
    if custom_images:
        st.success(f"✅ {len(custom_images)} Bild(er) hochgeladen")

def _render_features_highlights_selection():
    """Rendert die Features/Highlights Auswahl"""
    st.markdown("**Wählen Sie die Features und Highlights, die hervorgehoben werden sollen:**")
    
    features = {
        "high_efficiency": "🔋 Hocheffiziente Module",
        "smart_monitoring": "📱 Intelligentes Monitoring",
        "weather_resistant": "🌧️ Wetterfest & langlebig",
        "easy_maintenance": "🔧 Wartungsarm",
        "grid_integration": "🔌 Optimale Netzintegration",
        "energy_storage": "⚡ Intelligente Energiespeicherung",
        "co2_neutral": "🌱 CO₂-neutral",
        "roi_optimized": "💰 ROI-optimiert",
        "future_ready": "🚀 Zukunftssicher",
        "german_quality": "🇩🇪 Deutsche Qualität",
        "warranty_25": "🛡️ 25 Jahre Garantie",
        "app_control": "📲 App-Steuerung"
    }
    
    selected_features = []
    
    cols = st.columns(3)
    for i, (feature_key, feature_name) in enumerate(features.items()):
        with cols[i % 3]:
            if st.checkbox(feature_name, key=f"enhanced_feature_{feature_key}"):
                selected_features.append(feature_key)
    
    # Zusätzliche benutzerdefinierte Features
    st.markdown("**Benutzerdefinierte Features:**")
    custom_feature = st.text_input(
        "Weiteres Feature hinzufügen:",
        key="enhanced_custom_feature_input"
    )
    
    if custom_feature and st.button("Feature hinzufügen", key="add_custom_feature"):
        custom_features = st.session_state.get('central_pdf_custom_features', [])
        custom_features.append(custom_feature)
        st.session_state['central_pdf_custom_features'] = custom_features
        st.success(f"✅ Feature '{custom_feature}' hinzugefügt")
    
    # Gespeicherte benutzerdefinierte Features anzeigen
    custom_features = st.session_state.get('central_pdf_custom_features', [])
    if custom_features:
        st.markdown("**Ihre benutzerdefinierten Features:**")
        for i, feature in enumerate(custom_features):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"• {feature}")
            with col2:
                if st.button("🗑️", key=f"delete_custom_feature_{i}"):
                    custom_features.pop(i)
                    st.session_state['central_pdf_custom_features'] = custom_features
                    st.rerun()
    
    st.session_state['central_pdf_selected_features'] = selected_features
    
    if selected_features or custom_features:
        total_features = len(selected_features) + len(custom_features)
        st.success(f"✅ {total_features} Feature(s) ausgewählt")

def _render_section_order_content():
    """Rendert die Reihenfolge & Inhalte der Sektionen"""
    st.markdown("**Bestimmen Sie die Reihenfolge und den Inhalt der PDF-Sektionen:**")
    
    # Verfügbare Sektionen
    available_sections = {
        "cover_page": "📄 Deckblatt",
        "executive_summary": "📝 Zusammenfassung",
        "project_overview": "📋 Projektübersicht", 
        "technical_details": "🔧 Technische Details",
        "financial_analysis": "💰 Finanzanalyse",
        "visualizations": "📊 Diagramme",
        "environmental_impact": "🌱 Umweltauswirkungen",
        "features_benefits": "⭐ Features & Vorteile",
        "installation_process": "🏗️ Installationsprozess",
        "maintenance_support": "🛠️ Wartung & Support",
        "warranty_conditions": "🛡️ Garantiebedingungen",
        "company_information": "🏢 Firmeninformationen",
        "custom_text_areas": "✍️ Benutzerdefinierte Texte",
        "custom_images": "🖼️ Zusätzliche Bilder",
        "appendices": "📑 Anhänge"
    }
    
    # Session State für Sektionsreihenfolge initialisieren
    if 'central_pdf_section_order' not in st.session_state:
        st.session_state['central_pdf_section_order'] = list(available_sections.keys())
    
    # Drag & Drop Simulation mit Buttons
    st.markdown("**Aktuelle Reihenfolge:**")
    
    section_order = st.session_state['central_pdf_section_order'].copy()
    
    for i, section_key in enumerate(section_order):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            section_name = available_sections.get(section_key, section_key)
            enabled = st.checkbox(
                section_name,
                value=True,
                key=f"enhanced_section_order_{section_key}"
            )
        
        with col2:
            if i > 0 and st.button("⬆️", key=f"move_up_{section_key}"):
                section_order[i], section_order[i-1] = section_order[i-1], section_order[i]
                st.session_state['central_pdf_section_order'] = section_order
                st.rerun()
        
        with col3:
            if i < len(section_order) - 1 and st.button("⬇️", key=f"move_down_{section_key}"):
                section_order[i], section_order[i+1] = section_order[i+1], section_order[i]
                st.session_state['central_pdf_section_order'] = section_order
                st.rerun()
        
        with col4:
            if st.button("🗑️", key=f"remove_{section_key}"):
                section_order.remove(section_key)
                st.session_state['central_pdf_section_order'] = section_order
                st.rerun()
    
    # Reset-Button
    if st.button("🔄 Standardreihenfolge wiederherstellen", key="reset_section_order"):
        st.session_state['central_pdf_section_order'] = list(available_sections.keys())
        st.rerun()

def _render_professional_features():
    """Rendert die Professional PDF-Features"""
    st.markdown("**Erweiterte Professional Features für das PDF:**")
    
    features = {
        "advanced_charts": "📊 Erweiterte Diagramme",
        "detailed_calculations": "🧮 Detaillierte Berechnungen", 
        "financing_calculations": "💰 Finanzierungsberechnungen",
        "component_datasheets": "📋 Komponenten-Datenblätter",
        "installation_timeline": "📅 Installations-Zeitplan",
        "warranty_details": "🛡️ Detaillierte Garantieinformationen",
        "maintenance_schedule": "🔧 Wartungsplan",
        "performance_predictions": "📈 Performance-Prognosen",
        "financing_options": "💳 Finanzierungsoptionen"
    }
    
    selected_professional_features = {}
    
    # Session State eindeutig initialisieren
    timestamp = datetime.now().strftime("%H%M%S")
    
    cols = st.columns(2)
    for i, (feature_key, feature_name) in enumerate(features.items()):
        with cols[i % 2]:
            # Eindeutige Keys mit Timestamp
            session_key = f"enh_pro_{feature_key}_{timestamp}"
            selected_professional_features[feature_key] = st.checkbox(
                feature_name,
                value=True if feature_key == "financing_calculations" else False,
                key=session_key
            )
    
    st.session_state['central_pdf_professional_features'] = selected_professional_features
    return selected_professional_features

def _render_wow_features():
    """Rendert die WOW Features (Experimental)"""
    st.markdown("**Experimentelle WOW Features (Beta):**")
    
    features = {
        "3d_visualization": "🎯 3D-Visualisierung der Anlage",
        "interactive_roi": "💎 Interaktive ROI-Simulation",
        "ar_preview": "🥽 AR-Vorschau (Beta)",
        "ai_optimization": "🤖 KI-Optimierungsvorschläge",
        "smart_monitoring_demo": "📱 Smart Monitoring Demo",
        "future_expansion": "🚀 Zukunfts-Erweiterungsoptionen"
    }
    
    selected_wow_features = {}
    
    cols = st.columns(2)
    for i, (feature_key, feature_name) in enumerate(features.items()):
        with cols[i % 2]:
            selected_wow_features[feature_key] = st.checkbox(
                feature_name,
                value=False,
                key=generate_unique_key(f"enhanced_wow_{feature_key}")
            )
    
    st.session_state['central_pdf_wow_features'] = selected_wow_features
    return selected_wow_features

def _activate_all_pdf_sections():
    """Aktiviert alle PDF-Sektionen"""
    sections = [
        "ProjectOverview", "TechnicalComponents", "CostDetails", 
        "Economics", "SimulationDetails", "CO2Savings", 
        "Visualizations", "FutureAspects"
    ]
    
    for section in sections:
        st.session_state[f"enhanced_section_{section}"] = True
    
    st.success("✅ Alle Sektionen aktiviert!")

def _activate_essential_sections():
    """Aktiviert nur die wichtigsten Sektionen"""
    essential_sections = ["ProjectOverview", "CostDetails", "Economics"]
    all_sections = [
        "ProjectOverview", "TechnicalComponents", "CostDetails", 
        "Economics", "SimulationDetails", "CO2Savings", 
        "Visualizations", "FutureAspects"
    ]
    
    for section in all_sections:
        st.session_state[f"enhanced_section_{section}"] = section in essential_sections
    
    st.success("✅ Wichtigste Sektionen aktiviert!")

def _activate_advanced_features():
    """Aktiviert erweiterte Features"""
    professional_features = [
        "advanced_charts", "detailed_calculations", "component_datasheets",
        "installation_timeline", "warranty_details", "maintenance_schedule"
    ]
    
    for feature in professional_features:
        st.session_state[f"enhanced_professional_{feature}"] = True
    
    st.success("✅ Erweiterte Features aktiviert!")

def _deactivate_all_features():
    """Deaktiviert alle Features"""
    # Alle Sektionen deaktivieren
    sections = [
        "ProjectOverview", "TechnicalComponents", "CostDetails", 
        "Economics", "SimulationDetails", "CO2Savings", 
        "Visualizations", "FutureAspects"
    ]
    
    for section in sections:
        st.session_state[f"enhanced_section_{section}"] = False
    
    # Professional Features deaktivieren
    professional_features = [
        "advanced_charts", "detailed_calculations", "component_datasheets",
        "installation_timeline", "warranty_details", "maintenance_schedule",
        "performance_predictions", "financing_options"
    ]
    
    for feature in professional_features:
        st.session_state[f"enhanced_professional_{feature}"] = False
    
    st.warning("⚠️ Alle Features deaktiviert!")

def _activate_all_charts():
    """Aktiviert alle verfügbaren Diagramme"""
    charts = [
        'monthly_prod_cons_chart_bytes', 'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes', 'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes', 'annual_savings_chart_bytes',
        'roi_development_chart_bytes', 'co2_savings_chart_bytes'
    ]
    
    for chart in charts:
        st.session_state[f"enhanced_chart_{chart}"] = True
    
    st.success("✅ Alle Diagramme aktiviert!")

def _activate_essential_charts():
    """Aktiviert nur die wichtigsten Diagramme"""
    essential_charts = [
        'monthly_prod_cons_chart_bytes',
        'cost_projection_chart_bytes', 
        'cumulative_cashflow_chart_bytes'
    ]
    
    all_charts = [
        'monthly_prod_cons_chart_bytes', 'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes', 'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes', 'annual_savings_chart_bytes',
        'roi_development_chart_bytes', 'co2_savings_chart_bytes'
    ]
    
    for chart in all_charts:
        st.session_state[f"enhanced_chart_{chart}"] = chart in essential_charts
    
    st.success("✅ Wichtigste Diagramme aktiviert!")

def _deactivate_all_charts():
    """Deaktiviert alle Diagramme"""
    charts = [
        'monthly_prod_cons_chart_bytes', 'cost_projection_chart_bytes',
        'cumulative_cashflow_chart_bytes', 'consumption_coverage_pie_chart_bytes',
        'pv_usage_pie_chart_bytes', 'annual_savings_chart_bytes',
        'roi_development_chart_bytes', 'co2_savings_chart_bytes'
    ]
    
    for chart in charts:
        st.session_state[f"enhanced_chart_{chart}"] = False
    
    st.warning("⚠️ Alle Diagramme deaktiviert!")

def _show_enhanced_system_status_detailed():
    """Zeigt detaillierten System-Status"""
    
    # System-Status aus dem ursprünglichen System
    status = PDF_MANAGER.get_system_status()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**PDF-Systeme:**")
        systems = [
            ("Standard", status.get('standard', False)),
            ("TOM-90", status.get('tom90', False)),
            ("Mega Hybrid", status.get('mega_hybrid', False)),
            ("Preview", status.get('preview', False))
        ]
        
        for system_name, available in systems:
            icon = "✅" if available else "❌"
            st.write(f"{icon} {system_name}")
    
    with col2:
        st.markdown("**Feature-Status:**")
        
        # Zähle aktivierte Features
        professional_count = len([k for k in st.session_state.keys() if k.startswith('enhanced_professional_') and st.session_state[k]])
        wow_count = len([k for k in st.session_state.keys() if k.startswith('enhanced_wow_') and st.session_state[k]])
        section_count = len([k for k in st.session_state.keys() if k.startswith('enhanced_section_') and st.session_state[k]])
        chart_count = len([k for k in st.session_state.keys() if k.startswith('enhanced_chart_') and st.session_state[k]])
        
        st.write(f"📋 {professional_count} Professional Features")
        st.write(f"🚀 {wow_count} WOW Features")
        st.write(f"📄 {section_count} Sektionen")
        st.write(f"📊 {chart_count} Diagramme")

def _generate_enhanced_pdf_with_all_features(
    selected_layout: str,
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any], 
    company_info: Dict[str, Any],
    texts: Dict[str, str],
    load_admin_setting_func: Callable,
    save_admin_setting_func: Callable,
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int]
):
    """Generiert PDF mit allen erweiterten Features"""
    
    try:
        with st.spinner(f"Erstelle {selected_layout} PDF mit allen Features..."):
            
            # Sammle alle konfigurierten Optionen
            inclusion_options = {
                # Basis-Optionen
                "include_company_logo": st.session_state.get('enhanced_include_logo', True),
                "include_product_images": True,
                "include_all_documents": True,
                
                # Sektionen
                "selected_sections": st.session_state.get('central_pdf_selected_sections', []),
                
                # Charts
                "selected_charts_for_pdf": st.session_state.get('central_pdf_selected_charts', []),
                
                # Benutzerdefinierte Inhalte
                "custom_text_areas": st.session_state.get('central_pdf_custom_text_areas', []),
                "custom_images": st.session_state.get('central_pdf_custom_images', []),
                
                # Features
                "selected_features": st.session_state.get('central_pdf_selected_features', []),
                "custom_features": st.session_state.get('central_pdf_custom_features', []),
                "professional_features": st.session_state.get('central_pdf_professional_features', {}),
                "wow_features": st.session_state.get('central_pdf_wow_features', {}),
                
                # Template-Daten
                "selected_title_image_b64": st.session_state.get('central_pdf_selected_title_image_b64'),
                "selected_offer_title_text": st.session_state.get('central_pdf_selected_offer_title_text'),
                "selected_cover_letter_text": st.session_state.get('central_pdf_selected_cover_letter_text'),
                
                # Firmendokumente
                "company_document_ids_to_include": st.session_state.get('central_pdf_branding', {}).get('selected_doc_ids', [])
            }
            
            # PDF mit dem zentralen System generieren
            pdf_bytes = CENTRAL_PDF_UI.generate_pdf_central(
                layout_choice=selected_layout,
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                inclusion_options=inclusion_options,
                template_data={
                    "title_image_b64": inclusion_options["selected_title_image_b64"],
                    "offer_title_text": inclusion_options["selected_offer_title_text"],
                    "cover_letter_text": inclusion_options["selected_cover_letter_text"]
                },
                texts=texts,
                load_admin_setting_func=load_admin_setting_func,
                save_admin_setting_func=save_admin_setting_func,
                list_products_func=list_products_func,
                get_product_by_id_func=get_product_by_id_func,
                db_list_company_documents_func=db_list_company_documents_func,
                active_company_id=active_company_id
            )
            
            if pdf_bytes:
                st.success("🎉 PDF mit allen Features erfolgreich erstellt!")
                
                # Dateiname mit Timestamp
                customer_name = project_data.get('customer_data', {}).get('last_name', 'Kunde')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Angebot_Enhanced_{customer_name}_{selected_layout}_{timestamp}.pdf"
                
                # Download-Button
                st.download_button(
                    label="📥 Enhanced PDF herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"enhanced_pdf_download_{timestamp}"
                )
                
                # Feature-Zusammenfassung
                st.info(f"""
                **PDF-Features verwendet:**
                - Layout: {selected_layout.upper()}
                - Sektionen: {len(inclusion_options['selected_sections'])}
                - Diagramme: {len(inclusion_options['selected_charts_for_pdf'])}
                - Textbereiche: {len(inclusion_options['custom_text_areas'])}
                - Zusätzliche Bilder: {len(inclusion_options['custom_images'])}
                - Features: {len(inclusion_options['selected_features']) + len(inclusion_options['custom_features'])}
                """)
                
            else:
                st.error("❌ PDF-Erstellung fehlgeschlagen!")
                
    except Exception as e:
        st.error(f"❌ Fehler bei der erweiterten PDF-Erstellung: {e}")
        if st.checkbox("Fehlerdetails anzeigen", key="enhanced_pdf_error_details"):
            st.code(traceback.format_exc())

# =============================================================================
# HAUPT-RENDER-FUNKTION MIT ALLEN FEATURES
# =============================================================================

def render_enhanced_central_pdf_ui(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any], 
    company_info: Dict[str, Any],
    texts: Dict[str, str],
    load_admin_setting_func: Callable = None,
    save_admin_setting_func: Callable = None,
    list_products_func: Callable = None,
    get_product_by_id_func: Callable = None,
    db_list_company_documents_func: Callable = None,
    active_company_id: Optional[int] = None
) -> None:
    """
    ENHANCED ZENTRALE PDF UI - ALLE FEATURES ERHALTEN!
    ==================================================
    Kombiniert ALLE ursprünglichen Features mit dem zentralen System.
    NICHTS wird gelöscht - alles wird zentral verfügbar gemacht!
    """
    
    st.header("🎯 Enhanced Zentrale PDF-Ausgabe")
    st.success("🚀 ALLE ursprünglichen Features bleiben erhalten und werden zentral verfügbar gemacht!")
    
    # System Status mit allen verfügbaren Features
    _show_enhanced_system_status()
    
    # Layout-Auswahl mit MEGA Features
    st.subheader("🚀 PDF-Layout auswählen - MEGA HYBRID VERFÜGBAR!")
    st.write("Wählen Sie das gewünschte PDF-Layout:")
    
    layout_options = {
        "STANDARD": "📄 Standard PDF (Bewährtes klassisches Layout)",
        "TOM90": "⭐ TOM-90 Nur (Moderne 5-Seiten-Version)", 
        "MEGA_HYBRID": "🚀 MEGA HYBRID (TOM-90 + Standard kombiniert)",
        "PREVIEW": "📋 Kompakt (Reduzierte Version)"
    }
    
    selected_layout = st.radio(
        "Layout:",
        options=list(layout_options.keys()),
        format_func=lambda x: layout_options[x],
        key="enhanced_central_pdf_layout_selection"
    )
    
    if selected_layout == "MEGA_HYBRID":
        st.info("🚀 MEGA HYBRID GEWÄHLT! Kombiniert die modernen TOM-90 ersten 5 Seiten mit der vollständigen Standard-PDF-Ausgabe. Sie erhalten das Beste aus beiden Welten!")
        st.success("📋 Was Sie erhalten: TOM-90 Seiten 1-5 (exakt wie gewünscht) + alle Standard-PDF-Funktionen als zusätzliche Seiten")
    
    st.write(f"🎯 Aktives Layout: {layout_options[selected_layout]}")
    
    # 🚀 Schnellauswahl für PDF-Sektionen
    st.subheader("🚀 Schnellauswahl für PDF-Sektionen")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Alle Sektionen aktivieren", key="activate_all_sections"):
            _activate_all_pdf_sections()
        if st.button("Nur wichtigste Sektionen", key="essential_sections"):
            _activate_essential_sections()
    
    with col2:
        if st.button("Erweiterte Features aktivieren", key="advanced_features"):
            _activate_advanced_features()
        if st.button("Alles deaktivieren", key="deactivate_all"):
            _deactivate_all_features()
    
    # 🚀 Diagramm-Schnellauswahl
    st.subheader("🚀 Diagramm-Schnellauswahl")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Alle Diagramme", key="all_charts"):
            _activate_all_charts()
    with col2:
        if st.button("Wichtigste Diagramme", key="essential_charts"):
            _activate_essential_charts()
    with col3:
        if st.button("Keine Diagramme", key="no_charts"):
            _deactivate_all_charts()
    
    # Vorlagen für das Angebot auswählen
    st.subheader("Vorlagen für das Angebot auswählen")
    
    # Titelbild auswählen
    with st.expander("**Titelbild auswählen**", expanded=True):
        _render_title_image_selection(load_admin_setting_func, save_admin_setting_func)
    
    # Überschrift/Titel auswählen  
    with st.expander("**Überschrift/Titel auswählen**", expanded=True):
        _render_offer_title_selection(load_admin_setting_func, save_admin_setting_func)
    
    # Anschreiben auswählen
    with st.expander("**Anschreiben auswählen**", expanded=True):
        _render_cover_letter_selection(load_admin_setting_func, save_admin_setting_func)
    
    # 👁️ Template-Vorschau 
    with st.expander("👁️ Template-Vorschau", expanded=False):
        _render_template_preview()
    
    # 🎨 Moderne Design-Erweiterung (Optional)
    st.subheader("🎨 Moderne Design-Erweiterung (Optional)")
    design_mode = st.radio(
        "Design-Modus:",
        ["🔧 Standard Design aktiv", "🎨 Modernes Design", "⭐ Premium Design"],
        key="enhanced_design_mode_selection"
    )
    
    # Inhalte für das PDF auswählen
    st.subheader("Inhalte für das PDF auswählen")
    
    # Branding & Dokumente
    with st.expander("**Branding & Dokumente**", expanded=True):
        _render_branding_documents_section(
            company_info, active_company_id, db_list_company_documents_func
        )
    
    # Zusätzliche Firmendokumente (wiederholt für Benutzerfreundlichkeit)
    st.write("**Zusätzliche Firmendokumente**")
    
    # Hauptsektionen
    with st.expander("**Hauptsektionen**", expanded=True):
        selected_sections = _render_main_sections_selection()
        st.success(f"✅ {len(selected_sections)} Sektionen ausgewählt")
    
    # Diagramme & Visualisierungen
    with st.expander("**Diagramme & Visualisierungen**", expanded=True):
        selected_charts = _render_charts_visualization_selection(analysis_results)
        st.success(f"✅ {len(selected_charts)} Diagramme ausgewählt")
    
    # 🎨 Zusätzliche Inhalte für erweiterte PDF-Layouts
    st.subheader("🎨 Zusätzliche Inhalte für erweiterte PDF-Layouts")
    
    # 💰 Finanzierungsberechnungen & Vergleich (NEU!)
    _render_financing_ui_integration()
    
    # 🚀 Erweiterte Features (Experimental)
    with st.expander("🚀 Erweiterte Features (Experimental)", expanded=False):
        wow_features = _render_wow_features()
        st.success(f"🚀 {len([f for f in wow_features if wow_features[f]])} WOW Features aktiv")
    
    # 📊 Datenstatus für PDF-Erstellung (Original beibehalten)
    st.subheader("📊 Datenstatus für PDF-Erstellung")
    _show_original_data_status(project_data, analysis_results, texts)
    
    # 🔧 System-Status & verfügbare Features
    st.subheader("🔧 System-Status & verfügbare Features") 
    _show_enhanced_system_status_detailed()
    
    # PDF Generierung mit allen Features
    if st.button("🎯 PDF mit allen Features generieren", type="primary", key=generate_unique_key("enhanced_central_pdf_generate_1")):
        _generate_enhanced_pdf_with_all_features(
            selected_layout, project_data, analysis_results, 
            company_info, texts, load_admin_setting_func,
            save_admin_setting_func, list_products_func,
            get_product_by_id_func, db_list_company_documents_func, active_company_id
        )
    
    # 🖼️ Zusätzliche Bilder / Fotos hinzufügen
    with st.expander("🖼️ Zusätzliche Bilder / Fotos hinzufügen", expanded=False):
        _render_custom_images_section()
    
    # ⭐ Features / Highlights auswählen
    with st.expander("⭐ Features / Highlights auswählen", expanded=False):
        _render_features_highlights_selection()
    
    # 📑 Reihenfolge & Inhalte der Sektionen
    with st.expander("📑 Reihenfolge & Inhalte der Sektionen", expanded=False):
        _render_section_order_content()
    
    # 📋 Erweiterte PDF-Abschnitte
    with st.expander("📋 Erweiterte PDF-Abschnitte", expanded=False):
        professional_features = _render_professional_features()
        st.success(f"📋 {len([f for f in professional_features if professional_features[f]])} Professional Features aktiv")
    
    # 🚀 Erweiterte Features (Experimental)
    with st.expander("🚀 Erweiterte Features (Experimental)", expanded=False):
        wow_features = _render_wow_features()
        st.success(f"🚀 {len([f for f in wow_features if wow_features[f]])} WOW Features aktiv")

def _render_custom_text_areas_inline():
    """Rendert die gestaltbaren Textbereiche inline"""
    st.markdown("**Benutzerdefinierte Textbereiche für das PDF:**")
    
    # Anzahl der Textbereiche
    num_text_areas = st.number_input(
        "Anzahl der Textbereiche:",
        min_value=0,
        max_value=10,
        value=st.session_state.get('central_pdf_num_text_areas', 0),
        key=f"enhanced_num_text_areas_inline_{int(time.time() * 1000000) % 1000000}"
    )
    
    custom_text_areas = []
    
    for i in range(num_text_areas):
        with st.expander(f"Textbereich {i+1}", expanded=i == 0):
            title = st.text_input(
                f"Titel für Textbereich {i+1}:",
                value=f"Zusätzliche Informationen {i+1}",
                key=f"enhanced_text_area_title_inline_{i}_{int(time.time() * 1000000) % 1000000}"
            )
            
            content = st.text_area(
                f"Inhalt für Textbereich {i+1}:",
                value="",
                height=150,
                key=f"enhanced_text_area_content_inline_{i}_{int(time.time() * 1000000) % 1000000}",
                help="Hier können Sie zusätzliche Informationen eingeben, die im PDF erscheinen sollen."
            )
            
            position = st.selectbox(
                f"Position im PDF:",
                ["Nach Projektübersicht", "Nach technischen Details", "Nach Wirtschaftlichkeit", "Am Ende"],
                key=f"enhanced_text_area_position_inline_{i}_{int(time.time() * 1000000) % 1000000}"
            )
            
            if title and content:
                custom_text_areas.append({
                    'title': title,
                    'content': content,
                    'position': position
                })
    
    st.session_state['central_pdf_custom_text_areas'] = custom_text_areas
    st.session_state['central_pdf_num_text_areas'] = num_text_areas
    
    if custom_text_areas:
        st.success(f"✅ {len(custom_text_areas)} Textbereich(e) konfiguriert")
    
    # 📊 Datenstatus für PDF-Erstellung (Original beibehalten)
    st.subheader("📊 Datenstatus für PDF-Erstellung")
    _show_original_data_status(project_data, analysis_results, texts)
    
    # 🔧 System-Status & verfügbare Features
    st.subheader("🔧 System-Status & verfügbare Features") 
    _show_enhanced_system_status_detailed()
    
    # PDF Generierung mit allen Features
    if st.button("🎯 PDF mit allen Features generieren", type="primary", key=generate_unique_key("enhanced_central_pdf_generate_2")):
        _generate_enhanced_pdf_with_all_features(
            selected_layout, project_data, analysis_results, 
            company_info, texts, load_admin_setting_func,
            save_admin_setting_func, list_products_func,
            get_product_by_id_func, db_list_company_documents_func, active_company_id
        )
