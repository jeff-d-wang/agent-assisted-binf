# Task 1 run audit

Status: **accepted**. This records the configured case analysis, not a course grade.

- Analyst: Claude via Messages API. Codex is not part of this runtime.
- Exact prompts, responses, model IDs, token usage: `api/`.
- User approvals, review notes, computations, tool requests and results: `events.jsonl` (UTC timestamps).
- Inputs, versions, coordinate-file agreement: `config.json`, `input_checks.json`.
- Methods and executed code: `code/`; no randomness in the scientific calculations.
- Database sources, versions and hashes: `data/provenance.json`; retrieved literature: `data/pubmed_*.json` and `.xml`.
- Computed evidence: `tables/`, `figures/`, `verification.json`; tool evidence is identified in `events.jsonl`.
- Independent checks: SIFTS vs alignment; Biopython vs PyMOL ligand distances. Two LLM opinions are not an independent check.
- Mechanistic inference and scientific weaknesses: Claude's draft/report plus the user's review notes. Unsupported claims remain unverified.
- Structural scope: one static input structure; no mutant modeling, activity/affinity experiments, conservation or ddG calculations.
- Final report is accepted only after explicit user review; file existence does not validate the biology.


## 2026-10-29: pre-deliverable documentation review

At the user's request, Codex checked saved artifacts and edited prose with the humanizer skill. The user was the human reviewer of the analysis agent's plan and outputs and accepted this run. This documentation pass is separate from that scientific review. Numerical checks passed; no live model call or production analysis was run. See DOCUMENTATION_UPDATE.md, the task HANDOFF.md and PRE_DELIVERABLE_REVIEW.md for checks, sources, corrections and limits. The original data, figures, tables, settings, code, API messages and acceptance time are unchanged.
