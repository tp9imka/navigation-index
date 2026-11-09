"""Export preset worlds for the playground as close-area-world/1 JSON (world_json.to_json).

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python site/playground/results/export_presets.py

Writes site/playground/presets/<family>_<index>.json and presets/index.json. Families: the 5
complex families (worlds_complex.py) plus random, u_trap, narrow_gap (world.py), seed 0,
layout 0. Input type: synthetic (seeded generated layouts). No arena file is changed.
"""
import importlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
ARENA = os.path.join(ROOT, "samples", "close-area-arena")
OUT = os.path.normpath(os.path.join(HERE, "..", "presets"))

spec = importlib.util.spec_from_file_location("close_area_arena", os.path.join(ARENA, "__init__.py"),
                                              submodule_search_locations=[ARENA])
pkg = importlib.util.module_from_spec(spec)
sys.modules["close_area_arena"] = pkg
spec.loader.exec_module(pkg)
WJ = importlib.import_module("close_area_arena.world_json")
WC = importlib.import_module("close_area_arena.worlds_complex")

FAMILIES = ("office", "warehouse", "forest", "maze", "glass_office", "random", "u_trap", "narrow_gap")
LABELS = {"office": "Office (rooms + corridor)", "warehouse": "Warehouse (shelf aisles)",
          "forest": "Forest (40-90 poles)", "maze": "Maze (10 x 10 cells)",
          "glass_office": "Glass office (glass panels)", "random": "Random boxes + cylinders",
          "u_trap": "U trap", "narrow_gap": "Narrow gap"}


def main():
    os.makedirs(OUT, exist_ok=True)
    index = []
    for fam in FAMILIES:
        w = WC.make_any_world(fam, 0, 0)
        d = WJ.to_json(w)
        d["index"] = 0                      # world.make_world does not set w.index for the base families
        name = f"{fam}_0.json"
        with open(os.path.join(OUT, name), "w") as fh:
            json.dump(d, fh, separators=(",", ":"))
            fh.write("\n")
        # round trip must hold, as world_json --check does
        assert WJ.to_json(WJ.from_json(d)) == d, f"round trip failed for {fam}"
        index.append({"file": name, "family": fam, "seed": 0, "index": 0, "label": LABELS[fam],
                      "obstacles": len(d["obstacles"])})
        print(name, len(d["obstacles"]), "obstacles")
    with open(os.path.join(OUT, "index.json"), "w") as fh:
        json.dump({"schema": "close-area-world/1", "input": "synthetic",
                   "command": "samples/close-area-arena/.venv/bin/python site/playground/results/export_presets.py",
                   "presets": index}, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
