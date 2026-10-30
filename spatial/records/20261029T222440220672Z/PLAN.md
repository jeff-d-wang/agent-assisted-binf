## Verdict
Proceed with the supplied configuration. I found no parameter that is clearly inappropriate for this run, so I am not recommending a change. This is a plan review only. No analysis has run, no results exist yet, and no literature was retrieved, so I cite nothing.

## Question
Do expression-only clusters of Visium spots in this single adult mouse brain section form spatially coherent groups on the hexagonal lattice? Which candidate genes show spatial autocorrelation (Moran I) and differ across clusters (descriptive Kruskal-Wallis H)? Clusters are not checked against any reference labels, so anatomical identity is not assumed.

## Inputs
- Filtered 10x feature-barcode matrix (H5) from the V1 adult mouse brain dataset.
- Spot coordinates are used only for lattice adjacency and downstream spatial statistics. They do not enter clustering.

## Methods
1. Library-size normalization to 10,000 counts, then log transform.
2. Keep genes detected in at least 3 spots.
3. Select 2,000 HVGs by expression dispersion alone.
4. Scale with a maximum value of 10, then run PCA with 30 components.
5. Build a 15-neighbor expression graph, then run Leiden and UMAP. UMAP is for display only.
6. Test same-cluster agreement on immediate hexagonal neighbors against fixed-size label shuffles.
7. Compute Moran I and Kruskal-Wallis H for the same 200 expression-selected candidate genes.

## Parameters
- Seed 42.
- Leiden resolutions 0.3, 0.5 and 0.8.
- 999 randomizations.
- Mirrors the sensible defaults for this data type. The 3-spot gene filter is permissive and may keep sparse genes, which is acceptable because candidate ranking and spatial statistics are reported descriptively.

## Review stops
- QC is chosen only after QC plots are reviewed. Expected checks include total counts, detected genes and mitochondrial fraction per spot, to test whether clusters track technical quality.
- The primary resolution is chosen only from expression diagnostics (cluster stability and size distribution) before any tissue map is viewed.
- This plan requires review before execution. Any change to the configuration needs a new run.

## Null hypotheses
- Edge agreement: cluster labels are spatially unrelated to the lattice. Observed same-cluster neighbor agreement should match the fixed-size shuffled-label distribution.
- Moran I: a gene has no spatial autocorrelation. With 999 permutations, the smallest attainable p-value is about 0.001.
- Kruskal-Wallis H: a gene's expression distribution is the same across clusters. Results are descriptive ranks, not significance tests.

## Independent checks
None is available in this run. Cluster-derived DE and spatial statistics computed on the same clusters are not independent confirmation. No reference labels, external datasets or retrieved sources exist to test the clusters against. Any external check would need an explicit new input.

## Limitations
- Single section, so no replication across animals or sections.
- Quality confounding is possible, so clusters may reflect depth or mitochondrial content rather than biology.
- Isolated spots and small clusters may be unstable. Mixed spots at boundaries are expected in Visium.
- Only immediate hexagonal neighbors are used, so larger-scale structure is not captured.
- Resolution sensitivity is reported across 0.3, 0.5 and 0.8 rather than assumed away.
- Testing 200 genes across three resolutions creates multiplicity. Results will be descriptive and need adjustment or caution.
- Gene-function and anatomical interpretations remain unverified evidence gaps until supported by retrieved sources.
