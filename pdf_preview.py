#!/usr/bin/env python3
"""
Erweitertes PDF-Vorschau-Modul mit Live-Preview
Autor: Gemini Ultra
Datum: 2025-06-21
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Callable
import base64
import io
from datetime import datetime
import time


try:
    from pdf_generator import generate_offer_pdf
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False
    def generate_offer_pdf(*args, **kwargs): return None

try:
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    # Erstelle Dummy-Klassen, wenn ReportLab nicht installiert ist
    class Table: pass
    class TableStyle: pass
    class Paragraph: pass
    def getSampleStyleSheet(): return {}

PDF_PREVIEW_AVAILABLE = PDF_GENERATOR_AVAILABLE and REPORTLAB_AVAILABLE

try:
    from PIL import Image
    import fitz  # PyMuPDF
    _VISUAL_LIBS_AVAILABLE = True
except ImportError:
    _VISUAL_LIBS_AVAILABLE = False

class PDFPreviewEngine:
    """Engine für PDF-Vorschau mit Cache und Optimierungen"""
    
    def __init__(self):
        self.cache = {}
        self.max_cache_size = 10
        self.preview_dpi = 150  # DPI für Vorschau-Bilder
        
    def generate_preview_pdf(
        self,
        project_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        inclusion_options: Dict[str, Any],
        texts: Dict[str, str],
        **kwargs
    ) -> Optional[bytes]:
        """Generiert ein Vorschau-PDF"""
        try:
            from pdf_generator import generate_offer_pdf
            
            # Cache-Key erstellen (vereinfacht, kann erweitert werden)
            project_data = kwargs.get('project_data', {})
            inclusion_options = kwargs.get('inclusion_options', {})
            cache_key = self._create_cache_key(project_data, inclusion_options)
            
            # Aus Cache laden wenn vorhanden
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # PDF generieren
            pdf_bytes = generate_offer_pdf(
                project_data=project_data,
                analysis_results=analysis_results,
                company_info=company_info,
                inclusion_options=inclusion_options,
                texts=texts,
                **kwargs
            )
            
            # In Cache speichern
            if pdf_bytes and len(self.cache) < self.max_cache_size:
                self.cache[cache_key] = pdf_bytes
            
            return pdf_bytes
            
        except Exception as e:
            st.error(f"Fehler bei PDF-Generierung: {e}")
            return None
    
    def _create_cache_key(self, project_data: Dict, options: Dict) -> str:
        """Erstellt einen eindeutigen Cache-Key"""
        # Vereinfachter Key basierend auf wichtigen Parametern
        key_parts = [
            project_data.get('customer_data', {}).get('last_name', ''),
            str(project_data.get('project_details', {}).get('module_quantity', 0)),
            str(options.get('include_charts', True)),
            str(options.get('include_all_documents', True))
        ]
        return "_".join(key_parts)
    
    def pdf_to_images(self, pdf_bytes: bytes, max_pages: int = 5) -> List[Image.Image]:
        """Konvertiert PDF-Seiten zu Bildern für Vorschau"""
        if not PDF_PREVIEW_AVAILABLE or not pdf_bytes:
            return []
        
        try:
            images = []
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(min(len(pdf_document), max_pages)):
                page = pdf_document[page_num]
                pix = page.get_pixmap(dpi=self.preview_dpi)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            
            pdf_document.close()
            return images
            
        except Exception as e:
            st.error(f"Fehler bei PDF-zu-Bild-Konvertierung: {e}")
            return []

def render_pdf_preview_interface(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    texts: Dict[str, str],
    load_admin_setting_func: Callable,
    save_admin_setting_func: Callable,
    list_products_func: Callable,
    get_product_by_id_func: Callable,
    db_list_company_documents_func: Callable,
    active_company_id: Optional[int] = None
):
    """Rendert die erweiterte PDF-Vorschau-Oberfläche"""
    
    st.subheader("👁️ PDF-Vorschau & Bearbeitung")
    
    if not PDF_PREVIEW_AVAILABLE:
        st.error("PDF-Vorschau nicht verfügbar. Bitte installieren Sie PyMuPDF: `pip install pymupdf`")
        return None
    
    # Preview Engine initialisieren
    if 'pdf_preview_engine' not in st.session_state:
        st.session_state.pdf_preview_engine = PDFPreviewEngine()
    
    engine = st.session_state.pdf_preview_engine
    
    # Layout: Sidebar für Optionen, Hauptbereich für Vorschau
    col1, col2 = st.columns([1, 2])
    
    with st.expander("Vorschau-Einstellungen", expanded=False):
        preview_mode = st.radio("Vorschau-Modus", ["Schnell (erste 3 Seiten)", "Vollständig (eingebettet)"], horizontal=True)
        # Erste Instanz: Einfacher Button
        update_preview = st.button("🔄 Vorschau aktualisieren", use_container_width=True, key="preview_update_simple")
    if update_preview or 'preview_pdf_bytes' not in st.session_state:
        with st.spinner("Generiere Vorschau..."):
            # Holen der aktuellen UI-Einstellungen
            theme_name = st.session_state.get('pdf_theme_name', 'Blau Elegant')
            
            # Standard inclusion_options bereitstellen falls nicht verfügbar
            inclusion_options = st.session_state.get('pdf_inclusion_options', {
                "include_company_logo": True,
                "include_product_images": True,
                "include_all_documents": True,
                "company_document_ids_to_include": [],
                "selected_charts_for_pdf": [],
                "include_optional_component_details": True,
                "include_custom_footer": True,
                "include_header_logo": True
            })
            
            # Alle notwendigen Parameter für den finalen Generator zusammenstellen
            pdf_generation_params = {
                "project_data": project_data,
                "analysis_results": analysis_results,
                "company_info": company_info,
                "inclusion_options": inclusion_options,  # WICHTIG: Fehlender Parameter hinzugefügt
                "texts": texts,
                "theme_name": theme_name,
                # Weitere Parameter aus Session State
                "selected_title_image_b64": st.session_state.get('selected_title_image_b64_data_doc_output'),
                "selected_offer_title_text": st.session_state.get('selected_offer_title_text_content_doc_output', 'Ihr Angebot'),
                "selected_cover_letter_text": st.session_state.get('selected_cover_letter_text_content_doc_output', 'Sehr geehrte Damen und Herren,'),
                "sections_to_include": st.session_state.get('pdf_selected_main_sections', ["ProjectOverview", "TechnicalComponents", "CostDetails"])
            }

            # PDF über die Engine generieren
            pdf_bytes = engine.generate_preview_pdf(**pdf_generation_params)
            
            if pdf_bytes:
                st.session_state.preview_pdf_bytes = pdf_bytes
                st.success("✅ Vorschau aktualisiert")
            else:
                st.error("❌ Fehler bei der Vorschau-Generierung")

    # --- Vorschau anzeigen ---
    if 'preview_pdf_bytes' in st.session_state:
        pdf_bytes = st.session_state.preview_pdf_bytes
        
        if preview_mode == "Schnell (erste 3 Seiten)":
            images = engine.pdf_to_images(pdf_bytes, max_pages=3)
            if images:
                for idx, img in enumerate(images):
                    st.markdown(f"**Seite {idx + 1}**")
                    st.image(img, use_column_width=True)
                    st.markdown("---")
            else:
                st.warning("Vorschau-Bilder konnten nicht erstellt werden.")
        else: # Vollständige Vorschau
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    
    with col1:
        st.markdown("### ⚙️ Vorschau-Optionen")
        
        # Schnelloptionen
        preview_mode = st.radio(
            "Vorschau-Modus",
            ["Schnellvorschau", "Vollständige Vorschau", "Seitenweise"],
            help="Schnellvorschau zeigt nur erste Seiten"
        )
        
        # Aktualisierungsoptionen
        auto_update = st.checkbox(
            "Automatische Aktualisierung",
            value=True,
            help="Vorschau wird bei Änderungen automatisch aktualisiert"
        )
        
        update_delay = st.slider(
            "Aktualisierungsverzögerung (Sek.)",
            min_value=1,
            max_value=10,
            value=3,
            disabled=not auto_update
        )
        
        # Anzeigeoptionen
        st.markdown("### 🎨 Anzeigeoptionen")
        
        preview_zoom = st.slider(
            "Zoom (%)",
            min_value=50,
            max_value=200,
            value=100,
            step=10
        )
        
        show_annotations = st.checkbox(
            "Anmerkungen anzeigen",
            value=True
        )
        
        # Manuelle Aktualisierung
        update_preview = st.button(
            "🔄 Vorschau aktualisieren",
            use_container_width=True,
            disabled=auto_update,
            key="preview_update_manual"
        )
    
    with col2:
        st.markdown("### 📄 PDF-Vorschau")
        
        # Vorschau-Container
        preview_container = st.container()
        
        # PDF generieren wenn Update angefordert
        if update_preview or auto_update or 'preview_pdf_bytes' not in st.session_state:
            with st.spinner("Generiere Vorschau..."):
                # Basis-Inklusionsoptionen
                inclusion_options = {
                    'include_company_logo': True,
                    'include_all_documents': True,
                    'include_optional_component_details': True,
                    'include_charts': True,
                    'selected_charts_for_pdf': ['monthly_generation_chart', 'deckungsgrad_chart']
                }
                
                # PDF generieren
                pdf_bytes = engine.generate_preview_pdf(
                    project_data=project_data,
                    analysis_results=analysis_results,
                    company_info=company_info,
                    inclusion_options=inclusion_options,
                    texts=texts,
                    company_logo_base64=company_info.get('logo_base64'),
                    selected_title_image_b64=None,
                    selected_offer_title_text="Ihr Photovoltaik-Angebot",
                    selected_cover_letter_text="",
                    sections_to_include=['ProjectOverview', 'TechnicalComponents', 'CostDetails'],
                    load_admin_setting_func=load_admin_setting_func,
                    save_admin_setting_func=save_admin_setting_func,
                    list_products_func=list_products_func,
                    get_product_by_id_func=get_product_by_id_func,
                    db_list_company_documents_func=db_list_company_documents_func,
                    active_company_id=active_company_id
                )
                
                if pdf_bytes:
                    st.session_state.preview_pdf_bytes = pdf_bytes
                    st.success("✅ Vorschau aktualisiert")
                else:
                    st.error("❌ Fehler bei der PDF-Generierung")
                    return None
        
        # Vorschau anzeigen
        if 'preview_pdf_bytes' in st.session_state:
            pdf_bytes = st.session_state.preview_pdf_bytes
            
            with preview_container:
                if preview_mode == "Schnellvorschau":
                    # Erste Seiten als Bilder anzeigen
                    images = engine.pdf_to_images(pdf_bytes, max_pages=3)
                    
                    if images:
                        for idx, img in enumerate(images):
                            st.markdown(f"**Seite {idx + 1}**")
                            
                            # Bild mit Zoom anzeigen
                            width = int(img.width * preview_zoom / 100)
                            height = int(img.height * preview_zoom / 100)
                            img_resized = img.resize((width, height))
                            
                            st.image(img_resized, use_column_width=True)
                            st.markdown("---")
                    else:
                        # Fallback: PDF-Viewer
                        st.markdown("**PDF-Viewer:**")
                        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                
                elif preview_mode == "Vollständige Vorschau":
                    # Komplettes PDF einbetten
                    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                
                elif preview_mode == "Seitenweise":
                    # Seitenweise Navigation
                    images = engine.pdf_to_images(pdf_bytes, max_pages=20)
                    
                    if images:
                        total_pages = len(images)
                        
                        # Seitennavigation
                        col_prev, col_page, col_next = st.columns([1, 2, 1])
                        
                        if 'preview_current_page' not in st.session_state:
                            st.session_state.preview_current_page = 0
                        
                        with col_prev:
                            if st.button("⬅️ Zurück", disabled=st.session_state.preview_current_page == 0, key="preview_page_back"):
                                st.session_state.preview_current_page -= 1
                                st.rerun()
                        
                        with col_page:
                            page_num = st.number_input(
                                "Seite",
                                min_value=1,
                                max_value=total_pages,
                                value=st.session_state.preview_current_page + 1,
                                key="page_selector"
                            )
                            if page_num - 1 != st.session_state.preview_current_page:
                                st.session_state.preview_current_page = page_num - 1
                                st.rerun()
                        
                        with col_next:
                            if st.button("Weiter ➡️", disabled=st.session_state.preview_current_page >= total_pages - 1, key="preview_page_forward"):
                                st.session_state.preview_current_page += 1
                                st.rerun()
                        
                        # Aktuelle Seite anzeigen
                        current_img = images[st.session_state.preview_current_page]
                        width = int(current_img.width * preview_zoom / 100)
                        height = int(current_img.height * preview_zoom / 100)
                        img_resized = current_img.resize((width, height))
                        
                        st.image(img_resized, use_column_width=True)
                        st.caption(f"Seite {st.session_state.preview_current_page + 1} von {total_pages}")
        
        # Download-Button
        if 'preview_pdf_bytes' in st.session_state:
            st.markdown("---")
            st.download_button(
                label="📥 Vorschau-PDF herunterladen",
                data=st.session_state.preview_pdf_bytes,
                file_name=f"Vorschau_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    # Auto-Update-Logik
    if auto_update:
        # Placeholder für Auto-Update-Implementierung
        # In einer echten Implementierung würde hier ein Timer laufen
        pass
    
    return st.session_state.get('preview_pdf_bytes')

def create_preview_thumbnail(pdf_bytes: bytes, page_num: int = 0, size: tuple = (200, 280)) -> Optional[bytes]:
    """Erstellt ein Thumbnail-Bild einer PDF-Seite"""
    if not PDF_PREVIEW_AVAILABLE or not pdf_bytes:
        return None
    
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_num >= len(pdf_document):
            return None
        
        page = pdf_document[page_num]
        pix = page.get_pixmap(dpi=100)
        img_data = pix.tobytes("png")
        
        # Bild laden und resizen
        img = Image.open(io.BytesIO(img_data))
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Zurück zu Bytes konvertieren
        output = io.BytesIO()
        img.save(output, format='PNG')
        thumbnail_bytes = output.getvalue()
        
        pdf_document.close()
        return thumbnail_bytes
        
    except Exception as e:
        print(f"Fehler bei Thumbnail-Erstellung: {e}")
        return None

# Änderungshistorie
# 2025-06-21, Gemini Ultra: Erweiterte PDF-Vorschau-Funktionalität implementiert
#                           - Live-Preview mit verschiedenen Modi
#                           - PDF-zu-Bild-Konvertierung für bessere Performance
#                           - Seitenweise Navigation
#                           - Zoom-Funktionalität
#                           - Cache-System für schnellere Vorschau
#                           - Auto-Update-Option
