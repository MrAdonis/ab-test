import json

import dirstat


def test_collect_stats_counts_and_bytes(tmp_path):
    (tmp_path / "a.txt").write_text("hello")  # 5 bytes
    (tmp_path / "b.txt").write_text("hi")  # 2 bytes
    (tmp_path / "c.py").write_text("x" * 10)  # 10 bytes
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.txt").write_text("y" * 3)  # 3 bytes, nested

    stats = dirstat.collect_stats(tmp_path)

    assert stats["txt"] == {"count": 3, "bytes": 5 + 2 + 3}
    assert stats["py"] == {"count": 1, "bytes": 10}


def test_collect_stats_groups_no_extension(tmp_path):
    (tmp_path / "README").write_text("no ext")

    stats = dirstat.collect_stats(tmp_path)

    assert stats[dirstat.NO_EXT_KEY] == {"count": 1, "bytes": len("no ext")}


def test_collect_stats_empty_directory(tmp_path):
    assert dirstat.collect_stats(tmp_path) == {}


def test_run_json_output(tmp_path):
    (tmp_path / "a.md").write_text("abc")

    code, out, err = dirstat.run([str(tmp_path), "--json"])

    assert code == 0
    assert err == ""
    payload = json.loads(out)
    assert payload == {"md": {"count": 1, "bytes": 3}}


def test_run_text_output(tmp_path):
    (tmp_path / "a.md").write_text("abc")

    code, out, err = dirstat.run([str(tmp_path)])

    assert code == 0
    assert "md" in out
    assert "1" in out


def test_run_missing_directory_json_is_structured(tmp_path):
    missing = tmp_path / "does-not-exist"

    code, out, err = dirstat.run([str(missing), "--json"])

    assert code == 1
    assert out == ""
    payload = json.loads(err)
    assert payload["error"] == "path_not_found"
    assert str(missing) in payload["message"]


def test_run_missing_directory_text_is_structured_not_traceback(tmp_path):
    missing = tmp_path / "does-not-exist"

    code, out, err = dirstat.run([str(missing)])

    assert code == 1
    assert "Traceback" not in err
    assert "Error:" in err


def test_run_path_is_a_file_not_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")

    code, out, err = dirstat.run([str(file_path), "--json"])

    assert code == 1
    payload = json.loads(err)
    assert payload["error"] == "not_a_directory"


def test_main_returns_exit_code(tmp_path, capsys):
    (tmp_path / "a.txt").write_text("abc")

    exit_code = dirstat.main([str(tmp_path), "--json"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"txt": {"count": 1, "bytes": 3}}
