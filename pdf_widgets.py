"""
PDF Drag & Drop Manager und Reihenfolgen-Editor
Autor: Gemini Ultra
Datum: 2025-06-21
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Callable
import json
import uuid
from datetime import datetime
import base64
import io

try:
    from streamlit_sortables import sort_items
    SORTABLES_AVAILABLE = True
except ImportError:
    SORTABLES_AVAILABLE = False

class PDFSectionManager:
    """Manager für PDF-Sektionen mit Drag & Drop"""
    
    def __init__(self):
        self.available_sections = {
            'cover_page': {
                'name': 'Deckblatt',
                'icon': '📄',
                'default_order': 0,
                'required': True,
                'configurable': True,
                'content_types': ['image', 'text']
            },
            'project_overview': {
                'name': 'Projektübersicht',
                'icon': '📋',
                'default_order': 1,
                'required': False,
                'configurable': True,
                'content_types': ['text', 'table']
            },
            'technical_components': {
                'name': 'Technische Komponenten',
                'icon': '⚙️',
                'default_order': 2,
                'required': False,
                'configurable': True,
                'content_types': ['text', 'image', 'table']
            },
            'cost_details': {
                'name': 'Kostendetails',
                'icon': '💰',
                'default_order': 3,
                'required': False,
                'configurable': True,
                'content_types': ['table', 'chart']
            },
            'economics': {
                'name': 'Wirtschaftlichkeit',
                'icon': '📊',
                'default_order': 4,
                'required': False,
                'configurable': True,
                'content_types': ['chart', 'table']
            },
            'custom_section': {
                'name': 'Benutzerdefinierter Abschnitt',
                'icon': '➕',
                'default_order': 99,
                'required': False,
                'configurable': True,
                'content_types': ['image', 'text', 'pdf', 'table']
            }
        }
        
        self.content_templates = {
            'text': {
                'name': 'Textblock',
                'icon': '📝',
                'default_content': 'Hier können Sie Ihren Text eingeben...'
            },
            'image': {
                'name': 'Bild',
                'icon': '🖼️',
                'default_content': None
            },
            'pdf': {
                'name': 'PDF-Dokument',
                'icon': '📑',
                'default_content': None
            },
            'table': {
                'name': 'Tabelle',
                'icon': '📊',
                'default_content': []
            },
            'chart': {
                'name': 'Diagramm',
                'icon': '📈',
                'default_content': None
            }
        }
    
    def initialize_session_state(self):
        """Initialisiert Session State für Drag & Drop"""
        if 'pdf_section_order' not in st.session_state:
            # Standard-Reihenfolge
            st.session_state.pdf_section_order = [
                key for key, section in sorted(
                    self.available_sections.items(),
                    key=lambda x: x[1]['default_order']
                )
            ]
        
        if 'pdf_custom_sections' not in st.session_state:
            st.session_state.pdf_custom_sections = {}
        
        if 'pdf_section_contents' not in st.session_state:
            st.session_state.pdf_section_contents = {}
    
    def render_drag_drop_interface(self, texts: Dict[str, str]):
        """Rendert die Drag & Drop Oberfläche"""
        st.markdown("### 🔀 PDF-Reihenfolgen-Manager")
        
        # Aktivierung der Drag & Drop Funktion
        enable_drag_drop = st.checkbox(
            "Drag & Drop Bearbeitung aktivieren",
            value=False,
            help="Aktiviert die erweiterte Bearbeitungsfunktion"
        )
        
        if not enable_drag_drop:
            st.info("Aktivieren Sie Drag & Drop, um die PDF-Reihenfolge anzupassen.")
            return
        
        # Hauptlayout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📚 Verfügbare Sektionen")
            self._render_available_sections()
        
        with col2:
            st.markdown("#### 📄 PDF-Struktur")
            self._render_pdf_structure()
        
        # Benutzerdefinierte Sektionen
        with st.expander("➕ Benutzerdefinierte Sektionen", expanded=False):
            self._render_custom_section_creator()
    
    def _render_available_sections(self):
        """Zeigt verfügbare Sektionen an"""
        for key, section in self.available_sections.items():
            if key not in st.session_state.pdf_section_order:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"{section['icon']} **{section['name']}**")
                
                with col2:
                    if st.button("➕", key=f"add_{key}"):
                        st.session_state.pdf_section_order.append(key)
                        st.rerun()
    
    def _render_pdf_structure(self):
        """Zeigt die aktuelle PDF-Struktur"""
        if SORTABLES_AVAILABLE:
            # Mit Drag & Drop Sortierung
            items = []
            for section_key in st.session_state.pdf_section_order:
                section = self.available_sections.get(section_key, {})
                items.append({
                    'id': section_key,
                    'name': f"{section.get('icon', '')} {section.get('name', section_key)}"
                })
            
            sorted_items = sort_items(items)
            st.session_state.pdf_section_order = [item['id'] for item in sorted_items]
        else:
            # Fallback ohne Drag & Drop
            new_order = []
            
            for idx, section_key in enumerate(st.session_state.pdf_section_order):
                section = self.available_sections.get(section_key, {})
                
                col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
                
                with col1:
                    st.markdown(f"**{idx + 1}.**")
                
                with col2:
                    st.markdown(f"{section.get('icon', '')} {section.get('name', section_key)}")
                
                with col3:
                    # Hoch/Runter Buttons
                    if idx > 0:
                        if st.button("⬆️", key=f"up_{section_key}"):
                            st.session_state.pdf_section_order[idx], st.session_state.pdf_section_order[idx-1] = \
                                st.session_state.pdf_section_order[idx-1], st.session_state.pdf_section_order[idx]
                            st.rerun()
                    
                    if idx < len(st.session_state.pdf_section_order) - 1:
                        if st.button("⬇️", key=f"down_{section_key}"):
                            st.session_state.pdf_section_order[idx], st.session_state.pdf_section_order[idx+1] = \
                                st.session_state.pdf_section_order[idx+1], st.session_state.pdf_section_order[idx]
                            st.rerun()
                
                with col4:
                    if not section.get('required', False):
                        if st.button("❌", key=f"remove_{section_key}"):
                            st.session_state.pdf_section_order.remove(section_key)
                            st.rerun()
                
                # Sektion bearbeiten
                if section.get('configurable', False):
                    with st.expander(f"Bearbeiten: {section.get('name', '')}", expanded=False):
                        self._render_section_editor(section_key, section)
                
                new_order.append(section_key)
    
    def _render_section_editor(self, section_key: str, section_info: Dict[str, Any]):
        """Editor für einzelne Sektionen"""
        st.markdown(f"**Inhalte für {section_info['name']}:**")
        
        # Inhaltsliste für diese Sektion
        if section_key not in st.session_state.pdf_section_contents:
            st.session_state.pdf_section_contents[section_key] = []
        
        contents = st.session_state.pdf_section_contents[section_key]
        
        # Vorhandene Inhalte anzeigen
        for idx, content in enumerate(contents):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                content_type = content.get('type', 'text')
                template = self.content_templates.get(content_type, {})
                st.markdown(f"{template.get('icon', '')} {template.get('name', '')}")
            
            with col2:
                # Content-spezifischer Editor
                self._render_content_editor(section_key, idx, content)
            
            with col3:
                if st.button("🗑️", key=f"delete_content_{section_key}_{idx}"):
                    contents.pop(idx)
                    st.rerun()
        
        # Neue Inhalte hinzufügen
        st.markdown("**Inhalt hinzufügen:**")
        
        available_types = section_info.get('content_types', ['text'])
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_content_type = st.selectbox(
                "Inhaltstyp",
                options=available_types,
                format_func=lambda x: f"{self.content_templates.get(x, {}).get('icon', '')} {self.content_templates.get(x, {}).get('name', x)}",
                key=f"new_content_type_{section_key}"
            )
        
        with col2:
            if st.button("➕ Hinzufügen", key=f"add_content_{section_key}"):
                new_content = {
                    'id': str(uuid.uuid4()),
                    'type': new_content_type,
                    'data': self.content_templates.get(new_content_type, {}).get('default_content')
                }
                contents.append(new_content)
                st.rerun()
    
    def _render_content_editor(self, section_key: str, content_idx: int, content: Dict[str, Any]):
        """Editor für einzelne Inhalte"""
        content_type = content.get('type', 'text')
        
        if content_type == 'text':
            # Texteditor
            content['data'] = st.text_area(
                "Text",
                value=content.get('data', ''),
                key=f"text_{section_key}_{content_idx}",
                height=100
            )
        
        elif content_type == 'image':
            # Bildupload
            uploaded_file = st.file_uploader(
                "Bild hochladen",
                type=['png', 'jpg', 'jpeg', 'gif'],
                key=f"image_{section_key}_{content_idx}"
            )
            
            if uploaded_file:
                content['data'] = {
                    'filename': uploaded_file.name,
                    'data': base64.b64encode(uploaded_file.read()).decode()
                }
                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
        
        elif content_type == 'pdf':
            # PDF-Upload
            uploaded_file = st.file_uploader(
                "PDF hochladen",
                type=['pdf'],
                key=f"pdf_{section_key}_{content_idx}"
            )
            
            if uploaded_file:
                content['data'] = {
                    'filename': uploaded_file.name,
                    'data': base64.b64encode(uploaded_file.read()).decode()
                }
                st.success(f"PDF '{uploaded_file.name}' hochgeladen")
        
        elif content_type == 'table':
            # Tabellen-Editor (vereinfacht)
            st.info("Tabellen-Editor wird implementiert...")
        
        elif content_type == 'chart':
            # Diagramm-Auswahl
            available_charts = [
                'monthly_generation_chart',
                'deckungsgrad_chart',
                'cost_savings_chart',
                'amortization_chart'
            ]
            
            content['data'] = st.selectbox(
                "Diagramm auswählen",
                options=available_charts,
                value=content.get('data'),
                key=f"chart_{section_key}_{content_idx}"
            )
    
    def _render_custom_section_creator(self):
        """Interface zum Erstellen benutzerdefinierter Sektionen"""
        st.markdown("#### Neue Sektion erstellen")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            section_name = st.text_input(
                "Sektionsname",
                placeholder="z.B. Referenzen",
                key="new_section_name"
            )
        
        with col2:
            section_icon = st.text_input(
                "Icon",
                value="📄",
                max_chars=2,
                key="new_section_icon"
            )
        
        content_types = st.multiselect(
            "Erlaubte Inhaltstypen",
            options=list(self.content_templates.keys()),
            default=['text', 'image'],
            format_func=lambda x: f"{self.content_templates[x]['icon']} {self.content_templates[x]['name']}"
        )
        
        if st.button("➕ Sektion erstellen", type="primary"):
            if section_name and content_types:
                section_key = f"custom_{uuid.uuid4().hex[:8]}"
                
                # Neue Sektion zu verfügbaren Sektionen hinzufügen
                self.available_sections[section_key] = {
                    'name': section_name,
                    'icon': section_icon,
                    'default_order': 99,
                    'required': False,
                    'configurable': True,
                    'content_types': content_types
                }
                
                # Zur aktuellen Reihenfolge hinzufügen
                st.session_state.pdf_section_order.append(section_key)
                
                # In benutzerdefinierten Sektionen speichern
                st.session_state.pdf_custom_sections[section_key] = {
                    'name': section_name,
                    'icon': section_icon,
                    'content_types': content_types,
                    'created': datetime.now().isoformat()
                }
                
                st.success(f"Sektion '{section_name}' wurde erstellt!")
                st.rerun()
            else:
                st.error("Bitte geben Sie einen Namen ein und wählen Sie mindestens einen Inhaltstyp.")
    
    def export_configuration(self) -> Dict[str, Any]:
        """Exportiert die aktuelle PDF-Konfiguration"""
        return {
            'section_order': st.session_state.pdf_section_order,
            'custom_sections': st.session_state.pdf_custom_sections,
            'section_contents': st.session_state.pdf_section_contents,
            'timestamp': datetime.now().isoformat()
        }
    
    def import_configuration(self, config: Dict[str, Any]):
        """Importiert eine PDF-Konfiguration"""
        if 'section_order' in config:
            st.session_state.pdf_section_order = config['section_order']
        
        if 'custom_sections' in config:
            st.session_state.pdf_custom_sections = config['custom_sections']
            # Custom Sections zu verfügbaren hinzufügen
            for key, section in config['custom_sections'].items():
                self.available_sections[key] = {
                    'name': section['name'],
                    'icon': section.get('icon', '📄'),
                    'default_order': 99,
                    'required': False,
                    'configurable': True,
                    'content_types': section.get('content_types', ['text'])
                }
        
        if 'section_contents' in config:
            st.session_state.pdf_section_contents = config['section_contents']

def render_pdf_structure_manager(texts: Dict[str, str]):
    """Haupt-Render-Funktion für PDF-Strukturmanager"""
    st.header("📋 PDF-Struktur & Reihenfolgen-Manager")
    
    # Manager initialisieren
    if 'pdf_section_manager' not in st.session_state:
        st.session_state.pdf_section_manager = PDFSectionManager()
    
    manager = st.session_state.pdf_section_manager
    manager.initialize_session_state()
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["🔀 Reihenfolge", "📥 Import/Export", "📚 Vorlagen"])
    
    with tab1:
        manager.render_drag_drop_interface(texts)
    
    with tab2:
        st.markdown("### 📥 Konfiguration Import/Export")
        
        col1, col2 = st.columns(2)
        
        with# filepath: c:\12345\pdf_drag_drop_manager.py
"""
PDF Drag & Drop Manager und Reihenfolgen-Editor
Autor: Gemini Ultra
Datum: 2025-06-21
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Callable
import json
import uuid
from datetime import datetime
import base64
import io

try:
    from streamlit_sortables import sort_items
    SORTABLES_AVAILABLE = True
except ImportError:
    SORTABLES_AVAILABLE = False

class PDFSectionManager:
    """Manager für PDF-Sektionen mit Drag & Drop"""
    
    def __init__(self):
        self.available_sections = {
            'cover_page': {
                'name': 'Deckblatt',
                'icon': '📄',
                'default_order': 0,
                'required': True,
                'configurable': True,
                'content_types': ['image', 'text']
            },
            'project_overview': {
                'name': 'Projektübersicht',
                'icon': '📋',
                'default_order': 1,
                'required': False,
                'configurable': True,
                'content_types': ['text', 'table']
            },
            'technical_components': {
                'name': 'Technische Komponenten',
                'icon': '⚙️',
                'default_order': 2,
                'required': False,
                'configurable': True,
                'content_types': ['text', 'image', 'table']
            },
            'cost_details': {
                'name': 'Kostendetails',
                'icon': '💰',
                'default_order': 3,
                'required': False,
                'configurable': True,
                'content_types': ['table', 'chart']
            },
            'economics': {
                'name': 'Wirtschaftlichkeit',
                'icon': '📊',
                'default_order': 4,
                'required': False,
                'configurable': True,
                'content_types': ['chart', 'table']
            },
            'custom_section': {
                'name': 'Benutzerdefinierter Abschnitt',
                'icon': '➕',
                'default_order': 99,
                'required': False,
                'configurable': True,
                'content_types': ['image', 'text', 'pdf', 'table']
            }
        }
        
        self.content_templates = {
            'text': {
                'name': 'Textblock',
                'icon': '📝',
                'default_content': 'Hier können Sie Ihren Text eingeben...'
            },
            'image': {
                'name': 'Bild',
                'icon': '🖼️',
                'default_content': None
            },
            'pdf': {
                'name': 'PDF-Dokument',
                'icon': '📑',
                'default_content': None
            },
            'table': {
                'name': 'Tabelle',
                'icon': '📊',
                'default_content': []
            },
            'chart': {
                'name': 'Diagramm',
                'icon': '📈',
                'default_content': None
            }
        }
    
    def initialize_session_state(self):
        """Initialisiert Session State für Drag & Drop"""
        if 'pdf_section_order' not in st.session_state:
            # Standard-Reihenfolge
            st.session_state.pdf_section_order = [
                key for key, section in sorted(
                    self.available_sections.items(),
                    key=lambda x: x[1]['default_order']
                )
            ]
        
        if 'pdf_custom_sections' not in st.session_state:
            st.session_state.pdf_custom_sections = {}
        
        if 'pdf_section_contents' not in st.session_state:
            st.session_state.pdf_section_contents = {}
    
    def render_drag_drop_interface(self, texts: Dict[str, str]):
        """Rendert die Drag & Drop Oberfläche"""
        st.markdown("### 🔀 PDF-Reihenfolgen-Manager")
        
        # Aktivierung der Drag & Drop Funktion
        enable_drag_drop = st.checkbox(
            "Drag & Drop Bearbeitung aktivieren",
            value=False,
            help="Aktiviert die erweiterte Bearbeitungsfunktion"
        )
        
        if not enable_drag_drop:
            st.info("Aktivieren Sie Drag & Drop, um die PDF-Reihenfolge anzupassen.")
            return
        
        # Hauptlayout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📚 Verfügbare Sektionen")
            self._render_available_sections()
        
        with col2:
            st.markdown("#### 📄 PDF-Struktur")
            self._render_pdf_structure()
        
        # Benutzerdefinierte Sektionen
        with st.expander("➕ Benutzerdefinierte Sektionen", expanded=False):
            self._render_custom_section_creator()
    
    def _render_available_sections(self):
        """Zeigt verfügbare Sektionen an"""
        for key, section in self.available_sections.items():
            if key not in st.session_state.pdf_section_order:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"{section['icon']} **{section['name']}**")
                
                with col2:
                    if st.button("➕", key=f"add_{key}"):
                        st.session_state.pdf_section_order.append(key)
                        st.rerun()
    
    def _render_pdf_structure(self):
        """Zeigt die aktuelle PDF-Struktur"""
        if SORTABLES_AVAILABLE:
            # Mit Drag & Drop Sortierung
            items = []
            for section_key in st.session_state.pdf_section_order:
                section = self.available_sections.get(section_key, {})
                items.append({
                    'id': section_key,
                    'name': f"{section.get('icon', '')} {section.get('name', section_key)}"
                })
            
            sorted_items = sort_items(items)
            st.session_state.pdf_section_order = [item['id'] for item in sorted_items]
        else:
            # Fallback ohne Drag & Drop
            new_order = []
            
            for idx, section_key in enumerate(st.session_state.pdf_section_order):
                section = self.available_sections.get(section_key, {})
                
                col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
                
                with col1:
                    st.markdown(f"**{idx + 1}.**")
                
                with col2:
                    st.markdown(f"{section.get('icon', '')} {section.get('name', section_key)}")
                
                with col3:
                    # Hoch/Runter Buttons
                    if idx > 0:
                        if st.button("⬆️", key=f"up_{section_key}"):
                            st.session_state.pdf_section_order[idx], st.session_state.pdf_section_order[idx-1] = \
                                st.session_state.pdf_section_order[idx-1], st.session_state.pdf_section_order[idx]
                            st.rerun()
                    
                    if idx < len(st.session_state.pdf_section_order) - 1:
                        if st.button("⬇️", key=f"down_{section_key}"):
                            st.session_state.pdf_section_order[idx], st.session_state.pdf_section_order[idx+1] = \
                                st.session_state.pdf_section_order[idx+1], st.session_state.pdf_section_order[idx]
                            st.rerun()
                
                with col4:
                    if not section.get('required', False):
                        if st.button("❌", key=f"remove_{section_key}"):
                            st.session_state.pdf_section_order.remove(section_key)
                            st.rerun()
                
                # Sektion bearbeiten
                if section.get('configurable', False):
                    with st.expander(f"Bearbeiten: {section.get('name', '')}", expanded=False):
                        self._render_section_editor(section_key, section)
                
                new_order.append(section_key)
    
    def _render_section_editor(self, section_key: str, section_info: Dict[str, Any]):
        """Editor für einzelne Sektionen"""
        st.markdown(f"**Inhalte für {section_info['name']}:**")
        
        # Inhaltsliste für diese Sektion
        if section_key not in st.session_state.pdf_section_contents:
            st.session_state.pdf_section_contents[section_key] = []
        
        contents = st.session_state.pdf_section_contents[section_key]
        
        # Vorhandene Inhalte anzeigen
        for idx, content in enumerate(contents):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                content_type = content.get('type', 'text')
                template = self.content_templates.get(content_type, {})
                st.markdown(f"{template.get('icon', '')} {template.get('name', '')}")
            
            with col2:
                # Content-spezifischer Editor
                self._render_content_editor(section_key, idx, content)
            
            with col3:
                if st.button("🗑️", key=f"delete_content_{section_key}_{idx}"):
                    contents.pop(idx)
                    st.rerun()
        
        # Neue Inhalte hinzufügen
        st.markdown("**Inhalt hinzufügen:**")
        
        available_types = section_info.get('content_types', ['text'])
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_content_type = st.selectbox(
                "Inhaltstyp",
                options=available_types,
                format_func=lambda x: f"{self.content_templates.get(x, {}).get('icon', '')} {self.content_templates.get(x, {}).get('name', x)}",
                key=f"new_content_type_{section_key}"
            )
        
        with col2:
            if st.button("➕ Hinzufügen", key=f"add_content_{section_key}"):
                new_content = {
                    'id': str(uuid.uuid4()),
                    'type': new_content_type,
                    'data': self.content_templates.get(new_content_type, {}).get('default_content')
                }
                contents.append(new_content)
                st.rerun()
    
    def _render_content_editor(self, section_key: str, content_idx: int, content: Dict[str, Any]):
        """Editor für einzelne Inhalte"""
        content_type = content.get('type', 'text')
        
        if content_type == 'text':
            # Texteditor
            content['data'] = st.text_area(
                "Text",
                value=content.get('data', ''),
                key=f"text_{section_key}_{content_idx}",
                height=100
            )
        
        elif content_type == 'image':
            # Bildupload
            uploaded_file = st.file_uploader(
                "Bild hochladen",
                type=['png', 'jpg', 'jpeg', 'gif'],
                key=f"image_{section_key}_{content_idx}"
            )
            
            if uploaded_file:
                content['data'] = {
                    'filename': uploaded_file.name,
                    'data': base64.b64encode(uploaded_file.read()).decode()
                }
                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
        
        elif content_type == 'pdf':
            # PDF-Upload
            uploaded_file = st.file_uploader(
                "PDF hochladen",
                type=['pdf'],
                key=f"pdf_{section_key}_{content_idx}"
            )
            
            if uploaded_file:
                content['data'] = {
                    'filename': uploaded_file.name,
                    'data': base64.b64encode(uploaded_file.read()).decode()
                }
                st.success(f"PDF '{uploaded_file.name}' hochgeladen")
        
        elif content_type == 'table':
            # Tabellen-Editor (vereinfacht)
            st.info("Tabellen-Editor wird implementiert...")
        
        elif content_type == 'chart':
            # Diagramm-Auswahl
            available_charts = [
                'monthly_generation_chart',
                'deckungsgrad_chart',
                'cost_savings_chart',
                'amortization_chart'
            ]
            
            content['data'] = st.selectbox(
                "Diagramm auswählen",
                options=available_charts,
                value=content.get('data'),
                key=f"chart_{section_key}_{content_idx}"
            )
    
    def _render_custom_section_creator(self):
        """Interface zum Erstellen benutzerdefinierter Sektionen"""
        st.markdown("#### Neue Sektion erstellen")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            section_name = st.text_input(
                "Sektionsname",
                placeholder="z.B. Referenzen",
                key="new_section_name"
            )
        
        with col2:
            section_icon = st.text_input(
                "Icon",
                value="📄",
                max_chars=2,
                key="new_section_icon"
            )
        
        content_types = st.multiselect(
            "Erlaubte Inhaltstypen",
            options=list(self.content_templates.keys()),
            default=['text', 'image'],
            format_func=lambda x: f"{self.content_templates[x]['icon']} {self.content_templates[x]['name']}"
        )
        
        if st.button("➕ Sektion erstellen", type="primary"):
            if section_name and content_types:
                section_key = f"custom_{uuid.uuid4().hex[:8]}"
                
                # Neue Sektion zu verfügbaren Sektionen hinzufügen
                self.available_sections[section_key] = {
                    'name': section_name,
                    'icon': section_icon,
                    'default_order': 99,
                    'required': False,
                    'configurable': True,
                    'content_types': content_types
                }
                
                # Zur aktuellen Reihenfolge hinzufügen
                st.session_state.pdf_section_order.append(section_key)
                
                # In benutzerdefinierten Sektionen speichern
                st.session_state.pdf_custom_sections[section_key] = {
                    'name': section_name,
                    'icon': section_icon,
                    'content_types': content_types,
                    'created': datetime.now().isoformat()
                }
                
                st.success(f"Sektion '{section_name}' wurde erstellt!")
                st.rerun()
            else:
                st.error("Bitte geben Sie einen Namen ein und wählen Sie mindestens einen Inhaltstyp.")
    
    def export_configuration(self) -> Dict[str, Any]:
        """Exportiert die aktuelle PDF-Konfiguration"""
        return {
            'section_order': st.session_state.pdf_section_order,
            'custom_sections': st.session_state.pdf_custom_sections,
            'section_contents': st.session_state.pdf_section_contents,
            'timestamp': datetime.now().isoformat()
        }
    
    def import_configuration(self, config: Dict[str, Any]):
        """Importiert eine PDF-Konfiguration"""
        if 'section_order' in config:
            st.session_state.pdf_section_order = config['section_order']
        
        if 'custom_sections' in config:
            st.session_state.pdf_custom_sections = config['custom_sections']
            # Custom Sections zu verfügbaren hinzufügen
            for key, section in config['custom_sections'].items():
                self.available_sections[key] = {
                    'name': section['name'],
                    'icon': section.get('icon', '📄'),
                    'default_order': 99,
                    'required': False,
                    'configurable': True,
                    'content_types': section.get('content_types', ['text'])
                }
        
        if 'section_contents' in config:
            st.session_state.pdf_section_contents = config['section_contents']

# ...existing code...

def render_pdf_structure_manager(texts: Dict[str, str]):
    """Haupt-Render-Funktion für PDF-Strukturmanager"""
    st.header("📋 PDF-Struktur & Reihenfolgen-Manager")
    
    # Manager initialisieren
    if 'pdf_section_manager' not in st.session_state:
        st.session_state.pdf_section_manager = PDFSectionManager()
    
    manager = st.session_state.pdf_section_manager
    manager.initialize_session_state()
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["🔀 Reihenfolge", "📥 Import/Export", "📚 Vorlagen"])
    
    with tab1:
        manager.render_drag_drop_interface(texts)
    
    with tab2:
        st.markdown("### 📥 Konfiguration Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export")
            
            # Konfiguration exportieren
            if st.button("📤 Konfiguration exportieren", use_container_width=True):
                config = manager.export_configuration()
                config_json = json.dumps(config, indent=2, ensure_ascii=False)
                
                st.download_button(
                    label="💾 JSON herunterladen",
                    data=config_json,
                    file_name=f"pdf_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                st.success("✅ Konfiguration exportiert!")
        
        with col2:
            st.markdown("#### Import")
            
            uploaded_file = st.file_uploader(
                "Konfigurationsdatei hochladen",
                type=['json'],
                help="Laden Sie eine zuvor exportierte PDF-Konfiguration"
            )
            
            if uploaded_file:
                try:
                    config = json.load(uploaded_file)
                    manager.import_configuration(config)
                    st.success("✅ Konfiguration importiert!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler beim Import: {e}")
    
    with tab3:
        st.markdown("### 📚 PDF-Vorlagen")
        
        # Vordefinierte Vorlagen
        templates = {
            'standard': {
                'name': 'Standard-Angebot',
                'description': 'Vollständiges Angebot mit allen Details',
                'sections': ['cover_page', 'project_overview', 'technical_components', 'cost_details', 'economics']
            },
            'compact': {
                'name': 'Kompakt-Angebot',
                'description': 'Kurze Übersicht mit wichtigsten Informationen',
                'sections': ['cover_page', 'project_overview', 'cost_details']
            },
            'technical': {
                'name': 'Technisches Angebot',
                'description': 'Fokus auf technische Details',
                'sections': ['cover_page', 'technical_components', 'economics']
            }
        }
        
        # Vorlage auswählen
        selected_template = st.selectbox(
            "Vorlage auswählen",
            options=list(templates.keys()),
            format_func=lambda x: templates[x]['name']
        )
        
        if selected_template:
            template = templates[selected_template]
            st.info(f"**Beschreibung:** {template['description']}")
            
            # Vorschau der Sektionen
            st.markdown("**Enthaltene Sektionen:**")
            for section_key in template['sections']:
                section = manager.available_sections.get(section_key, {})
                st.markdown(f"- {section.get('icon', '')} {section.get('name', section_key)}")
            
            if st.button("📥 Vorlage anwenden", type="primary"):
                st.session_state.pdf_section_order = template['sections'].copy()
                st.success(f"✅ Vorlage '{template['name']}' angewendet!")
                st.rerun()

# Änderungshistorie
# 2025-06-21, Gemini Ultra: PDF Drag & Drop Manager mit Reihenfolgen-Editor implementiert