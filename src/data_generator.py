"""Generate a synthetic e-commerce dataset (customers, products, orders).

The data is intentionally imperfect (duplicates, missing values, bad rows)
so the cleaning pipeline in `data_cleaning.py` has real work to do.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 30
NUM_ORDERS = 6000

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = {
    "Electronics": ["Wireless Mouse", "Bluetooth Speaker", "USB-C Hub", "Laptop Stand", "Webcam"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Cutlery Set", "Toaster"],
    "Clothing": ["Denim Jacket", "Running Shoes", "Graphic Tee", "Wool Sweater", "Cargo Pants"],
    "Books": ["Mystery Novel", "Cookbook", "Self-Help Guide", "Sci-Fi Anthology", "Biography"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Cycling Helmet", "Tennis Racket", "Water Bottle"],
    "Beauty": ["Face Serum", "Shampoo Bar", "Lip Balm Set", "Sunscreen SPF50", "Hair Dryer"],
}

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Priya", "Ananya", "Diya", "Isha", "Kabir",
    "Rohan", "Sneha", "Neha", "Arjun", "Meera", "Karan", "Riya", "Sanjay",
    "Tara", "Nikhil", "Pooja", "Yash",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Reddy", "Nair", "Iyer", "Singh",
    "Mehta", "Kapoor", "Joshi", "Rao", "Chopra", "Malhotra", "Bose", "Desai",
]


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    join_dates = pd.to_datetime("2023-01-01") + pd.to_timedelta(
        rng.integers(0, 700, size=NUM_CUSTOMERS), unit="D"
    )
    customers = pd.DataFrame(
        {
            "customer_id": [f"C{i:04d}" for i in range(1, NUM_CUSTOMERS + 1)],
            "name": [
                f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}" for _ in range(NUM_CUSTOMERS)
            ],
            "region": rng.choice(REGIONS, size=NUM_CUSTOMERS),
            "join_date": join_dates,
        }
    )

    # Inject messiness: some missing regions, a few duplicate rows.
    missing_idx = rng.choice(customers.index, size=15, replace=False)
    customers.loc[missing_idx, "region"] = None
    customers = pd.concat([customers, customers.sample(5, random_state=42)], ignore_index=True)

    return customers


def generate_products(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    pid = 1
    for category, names in CATEGORIES.items():
        for name in names:
            price = round(rng.uniform(8, 250), 2)
            rows.append(
                {
                    "product_id": f"P{pid:03d}",
                    "product_name": name,
                    "category": category,
                    "unit_price": price,
                }
            )
            pid += 1
    return pd.DataFrame(rows)


def generate_orders(
    rng: np.random.Generator, customers: pd.DataFrame, products: pd.DataFrame
) -> pd.DataFrame:
    unique_customers = customers.drop_duplicates("customer_id")
    customer_ids = unique_customers["customer_id"].to_numpy()
    product_ids = products["product_id"].to_numpy()
    price_lookup = products.set_index("product_id")["unit_price"]

    start_date = pd.to_datetime("2023-01-01")
    end_date = pd.to_datetime("2024-12-31")
    date_range_days = (end_date - start_date).days

    order_dates = start_date + pd.to_timedelta(
        rng.integers(0, date_range_days, size=NUM_ORDERS), unit="D"
    )
    chosen_customers = rng.choice(customer_ids, size=NUM_ORDERS)
    chosen_products = rng.choice(product_ids, size=NUM_ORDERS)
    quantities = rng.integers(1, 6, size=NUM_ORDERS)
    unit_prices = price_lookup.loc[chosen_products].to_numpy()

    orders = pd.DataFrame(
        {
            "order_id": [f"O{i:05d}" for i in range(1, NUM_ORDERS + 1)],
            "customer_id": chosen_customers,
            "order_date": order_dates,
            "product_id": chosen_products,
            "quantity": quantities,
            "total_amount": np.round(quantities * unit_prices, 2),
        }
    )

    # Inject messiness: exact duplicates, bad quantities, and missing amounts.
    dup_rows = orders.sample(40, random_state=1)
    orders = pd.concat([orders, dup_rows], ignore_index=True)

    bad_qty_idx = rng.choice(orders.index, size=20, replace=False)
    orders.loc[bad_qty_idx, "quantity"] = -1

    missing_amount_idx = rng.choice(orders.index, size=25, replace=False)
    orders.loc[missing_amount_idx, "total_amount"] = np.nan

    return orders


def main() -> None:
    rng = np.random.default_rng(SEED)

    raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(rng)
    products = generate_products(rng)
    orders = generate_orders(rng, customers, products)

    customers.to_csv(raw_dir / "customers.csv", index=False)
    products.to_csv(raw_dir / "products.csv", index=False)
    orders.to_csv(raw_dir / "orders.csv", index=False)

    print(f"Generated {len(customers)} customer rows -> {raw_dir / 'customers.csv'}")
    print(f"Generated {len(products)} product rows -> {raw_dir / 'products.csv'}")
    print(f"Generated {len(orders)} order rows -> {raw_dir / 'orders.csv'}")


if __name__ == "__main__":
    main()
