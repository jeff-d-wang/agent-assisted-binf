# Prompt: draft the combined report (report.pdf)

Write a short, easy-to-read report covering the three finished analyses in this repository. The
readers are the grader and the user, and both need to find each result quickly. The analyses are
already done, accepted and documented. Summarize them; do not redo them.

The report must make three things clear: what the **data showed**, what the **agent inferred**, and
what **external evidence** supports. Prefer short sentences and tables. Do not over-explain.

## Sources (read these, quote only from them)

- `RUBRIC.md` (scoring and evidence index) and `PROJECT_PLAN.md` §6–7 (required content).
- For each task: `<task>/HANDOFF.md`, `<task>/records/RUN_ID/RESULTS.md`, `<task>/REVIEW_NOTES.md`,
  and `<task>/AGENT_LOG.md`. Use the CSVs in `<task>/tables/RUN_ID/` for exact numbers.
- `PRE_DELIVERABLE_REVIEW.md`: use its "Corrections to carry into the report", not the agent's
  original wording.
- `report/figures.md`: Figures 1–8 and their captions.

| Task | Run ID | Analysis agent |
|---|---|---|
| 1 Protein | `4hjo_submission_20261029T200938399152Z` | `claude-sonnet-5-5` |
| 2 Single-cell | `20261029T211700335443Z` | `claude-sonnet-5-5` |
| 3 Spatial | `20261029T222440220672Z` | `claude-haiku-5-5` |

## Rules

- **No invented content.** Every number, PMID and claim must come from a repository file. If one has
  no source, mark it `[TODO]`.
- **No new analysis.** No reruns, API calls or new literature. Do not edit `datasets/`, `runs/`,
  `records/`, `figures/` or `tables/`.
- **Keep uncertain and negative results as they are.** Do not turn them into conclusions.
- **Credit:**
  - The analysis agents (Sonnet, Haiku) planned and interpreted; Python computed.
  - The user reviewed, approved and accepted.
  - Codex wrote the software.
  - Claude Code (`claude-opus-5-5`) packaged the submission.

## Structure (target 6–8 pages including figures)

**Intro (a few lines):** the question for each task, the workflow (Python computes, agent
interprets, user reviews and accepts), the run IDs and models, and how evidence levels are tagged
(**Observed / Inferred / Retrieved**).

**One section per task, each with the same five parts:**
1. **Data and methods:** inputs, key settings, seed. A few bullet points.
2. **Results:** the required figures and tables (below), each followed by a one- or two-sentence
   takeaway.
3. **Interpretation:** what the agent inferred and what external evidence supports, tagged.
4. **Conclusion and uncertainty:** 2–4 bullet points.
5. **Agent Audit:** the four questions below, about ½ page.

Required results per task. Keep these numbers, because `RUBRIC.md` cites them.

| Task | Must include |
|---|---|
| Protein | Protein and mutation info. **Table 1:** one row per mutation with the structure residue, quantitative evidence, observation vs prediction, external evidence and confidence. **Figure 1:** structure. Mechanism per mutation, with literature/database support. |
| Single-cell | **Figure 2:** annotated UMAP. **Table 2:** population, markers, stability across resolutions and after downsampling, confidence. **Figure 3** and **Table 3:** resolution and downsampling robustness. **Figure 4:** ambiguous DC-like population. |
| Spatial | **Figure 5:** expression clusters on UMAP and tissue. Spatial statistic. **Figure 6:** spatially variable genes. **Figure 7:** DE vs spatial ranks. **Figure 8** and **Table 4 (Analysis \| Original \| Randomized):** negative control. |

**Agent Audit (per task), answering these four questions briefly:**
1. **Resources:** datasets, databases, packages, websites and papers. Say "none" where that is true.
2. **Computed vs retrieved:** a two-column table.
3. **Independent check:** what was checked, with which script in `<task>/review/`, and the result.
4. **Weakness:** one or two real problems with the agent's work, how we noticed them, and how we
   handled them.

**Limitations and reproducibility (short):** shared limits, and where the code, settings, versions
(`requirements.lock.txt`) and manifest are.

**References:** only sources found in the saved records (PMIDs, UniProt, PDB, datasets, key
software).

**Checkpoint evidence index (one table):** Checkpoint | Status | Page | Figure/Table | Files. Cover
P1–P4, S1–S5, T1–T5, the three audits and the reproducibility items. Take Status and Files from
`RUBRIC.md`. No scores.

## Render and check

```bash
cd report && pandoc report.md -o ../report.pdf --pdf-engine=xelatex \
  -V geometry:margin=2cm -V fontsize=10pt -V colorlinks=true --resource-path=.
```

- Write the source to `report/report.md`. Image paths are relative to `report/`, for example
  `../protein/figures/RUN_ID/structure_annotated.png`.
- Render once, fill the Page column of the index, then render again.
- Check that:
  - figures are legible;
  - tables fit the page (shorten text rather than shrinking the font);
  - no `[TODO]`, key or `/Users/` path remains.

Then run `python make_manifest.py && python make_manifest.py --check`.

**Report back:**
- The page count.
- Any `[TODO]`s.
- Claims where you were unsure of the evidence level.
- The page for each checkpoint.

Do not edit `RUBRIC.md` scores or `PROJECT_PLAN.md` checkboxes.
