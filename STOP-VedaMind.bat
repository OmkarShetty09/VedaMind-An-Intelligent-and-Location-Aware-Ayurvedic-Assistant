@echo off
REM Double-click to stop VedaMind (servers, database and Redis).
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\stop.ps1
echo.
echo VedaMind stopped.
pause
