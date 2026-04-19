"""
Export Router for Social Autopilot

Provides data export endpoints for posts, analytics, and scheduling data
in multiple formats (CSV, JSON). Designed for integration with external
scheduling tools like Buffer and Hootsuite.

Key Features:
- Posts export with filtering (status, platform, date range)
- Analytics data export with configurable time windows
- Schedule export in Buffer/Hootsuite-compatible CSV format
- Available formats discovery endpoint
"""

import csv
import io
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend import db, models
from backend.services.analytics_service import get_analytics_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Constants — no magic strings
# ---------------------------------------------------------------------------
EXPORT_FORMAT_CSV: str = "csv"
EXPORT_FORMAT_JSON: str = "json"
VALID_EXPORT_FORMATS: List[str] = [EXPORT_FORMAT_JSON, EXPORT_FORMAT_CSV]

SCHEDULE_COMPATIBLE_STATUSES: List[str] = ["queued", "draft"]

DEFAULT_SCHEDULE_DAYS_AHEAD: int = 7
MAX_SCHEDULE_DAYS_AHEAD: int = 30
DEFAULT_ANALYTICS_DAYS: int = 30
MIN_ANALYTICS_DAYS: int = 1
MAX_ANALYTICS_DAYS: int = 365

CSV_FILENAME_POSTS: str = "social_autopilot_posts.csv"
CSV_FILENAME_SCHEDULE: str = "social_autopilot_schedule.csv"

POST_CSV_COLUMNS: List[str] = [
    "id",
    "platform",
    "content",
    "status",
    "brand_voice",
    "topic",
    "created_at",
    "updated_at",
    "scheduled_at",
]

SCHEDULE_CSV_COLUMNS: List[str] = [
    "date",
    "time",
    "content",
    "platform",
    "status",
]

HTTP_400_BAD_REQUEST: int = 400
HTTP_500_INTERNAL_ERROR: int = 500

CONTENT_TYPE_CSV: str = "text/csv"
CONTENT_DISPOSITION_ATTACHMENT: str = "attachment; filename={filename}"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _post_to_dict(post: models.Post) -> Dict[str, Any]:
    """Convert a Post ORM object to a plain dict suitable for serialisation.

    All datetime fields are rendered as ISO-8601 strings so that CSV and JSON
    consumers receive a consistent, parseable representation.

    Args:
        post: SQLAlchemy Post model instance.

    Returns:
        Dictionary with all Post field names as keys.
    """
    return {
        "id": post.id,
        "platform": post.platform,
        "content": post.content,
        "status": post.status,
        "brand_voice": post.brand_voice,
        "topic": post.topic,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
    }


def _build_posts_query(
    db_session: Session,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> List[models.Post]:
    """Build and execute a filtered query against the posts table.

    Args:
        db_session: Active SQLAlchemy session.
        status: Optional status filter (e.g. ``"draft"``, ``"queued"``).
        platform: Optional platform filter (e.g. ``"twitter"``, ``"linkedin"``).
        date_from: Optional lower bound for ``created_at`` (inclusive).
        date_to: Optional upper bound for ``created_at`` (inclusive).

    Returns:
        List of Post model instances matching all provided filters.
    """
    query = db_session.query(models.Post)

    if status is not None:
        query = query.filter(models.Post.status == status)

    if platform is not None:
        query = query.filter(models.Post.platform == platform)

    if date_from is not None:
        query = query.filter(models.Post.created_at >= date_from)

    if date_to is not None:
        query = query.filter(models.Post.created_at <= date_to)

    return query.order_by(models.Post.created_at.desc()).all()


def _posts_to_csv_buffer(posts: List[models.Post]) -> io.StringIO:
    """Serialise a list of Post objects into a CSV-formatted StringIO buffer.

    Args:
        posts: List of Post model instances.

    Returns:
        StringIO buffer containing the CSV data, with cursor at position 0.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=POST_CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()

    for post in posts:
        row = _post_to_dict(post)
        writer.writerow(row)

    buffer.seek(0)
    return buffer


def _schedule_row(post: models.Post) -> Dict[str, str]:
    """Convert a Post into a Buffer/Hootsuite-compatible schedule row.

    The ``scheduled_at`` datetime is split into separate ``date`` and ``time``
    columns so that external scheduling tools can parse them independently.

    Args:
        post: Post model instance with a non-null ``scheduled_at``.

    Returns:
        Dictionary with keys matching :data:`SCHEDULE_CSV_COLUMNS`.
    """
    scheduled_date = ""
    scheduled_time = ""
    if post.scheduled_at:
        scheduled_date = post.scheduled_at.strftime("%Y-%m-%d")
        scheduled_time = post.scheduled_at.strftime("%H:%M")

    return {
        "date": scheduled_date,
        "time": scheduled_time,
        "content": post.content or "",
        "platform": post.platform or "",
        "status": post.status or "",
    }


def _schedule_to_csv_buffer(posts: List[models.Post]) -> io.StringIO:
    """Serialise a list of scheduled Post objects into a schedule CSV buffer.

    Args:
        posts: List of Post model instances with ``scheduled_at`` set.

    Returns:
        StringIO buffer containing the schedule CSV data, cursor at position 0.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=SCHEDULE_CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()

    for post in posts:
        writer.writerow(_schedule_row(post))

    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/posts")
def export_posts(
    format: str = Query(
        EXPORT_FORMAT_JSON,
        description="Export format: 'csv' or 'json'",
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by post status (draft, queued, published, rejected)",
    ),
    platform: Optional[str] = Query(
        None,
        description="Filter by platform (twitter, linkedin, threads)",
    ),
    date_from: Optional[datetime] = Query(
        None,
        description="Filter posts created on or after this ISO date",
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="Filter posts created on or before this ISO date",
    ),
    db_session: Session = Depends(db.get_db),
):
    """Export posts as CSV or JSON with optional filtering.

    Supports filtering by status, platform, and date range. CSV responses
    are streamed as a downloadable attachment; JSON responses include
    metadata (export timestamp, total count, applied filters).

    Args:
        format: Output format — ``"json"`` (default) or ``"csv"``.
        status: Optional status filter.
        platform: Optional platform filter.
        date_from: Optional inclusive lower bound for ``created_at``.
        date_to: Optional inclusive upper bound for ``created_at``.
        db_session: Injected database session.

    Returns:
        JSON dict with metadata + post data, **or** a ``StreamingResponse``
        with ``text/csv`` content type when ``format=csv``.

    Raises:
        HTTPException 400: When an unsupported format is requested.
        HTTPException 500: When the database query or serialisation fails.
    """
    try:
        # Validate format early
        if format not in VALID_EXPORT_FORMATS:
            logger.warning("Unsupported export format requested: %s", format)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format '{format}'. Use '{EXPORT_FORMAT_JSON}' or '{EXPORT_FORMAT_CSV}'.",
            )

        logger.info(
            "Exporting posts — format=%s, status=%s, platform=%s, date_from=%s, date_to=%s",
            format,
            status,
            platform,
            date_from,
            date_to,
        )

        posts = _build_posts_query(
            db_session,
            status=status,
            platform=platform,
            date_from=date_from,
            date_to=date_to,
        )

        logger.info("Exported %d posts", len(posts))

        if format == EXPORT_FORMAT_CSV:
            buffer = _posts_to_csv_buffer(posts)
            return StreamingResponse(
                buffer,
                media_type=CONTENT_TYPE_CSV,
                headers={
                    "Content-Disposition": CONTENT_DISPOSITION_ATTACHMENT.format(
                        filename=CSV_FILENAME_POSTS,
                    ),
                },
            )

        # JSON format
        filters_applied: Dict[str, Any] = {}
        if status is not None:
            filters_applied["status"] = status
        if platform is not None:
            filters_applied["platform"] = platform
        if date_from is not None:
            filters_applied["date_from"] = date_from.isoformat()
        if date_to is not None:
            filters_applied["date_to"] = date_to.isoformat()

        return {
            "exported_at": datetime.now().isoformat(),
            "total_count": len(posts),
            "filters_applied": filters_applied,
            "posts": [_post_to_dict(p) for p in posts],
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to export posts: %s", exc)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_ERROR,
            detail=f"Export failed: {exc}",
        )


@router.get("/analytics")
def export_analytics(
    days: int = Query(
        DEFAULT_ANALYTICS_DAYS,
        ge=MIN_ANALYTICS_DAYS,
        le=MAX_ANALYTICS_DAYS,
        description="Number of days to include in analytics export (1-365)",
    ),
    db_session: Session = Depends(db.get_db),
) -> Dict[str, Any]:
    """Export analytics data as a single JSON payload.

    Combines overview statistics, feedback patterns, and performance trends
    into one response, scoped to the requested time window.

    Args:
        days: Lookback window in days (1–365, default 30).
        db_session: Injected database session.

    Returns:
        Dictionary containing:
        - **overview**: Total posts, status breakdown, platform distribution, approval rate.
        - **feedback_patterns**: Action breakdown, platform insights, topic insights.
        - **performance_trends**: Daily breakdown, trend direction, change percentage.

    Raises:
        HTTPException 500: When the analytics service raises an error.
    """
    try:
        logger.info("Exporting analytics data for last %d days", days)

        analytics_service = get_analytics_service(db_session)

        overview = analytics_service.get_overview_stats()
        feedback_patterns = analytics_service.get_feedback_patterns()
        performance_trends = analytics_service.get_performance_trends(days=days)

        return {
            "exported_at": datetime.now().isoformat(),
            "period_days": days,
            "overview": overview,
            "feedback_patterns": feedback_patterns,
            "performance_trends": performance_trends,
        }

    except Exception as exc:
        logger.error("Failed to export analytics: %s", exc)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_ERROR,
            detail=f"Analytics export failed: {exc}",
        )


@router.get("/schedule")
def export_schedule(
    platform: Optional[str] = Query(
        None,
        description="Filter by platform (twitter, linkedin, threads)",
    ),
    days_ahead: int = Query(
        DEFAULT_SCHEDULE_DAYS_AHEAD,
        ge=1,
        le=MAX_SCHEDULE_DAYS_AHEAD,
        description="Number of days ahead to include (1-30, default 7)",
    ),
    db_session: Session = Depends(db.get_db),
):
    """Export scheduled posts in a Buffer/Hootsuite-compatible CSV format.

    Only posts with status ``"queued"`` or ``"draft"`` that have a
    ``scheduled_at`` date within the requested horizon are included. The
    CSV columns — ``date,time,content,platform,status`` — are specifically
    chosen for import compatibility with third-party scheduling tools.

    Args:
        platform: Optional platform filter.
        days_ahead: How many days into the future to include (1–30).
        db_session: Injected database session.

    Returns:
        ``StreamingResponse`` with ``text/csv`` content type and
        ``Content-Disposition: attachment`` header.

    Raises:
        HTTPException 500: When the query or CSV generation fails.
    """
    try:
        logger.info(
            "Exporting schedule — platform=%s, days_ahead=%d",
            platform,
            days_ahead,
        )

        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        query = (
            db_session.query(models.Post)
            .filter(
                models.Post.status.in_(SCHEDULE_COMPATIBLE_STATUSES),
                models.Post.scheduled_at.isnot(None),
                models.Post.scheduled_at <= cutoff_date,
            )
            .order_by(models.Post.scheduled_at.asc())
        )

        if platform is not None:
            query = query.filter(models.Post.platform == platform)

        posts = query.all()
        logger.info("Exported %d scheduled posts", len(posts))

        buffer = _schedule_to_csv_buffer(posts)

        return StreamingResponse(
            buffer,
            media_type=CONTENT_TYPE_CSV,
            headers={
                "Content-Disposition": CONTENT_DISPOSITION_ATTACHMENT.format(
                    filename=CSV_FILENAME_SCHEDULE,
                ),
            },
        )

    except Exception as exc:
        logger.error("Failed to export schedule: %s", exc)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_ERROR,
            detail=f"Schedule export failed: {exc}",
        )


@router.get("/formats")
def list_export_formats() -> Dict[str, Any]:
    """List all available export formats and their descriptions.

    Returns:
        Dictionary keyed by endpoint path, each containing a ``formats``
        list with name, media type, and human-readable description.

    Example::

        {
            "formats": {
                "/export/posts": [
                    {"name": "json", "media_type": "application/json", "description": "..."},
                    {"name": "csv",  "media_type": "text/csv",         "description": "..."}
                ],
                "/export/analytics": [...],
                "/export/schedule": [...]
            }
        }
    """
    logger.info("Listing available export formats")

    return {
        "formats": {
            "/export/posts": [
                {
                    "name": EXPORT_FORMAT_JSON,
                    "media_type": "application/json",
                    "description": "Standard JSON response with metadata (export timestamp, total count, filters applied) and full post data.",
                },
                {
                    "name": EXPORT_FORMAT_CSV,
                    "media_type": CONTENT_TYPE_CSV,
                    "description": "Downloadable CSV file with all post fields. Compatible with spreadsheets and data pipelines.",
                },
            ],
            "/export/analytics": [
                {
                    "name": EXPORT_FORMAT_JSON,
                    "media_type": "application/json",
                    "description": "Combined analytics payload with overview stats, feedback patterns, and performance trends.",
                },
            ],
            "/export/schedule": [
                {
                    "name": EXPORT_FORMAT_CSV,
                    "media_type": CONTENT_TYPE_CSV,
                    "description": "Buffer/Hootsuite-compatible CSV with columns: date, time, content, platform, status. Only includes queued/draft posts with a scheduled date.",
                },
            ],
        },
    }
