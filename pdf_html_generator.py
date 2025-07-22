# pdf_html_generator.py
# -*- coding: utf-8 -*-
"""
HTML+CSS basierte PDF-Generierung mit WeasyPrint und Jinja2
Erstellt wirklich schöne, professionelle PDFs mit modernem Design
"""

import streamlit as st
from jinja2 import Template, Environment, FileSystemLoader
import os
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64

try:
    from weasyprint import HTML, CSS
    _WEASYPRINT_AVAILABLE = True
except ImportError:
    _WEASYPRINT_AVAILABLE = False
    st.warning("⚠️ WeasyPrint nicht verfügbar. Installieren Sie es mit: pip install weasyprint")

class HTMLPDFGenerator:
    """
    HTML+CSS basierte PDF-Generierung
    Verwendet WeasyPrint für hochwertige PDF-Ausgabe
    """
    
    def __init__(self):
        self.template_dir = "pdf_templates_html"
        self.css_dir = "pdf_styles_css"
        self.images_dir = "pdf_images"
        
        # Erstelle Verzeichnisse falls sie nicht existieren
        for directory in [self.template_dir, self.css_dir, self.images_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Jinja2 Environment einrichten
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
    
    def create_templates(self):
        """Erstellt die HTML-Templates für verschiedene Angebots-Stile"""
        
        # Premium Luxus Template
        self.create_premium_luxus_template()
        # Corporate Professional Template
        self.create_corporate_template()
        # Modern Tech Template
        self.create_modern_tech_template()
        # Solar Green Template
        self.create_solar_green_template()
        
        # CSS-Dateien erstellen
        self.create_css_styles()
    
    def create_premium_luxus_template(self):
        """Erstellt Premium Luxus HTML Template"""
        
        html_content = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>Premium Photovoltaik-Angebot - {{ kunde_name }}</title>
    <link rel="stylesheet" href="../pdf_styles_css/premium_luxus.css">
</head>
<body>
    <!-- Header mit Logo -->
    <div class="header">
        <div class="logo-container">
            {% if firma_logo %}
            <img src="{{ firma_logo }}" alt="Firmenlogo" class="logo">
            {% endif %}
        </div>
        <div class="header-content">
            <h1 class="main-title">PREMIUM PHOTOVOLTAIK-ANGEBOT</h1>
            <p class="subtitle">Exklusive Solar-Lösung für {{ kunde_name }}</p>
        </div>
    </div>

    <!-- Angebots-Details -->
    <div class="angebot-info">
        <div class="info-grid">
            <div class="info-item">
                <strong>Angebotsnummer:</strong> {{ angebot_id }}
            </div>
            <div class="info-item">
                <strong>Datum:</strong> {{ datum }}
            </div>
            <div class="info-item">
                <strong>Gültig bis:</strong> {{ gueltig_bis }}
            </div>
            <div class="info-item">
                <strong>Projekttyp:</strong> Premium Photovoltaik-Anlage
            </div>
        </div>
    </div>

    <!-- Projekt-Highlights -->
    <div class="section highlights-section">
        <h2 class="section-title">🌟 Projekt-Highlights</h2>
        <div class="highlights-grid">
            <div class="highlight-card">
                <div class="highlight-icon">🏠</div>
                <div class="highlight-value">{{ system_power }} kWp</div>
                <div class="highlight-label">Anlagenleistung</div>
            </div>
            <div class="highlight-card">
                <div class="highlight-icon">⚡</div>
                <div class="highlight-value">{{ annual_yield | int | string | format_number }} kWh</div>
                <div class="highlight-label">Jahresertrag</div>
            </div>
            <div class="highlight-card">
                <div class="highlight-icon">💎</div>
                <div class="highlight-value">{{ total_cost | int | string | format_number }} €</div>
                <div class="highlight-label">Premium-Investition</div>
            </div>
            <div class="highlight-card">
                <div class="highlight-icon">📈</div>
                <div class="highlight-value">{{ annual_savings | int | string | format_number }} €</div>
                <div class="highlight-label">Jährliche Ersparnis</div>
            </div>
            <div class="highlight-card">
                <div class="highlight-icon">🌱</div>
                <div class="highlight-value">{{ co2_savings | int | string | format_number }} kg</div>
                <div class="highlight-label">CO₂-Einsparung/Jahr</div>
            </div>
            <div class="highlight-card">
                <div class="highlight-icon">⏰</div>
                <div class="highlight-value">{{ payback_time }} Jahre</div>
                <div class="highlight-label">Amortisation</div>
            </div>
        </div>
    </div>

    <!-- Executive Summary -->
    <div class="section summary-section">
        <h2 class="section-title">📊 Executive Summary</h2>
        <div class="summary-content">
            <p>Mit großer Freude präsentieren wir Ihnen unsere maßgeschneiderte Premium-Photovoltaik-Lösung für Ihr Objekt. 
            Unsere geplante Hochleistungsanlage mit <strong>{{ system_power }} kWp</strong> Spitzenleistung wird jährlich etwa 
            <strong>{{ annual_yield | int | string | format_number }} kWh</strong> erstklassigen, umweltfreundlichen Strom produzieren.</p>
            
            <p>Diese Premium-Investition von <strong>{{ total_cost | int | string | format_number }} €</strong> amortisiert sich 
            bereits nach <strong>{{ payback_time }} Jahren</strong> und wird Ihnen langfristig erhebliche Stromkosteneinsparungen ermöglichen.</p>
            
            <div class="benefits-box">
                <h3>🌟 Ihre Premium-Vorteile:</h3>
                <ul class="benefits-list">
                    <li>Drastische Reduzierung der Stromkosten um bis zu 80%</li>
                    <li>Signifikanter Beitrag zum Umwelt- und Klimaschutz</li>
                    <li>Erhebliche Wertsteigerung Ihrer Immobilie</li>
                    <li>Komplette Unabhängigkeit von Strompreiserhöhungen</li>
                    <li>Höchste Qualitätskomponenten mit Premiumgarantie</li>
                    <li>Professionelle Installation durch zertifizierte Experten</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Technische Spezifikationen -->
    <div class="section tech-section">
        <h2 class="section-title">🔧 Technische Spezifikationen</h2>
        <table class="tech-table">
            <thead>
                <tr>
                    <th>Komponente</th>
                    <th>Premium-Spezifikation</th>
                    <th>Anzahl</th>
                    <th>Leistung</th>
                    <th>Qualität</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Solarmodule</td>
                    <td>{{ module_type }}</td>
                    <td>{{ module_count }}</td>
                    <td>{{ module_power }} Wp</td>
                    <td>A+ Klasse</td>
                </tr>
                <tr>
                    <td>Wechselrichter</td>
                    <td>{{ inverter_type }}</td>
                    <td>1</td>
                    <td>{{ inverter_power }} kW</td>
                    <td>Premium-Qualität</td>
                </tr>
                <tr>
                    <td>Montagesystem</td>
                    <td>Premium Aufdach-Montage</td>
                    <td>1 Komplettsystem</td>
                    <td>{{ module_count }} Module</td>
                    <td>Alu-Premium</td>
                </tr>
                <tr>
                    <td>Überwachung</td>
                    <td>Smart-Monitoring Pro</td>
                    <td>1 System</td>
                    <td>Vollüberwachung</td>
                    <td>Premium-Features</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Wirtschaftlichkeit -->
    <div class="section finance-section">
        <h2 class="section-title">💰 Wirtschaftlichkeitsanalyse</h2>
        <div class="finance-grid">
            <div class="cost-breakdown">
                <h3>Investitionsaufschlüsselung</h3>
                <table class="cost-table">
                    {% for kosten_item in kosten_breakdown %}
                    <tr>
                        <td>{{ kosten_item.name }}</td>
                        <td class="cost-value">{{ kosten_item.betrag | int | string | format_number }} €</td>
                        <td class="cost-percent">{{ kosten_item.anteil }}%</td>
                    </tr>
                    {% endfor %}
                    <tr class="total-row">
                        <td><strong>GESAMTINVESTITION</strong></td>
                        <td class="cost-value"><strong>{{ total_cost | int | string | format_number }} €</strong></td>
                        <td class="cost-percent"><strong>100%</strong></td>
                    </tr>
                </table>
            </div>
            
            <div class="roi-box">
                <h3>💎 Return on Investment</h3>
                <p>Ihre jährliche Premium-Stromkosteneinsparung beträgt außergewöhnliche 
                <strong>{{ annual_savings | int | string | format_number }} €</strong>.</p>
                <p>Über die garantierte 25-jährige Premium-Lebensdauer sparen Sie insgesamt 
                <strong>{{ (annual_savings * 25) | int | string | format_number }} €</strong> an Energiekosten.</p>
                <div class="roi-highlight">
                    Das entspricht einer Rendite von über <strong>{{ ((annual_savings * 25 / total_cost * 100) | int) }}%</strong> 
                    auf Ihre Premium-Investition!
                </div>
            </div>
        </div>
    </div>

    <!-- Umwelt & Nachhaltigkeit -->
    <div class="section environment-section">
        <h2 class="section-title">🌍 Umwelt & Nachhaltigkeit</h2>
        <div class="environment-content">
            <div class="co2-highlight">
                <div class="co2-value">{{ co2_savings | int | string | format_number }} kg</div>
                <div class="co2-label">CO₂-Reduktion pro Jahr</div>
            </div>
            <div class="environment-facts">
                <h3>Ihr außergewöhnlicher Beitrag für unseren Planeten:</h3>
                <ul>
                    <li>Massive jährliche CO₂-Reduktion: <strong>{{ co2_savings | int | string | format_number }} kg</strong></li>
                    <li>Entspricht dem Pflanzen von ca. <strong>{{ (co2_savings / 22) | int }}</strong> Bäumen pro Jahr</li>
                    <li>Über 25 Jahre: <strong>{{ (co2_savings * 25) | int | string | format_number }} kg</strong> CO₂-Vermeidung</li>
                    <li>Sauberer Premium-Strom für ca. <strong>{{ (annual_yield / 3500) | int }}</strong> durchschnittliche Haushalte</li>
                    <li>Vermeidung von <strong>{{ (co2_savings * 25 / 1000) | round(1) }}</strong> Tonnen CO₂ über die Anlagenlebensdauer</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="footer">
        <div class="footer-content">
            <p><strong>{{ firma_name }}</strong></p>
            <p>{{ firma_adresse }}</p>
            <p>Tel: {{ firma_telefon }} | E-Mail: {{ firma_email }}</p>
            <p class="footer-note">Mit Ihrer Premium-Solaranlage leisten Sie einen bedeutenden Beitrag zur Energiewende 
            und schaffen ein nachhaltiges Erbe für kommende Generationen.</p>
        </div>
    </div>
</body>
</html>'''
        
        with open(os.path.join(self.template_dir, "premium_luxus.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def create_css_styles(self):
        """Erstellt die CSS-Stile für Premium Luxus Design"""
        
        css_content = '''/* Premium Luxus CSS Styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-color: #003366;
    --secondary-color: #0066CC;
    --accent-color: #FFD700;
    --success-color: #2E8B57;
    --background-color: #F8FBFF;
    --text-primary: #1A1A1A;
    --text-secondary: #4A4A4A;
    --border-color: #E6F2FF;
    --white: #FFFFFF;
    --light-blue: #E6F2FF;
    --dark-blue: #002244;
    --premium-gold: #B8860B;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', 'Arial', sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background-color: var(--white);
    font-size: 11pt;
}

.header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: var(--white);
    padding: 40px 30px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}

.header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
}

.logo-container {
    position: absolute;
    top: 20px;
    right: 30px;
    z-index: 2;
}

.logo {
    max-width: 120px;
    max-height: 80px;
    object-fit: contain;
}

.header-content {
    position: relative;
    z-index: 2;
}

.main-title {
    font-size: 32pt;
    font-weight: 700;
    margin-bottom: 15px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    letter-spacing: 1px;
}

.subtitle {
    font-size: 18pt;
    font-weight: 400;
    opacity: 0.95;
    margin-bottom: 0;
}

.angebot-info {
    background: var(--background-color);
    border: 2px solid var(--border-color);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 30px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

.info-item {
    padding: 12px;
    background: var(--white);
    border-radius: 8px;
    border-left: 4px solid var(--accent-color);
    font-size: 12pt;
}

.section {
    margin-bottom: 35px;
    padding: 0 20px;
}

.section-title {
    font-size: 20pt;
    font-weight: 600;
    color: var(--primary-color);
    margin-bottom: 20px;
    padding: 15px 20px;
    background: linear-gradient(90deg, var(--background-color) 0%, var(--white) 100%);
    border-left: 6px solid var(--accent-color);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.highlights-section {
    background: var(--background-color);
    border-radius: 15px;
    padding: 30px;
    margin-bottom: 40px;
}

.highlights-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 20px;
}

.highlight-card {
    background: var(--white);
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border: 1px solid var(--border-color);
    transition: transform 0.2s ease;
}

.highlight-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.highlight-icon {
    font-size: 24pt;
    margin-bottom: 10px;
}

.highlight-value {
    font-size: 20pt;
    font-weight: 700;
    color: var(--accent-color);
    margin-bottom: 8px;
}

.highlight-label {
    font-size: 10pt;
    color: var(--text-secondary);
    font-weight: 500;
}

.summary-content p {
    margin-bottom: 15px;
    text-align: justify;
    line-height: 1.7;
}

.benefits-box {
    background: linear-gradient(135deg, var(--accent-color) 0%, var(--premium-gold) 100%);
    color: var(--white);
    padding: 25px;
    border-radius: 12px;
    margin-top: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.benefits-box h3 {
    margin-bottom: 15px;
    font-size: 14pt;
}

.benefits-list {
    list-style: none;
    padding-left: 0;
}

.benefits-list li {
    padding: 8px 0;
    position: relative;
    padding-left: 25px;
}

.benefits-list li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: var(--white);
    font-weight: bold;
    font-size: 12pt;
}

.tech-table, .cost-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    background: var(--white);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.tech-table th {
    background: var(--primary-color);
    color: var(--white);
    padding: 15px 12px;
    font-weight: 600;
    text-align: center;
    font-size: 11pt;
}

.tech-table td {
    padding: 12px;
    border-bottom: 1px solid var(--border-color);
    text-align: center;
    font-size: 10pt;
}

.tech-table tbody tr:nth-child(even) {
    background: var(--background-color);
}

.tech-table tbody tr:hover {
    background: var(--light-blue);
}

.finance-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-top: 20px;
}

.cost-breakdown, .roi-box {
    background: var(--white);
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    border: 1px solid var(--border-color);
}

.cost-breakdown h3, .roi-box h3 {
    color: var(--primary-color);
    margin-bottom: 15px;
    font-size: 14pt;
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 8px;
}

.cost-table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-color);
    font-size: 10pt;
}

.cost-value {
    text-align: right;
    font-weight: 600;
    color: var(--primary-color);
}

.cost-percent {
    text-align: center;
    color: var(--text-secondary);
}

.total-row {
    background: var(--background-color);
    border-top: 2px solid var(--primary-color);
}

.roi-box p {
    margin-bottom: 12px;
    line-height: 1.6;
}

.roi-highlight {
    background: var(--accent-color);
    color: var(--primary-color);
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 12pt;
    margin-top: 15px;
}

.environment-content {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 30px;
    align-items: start;
}

.co2-highlight {
    background: linear-gradient(135deg, var(--success-color) 0%, #32CD32 100%);
    color: var(--white);
    text-align: center;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.co2-value {
    font-size: 24pt;
    font-weight: 700;
    margin-bottom: 10px;
}

.co2-label {
    font-size: 11pt;
    opacity: 0.95;
}

.environment-facts {
    background: var(--white);
    padding: 25px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.environment-facts h3 {
    color: var(--success-color);
    margin-bottom: 15px;
    font-size: 13pt;
}

.environment-facts ul {
    list-style: none;
    padding-left: 0;
}

.environment-facts li {
    padding: 8px 0;
    position: relative;
    padding-left: 25px;
    line-height: 1.5;
}

.environment-facts li::before {
    content: '🌱';
    position: absolute;
    left: 0;
    font-size: 11pt;
}

.footer {
    margin-top: 50px;
    padding: 30px;
    background: linear-gradient(135deg, var(--dark-blue) 0%, var(--primary-color) 100%);
    color: var(--white);
    border-radius: 12px;
    text-align: center;
}

.footer-content p {
    margin-bottom: 8px;
}

.footer-note {
    font-style: italic;
    opacity: 0.9;
    margin-top: 15px;
    font-size: 10pt;
    line-height: 1.5;
}

/* Print-spezifische Stile */
@media print {
    body {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }
    
    .highlight-card:hover {
        transform: none;
    }
    
    .tech-table tbody tr:hover {
        background: var(--background-color);
    }
}

/* Responsive Anpassungen für kleinere PDFs */
@media (max-width: 595px) {
    .highlights-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .finance-grid {
        grid-template-columns: 1fr;
    }
    
    .environment-content {
        grid-template-columns: 1fr;
    }
    
    .info-grid {
        grid-template-columns: 1fr;
    }
}'''
        
        with open(os.path.join(self.css_dir, "premium_luxus.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
    
    def render_premium_pdf(self, angebot_daten: Dict) -> BytesIO:
        """
        Rendert ein Premium-PDF mit HTML+CSS
        
        Args:
            angebot_daten: Dictionary mit allen Angebotsdaten
            
        Returns:
            BytesIO: PDF als Bytes
        """
        if not _WEASYPRINT_AVAILABLE:
            raise Exception("WeasyPrint ist nicht verfügbar. Bitte installieren Sie es.")
        
        # Stelle sicher, dass Templates existieren
        self.create_templates()
        
        # Lade HTML Template
        template = self.env.get_template("premium_luxus.html")
        
        # Formatiere Zahlen für bessere Darstellung
        def format_number(value):
            if isinstance(value, (int, float)):
                return f"{value:,.0f}".replace(",", ".")
            return str(value)
        
        # Füge Filter hinzu
        self.env.filters['format_number'] = format_number
        
        # Rendere HTML mit Daten
        html_content = template.render(**angebot_daten)
        
        # CSS laden
        css_path = os.path.join(self.css_dir, "premium_luxus.css")
        
        # PDF erstellen
        pdf_bytes = BytesIO()
        
        try:
            html_doc = HTML(string=html_content, base_url=os.getcwd())
            
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as css_file:
                    css_content = css_file.read()
                css_doc = CSS(string=css_content)
                html_doc.write_pdf(pdf_bytes, stylesheets=[css_doc])
            else:
                html_doc.write_pdf(pdf_bytes)
                
        except Exception as e:
            # Fallback ohne externe CSS
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(pdf_bytes)
        
        pdf_bytes.seek(0)
        return pdf_bytes
    
    def prepare_angebot_data(self, offer_data: Dict, kunde_name: str = None) -> Dict:
        """
        Bereitet Angebotsdaten für HTML-Template vor
        
        Args:
            offer_data: Rohe Angebotsdaten
            kunde_name: Name des Kunden
            
        Returns:
            Dict: Formatierte Daten für Template
        """
        
        # Basis-Daten extrahieren
        angebot_daten = {
            # Kunden-Info
            'kunde_name': kunde_name or offer_data.get('customer', {}).get('name', 'Geschätzter Kunde'),
            'angebot_id': offer_data.get('offer_id', f'PV-{datetime.now().strftime("%Y%m%d")}-PREMIUM'),
            'datum': datetime.now().strftime('%d. %B %Y'),
            'gueltig_bis': (datetime.now().replace(day=datetime.now().day + 30)).strftime('%d. %B %Y'),
            
            # System-Daten
            'system_power': offer_data.get('gesamtleistung_kwp', 0),
            'annual_yield': offer_data.get('jahresertrag_kwh', 0),
            'total_cost': offer_data.get('gesamtkosten', 0),
            'annual_savings': offer_data.get('jaehrliche_einsparung', 0),
            'payback_time': offer_data.get('amortisationszeit_jahre', 0),
            'co2_savings': offer_data.get('co2_einsparung_kg_jahr', 0),
            
            # Komponenten
            'module_type': offer_data.get('modul_typ', 'Premium Mono-Si Module'),
            'module_count': offer_data.get('anzahl_module', 0),
            'module_power': offer_data.get('modul_leistung_wp', 400),
            'inverter_type': offer_data.get('wechselrichter_typ', 'Premium String-Wechselrichter'),
            'inverter_power': offer_data.get('wechselrichter_leistung_kw', 0),
            
            # Firmen-Info
            'firma_name': 'Solar Premium Solutions GmbH',
            'firma_adresse': 'Sonnenallee 123, 12345 Solarstadt',
            'firma_telefon': '+49 123 456789',
            'firma_email': 'info@solar-premium.de',
            'firma_logo': None,  # Base64 oder URL
            
            # Kosten-Breakdown
            'kosten_breakdown': [
                {
                    'name': 'Premium Solarmodule',
                    'betrag': offer_data.get('kosten_module', 0),
                    'anteil': round((offer_data.get('kosten_module', 0) / offer_data.get('gesamtkosten', 1)) * 100, 1)
                },
                {
                    'name': 'Premium Wechselrichter',
                    'betrag': offer_data.get('kosten_wechselrichter', 0),
                    'anteil': round((offer_data.get('kosten_wechselrichter', 0) / offer_data.get('gesamtkosten', 1)) * 100, 1)
                },
                {
                    'name': 'Montagesystem',
                    'betrag': offer_data.get('kosten_montage', 0),
                    'anteil': round((offer_data.get('kosten_montage', 0) / offer_data.get('gesamtkosten', 1)) * 100, 1)
                },
                {
                    'name': 'Installation & Service',
                    'betrag': offer_data.get('kosten_installation', 0),
                    'anteil': round((offer_data.get('kosten_installation', 0) / offer_data.get('gesamtkosten', 1)) * 100, 1)
                }
            ]
        }
        
        return angebot_daten

def create_html_pdf_from_data(offer_data: Dict, kunde_name: str = None, template_style: str = "premium_luxus") -> BytesIO:
    """
    Hauptfunktion zur Erstellung von HTML+CSS basierten PDFs
    
    Args:
        offer_data: Angebotsdaten
        kunde_name: Name des Kunden
        template_style: Stil des Templates
        
    Returns:
        BytesIO: PDF als Bytes
    """
    
    generator = HTMLPDFGenerator()
    angebot_daten = generator.prepare_angebot_data(offer_data, kunde_name)
    
    return generator.render_premium_pdf(angebot_daten)

# Streamlit Integration
def render_html_pdf_in_streamlit():
    """Rendert HTML-PDF Integration in Streamlit"""
    
    st.subheader("🌟 HTML+CSS Premium PDF Generator")
    st.info("Erstellt wirklich schöne PDFs mit modernem HTML+CSS Design und WeasyPrint!")
    
    if not _WEASYPRINT_AVAILABLE:
        st.error("❌ WeasyPrint ist nicht installiert. Bitte installieren Sie es mit:")
        st.code("pip install weasyprint")
        return
    
    # Beispiel-Daten für Demo
    beispiel_daten = {
        'gesamtleistung_kwp': 12.8,
        'jahresertrag_kwh': 13500,
        'gesamtkosten': 28900,
        'jaehrliche_einsparung': 2850,
        'amortisationszeit_jahre': 10.1,
        'co2_einsparung_kg_jahr': 6750,
        'anzahl_module': 32,
        'modul_leistung_wp': 400,
        'modul_typ': 'Premium Mono-Si 400Wp Module',
        'wechselrichter_typ': 'Premium String-Wechselrichter 12kW',
        'wechselrichter_leistung_kw': 12,
        'kosten_module': 15600,
        'kosten_wechselrichter': 4200,
        'kosten_montage': 3800,
        'kosten_installation': 5300
    }
    
    # Kunde eingeben
    kunde_name = st.text_input("Kundenname:", "Familie Mustermann")
    
    # Template-Stil auswählen
    template_styles = {
        'premium_luxus': '💎 Premium Luxus - Edles tiefblaues Design',
        'corporate_professional': '💼 Corporate Professional - Business Design',
        'modern_tech': '🚀 Modern Tech - Innovative Technologie',
        'solar_green': '🌿 Solar Green - Nachhaltiges grünes Design'
    }
    
    selected_style = st.selectbox(
        "Template-Stil wählen:",
        options=list(template_styles.keys()),
        format_func=lambda x: template_styles[x]
    )
    
    # PDF generieren
    if st.button("🎨 HTML+CSS Premium PDF erstellen", type="primary"):
        try:
            with st.spinner(f'Erstelle {template_styles[selected_style]} PDF...'):
                
                # PDF erstellen
                pdf_bytes = create_html_pdf_from_data(
                    offer_data=beispiel_daten,
                    kunde_name=kunde_name,
                    template_style=selected_style
                )
                
                if pdf_bytes:
                    st.success("🌟 HTML+CSS Premium PDF erfolgreich erstellt!")
                    
                    # Download-Button
                    st.download_button(
                        label=f"📥 {template_styles[selected_style]} PDF herunterladen",
                        data=pdf_bytes.getvalue(),
                        file_name=f"premium_html_{selected_style}_{kunde_name.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                    
                    # Erfolgs-Animation
                    st.balloons()
                    
                    # Features-Info
                    st.info(f"""
                    ✨ **HTML+CSS Premium Features:**
                    - Template: {template_styles[selected_style]}
                    - WeasyPrint Rendering Engine
                    - Jinja2 Template System
                    - Responsive CSS Design
                    - Hochwertige Typografie
                    - Professionelle Farbgestaltung
                    - Moderne Layout-Elemente
                    """)
                    
                else:
                    st.error("❌ PDF konnte nicht erstellt werden.")
                    
        except Exception as e:
            st.error(f"❌ Fehler bei HTML+CSS PDF Erstellung: {str(e)}")
            
            # Debug-Info
            if st.checkbox("🔧 Debug-Information anzeigen"):
                st.code(f"Fehler-Details: {str(e)}")
                st.code(f"WeasyPrint verfügbar: {_WEASYPRINT_AVAILABLE}")

if __name__ == "__main__":
    # Teste die HTML+CSS PDF-Generierung
    beispiel_daten = {
        'gesamtleistung_kwp': 12.8,
        'jahresertrag_kwh': 13500,
        'gesamtkosten': 28900,
        'jaehrliche_einsparung': 2850,
        'amortisationszeit_jahre': 10.1,
        'co2_einsparung_kg_jahr': 6750,
        'anzahl_module': 32,
        'modul_typ': 'Premium Mono-Si Module',
        'wechselrichter_typ': 'Premium Wechselrichter',
        'kosten_module': 15600,
        'kosten_wechselrichter': 4200,
        'kosten_montage': 3800,
        'kosten_installation': 5300
    }
    
    try:
        pdf_bytes = create_html_pdf_from_data(beispiel_daten, "Test Kunde")
        print("✅ HTML+CSS PDF erfolgreich erstellt!")
        
        # Speichere Test-PDF
        with open("test_html_premium.pdf", "wb") as f:
            f.write(pdf_bytes.getvalue())
        print("📄 Test-PDF gespeichert als: test_html_premium.pdf")
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
