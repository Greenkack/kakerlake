#!/usr/bin/env python3
"""
Setup.py für Ömers Solar Dingel Dangel oder soo
Autor: Analysiert von GitHub Copilot
Datum: 19. Juni 2025
"""

from setuptools import setup, find_packages
import os

# Version aus gui.py extrahieren oder statisch setzen
VERSION = "1.0.0"

# README.md lesen falls vorhanden
long_description = "Ömers Solar Dingel Dangel oder soo - Photovoltaik Kalkulationssoftware mit PDF-Generierung"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

# Requirements aus Analyse
REQUIRED_PACKAGES = [
    "streamlit>=1.28.0",
    "pandas>=1.5.0", 
    "numpy>=1.24.0",
    "plotly>=5.15.0",
    "reportlab>=4.0.0",
    "requests>=2.31.0",
    "openpyxl>=3.1.0",
    "Pillow>=9.5.0",  # Für Bildverarbeitung
]

# Optionale Pakete
OPTIONAL_PACKAGES = [
    "streamlit-shadcn-ui>=0.2.0",
    "pypdf>=3.15.0",
    "PyPDF2>=3.0.1",
    "kaleido>=0.2.1",
]

setup(
    name="oemers-solar-dingel-dangel",
    version=VERSION,
    author="Ömer",
    author_email="", # Ihre E-Mail hier
    description="Ömers Solar Dingel Dangel oder soo - Photovoltaik Kalkulationssoftware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="", # Ihr Repository hier
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=REQUIRED_PACKAGES,
    extras_require={
        "full": OPTIONAL_PACKAGES,
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.json",
            "*.csv", 
            "*.xlsx",
            "*.db",
            "data/*",
            "data/**/*",
            "*.md",
            "*.txt",
        ],
    },    entry_points={
        "console_scripts": [
            "oemers-solar-dingel-dangel=gui:main",  # Kommandozeilen-Einstieg
        ],
    },
    zip_safe=False,  # Wichtig für Streamlit
    keywords="ömer solar dingel dangel photovoltaik kalkulation",
)
