"""Step 1 (P1): verify mutations against UniProt and map them onto the structure.

Two independent mappings UniProt -> structure residue numbers:
  A) PDBe SIFTS segment mapping (retrieved) + mmCIF pdbx_poly_seq_scheme
  B) global alignment of the deposited SEQRES to the UniProt sequence (computed)
The script stops if they disagree or if a wild-type residue does not match.

Run from repo root:
  python protein/01_map.py --cif datasets/4hjo.cif.gz --uniprot P00533 \
      --mutations G719S,T790M,C797S,L858R,L861Q
No randomness in this script.
"""
import argparse
import csv
import datetime
import gzip
import hashlib
import json
import re
import urllib.request
from pathlib import Path

from Bio.Align import PairwiseAligner, substitution_matrices
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

def fetch(url, dest):
    """Download once; later runs reuse the saved copy so results don't drift with database updates."""
    if not dest.exists():
        dest.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    return json.loads(dest.read_text())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


ap = argparse.ArgumentParser()
ap.add_argument("--cif", default="datasets/4hjo.cif.gz")
ap.add_argument("--uniprot", default="P00533")
ap.add_argument("--chain", default="A")
ap.add_argument("--mutations", default="G719S,T790M,C797S,L858R,L861Q")
ap.add_argument("--out", type=Path, default=Path(__file__).parent)
args = ap.parse_args()
OUT = args.out
(OUT / "data").mkdir(parents=True, exist_ok=True)
(OUT / "tables").mkdir(exist_ok=True)

opener = gzip.open if args.cif.endswith(".gz") else open
with opener(args.cif, "rt") as fh:
    cif = MMCIF2Dict(fh)
pdb_id = cif["_entry.id"][0].lower()
uni_url = f"https://rest.uniprot.org/uniprotkb/{args.uniprot}.json"
sifts_url = f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb_id}"
uni = fetch(uni_url, OUT / "data" / f"{args.uniprot}.json")
sifts = fetch(sifts_url, OUT / "data" / f"{pdb_id}_sifts.json")
useq = uni["sequence"]["value"]

# Polymer residue table for the chain: label seq_id -> (author number, residue name, observed?)
scheme = {}
for sid, num, mon, obs, strand in zip(
    cif["_pdbx_poly_seq_scheme.seq_id"], cif["_pdbx_poly_seq_scheme.pdb_seq_num"],
    cif["_pdbx_poly_seq_scheme.mon_id"], cif["_pdbx_poly_seq_scheme.pdb_mon_id"],
    cif["_pdbx_poly_seq_scheme.pdb_strand_id"]):
    if strand == args.chain:
        scheme[int(sid)] = (int(num), mon, obs != "?")

# Construct differences declared by the depositors (expression tags, engineered mutations)
seq_dif = [
    f"{d} {db}{dbnum}->{mon} (author {auth})"
    for mon, db, dbnum, auth, d, strand in zip(
        cif["_struct_ref_seq_dif.mon_id"], cif["_struct_ref_seq_dif.db_mon_id"],
        cif["_struct_ref_seq_dif.pdbx_seq_db_seq_num"], cif["_struct_ref_seq_dif.pdbx_auth_seq_num"],
        cif["_struct_ref_seq_dif.details"], cif["_struct_ref_seq_dif.pdbx_pdb_strand_id"])
    if strand == args.chain and d.upper() != "EXPRESSION TAG"
]

# Mapping A: SIFTS segments (label seq_id ranges <-> UniProt ranges)
map_a = {}
for seg in sifts[pdb_id]["UniProt"][args.uniprot]["mappings"]:
    if seg["chain_id"] != args.chain:
        continue
    s, u0, u1 = seg["start"]["residue_number"], seg["unp_start"], seg["unp_end"]
    for k in range(u1 - u0 + 1):
        map_a[u0 + k] = s + k

# Mapping B: align SEQRES (one-letter canonical) to UniProt
entity_index = next(i for i, chains in enumerate(cif["_entity_poly.pdbx_strand_id"])
                    if args.chain in chains.split(","))
seqres = re.sub(r"\s", "", cif["_entity_poly.pdbx_seq_one_letter_code_can"][entity_index])
aligner = PairwiseAligner(mode="global", open_gap_score=-10, extend_gap_score=-0.5,
                          target_end_gap_score=0, query_end_gap_score=0)
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aln = aligner.align(useq, seqres)[0]
map_b = {}
for (u0, u1), (s0, s1) in zip(*aln.aligned):
    for k in range(u1 - u0):
        map_b[u0 + k + 1] = s0 + k + 1  # both 1-based

# Functional residues annotated in UniProt (retrieved), for later distance measurements
func = []
for f in uni["features"]:
    if f["type"] in ("Active site", "Binding site"):
        for pos in range(f["location"]["start"]["value"], f["location"]["end"]["value"] + 1):
            lig = f.get("ligand", {}).get("name", "")
            func.append((pos, f["type"], f.get("description") or lig))
domains = [(f["description"], f["location"]["start"]["value"], f["location"]["end"]["value"])
           for f in uni["features"] if f["type"] == "Domain"]

THREE = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
         "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
         "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}


def map_pos(upos):
    a, b = map_a.get(upos), map_b.get(upos)
    if a != b:
        raise SystemExit(f"Mapping disagreement at UniProt {upos}: SIFTS label {a} vs alignment label {b}")
    if a is None:
        return None, None, False, ""
    auth, mon, observed = scheme[a]
    return a, auth, observed, THREE.get(mon, "X")


rows = []
for m in args.mutations.split(","):
    match = re.fullmatch(r"([ACDEFGHIKLMNPQRSTVWY])([1-9]\d*)([ACDEFGHIKLMNPQRSTVWY])", m.strip())
    if not match:
        raise SystemExit(f"Invalid missense mutation: {m}")
    wt, pos, mt = match.groups()
    pos = int(pos)
    if pos > len(useq) or wt == mt:
        raise SystemExit(f"Invalid position or unchanged residue: {m}")
    if useq[pos - 1] != wt:
        raise SystemExit(f"{m}: UniProt {args.uniprot} has {useq[pos - 1]} at {pos}, not {wt}")
    label, auth, observed, struct_aa = map_pos(pos)
    if struct_aa and struct_aa != wt:
        raise SystemExit(f"{m}: structure has {struct_aa} at author {auth}, not {wt}")
    dom = ";".join(d for d, s, e in domains if s <= pos <= e) or "none"
    rows.append(dict(mutation=m, uniprot_pos=pos, wt_uniprot=wt, mutant=mt, wt_structure=struct_aa or "",
                     label_seq_id=label or "", author_resnum=auth or "", observed_in_structure=observed,
                     offset_author_minus_uniprot=(auth - pos) if auth else "", uniprot_domain=dom,
                     sifts_alignment_agree=True))

with open(OUT / "tables" / "mapping.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

with open(OUT / "tables" / "functional_sites.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["uniprot_pos", "wt", "feature", "description", "author_resnum", "observed_in_structure"])
    for pos, ftype, desc in func:
        _, auth, observed, _ = map_pos(pos)
        w.writerow([pos, useq[pos - 1], ftype, desc, auth or "", observed])

# Retrieved evidence: UniProt variant / mutagenesis annotations at candidate positions (empty = none curated)
with open(OUT / "tables" / "uniprot_variants.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["mutation", "feature", "uniprot_change", "description", "pubmed_ids"])
    for r in rows:
        hits = [f for f in uni["features"] if f["type"] in ("Natural variant", "Mutagenesis")
                and f["location"]["start"]["value"] == r["uniprot_pos"]]
        for f in hits:
            alt = f.get("alternativeSequence", {})
            w.writerow([r["mutation"], f["type"],
                        f"{alt.get('originalSequence', '')}>{'/'.join(alt.get('alternativeSequences', []))}",
                        f.get("description", ""),
                        " ".join(sorted({e["id"] for e in f.get("evidences", []) if e.get("source") == "PubMed"}))])
        if not hits:
            w.writerow([r["mutation"], "none", "", "no UniProt variant/mutagenesis annotation at this position", ""])

(OUT / "data" / "provenance.json").write_text(json.dumps({
    "run_date": datetime.date.today().isoformat(),
    "structure_file": args.cif, "structure_sha256": sha256(args.cif), "chain": args.chain,
    "uniprot_url": uni_url, "uniprot_entry_version": uni["entryAudit"]["entryVersion"],
    "uniprot_sequence_version": uni["entryAudit"]["sequenceVersion"],
    "uniprot_sha256": sha256(OUT / "data" / f"{args.uniprot}.json"),
    "sifts_url": sifts_url, "sifts_sha256": sha256(OUT / "data" / f"{pdb_id}_sifts.json"),
    "construct_differences": seq_dif, "domains": domains,
    "alignment": "global PairwiseAligner, BLOSUM62, gap open -10 / extend -0.5, free end gaps",
}, indent=2))

for r in rows:
    print(r)
print("Construct differences:", seq_dif)
