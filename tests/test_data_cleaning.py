import pandas as pd

from src import data_cleaning


def test_clean_customers_fills_missing_region_and_drops_duplicates():
    raw = pd.DataFrame(
        {
            "customer_id": ["C1", "C2", "C1"],
            "name": [" Alice ", "Bob", " Alice "],
            "region": ["north", None, "north"],
            "join_date": ["2023-01-01", "2023-02-01", "2023-01-01"],
        }
    )
    cleaned, stats = data_cleaning.clean_customers(raw)

    assert len(cleaned) == 2
    assert stats["duplicate_customers_removed"] == 1
    assert stats["missing_regions_filled"] == 1
    assert cleaned.loc[cleaned["customer_id"] == "C2", "region"].iloc[0] == "Unknown"
    assert cleaned.loc[cleaned["customer_id"] == "C1", "region"].iloc[0] == "North"
    assert cleaned.loc[cleaned["customer_id"] == "C1", "name"].iloc[0] == "Alice"


def test_clean_products_normalizes_category_case():
    raw = pd.DataFrame(
        {
            "product_id": ["P1", "P1"],
            "product_name": [" Widget ", " Widget "],
            "category": ["tools", "tools"],
            "unit_price": ["9.999", "9.999"],
        }
    )
    cleaned, stats = data_cleaning.clean_products(raw)

    assert len(cleaned) == 1
    assert stats["duplicate_products_removed"] == 1
    assert cleaned["category"].iloc[0] == "Tools"
    assert cleaned["unit_price"].iloc[0] == 10.0


def test_clean_orders_drops_invalid_quantity_and_missing_amount():
    raw = pd.DataFrame(
        {
            "order_id": ["O1", "O2", "O3", "O3"],
            "customer_id": ["C1", "C1", "C2", "C2"],
            "order_date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-03"],
            "product_id": ["P1", "P1", "P1", "P1"],
            "quantity": [1, -1, 2, 2],
            "total_amount": [10.0, 10.0, None, None],
        }
    )
    cleaned, stats = data_cleaning.clean_orders(raw)

    assert stats["duplicate_orders_removed"] == 1
    assert stats["invalid_quantity_rows_dropped"] == 1
    assert stats["missing_amount_rows_dropped"] == 1
    assert len(cleaned) == 1
    assert cleaned["order_id"].iloc[0] == "O1"
