#!/usr/bin/env python3
"""
build_nuitka.py
────────────────────────────────────────────────────────
• erstellt eine One-File-EXE (OmersSolarDingelDangel.exe)
  mit allen installierten Paketen + allen .py-Dateien im Projekt
• Icon: Omer.ico
• Ergebnis: dist\OmersSolarDingelDangel.exe
"""

import sys, shlex, subprocess
from pathlib import Path
import importlib.metadata as meta

# ─────────────────────────────
# 1) Projekt-Konstanten
# ─────────────────────────────
ROOT      = Path(__file__).resolve().parent
ENTRY     = "start_app.py"                 # Einstiegspunkt
APP_NAME  = "OmersSolarDingelDangel"
ICON      = ROOT / "Omer.ico"              # Icon muss existieren

# ─────────────────────────────
# 2) Alle Pakete sammeln
# ─────────────────────────────
pkgs = {d.metadata["Name"] for d in meta.distributions()}
include_pkgs = [f"--include-package={name}" for name in sorted(pkgs, key=str.lower)]

# ─────────────────────────────
# 3) Lokale .py-Dateien als Data
# ─────────────────────────────
data_files = [
    f"--include-data-file={p}={p.name}"
    for p in ROOT.glob("*.py")
    if p.name != ENTRY
]

# ─────────────────────────────
# 4) Nuitka-Kommando bauen
# ─────────────────────────────
cmd = [
    sys.executable, "-m", "nuitka",
    "--onefile", "--standalone",
    f"--output-filename={APP_NAME}.exe",      #  ←  '=' wichtig!
    f"--windows-icon-from-ico={ICON}",
    "--disable-console",                      # bei Bedarf entfernen
    "--enable-plugin=implicit-imports",
    "--remove-output",
] + include_pkgs + data_files + [str(ROOT / ENTRY)]

print("\n» Nuitka-Kommando:\n", shlex.join(cmd), "\n")

# ─────────────────────────────
# 5) Build ausführen
# ─────────────────────────────
subprocess.run(cmd, check=True)

dist_exe = ROOT / "dist" / f"{APP_NAME}.exe"
if dist_exe.exists():
    print(f"✅  Build erfolgreich – EXE liegt hier:\n{dist_exe}")
else:
    print("❌  Build beendet, EXE nicht gefunden – siehe Log oben")
