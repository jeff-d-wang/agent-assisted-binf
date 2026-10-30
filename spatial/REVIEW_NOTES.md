# Task 3: human review notes

Run: `20261029T222440220672Z`. Analysis agent: `claude-haiku-5-5`.
Reviewer: the user (human), 2026-10-29. The user reviewed the plan, QC, resolution
choice and draft, sent one feedback round, accepted revision 1, and later confirmed
reading the report and checking the tissue overlay against H&E ("looks fine").

## What the user checked

The review followed PROJECT_PLAN and RUBRIC: compare the actual tables, plots,
settings and source records; separate observations from agent inferences; check a
number independently; identify unsupported claims and unresolved questions. No
literature was retrieved for this task, and no biological identity was established.

| Check | Evidence and outcome |
|---|---|
| Coordinates and graph | All 2,668 barcodes match raw positions; 7,679 edges, degree 1 to 6, no isolates. |
| Spatial coherence | Edge agreement reproduces: 0.825759 at 0.3, 0.780049 at 0.5, 0.780570 at 0.8. |
| Negative control | Saved upper tail is 0.001; null maximum 0.1017. A separate 999-shuffle check, seed 7, gives mean 0.0880 and SD 0.00325. |
| Resolution chosen before tissue maps | Request 003 contains three UMAP images; approval was at 22:39:04 UTC, the cluster tissue map at 22:39:09 UTC. |
| QC confounding | Mitochondrial fraction H 983.1, Moran I 0.551; counts H 747.7, Moran I 0.446. H would rank 35th and 66th among the 200 genes. Fourteen quantile groups give edge agreement 0.174 and 0.140, respectively. |
| PC30 | Variance ratio 0.0020185 means 0.20%, not 2.0%. |
| Stable small group | The same 56 barcodes occur at all three resolutions. At 0.5 they are cluster 12. |

The original extra checks used a scratch script that was not retained. Codex added
`review/check_task3.py` during the pre-deliverable review and reproduced the numerical
checks above. It imports no pipeline code and changes no run outputs. The user's
visual judgments remain separate from those calculations.

## Feedback and corrections

Haiku's first draft misstated the resolution/map ordering, questioned QC maps that
had been supplied earlier, reported PC30 variance tenfold too high, and omitted the
promised cluster-versus-QC check. The user also challenged its weak explanation of
DE versus Moran ranks, its description of Gm4952 as near-uniform, and its reference
to an undefined `weak_both` category. The plan and QC approvals occurred 4 and
16 seconds after the corresponding responses; these timestamps do not measure
review depth.

Revision 1 addressed most feedback. It introduced H=400 for 2900040C04Rik (actual
431.9) and retained one near-uniform description of Gm4952 (detected in 0.41% of spots).
The user accepted with these residuals recorded. The edited `RESULTS.md` now corrects
them and fixes "13-spot group" to "29-spot cluster 13". The original model text remains
in the local API records.

The user initially accepted the claim that QC tissue maps were absent, then checked
the saved request and corrected that mistake. Another review error was asking Haiku
to use `gene_cluster_means.csv` although the report packet omitted it. The model's
unverified explanations were therefore hypotheses, not computed findings.

## Follow-up on the gene-ranking disagreement

The user checked cluster means after acceptance. Dnali1 and 2900040C04Rik peak in
cluster 12 (mean log expression 0.49 and 1.04; next-highest 0.03 and 0.14). Of 240
unique edges touching that group, 83 stay inside it (34.6%). Counting edge endpoints
instead gives 51.4%; the denominator matters.

A narrow group is consistent with Dnali1's high H and lower Moran I. Haiku's claim
that 2900040C04Rik broadly overlaps clusters is unsupported. Expression in part of
the narrow group could explain its high Moran rank and lower H, but remains a
hypothesis. Pmch spans clusters 5, 9 and 4 (means 2.47, 1.19 and 0.96), consistent
with a spatial pattern crossing cluster boundaries.

## What remains uncertain

The shuffle cannot distinguish biological domains from smooth expression or
technical gradients. The identity of cluster 13 and the stable 56-spot group is
unknown. Gene-pattern mechanisms remain hypotheses. There is one section, seed
and parameter set. The user's visual alignment check does not establish anatomy.
