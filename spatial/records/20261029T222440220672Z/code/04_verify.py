"""Verify raw-matrix QC, lattice edges and statistics through separate calculations."""
import argparse
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
import anndata as ad
from scipy import sparse, stats
from workflow_common import (read_json, save_json, folders, integrity, require, resolution_key,
                             input_paths, SEED)


def independent_h(values, labels):
    groups = np.unique(labels)
    if len(groups) < 2 or np.ptp(values) == 0:
        return np.nan
    ranks = stats.rankdata(values)
    n = len(values)
    uncorrected = 12 / (n * (n + 1)) * sum(ranks[labels == k].sum() ** 2 / np.sum(labels == k) for k in groups) - 3 * (n + 1)
    _, ties = np.unique(values, return_counts=True)
    correction = 1 - np.sum(ties.astype(float) ** 3 - ties) / (n ** 3 - n)
    return uncorrected / correction


def verify(run):
    integrity(run, 'spatial')
    tables, figures = folders(run)
    c = read_json(run / 'config.json')
    q = read_json(run / 'qc_review.json')
    result = read_json(run / 'spatial_summary.json')
    # Bypass Scanpy's reader and QC routines for this independent raw-count check.
    with h5py.File(input_paths(c)[0], 'r') as f:
        g = f['matrix']
        raw = sparse.csc_matrix((g['data'][:], g['indices'][:], g['indptr'][:]), shape=tuple(g['shape'][:]))
        barcodes = g['barcodes'][:].astype(str)
        symbols = g['features/name'][:].astype(str)
        ids = g['features/id'][:].astype(str)
        feature_types = g['features/feature_type'][:].astype(str)
    is_gene = feature_types == 'Gene Expression'
    raw, symbols, ids = raw[is_gene].tocsc(), symbols[is_gene], ids[is_gene]
    raw.eliminate_zeros()
    total = np.asarray(raw.sum(axis=0)).ravel()
    detected = np.diff(raw.indptr)
    mt_counts = np.asarray(raw[np.char.startswith(np.char.lower(symbols), 'mt-')].sum(axis=0)).ravel()
    mt = np.divide(mt_counts * 100., total, out=np.zeros(len(total)), where=total > 0)
    qc = pd.read_csv(tables / 'qc_spots.csv', index_col='barcode')
    require(list(qc.index) == list(barcodes), 'QC barcode order differs from raw file')
    for col, expected in [('total_counts', total), ('n_genes_by_counts', detected), ('pct_counts_mt', mt)]:
        require(np.allclose(qc[col], expected, rtol=1e-5), 'Independent raw QC disagrees: ' + col)
    # Read position CSV directly rather than using the production join/graph builder.
    path = input_paths(c)[1]
    if path.name.endswith('_list.csv'):
        pos = pd.read_csv(path, header=None, names=['barcode', 'in_tissue', 'array_row', 'array_col', 'y', 'x'])
    else:
        pos = pd.read_csv(path).rename(columns={'pxl_row_in_fullres': 'y', 'pxl_col_in_fullres': 'x'})
    pos = pos.set_index('barcode')
    require(np.array_equal(qc.in_tissue, pos.loc[barcodes, 'in_tissue']), 'Tissue flags differ')
    retained = ((qc.in_tissue == 1) & (detected >= q['min_genes']) & (detected <= q['max_genes']) &
                (total >= q['min_counts']) & (total <= q['max_counts']) & (mt <= q['max_pct_mt']))
    decisions = pd.read_csv(tables / 'qc_decisions.csv', index_col='barcode')
    require(decisions.index.equals(qc.index) and np.array_equal(decisions.retained, retained), 'Retained spots disagree')
    primary = resolution_key(read_json(run / 'cluster_review.json')['resolution'])
    obs = pd.read_csv(tables / 'expression_clusters.csv', index_col='barcode', dtype={primary: str})
    require(obs.index.equals(qc.index[retained]), 'Expression analysis changed retained spots/order')
    mapped = pd.read_csv(tables / 'spatial_spots.csv', index_col='barcode', dtype={'cluster': str})
    require(mapped.index.equals(obs.index) and np.array_equal(mapped.cluster, obs[primary]), 'Tissue labels differ from frozen expression labels')
    for saved, source in [('array_row', 'array_row'), ('array_col', 'array_col'),
                          ('pxl_row_in_fullres', 'y'), ('pxl_col_in_fullres', 'x')]:
        require(np.array_equal(mapped[saved], pos.loc[obs.index, source]), 'Spatial coordinates reordered/mutated')
    coords = pos.loc[obs.index, ['array_row', 'array_col']].to_numpy()
    # Independent pairwise lattice metric; bounded temporary array per row.
    expected_edges = set()
    for i, (r, col) in enumerate(coords):
        dr, dc = coords[i + 1:, 0] - r, coords[i + 1:, 1] - col
        for j in np.flatnonzero(3 * dr ** 2 + dc ** 2 == 4) + i + 1:
            expected_edges.add((i, int(j)))
    saved_edges = pd.read_csv(tables / 'physical_edges.csv')
    lookup = {b: i for i, b in enumerate(obs.index)}
    edges = [(lookup[a], lookup[b]) for a, b in saved_edges.itertuples(index=False, name=None)]
    require(len(edges) == len(set(edges)) and set(edges) == expected_edges, 'Independent physical graph disagrees')
    labels = obs[primary].to_numpy()
    observed = sum(labels[i] == labels[j] for i, j in edges) / len(edges)
    require(np.isclose(observed, result['observed'], rtol=0, atol=1e-12), 'Edge agreement disagrees')
    e = np.array(edges)
    degree = np.bincount(e.ravel(), minlength=len(obs))
    require(np.array_equal(degree, mapped.degree), 'Degree table disagrees')
    null = pd.read_csv(tables / 'null_distribution.csv').edge_agreement.to_numpy()
    rng = np.random.default_rng(SEED)
    for value in null:
        shuffled = rng.permutation(labels)
        expected = np.count_nonzero(shuffled[e[:, 0]] == shuffled[e[:, 1]]) / len(e)
        require(np.isclose(value, expected, rtol=0, atol=1e-12), 'Seeded null does not reproduce')
    # Avoid CSV-rounding differences when counting exact null/observed ties.
    null_counts = np.rint(null * len(e)).astype(int)
    same_edges = sum(labels[i] == labels[j] for i, j in edges)
    tail = (1 + np.count_nonzero(null_counts >= same_edges)) / (len(null) + 1)
    require(len(null) == c['n_randomizations'] and np.isclose(tail, result['empirical_upper_tail']), 'Empirical tail disagrees')
    expression = ad.read_h5ad(run / 'data/candidate_expression.h5ad')
    require(expression.obs_names.equals(obs.index), 'Expression alignment differs')
    genes = pd.read_csv(tables / 'candidate_genes.csv')
    require(list(genes.gene) == list(expression.var_names) and len(genes) == c['n_candidates'], 'Candidate set changed')
    retained_raw = raw[:, np.asarray(retained)]
    keep_gene = np.asarray((retained_raw > 0).sum(axis=1)).ravel() >= c['min_spots_per_gene']
    filtered = retained_raw[keep_gene]
    require(len(set(ids)) == len(ids), 'Independent verifier requires unique gene IDs')
    raw_index = {g: i for i, g in enumerate(ids)}
    selected_raw = retained_raw[[raw_index[g] for g in genes.gene_ids]].toarray().T
    normalization_total = np.asarray(filtered.sum(axis=0)).ravel()
    expected_expression = np.log1p(selected_raw / normalization_total[:, None] * c['target_sum'])
    x = expression.X.toarray() if sparse.issparse(expression.X) else np.asarray(expression.X)
    require(np.allclose(x, expected_expression, rtol=1e-5, atol=1e-6), 'Candidate expression differs from independent normalization')
    scores = pd.read_csv(tables / 'gene_rankings.csv').set_index('gene').loc[genes.gene]
    active = degree > 0
    for j in range(x.shape[1]):
        z = x[:, j].astype(float) - x[active, j].astype(float).mean()
        denominator = np.dot(z[active], z[active])
        score = active.sum() / len(e) * sum(z[i] * z[k] for i, k in edges) / denominator if denominator else np.nan
        require(np.isclose(score, scores.iloc[j].moran_i, equal_nan=True), 'Independent Moran I disagrees')
        require(np.isclose(independent_h(x[:, j], labels), scores.iloc[j].kw_h, equal_nan=True), 'Independent tie-corrected H disagrees')
    for score, rank in [('moran_i', 'spatial_rank'), ('kw_h', 'de_rank')]:
        require(np.allclose(scores[score].rank(ascending=False, method='average'), scores[rank], equal_nan=True), 'Gene ranks disagree')
    expected_figures = ['qc_distributions.png', 'qc_joint.png', 'qc_tissue.png', 'clusters_umap_and_tissue.png',
                        'randomized_control.png', 'gene_tissue_maps.png', 'de_vs_spatial_ranks.png']
    for name in expected_figures:
        require((figures / name).is_file() and (figures / name).stat().st_size > 0, 'Missing figure: ' + name)
    report = {'passed': True, 'raw_spots_checked': len(qc), 'retained_spots_checked': len(obs),
              'physical_edges_checked': len(edges), 'null_repetitions_checked': len(null),
              'gene_statistics_checked': len(genes), 'input_and_artifact_hashes_checked': True,
              'independent_checks': ['h5py raw QC', 'barcode join and QC retention', 'pairwise lattice graph',
                                     'edge agreement', 'seeded null and ties', 'raw candidate normalization',
                                     'Moran edge sum', 'rank-sum/tie-corrected Kruskal–Wallis'],
              'scope': 'Numerical verification, not visual alignment or biological validation'}
    save_json(run / 'verification.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    print(verify(parser.parse_args().run.resolve()))
