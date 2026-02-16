# 🏗️ Architecture Documentation - NASA Space Monitoring Platform

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Data Architecture](#data-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Scalability Considerations](#scalability-considerations)

---

## System Architecture Overview

The NASA Space Monitoring Platform follows a **modern data lakehouse architecture** with distinct layers for ingestion, processing, storage, and visualization.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit Dashboard  │  Jupyter Notebooks  │  API Endpoints    │
└────────────┬────────────────────────┬────────────────┬──────────┘
             │                        │                │
             ▼                        ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         ANALYTICS LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  Aggregations  │  Metrics  │  Reports  │  Alerts  │  ML Models │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA WAREHOUSE (GOLD)                       │
├─────────────────────────────────────────────────────────────────┤
│  DuckDB/PostgreSQL  │  Star Schema  │  Fact & Dimension Tables │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION LAYER (SILVER)                 │
├─────────────────────────────────────────────────────────────────┤
│  Data Cleaning  │  Validation  │  Enrichment  │  Quality Checks│
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAKE (BRONZE)                          │
├─────────────────────────────────────────────────────────────────┤
│  Raw JSON  │  Raw Parquet  │  Unprocessed Data  │  Backups    │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        INGESTION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  API Clients  │  Rate Limiting  │  Error Handling  │  Logging  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────┤
│  NeoWs API  │  APOD  │  Mars Rover  │  DONKI  │  Earth Imagery│
└─────────────────────────────────────────────────────────────────┘
```

### Orchestration Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                      APACHE AIRFLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Ingest  │→ │Transform │→ │   Load   │→ │Analytics │       │
│  │   DAG    │  │   DAG    │  │   DAG    │  │   DAG    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       ↓              ↓              ↓              ↓           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │           Task Scheduler & Executor                  │       │
│  └─────────────────────────────────────────────────────┘       │
│       ↓              ↓              ↓              ↓           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Worker  │  │  Worker  │  │  Worker  │  │  Worker  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Architecture

### Medallion Architecture (Bronze → Silver → Gold)

#### 🥉 Bronze Layer (Raw Data)
- **Purpose**: Store raw, unprocessed data exactly as received from APIs
- **Format**: JSON, Parquet
- **Location**: `data/raw/`
- **Retention**: 90 days
- **Characteristics**:
  - Immutable
  - Schema-on-read
  - Complete history
  - No transformations

#### 🥈 Silver Layer (Processed Data)
- **Purpose**: Cleaned, validated, and enriched data
- **Format**: Parquet
- **Location**: `data/processed/`
- **Retention**: 365 days
- **Transformations**:
  - Data cleaning
  - Type conversions
  - Deduplication
  - Validation
  - Enrichment (calculated fields)

#### 🥇 Gold Layer (Analytics-Ready Data)
- **Purpose**: Aggregated, business-ready data
- **Format**: DuckDB tables, Parquet
- **Location**: `data/analytics/`, `data/warehouse/`
- **Retention**: Indefinite
- **Characteristics**:
  - Star schema
  - Pre-aggregated
  - Optimized for queries
  - Business logic applied

### Star Schema Design

```
                    ┌──────────────────┐
                    │   dim_asteroids  │
                    ├──────────────────┤
                    │ asteroid_id (PK) │
                    │ name             │
                    │ diameter_min_km  │
                    │ diameter_max_km  │
                    │ size_category    │
                    └────────┬─────────┘
                             │
                             │
┌─────────────────┐          │          ┌──────────────────┐
│    dim_time     │          │          │  dim_hazard_     │
├─────────────────┤          │          │  classification  │
│ date_id (PK)    │          │          ├──────────────────┤
│ date            │          │          │ hazard_id (PK)   │
│ year            │          │          │ threat_level     │
│ month           │          │          │ is_hazardous     │
│ day             │          ▼          └────────┬─────────┘
│ day_of_week     │   ┌─────────────────────┐   │
│ week_of_year    │◄──┤ fact_asteroid_      │◄──┘
└─────────────────┘   │    approaches       │
                      ├─────────────────────┤
                      │ approach_id (PK)    │
                      │ asteroid_id (FK)    │
                      │ date_id (FK)        │
                      │ hazard_id (FK)      │
                      │ miss_distance_km    │
                      │ miss_distance_lunar │
                      │ velocity_kms        │
                      │ risk_score          │
                      │ ingestion_timestamp │
                      └─────────────────────┘
```

---

## Component Details

### 1. Ingestion Layer

**Components:**
- `base_client.py`: Base API client with retry logic, rate limiting
- `neo_ingestion.py`: NEO data collection
- `apod_ingestion.py`: Astronomy Picture of the Day
- `mars_ingestion.py`: Mars Rover photos
- `donki_ingestion.py`: Space weather events

**Features:**
- ✅ Automatic retry on failure (3 attempts)
- ✅ Exponential backoff
- ✅ Rate limiting (1000 req/hour)
- ✅ Request caching
- ✅ Comprehensive logging
- ✅ Error handling

**Data Sources:**
```python
NASA_APIS = {
    'NeoWs': 'https://api.nasa.gov/neo/rest/v1/',
    'APOD': 'https://api.nasa.gov/planetary/apod',
    'Mars Rover': 'https://api.nasa.gov/mars-photos/api/v1/',
    'DONKI': 'https://api.nasa.gov/DONKI/',
    'Earth': 'https://api.nasa.gov/planetary/earth/'
}
```

### 2. Transformation Layer

**Components:**
- `neo_transformer.py`: Clean and enrich NEO data
- Data validation with Pandera schemas
- Quality checks with Great Expectations
- Calculated metrics and enrichments

**Transformations:**
```python
Enrichments = [
    'diameter_avg_km',          # Average diameter
    'estimated_volume_km3',     # Volume estimate
    'days_until_approach',      # Time to approach
    'size_category',            # Small/Medium/Large/VeryLarge
    'risk_score',               # 0-100 risk metric
    'threat_level'              # High/Medium/Low/Minimal
]
```

### 3. Storage Layer

**DuckDB (Default):**
- Embedded OLAP database
- Fast analytical queries
- No server required
- Perfect for local development

**PostgreSQL (Production):**
- Used by Airflow for metadata
- Optional for data warehouse
- ACID compliance
- Better for concurrent users

### 4. Orchestration Layer

**Apache Airflow:**
- **Scheduler**: Triggers DAGs on schedule
- **Workers**: Execute tasks in parallel
- **Webserver**: UI for monitoring
- **Executor**: LocalExecutor or CeleryExecutor

**DAG Configuration:**
```python
DAG_SCHEDULE = {
    'neo_feed': '0 */6 * * *',      # Every 6 hours
    'apod': '0 8 * * *',             # Daily at 8 AM
    'mars_rover': '0 10 * * *',      # Daily at 10 AM
    'donki_events': '0 */12 * * *',  # Every 12 hours
}
```

### 5. Visualization Layer

**Streamlit Dashboard:**
- Real-time data visualization
- Interactive filters
- Downloadable reports
- Responsive design

**Jupyter Notebooks:**
- Exploratory data analysis
- Ad-hoc queries
- Prototyping
- Documentation

---

## Data Flow

### End-to-End Pipeline

```
1. SCHEDULED TRIGGER (Airflow)
   ↓
2. API REQUEST (Python client)
   ↓
3. RAW DATA STORAGE (Bronze - JSON/Parquet)
   ↓
4. DATA CLEANING (Pandas/Polars)
   ↓
5. DATA VALIDATION (Pandera/Great Expectations)
   ↓
6. DATA ENRICHMENT (Calculated fields)
   ↓
7. PROCESSED DATA STORAGE (Silver - Parquet)
   ↓
8. SCHEMA MAPPING (To star schema)
   ↓
9. DATA WAREHOUSE LOAD (Gold - DuckDB)
   ↓
10. AGGREGATIONS (Analytics layer)
    ↓
11. VISUALIZATION (Streamlit)
```

### Sample Data Flow Timing

| Stage | Duration | Notes |
|-------|----------|-------|
| API Request | ~2-5 sec | Depends on NASA API response time |
| Raw Storage | ~1 sec | Write JSON/Parquet to disk |
| Transformation | ~5-10 sec | For 100-200 records |
| Validation | ~2-3 sec | Schema checks |
| Warehouse Load | ~3-5 sec | DuckDB insert |
| Dashboard Refresh | ~1-2 sec | Query + render |
| **Total Pipeline** | **~15-30 sec** | For typical batch |

---

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Data Collection** | Python 3.9+ | API clients, scripting |
| **API Client** | Requests, HTTPX | HTTP requests |
| **Data Processing** | Pandas, Polars | Data manipulation |
| **Storage** | DuckDB, PostgreSQL | Data warehouse |
| **File Format** | Parquet, JSON | Efficient storage |
| **Orchestration** | Apache Airflow | Workflow management |
| **Visualization** | Streamlit, Plotly | Dashboards |
| **Validation** | Pandera, Great Expectations | Data quality |
| **Logging** | Loguru | Structured logging |
| **Containerization** | Docker, Docker Compose | Deployment |

### Why These Technologies?

**Python**: 
- Rich data engineering ecosystem
- Easy NASA API integration
- Extensive libraries

**DuckDB**:
- In-process OLAP database
- Fast analytical queries
- No server overhead
- Perfect for local development

**Parquet**:
- Columnar storage format
- Excellent compression
- Fast read performance
- Schema evolution support

**Airflow**:
- Industry standard for orchestration
- Rich UI for monitoring
- Extensive operator library
- Python-native DAG definition

**Streamlit**:
- Rapid dashboard development
- Python-native
- Auto-refresh capabilities
- Easy deployment

---

## Scalability Considerations

### Current Architecture (Development)

**Designed for:**
- Single machine deployment
- 1-10 GB data volume
- Hourly/daily updates
- 1-10 concurrent users

**Characteristics:**
- ✅ Simple deployment (Docker Compose)
- ✅ Low resource requirements
- ✅ Easy to understand and maintain
- ❌ Limited horizontal scalability
- ❌ Single point of failure

### Production Architecture (Future)

**For scaling to:**
- Distributed deployment
- 100+ GB data volume
- Real-time updates
- 100+ concurrent users

**Recommended Changes:**

1. **Data Storage:**
   ```
   DuckDB → PostgreSQL/Snowflake/BigQuery
   Local Files → S3/GCS/Azure Blob
   ```

2. **Processing:**
   ```
   Pandas → Apache Spark/Dask
   Single machine → Distributed cluster
   ```

3. **Orchestration:**
   ```
   LocalExecutor → KubernetesExecutor
   Docker Compose → Kubernetes/ECS
   ```

4. **Caching:**
   ```
   Add Redis for query caching
   Add CDN for static assets
   ```

5. **Monitoring:**
   ```
   Add Prometheus + Grafana
   Add ELK stack for logs
   Add data lineage tracking
   ```

### Performance Optimization

**Query Optimization:**
```sql
-- Create indexes on frequently queried columns
CREATE INDEX idx_approach_date ON fact_asteroid_approaches(close_approach_date);
CREATE INDEX idx_hazardous ON fact_asteroid_approaches(is_potentially_hazardous);
CREATE INDEX idx_asteroid_id ON fact_asteroid_approaches(asteroid_id);

-- Partition large tables by date
CREATE TABLE fact_asteroid_approaches_partitioned (
    ...
) PARTITION BY RANGE (close_approach_date);
```

**Data Compression:**
```python
# Use appropriate Parquet compression
df.to_parquet(
    'data.parquet',
    compression='snappy',  # Fast compression
    # or 'gzip' for better compression ratio
)
```

---

## Security Considerations

### API Key Management
- ✅ Environment variables (.env)
- ✅ Never commit to Git
- ✅ Rotate keys periodically

### Database Security
- ✅ Strong passwords
- ✅ Network isolation
- ✅ Encryption at rest (production)
- ✅ SSL/TLS connections

### Access Control
- ✅ Airflow RBAC
- ✅ Database user permissions
- ✅ Dashboard authentication (production)

---

## Disaster Recovery

### Backup Strategy

**Bronze Layer (Raw Data):**
- Retention: 90 days
- Backup: Not needed (can re-fetch from API)

**Silver Layer (Processed Data):**
- Retention: 365 days
- Backup: Daily to S3/GCS

**Gold Layer (Warehouse):**
- Retention: Indefinite
- Backup: Daily snapshots
- Point-in-time recovery

### Recovery Procedures

**Scenario 1: Lost processed data**
```bash
# Re-transform from raw data
python src/transformation/neo_transformer.py
```

**Scenario 2: Lost raw data**
```bash
# Re-fetch from NASA API
python src/ingestion/neo_ingestion.py --backfill --days=90
```

**Scenario 3: Database corruption**
```bash
# Restore from backup
pg_restore -d nasa_space backup.dump
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

1. **Data Quality:**
   - Record count per batch
   - Null value percentage
   - Schema validation failures
   - Duplicate records

2. **Performance:**
   - Pipeline execution time
   - API response time
   - Query latency
   - Resource utilization

3. **Reliability:**
   - DAG success rate
   - Task failure count
   - API rate limit hits
   - Data freshness

### Alert Thresholds

```python
ALERT_THRESHOLDS = {
    'pipeline_duration': 3600,  # 1 hour max
    'api_errors': 5,  # consecutive
    'null_percentage': 10,  # percent
    'data_staleness': 86400,  # 24 hours
}
```

---

**For questions or contributions, see the main README.md**
