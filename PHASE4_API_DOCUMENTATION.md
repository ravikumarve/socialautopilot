# Phase 4: Analytics & Feedback Loop - API Documentation

## Overview

Phase 4 implements a comprehensive analytics and feedback loop system that provides AI-powered insights, content performance tracking, and optimization recommendations for social media content.

## Base URL

```
http://localhost:8000/analytics
```

## Authentication

Currently no authentication required (development mode).

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "data": { ... },
  "error": null,
  "timestamp": "2026-04-18T12:00:00Z"
}
```

---

## Endpoints

### 1. Overview Statistics

**Endpoint:** `GET /analytics/overview`

**Description:** Get comprehensive overview statistics for all posts including total counts, approval rates, platform distribution, and recent activity.

**Query Parameters:** None

**Response:**

```json
{
  "total_posts": 150,
  "status_breakdown": {
    "draft": 20,
    "queued": 80,
    "published": 40,
    "rejected": 10
  },
  "platform_distribution": {
    "twitter": 60,
    "linkedin": 50,
    "threads": 40
  },
  "approval_rate": 80.0,
  "recent_posts_7d": 25,
  "generated_at": "2026-04-18T12:00:00Z"
}
```

**Use Cases:**
- Dashboard overview widgets
- Quick performance snapshot
- Platform usage analysis

---

### 2. Feedback Patterns

**Endpoint:** `GET /analytics/feedback-patterns`

**Description:** Analyze feedback patterns to identify content preferences and approval/rejection trends.

**Query Parameters:** None

**Response:**

```json
{
  "total_feedback": 100,
  "action_breakdown": {
    "approved": 70,
    "rejected": 20,
    "edited": 10
  },
  "platform_insights": {
    "twitter": {
      "total_actions": 40,
      "approval_rate": 85.0,
      "breakdown": {
        "approved": 34,
        "rejected": 4,
        "edited": 2
      }
    },
    "linkedin": {
      "total_actions": 35,
      "approval_rate": 75.0,
      "breakdown": {
        "approved": 26,
        "rejected": 6,
        "edited": 3
      }
    }
  },
  "topic_insights": {
    "AI": {
      "total_actions": 25,
      "approval_rate": 90.0,
      "breakdown": {
        "approved": 22,
        "rejected": 2,
        "edited": 1
      }
    }
  },
  "analyzed_at": "2026-04-18T12:00:00Z"
}
```

**Use Cases:**
- Content strategy optimization
- Platform-specific adjustments
- Topic performance analysis

---

### 3. Performance Trends

**Endpoint:** `GET /analytics/performance-trends`

**Description:** Analyze performance trends over time with daily breakdown and trend analysis.

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze (1-365, default: 30)

**Response:**

```json
{
  "period_days": 30,
  "total_posts": 75,
  "daily_breakdown": {
    "2026-04-01": {
      "total": 5,
      "approved": 3,
      "rejected": 2,
      "edited": 0
    },
    "2026-04-02": {
      "total": 4,
      "approved": 4,
      "rejected": 0,
      "edited": 0
    }
  },
  "trend_analysis": {
    "direction": "improving",
    "change_percentage": 15.5,
    "recent_daily_avg": 3.5
  },
  "analyzed_at": "2026-04-18T12:00:00Z"
}
```

**Use Cases:**
- Performance monitoring
- Trend identification
- Progress tracking

---

### 4. Content Recommendations

**Endpoint:** `GET /analytics/recommendations`

**Description:** Generate AI-powered content recommendations based on performance data.

**Query Parameters:** None

**Response:**

```json
{
  "top_performing_topics": [
    {
      "topic": "AI",
      "approval_rate": 90.0
    },
    {
      "topic": "Technology",
      "approval_rate": 85.0
    }
  ],
  "platform_recommendations": {
    "twitter": {
      "status": "strong",
      "recommendation": "Continue current strategy for twitter. High approval rate indicates good content fit."
    },
    "linkedin": {
      "status": "moderate",
      "recommendation": "Consider refining content for linkedin. Moderate approval rate suggests room for improvement."
    }
  },
  "strategic_recommendations": [
    {
      "type": "topic_focus",
      "priority": "high",
      "insight": "Topic 'AI' has 90% approval rate",
      "action": "Generate more content around 'AI' to leverage high approval patterns"
    },
    {
      "type": "trend_positive",
      "priority": "medium",
      "insight": "Approval rate improving by 15.5%",
      "action": "Continue current content strategy and maintain posting frequency"
    }
  ],
  "generated_at": "2026-04-18T12:00:00Z"
}
```

**Use Cases:**
- Content strategy planning
- Topic selection guidance
- Platform optimization

---

### 5. Comprehensive Insights

**Endpoint:** `GET /analytics/insights`

**Description:** Get comprehensive AI-powered insights combining all analytics data with actionable next steps.

**Query Parameters:** None

**Response:**

```json
{
  "health_score": "excellent",
  "health_description": "Content strategy performing exceptionally well",
  "overview": {
    "total_posts": 150,
    "approval_rate": 80.0,
    "platform_distribution": { ... },
    "status_breakdown": { ... }
  },
  "feedback_analysis": {
    "total_feedback": 100,
    "platform_insights": { ... },
    "topic_insights": { ... }
  },
  "performance_trends": {
    "trend_analysis": {
      "direction": "improving",
      "change_percentage": 15.5
    }
  },
  "recommendations": {
    "top_performing_topics": [ ... ],
    "strategic_recommendations": [ ... ]
  },
  "next_steps": [
    "Maintain current content strategy and posting frequency",
    "Consider expanding to additional platforms or topics",
    "Continue using topic 'AI' - high approval rate"
  ],
  "generated_at": "2026-04-18T12:00:00Z"
}
```

**Health Scores:**
- `excellent`: Approval rate ≥ 80%
- `good`: Approval rate ≥ 60%
- `fair`: Approval rate ≥ 40%
- `poor`: Approval rate < 40%
- `insufficient_data`: Less than 10 posts

**Use Cases:**
- Main dashboard view
- Comprehensive performance analysis
- Strategic decision making

---

### 6. Post Performance Details

**Endpoint:** `GET /analytics/post/{post_id}`

**Description:** Get detailed performance analysis for a specific post including feedback metrics and comparison with similar posts.

**Path Parameters:**
- `post_id` (integer, required): ID of the post to analyze

**Response:**

```json
{
  "post_id": 123,
  "platform": "twitter",
  "topic": "AI",
  "status": "queued",
  "content": "Exciting breakthrough in AI innovation! 🚀 #AI #Innovation",
  "brand_voice": "professional",
  "created_at": "2026-04-18T10:00:00Z",
  "scheduled_at": "2026-04-18T14:00:00Z",
  "feedback_metrics": {
    "total_feedback": 5,
    "approvals": 4,
    "rejections": 1,
    "edits": 0
  },
  "comparison": {
    "similar_posts_count": 8,
    "similar_approval_rate": 75.0,
    "performs_better": true
  },
  "analyzed_at": "2026-04-18T12:00:00Z"
}
```

**Use Cases:**
- Individual post analysis
- Content performance comparison
- Detailed feedback review

---

### 7. Platform Analytics

**Endpoint:** `GET /analytics/platform/{platform}`

**Description:** Get platform-specific analytics and insights.

**Path Parameters:**
- `platform` (string, required): Platform name (twitter, linkedin, threads)

**Response:**

```json
{
  "platform": "twitter",
  "total_posts": 60,
  "feedback_insights": {
    "total_actions": 40,
    "approval_rate": 85.0,
    "breakdown": {
      "approved": 34,
      "rejected": 4,
      "edited": 2
    }
  },
  "recommendations": {
    "status": "strong",
    "recommendation": "Continue current strategy for twitter. High approval rate indicates good content fit."
  },
  "analyzed_at": "2026-04-18T12:00:00Z"
}
**Use Cases:**
- Platform-specific optimization
- Comparative platform analysis
- Platform strategy planning

---

### 8. Analytics Health

**Endpoint:** `GET /analytics/health`

**Description:** Get overall analytics health and system status including data availability and readiness.

**Query Parameters:** None

**Response:**

```json
{
  "health_status": "healthy",
  "message": "Analytics system fully operational",
  "recommendation": "Continue regular content generation and feedback collection",
  "data_availability": {
    "total_posts": 150,
    "feedback_count": 100,
    "platforms_active": 3,
    "topics_tracked": 15
  },
  "checked_at": "2026-04-18T12:00:00Z"
}
```

**Health Status:**
- `healthy`: Sufficient data for comprehensive analytics
- `limited_feedback`: Posts available but limited feedback data
- `insufficient_data`: Need more posts to provide meaningful analytics

**Use Cases:**
- System health monitoring
- Data availability checks
- Setup guidance

---

## Feedback Loop Optimization Endpoints

### 9. Feedback Pattern Analysis

**Endpoint:** `GET /analytics/feedback/patterns`

**Description:** Analyze approval/rejection patterns to identify success factors and content characteristics that correlate with approval.

**Query Parameters:** None

**Response:**

```json
{
  "status": "success",
  "approved_count": 70,
  "rejected_count": 20,
  "approved_patterns": {
    "topics": {
      "AI": 25,
      "Technology": 20
    },
    "platforms": {
      "twitter": 30,
      "linkedin": 25
    },
    "brand_voices": {
      "professional": 40,
      "casual": 30
    },
    "content_length": [150, 200, 180, 220, 160],
    "has_emoji": 70.0,
    "has_hashtags": 80.0,
    "has_mentions": 40.0,
    "has_call_to_action": 60.0,
    "avg_content_length": 182.0,
    "min_content_length": 150,
    "max_content_length": 220
  },
  "rejected_patterns": {
    "topics": {
      "Politics": 8,
      "Sports": 7
    },
    "has_emoji": 40.0,
    "has_hashtags": 60.0
  },
  "success_factors": [
    {
      "factor": "topic",
      "value": "AI",
      "approval_rate": 90.0,
      "confidence": "high",
      "recommendation": "Continue using topic 'AI' - high approval rate"
    },
    {
      "factor": "content_characteristic",
      "value": "emoji",
      "approved_percentage": 70.0,
      "rejected_percentage": 40.0,
      "difference": 30.0,
      "recommendation": "Include emoji in posts - correlates with higher approval rates"
    }
  ],
  "analyzed_at": "2026-04-18T12:00:00Z"
}
**Use Cases:**
- Content optimization
- Pattern identification
- Success factor analysis

---

### 10. Optimization Suggestions

**Endpoint:** `GET /analytics/feedback/optimization`

**Description:** Get optimization suggestions for content generation based on feedback patterns and success factors.

**Query Parameters:** None

**Response:**

```json
{
  "status": "success",
  "pattern_analysis": {
    "status": "success",
    "approved_count": 70,
    "rejected_count": 20,
    "success_factors": [ ... ]
  },
  "suggestions": {
    "topic_optimization": [
      {
        "topic": "AI",
        "approval_rate": 90.0,
        "suggestion": "Continue using topic 'AI' - high approval rate"
      }
    ],
    "content_optimization": [
      {
        "characteristic": "emoji",
        "approved_percentage": 70.0,
        "suggestion": "Include emoji in posts - correlates with higher approval rates"
      }
    ],
    "brand_voice_optimization": [
      {
        "brand_voice": "professional",
        "approval_rate": 85.0,
        "suggestion": "Continue using brand voice 'professional' - high approval rate"
      }
    ],
    "platform_optimization": []
  },
  "optimization_strategy": {
    "priority_actions": [
      {
        "action": "Continue using topic 'AI' - high approval rate",
        "impact": "high",
        "factor": "topic",
        "value": "AI"
      }
    ],
    "content_guidelines": [
      {
        "guideline": "Include emoji in posts - correlates with higher approval rates",
        "supporting_data": "70.0% of approved posts include this"
      }
    ],
    "avoidance_list": [
      {
        "item": "Politics",
        "reason": "Rejected 8 times",
        "action": "Avoid or significantly revise content using this topic"
      }
    ],
    "testing_recommendations": [
      {
        "recommendation": "A/B test different content lengths",
        "rationale": "Find optimal content length for each platform"
      },
      {
        "recommendation": "Test different posting times",
        "rationale": "Identify optimal posting schedules for maximum engagement"
      }
    ]
  },
  "generated_at": "2026-04-18T12:00:00Z"
}
**Use Cases:**
- Content strategy optimization
- Generation parameter tuning
- Continuous improvement

---

### 11. Optimization Progress Tracking

**Endpoint:** `GET /analytics/feedback/progress`

**Description:** Track progress of optimization efforts over time with baseline comparison and trend analysis.

**Query Parameters:** None

**Response:**

```json
{
  "status": "success",
  "recent_period": {
    "days": 30,
    "total_posts": 45,
    "approved_posts": 38,
    "approval_rate": 84.44
  },
  "baseline_period": {
    "days": 30,
    "total_posts": 30,
    "approved_posts": 20,
    "approval_rate": 66.67
  },
  "optimization_progress": {
    "direction": "improving",
    "improvement_percentage": 17.77,
    "trend": "positive"
  },
  "tracked_at": "2026-04-18T12:00:00Z"
}
**Trend Analysis:**
- `improving`: Recent approval rate higher than baseline
- `declining`: Recent approval rate lower than baseline
- `insufficient_baseline`: Not enough baseline data

**Trend Classification:**
- `positive`: Improvement > 5%
- `stable`: Improvement between -5% and 5%
- `negative`: Improvement < -5%

**Use Cases:**
- Optimization effectiveness tracking
- ROI measurement
- Progress reporting

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting implemented (development mode).

---

## Data Freshness

- Analytics data is calculated in real-time
- No caching implemented for development
- Consider implementing caching for production use

---

## Best Practices

1. **Call Frequency**: For dashboard applications, call comprehensive endpoints every 5-10 minutes
2. **Data Volume**: Use specific endpoints (e.g., `/platform/{platform}`) when you need focused data
3. **Error Handling**: Always implement proper error handling and retry logic
4. **Trend Analysis**: Use at least 30 days of data for meaningful trend analysis
5. **Health Checks**: Call `/health` endpoint before relying on analytics data

---

## Integration Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/analytics"

# Get comprehensive insights
response = requests.get(f"{BASE_URL}/insights")
data = response.json()

print(f"Health Score: {data['health_score']}")
print(f"Approval Rate: {data['overview']['approval_rate']}%")

# Get platform-specific analytics
platform_response = requests.get(f"{BASE_URL}/platform/twitter")
platform_data = platform_response.json()

print(f"Twitter Approval Rate: {platform_data['feedback_insights']['approval_rate']}%")
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000/analytics";

// Get comprehensive insights
async function getInsights() {
  const response = await fetch(`${BASE_URL}/insights`);
  const data = await response.json();

  console.log(`Health Score: ${data.health_score}`);
  console.log(`Approval Rate: ${data.overview.approval_rate}%`);

  return data;
}

// Get optimization suggestions
async function getOptimizationSuggestions() {
  const response = await fetch(`${BASE_URL}/feedback/optimization`);
  const data = await response.json();

  console.log("Priority Actions:", data.optimization_strategy.priority_actions);

  return data;
}
```

---

## Support

For issues or questions:
- GitHub Issues: [https://github.com/ravikumarve/socialautopilot/issues](https://github.com/ravikumarve/socialautopilot/issues)
- Documentation: [README.md](../README.md)