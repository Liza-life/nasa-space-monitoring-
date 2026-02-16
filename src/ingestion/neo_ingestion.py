"""
NEO (Near Earth Objects) Data Ingestion
Collects asteroid approach data from NASA's NeoWs API
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from loguru import logger
from base_client import NASAAPIClient


class NEOIngestion:
    """Ingest Near Earth Object data from NASA API"""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = "data/raw/neo"):
        """
        Initialize NEO ingestion
        
        Args:
            api_key: NASA API key
            output_dir: Directory to save raw data
        """
        self.client = NASAAPIClient(api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"NEO Ingestion initialized. Output: {self.output_dir}")
    
    def fetch_neo_feed(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch NEO feed for date range
        
        Args:
            start_date: Start date (defaults to today)
            end_date: End date (defaults to today + 7 days)
            
        Returns:
            API response with asteroid data
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        logger.info(f"Fetching NEO feed from {params['start_date']} to {params['end_date']}")
        
        try:
            response = self.client.get("/neo/rest/v1/feed", params=params)
            
            # Save raw response
            self._save_raw_json(response, "neo_feed", params["start_date"])
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching NEO feed: {e}")
            raise
    
    def fetch_neo_lookup(self, asteroid_id: str) -> Dict[str, Any]:
        """
        Lookup specific asteroid by ID
        
        Args:
            asteroid_id: NASA asteroid ID
            
        Returns:
            Detailed asteroid data
        """
        logger.info(f"Looking up asteroid {asteroid_id}")
        
        try:
            response = self.client.get(f"/neo/rest/v1/neo/{asteroid_id}")
            
            # Save raw response
            self._save_raw_json(response, "neo_lookup", asteroid_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error looking up asteroid {asteroid_id}: {e}")
            raise
    
    def fetch_neo_browse(self, page: int = 0, size: int = 20) -> Dict[str, Any]:
        """
        Browse overall NEO dataset
        
        Args:
            page: Page number
            size: Results per page
            
        Returns:
            Paginated asteroid data
        """
        params = {
            "page": page,
            "size": size
        }
        
        logger.info(f"Browsing NEO dataset - page {page}, size {size}")
        
        try:
            response = self.client.get("/neo/rest/v1/neo/browse", params=params)
            
            # Save raw response
            self._save_raw_json(response, "neo_browse", f"page_{page}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error browsing NEO dataset: {e}")
            raise
    
    def parse_neo_feed(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse NEO feed response into structured DataFrame
        
        Args:
            raw_data: Raw API response
            
        Returns:
            DataFrame with asteroid approach data
        """
        logger.info("Parsing NEO feed data")
        
        records = []
        
        near_earth_objects = raw_data.get("near_earth_objects", {})
        
        for date_str, asteroids in near_earth_objects.items():
            for asteroid in asteroids:
                # Extract basic info
                asteroid_id = asteroid.get("id")
                name = asteroid.get("name")
                is_potentially_hazardous = asteroid.get("is_potentially_hazardous_asteroid")
                
                # Extract size estimates
                estimated_diameter = asteroid.get("estimated_diameter", {})
                diameter_min_km = estimated_diameter.get("kilometers", {}).get("estimated_diameter_min")
                diameter_max_km = estimated_diameter.get("kilometers", {}).get("estimated_diameter_max")
                
                # Extract close approach data
                close_approach_data = asteroid.get("close_approach_data", [])
                
                for approach in close_approach_data:
                    record = {
                        "asteroid_id": asteroid_id,
                        "name": name,
                        "is_potentially_hazardous": is_potentially_hazardous,
                        "diameter_min_km": diameter_min_km,
                        "diameter_max_km": diameter_max_km,
                        "close_approach_date": approach.get("close_approach_date"),
                        "close_approach_date_full": approach.get("close_approach_date_full"),
                        "epoch_date_close_approach": approach.get("epoch_date_close_approach"),
                        "relative_velocity_kmh": float(approach.get("relative_velocity", {}).get("kilometers_per_hour", 0)),
                        "relative_velocity_kms": float(approach.get("relative_velocity", {}).get("kilometers_per_second", 0)),
                        "miss_distance_km": float(approach.get("miss_distance", {}).get("kilometers", 0)),
                        "miss_distance_lunar": float(approach.get("miss_distance", {}).get("lunar", 0)),
                        "miss_distance_astronomical": float(approach.get("miss_distance", {}).get("astronomical", 0)),
                        "orbiting_body": approach.get("orbiting_body"),
                        "ingestion_timestamp": datetime.now().isoformat()
                    }
                    
                    records.append(record)
        
        df = pd.DataFrame(records)
        
        logger.info(f"Parsed {len(df)} asteroid approach records")
        
        return df
    
    def _save_raw_json(self, data: Dict[str, Any], data_type: str, identifier: str):
        """Save raw JSON response"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{identifier}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Saved raw JSON to {filepath}")
    
    def save_to_parquet(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to Parquet format"""
        filepath = self.output_dir / f"{filename}.parquet"
        df.to_parquet(filepath, index=False, engine='pyarrow')
        logger.info(f"Saved {len(df)} records to {filepath}")
    
    def run_full_ingestion(self, days_ahead: int = 7) -> pd.DataFrame:
        """
        Run complete NEO ingestion pipeline
        
        Args:
            days_ahead: Number of days to fetch ahead
            
        Returns:
            DataFrame with all asteroid data
        """
        logger.info(f"Starting full NEO ingestion for next {days_ahead} days")
        
        # Fetch NEO feed
        raw_data = self.fetch_neo_feed(
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=days_ahead)
        )
        
        # Parse data
        df = self.parse_neo_feed(raw_data)
        
        # Save to Parquet
        timestamp = datetime.now().strftime("%Y%m%d")
        self.save_to_parquet(df, f"neo_approaches_{timestamp}")
        
        # Log statistics
        logger.info(f"Total asteroids: {df['asteroid_id'].nunique()}")
        logger.info(f"Total approaches: {len(df)}")
        logger.info(f"Potentially hazardous: {df['is_potentially_hazardous'].sum()}")
        
        return df
    
    def close(self):
        """Close API client"""
        self.client.close()


# Example usage
if __name__ == "__main__":
    # Configure logger
    logger.add(
        "logs/neo_ingestion.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    # Run ingestion
    ingestion = NEOIngestion()
    
    try:
        df = ingestion.run_full_ingestion(days_ahead=7)
        
        print("\n=== NEO Ingestion Summary ===")
        print(f"Total records: {len(df)}")
        print(f"\nTop 5 closest approaches:")
        print(df.nsmallest(5, 'miss_distance_km')[
            ['name', 'close_approach_date', 'miss_distance_km', 'is_potentially_hazardous']
        ])
        
    finally:
        ingestion.close()
