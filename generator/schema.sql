-- Raw landing schema for telemetry metadata

CREATE TABLE IF NOT EXISTS raw_query_logs (
    query_id VARCHAR,
    user_name VARCHAR,
    team_name VARCHAR,
    warehouse_size VARCHAR,
    execution_time_seconds DOUBLE,
    credits_used DOUBLE,
    bytes_scanned DOUBLE,
    query_text VARCHAR,
    start_time TIMESTAMP,
    status VARCHAR
);

CREATE TABLE IF NOT EXISTS raw_storage_snapshots (
    snapshot_date DATE,
    table_name VARCHAR,
    schema_name VARCHAR,
    team_name VARCHAR,
    size_gb DOUBLE,
    last_accessed_date DATE,
    creation_date DATE
);

CREATE TABLE IF NOT EXISTS raw_pipeline_runs (
    run_id VARCHAR,
    pipeline_name VARCHAR,
    team_name VARCHAR,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR, -- 'SUCCESS', 'FAILED', 'RETRY'
    error_message VARCHAR,
    sla_target_minutes INT,
    actual_duration_minutes DOUBLE
);