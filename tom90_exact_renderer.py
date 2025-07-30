"""
TOM-90 Exact Layout Renderer
============================

Dieser Renderer implementiert die exakte Layout-Struktur der TOM-90 PDF-Vorlage
basierend auf den analysierten txt-Dateien aus dem input-Ordner.

Jede Seite wird pixel-genau nachgebaut, aber mit dynamischen Inhalten gefüllt.
"""

import fitz
import os
import io
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import base64
import glob
import re
import ast


class TOM90ExactRenderer:
    """Exakter TOM-90 Layout Renderer basierend auf der Original-Vorlage."""

    def __init__(
        self,
        project_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        company_info: Dict[str, Any],
        inclusion_options: Optional[Dict[str, Any]] = None,
        texts: Optional[Dict[str, str]] = None,
        company_logo_base64: Optional[str] = None,
    ) -> None:
        self.project_data = project_data or {}
        self.analysis_results = analysis_results or {}
        self.company_info = company_info or {}
        self.inclusion_options = inclusion_options or {}
        self.texts = texts or {}
        self.company_logo_base64 = company_logo_base64

        # Pfad zum input-Verzeichnis mit den analysierten Daten
        self.input_dir = os.path.join(os.getcwd(), "input")

        # TOM-90 Farben (aus den analysierten Daten)
        self.tom90_blue = 0x353D96  # 3487029 in decimal
        self.tom90_orange = 0x0D3780  # Für Preise/Highlights
        self.tom90_white = 0xFFFFFF
        self.tom90_black = 0x000000

        # Standard Seiten-Dimensionen (wie in Original)
        self.page_width = 594.9599609375
        self.page_height = 841.9199829101562



    def _rgb_from_int(self, color_int: int) -> Tuple[float, float, float]:
        """Konvertiert Integer-Farbe zu RGB-Tupel (0-1)."""
        r = ((color_int >> 16) & 255) / 255.0
        g = ((color_int >> 8) & 255) / 255.0
        b = (color_int & 255) / 255.0
        return (r, g, b)

    def _format_currency(self, value: float, suffix: str = "EUR") -> str:
        """Formatiert Währungsbeträge."""
        return f"{value:,.0f} {suffix}".replace(",", ".")

    def _load_page_data(self, page_num: int) -> Dict[str, Any]:
        """Lädt alle Daten für eine spezifische Seite aus den txt-Dateien."""
        page_data = {"texts": [], "images": [], "shapes": [], "annotations": []}

        # Texte laden
        txt_path = os.path.join(self.input_dir, f"seite_{page_num}_texte.txt")
        if os.path.exists(txt_path):
            with open(txt_path, encoding="utf-8") as f:
                content = f.read()
                for block in content.split("-" * 40):
                    lines = [l for l in block.splitlines() if l.strip()]
                    text_data = {}
                    for line in lines:
                        if line.startswith("Text:"):
                            text_data["text"] = line.split("Text:", 1)[1].strip()
                        elif line.startswith("Position:"):
                            text_data["bbox"] = ast.literal_eval(
                                line.split("Position:", 1)[1].strip()
                            )
                        elif line.startswith("Schriftgröße:"):
                            text_data["size"] = float(
                                line.split("Schriftgröße:", 1)[1].strip()
                            )
                        elif line.startswith("Farbe:"):
                            text_data["color"] = int(line.split("Farbe:", 1)[1].strip())
                        elif line.startswith("Schriftart:"):
                            text_data["font"] = line.split("Schriftart:", 1)[1].strip()

                    if "text" in text_data and "bbox" in text_data:
                        page_data["texts"].append(text_data)

        # … innerhalb der PDF-Erstellung im TXT-System …


        # Bilder laden
        img_path = os.path.join(
            self.input_dir, f"seite_{page_num}_bilder_positionen.txt"
        )
        if os.path.exists(img_path):
            with open(img_path, encoding="utf-8") as f:
                for line in f:
                    match = re.match(r"Bild (\d+): Rect\(([^)]+)\)", line)
                    if match:
                        idx, coords = match.group(1), match.group(2)
                        bbox = ast.literal_eval(f"({coords})")

                        # Suche nach Bilddatei
                        img_file = None
                        for ext in ("png", "jpg", "jpeg", "tif", "tiff"):
                            candidate = os.path.join(
                                self.input_dir, f"seite_{page_num}_bild_{idx}.{ext}"
                            )
                            if os.path.exists(candidate):
                                img_file = candidate
                                break

                        if img_file:
                            page_data["images"].append({"bbox": bbox, "file": img_file})

        # Formen laden
        forms_path = os.path.join(self.input_dir, f"seite_{page_num}_formen.txt")
        if os.path.exists(forms_path):
            with open(forms_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("Linie von"):
                        pts = re.findall(r"\(([^,]+), ([^)]+)\)", line)
                        if len(pts) >= 2:
                            p1 = tuple(map(float, pts[0]))
                            p2 = tuple(map(float, pts[1]))
                            page_data["shapes"].append(
                                {"type": "line", "points": [p1, p2]}
                            )
                    elif line.startswith("Rechteck:"):
                        match = re.search(r"Rect\(([^)]+)\)", line)
                        if match:
                            vals = [float(v) for v in match.group(1).split(",")]
                            page_data["shapes"].append({"type": "rect", "bbox": vals})
                    elif line.startswith("Bezier-Kurve:"):
                        pts = re.findall(r"Point\(([^)]+)\)", line)
                        if len(pts) == 4:
                            points = [tuple(map(float, pt.split(", "))) for pt in pts]
                            page_data["shapes"].append(
                                {"type": "bezier", "points": points}
                            )

        return page_data

    def _substitute_dynamic_content(self, text: str, page_num: int) -> str:
        """Ersetzt statische Texte durch dynamische Inhalte und verarbeitet Keys."""

        # 1. DIREKTE KEY-ERSETZUNG (für txt-Dateien mit Keys)
        if "{" in text and "}" in text:
            return self._process_template_keys(text)

        # 2. LEGACY-ERSETZUNG (für bestehende statische Texte)

        # Kundendaten - Name und Anschrift
        if "Sehr geehrte" in text or "Kunde" in text:
            customer_name = self.project_data.get(
                "customer_name", "Sehr geehrte Kundin, sehr geehrter Kunde"
            )
            return customer_name

        # Kundenadresse ersetzen
        if any(
            addr_part in text for addr_part in ["Musterstraße", "12345", "Musterstadt"]
        ):
            address = self.project_data.get("customer_address", {})
            if isinstance(address, dict):
                street = address.get("street", "Musterstraße 1")
                city = address.get("city", "12345 Musterstadt")
                return f"{street}, {city}"
            else:
                return str(address) if address else text

        # Firmenname dynamisch
        if "TommaTech" in text and not "@" in text and not "GmbH" in text:
            return self.company_info.get("name", "TommaTech")

        # Vollständiger Firmenname mit Rechtsform
        if "TommaTech GmbH" in text:
            company_name = self.company_info.get("name", "TommaTech")
            legal_form = self.company_info.get("legal_form", "GmbH")
            return f"{company_name} {legal_form}"

        # Kontakt-Informationen
        if "mail@tommatech.de" in text:
            return self.company_info.get("email", "mail@tommatech.de")

        if "+49 89 1250 36 860" in text:
            return self.company_info.get("phone", "+49 89 1250 36 860")

        # Firmenadresse
        if any(addr in text for addr in ["Maximilianstraße", "München", "80539"]):
            company_address = self.company_info.get("address", {})
            if isinstance(company_address, dict):
                street = company_address.get("street", "Maximilianstraße 35")
                city = company_address.get("city", "80539 München")
                return f"{street}, {city}"
            else:
                return str(company_address) if company_address else text

        # Ersparnis-Werte
        if "36.958,00 EUR" in text or "36958" in text:
            savings_with = self.analysis_results.get(
                "total_savings_with_storage_eur", 36958
            )
            return self._format_currency(savings_with) + "*"

        if "29.150,00 EUR" in text or "29150" in text:
            savings_without = self.analysis_results.get(
                "total_savings_without_storage_eur", 29150
            )
            return self._format_currency(savings_without) + "*"

        # Anlagen-Daten
        if "8,4" in text and "kWp" in text:
            anlage_kwp = self.analysis_results.get("anlage_kwp", 8.4)
            return f"{anlage_kwp} kWp"

        if "6,1" in text and "kWh" in text:
            battery_capacity = self.project_data.get("battery_details", {}).get(
                "capacity_kwh", 6.1
            )
            return f"{battery_capacity} kWh"

        if "8.251,92" in text and "kWh/Jahr" in text:
            annual_production = self.analysis_results.get(
                "annual_pv_production_kwh", 8251.92
            )
            return f"{annual_production:,.2f} kWh/Jahr".replace(",", ".")

        if "6.000" in text and "kWh/Jahr" in text:
            annual_consumption = self.project_data.get("annual_consumption_kwh", 6000)
            return f"{annual_consumption:,.0f} kWh/Jahr".replace(",", ".")

        # Dachneigung
        if "30°" in text:
            roof_angle = self.project_data.get("roof_details", {}).get("angle", 30)
            return f"{roof_angle}°"

        # Module-Anzahl
        if "21" in text and "Module" in text:
            module_count = self.project_data.get("pv_details", {}).get(
                "module_quantity", 21
            )
            return f"{module_count} PV-Module"

        # Unabhängigkeitsgrad und Eigenverbrauch
        if "54%" in text and "Unabhängigkeit" in text:
            independence = self.analysis_results.get("independence_degree_percent", 54)
            return f"{independence}%"

        if "42%" in text and "Eigenverbrauch" in text:
            self_consumption = self.analysis_results.get("self_consumption_percent", 42)
            return f"{self_consumption}%"

        # CO2-Daten
        if "15.266" in text and "km" in text:
            co2_savings_kg = self.analysis_results.get("annual_co2_savings_kg", 3500)
            km_equivalent = co2_savings_kg / 0.12 if co2_savings_kg else 15266
            return f"{km_equivalent:,.0f} km".replace(",", ".")

        # Datum dynamisch
        if "29.11.2024" in text:
            current_date = datetime.now().strftime("%d.%m.%Y")
            return current_date

        # Angebotsnummer/Projektnummer
        if "tom-90" in text and len(text) < 10:
            project_id = self.project_data.get("project_id", "tom-90")
            return project_id

        # Standardrückgabe für unveränderte Texte
        return text

    def _process_template_keys(self, template_text: str) -> str:
        """Verarbeitet Template-Keys in geschweiften Klammern {}"""
        import re

        def replace_key(match):
            key = match.group(1)
            return self._get_value_for_key(key)

        # Ersetzt alle {key} Patterns
        return re.sub(r"\{([^}]+)\}", replace_key, template_text)

    def _get_value_for_key(self, key: str) -> str:
        """Gibt den Wert für einen spezifischen Key zurück"""

        # KUNDENDATEN
        if key == "customer_name":
            return self.project_data.get("customer_name", "Kunde")
        elif key == "customer_address_street":
            address = self.project_data.get("customer_address", {})
            return (
                address.get("street", "Musterstraße 1")
                if isinstance(address, dict)
                else str(address)
            )
        elif key == "customer_address_city":
            address = self.project_data.get("customer_address", {})
            return (
                address.get("city", "12345 Musterstadt")
                if isinstance(address, dict)
                else ""
            )

        # FIRMENDATEN
        elif key == "company_name":
            return self.company_info.get("name", "TommaTech")
        elif key == "company_email":
            return self.company_info.get("email", "mail@tommatech.de")
        elif key == "company_phone":
            return self.company_info.get("phone", "+49 89 1250 36 860")
        elif key == "company_website":
            return self.company_info.get("website", "www.tommatech.de")
        elif key == "company_tax_id":
            return self.company_info.get("tax_id", "DE354973606")
        elif key == "company_address_street":
            company_address = self.company_info.get("address", {})
            return (
                company_address.get("street", "Maximilianstraße 35")
                if isinstance(company_address, dict)
                else ""
            )
        elif key == "company_address_city":
            company_address = self.company_info.get("address", {})
            return (
                company_address.get("city", "80539 München")
                if isinstance(company_address, dict)
                else ""
            )

        # FINANZIELLE ERGEBNISSE
        elif key == "total_savings_with_storage_eur":
            savings = self.analysis_results.get("total_savings_with_storage_eur", 36958)
            return f"{savings:,.0f}".replace(",", ".")
        elif key == "total_savings_with_storage_eur_formatted":
            savings = self.analysis_results.get("total_savings_with_storage_eur", 36958)
            return self._format_currency(savings)
        elif key == "total_savings_without_storage_eur":
            savings = self.analysis_results.get(
                "total_savings_without_storage_eur", 29150
            )
            return f"{savings:,.0f}".replace(",", ".")
        elif key == "total_savings_without_storage_eur_formatted":
            savings = self.analysis_results.get(
                "total_savings_without_storage_eur", 29150
            )
            return self._format_currency(savings)

        # TECHNISCHE DATEN
        elif key == "anlage_kwp":
            return str(self.analysis_results.get("anlage_kwp", 8.4))
        elif key == "battery_capacity_kwh":
            return str(
                self.project_data.get("battery_details", {}).get("capacity_kwh", 6.1)
            )
        elif key == "annual_pv_production_kwh":
            production = self.analysis_results.get("annual_pv_production_kwh", 8251.92)
            return f"{production:,.2f}".replace(",", ".")
        elif key == "annual_consumption_kwh":
            consumption = self.project_data.get("annual_consumption_kwh", 6000)
            return f"{consumption:,.0f}".replace(",", ".")
        elif key == "module_quantity":
            return str(
                self.project_data.get("pv_details", {}).get("module_quantity", 21)
            )
        elif key == "roof_angle":
            return str(self.project_data.get("roof_details", {}).get("angle", 30))

        # PROZENTSÄTZE
        elif key == "independence_degree_percent":
            return f"{self.analysis_results.get('independence_degree_percent', 54)}%"
        elif key == "self_consumption_percent":
            return f"{self.analysis_results.get('self_consumption_percent', 42)}%"

        # UMWELTDATEN
        elif key == "co2_savings_km_equivalent":
            co2_savings_kg = self.analysis_results.get("annual_co2_savings_kg", 3500)
            km_equivalent = co2_savings_kg / 0.12 if co2_savings_kg else 15266
            return f"{km_equivalent:,.0f}".replace(",", ".")

        # DATUM UND PROJEKT
        elif key == "current_date":
            return datetime.now().strftime("%d.%m.%Y")
        elif key == "project_id":
            return self.project_data.get("project_id", "TOM-90")

        elif key == "salutation":
            return self.project_data.get("salutation", "")
        elif key == "first_name":
            return self.project_data.get("first_name", "")
        elif key == "last_name":
            return self.project_data.get("last_name", "")
        elif key == "house_number":
            addr = (
                self.project_data.get("customer_address")
                or self.project_data.get("address")
                or {}
            )
            if isinstance(addr, dict):
                return str(addr.get("house_number") or addr.get("number") or "")
            return ""
        elif key == "address":
            addr = (
                self.project_data.get("customer_address")
                or self.project_data.get("address")
                or {}
            )
            if isinstance(addr, dict):
                street = addr.get("street", "")
                number = addr.get("house_number") or addr.get("number") or ""
                return f"{street} {number}".strip()
            return str(addr)
        elif key == "anlage_kwp_formatted":
            kwp = self.analysis_results.get("anlage_kwp")
            if isinstance(kwp, (int, float)):
                return f"{kwp:,.2f}".replace(",", ".")
            return str(kwp) if kwp is not None else ""
        elif key == "final_cost":
            return str(self.analysis_results.get("final_cost", ""))
        elif key == "final_cost_formatted":
            value = self.analysis_results.get("final_cost")
            if value is None:
                return ""
            try:
                return self._format_currency(float(value))
            except Exception:
                return str(value)

        # FALLBACK
        else:
            print(f" Unbekannter Key: {key}")
            return f"{{{key}}}"  # Gibt Key zurück, wenn nicht gefunden

    def _adjust_text_position(
        self, text: str, x: float, y: float, page_num: int
    ) -> Tuple[float, float]:
        """Justiert Textpositionen für spezifische Elemente."""

        # 1cm = ~28.35 points, 1.5cm = ~42.52 points

        # Überschrift 1cm nach unten (nur Seite 1)
        if page_num == 1:
            if any(
                keyword in text
                for keyword in ["IHRE PERSÖNLICHE PV-ANLAGE, IM ÜBERBLICK"]
            ):
                return x, y + 13.35

        # Ersparnis-Block 2cm nach unten (statt 1cm nach oben)
        ersparnis_keywords = [
            "Ersparnis über 20 Jahre",
            "36.958",
            "36958",
            "EUR*",
            "29.150",
            "29150",
            "mit Batteriespeicher",
            "ohne Batteriespeicher",
            "inkl. Photovoltaikanlage",
            "Fördergelder",
        ]
        if any(keyword in text for keyword in ersparnis_keywords):
            return x, y + 10.7  # 2cm = ~56.7 points

        # Technische Daten 1,5cm nach unten
        tech_keywords = [
            "Heizung",
            "Warmwasser",
            "Verbrauch",
            "Dachneigung",
            "Solaranlage",
            "Batterie",
            "Jahresertrag",
            "Wärmepumpe",
            "Elektrischer Boiler",
            "6.000 kWh/Jahr",
            "30°",
            "8,4 kWp",
            "6,1 kWh",
            "8.251,92 kWh/Jahr",
        ]
        if any(keyword in text for keyword in tech_keywords):
            return x, y + 12.52

        # Keine Änderung für andere Texte
        return x, y

    def build_pdf(self) -> Optional[bytes]:
        """Erstellt die vollständige TOM-90 PDF basierend auf den analysierten Daten."""
        try:
            doc = fitz.open()

            # ERWEITERT AUF 20 SEITEN! Alle verfügbaren TXT-Dateien verwenden
            print(" TOM90: Erstelle 20-Seiten PDF...")
            for page_num in range(1, 21):
                print(f" Erstelle Seite {page_num}/20...")
                self._create_page_from_data(doc, page_num)

            # Konvertiere zu bytes
            buffer = io.BytesIO()
            doc.save(buffer)
            doc.close()
            return buffer.getvalue()

        except Exception as e:
            print(f"Fehler bei TOM-90 Exact PDF-Erstellung: {e}")
            return None

    def _create_page_from_data(self, doc: fitz.Document, page_num: int) -> None:
        """Erstellt eine Seite basierend auf den analysierten Daten."""
        page = doc.new_page(width=self.page_width, height=self.page_height)
        page_data = self._load_page_data(page_num)

        # Bilder einfügen
        for img_data in page_data["images"]:
            if img_data["file"] and os.path.exists(img_data["file"]):
                try:
                    # Spezielle Behandlung für Logo auf Seite 1
                    if page_num == 1 and self.company_logo_base64:
                        # Verwende Company Logo statt Original-Bild
                        logo_data = base64.b64decode(self.company_logo_base64)
                        page.insert_image(
                            fitz.Rect(*img_data["bbox"]), stream=logo_data
                        )
                    else:
                        page.insert_image(
                            fitz.Rect(*img_data["bbox"]), filename=img_data["file"]
                        )
                except Exception as e:
                    print(f"Fehler beim Einfügen von Bild {img_data['file']}: {e}")

        # Formen zeichnen
        for shape in page_data["shapes"]:
            try:
                if shape["type"] == "line":
                    page.draw_line(
                        shape["points"][0],
                        shape["points"][1],
                        color=(0, 0, 0),
                        width=0.5,
                    )
                elif shape["type"] == "rect":
                    page.draw_rect(
                        fitz.Rect(*shape["bbox"]), color=(0, 0, 0), width=0.5
                    )
                elif shape["type"] == "bezier":
                    page.draw_bezier(
                        shape["points"][0],
                        shape["points"][1],
                        shape["points"][2],
                        shape["points"][3],
                        color=(0, 0, 0),
                        width=0.5,
                    )
            except Exception as e:
                print(f"Fehler beim Zeichnen der Form: {e}")

        # Texte einfügen (mit dynamischen Inhalten)
        for text_data in page_data["texts"]:
            try:
                x0, y0, x1, y1 = text_data["bbox"]

                # Dynamische Inhalte ersetzen
                display_text = self._substitute_dynamic_content(
                    text_data["text"], page_num
                )

                # Position justieren für spezifische Texte
                adjusted_x, adjusted_y = self._adjust_text_position(
                    display_text, x0, y0, page_num
                )

                # Farbe konvertieren
                color_int = text_data.get("color", self.tom90_blue)
                r = ((color_int >> 16) & 255) / 255.0
                g = ((color_int >> 8) & 255) / 255.0
                b = (color_int & 255) / 255.0

                # Font bestimmen - nur eingebaute Schriftarten verwenden
                font_name = text_data.get("font", "Roboto-Regular")
                if "Bold" in font_name:
                    font = "hebo"  # Helvetica-Bold (built-in)
                elif "Medium" in font_name:
                    font = "hebo"  # Helvetica-Bold (built-in)
                else:
                    font = "helv"  # Helvetica (built-in)

                # Text einfügen mit Fehlerbehandlung und angepasster Position
                try:
                    page.insert_text(
                        (adjusted_x, adjusted_y),
                        display_text,
                        fontname=font,
                        fontsize=text_data.get("size", 12),
                        color=(r, g, b),
                    )
                except Exception as font_error:
                    # Fallback ohne Schriftart
                    try:
                        page.insert_text(
                            (adjusted_x, adjusted_y),
                            display_text,
                            fontsize=text_data.get("size", 12),
                            color=(r, g, b),
                        )
                    except Exception as text_error:
                        print(
                            f"Fehler beim Text einfügen '{display_text}': {text_error}"
                        )
                        continue

            except Exception as e:
                print(
                    f"Fehler beim Einfügen von Text '{text_data.get('text', '')}': {e}"
                )

    def _create_page1_cover(self, doc: fitz.Document) -> None:
        """Erstellt Seite 1 - Titelseite mit Ersparnis-Übersicht."""
        page = doc.new_page(width=self.page_width, height=self.page_height)

        # Logo einfügen (falls vorhanden)
        if self.company_logo_base64:
            try:
                logo_data = base64.b64decode(self.company_logo_base64)
                logo_rect = fitz.Rect(39.72, 14.24, 169.36, 66.69)  # Original Position
                page.insert_image(logo_rect, stream=logo_data)
            except:
                pass

        # Haupttitel-Bereich (dynamisch mit Kundendaten)
        # Name für die Titelseite zusammensetzen: erst customer_name, sonst salutation + first_name + last_name
        customer_name = (
            self.project_data.get("customer_name")
            or (
                (
                    f"{self.project_data.get('salutation', '')} "
                    f"{self.project_data.get('first_name', '')} "
                    f"{self.project_data.get('last_name', '')}"
                ).strip()
            )
            or "Sehr geehrte Kundin, sehr geehrter Kunde"
        )
        page.insert_text(
            (39.72, 100),
            f"Angebot für {customer_name}",
            fontname="helv-bold",
            fontsize=24,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Ersparnis-Bereich (exakte Positionen aus Original)
        savings_with = self.analysis_results.get(
            "total_savings_with_storage_eur", 36958
        )
        savings_without = self.analysis_results.get(
            "total_savings_without_storage_eur", 29150
        )

        # "Ersparnis über 20 Jahre" Header
        page.insert_text(
            (297.38, 367.96),
            "Ersparnis über 20 Jahre",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Mit Batteriespeicher
        page.insert_text(
            (297.38, 379.05),
            "mit Batteriespeicher",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (418.78, 368.43),
            f"{self._format_currency(savings_with)}*",
            fontname="helv-bold",
            fontsize=16,
            color=self._rgb_from_int(self.tom90_orange),
        )

        # Ohne Batteriespeicher
        page.insert_text(
            (297.38, 407.53),
            "ohne Batteriespeicher",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (418.78, 396.90),
            f"{self._format_currency(savings_without)}*",
            fontname="helv-bold",
            fontsize=16,
            color=self._rgb_from_int(self.tom90_orange),
        )

        # Trennlinien (aus Original-Formen)
        page.draw_line((297.50, 365.69), (554.53, 365.69), color=(0, 0, 0), width=0.5)
        page.draw_line((297.50, 394.17), (554.53, 394.17), color=(0, 0, 0), width=0.5)
        page.draw_line((418.90, 364.94), (418.90, 422.64), color=(0, 0, 0), width=0.5)

        # Fußnote
        page.insert_text(
            (297.38, 428.38),
            "*Ersparnis-Berechnung basierend auf aktuellen Strompreisen und Einspeisevergütung",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # System-Übersicht (rechte Seite)
        anlage_kwp = self.analysis_results.get("anlage_kwp", 8.4)
        annual_production = self.analysis_results.get("annual_pv_production_kwh", 8778)

        # Vertikale Trennlinien für System-Info
        system_lines = [
            (379.18, 550.79, 379.18, 567.27),
            (379.18, 576.27, 379.18, 592.75),
            (379.18, 601.74, 379.18, 618.23),
            (379.18, 652.70, 379.18, 669.19),
        ]

        for x1, y1, x2, y2 in system_lines:
            page.draw_line((x1, y1), (x2, y2), color=(0, 0, 0), width=0.5)

        # System-Info Text
        page.insert_text(
            (297.38, 550),
            f"Anlagenleistung: {anlage_kwp} kWp",
            fontname="helv",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (297.38, 570),
            f"Jahresertrag: {annual_production:,.0f} kWh".replace(",", "."),
            fontname="helv",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Platz für Diagramm/Bild (falls vorhanden)
        chart_rect = fitz.Rect(39.72, 546.29, 266.03, 737.38)
        # Prüfe, ob ein Diagramm als Bytes vorliegt (z. B. base64-String oder bytes)
        chart_data = self.analysis_results.get("ersparnis_chart_bytes")
        if chart_data:
            try:
                # Falls base64-String übergeben wurde, decodieren
                if isinstance(chart_data, str):
                    try:
                        chart_data = base64.b64decode(chart_data)
                    except Exception:
                        pass
                # Diagramm einfügen
                page.insert_image(chart_rect, stream=chart_data)
            except Exception:
                # Bei Fehler auf Platzhalter zurückfallen
                page.draw_rect(
                    chart_rect, color=self._rgb_from_int(self.tom90_blue), width=1
                )
                page.insert_text(
                    (60, 640),
                    "Ersparnis-Diagramm\n(wird hier eingefügt)",
                    fontname="helv",
                    fontsize=12,
                    color=self._rgb_from_int(self.tom90_blue),
                )
        else:
            # Kein Diagramm vorhanden – Standardplatzhalter zeichnen
            page.draw_rect(
                chart_rect, color=self._rgb_from_int(self.tom90_blue), width=1
            )
            page.insert_text(
                (60, 640),
                "Ersparnis-Diagramm\n(wird hier eingefügt)",
                fontname="helv",
                fontsize=12,
                color=self._rgb_from_int(self.tom90_blue),
            )

    def _create_page2_analysis(self, doc: fitz.Document) -> None:
        """Erstellt Seite 2 - Analyse und Erklärungen."""
        page = doc.new_page(width=self.page_width, height=self.page_height)

        # Haupt-Erklärungs-Text (linke Spalte)
        explanations = [
            {
                "title": "Warum speise ich Strom ins Netz ein?",
                "text": "Sie können Ihren Solarstrom direkt verbrauchen oder in Ihrem Batteriespeicher zwischenspeichern. Überschüsse werden ins Stromnetz eingespeist.",
                "y_start": 208,
            },
            {
                "title": "Warum brauche ich Strom vom Netz?",
                "text": "Selbst wenn Ihre Solarstromanlage über das ganze Jahr gesehen mehr Strom produziert als Sie verbrauchen, benötigen Sie z.B. in Winternächten trotz Batteriespeichers Strom vom Netz.",
                "y_start": 530,
            },
        ]

        for exp in explanations:
            # Titel
            page.insert_text(
                (379.50, exp["y_start"]),
                exp["title"],
                fontname="helv-bold",
                fontsize=12,
                color=self._rgb_from_int(self.tom90_blue),
            )

            # Text in mehreren Zeilen
            lines = exp["text"].split(". ")
            y_offset = exp["y_start"] + 30
            for line in lines:
                if line.strip():
                    page.insert_text(
                        (379.50, y_offset),
                        line + ("." if not line.endswith(".") else ""),
                        fontname="helv",
                        fontsize=12,
                        color=self._rgb_from_int(self.tom90_blue),
                    )
                    y_offset += 18

        # Energie-Fluss Diagramm (vereinfacht)
        # Haus
        house_rect = fitz.Rect(100, 250, 200, 350)
        page.draw_rect(house_rect, color=self._rgb_from_int(self.tom90_blue), width=2)
        page.insert_text(
            (120, 300),
            "HAUS",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # PV-Anlage
        pv_rect = fitz.Rect(100, 150, 200, 200)
        page.draw_rect(pv_rect, color=self._rgb_from_int(self.tom90_orange), width=2)
        page.insert_text(
            (110, 175),
            "PV-ANLAGE",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Batterie
        battery_rect = fitz.Rect(250, 250, 350, 350)
        page.draw_rect(battery_rect, color=self._rgb_from_int(self.tom90_blue), width=2)
        page.insert_text(
            (270, 300),
            "BATTERIE",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Stromnetz
        grid_rect = fitz.Rect(100, 400, 200, 450)
        page.draw_rect(grid_rect, color=self._rgb_from_int(self.tom90_blue), width=2)
        page.insert_text(
            (110, 425),
            "STROMNETZ",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Verbindungspfeile
        arrows = [
            ((150, 200), (150, 250)),  # PV -> Haus
            ((200, 300), (250, 300)),  # Haus -> Batterie
            ((150, 350), (150, 400)),  # Haus -> Netz
        ]

        for start, end in arrows:
            page.draw_line(
                start, end, color=self._rgb_from_int(self.tom90_blue), width=2
            )
            # Pfeilspitze (vereinfacht)
            page.draw_line(
                (end[0] - 5, end[1] - 5),
                end,
                color=self._rgb_from_int(self.tom90_blue),
                width=2,
            )
            page.draw_line(
                (end[0] + 5, end[1] - 5),
                end,
                color=self._rgb_from_int(self.tom90_blue),
                width=2,
            )

    def _create_page3_chart(self, doc: fitz.Document) -> None:
        """Erstellt Seite 3 - Ersparnis-Diagramm."""
        page = doc.new_page(width=self.page_width, height=self.page_height)

        # Y-Achsen Beschriftung (aus Original)
        y_labels = ["50.000", "40.000", "30.000", "20.000", "10.000", "0"]
        y_positions = [184.81, 211.78, 238.01, 264.99, 291.22, 318.20]

        for label, y_pos in zip(y_labels, y_positions):
            page.insert_text(
                (56.45, y_pos),
                label,
                fontname="helv",
                fontsize=6,
                color=self._rgb_from_int(self.tom90_blue),
            )

        # EUR Label
        page.insert_text(
            (41.98, 248.34),
            "EUR",
            fontname="helv-bold",
            fontsize=7.5,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Hauptwerte (dynamisch)
        savings_with = self.analysis_results.get(
            "total_savings_with_storage_eur", 36958
        )
        savings_without = self.analysis_results.get(
            "total_savings_without_storage_eur", 29150
        )

        # Balken für "mit Speicher"
        with_storage_height = (savings_with / 50000) * 150  # Skalierung auf Chart
        with_rect = fitz.Rect(120, 318 - with_storage_height, 180, 318)
        page.draw_rect(
            with_rect, color=self._rgb_from_int(self.tom90_orange), fill=True
        )

        # Balken für "ohne Speicher"
        without_storage_height = (savings_without / 50000) * 150
        without_rect = fitz.Rect(200, 318 - without_storage_height, 260, 318)
        page.draw_rect(
            without_rect, color=self._rgb_from_int(self.tom90_blue), fill=True
        )

        # Werte-Labels
        page.insert_text(
            (210, 192),
            f"{savings_with:,.0f}".replace(",", "."),
            fontname="helv-bold",
            fontsize=10.5,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (210, 204),
            "EUR",
            fontname="helv",
            fontsize=10.5,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Chart-Achsen
        page.draw_line(
            (80, 180), (80, 330), color=self._rgb_from_int(self.tom90_blue), width=1
        )  # Y-Achse
        page.draw_line(
            (80, 330), (350, 330), color=self._rgb_from_int(self.tom90_blue), width=1
        )  # X-Achse

        # Legende
        page.insert_text(
            (120, 350),
            "Mit Speicher",
            fontname="helv",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_orange),
        )

        page.insert_text(
            (220, 350),
            "Ohne Speicher",
            fontname="helv",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

    def _create_page4_components(self, doc: fitz.Document) -> None:
        """Erstellt Seite 4 - Komponenten-Übersicht."""
        page = doc.new_page(width=self.page_width, height=self.page_height)

        # Haupttitel
        page.insert_text(
            (39.65, 72.55),
            "KOMPONENTEN IHRES PV-SYSTEMS",
            fontname="helv-bold",
            fontsize=28,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Untertitel
        page.insert_text(
            (39.65, 136.02),
            "Wir empfehlen Ihnen die folgenden, hochwertigen Komponenten:",
            fontname="helv",
            fontsize=16,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Komponenten-Details (dynamisch aus Projektdaten)
        anlage_kwp = self.analysis_results.get("anlage_kwp", 8.4)
        module_count = self.project_data.get("pv_details", {}).get("module_quantity", 0)
        if module_count == 0:
            module_count = max(1, round(anlage_kwp * 1000 / 420))  # 420W Module

        # PV-Module Sektion
        y_start = 240
        component_details = [
            ("Hersteller:", " TommaTech"),
            ("Typ:", " TT420 108TNFB10"),
            ("Leistung:", " 420 Wp"),
            ("Herstellergarantie:", " 25 Jahre"),
            ("Anzahl Module:", f" {module_count} Stück"),
            ("Gesamtleistung:", f" {anlage_kwp} kWp"),
        ]

        for i, (label, value) in enumerate(component_details):
            y_pos = y_start + (i * 16)

            # Label (fett)
            page.insert_text(
                (238.64, y_pos),
                label,
                fontname="helv-bold",
                fontsize=10,
                color=self._rgb_from_int(self.tom90_blue),
            )

            # Wert (normal, dynamisch)
            page.insert_text(
                (284.66, y_pos),
                value,
                fontname="helv",
                fontsize=10,
                color=self._rgb_from_int(self.tom90_blue),
            )

        # Wechselrichter Sektion
        y_start = 380
        inverter_details = [
            ("Hersteller:", " Solax Power"),
            ("Typ:", " X3-HYBRID-8.0-D"),
            ("Leistung:", f" {anlage_kwp} kW"),
            ("Wirkungsgrad:", " > 97%"),
            ("Herstellergarantie:", " 10 Jahre"),
        ]

        page.insert_text(
            (238.64, 360),
            "WECHSELRICHTER",
            fontname="helv-bold",
            fontsize=12,
            color=self._rgb_from_int(self.tom90_blue),
        )

        for i, (label, value) in enumerate(inverter_details):
            y_pos = y_start + (i * 16)

            page.insert_text(
                (238.64, y_pos),
                label,
                fontname="helv-bold",
                fontsize=10,
                color=self._rgb_from_int(self.tom90_blue),
            )

            page.insert_text(
                (284.66, y_pos),
                value,
                fontname="helv",
                fontsize=10,
                color=self._rgb_from_int(self.tom90_blue),
            )

        # Batteriespeicher (falls konfiguriert)
        if self.project_data.get("pv_details", {}).get("include_storage"):
            battery_capacity = self.project_data.get("project_details", {}).get(
                "battery_capacity_kwh", 6.1
            )

            y_start = 520
            battery_details = [
                ("Hersteller:", " Solax Power"),
                ("Typ:", " Triple Power T58"),
                ("Kapazität:", f" {battery_capacity} kWh"),
                ("Zyklen:", " > 6000"),
                ("Herstellergarantie:", " 10 Jahre"),
            ]

            page.insert_text(
                (238.64, 500),
                "BATTERIESPEICHER",
                fontname="helv-bold",
                fontsize=12,
                color=self._rgb_from_int(self.tom90_blue),
            )

            for i, (label, value) in enumerate(battery_details):
                y_pos = y_start + (i * 16)

                page.insert_text(
                    (238.64, y_pos),
                    label,
                    fontname="helv-bold",
                    fontsize=10,
                    color=self._rgb_from_int(self.tom90_blue),
                )

                page.insert_text(
                    (284.66, y_pos),
                    value,
                    fontname="helv",
                    fontsize=10,
                    color=self._rgb_from_int(self.tom90_blue),
                )

        # Komponenten-Bilder (Platzhalter)
        image_rects = [
            fitz.Rect(50, 200, 200, 320),  # PV-Modul
            fitz.Rect(50, 340, 200, 460),  # Wechselrichter
        ]

        if self.project_data.get("pv_details", {}).get("include_storage"):
            image_rects.append(fitz.Rect(50, 480, 200, 600))  # Batterie

        for rect in image_rects:
            page.draw_rect(rect, color=self._rgb_from_int(self.tom90_blue), width=1)
            page.insert_text(
                (rect.x0 + 10, rect.y0 + (rect.height / 2)),
                "Komponenten-\nBild",
                fontname="helv",
                fontsize=10,
                color=self._rgb_from_int(self.tom90_blue),
            )

    def _create_page5_facts(self, doc: fitz.Document) -> None:
        """Erstellt Seite 5 - Wissenswertes und CO2-Fakten."""
        page = doc.new_page(width=self.page_width, height=self.page_height)

        # CO2-Einsparung (dynamisch)
        co2_savings_kg = self.analysis_results.get("annual_co2_savings_kg", 3500)
        co2_savings_tons = co2_savings_kg / 1000.0

        # Auto-Kilometer-Äquivalent
        km_per_year = 15000
        co2_per_km = 0.12  # kg CO2 pro km
        km_equivalent = co2_savings_kg / co2_per_km if co2_per_km else 0

        # Erste Fakten-Sektion
        page.insert_text(
            (208.14, 311.01),
            "Haben Sie gewusst?",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (208.14, 332.59),
            "Ein durchschnittliches Elektroauto ist 3-4 mal effizienter als ein Auto mit",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (208.14, 342.33),
            "Verbrennungsmotor.",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Kilometer-Anzeige (dynamisch)
        page.insert_text(
            (124.59, 230.85),
            f"{km_equivalent:,.0f} km".replace(",", "."),
            fontname="helv-bold",
            fontsize=20,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (124.59, 272.95),
            f"fahren Sie mit Ihrem Auto {km_equivalent:,.0f} km um die Welt".replace(
                ",", "."
            ),
            fontname="helv",
            fontsize=12,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Zweite Fakten-Sektion
        page.insert_text(
            (208.14, 465.38),
            "Haben Sie gewusst?",
            fontname="helv-bold",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (208.14, 486.96),
            "In Deutschland liegen die jährlichen durchschnittlichen pro Kopf",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        page.insert_text(
            (208.14, 496.70),
            f"Emissionen bei 7,69 Tonnen CO₂. Sie sparen {co2_savings_tons:.1f} Tonnen pro Jahr!",
            fontname="helv",
            fontsize=8,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # CO2-Visualisierung (vereinfacht)
        # Erdkugel-Symbol
        earth_center = (300, 150)
        earth_radius = 50
        page.draw_circle(
            earth_center,
            earth_radius,
            color=self._rgb_from_int(self.tom90_blue),
            width=2,
        )
        page.insert_text(
            (earth_center[0] - 20, earth_center[1]),
            "",
            fontname="helv",
            fontsize=30,
            color=self._rgb_from_int(self.tom90_blue),
        )

        # Pfeil nach unten
        page.draw_line(
            (earth_center[0], earth_center[1] + earth_radius + 10),
            (earth_center[0], earth_center[1] + earth_radius + 40),
            color=self._rgb_from_int(self.tom90_blue),
            width=3,
        )

        # CO2-Einsparung hervorheben
        co2_rect = fitz.Rect(200, 370, 400, 420)
        page.draw_rect(co2_rect, color=self._rgb_from_int(self.tom90_orange), fill=True)
        page.insert_text(
            (220, 395),
            f"{co2_savings_tons:.1f} t CO₂",
            fontname="helv-bold",
            fontsize=16,
            color=self._rgb_from_int(self.tom90_white),
        )
        page.insert_text(
            (220, 405),
            "weniger pro Jahr",
            fontname="helv",
            fontsize=10,
            color=self._rgb_from_int(self.tom90_white),
        )

        # Bäume-Äquivalent
        trees_per_ton = 12.5  # Bäume pro Tonne CO2
        trees_equivalent = co2_savings_tons * trees_per_ton

        page.insert_text(
            (50, 650),
            f"Das entspricht {trees_equivalent:.0f} gepflanzten Bäumen!",
            fontname="helv-bold",
            fontsize=12,
            color=self._rgb_from_int(self.tom90_blue),
        )


def generate_tom90_exact_pdf(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    company_info: Dict[str, Any],
    company_logo_base64: Optional[str] = None,
    inclusion_options: Optional[Dict[str, Any]] = None,
    texts: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Optional[bytes]:
    """Generiert TOM-90 PDF mit exaktem Layout."""

    renderer = TOM90ExactRenderer(
        project_data=project_data,
        analysis_results=analysis_results,
        company_info=company_info,
        inclusion_options=inclusion_options,
        texts=texts,
        company_logo_base64=company_logo_base64,
    )

    return renderer.build_pdf()
