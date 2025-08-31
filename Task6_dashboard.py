
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Global Superstore Dashboard", layout="wide")

@st.cache_data(show_spinner=False)
def load_data():
    # Try common relative locations to make it work both locally and on Streamlit Cloud
    candidates = [
        Path(__file__).parent / "superstore.csv",
        Path(__file__).parent / "data" / "superstore.csv",
        Path("superstore.csv"),
        Path("data/superstore.csv"),
    ]
    csv_path = next((p for p in candidates if p.exists()), None)
    if csv_path is None:
        raise FileNotFoundError(
            "Could not find 'superstore.csv'. Place it in the same folder as this app "
            "or inside a 'data/' folder in the repo."
        )

    df = pd.read_csv(csv_path, encoding="ISO-8859-1")

    # --- Normalize column names so both 'Order.Date' and 'Order Date' styles work ---
    cols = df.columns.str.replace(r"\.", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    df.columns = cols
    df = df.rename(columns={"Sub Category": "Sub-Category"})  # unify naming

    # Basic validations
    required = ["Sales", "Profit", "Order Date", "Region", "Category", "Sub-Category", "Customer Name"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}. Found columns: {list(df.columns)}")

    # Cleaning
    df = df.dropna(subset=["Sales", "Profit"])
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df = df.dropna(subset=["Order Date"])

    return df

# Load data
try:
    df = load_data()
except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Options")
with st.sidebar:
    region_filter = st.multiselect("Select Region:", options=sorted(df["Region"].dropna().unique().tolist()),
                                   default=sorted(df["Region"].dropna().unique().tolist()))
    category_filter = st.multiselect("Select Category:", options=sorted(df["Category"].dropna().unique().tolist()),
                                     default=sorted(df["Category"].dropna().unique().tolist()))
    sub_category_filter = st.multiselect("Select Sub-Category:", options=sorted(df["Sub-Category"].dropna().unique().tolist()),
                                         default=sorted(df["Sub-Category"].dropna().unique().tolist()))

# Apply filters safely
filtered_df = df.copy()
if region_filter:
    filtered_df = filtered_df[filtered_df["Region"].isin(region_filter)]
if category_filter:
    filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
if sub_category_filter:
    filtered_df = filtered_df[filtered_df["Sub-Category"].isin(sub_category_filter)]

st.title("📊 Global Superstore Dashboard")

if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()

# KPIs
kpi_cols = st.columns(2)
with kpi_cols[0]:
    total_sales = filtered_df["Sales"].sum()
    st.metric("Total Sales", f"${total_sales:,.2f}")
with kpi_cols[1]:
    total_profit = filtered_df["Profit"].sum()
    st.metric("Total Profit", f"${total_profit:,.2f}")

# Top 5 Customers by Sales
st.subheader("Top 5 Customers by Sales")
top_customers = (
    filtered_df.groupby("Customer Name", as_index=False)["Sales"].sum()
    .sort_values("Sales", ascending=False)
    .head(5)
)
fig_customers = px.bar(top_customers, x="Customer Name", y="Sales", text="Sales",
                       title="Top 5 Customers by Sales")
st.plotly_chart(fig_customers, use_container_width=True)

# Sales & Profit by Category
st.subheader("Sales & Profit by Category")
category_summary = (
    filtered_df.groupby("Category", as_index=False)[["Sales", "Profit"]].sum()
    .sort_values("Sales", ascending=False)
)
fig_category = px.bar(category_summary, x="Category", y=["Sales", "Profit"], barmode="group",
                      title="Sales vs Profit by Category")
st.plotly_chart(fig_category, use_container_width=True)

# Sales over Time
st.subheader("Sales Over Time")
sales_time = (
    filtered_df.groupby("Order Date", as_index=False)["Sales"].sum()
    .sort_values("Order Date")
)
fig_time = px.line(sales_time, x="Order Date", y="Sales", title="Sales Trend Over Time")
st.plotly_chart(fig_time, use_container_width=True)

# Debug/Help section (optional for you during deployment)
with st.expander("Debug: Columns & Sample", expanded=False):
    st.write("Columns:", list(df.columns))
    st.write("Row count:", len(df))
    st.dataframe(filtered_df.head())
