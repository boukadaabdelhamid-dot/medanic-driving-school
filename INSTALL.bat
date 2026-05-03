@echo off
title Medanic Installer
color 0A
cls

echo.
echo  ====================================================
echo            Medanic Driving School - Installer
echo  ====================================================
echo.
echo  Current folder: %~dp0
echo.
pause

echo.
echo  [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo  ERROR: Python is NOT installed
    echo  Download from: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" when installing
    echo.
    pause
    exit /b 1
)
echo       OK
echo.
pause

echo.
echo  [2/3] Installing required libraries (1 minute)...
pip install reportlab arabic-reshaper python-bidi pillow
if errorlevel 1 (
    echo.
    echo  ERROR: Failed to install libraries
    echo.
    pause
    exit /b 1
)
echo       OK
echo.
pause

echo.
echo  [3/3] Creating Desktop shortcut...

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $desk = [Environment]::GetFolderPath('Desktop'); $lnk = $ws.CreateShortcut(\"$desk\Medanic.lnk\"); $lnk.TargetPath = 'pythonw.exe'; $lnk.Arguments = '\"%APP_DIR%\driving_school_single.py\"'; $lnk.WorkingDirectory = '%APP_DIR%'; $lnk.IconLocation = '%APP_DIR%\medanic_icon.ico'; $lnk.Save()"

if errorlevel 1 (
    echo  ERROR: Failed to create shortcut
    pause
    exit /b 1
)

echo       OK
echo.
echo  ====================================================
echo                 INSTALLATION COMPLETE
echo  ====================================================
echo.
echo   A "Medanic" icon was created on your Desktop
echo   Double-click it to open the program
echo.
pause
