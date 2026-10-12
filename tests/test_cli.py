import json
import subprocess
import sys

import pytest

from eval_run_coverage.cli import InvalidInput, coverage, main


def write(path, raw):
    path.write_bytes(raw)
    return str(path)


def test_complete_and_empty():
    assert coverage(["a", "b"], ["b", "a"])["status"] == "complete"
    assert coverage([], []) == {
        "status": "complete", "expected_count": 0, "result_count": 0,
        "missing_expected_lines": [], "unknown_result_lines": [],
        "duplicate_result_lines": [],
    }


def test_missing_unknown_and_duplicate_groups_are_line_numbered():
    report = coverage(["a", "b"], ["a", "x", "x", "a"])
    assert report == {
        "status": "incomplete", "expected_count": 2, "result_count": 4,
        "missing_expected_lines": [2], "unknown_result_lines": [2, 3],
        "duplicate_result_lines": [[1, 4], [2, 3]],
    }


def test_duplicate_expected_is_invalid():
    with pytest.raises(InvalidInput):
        coverage(["a", "a"], [])


@pytest.mark.parametrize("newline", [b"\n", b"\r", b"\r\n"])
def test_newline_forms_and_unicode_exact_equality(tmp_path, newline):
    expected = write(tmp_path / "expected", '{"id":"é"}'.encode() + newline)
    results = write(tmp_path / "results", '{"id":"é"}'.encode())
    assert main([expected, results]) == 1


@pytest.mark.parametrize("raw", [
    b"\n", b"{}\n", b'{"id":""}\n', b'{"id":1}\n',
    b'{"id":"x","id":"y"}\n', b'{"id":"x"}\n\n',
    b'{"id":"x"}\nnot-json', b'{"id":NaN}\n', b'{"id":Infinity}\n',
    b'{"id":"x","extra":true}\n', b'\xff',
])
def test_invalid_content(raw, tmp_path, capsys):
    expected = write(tmp_path / "expected", b'{"id":"x"}')
    results = write(tmp_path / "results", raw)
    assert main([expected, results]) == 2
    captured = capsys.readouterr()
    assert captured.out == '{"status":"invalid_input"}\n'
    assert captured.err == ""


def test_cli_validates_suffix_without_emitting_partial_report(tmp_path, capsys):
    expected = write(tmp_path / "expected", b'{"id":"x"}')
    results = write(tmp_path / "results", b'{"id":"x"}\n{broken')
    assert main([expected, results]) == 2
    assert capsys.readouterr().out == '{"status":"invalid_input"}\n'


def test_misuse_does_not_echo_paths_or_write_stderr(capsys):
    assert main(["secret-expected-path"]) == 2
    captured = capsys.readouterr()
    assert captured.out == '{"status":"invalid_input"}\n'
    assert captured.err == ""
    assert "secret" not in captured.out


def test_module_cli_does_not_echo_ids_paths_or_source(tmp_path):
    expected = write(tmp_path / "private_expected_name", b'{"id":"TOP-SECRET-ID"}')
    results = write(tmp_path / "private_results_name", b'{"id":"OTHER-SECRET-ID"}')
    proc = subprocess.run(
        [sys.executable, "-m", "eval_run_coverage.cli", expected, results],
        capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["status"] == "incomplete"
    assert proc.stderr == ""
    assert all(secret not in proc.stdout for secret in ["TOP-SECRET", "OTHER-SECRET", "private_"])


def test_missing_file_is_invalid_without_echo(tmp_path, capsys):
    assert main([str(tmp_path / "sensitive-name"), str(tmp_path / "also-sensitive")]) == 2
    captured = capsys.readouterr()
    assert captured.out == '{"status":"invalid_input"}\n'
    assert captured.err == ""


def test_help(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])
    assert exit_info.value.code == 0
    assert "usage:" in capsys.readouterr().out.lower()
