"""
PDF BUTTON FIX - NOTFALL REPARATUR
==================================
Behebt blockierte PDF-Buttons durch Lock-Reset
"""

import streamlit as st

def fix_pdf_button_lock():
    """Repariert blockierte PDF-Buttons"""
    
    st.title("🔧 PDF-Button Notfall-Reparatur")
    
    # Aktuelle Lock-Status prüfen
    lock_status = st.session_state.get('pdf_generating_lock_v1', 'nicht gesetzt')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Status-Diagnose")
        st.write(f"**PDF Lock Status:** {lock_status}")
        
        # Alle PDF-bezogenen Session State Keys anzeigen
        pdf_keys = [k for k in st.session_state.keys() if 'pdf_' in k.lower()]
        st.write(f"**PDF Session Keys:** {len(pdf_keys)}")
        
        for key in pdf_keys[:10]:  # Nur erste 10 anzeigen
            value = st.session_state.get(key)
            st.write(f"- `{key}`: {value}")
    
    with col2:
        st.subheader("⚡ Schnell-Reparatur")
        
        if st.button("🔓 PDF-Lock zurücksetzen", type="primary"):
            # Reset alle PDF-bezogenen Locks
            st.session_state.pdf_generating_lock_v1 = False
            st.session_state.pdf_download_ready = False
            st.session_state.pdf_generation_successful = False
            
            if 'generated_pdf_bytes_for_download_v1' in st.session_state:
                del st.session_state['generated_pdf_bytes_for_download_v1']
            
            st.success("PDF-Lock zurückgesetzt!")
            st.rerun()
        
        if st.button("🧹 Alle PDF Session States löschen"):
            keys_to_remove = [k for k in st.session_state.keys() if 'pdf_' in k.lower()]
            for key in keys_to_remove:
                del st.session_state[key]
            st.success(f"{len(keys_to_remove)} PDF Session Keys gelöscht!")
            st.rerun()
        
        if st.button("🔄 Kompletter PDF-Reset"):
            # Vollständiger Reset
            keys_to_reset = [
                'pdf_generating_lock_v1',
                'pdf_download_ready', 
                'pdf_generation_successful',
                'generated_pdf_bytes_for_download_v1',
                'pdf_last_generation_timestamp',
                'pdf_selected_main_sections',
                'pdf_inclusion_options'
            ]
            
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Neu initialisieren
            st.session_state.pdf_generating_lock_v1 = False
            st.session_state.pdf_download_ready = False
            st.session_state.pdf_generation_successful = False
            
            st.success("Kompletter PDF-Reset durchgeführt!")
            st.rerun()
    
    st.markdown("---")
    
    # Test-Button für PDF-System
    if st.button("🧪 PDF-System testen"):
        try:
            from pdf_generator import generate_offer_pdf
            st.success("PDF-Generator verfügbar")
        except ImportError as e:
            st.error(f"PDF-Generator nicht verfügbar: {e}")
        
        try:
            from central_pdf_system import PDF_MANAGER
            status = PDF_MANAGER.get_system_status()
            st.json(status)
        except ImportError as e:
            st.error(f"Central PDF System nicht verfügbar: {e}")

if __name__ == "__main__":
    fix_pdf_button_lock()
