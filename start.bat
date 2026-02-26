@echo off
chcp 65001 >nul 2>&1
REM =============================================================================
REM  Phishing Detector - Windows ile Başlatma
REM  Kullanım: start.bat  (çift tıkla veya CMD'de çalıştır)
REM
REM  WSL veya bash gerektirmez. Doğrudan Windows'ta çalışır.
REM =============================================================================

echo.
echo   ========================================================
echo     Phishing Detector - Başlatılıyor...
echo   ========================================================
echo.

REM PowerShell ile start.ps1 çalıştır
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

if %ERRORLEVEL% neq 0 (
    echo.
    echo   [HATA] Başlatma sırasında sorun oluştu.
    echo   Lütfen Docker Desktop'ın çalıştığından emin ol.
    echo.
)

pause
