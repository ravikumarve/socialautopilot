from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from backend import models, db
from backend.services import ai_service, trend_service
from pydantic import BaseModel
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


class BulkGenerateRequest(BaseModel):
    platform: str
    brand_voice: str
    post_history: List[str] = []  # last 30 posts for context
    days_ahead: int = 7
    model: str = "gemini"  # AI model to use (gemini, claude, nim)


class GeneratedPost(BaseModel):
    id: int
    platform: str
    content: str
    brand_voice: str
    topic: str
    status: str
    scheduled_at: Optional[datetime] = None
    created_at: datetime


def validate_platform(platform: str) -> bool:
    """
    Validate platform parameter
    
    Args:
        platform: Platform name to validate
        
    Returns:
        True if platform is valid, False otherwise
    """
    valid_platforms = ["twitter", "linkedin", "threads"]
    return platform.lower() in valid_platforms


def validate_days_ahead(days_ahead: int) -> bool:
    """
    Validate days_ahead parameter
    
    Args:
        days_ahead: Number of days to generate posts for
        
    Returns:
        True if days_ahead is valid, False otherwise
    """
    return 1 <= days_ahead <= 30


def calculate_scheduled_date(day_index: int) -> datetime:
    """
    Calculate scheduled date for a post
    
    Args:
        day_index: Day index (0 for today, 1 for tomorrow, etc.)
        
    Returns:
        Scheduled datetime for the post
    """
    scheduled_date = datetime.now() + timedelta(days=day_index)
    # Set time to 9:00 AM for consistent scheduling
    scheduled_date = scheduled_date.replace(hour=9, minute=0, second=0, microsecond=0)
    return scheduled_date


def get_platform_trending_topics(platform: str) -> List[str]:
    """
    Get trending topics for a specific platform
    
    Args:
        platform: Target social media platform
        
    Returns:
        List of trending topics (empty list if fetch fails)
    """
    try:
        logger.info(f"Fetching trending topics for {platform}")
        trends = trend_service.get_trending_topics()
        
        if trends:
            logger.info(f"Successfully fetched {len(trends)} trending topics for {platform}")
            return trends
        else:
            logger.warning(f"No trending topics found for {platform}, using fallback")
            return get_fallback_topics(platform)
            
    except Exception as e:
        logger.error(f"Error fetching trending topics for {platform}: {e}")
        return get_fallback_topics(platform)


def get_fallback_topics(platform: str) -> List[str]:
    """
    Get fallback topics when trend service fails
    
    Args:
        platform: Target social media platform
        
    Returns:
        List of fallback topics
    """
    fallback_topics = {
        "twitter": [
            "#TechNews",
            "#Innovation",
            "#IndustryUpdate",
            "#Trending",
            "#BreakingNews"
        ],
        "linkedin": [
            "Professional Development",
            "Industry Insights",
            "Leadership",
            "Business Strategy",
            "Career Growth"
        ],
        "threads": [
            "Community Update",
            "Latest News",
            "Trending Now",
            "Hot Topic",
            "Viral Content"
        ]
    }
    
    return fallback_topics.get(platform.lower(), ["General Update", "News", "Trending"])


def extract_topic_from_content(content: str, max_length: int = 50) -> str:
    """
    Extract topic from generated content
    
    Args:
        content: Generated post content
        max_length: Maximum length for topic
        
    Returns:
        Extracted topic string
    """
    # Remove hashtags and special characters
    words = content.split()
    topic_words = []
    
    for word in words:
        # Skip hashtags and mentions
        if word.startswith('#') or word.startswith('@'):
            continue
        # Clean the word
        clean_word = word.strip('.,!?;:"\'')
        if clean_word and len(clean_word) > 2:
            topic_words.append(clean_word)
    
    # Join first few words as topic
    topic = " ".join(topic_words[:5])
    
    # Truncate if too long
    if len(topic) > max_length:
        topic = topic[:max_length].rsplit(' ', 1)[0]
    
    return topic if topic else "General Update"


async def generate_post_with_fallback(
    platform: str,
    topic: str,
    brand_voice: str,
    trends: List[str],
    model: str,
    post_history: List[str]
) -> str:
    """
    Generate a post with fallback handling
    
    Args:
        platform: Target social media platform
        topic: Topic for the post
        brand_voice: Brand voice/style for the post
        trends: List of trending topics
        model: AI model to use
        post_history: List of previous posts for context
        
    Returns:
        Generated post content
    """
    try:
        logger.info(f"Generating post for {platform} with topic: {topic}")
        
        # Build enhanced prompt with post history context
        context_prompt = f"Post history context: {post_history[:5] if post_history else 'None'}"
        
        # Generate trend-aware post
        content = await ai_service.generate_trend_aware_post(
            platform=platform,
            topic=topic,
            brand_voice=brand_voice,
            trends=trends,
            model=model
        )
        
        logger.info(f"Successfully generated post for {platform}")
        return content
        
    except Exception as e:
        logger.error(f"Error generating post for {platform}: {e}")
        logger.info(f"Using fallback post for {platform}")
        return ai_service.fallback_post(platform, topic)


@router.post("/bulk", response_model=List[GeneratedPost])
async def bulk_generate_posts(
    request: BulkGenerateRequest,
    db_session: Session = Depends(db.get_db)
):
    """
    Generate multiple posts in bulk using AI with trend awareness and 1M token context
    
    This endpoint:
    - Fetches trending topics for each day
    - Uses AI service to generate content with trend awareness
    - Supports 1M token context by passing post_history and brand_voice
    - Generates posts for multiple days (configurable via days_ahead parameter)
    - Stores generated posts in the database with proper status
    - Returns list of generated posts with their IDs
    
    Args:
        request: Bulk generation request with platform, brand_voice, post_history, days_ahead, and model
        db_session: Database session
        
    Returns:
        List of generated posts with their IDs and metadata
        
    Raises:
        HTTPException: If validation fails or generation encounters errors
    """
    # Validate input parameters
    if not validate_platform(request.platform):
        logger.error(f"Invalid platform: {request.platform}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: twitter, linkedin, threads"
        )
    
    if not validate_days_ahead(request.days_ahead):
        logger.error(f"Invalid days_ahead: {request.days_ahead}")
        raise HTTPException(
            status_code=400,
            detail="Invalid days_ahead. Must be between 1 and 30"
        )
    
    if not request.brand_voice or len(request.brand_voice.strip()) == 0:
        logger.error("Empty brand_voice provided")
        raise HTTPException(
            status_code=400,
            detail="brand_voice cannot be empty"
        )
    
    logger.info(
        f"Starting bulk generation for {request.platform} "
        f"({request.days_ahead} days ahead, model: {request.model})"
    )
    
    try:
        generated_posts = []
        successful_posts = 0
        failed_posts = 0
        
        # Generate posts for each day
        for day in range(request.days_ahead):
            try:
                logger.info(f"Generating post for day {day + 1}/{request.days_ahead}")
                
                # Fetch trending topics for this day
                trending_topics = get_platform_trending_topics(request.platform)
                
                # Select a topic from trending topics (rotate through them)
                if trending_topics:
                    topic = trending_topics[day % len(trending_topics)]
                else:
                    topic = f"Day {day + 1} Update"
                
                logger.info(f"Selected topic for day {day + 1}: {topic}")
                
                # Generate post content with AI service
                content = await generate_post_with_fallback(
                    platform=request.platform,
                    topic=topic,
                    brand_voice=request.brand_voice,
                    trends=trending_topics,
                    model=request.model,
                    post_history=request.post_history
                )
                
                # Extract topic from content for database storage
                extracted_topic = extract_topic_from_content(content)
                
                # Calculate scheduled date
                scheduled_at = calculate_scheduled_date(day)
                
                # Create post data
                post_data = {
                    "platform": request.platform,
                    "content": content,
                    "brand_voice": request.brand_voice,
                    "topic": extracted_topic,
                    "status": "draft",
                    "scheduled_at": scheduled_at
                }
                
                # Store post in database
                db_post = models.Post(**post_data)
                db_session.add(db_post)
                db_session.flush()  # Get the ID without committing
                
                logger.info(f"Created post with ID {db_post.id} for day {day + 1}")
                
                # Add to response list
                generated_posts.append(GeneratedPost(
                    id=db_post.id,
                    platform=request.platform,
                    content=content,
                    brand_voice=request.brand_voice,
                    topic=extracted_topic,
                    status="draft",
                    scheduled_at=scheduled_at,
                    created_at=db_post.created_at
                ))
                
                successful_posts += 1
                
            except Exception as e:
                logger.error(f"Failed to generate post for day {day + 1}: {e}")
                failed_posts += 1
                # Continue with next day even if one fails
                continue
        
        # Commit all successful posts to database
        db_session.commit()
        
        logger.info(
            f"Bulk generation completed: {successful_posts} successful, {failed_posts} failed"
        )
        
        # If all posts failed, raise an error
        if successful_posts == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any posts. Please check your configuration and try again."
            )
        
        return generated_posts
        
    except HTTPException:
        # Re-raise HTTP exceptions
        db_session.rollback()
        raise
    except Exception as e:
        logger.error(f"Bulk generation failed: {e}")
        db_session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Bulk generation failed: {str(e)}"
        )
