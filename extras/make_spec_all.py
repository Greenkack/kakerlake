#!/usr/bin/env python3
"""
make_spec_all.py
Erzeugt eine PyInstaller-Spec, die
• ALLE Pakete auf **jedem** sys.path-Verzeichnis einsammelt
• ALLE *.py-Dateien im Projektordner als Data-Files hinzufügt
• OmersSolarDingelDangel.exe mit Icon baut
"""

import sys, os, textwrap, site, pathlib
import importlib.metadata as meta

ROOT        = pathlib.Path(__file__).resolve().parent      # Projektordner
APP_NAME    = "OmersSolarDingelDangel"
ICON_NAME   = "Omer.ico"
ENTRYPOINT  = "start_app.py"
SPEC_FILE   = "start_app.spec"

# --------------------------------------------------------------------------
# 1) Sämtliche site-packages-Verzeichnisse zusammenstellen
# --------------------------------------------------------------------------
paths = set(site.getsitepackages()) | {
    *sys.path,                      # venv + global + Arbeitsordner
    pathlib.Path(sys.base_prefix, "Lib", "site-packages"),
    pathlib.Path(sys.base_prefix, "lib", "site-packages"),  # Linux/mac
}

# Pfade nur behalten, die existieren
pkg_paths = [str(p) for p in paths if pathlib.Path(p).exists()]

# --------------------------------------------------------------------------
# 2) Alle Pakete aus *allen* Pfaden einsammeln
# --------------------------------------------------------------------------
pkgnames = set()
for p in pkg_paths:
    for dist in meta.distributions(path=[p]):
        pkgnames.add(dist.metadata["Name"])

print(f"📦 Insgesamt gefundene Pakete: {len(pkgnames)}")

# --------------------------------------------------------------------------
# 3) Spec-Template erzeugen
# --------------------------------------------------------------------------
pkg_line = ", ".join(f"'{n}'" for n in sorted(pkgnames, key=str.lower))

spec_template = f"""
# {SPEC_FILE} – automatisch von make_spec_all.py generiert
# -*- mode: python ; coding: utf-8 -*-

import sys, pathlib, traceback
from PyInstaller.utils.hooks import (
    collect_submodules, collect_data_files,
    collect_dynamic_libs, copy_metadata
)

ROOT = pathlib.Path(__file__).resolve().parent

INSTALLED_PACKAGES = [{pkg_line}]

hidden, datas, binaries, metadata = [], [], [], []
for pkg in INSTALLED_PACKAGES:
    try:
        hidden   += collect_submodules(pkg)
        datas    += collect_data_files(pkg)
        binaries += collect_dynamic_libs(pkg)
        metadata += copy_metadata(pkg)
    except Exception as exc:
        print(f'⚠ {{pkg}}: {{exc}}')
        traceback.print_exc()

#  Alle .py-Dateien im Projektordner als Data-Files
for p in ROOT.glob('*.py'):
    if p.name != '{ENTRYPOINT}':
        datas.append((str(p), '.'))

icon_path = ROOT / '{ICON_NAME}'
if not icon_path.exists():
    print('⚠ Icon fehlt – EXE ohne Icon')
    icon_path = None

a = Analysis(
    ['{ENTRYPOINT}'],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas + metadata,
    hiddenimports=hidden + ['pandas._libs.tslibs.conversion'],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz, a.scripts,
    name='{APP_NAME}',
    icon=str(icon_path) if icon_path else None,
    console=False,
    upx=True,
)
print('✅ Spec geschrieben – jetzt "pyinstaller --clean --noconfirm {SPEC_FILE}" ausführen')
"""

# --------------------------------------------------------------------------
# 4) Datei schreiben
# --------------------------------------------------------------------------
(ROOT / SPEC_FILE).write_text(textwrap.dedent(spec_template), encoding="utf-8")
print(f"{SPEC_FILE} erfolgreich erstellt unter {ROOT}")
