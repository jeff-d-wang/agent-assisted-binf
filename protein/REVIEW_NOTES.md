# Task 1 independent review

- **Run:** `protein/runs/4hjo_submission_20261029T200938399152Z` (analysis agent `claude-sonnet-5-5`)
- **Reviewer:** the user (human), 2026-10-29. Verification rests on the independent checks below.
- **Check scripts:** `protein/review/check_dist.py`, `protein/review/check_sasa.py`
- **Accepted by the user:** 21:06:55 UTC. Review notes are in the run's `REVIEW.md`.

## What happened

1. **Plan review.** Sonnet's plan promised distances to literature landmarks (αC-helix, activation loop, DFG, hinge). The software only uses UniProt Active/Binding sites, so those distances could never be computed. The user sent a revision that removed them and allowed structural-element names only with a PMID, then approved the plan.
2. **Draft review.** The computed numbers were correct, but the interpretation had these problems:
   - **Sequence neighbours treated as functional proximity:** L858 to D855 (i−3), and G719 to V726/T725, which sit in G719's own annotated stretch. The long-range contacts were not used: L858 to K745, L788 and M766; L861 to E762, M766 and I759.
   - **Lost evidence:** the retry after the output-limit failure dropped 9 earlier queries, including PMID 22349823 (structures of G719S and L858R), and the audit undercounted queries.
   - **Merged drug-response comparisons:** "more sensitive than wild type" was merged with evidence that G719X and L861Q are less sensitive than L858R.
   - **Audit errors:** a wrong statement about the T790 gatekeeper source, and an unresolved question about the nearest-residue rule.
   - **Figure:** no legend, and the spheres were not identified.
3. **Feedback.**
   - **Round 1:** only the first line of the pasted feedback was sent, because the prompt reads one line.
   - **Round 2:** all points were sent as one line, and Sonnet addressed all five.
4. **Revised draft review.** The fixes held, and all 27 cited PMIDs matched their saved abstracts. Four small issues remained and were left in the accepted report:
   - the misquote "Threshold 790" (the abstract says Threonine 790);
   - an unsupported claim that the 22349823 L858R structure is in the active conformation;
   - the spheres described as "likely Cα" (they are Cα, per `03_render.py` line 80);
   - a misdescribed query round.

## Independent checks

| Check | Method | Outcome |
|---|---|---|
| Mapping and −24 offset | `check_dist.py`: plain-text PDB parse, compared with the UniProt sequence | Agrees; V948R confirmed at author 924 |
| Minimum heavy-atom distances | `check_dist.py`: numpy, no Biopython | All match the run to 0.01 Å; R948 is 22 to 31 Å from every candidate |
| Burial near the RSA 0.25 cutoff | `check_sasa.py`: PyMOL SASA at dot densities 2, 3 and 4 | G719 0.240 to 0.247, C797 0.228 to 0.234: buried, but within about 0.02 of the cutoff |
| Cited sources | Each claim compared with its saved abstract in `data/pubmed_*.json` | All exist and support the claims, apart from the two unresolved items above |
| Evidence integrity after acceptance | Recomputed all 81 manifest hashes | All match |

## Still uncertain

- Mechanisms for L858R, L861Q and G719S: there is one inactive, engineered-monomer crystal and no mutant modelling.
- Whether C797S affects intrinsic kinase activity.
- The drug-sensitivity ordering among G719S, L858R and L861Q.
- Why T790M causes resistance: the geometry suggests steric blocking, but the literature (18227510, 22349823) says increased ATP affinity.

## Reviewer error

In the plan review, the user gave the unobserved segments in author numbering without saying so, then corrected them to UniProt 734 to 737 and 985 onward. The conclusion was unchanged.

## Before deliverable preparation

The user requested a concise handoff and correction of reviewer attribution. See
HANDOFF.md for the short version. The pre-deliverable pass reproduced the numerical
checks and corrected the documented residual wording in the run's RESULTS.md, with
an editorial notice. The original model response remains in api/. Earlier review
entries above describe what the user saw at acceptance, before these editorial fixes.
Scientific uncertainty and omitted analyses remain explicit. See
../PRE_DELIVERABLE_REVIEW.md for the check scope and remaining packaging work.
