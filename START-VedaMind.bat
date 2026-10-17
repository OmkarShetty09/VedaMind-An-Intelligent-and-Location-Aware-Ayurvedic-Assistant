@echo off
REM Double-click to start VedaMind (first time: runs setup automatically).
cd /d "%~dp0"
if not exist "backend\.venv" (
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\setup.ps1 || goto :failed
  echo.
  echo Put your GEMINI_API_KEY in .env - Notepad opens now. Save it, then close Notepad.
  notepad .env
)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\start.ps1 || goto :failed
start "" http://localhost:5173
echo.
echo VedaMind is running. Keep the three VedaMind windows open. Close this window any time.
pause
exit /b 0
:failed
echo.
echo Something went wrong - read the message above.
pause
exit /b 1
