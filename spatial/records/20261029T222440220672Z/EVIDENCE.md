# Task 3 computed evidence

Python computed these results from local inputs. Haiku subsequently interpreted them, and the user reviewed and accepted the report. See RESULTS.md and REVIEW.md for the reviewed interpretation.
Settings and QC: config.json, qc_review.json, cluster_review.json, filter_summary.json.
Input hashes and package versions: inputs.json; complete environment: code/requirements.lock.txt.

- Retained spots: 2668; primary resolution: 0.5; clusters: 14.
- Physical edges: 7679; isolated spots: 0; components: 3.
- Same-cluster edge fraction: 0.780049; null mean: 0.087873.
- Empirical upper-tail proportion: 0.001 from 999 seed-42 label permutations.
- Candidate genes: 200; rankings are descriptive, with undefined results retained.

Figures: /Users/jeffwang/VSCode_Workspace/agent-assisted-binf/spatial/figures/20261029T222440220672Z
Tables: /Users/jeffwang/VSCode_Workspace/agent-assisted-binf/spatial/tables/20261029T222440220672Z

## Scope of the reviewed interpretation
The user reviewed the statistic, effect size, quality gradients, alignment, ranking examples and
resolution sensitivity. The primary result was selected from expression diagnostics before tissue
cluster maps. The report separates observations, agent inferences and external support.
Do not assign anatomical or cell-type labels without evidence. Global label shuffling does not rule out
technical spatial artifacts; this is one section, and spots can mix cell types. Gene ranks are not gene tests.
The independent verifier passed. Review corrections and remaining uncertainties are recorded in
REVIEW.md and the task-level REVIEW_NOTES.md.
