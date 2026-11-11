"""Write results/navdash/truth.jsonl (VPAIR query poses) and put it back into the navdash manifest.

VPAIR is "academic use only", so the repo does not ship its poses. Same writer as
../e2e-visual-nav-vpair/fetch_truth.py (it downloads the VPAIR sample if needed, 0.86 GB).

Usage: .venv/bin/python fetch_truth.py [--data ../relative-nav-benchmark/data/vpair]
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("e2e_fetch_truth", HERE.parent / "e2e-visual-nav-vpair" / "fetch_truth.py")
e2e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e2e)

if __name__ == "__main__":
    e2e.main(default_out=HERE / "results" / "navdash")
