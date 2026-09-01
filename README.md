# 🚀 One-Command Project Installer (`onecommandSite`)

> Turn any Python project into a reproducible, platform-specific **1-command installer** for Windows, Linux, and macOS.

---

## 💡 Core Philosophy

$$\text{DETECT} \longrightarrow \text{VERIFY} \longrightarrow \text{PLAN} \longrightarrow \text{INSTALL} \longrightarrow \text{VALIDATE} \longrightarrow \text{RUN}$$

Never: $\text{GUESS} \longrightarrow \text{EXECUTE} \longrightarrow \text{HOPE}$

---

## ✨ Features

- **🛡️ Secure ZIP Extraction**: Zip-Slip path traversal defense, file size / uncompressed size limits, and security scanning (detects hardcoded keys & sensitive files like `.env`).
- **🧠 Python AST Import Scanner**: No `requirements.txt`? Automatically parses Python AST import trees, ignores standard library modules (`os`, `sys`, `json`, `math`, `pathlib`, etc.) and project-local modules, mapping PyPI package names (`cv2` $\to$ `opencv-python`, `PIL` $\to$ `Pillow`, `sklearn` $\to$ `scikit-learn`, `yaml` $\to$ `PyYAML`, `dotenv` $\to$ `python-dotenv`).
- **🎯 Smart Entry Point Detection**: Identifies `if __name__ == '__main__':` blocks, common filenames (`main.py`, `app.py`, `server.py`, `run.py`), web frameworks (FastAPI, Flask, Streamlit, Gradio), and handles ambiguous entry points transparently.
- **📜 Intermediate Installation Plan (`InstallationPlan`)**: Decouples project analysis from target platform execution.
- **💻 Platform-Specific 1-Command Bootstrap Generators**:
  - **Windows (PowerShell)**: `irm http://.../i/ABC123.ps1 -OutFile install.ps1; .\install.ps1`
  - **Linux / macOS (Bash)**: `curl -fsSL http://.../i/ABC123.sh -o install.sh && bash install.sh`
- **⚡ 7-Step Verbose Terminal UX**:
  1. `[1/7]` Detects existing compatible Python on target machine (reuses immediately with 0 downloads).
  2. `[2/7]` Installs Python only if missing/incompatible via `winget` (Windows) or package manager (Linux/macOS).
  3. `[3/7]` Downloads and safely unpacks the project archive.
  4. `[4/7]` Creates an isolated virtual environment (`.venv`).
  5. `[5/7]` Installs resolved dependencies inside `.venv`.
  6. `[6/7]` Validates entry point and project integrity.
  7. `[7/7]` Starts the application cleanly!

---

## 🛠️ Quick Start

### 1. Backend (FastAPI)

```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```

API docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Frontend (React + Vite + Tailwind CSS)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Running Backend Tests

```bash
cd backend
python -m pytest -v
```

Includes tests for:
- Zip Slip path traversal defenses
- AST import extraction & stdlib filtering
- Local module discovery
- Package name translations (`package_map.py`)
- Python version requirement detection
- Entrypoint scoring & ambiguity detection
- PowerShell & Bash script generation
- End-to-end API integration test suite

---

## 📂 Repository Structure

```
onecommandSite/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Application
│   │   ├── config.py                # Environment & limits config
│   │   ├── storage.py               # Metadata & plan storage
│   │   ├── api/                     # REST API routes (upload, projects, installers)
│   │   ├── analyzer/                # AST import scanner, stdlib filter, entrypoint scorer
│   │   ├── resolver/                # requirements.txt parser & PyPI package mapping
│   │   ├── generator/               # PowerShell (.ps1) & Bash (.sh) script generators
│   │   ├── security/                # Zip Slip protection & security scanner
│   │   └── models/                  # Pydantic models for projects & installation plans
│   ├── tests/                       # Complete Pytest test suite
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/              # Dropzone, ProgressBar, AnalysisCard, CommandOutput, etc.
│   │   ├── pages/                   # HomePage
│   │   ├── api/                     # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── design.md                        # Architecture & Product Design
├── implement.md                     # Implementation Specifications
├── track.md                         # Context Tracker
└── README.md
```
