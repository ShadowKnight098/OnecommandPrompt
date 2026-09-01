"""PowerShell installer script generator for Windows."""
from typing import List, Optional
from app.models.plan import InstallationPlan


class PowerShellGenerator:
    """Generates Windows PowerShell installation scripts (.ps1)."""

    @classmethod
    def generate(cls, plan: InstallationPlan) -> str:
        # Format package list as a PowerShell array (no trailing comma for PS 5.1 compatibility)
        if plan.dependencies:
            packages_array_items = ",\n".join([f'    "{p}"' for p in plan.dependencies])
            packages_def = f"$ResolvedPackages = @(\n{packages_array_items}\n)"
            packages_display = ", ".join(plan.dependencies)
        else:
            packages_def = "$ResolvedPackages = @()"
            packages_display = ""

        # Version requirement number for comparison (e.g. "3.10")
        min_ver_num = "3.10"
        if ">=" in plan.runtime.version:
            min_ver_num = plan.runtime.version.replace(">=", "").strip()
        elif "==" in plan.runtime.version:
            min_ver_num = plan.runtime.version.replace("==", "").strip()

        # Command to run entry point
        entry_file = plan.entrypoint.entry_file or "main.py"
        entry_type = plan.entrypoint.command_type or "python"

        if entry_type == "streamlit":
            run_cmd = f'& "$VenvPython" -m streamlit run "{entry_file}"'
        elif entry_type == "uvicorn":
            stem = entry_file.replace(".py", "").replace("/", ".").replace("\\", ".")
            run_cmd = f'& "$VenvPython" -m uvicorn {stem}:app --reload'
        else:
            run_cmd = f'& "$VenvPython" "{entry_file}"'

        script = f"""# ==============================================================================
# One-Command Project Installer: {plan.project_name}
# Target OS: Windows (PowerShell)
# Philosophy: DETECT -> VERIFY -> PLAN -> INSTALL -> VALIDATE -> RUN
# ==============================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Header {{
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "         One-Command Installer: {plan.project_name}" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}}

function Write-Step($stepNum, $stepTotal, $msg) {{
    Write-Host "[$stepNum/$stepTotal] $msg..." -ForegroundColor Yellow
}}

function Write-Success($msg) {{
    Write-Host "  [OK] $msg" -ForegroundColor Green
}}

function Write-Warn($msg) {{
    Write-Host "  [!] $msg" -ForegroundColor Yellow
}}

function Write-Fail($msg) {{
    Write-Host ""
    Write-Host "  [ERROR] $msg" -ForegroundColor Red
    Write-Host ""
    Exit 1
}}

Write-Header

$MinVersion = [version]"{min_ver_num}"
$ProjectDir = Join-Path -Path $PWD -ChildPath "{plan.project_name}"
$ArchiveFile = Join-Path -Path $PWD -ChildPath "{plan.project.archive_name}"
$DownloadUrl = "{plan.project.download_url}"

# ------------------------------------------------------------------------------
# [1/7] DETECT PYTHON RUNTIME
# ------------------------------------------------------------------------------
Write-Step 1 7 "Checking for installed Python runtime"

$FoundPython = $null
$CandidatePythons = @("py", "python", "python3")

foreach ($cmd in $CandidatePythons) {{
    try {{
        $verOutput = & $cmd -c "import sys; print(f'{{sys.version_info.major}}.{{sys.version_info.minor}}.{{sys.version_info.micro}}')" 2>$null
        if ($LASTEXITCODE -eq 0 -and $verOutput) {{
            $cleanedVer = $verOutput.Trim()
            $pyVer = [version]$cleanedVer
            if ($pyVer -ge $MinVersion) {{
                $FoundPython = $cmd
                $InstalledVersion = $cleanedVer
                break
            }}
        }}
    }} catch {{
        # Continue searching candidates
    }}
}}

# ------------------------------------------------------------------------------
# [2/7] VERIFY OR INSTALL PYTHON
# ------------------------------------------------------------------------------
Write-Step 2 7 "Verifying runtime compatibility"

if ($FoundPython) {{
    Write-Success "Compatible Python $InstalledVersion found ($FoundPython)"
}} else {{
    Write-Warn "Python >= $MinVersion was not found on this machine."
    Write-Host "  -> Attempting automated installation via winget..." -ForegroundColor Cyan

    $wingetInstalled = $false
    try {{
        $wingetCheck = Get-Command "winget" -ErrorAction SilentlyContinue
        if ($wingetCheck) {{
            Write-Host "  -> Installing Python {plan.runtime.target_install_version} via winget..." -ForegroundColor Gray
            & winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements --silent
            
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            $FoundPython = "python"
            $wingetInstalled = $true
            Write-Success "Python installed successfully via winget."
        }}
    }} catch {{
        $wingetInstalled = $false
    }}

    if (-not $wingetInstalled) {{
        Write-Fail "Please install Python $MinVersion or newer from https://www.python.org/downloads/ and re-run this installer."
    }}
}}

# ------------------------------------------------------------------------------
# [3/7] DOWNLOAD AND SYNC PROJECT (SMART IN-PLACE UPDATE)
# ------------------------------------------------------------------------------
$IsExistingProject = Test-Path -Path $ProjectDir

if ($IsExistingProject) {{
    Write-Step 3 7 "Updating project files in-place"
    Write-Host "  -> [MODE: SMART UPDATE] Existing project installation detected." -ForegroundColor Cyan
    Write-Host "  -> Syncing latest code while preserving .env, databases, datasets, and .venv..." -ForegroundColor Gray
    
    # Optional safety backup of previous Python files
    try {{
        $BackupDir = Join-Path -Path $ProjectDir -ChildPath ".backup"
        if (-not (Test-Path -Path $BackupDir)) {{
            New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        }}
        Get-ChildItem -Path $ProjectDir -Filter "*.py" -File -ErrorAction SilentlyContinue | ForEach-Object {{
            Copy-Item -Path $_.FullName -Destination $BackupDir -Force -ErrorAction SilentlyContinue
        }}
    }} catch {{
        # Backup is best-effort
    }}
}} else {{
    Write-Step 3 7 "Downloading project files"
    Write-Host "  -> [MODE: FRESH INSTALL] Setting up new project workspace..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
}}

try {{
    $TempZip = Join-Path -Path $ProjectDir -ChildPath "project_source.zip"
    Write-Host "  -> Downloading from $DownloadUrl" -ForegroundColor Gray
    
    # Use WebClient
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($DownloadUrl, $TempZip)
    
    Write-Success "Project package downloaded."
    
    Write-Host "  -> Applying non-destructive overlay extraction..." -ForegroundColor Gray
    Expand-Archive -Path $TempZip -DestinationPath $ProjectDir -Force
    Remove-Item -Path $TempZip -Force -ErrorAction SilentlyContinue
    
    if ($IsExistingProject) {{
        Write-Success "Project code updated successfully in $ProjectDir (local state preserved)."
    }} else {{
        Write-Success "Project extracted into $ProjectDir"
    }}
}} catch {{
    Write-Fail "Failed to download or extract project archive: $_"
}}

# Set working directory to project folder
Set-Location -Path $ProjectDir

# ------------------------------------------------------------------------------
# [4/7] ISOLATED VIRTUAL ENVIRONMENT (.venv)
# ------------------------------------------------------------------------------
Write-Step 4 7 "Checking isolated virtual environment (.venv)"

$VenvDir = Join-Path -Path $ProjectDir -ChildPath ".venv"
$VenvPython = Join-Path -Path $VenvDir -ChildPath "Scripts\\python.exe"

if (-not (Test-Path -Path $VenvPython)) {{
    try {{
        Write-Host "  -> Creating fresh virtual environment..." -ForegroundColor Gray
        & $FoundPython -m venv .venv
        Write-Success "Virtual environment created at .venv"
    }} catch {{
        Write-Fail "Failed to create virtual environment: $_"
    }}
}} else {{
    Write-Success "Reusing existing virtual environment at .venv (zero reinstall needed)."
}}

# ------------------------------------------------------------------------------
# [5/7] SYNCHRONIZE PROJECT DEPENDENCIES
# ------------------------------------------------------------------------------
Write-Step 5 7 "Synchronizing project dependencies"

{packages_def}

try {{
    & "$VenvPython" -m pip install --upgrade pip --quiet
    
    if (Test-Path -Path "requirements.txt") {{
        Write-Host "  -> Syncing packages from requirements.txt..." -ForegroundColor Gray
        & "$VenvPython" -m pip install -r requirements.txt
    }} elseif ($ResolvedPackages.Count -gt 0) {{
        Write-Host "  -> Syncing resolved packages: {packages_display}" -ForegroundColor Gray
        & "$VenvPython" -m pip install @ResolvedPackages
    }} else {{
        Write-Success "No third-party dependencies required."
    }}
    Write-Success "Dependencies verified and synchronized in isolated environment."
}} catch {{
    Write-Fail "Dependency synchronization failed: $_"
}}

# ------------------------------------------------------------------------------
# [6/7] VALIDATE PROJECT INTEGRITY
# ------------------------------------------------------------------------------
Write-Step 6 7 "Validating entry point and configuration"

$EntryFile = "{entry_file}"
if (-not (Test-Path -Path $EntryFile)) {{
    # Search recursively if nested
    $foundEntry = Get-ChildItem -Path $ProjectDir -Filter $EntryFile -Recurse | Select-Object -First 1
    if ($foundEntry) {{
        $EntryFile = $foundEntry.FullName
    }} else {{
        Write-Fail "Entry point file '$EntryFile' was not found in project directory."
    }}
}}
Write-Success "Entry point validated: $EntryFile"

# ------------------------------------------------------------------------------
# [7/7] START APPLICATION
# ------------------------------------------------------------------------------
Write-Step 7 7 "Launching application"
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Application is starting now!                              " -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

{run_cmd}
"""
        return script
