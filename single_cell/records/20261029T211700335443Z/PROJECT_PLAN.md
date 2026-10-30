# Scientific Analysis with AI Agent Workspaces — Project Plan

Work through one section at a time. Each task section lists its goal, steps, required outputs, and checkpoints. Mark checkpoints `[x]` only when the result **and** the code/source behind it exist in the repo. After finishing each task, score it against `RUBRIC.md` and fill in Status / Evidence / Score there.

**Agent/model choice:** Fresh Tasks 1–3 use Claude Sonnet (`claude-sonnet-5-5`) through standalone Python programs. Codex develops and maintains software and is not a runtime scientific analyst. Python computes, Sonnet proposes/interprets, and the user approves stages and final reports. On 2026-10-29 the user selected 4HJO and its five configured EGFR mutations for submission and requested fresh runs. Six old runs and matching outputs were archived with hashes under `archive/2026-10-29-before-sonnet/`; original model attribution and historical Claude Code practice evidence are preserved. The original OpenScience workspace/install sections are not used. All workflows pass local tests; fresh live Sonnet runs, independent review, final audits and the combined report remain pending. See `CLEAN_RUN.md`.

**Ground rules (apply to every task)**
- No GPU, no model training. Everything runs on a laptop.
- No required "correct" answer. Grading is on appropriate methods, shown results, and conclusions matching evidence.
- Always separate: **what the data showed**, **what the agent inferred**, **what external evidence supports**.
- Never commit API keys (report, screenshots, notebooks, code, config).
- Record seeds, settings, software versions, input file names, and filtering decisions as you go.

---

## Checkpoints and grading at a glance

| Checkpoints | What to show | Points |
|---|---|---|
| P1–P4 · Protein | Verified sequence/structure mapping, measurements, annotated structure, mutation comparison with uncertainty | 25 |
| S1–S5 · Single-cell | QC and baseline, marker-based labels, resolution and downsampling comparisons, one investigated ambiguous population | 25 |
| T1–T5 · Spatial | Expression-only clusters on tissue, spatial statistic and genes, DE comparison, randomized null result | 25 |
| A · Agent audit | Per task: sources, computed vs retrieved, one independent check, one weakness | 15 |
| R · Reproducibility and report | Ordered code, data sources, settings/seeds, figures tied to results, checkpoint evidence list | 10 |
| **Total** | | **100** |

---

## Repository structure

```
science-agent-assignment/
├── PROJECT_PLAN.md
├── RUBRIC.md                 # score each task against this when done
├── README.md                 # how to run analyses and where to find evidence
├── report.pdf                # final report (added at the end)
├── datasets/
│   ├── pbmc3k/
│   └── visium_mouse_brain/
├── protein/
│   ├── analysis code
│   └── important outputs
├── single_cell/
│   ├── analysis code
│   └── important outputs
└── spatial/
    ├── analysis code
    └── important outputs
```

Do not commit package caches, temporary downloads, or other unnecessary files.

---

## 5. How to Work with the Agent

Same workflow for all three tasks — do **not** start by asking for a final report:

1. Explain the scientific question
2. Ask the agent to propose a plan
3. Review the plan
4. Let it perform the first analysis
5. Inspect code, figures, and intermediate results
6. Question weak or surprising results
7. Ask for controls or additional analysis
8. Decide which conclusions are actually supported

Opening request:
```
Before running the analysis, propose a clear analysis plan.
Explain what data, software, databases, and statistical methods
you intend to use and why.
```

Useful follow-ups:
- Why did you choose this clustering parameter?
- What evidence supports this cell-type annotation?
- Can you test whether this result remains stable with another parameter?
- Is this conclusion computed from the data, or retrieved from a database?
- What would be an appropriate negative control?

---

## Data supplied for this assignment

| Use | File | Source | Size |
|---|---|---|---|
| Task 2: PBMC3k filtered counts | `datasets/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz` | 10x Genomics PBMC3k | 7.3 MiB |
| Task 3: adult mouse-brain Visium counts | Visium count matrix (`.h5`) in `datasets/visium_mouse_brain/` | 10x Genomics | 20.1 MiB |
| Task 3: spatial coordinates + tissue images | `datasets/visium_mouse_brain/V1_Adult_Mouse_Brain_spatial.tar.gz` | 10x Genomics | 8.6 MiB |
| Task 1 (user-selected submission case) | 4HJO mmCIF / PDB | RCSB PDB 4HJO | 71 + 219 KiB |

Extract once from repo root:
```bash
tar -xzf datasets/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -C datasets/pbmc3k
tar -xzf datasets/visium_mouse_brain/V1_Adult_Mouse_Brain_spatial.tar.gz -C datasets/visium_mouse_brain
```
- PBMC3k matrix → `datasets/pbmc3k/filtered_gene_bc_matrices/hg19/`
- Visium: keep the `.h5` and extracted `spatial/` folder together in `datasets/visium_mouse_brain/`
- See the course dataset README for checksums, provenance, and loading examples.
- Record exact input file names and filtering decisions in the report.

---

## Task 1 — Predicting the Effects of Protein Mutations → `protein/`

**Scientific question:** Which of the assigned missense mutations are most likely to affect protein function, and what molecular mechanism could explain their effects?

**Inputs:** The user explicitly selected 4HJO and the five configured EGFR substitutions for submission on 2026-10-29. This supersedes the earlier practice-only restriction for new runs; historical results remain attributed as practice.

- Submission protein: EGFR kinase domain, UniProt P00533; structure 4HJO chain A (erlotinib-bound, inactive).
- Candidate mutations (agent-chosen, UniProt numbering): G719S, T790M, C797S, L858R, L861Q

### Standalone workflow

- Input preset: `protein/cases/4hjo.json`; supplied files remain read-only.
- Entry point: `python protein/run_analysis.py --config protein/cases/4hjo.json`.
- Sequence: input validation → Claude plan → user approval → numbered computation scripts → Claude interpretation using saved evidence and PubMed tools → user follow-ups → explicit report acceptance.
- Supported control: contact sensitivity at 4/5/6 Å. Unsupported analyses require a software change, not an unexecuted claim.
- Each run saves its own outputs, exact API exchanges, code snapshots, user review and checkpoint index under `protein/runs/`. See `protein/README.md` for setup and verification.
- Implementation has local computation and offline workflow tests. A live Claude API run and scientific review remain pending; a calculation-only run is not a completed agent analysis.

### Steps
1. Retrieve basic protein info: function, domains, catalytic residues, binding sites, ligands, known structures (UniProt, RCSB PDB, AlphaFold DB, literature).
2. Choose a structure/model. Record PDB ID, chain, ligand, residue numbering, and which assigned positions are covered. Verify sequence ↔ structure residue mapping (note any construct mutations/offsets).
3. For each mutation, answer:
   - Inside an important domain?
   - Close to a catalytic/functional residue?
   - Close to a ligand or binding interface?
   - Buried or solvent-exposed?
   - Major change in charge, polarity, or size?
   - Is the structural region reliable (e.g., resolution, pLDDT, missing density)?
4. Quantify where possible: mutation → active-site distance, mutation → ligand distance, residues within 5 Å. State the measurement rule (e.g., minimum heavy-atom distance).
5. Mark candidate sites on the structure.
6. For each mutation, separate **observation**, **prediction**, **external evidence**, and state uncertainty.

### Starting prompt
```
I want to evaluate how several missense mutations may affect this protein.

First create an analysis plan. Use protein sequence, structural information,
functional annotations, and scientific literature.

Whenever possible, perform quantitative structural analysis rather than
relying only on visual inspection.

For each mutation, clearly separate:
1. observations from the data,
2. mechanistic predictions,
3. external evidence.
```

### Expected results
- Short description of the protein
- Table comparing all candidate mutations (Mutation | Structural context | Quantitative evidence | Interpretation | Confidence)
- At least one structural visualization showing mutation locations
- Quantitative structural evidence
- Mechanistic interpretation of each mutation
- Supporting database or literature evidence

### Checkpoints (25 pts)

These checkboxes now refer to the final submission. Historical 4HJO practice results and code remain available; the fresh Sonnet workflow still needs a user-accepted live run. Submission scope is confirmed by the user.

- [ ] **P1** Confirm protein, mutation notation, and residue mapping to the chosen structure/model.
- [ ] **P2** Reproducible structural measurements for the candidates (or documented reason a measurement is invalid + justified alternative).
- [ ] **P3** Separate observed facts, mechanistic predictions, external evidence, and uncertainty in the mutation comparison.
- [ ] **P4** Annotated structure and a comparison table covering every candidate.

### Agent Audit — Protein

Historical practice audit is retained in `protein/AGENT_LOG.md`. Final-submission audit remains pending with the new accepted run.

- [ ] Resources used (datasets, databases, packages, websites, papers)
- [ ] Computed vs retrieved (table)
- [ ] At least one independent verification
- [ ] At least one agent weakness identified, and how it was evaluated/corrected

---

## Task 2 — Single-Cell Cell Types and Robustness → `single_cell/`

**Implementation:** `single_cell/run_analysis.py`; setup, review gates, verification and remaining
work are in `single_cell/README.md`. Claude proposes numerical settings within the documented
supported method family, then chooses QC thresholds after inspecting computed distributions.
Software implementation/testing alone does not complete S1–S5.

**Scientific question:** Which biological conclusions remain stable when reasonable analysis choices are changed?

**Input:** PBMC3k filtered counts at `datasets/pbmc3k/filtered_gene_bc_matrices/hg19/`. Start from counts — no preassigned labels.

### Steps
1. **Baseline:** QC → normalization → highly variable genes → PCA → neighbor graph → clustering → marker genes → annotation. Let the agent choose the workflow; evaluate whether it's reasonable and correctly implemented.
2. **QC:** Inspect genes per cell, total counts, mitochondrial fraction. Choose and justify thresholds from PBMC3k's own distributions.
3. **Annotation:** Cluster → data-derived marker genes → possible identity → database/literature evidence → final label. Keep labels uncertain where evidence is weak.
4. **Resolution comparison:** At least three Leiden resolutions (e.g., 0.3, 0.6, 1.0), all other preprocessing and neighbor settings fixed. Ask: which populations are consistent, which split, which merge, do annotations stay stable? Quantify a meaningful change.
5. **Downsampling:** Randomly retain 60–80% of cells (e.g., ~70%), record the seed, rerun baseline steps. Compare to baseline on cells present in both runs (cluster composition, markers, annotations, ARI, NMI — pick what answers the question).
6. **Ambiguous population:** Pick at least one hard-to-annotate or unstable population and investigate why (related cell types, shared markers, continuous states, small size, technical noise, parameter sensitivity). Consider whether the biology is a continuum.

### Starting prompt
```
Analyze the PBMC3k dataset and identify its major cell populations.

Do not use predefined cell labels.

First propose a reasonable single-cell analysis plan. Use marker genes
derived from the data to support each annotation.

After obtaining a baseline result, test whether the main biological
conclusions remain stable when clustering parameters are changed and
when the dataset is downsampled.

Finally, identify at least one ambiguous or unstable population and
investigate why it is difficult to separate.
```

### Expected results
- Annotated UMAP
- Marker-gene evidence for major populations
- Comparison across several clustering parameters
- Downsampling robustness analysis
- Discussion of at least one ambiguous population
- Summary table: Cell population | Main marker genes | Stable across resolutions? | Stable after downsampling? | Notes
- Final discussion: Which conclusions are robust, and which depend strongly on analytical choices?

### Checkpoints (25 pts)
- [ ] **S1** QC decisions, analysis settings and seed, cluster sizes, and a cluster-labeled UMAP.
- [ ] **S2** Major cell labels supported by markers computed from the data; uncertain labels retained where needed.
- [ ] **S3** At least three Leiden resolutions compared with other settings fixed; splits/merges quantified and label stability discussed.
- [ ] **S4** Fixed-seed 60–80% subsample rerun; retained cells compared quantitatively and label stability discussed.
- [ ] **S5** One ambiguous or unstable population investigated with marker evidence.

### Agent Audit — Single-cell
- [ ] Resources used
- [ ] Computed vs retrieved (table)
- [ ] At least one independent verification
- [ ] At least one agent weakness identified, and how it was evaluated/corrected

---

## Task 3 — Spatial Transcriptomics and Non-Random Tissue Organization → `spatial/`

**Scientific question:** Do transcriptionally defined tissue domains correspond to genuine non-random spatial organization?

**Inputs:** V1 Adult Mouse Brain Visium count matrix + spatial coordinates + tissue images in `datasets/visium_mouse_brain/`.
- Count matrix → expression-based spot clusters
- Spatial coordinates → map clusters onto tissue, define physical neighbors
- Histology image → context only (not used to create clusters)

### Steps
1. **Expression-only clustering:** Gene expression → feature selection → PCA → expression neighbor graph → clustering. **No spatial coordinates in this step.**
2. **Project to tissue:** Plot the same cluster labels at true spatial coordinates. Assess: clear regions vs mixed, recognizable boundaries, consistent neighbors.
3. **Quantify spatial organization:** Neighborhood enrichment, Moran's I, spatial autocorrelation, or another justified statistic. Have the agent explain what it measures and why it's relevant. State the spatial-neighbor definition.
4. **Spatially variable genes:** Restrict to ~100–300 HVGs. Rank by spatial statistic; plot where selected genes are expressed.
5. **DE vs spatial ranking:** For the same candidate genes, compare differential-expression ranking with spatial-autocorrelation ranking. Find genes that are:
   - strong in both,
   - strong DE but weak spatial,
   - strong spatial but weaker DE.
   Explain why the two analyses measure different properties.
6. **Negative control:** ≥100 randomizations with a recorded seed, same statistic on original vs randomized data:
   - Shuffle cluster labels → keep spatial graph fixed, preserve cluster sizes; **or**
   - Permute coordinates → rebuild graph the same way each repetition.
   Show observed value vs null distribution; report empirical tail proportion `(1 + #null ≥ observed) / (n_randomizations + 1)`.

### Implemented workflow and review stops (2026-10-29)

See `spatial/README.md` for setup and exact commands. Run `spatial/run_analysis.py --check`
and the synthetic tests first. Ordered code: `01_qc.py`, `02_cluster.py`, `03_spatial.py`,
`04_verify.py`, dispatched through `run_analysis.py`.

- `python spatial/run_analysis.py agent` starts Sonnet plan review before numerical work.
- Sonnet proposes QC thresholds from computed distributions, then the user approves before filtering.
- Expression clustering defaults to normalization 10,000, 2,000 dispersion-ranked HVGs,
  30 PCs, 15 expression neighbors and Leiden resolutions 0.3/0.5/0.8. Seed 42 throughout.
- Sonnet proposes the primary resolution from expression evidence; user approval freezes it before cluster tissue maps.
- Physical graph: immediate Visium lattice neighbors, symmetric binary weights, no gap bridging.
  Primary statistic: same-cluster edge fraction; 999 fixed-seed label shuffles on the fixed graph.
- Rank 200 expression-selected candidate genes by Moran's I and descriptive omnibus
  Kruskal–Wallis H on unscaled log expression. Retain undefined scores and absent example categories.
- Verify raw QC, graph construction, candidate normalization, both gene statistics, and the null
  independently. Review histology alignment and biological interpretation separately.

Sonnet receives computed/verified evidence and can retrieve PubMed abstracts, then writes a draft
for independent feedback and explicit user acceptance. Exact API exchanges, decisions and review
notes are saved. The earlier QC-only run is archived. Checkpoints remain unchecked pending fresh
results, source assessment, independent review and the Agent Audit.

### Starting prompt
```
I want to determine whether transcriptionally defined tissue domains
show genuine spatial organization.

First cluster the spots using gene expression without using spatial
coordinates.

Then project those clusters back into physical tissue space and quantify
their spatial organization using an appropriate spatial statistic.

Identify spatially variable genes and compare them with genes identified
through differential expression.

Finally, design a randomized negative control and compare the spatial
signal before and after randomization.

Clearly distinguish results directly supported by the data from
biological interpretations.
```

### Expected results
- Expression-based clustering
- Clusters visualized in tissue coordinates
- Quantitative analysis of spatial organization
- Several spatially variable genes
- DE vs spatial ranking comparison
- Randomized negative control
- Comparison table: Analysis | Original data | Randomized control
- Final discussion: Does transcriptional identity correspond to non-random spatial tissue organization? (supported by visual + quantitative evidence)

### Checkpoints (25 pts)
- [ ] **T1** Cluster using expression only; show the same labels in expression space (UMAP) and on tissue, with settings and spot counts.
- [ ] **T2** Define the physical-neighbor graph and report an interpreted numerical spatial statistic.
- [ ] **T3** State the tested gene set and method, rank spatially variable genes, and map at least two genes on tissue.
- [ ] **T4** Compare DE and spatial rankings for the same candidate genes.
- [ ] **T5** Compare observed statistic with ≥100 fixed-seed randomizations using the same statistic; report null distribution and empirical comparison, and note a limitation.

### Agent Audit — Spatial
- [ ] Resources used
- [ ] Computed vs retrieved (table)
- [ ] At least one independent verification
- [ ] At least one agent weakness identified, and how it was evaluated/corrected

---

## 6. What You Need to Submit

One short `report.pdf` + important analysis files (structure above).

### Required report content
- **Protein:** protein and mutation info, mutation comparison table, structural visualization, quantitative structural evidence, mechanistic interpretation, external database/literature evidence.
- **Single-cell:** annotated UMAP, marker evidence, resolution comparison, downsampling analysis, ambiguous population discussion, robustness conclusion.
- **Spatial:** expression-only clusters, tissue-coordinate plot, spatial statistic, spatially variable genes, DE vs spatial comparison, negative control, conclusion.
- **Agent Audit** section for each task (Section 7).
- **Checkpoint evidence list:** checkpoint ID → page/figure/table/code file, each marked *complete* or *needs revision*.

### Reproducibility (R · 10 pts)
- [ ] Ordered code (run order clear in README)
- [ ] Data sources, exact input file names, and software versions
- [ ] Settings and seeds recorded
- [ ] Figures tied to results
- [ ] Checkpoint evidence list in report

---

## 7. Agent Audit (A · 15 pts)

For **each** task, answer:
1. **What resources did the agent use?** Datasets, databases, packages, websites, papers.
2. **What did the agent actually compute?** Table separating computed (e.g., PCA, Leiden, Moran's I, residue–ligand distance) from retrieved (e.g., UniProt annotations, PDB structure, literature, known functional residues).
3. **What did you independently verify?** At least one example per task.
4. **What did the agent do poorly?** At least one incorrect result, questionable choice, unsupported statement, misleading visualization, unnecessary analysis, or weak assumption — and how you evaluated or corrected it.

Keep a running log while working so these are easy to fill in.

---

## 8. What We Are Looking For

| Component | What matters |
|---|---|
| Scientific workflow | Reasonable steps chosen and correctly executed |
| Evidence | Conclusions supported by data and appropriate external evidence |
| Robustness | Tested whether results depend on arbitrary choices |
| Reproducibility | Clear how figures and conclusions were produced |
| Agent audit | Critically inspected and evaluated the agent's work |

Throughout: **What did the data show, what did the agent infer, and what was supported by external scientific evidence?**
