"""
Inferencia estadística para modelos lineales y logísticos.

Produce tablas de:
  - coeficientes
  - intervalos de confianza 95%
  - p-values
  - odds ratios (modelos logísticos)
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")

PROCESSED = Path("data/processed")
OUTPUTS = Path("data/outputs")
OUTPUTS.mkdir(parents=True, exist_ok=True)

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

M2A_FEATURES = [
    "home_xg_for_avg5",
    "away_xg_for_avg5",
    "home_sot_avg5",
    "away_sot_avg5",
    "expected_total_xg",
    "bookmaker_spread_draw",
    "implied_prob_d",
    "away_strength_rating",
]

M2B_FEATURES_PREDICTIVE = [
    "implied_prob_h",
    "implied_prob_d",
    "implied_prob_a",
    "xg_form_diff",
    "points_form_diff",
    "big_chances_diff",
    "home_strength_rating",
]

# Para inferencia multinomial omitimos implied_prob_a:
# implied_prob_h + implied_prob_d + implied_prob_a = 1
M2B_FEATURES_INFERENTIAL = [
    "implied_prob_h",
    "implied_prob_d",
    "xg_form_diff",
    "points_form_diff",
    "big_chances_diff",
    "home_strength_rating",
]


def export_binary_logit():
    df = pd.read_csv(PROCESSED / "features_modelo1.csv")
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    feats = [f for f in M1_FEATURES if f in df.columns]
    df = df.dropna(subset=feats + ["is_goal", "match_date"]).copy()
    X = sm.add_constant(df[feats].astype(float))
    y = df["is_goal"].astype(int)

    model = sm.Logit(y, X).fit(disp=False)
    params = model.params
    conf = model.conf_int()
    pvals = model.pvalues

    out = pd.DataFrame({
        "term": params.index,
        "coef_log_odds": params.values,
        "ci_low_log_odds": conf[0].values,
        "ci_high_log_odds": conf[1].values,
        "p_value": pvals.values,
    })
    out["odds_ratio"] = np.exp(out["coef_log_odds"])
    out["ci_low_or"] = np.exp(out["ci_low_log_odds"])
    out["ci_high_or"] = np.exp(out["ci_high_log_odds"])
    out.to_csv(OUTPUTS / "inference_modelo1_logit.csv", index=False)


def export_linear_ols():
    df = pd.read_csv(PROCESSED / "features_modelo2.csv")
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    feats = [f for f in M2A_FEATURES if f in df.columns]
    df = df.dropna(subset=feats + ["total_goals", "match_date"]).copy()
    X = sm.add_constant(df[feats].astype(float))
    y = df["total_goals"].astype(float)

    model = sm.OLS(y, X).fit()
    params = model.params
    conf = model.conf_int()
    pvals = model.pvalues

    out = pd.DataFrame({
        "term": params.index,
        "coef": params.values,
        "ci_low": conf[0].values,
        "ci_high": conf[1].values,
        "p_value": pvals.values,
    })
    out.to_csv(OUTPUTS / "inference_modelo2a_ols.csv", index=False)


def export_multinomial_logit():
    df = pd.read_csv(PROCESSED / "features_modelo2.csv")
    df["match_date"] = pd.to_datetime(df["match_date"], dayfirst=True, errors="coerce")
    feats = [f for f in M2B_FEATURES_INFERENTIAL if f in df.columns]
    df = df.dropna(subset=feats + ["ftr", "match_date"]).copy()
    feats = [f for f in feats if df[f].nunique(dropna=True) > 1]

    # Baseline alfabético: la clase omitida queda como referencia.
    y = pd.Categorical(df["ftr"], categories=sorted(df["ftr"].unique()))
    X = sm.add_constant(df[feats].astype(float))
    model = sm.MNLogit(y, X).fit(disp=False)

    params = model.params
    pvals = model.pvalues
    conf = model.conf_int()
    class_labels = list(conf.index.get_level_values(0).unique())

    rows = []
    for cls, class_name in zip(params.columns, class_labels):
        cls_params = params[cls]
        cls_pvals = pvals[cls]
        cls_conf = conf.xs(class_name, level=0)
        for term in cls_params.index:
            low = cls_conf.loc[term, "lower"]
            high = cls_conf.loc[term, "upper"]
            coef = cls_params.loc[term]
            rows.append({
                "class_vs_reference": class_name,
                "term": term,
                "coef_log_odds": coef,
                "ci_low_log_odds": low,
                "ci_high_log_odds": high,
                "p_value": cls_pvals.loc[term],
                "odds_ratio": np.exp(coef),
                "ci_low_or": np.exp(low),
                "ci_high_or": np.exp(high),
            })

    pd.DataFrame(rows).to_csv(OUTPUTS / "inference_modelo2b_mnlogit.csv", index=False)


def main():
    export_binary_logit()
    export_linear_ols()
    export_multinomial_logit()
    print("Inferencia guardada en data/outputs/")


if __name__ == "__main__":
    main()
