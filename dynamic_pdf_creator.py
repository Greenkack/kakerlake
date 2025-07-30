#!/usr/bin/env python3
"""
DYNAMISCHES PDF-ERSTELLUNGS-SYSTEM
==================================

Erstellt PDF direkt aus den dynamisch verarbeiteten TXT-Inhalten,
ohne externe Skripte oder Datei-Manipulation.
"""

import os
import sys
from typing import Dict, Any, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

class DynamicPDFCreator:
    """Erstellt PDF direkt aus dynamischen Text-Daten."""
    
    def __init__(self):
        self.setup_fonts()
        
    def setup_fonts(self):
        """Richtet verfügbare Schriftarten ein."""
        try:
            # Versuche System-Schriftarten zu laden
            if os.name == 'nt':  # Windows
                font_paths = [
                    'C:/Windows/Fonts/arial.ttf',
                    'C:/Windows/Fonts/calibri.ttf',
                ]
            else:  # Linux/Mac
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/System/Library/Fonts/Arial.ttf',
                ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_name = os.path.basename(font_path).split('.')[0]
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✅ Schriftart geladen: {font_name}")
                    break
        except Exception as e:
            print(f"⚠️ Schriftarten-Setup: {e} - verwende Standard-Schriftarten")
    
    def create_pdf_from_dynamic_texts(self, dynamic_texts: Dict[str, str]) -> bytes:
        """
        Erstellt PDF aus den dynamisch verarbeiteten TXT-Inhalten.
        
        Args:
            dynamic_texts: Dict mit Dateinamen als Keys und verarbeiteten Inhalten als Values
            
        Returns:
            bytes: PDF-Bytes
        """
        buffer = io.BytesIO()
        
        # PDF-Canvas erstellen
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        print(f"🔄 Erstelle PDF aus {len(dynamic_texts)} dynamischen Seiten...")
        
        # Sortiere Seiten nach Seitennummer
        sorted_files = sorted(dynamic_texts.keys(), key=self._extract_page_number)
        
        for page_num, filename in enumerate(sorted_files, 1):
            print(f"  📄 Verarbeite {filename}...")
            
            # Neue Seite (außer für erste Seite)
            if page_num > 1:
                c.showPage()
            
            # Text-Inhalt verarbeiten
            text_content = dynamic_texts[filename]
            self._render_page_content(c, text_content, width, height)
        
        # PDF abschließen
        c.save()
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        
        print(f"✅ PDF erfolgreich erstellt ({len(pdf_bytes)} bytes, {len(sorted_files)} Seiten)")
        return pdf_bytes
    
    def _extract_page_number(self, filename: str) -> int:
        """Extrahiert Seitennummer aus Dateiname."""
        import re
        match = re.search(r'seite_(\d+)_', filename)
        return int(match.group(1)) if match else 999
    
    def _render_page_content(self, canvas_obj, content: str, width: float, height: float):
        """Rendert den Inhalt einer Seite auf das PDF-Canvas."""
        lines = content.split('\n')
        
        current_text = None
        current_position = None
        current_font = None
        current_size = None
        current_color = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Text: '):
                current_text = line[6:]  # Entferne "Text: "
                
            elif line.startswith('Position: '):
                current_position = self._parse_position(line)
                
            elif line.startswith('Schriftart: '):
                current_font = line[12:]
                
            elif line.startswith('Schriftgröße: '):
                try:
                    current_size = float(line[14:])
                except ValueError:
                    current_size = 10.0
                    
            elif line.startswith('Farbe: '):
                current_color = self._parse_color(line[7:])
                
            elif line.startswith('---'):
                # Ende eines Text-Blocks - rendern
                if current_text and current_position and current_text.strip():
                    self._draw_text(
                        canvas_obj, current_text, current_position,
                        current_font, current_size, current_color
                    )
                
                # Reset für nächsten Block
                current_text = None
                current_position = None
                current_font = None  
                current_size = None
                current_color = None
    
    def _parse_position(self, position_line: str) -> tuple:
        """Parst Position aus Text-Zeile."""
        import re
        match = re.search(r'\\(([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+),\\s*([\\d.]+)\\)', position_line)
        if match:
            return tuple(float(x) for x in match.groups())
        return (50, 700, 550, 720)  # Fallback-Position
    
    def _parse_color(self, color_str: str) -> Color:
        """Konvertiert Farb-Integer zu ReportLab Color."""
        try:
            color_int = int(color_str)
            # RGB aus Integer extrahieren
            r = (color_int >> 16) & 255
            g = (color_int >> 8) & 255
            b = color_int & 255
            return Color(r/255.0, g/255.0, b/255.0)
        except:
            return Color(0.2, 0.2, 0.2)  # Fallback: Dunkelgrau
    
    def _draw_text(self, canvas_obj, text: str, position: tuple, font: str, size: float, color: Color):
        """Zeichnet Text auf das Canvas."""
        if not text.strip():
            return
        
        x1, y1, x2, y2 = position
        
        # Y-Koordinate für ReportLab umrechnen (unten statt oben)
        page_height = A4[1]
        y = page_height - y1 - (size or 10)
        
        # Schriftart setzen
        font_name = self._map_font_name(font)
        canvas_obj.setFont(font_name, size or 10)
        
        # Farbe setzen
        if color:
            canvas_obj.setFillColor(color)
        
        # Text zeichnen
        try:
            canvas_obj.drawString(x1, y, text)
        except Exception as e:
            print(f"⚠️ Text-Rendering Fehler: {e} - verwende Fallback")
            canvas_obj.drawString(x1, y, str(text).encode('utf-8', errors='ignore').decode('utf-8'))
    
    def _map_font_name(self, font: str) -> str:
        """Mappt Schriftart-Namen zu verfügbaren Schriftarten."""
        if not font:
            return 'Helvetica'
        
        font_lower = font.lower()
        
        if 'roboto' in font_lower or 'arial' in font_lower:
            return 'Helvetica'
        elif 'bold' in font_lower:
            return 'Helvetica-Bold'
        else:
            return 'Helvetica'


def create_dynamic_pdf(dynamic_texts: Dict[str, str]) -> bytes:
    """
    Hauptfunktion zum Erstellen eines PDFs aus dynamischen Texten.
    
    Args:
        dynamic_texts: Dict mit verarbeiteten TXT-Inhalten
        
    Returns:
        bytes: PDF-Bytes
    """
    creator = DynamicPDFCreator()
    return creator.create_pdf_from_dynamic_texts(dynamic_texts)


if __name__ == "__main__":
    # Test mit Beispiel-Daten
    test_texts = {
        "seite_1_texte.txt": """Text: TEST KUNDE
Position: (100, 100, 200, 120)
Schriftart: Helvetica
Schriftgröße: 12.0
Farbe: 0
----------------------------------------"""
    }
    
    pdf_bytes = create_dynamic_pdf(test_texts)
    print(f"Test-PDF erstellt: {len(pdf_bytes)} bytes")
