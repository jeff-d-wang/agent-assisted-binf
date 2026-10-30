# Task 1: reviewed findings for the report

Run: `4hjo_submission_20261029T200938399152Z`. Analysis agent: Claude Sonnet
(`claude-sonnet-5-5`). The user reviewed the plan, challenged the draft, checked the
evidence and accepted the report on 2026-10-29. Codex maintained the software and
edited this summary; it did not act as the scientific analysis agent.

## What the data support

The input is the erlotinib-bound, inactive EGFR structure 4HJO, chain A, at 2.75 Å.
All five sites map correctly: author numbering is UniProt numbering minus 24.
The structure includes the engineered V948R difference, 22 to 31 Å from the candidates.
Measurements describe the unmutated candidate sites in this construct. No mutant
structure, dynamics, activity or binding affinity was calculated.

| Mutation | Author residue | Erlotinib distance, Å | Relative solvent accessibility | Interpretation and evidence |
|---|---|---|---|---|
| G719S | 695 | 5.06 | 0.232 | Borderline ligand proximity. Local packing or flexibility is a hypothesis. UniProt and PMID 22349823 support increased activity; drug comparisons need their own comparators. |
| T790M | 766 | 3.48 | 0.182 | Close to erlotinib. Geometry suggests a steric effect, but PMIDs 18227510 and 22349823 support increased ATP affinity as a resistance mechanism. |
| C797S | 773 | 3.54 | 0.238 | Close to erlotinib. PMID 29802850 supports loss of covalent inhibitor attachment. Its intrinsic kinase-activity effect remains unknown. |
| L858R | 834 | 5.26 | 0.096 | Buried, with contacts to K745, L788 and M766. Packing effects are hypotheses; UniProt and PMID 22349823 support increased activity. |
| L861Q | 837 | 9.22 | 0.024 | Buried and distant from erlotinib, with contacts to E762, M766 and I759. The proposed indirect mechanism is untested; UniProt supports increased activity. |

The buried threshold was 0.25. G719 and C797 are close to it; independent PyMOL
estimates also place them just below it. T790 and C797 contact the ligand at every
4/5/6 Å cutoff; G719 and L858 do so only at 6 Å. Sequence-adjacent contacts are not
independent evidence of functional proximity.

## What the user changed through review

The user removed a plan to measure landmarks the software could not identify,
challenged sequence-local contacts as mechanistic evidence, recovered literature
missed after the token-limit failure, and separated incompatible drug comparisons.
Independent parser checks reproduce mapping and distances to 0.01 Å. PyMOL provides
a second solvent-accessibility calculation. Source checks use saved abstracts,
not full papers. The review scripts are in `protein/review/`.

The report must keep these comparisons separate: UniProt's gefitinib sensitivity
versus wild type; G719S/L858R sensitivity without a stated comparator in PMID 22349823;
G719X group evidence versus classical mutations in PMID 42735369; and the L861Q model
comparison with exon 19 deletion/L858R in PMID 37196448. They do not establish one
drug-response ranking.

## Limits and presentation

One inactive construct cannot establish mutant mechanisms. Abstract-only evidence,
wildcard G719X results, case reports and missing primary papers limit confidence.
Do not infer a small C797S activity effect from missing evidence or call the L858R
structure in PMID 22349823 active without supporting evidence.

Use the structure figure with a caption: yellow sticks are erlotinib; colored spheres
mark candidate Cα atoms; side-chain sticks show the existing residues; blue marks D837.
Mutation labels identify proposed substitutions, not modeled mutants. Some labels
overlap the structure, so inspect the figure at final report size.

Full evidence: `runs/4hjo_submission_20261029T200938399152Z/RESULTS.md`, `tables/`,
`figures/`, `data/`, `verification.json` and `REVIEW.md` within that run.
See `REVIEW_NOTES.md` for the review history and `../PRE_DELIVERABLE_REVIEW.md` for
remaining packaging work. Historical root-level practice outputs are not this submission.
