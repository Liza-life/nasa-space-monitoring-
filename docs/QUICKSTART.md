# 🚀 Quick Start Guide - NASA Space Monitoring Platform

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Platform](#running-the-platform)
5. [Accessing Services](#accessing-services)
6. [First Run Tutorial](#first-run-tutorial)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop))
- **Git** ([Download](https://git-scm.com/downloads))

### Optional but Recommended
- **Visual Studio Code** with Python extension
- **DBeaver** or **pgAdmin** for database management
- **Postman** for API testing

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 10GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/nasa-space-monitoring.git
cd nasa-space-monitoring
```

### Step 2: Get NASA API Key

1. Visit: https://api.nasa.gov/
2. Fill out the form with your name and email
3. Check your email for the API key
4. **IMPORTANT**: Save this key securely!

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your favorite text editor
nano .env  # or vim, code, notepad++, etc.
```

**Replace the following in `.env`:**
```bash
NASA_API_KEY=YOUR_ACTUAL_NASA_API_KEY_HERE
```

### Step 4: Install Python Dependencies (Local Development)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### Database Setup

The platform uses **DuckDB** by default (no setup needed) and **PostgreSQL** for Airflow.

PostgreSQL is automatically configured through Docker Compose.

### API Rate Limiting

By default, the NASA API allows:
- **1,000 requests per hour** with a registered API key
- **30 requests per hour** with DEMO_KEY

To avoid rate limiting issues:
```bash
# In .env file:
API_RATE_LIMIT_PER_HOUR=1000
```

---

## Running the Platform

### Option 1: Using Docker (Recommended)

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Services will start:**
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ Airflow Webserver (port 8080)
- ✅ Airflow Scheduler
- ✅ Airflow Worker
- ✅ Streamlit Dashboard (port 8501)
- ✅ Jupyter Notebook (port 8888)

### Option 2: Running Components Individually

#### Run Data Ingestion
```bash
python src/ingestion/neo_ingestion.py
```

#### Run Data Transformation
```bash
python src/transformation/neo_transformer.py
```

#### Run Dashboard
```bash
streamlit run src/dashboard/app.py
```

---

## Accessing Services

### 🌐 Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:8501 | None |
| **Airflow UI** | http://localhost:8080 | admin / admin |
| **Jupyter Notebook** | http://localhost:8888 | Check logs for token |

### 🔍 Getting Jupyter Token

```bash
docker logs nasa_jupyter 2>&1 | grep token
```

Look for a line like:
```
http://127.0.0.1:8888/?token=abc123def456...
```

---

## First Run Tutorial

### 1. Manual Data Collection (No Airflow)

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Create data directories
mkdir -p data/{raw,processed,analytics}/neo
mkdir -p logs

# Run data ingestion
python src/ingestion/neo_ingestion.py

# You should see output like:
# INFO: Starting full NEO ingestion for next 7 days
# INFO: Successfully ingested 150 NEO records
# INFO: Total asteroids: 45
# INFO: Potentially hazardous: 8
```

### 2. Transform the Data

```bash
# Run transformation
python src/transformation/neo_transformer.py

# Expected output:
# INFO: Starting NEO transformation pipeline
# INFO: Parsed 150 asteroid approach records
# INFO: Added 12 new fields
# INFO: Transformation pipeline completed successfully
```

### 3. View in Dashboard

```bash
# Start the dashboard
streamlit run src/dashboard/app.py

# Your browser should open automatically to:
# http://localhost:8501
```

**What you'll see:**
- 📊 Real-time asteroid approach data
- 🎯 Closest approaches in the next 7 days
- ⚠️ Potentially hazardous asteroids
- 📈 Interactive charts and visualizations

### 4. Using Airflow (Full Automation)

```bash
# Make sure Docker is running
docker-compose up -d

# Wait ~60 seconds for services to start

# Open Airflow UI
# http://localhost:8080
# Login: admin / admin

# Enable the DAG:
# 1. Click on the "nasa_space_monitoring_pipeline" DAG
# 2. Toggle the switch to "On"
# 3. Click "Trigger DAG" to run immediately
```

**Monitor the Pipeline:**
1. Click on the DAG name
2. Go to "Graph" view
3. Watch tasks turn green as they complete
4. Check logs by clicking on any task

---

## Data Flow Diagram

```
┌─────────────────┐
│   NASA APIs     │
│  (Raw Data)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ingestion     │  ← Python scripts
│   (Bronze)      │    fetch data via API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transformation  │  ← Pandas/Polars
│   (Silver)      │    clean & enrich
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Warehouse  │  ← DuckDB
│    (Gold)       │    analytics ready
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │  ← Streamlit
│ (Visualization) │    interactive UI
└─────────────────┘
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'X'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate

# Install dependencies again
pip install -r requirements.txt
```

### Problem: Docker services won't start

**Solution:**
```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild and start
docker-compose up --build -d
```

### Problem: "Rate limit exceeded" error

**Solution:**
1. Check you're using your real API key (not DEMO_KEY)
2. Reduce request frequency in the code
3. Wait an hour for rate limit to reset

### Problem: Dashboard shows no data

**Solution:**
1. Make sure you've run ingestion at least once
2. Check that Parquet files exist in `data/raw/neo/`
3. Run transformation to create processed data
4. Restart the dashboard

### Problem: Can't access Airflow UI

**Solution:**
```bash
# Check if services are running
docker-compose ps

# Check Airflow logs
docker-compose logs airflow-webserver

# If needed, restart Airflow
docker-compose restart airflow-webserver
```

### Problem: PostgreSQL connection refused

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

---

## Stopping the Platform

### Stop all services:
```bash
docker-compose down
```

### Stop and remove all data (fresh start):
```bash
docker-compose down -v
```

### Stop individual services:
```bash
docker-compose stop dashboard
docker-compose stop airflow-webserver
```

---

## Next Steps

Once everything is running:

1. ✅ **Explore the Dashboard** - Visualize asteroid data
2. ✅ **Check Airflow DAGs** - View the automated pipeline
3. ✅ **Run Jupyter Notebooks** - Perform custom analysis
4. ✅ **Read the Documentation** - Learn advanced features
5. ✅ **Customize Alerts** - Set up Slack/Email notifications

---

## Getting Help

- 📖 **Documentation**: `docs/` folder
- 🐛 **Issues**: GitHub Issues page
- 💬 **Discussions**: GitHub Discussions
- 📧 **Email**: your.email@example.com

---

**Happy Space Monitoring! 🚀🌌**
