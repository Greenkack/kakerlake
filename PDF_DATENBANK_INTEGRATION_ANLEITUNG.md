# PDF-Datenbankintegration - Vollständige Anleitung

## Übersicht

Das erweiterte PDF-System integriert jetzt vollständig mit der Datenbank und lädt automatisch:

- **Produktbilder** aus der `products.image_base64` Spalte
- **Produktdatenblätter** aus dem `product_datasheets` Verzeichnis
- **Firmendokumente** aus der `company_documents` Tabelle
- **Firmenlogos** aus der `companies.logo_base64` Spalte
- **Bildvorlagen** aus der `company_image_templates` Tabelle
- **Textvorlagen** aus der `company_text_templates` Tabelle

## Verwendung

### 1. Basis-Integration (erweiterte PDF-Generierung)

```python
from pdf_design_enhanced_modern import create_comprehensive_database_pdf

# Vollständige PDF mit allen Datenbankdaten
elements = create_comprehensive_database_pdf(
    project_data=project_data,
    analysis_results=analysis_results,
    active_company_id=1,
    enhancement_config={
        'enable_modern_design': True,
        'use_database_integration': True,
        'include_product_images': True,
        'include_company_docs': True,
        'include_datasheets': True,
        'color_scheme': 'premium_blue_modern'
    }
)
```

### 2. Einzelne Komponenten nutzen

#### Produktdaten mit Bildern laden
```python
from pdf_database_integration import create_pdf_data_manager

# Datenmanager erstellen
pdf_manager = create_pdf_data_manager()

# Vollständige Produktdaten laden
complete_dataset = pdf_manager.create_complete_pdf_dataset(
    project_data=project_data,
    company_id=1,
    include_product_images=True,
    include_company_docs=True,
    include_datasheets=True
)

# Statistiken anzeigen
stats = complete_dataset['data_statistics']
print(f"Produkte geladen: {stats['total_products']}")
print(f"Produktbilder verfügbar: {stats['products_with_images']}")
print(f"Datenblätter verfügbar: {stats['products_with_datasheets']}")
print(f"Firmendokumente: {stats['available_documents']}")
print(f"Content-Vollständigkeit: {complete_dataset['content_completeness']}%")
```

#### Nur Produktbilder laden
```python
# Einzelnes Produktbild als Base64
product_image = pdf_manager.get_product_image_as_base64(product_id=123)

# Firmenlogo laden
company_logo = pdf_manager.get_company_logo_as_base64(company_id=1)

# Produkt-Showcase erstellen
showcase_products = pdf_manager.create_product_showcase_data([123, 456, 789])
```

### 3. Spezielle PDF-Abschnitte

#### Produktdatenblatt-Anhang
```python
from pdf_design_enhanced_modern import create_product_datasheet_appendix

# Anhang mit allen Produktdatenblättern
datasheet_elements = create_product_datasheet_appendix(
    product_ids=[123, 456, 789]
)
```

#### Firmendokumente-Abschnitt
```python
from pdf_design_enhanced_modern import create_company_document_section

# Abschnitt mit Firmendokumenten
company_doc_elements = create_company_document_section(company_id=1)
```

## Datenbankstruktur (erforderlich)

### Produkttabelle
```sql
products:
- id (INTEGER PRIMARY KEY)
- model_name (TEXT)
- manufacturer (TEXT)  
- category (TEXT)
- description (TEXT)
- image_base64 (TEXT)           -- Produktbild als Base64
- datasheet_link_db_path (TEXT) -- Pfad zum Datenblatt
- price_euro (REAL)
- capacity_w (REAL)
- power_kw (REAL)
- efficiency_percent (REAL)
- warranty_years (INTEGER)
- length_m, width_m, weight_kg (REAL)
```

### Firmentabelle
```sql
companies:
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- logo_base64 (TEXT)           -- Firmenlogo als Base64
- street, zip_code, city (TEXT)
- phone, email, website (TEXT)
- pdf_footer_text (TEXT)
```

### Firmendokumente
```sql
company_documents:
- id (INTEGER PRIMARY KEY)
- company_id (INTEGER)
- document_type (TEXT)         -- 'certificate', 'warranty', 'brochure', etc.
- display_name (TEXT)
- absolute_file_path (TEXT)    -- Vollständiger Dateipfad
- uploaded_at (TEXT)
```

### Bildvorlagen
```sql
company_image_templates:
- id (INTEGER PRIMARY KEY)
- company_id (INTEGER)
- name (TEXT)
- template_type (TEXT)         -- 'title_image', 'installation_example', etc.
- file_path (TEXT)             -- Relativer Pfad zur Bilddatei
```

### Textvorlagen
```sql
company_text_templates:
- id (INTEGER PRIMARY KEY)
- company_id (INTEGER)
- name (TEXT)
- content (TEXT)
- template_type (TEXT)         -- 'offer_text', 'cover_letter', etc.
```

## Verzeichnisstruktur

```
data/
├── company_docs/              -- Firmendokumente und Bildvorlagen
│   ├── 1/                     -- Company ID 1
│   │   ├── documents/
│   │   └── images/
│   └── 2/                     -- Company ID 2
├── product_datasheets/        -- Produktdatenblätter
│   ├── pv_modules/
│   ├── inverters/
│   └── batteries/
└── database.db               -- SQLite-Datenbank
```

## Fehlerbehandlung

Das System ist robust konzipiert:

1. **Fehlende Bilder**: Platzhalter werden angezeigt
2. **Nicht verfügbare Datenblätter**: Info-Box mit Hinweis
3. **DB-Verbindungsfehler**: Fallback auf Content-System
4. **Fehlende Dokumente**: Status wird korrekt angezeigt

## Automatische Content-Vollständigkeit

Das System berechnet automatisch die Vollständigkeit der verfügbaren Inhalte:

- **Firmeninfo (20%)**: Logo, Kontaktdaten
- **Produktbilder (30%)**: Anteil Produkte mit Bildern
- **Firmendokumente (25%)**: Verfügbare Dokumente
- **Bildvorlagen (25%)**: Firmenspezifische Vorlagen

**Beispiel-Ausgabe:**
```
✅ PDF-Daten geladen: {
    'total_products': 5,
    'products_with_images': 4,
    'products_with_datasheets': 3,
    'total_documents': 8,
    'available_documents': 6,
    'image_templates_count': 12,
    'content_completeness': 87.5
}
```

## Integration in bestehende Systeme

### Streamlit-App Integration
```python
# In der Streamlit-App
if st.button("PDF mit Datenbankintegration erstellen"):
    try:
        # Vollständige PDF mit allen DB-Daten
        pdf_elements = create_comprehensive_database_pdf(
            project_data=st.session_state['project_data'],
            analysis_results=st.session_state['analysis_results'],
            active_company_id=st.session_state.get('active_company_id', 1)
        )
        
        # PDF generieren und anzeigen
        pdf_buffer = generate_pdf_from_elements(pdf_elements)
        st.download_button(
            label="📄 PDF mit Datenbankintegration herunterladen",
            data=pdf_buffer,
            file_name=f"solar_angebot_vollstaendig_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"Fehler bei PDF-Generierung: {e}")
        st.info("Fallback auf Standard-PDF ohne Datenbankintegration verfügbar.")
```

### Admin-Panel Integration
```python
# Übersicht verfügbarer Inhalte
def show_content_overview(company_id: int):
    pdf_manager = create_pdf_data_manager()
    
    # Lade Übersichtsdaten
    dataset = pdf_manager.create_complete_pdf_dataset(
        project_data={}, 
        company_id=company_id
    )
    
    st.metric("Content-Vollständigkeit", f"{dataset['content_completeness']}%")
    st.metric("Produktbilder", f"{dataset['data_statistics']['products_with_images']}")
    st.metric("Firmendokumente", f"{dataset['data_statistics']['available_documents']}")
```

## Performance-Optimierung

- **Bild-Caching**: Produktbilder werden beim ersten Laden gecacht
- **Lazy Loading**: Bilder werden nur bei Bedarf geladen
- **Datenbankverbindung**: Effiziente Verbindungsnutzung
- **Fehler-Resilience**: Graceful Degradation bei Fehlern

## Erweiterte Features

### Custom Color Schemes
```python
enhancement_config = {
    'color_scheme': 'solar_professional_enhanced',  # Grüne Farben für Solar
    'enable_modern_design': True,
    'use_database_integration': True
}
```

### Selective Content Loading
```python
# Nur bestimmte Inhalte laden
dataset = pdf_manager.create_complete_pdf_dataset(
    project_data=project_data,
    company_id=1,
    include_product_images=True,    # Produktbilder ja
    include_company_docs=False,     # Firmendokumente nein
    include_datasheets=True         # Datenblätter ja
)
```
