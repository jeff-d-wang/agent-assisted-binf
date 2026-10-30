# Checkpoints and Grading Rubric

Score each task against this file **after finishing that task**, then do a final pass of all sections before submitting. Fill in Status, Evidence, and Score for every checkpoint.

**How points are awarded**
- Full credit: clear results **and** enough code or source information to check them.
- Partial credit: incomplete but valid evidence.
- 0: missing or unverifiable evidence.
- No required biological answer or target statistic. A well-supported negative or uncertain result can earn full credit.

**Status values:** `complete` · `needs revision` · `not started`
**Evidence format:** page/figure/table/code file, e.g. `P2 → Figure 2, Table 1, protein/measure.py`

---

## Task 1: Protein mutation analysis — 25 points

The user selected 4HJO and its five configured EGFR substitutions for submission on
2026-10-29. Historical practice artifacts remain evidence of prior work, not a newly
accepted Sonnet analysis. Fresh execution, source review and acceptance remain pending;
scores are deferred. See `CLEAN_RUN.md` and `protein/README.md`.

| Checkpoint | Show in your submission | Pts | Status | Evidence | Score |
|---|---|---|---|---|---|
| P1 · Map the variants | Identify the protein, verify each variant against its sequence, and map all candidate residues to the chosen structure/model. | 5 | needs revision | Practice: protein/tables/mapping.csv, functional_sites.csv; protein/01_map.py. Fresh Sonnet run/review pending. | pending |
| P2 · Measure structural evidence | Define and report reproducible measurements for each candidate, or explain and document a justified alternative where coordinates are unavailable. | 7 | needs revision | Practice: protein/tables/measurements.csv, contacts_5A.csv, pymol_check.csv; protein/02_measure.py, 03_render.py; protein/VALIDATION.md. Fresh Sonnet run/review pending. | pending |
| P3 · Interpret with evidence | Compare candidate mechanisms using observed results and cited sources; separate observations from predictions and state uncertainty. | 8 | needs revision | Historical practice: protein/RESULTS.md, AGENT_LOG.md. New live Claude interpretation and review pending. | pending |
| P4 · Communicate the comparison | Provide an annotated structure of the assigned protein and one table covering every candidate. | 5 | needs revision | Practice: protein/figures/structure_annotated.png; protein/RESULTS.md; protein/03_render.py. Fresh Sonnet report and review pending. | pending |
| **Subtotal** | | **25** | | | |

## Task 2: Single-cell analysis — 25 points

Earlier runs, including `20261028T235728272943Z`, and their matching tables/figures are
archived under `archive/2026-10-29-before-sonnet/`. Evidence references below describe
historical work inside that archive. The requested fresh Sonnet run, source review,
curated submission evidence and acceptance remain pending; scores are deferred.

| Checkpoint | Show in your submission | Pts | Status | Evidence | Score |
|---|---|---|---|---|---|
| S1 · Baseline and QC | Report QC decisions, analysis settings and seed, cluster sizes, and a cluster-labeled UMAP. | 6 | needs revision | Run 20261028T235728272943Z: QC.md, computation.json; task tables/figures under the same ID. Final presentation pending. | pending |
| S2 · Cell-type evidence | Use markers computed from your PBMC3k data and cited biology to support major labels; do not use predefined labels. | 7 | needs revision | Computed markers and recovered provisional annotations; source support/human review pending. | pending |
| S3 · Resolution check | Compare at least three Leiden resolutions with other settings fixed; quantify splits/merges and discuss label stability. | 5 | needs revision | Run tables: robustness_metrics.csv, cluster_overlaps.csv. Final biological interpretation pending. | pending |
| S4 · Downsampling check | Rerun a fixed-seed 60–80% cell sample; compare retained cells quantitatively and discuss label stability. | 4 | needs revision | Run tables: cells_downsample.csv, robustness_metrics.csv; verification.json. Label-stability review pending. | pending |
| S5 · Ambiguous population | Investigate one unclear or unstable population with marker comparisons and a reason for the uncertainty. | 3 | needs revision | investigation_51c01c3c0b77 expression/pairwise tables and figure. Recovered discussion needs review. | pending |
| **Subtotal** | | **25** | | | |

## Task 3: Spatial transcriptomics — 25 points

The numerical pipeline and standalone Sonnet review workflow are implemented and tested
with synthetic data/mocked responses (2026-10-29). The earlier QC-only run is archived.
Fresh end-to-end analysis and independent scientific review remain pending. T1–T5 have
no accepted submission results yet; see `spatial/README.md` and `spatial/VALIDATION.md`.

| Checkpoint | Show in your submission | Pts | Status | Evidence | Score |
|---|---|---|---|---|---|
| T1 · Expression-only domains | Cluster using expression without spatial information; show the same labels in expression space and on tissue, with settings and spot counts. | 5 | not started | | |
| T2 · Spatial organization | Define the physical-neighbor graph and report an interpreted numerical spatial statistic. | 5 | not started | | |
| T3 · Spatial genes | State the tested gene set and method, rank spatially variable genes, and map at least two genes on tissue. | 4 | not started | | |
| T4 · Compare gene rankings | Compare differential-expression and spatial rankings for the same genes, with examples that explain their differences. | 4 | not started | | |
| T5 · Negative control | Use at least 100 fixed-seed randomizations; compare the same observed and null statistic, report an empirical comparison, and note a limitation. | 7 | not started | | |
| **Subtotal** | | **25** | | | |

## Agent Audit — 15 points (5 per task)

| Item | Pts | Protein | Single-cell | Spatial |
|---|---|---|---|---|
| Sources used | 1 | | | |
| What the agent computed vs retrieved | 1 | | | |
| One independent check and its result | 2 | | | |
| One weakness or limitation you evaluated | 1 | | | |
| **Subtotal** | **5 each** | | | |

## Reproducibility and report — 10 points (2 each)

| Item | Pts | Status | Evidence | Score |
|---|---|---|---|---|
| Ordered code/notebooks with a run README | 2 | not started | | |
| Data sources and software versions | 2 | not started | | |
| Settings and random seeds | 2 | not started | | |
| Labeled figures/tables tied to conclusions | 2 | not started | | |
| Readable report.pdf with all three Agent Audits and the checkpoint evidence index | 2 | not started | | |
| **Subtotal** | **10** | | | |

---

## Total

| Section | Max | Score |
|---|---|---|
| Task 1 · Protein | 25 | |
| Task 2 · Single-cell | 25 | |
| Task 3 · Spatial | 25 | |
| Agent Audit | 15 | |
| Reproducibility and report | 10 | |
| **Total** | **100** | |

Before submitting: every checkpoint is marked `complete` or `needs revision` with the page or file containing its evidence, and the same evidence index appears in report.pdf.
