"""Unix/macOS Bash installer script generator."""
from app.models.plan import InstallationPlan


class UnixGenerator:
    """Generates POSIX/Bash installation scripts (.sh) for Linux and macOS."""

    @classmethod
    def generate(cls, plan: InstallationPlan) -> str:
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
        else:
            run_cmd = f'"$VENV_PYTHON" "{entry_file}"'

        script = f"""#!/usr/bin/env bash
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
NC='\\033[0m' # No Color

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
    echo -e "  ${{GREEN}}[OK] $1${{NC}}"
}}

print_warn() {{
    echo -e "  ${{YELLOW}}[!] $1${{NC}}"
}}

print_fail() {{
    echo ""
    echo -e "  ${{RED}}[ERROR] $1${{NC}}"
    echo ""
    exit 1
}}

print_header

MIN_VERSION="{min_ver_num}"
PROJECT_DIR="$(pwd)/{plan.project_name}"
DOWNLOAD_URL="{plan.project.download_url}"

# ------------------------------------------------------------------------------
# [1/7] DETECT PYTHON RUNTIME
# ------------------------------------------------------------------------------
print_step 1 7 "Checking for installed Python runtime"

FOUND_PYTHON=""
CANDIDATES=("python3" "python")

for cmd in "${{CANDIDATES[@]}}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PY_VER=$("$cmd" -c "import sys; print(f'{{sys.version_info.major}}.{{sys.version_info.minor}}')" 2>/dev/null || true)
        if [ -n "$PY_VER" ]; then
            # Compare versions
            if [ "$(printf '%s\\n' "$MIN_VERSION" "$PY_VER" | sort -V | head -n1)" = "$MIN_VERSION" ]; then
                FOUND_PYTHON="$cmd"
                INSTALLED_VER="$PY_VER"
                break
            fi
        fi
    fi
done

# ------------------------------------------------------------------------------
# [2/7] VERIFY OR INSTALL PYTHON
# ------------------------------------------------------------------------------
print_step 2 7 "Verifying runtime compatibility"

if [ -n "$FOUND_PYTHON" ]; then
    print_success "Compatible Python $INSTALLED_VER found ($FOUND_PYTHON)"
else
    print_warn "Python >= $MIN_VERSION was not found on this system."
    echo -e "  -> Attempting package manager fallback..."

    if command -v apt-get >/dev/null 2>&1; then
        echo -e "${{GRAY}}  -> Installing python3 and python3-venv via apt-get...${{NC}}"
        sudo apt-get update -y && sudo apt-get install -y python3 python3-venv python3-pip
        FOUND_PYTHON="python3"
    elif command -v brew >/dev/null 2>&1; then
        echo -e "${{GRAY}}  -> Installing python via Homebrew...${{NC}}"
        brew install python@{plan.runtime.target_install_version}
        FOUND_PYTHON="python3"
    else
        print_fail "Please install Python >= $MIN_VERSION using your system package manager and re-run this script."
    fi
fi

# ------------------------------------------------------------------------------
# [3/7] DOWNLOAD AND SYNC PROJECT (SMART IN-PLACE UPDATE)
# ------------------------------------------------------------------------------
IS_EXISTING_PROJECT=false
if [ -d "$PROJECT_DIR" ]; then
    IS_EXISTING_PROJECT=true
    print_step 3 7 "Updating project files in-place"
    echo -e "  ${{CYAN}}-> [MODE: SMART UPDATE] Existing project installation detected.${{NC}}"
    echo -e "${{GRAY}}  -> Syncing latest code while preserving .env, databases, datasets, and .venv...${{NC}}"
    
    # Optional safety backup of previous Python files
    mkdir -p "$PROJECT_DIR/.backup" 2>/dev/null || true
    cp "$PROJECT_DIR"/*.py "$PROJECT_DIR/.backup/" 2>/dev/null || true
else
    print_step 3 7 "Downloading project files"
    echo -e "  ${{CYAN}}-> [MODE: FRESH INSTALL] Setting up new project workspace...${{NC}}"
    mkdir -p "$PROJECT_DIR"
fi

TEMP_ZIP="$PROJECT_DIR/project_source.zip"

echo -e "${{GRAY}}  -> Downloading from $DOWNLOAD_URL...${{NC}}"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$DOWNLOAD_URL" -o "$TEMP_ZIP"
elif command -v wget >/dev/null 2>&1; then
    wget -q "$DOWNLOAD_URL" -O "$TEMP_ZIP"
else
    print_fail "Neither curl nor wget was found to download project archive."
fi

print_success "Project archive downloaded."

echo -e "${{GRAY}}  -> Applying non-destructive overlay extraction...${{NC}}"
if command -v unzip >/dev/null 2>&1; then
    unzip -q -o "$TEMP_ZIP" -d "$PROJECT_DIR"
else
    "$FOUND_PYTHON" -m zipfile -e "$TEMP_ZIP" "$PROJECT_DIR"
fi
rm -f "$TEMP_ZIP"

if [ "$IS_EXISTING_PROJECT" = true ]; then
    print_success "Project code updated successfully in $PROJECT_DIR (local state preserved)."
else
    print_success "Project extracted into $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# ------------------------------------------------------------------------------
# [4/7] ISOLATED VIRTUAL ENVIRONMENT (.venv)
# ------------------------------------------------------------------------------
print_step 4 7 "Checking isolated virtual environment (.venv)"

VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${{GRAY}}  -> Creating fresh virtual environment...${{NC}}"
    "$FOUND_PYTHON" -m venv .venv
    print_success "Virtual environment created at .venv"
else
    print_success "Reusing existing virtual environment at .venv (zero reinstall needed)."
fi

# ------------------------------------------------------------------------------
# [5/7] SYNCHRONIZE PROJECT DEPENDENCIES
# ------------------------------------------------------------------------------
print_step 5 7 "Synchronizing project dependencies"

{packages_def}

"$VENV_PYTHON" -m pip install --upgrade pip --quiet

if [ -f "requirements.txt" ]; then
    echo -e "${{GRAY}}  -> Syncing packages from requirements.txt...${{NC}}"
    "$VENV_PYTHON" -m pip install -r requirements.txt
elif [ ${{#RESOLVED_PACKAGES[@]}} -gt 0 ]; then
    echo -e "${{GRAY}}  -> Syncing resolved packages: {packages_display}...${{NC}}"
    "$VENV_PYTHON" -m pip install "${{RESOLVED_PACKAGES[@]}}"
else
    print_success "No external dependencies required."
fi

print_success "Dependencies verified and synchronized in isolated environment."

# ------------------------------------------------------------------------------
# [6/7] VALIDATE PROJECT INTEGRITY
# ------------------------------------------------------------------------------
print_step 6 7 "Validating entry point and configuration"

ENTRY_FILE="{entry_file}"
if [ ! -f "$ENTRY_FILE" ]; then
    # Look for nested entry file
    FOUND_FILE=$(find . -name "$ENTRY_FILE" -print -quit)
    if [ -n "$FOUND_FILE" ]; then
        ENTRY_FILE="$FOUND_FILE"
    else
        print_fail "Entry point '$ENTRY_FILE' was not found in project directory."
    fi
fi

print_success "Entry point validated: $ENTRY_FILE"

# ------------------------------------------------------------------------------
# [7/7] START APPLICATION
# ------------------------------------------------------------------------------
print_step 7 7 "Launching application"
echo ""
echo -e "${{GREEN}}============================================================${{NC}}"
echo -e "  ${{GREEN}}Application is starting now!${{NC}}"
echo -e "${{GREEN}}============================================================${{NC}}"
echo ""

{run_cmd}
"""
        return script
