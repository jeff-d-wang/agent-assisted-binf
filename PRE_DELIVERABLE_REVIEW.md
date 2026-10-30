# Review before deliverable preparation

Reviewed 2026-10-29. All three selected runs are accepted and pass their numerical
verifiers. The user was the human reviewer: they reviewed plans and outputs, checked
evidence, sent feedback and accepted the analyses. Sonnet analyzed Tasks 1 and 2;
Haiku analyzed Task 3. Codex's work here was software verification and documentation.

Section 6 can begin with the limits below carried into the report. No fresh live
analysis is needed just for packaging. The combined PDF has not been created.

## Start here

| Task | Short reader-facing summary | Detailed review | Accepted run |
|---|---|---|---|
| 1 | [Protein handoff](protein/HANDOFF.md) | [Review notes](protein/REVIEW_NOTES.md) | `4hjo_submission_20261029T200938399152Z` |
| 2 | [Single-cell handoff](single_cell/HANDOFF.md) | [Review notes](single_cell/REVIEW_NOTES.md) | `20261029T211700335443Z` |
| 3 | [Spatial handoff](spatial/HANDOFF.md) | [Review notes](spatial/REVIEW_NOTES.md) | `20261029T222440220672Z` |

The handoffs are concise summaries. Detailed reports, tables, sources and audit logs
retain the supporting evidence. Documentation edits use the humanizer skill and are
identified as editorial work, not new model responses or new scientific acceptance.

## Checks completed

- All three original run manifests matched before editing. Numerical verifiers pass:
  five protein candidates; 2,700 raw and 2,664 retained cells, 1,864 sampled cells and
  four ARIs; 2,702 raw and 2,668 retained spots, 7,679 edges, 999 null values and 200
  spatial gene statistics.
- All 89 CSV tables parsed. No numeric infinities were found. Four missing entries in
  protein contact/variant tables remain visible; no values were invented to fill them.
- All 42 PNG figures opened and were visually inspected for presentation. The protein
  labels overlap some structure; the single-cell annotation legends squeeze the UMAPs.
  This inspection is separate from the user's scientific and H&E review.
- Independent protein scripts reproduce mapping, distances to 0.01 Å and the near-cutoff
  G719/C797 burial checks. The SASA check runs inside PyMOL, not ordinary Python.
- Single-cell reviewer scripts reproduce QC, ARI/NMI, downsample denominators, marker
  fractions and exact DC barcode overlap. All 29 sampled DC-like cells belong to the
  same 36-cell group, with no extras.
- The spatial review now has a saved, read-only script, `spatial/review/check_task3.py`.
  It reproduces graph/coordinate checks, a separate seed-7 null, QC-confounding values,
  cluster means and the 56-spot group's membership. Its assertions pass.
- Report PMIDs were checked against saved source records. The protein structure citation
  is supplied by structural metadata, not a PubMed-tool retrieval. Key disputed protein
  mechanisms were reread in their saved abstracts. This pass did not retrieve full papers
  or re-adjudicate every biological claim; the user's source-review record and its limits
  remain part of the evidence.

## Clean-run issues and fixes

| Issue | Cause and consequence | Fix or current disposition |
|---|---|---|
| Task 1 hit its output limit | Reasoning and report text shared the old 16,000-token cap. | Already raised to 32,000 with a 360-second timeout; run completed. A larger cap is not a guaranteed cost or completion bound. |
| Task 1 lost evidence from the interrupted attempt | Retry restarted interpretation without the nine earlier searches in its active context. | User feedback recovered key sources and corrected the total to 29 queries. Future code should checkpoint the interpretation conversation, not just source files. |
| Pasted feedback was truncated | The runner reads one line, so only the first line of Task 1's initial feedback reached the agent. | User resent one complete line. A future fix is multiline/file input; current instructions explicitly say one line. |
| Task 2 QC proposal was rejected | Sonnet used `" min_genes"` with leading whitespace. | Validator now trims field whitespace and rejects collisions; the saved proposal was recovered without changing thresholds. Completed. |
| Task 2 Wilcoxon warnings | Genes absent in both compared groups produce an intermediate 0/0. Scanpy sets their score to 0 and p-value to 1. | Saved marker tables are finite; no rerun required. Do not suppress unrelated warnings indiscriminately. |
| Task 2 label-agreement scores mislead | Exact text matching treats synonymous B-cell labels as disagreement; tentative labels also count as resolved. | Exclude these columns from biological conclusions. Use barcode overlaps and reviewed labels. A future fix needs explicit human-reviewed label mapping or a clearly named exact-text metric, not fuzzy matching. |
| Annotated UMAPs are hard to read | Long legends occupy most of the figure width. | Use existing numbered UMAPs and a compact label table for the report, or rerender from saved coordinates with a separate legend panel. No reclustering is needed. |
| Task 3 invalid JSON | Haiku put literal newlines inside a quoted string; the response was complete and below the token cap. | Retrying corrected the response. Future fix: explicit escaping instructions or narrow, logged newline recovery followed by schema validation. |
| Task 3 `pause` became feedback | Only `quit` is a pause command; other text is treated as feedback. | State was restored offline with provenance. Use `quit`; a future fix is to recognize `pause` explicitly. |
| Agent lacked requested evidence | `gene_cluster_means.csv` exists, but Task 3's report packet omits it. | Human follow-up checked the table and corrected the interpretation. Future fix: supply the selected genes' cluster means in the report packet. |
| Report arithmetic and evidence errors | Protein misquoted Threonine 790 and overstated an L858R conformation; Task 2 used wrong denominators/comparators; Task 3 had a tenfold PCA error, wrong H value and sparse-gene wording. | User feedback fixed most errors. Edited reports now include the documented residual corrections; original model responses are retained. |
| Missing promised analyses | Task 2 did not perform per-cell doublet co-detection, Jaccard best matches or top-marker overlap. | Disclose the omissions. Existing overlap/ARI evidence remains useful; do not claim these planned checks were done. Implement and review them only if expanding scope. |
| Weak source support | Several cell labels cite disease-context or label-only abstracts. | Keep subtype labels tentative and describe evidence depth. Stronger sources would strengthen the report; canonical expectations are not computed validation. |
| Draft-status and reviewer errors | Accepted files retained pre-acceptance wording and incorrectly credited a model as reviewer. | Current reader-facing documents credit the user, identify acceptance, and record editorial changes. Raw API messages and superseded audit copies remain historical records. |
| Extra spatial checks lacked code | The original reviewer used an unretained scratch script. | Added and ran `spatial/review/check_task3.py`; numerical values reproduce. This is a reproducibility repair, not a new scientific-agent run. |
| Copied manifests are not portable | Original manifests include local absolute paths and files excluded from curated records. | Retain them as provenance, but create a repository-relative manifest for the actual submission in section 6. Task 3's existing copy needs that packaging step too. |

## Corrections to carry into the report

Protein: say **Threonine 790**, leave the L858R conformation unspecified where the
abstract does, and identify spheres as Cα atoms. C797S intrinsic activity is unknown;
absence of evidence does not establish a small effect. Relative B-factors are not
measurements of molecular dynamics. Keep drug, substitution and comparator specific.

Single-cell: use sampled baseline cells as downsampling denominators. CD4 detection in
the res_1p5 cluster 0 is 15.5% versus 10.9% in all other cells; the earlier 6.8% comparison
was to a sibling cluster. NKG7 detection in res_1 monocyte cluster 2 is 19.7%, not 22%.
The old CD4-like phrase remains only in a note recording its removal. DC membership
overlap is now checked; identity, mixtures and doublets remain unresolved.

Spatial: PC30 explains 0.20%; 2900040C04Rik H is 431.9; Gm4952 is detected in 0.41% of
spots; cluster 13 contains 29 spots. Both Dnali1 and 2900040C04Rik peak in cluster 12.
Its 34.6% internal-edge share uses unique touching edges as denominator; endpoint
counting gives 51.4%. The global shuffle establishes nonrandom label placement, not
biological domains independent of smooth technical or expression gradients.

## Remaining section 6 work

1. Curate Tasks 1 and 2 and check the already copied Task 3 records. Ship the current
   corrected documents and review scripts, not practice outputs, caches or raw transcripts.
2. Retain executed code plus any recovery runtime separately. Freeze the current Python
   environment and record the separate PyMOL environment; the root lock file is not yet present.
3. Select readable figures, add captions and build the portable submission manifest.
4. Write and render `report.pdf` with three task audits, limitations, sources and the
   checkpoint evidence index. Reassess the remaining rubric revisions and assign scores.

The pre-edit documentation and artifact hashes are preserved in
`archive/2026-10-29-before-deliverable-review/`. Each edited run has a
`DOCUMENTATION_UPDATE.md` explaining the changes and an updated integrity record.
No production analysis, live model call or new biological annotation was performed here.
