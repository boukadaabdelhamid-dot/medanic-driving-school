@echo off
title Medanic - Patch Database Path Fix
color 0E
cls

echo.
echo  ====================================================
echo      Medanic - Patch Database Save Fix
echo      اصلاح مشكلة عدم حفظ البيانات
echo  ====================================================
echo.
echo  This script fixes the source code, then you rebuild
echo  سيقوم باصلاح الكود ثم تعيد البناء
echo.
pause

REM ── التحقق من وجود الملف ─────────────────────────────
if not exist "driving_school_single.py" (
    color 0C
    echo  ERROR: driving_school_single.py not found
    echo  ضع هذا الملف في نفس مجلد البرنامج
    pause
    exit /b 1
)

REM ── حفظ نسخة احتياطية ────────────────────────────────
echo  [1/3] Backing up original file...
copy /Y "driving_school_single.py" "driving_school_single.py.backup" >nul
echo       OK: driving_school_single.py.backup

REM ── تطبيق الإصلاح عبر PowerShell ─────────────────────
echo  [2/3] Applying database path fix...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$file = 'driving_school_single.py';" ^
    "$content = Get-Content $file -Raw -Encoding UTF8;" ^
    "$old = 'DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), \"driving_school.db\")';" ^
    "$new = \"if getattr(sys, 'frozen', False):`n    _BASE_DIR = os.path.dirname(sys.executable)`nelse:`n    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))`nDB_PATH = os.path.join(_BASE_DIR, 'driving_school.db')\";" ^
    "if ($content -match [regex]::Escape($old)) {" ^
    "    $content = $content.Replace($old, $new);" ^
    "    [System.IO.File]::WriteAllText((Resolve-Path $file), $content, [System.Text.UTF8Encoding]::new($false));" ^
    "    Write-Host '      OK: Fix applied successfully';" ^
    "} elseif ($content -match 'frozen.*sys.executable') {" ^
    "    Write-Host '      OK: Fix already applied (no changes needed)';" ^
    "} else {" ^
    "    Write-Host '      WARNING: Could not find exact line - manual fix needed';" ^
    "    exit 1;" ^
    "}"

if errorlevel 1 (
    color 0C
    echo.
    echo  ERROR: Patch failed
    echo  Please contact developer for manual fix
    pause
    exit /b 1
)

REM ── إخبار المستخدم ───────────────────────────────────
echo  [3/3] Done!
echo.

color 0A
echo  ====================================================
echo            ✓ PATCH APPLIED SUCCESSFULLY
echo            ✓ تم الاصلاح بنجاح
echo  ====================================================
echo.
echo   الخطوة التالية:
echo   NEXT STEP:
echo.
echo   1. Run BUILD_EXE.bat again to rebuild Medanic.exe
echo      شغّل BUILD_EXE.bat من جديد لبناء Medanic.exe
echo.
echo   2. Send the new Medanic.exe to your customer
echo      أرسل Medanic.exe الجديد للزبون
echo.
echo   3. Customer replaces the old exe with the new one
echo      الزبون يستبدل القديم بالجديد
echo.
pause
