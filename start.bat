@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Liuying Blog - One-Click Start

echo ============================================
echo         Liuying Blog - One-Click Start Script
echo ============================================
echo.

:: ---- Configuration ----
set "PROJECT_DIR=%~dp0"
set "CONDA_ENV=liuyingblog"
set "CONDA_ROOT=C:\ProgramSoftware\Miniconda"
set "DJANGO_HOST=127.0.0.1"
set "DJANGO_PORT=8000"

:: Docker Redis container name
set "REDIS_CONTAINER=redis"

:: ---- Activate Conda Environment ----
echo [1/4] Activating Conda environment: %CONDA_ENV%
call "%CONDA_ROOT%\condabin\conda.bat" activate %CONDA_ENV%
if errorlevel 1 (
    echo [Error] Cannot activate Conda environment %CONDA_ENV%, please check if it exists.
    pause
    exit /b 1
)
echo       Conda environment activated.
echo.

:: ---- Switch to project directory ----
cd /d "%PROJECT_DIR%"

:: ---- Start Docker Redis ----
echo [2/4] Checking Docker Redis container...
docker inspect -f "{{.State.Running}}" %REDIS_CONTAINER% >nul 2>&1
if errorlevel 1 (
    echo       Container %REDIS_CONTAINER% not found, creating and starting...
    docker run -d --name %REDIS_CONTAINER% -p 6379:6379 redis
) else (
    for /f %%s in ('docker inspect -f "{{.State.Running}}" %REDIS_CONTAINER%') do set "REDIS_RUNNING=%%s"
    if "!REDIS_RUNNING!"=="true" (
        echo       Redis container is already running.
    ) else (
        echo       Starting Redis container...
        docker start %REDIS_CONTAINER%
    )
)
timeout /t 2 /nobreak >nul
echo       Redis ready.
echo.

:: ---- Start Celery Worker ----
echo [3/4] Starting Celery Worker...
start "Celery Worker" /min cmd /k "cd /d "%PROJECT_DIR%" && call "%CONDA_ROOT%\condabin\conda.bat" activate %CONDA_ENV% && celery -A liuyingblog worker --loglevel=info --pool=solo"
timeout /t 3 /nobreak >nul
echo       Celery Worker started (running in minimized window).
echo.

:: ---- Start Django Development Server ----
echo [4/4] Starting Django development server...
echo       Address: http://%DJANGO_HOST%:%DJANGO_PORT%/
echo.
echo ============================================
echo   All services started!
echo   Django:  http://%DJANGO_HOST%:%DJANGO_PORT%/
echo   Admin:   http://%DJANGO_HOST%:%DJANGO_PORT%/admin/
echo   Press Ctrl+C to stop Django server
echo   To stop all services, run stop.bat
echo ============================================
echo.

python manage.py runserver %DJANGO_HOST%:%DJANGO_PORT%