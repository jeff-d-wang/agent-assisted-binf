"""Compute cluster overlaps and, when available, Claude-label agreement."""
import argparse
import importlib.util
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from workflow_common import folders, read_json, require


def cells(tables, name):
    result = pd.read_csv(tables / f'cells_{name}.csv', dtype={'cell': str, 'cluster': str}).set_index('cell')
    require(result.index.is_unique and result.cluster.notna().all(), 'Invalid cell assignments')
    return result


def align(base, other):
    require(other.index.isin(base.index).all() and other.index.is_unique, 'Foreign or duplicate comparison cells')
    return base.loc[other.index, 'cluster'], other.cluster


def compare(run):
    tables, figures = folders(run)
    meta = read_json(run / 'computation.json')
    base = cells(tables, meta['baseline'])
    metrics, overlaps = [], []
    for name in meta['runs']:
        if name == meta['baseline']:
            continue
        other = cells(tables, name)
        if name != 'downsample':
            require(set(base.index) == set(other.index), 'Resolution comparisons must use all baseline cells')
        left, right = align(base, other)
        cross = pd.crosstab(left, right)
        for a in cross.index:
            for b in cross.columns:
                n = int(cross.loc[a, b])
                if n:
                    overlaps.append(dict(comparison=name, baseline_cluster=a, other_cluster=b, n_cells=n,
                                         fraction_of_baseline=n / int(cross.loc[a].sum()),
                                         fraction_of_other=n / int(cross[b].sum())))
        metrics.append(dict(comparison=name, n_shared=len(other), baseline_clusters=left.nunique(),
                            other_clusters=right.nunique(), ari=adjusted_rand_score(left, right),
                            nmi=normalized_mutual_info_score(left, right, average_method='arithmetic')))
        fig, ax = plt.subplots(figsize=(7, 5))
        im = ax.imshow(cross.div(cross.sum(axis=1), axis=0), vmin=0, vmax=1, aspect='auto')
        ax.set(xticks=range(len(cross.columns)), xticklabels=cross.columns,
               yticks=range(len(cross.index)), yticklabels=cross.index,
               xlabel=name + ' cluster', ylabel='Baseline cluster', title='Fraction of baseline cluster (shared cells)')
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(figures / f'overlap_{name}.png', dpi=160)
        plt.close(fig)
    pd.DataFrame(metrics).to_csv(tables / 'robustness_metrics.csv', index=False)
    pd.DataFrame(overlaps).to_csv(tables / 'cluster_overlaps.csv', index=False)


def render_annotations(run):
    tables, figures = folders(run)
    meta = read_json(run / 'computation.json')
    annotations = read_json(run / 'interpretation.json')['annotations']
    rows = [dict(row, markers='; '.join(row['markers']), pmids='; '.join(row['pmids'])) for row in annotations]
    pd.DataFrame(rows).to_csv(tables / 'annotations.csv', index=False)
    spec = importlib.util.spec_from_file_location('cluster', Path(__file__).with_name('02_cluster.py'))
    cluster = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cluster)
    indexed = {(r['run'], r['cluster']): r for r in annotations}
    all_cells = {}
    for name in meta['runs']:
        obs = cells(tables, name)
        obs['label'] = [indexed[name, c]['label'] for c in obs.cluster]
        obs['confidence'] = [indexed[name, c]['confidence'] for c in obs.cluster]
        obs.to_csv(tables / f'annotated_cells_{name}.csv', index_label='cell')
        display_labels = obs.label + obs.confidence.map({'supported': '', 'tentative': ' (tentative)', 'uncertain': ' (uncertain)'})
        cluster.plot_embedding(obs, display_labels, figures / f'annotated_umap_{name}.png', name + ' (Claude annotations)')
        all_cells[name] = obs
    base = all_cells[meta['baseline']]
    summary = []
    for label, group in base.groupby('label'):
        members = [indexed[meta['baseline'], c] for c in group.cluster.unique()]
        row = dict(population=label, n_cells=len(group),
                   main_markers='; '.join(sorted({g for m in members for g in m['markers']})),
                   notes=' | '.join(m['notes'] for m in members))
        for name in meta['runs']:
            if name == meta['baseline']:
                continue
            other = all_cells[name]
            common = group.index.intersection(other.index)
            row[name + '_shared_cells'] = len(common)
            # Uncertain labels matching each other are not evidence of biological stability.
            resolved = (base.loc[common, 'confidence'] != 'uncertain') & (other.loc[common, 'confidence'] != 'uncertain')
            agrees = (other.loc[common, 'label'] == label) & resolved
            row[name + '_supported_label_agreement'] = float(agrees.mean()) if len(common) else np.nan
            row[name + '_unresolved_fraction'] = float((~resolved).mean()) if len(common) else np.nan
        summary.append(row)
    pd.DataFrame(summary).to_csv(tables / 'population_stability.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--annotations', action='store_true')
    args = parser.parse_args()
    if args.annotations:
        render_annotations(args.run.resolve())
    else:
        compare(args.run.resolve())
