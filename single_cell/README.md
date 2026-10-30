# Task 2: standalone Claude single-cell workflow

Start with [HANDOFF.md](HANDOFF.md) for the accepted findings, review corrections and
remaining limits. The user was the human reviewer; Claude was the analysis agent.
The original runs remain local evidence; final packaging is still pending.


Claude proposes and defends the analysis, chooses QC thresholds after seeing the distributions,
and interprets computed markers and robustness tests. Python executes the approved settings.
Codex developed this software; it is not a runtime analyst or intermediary.

**Current state (2026-10-29):** fresh runs use `claude-sonnet-5-5`. Earlier runs and matching
figures/tables were archived under `archive/2026-10-29-before-sonnet/`, preserving their
original models, drafts and recovery records. Use the accepted submission run for packaging; the commands below also support deliberate new runs.
See [the end-to-end checklist](../CLEAN_RUN.md). The submission run has been reviewed and accepted; final packaging remains pending.

## Run it on this laptop

Start a terminal in the repository:

```bash
cd /Users/jeffwang/VSCode_Workspace/agent-assisted-binf
python single_cell/run_analysis.py --config single_cell/config.json --check
```

That Python already has the tested packages. `--check` checks imports, input existence and hashes;
it neither calls Claude nor analyzes cells. The system Python may lack these dependencies.

On another machine, use a Python 3.9 or 3.10 environment and install:

```bash
python -m pip install -r single_cell/requirements.txt
```

The root `requirements.txt` installs these same pins together with those for Tasks 1 and 3;
Task 3 adds only h5py. Full installed versions are recorded in each run's `inputs.json`.
Do not upgrade packages during a run. The code supports the supplied 10x v2 human count files.
If they are missing, use the plan's extraction command once:

```bash
tar -xzf datasets/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -C datasets/pbmc3k
```

Set your Anthropic API key in your terminal. In zsh, this avoids displaying it or putting its
value in shell history:

```zsh
read -rs 'ANTHROPIC_API_KEY?Anthropic API key: '
export ANTHROPIC_API_KEY
```

The model ID in `single_cell/config.json` is `claude-sonnet-5-5`, matching the other tasks.
Preflight cannot validate your account/model access. Live requests incur API charges.

```bash
python single_cell/run_analysis.py --config single_cell/config.json
```

The program prints a unique `single_cell/runs/RUN_ID` directory. Keep that path.

1. **Review Claude's plan.** Read `PLAN.md` and its executable settings. Type feedback to revise,
   `approve` to compute QC only, or `quit` to pause. No tutorial settings are prefilled as an accepted plan.
2. **Review QC.** Open `qc_distributions.png`, `qc_joint.png`, and `qc_quantiles.csv` in the printed
   run's figure/table directories. Claude sees these plots before writing `QC.md`. Challenge thresholds
   that lack distribution-based justification. `approve` now runs the baseline and robustness analyses.
3. **Inspect computed evidence.** The scripts save sizes, UMAPs, full and top marker tables,
   resolution overlaps, and retained-cell downsampling comparisons. Independent numerical checks run.
4. **Review Claude's interpretation.** Claude receives focused evidence and completes separately
   saved annotations for each analysis run, an ambiguity investigation, then a report of at most
   1200 words (requested length). Annotation/investigation steps can retrieve PubMed abstracts and
   inspect expression/pairwise contrasts. The final report step uses saved evidence without new tools.
   Python then renders annotated UMAPs and `population_stability.csv` from the provisional labels.
5. **Challenge weak claims.** Type follow-up questions. Claude can revise annotations and the report
   using supported evidence tools. Changing preprocessing after execution requires a new run and review;
   a prose request cannot silently change scientific settings.
6. **Accept only after checking.** Type `accept`, then enter your independent check/result, an actual
   agent weakness and how you evaluated it, and remaining uncertainties. This saves `RESULTS.md` and
   `REVIEW.md`. Acceptance does not assign a grade or mark the course checkpoints complete.

Useful challenges:

- “Which labels have conflicting marker evidence? Compare the closest competing clusters.”
- “Does a split change the broad cell identity, or only its finer subdivisions? Give overlap fractions.”
- “Which small population loses stability after downsampling? State the retained-cell denominator.”
- “Does the cited abstract actually support this identity, or only expression of one marker?”

To resume after quitting or an API failure, replace `RUN_DIRECTORY` with the printed path:

```bash
python single_cell/run_analysis.py --resume RUN_DIRECTORY
```

Each completed tool result and response is checkpointed in `api/job_*.json`; validated interpretation
parts are saved in `interpretation_parts/REVISION/`. After a failure, resume skips complete parts
and reuses pending tool exchanges. A truncated answer is never accepted as a complete report.
Surrounding whitespace in QC field names is trimmed and logged; unknown fields, conflicting
names and invalid values still fail validation. Other schema errors are fed back on the next
resume; a retry may incur another charge. The tool loop is
bounded to twelve API responses per invocation of a part. Review feedback creates a new revision,
preserving earlier parts. Changed inputs, evidence or package versions stop resume.

If source code changes, use the run's saved runtime with the recorded environment: normally
`RUN_DIRECTORY/code/run_analysis.py --resume RUN_DIRECTORY`, or **`RUN_DIRECTORY/runtime/run_analysis.py`
for repaired runs**. Do not use a repaired run's old `code/run_analysis.py` to resume interpretation;
that code remains the historical record. Computation logs are saved per numbered script.

### Continue the fresh Sonnet run after QC recovery

Run `20261029T211700335443Z` returned `" min_genes"` with a leading space. The saved
proposal was recovered without changing thresholds/rationale or making another API call.
Its original code and response remain intact; `recovery/` records provenance and the prior
state, and `runtime/` contains the updated runner. That repair returned the run to QC review; the run has since been accepted. The historical resume command is:

```bash
python single_cell/run_analysis.py --resume single_cell/runs/20261029T211700335443Z
```

QC, clustering and human review have since completed. See HANDOFF.md for the accepted result.

### Historical interpretation repair

Historical recovery instructions only: this run is now archived. Restore its run directory
AND matching table/figure directories to their original locations before using these commands;
see the archive manifest. For the requested fresh Sonnet analysis, use the new-run command above.

From the repository root, with your API key already exported:

```bash
python single_cell/run_analysis.py --resume single_cell/runs/20261028T235728272943Z
```

This run has already been repaired. The next paid request is report writing, using the recovered
Claude annotations, investigation and retrieved sources. It does not repeat plan/QC approval,
clustering or downsampling. Review the resulting `DRAFT.md`, figures and tables; ask follow-ups to
correct unsupported claims, especially source relevance and any assertion of a biological continuum.

For an older, unrepaired run stopped at interpretation, the one-time offline command is:

```bash
python single_cell/run_analysis.py --repair RUN_DIRECTORY
```

Repair checks input/artifact integrity, compatibility of the scientific scripts and package versions,
and saved tool records. It preserves original code/API records, archives the old state/manifest/log
in `recovery/`, and installs a versioned runtime snapshot in `runtime/`. Only complete leading JSON
sections are recovered and validated; incomplete values are not reconstructed. Recovery records the
source response and hash, does not accept the biological claims, and makes no API calls. The report
is generated separately. Do not manually edit a sealed run to bypass validation.

## What is implemented, and what Claude chooses

The software supports one explicit method family, not arbitrary agent-generated code:
count QC → gene filtering → library-size normalization/log1p → Seurat dispersion HVGs →
centered scaling/clipping → arpack PCA → Euclidean neighbor graph → Leiden (`leidenalg`) →
UMAP → exploratory cluster-versus-rest Wilcoxon markers with BH correction.
Claude chooses normalization target, HVG count, PCs, neighbors, resolutions, gene filtering,
clipping and a 60–80% sample fraction within validated bounds, and defends the choices. It chooses
inclusive cell-QC thresholds only after the QC step. All scientific randomness uses seed **42**.
Unsupported methods require a software change; they are not silently claimed to have run.

Resolution comparisons reuse exactly the same representation, graph and UMAP. Downsampling
samples QC-passing cells without replacement, then reruns gene filtering, normalization, HVG
selection, PCA, neighbors, clustering, UMAP and markers. The actual integer sample size is the
floor of the chosen fraction times QC-passing cells. Comparisons align by retained barcodes.
The subsample UMAP is independently fitted; coordinates are not compared between the two runs.

Marker tests use all gene-filtered log expression, including genes outside the HVG set. Full
statistics are retained locally; the initial Claude evidence packet includes the top twenty
positive markers per cluster with adjusted p < 0.05. This cutoff selects evidence for inspection,
not a proof of identity. Claude can inspect additional named genes and pairwise contrasts.
Singleton/one-cluster cases remain explicitly untestable and uncertain. No predefined label map
is supplied. Non-uncertain annotations require at least two computed enriched markers and a
retrieved PMID; this checks traceability, not whether a paper actually supports the interpretation.

## Outputs

Metadata, transcript, cached expression and review files: `single_cell/runs/RUN_ID/`.
Figures: `single_cell/figures/RUN_ID/`. Tables: `single_cell/tables/RUN_ID/`.
All numerical tables and figures come from the scripts in this repository.

| Evidence | Files |
|---|---|
| Proposed workflow and reviewed QC | `PLAN.md`, `plan.json`, `QC.md`, `qc.json` |
| Inputs, software and exact code | `config.json`, `inputs.json`, `code/`, plan/rubric snapshots |
| QC and exclusions | `qc_cells.csv`, `qc_quantiles.csv`, `qc_decisions.csv`, `filter_summary.json`, QC plots |
| Baseline and each alternative | `cells_*.csv`, `sizes_*.csv`, `markers_*.csv`, `top_markers_*.csv`, `umap_*.png` |
| Representation | `hvg_*.csv`, `pca_variance.csv`, `pca_variance.png` |
| Cluster robustness | `robustness_metrics.csv`, `cluster_overlaps.csv`, `overlap_*.png` |
| Claude's labels and their agreement | `annotations.csv`, `annotated_cells_*.csv`, `annotated_umap_*.png`, `population_stability.csv` |
| Ambiguity investigation | `investigation_*_expression.csv`, optional `*_pairwise.csv`, investigation PNG and saved tool JSON |
| Retrieved biology | `data/pubmed_*.json`, `data/pubmed_*.xml` (queries, dates, URLs, titles/abstracts) |
| Interpretation and human audit | `DRAFT.md`, `interpretation.json`; accepted `RESULTS.md`, `REVIEW.md`; `AGENT_LOG.md`, `events.jsonl`, `api/` |
| Verification | `manifest.json`, `verification.json` |
| Interpretation/recovery progress | `interpretation_parts/`, `api/job_*.json`; repaired runs: `recovery/`, `runtime/` |

The numbered execution order is `01_qc.py` → `02_cluster.py` → `03_compare.py` → `04_verify.py`.
The runner executes the first three as reviewed stages and invokes the verifier; it reruns
`03_compare.py --annotations` whenever Claude's annotations change.

## Verify results yourself

Run the independent verifier after computation:

```bash
python single_cell/run_analysis.py --verify RUN_DIRECTORY
```

It checks raw-input and saved-evidence hashes; recomputes total counts, detected genes and
mitochondrial fractions directly from the Matrix Market file without Scanpy; checks filtering,
seeded subsample membership, cluster sizes and barcode alignment; and recomputes ARI using the
contingency-table formula independently of scikit-learn. It verifies overlap counts/fractions
and resolution embedding identity. These checks are necessary but do not establish the biology.

Then inspect these five things:

1. **S1:** Compare `QC.md` to QC plots and exclusion counts. Threshold failures overlap, so their
   individual counts need not sum to total excluded cells. Inspect PCA variance and cluster sizes.
2. **S2:** For each important label, find its genes in `top_markers_*.csv` or the full marker table.
   Check effect direction and detection fractions, inspect conflicting genes, and read the saved
   source abstract or linked paper. A PMID being retrieved does not make the claim supported.
3. **S3:** Read `cluster_overlaps.csv`. `fraction_of_baseline` shows splits; `fraction_of_other`
   shows merges. Each denominator uses shared cells. Assess identities as well as cluster ARI/NMI;
   low cluster agreement need not imply loss of broad population identity.
4. **S4:** Compare only `cells_downsample.csv` barcodes with baseline. In `population_stability.csv`,
   supported label agreement is the fraction of shared cells assigned the same label with neither
   annotation uncertain. Unresolved fractions are reported separately; zero retained cells gives a
   missing fraction, not an assertion of stability or instability. No arbitrary pass/fail cutoff is imposed.
5. **S5:** Inspect the actual investigation expression table/plot and any pairwise contrast. Check
   whether Claude's explanation is consistent with shared markers, QC, sample size and parameter
   sensitivity. A continuum is a possible explanation, not established by a UMAP alone.

To check the software without an API key or analyzing PBMC3k:

```bash
python -m unittest discover -s single_cell -p 'test_*.py' -v
```

These tests create temporary synthetic count data and mocked Claude responses. They do not
produce course findings. See `VALIDATION.md` for the checked scope.

## Remaining deliverable work

Use accepted run `20261029T211700335443Z`. The user has reviewed its labels, robustness
results and ambiguity investigation, sent feedback and accepted the revised report.
`HANDOFF.md` summarizes the findings and limits; `REVIEW_NOTES.md` records the checks.

1. Curate the selected report, review, settings, sources, code and small outputs as described
   in `CLEAN_RUN.md` section 6. Keep original runs locally; exclude credentials and large caches.
2. Write the Task 2 discussion and audit using readable numbered UMAPs, overlap counts and
   ARI/NMI. Keep weak source support and omitted planned checks visible. Exact-text label
   agreement is not biological stability evidence.
3. Freeze the environment, add report evidence references and reassess the rubric against
   the packaged deliverable. S2 still needs stronger source support or appropriately limited claims.

Limits: one donor/sample and one subsampling draw; p-values are exploratory because clusters and
markers come from the same cells; no automatic doublet classification; PubMed access is abstract-level;
Claude responses may vary and need review. Parameter bounds are implementation limits, not scientific
proof that every allowed choice is appropriate. The repaired staged report generation has been
tested with mocked responses and exercised by the accepted submission run. Preserve the documented scientific limits.

Implementation references (software documentation, not evidence for cell identities):
- https://scanpy.readthedocs.io/en/1.9.x/generated/scanpy.pp.highly_variable_genes.html
- https://scanpy.readthedocs.io/en/1.9.x/generated/scanpy.tl.rank_genes_groups.html
- https://scanpy.readthedocs.io/en/1.9.x/generated/scanpy.tl.leiden.html
- https://platform.claude.com/docs/en/api/messages/create
- https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost
