# ⚡ Enterprise Data Warehouse FinOps & Pipeline Reliability Intelligence Engine

An end-to-end data platform observability and FinOps engineering engine built locally using Python, DuckDB, SQL, and Streamlit. This project monitors cloud warehouse compute spend, detects storage waste (zombie tables), tracks pipeline reliability SLAs, and generates automated remediation alerts.

---

## 🚀 Project Overview & Architecture

Modern data platforms face two massive operational bottlenecks: **uncontrolled cloud compute/storage waste** and **silent pipeline failures**. This project simulates an enterprise-grade telemetry ecosystem and automates intelligence across three core pillars:

1. **FinOps Cost Attribution:** Tracks team-level query compute spend, identifies unoptimized table scans, and calculates avoidable dollar waste.
2. **Storage Governance:** Flags "zombie tables" (datasets unaccessed for 90+ days) to eliminate monthly cloud storage overhead.
3. **Pipeline Reliability Scorecard:** Monitors DAG run success rates, SLA compliance, and failure recovery times.

### 🏛️ Medallion Architecture

```text
[ Raw Telemetry (Generator) ] 
       │
       ▼ (Bronze Landing Tables)
[ DuckDB Analytical Engine ] 
       │
       ▼ (Silver: stg_queries, stg_storage, stg_pipelines)
[ Standardized & Enriched Views ] 
       │
       ▼ (Gold: mart_daily_team_finops, mart_storage_governance, mart_pipeline_reliability)
[ Intelligence Engine & Streamlit Dashboard ]
```

---

## 🛠️ Tech Stack

* **Storage & Compute:** **DuckDB** (Blazing-fast in-process OLAP SQL database)
* **Transformation:** Modular SQL scripts following Medallion Architecture
* **Intelligence & Logic:** **Python** (Pandas, NumPy, automated anomaly and remediation algorithms)
* **Dashboard UI:** **Streamlit** (Interactive executive and engineering web cockpit)
* **Simulation:** **Faker & Pandas** (Generates realistic enterprise metadata and failure logs)

---

## 📂 Project Directory Structure

```text
warehouse-finops-engine/
│
├── data/                       # Local DuckDB database and audit payloads
├── models/                     # SQL transformation models
│   ├── staging/                # Silver layer views (stg_telemetry.sql)
│   └── marts/                  # Gold layer tables (mart_finops_and_reliability.sql)
│
├── generator/                  # Synthetic telemetry generation
│   ├── schema.sql              # Raw landing table definitions
│   └── generate_logs.py        # Enterprise log simulation script
│
├── engine/                     # Intelligence & remediation logic
│   ├── finops_engine.py        # Cost spike & waste analytics
│   └── remediation_engine.py   # Webhook & alert payload generator
│
├── dashboard/                  # Streamlit web interface
│   └── app.py                  # Executive cockpit UI
│
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## ⚙️ How to Run Locally

### 1. Clone the Repository & Install Dependencies
```bash
git clone https://github.com/surajgirii/warehouse-finops-engine.git
cd warehouse-finops-engine
pip install -r requirements.txt
```

### 2. Generate Synthetic Telemetry & Load Database
```bash
python generator/generate_logs.py
```

### 3. Run the SQL Transformations (Silver & Gold Layers)
```bash
python models/run_transformations.py
```

### 4. Execute the Intelligence & Remediation Engine
```bash
python engine/finops_engine.py
python engine/remediation_engine.py
```

### 5. Launch the Interactive Streamlit Dashboard
```bash
python -m streamlit run dashboard/app.py
```
*(Open your browser at `http://localhost:8501`)*

---

## 📊 Dashboard Preview

* **FinOps Tab:** Breakdown of compute spend and avoidable waste per team.
* **Storage Governance Tab:** Identification of zombie tables racking up unneeded cloud costs.
* **Reliability Scorecard Tab:** Pipeline success rates and SLA compliance tracking.
* **Remediation Actions Tab:** Actionable JSON alert payloads formatted for Slack and PagerDuty.