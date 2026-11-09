#!/bin/sh
# Reproduces results/2026-11-09-smoke-run.txt. Run from the repo root:
#   sh templates/drone-adapter/drivers/results/run_smoke.sh > templates/drone-adapter/drivers/results/2026-11-09-smoke-run.txt 2>&1
# Synthetic input only: fake connection objects, no SDK, no vehicle, no SITL.
D=templates/drone-adapter
echo "# drivers smoke run $(date -u +%Y-%m-%dT%H:%MZ). Synthetic input: fakes, no SDK, no vehicle, no SITL."
for py in python3.12 python3; do
  command -v "$py" >/dev/null 2>&1 || continue
  echo "## $($py --version 2>&1): SDKs importable? (expected: all missing)"
  "$py" -c "import importlib.util as u; [print(m, 'present' if u.find_spec(m) else 'missing') for m in ('mavsdk','pymavlink','cflib','djitellopy')]"
done
echo "## brief check: ast.parse every drivers/*.py; each *Adapter class has pose, ranges, send_setpoint"
python3 - <<'EOF'
import ast, glob
files = sorted(glob.glob('templates/drone-adapter/drivers/*.py'))
for f in files:
    t = ast.parse(open(f).read())
    for c in [n for n in t.body if isinstance(n, ast.ClassDef) and n.name.endswith('Adapter')]:
        m = {n.name for n in c.body if isinstance(n, ast.FunctionDef)}
        print(f, c.name, 'OK' if {'pose', 'ranges', 'send_setpoint'} <= m else 'MISSING')
print('ast.parse ok for', len(files), 'files')
EOF
for py in python3.12 python3; do
  command -v "$py" >/dev/null 2>&1 || continue
  echo "## $($py --version 2>&1): python -m unittest -v (flat folder, run inside $D)"
  (cd "$D" && "$py" -m unittest -v 2>&1)
done
echo "## package mode: folder copied to a temp dir as drone_adapter/"
T=$(mktemp -d)
cp -r "$D" "$T/drone_adapter"
(cd "$T" && python3 -c "
from drone_adapter import Adapter
from drone_adapter.drivers import Px4MavsdkAdapter, ArduPilotPymavlinkAdapter, CrazyflieCflibAdapter, TelloDjitellopyAdapter
print('package import ok; all isinstance Adapter:', all(isinstance(c(), Adapter) for c in (Px4MavsdkAdapter, ArduPilotPymavlinkAdapter, CrazyflieCflibAdapter, TelloDjitellopyAdapter)))
" && python3 -m unittest drone_adapter.drivers.test_drivers_smoke 2>&1)
rm -rf "$T"
