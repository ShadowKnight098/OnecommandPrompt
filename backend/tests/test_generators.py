"""Tests for installer script generators."""
from app.models.plan import (
    InstallationPlan,
    RuntimeConfig,
    ProjectDownloadConfig,
    EnvironmentConfig,
    EntryPointConfig,
)
from app.generator.powershell import PowerShellGenerator
from app.generator.unix import UnixGenerator


def test_powershell_generator():
    plan = InstallationPlan(
        project_id="TEST001",
        project_name="my-demo-app",
        runtime=RuntimeConfig(type="python", version=">=3.11", target_install_version="3.12"),
        project=ProjectDownloadConfig(
            project_id="TEST001",
            archive_name="project.zip",
            download_url="http://localhost:8000/api/projects/TEST001/download",
            target_directory_name="my-demo-app",
        ),
        environment=EnvironmentConfig(type="venv", path=".venv"),
        dependencies_source="requirements.txt",
        dependencies=["numpy", "pandas", "fastapi"],
        entrypoint=EntryPointConfig(command_type="python", entry_file="main.py", run_command="python main.py"),
    )

    ps_script = PowerShellGenerator.generate(plan)

    assert "$MinVersion = [version]\"3.11\"" in ps_script
    assert "DETECT PYTHON RUNTIME" in ps_script
    assert "VERIFY OR INSTALL PYTHON" in ps_script
    assert "ISOLATED VIRTUAL ENVIRONMENT" in ps_script
    assert "SYNCHRONIZE PROJECT DEPENDENCIES" in ps_script
    assert "START APPLICATION" in ps_script
    assert "main.py" in ps_script
    assert "SMART UPDATE" in ps_script


def test_unix_generator():
    plan = InstallationPlan(
        project_id="TEST001",
        project_name="my-demo-app",
        runtime=RuntimeConfig(type="python", version=">=3.10", target_install_version="3.12"),
        project=ProjectDownloadConfig(
            project_id="TEST001",
            archive_name="project.zip",
            download_url="http://localhost:8000/api/projects/TEST001/download",
            target_directory_name="my-demo-app",
        ),
        environment=EnvironmentConfig(type="venv", path=".venv"),
        dependencies_source="inferred_imports",
        dependencies=["opencv-python", "Pillow"],
        entrypoint=EntryPointConfig(command_type="python", entry_file="app.py", run_command="python app.py"),
    )

    sh_script = UnixGenerator.generate(plan)

    assert "#!/usr/bin/env bash" in sh_script
    assert "MIN_VERSION=\"3.10\"" in sh_script
    assert "DETECT PYTHON RUNTIME" in sh_script
    assert "VERIFY OR INSTALL PYTHON" in sh_script
    assert "ISOLATED VIRTUAL ENVIRONMENT" in sh_script
    assert "SMART UPDATE" in sh_script
    assert "opencv-python" in sh_script
    assert "Pillow" in sh_script
