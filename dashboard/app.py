"""Flipkart Mobiles Analytics Dashboard.

Run with:
    streamlit run dashboard/app.py
"""

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(r"C:\Users\Day\Downloads\Flipkart_Mobiles.csv")

st.set_page_config(
    page_title="Flipkart Mobiles Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label { font-weight: 600 !important; }

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
}
.metric-card.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 8px 32px rgba(245, 87, 108, 0.25); }
.metric-card.orange:hover { box-shadow: 0 12px 40px rgba(245, 87, 108, 0.35); }
.metric-card.green { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); box-shadow: 0 8px 32px rgba(79, 172, 254, 0.25); }
.metric-card.green:hover { box-shadow: 0 12px 40px rgba(79, 172, 254, 0.35); }
.metric-card.blue { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); box-shadow: 0 8px 32px rgba(67, 233, 123, 0.25); }
.metric-card.blue:hover { box-shadow: 0 12px 40px rgba(67, 233, 123, 0.35); }
.metric-card.red { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); box-shadow: 0 8px 32px rgba(250, 112, 154, 0.25); }
.metric-card.red:hover { box-shadow: 0 12px 40px rgba(250, 112, 154, 0.35); }

.metric-value { font-size: 2rem; font-weight: 700; color: #fff; margin: 4px 0; }
.metric-label { font-size: 0.85rem; font-weight: 500; color: rgba(255,255,255,0.85); text-transform: uppercase; letter-spacing: 1px; }

.chart-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #667eea;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.header-container {
    text-align: center;
    padding: 20px 0 10px 0;
}
.header-container h1 {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.header-subtitle {
    font-size: 1rem;
    color: #888;
    margin-top: 0;
}

div[data-testid="stMetric"] { display: none; }

.deal-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f5576c, #ff6b6b);
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

COLORS = ["#667eea", "#764ba2", "#f5576c", "#4facfe", "#43e97b", "#fa709a",
          "#fee140", "#00f2fe", "#38f9d7", "#f093fb", "#a18cd1", "#fbc2eb",
          "#ff9a9e", "#fad0c4", "#ffecd2"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#ccc"),
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="#1a1a2e", font_size=13, font_family="Inter"),
)


def extract_num(s):
    m = re.search(r"[\d.]+", str(s))
    return float(m.group()) if m else 0


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Selling Price"] = pd.to_numeric(df["Selling Price"], errors="coerce")
    df["Original Price"] = pd.to_numeric(df["Original Price"], errors="coerce")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Discount"] = df["Original Price"] - df["Selling Price"]
    df["Discount %"] = ((df["Discount"] / df["Original Price"]) * 100).round(1)
    df["Memory (GB)"] = df["Memory"].str.extract(r"([\d.]+)").astype(float)
    df["Storage (GB)"] = df["Storage"].str.extract(r"(\d+)").astype(float)
    return df.dropna(subset=["Selling Price"])


df = load_data()

# --- Header ---
st.markdown("""
<div class="header-container">
    <h1>📱 Flipkart Mobiles Analytics</h1>
    <p class="header-subtitle">Interactive dashboard for exploring mobile phone listings, pricing & trends</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    brands = sorted(df["Brand"].unique())
    selected_brands = st.multiselect("📦 Brand", brands, default=brands)

    st.markdown("")
    price_min, price_max = int(df["Selling Price"].min()), int(df["Selling Price"].max())
    price_range = st.slider("💰 Price Range (₹)", price_min, price_max, (price_min, price_max), step=500)

    st.markdown("")
    rating_min = st.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0, step=0.1)

    st.markdown("")
    memory_options = sorted(df["Memory"].dropna().unique(), key=extract_num)
    selected_memory = st.multiselect("🧠 RAM", memory_options, default=memory_options)

    st.markdown("")
    storage_options = sorted(df["Storage"].dropna().unique(), key=extract_num)
    selected_storage = st.multiselect("💾 Storage", storage_options, default=storage_options)

    st.markdown("---")
    st.markdown(f"<p style='text-align:center; font-size:0.8rem; opacity:0.5;'>Dataset: {len(df):,} listings</p>", unsafe_allow_html=True)

# --- Apply filters ---
filtered = df[
    (df["Brand"].isin(selected_brands))
    & (df["Selling Price"] >= price_range[0])
    & (df["Selling Price"] <= price_range[1])
    & (df["Rating"] >= rating_min)
    & (df["Memory"].isin(selected_memory))
    & (df["Storage"].isin(selected_storage))
]

# --- KPI cards ---
kpi_cols = st.columns(5)
kpis = [
    ("Total Listings", f"{len(filtered):,}", ""),
    ("Brands", f"{filtered['Brand'].nunique()}", "orange"),
    ("Avg Price", f"₹{filtered['Selling Price'].mean():,.0f}", "green"),
    ("Avg Rating", f"{filtered['Rating'].mean():.2f} ⭐", "blue"),
    ("Avg Discount", f"{filtered['Discount %'].mean():.1f}%", "red"),
]
for col, (label, value, css_class) in zip(kpi_cols, kpis):
    col.markdown(f"""
    <div class="metric-card {css_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if filtered.empty:
    st.warning("No phones match the current filters.")
    st.stop()

# --- Row 1: Brand distribution & Price by Brand ---
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-header">📊 Listings by Brand (Top 15)</div>', unsafe_allow_html=True)
    brand_counts = filtered["Brand"].value_counts().head(15).reset_index()
    brand_counts.columns = ["Brand", "Count"]
    fig = px.bar(brand_counts, x="Count", y="Brand", orientation="h",
                 color="Count", color_continuous_scale=["#667eea", "#764ba2"])
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, coloraxis_showscale=False,
                      yaxis=dict(autorange="reversed"), height=450)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Listings: %{x}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown('<div class="section-header">💰 Avg Selling Price by Brand (Top 15)</div>', unsafe_allow_html=True)
    avg_price = filtered.groupby("Brand")["Selling Price"].mean().sort_values(ascending=False).head(15).reset_index()
    avg_price.columns = ["Brand", "Avg Price"]
    avg_price["Avg Price"] = avg_price["Avg Price"].round(0)
    fig = px.bar(avg_price, x="Avg Price", y="Brand", orientation="h",
                 color="Avg Price", color_continuous_scale=["#4facfe", "#00f2fe"])
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, coloraxis_showscale=False,
                      yaxis=dict(autorange="reversed"), height=450)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Avg: ₹%{x:,.0f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

# --- Row 2: Rating & Discount ---
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="section-header">⭐ Rating Distribution</div>', unsafe_allow_html=True)
    rating_dist = filtered["Rating"].value_counts().sort_index().reset_index()
    rating_dist.columns = ["Rating", "Count"]
    fig = px.bar(rating_dist, x="Rating", y="Count", color="Count",
                 color_continuous_scale=["#43e97b", "#38f9d7"])
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, coloraxis_showscale=False, height=400)
    fig.update_traces(hovertemplate="Rating: %{x}<br>Count: %{y}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.markdown('<div class="section-header">🏷️ Avg Discount % by Brand (Top 15)</div>', unsafe_allow_html=True)
    disc_brand = filtered.groupby("Brand")["Discount %"].mean().sort_values(ascending=False).head(15).reset_index()
    disc_brand.columns = ["Brand", "Discount %"]
    disc_brand["Discount %"] = disc_brand["Discount %"].round(1)
    fig = px.bar(disc_brand, x="Discount %", y="Brand", orientation="h",
                 color="Discount %", color_continuous_scale=["#fa709a", "#fee140"])
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, coloraxis_showscale=False,
                      yaxis=dict(autorange="reversed"), height=400)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Discount: %{x:.1f}%<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

# --- Row 3: Scatter & Storage ---
col_e, col_f = st.columns(2)

with col_e:
    st.markdown('<div class="section-header">📈 Price vs Rating</div>', unsafe_allow_html=True)
    scatter_data = filtered[["Brand", "Model", "Selling Price", "Rating", "Discount %"]].dropna()
    fig = px.scatter(scatter_data, x="Selling Price", y="Rating", color="Brand",
                     hover_data=["Model", "Discount %"], opacity=0.7,
                     color_discrete_sequence=COLORS)
    fig.update_layout(**PLOTLY_LAYOUT, height=450,
                      legend=dict(font=dict(size=10), itemsizing="constant"),
                      xaxis_title="Selling Price (₹)", yaxis_title="Rating")
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="rgba(255,255,255,0.3)")))
    st.plotly_chart(fig, use_container_width=True)

with col_f:
    st.markdown('<div class="section-header">💾 Listings by Storage Capacity</div>', unsafe_allow_html=True)
    storage_counts = filtered["Storage"].value_counts().reset_index()
    storage_counts.columns = ["Storage", "Count"]
    storage_counts["sort_key"] = storage_counts["Storage"].apply(extract_num)
    storage_counts = storage_counts.sort_values("sort_key")
    fig = px.bar(storage_counts, x="Storage", y="Count", color="Count",
                 color_continuous_scale=["#a18cd1", "#fbc2eb"])
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, coloraxis_showscale=False, height=450)
    fig.update_traces(hovertemplate="Storage: %{x}<br>Count: %{y}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

# --- Price Segments Donut ---
st.markdown('<div class="section-header">🎯 Price Segments</div>', unsafe_allow_html=True)
bins = [0, 10000, 20000, 30000, 50000, 100000, float("inf")]
labels = ["Under ₹10K", "₹10K-20K", "₹20K-30K", "₹30K-50K", "₹50K-1L", "Above ₹1L"]
filtered_copy = filtered.copy()
filtered_copy["Segment"] = pd.cut(filtered_copy["Selling Price"], bins=bins, labels=labels)
seg_counts = filtered_copy["Segment"].value_counts().reindex(labels).reset_index()
seg_counts.columns = ["Segment", "Count"]

seg_left, seg_right = st.columns([1, 2])
with seg_left:
    fig = go.Figure(data=[go.Pie(
        labels=seg_counts["Segment"], values=seg_counts["Count"],
        hole=0.55, marker=dict(colors=COLORS[:len(seg_counts)]),
        textinfo="label+percent", textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
    )])
    fig.update_layout(**PLOTLY_LAYOUT, height=400, showlegend=False,
                      annotations=[dict(text="Price<br>Segments", x=0.5, y=0.5,
                                        font_size=14, font_color="#ccc", showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)

with seg_right:
    fig = px.bar(seg_counts, x="Segment", y="Count", color="Segment",
                 color_discrete_sequence=COLORS[:len(seg_counts)])
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=400,
                      xaxis_title="", yaxis_title="Number of Listings")
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Listings: %{y}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

# --- Brand Market Share Treemap ---
st.markdown('<div class="section-header">🗺️ Brand Market Share</div>', unsafe_allow_html=True)
brand_share = filtered["Brand"].value_counts().head(20).reset_index()
brand_share.columns = ["Brand", "Count"]
fig = px.treemap(brand_share, path=["Brand"], values="Count",
                 color="Count", color_continuous_scale=["#667eea", "#764ba2", "#f5576c"])
fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
fig.update_traces(textinfo="label+value+percent root",
                  textfont=dict(size=14, color="white"),
                  hovertemplate="<b>%{label}</b><br>Listings: %{value}<br>Share: %{percentRoot:.1%}<extra></extra>")
st.plotly_chart(fig, use_container_width=True)

# --- Top Deals ---
st.markdown('<div class="section-header">🔥 Top 20 Best Deals (Highest Discount)</div>', unsafe_allow_html=True)
top_deals = (
    filtered.nlargest(20, "Discount %")[
        ["Brand", "Model", "Color", "Memory", "Storage", "Rating",
         "Selling Price", "Original Price", "Discount %"]
    ]
    .reset_index(drop=True)
)
top_deals.index = top_deals.index + 1

st.dataframe(
    top_deals.style
        .format({"Selling Price": "₹{:,.0f}", "Original Price": "₹{:,.0f}", "Discount %": "{:.1f}%"})
        .background_gradient(subset=["Discount %"], cmap="YlOrRd")
        .background_gradient(subset=["Rating"], cmap="Greens"),
    use_container_width=True,
    height=500,
)

# --- Full dataset ---
st.markdown('<div class="section-header">📋 Full Dataset</div>', unsafe_allow_html=True)

search = st.text_input("🔍 Search by brand or model...", "")
display_df = filtered[["Brand", "Model", "Color", "Memory", "Storage", "Rating",
                        "Selling Price", "Original Price", "Discount %"]].copy()
if search:
    mask = (
        display_df["Brand"].str.contains(search, case=False, na=False)
        | display_df["Model"].str.contains(search, case=False, na=False)
    )
    display_df = display_df[mask]

st.dataframe(
    display_df
        .sort_values("Selling Price")
        .reset_index(drop=True)
        .style
        .format({"Selling Price": "₹{:,.0f}", "Original Price": "₹{:,.0f}", "Discount %": "{:.1f}%"}),
    use_container_width=True,
    height=500,
)

st.markdown(f"""
<div style="text-align: center; padding: 30px 0 10px 0; opacity: 0.4; font-size: 0.8rem;">
    Flipkart Mobiles Analytics Dashboard &bull; {len(filtered):,} listings shown
</div>
""", unsafe_allow_html=True)
