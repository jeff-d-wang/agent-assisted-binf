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

Submission run `4hjo_submission_20261029T200938399152Z`, analyzed by Sonnet and
reviewed and accepted by the user. See `protein/HANDOFF.md` and `protein/REVIEW_NOTES.md`.
Paths: `fig/` = `protein/figures/RUN/`, `tab/` = `protein/tables/RUN/`, `rec/` = `protein/records/RUN/`.
Figure, table and page numbers refer to `report.pdf` (source `report/report.md`; captions also in `report/figures.md`).
Scored 2026-10-29 by Claude Code (claude-opus-5-5) at the user's request; the user may revise.

| Checkpoint | Show in your submission | Pts | Status | Evidence | Score |
|---|---|---|---|---|---|
| P1 · Map the variants | Identify the protein, verify each variant against its sequence, and map all candidate residues to the chosen structure/model. | 5 | complete | report.pdf p. 1-3; Report Task 1 mapping table; `tab/mapping.csv`, `functional_sites.csv`; `rec/input_checks.json`, `rec/data/4hjo_sifts.json`, `P00533.json`; `protein/01_map.py`. SIFTS and alignment agree for all 5 (offset −24); reproduced by `protein/review/check_dist.py`. | 5 |
| P2 · Measure structural evidence | Define and report reproducible measurements for each candidate, or explain and document a justified alternative where coordinates are unavailable. | 7 | complete | report.pdf p. 1-3; Report Table 1; `tab/measurements.csv`, `contacts_5A.csv`, `contact_sensitivity.csv` (4/5/6 Å), `pymol_check.csv`; `protein/02_measure.py`, `03_render.py`. Distances reproduced to 0.01 Å (`review/check_dist.py`); near-cutoff burial checked with `review/check_sasa.py`. RSA threshold itself not varied. | 7 |
| P3 · Interpret with evidence | Compare candidate mechanisms using observed results and cited sources; separate observations from predictions and state uncertainty. | 8 | complete | report.pdf p. 3; `rec/RESULTS.md` §5–8; `rec/data/pubmed_*.json`; `protein/REVIEW_NOTES.md`. Observation / prediction / evidence / confidence kept separate; drug comparisons kept comparator-specific. −1: literature is abstract-only, UniProt-cited primary papers not fetched, and G719S/L861Q rest mostly on pooled, small or computational studies. | 7 |
| P4 · Communicate the comparison | Provide an annotated structure of the assigned protein and one table covering every candidate. | 5 | complete | report.pdf p. 2-3; Figure 1 (`fig/structure_annotated.png`, `protein/03_render.py`) and Table 1 (all 5 candidates). −1: the figure has no in-image legend and relies on its caption; C797S and D837 labels overlap structure. | 4 |
| **Subtotal** | | **25** | | | **23** |

## Task 2: Single-cell analysis — 25 points

Submission run `20261029T211700335443Z`, analyzed by Sonnet and reviewed and accepted
by the user. See `single_cell/HANDOFF.md` and `single_cell/REVIEW_NOTES.md`.
Paths: `fig/`, `tab/`, `rec/` = `single_cell/{figures,tables,records}/RUN/`. Scored 2026-10-29 by
Claude Code (claude-opus-5-5) at the user's request; the user may revise.

| Checkpoint | Show in your submission | Pts | Status | Evidence | Score |
|---|---|---|---|---|---|
| S1 · Baseline and QC | Report QC decisions, analysis settings and seed, cluster sizes, and a cluster-labeled UMAP. | 6 | complete | report.pdf p. 4; Figure 2 (`fig/annotated_umap_res_0p6.png`); `rec/QC.md`, `rec/qc.json`, `rec/plan.json`, `rec/computation.json`; `tab/sizes_res_0p6.csv`; `single_cell/01_qc.py`, `02_cluster.py`. QC reproduced from raw `matrix.mtx` (`review/check_task2.py`). | 6 |
| S2 · Cell-type evidence | Use markers computed from your PBMC3k data and cited biology to support major labels; do not use predefined labels. | 7 | complete | report.pdf p. 5-6; Table 2 (population summary); `tab/annotations.csv`, `investigation_*`; `rec/RESULTS.md` §3, §6; `rec/data/pubmed_*.json`. Labels come from computed markers, with tentative subtypes kept. Sonnet's own citations were weak (disease-context or label-only abstracts). Reviewer-added primary sources [1]-[4] (report p. 6, 11; PMIDs 28091601, 28428369, 32271902, 33271118), checked against source text, now support the marker reading for every major label: T, B, CD14 and FCGR3A monocytes, cytotoxic/NK, DC-like. −1: LDHB, MS4A1, LYZ, FCN1, MS4A7, CDKN1C and LILRA4 remain uncovered; [4] was checked at abstract level; the sources support marker interpretation, not these cells' identities. | 6 |
| S3 · Resolution check | Compare at least three Leiden resolutions with other settings fixed; quantify splits/merges and discuss label stability. | 5 | complete | report.pdf p. 5; Figure 3 (`fig/overlap_res_1.png`); `tab/robustness_metrics.csv`, `cluster_overlaps.csv`; `rec/RESULTS.md` §2. Four resolutions (0.3/0.6/1.0/1.5) on one graph; ARI/NMI reproduced (`review/check_task2.py`). The exact-string label-agreement columns are not used. | 5 |
| S4 · Downsampling check | Rerun a fixed-seed 60–80% cell sample; compare retained cells quantitatively and discuss label stability. | 4 | complete | report.pdf p. 4-5; `tab/cells_downsample.csv`, `annotated_cells_downsample.csv`, `robustness_metrics.csv`; `rec/RESULTS.md` §2; 1,864 cells (70%, seed 42), ARI 0.906 / NMI 0.877, recovery on baseline denominators (checked by crosstab). Disclosed: one draw, clustered at 0.6 only; planned Jaccard and marker-overlap metrics not computed. | 4 |
| S5 · Ambiguous population | Investigate one unclear or unstable population with marker comparisons and a reason for the uncertainty. | 3 | complete | report.pdf p. 6; Figure 4 (`fig/investigation_af28023de2e1.png`); `rec/RESULTS.md` §4; `review/check_dc_overlap.py` (same 36 cells at 0.3/1.0/1.5; all 29 sampled cells form downsample cluster 5). Identity (cDC2 / pDC admixture / doublets) left unresolved, with reasons. | 3 |
| **Subtotal** | | **25** | | | **24** |

## Task 3: Spatial transcriptomics — 25 points

Submission run `20261029T222440220672Z` (analysis agent `claude-haiku-5-5`, due to credit balance issues),
reviewed and accepted by the user (human reviewer) on 2026-10-29. Report:
`spatial/records/20261029T222440220672Z/RESULTS.md`; review: `spatial/records/20261029T222440220672Z/REVIEW.md`, `spatial/REVIEW_NOTES.md`. The report's own
T1–T5 headings follow the workflow prompt, not this rubric; the section mapping is given below.
Paths: `fig/`, `tab/`, `rec/` = `spatial/{figures,tables,records}/RUN/`. Scored 2026-10-29 by
Claude Code (claude-opus-5-5) at the user's request; the user may revise.

| Checkpoint | Show in your submission | Pts | Status | Evidence | Score |
|---|---|---|---|---|---|
| T1 · Expression-only domains | Cluster using expression without spatial information; show the same labels in expression space and on tissue, with settings and spot counts. | 5 | complete | report.pdf p. 7-8; Figure 5 (`fig/clusters_umap_and_tissue.png`); `fig/umap_res_*.png`; `tab/cluster_sizes.csv`, `resolution_comparison.csv`; `rec/config.json`, `approved_qc.json`, `approved_cluster.json`; `spatial/02_cluster.py`, `03_spatial.py`. Resolution approved before tissue maps existed (`rec/events.jsonl`). | 5 |
| T2 · Spatial organization | Define the physical-neighbor graph and report an interpreted numerical spatial statistic. | 5 | complete | report.pdf p. 7-8; `tab/physical_edges.csv`, `original_vs_randomized.csv`; `rec/graph_summary.json`; `rec/RESULTS.md` §T3 (lattice graph, 7,679 edges; same-cluster edge fraction 0.780); `spatial/03_spatial.py`. Graph and statistic reproduced by `spatial/review/check_task3.py`. | 5 |
| T3 · Spatial genes | State the tested gene set and method, rank spatially variable genes, and map at least two genes on tissue. | 4 | complete | report.pdf p. 8; Figure 6 (`fig/gene_tissue_maps.png`, 5 genes); `tab/candidate_genes.csv`, `gene_rankings.csv`; `rec/gene_methods.json` (200 expression-selected genes, Moran I, binary lattice weights); `spatial/03_spatial.py`. | 4 |
| T4 · Compare gene rankings | Compare differential-expression and spatial rankings for the same genes, with examples that explain their differences. | 4 | complete | report.pdf p. 9-10; Figure 7 (`fig/de_vs_spatial_ranks.png`); `tab/gene_rankings.csv`, `ranking_examples.csv`, `gene_cluster_means.csv`; `rec/RESULTS.md` §T5; cluster-mean check in `spatial/REVIEW_NOTES.md` and `review/check_task3.py` (supports Dnali1/Pmch, corrects the agent's 2900040C04Rik hypothesis). | 4 |
| T5 · Negative control | Use at least 100 fixed-seed randomizations; compare the same observed and null statistic, report an empirical comparison, and note a limitation. | 7 | complete | report.pdf p. 9; Figure 8 (`fig/randomized_control.png`); `tab/null_distribution.csv`, `original_vs_randomized.csv`, `spatial_resolution_sensitivity.csv`; `rec/verification.json`. 999 shuffles, seed 42, tail 0.001; limitation stated (shuffle ignores autocorrelation); separate seed-7 null reproduced. | 7 |
| **Subtotal** | | **25** | | | **25** |

## Agent Audit — 15 points (5 per task)

| Item | Pts | Protein | Single-cell | Spatial |
|---|---|---|---|---|
| Sources used | 1 | 1: 4HJO, UniProt P00533 v301, SIFTS, 29 PubMed queries (27 cited PMIDs), Biopython/PyMOL versions (`rec/data/provenance.json`, `rec/input_checks.json`) | 1: PBMC3k matrix (SHA-256), Scanpy stack versions, PubMed abstracts (`rec/inputs.json`, `rec/data/`); reviewer-added sources [1]-[4] listed separately as not agent resources | 1: Visium h5 + spatial folder (SHA-256), package versions; no literature retrieved, stated (`rec/inputs.json`) |
| What the agent computed vs retrieved | 1 | 1: table in `rec/RESULTS.md` §10 | 1: Computed / Inference / Retrieved tags throughout `rec/RESULTS.md` | 1: claim-status table in `rec/RESULTS.md` (Draft audit) |
| One independent check and its result | 2 | 2: `protein/review/check_dist.py` (distances match to 0.01 Å), `check_sasa.py` (G719/C797 within 0.02 of RSA cutoff), PMID-vs-abstract check | 2: `single_cell/review/check_task2.py`, `check_rev1.py`, `check_dc_overlap.py` (QC, ARI/NMI, denominators, marker fractions all match; revision-0 denominators wrong) | 2: `spatial/review/check_task3.py` (graph, edge agreement, seed-7 null, QC confounding, cluster means; PC30 2.0% error found) |
| One weakness or limitation you evaluated | 1 | 1: sequence-local contacts used as functional evidence, lost queries, misquote; corrected or disclosed (`protein/REVIEW_NOTES.md`) | 1: wrong denominators, unsupported PMIDs, skipped doublet check; corrected or disclosed (`single_cell/REVIEW_NOTES.md`) | 1: false caveats, PC30 error, untested QC confounding, wrong discordant-gene hypothesis (`spatial/REVIEW_NOTES.md`) |
| **Subtotal** | **5 each** | **5** | **5** | **5** |

## Reproducibility and report — 10 points (2 each)

| Item | Pts | Status | Evidence | Score |
|---|---|---|---|---|
| Ordered code/notebooks with a run README | 2 | complete | `README.md` (run order per task), task READMEs, numbered scripts, `<task>/records/RUN/code/` snapshots | 2 |
| Data sources and software versions | 2 | complete | `README.md` Data table; input SHA-256 in each `rec/inputs.json` / `input_checks.json`; `requirements.lock.txt` (imported versions; h5py 3.6.0 metadata discrepancy disclosed); PyMOL 3.1.0; per-run hashes in `records/RUN/manifest.json` | 2 |
| Settings and random seeds | 2 | complete | `rec/config.json` and approved settings (`plan.json`, `qc.json`, `approved_*.json`); seed 42 for Tasks 2–3; Task 1 deterministic | 2 |
| Labeled figures/tables tied to conclusions | 2 | complete | report.pdf pp. 2-9: Figures 1-8 and Tables 1-4, each with a caption naming its source file or script and a takeaway tied to a conclusion; `report/figures.md`. Residual: tick labels in Figures 3 and 6 are small at page size (captions carry the content) | 2 |
| Readable report.pdf with all three Agent Audits and the checkpoint evidence index | 2 | complete | `report.pdf` (12 pages; source `report/report.md`): audits pp. 3, 7, 10-11, each answering the four questions; evidence index p. 12, with page numbers checked against the rendered PDF | 2 |
| **Subtotal** | **10** | | | **10** |

---

## Total

| Section | Max | Score |
|---|---|---|
| Task 1 · Protein | 25 | 23 |
| Task 2 · Single-cell | 25 | 24 |
| Task 3 · Spatial | 25 | 25 |
| Agent Audit | 15 | 15 |
| Reproducibility and report | 10 | 10 |
| **Total** | **100** | **97** |

All scores are a provisional self-assessment by Claude Code (claude-opus-5-5) at the user's request, not a grader's award. Changes on 2026-10-29 after the report revision: S2 5 → 6 (reviewer-added marker sources), the two report items pending → 2 each (report.pdf rendered and checked), and the total 92 → 97.

Before submitting: every checkpoint is marked `complete` or `needs revision` with the page or file containing its evidence, and the same evidence index appears in report.pdf.
