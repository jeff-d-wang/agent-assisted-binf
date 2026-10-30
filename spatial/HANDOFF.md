# Task 3: reviewed findings for the report

Run: `20261029T222440220672Z`. Analysis agent: Claude Haiku (`claude-haiku-5-5`),
chosen by the user for budget reasons. The user reviewed the plan, QC, resolution
choice and draft, sent feedback, accepted revision 1 and confirmed the tissue overlay
looked aligned. Codex maintained the software and edited this summary.

## What the data support

QC retained 2,668 of 2,702 spots. Expression-only clustering used 2,000 HVGs, 30 PCs,
15 neighbors and seed 42. The user approved resolution 0.5 before cluster tissue maps
were produced. It gives 14 clusters of 29 to 338 spots. QC tissue maps were available
earlier; those are different from cluster tissue maps.

| Check | Result |
|---|---|
| Physical graph | 7,679 undirected edges; 3 components; degree 1 to 6; no isolates |
| Same-cluster edge fraction, resolution 0.5 | 0.7800 |
| Mean under 999 size-preserving label shuffles, seed 42 | 0.0879 |
| Excess over null mean | 0.6922 |
| Empirical upper tail | 0.001, the minimum possible with 999 shuffles |
| Edge fraction at resolutions 0.3 / 0.8 | 0.8258 / 0.7806 |

Expression-derived labels are spatially coherent. The global shuffle does not preserve
expression or quality gradients, so this result does not establish anatomical domains
or biological organization beyond smooth variation. Quantile partitions of counts and
mitochondrial fraction give much lower agreement (0.1403 and 0.1737), but quality
confounding remains possible.

## Same genes, different rankings

The 200 candidates were selected by expression dispersion before spatial analysis.
Moran's I measures neighboring expression similarity. Kruskal-Wallis H measures
between-cluster differences; it is descriptive because expression also defined clusters.

| Gene | Moran's I | H | Spatial / DE rank | Interpretation |
|---|---|---|---|---|
| Prkcd | 0.902 | 1162.8 | 1 / 14 | Strong on both measures |
| Pmch | 0.866 | 701.6 | 2 / 73 | Expression spans clusters 5, 9 and 4; consistent with a spatial pattern crossing cluster boundaries |
| Dnali1 | 0.263 | 1077.2 | 140 / 23 | Highest mean in cluster 12; a narrow group can separate expression distributions without high neighbor similarity |
| 2900040C04Rik | 0.704 | 431.9 | 14 / 116 | Highest mean in cluster 12, not broadly shared across clusters; the explanation for its rank difference remains a hypothesis |
| Gm4952 | -0.0025 | 11.7 | 200 / 199 | Detected in only 0.41% of spots; describe as sparse, not uniformly expressed |

The same 56 spots form cluster 12 at the primary resolution and matching groups at
0.3 and 0.8. Of 240 unique edges touching this group, 83 stay inside it (34.6%).
Counting edge endpoints instead gives 51.4%; specify the denominator. These counts
support describing a narrow spatial group, not an anatomical identity.

## What the user changed through review

The user corrected PC30 variance (0.20%, not 2.0%), the evidence-history claims,
missing QC-confounding checks and sparse-gene wording. A follow-up check refuted
Haiku's suggestion that 2900040C04Rik broadly overlaps clusters. The H value is 431.9,
not 400. Cluster 13 contains 29 spots; "13-spot group" was another wording error.

All pipeline verification checks pass. `review/check_task3.py` now reproduces the
additional graph, coordinate, seed-7 null, QC-covariate and cluster-mean checks without
importing pipeline code. No literature was retrieved and no cell-type, anatomical or
gene-function identity is established. One section, seed and parameter set limit inference.

Full evidence: `records/20261029T222440220672Z/`, `tables/20261029T222440220672Z/`,
`figures/20261029T222440220672Z/` and `REVIEW_NOTES.md`. Original API exchanges remain
in the local run. See `../PRE_DELIVERABLE_REVIEW.md` for packaging and provenance.
