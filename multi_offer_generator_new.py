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
from typing import Dict, List, Any
import traceback

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
        self.products = self.load_all_products()

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

    def load_all_products(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lädt alle Produkte und kategorisiert sie."""
        try:
            all_products = list_products() if callable(list_products) else []
            categorized = {"module": [], "inverter": [], "storage": []}
            for p in all_products:
                cat = p.get("category", "Sonstiges").lower()
                if "modul" in cat:
                    categorized["module"].append(p)
                elif "wechselrichter" in cat:
                    categorized["inverter"].append(p)
                elif "speicher" in cat or "battery" in cat:
                    categorized["storage"].append(p)
            return categorized
        except Exception as e:
            st.warning(f"Konnte Produkte nicht laden: {e}")
            return {"module": [], "inverter": [], "storage": []}

    def get_available_companies(self) -> List[Dict[str, Any]]:
        """Lädt verfügbare Firmen"""
        try:
            return list_companies() if callable(list_companies) else []
        except Exception as e:
            st.warning(f"Konnte Firmen nicht laden: {e}")
            return []

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
        """Schritt 2: Firmenauswahl"""
        st.subheader("Schritt 2: Firmen für Angebote auswählen")
        
        all_companies = self.get_available_companies()
        if not all_companies:
            st.warning("Keine Firmen in der Datenbank gefunden. Bitte im Admin-Panel anlegen.")
            return False
        
        company_options = {c["name"]: c["id"] for c in all_companies}
        selected_company_names = st.multiselect(
            "Wählen Sie eine oder mehrere Firmen aus:",
            options=list(company_options.keys()),
            default=[
                name
                for name, cid in company_options.items()
                if cid in st.session_state.multi_offer_selected_companies
            ],
        )
        
        st.session_state.multi_offer_selected_companies = [
            company_options[name] for name in selected_company_names
        ]
        
        if st.session_state.multi_offer_selected_companies:
            st.success(f"✅ {len(st.session_state.multi_offer_selected_companies)} Firmen ausgewählt")
            return True
        else:
            st.warning("Bitte mindestens eine Firma auswählen.")
            return False

    def render_offer_configuration(self):
        """Schritt 3: Angebotskonfiguration"""
        st.subheader("Schritt 3: Globale Angebotskonfiguration")
        
        settings = st.session_state.multi_offer_settings
        cols = st.columns(2)
        
        settings["module_quantity"] = cols[0].slider(
            "Anzahl der Module", 5, 100, settings.get("module_quantity", 20)
        )
        settings["include_storage"] = cols[1].checkbox(
            "Batteriespeicher ins Angebot aufnehmen?",
            value=settings.get("include_storage", True),
        )
        
        products = self.products
        
        # PV-Modul auswählen
        if products.get("module"):
            module_options = {p["model_name"]: p["id"] for p in products["module"]}
            default_module = settings.get("selected_module_id")
            default_module_index = (
                list(module_options.values()).index(default_module)
                if default_module in module_options.values()
                else 0
            )
            selected_module_name = st.selectbox(
                "PV-Modul auswählen",
                options=list(module_options.keys()),
                index=default_module_index,
            )
            settings["selected_module_id"] = module_options.get(selected_module_name)
        else:
            st.warning("Keine PV-Module in der Produktdatenbank gefunden.")
            settings["selected_module_id"] = None
        
        # Wechselrichter auswählen
        if products.get("inverter"):
            inverter_options = {p["model_name"]: p["id"] for p in products["inverter"]}
            default_inverter = settings.get("selected_inverter_id")
            default_inverter_index = (
                list(inverter_options.values()).index(default_inverter)
                if default_inverter in inverter_options.values()
                else 0
            )
            selected_inverter_name = st.selectbox(
                "Wechselrichter auswählen",
                options=list(inverter_options.keys()),
                index=default_inverter_index,
            )
            settings["selected_inverter_id"] = inverter_options.get(selected_inverter_name)
        else:
            st.warning("Keine Wechselrichter in der Produktdatenbank gefunden.")
            settings["selected_inverter_id"] = None
        
        # Batteriespeicher auswählen (wenn aktiviert)
        if settings["include_storage"] and products.get("storage"):
            storage_options = {p["model_name"]: p["id"] for p in products["storage"]}
            default_storage = settings.get("selected_storage_id")
            default_storage_index = (
                list(storage_options.values()).index(default_storage)
                if default_storage in storage_options.values()
                else 0
            )
            selected_storage_name = st.selectbox(
                "Batteriespeicher auswählen",
                options=list(storage_options.keys()),
                index=default_storage_index,
            )
            settings["selected_storage_id"] = storage_options.get(selected_storage_name)
        else:
            settings["selected_storage_id"] = None
        
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
                    try:
                        # Company-Daten laden
                        company = get_company(company_id) if callable(get_company) else {}
                        company_name = company.get("name", f"Firma_{company_id}")
                        
                        status_text.text(f"Erstelle Angebot für {company_name}...")
                        
                        # PDF-Generierung vorbereiten
                        offer_data = self._prepare_offer_data(customer_data, company, settings, project_data)
                        
                        # PDF generieren
                        pdf_content = self._generate_company_pdf(offer_data, company)
                        
                        if pdf_content:
                            generated_pdfs.append({
                                "company_name": company_name,
                                "pdf_content": pdf_content,
                                "filename": f"Angebot_{company_name}_{customer_data.get('last_name', 'Kunde')}.pdf"
                            })
                            st.success(f"✅ PDF für {company_name} erstellt")
                        else:
                            st.error(f"❌ PDF für {company_name} konnte nicht erstellt werden")
                        
                        # Fortschritt aktualisieren
                        progress_bar.progress((i + 1) / total_companies)
                        
                    except Exception as e:
                        st.error(f"Fehler bei {company_name}: {str(e)}")
                        logging.error(f"Fehler bei PDF-Generierung für {company_name}: {e}")
                
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

    def _prepare_offer_data(self, customer_data: Dict, company: Dict, settings: Dict, project_data: Dict) -> Dict:
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
                offer_data["calculation_results"] = project_data["calculation_results"]
        
        # Produktdaten hinzufügen
        try:
            if settings.get("selected_module_id"):
                offer_data["selected_module"] = get_product_by_id(settings["selected_module_id"])
            
            if settings.get("selected_inverter_id"):
                offer_data["selected_inverter"] = get_product_by_id(settings["selected_inverter_id"])
            
            if settings.get("selected_storage_id"):
                offer_data["selected_storage"] = get_product_by_id(settings["selected_storage_id"])
        except Exception as e:
            logging.warning(f"Produktdaten konnten nicht geladen werden: {e}")
        
        return offer_data

    def _generate_company_pdf(self, offer_data: Dict, company: Dict) -> bytes:
        """Generiert PDF für eine spezifische Firma"""
        try:
            # PDF-Generierung über generate_offer_pdf
            if callable(generate_offer_pdf):
                pdf_content = generate_offer_pdf(
                    customer_data=offer_data["customer_data"],
                    offer_data=offer_data,
                    company_data=company
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
def main():
    """Hauptfunktion für den Multi-Angebotsgenerator"""
    generator = MultiCompanyOfferGenerator()
    generator.render_ui()


if __name__ == "__main__":
    main()
