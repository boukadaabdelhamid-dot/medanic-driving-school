@echo off
chcp 65001 >nul
title تثبيت برنامج ميدانيك
color 0A
cls

echo.
echo  ════════════════════════════════════════════════════
echo            تثبيت برنامج ميدانيك على جهازك
echo  ════════════════════════════════════════════════════
echo.

REM ── 1. التحقق من Python ─────────────────────────────────
echo  [1/3] التحقق من Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  ❌ Python غير مثبّت على جهازك
    echo.
    echo  حمّله من: https://www.python.org/downloads/
    echo  ⚠ مهم: ضع علامة على "Add Python to PATH" عند التثبيت
    echo.
    pause
    exit /b 1
)
echo      ✔ Python جاهز
echo.

REM ── 2. تثبيت المكتبات المطلوبة ──────────────────────────
echo  [2/3] تثبيت المكتبات (دقيقة واحدة)...
pip install --quiet reportlab arabic-reshaper python-bidi pillow >nul 2>&1
echo      ✔ المكتبات جاهزة
echo.

REM ── 3. إنشاء اختصار سطح المكتب ───────────────────────────
echo  [3/3] إنشاء اختصار سطح المكتب...

set "APP_DIR=%~dp0"
set "APP_DIR=%APP_DIR:~0,-1%"

powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell;" ^
    "$desk = [Environment]::GetFolderPath('Desktop');" ^
    "$lnk = $ws.CreateShortcut(\"$desk\برنامج ميدانيك.lnk\");" ^
    "$lnk.TargetPath = 'pythonw.exe';" ^
    "$lnk.Arguments = '\"%APP_DIR%\driving_school_single.py\"';" ^
    "$lnk.WorkingDirectory = '%APP_DIR%';" ^
    "$lnk.IconLocation = '%APP_DIR%\medanic_icon.ico';" ^
    "$lnk.Description = 'برنامج ميدانيك - إدارة مدرسة تعليم السياقة';" ^
    "$lnk.Save();"

if errorlevel 1 (
    color 0C
    echo  ❌ فشل إنشاء الاختصار
    pause
    exit /b 1
)
echo      ✔ تم إنشاء اختصار "برنامج ميدانيك" على سطح المكتب
echo.

echo  ════════════════════════════════════════════════════
echo                    ✔  تم التثبيت بنجاح
echo  ════════════════════════════════════════════════════
echo.
echo   ابحث عن أيقونة "برنامج ميدانيك" على سطح المكتب
echo   وانقر عليها مرتين لفتح البرنامج
echo.
pause
