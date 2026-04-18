from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend import models, db
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class BulkGenerateRequest(BaseModel):
    platform: str
    brand_voice: str
    post_history: List[str] = []  # last 30 posts
    days_ahead: int = 7


class GeneratedPost(BaseModel):
    platform: str
    content: str
    brand_voice: str
    topic: str  # We'll use the first few words as topic for simplicity
    status: str = "draft"


@router.post("/bulk", response_model=List[GeneratedPost])
async def bulk_generate_posts(
    request: BulkGenerateRequest, db_session: Session = Depends(db.get_db)
):
    """
    Generate multiple posts in bulk using Gemini 2.5 Pro with 1M token context
    """
    try:
        # In a full implementation, we would:
        # 1. Use the ai_service to generate posts with the entire context
        # 2. For now, we'll create placeholder posts

        generated_posts = []
        for day in range(request.days_ahead):
            # Placeholder: In reality, we'd call ai_service.generate_post with a topic
            # that might be derived from trends or user input
            topic = f"Topic for day {day + 1}"
            content = (
                f"This is a generated post for {request.platform} on day {day + 1}. "
            )
            content += f"Brand voice: {request.brand_voice}. "
            if request.post_history:
                content += f"Considering history: {request.post_history[0][:50]}..."

            post_data = {
                "platform": request.platform,
                "content": content,
                "brand_voice": request.brand_voice,
                "topic": topic,
                "status": "draft",
            }

            db_post = models.Post(**post_data)
            db_session.add(db_post)
            generated_posts.append(GeneratedPost(**post_data))

        db_session.commit()
        return generated_posts

    except Exception as e:
        logger.error(f"Bulk generation failed: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Bulk generation failed")
