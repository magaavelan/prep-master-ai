import os
import logging
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from .ai_providers import get_provider

load_dotenv()

logger = logging.getLogger(__name__)


def evaluate_answer(question: str, user_answer: str) -> Optional[Dict[str, Any]]:
    """
    Evaluate a user's answer using the configured AI provider.
    
    Supports multiple providers via AI_PROVIDER environment variable:
    - 'openai': Uses OpenAI API
    - 'openrouter': Uses OpenRouter API (supports 100+ models)
    - 'grok': Uses xAI Grok API
    
    Args:
        question: The interview question
        user_answer: The user's response to evaluate
    
    Returns:
        dict: {score, strengths, weaknesses, ideal_answer}
        None: If evaluation fails
    
    Environment Variables:
        AI_PROVIDER: Which provider to use (default: 'openrouter')
        
        For OpenAI:
            OPENAI_API_KEY: Your OpenAI API key
            OPENAI_MODEL: Model name (default: 'gpt-4o')
        
        For OpenRouter:
            OPENROUTER_API_KEY: Your OpenRouter API key
            OPENROUTER_MODEL: Model format (default: 'openai/gpt-4o')
            OPENROUTER_HTTP_REFERER: HTTP referer header (default: 'http://localhost')
            OPENROUTER_X_TITLE: X-Title header (default: 'AI Interview Simulator')
        
        For Grok:
            GROK_API_KEY: Your Grok (xAI) API key
            GROK_MODEL: Model name (default: 'grok-2-latest')
    """
    provider_name = (os.getenv("AI_PROVIDER") or "openrouter").strip().lower()

    logger.info(f"[EvaluateAnswer] Starting evaluation with provider: {provider_name}")
    logger.debug(f"[EvaluateAnswer] Question length: {len(question)}, Answer length: {len(user_answer)}")

    try:
        logger.debug(f"[EvaluateAnswer] Initializing {provider_name} provider...")
        provider = get_provider(provider_name)
        
        logger.debug(f"[EvaluateAnswer] Calling evaluate method on {provider_name} provider...")
        result = provider.evaluate(question=question, user_answer=user_answer)
        
        logger.info(f"[EvaluateAnswer] Successfully evaluated answer - score: {result.get('score')}")
        return result

    except PermissionError as e:
        logger.error(f"[EvaluateAnswer] PermissionError with {provider_name}: {e}")
        logger.error(f"[EvaluateAnswer] Check your API key for provider: {provider_name}")
        logger.error(f"[EvaluateAnswer] Missing API key might be: {provider_name.upper()}_API_KEY")
        return None
    except RuntimeError as e:
        logger.error(f"[EvaluateAnswer] RuntimeError from {provider_name}: {e}")
        logger.error(f"[EvaluateAnswer] Full error details: {type(e).__name__}")
        return None
    except Exception as e:
        logger.error(f"[EvaluateAnswer] Unexpected error with {provider_name}: {type(e).__name__}: {e}")
        logger.exception(f"[EvaluateAnswer] Exception traceback:")
        return None



