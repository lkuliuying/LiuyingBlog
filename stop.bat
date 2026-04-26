@echo off
chcp 65001 >nul 2>&1
title Liuying Blog - One-Click Stop

echo ============================================
echo         Liuying Blog - One-Click Stop Script
echo ============================================
echo.

:: ---- Stop Django Development Server ----
echo [1/3] Stopping Django server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
taskkill /f /im python.exe /fi "WINDOWTITLE eq Liuying Blog*" >nul 2>&1
echo       Django server stopped.
echo.

:: ---- Stop Celery Worker ----
echo [2/3] Stopping Celery Worker...
taskkill /f /fi "WINDOWTITLE eq Celery Worker*" >nul 2>&1
taskkill /f /im celery.exe >nul 2>&1
echo       Celery Worker stopped.
echo.

:: ---- Stop Docker Redis Container ----
echo [3/3] Stopping Docker Redis container...
docker stop redis >nul 2>&1
if errorlevel 1 (
    echo       Redis container not running or does not exist, skipping.
) else (
    echo       Redis container stopped.
)
echo.

echo ============================================
echo   All services stopped!
echo ============================================
echo.
timeout /t 3 /nobreak >nul