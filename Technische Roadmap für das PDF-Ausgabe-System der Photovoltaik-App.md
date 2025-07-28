Technische Roadmap für das PDF-Ausgabe-
System der Photovoltaik-App
Diese Roadmap skizziert die  Phasen,  Prioritäten und Architektur für die finale Umsetzung des PDF-
Ausgabe-Systems.  Das  Ziel  ist  ein  modulares,  vollständig  konfigurierbares  und  professionell
designtes  PDF-Generierungssystem,  basierend  auf  der  bestehenden  Codebasis  ( pdf_ui.py , 
pdf_generator.py ,  pdf_preview.py ,  pdf_widgets.py ,  pdf_styles.py  etc.). Die Roadmap

umfasst  zudem  UI-Integration,  Design-Layer,  Beispielkomponenten sowie  spätere
Erweiterungsmöglichkeiten.  Alle  bestehenden  Funktionen  der  App  bleiben  erhalten  und  werden
nahtlos integriert.

Phase 1: Analyse der Codebasis & Architekturplanung (Priorität:
Hoch)
Ziele: Verständnis der bestehenden Module und Grundsteine für Erweiterungen legen. In dieser Phase
wird der vorhandene PDF-Code (UI, Generator, Preview, Widgets, Styles) gründlich analysiert, um die
neuen Anforderungen sauber darauf aufzusetzen. 

• Bestandsaufnahme & Code-Review: Überprüfung von pdf_generator.py  (PDF-Erstellung), 
pdf_ui.py  (UI-Steuerung), pdf_preview.py  (Vorschau-Logik) und Hilfsmodulen.

Identifizierung, wo Erweiterungen nötig sind, z. B. für neue Inhalte oder Optionen. Bestehende
Problemstellen (z. B. Patch-Bedarf bei der Datenvalidierung) werden behoben, damit die Basis
stabil ist 1 2 . 

• Architekturentscheidung: Festlegung, wie die PDF-Inhalte modularisiert werden. Geplant ist, 
jedes Inhaltsmodul (Deckblatt, Anschreiben, Tabellen, Diagramme etc.) als separate
Komponente/Funktion zu gestalten, die der pdf_generator  bei Bedarf einfügt. Dies erlaubt
optionale Abschnitte und Wiederverwendung. 

• Datenmodell prüfen: Sicherstellen, dass die Datenstrukturen ( project_data , 
analysis_results , company_info , etc.) alle benötigten Informationen für die neuen PDF-

Elemente liefern. Ggf. Erweiterung um Felder für Titelbild, Kundengruß, Auswahl an
Dokumenten usw. 

• Priorisierung festlegen: Kernfunktionen (UI-Konfiguration, modulare Inhalte, Design-Vorlagen)
werden zuerst angegangen (Phase 2–4). Erweiterte Features wie Multi-Offer und Passwortschutz
folgen danach (Phase 5). Dies stellt sicher, dass ein lauffähiges Grundsystem früh verfügbar ist
und dann ausgebaut wird. 

• Backward-Compatibility-Plan: Definition von Strategien, um Abwärtskompatibilität zu
gewährleisten. Z.B. behält generate_offer_pdf  seine Schnittstelle bei, erweitert aber
Parameter optional. Standardwerte für neue Optionen stellen sicher, dass Aufrufe ohne neue
Parameter wie zuvor funktionieren.

1



Phase 2: UI-Integration & Konfigurierbarkeit der PDF-Erstellung
(Priorität: Hoch)
Ziele: Alle PDF-Inhalte sollen über die Benutzeroberfläche flexibel wähl- und konfigurierbar sein. Die
UI  wird  so  erweitert,  dass  Nutzerinnen  Inhalt,  Reihenfolge  und  Stil*  der  PDF-Angebote  bestimmen
können.

• Konfigurationspanel in der UI: In pdf_ui.py /Streamlit wird ein dedizierter Bereich “PDF-
Konfiguration” bereitgestellt. Hier können Nutzer:innen festlegen: 

• Titelbild und Titeltext: Upload-Feld für ein Deckblatt-Bild (z. B. Firmen- oder Stimmungsbild)
und Eingabefeld für den Angebots-Titel. Diese Werte werden an den PDF-Generator
weitergereicht (z. B. als selected_title_image_b64  und selected_offer_title_text ). 

• Deckblatt & Anschreiben: Option, ein persönliches Anschreiben (Begrüßungstext) einzufügen.
Textvorlagen (verschiedene Tonalitäten, siehe Phase 5) können per Dropdown gewählt oder frei
editiert werden. Der gewählte Text fließt als selected_cover_letter_text  in die PDF-
Erstellung ein. 

• Modul-Auswahl: Liste aller verfügbaren Inhaltsmodule (z. B. Projektübersicht, Technische Details, 
Wirtschaftlichkeit, Produktbilder, CO₂-Ersparnis, Firmenunterlagen, Datenblätter). Für jedes Modul
eine Checkbox oder Multiselect, um es ein- oder auszuschließen. Diese steuern ein 
sections_to_include -Array, das an generate_offer_pdf  übergeben wird.

Standardmäßig sind Hauptsektionen vorausgewählt, aber alles ist abwählbar. 
• Reihenfolge via Drag & Drop: Implementierung einer intuitiven Möglichkeit, die Reihenfolge

der PDF-Seiten zu ändern (z. B. per Drag & Drop auf eine Liste der gewählten Module).
Gegebenenfalls wird pdf_widgets.py  erweitert, um eine sortierbare Liste (z. B. mittels drag
and drop reorder Pattern) bereitzustellen. In Streamlit gibt es nativ keine Drag&Drop-Liste, daher
könnte ein Workaround zum Einsatz kommen (z. B. Buttons “nach oben/unten” oder eine
spezielle Custom-Component). Wichtig ist, dass die vom Nutzer festgelegte Reihenfolge der
Module beim PDF-Generieren berücksichtigt wird. 

• Template-/Stil-Auswahl: (Siehe Phase 4) Dropdown für verschiedene PDF-Design-Vorlagen
(Themen). Die Auswahl bestimmt Farben, Schrift und Layout und wird als Parameter (z. B. 
selected_theme ) gespeichert. 

• Weitere Optionen: Checkbox für Diagramme einfügen (sofern nicht in Modul-Checkboxen
abgedeckt), Toggle für alle Dokumente anhängen (z. B. firmenweite Anhänge), Checkbox 
Produktdetails einblenden etc. Solche Optionen werden in einem inclusion_options  Dict
gesammelt und an den Generator gegeben 3 4 . Auch eine Passwort setzen-Option (siehe
Phase 5) wird hier untergebracht, deaktiviert standardmäßig. 

• Live-Vorschau Anbindung: Das bestehende Vorschau-Modul ( pdf_preview.py ) wird mit der
neuen Konfiguration verknüpft. Bei Änderungen an den Einstellungen soll eine PDF-Vorschau
schnell verfügbar sein. Die Preview-Engine generiert ein Vorschau-PDF auf Basis der aktuellen
Auswahl und wandelt es in Bilder um 5 , um es in der App anzuzeigen. Der Nutzer kann so das
Layout prüfen, bevor das finale PDF erzeugt wird. 

• Validierung & Nutzerführung: Während der Konfiguration zeigt die App an, ob alle nötigen
Daten vorhanden sind (bspw. Projektdaten, Analyseergebnisse) – hierzu wird die bestehende
Datenstatus-Prüfung (_show_pdf_data_status) genutzt und ggf. verbessert, damit bei fehlenden
Daten Warnungen erscheinen aber trotzdem ein PDF (mit Lückenhinweis) generiert werden
kann. Dieses Verhalten wurde bereits per Patch adressiert (keine Blockade mehr bei kleineren
Lücken) 6 7 . Zudem erhält der/die Nutzer:in Hinweise, falls z. B. kein Titelbild gewählt wurde
oder keine Module selektiert sind, um leere PDFs zu vermeiden. 

2



Ergebnis  von  Phase   2: Die  UI  bietet  ein  vollständiges  Kontrollzentrum  für  die  PDF-Erstellung.
Nutzer:innen  können  inhaltliche  Bausteine  auswählen,  anordnen  und  gestalten,  bevor  sie  das
Angebot als  PDF exportieren.  Dies bildet  die Grundlage für die folgenden Phasen,  da alle  weiteren
Funktionen (Design, Module, Multi-PDF) hier eingebunden werden.

Phase 3: Implementierung der PDF-Inhaltsmodule (Priorität:
Hoch)
Ziele: Entwicklung  aller  inhaltlichen  Bausteine  des  PDFs  in  modularer  Form.  Jedes  Modul  wird
professionell aufbereitet und kann einzeln ein- oder ausgeschaltet werden. Die deutsche Sprache und
Formatierung wird konsequent berücksichtigt (lokale Zahl-/Datumsformate, Ansprache etc.).

Die folgenden Inhaltskomponenten werden umgesetzt oder verfeinert: 

• Deckblatt (Titelseite): Enthält das hochgeladene Titelbild (vollflächig oder als Banner) und den
Angebots-Titel. Zusätzlich ggf. Angebotsnummer, Datum und Kundennamen, um den Einstieg zu
personalisieren. Gestaltung: großflächiges Bild mit Overlay-Text oder klare Titel-Seite nach dem
Corporate Design. (Beispiel: Ein ganzseitiges Foto einer PV-Anlage mit darüber liegendem Angebots-
Titel in Firmenfarbe).

• Anschreiben (Begleitbrief): Ein optionaler Brief an den Kunden mit personalisierter Anrede
(z. B. “Sehr geehrte Frau Müller,”) und passender Tonalität. Dieser Textblock kann sich über eine
Seite+ erstrecken, je nach Länge. Technisch wird dies als Flowable (Paragraph/Frame in
ReportLab) umgesetzt, der an den Rändern genügend Weißraum lässt (für einen echten
Briefcharakter). Tonalität und Anrede werden flexibel gehandhabt: je nach gewählter Vorlage
formal ("Sie") oder locker ("Du"), technisch-sachlich oder emotional-freundlich. Textbausteine in
der deutschen Sie-Form werden standardmäßig geliefert, evtl. ergänzt um Alternativen. Alle
Platzhalter (Name, Daten) füllt das System automatisch. 

• Projektübersicht (Textblöcke): Eine Seite mit den wichtigsten Projektdaten in Fließtext oder
Stichpunkten. Z.B. “Dieses Angebot umfasst eine Photovoltaikanlage mit XX Modulen und YY kWp,
geplant für Ihr Dach in Musterstadt...” plus Highlights (Jahresertrag, Eigenverbrauchsquote etc.).
Diese Sektion wird aus den project_data  und analysis_results  generiert. Layout: gut
lesbare Absätze, evtl. Icons/Piktogramme für jede Kennzahl. 

• Wirtschaftlichkeitsanalyse (Tabellen & Kennzahlen): Detaillierte tabellarische Aufstellung von
Kosten, Einsparungen, Förderung, Amortisationszeit etc. Hier werden Berechnungsergebnisse
aus analysis_results  ansprechend formatiert. Einsatz von Tabellen-Stilen aus 
pdf_styles.py  (z. B. unterschiedlichfarbige Header, abgesetzte Summenzeilen) für ein

professionelles Aussehen 8 . Zahlen werden ins deutsche Format gebracht (Dezimalpunkt zu
Komma, Tausenderpunkt) und mit € versehen. Falls Daten fehlen, werden Felder mit “–” oder
einem Hinweis belegt, aber die Tabelle dennoch gezeigt, um Transparenz zu wahren. 

• Diagramme (Ertrags- und Verbrauchsgrafiken, CO₂-Ersparnis): Grafische Aufbereitung der
wichtigsten Zahlen. Geplant sind z. B. ein Monatlicher Ertragsdiagramm, ein 
Eigenverbrauchs-/Deckungsgrad-Diagramm, evtl. ROI-Verlauf, und eine CO₂-Ersparnis-
Visualisierung. Die bestehenden Chart-Funktionen (Matplotlib/Seaborn) werden verwendet und
an das PDF angepasst. In pdf_styles  sind bereits Chart-Themes definiert (z. B. modern, 
elegant mit passenden Farben) 9 , diese werden angewandt, damit die Diagramme im PDF
farblich zum Template passen. Diagramme werden als Bilder gerendert und in den PDF-Flow
eingefügt (ReportLab Canvas oder Platypus Image-Flows). Wichtig: Auf ausreichende Auflösung
achten, damit Druckqualität gewährleistet ist, aber auch Dateigröße im Rahmen bleibt.
Diagrammbeschriftungen in Deutsch (Achsen: “Monat”, “Energie (kWh)” etc.). 

3



• Produktübersicht und -bilder: Auflistung der angebotenen Komponenten (Module,
Wechselrichter, Speicher etc.) jeweils mit Bild, Modellname, Leistungsdaten und Anzahl. Dies
kann als Tabelle oder Kachel-Layout umgesetzt werden. Z.B. eine Tabelle mit Spalten Produktbild
– Name – Kennzahlen – Stückpreis – Gesamtpreis. Produktbilder können aus der Datenbank oder
einer URL geladen und per PIL verkleinert ins PDF eingebettet werden. pdf_generator  erhält
dafür Zugriff über list_products_func / get_product_by_id_func  (wie schon
vorgesehen). Falls keine Bilder vorhanden sind, wird ersatzweise der Name textuell
hervorgehoben. Tabellen-Stil: zwei-spaltig für Bild und Text, oder Bilder als kleine Thumbnails
neben Text. Diese Sektion ist optional – bei reinen Wirtschaftlichkeitsangeboten kann sie
abgewählt werden. 

• CO₂-Ersparnis & Nachhaltigkeit: Neben Diagrammen kann ein dedizierter Abschnitt die
jährliche CO₂-Einsparung in Tonnen erläutern, ggf. verglichen mit PKW-Kilometern oder Bäumen.
Dieser Textblock (mit eventuell einem Icon) betont die Umweltvorteile des Projekts. Daten
kommen aus analysis_results  (CO₂ Daten). 

• Firmen- und Vertragsdokumente: Möglichkeit, standardisierte Firmendokumente ans Angebot
anzuhängen, z. B. AGB, Zertifikate, Referenzen. In der UI kann die Firma hinterlegen, welche
Dokumente angehängt werden sollen (z. B. als PDF in der DB). Wenn 
include_all_documents  gewählt ist 3 4 , werden alle hinterlegten PDFs der aktiven

Firma in das Angebots-PDF eingebettet (als zusätzliche Seiten, ggf. nach dem Hauptteil oder als
Anhang mit eigenem Deckblatt “Anlagen”). Alternativ kann der Nutzer im UI gezielt Dokumente
auswählen (dann müsste pdf_ui  eine Mehrfachauswahl der verfügbaren Dokumente
anbieten). Technisch werden PDFs entweder per PyMuPDF zusammengeführt oder als Bytes in
ReportLab importiert (PageCatcher oder via canvas). Diese Anhänge sollen nicht das
Hauptlayout beeinflussen, aber im Inhaltsverzeichnis/Seitennummerierung berücksichtigt
werden, falls vorgesehen. 

• Produkt-Datenblätter: Zusätzlich zu obiger Produktübersicht können detaillierte Datenblätter
(PDFs vom Hersteller) als separate Anhänge hinzugefügt werden. Falls z. B. Datenblätter einfügen
ausgewählt ist, sammelt das System zu jedem Produkt das zugehörige PDF (via 
db_list_company_documents_func(..., dtype="datasheet")  oder ähnlichem) und

hängt es ans Ende an. So hat der Kunde auf Wunsch alle technischen Details parat. Diese
Funktion wird modular gehandhabt, damit bei Nichtbedarf die PDFs nicht geladen werden. 

Modulare Umsetzung: Jedes der obigen Elemente wird als eigenständige  Funktion oder Klasse im
Generator  umgesetzt  (z. B.  def  _build_cover_page(data,  style) ,  def  
_build_financial_table(data,  style) ,  ...).  Der  generate_offer_pdf  ruft  diese  je  nach
sections_to_include  auf und fügt die retournierten Flowables/Canvas-Inhalte in das Dokument

ein. Dadurch ist sichergestellt, dass die Kombination und Reihenfolge beliebig variieren kann. 

Deutschsprachige  Formatierung: Während  der  Implementierung  wird  darauf  geachtet,  dass  alle
Inhalte sprachlich konsistent auf Deutsch sind. Texte aus der texts -Struktur (Übersetzungsdictionary)
werden verwendet für Labels, Überschriften und Hinweise, um z.B. “Table of Contents” zu vermeiden.
Zahlen  und  Datumsangaben  werden  mit  deutschen  Formaten  formatiert  (z.B.  f"{wert:,.
2f}".replace(',', 'X').replace('.', ',').replace('X', '.')  als  einfacher  Ansatz  für
1.234,56).  Wo  nötig,  werden  Python-Bibliotheken  ( locale  oder  babel )  verwendet,  um  Datum
(TT.MM.JJJJ) und Währung (€ 1.234,00) korrekt darzustellen. Die Ansprache im Anschreiben wird passend
gewählt  (standardmäßig  “Sie”).  Insgesamt  soll  das  Dokument  so  wirken,  als  wäre  es  von  einem
deutschen Muttersprachler erstellt worden.

Ergebnis  von  Phase   3: Alle  gewünschten  Inhaltselemente  können  erzeugt  und  in  beliebiger
Zusammensetzung ins PDF eingebaut werden. Das System deckt damit  Titelbilder, Texte, Tabellen,

4



Diagramme, Bilder und Dokumente vollständig ab. Durch die modulare Struktur kann das Angebot
individuell zusammengestellt werden, ohne Code-Anpassungen pro Variante. 

Phase 4: Design-Integration und Vorlagen-Stile (Priorität: Hoch)
Ziele: Dem  PDF  ein  professionelles,  modernes  Design verleihen,  basierend  auf  den  gelieferten
Beispiel-PDFs.  Außerdem  mehrere  Design-Themes implementieren,  zwischen  denen  umgeschaltet
werden kann (Farbe, Layout, Typografie). 

• Design-Analyse der Beispiel-PDFs: Zu Beginn dieser Phase werden die bereitgestellten Muster-
PDFs genau analysiert, um wiederkehrende Designmerkmale abzuleiten – z.B. Farbpaletten
(Primär-/Sekundärfarben), Schriftarten und -größen für Überschriften und Fließtext, Abstände
(Weißraum) um Elemente, Gestaltung der Diagramme (Farben, Linienstile) etc. Diese
Erkenntnisse fließen in das Styling ein. 

• Umsetzung Corporate Design: In pdf_styles.py  sind bereits zentrale Styles definiert
(Helvetica als Basisschrift, Standardfarben etc.) und sogar ein Theme-Manager mit
vordefinierten Themes vorhanden 10 . Darauf aufbauend werden die Farb- und
Schriftvorgaben entsprechend der Muster angepasst. Beispielsweise könnte das Theme Modern
Blau (Primärfarbe dunkelblau, Sekundär hellgrau, Akzent blau) dem Corporate Design
entsprechen 11 . Falls spezifische Firmenfarben vorgegeben sind, werden diese als Default
übernommen. Ebenso wird die Typografie überprüft: evtl. Verwendung einer moderneren Schrift
(z.B. eine serifenlose Corporate Font) – falls diese als TTF vorliegt, kann sie via ReportLab
eingebettet werden. Andernfalls bleibt Helvetica/Arial als Ersatz in Nutzung, aber mit
konsistenter Anwendung (fette Schnitte für Überschriften, normal für Text, Kapitälchen oder
Kursiv für Akzente). 

• Whitespace und Layout: Ein professionelles Layout zeichnet sich durch ausreichend
Weißraum und klare Hierarchien aus. Daher werden in den Platypus-Templates die Ränder,
Abstände zwischen Absätzen und Tabellenzellen etc. an die Beispiele angelehnt. Z.B. größere
Seitenränder (2-2.5 cm), Absätze mit spacing after 6 pt, Tabellen nicht randlos an Seitenkante,
etc. Das Ergebnis soll luftig und lesbar wirken, statt gequetscht. Grafische Elemente wie
Trennlinien oder Hintergrundflächen (etwa farbige Balken unter Überschriften) werden dezent
eingesetzt, um das Angebot optisch zu strukturieren. 

• Diagramm-Design: Die Diagramme aus Phase 3 werden optisch an den gewählten Stil
angepasst. Dank PDFVisualEnhancer  in pdf_styles  können wir definierte Farbschemata
für Charts nutzen (z.B. modern mit Blau-Tönen, eco mit Grün-Tönen) 9 . Diese Themes werden
mit Matplotlib/Seaborn verbunden, sodass die Balken, Linien und Beschriftungen in den
firmenkonformen Farben erscheinen. Zusätzlich wird darauf geachtet, dass z.B. alle Diagramm-
Schriftarten mit den PDF-Schriften übereinstimmen (Matplotlib kann via rcParams  auf
Helvetica gesetzt werden). Diagramme erhalten wo sinnvoll eine Legende und Beschriftungen
laut Muster (deutsche Bezeichnungen, Einheitensymbole). 

• Seitenelemente: Falls von Beispiel-PDFs vorgesehen, werden Kopf- oder Fußzeilen hinzugefügt.
Beispielsweise eine Fußzeile mit Firmenname und Seitenzahl („Seite x von y“ in Deutsch) auf jeder
Seite außer Deckblatt. Oder Logos in der Kopfzeile ab Seite 2. Diese Elemente steigern die
Professionalität und werden über ReportLab PageTemplates realisiert (frame on pages). Solche
designtechnischen Feinheiten werden geprüft und entsprechend implementiert. 

• Mehrere Stil-Vorlagen: Aufbauend auf dem Theme-Manager werden mehrere Style-Templates
angeboten. Z.B.: 

• Modern (helles Layout, Blautöne), 
• Elegant (dunkler Hintergrund, weiße Schrift für edlen Look), 
• Öko (grüne Akzente), 

5



• Corporate (neutrales Grau, fokus auf Fakten), etc.
Diese Themes sind in pdf_styles.py  bereits als predefined_themes  angelegt 10  – inkl.
jeweiliger Farben und Schriftennamen. Die Aufgabe besteht darin, sie dynamisch auswählbar
zu machen und konsequent anzuwenden. In der UI (Phase 2) wurde dafür eine Auswahl
geschaffen; hier implementieren wir die Logik: je nach gewähltem Theme lädt 
generate_offer_pdf  das entsprechende Farbprofil und Schriftprofil. Beispielsweise würde 

Elegant Dunkel dunkle Hintergründe und Serifenschrift nutzen 12 , während Öko Grün helle
Grüntöne und klare Sans-Serif-Schrift hat 13 . Neue Themes können einfach hinzugefügt
werden, indem man den Dictionary-Eintrag im Theme-Manager ergänzt – so ist das System
zukunftssicher erweiterbar. 

• Template-spezifisches Layout: Neben Farben/Schriften können auch Layouts leicht variieren
zwischen Vorlagen. Denkbar: Im Template Elegant werden Kapitel-Seiten mit ganzseitigem
Hintergrundbild und weißer Schrift gestaltet, während Modern eher klassisch weiß ist. Solche
Unterschiede werden im Code mittels Template-bezogener Bedingungen umgesetzt. Das 
layout -Attribut im Theme (z.B. 'clean'  vs 'sophisticated'  in den vordefinierten

Themes 14 15 ) könnte genutzt werden, um bestimmte Layout-Stile zu variieren (z.B. Position
des Logos, Stil der Aufzählungen etc.). 

Ergebnis von Phase 4: Das PDF-Ausgabesystem erzeugt Angebote,  die  optisch überzeugend sind:
modernes Layout, konsistente Verwendung von Farben/Schrift, gute Lesbarkeit und Anmutung nahe an
den Referenz-PDFs. Der Nutzer kann zwischen mehreren Design-Vorlagen wählen, was Flexibilität für
verschiedene Zielgruppen bietet. Durch die klare Trennung von Inhalt und Stil (über pdf_styles  und
Themes) bleibt das System erweiterbar – zukünftige Design-Updates können ohne Änderung der Inhalt-
Logik erfolgen.

Phase 5: Erweiterte Funktionen – Multi-Offers & Sicherheit
(Priorität: Mittel)
Ziele: Umsetzung  von  fortgeschrittenen  Features:  Multi-Firmen-Angebote (gleichzeitiges  Erstellen
mehrerer Angebote) und PDF-Passwortschutz. Diese Funktionen ergänzen das Kernsystem und bieten
zusätzlichen Nutzen, ohne die Kern-Generierung zu verändern.

• Multi-Offer Generator Integration: Die App verfügt bereits über ein Modul 
multi_offer_generator.py , das Angebote für mehrere Firmen erstellen kann (z.B. um ein

Projekt an mehrere Installateur-Firmen auszuschreiben) 16 . In Phase 5 wird dieses Modul
nahtlos mit dem neuen PDF-System verheiratet. Konkret: 

• Gemeinsame Konfiguration: Die Schritte 1–3 des Multi-Offer-Moduls (Kundendaten,
Firmenauswahl, Konfiguration) werden so erweitert, dass in Schritt 3 (Konfiguration) die
gleichen PDF-Einstellungsoptionen zur Verfügung stehen wie im Einzel-Angebot 17 18 . Der/
die Nutzer:in soll pro Durchlauf der Konfiguration das Template, Titelbild, und die gewünschten
Module festlegen, die dann für alle ausgewählten Firmenangebote gelten. (Optional könnte man
auch differenzieren, aber zunächst Einheitlichkeit pro Multi-Run). 

• PDF-Erstellung in Schleife: In Schritt 4 generiert dann generate_multi_offers()  für jede
ausgewählte Firma ein PDF durch Aufruf von generate_offer_pdf  mit den jeweiligen
Firmendaten. Alle PDFs werden gesammelt (z.B. in einer Liste von Bytes). Die bestehende
Implementierung schreibt alle PDFs in eine ZIP-Datei und bietet diese zum Download an 19 .
Diese Logik bleibt erhalten, wird aber dahingehend geprüft, dass auch Stilvorlagen und Namen
korrekt berücksichtigt sind – z.B. Dateiname enthält den Firmenname für klare Unterscheidung. 

• Performance & Limits: Wenn viele Firmen (z.B. >10) ausgewählt sind, muss die Generierung
effizient bleiben. Durch Caching der Analyse-Ergebnisse und parallele Verarbeitung (optional via

6



Threads oder einfach sequenziell) wird die Wartezeit minimiert. Der Preview-Modus wird für
Multi-Offers eventuell deaktiviert oder vereinfacht (man könnte eine Vorschau pro PDF schwer
realisieren; stattdessen evtl. nur Hinweis “X PDFs werden erstellt”). 

• UI-Anpassungen: Das Multi-Offer-UI wird überprüft, um sicherzustellen, dass es die neuen
Felder aufnehmen kann, ohne unübersichtlich zu werden. Evtl. wird ein Accordion-Element oder
Tabs genutzt: “Allgemeine Einstellungen” vs “PDF-Einstellungen”. So kann der/die Nutzer:in in
Multi-Offer ähnlich bequem alles einstellen. 

• Testen: Insbesondere wird getestet, ob alle generierten PDFs korrekt und vollständig sind. Auch
Randfälle  wie  fehlende  Firmendaten  für  eine  Firma  (dann  evtl.  Warnung  je  Firma  ins  PDF
einbauen) müssen gehandhabt werden, damit der Batch-Prozess robust ist. 

• Passwortgeschützte PDFs: Für  Angebote,  die vertrauliche Daten enthalten,  soll  optional  ein
Lesepasswort gesetzt werden können. Umsetzung: 

• In der UI (Phase 2) gibt es ein Feld/Checkbox “PDF mit Passwort schützen”. Wenn aktiviert, kann
der/die Nutzer:in ein Passwort eingeben. 

• Bei der PDF-Generierung wird dieses Passwort an das PDF-Toolkit übergeben. Mit ReportLab
kann z.B. das Canvas-Objekt mit einem Passwort initialisiert werden ( canvas.Canvas(..., 
encrypt=password) ), sodass die PDF-Datei verschlüsselt gespeichert wird 20 . Alternativ
könnte PyPDF2 nachträglich das PDF verschlüsseln, aber die ReportLab-Lösung ist direkter. 

• Ergebnis: Der Empfänger muss beim Öffnen des PDFs das Passwort eingeben; ohne Passwort
bleibt es verschlüsselt. Wichtig: Das User-Passwort wird gesetzt (fürs Öffnen), ein Owner-
Passwort kann intern generiert werden, um Bearbeitungsrechte zu steuern 21 . Standardmäßig
wird lediglich der Lesezugriff geschützt, Druck/Kopier-Sperren sind zunächst nicht erforderlich
(könnten aber als Option später kommen). 

• Integration ins Multi-Offer: Wenn mehrere PDFs auf einmal erstellt werden, kann entweder ein
gemeinsames Passwort für alle verwendet werden (einfacher für Nutzer) oder je Firma ein
unterschiedliches (falls z.B. an verschiedene Empfänger versendet). Erstmal wird eine globale
Passworteingabe für den Multi-Run angenommen, die dann auf alle PDFs angewandt wird. In
der ZIP-Datei sind dann alle PDFs geschützt. 

• UX & Sicherheit: Bei Aktivierung des Passwortschutzes sollten Hinweise angezeigt werden, z.B.
“⚠  Stellen Sie sicher, das Passwort dem Kunden sicher mitzuteilen.” Das Passwort selbst wird
nicht  im  Klartext  gespeichert  (nur  zur  Laufzeit  verwendet).  Nach  Generierung  wird  das
Eingabefeld geleert aus Sicherheitsgründen. 

• Flexible  Textvorlagen  (Tonalität  &  Ansprache): Ergänzend  wird  das  System  für  variable
Textbausteine vorbereitet. Dies betrifft insbesondere das Anschreiben: In Phase 3 wurde bereits
vorgesehen, dass verschiedene Tonalitäten genutzt werden können. Hier in Phase 5 werden die
Vorlagen tatsächlich hinterlegt und die UI-Option mit Leben gefüllt:

• Es werden z.B. drei Begrüßungs-Textmodule erstellt: technisch-sachlich, freundlich-beratungsvoll, 
direkt-auf-den-Punkt. Diese liegen als Vorlagentexte (in Deutsch) im texts -Dictionary oder in
einer externen JSON. 

• Wählt der Nutzer eine Tonalität aus, lädt das System den passenden Textbaustein, fügt
Kundenname und evtl. Projektreferenz dynamisch ein, und zeigt ihn im Anschreiben-Editor an,
wo er noch angepasst werden kann. 

• Auch Anrede-Form (Du/Sie) könnte hierüber gesteuert werden: Ein Toggle “informell” würde die
Du-Variante laden. Da die gesamte App auf Deutsch/Sie ausgelegt scheint, könnte Du optional
sein – nur falls gewünscht vom Firmenuser. 

7



• Diese Mechanik erhöht die Individualisierbarkeit weiter und trägt dem Kundenwunsch nach
passender Ansprache Rechnung. Technisch ist es leicht integrierbar, da texts  bereits
verwendet wird, man muss nur entsprechende Keys definieren (z.B. 
cover_letter_friendly , cover_letter_formal ) und in der UI Auswahl anbieten. 

Ergebnis  von  Phase   5: Das  PDF-System  deckt  jetzt  auch  spezielle  Anwendungsfälle  ab.  Mehrere
Angebote lassen sich in einem Rutsch erzeugen, was bei größeren Projekten Zeit spart. Zudem kann
jedes PDF auf Wunsch mit Passwort geschützt werden, um sensible Informationen zu sichern. Durch die
flexible  Textbaustein-Verwendung  ist  auch  die  Ansprache im  Dokument  anpassbar  (Corporate
Wording).  Diese Features steigern den  professionellen Anspruch der  Anwendung weiter,  ohne die
Kernfunktionalität zu beeinträchtigen.

Phase 6: Systemintegration, Tests & Roll-out (Priorität: Hoch)
Ziele: Finale  Qualitätssicherung,  Performance-Optimierung  und  reibungslose  Integration  ins
bestehende Framework, bevor das neue PDF-System live geht.

• Umfassende Tests: Alle Komponenten werden einzeln und im Zusammenspiel getestet. Unit-
Tests für modulare Funktionen (z.B. erzeugt _build_financial_table  korrekte Tabellen
auch bei Sonderfällen wie fehlenden Daten?). Integrationstests via Streamlit-Simulation, um
sicherzustellen, dass UI-Einstellungen tatsächlich die gewünschte PDF-Ausgabe ergeben. 
Testfälle umfassen:

• Verschiedene Kombinationen von gewählten Modulen (nur ein Modul, alle Module, zufällige
Teilmengen).

• Alle Designvorlagen durchprobieren – Überprüfung, dass Farben/Schriften tatsächlich
übernommen wurden und nichts überlappt oder falsch skaliert ist.

• Grenzfälle wie extrem lange Texte (prüfen, ob sie mehrseitig umbrechen und ob
Seitennummerierung passt), sehr viele Produkte (mehrere Seiten Produktliste), sehr große
Zahlenwerte etc.

• Multi-Offer mit 2, 5, 10 Firmen – PDFs kommen alle an, stimmen inhaltlich je Firma und sind
korrekt benannt.

• Passwort-PDF öffnen mit richtigem/falschem Passwort – sicherstellen, dass Verschlüsselung
greift.

• Backward-Compatibility: Test eines bestehenden Workflows, der nur das Standard-PDF mit
Defaults erzeugt (als Vergleich: alte vs. neue Ausgabe). Dabei sollte kein Fehler auftreten und das
Ergebnis sinnvoll bleiben (ggf. minimal andere Optik, aber akzeptabel). 

• Performance & Optimierung: Messen der PDF-Generierungsdauer für typische Fälle. Falls
nötig, Optimierungen durchführen, z.B.:

• Caching von Charts-Bildern, wenn die gleiche Grafik mehrfach gebraucht wird.
• Bei Mehrfach-PDF Erstellung gemeinsame Schritte (Analyse nur einmal berechnen, dann in alle

einfügen).
• Bildkompression einstellen: z.B. JPEG-Kompression für eingebettete Fotos, um die Dateigröße

klein zu halten, ohne sichtbaren Qualitätsverlust.
• Speichermanagement: sicherstellen, dass große Objekte (Bilder, PDFs) aus dem Speicher

freigegeben werden (gerade bei multi_offer wichtig, um Memory nicht zu sprengen). 
• Dokumentation: Parallel zum Testen wird die interne Dokumentation erstellt/aktualisiert:
• Code-Doku: Kommentare und Docstrings zu allen neuen Funktionen (besonders in 
pdf_generator.py  für die Modul-Funktionen, damit künftige Entwickler wissen, wie Inhalte

erzeugt werden). 
• README/Handbuch: Beschreibung der PDF-Konfigurationsmöglichkeiten für Anwender (z. B. als

Teil des User Manuals der App: “So erstellen Sie ein Angebot – Schritt 3: PDF gestalten...”). Auch

8



Hinweise zu Passwortschutz und dessen Grenzen (kein absoluter Schutz vor Weitergabe, aber
zumindest erschwert). 

• Konfigurationsanleitung für Templates: Falls der Betreiber später neue Themes hinzufügen
will, sollte eine Anleitung existieren, wie man pdf_styles.py  erweitert oder eine neue
Farbpalette definiert. Da das System modular ist, können so auch Nicht-Entwickler (mit JSON-
Konfiguration) neue Designs einspielen – das sollte dokumentiert sein. 

• Deployment & Roll-out: Nach bestandenen Tests wird das neue System in die App integriert.
Möglicherweise wird es zunächst als Beta-Feature ausgerollt (z. B. nur für Admins sichtbar) um
Feedback einzuholen. Dann erfolgt der vollständige Roll-out an alle Nutzer. 

• Migration: Etwaige Migrationsschritte, z.B. neue Datenbankfelder für gespeicherte PDF-
Einstellungen oder hinterlegte Dokumente, werden in dieser Phase durchgeführt. Bestehende
Angebote/Daten bleiben unberührt. 

• Monitoring: Nach Go-Live wird besonders auf Fehlerlogs der PDF-Generierung geachtet. Sollte
ein Fehler auftreten (z. B. ein Sonderzeichen im Text, das ein Encoding-Problem verursacht), wird
schnell ein Fix nachgeschoben – dank der modularen Struktur meist lokal begrenzbar. 

• Backup-Lösung: Für den Notfall (falls schwerwiegende Probleme auftreten) steht das alte PDF-
System ggf. noch als Fallback zur Verfügung, bis der neue stabil läuft – aber Ziel ist natürlich, den
neuen vollständig zu übernehmen, da er rückwärtskompatibel implementiert ist.

Nach  Phase   6  ist  das  PDF-Ausgabe-System offiziell  fertiggestellt  und  bildet  das  Herzstück  der
Photovoltaik-App in finaler Ausprägung: flexibel, individuell anpassbar und professionell gestaltet.

Zukünftige Erweiterungen (Ausblick)
Abschließend werden mögliche  Erweiterungen aufgeführt,  die in späteren Versionen berücksichtigt
werden können, um das PDF-System noch weiter aufzuwerten:

• Digitale Signatur des PDFs: Integration einer digitalen Unterschrift des Anbieters direkt im PDF.
Dies kann eine einfache eingescannte Unterschrift sein, die am Ende des Anschreibens platziert
wird, oder sogar eine qualifizierte elektronische Signatur (z.B. X.509-Zertifikat), um das
Dokument rechtlich verbindlich zu machen. Umsetzung erfordert entweder die Nutzung von
Bibliotheken wie PyPDF2/PyMuPDF zur Zertifikatsanbringung oder Anbindung an einen externen
Signing-Service. 

• Direkter PDF-Versand (API/E-Mail): Nach Erstellung des PDFs könnte die App das Dokument
direkt an den Kunden versenden. Eine Integration mit einem E-Mail-Service (z.B. SMTP oder API
von SendGrid) würde ermöglichen, dass der Nutzer mit einem Klick das Angebot als E-Mail-
Anhang versendet. Alternativ könnte eine API bereitgestellt werden, um das PDF an andere
Systeme zu übertragen (etwa CRM oder Dokumentenmanagement). Dabei ist zu beachten, dass
bei Passwort-geschützten PDFs das Passwort sicher übermittelt werden muss (z.B. in separater
Mail oder telefonisch). 

• Interaktive PDF-Formulare: Ein weiterer Schritt wären PDF-Formulare, in denen der Kunde
direkt Angaben machen oder das Angebot elektronisch annehmen kann. Z.B. ein
Unterschriftsfeld oder Checkboxen für Optionen. ReportLab kann Form-Fields erstellen, jedoch
ist die Umsetzung komplexer. Dieses Feature würde den Angebotsprozess noch digitaler
gestalten (Kunde kann ohne Drucken/Scannen reagieren). 

• Weitere Inhaltsmodule: Die modulare Architektur erlaubt es, leicht neue Abschnitte
hinzuzufügen. Denkbar wären z.B. Simulationsergebnisse (Graphiken zur
Verschattungsanalyse), Wartungsangebote, Finanzierungsoptionen etc., je nach zukünftigen
Anforderungen der App. Dank der Trennung in UI-Option und Generator-Funktion müsste man
nur einen neuen UI-Schalter hinzufügen und die entsprechende PDF-Render-Funktion
implementieren. 

9



• Multi-Language Support: Bisher ist das System auf Deutsch ausgerichtet. In Zukunft könnte
eine Mehrsprachigkeit unterstützt werden, um etwa Angebote auf Englisch oder anderen
Sprachen zu erstellen. Die Grundlage mit texts -Dictionary ist bereits vorhanden; es müssten
dann Übersetzungen aller Textbausteine gepflegt und eine Sprachauswahl in der UI angeboten
werden. Layout-Technisch müsste man prüfen, ob z.B. längere englische Texte das Design
beeinflussen (ggf. kleinere Schrift oder Anpassung von Tabellenbreiten). 

• Feingranularer Berechtigungsschutz: Aufbauend auf dem Passwortschutz ließe sich die PDF-
Sicherheit weiter erhöhen durch Einstellen von Berechtigungen (z.B. Druck sperren, Kopieren
von Text verhindern). Das PDF-Standard-Sicherheitsmodell erlaubt es, über ein Owner-Passwort
solche Einschränkungen zu setzen 22 23 . In einer zukünftigen Version könnte der Admin
festlegen, dass versandte Angebote z.B. nicht druckbar sind, um unkontrollierte Verbreitung
einzuschränken – wobei dies eher ein Randanliegen ist, da der Kunde ja drucken können sollte. 

• Visueller PDF-Editor: Langfristig könnte man dem Nutzer einen noch intuitiveren Weg bieten,
das PDF-Layout zu gestalten – z.B. einen WYSIWYG-Editor im Browser, wo Textblöcke direkt
bearbeitet oder verschoben werden können. Dies wäre ein größeres Projekt (ggf. mittels HTML-
zu-PDF Ansätzen oder spezieller Libraries), aber die jetzige Struktur könnte als Grundgerüst
dienen, da sie bereits Seiten-Widgets kennt. 

Durch  die  Umsetzung  dieser  Erweiterungen  würde  das  PDF-System  noch  leistungsfähiger und
zukunftssicher. Wichtig ist, dass die aktuelle Architektur – modular, konfigurierbar und sauber in die App
integriert  –  diese Ausbaustufen ermöglicht,  ohne von Grund auf neu beginnen zu müssen. Mit  der
finalen Version aus Phase 6 ist eine exzellente Basis geschaffen, auf der diese zusätzlichen Features
aufsetzen können. 

1 6 7 fix_pdf_generation.py
file://file-WgWvjhD4eZMzZfU1RZaYHN

2 3 4 5 pdf_preview.py
file://file-Axg7Gkm2BKsgiG9JRkuyud

8 9 10 11 12 13 14 15 pdf_styles.py
file://file-SFrKgHPR7d5wyAdpyyftcx

16 17 18 19 multi_offer_generator.py
file://file-NXbeSkN82ktUKothqM9g1b

20 django - How do you set a password on a PDF using Python reportlab and buffer from BytesIO -
Stack Overflow
https://stackoverflow.com/questions/65006871/how-do-you-set-a-password-on-a-pdf-using-python-reportlab-and-buffer-
from-bytesi

21 22 23 untitled
https://www.reportlab.com/docs/PdfEncryptIntro.pdf

10