"""
Bonus — modelos avanzados para comparar contra baseline logístico.

Produce:
  data/outputs/metrics_bonus_modelos_avanzados.json
  data/outputs/bonus_m1_model_compare.csv
  data/outputs/bonus_m2b_model_compare.csv
  pagina_web/graficas/bonus_m1_auc_compare.png
  pagina_web/graficas/bonus_m2b_accuracy_compare.png
  models/modelo1_xg_bonus_random_forest.joblib
"""
import json
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

PROCESSED = Path("data/processed")
OUTPUTS = Path("data/outputs")
MODELS = Path("models")
GRAFICAS = Path("pagina_web/graficas")
for p in (OUTPUTS, MODELS, GRAFICAS):
    p.mkdir(parents=True, exist_ok=True)

M1_FEATURES = [
    "distance_to_goal",
    "angle_to_goal",
    "is_penalty",
    "shot_quality_index",
    "defensive_pressure",
    "buildup_passes",
    "buildup_unique_players",
    "buildup_decentralized",
    "ppda",
    "pass_decentralization",
    "first_touch",
]

M2B_FEATURES = [
    "implied_prob_h",
    "implied_prob_d",
    "implied_prob_a",
    "xg_form_diff",
    "points_form_diff",
    "big_chances_diff",
    "home_strength_rating",
]


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, ylabel: str, path: Path):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(df[x], df[y], color=["#244855", "#8fb9a8", "#e9c46a", "#d97d54"])
    ax.bar_label(bars, fmt="%.4f", padding=3)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(df[y]) * 1.15)
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def evaluate_m1():
    df = pd.read_csv(PROCESSED / "features_modelo1.csv")
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    feats = [f for f in M1_FEATURES if f in df.columns]
    df = df.dropna(subset=feats + ["is_goal", "match_date"]).sort_values("match_date")

    cutoff = df["match_date"].quantile(0.80)
    train = df[df["match_date"] <= cutoff]
    test = df[df["match_date"] > cutoff]
    X_train = train[feats].astype(float)
    y_train = train["is_goal"].astype(int)
    X_test = test[feats].astype(float)
    y_test = test["is_goal"].astype(int)

    models = {
        "logistic_unweighted": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, solver="lbfgs")),
        ]),
        "logistic_balanced": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, solver="lbfgs", class_weight="balanced")),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1,
        ),
        "svm_rbf": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(C=1.0, kernel="rbf", probability=True, random_state=42)),
        ]),
        "mlp": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)),
        ]),
    }

    rows = []
    trained = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        rows.append({
            "model": name,
            "auc": round(float(roc_auc_score(y_test, proba)), 4),
            "brier": round(float(brier_score_loss(y_test, proba)), 4),
            "log_loss": round(float(log_loss(y_test, proba)), 4),
            "mean_pred": round(float(proba.mean()), 4),
        })
        trained[name] = model

    results = pd.DataFrame(rows).sort_values("auc", ascending=False)
    results.to_csv(OUTPUTS / "bonus_m1_model_compare.csv", index=False)
    plot_bar(
        results.sort_values("auc", ascending=False),
        "model",
        "auc",
        "Bonus M1 — AUC por modelo",
        "AUC",
        GRAFICAS / "bonus_m1_auc_compare.png",
    )

    best_name = results.iloc[0]["model"]
    if best_name == "random_forest":
        joblib.dump(trained[best_name], MODELS / "modelo1_xg_bonus_random_forest.joblib")

    return {
        "split": {"n_train": int(len(train)), "n_test": int(len(test))},
        "features": feats,
        "results": rows,
        "best_model_by_auc": best_name,
    }


def bet365_accuracy(df: pd.DataFrame) -> float:
    bet_pred = df[["implied_prob_h", "implied_prob_d", "implied_prob_a"]].idxmax(axis=1)
    bet_pred = bet_pred.map({
        "implied_prob_h": "H",
        "implied_prob_d": "D",
        "implied_prob_a": "A",
    })
    return accuracy_score(df["ftr"], bet_pred)


def evaluate_m2b():
    df = pd.read_csv(PROCESSED / "features_modelo2.csv")
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    feats = [f for f in M2B_FEATURES if f in df.columns]
    df = df.dropna(subset=feats + ["ftr", "match_date"]).sort_values("match_date")

    X = df[feats].astype(float).values
    y = df["ftr"].values
    tscv = TimeSeriesSplit(n_splits=5)

    models = {
        "logistic_multinomial": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs")),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
        ),
        "svm_rbf": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(C=1.0, kernel="rbf", probability=False, random_state=42)),
        ]),
        "mlp": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=700, random_state=42)),
        ]),
    }

    rows = []
    for name, model in models.items():
        accs, f1s, bets = [], [], []
        for train_idx, test_idx in tscv.split(X):
            model.fit(X[train_idx], y[train_idx])
            pred = model.predict(X[test_idx])
            accs.append(accuracy_score(y[test_idx], pred))
            f1s.append(f1_score(y[test_idx], pred, average="macro"))
            bets.append(bet365_accuracy(df.iloc[test_idx]))
        rows.append({
            "model": name,
            "accuracy": round(float(np.mean(accs)), 4),
            "f1_macro": round(float(np.mean(f1s)), 4),
            "bet365_accuracy": round(float(np.mean(bets)), 4),
        })

    results = pd.DataFrame(rows).sort_values("accuracy", ascending=False)
    results.to_csv(OUTPUTS / "bonus_m2b_model_compare.csv", index=False)
    plot_bar(
        results.sort_values("accuracy", ascending=False),
        "model",
        "accuracy",
        "Bonus M2B — Accuracy por modelo",
        "Accuracy",
        GRAFICAS / "bonus_m2b_accuracy_compare.png",
    )

    return {
        "n_matches_used": int(len(df)),
        "features": feats,
        "results": rows,
        "best_model_by_accuracy": results.iloc[0]["model"],
    }


def main():
    metrics = {
        "modelo1_xg_bonus": evaluate_m1(),
        "modelo2b_bonus": evaluate_m2b(),
    }
    (OUTPUTS / "metrics_bonus_modelos_avanzados.json").write_text(
        json.dumps(metrics, indent=2)
    )
    print("Bonus modelos avanzados guardado en data/outputs/ y pagina_web/graficas/")


if __name__ == "__main__":
    main()
