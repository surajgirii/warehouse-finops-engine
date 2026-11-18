import os
from datetime import datetime, timedelta
import duckdb
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
np.random.seed(42)

DB_PATH = "data/warehouse.duckdb"
SCHEMA_PATH = "generator/schema.sql"

TEAMS = ["Data Engineering", "Product Analytics", "Finance BI", "Growth Marketing", "Machine Learning"]
WAREHOUSES = {"X-Small": 1, "Small": 2, "Medium": 4, "Large": 8, "X-Large": 16}
USERS = [fake.user_name() for _ in range(25)]

def initialize_database():
    os.makedirs("data", exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.execute(f.read())
    print("Database initialized successfully at", DB_PATH)
    return conn

def generate_query_logs(num_records=5000):
    print(f"Generating {num_records} query logs...")
    start_date = datetime.now() - timedelta(days=30)
    
    records = []
    for _ in range(num_records):
        query_id = fake.uuid4()
        user = np.random.choice(USERS)
        team = np.random.choice(TEAMS)
        wh_size = np.random.choice(list(WAREHOUSES.keys()), p=[0.4, 0.3, 0.15, 0.1, 0.05])
        
        # Inject intentional waste: Large warehouses scanning massive bytes with long execution times
        if wh_size in ["Large", "X-Large"] and np.random.rand() > 0.3:
            exec_time = np.random.uniform(300, 3600)
            bytes_scan = np.random.uniform(5e11, 5e12) # 500GB - 5TB
            query_text = "SELECT * FROM raw_events WHERE 1=1 -- FULL TABLE SCAN NO PARTITION"
        else:
            exec_time = np.random.uniform(1, 120)
            bytes_scan = np.random.uniform(1e7, 5e9)
            query_text = f"SELECT date_trunc('day', timestamp), count(*) FROM {fake.word()}_events GROUP BY 1"
            
        credits = (exec_time / 3600.0) * WAREHOUSES[wh_size] * np.random.uniform(0.9, 1.1)
        q_time = start_date + timedelta(seconds=int(np.random.uniform(0, 30*86400)))
        status = np.random.choice(["SUCCESS", "FAILED", "CANCELLED"], p=[0.88, 0.08, 0.04])
        
        records.append((query_id, user, team, wh_size, exec_time, credits, bytes_scan, query_text, q_time, status))
        
    return pd.DataFrame(records, columns=[
        "query_id", "user_name", "team_name", "warehouse_size", 
        "execution_time_seconds", "credits_used", "bytes_scanned", 
        "query_text", "start_time", "status"
    ])

def generate_storage_snapshots():
    print("Generating storage snapshots...")
    tables = [f"{schema}.tbl_{fake.word()}" for schema in ["staging", "analytics", "marts", "raw"] for _ in range(15)]
    
    records = []
    snapshot_date = datetime.now().date()
    for tbl in tables:
        team = np.random.choice(TEAMS)
        size_gb = np.random.exponential(scale=150.0) # Distribution of table sizes
        
        # Inject zombie tables (not accessed in 90+ days)
        if np.random.rand() > 0.75:
            last_accessed = snapshot_date - timedelta(days=int(np.random.uniform(90, 250)))
        else:
            last_accessed = snapshot_date - timedelta(days=int(np.random.uniform(0, 5)))
            
        creation_date = snapshot_date - timedelta(days=int(np.random.uniform(100, 500)))
        
        records.append((snapshot_date, tbl.split('.')[1], tbl.split('.')[0], team, size_gb, last_accessed, creation_date))
        
    return pd.DataFrame(records, columns=[
        "snapshot_date", "table_name", "schema_name", "team_name", 
        "size_gb", "last_accessed_date", "creation_date"
    ])

def generate_pipeline_runs(num_records=1000):
    print(f"Generating {num_records} pipeline execution logs...")
    start_date = datetime.now() - timedelta(days=30)
    pipelines = [f"pipe_{fake.word()}_{i}" for i in range(20)]
    
    records = []
    for _ in range(num_records):
        run_id = fake.uuid4()
        pipe = np.random.choice(pipelines)
        team = np.random.choice(TEAMS)
        p_start = start_date + timedelta(seconds=int(np.random.uniform(0, 30*86400)))
        
        sla_target = np.random.choice([30, 60, 120, 240])
        actual_duration = np.random.exponential(scale=float(sla_target) * 0.6)
        
        # Inject failing pipelines or SLA breaches
        if np.random.rand() > 0.85:
            status = "FAILED"
            err_msg = np.random.choice([
                "SchemaMismatch: Column 'user_id' type changed from INT to VARCHAR",
                "TimeoutError: Snowflake warehouse connection dropped after 3600s",
                "DependencyError: Upstream source table raw_events is empty"
            ])
            actual_duration *= 2.0
        else:
            status = "SUCCESS"
            err_msg = None
            
        p_end = p_start + timedelta(minutes=actual_duration)
        
        records.append((run_id, pipe, team, p_start, p_end, status, err_msg, int(sla_target), actual_duration))
        
    return pd.DataFrame(records, columns=[
        "run_id", "pipeline_name", "team_name", "start_time", 
        "end_time", "status", "error_message", "sla_target_minutes", "actual_duration_minutes"
    ])

if __name__ == "__main__":
    conn = initialize_database()
    
    df_queries = generate_query_logs(6000)
    df_storage = generate_storage_snapshots()
    df_pipelines = generate_pipeline_runs(1200)
    
    conn.execute("DELETE FROM raw_query_logs;")
    conn.execute("DELETE FROM raw_storage_snapshots;")
    conn.execute("DELETE FROM raw_pipeline_runs;")
    
    conn.register("df_queries_temp", df_queries)
    conn.register("df_storage_temp", df_storage)
    conn.register("df_pipelines_temp", df_pipelines)
    
    conn.execute("INSERT INTO raw_query_logs SELECT * FROM df_queries_temp;")
    conn.execute("INSERT INTO raw_storage_snapshots SELECT * FROM df_storage_temp;")
    conn.execute("INSERT INTO raw_pipeline_runs SELECT * FROM df_pipelines_temp;")
    
    print("\nTelemetry generation complete! Loaded into DuckDB.")
    print(f"- Query Logs: {len(df_queries)} rows")
    print(f"- Storage Snapshots: {len(df_storage)} rows")
    print(f"- Pipeline Runs: {len(df_pipelines)} rows")
    
    conn.close()