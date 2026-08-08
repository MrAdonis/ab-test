import json
import subprocess
import sys
from pathlib import Path

import dirstat

SCRIPT = Path(__file__).parent / "dirstat.py"


def make_tree(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"1234")
    (tmp_path / "b.txt").write_bytes(b"12")
    (tmp_path / "c.py").write_bytes(b"123456")
    (tmp_path / "noext").write_bytes(b"1")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.txt").write_bytes(b"12345")
    return tmp_path


def test_collect_stats_groups_by_extension(tmp_path):
    make_tree(tmp_path)
    stats = dirstat.collect_stats(tmp_path)

    assert stats[".txt"] == {"files": 3, "bytes": 11}
    assert stats[".py"] == {"files": 1, "bytes": 6}
    assert stats["no_ext"] == {"files": 1, "bytes": 1}


def test_collect_stats_empty_dir(tmp_path):
    assert dirstat.collect_stats(tmp_path) == {}


def test_run_success(tmp_path):
    make_tree(tmp_path)
    result = dirstat.run(str(tmp_path))

    assert result["success"] is True
    assert result["data"][".txt"]["files"] == 3


def test_run_missing_path_returns_structured_error(tmp_path):
    missing = tmp_path / "does_not_exist"
    result = dirstat.run(str(missing))

    assert result == {"success": False, "error": f"path does not exist: {missing}"}


def test_run_path_is_file_not_dir(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("x")
    result = dirstat.run(str(f))

    assert result["success"] is False
    assert "not a directory" in result["error"]


def test_cli_json_output(tmp_path):
    make_tree(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--json"],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["success"] is True
    assert payload["data"][".txt"]["files"] == 3


def test_cli_missing_dir_no_traceback(tmp_path):
    missing = tmp_path / "nope"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(missing), "--json"],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 1
    assert "Traceback" not in proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["success"] is False
    assert "does not exist" in payload["error"]


def test_cli_text_output_no_json_flag(tmp_path):
    make_tree(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0
    assert ".txt" in proc.stdout
    assert "Traceback" not in proc.stderr
