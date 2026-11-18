import duckdb

DB_PATH = "data/warehouse.duckdb"
SQL_FILES = [
    "models/staging/stg_telemetry.sql",
    "models/marts/mart_finops_and_reliability.sql"
]

def run_models():
    conn = duckdb.connect(DB_PATH)
    for sql_file in SQL_FILES:
        print(f"Executing {sql_file}...")
        with open(sql_file, "r") as f:
            conn.execute(f.read())
            
    # Verify Gold Marts
    marts = ["mart_daily_team_finops", "mart_storage_governance", "mart_pipeline_reliability"]
    print("\nGold Marts Built Successfully:")
    for mart in marts:
        count = conn.execute(f"SELECT COUNT(*) FROM {mart}").fetchone()[0]
        print(f"- {mart}: {count} rows")
        
    conn.close()

if __name__ == "__main__":
    run_models()