# Independent burial check with PyMOL's SASA engine (not Biopython Shrake-Rupley).
import sys
from pymol import cmd
cmd.load(sys.argv[1], "p")
cmd.remove("not (chain A and polymer.protein)")  # protein only, as in 02_measure.py
cmd.remove("hydro")
cmd.set("dot_solvent", 1); cmd.set("solvent_radius", 1.4)
MAX = dict(GLY=104, THR=172, CYS=167, LEU=201)  # Tien 2013 theoretical
for density in (2, 3, 4):
    cmd.set("dot_density", density)
    out = []
    for up, rn in ((719, "GLY"), (790, "THR"), (797, "CYS"), (858, "LEU"), (861, "LEU")):
        a = cmd.get_area(f"chain A and resi {up-24}")
        out.append(f"{up}:{a/MAX[rn]:.3f}")
    print("dot_density", density, " ".join(out))
