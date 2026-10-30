"""Apply explicit QC review and cluster using expression only. No tissue plots here."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from sklearn.metrics import adjusted_rand_score
from workflow_common import (SEED, read_json, save_json, counts, folders, integrity, seal,
                             log_step, validate_qc, qc_decisions, require, resolution_key,
                             cluster_colors, QC_COLUMNS)


def main(run, qc_path):
    integrity(run, 'qc')
    c, q = read_json(run / 'config.json'), validate_qc(read_json(qc_path))
    tables, figures = folders(run)
    a = counts(c)
    decisions = qc_decisions(a.obs, q)
    decisions.to_csv(tables / 'qc_decisions.csv', index_label='barcode')
    a = a[decisions.retained].copy()
    require(a.n_obs > max(c['n_pcs'] + 1, c['n_neighbors']), 'Too few retained spots; review QC/settings in a new run')
    sc.pp.filter_genes(a, min_cells=c['min_spots_per_gene'])
    require((np.asarray(a.X.sum(axis=1)).ravel() > 0).all(), 'Gene filtering produced zero-count spots')
    sc.pp.normalize_total(a, target_sum=c['target_sum'])
    sc.pp.log1p(a)
    sc.pp.highly_variable_genes(a, flavor='seurat', n_top_genes=min(c['n_hvgs'], a.n_vars))
    rank = a.var.loc[np.isfinite(a.var.dispersions_norm)].copy()
    rank['gene'] = rank.index
    rank = rank.sort_values(['dispersions_norm', 'gene'], ascending=[False, True], kind='mergesort')
    require(len(rank) >= c['n_candidates'], 'Too few finite-dispersion genes for fixed candidate count')
    hvgs = rank.index[:c['n_hvgs']]
    candidates = rank.index[:c['n_candidates']]
    require(len(hvgs) > c['n_pcs'], 'Too few HVGs for PCA')
    rank.loc[hvgs, ['gene', 'gene_ids', 'gene_symbol', 'means', 'dispersions_norm']].to_csv(tables / 'hvg_genes.csv', index=False)
    rank.loc[candidates, ['gene', 'gene_ids', 'gene_symbol', 'means', 'dispersions_norm']].to_csv(tables / 'candidate_genes.csv', index=False)
    # No spatial coordinates or image are attached to either expression object.
    expression = a[:, candidates].copy()
    b = a[:, hvgs].copy()
    sc.pp.scale(b, zero_center=True, max_value=c['scale_max'])
    sc.tl.pca(b, n_comps=c['n_pcs'], svd_solver='arpack', random_state=SEED, use_highly_variable=False)
    sc.pp.neighbors(b, n_neighbors=c['n_neighbors'], n_pcs=c['n_pcs'], random_state=SEED,
                    method='umap', metric='euclidean')
    sc.tl.umap(b, random_state=SEED, min_dist=.5, spread=1)
    obs = b.obs[QC_COLUMNS].copy()
    obs[['umap_1', 'umap_2']] = b.obsm['X_umap']
    sizes, overlaps, comparisons = [], [], []
    first = resolution_key(c['resolutions'][0])
    for r in c['resolutions']:
        key = resolution_key(r)
        sc.tl.leiden(b, resolution=r, key_added=key, random_state=SEED, n_iterations=-1,
                     directed=True, use_weights=True)
        obs[key] = b.obs[key].astype(str)
        size = obs.groupby(key).agg(n_spots=(key, 'size'), median_counts=('total_counts', 'median'),
                                   median_mt=('pct_counts_mt', 'median')).reset_index().rename(columns={key: 'cluster'})
        size['resolution'] = r
        sizes.append(size)
        fig, ax = plt.subplots(figsize=(8, 5))
        for label, color in cluster_colors(obs[key]).items():
            points = obs[obs[key] == label]
            ax.scatter(points.umap_1, points.umap_2, s=7, color=color, label=label)
        ax.set(xlabel='UMAP 1', ylabel='UMAP 2', title=f'Expression-only Leiden resolution {r:g}')
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
        fig.tight_layout()
        fig.savefig(figures / f'umap_{key}.png', dpi=160)
        plt.close(fig)
        comparisons.append({'reference': first, 'comparison': key, 'n_clusters': obs[key].nunique(),
                            'min_cluster_size': int(obs[key].value_counts().min()),
                            'ari': adjusted_rand_score(obs[first], obs[key])})
        cross = pd.crosstab(obs[first].rename('reference_cluster'), obs[key].rename('other_cluster'))
        cross = cross.stack().rename('n_spots').reset_index()
        cross['comparison'] = key
        overlaps.append(cross)
    obs.to_csv(tables / 'expression_clusters.csv', index_label='barcode')
    pd.concat(sizes).to_csv(tables / 'cluster_sizes.csv', index=False)
    pd.concat(overlaps).to_csv(tables / 'resolution_overlaps.csv', index=False)
    pd.DataFrame(comparisons).to_csv(tables / 'resolution_comparison.csv', index=False)
    pd.DataFrame({'pc': np.arange(1, c['n_pcs'] + 1),
                  'variance_ratio': b.uns['pca']['variance_ratio']}).to_csv(tables / 'pca_variance.csv', index=False)
    expression.write_h5ad(run / 'data/candidate_expression.h5ad')
    save_json(run / 'qc_review.json', q)
    save_json(run / 'filter_summary.json', {'input_spots': len(decisions), 'retained_spots': len(obs),
              'filter_failures_nonexclusive': {col: int(decisions[col].sum()) for col in decisions if col != 'retained'},
              'genes_after_filtering': a.n_vars, 'clustering_hvgs': len(hvgs), 'candidate_genes': len(candidates),
              'threshold_rule': 'Inclusive; out-of-tissue and zero-count spots excluded'})
    log_step(run, f'Python computed expression-only clustering; QC reviewer rationale: {q["rationale"]}\n'
             f'Settings: config.json, QC: qc_review.json; seed {SEED}; Seurat dispersion ranking with gene-name tie break; '
             'centered scaling clipped at scale_max; Euclidean expression neighbors; Leiden on fixed graph, UMAP display only. '
             'Candidate log expression is saved before scaling. No scientific-agent interpretation or retrieved biology. '
             'Check cluster sizes, PCA variance and resolution overlaps before freezing labels. '
             'Weakness to evaluate: parameter-sensitive partitions are not established anatomical domains.')
    seal(run, 'cluster')
    print(f'Expression clustering complete: {figures}\nReview before running the spatial stage.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--qc', required=True, type=Path)
    args = parser.parse_args()
    main(args.run.resolve(), args.qc)
