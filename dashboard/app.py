import streamlit as st
import duckdb
import pandas as pd
import json

# Page Config
st.set_page_config(
    page_title="Data Warehouse FinOps & Reliability Engine",
    page_icon="⚡",
    layout="wide"
)

DB_PATH = "data/warehouse.duckdb"

@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

conn = get_connection()

# App Header
st.title("⚡ Enterprise Data Warehouse FinOps & Pipeline Reliability Intelligence")
st.markdown("Monitor cloud compute spend, eliminate storage waste, enforce pipeline SLAs, and review automated remediation workflows.")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("🔍 Control Center")
selected_team = st.sidebar.selectbox(
    "Filter by Team", 
    ["All Teams", "Data Engineering", "Product Analytics", "Finance BI", "Growth Marketing", "Machine Learning"]
)

team_filter_clause = "" if selected_team == "All Teams" else f"WHERE team_name = '{selected_team}'"

# Fetch Summary Metrics
total_spend_query = f"SELECT SUM(total_compute_cost_usd), SUM(wasted_compute_cost_usd) FROM mart_daily_team_finops {team_filter_clause}"
spend_res = conn.execute(total_spend_query).fetchone()
total_spend = spend_res[0] or 0.0
wasted_spend = spend_res[1] or 0.0
waste_pct = (wasted_spend / total_spend * 100) if total_spend > 0 else 0.0

zombie_query = f"SELECT SUM(size_gb), SUM(monthly_storage_cost_usd) FROM mart_storage_governance WHERE is_zombie_table = TRUE"
zombie_res = conn.execute(zombie_query).fetchone()
zombie_gb = zombie_res[0] or 0.0
zombie_cost = zombie_res[1] or 0.0

pipeline_query = f"SELECT AVG(success_rate_pct), AVG(sla_compliance_pct) FROM mart_pipeline_reliability"
pipe_res = conn.execute(pipeline_query).fetchone()
avg_success = pipe_res[0] or 100.0
avg_sla = pipe_res[1] or 100.0

# Top KPI Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Compute Spend", f"${total_spend:,.2f}")
col2.metric("Avoidable Compute Waste", f"${wasted_spend:,.2f}", f"{waste_pct:.1f}% of spend", delta_color="inverse")
col3.metric("Zombie Storage Waste", f"${zombie_cost:,.2f}/mo", f"{zombie_gb:,.1f} GB")
col4.metric("Avg Pipeline Success", f"{avg_success:.1f}%")
col5.metric("SLA Compliance", f"{avg_sla:.1f}%")

st.markdown("---")

# Tabs for Detailed Analysis
tab1, tab2, tab3, tab4 = st.tabs(["💰 FinOps Cost Attribution", "🗑️ Storage Governance", "🚨 Reliability Scorecard", "🔔 Remediation Actions"])

with tab1:
    st.subheader("Team Compute Spend & Inefficient Query Waste")
    finops_df = conn.execute(f"SELECT * FROM mart_daily_team_finops {team_filter_clause} ORDER BY total_compute_cost_usd DESC").fetchdf()
    st.dataframe(finops_df, use_container_width=True)

with tab2:
    st.subheader("Zombie Tables & Storage Optimization")
    storage_df = conn.execute(f"SELECT * FROM mart_storage_governance ORDER BY monthly_storage_cost_usd DESC").fetchdf()
    st.dataframe(storage_df, use_container_width=True)

with tab3:
    st.subheader("Pipeline Reliability & SLA Compliance Scorecard")
    reliability_df = conn.execute(f"SELECT * FROM mart_pipeline_reliability ORDER BY success_rate_pct ASC").fetchdf()
    st.dataframe(reliability_df, use_container_width=True)

with tab4:
    st.subheader("Automated Webhook & Remediation Alerts")
    try:
        with open("data/latest_alerts.json", "r") as f:
            alerts = json.load(f)
            for alert in alerts:
                severity_color = "🔴" if alert["severity"] == "CRITICAL" else "🟠" if alert["severity"] == "HIGH" else "🟡"
                with st.expander(f"{severity_color} [{alert['severity']}] {alert['title']} ({alert['channel']})"):
                    st.write(f"**Message:** {alert['message']}")
                    st.info(f"**Recommended Action:** {alert['recommended_action']}")
    except FileNotFoundError:
        st.warning("No alert payloads found. Run `python engine/remediation_engine.py` first to generate alerts.")

# Footer
st.markdown("---")
st.markdown("💡 *Enterprise Data Warehouse FinOps & Pipeline Reliability Intelligence Engine | Local DuckDB Instance*")