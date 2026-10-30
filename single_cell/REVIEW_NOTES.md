# Task 2 independent review

- **Run:** `single_cell/runs/20261029T211700335443Z` (analysis agent `claude-sonnet-5-5`). Figures and tables: `single_cell/figures/20261029T211700335443Z/`, `single_cell/tables/20261029T211700335443Z/`.
- **Reviewer:** the user (human), 2026-10-29. Verification rests on the independent checks below.
- **Check scripts:** `single_cell/review/check_task2.py`, `check_rev1.py`, `check_dc_overlap.py`. They use scipy, sklearn and anndata only, and no pipeline code.
- **Who acted:** the user reviewed the results, sent feedback to Sonnet and accepted the report at 22:02:58 UTC. The three acceptance notes in the run's `REVIEW.md` record the user's review.

## Review prompt (from the user)

> Independently review Task 2 in single_cell/runs/20261029T211700335443Z against PROJECT_PLAN.md and RUBRIC.md. Read the actual tables, plots, settings, verification and cited source records. Separate computed observations, the analysis agent's inferences and external support. Independently check at least one numerical result or source claim and identify exactly what you checked and the outcome. Find actual unsupported claims, questionable choices or limitations and explain their impact; do not invent errors to fill the audit. Tell me what feedback to send Sonnet, what additional evidence is needed and which conclusions remain uncertain. Do not edit the run, approve it or award grades automatically.

## What happened

1. **First-draft review (revision 0).** The computed numbers were correct. The problems were in the interpretation:
   - **Wrong denominators:** downsampling recovery was divided by the size of the downsample cluster instead of the baseline shared cells. For example, B cells were given as "235 of 236" when the correct figure is 235/235.
   - **Misread negatives:** NK-like and GZMK+ CD8 were reported as "not separated" after downsampling. The downsample was clustered only at 0.6, so those splits could not be tested there.
   - **Confidence contradicting the text:** NK-like and GZMK+ CD8 were labelled *supported* while the text called the split probable and sensitive. FCGR3A+ monocytes were *tentative* in two runs and *supported* in two others, with identical markers and PMIDs.
   - **Self-contradiction:** FCGR3A+ monocytes were listed as both robust and sensitive (they merge into CD14 at 0.3).
   - **Inference from absence:** "CD4-like predominant", although CD4 (10%) and CD8A (11%) were detected at the same rate in baseline T cells.
   - **Citations that do not support the claim:**
     - 42794611 does not mention S100A8 or S100A9.
     - 42868142 uses the monocyte labels but gives no markers.
     - 34616175 is an osteoarthritis/metabolic-syndrome biomarker study.
     - 35101945 does not mention FCER1A.
   - **Platelet-like cluster:** called "unsupported for PBMC" when only literature retrieval had failed. The data show PPBP in 100% of cells and PF4, GP9 and ITGA2B in 80 to 90%.
   - **Broken promise:** the doublet co-expression check promised in QC.md was not done.
   - **Minor:** "three of four" non-baseline runs should be all four; a 5% mitochondrial cut removes 57 cells (2.1%), not "about 5%".
   - **Software, not Sonnet:** `population_stability.csv` label agreement compares exact label strings. B cells score 0.0 at res_1 and res_1p5 despite identical membership. This is reported for Codex to fix.
2. **Feedback.** The user sent all ten points in one round, as one line followed by `quit`, through `runtime/run_analysis.py --resume` (`events.jsonl` `user_feedback`, 21:53:37 UTC). The API key was loaded from `.env` and not displayed. Sonnet made 11 responses, 4 new population inspections and 1 PubMed query, which returned nothing.
3. **Revised-draft review (revision 1).** The eight substantive points were fixed, or now stated plainly as not done. The ambiguity section now covers the 36-cell DC-like group; NK versus CD8 stays in the population table as tentative. The revision also cites two PMIDs retrieved in revision 0 but not used then: 42889286 (labels only) and 42609202 (cytotoxic genes in CD4 T cells). Three minor issues were left in the accepted report:
   - It says a stale CD4-like label persists in `population_stability.csv`; the phrase appears only in a note recording its removal.
   - "CD4 15% vs 6.8%" compares against the naive-like sibling, cluster 1 at 1.5, not against all other cells. Against all other cells it is 10.9%.
   - Monocyte NKG7 is given as 22%; I get 19.7 to 20.7% (res_1 cluster 2, res_0p6 cluster 1).

## Independent checks

| Check | Method | Outcome |
|---|---|---|
| QC filtering | `check_task2.py`: raw `matrix.mtx` with scipy, approved thresholds | Match: 2664/2700 retained; failures 15/5/13/5/8; 13 MT genes |
| ARI/NMI, 4 comparisons | sklearn on `cells_*.csv` (the pipeline verifier checks ARI only) | Match: 0.917/0.909, 0.661/0.836, 0.523/0.772, 0.906/0.877 |
| Downsampling denominators | Baseline × downsample crosstab | Revision 0 wrong; revision 1 correct (B 235/235, T 830/852, cytotoxic 286/305, CD14 313/363, FCGR3A 100/109) |
| Ambiguity, res_1 clusters 4 vs 6 | `check_task2.py`: detection fractions from the `baseline.h5ad` raw layer | Match: CD3D 84/7, CD8A 46/8, GZMK 58/3, GNLY 35/97, FCGR3A 26/89 |
| Revision 1 new values | `check_rev1.py` | Match: platelet PPBP 100, PF4 90, GP9 90, ITGA2B 80, GP1BA 60, LYZ 70%; PPBP ≤7% in all other clusters; DC FCER1A 83, CD3D 17, CD79A 17, NKG7 33%; FCGR3A 91 vs 14%. The two exceptions are the minor issues in step 3 |
| Cited sources | Every cited PMID looked up in `data/pubmed_*.json`; claims compared with the abstract text | All cited PMIDs were retrieved. Revision 1's characterisations match the abstracts |
| DC-like membership | `check_dc_overlap.py` (after acceptance, not in the report) | The same 36 barcodes form the cluster at 0.3, 1.0 and 1.5. 29 were sampled, and exactly those 29 form downsample cluster 5 |
| Evidence integrity | `--verify` against `manifest.json` after acceptance | Passed; all 31 figures and 63 tables are sealed; stage `accepted` |

## Still uncertain

- **NK-like versus GZMK+ CD8:** a continuum is neither shown nor excluded, and no protein or TCR data are available.
- **T cells:** the CD4/CD8 and naive/memory make-up.
- **CD14 split at 1.5:** whether it is real.
- **DC-like group identity:** cDC2, pDC admixture or doublets. No per-cell co-detection test was run. Its membership is now known to be stable (check above); what is uncertain is the identity, not the boundary.
- **Platelet-like cluster:** aggregates or ambient RNA.
- **Ribosomal-high cluster:** a technical effect or a low-RNA state.
- **Downsampling evidence:** one draw, clustered only at 0.6. Populations defined at resolution ≥1.0 have no downsampling evidence.
- **Sensitivity and scope:** PC-number, k and HVG sensitivity are untested; there is one donor and no doublet calling; sources are abstract-only and mostly from disease contexts.

## Reviewer errors and omissions

- **Missed promise:** the first review did not check that PLAN.md step 10 promised Jaccard best-match and top-marker overlap between the downsample and baseline. Neither was computed or reported, and this was not raised before acceptance. Impact: S4 rests on overlap fractions and ARI/NMI only. The marker-level stability of downsampled labels remains unshown.
- **Feedback format:** the user submitted the review feedback as one line because the runner reads one line at a time.

## Before deliverable preparation

The user requested a concise handoff and correction of reviewer attribution. See
HANDOFF.md for the short version. The pre-deliverable pass reproduced the numerical
checks and corrected the documented residual wording in the run's RESULTS.md, with
an editorial notice. The original model response remains in api/. Earlier review
entries above describe what the user saw at acceptance, before these editorial fixes.
Scientific uncertainty and omitted analyses remain explicit. See
../PRE_DELIVERABLE_REVIEW.md for the check scope and remaining packaging work.
