"""
Vereinfachtes Patch-Skript für die PDF-Generierung in der SolarDING App.
"""
import os
import traceback
from typing import Dict, Any, List, Optional

def print_separator(title: str):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def patch_pdf_generator():
    print_separator("PATCH: pdf_generator.py verbessern")
    
    filepath = "pdf_generator.py"
    if not os.path.exists(filepath):
        print(f"Datei {filepath} nicht gefunden.")
        return False
    
    try:
        # Sicherungskopie erstellen
        backup_path = f"{filepath}.bak"
        with open(filepath, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"Backup erstellt: {backup_path}")
        
        # Den problematischen Teil in der Validierungsfunktion identifizieren und ersetzen
        validation_func_start = content.find("def _validate_pdf_data_availability")
        if validation_func_start == -1:
            print("Validierungsfunktion nicht gefunden.")
            return False
        
        validation_func_end = content.find("def _create_no_data_fallback_pdf", validation_func_start)
        if validation_func_end == -1:
            print("Ende der Validierungsfunktion nicht gefunden.")
            return False
        
        # Die gesamte Validierungsfunktion extrahieren
        old_validation_func = content[validation_func_start:validation_func_end]
        
        # Verbesserte Validierungsfunktion
        improved_validation_func = '''def _validate_pdf_data_availability(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]) -> Dict[str, Any]:
    """
    Validiert die Verfügbarkeit von Daten für die PDF-Erstellung und gibt Warnmeldungen zurück.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
        texts: Text-Dictionary
        
    Returns:
        Dict mit Validierungsergebnissen und Warnmeldungen
    """
    validation_result = {
        'is_valid': True,
        'warnings': [],
        'critical_errors': [],
        'missing_data_summary': []
    }
    
    # Kundendaten prüfen (nicht kritisch)
    customer_data = project_data.get('customer_data', {})
    if not customer_data or not customer_data.get('last_name'):
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_customer_name', 'Kein Kundenname verfügbar - wird als "Kunde" angezeigt')
        )
        validation_result['missing_data_summary'].append('Kundenname')
    
    # PV-Details prüfen
    pv_details = project_data.get('pv_details', {})
    project_details = project_data.get('project_details', {})
    
    # Entweder module in pv_details ODER module_quantity in project_details ist ausreichend
    modules_present = False
    if pv_details and pv_details.get('selected_modules'):
        modules_present = True
    elif project_details and project_details.get('module_quantity', 0) > 0:
        modules_present = True
    
    if not modules_present:
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_modules', 'Keine PV-Module ausgewählt - Standardwerte werden verwendet')
        )
        validation_result['missing_data_summary'].append('PV-Module')
        # Nur als Warnung, nicht als kritischer Fehler
    
    # Analyseergebnisse prüfen - mit mehr Toleranz
    if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
        # Wirklich leere oder sehr minimale Analyse ist ein kritischer Fehler
        validation_result['critical_errors'].append(
            get_text(texts, 'pdf_error_no_analysis', 'Keine Analyseergebnisse verfügbar - PDF kann nicht erstellt werden')
        )
        validation_result['is_valid'] = False
        validation_result['missing_data_summary'].append('Analyseergebnisse')
    else:
        # Wenn die Analyse mindestens einige Werte enthält, betrachten wir es als gültig
        # und geben nur Warnungen aus, wenn wichtige KPIs fehlen
        important_kpis = ['anlage_kwp', 'annual_pv_production_kwh', 'total_investment_cost_netto']
        missing_kpis = []
        for kpi in important_kpis:
            if not analysis_results.get(kpi):
                missing_kpis.append(kpi)
                
        if missing_kpis:
            missing_kpi_names = ', '.join(missing_kpis)
            validation_result['warnings'].append(
                get_text(texts, 'pdf_warning_missing_kpis', f'Fehlende wichtige Kennzahlen: {missing_kpi_names}')
            )
            validation_result['missing_data_summary'].extend(missing_kpis)
            # Fehlende KPIs sind kein kritischer Fehler mehr
    
    # Firmendaten prüfen (nicht kritisch)
    if not project_data.get('company_information', {}).get('name'):
        validation_result['warnings'].append(
            get_text(texts, 'pdf_warning_no_company', 'Keine Firmendaten verfügbar - Fallback wird verwendet')
        )
        validation_result['missing_data_summary'].append('Firmendaten')
    
    # Debug-Ausgabe
    print(f"PDF Validierung: is_valid={validation_result['is_valid']}, "
          f"Warnungen={len(validation_result['warnings'])}, "
          f"Kritische Fehler={len(validation_result['critical_errors'])}")
    
    return validation_result
'''
        
        # Ersetze die alte Funktion durch die neue
        new_content = content.replace(old_validation_func, improved_validation_func)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Validierungsfunktion erfolgreich verbessert.")
        return True
    except Exception as e:
        print(f"Fehler beim Patchen von pdf_generator.py:")
        traceback.print_exc()
        return False

def patch_doc_output():
    print_separator("PATCH: doc_output.py verbessern")
    
    filepath = "doc_output.py"
    if not os.path.exists(filepath):
        print(f"Datei {filepath} nicht gefunden.")
        return False
    
    try:
        # Sicherungskopie erstellen
        backup_path = f"{filepath}.bak"
        with open(filepath, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"Backup erstellt: {backup_path}")
        
        # Den problematischen Teil in der PDF-Statusanzeige identifizieren und ersetzen
        status_func_start = content.find("def _show_pdf_data_status")
        if status_func_start == -1:
            print("Statusanzeige-Funktion nicht gefunden.")
            return False
        
        # Suche nach dem Ende der Funktion (nächste Funktion oder Klassendeklaration)
        next_def = content.find("\ndef ", status_func_start + 10)
        next_class = content.find("\nclass ", status_func_start + 10)
        
        if next_def == -1 and next_class == -1:
            print("Ende der Statusanzeige-Funktion nicht gefunden.")
            return False
        
        status_func_end = min(pos for pos in [next_def, next_class] if pos != -1)
        
        # Die gesamte Statusanzeige-Funktion extrahieren
        old_status_func = content[status_func_start:status_func_end]
        
        # Verbesserte Statusanzeige-Funktion
        improved_status_func = '''def _show_pdf_data_status(project_data: Dict[str, Any], analysis_results: Dict[str, Any], texts: Dict[str, str]) -> bool:
    """
    Zeigt den Status der verfügbaren Daten für die PDF-Erstellung an und gibt zurück, ob die Daten ausreichen.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse  
        texts: Text-Dictionary
        
    Returns:
        bool: True wenn ausreichende Daten für PDF-Erstellung vorhanden sind
    """
    st.subheader(get_text_pdf_ui(texts, "pdf_data_status_header", "📊 Datenstatus für PDF-Erstellung"))
    
    # Datenvalidierung mit direktem Import der PDF-Generator-Validierung
    try:
        from pdf_generator import _validate_pdf_data_availability
        validation_result = _validate_pdf_data_availability(project_data or {}, analysis_results or {}, texts)
        data_sufficient = validation_result['is_valid']
    except ImportError:
        # Fallback zur lokalen Validierung, wenn Import fehlschlägt
        validation_result = {'is_valid': True, 'warnings': [], 'critical_errors': [], 'missing_data_summary': []}
        data_sufficient = True
        
        # Prüfe Analyseergebnisse als wichtigsten Faktor
        if not analysis_results or not isinstance(analysis_results, dict) or len(analysis_results) < 2:
            validation_result['critical_errors'].append("Keine Analyseergebnisse verfügbar")
            validation_result['missing_data_summary'].append("Analyseergebnisse")
            data_sufficient = False
    
    # Status-Indikatoren anzeigen
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Kundendaten
        customer_data = project_data.get('customer_data', {})
        if customer_data and customer_data.get('last_name'):
            st.success("✅ " + get_text_pdf_ui(texts, "customer_data_complete", "Kundendaten"))
        else:
            st.info("ℹ️ " + get_text_pdf_ui(texts, "customer_data_incomplete", "Kundendaten"))
            # Nur Infoanzeige, kein Blocker
    
    with col2:
        # PV-Konfiguration - flexible Bedingung
        pv_details = project_data.get('pv_details', {})
        project_details = project_data.get('project_details', {})
        
        modules_ok = (pv_details and pv_details.get('selected_modules')) or \
                    (project_details and project_details.get('module_quantity', 0) > 0)
                    
        if modules_ok:
            st.success("✅ " + get_text_pdf_ui(texts, "pv_config_complete", "PV-Module"))
        else:
            st.info("ℹ️ " + get_text_pdf_ui(texts, "pv_config_incomplete", "PV-Module"))
            # Nur Info, kein Blocker
    
    with col3:
        # Wechselrichter
        inverter_ok = project_details and (project_details.get('selected_inverter_id') or 
                                         project_details.get('selected_inverter_name'))
        if inverter_ok:
            st.success("✅ " + get_text_pdf_ui(texts, "inverter_config_complete", "Wechselrichter"))
        else:
            st.info("ℹ️ " + get_text_pdf_ui(texts, "inverter_config_incomplete", "Wechselrichter"))
            # Nur Info, kein Blocker
    
    with col4:
        # Analyseergebnisse sind der wichtigste Faktor
        if analysis_results and isinstance(analysis_results, dict) and len(analysis_results) > 1:
            if analysis_results.get('anlage_kwp'):
                st.success("✅ " + get_text_pdf_ui(texts, "analysis_complete", "Berechnung"))
            else:
                st.warning("⚠️ " + get_text_pdf_ui(texts, "analysis_minimal", "Einfache Berechnung"))
        else:
            st.error("❌ " + get_text_pdf_ui(texts, "analysis_missing", "Berechnung"))
            # Kritischer Fehler, blockiert PDF-Erstellung
    
    # Handlungsempfehlungen nur bei kritischen Fehlern
    if not data_sufficient:
        critical_messages = validation_result.get('critical_errors', [])
        critical_summary = ", ".join(critical_messages) if critical_messages else "Kritische Daten fehlen"
        st.error("🚫 " + get_text_pdf_ui(texts, "pdf_creation_blocked", 
            f"PDF-Erstellung nicht möglich. {critical_summary}"))
        st.info(get_text_pdf_ui(texts, "pdf_creation_instructions",  
            "Bitte führen Sie eine Wirtschaftlichkeitsberechnung durch, bevor Sie ein PDF erstellen."))
    elif validation_result.get('warnings'):
        st.warning("⚠️ " + get_text_pdf_ui(texts, "pdf_creation_warnings", 
            "PDF kann erstellt werden, enthält aber möglicherweise nicht alle gewünschten Informationen."))
        st.info(get_text_pdf_ui(texts, "pdf_creation_with_warnings", 
            "Bei unvollständigen Daten wird ein vereinfachtes PDF mit den verfügbaren Informationen erstellt."))
    else:
        st.success("🎉 " + get_text_pdf_ui(texts, "pdf_data_complete", 
            "Alle erforderlichen Daten verfügbar - vollständiges PDF kann erstellt werden!"))
    
    return data_sufficient
'''
        
        # Ersetze die alte Funktion durch die neue
        new_content = content.replace(old_status_func, improved_status_func)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Statusanzeige-Funktion erfolgreich verbessert.")
        return True
    except Exception as e:
        print(f"Fehler beim Patchen von doc_output.py:")
        traceback.print_exc()
        return False

def patch_pdf_ui():
    print_separator("PATCH: pdf_ui.py korrigieren")
    
    filepath = "pdf_ui.py"
    if not os.path.exists(filepath):
        print(f"Datei {filepath} nicht gefunden.")
        return False
    
    try:
        # Sicherungskopie erstellen
        backup_path = f"{filepath}.bak"
        with open(filepath, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"Backup erstellt: {backup_path}")
        
        # Problematische Zeile um Zeile 302 finden
        lines = content.split('\n')
        
        # Suche nach der problematischen Zeile
        found = False
        for i in range(max(0, 295), min(len(lines), 310)):
            if "else: st.caption" in lines[i] and "pdf_select_active_company_for_docs" in lines[i]:
                # Problematische Zeile gefunden
                lines[i] = '            else:'
                lines.insert(i+1, '                st.caption(get_text_pdf_ui(texts, "pdf_select_active_company_for_docs", "Aktive Firma nicht korrekt."))')
                found = True
                break
        
        if not found:
            print("Problematische Zeile nicht gefunden.")
            return False
        
        # Speichere die korrigierte Datei
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print("Syntaxfehler in pdf_ui.py erfolgreich korrigiert.")
        return True
    except Exception as e:
        print(f"Fehler beim Patchen von pdf_ui.py:")
        traceback.print_exc()
        return False

def main():
    print_separator("PDF GENERIERUNGS-BUGFIX")
    print("Dieses Skript behebt den Fehler, bei dem trotz vollständiger Daten")
    print("die 'No Data Info' Fallback-Meldung erscheint und keine PDF generiert wird.")
    
    success = True
    
    if not patch_pdf_generator():
        success = False
    
    if not patch_doc_output():
        success = False
    
    if not patch_pdf_ui():
        success = False
    
    if success:
        print_separator("PATCH ERFOLGREICH")
        print("Alle Probleme wurden erfolgreich behoben. Die PDF-Generierung sollte jetzt funktionieren.")
        print("Originaldateien wurden als .bak-Dateien gesichert.")
    else:
        print_separator("PATCH TEILWEISE FEHLGESCHLAGEN")
        print("Es sind Probleme aufgetreten. Bitte überprüfen Sie die Fehlermeldungen.")

if __name__ == "__main__":
    main()
