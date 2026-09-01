"""Tests for entry point scoring and ambiguity detection."""
from pathlib import Path
from app.analyzer.entrypoint import EntryPointDetector


def test_single_main_entrypoint(tmp_path):
    main_py = tmp_path / "main.py"
    main_py.write_text("""
def main():
    print("Application entry")

if __name__ == '__main__':
    main()
""", encoding="utf-8")

    utils_py = tmp_path / "utils.py"
    utils_py.write_text("def helper(): pass", encoding="utf-8")

    selected, framework, candidates, is_ambiguous = EntryPointDetector.detect_entry_points(tmp_path)

    assert selected == "main.py"
    assert is_ambiguous is False
    assert len(candidates) >= 1
    assert candidates[0].has_main_block is True


def test_ambiguous_entrypoints(tmp_path):
    main_py = tmp_path / "main.py"
    main_py.write_text("""
if __name__ == '__main__':
    print("Main entry")
""", encoding="utf-8")

    app_py = tmp_path / "app.py"
    app_py.write_text("""
if __name__ == '__main__':
    print("App entry")
""", encoding="utf-8")

    selected, framework, candidates, is_ambiguous = EntryPointDetector.detect_entry_points(tmp_path)
    assert is_ambiguous is True
    assert len(candidates) >= 2
