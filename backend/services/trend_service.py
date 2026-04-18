"""
Trend Service Module for Social Autopilot

This module provides trend awareness functionality using SerpAPI's Google Trends integration.
It fetches real-time trending topics and caches them for efficient access.

Author: Social Autopilot Team
Version: 1.0.0
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendConstants:
    """Constants for trend service configuration"""
    
    # API configuration
    SERPAPI_ENGINE = "google_trends_trending_now"
    DEFAULT_GEO = "US"  # Default region for trends
    DEFAULT_HL = "en"   # Default language
    
    # Cache configuration
    CACHE_EXPIRY_HOURS = 1  # Cache expires after 1 hour
    MAX_TRENDS_RETURN = 10   # Maximum number of trends to return
    
    # Error messages
    API_KEY_MISSING_ERROR = "SERPAPI_KEY not found in .env"
    API_KEY_INVALID_ERROR = "SERPAPI_KEY not properly configured in .env"
    NO_TRENDS_ERROR = "No trends found in API response"
    API_FAILURE_ERROR = "SerpAPI failed: {error}"
    
    # Placeholder values
    PLACEHOLDER_API_KEY = "your_key_here"


@dataclass
class TrendItem:
    """Data class for individual trend items"""
    query: str
    search_volume: int
    increase_percentage: int
    categories: List[str]
    active: bool
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trend item to dictionary"""
        return {
            "query": self.query,
            "search_volume": self.search_volume,
            "increase_percentage": self.increase_percentage,
            "categories": self.categories,
            "active": self.active,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class TrendResponse:
    """Data class for trend API responses"""
    trends: List[TrendItem]
    metadata: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trend response to dictionary"""
        return {
            "trends": [trend.to_dict() for trend in self.trends],
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error
        }


class SerpAPIClient:
    """Client for interacting with SerpAPI Google Trends"""
    
    def __init__(self):
        """Initialize the SerpAPI client with API key validation"""
        self.api_key = self._validate_api_key()
        self.base_url = "https://serpapi.com/search.json"
    
    def _validate_api_key(self) -> str:
        """
        Validate and return the SerpAPI key
        
        Returns:
            Validated API key
            
        Raises:
            ValueError: If API key is missing or invalid
        """
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            raise ValueError(TrendConstants.API_KEY_MISSING_ERROR)
        
        if serpapi_key == TrendConstants.PLACEHOLDER_API_KEY:
            raise ValueError(TrendConstants.API_KEY_INVALID_ERROR)
        
        return serpapi_key
    
    def fetch_trending_topics(
        self, 
        geo: str = TrendConstants.DEFAULT_GEO,
        hl: str = TrendConstants.DEFAULT_HL
    ) -> TrendResponse:
        """
        Fetch trending topics from Google Trends via SerpAPI
        
        Args:
            geo: Geographic region code (default: "US")
            hl: Language code (default: "en")
            
        Returns:
            TrendResponse containing trending topics
            
        Raises:
            RuntimeError: If API call fails
            ValueError: If response format is invalid
        """
        logger.info(f"Fetching trending topics for region: {geo}, language: {hl}")
        
        params = {
            "engine": TrendConstants.SERPAPI_ENGINE,
            "api_key": self.api_key,
            "geo": geo,
            "hl": hl
        }
        
        try:
            import requests
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract trending searches from the response
            if "trending_searches" not in result or not result["trending_searches"]:
                logger.warning("No trending searches found in API response")
                return TrendResponse(
                    trends=[],
                    metadata={"geo": geo, "hl": hl, "timestamp": datetime.now().isoformat()},
                    success=False,
                    error=TrendConstants.NO_TRENDS_ERROR
                )
            
            # Parse trend items
            trend_items = []
            for trend_data in result["trending_searches"][:TrendConstants.MAX_TRENDS_RETURN]:
                try:
                    # Extract categories
                    categories = []
                    if "categories" in trend_data:
                        categories = [cat.get("name", "General") for cat in trend_data["categories"]]
                    
                    # Create trend item
                    trend_item = TrendItem(
                        query=trend_data.get("query", ""),
                        search_volume=trend_data.get("search_volume", 0),
                        increase_percentage=trend_data.get("increase_percentage", 0),
                        categories=categories if categories else ["General"],
                        active=trend_data.get("active", True),
                        timestamp=datetime.now()
                    )
                    trend_items.append(trend_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse trend item: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(trend_items)} trending topics")
            
            return TrendResponse(
                trends=trend_items,
                metadata={
                    "geo": geo,
                    "hl": hl,
                    "timestamp": datetime.now().isoformat(),
                    "total_results": len(result.get("trending_searches", []))
                },
                success=True
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = TrendConstants.API_FAILURE_ERROR.format(error=str(e))
            logger.error(error_msg)
            return TrendResponse(
                trends=[],
                metadata={"geo": geo, "hl": hl},
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = TrendConstants.API_FAILURE_ERROR.format(error=str(e))
            logger.error(error_msg)
            return TrendResponse(
                trends=[],
                metadata={"geo": geo, "hl": hl},
                success=False,
                error=error_msg
            )


def get_trending_topics(
    geo: str = TrendConstants.DEFAULT_GEO,
    hl: str = TrendConstants.DEFAULT_HL
) -> List[str]:
    """
    Get list of trending topic queries
    
    Args:
        geo: Geographic region code (default: "US")
        hl: Language code (default: "en")
        
    Returns:
        List of trending topic strings
    """
    try:
        client = SerpAPIClient()
        response = client.fetch_trending_topics(geo=geo, hl=hl)
        
        if response.success:
            return [trend.query for trend in response.trends]
        else:
            logger.warning(f"Failed to fetch trends: {response.error}")
            return []
            
    except Exception as e:
        logger.error(f"Error getting trending topics: {e}")
        return []


def get_trending_topics_with_metadata(
    geo: str = TrendConstants.DEFAULT_GEO,
    hl: str = TrendConstants.DEFAULT_HL
) -> TrendResponse:
    """
    Get trending topics with full metadata
    
    Args:
        geo: Geographic region code (default: "US")
        hl: Language code (default: "en")
        
    Returns:
        TrendResponse with full trend metadata
    """
    try:
        client = SerpAPIClient()
        return client.fetch_trending_topics(geo=geo, hl=hl)
        
    except Exception as e:
        logger.error(f"Error getting trending topics with metadata: {e}")
        return TrendResponse(
            trends=[],
            metadata={"geo": geo, "hl": hl},
            success=False,
            error=str(e)
        )


def validate_serpapi_key() -> bool:
    """
    Validate SerpAPI key is properly configured
    
    Returns:
        True if API key is valid, False otherwise
    """
    try:
        serpapi_key = os.getenv("SERPAPI_KEY")
        return bool(serpapi_key and serpapi_key != TrendConstants.PLACEHOLDER_API_KEY)
    except Exception:
        return False


if __name__ == "__main__":
    # Example usage and testing
    print("Testing Trend Service...")
    print(f"SerpAPI key valid: {validate_serpapi_key()}")
    
    # Test fetching trending topics
    print("\nFetching trending topics...")
    trends = get_trending_topics()
    print(f"Found {len(trends)} trending topics:")
    for i, trend in enumerate(trends, 1):
        print(f"{i}. {trend}")
    
    # Test fetching with metadata
    print("\nFetching trending topics with metadata...")
    response = get_trending_topics_with_metadata()
    print(f"Success: {response.success}")
    print(f"Total trends: {len(response.trends)}")
    print(f"Metadata: {response.metadata}")
    
    if response.trends:
        print("\nFirst trend with details:")
        first_trend = response.trends[0]
        print(f"Query: {first_trend.query}")
        print(f"Search Volume: {first_trend.search_volume}")
        print(f"Increase: {first_trend.increase_percentage}%")
        print(f"Categories: {first_trend.categories}")
        print(f"Active: {first_trend.active}")
