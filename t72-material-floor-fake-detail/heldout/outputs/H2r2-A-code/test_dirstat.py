import json
import subprocess
import sys
from pathlib import Path

import pytest

import dirstat


def make_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    make_file(tmp_path / "a.txt", b"hello")  # 5 bytes
    make_file(tmp_path / "b.txt", b"hi")  # 2 bytes
    make_file(tmp_path / "sub" / "c.py", b"print(1)")  # 8 bytes
    make_file(tmp_path / "sub" / "d.PY", b"x")  # 1 byte, uppercase ext
    make_file(tmp_path / "noext", b"abc")  # 3 bytes, no extension
    return tmp_path


class TestCollectStats:
    def test_counts_and_bytes_per_extension(self, sample_dir: Path):
        stats = dirstat.collect_stats(str(sample_dir))

        assert stats[".txt"].count == 2
        assert stats[".txt"].total_bytes == 7
        assert stats[".py"].count == 2  # .py and .PY merged (lowercased)
        assert stats[".py"].total_bytes == 9
        assert stats[dirstat.NO_EXT_KEY].count == 1
        assert stats[dirstat.NO_EXT_KEY].total_bytes == 3

    def test_recurses_into_subdirectories(self, sample_dir: Path):
        stats = dirstat.collect_stats(str(sample_dir))
        assert stats[".py"].count == 2

    def test_empty_directory(self, tmp_path: Path):
        stats = dirstat.collect_stats(str(tmp_path))
        assert stats == {}

    def test_missing_path_raises_structured_error(self, tmp_path: Path):
        missing = tmp_path / "does-not-exist"
        with pytest.raises(dirstat.PathNotFoundError) as exc_info:
            dirstat.collect_stats(str(missing))
        assert exc_info.value.code == "path_not_found"
        assert exc_info.value.path == str(missing)

    def test_file_instead_of_directory_raises_structured_error(self, tmp_path: Path):
        file_path = tmp_path / "not-a-dir.txt"
        file_path.write_text("x")
        with pytest.raises(dirstat.NotADirectoryStatError) as exc_info:
            dirstat.collect_stats(str(file_path))
        assert exc_info.value.code == "not_a_directory"


class TestMainJsonOutput:
    def test_json_success_output(self, sample_dir: Path, capsys):
        exit_code = dirstat.main([str(sample_dir), "--json"])
        captured = capsys.readouterr()

        assert exit_code == 0
        payload = json.loads(captured.out)
        assert payload["success"] is True
        assert payload["data"][".txt"]["count"] == 2
        assert payload["data"][".txt"]["total_bytes"] == 7

    def test_json_error_output_no_traceback(self, tmp_path: Path, capsys):
        missing = tmp_path / "nope"
        exit_code = dirstat.main([str(missing), "--json"])
        captured = capsys.readouterr()

        assert exit_code == 1
        assert captured.out == ""  # nothing on stdout when it fails
        payload = json.loads(captured.err)
        assert payload["success"] is False
        assert payload["error"]["code"] == "path_not_found"
        assert "Traceback" not in captured.err

    def test_human_error_output_no_traceback(self, tmp_path: Path, capsys):
        missing = tmp_path / "nope"
        exit_code = dirstat.main([str(missing)])
        captured = capsys.readouterr()

        assert exit_code == 1
        assert captured.out == ""
        assert captured.err.startswith("Error:")
        assert "Traceback" not in captured.err


class TestCLISubprocess:
    def test_cli_invocation_json(self, sample_dir: Path):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "dirstat.py"), str(sample_dir), "--json"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["success"] is True
        assert payload["data"][".py"]["count"] == 2

    def test_cli_invocation_missing_dir_exit_code(self, tmp_path: Path):
        missing = tmp_path / "nope"
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "dirstat.py"), str(missing)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Traceback" not in result.stderr
        assert result.stdout == ""
