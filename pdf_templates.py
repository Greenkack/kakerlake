# pdf_templates.py
# -*- coding: utf-8 -*-
"""
pdf_templates.py

Zentralisiert alle textlichen Inhalte für wiederverwendbare PDF-Module wie
Anschreiben, Deckblätter oder Schlussseiten. Dies ermöglicht eine einfache
Anpassung von Inhalten ohne Änderung am Programmcode.

Author: Suratina Sicmislar
Version: 1.0 (AI-Generated & Modular)
"""

def get_cover_letter_template(customer_name: str, offer_id: str) -> str:
    """
    Gibt den formatierten Text für ein Standard-Anschreiben zurück.
    Verwendet Platzhalter, die vom PDF-Generator ersetzt werden.

    Args:
        customer_name (str): Der Name des Kunden.
        offer_id (str): Die Angebotsnummer.

    Returns:
        str: Der formatierte Anschreiben-Text.
    """
    
    text = f"""
Sehr geehrte Damen und Herren von {customer_name},

vielen Dank für Ihr Interesse an unseren Lösungen.

Anbei erhalten Sie unser detailliertes Angebot mit der Nummer **{offer_id}**, das speziell auf Ihre Bedürfnisse zugeschnitten ist. Wir haben alle Aspekte Ihrer Anfrage sorgfältig geprüft und eine Lösung konzipiert, die Ihnen maximale Effizienz und Wirtschaftlichkeit bietet.

Die folgenden Seiten geben Ihnen einen umfassenden Überblick über die vorgeschlagenen Komponenten, die zu erwartenden Einsparungen und die damit verbundenen Investitionskosten.

Für Rückfragen stehen wir Ihnen jederzeit gerne persönlich zur Verfügung.

Mit freundlichen Grüßen,

Ihr Team der Zukunft
"""
    return text.strip()


def get_project_summary_template() -> str:
    """Gibt den Text für eine Projektzusammenfassung zurück."""
    
    return """
**Zusammenfassung des Projekts**

Dieses Dokument beschreibt die Planung und Installation einer hochmodernen Photovoltaikanlage, optional erweitert um einen Energiespeicher und eine Wallbox für Elektromobilität. Unser Ziel ist es, Ihre Energieunabhängigkeit zu maximieren und Ihre Betriebskosten nachhaltig zu senken. Alle Komponenten sind von führenden Herstellern und garantieren höchste Qualität und Langlebigkeit.
"""

# Hier können beliebig viele weitere Textvorlagen hinzugefügt werden.
# z.B. für Datenschutzhinweise, technische Erläuterungen etc.