"""Tests for owasp_llm_audit.collector"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from owasp_llm_audit.collector import collect, _gather, FILE_LIMIT, TOTAL_LIMIT


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_collect_single_file(tmp_path):
    f = _write(tmp_path, "agent.py", "print('hello')")
    result = collect(str(f))
    assert "agent.py" in result
    assert "print('hello')" in result


def test_collect_directory(tmp_path):
    _write(tmp_path, "a.py", "# a")
    _write(tmp_path, "b.md", "# b")
    result = collect(str(tmp_path))
    assert "a.py" in result
    assert "b.md" in result


def test_collect_filter_glob(tmp_path):
    _write(tmp_path, "uc1-foo.md", "uc1 content")
    _write(tmp_path, "other.md", "other content")
    result = collect(str(tmp_path), filter_glob="uc1-*.md")
    assert "uc1-foo.md" in result
    assert "other.md" not in result


def test_collect_multi_target(tmp_path):
    d1 = tmp_path / "d1"; d1.mkdir()
    d2 = tmp_path / "d2"; d2.mkdir()
    _write(d1, "a.py", "# a")
    _write(d2, "b.py", "# b")
    result = collect([str(d1), str(d2)])
    assert "a.py" in result
    assert "b.py" in result


def test_collect_skips_oversized_files(tmp_path, monkeypatch):
    """Oversized files are skipped; smaller files after them are still included."""
    import owasp_llm_audit.collector as mod
    # Set a tiny total limit so the big file fills the budget
    monkeypatch.setattr(mod, "TOTAL_LIMIT", 100)
    _write(tmp_path, "aaa_big.py", "x" * 200)   # sorted first, exceeds limit
    _write(tmp_path, "zzz_small.py", "# hi")    # sorted after; should still appear
    result = mod.collect(str(tmp_path))
    assert "zzz_small.py" in result
    assert "skipped" in result.lower()


def test_collect_unsupported_extension_ignored(tmp_path):
    _write(tmp_path, "data.csv", "a,b,c")
    with pytest.raises(ValueError, match="No supported files"):
        collect(str(tmp_path))


def test_collect_missing_target():
    with pytest.raises(FileNotFoundError):
        collect("/nonexistent/path/agent.py")
