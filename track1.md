# One-Command Project Installer — Project Tracker

> **Last Updated**: 2026-08-31
> **Status**: Active Development

---

## What This Project Does

Transforms any Python project (uploaded as ZIP or folder) into a **single copy-paste command** that bootstraps the entire project on any Windows, macOS, or Linux machine — installing Python if needed, creating a virtual environment, installing dependencies, and running the app.

```
UPLOAD → ANALYZE → PLAN → GENERATE COMMAND → TARGET MACHINE RUNS IT
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, Tailwind CSS 3.4, Lucide Icons |
| Backend | Python, FastAPI, Pydantic v2, Uvicorn |
| Analysis | Python `ast` module (static parsing, no code execution) |
| Scripts | PowerShell (.ps1) for Windows, Bash (.sh) for Linux/macOS |
| Storage | Local filesystem (migrating to Supabase — see changelog) |

---

## Project Structure

```
d:\onecommandSite\
├── README.md
├── design.md                    # Architecture specs
├── implement.md                 # Implementation checklist
├── track.md                     # Original context tracker
├── track1.md                    # THIS FILE — full project tracker
│
├── backend/
│   ├── run.py                   # Dev server launcher
│   ├── requirements.txt         # Python dependencies
│   ├── storage/                 # Local project file storage
│   ├── generated/               # Generated script cache
│   ├── tests/                   # Pytest test suite
│   │   ├── test_analyzer.py
│   │   ├── test_api.py
│   │   ├── test_entrypoint.py
│   │   ├── test_generators.py
│   │   ├── test_resolver.py
│   │   └── test_zip_security.py
│   └── app/
│       ├── main.py              # FastAPI app, CORS, SPA mount
│       ├── config.py            # Paths, limits, env vars
│       ├── storage.py           # ProjectStore (persistence layer)
│       ├── models/
│       │   ├── project.py       # ProjectRecord, ProjectAnalysis, etc.
│       │   └── plan.py          # InstallationPlan schemas
│       ├── api/
│       │   ├── upload.py        # /upload and /upload-folder endpoints
│       │   ├── projects.py      # Project CRUD, generate, download
│       │   └── installers.py    # Raw .ps1 / .sh script endpoints
│       ├── analyzer/
│       │   ├── project.py       # Main analysis orchestrator
│       │   ├── imports.py       # AST import extraction
│       │   ├── entrypoint.py    # Entry point scoring & detection
│       │   ├── python.py        # Python version detection
│       │   └── standard_library.py  # Stdlib module list
│       ├── resolver/
│       │   ├── resolver.py      # Unified dependency resolver
│       │   ├── requirements.py  # requirements.txt parser
│       │   └── package_map.py   # Import → PyPI mapping
│       ├── generator/
│       │   ├── powershell.py    # Windows .ps1 script generator
│       │   └── unix.py          # Linux/macOS .sh script generator
│       └── security/
│           ├── limits.py        # Size/count/extension limits
│           ├── scanner.py       # Secret & credential scanner
│           └── zip_validator.py # Zip-Slip & bomb protection
│
└── frontend/
    ├── package.json
    ├── vite.config.js           # Dev proxy → backend :8000
    ├── tailwind.config.js       # Paper & Ink theme
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        ├── api/
        │   └── client.js        # API client (uploadProject, uploadFolder, etc.)
        ├── pages/
        │   └── HomePage.jsx     # 4-stage UI orchestrator
        └── components/
            ├── Navbar.jsx       # Header with pipeline steps
            ├── Dropzone.jsx     # Drag-drop upload (ZIP + folder)
            ├── ProgressBar.jsx  # Analysis progress animation
            ├── AnalysisCard.jsx # Results dashboard
            ├── DependenciesList.jsx   # Dependency review modal
            ├── EntrypointSelector.jsx # Entry point picker modal
            └── CommandOutput.jsx      # Terminal output + script viewer
```

---

## All API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/projects/upload` | Upload ZIP file → analyze |
| `POST` | `/api/projects/upload-folder` | Upload folder files → analyze |
| `GET` | `/api/projects/{id}` | Get project record + plan + commands |
| `POST` | `/api/projects/{id}/entrypoint` | Override entry point |
| `POST` | `/api/projects/{id}/dependencies` | Update dependencies |
| `POST` | `/api/projects/{id}/generate` | Regenerate install plan + commands |
| `GET` | `/api/projects/{id}/download` | Download project ZIP |
| `GET` | `/i/{id}.ps1` | Raw PowerShell installer script |
| `GET` | `/i/{id}.sh` | Raw Bash installer script |
| `GET` | `/api/installers/{id}/plan` | Raw JSON installation plan |

---

## Data Models

### ProjectRecord
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique project ID (8-char hex) |
| `original_filename` | `str` | Uploaded filename |
| `status` | `enum` | `uploaded` / `analyzing` / `needs_input` / `ready` / `failed` / `expired` |
| `analysis` | `ProjectAnalysis` | Full analysis results (nested) |
| `archive_path` | `str` | Path to stored ZIP |
| `extracted_path` | `str` | Path to extracted files |
| `created_at` | `datetime` | Creation timestamp |

### ProjectAnalysis
| Field | Type | Description |
|-------|------|-------------|
| `python_requirement` | `str` | e.g. `>=3.10` |
| `entry_point` | `str?` | Selected entry file |
| `entry_point_framework` | `str?` | `fastapi` / `flask` / `streamlit` / etc. |
| `candidate_entry_points` | `list` | Scored candidates with code preview |
| `is_ambiguous_entrypoint` | `bool` | True if top candidates are close in score |
| `dependencies` | `list[DependencyItem]` | Resolved packages |
| `dependency_source` | `str` | `requirements.txt` or `inferred_imports` |
| `security_warnings` | `list` | Detected secrets/issues |
| `file_count` / `total_size_bytes` | `int` | Project stats |

### InstallationPlan
| Field | Type | Description |
|-------|------|-------------|
| `project_id` / `project_name` | `str` | Identifiers |
| `runtime` | `RuntimeConfig` | Python version info |
| `project` | `ProjectDownloadConfig` | Download URL + archive name |
| `environment` | `EnvironmentConfig` | venv settings |
| `dependencies` | `list[str]` | Package list for pip |
| `entrypoint` | `EntryPointConfig` | Run command + framework |

---

## Security Features

1. **Zip-Slip Protection** — Rejects archives with path traversal (`..`) or absolute paths
2. **Zip Bomb Defense** — 50 MB upload limit, 200 MB extracted limit, 2000 file limit
3. **Binary Blocking** — Warns on `.exe`, `.dll`, `.bat`, `.msi`, `.so` files
4. **Secret Scanning** — Detects `.env`, `id_rsa`, API keys, AWS keys, Stripe keys, GitHub PATs
5. **No Code Execution** — 100% static AST parsing, never imports/runs user code
6. **Isolated venv** — Generated scripts always create `.venv`

---

## Generated Installer Steps (7-step bootstrap on target machine)

1. **[1/7] Detect Python** — Check if compatible Python exists
2. **[2/7] Install if Missing** — Auto-install via `winget` / `apt` / `brew`
3. **[3/7] Download Project** — Fetch ZIP from server, extract
4. **[4/7] Create venv** — Isolated `.venv`
5. **[5/7] Install Dependencies** — `pip install` all packages
6. **[6/7] Validate** — Confirm entry point exists
7. **[7/7] Launch** — Run with `python` / `uvicorn` / `streamlit`

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `HomePage.jsx` | 4-stage orchestrator: upload → analyzing → results → command |
| `Navbar.jsx` | Header with pipeline steps (DETECT → VERIFY → PLAN → INSTALL → RUN) |
| `Dropzone.jsx` | Drag-drop for ZIP + folder, 3 sample project generators |
| `ProgressBar.jsx` | 4-step animated analysis progress |
| `AnalysisCard.jsx` | Results dashboard (runtime, entry point, deps, security) |
| `DependenciesList.jsx` | Modal to review/toggle/add/delete packages |
| `EntrypointSelector.jsx` | Modal to pick entry point with code preview |
| `CommandOutput.jsx` | Terminal display with OS tabs, copy button, script inspector |

---

## Changelog

### 2026-08-31 — Folder Upload Fix

**Problem**: Selecting a folder triggered a client-side ZIP builder (`bundleFilesIntoZip`) that produced malformed ZIPs, causing backend extraction errors.

**Fix**: Folder uploads now send files directly to `/api/projects/upload-folder` endpoint.

**Files Changed**:
- `frontend/src/api/client.js` — Added `uploadFolder()` function
- `frontend/src/pages/HomePage.jsx` — `handleFileSelected` detects array vs File
- `frontend/src/components/Dropzone.jsx` — Passes raw file arrays; removed `bundleFilesIntoZip` (~110 lines) and `processFileList`

---

### 2026-08-31 — Backend Startup Fix (Windows)

**Problem**: `run.py` crashed on Windows — rocket emoji can't be encoded in cp1252 console.

**Fix**: Removed emoji from print statement.

**Files Changed**:
- `backend/run.py` — Removed emoji from startup message

---

### 2026-09-01 — PowerShell & Unix Installer Array Syntax Fix

**Problem**: The generated `.ps1` installer script had double quote collisions and a trailing comma in array syntax (`$ResolvedPackages`), which caused Windows PowerShell 5.1 / 7 to throw parser errors (`Missing expression after ','` and `Unexpected token`).

**Fix**:
- Updated [`backend/app/generator/powershell.py`](file:///d:/onecommandSite/backend/app/generator/powershell.py) to format resolved dependencies into a clean PowerShell array (`$ResolvedPackages = @(...)`) without trailing commas.
- Updated [`backend/app/generator/unix.py`](file:///d:/onecommandSite/backend/app/generator/unix.py) to format resolved dependencies into a standard Bash array (`RESOLVED_PACKAGES=(...)`).
- Validated with Windows PowerShell parser AST engine: 0 syntax errors.

---

### 2026-09-01 — AST Malware & Payload Scanner (Security Layer)

**Feature**: Enhanced [`backend/app/security/scanner.py`](file:///d:/onecommandSite/backend/app/security/scanner.py) with an AST (Abstract Syntax Tree) code scanner to inspect Python files statically for dangerous/malicious patterns:
- **Obfuscated Payloads**: Detects `exec()` / `eval()` combined with `base64`, `b85decode`, `zlib`, or dynamic decompressed strings.
- **Dangerous Process Spawning**: Flags `os.system()`, `os.popen()`, and `subprocess.Popen(..., shell=True)`.
- **Reverse Shells / Socket Exfiltration**: Detects `socket.connect()`, `pty.spawn()`, and interactive shell signatures.
- **Untrusted Deserialization**: Flags `pickle.loads()`.
- **Destructive Commands**: Flags `rm -rf /` and recursive filesystem deletions.

---

### 2026-09-01 — 1-Click Share & Deep Linking Feature

**Feature**: Added project sharing capabilities across frontend and backend:
- **Share Button**: Added prominent Share button in [`CommandOutput.jsx`](file:///d:/onecommandSite/frontend/src/components/CommandOutput.jsx) with native Web Share API support (`navigator.share`).
- **Share Modal**: Includes 1-click Direct Link copy, GitHub README Markdown snippet with SVG badge, and quick social links (Twitter/X, WhatsApp, Email).
- **Deep Linking**: [`HomePage.jsx`](file:///d:/onecommandSite/frontend/src/pages/HomePage.jsx) automatically loads shared projects from URL query params (`?p=PROJECT_ID`) and updates browser history on upload.

---

### 2026-09-01 — Animated Carousel Hero & Modern Marketplace Redesign

**Features**:
1. **Prominent Hero Carousel ([`StepsCarousel.jsx`](file:///d:/onecommandSite/frontend/src/components/StepsCarousel.jsx))**:
   - Re-positioned to the top hero section for maximum visual impact.
   - **Rich Animations**: Smooth auto-play progress bar filling up dynamically across 4 steps, ambient radial glow effects, and interactive pause/play toggles.
   - **High-Tech Terminal Window**: Color-coded syntax highlights, live AST engine status badge, copyable code snippets, and structured feature checklists.
2. **Dynamic Project Marketplace & Hub ([`ProjectShowcase.jsx`](file:///d:/onecommandSite/frontend/src/components/ProjectShowcase.jsx))**:
   - Modern developer storefront with framework-specific color banners (FastAPI, Flask, Streamlit, Django, Python CLI).
   - **Category Filter Tabs**: Quick filter by *All*, *FastAPI*, *Streamlit*, *AI & Data Science*, and *CLI*.
   - **1-Click Command Copy**: Direct command copy button right on each project card.
   - **Live Search & Empty States**: Real-time debounce search across project names, descriptions, and frameworks.
3. **Custom Project Name & Description**:
   - Added metadata inputs in [`Dropzone.jsx`](file:///d:/onecommandSite/frontend/src/components/Dropzone.jsx) and backend [`upload.py`](file:///d:/onecommandSite/backend/app/api/upload.py) to save custom project titles and descriptions in Supabase.
4. **Floating `+ New Project` Button**:
   - Added a floating corner action button on [`HomePage.jsx`](file:///d:/onecommandSite/frontend/src/pages/HomePage.jsx) to restart the flow anytime.

---

## Supabase Setup Instructions (SQL Editor)

Run the following SQL snippet in your Supabase project's **SQL Editor**:

```sql
-- 1. Create Projects Table
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  original_filename TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'uploaded',
  error_message TEXT,
  analysis JSONB,
  archive_path TEXT,
  extracted_path TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create Installation Plans Table
CREATE TABLE IF NOT EXISTS installation_plans (
  project_id TEXT PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE,
  plan_data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create Public Storage Bucket for Project Archives
INSERT INTO storage.buckets (id, name, public)
VALUES ('project-archives', 'project-archives', true)
ON CONFLICT (id) DO NOTHING;

-- 4. Enable Public Read Access Policy for Project Archives
CREATE POLICY "Public Read Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'project-archives');

-- 5. Enable Public Insert/Upload Access Policy for Project Archives
CREATE POLICY "Public Upload Access"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'project-archives');

-- 6. Enable Public Update Access Policy for Project Archives
CREATE POLICY "Public Update Access"
ON storage.objects FOR UPDATE
USING (bucket_id = 'project-archives');
```

