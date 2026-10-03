@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install.ps1" -Verify %*
set "MOD_EXIT=%ERRORLEVEL%"
echo.
pause
exit /b %MOD_EXIT%
