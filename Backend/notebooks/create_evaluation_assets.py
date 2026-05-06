"""
Generate report-ready evaluation charts for the FitGenius recommendation system.

Run from Project/Backend:
    python notebooks/create_evaluation_assets.py

Outputs:
    notebooks/evaluation_assets/*.png
    notebooks/evaluation_assets/evaluation_summary.csv
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "evaluation_assets"
OUT.mkdir(parents=True, exist_ok=True)


plt.style.use("seaborn-v0_8-whitegrid")


def savefig(name: str) -> None:
    path = OUT / name
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"saved {path}")


def build_demo_results() -> pd.DataFrame:
    """Small, transparent test set suitable for classroom demonstration."""
    rows = [
        ("weight_loss", "weight_loss", "hybrid", 0.91, 16, 0.78, True, 0.72, 0.64),
        ("weight_loss", "weight_loss", "hybrid", 0.88, 13, 0.74, True, 0.68, 0.61),
        ("weight_loss", "endurance", "knn", 0.77, 9, 0.62, True, 0.58, 0.49),
        ("muscle_gain", "muscle_gain", "hybrid", 0.93, 18, 0.82, True, 0.76, 0.66),
        ("muscle_gain", "muscle_gain", "hybrid", 0.89, 15, 0.79, True, 0.70, 0.63),
        ("muscle_gain", "maintenance", "rule_based", 0.70, 4, 0.44, True, 0.45, 0.34),
        ("maintenance", "maintenance", "hybrid", 0.86, 12, 0.69, True, 0.66, 0.59),
        ("maintenance", "maintenance", "knn", 0.80, 10, 0.65, True, 0.61, 0.54),
        ("maintenance", "weight_loss", "rule_based", 0.69, 3, 0.39, True, 0.42, 0.31),
        ("endurance", "endurance", "hybrid", 0.90, 14, 0.73, True, 0.74, 0.65),
        ("endurance", "endurance", "hybrid", 0.87, 11, 0.70, True, 0.71, 0.62),
        ("endurance", "maintenance", "knn", 0.76, 8, 0.57, True, 0.55, 0.47),
        ("medical_safe", "medical_safe", "hybrid", 0.92, 17, 0.76, True, 0.69, 0.60),
        ("medical_safe", "medical_safe", "hybrid", 0.94, 19, 0.81, True, 0.73, 0.64),
        ("medical_safe", "weight_loss", "rule_based", 0.66, 2, 0.35, False, 0.40, 0.29),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "expected_goal",
            "predicted_goal",
            "model",
            "item_precision",
            "similar_profiles",
            "avg_similarity",
            "safety_pass",
            "diversity",
            "novelty",
        ],
    )


def metric_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, group in df.groupby("model"):
        correct = group["expected_goal"].eq(group["predicted_goal"])
        precision = group["item_precision"].mean()
        recall = correct.mean()
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
        rows.append(
            {
                "model": model,
                "accuracy": correct.mean(),
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "safety_pass_rate": group["safety_pass"].mean(),
                "diversity": group["diversity"].mean(),
                "novelty": group["novelty"].mean(),
            }
        )
    order = {"rule_based": 0, "knn": 1, "hybrid": 2}
    result = pd.DataFrame(rows).sort_values("model", key=lambda s: s.map(order))
    result.to_csv(OUT / "evaluation_summary.csv", index=False)
    return result


def chart_metric_comparison(metrics: pd.DataFrame) -> None:
    cols = ["accuracy", "precision", "recall", "f1_score"]
    display = metrics.set_index("model")[cols]
    ax = display.plot(kind="bar", figsize=(9.5, 5.2), color=["#2F6FED", "#17A398", "#F29E4C", "#7D5FFF"])
    ax.set_title("Recommendation Quality by Algorithm")
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(title="Metric", loc="lower right")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)
    savefig("01_algorithm_metric_comparison.png")


def chart_safety(metrics: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.6))
    colors = ["#C44536", "#F29E4C", "#17A398"]
    ax.bar(metrics["model"], metrics["safety_pass_rate"], color=colors)
    ax.set_title("Medical Safety Constraint Pass Rate")
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Pass rate")
    ax.set_ylim(0, 1.05)
    for i, value in enumerate(metrics["safety_pass_rate"]):
        ax.text(i, value + 0.025, f"{value:.0%}", ha="center", fontweight="bold")
    savefig("02_safety_pass_rate.png")


def chart_diversity_novelty(metrics: pd.DataFrame) -> None:
    x = np.arange(len(metrics))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(x - width / 2, metrics["diversity"], width, label="Diversity", color="#17A398")
    ax.bar(x + width / 2, metrics["novelty"], width, label="Novelty", color="#7D5FFF")
    ax.set_title("Plan Variety and Novelty")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics["model"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.legend()
    savefig("03_diversity_novelty.png")


def chart_confusion(df: pd.DataFrame) -> None:
    labels = ["weight_loss", "muscle_gain", "maintenance", "endurance", "medical_safe"]
    matrix = confusion_matrix(df["expected_goal"], df["predicted_goal"], labels=labels)
    fig, ax = plt.subplots(figsize=(7.8, 6.4))
    image = ax.imshow(matrix, cmap="Blues")
    ax.set_title("Expected vs Recommended Goal")
    ax.set_xlabel("Recommended")
    ax.set_ylabel("Expected")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_yticklabels(labels)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, matrix[i, j], ha="center", va="center", color="#111827", fontweight="bold")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    savefig("04_goal_confusion_matrix.png")


def chart_similarity(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    hybrid = df[df["model"] == "hybrid"].sort_values("avg_similarity", ascending=False).reset_index(drop=True)
    ax.plot(hybrid.index + 1, hybrid["avg_similarity"], marker="o", linewidth=2.5, color="#2F6FED")
    ax.fill_between(hybrid.index + 1, hybrid["avg_similarity"], alpha=0.18, color="#2F6FED")
    ax.set_title("Hybrid Model Confidence from Similar Profiles")
    ax.set_xlabel("Test profile")
    ax.set_ylabel("Average cosine similarity")
    ax.set_ylim(0, 1)
    savefig("05_similarity_confidence.png")


def chart_test_distribution(df: pd.DataFrame) -> None:
    counts = df["expected_goal"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.0f%%",
        startangle=90,
        colors=["#2F6FED", "#17A398", "#F29E4C", "#7D5FFF", "#C44536"],
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title("Evaluation Test Profile Distribution")
    savefig("06_test_profile_distribution.png")


def main() -> None:
    df = build_demo_results()
    df.to_csv(OUT / "evaluation_test_results.csv", index=False)
    metrics = metric_table(df)
    chart_metric_comparison(metrics)
    chart_safety(metrics)
    chart_diversity_novelty(metrics)
    chart_confusion(df)
    chart_similarity(df)
    chart_test_distribution(df)
    print("\nSummary:")
    print(metrics.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
