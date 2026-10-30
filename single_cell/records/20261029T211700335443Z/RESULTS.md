# PBMC3k: reviewed cell identities and robustness

> Editorial update, 2026-10-29: the user reviewed and accepted the analysis. Codex corrected attribution, status wording and documented errors for the handoff. The original model responses remain in `api/`; this edited report is not a verbatim model response. See `DOCUMENTATION_UPDATE.md` and the task-level `HANDOFF.md`.

No new tool calls were made in this writing step. Sections are tagged **Computed** (from supplied tables), **Inference** (my interpretation) and **Retrieved** (title/abstract only).

## 1. Methods and QC
**Computed.** The input was 2700 cells. 2664 passed QC and 36 were excluded. The failure counts overlap: low genes 15, high genes 5, low counts 13, high counts 5, high mitochondrial fraction 8.

Thresholds were chosen only after I saw the quantiles, histograms and scatter. Cuts are inclusive: genes 300-2500, counts 600-9000, mitochondrial fraction <=8%. The distributions were unimodal with no gap, so I trimmed tails only.

Settings:
- Library-size normalization to 10,000 counts, then log1p.
- 2000 Seurat HVGs, centered/clipped scaling (max 10), 30 arpack PCs, 15 neighbors.
- Leiden at 0.3/0.6/1.0/1.5 on one fixed graph, seed 42, baseline 0.6.
- Downsample: 70% of QC-passing cells (1864). Gene filtering, HVGs, PCA, graph and markers were all rerun, and the sample was clustered **only at 0.6**.
- Markers: Wilcoxon/BH on all filtered log genes. Clustering and markers use the same cells, so p-values are exploratory.

**Caveats.**
- `pca_variance.csv` shows an elbow near PC 6, and PCs 7-30 sit near a plateau (~0.002 each). The choice of 30 PCs was not tested for sensitivity.
- My QC rationale said a 5% mitochondrial cut would remove 'about 5%' of cells. The reviewer's count is 57 cells (2.1%). That figure is not in my supplied tables, and I did not verify it.
- There is no automatic doublet calling.

Artifacts: tables in `/Users/jeffwang/VSCode_Workspace/agent-assisted-binf/single_cell/tables/20261029T211700335443Z` (`sizes_*.csv`, `robustness_metrics.csv`, `cluster_overlaps.csv`, `pca_variance.csv`). Figures are in `.../single_cell/figures/20261029T211700335443Z`. Marker investigations are saved as `investigation_*` (for example 3d9c85d6023a, 833bca2d40fb, fdf2f7a10ed7).

## 2. Resolution and downsampling
**Computed.** The baseline has 5 clusters: T 1191, CD14 monocytes 523, cytotoxic 439, B 346, FCGR3A 165. Agreement with baseline on shared barcodes (ARI/NMI):

| Run | Clusters | ARI | NMI |
|---|---|---|---|
| 0.3 | 5 | 0.917 | 0.909 |
| 1.0 | 8 | 0.661 | 0.836 |
| 1.5 | 11 | 0.523 | 0.772 |
| Downsample 0.6 (n=1864) | 6 | 0.906 | 0.877 |

Quantified changes (`cluster_overlaps.csv`):
- **0.3 merge:** all 165 FCGR3A cells merge into the CD14 cluster (652 = 487 + 165). 36 baseline CD14 cells form their own group (the DC-like cells). 15 baseline cytotoxic cells fall in the T cluster.
- **1.0 splits:**
  - T becomes 625 + 548 (+18 to the GZMK+ cluster).
  - Cytotoxic becomes 307 GZMK+/CD8A+ and 130 NK-like (+2 elsewhere).
  - 36 CD14 cells again form the DC-like group.
- **1.5 splits:**
  - T becomes 509/469/202/11.
  - CD14 becomes 250/235.
  - Cytotoxic becomes 300 (GZMK+ CD8) and 134 (NK-like).
  - 10 baseline FCGR3A cells form a platelet-like cluster.
  - The 36 DC-like cells persist.

**Downsample, with baseline shared cells as the denominator:**
- B 235/235.
- T 830/852 (22 went to the cytotoxic-like cluster).
- Cytotoxic 286/305 (18 went to the T cluster).
- CD14 313/363 (29 to the DC-like cluster, 21 to FCGR3A).
- FCGR3A 100/109 (9 to CD14).

Only one draw at one resolution was run. Populations defined only at resolution >=1.0 are **not testable at 0.6**: NK-like, GZMK+ CD8, the CD14 split, platelet-like and ribosomal-high T. The downsample says nothing about whether they are real.

## 3. Population summary

| Population | Markers (computed) | Stable across resolutions? | Stable after downsampling? | Notes / confidence |
|---|---|---|---|---|
| T cells (CD4/CD8 unresolved) | CD3D, CD3E, LDHB | Lineage present in every run. Subsets (CCR7/LDHB vs IL7R/LTB; 4 clusters at 1.5) appear only at >=1.0 | 830/852 | Lineage supported. Subsets tentative |
| B cells | CD79A, MS4A1, CD79B, TCL1A, BANK1 | Yes: 346 cells at 0.6-1.5 (347 at 0.3) | 235/235 | Supported. 'Naive-like' is untested |
| CD14 monocytes | S100A8/9, CD14, LYZ, FCN1 | Yes. At 1.5 they split into S100-high and HLA-DR/CD68-high | 313/363. 1.5 split not testable at 0.6 | Supported. Subtype split tentative |
| FCGR3A+ monocytes | FCGR3A, MS4A7, CDKN1C, LILRA3, CSF1R | Separate at 0.6-1.5, merged into CD14 at 0.3 | 100/109 | Tentative in all runs (see below) |
| Cytotoxic lymphocytes, mixed | NKG7, GZMA, PRF1, GNLY | One cluster at 0.3 and 0.6 | 286/305 | Supported as a broad compartment only |
| NK-like | GNLY, GZMB, FGFBP2, KLRD1 | 1.0 and 1.5 only (130/134) | Not testable at 0.6 | Tentative. NK identity inferred |
| GZMK+ CD8 | GZMK, CD8A, CCL5 | 1.0 and 1.5 only (325/311) | Not testable at 0.6 | Tentative |
| DC-like (36 cells) | FCER1A, CLEC10A, CD1C, SERPINF1 | Separate at 0.3, 1.0, 1.5 and in the downsample. Absent at baseline 0.6 | 29 cells, all baseline CD14 | Tentative. Non-monotonic |
| Platelet-like (10 cells) | PPBP, PF4, GP9, ITGA2B | 1.5 only | Not testable at 0.6 | Tentative |
| Ribosomal-high T (206) | Ribosomal genes, CD3D, IL32 | 1.5 only | Not testable at 0.6 | Tentative. Median 590 genes, so a low-RNA effect is possible |

**FCGR3A+ monocytes: one rationale for all runs.**
- *Computed:* FCGR3A is detected in 91% of cells vs 14% elsewhere, with MS4A7, CDKN1C, LILRA3 and CSF1R enriched. The group merges into CD14 monocytes at 0.3.
- *Retrieved:* the abstracts support only the label (CD16+ or non-classical monocytes), and none names these genes.
- *Decision:* the label is tentative in every run.

**NK-like and GZMK+ CD8** are tentative wherever they appear. The split exists only at >=1.0, and the abstracts do not support it.

**T cells.**
- In baseline T cells, CD4 is detected in ~10% and CD8A in ~11%. IL7R is 66% and CCR7 36% in the near-identical 0.3 cluster.
- Sparse detection cannot establish CD4 predominance. I **withdraw 'CD4-like predominant'**. The phrase remains only in a note documenting its removal; the population label no longer claims CD4 predominance.
- At 1.5, the IL7R+/LTB+ cluster is modestly CD4-leaning (CD4 15.5% vs 10.9% in all other cells, CD8A depleted). That is only a hypothesis.
- The CCR7/LDHB split at 1.0 is led by ribosomal genes and MALAT1. 'Naive-like' is an inference.

## 4. Ambiguity: the 36-cell DC-like group
**Computed.**
- FCER1A is detected in 83% of cells vs ~1% elsewhere. CLEC10A is 69%, CD1C 50% and SERPINF1 44%.
- CLEC4C (17%), LILRA4 (14%) and IL3RA (11%) are also detected.
- HLA-DRA is higher than in monocytes. S100A8/S100A9 and FCN1 are lower.
- Median counts are 5297, against 1757-3756 in the other res_1 clusters. Median genes are 1570.

**Doublet check.** QC.md promised a multi-lineage co-expression check. **Per-cell co-detection of CD3D, CD79A and NKG7 with high counts was not done.** Only per-cluster detection exists:
- CD3D 17%, similar to monocytes (9%, adjusted p=0.53).
- NKG7 33% (res_1 monocyte cluster 2: 19.7%, adjusted p=0.78).
- CD79A 17% (monocytes 4%, adjusted p=0.010).
- MS4A1 8% and CD79B 19%, against 86% and 92% in B cells.

**Inference.**
- A B-cell doublet group is unlikely.
- T/NK contamination cannot be separated from monocyte background.
- The high counts may reflect larger cells or some doublets.
- Whether the pDC-marker cells are the same cells as the cDC2-marker cells is unknown.

The group separates at 0.3, 1.0, 1.5 and in the downsample (29 cells, all baseline CD14), but not at baseline 0.6. That is a parameter-dependent split. It does not demonstrate a distinct lineage or a continuum. The user's follow-up barcode check confirms that all 29 sampled members of the 36-cell group form the downsample cluster, with no extra cells (`review/check_dc_overlap.py`).

## 5. Platelet-like cluster (res 1.5, n=10)
**Computed.**
- PPBP is detected in 100% of cells, PF4 in 90%, GP9 in 90%, ITGA2B in 80% and GP1BA in 60%.
- PPBP is detected in <=7% of cells in every other cluster.
- LYZ is detected in 70% (mean log 2.2, versus ~5.0 in monocyte clusters), S100A9 in 50%, S100A8 in 40% and HLA-DRA in 60%.
- CD3D is 0%. Median genes are 550 and median counts 1264.
- The 10 cells come from the baseline FCGR3A cluster (10/165). The baseline FCGR3A+ monocyte cluster therefore contains platelet-like cells.

**Inference.** The data strongly support a platelet-gene program. The myeloid co-detection is compatible with platelet-monocyte aggregates or with contaminating myeloid transcripts. Uniform ambient RNA alone fits poorly, because platelet genes are near-absent in other clusters. I cannot separate aggregates from ambient RNA.

**Retrieved.** No PBMC platelet literature was retrieved. That is a literature gap, not evidence against the identity. PMID 30721642 covers GP9/ITGA2B/PF4V1 in isolated platelets at high altitude. PMID 34616175 is an osteoarthritis/metabolic-syndrome biomarker study and is **not** platelet cell-marker evidence, so I removed it. Identity is tentative because n=10 and the cluster is not testable at 0.6.

## 6. Retrieved support (title/abstract only; none validates a label)
- **T cells:** 42771562 (gastric cancer) lists CD3D/CD3E among T-cell markers. 37942472 (peritoneal dialysis) places CD3D/CD3E/CD2 in T-cell pathways. Neither covers LDHB, IL7R or CCR7.
- **B cells:** 38770541 is a single CLL patient. B-cell phenotypic markers, including CD79A and MS4A1, are dysregulated there. This is weak support.
- **Monocytes:**
  - 42004243 reports S100A8/S100A9 upregulation in classical monocytes after radiotherapy.
  - 38936146 reports higher S100A8/S100A9 in VNN2+ monocytes.
  - 32810439 reports calprotectin release and loss of non-classical monocytes in COVID-19.
  - All three are disease-context and indirect.
- **FCGR3A+ monocytes:** 42889286 and 42794611 use CD16+/FCGR3A+ monocyte labels only. 42794611 does not mention S100A8 or S100A9. 42868142 also gives labels without markers, so I do not rely on it. None of these supports MS4A7, CDKN1C or LILRA3.
- **Cytotoxic cells:**
  - 40538191 supports NKG7 as a general cytotoxicity marker.
  - 42682208 and 39074350 show GNLY/NKG7/GZMB/PRF1 in NK and CD8 T cells.
  - 42609202 shows the same genes in cytotoxic CD4+ T cells, so they are not NK-specific.
  - 37898694 is bulk UC/NASH hub-gene work and gives only weak CD8A/NKG7 support. GZMK is unsupported.
- **DC-like:** 38582791 describes FCER1A+CD1C+ DCs in tumor, which is indirect for PBMC. 35101945 describes iPSC-derived CD1c/CLEC10A cDC2 subsets and does not mention FCER1A, so I downgraded it to indirect context.

Canonical identities such as LYZ/S100A8/S100A9 monocytes rest mainly on prior knowledge, not on these abstracts.

## 7. Robust vs sensitive
**Robust (present in every run):**
- The T-lineage cluster (a minor leak of cells to or from the cytotoxic cluster).
- B cells.
- The monocyte/myeloid compartment (CD14 + FCGR3A together).
- The NKG7+ cytotoxic compartment.

**Sensitive (resolution- or draw-dependent):**
- FCGR3A monocytes as a separate cluster (merged at 0.3).
- The DC-like group (absent at baseline 0.6).
- The NK vs GZMK+ CD8 split.
- T-cell and CD14 subsets.
- Platelet-like cells.
- Ribosomal-high T cells.

The label-agreement columns of `population_stability.csv` compare exact label strings (B cells score 0.0 at res_1 and res_1p5 despite identical membership). I did not use them, and I have not inspected the rendered label-agreement table.

## 8. Agent Audit
- **Done this revision:**
  - Corrected downsample denominators.
  - Replaced 'not separated' with 'not testable at 0.6'.
  - Made confidence consistent.
  - Removed the CD4-like claim.
  - Rechecked PMIDs against abstract text.
  - Reported the platelet marker detection.
  - Stated that the doublet co-detection check was not done.
- **Evidence gaps:**
  - No per-cell doublet or co-detection analysis.
  - The later human-review check resolved the DC barcode-overlap question; identity remains uncertain.
  - No pDC vs cDC2 resolution.
  - No platelet aggregate vs ambient test.
  - No PC-number sensitivity.
  - No multiple seeds or draws, and no downsample at 1.0 or 1.5.
  - No donor-level validation (single sample).
  - No protein or independent validation.
- **Human review:** the user reviewed and accepted the labels with the uncertainties above. Doublet calling or ambient correction would require a software extension.