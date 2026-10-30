---
title: "Agent-assisted bioinformatics: protein mutations, PBMC3k and Visium mouse brain"
author: "Jeffrey Wang (jdw2)"
date: "2026-10-29"
mainfont: "STIXGeneral"
monofont: "Menlo"
monofontoptions: "Scale=0.85"
header-includes:
  - '`\usepackage{float}`{=latex}'
  - '`\floatplacement{figure}{H}`{=latex}'
  - '`\setlength{\tabcolsep}{4pt}`{=latex}'
  - '`\renewcommand{\arraystretch}{1.1}`{=latex}'
  - '`\setlength{\LTcapwidth}{\textwidth}`{=latex}'
---

# Introduction

| Task | Question | Run (short name) | Analysis agent |
|:-------|:------------------------------------|:----------------------|:-----------------|
| 1 Protein | Which of five EGFR substitutions affect function, and how? | **RUN1** = `4hjo_submission_` `20261029T200938399152Z` | `claude-sonnet-5-5` |
| 2 Single-cell | Which PBMC3k cell-type conclusions survive changes in resolution and downsampling? | **RUN2** = `20261029T211700335443Z` | `claude-sonnet-5-5` |
| 3 Spatial | Do expression-defined Visium clusters form non-random spatial patterns? | **RUN3** = `20261029T222440220672Z` | `claude-haiku-5-5` (credit balance) |

**Workflow:** Python computed every number. The analysis agent planned the work and interpreted the saved results. I approved each plan and gate, checked outputs, sent feedback and accepted each task report. Codex wrote the software. Claude Code (`claude-opus-5-5`) packaged the submission, drafted and revised this report from the saved records, and added the Task 2 marker sources marked *Reviewer-added*.

**Evidence tags:** *Observed*: computed from the data, by the pipeline or by a review check. *Inferred*: the analysis agent's interpretation. *Reviewer*: my interpretation during review. *Retrieved*: from a database or PubMed abstract. Where an accepted agent report had a known error, this report uses the correction recorded in `PRE_DELIVERABLE_REVIEW.md`.

**Paths:** results live in `<task>/figures/RUNn/`, `<task>/tables/RUNn/` and `<task>/records/RUNn/` (accepted report, settings, sources, executed code). Scripts are numbered in run order in each task folder; review checks are in `<task>/review/`.

# Task 1: EGFR mutations in structure 4HJO

## Data and methods

- **Protein:** EGFR (UniProt P00533, entry v301), a receptor tyrosine kinase. All five sites lie in the kinase domain (712-979); D837 is the annotated proton acceptor. *Retrieved.*
- **Structure:** PDB 4HJO chain A, X-ray 2.75 Å, inactive kinase domain with erlotinib (AQ4). It is wild type at all five candidate sites but carries one engineered substitution, V948R, 22-31 Å from every candidate.
- **Mapping:** SIFTS and a BLOSUM62 alignment agree for all five sites; author numbering = UniProt − 24; all candidate heavy atoms observed.
- **Measurements** (`protein/02_measure.py`): minimum heavy-atom distances to erlotinib and UniProt Active/Binding residues; contacts at 5 Å (also 4 and 6 Å); Shrake-Rupley RSA, buried if < 0.25. The calculations are deterministic, so no seed applies. No mutant was modelled, and no dynamics, affinity or energy was calculated.

## Results

![**EGFR kinase domain (PDB 4HJO chain A) with erlotinib.** The structure is wild type at the five candidate sites and carries the engineered V948R substitution elsewhere. Grey: protein. Light blue: UniProt ATP-binding residues. Yellow sticks: erlotinib. Blue sticks: catalytic D837. Spheres mark the Cα atom of each candidate: G719S red, T790M orange, C797S magenta, L858R green, L861Q cyan (UniProt numbering). The G719S sphere overlaps the ligand only in this 2D view; its distance is 5.06 Å. Source: `protein/03_render.py`.](../protein/figures/4hjo_submission_20261029T200938399152Z/structure_annotated.png){width=50%}

*Takeaway (Figure 1):* T790 and C797 contact erlotinib, G719 and L858 sit in the second shell, and L861 is far from it.

`\setcounter{table}{0}`{=latex}

| Mutation (author) | Quantitative evidence (*Observed*) | Prediction (*Inferred*) | External evidence (*Retrieved*) | Confidence |
|:-------------|:--------------------------|:---------------------|:--------------------------|:--------------|
| G719S (G695) | 5.06 Å, in range only at 6 Å. RSA 0.232 (near cutoff). +28.9 Å³. ATP-binding residue; contacts lie in its own 718-726 stretch | Extra side chain may change local packing or flexibility | UniProt: strongly increased activity. PMID 22349823: constitutively active | Activity moderate to high; mechanism low |
| T790M (T766) | 3.48 Å at every cutoff. 19.3 Å² covered by ligand. RSA 0.182. +46.8 Å³ | Geometry suggests steric clash with erlotinib | PMIDs 18227510, 22349823: "gatekeeper"; resistance mainly via higher ATP affinity | Resistance moderate to high; steric-only low |
| C797S (C773) | 3.54 Å at every cutoff. 27.0 Å² covered by ligand. RSA 0.238 (near cutoff). Not an annotated site | Loss of the thiol would prevent covalent attachment; not testable in this erlotinib complex | PMID 29802850: C797S "abolishes the covalent bonding" of third-generation TKIs | Covalent-TKI resistance moderate to high; intrinsic activity unknown |
| L858R (L834) | 5.26 Å, in range only at 6 Å. RSA 0.096. +1 charge. Non-local contacts K745 3.21, L788 3.64, M766 4.57 Å. Closest to D837 (6.37 Å) | Buried charge may alter packing or the active/inactive balance | UniProt: strongly increased activity. PMID 22349823: constitutively active; cleft expanded via F723 | Activity moderate to high; mechanism moderate |
| L861Q (L837) | 9.22 Å; no ligand within 6 Å. Most buried (RSA 0.024). Contacts E762, M766, I759, none annotated | Polar residue may disturb buried packing (indirect, untested) | UniProt: constitutively activated. PMID 37196448: less sensitive than ex19del/L858R cells | Activity moderate; drug response low |

: **Mutation comparison.** Distances are to erlotinib in 4HJO. Sources: `protein/tables/RUN1/measurements.csv`, `contacts_5A.csv`, `contact_sensitivity.csv`, `mapping.csv`; `protein/records/RUN1/RESULTS.md` §5.

*Takeaway (Table 1):* only T790 and C797 contact the ligand at every cutoff. The G719 and L858 ligand calls, and the G719 and C797 burial calls, depend on the cutoff.

## Interpretation

- **Activity:** UniProt exact-substitution notes report increased activity for G719S, T790M, L858R and L861Q (*Retrieved*). The structure adds geometric context only (*Observed*); the G719S, L858R and L861Q mechanisms are hypotheses (*Inferred*).
- **T790M:** Geometry suggests steric blocking (*Inferred*), but two primary abstracts attribute resistance mainly to higher ATP affinity; PMID 18227510: "Threonine 790 is the 'gatekeeper' residue" (*Retrieved*).
- **C797S:** C797 lies 3.54 Å from erlotinib (*Observed*). Separately, PMID 29802850 reports that C797S abolishes covalent bonding of third-generation inhibitors (*Retrieved*). 4HJO contains no covalent inhibitor, so the measured contact does not test that mechanism. The effect on intrinsic activity is unknown; absence of evidence does not imply a small effect.
- **L858R:** PMID 22349823 reports cleft expansion via F723 (*Retrieved*). The abstract does not state the conformation of its L858R structure, so none is assumed.
- **Drug response is comparator-specific:** UniProt: G719S, L858R, L861Q "more sensitive to gefitinib than wild type". PMID 22349823: sensitivity without a stated comparator. PMID 37196448: L861Q versus ex19del/L858R. These answer different questions and give no single ranking.

## Conclusion and uncertainty

- The best-supported drug-response effects come from the literature: higher ATP affinity for T790M and loss of covalent inhibitor bonding for C797S (*Retrieved*). Both residues contact erlotinib in 4HJO (*Observed*), but that geometry does not demonstrate either mechanism.
- G719S, L858R and L861Q are annotated as activating; their structural mechanisms are untested.
- One inactive, single-chain crystal at 2.75 Å (wild type at the candidate sites, with V948R) cannot test conformational or dimerization effects. Relative B-factors (0.90-1.05) do not measure dynamics.
- Literature is abstract-only; UniProt-cited primary papers were not fetched; G719S and L861Q drug evidence is mostly pooled (G719X), small or computational.

## Agent Audit: Task 1

**Resources:** 4HJO mmCIF/PDB (RCSB); UniProt P00533 v301 (rest.uniprot.org); SIFTS (PDBe API); PubMed: 29 queries, 27 cited PMIDs, abstract-only; Biopython 1.85, NumPy 1.25.2, Python 3.9.15, PyMOL 3.1.0 (`protein/records/RUN1/data/provenance.json`).

| Computed (Python) | Retrieved |
|:----------------------------------------|:----------------------------------------|
| Mapping and offset, distances, 4/5/6 Å contacts, SASA/RSA, relative B-factor, physicochemical deltas, PyMOL distance recheck | UniProt sites and variant notes; SIFTS; PDB metadata; PubMed abstracts. Mechanisms are Sonnet's inference |

**Independent check:** `protein/review/check_dist.py` (plain-text PDB parse with NumPy, no Biopython) reproduces the mapping, the −24 offset and every checked distance to 0.01 Å. `check_sasa.py` (PyMOL, dot densities 2-4) gives RSA 0.240-0.247 for G719 and 0.228-0.234 for C797: buried, within about 0.02 of the cutoff. All 27 PMIDs match their saved abstracts.

**Weaknesses:** (1) The first draft used sequence neighbours as functional evidence: L858 to D855 (i−3), and G719 to residues in its own stretch. I spotted this in `contacts_5A.csv`; Sonnet switched to the non-local contacts. (2) After an output-limit failure, the retry silently dropped 9 queries, including PMID 22349823. I asked Sonnet to retrieve it again. The accepted report still misquoted "Threonine 790" as "Threshold 790" and claimed an active L858R conformation its source does not state; both are corrected here.

# Task 2: PBMC3k cell types and robustness

## Data and methods

- **Input:** 10x PBMC3k filtered counts (`datasets/pbmc3k/filtered_gene_bc_matrices/hg19/`), 2,700 cells × 32,738 genes; no predefined labels.
- **QC** (`single_cell/01_qc.py`), thresholds chosen by Sonnet from the distributions: 300-2,500 genes, 600-9,000 counts, mitochondrial ≤ 8%; 2,664 cells kept.
- **Pipeline** (`single_cell/02_cluster.py`): normalize to 10,000 and log1p; 2,000 Seurat HVGs; scale (max 10); 30 PCs; 15 neighbours; Leiden 0.3, 0.6 (baseline), 1.0, 1.5 on one fixed graph; Wilcoxon markers.
- **Downsampling:** 70% (1,864 cells), full rerun, clustered at 0.6 only; compared in `single_cell/03_compare.py`. **Seed 42.** Scanpy 1.9.8, leidenalg 0.12.0.

## Results

![**PBMC3k baseline clusters (Leiden 0.6, seed 42) with reviewed labels.** UMAP of 2,664 QC-passing cells: T cells (1,191), CD14+ monocytes (523), cytotoxic lymphocytes, NK and CD8+ mixed (439), B cells (346), FCGR3A+ monocytes, tentative (165). Labels are agent inferences from computed markers (Table 2). Source: `single_cell/03_compare.py`.](../single_cell/figures/20261029T211700335443Z/annotated_umap_res_0p6.png){width=85%}

*Takeaway (Figure 2):* five separated groups; T and cytotoxic cells touch, as do the two monocyte groups.

`\setcounter{table}{1}`{=latex}

| Population | Markers (*Observed*) [support] | Across resolutions | After downsampling | Confidence |
|:--------------|:-------------------|:----------------------|:-------------|:------------|
| T cells (CD4/CD8 unresolved) | CD3D, CD3E, LDHB [1] | Lineage in every run; subsets only at ≥ 1.0 | 830/852 | Lineage supported; subsets tentative |
| B cells | CD79A, MS4A1, CD79B [1] | 346 cells at 0.6-1.5 (347 at 0.3) | 235/235 | Supported |
| CD14 monocytes | S100A8/9, CD14, LYZ, FCN1 [1, 2] | Stable; split at 1.5 | 313/363 | Supported; split tentative |
| FCGR3A+ monocytes | FCGR3A, MS4A7, CDKN1C [1, 2] | Separate at 0.6-1.5; merged at 0.3 | 100/109 | Tentative |
| Cytotoxic, mixed | NKG7, GZMA, PRF1, GNLY [1, 3] | One cluster at 0.3 and 0.6 | 286/305 | Broad compartment only |
| NK-like / GZMK+ CD8 | GNLY, GZMB / GZMK, CD8A [3, 4] | 1.0 and 1.5 only | Not testable at 0.6 | Tentative |
| DC-like (36 cells) | FCER1A, CLEC10A, CD1C [1, 2] | At 0.3, 1.0, 1.5; absent at 0.6 | All 29 sampled cells | Tentative |
| Platelet-like (10 cells) | PPBP, PF4, GP9 [1] | 1.5 only | Not testable at 0.6 | Tentative |

: **Population summary.** Downsampling recovery uses sampled baseline cells as the denominator. [n] = *Reviewer-added* source supporting part of the marker combination (see Interpretation). Sources: `single_cell/tables/RUN2/annotations.csv`, `cluster_overlaps.csv`; `single_cell/records/RUN2/RESULTS.md` §3.

`\setcounter{table}{2}`{=latex}

| Comparison | Cells | Clusters | ARI | NMI |
|:---|---:|---:|---:|---:|
| Resolution 0.3 | 2,664 | 5 | 0.917 | 0.909 |
| Resolution 1.0 | 2,664 | 8 | 0.661 | 0.836 |
| Resolution 1.5 | 2,664 | 11 | 0.523 | 0.772 |
| Downsample 70%, resolution 0.6 | 1,864 | 6 | 0.906 | 0.877 |

: **Robustness against the 0.6 baseline** on shared barcodes. Source: `single_cell/tables/RUN2/robustness_metrics.csv` (`single_cell/03_compare.py`).

![**How baseline clusters split at resolution 1.0.** Rows: baseline (0.6) clusters; colour: fraction of cells in each 1.0 cluster (same cells, same graph). T cells (0) split into 0 and 1; cytotoxic cells (2) into GZMK+ CD8-like (4) and NK-like (6); CD14 monocytes (1) give 36 cells to DC-like cluster 7. B cells (3 → 3) and FCGR3A+ monocytes (4 → 5) are unchanged. Source: `single_cell/03_compare.py`.](../single_cell/figures/20261029T211700335443Z/overlap_res_1.png){width=46%}

*Takeaway (Table 3, Figure 3):* ARI falls with resolution because large groups split, not because lineages mix. Downsampling at 0.6 reproduces the baseline (ARI 0.906).

![**The ambiguous DC-like group (resolution 1.0, cluster 7, 36 cells).** Dot area: fraction of cells detected; colour: mean log expression. Cluster 7 expresses FCER1A, CD1C, CLEC10A (cDC2-like), some CLEC4C, IL3RA, LILRA4 (pDC markers) and high HLA-DRA, with less CD14 than CD14 monocytes (cluster 2). Source: marker-inspection tool in `single_cell/agent.py`.](../single_cell/figures/20261029T211700335443Z/investigation_af28023de2e1.png){width=64%}

*Takeaway (Figure 4):* the DC-like group's membership is reproducible, but it mixes cDC2-like and pDC-like markers.

## Interpretation

- **Labels** are inferred from markers computed per run (*Observed* markers, *Inferred* labels). The abstracts Sonnet retrieved mostly come from disease contexts or name labels without markers, so they do not validate the labels (*Retrieved*, weak).
- **Reviewer-added marker support** (*Retrieved* after acceptance; not used by Sonnet). Primary single-cell papers support the marker interpretations used here: CD3D for T cells, CD79A for B cells, S100A8/S100A9 for myeloid cells, NKG7 for NK and cytotoxic T cells, FCER1A for dendritic cells and PF4 for megakaryocytes [1]; CD14 versus CD16 for classical versus non-classical monocytes and CD1C, CLEC10A and FCER1A for CD1C+ dendritic cells [2]; FCGR3A, GNLY and PRF1 in CD56dim NK cells [3]; and a GZMK+ CD8+ T-cell population in human blood [4]. They support the marker interpretation; they do not independently validate the identities of these particular cells. Not covered: LDHB, MS4A1, LYZ, FCN1, MS4A7, CDKN1C and LILRA4.
- **NK-like versus GZMK+ CD8:** GZMK is also expressed by CD56bright NK cells [3], so the CD8 label rests on CD8A co-detection, not on GZMK. The split stays tentative.
- **T cells:** CD4 (~10%) and CD8A (~11%) are detected at similar rates, so CD4 predominance cannot be claimed (*Observed*). The IL7R+/LTB+ cluster at 1.5 is modestly CD4-leaning (15.5% vs 10.9% in all other cells), a hypothesis only (*Inferred*).
- **DC-like group:** FCER1A 83%, CLEC10A 69%, CD1C 50%; CLEC4C 17%, LILRA4 14%, IL3RA 11%; median counts 5,297 versus 1,757-3,756 elsewhere (*Observed*). The same 36 barcodes separate at 0.3, 1.0 and 1.5, and all 29 sampled ones form downsample cluster 5 (*Observed*, `single_cell/review/check_dc_overlap.py`). The cDC2-like reading fits [2]. IL3RA and CLEC4C are also expressed by a non-pDC AXL+SIGLEC6+ population [2], so their detection does not by itself establish pDCs. Whether the group is cDC2, a pDC admixture or doublets is unresolved (*Inferred*); no per-cell co-detection test was run.
- **Platelet-like cells:** PPBP 100%, PF4 90%, GP9 90%, PPBP ≤ 7% in all other clusters (*Observed*). Aggregates and ambient RNA cannot be told apart (*Inferred*).

## Conclusion and uncertainty

- **Robust:** T, B, monocyte/myeloid and NKG7+ cytotoxic compartments appear in every run.
- **Choice-dependent:** FCGR3A+ monocytes as a separate cluster, the DC-like group, NK versus GZMK+ CD8, T and CD14 subsets, platelet-like cells.
- Downsampling is one draw at 0.6, so populations defined at ≥ 1.0 have no downsampling evidence. The planned Jaccard and top-marker overlaps were never computed.
- PC number, k, HVG count and per-cell doublets were not tested, and there is one donor.

## Agent Audit: Task 2

**Resources:** PBMC3k matrix (10x Genomics; SHA-256 in `single_cell/records/RUN2/inputs.json`); Scanpy 1.9.8, AnnData 0.10.5.post1, leidenalg 0.12.0, igraph 1.0.0, umap-learn 0.5.5, scikit-learn 1.1.1, SciPy 1.13.1, Python 3.9.15; PubMed: 25 queries (14 empty), 40 unique PMIDs, abstract-only. Sources [1]-[4] were added during report review and were not resources of the agent.

| Computed (Python) | Retrieved |
|:----------------------------------------|:----------------------------------------|
| QC and filtering, HVGs, PCA, graph, Leiden, UMAP, Wilcoxon markers, overlaps, ARI/NMI, downsample rerun, population inspections | PubMed titles and abstracts. Labels and the robust/sensitive split are Sonnet's inference |

**Independent check:** `single_cell/review/check_task2.py` (SciPy and scikit-learn on raw `matrix.mtx`, no pipeline code) reproduces QC (2,664/2,700), all four ARI/NMI pairs and the downsampling crosstab. `check_rev1.py` reproduces the revision-1 marker fractions; `check_dc_overlap.py` confirms the DC-like overlap. All match, except the revision-0 denominators (weakness 1) and two minor values corrected here (monocyte NKG7 is 19.7%, not 22%).

**Weaknesses:** (1) Revision 0 divided downsampling recovery by the downsample cluster size (B cells "235 of 236") and called the NK/CD8 split "not separated" though it could not be tested at 0.6. I rebuilt the crosstab; revision 1 reports 235/235 and "not testable". (2) Revision 0 inferred "CD4-like predominant" from sparse detection, cited four PMIDs that did not support their claims (34616175 is an osteoarthritis study), and skipped the doublet check promised at QC. I compared each claim with its abstract; Sonnet withdrew the claim, dropped or re-described the PMIDs and reported the check as not done. Sonnet's own retrieval never found direct marker sources; [1]-[4] fill part of that gap after the fact.

# Task 3: Visium mouse-brain spatial organization

## Data and methods

- **Input:** `V1_Adult_Mouse_Brain_filtered_feature_bc_matrix.h5` and `spatial/` (10x Genomics), 2,702 in-tissue spots × 32,285 genes. H&E used for context only.
- **QC** (`spatial/01_qc.py`, `02_cluster.py`), thresholds chosen by Haiku: counts 5,000-100,000, genes 2,000-10,000, mitochondrial ≤ 30%; 2,668 spots kept.
- **Expression-only clustering** (`spatial/02_cluster.py`): 2,000 dispersion HVGs, 30 PCs, 15 neighbours, Leiden 0.3/0.5/0.8. Haiku proposed 0.5 (14 clusters, 29-338 spots) and I approved it before any cluster tissue map existed.
- **Physical graph** (`spatial/03_spatial.py`): immediate Visium lattice neighbours, binary symmetric weights, no gap bridging: 7,679 edges, degree 1-6, no isolates.
- **Statistics** (`spatial/03_spatial.py`). *Same-cluster edge fraction:* the share of physical edges whose two spots carry the same cluster label. *Moran's I:* how similar a gene's level is between lattice neighbours, regardless of cluster. *Kruskal-Wallis H:* how strongly a gene's distribution differs between clusters; descriptive only, because expression also defined the clusters. Both gene scores were computed for 200 expression-selected candidate genes. *Null:* 999 size-preserving label shuffles on the fixed graph. **Seed 42.**

## Results

![**Expression-only clusters (resolution 0.5, 14 clusters, 2,668 spots).** Left: UMAP from expression alone. Right: the same labels at the spots' tissue coordinates over the H&E image. Source: `spatial/03_spatial.py`.](../spatial/figures/20261029T222440220672Z/clusters_umap_and_tissue.png){width=100%}

*Takeaway (Figure 5):* clusters defined without coordinates form contiguous regions on tissue.

**Spatial statistic:** 78.0% of physical edges join same-cluster spots (0.780); 0.826 at resolution 0.3 and 0.781 at 0.8 (*Observed*; `spatial/records/RUN3/graph_summary.json`, `spatial/tables/RUN3/spatial_resolution_sensitivity.csv`).

![**Selected candidate genes on tissue (log1p normalised expression).** Prkcd and Pmch rank 1 and 2 by Moran's I; 2900040C04Rik ranks 14 (strong spatial, weaker DE); Dnali1 ranks 140 (strong DE, weak spatial); Gm4952 ranks 200 because it is detected in only 0.41% of spots. Source: `spatial/03_spatial.py`.](../spatial/figures/20261029T222440220672Z/gene_tissue_maps.png){width=80%}

*Takeaway (Figure 6):* high-Moran genes form compact patches; Gm4952's low rank reflects sparsity, not uniform expression.

![**DE rank vs spatial rank for the same 200 candidate genes.** x: Kruskal-Wallis H rank across the 14 clusters (1 = highest); y: Moran's I rank on the lattice graph. Labelled genes as in Figure 6. Both are descriptive rankings, not significance tests. Source: `spatial/03_spatial.py`.](../spatial/figures/20261029T222440220672Z/de_vs_spatial_ranks.png){width=45%}

*Takeaway (Figure 7):* the ranks trend together, but some genes diverge (no rank correlation was computed). Spatial / DE rank: Prkcd 1/14 (strong on both); Dnali1 140/23 (strong DE, weak spatial); 2900040C04Rik 14/116 (strong spatial, weaker DE) (`spatial/tables/RUN3/gene_rankings.csv`, `ranking_examples.csv`).

![**Randomized negative control.** Same-cluster edge fraction on the fixed graph: observed 0.780 (red) against 999 size-preserving label shuffles (seed 42; null mean 0.088). Empirical upper tail 0.001, the smallest possible with 999 shuffles. Source: `spatial/03_spatial.py`.](../spatial/figures/20261029T222440220672Z/randomized_control.png){width=52%}

`\setcounter{table}{3}`{=latex}

| Analysis | Original | Randomized |
|:------------------------------|:---------|:-----------------------------------|
| Same-cluster edge fraction, res. 0.5 (999 shuffles, seed 42) | 0.780 | Mean 0.0879 (SD 0.0032); 95% range 0.0818-0.0938; max 0.1017 |
| Null values ≥ observed | n/a | 0 of 999 |
| Empirical upper tail, (1 + 0)/(999 + 1) | 0.001 | Smallest value possible with 999 shuffles |
| Separate check, 999 shuffles, seed 7 | 0.780 | Mean 0.0880 (SD 0.00325) |

: **Negative control.** Sources: `spatial/tables/RUN3/original_vs_randomized.csv`, `null_distribution.csv`; seed-7 row from `spatial/review/check_task3.py`.

*Takeaway (Table 4, Figure 8):* the observed value is far above every shuffle, so the labels are not placed at random.

## Interpretation

- **Discordant genes: measurements** (*Observed*; `spatial/tables/RUN3/gene_cluster_means.csv`, `physical_edges.csv`; my follow-up check after acceptance, reproduced by `spatial/review/check_task3.py`). Dnali1 and 2900040C04Rik both peak in cluster 12 (means 0.49 and 1.04; next-highest 0.03 and 0.14), a 56-spot group present at all three resolutions. Of 240 unique edges touching it, 83 (34.6%) stay inside; counting edge endpoints gives 51.4%. Pmch spans clusters 5, 9 and 4 (means 2.47, 1.19, 0.96).
- **Discordant genes: explanations.** Haiku, without the cluster means, proposed that Dnali1 separates clusters without spatial contiguity, that 2900040C04Rik is contiguous but overlaps across clusters, and that Pmch forms a patch split across clusters (*Inferred*). In review I judged that a narrow, cluster-specific group fits Dnali1's high H and low Moran's I, that the means do not support Haiku's broad-overlap explanation for 2900040C04Rik, and that the Pmch means fit Haiku's hypothesis (*Reviewer*). Expression in only part of cluster 12 could explain 2900040C04Rik's high Moran rank and lower H; this remains untested (*Reviewer*, hypothesis).
- **QC confounding** (*Observed*; my review check, reproduced by `spatial/review/check_task3.py`). Fourteen quantile groups of total counts or mitochondrial fraction give edge fractions of only 0.140 and 0.174. Mitochondrial fraction still differs strongly between clusters (H 983.1). I read the low quantile-group values as arguing against a simple depth explanation (*Reviewer*). Cluster 13 (29 spots) follows the high-count arc in the QC tissue map (*Reviewer* observation), and Haiku inferred it may be technical (*Inferred*).
- **Null:** the shuffle rejects random label placement. It does not preserve spatial autocorrelation, so it cannot separate biological domains from smooth expression or technical gradients (*Inferred* by Haiku; I agree).
- **External evidence:** none retrieved; no anatomical, cell-type or gene-function identity is claimed.

## Conclusion and uncertainty

- Expression-defined clusters are spatially coherent: 0.780 versus a null mean of 0.088, empirical tail 0.001.
- The global shuffle shows non-random label placement only. It cannot separate biological domains from smooth expression or technical gradients.
- Gene-pattern mechanisms and the identities of cluster 13 and the 56-spot group remain hypotheses.

## Agent Audit: Task 3

**Resources:** Visium matrix and `spatial/` folder (10x Genomics; SHA-256 in `spatial/records/RUN3/inputs.json`); Scanpy 1.9.8, AnnData 0.10.5.post1, leidenalg 0.12.0, SciPy 1.13.1, scikit-learn 1.1.1; h5py 3.6.0 as imported (the run record lists 3.11.0 from duplicate metadata). Databases, websites, papers: none.

| Computed | Retrieved | Interpreted |
|:----------------------------|:----------------|:-------------------------------------|
| Pipeline (Python): QC, HVGs, PCA, Leiden, UMAP, lattice graph, edge fraction, 999-shuffle null, Moran's I, Kruskal-Wallis H, cluster means. Review checks (mine; reproduced by `check_task3.py`): QC-covariate H, Moran's I and quantile partitions, cluster-12 edge counts | None | Haiku: QC thresholds, resolution proposal, null limitation, cluster 13 as possibly technical, discordant-gene hypotheses. Me (review): QC-confounding reading, cluster-mean reading of the discordant genes |

**Independent check:** `spatial/review/check_task3.py` (no pipeline imports; added by Codex to reproduce my review checks) reproduces the coordinate join and graph (7,679 edges), the edge fractions (0.825759 / 0.780049 / 0.780570), a separate seed-7 null, the QC-covariate values and the cluster means. All assertions pass. `spatial/tables/RUN3/pca_variance.csv` shows PC30 at 0.20%, not the 2.0% Haiku reported.

**Weaknesses:** (1) Haiku reported PC30 variance tenfold too high, wrongly said QC tissue maps were never supplied, gave 2900040C04Rik's H as 400 (actual 431.9) and called the sparse Gm4952 "near-uniform". Revision 1 fixed the first two; the edited `RESULTS.md` and this report fix the rest. (2) Haiku explained the 2900040C04Rik rank gap as broad overlap across clusters without having `gene_cluster_means.csv`; the cluster means did not support it. Haiku also skipped the planned cluster-versus-QC test, which I ran in review.

# Limitations and reproducibility

**Shared limits:** One structure, sample or section per task; abstract-only literature for Tasks 1-2 (none for Task 3); one seed and parameter set in Tasks 2-3; one human reviewer. Accepted `RESULTS.md` files carry dated editorial corrections; original model responses stay in each local run's `api/`.

**Where things are:** Run order and commands: `README.md`. Settings and seeds: `<task>/records/RUNn/` (`config.json`, `plan.json`, `qc.json`, `approved_*.json`), with executed code in `<task>/records/RUNn/code/`. Versions: `requirements.lock.txt` (PyMOL 3.1.0 separate). Run file hashes: `<task>/records/RUNn/manifest.json`. Review scripts: `<task>/review/`. Audit logs: `<task>/AGENT_LOG.md`.

# References

*Data and databases.* RCSB PDB 4HJO, inactive EGFR kinase domain with erlotinib (structure citation PMID 23101586, from PDB metadata). UniProt P00533, entry v301. PDBe SIFTS mapping for 4hjo. 10x Genomics PBMC3k filtered matrices (hg19). 10x Genomics V1 Adult Mouse Brain Visium.

*PubMed abstracts retrieved by the analysis agents and cited here.* 18227510, 22349823, 29802850, 37196448 (Task 1); 34616175 (Task 2, unsupported citation). Full lists: `protein/AGENT_LOG.md` (27 PMIDs), `single_cell/records/RUN2/RESULTS.md` §6.

*Reviewer-added sources (Task 2; full text checked during report review, not retrieved by Sonnet).*

- [1] Zheng GXY, Terry JM, Belgrader P, et al. Massively parallel digital transcriptional profiling of single cells. *Nat Commun.* 2017;8:14049. PMID 28091601.
- [2] Villani AC, Satija R, Reynolds G, et al. Single-cell RNA-seq reveals new types of human blood dendritic cells, monocytes, and progenitors. *Science.* 2017;356(6335):eaah4573. PMID 28428369.
- [3] Smith SL, Kennedy PR, Stacey KB, et al. Diversity of peripheral blood human NK cells identified by single-cell RNA sequencing. *Blood Adv.* 2020;4(7):1388-1406. PMID 32271902.
- [4] Mogilenko DA, Shpynov O, Andhey PS, et al. Comprehensive profiling of an aging immune system reveals clonal GZMK+ CD8+ T cells as conserved hallmark of inflammaging. *Immunity.* 2021;54(1):99-115.e12. PMID 33271118 (abstract checked).

*Software.* Python 3.9.15; Biopython 1.85; NumPy 1.25.2; PyMOL 3.1.0; Scanpy 1.9.8; AnnData 0.10.5.post1; leidenalg 0.12.0; igraph 1.0.0; umap-learn 0.5.5; scikit-learn 1.1.1; SciPy 1.13.1; h5py 3.6.0.

`\newpage`{=latex}

# Checkpoint evidence index

Status from `RUBRIC.md`. Paths start at the repository root; RUN1-RUN3 are defined in the Introduction.

\begingroup\footnotesize

| ID | Status | Page | Fig./Table | Result files | Code |
|:-------------------|:---------|:------|:-----------|:------------------------------------|:------------------------|
| P1 Map variants | complete | 1-3 | Table 1 | `protein/tables/RUN1/` mapping.csv, functional_sites.csv | `protein/01_map.py` |
| P2 Measurements | complete | 1-3 | Table 1 | `protein/tables/RUN1/` measurements.csv, contacts_5A.csv, contact_sensitivity.csv | `protein/02_measure.py` |
| P3 Interpretation | complete | 3 | Table 1 | `protein/records/RUN1/` RESULTS.md §5-8, data/ | `protein/run_analysis.py` |
| P4 Structure + table | complete | 2-3 | Fig. 1, Table 1 | `protein/figures/RUN1/` structure_annotated.png | `protein/03_render.py` |
| S1 Baseline and QC | complete | 4 | Fig. 2 | `single_cell/records/RUN2/` QC.md, qc.json; `single_cell/tables/RUN2/` sizes_res_0p6.csv | `single_cell/01_qc.py`, `02_cluster.py` |
| S2 Cell-type evidence | complete | 5-6 | Table 2 | `single_cell/tables/RUN2/` annotations.csv, top_markers_res_*.csv | `single_cell/02_cluster.py`, `agent.py` |
| S3 Resolutions | complete | 5 | Fig. 3, Table 3 | `single_cell/tables/RUN2/` robustness_metrics.csv, cluster_overlaps.csv | `single_cell/03_compare.py` |
| S4 Downsampling | complete | 4-5 | Tables 2-3 | `single_cell/tables/RUN2/` cells_downsample.csv, robustness_metrics.csv | `single_cell/02_cluster.py`, `03_compare.py` |
| S5 Ambiguous population | complete | 6 | Fig. 4 | `single_cell/tables/RUN2/` investigation_af28023de2e1_*.csv | `single_cell/agent.py`, `review/check_dc_overlap.py` |
| T1 Expression domains | complete | 7-8 | Fig. 5 | `spatial/tables/RUN3/` cluster_sizes.csv, resolution_comparison.csv | `spatial/02_cluster.py`, `03_spatial.py` |
| T2 Spatial statistic | complete | 7-8 | Fig. 5, Table 4 | `spatial/records/RUN3/` graph_summary.json; `spatial/tables/RUN3/` physical_edges.csv | `spatial/03_spatial.py` |
| T3 Spatial genes | complete | 8 | Fig. 6 | `spatial/tables/RUN3/` candidate_genes.csv, gene_rankings.csv | `spatial/02_cluster.py`, `03_spatial.py` |
| T4 DE vs spatial | complete | 9-10 | Fig. 7 | `spatial/tables/RUN3/` ranking_examples.csv, gene_cluster_means.csv | `spatial/03_spatial.py`, `review/check_task3.py` |
| T5 Negative control | complete | 9 | Fig. 8, Table 4 | `spatial/tables/RUN3/` null_distribution.csv, original_vs_randomized.csv | `spatial/03_spatial.py`, `04_verify.py` |
| Audit: Task 1 | complete | 3 | audit table | `protein/REVIEW_NOTES.md`, `protein/AGENT_LOG.md` | `protein/review/` |
| Audit: Task 2 | complete | 7 | audit table | `single_cell/REVIEW_NOTES.md`, `single_cell/AGENT_LOG.md` | `single_cell/review/` |
| Audit: Task 3 | complete | 10-11 | audit table | `spatial/REVIEW_NOTES.md`, `spatial/AGENT_LOG.md` | `spatial/review/` |
| R1-R3 Code, versions, seeds | complete | 11 | none | `README.md`, `requirements.lock.txt`, `<task>/records/RUNn/` config.json | numbered scripts per task |
| R4 Figures tied to results | complete | 2-9 | Figs. 1-8, Tables 1-4 | `report/figures.md` | scripts named in captions |
| R5 Report with index | complete | 12 | this table | `report.pdf`, `report/report.md` | none |

\endgroup
