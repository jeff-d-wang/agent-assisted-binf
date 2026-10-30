# Task 2 run audit

Status: qc_review; no automatic course grade or checkpoint completion.
Saved interpretation parts (revision 0): none.

- Claude is the scientific agent; Codex developed the software separately.
- Exact prompts, answers, model IDs and token usage: api/. Decisions and tool results: events.jsonl (UTC).
- Pending tool exchanges and completed responses: api/job_*.json; validated parts: interpretation_parts/.
- If repaired: original run state/manifest/log in recovery/; original scientific code in code/;
  repaired runtime in runtime/. Recovered annotations remain provisional Claude output.
- Proposed methods and defense: PLAN.md; thresholds and reasons: QC.md. Seed: 42.
- Inputs, SHA256, Python/package versions: inputs.json; executed code: code/.
- Computed evidence: /Users/jeffwang/VSCode_Workspace/agent-assisted-binf/single_cell/tables/20261029T211700335443Z, /Users/jeffwang/VSCode_Workspace/agent-assisted-binf/single_cell/figures/20261029T211700335443Z; numerical checks: verification.json.
- Retrieved evidence: data/pubmed_*.json and XML (titles/abstracts only, queries and retrieval dates).
- Agent inferences: interpretation.json and DRAFT.md; accepted report: RESULTS.md only after review.
- Independent checks: raw Matrix Market sums/detection/mitochondrial fractions and explicit contingency-table ARI.
- User's independent review, agent weakness and unresolved issues: REVIEW.md (pending until acceptance).
- Software tests are not biological validation. One fixed subsample, exploratory markers, no reference labels.

Evidence index: S1 QC/cells/sizes/UMAP/PCA and computation.json; S2 markers/annotations and retrieved sources;
S3 robustness_metrics.csv and cluster_overlaps.csv; S4 the downsample rows and membership;
S5 investigation tables/plot plus the ambiguity discussion. All require scientific review.
