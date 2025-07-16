# app_status.py
from typing import List

# Globale Liste für Importfehler, die von verschiedenen Modulen genutzt werden kann.
import_errors: List[str] = []

# Hier könnten später weitere globale Statusvariablen der Anwendung hinzukommen,
# die von mehreren Modulen geteilt werden müssen, ohne zirkuläre Importe zu erzeugen.