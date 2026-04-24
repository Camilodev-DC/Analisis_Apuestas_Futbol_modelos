"""
Feature engineering para Modelo 1 — xG por tiro.
Input:  data/raw/events.csv
Output: data/processed/features_modelo1.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)
PREBUILT = OUT / "features_modelo1_a_j.csv"
SHOT_EVENTS = {"shot", "savedshot", "missedshots", "goal", "shotonpost"}


def load_events(path: Path) -> pd.DataFrame:
    if PREBUILT.exists():
        df = pd.read_csv(PREBUILT, parse_dates=["match_date"])
        if "event_type" in df.columns:
            df = df[df["event_type"].astype(str).str.lower().isin(SHOT_EVENTS)].copy()
        return df

    df = pd.read_csv(path)
    if "match_date" not in df.columns:
        matches = pd.read_csv(RAW / "matches.csv", parse_dates=["date"])
        match_id_col = "match_id" if "match_id" in matches.columns else "id"
        matches = matches.rename(columns={match_id_col: "match_id", "date": "match_date"})
        keep_cols = [c for c in ["match_id", "match_date", "home_team", "away_team", "referee"] if c in matches.columns]
        df = df.merge(matches[keep_cols], on="match_id", how="left")
    else:
        df["match_date"] = pd.to_datetime(df["match_date"])

    team_col = "team_name" if "team_name" in df.columns else "team"
    if team_col == "team_name":
        df["team"] = df["team_name"]

    shots = df[df["event_type"].astype(str).str.lower().isin(SHOT_EVENTS)].copy()
    return shots


def add_geometry(df: pd.DataFrame) -> pd.DataFrame:
    goal_x, goal_y = 105.0, 34.0
    dx = goal_x - df["x"]
    dy = goal_y - df["y"]
    df["distance_to_goal"] = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(7.32 * df["x"], df["x"] ** 2 + dy**2 - (7.32 / 2) ** 2)
    df["angle_to_goal"] = np.degrees(angle.clip(-np.pi, np.pi))
    df["dist_squared"] = df["distance_to_goal"] ** 2
    df["dist_angle"] = df["distance_to_goal"] * df["angle_to_goal"].abs()
    df["is_in_area"] = (df["x"] >= 88.5) & (df["y"].between(13.84, 54.16))
    df["is_central"] = df["y"].between(24.0, 44.0)
    return df


def add_porteria_zone(df: pd.DataFrame) -> pd.DataFrame:
    goal_y = 34.0
    x_bins = pd.cut(df["distance_to_goal"], bins=[0, 11, 22, 105], labels=["close", "mid", "far"])
    y_bins = pd.cut((df["y"] - goal_y).abs(), bins=[0, 5, 11, 34], labels=["central", "offset", "wide"])
    df["porteria_zone"] = x_bins.astype(str) + "_" + y_bins.astype(str)
    zone_dummies = pd.get_dummies(df["porteria_zone"], prefix="zone")
    df = pd.concat([df, zone_dummies], axis=1)
    return df


def add_shot_quality_index(df: pd.DataFrame) -> pd.DataFrame:
    components = []
    if "is_big_chance" in df.columns:
        components.append(df["is_big_chance"].fillna(0) * 0.35)
    if "is_in_area" in df.columns:
        components.append(df["is_in_area"].astype(int) * 0.25)
    if "is_central" in df.columns:
        components.append(df["is_central"].astype(int) * 0.20)
    dist_norm = 1 - df["distance_to_goal"].clip(0, 40) / 40
    components.append(dist_norm * 0.20)
    df["shot_quality_index"] = sum(components)
    return df


def add_buildup_features(df: pd.DataFrame) -> pd.DataFrame:
    if "buildup_passes" not in df.columns:
        df["buildup_passes"] = 0
        df["buildup_unique_players"] = 0
        df["buildup_decentralized"] = 0.0
    return df


def add_pressure_features(df: pd.DataFrame) -> pd.DataFrame:
    if "defensive_pressure" not in df.columns:
        df["defensive_pressure"] = 0.0
    if "ppda" not in df.columns:
        df["ppda"] = 0.0
    if "pass_decentralization" not in df.columns:
        df["pass_decentralization"] = 0.0
    return df


BOOL_COLS = [
    "is_big_chance", "is_header", "is_penalty", "is_volley",
    "first_touch", "is_set_piece", "from_corner", "is_counter",
    "is_right_foot", "is_left_foot",
]

FEATURE_COLS = [
    "match_id", "match_date", "is_goal",
    "distance_to_goal", "angle_to_goal", "dist_squared", "dist_angle",
    "is_in_area", "is_central",
    "is_big_chance", "is_header", "is_penalty", "is_volley",
    "first_touch", "is_set_piece", "from_corner", "is_counter",
    "is_right_foot", "is_left_foot",
    "shot_quality_index",
    "defensive_pressure", "buildup_passes", "buildup_unique_players",
    "buildup_decentralized", "ppda", "pass_decentralization",
]


def main():
    df = load_events(RAW / "events.csv")
    df = add_geometry(df)
    df = add_porteria_zone(df)
    df = add_shot_quality_index(df)
    df = add_buildup_features(df)
    df = add_pressure_features(df)

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    zone_cols = [c for c in df.columns if c.startswith("zone_")]
    cols = [c for c in FEATURE_COLS if c in df.columns] + zone_cols
    df[cols].to_csv(OUT / "features_modelo1.csv", index=False)
    print(f"features_modelo1.csv  — {len(df):,} tiros  |  {len(cols)} features")


if __name__ == "__main__":
    main()
