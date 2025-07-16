import os, sys
try:
    import streamlit.web.cli as stcli
except ModuleNotFoundError:
    import streamlit.cli as stcli                        # Fallback < 1.28

def _base() -> str:
    return sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__)

def main():
    gui = os.path.join(_base(), "gui.py")
    sys.argv = ["streamlit", "run", gui, "--server.headless", "true",
                "--server.port", "8501"]
    stcli.main()

if __name__ == "__main__":
    main()
