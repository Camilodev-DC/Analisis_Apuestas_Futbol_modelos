"""
Entrena Modelo 1 — xG por tiro (regresión logística).
Input:  data/processed/features_modelo1.csv
Output: models/modelo1_xg.joblib
        data/outputs/metrics_modelo1.json
        pagina_web/graficas/  (ROC, calibration, VIF)
"""
import json
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibrationDisplay, calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")

PROCESSED = Path("data/processed")
OUTPUTS = Path("data/outputs")
MODELS = Path("models")
GRAFICAS = Path("pagina_web/graficas")
for p in (OUTPUTS, MODELS, GRAFICAS):
    p.mkdir(parents=True, exist_ok=True)

# Mejora: is_penalty + shot_quality_index + is_in_area + is_central añadidos
FEATURES = [
    "distance_to_goal", "angle_to_goal",
    "is_penalty", "shot_quality_index",
    "defensive_pressure", "buildup_passes", "buildup_unique_players",
    "buildup_decentralized", "ppda", "pass_decentralization",
    "first_touch",
]
TARGET = "is_goal"


def temporal_split(df: pd.DataFrame, test_frac: float = 0.20):
    df = df.sort_values("match_date")
    cutoff = df["match_date"].quantile(1 - test_frac)
    return df[df["match_date"] <= cutoff], df[df["match_date"] > cutoff]


def check_vif(X: pd.DataFrame, threshold: float = 5.0) -> pd.DataFrame:
    X = X.astype(float)
    vif = pd.DataFrame({"feature": X.columns})
    vif["VIF"] = [
        variance_inflation_factor(X.values, i) for i in range(X.shape[1])
    ]
    over = vif[vif["VIF"] > threshold]
    if not over.empty:
        print(f"  AVISO VIF > {threshold}:\n{over.to_string(index=False)}")
    return vif


def train_variant(X_train, y_train, class_weight=None) -> Pipeline:
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=1000, class_weight=class_weight,
            solver="lbfgs", C=1.0,
        )),
    ])
    pipe.fit(X_train, y_train)
    return pipe


def plot_roc(fpr, tpr, auc, path: Path):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, lw=2, label=f"AUC = {auc:.4f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title("ROC — Modelo 1 xG")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_calibration(y_true, y_prob, path: Path):
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=10)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(prob_pred, prob_true, "s-", label="Modelo 1")
    ax.plot([0, 1], [0, 1], "k--", label="Perfecta")
    ax.set_xlabel("xG predicho (media bin)")
    ax.set_ylabel("Tasa de gol real")
    ax.set_title("Calibración — Modelo 1 xG")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    df = pd.read_csv(PROCESSED / "features_modelo1.csv", parse_dates=["match_date"])
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["match_date"])

    features_available = [f for f in FEATURES if f in df.columns]
    missing = set(FEATURES) - set(features_available)
    if missing:
        print(f"  Features no encontradas (se omiten): {missing}")

    df = df.dropna(subset=features_available + [TARGET])
    train, test = temporal_split(df)

    X_train = train[features_available].astype(float)
    y_train = train[TARGET]
    X_test = test[features_available].astype(float)
    y_test = test[TARGET]

    print(f"Train: {len(train):,} tiros | Test: {len(test):,} tiros")

    print("\n--- VIF (train) ---")
    vif_df = check_vif(X_train)
    vif_df.to_csv(OUTPUTS / "vif_modelo1.csv", index=False)

    pipe_uw = train_variant(X_train, y_train, class_weight=None)
    pipe_bal = train_variant(X_train, y_train, class_weight="balanced")

    for name, pipe in [("unweighted", pipe_uw), ("balanced", pipe_bal)]:
        proba = pipe.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, proba)
        bs = brier_score_loss(y_test, proba)
        ll = log_loss(y_test, proba)
        xg_mean = proba.mean()
        goal_rate = y_test.mean()
        ratio = xg_mean / goal_rate
        print(f"\n[{name}] AUC={auc:.4f}  Brier={bs:.4f}  LogLoss={ll:.4f}")
        print(f"  xG medio={xg_mean:.4f}  gol_real={goal_rate:.4f}  ratio={ratio:.3f}")

    best_pipe = pipe_uw
    y_prob = best_pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)

    fpr, tpr, _ = roc_curve(y_test, y_prob)
    plot_roc(fpr, tpr, auc, GRAFICAS / "roc_modelo1.png")
    plot_calibration(y_test, y_prob, GRAFICAS / "calibration_modelo1.png")

    metrics = {
        "auc_roc": round(float(auc), 4),
        "brier_score": round(float(brier_score_loss(y_test, y_prob)), 4),
        "log_loss": round(float(log_loss(y_test, y_prob)), 4),
        "xg_mean": round(float(y_prob.mean()), 4),
        "goal_rate": round(float(y_test.mean()), 4),
        "features_used": features_available,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
    }
    (OUTPUTS / "metrics_modelo1.json").write_text(json.dumps(metrics, indent=2))
    joblib.dump(best_pipe, MODELS / "modelo1_xg.joblib")

    print(f"\nModelo guardado → models/modelo1_xg.joblib")
    print(f"AUC final: {auc:.4f}  {'✅ > 0.78' if auc > 0.78 else '❌ < 0.78'}")


if __name__ == "__main__":
    main()
