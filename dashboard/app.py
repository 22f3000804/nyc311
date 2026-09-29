import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="NYC 311 Equity Analysis", layout="wide")
st.title("NYC 311: Resolution Time by Neighborhood Income")
st.markdown("Comparing complaint resolution times across income quartiles (Q1 = lowest income, Q4 = highest)")

con = duckdb.connect('nyc311.db', read_only=True)

complaint_types = con.execute("""
    SELECT DISTINCT complaint_type FROM requests_with_income
    GROUP BY complaint_type HAVING COUNT(*) >= 30 ORDER BY complaint_type
""").fetchdf()['complaint_type'].tolist()

selected = st.selectbox("Select complaint type", complaint_types)

data = con.execute(f"""
    SELECT income_quartile,
           MEDIAN(DATEDIFF('hour', CAST(created_date AS TIMESTAMP), CAST(closed_date AS TIMESTAMP))) AS median_hrs,
           COUNT(*) AS n
    FROM requests_with_income
    WHERE complaint_type = '{selected}'
    GROUP BY income_quartile ORDER BY income_quartile
""").fetchdf()

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(data, x='income_quartile', y='median_hrs',
                 labels={'income_quartile': 'Income Quartile', 'median_hrs': 'Median Resolution Time (hrs)'},
                 title=f"{selected}: Median Resolution Time by Income Quartile")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Q1 (lowest income)", f"{data.iloc[0]['median_hrs']:.0f} hrs", f"n={data.iloc[0]['n']}")
    st.metric("Q4 (highest income)", f"{data.iloc[-1]['median_hrs']:.0f} hrs", f"n={data.iloc[-1]['n']}")

    if len(data) == 4 and data['n'].min() >= 10:
        q1 = con.execute(f"""SELECT DATEDIFF('hour', CAST(created_date AS TIMESTAMP), CAST(closed_date AS TIMESTAMP)) as hrs
            FROM requests_with_income WHERE complaint_type = '{selected}' AND income_quartile = 1""").fetchdf()['hrs']
        q4 = con.execute(f"""SELECT DATEDIFF('hour', CAST(created_date AS TIMESTAMP), CAST(closed_date AS TIMESTAMP)) as hrs
            FROM requests_with_income WHERE complaint_type = '{selected}' AND income_quartile = 4""").fetchdf()['hrs']
        _, pval = stats.mannwhitneyu(q1, q4)
        sig = " Statistically significant" if pval < 0.05 else " Not statistically significant"
        st.write(f"**p-value:** {pval:.4f}")
        st.write(sig)

st.markdown("---")

st.markdown("Data: [NYC Open Data 311](https://data.cityofnycollections.gov) · [Census ACS 5-Year](https://data.census.gov)")