# AGENT_LOG — Task 1 (Protein mutations)

Current submission summary: `HANDOFF.md`. The user was the human reviewer for the
2026-10-29 submission run. Dated entries below preserve the history of plans, checks,
feedback and maintenance; earlier analyst credits refer to historical work.


Historical practice case: **4HJO** (EGFR kinase domain + erlotinib). Submission eligibility remains
unconfirmed. The scripts accept structure, UniProt accession and mutation arguments but have
structural constraints; the earlier claim that they run on any protein was too broad. See README.md.

## 2026-10-28 — Analysis plan

- **Prompt:** "Read the Task 1 section of PROJECT_PLAN.md. Propose an analysis plan with data, packages,
  methods, and parameters, and why. Don't run anything yet."
- **Agent:** Claude Code (Opus 5.5), VS Code extension. *(PROJECT_PLAN.md names ChatGPT as the analysis agent; this task was run with Claude Code.)*
- **Answer (summary):** UniProt for sequence and features, RCSB mmCIF/PDB for coordinates, PDBe SIFTS
  for the residue mapping, cross-checked by an independent sequence alignment. Biopython for distances,
  SASA and mapping, PyMOL for the figure. Minimum heavy-atom distance as the measurement rule, a 5 Å contact
  cutoff, and RSA < 0.25 as "buried". Interpretation keeps observation / prediction / external evidence apart.
  FoldX/Rosetta ΔΔG and a custom conservation MSA were skipped (license, setup cost, not needed to separate the candidates).
- **User decisions:** use 4HJO as the test case; inputs are `datasets/4hjo.cif.gz` and `datasets/4hjo.pdb`
  (delivered as `4hjo.pdb.txt`); PyMOL via Homebrew is approved.

## 2026-10-28 — Step 1: mutation check and residue mapping (P1) — `01_map.py`

- **Candidates (chosen by the agent; no list was assigned):** G719S, T790M, C797S, L858R, L861Q. These are
  well-characterised EGFR kinase-domain variants that span the P-loop, gatekeeper, solvent-front/covalent-drug
  site and activation loop. HGVS/UniProt numbering (P00533 precursor, including the 24-aa signal peptide).
- **Resources (retrieved):**
  - UniProt P00533 JSON: `https://rest.uniprot.org/uniprotkb/P00533.json` (entry/sequence versions in `data/provenance.json`; saved to `data/P00533.json`)
  - PDBe SIFTS: `https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/4hjo` (saved to `data/4hjo_sifts.json`)
  - `datasets/4hjo.cif.gz`, sha256 `391217cf…a6d81e`
- **Packages:** Python 3.9.15, Biopython 1.85, NumPy (see `requirements.lock.txt` once frozen).
- **Settings:** chain A. Global alignment: BLOSUM62, gap open −10, extend −0.5, free end gaps. No randomness.
- **Computed:**
  - Wild-type identity in UniProt and in the structure for every candidate (the script exits on mismatch).
  - UniProt → label_seq → author number via SIFTS, and separately via alignment. The two must agree or the script exits.
- **Observed:**
  - **Author numbering = UniProt − 24** (mature-protein numbering). L858R is author residue 834 in the file.
  - Construct differences: N-terminal expression tag (MKKGHHHHHG), **engineered V948R** (author 924;
    asymmetric-dimer interface mutation).
  - All five candidates are observed, with complete side chains. Unobserved segments: author 662–678,
    710–713 (UniProt 734–737), 961–972 (UniProt 985–996).
  - Retrieved: UniProt curates G719S, T790M, L858R and L861Q as lung-cancer variants with functional notes.
    **C797 has no UniProt variant annotation** (`tables/uniprot_variants.csv`).
- **Checks:**
  - SIFTS and the alignment agree at all candidate and functional positions.
  - Negative tests: `--mutations V948A` exits with "structure has R at author 924" (catches the
    engineered construct mutation); `--mutations A858R` exits with "UniProt has L at 858". Both behaved as intended.
- **Agent weaknesses:**
  - In the planning answer the agent assumed 4HJO "should" use UniProt numbering. It does not (offset −24).
    This was caught by the DBREF record and confirmed by the script.
  - While drafting, the agent recalled a wrong PMID for the 4HJO paper. The correct one (23101586, read from
    the mmCIF `_citation`) replaced it. All other cited PMIDs were checked against NCBI esummary (below).

## 2026-10-28 — Step 2: structural measurements (P2) — `02_measure.py`

- **Input:** `datasets/4hjo.pdb.txt` (same deposition as the mmCIF; the script defaults to `datasets/4hjo.pdb`).
- **Rules:**
  - Distance: minimum heavy-atom distance (H and water excluded). Ligand: AQ4 (erlotinib); additives list excluded, none present.
  - Contacts: any heavy atom within 5.0 Å.
  - RSA: Shrake–Rupley on protein only, divided by the Tien 2013 theoretical max ASA. Buried if < 0.25.
  - Ligand-contact SASA = SASA(apo) − SASA(with ligand).
  - Relative B = residue mean B / chain mean B.
  - Physico-chemistry: Kyte–Doolittle hydropathy, Zamyatnin volume, BLOSUM62, charge at pH 7.
- **Computed:** `tables/measurements.csv`, `tables/contacts_5A.csv`.
- **Agent weakness (found in own output):** the first version reported G719's "nearest functional residue"
  as S720 at 1.32 Å, which is just the peptide bond to the next residue. Fixed by excluding i±1 from that
  metric. Contacts still include i±1, and the docstring says so.
- **Caveat:** RSA is computed on a monomer with missing loops. Residues near the unobserved segments
  (e.g. around 734–737) may appear more exposed than in the full protein. None of the candidates is adjacent to a gap.

## 2026-10-28 — Literature verification (retrieved)

PMIDs checked with NCBI E-utilities esummary (first author / year / journal / title matched):
15118125 Paez 2004 Science; 15118073 Lynch 2004 NEJM; 16205628 Chen 2006 Oncogene; 17349580 Yun 2007
Cancer Cell; 18227510 Yun 2008 PNAS; 15728811 Kobayashi 2005 NEJM; 25939061 Thress 2015 Nat Med;
16777603 Zhang 2006 Cell; 23101586 Park 2012 Biochem J (4HJO). Abstract-level claims are taken from
these papers' titles and the UniProt curation. Full texts were not re-read in this session.

## 2026-10-28 — Step 3: annotated structure + independent check (P2, P4) — `03_render.py`

- **Tool:** PyMOL 3.1.0 (Homebrew, own Python 3.14). Run: `pymol -cq protein/03_render.py -- datasets/4hjo.pdb`.
- **Independent verification:** for each mutation → erlotinib distance from Biopython, PyMOL's own parser
  and selection engine found 0 atoms closer than d − 0.01 Å and ≥ 1 atom within d + 0.01 Å. **5/5 agree**
  (`tables/pymol_check.csv`).
- **Second check:** the claim that L858 and L861 sit in an activation-loop helix was re-verified from the
  deposited HELIX records (author 833–838 = UniProt 857–862; αC = UniProt 755–769). The first reading
  came from a misaligned awk column split and was only trusted after the fixed-column re-parse.
- **Agent weaknesses (figure):**
  - First renders: labels hidden behind the cartoon; G719S/C797S labels overlapping; two mutations in
    near-identical magenta/purple.
  - Fixes: labels pulled toward the camera, collision-aware placement, distinct palette.
  - A whole-domain overview still put the L858R label on L861's sphere, so it was **dropped** rather than
    shipped as a misleading figure. Only the binding-cleft view is kept.

## 2026-10-28 — Step 4: interpretation (P3) — `RESULTS.md`

- **Computed vs retrieved:**

  | Item | Computed here | Retrieved |
  |---|---|---|
  | WT check, UniProt ↔ structure mapping, numbering offset | ✔ (alignment) | SIFTS segment map |
  | Distances, 5 Å contacts, RSA, ligand-covered SASA, relative B | ✔ | |
  | Physico-chemical deltas | ✔ (from fixed published scales) | scales: KD 1982, Zamyatnin 1972, Tien 2013, BLOSUM62 |
  | Domain, ATP-binding and catalytic residues | | UniProt P00533 |
  | Secondary structure (A-loop helix, αC) | | deposited HELIX records |
  | Variant functional effects, drug response | | UniProt curation + PubMed papers |
  | Mechanistic predictions | agent inference (not computed, not retrieved) | |

- **Agent weakness (scientific):** from distance alone the agent's first prediction for T790M was steric
  clash with erlotinib. Yun et al. 2008 (PMID 18227510) show the main resistance mechanism is increased
  ATP affinity. Kept in RESULTS.md as an explicit contradiction rather than rewritten away.
- **Uncertain results kept:**
  - C797S has no UniProt annotation and no evidence in our sources for a change in intrinsic activity.
  - G719S's mechanism is only weakly supported by our measurements.
  - G719 (5.06 Å) and L858 (5.26 Å) sit at the arbitrary 5 Å cutoff.

## 2026-10-28 — Standalone Claude workflow implementation (Codex development)

- **User request:** Implement the agreed JSON-preset workflow, with Claude as the only runtime
  analysis agent and Codex solely developing code; summarize verification and remaining work.
- **Answer/implementation:** Added `run_analysis.py`, `cases/4hjo.json`, Task 1 setup instructions
  and offline tests. Python calls the Claude Messages API directly, presents plan approval,
  executes the numbered scripts, supplies actual tables and the structure image, supports
  PubMed retrieval and contact-cutoff sensitivity, and saves user-reviewed reports and audit records.
  Runs are isolated under `protein/runs/`; credentials stay in the environment. Historical Claude
  Code work is not relabeled as work produced by the new API workflow.
- **Resources:** Existing raw `datasets/4hjo.cif.gz` and `datasets/4hjo.pdb` (unchanged), cached
  UniProt P00533/SIFTS inputs, Python 3.9.15, Biopython 1.85, NumPy 1.25.2, PyMOL 3.1.0.
  Claude API documentation consulted: https://platform.claude.com/docs/en/api/messages/create,
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools,
  https://platform.claude.com/docs/en/models/overview. Preset model: `claude-sonnet-5-5`.
- **Settings:** Baseline methods unchanged: chain A, 5 Å contacts, RSA < 0.25; sensitivity uses
  4/5/6 Å. Scientific calculations are deterministic, so no random seed. API requests use
  max_tokens=8192 and an explicit model; exact requests/responses and usage are saved. At most
  10 API turns per user exchange; no arbitrary code execution tools.
- **Computed versus retrieved:** Recomputed the local mapping, structural measurements,
  PyMOL figure/check and sensitivity table. Reused cached database inputs. Separately tested
  live PubMed retrieval of PMID 18227510: the expected title and a nonempty abstract were returned.
  No Claude API response or new biological interpretation was generated: no API key is configured.
- **Checks:** Both input files match at all 2,264 heavy atoms in chain A. All six baseline CSVs
  match the historical outputs exactly. All five PyMOL ligand-distance checks pass. The figure
  was visually inspected. Offline tests exercise approval before execution, pause/resume,
  follow-ups and acceptance, mismatched inputs, invalid config, artifact tampering, API failure,
  truncated output, unsupported tools and PubMed parsing. Fixture responses are labeled as tests,
  never used as scientific evidence. Verification summaries and run paths are in VALIDATION.md.
- **Weaknesses found/corrected:** Codex initially proposed itself as a runtime intermediary;
  the user corrected that design. The implementation has no Codex dependency. The historical
  report said four buried sites, but the CSV marks all five below the cutoff; corrected the
  count and removed the unsupported implication that burial establishes a strong effect.
  The two input files are now checked before any paid call; an altered-coordinate fixture fails.
- **Remaining:** Run with real Claude credentials, review its sources and conclusions, exercise
  a scientific follow-up, accept only supported claims, confirm the assigned submission case,
  then finalize rubric scores and report evidence. Existing practice artifacts are not proof
  that the new live API workflow has completed Task 1.

## 2026-10-29 — Fresh Sonnet submission setup (Codex development)

User requested fresh Tasks 1–3, old-run cleanup, Sonnet instead of Haiku, and a separate reviewer. The user explicitly confirmed: “Use 4HJO for the submission.” Updated the active preset to `4hjo_submission` / `claude-sonnet-5-5` and removed the prior practice-only restriction for new runs. Historical root practice artifacts and archived model attribution are unchanged. Three prior protein runs were archived, byte-verified, under `archive/2026-10-29-before-sonnet/`; see its manifest for original paths. The new run, scientific review and final report remain pending.

Resources: existing code/tests and Anthropic's model overview (https://platform.claude.com/docs/en/models/overview, consulted 2026-10-29, documents `claude-sonnet-5-5`). Computed: local input preflight and 13 offline tests passed; no new scientific result, retrieval or live model call. Baseline scientific methods are unchanged and deterministic. Weakness addressed: prior practice-only labels would misstate the now user-selected submission scope; current instructions updated while historical records were preserved. See CLEAN_RUN.md for exact fresh-run, reviewer, audit and report steps. API access/credentials must be supplied by the user; not live-tested by Codex.

## 2026-10-29 — Sonnet output-budget adjustment (Codex maintenance)

User reported a max-token failure in protein run `4hjo_submission_20261029T200938399152Z` and requested reasonable limits for all tasks. Saved response `api/005.response.json` reported `stop_reason=max_tokens`, 16,000 output tokens, including 9,881 thinking tokens; request-to-response elapsed time was approximately 113 seconds. These are retrieved execution records, not new scientific results. Anthropic documentation confirms reasoning and text share max_tokens: https://platform.claude.com/docs/en/build-with-claude/thinking (consulted 2026-10-29).

Changed this task's per-response cap from 16,000 to 32,000 and HTTP timeout from 180 to 360 seconds. Model, scientific methods/seeds, report-length instructions and truncation rejection are unchanged. All 13 protein tests passed, including request cap, HTTP timeout, truncated-draft rejection and resume behavior. Original run inputs and evidence manifest passed integrity checks. No live API request, scientific analysis or package change was made. Higher caps are upper bounds and may increase cost/latency; they cannot guarantee completion.

Weakness evaluated: the earlier caps left insufficient combined reasoning/report room for the observed Sonnet response. The protein run's original snapshot and truncated response are retained; a separate runtime copy, hashes and change note document the adjustment. Resume that run at interpretation using the updated root script. New Task 2/3 runs inherit the new limits; no existing Task 2/3 runtime snapshots were altered.

## 2026-10-29 — Submission run: plan gate (Sonnet)

- **Run:** `4hjo_submission_20261029T200938399152Z`, analysis agent `claude-sonnet-5-5` via `protein/run_analysis.py` (`PLAN.md`, `api/001`–`002`).
- **Request/answer:**
  - The program asked for a feasible plan before any analysis.
  - Sonnet proposed: SIFTS plus alignment mapping; minimum heavy-atom distances to erlotinib and functional sites; 5 Å contacts with a 4/5/6 Å sensitivity check; Shrake–Rupley RSA < 0.25; relative B-factors; physicochemical deltas; a PyMOL figure and distance check; one PubMed query per substitution. Kinase activity and drug response were kept as separate axes.
- **Independent review:** the user (human); see `REVIEW_NOTES.md`, step 1. Plan §3.2 promised distances to literature landmarks (hinge, DFG, αC-helix, activation loop), but `01_map.py` only uses UniProt Active/Binding sites and cannot add residues.
- **User decision:**
  - Revision sent 20:14 UTC: "Functional sites are limited to UniProt Active/Binding site features; the program cannot add residues, so drop the plan to compute distances to non-UniProt landmarks. You may name structural elements (αC-helix, activation loop, P-loop, hinge) only as retrieved literature context with a PMID, never as a computed measurement. Keep the 5 Å baseline and the PubMed scope as proposed."
  - Sonnet removed the landmark distances.
  - Approved 20:15 UTC; `PLAN.md` sha256 `ff605cf4…b8bcae`.
- **Settings:** chain A; 5 Å contacts; RSA < 0.25; deterministic, so no seed. Inputs `datasets/4hjo.cif.gz` and `datasets/4hjo.pdb` (hashes in `input_checks.json`).
- **Agent weakness:** the first plan promised an analysis the software cannot run (unexecutable "measurements"). It was caught at the gate and removed before any computation.

## 2026-10-29 — Submission run: computation (Python)

- **Computed** (20:15 UTC, all three steps exit 0, `step_1-3.log`):
  - `tables/mapping.csv`, `functional_sites.csv`, `uniprot_variants.csv`, `measurements.csv`, `contacts_5A.csv`, `pymol_check.csv`
  - `figures/structure_annotated.png`
  - `verification.json`: 5 candidates, 5/5 ligand distances verified, 5 buried, none missing
- **Retrieved:** UniProt P00533 (entry version 301, sequence version 2) and SIFTS 4hjo; hashes in `data/provenance.json`.
- **Packages:** Python 3.9.15, Biopython 1.85, NumPy 1.25.2, PyMOL 3.1.0.
- **Observed:**
  - Offset −24, with SIFTS and the alignment in agreement.
  - One construct difference, V948R (author 924).
  - Ligand AQ4 only.
  - Erlotinib distances: T790 3.48 Å, C797 3.54 Å, G719 5.06 Å, L858 5.26 Å, L861 9.22 Å.

## 2026-10-29 — Submission run: interpretation, output-limit failure and first draft

- **Request/answer:**
  - Sonnet received the evidence packet and image (`api/003`–`005`). It ran `contact_sensitivity` and 9 PubMed queries, 4 of which returned nothing.
  - Response 005 stopped at `max_tokens` (16,000). Codex raised the cap (see the maintenance entry above).
  - On resume, interpretation restarted from the stage start (`api/006`–`007`), with `contact_sensitivity` and 5 new queries. Response 007 became the first `DRAFT.md`.
- **Computed vs retrieved:**
  - Computed: cutoff sensitivity at 4/5/6 Å (`tables/contact_sensitivity.csv`). Ligand contact for G719 and L858 appears only at 6 Å; T790 and C797 are within 4 Å at every cutoff.
  - Retrieved: PubMed titles and abstracts only, plus UniProt variant text. Mechanisms are Sonnet's inference.
- **Agent weaknesses:**
  - The retry silently dropped the first attempt's 9 queries and results, including PMID 22349823 (structures of G719S and L858R).
  - The audit reported 5 queries.
  - Other weaknesses were found in review (next entry).

## 2026-10-29: Independent review of first draft (human reviewer)

- **Reviewer:** the user (human), reviewing without changing the run. Summary and check outcomes are in `REVIEW_NOTES.md`, step 2.
- **Checks (independent methods; scripts in `protein/review/`):**
  - `check_dist.py` (plain-text PDB parse + numpy, no Biopython): mapping, offset and all checked minimum distances **match the run to 0.01 Å**. R948 is 22–31 Å from all candidates.
  - `check_sasa.py` (PyMOL SASA at dot densities 2/3/4):
    - G719 RSA is 0.240–0.247 and C797 is 0.228–0.234. Both are still below 0.25, but within about 0.02 of the cutoff.
    - L858 and L861 are clearly buried.
  - **Sources:** all 12 cited PMIDs exist in `data/pubmed_*.json`, and every quoted claim matches its abstract.
- **Agent weaknesses found:**
  1. Sequence-neighbour contacts were presented as functional proximity: L858 to D855 at i−3, and G719 to V726 and T725 within its own annotated stretch. The long-range contacts were left out: L858 to K745, L788 and M766; L861 to E762, M766 and I759.
  2. The retry lost 22349823.
  3. The drug axis merged "more sensitive than WT" with evidence that G719X and L861Q are less sensitive than L858R.
  4. Audit weakness 7 was wrong: 18227510 calls T790 the gatekeeper.
  5. The figure has no legend, and its spheres are Cα atoms.
- **Reviewer weakness:** in Review 1 the user gave the unobserved segments in author numbering without saying so, then corrected them to UniProt 734 to 737 and 985 onward. The conclusion was unchanged.

## 2026-10-29 — Feedback rounds 1–2 and revised draft

- **Round 1 (user, 20:49 UTC):**
  - Multi-line feedback was pasted at the review prompt, which reads one line with `input()`. Only "Revise the draft; do not change computed values." reached Sonnet (`events.jsonl` `follow_up`).
  - Sonnet ran 12 queries (6 long ones returned nothing) and revised without the specific points (`api/008`–`010`).
- **Round 2 (user, 20:55 UTC):**
  - The same five points were sent as one line, followed by `quit`, through `--resume` (`api/011`–`012`). The key was loaded from `.env` and not displayed.
  - Sonnet queried the 22349823 title, its PMID and "EGFR V948R". It returned a revised `DRAFT.md` and listed every change.
- **Resources (cited in the revised draft, 27 PMIDs):** 18227510 22349823 29802850 31855568 34319231 36188595 37196448 38523074 38850084 39358400 40277759 41872782 42388639 42466433 42514920 42583967 42637134 42656146 42691523 42711860 42719457 42735369 42757013 42835192 42858544 42868668 42906389. All are abstract-only.
- **Usage:** 12 Sonnet responses across the run, 570,025 input and 80,558 output tokens.
- **Checks:**
  - All five points were addressed.
  - The query total of 29 matches a recount from `events.jsonl` (9 + 5 + 12 + 3).
  - All 27 PMIDs are in the saved records. New claims checked against abstracts are supported, including 29802850 ("abolishes the covalent bonding").
- **Agent weaknesses still in the revised draft** (`REVIEW_NOTES.md`, step 4):
  1. A misquotation: "Threshold 790" instead of "Threonine 790".
  2. An unsupported statement that the 22349823 L858R structure is in the active conformation.
  3. The spheres are described as "likely Cα", although `03_render.py` line 80 shows they are Cα.
  4. The first retained query round is misdescribed.
  5. Sonnet notes that two key sources came from user instructions or an incidental hit, not from its own searches.
- **Workflow weakness:** the single-line review prompt silently truncates pasted feedback. Feedback must be entered as one line or piped in.
- **Status at this gate:** the draft was in review. It was accepted later (next entry).

## 2026-10-29 — Submission run: user acceptance

- **Decision:** the user typed `accept` at 21:06:55 UTC (`events.jsonl` `report_accepted`). The four remaining fixes were **not** sent to Sonnet. `RESULTS.md` is byte-identical to the round-2 `DRAFT.md` (response 012), so the "Threshold 790" misquote, the unsupported active-conformation claim, the "likely Cα" wording and the misdescribed query round all remain in the accepted report.
- **Review notes:** entered by the user and saved verbatim in `REVIEW.md`. They record:
  - the independent distance and RSA checks;
  - the plan overpromise, the lost retry evidence and the sequence-local contacts as agent weaknesses;
  - the misquote and the active-conformation claim as unresolved in the report;
  - unresolved science: the L858R, L861Q and G719S mechanisms, C797S intrinsic activity, and the drug-sensitivity ordering.

  The square brackets around the unresolved-items clause are literal text from the suggested note.
- **Artifacts:**
  - `RESULTS.md` sha256 `aa1e0d8c…7c4e70`
  - `REVIEW.md` sha256 at acceptance `f49091d2…eaa873` (see the formatting correction below)
  - `manifest.json` sha256 at acceptance `1b215735…96e518` (before that correction)
  - `verification.json` unchanged: 5 candidates, 5/5 ligand distances verified.
- **Check:** the reviewer recomputed all 81 manifest hashes read-only after acceptance. All match, and `RESULTS.md` and `REVIEW.md` are sealed. Run stage is `accepted`.
- **Not yet done:**
  - Curation into `protein/figures/RUN_ID/`, `protein/tables/RUN_ID/` and `protein/records/RUN_ID/` (`CLEAN_RUN.md` §6).
  - PROJECT_PLAN checkpoints and RUBRIC scores, which come after all three tasks.
  - The combined report. When citing `RESULTS.md` there, correct or flag the four known issues listed in `REVIEW_NOTES.md`, step 4.

## 2026-10-29: Reviewer attribution correction (Codex documentation)

The user clarified that they acted as the human reviewer. Updated `REVIEW_NOTES.md`
and the submission-run review and feedback entries here to credit the user. Applied
the humanizer skill to the affected prose. Historical analysis-agent attribution
remains unchanged.

Resources were the user's clarification and existing local records. No scientific
agent was queried, no analysis was rerun, and no scientific settings, check results
or uncertainties changed. This corrects a documentation error.

The integrity check also found existing paragraph-spacing changes in the run's
`REVIEW.md`. Reconstructing the original review from the acceptance event reproduced
the recorded hash `f49091d2dad240dd71691ac769d48ae55b53c4773b5cddc0bde242e0f7eaa873`.
The current review differs only in whitespace. Updated its manifest entry to
`85adadf41f7e50e183e57db25d8b325426b37d2c446c340bcbb0533e3a56186a` without editing
the review or acceptance event. All protein manifest hashes now match.

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

## 2026-10-29: Submission packaging, run `4hjo_submission_20261029T200938399152Z` (Claude Code, claude-opus-5-5)

Copied the run's figures/ (without .pse) to protein/figures/RUN_ID/, tables/ to
protein/tables/RUN_ID/ and its records and code to protein/records/RUN_ID/ (86 files).
All copies hash-match the run folder.

No model was contacted and no computation, setting or result changed.
Excluded: api/, the message history in state.json, caches/.h5ad, DRAFT.md, REVIEW_PACKET.md
(same rule as the Task 3 records). requirements.lock.txt and submission_manifest.json
(repository-relative SHA-256 of 463 shipped files; `python make_manifest.py --check`)
were created for all three tasks. The lock gives imported module versions where the
environment has duplicate package metadata: h5py 3.6.0 and matplotlib 3.9.4.

## 2026-10-29: Report revision, structure and mechanism wording (Claude Code, claude-opus-5-5; editorial and source review)

Request (user): qualify "wild type" and keep the measured C797 proximity separate from the
covalent-inhibitor mechanism.

Changes: the structure is described as wild type at the five candidate sites with the
engineered V948R substitution (methods, Figure 1 caption, uncertainty). The C797S prediction
now says the covalent mechanism is not testable in this erlotinib complex. The conclusion
attributes the T790M and C797S drug-response effects to the literature and states that the
erlotinib contacts do not demonstrate either mechanism. No mutant modelling, dynamics or
affinity claim was added.

No analysis was rerun, no analysis agent was called, and no number, threshold, label or
raw input changed; every value in the pre-revision report is still present in the new report.pdf.
