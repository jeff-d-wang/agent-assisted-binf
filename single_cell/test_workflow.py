"""No-key tests; all scientific calculations use a synthetic 10x matrix."""
import copy
import importlib.metadata
import json
import os
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.io import mmwrite
import agent
import run_analysis as workflow
from workflow_common import (SEED, PACKAGES, digest, folders, read_json, save_json,
                             validate_plan, validate_qc)

PLAN = {'rationale': 'Synthetic test settings, not a proposed PBMC3k analysis.', 'settings': {
    'target_sum': 10000, 'n_top_genes': 150, 'n_pcs': 5, 'n_neighbors': 8,
    'baseline_resolution': .6, 'resolutions': [.3, .6, 1.0], 'sample_fraction': .7,
    'min_cells_per_gene': 2, 'scale_max': 10}}
QC = dict(rationale='Synthetic QC excludes the deliberately high-mitochondrial cell.',
          min_genes=0, max_genes=1000, min_counts=0, max_counts=1000000, max_pct_mt=60)


def fixture(root):
    source = root / 'input'
    source.mkdir()
    rng = np.random.default_rng(SEED)
    x = rng.poisson(.4, (180, 300))
    for i in range(3):
        x[i * 60:(i + 1) * 60, 1 + i * 30:31 + i * 30] += rng.poisson(5, (60, 30))
    x[0, 0] = 10000
    mmwrite(source / 'matrix.mtx', sparse.coo_matrix(x.T))
    (source / 'genes.tsv').write_text(''.join(f'ENSG{i}\t' + ('MT-TEST' if i == 0 else f'GENE{i}') + '\n' for i in range(300)))
    (source / 'barcodes.tsv').write_text(''.join(f'cell{i:03}\n' for i in range(180)))
    c = dict(input_dir=str(source), model='claude-test', question='Synthetic software check only')
    checks = {'sha256': {str(p): digest(p) for p in source.iterdir()},
              'versions': {p: importlib.metadata.version(p) for p in PACKAGES}, 'seed': SEED}
    return workflow.create_run(c, checks, root / 'task')


def fake_report(run):
    tables, _ = folders(run)
    meta = read_json(run / 'computation.json')
    annotations = []
    for name in meta['runs']:
        obs = pd.read_csv(tables / f'cells_{name}.csv', dtype={'cluster': str})
        for c in obs.cluster.unique():
            annotations.append(dict(run=name, cluster=c, label='Unresolved synthetic population',
                                    confidence='uncertain', markers=[], pmids=[], notes='Synthetic mock, no biological interpretation'))
    obs = pd.read_csv(tables / f"cells_{meta['baseline']}.csv", dtype={'cluster': str})
    groups = list(obs.cluster.unique())
    evidence = agent.inspect_population(run, meta['baseline'], groups[0], groups[1] if len(groups) > 1 else '', ['GENE1', 'GENE35', 'missing'])
    return {'annotations': annotations,
            'ambiguity': {'investigation': evidence['evidence_prefix'], 'discussion': 'Synthetic contrast only; unsupported labels remain uncertain.'},
            'report_md': '# Synthetic software test\n\nThis mock response is not a Claude analysis or a biological result. All populations remain unresolved. Human scientific review is still required.'}


class WorkflowTests(unittest.TestCase):
    def test_settings_reject_unsupported_and_invalid(self):
        validate_plan(PLAN)
        validate_qc(QC)
        for key, value in [('resolutions', [.3, .6]), ('sample_fraction', .5), ('n_pcs', True), ('target_sum', float('nan'))]:
            bad = copy.deepcopy(PLAN)
            bad['settings'][key] = value
            with self.assertRaises(ValueError):
                validate_plan(bad)
        bad = dict(QC, max_counts=-1)
        with self.assertRaises(ValueError):
            validate_qc(bad)

    def test_alignment_and_ari_with_renamed_reordered_clusters(self):
        compare, verify = workflow.module('03_compare.py'), workflow.module('04_verify.py')
        base = pd.DataFrame({'cluster': ['a', 'a', 'b', 'b']}, index=['x', 'y', 'z', 'w'])
        other = pd.DataFrame({'cluster': ['9', '8', '9', '8']}, index=['w', 'y', 'z', 'x'])
        left, right = compare.align(base, other)
        self.assertEqual(verify.independent_ari(left, right), 1)
        self.assertAlmostEqual(verify.independent_ari(['a', 'a', 'b', 'b'], ['x', 'y', 'x', 'y']), -.5)
        with self.assertRaises(ValueError):
            compare.align(base, pd.DataFrame({'cluster': ['a']}, index=['foreign']))

    def test_qc_key_whitespace_is_normalized_without_changing_values(self):
        raw = {(' min_genes' if key == 'min_genes' else key): value for key, value in QC.items()}
        self.assertEqual(validate_qc(raw), QC)
        self.assertIn(' min_genes', raw)  # The original agent response remains unchanged.
        with self.assertRaisesRegex(ValueError, 'collide'):
            validate_qc(dict(raw, min_genes=100))
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            validate_qc(dict(raw, min_cells=10))
        with self.assertRaises(ValueError):
            validate_qc({**raw, ' min_genes': '300'})
        with self.assertRaisesRegex(ValueError, 'object'):
            validate_qc([])

    def test_qc_request_saves_normalized_proposal_for_user_review(self):
        raw = {(' min_genes' if key == 'min_genes' else key): value for key, value in QC.items()}
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            state = {'stage': 'qc_review', 'messages': [], 'response': None}
            messages = [{'role': 'assistant', 'content': [{'type': 'text', 'text': json.dumps(raw)}]}]
            with patch.object(workflow, 'ask', return_value=(raw, messages)), patch.object(workflow, 'seal'):
                workflow.request(run, {}, state, 'QC fixture', 'qc_review')
            self.assertEqual(read_json(run / 'qc.json'), QC)
            self.assertEqual(state['response'], QC)
            self.assertEqual(state['stage'], 'qc_review')
            self.assertEqual(json.loads(state['messages'][-1]['content'][0]['text']), raw)
            self.assertIn('qc_field_whitespace_normalized', (run / 'events.jsonl').read_text())

    def test_truncated_api_response_preserves_state(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'api').mkdir()
            state = {'messages': [], 'response': {'previous': True}}
            original = copy.deepcopy(state)
            with patch.object(agent, 'call_claude', return_value={'stop_reason': 'max_tokens', 'content': []}) as api:
                with self.assertRaises(ValueError):
                    agent.ask(run, {'model': 'claude-test'}, state, 'test')
                self.assertEqual(api.call_args.args[0]['max_tokens'], 32000)
            self.assertEqual(state, original)
            self.assertTrue((run / 'api/001.response.json').exists())

    def test_tool_failure_is_returned_to_claude_without_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'api').mkdir()
            responses = [
                {'stop_reason': 'tool_use', 'content': [{'type': 'tool_use', 'id': 'one', 'name': 'run_shell', 'input': {'command': 'not allowed'}}]},
                {'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': '{"answer": "unsupported"}'}]},
            ]
            state = {'messages': []}
            with patch.object(agent, 'call_claude', side_effect=responses) as api:
                value, messages = agent.ask(run, {'model': 'claude-test'}, state, 'test', allow_tools=True)
            self.assertEqual(value['answer'], 'unsupported')
            self.assertTrue(api.call_args_list[1].args[0]['messages'][-2]['content'][0]['is_error'])
            self.assertEqual(state['messages'], [])

    def test_tool_checkpoint_survives_truncation_and_reuses_completed_response(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'api').mkdir()
            tool = {'stop_reason': 'tool_use', 'content': [dict(type='tool_use', id='search1', name='search_pubmed', input={'query': 'test'})]}
            cut = {'stop_reason': 'max_tokens', 'content': [{'type': 'text', 'text': '{"annotations": ['}]}
            with patch.object(agent, 'call_claude', side_effect=[tool, cut]), patch.object(agent, 'search_pubmed', return_value={'papers': []}) as search:
                with self.assertRaisesRegex(ValueError, 'output limit'):
                    agent.ask(run, {'model': 'claude-test'}, {'messages': []}, 'small task', allow_tools=True, job='part')
                self.assertEqual(search.call_count, 1)
            end = {'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': '{"annotations": []}'}]}
            with patch.object(agent, 'call_claude', return_value=end) as api, patch.object(agent, 'search_pubmed', side_effect=AssertionError('Repeated tool')):
                value, messages = agent.ask(run, {'model': 'claude-test'}, {'messages': []}, 'rebuilt prompt', allow_tools=True, job='part')
                self.assertEqual(value, {'annotations': []})
                tool_results = [b for m in api.call_args.args[0]['messages'] if isinstance(m['content'], list)
                                for b in m['content'] if b['type'] == 'tool_result']
                self.assertEqual(len(tool_results), 1)
            with patch.object(agent, 'call_claude', side_effect=AssertionError('Paid response repeated')):
                self.assertEqual(agent.ask(run, {'model': 'claude-test'}, {'messages': []}, '', allow_tools=True, job='part')[0], value)

    def test_partial_tool_batch_is_checkpointed(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'api').mkdir()
            tool = {'stop_reason': 'tool_use', 'content': [dict(type='tool_use', id=str(i), name='search_pubmed', input={'query': str(i)}) for i in (1, 2)]}
            with patch.object(agent, 'call_claude', return_value=tool), patch.object(agent, 'search_pubmed', side_effect=[{'papers': []}, KeyboardInterrupt]):
                with self.assertRaises(KeyboardInterrupt):
                    agent.ask(run, {'model': 'claude-test'}, {'messages': []}, 'task', allow_tools=True, job='batch')
            end = {'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': '{"ok": true}'}]}
            with patch.object(agent, 'call_claude', return_value=end), patch.object(agent, 'search_pubmed', return_value={'papers': []}) as search:
                agent.ask(run, {'model': 'claude-test'}, {'messages': []}, 'task', allow_tools=True, job='batch')
                self.assertEqual(search.call_count, 1)
                self.assertEqual(search.call_args.kwargs, {'query': '2'})

    def test_complete_fields_never_invents_truncated_values(self):
        self.assertEqual(workflow.complete_json_fields('```json\n{"annotations": [], "ambiguity": {"x": "y"}, "report_md": "cut'),
                         {'annotations': [], 'ambiguity': {'x': 'y'}})
        self.assertEqual(workflow.complete_json_fields('{"annotations": [{"run": "cut'), {})
        self.assertEqual(workflow.complete_json_fields('{"number": 12'), {})
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            workflow.complete_json_fields('{"x": 1, "x": 2}')

    def test_offline_repair_preserves_original_code_and_response(self):
        with tempfile.TemporaryDirectory() as temp:
            run = fixture(Path(temp))
            tables, _ = folders(run)
            names = ['res_0p3', 'res_0p6', 'res_1', 'downsample']
            save_json(run / 'computation.json', {'runs': names})
            rows = []
            for name in names:
                pd.DataFrame({'cell': ['a', 'b'], 'cluster': ['0', '0']}).to_csv(tables / f'cells_{name}.csv', index=False)
                pd.DataFrame(columns=['cluster', 'names', 'logfoldchanges', 'pvals_adj']).to_csv(tables / f'markers_{name}.csv', index=False)
                rows.append(dict(run=name, cluster='0', label='Unknown', confidence='uncertain', markers=[], pmids=[], notes='Synthetic'))
            save_json(run / 'data/investigation_test.json', {'expression': [{'gene': 'GENE1'}]})
            ambiguity = {'investigation': 'investigation_test', 'discussion': 'Synthetic hypothesis only'}
            text = '{"annotations": ' + json.dumps(rows) + ', "ambiguity": ' + json.dumps(ambiguity) + ', "report_md": "cut'
            save_json(run / 'api/001.response.json', {'stop_reason': 'max_tokens', 'content': [{'type': 'text', 'text': text}]})
            state = read_json(run / 'state.json')
            state['stage'] = 'interpret'
            save_json(run / 'state.json', state)
            workflow.seal(run)
            before = {str(p): digest(p) for p in (run / 'code').glob('*') if p.is_file()}
            before[str(run / 'api/001.response.json')] = digest(run / 'api/001.response.json')
            with patch.object(agent, 'call_claude', side_effect=AssertionError('Repair must be offline')):
                workflow.repair(run)
            self.assertTrue(all(digest(p) == h for p, h in before.items()))
            self.assertEqual(len(list((run / 'interpretation_parts/0').glob('*.json'))), 5)
            self.assertFalse((run / 'DRAFT.md').exists())
            self.assertEqual(read_json(run / 'recovery/state.json')['stage'], 'interpret')
            self.assertIn('Status: interpret', (run / 'AGENT_LOG.md').read_text())
            workflow.integrity(run)

    def test_full_synthetic_review_resume_and_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            run = fixture(Path(temp))
            tables, figures = folders(run)
            report = None
            calls = []
            def fake_ask(run, config, state, prompt, image_names=(), allow_tools=False, job=None):
                nonlocal report
                calls.append(state['stage'])
                if state['stage'] == 'plan':
                    self.assertFalse((tables / 'qc_cells.csv').exists())
                    value = copy.deepcopy(PLAN)
                elif state['stage'] == 'qc_review':
                    self.assertTrue((tables / 'qc_cells.csv').exists())
                    self.assertFalse((run / 'computation.json').exists())
                    value = dict(QC)
                else:
                    if report is None:
                        report = fake_report(run)
                    if state['stage'].startswith('annotations_'):
                        name = state['stage'].removeprefix('annotations_')
                        value = {'annotations': [a for a in report['annotations'] if a['run'] == name]}
                    elif state['stage'] == 'ambiguity':
                        value = {'ambiguity': report['ambiguity']}
                    else:
                        value = {'report_md': report['report_md']}
                return value, state['messages'] + [{'role': 'assistant', 'content': 'mock response'}]
            with patch.object(workflow, 'ask', side_effect=fake_ask), patch('builtins.input', side_effect=['quit']):
                workflow.interact(run)
            self.assertFalse((tables / 'qc_cells.csv').exists())
            def fail_report(*args, **kwargs):
                if args[2]['stage'] == 'report':
                    raise ValueError('simulated report limit')
                return fake_ask(*args, **kwargs)
            with patch.object(workflow, 'ask', side_effect=fail_report), patch('builtins.input', side_effect=['approve', 'approve']):
                with self.assertRaisesRegex(ValueError, 'simulated report limit'):
                    workflow.interact(run)
            self.assertEqual(len(list((run / 'interpretation_parts/0').glob('*.json'))), 5)
            self.assertIn('Status: interpret', (run / 'AGENT_LOG.md').read_text())
            calls.clear()
            with patch.object(workflow, 'ask', side_effect=fake_ask), patch('builtins.input', side_effect=['quit']):
                workflow.interact(run)
            self.assertEqual(calls, ['report'])
            self.assertEqual(read_json(run / 'state.json')['stage'], 'review')
            result = workflow.module('04_verify.py').verify(run)
            self.assertEqual(result['raw_cells_verified'], 180)
            self.assertEqual(result['retained_cells'], 179)
            self.assertEqual(result['sampled_cells'], 125)
            self.assertEqual(result['independent_ari_comparisons'], 3)
            stability = pd.read_csv(tables / 'population_stability.csv')
            for col in stability:
                if col.endswith('_supported_label_agreement'):
                    self.assertEqual(stability[col].iloc[0], 0)
            interpretation = read_json(run / 'interpretation.json')
            bad = copy.deepcopy(interpretation)
            bad['annotations'][0]['pmids'] = ['unretrieved']
            with self.assertRaises(ValueError):
                workflow.validate_interpretation(run, bad)
            # Persist the new valid response before rendering; a rendering failure can be retried without another API call.
            state = read_json(run / 'state.json')
            workflow.save_interpretation(run, state, interpretation)
            self.assertEqual(read_json(run / 'state.json')['stage'], 'render_review')
            with patch.object(workflow, 'step', side_effect=ValueError('simulated rendering failure')):
                with self.assertRaisesRegex(ValueError, 'simulated rendering'):
                    workflow.interact(run)
            workflow.integrity(run)
            with patch('builtins.input', side_effect=['accept', 'raw QC and ARI checked', 'synthetic labels deliberately uncertain', 'no real biology tested']):
                workflow.interact(run)
            self.assertTrue((run / 'RESULTS.md').exists())
            workflow.module('04_verify.py').verify(run)
            if os.environ.get('TASK2_TEST_ARTIFACTS'):
                shutil.copytree(figures, Path(os.environ['TASK2_TEST_ARTIFACTS']) / 'figures', dirs_exist_ok=True)
                shutil.copy2(run / 'verification.json', Path(os.environ['TASK2_TEST_ARTIFACTS']) / 'verification.json')
            metric_path = tables / 'robustness_metrics.csv'
            metrics = pd.read_csv(metric_path)
            metrics.loc[0, 'ari'] = -99
            metrics.to_csv(metric_path, index=False)
            with self.assertRaisesRegex(ValueError, 'Saved evidence changed'):
                workflow.integrity(run)
            with self.assertRaisesRegex(ValueError, 'Independent ARI disagrees'):
                workflow.module('04_verify.py').verify(run, check_manifest=False)
            self.assertTrue((figures / 'annotated_umap_res_0p6.png').exists())


if __name__ == '__main__':
    unittest.main()
