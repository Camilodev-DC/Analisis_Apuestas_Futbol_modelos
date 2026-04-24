"""
Bonus — clustering de jugadores por perfil de remate.

Produce:
  data/outputs/bonus_clustering_players.csv
  data/outputs/bonus_clustering_summary.csv
  pagina_web/graficas/bonus_clustering_silhouette.png
  pagina_web/graficas/bonus_clustering_players_pca.png
"""
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

PROCESSED = Path("data/processed")
OUTPUTS = Path("data/outputs")
GRAFICAS = Path("pagina_web/graficas")
for p in (OUTPUTS, GRAFICAS):
    p.mkdir(parents=True, exist_ok=True)

SHOT_EVENTS = {"savedshot", "missedshots", "goal", "shotonpost"}
MIN_SHOTS = 20


def load_player_profiles() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "features_modelo1_a_j.csv")
    df = df[df["event_type"].astype(str).str.lower().isin(SHOT_EVENTS)].copy()
    for col in [
        "is_goal",
        "is_big_chance",
        "is_header",
        "is_penalty",
        "is_volley",
        "first_touch",
        "is_in_area",
        "is_central",
    ]:
        if col in df.columns:
            df[col] = df[col].astype(int)

    profiles = df.groupby(["player_name", "team_name"]).agg(
        shots=("id", "count"),
        goals=("is_goal", "sum"),
        mean_distance=("distance_to_goal", "mean"),
        mean_angle=("angle_to_goal", "mean"),
        mean_xg=("xg_provisional", "mean"),
        box_share=("is_in_area", "mean"),
        central_share=("is_central", "mean"),
        big_chance_share=("is_big_chance", "mean"),
        header_share=("is_header", "mean"),
        penalty_share=("is_penalty", "mean"),
        first_touch_share=("first_touch", "mean"),
    ).reset_index()
    profiles = profiles[profiles["shots"] >= MIN_SHOTS].copy()
    profiles["goal_rate"] = profiles["goals"] / profiles["shots"]
    return profiles


def plot_silhouette(scores: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(scores["k"], scores["silhouette"], marker="o", lw=2)
    ax.set_title("Bonus Clustering — Silhouette por K")
    ax.set_xlabel("Número de clusters")
    ax.set_ylabel("Silhouette")
    fig.tight_layout()
    fig.savefig(GRAFICAS / "bonus_clustering_silhouette.png", dpi=150)
    plt.close(fig)


def plot_pca(df_plot: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = ["#264653", "#2a9d8f", "#e76f51"]
    for cluster in sorted(df_plot["cluster"].unique()):
        part = df_plot[df_plot["cluster"] == cluster]
        ax.scatter(
            part["pc1"],
            part["pc2"],
            s=35,
            alpha=0.75,
            label=f"Cluster {cluster}",
            color=colors[cluster % len(colors)],
        )

    top_players = df_plot.sort_values("shots", ascending=False).head(12)
    for _, row in top_players.iterrows():
        ax.annotate(row["player_name"], (row["pc1"], row["pc2"]), fontsize=7, alpha=0.85)

    ax.set_title("Bonus Clustering — Jugadores por perfil de remate (PCA)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAFICAS / "bonus_clustering_players_pca.png", dpi=150)
    plt.close(fig)


def main():
    df = load_player_profiles()
    feature_cols = [
        "shots",
        "goal_rate",
        "mean_distance",
        "mean_angle",
        "mean_xg",
        "box_share",
        "central_share",
        "big_chance_share",
        "header_share",
        "penalty_share",
        "first_touch_share",
    ]
    scaler = StandardScaler()
    X = scaler.fit_transform(df[feature_cols])

    score_rows = []
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(X)
        score_rows.append({"k": k, "silhouette": round(float(silhouette_score(X, labels)), 4)})
    scores = pd.DataFrame(score_rows)
    scores.to_csv(OUTPUTS / "bonus_clustering_silhouette.csv", index=False)
    plot_silhouette(scores)

    final_k = 3
    km = KMeans(n_clusters=final_k, random_state=42, n_init=20)
    df["cluster"] = km.fit_predict(X)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)
    df["pc1"] = coords[:, 0]
    df["pc2"] = coords[:, 1]
    plot_pca(df)

    summary = df.groupby("cluster")[feature_cols].mean().round(4).reset_index()
    summary.to_csv(OUTPUTS / "bonus_clustering_summary.csv", index=False)
    df.sort_values(["cluster", "shots"], ascending=[True, False]).to_csv(
        OUTPUTS / "bonus_clustering_players.csv", index=False
    )

    print(
        f"Clustering guardado → {len(df)} jugadores, k={final_k}, "
        f"silhouette_k3={scores.loc[scores['k'] == 3, 'silhouette'].iloc[0]:.4f}"
    )


if __name__ == "__main__":
    main()
