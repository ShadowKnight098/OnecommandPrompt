"""PowerShell installer script generator for Windows (supporting Python, React, Vite, Node, HTML, and Fullstack)."""
from typing import List, Optional
from app.models.plan import InstallationPlan


class PowerShellGenerator:
    """Generates Windows PowerShell installation scripts (.ps1)."""

    @classmethod
    def generate(cls, plan: InstallationPlan) -> str:
        rtype = plan.runtime.type.lower()
        if rtype in ["node", "react", "vite", "nextjs", "vue", "svelte", "nodejs"]:
            return cls._generate_node_script(plan)
        elif rtype in ["static_web", "html", "html_static"]:
            return cls._generate_static_web_script(plan)
        elif rtype in ["fullstack"]:
            return cls._generate_fullstack_script(plan)
        else:
            return cls._generate_python_script(plan)

    @classmethod
    def _generate_static_web_script(cls, plan: InstallationPlan) -> str:
        """Generates installer for static HTML/CSS/JS projects."""
        port = plan.entrypoint.target_port or 8080
        entry_file = plan.entrypoint.entry_file or "index.html"

        return f"""# ==============================================================================
# One-Command Project Installer: {plan.project_name} (Static Web / HTML5)
# Target OS: Windows (PowerShell)
# ==============================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Header {{
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "         One-Command Installer: {plan.project_name} (Web)" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}}

function Write-Step($stepNum, $stepTotal, $msg) {{
    Write-Host "[$stepNum/$stepTotal] $msg..." -ForegroundColor Yellow
}}

function Write-Success($msg) {{
    Write-Host "  [OK] $msg" -ForegroundColor Green
}}

function Write-Fail($msg) {{
    Write-Host ""
    Write-Host "  [ERROR] $msg" -ForegroundColor Red
    Write-Host ""
    Exit 1
}}

Write-Header

$ProjectDir = Join-Path -Path $PWD -ChildPath "{plan.project_name}"
$ArchiveFile = Join-Path -Path $PWD -ChildPath "{plan.project.archive_name}"
$DownloadUrl = "{plan.project.download_url}"
$Port = {port}

# 1. DOWNLOAD ARCHIVE
Write-Step 1 4 "Downloading project archive"
try {{
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ArchiveFile -UseBasicParsing
    Write-Success "Archive downloaded to $ArchiveFile"
}} catch {{
    Write-Fail "Failed to download project archive: $_"
}}

# 2. EXTRACT PROJECT
Write-Step 2 4 "Extracting files to $ProjectDir"
try {{
    if (Test-Path $ProjectDir) {{
        Remove-Item -Path $ProjectDir -Recurse -Force
    }}
    Expand-Archive -Path $ArchiveFile -DestinationPath $ProjectDir -Force
    Remove-Item -Path $ArchiveFile -Force
    Write-Success "Extracted successfully"
}} catch {{
    Write-Fail "Extraction failed: $_"
}}

# 3. VERIFY ENTRY FILE
Write-Step 3 4 "Verifying web assets"
$TargetHtml = Join-Path $ProjectDir "{entry_file}"
if (-not (Test-Path $TargetHtml)) {{
    # Fallback search for any html file
    $foundHtml = Get-ChildItem -Path $ProjectDir -Filter "*.html" -Recurse | Select-Object -First 1
    if ($foundHtml) {{
        $TargetHtml = $foundHtml.FullName
    }}
}}
Write-Success "Entry point found: $TargetHtml"

# 4. LAUNCH LOCAL WEB SERVER & BROWSER
Write-Step 4 4 "Starting local web server on port $Port"
Set-Location -Path $ProjectDir

# Open default browser
$TargetUrl = "http://localhost:$Port"
Start-Process $TargetUrl

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  [READY] Serving {plan.project_name} at $TargetUrl" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Use Python http.server or npx serve
$hasPy = Get-Command "python" -ErrorAction SilentlyContinue
if ($hasPy) {{
    & python -m http.server $Port
}} else {{
    $hasNpx = Get-Command "npx" -ErrorAction SilentlyContinue
    if ($hasNpx) {{
        & npx serve . -l $Port
    }} else {{
        # Direct file launch fallback
        Start-Process $TargetHtml
    }}
}}
"""

    @classmethod
    def _generate_node_script(cls, plan: InstallationPlan) -> str:
        """Generates installer for Node / React / Vite / Next.js projects."""
        pkg_manager = plan.environment.package_manager or "npm"
        run_cmd = plan.entrypoint.run_command or "npm run dev"
        port = plan.entrypoint.target_port or 5173

        return f"""# ==============================================================================
# One-Command Project Installer: {plan.project_name} (Node / React / Vite)
# Target OS: Windows (PowerShell)
# ==============================================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Header {{
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "    One-Command Installer: {plan.project_name} (Node/Web)" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}}

function Write-Step($stepNum, $stepTotal, $msg) {{
    Write-Host "[$stepNum/$stepTotal] $msg..." -ForegroundColor Yellow
}}

function Write-Success($msg) {{
    Write-Host "  [OK] $msg" -ForegroundColor Green
}}

function Write-Fail($msg) {{
    Write-Host ""
    Write-Host "  [ERROR] $msg" -ForegroundColor Red
    Write-Host ""
    Exit 1
}}

Write-Header

$ProjectDir = Join-Path -Path $PWD -ChildPath "{plan.project_name}"
$ArchiveFile = Join-Path -Path $PWD -ChildPath "{plan.project.archive_name}"
$DownloadUrl = "{plan.project.download_url}"

# 1. VERIFY NODE.JS RUNTIME
Write-Step 1 5 "Checking for Node.js runtime"
$FoundNode = Get-Command "node" -ErrorAction SilentlyContinue
if (-not $FoundNode) {{
    Write-Host "  Node.js is not installed or not in PATH." -ForegroundColor Yellow
    Write-Host "  Installing via winget (Windows Package Manager)..." -ForegroundColor Cyan
    try {{
        winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        $FoundNode = Get-Command "node" -ErrorAction SilentlyContinue
    }} catch {{
        Write-Fail "Please install Node.js from https://nodejs.org and re-run this command."
    }}
}}

if ($FoundNode) {{
    $nodeVer = & node -v
    Write-Success "Found Node.js runtime: $nodeVer"
}} else {{
    Write-Fail "Node.js is required. Install from https://nodejs.org"
}}

# 2. DOWNLOAD ARCHIVE
Write-Step 2 5 "Downloading project archive"
try {{
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ArchiveFile -UseBasicParsing
    Write-Success "Archive downloaded to $ArchiveFile"
}} catch {{
    Write-Fail "Download failed: $_"
}}

# 3. EXTRACT PROJECT
Write-Step 3 5 "Extracting files to $ProjectDir"
try {{
    if (Test-Path $ProjectDir) {{
        Remove-Item -Path $ProjectDir -Recurse -Force
    }}
    Expand-Archive -Path $ArchiveFile -DestinationPath $ProjectDir -Force
    Remove-Item -Path $ArchiveFile -Force
    Write-Success "Extracted successfully"
}} catch {{
    Write-Fail "Extraction failed: $_"
}}

# 4. INSTALL NODE DEPENDENCIES
Write-Step 4 5 "Installing packages via {pkg_manager}"
Set-Location -Path $ProjectDir
try {{
    & {pkg_manager} install
    Write-Success "Dependencies installed successfully"
}} catch {{
    Write-Fail "Package installation failed: $_"
}}

# 5. LAUNCH DEV SERVER
Write-Step 5 5 "Launching development server: {run_cmd}"
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  [READY] Starting {plan.project_name} on http://localhost:{port}" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop the application" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Start-Process "http://localhost:{port}"
& {run_cmd}
"""

    @classmethod
    def _generate_fullstack_script(cls, plan: InstallationPlan) -> str:
        """Generates installer for Full-Stack Python + React/Web projects."""
        py_script = cls._generate_python_script(plan)
        return py_script

    @classmethod
    def _generate_python_script(cls, plan: InstallationPlan) -> str:
        """Standard Python virtualenv installer."""
        # Format package list as a PowerShell array
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
        elif entry_type in ["npm_dev", "npm_start"]:
            run_cmd = f'& npm run dev'
        else:
            run_cmd = f'& "$VenvPython" "{entry_file}"'

        return f"""# ==============================================================================
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
# [1/7] DETECT PYTHON RUNTIME & VERIFY OR INSTALL PYTHON
# ------------------------------------------------------------------------------
Write-Step 1 7 "Checking for installed Python runtime (DETECT PYTHON RUNTIME)"

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
        # Continue to next candidate
    }}
}}

if (-not $FoundPython) {{
    Write-Host "  Python $MinVersion or newer was not detected in PATH (VERIFY OR INSTALL PYTHON)." -ForegroundColor Yellow
    Write-Host "  Attempting automated installation via winget (Windows Package Manager)..." -ForegroundColor Cyan
    
    try {{
        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        $FoundPython = "python"
        $InstalledVersion = "3.12 (auto-installed)"
    }} catch {{
        Write-Fail "Could not auto-install Python. Please install Python {plan.runtime.version} from https://www.python.org/downloads/ and rerun this installer."
    }}
}}

Write-Success "Using Python runtime: $FoundPython ($InstalledVersion)"

# ------------------------------------------------------------------------------
# [2/7] PRE-FLIGHT SYSTEM CHECKS
# ------------------------------------------------------------------------------
Write-Step 2 7 "Running pre-flight checks"

$drive = (Get-Item $PWD).PSDrive.Name
$freeSpaceGB = [math]::Round((Get-PSDrive $drive).Free / 1GB, 2)
if ($freeSpaceGB -lt 1.0) {{
    Write-Fail "Insufficient disk space ($freeSpaceGB GB free). At least 1.0 GB is required."
}}
Write-Success "Disk space check passed: $freeSpaceGB GB available on drive $drive:"

# ------------------------------------------------------------------------------
# [3/7] DOWNLOAD PROJECT ARCHIVE
# ------------------------------------------------------------------------------
Write-Step 3 7 "Downloading project archive"

try {{
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ArchiveFile -UseBasicParsing
    Write-Success "Archive downloaded successfully: $ArchiveFile"
}} catch {{
    Write-Fail "Failed to download project archive from $DownloadUrl. Error: $_"
}}

# ------------------------------------------------------------------------------
# [4/7] EXTRACT PROJECT FILES & SMART UPDATE
# ------------------------------------------------------------------------------
Write-Step 4 7 "Extracting project files (SMART UPDATE support) to $ProjectDir"

try {{
    if (Test-Path $ProjectDir) {{
        Write-Warn "Directory $ProjectDir exists (SMART UPDATE mode). Updating contents..."
    }} else {{
        New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
    }}

    Expand-Archive -Path $ArchiveFile -DestinationPath $ProjectDir -Force
    Remove-Item -Path $ArchiveFile -Force
    Write-Success "Extracted project to $ProjectDir"
}} catch {{
    Write-Fail "Failed to extract project archive: $_"
}}

# ------------------------------------------------------------------------------
# [5/7] SETUP ISOLATED VIRTUAL ENVIRONMENT
# ------------------------------------------------------------------------------
Write-Step 5 7 "Configuring ISOLATED VIRTUAL ENVIRONMENT (.venv)"

Set-Location -Path $ProjectDir
$VenvDir = Join-Path -Path $ProjectDir -ChildPath ".venv"
$VenvPython = Join-Path -Path $VenvDir -ChildPath "Scripts\\python.exe"
$VenvPip = Join-Path -Path $VenvDir -ChildPath "Scripts\\pip.exe"

if (-not (Test-Path $VenvPython)) {{
    try {{
        & $FoundPython -m venv .venv
        Write-Success "Virtual environment created at $VenvDir"
    }} catch {{
        Write-Fail "Failed to create virtual environment: $_"
    }}
}} else {{
    Write-Success "Existing virtual environment detected at $VenvDir"
}}

# Upgrade pip silently
& "$VenvPython" -m pip install --upgrade pip --quiet 2>$null

# ------------------------------------------------------------------------------
# [6/7] SYNCHRONIZE PROJECT DEPENDENCIES
# ------------------------------------------------------------------------------
Write-Step 6 7 "SYNCHRONIZE PROJECT DEPENDENCIES ({plan.dependencies_source})"

{packages_def}

if ($ResolvedPackages.Count -gt 0) {{
    Write-Host "  Packages to install: {packages_display}" -ForegroundColor Gray
    try {{
        & "$VenvPip" install @ResolvedPackages
        if ($LASTEXITCODE -ne 0) {{
            Write-Fail "pip install failed with exit code $LASTEXITCODE"
        }}
        Write-Success "All dependencies installed successfully"
    }} catch {{
        Write-Fail "Dependency installation error: $_"
    }}
}} else {{
    Write-Success "No external dependencies required"
}}

# ------------------------------------------------------------------------------
# [7/7] VALIDATION & START APPLICATION
# ------------------------------------------------------------------------------
Write-Step 7 7 "Validating and launching project entry point (START APPLICATION)"

$TargetEntry = Join-Path -Path $ProjectDir -ChildPath "{entry_file}"
if (-not (Test-Path $TargetEntry)) {{
    $found = Get-ChildItem -Path $ProjectDir -Filter "*.py" -Recurse | Select-Object -First 1
    if ($found) {{
        $TargetEntry = $found.FullName
        Write-Warn "Default entry file not found, falling back to: $TargetEntry"
    }} else {{
        Write-Fail "No runnable Python entry point found in $ProjectDir"
    }}
}}

Write-Success "Entry point validated: $TargetEntry"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  [SUCCESS] Installation complete! Launching {plan.project_name}..." -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Run project
{run_cmd}
"""
