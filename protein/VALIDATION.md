# Task 1 implementation verification — 2026-10-28

The standalone workflow is implemented. The local scientific computation and offline
conversation-flow tests pass. **No live Claude API analysis has been run:** the environment
does not contain `ANTHROPIC_API_KEY`. Fixture responses in tests are not scientific evidence.

## Checks performed

- `python -m unittest discover -s protein -p 'test_*.py' -v`: **13 tests pass**. Covers plan
  approval, quitting/resuming without execution, full review/follow-up/acceptance flow,
  invalid inputs/config, mismatched coordinates, changed evidence, failed PyMOL checks,
  API transport/header construction, failed/truncated API responses, unsupported tools,
  PubMed parsing and the actual contact-cutoff calculation.
- `--check`: both supplied files identify 4HJO chain A; **2,264 heavy atoms match** within
  0.002 Å. Raw input checksums are recorded in each run's `input_checks.json`.
- `--compute-only`: all three numbered scripts run successfully. All **six baseline CSVs**
  match the original practice outputs exactly. Five candidate rows; **5/5** PyMOL ligand
  distances agree; no candidate coordinates are missing; all five RSA values are below 0.25.
- The newly generated structure PNG was inspected: all five candidate labels and the catalytic
  residue are visible. Labels identify sites in the original structure, not modeled mutants.
- The sensitivity table identifies G719S and L858R outside the 5 Å ligand threshold and inside
  6 Å. Protein-contact counts are separate from ligand proximity in this table.
- Live public PubMed retrieval was tested for PMID **18227510**. It returned the expected title
  (“The T790M mutation in EGFR kinase causes drug resistance by increasing the affinity for ATP.”)
  and a nonempty abstract. This tests retrieval, not a new scientific interpretation.
- All Python files compile. Local validation requires no Claude key, paid API request or Codex runtime.

## Saved local run

The latest verified calculation-only run is:

`protein/runs/4hjo_practice_20261028T185835503455Z`

```bash
python protein/run_analysis.py --verify protein/runs/4hjo_practice_20261028T185835503455Z
```

Run directories are intentionally ignored by Git. To reproduce on another checkout:

```bash
python protein/run_analysis.py --config protein/cases/4hjo.json --compute-only
```

Tested versions: Python 3.9.15, Biopython 1.85, NumPy 1.25.2, PyMOL 3.1.0.
Scientific calculations use no randomness. The CLI and API request logic use the standard library.

## What remains before Task 1 is satisfactory

1. Configure Anthropic credentials and run the normal command in `README.md`.
2. Review Claude's plan before approving computation. Verify model access and a complete API response.
3. Review the draft against its saved tables, figure and source abstracts. Ask at least one meaningful
   scientific challenge; inspect any additional evidence. Document a weakness or limitation and its handling.
4. Accept the supported report with review notes. Inspect that run's `CHECKPOINTS.md` and `AGENT_LOG.md`.
5. Confirm the assigned protein/candidates or an approved exception for 4HJO, then complete the final
   submission checkpoints, rubric scores and report evidence. Freeze the final environment before reporting.

The existing `protein/RESULTS.md` remains a historical Claude Code practice result, with its buried-site
count corrected to match the computed CSV. It is not a substitute for the pending live standalone run.
