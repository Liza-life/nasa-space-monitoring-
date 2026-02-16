"""
NASA Space Monitoring Pipeline DAG
Orchestrates the complete ETL pipeline for NASA data
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import sys
from pathlib import Path

# Add project src to path
sys.path.append('/opt/airflow/src')

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# DAG definition
dag = DAG(
    'nasa_space_monitoring_pipeline',
    default_args=default_args,
    description='Complete ETL pipeline for NASA space monitoring data',
    schedule_interval='0 */6 * * *',  # Run every 6 hours
    start_date=days_ago(1),
    catchup=False,
    tags=['nasa', 'etl', 'space', 'asteroids'],
)


# Task functions
def ingest_neo_data(**context):
    """Ingest NEO (asteroid) data from NASA API"""
    from ingestion.neo_ingestion import NEOIngestion
    from loguru import logger
    
    logger.info("Starting NEO data ingestion")
    
    ingestion = NEOIngestion()
    
    try:
        # Fetch data for next 7 days
        df = ingestion.run_full_ingestion(days_ahead=7)
        
        # Push metadata to XCom
        context['ti'].xcom_push(key='neo_record_count', value=len(df))
        context['ti'].xcom_push(key='neo_hazardous_count', value=int(df['is_potentially_hazardous'].sum()))
        
        logger.info(f"Successfully ingested {len(df)} NEO records")
        
    finally:
        ingestion.close()


def transform_neo_data(**context):
    """Transform raw NEO data to processed format"""
    from transformation.neo_transformer import NEOTransformer
    from loguru import logger
    
    logger.info("Starting NEO data transformation")
    
    transformer = NEOTransformer()
    
    # Find latest raw file
    raw_files = list(Path("/opt/airflow/data/raw/neo").glob("neo_approaches_*.parquet"))
    
    if not raw_files:
        raise FileNotFoundError("No raw NEO data files found")
    
    latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Processing file: {latest_file.name}")
    
    # Run transformation
    df_processed = transformer.transform_pipeline(latest_file.name)
    
    # Push metadata to XCom
    context['ti'].xcom_push(key='processed_record_count', value=len(df_processed))
    context['ti'].xcom_push(key='high_threat_count', value=int((df_processed['threat_level'] == 'High').sum()))
    
    logger.info(f"Successfully transformed {len(df_processed)} records")


def load_to_warehouse(**context):
    """Load processed data to DuckDB warehouse"""
    from loguru import logger
    import duckdb
    import pandas as pd
    
    logger.info("Loading data to warehouse")
    
    # Connect to DuckDB
    conn = duckdb.connect('/opt/airflow/data/warehouse/nasa_space.duckdb')
    
    try:
        # Find latest processed file
        processed_files = list(Path("/opt/airflow/data/processed/neo").glob("neo_processed_*.parquet"))
        
        if not processed_files:
            raise FileNotFoundError("No processed NEO data files found")
        
        latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Loading file: {latest_file.name}")
        
        # Read parquet file
        df = pd.read_parquet(latest_file)
        
        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_asteroid_approaches (
                asteroid_id VARCHAR,
                name VARCHAR,
                close_approach_date TIMESTAMP,
                miss_distance_km DOUBLE,
                miss_distance_lunar DOUBLE,
                relative_velocity_kms DOUBLE,
                diameter_avg_km DOUBLE,
                is_potentially_hazardous BOOLEAN,
                threat_level VARCHAR,
                size_category VARCHAR,
                risk_score DOUBLE,
                days_until_approach INTEGER,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                ingestion_timestamp TIMESTAMP,
                PRIMARY KEY (asteroid_id, close_approach_date)
            )
        """)
        
        # Insert data (upsert to avoid duplicates)
        conn.execute("""
            INSERT OR REPLACE INTO fact_asteroid_approaches
            SELECT * FROM df
        """)
        
        row_count = conn.execute("SELECT COUNT(*) FROM fact_asteroid_approaches").fetchone()[0]
        
        logger.info(f"Loaded data to warehouse. Total rows: {row_count}")
        
        # Push metadata
        context['ti'].xcom_push(key='warehouse_total_rows', value=row_count)
        
    finally:
        conn.close()


def generate_analytics(**context):
    """Generate analytics and aggregated views"""
    from loguru import logger
    import duckdb
    
    logger.info("Generating analytics")
    
    conn = duckdb.connect('/opt/airflow/data/warehouse/nasa_space.duckdb')
    
    try:
        # Create analytics view: Daily statistics
        conn.execute("""
            CREATE OR REPLACE VIEW analytics_daily_stats AS
            SELECT 
                DATE_TRUNC('day', close_approach_date) as date,
                COUNT(*) as total_approaches,
                SUM(CASE WHEN is_potentially_hazardous THEN 1 ELSE 0 END) as hazardous_count,
                AVG(miss_distance_lunar) as avg_distance_lunar,
                MIN(miss_distance_lunar) as min_distance_lunar,
                AVG(relative_velocity_kms) as avg_velocity_kms,
                AVG(risk_score) as avg_risk_score
            FROM fact_asteroid_approaches
            WHERE close_approach_date >= CURRENT_DATE
            GROUP BY DATE_TRUNC('day', close_approach_date)
            ORDER BY date
        """)
        
        # Create analytics view: Threat level summary
        conn.execute("""
            CREATE OR REPLACE VIEW analytics_threat_summary AS
            SELECT 
                threat_level,
                COUNT(*) as count,
                AVG(miss_distance_lunar) as avg_distance_lunar,
                AVG(diameter_avg_km) as avg_diameter_km,
                AVG(risk_score) as avg_risk_score
            FROM fact_asteroid_approaches
            WHERE close_approach_date >= CURRENT_DATE
            GROUP BY threat_level
        """)
        
        # Export analytics to CSV for dashboard
        conn.execute("""
            COPY analytics_daily_stats 
            TO '/opt/airflow/data/analytics/daily_stats.csv' 
            (HEADER, DELIMITER ',')
        """)
        
        logger.info("Analytics generated successfully")
        
    finally:
        conn.close()


def send_alerts(**context):
    """Send alerts for high-risk asteroids"""
    from loguru import logger
    import duckdb
    
    logger.info("Checking for alerts")
    
    conn = duckdb.connect('/opt/airflow/data/warehouse/nasa_space.duckdb')
    
    try:
        # Query high-threat asteroids approaching in next 7 days
        high_threats = conn.execute("""
            SELECT 
                name,
                close_approach_date,
                miss_distance_lunar,
                risk_score,
                threat_level
            FROM fact_asteroid_approaches
            WHERE threat_level = 'High'
                AND close_approach_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY close_approach_date
        """).fetchdf()
        
        if len(high_threats) > 0:
            logger.warning(f"🚨 {len(high_threats)} HIGH THREAT asteroids detected!")
            
            for _, asteroid in high_threats.iterrows():
                logger.warning(
                    f"  - {asteroid['name']}: "
                    f"{asteroid['close_approach_date'].strftime('%Y-%m-%d')}, "
                    f"Distance: {asteroid['miss_distance_lunar']:.2f} LD, "
                    f"Risk: {asteroid['risk_score']:.1f}"
                )
            
            # In production, send to Slack/Email here
            context['ti'].xcom_push(key='alert_count', value=len(high_threats))
        else:
            logger.info("✅ No high-threat asteroids detected")
            context['ti'].xcom_push(key='alert_count', value=0)
        
    finally:
        conn.close()


# Define tasks
task_ingest = PythonOperator(
    task_id='ingest_neo_data',
    python_callable=ingest_neo_data,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_neo_data',
    python_callable=transform_neo_data,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag,
)

task_analytics = PythonOperator(
    task_id='generate_analytics',
    python_callable=generate_analytics,
    dag=dag,
)

task_alerts = PythonOperator(
    task_id='send_alerts',
    python_callable=send_alerts,
    dag=dag,
)

task_cleanup = BashOperator(
    task_id='cleanup_old_data',
    bash_command="""
    # Remove raw files older than 90 days
    find /opt/airflow/data/raw/neo -name "*.json" -mtime +90 -delete
    find /opt/airflow/data/raw/neo -name "*.parquet" -mtime +90 -delete
    
    # Remove processed files older than 365 days
    find /opt/airflow/data/processed/neo -name "*.parquet" -mtime +365 -delete
    
    echo "Cleanup completed"
    """,
    dag=dag,
)

# Define dependencies
task_ingest >> task_transform >> task_load >> task_analytics >> task_alerts >> task_cleanup
