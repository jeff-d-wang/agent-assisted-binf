"""Compute QC evidence only, before Claude selects thresholds."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from workflow_common import folders, load_counts, read_json, save_json


def main(run):
    tables, figures = folders(run)
    adata = load_counts(read_json(run / 'config.json')['input_dir'])
    columns = ['n_genes_by_counts', 'total_counts', 'pct_counts_mt']
    adata.obs[columns].to_csv(tables / 'qc_cells.csv', index_label='cell')
    adata.obs[columns].describe(percentiles=[.01, .05, .5, .9, .95, .99]).to_csv(tables / 'qc_quantiles.csv')
    save_json(run / 'qc_summary.json', {'cells': adata.n_obs, 'genes': adata.n_vars,
                                      'mitochondrial_genes': int(adata.var.mt.sum())})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    for ax, column in zip(axes, columns):
        ax.hist(adata.obs[column], bins=60)
        ax.set(xlabel=column, ylabel='Cells')
    fig.tight_layout()
    fig.savefig(figures / 'qc_distributions.png', dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    points = ax.scatter(adata.obs.total_counts, adata.obs.n_genes_by_counts,
                        c=adata.obs.pct_counts_mt, s=4, cmap='viridis')
    ax.set(xscale='log', yscale='log', xlabel='Total counts', ylabel='Detected genes')
    fig.colorbar(points, ax=ax, label='Mitochondrial counts (%)')
    fig.tight_layout()
    fig.savefig(figures / 'qc_joint.png', dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    main(parser.parse_args().run.resolve())
