# Independent recheck: are the DC-like cells the same barcodes in every run where they separate?
# Usage: python -I check_dc_overlap.py single_cell/tables/20261029T211700335443Z
import sys
from pathlib import Path
import pandas as pd

T = Path(sys.argv[1])
cl = lambda n: pd.read_csv(T / f'cells_{n}.csv', index_col='cell', dtype={'cluster': str}).cluster
ids = lambda s, c: set(s[s == c].index)
dc = {n: ids(cl(n), c) for n, c in [('res_0p3', '4'), ('res_1', '7'), ('res_1p5', '9')]}
ds = cl('downsample')
sampled = dc['res_0p3'] & set(ds.index)
print('identical across 0.3/1.0/1.5:', dc['res_0p3'] == dc['res_1'] == dc['res_1p5'], len(dc['res_0p3']))
print('sampled into downsample:', len(sampled), '| in downsample cluster 5:', len(sampled & ids(ds, '5')),
      '| cluster 5 cells outside the 36:', len(ids(ds, '5') - dc['res_0p3']))
