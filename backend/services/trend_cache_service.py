"""
Trend Cache Service Module for Social Autopilot

This module provides caching functionality for trend data with automatic expiration.
It implements a 1-hour cache expiration policy to balance freshness and performance.

Author: Social Autopilot Team
Version: 1.0.0
"""

import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models import TrendCache
from backend.services.trend_service import (
    get_trending_topics_with_metadata, 
    TrendResponse,
    TrendConstants
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendCacheService:
    """Service for managing trend data caching with expiration"""
    
    def __init__(self, db: Session):
        """
        Initialize the trend cache service
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.cache_expiry_hours = TrendConstants.CACHE_EXPIRY_HOURS
    
    def _calculate_expiry_time(self) -> datetime:
        """
        Calculate the expiration time for cache entries
        
        Returns:
            DateTime object representing when cache should expire
        """
        return datetime.now() + timedelta(hours=self.cache_expiry_hours)
    
    def _serialize_trend_response(self, response: TrendResponse) -> str:
        """
        Serialize TrendResponse to JSON string for storage
        
        Args:
            response: TrendResponse object to serialize
            
        Returns:
            JSON string representation
        """
        return json.dumps(response.to_dict())
    
    def _deserialize_trend_response(self, data: str) -> TrendResponse:
        """
        Deserialize JSON string to TrendResponse
        
        Args:
            data: JSON string containing trend data
            
        Returns:
            TrendResponse object
        """
        try:
            parsed_data = json.loads(data)
            
            # Reconstruct TrendItem objects
            trend_items = []
            for trend_data in parsed_data.get("trends", []):
                from backend.services.trend_service import TrendItem
                trend_item = TrendItem(
                    query=trend_data.get("query", ""),
                    search_volume=trend_data.get("search_volume", 0),
                    increase_percentage=trend_data.get("increase_percentage", 0),
                    categories=trend_data.get("categories", []),
                    active=trend_data.get("active", True),
                    timestamp=datetime.fromisoformat(trend_data.get("timestamp", datetime.now().isoformat()))
                )
                trend_items.append(trend_item)
            
            return TrendResponse(
                trends=trend_items,
                metadata=parsed_data.get("metadata", {}),
                success=parsed_data.get("success", True),
                error=parsed_data.get("error")
            )
            
        except Exception as e:
            logger.error(f"Failed to deserialize trend data: {e}")
            return TrendResponse(
                trends=[],
                metadata={},
                success=False,
                error=f"Deserialization error: {str(e)}"
            )
    
    def get_cached_trends(
        self, 
        geo: str = "US", 
        hl: str = "en"
    ) -> Optional[TrendResponse]:
        """
        Retrieve cached trends if available and not expired
        
        Args:
            geo: Geographic region code
            hl: Language code
            
        Returns:
            TrendResponse if cache exists and is valid, None otherwise
        """
        try:
            # Query for cache entry
            cache_entry = self.db.query(TrendCache).filter(
                and_(
                    TrendCache.geo == geo,
                    TrendCache.hl == hl
                )
            ).first()
            
            if not cache_entry:
                logger.info(f"No cache found for geo={geo}, hl={hl}")
                return None
            
            # Check if cache has expired
            if cache_entry.is_expired():
                logger.info(f"Cache expired for geo={geo}, hl={hl}")
                # Delete expired entry
                self.db.delete(cache_entry)
                self.db.commit()
                return None
            
            # Deserialize and return cached data
            logger.info(f"Cache hit for geo={geo}, hl={hl}")
            return self._deserialize_trend_response(cache_entry.trends_data)
            
        except Exception as e:
            logger.error(f"Error retrieving cached trends: {e}")
            return None
    
    def cache_trends(
        self, 
        response: TrendResponse, 
        geo: str = "US", 
        hl: str = "en"
    ) -> bool:
        """
        Cache trend response data
        
        Args:
            response: TrendResponse to cache
            geo: Geographic region code
            hl: Language code
            
        Returns:
            True if caching successful, False otherwise
        """
        try:
            # Check if existing cache entry exists
            existing_entry = self.db.query(TrendCache).filter(
                and_(
                    TrendCache.geo == geo,
                    TrendCache.hl == hl
                )
            ).first()
            
            # Serialize the response
            serialized_data = self._serialize_trend_response(response)
            
            if existing_entry:
                # Update existing entry
                existing_entry.trends_data = serialized_data
                existing_entry.created_at = datetime.now()
                existing_entry.expires_at = self._calculate_expiry_time()
                logger.info(f"Updated cache for geo={geo}, hl={hl}")
            else:
                # Create new cache entry
                new_cache = TrendCache(
                    geo=geo,
                    hl=hl,
                    trends_data=serialized_data,
                    expires_at=self._calculate_expiry_time()
                )
                self.db.add(new_cache)
                logger.info(f"Created new cache for geo={geo}, hl={hl}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error caching trends: {e}")
            self.db.rollback()
            return False
    
    def get_or_fetch_trends(
        self, 
        geo: str = "US", 
        hl: str = "en",
        force_refresh: bool = False
    ) -> TrendResponse:
        """
        Get trends from cache or fetch from API if cache is expired/missing
        
        Args:
            geo: Geographic region code
            hl: Language code
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            TrendResponse with trend data
        """
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_response = self.get_cached_trends(geo=geo, hl=hl)
            if cached_response and cached_response.success:
                logger.info(f"Returning cached trends for geo={geo}, hl={hl}")
                return cached_response
        
        # Fetch fresh data from API
        logger.info(f"Fetching fresh trends for geo={geo}, hl={hl}")
        fresh_response = get_trending_topics_with_metadata(geo=geo, hl=hl)
        
        # Cache the fresh response if successful
        if fresh_response.success:
            self.cache_trends(fresh_response, geo=geo, hl=hl)
        
        return fresh_response
    
    def clear_expired_cache(self) -> int:
        """
        Clear all expired cache entries
        
        Returns:
            Number of entries cleared
        """
        try:
            # Find all expired entries
            expired_entries = self.db.query(TrendCache).filter(
                TrendCache.expires_at < datetime.now()
            ).all()
            
            count = len(expired_entries)
            
            # Delete expired entries
            for entry in expired_entries:
                self.db.delete(entry)
            
            self.db.commit()
            
            if count > 0:
                logger.info(f"Cleared {count} expired cache entries")
            
            return count
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            self.db.rollback()
            return 0
    
    def clear_all_cache(self) -> int:
        """
        Clear all cache entries regardless of expiration
        
        Returns:
            Number of entries cleared
        """
        try:
            # Get all entries
            all_entries = self.db.query(TrendCache).all()
            count = len(all_entries)
            
            # Delete all entries
            for entry in all_entries:
                self.db.delete(entry)
            
            self.db.commit()
            
            logger.info(f"Cleared all {count} cache entries")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            self.db.rollback()
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current cache state
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            total_entries = self.db.query(TrendCache).count()
            expired_entries = self.db.query(TrendCache).filter(
                TrendCache.expires_at < datetime.now()
            ).count()
            valid_entries = total_entries - expired_entries
            
            # Get unique regions and languages
            regions = [entry[0] for entry in self.db.query(TrendCache.geo).distinct().all()]
            languages = [entry[0] for entry in self.db.query(TrendCache.hl).distinct().all()]
            
            return {
                "total_entries": total_entries,
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "regions": regions,
                "languages": languages,
                "cache_expiry_hours": self.cache_expiry_hours
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                "error": str(e)
            }


def get_trend_service(db: Session) -> TrendCacheService:
    """
    Factory function to get TrendCacheService instance
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        TrendCacheService instance
    """
    return TrendCacheService(db)


if __name__ == "__main__":
    # Example usage and testing
    print("Testing Trend Cache Service...")
    
    # This would require a database session to test properly
    print("Trend Cache Service module loaded successfully")
    print("Use with a database session to test caching functionality")