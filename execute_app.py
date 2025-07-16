"""
Wrapper-Starter für PyInstaller-Builds.
Er startet deine Streamlit-App genauso, als würdest du `streamlit run app.py`
in der Shell eintippen – nur eben aus einer EXE heraus.
"""
from __future__ import annotations # MUSS DIE ALLERERSTE CODE-ZEILE SEIN

import importlib
import traceback
from typing import Any, Callable, Dict, List, Optional, IO, Union
import io
import math
import pandas as pd
import streamlit as st
import json
import os, sys
from streamlit.web import cli as stcli

# Import streamlit_shadcn_ui with fallback
try:
    import streamlit_shadcn_ui as sui
    SUI_AVAILABLE = True
except ImportError:
    SUI_AVAILABLE = False
    sui = None


# Globale Importfehlerliste
import_errors: List[str] = []

# Initialtexte laden
_texts_initial: Dict[str, str] = {}

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(base_dir)                         # sicheres CWD
    sys.argv = [
        "streamlit", "run", "gui.py",
        "--server.port=8501",
        "--global.developmentMode=false",
        "--logger.level=info",
    ]
    sys.exit(stcli.main())
