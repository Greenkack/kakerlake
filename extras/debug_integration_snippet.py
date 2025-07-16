# PDF DEBUG INTEGRATION - Füge diesen Code in deine doc_output.py ein

# Am Anfang der Datei, bei den Imports:
try:
    from pdf_debug_widget import integrate_pdf_debug
    DEBUG_AVAILABLE = True
except ImportError:
    DEBUG_AVAILABLE = False

# In der render_pdf_ui Funktion, direkt nach dem Header:
def render_pdf_ui(
    texts: Dict[str, str],
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any],
    # ... andere Parameter
):
    st.header(get_text_pdf_ui(texts, "menu_item_doc_output", "Angebotsausgabe (PDF)"))
    
    # DEBUG WIDGET INTEGRATION - Füge diese Zeilen ein:
    if DEBUG_AVAILABLE:
        integrate_pdf_debug(project_data, analysis_results, texts)
    
    # Rest der ursprünglichen Funktion...
    # DATENSTATUS-ANZEIGE
    data_sufficient = _show_pdf_data_status(project_data, analysis_results, texts)
    # ... usw.
