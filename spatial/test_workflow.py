"""Synthetic tests only. Never reads the course dataset or calls a language model."""
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_analysis  # Configure single-thread numerical libraries and writable caches first.
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse, stats
from workflow_common import (lattice_graph, agreement, randomized_agreement, moran, positions,
                             validate_qc, validate_config, read_json, save_json, integrity, folders)

HERE = Path(__file__).resolve().parent


def module(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), HERE / name)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def fixture(root):
    """Create a tiny 10x-formatted matrix and visibly synthetic hexagonal tissue image."""
    source = root / 'inputs'
    (source / 'spatial').mkdir(parents=True)
    rng = np.random.default_rng(42)
    coords = np.array([(r, 2 * col + r % 2) for r in range(12) for col in range(12)])
    barcodes = [f'SYNTHETIC_{i:03d}-1' for i in range(len(coords))]
    n_genes = 400
    rates = np.full((len(coords), n_genes), 1.5)
    rates[coords[:, 1] < 12, :80] = 8
    rates[coords[:, 1] >= 12, 80:160] = 8
    matrix = sparse.csc_matrix(rng.poisson(rates).astype(np.int32).T)
    symbols = ['mt-Synthetic'] + [f'Gene_{i:03d}' for i in range(1, n_genes)]
    with h5py.File(source / 'synthetic.h5', 'w') as f:
        g = f.create_group('matrix')
        for name in ('data', 'indices', 'indptr'):
            g[name] = getattr(matrix, name)
        g['shape'] = matrix.shape
        g['barcodes'] = np.array(barcodes, dtype='S')
        feature = g.create_group('features')
        feature['name'] = np.array(symbols, dtype='S')
        feature['id'] = np.array([f'ID{i}' for i in range(n_genes)], dtype='S')
        feature['feature_type'] = np.array(['Gene Expression'] * n_genes, dtype='S')
        feature['genome'] = np.array(['synthetic'] * n_genes, dtype='S')
        feature['_all_tag_keys'] = np.array(['genome'], dtype='S')
    p = pd.DataFrame({'barcode': barcodes, 'in_tissue': 1, 'array_row': coords[:, 0],
                      'array_col': coords[:, 1], 'pxl_row_in_fullres': 20 + coords[:, 0] * 12,
                      'pxl_col_in_fullres': 20 + coords[:, 1] * 7})
    # Permute rows to catch accidental positional matching instead of barcode joins.
    p.sample(frac=1, random_state=42).to_csv(source / 'spatial/tissue_positions_list.csv', index=False, header=False)
    image = np.ones((200, 200, 3)) * .9
    image[10:180, 10:185] = [.85, .72, .78]
    plt.imsave(source / 'spatial/tissue_hires_image.png', image)
    save_json(source / 'spatial/scalefactors_json.json', {'tissue_hires_scalef': 1, 'spot_diameter_fullres': 10})
    c = read_json(HERE / 'config.json')
    c.update(input_dir=str(source), counts_file='synthetic.h5', n_candidates=100,
             n_hvgs=200, n_pcs=8, n_neighbors=8, n_randomizations=100)
    return c


class StatisticsTests(unittest.TestCase):
    def test_hand_checked_hex_graph_and_missing_site(self):
        # Triangle plus one isolate. A missing intermediate spot must not be bridged.
        coords = [[0, 0], [0, 2], [1, 1], [0, 6]]
        edges, w = lattice_graph(coords)
        self.assertEqual(set(map(tuple, edges)), {(0, 1), (0, 2), (1, 2)})
        self.assertEqual((w != w.T).nnz, 0)
        self.assertEqual(w.diagonal().sum(), 0)
        self.assertAlmostEqual(agreement(['a', 'a', 'b', 'b'], edges), 1 / 3)
        # On a complete three-vertex graph, any nonconstant centered feature has I=-1/2.
        np.testing.assert_allclose(moran([1, 2, 3, 999], w), [-.5])
        self.assertTrue(np.isnan(moran([1, 1, 1, 999], w)[0]))
        with self.assertRaises(ValueError):
            lattice_graph([[0, 0], [0, 0]])
        with self.assertRaises(ValueError):
            lattice_graph([[0, 1]])

    def test_fixed_size_null_and_ties(self):
        edges, _ = lattice_graph([[0, 0], [0, 2], [0, 4], [0, 6]])
        labels = np.array(['a', 'a', 'b', 'b'])
        possibilities = set(itertools.permutations(labels))
        self.assertAlmostEqual(np.mean([agreement(x, edges) for x in possibilities]), 1 / 3)
        a, null, tail = randomized_agreement(labels, edges, 999)
        _, again, _ = randomized_agreement(labels, edges, 999)
        np.testing.assert_array_equal(null, again)
        self.assertEqual(tail, (1 + np.count_nonzero(null >= a)) / 1000)
        _, _, tail = randomized_agreement(['a'] * 4, edges, 100)
        self.assertEqual(tail, 1)
        with self.assertRaises(ValueError):
            agreement(labels, np.empty((0, 2), dtype=int))

    def test_kw_independent_tie_correction(self):
        values = np.array([0, 0, 1, 1, 2, 2, 3, 5], dtype=float)
        labels = np.array(['a'] * 4 + ['b'] * 4)
        h = module('04_verify.py').independent_h(values, labels)
        self.assertAlmostEqual(h, stats.kruskal(values[:4], values[4:]).statistic)

    def test_invalid_reviews_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_qc(read_json(HERE / 'qc_review.template.json'))
        c = read_json(HERE / 'config.json')
        c['n_randomizations'] = 99
        with self.assertRaises(ValueError):
            validate_config(c)

    def test_one_cluster_and_constant_genes_are_not_claimed(self):
        step = module('03_spatial.py')
        _, w = lattice_graph([[0, 0], [0, 2], [0, 4]])
        x = np.array([[1, 0], [1, 1], [1, 2]])
        obs = pd.DataFrame({'total_counts': [10, 20, 30], 'pct_counts_mt': [1, 1, 2]})
        scores = step.gene_statistics(x, ['constant', 'gradient'], np.array(['a'] * 3), w, obs)
        self.assertTrue(scores.kw_h.isna().all())
        self.assertTrue(np.isnan(scores.iloc[0].moran_i))
        self.assertTrue((scores.comparison == 'other_or_undefined').all())


class WorkflowTests(unittest.TestCase):
    def test_complete_synthetic_workflow_and_integrity(self):
        with tempfile.TemporaryDirectory(prefix='task3-test-') as tmp:
            root = Path(tmp)
            c = fixture(root)
            # Both supported position formats preserve barcode identity after shuffled rows.
            p = positions(c)
            old = Path(c['input_dir']) / 'spatial/tissue_positions_list.csv'
            new = old.with_name('tissue_positions.csv')
            p.reset_index().to_csv(new, index=False)
            old.unlink()
            pd.testing.assert_frame_equal(p, positions(c))
            task = root / 'spatial'
            task.mkdir()
            for source in HERE.glob('*.py'):
                shutil.copy2(source, task / source.name)
            shutil.copy2(HERE / 'requirements.txt', task / 'requirements.txt')
            inputs = run_analysis.preflight(c)
            run = module('01_qc.py').main(c, inputs, task)
            tables, figures = folders(run)
            self.assertEqual(read_json(run / 'state.json')['stage'], 'qc')
            q = {'rationale': 'Synthetic test: retain all positive-count generated spots.', 'min_genes': 1,
                 'max_genes': 10000, 'min_counts': 1, 'max_counts': 1000000, 'max_pct_mt': 100}
            review = root / 'qc.json'
            save_json(review, q)
            def command(*args):
                result = subprocess.run([sys.executable, str(HERE / 'run_analysis.py'), *map(str, args)],
                                        capture_output=True, text=True, timeout=180)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            command('cluster', run, '--qc', review)
            self.assertFalse((figures / 'clusters_umap_and_tissue.png').exists())
            self.assertEqual(len(pd.read_csv(tables / 'candidate_genes.csv')), 100)
            reason = 'Synthetic integration test freezes the planned baseline.'
            # Simulate a failed spatial stage that already froze its resolution.
            save_json(run / 'cluster_review.json', {'resolution': .5, 'reason': reason,
                      'selection_rule': 'Chosen using expression diagnostics before cluster tissue maps'})
            with self.assertRaisesRegex(ValueError, 'Resolution already frozen'):
                module('03_spatial.py').main(run, .8, reason)
            command('spatial', run, '--resolution', '.5', '--reason', reason)
            command('verify', run)
            report = read_json(run / 'verification.json')
            self.assertTrue(report['passed'])
            self.assertEqual(report['gene_statistics_checked'], 100)
            with self.assertRaisesRegex(ValueError, 'Expected completed stage'):
                module('02_cluster.py').main(run, review)
            # Preserve a preview outside TemporaryDirectory only when explicitly requested.
            import os
            preview = os.environ.get('TASK3_TEST_PREVIEW')
            if preview:
                Path(preview).mkdir(parents=True, exist_ok=True)
                for f in figures.glob('*.png'):
                    shutil.copy2(f, Path(preview) / f.name)
            with (tables / 'gene_rankings.csv').open('a') as f:
                f.write('\n# tampered\n')
            with self.assertRaisesRegex(ValueError, 'Input/evidence changed'):
                integrity(run)

    def test_duplicate_and_missing_barcodes_rejected(self):
        with tempfile.TemporaryDirectory(prefix='task3-input-test-') as tmp:
            c = fixture(Path(tmp))
            path = Path(c['input_dir']) / 'spatial/tissue_positions_list.csv'
            p = pd.read_csv(path, header=None)
            original = p.copy()
            p.iloc[0, 0] = p.iloc[1, 0]
            p.to_csv(path, index=False, header=False)
            with self.assertRaisesRegex(ValueError, 'duplicate spatial barcodes'):
                positions(c)
            original.iloc[1:].to_csv(path, index=False, header=False)
            from workflow_common import counts
            with self.assertRaisesRegex(ValueError, 'barcodes missing'):
                counts(c)


class AgentTests(unittest.TestCase):
    def test_full_synthetic_agent_review_workflow(self):
        import agent_workflow as workflow
        with tempfile.TemporaryDirectory(prefix='task3-agent-test-') as tmp:
            root = Path(tmp)
            c = fixture(root)
            task = root / 'spatial'
            task.mkdir()
            for p in HERE.glob('*.py'):
                shutil.copy2(p, task / p.name)
            shutil.copy2(HERE / 'requirements.txt', task / 'requirements.txt')
            run = workflow.start(c, run_analysis.preflight(c), task)
            reason = 'Synthetic fixture retains all positive-count spots for software tests.'
            replies = [({'rationale': 'Synthetic plan fixture, not a scientific-agent finding.'}, []),
                       ({'rationale': reason, 'min_genes': 1, 'max_genes': 10000, 'min_counts': 1,
                         'max_counts': 1000000, 'max_pct_mt': 100}, []),
                       ({'resolution': .5, 'reason': 'Synthetic expression-based resolution choice fixture.'}, []),
                       ({'report_md': 'Synthetic report fixture. No scientific conclusion or real model answer.', 'pmids': []}, [])]
            with patch('agent_workflow.ask', side_effect=replies) as ask, patch('builtins.input', return_value='quit'):
                workflow.interact(run)
                self.assertEqual(ask.call_count, 1)
                self.assertEqual(read_json(run / 'state.json')['stage'], 'plan')
                self.assertFalse((folders(run)[0] / 'qc_spots.csv').exists())
                answers = ['approve', 'approve', 'approve', 'accept', 'Fixture reviewer',
                           'Fixture numerical verification passed', 'Fixture limitation checked', 'Synthetic data only']
                with patch('builtins.input', side_effect=answers):
                    workflow.interact(run)
                self.assertEqual(ask.call_count, 4)  # Resuming does not repay for the plan.
                cluster_prompt = ask.call_args_list[2].args[3]
                self.assertNotIn('spatial_summary.json', cluster_prompt)
                self.assertTrue(all(name.startswith('umap_') for name in ask.call_args_list[2].args[4]))
            self.assertEqual(read_json(run / 'agent_state.json')['stage'], 'accepted')
            self.assertTrue(read_json(run / 'verification.json')['passed'])
            for name in ('RESULTS.md', 'REVIEW.md', 'REVIEW_PACKET.md', 'PLAN.md', 'QC.md', 'CLUSTER_REVIEW.md'):
                self.assertTrue((run / name).is_file())
            integrity(run)

    def test_transport_truncation_and_saved_response(self):
        import agent
        with tempfile.TemporaryDirectory(prefix='task3-transport-test-') as tmp:
            run = Path(tmp) / 'spatial/runs/fixture'
            (run / 'api').mkdir(parents=True)
            config = {'model': 'claude-sonnet-5-5'}
            truncated = {'model': config['model'], 'stop_reason': 'max_tokens', 'content': [{'type': 'text', 'text': 'partial'}]}
            complete = {'model': config['model'], 'stop_reason': 'end_turn',
                        'content': [{'type': 'text', 'text': '{"rationale": "Complete synthetic plan fixture"}'}]}
            with patch('agent.call_claude', side_effect=[truncated, complete]) as api:
                with self.assertRaisesRegex(ValueError, 'output limit'):
                    agent.ask(run, config, {'messages': []}, 'fixture', job='plan')
                value, _ = agent.ask(run, config, {'messages': []}, 'fixture', job='plan')
                replay, _ = agent.ask(run, config, {'messages': []}, 'fixture', job='plan')
                self.assertEqual(value, replay)
                self.assertEqual(api.call_count, 2)
                self.assertTrue(all(call.args[0]['max_tokens'] == 32000 for call in api.call_args_list))
                self.assertNotIn('partial', json.dumps(api.call_args.args[0]['messages']))

    def test_report_requires_retrieved_sources(self):
        import agent_workflow as workflow
        with tempfile.TemporaryDirectory(prefix='task3-source-test-') as tmp:
            run = Path(tmp)
            (run / 'data').mkdir()
            with self.assertRaisesRegex(ValueError, 'unretrieved'):
                workflow.validate_response(run, 'report', {'report_md': 'An unsupported report fixture.', 'pmids': ['12345']})


if __name__ == '__main__':
    unittest.main()
