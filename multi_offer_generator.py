# multi_offer_generator.py
"""
Multi-Firmen-Angebotsgenerator
Erstellt mehrere Angebote für verschiedene Firmen mit einem Klick
VERSION 3.0 - KORRIGIERT: Verwendet Kundendaten aus Projekt und Bedarfsanalyse
"""
import logging
import os
import tempfile
from datetime import datetime
import streamlit as st
import zipfile
import io
import re
import pandas as pd
import json
import random
from typing import Dict, List, Any, Callable, Optional
import traceback

try:
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
except ImportError:
    # Erstelle Dummy-Klassen, wenn ReportLab nicht installiert ist
    class Table: 
        def __init__(self, *args, **kwargs): pass
        def setStyle(self, *args, **kwargs): pass
    
    class TableStyle: 
        def __init__(self, *args, **kwargs): pass
        def add(self, *args, **kwargs): pass
    
    class Paragraph: 
        def __init__(self, *args, **kwargs): pass
    
    def getSampleStyleSheet(): return {}

try:
    from tqdm import tqdm
except ImportError:
    # Fallback, falls tqdm nicht installiert ist
    print("Hinweis: Für eine Fortschrittsanzeige installieren Sie 'tqdm' via 'pip install tqdm'.")
    tqdm = lambda x, **kwargs: x

# Import der bestehenden Module
try:
    from database import (
        get_db_connection,
        list_companies,
        get_company,
        load_admin_setting,
        save_admin_setting,
        list_company_documents,
    )
    from calculations import perform_calculations, calculate_offer_details
    from pdf_generator import generate_offer_pdf, create_offer_pdf, merge_pdfs
    from product_db import get_product_by_id, list_products
    
    # PDF Output Directory - lokale Definition statt Import
    PDF_OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdf_output")
except ImportError as e:
    st.error(f"Import-Fehler im Multi-Angebots-Generator: {e}")
    # Fallback für PDF_OUTPUT_DIRECTORY
    PDF_OUTPUT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdf_output")


def get_text_mog(key: str, fallback: str) -> str:
    """Hilfsfunktion für Texte"""
    return st.session_state.get("TEXTS", {}).get(key, fallback)


class MultiCompanyOfferGenerator:
    """Generator für Multi-Firmen-Angebote - übernimmt Kundendaten aus Projekt"""

    def __init__(self):
        self.customer_data = {}
        self.selected_companies = []
        self.offer_settings = {}
        self.products = self._load_all_products()

    def initialize_session_state(self):
        """Initialisiert Session State"""
        if "multi_offer_customer_data" not in st.session_state:
            st.session_state.multi_offer_customer_data = {}
        if "multi_offer_selected_companies" not in st.session_state:
            st.session_state.multi_offer_selected_companies = []
        if "multi_offer_settings" not in st.session_state:
            st.session_state.multi_offer_settings = {
                "module_quantity": 20,
                "include_storage": True,
            }

    def _load_all_products(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lädt alle Produkte und kategorisiert sie."""
        try:
            from product_db import list_products  # Lokaler Import
            all_products = list_products()
            categorized = {"module": [], "inverter": [], "storage": [], "other": []}
            for p in all_products:
                cat = p.get("category", "Sonstiges").lower()
                if "modul" in cat: categorized["module"].append(p)
                elif "wechselrichter" in cat: categorized["inverter"].append(p)
                elif "speicher" in cat or "battery" in cat: categorized["storage"].append(p)
                else: categorized["other"].append(p)
            return categorized
        except Exception as e:
            st.warning(f"Konnte Produkte nicht laden: {e}")
            return {"module": [], "inverter": [], "storage": [], "other": []}

    def _get_available_companies(self) -> List[Dict[str, Any]]:
        """Lädt verfügbare Firmen."""
        try:
            from database import list_companies  # Lokaler Import
            return list_companies()
        except Exception as e:
            st.warning(f"Konnte Firmen nicht laden: {e}")
            return []
    
    def get_available_companies(self) -> List[Dict[str, Any]]:
        """Öffentliche Methode zum Laden verfügbarer Firmen."""
        return self._get_available_companies()
            
    def _generate_single_company_pdf(self, offer_data: Dict, company_info: Dict, company_index: int) -> Optional[bytes]:
        """Wrapper, der den finalen `generate_offer_pdf` für eine Firma aufruft."""
        try:
            from pdf_generator import generate_offer_pdf # Lokaler Import
            from database import load_admin_setting, save_admin_setting, list_company_documents
            from product_db import list_products, get_product_by_id

            # Annahme: UI-Einstellungen werden im session_state gehalten
            settings = st.session_state.get("multi_offer_settings", {})
            
            # Hier müssen alle Parameter für generate_offer_pdf bereitgestellt werden
            # Dies ist eine vereinfachte Version. Sie müssen dies an Ihre finale Funktionssignatur anpassen.
            pdf_bytes = generate_offer_pdf(
                project_data=offer_data.get('project_data', {}),
                analysis_results=offer_data.get('analysis_results', {}),
                company_info=company_info,
                texts=self.texts,
                theme_name=settings.get('theme_name', 'Blau Elegant'),
                inclusion_options=settings.get('inclusion_options', {}),
                section_order=settings.get('section_order', []),
                # ... weitere Parameter ...
            )
            return pdf_bytes
        except Exception as e:
            st.error(f"Fehler bei PDF-Generierung für {company_info.get('name', 'Unbekannt')}: {e}")
            traceback.print_exc()
            return None

    def render_customer_input(self):
        """Übernimmt Kundendaten aus der Projekt-/Bedarfsanalyse"""
        st.subheader("Schritt 1: Kundendaten aus Projekt übernehmen")
        
        # Versuche Kundendaten aus project_data zu übernehmen
        project_data = st.session_state.get("project_data", {})
        customer_data = project_data.get("customer_data", {})
        
        if customer_data:
            # Daten gefunden - anzeigen und übernehmen
            st.success("✅ Kundendaten aus Projekt-/Bedarfsanalyse gefunden!")
            
            cols = st.columns(2)
            with cols[0]:
                st.write("**Kundendaten:**")
                st.write(f"Name: {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}")
                st.write(f"E-Mail: {customer_data.get('email', 'Nicht angegeben')}")
                st.write(f"Telefon: {customer_data.get('phone', 'Nicht angegeben')}")
            
            with cols[1]:
                st.write("**Adresse:**")
                st.write(f"Straße: {customer_data.get('address', 'Nicht angegeben')}")
                st.write(f"PLZ/Ort: {customer_data.get('zip_code', '')} {customer_data.get('city', '')}")
            
            # Kundendaten in multi_offer_customer_data übernehmen
            st.session_state.multi_offer_customer_data = customer_data.copy()
            
            # Projektdaten anzeigen falls verfügbar
            if project_data.get("consumption_data"):
                st.write("**Verbrauchsdaten:**")
                consumption = project_data["consumption_data"]
                st.write(f"Jahresverbrauch: {consumption.get('annual_consumption', 'N/A')} kWh")
                st.write(f"Strompreis: {consumption.get('electricity_price', 'N/A')} €/kWh")
              # Projektdaten auch in session state speichern für PDF-Generierung
            st.session_state.multi_offer_project_data = project_data.copy()
            
        else:
            # Fallback: Manuelle Eingabe wenn keine Projektdaten vorhanden
            st.warning("⚠️ Keine Kundendaten aus Projekt gefunden. Bitte zuerst die Projekt-/Bedarfsanalyse durchführen oder Daten manuell eingeben.")
            
            with st.form("customer_data_form_multi"):
                cols = st.columns(2)
                data = st.session_state.multi_offer_customer_data
                
                data["salutation"] = cols[0].selectbox(
                    "Anrede",
                    ["Herr", "Frau", "Divers"],
                    index=["Herr", "Frau", "Divers"].index(data.get("salutation", "Herr")),
                )
                data["first_name"] = cols[0].text_input(
                    "Vorname", value=data.get("first_name", "")
                )
                data["last_name"] = cols[1].text_input(
                    "Nachname", value=data.get("last_name", "")
                )
                data["address"] = st.text_input(
                    "Straße & Hausnummer", value=data.get("address", "")
                )
                data["zip_code"] = cols[0].text_input("PLZ", value=data.get("zip_code", ""))
                data["city"] = cols[1].text_input("Ort", value=data.get("city", ""))
                data["email"] = st.text_input("E-Mail", value=data.get("email", ""))
                data["phone"] = st.text_input("Telefon", value=data.get("phone", ""))
                
                if st.form_submit_button("Kundendaten speichern"):
                    st.success("Kundendaten gespeichert.")
        
        return bool(st.session_state.multi_offer_customer_data.get("first_name"))

    def render_company_selection(self):
        """Schritt 2: Firmenauswahl - Vollständig flexibel für 2-20+ Firmen"""
        st.subheader("Schritt 2: Firmen für Angebote auswählen")
        
        all_companies = self._get_available_companies()
        if not all_companies:
            st.warning("Keine Firmen in der Datenbank gefunden. Bitte im Admin-Panel anlegen.")
            return False
        
        # Erweiterte Firmenauswahl-UI
        cols = st.columns([3, 1])
        
        with cols[0]:
            company_options = {c["name"]: c["id"] for c in all_companies}
            selected_company_names = st.multiselect(
                f"Wählen Sie 2-{len(all_companies)} Firmen aus (unbegrenzt):",
                options=list(company_options.keys()),
                default=[
                    name
                    for name, cid in company_options.items()
                    if cid in st.session_state.multi_offer_selected_companies
                ],
                help=f"Verfügbare Firmen: {len(all_companies)} | Keine Begrenzung auf 5 Firmen!"
            )
        
        with cols[1]:
            # Schnellauswahl-Buttons
            if st.button("🎯 Alle auswählen"):
                st.session_state.multi_offer_selected_companies = list(company_options.values())
                st.rerun()
            if st.button("❌ Alle abwählen"):
                st.session_state.multi_offer_selected_companies = []
                st.rerun()
        
        st.session_state.multi_offer_selected_companies = [
            company_options[name] for name in selected_company_names
        ]
        
        # Erweiterte Firmen-Übersicht
        if st.session_state.multi_offer_selected_companies:
            num_companies = len(st.session_state.multi_offer_selected_companies)
            
            # Status-Übersicht
            if num_companies == 1:
                st.info("ℹ️ **1 Firma ausgewählt** - Für echte Multi-Angebote mindestens 2 Firmen empfohlen.")
            elif num_companies <= 5:
                st.success(f"✅ **{num_companies} Firmen ausgewählt** - Optimale Anzahl für Vergleichsangebote!")
            elif num_companies <= 10:
                st.success(f"✅ **{num_companies} Firmen ausgewählt** - Umfassende Marktabdeckung!")
            else:
                st.success(f"✅ **{num_companies} Firmen ausgewählt** - Maximale Auswahl für Kunden!")
            
            # Firmen-Vorschau in expandierbarer Sektion
            with st.expander(f"📋 Gewählte Firmen anzeigen ({num_companies})", expanded=num_companies <= 8):
                preview_cols = st.columns(min(4, num_companies))
                for i, company_id in enumerate(st.session_state.multi_offer_selected_companies[:12]):  # Max 12 in Vorschau
                    col_index = i % 4
                    try:
                        company = get_company(company_id) if callable(get_company) else {"name": f"Firma {company_id}", "id": company_id}
                        with preview_cols[col_index]:
                            st.markdown(f"**{i+1}. {company.get('name', 'Unbekannt')}**")
                            st.caption(f"ID: {company_id}")
                    except:
                        with preview_cols[col_index]:
                            st.markdown(f"**{i+1}. Firma {company_id}**")
                            st.caption(f"ID: {company_id}")
                
                if num_companies > 12:
                    st.caption(f"... und {num_companies-12} weitere Firmen")
            
            return True
        else:
            st.warning("⚠️ Bitte mindestens eine Firma auswählen. Für Multi-Angebote sind 2+ Firmen empfohlen.")
            return False

    def render_offer_configuration(self):
        """Schritt 3: Angebotskonfiguration"""
        st.subheader("Schritt 3: Globale Angebotskonfiguration")
        
        settings = st.session_state.multi_offer_settings
        
        # Basis-Einstellungen
        cols = st.columns(3)
        
        settings["module_quantity"] = cols[0].slider(
            "Anzahl der Module", 5, 100, settings.get("module_quantity", 20)
        )
        settings["include_storage"] = cols[1].checkbox(
            "Batteriespeicher ins Angebot aufnehmen?",
            value=settings.get("include_storage", True),
        )
          # NEUE FEATURE: Automatische Preisstaffelung
        st.markdown("### 🎯 Automatische Produktrotation & Preisstaffelung")
        auto_cols = st.columns(3)
        
        settings["enable_product_rotation"] = auto_cols[0].checkbox(
            "🔄 Automatische Produktrotation aktivieren",
            value=settings.get("enable_product_rotation", True),
            help="Jede Firma bekommt ein anderes Produkt aus der gleichen Kategorie"
        )
        
        if settings["enable_product_rotation"]:
            settings["product_rotation_step"] = auto_cols[1].slider(
                "📦 Produktrotation-Schritt", 
                1, 5, 
                settings.get("product_rotation_step", 1),
                help="Wie viele Produkte überspringen? 1=nächstes, 2=übernächstes, etc."
            )
        else:
            settings["product_rotation_step"] = 1
        
        settings["price_increment_percent"] = auto_cols[2].slider(
            "💰 Preisstaffelung pro Firma (%)", 
            0.0, 20.0, 
            settings.get("price_increment_percent", 3.0),
            step=0.1,
            help="Vollständig anpassbar: 0% = keine Steigerung, bis 20% möglich"
        )
        
        # Erweiterte Einstellungen in Expander
        with st.expander("🔧 Erweiterte Rotation & Preiseinstellungen"):
            adv_cols = st.columns(2)
            
            with adv_cols[0]:
                settings["rotation_mode"] = st.selectbox(
                    "Rotationsmodus",
                    ["linear", "zufällig", "kategorie-spezifisch"],
                    index=["linear", "zufällig", "kategorie-spezifisch"].index(settings.get("rotation_mode", "linear")),
                    help="Linear: der Reihe nach, Zufällig: per Zufall, Kategorie-spezifisch: unterschiedliche Schritte pro Kategorie"
                )
                
                if settings["rotation_mode"] == "kategorie-spezifisch":
                    st.write("**Kategorie-spezifische Rotation:**")
                    settings["module_rotation_step"] = st.slider("Module-Rotation", 1, 10, settings.get("module_rotation_step", 1))
                    settings["inverter_rotation_step"] = st.slider("Wechselrichter-Rotation", 1, 10, settings.get("inverter_rotation_step", 1))
                    settings["storage_rotation_step"] = st.slider("Speicher-Rotation", 1, 10, settings.get("storage_rotation_step", 1))
            
            with adv_cols[1]:
                settings["price_calculation_mode"] = st.selectbox(
                    "Preisberechnungsmodus",
                    ["linear", "exponentiell", "custom"],
                    index=["linear", "exponentiell", "custom"].index(settings.get("price_calculation_mode", "linear")),
                    help="Linear: +X% pro Firma, Exponentiell: X%^Firma, Custom: individuelle Faktoren"
                )
                
                if settings["price_calculation_mode"] == "exponentiell":
                    settings["price_exponent"] = st.slider(
                        "Exponentieller Faktor", 
                        1.01, 1.20, 
                        settings.get("price_exponent", 1.03),
                        step=0.01,
                        help="Firma 1: 100%, Firma 2: 103%, Firma 3: 106.09%, etc."
                    )
                elif settings["price_calculation_mode"] == "custom":
                    st.text_area(
                        "Custom Preisfaktoren (JSON)",
                        value=settings.get("custom_price_factors", "[1.0, 1.03, 1.07, 1.12, 1.18]"),
                        help="JSON-Array mit Preisfaktoren für jede Firma, z.B. [1.0, 1.05, 1.15, 1.25]"
                    )
        
        # Dynamische Vorschau basierend auf ausgewählten Firmen
        if st.session_state.multi_offer_selected_companies:
            num_companies = len(st.session_state.multi_offer_selected_companies)
            st.markdown(f"### 📋 Vorschau für {num_companies} Firmen")
            
            preview_cols = st.columns(min(4, num_companies))
            for i in range(min(4, num_companies)):  # Zeige max 4 Firmen-Previews
                with preview_cols[i]:
                    if settings["enable_product_rotation"]:
                        st.info(f"**Firma {i+1}**\n🔄 Produkt-Offset: {i * settings.get('product_rotation_step', 1)}")
                    else:
                        st.info(f"**Firma {i+1}**\n📦 Gleiches Produkt")
                    
                    if settings["price_increment_percent"] > 0:
                        if settings["price_calculation_mode"] == "linear":
                            price_factor = 1.0 + (i * settings["price_increment_percent"] / 100.0)
                        elif settings["price_calculation_mode"] == "exponentiell":
                            price_factor = settings.get("price_exponent", 1.03) ** i
                        else:  # custom
                            try:
                                import json
                                factors = json.loads(settings.get("custom_price_factors", "[1.0]"))
                                price_factor = factors[i] if i < len(factors) else factors[-1]
                            except:
                                price_factor = 1.0 + (i * 0.03)
                        
                        st.success(f"💰 Preisfaktor: {price_factor:.3f} ({(price_factor-1)*100:.1f}%)")
                    else:
                        st.success("💰 Originalpreis")
            
            if num_companies > 4:
                st.caption(f"... und {num_companies-4} weitere Firmen mit entsprechender Rotation/Preisstaffelung")
        
        if settings["enable_product_rotation"]:
            st.info("ℹ️ **Produktrotation aktiv:** Jede Firma erhält automatisch andere Produkte derselben Kategorie (sofern verfügbar).")
        
        if settings["price_increment_percent"] > 0:
            st.info(f"ℹ️ **Preisstaffelung aktiv:** Vollständig anpassbare Preisgestaltung für alle Firmen.")
        
        st.markdown("---")
        products = self.products
        
        # Produktauswahl
        st.markdown("### 📦 Basisprodukte auswählen")
        prod_cols = st.columns(3)
        
        # PV-Modul auswählen
        with prod_cols[0]:
            if products.get("module"):
                module_options = {p["model_name"]: p["id"] for p in products["module"]}
                default_module = settings.get("selected_module_id")
                default_module_index = (
                    list(module_options.values()).index(default_module)
                    if default_module in module_options.values()
                    else 0
                )
                selected_module_name = st.selectbox(
                    "🔋 PV-Modul (Basis)",
                    options=list(module_options.keys()),
                    index=default_module_index,
                    help="Erste Firma erhält dieses Modul, weitere automatisch andere (falls Rotation aktiv)"
                )
                settings["selected_module_id"] = module_options.get(selected_module_name)
            else:
                st.warning("Keine PV-Module in der Produktdatenbank gefunden.")
                settings["selected_module_id"] = None
        
        # Wechselrichter auswählen
        with prod_cols[1]:
            if products.get("inverter"):
                inverter_options = {p["model_name"]: p["id"] for p in products["inverter"]}
                default_inverter = settings.get("selected_inverter_id")
                default_inverter_index = (
                    list(inverter_options.values()).index(default_inverter)
                    if default_inverter in inverter_options.values()
                    else 0
                )
                selected_inverter_name = st.selectbox(
                    "⚡ Wechselrichter (Basis)",
                    options=list(inverter_options.keys()),
                    index=default_inverter_index,
                    help="Erste Firma erhält diesen Wechselrichter, weitere automatisch andere (falls Rotation aktiv)"
                )
                settings["selected_inverter_id"] = inverter_options.get(selected_inverter_name)
            else:
                st.warning("Keine Wechselrichter in der Produktdatenbank gefunden.")
                settings["selected_inverter_id"] = None
        
        # Batteriespeicher auswählen (wenn aktiviert)
        with prod_cols[2]:
            if settings["include_storage"] and products.get("storage"):
                storage_options = {p["model_name"]: p["id"] for p in products["storage"]}
                default_storage = settings.get("selected_storage_id")
                default_storage_index = (
                    list(storage_options.values()).index(default_storage)
                    if default_storage in storage_options.values()
                    else 0
                )
                selected_storage_name = st.selectbox(
                    "🔋 Batteriespeicher (Basis)",
                    options=list(storage_options.keys()),
                    index=default_storage_index,
                    help="Erste Firma erhält diesen Speicher, weitere automatisch andere (falls Rotation aktiv)"
                )
                settings["selected_storage_id"] = storage_options.get(selected_storage_name)
            elif settings["include_storage"]:
                st.warning("Keine Batteriespeicher gefunden.")
                settings["selected_storage_id"] = None
            else:
                settings["selected_storage_id"] = None
                st.info("Batteriespeicher nicht im Angebot enthalten.")
        
        st.markdown("---")
        
        # NEUE FEATURE: Template-Auswahl wie bei Einzel-PDF
        st.markdown("### 🎨 Vorlagen & Design-Auswahl")
        
        # Template-Optionen initialisieren falls nicht vorhanden
        if "template_options" not in settings:
            settings["template_options"] = {
                "selected_title_image_b64": None,
                "selected_offer_title_text": "Ihr individuelles Solaranlagen-Angebot",
                "selected_cover_letter_text": "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse an nachhaltiger Solarenergie."
            }
        
        template_options = settings["template_options"]
        
        # Template-Auswahl in 3 Spalten (wie in doc_output.py)
        with st.expander("🎨 Vorlagen für alle Angebote auswählen", expanded=False):
            try:
                from database import load_admin_setting
                title_image_templates = load_admin_setting('pdf_title_image_templates', [])
                offer_title_templates = load_admin_setting('pdf_offer_title_templates', [])
                cover_letter_templates = load_admin_setting('pdf_cover_letter_templates', [])
                
                if not isinstance(title_image_templates, list): title_image_templates = []
                if not isinstance(offer_title_templates, list): offer_title_templates = []
                if not isinstance(cover_letter_templates, list): cover_letter_templates = []
                
                template_cols = st.columns(3)
                
                with template_cols[0]:
                    st.markdown("**📷 Titelbild auswählen:**")
                    title_image_options = {t.get('name', f"Bild {i+1}"): t.get('data') for i, t in enumerate(title_image_templates) if isinstance(t,dict) and t.get('name')}
                    if not title_image_options: 
                        title_image_options = {"Kein Titelbild verfügbar": None}
                    
                    # Aktuellen Index finden
                    current_title_name = next((name for name, data in title_image_options.items() if data == template_options.get("selected_title_image_b64")), list(title_image_options.keys())[0])
                    current_title_index = list(title_image_options.keys()).index(current_title_name) if current_title_name in title_image_options else 0
                    
                    selected_title_image_name = st.selectbox(
                        "Titelbild für alle PDFs:", 
                        options=list(title_image_options.keys()),
                        index=current_title_index,
                        key="multi_title_image_select",
                        help="Dieses Titelbild wird in allen generierten PDFs verwendet"
                    )
                    template_options["selected_title_image_b64"] = title_image_options.get(selected_title_image_name)
                
                with template_cols[1]:
                    st.markdown("**📝 Angebotstitel auswählen:**")
                    offer_title_options = {t.get('name', f"Titel {i+1}"): t.get('content') for i, t in enumerate(offer_title_templates) if isinstance(t,dict) and t.get('name')}
                    if not offer_title_options: 
                        offer_title_options = {"Standard Titel": "Ihr individuelles Solaranlagen-Angebot"}
                    
                    # Aktuellen Index finden
                    current_title_text = template_options.get("selected_offer_title_text", "")
                    current_offer_name = next((name for name, content in offer_title_options.items() if content == current_title_text), list(offer_title_options.keys())[0])
                    current_offer_index = list(offer_title_options.keys()).index(current_offer_name) if current_offer_name in offer_title_options else 0
                    
                    selected_offer_title_name = st.selectbox(
                        "Angebotstitel für alle PDFs:", 
                        options=list(offer_title_options.keys()),
                        index=current_offer_index,
                        key="multi_offer_title_select",
                        help="Dieser Titel wird in allen generierten PDFs verwendet"
                    )
                    template_options["selected_offer_title_text"] = offer_title_options.get(selected_offer_title_name, "")
                    
                    # Vorschau des Titels anzeigen
                    if template_options["selected_offer_title_text"]:
                        st.text_area("Titel-Vorschau:", value=template_options["selected_offer_title_text"], height=60, disabled=True)
                
                with template_cols[2]:
                    st.markdown("**📄 Anschreiben auswählen:**")
                    cover_letter_options = {t.get('name', f"Anschreiben {i+1}"): t.get('content') for i, t in enumerate(cover_letter_templates) if isinstance(t,dict) and t.get('name')}
                    if not cover_letter_options: 
                        cover_letter_options = {"Standard Anschreiben": "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse an nachhaltiger Solarenergie."}
                    
                    # Aktuellen Index finden
                    current_letter_text = template_options.get("selected_cover_letter_text", "")
                    current_letter_name = next((name for name, content in cover_letter_options.items() if content == current_letter_text), list(cover_letter_options.keys())[0])
                    current_letter_index = list(cover_letter_options.keys()).index(current_letter_name) if current_letter_name in cover_letter_options else 0
                    
                    selected_cover_letter_name = st.selectbox(
                        "Anschreiben für alle PDFs:", 
                        options=list(cover_letter_options.keys()),
                        index=current_letter_index,
                        key="multi_cover_letter_select",
                        help="Dieses Anschreiben wird in allen generierten PDFs verwendet"
                    )
                    template_options["selected_cover_letter_text"] = cover_letter_options.get(selected_cover_letter_name, "")
                    
                    # Vorschau des Anschreibens anzeigen
                    if template_options["selected_cover_letter_text"]:
                        st.text_area("Anschreiben-Vorschau:", value=template_options["selected_cover_letter_text"][:200] + "..." if len(template_options["selected_cover_letter_text"]) > 200 else template_options["selected_cover_letter_text"], height=100, disabled=True)
                
                # Status-Anzeige für Template-Auswahl
                st.info(f"✅ Templates ausgewählt: Titelbild ({'✓' if template_options['selected_title_image_b64'] else '✗'}), Titel ({'✓' if template_options['selected_offer_title_text'] else '✗'}), Anschreiben ({'✓' if template_options['selected_cover_letter_text'] else '✗'})")
                        
            except Exception as e:
                st.warning(f"Template-Laden fehlgeschlagen: {e}")
                # Fallback-Werte setzen
                template_options["selected_title_image_b64"] = None
                template_options["selected_offer_title_text"] = "Ihr individuelles Solaranlagen-Angebot"
                template_options["selected_cover_letter_text"] = "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse an nachhaltiger Solarenergie."
        
        st.markdown("---")
        
        # NEUE FEATURE: Erweiterte PDF-Optionen wie bei Einzel-PDF
        st.markdown("### 🎨 PDF-Darstellungsoptionen")
        
        # PDF-Optionen initialisieren falls nicht vorhanden
        if "pdf_options" not in settings:
            settings["pdf_options"] = {
                "include_company_logo": True,
                "include_product_images": True,
                "include_charts": True,
                "include_visualizations": True,
                "include_all_documents": True,
                "include_optional_component_details": True,
                "selected_sections": [
                    "ProjectOverview", "TechnicalComponents", "CostDetails", 
                    "Economics", "SimulationDetails", "CO2Savings", 
                    "Visualizations", "FutureAspects"
                ]
            }
        
        pdf_options = settings["pdf_options"]
        
        # PDF-Optionen in 3 Spalten
        pdf_cols = st.columns(3)
        
        with pdf_cols[0]:
            st.markdown("**🏢 Branding & Layout**")
            pdf_options["include_company_logo"] = st.checkbox(
                "Firmenlogo anzeigen",
                value=pdf_options.get("include_company_logo", True),
                help="Logo der jeweiligen Firma im PDF anzeigen"
            )
            pdf_options["include_product_images"] = st.checkbox(
                "Produktbilder anzeigen",
                value=pdf_options.get("include_product_images", True),
                help="Bilder der Produkte im PDF anzeigen"
            )
            pdf_options["include_all_documents"] = st.checkbox(
                "Produktdatenblätter anhängen",
                value=pdf_options.get("include_all_documents", True),
                help="Produktdatenblätter und Firmendokumente als Anhang"
            )
        
        with pdf_cols[1]:
            st.markdown("**📊 Diagramme & Visualisierungen**")
            pdf_options["include_charts"] = st.checkbox(
                "Wirtschaftlichkeits-Diagramme",
                value=pdf_options.get("include_charts", True),
                help="Kostenprojektionen, ROI-Diagramme etc."
            )
            pdf_options["include_visualizations"] = st.checkbox(
                "Technische Visualisierungen",
                value=pdf_options.get("include_visualizations", True),
                help="Produktionsdiagramme, Verbrauchsanalysen etc."
            )
            pdf_options["include_optional_component_details"] = st.checkbox(
                "Details zu Zusatzkomponenten",
                value=pdf_options.get("include_optional_component_details", True),
                help="Wallbox, EMS, Optimierer etc."
            )
        
        with pdf_cols[2]:
            st.markdown("**📋 Inhalts-Sektionen**")
            available_sections = {
                "ProjectOverview": "1. Projektübersicht",
                "TechnicalComponents": "2. Systemkomponenten", 
                "CostDetails": "3. Kostenaufstellung",
                "Economics": "4. Wirtschaftlichkeit",
                "SimulationDetails": "5. Simulation",
                "CO2Savings": "6. CO₂-Einsparung",
                "Visualizations": "7. Grafiken",
                "FutureAspects": "8. Zukunftsaspekte"
            }
            
            # Multi-Select für Sektionen
            selected_sections = st.multiselect(
                "Sektionen auswählen",
                options=list(available_sections.keys()),
                default=pdf_options.get("selected_sections", list(available_sections.keys())),
                format_func=lambda x: available_sections[x]
            )
            pdf_options["selected_sections"] = selected_sections
            
            if len(selected_sections) == 0:
                st.warning("⚠️ Mindestens eine Sektion muss ausgewählt sein!")
            else:
                st.success(f"✅ {len(selected_sections)} Sektionen ausgewählt")
        
        return True

    def generate_multi_offers(self):
        """Generiert PDFs für alle ausgewählten Firmen"""
        st.subheader("Schritt 4: PDF-Angebote generieren")
        
        customer_data = st.session_state.multi_offer_customer_data
        selected_companies = st.session_state.multi_offer_selected_companies
        settings = st.session_state.multi_offer_settings
        project_data = st.session_state.get("multi_offer_project_data", {})
        
        if not customer_data or not selected_companies:
            st.error("Kundendaten oder Firmenauswahl fehlt!")
            return
        
        if st.button("🎯 Angebote für alle Firmen erstellen", type="primary"):
            
            try:
                # Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                generated_pdfs = []
                total_companies = len(selected_companies)
                
                for i, company_id in enumerate(selected_companies):
                    company_name = f"Firma_{company_id}"  # Fallback-Name sofort setzen
                    try:
                        # Company-Daten laden
                        company = get_company(company_id) if callable(get_company) else {}
                        company_name = company.get("name", f"Firma_{company_id}")  # Überschreibe mit echtem Namen
                        
                        status_text.text(f"Erstelle Angebot für {company_name} (Firma {i+1}/{total_companies})...")
                        
                        # NEUE FEATURE: Produktrotation für diese Firma
                        company_settings = self.get_rotated_products_for_company(i, settings)
                          # PDF-Generierung vorbereiten mit firmenspezifischen Produkten
                        offer_data = self._prepare_offer_data(customer_data, company, company_settings, project_data, i)
                        
                        # PDF generieren mit company_index für Preisstaffelung
                        pdf_content = self._generate_company_pdf(offer_data, company, i)
                        
                        if pdf_content:
                            generated_pdfs.append({
                                "company_name": company_name,
                                "pdf_content": pdf_content,
                                "filename": f"Angebot_{company_name}_{customer_data.get('last_name', 'Kunde')}.pdf"
                            })
                            st.success(f"✅ PDF für {company_name} erstellt")
                        else:
                            st.error(f"❌ PDF für {company_name} konnte nicht erstellt werden")                        # Fortschritt aktualisieren
                        progress_bar.progress((i + 1) / total_companies)
                        
                    except Exception as e:
                        # Sichere Verwendung von company_name - falls nicht definiert, Fallback verwenden
                        safe_company_name = locals().get('company_name', f"Firma_{company_id}")
                        st.error(f"Fehler bei {safe_company_name}: {str(e)}")
                        logging.error(f"Fehler bei PDF-Generierung für {safe_company_name}: {e}")
                        logging.error(f"Exception Typ: {type(e).__name__}")
                        logging.error(f"Verfügbare lokale Variablen: {list(locals().keys())}")
                        # Ausführlichere Fehlerbehandlung für company_name Probleme
                        if "company_name" in str(e):
                            logging.error(f"COMPANY_NAME DEBUG: company_id={company_id}, locals company_name: {locals().get('company_name', 'NOT_FOUND')}")
                        continue  # Weiter mit der nächsten Firma
                
                # ZIP-Download erstellen
                if generated_pdfs:
                    zip_content = self._create_zip_download(generated_pdfs)
                    
                    st.success(f"🎉 {len(generated_pdfs)} Angebote erfolgreich erstellt!")
                    st.download_button(
                        label="📦 Alle Angebote als ZIP herunterladen",
                        data=zip_content,
                        file_name=f"Multi_Angebote_{customer_data.get('last_name', 'Kunde')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("Keine PDFs konnten erstellt werden!")
                
                status_text.text("Fertig!")
                
            except Exception as e:
                st.error(f"Fehler bei der PDF-Generierung: {str(e)}")
                logging.error(f"Fehler in generate_multi_offers: {e}")

    def get_rotated_products_for_company(self, company_index: int, base_settings: Dict) -> Dict:
        """
        Vollständig flexible Produktrotation für verschiedene Firmen
        company_index: 0 = erste Firma, 1 = zweite Firma, etc.
        Unterstützt: Lineare Rotation, Zufällige Auswahl, Kategorie-spezifische Schritte
        """
        rotated_settings = base_settings.copy()
        
        if not base_settings.get("enable_product_rotation", True):
            return rotated_settings
        
        try:
            rotation_mode = base_settings.get("rotation_mode", "linear")
            
            # Kategorien mit individuellen Rotation-Schritten
            categories = ["module", "inverter", "storage"]
            
            for category in categories:
                base_id_key = f"selected_{category}_id"
                base_id = base_settings.get(base_id_key)
                
                if not base_id or category not in self.products:
                    continue
                
                available_products = self.products[category]
                if len(available_products) <= 1:
                    # Nur ein Produkt verfügbar - behalte das Original
                    logging.info(f"Produktrotation {category}: Nur 1 Produkt verfügbar, behalte Original")
                    continue
                
                # Finde Index des Basisprodukts
                base_index = -1
                for i, product in enumerate(available_products):
                    if product.get("id") == base_id:
                        base_index = i
                        break
                
                if base_index == -1:
                    logging.warning(f"Produktrotation {category}: Basisprodukt nicht gefunden")
                    continue
                
                # Bestimme Rotation-Schritt basierend auf Modus
                if rotation_mode == "kategorie-spezifisch":
                    rotation_step = base_settings.get(f"{category}_rotation_step", 1)
                elif rotation_mode == "zufällig":
                    import random
                    rotation_step = random.randint(1, len(available_products) - 1)
                else:  # linear
                    rotation_step = base_settings.get("product_rotation_step", 1)
                
                # Berechne neuen Index mit flexiblem Schritt
                new_index = (base_index + (company_index * rotation_step)) % len(available_products)
                rotated_product = available_products[new_index]
                rotated_settings[base_id_key] = rotated_product.get("id")
                
                logging.info(f"Produktrotation {category}: Firma {company_index+1} -> {rotated_product.get('model_name', 'Unknown')} (Schritt: {rotation_step}, Verfügbare: {len(available_products)})")
        
        except Exception as e:
            logging.warning(f"Fehler bei Produktrotation: {e}")
        
        return rotated_settings

    def apply_price_scaling(self, company_index: int, base_settings: Dict, calc_results: Dict) -> Dict:
        """
        Vollständig flexible Preisstaffelung für verschiedene Firmen
        Unterstützt: Linear, Exponentiell, Custom-Faktoren
        company_index: 0 = erste Firma, 1 = zweite Firma, etc.
        """
        if company_index == 0:
            return calc_results  # Erste Firma behält Originalpreis
        
        price_increment = base_settings.get("price_increment_percent", 0)
        if price_increment == 0:
            return calc_results  # Keine Preissteigerung
        
        scaled_results = calc_results.copy()
        
        try:
            # Bestimme Preisfaktor basierend auf Berechnungsmodus
            calc_mode = base_settings.get("price_calculation_mode", "linear")
            
            if calc_mode == "linear":
                price_factor = 1.0 + (company_index * price_increment / 100.0)
            elif calc_mode == "exponentiell":
                exponent = base_settings.get("price_exponent", 1.03)
                price_factor = exponent ** company_index
            elif calc_mode == "custom":
                try:
                    import json
                    custom_factors = json.loads(base_settings.get("custom_price_factors", "[1.0]"))
                    price_factor = custom_factors[company_index] if company_index < len(custom_factors) else custom_factors[-1]
                except:
                    # Fallback auf linear
                    price_factor = 1.0 + (company_index * price_increment / 100.0)
            else:
                price_factor = 1.0
            
            logging.info(f"Preisstaffelung: Firma {company_index+1}, Modus: {calc_mode}, Faktor: {price_factor:.3f}")
            
            # Preisbezogene Felder skalieren
            price_fields = [
                'total_investment_netto',
                'total_investment_brutto', 
                'module_cost_total',
                'inverter_cost_total',
                'storage_cost_total',
                'additional_costs',
                'installation_cost',
                'total_cost_euro',
                'wallbox_cost',
                'ems_cost',
                'optimizer_cost',
                'carport_cost',
                'notstrom_cost',
                'tierabwehr_cost'
            ]
            
            for field in price_fields:
                if field in scaled_results and isinstance(scaled_results[field], (int, float)):
                    original_value = scaled_results[field]
                    scaled_results[field] = original_value * price_factor
                    
            # Wirtschaftlichkeitsberechnungen intelligent anpassen
            if 'amortization_time_years' in scaled_results and isinstance(scaled_results['amortization_time_years'], (int, float)):
                # Längere Amortisationszeit durch höhere Kosten (aber begrenzt)
                amort_factor = min(price_factor, 1.5)  # Maximal 50% längere Amortisation
                scaled_results['amortization_time_years'] = scaled_results['amortization_time_years'] * amort_factor
            
            # ROI anpassen (niedriger durch höhere Investition)
            roi_fields = ['roi_percent_year1', 'roi_percent_year10', 'roi_percent_year20']
            for roi_field in roi_fields:
                if roi_field in scaled_results and isinstance(scaled_results[roi_field], (int, float)):
                    scaled_results[roi_field] = scaled_results[roi_field] / price_factor
              # Jährliche Ersparnisse bleiben gleich (da gleiche Anlage, nur teurer)
            # annual_savings bleibt unverändert
                
        except Exception as e:
            logging.warning(f"Fehler bei Preisstaffelung für Firma {company_index+1}: {e}")
        
        return scaled_results

    def _prepare_offer_data(self, customer_data: Dict, company: Dict, settings: Dict, project_data: Dict, company_index: int = 0) -> Dict:
        """Bereitet die Angebotsdaten für PDF-Generierung vor"""
        # Basis-Angebotsdaten
        offer_data = {
            "customer_data": customer_data,
            "company_data": company,
            "offer_date": datetime.now().strftime("%d.%m.%Y"),
            "module_quantity": settings.get("module_quantity", 20),
            "include_storage": settings.get("include_storage", True),
        }
        
        # Projektdaten hinzufügen
        if project_data:
            offer_data["project_data"] = project_data
            
            # Verbrauchsdaten
            if project_data.get("consumption_data"):
                offer_data["consumption_data"] = project_data["consumption_data"]
            
            # Berechnungen
            if project_data.get("calculation_results"):
                offer_data["calculation_results"] = project_data["calculation_results"]        # KRITISCH: Produktdetails für PDF-Generierung vorbereiten
        # Die PDF-Generierung erwartet diese Daten in "project_details"
        project_details = {
            "module_quantity": settings.get("module_quantity", 20),
            "include_storage": settings.get("include_storage", True),
            "include_additional_components": True,  # Zusatzkomponenten aktivieren
        }
        
        # Fallback: Verwende Produktauswahl aus project_data falls verfügbar
        existing_project_details = project_data.get("project_details", {}) if project_data else {}
        
        # Produktdaten hinzufügen
        try:
            # Modul
            module_id = settings.get("selected_module_id") or existing_project_details.get("selected_module_id")
            if module_id:
                offer_data["selected_module"] = get_product_by_id(module_id)
                project_details["selected_module_id"] = module_id
            
            # Wechselrichter
            inverter_id = settings.get("selected_inverter_id") or existing_project_details.get("selected_inverter_id")
            if inverter_id:
                offer_data["selected_inverter"] = get_product_by_id(inverter_id)
                project_details["selected_inverter_id"] = inverter_id
            
            # Speicher
            storage_id = settings.get("selected_storage_id") or existing_project_details.get("selected_storage_id")
            if storage_id:
                offer_data["selected_storage"] = get_product_by_id(storage_id)
                project_details["selected_storage_id"] = storage_id
                  # Speicher-spezifische Details
                storage_product = get_product_by_id(storage_id)
                if storage_product:
                    project_details["selected_storage_storage_power_kw"] = storage_product.get("storage_power_kw", 0)
            
            # Zusatzkomponenten (Wallbox, EMS, etc.) aus Projektdaten übertragen
            additional_components = [
                'selected_wallbox_id',
                'selected_ems_id', 
                'selected_optimizer_id',
                'selected_carport_id',
                'selected_notstrom_id',
                'selected_tierabwehr_id'
            ]
            
            for comp_key in additional_components:
                comp_id = existing_project_details.get(comp_key)
                if comp_id:
                    project_details[comp_key] = comp_id
                    # Produktdaten auch zu offer_data hinzufügen für Vollständigkeit
                    comp_product = get_product_by_id(comp_id)
                    if comp_product:
                        offer_data[comp_key.replace('_id', '')] = comp_product
            
            # Weitere wichtige Felder aus existing_project_details übernehmen
            if existing_project_details:
                # Übernehme Modulanzahl falls nicht in settings
                if "module_quantity" not in settings and "module_quantity" in existing_project_details:
                    project_details["module_quantity"] = existing_project_details["module_quantity"]
                    offer_data["module_quantity"] = existing_project_details["module_quantity"]
                
                # Übernehme Speicher-Einstellung falls nicht in settings
                if "include_storage" not in settings and "include_storage" in existing_project_details:
                    project_details["include_storage"] = existing_project_details["include_storage"]
                    offer_data["include_storage"] = existing_project_details["include_storage"]
                
                # Übernehme zusätzliche Komponenten-Einstellungen
                for field in ["include_additional_components", "visualize_roof_in_pdf_satellite", "satellite_image_base64_data"]:
                    if field in existing_project_details:
                        project_details[field] = existing_project_details[field]
        except Exception as e:
            logging.warning(f"Produktdaten konnten nicht geladen werden: {e}")
        
        # Project_details zu offer_data hinzufügen (KRITISCH für PDF-Generierung)
        offer_data["project_details"] = project_details
        
        return offer_data

    def _generate_company_pdf(self, offer_data: Dict, company: Dict, company_index: int = 0) -> bytes:
        """Generiert PDF für eine spezifische Firma mit firmenspezifischen Produkten und Preisen"""
        try:
            # PDF-Generierung über generate_offer_pdf mit allen 16 erforderlichen Parametern
            if callable(generate_offer_pdf):
                  # Vorbereitung der Berechnungsergebnisse - ECHTE DATEN verwenden!
                calc_results = st.session_state.get('calculation_results', {})
                
                # Fallback: Multi-Offer spezifische Berechnungen
                if not calc_results:
                    calc_results = st.session_state.get('multi_offer_calc_results', {})
                
                # Als letzter Fallback Mock-Daten, aber mit Warnung
                if not calc_results:
                    logging.warning("Keine echten Berechnungsergebnisse verfügbar - verwende Mock-Daten")
                    calc_results = {
                        'anlage_kwp': offer_data.get('module_quantity', 20) * 0.4,  # Geschätzt
                        'annual_pv_production_kwh': offer_data.get('module_quantity', 20) * 400,
                        'total_investment_netto': offer_data.get('module_quantity', 20) * 750,
                        'amortization_time_years': 12.5,
                        'self_supply_rate_percent': 65.0,
                        'annual_financial_benefit_year1': 1200
                    }
                else:
                    logging.info(f"Verwende echte Berechnungsergebnisse mit {len(calc_results)} Feldern")

                # NEUE FEATURE: Preisstaffelung anwenden
                base_settings = st.session_state.get("multi_offer_settings", {})
                calc_results = self.apply_price_scaling(company_index, base_settings, calc_results)
                
                logging.info(f"PDF-Generierung für Firma {company_index+1}: Preise angepasst")# KRITISCH: PDF-kompatible Datenstruktur erstellen
                # Die PDF-Funktion erwartet project_data mit customer_data und project_details
                pdf_project_data = {
                    "customer_data": offer_data.get("customer_data", {}),
                    "project_details": offer_data.get("project_details", {}),
                    # Weitere Felder aus offer_data übernehmen
                    "consumption_data": offer_data.get("consumption_data", {}),
                    "calculation_results": offer_data.get("calculation_results", {})
                }
                  # Falls ursprüngliche project_data vorhanden, deren Struktur beibehalten
                if "project_data" in offer_data and offer_data["project_data"]:
                    original_project_data = offer_data["project_data"]
                    # Wichtige Felder aus original_project_data übernehmen
                    for key in ["address", "roof_data", "location_data", "technical_specs"]:
                        if key in original_project_data:
                            pdf_project_data[key] = original_project_data[key]
                  # DEBUG: Ausgabe der PDF-Datenstruktur
                logging.info(f"Multi-Offer PDF Datenstruktur:")
                logging.info(f"  project_details keys: {list(pdf_project_data.get('project_details', {}).keys())}")
                logging.info(f"  selected_module_id: {pdf_project_data.get('project_details', {}).get('selected_module_id', 'NICHT GESETZT')}")
                logging.info(f"  selected_inverter_id: {pdf_project_data.get('project_details', {}).get('selected_inverter_id', 'NICHT GESETZT')}")
                logging.info(f"  selected_storage_id: {pdf_project_data.get('project_details', {}).get('selected_storage_id', 'NICHT GESETZT')}")
                  # KRITISCH: Verfügbare Charts aus analysis_results extrahieren
                available_charts = []
                if calc_results and isinstance(calc_results, dict):
                    # Chart-Keys aus analysis_results finden
                    chart_keys = [k for k in calc_results.keys() if k.endswith('_chart_bytes') and calc_results[k] is not None]
                    available_charts = chart_keys
                    logging.info(f"Multi-Offer PDF: {len(available_charts)} Charts gefunden: {chart_keys}")
                
                # PDF-Templates aus Admin-Einstellungen laden
                try:
                    # Templates laden (falls verfügbar)
                    title_image_templates = load_admin_setting("pdf_title_image_templates", []) if callable(load_admin_setting) else []
                    offer_title_templates = load_admin_setting("pdf_offer_title_templates", []) if callable(load_admin_setting) else []
                    cover_letter_templates = load_admin_setting("pdf_cover_letter_templates", []) if callable(load_admin_setting) else []
                    
                    # Erstes verfügbares Template verwenden
                    selected_title_image = title_image_templates[0] if title_image_templates else None
                    selected_offer_title = offer_title_templates[0] if offer_title_templates else None
                    selected_cover_letter = cover_letter_templates[0] if cover_letter_templates else None
                    
                    logging.info(f"Templates geladen: Titelbild={bool(selected_title_image)}, Titel={bool(selected_offer_title)}, Anschreiben={bool(selected_cover_letter)}")
                except Exception as e:
                    logging.warning(f"Fehler beim Laden der Templates: {e}")
                    selected_title_image = selected_offer_title = selected_cover_letter = None
                  # NEUE FEATURE: Benutzerdefinierten PDF-Optionen aus Einstellungen verwenden
                base_settings = st.session_state.get("multi_offer_settings", {})
                pdf_options = base_settings.get("pdf_options", {})
                
                # Sektionen aus Benutzereinstellungen
                selected_sections = pdf_options.get("selected_sections", [
                    "ProjectOverview", "TechnicalComponents", "CostDetails",
                    "Economics", "SimulationDetails", "CO2Savings", 
                    "Visualizations", "FutureAspects"
                ])
                
                # Charts basierend auf Benutzereinstellungen filtern
                charts_to_include = available_charts if pdf_options.get("include_charts", True) else []
                if not pdf_options.get("include_visualizations", True):
                    # Technische Visualisierungen entfernen
                    charts_to_include = [c for c in charts_to_include if not any(
                        vis_key in c for vis_key in ['daily_production', 'weekly_production', 'yearly_production']
                    )]
                
                # Erstelle section_order_df aus selected_sections
                import pandas as pd
                section_order_df = pd.DataFrame({
                    "Aktiv": [True] * len(selected_sections),
                    "Sektion": selected_sections
                })
                
                # NEUE FEATURE: Template-Parameter aus Benutzereinstellungen verwenden
                template_options = base_settings.get("template_options", {})
                
                pdf_content = generate_offer_pdf(
                    project_data=pdf_project_data,  # Korrekt strukturierte Daten
                    analysis_results=calc_results,
                    company_info=company,
                    company_logo_base64=company.get('logo_base64'),  # Firmen-spezifisches Logo
                    selected_title_image_b64=template_options.get("selected_title_image_b64"),  # Template-Titelbild
                    selected_offer_title_text=template_options.get("selected_offer_title_text", f"Ihr individuelles Solaranlagen-Angebot von {company.get('name', 'Unser Unternehmen')}"),  # Template-Titel
                    selected_cover_letter_text=template_options.get("selected_cover_letter_text", "Sehr geehrte Damen und Herren,\n\nvielen Dank für Ihr Interesse an nachhaltiger Solarenergie."),  # Template-Anschreiben
                    sections_to_include=selected_sections,  # Benutzer-definierte Sektionen
                    inclusion_options={
                        "include_company_logo": pdf_options.get("include_company_logo", True),
                        "include_product_images": pdf_options.get("include_product_images", True),
                        "include_all_documents": pdf_options.get("include_all_documents", True),
                        "company_document_ids_to_include": [],  # TODO: Firmen-spezifische Dokumente
                        "selected_charts_for_pdf": charts_to_include,
                        "include_optional_component_details": pdf_options.get("include_optional_component_details", True),
                        "include_custom_footer": True,  # Standard Footer
                        "include_header_logo": True,  # Header Logo
                    },
                    load_admin_setting_func=load_admin_setting if callable(load_admin_setting) else lambda k, d: d,
                    save_admin_setting_func=save_admin_setting if callable(save_admin_setting) else lambda k, v: True,
                    list_products_func=list_products if callable(list_products) else lambda: [],
                    get_product_by_id_func=get_product_by_id if callable(get_product_by_id) else lambda x: {},
                    db_list_company_documents_func=list_company_documents if callable(list_company_documents) else lambda cid, dtype=None: [],
                    active_company_id=company.get("id", 1),
                    texts=st.session_state.get("TEXTS", {})
                )
                return pdf_content
            else:
                st.error("PDF-Generator nicht verfügbar")
                return None
                
        except Exception as e:
            logging.error(f"Fehler bei PDF-Generierung: {e}")
            st.error(f"PDF-Generierung fehlgeschlagen: {str(e)}")
            return None

    def _create_zip_download(self, generated_pdfs: List[Dict]) -> bytes:
        """Erstellt ZIP-Datei mit allen PDFs"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for pdf_info in generated_pdfs:
                zip_file.writestr(
                    pdf_info["filename"],
                    pdf_info["pdf_content"]
                )
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def render_ui(self):
        """Hauptfunktion für die UI-Darstellung"""
        st.title("🏢 Multi-Firmen-Angebotsgenerator")
        st.markdown("Erstellen Sie Angebote für mehrere Firmen basierend auf Ihren Projektdaten.")
        
        self.initialize_session_state()
        
        # Schritt 1: Kundendaten
        customer_data_ready = self.render_customer_input()
        
        if customer_data_ready:
            # Schritt 2: Firmenauswahl
            companies_selected = self.render_company_selection()
            
            if companies_selected:
                # Schritt 3: Konfiguration
                config_ready = self.render_offer_configuration()
                
                if config_ready:
                    # Schritt 4: PDF-Generierung
                    self.generate_multi_offers()


# Hauptfunktion für Streamlit
def render_multi_offer_generator(texts, project_data_doc=None, calc_results_doc=None):
    """
    Hauptfunktion für den Multi-Firmen-Angebotsgenerator
    Wird vom GUI-Modul aufgerufen
    """
    st.header("🏢 Multi-Firmen-Angebotsgenerator")
    st.markdown("Erstellen Sie Angebote für mehrere Firmen basierend auf Ihren Projektdaten.")
    
    # Generator initialisieren
    if "mog_generator" not in st.session_state:
        st.session_state.mog_generator = MultiCompanyOfferGenerator()
    
    generator = st.session_state.mog_generator
    generator.initialize_session_state()
    
    # Texte für das System setzen
    st.session_state["TEXTS"] = texts
    
    # Projektdaten übernehmen falls vorhanden
    if project_data_doc and "customer_data" in project_data_doc:
        if not st.session_state.multi_offer_customer_data.get("last_name"):
            st.session_state.multi_offer_customer_data = project_data_doc["customer_data"]
            st.session_state.multi_offer_project_data = project_data_doc
    
    # Berechungsergebnisse übernehmen falls vorhanden
    if calc_results_doc:
        st.session_state.multi_offer_calc_results = calc_results_doc
    
    # UI rendern
    try:
        # Schritt 1: Kundendaten
        customer_data_ready = generator.render_customer_input()
        
        if customer_data_ready:
            st.markdown("---")
            # Schritt 2: Firmenauswahl
            companies_selected = generator.render_company_selection()
            
            if companies_selected:
                st.markdown("---")                # Schritt 3: Konfiguration
                config_ready = generator.render_offer_configuration()
                
                if config_ready:
                    st.markdown("---")
                    # Schritt 4: PDF-Generierung
                    generator.generate_multi_offers()
        
    except Exception as e:
        st.error(f"Fehler im Multi-Angebotsgenerator: {str(e)}")
        logging.error(f"Fehler in render_multi_offer_generator: {e}")
        logging.error(f"Exception Typ: {type(e).__name__}")
        logging.error(f"Exception Details: {repr(e)}")
        # Zusätzliche Debug-Info für company_name Fehler
        if "company_name" in str(e) and "not associated with a value" in str(e):
            logging.error("COMPANY_NAME DEBUG: Dies ist der spezifische company_name Fehler")
            logging.error(f"Traceback Details verfügbar in den Logs")
        st.info("Bitte versuchen Sie es erneut oder wenden Sie sich an den Support.")


def main():
    """Hauptfunktion für den Multi-Angebotsgenerator"""
    generator = MultiCompanyOfferGenerator()
    generator.render_ui()


if __name__ == "__main__":
    main()
