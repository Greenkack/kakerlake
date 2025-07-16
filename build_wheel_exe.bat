@echo off
echo ========================================
echo   OmersSolarDingelDangel EXE Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Install required build tools
echo Installing required build tools...
pip install --upgrade pip
pip install build wheel pyinstaller

REM Run the build script
echo.
echo Starting build process...
python build_wheel_exe.py

echo.
echo Build process completed!
pause
