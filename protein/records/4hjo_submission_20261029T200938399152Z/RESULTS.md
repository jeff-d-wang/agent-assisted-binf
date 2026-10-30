# EGFR kinase domain (4HJO chain A): reviewed report on five substitutions

**Status:** Accepted by the user on 2026-10-29; no course grade assigned.
> Editorial update, 2026-10-29: the user reviewed and accepted the analysis. Codex corrected attribution, status wording and documented errors for the handoff. The original model responses remain in `api/`; this edited report is not a verbatim model response. See `DOCUMENTATION_UPDATE.md` and the task-level `HANDOFF.md`.

- **Computed values:** unchanged. All structural values come from the saved baseline outputs for the wild-type crystal structure. `contact_sensitivity` was not re-run because it takes no parameters and nothing about its inputs changed. The 4/5/6 Å values below are from the earlier run.
- **No mutant modeling:** no mutant structure, dynamics, activity, affinity or ddG was computed.
- **User-supplied items:** the V948R distances, the `02_measure.py` docstring reading, and the count of the discarded 9-query attempt come from you. I have not independently verified them.

---

## 0. Changes from the previous draft

| # | Change | Instruction |
|---|---|---|
| 1 | **L858R and L861Q:** sequence-local proximity to D855 (i−3 for L858, i−6 for L861) is no longer used as functional evidence. It stays in the tables as a computed value, flagged as sequence-local. Structural context now rests on the non-local contacts from `contacts_5A.csv`. | (1) |
| 2 | **G719S:** I now state that its V726 and T725 contacts lie in the same annotated 718–726 stretch as G719, so they are not independent functional evidence. | (1) |
| 3 | **22349823 retrieved** and used only where its abstract supports the claim: G719S, L858R and T790M. | (2) |
| 4 | **Drug-response axis restructured.** Four sensitivity statements are shown separately in a comparator table (UniProt vs wild type; 22349823; 42735369 vs classical sensitizing mutations; 37196448 vs ex19del/L858R). They are not merged into one ranking. | (3) |
| 5 | **Query count corrected** to include all attempts: 29 in total (see the Agent Audit). | (4) |
| 6 | **Weakness 7 corrected.** The 18227510 abstract calls T790 the "gatekeeper" residue, so that name is PMID-supported. The structural-element inventory is now complete (Section 4). | (4) |
| 7 | **Weakness 3 resolved.** The nearest-annotated-residue rule excludes the site itself and its i±1 neighbors by design (user-reported `02_measure.py` docstring). T790 therefore lists K745, not Q791. | (4) |
| 8 | **V948R** is reported as an engineered construct difference 22–31 Å from all five candidates (user-measured, independent parser). Functional relevance is stated only with PMIDs, and no retrieved abstract states one. | (5) |
| 9 | **C797S:** the covalent mechanism now has explicit abstract support from [29802850](https://pubmed.ncbi.nlm.nih.gov/29802850/). I retrieved it through the V948R query. | Follow-on from (5) |
| 10 | **T790M:** two primary biochemical abstracts (18227510 and 22349823) now agree on increased ATP affinity. I revised the confidence and conflict statements. | Follow-on from (2) |
| 11 | Erlotinib-specific evidence is no longer entirely absent: 22349823 states that G719S and L858R display sensitivity to gefitinib and erlotinib (no wild-type comparator stated). | Follow-on from (2) |
| 12 | I added a structural-element inventory table, and an unresolved-limitations list that is shorter and updated. | Housekeeping |

---

## 1. Protein description

**Source and function (UniProt P00533, [entry](https://www.uniprot.org/uniprotkb/P00533/entry), entry version 301):**
- **Protein and enzyme:** Epidermal growth factor receptor, a receptor tyrosine kinase (EC 2.7.10.1). The annotated reaction is L-tyrosyl-protein + ATP → O-phospho-L-tyrosyl-protein + ADP.
- **Activation:** Ligand binding triggers receptor homo- and/or heterodimerization and autophosphorylation, which recruits adapters such as GRB2.
- **Kinase domain:** UniProt "Protein kinase" domain, residues 712–979. All five candidates lie inside it.
- **Functional sites used (UniProt Active site and Binding site features only):**
  - D837, Active site, proton acceptor.
  - ATP binding sites at L718, G719, S720, G721, A722, F723, G724, T725, V726, K745, T790, Q791 and D855.

**Structure (4HJO):**
- Title: "Crystal structure of the inactive EGFR tyrosine kinase domain with erlotinib." X-ray, 2.75 Å, structure citation PMID 23101586.
- Chain A has one ligand, AQ4 (erlotinib).
- One engineered construct difference, V948R (author residue 924).
- Mean chain B-factor 47.2.

---

## 2. Methods

**Computation (deterministic, unchanged)**
- **Mapping.** SIFTS and a global alignment (BLOSUM62, gap open −10, extend −0.5), which had to agree.
- **Distances.** Minimum heavy-atom distance to the ligand and to UniProt Active/Binding residues.
- **"Nearest annotated residue" rule.** This excludes the site itself and its i±1 neighbors by design (per the `02_measure.py` docstring, as reported by the user). For example, T790 lists K745 and not the adjacent annotated Q791.
- **Contacts.** Residues within 5 Å. `contact_sensitivity` was run at 4, 5 and 6 Å.
- **Burial.** Shrake-Rupley SASA (100 points, 1.4 Å probe), protein-only RSA with Tien max ASA, buried if RSA < 0.25. Ligand-covered SASA.
- **Other.** Relative B-factor, physicochemical lookup deltas, and a PyMOL ligand-distance recheck.

**Use of contacts as functional evidence**
- A contact with a residue in the same local sequence stretch reflects chain connectivity, so I do not treat it as independent evidence of proximity to a functional element.
- Where I cite functional context, I use contacts with sequence-distant residues, taken from `contacts_5A.csv`. The file does not say which atoms (side chain or backbone) make each contact.

**Literature (PubMed, title and abstract only)**
- Structural-element names appear only with a PMID, as context, and are never presented as measurements (inventory in Section 4).
- UniProt variant statements are UniProt annotations. I did not fetch the PubMed abstracts they cite.

---

## 3. Coordinate observations

### Mapping (P1)
- Author numbering = UniProt − 24. SIFTS and alignment agree for all five, and wild-type residues match the notation.

| Substitution | Author residue |
|---|---|
| G719S | G695 |
| T790M | T766 |
| C797S | C773 |
| L858R | L834 |
| L861Q | L837 |

- All five are in the kinase domain, with every heavy atom observed. The figure labels use UniProt numbers, so D837 in the figure is author 813.

### Quantitative evidence
All values are wild-type geometry, identical to the previous draft.

| Substitution | UniProt Active/Binding site? | Min dist. to erlotinib (Å) | Ligand-covered SASA (Å²) | Nearest annotated residue, excl. self and i±1 (Å) | Dist. to D837 (Å) / Cα–Cα | RSA (buried <0.25) | 5 Å contacts (incl. ligand) | Rel. B | Δcharge / Δhydropathy / Δvolume (Å³) |
|---|---|---|---|---|---|---|---|---|---|
| G719S | Yes (ATP binding) | 5.06 | 0.0 | V726, 2.88 | 13.51 / 16.89 | 0.232 (buried) | 7 | 1.05 | 0 / −0.4 / +28.9 |
| T790M | Yes (ATP binding) | 3.48 | 19.3 | K745, 6.20 | 13.77 / 17.60 | 0.182 (buried) | 10 | 0.95 | 0 / +2.6 / +46.8 |
| C797S | No | 3.54 | 27.0 | L718, 7.93 | 10.87 / 14.77 | 0.238 (buried) | 12 | 0.90 | 0 / −3.3 / −19.5 |
| L858R | No | 5.26 | 3.6 | D855, 2.96 (sequence-local, i−3) | 6.37 / 8.22 | 0.096 (buried) | 12 | 0.90 | +1 / −8.3 / +6.7 |
| L861Q | No | 9.22 | 0.0 | D855, 7.44 (sequence-local, i−6) | 9.61 / 11.77 | 0.024 (buried) | 15 | 1.05 | 0 / −7.3 / −22.9 |

- **Relative B-factors** are all near 1, so these sites do not have unusually high B-factors relative to this chain; this does not measure molecular dynamics.
- **Rows where the annotated residue is sequence-local.**
  - For L858R and L861Q, D855 is the nearest annotated residue by the rule. It lies at i−3 and i−6 along the chain, so I do not use it as functional evidence.
  - For G719S, the nearest annotated residue V726 (i+7) and the contact T725 (i+6) both lie in the same annotated 718–726 stretch as G719 itself, as do G721 and G724 in its contact list. These contacts therefore show packing within one annotated stretch, not proximity to a separate functional element.

### Non-local contacts from `contacts_5A.csv` (used for L858R and L861Q)

| Candidate | Non-local contact | Min heavy-atom distance (Å) | UniProt-annotated? |
|---|---|---|---|
| L858R | K745 | 3.21 | Yes (ATP binding) |
| L858R | L788 | 3.64 | No |
| L858R | M766 | 4.57 | No |
| L861Q | E762 | 3.30 | No |
| L861Q | M766 | 3.81 | No |
| L861Q | I759 | 3.94 | No |

- L858 also has sequence-local contacts at 5 Å (D855, F856, K860, L861, L862, and the covalent neighbors G857 and A859). I do not count these as functional evidence.
- The files list further partners for both sites. The six above are the ones highlighted for interpretation.
- None of the non-local partners of L861 is a UniProt Active/Binding residue. L861 has no annotated non-local contact within 5 Å.

### Cutoff sensitivity (`contact_sensitivity`, from the earlier run)

| Substitution | Protein contacts 4 / 5 / 6 Å | Ligand within 4 / 5 / 6 Å |
|---|---|---|
| G719S | 5 / 7 / 8 | No / No / **Yes** |
| T790M | 7 / 9 / 15 | Yes / Yes / Yes |
| C797S | 10 / 11 / 13 | Yes / Yes / Yes |
| L858R | 9 / 12 / 13 | No / No / **Yes** |
| L861Q | 12 / 15 / 21 | No / No / No |

- **Robust:** erlotinib proximity of T790 and C797 holds at every cutoff, and L861 has no ligand within 6 Å.
- **Cutoff-dependent:** the ligand contact for G719 (5.06 Å) and L858 (5.26 Å) appears only at 6 Å. I call these borderline second-shell proximity, not direct contact.
- **Counts include neighbors.** The protein counts include sequence-adjacent residues at about 1.3 Å and exclude the ligand, so I do not rank sites by contact count.
- **Not tested:** RSA is near the 0.25 threshold for G719 (0.232) and C797 (0.238). The tool does not vary the RSA threshold, so "buried" for those two is threshold-sensitive.

### Engineered construct difference V948R
- 4HJO carries an engineered V948R substitution (author residue 924), recorded as a construct difference in the run provenance.
- **Distance to the candidates:** 22–31 Å from all five, as measured by you with an independent parser. I did not compute this and have not verified it.
- **Functional relevance (PMIDs only):** no retrieved abstract states a functional effect of V948R. The abstracts only show V948R as part of crystallized or modeled kinase constructs:
  - T790M/C797S/V948R in complex with EAI045 ([29802850](https://pubmed.ncbi.nlm.nih.gov/29802850/)).
  - T790M/V948R with BI-4020 ([38523074](https://pubmed.ncbi.nlm.nih.gov/38523074/)).
  - An L858R/T790M/V948R construct in a docking study ([42858544](https://pubmed.ncbi.nlm.nih.gov/42858544/)).
- **Conflicting description:** one docking-paper abstract ([31855568](https://pubmed.ncbi.nlm.nih.gov/31855568/)) lists V948R among mutations "found" in NSCLC. That conflicts with the construct-difference designation in this run, and I treat it as unreliable. It does not change the designation.
- I make no claim that V948R affects the candidates.

### Figure inspection
![Annotated structure](figures/structure_annotated.png)

- **What is shown:** the wild-type ribbon with erlotinib as yellow sticks. The candidates are colored spheres with side-chain sticks: T790M orange, C797S magenta, G719S red, L858R green, L861Q cyan. D837 is blue. No mutant was modeled.
- **Agreement with the tables:** T790M and C797S sit next to erlotinib, L861Q is farthest from it, and L858R sits near the D837 side of the cleft.
- **Projection caution:** the G719S sphere appears to overlay the quinazoline ring in this 2D view, but the measured distance is 5.06 Å.
- **Legibility:** the C797S and D837 labels overlap sticks or helices. The legend does not say what the spheres mark. They mark Cα atoms, as confirmed in `03_render.py`.

---

## 4. Structural-element inventory (literature context only)

None of these names is a computed measurement. Except for the gatekeeper, none is placed on a candidate residue.

| Element | PMID(s) | What the abstract says | Applied to a candidate? |
|---|---|---|---|
| Gatekeeper residue | [18227510](https://pubmed.ncbi.nlm.nih.gov/18227510/), [22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/) | "Threonine 790 is the 'gatekeeper' residue" (18227510); "gatekeeper residue, T790M" (22349823). | **Yes: T790**, explicitly in both abstracts. |
| P-loop | [22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/), [42735369](https://pubmed.ncbi.nlm.nih.gov/42735369/) | Phe723 repositioning within the P-loop in the L858R structure (22349823). "P-loop/αC-helix compressing" is a class of mutations including G719X (42735369). | No. F723 is not a candidate. The G719X class label is not a statement of where G719 sits. |
| αC-helix | [42735369](https://pubmed.ncbi.nlm.nih.gov/42735369/), [42583967](https://pubmed.ncbi.nlm.nih.gov/42583967/) | Class label (42735369). L858R, T790M and C797S collectively alter αC-helix orientation (42583967). | No |
| Activation loop | [42583967](https://pubmed.ncbi.nlm.nih.gov/42583967/) | Collective statement as above. | No |
| Hinge | [34319231](https://pubmed.ncbi.nlm.nih.gov/34319231/), [38523074](https://pubmed.ncbi.nlm.nih.gov/38523074/) | Hinge motion in MD simulations (34319231). Inhibitor interactions with the hinge region (38523074). | No |
| Hydrophobic spine, active-site cleft | [22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/) | T790M stabilizes the hydrophobic spine of the active conformation. In the L858R structure, the active-site cleft is expanded. | T790M and L858R only as the abstract states. |

---

## 5. Comparison table

I show mechanistic predictions as hypotheses only, since no mutant calculation was done.

| Mutation | Observation (computed on wild type) | Prediction (inference, not computed) | External evidence | Confidence |
|---|---|---|---|---|
| **G719S** | Annotated ATP-binding residue. Erlotinib at 5.06 Å, so borderline at 5 Å and in range only at 6 Å. Its contacts (V717, L718, S720, G721, G724, T725, V726) lie in or next to the same annotated 718–726 stretch as G719, so they show local packing, not a separate functional element. RSA 0.232, near the buried threshold. Gly→Ser adds 28.9 Å³ and is a Gly/Pro change. | **Activity:** the added side chain in the ATP-binding stretch may alter local packing or backbone freedom. **Drug response:** a direct effect on erlotinib binding is unlikely from distance alone. | **UniProt, exact G>S** ([entry](https://www.uniprot.org/uniprotkb/P00533/entry)): somatic, strongly increased kinase activity, constitutive activation, more sensitive to gefitinib than wild type. **[22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/) (abstract, exact G719S):** constitutively active and oncogenic, displays sensitivity to gefitinib and erlotinib (no wild-type comparator stated). With T790M added, the double mutant has enhanced activity, higher ATP affinity, and gefitinib resistance while retaining high gefitinib-binding affinity. The abstract does not state what the G719S structure itself showed. **Pooled or indirect:** [42735369](https://pubmed.ncbi.nlm.nih.gov/42735369/) (G719X in the P-loop/αC-helix compressing class, afatinib most consistent among second-generation TKIs), [41872782](https://pubmed.ncbi.nlm.nih.gov/41872782/) (G719X+S768I cohort, G719S 8.7% of G719X), [40277759](https://pubmed.ncbi.nlm.nih.gov/40277759/) (single case with acquired C797S), [39358400](https://pubmed.ncbi.nlm.nih.gov/39358400/) (G719X cell lines). | Activity effect: moderate to high (UniProt plus an independent abstract). Structural mechanism: low (untested). Sensitivity to first-generation TKIs: moderate (exact-substitution abstract, no comparator stated). Sensitivity relative to classical mutations: low (wildcard evidence only). |
| **T790M** | Annotated ATP-binding residue. Erlotinib at 3.48 Å (within 4 Å), 19.3 Å² covered by the ligand. Largest volume change (+46.8 Å³). Buried (RSA 0.182). Nearest annotated residue by the rule: K745 at 6.20 Å. | **Drug response:** wild-type geometry suggests a steric effect on erlotinib. The primary biochemical abstracts argue the main mechanism is increased ATP affinity, so geometry alone would mislead. **Activity:** an effect on the pocket that increases activity is plausible. | **UniProt, exact T>M:** increased kinase activity. **[18227510](https://pubmed.ncbi.nlm.nih.gov/18227510/)** (abstract): T790 is the gatekeeper residue. The mutant retains low-nanomolar gefitinib affinity, activates WT EGFR, and raises ATP affinity of L858R by more than 10-fold. Increased ATP affinity is reported as the primary resistance mechanism. **[22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/)** (abstract): T790M raises ATP affinity of the G719S mutant and confers gefitinib resistance on it. T790M stabilizes the hydrophobic spine of the active conformation. The Met790 side chain adopts different conformations in the apo, gefitinib-bound and AMPPNP-bound forms, explaining accommodation of these ligands. **[29802850](https://pubmed.ncbi.nlm.nih.gov/29802850/)** (abstract): patients on gefitinib and erlotinib develop resistance in about half of cases through T790M. **Conflicting statement:** [42514920](https://pubmed.ncbi.nlm.nih.gov/42514920/), a computational study, says T790M acts by "sterically hindering inhibitors and restoring ATP affinity" (background statement, not primary data). | Resistance and activity: moderate to high for the literature mechanism (two independent primary biochemical abstracts agree). Structural contribution of geometry alone: low. |
| **C797S** | Not a UniProt Active/Binding site, and no UniProt variant or mutagenesis annotation at this position. Erlotinib at 3.54 Å and within 4 Å. Largest ligand-covered SASA (27.0 Å²). RSA 0.238, near the buried threshold. Cys→Ser: −19.5 Å³, no charge change. | **Activity:** unknown; geometry alone and the retrieved records do not establish the effect of C797S alone. **Drug response:** loss of the thiol should abolish covalent attachment of inhibitors that bind through Cys797. Whether reversible binding changes cannot be judged from this structure. | **[29802850](https://pubmed.ncbi.nlm.nih.gov/29802850/)** (abstract): third-generation TKIs overcome T790M through covalent binding via Cys797 but lose efficacy when C797S "abolishes the covalent bonding"; reversible EAI001 and EAI045 do not rely on Cys797. [42906389](https://pubmed.ncbi.nlm.nih.gov/42906389/) (review abstract): covalent inhibitors capture Cys797. [42757013](https://pubmed.ncbi.nlm.nih.gov/42757013/): C797S in 23.3% of 86 T790M patients after osimertinib. [42835192](https://pubmed.ncbi.nlm.nih.gov/42835192/): fourth-generation inhibitors retained binding to C797S mutants. [42868668](https://pubmed.ncbi.nlm.nih.gov/42868668/): co-crystal (PDB 9XU9) shows a hydrogen bond to Ser797. **Reversible-inhibitor case reports (n=1 each):** [42466433](https://pubmed.ncbi.nlm.nih.gov/42466433/), [42691523](https://pubmed.ncbi.nlm.nih.gov/42691523/), [40277759](https://pubmed.ncbi.nlm.nih.gov/40277759/). | Resistance to covalent third-generation inhibitors via loss of covalent bonding: moderate to high (explicit abstract statement plus clinical data). Reversible-inhibitor response: low (case-level, confounded by co-treatment and compound mutations). Intrinsic activity effect: low (no evidence retrieved). |
| **L858R** | Not annotated as a functional site. Fully buried (RSA 0.096). Erlotinib at 5.26 Å, in range only at 6 Å. Non-local contacts: K745 (3.21 Å, annotated ATP-binding residue), L788 (3.64 Å) and M766 (4.57 Å). Distance to D837: 6.37 Å, the closest of the five. Leu→Arg adds charge (+1) and drops hydropathy by 8.3. F723 does not appear in the 5 Å contact list for L858. | **Activity:** a charged side chain replacing a buried leucine, in contact with a hydrophobic non-local neighborhood (L788, M766) and the annotated K745, may change local packing or electrostatics and could shift the active/inactive balance. Which atoms make the K745 contact is not given. A single inactive crystal cannot test the effect. **Drug response:** no direct erlotinib contact at the baseline cutoff. | **UniProt, exact L>R:** constitutively activated, strongly increased kinase activity, more sensitive to gefitinib than wild type. **[22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/)** (abstract): L858R is constitutively active and oncogenic and displays sensitivity to gefitinib and erlotinib. In the L858R structure, the active-site cleft is expanded by repositioning of Phe723 within the P-loop. F723A in wild-type EGFR enhanced gefitinib sensitivity in vivo, supporting the authors' hypothesis that cleft expansion enhances gefitinib sensitivity. That structure is of the active conformation, whereas 4HJO is inactive. [42656146](https://pubmed.ncbi.nlm.nih.gov/42656146/) (review): L858R drives ligand-independent asymmetric dimerization. [34319231](https://pubmed.ncbi.nlm.nih.gov/34319231/) (MD): L858R affects the active/inactive equilibrium. [42583967](https://pubmed.ncbi.nlm.nih.gov/42583967/): collective statement on activation loop and αC-helix. [38850084](https://pubmed.ncbi.nlm.nih.gov/38850084/) (computational, active state): L858R increases flexibility. | Activity: moderate to high for the effect; moderate for the mechanism. Drug response (sensitivity): moderate (UniProt plus an exact-substitution abstract with a structural rationale). Link between 4HJO geometry and the cleft-expansion mechanism: low. |
| **L861Q** | Not an annotated site. Most buried (RSA 0.024) and most contacts (15 at 5 Å; 21 at 6 Å). Non-local contacts: E762 (3.30 Å), M766 (3.81 Å) and I759 (3.94 Å). None is a UniProt Active/Binding residue, so L861 has no annotated non-local contact within 5 Å. No ligand within 6 Å (9.22 Å). Distance to D837: 9.61 Å. Leu→Gln: polar insertion, −22.9 Å³, hydropathy −7.3. | **Activity:** a smaller polar residue in a buried hydrophobic environment may disturb packing with the non-local neighbors (I759, M766, E762). The effect would be indirect, with no contact to erlotinib and no annotated functional partner. **Drug response:** no direct effect on erlotinib binding expected from distance. | **UniProt, exact L>Q:** constitutively activated kinase with higher basal autophosphorylation, more sensitive to gefitinib than wild type. **[37196448](https://pubmed.ncbi.nlm.nih.gov/37196448/)** (abstract): the therapeutic window of an exon 19 insertion mutant was most akin to L861Q-driven and A763_Y764insFQEA-driven cells, and less sensitive than the pattern seen with exon 19 deletion or L858R. **Pooled or indirect:** [42711860](https://pubmed.ncbi.nlm.nih.gov/42711860/), [42637134](https://pubmed.ncbi.nlm.nih.gov/42637134/), [36188595](https://pubmed.ncbi.nlm.nih.gov/36188595/) (computational prediction), [42719457](https://pubmed.ncbi.nlm.nih.gov/42719457/) (31 patients, exploratory docking), [42388639](https://pubmed.ncbi.nlm.nih.gov/42388639/) (single case, afatinib resistance). | Activity: moderate (UniProt exact annotation; structural mechanism is a hypothesis). Drug response: low, because the two comparator-specific statements differ and the rest is pooled, small, computational or anecdotal. |

---

## 6. Drug-response comparisons, kept separate

The comparators, drugs, substitutions and readouts differ, so I do not merge these into one ranking or call them contradictory.

| Source | Substitution (exact or wildcard) | Comparator | Drug(s) | Statement |
|---|---|---|---|---|
| UniProt annotation | G719S, L858R, L861Q (exact) | Wild type | Gefitinib | "More sensitive to gefitinib than wild type." Primary abstracts not retrieved. |
| [22349823](https://pubmed.ncbi.nlm.nih.gov/22349823/) (abstract) | G719S, L858R (exact) | None stated | Gefitinib, erlotinib | They "display sensitivity" to TKIs. For L858R, a cleft-expansion hypothesis is proposed for enhanced gefitinib sensitivity. |
| [42735369](https://pubmed.ncbi.nlm.nih.gov/42735369/) (review abstract) | G719X within PACC mutations (wildcard) | "Classical sensitizing mutations" | TKIs approved for classical mutations | PACC mutations "display reduced sensitivity." Among second-generation TKIs, afatinib gives the most consistent activity. The abstract does not enumerate which mutations count as classical. |
| [37196448](https://pubmed.ncbi.nlm.nih.gov/37196448/) (abstract) | L861Q (exact, as a comparison model) | Exon 19 deletion and L858R cells | Erlotinib, afatinib, osimertinib, mobocertinib | The window of an exon 19 insertion mutant resembles L861Q's and is less sensitive than the pattern seen with exon 19 deletion or L858R. The abstract reports no L861Q-versus-wild-type result and no G719S result. |

- A mutation can be more sensitive than wild type to one drug and less sensitive than classical mutants to the same or other drugs. These statements answer different questions and can all be true.
- The 4HJO structure with erlotinib cannot resolve any of these comparisons. It shows only that G719 and L858 are second-shell, and L861 is distant, relative to the bound ligand.

---

## 7. Uncertainty
- **Wild-type, inactive structure.** Mechanisms for L858R and L861Q point to shifts in the conformational balance, which one inactive crystal cannot test. The saved 22349823 abstract describes cleft expansion in L858R but does not establish the conformation of that structure.
- **Chain A only.** Dimer partners are absent, yet the L858R literature centers on dimerization.
- **Resolution.** At 2.75 Å, side-chain positions are uncertain.
- **Contact atoms.** `contacts_5A.csv` gives minimum heavy-atom distances without atom identities. I cannot say whether the L858–K745 contact involves side chains.
- **Functional-site scope.** Annotated sites are UniProt Active/Binding features only. Being far from them does not mean a candidate is functionally neutral. L858R and L861Q are not annotated sites, yet both have UniProt activity annotations.
- **Drug scope.** 4HJO has erlotinib only. Evidence for gefitinib, afatinib and others is literature-derived and labeled as such.
- **Evidence quality.** Much retrieved drug-response evidence is pooled, retrospective, single-case or computational.
- **Threshold dependence.** Ligand proximity for G719S and L858R, and burial for G719 and C797, depend on the stated cutoffs.
- **Evidence depth.** PubMed evidence is abstract-only.

---

## 8. Answer to the scientific question

**Activity.** From UniProt exact-substitution annotations, G719S, T790M, L858R and L861Q are reported to increase kinase activity. The 22349823 abstract independently reports G719S and L858R as constitutively active and oncogenic, and reports enhanced activity for T790M in the G719S background. C797S has no UniProt or retrieved activity evidence, so its intrinsic activity effect remains unknown.
- **L858R:** buried, with a non-local contact to the annotated K745 (3.21 Å) and hydrophobic neighbors L788 and M766. It is 6.37 Å from D837. The structure supports a hypothesis of indirect effects on local packing. The retrieved literature describes cleft expansion and dimerization or equilibrium effects; the saved abstract does not establish an active conformation for the L858R structure.
- **L861Q:** the most buried site, with non-local contacts E762, M766 and I759, none annotated. It has no functional partner within 5 Å, so any effect on activity would be through packing and is untested.
- **G719S:** this lies in the annotated ATP-binding stretch, and its contacts are within that same stretch. The proposed effect is local packing or flexibility, and it is hypothetical.
- **T790M:** two primary biochemical abstracts support increased ATP affinity and activation, and one reports stabilization of the hydrophobic spine.

**Drug response (see Section 6 for the separate comparisons).**
- **T790M:** the best-supported resistance effect. The structure shows close erlotinib contact, but the primary abstracts attribute resistance mainly to increased ATP affinity, with the Met790 side chain accommodating ligands. A general statement in 29802850 links T790M to resistance to gefitinib and erlotinib.
- **C797S:** explicit abstract support that C797S abolishes covalent bonding of third-generation inhibitors. Case reports suggest reversible inhibitors can still work in C797S-positive tumors, but they are single cases and confounded.
- **G719S, L858R:** reported to display sensitivity to gefitinib and erlotinib (22349823) and to be more sensitive than wild type to gefitinib (UniProt). The structure shows second-shell proximity to erlotinib only.
- **L861Q:** more sensitive than wild type to gefitinib (UniProt), yet in one abstract less sensitive than L858R and ex19del (37196448). These are different comparators and are not merged.
- **Separate axes:** T790M influences both axes. C797S influences mainly drug response. G719S, L858R and L861Q influence mainly activity, with TKI sensitivity as a downstream correlate.

This is a ranked, evidence-weighted hypothesis, not a measured result.

---

## 9. Unresolved limitations
1. No mutant effect was computed. Every mechanism is an inference from the wild-type structure plus abstract-level literature.
2. **Contact atom identities** are not available, so the type of the L858–K745 contact (backbone or side chain) is unknown.
3. **Cleft expansion** is reported in 22349823; the saved abstract does not specify that the L858R structure is in the active conformation. I did not measure L858 or F723 geometry beyond noting that F723 is absent from the 5 Å contact list.
4. **Erlotinib-specific evidence** is limited: 22349823 states sensitivity to erlotinib for G719S and L858R without a comparator. None was retrieved for T790M, C797S or L861Q at the exact-substitution level.
5. **UniProt-cited primary papers** for the variant statements were not fetched.
6. **Figure.** The spheres mark Cα atoms; the final caption must say so. Labels overlap, and the 2D projection can mislead. I cannot edit the figure with the available tools.
7. **Threshold-sensitive calls** (ligand proximity for G719S and L858R, burial for G719 and C797). The RSA threshold was not varied.
8. **Search coverage.** Retrieval is limited to five records per query, and wording sensitivity means I may have missed relevant papers.
9. **V948R.** The 22–31 Å distances are user-measured, and no retrieved abstract gives a functional effect. One docking-paper abstract describes V948R inconsistently with its construct-difference status.
10. **Structural-element names** remain literature context only.

---

## 10. Agent Audit

### Resources
- **Files and software:** 4HJO mmCIF/PDB (SHA-256 logged), UniProt P00533 JSON (entry version 301, sequence version 2), SIFTS, Biopython 1.85, numpy 1.25.2, Python 3.9.15, PyMOL 3.1.0.
- **Tools used:** `contact_sensitivity` (first round only) and `search_pubmed`.
- **PubMed query total across all attempts: 29.**

| Attempt | Queries | Notes |
|---|---|---|
| Discarded attempt (output-limit failure) | 9 | User-reported. These are not in my retained record, and I cannot verify them. |
| First retained round | 5 | Five queries after the interrupted attempt; the event log records each query. |
| Revision 1 | 12 | Six long queries returned nothing. Six shorter retries returned records. |
| This revision | 3 | The 22349823 title query, the 22349823 PMID query (same record), and "EGFR V948R". |
| **Total** | **29** | 20 retained plus 9 discarded. |

### Computed vs retrieved

| Item | Computed or retrieved |
|---|---|
| Mapping, distances, contacts, SASA/RSA, relative B, physicochemical deltas | Computed (wild type) |
| Cutoff sensitivity (4/5/6 Å) | Computed |
| UniProt domain, Active/Binding sites, variant text | Retrieved |
| PubMed claims | Retrieved, abstract-only |
| V948R distances (22–31 Å) | User-measured with an independent parser |
| `02_measure.py` rule | User-reported docstring reading |
| Mechanism text in the "Prediction" column | My inference; not computed |

### Independent checks
- **PyMOL recheck:** distance agreement for all 5. This is a code check on the same coordinates, not an independent data source.
- **Contact-sensitivity re-run (first round):** matched the saved table. This is a repeatability check.
- **Mapping:** SIFTS and alignment agree for all five.
- **Wild-type residue identity** matches the notation for all five.
- **Contact-list cross-check:** I checked every contact value I cite for L858R and L861Q (and for G719S) against `contacts_5A.csv`, and the values match.
- **V948R distances:** an independent parser by the user. I have not reproduced it.

### Weaknesses, including corrections
1. **Weakness 3 (resolved).** I had inferred that the "nearest annotated residue" column skipped ±1 neighbors and listed this as a possible inconsistency. The `02_measure.py` docstring, as reported by the user, says the exclusion is by design, so T790 lists K745 and not Q791. I have removed it as an open problem and moved the rule into Methods. I have not read the file myself.
2. **Weakness 7 (corrected).** In earlier drafts my inventory of PMID-supported structural-element names omitted the gatekeeper, even though my T790M rows used it. The 18227510 abstract calls T790 the gatekeeper residue, and 22349823 repeats it. The inventory in Section 4 now includes it.
3. **Sequence-local functional evidence (corrected).** Earlier drafts used D855 (i−3 for L858, i−6 for L861) as functional context for L858R and L861Q. A contact within the same local stretch largely reflects chain connectivity. I replaced it with the non-local contacts you named. I also flagged that G719S's V726 and T725 contacts lie in the same annotated stretch as G719.
4. **Query design.** My earlier evidence searches were poorly worded: six long queries returned nothing, and I needed a retry. Key sources (22349823, 29802850) came from your instruction or an incidental hit on the V948R query, not from my first-pass searches. I may still be missing relevant papers.
5. **Evidence quality.** Several sources are case reports, a small retrospective cohort, or computational studies. Pooled G719X data stand in for G719S where no exact data exist. Abstract-level reading limits how far I can verify mechanisms.
6. **Contested mechanism.** Wild-type geometry would have led me to a steric explanation for T790M. Two primary abstracts argue otherwise.
7. **Figure limits** as described above.
8. **Retained-record gap.** I cannot account for the 9 discarded queries beyond your count, so the total of 29 depends on your figure.

The user accepted the analysis after review. The combined report, evidence packaging and grading remain separate steps.
