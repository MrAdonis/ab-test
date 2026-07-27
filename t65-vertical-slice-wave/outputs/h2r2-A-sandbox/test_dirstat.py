import json
from pathlib import Path

import pytest

import dirstat


def make_file(path: Path, content: bytes) -> None:
    path.write_bytes(content)


def test_collect_stats_counts_and_bytes(tmp_path):
    make_file(tmp_path / "a.txt", b"hello")
    make_file(tmp_path / "b.txt", b"world!")
    make_file(tmp_path / "c.py", b"print(1)")
    sub = tmp_path / "sub"
    sub.mkdir()
    make_file(sub / "d.txt", b"12")

    stats = dirstat.collect_stats(tmp_path)

    assert stats[".txt"]["count"] == 3
    assert stats[".txt"]["bytes"] == len(b"hello") + len(b"world!") + len(b"12")
    assert stats[".py"]["count"] == 1
    assert stats[".py"]["bytes"] == len(b"print(1)")


def test_collect_stats_no_extension(tmp_path):
    make_file(tmp_path / "README", b"data")
    stats = dirstat.collect_stats(tmp_path)
    assert stats["<no extension>"]["count"] == 1
    assert stats["<no extension>"]["bytes"] == 4


def test_collect_stats_empty_dir(tmp_path):
    assert dirstat.collect_stats(tmp_path) == {}


def test_collect_stats_sorted_by_bytes_desc(tmp_path):
    make_file(tmp_path / "small.txt", b"x")
    make_file(tmp_path / "big.log", b"x" * 100)
    stats = dirstat.collect_stats(tmp_path)
    assert list(stats.keys()) == [".log", ".txt"]


def test_collect_stats_missing_dir_raises(tmp_path):
    missing = tmp_path / "nope"
    with pytest.raises(dirstat.DirStatError) as exc_info:
        dirstat.collect_stats(missing)
    assert exc_info.value.code == "not_found"


def test_collect_stats_not_a_directory_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    make_file(file_path, b"x")
    with pytest.raises(dirstat.DirStatError) as exc_info:
        dirstat.collect_stats(file_path)
    assert exc_info.value.code == "not_a_directory"


def test_main_json_output(tmp_path, capsys):
    make_file(tmp_path / "a.txt", b"hello")
    exit_code = dirstat.main([str(tmp_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload[".txt"]["count"] == 1
    assert payload[".txt"]["bytes"] == 5


def test_main_table_output(tmp_path, capsys):
    make_file(tmp_path / "a.txt", b"hello")
    exit_code = dirstat.main([str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert ".txt" in captured.out
    assert "TOTAL" in captured.out


def test_main_missing_dir_json_error_no_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    payload = json.loads(captured.err)
    assert payload["error"] == "not_found"


def test_main_missing_dir_text_error_no_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Traceback" not in captured.err
    assert "not_found" in captured.err


def test_main_not_a_directory_error(tmp_path, capsys):
    file_path = tmp_path / "file.txt"
    make_file(file_path, b"x")
    exit_code = dirstat.main([str(file_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.err)
    assert payload["error"] == "not_a_directory"
