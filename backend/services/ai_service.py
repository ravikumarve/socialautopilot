"""
AI Service Module for Social Autopilot

This module provides multi-API support for generating social media content
using different AI providers (Gemini, Claude, NVIDIA NIM).

Author: Social Autopilot Team
Version: 1.0.0
"""

import google.genai as genai
import os
import logging
import requests
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIModel(Enum):
    """Enumeration of supported AI models"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    NIM = "nim"


class AIConstants:
    """Constants for AI service configuration"""
    
    # Model identifiers
    GEMINI_MODEL = "gemini-2.5-pro"
    NIM_MODEL = "meta/llama-3.1-405b-instruct"
    
    # API endpoints
    NIM_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    # API configuration
    DEFAULT_MAX_TOKENS = 100
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_TRENDS = 3
    
    # Error messages
    UNSUPPORTED_MODEL_ERROR = "Unsupported model: {model}"
    API_KEY_MISSING_ERROR = "{model}_API_KEY not found in .env"
    API_KEY_INVALID_ERROR = "{model}_API_KEY not properly configured in .env"
    NO_RESPONSE_ERROR = "No response text found in {model} API response"
    API_FAILURE_ERROR = "{model} API failed: {error}"
    
    # Placeholder values
    PLACEHOLDER_API_KEY = "your_key_here"
    
    # Prompt templates
    BASE_PROMPT_TEMPLATE = (
        "Generate a {platform} post about {topic} with a {brand_voice} brand voice. "
        "Make it engaging and appropriate for the platform."
    )
    
    TREND_AWARE_PROMPT_TEMPLATE = (
        "Generate a {platform} post about {topic} that incorporates these trending topics: {trends}. "
        "Brand voice: {brand_voice}. Make it engaging and appropriate for the platform."
    )
    
    FALLBACK_POST_TEMPLATE = "Check out our latest update on {topic}! #news #update"


@dataclass
class AIResponse:
    """Data class for AI model responses"""
    text: str
    metadata: Dict[str, Any]
    model: str
    success: bool = True
    error: Optional[str] = None


class MockClaudeModel:
    """Mock implementation of Claude API for testing purposes"""
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a simulated Claude API response
        
        Args:
            prompt: The input prompt for generation
            
        Returns:
            Dictionary containing generated text and metadata
        """
        logger.info("Using mock Claude model for generation")
        
        # Simulate Claude response by transforming the prompt
        simulated_response = prompt.replace('Generate a', 'Here is').replace('brand voice', 'in a simulated voice')
        
        return {
            "text": f"[Claude] {simulated_response}",
            "metadata": {
                "token_usage": {
                    "input": 10,
                    "output": 50
                },
                "model": "mock-claude"
            }
        }


class RealNIMModel:
    """Real implementation of NVIDIA NIM API"""
    
    def __init__(self):
        """Initialize the NIM model with API key validation"""
        self.api_key = self._validate_api_key()
        self.model = AIConstants.NIM_MODEL
        self.api_url = AIConstants.NIM_API_URL
    
    def _validate_api_key(self) -> str:
        """
        Validate and return the NIM API key
        
        Returns:
            Validated API key
            
        Raises:
            ValueError: If API key is missing or invalid
        """
        nim_api_key = os.getenv("NIM_API_KEY")
        if not nim_api_key:
            raise ValueError(AIConstants.API_KEY_MISSING_ERROR.format(model="NIM"))
        
        if nim_api_key == AIConstants.PLACEHOLDER_API_KEY:
            raise ValueError(AIConstants.API_KEY_INVALID_ERROR.format(model="NIM"))
        
        return nim_api_key
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate content using NVIDIA NIM API
        
        Args:
            prompt: The input prompt for generation
            
        Returns:
            Dictionary containing generated text and metadata
            
        Raises:
            RuntimeError: If API call fails
            ValueError: If response format is invalid
        """
        logger.info(f"Using NIM model ({self.model}) for generation")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": AIConstants.DEFAULT_MAX_TOKENS,
            "temperature": AIConstants.DEFAULT_TEMPERATURE
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated text from the response
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0]["message"]["content"]
                logger.info(f"NIM generation successful. Tokens used: {result.get('usage', {})}")
                
                return {
                    "text": generated_text,
                    "metadata": {
                        "token_usage": result.get("usage", {"input": 15, "output": 60}),
                        "model": result.get("model", self.model)
                    }
                }
            else:
                raise ValueError(AIConstants.NO_RESPONSE_ERROR.format(model="NIM"))
                
        except requests.exceptions.RequestException as e:
            error_msg = AIConstants.API_FAILURE_ERROR.format(model="NIM", error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = AIConstants.API_FAILURE_ERROR.format(model="NIM", error=str(e))
            logger.error(error_msg)
            raise RuntimeError(error_msg)


def get_ai_model(model_name: str) -> Any:
    """
    Factory function to get the appropriate AI model instance
    
    Args:
        model_name: Name of the AI model (gemini, claude, nim)
        
    Returns:
        Instance of the requested AI model
        
    Raises:
        ValueError: If model name is invalid or API key is missing
    """
    try:
        model_enum = AIModel(model_name.lower())
    except ValueError:
        raise ValueError(AIConstants.UNSUPPORTED_MODEL_ERROR.format(model=model_name))
    
    if model_enum == AIModel.GEMINI:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key or gemini_api_key == AIConstants.PLACEHOLDER_API_KEY:
            raise ValueError(AIConstants.API_KEY_INVALID_ERROR.format(model="GEMINI"))
        
        logger.info(f"Initializing Gemini model: {AIConstants.GEMINI_MODEL}")
        client = genai.Client(api_key=gemini_api_key)
        return client
    
    elif model_enum == AIModel.CLAUDE:
        logger.info("Initializing mock Claude model")
        return MockClaudeModel()
    
    elif model_enum == AIModel.NIM:
        logger.info("Initializing NIM model")
        return RealNIMModel()


def build_prompt(platform: str, topic: str, brand_voice: str) -> str:
    """
    Build a prompt for social media post generation
    
    Args:
        platform: Target social media platform (Twitter, LinkedIn, Threads)
        topic: Topic for the post
        brand_voice: Brand voice/style for the post
        
    Returns:
        Formatted prompt string
    """
    return AIConstants.BASE_PROMPT_TEMPLATE.format(
        platform=platform,
        topic=topic,
        brand_voice=brand_voice
    )


def build_trend_aware_prompt(platform: str, topic: str, brand_voice: str, trends: List[str]) -> str:
    """
    Build a prompt that incorporates trending topics
    
    Args:
        platform: Target social media platform
        topic: Topic for the post
        brand_voice: Brand voice/style for the post
        trends: List of trending topics to incorporate
        
    Returns:
        Formatted prompt string with trend context
    """
    trends_context = ", ".join(trends[:AIConstants.DEFAULT_TOP_TRENDS])
    return AIConstants.TREND_AWARE_PROMPT_TEMPLATE.format(
        platform=platform,
        topic=topic,
        trends=trends_context,
        brand_voice=brand_voice
    )


def fallback_post(platform: str, topic: str) -> str:
    """
    Generate a fallback post when AI generation fails
    
    Args:
        platform: Target social media platform
        topic: Topic for the post
        
    Returns:
        Fallback post string
    """
    return AIConstants.FALLBACK_POST_TEMPLATE.format(topic=topic)


async def generate_post(
    platform: str, 
    topic: str, 
    brand_voice: str, 
    model: str = "gemini"
) -> str:
    """
    Generate a social media post using the specified AI model
    
    Args:
        platform: Target social media platform (Twitter, LinkedIn, Threads)
        topic: Topic for the post
        brand_voice: Brand voice/style for the post
        model: AI model to use (gemini, claude, nim). Defaults to "gemini"
        
    Returns:
        Generated social media post text
        
    Raises:
        ValueError: If model name is invalid
        RuntimeError: If API call fails
    """
    logger.info(f"Generating post for {platform} using {model} model")
    
    try:
        prompt = build_prompt(platform, topic, brand_voice)
        ai_model = get_ai_model(model)
        
        if model == AIModel.GEMINI.value:
            response = ai_model.models.generate_content(
                model=AIConstants.GEMINI_MODEL,
                contents=prompt
            )
            logger.info(f"Gemini generation successful")
            return response.text
        
        elif model in [AIModel.CLAUDE.value, AIModel.NIM.value]:
            response = ai_model.generate(prompt)
            logger.info(f"{model.upper()} generation successful")
            return response["text"]
        
        else:
            raise ValueError(AIConstants.UNSUPPORTED_MODEL_ERROR.format(model=model))
            
    except Exception as e:
        error_msg = f"{model} generation failed: {e}"
        logger.error(error_msg)
        logger.info(f"Using fallback post for {platform}")
        return fallback_post(platform, topic)


async def generate_trend_aware_post(
    platform: str, 
    topic: str, 
    brand_voice: str, 
    trends: List[str], 
    model: str = "gemini"
) -> str:
    """
    Generate a social media post incorporating trending topics
    
    Args:
        platform: Target social media platform (Twitter, LinkedIn, Threads)
        topic: Topic for the post
        brand_voice: Brand voice/style for the post
        trends: List of trending topics to incorporate
        model: AI model to use (gemini, claude, nim). Defaults to "gemini"
        
    Returns:
        Generated social media post text with trend integration
        
    Raises:
        ValueError: If model name is invalid
        RuntimeError: If API call fails
    """
    logger.info(f"Generating trend-aware post for {platform} using {model} model")
    
    try:
        prompt = build_trend_aware_prompt(platform, topic, brand_voice, trends)
        ai_model = get_ai_model(model)
        
        if model == AIModel.GEMINI.value:
            response = ai_model.models.generate_content(
                model=AIConstants.GEMINI_MODEL,
                contents=prompt
            )
            logger.info(f"Gemini trend-aware generation successful")
            return response.text
        
        elif model in [AIModel.CLAUDE.value, AIModel.NIM.value]:
            response = ai_model.generate(prompt)
            logger.info(f"{model.upper()} trend-aware generation successful")
            return response["text"]
        
        else:
            raise ValueError(AIConstants.UNSUPPORTED_MODEL_ERROR.format(model=model))
            
    except Exception as e:
        error_msg = f"{model} trend-aware generation failed: {e}"
        logger.error(error_msg)
        logger.info(f"Using fallback post for {platform}")
        return fallback_post(platform, topic)


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate all API keys are properly configured
    
    Returns:
        Dictionary mapping model names to validation status
    """
    validation_status = {
        AIModel.GEMINI.value: bool(os.getenv("GEMINI_API_KEY") and 
                                  os.getenv("GEMINI_API_KEY") != AIConstants.PLACEHOLDER_API_KEY),
        AIModel.CLAUDE.value: True,  # Mock model doesn't require API key
        AIModel.NIM.value: bool(os.getenv("NIM_API_KEY") and 
                              os.getenv("NIM_API_KEY") != AIConstants.PLACEHOLDER_API_KEY)
    }
    
    logger.info(f"API key validation status: {validation_status}")
    return validation_status


def get_supported_models() -> List[str]:
    """
    Get list of supported AI models
    
    Returns:
        List of supported model names
    """
    return [model.value for model in AIModel]


if __name__ == "__main__":
    # Example usage and testing
    import asyncio
    
    async def test_generation():
        """Test function for AI generation"""
        print("Testing AI Service...")
        print(f"Supported models: {get_supported_models()}")
        print(f"API key validation: {validate_api_keys()}")
        
        # Test prompt building
        test_prompt = build_prompt("Twitter", "AI Innovation", "Professional")
        print(f"\nTest prompt:\n{test_prompt}")
        
        # Test trend-aware prompt
        test_trends = ["#AI", "#MachineLearning", "#Tech"]
        trend_prompt = build_trend_aware_prompt("LinkedIn", "Data Science", "Corporate", test_trends)
        print(f"\nTrend-aware prompt:\n{trend_prompt}")
        
        # Test fallback post
        fallback = fallback_post("Threads", "New Feature")
        print(f"\nFallback post:\n{fallback}")
    
    asyncio.run(test_generation())