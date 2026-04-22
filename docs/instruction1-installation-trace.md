# Instruction 1 Installation Trace

This document records the end-to-end implementation of [`instructions/instruction1_installation_garak.md`](../instructions/instruction1_installation_garak.md).

## Summary

Instruction 1 is complete.

- Garak was installed into an isolated virtual environment at `/root/venvs/garak-lab`.
- The lab working directories were created under `/root/garak-lab`.
- The OpenAI API key was loaded from [`Garak/.env`](../.env) without copying the secret into repo files.
- Garak CLI verification succeeded.
- The required Garak self-test succeeded.
- The required OpenAI smoke run against `gpt-5.2` succeeded.
- A small extra local-only verification run was added to generate a real hitlog artifact, because the required clean runs did not create one.
- On April 23, 2026, the run artifacts were moved into repo-relative storage and the runs were repeated with outputs written directly under [`runs/`](../runs).

## Artifact Location Update

The initial instruction implementation wrote Garak report artifacts under `/root/garak-lab/runs`.

Per repository preference, the canonical location was then changed to the repo-relative directory:

- [`runs/`](../runs)

What changed:

- Existing artifacts were copied from `/root/garak-lab/runs` into `Garak/runs`
- The Garak runs were repeated with `--report_prefix` values pointing directly at `/root/workspace/Garak/runs/...`
- Console output for each rerun was also saved in `Garak/runs` as `*.console.log`

Current canonical run files:

- [`runs/00-selftest.report.jsonl`](../runs/00-selftest.report.jsonl)
- [`runs/00-selftest.report.html`](../runs/00-selftest.report.html)
- [`runs/00-selftest.console.log`](../runs/00-selftest.console.log)
- [`runs/00a-hitlog-check.report.jsonl`](../runs/00a-hitlog-check.report.jsonl)
- [`runs/00a-hitlog-check.report.html`](../runs/00a-hitlog-check.report.html)
- [`runs/00a-hitlog-check.hitlog.jsonl`](../runs/00a-hitlog-check.hitlog.jsonl)
- [`runs/00a-hitlog-check.console.log`](../runs/00a-hitlog-check.console.log)
- [`runs/01-openai-smoke.report.jsonl`](../runs/01-openai-smoke.report.jsonl)
- [`runs/01-openai-smoke.report.html`](../runs/01-openai-smoke.report.html)
- [`runs/01-openai-smoke.console.log`](../runs/01-openai-smoke.console.log)

## What Was Done

### 1. Created the lab directories

Created:

- `/root/garak-lab/services`
- `/root/garak-lab/configs`
- `/root/garak-lab/runs`
- `/root/garak-lab/logs`
- `/root/garak-lab/review`
- `/root/venvs`

### 2. Fixed the system prerequisite for `venv`

The first `python3 -m venv` attempt failed because the host was missing `python3.12-venv`.

Installed:

- `python3.12-venv` via `apt-get install -y python3.12-venv`

### 3. Created the Python environment

Created the dedicated environment:

- `/root/venvs/garak-lab`

Verified:

- `python --version` -> `Python 3.12.3`
- `which python` -> `/root/venvs/garak-lab/bin/python`
- `pip --version` -> `pip 26.0.1`

### 4. Installed Garak and supporting packages

Installed with:

```bash
python -m pip install -U garak fastapi "uvicorn[standard]" openai
```

Relevant installed versions:

- `garak 0.14.1`
- `openai 2.32.0`
- `fastapi 0.136.0`
- `uvicorn 0.45.0`

Note:

- Garak's current dependency graph on this host pulled a large `torch` stack, including CUDA-related packages. Installation still completed successfully.

### 5. Loaded the OpenAI key from `.env`

Source file:

- [`Garak/.env`](../.env)

The key was read at runtime and exported to `OPENAI_API_KEY` for commands that needed it. The secret value was not written into any docs or repo files.

### 6. Verified model access before the Garak smoke run

A minimal OpenAI Responses API check was executed and succeeded with:

- `SELECTED_MODEL=gpt-5.2`
- `OUTPUT=OK`

Execution log:

- `/root/garak-lab/logs/openai-model-check.log`

## Garak CLI Verification

Commands completed successfully:

- `python -m garak --version`
- `python -m garak --help`
- `python -m garak --list_generators`
- `python -m garak --list_detectors`
- `python -m garak --list_probes -v`

Observed version:

- `garak LLM vulnerability scanner v0.14.1`

Saved review files:

- `/root/garak-lab/review/garak-help.txt`
- `/root/garak-lab/review/garak-generators.txt`
- `/root/garak-lab/review/garak-detectors.txt`
- `/root/garak-lab/review/garak-probes.txt`

Inventory counts captured during setup:

- Generators: `63`
- Detectors: `137`
- Probes: `222`

## Run Results

### Required run 1: Garak self-test

Command intent:

- `test.Blank` generator
- `test.Test` probe
- report prefix `/root/workspace/Garak/runs/00-selftest`

Result:

- Completed successfully
- Final line: `garak run complete in 0.76s`
- Probe summary: `always.Pass: PASS ok on 40/40`

Artifacts:

- `/root/workspace/Garak/runs/00-selftest.report.jsonl`
- `/root/workspace/Garak/runs/00-selftest.report.html`
- `/root/workspace/Garak/runs/00-selftest.console.log`

Execution log:

- `/root/workspace/Garak/runs/00-selftest.console.log`

### Required run 2: OpenAI smoke run

Command intent:

- target type `openai`
- target name `gpt-5.2`
- probe `ansiescape.AnsiEscaped`
- `--generations 1`
- report prefix `/root/workspace/Garak/runs/01-openai-smoke`

Result:

- Completed successfully
- Final line: `garak run complete in 12.27s`
- OpenAI generator loaded successfully: `OpenAI: gpt-5.2`
- No authentication error
- No model lookup error
- Detector summary: `ansiescape.Escaped: SKIP ok on 0/0`

Artifacts:

- `/root/workspace/Garak/runs/01-openai-smoke.report.jsonl`
- `/root/workspace/Garak/runs/01-openai-smoke.report.html`
- `/root/workspace/Garak/runs/01-openai-smoke.console.log`

Execution log:

- `/root/workspace/Garak/runs/01-openai-smoke.console.log`

### Extra verification run: explicit hitlog creation

Why this was added:

- The two required runs were successful but did not produce a `.hitlog.jsonl`.
- Inspection of the installed Garak source showed that the hitlog file is created lazily only when Garak records failing detector results.
- To verify hitlog generation end to end, a tiny local-only run was added with `always.Fail`.

Run setup:

- generator `test.Blank`
- probe `test.Test`
- detector `always.Fail`
- report prefix `/root/workspace/Garak/runs/00a-hitlog-check`

Result:

- Completed successfully
- Summary: `always.Fail: FAIL ok on 0/8 (attack success rate: 100.00%)`

Artifacts:

- `/root/workspace/Garak/runs/00a-hitlog-check.report.jsonl`
- `/root/workspace/Garak/runs/00a-hitlog-check.report.html`
- `/root/workspace/Garak/runs/00a-hitlog-check.hitlog.jsonl`
- `/root/workspace/Garak/runs/00a-hitlog-check.console.log`

Execution log:

- `/root/workspace/Garak/runs/00a-hitlog-check.console.log`

## Final Artifact Inventory

Files now present in `/root/workspace/Garak/runs`:

- `00-selftest.report.jsonl`
- `00-selftest.report.html`
- `00-selftest.console.log`
- `00a-hitlog-check.report.jsonl`
- `00a-hitlog-check.report.html`
- `00a-hitlog-check.hitlog.jsonl`
- `00a-hitlog-check.console.log`
- `01-openai-smoke.report.jsonl`
- `01-openai-smoke.report.html`
- `01-openai-smoke.console.log`

## Important Observation

For this installed Garak version, a hitlog is not created for a clean pass or a skipped detector path. It is created when there are failing detector results. This explains why the required self-test and smoke run produced JSONL and HTML but not a hitlog, while the extra `always.Fail` verification run did.

## Conclusion

Instruction 1 is implemented end to end.

The environment is ready for the next stages:

- the venv is working
- Garak CLI is working
- OpenAI access is working with `gpt-5.2`
- required review files were saved
- required self-test passed
- required OpenAI smoke run passed
- the lab now also contains a verified `.hitlog.jsonl` example for later analysis
