#!/usr/bin/env python3
"""One local-ENU pose stream, replayed from JSONL or optional MCAP. No live control."""
import argparse
import json
import math
from pathlib import Path

SCHEMA = {
    'title': 'NavigationPose', 'type': 'object',
    'required': ['t_ns', 'frame', 'position_m', 'truth_m'],
    'properties': {'t_ns': {'type': 'integer', 'minimum': 0},
                   'frame': {'const': 'local_enu'},
                   **{key: {'type': 'array', 'items': {'type': 'number'}, 'minItems': 3, 'maxItems': 3}
                      for key in ('position_m', 'truth_m')}},
}


def demo_records():
    rows = []
    for i in range(101):
        t = i / 10
        truth = [t, math.sin(t / 2), 0.0]
        rows.append(dict(t_ns=i * 100_000_000, frame='local_enu', truth_m=truth,
                         position_m=[truth[0] + 0.3, truth[1] + 0.4, 0.0]))
    return rows


def metrics(rows):
    if not rows:
        raise ValueError('recording is empty')
    previous, squared = -1, []
    for row in rows:
        stamp = row.get('t_ns')
        if type(stamp) is not int or stamp <= previous:
            raise ValueError('t_ns must be nonnegative integer nanoseconds, strictly increasing')
        previous = stamp
        if row.get('frame') != 'local_enu':
            raise ValueError('frame must be local_enu; convert NED/ECEF/lat-lon explicitly')
        for key in ('position_m', 'truth_m'):
            vec = row.get(key)
            if not isinstance(vec, list) or len(vec) != 3 or not all(
                    type(v) in (int, float) and math.isfinite(v) for v in vec):
                raise ValueError(f'{key} must contain three finite metre values')
        squared.append(sum((a - b) ** 2 for a, b in zip(row['position_m'], row['truth_m'])))
    return dict(epochs=len(rows), duration_s=(rows[-1]['t_ns'] - rows[0]['t_ns']) / 1e9,
                frame='local_enu', position_rmse_m=round(math.sqrt(sum(squared) / len(squared)), 9),
                input='synthetic', alignment='none')


def write_jsonl(path, rows):
    metrics(rows)
    Path(path).write_text(''.join(json.dumps(r, allow_nan=False) + '\n' for r in rows))


def read_jsonl(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    metrics(rows)
    return rows


def write_mcap(path, rows):
    from mcap.writer import CompressionType, Writer
    metrics(rows)
    with Path(path).open('wb') as stream:
        writer = Writer(stream, compression=CompressionType.NONE)
        writer.start(profile='')
        schema = writer.register_schema('NavigationPose', 'jsonschema', json.dumps(SCHEMA).encode())
        channel = writer.register_channel('/navigation/pose', 'json', schema)
        for i, row in enumerate(rows):
            writer.add_message(channel, row['t_ns'], json.dumps(row, allow_nan=False).encode(), row['t_ns'], i)
        writer.finish()


def read_mcap(path):
    from mcap.reader import make_reader
    rows = []
    with Path(path).open('rb') as stream:
        for schema, channel, message in make_reader(stream).iter_messages(topics=['/navigation/pose']):
            if not schema or schema.name != 'NavigationPose' or channel.message_encoding != 'json':
                raise ValueError('unsupported MCAP schema or message encoding')
            row = json.loads(message.data)
            if row['t_ns'] != message.log_time:
                raise ValueError('payload time and MCAP log time disagree')
            rows.append(row)
    metrics(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('out'))
    parser.add_argument('--input', type=Path)
    parser.add_argument('--mcap', action='store_true', help='also verify optional MCAP round trip')
    args = parser.parse_args()
    rows = (read_mcap(args.input) if args.input.suffix == '.mcap' else read_jsonl(args.input)) if args.input else demo_records()
    args.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out / 'poses.jsonl', rows)
    replay = read_jsonl(args.out / 'poses.jsonl')
    if args.mcap:
        write_mcap(args.out / 'poses.mcap', rows)
        if read_mcap(args.out / 'poses.mcap') != rows:
            raise ValueError('MCAP round trip changed the recording')
    result = metrics(replay)
    result['mcap_round_trip'] = 'passed' if args.mcap else 'not-run'
    (args.out / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
