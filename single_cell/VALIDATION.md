# Task 2 software validation — 2026-10-28

Codex performed software validation, not biological analysis. Initial development used synthetic
counts and mocked agent responses. The subsequent user-run Claude analysis and its recovery are
documented below; scientific conclusions remain provisional until human review.

Environment: `/Users/jeffwang/miniforge3/bin/python`, Python 3.9.15; Scanpy 1.9.8,
AnnData 0.10.5.post1, NumPy 1.25.2, pandas 1.4.2, SciPy 1.13.1, Matplotlib 3.9.4,
scikit-learn 1.1.1, igraph 1.0.0, leidenalg 0.12.0, umap-learn 0.5.5,
pynndescent 0.5.11, numba 0.59.0. These are the local versions checked by preflight.

Reproduce:

```bash
/Users/jeffwang/miniforge3/bin/python single_cell/run_analysis.py --config single_cell/config.json --check
/Users/jeffwang/miniforge3/bin/python -m unittest discover -s single_cell -p 'test_*.py' -v
```

The preflight passed for all three supplied, extracted PBMC3k files. It checks hashes and
dependency imports only; no PBMC3k observations or scientific results are claimed from that check.

Initial implementation result: **all five original tests passed**. Python compilation and whitespace
checks also passed. Synthetic QC, annotated UMAP, overlap and investigation figures were visually
inspected and readable.

The tests exercise:

- Rejection of invalid/unsupported settings, NaN, booleans used as numbers, and out-of-range subsampling.
- Barcode alignment despite reordering and renamed clusters; ARI 1 for equivalent partitions and
  -0.5 for a crossed four-cell partition; rejection of foreign cells.
- Truncated API responses retained for audit without replacing conversation state.
- Unsupported API tools returned as errors without executing arbitrary commands.
- Complete staged workflow on a generated **180-cell × 300-gene synthetic count matrix**, with
  mocked Claude plan/QC/report responses. Seed 42; 150 HVGs, 5 PCs, 8 neighbors, resolutions
  0.3/0.6/1.0, 70% sampling. These are test-fixture values, not proposed PBMC3k settings.
- No QC before plan approval; no clustering before QC approval; pause/resume; report acceptance
  requiring human audit notes; resuming a failed annotation-rendering step without a new API call.
- Independent raw-matrix QC checks for 180 cells; 179 retained after deliberate synthetic mitochondrial
  contamination; 125 sampled cells; three independently checked ARI comparisons and overlap fractions.
- All-uncertain labels giving zero supported-label agreement, rather than a false claim of stability.
- Rejection of unretrieved citations and detection of deliberate table tampering by hashes and numerical checks.

Synthetic figures are inspected for readability during development; they are not course evidence.
No API credentials or real Claude response are used by the tests. Deprecated NumPy/pandas API warnings
from this existing environment do not indicate test failures.

At initial implementation, live Claude/API retrieval and PBMC3k computation had not been tested.
The later user-run session exercised those paths, revealing an output-limit/recovery defect.
Numerical verification still does not validate literature interpretation or prove that a population is real.

## Interpretation/recovery repair — 2026-10-28

The user's run `20261028T235728272943Z` completed computation and tool retrieval, then its sixth
API response ended with `max_tokens` at 24,000 output tokens. The old runner rejected the incomplete
report correctly but did not checkpoint the interpretation conversation. Its status log remained stale.

The repair separates per-run annotations, ambiguity and report writing, checkpoints individual tool
results and completed responses, and updates the audit from saved state even on failure. The report
request uses a fresh context with saved evidence, asks for at most 1200 words and has no new tools.
The output ceiling remains 24,000 tokens; no arbitrary cost-limit increase was made.

**All nine tests passed** after the repair, including the original end-to-end synthetic calculations
and these recovery cases:

- A truncated response preserves the completed search; resume does not repeat that tool.
- An interruption between two tool calls preserves the first result and executes only the second.
- A completed response is reused without a new API call.
- Incomplete JSON values are never reconstructed; duplicate keys are rejected.
- Offline repair preserves original code and the API response, and recovers only validated complete fields.
- Failure during final report writing leaves all annotation/investigation parts saved; resume requests only the report.
- The audit reports the actual saved `interpret` stage after an exception.

Applied the offline repair to the real run without API calls or scientific recalculation. It recovered
**25 provisional Claude annotations across four analyses plus one ambiguity discussion**. The truncated
report was not accepted. Original code/API files remain in place; old state, manifest and audit are
archived under `recovery/`; the repaired runtime is under `runtime/`.

Real-run checks after repair:

- All **102 original manifest entries** are preserved, using the archived original state for its entry.
- Independent verification passes: 2,700 raw cells; 2,673 retained; 1,871 sampled; three ARI comparisons.
- A no-network dry run stops exactly at the next report request, with tool use disabled and no
  recomputation or repeated annotation request. Its prompt is 97,674 characters; this is a character
  count, not a token estimate.
- Python compilation and whitespace checks pass. The scientific scripts and dependency requirements
  were not changed by this repair.

Pending: the next live report response, human assessment of source relevance and annotation quality,
and final acceptance. A short requested report can still hit an API limit; if it does, the saved parts
and tool exchanges now survive and the retry is limited to the incomplete part.

API reference consulted for output/thinking budgeting:
https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost

## QC field whitespace recovery — 2026-10-29

All **11 tests passed** with writable temporary Matplotlib/Numba caches, including two new
regressions: trimming QC field whitespace without changing values or the original response,
rejecting conflicting/unknown fields and invalid values, and saving the normalized proposal
while retaining the original conversation and user approval gate. The full synthetic
review/resume/verification and earlier recovery tests also passed.

Recovered run `20261029T211700335443Z` from its complete saved `api/002.response.json`:
only `" min_genes"` became `"min_genes"`. Original sealed evidence was hash-checked,
with old state retained under `recovery/`; original API records and code remain intact.
A dry resume with API/computation functions blocked successfully paused at QC review.
No scientific recalculation, paid API request, or automatic QC approval occurred. Live
downstream Sonnet analysis and scientific assessment of its proposed filters remain pending.
