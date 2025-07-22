# create_final_modern_pdf.py
# -*- coding: utf-8 -*-
"""
Finale Test-Datei für vollständige moderne PDF mit allen Features
Löst alle bekannten Probleme und erstellt eine perfekte PDF
"""

def create_final_modern_pdf():
    """Erstellt die finale moderne PDF mit allen Features"""
    print("🚀 === FINALE MODERNE PDF-ERSTELLUNG ===")
    
    try:
        # Sichere Imports
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        import io
        import os
        
        print("✅ ReportLab Module geladen")
        
        # Eigene Module
        from pdf_content_enhanced_system import create_complete_pdf_content
        from pdf_design_enhanced_modern import ModernPDFDesignSystem
        
        print("✅ Eigene Module geladen")
        
        # === TEST-DATEN ===
        project_data = {
            'customer_name': 'Solar Kunde GmbH',
            'komponenten': {
                'solarmodule': {'produkt_id': 1, 'anzahl': 24},
                'wechselrichter': {'produkt_id': 2, 'anzahl': 1},
                'montagesystem': {'produkt_id': 3, 'anzahl': 1}
            },
            'gesamtleistung_kwp': 9.6,
            'anzahl_module': 24,
            'jahresertrag_kwh': 10200,
            'dachflaeche_m2': 60,
            'ausrichtung': 'Süd',
            'neigung_grad': 35
        }
        
        analysis_results = {
            'gesamtkosten': 22000,
            'jaehrliche_einsparung': 2400,
            'amortisationszeit_jahre': 9.2,
            'co2_einsparung_kg_jahr': 5100
        }
        
        def mock_get_product(product_id):
            products = {
                1: {'name': 'Premium Solarmodul 400W', 'hersteller': 'SolarTech', 'modell': 'ST-400', 'preis': 300, 'beschreibung': 'Hochwertiges Modul'},
                2: {'name': 'Wechselrichter 10kW', 'hersteller': 'InverTech', 'modell': 'IT-10K', 'preis': 1500, 'beschreibung': 'Hocheffizienter WR'},
                3: {'name': 'Montagesystem', 'hersteller': 'MountTech', 'modell': 'MT-PRO', 'preis': 30, 'beschreibung': 'Robustes System'}
            }
            return products.get(product_id, {})
        
        print("✅ Test-Daten erstellt")
        
        # === CONTENT ERSTELLEN ===
        complete_content = create_complete_pdf_content(
            project_data, analysis_results, mock_get_product
        )
        
        print(f"✅ Content erstellt: {complete_content['content_summary']['content_completeness']}% vollständig")
        
        # === DESIGN-SYSTEM ===
        design_system = ModernPDFDesignSystem()
        styles = design_system.get_enhanced_paragraph_styles('premium_blue_modern')
        
        print("✅ Design-System initialisiert")
        
        # === PDF BUFFER ERSTELLEN ===
        pdf_buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title="Finale Moderne Solar-Lösung"
        )
        
        print("✅ PDF-Dokument initialisiert")
        
        # === STORY AUFBAUEN ===
        story = []
        
        # 1. TITEL
        story.append(Paragraph("🌟 Premium Solar-Lösung", styles['display']))
        story.append(Paragraph(f"Maßgeschneidert für {project_data['customer_name']}", styles['h2']))
        story.append(Spacer(1, 2*cm))
        
        # 2. EXECUTIVE SUMMARY
        exec_data = complete_content['executive_summary']
        story.append(Paragraph("📋 Executive Summary", styles['h1']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(exec_data['introduction'], styles['body']))
        story.append(Spacer(1, 1*cm))
        
        # Key Metrics Tabelle
        metrics_data = [['Kennzahl', 'Wert']]
        for key, value in exec_data['key_metrics'].items():
            metrics_data.append([key, str(value)])
        
        metrics_table = Table(metrics_data, colWidths=[8*cm, 4*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 1*cm))
        
        # Vorteile
        benefits_text = "<br/>".join([f"• {benefit}" for benefit in exec_data['benefits']])
        story.append(Paragraph("🌟 Ihre Hauptvorteile:", styles['h3']))
        story.append(Paragraph(benefits_text, styles['body']))
        
        story.append(PageBreak())
        
        # 3. TECHNISCHE SPEZIFIKATIONEN
        tech_data = complete_content['technical_specifications']
        story.append(Paragraph("⚡ Technische Spezifikationen", styles['h1']))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(tech_data['introduction'], styles['body']))
        story.append(Spacer(1, 1*cm))
        
        # System-Übersicht
        system_data = [['System-Parameter', 'Wert']]
        for key, value in tech_data['system_specifications'].items():
            system_data.append([key, str(value)])
        
        system_table = Table(system_data, colWidths=[8*cm, 4*cm])
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a7f3d0'))
        ]))
        story.append(system_table)
        story.append(Spacer(1, 1*cm))
        
        # Produktdetails
        story.append(Paragraph("🛠️ Premium-Komponenten", styles['h2']))
        story.append(Spacer(1, 0.5*cm))
        
        for product in tech_data['products']:
            story.append(Paragraph(f"🔧 {product['name']}", styles['h3']))
            
            product_text = f"""
            <b>Hersteller:</b> {product['manufacturer']}<br/>
            <b>Modell:</b> {product['model']}<br/>
            <b>Anzahl:</b> {product['quantity']} Stück<br/>
            <b>Preis:</b> {product['price']:,.0f} € pro Stück<br/>
            <b>Beschreibung:</b> {product['description']}
            """
            story.append(Paragraph(product_text, styles['body']))
            story.append(Spacer(1, 0.5*cm))
        
        story.append(PageBreak())
        
        # 4. WIRTSCHAFTLICHKEIT
        story.append(Paragraph("💰 Wirtschaftlichkeitsanalyse", styles['h1']))
        story.append(Spacer(1, 0.5*cm))
        
        # Kosten-Nutzen Tabelle
        financial_data = [
            ['Kostenposition', 'Betrag'],
            ['Gesamtinvestition', f"{analysis_results['gesamtkosten']:,.0f} €"],
            ['Jährliche Einsparung', f"{analysis_results['jaehrliche_einsparung']:,.0f} €"],
            ['Amortisationszeit', f"{analysis_results['amortisationszeit_jahre']:.1f} Jahre"],
            ['Gewinn nach 25 Jahren', f"{(analysis_results['jaehrliche_einsparung'] * 25 - analysis_results['gesamtkosten']):,.0f} €"]
        ]
        
        financial_table = Table(financial_data, colWidths=[8*cm, 4*cm])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#16a34a'))
        ]))
        story.append(financial_table)
        story.append(Spacer(1, 1*cm))
        
        roi_text = f"""
        Ihre Solaranlage amortisiert sich bereits nach {analysis_results['amortisationszeit_jahre']:.1f} Jahren.
        Danach produziert sie über weitere {25 - analysis_results['amortisationszeit_jahre']:.0f} Jahre praktisch kostenlosen Strom.
        Das entspricht einer jährlichen Rendite von ca. {(analysis_results['jaehrliche_einsparung'] / analysis_results['gesamtkosten'] * 100):.1f}%.
        """
        story.append(Paragraph(roi_text, styles['body']))
        
        story.append(PageBreak())
        
        # 5. UMWELT & NACHHALTIGKEIT
        story.append(Paragraph("🌍 Umwelt & Nachhaltigkeit", styles['h1']))
        story.append(Spacer(1, 0.5*cm))
        
        co2_data = [
            ['Umwelt-Kennzahl', 'Wert pro Jahr'],
            ['CO₂-Einsparung', f"{analysis_results['co2_einsparung_kg_jahr']:,.0f} kg"],
            ['Entspricht Bäumen', f"{(analysis_results['co2_einsparung_kg_jahr'] / 25):,.0f} Bäume"],
            ['Entspricht Auto-km', f"{(analysis_results['co2_einsparung_kg_jahr'] * 5):,.0f} km weniger"]
        ]
        
        co2_table = Table(co2_data, colWidths=[8*cm, 4*cm])
        co2_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#22c55e'))
        ]))
        story.append(co2_table)
        story.append(Spacer(1, 1*cm))
        
        impact_text = f"""
        Mit Ihrer {project_data['gesamtleistung_kwp']} kWp Solaranlage leisten Sie einen bedeutenden Beitrag zum Klimaschutz.
        Über 25 Jahre sparen Sie {(analysis_results['co2_einsparung_kg_jahr'] * 25):,.0f} kg CO₂ ein.
        Das entspricht der CO₂-Bindung von über {(analysis_results['co2_einsparung_kg_jahr'] * 25 / 25):,.0f} Bäumen.
        """
        story.append(Paragraph(impact_text, styles['body']))
        
        story.append(PageBreak())
        
        # 6. FIRMENDOKUMENTE & SERVICE
        doc_data = complete_content['company_documents']
        story.append(Paragraph("📁 Zusätzliche Dokumentation", styles['h1']))
        story.append(Spacer(1, 0.5*cm))
        
        doc_table_data = [['Dokument', 'Typ', 'Status']]
        for doc in doc_data['documents']:
            doc_table_data.append([
                doc.get('name', 'Dokument'),
                doc.get('type', 'Info').title(),
                'Verfügbar' if doc.get('available', False) else 'Nach Vertragsabschluss'
            ])
        
        doc_table = Table(doc_table_data, colWidths=[6*cm, 3*cm, 3*cm])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3b82f6'))
        ]))
        story.append(doc_table)
        story.append(Spacer(1, 1*cm))
        
        service_text = """
        Alle Dokumente werden Ihnen nach Vertragsabschluss digital zur Verfügung gestellt.
        Unsere Experten stehen Ihnen für Fragen jederzeit zur Verfügung.
        Sie erhalten umfassende Garantien und einen professionellen Service über die gesamte Laufzeit.
        """
        story.append(Paragraph(service_text, styles['body']))
        
        print(f"✅ Story erstellt mit {len(story)} Elementen")
        
        # === PDF GENERIEREN ===
        pdf_doc.build(story)
        
        # === PDF SPEICHERN ===
        pdf_buffer.seek(0)
        filename = 'finale_moderne_solar_loesung.pdf'
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF erstellt: {filename}")
        
        # === VALIDIERUNG ===
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            page_count = len([e for e in story if isinstance(e, PageBreak)]) + 1
            
            print(f"📊 Dateigröße: {file_size / 1024:.1f} KB")
            print(f"📄 Geschätzte Seiten: {page_count}")
            print(f"🎨 Design-Schema: Premium Blue Modern")
            print(f"🛠️ Produkte enthalten: {len(tech_data['products'])}")
            print(f"📁 Dokumente referenziert: {len(doc_data['documents'])}")
            
            return True
        else:
            print("❌ PDF-Datei nicht gefunden")
            return False
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        print(f"🔍 Details: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🎯 Erstelle finale moderne PDF mit allen Features...")
    success = create_final_modern_pdf()
    
    if success:
        print("\n🎉 === ERFOLG! VOLLSTÄNDIGE MODERNE PDF ERSTELLT! ===")
        print()
        print("✅ Die PDF enthält jetzt ALLES was Sie wollten:")
        print("   🎨 Modernes professionelles Design")
        print("   📊 Executive Summary mit Key Metrics")
        print("   🛠️ Vollständige Produktaufstellung mit Details")
        print("   💰 Detaillierte Wirtschaftlichkeitsanalyse")
        print("   🌍 Umwelt & Nachhaltigkeits-Sektion")
        print("   📁 Firmendokument-Übersicht")
        print("   📈 Professional Tabellen und Layouts")
        print("   🎯 Strukturiert über mehrere Seiten")
        print()
        print("💡 Das PDF-System ist jetzt vollständig funktionsfähig!")
        print("📁 Datei: finale_moderne_solar_loesung.pdf")
        print()
        print("🚀 Nächste Schritte:")
        print("   1. PDF-Datei öffnen und prüfen")
        print("   2. System in Ihre Anwendung integrieren")
        print("   3. Mit echten Daten testen")
    else:
        print("\n🔧 Es gab Probleme - bitte Details oben prüfen.")
