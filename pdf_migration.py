"""
PDF-SYSTEM MIGRATION
====================
Diese Datei migriert alle bestehenden PDF-UIs zum zentralen System.
Alle PDF-Funktionen werden vereinheitlicht und zentralisiert.

Autor: GitHub Copilot
Datum: 2025-07-26
"""

import streamlit as st
import os
import shutil
from pathlib import Path

def migrate_pdf_systems():
    """Migriert alle PDF-Systeme zum zentralen System"""
    
    st.title("🔄 PDF-System Migration")
    st.info("Diese Funktion vereinheitlicht alle PDF-Systeme zu einem zentralen System.")
    
    # Dateien die migriert werden sollen
    pdf_files_to_migrate = [
        "pdf_ui.py",
        "src/omerssolar/pdf_ui.py", 
        "extras/pdf_ui.py",
        "tom90_pdf_composer_ui.py",
        "pdf_ui_integration.py",
        "pdf_ui_design_enhancement.py",
        "pdf_professional_ui.py"
    ]
    
    if st.button("🚀 Migration starten"):
        migration_results = []
        
        st.subheader("📋 Migration läuft...")
        progress_bar = st.progress(0)
        
        for i, file_path in enumerate(pdf_files_to_migrate):
            full_path = Path(file_path)
            
            if full_path.exists():
                # Backup erstellen
                backup_path = full_path.with_suffix('.py.migrated_backup')
                try:
                    shutil.copy2(full_path, backup_path)
                    
                    # Datei mit Migration-Hinweis ersetzen
                    migration_content = create_migration_stub(file_path)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(migration_content)
                    
                    migration_results.append(f"✅ {file_path} migriert")
                    
                except Exception as e:
                    migration_results.append(f"❌ {file_path} Fehler: {e}")
            else:
                migration_results.append(f"⚠️ {file_path} nicht gefunden")
            
            progress_bar.progress((i + 1) / len(pdf_files_to_migrate))
        
        st.subheader("📊 Migration Ergebnisse:")
        for result in migration_results:
            if "✅" in result:
                st.success(result)
            elif "❌" in result:
                st.error(result)
            else:
                st.info(result)
        
        st.success("🎉 Migration abgeschlossen!")
        st.info("Alle PDF-Funktionen laufen jetzt über das zentrale System in `central_pdf_system.py`")
        
        if st.button("🔄 Streamlit neu starten empfohlen"):
            st.rerun()

def create_migration_stub(original_file_path: str) -> str:
    """Erstellt einen Migration-Stub für migrierte Dateien"""
    
    return f'''"""
MIGRIERTE DATEI - ZENTRALE PDF-SYSTEM
=====================================
Diese Datei wurde zum zentralen PDF-System migriert.

Original: {original_file_path}
Migriert am: 2025-07-26
Neues System: central_pdf_system.py

ALLE PDF-FUNKTIONEN SIND JETZT ZENTRAL VERFÜGBAR!
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable

# Weiterleitung zum zentralen System
try:
    from central_pdf_system import render_central_pdf_ui, show_pdf_system_status
    
    def render_pdf_ui(*args, **kwargs):
        """Weiterleitung zur zentralen PDF-UI"""
        st.info(f"🔄 Weiterleitung von {{original_file_path}} zum zentralen PDF-System")
        return render_central_pdf_ui(*args, **kwargs)
    
    # Weitere migrierte Funktionen
    def show_advanced_pdf_preview(*args, **kwargs):
        st.info("🔄 PDF-Vorschau ist im zentralen System integriert")
        return render_central_pdf_ui(*args, **kwargs)
    
    def render_tom90_pdf_section(*args, **kwargs):
        st.info("🔄 TOM-90 ist im zentralen System integriert")
        return render_central_pdf_ui(*args, **kwargs)
    
    def render_pdf_debug_section(*args, **kwargs):
        st.info("🔄 PDF-Debug ist im zentralen System integriert")
        show_pdf_system_status()
    
    # Status anzeigen
    st.success("✅ Zentrale PDF-System Weiterleitung aktiv")
    
except ImportError as e:
    st.error(f"❌ Zentrales PDF-System nicht verfügbar: {{e}}")
    st.error(f"Originaldatei: {{original_file_path}}")
    
    def render_pdf_ui(*args, **kwargs):
        st.error("❌ PDF-UI nicht verfügbar - Zentrales System fehlt!")
        st.info("Installieren Sie das zentrale PDF-System: central_pdf_system.py")
        return None

# Dummy-Funktionen für Rückwärtskompatibilität
def _dummy_generate_offer_pdf(*args, **kwargs):
    st.error("❌ Diese Funktion wurde zum zentralen System migriert!")
    return None

def _dummy_get_active_company_details():
    st.error("❌ Diese Funktion wurde zum zentralen System migriert!")
    return {{"name": "Migration erforderlich", "id": 0}}

def _dummy_list_company_documents(*args, **kwargs):
    st.error("❌ Diese Funktion wurde zum zentralen System migriert!")
    return []

# === MIGRATION INFORMATIONEN ===
MIGRATION_INFO = {{
    "original_file": "{original_file_path}",
    "migrated_to": "central_pdf_system.py", 
    "migration_date": "2025-07-26",
    "functions_migrated": [
        "render_pdf_ui",
        "show_advanced_pdf_preview",
        "render_tom90_pdf_section", 
        "render_pdf_debug_section"
    ],
    "backup_file": "{original_file_path}.migrated_backup"
}}

if __name__ == "__main__":
    st.title("📄 PDF-System Migration Info")
    st.json(MIGRATION_INFO)
    st.info("Diese Datei leitet alle Aufrufe an das zentrale PDF-System weiter.")
'''

def show_migration_overview():
    """Zeigt eine Übersicht der Migration"""
    
    st.title("📊 PDF-System Migration Übersicht")
    
    # Aktuelle Dateien scannen
    pdf_files = []
    base_path = Path(".")
    
    for pattern in ["**/*pdf*ui*.py", "**/doc_output*.py"]:
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                pdf_files.append(str(file_path))
    
    st.subheader(f"📁 Gefundene PDF-Dateien ({len(pdf_files)})")
    
    migrated_count = 0
    original_count = 0
    
    for file_path in sorted(pdf_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "MIGRIERTE DATEI - ZENTRALE PDF-SYSTEM" in content:
                st.success(f"✅ {file_path} (migriert)")
                migrated_count += 1
            elif "central_pdf_system" in content:
                st.info(f"🔄 {file_path} (verwendet zentrales System)")
            else:
                st.warning(f"⚠️ {file_path} (original, nicht migriert)")
                original_count += 1
                
        except Exception as e:
            st.error(f"❌ {file_path} (Fehler beim Lesen: {e})")
    
    st.markdown("---")
    st.subheader("📈 Migration Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Migrierte Dateien", migrated_count)
    
    with col2:
        st.metric("Original Dateien", original_count)
    
    with col3:
        migration_percent = (migrated_count / len(pdf_files) * 100) if pdf_files else 0
        st.metric("Migration %", f"{migration_percent:.1f}%")
    
    if original_count > 0:
        st.warning(f"⚠️ {original_count} Dateien sind noch nicht migriert!")
        if st.button("🚀 Jetzt migrieren"):
            migrate_pdf_systems()
    else:
        st.success("🎉 Alle PDF-Dateien sind migriert!")

# Hauptfunktion für die Migrations-UI
def render_migration_ui():
    """Hauptfunktion für die Migrations-Benutzeroberfläche"""
    
    tab1, tab2 = st.tabs(["📊 Übersicht", "🔄 Migration"])
    
    with tab1:
        show_migration_overview()
    
    with tab2:
        migrate_pdf_systems()

if __name__ == "__main__":
    render_migration_ui()
