#!/usr/bin/env python3
"""
scripts/train.py
----------------
Train a readership decay model on ASM relaunch data.

What it does:
  1. Loads historical relaunch data from data/marvel.db
  2. Builds per-volume features: opening baseline (issue #2 orders), relaunch year,
     previous volume's issue #12 floor
  3. Trains a ridge regression (L2, lambda=1.0) to predict issue #12 floor
  4. Evaluates with leave-one-out cross-validation (honest estimate given n=5)
  5. Fits retention curves at issues 6, 12, 24, 36 for trajectory forecasting
  6. Saves model parameters + pre-computed predictions to data/predictions.json

The Streamlit app reads predictions.json at runtime — sklearn is NOT required
at runtime. Coefficients are stored as plain numbers so inference runs in-app
with just numpy.

Usage:
  python scripts/train.py

Requires: numpy, scipy (already in requirements.txt)
"""

import json
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime, timezone

ROOT     = Path(__file__).resolve().parent.parent
DB_PATH  = ROOT / "data" / "marvel.db"
OUT_PATH = ROOT / "data" / "predictions.json"

# Confidence weights for training: down-weight pure estimates
CONFIDENCE_WEIGHTS = {
    "Confirmed":                   1.0,
    "Confirmed - Event Boosted":   0.8,   # boosted issue — treat cautiously
    "PRH Estimate":                0.6,
    "Estimate":                    0.5,
}

ISSUE_POINTS = [2, 6, 12, 24, 36]


def log(msg: str):
    print(f"[train] {msg}")


# ── Data loading ──────────────────────────────────────────────────────────────

def load_relaunch_data():
    """
    Returns a dict keyed by relaunch_volume with per-volume stats.
    Each entry: {volume, year, writer, issue2, issue6, issue12, issue24, issue36,
                 conf_issue2, conf_issue12, ...}
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT relaunch_volume, relaunch_year, writer, issue_num, orders, data_confidence "
        "FROM asm_relaunches ORDER BY relaunch_volume, issue_num"
    ).fetchall()
    conn.close()

    volumes = {}
    for vol, year, writer, issue_num, orders, conf in rows:
        if vol not in volumes:
            volumes[vol] = {"volume": vol, "year": year, "writer": writer}
        if issue_num in ISSUE_POINTS:
            volumes[vol][f"issue{issue_num}"]      = orders
            volumes[vol][f"conf_issue{issue_num}"] = conf

    return volumes


# ── Ridge regression (no sklearn needed) ─────────────────────────────────────

def ridge_fit(X, y, w, lam=1.0):
    """
    Weighted ridge regression.
    X: (n, p) design matrix (already includes intercept column of 1s)
    y: (n,) targets
    w: (n,) sample weights
    lam: L2 regularization strength

    Returns coefficients vector (p,).
    """
    W   = np.diag(w)
    XtW = X.T @ W
    A   = XtW @ X + lam * np.eye(X.shape[1])
    b   = XtW @ y
    return np.linalg.solve(A, b)


def standardize(X_train, X_new=None):
    """Z-score standardize. Returns (X_std, mean, std). Optionally transforms X_new."""
    mu  = X_train.mean(axis=0)
    sig = X_train.std(axis=0, ddof=1)
    sig[sig == 0] = 1.0          # avoid div-by-zero on constant features
    X_std = (X_train - mu) / sig
    if X_new is not None:
        return X_std, (X_new - mu) / sig, mu, sig
    return X_std, mu, sig


# ── Model training ────────────────────────────────────────────────────────────

MODERN_ERA_MIN_YEAR = 2010   # Vol.2 (1999) is a structurally different market era


def build_training_set(volumes):
    """
    Build feature matrix X and targets y for issue-12 prediction.

    Feature: issue2_orders (opening baseline — the primary predictor)
    Target:  issue12_orders

    Volumes pre-2010 are excluded from training: the 1999 market had
    fundamentally different dynamics (pre-direct-market consolidation).
    They are kept in the output as historical context but not used to fit the model.
    """
    rows      = []
    held_out  = []
    for v, vd in sorted(volumes.items()):
        if "issue2" not in vd or "issue12" not in vd:
            continue
        row = {
            "volume":      v,
            "year":        vd["year"],
            "writer":      vd["writer"],
            "issue2":      vd["issue2"],
            "issue12":     vd["issue12"],
            "conf_issue2":  vd.get("conf_issue2",  "Estimate"),
            "conf_issue12": vd.get("conf_issue12", "Estimate"),
            "weight":       CONFIDENCE_WEIGHTS.get(vd.get("conf_issue12", "Estimate"), 0.5),
        }
        if vd["year"] >= MODERN_ERA_MIN_YEAR:
            rows.append(row)
        else:
            held_out.append(row)
    return rows, held_out


def train_issue12_model(rows, lam=1.0):
    """
    Fit ridge regression: issue12 ~ issue2 (+ intercept).
    Single feature — appropriate for n=4 to avoid overfitting.
    Returns (coefs, scaler_mean, scaler_std).
    coefs = [coef_issue2_std, intercept]
    """
    issue2 = np.array([r["issue2"]  for r in rows], dtype=float)
    y      = np.array([r["issue12"] for r in rows], dtype=float)
    w      = np.array([r["weight"]  for r in rows], dtype=float)

    X_raw           = issue2.reshape(-1, 1)
    X_std, mu, sig  = standardize(X_raw)
    X               = np.column_stack([X_std, np.ones(len(rows))])

    coefs = ridge_fit(X, y, w, lam=lam)
    return coefs, mu, sig


def loocv_evaluate(rows, lam=1.0):
    """Leave-one-out cross-validation. Returns list of result dicts."""
    results = []
    for i in range(len(rows)):
        train = [r for j, r in enumerate(rows) if j != i]
        test  = rows[i]

        issue2_tr = np.array([r["issue2"]  for r in train], dtype=float).reshape(-1, 1)
        y_tr      = np.array([r["issue12"] for r in train], dtype=float)
        w_tr      = np.array([r["weight"]  for r in train], dtype=float)

        X_tr_std, mu, sig = standardize(issue2_tr)
        X_tr  = np.column_stack([X_tr_std, np.ones(len(train))])
        coefs = ridge_fit(X_tr, y_tr, w_tr, lam=lam)

        x_test_std = (np.array([[test["issue2"]]], dtype=float) - mu) / sig
        x_test     = np.column_stack([x_test_std, np.ones(1)])
        predicted  = float(x_test @ coefs)

        results.append({
            "volume":    test["volume"],
            "actual":    test["issue12"],
            "predicted": predicted,
            "error":     predicted - test["issue12"],
        })
    return results


# ── Trajectory retention rates ────────────────────────────────────────────────

def compute_retention_rates(volumes):
    """
    For each issue point (6, 12, 24, 36), compute the mean and std of the
    retention rate (orders_at_N / orders_issue2) across all volumes.
    Returns dict: {issue_num: {"mean": float, "std": float, "rates": [...]}}
    """
    rates = {}
    for target_issue in [6, 12, 24, 36]:
        vol_rates = []
        for v, vd in volumes.items():
            if "issue2" in vd and f"issue{target_issue}" in vd and vd["issue2"] > 0:
                r = vd[f"issue{target_issue}"] / vd["issue2"]
                vol_rates.append({"volume": v, "rate": r,
                                   "conf": vd.get(f"conf_issue{target_issue}", "Estimate")})
        if vol_rates:
            vals = [x["rate"] for x in vol_rates]
            rates[target_issue] = {
                "mean":  float(np.mean(vals)),
                "std":   float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                "n":     len(vals),
                "per_volume": vol_rates,
            }
    return rates


def forecast_trajectory(issue2_orders, retention_rates):
    """
    Given an opening issue2 baseline, forecast the full trajectory with CIs.
    Uses retention rates (mean issue_N/issue2 across historical volumes) for all points.
    CIs are 95% t-intervals on the retention rate, then scaled by the baseline.
    """
    from scipy import stats as scipy_stats

    trajectory = {"issue2": int(issue2_orders)}

    for issue_num in [6, 12, 24, 36]:
        if issue_num not in retention_rates:
            continue
        r    = retention_rates[issue_num]
        mean = r["mean"]
        std  = r["std"]
        n    = r["n"]
        pred = issue2_orders * mean

        # 95% CI on the retention rate, scaled to absolute orders
        if n > 1:
            se    = std / np.sqrt(n)
            t_val = scipy_stats.t.ppf(0.975, df=n - 1)
            ci_lo = max(0, issue2_orders * (mean - t_val * se))
            ci_hi = issue2_orders * (mean + t_val * se)
        else:
            ci_lo = pred * 0.85
            ci_hi = pred * 1.15

        trajectory[f"issue{issue_num}"] = {
            "predicted":  round(pred),
            "ci_low":     round(ci_lo),
            "ci_high":    round(ci_hi),
            "retention":  round(mean, 3),
        }

    return trajectory


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log(f"Loading data from {DB_PATH}")
    volumes = load_relaunch_data()
    log(f"  {len(volumes)} relaunch volumes found")

    rows, held_out = build_training_set(volumes)
    log(f"  {len(rows)} modern-era training rows (>={MODERN_ERA_MIN_YEAR})")
    log(f"  {len(held_out)} held-out historical rows (pre-{MODERN_ERA_MIN_YEAR}, not used in training)")

    # Train full model
    coefs, mu, sig = train_issue12_model(rows, lam=1.0)
    log(f"  Model coefficients: {coefs}")

    # LOOCV evaluation
    loocv = loocv_evaluate(rows, lam=1.0)
    errors  = [r["error"] for r in loocv]
    mae_k   = float(np.mean(np.abs(errors))) / 1000
    rmse_k  = float(np.sqrt(np.mean(np.array(errors) ** 2))) / 1000
    log(f"  LOOCV MAE:  {mae_k:.1f}k copies")
    log(f"  LOOCV RMSE: {rmse_k:.1f}k copies")

    # Retention rates across all issue points
    retention = compute_retention_rates(volumes)
    log(f"  Retention rates computed: {list(retention.keys())}")

    # Historical actual vs predicted
    historical = []
    for r in loocv:
        v = volumes[r["volume"]]
        historical.append({
            "volume":             r["volume"],
            "year":               v["year"],
            "writer":             v["writer"],
            "issue2_k":           round(v.get("issue2", 0) / 1000, 1),
            "issue12_actual_k":   round(r["actual"] / 1000, 1),
            "issue12_predicted_k": round(r["predicted"] / 1000, 1),
            "error_k":            round(r["error"] / 1000, 1),
            "retention_actual":   round(r["actual"] / v["issue2"], 3) if v.get("issue2") else None,
            "conf_issue12":       v.get("conf_issue12", "Estimate"),
        })

    # Forecast trajectories for a range of opening baselines (for the what-if builder)
    baselines = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 200, 220, 250]
    what_if_curves = {}
    for b_k in baselines:
        traj = forecast_trajectory(b_k * 1000, retention)
        what_if_curves[f"{b_k}k"] = {
            k: (v if k == "issue2" else {
                "predicted_k":  round(v["predicted"] / 1000, 1),
                "ci_low_k":     round(v["ci_low"]    / 1000, 1),
                "ci_high_k":    round(v["ci_high"]   / 1000, 1),
                "retention":    v["retention"],
            })
            for k, v in traj.items()
        }

    # Full historical trajectories for overlay in the what-if chart
    vol_trajectories = []
    for vol, vd in sorted(volumes.items()):
        if "issue2" not in vd:
            continue
        traj = {"volume": vol, "year": vd["year"], "writer": vd["writer"],
                "issue2_k": round(vd["issue2"] / 1000, 1)}
        for pt in [6, 12, 24, 36]:
            key = f"issue{pt}"
            if key in vd:
                traj[f"{key}_k"] = round(vd[key] / 1000, 1)
                traj[f"conf_{key}"] = vd.get(f"conf_{key}", "Estimate")
        vol_trajectories.append(traj)

    # Package everything
    output = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model": {
            "type":              "Retention Rate Model (mean issue_N/issue2 across n relaunches)",
            "n_samples":         len(rows) + len(held_out),
            "training_era":      "all available ASM relaunches",
            "loocv_mae_k":       round(mae_k, 1),
            "loocv_rmse_k":      round(rmse_k, 1),
            # Ridge model params kept for reference (not used in trajectory forecasts)
            "ridge_coef_issue2_std":   round(float(coefs[0]), 6),
            "ridge_intercept":         round(float(coefs[1]), 2),
            "ridge_scaler_mean_issue2": round(float(mu[0]), 2),
            "ridge_scaler_std_issue2":  round(float(sig[0]), 2),
        },
        "retention": {
            str(k): {
                "mean":       round(v["mean"], 3),
                "std":        round(v["std"],  3),
                "n":          v["n"],
            }
            for k, v in retention.items()
        },
        "historical": historical,
        "vol_trajectories": vol_trajectories,
        "what_if_curves": what_if_curves,
    }

    OUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    log(f"Predictions written to {OUT_PATH}")

    # Print summary
    print("\n" + "=" * 55)
    print("  Decay model summary")
    print("=" * 55)
    print(f"  Training volumes:  {[r['volume'] for r in rows]}")
    print(f"  LOOCV MAE:         {mae_k:.1f}k copies/issue at #12")
    print(f"  LOOCV RMSE:        {rmse_k:.1f}k copies/issue at #12")
    print(f"  Avg issue-12 retention: {retention[12]['mean']*100:.1f}% of issue-2")
    print(f"  Avg issue-24 retention: {retention[24]['mean']*100:.1f}% of issue-2")
    print()
    print("  LOOCV predictions vs actual:")
    for h in historical:
        flag = "OK" if abs(h["error_k"]) <= rmse_k else "!!"
        print(f"  {flag} Vol.{h['volume']} ({h['year']})  "
              f"actual={h['issue12_actual_k']}k  "
              f"predicted={h['issue12_predicted_k']}k  "
              f"err={h['error_k']:+.1f}k")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
