"""Standalone Task 2: Claude proposes and interprets; Python computes and verifies."""
import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from workflow_common import (PACKAGES, SEED, digest, event, folders, read_json, save_json,
                             require, validate_plan, validate_qc)
from agent import ask, reject_job

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PLAN_PROMPT = """Propose and defend a feasible workflow BEFORE any analysis. Explain why it
answers which conclusions remain stable. Choose numerical settings within the supported
method family, explain QC selection after distributions are available, annotation order,
resolution control, downsampling, ambiguity investigation, independent checks and limitations.
Return {"rationale": "Markdown plan and defense", "settings": {
"target_sum": number 1000–100000, "n_top_genes": integer 100–5000,
"n_pcs": integer 2–100, "n_neighbors": integer 2–100,
"baseline_resolution": number .05–3, "resolutions": 3–5 distinct numbers .05–3 including baseline,
"sample_fraction": number .6–.8, "min_cells_per_gene": integer 1–20, "scale_max": number 5–20}}.
These are executable settings, not illustrative values. Seed is fixed at 42. No QC thresholds yet.
"""
QC_PROMPT = """Inspect the QC plots and quantiles. Choose inclusive cell-retention thresholds
from these distributions and justify each, including high-count/doublet caveats. Do not
simply adopt tutorial cutoffs. Return {"rationale": "Markdown justification",
"min_genes": integer, "max_genes": integer, "min_counts": integer, "max_counts": integer,
"max_pct_mt": number 0–100}. No other fields. This is reviewed before filtering/clustering.
"""
ANNOTATION_PROMPT = """Annotate ONLY the requested analysis run, using its own computed markers.
Return {"annotations": [...]}, one object per cluster with "run", "cluster" (string),
"label", "confidence" (supported/tentative/uncertain), "markers" (3–6 positively enriched
significant genes, or fewer if evidence is insufficient), "pmids" (retrieved PMID strings),
and "notes" (at most 60 words per cluster). Use consistent broad names where independently
justified; existing annotations are provisional hypotheses, not a reference label map.
Non-uncertain labels require two computed enriched genes and relevant retrieved support.
A source mentioning a cell type without supporting the claimed markers is an evidence gap.
Reuse saved evidence; search only to fill a specific gap. Keep unsupported labels uncertain.
Do not write the report or annotate other runs in this response.
"""
AMBIGUITY_PROMPT = """Investigate one ambiguity using saved evidence and inspect_population if
needed. Reuse an existing relevant investigation instead of recomputing it. Return only
{"ambiguity": {"investigation": "investigation_HASH", "discussion": "at most 350 words"}}.
Compare relevant markers, shared programs, QC, size and parameter sensitivity. A mixed
cluster or a resolution-dependent split does NOT by itself demonstrate a biological continuum.
State what evidence supports each explanation and what remains unknown. No full report.
"""
REPORT_PROMPT = """Write ONLY {"report_md": "complete Markdown report"}, at most 1200 words.
Use the provided provisional annotations, investigation, sources and computed comparisons.
Do not regenerate the annotations JSON. Critically distinguish observations, agent inferences
and external support, including weaknesses of recovered material. Do not turn a mixed cluster
or parameter-dependent split into a demonstrated biological continuum. Flag unsupported
identities; a retrieved PMID alone does not validate a claim. Cover methods/QC, marker evidence,
quantified resolution splits/merges, shared-cell downsampling, ambiguity, a population | markers |
stable across resolutions? | stable after downsampling? | notes table, robust versus sensitive
conclusions, and Agent Audit. Cite only supplied retrieved PubMed sources and use actual artifact
paths. User review and acceptance are still pending. The machine-readable label-agreement table
is rendered afterwards; do not claim to have inspected it unless it is supplied. Keep references
brief. No new tool calls in this final writing step; identify remaining evidence gaps explicitly.
"""


def load_config(path):
    c = read_json(path)
    require(set(c) == {'input_dir', 'model', 'question'}, 'Use the fields in single_cell/config.json')
    require(isinstance(c['model'], str) and c['model'].startswith('claude-'), 'Choose an explicit Claude model ID')
    require(isinstance(c['question'], str) and bool(c['question'].strip()), 'Supply the scientific question')
    c['input_dir'] = str((ROOT / c['input_dir']).resolve())
    return c


def preflight(c):
    versions = {p: importlib.metadata.version(p) for p in PACKAGES}
    require(versions['scanpy'] == '1.9.8', 'Use the tested single_cell/requirements.txt environment (Scanpy 1.9.8)')
    # Import compiled dependencies before making a paid request.
    import scanpy
    import leidenalg
    import igraph
    paths = [Path(c['input_dir']) / name for name in ('matrix.mtx', 'genes.tsv', 'barcodes.tsv')]
    require(all(p.is_file() for p in paths), 'Missing 10x v2 files; extract with PROJECT_PLAN.md tar command')
    return {'sha256': {str(p): digest(p) for p in paths}, 'versions': versions,
            'python': sys.version, 'seed': SEED}


def create_run(c, inputs, task_dir=HERE):
    run = Path(task_dir) / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for folder in ('api', 'data', 'cache', 'code'):
        (run / folder).mkdir(parents=True, exist_ok=True)
    for folder in folders(run):
        folder.mkdir(parents=True)
    save_json(run / 'config.json', c)
    save_json(run / 'inputs.json', inputs)
    save_json(run / 'state.json', {'stage': 'plan', 'messages': [], 'response': None})
    for path in HERE.glob('*.py'):
        shutil.copy2(path, run / 'code' / path.name)
    shutil.copy2(HERE / 'requirements.txt', run / 'code/requirements.txt')
    for name in ('PROJECT_PLAN.md', 'RUBRIC.md'):
        shutil.copy2(ROOT / name, run / name)
    event(run, 'created', analyst='Claude', developer='Codex', seed=SEED)
    seal(run)
    return run


def seal(run):
    paths = [run / 'config.json', run / 'inputs.json', run / 'state.json', run / 'PROJECT_PLAN.md', run / 'RUBRIC.md']
    for name in ('plan.json', 'qc.json', 'PLAN.md', 'QC.md', 'qc_summary.json', 'filter_summary.json',
                 'computation.json', 'interpretation.json', 'DRAFT.md', 'RESULTS.md', 'REVIEW.md'):
        if (run / name).exists():
            paths.append(run / name)
    for directory in (run / 'code', run / 'runtime', run / 'recovery', run / 'interpretation_parts', run / 'data', run / 'cache', *folders(run)):
        paths.extend(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    if read_json(run / 'state.json')['stage'] == 'render_review':
        # Annotation outputs may be partially rewritten on failure; the saved response is authoritative.
        paths = [p for p in paths if not p.name.startswith('annotated_') and
                 p.name not in ('annotations.csv', 'population_stability.csv')]
    save_json(run / 'manifest.json', {str(p): digest(p) for p in paths})


def integrity(run):
    for path, expected in read_json(run / 'inputs.json')['sha256'].items():
        require(digest(path) == expected, 'Raw input changed; start a new run')
    for path, expected in read_json(run / 'manifest.json').items():
        require(digest(path) == expected, 'Saved evidence changed: ' + path)


def step(run, name, *extra):
    environment = dict(os.environ)
    environment.update(MPLCONFIGDIR=str(run / 'cache/matplotlib'), NUMBA_CACHE_DIR=str(run / 'cache/numba'),
                       NUMBA_NUM_THREADS='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                       PYTHONHASHSEED=str(SEED))
    print('Running', name, flush=True)
    with (run / (name + '.log')).open('w') as log:
        result = subprocess.run([sys.executable, str(run / 'code' / name), str(run), *extra],
                                env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=1800)
    event(run, 'computation', script=name, arguments=extra, returncode=result.returncode)
    require(result.returncode == 0, f'{name} failed; inspect {run / (name + ".log")} and resume')


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), HERE / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def packet(run, run_names=None, include_markers=True):
    import pandas as pd
    tables, figures = folders(run)
    meta = read_json(run / 'computation.json')
    value = {'computation': meta, 'qc': read_json(run / 'filter_summary.json'),
             'tables_path': str(tables), 'figures_path': str(figures), 'tables': {}}
    for pattern in ('top_markers_*.csv', 'sizes_*.csv', 'robustness_metrics.csv', 'cluster_overlaps.csv', 'pca_variance.csv', 'population_stability.csv'):
        for path in tables.glob(pattern):
            if path.name.startswith('top_markers_') and (not include_markers or
                    (run_names is not None and path.stem.removeprefix('top_markers_') not in run_names)):
                continue
            frame = pd.read_csv(path).round(5)
            value['tables'][path.name] = frame.to_csv(index=False)
    if (run / 'verification.json').exists():
        value['verification'] = read_json(run / 'verification.json')
    papers = {}
    for path in sorted((run / 'data').glob('pubmed_*.json')):
        for paper in read_json(path)['papers']:
            papers[paper['pmid']] = paper
    value['retrieved_sources'] = list(papers.values())
    value['saved_investigations'] = [read_json(p) for p in sorted((run / 'data').glob('investigation_*.json'))]
    return json.dumps(value)


def validate_annotations(run, annotations, run_names=None):
    import pandas as pd
    tables, _ = folders(run)
    meta = read_json(run / 'computation.json')
    expected, positive = set(), {}
    for name in meta['runs'] if run_names is None else run_names:
        obs = pd.read_csv(tables / f'cells_{name}.csv', dtype={'cluster': str})
        expected.update((name, c) for c in obs.cluster.unique())
        markers = pd.read_csv(tables / f'markers_{name}.csv', dtype={'cluster': str})
        for cluster in obs.cluster.unique():
            keep = markers[(markers.cluster == cluster) & (markers.logfoldchanges > 0) & (markers.pvals_adj < .05)]
            positive[name, cluster] = set(keep.names)
    retrieved = {paper['pmid'] for path in (run / 'data').glob('pubmed_*.json') for paper in read_json(path)['papers']}
    actual = []
    for row in annotations:
        require(set(row) == {'run', 'cluster', 'label', 'confidence', 'markers', 'pmids', 'notes'}, 'Invalid annotation fields')
        key = row['run'], row['cluster']
        require(key in expected, 'Unknown run/cluster annotation')
        require(all(isinstance(row[k], str) and row[k].strip() for k in ('label', 'notes')), 'Labels and notes must be nonempty')
        require(row['confidence'] in ('supported', 'tentative', 'uncertain'), 'Unknown confidence')
        require(isinstance(row['markers'], list) and all(isinstance(g, str) for g in row['markers']) and
                isinstance(row['pmids'], list) and all(isinstance(p, str) for p in row['pmids']), 'Markers/PMIDs must be lists of strings')
        require(set(row['markers']) <= positive[key], 'Annotation cites genes not positively enriched in the computed contrast')
        require(set(row['pmids']) <= retrieved, 'Annotation cites an unretrieved PMID')
        if row['confidence'] != 'uncertain':
            require(len(set(row['markers'])) >= 2 and len(row['pmids']) > 0,
                    'Supported/tentative labels need two computed markers and retrieved evidence; otherwise retain uncertainty')
        actual.append(key)
    require(len(actual) == len(set(actual)) and set(actual) == expected, 'Annotate every cluster exactly once')


def validate_ambiguity(run, ambiguity):
    require(set(ambiguity) == {'investigation', 'discussion'} and isinstance(ambiguity['discussion'], str)
            and bool(ambiguity['discussion'].strip()), 'Missing ambiguity discussion')
    valid = {p.stem for p in (run / 'data').glob('investigation_*.json')
             if read_json(p).get('expression')}
    require(ambiguity['investigation'] in valid, 'Ambiguity needs an actual successful expression investigation')


def validate_interpretation(run, value):
    require(set(value) == {'annotations', 'ambiguity', 'report_md'}, 'Report fields do not match requested schema')
    require(isinstance(value['report_md'], str) and len(value['report_md'].strip()) > 100, 'Missing full report')
    validate_annotations(run, value['annotations'])
    validate_ambiguity(run, value['ambiguity'])
    return value


def request(run, c, state, prompt, stage):
    require(stage in ('plan', 'qc_review'), 'Interpretation uses separately checkpointed parts')
    images = ('qc_distributions.png', 'qc_joint.png') if stage == 'qc_review' else ()
    job = f'{stage}:{len(state["messages"])}:{prompt}'
    response, messages = ask(run, c, state, prompt, images, job=job)
    try:
        validated = (validate_plan if stage == 'plan' else validate_qc)(response)
    except (ValueError, TypeError, KeyError) as exc:
        reject_job(run, job, exc)
        raise
    if validated != response:
        event(run, 'qc_field_whitespace_normalized', original_fields=list(response), normalized_fields=list(validated),
              values_unchanged=True, job=job)
    response = validated
    if stage == 'plan':
        validate_plan(response)
        save_json(run / 'plan.json', response)
        (run / 'PLAN.md').write_text(response['rationale'] + '\n\n```json\n' + json.dumps(response['settings'], indent=2) + '\n```\n')
    elif stage == 'qc_review':
        validate_qc(response)
        save_json(run / 'qc.json', response)
        (run / 'QC.md').write_text(response['rationale'] + '\n\n```json\n' + json.dumps(response, indent=2) + '\n```\n')
    state.update(response=response, messages=messages, stage=stage)
    save_json(run / 'state.json', state)
    seal(run)


def parts_dir(run, state):
    return run / 'interpretation_parts' / str(state.get('interpretation_revision', 0))


def interpretation_part(run, c, state, name, prompt, validate, tools=False, images=()):
    directory = parts_dir(run, state)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (name + '.json')
    if path.exists():
        value = read_json(path)
        validate(value)
        return value
    job = f'interpretation:{state.get("interpretation_revision", 0)}:{name}'
    # Each task starts with focused evidence, not the accumulating plan/QC/tool conversation.
    context = {'messages': [], 'stage': name}
    value, _ = ask(run, c, context, prompt, images, allow_tools=tools, job=job)
    try:
        validate(value)
    except (ValueError, KeyError, TypeError) as exc:
        reject_job(run, job, exc)
        raise ValueError(f'{name} needs correction: {exc}. Resume retries only this part.') from exc
    save_json(path, value)
    event(run, 'interpretation_part_saved', part=name, revision=state.get('interpretation_revision', 0), job=job)
    seal(run)
    audit(run, state)
    return value


def save_interpretation(run, state, value):
    validate_interpretation(run, value)
    save_json(run / 'interpretation.json', value)
    (run / 'DRAFT.md').write_text(value['report_md'] + '\n')
    state.update(response=value, stage='render_review')
    save_json(run / 'state.json', state)
    seal(run)
    audit(run, state)


def interpret(run, c, state):
    meta = read_json(run / 'computation.json')
    annotations = []
    previous = state.get('response') or {}
    feedback = '\nUser feedback for this revision: ' + state.get('interpretation_feedback', 'Initial interpretation; no human acceptance yet.')
    for name in meta['runs']:
        def validate(value):
            require(set(value) == {'annotations'}, 'Return annotations only')
            validate_annotations(run, value['annotations'], [name])
        context = {'requested_run': name, 'other_provisional_annotations': annotations,
                   'previous_annotations_for_this_run': [a for a in previous.get('annotations', []) if a['run'] == name]}
        result = interpretation_part(run, c, state, 'annotations_' + name,
            ANNOTATION_PROMPT + feedback + '\n' + json.dumps(context) + '\n' + packet(run, [name]),
            validate, tools=True, images=(f'umap_{name}.png',))
        annotations.extend(result['annotations'])
    def validate_ambiguity_part(value):
        require(set(value) == {'ambiguity'}, 'Return ambiguity only')
        validate_ambiguity(run, value['ambiguity'])
    ambiguity = interpretation_part(run, c, state, 'ambiguity', AMBIGUITY_PROMPT + feedback + '\n' +
        json.dumps(annotations) + '\n' + packet(run, include_markers=False), validate_ambiguity_part, tools=True)
    def validate_report(value):
        require(set(value) == {'report_md'} and isinstance(value['report_md'], str) and
                len(value['report_md'].strip()) > 100, 'Return a complete report_md only')
    report = interpretation_part(run, c, state, 'report', REPORT_PROMPT + feedback + '\n' +
        json.dumps({'annotations': annotations, **ambiguity}) + '\n' + packet(run, include_markers=False),
        validate_report, images=(f"umap_{meta['baseline']}.png", 'pca_variance.png'))
    save_interpretation(run, state, dict(annotations=annotations, **ambiguity, **report))


def complete_json_fields(text):
    """Read only complete leading JSON values; never repair or invent truncated content."""
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
    require(text.startswith('{'), 'Response is not a JSON object')
    decoder, fields, pos = json.JSONDecoder(), {}, 1
    while True:
        try:
            while pos < len(text) and text[pos].isspace():
                pos += 1
            if pos >= len(text) or text[pos] == '}':
                return fields
            key, pos = decoder.raw_decode(text, pos)
            require(isinstance(key, str) and key not in fields, 'Duplicate or invalid JSON key')
            while pos < len(text) and text[pos].isspace():
                pos += 1
            require(pos < len(text) and text[pos] == ':', 'Invalid JSON separator')
            pos += 1
            while pos < len(text) and text[pos].isspace():
                pos += 1
            value, end = decoder.raw_decode(text, pos)
            # Require the delimiter too: a number at EOF may itself be truncated.
            while end < len(text) and text[end].isspace():
                end += 1
            if end >= len(text):
                return fields
            require(text[end] in ',}', 'Invalid JSON value delimiter')
            fields[key] = value
            if text[end] == '}':
                return fields
            pos = end + 1
        except json.JSONDecodeError:
            return fields


def repair(run):
    """Offline migration of a stopped interpretation, preserving original code and API records."""
    integrity(run)
    state = read_json(run / 'state.json')
    require(state['stage'] == 'interpret' and (run / 'computation.json').exists(),
            'Repair supports a stopped interpretation after successful computation only')
    require(not (run / 'recovery').exists() and not (run / 'runtime').exists(), 'This run already has a repair snapshot; use --resume')
    for name in ('01_qc.py', '02_cluster.py', '03_compare.py', '04_verify.py', 'workflow_common.py', 'requirements.txt'):
        require(digest(run / 'code' / name) == digest(HERE / name), 'Scientific code changed; cannot repair in place: ' + name)
    require(preflight(read_json(run / 'config.json'))['versions'] == read_json(run / 'inputs.json')['versions'],
            'Restore the recorded package versions before repairing')
    # New tool artifacts were written after the previous manifest; verify their event records too.
    for line in (run / 'events.jsonl').read_text().splitlines():
        entry = json.loads(line)
        if entry['event'] == 'tool' and not entry['result'].get('is_error'):
            result = json.loads(entry['result']['content'])
            if entry['name'] == 'search_pubmed':
                matches = [p for p in (run / 'data').glob('pubmed_*.json') if read_json(p) == result]
                require(bool(matches), 'Retrieved source differs from saved tool event')
            elif entry['name'] == 'inspect_population':
                require(read_json(run / 'data' / (result['evidence_prefix'] + '.json')) == result,
                        'Investigation differs from saved tool event')
    recovered, provenance = {}, {}
    responses = sorted((run / 'api').glob('*.response.json'))
    if responses:
        source = responses[-1]
        response = read_json(source)
        require(response.get('stop_reason') in ('max_tokens', 'end_turn'), 'Latest response has no recoverable text output')
        text = '\n'.join(b['text'] for b in response['content'] if b['type'] == 'text')
        fields = complete_json_fields(text) if text.strip() else {}
        if 'annotations' in fields:
            validate_annotations(run, fields['annotations'])
            for name in read_json(run / 'computation.json')['runs']:
                recovered['annotations_' + name] = {'annotations': [a for a in fields['annotations'] if a['run'] == name]}
        if 'ambiguity' in fields:
            validate_ambiguity(run, fields['ambiguity'])
            recovered['ambiguity'] = {'ambiguity': fields['ambiguity']}
        # Deliberately regenerate the report to assess recovered hypotheses and evidence gaps.
        provenance = {'source': str(source), 'sha256': digest(source), 'stop_reason': response['stop_reason'],
                      'recovered_parts': list(recovered), 'status': 'Provisional Claude output; not human accepted'}
    backup = run / 'recovery'
    backup.mkdir()
    for name in ('state.json', 'manifest.json', 'AGENT_LOG.md'):
        if (run / name).exists():
            shutil.copy2(run / name, backup / name)
    runtime = run / 'runtime'
    runtime.mkdir()
    for path in HERE.glob('*.py'):
        shutil.copy2(path, runtime / path.name)
    shutil.copy2(HERE / 'requirements.txt', runtime / 'requirements.txt')
    state.update(interpretation_revision=0)
    directory = parts_dir(run, state)
    directory.mkdir(parents=True, exist_ok=True)
    for name, value in recovered.items():
        save_json(directory / (name + '.json'), value)
    save_json(backup / 'provenance.json', provenance)
    save_json(run / 'state.json', state)
    event(run, 'interpretation_repaired', **provenance)
    seal(run)
    audit(run, state)
    print('Offline repair complete. Saved provisional parts:', ', '.join(recovered) or 'none')
    print('No API call or scientific recalculation was made. Next: --resume', run)


def audit(run, state):
    tables, figures = folders(run)
    completed = ', '.join(p.stem for p in sorted(parts_dir(run, state).glob('*.json'))) or 'none'
    (run / 'AGENT_LOG.md').write_text(f'''# Task 2 run audit

Status: {state['stage']}; no automatic course grade or checkpoint completion.
Saved interpretation parts (revision {state.get('interpretation_revision', 0)}): {completed}.

- Claude is the scientific agent; Codex developed the software separately.
- Exact prompts, answers, model IDs and token usage: api/. Decisions and tool results: events.jsonl (UTC).
- Pending tool exchanges and completed responses: api/job_*.json; validated parts: interpretation_parts/.
- If repaired: original run state/manifest/log in recovery/; original scientific code in code/;
  repaired runtime in runtime/. Recovered agent proposals remain provisional Claude output.
- Proposed methods and defense: PLAN.md; thresholds and reasons: QC.md. Seed: {SEED}.
- Inputs, SHA256, Python/package versions: inputs.json; executed code: code/.
- Computed evidence: {tables}, {figures}; numerical checks: verification.json.
- Retrieved evidence: data/pubmed_*.json and XML (titles/abstracts only, queries and retrieval dates).
- Agent inferences: interpretation.json and DRAFT.md; accepted report: RESULTS.md only after review.
- Independent checks: raw Matrix Market sums/detection/mitochondrial fractions and explicit contingency-table ARI.
- User's independent review, agent weakness and unresolved issues: REVIEW.md (pending until acceptance).
- Software tests are not biological validation. One fixed subsample, exploratory markers, no reference labels.

Evidence index: S1 QC/cells/sizes/UMAP/PCA and computation.json; S2 markers/annotations and retrieved sources;
S3 robustness_metrics.csv and cluster_overlaps.csv; S4 the downsample rows and membership;
S5 investigation tables/plot plus the ambiguity discussion. All require scientific review.
''')


def interact(run):
    try:
        _interact(run)
    finally:
        # Status must describe the saved state even when an API call or computation fails.
        if (run / 'state.json').exists():
            audit(run, read_json(run / 'state.json'))


def _interact(run):
    c, state = read_json(run / 'config.json'), read_json(run / 'state.json')
    integrity(run)
    while state['stage'] != 'accepted':
        audit(run, state)
        stage = state['stage']
        if stage == 'plan' and state['response'] is None:
            task = (run / 'PROJECT_PLAN.md').read_text().split('## Task 2 —', 1)[1].split('## Task 3 —', 1)[0]
            request(run, c, state, PLAN_PROMPT + '\n' + json.dumps(c) + '\n' + task, 'plan')
        elif stage == 'qc_compute':
            step(run, '01_qc.py')
            state.update(stage='qc_review', response=None)
            save_json(run / 'state.json', state)
            seal(run)
            continue
        elif stage == 'qc_review' and state['response'] is None:
            tables, _ = folders(run)
            request(run, c, state, QC_PROMPT + '\n' + (tables / 'qc_quantiles.csv').read_text() + '\n' +
                    json.dumps(read_json(run / 'qc_summary.json')), 'qc_review')
        elif stage == 'compute':
            integrity(run)
            step(run, '02_cluster.py')
            step(run, '03_compare.py')
            module('04_verify.py').verify(run, check_manifest=False)
            state.update(stage='interpret', response=None)
            save_json(run / 'state.json', state)
            seal(run)
            continue
        elif stage == 'interpret':
            interpret(run, c, state)
            continue
        elif stage == 'render_review':
            step(run, '03_compare.py', '--annotations')
            state['stage'] = 'review'
            save_json(run / 'state.json', state)
            seal(run)
        audit(run, state)
        print('\n' + (state['response'].get('rationale') or state['response']['report_md']))
        if state['stage'] != 'review':
            print(json.dumps(state['response'], indent=2))
        print('Saved run:', run)
        action = input('Type approve (plan/QC), accept (report), feedback, or quit: ').strip()
        if not action or action.lower() == 'quit':
            print(f'Paused. Resume: python single_cell/run_analysis.py --resume {run}')
            return
        if action.lower() == 'approve' and state['stage'] in ('plan', 'qc_review'):
            event(run, state['stage'] + '_approved', response=state['response'])
            state.update(stage='qc_compute' if state['stage'] == 'plan' else 'compute', response=None)
        elif action.lower() == 'accept' and state['stage'] == 'review':
            integrity(run)
            module('04_verify.py').verify(run)
            notes = {label: input(label + ': ').strip() for label in
                     ('Independent check and result', 'Agent weakness and how evaluated', 'Remaining uncertainties')}
            if not all(notes.values()):
                print('All three review notes are required; report remains a draft.')
                continue
            (run / 'RESULTS.md').write_text(state['response']['report_md'] + '\n')
            (run / 'REVIEW.md').write_text('\n\n'.join(f'## {k}\n\n{v}' for k, v in notes.items()) + '\n')
            event(run, 'report_accepted', review=notes)
            state['stage'] = 'accepted'
        elif action.lower() in ('approve', 'accept'):
            print('That action is not available at this stage.')
            continue
        else:
            event(run, 'user_feedback', stage=state['stage'], text=action)
            if state['stage'] == 'review':
                state.update(stage='interpret', interpretation_revision=state.get('interpretation_revision', 0) + 1,
                             interpretation_feedback=action)
            else:
                instructions = {'plan': PLAN_PROMPT, 'qc_review': QC_PROMPT}[state['stage']]
                request(run, c, state, instructions + '\nRevise the full response using this feedback: ' + action, state['stage'])
        save_json(run / 'state.json', state)
        seal(run)
        audit(run, state)
    print('User-accepted report:', run / 'RESULTS.md')
    print('Review and copy selected evidence into the course submission; score the rubric separately.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--config', type=Path)
    source.add_argument('--resume', type=Path)
    source.add_argument('--verify', type=Path)
    source.add_argument('--repair', type=Path, help='Offline recovery of a stopped interpretation; preserve evidence and make no API calls')
    parser.add_argument('--check', action='store_true', help='Input/dependency preflight only; no analysis or API call')
    args = parser.parse_args()
    if args.check and not args.config:
        parser.error('--check requires --config')
    if args.repair:
        repair(args.repair.resolve())
        return
    if args.verify:
        run = args.verify.resolve()
        integrity(run)
        print(json.dumps(module('04_verify.py').verify(run), indent=2))
        print('Run stage:', read_json(run / 'state.json')['stage'])
        return
    if args.resume:
        run = args.resume.resolve()
        runtime = run / ('runtime' if (run / 'runtime').exists() else 'code')
        for path in runtime.glob('*.py'):
            require((HERE / path.name).exists() and digest(path) == digest(HERE / path.name),
                    f'Code changed since this run. Use {runtime / "run_analysis.py"} --resume, or --repair for a legacy stopped interpretation.')
        current = preflight(read_json(run / 'config.json'))
        require(current['versions'] == read_json(run / 'inputs.json')['versions'], 'Package versions changed; restore the recorded environment')
    else:
        c = load_config(args.config)
        inputs = preflight(c)
        if args.check:
            print(json.dumps(inputs, indent=2))
            print('Input/dependency checks passed; no analysis or Claude call made.')
            return
        require(bool(os.environ.get('ANTHROPIC_API_KEY')), 'Set ANTHROPIC_API_KEY in the shell environment; see README')
        run = create_run(c, inputs)
        print('Run directory:', run, flush=True)
    interact(run)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, ImportError, subprocess.TimeoutExpired) as exc:
        sys.exit(f'Stopped: {exc}')
    except (EOFError, KeyboardInterrupt):
        sys.exit('Paused; resume with the printed run directory.')
