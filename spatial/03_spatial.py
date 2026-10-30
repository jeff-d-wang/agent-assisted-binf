"""Freeze expression labels, map them, rank genes and run a label-permutation control."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import anndata as ad
from scipy import sparse, stats
from scipy.sparse.csgraph import connected_components
from workflow_common import (SEED, read_json, save_json, folders, integrity, seal, log_step,
                             positions, lattice_graph, agreement, randomized_agreement, moran,
                             require, resolution_key, cluster_colors, tissue_axes)


def gene_statistics(x, genes, labels, w, obs):
    groups = [np.flatnonzero(labels == k) for k in sorted(set(labels))]
    spatial_score = moran(x, w)
    records = []
    for j, gene in enumerate(genes):
        values = x[:, j]
        constant = np.ptp(values) == 0
        h = float(stats.kruskal(*(values[idx] for idx in groups)).statistic) if len(groups) > 1 and not constant else np.nan
        def correlation(other):
            return float(stats.spearmanr(values, other).statistic) if not constant and np.ptp(other) > 0 else np.nan
        records.append({'gene': gene, 'moran_i': spatial_score[j], 'kw_h': h,
                        'mean_log_expression': float(values.mean()), 'fraction_detected': float(np.mean(values > 0)),
                        'rho_counts': correlation(obs.total_counts.to_numpy()),
                        'rho_mt': correlation(obs.pct_counts_mt.to_numpy()),
                        'spatial_status': 'ranked' if np.isfinite(spatial_score[j]) else 'constant_on_connected_spots',
                        'de_status': 'ranked' if np.isfinite(h) else ('one_cluster' if len(groups) == 1 else 'constant')})
    result = pd.DataFrame(records)
    result['spatial_rank'] = result.moran_i.rank(ascending=False, method='average')
    result['de_rank'] = result.kw_h.rank(ascending=False, method='average')
    result['spatial_rank_fraction'] = result.spatial_rank / result.moran_i.notna().sum()
    result['de_rank_fraction'] = result.de_rank / max(1, result.kw_h.notna().sum())
    result['comparison'] = 'other_or_undefined'
    s, d = result.spatial_rank_fraction, result.de_rank_fraction
    result.loc[(s <= .25) & (d <= .25), 'comparison'] = 'strong_both'
    result.loc[(d <= .25) & (s > .5), 'comparison'] = 'strong_de_weak_spatial'
    result.loc[(s <= .25) & (d > .5), 'comparison'] = 'strong_spatial_weaker_de'
    return result


def main(run, resolution, reason):
    integrity(run, 'cluster')
    c = read_json(run / 'config.json')
    require(resolution in c['resolutions'], 'Choose a resolution already computed from expression')
    require(len(reason.strip()) >= 20, 'Record an expression-based clustering rationale (at least 20 characters)')
    tables, figures = folders(run)
    obs = pd.read_csv(tables / 'expression_clusters.csv', index_col='barcode',
                      dtype={resolution_key(r): str for r in c['resolutions']})
    key = resolution_key(resolution)
    labels = obs[key].to_numpy()
    # Save the choice before reading positions or producing any cluster tissue map.
    review = {'resolution': resolution, 'reason': reason,
              'selection_rule': 'Chosen using expression diagnostics before cluster tissue maps'}
    if (run / 'cluster_review.json').exists():
        require(read_json(run / 'cluster_review.json') == review,
                'Resolution already frozen, including after a partial failure; resume with the same resolution/reason')
    save_json(run / 'cluster_review.json', review)
    p = positions(c).loc[obs.index]
    edges, w = lattice_graph(p[['array_row', 'array_col']].to_numpy())
    observed, null, tail = randomized_agreement(labels, edges, c['n_randomizations'])
    degree = np.asarray(w.sum(axis=1)).ravel().astype(int)
    components, membership = connected_components(w, directed=False)
    p = p.copy()
    p['cluster'], p['degree'], p['component'] = labels, degree, membership
    p.to_csv(tables / 'spatial_spots.csv', index_label='barcode')
    pd.DataFrame({'source': obs.index[edges[:, 0]], 'target': obs.index[edges[:, 1]]}).to_csv(tables / 'physical_edges.csv', index=False)
    graph = {'definition': 'Original Visium lattice immediate neighbors: offsets (0,+/-2), (+/-1,+/-1)',
             'weights': 'Symmetric binary, no self edges, no row normalization; no bridging missing sites',
             'spots': len(obs), 'undirected_edges': len(edges), 'isolated_spots': int((degree == 0).sum()),
             'connected_components': int(components), 'min_degree': int(degree.min()), 'max_degree': int(degree.max()),
             'moran_spots': int((degree > 0).sum()),
             'isolate_policy': 'Moran excludes isolates before centering; DE includes all retained spots. Label permutations include all retained spots.'}
    save_json(run / 'graph_summary.json', graph)
    counts = pd.Series(labels).value_counts().to_numpy()
    expected = float(np.sum(counts * (counts - 1)) / (len(labels) * (len(labels) - 1)))
    result = {'statistic': 'Fraction of undirected physical edges whose endpoints have identical cluster labels',
              'observed': observed, 'null_mean': float(null.mean()), 'null_sd': float(null.std(ddof=1)),
              'null_q025': float(np.quantile(null, .025)), 'null_q975': float(np.quantile(null, .975)),
              'analytic_random_label_expectation': expected, 'excess_over_null_mean': float(observed - null.mean()),
              'empirical_upper_tail': tail, 'n_null_ge_observed': int(np.count_nonzero(null >= observed)),
              'n_randomizations': len(null), 'seed': SEED, 'n_clusters': len(counts),
              'limitation': 'Global label exchangeability can be broken by spatial QC artifacts. One section; no anatomical identity or individual-gene significance established.'}
    save_json(run / 'spatial_summary.json', result)
    pd.DataFrame({'iteration': np.arange(1, len(null) + 1), 'edge_agreement': null}).to_csv(tables / 'null_distribution.csv', index=False)
    pd.DataFrame([{'analysis': 'Same-cluster edge fraction', 'original': observed,
                   'randomized_control_mean': null.mean(), 'null_q025': result['null_q025'],
                   'null_q975': result['null_q975'], 'empirical_upper_tail': tail,
                   'randomizations': len(null)}]).to_csv(tables / 'original_vs_randomized.csv', index=False)
    pd.DataFrame([{'resolution': r, 'n_clusters': obs[resolution_key(r)].nunique(),
                   'edge_agreement': agreement(obs[resolution_key(r)], edges),
                   'primary': r == resolution} for r in c['resolutions']]).to_csv(tables / 'spatial_resolution_sensitivity.csv', index=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(null, bins=min(40, len(np.unique(null))), color='steelblue', label='Shuffled labels')
    ax.axvline(observed, color='crimson', lw=2, label=f'Observed {observed:.4f}')
    ax.set(xlabel='Fraction of same-cluster physical edges', ylabel='Randomizations',
           title=f'Fixed graph; cluster sizes preserved; upper-tail proportion {tail:.4g}')
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures / 'randomized_control.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    colors = cluster_colors(labels)
    for label, color in colors.items():
        points = obs[obs[key] == label]
        axes[0].scatter(points.umap_1, points.umap_2, color=color, s=7, label=label)
    axes[0].set(xlabel='UMAP 1', ylabel='UMAP 2', title='Expression-only clusters')
    circles = tissue_axes(axes[1], p, c)
    circles.set_facecolors([colors[v] for v in labels])
    axes[1].set_title(f'Identical labels on tissue; resolution {resolution:g}')
    axes[0].legend(loc='best', fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / 'clusters_umap_and_tissue.png', dpi=160)
    plt.close(fig)
    expression = ad.read_h5ad(run / 'data/candidate_expression.h5ad')
    require(expression.obs_names.equals(obs.index), 'Candidate expression/barcode order differs')
    x = expression.X.toarray() if sparse.issparse(expression.X) else np.asarray(expression.X)
    genes = gene_statistics(x, expression.var_names, labels, w, obs)
    genes.to_csv(tables / 'gene_rankings.csv', index=False)
    means = pd.DataFrame(x, index=obs.index, columns=expression.var_names).groupby(labels).mean()
    means.to_csv(tables / 'gene_cluster_means.csv', index_label='cluster')
    examples = []
    for category in ('strong_both', 'strong_de_weak_spatial', 'strong_spatial_weaker_de'):
        subset = genes[genes.comparison == category].sort_values('de_rank' if category == 'strong_de_weak_spatial' else 'spatial_rank')
        if subset.empty:
            examples.append({'category': category, 'gene': '', 'status': 'No candidate meets the prespecified rank thresholds'})
        else:
            examples.append({'category': category, 'gene': subset.iloc[0].gene, 'status': 'Descriptive example; not a significance claim'})
    pd.DataFrame(examples).to_csv(tables / 'ranking_examples.csv', index=False)
    finite = genes.dropna(subset=['moran_i']).sort_values(['spatial_rank', 'gene'])
    require(len(finite) >= 2, 'Fewer than two spatially rankable candidates; review inputs/settings')
    selected = list(dict.fromkeys(list(finite.head(2).gene) + list(finite.tail(1).gene) + [e['gene'] for e in examples if e['gene']]))
    pd.DataFrame({'gene': selected}).to_csv(tables / 'mapped_genes.csv', index=False)
    rows = (len(selected) + 2) // 3
    fig, axes = plt.subplots(rows, 3, figsize=(15, 5 * rows), squeeze=False)
    for ax in axes.flat:
        ax.set_axis_off()
    for ax, gene in zip(axes.flat, selected):
        j = expression.var_names.get_loc(gene)
        circles = tissue_axes(ax, p, c)
        circles.set_array(x[:, j].astype(float))
        circles.set_cmap('viridis')
        score = genes.set_index('gene').loc[gene]
        ax.set_title(f'{gene}: Moran I={score.moran_i:.3f}, rank={score.spatial_rank:g}')
        fig.colorbar(circles, ax=ax, shrink=.6, label='Log1p normalized expression')
    fig.tight_layout()
    fig.savefig(figures / 'gene_tissue_maps.png', dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(genes.de_rank, genes.spatial_rank, s=18, alpha=.6)
    for gene in selected:
        row = genes.set_index('gene').loc[gene]
        if np.isfinite(row.de_rank):
            ax.annotate(gene, (row.de_rank, row.spatial_rank), fontsize=8)
    ax.set(xlabel='Omnibus cluster-DE rank (Kruskal–Wallis H; 1=highest)',
           ylabel='Spatial rank (Moran I; 1=highest)', title='Same expression-selected candidate genes')
    ax.invert_xaxis()
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(figures / 'de_vs_spatial_ranks.png', dpi=160)
    plt.close(fig)
    save_json(run / 'gene_methods.json', {
        'candidates': len(genes), 'selection': 'Top expression-only Seurat normalized dispersions; gene-name tie break; frozen before spatial analysis',
        'expression': 'Library normalization after gene filtering, log1p; not scaled expression',
        'moran': 'I = N/S0 * sum_ij(w_ij (x_i-mean)(x_j-mean)) / sum_i((x_i-mean)^2); binary weights, isolates excluded',
        'de': 'Tie-corrected Kruskal–Wallis H across frozen clusters; all retained spots. No inferential p-values because clusters were expression-derived.',
        'examples': 'Strong = top quartile of defined ranks; weaker = below median. Average ranks for ties; missing categories retained.',
        'gene_inference': 'Descriptive ranking only; label-permutation control does not test individual genes',
        'confound_checks': 'Per-gene Spearman correlations with raw library size and mitochondrial fraction; QC tissue maps',
        'de_caveat': 'Small clusters and expression-derived group selection limit inference; no claim of independent DE confirmation'})
    (run / 'EVIDENCE.md').write_text(f'''# Task 3 computed evidence — interpretation pending

Python computed these results from local inputs; no language model supplied a scientific interpretation.
Settings and QC: config.json, qc_review.json, cluster_review.json, filter_summary.json.
Input hashes and package versions: inputs.json; complete environment: code/requirements.lock.txt.

- Retained spots: {len(obs)}; primary resolution: {resolution:g}; clusters: {len(counts)}.
- Physical edges: {len(edges)}; isolated spots: {graph['isolated_spots']}; components: {components}.
- Same-cluster edge fraction: {observed:.6f}; null mean: {null.mean():.6f}.
- Empirical upper-tail proportion: {tail:.6g} from {len(null)} seed-42 label permutations.
- Candidate genes: {len(genes)}; rankings are descriptive, with undefined results retained.

Figures: {figures}
Tables: {tables}

## Scientific review still required
Explain the statistic and effect size, inspect quality gradients and alignment, compare ranking examples
(including missing categories), and assess resolution sensitivity without selecting a new primary result
for its spatial score. Separate data observations, agent inferences, and external biological support.
Do not assign anatomical or cell-type labels without evidence. Global label shuffling does not rule out
technical spatial artifacts; this is one section, and spots can mix cell types. Gene ranks are not gene tests.
Run the independent verifier; record an actual scientific-agent weakness and how it was evaluated.
''')
    log_step(run, f'Python computed spatial statistics and plots, with no retrieved biological evidence or model interpretation. '
             f'Frozen resolution {resolution:g}; reviewer rationale: {reason}. '
             f'{len(null)} permutations, seed {SEED}; observed {observed:.6g}, empirical upper-tail {tail:.6g}. '
             'Methods/settings and denominators: graph_summary.json, spatial_summary.json, gene_methods.json. '
             'Checks: gene/barcode alignment and image bounds passed; independent numerical verification is next. '
             'Weaknesses retained: missing rank-example categories, undefined gene statistics, spatial QC confounding, and descriptive DE circularity.')
    seal(run, 'spatial')
    print(f'Spatial computation complete. Run verify next.\nEvidence: {run / "EVIDENCE.md"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--resolution', type=float, required=True)
    parser.add_argument('--reason', required=True)
    args = parser.parse_args()
    main(args.run.resolve(), args.resolution, args.reason)
