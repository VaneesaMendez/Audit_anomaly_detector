"""
Simple Internal Audit Dashboard
-----------------------------------
A beginner-friendly dashboard built with Streamlit.

How to run it:
    1. Make sure audit_analytics.py has been run first.
    2. pip install streamlit pandas
    3. streamlit run dashboard.py
    4. It opens automatically in browser.
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Transaction Risk Dashboard", layout="wide")

# =========================================================
# Load the results created by audit_analytics.py
# =========================================================
df = pd.read_csv("all_transactions.csv")

# =========================================================
# Title and short intro
# =========================================================
st.title("Transaction Risk Dashboard")
st.write(
    "This dashboard shows the results of an automated scan that checked "
    "every transaction for six common audit red flags: self-approval, "
    "duplicate payments, amounts just under the approval limit, round "
    "numbers, unusually high amounts, and weekend activity."
)

# =========================================================
# Top summary numbers (simple counting and filtering)
# =========================================================
total_transactions = len(df)
flagged_df = df[df["risk_score"] > 0]
high_risk_df = df[df["risk_level"] == "High"]
value_flagged = flagged_df["amount"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total transactions", total_transactions)
col2.metric("Flagged for review", len(flagged_df))
col3.metric("High risk", len(high_risk_df))
col4.metric("Value flagged", f"£{value_flagged:,.0f}")

st.divider()

# =========================================================
# Chart 1: how many transactions fall into each risk level
# =========================================================
st.subheader("Transactions by risk level")
risk_level_counts = df["risk_level"].value_counts()
st.bar_chart(risk_level_counts)

# =========================================================
# Chart 2: which rule caught the most transactions
# =========================================================
st.subheader("Which rule caught the most transactions")

rule_names = ["Self-approved", "Just under approval limit", "Round number",
              "Unusually high amount", "Weekend transaction", "Possible duplicate payment"]

rule_counts = {}
for rule in rule_names:
    count = df["flags_text"].str.contains(rule).sum()
    rule_counts[rule] = count

rule_counts_series = pd.Series(rule_counts)
st.bar_chart(rule_counts_series)

st.divider()

# =========================================================
# Chart 3: flagged transactions by department
# =========================================================
st.subheader("Flagged transactions by department")
department_counts = flagged_df["department"].value_counts()
st.bar_chart(department_counts)

st.divider()

# =========================================================
# Table: let the user filter and look at the actual transactions
# =========================================================
st.subheader("Look at the transactions yourself")

chosen_level = st.selectbox("Show me transactions with risk level:",
                             ["All", "High", "Medium", "Low", "Clear"])

if chosen_level == "All":
    table_to_show = df
else:
    table_to_show = df[df["risk_level"] == chosen_level]

st.write(f"Showing {len(table_to_show)} transactions")
st.dataframe(table_to_show, use_container_width=True)

st.divider()
st.caption(
    "Note: all data here is made up by audit_analytics.py for practice purposes, "
    "not a real company's records."
)
