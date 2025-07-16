"""
Multi-Firmen-Angebotsgenerator
Erstellt mehrere Angebote für verschiedene Firmen mit einem Klick
"""

import streamlit as st
import os
import zipfile
import io
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sqlite3
import traceback

# Import der bestehenden Module
try:
    from database import get_db_connection, list_companies, get_company
    from pdf_generator import generate_offer_pdf
    from product_db import get_product_by_id
    # from locales import get_text_dict  # Entfernt, da nicht existent
except ImportError as e:
    st.error(f"Import-Fehler: {e}")


class MultiCompanyOfferGenerator:
    """Generator für Multi-Firmen-Angebote"""
    
    def __init__(self):
        self.customer_data = {}
        self.selected_companies = []
        self.offer_settings = {}
        
    def initialize_session_state(self):
        """Initialisiert Session State"""
        if 'multi_offer_customer_data' not in st.session_state:
            st.session_state.multi_offer_customer_data = {}
        if 'multi_offer_selected_companies' not in st.session_state:
            st.session_state.multi_offer_selected_companies = []
        if 'multi_offer_settings' not in st.session_state:
            st.session_state.multi_offer_settings = {}
            
    def get_available_companies(self) -> List[Dict[str, Any]]:
        """Holt verfügbare Firmen aus der Datenbank"""
        try:
            companies = list_companies()
            return companies if companies else []
        except Exception as e:
            st.error(f"Fehler beim Laden der Firmen: {e}")
            return []
            
    def get_company_products(self, company_id: int) -> Dict[str, List[Dict]]:
        """Holt Produkte einer spezifischen Firma"""
        try:
            conn = get_db_connection()
            if not conn:
                return {}
                
            cursor = conn.cursor()
            
            # Produkte nach Kategorie gruppiert laden
            products_by_category = {}
            
            categories = ['modul', 'wechselrichter', 'batteriespeicher', 'wallbox', 
                         'energiemanagementsystem', 'leistungsoptimierer', 'carport',
                         'notstromversorgung', 'tierabwehrschutz']
            
            for category in categories:
                cursor.execute("""
                    SELECT id, brand, model_name, capacity_w, power_kw, 
                           storage_power_kw, price_euro, category
                    FROM products 
                    WHERE company_id = ? AND category = ?
                    ORDER BY brand, model_name
                """, (company_id, category))
                
                products = []
                for row in cursor.fetchall():
                    products.append({
                        'id': row[0],
                        'brand': row[1],
                        'model_name': row[2],
                        'capacity_w': row[3],
                        'power_kw': row[4],
                        'storage_power_kw': row[5],
                        'price_euro': row[6],
                        'category': row[7]
                    })
                
                if products:
                    products_by_category[category] = products
                    
            conn.close()
            return products_by_category
            
        except Exception as e:
            st.error(f"Fehler beim Laden der Produkte für Firma {company_id}: {str(e).replace('price_eurprice_eur', 'price_euro')}")
            return {}
            
    def render_customer_input(self):
        """Rendert Kundendaten-Eingabe"""
        st.subheader("👤 Kundendaten (für alle Angebote gleich)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            salutation = st.selectbox(
                "Anrede", 
                ["Herr", "Frau", "Familie", "Firma", "Divers"],
                key="multi_customer_salutation"
            )
            
            first_name = st.text_input(
                "Vorname", 
                key="multi_customer_first_name"
            )
            
            company_name = st.text_input(
                "Firmenname (optional)", 
                key="multi_customer_company"
            )
            
            address = st.text_input(
                "Straße", 
                key="multi_customer_address"
            )
            
            city = st.text_input(
                "Ort", 
                key="multi_customer_city"
            )
            
        with col2:
            title = st.text_input(
                "Titel (optional)", 
                key="multi_customer_title"
            )
            
            last_name = st.text_input(
                "Nachname", 
                key="multi_customer_last_name"
            )
            
            email = st.text_input(
                "E-Mail", 
                key="multi_customer_email"
            )
            
            house_number = st.text_input(
                "Hausnummer", 
                key="multi_customer_house_number"
            )
            
            zip_code = st.text_input(
                "PLZ", 
                key="multi_customer_zip"
            )
            
        # Kundendaten in Session State speichern
        st.session_state.multi_offer_customer_data = {
            "salutation": salutation,
            "title": title, 
            "first_name": first_name,
            "last_name": last_name,
            "company_name": company_name,
            "email": email,
            "address": address,
            "house_number": house_number,
            "zip_code": zip_code,
            "city": city
        }
        
    def render_company_selection(self):
        """Rendert Firmenauswahl"""
        st.subheader("🏢 Firmenauswahl (verschiedene Angebote)")
        
        companies = self.get_available_companies()
        
        if not companies:
            st.warning("⚠️ Keine Firmen in der Datenbank gefunden!")
            st.info("💡 Gehen Sie zu Admin > Firmenverwaltung, um Firmen hinzuzufügen.")
            return
            
        st.markdown("**Wählen Sie die Firmen aus, für die Angebote erstellt werden sollen:**")
        
        # Company Selection mit Details
        selected_company_ids = []
        
        for company in companies:
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                is_selected = st.checkbox(
                    "", 
                    key=f"select_company_{company['id']}",
                    value=company['id'] in st.session_state.multi_offer_selected_companies
                )
                
            with col2:
                st.write(f"**{company['name']}**")
                if company.get('street'):
                    st.write(f"{company['street']}, {company.get('zip_code', '')} {company.get('city', '')}")
                    
            with col3:
                # Anzahl Produkte anzeigen
                products = self.get_company_products(company['id'])
                total_products = sum(len(prods) for prods in products.values())
                st.write(f"📦 {total_products} Produkte")
                
            with col4:
                # Quick Info
                if company.get('phone'):
                    st.write(f"📞 {company['phone']}")
                if company.get('email'):
                    st.write(f"📧 {company['email']}")
                    
            if is_selected:
                selected_company_ids.append(company['id'])
                
        # Update Session State
        st.session_state.multi_offer_selected_companies = selected_company_ids
        
        if selected_company_ids:
            st.success(f"✅ {len(selected_company_ids)} Firma(en) ausgewählt")
        else:
            st.info("💡 Bitte mindestens eine Firma auswählen")
            
    def render_offer_configuration(self):
        """Rendert Angebotskonfiguration pro Firma"""
        if not st.session_state.multi_offer_selected_companies:
            return

        st.subheader("⚙️ Angebotskonfiguration pro Firma")

        companies = self.get_available_companies()
        company_dict = {c['id']: c for c in companies}

        for company_id in st.session_state.multi_offer_selected_companies:
            company = company_dict.get(company_id)
            if not company:
                continue

            with st.expander(f"{company['name']} - Konfiguration", expanded=True):
                st.markdown(f"### 🏢 {company['name']}")

                # Produktauswahl für die Firma
                module_quantity = st.number_input(
                    f"Anzahl PV-Module für {company['name']}",
                    min_value=1,
                    max_value=100,
                    value=20,
                    key=f"module_qty_{company_id}"
                )

                selected_module = st.selectbox(
                    f"PV-Modul-Modell für {company['name']}",
                    ["Vitovolt 300-DG M440HC (440 Wp)", "Modul X (500 Wp)", "Modul Y (600 Wp)"],
                    key=f"module_select_{company_id}"
                )   
                module_price = st.number_input(
                    f"Preis pro Modul für {company['name']} (€)",
                    min_value=0.0,
                    value=100.0,
                    step=1.0,
                    key=f"module_price_{company_id}"
                )

                st.write(f"**Ausgewählte Konfiguration für {company['name']}:**")
                st.write(f"- Anzahl PV-Module: {module_quantity}")
                st.write(f"- PV-Modul-Modell: {selected_module}")                
                st.write(f"- Preis pro Modul: {module_price:.2f} €")
                
                # Speichere aktuelles company_id für die Angebots-Einstellungen
                current_company_id = company_id
                current_company_name = company['name']
                
                # Angebotsspezifische Einstellungen
                st.markdown("#### 📄 Angebots-Einstellungen")
                
                col1, col2 = st.columns(2)                
                with col1:
                    offer_title = st.text_input(
                        "Angebots-Titel",
                        value=f"Ihr individuelles PV-Angebot von {current_company_name}",
                        key=f"offer_title_{current_company_id}"
                    )
                    
                with col2:
                    offer_validity_days = st.number_input(
                        "Gültigkeit (Tage)",
                        min_value=1,
                        max_value=365,
                        value=30,
                        key=f"offer_validity_{current_company_id}"
                    )
                    
                # Cover Letter
                cover_letter = st.text_area(
                    "Anschreiben-Text",
                    value=f"""Sehr geehrte/r {{salutation_line}},

vielen Dank für Ihr Interesse an einer Photovoltaikanlage. Gerne unterbreiten wir Ihnen unser maßgeschneidertes Angebot.

Mit {current_company_name} entscheiden Sie sich für:
• Premium-Qualität und langjährige Erfahrung
• Persönliche Beratung und Service
• Faire Preise bei höchster Qualität

Wir freuen uns auf Ihre Rückmeldung!

Mit freundlichen Grüßen
Ihr Team von {current_company_name}""",
                    height=200,
                    key=f"cover_letter_{current_company_id}"                )
                
                # Produktdaten für diese Firma laden
                products = self.get_company_products(company_id)
                
                # Wechselrichter-Auswahl
                selected_inverter = None
                if 'wechselrichter' in products and products['wechselrichter']:
                    inverter_options = [f"{p['brand']} {p['model_name']}" for p in products['wechselrichter']]
                    selected_inverter_name = st.selectbox(
                        f"Wechselrichter für {company['name']}",
                        inverter_options,
                        key=f"inverter_select_{company_id}"
                    )
                    # Ausgewählten Wechselrichter finden
                    for inverter in products['wechselrichter']:
                        if f"{inverter['brand']} {inverter['model_name']}" == selected_inverter_name:
                            selected_inverter = inverter
                            break
                
                # Speicher-Option                include_storage = st.checkbox(
                    f"Batteriespeicher hinzufügen für {company['name']}",
                    value=False,
                    key=f"include_storage_{company_id}"
                        
                # Speicher-Auswahl wenn aktiviert
                selected_storage = None
                if include_storage and 'batteriespeicher' in products and products['batteriespeicher']:
                    storage_options = [f"{p['brand']} {p['model_name']}" for p in products['batteriespeicher']]
                    selected_storage_name = st.selectbox(
                        f"Speicher-Modell für {company['name']}",
                        storage_options,
                        key=f"storage_select_{company_id}"
                    )
                    # Ausgewählten Speicher finden
                    for storage in products['batteriespeicher']:
                        if f"{storage['brand']} {storage['model_name']}" == selected_storage_name:
                            selected_storage = storage
                            break
                
                # Wallbox-Option
                include_wallbox = st.checkbox(
                    f"Wallbox hinzufügen für {company['name']}",
                    value=False,
                    key=f"include_wallbox_{company_id}"
                )
                
                # Konfiguration in Session State speichern
                config_key = f"company_config_{company_id}"
                st.session_state[config_key] = {
                    "company_id": company_id,
                    "company_name": company["name"],
                    "selected_module": selected_module,
                    "module_quantity": module_quantity,
                    "selected_inverter": selected_inverter,
                    "selected_storage": selected_storage,
                    "include_storage": include_storage,
                    "include_wallbox": include_wallbox,
                    "offer_title": offer_title,
                    "offer_validity_days": offer_validity_days,
                    "cover_letter": cover_letter
                }
                
                # Kostenübersicht anzeigen
                if products and 'modul' in products and 'wechselrichter' in products:
                    self.show_cost_preview(company_id)
            
    def show_cost_preview(self, company_id: int):
        """Zeigt Kostenvorschau für eine Firma"""
        config_key = f"company_config_{company_id}"
        if config_key not in st.session_state:
            return
            
        config = st.session_state[config_key]
        
        st.markdown("#### 💰 Kostenvorschau")
        
        total_cost = 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if config['selected_module']:
                module_cost = config['selected_module']['price_euro'] * config['module_quantity']
                st.metric("Module", f"{module_cost:,.2f} €")
                total_cost += module_cost
                
        with col2:
            if config['selected_inverter']:
                inverter_cost = config['selected_inverter']['price_euro']
                st.metric("Wechselrichter", f"{inverter_cost:,.2f} €")
                total_cost += inverter_cost
                
        with col3:
            if config['selected_storage']:
                storage_cost = config['selected_storage']['price_euro']
                st.metric("Batteriespeicher", f"{storage_cost:,.2f} €")
                total_cost += storage_cost
                
        # Gesamtkosten
        st.markdown(f"**Gesamtkosten (netto): {total_cost:,.2f} €**")
        
        # AnlagengrößeEin kritischer Fehler ist in der Anwendung aufgetreten! Details: name 'company_name' is not defined
        if config['selected_module']:
            total_kwp = (config['selected_module']['capacity_w'] * config['module_quantity']) / 1000
            st.markdown(f"**Anlagengröße: {total_kwp:.2f} kWp**")
            
    def generate_multi_offers(self) -> Optional[bytes]:
        """Generiert alle Angebote und packt sie in eine ZIP-Datei"""
        if not st.session_state.multi_offer_selected_companies:
            st.error("❌ Keine Firmen ausgewählt!")
            return None
            
        if not st.session_state.multi_offer_customer_data.get('last_name'):
            st.error("❌ Kundendaten unvollständig!")
            return None
            
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # texts = get_text_dict("de")  # Deutsche Texte - Nicht verfügbar
            texts = {"default": "Standard"}  # Fallback
            
            for company_id in st.session_state.multi_offer_selected_companies:
                try:
                    # Firmendaten laden
                    company_info = get_company(company_id)
                    if not company_info:
                        st.warning(f"⚠️ Firma {company_id} nicht gefunden - übersprungen")
                        continue
                        
                    # Konfiguration laden
                    config_key = f"company_config_{company_id}"
                    if config_key not in st.session_state:
                        st.warning(f"⚠️ Keine Konfiguration für {company_info['name']} - übersprungen")
                        continue
                        
                    config = st.session_state[config_key]
                    
                    # Projektdaten für diese Firma zusammenstellen
                    project_data = {
                        "customer_data": st.session_state.multi_offer_customer_data,
                        "project_details": {
                            "module_quantity": config.get('module_quantity', 0),
                            "selected_module_id": config['selected_module']['id'] if config.get('selected_module') else None,
                            "selected_inverter_id": config['selected_inverter']['id'] if config.get('selected_inverter') else None,
                            "include_storage": config.get('include_storage', False),
                            "selected_storage_id": config['selected_storage']['id'] if config.get('selected_storage') else None,
                            "include_additional_components": config.get('include_wallbox', False)
                        }
                    }
                    
                    # Einfache Analyse-Ergebnisse berechnen
                    analysis_results = self.calculate_simple_analysis(config)
                    
                    # Angebotsnummer generieren
                    offer_number = f"{datetime.now().strftime('%Y%m%d')}-{company_id:03d}"
                    
                    # PDF generieren
                    pdf_bytes = generate_offer_pdf(
                        project_data=project_data,
                        analysis_results=analysis_results,
                        texts=texts,
                        company_info=company_info,
                        selected_offer_title_text=config.get('offer_title', 'Ihr PV-Angebot'),
                        selected_cover_letter_text=config.get('cover_letter', ''),
                        selected_title_image_b64=None,
                        offer_number=offer_number,
                        sections_to_include=["ProjectOverview", "TechnicalComponents", "CostDetails"],
                        inclusion_options={
                            "include_company_logo": True,
                            "include_all_documents": False,
                            "include_optional_component_details": True,
                            "selected_charts_for_pdf": []
                        },
                        get_product_by_id_func=get_product_by_id,
                        db_list_company_documents_func=lambda x, y: [],
                        active_company_id=company_id,
                        company_document_ids_to_include=[],
                        company_logo_base64=company_info.get('logo_base64'),
                        load_admin_setting_func=lambda x: None,
                        save_admin_setting_func=lambda x, y: None,
                        list_products_func=lambda: []
                    )
                    
                    if pdf_bytes:
                        # Dateiname für das PDF
                        company_name_clean = "".join(c for c in company_info['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        filename = f"Angebot_{company_name_clean}_{offer_number}.pdf"
                        
                        # PDF zur ZIP hinzufügen                        zip_file.writestr(filename, pdf_bytes)
                        
                    else:
                        st.warning(f"⚠️ PDF für {company_info['name']} konnte nicht erstellt werden")
                        
                except Exception as e:
                    st.error(f"❌ Fehler bei {company_info.get('name', f'Firma {company_id}')}: {str(e)}")
                    continue
                    
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    def calculate_simple_analysis(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet einfache Analyse-Ergebnisse"""
        analysis = {}
        
        # Anlagengröße berechnen - Verarbeitung des ausgewählten Moduls
        selected_module = config.get('selected_module')
        module_quantity = config.get('module_quantity', 0)
        
        if selected_module and module_quantity:
            # Kapazität aus dem Modulnamen extrahieren, wenn es ein String ist
            if isinstance(selected_module, str):
                # Versuche, die Leistung aus dem Modulnamen zu extrahieren (z.B. "Modul X (500 Wp)")
                import re
                match = re.search(r'(\d+)\s*Wp', selected_module)
                if match:
                    capacity_w = float(match.group(1))
                else:
                    # Standardwert, wenn keine Leistungsangabe gefunden wurde
                    capacity_w = 400.0  # Annahme: 400 Watt pro Modul als Standard
            else:
                # Falls es ein Dictionary ist mit Kapazitätsangabe
                capacity_w = selected_module.get('capacity_w', 400.0)
                
            total_kwp = (capacity_w * module_quantity) / 1000
            analysis['anlage_kwp'] = total_kwp
            
            # Geschätzte jährliche Produktion (950 kWh/kWp als Standard)
            analysis['annual_pv_production_kwh'] = total_kwp * 950
            
            # Geschätzte Autarkie (einfache Schätzung)
            analysis['self_supply_rate_percent'] = min(75, 25 + (total_kwp * 5))
            
        # Gesamtinvestition berechnen
        total_cost = 0
        
        # Modulkosten
        if selected_module:
            if isinstance(selected_module, dict) and 'price_euro' in selected_module:
                module_price = selected_module['price_euro']
            else:
                # Wenn es kein Dictionary ist oder keine Preisangabe hat, verwenden wir den eingegebenen Preis
                module_price = config.get('module_price', 100.0)
                
            total_cost += module_price * module_quantity
            
        # Wechselrichterkosten
        if config.get('selected_inverter') and isinstance(config['selected_inverter'], dict):
            total_cost += config['selected_inverter'].get('price_euro', 0)
            
        # Speicherkosten
        if config.get('selected_storage') and isinstance(config['selected_storage'], dict):
            total_cost += config['selected_storage'].get('price_euro', 0)
            
        analysis['total_investment_cost'] = total_cost
        
        # Einfache ROI-Schätzung
        if total_cost > 0 and analysis.get('annual_pv_production_kwh'):
            annual_savings = analysis['annual_pv_production_kwh'] * 0.30  # 30 Cent/kWh Ersparnis
            analysis['annual_savings'] = annual_savings
            analysis['payback_period_years'] = total_cost / annual_savings if annual_savings > 0 else 25
            
        return analysis
        
    def render_generation_interface(self):
        """Rendert die Generierungs-Oberfläche"""
        if not st.session_state.multi_offer_selected_companies:
            st.info("💡 Bitte erst Firmen auswählen und konfigurieren")
            return
            
        st.subheader("🚀 Angebote generieren")
        
        # Zusammenfassung
        companies = self.get_available_companies()
        company_dict = {c['id']: c for c in companies}
        
        selected_company_names = [
            company_dict[cid]['name'] 
            for cid in st.session_state.multi_offer_selected_companies
        ]
        
        st.markdown("**📋 Zusammenfassung:**")
        st.markdown(f"**Kunde:** {st.session_state.multi_offer_customer_data.get('first_name', '')} {st.session_state.multi_offer_customer_data.get('last_name', '')}")
        st.markdown(f"**Anzahl Angebote:** {len(selected_company_names)}")
        st.markdown(f"**Firmen:** {', '.join(selected_company_names)}")
        
        # Generierungs-Button
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            if st.button("🎯 ALLE ANGEBOTE ERSTELLEN", type="primary", use_container_width=True):
                self.execute_generation()
                
    def execute_generation(self):
        """Führt die Generierung aus"""
        with st.spinner("🔄 Erstelle Multi-Firmen-Angebote..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # ZIP-Datei generieren
            status_text.text("📦 Generiere PDF-Angebote...")
            progress_bar.progress(25)
            
            zip_bytes = self.generate_multi_offers()
            
            if zip_bytes:
                progress_bar.progress(100)
                status_text.text("✅ Alle Angebote erfolgreich erstellt!")
                
                # Download-Button
                customer_name = f"{st.session_state.multi_offer_customer_data.get('last_name', 'Kunde')}"
                filename = f"Multi_Angebote_{customer_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                
                st.download_button(
                    label="📥 ALLE ANGEBOTE HERUNTERLADEN (ZIP)",
                    data=zip_bytes,
                    file_name=filename,
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
                
                st.success(f"🎉 {len(st.session_state.multi_offer_selected_companies)} Angebote erfolgreich erstellt!")
                
                # Statistiken anzeigen
                st.markdown("### 📊 Generierungs-Statistik")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Angebote erstellt", len(st.session_state.multi_offer_selected_companies))
                    
                with col2:
                    st.metric("ZIP-Dateigröße", f"{len(zip_bytes) / 1024:.1f} KB")
                    
                with col3:
                    st.metric("Erstellungszeit", f"{datetime.now().strftime('%H:%M:%S')}")
                    
            else:
                progress_bar.progress(0)
                status_text.text("❌ Fehler bei der Generierung")
                st.error("❌ Keine Angebote konnten erstellt werden!")
                
    def render_offer_generation(self):
        """Rendert die Angebotsgenerierung"""
        st.subheader("🚀 Angebote generieren")
        
        # Prüfung der Voraussetzungen
        customer_data = st.session_state.multi_offer_customer_data
        selected_companies = st.session_state.multi_offer_selected_companies
        
        if not customer_data.get('first_name') or not customer_data.get('last_name'):
            st.warning("⚠️ Bitte geben Sie zuerst die Kundendaten ein.")
            return
            
        if not selected_companies:
            st.warning("⚠️ Bitte wählen Sie mindestens eine Firma aus.")
            return
            
        # Status anzeigen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👤 Kunde", f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}")
            
        with col2:
            st.metric("🏢 Firmen", len(selected_companies))
            
        with col3:
            st.metric("📄 Angebote", len(selected_companies))
        
        # Generierung starten
        if st.button("🚀 Alle Angebote generieren", key="generate_all_offers", type="primary"):
            with st.spinner("Generiere Angebote..."):
                self.generate_all_offers()
        
        # Vorschau der Konfigurationen
        if st.checkbox("🔍 Konfigurationen anzeigen", key="show_configs"):
            st.markdown("### Konfigurationen pro Firma")
            
            companies = self.get_available_companies()  
            company_dict = {c['id']: c for c in companies}
            
            for company_id in selected_companies:
                company = company_dict.get(company_id)
                if not company:
                    continue
                    
                config_key = f"company_config_{company_id}"
                config = st.session_state.get(config_key, {})
                
                with st.expander(f"📋 {company['name']} - Konfiguration"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Grunddaten:**")
                        st.write(f"• Firma: {company['name']}")
                        st.write(f"• Module: {config.get('module_quantity', 0)} Stück")
                        st.write(f"• Wechselrichter: {'Ja' if config.get('selected_inverter') else 'Nein'}")
                        st.write(f"• Speicher: {'Ja' if config.get('include_storage') else 'Nein'}")
                        
                    with col2:
                        st.write("**Angebot:**")
                        st.write(f"• Titel: {config.get('offer_title', 'Standard')}")
                        st.write(f"• Gültigkeit: {config.get('offer_validity_days', 30)} Tage")
        
    def generate_all_offers(self):
        """Generiert alle Angebote für die ausgewählten Firmen"""
        try:
            customer_data = st.session_state.multi_offer_customer_data
            selected_companies = st.session_state.multi_offer_selected_companies
            companies = self.get_available_companies()
            company_dict = {c['id']: c for c in companies}
            
            generated_pdfs = {}
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, company_id in enumerate(selected_companies):
                company = company_dict.get(company_id)
                if not company:
                    continue
                    
                status_text.text(f"Generiere Angebot für {company['name']}...")
                  # Konfiguration laden
                config_key = f"company_config_{company_id}"
                config = st.session_state.get(config_key, {})
                
                # PDF generieren (simuliert)
                pdf_filename = f"Angebot_{company['name'].replace(' ', '_')}.pdf"
                
                # Hier würde die echte PDF-Generierung stattfinden
                # pdf_content = self.generate_company_pdf(company, customer_data, config)
                # generated_pdfs[pdf_filename] = pdf_content
                
                # Simulation für Demo
                generated_pdfs[pdf_filename] = f"PDF Inhalt für {company['name']}"
                
                # Progress aktualisieren
                progress_bar.progress((i + 1) / len(selected_companies))
            
            status_text.text("✅ Alle Angebote erfolgreich generiert!")
            
            # Download-Button für ZIP
            if generated_pdfs:
                zip_data = self.create_zip_from_pdfs(generated_pdfs)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"Multi_Angebote_{customer_data.get('last_name', 'Kunde')}_{timestamp}.zip"
                
                st.download_button(
                    label="📦 Alle Angebote als ZIP herunterladen",
                    data=zip_data,
                    file_name=zip_filename,
                    mime="application/zip",
                    key="download_all_offers"
                )
                
                st.success(f"🎉 {len(generated_pdfs)} Angebote erfolgreich erstellt!")
                
        except Exception as e:
            st.error(f"❌ Fehler bei der Angebotsgenerierung: {e}")
            st.exception(e)
    
    def create_zip_from_pdfs(self, pdf_dict: Dict[str, str]) -> bytes:
        """Erstellt eine ZIP-Datei aus den generierten PDFs"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in pdf_dict.items():
                # Simulation - in echter Implementierung wären das PDF-Bytes
                zip_file.writestr(filename, content.encode('utf-8'))        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    def render_product_selection(self):
        """Rendert die Produktauswahl und Konfiguration pro Firma"""
        st.subheader("📦 Produktauswahl pro Firma")

        if not st.session_state.multi_offer_selected_companies:
            st.warning("⚠️ Bitte wählen Sie zuerst Firmen aus, bevor Sie Produkte konfigurieren.")
            return

        companies = self.get_available_companies()
        company_dict = {c['id']: c for c in companies}
        
        for company_id in st.session_state.multi_offer_selected_companies:
            company = company_dict.get(company_id)
            if not company:
                continue
                
            st.markdown(f"### {company['name']}")

            products_by_category = self.get_company_products(company_id)

            if not products_by_category:
                st.info(f"ℹ️ Keine Produkte für {company['name']} verfügbar.")
                continue

            for category, products in products_by_category.items():
                st.markdown(f"#### {category.capitalize()}")

                for product in products:
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.text(f"{product['brand']} {product['model_name']} ({product['capacity_w']} W)")

                    with col2:
                        quantity = st.number_input(
                            "Anzahl",
                            min_value=0,
                            step=1,
                            key=f"quantity_{company_id}_{product['id']}"
                        )

                    with col3:
                        price = st.number_input(
                            "Preis (€)",
                            min_value=0.0,
                            step=0.01,
                            key=f"price_{company_id}_{product['id']}"
                        )

                    # Speichern der Konfiguration in Session State
                    if quantity > 0:
                        st.session_state.multi_offer_settings.setdefault(company_id, {})[product['id']] = {
                            'quantity': quantity,
                            'price': price
                        }
                

# Hauptfunktion für die Multi-Offer Seite
def render_multi_offer_page():
    """Hauptfunktion für die Multi-Firmen-Angebots-Seite"""
    st.title("🏢 Multi-Firmen-Angebotsgenerator")
    st.markdown("*Erstellen Sie mehrere Angebote für verschiedene Firmen mit nur einer Eingabe!*")
    
    generator = MultiCompanyOfferGenerator()
    generator.initialize_session_state()
    
    # Navigation durch den Prozess
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Kundendaten", 
        "🏢 Firmen wählen", 
        "⚙️ Konfiguration", 
        "🚀 Generierung"
    ])
    
    with tab1:
        generator.render_customer_input()
        
    with tab2:
        generator.render_company_selection()
        
    with tab3:
        generator.render_offer_configuration()
        
    with tab4:
        generator.render_generation_interface()
        
    # Info-Sidebar
    with st.sidebar:
        st.markdown("### 💡 Multi-Firmen-Angebote")
        st.markdown("""
        **Vorteile:**
        • Ein Kunde → Mehrere Angebote
        • Verschiedene Firmen & Produkte
        • Individuelle Preise & Logos
        • Zeitersparnis durch Automatisierung
        • Höhere Conversion-Rate
        
        **Ablauf:**
        1. Kundendaten eingeben
        2. Firmen auswählen  
        3. Produkte & Preise pro Firma
        4. Alle Angebote als ZIP downloaden
        """)
        
        if st.session_state.multi_offer_selected_companies:
            st.success(f"✅ {len(st.session_state.multi_offer_selected_companies)} Firma(en) gewählt")
        else:
            st.info("💡 Noch keine Firmen gewählt")


def render_multi_offer_generator(TEXTS, project_data_doc, calc_results_doc):
    """Hauptfunktion für die Multi-Firmen-Angebotsgenerator-Benutzeroberfläche"""
    
    # Initialize generator instance
    if 'multi_offer_generator' not in st.session_state:
        st.session_state.multi_offer_generator = MultiCompanyOfferGenerator()
    
    generator = st.session_state.multi_offer_generator
    generator.initialize_session_state()
    
    st.markdown("""
    ## 🏢 Multi-Firmen-Angebotsgenerator
    
    **Erstellen Sie mehrere individualisierte Angebote für verschiedene Firmen mit einer einzigen Eingabe!**
    
    ---
    """)
    
    # Use the passed arguments (TEXTS, project_data_doc, calc_results_doc) as needed
    # Placeholder for further implementation

    # Step 1: Kundendaten eingeben
    with st.container():
        generator.render_customer_input()
    
    st.markdown("---")
    
    # Step 2: Firmen auswählen
    with st.container():
        generator.render_company_selection()
    
    st.markdown("---")
    
    # Step 3: Angebotskonfiguration (nur wenn Firmen ausgewählt)
    if st.session_state.multi_offer_selected_companies:
        with st.container():
            generator.render_offer_configuration()
        
        st.markdown("---")
        
        # Step 4: Angebote generieren
        with st.container():
            generator.render_offer_generation()
    
    # Status-Anzeige
    with st.sidebar:
        st.markdown("### 📊 Status")
        
        customer_status = "✅" if st.session_state.multi_offer_customer_data.get('first_name') else "❌"
        st.write(f"{customer_status} Kundendaten")
        
        company_count = len(st.session_state.multi_offer_selected_companies)
        company_status = "✅" if company_count > 0 else "❌"
        st.write(f"{company_status} Firmen ({company_count})")
        
        if company_count > 0:
            st.info(f"💡 {company_count} Angebote werden erstellt")


# Test-Funktion für Standalone-Nutzung
if __name__ == "__main__":
    # st.set_page_config wird vom Hauptskript gehandhabt
    render_multi_offer_generator(None, None, None)
