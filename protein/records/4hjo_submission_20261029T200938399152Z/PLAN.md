# Revised analysis plan: EGFR kinase domain (4HJO chain A), five substitutions

This plan covers what I intend to do after approval. I have run no analysis and draw no conclusions here.

## What changed from the previous plan
- **Functional sites** are now only UniProt **Active site** and **Binding site** features for P00533. I removed the plan to add literature-derived landmarks. No distance is computed to anything outside those features.
- **Structural element names** (αC-helix, activation loop, P-loop, hinge, and similar) are retrieved literature context only.
  - I will use one only when a retrieved PubMed record supports it, and I will give the PMID and URL.
  - I will never present one as a computed measurement.
  - If no PMID supports a name, I will leave it out and not use it from memory.
- **Unchanged:** the 5 Å baseline cutoff and the PubMed scope (activity and inhibitor response, one focused query per exact substitution).

## 1. Scope and question
- **Protein:** EGFR (UniProt P00533), kinase domain. Structure is 4HJO chain A, the inactive kinase with erlotinib, X-ray, 2.75 Å.
- **Candidates:** G719S, T790M, C797S, L858R, L861Q (UniProt numbering).
- **Question:** which substitutions are likely to affect function, and by what mechanism? I will treat **kinase activity** and **drug response** as separate axes.

## 2. Sources and evidence types
| Source | Use | Evidence type |
|---|---|---|
| Supplied 4HJO files (SHA-256 logged) | All geometry | Coordinate observation |
| UniProt P00533 features (Domain, Active site, Binding site, and variant annotations) | Functional-site definition, and exact-substitution checks | Retrieved |
| SIFTS plus sequence alignment | UniProt-to-PDB numbering | Computed, cross-checked |
| Program output (distances, contacts, SASA/RSA, B-factors, physicochemical deltas) | Quantitative structure on the wild type | Computed |
| PubMed via `search_pubmed` | Substitution-specific evidence, plus literature context for named structural elements | Retrieved, abstract-level |

## 3. Methods and parameters
1. **Mapping and validation (P1).**
   - Map UniProt to PDB numbering by SIFTS and by alignment, and require the two to agree.
   - Confirm a single constant offset and that chain A is the only chain used.
   - Confirm the wild-type residue at each position matches the notation (G719, T790, C797, L858, L861).
   - Report missing residues and construct differences near the sites.
   - Report whether each UniProt Active/Binding site residue is resolved in 4HJO. Any that is unresolved is reported as such and excluded from distances.
2. **Functional-site set.**
   - The set is exactly the residues in UniProt Active site and Binding site features, with their feature types and ligand names as annotated.
   - I do not yet know whether any candidate lies inside these features. The program will report that directly, and "none" is an acceptable result.
   - Domain membership (the UniProt Domain feature) is reported as annotation context only. It is not a functional site and gets no distance calculation.
3. **Distances.** Minimum heavy-atom distance from each candidate residue to (a) erlotinib and any other uniquely named ligand and (b) each UniProt Active/Binding site residue. I will state this rule in the report.
4. **Contacts.** The baseline is residues within 5 Å of each candidate. I will call `contact_sensitivity` at 4, 5 and 6 Å only where an interpretation depends on a near-threshold contact, and I will state which sites triggered it.
5. **Burial.**
   - Protein-only Shrake-Rupley SASA (100 points, 1.4 Å probe).
   - RSA from Tien max ASA, with buried defined as RSA < 0.25.
   - Ligand-covered SASA.
6. **Structure quality.** Resolution, relative B-factor at each site, and missing density nearby.
7. **Physicochemical deltas.** Lookup-table changes in size, charge, polarity, and hydrophobicity for each substitution.
8. **Figure.** PyMOL image labeled by substitution, showing wild-type geometry. The legend will say that no mutant structure was modeled. I will inspect the figure against the numeric tables.
9. **Literature search.**
   - One focused query per substitution, for activity and for inhibitor sensitivity or resistance.
   - Where I want to name a structural element in the report, I will run an additional retrieval so a PMID supports the name.
   - For each record I will log the PMID and URL, whether support is abstract-only, and whether the abstract names the exact substitution.
   - A citation that exists does not verify a mechanism.

## 4. Handling the two axes
- **Activity axis.** Based on the computed observations (domain annotation, proximity to UniProt Active/Binding residues, burial, contacts, physicochemical change) plus retrieved evidence. Any mechanism involving a named structural element rests on the cited literature, not on my calculations.
- **Drug-response axis.** Based on erlotinib distance, ligand-covered SASA, and 5 Å contacts, and on retrieved inhibitor-response evidence. 4HJO contains erlotinib only, so any statement about other inhibitors or binding modes is literature-derived and labeled that way.
- **Table.** One row per candidate: observation, prediction, external evidence, confidence, and which axis each item bears on. Missing evidence is shown explicitly.

## 5. Checks
- SIFTS versus alignment agreement.
- The independent PyMOL ligand-distance check, compared with the Python distances.
- Cutoff sensitivity where triggered.
- Figure compared with the numbers.
- Each PubMed claim checked against the exact substitution in the retrieved abstract.
- Every UniProt-derived claim traced to a feature that actually covers the residue. For the exact substitution, I will check the variant annotation rather than inferring it from the position.

## 6. Limitations to state in the report
- **No mutant modeling.** No mutant structure, dynamics, affinity, ddG, or activity is computed. Every mechanism is an inference from the wild-type structure plus retrieved text.
- **Functional-site coverage.** UniProt's Active/Binding annotation may not include residues that matter for regulation or resistance. Measuring only against it can miss real effects, and a candidate being far from these sites does not show it is functionally neutral.
- **Conformational state.** 4HJO is a single inactive-state snapshot, so it cannot show shifts in conformational equilibrium.
- **Missing partners.** Chain A only omits dimer partners and crystal contacts.
- **Resolution.** At 2.75 Å, side-chain placement and loop positions are uncertain, and B-factors are a rough proxy.
- **Drug scope.** One erlotinib complex does not represent other inhibitors or covalent binding.
- **Evidence depth.** Abstract-only literature access limits mechanistic verification.
- **Cutoff dependence.** Contact and distance conclusions depend on the stated rules.
- **Method boundaries.** I will not claim docking, MD, free-energy, or any analysis outside the supported set.

## 7. Next step
On your approval I will run the baseline, review the figure and tables, call `contact_sensitivity` if triggered, run the PubMed queries, and write the report. I will not name structural elements without a supporting PMID.
