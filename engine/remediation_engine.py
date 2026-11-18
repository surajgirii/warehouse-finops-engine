import duckdb
import json
import pandas as pd

DB_PATH = "data/warehouse.duckdb"

def generate_remediation_alerts():
    conn = duckdb.connect(DB_PATH)
    
    print("="*60)
    print(" 🔔 AUTOMATED FINOPS & RELIABILITY REMEDIATION ALERTS")
    print("="*60)
    
    alerts = []
    
    # 1. FinOps Cost Waste Alerts
    waste_query = """
        SELECT team_name, wasted_compute_cost_usd, unoptimized_scan_count
        FROM mart_daily_team_finops
        WHERE wasted_compute_cost_usd > 1000
        ORDER BY wasted_compute_cost_usd DESC;
    """
    waste_rows = conn.execute(waste_query).fetchall()
    for row in waste_rows:
        team, wasted_cost, unopt_count = row
        alert = {
            "channel": "#finops-alerts",
            "severity": "HIGH",
            "title": f"💰 FinOps Cost Waste Detected: {team}",
            "message": f"Team {team} incurred ${wasted_cost:,.2f} in avoidable compute waste across {unopt_count} unoptimized table scans or oversized warehouses.",
            "recommended_action": "Review top queries, add partition filters to large tables, and downsize oversized warehouse clusters."
        }
        alerts.append(alert)

    # 2. Storage Governance / Zombie Table Alerts
    zombie_query = """
        SELECT team_name, full_table_name, size_gb, monthly_storage_cost_usd, days_since_last_access
        FROM mart_storage_governance
        WHERE is_zombie_table = TRUE AND size_gb > 100
        ORDER BY monthly_storage_cost_usd DESC
        LIMIT 5;
    """
    zombie_rows = conn.execute(zombie_query).fetchall()
    for row in zombie_rows:
        team, table_name, size_gb, cost, days = row
        alert = {
            "channel": "#data-governance",
            "severity": "MEDIUM",
            "title": f"🗑️ Zombie Table Storage Waste: {table_name}",
            "message": f"Table `{table_name}` owned by {team} is {size_gb:.1f} GB, costs ${cost:.2f}/month, and has not been accessed in {days} days.",
            "recommended_action": "Archive table to cold storage or drop table if no longer required."
        }
        alerts.append(alert)

    # 3. Pipeline Failure / SLA Breach Alerts
    pipeline_query = """
        SELECT pipeline_name, team_name, success_rate_pct, sla_compliance_pct, failed_runs
        FROM mart_pipeline_reliability
        WHERE success_rate_pct < 85.0
        ORDER BY success_rate_pct ASC
        LIMIT 5;
    """
    pipe_rows = conn.execute(pipeline_query).fetchall()
    for row in pipe_rows:
        pipe, team, success_pct, sla_pct, failures = row
        alert = {
            "channel": "#data-engineering-alerts",
            "severity": "CRITICAL",
            "title": f"🚨 Pipeline Reliability Failure: {pipe}",
            "message": f"Pipeline `{pipe}` managed by {team} has a success rate of only {success_pct}% with {failures} recent failures.",
            "recommended_action": "Inspect schema drift, check upstream dependencies, and verify error logs in DuckDB/orchestrator."
        }
        alerts.append(alert)

    conn.close()

    # Print Formatted JSON Alerts (Ready for Webhook / Slack API)
    print(f"\nGenerated {len(alerts)} Actionable Webhook Alerts:\n")
    print(json.dumps(alerts, indent=2))
    
    # Save alerts locally as an audit artifact
    with open("data/latest_alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)
    print("\nSaved alert payloads to `data/latest_alerts.json`")
    print("="*60)

if __name__ == "__main__":
    generate_remediation_alerts()