"""Independent raw-matrix QC and contingency-table checks; no Claude calls."""
import argparse
from math import comb
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import mmread
from workflow_common import SEED, digest, folders, read_json, save_json, require, qc_failures


def independent_ari(left, right):
    cross = pd.crosstab(np.asarray(left), np.asarray(right))
    n = int(cross.to_numpy().sum())
    pairs = comb(n, 2)
    if not pairs:
        return 1.0
    joint = sum(comb(int(v), 2) for v in cross.to_numpy().ravel())
    row = sum(comb(int(v), 2) for v in cross.sum(axis=1))
    col = sum(comb(int(v), 2) for v in cross.sum(axis=0))
    expected = row * col / pairs
    maximum = (row + col) / 2
    return (joint - expected) / (maximum - expected) if maximum != expected else 1.0


def verify(run, check_manifest=True):
    tables, figures = folders(run)
    inputs = read_json(run / 'inputs.json')
    for path, expected in inputs['sha256'].items():
        require(digest(path) == expected, 'Raw input changed: ' + path)
    if check_manifest:
        require((run / 'manifest.json').exists(), 'No sealed evidence manifest yet')
        for path, expected in read_json(run / 'manifest.json').items():
            require(digest(path) == expected, 'Saved evidence changed: ' + path)
    source = Path(read_json(run / 'config.json')['input_dir'])
    matrix = mmread(source / 'matrix.mtx').tocsc()
    matrix.eliminate_zeros()
    barcodes = pd.read_csv(source / 'barcodes.tsv', header=None)[0].astype(str)
    genes = pd.read_csv(source / 'genes.tsv', sep='\t', header=None)[1].astype(str)
    observed = pd.read_csv(tables / 'qc_cells.csv', index_col='cell')
    require(list(observed.index) == list(barcodes), 'QC barcode order differs from raw input')
    total = np.asarray(matrix.sum(axis=0)).ravel()
    detected = np.diff(matrix.indptr)
    mt = np.asarray(matrix[genes.str.startswith('MT-').to_numpy()].sum(axis=0)).ravel() / total * 100
    for key, expected in [('total_counts', total), ('n_genes_by_counts', detected), ('pct_counts_mt', mt)]:
        require(np.allclose(observed[key], expected, rtol=1e-5), 'Raw-matrix QC disagrees: ' + key)
    result = {'raw_cells_verified': len(observed), 'qc_independent_of_scanpy': True}
    if (run / 'computation.json').exists():
        meta = read_json(run / 'computation.json')
        decisions = pd.read_csv(tables / 'qc_decisions.csv', index_col='cell')
        failures = qc_failures(observed, read_json(run / 'qc.json'))
        require(decisions.index.equals(observed.index), 'QC decisions reordered')
        for column in failures:
            require(np.array_equal(decisions[column], failures[column]), 'QC exclusion mismatch: ' + column)
        kept = observed.index[~failures.any(axis=1)]
        require(np.array_equal(decisions.retained, ~failures.any(axis=1)), 'QC retained flags disagree')
        base = pd.read_csv(tables / f"cells_{meta['baseline']}.csv", dtype={'cluster': str}).set_index('cell')
        require(base.index.is_unique and base.index.equals(kept), 'Baseline differs from QC-passing cells')
        sample = pd.read_csv(tables / 'cells_downsample.csv', dtype={'cluster': str}).set_index('cell')
        n = int(np.floor(len(kept) * meta['settings']['sample_fraction']))
        idx = np.sort(np.random.default_rng(SEED).choice(len(kept), n, replace=False))
        require(sample.index.equals(kept[idx]), 'Seeded subsample membership differs')
        metrics = pd.read_csv(tables / 'robustness_metrics.csv')
        require(set(metrics.comparison) == set(meta['runs']) - {meta['baseline']}, 'Missing comparison')
        overlaps = pd.read_csv(tables / 'cluster_overlaps.csv', dtype={'baseline_cluster': str, 'other_cluster': str})
        for row in metrics.itertuples():
            other = pd.read_csv(tables / f'cells_{row.comparison}.csv', dtype={'cluster': str}).set_index('cell')
            require(other.index.is_unique and other.index.isin(base.index).all(), 'Invalid comparison barcodes')
            if row.comparison != 'downsample':
                require(other.index.equals(base.index), 'Resolution changed cells')
                require(np.allclose(other[['umap_1', 'umap_2']], base[['umap_1', 'umap_2']]), 'Resolution changed embedding')
            left = base.loc[other.index, 'cluster']
            require(row.n_shared == len(other), 'Shared-cell denominator is wrong')
            require(np.isclose(independent_ari(left, other.cluster), row.ari), 'Independent ARI disagrees')
            expected_cross = pd.crosstab(left, other.cluster)
            saved = overlaps[overlaps.comparison == row.comparison]
            require(int(saved.n_cells.sum()) == len(other), 'Overlap totals disagree')
            for edge in saved.itertuples():
                count = int(expected_cross.loc[edge.baseline_cluster, edge.other_cluster])
                require(edge.n_cells == count and
                        np.isclose(edge.fraction_of_baseline, count / expected_cross.loc[edge.baseline_cluster].sum()) and
                        np.isclose(edge.fraction_of_other, count / expected_cross[edge.other_cluster].sum()), 'Overlap fractions disagree')
        for name in meta['runs']:
            obs = pd.read_csv(tables / f'cells_{name}.csv', dtype={'cluster': str})
            sizes = pd.read_csv(tables / f'sizes_{name}.csv', dtype={'cluster': str}).set_index('cluster')
            require(obs.groupby('cluster').size().sort_index().equals(sizes.n_cells.sort_index()), 'Cluster sizes disagree')
            require(np.isfinite(obs[['umap_1', 'umap_2']]).all().all(), 'Nonfinite UMAP')
            require((figures / f'umap_{name}.png').stat().st_size > 0, 'Missing UMAP')
        result.update(retained_cells=len(base), sampled_cells=n, independent_ari_comparisons=len(metrics),
                      scope='Numerical and file integrity checks; source support and biological interpretation require human review')
    save_json(run / 'verification.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(verify(args.run.resolve()))
