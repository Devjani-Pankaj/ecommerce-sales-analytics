"""Generate static charts (PNG) from the processed data for the README/report."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import analysis

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"

sns.set_theme(style="whitegrid")


def _load_processed(processed_dir: Path):
    customers = pd.read_csv(processed_dir / "customers.csv")
    products = pd.read_csv(processed_dir / "products.csv")
    orders = pd.read_csv(processed_dir / "orders.csv")
    return customers, products, orders


def plot_monthly_revenue(orders: pd.DataFrame, out_path: Path) -> None:
    trend = analysis.monthly_revenue(orders)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trend["month"], trend["revenue"], marker="o")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_top_products(orders: pd.DataFrame, products: pd.DataFrame, out_path: Path) -> None:
    top = analysis.top_products(orders, products, n=10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top, x="revenue", y="product_name", hue="category", dodge=False, ax=ax)
    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Revenue ($)")
    ax.set_ylabel("Product")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_rfm_segments(orders: pd.DataFrame, out_path: Path) -> None:
    rfm = analysis.rfm_analysis(orders)
    segment_counts = rfm["segment"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=segment_counts.index, y=segment_counts.values, ax=ax)
    ax.set_title("Customer Count by RFM Segment")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Number of Customers")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_cohort_retention(orders: pd.DataFrame, out_path: Path) -> None:
    retention = analysis.cohort_retention(orders)
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(retention, annot=True, fmt=".0%", cmap="Blues", ax=ax)
    ax.set_title("Monthly Cohort Retention")
    ax.set_xlabel("Months Since First Purchase")
    ax.set_ylabel("Cohort Month")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def generate_all_figures(
    processed_dir: Path = PROCESSED_DIR, figures_dir: Path = FIGURES_DIR
) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    customers, products, orders = _load_processed(processed_dir)

    plot_monthly_revenue(orders, figures_dir / "monthly_revenue.png")
    plot_top_products(orders, products, figures_dir / "top_products.png")
    plot_rfm_segments(orders, figures_dir / "rfm_segments.png")
    plot_cohort_retention(orders, figures_dir / "cohort_retention.png")

    print(f"Saved 4 figures to {figures_dir}")


if __name__ == "__main__":
    generate_all_figures()
