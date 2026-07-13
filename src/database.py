"""Load cleaned CSVs into a SQLite warehouse for SQL-based analysis."""

import sqlite3
from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "warehouse.db"


def load_warehouse(processed_dir: Path = PROCESSED_DIR, db_path: Path = DB_PATH) -> None:
    customers = pd.read_csv(processed_dir / "customers.csv")
    products = pd.read_csv(processed_dir / "products.csv")
    orders = pd.read_csv(processed_dir / "orders.csv")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        customers.to_sql("customers", conn, if_exists="replace", index=False)
        products.to_sql("products", conn, if_exists="replace", index=False)
        orders.to_sql("orders", conn, if_exists="replace", index=False)

    print(f"Loaded {len(customers)} customers, {len(products)} products, "
          f"{len(orders)} orders into {db_path}")


def run_query(sql: str, db_path: Path = DB_PATH) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql, conn)


if __name__ == "__main__":
    load_warehouse()
