param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("user", "admin")]
    [string]$Target
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $Root ".run"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$VenvActivate = Join-Path $Root ".venv\Scripts\activate.bat"
$Requirements = Join-Path $Root "requirements.txt"
$RequirementsStamp = Join-Path $Root ".venv\.requirements-installed"
$startedBackend = $null
$startedFrontend = $null

function Invoke-Checked {
    param([string]$FilePath, [string[]]$Arguments, [string]$WorkingDirectory = $Root)
    Push-Location $WorkingDirectory
    try {
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) { throw "$FilePath failed with exit code $LASTEXITCODE" }
    }
    finally { Pop-Location }
}

function Test-TcpPort {
    param([int]$Port)
    $client = [Net.Sockets.TcpClient]::new()
    try { $client.Connect("127.0.0.1", $Port); return $true }
    catch { return $false }
    finally { $client.Dispose() }
}

function Get-ServiceState {
    param([int]$Port, [string]$HealthUrl)
    try {
        $response = Invoke-WebRequest -UseBasicParsing $HealthUrl -TimeoutSec 2
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { return "ready" }
    }
    catch {}
    if (Test-TcpPort $Port) { return "occupied" }
    return "free"
}

function Wait-ForService {
    param([string]$HealthUrl, [int]$TimeoutSeconds = 30)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -UseBasicParsing $HealthUrl -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { return $true }
        }
        catch {}
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Save-Pid {
    param([string]$Name, [int]$ProcessId)
    New-Item -ItemType Directory -Force $RunDir | Out-Null
    Set-Content -LiteralPath (Join-Path $RunDir $Name) -Value $ProcessId -Encoding Ascii
}

function Stop-StartedProcess {
    param([System.Diagnostics.Process]$Process)
    if ($null -ne $Process -and -not $Process.HasExited) { & taskkill.exe /PID $Process.Id /T /F | Out-Null }
}

try {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Python was not found in PATH" }
    if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw "npm was not found in PATH" }

    if (-not (Test-Path $VenvActivate)) {
        Write-Host "[setup] creating Python virtualenv .venv\"
        Invoke-Checked "python" @("-m", "venv", ".venv")
        Write-Host "[setup] installing Python dependencies"
        Invoke-Checked $VenvPython @("-m", "pip", "install", "--upgrade", "pip")
        Invoke-Checked $VenvPython @("-m", "pip", "install", "-r", $Requirements)
        New-Item -ItemType File -Force $RequirementsStamp | Out-Null
    }
    else {
        $needsPythonDeps = -not (Test-Path $RequirementsStamp)
        if (-not $needsPythonDeps) { $needsPythonDeps = (Get-Item $Requirements).LastWriteTimeUtc -gt (Get-Item $RequirementsStamp).LastWriteTimeUtc }
        if ($needsPythonDeps) {
            Write-Host "[setup] installing updated Python dependencies"
            Invoke-Checked $VenvPython @("-m", "pip", "install", "-r", $Requirements)
            New-Item -ItemType File -Force $RequirementsStamp | Out-Null
        }
    }

    Write-Host "[setup] running migrate"
    Invoke-Checked $VenvPython @("manage.py", "migrate", "--noinput")

    if ($Target -eq "user") {
        $FrontendDir = Join-Path $Root "frontend"
        $FrontendPort = 5173
        $FrontendUrl = "http://127.0.0.1:5173/"
        $BrowserUrl = "http://localhost:5173/"
        $FrontendTitle = "liuying-frontend"
        $FrontendPidFile = "frontend.pid"
        $FrontendLabel = "user frontend"
    }
    else {
        $FrontendDir = Join-Path $Root "admin-frontend"
        $FrontendPort = 5174
        $FrontendUrl = "http://127.0.0.1:5174/manage/"
        $BrowserUrl = "http://localhost:5174/manage/"
        $FrontendTitle = "liuying-admin-frontend"
        $FrontendPidFile = "admin-frontend.pid"
        $FrontendLabel = "admin frontend"
    }

    $nodeStamp = Join-Path $FrontendDir "node_modules\.package-lock.json"
    $packageJson = Join-Path $FrontendDir "package.json"
    $packageLock = Join-Path $FrontendDir "package-lock.json"
    $needsNodeDeps = -not (Test-Path $nodeStamp)
    if (-not $needsNodeDeps) {
        $stampTime = (Get-Item $nodeStamp).LastWriteTimeUtc
        $needsNodeDeps = (Get-Item $packageJson).LastWriteTimeUtc -gt $stampTime -or ((Test-Path $packageLock) -and (Get-Item $packageLock).LastWriteTimeUtc -gt $stampTime)
    }
    if ($needsNodeDeps) {
        Write-Host "[setup] installing updated $FrontendLabel dependencies"
        Invoke-Checked "npm.cmd" @("install") $FrontendDir
    }

    $backendState = Get-ServiceState 8000 "http://127.0.0.1:8000/api/blogs/"
    if ($backendState -eq "occupied") { throw "port 8000 is occupied by a service that failed the backend health check" }
    $frontendState = Get-ServiceState $FrontendPort $FrontendUrl
    if ($frontendState -eq "occupied") { throw "port $FrontendPort is occupied by a service that failed the $FrontendLabel health check" }

    if ($backendState -eq "ready") { Write-Host "[reuse] Django backend is already running on port 8000" }
    else {
        Write-Host "[start] launching Django backend on port 8000"
        $command = "title liuying-backend && call .venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8000"
        $startedBackend = Start-Process -FilePath $env:ComSpec -ArgumentList "/k", $command -WorkingDirectory $Root -PassThru
        Save-Pid "backend.pid" $startedBackend.Id
    }

    if ($frontendState -eq "ready") { Write-Host "[reuse] $FrontendLabel is already running on port $FrontendPort" }
    else {
        Write-Host "[start] launching $FrontendLabel on port $FrontendPort"
        $command = "title $FrontendTitle && npm run dev -- --host 127.0.0.1 --strictPort"
        $startedFrontend = Start-Process -FilePath $env:ComSpec -ArgumentList "/k", $command -WorkingDirectory $FrontendDir -PassThru
        Save-Pid $FrontendPidFile $startedFrontend.Id
    }

    Write-Host "[startup] waiting for services"
    if (-not (Wait-ForService "http://127.0.0.1:8000/api/blogs/")) { throw "Django backend did not become ready within 30 seconds" }
    if (-not (Wait-ForService $FrontendUrl)) { throw "$FrontendLabel did not become ready within 30 seconds" }

    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  backend : http://127.0.0.1:8000"
    Write-Host "  $FrontendLabel : $BrowserUrl"
    Write-Host "  stop    : run stop.bat"
    Write-Host "============================================================"
    Write-Host ""
    if (-not $env:LIUYING_NO_BROWSER) { Start-Process $BrowserUrl }
    exit 0
}
catch {
    Write-Host ""
    Write-Host "[error] $($_.Exception.Message)" -ForegroundColor Red
    Stop-StartedProcess $startedFrontend
    Stop-StartedProcess $startedBackend
    exit 1
}