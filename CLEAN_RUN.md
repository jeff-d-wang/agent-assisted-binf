# Clean runs, human review and final submission

Updated 2026-10-29. All three submission runs are accepted. The user reviewed the
analysis agents' plans and outputs, sent feedback, checked evidence and accepted the
reports. Sonnet analyzed Tasks 1 and 2; Haiku analyzed Task 3 for budget reasons.
Codex developed the software and edited documentation.

Start with [PRE_DELIVERABLE_REVIEW.md](PRE_DELIVERABLE_REVIEW.md) and each task's
`HANDOFF.md`. No new live run is needed solely to start section 6. Keep the documented
uncertainties and software limitations in the final report.

## 0. Selected runs and retained history

| Task | Submission run | Analysis model | Status |
|---|---|---|---|
| 1 | `4hjo_submission_20261029T200938399152Z` | `claude-sonnet-5-5` | Accepted after user review |
| 2 | `20261029T211700335443Z` | `claude-sonnet-5-5` | Accepted after user review |
| 3 | `20261029T222440220672Z` | `claude-haiku-5-5` | Accepted after user review |

Six earlier runs are in `archive/2026-10-29-before-sonnet/`. They are historical work,
not submission evidence. Original protein practice outputs retain their analysis-agent
attribution. Documentation before the handoff edits is in
`archive/2026-10-29-before-deliverable-review/`. Raw inputs remain unchanged.

## 1. Environment and offline checks

Use the existing scientific Python environment. Live scripts read `ANTHROPIC_API_KEY`
from the environment. The key is in `.env`; load it only when making live requests:

```zsh
cd /Users/jeffwang/VSCode_Workspace/agent-assisted-binf
set -a
source .env
set +a
```

Do not include `.env` in the submission. No API key is needed for offline verification.
Do not upgrade dependencies mid-run. Runs record their package versions; the final
root `requirements.lock.txt` still needs to be created in section 6.

```bash
python protein/run_analysis.py --verify protein/runs/4hjo_submission_20261029T200938399152Z
python single_cell/run_analysis.py --verify single_cell/runs/20261029T211700335443Z
python spatial/run_analysis.py verify spatial/runs/20261029T222440220672Z
```

All three passed during the pre-deliverable review. These commands check numerical
results and file integrity, not biological interpretation. The supplemental spatial
review checks can be repeated with `python spatial/review/check_task3.py`.

## 2. Task 1

Read `protein/HANDOFF.md`, `REVIEW_NOTES.md` and the selected run's `RESULTS.md`.
The user selected 4HJO and G719S, T790M, C797S, L858R and L861Q. All five mapped and
passed numerical checks. Keep mutant-mechanism uncertainty and drug comparators separate.
Figures/tables remain inside the run until section 6.

Only if deliberately starting a new analysis:

```bash
python protein/run_analysis.py --config protein/cases/4hjo.json
```

To continue an interrupted run, use `--resume` with its existing path. The selected
run's token-limit failure was already recovered; it does not need another retry.

## 3. Task 2

Read `single_cell/HANDOFF.md`, `REVIEW_NOTES.md` and the selected run's `RESULTS.md`.
QC retained 2,664 cells; the 70% subsample contains 1,864. The QC-field typo was repaired
and the workflow completed. Pairwise Wilcoxon warnings did not invalidate its saved tables.

Do not use exact-string label agreement as biological stability evidence. Use barcode
overlaps, ARI/NMI and reviewed marker interpretations. For figures, the numbered UMAPs
are easier to read than the plots with long annotation legends.

Only if deliberately starting a new analysis:

```bash
python single_cell/run_analysis.py --config single_cell/config.json
```

## 4. Task 3

Read `spatial/HANDOFF.md`, `REVIEW_NOTES.md` and the corrected report under
`spatial/records/20261029T222440220672Z/`. The user selected resolution 0.5 before
cluster tissue maps, accepted the report and confirmed the H&E overlay visually.
The additional review checks now have a saved script in `spatial/review/`.

Only if deliberately starting a new analysis:

```bash
python spatial/run_analysis.py agent
```

Use `quit` to pause, not `pause`. Other input is treated as feedback. The invalid JSON
and accidental-feedback interruption in this run were resolved; no retry is pending.
Do not run the separate numerical commands again to prepare the deliverable.

## 5. Human review and audit records

The reviewer for these submission runs is the user. Describe the process directly:
"I reviewed the agent's plan, checked the outputs against the data and sources, sent
feedback, and accepted the revised analysis with the stated limitations."

For each task, retain the actual question, agent answer, approved settings, check and
outcome, correction, and remaining uncertainty in `REVIEW_NOTES.md` and `AGENT_LOG.md`.
Credit Python for computations and the configured Claude model for proposals and
interpretation. Credit Codex separately for software and documentation work.

A source being retrieved does not prove a claim. A numerical verifier does not validate
cell identity, mechanism or anatomy. State which raw-data calculation, independent
method or source comparison the user used. Preserve negative and uncertain findings.

Feedback prompts read one line. Use one line for each complete feedback message.
Resume interrupted work with the existing run path rather than starting over:

```bash
python protein/run_analysis.py --resume protein/runs/4hjo_submission_20261029T200938399152Z
python single_cell/run_analysis.py --resume single_cell/runs/20261029T211700335443Z
python spatial/run_analysis.py agent --resume spatial/runs/20261029T222440220672Z
```

These selected runs are accepted; the commands are recovery references, not required
next steps. Any change to numerical preprocessing needs a new reviewed run. Documentation
corrections require an explicit change record and updated integrity hashes.

## 6. After all three are accepted: assemble the deliverable

This is the next phase. The combined `report.pdf` has not been written.

1. Curate the selected runs into the project layout. Task 3 already has a records copy;
   Tasks 1 and 2 still need one. Copy Task 1 figures/tables to `protein/figures/RUN_ID/`
   and `protein/tables/RUN_ID/`. Tasks 2 and 3 already write there. Exclude historical
   practice outputs from the submission selection.
2. Copy the current `RESULTS.md`, `REVIEW.md`, `AGENT_LOG.md`, documentation correction
   records, settings/version JSON, `verification.json`, source records and exact generating
   `code/` into `<task>/records/RUN_ID/`. Include the `HANDOFF.md`, task-level review notes
   and independent check scripts. Preserve original runs locally. Do not include `.env`,
   `.h5ad`, caches, full API transcripts, raw event logs or superseded recovery copies.
   If a recovery runtime differs from `code/`, retain it separately with its change record.
3. Generate a manifest for the files actually shipped, using repository-relative paths.
   Original run manifests record the original environment and are not portable package
   inventories. Verify every curated copy against its source.
4. Freeze the current environment and record PyMOL separately:

```bash
python -m pip freeze > requirements.lock.txt
```

5. Write the short `report.pdf`: mutation comparison; cell identities, robustness and
   ambiguity; spatial organization, genes and null comparison; one Agent Audit per task;
   limits, citations and a checkpoint-to-evidence index. Start from the concise handoffs,
   then check every number and citation against the detailed records. Use readable figures
   and explain the protein colors and Cα spheres in its caption.
6. Reassess PROJECT_PLAN checkpoints and RUBRIC Status/Evidence/Score against the actual
   packaged evidence. Scores remain for assessment; unresolved work stays visible. Add
   final page and figure references to the report's evidence index.
7. Render and inspect the PDF, check its links/citations and confirm that all included
   figures and tables have generating code and reproducibility instructions.

The accepted runs supply evidence for the report. Acceptance does not remove their
scientific limits or automatically award rubric points.
