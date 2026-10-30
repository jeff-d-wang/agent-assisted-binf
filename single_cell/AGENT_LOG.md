# Task 2 agent log

Current submission summary: `HANDOFF.md`. The user was the human reviewer for the
2026-10-29 submission run. Dated entries below preserve the history of plans, checks,
feedback and maintenance; earlier analyst credits refer to historical work.


## 2026-10-28 — Standalone workflow implementation (Codex software development)

- **User request:** implement the agreed Claude-first workflow, explain how to run/verify it,
  and identify what remains for Task 2. Claude should propose/defend its plan before its output
  is evaluated against S1–S5. Codex is the developer, not the runtime scientific analyst.
- **Prompt/answer attribution:** no live prompt was sent to Claude and no Claude scientific answer
  was obtained. `run_analysis.py` stores the runtime plan, QC and report prompts; the live runner
  saves exact calls and answers under its `api/` directory. Tests use explicitly synthetic mock responses.
- **Implemented:** reviewed plan → QC distributions → reviewed thresholds → baseline → fixed-graph
  resolution comparison → full count-based subsample rerun → marker/source interpretation and ambiguity
  investigation → human review. Labels are not preassigned. Unsupported methods require extension.
- **Resources:** supplied 10x PBMC3k input paths under `datasets/pbmc3k/filtered_gene_bc_matrices/hg19/`
  (preflight only); existing Task 1 transport/PubMed helper code reused without modifying Task 1;
  Scanpy and Anthropic API documentation listed below. Exact tested package versions: `VALIDATION.md`
  and `requirements.txt`; each future run records its own `inputs.json`.
- **Computed versus retrieved:** synthetic scientific calculations and local file/dependency checks
  were computed here; software API documentation was retrieved. No real cell identities, marker
  results or biological literature evidence were computed/retrieved for Task 2 in this session.
- **Settings:** scientific seed fixed at 42. Synthetic tests use 180 cells × 300 genes, 150 HVGs,
  5 PCs, 8 neighbors, resolutions 0.3/0.6/1.0 and 70% sampling. These are test settings only.
  Claude must select real settings and distribution-based QC thresholds in the reviewed live run.
  Raw datasets were not modified. Synthetic files are created in temporary directories.
- **Checks:** input/dependency preflight and all five final automated tests passed. Synthetic figures
  were visually inspected. The synthetic workflow checks raw counts/genes/MT
  fractions independently of Scanpy, verifies exact seeded membership (179 retained, 125 sampled),
  recomputes three ARIs from contingency tables, and checks split/merge fractions. Tests also cover
  approval gates, pause/resume, invalid settings, truncated/unsupported agent responses, unresolved
  labels, missing citations and deliberate evidence tampering. See `VALIDATION.md`.
- **Weaknesses/limits:** no live Claude weakness has yet been observed; do not count hypothetical
  limitations as a completed agent audit. The implementation rejects traceability failures but cannot
  decide whether a retrieved abstract truly supports an annotation. It uses one supported method family
  and one subsample, not arbitrary generated analyses. A rendering interruption recovery path was added
  and tested so a validated response can be rendered again without repeating a paid Claude call.
- **Pending:** real Claude plan/QC review, PBMC3k computation, source and annotation review, a supported
  ambiguity investigation, an actual agent weakness/correction, final acceptance and S1–S5 scoring.

Software references (consulted 2026-10-28; not biological evidence):
- https://scanpy.readthedocs.io/en/1.9.x/generated/scanpy.pp.highly_variable_genes.html
- https://scanpy.readthedocs.io/en/1.9.x/generated/scanpy.tl.rank_genes_groups.html
- https://scanpy.readthedocs.io/en/1.9.x/generated/scanpy.tl.leiden.html
- https://platform.claude.com/docs/en/api/messages/create

Each live run writes its own `AGENT_LOG.md`, exact prompts/answers, dated events, settings,
source records and human `REVIEW.md`. After review, add a dated entry here linking the selected
run and summarizing Claude's actual findings, checked claims and observed weaknesses.

## 2026-10-28 — Live-run failure review and recovery (Codex software development)

- **User request:** review run `20261028T235728272943Z`, explain why it stopped, then repair
  interpretation/recovery handling and explain the next step. The run's API timestamps cross midnight
  UTC; this entry uses the user's America/New_York date.
- **Claude's work:** the user approved Claude's plan and distribution-based QC. Python completed
  the calculations: 2,700 input cells, 2,673 retained, baseline six clusters, 1,871 sampled cells,
  and three resolution/downsampling comparisons. Claude requested a cytotoxic-population contrast
  and PubMed searches, then wrote 25 provisional annotations and an ambiguity discussion before
  its report was cut off. These are Claude-authored hypotheses, not Codex biological conclusions.
- **Failure:** `api/006.response.json` has `stop_reason=max_tokens`, 24,000 output tokens, including
  15,031 reported thinking tokens. User approvals and numerical steps succeeded. The old code
  rejected the partial report but failed to save intermediate interpretation progress to resumable
  state and left the human-readable status at `compute`.
- **Repair:** separate annotations for each analysis, ambiguity and a concise final report;
  checkpoint each tool result and valid response; preserve completed parts across failures; feed
  validation errors back on retry; refresh audit status on exceptions. No new scientific method,
  QC threshold, random seed, package requirement or numerical analysis was introduced.
- **Recovery:** complete leading JSON sections were parsed and validated without inventing missing
  text. All 25 annotations and the ambiguity object were saved verbatim as provisional Claude
  output in `interpretation_parts/0/`. The report remains pending. Original code and API records
  were preserved; `recovery/` records archived state/manifest/audit and source-response provenance;
  `runtime/` stores the repaired program. No paid API call was made during repair.
- **Computed versus retrieved:** recovery/checks are software operations on existing local evidence.
  The prior live run computed marker/robustness tables and retrieved PubMed abstracts. Codex consulted
  official Claude API budgeting documentation, not additional biological sources, during this repair.
  Exact scientific settings and package versions remain in the run's `computation.json` and `inputs.json`.
- **Checks:** all nine tests passed, including truncated-output recovery, mid-tool interruption,
  saved-response reuse, complete-field parsing and synthetic end-to-end resume. All 102 original
  manifest entries remain preserved (old state archived). Independent verification still passes
  for all 2,700 raw cells and three ARIs. A no-network dry run confirmed the next request is only
  report writing. No plan/QC, clustering or downsampling rerun is required.
- **Agent weakness and remaining review:** several retrieved sources provide weak/context-mismatched
  support; some searches were empty. The recovered ambiguity discussion calls a mixed cytotoxic
  population a continuum more strongly than the computation alone establishes. The new report prompt
  asks Claude to assess these gaps, but the recovered text was not silently rewritten or accepted.
  Human source review and scientific corrections remain required.
- **Next:** resume the same run to obtain the report, review the annotated outputs and claims,
  record independent review/weaknesses, and accept only when satisfied. Rubric scores remain deferred.

## 2026-10-29 — Fresh Sonnet setup and archive (Codex development)

User requested fresh Tasks 1–3, Sonnet as analyst and another agent for review/audit feedback. Set the active model to `claude-sonnet-5-5`. Two previous single-cell runs and corresponding figures/tables were moved, byte-verified, into `archive/2026-10-29-before-sonnet/`; historical API responses/model identities and recovery artifacts are unchanged. Both old runs were at review/interpretation stages; fresh-run evidence must not be confused with them.

Resources: existing Task 2 runtime/tests and Anthropic's model overview (https://platform.claude.com/docs/en/models/overview, 2026-10-29). Computed: dependency/input preflight and nine offline/synthetic tests passed, including review/resume/verification and truncated-response recovery. No new PBMC3k analysis or live Sonnet call occurred. Settings remain chosen/reviewed at runtime, scientific seed remains 42. Weakness addressed: active README previously encouraged resuming old repaired work despite the request for a fresh model/run; now points to CLEAN_RUN.md and marks recovery instructions historical. Scientific-agent critique and final acceptance remain pending; independent reviewer agreement alone is not verification.

## 2026-10-29 — Sonnet output-budget adjustment (Codex maintenance)

User reported a max-token failure in protein run `4hjo_submission_20261029T200938399152Z` and requested reasonable limits for all tasks. Saved response `api/005.response.json` reported `stop_reason=max_tokens`, 16,000 output tokens, including 9,881 thinking tokens; request-to-response elapsed time was approximately 113 seconds. These are retrieved execution records, not new scientific results. Anthropic documentation confirms reasoning and text share max_tokens: https://platform.claude.com/docs/en/build-with-claude/thinking (consulted 2026-10-29).

Changed this task's per-response cap from 24,000 to 32,000 and HTTP timeout from 180 to 360 seconds. Model, scientific methods/seeds, report-length instructions and truncation rejection are unchanged. Two targeted transport tests passed: the outgoing cap is 32,000, truncation preserves state, and retry reuses completed tool work. No live API request, scientific analysis or package change was made. Higher caps are upper bounds and may increase cost/latency; they cannot guarantee completion.

Weakness evaluated: the earlier caps left insufficient combined reasoning/report room for the observed Sonnet response. The protein run's original snapshot and truncated response are retained; a separate runtime copy, hashes and change note document the adjustment. Resume that run at interpretation using the updated root script. New Task 2/3 runs inherit the new limits; no existing Task 2/3 runtime snapshots were altered.

## 2026-10-29 — QC field-name repair (Codex software maintenance)

- **Request and Claude output:** user reported `QC fields do not match the supported filters`
  in run `20261029T211700335443Z`. In response to the saved QC prompt, plots and quantiles,
  Sonnet proposed inclusive genes 300–2500, counts 600–9000 and mitochondrial percentage
  at most 8, with its rationale in `api/002.response.json`. These remain provisional Claude
  decisions requiring user review; Codex did not choose or scientifically endorse them.
- **Observed weakness:** the complete response (`stop_reason=end_turn`) used `" min_genes"`
  with a leading space. The strict field check rejected it. This was not token truncation.
  QC validation now trims surrounding field-name whitespace and logs normalization while
  still rejecting collisions, unknown/missing fields, invalid types and invalid ranges.
- **Recovery:** restored the existing proposal to `qc_review` without changing any value or
  rationale, and preserved original assistant content in the conversation. Original code/API
  records remain intact. `recovery/` retains prior state/manifest/audit and source hashes;
  `runtime/` holds the updated program. No live API request, QC approval or PBMC3k recalculation.
- **Resources/settings:** local saved request/response, existing QC outputs and Python test
  suite only; no external biological evidence retrieved. Seed 42, scientific scripts, package
  requirements and recorded versions in `inputs.json` are unchanged.
- **Checks:** all 11 offline/synthetic tests passed, including new whitespace/collision tests,
  normalized proposal persistence, and end-to-end review/resume/verification. Sandbox tests
  used writable temporary Matplotlib/Numba caches after the default cache location failed.
  Hash checks verified original sealed evidence (old state in recovery). A dry resume of the
  actual run, with API and computation calls blocked, paused at user QC approval successfully.
- **Remaining:** user review of QC rationale/plots, then clustering, interpretation and final
  scientific review. The field-name fix is software handling, not independent biological validation.

## 2026-10-29 — Pairwise Wilcoxon warning inspection (Codex diagnostics)

- **User question:** after approving QC in run `20261029T211700335443Z`, Scanpy emitted
  `RuntimeWarning: invalid value encountered in divide` at `_rank_genes_groups.py:286`.
  Codex inspected saved logs/tables and the installed Scanpy 1.9.8 source; no new Claude prompt.
- **Finding:** this is the tie-corrected pairwise Wilcoxon division in `inspect_population`.
  Genes absent in both compared groups have tied ranks and zero standard deviation, giving
  an intermediate 0/0. The installed source immediately replaces NaN scores with zero;
  its resulting two-sided p-value is 1. The warning did not stop the run.
- **Computed checks:** both clustering/comparison scripts exited successfully. Existing
  `verification.json` records 2,700 raw cells, 2,664 retained, 1,864 sampled and four independently
  checked ARIs. Read-only checks of all five saved marker tables and the four pairwise tables
  present at inspection found all numeric values finite. The pairwise tables each contain
  13,658 genes; respectively 351, 944, 1,699 and 584 genes absent in both groups had score 0,
  p-value 1 and adjusted p-value 1. These checks inspected cached expression and saved tables;
  they did not rerun clustering or statistical tests.
- **Progress/settings:** the run remains at interpretation, with annotations for resolutions
  0.3 and 0.6 checkpointed and later tool calls continuing. No runtime, thresholds, seed,
  dependencies, evidence or active state were changed, and no paid API call was initiated.
- **Limitations:** this verifies handling of these numerical warnings, not biological labels
  or literature support. Final interpretation and scientific review remain pending. No agent
  scientific error is established by this warning alone.

> The user was the human reviewer for this submission run. The entries below were
> documented on 2026-10-29 after acceptance, using the run's `events.jsonl`, `api/`
> and saved files cited in each entry. Times are UTC.

## 2026-10-29 — Submission run: plan gate (Sonnet)

- **Run:** `single_cell/runs/20261029T211700335443Z`, created 21:17:00. Analyst `claude-sonnet-5-5`; developer Codex.
- **Request/answer:** the plan prompt (`api/001`) asked Sonnet to propose and defend the workflow and its executable settings before seeing any data. Sonnet's `PLAN.md`:
  - Annotate each run separately from that run's own markers, and match runs only by barcode.
  - Hold the graph fixed across resolutions.
  - Downsample with a full rerun.
  - Choose the ambiguity target after seeing the data.
  - Run four self-checks, including QC-covariate checks and a sparing PubMed check.
- **Settings proposed and approved** (`plan.json`): target_sum 10000, min_cells_per_gene 3, 2000 Seurat HVGs, scale_max 10, 30 arpack PCs, 15 neighbors, Leiden 0.3/0.6/1.0/1.5 with baseline 0.6, sample_fraction 0.7, seed 42 (fixed by software).
- **Gate:** `plan_approved` at 21:19:06 at the runner prompt. No feedback round was logged.
- **Agent weakness, found later:** step 10 promised Jaccard best-match and top-marker overlap for the downsample. Neither is implemented or reported (`REVIEW_NOTES.md`, reviewer omissions).

## 2026-10-29 — Submission run: QC gate (Sonnet)

- **Computed:** `01_qc.py` at 21:19:28 (`qc_quantiles.csv`, `qc_distributions.png`, `qc_joint.png`). Input: 2700 cells, 32,738 genes, 13 MT genes.
- **Request/answer:** Sonnet saw the quantiles and plots (`api/002`, `QC.md`). It chose inclusive tail cuts: genes 300–2500, counts 600–9000, MT ≤8%. Its reasoning was that the distributions are unimodal with no gap. It promised to watch for multi-lineage co-expression as a doublet signal.
- **Software:** the `" min_genes"` field-name repair at 21:25:17 is logged above (Codex).
- **Gate:** `qc_review_approved` at 21:31:37. No feedback round was logged.
- **Result** (`filter_summary.json`): 2664 retained, 36 excluded. Failures overlap: low genes 15, high genes 5, low counts 13, high counts 5, high MT 8.
- **Agent weaknesses:**
  - "A 5% MT cut would remove about 5%" is wrong; it would remove 57 cells (2.1%).
  - The promised co-expression check was never run.

## 2026-10-29 — Submission run: computation (Python)

- **Computed:** `02_cluster.py` at 21:33:07 and `03_compare.py` at 21:33:11; inputs and versions in `inputs.json` (scanpy 1.9.8, anndata 0.10.5.post1, leidenalg 0.12.0, igraph 1.0.0, umap-learn 0.5.5, scikit-learn 1.1.1, Python 3.9.15).
- **Baseline at 0.6:** 5 clusters of 1191, 523, 439, 346 and 165 cells.
- **Other resolutions:** 0.3 gives 5 clusters, 1.0 gives 8, 1.5 gives 11.
- **Downsample:** 1864 cells, 6 clusters.
- **ARI/NMI vs baseline:** 0.917/0.909, 0.661/0.836, 0.523/0.772, 0.906/0.877.
- **Checks:** `verification.json` recomputed raw-matrix QC, seeded subsample membership and four contingency-table ARIs. All passed.

## 2026-10-29 — Submission run: interpretation and first draft (revision 0)

- **Sonnet's work:**
  - Annotated each of the five runs.
  - Ran 10 saved population inspections and 24 PubMed queries; 13 queries returned nothing, and 40 unique PMIDs were retrieved, abstract-only.
  - Chose NK versus CD8 in the cytotoxic cluster as the ambiguous population.
  - Wrote `DRAFT.md`.
- **Rendering:** annotations rendered at 21:39:31.
- **Usage, plan through draft:** 20 Sonnet responses; 1,858,080 input and 48,549 output tokens.
- **Computed vs retrieved vs inferred:**
  - Python computed the markers, overlaps and inspections.
  - PubMed records were retrieved.
  - All labels and the robust/sensitive classification are Sonnet's inferences.

## 2026-10-29: Independent review of first draft (human reviewer)

- **Review scope:** the CLEAN_RUN §5 review prompt, quoted in `REVIEW_NOTES.md`. The user performed the review.
- **Checks:**
  - Raw-matrix QC, ARI and NMI recomputed with sklearn.
  - Ambiguity detection fractions recomputed.
  - Downsampling crosstab rebuilt.
  - All 17 cited PMIDs compared with their abstracts.
  - All match except the draft's downsampling denominators (`single_cell/review/check_task2.py`).
- **Agent weaknesses found:** ten, listed in `REVIEW_NOTES.md` step 1. They include wrong denominators, confidence contradicting the text, the robust/sensitive contradiction, an inferred CD4 predominance, four weak citations, a misread platelet "unsupported" claim and the skipped doublet check.
- **Codex software issue:** `population_stability.csv` label agreement compares exact strings, giving false instability. Not for Sonnet.

## 2026-10-29 — Feedback round 1 and revised draft (revision 1)

- **Request:** the user sent the ten review points as one line, then `quit` (`user_feedback` 21:53:37).
- **Sonnet's answer:**
  - Corrected the denominators and the "not testable at 0.6" wording.
  - Made NK-like, GZMK+ CD8 and FCGR3A+ monocytes tentative in every run.
  - Removed CD4-like predominance.
  - Re-described or dropped the weak PMIDs, removing 34616175.
  - Reported platelet marker detection and stated the doublet check as not done.
  - Moved the ambiguity section to the 36-cell DC-like group.
- **Usage:** 11 Sonnet responses (2,312,388 input, 57,925 output tokens), 4 new inspections, 1 PubMed query that returned nothing. No setting or computed value changed; annotations were re-rendered at 22:01:04.
- **Checks:**
  - All new expression values reproduce (`single_cell/review/check_rev1.py`).
  - All cited PMIDs are in the saved records.
  - Three minor residual issues remain in the accepted report (`REVIEW_NOTES.md` step 3).

## 2026-10-29 — Submission run: acceptance

- **Decision:** the user accepted the report at 22:02:58 (`report_accepted`). The three acceptance notes in `REVIEW.md` record the user's review. `RESULTS.md` is identical to revision 1's `DRAFT.md`.
- **Artifacts at original acceptance (sha256, before the reviewer attribution correction below):**
  - `RESULTS.md` `a2e95d6f…9f194b`
  - `REVIEW.md` `d9d6eea3…ec05d0`
  - `manifest.json` `6436a6be…59913a`
  - `verification.json` `29983fa0…6a47fb`: 2700 raw cells, 2664 retained, 1864 sampled, 4 independent ARIs.
- **Checks after acceptance:**
  - `--verify` against the manifest passed. Stage is `accepted`, and all 31 figures and 63 tables are sealed.
  - The same 36 barcodes form the DC-like cluster at 0.3, 1.0 and 1.5, and the 29 that were sampled form downsample cluster 5 exactly (`single_cell/review/check_dc_overlap.py`). This result is not in `RESULTS.md`.
- **Total run usage:** 31 Sonnet responses, 4,170,468 input and 106,474 output tokens.
- **Not yet done:**
  - Curation into `single_cell/records/RUN_ID/` (CLEAN_RUN §6).
  - The Codex fix to label agreement.
  - PROJECT_PLAN checkpoints and RUBRIC scores, which come after all three tasks.
  - The combined report. When citing `RESULTS.md` there, flag the three minor issues, the unmet plan promise (Jaccard/top-marker overlap) and the DC membership result.

## 2026-10-29: Reviewer attribution correction (Codex documentation)

The user clarified that they acted as the human reviewer and requested corrections to
the review records. Updated `REVIEW_NOTES.md`, the affected entries here, the run's
`REVIEW.md` and its matching `report_accepted` event. The user is now credited for
review, feedback and acceptance. Applied the humanizer skill to the affected prose.

The run's `review_attribution_correction/` folder retains the superseded review,
acceptance event and manifest, with a note explaining the correction. Updated the
manifest entry for `REVIEW.md` and added hashes for those correction records.
`events.jsonl` was not covered by the original manifest; it now includes a dated
correction event. The acceptance timestamp and all other existing events are unchanged.

Resources were the user's clarification and local records. No scientific agent was
queried, no analysis was rerun, and no scientific settings, results or uncertainties
changed. The corrected attribution addresses a documentation error, not a new
scientific finding. File-hash and event-consistency checks passed. The corrected
`REVIEW.md` SHA-256 is `cca201de20435752cb98875ffaa0a21fb4540c5d6e42fcd313dbd49be15be290`;
the updated manifest SHA-256 is `337c9ed2ac1c0b18ed5bb33bf4eabd9f243c854102548e2241fcc908da47b51b`.

## 2026-10-29: Pre-deliverable review and documentation (Codex)

The user requested an artifact review, correction of reviewer attribution, concise
handoffs and an account of clean-run issues. The human reviewer is the user; Claude
remains the analysis agent. Applied the humanizer skill to reader-facing prose.

Checked the accepted run's integrity and numerical verifier, inspected tables and
figures, and reran the relevant independent review checks. The task-level HANDOFF.md
summarizes findings and limits; PRE_DELIVERABLE_REVIEW.md records scope, issues, fixes
and packaging work. Current RESULTS.md includes documented corrections and an explicit
editorial notice. Original responses remain unchanged in api/; pre-edit documentation
and hashes are in archive/2026-10-29-before-deliverable-review/.

No model was contacted and no production computation, threshold, seed or biological
label changed. Resources were the user's clarification, local artifacts, saved sources
and installed verification tools. These checks reproduce numerical evidence and
document known limitations; they do not replace the user's scientific judgment.

## 2026-10-29: Submission packaging, run `20261029T211700335443Z` (Claude Code, claude-opus-5-5)

Copied the run's records, code, runtime/, recovery/ and data/ to
single_cell/records/RUN_ID/ (126 files); figures and tables were already under
single_cell/{figures,tables}/RUN_ID/. All copies hash-match the run folder.

No model was contacted and no computation, setting or result changed.
Excluded: api/, the message history in state.json, caches/.h5ad, DRAFT.md, REVIEW_PACKET.md
(same rule as the Task 3 records). requirements.lock.txt and submission_manifest.json
(repository-relative SHA-256 of 463 shipped files; `python make_manifest.py --check`)
were created for all three tasks. The lock gives imported module versions where the
environment has duplicate package metadata: h5py 3.6.0 and matplotlib 3.9.4.

## 2026-10-29: Report revision, reviewer-added marker sources (Claude Code, claude-opus-5-5; editorial and source review)

Request (user): strengthen external support for the Task 2 labels with primary papers,
checked against their text, and label them as reviewer-added rather than Sonnet's resources.

Resources (retrieved during report review, not by Sonnet): full text via PubMed Central of
Zheng et al. 2017 Nat Commun (PMID 28091601, PMC5241818), Villani et al. 2017 Science
(PMID 28428369, PMC5775029) and Smith et al. 2020 Blood Adv (PMID 32271902, PMC7160259); the
PubMed abstract of Mogilenko et al. 2021 Immunity (PMID 33271118). Text was read through the
WebFetch tool, which returns model-extracted quotes rather than the raw page; claims were kept
narrow for that reason.

Claim to source:
- [1] Zheng: CD3D for T cells; CD8A; NKG7 for NK and cytotoxic T cells; CD79A for B cells;
  S100A8/S100A9 for myeloid cells; FCER1A for DCs; CD16+ monocytes; PF4 for megakaryocytes.
- [2] Villani: CD1C, CLEC10A and FCER1A for CD1C+ DCs; classical (CD14++CD16-) versus
  non-classical (CD14+CD16++) monocytes; IL3RA and CLEC4C are also expressed by AXL+SIGLEC6+
  cells, so they do not by themselves establish pDCs.
- [3] Smith: FCGR3A, GNLY and PRF1 in CD56dim NK cells; GZMK in CD56bright NK cells, so GZMK
  alone does not mark CD8 T cells.
- [4] Mogilenko (abstract only): a GZMK+ CD8+ T-cell population in human blood.
- Not covered: LDHB, MS4A1, LYZ, FCN1, MS4A7, CDKN1C, LILRA4. No source validates the identity of
  these particular cells; labels stay tentative where they were tentative.

Changes: Table 2 cites [1]-[4] per row; Interpretation adds a reviewer-added support bullet, the
GZMK caveat and the IL3RA/CLEC4C caveat; the audit lists [1]-[4] separately from agent resources
and keeps the original citation failures. RUBRIC S2 provisional score 5 -> 6.

No analysis was rerun, no analysis agent was called, and no number, threshold, label or
raw input changed; every value in the pre-revision report is still present in the new report.pdf.
