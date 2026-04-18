"""
Trends Router Module for Social Autopilot

This module provides API endpoints for accessing trend data and managing trend cache.
It integrates with the trend service and cache service to provide real-time trend information.

Author: Social Autopilot Team
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging

from backend.db import get_db
from backend.services.trend_service import (
    get_trending_topics,
    get_trending_topics_with_metadata,
    validate_serpapi_key,
    TrendResponse
)
from backend.services.trend_cache_service import get_trend_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/trends")
async def get_trends(
    geo: str = Query("US", description="Geographic region code (e.g., 'US', 'UK', 'CA')"),
    hl: str = Query("en", description="Language code (e.g., 'en', 'es', 'fr')"),
    use_cache: bool = Query(True, description="Whether to use cached data if available"),
    force_refresh: bool = Query(False, description="Force refresh of trend data"),
    db: Session = Depends(get_db)
):
    """
    Get trending topics for a specific region and language
    
    Args:
        geo: Geographic region code (default: "US")
        hl: Language code (default: "en")
        use_cache: Whether to use cached data (default: True)
        force_refresh: Force refresh of trend data (default: False)
        db: Database session
        
    Returns:
        Dictionary containing trending topics and metadata
    """
    try:
        logger.info(f"Fetching trends for geo={geo}, hl={hl}, use_cache={use_cache}, force_refresh={force_refresh}")
        
        # Validate API key
        if not validate_serpapi_key():
            logger.warning("SerpAPI key not properly configured")
            return {
                "success": False,
                "error": "SerpAPI key not properly configured in .env file",
                "trends": [],
                "metadata": {"geo": geo, "hl": hl, "cached": False}
            }
        
        # Get trend service
        trend_service = get_trend_service(db)
        
        if use_cache and not force_refresh:
            # Try to get from cache first
            response = trend_service.get_or_fetch_trends(geo=geo, hl=hl, force_refresh=force_refresh)
        else:
            # Fetch fresh data directly
            if force_refresh:
                logger.info("Force refresh requested, bypassing cache")
            response = get_trending_topics_with_metadata(geo=geo, hl=hl)
            
            # Cache the fresh response if successful
            if response.success:
                trend_service.cache_trends(response, geo=geo, hl=hl)
        
        return response.to_dict()
        
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/simple")
async def get_trends_simple(
    geo: str = Query("US", description="Geographic region code"),
    hl: str = Query("en", description="Language code"),
    limit: int = Query(10, description="Maximum number of trends to return")
):
    """
    Get simple list of trending topic queries
    
    Args:
        geo: Geographic region code (default: "US")
        hl: Language code (default: "en")
        limit: Maximum number of trends to return (default: 10)
        
    Returns:
        Dictionary containing list of trend queries
    """
    try:
        logger.info(f"Fetching simple trends for geo={geo}, hl={hl}, limit={limit}")
        
        # Validate API key
        if not validate_serpapi_key():
            logger.warning("SerpAPI key not properly configured")
            return {
                "success": False,
                "error": "SerpAPI key not properly configured in .env file",
                "trends": []
            }
        
        # Get trending topics
        trends = get_trending_topics(geo=geo, hl=hl)
        
        # Limit results
        limited_trends = trends[:limit]
        
        return {
            "success": True,
            "trends": limited_trends,
            "count": len(limited_trends),
            "geo": geo,
            "hl": hl
        }
        
    except Exception as e:
        logger.error(f"Error fetching simple trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/cache/stats")
async def get_cache_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the trend cache
    
    Args:
        db: Database session
        
    Returns:
        Dictionary containing cache statistics
    """
    try:
        trend_service = get_trend_service(db)
        stats = trend_service.get_cache_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trends/cache/clear")
async def clear_cache(
    expired_only: bool = Query(False, description="Only clear expired entries"),
    db: Session = Depends(get_db)
):
    """
    Clear trend cache entries
    
    Args:
        expired_only: Only clear expired entries (default: False)
        db: Database session
        
    Returns:
        Dictionary containing operation results
    """
    try:
        trend_service = get_trend_service(db)
        
        if expired_only:
            count = trend_service.clear_expired_cache()
            message = f"Cleared {count} expired cache entries"
        else:
            count = trend_service.clear_all_cache()
            message = f"Cleared all {count} cache entries"
        
        logger.info(message)
        
        return {
            "success": True,
            "message": message,
            "cleared_count": count
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/validate")
async def validate_api():
    """
    Validate SerpAPI configuration
    
    Returns:
        Dictionary containing validation status
    """
    try:
        is_valid = validate_serpapi_key()
        
        return {
            "success": True,
            "valid": is_valid,
            "message": "SerpAPI key is properly configured" if is_valid else "SerpAPI key not found or invalid"
        }
        
    except Exception as e:
        logger.error(f"Error validating API: {e}")
        return {
            "success": False,
            "valid": False,
            "message": f"Validation error: {str(e)}"
        }


@router.get("/trends/regions")
async def get_supported_regions():
    """
    Get list of supported geographic regions
    
    Returns:
        Dictionary containing supported regions
    """
    try:
        # Common region codes
        regions = [
            {"code": "US", "name": "United States"},
            {"code": "UK", "name": "United Kingdom"},
            {"code": "CA", "name": "Canada"},
            {"code": "AU", "name": "Australia"},
            {"code": "DE", "name": "Germany"},
            {"code": "FR", "name": "France"},
            {"code": "ES", "name": "Spain"},
            {"code": "IT", "name": "Italy"},
            {"code": "BR", "name": "Brazil"},
            {"code": "JP", "name": "Japan"},
            {"code": "IN", "name": "India"},
            {"code": "MX", "name": "Mexico"}
        ]
        
        return {
            "success": True,
            "regions": regions,
            "count": len(regions)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported regions: {e}")
        raise HTTPException(status_code=500, detail=str(e))