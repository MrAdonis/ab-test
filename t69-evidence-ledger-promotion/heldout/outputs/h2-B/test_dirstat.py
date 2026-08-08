import json
import subprocess
import sys
from pathlib import Path

import pytest

import dirstat


SCRIPT = str(Path(__file__).with_name("dirstat.py"))


def run_cli(*args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
    )


# --- collect_stats: normal paths ---------------------------------------


def test_counts_and_bytes_by_extension(tmp_path):
    (tmp_path / "a.py").write_bytes(b"x" * 10)
    (tmp_path / "b.py").write_bytes(b"x" * 20)
    (tmp_path / "c.txt").write_bytes(b"x" * 5)

    data = dirstat.collect_stats(tmp_path)

    assert data["extensions"][".py"] == {"count": 2, "bytes": 30}
    assert data["extensions"][".txt"] == {"count": 1, "bytes": 5}
    assert data["total_files"] == 3
    assert data["total_bytes"] == 35


def test_recurses_into_subdirectories(tmp_path):
    (tmp_path / "a.py").write_bytes(b"x" * 3)
    sub = tmp_path / "nested" / "deeper"
    sub.mkdir(parents=True)
    (sub / "b.py").write_bytes(b"x" * 7)

    data = dirstat.collect_stats(tmp_path)

    assert data["extensions"][".py"] == {"count": 2, "bytes": 10}
    assert data["total_files"] == 2


def test_files_without_extension_grouped_separately(tmp_path):
    (tmp_path / "README").write_bytes(b"x" * 4)
    (tmp_path / ".gitignore").write_bytes(b"x" * 2)

    data = dirstat.collect_stats(tmp_path)

    assert data["extensions"][dirstat.NO_EXT_KEY] == {"count": 2, "bytes": 6}
    assert data["total_files"] == 2


# --- collect_stats: edge cases -------------------------------------------


def test_empty_directory(tmp_path):
    data = dirstat.collect_stats(tmp_path)

    assert data["extensions"] == {}
    assert data["total_files"] == 0
    assert data["total_bytes"] == 0


def test_path_resolved_to_absolute(tmp_path):
    data = dirstat.collect_stats(tmp_path)
    assert Path(data["path"]).is_absolute()


# --- collect_stats: error paths -------------------------------------------


def test_missing_directory_raises_file_not_found(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(FileNotFoundError):
        dirstat.collect_stats(missing)


def test_path_is_a_file_raises_not_a_directory(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    with pytest.raises(NotADirectoryError):
        dirstat.collect_stats(f)


# --- CLI: human-readable output -------------------------------------------


def test_cli_human_output(tmp_path):
    (tmp_path / "a.py").write_bytes(b"x" * 10)

    result = run_cli(str(tmp_path))

    assert result.returncode == 0
    assert ".py" in result.stdout
    assert "Total: 1 files, 10 bytes" in result.stdout


# --- CLI: --json output ----------------------------------------------------


def test_cli_json_output_success(tmp_path):
    (tmp_path / "a.py").write_bytes(b"x" * 10)
    (tmp_path / "b.md").write_bytes(b"x" * 5)

    result = run_cli(str(tmp_path), "--json")

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["data"]["total_files"] == 2
    assert payload["data"]["total_bytes"] == 15
    assert payload["data"]["extensions"][".py"]["count"] == 1


# --- CLI: structured errors, no traceback ----------------------------------


def test_cli_missing_directory_json_error(tmp_path):
    missing = tmp_path / "nope"

    result = run_cli(str(missing), "--json")

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    payload = json.loads(result.stdout)
    assert payload["success"] is False
    assert "error" in payload


def test_cli_missing_directory_human_error(tmp_path):
    missing = tmp_path / "nope"

    result = run_cli(str(missing))

    assert result.returncode == 1
    assert "Traceback" not in result.stdout
    assert "Traceback" not in result.stderr
    assert "error" in result.stderr.lower()


def test_cli_file_instead_of_directory_json_error(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")

    result = run_cli(str(f), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["success"] is False
