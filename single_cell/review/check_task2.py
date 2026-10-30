"""Independent reviewer checks for Task 2 run 20261029T211700335443Z (read-only).

Usage: python -I check_task2.py REPO_ROOT  (scipy/sklearn/anndata only; no pipeline code)
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import mmread
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
import anndata as ad

root = Path(sys.argv[1])
run = '20261029T211700335443Z'
raw = root / 'datasets/pbmc3k/filtered_gene_bc_matrices/hg19'
T = root / 'single_cell/tables' / run
R = root / 'single_cell/runs' / run

# 1. QC from the raw Matrix Market file, own code
m = mmread(raw / 'matrix.mtx').tocsc()  # genes x cells
genes = pd.read_csv(raw / 'genes.tsv', sep='\t', header=None)[1]
total = np.asarray(m.sum(0)).ravel()
ngenes = np.asarray((m > 0).sum(0)).ravel()
mt = np.asarray(m[np.flatnonzero(genes.str.startswith('MT-'))].sum(0)).ravel() / total * 100
fail = pd.DataFrame(dict(low_genes=ngenes < 300, high_genes=ngenes > 2500, low_counts=total < 600,
                         high_counts=total > 9000, high_mt=mt > 8))
print('QC cells', m.shape[1], 'MT genes', genes.str.startswith('MT-').sum(),
      'retained', (~fail.any(axis=1)).sum(), dict(fail.sum()))
print('cells with mt>5%:', (mt > 5).sum(), 'mt>4%:', (mt > 4).sum(), 'genes<500:', (ngenes < 500).sum())

# 2. ARI and NMI from saved cell tables (sklearn, not pipeline code)
base = pd.read_csv(T / 'cells_res_0p6.csv', index_col='cell', dtype={'cluster': str})
for name in ['res_0p3', 'res_1', 'res_1p5', 'downsample']:
    o = pd.read_csv(T / f'cells_{name}.csv', index_col='cell', dtype={'cluster': str})
    b = base.loc[o.index, 'cluster']
    print(name, len(o), round(adjusted_rand_score(b, o.cluster), 4), round(normalized_mutual_info_score(b, o.cluster), 4))

# 3. Downsample recovery with the baseline cluster as denominator
o = pd.read_csv(T / 'cells_downsample.csv', index_col='cell', dtype={'cluster': str})
ct = pd.crosstab(base.loc[o.index, 'cluster'], o.cluster)
print('baseline (rows) x downsample (cols), shared cells\n', ct)

# 4. Marker detection fractions from the cached log-normalised raw layer
a = ad.read_h5ad(R / 'cache/baseline.h5ad')
X = a.raw.to_adata()
def pct(cl_key, cl, gs):
    sub = X[a.obs[cl_key].astype(str) == cl]
    return {g: round(float((sub[:, g].X > 0).mean()) * 100) for g in gs if g in X.var_names}
amb = ['CD3D', 'CD3E', 'CD8A', 'CD8B', 'GZMK', 'GNLY', 'FCGR3A', 'KLRF1', 'NCAM1', 'TRDC', 'TRGC1']
print('res_1 c4', pct('res_1', '4', amb)); print('res_1 c6', pct('res_1', '6', amb))
plt = ['PPBP', 'PF4', 'GP9', 'ITGA2B', 'CD3D', 'LYZ', 'S100A9', 'FCGR3A']
print('res_1p5 c10 (platelet-like)', pct('res_1p5', '10', plt))
dc = ['FCER1A', 'CD1C', 'CLEC10A', 'LILRA4', 'CLEC4C', 'IL3RA', 'CD3D', 'MS4A1', 'CD79A', 'LYZ', 'S100A9', 'NKG7']
print('res_1 c7 (DC-like)', pct('res_1', '7', dc))
print('res_0p6 c0 (T)', pct('res_0p6', '0', ['CD4', 'CD8A', 'IL7R', 'CCR7']))
print('res_0p6 c4 (FCGR3A mono)', pct('res_0p6', '4', ['CD14', 'FCGR3A', 'LYZ']))
