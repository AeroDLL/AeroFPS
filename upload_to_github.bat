@echo off
REM AeroFPS PRO - GitHub Upload Script
REM Bu script projeyi GitHub'a yükler

echo.
echo ============================================
echo   AeroFPS PRO - GitHub Upload
echo ============================================
echo.

REM Git yapılandırma kontrolü
echo [1] Git kontrolu...
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Git yuklu degil!
    echo.
    echo Git indirmek icin: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git yuklu: 
git --version
echo.

REM Kullanıcıdan repo URL al
echo [2] GitHub Repo URL'si girin:
echo    Ornek: https://github.com/AeroDLL/AeroFPS.git
echo.
set /p REPO_URL="URL: "

if "%REPO_URL%"=="" (
    echo [HATA] URL bos olamaz!
    pause
    exit /b 1
)

echo.
echo [3] Git repository baslatiliyor...
git init

echo.
echo [4] Dosyalar ekleniyor...
git add .

echo.
echo [5] Ilk commit yapiliyor...
git commit -m "🎉 Initial commit - AeroFPS PRO v1.0"

echo.
echo [6] Branch ismi ayarlanıyor...
git branch -M main

echo.
echo [7] Remote repository ekleniyor...
git remote add origin %REPO_URL%

echo.
echo [8] GitHub'a yukleniyor (Push)...
echo    NOT: GitHub kullanici adi ve Personal Access Token isteyecek!
echo.
git push -u origin main

echo.
echo ============================================
echo   TAMAMLANDI!
echo ============================================
echo.
echo Projeniz GitHub'a yuklendi!
echo URL: %REPO_URL%
echo.
pause
