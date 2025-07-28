# weasyprint_installation.md
# WeasyPrint Installation Guide

## WeasyPrint + Jinja2 für schöne PDF-Templates

### 🚀 Installation

```bash
# Hauptkomponenten installieren
pip install weasyprint jinja2

# Zusätzliche Abhängigkeiten (falls nötig)
pip install cffi cairocffi

# Für Windows (falls GTK fehlt):
pip install --only-binary=weasyprint weasyprint
```

### ⚠️ Windows Troubleshooting

Falls WeasyPrint nicht installiert werden kann:

1. **GTK für Windows installieren:**
   - Download: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   - Oder verwende conda: `conda install -c conda-forge weasyprint`

2. **Alternative: Verwende Docker:**
   ```bash
   docker pull weasyprint/weasyprint
   ```

3. **Fallback: Verwende Online-Service:**
   - API-basierte PDF-Generierung mit HTML/CSS

### 🎨 Warum HTML+CSS für PDFs?

| Vorteil | Beschreibung |
|---------|--------------|
| **Design-Flexibilität** | Moderne CSS3-Features, Gradienten, Schatten |
| **Responsive Design** | Layouts passen sich an verschiedene Seitengrößen an |
| **Webentwickler-freundlich** | Bekannte HTML/CSS-Syntax |
| **Template-System** | Jinja2 für dynamische Inhalte |
| **Wartbarkeit** | Trennung von Design (CSS) und Logik (Python) |
| **Pixel-perfekt** | Exakte Kontrolle über Layout und Typografie |

### 📊 Vergleich: ReportLab vs. HTML+CSS

| Feature | ReportLab | HTML+CSS (WeasyPrint) |
|---------|-----------|------------------------|
| **Lernkurve** | Steiler | Flacher (bekannte Technologien) |
| **Design-Flexibilität** | Mittel | Hoch |
| **Performance** | Sehr schnell | Schnell |
| **Wartbarkeit** | Schwieriger | Einfacher |
| **Templates** | Programmiert | Deklarativ |
| **Responsive** | Nein | Ja |

### 🛠️ Verwendung in der App

```python
# 1. Import
from pdf_html_generator import create_html_pdf_from_data

# 2. Daten vorbereiten
angebot_daten = {
    'kunde_name': 'Familie Mustermann',
    'system_power': 12.8,
    'total_cost': 28900,
    # ... weitere Daten
}

# 3. PDF erstellen
pdf_bytes = create_html_pdf_from_data(
    offer_data=angebot_daten,
    kunde_name='Familie Mustermann',
    template_style='premium_luxus'
)

# 4. Download anbieten
st.download_button(
    label="📥 Premium PDF herunterladen",
    data=pdf_bytes.getvalue(),
    file_name="premium_angebot.pdf",
    mime="application/pdf"
)
```

### 🎨 Template-Struktur

```
pdf_templates_html/
├── premium_luxus.html       # Luxus-Design
├── corporate_professional.html  # Business-Design
├── modern_tech.html         # Tech-Design
└── solar_green.html         # Nachhaltigkeits-Design

pdf_styles_css/
├── premium_luxus.css        # Luxus-Styles
├── corporate_professional.css   # Business-Styles
├── modern_tech.css          # Tech-Styles
└── solar_green.css          # Nachhaltigkeits-Styles
```

### 🔧 Template-Anpassung

1. **HTML editieren:**
   ```html
   <!-- Neue Sektion hinzufügen -->
   <div class="custom-section">
       <h2>{{ custom_title }}</h2>
       <p>{{ custom_content }}</p>
   </div>
   ```

2. **CSS anpassen:**
   ```css
   .custom-section {
       background: linear-gradient(135deg, #ff6b6b, #feca57);
       padding: 20px;
       border-radius: 10px;
   }
   ```

3. **Python-Daten erweitern:**
   ```python
   angebot_daten.update({
       'custom_title': 'Meine neue Sektion',
       'custom_content': 'Individueller Inhalt...'
   })
   ```

### 🌟 Design-Features

- **CSS3 Gradienten:** Moderne Farbverläufe
- **Box-Shadow:** Schatten-Effekte für Tiefe
- **Border-Radius:** Abgerundete Ecken
- **Grid/Flexbox:** Moderne Layout-Systeme
- **Custom Fonts:** Google Fonts Integration
- **Icons:** Emoji oder SVG-Icons
- **Responsive Tables:** Automatische Anpassung

### 📱 Responsive Design

```css
/* Desktop */
.highlights-grid {
    grid-template-columns: repeat(3, 1fr);
}

/* Tablet */
@media (max-width: 768px) {
    .highlights-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Mobile */
@media (max-width: 480px) {
    .highlights-grid {
        grid-template-columns: 1fr;
    }
}
```

### 🚀 Performance-Tipps

1. **CSS optimieren:** Inline-Styles vermeiden
2. **Bilder komprimieren:** WebP oder optimierte PNGs
3. **Font-Loading:** Lokale Fonts bevorzugen
4. **Template-Caching:** Jinja2 Templates cachen
5. **PDF-Caching:** Generierte PDFs temporär speichern

### 🔍 Debugging

```python
# HTML-Output debuggen
html_content = template.render(**angebot_daten)
with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# CSS-Probleme finden
import weasyprint
html = weasyprint.HTML(string=html_content)
html.write_pdf('debug.pdf')
```

### 📈 Erweiterte Features

1. **Mehrsprachigkeit:** i18n mit Jinja2
2. **Bedingte Inhalte:** {% if %} Statements
3. **Schleifen:** {% for %} für dynamische Listen
4. **Makros:** Wiederverwendbare Template-Teile
5. **Include:** Template-Vererbung
6. **Custom Filters:** Python-Funktionen in Templates

Diese HTML+CSS-Lösung bietet maximale Flexibilität für schöne, professionelle PDFs!
