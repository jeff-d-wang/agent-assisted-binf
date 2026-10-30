"""Task 3: standalone Claude analysis with reviewed local numerical stages."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

# Set these before importing scientific packages, including in direct script execution.
for key in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'task3-matplotlib'))
os.environ.setdefault('NUMBA_CACHE_DIR', str(Path(tempfile.gettempdir()) / 'task3-numba'))
os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir()) / 'task3-xdg'))

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def preflight(config):
    from workflow_common import validate_config, input_paths, digest, versions
    import scanpy
    import leidenalg
    import h5py
    c = validate_config(config)
    return {'sha256': {str(p.resolve()): digest(p) for p in input_paths(c)},
            'versions': versions(), 'python': sys.version, 'seed': c['seed']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check imports and hash inputs; no analysis')
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    sub = parser.add_subparsers(dest='command')
    analyst = sub.add_parser('agent', help='Fresh Claude plan, QC, cluster review and interpretation')
    analyst.add_argument('--resume', type=Path, help='Resume a saved Claude run')
    sub.add_parser('qc', help='Create a new run and compute QC only')
    cluster = sub.add_parser('cluster', help='Apply reviewed QC; produce expression-only results')
    cluster.add_argument('run', type=Path)
    cluster.add_argument('--qc', type=Path, required=True)
    spatial = sub.add_parser('spatial', help='Freeze a resolution before showing its tissue map')
    spatial.add_argument('run', type=Path)
    spatial.add_argument('--resolution', type=float, required=True)
    spatial.add_argument('--reason', required=True, help='Expression-based rationale for freezing this resolution')
    verify = sub.add_parser('verify', help='Independently verify a completed run')
    verify.add_argument('run', type=Path)
    args = parser.parse_args()
    from workflow_common import read_json, require
    if args.command == 'agent' and args.resume:
        run = args.resume.resolve()
        from workflow_common import integrity
        integrity(run)
        # Use the exact runtime saved when this run was created.
        result = subprocess.run([sys.executable, str(run / 'code/agent_workflow.py'), str(run)],
                                env=dict(os.environ, PYTHONHASHSEED='42'))
        raise SystemExit(result.returncode)
    if args.command == 'agent':
        require(bool(os.environ.get('ANTHROPIC_API_KEY')), 'Set ANTHROPIC_API_KEY before starting a Claude run')
        c = read_json(args.config)
        c['input_dir'] = str((ROOT / c['input_dir']).resolve())
        inputs = preflight(c)
        from agent_workflow import start
        run = start(c, inputs, HERE)
        print(f'RUN={run}', flush=True)
        result = subprocess.run([sys.executable, str(run / 'code/agent_workflow.py'), str(run)],
                                env=dict(os.environ, PYTHONHASHSEED='42'))
        raise SystemExit(result.returncode)
    if args.check or args.command == 'qc':
        c = read_json(args.config)
        c['input_dir'] = str((ROOT / c['input_dir']).resolve())
        inputs = preflight(c)
        if args.check:
            import json
            print(json.dumps(inputs, indent=2))
            return
        import importlib.util
        spec = importlib.util.spec_from_file_location('qc_step', HERE / '01_qc.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        run = module.main(c, inputs, HERE)
        print(f'QC complete. Review figures/tables before choosing thresholds.\nRUN={run}')
        return
    require(args.command is not None, 'Choose --check, qc, cluster, spatial, or verify; see --help')
    run = args.run.resolve()
    from workflow_common import integrity
    integrity(run)
    names = {'cluster': '02_cluster.py', 'spatial': '03_spatial.py', 'verify': '04_verify.py'}
    command = [sys.executable, str(run / 'code' / names[args.command]), str(run)]
    if args.command == 'cluster':
        command.extend(['--qc', str(args.qc.resolve())])
    if args.command == 'spatial':
        command.extend(['--resolution', str(args.resolution), '--reason', args.reason])
    env = dict(os.environ, PYTHONHASHSEED='42')
    result = subprocess.run(command, env=env)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
