# Agent-assisted bioinformatics

3 tasks: effects of EGFR missense mutations (protein), cell types
and robustness in PBMC3k (single-cell), and spatial organization in a Visium adult mouse
brain section (spatial). `RUBRIC.md` records each checkpoint's status, evidence and
score, and `PRE_DELIVERABLE_REVIEW.md` summarizes the checks and corrections made before the report. The final report is `report.pdf` (12 pages; source `report/report.md`).

In every task, Python does the calculations and Claude proposes the plan and interprets the
results: Sonnet (`claude-sonnet-5-5`) for Tasks 1–2, and Haiku (`claude-haiku-5-5`) for
Task 3 due to credit balance issues. The user (me, Jeff) reviews the plans and outputs, sends feedback, checks evidence and accepts the final task report as the human reviewer.

## Layout

```
├── README.md                 # this file
├── RUBRIC.md                 # checkpoint status, evidence and scores
├── PRE_DELIVERABLE_REVIEW.md # review checks and corrections
├── report.pdf                # final report
├── report/                   # report source (report.md) and figure list (figures.md)
├── requirements.txt          # all three tasks; includes the per-task pins
├── requirements.lock.txt     # exact environment used for the submission runs
├── datasets/                 # raw inputs (not included; see Data)
├── protein/                  # Task 1
├── single_cell/              # Task 2
└── spatial/                  # Task 3
```

Each task folder has the same contents:

| Path | Contents |
|---|---|
| `01_*.py`, `02_*.py`, ... | Analysis scripts, numbered in run order |
| `run_analysis.py` | Entry point that runs the scripts with the Claude review stops |
| `README.md` | Setup, commands, outputs and how to check them |
| `AGENT_LOG.md` | Dated audit log: prompts, resources, settings, checks, agent weaknesses |
| `figures/RUN_ID/`, `tables/RUN_ID/` | Figures and tables from the submission run |
| `records/RUN_ID/` | Accepted report, review notes, settings, versions, sources and a code snapshot from that run |
| `runs/` | Full run folders with API transcripts (local only, not included) |

The files at the top level of `protein/figures/` and `protein/tables/`, along with
`protein/RESULTS.md`, come from the earlier Task 1 practice analysis. They are kept there,
under their original attribution, and are not the submission run.

## Data

| Task | Input files | Source |
|---|---|---|
| 1 | `datasets/4hjo.cif.gz`, `datasets/4hjo.pdb` (chain A, erlotinib-bound) | RCSB PDB 4HJO; UniProt P00533 and SIFTS are fetched at run time |
| 2 | `datasets/pbmc3k/filtered_gene_bc_matrices/hg19/{matrix.mtx,genes.tsv,barcodes.tsv}` | 10x Genomics PBMC3k |
| 3 | `datasets/visium_mouse_brain/V1_Adult_Mouse_Brain_filtered_feature_bc_matrix.h5` and `spatial/` (positions, scale factors, images) | 10x Genomics V1 Adult Mouse Brain |

The candidate substitutions for Task 1 are G719S, T790M, C797S, L858R and L861Q (UniProt
numbering). The input files are not included in this submission. Put the course-provided
PBMC3k and Visium archives in `datasets/pbmc3k/` and `datasets/visium_mouse_brain/`, download
4HJO from RCSB, then extract the archives once from the repository root:

```bash
curl -o datasets/4hjo.cif.gz https://files.rcsb.org/download/4HJO.cif.gz
curl -o datasets/4hjo.pdb https://files.rcsb.org/download/4HJO.pdb
tar -xzf datasets/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -C datasets/pbmc3k
tar -xzf datasets/visium_mouse_brain/V1_Adult_Mouse_Brain_spatial.tar.gz -C datasets/visium_mouse_brain
```

Each run records the SHA-256 of its inputs (`records/RUN_ID/inputs.json`, or `input_checks.json`
for Task 1), so you can confirm you have the same files. Database records and PubMed abstracts that a run
retrieved are saved in its `data/` folder.

## Setup

You need Python 3.9 or 3.10. PyMOL is installed separately for the Task 1 figure:

```bash
python -m pip install -r requirements.txt
brew install pymol
```

Each run records its package versions, and `requirements.lock.txt` freezes the environment
that ran all three submission runs (PyMOL 3.1.0 separately). In that environment some packages
have two installed metadata versions; the lock gives the version Python actually imports, so
h5py is 3.6.0 although the Task 3 run's `inputs.json` records 3.11.0. Live runs read `ANTHROPIC_API_KEY` from the
environment and are billed for API usage. Never commit the key. The preflight checks and
unit tests below make no API calls:

```bash
python protein/run_analysis.py --config protein/cases/4hjo.json --check
python single_cell/run_analysis.py --config single_cell/config.json --check
python spatial/run_analysis.py --check
python -m unittest discover -s protein -p 'test_*.py' -v      # same for single_cell, spatial
```

## Running each task

| Task | Command | Script order | Settings and seed |
|---|---|---|---|
| 1 Protein | `python protein/run_analysis.py --config protein/cases/4hjo.json` | `01_map.py` → `02_measure.py` → `03_render.py` | `protein/cases/4hjo.json`; no random steps |
| 2 Single-cell | `python single_cell/run_analysis.py --config single_cell/config.json` | `01_qc.py` → `02_cluster.py` → `03_compare.py` → `04_verify.py` | Sonnet proposes settings and the user approves them (`plan.json`, `qc.json` in the run); seed 42 |
| 3 Spatial | `python spatial/run_analysis.py agent` | `01_qc.py` → `02_cluster.py` → `03_spatial.py` → `04_verify.py` | `spatial/config.json` plus the approved QC thresholds and resolution; seed 42 |

Each command prints a run folder and stops at review gates where you approve, give
feedback, or quit. Resume with `--resume RUN_DIR`; for Task 3 the command is `agent --resume RUN_DIR`.
To verify a run independently, use `--verify RUN_DIR` for Tasks 1 and 2 or `verify RUN_DIR`
for Task 3. Details are in each task's README.

## Submission runs and evidence

| Task | Run ID | Report | Figures and tables |
|---|---|---|---|
| 1 Protein | `4hjo_submission_20261029T200938399152Z` | `protein/records/RUN_ID/RESULTS.md` | `protein/figures/RUN_ID/`, `protein/tables/RUN_ID/` |
| 2 Single-cell | `20261029T211700335443Z` | `single_cell/records/RUN_ID/RESULTS.md` | `single_cell/figures/RUN_ID/`, `single_cell/tables/RUN_ID/` |
| 3 Spatial | `20261029T222440220672Z` | `spatial/records/RUN_ID/RESULTS.md` | `spatial/figures/RUN_ID/`, `spatial/tables/RUN_ID/` |

Every figure and table comes from a script in the same task folder, and the code snapshot in
`records/RUN_ID/code/` is the exact version that produced it. The index that maps each
checkpoint to its evidence is in `RUBRIC.md` and on the last page of `report.pdf`, with page references checked against the rendered PDF. The
Agent Audit for each task draws on `<task>/AGENT_LOG.md` and `records/RUN_ID/REVIEW.md`.

`records/RUN_ID/` holds everything from the run except API transcripts (`api/`, the message
history in `state.json`), caches and `.h5ad` files, the pre-review `DRAFT.md` and the review
packet; the full run folders stay local. Each `records/RUN_ID/manifest.json` lists the SHA-256
of the run's original files (keyed by their original local paths).
