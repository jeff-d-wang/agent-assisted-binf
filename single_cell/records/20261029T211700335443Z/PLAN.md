# Plan and defense (pre-analysis; no data inspected, no QC thresholds chosen)

## What this plan answers
The question is which major PBMC populations are supported by markers derived from the data, and which conclusions survive two perturbations. The first perturbation is Leiden resolution, with the representation and graph held fixed. The second is a fixed-seed cell subsample, with the full pipeline rerun. A conclusion counts as *stable* only if it is recovered independently in each run from that run's own markers. I will not carry baseline labels forward by cluster ID.

## Workflow, in order
1. **QC evidence first.** Before setting any threshold, I will inspect the computed distributions of genes per cell, total counts per cell and mitochondrial fraction (MT- genes). I will look at their joint structure, including genes vs counts and the mito tail. I will then choose thresholds from the PBMC3k distributions, for example the low-complexity shoulder, the upper tail where doublets are plausible, and the mito tail separated from the bulk. I will record how many cells each threshold removes and justify each cut. No automatic doublet calling is available. I will treat very high gene or count cells as a possible doublet-like technical concern rather than label them.
2. **Gene filtering.** `min_cells_per_gene = 3`. This removes genes seen in almost no cells. They add noise and cannot support a marker for any population of realistic size. The threshold is low enough to keep genes from rare populations. About 3 cells out of ~2.7k is a conventional floor.
3. **Normalization.** Library-size normalization to `target_sum = 10000`, then log1p. This is the standard scale for 10x data with a median of a few thousand UMIs. The Wilcoxon markers then use all filtered log genes, not only HVGs.
4. **HVGs.** Seurat dispersion with `n_top_genes = 2000`. This is large enough to include lineage genes (T, NK, B, myeloid, platelet) and small enough to limit noise. Both baseline and subsample use the same count.
5. **Scaling.** Centered and clipped scaling, `scale_max = 10`. This stops a few highly expressed genes, such as platelet and myeloid genes in a few cells, from dominating PCs. It also keeps real signal from rare populations. No regression is used. Any residual library-size or mito effect will be checked, not removed.
6. **PCA.** ARPACK with `n_pcs = 30`. I will check the variance-ratio curve afterward for an elbow. Thirty PCs is deliberately a little generous. The aim is to avoid dropping weak but real axes, such as the DC or platelet axes. The cost is mild noise, and clustering on a kNN graph tolerates this. If the elbow is clearly earlier, I will say so as a limitation of the fixed setting. The setting is fixed now, so I cannot change it silently later.
7. **Graph.** Euclidean neighbors with `n_neighbors = 15`. This is a standard local scale. It resolves small groups (tens of cells) without fragmenting the continuum. The graph is built once and is shared by all resolutions.
8. **Resolution control.** `baseline_resolution = 0.6` and `resolutions = [0.3, 0.6, 1.0, 1.5]`. Only the Leiden resolution changes, with seed 42, the same PCA and the same graph. I will quantify the following:
   - the contingency table between adjacent resolutions on shared cells;
   - which parent clusters split, using the fraction of a child that comes from one parent;
   - which clusters merge;
   - ARI and NMI between resolutions.
   A *meaningful* change is a split that creates a child with at least about 5% of the parent's cells **and** its own marker set that differs from the sibling's. It is not meaningful if the split only renumbers cells or breaks a cluster into groups with the same markers.
9. **Annotation order.** For each cluster in each run:
   - (a) compute data-derived Wilcoxon/BH markers on all filtered log genes;
   - (b) read the top markers, together with the fraction of cells expressing them and the log fold-change;
   - (c) propose an identity from canonical-marker knowledge (for example IL7R/CCR7 for T cells, CD8A/GZMK for CD8 T cells, NKG7/GNLY for NK cells, MS4A1/CD79A for B cells, LYZ/CD14 for classical monocytes, FCGR3A/MS4A7 for non-classical monocytes, FCER1A/CST3 for DCs, PPBP for platelets);
   - (d) check retrieved PubMed abstracts only where they help, and cite only retrieved PMIDs;
   - (e) assign a final label, keeping it **uncertain** when markers are weak, shared or too few.
   I will annotate each run separately. Labels come from that run's markers and are matched across runs only through shared barcodes.
10. **Downsampling.** `sample_fraction = 0.7`, seed 42. I sample from the QC-passing cells only, then rerun gene filtering, normalization, HVGs, scaling, PCA, neighbors, Leiden and markers. I compare the retained cells with the baseline on shared barcodes by:
    - ARI and NMI;
    - the best-overlap cluster matching, using Jaccard similarity rather than numeric IDs;
    - the overlap between top marker genes;
    - whether each population's label is reproduced.
    I chose 0.7 because it is mid-range. It removes enough cells to perturb the graph, yet leaves enough cells to retain small clusters. At 0.7 a population of about 30 cells would drop to about 20. So rare populations, such as DCs or platelets, are the ones most at risk.
11. **Ambiguity investigation.** I will choose after seeing the data. The candidates are:
    - the CD4 T-cell subsets (naive vs memory) and the CD8/NK boundary, which are expected to be a continuum with shared markers;
    - a small cluster, such as DC or platelet, at risk from size or technical noise;
    - any cluster that splits or merges across resolutions or after downsampling.
    For the chosen population, I will run a pairwise Wilcoxon contrast against its nearest neighbor cluster. I will inspect selected genes, cluster size and QC covariates (counts, genes, mito fraction), and I will ask whether the boundary is a continuum. The contrast is exploratory.
12. **Independent checks.** (i) Compare the annotations with the canonical marker expression computed on the log matrix, but not used to drive clustering. (ii) Check whether clusters are driven by QC covariates, since no regression is used. (iii) Compare the subsample result with the resolution result: a split seen at a higher resolution but not after downsampling is a parameter-sensitive split. (iv) Retrieve a small number of PubMed abstracts for the uncertain labels. They are a literature check, not proof.

## Computed vs retrieved vs inferred
- **Computed:** QC distributions, clusters, markers, ARI/NMI, overlaps.
- **Retrieved:** only what a PubMed search returns, as titles and abstracts.
- **Inferred:** the identity labels and the interpretation of the biology.

## Limitations
- Clustering and marker discovery use the same cells, so p-values are exploratory. They are not independent donor-level validation.
- This is one donor-level sample, so no donor generalization is possible.
- UMAP distances do not prove lineage relationships.
- One subsample tests only one draw. Stability here does not generalize to other draws, other seeds, other fractions or other datasets.
- Four resolutions sample only a limited range.
- No doublet calling, regression or batch integration is available. Anything beyond this needs a software extension.
- The fixed settings (30 PCs, 15 neighbors, 2000 HVGs) are chosen without data. I will report whether the PCA elbow or QC covariates suggest they were poor.
- The sample is a single seed, so I cannot separate algorithmic randomness from data sensitivity.
- Human review decides acceptance.

```json
{
  "target_sum": 10000,
  "n_top_genes": 2000,
  "n_pcs": 30,
  "n_neighbors": 15,
  "baseline_resolution": 0.6,
  "resolutions": [
    0.3,
    0.6,
    1.0,
    1.5
  ],
  "sample_fraction": 0.7,
  "min_cells_per_gene": 3,
  "scale_max": 10
}
```
