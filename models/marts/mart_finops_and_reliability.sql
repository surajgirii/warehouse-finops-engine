-- Gold Layer: Business & Engineering Data Marts

-- 1. Daily FinOps Cost Attribution by Team
CREATE OR REPLACE TABLE mart_daily_team_finops AS
SELECT
    query_date,
    team_name,
    COUNT(query_id) AS total_queries,
    ROUND(SUM(credits_used), 2) AS total_credits,
    ROUND(SUM(estimated_cost_usd), 2) AS total_compute_cost_usd,
    ROUND(SUM(CASE WHEN is_unoptimized_scan OR is_oversized_warehouse THEN estimated_cost_usd ELSE 0 END), 2) AS wasted_compute_cost_usd,
    SUM(CASE WHEN is_unoptimized_scan THEN 1 ELSE 0 END) AS unoptimized_scan_count,
    ROUND(SUM(gb_scanned) / 1024.0, 2) AS total_tb_scanned
FROM stg_queries
GROUP BY 1, 2
ORDER BY query_date DESC, total_compute_cost_usd DESC;

-- 2. Storage & Zombie Table Governance Mart
CREATE OR REPLACE TABLE mart_storage_governance AS
SELECT
    team_name,
    schema_name,
    full_table_name,
    size_gb,
    monthly_storage_cost_usd,
    days_since_last_access,
    is_zombie_table,
    CASE 
        WHEN is_zombie_table AND size_gb > 50 THEN 'ARCHIVE_OR_DROP'
        WHEN is_zombie_table THEN 'REVIEW_DEPRECATION'
        ELSE 'HEALTHY'
    END AS governance_action
FROM stg_storage
ORDER BY monthly_storage_cost_usd DESC;

-- 3. Pipeline Reliability & SLA Scorecard
CREATE OR REPLACE TABLE mart_pipeline_reliability AS
SELECT
    pipeline_name,
    team_name,
    COUNT(run_id) AS total_runs,
    SUM(is_failure) AS failed_runs,
    ROUND((1.0 - (SUM(is_failure) * 1.0 / COUNT(run_id))) * 100, 2) AS success_rate_pct,
    SUM(is_sla_breach) AS sla_breaches,
    ROUND((1.0 - (SUM(is_sla_breach) * 1.0 / COUNT(run_id))) * 100, 2) AS sla_compliance_pct,
    ROUND(AVG(actual_duration_minutes), 2) AS avg_duration_mins,
    MAX(sla_target_minutes) AS sla_target_mins,
    -- Estimate Mean Time To Recovery (MTTR) proxy based on failed run overrun
    ROUND(AVG(CASE WHEN is_failure = 1 THEN actual_duration_minutes ELSE NULL END), 2) AS avg_failure_recovery_mins
FROM stg_pipelines
GROUP BY 1, 2
ORDER BY success_rate_pct ASC, sla_breaches DESC;