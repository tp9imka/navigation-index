"""Shared, conservative readiness schema and constraint filtering. Stdlib only."""
import math
from pathlib import Path, PurePosixPath

ENUMS = {
    'compute': ('cpu', 'gpu', 'optional-gpu', 'unknown'),
    'hardware': ('none', 'optional', 'required', 'unknown'),
    'offline': ('verified', 'cache-required', 'unknown'),
    'validation': ('integrated', 'components', 'unverified'),
}
BUDGETS = {'max_setup_minutes': 'setup_minutes', 'max_download_mb': 'download_mb'}
FILTER_KEYS = (*ENUMS, 'platform', *BUDGETS)
DEFAULTS = dict(compute='unknown', hardware='unknown', offline='unknown',
                setup_minutes=None, download_mb=None, platforms=[], validation='unverified',
                limitation='', evidence=[])


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def normalize(value, root=None):
    if not isinstance(value, dict):
        raise ValueError('readiness must be an object')
    if set(value) - set(DEFAULTS):
        raise ValueError('unknown readiness fields: ' + ', '.join(sorted(set(value) - set(DEFAULTS))))
    out = {**DEFAULTS, **value}
    for key, choices in ENUMS.items():
        if out[key] not in choices:
            raise ValueError(f'{key} must be one of {choices}')
    for key in BUDGETS.values():
        if out[key] is not None and not number(out[key]):
            raise ValueError(f'{key} must be a finite nonnegative number or null')
    for key in ('platforms', 'evidence'):
        if not isinstance(out[key], list) or not all(isinstance(s, str) and s.strip() for s in out[key]):
            raise ValueError(f'{key} must be a list of nonempty strings')
        out[key] = list(dict.fromkeys(out[key]))
    if not isinstance(out['limitation'], str):
        raise ValueError('limitation must be text')
    for evidence in out['evidence']:
        path = PurePosixPath(evidence)
        if path.is_absolute() or '..' in path.parts or '\\' in evidence:
            raise ValueError('evidence must be a repository-relative path')
        if root is not None:
            target = (Path(root) / evidence).resolve()
            if not target.is_relative_to(Path(root).resolve()) or not target.is_file():
                raise ValueError(f'readiness evidence does not exist: {evidence}')
    if out['offline'] == 'verified' and (not out['evidence'] or not out['limitation'].strip()):
        raise ValueError('verified offline readiness requires evidence and a limitation')
    return out


def apply(nodes, source, root=None):
    if not isinstance(source, dict):
        raise ValueError('readiness source must map record ids to objects')
    if set(source) - set(nodes):
        raise ValueError('readiness references unknown record: ' + ', '.join(sorted(set(source) - set(nodes))))
    for rid, node in nodes.items():
        if node.get('kind') == 'sample' or rid in source or 'readiness' in node:
            node['readiness'] = normalize({**source.get(rid, {}), **node.get('readiness', {})}, root)


def filter_options(options):
    """Validate JSON tool arguments, including zero ceilings; return only active filters."""
    out = {}
    for key in FILTER_KEYS:
        value = options.get(key)
        if value is None:
            continue
        if key in ENUMS and value not in ENUMS[key]:
            raise ValueError(f'{key} must be one of {ENUMS[key]}')
        if key in BUDGETS and not number(value):
            raise ValueError(f'{key} must be a finite nonnegative number')
        if key == 'platform' and (not isinstance(value, str) or not value.strip()):
            raise ValueError('platform must be a nonempty tested OS/architecture label')
        out[key] = value
    return out


def matches(record, options):
    opts = options if isinstance(options, dict) else vars(options)
    rd = record.get('readiness') or DEFAULTS
    for key in ENUMS:
        if opts.get(key) is not None and rd.get(key, DEFAULTS[key]) != opts[key]:
            return False
    if opts.get('platform') is not None and opts['platform'] not in rd.get('platforms', []):
        return False
    for option, field in BUDGETS.items():
        if opts.get(option) is not None:
            value = rd.get(field)
            if value is None or not number(value) or value > opts[option]:
                return False
    return True
