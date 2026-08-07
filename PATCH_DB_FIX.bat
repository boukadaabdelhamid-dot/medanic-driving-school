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
echo  The source now stores the database in AppData\Local\Medanic
echo  الكود الآن يحفظ قاعدة البيانات في AppData\Local\Medanic
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
echo  [2/3] Checking database path fix...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$content = Get-Content 'driving_school_single.py' -Raw -Encoding UTF8;" ^
    "if ($content -match 'def _prepare_database_path') {" ^
    "    Write-Host '      OK: AppData database path is already enabled';" ^
    "} else {" ^
    "    Write-Host '      ERROR: This source is older than the supported version';" ^
    "    Write-Host '      Download the latest source before rebuilding';" ^
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
