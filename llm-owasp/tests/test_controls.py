"""Tests for owasp_llm_audit.controls"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from owasp_llm_audit.controls import load_controls, CONTROL_IDS


def test_load_controls_returns_all_ten():
    controls = load_controls()
    assert len(controls) == 10


def test_load_controls_ids_match():
    controls = load_controls()
    assert [c.id for c in controls] == CONTROL_IDS


def test_load_controls_names_non_empty():
    for ctrl in load_controls():
        assert ctrl.name.strip(), f"{ctrl.id} has empty name"


def test_load_controls_descriptions_non_empty():
    for ctrl in load_controls():
        assert len(ctrl.description) > 50, f"{ctrl.id} description too short"


def test_load_controls_missing_file(tmp_path, monkeypatch):
    import owasp_llm_audit.controls as mod
    monkeypatch.setattr(mod, "DOCS_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        mod.load_controls()
