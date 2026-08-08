import json

import pytest

from dirstat import DirStatError, collect_stats, main


@pytest.fixture
def sample_dir(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    (tmp_path / "b.txt").write_text("world!")
    (tmp_path / "c.py").write_text("print(1)")
    (tmp_path / "noext").write_text("x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.txt").write_text("nested")
    return tmp_path


def test_collect_stats_counts_and_bytes(sample_dir):
    stats = collect_stats(sample_dir)

    assert stats[".txt"]["count"] == 3
    assert stats[".txt"]["bytes"] == len("hello") + len("world!") + len("nested")
    assert stats[".py"]["count"] == 1
    assert stats[".py"]["bytes"] == len("print(1)")


def test_collect_stats_no_extension(sample_dir):
    stats = collect_stats(sample_dir)

    assert stats["<no ext>"]["count"] == 1
    assert stats["<no ext>"]["bytes"] == len("x")


def test_collect_stats_recurses_into_subdirs(sample_dir):
    stats = collect_stats(sample_dir)

    # d.txt lives in sub/ and must be counted alongside top-level .txt files
    assert stats[".txt"]["count"] == 3


def test_collect_stats_empty_dir(tmp_path):
    assert collect_stats(tmp_path) == {}


def test_collect_stats_nonexistent_path_raises(tmp_path):
    missing = tmp_path / "does-not-exist"

    with pytest.raises(DirStatError) as exc_info:
        collect_stats(missing)

    assert exc_info.value.code == "path_not_found"


def test_collect_stats_path_is_a_file_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")

    with pytest.raises(DirStatError) as exc_info:
        collect_stats(file_path)

    assert exc_info.value.code == "not_a_directory"


def test_cli_json_success(sample_dir, capsys):
    exit_code = main([str(sample_dir), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["success"] is True
    assert payload["data"][".txt"]["count"] == 3


def test_cli_table_output(sample_dir, capsys):
    exit_code = main([str(sample_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert ".txt" in captured.out
    assert "extension" in captured.out


def test_cli_json_error_on_missing_dir(tmp_path, capsys):
    missing = tmp_path / "does-not-exist"
    exit_code = main([str(missing), "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 1
    assert payload["success"] is False
    assert payload["error"]["code"] == "path_not_found"


def test_cli_no_traceback_on_missing_dir_without_json(tmp_path, capsys):
    missing = tmp_path / "does-not-exist"
    exit_code = main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "Traceback" not in captured.err
    assert "error:" in captured.err
