@echo off
REM ============================================================
REM  Build-Skript: Ömers Solar Dingel Dangel  ►  dist\gui.exe
REM ============================================================
setlocal

set "APP_NAME=OemersSolarDingelDangel"
set "ENTRY_SCRIPT=execute_app.py"
set "ICON=assets\icon.ico"
set "EXTRA_DATA=assets;assets"

REM ---------- Alte Artefakte sauber löschen ----------
if exist build rd /s /q build
if exist dist  rd /s /q dist
if exist %APP_NAME%.spec del /q %APP_NAME%.spec

REM ---------- PyInstaller-Aufruf ----------
pyinstaller ^
   "%ENTRY_SCRIPT%" ^
   --noconfirm --onefile ^
   --icon "%ICON%" ^
   --add-data "%EXTRA_DATA%" ^
   --paths . ^
   ^
   REM ===== alle collect-all / copy-metadata Aufrufe (wie schon vorhanden) =====
   --collect-all adlfs --copy-metadata adlfs ^
   --collect-all aiobotocore --copy-metadata aiobotocore ^
   ... (deine komplette Liste bleibt unverändert) ...
   --collect-all zope.interface --copy-metadata zope.interface ^
   ^
   REM =======  ✦ Eigene Module als hidden-imports ✦  =======
   --hidden-import=locales ^
   --hidden-import=database ^
   --hidden-import=product_db ^
   --hidden-import=data_input ^
   --hidden-import=calculations ^
   --hidden-import=analysis ^
   --hidden-import=crm ^
   --hidden-import=admin_panel ^
   --hidden-import=pdf_ui ^
   --hidden-import=quick_calc ^
   --hidden-import=options ^
   --hidden-import=pv_visuals ^
   --hidden-import=ai_companion ^
   --hidden-import=multi_offer_generator ^
   --hidden-import=add_company_id_column ^
   --hidden-import=ai_models ^
   --hidden-import=analyze_pdf_debug ^
   --hidden-import=analyze_session_state ^
   --hidden-import=app_status ^
   --hidden-import=check_db ^
   --hidden-import=check_db_column ^
   --hidden-import=check_lines ^
   --hidden-import=check_matrix_db ^
   --hidden-import=check_products ^
   --hidden-import=debug_integration_snippet ^
   --hidden-import=debug_pdf_validation ^
   --hidden-import=doc_output ^
   --hidden-import=financial_tools ^
   --hidden-import=fix_pdf_generation ^
   --hidden-import=fix_pdf_generation_simple ^
   --hidden-import=gui_clean ^
   --hidden-import=gui_integration_test ^
   --hidden-import=gui_new ^
   --hidden-import=info_platform ^
   --hidden-import=local_storage ^
   --hidden-import=map_integration ^
   --hidden-import=pdf_debug_widget ^
   --hidden-import=pdf_generator_cleaned ^
   --hidden-import=pdf_preview ^
   --hidden-import=pdf_status_widget ^
   --hidden-import=pdf_styles ^
   --hidden-import=pdf_widgets ^
   --hidden-import=scenario_manager ^
   --hidden-import=session_state_detective ^
   --hidden-import=session_state_fix ^
   --hidden-import=test_design_simple ^
   --hidden-import=test_new_features ^
   --hidden-import=update_tariffs ^
   --hidden-import=utils ^
   --hidden-import=variant_input

echo.
echo ============================================================
echo  Fertig!  →  dist\gui.exe erzeugt
echo ============================================================
pause
endlocal
