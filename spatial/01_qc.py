"""Create a recorded run and QC evidence, without filtering or clustering."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from workflow_common import (counts, positions, folders, save_json, seal, log_step,
                             tissue_axes, QC_COLUMNS)


def create_run(c, inputs, task):
    run = task / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    tables, figures = folders(run)
    for folder in (run / 'code', run / 'data', run / 'api', tables, figures):
        folder.mkdir(parents=True, exist_ok=False)
    for p in task.glob('*.py'):
        shutil.copy2(p, run / 'code' / p.name)
    if (task / 'requirements.txt').exists():
        shutil.copy2(task / 'requirements.txt', run / 'code/requirements.txt')
    (run / 'code/requirements.lock.txt').write_text(subprocess.check_output(
        [sys.executable, '-m', 'pip', 'freeze'], text=True))
    save_json(run / 'config.json', c)
    save_json(run / 'inputs.json', inputs)
    return run


def main(c, inputs, task, run=None):
    run = create_run(c, inputs, task) if run is None else run
    tables, figures = folders(run)
    a = counts(c)
    obs = a.obs[QC_COLUMNS + ['in_tissue']]
    obs.to_csv(tables / 'qc_spots.csv', index_label='barcode')
    tissue = obs[obs.in_tissue == 1]
    tissue[QC_COLUMNS].describe(percentiles=[.01, .05, .5, .9, .95, .99]).to_csv(tables / 'qc_quantiles.csv')
    save_json(run / 'qc_summary.json', {'matrix_spots': a.n_obs, 'in_tissue_spots': len(tissue),
              'genes': a.n_vars, 'mitochondrial_genes': int(a.var.mt.sum()),
              'zero_count_spots': int((obs.total_counts == 0).sum())})
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    for ax, col in zip(axes, QC_COLUMNS):
        ax.hist(tissue[col], bins=50)
        ax.set(xlabel=col, ylabel='In-tissue spots')
    fig.tight_layout()
    fig.savefig(figures / 'qc_distributions.png', dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    points = ax.scatter(tissue.total_counts, tissue.n_genes_by_counts, c=tissue.pct_counts_mt, s=6)
    ax.set(xlabel='Total counts', ylabel='Detected genes', xscale='symlog', yscale='symlog')
    fig.colorbar(points, ax=ax, label='Mitochondrial counts (%)')
    fig.tight_layout()
    fig.savefig(figures / 'qc_joint.png', dpi=160)
    plt.close(fig)
    p = positions(c).loc[tissue.index]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, col in zip(axes, QC_COLUMNS):
        circles = tissue_axes(ax, p, c)
        circles.set_array(tissue[col].to_numpy(dtype=float))
        circles.set_cmap('viridis')
        ax.set_title(col)
        fig.colorbar(circles, ax=ax, shrink=.6)
    fig.tight_layout()
    fig.savefig(figures / 'qc_tissue.png', dpi=160)
    plt.close(fig)
    log_step(run, 'Python computed QC metrics from supplied counts; these measurements are not model-generated. '
             'Codex developed the software. Sources/hashes/versions: inputs.json and code/requirements.lock.txt. '
             'No filtering yet; QC quantiles use in-tissue spots. Seed 42 is reserved for subsequent stochastic steps. '
             'Barcode matching, count validity and image-center bounds checked; visual alignment still needs human review. '
             'Weakness to examine: quality gradients can resemble biological regions.')
    seal(run, 'qc')
    return run


if __name__ == '__main__':
    raise SystemExit('Start QC with python spatial/run_analysis.py qc')
