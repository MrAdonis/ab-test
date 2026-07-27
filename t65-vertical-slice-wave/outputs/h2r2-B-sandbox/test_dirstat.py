import json

import pytest

import dirstat


@pytest.fixture
def sample_dir(tmp_path):
    (tmp_path / "a.txt").write_text("hello")  # 5 bytes
    (tmp_path / "b.txt").write_text("hi")  # 2 bytes
    (tmp_path / "c.py").write_text("print(1)\n")  # 9 bytes
    (tmp_path / "noext").write_text("x")  # 1 byte, no extension

    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.py").write_text("pass\n")  # 5 bytes

    return tmp_path


def test_collect_stats_counts_and_bytes(sample_dir):
    stats = dirstat.collect_stats(sample_dir)

    assert stats[".txt"].count == 2
    assert stats[".txt"].bytes == 7
    assert stats[".py"].count == 2  # recursive: c.py + sub/d.py
    assert stats[".py"].bytes == 14
    assert stats[""].count == 1
    assert stats[""].bytes == 1


def test_collect_stats_missing_dir_raises_structured_error(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(dirstat.DirStatError) as exc_info:
        dirstat.collect_stats(missing)

    err = exc_info.value
    assert err.code == "path_not_found"
    assert err.to_dict()["error"] == "path_not_found"
    assert str(missing) in err.to_dict()["message"]


def test_collect_stats_path_is_file_raises_structured_error(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hi")
    with pytest.raises(dirstat.DirStatError) as exc_info:
        dirstat.collect_stats(f)

    assert exc_info.value.code == "not_a_directory"


def test_format_json_is_valid_and_sorted(sample_dir):
    stats = dirstat.collect_stats(sample_dir)
    out = dirstat.format_json(stats, str(sample_dir))
    data = json.loads(out)

    assert data["path"] == str(sample_dir)
    assert data["total_files"] == 5
    assert data["total_bytes"] == 22

    byte_counts = [row["bytes"] for row in data["extensions"]]
    assert byte_counts == sorted(byte_counts, reverse=True)


def test_main_json_success_exit_code(sample_dir, capsys):
    exit_code = dirstat.main([str(sample_dir), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["total_files"] == 5


def test_main_table_output_exit_code(sample_dir, capsys):
    exit_code = dirstat.main([str(sample_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "TOTAL" in captured.out


def test_main_missing_dir_no_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Traceback" not in captured.err
    assert "Error:" in captured.err


def test_main_missing_dir_json_error_is_structured(tmp_path, capsys):
    missing = tmp_path / "nope"
    exit_code = dirstat.main([str(missing), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Traceback" not in captured.err
    err = json.loads(captured.err)
    assert err["error"] == "path_not_found"
    assert "message" in err
