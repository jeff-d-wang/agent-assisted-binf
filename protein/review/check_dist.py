# Independent recheck: raw PDB text parsing + numpy, no Biopython.
import sys, json, numpy as np
from collections import defaultdict
pdb, uni = sys.argv[1], sys.argv[2]
res = defaultdict(list); names = {}; altlocs = set(); het = set()
for line in open(pdb):
    if line.startswith("ENDMDL"): break
    if line[:6] in ("ATOM  ", "HETATM") and line[21] == "A":
        el = line[76:78].strip() or line[12:16].strip()[0]
        if el == "H": continue
        rn = line[17:20]; num = int(line[22:26])
        if line[16] not in " A":  # keep first altloc only
            altlocs.add((rn, num)); continue
        if line[16] == "A": altlocs.add((rn, num))
        if line[:6] == "HETATM": het.add(rn)
        if rn == "HOH": continue
        res[(rn, num)].append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
        names[num if line[:6] == "ATOM  " else rn] = rn
xyz = {k: np.array(v) for k, v in res.items()}
bynum = {k[1]: k for k in xyz if k[0] != "AQ4"}
lig = [k for k in xyz if k[0] == "AQ4"]
useq = json.load(open(uni))["sequence"]["value"]
three = dict(GLY="G", THR="T", CYS="C", LEU="L", ASP="D", LYS="K", VAL="V", ARG="R", GLU="E", MET="M")
def d(a, b): return np.sqrt(((xyz[a][:, None] - xyz[b][None]) ** 2).sum(-1)).min()
print("HETATM names chain A:", sorted(het), "| AQ4 copies:", len(lig), "| altloc residues:", sorted(altlocs))
for up in (719, 790, 797, 858, 861, 948, 837, 745, 855, 762, 766):
    k = bynum[up - 24]
    print(f"UniProt {up}: UniProt aa {useq[up-1]} | structure author {up-24} {k[0]}")
OFF = -24
cand = [719, 790, 797, 858, 861]
print("\nmin heavy-atom distance (A)")
for up in cand:
    k = bynum[up + OFF]
    row = {"AQ4": d(k, lig[0])}
    for t in (837, 745, 855, 762, 766, 948):
        row[t] = d(k, bynum[t + OFF])
    print(up, " ".join(f"{t}:{v:.2f}" for t, v in row.items()))
