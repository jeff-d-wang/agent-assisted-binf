"""File layout and validated settings for the standalone Claude workflow."""
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

SEED = 42  # Every stochastic scientific step uses this recorded seed.
PACKAGES = ('scanpy', 'anndata', 'numpy', 'pandas', 'scipy', 'matplotlib',
            'scikit-learn', 'igraph', 'leidenalg', 'umap-learn', 'pynndescent', 'numba')


def now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def read_json(path):
    return json.loads(Path(path).read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def folders(run):
    run = Path(run)
    return (run.parent.parent / 'tables' / run.name,
            run.parent.parent / 'figures' / run.name)


def event(run, kind, **values):
    with (Path(run) / 'events.jsonl').open('a') as fh:
        fh.write(json.dumps(dict(time=now(), event=kind, **values)) + '\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, low, high, name, integer=False):
    require(type(value) in ((int,) if integer else (int, float)) and
            math.isfinite(value) and low <= value <= high, f'Invalid {name}: {value}')


def validate_plan(plan):
    require(set(plan) == {'rationale', 'settings'}, 'Plan needs rationale and settings only')
    require(isinstance(plan['rationale'], str) and bool(plan['rationale'].strip()), 'Explain the plan')
    s = plan['settings']
    require(set(s) == {'target_sum', 'n_top_genes', 'n_pcs', 'n_neighbors', 'baseline_resolution',
                       'resolutions', 'sample_fraction', 'min_cells_per_gene', 'scale_max'},
            'Unsupported or missing settings; see the plan prompt')
    for key, lo, hi, integer in [('target_sum', 1000, 100000, False), ('n_top_genes', 100, 5000, True),
                                ('n_pcs', 2, 100, True), ('n_neighbors', 2, 100, True),
                                ('sample_fraction', .6, .8, False), ('min_cells_per_gene', 1, 20, True),
                                ('scale_max', 5, 20, False), ('baseline_resolution', .05, 3, False)]:
        number(s[key], lo, hi, key, integer)
    require(isinstance(s['resolutions'], list) and 3 <= len(s['resolutions']) <= 5,
            'Choose three to five resolutions')
    for r in s['resolutions']:
        number(r, .05, 3, 'resolution')
    require(len(set(s['resolutions'])) == len(s['resolutions']) and
            s['baseline_resolution'] in s['resolutions'], 'Use distinct resolutions including baseline')
    return plan


def validate_qc(qc):
    require(set(qc) == {'rationale', 'min_genes', 'max_genes', 'min_counts', 'max_counts', 'max_pct_mt'},
            'QC fields do not match the supported filters')
    require(isinstance(qc['rationale'], str) and bool(qc['rationale'].strip()), 'Explain QC thresholds')
    for key in ('min_genes', 'max_genes', 'min_counts', 'max_counts'):
        number(qc[key], 0, 10000000, key, True)
    number(qc['max_pct_mt'], 0, 100, 'max_pct_mt')
    require(qc['min_genes'] < qc['max_genes'] and qc['min_counts'] < qc['max_counts'],
            'QC minimum must be below maximum')
    return qc


def qc_failures(obs, qc):
    import pandas as pd
    return pd.DataFrame({
        'low_genes': obs.n_genes_by_counts < qc['min_genes'],
        'high_genes': obs.n_genes_by_counts > qc['max_genes'],
        'low_counts': obs.total_counts < qc['min_counts'],
        'high_counts': obs.total_counts > qc['max_counts'],
        'high_mt': obs.pct_counts_mt > qc['max_pct_mt'],
    }, index=obs.index)


def resolution_name(value):
    return 'res_' + format(value, 'g').replace('.', 'p')


def load_counts(input_dir):
    import numpy as np
    import scanpy as sc
    adata = sc.read_10x_mtx(input_dir, var_names='gene_symbols', cache=False)
    adata.var_names_make_unique()
    require(adata.obs_names.is_unique and adata.n_obs > 0 and adata.n_vars > 0,
            'Expected a nonempty matrix with unique cell barcodes')
    values = adata.X.data
    require(np.isfinite(values).all() and (values >= 0).all() and
            np.equal(values, np.floor(values)).all(), 'Input must contain nonnegative integer counts')
    adata.X.eliminate_zeros()
    adata.var['mt'] = adata.var_names.str.startswith('MT-')
    require(adata.var.mt.any(), 'No MT- genes found; verify human gene symbols before QC')
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
    require((adata.obs.total_counts > 0).all(), 'Zero-count cells need explicit handling')
    return adata
