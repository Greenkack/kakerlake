@echo off
chcp 65001 >nul
title UPX Komprimierung für Ömers Solar Dingel Dangel

echo.
echo 📦 UPX Komprimierung für Ömers Solar Dingel Dangel
echo ===================================================
echo.

rem Prüfe ob UPX verfügbar ist
where upx >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ UPX nicht gefunden!
    echo.
    echo Bitte installieren Sie UPX:
    echo 1. Download von: https://upx.github.io/
    echo 2. upx.exe nach C:\Windows\System32 kopieren
    echo 3. Oder UPX-Pfad zu PATH hinzufügen
    pause
    exit /b 1
)

rem Finde die EXE
set "EXE_PATH=dist\OemersSolarDingelDangel.exe"
if not exist "%EXE_PATH%" (
    echo ❌ EXE nicht gefunden: %EXE_PATH%
    echo.
    echo Bitte zuerst die EXE erstellen:
    echo python build_exe.py
    pause
    exit /b 1
)

rem Zeige Original-Größe
echo 📏 Original-Größe:
for %%i in ("%EXE_PATH%") do (
    set /a "size_mb=%%~zi / 1024 / 1024"
    echo   %%~zi Bytes (~!size_mb! MB)
)

rem Backup erstellen
echo.
echo 💾 Erstelle Backup...
copy "%EXE_PATH%" "%EXE_PATH%.backup" >nul
if %errorlevel% neq 0 (
    echo ❌ Backup fehlgeschlagen!
    pause
    exit /b 1
)

rem Komprimierungs-Level auswählen
echo.
echo 🗜️ Wählen Sie Komprimierungs-Level:
echo   1) --best (empfohlen, ~65-75%% Ersparnis)
echo   2) -9 (schneller, ~60-70%% Ersparnis)
echo   3) -6 (standard, ~50-60%% Ersparnis)
echo   4) -1 (schnell, ~40-50%% Ersparnis)
echo.

set /p "choice=Ihre Wahl [1-4, Enter für 1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" set "level=--best"
if "%choice%"=="2" set "level=-9"
if "%choice%"=="3" set "level=-6"
if "%choice%"=="4" set "level=-1"

echo.
echo 🗜️ Starte UPX Komprimierung mit %level%...
echo.

rem UPX Komprimierung
upx %level% --lzma "%EXE_PATH%"

if %errorlevel% equ 0 (
    echo.
    echo ✅ UPX Komprimierung erfolgreich!
    echo.
    
    rem Zeige neue Größe
    echo 📏 Komprimierte Größe:
    for %%i in ("%EXE_PATH%") do (
        set /a "new_size_mb=%%~zi / 1024 / 1024"
        echo   %%~zi Bytes (~!new_size_mb! MB)
    )
    
    rem UPX Info
    echo.
    echo 💡 UPX Details:
    upx -l "%EXE_PATH%"
    
    echo.
    echo 🎉 Komprimierung abgeschlossen!
    echo.
    echo 📁 Verfügbare Dateien:
    echo   %EXE_PATH% (komprimiert)
    echo   %EXE_PATH%.backup (original)
    echo.
    echo 💡 Tipp: Testen Sie die komprimierte EXE gründlich!
    
) else (
    echo.
    echo ❌ UPX Komprimierung fehlgeschlagen!
    echo.
    echo 🔄 Stelle Original wieder her...
    copy "%EXE_PATH%.backup" "%EXE_PATH%" >nul
    if %errorlevel% equ 0 (
        echo ✅ Original wiederhergestellt
        del "%EXE_PATH%.backup" >nul
    )
)

echo.
pause
