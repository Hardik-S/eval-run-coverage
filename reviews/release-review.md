# Independent release review — issue #3

**Verdict: PASS** for the frozen contract on PR #2 head `e9995d2bc28e4e2659a9cbdf2bfea7c7851d5c9c` (reviewed 2026-10-12). This is an independent contract review; no merge, tag, or release was performed.

## Reviewed artifact identity

| Artifact | SHA-256 |
| --- | --- |
| `CONTRACT.md` | `C4C751572F7AA94E2E2CAF2FD7A8B324F6BD17F189C5078EB1E2D3E45F1171F0` |
| `src/eval_run_coverage/cli.py` | `0F68857DDFF436E73CF943C2A009D60DDDFC66D44C7AA8EC15F6226432686741` |
| `README.md` | `F1B6BC2A2E1AF7AEDC984F25770A36DDABDB1E975EDB46B7BD6ECFB546654665` |
| `LAUNCH.md` | `2402FEBF212A1AFF4BF3C486262CCC100DC00184421DD32340106FF6AD7796A8` |
| `.github/workflows/ci.yml` | `3DAB810B0E7804FF3AEE4C23345C574230916B47DA012ABC71B080F86EF26052` |

## Commands and evidence

The install/test source was a clean `git archive` export of the reviewed SHA, with its venv outside the checkout:

```powershell
git archive HEAD | tar -x -C <temp>\src
py -3.13 -m venv <temp>\venv
Push-Location <temp>\src
<temp>\venv\Scripts\python.exe -m pip install ".[test]"
<temp>\venv\Scripts\python.exe -m pytest -q <temp>\src\tests
```

Install succeeded on Windows Python 3.13.1. Pytest reported **22 passed**, with no skips. The installed console entry point produced the documented results:

| Fixture | Exit | Result |
| --- | ---: | --- |
| `examples/complete` | 0 | `complete` |
| `examples/incomplete` | 1 | `incomplete` |
| `examples/invalid` | 2 | exactly `{"status":"invalid_input"}` |
| `examples/adversarial` | 1 | `incomplete`; private-looking ID absent from output |

Installed-entry-point probes also passed: duplicate expected IDs, duplicate JSON keys, `NaN`, malformed trailing JSON, and missing-argument misuse returned exit 2 with only the invalid-input object and no stderr. Duplicate and unknown result IDs returned exit 1 with unknown lines `[2,3]` and duplicate groups `[[1,4],[2,3]]`, in the required order. CR, LF, and CRLF handling and composed-versus-decomposed Unicode behavior passed the installed package tests; an installed probe confirmed the distinct Unicode strings remain distinct.

The bundled README and launch notes accurately describe the tested fixture exits, offline/no-runtime-dependency scope, identifier-only coverage meaning, no-echo invalid output, and the four-job CI matrix. No scoring or provenance claims were found.

GitHub Actions at the reviewed SHA passed all four jobs in both runs:

- PR run `38253316442`: Ubuntu and Windows, Python 3.10 and 3.13 — all success.
- Push run `38253313310`: Ubuntu and Windows, Python 3.10 and 3.13 — all success.

## Limits

Direct local execution was on Windows/Python 3.13.1; Linux and Python 3.10 evidence is from the successful GitHub Actions matrix. `gh pr checks --required` reported that no required checks are configured for the branch, although both observed CI runs completed successfully. This review does not certify a tagged release artifact because release creation is outside this review's authorized scope.