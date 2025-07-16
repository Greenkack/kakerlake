@echo off
rem ============================================================
rem  Ein-Klick-Builder  –  erzeugt Setup-EXE unter .\dist
rem ============================================================
setlocal EnableDelayedExpansion

rem ---- 1) One-File-EXE bauen -------------------------------
call :msg "Baue PyInstaller-EXE …"
py -3.12 -m pip install --quiet --upgrade pyinstaller >nul
py -3.12 -m pyinstaller --noconfirm --onefile ^
    --icon Omer.ico ^
    --paths . ^
    gui.py || goto :err
if not exist dist\OmersSolarDingelDangel.exe (
    ren dist\gui.exe OmersSolarDingelDingel.exe
)
call :msg "✓ EXE fertig."

rem ---- 2) Constructor-Setup bauen --------------------------
call :msg "Baue Constructor-Installer …"
if not exist "%USERPROFILE%\.conda\constructor" md "%USERPROFILE%\.conda\constructor" >nul
constructor --verbose --output-dir dist .
if errorlevel 1 goto :err

call :msg "===== FERTIG ====="
echo Setup liegt in dist\OmersSolarDingelDangel-*.exe
pause
endlocal & exit /b 0

:msg
echo.
echo ********** %~1
echo.
exit /b 0

:err
echo.
echo *** FEHLER – Log oben pruefen!
pause
exit /b 1
