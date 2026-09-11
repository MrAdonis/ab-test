import json

import pytest

import dirstat


def _make_files(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")  # 5 bytes
    (tmp_path / "b.txt").write_bytes(b"world!")  # 6 bytes
    (tmp_path / "c.py").write_bytes(b"print(1)")  # 8 bytes
    (tmp_path / "noext").write_bytes(b"xx")  # 2 bytes, no extension
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.py").write_bytes(b"x")  # 1 byte, nested
    return tmp_path


def test_collect_stats_counts_and_bytes(tmp_path):
    root = _make_files(tmp_path)
    stats = dirstat.collect_stats(root)

    assert stats[".txt"] == {"count": 2, "bytes": 11}
    assert stats[".py"] == {"count": 2, "bytes": 9}
    assert stats[dirstat.NO_EXT_KEY] == {"count": 1, "bytes": 2}


def test_collect_stats_recurses_into_subdirectories(tmp_path):
    root = _make_files(tmp_path)
    stats = dirstat.collect_stats(root)
    # d.py 在 sub/ 下，应被计入 .py 的合计里
    assert stats[".py"]["count"] == 2


def test_collect_stats_empty_directory(tmp_path):
    stats = dirstat.collect_stats(tmp_path)
    assert stats == {}


def test_collect_stats_extension_case_insensitive(tmp_path):
    (tmp_path / "a.TXT").write_bytes(b"abc")
    (tmp_path / "b.txt").write_bytes(b"de")
    stats = dirstat.collect_stats(tmp_path)
    assert stats[".txt"] == {"count": 2, "bytes": 5}


def test_collect_stats_missing_path_raises_structured_error(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(dirstat.PathNotFoundError) as exc_info:
        dirstat.collect_stats(missing)
    assert exc_info.value.error_type == "PathNotFoundError"
    assert str(missing) in exc_info.value.message


def test_collect_stats_path_is_file_not_dir_raises(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")
    with pytest.raises(dirstat.NotADirectoryDirstatError) as exc_info:
        dirstat.collect_stats(file_path)
    assert exc_info.value.error_type == "NotADirectoryError"


def test_main_json_output_success(tmp_path, capsys):
    _make_files(tmp_path)
    exit_code = dirstat.main([str(tmp_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["success"] is True
    assert payload["root"] == str(tmp_path)
    assert payload["total_files"] == 5
    assert payload["total_bytes"] == 22
    assert payload["stats"][".py"]["count"] == 2


def test_main_json_output_missing_dir_is_structured_not_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.err == ""  # 结构化错误走 stdout JSON，不是裸 traceback
    payload = json.loads(captured.out)
    assert payload["success"] is False
    assert payload["error"]["type"] == "PathNotFoundError"


def test_main_human_output_missing_dir_prints_to_stderr(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "错误" in captured.err
    assert str(missing) in captured.err


def test_main_human_output_readable_table(tmp_path, capsys):
    _make_files(tmp_path)
    exit_code = dirstat.main([str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "合计: 5 个文件, 22 字节" in captured.out


def test_main_path_is_file_returns_error(tmp_path, capsys):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")
    exit_code = dirstat.main([str(file_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["error"]["type"] == "NotADirectoryError"
