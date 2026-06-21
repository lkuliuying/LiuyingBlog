@echo off
REM =====================================================================
REM Liuying Blog - stop Django and Vite processes started by start.bat
REM
REM NOTE: keep this file ASCII-only for compatibility with cmd.exe.
REM =====================================================================
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%"

echo [stop] looking for Liuying backend and frontend processes...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='SilentlyContinue'; $targets=[System.Collections.Generic.HashSet[int]]::new(); $failed=$false; function IsLiuyingProcess($p) { $line=[string]$p.CommandLine; return $line -match 'liuying-(backend|frontend|admin-frontend)' -or $line -match 'manage\.py\s+runserver' -or $line -match 'npm(\.cmd)?\s+run\s+dev' -or $line -match '[\\/]vite([\\/]|\.js|\s)' }; foreach ($file in @('.run\backend.pid','.run\frontend.pid','.run\admin-frontend.pid')) { if (Test-Path -LiteralPath $file) { $processId=0; if ([int]::TryParse((Get-Content -LiteralPath $file -First 1).Trim(),[ref]$processId) -and (Get-Process -Id $processId)) { [void]$targets.Add($processId) } } }; foreach ($port in 8000,5173,5174) { foreach ($ownerId in @(Get-NetTCPConnection -State Listen -LocalPort $port | Select-Object -ExpandProperty OwningProcess -Unique)) { $p=Get-CimInstance Win32_Process -Filter ('ProcessId='+$ownerId); if ($p -and (IsLiuyingProcess $p)) { [void]$targets.Add([int]$ownerId) } } }; if ($targets.Count -eq 0) { Write-Host '[stop] no running Liuying services found' } else { foreach ($processId in $targets) { Write-Host ('[stop] stopping process tree '+$processId); & taskkill.exe /PID $processId /T /F | Out-Host; if ($LASTEXITCODE -ne 0 -and (Get-Process -Id $processId)) { $failed=$true } } }; if ($failed) { Write-Host '[error] some processes could not be stopped; try running stop.bat as Administrator'; exit 1 }; Remove-Item -LiteralPath '.run\backend.pid','.run\frontend.pid','.run\admin-frontend.pid' -Force; exit 0"
set "RESULT=%ERRORLEVEL%"

popd
endlocal & exit /b %RESULT%
