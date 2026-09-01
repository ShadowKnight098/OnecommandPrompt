# 🚀 One-Command Project Installer (`onecommandSite`) — Project Progress & Context Tracker

> **File Purpose:** This tracking file (`track.md`) serves as the single source of truth for the project lifecycle. If context runs out or another AI/developer picks up the project, this document provides complete continuity regarding architecture, specifications, progress, checklist, and exact next steps.

---

## 📌 1. Project Overview & Vision

- **Product Name:** One-Command Project Installer (`onecommandSite`)
- **Core Vision:** "Here is my project. Give me one command that prepares another computer and runs it."
- **Core Philosophy:**
  $$\text{DETECT} \longrightarrow \text{VERIFY} \longrightarrow \text{PLAN} \longrightarrow \text{INSTALL} \longrightarrow \text{VALIDATE} \longrightarrow \text{RUN}$$
  *(Never: $\text{GUESS} \longrightarrow \text{EXECUTE} \longrightarrow \text{HOPE}$)*
- **Primary Goal (V1):** Upload a Python project (`.zip`), analyze dependencies, entry points, and Python version constraints, generate a clean intermediate plan, and produce platform-specific one-command bootstrap scripts (`.ps1` for Windows, `.sh` for Linux/macOS) that inspect target runtime, install Python if missing, set up isolated `.venv`, install packages, and launch the application cleanly.

---

## 🛠️ 2. Technology Stack

| Layer | Technologies & Tools |
| :--- | :--- |
| **Frontend** | React 18+, Vite, Tailwind CSS, Lucide React (Icons), Axios / Fetch |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Uvicorn, Python AST (`ast` module) |
| **Generators** | PowerShell (`install.ps1`), POSIX Shell (`install.sh`) |
| **Storage & Security** | Local storage (Dev) / S3 + PostgreSQL (Prod), Zip Slip traversal protections, file/archive size limits |
| **Testing** | Pytest (Backend unit/integration), Sample test projects |

---

## 🏗️ 3. Architecture & Data Flow

```
+-------------------------------------------------------------------------+
|                              React Frontend                             |
|    (Upload UI -> Analysis Progress -> Review/Select Entrypoint -> Copy) |
+------------------------------------+------------------------------------+
                                     | HTTPS / REST API
                                     v
+-------------------------------------------------------------------------+
|                             FastAPI Backend                             |
|  +-------------------+  +-------------------+  +---------------------+  |
|  |  Project Upload   |  | Project Analyzer  |  | Dependency Resolver |  |
|  |  & Zip Validator  |  |  (AST + stdlib)   |  | (package_map.py)    |  |
|  +-------------------+  +-------------------+  +---------------------+  |
|                                    |                                    |
|                                    v                                    |
|                       [ Intermediate Install Plan ]                     |
|                                    |                                    |
|                                    v                                    |
|                        +-----------------------+                        |
|                        |  Installer Generator  |                        |
|                        | (PowerShell & Bash)   |                        |
|                        +-----------------------+                        |
+-------------------------------------------------------------------------+
```

### The Intermediate Installation Plan (`InstallationPlan`)
To decouple project analysis from script generation, we convert the project analysis into a structured plan:
```json
{
  "project_id": "ABC123",
  "runtime": {
    "type": "python",
    "version": ">=3.11"
  },
  "project": {
    "download_url": "/api/projects/ABC123/download",
    "archive_name": "project.zip"
  },
  "environment": {
    "type": "venv",
    "path": ".venv"
  },
  "dependencies": {
    "source": "requirements.txt",
    "packages": ["numpy", "pandas", "flask"]
  },
  "entrypoint": {
    "command": "main.py"
  }
}
```

---

## 📂 4. Target Repository Structure

```
onecommandSite/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py
│   │   │   ├── projects.py
│   │   │   └── installers.py
│   │   ├── analyzer/
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── python.py
│   │   │   ├── imports.py
│   │   │   ├── entrypoint.py
│   │   │   └── standard_library.py
│   │   ├── resolver/
│   │   │   ├── __init__.py
│   │   │   ├── requirements.py
│   │   │   ├── package_map.py
│   │   │   └── resolver.py
│   │   ├── generator/
│   │   │   ├── __init__.py
│   │   │   ├── powershell.py
│   │   │   └── unix.py
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── zip_validator.py
│   │   │   ├── scanner.py
│   │   │   └── limits.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── project.py
│   │       └── plan.py
│   ├── tests/
│   │   ├── test_analyzer.py
│   │   ├── test_imports.py
│   │   ├── test_resolver.py
│   │   ├── test_generators.py
│   │   └── sample_projects/
│   ├── storage/             # Project ZIPs & extracted files (dev)
│   ├── generated/           # Generated .ps1 / .sh scripts
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dropzone.jsx
│   │   │   ├── AnalysisCard.jsx
│   │   │   ├── DependenciesList.jsx
│   │   │   ├── EntrypointSelector.jsx
│   │   │   ├── CommandOutput.jsx
│   │   │   └── ProgressBar.jsx
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   └── ProjectDetailsPage.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── index.html
│
├── design.md                # System & UX Design Document
├── implement.md             # Implementation Plan & Specifications
└── track.md                 # Process & Progress Tracker (THIS FILE)
```

---

## 🚦 5. Implementation Roadmap & Status Checklist

### 📍 Milestone 1: Backend Foundation & Safe Upload API
- [x] Initialize Python backend environment and virtual environment
- [x] Create `backend/requirements.txt` (`fastapi`, `uvicorn`, `pydantic`, `python-multipart`, `pytest`, etc.)
- [x] Implement `backend/app/security/limits.py` (max file size, max extracted size, max file count)
- [x] Implement `backend/app/security/zip_validator.py` (Zip Slip path traversal prevention, path normalization)
- [x] Implement `POST /api/projects/upload` in `backend/app/api/upload.py`
- [x] Unit tests for Zip Slip and size limit rejections

### 📍 Milestone 2: Python Project Detection & `requirements.txt` Parser
- [x] Implement `backend/app/analyzer/python.py` (detect `*.py`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`)
- [x] Implement `backend/app/analyzer/project.py` (orchestrate extraction and structure inspection)
- [x] Implement `backend/app/resolver/requirements.py` (parse `requirements.txt` with specifier support `>=, ==, <=`)
- [x] Detect Python version hints from `pyproject.toml` / `setup.py` / `runtime.txt` or default to `>=3.10`
- [x] Unit tests for requirements parsing and version detection

### 📍 Milestone 3: AST Import Scanner, Stdlib Filter & Package Mapping
- [x] Implement `backend/app/analyzer/standard_library.py` (comprehensive list of Python 3.8-3.14 stdlib modules)
- [x] Implement `backend/app/analyzer/imports.py` using Python `ast` to parse AST trees across all `.py` files
- [x] Implement local module detection (identify project-local modules/packages and filter them out from pip installs)
- [x] Implement `backend/app/resolver/package_map.py` (mapping `cv2` $\to$ `opencv-python`, `PIL` $\to$ `Pillow`, `sklearn` $\to$ `scikit-learn`, `yaml` $\to$ `PyYAML`, etc.)
- [x] Implement fallback resolver `backend/app/resolver/resolver.py` (explicit requirements $\to$ imports fallback)
- [x] Unit tests for AST parsing, stdlib filtering, and package name mapping

### 📍 Milestone 4: Entry-Point Detection & Analysis API
- [x] Implement `backend/app/analyzer/entrypoint.py` (detect `main.py`, `app.py`, `run.py`, `server.py`, `if __name__ == '__main__':` blocks)
- [x] Handle unambiguous entry points vs ambiguous entry points requiring user selection
- [x] Implement `backend/app/models/project.py` & `backend/app/models/plan.py`
- [x] Implement `GET /api/projects/{id}` and `POST /api/projects/{id}/entrypoint`
- [x] Unit tests for entry point detection logic

### 📍 Milestone 5: PowerShell & Unix Installer Generators
- [x] Create clean, robust template for Windows `install.ps1`:
  - [x] Terminal banner and step progress reporting `[1/7]` to `[7/7]`
  - [x] Check installed Python (`python`, `py`, `where.exe`) and check version compatibility
  - [x] Fallback installation via `winget install --id Python.Python.3.12 --exact` if missing/incompatible
  - [x] Project download / extraction
  - [x] Virtual environment creation (`python -m venv .venv`)
  - [x] Pip dependency installation (`.venv\Scripts\python.exe -m pip install -r requirements.txt`)
  - [x] Entry point validation and application launch
- [x] Create clean, robust template for Unix/macOS `install.sh`:
  - [x] Terminal banner and step progress reporting `[1/7]` to `[7/7]`
  - [x] Check installed Python (`python3`, `python`, `command -v`) and verify version
  - [x] Fallback instructions / package manager installation (`apt`, `brew`)
  - [x] Project download / extraction
  - [x] Virtual environment creation (`python3 -m venv .venv`)
  - [x] Pip dependency installation (`.venv/bin/python -m pip install -r requirements.txt`)
  - [x] Entry point validation and application launch
- [x] Implement `backend/app/generator/powershell.py` and `backend/app/generator/unix.py`
- [x] Implement `GET /i/{project_id}.ps1` and `GET /i/{project_id}.sh` endpoints

### 📍 Milestone 6: Intermediate Installation Plan & API Completion
- [x] Connect Analyzer, Resolver, and Generator via `InstallationPlan`
- [x] Implement `POST /api/projects/{id}/generate` endpoint
- [x] Serve generated installation files and project download packages
- [x] End-to-end tests verifying script output matching project specs

### 📍 Milestone 7: React + Tailwind Frontend (Vite)
- [x] Initialize Vite React frontend with Tailwind CSS
- [x] Create Drag-and-drop ZIP upload component (`Dropzone.jsx`) with active animated progress & sample projects
- [x] Create Analysis Results View (`AnalysisCard.jsx`) showing runtime, dependencies, source, and warnings
- [x] Create Missing `requirements.txt` Warning & Review View (`DependenciesList.jsx`)
- [x] Create Ambiguous Entry Point Selection View (`EntrypointSelector.jsx`)
- [x] Create Command Generation Screen (`CommandOutput.jsx`) with 1-click copy for Windows (`irm ...`) and Linux/macOS (`curl ...`)
- [x] Add "What will this command do?" expandable explanation drawer
- [x] Wire up API client (`api/client.js`) connecting frontend to FastAPI backend

### 📍 Milestone 8: Security Hardening, Verification & Full End-to-End Demo
- [x] Security testing against malicious ZIPs (zip bombs, directory traversal)
- [x] End-to-end testing with sample projects:
  - [x] `FastAPI Project` (main.py + requirements.txt)
  - [x] `Data Science Project` (app.py with imports: `numpy`, `cv2`, `PIL`)
  - [x] `Multi-Entrypoint App` (has both `main.py` and `server.py`)
  - [x] `Local Modules Project` (imports internal project modules)
- [x] Documentation and user guide in `README.md`

---

## 📊 6. Current Status Snapshot

- **Current Phase:** Completed V1 Production Build & Classic Clean Typographic Design
- **Completed So Far:**
  - Full FastAPI Backend with AST Analyzer, Resolver, Generator, Storage, and Security
  - Complete 15/15 Pytest suite passing
  - React 18 + Vite + Tailwind CSS Frontend crafted with a clean paper canvas (`#fafafa`), deep ink typography (`#09090b` / `#18181b`), balanced headings (`text-wrap: balance`), crisp JetBrains Mono code styling, and authentic terminal window
  - Project documentation in `README.md`
- **In Progress:** Ready for runtime execution / deployment.

---

## 🧭 7. Quick Handoff Instructions for New AI Session / Developer

When picking up work in a new conversation or session:
1. **Read this file (`track.md`)** to get instant orientation on architecture and progress.
2. Run backend tests: `cd backend && python -m pytest`
3. Run frontend dev server: `cd frontend && npm run dev`
4. Run backend dev server: `cd backend && python run.py`
