# NVIDIA Garak Testing Project

Small repository for testing and documenting work around NVIDIA Garak.

## Status

Instruction 1 setup is complete as of April 22-23, 2026.
Instruction 2 three-service testing is complete as of April 23, 2026.

## Environment

The Garak lab environment created for this project lives outside the repo:

- `/root/venvs/garak-lab` for the dedicated Python virtual environment
- `/root/garak-lab` for supporting lab directories such as review output, logs, and future configs

The canonical Garak run outputs for this repository now live inside the repo:

- `/root/workspace/Garak/runs` for run-specific subdirectories

Each Garak run should have its own subfolder inside `runs/`, with that run's report JSONL, HTML summary, optional hitlog, and console log stored together.

## Documentation

- [Instruction 1 installation trace](./docs/instruction1-installation-trace.md)
- [Instruction 2 testing trace](./docs/instruction2-testing-trace.md)

## Generated Review Files

The installation stage wrote the following inventory files under `/root/garak-lab/review`:

- `garak-help.txt`
- `garak-generators.txt`
- `garak-detectors.txt`
- `garak-probes.txt`

## Run Artifacts

The current Garak execution artifacts are stored in repo-relative form under `runs/`, split by run:

- `runs/00-selftest/`
- `runs/00a-hitlog-check/`
- `runs/01-openai-smoke/`
- `runs/10-ansi-terminal-proxy/`
- `runs/20-rag-promptinject/`
- `runs/21-rag-latentinjection/`
- `runs/21-rag-latentinjection-interrupted-2026-04-23/`
- `runs/30-code-helper-bad-imports/`
