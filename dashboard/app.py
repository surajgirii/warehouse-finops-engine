import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
total_spend_query = f"SELECT SUM(total_credits * 3.0), SUM(wasted_compute_cost_usd) FROM mart_daily_team_finops {team_filter_clause}"
spend_res = conn.execute(total_spend_query).fetchone()
total_spend = spend_res[0] or 0.0
wasted_spend = spend_res[1] or 0.0
waste_pct = (wasted_spend / total_spend * 100) if total_spend > 0 else 0.0

zombie_query = "SELECT SUM(size_gb), SUM(monthly_storage_cost_usd) FROM mart_storage_governance WHERE is_zombie_table = TRUE"
zombie_res = conn.execute(zombie_query).fetchone()
zombie_gb = zombie_res[0] or 0.0
zombie_cost = zombie_res[1] or 0.0

pipeline_query = "SELECT AVG(success_rate_pct), AVG(sla_compliance_pct) FROM mart_pipeline_reliability"
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
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 FinOps Cost Attribution", 
    "🗑️ Storage Governance", 
    "🚨 Reliability Scorecard", 
    "🔔 Remediation Actions"
])

with tab1:
    st.subheader("Compute Spend Trends & Team Attribution")
    finops_df = conn.execute(f"SELECT * FROM mart_daily_team_finops {team_filter_clause} ORDER BY query_date ASC").fetchdf()
    
    if not finops_df.empty:
        finops_df["total_compute_cost_usd"] = finops_df["total_credits"] * 3.0
        finops_df["productive_cost_usd"] = finops_df["total_compute_cost_usd"] - finops_df["wasted_compute_cost_usd"]
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Daily Trend Line Chart
            daily_trend = finops_df.groupby("query_date", as_index=False)[["total_compute_cost_usd", "wasted_compute_cost_usd"]].sum()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=daily_trend["query_date"], y=daily_trend["total_compute_cost_usd"],
                mode="lines+markers", name="Total Compute ($)", line=dict(color="#3B82F6", width=2)
            ))
            fig_trend.add_trace(go.Scatter(
                x=daily_trend["query_date"], y=daily_trend["wasted_compute_cost_usd"],
                mode="lines+markers", name="Avoidable Waste ($)", fill="tozeroy", line=dict(color="#EF4444", width=2)
            ))
            fig_trend.update_layout(
                title="Daily Compute Spend vs. Avoidable Waste",
                xaxis_title="Date", yaxis_title="Cost (USD)",
                hovermode="x unified", legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with chart_col2:
            # Stacked Bar Chart by Team
            team_summary = finops_df.groupby("team_name", as_index=False)[["productive_cost_usd", "wasted_compute_cost_usd"]].sum()
            fig_team = px.bar(
                team_summary,
                x="team_name",
                y=["productive_cost_usd", "wasted_compute_cost_usd"],
                title="Productive vs. Wasted Compute by Team",
                labels={"value": "Cost (USD)", "team_name": "Team", "variable": "Spend Category"},
                color_discrete_map={"productive_cost_usd": "#10B981", "wasted_compute_cost_usd": "#EF4444"},
                barmode="stack"
            )
            fig_team.update_layout(legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_team, use_container_width=True)

    with st.expander("View Raw FinOps Data Table"):
        st.dataframe(finops_df.sort_values(by="total_credits", ascending=False), use_container_width=True)

with tab2:
    st.subheader("Zombie Tables & Storage Optimization")
    storage_df = conn.execute("SELECT * FROM mart_storage_governance ORDER BY monthly_storage_cost_usd DESC").fetchdf()
    
    zombie_only = storage_df[storage_df["is_zombie_table"] == True].head(10)
    if not zombie_only.empty:
        fig_zombie = px.bar(
            zombie_only.sort_values(by="monthly_storage_cost_usd", ascending=True),
            x="monthly_storage_cost_usd",
            y="full_table_name",
            color="team_name",
            orientation="h",
            title="Top 10 Costliest Zombie Tables (Unaccessed 90+ Days)",
            labels={"monthly_storage_cost_usd": "Monthly Cost ($)", "full_table_name": "Table Name", "team_name": "Owner Team"},
            hover_data=["size_gb", "days_since_last_access"]
        )
        st.plotly_chart(fig_zombie, use_container_width=True)

    with st.expander("View Full Storage Governance Inventory"):
        st.dataframe(storage_df, use_container_width=True)

with tab3:
    st.subheader("Pipeline Reliability & SLA Compliance Scorecard")
    reliability_df = conn.execute("SELECT * FROM mart_pipeline_reliability ORDER BY success_rate_pct ASC").fetchdf()
    
    if not reliability_df.empty:
        fig_rel = px.scatter(
            reliability_df,
            x="success_rate_pct",
            y="sla_compliance_pct",
            size="total_runs",
            color="team_name",
            hover_name="pipeline_name",
            title="Pipeline Health Matrix: Success Rate vs. SLA Compliance",
            labels={
                "success_rate_pct": "Success Rate (%)",
                "sla_compliance_pct": "SLA Compliance (%)",
                "team_name": "Team"
            }
        )
        fig_rel.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="85% SLA Target")
        fig_rel.add_vline(x=85, line_dash="dash", line_color="red", annotation_text="85% Success Target")
        st.plotly_chart(fig_rel, use_container_width=True)

    with st.expander("View Pipeline Reliability Scorecard Table"):
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