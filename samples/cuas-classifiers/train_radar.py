"""UAV vs bird classification on NRC/Echodyne radar tracks.

Evaluation never mixes a recording session between train and test:
  1. GroupKFold over sessions (Demo-0 R1/R2 files of the same session share a group).
  2. Cross-site: train on Alma 2019 (Demo-0), test on Laval 2020-21 (Demo-2/3/5/6).

Usage: python train_radar.py [--data data/radar] [--out out/radar_metrics.json] [--save-model out/radar_model.pkl]
"""
import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (balanced_accuracy_score, classification_report, confusion_matrix,
                             roc_auc_score)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

from radar_features import FEATURES, KINEMATIC_FEATURES, load_dataset

CLASSES = ["BIRD", "UAV"]
N_FOLDS = 5
SEED = 0
TRAIN_SITE = "Demo-0"


def models():
    return {
        "hist_gb": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05,
                                                  class_weight="balanced", random_state=SEED),
        "random_forest": make_pipeline(SimpleImputer(strategy="median"),
                                       RandomForestClassifier(n_estimators=400, min_samples_leaf=2,
                                                              class_weight="balanced_subsample",
                                                              random_state=SEED, n_jobs=-1)),
        "majority": DummyClassifier(strategy="most_frequent"),
    }


def report(y, pred, proba):
    rep = classification_report(y, pred, labels=[0, 1], target_names=CLASSES, output_dict=True,
                                zero_division=0)
    return {
        "n": int(len(y)),
        "confusion_matrix(rows=true BIRD,UAV)": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        "balanced_accuracy": round(balanced_accuracy_score(y, pred), 3),
        "roc_auc": round(roc_auc_score(y, proba), 3) if len(set(y)) == 2 else None,
        "per_class": {c: {k: round(rep[c][k], 3) for k in ("precision", "recall", "f1-score", "support")}
                      for c in CLASSES},
    }


def grouped_cv(model_fn, X, y, groups):
    pred = np.zeros_like(y)
    proba = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=N_FOLDS).split(X, y, groups):
        m = model_fn()
        m.fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
        proba[te] = m.predict_proba(X[te])[:, 1]
    return report(y, pred, proba)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/radar")
    ap.add_argument("--out", default="out/radar_metrics.json")
    ap.add_argument("--save-model")
    a = ap.parse_args()

    t0 = time.time()
    df = load_dataset(a.data)
    t_feat = time.time() - t0
    df = df[df["label"].isin(CLASSES)].reset_index(drop=True)
    y = (df["label"] == "UAV").to_numpy().astype(int)
    groups = df["session"].to_numpy()
    print(f"{len(df)} tracks ({dict(df['label'].value_counts())}) in {df['session'].nunique()} sessions; "
          f"features {t_feat:.1f}s")

    out = {"n_tracks": int(len(df)), "class_counts": df["label"].value_counts().to_dict(),
           "n_sessions": int(df["session"].nunique()), "feature_extraction_s": round(t_feat, 1),
           "grouped_cv": {}, "cross_site": {}}
    # duration_s partly reflects how long annotators kept a track, so it is ablated too
    feature_sets = {"kinematic+rcs": FEATURES, "kinematic_only": KINEMATIC_FEATURES,
                    "no_duration": [c for c in FEATURES if c != "duration_s"]}
    for fs_name, cols in feature_sets.items():
        X = df[cols].to_numpy(float)
        for name, ctor in models().items():
            t1 = time.time()
            r = grouped_cv(lambda: models()[name], X, y, groups)
            r["fit_predict_s"] = round(time.time() - t1, 2)
            out["grouped_cv"][f"{name}/{fs_name}"] = r
            print(f"[cv {N_FOLDS}-fold by session] {name:14s} {fs_name:14s} bal_acc={r['balanced_accuracy']} "
                  f"auc={r['roc_auc']} UAV P/R={r['per_class']['UAV']['precision']}/{r['per_class']['UAV']['recall']} "
                  f"cm={r['confusion_matrix(rows=true BIRD,UAV)']}")

    tr = (df["folder"] == TRAIN_SITE).to_numpy()
    X = df[FEATURES].to_numpy(float)
    for name in ("hist_gb", "random_forest"):
        m = models()[name].fit(X[tr], y[tr])
        r = report(y[~tr], m.predict(X[~tr]), m.predict_proba(X[~tr])[:, 1])
        out["cross_site"][name] = r
        print(f"[train Alma 2019 => test Laval 2020-21] {name:14s} bal_acc={r['balanced_accuracy']} "
              f"auc={r['roc_auc']} UAV P/R={r['per_class']['UAV']['precision']}/{r['per_class']['UAV']['recall']} "
              f"cm={r['confusion_matrix(rows=true BIRD,UAV)']}")

    rf = models()["random_forest"].fit(X, y)
    imp = rf[-1].feature_importances_
    out["rf_top_features"] = {FEATURES[i]: round(float(imp[i]), 3) for i in np.argsort(imp)[::-1][:8]}
    print("RF top features:", out["rf_top_features"])
    out["total_runtime_s"] = round(time.time() - t0, 1)

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=2))
    if a.save_model:
        # trained on Alma only, so cuas_cot.py demos on Laval sessions are out-of-sample
        hgb = models()["hist_gb"].fit(X[tr], y[tr])
        Path(a.save_model).write_bytes(pickle.dumps({"model": hgb, "features": FEATURES, "classes": CLASSES,
                                                       "trained_on": TRAIN_SITE}))
    print(f"wrote {a.out}; total {out['total_runtime_s']}s")


if __name__ == "__main__":
    main()
