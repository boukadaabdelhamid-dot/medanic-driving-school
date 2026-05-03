@echo off
chcp 65001 >nul
title إنشاء اختصار سطح المكتب — ميدانيك
color 0A

echo.
echo ========================================================
echo   إنشاء اختصار البرنامج على سطح المكتب
echo ========================================================
echo.

REM التحقق من وجود ملف EXE
if not exist "dist\Medanic.exe" (
    echo [خطأ] ملف dist\Medanic.exe غير موجود
    echo شغّل أولاً:  build_exe.bat
    pause
    exit /b 1
)

REM إنشاء اختصار باستخدام PowerShell
powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell;" ^
    "$desk = [Environment]::GetFolderPath('Desktop');" ^
    "$lnk = $ws.CreateShortcut(\"$desk\برنامج ميدانيك.lnk\");" ^
    "$lnk.TargetPath = (Resolve-Path '.\dist\Medanic.exe').Path;" ^
    "$lnk.WorkingDirectory = (Resolve-Path '.\dist').Path;" ^
    "$lnk.IconLocation = (Resolve-Path '.\medanic_icon.ico').Path;" ^
    "$lnk.Description = 'برنامج ميدانيك — إدارة مدرسة تعليم السياقة';" ^
    "$lnk.Save();"

if errorlevel 1 (
    echo [خطأ] فشل إنشاء الاختصار
    pause
    exit /b 1
)

echo.
echo ✔  تم إنشاء الاختصار "برنامج ميدانيك" على سطح المكتب
echo.
pause
