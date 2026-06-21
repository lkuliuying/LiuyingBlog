@echo off
REM =====================================================================
REM Liuying Blog - one-shot dev launcher (Windows)
REM
REM Convention: virtualenv lives at .venv\
REM First run : create .venv, install deps, run migrate
REM Later runs: just spawn Django 8000 and Vite 5173 in two new windows
REM Stop      : run stop.bat (PID files live under .run\)
REM
REM NOTE: keep this file ASCII-only. cmd.exe parses .bat under the system
REM       code page (GBK on zh-CN Windows); non-ASCII text breaks parsing.
REM =====================================================================
setlocal

set ROOT=%~dp0
pushd "%ROOT%"

where python >NUL 2>NUL || goto :nopython
where npm >NUL 2>NUL || goto :nonpm

REM -------- 1. backend virtualenv .venv\ -------------------------------
set "REQ_STAMP=.venv\.requirements-installed"
if not exist ".venv\Scripts\activate.bat" (
    echo [setup] creating Python virtualenv .venv\
    python -m venv .venv || goto :err
    call .venv\Scripts\activate.bat
    echo [setup] installing Python deps
    python -m pip install --upgrade pip || goto :err
    pip install -r requirements.txt || goto :err
    type NUL > "%REQ_STAMP%"
) else (
    call .venv\Scripts\activate.bat
    set "NEED_PY_DEPS="
    if not exist "%REQ_STAMP%" set "NEED_PY_DEPS=1"
    if exist "%REQ_STAMP%" (
        powershell -NoProfile -Command "if ((Get-Item 'requirements.txt').LastWriteTimeUtc -gt (Get-Item '%REQ_STAMP%').LastWriteTimeUtc) { exit 1 }"
        if errorlevel 1 set "NEED_PY_DEPS=1"
    )
    python -c "import django" 2>NUL
    if errorlevel 1 set "NEED_PY_DEPS=1"
    if defined NEED_PY_DEPS (
        echo [setup] installing updated Python deps
        python -m pip install --upgrade pip || goto :err
        pip install -r requirements.txt || goto :err
        type NUL > "%REQ_STAMP%"
    )
)

REM -------- 2. database migrate ----------------------------------------
echo [setup] running migrate
python manage.py migrate --noinput || goto :err

REM -------- 3. frontend node_modules -----------------------------------
set "NEED_NODE_DEPS="
if not exist "frontend\node_modules\.package-lock.json" set "NEED_NODE_DEPS=1"
if exist "frontend\node_modules\.package-lock.json" (
    powershell -NoProfile -Command "$stamp=(Get-Item 'frontend\node_modules\.package-lock.json').LastWriteTimeUtc; if ((Get-Item 'frontend\package.json').LastWriteTimeUtc -gt $stamp -or (Test-Path 'frontend\package-lock.json') -and (Get-Item 'frontend\package-lock.json').LastWriteTimeUtc -gt $stamp) { exit 1 }"
    if errorlevel 1 set "NEED_NODE_DEPS=1"
)
if defined NEED_NODE_DEPS (
    echo [setup] installing updated frontend deps - first run may take a while
    pushd frontend
    call npm install || (popd & goto :err)
    popd
)

REM -------- 4. launch both ---------------------------------------------
REM Refuse to silently move to another port or start duplicate services.
powershell -NoProfile -Command "$c=[Net.Sockets.TcpClient]::new(); try { $c.Connect('127.0.0.1',8000); $c.Dispose(); exit 1 } catch { exit 0 }"
if errorlevel 1 goto :port8000
powershell -NoProfile -Command "$c=[Net.Sockets.TcpClient]::new(); try { $c.Connect('127.0.0.1',5173); $c.Dispose(); exit 1 } catch { exit 0 }"
if errorlevel 1 goto :port5173

echo.
echo ============================================================
echo   backend : http://127.0.0.1:8000
echo   frontend: http://localhost:5173   (browser opens automatically)
echo   stop    : run stop.bat
echo ============================================================
echo.

if not exist ".run" mkdir ".run" || goto :err
del /Q ".run\backend.pid" ".run\frontend.pid" 2>NUL

powershell -NoProfile -Command "$p=Start-Process -FilePath $env:ComSpec -ArgumentList '/k','title liuying-backend && call .venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8000' -WorkingDirectory '%ROOT%' -PassThru; Set-Content -LiteralPath '%ROOT%.run\backend.pid' -Value $p.Id -Encoding Ascii"
if errorlevel 1 goto :launcherr
powershell -NoProfile -Command "$p=Start-Process -FilePath $env:ComSpec -ArgumentList '/k','title liuying-frontend && npm run dev -- --host 127.0.0.1 --strictPort' -WorkingDirectory '%ROOT%frontend' -PassThru; Set-Content -LiteralPath '%ROOT%.run\frontend.pid' -Value $p.Id -Encoding Ascii"
if errorlevel 1 goto :launcherr

echo [startup] waiting for backend and frontend
powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(30); do { try { $api=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/api/blogs/' -TimeoutSec 2; $web=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:5173/' -TimeoutSec 2; if ($api.StatusCode -eq 200 -and $web.StatusCode -eq 200) { exit 0 } } catch {}; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 goto :healtherr

echo [startup] services are ready, opening the frontend
if not defined LIUYING_NO_BROWSER start "" "http://localhost:5173/"

popd
endlocal
exit /b 0

:port8000
echo.
echo [error] port 8000 is already in use
echo         close the old backend window, then run start.bat again
popd
endlocal
exit /b 1

:port5173
echo.
echo [error] port 5173 is already in use
echo         close the old frontend window, then run start.bat again
popd
endlocal
exit /b 1

:healtherr
echo.
echo [error] services did not become ready within 30 seconds
echo         check the backend and frontend windows for the actual error
call stop.bat >NUL 2>NUL
popd
endlocal
exit /b 1

:launcherr
echo.
echo [error] could not launch both services
call stop.bat >NUL 2>NUL
popd
endlocal
exit /b 1

:nopython
echo [error] Python was not found in PATH
popd
endlocal
exit /b 1

:nonpm
echo [error] npm was not found in PATH
popd
endlocal
exit /b 1

:err
echo.
echo [error] startup failed, check the messages above
popd
endlocal
exit /b 1
