import pandas as pd
import pytest

from src import analysis


@pytest.fixture
def products_df():
    return pd.DataFrame(
        {
            "product_id": ["P1", "P2"],
            "product_name": ["Widget", "Gadget"],
            "category": ["Tools", "Electronics"],
            "unit_price": [10.0, 20.0],
        }
    )


@pytest.fixture
def customers_df():
    return pd.DataFrame(
        {
            "customer_id": [f"C{i}" for i in range(1, 9)],
            "name": [f"Customer {i}" for i in range(1, 9)],
            "region": ["North", "South"] * 4,
            "join_date": ["2023-01-01"] * 8,
        }
    )


@pytest.fixture
def orders_df():
    # 8 customers, varying order counts/amounts/dates across two months so
    # RFM quartiles and cohort retention both have something to compute.
    rows = []
    order_id = 1
    for i, customer in enumerate([f"C{n}" for n in range(1, 9)], start=1):
        num_orders = (i % 3) + 1
        for j in range(num_orders):
            month = "2023-01" if j == 0 else "2023-02"
            rows.append(
                {
                    "order_id": f"O{order_id}",
                    "customer_id": customer,
                    "order_date": f"{month}-{10 + j:02d}",
                    "product_id": "P1" if order_id % 2 == 0 else "P2",
                    "quantity": 1 + (order_id % 3),
                    "total_amount": 10.0 * i + j,
                }
            )
            order_id += 1
    return pd.DataFrame(rows)


def test_monthly_revenue_totals_match(orders_df):
    result = analysis.monthly_revenue(orders_df)
    assert set(result.columns) == {"month", "revenue", "orders"}
    assert result["revenue"].sum() == pytest.approx(orders_df["total_amount"].sum())
    assert list(result["month"]) == sorted(result["month"])


def test_top_products_ordered_by_revenue_desc(orders_df, products_df):
    result = analysis.top_products(orders_df, products_df, n=2)
    assert len(result) == 2
    assert list(result["revenue"]) == sorted(result["revenue"], reverse=True)


def test_revenue_by_category_matches_totals(orders_df, products_df):
    result = analysis.revenue_by_category(orders_df, products_df)
    assert result["revenue"].sum() == pytest.approx(orders_df["total_amount"].sum())


def test_rfm_analysis_scores_in_range(orders_df):
    rfm = analysis.rfm_analysis(orders_df)
    assert len(rfm) == orders_df["customer_id"].nunique()
    for col in ("r_score", "f_score", "m_score"):
        assert rfm[col].between(1, 4).all()
    assert set(rfm["segment"]) <= {
        "Champions",
        "Loyal Customers",
        "Potential Loyalists",
        "At Risk",
        "Lost",
    }


def test_cohort_retention_first_month_is_full_retention(orders_df):
    retention = analysis.cohort_retention(orders_df)
    assert (retention[0] == 1.0).all()
