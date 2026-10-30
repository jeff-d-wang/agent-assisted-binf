# Independent recheck of revision-1 expression claims from the cached raw log layer.
# Usage: python -I check_rev1.py single_cell/runs/20261029T211700335443Z/cache/baseline.h5ad
import sys, numpy as np, anndata as ad
a = ad.read_h5ad(sys.argv[1]); X = a.raw.to_adata()
def stat(key, cl, gs, neg=False):
    m = (a.obs[key].astype(str) != cl) if neg else (a.obs[key].astype(str) == cl)
    s = X[m.values]
    return {g: (round(float((s[:, g].X > 0).mean())*100, 1), round(float(s[:, g].X.mean()), 2)) for g in gs}
print('1p5 c10 platelet', stat('res_1p5', '10', ['PPBP','PF4','GP9','ITGA2B','GP1BA','LYZ','S100A9','S100A8','HLA-DRA','CD3D']))
for c in sorted(a.obs.res_1p5.astype(str).unique(), key=int):
    if c != '10': print('  1p5 c'+c, 'PPBP %', stat('res_1p5', c, ['PPBP'])['PPBP'][0], 'LYZ meanlog', stat('res_1p5', c, ['LYZ'])['LYZ'][1])
print('1p5 c0 CD4/CD8A', stat('res_1p5','0',['CD4','CD8A']), 'rest', stat('res_1p5','0',['CD4','CD8A'],neg=True))
print('res1 c7 DC', stat('res_1','7',['FCER1A','CLEC10A','CD1C','SERPINF1','CD3D','NKG7','CD79A','MS4A1','CD79B','HLA-DRA','FCN1','S100A8']))
print('res1 c2 mono', stat('res_1','2',['CD3D','NKG7','CD79A','HLA-DRA','FCN1','S100A8']))
print('res1 c3 B', stat('res_1','3',['MS4A1','CD79B']))
print('res0p6 c4 FCGR3A', stat('res_0p6','4',['FCGR3A']), 'rest', stat('res_0p6','4',['FCGR3A'],neg=True))
