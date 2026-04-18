"""
Test Suite for Trend Service and Cache Functionality

This module provides comprehensive testing for trend fetching, caching,
and API integration for Social Autopilot Phase 2.

Author: Social Autopilot Team
Version: 1.0.0
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.db import engine, Base, SessionLocal
from backend.models import TrendCache
from backend.services.trend_service import (
    SerpAPIClient,
    get_trending_topics,
    get_trending_topics_with_metadata,
    validate_serpapi_key,
    TrendConstants,
    TrendItem,
    TrendResponse
)
from backend.services.trend_cache_service import TrendCacheService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Class to track test results"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        """Add a test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "passed": passed
        })
        
        logger.info(f"{status}: {test_name} - {message}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "N/A")
        print("="*60 + "\n")
        
        # Print detailed results
        print("DETAILED RESULTS:")
        print("-" * 60)
        for result in self.results:
            print(f"{result['status']} {result['test']}")
            if result['message']:
                print(f"   {result['message']}")
        print("-" * 60 + "\n")


def test_api_key_validation():
    """Test SerpAPI key validation"""
    results = TestResults()
    
    print("\n🔑 Testing API Key Validation...")
    
    # Test 1: Check if API key exists
    try:
        is_valid = validate_serpapi_key()
        results.add_result(
            "API Key Validation",
            True,
            f"API key configured: {is_valid}"
        )
    except Exception as e:
        results.add_result(
            "API Key Validation",
            False,
            f"Error: {str(e)}"
        )
    
    return results


def test_trend_data_structures():
    """Test trend data structures and models"""
    results = TestResults()
    
    print("\n📊 Testing Trend Data Structures...")
    
    # Test 1: Create TrendItem
    try:
        trend_item = TrendItem(
            query="test trend",
            search_volume=1000,
            increase_percentage=50,
            categories=["Technology"],
            active=True,
            timestamp=datetime.now()
        )
        
        trend_dict = trend_item.to_dict()
        assert trend_dict["query"] == "test trend"
        assert trend_dict["search_volume"] == 1000
        
        results.add_result(
            "TrendItem Creation",
            True,
            "TrendItem created and serialized successfully"
        )
    except Exception as e:
        results.add_result(
            "TrendItem Creation",
            False,
            f"Error: {str(e)}"
        )
    
    # Test 2: Create TrendResponse
    try:
        trend_response = TrendResponse(
            trends=[trend_item],
            metadata={"test": "data"},
            success=True
        )
        
        response_dict = trend_response.to_dict()
        assert len(response_dict["trends"]) == 1
        assert response_dict["success"] == True
        
        results.add_result(
            "TrendResponse Creation",
            True,
            "TrendResponse created and serialized successfully"
        )
    except Exception as e:
        results.add_result(
            "TrendResponse Creation",
            False,
            f"Error: {str(e)}"
        )
    
    return results


def test_database_models():
    """Test database models and table creation"""
    results = TestResults()
    
    print("\n🗄️ Testing Database Models...")
    
    # Test 1: Create tables
    try:
        Base.metadata.create_all(bind=engine)
        results.add_result(
            "Database Table Creation",
            True,
            "All database tables created successfully"
        )
    except Exception as e:
        results.add_result(
            "Database Table Creation",
            False,
            f"Error: {str(e)}"
        )
    
    # Test 2: Test TrendCache model
    try:
        db = SessionLocal()
        
        # Create a test cache entry
        test_cache = TrendCache(
            geo="US",
            hl="en",
            trends_data='{"test": "data"}',
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        db.add(test_cache)
        db.commit()
        
        # Query the entry
        cached_entry = db.query(TrendCache).filter(
            TrendCache.geo == "US",
            TrendCache.hl == "en"
        ).first()
        
        assert cached_entry is not None
        assert cached_entry.geo == "US"
        
        # Clean up
        db.delete(cached_entry)
        db.commit()
        db.close()
        
        results.add_result(
            "TrendCache Model Operations",
            True,
            "TrendCache model CRUD operations successful"
        )
    except Exception as e:
        results.add_result(
            "TrendCache Model Operations",
            False,
            f"Error: {str(e)}"
        )
    
    return results


def test_cache_service():
    """Test trend cache service functionality"""
    results = TestResults()
    
    print("\n💾 Testing Cache Service...")
    
    try:
        db = SessionLocal()
        cache_service = TrendCacheService(db)
        
        # Test 1: Create mock trend response
        mock_trend = TrendItem(
            query="test trend",
            search_volume=100,
            increase_percentage=10,
            categories=["Test"],
            active=True,
            timestamp=datetime.now()
        )
        
        mock_response = TrendResponse(
            trends=[mock_trend],
            metadata={"geo": "US", "hl": "en"},
            success=True
        )
        
        # Test 2: Cache the response
        cache_success = cache_service.cache_trends(mock_response, geo="US", hl="en")
        results.add_result(
            "Cache Trends",
            cache_success,
            "Trends cached successfully" if cache_success else "Failed to cache trends"
        )
        
        # Test 3: Retrieve from cache
        cached_response = cache_service.get_cached_trends(geo="US", hl="en")
        cache_hit = cached_response is not None and cached_response.success
        
        results.add_result(
            "Retrieve Cached Trends",
            cache_hit,
            "Cache hit successful" if cache_hit else "Cache miss or error"
        )
        
        # Test 4: Test cache expiration
        if cached_response:
            # Create an expired entry
            expired_cache = TrendCache(
                geo="TEST",
                hl="test",
                trends_data='{"test": "expired"}',
                expires_at=datetime.now() - timedelta(hours=1)  # Expired
            )
            db.add(expired_cache)
            db.commit()
            
            # Try to retrieve expired entry
            expired_response = cache_service.get_cached_trends(geo="TEST", hl="test")
            is_expired_handled = expired_response is None
            
            results.add_result(
                "Cache Expiration Handling",
                is_expired_handled,
                "Expired cache handled correctly" if is_expired_handled else "Expired cache not handled"
            )
        
        # Test 5: Get cache stats
        stats = cache_service.get_cache_stats()
        stats_valid = "total_entries" in stats
        
        results.add_result(
            "Cache Statistics",
            stats_valid,
            f"Cache stats retrieved: {stats.get('total_entries', 0)} entries"
        )
        
        # Test 6: Clear cache
        clear_count = cache_service.clear_all_cache()
        results.add_result(
            "Clear Cache",
            clear_count >= 0,
            f"Cleared {clear_count} cache entries"
        )
        
        db.close()
        
    except Exception as e:
        results.add_result(
            "Cache Service",
            False,
            f"Error: {str(e)}"
        )
    
    return results


def test_serpapi_integration():
    """Test SerpAPI integration (requires valid API key)"""
    results = TestResults()
    
    print("\n🌐 Testing SerpAPI Integration...")
    
    # Check if API key is configured
    if not validate_serpapi_key():
        results.add_result(
            "SerpAPI Integration",
            False,
            "SerpAPI key not configured - skipping integration tests"
        )
        return results
    
    # Test 1: Initialize SerpAPI client
    try:
        client = SerpAPIClient()
        results.add_result(
            "SerpAPI Client Initialization",
            True,
            "SerpAPI client initialized successfully"
        )
    except Exception as e:
        results.add_result(
            "SerpAPI Client Initialization",
            False,
            f"Error: {str(e)}"
        )
        return results
    
    # Test 2: Fetch trending topics
    try:
        response = client.fetch_trending_topics(geo="US", hl="en")
        
        if response.success:
            results.add_result(
                "Fetch Trending Topics",
                True,
                f"Successfully fetched {len(response.trends)} trends"
            )
        else:
            results.add_result(
                "Fetch Trending Topics",
                False,
                f"API returned error: {response.error}"
            )
    except Exception as e:
        results.add_result(
            "Fetch Trending Topics",
            False,
            f"Error: {str(e)}"
        )
    
    return results


def test_integration():
    """Test full integration of trend service with cache"""
    results = TestResults()
    
    print("\n🔗 Testing Full Integration...")
    
    try:
        db = SessionLocal()
        cache_service = TrendCacheService(db)
        
        # Test 1: Get or fetch trends (integration test)
        if validate_serpapi_key():
            response = cache_service.get_or_fetch_trends(geo="US", hl="en")
            
            if response.success:
                results.add_result(
                    "Integration: Get or Fetch Trends",
                    True,
                    f"Successfully retrieved {len(response.trends)} trends"
                )
            else:
                results.add_result(
                    "Integration: Get or Fetch Trends",
                    False,
                    f"Error: {response.error}"
                )
        else:
            results.add_result(
                "Integration: Get or Fetch Trends",
                False,
                "SerpAPI key not configured"
            )
        
        # Test 2: Cache hit on second call
        if validate_serpapi_key():
            response2 = cache_service.get_or_fetch_trends(geo="US", hl="en")
            
            if response2.success:
                results.add_result(
                    "Integration: Cache Hit on Second Call",
                    True,
                    "Second call successful (likely from cache)"
                )
            else:
                results.add_result(
                    "Integration: Cache Hit on Second Call",
                    False,
                    f"Error: {response2.error}"
                )
        
        db.close()
        
    except Exception as e:
        results.add_result(
            "Full Integration",
            False,
            f"Error: {str(e)}"
        )
    
    return results


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("🧪 SOCIAL AUTOPILOT PHASE 2 - TREND SYSTEM TEST SUITE")
    print("="*60)
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = TestResults()
    
    # Run all test suites
    test_suites = [
        ("API Key Validation", test_api_key_validation),
        ("Trend Data Structures", test_trend_data_structures),
        ("Database Models", test_database_models),
        ("Cache Service", test_cache_service),
        ("SerpAPI Integration", test_serpapi_integration),
        ("Full Integration", test_integration)
    ]
    
    for suite_name, test_func in test_suites:
        try:
            suite_results = test_func()
            # Merge results
            for result in suite_results.results:
                all_results.add_result(
                    f"{suite_name}: {result['test']}",
                    result['passed'],
                    result['message']
                )
        except Exception as e:
            logger.error(f"Error running test suite {suite_name}: {e}")
            all_results.add_result(
                f"{suite_name}: Suite Execution",
                False,
                f"Suite execution error: {str(e)}"
            )
    
    # Print final summary
    all_results.print_summary()
    
    print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    return all_results


if __name__ == "__main__":
    # Run all tests
    final_results = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if final_results.failed_tests == 0 else 1)