"""
Analytics Service for Social Autopilot

This service provides comprehensive analytics and AI-powered insights
for social media content performance, including feedback pattern analysis
and optimization recommendations.

Key Features:
- Content performance tracking
- AI-powered insights using multi-API support
- Feedback pattern analysis
- Trend performance correlation
- Platform-specific recommendations
- Time-based performance analysis
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend import models
from backend.services.ai_service import generate_trend_aware_post
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Comprehensive analytics service for social media content performance"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_overview_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive overview statistics for all posts

        Returns:
            Dict containing total posts, approval rates, platform distribution, etc.
        """
        try:
            # Total posts by status
            status_counts = (
                self.db_session.query(
                    models.Post.status,
                    func.count(models.Post.id).label('count')
                )
                .group_by(models.Post.status)
                .all()
            )

            status_dict = {status: count for status, count in status_counts}
            total_posts = sum(status_dict.values())

            # Platform distribution
            platform_counts = (
                self.db_session.query(
                    models.Post.platform,
                    func.count(models.Post.id).label('count')
                )
                .group_by(models.Post.platform)
                .all()
            )

            platform_dict = {platform: count for platform, count in platform_counts}

            # Calculate approval rate
            approved = status_dict.get('queued', 0) + status_dict.get('published', 0)
            rejected = status_dict.get('rejected', 0)
            approval_rate = (approved / total_posts * 100) if total_posts > 0 else 0

            # Time-based analysis (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_posts = (
                self.db_session.query(models.Post)
                .filter(models.Post.created_at >= week_ago)
                .count()
            )

            return {
                "total_posts": total_posts,
                "status_breakdown": status_dict,
                "platform_distribution": platform_dict,
                "approval_rate": round(approval_rate, 2),
                "recent_posts_7d": recent_posts,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting overview stats: {e}")
            raise

    def get_feedback_patterns(self) -> Dict[str, Any]:
        """
        Analyze feedback patterns to identify content preferences

        Returns:
            Dict containing feedback analysis, approval patterns, and rejection reasons
        """
        try:
            # Get all feedback data
            feedback_data = (
                self.db_session.query(models.PostFeedback)
                .join(models.Post)
                .all()
            )

            if not feedback_data:
                return {
                    "message": "No feedback data available yet",
                    "total_feedback": 0,
                    "patterns": {}
                }

            # Analyze approval vs rejection patterns
            action_counts = {}
            platform_actions = {}
            topic_actions = {}

            for feedback in feedback_data:
                # Count actions
                action = feedback.action
                action_counts[action] = action_counts.get(action, 0) + 1

                # Platform-specific patterns
                if feedback.post:
                    platform = feedback.post.platform
                    if platform not in platform_actions:
                        platform_actions[platform] = {"approved": 0, "rejected": 0, "edited": 0}

                    if action == "approved":
                        platform_actions[platform]["approved"] += 1
                    elif action == "rejected":
                        platform_actions[platform]["rejected"] += 1
                    elif action == "edited":
                        platform_actions[platform]["edited"] += 1

                    # Topic-specific patterns
                    topic = feedback.post.topic
                    if topic:
                        if topic not in topic_actions:
                            topic_actions[topic] = {"approved": 0, "rejected": 0, "edited": 0}

                        if action == "approved":
                            topic_actions[topic]["approved"] += 1
                        elif action == "rejected":
                            topic_actions[topic]["rejected"] += 1
                        elif action == "edited":
                            topic_actions[topic]["edited"] += 1

            # Calculate approval rates by platform
            platform_insights = {}
            for platform, actions in platform_actions.items():
                total = sum(actions.values())
                if total > 0:
                    approval_rate = (actions["approved"] / total) * 100
                    platform_insights[platform] = {
                        "total_actions": total,
                        "approval_rate": round(approval_rate, 2),
                        "breakdown": actions
                    }

            # Calculate approval rates by topic
            topic_insights = {}
            for topic, actions in topic_actions.items():
                total = sum(actions.values())
                if total > 0:
                    approval_rate = (actions["approved"] / total) * 100
                    topic_insights[topic] = {
                        "total_actions": total,
                        "approval_rate": round(approval_rate, 2),
                        "breakdown": actions
                    }

            return {
                "total_feedback": len(feedback_data),
                "action_breakdown": action_counts,
                "platform_insights": platform_insights,
                "topic_insights": topic_insights,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing feedback patterns: {e}")
            raise

    def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Args:
            days: Number of days to analyze

        Returns:
            Dict containing time-based performance data and trends
        """
        try:
            start_date = datetime.now() - timedelta(days=days)

            # Get posts created in the time period
            posts = (
                self.db_session.query(models.Post)
                .filter(models.Post.created_at >= start_date)
                .order_by(models.Post.created_at)
                .all()
            )

            # Group by day
            daily_stats = {}
            for post in posts:
                date_key = post.created_at.strftime("%Y-%m-%d")
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        "total": 0,
                        "approved": 0,
                        "rejected": 0,
                        "edited": 0
                    }

                daily_stats[date_key]["total"] += 1
                if post.status in ["queued", "published"]:
                    daily_stats[date_key]["approved"] += 1
                elif post.status == "rejected":
                    daily_stats[date_key]["rejected"] += 1

            # Calculate trends
            if len(daily_stats) > 1:
                dates = sorted(daily_stats.keys())
                recent_avg = sum(daily_stats[d]["approved"] for d in dates[-7:]) / min(7, len(dates))
                earlier_avg = sum(daily_stats[d]["approved"] for d in dates[:-7]) / max(1, len(dates) - 7)

                trend_direction = "improving" if recent_avg > earlier_avg else "declining"
                trend_change = round(((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0, 2)
            else:
                trend_direction = "insufficient_data"
                trend_change = 0

            return {
                "period_days": days,
                "total_posts": len(posts),
                "daily_breakdown": daily_stats,
                "trend_analysis": {
                    "direction": trend_direction,
                    "change_percentage": trend_change,
                    "recent_daily_avg": round(recent_avg, 2) if 'recent_avg' in locals() else 0
                },
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            raise

    def get_content_recommendations(self) -> Dict[str, Any]:
        """
        Generate AI-powered content recommendations based on performance data

        Returns:
            Dict containing personalized recommendations and insights
        """
        try:
            # Get feedback patterns
            feedback_patterns = self.get_feedback_patterns()

            # Get performance trends
            performance_trends = self.get_performance_trends(days=30)

            # Analyze top-performing topics
            topic_insights = feedback_patterns.get("topic_insights", {})
            top_topics = sorted(
                topic_insights.items(),
                key=lambda x: x[1]["approval_rate"],
                reverse=True
            )[:5]

            # Analyze platform performance
            platform_insights = feedback_patterns.get("platform_insights", {})
            platform_recommendations = {}

            for platform, insights in platform_insights.items():
                if insights["approval_rate"] > 70:
                    platform_recommendations[platform] = {
                        "status": "strong",
                        "recommendation": f"Continue current strategy for {platform}. High approval rate indicates good content fit."
                    }
                elif insights["approval_rate"] > 50:
                    platform_recommendations[platform] = {
                        "status": "moderate",
                        "recommendation": f"Consider refining content for {platform}. Moderate approval rate suggests room for improvement."
                    }
                else:
                    platform_recommendations[platform] = {
                        "status": "needs_improvement",
                        "recommendation": f"Significant content adjustment needed for {platform}. Low approval rate indicates poor content fit."
                    }

            # Generate strategic recommendations
            recommendations = []

            # Topic-based recommendations
            if top_topics:
                best_topic = top_topics[0]
                recommendations.append({
                    "type": "topic_focus",
                    "priority": "high",
                    "insight": f"Topic '{best_topic[0]}' has {best_topic[1]['approval_rate']}% approval rate",
                    "action": f"Generate more content around '{best_topic[0]}' to leverage high approval patterns"
                })

            # Trend-based recommendations
            if performance_trends["trend_analysis"]["direction"] == "improving":
                recommendations.append({
                    "type": "trend_positive",
                    "priority": "medium",
                    "insight": f"Approval rate improving by {performance_trends['trend_analysis']['change_percentage']}%",
                    "action": "Continue current content strategy and maintain posting frequency"
                })
            elif performance_trends["trend_analysis"]["direction"] == "declining":
                recommendations.append({
                    "type": "trend_concern",
                    "priority": "high",
                    "insight": f"Approval rate declining by {abs(performance_trends['trend_analysis']['change_percentage'])}%",
                    "action": "Review recent content and consider adjusting topics or posting times"
                })

            # Platform-specific recommendations
            for platform, rec in platform_recommendations.items():
                if rec["status"] == "needs_improvement":
                    recommendations.append({
                        "type": "platform_optimization",
                        "priority": "high",
                        "insight": f"{platform} performance needs improvement",
                        "action": rec["recommendation"]
                    })

            return {
                "top_performing_topics": [
                    {"topic": topic, "approval_rate": data["approval_rate"]}
                    for topic, data in top_topics
                ],
                "platform_recommendations": platform_recommendations,
                "strategic_recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating content recommendations: {e}")
            raise

    def get_comprehensive_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive AI-powered insights combining all analytics data

        Returns:
            Dict containing complete analytics picture with actionable insights
        """
        try:
            # Gather all analytics data
            overview = self.get_overview_stats()
            feedback_patterns = self.get_feedback_patterns()
            performance_trends = self.get_performance_trends(days=30)
            recommendations = self.get_content_recommendations()

            # Calculate overall health score
            total_posts = overview["total_posts"]
            approval_rate = overview["approval_rate"]

            if total_posts < 10:
                health_score = "insufficient_data"
                health_description = "Need more posts to calculate health score"
            elif approval_rate >= 80:
                health_score = "excellent"
                health_description = "Content strategy performing exceptionally well"
            elif approval_rate >= 60:
                health_score = "good"
                health_description = "Content strategy performing well with room for optimization"
            elif approval_rate >= 40:
                health_score = "fair"
                health_description = "Content strategy needs improvement"
            else:
                health_score = "poor"
                health_description = "Content strategy requires significant revision"

            return {
                "health_score": health_score,
                "health_description": health_description,
                "overview": overview,
                "feedback_analysis": feedback_patterns,
                "performance_trends": performance_trends,
                "recommendations": recommendations,
                "next_steps": self._generate_next_steps(recommendations, health_score),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            raise

    def _generate_next_steps(self, recommendations: Dict[str, Any], health_score: str) -> List[str]:
        """
        Generate actionable next steps based on recommendations and health score

        Args:
            recommendations: Content recommendations
            health_score: Overall health score

        Returns:
            List of actionable next steps
        """
        next_steps = []

        # Health score based steps
        if health_score == "excellent":
            next_steps.append("Maintain current content strategy and posting frequency")
            next_steps.append("Consider expanding to additional platforms or topics")
        elif health_score == "good":
            next_steps.append("Continue current strategy with minor optimizations")
            next_steps.append("A/B test different content formats to improve approval rates")
        elif health_score == "fair":
            next_steps.append("Review and revise content strategy based on low-performing topics")
            next_steps.append("Focus on high-performing topics identified in recommendations")
        elif health_score == "poor":
            next_steps.append("Immediate content strategy revision required")
            next_steps.append("Analyze rejected posts to identify common issues")
            next_steps.append("Consider adjusting brand voice or topic focus")

        # Recommendation based steps
        strategic_recs = recommendations.get("strategic_recommendations", [])
        high_priority_recs = [rec for rec in strategic_recs if rec.get("priority") == "high"]

        for rec in high_priority_recs[:3]:  # Top 3 high-priority recommendations
            next_steps.append(rec.get("action", ""))

        return next_steps

    def get_post_performance_details(self, post_id: int) -> Dict[str, Any]:
        """
        Get detailed performance analysis for a specific post

        Args:
            post_id: ID of the post to analyze

        Returns:
            Dict containing detailed post performance metrics
        """
        try:
            post = (
                self.db_session.query(models.Post)
                .filter(models.Post.id == post_id)
                .first()
            )

            if not post:
                return {"error": "Post not found"}

            # Get feedback for this post
            feedback = (
                self.db_session.query(models.PostFeedback)
                .filter(models.PostFeedback.post_id == post_id)
                .all()
            )

            # Calculate performance metrics
            feedback_count = len(feedback)
            approval_count = sum(1 for f in feedback if f.action == "approved")
            rejection_count = sum(1 for f in feedback if f.action == "rejected")
            edit_count = sum(1 for f in feedback if f.action == "edited")

            # Get similar posts for comparison
            similar_posts = (
                self.db_session.query(models.Post)
                .filter(
                    and_(
                        models.Post.topic == post.topic,
                        models.Post.platform == post.platform,
                        models.Post.id != post_id
                    )
                )
                .limit(5)
                .all()
            )

            similar_approval_rate = 0
            if similar_posts:
                approved_similar = sum(1 for p in similar_posts if p.status in ["queued", "published"])
                similar_approval_rate = (approved_similar / len(similar_posts)) * 100

            return {
                "post_id": post.id,
                "platform": post.platform,
                "topic": post.topic,
                "status": post.status,
                "content": post.content,
                "brand_voice": post.brand_voice,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
                "feedback_metrics": {
                    "total_feedback": feedback_count,
                    "approvals": approval_count,
                    "rejections": rejection_count,
                    "edits": edit_count
                },
                "comparison": {
                    "similar_posts_count": len(similar_posts),
                    "similar_approval_rate": round(similar_approval_rate, 2),
                    "performs_better": post.status in ["queued", "published"] and similar_approval_rate > 0
                },
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting post performance details: {e}")
            raise


# Convenience functions for direct usage
def get_analytics_service(db_session: Session) -> AnalyticsService:
    """Factory function to create AnalyticsService instance"""
    return AnalyticsService(db_session)