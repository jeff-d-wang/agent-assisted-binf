# Report figures

Figures used in `report.pdf`, in order. All are existing outputs of the submission runs, used
unchanged; no figure was re-rendered for the report. Paths are relative to the repository root.

| Fig. | Checkpoint | File | Made by |
|---|---|---|---|
| 1 | P4 | `protein/figures/4hjo_submission_20261029T200938399152Z/structure_annotated.png` | `protein/03_render.py` |
| 2 | S1, S2 | `single_cell/figures/20261029T211700335443Z/annotated_umap_res_0p6.png` | `single_cell/03_compare.py` |
| 3 | S3 | `single_cell/figures/20261029T211700335443Z/overlap_res_1.png` | `single_cell/03_compare.py` |
| 4 | S5 | `single_cell/figures/20261029T211700335443Z/investigation_af28023de2e1.png` | `single_cell/agent.py` (marker inspection tool) |
| 5 | T1 | `spatial/figures/20261029T222440220672Z/clusters_umap_and_tissue.png` | `spatial/03_spatial.py` |
| 6 | T3 | `spatial/figures/20261029T222440220672Z/gene_tissue_maps.png` | `spatial/03_spatial.py` |
| 7 | T4 | `spatial/figures/20261029T222440220672Z/de_vs_spatial_ranks.png` | `spatial/03_spatial.py` |
| 8 | T5 | `spatial/figures/20261029T222440220672Z/randomized_control.png` | `spatial/03_spatial.py` |

## Captions

**Figure 1. EGFR kinase domain (PDB 4HJO chain A, inactive; wild type at the five candidate sites, engineered V948R elsewhere) with erlotinib.**
Grey cartoon: protein. Light-blue cartoon: UniProt ATP-binding residues. Yellow sticks: erlotinib
(AQ4). Blue sticks: catalytic D837. Spheres mark the Cα atom of each candidate site, with side-chain
sticks: G719S red, T790M orange, C797S magenta, L858R green, L861Q cyan. Labels use UniProt numbering
(author numbering = UniProt − 24). No mutant was modelled. The G719S sphere appears to overlap the
ligand only in this 2D projection; its minimum heavy-atom distance to erlotinib is 5.06 Å (Table 1).

**Figure 2. PBMC3k baseline clusters (Leiden resolution 0.6, seed 42) with reviewed labels.**
UMAP of 2,664 QC-passing cells. Clusters: 0 T cells (1,191), 1 CD14+ monocytes (523), 2 cytotoxic
lymphocytes, NK and CD8+ mixed (439), 3 B cells (346), 4 FCGR3A+ monocytes, tentative (165).
Labels are agent inferences from computed markers (Table 2); they are not predefined labels.

**Figure 3. How baseline clusters split at resolution 1.0.** Each row is a baseline (0.6) cluster;
colour is the fraction of its cells in each resolution-1.0 cluster (same cells, same graph). Baseline
T cells (0) split into 1.0 clusters 0 and 1; cytotoxic cells (2) split into GZMK+ CD8-like (4) and
NK-like (6); CD14 monocytes (1) give up 36 cells to the DC-like cluster 7. B cells (3 → 3) and
FCGR3A+ monocytes (4 → 5) are unchanged.

**Figure 4. The ambiguous DC-like group (resolution 1.0, cluster 7, 36 cells) against other clusters.**
Dot area: fraction of cells with detected expression; colour: mean log expression. Cluster 7 expresses
FCER1A, CD1C and CLEC10A (cDC2-like) with some CLEC4C, IL3RA and LILRA4 (pDC markers) and high
HLA-DRA, and it has lower CD14 than CD14 monocytes (cluster 2). Whether the pDC-marker and
cDC2-marker cells are the same cells, and whether some are doublets, was not tested.

**Figure 5. Expression-only clusters of the Visium section (resolution 0.5, 14 clusters, 2,668 spots).**
Left: UMAP from expression alone. Right: the same labels at the spots' tissue coordinates over the
H&E image. Resolution 0.5 was approved from the UMAPs before any cluster tissue map existed.

**Figure 6. Selected candidate genes on tissue (log1p normalised expression).** Prkcd and Pmch rank
1 and 2 by Moran's I; 2900040C04Rik ranks 14 (strong spatial, weaker DE); Dnali1 ranks 140 (strong DE,
weak spatial); Gm4952 ranks last (200) because it is detected in only 0.41% of spots.

**Figure 7. Differential-expression rank vs spatial rank for the same 200 candidate genes.**
x: rank by Kruskal–Wallis H across the 14 clusters (1 = highest); y: rank by Moran's I on the
physical lattice graph. Labelled genes are the examples in Figure 6. Both scores are descriptive
rankings, not significance tests.

**Figure 8. Randomized negative control.** Same-cluster edge fraction on the fixed physical graph:
observed 0.780 (red) against 999 cluster-label shuffles that preserve cluster sizes (seed 42; null
mean 0.088). Empirical upper tail (1 + 0)/(999 + 1) = 0.001, the smallest value possible with 999
shuffles. Limitation: shuffling does not preserve spatial autocorrelation, so it rules out random
label placement but not smooth expression or technical gradients.
