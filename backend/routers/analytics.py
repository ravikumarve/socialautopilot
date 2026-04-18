"""
Analytics Router for Social Autopilot

Comprehensive analytics endpoints providing:
- Content performance tracking
- AI-powered insights
- Feedback pattern analysis
- Platform-specific recommendations
- Time-based performance analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from backend import db
from backend.services.analytics_service import get_analytics_service, AnalyticsService
from backend.services.feedback_optimizer import get_feedback_optimizer, FeedbackLoopOptimizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview", response_model=Dict[str, Any])
def get_overview_stats(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive overview statistics for all posts

    Returns:
        - Total posts count
        - Status breakdown (draft, queued, published, rejected)
        - Platform distribution
        - Approval rates
        - Recent activity (last 7 days)
    """
    try:
        analytics_service = get_analytics_service(db_session)
        return analytics_service.get_overview_stats()
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback-patterns", response_model=Dict[str, Any])
def get_feedback_patterns(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Analyze feedback patterns to identify content preferences

    Returns:
        - Total feedback count
        - Action breakdown (approved, rejected, edited)
        - Platform-specific insights
        - Topic-specific insights
        - Approval rates by category
    """
    try:
        analytics_service = get_analytics_service(db_session)
        return analytics_service.get_feedback_patterns()
    except Exception as e:
        logger.error(f"Error analyzing feedback patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-trends", response_model=Dict[str, Any])
def get_performance_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Analyze performance trends over time

    Args:
        days: Number of days to analyze (1-365)

    Returns:
        - Time-based performance data
        - Daily breakdown
        - Trend analysis (improving/declining)
        - Percentage change over time
    """
    try:
        analytics_service = get_analytics_service(db_session)
        return analytics_service.get_performance_trends(days=days)
    except Exception as e:
        logger.error(f"Error analyzing performance trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=Dict[str, Any])
def get_content_recommendations(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Generate AI-powered content recommendations based on performance data

    Returns:
        - Top performing topics
        - Platform-specific recommendations
        - Strategic recommendations
        - Actionable insights
    """
    try:
        analytics_service = get_analytics_service(db_session)
        return analytics_service.get_content_recommendations()
    except Exception as e:
        logger.error(f"Error generating content recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", response_model=Dict[str, Any])
def get_comprehensive_insights(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive AI-powered insights combining all analytics data

    This is the main analytics endpoint that provides a complete picture
    of content performance with actionable insights.

    Returns:
        - Overall health score (excellent/good/fair/poor)
        - Health description
        - Complete overview statistics
        - Feedback analysis
        - Performance trends
        - Personalized recommendations
        - Actionable next steps
    """
    try:
        analytics_service = get_analytics_service(db_session)
        return analytics_service.get_comprehensive_insights()
    except Exception as e:
        logger.error(f"Error generating comprehensive insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/post/{post_id}", response_model=Dict[str, Any])
def get_post_performance_details(
    post_id: int,
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Get detailed performance analysis for a specific post

    Args:
        post_id: ID of the post to analyze

    Returns:
        - Post details (platform, topic, status, content)
        - Feedback metrics
        - Comparison with similar posts
        - Performance indicators
    """
    try:
        analytics_service = get_analytics_service(db_session)
        return analytics_service.get_post_performance_details(post_id)
    except Exception as e:
        logger.error(f"Error getting post performance details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platform/{platform}", response_model=Dict[str, Any])
def get_platform_analytics(
    platform: str,
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Get platform-specific analytics and insights

    Args:
        platform: Platform name (twitter, linkedin, threads)

    Returns:
        - Platform-specific performance metrics
        - Approval rates
        - Top performing topics
        - Platform recommendations
    """
    try:
        analytics_service = get_analytics_service(db_session)

        # Get overview stats
        overview = analytics_service.get_overview_stats()
        platform_data = overview["platform_distribution"].get(platform, {})

        # Get feedback patterns
        feedback = analytics_service.get_feedback_patterns()
        platform_feedback = feedback["platform_insights"].get(platform, {})

        # Get recommendations
        recommendations = analytics_service.get_content_recommendations()
        platform_rec = recommendations["platform_recommendations"].get(platform, {})

        return {
            "platform": platform,
            "total_posts": platform_data,
            "feedback_insights": platform_feedback,
            "recommendations": platform_rec,
            "analyzed_at": recommendations.get("generated_at")
        }
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
def get_analytics_health(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Get overall analytics health and system status

    Returns:
        - System health status
        - Data availability
        - Analytics readiness
        - Recommendations for data collection
    """
    try:
        analytics_service = get_analytics_service(db_session)
        overview = analytics_service.get_overview_stats()

        total_posts = overview["total_posts"]
        feedback_count = overview.get("feedback_count", 0)

        # Determine health status
        if total_posts < 10:
            health_status = "insufficient_data"
            message = "Need more posts to provide meaningful analytics"
            recommendation = "Generate at least 10 posts to enable comprehensive analytics"
        elif feedback_count < 5:
            health_status = "limited_feedback"
            message = "Posts available but limited feedback data"
            recommendation = "Review and provide feedback on more posts to enable pattern analysis"
        else:
            health_status = "healthy"
            message = "Analytics system fully operational"
            recommendation = "Continue regular content generation and feedback collection"

        return {
            "health_status": health_status,
            "message": message,
            "recommendation": recommendation,
            "data_availability": {
                "total_posts": total_posts,
                "feedback_count": feedback_count,
                "platforms_active": len(overview["platform_distribution"]),
                "topics_tracked": len(analytics_service.get_feedback_patterns().get("topic_insights", {}))
            },
            "checked_at": overview["generated_at"]
        }
    except Exception as e:
        logger.error(f"Error getting analytics health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Feedback Loop Optimization Endpoints

@router.get("/feedback/patterns", response_model=Dict[str, Any])
def analyze_feedback_patterns(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Analyze approval/rejection patterns to identify success factors

    Returns:
        - Pattern analysis results
        - Success factors with confidence scores
        - Content characteristics that correlate with approval
    """
    try:
        optimizer = get_feedback_optimizer(db_session)
        return optimizer.analyze_approval_patterns()
    except Exception as e:
        logger.error(f"Error analyzing feedback patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/optimization", response_model=Dict[str, Any])
def get_optimization_suggestions(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Get optimization suggestions for content generation

    Returns:
        - Topic optimization recommendations
        - Content optimization guidelines
        - Brand voice optimization
        - Comprehensive optimization strategy
    """
    try:
        optimizer = get_feedback_optimizer(db_session)
        return optimizer.get_optimization_suggestions()
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/progress", response_model=Dict[str, Any])
def track_optimization_progress(
    db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    """
    Track progress of optimization efforts over time

    Returns:
        - Recent period performance metrics
        - Baseline comparison
        - Optimization progress indicators
        - Trend analysis
    """
    try:
        optimizer = get_feedback_optimizer(db_session)
        return optimizer.track_optimization_progress()
    except Exception as e:
        logger.error(f"Error tracking optimization progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))