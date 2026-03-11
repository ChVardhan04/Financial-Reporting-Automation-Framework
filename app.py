import streamlit as st
from google.cloud import bigquery
import pandas as pd
import os
import altair as alt

PROJECT_ID = "financial-reporting-af"

st.set_page_config(layout="wide")

# Remove top padding
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## Financial Reporting Automation Dashboard")

# BigQuery Connection
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "financial-reporting-af-5a4714cdc929.json"
client = bigquery.Client(project=PROJECT_ID)

# Company Dropdown
company_query = f"""
SELECT DISTINCT company_name
FROM `{PROJECT_ID}.financial_reporting.dim_company`
ORDER BY company_name
"""
company_df = client.query(company_query).to_dataframe()

selected_company = st.selectbox("Company", company_df["company_name"])

# Query Data
query = f"""
SELECT 
    d.year,
    f.total_revenue,
    f.net_income,
    f.ebitda,
    f.roe,
    f.roa
FROM `{PROJECT_ID}.financial_reporting.fact_financials` f
JOIN `{PROJECT_ID}.financial_reporting.dim_company` c
ON f.company_id = c.company_id
JOIN `{PROJECT_ID}.financial_reporting.dim_date` d
ON f.date_id = d.date_id
WHERE c.company_name = '{selected_company}'
ORDER BY d.year
"""

df = client.query(query).to_dataframe()

# Calculations
df["revenue_growth_%"] = df["total_revenue"].pct_change() * 100
df["net_income_growth_%"] = df["net_income"].pct_change() * 100
df["total_revenue_b"] = df["total_revenue"] / 1000
df["net_income_b"] = df["net_income"] / 1000
df["ebitda_b"] = df["ebitda"] / 1000

# KPI Row
latest = df.iloc[-1]
k1, k2, k3, k4 = st.columns(4)

k1.metric("Revenue (B)", f"{latest['total_revenue_b']:,.2f}")
k2.metric("Net Income (B)", f"{latest['net_income_b']:,.2f}")
k3.metric("EBITDA (B)", f"{latest['ebitda_b']:,.2f}")
k4.metric("ROE (%)", f"{latest['roe']}")

# Chart Height Setting
chart_height = 220

c1, c2 = st.columns(2)

with c1:
    chart = alt.Chart(df).mark_line().encode(
        x="year:O",
        y="total_revenue_b:Q"
    ).properties(height=chart_height)
    st.altair_chart(chart, use_container_width=True)

with c2:
    chart = alt.Chart(df).mark_bar().encode(
        x="year:O",
        y="revenue_growth_%:Q"
    ).properties(height=chart_height)
    st.altair_chart(chart, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    chart = alt.Chart(df).mark_bar().encode(
        x="year:O",
        y="net_income_growth_%:Q"
    ).properties(height=chart_height)
    st.altair_chart(chart, use_container_width=True)

with c4:
    chart = alt.Chart(df).mark_line().encode(
        x="year:O",
        y="roe:Q"
    ).properties(height=chart_height)
    st.altair_chart(chart, use_container_width=True)