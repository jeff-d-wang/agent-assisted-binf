"""Read-only checks of the submission run, without importing pipeline code.

Usage: python spatial/review/check_task3.py
Reproduces the human review's numerical checks; does not choose scientific labels.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = '20261029T222440220672Z'
SEED = 7  # Independent null check; production used seed 42.


def check():
    tables = ROOT / 'spatial/tables' / RUN_ID
    run = ROOT / 'spatial/runs' / RUN_ID
    if not run.exists():
        run = ROOT / 'spatial/records' / RUN_ID
    obs = pd.read_csv(tables / 'expression_clusters.csv', index_col='barcode')
    mapped = pd.read_csv(tables / 'spatial_spots.csv', index_col='barcode')
    positions = pd.read_csv(
        ROOT / 'datasets/visium_mouse_brain/spatial/tissue_positions_list.csv',
        header=None, names=['barcode', 'in_tissue', 'array_row', 'array_col',
                           'pxl_row_in_fullres', 'pxl_col_in_fullres']).set_index('barcode')
    assert obs.index.equals(mapped.index)
    columns = list(positions.columns)
    assert np.array_equal(mapped[columns], positions.loc[obs.index, columns])
    assert (mapped.in_tissue == 1).all()
    coords = positions.loc[obs.index, ['array_row', 'array_col']].to_numpy()
    edges = []
    for i in range(len(coords)):
        delta = coords[i + 1:] - coords[i]
        neighbors = np.flatnonzero(3 * delta[:, 0] ** 2 + delta[:, 1] ** 2 == 4)
        edges.extend((i, int(j + i + 1)) for j in neighbors)
    edge = np.asarray(edges)
    saved = pd.read_csv(tables / 'physical_edges.csv')
    lookup = {barcode: i for i, barcode in enumerate(obs.index)}
    actual = {(lookup[a], lookup[b]) for a, b in saved.itertuples(index=False, name=None)}
    assert actual == set(edges) and len(saved) == len(edges)
    degree = np.bincount(edge.ravel(), minlength=len(obs))
    assert np.array_equal(degree, mapped.degree)

    def agreement(labels):
        labels = np.asarray(labels)
        return float(np.mean(labels[edge[:, 0]] == labels[edge[:, 1]]))

    def moran(values):
        centered = np.asarray(values) - np.mean(values)
        return float(len(values) / len(edge) *
                     np.sum(centered[edge[:, 0]] * centered[edge[:, 1]]) /
                     np.dot(centered, centered))

    labels = obs.res_0p5.to_numpy()
    by_resolution = {name: agreement(obs[name]) for name in ['res_0p3', 'res_0p5', 'res_0p8']}
    sensitivity = pd.read_csv(tables / 'spatial_resolution_sensitivity.csv')
    for row in sensitivity.itertuples():
        assert np.isclose(by_resolution['res_' + format(row.resolution, 'g').replace('.', 'p')], row.edge_agreement)
    null = pd.read_csv(tables / 'null_distribution.csv').edge_agreement.to_numpy()
    tail = (1 + np.count_nonzero(null >= by_resolution['res_0p5'])) / (len(null) + 1)
    rng = np.random.default_rng(SEED)
    own_null = np.array([agreement(rng.permutation(labels)) for _ in range(999)])
    rankings = pd.read_csv(tables / 'gene_rankings.csv').set_index('gene')
    quality = {}
    for name in ['total_counts', 'pct_counts_mt']:
        values = obs[name].to_numpy()
        h = float(kruskal(*(values[labels == c] for c in np.unique(labels))).statistic)
        quality[name] = {'kw_h': h, 'moran_i': moran(values),
                         'h_rank_among_candidates': int(1 + (rankings.kw_h > h).sum()),
                         'quantile_edge_agreement': agreement(pd.qcut(values, 14, labels=False))}

    means = pd.read_csv(tables / 'gene_cluster_means.csv', index_col='cluster')
    peak_means = {g: {str(k): float(v) for k, v in means[g].nlargest(3).items()}
                  for g in ['Dnali1', '2900040C04Rik', 'Pmch']}
    c12 = labels == 12
    internal_edges = int(np.sum(c12[edge[:, 0]] & c12[edge[:, 1]]))
    incident_edges = int(np.sum(c12[edge[:, 0]] | c12[edge[:, 1]]))
    # Endpoint-based share: internal edges count twice, boundary edges once.
    within_share = float(2 * np.sum(c12[edge[:, 0]] & c12[edge[:, 1]]) / degree[c12].sum())
    group_sets = [set(obs.index[obs[key] == cluster]) for key, cluster in
                  [('res_0p3', 9), ('res_0p5', 12), ('res_0p8', 15)]]
    assert group_sets[0] == group_sets[1] == group_sets[2]
    request_path = run / 'api/003.request.json'
    image_count = None  # Raw API transcripts are intentionally excluded from the deliverable.
    if request_path.exists():
        request = json.loads(request_path.read_text())
        image_count = sum(b['type'] == 'image' for m in request['messages']
                          if isinstance(m['content'], list) for b in m['content'])
        assert image_count == 3
    summary = json.loads((run / 'spatial_summary.json').read_text())
    assert np.isclose(tail, summary['empirical_upper_tail'])
    return {'spots': len(obs), 'edges': len(edge), 'isolates': int((degree == 0).sum()),
            'edge_agreement': by_resolution, 'saved_null_tail': tail,
            'independent_null_seed': SEED, 'independent_null_mean': float(own_null.mean()),
            'independent_null_sd': float(own_null.std()), 'qc_covariates': quality,
            'peak_cluster_means': peak_means, 'cluster12_n': int(c12.sum()),
            'cluster12_internal_edges': internal_edges, 'cluster12_incident_edges': incident_edges,
            'cluster12_within_share_of_incident_edges': internal_edges / incident_edges,
            'cluster12_within_edge_endpoint_share': within_share,
            'stable_56_spot_membership': True,
            'gene_checks': rankings.loc[['Dnali1', '2900040C04Rik', 'Pmch', 'Gm4952'],
                                       ['moran_i', 'kw_h', 'fraction_detected', 'spatial_rank', 'de_rank']].to_dict('index'),
            'cluster_request_image_count': image_count,
            'scope': 'Numerical reproduction; human visual and scientific judgments are separate.'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
