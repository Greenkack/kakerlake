# test_new_features.py - Test für AI-Begleiter und Multi-Angebote
"""
Testskript für die neuen Features:
1. AI-Begleiter (DeepSeek)
2. Multi-Firmen-Angebotsgenerator
"""

import streamlit as st

# Page Config MUSS als erstes stehen
st.set_page_config(
    page_title="🚀 Neue Features Test",
    page_icon="🚀",
    layout="wide"
)

import sys
import os

# Pfad zur App hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Module importieren
try:
    from ai_companion import render_ai_companion, get_ai_companion_status
    from multi_offer_generator import render_multi_offer_generator
    AI_COMPANION_AVAILABLE = True
    MULTI_OFFER_AVAILABLE = True
except ImportError as e:
    st.error(f"Import-Fehler: {e}")
    AI_COMPANION_AVAILABLE = False
    MULTI_OFFER_AVAILABLE = False

def main():
    """Hauptfunktion für den Test"""
    
    st.title("🚀 Solar-App - Neue Features")
    st.markdown("---")
    
    # Navigation
    tab1, tab2, tab3 = st.tabs([
        "🤖 AI-Begleiter", 
        "🏢 Multi-Angebote", 
        "📊 Status"
    ])
    
    # Tab 1: AI-Begleiter
    with tab1:
        if AI_COMPANION_AVAILABLE:
            st.header("🤖 AI-Begleiter (DeepSeek)")
            st.markdown("""
            **Features:**
            - DeepSeek API-Integration
            - Schwebender Chat-Assistent
            - Solar-spezifische Beratung
            - Chatverlauf mit Export
            """)
            
            render_ai_companion()
            
        else:
            st.error("❌ AI-Begleiter Modul nicht verfügbar")
    
    # Tab 2: Multi-Angebote
    with tab2:
        if MULTI_OFFER_AVAILABLE:
            st.header("🏢 Multi-Firmen-Angebotsgenerator")
            st.markdown("""
            **Features:**
            - Eine Kundeneingabe → Mehrere Angebote
            - Firmen-spezifische Produkte und Preise
            - Individuelle PDFs pro Firma
            - ZIP-Download aller Angebote
            """)
            
            render_multi_offer_generator()
            
        else:
            st.error("❌ Multi-Angebote Modul nicht verfügbar")
    
    # Tab 3: Status
    with tab3:
        st.header("📊 Feature-Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🤖 AI-Begleiter")
            if AI_COMPANION_AVAILABLE:
                st.success("✅ Modul verfügbar")
                try:
                    status = get_ai_companion_status()
                    st.json(status)
                except:
                    st.info("Status nicht abrufbar")
            else:
                st.error("❌ Modul nicht verfügbar")
        
        with col2:
            st.subheader("🏢 Multi-Angebote")
            if MULTI_OFFER_AVAILABLE:
                st.success("✅ Modul verfügbar")
                
                # Datenbankstatus prüfen
                try:
                    from database import get_db_connection, list_companies
                    conn = get_db_connection()
                    if conn:
                        companies = list_companies()
                        st.success(f"✅ {len(companies)} Firmen in DB")
                        conn.close()
                    else:
                        st.warning("⚠️ DB-Verbindung fehlgeschlagen")
                except Exception as e:
                    st.error(f"❌ DB-Fehler: {e}")
            else:
                st.error("❌ Modul nicht verfügbar")
        
        # System-Info
        st.markdown("---")
        st.subheader("🔧 System-Info")
        
        import platform
        st.write(f"**Python:** {platform.python_version()}")
        st.write(f"**Streamlit:** {st.__version__}")
        st.write(f"**OS:** {platform.system()} {platform.release()}")
        
        # Installierte Pakete prüfen
        required_packages = [
            'streamlit', 'requests', 'sqlite3', 'reportlab', 'pandas'
        ]
        
        for package in required_packages:
            try:
                if package == 'sqlite3':
                    import sqlite3
                    st.success(f"✅ {package}")
                else:
                    __import__(package)
                    st.success(f"✅ {package}")
            except ImportError:
                st.error(f"❌ {package} fehlt")


if __name__ == "__main__":
    main()
