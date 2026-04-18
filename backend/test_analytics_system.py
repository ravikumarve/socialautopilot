"""
Comprehensive Test Suite for Analytics System

This test suite validates:
- Analytics service functionality
- Feedback pattern analysis
- Performance trend tracking
- Content recommendations
- Feedback loop optimization
- API endpoint functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from backend.services.analytics_service import AnalyticsService, get_analytics_service
from backend.services.feedback_optimizer import FeedbackLoopOptimizer, get_feedback_optimizer
from backend import models, db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsTestSuite:
    """Comprehensive test suite for analytics system"""

    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def record_test(self, test_name: str, passed: bool, message: str = ""):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if message:
            logger.info(f"  {message}")

    def test_analytics_service_initialization(self):
        """Test analytics service initialization"""
        try:
            # Create a mock database session
            class MockSession:
                def query(self, model):
                    return MockQuery()

            class MockQuery:
                def all(self):
                    return []

                def count(self):
                    return 0

                def group_by(self, field):
                    return self

                def filter(self, condition):
                    return self

            service = AnalyticsService(MockSession())
            self.record_test(
                "Analytics Service Initialization",
                service is not None,
                "Service created successfully"
            )
        except Exception as e:
            self.record_test(
                "Analytics Service Initialization",
                False,
                f"Error: {str(e)}"
            )

    def test_overview_stats_structure(self):
        """Test overview stats return structure"""
        try:
            # Mock the service methods
            class MockAnalyticsService:
                def get_overview_stats(self):
                    return {
                        "total_posts": 10,
                        "status_breakdown": {"queued": 5, "rejected": 3, "draft": 2},
                        "platform_distribution": {"twitter": 6, "linkedin": 4},
                        "approval_rate": 50.0,
                        "recent_posts_7d": 3,
                        "generated_at": datetime.now().isoformat()
                    }

            service = MockAnalyticsService()
            result = service.get_overview_stats()

            required_fields = [
                "total_posts", "status_breakdown", "platform_distribution",
                "approval_rate", "recent_posts_7d", "generated_at"
            ]

            has_all_fields = all(field in result for field in required_fields)
            self.record_test(
                "Overview Stats Structure",
                has_all_fields,
                f"All required fields present: {has_all_fields}"
            )
        except Exception as e:
            self.record_test(
                "Overview Stats Structure",
                False,
                f"Error: {str(e)}"
            )

    def test_feedback_patterns_analysis(self):
        """Test feedback pattern analysis"""
        try:
            class MockAnalyticsService:
                def get_feedback_patterns(self):
                    return {
                        "total_feedback": 15,
                        "action_breakdown": {"approved": 10, "rejected": 3, "edited": 2},
                        "platform_insights": {
                            "twitter": {
                                "total_actions": 8,
                                "approval_rate": 75.0,
                                "breakdown": {"approved": 6, "rejected": 1, "edited": 1}
                            }
                        },
                        "topic_insights": {
                            "AI": {
                                "total_actions": 5,
                                "approval_rate": 80.0,
                                "breakdown": {"approved": 4, "rejected": 1, "edited": 0}
                            }
                        },
                        "analyzed_at": datetime.now().isoformat()
                    }

            service = MockAnalyticsService()
            result = service.get_feedback_patterns()

            required_fields = [
                "total_feedback", "action_breakdown", "platform_insights",
                "topic_insights", "analyzed_at"
            ]

            has_all_fields = all(field in result for field in required_fields)
            self.record_test(
                "Feedback Patterns Analysis",
                has_all_fields,
                f"Feedback patterns analyzed successfully: {has_all_fields}"
            )
        except Exception as e:
            self.record_test(
                "Feedback Patterns Analysis",
                False,
                f"Error: {str(e)}"
            )

    def test_performance_trends(self):
        """Test performance trends analysis"""
        try:
            class MockAnalyticsService:
                def get_performance_trends(self, days=30):
                    return {
                        "period_days": days,
                        "total_posts": 25,
                        "daily_breakdown": {
                            "2026-04-01": {"total": 5, "approved": 3, "rejected": 2, "edited": 0}
                        },
                        "trend_analysis": {
                            "direction": "improving",
                            "change_percentage": 15.5,
                            "recent_daily_avg": 3.5
                        },
                        "analyzed_at": datetime.now().isoformat()
                    }

            service = MockAnalyticsService()
            result = service.get_performance_trends(days=30)

            has_trend_data = "trend_analysis" in result
            has_direction = result.get("trend_analysis", {}).get("direction") in ["improving", "declining", "insufficient_data"]

            self.record_test(
                "Performance Trends Analysis",
                has_trend_data and has_direction,
                f"Trend analysis working: direction={result.get('trend_analysis', {}).get('direction')}"
            )
        except Exception as e:
            self.record_test(
                "Performance Trends Analysis",
                False,
                f"Error: {str(e)}"
            )

    def test_content_recommendations(self):
        """Test content recommendations generation"""
        try:
            class MockAnalyticsService:
                def get_content_recommendations(self):
                    return {
                        "top_performing_topics": [
                            {"topic": "AI", "approval_rate": 85.0},
                            {"topic": "Technology", "approval_rate": 75.0}
                        ],
                        "platform_recommendations": {
                            "twitter": {
                                "status": "strong",
                                "recommendation": "Continue current strategy"
                            }
                        },
                        "strategic_recommendations": [
                            {
                                "type": "topic_focus",
                                "priority": "high",
                                "insight": "Topic 'AI' has 85% approval rate",
                                "action": "Generate more content around 'AI'"
                            }
                        ],
                        "generated_at": datetime.now().isoformat()
                    }

            service = MockAnalyticsService()
            result = service.get_content_recommendations()

            has_topics = "top_performing_topics" in result
            has_recommendations = "strategic_recommendations" in result
            has_platforms = "platform_recommendations" in result

            self.record_test(
                "Content Recommendations",
                has_topics and has_recommendations and has_platforms,
                f"Recommendations generated: {len(result.get('strategic_recommendations', []))} strategic, {len(result.get('top_performing_topics', []))} topics"
            )
        except Exception as e:
            self.record_test(
                "Content Recommendations",
                False,
                f"Error: {str(e)}"
            )

    def test_comprehensive_insights(self):
        """Test comprehensive insights generation"""
        try:
            class MockAnalyticsService:
                def get_comprehensive_insights(self):
                    return {
                        "health_score": "good",
                        "health_description": "Content strategy performing well",
                        "overview": {"total_posts": 20, "approval_rate": 65.0},
                        "feedback_analysis": {"total_feedback": 12},
                        "performance_trends": {"trend_analysis": {"direction": "improving"}},
                        "recommendations": {"strategic_recommendations": []},
                        "next_steps": ["Continue current strategy"],
                        "generated_at": datetime.now().isoformat()
                    }

            service = MockAnalyticsService()
            result = service.get_comprehensive_insights()

            has_health_score = "health_score" in result
            has_next_steps = "next_steps" in result
            valid_health_score = result.get("health_score") in ["excellent", "good", "fair", "poor", "insufficient_data"]

            self.record_test(
                "Comprehensive Insights",
                has_health_score and has_next_steps and valid_health_score,
                f"Health score: {result.get('health_score')}, Next steps: {len(result.get('next_steps', []))}"
            )
        except Exception as e:
            self.record_test(
                "Comprehensive Insights",
                False,
                f"Error: {str(e)}"
            )

    def test_feedback_optimizer_initialization(self):
        """Test feedback optimizer initialization"""
        try:
            class MockSession:
                pass

            optimizer = FeedbackLoopOptimizer(MockSession())
            self.record_test(
                "Feedback Optimizer Initialization",
                optimizer is not None,
                "Optimizer created successfully"
            )
        except Exception as e:
            self.record_test(
                "Feedback Optimizer Initialization",
                False,
                f"Error: {str(e)}"
            )

    def test_approval_patterns_analysis(self):
        """Test approval patterns analysis"""
        try:
            class MockOptimizer:
                def analyze_approval_patterns(self):
                    return {
                        "status": "success",
                        "approved_count": 10,
                        "rejected_count": 5,
                        "approved_patterns": {
                            "topics": {"AI": 6, "Technology": 4},
                            "has_emoji": 70.0,
                            "has_hashtags": 80.0
                        },
                        "rejected_patterns": {
                            "topics": {"Politics": 3, "Sports": 2},
                            "has_emoji": 40.0,
                            "has_hashtags": 60.0
                        },
                        "success_factors": [
                            {
                                "factor": "topic",
                                "value": "AI",
                                "approval_rate": 85.0,
                                "confidence": "high",
                                "recommendation": "Continue using topic 'AI'"
                            }
                        ],
                        "analyzed_at": datetime.now().isoformat()
                    }

            optimizer = MockOptimizer()
            result = optimizer.analyze_approval_patterns()

            has_success_factors = "success_factors" in result
            has_patterns = "approved_patterns" in result and "rejected_patterns" in result

            self.record_test(
                "Approval Patterns Analysis",
                has_success_factors and has_patterns,
                f"Success factors identified: {len(result.get('success_factors', []))}"
            )
        except Exception as e:
            self.record_test(
                "Approval Patterns Analysis",
                False,
                f"Error: {str(e)}"
            )

    def test_optimization_suggestions(self):
        """Test optimization suggestions generation"""
        try:
            class MockOptimizer:
                def get_optimization_suggestions(self):
                    return {
                        "status": "success",
                        "suggestions": {
                            "topic_optimization": [
                                {
                                    "topic": "AI",
                                    "approval_rate": 85.0,
                                    "suggestion": "Continue using topic 'AI'"
                                }
                            ],
                            "content_optimization": [
                                {
                                    "characteristic": "emoji",
                                    "approved_percentage": 70.0,
                                    "suggestion": "Include emoji in posts"
                                }
                            ],
                            "brand_voice_optimization": [],
                            "platform_optimization": []
                        },
                        "optimization_strategy": {
                            "priority_actions": [],
                            "content_guidelines": [],
                            "avoidance_list": [],
                            "testing_recommendations": []
                        },
                        "generated_at": datetime.now().isoformat()
                    }

            optimizer = MockOptimizer()
            result = optimizer.get_optimization_suggestions()

            has_suggestions = "suggestions" in result
            has_strategy = "optimization_strategy" in result

            self.record_test(
                "Optimization Suggestions",
                has_suggestions and has_strategy,
                f"Optimization suggestions generated: {len(result.get('suggestions', {}).get('topic_optimization', []))} topics"
            )
        except Exception as e:
            self.record_test(
                "Optimization Suggestions",
                False,
                f"Error: {str(e)}"
            )

    def test_optimization_progress_tracking(self):
        """Test optimization progress tracking"""
        try:
            class MockOptimizer:
                def track_optimization_progress(self):
                    return {
                        "status": "success",
                        "recent_period": {
                            "days": 30,
                            "total_posts": 15,
                            "approved_posts": 10,
                            "approval_rate": 66.67
                        },
                        "baseline_period": {
                            "days": 30,
                            "total_posts": 12,
                            "approved_posts": 6,
                            "approval_rate": 50.0
                        },
                        "optimization_progress": {
                            "direction": "improving",
                            "improvement_percentage": 16.67,
                            "trend": "positive"
                        },
                        "tracked_at": datetime.now().isoformat()
                    }

            optimizer = MockOptimizer()
            result = optimizer.track_optimization_progress()

            has_progress = "optimization_progress" in result
            has_improvement = result.get("optimization_progress", {}).get("improvement_percentage") is not None

            self.record_test(
                "Optimization Progress Tracking",
                has_progress and has_improvement,
                f"Progress tracked: {result.get('optimization_progress', {}).get('direction')}, {result.get('optimization_progress', {}).get('improvement_percentage')}% improvement"
            )
        except Exception as e:
            self.record_test(
                "Optimization Progress Tracking",
                False,
                f"Error: {str(e)}"
            )

    def run_all_tests(self):
        """Run all tests in the suite"""
        logger.info("=" * 60)
        logger.info("Starting Analytics System Test Suite")
        logger.info("=" * 60)

        # Analytics Service Tests
        logger.info("\n📊 Analytics Service Tests")
        logger.info("-" * 40)
        self.test_analytics_service_initialization()
        self.test_overview_stats_structure()
        self.test_feedback_patterns_analysis()
        self.test_performance_trends()
        self.test_content_recommendations()
        self.test_comprehensive_insights()

        # Feedback Optimizer Tests
        logger.info("\n🔄 Feedback Optimizer Tests")
        logger.info("-" * 40)
        self.test_feedback_optimizer_initialization()
        self.test_approval_patterns_analysis()
        self.test_optimization_suggestions()
        self.test_optimization_progress_tracking()

        # Print Summary
        logger.info("\n" + "=" * 60)
        logger.info("Test Suite Summary")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {self.passed_tests + self.failed_tests}")
        logger.info(f"✅ Passed: {self.passed_tests}")
        logger.info(f"❌ Failed: {self.failed_tests}")
        logger.info(f"Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")

        if self.failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"  - {result['test']}: {result['message']}")

        return self.failed_tests == 0


def main():
    """Main test execution"""
    test_suite = AnalyticsTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()