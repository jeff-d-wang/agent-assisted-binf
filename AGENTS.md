# AGENTS.md

Course assignment: AI-agent-assisted analysis of three bioinformatics tasks (protein mutations, PBMC3k single-cell, Visium mouse-brain spatial). `PROJECT_PLAN.md` is the source of truth for steps and checkpoints; `RUBRIC.md` is the scoring sheet.

## Layout

- `datasets/` holds raw inputs only. Never modify them; extract with the tar commands in `PROJECT_PLAN.md`.
- `protein/`, `single_cell/`, `spatial/`: one folder per task, holding that task's code, outputs, and `AGENT_LOG.md`.
- Scripts are numbered in run order (`01_qc.py`, `02_cluster.py`, ...) so the README can list them in sequence.
- Outputs go in `<task>/figures/` and `<task>/tables/`. Every figure or table must come from a script in the repo.

## Working rules

- Work on one task at a time. Don't start analysis until asked.
- Claude is the Task 1 scientific analysis agent via the standalone Python program. Codex develops and maintains code; it is not a runtime analyst or intermediary. Preserve the attribution of historical work.
- Laptop only: no GPU, no model training.
- Set a seed for anything random, write it in the script, and log it.
- Always keep three things separate: **what the data showed**, **what the agent inferred**, and **what external evidence supports**.
- Keep uncertain labels and negative results. Don't round them up into conclusions.
- Never commit API keys, tokens, or large derived files (`.h5ad`, caches).

## AGENT_LOG.md (one per task)

Add a dated entry for each meaningful step. Each entry covers:
- Prompt or question given to the analysis agent (Claude for the new Task 1 workflow) and a short summary of its answer; attribute Codex software-development work separately
- Resources used: datasets, databases, packages + versions, papers, URLs
- Computed vs retrieved: whether each result was calculated here or looked up
- Settings: seeds, parameters, thresholds, input file names, filtering decisions
- Checks: what was independently verified and what came out
- Agent weaknesses: wrong, unsupported, or questionable output, and how it was handled

This log feeds the Agent Audit (Section 7) and the rubric evidence column.

## Checkpoints

Mark a checkpoint `[x]` in `PROJECT_PLAN.md` only when both the result and the code behind it are in the repo. After each task, fill in Status / Evidence / Score in `RUBRIC.md`.

## Environment

`pip install -r requirements.txt`. Record exact versions with `pip freeze > requirements.lock.txt` before the final report.
