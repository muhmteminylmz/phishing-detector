@echo off
REM =============================================================================
REM  Phishing Detector - Windows ile Baslatma
REM  Kullanim: start.bat  (cift tikla veya CMD'de calistir)
REM
REM  WSL veya bash gerektirmez. Dogrudan Windows'ta calisir.
REM =============================================================================

echo.
echo   ========================================================
echo     Phishing Detector - Baslatiliyor...
echo   ========================================================
echo.

REM PowerShell ile start.ps1 calistir
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

if %ERRORLEVEL% neq 0 (
    echo.
    echo   [HATA] Baslatma sirasinda sorun olustu.
    echo   Lutfen Docker Desktop'in calistiginden emin ol.
    echo.
)

pause
