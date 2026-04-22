param(
    [switch]$InstallDeps,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# El script vive en scripts/, asi que subimos un nivel para trabajar siempre
# desde la raiz del proyecto aunque la usuaria lo lance desde otra carpeta.
$projectRoot = Split-Path -Path $PSScriptRoot -Parent
$frontendRoot = Join-Path $projectRoot "frontend"
$venvRoot = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvRoot "Scripts\python.exe"
$frontendNodeModules = Join-Path $frontendRoot "node_modules"
$venvWasCreated = $false

function Test-CommandAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )

    return [bool](Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "== $Label ==" -ForegroundColor Cyan
    & $Action
}

function Start-WindowProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    # Montamos el comando completo dentro de una nueva ventana de PowerShell
    # para que backend y frontend dejen sus logs visibles durante la demo.
    $escapedWorkingDirectory = $WorkingDirectory.Replace("'", "''")
    $windowCommand = "Set-Location '$escapedWorkingDirectory'; `$Host.UI.RawUI.WindowTitle = '$Title'; $Command"

    if ($DryRun) {
        Write-Host "[DryRun] Ventana: $Title" -ForegroundColor Yellow
        Write-Host "[DryRun] Workdir: $WorkingDirectory" -ForegroundColor Yellow
        Write-Host "[DryRun] Command: $Command" -ForegroundColor Yellow
        return
    }

    Start-Process powershell `
        -WorkingDirectory $WorkingDirectory `
        -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $windowCommand
        ) | Out-Null
}

if (-not (Test-CommandAvailable "python")) {
    throw "No se encontro 'python' en PATH. Instala Python o abre una terminal donde ya este disponible."
}

if (-not (Test-CommandAvailable "npm")) {
    throw "No se encontro 'npm' en PATH. Instala Node.js o abre una terminal donde ya este disponible."
}

Invoke-Step -Label "Preparando entorno Python" -Action {
    if (-not (Test-Path $venvPython)) {
        if ($DryRun) {
            Write-Host "[DryRun] Se crearia el entorno virtual en $venvRoot" -ForegroundColor Yellow
        }
        else {
            python -m venv $venvRoot
            $venvWasCreated = $true
        }
    }
    else {
        Write-Host "Entorno virtual detectado en $venvRoot"
    }
}

Invoke-Step -Label "Instalando dependencias si hace falta" -Action {
    $mustInstallPythonDeps = $InstallDeps -or $venvWasCreated -or -not (Test-Path $venvPython)
    $mustInstallFrontendDeps = $InstallDeps -or -not (Test-Path $frontendNodeModules)

    if ($mustInstallPythonDeps) {
        if ($DryRun) {
            Write-Host "[DryRun] $venvPython -m pip install -r requirements.txt" -ForegroundColor Yellow
        }
        else {
            & $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")
        }
    }
    else {
        Write-Host "Dependencias Python ya presentes."
    }

    if ($mustInstallFrontendDeps) {
        if ($DryRun) {
            Write-Host "[DryRun] npm install (en $frontendRoot)" -ForegroundColor Yellow
        }
        else {
            Push-Location $frontendRoot
            try {
                npm install
            }
            finally {
                Pop-Location
            }
        }
    }
    else {
        Write-Host "Dependencias frontend ya presentes."
    }
}

$backendCommand = "& '$venvPython' -m uvicorn backend.main:app --reload"
$frontendCommand = "npm run dev"

Invoke-Step -Label "Arrancando backend y frontend" -Action {
    Start-WindowProcess `
        -Title "NeuroBotics Backend" `
        -WorkingDirectory $projectRoot `
        -Command $backendCommand

    Start-WindowProcess `
        -Title "NeuroBotics Frontend" `
        -WorkingDirectory $frontendRoot `
        -Command $frontendCommand
}

Write-Host ""
Write-Host "Demo local preparada." -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:4321" -ForegroundColor Green
Write-Host ""
Write-Host "Uso recomendado:" -ForegroundColor Cyan
Write-Host "powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1"
Write-Host ""
Write-Host "Opciones utiles:" -ForegroundColor Cyan
Write-Host "-InstallDeps  Fuerza pip install y npm install antes de arrancar."
Write-Host "-DryRun       Muestra los pasos sin abrir ventanas ni lanzar procesos."
