"""
Feedback Loop Optimization Service

This service implements a feedback loop system that:
- Analyzes approval/rejection patterns
- Identifies content characteristics that lead to approvals
- Provides optimization suggestions for content generation
- Implements learning from user feedback

Key Features:
- Pattern recognition from feedback data
- Content optimization recommendations
- Automatic adjustment of generation parameters
- Continuous improvement of content quality
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend import models
import logging

logger = logging.getLogger(__name__)


class FeedbackLoopOptimizer:
    """Feedback loop optimization system for continuous content improvement"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def analyze_approval_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in approved vs rejected posts to identify success factors

        Returns:
            Dict containing pattern analysis and success indicators
        """
        try:
            # Get approved and rejected posts
            approved_posts = (
                self.db_session.query(models.Post)
                .filter(models.Post.status.in_(["queued", "published"]))
                .all()
            )

            rejected_posts = (
                self.db_session.query(models.Post)
                .filter(models.Post.status == "rejected")
                .all()
            )

            if not approved_posts and not rejected_posts:
                return {
                    "status": "insufficient_data",
                    "message": "Need both approved and rejected posts for pattern analysis"
                }

            # Analyze content characteristics
            approved_patterns = self._extract_content_patterns(approved_posts)
            rejected_patterns = self._extract_content_patterns(rejected_posts)

            # Identify success factors
            success_factors = self._identify_success_factors(
                approved_patterns,
                rejected_patterns
            )

            return {
                "status": "success",
                "approved_count": len(approved_posts),
                "rejected_count": len(rejected_posts),
                "approved_patterns": approved_patterns,
                "rejected_patterns": rejected_patterns,
                "success_factors": success_factors,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing approval patterns: {e}")
            raise

    def _extract_content_patterns(self, posts: List[models.Post]) -> Dict[str, Any]:
        """
        Extract content patterns from a list of posts

        Args:
            posts: List of posts to analyze

        Returns:
            Dict containing content patterns and characteristics
        """
        if not posts:
            return {}

        patterns = {
            "topics": {},
            "platforms": {},
            "brand_voices": {},
            "content_length": [],
            "has_emoji": 0,
            "has_hashtags": 0,
            "has_mentions": 0,
            "has_call_to_action": 0
        }

        for post in posts:
            # Topic patterns
            if post.topic:
                patterns["topics"][post.topic] = patterns["topics"].get(post.topic, 0) + 1

            # Platform patterns
            if post.platform:
                patterns["platforms"][post.platform] = patterns["platforms"].get(post.platform, 0) + 1

            # Brand voice patterns
            if post.brand_voice:
                patterns["brand_voices"][post.brand_voice] = patterns["brand_voices"].get(post.brand_voice, 0) + 1

            # Content characteristics
            if post.content:
                content = post.content.lower()
                patterns["content_length"].append(len(post.content))

                if any(c in post.content for c in "😀😃😄😁😆😅🤣😂🙂😉😊😇"):
                    patterns["has_emoji"] += 1

                if "#" in post.content:
                    patterns["has_hashtags"] += 1

                if "@" in post.content:
                    patterns["has_mentions"] += 1

                # Call to action detection
                cta_keywords = ["check out", "learn more", "discover", "find out", "click", "visit", "read"]
                if any(keyword in content for keyword in cta_keywords):
                    patterns["has_call_to_action"] += 1

        # Calculate percentages
        total_posts = len(posts)
        if total_posts > 0:
            patterns["has_emoji"] = round((patterns["has_emoji"] / total_posts) * 100, 2)
            patterns["has_hashtags"] = round((patterns["has_hashtags"] / total_posts) * 100, 2)
            patterns["has_mentions"] = round((patterns["has_mentions"] / total_posts) * 100, 2)
            patterns["has_call_to_action"] = round((patterns["has_call_to_action"] / total_posts) * 100, 2)

            # Average content length
            if patterns["content_length"]:
                patterns["avg_content_length"] = round(sum(patterns["content_length"]) / len(patterns["content_length"]), 2)
                patterns["min_content_length"] = min(patterns["content_length"])
                patterns["max_content_length"] = max(patterns["content_length"])

        return patterns

    def _identify_success_factors(
        self,
        approved_patterns: Dict[str, Any],
        rejected_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify factors that contribute to post approval

        Args:
            approved_patterns: Patterns from approved posts
            rejected_patterns: Patterns from rejected posts

        Returns:
            List of success factors with confidence scores
        """
        success_factors = []

        if not approved_patterns or not rejected_patterns:
            return success_factors

        # Compare topic performance
        approved_topics = approved_patterns.get("topics", {})
        rejected_topics = rejected_patterns.get("topics", {})

        for topic, approved_count in approved_topics.items():
            rejected_count = rejected_topics.get(topic, 0)
            total = approved_count + rejected_count

            if total > 0:
                approval_rate = (approved_count / total) * 100
                if approval_rate > 70:
                    success_factors.append({
                        "factor": "topic",
                        "value": topic,
                        "approval_rate": round(approval_rate, 2),
                        "confidence": "high" if total >= 5 else "medium",
                        "recommendation": f"Continue using topic '{topic}' - high approval rate"
                    })

        # Compare content characteristics
        characteristics = [
            ("emoji", "has_emoji"),
            ("hashtags", "has_hashtags"),
            ("mentions", "has_mentions"),
            ("call_to_action", "has_call_to_action")
        ]

        for char_name, char_key in characteristics:
            approved_pct = approved_patterns.get(char_key, 0)
            rejected_pct = rejected_patterns.get(char_key, 0)

            if approved_pct > rejected_pct + 20:  # Significant difference
                success_factors.append({
                    "factor": "content_characteristic",
                    "value": char_name,
                    "approved_percentage": approved_pct,
                    "rejected_percentage": rejected_pct,
                    "difference": round(approved_pct - rejected_pct, 2),
                    "recommendation": f"Include {char_name} in posts - correlates with higher approval rates"
                })

        # Compare brand voice performance
        approved_voices = approved_patterns.get("brand_voices", {})
        rejected_voices = rejected_patterns.get("brand_voices", {})

        for voice, approved_count in approved_voices.items():
            rejected_count = rejected_voices.get(voice, 0)
            total = approved_count + rejected_count

            if total > 0:
                approval_rate = (approved_count / total) * 100
                if approval_rate > 70:
                    success_factors.append({
                        "factor": "brand_voice",
                        "value": voice,
                        "approval_rate": round(approval_rate, 2),
                        "confidence": "high" if total >= 5 else "medium",
                        "recommendation": f"Continue using brand voice '{voice}' - high approval rate"
                    })

        # Sort by approval rate
        success_factors.sort(
            key=lambda x: x.get("approval_rate", 0),
            reverse=True
        )

        return success_factors[:10]  # Return top 10 factors

    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """
        Get optimization suggestions for content generation

        Returns:
            Dict containing actionable optimization suggestions
        """
        try:
            # Analyze approval patterns
            pattern_analysis = self.analyze_approval_patterns()

            if pattern_analysis.get("status") == "insufficient_data":
                return {
                    "status": "insufficient_data",
                    "message": "Need more data for optimization suggestions",
                    "recommendation": "Generate more posts and provide feedback to enable optimization"
                }

            success_factors = pattern_analysis.get("success_factors", [])

            # Generate optimization suggestions
            suggestions = {
                "topic_optimization": [],
                "content_optimization": [],
                "brand_voice_optimization": [],
                "platform_optimization": []
            }

            for factor in success_factors:
                factor_type = factor.get("factor")
                recommendation = factor.get("recommendation", "")

                if factor_type == "topic":
                    suggestions["topic_optimization"].append({
                        "topic": factor.get("value"),
                        "approval_rate": factor.get("approval_rate"),
                        "suggestion": recommendation
                    })
                elif factor_type == "content_characteristic":
                    suggestions["content_optimization"].append({
                        "characteristic": factor.get("value"),
                        "approved_percentage": factor.get("approved_percentage"),
                        "suggestion": recommendation
                    })
                elif factor_type == "brand_voice":
                    suggestions["brand_voice_optimization"].append({
                        "brand_voice": factor.get("value"),
                        "approval_rate": factor.get("approval_rate"),
                        "suggestion": recommendation
                    })

            # Generate overall optimization strategy
            optimization_strategy = self._generate_optimization_strategy(
                pattern_analysis,
                suggestions
            )

            return {
                "status": "success",
                "pattern_analysis": pattern_analysis,
                "suggestions": suggestions,
                "optimization_strategy": optimization_strategy,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {e}")
            raise

    def _generate_optimization_strategy(
        self,
        pattern_analysis: Dict[str, Any],
        suggestions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive optimization strategy

        Args:
            pattern_analysis: Pattern analysis results
            suggestions: Optimization suggestions

        Returns:
            Dict containing optimization strategy
        """
        strategy = {
            "priority_actions": [],
            "content_guidelines": [],
            "avoidance_list": [],
            "testing_recommendations": []
        }

        # Priority actions based on success factors
        success_factors = pattern_analysis.get("success_factors", [])

        for factor in success_factors[:5]:  # Top 5 factors
            if factor.get("confidence") == "high":
                strategy["priority_actions"].append({
                    "action": factor.get("recommendation"),
                    "impact": "high",
                    "factor": factor.get("factor"),
                    "value": factor.get("value")
                })

        # Content guidelines
        if suggestions["content_optimization"]:
            for opt in suggestions["content_optimization"]:
                strategy["content_guidelines"].append({
                    "guideline": opt["suggestion"],
                    "supporting_data": f"{opt['approved_percentage']}% of approved posts include this"
                })

        # Avoidance list (from rejected patterns)
        rejected_patterns = pattern_analysis.get("rejected_patterns", {})
        rejected_topics = rejected_patterns.get("topics", {})

        for topic, count in rejected_topics.items():
            if count >= 3:  # Topics rejected 3+ times
                strategy["avoidance_list"].append({
                    "item": topic,
                    "reason": f"Rejected {count} times",
                    "action": "Avoid or significantly revise content using this topic"
                })

        # Testing recommendations
        strategy["testing_recommendations"].append({
            "recommendation": "A/B test different content lengths",
            "rationale": "Find optimal content length for each platform"
        })

        strategy["testing_recommendations"].append({
            "recommendation": "Test different posting times",
            "rationale": "Identify optimal posting schedules for maximum engagement"
        })

        return strategy

    def track_optimization_progress(self) -> Dict[str, Any]:
        """
        Track progress of optimization efforts over time

        Returns:
            Dict containing optimization progress metrics
        """
        try:
            # Get recent posts (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)

            recent_posts = (
                self.db_session.query(models.Post)
                .filter(models.Post.created_at >= thirty_days_ago)
                .all()
            )

            if not recent_posts:
                return {
                    "status": "insufficient_data",
                    "message": "No recent posts to track optimization progress"
                }

            # Calculate approval rate for recent posts
            approved_recent = sum(1 for p in recent_posts if p.status in ["queued", "published"])
            recent_approval_rate = (approved_recent / len(recent_posts)) * 100

            # Get older posts for comparison (30-60 days ago)
            sixty_days_ago = datetime.now() - timedelta(days=60)

            older_posts = (
                self.db_session.query(models.Post)
                .filter(
                    and_(
                        models.Post.created_at >= sixty_days_ago,
                        models.Post.created_at < thirty_days_ago
                    )
                )
                .all()
            )

            if older_posts:
                approved_older = sum(1 for p in older_posts if p.status in ["queued", "published"])
                older_approval_rate = (approved_older / len(older_posts)) * 100

                # Calculate improvement
                improvement = recent_approval_rate - older_approval_rate
                improvement_direction = "improving" if improvement > 0 else "declining"
            else:
                older_approval_rate = 0
                improvement = 0
                improvement_direction = "insufficient_baseline"

            return {
                "status": "success",
                "recent_period": {
                    "days": 30,
                    "total_posts": len(recent_posts),
                    "approved_posts": approved_recent,
                    "approval_rate": round(recent_approval_rate, 2)
                },
                "baseline_period": {
                    "days": 30,
                    "total_posts": len(older_posts),
                    "approved_posts": approved_older if older_posts else 0,
                    "approval_rate": round(older_approval_rate, 2) if older_posts else 0
                },
                "optimization_progress": {
                    "direction": improvement_direction,
                    "improvement_percentage": round(improvement, 2),
                    "trend": "positive" if improvement > 5 else "stable" if abs(improvement) <= 5 else "negative"
                },
                "tracked_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error tracking optimization progress: {e}")
            raise


# Convenience functions for direct usage
def get_feedback_optimizer(db_session: Session) -> FeedbackLoopOptimizer:
    """Factory function to create FeedbackLoopOptimizer instance"""
    return FeedbackLoopOptimizer(db_session)