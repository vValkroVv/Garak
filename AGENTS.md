# NVIDIA Garak Testing Project

This repository is an NVIDIA Garak testing project.

## Purpose

- Keep a simple workspace for Garak-related testing and evaluation.
- Store lightweight notes, configs, and test assets as the project grows.

## Working Rules

- Keep the repository structure minimal unless expansion is necessary.
- Update `README.md` when adding commands, setup steps, or new workflows.
- Favor clear naming and short documentation for anything user-facing.
- Write Garak run artifacts into the repo-relative `runs/` directory under `Garak/runs`.
- When Garak is rerun, keep the canonical report files and console logs inside `Garak/runs` rather than external lab paths.
- Do not place every Garak artifact directly in `Garak/runs`.
- Create one subdirectory per Garak run, for example `Garak/runs/00-selftest/` or `Garak/runs/01-openai-smoke/`.
- Keep each run's `report.jsonl`, `report.html`, optional `hitlog.jsonl`, and `console.log` together inside that run-specific subdirectory.
