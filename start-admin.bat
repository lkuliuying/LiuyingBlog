@echo off
REM Start or reuse Django backend, then start or reuse the admin frontend.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-stack.ps1" admin
exit /b %ERRORLEVEL%