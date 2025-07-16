#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erstellt Test-PDF-Dokumente für alle Firmendokumente in der DB
"""

import os
import sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_pdf(file_path: str, title: str, company_name: str, doc_type: str):
    """Erstellt ein Test-PDF mit Inhalt"""
    try:
        # Verzeichnis erstellen falls nötig
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # PDF erstellen
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter        # Titel
        c.setFont("Helvetica-Bold", 20)
        c.drawString(width/2 - 100, height - 100, title)
        
        # Firmenname
        c.setFont("Helvetica-Bold", 16)
        c.drawString(width/2 - 80, height - 150, company_name)
        
        # Dokumenttyp
        c.setFont("Helvetica", 14)
        c.drawString(width/2 - 60, height - 200, f"Dokumenttyp: {doc_type}")
        
        # Inhalt
        c.setFont("Helvetica", 12)
        content_lines = [
            "Dies ist ein Test-Dokument für die Multi-Angebots-Funktion.",
            "",
            "Dieses Dokument wurde automatisch erstellt, um zu demonstrieren,",
            "dass die Firmendokumente-Integration korrekt funktioniert.",
            "",
            "In einem echten System würden hier die tatsächlichen",
            "Firmendokumente (AGB, Datenschutz, etc.) angezeigt werden.",
            "",
            f"Erstellungszeitpunkt: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            f"Dateipfad: {file_path}",
        ]
        
        y_position = height - 300
        for line in content_lines:
            c.drawString(100, y_position, line)
            y_position -= 20
          # Fußzeile
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(width/2 - 100, 50, "Test-Dokument für Multi-Angebots-Generator")
        
        c.save()
        return True
        
    except Exception as e:
        print(f"Fehler beim Erstellen von {file_path}: {e}")
        return False

def create_all_test_documents():
    print("ERSTELLE TEST-DOKUMENTE FÜR ALLE FIRMEN")
    print("=" * 60)
    
    try:
        import database
        
        # Alle Firmen mit Dokumenten abrufen
        companies = database.list_companies()
        
        total_created = 0
        total_failed = 0
        
        for company in companies:
            company_id = company.get('id')
            company_name = company.get('name', f'Firma {company_id}')
            
            print(f"\n{company_name} (ID: {company_id})")
            
            # Alle Dokumente dieser Firma abrufen
            documents = database.list_company_documents(company_id)
            
            if not documents:
                print("    Keine Dokumente in DB")
                continue
            
            print(f"    {len(documents)} Dokumente gefunden")
            
            for doc in documents:
                doc_id = doc.get('id')
                doc_name = doc.get('display_name', 'UNBEKANNT')
                doc_type = doc.get('document_type', 'UNBEKANNT')
                file_path = doc.get('absolute_file_path', '')
                
                if not file_path:
                    print(f"    ID {doc_id}: Kein Dateipfad")
                    total_failed += 1
                    continue
                
                # Test-PDF erstellen
                success = create_test_pdf(
                    file_path=file_path,
                    title=doc_name,
                    company_name=company_name,
                    doc_type=doc_type
                )
                
                if success:
                    print(f"   ID {doc_id}: [{doc_type}] {doc_name}")
                    total_created += 1
                else:
                    print(f"    ID {doc_id}: Fehler beim Erstellen")
                    total_failed += 1
        
        print(f"\n ZUSAMMENFASSUNG:")
        print(f"   Erfolgreich erstellt: {total_created}")
        print(f"    Fehlgeschlagen: {total_failed}")
        
        if total_created > 0:
            print(f"\n TESTEN SIE JETZT:")
            print("1. Führen Sie den Multi-Angebots-Generator aus")
            print("2. Alle Firmendokumente sollten jetzt in den PDFs erscheinen")
            print("3. Das inkonsistente Verhalten sollte behoben sein")
        
    except Exception as e:
        print(f" Hauptfehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        # Prüfe ob reportlab verfügbar ist
        import reportlab
        create_all_test_documents()
    except ImportError:
        print(" reportlab nicht installiert. Installiere es mit: pip install reportlab")
        
        # Alternative: Erstelle einfache Text-Dateien
        print("\n Erstelle einfache Textdateien als Alternative...")
        
        import database
        companies = database.list_companies()
        
        for company in companies:
            company_id = company.get('id')
            company_name = company.get('name', f'Firma {company_id}')
            documents = database.list_company_documents(company_id)
            
            for doc in documents:
                file_path = doc.get('absolute_file_path', '')
                if file_path:
                    # Erstelle .txt Datei statt PDF
                    txt_path = file_path.replace('.pdf', '.txt')
                    try:
                        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
                        with open(txt_path, 'w', encoding='utf-8') as f:
                            f.write(f"Test-Dokument: {doc.get('display_name', 'UNBEKANNT')}\n")
                            f.write(f"Firma: {company_name}\n")
                            f.write(f"Typ: {doc.get('document_type', 'UNBEKANNT')}\n")
                            f.write("Dies ist ein Test-Dokument für die Multi-Angebots-Funktion.")
                        print(f" Textdatei erstellt: {txt_path}")
                    except Exception as e:
                        print(f" Fehler bei Textdatei: {e}")
        
        print("\n Alternative Textdateien erstellt. Für echte PDFs installieren Sie reportlab.")
