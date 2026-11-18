-- Silver Layer: Standardized & Enriched Telemetry Views

CREATE OR REPLACE VIEW stg_queries AS
SELECT
    query_id,
    user_name,
    team_name,
    warehouse_size,
    CAST(start_time AS DATE) AS query_date,
    start_time,
    execution_time_seconds,
    credits_used,
    ROUND(credits_used * 3.00, 4) AS estimated_cost_usd, -- $3.00 per compute credit
    ROUND(bytes_scanned / 1e9, 4) AS gb_scanned,
    query_text,
    status,
    CASE 
        WHEN query_text ILIKE '%SELECT *%' AND bytes_scanned > 1e11 THEN TRUE 
        ELSE FALSE 
    END AS is_unoptimized_scan,
    CASE 
        WHEN warehouse_size IN ('Large', 'X-Large') AND execution_time_seconds < 10 THEN TRUE 
        ELSE FALSE 
    END AS is_oversized_warehouse
FROM raw_query_logs;

CREATE OR REPLACE VIEW stg_storage AS
SELECT
    snapshot_date,
    schema_name,
    table_name,
    schema_name || '.' || table_name AS full_table_name,
    team_name,
    ROUND(size_gb, 2) AS size_gb,
    ROUND((size_gb / 1024.0) * 23.00, 2) AS monthly_storage_cost_usd, -- $23/TB/month
    last_accessed_date,
    creation_date,
    DATE_DIFF('day', last_accessed_date, snapshot_date) AS days_since_last_access,
    CASE 
        WHEN DATE_DIFF('day', last_accessed_date, snapshot_date) >= 90 THEN TRUE 
        ELSE FALSE 
    END AS is_zombie_table
FROM raw_storage_snapshots;

CREATE OR REPLACE VIEW stg_pipelines AS
SELECT
    run_id,
    pipeline_name,
    team_name,
    CAST(start_time AS DATE) AS run_date,
    start_time,
    end_time,
    status,
    error_message,
    sla_target_minutes,
    ROUND(actual_duration_minutes, 2) AS actual_duration_minutes,
    CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END AS is_failure,
    CASE WHEN actual_duration_minutes > sla_target_minutes THEN 1 ELSE 0 END AS is_sla_breach
FROM raw_pipeline_runs;