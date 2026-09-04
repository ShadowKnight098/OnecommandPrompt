"""Unit tests for Web, HTML, CSS, React, and Fullstack Project Analyzer."""
import pytest
from pathlib import Path
import tempfile
import json
from app.analyzer.web import WebProjectAnalyzer
from app.analyzer.project import ProjectAnalyzer
from app.generator.powershell import PowerShellGenerator
from app.generator.unix import UnixGenerator
from app.models.plan import (
    InstallationPlan,
    RuntimeConfig,
    ProjectDownloadConfig,
    EnvironmentConfig,
    EntryPointConfig,
)


@pytest.fixture
def temp_static_html_project():
    """Creates a temporary static HTML/CSS web project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Awesome Portfolio Website</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-gray-100 p-8">
    <h1 class="text-3xl font-bold">Welcome</h1>
    <script src="js/main.js"></script>
</body>
</html>"""
        (root / "index.html").write_text(html_content, encoding="utf-8")
        
        css_dir = root / "css"
        css_dir.mkdir()
        (css_dir / "style.css").write_text("body { font-family: sans-serif; }", encoding="utf-8")

        js_dir = root / "js"
        js_dir.mkdir()
        (js_dir / "main.js").write_text("console.log('App loaded');", encoding="utf-8")

        yield root


@pytest.fixture
def temp_react_vite_project():
    """Creates a temporary React + Vite project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        pkg_json = {
            "name": "my-vite-react-app",
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "lucide-react": "^0.300.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.2.0",
                "vite": "^5.0.0",
                "tailwindcss": "^3.4.0"
            }
        }
        (root / "package.json").write_text(json.dumps(pkg_json, indent=2), encoding="utf-8")
        (root / "vite.config.js").write_text("export default {};", encoding="utf-8")
        (root / "index.html").write_text("<html><head><title>Vite App</title></head><body><div id='root'></div><script type='module' src='/src/main.jsx'></script></body></html>", encoding="utf-8")

        src = root / "src"
        src.mkdir()
        (src / "main.jsx").write_text("import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\n", encoding="utf-8")
        (src / "App.jsx").write_text("export default function App() { return <h1>Hello Vite</h1>; }\n", encoding="utf-8")

        yield root


def test_scan_static_html_project(temp_static_html_project):
    """Tests deep scanning of static HTML, CSS, and CDN libraries."""
    res = WebProjectAnalyzer.scan_web_project(temp_static_html_project)
    
    assert res["is_web_project"] is True
    assert res["project_type"] == "static_html"
    assert res["ui_framework"] == "html5"
    assert res["css_framework"] == "tailwind"
    assert res["entry_point"] == "index.html"
    
    meta = res["web_metadata"]
    assert meta.html_title == "Awesome Portfolio Website"
    assert "Tailwind CSS" in meta.cdn_libraries
    assert "Lucide Icons" in meta.cdn_libraries
    assert "css/style.css" in meta.stylesheets
    assert "js/main.js" in meta.scripts


def test_scan_react_vite_project(temp_react_vite_project):
    """Tests scanning of React + Vite projects."""
    res = WebProjectAnalyzer.scan_web_project(temp_react_vite_project)
    
    assert res["is_web_project"] is True
    assert res["project_type"] == "vite"
    assert res["ui_framework"] == "react"
    assert res["css_framework"] == "tailwind"
    
    meta = res["web_metadata"]
    assert meta.dev_command == "npm run dev"
    assert meta.target_port == 5173
    
    dep_names = [d.name for d in res["dependencies"]]
    assert "react" in dep_names
    assert "lucide-react" in dep_names


def test_project_analyzer_orchestrator_web(temp_react_vite_project):
    """Tests ProjectAnalyzer end-to-end classification for web projects."""
    analysis = ProjectAnalyzer.analyze_project(
        project_id="TEST_WEB_1",
        project_name="my-vite-react-app",
        extracted_root=temp_react_vite_project,
    )
    
    assert analysis.language in ["javascript", "typescript"]
    assert analysis.project_type == "vite"
    assert analysis.entry_point == "index.html"
    assert analysis.web_metadata is not None
    assert analysis.web_metadata.target_port == 5173


def test_powershell_generator_web():
    """Tests generating PowerShell command for static web project."""
    plan = InstallationPlan(
        project_id="WEB01",
        project_name="Portfolio",
        runtime=RuntimeConfig(type="static_web", version=">=3.10"),
        project=ProjectDownloadConfig(
            project_id="WEB01",
            archive_name="project.zip",
            download_url="https://test.com/api/projects/WEB01/download",
            target_directory_name="Portfolio",
        ),
        environment=EnvironmentConfig(type="static", path=".", package_manager="none"),
        dependencies_source="cdn",
        dependencies=["Tailwind CSS"],
        entrypoint=EntryPointConfig(
            command_type="static_http",
            entry_file="index.html",
            run_command="python -m http.server 8080",
            target_port=8080,
        ),
    )
    
    script = PowerShellGenerator.generate(plan)
    assert "http.server" in script
    assert "8080" in script
    assert "Start-Process" in script


def test_unix_generator_node():
    """Tests generating Bash command for Node/React project."""
    plan = InstallationPlan(
        project_id="NODE01",
        project_name="ReactApp",
        runtime=RuntimeConfig(type="node", version=">=18.0.0"),
        project=ProjectDownloadConfig(
            project_id="NODE01",
            archive_name="project.zip",
            download_url="https://test.com/api/projects/NODE01/download",
            target_directory_name="ReactApp",
        ),
        environment=EnvironmentConfig(type="node_modules", path="node_modules", package_manager="npm"),
        dependencies_source="package.json",
        dependencies=["react", "react-dom"],
        entrypoint=EntryPointConfig(
            command_type="npm_dev",
            entry_file="index.html",
            run_command="npm run dev",
            target_port=5173,
        ),
    )
    
    script = UnixGenerator.generate(plan)
    assert "npm install" in script
    assert "npm run dev" in script
    assert "5173" in script
