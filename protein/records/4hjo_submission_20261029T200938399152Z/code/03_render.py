"""Step 3 (P4 figure + independent check of P2). Runs inside PyMOL, not plain python:

  pymol -cq protein/03_render.py -- datasets/4hjo.pdb

Figure: binding-cleft view of all candidates, ligand and catalytic residue, labelled in UniProt numbering.
Colours: ligand C = yellow, catalytic D = blue, UniProt ATP-binding residues = light blue cartoon,
mutations = red/orange/magenta/forest/cyan in mapping.csv order. Session saved for interactive viewing.
Independent check: for each mutation->ligand distance from 02_measure.py (Biopython), use PyMOL's own
parser and selection engine to confirm (a) no heavy atom pair is closer than the reported value - 0.01 A
and (b) at least one pair lies within the reported value + 0.01 A. Written to tables/pymol_check.csv.
No randomness in this script.
"""
import csv
import json
import sys
from pathlib import Path

from pymol import cmd

OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("protein")
pdb = sys.argv[1] if len(sys.argv) > 1 else "datasets/4hjo.pdb"
chain = sys.argv[3] if len(sys.argv) > 3 else "A"
(OUT / "figures").mkdir(exist_ok=True)

mapping = list(csv.DictReader(open(OUT / "tables" / "mapping.csv")))
meas = {r["mutation"]: r for r in csv.DictReader(open(OUT / "tables" / "measurements.csv"))}
funcs = list(csv.DictReader(open(OUT / "tables" / "functional_sites.csv")))
ligs = sorted({kv.split(":")[0] for r in meas.values() for kv in r.get("min_dist_ligand", "").split(";") if ":" in kv})

cmd.load(pdb, "prot", format="pdb")
cmd.remove(f"not chain {chain}")
cmd.remove("solvent or hydro")
lig_sel = " or ".join(f"resn {l}" for l in ligs) or "none"
muts = {m["mutation"]: f"prot and polymer and resi {m['author_resnum']}" for m in mapping
        if m["observed_in_structure"] == "True"}

# --- independent distance check ---
rows = []
for name, sel in muts.items():
    for kv in meas[name]["min_dist_ligand"].split(";"):
        if ":" not in kv:
            continue
        lig, d = kv.split(":")
        d = float(d)
        closer = cmd.count_atoms(f"({sel}) within {d - 0.01:.2f} of (resn {lig})")
        at = cmd.count_atoms(f"({sel}) within {d + 0.01:.2f} of (resn {lig})")
        rows.append(dict(mutation=name, ligand=lig, biopython_min_dist=d, pymol_atoms_closer=closer,
                         pymol_atoms_within_d_plus_0p01=at, agrees=closer == 0 and at > 0))
with open(OUT / "tables" / "pymol_check.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["mutation", "ligand", "biopython_min_dist", "pymol_atoms_closer",
                                     "pymol_atoms_within_d_plus_0p01", "agrees"])
    w.writeheader()
    w.writerows(rows)
print(*rows, sep="\n")
if any(not r["agrees"] for r in rows):
    raise RuntimeError("PyMOL distance verification failed")

# --- figure ---
cmd.bg_color("white")
cmd.set("ray_opaque_background", 1)
cmd.hide("everything")
cmd.show("cartoon", "prot and polymer")
cmd.color("grey80", "prot and polymer")
cmd.set("cartoon_transparency", 0.15)

active = [f for f in funcs if f["feature"] == "Active site" and f["author_resnum"]]
binding = [f for f in funcs if f["feature"] == "Binding site" and f["author_resnum"]]
cmd.select("binding", "prot and polymer and resi " + "+".join(f["author_resnum"] for f in binding) if binding else "none")
cmd.color("lightblue", "binding")
cmd.select("active", "prot and polymer and resi " + "+".join(f["author_resnum"] for f in active) if active else "none")
cmd.show("sticks", "active and not name N+C+O")
cmd.color("blue", "active and elem C")

cmd.show("sticks", lig_sel)
cmd.color("yellow", f"({lig_sel}) and elem C")

palette = ["red", "orange", "magenta", "forest", "cyan", "brown", "salmon", "teal"]
for (name, sel), col in zip(muts.items(), palette):
    cmd.show("sticks", f"({sel}) and not name N+C+O")
    cmd.show("spheres", f"({sel}) and name CA")
    cmd.set("sphere_scale", 0.6, f"({sel}) and name CA")
    cmd.color(col, f"({sel}) and (elem C or name CA)")
    cmd.label(f"({sel}) and name CA", f'"{name}"')
for f in active:
    cmd.label(f"active and resi {f['author_resnum']} and name CA", f'"{f["wt"]}{f["uniprot_pos"]} (catalytic)"')
cmd.util.cnc("all")  # heteroatom colouring, keeps carbon colours

cmd.set("label_size", 22)
cmd.set("label_color", "black")
cmd.set("label_outline_color", "white")


def place_labels(min_dx, min_dy):
    """Offsets are in camera space (A); z pulls labels in front of the cartoon, x/y avoid collisions.
    min_dx/min_dy = label footprint in A at the current zoom (labels are sized in pixels)."""
    rot = cmd.get_view()[:9]
    placed = []
    for model in cmd.get_model("prot and name CA and (" + " or ".join(f"({s})" for s in muts.values()) + " or active)").atom:
        x, y, z = model.coord
        sx = x * rot[0] + y * rot[3] + z * rot[6]  # PyMOL view matrix is column-major
        sy = x * rot[1] + y * rot[4] + z * rot[7]
        for dx, dy in [(0, 1), (0, -1), (0.8, 0), (-0.8, 0), (0, 2), (0, -2)]:
            dx, dy = dx * min_dx, dy * min_dy
            px, py = sx + dx, sy + dy
            if all(abs(px - qx) > min_dx or abs(py - qy) > min_dy for qx, qy in placed):
                break
        placed.append((px, py))
        cmd.set("label_position", (dx, dy, 50), f"prot and resi {model.resi} and name CA")


focus = " or ".join(f"({s})" for s in muts.values()) + f" or ({lig_sel}) or active"
# ponytail: one close-up view only; a whole-domain view put labels on the wrong spheres at that zoom
cmd.set("orthoscopic", 1)  # so the z offset doesn't shift labels sideways
cmd.orient(focus)
cmd.zoom(focus, 2)
cmd.clip("slab", 200)
place_labels(8, 2.5)
cmd.png(str(OUT / "figures" / "structure_annotated.png"), width=1800, height=1350, dpi=300, ray=1)
cmd.save(str(OUT / "figures" / "structure_annotated.pse"))
provenance = json.loads((OUT / "data/provenance.json").read_text())
provenance["pymol_version"] = cmd.get_version()[0]
(OUT / "data/provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
