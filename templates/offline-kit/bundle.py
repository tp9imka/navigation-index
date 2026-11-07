#!/usr/bin/env python3
"""Selective offline bundles over prep.py. Run 'plan NAME' before 'prepare NAME'.

prepare downloads online and seals inputs; verify checks those inputs and the runtime;
rehearse runs the sample and checks fresh outputs. --network-disabled is an operator
declaration, not a firewall: disconnect external networking before using it.
"""
import argparse
import datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import time
import zipfile

import prep

KIT = Path(__file__).resolve().parent
REPO = KIT.parent.parent


def read_json(path):
    return json.loads(Path(path).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def selection(definition, manifest):
    items = {i['id']: i for i in manifest['items']}
    items.update({i['id']: i for i in definition.get('extra_items', [])})
    missing = set(definition['prep_items']) - items.keys()
    if missing:
        raise ValueError('unknown preparation items: ' + ', '.join(sorted(missing)))
    return [items[i] for i in definition['prep_items']]


def run_command(argv, cwd, env, folder, commands, timeout=1800):
    started = time.monotonic()
    log = folder / ('command-%02d.log' % len(commands))
    entry = dict(argv=argv, cwd=str(cwd), log=str(log), returncode=None)
    with log.open('w') as output:
        try:
            p = subprocess.run(argv, cwd=cwd, env=env, stdout=output,
                               stderr=subprocess.STDOUT, timeout=timeout)
            entry['returncode'] = p.returncode
        except (OSError, subprocess.TimeoutExpired) as e:
            entry['returncode'] = -1
            output.write(str(e))
    entry['elapsed_s'] = round(time.monotonic() - started, 4)
    commands.append(entry)
    if entry['returncode']:
        excerpt = log.read_text(errors='replace')[-1800:]
        raise ValueError(f"command exited {entry['returncode']}; log {log}\n{excerpt}")


def runtime(python, packages, tools=None):
    code = ('import importlib.metadata as m,json,platform,sys; '
            'print(json.dumps(dict(python=platform.python_version(),'
            'system=platform.system(),machine=platform.machine(),'
            'venv=sys.prefix!=sys.base_prefix,packages={'
            + ','.join(repr(p) + ':m.version(' + repr(p) + ')' for p in packages)
            + '})))')
    p = subprocess.run([python, '-c', code], text=True, capture_output=True, timeout=30)
    if p.returncode:
        raise ValueError('runtime or required package unavailable: ' + p.stderr[-800:])
    result = json.loads(p.stdout)
    result['tools'] = {}
    for name, argv in (tools or {}).items():
        p = subprocess.run(argv, text=True, capture_output=True, timeout=30)
        if p.returncode or not p.stdout.strip():
            raise ValueError(f'runtime tool {name} exited {p.returncode}: {p.stderr[-800:]}')
        result['tools'][name] = dict(argv=argv, stdout=p.stdout.strip(), returncode=p.returncode)
    return result


def inventory(definition, items, repo, cache, pip_platform):
    """Record paths relative to repo/cache, so a copied kit can be checked elsewhere."""
    found = {}
    patterns = [('repo', repo, p) for p in definition.get('repo_inputs', [])]
    patterns += [('cache', cache, p.format(pip_platform=pip_platform))
                 for p in definition.get('cache_inputs', [])]
    state = prep.load_state(str(cache))
    for item in items:
        st = state.get(item['id'], {})
        if st.get('status') != 'done':
            raise ValueError(f"{item['id']}: preparation status is {st.get('status', 'missing')}")
        for rel, expected in st.get('files', {}).items():
            p = cache / rel
            if not p.is_file() or prep.file_hash(p) != expected:
                raise ValueError('missing/corrupt preparation asset: ' + rel)
            patterns.append(('cache', cache, rel))
    for scope, root, pattern in patterns:
        matches = sorted(p for p in root.glob(pattern) if p.is_file())
        if not matches:
            raise ValueError(f'missing prerequisite: {scope}/{pattern}')
        for path in matches:
            if path.stat().st_size == 0:
                raise ValueError('empty prerequisite: ' + str(path))
            found[scope + '/' + path.relative_to(root).as_posix()] = prep.file_hash(path)
    if not found:
        raise ValueError('no known prerequisites: refusing an empty readiness check')
    return found


def unpack(definition, cache):
    for spec in definition.get('unpack', []):
        source = cache / spec['source']
        target = cache / spec['target']
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == '.xz':
            with lzma.open(source) as src, target.open('wb') as dst:
                shutil.copyfileobj(src, dst)
        elif source.suffix == '.zip':
            target.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(source) as archive:
                for name in archive.namelist():
                    if not (target / name).resolve().is_relative_to(target.resolve()):
                        raise ValueError('unsafe archive member: ' + name)
                archive.extractall(target)
        else:
            raise ValueError('unsupported archive: ' + str(source))


def install_runtime(items, python, repo, cache, pip_platform, env, folder, commands):
    if not any(item['type'] == 'pip' for item in items):
        return
    wheels = cache / 'pip' / pip_platform
    for item in items:
        if item['type'] != 'pip':
            continue
        vcs_wheels = []
        for req in item.get('vcs', []):
            name = req.split('@', 1)[0].strip().lower().replace('-', '_')
            sources = list((cache / 'pip' / 'sdist').glob(name + '-*'))
            if not sources:
                raise ValueError('missing cached VCS source: ' + req)
            # Build the already downloaded pinned source without consulting an index.
            run_command([python, '-m', 'pip', 'wheel', '--no-index', '--no-deps',
                         '--no-build-isolation', '--find-links', str(wheels),
                         '--wheel-dir', str(wheels), str(sorted(sources)[-1])],
                        repo, env, folder, commands)
            built = sorted(wheels.glob(name + '-*.whl'))
            if not built:
                raise ValueError('no built wheel for ' + name)
            vcs_wheels.append(str(built[-1]))
        run_command([python, '-m', 'pip', 'install', '--no-index', '--find-links', str(wheels)]
                    + item['requirements'] + vcs_wheels, repo, env, folder, commands)


def validate_outputs(specs, variables, started_ns):
    result = {}
    if not specs:
        raise ValueError('no expected outputs defined')
    for spec in specs:
        path = Path(spec['path'].format(**variables))
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError('missing/empty rehearsal output: ' + str(path))
        if path.stat().st_mtime_ns < started_ns:
            raise ValueError('stale rehearsal output: ' + str(path))
        if spec.get('kind') in ('json', 'replay'):
            obj = read_json(path)
            if not obj:
                raise ValueError('empty JSON output: ' + str(path))
            if spec['kind'] == 'replay':
                rows = obj.get('results', [])
                if sorted(r['file'] for r in rows) != sorted(spec['expected_files']):
                    raise ValueError('replay silently skipped required receiver logs')
                if any(r.get('epochs', 0) <= 0 for r in rows):
                    raise ValueError('replay produced no epochs for a required log')
        result[str(path)] = dict(sha256=prep.file_hash(path), bytes=path.stat().st_size)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['list', 'plan', 'prepare', 'verify', 'rehearse'])
    ap.add_argument('bundle', nargs='?')
    ap.add_argument('--definitions', default=str(KIT / 'bundles.json'))
    ap.add_argument('--manifest', default=str(KIT / 'manifest.json'))
    ap.add_argument('--repo', default=str(REPO))
    ap.add_argument('--cache', default='navkit-cache')
    ap.add_argument('--python', default=sys.executable, help='sample venv interpreter for heavy bundles')
    ap.add_argument('--pip-platform', choices=['macos-arm64', 'linux-amd64', 'linux-arm64'],
                    default={'Darwin-arm64': 'macos-arm64', 'Linux-x86_64': 'linux-amd64',
                             'Linux-aarch64': 'linux-arm64'}.get(platform.system() + '-' + platform.machine()))
    ap.add_argument('--fixture', action='store_true', help='synthetic receiver replay only; never marks the real bundle ready')
    ap.add_argument('--cached-only', action='store_true', help='prepare runtime from an existing cache, with no fetcher or online model warm-up')
    ap.add_argument('--network-disabled', action='store_true',
                    help='attest external networking was disabled by the operator for this rehearsal')
    a = ap.parse_args(argv)
    definitions = read_json(a.definitions)['bundles']
    if a.action == 'list':
        print(json.dumps([{'id': d['id'], 'sample': d['sample']} for d in definitions], indent=2))
        return 0
    matches = [d for d in definitions if d['id'] == a.bundle]
    if not matches:
        ap.error('unknown bundle: ' + str(a.bundle))
    definition = matches[0]
    if a.fixture:
        if 'fixture' not in definition:
            ap.error('this bundle has no fixture mode')
        definition = dict(definition, **definition['fixture'])
    manifest = read_json(a.manifest)
    items = selection(definition, manifest)
    selected_manifest = dict(manifest, items=items)
    tool_hashes = {name: prep.file_hash(KIT / name) for name in ('bundle.py', 'prep.py', 'warm_models.py')}
    fingerprint = digest(dict(definition=definition, manifest=selected_manifest, tools=tool_hashes))
    if a.action == 'plan':
        print(json.dumps(dict(bundle=a.bundle, scope='synthetic-fixture' if a.fixture else 'sample',
            selected_items=[i['id'] for i in items], prerequisites=definition.get('cache_inputs', []),
            known_download_bytes=sum(i.get('size') or 0 for i in items),
            unknown_size_items=[i['id'] for i in items if not i.get('size_complete')],
            weights=definition.get('weights', 'none'), commands=definition['rehearse_commands'],
            offline_ready=False), indent=2))
        return 0
    repo, cache = Path(a.repo).resolve(), Path(a.cache).resolve()
    python = str(Path(a.python).absolute()) if '/' in a.python else shutil.which(a.python)
    if not python:
        raise ValueError('Python interpreter not found')
    folder = cache / 'bundles' / (a.bundle + ('-fixture' if a.fixture else ''))
    folder.mkdir(parents=True, exist_ok=True)
    run = folder / ('run-' + str(time.time_ns()))
    run.mkdir()
    variables = dict(repo=str(repo), cache=str(cache), python=python, run=str(run),
                     kit=str(KIT), pip_platform=a.pip_platform)
    env = dict(os.environ, TORCH_HOME=str(cache / 'torch'), PYTHON=python,
               PIP_NO_INDEX='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    if a.action == 'prepare' and not a.cached_only:
        env.pop('PIP_NO_INDEX', None)  # prep.py must download wheels while online.
        env.pop('HF_HUB_OFFLINE', None)
        env.pop('TRANSFORMERS_OFFLINE', None)
    receipt = dict(bundle=a.bundle, action=a.action, scope='synthetic-fixture' if a.fixture else 'sample',
        at=datetime.datetime.now(datetime.timezone.utc).isoformat(), fingerprint=fingerprint,
        selected_items=[i['id'] for i in items], offline_ready=False, success=False, commands=[],
        network_test='operator-declared-network-disabled' if a.network_disabled else 'not-attested',
        platform=platform.platform(), outputs={}, errors=[])
    try:
        if a.action == 'prepare':
            rt = runtime(python, [])
            if definition.get('requires_venv') and not rt['venv']:
                raise ValueError('use --python with a sample venv; global installs are prohibited')
            selected_path = folder / 'manifest.json'
            selected_path.write_text(json.dumps(selected_manifest, indent=2) + '\n')
            if a.cached_only:
                old = read_json(folder / 'prepare.json')
                if not old.get('success') or old.get('fingerprint') != fingerprint:
                    raise ValueError('cached-only preparation requires a matching successful preparation receipt')
                if inventory(definition, items, repo, cache, a.pip_platform) != old['inputs']:
                    raise ValueError('cached-only inputs differ from the prepared receipt')
            if items and not a.cached_only:
                if any(i['type'] == 'pip' for i in items) and not a.pip_platform:
                    raise ValueError('unknown pip platform; select a supported --pip-platform')
                run_command([sys.executable, str(KIT / 'prep.py'), '--manifest', str(selected_path),
                    '--out', str(cache), '--repo', str(repo), '--profile', 'full', '--pip', shlex.join([python, '-m', 'pip']),
                    '--python-version', '.'.join(rt['python'].split('.')[:2])]
                    + (['--pip-platforms', a.pip_platform] if a.pip_platform else []),
                    repo, env, run, receipt['commands'])
            unpack(definition, cache)
            install_runtime(items, python, repo, cache, a.pip_platform, env, run, receipt['commands'])
            image_items = [i for i in items if i['type'] == 'docker-build']
            if image_items:
                image_files = list(prep.load_state(str(cache)).get(image_items[0]['id'], {}).get('files', {}))
                if len(image_files) != 1:
                    raise ValueError('unknown image archive for ' + image_items[0]['id'])
                variables['image_archive'] = str(cache / image_files[0])
            for command in definition.get('prepare_commands', []):
                if a.cached_only and command.get('online_only'):
                    continue
                run_command([s.format(**variables) for s in command['argv']],
                            command['cwd'].format(**variables), env, run, receipt['commands'])
            receipt['runtime'] = runtime(python, definition.get('packages', []), definition.get('runtime_tools'))
            receipt['inputs'] = inventory(definition, items, repo, cache, a.pip_platform)
            all_items = {i['id']: i for i in manifest['items']}
            for bundle in definitions:
                all_items.update({i['id']: i for i in bundle.get('extra_items', [])})
            prep.write_reports(str(cache), dict(manifest, items=list(all_items.values())),
                               prep.load_state(str(cache)))
        else:
            prepared = read_json(folder / 'prepare.json')
            if not prepared.get('success') or prepared.get('fingerprint') != fingerprint:
                raise ValueError('preparation missing, failed or stale; run prepare again')
            receipt['runtime'] = runtime(python, definition.get('packages', []), definition.get('runtime_tools'))
            if receipt['runtime'] != prepared['runtime']:
                raise ValueError('runtime versions/platform differ from preparation; prepare on this laptop')
            receipt['inputs'] = inventory(definition, items, repo, cache, a.pip_platform)
            if receipt['inputs'] != prepared['inputs']:
                raise ValueError('input hashes changed or assets added/removed; run prepare again')
            if a.action == 'rehearse':
                started_ns = time.time_ns()
                for command in definition['rehearse_commands']:
                    run_command([s.format(**variables) for s in command['argv']],
                                command['cwd'].format(**variables), env, run, receipt['commands'])
                receipt['outputs'] = validate_outputs(definition['expected_outputs'], variables, started_ns)
                receipt['offline_ready'] = bool(a.network_disabled and not a.fixture)
        receipt['success'] = True
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired, zipfile.BadZipFile, lzma.LZMAError) as e:
        receipt['errors'].append(str(e))
    target = folder / (a.action + '.json')
    # Keep every attempt; the latest pointer never hides a failed latest rehearsal.
    (run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    target.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(success=receipt['success'], offline_ready=receipt['offline_ready'],
                          receipt=str(target), errors=receipt['errors']), indent=2))
    return 0 if receipt['success'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
