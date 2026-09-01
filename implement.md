One-Command Project Installer — Implementation Plan

1. Goal

Build a web platform where a developer uploads a project and receives a platform-specific command that installs and runs the project on another computer.

V1 scope

V1 focuses on Python projects.

The installer must:

Analyze an uploaded ZIP project.

Detect the Python project structure.

Detect requirements.txt when available.

If requirements.txt is missing, scan Python imports and infer dependencies.

Detect a suitable application entry point.

Detect whether the target machine already has a compatible Python version.

Reuse an existing compatible Python installation.

Install Python only when required.

Create an isolated virtual environment.

Install project dependencies into that environment.

Download/extract the project.

Start the application.

Generate Windows and Linux/macOS installer scripts.

Show the generated command in the web UI.

Explicitly out of scope for V1

Database provisioning.

Automatic database/query generation.

Node.js projects.

Java projects.

Docker orchestration.

Private dataset hosting.

Automatic Kaggle authentication.

Training an ML model for dependency detection.

2. High-Level Architecture

                    WEB APPLICATION
                          |
             +------------+------------+
             |                         |
        React Frontend            FastAPI Backend
             |                         |
             |                    Project Analyzer
             |                         |
             |                    Dependency Resolver
             |                         |
             |                    Installer Generator
             |                         |
             +------------+------------+
                          |
                    Project Storage
                          |
                    Generated Scripts

The system has five main modules:

1. Project Upload
2. Project Analyzer
3. Dependency Resolver
4. Runtime Manager / Installer Generator
5. Web Interface

3. Technology Stack

Frontend

React

Vite

Tailwind CSS

Fetch/Axios for API requests

Backend

Python

FastAPI

Pydantic

Python ast module for import analysis

Storage

Development:

Local filesystem

Production:

Object storage such as S3-compatible storage

PostgreSQL for project metadata

Execution/Security

Docker sandbox for untrusted project analysis

Resource limits

File-size limits

Timeouts

4. Repository Structure

project-installer/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── projects.py
│   │   │   └── installers.py
│   │   │
│   │   ├── analyzer/
│   │   │   ├── project.py
│   │   │   ├── python.py
│   │   │   ├── imports.py
│   │   │   ├── entrypoint.py
│   │   │   └── standard_library.py
│   │   │
│   │   ├── resolver/
│   │   │   ├── requirements.py
│   │   │   ├── package_map.py
│   │   │   └── resolver.py
│   │   │
│   │   ├── generator/
│   │   │   ├── powershell.py
│   │   │   └── unix.py
│   │   │
│   │   ├── security/
│   │   │   ├── zip_validator.py
│   │   │   ├── scanner.py
│   │   │   └── limits.py
│   │   │
│   │   └── models/
│   │       └── project.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── App.jsx
│   └── package.json
│
├── docs/
│   ├── design.md
│   └── implement.md
│
└── README.md

5. Module 1 — Project Upload

Input

A .zip file.

API

POST /api/projects
Content-Type: multipart/form-data

Process

Upload ZIP
   ↓
Validate extension
   ↓
Validate size
   ↓
Generate project ID
   ↓
Store ZIP
   ↓
Safely extract
   ↓
Analyze

Important security rule

Never extract ZIP files blindly.

Reject paths such as:

../../file
../../../etc/passwd

Normalize every extracted path and verify that it remains inside the project directory.

6. Module 2 — Project Analyzer

The analyzer determines what the project needs.

Detection order

1. Inspect project files
2. Detect Python project
3. Detect Python version requirement
4. Detect dependency declaration
5. Detect imports if required
6. Detect local modules
7. Detect entry point
8. Produce analysis result

Python project indicators

Look for:

*.py
requirements.txt
pyproject.toml
Pipfile
setup.py

V1 should prioritize:

requirements.txt

and fallback to:

*.py import scanning

7. Module 3 — Dependency Resolver

Case A: requirements.txt exists

Use it as the primary dependency source.

Example:

numpy
pandas>=2.0
flask

Do not replace it with guessed dependencies.

Case B: requirements.txt does not exist

Scan Python source files using ast.

Example:

import numpy
import pandas
import cv2
from PIL import Image
from sklearn.model_selection import train_test_split

Extract:

numpy
pandas
cv2
PIL
sklearn

Then:

cv2     → opencv-python
PIL     → Pillow
sklearn → scikit-learn

8. Standard Library Handling

Never install Python standard-library modules.

Examples:

os
sys
json
math
re
pathlib
sqlite3
datetime
logging
subprocess
typing

The analyzer should maintain a version-aware standard-library set.

9. Local Module Detection

Suppose:

project/
├── main.py
└── utils.py

and:

import utils

The analyzer should recognize that utils is a local project module.

Therefore:

utils → DO NOT pip install

This prevents false dependencies.

10. Package Mapping

Maintain a small mapping for import names that differ from package names.

Example:

{
  "cv2": "opencv-python",
  "PIL": "Pillow",
  "sklearn": "scikit-learn",
  "yaml": "PyYAML",
  "bs4": "beautifulsoup4",
  "dotenv": "python-dotenv"
}

This mapping should grow from observed cases and package metadata rather than becoming an arbitrary manually maintained dataset.

11. Entry Point Detection

V1 should support common entry points.

Priority:

main.py
app.py
run.py
server.py

If exactly one likely entry point exists:

Entry point: main.py

If multiple candidates exist:

Possible entry points:

1. main.py
2. app.py
3. server.py

Please choose one.

Do not randomly select between ambiguous entry points.

12. Project Analysis Result

Return structured data.

Example:

{
  "project_id": "abc123",
  "language": "python",
  "python_requirement": ">=3.11",
  "dependencies": [
    "numpy",
    "pandas",
    "flask"
  ],
  "entry_point": "main.py",
  "dependency_source": "requirements.txt",
  "warnings": []
}

13. Runtime Manager

The generated installer must check the target machine before installing anything.

Windows detection

Possible checks:

python --version
py --version
py -3.12 --version
where.exe python

The installer should find a compatible Python installation before downloading anything.

Unix detection

Check:

python3 --version
python --version
command -v python3
command -v python

14. Python Compatibility

Suppose the project requires:

Python >= 3.11

Target machine has:

Python 3.12

Result:

Compatible Python found.
Use existing Python.

Target machine has:

Python 3.8

Result:

Existing Python is incompatible.
Search for another installed version.

Only if no compatible runtime exists should installation be attempted.

15. Python Installation Strategy

V1 should use the operating system's normal package mechanism where practical.

Windows:

winget install --id Python.Python.3.12 --exact

Linux:

Use the detected package manager, such as apt, where supported.

macOS:

Use Homebrew where available.

The installer must verify the installation afterward.

Never assume installation succeeded.

16. Virtual Environment

Never install project dependencies globally.

Use:

python -m venv .venv

Then install through the environment's Python:

Windows:

.venv\Scripts\python.exe -m pip install -r requirements.txt

Unix:

.venv/bin/python -m pip install -r requirements.txt

This prevents the project from corrupting unrelated Python environments.

17. Generated Installer

The backend generates an installer for the target platform.

Windows

Example bootstrap:

irm https://example.com/i/PROJECT_ID.ps1 -OutFile install.ps1
.\install.ps1

For an experimental one-command version:

irm https://example.com/i/PROJECT_ID.ps1 | iex

The second approach should not be the preferred production security model because it executes remote content immediately.

Linux/macOS

Preferred:

curl -fsSL https://example.com/i/PROJECT_ID.sh -o install.sh && bash install.sh

18. Installer Steps

The generated installer should follow:

1. Print project information
2. Detect operating system
3. Detect compatible Python
4. Install Python only if necessary
5. Download project archive
6. Verify archive
7. Extract project
8. Create .venv
9. Upgrade pip if appropriate
10. Install dependencies
11. Validate required files
12. Start application

19. Dataset Support — Future V2

Dataset handling is intentionally excluded from V1.

V2 should support:

Included dataset
Kaggle dataset
Public URL
User-provided dataset

A future project manifest could look like:

datasets:
  - name: ravdess
    type: kaggle
    source: "kaggle-dataset-id"
    destination: "data/ravdess"

  - name: custom
    type: user
    destination: "data/custom"
    required: true

The installer should validate expected files before running the application.

20. Database Support — Future

Do not implement database provisioning in V1.

Later versions may support:

SQLite
PostgreSQL
MySQL

Potential future capabilities:

Detect database type.

Inspect schema.

Detect application database configuration.

Validate schema compatibility.

Run explicit migrations.

Request credentials securely.

Do not attempt to invent business queries automatically.

21. Security Requirements

Before public deployment, implement:

Upload protection

Maximum ZIP size.

Maximum extracted size.

Maximum file count.

ZIP path traversal protection.

Reject suspicious archive structures.

Analysis sandbox

Uploaded code must never execute directly on the backend.

Use an isolated container with:

No host filesystem access.

Restricted network.

CPU limit.

Memory limit.

Execution timeout.

Read-only base filesystem where possible.

Dependency security

Do not blindly trust package names inferred from imports.

Validate package metadata and give the user visibility into inferred dependencies.

Secrets

Never upload or display:

.env
API keys
passwords
private credentials

Treat them as sensitive.

22. Testing Strategy

Unit tests

Test:

requirements.txt parsing
import extraction
standard-library detection
local-module detection
package mapping
entry-point detection
Python version comparison

Integration tests

Create sample projects:

simple-python/
no-requirements/
multiple-entrypoints/
local-modules/
requirements-project/
invalid-project/

Installer tests

Use clean virtual machines/containers for:

Windows + Python installed
Windows + Python missing
Linux + Python installed
Linux + Python missing
Wrong Python version
Multiple Python versions

23. Development Milestones

Milestone 1

FastAPI
+
ZIP upload
+
safe extraction

Milestone 2

Python detection
+
requirements.txt parsing

Milestone 3

AST import scanner
+
standard library detection
+
local module detection

Milestone 4

Entry-point detection
+
analysis API

Milestone 5

Windows installer generator
+
Unix installer generator

Milestone 6

Runtime detection
+
Python installation fallback
+
virtual environment

Milestone 7

React UI
+
upload screen
+
analysis screen
+
command generation

Milestone 8

Security hardening
+
sandbox
+
limits
+
verification

24. V1 Success Criteria

V1 is successful when a user can take a simple Python project and:

ZIP project
   ↓
Upload to website
   ↓
Get analysis
   ↓
Generate command
   ↓
Run command on clean machine
   ↓
Python is detected/installed
   ↓
Virtual environment created
   ↓
Dependencies installed
   ↓
Application starts

The goal is not to support every possible project.

The goal is to make the common Python-project path extremely reliable.