One-Command Project Installer — Product & System Design

1. Product Vision

Create a platform that turns a project into a reproducible installation experience.

The developer should be able to say:

"Here is my project. Give me one command that prepares another computer and runs it."

The system should automate deterministic setup work while asking the user only when required information cannot safely be inferred.

2. Core Principle

DETECT → VERIFY → PLAN → INSTALL → VALIDATE → RUN

Never:

GUESS → EXECUTE → HOPE

This principle should guide the entire product.

3. User Journey

Step 1 — Upload

The landing page presents:

+------------------------------------------------+
|                                                |
|           One-Command Project Installer        |
|                                                |
|       Upload your Python project as ZIP        |
|                                                |
|          [ Drop ZIP here ]                     |
|                                                |
+------------------------------------------------+

Step 2 — Analyze

After upload:

Analyzing project...

✓ Project structure detected
✓ Python project detected
✓ Dependencies analyzed
✓ Entry point detected
✓ Runtime requirements detected

A progress indicator should make the process feel active rather than frozen.

4. Analysis Results Screen

Example:

+------------------------------------------------+
| Project Analysis                         ✓     |
+------------------------------------------------+
|                                                |
| Runtime                                        |
| Python              3.11+                      |
|                                                |
| Entry Point                                    |
| main.py                                        |
|                                                |
| Dependencies                                   |
| 8 packages                                     |
|                                                |
| Dependency Source                              |
| requirements.txt                               |
|                                                |
| Warnings                                       |
| None                                           |
|                                                |
|              [ Generate Installer ]             |
+------------------------------------------------+

5. Missing requirements.txt Experience

If no requirements file exists:

+------------------------------------------------+
| requirements.txt not found                    |
+------------------------------------------------+
|                                                |
| We analyzed your Python source files.          |
|                                                |
| Detected dependencies:                         |
|                                                |
| ✓ numpy                                         |
| ✓ pandas                                        |
| ✓ opencv-python                                |
| ✓ Pillow                                        |
| ✓ scikit-learn                                 |
|                                                |
| These dependencies were inferred from imports. |
|                                                |
|              [ Review ] [ Continue ]           |
+------------------------------------------------+

This is important because inferred dependencies are less certain than explicitly declared dependencies.

6. Ambiguous Entry Point

If several possible entry points are found:

+------------------------------------------------+
| Choose application entry point                |
+------------------------------------------------+
|                                                |
| We found multiple possible entry points.      |
|                                                |
| ( ) main.py                                    |
| ( ) app.py                                     |
| ( ) server.py                                  |
|                                                |
|              [ Confirm ]                       |
+------------------------------------------------+

Never silently choose an arbitrary file.

7. Generated Command Screen

The command screen should be extremely simple.

+------------------------------------------------+
| Your installer is ready                  ✓     |
+------------------------------------------------+
|                                                |
| Windows                                        |
|                                                |
| irm https://example.com/i/ABC123.ps1           |
|     -OutFile install.ps1; .\install.ps1        |
|                                                |
|                    [ Copy ]                    |
|                                                |
| Linux / macOS                                  |
|                                                |
| curl -fsSL https://example.com/i/ABC123.sh     |
| -o install.sh && bash install.sh               |
|                                                |
+------------------------------------------------+

Include a small expandable section:

What will this command do?

which explains:

1. Detect Python
2. Install it only if required
3. Download your project
4. Create an isolated environment
5. Install dependencies
6. Start the project

8. Installer UX

The installer should be verbose enough to explain what's happening.

Example:

============================================
        Project Installer
============================================

[1/7] Checking Python...
✓ Python 3.12.4 found

[2/7] Checking compatibility...
✓ Compatible with project

[3/7] Downloading project...
████████████████████ 100%

[4/7] Creating virtual environment...
✓ .venv created

[5/7] Installing dependencies...
✓ numpy
✓ pandas
✓ flask

[6/7] Validating project...
✓ main.py found

[7/7] Starting application...

🚀 Application started

If Python is missing:

[1/7] Checking Python...
✗ Compatible Python not found

→ Installing required Python runtime...

The important UX behavior is:

Existing compatible runtime = reuse it immediately.

9. Error UX

Errors should be actionable.

Bad:

ERROR 0x34982

Good:

Python 3.8 was found, but this project requires Python 3.11 or newer.

We could not find another compatible Python installation.

Please install Python 3.11+ and run the installer again.

Another example:

Dependency installation failed.

Package:
torch

Reason:
The package could not be installed for this operating system.

Suggested action:
Review the project's supported Python/OS versions.

10. Architecture

                    ┌─────────────────┐
                    │ React Frontend  │
                    └────────┬────────┘
                             │
                           HTTPS
                             │
                    ┌────────▼────────┐
                    │ FastAPI Backend │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   Project Analyzer   Dependency Resolver   Generator
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                      Project Metadata
                             │
                             ▼
                      Object Storage

11. Component Responsibilities

Frontend

Responsible for:

Uploading project.

Showing progress.

Displaying analysis.

Handling user choices.

Displaying generated commands.

Copying commands.

The frontend should not perform project analysis.

API Layer

Responsible for:

Request validation.

Upload handling.

Project IDs.

Returning analysis.

Returning generated installers.

Analyzer

Responsible for understanding the project.

It should not:

Install dependencies.

Execute arbitrary project code.

Modify the user's project.

Dependency Resolver

Responsible for determining the dependency installation plan.

Priority:

Explicit requirements
       ↓
Project metadata
       ↓
Import analysis
       ↓
Package mapping

Installer Generator

Turns the validated installation plan into platform-specific scripts.

Inputs:

OS
Python requirement
Project URL
Dependencies
Entry point

Outputs:

PowerShell installer
Unix shell installer

12. Data Model

A project record can contain:

{
  "id": "ABC123",
  "name": "emotion-detector",
  "language": "python",
  "python_requirement": ">=3.11",
  "entry_point": "main.py",
  "dependencies": [
    "numpy",
    "pandas"
  ],
  "dependency_source": "requirements.txt",
  "status": "ready",
  "warnings": []
}

Potential statuses:

uploaded
analyzing
needs_input
ready
failed
expired

13. Installation Plan

Do not generate a script directly from raw upload data.

First create an intermediate installation plan.

Example:

{
  "runtime": {
    "type": "python",
    "version": ">=3.11"
  },
  "project": {
    "download": "/projects/ABC123/download"
  },
  "environment": {
    "type": "venv",
    "path": ".venv"
  },
  "dependencies": [
    "numpy",
    "pandas",
    "flask"
  ],
  "entrypoint": {
    "command": "main.py"
  }
}

Then:

Installation Plan
       ↓
Windows Generator
       ↓
install.ps1

Installation Plan
       ↓
Unix Generator
       ↓
install.sh

This separation makes the architecture easier to extend.

14. Why the Intermediate Plan Matters

Without it:

Upload → Generate random script

With it:

Upload
 ↓
Analyze
 ↓
Validated installation plan
 ↓
Platform-specific generator

Later we can add:

Docker generator
Windows executable generator
CI/CD generator
Cloud deployment generator

without rewriting the analyzer.

15. Dataset Design — V2

Datasets should be represented as explicit resources.

Possible types:

included
kaggle
url
user

Example:

{
  "name": "ravdess",
  "type": "kaggle",
  "source": "owner/dataset",
  "destination": "data/ravdess",
  "required": true
}

For custom data:

{
  "name": "custom-data",
  "type": "user",
  "destination": "data/custom",
  "required": true
}

The system should validate the data before launching the project.

16. Dataset UX — Future

The analysis screen could show:

DATASETS

✓ Included
  data/train.csv

⚠ Kaggle
  RAVDESS
  Requires user authentication

⚠ Custom
  Expected at: data/custom

The installer should never embed private credentials.

17. Database Design — Future

Database provisioning is deliberately excluded from V1.

Future architecture:

Database Detector
       ↓
Database Type
       ↓
Schema Inspector
       ↓
Migration Validator
       ↓
Database Setup

The system should prefer explicit migrations/schema definitions over guessing application logic.

18. Security Design

The biggest security principle:

Uploaded projects are untrusted.

Never execute uploaded project code on the main backend.

Use:

Upload
  ↓
Quarantine
  ↓
Sandbox
  ↓
Static analysis
  ↓
Validation
  ↓
Metadata

Potential sandbox restrictions:

No privileged container
No host filesystem
Restricted network
CPU limit
RAM limit
Process limit
Execution timeout
Maximum archive size
Maximum extracted size

19. Trust Model for Generated Commands

The installer command is effectively a remote code execution mechanism.

Therefore production should eventually include:

HTTPS only.

Signed installers or verified script hashes.

Immutable project versions.

Short-lived project URLs where appropriate.

Clear display of installer source.

Versioned generated scripts.

Audit logs.

No secrets embedded in scripts.

Avoid making:

curl | bash

the final trust model.

It can be used for a prototype, but production should favor downloading a verifiable installer and then executing it.

20. Scalability Design

V1:

FastAPI
+
local storage

Later:

Load Balancer
      ↓
API Servers
      ↓
Job Queue
      ↓
Analyzer Workers
      ↓
Object Storage
      ↓
PostgreSQL

Large uploads and analysis jobs should become asynchronous.

21. Future Expansion

After V1 is stable:

V1
Python

V2
Datasets

V3
Node.js

V4
Docker

V5
Java

V6
Database setup

V7
Cloud deployment

V8
Multi-language project detection

The analyzer architecture should allow additional providers:

RuntimeProvider
├── PythonProvider
├── NodeProvider
├── JavaProvider
└── DockerProvider

Likewise:

DatasetProvider
├── IncludedProvider
├── KaggleProvider
├── URLProvider
└── UserProvider

22. Design Philosophy

The product should feel:

Simple for the user.

Transparent about what it is doing.

Fast when dependencies already exist.

Conservative when information is ambiguous.

Safe around uploaded code.

Modular internally.

Extensible to other runtimes later.

The user should not need to understand:

virtual environments
PATH
pip
Python versions
dependency resolution
package mappings

The platform handles those details.

The user experience should ultimately feel like:

UPLOAD
   ↓
ANALYZE
   ↓
COPY ONE COMMAND
   ↓
RUN
   ↓
DONE 🚀