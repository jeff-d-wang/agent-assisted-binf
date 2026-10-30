# Task 2: reviewed findings for the report

Run: `20261029T211700335443Z`. Analysis agent: Claude Sonnet (`claude-sonnet-5-5`).
The user reviewed the plan and QC, checked the draft against tables and sources,
sent corrections, and accepted revision 1 on 2026-10-29. Codex maintained the code
and edited this summary.

## What the data support

QC retained 2,664 of 2,700 PBMC3k cells: 300 to 2,500 genes, 600 to 9,000 counts,
and mitochondrial fraction at most 8%. The pipeline used 2,000 HVGs, 30 PCs,
15 neighbors and seed 42. Four Leiden resolutions shared one expression graph.
The 70% subsample contained 1,864 cells and reran preprocessing and clustering at 0.6.

| Comparison with baseline 0.6 | Clusters | ARI | NMI |
|---|---|---|---|
| Resolution 0.3 | 5 | 0.917 | 0.909 |
| Resolution 1.0 | 8 | 0.661 | 0.836 |
| Resolution 1.5 | 11 | 0.523 | 0.772 |
| Downsample at 0.6 | 6 | 0.906 | 0.877 |

| Baseline interpretation | Cells | Computed marker evidence | Recovery among sampled baseline cells |
|---|---|---|---|
| T lineage; CD4/CD8 unresolved | 1,191 | CD3D, CD3E, LDHB | 830/852 |
| CD14 monocytes | 523 | S100A8/9, CD14, LYZ, FCN1 | 313/363 |
| Mixed cytotoxic lymphocytes | 439 | NKG7, GZMA, PRF1, GNLY | 286/305 |
| B cells | 346 | CD79A, MS4A1, CD79B | 235/235 |
| FCGR3A monocytes, tentative | 165 | FCGR3A, MS4A7, CDKN1C | 100/109 |

These are interpretations of computed markers. The retrieved abstracts offer uneven,
often disease-context support. They do not independently validate every label.
The T, B, myeloid and cytotoxic compartments recur; finer labels depend on resolution.

## Ambiguity and negative results

The same 36 DC-like cells separate at resolutions 0.3, 1.0 and 1.5, but merge into
baseline CD14 cells at 0.6. All 29 sampled members form the downsample DC-like cluster,
with no extra cells. Membership is reproducible; cDC2/pDC mixture, doublets and exact
identity remain unresolved. Markers include FCER1A (83%), CLEC10A (69%) and CD1C (50%).

NK-like and GZMK+ CD8 groups appear only at higher resolutions. The downsample at 0.6
cannot test those splits. Ten platelet-like cells at 1.5 express PPBP (100%), PF4 and
GP9 (90% each), but aggregates and ambient RNA remain possible. A ribosomal-high T
group may reflect low RNA content. No per-cell doublet check, PC sensitivity study,
additional draw or higher-resolution downsample was performed.

## What the user changed through review

The user corrected downsampling denominators, unsupported CD4 predominance, inconsistent
confidence, weak citations and claims that an untested split had disappeared. Independent
scripts reproduce QC, ARI/NMI, marker fractions and DC barcode overlap. The numerical
verifier and these checks pass. The plan's promised Jaccard and top-marker-overlap analyses
were not implemented; report that omission rather than imply they were done.

Do not use the `*_supported_label_agreement` columns in `population_stability.csv` as
biological stability scores. The code compares exact label strings and counts tentative
labels as resolved. B cells receive zero agreement at higher resolutions despite identical
membership. Use barcode overlaps, ARI/NMI and the reviewed population table above.

For the report, use the readable numbered UMAPs with a compact label table. The annotated
UMAP legends compress the plotting area. Preserve tentative labels in the caption.

Full evidence: `runs/20261029T211700335443Z/RESULTS.md`, `REVIEW.md` and
`verification.json`; `tables/20261029T211700335443Z/`; `figures/20261029T211700335443Z/`;
review scripts in `review/`. Detailed source limitations remain in `REVIEW_NOTES.md`
and the full report. See `../PRE_DELIVERABLE_REVIEW.md` before packaging.
