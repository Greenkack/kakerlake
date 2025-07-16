# ui/pdf_composer_ui.py
# -*- coding: utf-8 -*-
"""
PDF Composer - Interaktive UI zur Zusammenstellung von PDF-Dokumenten.
Ermöglicht das Anordnen von Modulen und das Hinzufügen von Inhalten.

Author: Suratina Sicmislar
Version: 1.0 (AI-Generated & Interactive)
"""

import streamlit as st
import os
import tempfile
import base64
from typing import Dict, Any
from pdf_generator import create_offer_pdf
from pdf_generator import PDFGenerator
# Definition der verfügbaren Module
AVAILABLE_MODULES = {
    "deckblatt": "Deckblatt",
    "anschreiben": "Anschreiben",
    "angebotstabelle": "Angebotstabelle",
    # ... weitere Module
}

def display_pdf_composer_ui(offer_data: dict):
    """Zeigt die vollständige UI zur PDF-Zusammenstellung an."""
    st.header("PDF-Zusammenstellung & Live-Vorschau")
    st.info("Ordnen Sie die PDF-Module an, fügen Sie eigene Inhalte hinzu und sehen Sie das Ergebnis sofort in der Vorschau.")

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.subheader("Struktur anpassen")
        
        if 'pdf_module_order' not in st.session_state:
            st.session_state.pdf_module_order = [
                {"id": "deckblatt", "label": "Deckblatt"},
                {"id": "anschreiben", "label": "Anschreiben"},
                {"id": "angebotstabelle", "label": "Angebotstabelle"},
            ]

        # Zeige die aktuelle Reihenfolge an und biete Steuerelemente
        for i, module in enumerate(st.session_state.pdf_module_order):
            cols = st.columns([0.8, 0.1, 0.1])
            with cols[0]:
                st.text(f"{i+1}. {module['label']}")
            with cols[1]:
                if i > 0 and st.button("⬆️", key=f"up_{i}"):
                    st.session_state.pdf_module_order.insert(i - 1, st.session_state.pdf_module_order.pop(i))
                    st.experimental_rerun()
            with cols[2]:
                if i < len(st.session_state.pdf_module_order) - 1 and st.button("⬇️", key=f"down_{i}"):
                    st.session_state.pdf_module_order.insert(i + 1, st.session_state.pdf_module_order.pop(i))
                    st.experimental_rerun()
            
            # Wenn es ein benutzerdefiniertes Modul ist, zeige die Upload-Felder
            if module["id"] == "benutzerdefiniert":
                module['content'] = module.get('content', {})
                uploaded_file = st.file_uploader("Bild hochladen", type=['png', 'jpg'], key=f"upload_{i}")
                if uploaded_file:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        module['content']['type'] = 'image'
                        module['content']['data'] = tmp.name
        
        st.markdown("---")
        st.write("**Module hinzufügen**")
        
        cols_add = st.columns(2)
        with cols_add[0]:
            if st.button("Benutzerdefinierte Seite"):
                new_module = {"id": "benutzerdefiniert", "label": f"Eigene Seite {len(st.session_state.pdf_module_order) + 1}"}
                st.session_state.pdf_module_order.append(new_module)
                st.experimental_rerun()
        with cols_add[1]:
            # Hier könnten weitere Standardmodule hinzugefügt werden
            pass
            
    with col2:
        st.subheader("Live-Vorschau")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                # Erstelle eine Instanz des Generators und rufe die Methode auf
                generator = PDFGenerator(
                    offer_data=offer_data,
                    module_order=st.session_state.pdf_module_order,
                    theme_name=st.session_state.get("pdf_theme_name", "Classic Light"),
                    filename=tmp.name
                )
                generator.create_pdf()
                
                # Lese die erstellte Datei und bette sie als Base64-String ein
                with open(tmp.name, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # Zeige das PDF direkt in der App an
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Fehler bei der PDF-Vorschau: {e}")