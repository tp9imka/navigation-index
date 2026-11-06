"""Drone detection (drone vs background) and identification (background / Bebop / AR / Phantom)
on a DroneRF low-band subset.

Windows from one segment never straddle train and test. Two splits:
  1. GroupKFold over segments.
  2. Temporal holdout: per class, the highest-numbered HOLDOUT_FRAC of segments are test
     (adjacent segments are consecutive captures, so this is the stricter split).

Usage: python train_rf.py [--data data/dronerf/csv] [--out out/rf_metrics.json] [--save-model out/rf_model.pkl]
"""
import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupKFold

from rf_features import iter_segments, read_segment, segment_features

N_FOLDS = 5
HOLDOUT_FRAC = 0.3
SEED = 0


def build_table(root):
    rows = []
    for path, bui, band, idx, label in iter_segments(root):
        for w, f in enumerate(segment_features(read_segment(path))):
            f.update(bui=bui, band=band, seg_idx=idx, window=w, label=label, segment=f"{bui}{band}_{idx}")
            rows.append(f)
    return pd.DataFrame(rows)


def models():
    return {
        "random_forest": RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                random_state=SEED, n_jobs=-1),
        "hist_gb": HistGradientBoostingClassifier(max_iter=200, class_weight="balanced",
                                                  random_state=SEED),
    }


def report(y, pred, labels):
    rep = classification_report(y, pred, labels=labels, output_dict=True, zero_division=0)
    return {
        "n_windows": int(len(y)),
        "labels": labels,
        "confusion_matrix(rows=true)": confusion_matrix(y, pred, labels=labels).tolist(),
        "balanced_accuracy": round(balanced_accuracy_score(y, pred), 3),
        "per_class": {c: {k: round(rep[c][k], 3) for k in ("precision", "recall", "support")} for c in labels},
    }


def temporal_split(df):
    test = np.zeros(len(df), bool)
    for _, g in df.groupby("label"):
        segs = np.sort(g["seg_idx"].unique())
        cut = segs[int(np.floor(len(segs) * (1 - HOLDOUT_FRAC)))]
        test[g.index[g["seg_idx"] >= cut]] = True
    return ~test, test


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/dronerf/csv")
    ap.add_argument("--out", default="out/rf_metrics.json")
    ap.add_argument("--save-model")
    a = ap.parse_args()

    t0 = time.time()
    df = build_table(a.data)
    t_feat = time.time() - t0
    feats = [c for c in df.columns if c.startswith("band_") or c.startswith("env_") or c == "spectral_flatness"]
    X = df[feats].to_numpy(float)
    groups = df["segment"].to_numpy()
    seg_counts = df.groupby("label")["segment"].nunique().to_dict()
    print(f"{df['segment'].nunique()} segments {seg_counts}, {len(df)} windows, {len(feats)} features, "
          f"extraction {t_feat:.1f}s")
    out = {"segments_per_class": seg_counts, "n_windows": int(len(df)), "n_features": len(feats),
           "feature_extraction_s": round(t_feat, 1), "results": {}}

    tasks = {
        "detect(drone_vs_background)": np.where(df["label"] == "background", "background", "drone"),
        "identify(4_class)": df["label"].to_numpy(),
    }
    tr, te = temporal_split(df)
    for task, y in tasks.items():
        labels = sorted(set(y))
        for name in models():
            t1 = time.time()
            pred = np.empty_like(y)
            for a_idx, b_idx in GroupKFold(n_splits=N_FOLDS).split(X, y, groups):
                pred[b_idx] = models()[name].fit(X[a_idx], y[a_idx]).predict(X[b_idx])
            r_cv = report(y, pred, labels)
            m = models()[name].fit(X[tr], y[tr])
            r_tmp = report(y[te], m.predict(X[te]), labels)
            dt = round(time.time() - t1, 2)
            out["results"][f"{task}/{name}"] = {"grouped_cv": r_cv, "temporal_holdout": r_tmp, "fit_predict_s": dt}
            for split, r in (("cv-by-segment", r_cv), ("temporal-holdout", r_tmp)):
                print(f"[{split:16s}] {task:28s} {name:13s} bal_acc={r['balanced_accuracy']} "
                      f"cm={r['confusion_matrix(rows=true)']} labels={labels}")

    out["total_runtime_s"] = round(time.time() - t0, 1)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2))
    if a.save_model:
        m = models()["random_forest"].fit(X, tasks["identify(4_class)"])
        Path(a.save_model).write_bytes(pickle.dumps({"model": m, "features": feats}))
    print(f"wrote {a.out}; total {out['total_runtime_s']}s")


if __name__ == "__main__":
    main()
