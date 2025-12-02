<#
Setup script for Windows (PowerShell) to ensure Python is installed,
create a virtual environment `.venv`, and install Python dependencies.

Usage (run in repository root):
  1. Open PowerShell as Administrator if you want the script to install Python.
  2. Run: `.\ackup.ps1` or `powershell -ExecutionPolicy Bypass -File .\setup_env.ps1`

The script will:
  - Check for `python` or `py` command
  - Try to install Python using `winget` if missing
  - Create `.venv` virtualenv
  - Install packages from `requirements.txt` using the venv pip
#>

function Test-CommandExists {
    param([string]$cmd)
    return (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null
}

Write-Host "Checking for Python..."

$pythonCmd = $null
if (Test-CommandExists python) {
    $pythonCmd = "python"
} elseif (Test-CommandExists py) {
    $pythonCmd = "py -3"
}

if (-not $pythonCmd) {
    Write-Host "Python executable not found on PATH." -ForegroundColor Yellow
    if (Test-CommandExists winget) {
        Write-Host "Attempting to install Python via winget..." -ForegroundColor Cyan
        try {
            winget install --id Python.Python.3 -e --accept-package-agreements --accept-source-agreements
        } catch {
            Write-Host "winget install failed: $_" -ForegroundColor Red
            Write-Host "Please install Python manually from https://www.python.org/downloads/ and re-run this script." -ForegroundColor Yellow
            exit 1
        }

        # After install, try to pick up python
        if (Test-CommandExists python) { $pythonCmd = "python" }
        elseif (Test-CommandExists py) { $pythonCmd = "py -3" }
    } else {
        Write-Host "No 'winget' available to automate install." -ForegroundColor Yellow
        Write-Host "Please install Python (3.8+) and re-run. Download: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Using Python command: $pythonCmd"

# Create virtual environment
$venvPath = Join-Path $PWD '.venv'
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..."
    & $pythonCmd -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtualenv. See output above." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ".venv already exists, skipping creation." -ForegroundColor Green
}

# Use the venv pip to install requirements
$pipExe = Join-Path $venvPath 'Scripts\pip.exe'
if (-not (Test-Path $pipExe)) {
    Write-Host "pip not found inside venv, attempting to bootstrap..." -ForegroundColor Yellow
    & $pythonCmd -m ensurepip --upgrade
}

if (-not (Test-Path $pipExe)) {
    # Try using python -m pip inside venv
    $pipCmd = "& '$venvPath\Scripts\python.exe' -m pip"
} else {
    $pipCmd = "& '$pipExe'"
}

Write-Host "Upgrading pip and installing requirements..."
try {
    iex "$pipCmd install --upgrade pip"
    iex "$pipCmd install -r requirements.txt"
} catch {
    Write-Host "Failed to install requirements: $_" -ForegroundColor Red
    Write-Host "You can try running the following commands manually:" -ForegroundColor Yellow
    Write-Host "  .\ .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    exit 1
}

Write-Host "Setup complete." -ForegroundColor Green
Write-Host "To activate the virtualenv in this PowerShell session run:" -ForegroundColor Cyan
Write-Host "  .\ .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "Then run tests with: python run_tests.py" -ForegroundColor Cyan
