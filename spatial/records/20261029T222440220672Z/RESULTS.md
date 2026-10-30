# Mouse-brain Visium: reviewed spatial organization report
> Editorial update, 2026-10-29: the user reviewed and accepted the analysis. Codex corrected attribution, status wording and documented errors for the handoff. The original model responses remain in `api/`; this edited report is not a verbatim model response. See `DOCUMENTATION_UPDATE.md` and the task-level `HANDOFF.md`.


## Evidence labels
- **Observed**: values in the supplied tables, metadata, figures, or the QC/cluster review text.
- **Reviewer-computed**: numbers supplied through the user's human review on 2026-10-29. These were separate from the pipeline verifier; `spatial/review/check_task3.py` now reproduces the additional numerical checks.
- **Inference**: my interpretation. Labelled as such.
- **External support**: none retrieved. The retrieved_sources list is empty. No anatomical, cell-type, or gene-function claim is made.

## T1. Methods and QC
- **Observed**: the raw matrix has 2702 in-tissue spots, 32285 genes, 13 mitochondrial genes, and no zero-count spots.
- **Observed**: QC was chosen after the QC plots and recorded thresholds: min_counts 5000, min_genes 2000, max_counts 100000, max_genes 10000, max_pct_mt 30. The QC review cites the 1%, 99%, and 99th-percentile values that motivated these cut-offs.
- **Observed**: 2668 spots were retained (34 removed). Failure counts are non-exclusive: low_genes 10, high_genes 7, low_counts 9, high_counts 11, high_mt 11. Genes with at least 3 spots: 19622. Clustering used 2000 expression-only dispersion HVGs, 30 PCs, 15 neighbours, and scale_max 10.
- **Observed**: the QC tissue maps (total_counts, n_genes_by_counts, pct_counts_mt) were supplied with the QC request. High-count and high-gene spots form broad regions. Elevated mt occurs along the left edge and in a curved band.
- **Inference**: these spatial QC patterns can reflect tissue quality, cell composition, or section-edge effects. QC cannot separate these causes, so high-mt spots were retained and not assumed damaged.

## T2. Matching expression and tissue labels
- **Observed**: the primary resolution is 0.5, with 14 clusters of sizes 29 to 338 (sum 2668, matching the retained spot count). Resolution 0.3 gives 10 clusters (minimum 56) and 0.8 gives 16 clusters (minimum 56).
- **Observed**: ARI is 0.787 between 0.3 and 0.5, and 0.732 between 0.3 and 0.8.
- **Observed (PCA)**: the variance ratio falls from 10.1% on PC1 to 0.20% on PC30 (reviewer-corrected; the earlier draft said 2.0%). The table shows no sharp elbow, so the configured 30 PCs were kept.
- **Observed (ordering)**: per the human reviewer, the cluster-approval log entry (22:39:04 UTC) precedes the tissue cluster-map write (22:39:09 UTC), and the earlier image set contained only the three UMAP images. I have not independently inspected these logs. The earlier statement that the ordering could not be confirmed is withdrawn on this basis.
- **Observed**: a group of 56 spots with identical summary statistics (median counts 41122, median mt 11.49) appears as cluster 9 at 0.3, cluster 12 at 0.5, and cluster 15 at 0.8.
- **Inference**: this suggests the same spots persist across resolutions. It is not a biological claim.
- **Observed**: 0.5 cluster 13 has 29 spots, median counts 66059, and median mt 9.12. In the UMAP it is an isolated light-green tail at the bottom.
- **Reviewer-computed**: cluster 13 forms a thin continuous arc on tissue that coincides with the high-count arc in the QC total_counts map. This is described as observation only, not anatomy.
- **Inference**: cluster 13 may reflect quality or depth rather than a biological group. Its size makes it vulnerable to small-group or mixed-spot effects.

## T3. Numerical statistic and graph
- **Observed**: the graph uses original Visium lattice offsets (0, plus or minus 2) and (plus or minus 1, plus or minus 1). It has 2668 spots, 7679 undirected edges, 0 isolated spots, 3 connected components, and degree 1 to 6. Weights are binary and symmetric, with no bridging of missing sites.
- **Observed**: the statistic is the fraction of physical edges whose two endpoints share a cluster label. At 0.5 the observed value is 0.780.
- **Inference**: the statistic depends on both the lattice graph and the partition. It is not graph-free.

## T4. Effect size and null comparison
- **Observed**: 999 label shuffles on the fixed graph, preserving cluster sizes. Null mean 0.0879 (SD 0.0032; 2.5 to 97.5 percent range 0.0818 to 0.0938). Analytic expectation 0.0881. No null value reached 0.780. The empirical upper tail is 0.001, which is the resolution limit of 1/1000.
- **Observed**: excess over the null mean is 0.692.
- **Observed sensitivity**: edge agreement is 0.826 at 0.3 (10 clusters), 0.780 at 0.5 (14, primary), and 0.781 at 0.8 (16).
- **Reviewer-computed**: partitioning into 14 quantile groups of total_counts gives edge agreement 0.14, and of pct_counts_mt gives 0.17, against 0.78 observed.
- **Reviewer-computed (QC covariates at cluster level)**: Kruskal-Wallis H across the 0.5 clusters is 983 for pct_counts_mt and 748 for total_counts. Moran I is 0.55 for pct_counts_mt and 0.45 for total_counts. The reviewer estimates these H values would rank about 35th and 66th among the 200 candidates. The original agent packet did not include these covariate statistics; the independent review script now reproduces the values and ranks.
- **Inference (what each statistic measures)**: H measures between-cluster separation of a gene's expression distribution. Moran I measures similarity between a spot and its lattice neighbours, regardless of cluster. A gene can score high on one and low on the other.
- **Inference (null meaning)**: the global label shuffle shows that labels are not randomly placed on the section. It cannot separate organisation beyond smooth expression or depth variation, because shuffling does not preserve spatial autocorrelation of expression or QC covariates. The low quantile-partition agreement argues against a simple depth or mt explanation of the 0.78 value, but a shared smooth spatial gradient remains possible.

## T5. Candidate genes, maps, and same-gene DE/spatial examples
- **Observed method**: 200 candidates from expression-only Seurat-style normalised dispersion, frozen before spatial analysis. Moran I uses binary weights with no isolates. Descriptive tie-corrected Kruskal-Wallis H uses all 2668 retained spots across the frozen clusters. No DE p-values are reported, because the clusters are expression-derived.
- **Observed ranks** (spatial rank / DE rank): Prkcd (1/14; Moran 0.902; H 1162.8); Pmch (2/73; Moran 0.866; H 701.6); Tcf7l2 (3/4); Gm4952 (200/199; Moran -0.0025; H 11.7).
- **Observed example categories**: strong_both (Prkcd); strong_de_weak_spatial (Dnali1: spatial 140, DE 23); strong_spatial_weaker_de (2900040C04Rik: spatial 14, DE 116). The example file lists only these three categories. Any other category is absent from the supplied output and is not treated as zero or as an empty class.
- **Observed maps**: Prkcd has a high-expression contiguous patch in a central-left portion of the section. Pmch has a patch in a lower-left portion. Dnali1 and 2900040C04Rik show narrow, localised streaks. Gm4952 is sparse, detected in only 0.41% of spots.
- **Observed confound checks** (Spearman): Prkcd rho_counts -0.103, rho_mt 0.071; Pmch rho_counts 0.183, rho_mt -0.186; Dnali1 rho_counts 0.099, rho_mt -0.196.
- **Reviewer-observed (Gm4952)**: detected in 0.4 percent of spots (0.0041). Its bottom rank is best described as a sparsity effect. Ten candidates are detected in under 1 percent of spots: Igha, Ccl4, Cxcl10, Cyp2f2, Qrfp, Pitx1, Fndc3c1, Tfec, Atp8b4, and Gm4952.
- **Discordant genes (review follow-up)**: Haiku did not receive `gene_cluster_means.csv` in its report packet, so its original explanations were hypotheses. The user checked the table afterwards: Dnali1 and 2900040C04Rik peak in cluster 12 (mean log expression 0.49 and 1.04; next-highest 0.03 and 0.14). Of 240 unique physical edges touching that group, 83 are internal (34.6%). Dnali1 has Moran I 0.263 and H 1077.2; a narrow group is consistent with high between-cluster separation but lower neighbor similarity. For 2900040C04Rik, Moran I is 0.704 and H is 431.9, not 400. The proposed broad overlap across clusters is unsupported; a patch within the narrow group remains a hypothesis. Pmch spans clusters 5, 9 and 4 (means 2.47, 1.19 and 0.96), consistent with a spatial pattern crossing cluster boundaries. These observations do not establish biological mechanisms.
- **Caveat**: candidates were selected from the same expression features used for clustering. Cluster-derived DE is not independent confirmation.

## Limitations
- One section, one seed, one parameter set. No replicate.
- Clusters are derived from expression, so spatial agreement can reflect expression continuity or QC gradients.
- Global label shuffling does not preserve spatial autocorrelation and cannot establish spatial organisation beyond smooth variation.
- Small clusters (cluster 13 at 0.5; the 56-spot group) may be artifacts.
- Moran I and H are descriptive; gene ranks are not significance tests.
- No atlas, reference labels, or retrieved literature were used. Anatomical identity is unassessed.

## Qualified answer to the scientific question
On this single section, the 0.5 expression-derived partition shows strong spatial label coherence: 78 percent of physical edges join same-cluster spots, against about 9 percent under a global shuffle. Resolution changes move edge agreement only modestly (0.78 to 0.83). Quantile partitions of depth or mt give much lower agreement (0.14 to 0.17), which argues against a simple depth or mt explanation of the coherence. Several candidate genes show strong spatial autocorrelation and high DE ranks, while others diverge. Whether these patterns reflect biology, tissue quality, or smooth expression gradients cannot be decided from these outputs. No anatomical or cell-type identity is established.

## Draft audit
- **Resources (actual)**: input_dir visium_mouse_brain; counts file V1_Adult_Mouse_Brain_filtered_feature_bc_matrix.h5; tables path spatial/tables/20261029T222440220672Z; figures path spatial/figures/20261029T222440220672Z; config model claude-haiku-5-5; seed 42.
- **Retrieved sources**: none (retrieved_sources list empty; pmids empty).
- **Numerical verifier scope (verification.json, passed)**: checked 2702 raw spots, 2668 retained spots, 7679 edges, 999 nulls, 200 gene statistics, input and artifact hashes, h5py QC, barcode join, lattice graph, edge agreement, seeded null and ties, candidate normalisation, Moran edge sum, and tie-corrected Kruskal-Wallis. Scope is numerical only; it is not visual alignment or biological validation.

| Claim | Status |
|---|---|
| QC counts, thresholds, retention | Observed (tables and QC review) |
| Resolution 0.5 choice and ordering | Observed diagnostics; ordering per reviewer log timestamps, not independently inspected |
| PC30 variance 0.20% | Reviewer-corrected |
| Edge agreement 0.780 vs null | Observed |
| Resolution sensitivity | Observed |
| Quantile-partition agreement 0.14 and 0.17 | Reviewer-computed |
| QC covariate H (983, 748) and Moran (0.55, 0.45) | Human-review calculation; values and ranks reproduced by the review script |
| Gene ranks and examples | Observed |
| Gm4952 detection 0.4 percent; 10 candidates under 1 percent | Observed (Gm4952 and the 10 are from fraction_detected) |
| Cluster 13 arc on tissue | Reviewer observation of QC map; not anatomy |
| Discordant-gene explanations | Human follow-up checked cluster means; biological explanations remain hypotheses |
| Anatomy, cell type, gene function | None claimed; unresolved; no retrieved support |

- **Unresolved claims**: cluster means were checked after acceptance, but mechanisms remain hypotheses; null adequacy for spatial autocorrelation; 29-spot cluster 13 and 56-spot group interpretation; candidate overlap with clustering features; biological meaning of all gene patterns.
- **Human review and acceptance**: the user reviewed the plan and analysis outputs, sent one feedback round, accepted revision 1 and confirmed the tissue overlay against H&E looked aligned. Numerical checks are recorded in `REVIEW.md` and the task-level `REVIEW_NOTES.md`; visual judgment is separate from biological validation.

