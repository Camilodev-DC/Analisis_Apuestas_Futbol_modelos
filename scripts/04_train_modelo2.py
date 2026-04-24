"""
Entrena Modelo 2A (regresión total_goals) y Modelo 2B (clasificación ftr).
Input:  data/processed/features_modelo2.csv
Output: models/modelo2a_regresion.joblib
        models/modelo2b_clasificacion.joblib
        data/outputs/metrics_modelo2.json
        pagina_web/graficas/  (residuals, confusion matrix, accuracy vs bet365)
"""
import json
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

PROCESSED = Path("data/processed")
OUTPUTS = Path("data/outputs")
MODELS = Path("models")
GRAFICAS = Path("pagina_web/graficas")
for p in (OUTPUTS, MODELS, GRAFICAS):
    p.mkdir(parents=True, exist_ok=True)

N_SPLITS = 5
WINDOW = 5

# ─── Feature blocks ──────────────────────────────────────────────────────────
REGRESSION_FEATURES = [
    f"home_xg_for_avg{WINDOW}", f"away_xg_for_avg{WINDOW}",
    f"home_sot_avg{WINDOW}", f"away_sot_avg{WINDOW}",
    "expected_total_xg",
    "bookmaker_spread_draw", "implied_prob_d",
    "away_strength_rating",
]

# Mejora M2B: odds + xg_form_diff + points_form_diff + big_chances_diff
CLASSIFICATION_FEATURES = [
    "implied_prob_h", "implied_prob_d", "implied_prob_a",
    "xg_form_diff", "points_form_diff", "big_chances_diff",
    "home_strength_rating",
]

TARGET_REG = "total_goals"
TARGET_CLF = "ftr"


def bet365_accuracy(df: pd.DataFrame) -> float:
    if not {"implied_prob_h", "implied_prob_d", "implied_prob_a"}.issubset(df.columns):
        return float("nan")
    bet_pred = df[["implied_prob_h", "implied_prob_d", "implied_prob_a"]].idxmax(axis=1)
    label_map = {"implied_prob_h": "H", "implied_prob_d": "D", "implied_prob_a": "A"}
    bet_pred = bet_pred.map(label_map)
    return accuracy_score(df[TARGET_CLF], bet_pred)


def cv_regression(df: pd.DataFrame, features: list) -> dict:
    df = df.dropna(subset=features + [TARGET_REG]).sort_values("match_date")
    X = df[features].values
    y = df[TARGET_REG].values
    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    r2s, rmses, maes = [], [], []
    for train_idx, test_idx in tscv.split(X):
        pipe = Pipeline([("scaler", StandardScaler()), ("reg", LinearRegression())])
        pipe.fit(X[train_idx], y[train_idx])
        pred = pipe.predict(X[test_idx])
        r2s.append(r2_score(y[test_idx], pred))
        rmses.append(np.sqrt(mean_squared_error(y[test_idx], pred)))
        maes.append(mean_absolute_error(y[test_idx], pred))
    return {"r2": np.mean(r2s), "rmse": np.mean(rmses), "mae": np.mean(maes)}


def cv_classification(df: pd.DataFrame, features: list) -> dict:
    df = df.dropna(subset=features + [TARGET_CLF]).sort_values("match_date")
    X = df[features].values
    y = df[TARGET_CLF].values
    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    accs, f1s, bet_accs = [], [], []
    for train_idx, test_idx in tscv.split(X):
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs")),
        ])
        pipe.fit(X[train_idx], y[train_idx])
        pred = pipe.predict(X[test_idx])
        accs.append(accuracy_score(y[test_idx], pred))
        f1s.append(f1_score(y[test_idx], pred, average="macro"))
        bet_accs.append(bet365_accuracy(df.iloc[test_idx]))
    return {
        "accuracy": np.mean(accs),
        "f1_macro": np.mean(f1s),
        "bet365_accuracy": np.mean(bet_accs),
    }


def plot_residuals(df: pd.DataFrame, features: list, path: Path):
    df = df.dropna(subset=features + [TARGET_REG]).sort_values("match_date")
    pipe = Pipeline([("scaler", StandardScaler()), ("reg", LinearRegression())])
    cut = int(len(df) * 0.8)
    pipe.fit(df.iloc[:cut][features], df.iloc[:cut][TARGET_REG])
    pred = pipe.predict(df.iloc[cut:][features])
    residuals = df.iloc[cut:][TARGET_REG].values - pred
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(pred, residuals, alpha=0.4, s=20)
    ax.axhline(0, color="red", lw=1)
    ax.set_xlabel("Goles predichos")
    ax.set_ylabel("Residuo")
    ax.set_title("Residuos — Modelo 2A total_goals")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_confusion(df: pd.DataFrame, features: list, path: Path):
    df = df.dropna(subset=features + [TARGET_CLF]).sort_values("match_date")
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs")),
    ])
    cut = int(len(df) * 0.8)
    pipe.fit(df.iloc[:cut][features], df.iloc[:cut][TARGET_CLF])
    pred = pipe.predict(df.iloc[cut:][features])
    labels = ["H", "D", "A"]
    cm = confusion_matrix(df.iloc[cut:][TARGET_CLF], pred, labels=labels)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, colorbar=False)
    ax.set_title("Matriz de Confusión — Modelo 2B ftr")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_accuracy_vs_bet365(model_acc: float, bet_acc: float, path: Path):
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(["Modelo 2B", "Bet365"], [model_acc * 100, bet_acc * 100],
                  color=["steelblue", "coral"])
    ax.bar_label(bars, fmt="%.2f%%", padding=3)
    ax.set_ylim(0, 70)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Accuracy CV — Modelo 2B vs Bet365")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def train_final_model(df: pd.DataFrame, features: list, target: str, kind: str) -> Pipeline:
    df = df.dropna(subset=features + [target])
    estimator = (LinearRegression() if kind == "reg"
                 else LogisticRegression(max_iter=1000, multi_class="multinomial", solver="lbfgs"))
    pipe = Pipeline([("scaler", StandardScaler()), ("est", estimator)])
    pipe.fit(df[features], df[target])
    return pipe


def main():
    df = pd.read_csv(PROCESSED / "features_modelo2.csv", parse_dates=["match_date"])
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["match_date"])

    reg_feats = [f for f in REGRESSION_FEATURES if f in df.columns]
    clf_feats = [f for f in CLASSIFICATION_FEATURES if f in df.columns]
    missing_reg = set(REGRESSION_FEATURES) - set(reg_feats)
    missing_clf = set(CLASSIFICATION_FEATURES) - set(clf_feats)
    if missing_reg:
        print(f"  Regresión: features no encontradas (omitidas): {missing_reg}")
    if missing_clf:
        print(f"  Clasificación: features no encontradas (omitidas): {missing_clf}")

    print("\n--- Modelo 2A — Regresión total_goals ---")
    reg_metrics = cv_regression(df, reg_feats)
    print(f"  R²={reg_metrics['r2']:.4f}  RMSE={reg_metrics['rmse']:.4f}  MAE={reg_metrics['mae']:.4f}")
    r2_status = "✅ > 0" if reg_metrics["r2"] > 0 else "❌ < 0"
    print(f"  {r2_status}")

    print("\n--- Modelo 2B — Clasificación ftr ---")
    clf_metrics = cv_classification(df, clf_feats)
    print(f"  Accuracy={clf_metrics['accuracy']*100:.2f}%  F1-macro={clf_metrics['f1_macro']:.4f}")
    print(f"  Bet365={clf_metrics['bet365_accuracy']*100:.2f}%")
    beats = clf_metrics["accuracy"] > clf_metrics["bet365_accuracy"]
    print(f"  {'✅ Supera Bet365' if beats else '❌ Por debajo de Bet365'}")

    plot_residuals(df, reg_feats, GRAFICAS / "regression_residuals.png")
    plot_confusion(df, clf_feats, GRAFICAS / "confusion_matrix_multiclass.png")
    plot_accuracy_vs_bet365(
        clf_metrics["accuracy"], clf_metrics["bet365_accuracy"],
        GRAFICAS / "accuracy_vs_bet365.png",
    )

    pipe_reg = train_final_model(df, reg_feats, TARGET_REG, "reg")
    pipe_clf = train_final_model(df, clf_feats, TARGET_CLF, "clf")

    joblib.dump(pipe_reg, MODELS / "modelo2a_regresion.joblib")
    joblib.dump(pipe_clf, MODELS / "modelo2b_clasificacion.joblib")

    metrics = {
        "regresion": {k: round(float(v), 4) for k, v in reg_metrics.items()},
        "clasificacion": {k: round(float(v), 4) for k, v in clf_metrics.items()},
        "features_regresion": reg_feats,
        "features_clasificacion": clf_feats,
    }
    (OUTPUTS / "metrics_modelo2.json").write_text(json.dumps(metrics, indent=2))
    print("\nModelos guardados → models/")


if __name__ == "__main__":
    main()
