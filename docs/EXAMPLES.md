# 📚 Usage Examples - NASA Space Monitoring Platform

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [API Integration Examples](#api-integration-examples)
3. [Data Analysis Examples](#data-analysis-examples)
4. [Dashboard Customization](#dashboard-customization)
5. [Airflow DAG Examples](#airflow-dag-examples)
6. [Advanced Queries](#advanced-queries)

---

## Basic Usage

### Example 1: Fetch Asteroid Data for Next 7 Days

```python
from src.ingestion.neo_ingestion import NEOIngestion
from datetime import datetime, timedelta

# Initialize ingestion
ingestion = NEOIngestion()

# Fetch data
df = ingestion.run_full_ingestion(days_ahead=7)

# Display summary
print(f"Total asteroids: {df['asteroid_id'].nunique()}")
print(f"Total approaches: {len(df)}")
print(f"Potentially hazardous: {df['is_potentially_hazardous'].sum()}")

# Show closest approaches
closest = df.nsmallest(5, 'miss_distance_km')
print("\nClosest Approaches:")
print(closest[['name', 'close_approach_date', 'miss_distance_km']])

ingestion.close()
```

**Output:**
```
Total asteroids: 45
Total approaches: 152
Potentially hazardous: 8

Closest Approaches:
                      name close_approach_date  miss_distance_km
0        (2024 AB1)        2024-02-15         384000.5
1        (2024 BC2)        2024-02-16         412500.3
...
```

---

## API Integration Examples

### Example 2: Get Today's Astronomy Picture

```python
from src.ingestion.base_client import NASAAPIClient

with NASAAPIClient() as client:
    # Get APOD
    apod = client.get('/planetary/apod')
    
    print(f"Title: {apod['title']}")
    print(f"Date: {apod['date']}")
    print(f"Explanation: {apod['explanation'][:200]}...")
    print(f"Image URL: {apod['url']}")
```

### Example 3: Search for Specific Asteroid

```python
from src.ingestion.neo_ingestion import NEOIngestion

ingestion = NEOIngestion()

# Look up specific asteroid by ID
asteroid_id = "3542519"
asteroid_data = ingestion.fetch_neo_lookup(asteroid_id)

print(f"Name: {asteroid_data['name']}")
print(f"Absolute Magnitude: {asteroid_data['absolute_magnitude_h']}")
print(f"Is Hazardous: {asteroid_data['is_potentially_hazardous_asteroid']}")

ingestion.close()
```

### Example 4: Batch Fetch Multiple Date Ranges

```python
from src.ingestion.neo_ingestion import NEOIngestion
from datetime import datetime, timedelta
import pandas as pd

ingestion = NEOIngestion()

# Fetch data for multiple weeks
all_data = []

for week in range(4):  # 4 weeks
    start_date = datetime.now() + timedelta(weeks=week)
    end_date = start_date + timedelta(days=7)
    
    print(f"Fetching week {week+1}...")
    raw_data = ingestion.fetch_neo_feed(start_date, end_date)
    df = ingestion.parse_neo_feed(raw_data)
    all_data.append(df)

# Combine all weeks
combined_df = pd.concat(all_data, ignore_index=True)
print(f"\nTotal records: {len(combined_df)}")

ingestion.close()
```

---

## Data Analysis Examples

### Example 5: Risk Analysis

```python
import pandas as pd
from pathlib import Path

# Load processed data
data_dir = Path('data/processed/neo')
latest_file = max(data_dir.glob('neo_processed_*.parquet'))
df = pd.read_parquet(latest_file)

# Analyze by threat level
threat_analysis = df.groupby('threat_level').agg({
    'asteroid_id': 'count',
    'miss_distance_lunar': 'mean',
    'risk_score': 'mean',
    'diameter_avg_km': 'mean'
}).round(2)

print("Risk Analysis by Threat Level:")
print(threat_analysis)

# Find asteroids within Moon's orbit (< 1 LD)
within_moon_orbit = df[df['miss_distance_lunar'] < 1.0]
print(f"\nAsteroids within Moon's orbit: {len(within_moon_orbit)}")
```

### Example 6: Temporal Patterns

```python
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_parquet('data/processed/neo/neo_processed_20240213.parquet')

# Group by date
daily_stats = df.groupby(df['close_approach_date'].dt.date).agg({
    'asteroid_id': 'count',
    'is_potentially_hazardous': 'sum',
    'miss_distance_lunar': 'min'
}).reset_index()

# Rename columns
daily_stats.columns = ['date', 'total', 'hazardous', 'closest_distance']

# Create visualization
fig = px.line(
    daily_stats,
    x='date',
    y='total',
    title='Daily Asteroid Approaches'
)
fig.show()
```

### Example 7: Size Distribution Analysis

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet('data/processed/neo/neo_processed_20240213.parquet')

# Create size bins
df['size_bin'] = pd.cut(
    df['diameter_avg_km'],
    bins=[0, 0.1, 0.5, 1.0, 5.0, float('inf')],
    labels=['Very Small (<100m)', 'Small (100-500m)', 
            'Medium (500m-1km)', 'Large (1-5km)', 'Very Large (>5km)']
)

# Plot distribution
fig, ax = plt.subplots(figsize=(10, 6))
df['size_bin'].value_counts().plot(kind='bar', ax=ax)
ax.set_title('Asteroid Size Distribution')
ax.set_xlabel('Size Category')
ax.set_ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

---

## Dashboard Customization

### Example 8: Custom Dashboard Widget

Add this to `src/dashboard/app.py`:

```python
def create_custom_metric_card(title, value, delta=None, icon="📊"):
    """Create a custom styled metric card"""
    col = st.columns(1)[0]
    
    with col:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        '>
            <h3 style='margin:0; font-size: 1.2em;'>{icon} {title}</h3>
            <h1 style='margin: 10px 0; font-size: 2.5em;'>{value}</h1>
            {f"<p style='margin:0; opacity: 0.9;'>{delta}</p>" if delta else ""}
        </div>
        """, unsafe_allow_html=True)

# Usage
create_custom_metric_card(
    "High Risk Asteroids",
    len(df[df['threat_level'] == 'High']),
    delta="in next 7 days",
    icon="🚨"
)
```

### Example 9: Interactive Filter Panel

```python
def create_advanced_filters():
    """Create advanced filtering options"""
    with st.sidebar.expander("🔍 Advanced Filters", expanded=False):
        # Distance filter
        distance_range = st.slider(
            "Distance Range (Lunar Distances)",
            min_value=0.0,
            max_value=20.0,
            value=(0.0, 20.0),
            step=0.1
        )
        
        # Size filter
        size_categories = st.multiselect(
            "Size Categories",
            options=['Small (<25m)', 'Medium (25-140m)', 
                    'Large (140m-1km)', 'Very Large (>1km)'],
            default=['Small (<25m)', 'Medium (25-140m)']
        )
        
        # Velocity filter
        min_velocity = st.number_input(
            "Minimum Velocity (km/s)",
            min_value=0.0,
            max_value=100.0,
            value=0.0
        )
        
        return {
            'distance_range': distance_range,
            'size_categories': size_categories,
            'min_velocity': min_velocity
        }
```

---

## Airflow DAG Examples

### Example 10: Custom Alert DAG

Create `src/orchestration/dags/custom_alert_dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import duckdb

def check_extreme_close_approaches(**context):
    """Alert on asteroids closer than 0.5 LD"""
    conn = duckdb.connect('data/warehouse/nasa_space.duckdb')
    
    extreme_close = conn.execute("""
        SELECT 
            name,
            close_approach_date,
            miss_distance_lunar,
            diameter_avg_km
        FROM fact_asteroid_approaches
        WHERE miss_distance_lunar < 0.5
            AND close_approach_date >= CURRENT_DATE
        ORDER BY miss_distance_lunar
    """).fetchdf()
    
    if len(extreme_close) > 0:
        print(f"🚨 EXTREME ALERT: {len(extreme_close)} asteroids < 0.5 LD")
        for _, row in extreme_close.iterrows():
            print(f"  - {row['name']}: {row['miss_distance_lunar']:.3f} LD")
    
    conn.close()

dag = DAG(
    'extreme_close_approach_alerts',
    schedule_interval='0 */1 * * *',  # Every hour
    start_date=datetime(2024, 1, 1),
    catchup=False
)

alert_task = PythonOperator(
    task_id='check_extreme_approaches',
    python_callable=check_extreme_close_approaches,
    dag=dag
)
```

### Example 11: Data Quality Monitoring DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import duckdb

def monitor_data_quality(**context):
    """Monitor key data quality metrics"""
    conn = duckdb.connect('data/warehouse/nasa_space.duckdb')
    
    # Check for data staleness
    latest_date = conn.execute("""
        SELECT MAX(close_approach_date) as latest
        FROM fact_asteroid_approaches
    """).fetchone()[0]
    
    # Check for duplicates
    duplicates = conn.execute("""
        SELECT COUNT(*) as dup_count
        FROM (
            SELECT asteroid_id, close_approach_date, COUNT(*) as cnt
            FROM fact_asteroid_approaches
            GROUP BY asteroid_id, close_approach_date
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    
    # Check for nulls
    null_count = conn.execute("""
        SELECT 
            SUM(CASE WHEN diameter_avg_km IS NULL THEN 1 ELSE 0 END) as null_diameter,
            SUM(CASE WHEN risk_score IS NULL THEN 1 ELSE 0 END) as null_risk
        FROM fact_asteroid_approaches
    """).fetchone()
    
    print(f"Latest data date: {latest_date}")
    print(f"Duplicates: {duplicates}")
    print(f"Null diameters: {null_count[0]}, Null risk scores: {null_count[1]}")
    
    # Push to XCom
    context['ti'].xcom_push(key='quality_score', 
                           value=100 if duplicates == 0 else 50)
    
    conn.close()

dag = DAG(
    'data_quality_monitoring',
    schedule_interval='0 0 * * *',  # Daily
    start_date=datetime(2024, 1, 1)
)

quality_task = PythonOperator(
    task_id='monitor_quality',
    python_callable=monitor_data_quality,
    dag=dag
)
```

---

## Advanced Queries

### Example 12: Complex DuckDB Queries

```python
import duckdb

conn = duckdb.connect('data/warehouse/nasa_space.duckdb')

# Query 1: Top 10 fastest asteroids
fastest = conn.execute("""
    SELECT 
        name,
        relative_velocity_kms,
        miss_distance_lunar,
        close_approach_date
    FROM fact_asteroid_approaches
    WHERE close_approach_date >= CURRENT_DATE
    ORDER BY relative_velocity_kms DESC
    LIMIT 10
""").fetchdf()

print("Fastest Asteroids:")
print(fastest)

# Query 2: Monthly statistics
monthly_stats = conn.execute("""
    SELECT 
        year,
        month,
        COUNT(*) as total_approaches,
        AVG(miss_distance_lunar) as avg_distance,
        AVG(risk_score) as avg_risk,
        SUM(CASE WHEN is_potentially_hazardous THEN 1 ELSE 0 END) as hazardous_count
    FROM fact_asteroid_approaches
    GROUP BY year, month
    ORDER BY year, month
""").fetchdf()

print("\nMonthly Statistics:")
print(monthly_stats)

# Query 3: Risk distribution by size
risk_by_size = conn.execute("""
    SELECT 
        size_category,
        threat_level,
        COUNT(*) as count,
        AVG(risk_score) as avg_risk
    FROM fact_asteroid_approaches
    WHERE close_approach_date >= CURRENT_DATE
    GROUP BY size_category, threat_level
    ORDER BY size_category, threat_level
""").fetchdf()

print("\nRisk Distribution by Size:")
print(risk_by_size)

conn.close()
```

### Example 13: Pandas + DuckDB Integration

```python
import duckdb
import pandas as pd

# Load data with Pandas
df = pd.read_parquet('data/processed/neo/neo_processed_20240213.parquet')

# Use DuckDB for SQL queries on Pandas DataFrame
result = duckdb.query("""
    SELECT 
        size_category,
        COUNT(*) as count,
        AVG(risk_score) as avg_risk,
        MAX(diameter_avg_km) as max_diameter
    FROM df
    WHERE is_potentially_hazardous = true
    GROUP BY size_category
    ORDER BY avg_risk DESC
""").to_df()

print("Hazardous Asteroids by Size:")
print(result)
```

---

## Production Deployment Examples

### Example 14: Docker Compose Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    
  airflow-webserver:
    build: .
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__WEBSERVER__EXPOSE_CONFIG: 'false'
    restart: always
    
  dashboard:
    build: .
    environment:
      STREAMLIT_SERVER_ENABLE_STATIC_SERVING: 'true'
    restart: always

volumes:
  postgres_data:
```

### Example 15: Health Check Script

```python
#!/usr/bin/env python3
"""
Health check script for monitoring system status
"""

import duckdb
import requests
from datetime import datetime, timedelta

def check_database():
    """Check if database is accessible and has recent data"""
    try:
        conn = duckdb.connect('data/warehouse/nasa_space.duckdb')
        latest = conn.execute("""
            SELECT MAX(ingestion_timestamp) as latest
            FROM fact_asteroid_approaches
        """).fetchone()[0]
        
        if latest and (datetime.now() - latest) < timedelta(hours=12):
            return True, "Database OK"
        else:
            return False, "Data is stale"
    except Exception as e:
        return False, f"Database error: {e}"

def check_api():
    """Check if NASA API is accessible"""
    try:
        response = requests.get(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": "DEMO_KEY"},
            timeout=10
        )
        return response.status_code == 200, f"API status: {response.status_code}"
    except Exception as e:
        return False, f"API error: {e}"

def main():
    checks = [
        ("Database", check_database),
        ("NASA API", check_api)
    ]
    
    print("🏥 Health Check Report")
    print("=" * 50)
    
    all_ok = True
    for name, check_func in checks:
        status, message = check_func()
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}: {message}")
        all_ok = all_ok and status
    
    print("=" * 50)
    print(f"Overall Status: {'✅ HEALTHY' if all_ok else '❌ UNHEALTHY'}")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())
```

---

**For more examples, check the notebooks/ directory and the main documentation.**
