#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import streamlit as st
import plotly.express as px


# 
# # Load and clean dataset

# In[ ]:


@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\DELL\Downloads\superstore.csv\superstore.csv", encoding='ISO-8859-1')
    # Drop rows with missing Sales or Profit
    df = df.dropna(subset=['Sales', 'Profit'])
    # Convert Order Date to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    return df

df = load_data()


# 
# # Sidebar Filters

# In[ ]:


st.sidebar.header("Filter Options")
region_filter = st.sidebar.multiselect("Select Region:", options=df['Region'].unique(), default=df['Region'].unique())
category_filter = st.sidebar.multiselect("Select Category:", options=df['Category'].unique(), default=df['Category'].unique())
sub_category_filter = st.sidebar.multiselect("Select Sub-Category:", options=df['Sub-Category'].unique(), default=df['Sub-Category'].unique())

# Apply filters
filtered_df = df[
    (df['Region'].isin(region_filter)) &
    (df['Category'].isin(category_filter)) &
    (df['Sub-Category'].isin(sub_category_filter))
]


# 
# # KPIs

# In[ ]:


# ----------------------
# KPIs
# ----------------------
st.title("📊 Global Superstore Dashboard")

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()

st.metric("Total Sales", f"${total_sales:,.2f}")
st.metric("Total Profit", f"${total_profit:,.2f}")


# # Top 5 Customers by Sales

# In[ ]:


top_customers = filtered_df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(5).reset_index()
st.subheader("Top 5 Customers by Sales")
fig_customers = px.bar(top_customers, x='Customer Name', y='Sales', text='Sales', title="Top 5 Customers by Sales")
st.plotly_chart(fig_customers)


# # Sales & Profit by Category 

# In[ ]:


st.subheader("Sales & Profit by Category")
category_summary = filtered_df.groupby('Category')[['Sales','Profit']].sum().reset_index()
fig_category = px.bar(category_summary, x='Category', y=['Sales','Profit'], barmode='group', title="Sales vs Profit by Category")
st.plotly_chart(fig_category)


# #  Sales over Time

# st.subheader("Sales Over Time")
# sales_time = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
# fig_time = px.line(sales_time, x='Order Date', y='Sales', title="Sales Trend Over Time")
# st.plotly_chart(fig_time)
