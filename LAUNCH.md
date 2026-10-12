# Launch notes

## v0.1.0 readiness

- Install from a fresh environment with `python -m pip install .[test]`.
- Run `python -m pytest -q`; all contract cases must pass without skips.
- From the repository root, run the complete, incomplete, and invalid examples. Expected exits are 0, 1, and 2 respectively. The adversarial example exits 1 and must not echo its ID.
- CI covers Ubuntu and Windows on Python 3.10 and 3.13.

The release is a local offline coverage checker. It has no network or model runtime dependency. Do not describe a coverage pass as a quality or provenance guarantee. A tagged public v0.1.0 release should be created only after the CI matrix passes.
