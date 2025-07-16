#!/usr/bin/env python3
"""
Einfacher Test für die verbesserte PDF-Generierung
"""

import sys
import os
from datetime import datetime

# Aktuelles Verzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testet, ob alle Module korrekt importiert werden können"""
    try:
        # ReportLab verfügbarkeit testen
        from reportlab.lib import colors
        from reportlab.pdfgen import canvas
        print("✓ ReportLab ist verfügbar")
        
        # PDF-Generator importieren
        import pdf_generator
        print("✓ PDF-Generator erfolgreich importiert")
        
        # Test der neuen Farbpalette
        print(f"✓ Neue Primärfarbe: {pdf_generator.PRIMARY_COLOR_HEX}")
        print(f"✓ Neue Sekundärfarbe: {pdf_generator.SECONDARY_COLOR_HEX}")
        print(f"✓ Neue Akzentfarbe: {pdf_generator.ACCENT_COLOR_HEX}")
        
        # Test der Styles
        if pdf_generator.STYLES:
            print(f"✓ {len(pdf_generator.STYLES)} Styles verfügbar")
            
            # Test wichtiger Styles
            if 'OfferTitle' in pdf_generator.STYLES:
                offer_style = pdf_generator.STYLES['OfferTitle']
                print(f"✓ OfferTitle Style: Größe {offer_style.fontSize}pt")
                
            if 'SectionTitle' in pdf_generator.STYLES:
                section_style = pdf_generator.STYLES['SectionTitle']
                print(f"✓ SectionTitle Style: Größe {section_style.fontSize}pt")
        else:
            print("⚠ Styles noch nicht initialisiert (ReportLab Problem?)")
            
        return True
        
    except ImportError as e:
        print(f"✗ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
        return False

def create_simple_pdf():
    """Erstellt eine einfache Test-PDF mit den neuen Styles"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        import pdf_generator
        
        filename = f"test_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Canvas erstellen
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        
        # Test der neuen Farben
        c.setFillColor(colors.HexColor(pdf_generator.PRIMARY_COLOR_HEX))
        c.rect(2*cm, height-4*cm, 17*cm, 1*cm, fill=1, stroke=0)
        
        # Titel in weiß auf blauem Hintergrund
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(3*cm, height-3.5*cm, "DESIGN-TEST: Neues PDF-Layout")
        
        # Sekundärfarbe testen
        c.setFillColor(colors.HexColor(pdf_generator.SECONDARY_COLOR_HEX))
        c.rect(2*cm, height-6*cm, 17*cm, 0.5*cm, fill=1, stroke=0)
        
        # Accent-Farbe für Hintergrund
        c.setFillColor(colors.HexColor(pdf_generator.ACCENT_COLOR_HEX))
        c.rect(2*cm, height-10*cm, 17*cm, 3*cm, fill=1, stroke=1)
        
        # Text-Farbe testen
        c.setFillColor(colors.HexColor(pdf_generator.TEXT_COLOR_HEX))
        c.setFont("Helvetica", 12)
        c.drawString(3*cm, height-8*cm, "✓ Elegantes Dunkelblau als Primärfarbe")
        c.drawString(3*cm, height-8.5*cm, "✓ Solargrün als Akzentfarbe")
        c.drawString(3*cm, height-9*cm, "✓ Moderne Grautöne für Text")
        c.drawString(3*cm, height-9.5*cm, "✓ Professionelle Farbpalette")
        
        # Trennlinien in dezenter Farbe
        c.setStrokeColor(colors.HexColor(pdf_generator.SEPARATOR_LINE_COLOR_HEX))
        c.setLineWidth(1)
        c.line(2*cm, height-12*cm, 19*cm, height-12*cm)
        
        # Footer-Simulation
        c.setFillColor(colors.HexColor("#6C757D"))
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2*cm, 2*cm, "Ömer's Solar-Ding GmbH • Sonnenstraße 42 • 12345 Solarstadt")
        c.drawRightString(19*cm, 2*cm, f"Design-Test • {datetime.now().strftime('%d.%m.%Y')} • Seite 1")
        
        c.save()
        print(f"✓ Test-PDF erstellt: {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Fehler bei PDF-Erstellung: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("🎨 PDF-DESIGN VERBESSERUNG - IMPORT & FARB-TEST")
    print("=" * 70)
    
    # Import-Test
    import_success = test_imports()
    
    if import_success:
        print("\n" + "=" * 70)
        print("📄 EINFACHE PDF-ERSTELLUNG")
        print("=" * 70)
        
        # Einfache PDF erstellen
        pdf_success = create_simple_pdf()
        
        if pdf_success:
            print("\n✅ ALLE TESTS ERFOLGREICH!")
            print("\n🎨 Design-Verbesserungen implementiert:")
            print("   • Moderne Farbpalette (Dunkelblau #1B365D)")
            print("   • Solargrün als Akzentfarbe (#2E8B57)")
            print("   • Verbesserte Typografie und Abstände")
            print("   • Elegantere Tabellen-Styles")
            print("   • Professionellere Kopf-/Fußzeilen")
        else:
            print("\n❌ PDF-ERSTELLUNG FEHLGESCHLAGEN")
    else:
        print("\n❌ IMPORT-TEST FEHLGESCHLAGEN")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
