@echo off
chcp 65001 >nul
title بناء برنامج ميدانيك إلى ملف EXE
color 0B

echo.
echo ========================================================
echo   بناء برنامج ميدانيك إلى ملف تنفيذي مستقل (.exe)
echo ========================================================
echo.

REM ── 1. التحقق من وجود Python ─────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [خطأ] Python غير مثبّت على هذا الجهاز.
    echo حمّله من: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM ── 2. تثبيت PyInstaller والمكتبات المطلوبة ──────────────
echo [1/4] تثبيت المكتبات المطلوبة...
pip install --quiet --upgrade pyinstaller pillow reportlab arabic-reshaper python-bidi
if errorlevel 1 (
    echo [خطأ] فشل تثبيت المكتبات
    pause
    exit /b 1
)

REM ── 3. التحقق من وجود الملفات ────────────────────────────
echo [2/4] التحقق من الملفات...
if not exist "driving_school_single.py" (
    echo [خطأ] ملف driving_school_single.py غير موجود
    pause
    exit /b 1
)
if not exist "license_guard.py" (
    echo [خطأ] ملف license_guard.py غير موجود
    pause
    exit /b 1
)
if not exist "medanic_icon.ico" (
    echo [خطأ] ملف medanic_icon.ico غير موجود
    pause
    exit /b 1
)

REM ── 4. تنظيف البناء السابق ────────────────────────────────
echo [3/4] تنظيف الملفات القديمة...
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"
if exist "Medanic.spec" del /q "Medanic.spec"

REM ── 5. بناء ملف EXE ──────────────────────────────────────
echo [4/4] بناء ملف EXE (قد يستغرق دقيقتين)...
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "Medanic" ^
    --icon "medanic_icon.ico" ^
    --add-data "license_guard.py;." ^
    --add-data "medanic_icon.ico;." ^
    --hidden-import "license_guard" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "arabic_reshaper" ^
    --hidden-import "bidi.algorithm" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_winansi" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_macroman" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_standard" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_symbol" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_zapfdingbats" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_pdfdoc" ^
    --hidden-import "reportlab.pdfbase._fontdata_enc_macexpert" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_helvetica" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_courier" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_timesroman" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_helveticaoblique" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_helveticabold" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_helveticaboldoblique" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_courieroblique" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_courierbold" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_courierboldoblique" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_timesitalic" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_timesbold" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_timesbolditalic" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_symbol" ^
    --hidden-import "reportlab.pdfbase._fontdata_widths_zapfdingbats" ^
    "driving_school_single.py"

if errorlevel 1 (
    echo.
    echo [خطأ] فشل البناء
    pause
    exit /b 1
)

echo.
echo ========================================================
echo                  ✔  تم البناء بنجاح
echo ========================================================
echo.
echo الملف الناتج:  dist\Medanic.exe
echo.
echo لإنشاء اختصار على سطح المكتب، شغّل:
echo    create_desktop_shortcut.bat
echo.
pause
