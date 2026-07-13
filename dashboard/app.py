"""Interactive Streamlit dashboard for the e-commerce sales analytics project.

Run with:
    streamlit run dashboard/app.py

Requires the pipeline to have been run first (python main.py run-all) so
data/processed/*.csv exist.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import analysis

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

st.set_page_config(page_title="E-Commerce Sales Analytics", layout="wide")


@st.cache_data
def load_data():
    customers = pd.read_csv(PROCESSED_DIR / "customers.csv")
    products = pd.read_csv(PROCESSED_DIR / "products.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders.csv")
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    return customers, products, orders


st.title("E-Commerce Sales Analytics Dashboard")

if not (PROCESSED_DIR / "orders.csv").exists():
    st.error(
        "No processed data found. Run `python main.py run-all` from the project "
        "root first, then reload this page."
    )
    st.stop()

customers, products, orders = load_data()

# --- Sidebar filters -------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = orders["order_date"].min().date(), orders["order_date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

categories = sorted(products["category"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

regions = sorted(customers["region"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

# --- Apply filters ----------------------------------------------------------
start_date, end_date = date_range if len(date_range) == 2 else (min_date, max_date)

filtered_products = products[products["category"].isin(selected_categories)]
filtered_customers = customers[customers["region"].isin(selected_regions)]

filtered_orders = orders[
    (orders["order_date"].dt.date >= start_date)
    & (orders["order_date"].dt.date <= end_date)
    & (orders["product_id"].isin(filtered_products["product_id"]))
    & (orders["customer_id"].isin(filtered_customers["customer_id"]))
]

# --- KPI row -----------------------------------------------------------------
total_revenue = filtered_orders["total_amount"].sum()
total_orders = filtered_orders["order_id"].nunique()
avg_order_value = filtered_orders["total_amount"].mean() if total_orders else 0
unique_customers = filtered_orders["customer_id"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("Unique Customers", f"{unique_customers:,}")

st.divider()

# --- Charts -------------------------------------------------------------------
if filtered_orders.empty:
    st.warning("No orders match the current filters.")
    st.stop()

left, right = st.columns(2)

with left:
    st.subheader("Monthly Revenue Trend")
    trend = analysis.monthly_revenue(filtered_orders)
    st.line_chart(trend.set_index("month")["revenue"])

with right:
    st.subheader("Top 10 Products by Revenue")
    top = analysis.top_products(filtered_orders, filtered_products, n=10)
    st.bar_chart(top.set_index("product_name")["revenue"])

st.subheader("Revenue by Category")
cat_revenue = analysis.revenue_by_category(filtered_orders, filtered_products)
st.bar_chart(cat_revenue.set_index("category")["revenue"])

st.subheader("Customer RFM Segmentation")
rfm = analysis.rfm_analysis(filtered_orders)
segment_summary = (
    rfm.groupby("segment")
    .agg(customers=("customer_id", "count"), avg_monetary=("monetary", "mean"))
    .sort_values("customers", ascending=False)
)
segment_summary["avg_monetary"] = segment_summary["avg_monetary"].round(2)

seg_col, table_col = st.columns([1, 2])
with seg_col:
    st.bar_chart(segment_summary["customers"])
with table_col:
    st.dataframe(
        rfm.merge(customers[["customer_id", "name", "region"]], on="customer_id", how="left")
        .sort_values("monetary", ascending=False)[
            ["customer_id", "name", "region", "recency", "frequency", "monetary", "segment"]
        ],
        use_container_width=True,
        height=300,
    )
