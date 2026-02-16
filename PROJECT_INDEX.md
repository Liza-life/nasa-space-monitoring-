# 🚀 NASA Space Monitoring Platform - Project Index

## 📁 Project Structure Overview

```
nasa-space-monitoring/
│
├── 📄 README.md                          # Main project documentation
├── 📄 requirements.txt                   # Python dependencies
├── 📄 .env.example                       # Environment variables template
├── 📄 docker-compose.yml                # Docker orchestration
├── 🔧 setup.sh                          # Automated setup script
│
├── 📂 config/                           # Configuration files
│   └── api_endpoints.yaml               # NASA API endpoints configuration
│
├── 📂 src/                              # Source code
│   ├── 📂 ingestion/                    # Data collection modules
│   │   ├── base_client.py               # ⭐ Base API client (retry, rate limiting)
│   │   └── neo_ingestion.py             # ⭐ NEO asteroid data ingestion
│   │
│   ├── 📂 transformation/               # Data processing modules
│   │   └── neo_transformer.py           # ⭐ Data cleaning & enrichment
│   │
│   ├── 📂 orchestration/                # Airflow workflows
│   │   └── dags/
│   │       └── nasa_pipeline_dag.py     # ⭐ Main ETL pipeline DAG
│   │
│   └── 📂 dashboard/                    # Visualization
│       └── app.py                       # ⭐ Streamlit dashboard app
│
├── 📂 data/                             # Data storage (gitignored)
│   ├── raw/                             # Bronze layer - raw data
│   ├── processed/                       # Silver layer - cleaned data
│   ├── analytics/                       # Gold layer - analytics
│   └── warehouse/                       # DuckDB database
│
├── 📂 notebooks/                        # Jupyter notebooks
│   └── 01_exploratory_analysis.ipynb    # ⭐ Data analysis notebook
│
├── 📂 docs/                             # Documentation
│   ├── QUICKSTART.md                    # ⭐ Getting started guide
│   ├── ARCHITECTURE.md                  # ⭐ System architecture
│   └── EXAMPLES.md                      # ⭐ Code examples
│
├── 📂 logs/                             # Application logs
│
└── 📂 tests/                            # Unit tests
```

---

## 🌟 Key Files Quick Reference

### Essential Files to Start With

| File | Purpose | When to Use |
|------|---------|-------------|
| `README.md` | Project overview & introduction | **Start here!** |
| `docs/QUICKSTART.md` | Step-by-step setup guide | Setting up for first time |
| `setup.sh` | Automated setup script | Quick installation |
| `.env.example` | Configuration template | Environment setup |

### Core Implementation Files

| File | Purpose | Technology |
|------|---------|-----------|
| `src/ingestion/base_client.py` | NASA API client with retry logic | Python, Requests |
| `src/ingestion/neo_ingestion.py` | Asteroid data collection | Python, Pandas |
| `src/transformation/neo_transformer.py` | Data cleaning & enrichment | Pandas, Pandera |
| `src/dashboard/app.py` | Interactive dashboard | Streamlit, Plotly |
| `src/orchestration/dags/nasa_pipeline_dag.py` | Automated pipeline | Apache Airflow |

### Documentation Files

| File | Content | Audience |
|------|---------|----------|
| `docs/QUICKSTART.md` | Installation & first steps | Beginners |
| `docs/ARCHITECTURE.md` | System design & data flow | Engineers |
| `docs/EXAMPLES.md` | Code samples & recipes | Developers |
| `notebooks/01_exploratory_analysis.ipynb` | Data analysis tutorial | Data Scientists |

---

## 🎯 Quick Start Commands

### Option 1: Automated Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup
```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add your NASA_API_KEY

# 3. Run components
python src/ingestion/neo_ingestion.py          # Collect data
python src/transformation/neo_transformer.py   # Process data
streamlit run src/dashboard/app.py            # View dashboard
```

### Option 3: Docker (Full Stack)
```bash
docker-compose up -d
# Access services:
# Dashboard: http://localhost:8501
# Airflow: http://localhost:8080
# Jupyter: http://localhost:8888
```

---

## 📊 Data Pipeline Visualization

```
┌─────────────┐
│  NASA APIs  │  ← Data Sources
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Ingestion  │  ← src/ingestion/neo_ingestion.py
│   (Bronze)  │     • API calls with retry logic
└──────┬──────┘     • Rate limiting (1000 req/hr)
       │            • Save raw JSON & Parquet
       ▼
┌─────────────┐
│Transform.   │  ← src/transformation/neo_transformer.py
│  (Silver)   │     • Data cleaning & validation
└──────┬──────┘     • Enrichment (risk scores, categories)
       │            • Quality checks
       ▼
┌─────────────┐
│  Warehouse  │  ← data/warehouse/nasa_space.duckdb
│   (Gold)    │     • Star schema
└──────┬──────┘     • Optimized for queries
       │
       ▼
┌─────────────┐
│  Dashboard  │  ← src/dashboard/app.py
│   (Viz)     │     • Real-time charts
└─────────────┘     • Interactive filters
                    • Download reports

       ▲
       │
┌──────┴──────┐
│   Airflow   │  ← src/orchestration/dags/
│ (Schedule)  │     • Runs every 6 hours
└─────────────┘     • Monitors & alerts
```

---

## 🔑 Key Features Implemented

### ✅ Data Engineering
- [x] Multi-source data ingestion (NASA APIs)
- [x] Medallion architecture (Bronze → Silver → Gold)
- [x] Data quality validation (Pandera, Great Expectations)
- [x] Error handling & retry logic
- [x] Rate limiting & caching
- [x] Comprehensive logging

### ✅ Data Processing
- [x] Automated data cleaning
- [x] Field enrichment (risk scores, categories)
- [x] Temporal analysis features
- [x] Duplicate detection & removal
- [x] Schema validation

### ✅ Data Storage
- [x] Data Lake (Parquet files)
- [x] Data Warehouse (DuckDB)
- [x] Star schema design
- [x] Fact & dimension tables
- [x] Optimized for analytics

### ✅ Orchestration
- [x] Apache Airflow DAGs
- [x] Scheduled pipelines (every 6 hours)
- [x] Task dependencies
- [x] Monitoring & alerting
- [x] Retry mechanisms

### ✅ Visualization
- [x] Interactive Streamlit dashboard
- [x] Real-time asteroid tracking
- [x] Risk assessment widgets
- [x] Temporal analysis charts
- [x] Data export functionality

### ✅ Development Tools
- [x] Jupyter notebooks for analysis
- [x] Docker containerization
- [x] Automated setup script
- [x] Comprehensive documentation
- [x] Code examples

---

## 📈 Dashboard Features Preview

When you run the dashboard (`streamlit run src/dashboard/app.py`), you'll see:

### Main Metrics (Top Row)
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 🌑 Total        │  │ ⚠️ Potentially  │  │ 🎯 Closest      │  │ ⚡ Avg Velocity │
│ Asteroids: 45   │  │ Hazardous: 8    │  │ Approach: 1.2LD │  │ 25.3 km/s      │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Visualizations
- 📅 **Timeline Chart**: Upcoming approaches over time
- 📊 **Distance Distribution**: Histogram of approach distances
- 📦 **Size Analysis**: Box plots of asteroid sizes
- ⚡ **Velocity Scatter**: Distance vs velocity correlation
- 🚨 **Alerts Panel**: High-risk asteroids

### Interactive Features
- 🔍 Date range selector
- 🎛️ Distance & size filters
- 📥 CSV export
- 🔄 Real-time data refresh

---

## 🛠️ Technology Stack

### Core Technologies
```
Python 3.9+      →  Main programming language
Pandas/Polars    →  Data manipulation
DuckDB           →  Embedded data warehouse
Apache Airflow   →  Workflow orchestration
Streamlit        →  Dashboard framework
Plotly           →  Interactive visualizations
Docker           →  Containerization
```

### Supporting Tools
```
Requests         →  API calls
Loguru           →  Logging
Pandera          →  Data validation
PyArrow          →  Parquet file handling
Great Expect.    →  Data quality
Tenacity         →  Retry logic
```

---

## 📚 Documentation Map

```
Start Here
    ↓
README.md ──────────→ Project Overview
    ↓
docs/QUICKSTART.md ──→ Installation Guide
    ↓
    ├─→ Option 1: Run setup.sh
    ├─→ Option 2: Manual setup
    └─→ Option 3: Docker
        ↓
    Run Pipeline
        ↓
docs/EXAMPLES.md ────→ Code Examples
    ↓
docs/ARCHITECTURE.md ─→ System Design
    ↓
notebooks/ ──────────→ Data Analysis
```

---

## 🎓 Learning Path

### Beginner (Just Getting Started)
1. Read `README.md` - understand what the project does
2. Follow `docs/QUICKSTART.md` - get it running
3. Explore the dashboard - see it in action
4. Read code in `src/ingestion/` - understand data collection

### Intermediate (Want to Customize)
1. Study `docs/ARCHITECTURE.md` - understand the design
2. Read `docs/EXAMPLES.md` - learn code patterns
3. Modify `src/transformation/` - add custom enrichments
4. Create custom DAGs in `src/orchestration/`

### Advanced (Production Deployment)
1. Review scaling considerations in `ARCHITECTURE.md`
2. Set up PostgreSQL instead of DuckDB
3. Configure Airflow with KubernetesExecutor
4. Implement monitoring with Prometheus + Grafana
5. Add CI/CD with GitHub Actions

---

## 🤝 How to Contribute

1. **Report Issues**: Found a bug? Open an issue!
2. **Suggest Features**: Ideas for improvement? Let us know!
3. **Submit PRs**: Fixed something? Send a pull request!
4. **Improve Docs**: Documentation can always be better!
5. **Share Examples**: Created something cool? Share it!

---

## 📞 Getting Help

### Quick Help Resources

| Question Type | Resource |
|--------------|----------|
| "How do I install this?" | `docs/QUICKSTART.md` |
| "How does this work?" | `docs/ARCHITECTURE.md` |
| "How do I use X?" | `docs/EXAMPLES.md` |
| "Something's broken!" | Check logs in `logs/` |
| "Can I see examples?" | `notebooks/` directory |

### Common Issues & Solutions

**Problem**: "ModuleNotFoundError"
→ Solution: Activate venv and run `pip install -r requirements.txt`

**Problem**: "API rate limit exceeded"
→ Solution: Use your own API key (not DEMO_KEY)

**Problem**: "No data in dashboard"
→ Solution: Run ingestion & transformation first

**Problem**: "Docker won't start"
→ Solution: Check Docker is running, then `docker-compose down -v` and retry

---

## 🎯 Next Steps

After exploring this project:

1. ✅ **Customize the dashboard** - Add your own visualizations
2. ✅ **Extend data sources** - Add APOD, Mars, DONKI APIs
3. ✅ **Build ML models** - Predict asteroid approaches
4. ✅ **Set up alerts** - Slack/Email notifications
5. ✅ **Deploy to production** - AWS/GCP/Azure

---

## 🌟 Project Highlights

This is a **production-ready data engineering project** featuring:

- ✨ **Modern architecture**: Medallion (Bronze/Silver/Gold)
- 🚀 **Best practices**: Logging, error handling, testing
- 📊 **Real data**: Live NASA asteroid tracking
- 🔄 **Automation**: Airflow orchestration
- 📈 **Visualization**: Interactive Streamlit dashboard
- 📚 **Documentation**: Comprehensive guides
- 🐳 **Containerization**: Docker ready
- 🎓 **Educational**: Great for learning data engineering

---

**Ready to monitor space? Start with `docs/QUICKSTART.md`! 🚀**
