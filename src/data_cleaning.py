"""Clean the raw e-commerce CSVs and save analysis-ready versions.

Each function returns the cleaned DataFrame *and* a dict of counts describing
what was fixed, so the pipeline can print a short data-quality report.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def clean_customers(customers: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stats = {}

    before = len(customers)
    customers = customers.drop_duplicates(subset="customer_id").copy()
    stats["duplicate_customers_removed"] = before - len(customers)

    missing_region = customers["region"].isna().sum()
    customers["region"] = customers["region"].fillna("Unknown")
    stats["missing_regions_filled"] = int(missing_region)

    customers["region"] = customers["region"].str.strip().str.title()
    customers["name"] = customers["name"].str.strip()
    customers["join_date"] = pd.to_datetime(customers["join_date"])

    return customers.reset_index(drop=True), stats


def clean_products(products: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stats = {}

    before = len(products)
    products = products.drop_duplicates(subset="product_id").copy()
    stats["duplicate_products_removed"] = before - len(products)

    products["category"] = products["category"].str.strip().str.title()
    products["product_name"] = products["product_name"].str.strip()
    products["unit_price"] = products["unit_price"].astype(float).round(2)

    return products.reset_index(drop=True), stats


def clean_orders(orders: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stats = {}

    before = len(orders)
    orders = orders.drop_duplicates(subset="order_id").copy()
    stats["duplicate_orders_removed"] = before - len(orders)

    invalid_qty = orders["quantity"] <= 0
    stats["invalid_quantity_rows_dropped"] = int(invalid_qty.sum())
    orders = orders.loc[~invalid_qty].copy()

    missing_amount = orders["total_amount"].isna()
    stats["missing_amount_rows_dropped"] = int(missing_amount.sum())
    orders = orders.loc[~missing_amount].copy()

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders["quantity"] = orders["quantity"].astype(int)
    orders["total_amount"] = orders["total_amount"].astype(float).round(2)

    return orders.reset_index(drop=True), stats


def run_cleaning_pipeline(
    raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DIR
) -> dict:
    processed_dir.mkdir(parents=True, exist_ok=True)

    customers_raw = pd.read_csv(raw_dir / "customers.csv")
    products_raw = pd.read_csv(raw_dir / "products.csv")
    orders_raw = pd.read_csv(raw_dir / "orders.csv")

    customers, customer_stats = clean_customers(customers_raw)
    products, product_stats = clean_products(products_raw)
    orders, order_stats = clean_orders(orders_raw)

    # Drop orders that reference a customer/product no longer present after cleaning.
    before = len(orders)
    orders = orders[
        orders["customer_id"].isin(customers["customer_id"])
        & orders["product_id"].isin(products["product_id"])
    ].copy()
    order_stats["orphaned_orders_dropped"] = before - len(orders)

    customers.to_csv(processed_dir / "customers.csv", index=False)
    products.to_csv(processed_dir / "products.csv", index=False)
    orders.to_csv(processed_dir / "orders.csv", index=False)

    summary = {"customers": customer_stats, "products": product_stats, "orders": order_stats}
    return summary


def print_summary(summary: dict) -> None:
    print("Data cleaning summary")
    print("=" * 40)
    for table, stats in summary.items():
        print(f"\n{table}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    summary = run_cleaning_pipeline()
    print_summary(summary)
