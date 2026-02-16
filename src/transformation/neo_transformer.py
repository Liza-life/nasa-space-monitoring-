"""
Data Transformation Module - Bronze to Silver Layer
Clean, validate, and enrich raw asteroid data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger
import pandera as pa
from pandera import Column, DataFrameSchema, Check


class NEOTransformer:
    """Transform raw NEO data into clean, validated format"""
    
    # Define schema for validation
    SCHEMA = DataFrameSchema({
        "asteroid_id": Column(str, nullable=False),
        "name": Column(str, nullable=False),
        "is_potentially_hazardous": Column(bool, nullable=False),
        "diameter_min_km": Column(float, Check.greater_than(0)),
        "diameter_max_km": Column(float, Check.greater_than(0)),
        "close_approach_date": Column(pd.DatetimeTZDtype(tz=None), nullable=False),
        "relative_velocity_kms": Column(float, Check.greater_than(0)),
        "miss_distance_km": Column(float, Check.greater_than(0)),
        "miss_distance_lunar": Column(float, Check.greater_than(0)),
    })
    
    def __init__(self, input_dir: str = "data/raw/neo", output_dir: str = "data/processed/neo"):
        """
        Initialize transformer
        
        Args:
            input_dir: Directory with raw data
            output_dir: Directory for processed data
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"NEO Transformer initialized. Input: {self.input_dir}, Output: {self.output_dir}")
    
    def load_raw_data(self, filename: str) -> pd.DataFrame:
        """Load raw parquet data"""
        filepath = self.input_dir / filename
        
        logger.info(f"Loading raw data from {filepath}")
        df = pd.read_parquet(filepath)
        logger.info(f"Loaded {len(df)} records")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize data
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning")
        
        df_clean = df.copy()
        
        # Remove duplicates
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(
            subset=['asteroid_id', 'close_approach_date'],
            keep='first'
        )
        logger.info(f"Removed {initial_count - len(df_clean)} duplicate records")
        
        # Handle missing values
        df_clean['diameter_min_km'] = df_clean['diameter_min_km'].fillna(
            df_clean['diameter_min_km'].median()
        )
        df_clean['diameter_max_km'] = df_clean['diameter_max_km'].fillna(
            df_clean['diameter_max_km'].median()
        )
        
        # Convert dates
        df_clean['close_approach_date'] = pd.to_datetime(df_clean['close_approach_date'])
        
        # Remove invalid records (negative or zero values)
        df_clean = df_clean[
            (df_clean['diameter_min_km'] > 0) &
            (df_clean['diameter_max_km'] > 0) &
            (df_clean['relative_velocity_kms'] > 0) &
            (df_clean['miss_distance_km'] > 0)
        ]
        
        logger.info(f"Cleaning complete. {len(df_clean)} valid records remaining")
        
        return df_clean
    
    def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated fields and enrichments
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Enriched DataFrame
        """
        logger.info("Enriching data with calculated fields")
        
        df_enriched = df.copy()
        
        # Calculate average diameter
        df_enriched['diameter_avg_km'] = (
            df_enriched['diameter_min_km'] + df_enriched['diameter_max_km']
        ) / 2
        
        # Estimate volume (assuming spherical)
        df_enriched['estimated_volume_km3'] = (
            4/3 * np.pi * (df_enriched['diameter_avg_km'] / 2) ** 3
        )
        
        # Calculate time to closest approach
        df_enriched['days_until_approach'] = (
            df_enriched['close_approach_date'] - pd.Timestamp.now()
        ).dt.days
        
        # Classify by size (NASA classification)
        def classify_size(diameter_km):
            if diameter_km < 0.025:
                return 'Small (<25m)'
            elif diameter_km < 0.14:
                return 'Medium (25-140m)'
            elif diameter_km < 1.0:
                return 'Large (140m-1km)'
            else:
                return 'Very Large (>1km)'
        
        df_enriched['size_category'] = df_enriched['diameter_avg_km'].apply(classify_size)
        
        # Calculate risk score (0-100)
        # Based on: proximity, size, velocity, and hazardous classification
        df_enriched['risk_score'] = (
            (1 / df_enriched['miss_distance_lunar']).clip(0, 10) * 20 +  # Proximity
            (df_enriched['diameter_avg_km'] * 100).clip(0, 30) +  # Size
            (df_enriched['relative_velocity_kms'] / 50).clip(0, 20) +  # Velocity
            (df_enriched['is_potentially_hazardous'].astype(int) * 30)  # Hazardous flag
        ).clip(0, 100)
        
        # Classify threat level
        def classify_threat(row):
            if row['is_potentially_hazardous'] and row['miss_distance_lunar'] < 1.0:
                return 'High'
            elif row['is_potentially_hazardous'] and row['miss_distance_lunar'] < 5.0:
                return 'Medium'
            elif row['miss_distance_lunar'] < 2.0:
                return 'Low'
            else:
                return 'Minimal'
        
        df_enriched['threat_level'] = df_enriched.apply(classify_threat, axis=1)
        
        # Extract date components for dimensional modeling
        df_enriched['year'] = df_enriched['close_approach_date'].dt.year
        df_enriched['month'] = df_enriched['close_approach_date'].dt.month
        df_enriched['day'] = df_enriched['close_approach_date'].dt.day
        df_enriched['day_of_week'] = df_enriched['close_approach_date'].dt.dayofweek
        df_enriched['week_of_year'] = df_enriched['close_approach_date'].dt.isocalendar().week
        
        logger.info(f"Added {len(df_enriched.columns) - len(df.columns)} new fields")
        
        return df_enriched
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data quality
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validated DataFrame
        """
        logger.info("Validating data quality")
        
        try:
            # Validate against schema (subset of columns)
            validation_cols = [col for col in self.SCHEMA.columns.keys() if col in df.columns]
            validated_df = self.SCHEMA.validate(df[validation_cols], lazy=True)
            logger.info("✅ Data validation passed")
            
            return df
            
        except pa.errors.SchemaErrors as e:
            logger.error(f"❌ Data validation failed: {e}")
            
            # Log specific failures
            for error in e.failure_cases.itertuples():
                logger.error(f"  - {error.column}: {error.check}")
            
            raise
    
    def create_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate data quality report
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Quality metrics dictionary
        """
        logger.info("Generating quality report")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'unique_asteroids': df['asteroid_id'].nunique(),
            'date_range': {
                'min': df['close_approach_date'].min().isoformat(),
                'max': df['close_approach_date'].max().isoformat()
            },
            'completeness': {
                col: f"{(1 - df[col].isna().sum() / len(df)) * 100:.2f}%"
                for col in df.columns
            },
            'hazardous_count': int(df['is_potentially_hazardous'].sum()),
            'hazardous_percentage': f"{(df['is_potentially_hazardous'].sum() / len(df)) * 100:.2f}%",
            'threat_distribution': df['threat_level'].value_counts().to_dict() if 'threat_level' in df.columns else {},
            'size_distribution': df['size_category'].value_counts().to_dict() if 'size_category' in df.columns else {},
            'statistics': {
                'avg_distance_lunar': float(df['miss_distance_lunar'].mean()),
                'min_distance_lunar': float(df['miss_distance_lunar'].min()),
                'avg_velocity_kms': float(df['relative_velocity_kms'].mean()),
                'avg_diameter_km': float(df['diameter_avg_km'].mean()) if 'diameter_avg_km' in df.columns else None
            }
        }
        
        return report
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to Parquet"""
        filepath = self.output_dir / f"{filename}.parquet"
        df.to_parquet(filepath, index=False, engine='pyarrow')
        logger.info(f"Saved {len(df)} processed records to {filepath}")
    
    def transform_pipeline(self, input_filename: str, output_filename: Optional[str] = None) -> pd.DataFrame:
        """
        Run complete transformation pipeline
        
        Args:
            input_filename: Input Parquet file
            output_filename: Output filename (auto-generated if None)
            
        Returns:
            Transformed DataFrame
        """
        logger.info("=" * 60)
        logger.info("Starting NEO transformation pipeline")
        logger.info("=" * 60)
        
        # Load data
        df_raw = self.load_raw_data(input_filename)
        
        # Clean data
        df_clean = self.clean_data(df_raw)
        
        # Enrich data
        df_enriched = self.enrich_data(df_clean)
        
        # Validate data
        df_validated = self.validate_data(df_enriched)
        
        # Generate quality report
        quality_report = self.create_quality_report(df_validated)
        
        # Log report summary
        logger.info("Quality Report Summary:")
        logger.info(f"  Total records: {quality_report['total_records']}")
        logger.info(f"  Unique asteroids: {quality_report['unique_asteroids']}")
        logger.info(f"  Hazardous: {quality_report['hazardous_count']} ({quality_report['hazardous_percentage']})")
        
        # Save processed data
        if output_filename is None:
            output_filename = f"neo_processed_{datetime.now().strftime('%Y%m%d')}"
        
        self.save_processed_data(df_validated, output_filename)
        
        # Save quality report
        import json
        report_path = self.output_dir / f"{output_filename}_quality_report.json"
        with open(report_path, 'w') as f:
            json.dump(quality_report, f, indent=2, default=str)
        logger.info(f"Saved quality report to {report_path}")
        
        logger.info("=" * 60)
        logger.info("Transformation pipeline completed successfully")
        logger.info("=" * 60)
        
        return df_validated


# Example usage
if __name__ == "__main__":
    # Configure logger
    logger.add(
        "logs/neo_transformation.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    # Run transformation
    transformer = NEOTransformer()
    
    # Find latest raw file
    raw_files = list(Path("data/raw/neo").glob("neo_approaches_*.parquet"))
    
    if raw_files:
        latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Processing latest file: {latest_file.name}")
        
        df_processed = transformer.transform_pipeline(latest_file.name)
        
        print("\n=== Transformation Summary ===")
        print(f"Processed records: {len(df_processed)}")
        print(f"\nThreat level distribution:")
        print(df_processed['threat_level'].value_counts())
        print(f"\nSize category distribution:")
        print(df_processed['size_category'].value_counts())
    else:
        logger.warning("No raw data files found. Run ingestion first.")
