"""
Feature engineering para Modelo 2 — predictor de partido.
Input:  data/raw/matches.csv
        data/processed/features_modelo1.csv  (xG por tiro → rolling por partido)
Output: data/processed/features_modelo2.csv
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

WINDOW = 5


def load_matches(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.rename(columns={
        "id": "match_id",
        "date": "match_date",
        "hs": "home_shots",
        "as_": "away_shots",
        "hst": "home_shots_target",
        "ast": "away_shots_target",
    })
    df = df.sort_values("match_date").reset_index(drop=True)
    return df


def compute_match_xg(events_path: Path) -> pd.DataFrame:
    if not events_path.exists():
        return pd.DataFrame(columns=["match_id", "home_xg", "away_xg"])
    ev = pd.read_csv(events_path)
    team_col = "team" if "team" in ev.columns else "team_name" if "team_name" in ev.columns else None
    xg_col = "xg_pred" if "xg_pred" in ev.columns else "xg_provisional" if "xg_provisional" in ev.columns else None
    required = {"match_id"}
    if team_col is None or xg_col is None or not required.issubset(ev.columns):
        return pd.DataFrame(columns=["match_id", "home_xg", "away_xg"])

    if team_col != "team":
        ev = ev.rename(columns={team_col: "team"})
    if xg_col != "xg_pred":
        ev = ev.rename(columns={xg_col: "xg_pred"})
    agg = ev.groupby(["match_id", "team"])["xg_pred"].sum().unstack(fill_value=0)
    agg = agg.reset_index()
    if {"match_id", "home_team", "away_team"}.issubset(pd.read_csv(RAW / "matches.csv", nrows=1).columns | {"match_id"}):
        pass
    return agg


def rolling_team_stats(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    stats_home = df[["match_date", "home_team", "fthg", "ftag",
                      "home_shots", "home_shots_target",
                      "home_xg", "away_xg"]].copy()
    stats_home.columns = ["match_date", "team", "gf", "ga",
                           "shots_f", "sot_f", "xg_f", "xg_a"]
    stats_home["pts"] = np.where(df["ftr"] == "H", 3, np.where(df["ftr"] == "D", 1, 0))

    stats_away = df[["match_date", "away_team", "ftag", "fthg",
                      "away_shots", "away_shots_target",
                      "away_xg", "home_xg"]].copy()
    stats_away.columns = ["match_date", "team", "gf", "ga",
                           "shots_f", "sot_f", "xg_f", "xg_a"]
    stats_away["pts"] = np.where(df["ftr"] == "A", 3, np.where(df["ftr"] == "D", 1, 0))

    all_stats = pd.concat([stats_home, stats_away]).sort_values("match_date")

    def roll(grp):
        num_cols = ["gf", "ga", "shots_f", "sot_f", "xg_f", "xg_a", "pts"]
        rolled = grp[num_cols].shift(1).rolling(window, min_periods=1).mean()
        rolled.columns = [f"{c}_avg{window}" for c in num_cols]
        return pd.concat([grp.reset_index(drop=True), rolled.reset_index(drop=True)], axis=1)

    return all_stats.groupby("team", group_keys=False).apply(roll)


def add_rolling_to_matches(df: pd.DataFrame, rolled: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    def get_rolling(team_col, prefix):
        team_stats = rolled[["match_date", "team",
                              f"gf_avg{window}", f"ga_avg{window}",
                              f"shots_f_avg{window}", f"sot_f_avg{window}",
                              f"xg_f_avg{window}", f"xg_a_avg{window}",
                              f"pts_avg{window}"]].copy()
        team_stats.columns = ["match_date", team_col,
                               f"{prefix}_gf_avg{window}", f"{prefix}_ga_avg{window}",
                               f"{prefix}_shots_avg{window}", f"{prefix}_sot_avg{window}",
                               f"{prefix}_xg_for_avg{window}", f"{prefix}_xg_ag_avg{window}",
                               f"{prefix}_pts_avg{window}"]
        return df.merge(team_stats, on=["match_date", team_col], how="left")

    df = get_rolling("home_team", "home")
    df = get_rolling("away_team", "away")
    return df


def add_differential_features(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    df["xg_form_diff"] = df[f"home_xg_for_avg{window}"] - df[f"away_xg_for_avg{window}"]
    df["points_form_diff"] = df[f"home_pts_avg{window}"] - df[f"away_pts_avg{window}"]
    df["sot_diff"] = df[f"home_sot_avg{window}"] - df[f"away_sot_avg{window}"]
    df["gf_diff"] = df[f"home_gf_avg{window}"] - df[f"away_gf_avg{window}"]
    df["expected_total_xg"] = df[f"home_xg_for_avg{window}"] + df[f"away_xg_for_avg{window}"]
    return df


def add_strength_ratings(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    for side in ("home", "away"):
        att = df[f"{side}_gf_avg{window}"].fillna(0)
        deff = 1 / (df[f"{side}_ga_avg{window}"].fillna(1) + 0.1)
        df[f"{side}_strength_rating"] = (att + deff) / 2
    return df


def add_implied_probs(df: pd.DataFrame) -> pd.DataFrame:
    for col, target in [("b365h", "h"), ("b365d", "d"), ("b365a", "a")]:
        if col in df.columns:
            df[f"implied_prob_{target}"] = 1 / df[col]
    if all(f"implied_prob_{t}" in df.columns for t in ("h", "d", "a")):
        total = df["implied_prob_h"] + df["implied_prob_d"] + df["implied_prob_a"]
        for t in ("h", "d", "a"):
            df[f"implied_prob_{t}"] /= total
        df["bookmaker_spread_draw"] = df["b365h"] - df["b365a"] if "b365h" in df.columns else 0.0
    return df


def add_big_chances_diff(df: pd.DataFrame) -> pd.DataFrame:
    if "home_big_chances" in df.columns and "away_big_chances" in df.columns:
        df["big_chances_diff"] = df["home_big_chances"] - df["away_big_chances"]
    else:
        df["big_chances_diff"] = 0.0
    return df


def add_referee_features(df: pd.DataFrame) -> pd.DataFrame:
    if "referee" not in df.columns:
        return df
    ref_stats = df.groupby("referee").agg(
        ref_yellow_avg=("hy", "mean"),
        ref_red_avg=("hr", "mean"),
        ref_foul_avg=("hf", "mean"),
    ).reset_index()
    return df.merge(ref_stats, on="referee", how="left")


def main():
    df = load_matches(RAW / "matches.csv")
    xg_match = compute_match_xg(PROCESSED / "features_modelo1.csv")
    if not xg_match.empty and "match_id" in df.columns:
        match_teams = df[["match_id", "home_team", "away_team"]].copy()
        xg_long = xg_match.melt(id_vars="match_id", var_name="team", value_name="xg")
        if xg_long["team"].isin(match_teams["home_team"]).any() or xg_long["team"].isin(match_teams["away_team"]).any():
            home_xg = (
                xg_long.merge(match_teams[["match_id", "home_team"]], left_on=["match_id", "team"], right_on=["match_id", "home_team"], how="inner")
                [["match_id", "xg"]]
                .rename(columns={"xg": "home_xg"})
            )
            away_xg = (
                xg_long.merge(match_teams[["match_id", "away_team"]], left_on=["match_id", "team"], right_on=["match_id", "away_team"], how="inner")
                [["match_id", "xg"]]
                .rename(columns={"xg": "away_xg"})
            )
            df = df.merge(home_xg, on="match_id", how="left").merge(away_xg, on="match_id", how="left")
        else:
            xg_cols = [c for c in xg_match.columns if c != "match_id"]
            if len(xg_cols) >= 2:
                df = df.merge(
                    xg_match.rename(columns={xg_cols[0]: "away_xg", xg_cols[1]: "home_xg"})[["match_id", "home_xg", "away_xg"]],
                    on="match_id",
                    how="left",
                )

    if "home_xg" not in df.columns:
        df["home_xg"] = 0.0
    if "away_xg" not in df.columns:
        df["away_xg"] = 0.0
    df["home_xg"] = df["home_xg"].fillna(0.0)
    df["away_xg"] = df["away_xg"].fillna(0.0)

    for col in ("home_shots", "away_shots", "home_shots_target", "away_shots_target"):
        if col not in df.columns:
            df[col] = 0

    rolled = rolling_team_stats(df)
    df = add_rolling_to_matches(df, rolled)
    df = add_differential_features(df)
    df = add_strength_ratings(df)
    df = add_implied_probs(df)
    df = add_big_chances_diff(df)
    df = add_referee_features(df)

    df["total_goals"] = df["fthg"] + df["ftag"]
    df.to_csv(PROCESSED / "features_modelo2.csv", index=False)
    print(f"features_modelo2.csv  — {len(df):,} partidos  |  {len(df.columns)} columnas")


if __name__ == "__main__":
    main()
