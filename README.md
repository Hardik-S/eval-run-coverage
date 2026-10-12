# Eval Run Coverage

`eval-run-coverage` checks whether a JSONL result file contains exactly one result for every expected case ID, without unknown IDs. It is a small offline Python CLI with no runtime dependencies.

## Install and run

Python 3.10 or newer is required.

```console
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install .[test]
eval-run-coverage examples/complete/expected.jsonl examples/complete/results.jsonl
```

The complete example exits 0. To see a coverage failure, run:

```console
eval-run-coverage examples/incomplete/expected.jsonl examples/incomplete/results.jsonl
```

It prints a JSON report and exits 1. Invalid input or command usage prints only `{"status":"invalid_input"}` and exits 2. Try the invalid fixture with:

```console
eval-run-coverage examples/invalid/expected.jsonl examples/invalid/results.jsonl
```

The `examples/adversarial` fixture also exits 1; its private-looking ID is deliberately never printed.

## Input and output

Each UTF-8 JSONL record must be exactly an object with one nonempty string field named `id`. Expected IDs must be unique. Results may repeat or include unknown IDs; both are coverage failures. IDs are compared exactly, with no Unicode normalization. LF, CRLF, and CR line endings are accepted. Empty files are valid.

The report contains status, input counts, missing expected line numbers, unknown result line numbers, and groups of duplicate result line numbers. It never includes IDs, paths, or input text. Both files are fully validated before a report is emitted. Input memory use grows with file size.

This tool measures identifier coverage only. It does not assess result quality, score model outputs, interpret repeated trials, or make claims about data provenance. Normalize IDs before supplying inputs if a different comparison policy is needed.

Run tests with `python -m pytest`.
