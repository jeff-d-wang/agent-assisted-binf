"""Step 2 (P2): structural measurements for each candidate mutation.

Measurement rules (all computed here from coordinates):
  - distance = minimum heavy-atom distance (H and waters excluded), in Angstrom
  - contacts = residues with any heavy atom within 5.0 A of any heavy atom of the site residue
    (includes the i+-1 backbone neighbours); nearest functional residue excludes i+-1
  - RSA = Shrake-Rupley residue SASA (protein only, ligand removed) / Tien et al. 2013 theoretical max ASA;
    "buried" if RSA < 0.25 (a convention, not a sharp boundary)
  - ligand-contact SASA = residue SASA without ligand minus with ligand (> 0 means the ligand covers it)
  - relative B = mean residue B-factor / chain mean B-factor (>1.5 flagged as mobile)
Physico-chemical deltas come from fixed lookup tables (Kyte-Doolittle 1982, Zamyatnin 1972, BLOSUM62).

Run from repo root after 01_map.py:
  python protein/02_measure.py --pdb datasets/4hjo.pdb
No randomness in this script.
"""
import argparse
import copy
import csv
import json
from pathlib import Path

import numpy as np
from Bio.Align import substitution_matrices
from Bio.PDB import NeighborSearch, PDBParser
from Bio.PDB.SASA import ShrakeRupley

OUT = Path(__file__).parent
CUTOFF = 5.0
BURIED_RSA = 0.25
WATER = {"HOH", "WAT", "DOD"}
ADDITIVES = {"GOL", "EDO", "SO4", "PO4", "PEG", "PG4", "ACT", "DMS", "CL", "NA", "MPD", "FMT", "TRS", "EPE"}

MAX_ASA = dict(A=129, R=274, N=195, D=193, C=167, E=223, Q=225, G=104, H=224, I=197, L=201, K=236,
               M=224, F=240, P=159, S=155, T=172, W=285, Y=263, V=174)  # Tien et al. 2013, theoretical
KD = dict(A=1.8, R=-4.5, N=-3.5, D=-3.5, C=2.5, Q=-3.5, E=-3.5, G=-0.4, H=-3.2, I=4.5, L=3.8, K=-3.9,
          M=1.9, F=2.8, P=-1.6, S=-0.8, T=-0.7, W=-0.9, Y=-1.3, V=4.2)  # Kyte & Doolittle 1982
VOL = dict(A=88.6, R=173.4, N=114.1, D=111.1, C=108.5, Q=143.8, E=138.4, G=60.1, H=153.2, I=166.7,
           L=166.7, K=168.6, M=162.9, F=189.9, P=112.7, S=89.0, T=116.1, W=227.8, Y=193.6, V=140.0)  # A^3
CHARGE = dict(D=-1, E=-1, K=1, R=1)  # pH 7; His treated as neutral
HEAVY = dict(G=4, A=5, S=6, C=6, P=7, T=7, V=7, D=8, N=8, I=8, L=8, M=8, E=9, Q=9, K=9, H=10, F=11,
             R=11, Y=12, W=14)  # expected heavy atoms per residue (no OXT)
B62 = substitution_matrices.load("BLOSUM62")

ap = argparse.ArgumentParser()
ap.add_argument("--pdb", default="datasets/4hjo.pdb")
ap.add_argument("--chain", default="A")
ap.add_argument("--out", type=Path, default=Path(__file__).parent)
args = ap.parse_args()
OUT = args.out

mapping = list(csv.DictReader(open(OUT / "tables" / "mapping.csv")))
funcs = list(csv.DictReader(open(OUT / "tables" / "functional_sites.csv")))
offset = {int(r["author_resnum"]) - int(r["uniprot_pos"]) for r in mapping + funcs if r["author_resnum"]}
assert len(offset) == 1, f"non-constant numbering offset {offset}; per-residue mapping needed"
offset = offset.pop()

chain = PDBParser(QUIET=True).get_structure("s", args.pdb)[0][args.chain]
protein = [r for r in chain if r.id[0] == " "]
ligands = [r for r in chain if r.id[0].startswith("H_") and r.get_resname() not in WATER | ADDITIVES]
heavy = lambda res: [a for a in res if a.element != "H"]
by_auth = {r.id[1]: r for r in protein}
all_heavy = [a for r in protein + ligands for a in heavy(r)]
ns = NeighborSearch(all_heavy)


def min_dist(r1, r2):
    a = np.array([x.coord for x in heavy(r1)])
    b = np.array([x.coord for x in heavy(r2)])
    return float(np.sqrt(((a[:, None] - b[None]) ** 2).sum(-1)).min())


def sasa(entity_residues):
    """Per-residue SASA on a copy of the chain holding only the given residues."""
    ch = copy.deepcopy(chain)
    keep = {r.id for r in entity_residues}
    for r in list(ch):
        if r.id not in keep:
            ch.detach_child(r.id)
    ShrakeRupley().compute(ch, level="R")
    return {r.id[1]: r.sasa for r in ch if r.id[0] == " "}


sasa_apo = sasa(protein)
sasa_holo = sasa(protein + ligands)
chain_b = np.mean([a.bfactor for r in protein for a in heavy(r)])
active = [f for f in funcs if f["feature"] == "Active site" and f["observed_in_structure"] == "True"]

rows, contact_rows = [], []
for m in mapping:
    wt, mt, upos = m["wt_uniprot"], m["mutant"], int(m["uniprot_pos"])
    row = dict(mutation=m["mutation"], author_resnum=m["author_resnum"])
    res = by_auth.get(int(m["author_resnum"])) if m["author_resnum"] else None
    if res is None:
        row["note"] = "not observed in structure; no coordinate-based measurement"
        rows.append(row)
        continue

    near = set()
    for atom in heavy(res):
        for b in ns.search(atom.coord, CUTOFF):
            if b.get_parent() is not res:
                near.add(b.get_parent())
    for r in sorted(near, key=lambda r: (r.id[0] != " ", r.id[1])):
        is_lig = r in ligands
        contact_rows.append(dict(mutation=m["mutation"], partner=r.get_resname(),
                                 partner_author=r.id[1], partner_uniprot="" if is_lig else r.id[1] - offset,
                                 min_heavy_dist=round(min_dist(res, r), 2)))

    lig_d = {l.get_resname(): min_dist(res, l) for l in ligands}
    func_d = []
    for f in funcs:
        fr = by_auth.get(int(f["author_resnum"])) if f["author_resnum"] else None
        # skip i-1..i+1: covalent backbone neighbours are trivially ~1.3 A away
        if fr is not None and abs(int(f["uniprot_pos"]) - upos) > 1:
            func_d.append((min_dist(res, fr), f"{f['wt']}{f['uniprot_pos']}"))
    act = [(min_dist(res, by_auth[int(f["author_resnum"])]), f"{f['wt']}{f['uniprot_pos']}") for f in active]
    rsa = sasa_apo[res.id[1]] / MAX_ASA[wt]
    ca_act = [float(np.linalg.norm(res["CA"].coord - by_auth[int(f["author_resnum"])]["CA"].coord)) for f in active]

    row.update(
        is_annotated_functional_site=any(int(f["uniprot_pos"]) == upos for f in funcs),
        min_dist_ligand=";".join(f"{k}:{v:.2f}" for k, v in lig_d.items()) or "no ligand",
        nearest_functional_residue="{1}:{0:.2f}".format(*min(func_d)) if func_d else "",
        min_dist_active_site=";".join(f"{n}:{d:.2f}" for d, n in act),
        ca_ca_active_site=";".join(f"{d:.2f}" for d in ca_act),
        n_contacts_5A=len(near),
        ligand_in_5A=any(r in ligands for r in near),
        rsa=round(rsa, 3), buried=rsa < BURIED_RSA,
        ligand_contact_sasa=round(sasa_apo[res.id[1]] - sasa_holo[res.id[1]], 1),
        rel_bfactor=round(np.mean([a.bfactor for a in heavy(res)]) / chain_b, 2),
        heavy_atoms_observed=f"{len(heavy(res))}/{HEAVY[wt]}",
        d_charge=CHARGE.get(mt, 0) - CHARGE.get(wt, 0),
        d_hydropathy=round(KD[mt] - KD[wt], 1),
        d_volume=round(VOL[mt] - VOL[wt], 1),
        blosum62=int(B62[wt][mt]),
        gly_pro_change=wt in "GP" or mt in "GP",
    )
    rows.append(row)

fields = list(dict.fromkeys(k for r in rows for k in r))
with open(OUT / "tables" / "measurements.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
with open(OUT / "tables" / "contacts_5A.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["mutation", "partner", "partner_author", "partner_uniprot", "min_heavy_dist"])
    w.writeheader()
    w.writerows(contact_rows)

meta = json.loads((OUT / "data" / "provenance.json").read_text())
meta["measure"] = dict(pdb_file=args.pdb, ligands=[l.get_resname() for l in ligands], cutoff_A=CUTOFF,
                       buried_rsa=BURIED_RSA, chain_mean_b=round(float(chain_b), 1), author_minus_uniprot=offset)
(OUT / "data" / "provenance.json").write_text(json.dumps(meta, indent=2))
for r in rows:
    print(r)
