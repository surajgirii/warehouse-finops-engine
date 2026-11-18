import duckdb
import pandas as pd
import numpy as np

DB_PATH = "data/warehouse.duckdb"

def run_finops_intelligence():
    conn = duckdb.connect(DB_PATH)
    
    print("="*60)
    print(" 🚀 ENTERPRISE FINOPS & RELIABILITY INTELLIGENCE REPORT")
    print("="*60)
    
    # 1. FinOps Cost Spike & Waste Analysis
    print("\n--- [1] FINOPS COST ANOMALIES & TOP WASTE SPENDERS ---")
    query_waste = """
        SELECT 
            team_name,
            SUM(total_compute_cost_usd) AS total_spend,
            SUM(wasted_compute_cost_usd) AS wasted_spend,
            ROUND((SUM(wasted_compute_cost_usd) / NULLIF(SUM(total_compute_cost_usd), 0)) * 100, 2) AS waste_pct,
            SUM(unoptimized_scan_count) AS total_unoptimized_scans
        FROM mart_daily_team_finops
        GROUP BY team_name
        ORDER BY wasted_spend DESC;
    """
    df_waste = conn.execute(query_waste.strip()).fetchdf()
    print(df_waste.to_string(index=False))
    
    # 2. Storage & Zombie Table Governance
    print("\n--- [2] STORAGE GOVERNANCE & ZOMBIE TABLE WASTE ---")
    query_storage = """
        SELECT 
            team_name,
            COUNT(full_table_name) AS zombie_table_count,
            ROUND(SUM(size_gb), 2) AS total_zombie_size_gb,
            ROUND(SUM(monthly_storage_cost_usd), 2) AS monthly_wasted_storage_usd,
            governance_action
        FROM mart_storage_governance
        WHERE is_zombie_table = TRUE
        GROUP BY team_name, governance_action
        ORDER BY monthly_wasted_storage_usd DESC;
    """
    df_storage = conn.execute(query_storage.strip()).fetchdf()
    print(df_storage.to_string(index=False))
    
    # 3. Pipeline Reliability & SLA Scorecard
    print("\n--- [3] PIPELINE RELIABILITY & SLA BOTTLENECK SCORECARD ---")
    query_reliability = """
        SELECT 
            pipeline_name,
            team_name,
            total_runs,
            failed_runs,
            success_rate_pct,
            sla_compliance_pct,
            avg_duration_mins,
            avg_failure_recovery_mins
        FROM mart_pipeline_reliability
        WHERE success_rate_pct < 90.0 OR sla_compliance_pct < 90.0
        ORDER BY success_rate_pct ASC
        LIMIT 10;
    """
    df_reliability = conn.execute(query_reliability.strip()).fetchdf()
    print(df_reliability.to_string(index=False))
    
    conn.close()
    print("\n" + "="*60)
    print(" Intelligence Engine execution complete.")
    print("="*60)

if __name__ == "__main__":
    run_finops_intelligence()