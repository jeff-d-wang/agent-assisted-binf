"""Interactive Sonnet plan/review/interpretation around Task 3's numerical scripts."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from agent import ask, reject_job
from workflow_common import (read_json, save_json, folders, integrity, seal, log_step, event,
                             require, validate_qc, resolution_key)

HERE = Path(__file__).resolve().parent
PROMPTS = {
    'plan': '''Propose and defend the supplied executable plan, before analysis. Return
{"rationale": "Markdown, <=700 words"}. Explain the question, inputs, methods, parameters,
review stops, independent checks, null hypothesis and limitations. Config is fixed for this
run: recommend quitting and changing it if inappropriate; do not pretend to change settings.''',
    'qc': '''Inspect QC plots and quantiles, then propose inclusive retention thresholds with
distribution-based justification. Return {"rationale": "<=500 words", "min_genes": integer,
"max_genes": integer, "min_counts": integer, "max_counts": integer, "max_pct_mt": number}.
Positive integer minima; max_pct_mt 0–100. Discuss tissue quality gradients and alignment.
Only approve image alignment if actually supported by the supplied plot; uncertainty remains.''',
    'cluster': '''Choose one already computed resolution using ONLY the supplied expression
diagnostics. Return {"resolution": number, "reason": "<=500 words"}. Defend using cluster
sizes, PCA, expression UMAPs and overlaps. No tissue cluster map has been supplied. Do not
guess anatomy. Baseline 0.5 was proposed, not guaranteed correct. If preprocessing is
inadequate, explain that the user must quit and start a revised run before approval.''',
    'report': '''Write {"report_md": "complete Markdown report, <=1500 words", "pmids": ["..."]}.
Cover T1–T5: methods and QC, matching expression/tissue labels, numerical statistic and graph,
effect size and null comparison, candidate gene method and maps, same-gene DE/spatial examples
including absent categories, sensitivity, limitations and a qualified answer to the scientific
question. Separate computed observations, agent inference and external support explicitly.
Use search_pubmed only for specific biological claims needing support; cite only retrieved
PMIDs and list them in pmids. Do not infer cell types/anatomy from numeric clusters alone.
Include a draft audit: actual resources, computed vs retrieved table, numerical verifier's
scope, unresolved claims; leave the external reviewer/user audit pending. Do not invent an
independent human check or an actual agent error. This is a draft awaiting user acceptance.''',
}


def module(name, folder=HERE):
    spec = importlib.util.spec_from_file_location('spatial_' + name.replace('.', '_'), folder / name)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def start(c, inputs, task):
    run = module('01_qc.py', task).create_run(c, inputs, task)
    save_json(run / 'agent_state.json', {'stage': 'plan', 'revision': 0, 'response': None, 'feedback': []})
    log_step(run, f'Started standalone scientific-agent workflow. Analyst model: {c["model"]}; '
             'developer: Codex; computations: Python. No analysis or approvals yet. '
             'Exact requests/responses and retrieved sources will be saved in api/ and data/.')
    seal(run, 'plan')
    return run


def persist(run, state):
    save_json(run / 'agent_state.json', state)
    seal(run, read_json(run / 'state.json')['stage'])


def packet(run, stage):
    tables, figures = folders(run)
    data = {'config': read_json(run / 'config.json'), 'tables_path': str(tables),
            'figures_path': str(figures), 'tables': {}, 'metadata': {}}
    files = {
        'plan': [],
        'qc': ['qc_quantiles.csv'],
        'cluster': ['cluster_sizes.csv', 'resolution_comparison.csv', 'resolution_overlaps.csv', 'pca_variance.csv'],
        'report': ['cluster_sizes.csv', 'resolution_comparison.csv', 'gene_rankings.csv',
                   'ranking_examples.csv', 'mapped_genes.csv', 'original_vs_randomized.csv',
                   'spatial_resolution_sensitivity.csv'],
    }
    for name in files[stage]:
        data['tables'][name] = (tables / name).read_text()
    for name in ('qc_summary.json', 'qc_review.json', 'filter_summary.json', 'cluster_review.json',
                 'graph_summary.json', 'spatial_summary.json', 'gene_methods.json', 'verification.json'):
        if (run / name).exists():
            data['metadata'][name] = read_json(run / name)
    data['retrieved_sources'] = [read_json(p) for p in sorted((run / 'data').glob('pubmed_*.json'))]
    return json.dumps(data)


def validate_response(run, stage, value):
    require(isinstance(value, dict), 'Response must be a JSON object')
    if stage == 'qc':
        return validate_qc(value)
    if stage == 'plan':
        require(set(value) == {'rationale'}, 'Plan needs rationale only')
        text = value['rationale']
    elif stage == 'cluster':
        require(set(value) == {'resolution', 'reason'} and
                value['resolution'] in read_json(run / 'config.json')['resolutions'], 'Choose a computed resolution')
        text = value['reason']
    else:
        require(set(value) == {'report_md', 'pmids'}, 'Report needs report_md and pmids')
        require(isinstance(value['pmids'], list) and all(isinstance(p, str) for p in value['pmids']), 'Invalid PMID list')
        retrieved = {p['pmid'] for f in (run / 'data').glob('pubmed_*.json') for p in read_json(f)['papers']}
        require(set(value['pmids']) <= retrieved, 'Report lists unretrieved PMIDs')
        text = value['report_md']
    require(isinstance(text, str) and len(text.strip()) >= 20, 'Missing substantive explanation')
    return value


def numerical_step(run, script, *args):
    print(f'Computing {script}; log in {run / (script + ".log")}', flush=True)
    with (run / (script + '.log')).open('w') as log:
        completed = subprocess.run([sys.executable, str(run / 'code' / script), str(run), *args],
                                   stdout=log, stderr=subprocess.STDOUT)
    require(completed.returncode == 0, f'{script} failed; inspect its log and resume after resolving the cause')


def interact(run):
    integrity(run)
    c = read_json(run / 'config.json')
    state = read_json(run / 'agent_state.json')
    while state['stage'] != 'accepted':
        stage = state['stage']
        numerical = read_json(run / 'state.json')['stage']
        # Completed numeric stages can survive an interruption before agent_state advances.
        if stage == 'compute_qc':
            if numerical == 'plan':
                module('01_qc.py', run / 'code').main(c, read_json(run / 'inputs.json'), run.parent.parent, run=run)
            state.update(stage='qc', response=None, revision=0)
            persist(run, state)
            continue
        if stage == 'compute_cluster':
            if numerical == 'qc':
                numerical_step(run, '02_cluster.py', '--qc', str(run / 'approved_qc.json'))
            state.update(stage='cluster', response=None, revision=0)
            persist(run, state)
            continue
        if stage == 'compute_spatial':
            if numerical == 'cluster':
                review = read_json(run / 'approved_cluster.json')
                numerical_step(run, '03_spatial.py', '--resolution', str(review['resolution']), '--reason', review['reason'])
            numerical_step(run, '04_verify.py')
            state.update(stage='report', response=None, revision=0)
            persist(run, state)
            continue
        if state['response'] is None:
            images = {'plan': [], 'qc': ['qc_distributions.png', 'qc_joint.png', 'qc_tissue.png'],
                      'cluster': [f'umap_{resolution_key(r)}.png' for r in c['resolutions']],
                      'report': ['clusters_umap_and_tissue.png', 'gene_tissue_maps.png',
                                 'randomized_control.png', 'de_vs_spatial_ranks.png', 'qc_tissue.png']}[stage]
            context = packet(run, stage)
            prompt = PROMPTS[stage] + '\nEvidence:\n' + context + '\nReview history:\n' + json.dumps(state['feedback'])
            job = f'{stage}_{state["revision"]}'
            value, _ = ask(run, c, {'messages': []}, prompt, images, allow_tools=stage == 'report', job=job)
            try:
                validate_response(run, stage, value)
            except (ValueError, KeyError, TypeError) as error:
                reject_job(run, job, error)
                raise ValueError(f'Invalid {stage} response retained; resume to request correction: {error}') from error
            state['response'] = value
            save_json(run / f'agent_{stage}.json', value)
            text = value.get('report_md', value.get('rationale', value.get('reason')))
            filename = {'plan': 'PLAN.md', 'qc': 'QC.md', 'cluster': 'CLUSTER_REVIEW.md', 'report': 'DRAFT.md'}[stage]
            (run / filename).write_text(text + '\n')
            if stage == 'report':
                (run / 'REVIEW_PACKET.md').write_text('# Evidence for independent review\n\n'
                    'Read DRAFT.md, PLAN.md, QC.md, CLUSTER_REVIEW.md, verification.json, AGENT_LOG.md, '
                    'and the linked figures/tables. API exchanges are in api/; sources in data/.\n\n'
                    'Check actual source support and at least one result independently. Another model agreeing '
                    'is not independent verification. Record the reviewer identity/version, prompts, answers, '
                    'files checked, actual weaknesses and corrections. Never invent a failure for the rubric.\n\n'
                    '```json\n' + packet(run, stage) + '\n```\n')
            log_step(run, f'Claude ({c["model"]}) answered {stage}; response summary and proposed decisions: '
                     f'{filename}; exact prompt/response: api/ job {job}. Human approval is still pending. '
                     'Computed evidence is supplied by Python; retrieved support is in data/pubmed_*.json.')
            persist(run, state)
        value = state['response']
        print('\n' + value.get('report_md', value.get('rationale', value.get('reason'))) + '\n')
        if stage == 'qc':
            print(json.dumps({k: v for k, v in value.items() if k != 'rationale'}, indent=2))
        if stage == 'cluster':
            print('Proposed primary resolution:', value['resolution'])
        action = 'accept' if stage == 'report' else 'approve'
        answer = input(f'Type feedback, {action}, or quit (pause for external review): ').strip()
        if answer.lower() == 'quit':
            print(f'Paused. Resume: python spatial/run_analysis.py agent --resume {run}')
            return
        if not answer:
            continue
        if answer.lower() != action:
            state['feedback'].append({'stage': stage, 'previous_response': value, 'user_feedback': answer})
            state['revision'] += 1
            state['response'] = None
            event(run, 'user_feedback', stage=stage, feedback=answer)
            persist(run, state)
            continue
        if stage == 'report':
            review = {}
            for key, question in [('reviewer', 'Reviewer identity/model and date: '),
                                  ('independent_check', 'Actual independent check, evidence file and result: '),
                                  ('agent_weakness', 'Actual questionable output/choice and how checked/corrected: '),
                                  ('uncertainties', 'Remaining uncertainties: ')]:
                review[key] = input(question).strip()
            if not all(review.values()):
                print('All audit fields are required; nothing accepted.')
                continue
            (run / 'REVIEW.md').write_text('# User acceptance and independent review\n\n' +
                                          '\n\n'.join(f'**{k}:** {v}' for k, v in review.items()) + '\n')
            (run / 'RESULTS.md').write_text(value['report_md'] + '\n')
            state['stage'] = 'accepted'
            log_step(run, 'User accepted the report. Review/audit statements: REVIEW.md. '
                     'Acceptance records user judgment; it does not automatically prove claims or complete rubric scores.')
            event(run, 'accepted', review=review)
        else:
            if stage in ('qc', 'cluster'):
                save_json(run / f'approved_{stage}.json', value)
            state.update(stage={'plan': 'compute_qc', 'qc': 'compute_cluster', 'cluster': 'compute_spatial'}[stage], response=None)
            event(run, 'approved', stage=stage, proposal=value)
        persist(run, state)
    print(f'User-accepted report: {run / "RESULTS.md"}. Curate submission evidence and finish the rubric separately.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    try:
        interact(parser.parse_args().run.resolve())
    except KeyboardInterrupt:
        raise SystemExit('Paused; resume with spatial/run_analysis.py agent --resume RUN_DIRECTORY')
