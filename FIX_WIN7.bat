@echo off
title Medanic - Fix System Error
color 0E
cls

echo.
echo  ====================================================
echo         Medanic - Fix DLL Error
echo         اصلاح خطا في الويندوز
echo  ====================================================
echo.
echo  This will install Microsoft Visual C++ Runtime
echo  (required to run Medanic on your computer)
echo.
echo  سيتم تثبيت مكتبات النظام المطلوبة
echo  الحجم: حوالي 25 MB - يحتاج انترنت
echo.
pause

REM ── التحقق من الإنترنت ────────────────────────────────
echo.
echo  Checking internet connection...
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERROR: No internet connection
    echo  يرجى الاتصال بالانترنت أولاً
    pause
    exit /b 1
)
echo  OK - Connected

REM ── تحميل وتثبيت VC++ Redistributable ───────────────
echo.
echo  Downloading Microsoft Visual C++ Runtime...
echo  (please wait - جاري التحميل)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%TEMP%\vc_redist.x64.exe'"

if not exist "%TEMP%\vc_redist.x64.exe" (
    color 0C
    echo.
    echo  ERROR: Download failed
    echo  فشل التحميل - تحقق من الانترنت
    pause
    exit /b 1
)

echo  Installing... (may take 1-2 minutes)
echo  جاري التثبيت...
echo.

"%TEMP%\vc_redist.x64.exe" /install /quiet /norestart

if errorlevel 1 (
    REM Try x86 version for 32-bit Windows
    echo  Trying 32-bit version...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x86.exe' -OutFile '%TEMP%\vc_redist.x86.exe'"
    "%TEMP%\vc_redist.x86.exe" /install /quiet /norestart
)

del /Q "%TEMP%\vc_redist.x64.exe" 2>nul
del /Q "%TEMP%\vc_redist.x86.exe" 2>nul

color 0A
echo.
echo  ====================================================
echo            تم التثبيت بنجاح
echo            Installation Complete!
echo  ====================================================
echo.
echo  الان افتح برنامج Medanic من سطح المكتب
echo  Double-click the Medanic icon on your Desktop
echo.
echo  اذا ما زالت المشكلة:
echo  Tel / WhatsApp: +213 540 77 28 07
echo.
pause
