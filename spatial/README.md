# Task 3: spatial transcriptomics

Start with [HANDOFF.md](HANDOFF.md) for the accepted findings, review corrections and
remaining limits. The user was the human reviewer; Claude was the analysis agent.
The original runs remain local evidence; final packaging is still pending.


The reviewed plan now has a standalone Claude workflow as well as manual numerical
stages. Codex developed the software; Python computes; Haiku proposes, interprets and
responds to feedback; the user approves decisions. `config.json` selects `claude-haiku-5-5`
(switched from `claude-sonnet-5-5` due to credit balance issues).
The earlier QC-only run is archived under `archive/2026-10-29-before-sonnet/`. Start fresh.
The generated `EVIDENCE.md` is numerical evidence, not an accepted scientific report.

## Recommended: fresh Haiku analysis

Use [CLEAN_RUN.md](../CLEAN_RUN.md) for the literal sequence across all three tasks.
After setting `ANTHROPIC_API_KEY` in your terminal, run:

```bash
/Users/jeffwang/miniforge3/bin/python spatial/run_analysis.py agent
```

The program prints a new run path and pauses at each review gate:

1. Read Haiku's `PLAN.md`. Type feedback, `approve`, or `quit`. Numerical settings are
   explicit in `config.json`; to change them, quit, edit the config, then start a new run.
2. Python computes QC only. Haiku inspects plots/quantiles and proposes thresholds in
   `QC.md`. Review visual alignment and the actual numbers before typing `approve`.
3. Python clusters expression. Haiku sees only expression diagnostics and proposes the
   primary resolution in `CLUSTER_REVIEW.md`. Review before `approve`; tissue cluster maps
   have not yet been generated. QC/resolution approvals are saved as executable settings.
4. Python computes spatial results and runs the independent verifier. Haiku receives
   the evidence, can retrieve PubMed abstracts and writes `DRAFT.md` plus a draft audit.
5. Type `quit` to consult your independent reviewer. Use `REVIEW_PACKET.md`, actual figures,
   tables, sources and logs. Resume with the command below, paste substantive feedback,
   and inspect the revised draft. Changes to preprocessing require a new run, not prose edits.
6. Type `accept` only when satisfied. Record reviewer identity, an actual independent
   check/result, an actual weakness and its evaluation, and uncertainties. This saves
   `RESULTS.md` and `REVIEW.md`. Acceptance does not auto-grade the rubric.

```bash
/Users/jeffwang/miniforge3/bin/python spatial/run_analysis.py agent --resume RUN_DIRECTORY
```

API prompts, responses and usage are saved in `api/`; decisions in `events.jsonl`; sources
in `data/`; stage summaries in `AGENT_LOG.md`. Truncated/invalid responses are not accepted.
Completed exchanges are reused on resume; correcting a failed response may incur another
charge. Each response has a bounded tool loop. Scripts run from the saved code snapshot.
The workflow's model transport and review sequence have offline/synthetic tests; a live
model request and real scientific acceptance are not claimed as tested here.

## Setup and checks

On this laptop, start in the repository and use the tested Python:

```bash
cd /Users/jeffwang/VSCode_Workspace/agent-assisted-binf
PY=/Users/jeffwang/miniforge3/bin/python
"$PY" spatial/run_analysis.py --check
"$PY" -m unittest discover -s spatial -p 'test_*.py' -v
```

`--check` imports dependencies and hashes the four raw inputs. It does not analyze the
mouse-brain matrix, create a run or call an API. Tests create synthetic 10x files in
temporary folders, run all four stages, and remove the fixture afterward. They never
read the course dataset. These checks and the manual numerical stages need no API key;
the recommended `agent` command does require your key and makes paid requests.

Elsewhere, create a Python 3.9 or 3.10 environment and install:

```bash
python -m pip install -r spatial/requirements.txt
```

Use that environment's Python instead of `$PY`. Task 3 pins the tested Scanpy stack;
Squidpy is not required. Do not upgrade the environment during a run. Full installed
versions are frozen per run. The supplied inputs are already extracted on this laptop.
If the spatial directory is absent elsewhere, use the plan's command once:

```bash
tar -xzf datasets/visium_mouse_brain/V1_Adult_Mouse_Brain_spatial.tar.gz -C datasets/visium_mouse_brain
```

Never edit raw inputs. `config.json` input paths are relative to the repository, or
absolute. Review settings before starting; defaults include seed 42, 200 candidates
and 999 permutations. To use a different config, place `--config PATH` before `qc`.

## Manual numerical stages (optional; the agent workflow already dispatches these)

### 1. QC only: `01_qc.py`

```bash
"$PY" spatial/run_analysis.py qc
```

The command prints a unique run path. Store it, replacing the placeholder:

```bash
RUN=spatial/runs/REPLACE_WITH_PRINTED_RUN_ID
```

Figures are in `spatial/figures/RUN_ID/`, tables in `spatial/tables/RUN_ID/`, and
metadata/code snapshots in `$RUN`. Inspect:

- `qc_distributions.png`, `qc_joint.png`, `qc_quantiles.csv`: count, detected-gene and
  mitochondrial distributions for in-tissue spots.
- `qc_tissue.png`: confirm spot centers overlay the correct tissue; inspect quality
  gradients. Numeric bounds checks cannot prove correct image alignment.
- `qc_spots.csv` and `qc_summary.json`: matrix/in-tissue counts and zero-count spots.

Copy the review template without overwriting an existing review, then edit it:

```bash
cp -n spatial/qc_review.template.json spatial/qc_review.json
```

Replace every `null` using the QC distributions and write a substantive `rationale`.
`min_genes`, `max_genes`, `min_counts`, and `max_counts` are positive integers;
`max_pct_mt` is a percentage from 0 to 100. Boundaries are inclusive. Out-of-tissue and
zero-count spots cannot pass. The blank template deliberately fails validation.

### 2. Expression-only clustering: `02_cluster.py`

```bash
"$PY" spatial/run_analysis.py cluster "$RUN" --qc spatial/qc_review.json
```

Inspect `umap_res_0p3.png`, `umap_res_0p5.png`, `umap_res_0p8.png`, `cluster_sizes.csv`,
`resolution_comparison.csv`, `resolution_overlaps.csv`, and `pca_variance.csv`. ARI
comparisons use the first configured resolution as reference. Check `qc_decisions.csv`
and `filter_summary.json` for exclusions and retained counts.

Defaults: retain genes detected in at least three retained spots; normalize to 10,000
counts; log1p; rank Seurat normalized dispersions; use up to 2,000 HVGs, centered scaling
clipped at 10, 30-PC arpack PCA and 15 Euclidean expression neighbors; run Leiden at
0.3, 0.5 and 0.8 on one expression graph; display a seed-42 UMAP. HVG ties use gene-name
order. PCA, neighbors, Leiden and UMAP receive the seed. No coordinates or histology
are attached to the expression objects. The top 200 candidates are frozen here for
both later rankings. Statistical gene comparisons use unscaled log expression.

Choose the primary resolution from expression diagnostics. The proposed baseline was
0.5; any change needs an expression-based justification. Keep small/unstable clusters
visible. If preprocessing needs revision, start a new QC run with revised settings.

### 3. Freeze labels and compute spatial evidence: `03_spatial.py`

Replace the quoted placeholder with your actual reason before executing:

```bash
"$PY" spatial/run_analysis.py spatial "$RUN" --resolution 0.5 --reason "REPLACE: explain your expression-based choice using cluster sizes and resolution comparisons"
```

The choice is written before any cluster tissue map appears. A failed spatial step
must be retried with the same resolution and reason. Completed stages cannot be
silently overwritten. Do not choose another primary result for its spatial score.

| Evidence | Outputs |
|---|---|
| T1: identical labels/colors in expression and tissue space | `clusters_umap_and_tissue.png`, `expression_clusters.csv`, `spatial_spots.csv` |
| T2: physical graph and cluster statistic | `physical_edges.csv`, `graph_summary.json`, `spatial_summary.json` |
| T3: tested genes, spatial rankings and maps | `candidate_genes.csv`, `gene_rankings.csv`, `mapped_genes.csv`, `gene_tissue_maps.png` |
| T4: same-gene DE vs spatial comparison | `de_vs_spatial_ranks.png`, `ranking_examples.csv`, `gene_cluster_means.csv` |
| T5: observed vs randomized statistic | `randomized_control.png`, `null_distribution.csv`, `original_vs_randomized.csv` |
| Supporting sensitivity check | `spatial_resolution_sensitivity.csv` (descriptive; not a selection criterion) |

JSON files are in `$RUN`; CSVs and PNGs are in the run's table/figure folders.
`EVIDENCE.md` links those folders and lists calculated values.

**Graph:** unweighted, undirected immediate Visium neighbors at array offsets `(0, ±2)`
and `(±1, ±1)`. Missing spots leave gaps. Degrees, components and isolates are recorded.

**Primary statistic:** fraction of undirected edges with matching cluster labels. Shuffle
labels 999 times on the fixed graph, preserving cluster sizes and including isolates in
the permutation pool. Report observed fraction, null mean/spread, excess above the null,
and `(1 + #null >= observed) / (999 + 1)`. Minimum attainable tail proportion: 0.001,
never zero. A one-cluster result has agreement 1 before/after shuffling and no enrichment.

**Genes:** Moran's I uses symmetric binary weights without row normalization. Isolates
are excluded from its mean and denominator; DE includes all retained spots. Constant
genes retain undefined statistics. DE uses tie-corrected Kruskal–Wallis H across frozen
clusters, descriptively, without confirmatory p-values because groups came from expression.

Example categories are prespecified: strong means top quartile of defined ranks; weaker
means below the median. Ties are averaged and missing categories remain absent. Maps
show the top two spatial genes, the lowest defined spatial rank and available category
examples. High ranks do not prove significance. Label shuffling does not test individual
genes. Gene/count and gene/mitochondrial Spearman correlations flag potential confounding.

### 4. Independent verification: `04_verify.py`

```bash
"$PY" spatial/run_analysis.py verify "$RUN"
```

Expect `passed: True` in `$RUN/verification.json`. Checks include raw QC with h5py instead
of Scanpy, retained barcodes, matching tissue labels, independent pairwise lattice edges,
edge agreement, every seeded null value and inclusive tail count, candidate expression
from raw counts, Moran's I via edge sums, and Kruskal–Wallis via rank sums/tie correction.
Input/evidence hashes and required figures are checked too. This does not certify visual
alignment, biological identities or scientific conclusions.

Completed files are sealed by hashes. Input/evidence changes stop later stages; do not
edit manifests to bypass this. Subsequent stages execute the run's saved code snapshot.
A failed stage can be retried with the same command after fixing the cause; prior completed
evidence is preserved. For software fixes affecting computation, create a new run.

## Task 3 status

Submission run `20261029T222440220672Z` was accepted on 2026-10-29 (analysis agent `claude-haiku-5-5`;
review in `REVIEW_NOTES.md`; audit trail in `AGENT_LOG.md`). Curated records are in
`records/20261029T222440220672Z/`; figures and tables in `figures/20261029T222440220672Z/` and `tables/20261029T222440220672Z/`.

Remaining, as part of the combined deliverable (`CLEAN_RUN.md` section 6):

1. Write the Task 3 section and Agent Audit of `report.pdf`, mapping the report's T1–T5
   headings to the rubric checkpoints (see `RUBRIC.md`).
2. Use the corrected `RESULTS.md` and concise `HANDOFF.md`. The saved review script
   reproduces the cluster-mean and QC-confounding checks; retain its code with the audit.
3. Keep the discussion limited to the data: no external sources were retrieved, so no
   anatomy or gene-function claims. Note spatial QC confounding, one-section generality and
   mixed-cell spots.
