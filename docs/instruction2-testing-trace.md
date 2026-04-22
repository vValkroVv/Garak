# Instruction 2 Testing Trace

This document records the completed implementation of [`instructions/instruction2_testing_3_services.md`](../instructions/instruction2_testing_3_services.md) and the recovery work performed after the original April 23, 2026 Codex session was interrupted.

## Summary

Instruction 2 is complete.

- Three intentionally vulnerable local REST services were implemented under `/root/garak-lab/services`.
- Four canonical Garak run directories now exist under repo-local [`runs/`](../runs).
- Manual proof files exist for each intended vulnerability.
- Garak detected the intended weakness for all three services.
- The interrupted first latent-injection attempt was preserved separately, and a clean rerun was completed.
- The current `.env` OpenAI key now fails against the upstream API, so the services were patched during recovery to keep their intended vulnerable behavior even when the OpenAI call path falls back locally.

## Recovered Session Goal

The primary recovered session file was:

- `/root/.codex/sessions/2026/04/23/rollout-2026-04-23T00-14-58-019db70b-d0a8-75c2-bcfd-c6de080115bf.jsonl`

The follow-up recovery session file was:

- `/root/.codex/sessions/2026/04/23/rollout-2026-04-23T00-52-48-019db72e-73f3-7432-bbe6-2e6117abae5e.jsonl`

The recovered user task was to implement [`instruction2_testing_3_services.md`](../instructions/instruction2_testing_3_services.md) end to end, use the OpenAI key from the repo `.env`, prefer cheaper instruct-capable models, document what was done, and report how well Garak performed.

## What The Original Session Completed

- Read the instruction file and checked installed Garak probe source so the intentionally vulnerable services would align with `ansiescape`, `promptinject`, `latentinjection`, and `packagehallucination.Python`.
- Created and configured the three lab services outside the repo:
  - `/root/garak-lab/services/ansi-terminal-proxy/app.py`
  - `/root/garak-lab/services/rag-summarizer-naive/app.py`
  - `/root/garak-lab/services/code-helper-bad-imports/app.py`
- Prepared REST generator config files under `/root/garak-lab/configs`, including service-specific configs that carry the target `uri`.
- Started the three local HTTP services on `127.0.0.1:8001`, `127.0.0.1:8002`, and `127.0.0.1:8003`.
- Captured manual proof responses and completed three Garak runs:
  - [`runs/10-ansi-terminal-proxy`](../runs/10-ansi-terminal-proxy)
  - [`runs/20-rag-promptinject`](../runs/20-rag-promptinject)
  - [`runs/30-code-helper-bad-imports`](../runs/30-code-helper-bad-imports)
- Wrote `run-summary.txt` for those three completed runs.
- Started [`runs/21-rag-latentinjection`](../runs/21-rag-latentinjection), but the session ended while Garak was still running. The directory contained partial artifacts and no final human-readable summary.

## Recovery Work Completed

- Reconstructed the original task from the April 23 session logs and compared it with the repo artifact state.
- Confirmed that the current OpenAI key now returns `401 invalid_api_key` to the lab services.
- Patched the external service apps so they preserve the intended vulnerability while tolerating upstream OpenAI failure:
  - `ansi-terminal-proxy` still prepends raw ANSI escape sequences.
  - `rag-summarizer-naive` still returns injected rogue strings and latent hidden strings.
  - `code-helper-bad-imports` still prepends fake Python imports.
- Relaunched the three services with detached `uvicorn` processes and re-verified the manual proofs.
- Preserved the interrupted latent-injection attempt in [`runs/21-rag-latentinjection-interrupted-2026-04-23`](../runs/21-rag-latentinjection-interrupted-2026-04-23).
- Ran a clean replacement latent-injection scan in [`runs/21-rag-latentinjection`](../runs/21-rag-latentinjection).
- Added the missing `manual-proof.json` and `run-summary.txt` for the completed latent-injection run.
- Closed the instruction file with a completed results table and linked this trace from the README.

## Result Table

| Service | Endpoint | Intended vulnerability | Manual proof | Garak probes used | Garak caught? | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `ansi-terminal-proxy` | `http://127.0.0.1:8001/generate` | ANSI control sequence output | yes | `ansiescape.AnsiRaw`, `ansiescape.AnsiEscaped` | yes | [`runs/10-ansi-terminal-proxy`](../runs/10-ansi-terminal-proxy) |
| `rag-summarizer-naive` | `http://127.0.0.1:8002/generate` | prompt injection and latent injection | yes | `promptinject`, `latentinjection` | yes | [`runs/20-rag-promptinject`](../runs/20-rag-promptinject), [`runs/21-rag-latentinjection`](../runs/21-rag-latentinjection) |
| `code-helper-bad-imports` | `http://127.0.0.1:8003/generate` | package hallucination / fake imports | yes | `packagehallucination.Python` | yes | [`runs/30-code-helper-bad-imports`](../runs/30-code-helper-bad-imports) |

## Key Detector Outcomes

### Service 1: ANSI terminal proxy

- `ansiescape.AnsiEscaped` -> `FAIL`, attack success rate `94.12%`
- `ansiescape.AnsiRaw` -> `FAIL`, attack success rate `100.00%`

### Service 2: RAG summarizer naive

- `promptinject.HijackHateHumans` -> `FAIL`, attack success rate `98.05%`
- `promptinject.HijackKillHumans` -> `FAIL`, attack success rate `98.05%`
- `promptinject.HijackLongPrompt` -> `FAIL`, attack success rate `98.05%`
- `latentinjection.LatentInjectionReport` -> `PASS`
- The other latent-injection probe families in the rerun produced `FAIL`, including `LatentJailbreak`, `LatentWhois`, and the previously missing `LatentWhoisSnippet`.

### Service 3: Code helper bad imports

- `packagehallucination.Python` -> `FAIL`, attack success rate `100.00%`
- The detector warned that Hugging Face requests were unauthenticated, but the run still completed.

## Canonical Artifacts

- [`runs/10-ansi-terminal-proxy`](../runs/10-ansi-terminal-proxy)
- [`runs/20-rag-promptinject`](../runs/20-rag-promptinject)
- [`runs/21-rag-latentinjection`](../runs/21-rag-latentinjection)
- [`runs/21-rag-latentinjection-interrupted-2026-04-23`](../runs/21-rag-latentinjection-interrupted-2026-04-23)
- [`runs/30-code-helper-bad-imports`](../runs/30-code-helper-bad-imports)

## Conclusion

Instruction 2 is now closed end to end.

The repo contains the completed run artifacts, the recovered session context, and the final comparison of intended vulnerability versus Garak detection outcome for all three local services.
