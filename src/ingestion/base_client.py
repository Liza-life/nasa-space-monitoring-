"""
Base API Client for NASA APIs
Handles authentication, rate limiting, retries, and error handling
"""

import os
import time
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()


class NASAAPIClient:
    """Base client for NASA API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NASA API client
        
        Args:
            api_key: NASA API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("NASA_API_KEY", "DEMO_KEY")
        self.base_url = "https://api.nasa.gov"
        self.session = self._create_session()
        self.rate_limit_per_hour = int(os.getenv("API_RATE_LIMIT_PER_HOUR", 1000))
        self.request_count = 0
        self.request_window_start = time.time()
        
        logger.info(f"NASA API Client initialized with key: {self.api_key[:8]}...")
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        elapsed_time = current_time - self.request_window_start
        
        # Reset counter if an hour has passed
        if elapsed_time >= 3600:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Check if we're over the limit
        if self.request_count >= self.rate_limit_per_hour:
            sleep_time = 3600 - elapsed_time
            logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            self.request_count = 0
            self.request_window_start = time.time()
        
        self.request_count += 1
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make HTTP request to NASA API
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method
            
        Returns:
            JSON response as dictionary
        """
        self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        
        logger.debug(f"Making {method} request to {endpoint}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=int(os.getenv("API_TIMEOUT_SECONDS", 30))
            )
            response.raise_for_status()
            
            logger.info(f"Successfully fetched data from {endpoint}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error for {endpoint}: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {endpoint}: {e}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._make_request(endpoint, params, method="GET")
    
    def close(self):
        """Close session"""
        self.session.close()
        logger.info("API client session closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    # Configure logger
    logger.add(
        "logs/api_client.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    # Test API client
    with NASAAPIClient() as client:
        # Test APOD endpoint
        response = client.get("/planetary/apod")
        print(f"APOD Title: {response.get('title')}")
        print(f"Date: {response.get('date')}")
