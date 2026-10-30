# Task 1: standalone Claude analysis

Start with [HANDOFF.md](HANDOFF.md) for the accepted findings, review corrections and
remaining limits. The user was the human reviewer; Claude was the analysis agent.
The original runs remain local evidence; final packaging is still pending.


Claude is the only language model used at runtime. Python handles scientific calculations,
retrieval, file writing and the review prompts. Codex is used only to develop this software.
The existing `protein/RESULTS.md` is the historical Claude Code practice analysis, not the
output of a new API run. New runs never overwrite it.

**Fresh-run setup (2026-10-29):** the user selected 4HJO and the five configured EGFR
mutations for submission. The preset now uses `claude-sonnet-5-5` and case name
`4hjo_submission`. Earlier run directories are archived under
`archive/2026-10-29-before-sonnet/`; historical practice artifacts remain attributed
as practice. Follow [the end-to-end checklist](../CLEAN_RUN.md).

## Setup

Use Python 3.9 or later with Biopython, NumPy and the `pymol` command available:

```bash
python -m pip install -r protein/requirements.txt
brew install pymol
```

On this laptop, the tested Python is `/Users/jeffwang/miniforge3/bin/python`;
the system `/usr/bin/python3` does not have the scientific packages installed.
No Anthropic SDK or agent framework is required. The client makes HTTPS requests to the
Anthropic Messages API. The model ID is explicit in the preset; change it to a supported
Claude model you can access if needed. Live Claude requests incur API usage charges.

Configure `ANTHROPIC_API_KEY` in your shell environment. Do not put it in JSON, source code,
review prompts or the repository. For an interactive zsh terminal, this reads it without
displaying it or placing the value in shell history:

```zsh
read -rs 'ANTHROPIC_API_KEY?Anthropic API key: '
export ANTHROPIC_API_KEY
```

## Input and one-command workflow

`cases/4hjo.json` points to the supplied mmCIF and PDB files and specifies chain A,
UniProt P00533, five candidate substitutions, the question, output directory and Claude model.
Paths inside the JSON are relative to the repository root. The config path on the command
line is relative to your terminal's current directory. No API key is stored in the preset.

From the repository root:

```bash
python protein/run_analysis.py --config protein/cases/4hjo.json
```

1. The program validates the inputs, matching the entry ID, chain, heavy atoms and coordinates
   across both files. It checks the local dependencies before making a paid request.
2. Claude proposes a plan within the supported methods. Read it and type `approve`, request
   a revision in plain language, or type `quit` to pause. Do not approve unsupported methods.
3. Python runs mapping, measurements, rendering and independent checks. Cached UniProt/SIFTS
   inputs are reused where available; other inputs require internet access.
4. Claude receives the actual tables, source annotations, structure metadata and figure.
   It can search PubMed titles/abstracts and run the contact-cutoff sensitivity check.
5. Read `DRAFT.md` and the figure. Ask follow-up questions in the terminal. Claude can retrieve
   more literature, run the supported control, and return a revised full report.
6. Type `accept` only when satisfied, then record your checks, an agent weakness or limitation,
   and remaining uncertainties. The program saves `RESULTS.md` and `REVIEW.md`.

A useful challenge for 4HJO is: “Test contact cutoffs of 4, 5 and 6 Angstroms. Does that change
your conclusions about G719S and L858R? Is the T790M steric explanation supported by the
retrieved literature?” The program has no arbitrary shell or code-generation tool; unsupported
analyses require a software extension and are not silently claimed as completed.

Each run prints a unique directory under `protein/runs/`. To continue after quitting or an
API failure, replace `RUN_DIRECTORY` below with that printed directory:

```bash
python protein/run_analysis.py --resume RUN_DIRECTORY
```

Completed exchanges are preserved. Failed/truncated exchanges are retained in `api/` but do
not replace the current draft. Retrying may incur another API charge. Inputs and saved evidence
must be unchanged when resuming. Start a fresh run to change a case or model.

## Outputs and verification

Each run includes:

| File/folder | Contents |
|---|---|
| PLAN.md | Claude's proposed plan, reviewed before computation |
| tables/, figures/ | Calculations, PyMOL verification, structure PNG/session; optional sensitivity table |
| DRAFT.md / RESULTS.md | Current interpretation / explicitly accepted interpretation |
| REVIEW.md | Your acceptance notes |
| config.json, input_checks.json | Resolved inputs, hashes, file agreement, Python/package versions |
| data/ | Retrieved UniProt/SIFTS inputs, provenance, PyMOL version, PubMed source records |
| api/, events.jsonl | Exact API request bodies/responses, usage, tool results, user decisions and timestamps |
| code/ | Copies of the exact scripts used for the run |
| manifest.json, verification.json | Evidence hashes and numerical/artifact check results |
| AGENT_LOG.md, CHECKPOINTS.md | Audit pointers and per-run checkpoint evidence index |

The API receives the case, plan, evidence and image; your local file system is not exposed as
a tool. Credentials are used only in the HTTP header, not written into request logs.
Run folders are ignored by Git because transcripts include images and repeated source caches.
Select important evidence for submission rather than committing every run wholesale.

No-key local checks:

```bash
python protein/run_analysis.py --config protein/cases/4hjo.json --check
python -m unittest discover -s protein -p 'test_*.py' -v
python protein/run_analysis.py --config protein/cases/4hjo.json --compute-only
python protein/run_analysis.py --verify RUN_DIRECTORY
```

`--compute-only` is explicitly a calculation test. It never calls Claude, approves a plan,
creates a final interpretation, or counts as completion of the agent workflow. It also produces
the contact sensitivity table. It cannot be resumed as an approved Claude run.

For the supplied 4HJO files, expect 2,264 matching heavy atoms, five candidate rows, five
successful independent ligand-distance checks and no candidates missing coordinates.
Erlotinib distances in candidate order are 5.06, 3.48, 3.54, 5.26 and 9.22 Å.
All five sites fall below the chosen RSA < 0.25 cutoff; G719 and C797 are close to that boundary.
Baseline contact counts include ligands and adjacent protein residues. The sensitivity table
reports protein-contact counts and a separate ligand flag, so its count can differ by one.

Inspect the figure to confirm every candidate is labeled. Labels name substitutions, but the
displayed atoms are the input structure, not modeled mutants. Verify every key interpretation
against the saved tables and source abstracts. `--verify` checks numerical/artifact consistency
and hashes; it does not prove that Claude interpreted literature correctly or that a predicted
mechanism is true. `CHECKPOINTS.md` does not assign a course grade or auto-check PROJECT_PLAN.md.

## Scientific scope

The numbered scripts remain the computation sequence: `01_map.py` → `02_measure.py` →
`03_render.py`. `run_analysis.py` is the entry point and implements retrieval and the sensitivity
table. The baseline has no random operations. Claude outputs may vary; exact calls are logged.
No GPU, training, mutant modeling, ΔΔG or molecular dynamics is used.

This first implementation supports deposited PDB structures with one model, one selected
single-character chain, standard residues, a constant UniProt/author numbering offset, no
insertion codes, unique ligand names, and 1–8 substitutions at distinct positions. Mapping
disagreements stop the run. Missing candidate coordinates remain missing and require a
justified alternative in the interpretation. It is not a universal protein-analysis pipeline.
PubMed retrieval provides abstracts, not full-text validation. Unsupported or failed retrieval
must remain an evidence gap in the report.

The user reviewed and accepted submission run `4hjo_submission_20261029T200938399152Z`.
The corrected findings and remaining limits are in `HANDOFF.md`. Earlier practice results
remain separate from this Sonnet run. Packaging and the combined report are still pending. Freeze the final analysis environment with
`python -m pip freeze > requirements.lock.txt` before the final course report.

API references used during implementation:
- https://platform.claude.com/docs/en/api/messages/create
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- https://platform.claude.com/docs/en/models/overview
