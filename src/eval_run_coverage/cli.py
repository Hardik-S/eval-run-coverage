"""Command line interface for checking JSONL evaluation coverage."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


class InvalidInput(Exception):
    """An input file is not valid under the public JSONL contract."""


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput
        result[key] = value
    return result


def _reject_constant(_value):
    raise InvalidInput


def _read_ids(path):
    try:
        content = Path(path).read_bytes().decode("utf-8", errors="strict")
    except (OSError, UnicodeError):
        raise InvalidInput from None
    if content == "":
        return []
    lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines[-1] == "":
        lines.pop()
    ids = []
    for line in lines:
        if not line:
            raise InvalidInput
        try:
            value = json.loads(
                line,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
        except (ValueError, TypeError, RecursionError):
            raise InvalidInput from None
        if type(value) is not dict or set(value) != {"id"}:
            raise InvalidInput
        item = value["id"]
        if type(item) is not str or item == "":
            raise InvalidInput
        ids.append(item)
    return ids


def coverage(expected, results):
    """Return the contract's coverage fields without exposing identifiers."""
    if len(set(expected)) != len(expected):
        raise InvalidInput
    expected_lines = {item: line for line, item in enumerate(expected, 1)}
    result_lines = defaultdict(list)
    for line, item in enumerate(results, 1):
        result_lines[item].append(line)
    missing = sorted(
        line for item, line in expected_lines.items() if item not in result_lines
    )
    unknown = sorted(
        line for item, lines in result_lines.items() if item not in expected_lines
        for line in lines
    )
    duplicates = sorted(
        (lines for lines in result_lines.values() if len(lines) >= 2),
        key=lambda lines: lines[0],
    )
    complete = not missing and not unknown and not duplicates
    return {
        "status": "complete" if complete else "incomplete",
        "expected_count": len(expected),
        "result_count": len(results),
        "missing_expected_lines": missing,
        "unknown_result_lines": unknown,
        "duplicate_result_lines": duplicates,
    }


class _Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise InvalidInput


def main(argv=None):
    parser = _Parser(prog="eval-run-coverage", add_help=True)
    parser.add_argument("expected")
    parser.add_argument("results")
    try:
        args = parser.parse_args(argv)
        expected = _read_ids(args.expected)
        results = _read_ids(args.results)
        report = coverage(expected, results)
        print(json.dumps(report, separators=(",", ":"), ensure_ascii=True))
        return 0 if report["status"] == "complete" else 1
    except InvalidInput:
        print('{"status":"invalid_input"}')
        return 2


if __name__ == "__main__":
    sys.exit(main())
