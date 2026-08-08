import json

import pytest

import dirstat
from dirstat import DirStatError, collect_stats, format_human, main


# ---- collect_stats: error paths ----------------------------------------

def test_nonexistent_path_raises_structured_error(tmp_path):
    missing = tmp_path / "does_not_exist"
    with pytest.raises(DirStatError) as exc_info:
        collect_stats(missing)
    assert exc_info.value.error_type == "path_not_found"
    assert str(missing) in exc_info.value.message


def test_path_is_file_not_directory_raises_structured_error(tmp_path):
    file_path = tmp_path / "a_file.txt"
    file_path.write_text("hello")
    with pytest.raises(DirStatError) as exc_info:
        collect_stats(file_path)
    assert exc_info.value.error_type == "not_a_directory"


# ---- collect_stats: aggregation -----------------------------------------

def test_empty_directory_has_zero_totals(tmp_path):
    stats = collect_stats(tmp_path)
    assert stats["extensions"] == {}
    assert stats["total_files"] == 0
    assert stats["total_bytes"] == 0


def test_counts_and_bytes_grouped_by_extension(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"1234567890")  # 10 bytes
    (tmp_path / "b.txt").write_bytes(b"12345")  # 5 bytes
    (tmp_path / "c.py").write_bytes(b"123")  # 3 bytes

    stats = collect_stats(tmp_path)

    assert stats["extensions"][".txt"] == {"count": 2, "bytes": 15}
    assert stats["extensions"][".py"] == {"count": 1, "bytes": 3}
    assert stats["total_files"] == 3
    assert stats["total_bytes"] == 18


def test_files_without_extension_are_grouped_together(tmp_path):
    (tmp_path / "Makefile").write_bytes(b"abc")
    (tmp_path / "README").write_bytes(b"de")

    stats = collect_stats(tmp_path)

    assert stats["extensions"]["<no ext>"] == {"count": 2, "bytes": 5}


def test_extension_matching_is_case_insensitive(tmp_path):
    (tmp_path / "a.PY").write_bytes(b"12")
    (tmp_path / "b.py").write_bytes(b"345")

    stats = collect_stats(tmp_path)

    assert stats["extensions"][".py"] == {"count": 2, "bytes": 5}
    assert ".PY" not in stats["extensions"]


def test_recurses_into_subdirectories(tmp_path):
    nested = tmp_path / "sub" / "deeper"
    nested.mkdir(parents=True)
    (tmp_path / "top.txt").write_bytes(b"1")
    (nested / "bottom.txt").write_bytes(b"22")

    stats = collect_stats(tmp_path)

    assert stats["extensions"][".txt"] == {"count": 2, "bytes": 3}
    assert stats["total_files"] == 2


# ---- format_human ---------------------------------------------------------

def test_format_human_reports_no_files_found(tmp_path):
    stats = collect_stats(tmp_path)
    output = format_human(stats)
    assert "no files found" in output


def test_format_human_includes_extension_and_total(tmp_path):
    (tmp_path / "a.log").write_bytes(b"12345")
    stats = collect_stats(tmp_path)
    output = format_human(stats)
    assert ".log" in output
    assert "Total: 1 files, 5 bytes" in output


# ---- CLI: main() ------------------------------------------------------

def test_cli_json_success_has_unified_schema(tmp_path, capsys):
    (tmp_path / "a.txt").write_bytes(b"12345")

    exit_code = main([str(tmp_path), "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["success"] is True
    assert payload["data"]["total_files"] == 1
    assert payload["data"]["extensions"][".txt"]["bytes"] == 5


def test_cli_json_error_for_missing_path_has_no_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"

    exit_code = main([str(missing), "--json"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Traceback" not in captured.out
    assert "Traceback" not in captured.err
    payload = json.loads(captured.out)
    assert payload["success"] is False
    assert payload["error"]["type"] == "path_not_found"


def test_cli_non_json_error_goes_to_stderr_without_traceback(tmp_path, capsys):
    missing = tmp_path / "nope"

    exit_code = main([str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Traceback" not in captured.err
    assert "does not exist" in captured.err


def test_cli_non_json_success_prints_human_table(tmp_path, capsys):
    (tmp_path / "a.txt").write_bytes(b"12345")

    exit_code = main([str(tmp_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert ".txt" in captured.out
    assert "Total: 1 files, 5 bytes" in captured.out


def test_help_does_not_crash(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    assert "--json" in capsys.readouterr().out
