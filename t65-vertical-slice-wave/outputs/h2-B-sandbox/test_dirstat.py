import json
import subprocess
import sys
from pathlib import Path

import pytest

import dirstat


def make_tree(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "b.txt").write_text("hi")
    (tmp_path / "c.py").write_text("print(1)\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.txt").write_text("x")
    (sub / "noext").write_text("y")
    return tmp_path


def test_collect_stats_counts_and_bytes(tmp_path):
    make_tree(tmp_path)
    stats = dirstat.collect_stats(tmp_path)
    assert stats[".txt"]["count"] == 3
    assert stats[".txt"]["bytes"] == len("hello") + len("hi") + len("x")
    assert stats[".py"]["count"] == 1
    assert stats[".py"]["bytes"] == len("print(1)\n")
    assert stats["(no extension)"]["count"] == 1


def test_collect_stats_empty_dir(tmp_path):
    stats = dirstat.collect_stats(tmp_path)
    assert stats == {}


def test_collect_stats_missing_path(tmp_path):
    missing = tmp_path / "does_not_exist"
    with pytest.raises(dirstat.DirstatError) as exc_info:
        dirstat.collect_stats(missing)
    assert exc_info.value.code == "path_not_found"


def test_collect_stats_not_a_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hi")
    with pytest.raises(dirstat.DirstatError) as exc_info:
        dirstat.collect_stats(f)
    assert exc_info.value.code == "not_a_directory"


def test_main_json_output(tmp_path, capsys):
    make_tree(tmp_path)
    exit_code = dirstat.main([str(tmp_path), "--json"])
    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data[".txt"]["count"] == 3


def test_main_text_output(tmp_path, capsys):
    make_tree(tmp_path)
    exit_code = dirstat.main([str(tmp_path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert ".txt" in captured.out


def test_main_missing_dir_structured_error_json(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing), "--json"])
    captured = capsys.readouterr()
    assert exit_code == 1
    error = json.loads(captured.err)
    assert error["error"] == "path_not_found"


def test_main_missing_dir_no_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing)])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Traceback" not in captured.err
    assert "Error" in captured.err


def test_cli_subprocess_json(tmp_path):
    make_tree(tmp_path)
    script = Path(__file__).parent / "dirstat.py"
    result = subprocess.run(
        [sys.executable, str(script), str(tmp_path), "--json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data[".py"]["count"] == 1


def test_cli_subprocess_missing_dir(tmp_path):
    missing = tmp_path / "nope"
    script = Path(__file__).parent / "dirstat.py"
    result = subprocess.run(
        [sys.executable, str(script), str(missing)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
