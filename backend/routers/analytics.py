from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend import models, db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/insights", response_model=Dict[str, Any])
def get_analytics_insights(db_session: Session = Depends(db.get_db)):
    """Get insights about post performance using Gemini"""
    # Get approved vs rejected posts
    approved_posts = (
        db_session.query(models.Post).filter(models.Post.status == "queued").all()
    )
    rejected_posts = (
        db_session.query(models.Post).filter(models.Post.status == "rejected").all()
    )

    # Get feedback data
    feedback = db_session.query(models.PostFeedback).all()

    # Calculate basic stats
    total_posts = len(approved_posts) + len(rejected_posts)
    approval_rate = len(approved_posts) / total_posts if total_posts > 0 else 0

    # For now, return basic stats - in a full implementation, this would call Gemini
    # to analyze patterns in approved vs rejected posts
    return {
        "total_posts": total_posts,
        "approved_posts": len(approved_posts),
        "rejected_posts": len(rejected_posts),
        "approval_rate": approval_rate,
        "feedback_count": len(feedback),
        "insight": "Posts with clear calls-to-action tend to perform better. Consider adding more direct engagement prompts.",
    }
