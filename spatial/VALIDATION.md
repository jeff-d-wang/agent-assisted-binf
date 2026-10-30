# Task 3 software validation — 2026-10-29

Codex implemented the local numerical workflow and tested software behavior, not the
biological conclusions. No scientific-agent model was called and no mouse-brain analysis
was run. The actual input files were checked for existence and hashed only.

Environment: Python 3.9.15 from `/Users/jeffwang/miniforge3/bin/python`; Scanpy 1.9.8,
AnnData 0.10.5.post1, NumPy 1.25.2, pandas 1.4.2, SciPy 1.13.1, Matplotlib 3.9.4,
scikit-learn 1.1.1, igraph 1.0.0, leidenalg 0.12.0, UMAP 0.5.5, PyNNDescent 0.5.11,
Numba 0.59.0 and h5py 3.11.0. Exact direct dependencies are in `requirements.txt`;
each real run saves a complete environment freeze. Correction (2026-10-29): the h5py
version above came from package metadata; the interpreter imports h5py 3.6.0 because two
h5py dist-info directories are installed. The pin is now 3.6.0 (see requirements.lock.txt).

Commands:

```bash
/Users/jeffwang/miniforge3/bin/python spatial/run_analysis.py --check
/Users/jeffwang/miniforge3/bin/python -m unittest discover -s spatial -p 'test_*.py' -v
```

The preflight passed on the supplied files. The seven tests cover:

- A hand-checked lattice triangle plus an isolate, missing-neighbor gaps, symmetric edges,
  duplicate/invalid lattice sites, and edge agreement of 1/3.
- Independently known Moran I of -1/2 on a complete three-spot graph; constant-expression
  undefined values; exclusion of isolates from centering.
- Exhaustive tiny label permutations and the expected null mean; deterministic seed-42
  sampling, inclusive empirical tails and a one-cluster null returning 1.
- Independent rank-sum/tie-corrected Kruskal–Wallis versus SciPy.
- Rejection of an unfilled QC template and fewer than 100 permutations.
- Retention of undefined DE for one cluster and undefined Moran I for constant genes.
- Complete temporary synthetic run: 144 spots, 400 genes, shuffled coordinate rows,
  both CSV formats, QC, three resolutions, 100 candidates, 100 permutations, all plots,
  and independent verification of every gene/null value. It also checks review-stage
  protections, frozen resolution after a partial failure, missing/duplicate barcodes,
  and detection of modified output evidence.

The synthetic UMAP/tissue comparison and gene maps were visually inspected. A crowded
legend and unused second plot row were corrected. Synthetic files are test fixtures,
not mouse-brain results and not evidence toward T1–T5. Tests do not establish image
alignment, suitable real-data QC thresholds, anatomical identities, or biological validity.

Some third-party pandas/NumPy deprecation warnings are emitted in this pinned environment;
they did not prevent the checks. No dependency was installed or upgraded during this work.

## Added standalone Sonnet workflow — 2026-10-29

The original seven-test numerical scope remains valid. The suite now has **10 passing tests**, including a complete synthetic run with mocked Sonnet proposals, user plan/QC/resolution approval, numerical verification, report acceptance and audit fields. It checks plan pause/resume without repeated requests, absence of spatial evidence in the resolution prompt, truncated-response rejection with saved-response reuse, and rejection of unretrieved source IDs. `--check` passed again. These are mocked model responses; no live Sonnet request/account access or biological interpretation was validated. Task 1's 13 and Task 2's 9 offline tests also passed during the shared fresh-run setup. All active configs use `claude-sonnet-5-5`. Earlier real runs are archived; see CLEAN_RUN.md.
