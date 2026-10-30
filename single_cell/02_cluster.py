"""Execute approved baseline, fixed-graph resolutions and full subsample rerun."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from workflow_common import (SEED, folders, load_counts, read_json, save_json, require,
                             validate_plan, validate_qc, qc_failures, resolution_name)


def plot_embedding(obs, labels, path, title):
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = pd.Series(np.asarray(labels, dtype=str), index=obs.index)
    for i, label in enumerate(sorted(labels.unique())):
        points = obs.loc[labels == label]
        ax.scatter(points.umap_1, points.umap_2, s=5, label=label, color=plt.get_cmap('tab20')(i % 20))
    ax.set(xlabel='UMAP 1', ylabel='UMAP 2', title=title)
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', markerscale=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def representation(counts, settings):
    a = counts.copy()
    sc.pp.filter_genes(a, min_cells=settings['min_cells_per_gene'])
    require((np.asarray(a.X.sum(axis=1)).ravel() > 0).all(),
            'Gene filtering left a zero-count cell; revise filtering in a new run')
    require(a.n_vars > settings['n_pcs'] and a.n_obs > settings['n_pcs'] + 1,
            'Too few cells/genes for approved PCs; revise settings in a new run')
    require(a.n_obs > settings['n_neighbors'], 'Too few cells for approved neighbor count')
    sc.pp.normalize_total(a, target_sum=settings['target_sum'])
    sc.pp.log1p(a)
    # Keep all gene-filtered log expression for markers; never test scaled/HVG-only data.
    a.raw = a
    sc.pp.highly_variable_genes(a, flavor='seurat', n_top_genes=min(settings['n_top_genes'], a.n_vars))
    a = a[:, a.var.highly_variable].copy()
    require(a.n_vars > settings['n_pcs'], 'Too few variable genes for approved PCs')
    sc.pp.scale(a, max_value=settings['scale_max'], zero_center=True)
    sc.tl.pca(a, n_comps=settings['n_pcs'], svd_solver='arpack', random_state=SEED, use_highly_variable=False)
    sc.pp.neighbors(a, n_neighbors=settings['n_neighbors'], n_pcs=settings['n_pcs'],
                    random_state=SEED, method='umap', metric='euclidean')
    sc.tl.umap(a, random_state=SEED, min_dist=.5, spread=1)
    return a


def marker_table(a, key):
    sizes = a.obs[key].value_counts()
    if len(sizes) < 2 or sizes.min() < 2:
        return pd.DataFrame(columns=['cluster', 'names', 'scores', 'logfoldchanges', 'pvals',
                                     'pvals_adj', 'pct_nz_group', 'pct_nz_reference']), 'Untestable: singleton or one cluster'
    sc.tl.rank_genes_groups(a, key, method='wilcoxon', use_raw=True, pts=True,
                           tie_correct=True, corr_method='benjamini-hochberg')
    result = sc.get.rank_genes_groups_df(a, group=None).rename(columns={'group': 'cluster'})
    return result, 'Exploratory cluster-versus-rest Wilcoxon; BH across genes within each contrast'


def save_clustering(a, key, name, run):
    tables, figures = folders(run)
    obs = a.obs[['n_genes_by_counts', 'total_counts', 'pct_counts_mt']].copy()
    obs['cluster'] = a.obs[key].astype(str)
    obs[['umap_1', 'umap_2']] = a.obsm['X_umap']
    obs.to_csv(tables / f'cells_{name}.csv', index_label='cell')
    markers, status = marker_table(a, key)
    markers.to_csv(tables / f'markers_{name}.csv', index=False)
    positive = markers[(markers.logfoldchanges > 0) & (markers.pvals_adj < .05)]
    positive.groupby('cluster', sort=False).head(20).to_csv(tables / f'top_markers_{name}.csv', index=False)
    obs.groupby('cluster').agg(n_cells=('cluster', 'size'), median_counts=('total_counts', 'median'),
                               median_genes=('n_genes_by_counts', 'median'), median_mt=('pct_counts_mt', 'median')).to_csv(tables / f'sizes_{name}.csv')
    plot_embedding(obs, obs.cluster, figures / f'umap_{name}.png', name + ' (clusters)')
    return status


def main(run):
    tables, figures = folders(run)
    settings = validate_plan(read_json(run / 'plan.json'))['settings']
    qc = validate_qc(read_json(run / 'qc.json'))
    counts = load_counts(read_json(run / 'config.json')['input_dir'])
    failures = qc_failures(counts.obs, qc)
    failures['retained'] = ~failures.any(axis=1)
    failures.to_csv(tables / 'qc_decisions.csv', index_label='cell')
    counts = counts[failures.retained].copy()
    require(counts.n_obs >= 30, 'Fewer than 30 retained cells; review QC before proceeding')
    save_json(run / 'filter_summary.json', {'input_cells': len(failures), 'retained_cells': counts.n_obs,
              'excluded_any': int((~failures.retained).sum()),
              'nonexclusive_filter_failures': {k: int(failures[k].sum()) for k in failures if k != 'retained'},
              'boundary_rule': 'Inclusive keep thresholds; failure counts overlap'})
    baseline = representation(counts, settings)
    graph = baseline.obsp['connectivities'].copy()
    status = {}
    for resolution in settings['resolutions']:
        key = resolution_name(resolution)
        sc.tl.leiden(baseline, resolution=resolution, key_added=key, random_state=SEED,
                     n_iterations=-1, directed=True, use_weights=True)
        require((baseline.obsp['connectivities'] != graph).nnz == 0, 'Resolution changed graph')
        status[key] = save_clustering(baseline, key, key, run)
    baseline.obs['cluster'] = baseline.obs[resolution_name(settings['baseline_resolution'])]
    baseline.write_h5ad(run / 'cache/baseline.h5ad')
    pd.DataFrame({'gene': baseline.var_names}).to_csv(tables / 'hvg_baseline.csv', index=False)
    pd.DataFrame({'pc': np.arange(1, settings['n_pcs'] + 1),
                  'variance_ratio': baseline.uns['pca']['variance_ratio']}).to_csv(tables / 'pca_variance.csv', index=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(np.arange(1, settings['n_pcs'] + 1), baseline.uns['pca']['variance_ratio'], marker='.')
    ax.set(xlabel='Principal component', ylabel='Explained variance ratio')
    fig.tight_layout()
    fig.savefig(figures / 'pca_variance.png', dpi=160)
    plt.close(fig)
    n = int(np.floor(counts.n_obs * settings['sample_fraction']))
    indices = np.sort(np.random.default_rng(SEED).choice(counts.n_obs, n, replace=False))
    sampled = representation(counts[indices], settings)
    sc.tl.leiden(sampled, resolution=settings['baseline_resolution'], key_added='cluster',
                 random_state=SEED, n_iterations=-1, directed=True, use_weights=True)
    status['downsample'] = save_clustering(sampled, 'cluster', 'downsample', run)
    sampled.write_h5ad(run / 'cache/downsample.h5ad')
    pd.DataFrame({'gene': sampled.var_names}).to_csv(tables / 'hvg_downsample.csv', index=False)
    save_json(run / 'computation.json', {'seed': SEED, 'settings': settings, 'qc': qc,
              'baseline': resolution_name(settings['baseline_resolution']), 'runs': list(status),
              'marker_status': status, 'resolution_graph_identical': True,
              'downsample_cells': n, 'sample_actual_fraction': n / counts.n_obs,
              'methods': 'log1p; seurat HVGs; centered clipped scale; arpack PCA; Euclidean UMAP neighbors; leidenalg; Wilcoxon markers on all filtered log genes'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    main(parser.parse_args().run.resolve())
