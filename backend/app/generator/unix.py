"""Unix/macOS Bash installer script generator (supporting Python, React, Vite, Node, HTML, and Fullstack)."""
from app.models.plan import InstallationPlan


class UnixGenerator:
    """Generates POSIX/Bash installation scripts (.sh) for Linux and macOS."""

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
        """Generates Bash installer for static HTML/CSS/JS projects."""
        port = plan.entrypoint.target_port or 8080
        entry_file = plan.entrypoint.entry_file or "index.html"

        return f"""#!/usr/bin/env bash
# ==============================================================================
# One-Command Project Installer: {plan.project_name} (Static Web / HTML5)
# Target OS: Linux / macOS (Bash)
# ==============================================================================

set -e

RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
CYAN='\\033[0;36m'
NC='\\033[0m'

echo ""
echo -e "${{CYAN}}============================================================${{NC}}"
echo -e "         One-Command Installer: ${{YELLOW}}{plan.project_name}${{NC}} (Web)"
echo -e "${{CYAN}}============================================================${{NC}}"
echo ""

PROJECT_DIR="$PWD/{plan.project_name}"
ARCHIVE_FILE="$PWD/{plan.project.archive_name}"
DOWNLOAD_URL="{plan.project.download_url}"
PORT={port}

# 1. DOWNLOAD ARCHIVE
echo -e "${{YELLOW}}[1/4] Downloading project archive...${{NC}}"
curl -fsSL "$DOWNLOAD_URL" -o "$ARCHIVE_FILE"
echo -e "${{GREEN}}  [OK] Archive downloaded${{NC}}"

# 2. EXTRACT PROJECT
echo -e "${{YELLOW}}[2/4] Extracting files to $PROJECT_DIR...${{NC}}"
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
unzip -q -o "$ARCHIVE_FILE" -d "$PROJECT_DIR"
rm -f "$ARCHIVE_FILE"
echo -e "${{GREEN}}  [OK] Extraction complete${{NC}}"

# 3. VERIFY ENTRY FILE
echo -e "${{YELLOW}}[3/4] Verifying web assets...${{NC}}"
cd "$PROJECT_DIR"

# 4. LAUNCH LOCAL WEB SERVER
echo -e "${{YELLOW}}[4/4] Starting local web server on port $PORT...${{NC}}"
TARGET_URL="http://localhost:$PORT"

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$TARGET_URL" &
elif command -v open >/dev/null 2>&1; then
    open "$TARGET_URL" &
fi

echo ""
echo -e "${{GREEN}}============================================================${{NC}}"
echo -e "  [READY] Serving {plan.project_name} at $TARGET_URL"
echo -e "  Press Ctrl+C to stop the server"
echo -e "${{GREEN}}============================================================${{NC}}"
echo ""

if command -v python3 >/dev/null 2>&1; then
    python3 -m http.server $PORT
elif command -v python >/dev/null 2>&1; then
    python -m http.server $PORT
elif command -v npx >/dev/null 2>&1; then
    npx serve . -l $PORT
else
    echo "Server started. Open $TARGET_URL in your browser."
fi
"""

    @classmethod
    def _generate_node_script(cls, plan: InstallationPlan) -> str:
        """Generates Bash installer for Node / React / Vite / Next.js projects."""
        pkg_manager = plan.environment.package_manager or "npm"
        run_cmd = plan.entrypoint.run_command or "npm run dev"
        port = plan.entrypoint.target_port or 5173

        return f"""#!/usr/bin/env bash
# ==============================================================================
# One-Command Project Installer: {plan.project_name} (Node / React / Vite)
# Target OS: Linux / macOS (Bash)
# ==============================================================================

set -e

RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
CYAN='\\033[0;36m'
NC='\\033[0m'

echo ""
echo -e "${{CYAN}}============================================================${{NC}}"
echo -e "    One-Command Installer: ${{YELLOW}}{plan.project_name}${{NC}} (Node/Web)"
echo -e "${{CYAN}}============================================================${{NC}}"
echo ""

PROJECT_DIR="$PWD/{plan.project_name}"
ARCHIVE_FILE="$PWD/{plan.project.archive_name}"
DOWNLOAD_URL="{plan.project.download_url}"

# 1. VERIFY NODE.JS RUNTIME
echo -e "${{YELLOW}}[1/5] Checking for Node.js runtime...${{NC}}"
if ! command -v node >/dev/null 2>&1; then
    echo -e "${{RED}}  [ERROR] Node.js is not installed. Please install Node.js (https://nodejs.org) and rerun.${{NC}}"
    exit 1
fi
echo -e "${{GREEN}}  [OK] Node.js $(node -v) detected${{NC}}"

# 2. DOWNLOAD ARCHIVE
echo -e "${{YELLOW}}[2/5] Downloading project archive...${{NC}}"
curl -fsSL "$DOWNLOAD_URL" -o "$ARCHIVE_FILE"
echo -e "${{GREEN}}  [OK] Archive downloaded${{NC}}"

# 3. EXTRACT PROJECT
echo -e "${{YELLOW}}[3/5] Extracting files to $PROJECT_DIR...${{NC}}"
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
unzip -q -o "$ARCHIVE_FILE" -d "$PROJECT_DIR"
rm -f "$ARCHIVE_FILE"
echo -e "${{GREEN}}  [OK] Extraction complete${{NC}}"

# 4. INSTALL DEPENDENCIES
echo -e "${{YELLOW}}[4/5] Installing dependencies via {pkg_manager}...${{NC}}"
cd "$PROJECT_DIR"
{pkg_manager} install
echo -e "${{GREEN}}  [OK] Dependencies installed${{NC}}"

# 5. LAUNCH DEV SERVER
echo -e "${{YELLOW}}[5/5] Launching development server: {run_cmd}...${{NC}}"
TARGET_URL="http://localhost:{port}"

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$TARGET_URL" 2>/dev/null &
elif command -v open >/dev/null 2>&1; then
    open "$TARGET_URL" 2>/dev/null &
fi

echo ""
echo -e "${{GREEN}}============================================================${{NC}}"
echo -e "  [READY] Launching {plan.project_name} at $TARGET_URL"
echo -e "  Press Ctrl+C to stop the application"
echo -e "${{GREEN}}============================================================${{NC}}"
echo ""

{run_cmd}
"""

    @classmethod
    def _generate_fullstack_script(cls, plan: InstallationPlan) -> str:
        return cls._generate_python_script(plan)

    @classmethod
    def _generate_python_script(cls, plan: InstallationPlan) -> str:
        """Standard Python Bash installer."""
        # Format package list as a Bash array
        if plan.dependencies:
            packages_array_items = " ".join([f'"{p}"' for p in plan.dependencies])
            packages_def = f"RESOLVED_PACKAGES=({packages_array_items})"
            packages_display = ", ".join(plan.dependencies)
        else:
            packages_def = "RESOLVED_PACKAGES=()"
            packages_display = ""

        min_ver_num = "3.10"
        if ">=" in plan.runtime.version:
            min_ver_num = plan.runtime.version.replace(">=", "").strip()
        elif "==" in plan.runtime.version:
            min_ver_num = plan.runtime.version.replace("==", "").strip()

        entry_file = plan.entrypoint.entry_file or "main.py"
        entry_type = plan.entrypoint.command_type or "python"

        if entry_type == "streamlit":
            run_cmd = f'"$VENV_PYTHON" -m streamlit run "{entry_file}"'
        elif entry_type == "uvicorn":
            stem = entry_file.replace(".py", "").replace("/", ".").replace("\\", ".")
            run_cmd = f'"$VENV_PYTHON" -m uvicorn {stem}:app --reload'
        elif entry_type in ["npm_dev", "npm_start"]:
            run_cmd = f'npm run dev'
        else:
            run_cmd = f'"$VENV_PYTHON" "{entry_file}"'

        return f"""#!/usr/bin/env bash
# ==============================================================================
# One-Command Project Installer: {plan.project_name}
# Target OS: Linux / macOS (Bash)
# Philosophy: DETECT -> VERIFY -> PLAN -> INSTALL -> VALIDATE -> RUN
# ==============================================================================

set -e

# Color definitions
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
CYAN='\\033[0;36m'
GRAY='\\033[0;90m'
NC='\\033[0m'

print_header() {{
    echo ""
    echo -e "${{CYAN}}============================================================${{NC}}"
    echo -e "         One-Command Installer: ${{YELLOW}}{plan.project_name}${{NC}}"
    echo -e "${{CYAN}}============================================================${{NC}}"
    echo ""
}}

print_step() {{
    echo -e "${{YELLOW}}[$1/$2] $3...${{NC}}"
}}

print_success() {{
    echo -e "${{GREEN}}  [OK] $1${{NC}}"
}}

print_warn() {{
    echo -e "${{YELLOW}}  [!] $1${{NC}}"
}}

print_fail() {{
    echo ""
    echo -e "${{RED}}  [ERROR] $1${{NC}}"
    echo ""
    exit 1
}}

print_header

MIN_VERSION="{min_ver_num}"
PROJECT_DIR="$PWD/{plan.project_name}"
ARCHIVE_FILE="$PWD/{plan.project.archive_name}"
DOWNLOAD_URL="{plan.project.download_url}"

# ------------------------------------------------------------------------------
# [1/7] DETECT PYTHON RUNTIME & VERIFY OR INSTALL PYTHON
# ------------------------------------------------------------------------------
print_step 1 7 "Checking for installed Python runtime (DETECT PYTHON RUNTIME)"

FOUND_PYTHON=""
CANDIDATES=("python3" "python")

for cmd in "${{CANDIDATES[@]}}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        INSTALLED_VER=$("$cmd" -c "import sys; print(f'{{sys.version_info.major}}.{{sys.version_info.minor}}.{{sys.version_info.micro}}')" 2>/dev/null || true)
        if [ -n "$INSTALLED_VER" ]; then
            # Compare versions
            HIGHEST=$(printf '%s\\n%s' "$MIN_VERSION" "$INSTALLED_VER" | sort -V | tail -n1)
            if [ "$HIGHEST" = "$INSTALLED_VER" ] || [ "$MIN_VERSION" = "$INSTALLED_VER" ]; then
                FOUND_PYTHON="$cmd"
                break
            fi
        fi
    fi
done

if [ -z "$FOUND_PYTHON" ]; then
    print_warn "Python >= $MIN_VERSION not detected (VERIFY OR INSTALL PYTHON)."
    print_fail "Please install Python {plan.runtime.version} and re-run this script."
fi

print_success "Using Python runtime: $FOUND_PYTHON ($INSTALLED_VER)"

# ------------------------------------------------------------------------------
# [2/7] PRE-FLIGHT SYSTEM CHECKS
# ------------------------------------------------------------------------------
print_step 2 7 "Running pre-flight checks"

# Check disk space (need at least 1GB)
AVAILABLE_KB=$(df -k "$PWD" | tail -1 | awk '{{print $4}}')
if [ "$AVAILABLE_KB" -lt 1048576 ]; then
    print_fail "Insufficient disk space. At least 1.0 GB is required."
fi
print_success "Disk space check passed"

# ------------------------------------------------------------------------------
# [3/7] DOWNLOAD PROJECT ARCHIVE
# ------------------------------------------------------------------------------
print_step 3 7 "Downloading project archive"

if ! curl -fsSL "$DOWNLOAD_URL" -o "$ARCHIVE_FILE"; then
    print_fail "Failed to download project archive from $DOWNLOAD_URL"
fi
print_success "Archive downloaded successfully: $ARCHIVE_FILE"

# ------------------------------------------------------------------------------
# [4/7] EXTRACT PROJECT FILES & SMART UPDATE
# ------------------------------------------------------------------------------
print_step 4 7 "Extracting project files (SMART UPDATE mode) to $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    print_warn "Directory $PROJECT_DIR exists (SMART UPDATE). Updating contents..."
else
    mkdir -p "$PROJECT_DIR"
fi

if ! unzip -q -o "$ARCHIVE_FILE" -d "$PROJECT_DIR"; then
    print_fail "Failed to extract project archive. Ensure 'unzip' is installed."
fi
rm -f "$ARCHIVE_FILE"
print_success "Extracted project to $PROJECT_DIR"

# ------------------------------------------------------------------------------
# [5/7] SETUP ISOLATED VIRTUAL ENVIRONMENT
# ------------------------------------------------------------------------------
print_step 5 7 "Configuring ISOLATED VIRTUAL ENVIRONMENT (.venv)"

cd "$PROJECT_DIR"
VENV_DIR="$PROJECT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [ ! -f "$VENV_PYTHON" ]; then
    if ! "$FOUND_PYTHON" -m venv .venv; then
        print_fail "Failed to create virtual environment. Ensure 'python3-venv' is installed."
    fi
    print_success "Virtual environment created at $VENV_DIR"
else
    print_success "Existing virtual environment detected at $VENV_DIR"
fi

# Upgrade pip silently
"$VENV_PYTHON" -m pip install --upgrade pip --quiet 2>/dev/null || true

# ------------------------------------------------------------------------------
# [6/7] SYNCHRONIZE PROJECT DEPENDENCIES
# ------------------------------------------------------------------------------
print_step 6 7 "SYNCHRONIZE PROJECT DEPENDENCIES ({plan.dependencies_source})"

{packages_def}

if [ ${{#RESOLVED_PACKAGES[@]}} -gt 0 ]; then
    echo -e "${{GRAY}}  Packages to install: {packages_display}${{NC}}"
    if ! "$VENV_PIP" install "${{RESOLVED_PACKAGES[@]}}"; then
        print_fail "pip install failed"
    fi
    print_success "All dependencies installed successfully"
else
    print_success "No external dependencies required"
fi

# ------------------------------------------------------------------------------
# [7/7] VALIDATION & START APPLICATION
# ------------------------------------------------------------------------------
print_step 7 7 "Validating and launching project entry point (START APPLICATION)"

TARGET_ENTRY="$PROJECT_DIR/{entry_file}"
if [ ! -f "$TARGET_ENTRY" ]; then
    FOUND_ENTRY=$(find "$PROJECT_DIR" -name "*.py" -not -path "*/.*" | head -n 1)
    if [ -n "$FOUND_ENTRY" ]; then
        TARGET_ENTRY="$FOUND_ENTRY"
        print_warn "Default entry file not found, falling back to: $TARGET_ENTRY"
    else
        print_fail "No runnable Python entry point found in $PROJECT_DIR"
    fi
fi

print_success "Entry point validated: $TARGET_ENTRY"

echo ""
echo -e "${{GREEN}}============================================================${{NC}}"
echo -e "  [SUCCESS] Installation complete! Launching {plan.project_name}..."
echo -e "${{GREEN}}============================================================${{NC}}"
echo ""

# Run project
{run_cmd}
"""
