@echo off
REM Start or reuse Django backend, then start or reuse the user frontend.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-stack.ps1" user
exit /b %ERRORLEVEL%