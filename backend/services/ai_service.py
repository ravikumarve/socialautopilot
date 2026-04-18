import google.generativeai as genai
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")


async def generate_post(platform: str, topic: str, brand_voice: str) -> str:
    """
    Generate a social media post using Gemini 2.5 Pro
    """
    try:
        prompt = build_prompt(platform, topic, brand_voice)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        return fallback_post(platform, topic)


def build_prompt(platform: str, topic: str, brand_voice: str) -> str:
    """Build the prompt for post generation"""
    return f"""Generate a {platform} post about {topic} with a {brand_voice} brand voice.
    Make it engaging and appropriate for the platform."""


def fallback_post(platform: str, topic: str) -> str:
    """Fallback post when AI generation fails"""
    return f"Check out our latest update on {topic}! #news #update"


async def generate_trend_aware_post(
    platform: str, topic: str, brand_voice: str, trends: list
) -> str:
    """
    Generate a post incorporating trending topics
    """
    try:
        trends_context = ", ".join(trends[:3])  # Top 3 trends
        prompt = f"""Generate a {platform} post about {topic} that incorporates these trending topics: {trends_context}.
        Brand voice: {brand_voice}. Make it engaging and appropriate for the platform."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini trend-aware generation failed: {e}")
        return fallback_post(platform, topic)
