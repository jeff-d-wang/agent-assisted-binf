"""Task 3 input validation, provenance, and small auditable statistical functions."""
import hashlib
import importlib.metadata
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

SEED = 42
PACKAGES = ('scanpy', 'anndata', 'numpy', 'pandas', 'scipy', 'matplotlib',
            'scikit-learn', 'igraph', 'leidenalg', 'umap-learn', 'numba',
            'pynndescent', 'h5py')
POSITION_COLUMNS = ['barcode', 'in_tissue', 'array_row', 'array_col',
                    'pxl_row_in_fullres', 'pxl_col_in_fullres']
QC_COLUMNS = ['total_counts', 'n_genes_by_counts', 'pct_counts_mt']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text())


def save_json(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def versions():
    return {p: importlib.metadata.version(p) for p in PACKAGES}


def validate_config(c):
    expected = {'input_dir', 'model', 'counts_file', 'seed', 'target_sum', 'min_spots_per_gene',
                'n_hvgs', 'n_candidates', 'n_pcs', 'n_neighbors', 'scale_max',
                'resolutions', 'n_randomizations'}
    require(set(c) == expected, 'Config fields must match spatial/config.json')
    require(isinstance(c['model'], str) and c['model'].startswith('claude-'), 'Supply an explicit Claude model ID')
    for key in expected - {'input_dir', 'model', 'counts_file', 'resolutions'}:
        require(type(c[key]) is int and c[key] > 0, f'{key} must be a positive integer')
    require(c['seed'] == SEED, 'This workflow records seed 42')
    require(100 <= c['n_candidates'] <= 300 and c['n_hvgs'] >= c['n_candidates'],
            'Use 100–300 candidates and at least that many clustering HVGs')
    require(2 <= c['n_pcs'] < c['n_hvgs'] and c['n_neighbors'] >= 2, 'Invalid PCA/neighbors')
    require(c['n_randomizations'] >= 100, 'At least 100 randomizations required')
    r = c['resolutions']
    require(isinstance(r, list) and len(r) == 3 and len(set(r)) == 3 and
            all(type(v) in (int, float) and math.isfinite(v) and 0 < v <= 3 for v in r),
            'Specify three distinct positive Leiden resolutions <=3')
    require(isinstance(c['input_dir'], str) and bool(c['input_dir']), 'Missing input_dir')
    require(isinstance(c['counts_file'], str) and Path(c['counts_file']).name == c['counts_file'],
            'counts_file must be a filename')
    return c


def input_paths(c):
    root = Path(c['input_dir'])
    old, new = root / 'spatial/tissue_positions_list.csv', root / 'spatial/tissue_positions.csv'
    require(old.exists() != new.exists(), 'Expected exactly one old/new tissue positions CSV')
    paths = [root / c['counts_file'], old if old.exists() else new,
             root / 'spatial/scalefactors_json.json', root / 'spatial/tissue_hires_image.png']
    require(all(p.is_file() for p in paths), 'Missing Visium inputs; see extraction instructions')
    return paths


def positions(c):
    path = input_paths(c)[1]
    p = pd.read_csv(path, header=None, names=POSITION_COLUMNS) if path.name.endswith('_list.csv') else pd.read_csv(path)
    require(list(p.columns) == POSITION_COLUMNS, 'Unexpected tissue-position columns/order')
    require(p.barcode.notna().all() and p.barcode.is_unique, 'Missing/duplicate spatial barcodes')
    for column in POSITION_COLUMNS[1:]:
        p[column] = pd.to_numeric(p[column], errors='raise')
    values = p[POSITION_COLUMNS[1:]].to_numpy()
    require(np.isfinite(values).all() and (values >= 0).all(), 'Invalid tissue coordinates')
    require(np.equal(values[:, :3], np.floor(values[:, :3])).all(), 'Array coordinates must be integers')
    require(p.in_tissue.isin([0, 1]).all(), 'in_tissue must be 0 or 1')
    require(not p.duplicated(['array_row', 'array_col']).any(), 'Duplicate lattice sites')
    require(((p.array_row - p.array_col) % 2 == 0).all(), 'Expected original Visium hexagonal lattice')
    return p.set_index('barcode')


def counts(c):
    import scanpy as sc
    a = sc.read_10x_h5(input_paths(c)[0], gex_only=True)
    a.var['gene_symbol'] = a.var_names.astype(str)
    a.var_names_make_unique()
    require(a.obs_names.is_unique and a.n_obs > 0 and a.n_vars > 0, 'Invalid count matrix')
    a.X = sparse.csr_matrix(a.X)
    a.X.eliminate_zeros()
    v = a.X.data
    require(np.isfinite(v).all() and (v >= 0).all() and (v == np.floor(v)).all(),
            'Expected nonnegative integer counts')
    a.var['mt'] = a.var.gene_symbol.str.lower().str.startswith('mt-')
    require(a.var.mt.any(), 'No mouse mt- genes; verify gene symbols before QC')
    sc.pp.calculate_qc_metrics(a, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
    a.obs.loc[a.obs.total_counts == 0, 'pct_counts_mt'] = 0
    p = positions(c)
    require(a.obs_names.isin(p.index).all(), 'Count barcodes missing from spatial positions')
    a.obs['in_tissue'] = p.loc[a.obs_names, 'in_tissue'].to_numpy()
    return a


def validate_qc(q):
    require(set(q) == {'rationale', 'min_genes', 'max_genes', 'min_counts', 'max_counts', 'max_pct_mt'},
            'Use qc_review.template.json fields')
    require(isinstance(q['rationale'], str) and len(q['rationale'].strip()) >= 20,
            'Record a distribution-based QC rationale (at least 20 characters)')
    for key in ('min_genes', 'max_genes', 'min_counts', 'max_counts'):
        require(type(q[key]) is int and q[key] >= 1, f'Fill {key} with a positive integer')
    require(q['min_genes'] <= q['max_genes'] and q['min_counts'] <= q['max_counts'], 'Reversed QC limits')
    require(type(q['max_pct_mt']) in (int, float) and 0 <= q['max_pct_mt'] <= 100,
            'Fill max_pct_mt with a percentage from 0 to 100')
    return q


def qc_decisions(obs, q):
    result = pd.DataFrame({
        'outside_tissue': obs.in_tissue != 1,
        'low_genes': obs.n_genes_by_counts < q['min_genes'],
        'high_genes': obs.n_genes_by_counts > q['max_genes'],
        'low_counts': obs.total_counts < q['min_counts'],
        'high_counts': obs.total_counts > q['max_counts'],
        'high_mt': obs.pct_counts_mt > q['max_pct_mt'],
    }, index=obs.index)
    result['retained'] = ~result.any(axis=1)
    return result


def folders(run):
    task = Path(run).parent.parent
    return task / 'tables' / run.name, task / 'figures' / run.name


def seal(run, stage):
    save_json(run / 'state.json', {'stage': stage})
    paths = list(run.glob('*.json')) + list(run.glob('*.md'))
    for folder in (run / 'code', run / 'data', *folders(run)):
        paths.extend(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    save_json(run / 'manifest.json', {str(p.resolve()): digest(p) for p in paths
                                    if p.name not in ('manifest.json', 'verification.json')})


def integrity(run, stage=None):
    meta = read_json(run / 'inputs.json')
    require(versions() == meta['versions'], 'Package versions changed; use the recorded environment')
    for path, expected in {**meta['sha256'], **read_json(run / 'manifest.json')}.items():
        require(Path(path).is_file() and digest(path) == expected, 'Input/evidence changed: ' + path)
    if stage is not None:
        require(read_json(run / 'state.json')['stage'] == stage, f'Expected completed stage: {stage}')


def log_step(run, text):
    with (run / 'AGENT_LOG.md').open('a') as f:
        f.write(f'\n## {datetime.now(timezone.utc).isoformat()}\n{text}\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def event(run, kind, **values):
    with (run / 'events.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(time=now(), event=kind, **values)) + '\n')


def resolution_key(r):
    return 'res_' + format(r, 'g').replace('.', 'p')


def lattice_graph(coords):
    coords = np.asarray(coords)
    require(coords.ndim == 2 and coords.shape[1] == 2 and np.isfinite(coords).all(), 'Invalid lattice coordinates')
    require((coords >= 0).all() and (coords == np.floor(coords)).all() and
            ((coords[:, 0] - coords[:, 1]) % 2 == 0).all(), 'Invalid Visium lattice sites')
    lookup = {tuple(rc): i for i, rc in enumerate(coords)}
    require(len(lookup) == len(coords), 'Duplicate lattice sites')
    edges = []
    # Only forward offsets: each undirected immediate-neighbor edge appears once.
    for (row, col), i in lookup.items():
        for dr, dc in ((0, 2), (1, -1), (1, 1)):
            j = lookup.get((row + dr, col + dc))
            if j is not None:
                edges.append((min(i, j), max(i, j)))
    e = np.asarray(sorted(edges), dtype=int).reshape(-1, 2)
    w = sparse.csr_matrix((np.ones(len(e) * 2),
                         (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])),
                         shape=(len(coords), len(coords)))
    return e, w


def agreement(labels, edges):
    require(len(edges) > 0, 'No physical edges; spatial statistic is undefined')
    labels = np.asarray(labels)
    return float(np.mean(labels[edges[:, 0]] == labels[edges[:, 1]]))


def randomized_agreement(labels, edges, n, seed=SEED):
    rng = np.random.default_rng(seed)
    observed = agreement(labels, edges)
    null = np.array([agreement(rng.permutation(labels), edges) for _ in range(n)])
    return observed, null, float((1 + np.count_nonzero(null >= observed)) / (n + 1))


def moran(values, w):
    x = np.asarray(values, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    # Exclude isolates from centering and N; they remain in clustering and DE.
    active = np.asarray(w.sum(axis=1)).ravel() > 0
    w = w[active][:, active]
    require(w.sum() > 0, 'Moran I undefined without edges')
    z = x[active] - x[active].mean(axis=0)
    denominator = (z * z).sum(axis=0)
    return np.divide(len(z) * (z * (w @ z)).sum(axis=0), float(w.sum()) * denominator,
                     out=np.full(x.shape[1], np.nan), where=denominator > 0)


def cluster_colors(labels):
    import matplotlib.pyplot as plt
    keys = sorted(set(map(str, labels)))
    cmap = plt.get_cmap('tab20' if len(keys) <= 20 else 'gist_rainbow', max(20, len(keys)))
    return {key: cmap(i) for i, key in enumerate(keys)}


def tissue_axes(ax, p, c):
    import matplotlib.pyplot as plt
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Circle
    scale = read_json(input_paths(c)[2])
    factor, diameter = scale['tissue_hires_scalef'], scale['spot_diameter_fullres']
    require(np.isfinite([factor, diameter]).all() and factor > 0 and diameter > 0, 'Invalid image scale')
    image = plt.imread(input_paths(c)[3])
    xy = p[['pxl_col_in_fullres', 'pxl_row_in_fullres']].to_numpy() * factor
    require((xy >= 0).all() and (xy[:, 0] < image.shape[1]).all() and
            (xy[:, 1] < image.shape[0]).all(), 'Spot centers outside scaled histology; inspect alignment')
    ax.imshow(image, origin='upper')
    ax.set(xlim=(-.5, image.shape[1] - .5), ylim=(image.shape[0] - .5, -.5), aspect='equal')
    ax.set_axis_off()
    circles = PatchCollection([Circle(point, diameter * factor / 2) for point in xy], linewidths=0, alpha=.8)
    ax.add_collection(circles)
    return circles
