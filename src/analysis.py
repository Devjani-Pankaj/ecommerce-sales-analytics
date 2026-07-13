"""Core analytics: revenue trends, product/category breakdowns, RFM
segmentation, and cohort retention. Pure pandas, no I/O side effects, so
these are easy to unit test and reuse from both the CLI and the dashboard.
"""

import pandas as pd


def monthly_revenue(orders: pd.DataFrame) -> pd.DataFrame:
    df = orders.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    result = (
        df.groupby("month")
        .agg(revenue=("total_amount", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("month")
    )
    result["revenue"] = result["revenue"].round(2)
    return result


def top_products(orders: pd.DataFrame, products: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    merged = orders.merge(products, on="product_id", how="left")
    result = (
        merged.groupby(["product_id", "product_name", "category"])
        .agg(revenue=("total_amount", "sum"), units_sold=("quantity", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(n)
    )
    result["revenue"] = result["revenue"].round(2)
    return result.reset_index(drop=True)


def revenue_by_category(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    merged = orders.merge(products, on="product_id", how="left")
    result = (
        merged.groupby("category")
        .agg(revenue=("total_amount", "sum"), units_sold=("quantity", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    result["revenue"] = result["revenue"].round(2)
    return result


def revenue_by_region(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    merged = orders.merge(customers, on="customer_id", how="left")
    result = (
        merged.groupby("region")
        .agg(
            revenue=("total_amount", "sum"),
            orders=("order_id", "nunique"),
            avg_order_value=("total_amount", "mean"),
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    result["revenue"] = result["revenue"].round(2)
    result["avg_order_value"] = result["avg_order_value"].round(2)
    return result


def rfm_analysis(orders: pd.DataFrame) -> pd.DataFrame:
    """Recency/Frequency/Monetary segmentation.

    Quartile scores use `rank(method="first")` before `qcut` so duplicate
    values (e.g. many customers with the same order count) never trigger a
    "duplicate bin edges" error.
    """
    df = orders.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    rfm = (
        df.groupby("customer_id")
        .agg(
            recency=("order_date", lambda x: (snapshot_date - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("total_amount", "sum"),
        )
        .reset_index()
    )
    rfm["monetary"] = rfm["monetary"].round(2)

    rfm["r_score"] = pd.qcut(
        rfm["recency"].rank(method="first", ascending=False), 4, labels=[1, 2, 3, 4]
    ).astype(int)
    rfm["f_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]
    ).astype(int)
    rfm["m_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]
    ).astype(int)
    rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    def _segment(score: int) -> str:
        if score >= 10:
            return "Champions"
        if score >= 8:
            return "Loyal Customers"
        if score >= 6:
            return "Potential Loyalists"
        if score >= 4:
            return "At Risk"
        return "Lost"

    rfm["segment"] = rfm["rfm_score"].apply(_segment)
    return rfm


def cohort_retention(orders: pd.DataFrame) -> pd.DataFrame:
    """Monthly cohort retention matrix: % of each acquisition cohort that
    is still ordering N months later."""
    df = orders.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.to_period("M")
    df["cohort_month"] = df.groupby("customer_id")["order_date"].transform("min").dt.to_period("M")
    df["cohort_index"] = (df["order_month"] - df["cohort_month"]).apply(lambda x: x.n)

    cohort_counts = (
        df.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
    )
    cohort_pivot = cohort_counts.pivot(
        index="cohort_month", columns="cohort_index", values="customer_id"
    )
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0).round(3)
    retention.index = retention.index.astype(str)
    return retention
