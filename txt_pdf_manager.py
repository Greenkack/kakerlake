"""
TXT-PDF Management Tool
Hilft bei der Verwaltung und Erstellung von TXT-Dateien für die PDF-Generierung

Autor: GitHub Copilot  
Datum: 28.07.2025
"""

import os
import glob
from typing import Dict, List, Optional, Tuple
import streamlit as st

def list_available_pages() -> List[int]:
    """
    Listet alle verfügbaren Seiten im input-Ordner auf
    
    Returns:
        List[int]: Sortierte Liste der verfügbaren Seitennummern
    """
    base_dir = os.getcwd()
    input_dir = os.path.join(base_dir, "input")
    
    if not os.path.exists(input_dir):
        return []
    
    # Finde alle seite_*_*.txt Dateien
    pattern = os.path.join(input_dir, "seite_*_*.txt")
    files = glob.glob(pattern)
    
    page_nums = set()
    for file in files:
        try:
            filename = os.path.basename(file)
            # Extrahiere Seitennummer aus seite_N_*.txt
            if filename.startswith("seite_"):
                parts = filename.split("_")
                if len(parts) >= 2:
                    page_num = int(parts[1])
                    page_nums.add(page_num)
        except (ValueError, IndexError):
            continue
    
    return sorted(list(page_nums))

def get_page_files(page_num: int) -> Dict[str, str]:
    """
    Gibt alle Dateien für eine bestimmte Seite zurück
    
    Args:
        page_num: Seitennummer
        
    Returns:
        Dict mit Dateityp als Key und Dateipfad als Value
    """
    base_dir = os.getcwd()
    input_dir = os.path.join(base_dir, "input")
    
    files = {}
    
    # Standarddateien für jede Seite
    file_types = [
        "texte", "formen", "details", "annotationen", "bilder_positionen"
    ]
    
    for file_type in file_types:
        file_path = os.path.join(input_dir, f"seite_{page_num}_{file_type}.txt")
        if os.path.exists(file_path):
            files[file_type] = file_path
    
    # Bildateien suchen
    image_extensions = ["png", "jpg", "jpeg", "tif", "tiff"]
    for ext in image_extensions:
        pattern = os.path.join(input_dir, f"seite_{page_num}_bild_*.{ext}")
        image_files = glob.glob(pattern)
        for img_file in image_files:
            # Extrahiere Bildnummer
            basename = os.path.basename(img_file)
            try:
                # seite_N_bild_M.ext -> M
                parts = basename.replace(f".{ext}", "").split("_")
                if len(parts) >= 4 and parts[2] == "bild":
                    img_num = parts[3]
                    files[f"bild_{img_num}"] = img_file
            except:
                continue
    
    return files

def show_txt_system_overview():
    """
    Zeigt eine Übersicht über das TXT-System in Streamlit
    """
    st.header("📄 TXT-PDF System Übersicht")
    
    pages = list_available_pages()
    
    if not pages:
        st.error("❌ Keine Seiten im input-Ordner gefunden!")
        return
    
    st.success(f"✅ {len(pages)} Seiten gefunden: {', '.join(map(str, pages))}")
    
    # Seiten-Details
    with st.expander("📋 Seiten-Details", expanded=False):
        for page_num in pages[:10]:  # Zeige erste 10 Seiten
            files = get_page_files(page_num)
            
            st.subheader(f"Seite {page_num}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**TXT-Dateien:**")
                txt_files = {k: v for k, v in files.items() if not k.startswith("bild_")}
                for file_type, file_path in txt_files.items():
                    st.text(f"✅ {file_type}.txt")
            
            with col2:
                st.write("**Bilder:**")
                img_files = {k: v for k, v in files.items() if k.startswith("bild_")}
                if img_files:
                    for img_key, img_path in img_files.items():
                        ext = os.path.splitext(img_path)[1]
                        st.text(f"🖼️ {img_key}{ext}")
                else:
                    st.text("Keine Bilder")
            
            st.markdown("---")

def create_missing_pages_template(target_pages: int = 20):
    """
    Erstellt Template-Dateien für fehlende Seiten
    
    Args:
        target_pages: Zielanzahl der Seiten (Standard: 20)
    """
    base_dir = os.getcwd()
    input_dir = os.path.join(base_dir, "input")
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"✅ Erstellt: {input_dir}")
    
    existing_pages = list_available_pages()
    missing_pages = [i for i in range(1, target_pages + 1) if i not in existing_pages]
    
    if not missing_pages:
        print(f"✅ Alle {target_pages} Seiten bereits vorhanden!")
        return
    
    # Template-Inhalte
    templates = {
        "texte": """Text: [Hauptüberschrift Seite {page_num}]
Position: (100, 750, 500, 780)
Schriftgröße: 16
Farbe: 0

----------------------------------------

Text: [Inhalt für Seite {page_num} - bitte anpassen]  
Position: (100, 700, 500, 730)
Schriftgröße: 12
Farbe: 0
""",
        
        "details": """Seitengröße: Rect(0.0, 0.0, 595.0, 842.0)
""",
        
        "formen": """# Keine Formen auf Seite {page_num}
""",
        
        "annotationen": """# Keine Annotationen auf Seite {page_num}
""",
        
        "bilder_positionen": """# Keine Bilder auf Seite {page_num}
"""
    }
    
    created_files = []
    
    for page_num in missing_pages:
        for file_type, template_content in templates.items():
            file_path = os.path.join(input_dir, f"seite_{page_num}_{file_type}.txt")
            
            content = template_content.format(page_num=page_num)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            created_files.append(file_path)
    
    print(f"✅ {len(created_files)} Template-Dateien erstellt für Seiten: {', '.join(map(str, missing_pages))}")
    return created_files

def validate_page_structure(page_num: int) -> Dict[str, bool]:
    """
    Validiert die Struktur einer Seite
    
    Args:
        page_num: Seitennummer
        
    Returns:
        Dict mit Validierungsresultaten
    """
    files = get_page_files(page_num)
    
    required_files = ["texte", "details", "formen", "annotationen", "bilder_positionen"]
    
    validation = {}
    for required in required_files:
        validation[f"{required}_exists"] = required in files
    
    # Prüfe ob details.txt Seitengröße enthält
    if "details" in files:
        try:
            with open(files["details"], 'r', encoding='utf-8') as f:
                content = f.read()
            validation["details_has_size"] = "Seitengröße:" in content and "Rect(" in content
        except:
            validation["details_has_size"] = False
    else:
        validation["details_has_size"] = False
    
    return validation

if __name__ == "__main__":  
    print("🧪 TXT-PDF Management Tool")
    print("=" * 40)
    
    pages = list_available_pages()
    print(f"Verfügbare Seiten: {pages}")
    
    if len(pages) < 20:
        print(f"⚠️ Nur {len(pages)} von 20 Seiten vorhanden")
        
        # Erstelle fehlende Seiten
        create_missing_pages_template(20)
        print("✅ Template-Seiten erstellt")
    
    # Validiere erste 5 Seiten
    print("\n📋 Struktur-Validierung (erste 5 Seiten):")
    for page_num in pages[:5]:
        validation = validate_page_structure(page_num)
        all_valid = all(validation.values())
        status = "✅" if all_valid else "⚠️"
        print(f"{status} Seite {page_num}: {sum(validation.values())}/{len(validation)} Checks")
