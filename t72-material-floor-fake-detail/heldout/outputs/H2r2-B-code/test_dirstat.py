import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "dirstat.py"


def run(*args):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return result


def make_tree(base):
    (base / "a.py").write_text("x" * 10)
    (base / "b.py").write_text("x" * 20)
    (base / "notes.txt").write_text("x" * 5)
    (base / "README").write_text("x" * 7)  # no extension
    sub = base / "sub"
    sub.mkdir()
    (sub / "c.py").write_text("x" * 3)


def test_json_output_counts_and_bytes(tmp_path):
    make_tree(tmp_path)

    result = run(str(tmp_path), "--json")

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["success"] is True
    assert data["total_files"] == 5
    assert data["total_bytes"] == 45

    by_ext = {e["extension"]: e for e in data["extensions"]}
    assert by_ext[".py"] == {"extension": ".py", "files": 3, "bytes": 33}
    assert by_ext[".txt"] == {"extension": ".txt", "files": 1, "bytes": 5}
    assert by_ext[""] == {"extension": "", "files": 1, "bytes": 7}


def test_json_extensions_sorted_by_bytes_desc(tmp_path):
    make_tree(tmp_path)

    result = run(str(tmp_path), "--json")
    data = json.loads(result.stdout)

    sizes = [e["bytes"] for e in data["extensions"]]
    assert sizes == sorted(sizes, reverse=True)


def test_text_output_is_human_readable(tmp_path):
    make_tree(tmp_path)

    result = run(str(tmp_path))

    assert result.returncode == 0
    assert ".py" in result.stdout
    assert "TOTAL" in result.stdout
    # text mode must not be JSON
    assert not result.stdout.strip().startswith("{")


def test_empty_directory(tmp_path):
    result = run(str(tmp_path), "--json")

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data == {
        "success": True,
        "path": str(tmp_path),
        "total_files": 0,
        "total_bytes": 0,
        "extensions": [],
    }


def test_nested_directories_are_recursed(tmp_path):
    make_tree(tmp_path)

    result = run(str(tmp_path), "--json")
    data = json.loads(result.stdout)

    by_ext = {e["extension"]: e for e in data["extensions"]}
    assert by_ext[".py"]["files"] == 3  # a.py, b.py, sub/c.py


def test_missing_directory_json_gives_structured_error(tmp_path):
    missing = tmp_path / "does-not-exist"

    result = run(str(missing), "--json")

    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["success"] is False
    assert data["error"]["code"] == "not_found"
    assert str(missing) in data["error"]["message"]
    assert result.stderr == ""


def test_missing_directory_text_gives_message_not_traceback(tmp_path):
    missing = tmp_path / "does-not-exist"

    result = run(str(missing))

    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout
    assert "not found" in result.stderr.lower()


def test_path_is_file_not_directory_gives_structured_error(tmp_path):
    a_file = tmp_path / "just_a_file.txt"
    a_file.write_text("hi")

    result = run(str(a_file), "--json")

    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["success"] is False
    assert data["error"]["code"] == "not_a_directory"


def test_help_has_usage_examples():
    result = run("--help")

    assert result.returncode == 0
    assert "--json" in result.stdout
    assert "Examples:" in result.stdout
