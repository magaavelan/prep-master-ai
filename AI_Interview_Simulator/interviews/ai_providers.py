import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)



class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def evaluate(self, question: str, user_answer: str) -> Dict[str, Any]:
        """
        Evaluate a user's answer.
        
        Returns:
            dict: {score, strengths, weaknesses, ideal_answer}
        
        Raises:
            PermissionError: For authentication failures (401)
            RuntimeError: For other API errors
        """
        pass



@dataclass(frozen=True)
class OpenAIConfig:
    """Configuration for OpenAI provider."""
    api_key: str
    model: str = "gpt-4o"


@dataclass(frozen=True)
class OpenRouterConfig:
    """Configuration for OpenRouter provider."""
    api_key: str
    model: str = "openai/gpt-4o"
    http_referer: str = "http://localhost"
    x_title: str = "AI Interview Simulator"


@dataclass(frozen=True)
class GrokConfig:
    """Configuration for Grok (xAI) provider."""
    api_key: str
    model: str = "grok-2-latest"



class OpenAIProvider(AIProvider):
    """OpenAI API provider implementation."""

    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.url = "https://api.openai.com/v1/chat/completions"

    def evaluate(self, question: str, user_answer: str) -> Dict[str, Any]:
        """Evaluate answer using OpenAI API."""
        
        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer.\n"
            "You must respond with a valid JSON object containing exactly these fields:\n"
            "- score: integer from 1 to 10 (1 being poor, 10 being excellent)\n"
            "- strengths: string describing what the candidate did well\n"
            "- weaknesses: string describing areas for improvement\n"
            "- ideal_answer: string containing a sample ideal answer for the question\n\n"
            "IMPORTANT: Return ONLY the JSON object, with no additional text or markdown formatting.\n"
            "Ensure the JSON is valid and can be parsed directly."
        )

        user_prompt = (
            "Please evaluate the following interview answer:\n\n"
            f"Question: {question}\n\n"
            f"Candidate's Answer: {user_answer}"
        )

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f"OpenAI request failed: {e}") from e

        if resp.status_code == 401:
            raise PermissionError("OpenAI authentication failed (401)")

        if resp.status_code >= 400:
            raise RuntimeError(f"OpenAI error ({resp.status_code}): {resp.text}")

        try:
            data = resp.json()
        except ValueError as e:
            raise RuntimeError("OpenAI response was not valid JSON") from e

        try:
            choices = data.get("choices") or []
            message = choices[0].get("message") or {}
            model_text = message.get("content")
        except Exception as e:
            raise RuntimeError(f"OpenAI response missing expected fields: {e}") from e

        if not model_text:
            raise RuntimeError("OpenAI returned empty content")

        return _extract_json_object(model_text)



class OpenRouterProvider(AIProvider):
    """OpenRouter API provider implementation."""

    def __init__(self, config: OpenRouterConfig):
        self.config = config
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def evaluate(self, question: str, user_answer: str) -> Dict[str, Any]:
        """Evaluate answer using OpenRouter API with detailed logging."""
        
        logger.info("[OpenRouter] Starting answer evaluation")
        logger.debug(f"[OpenRouter] Model: {self.config.model}, Question length: {len(question)}, Answer length: {len(user_answer)}")
        
        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer.\n"
            "You must respond with a valid JSON object containing exactly these fields:\n"
            "- score: integer from 1 to 10 (1 being poor, 10 being excellent)\n"
            "- strengths: string describing what the candidate did well\n"
            "- weaknesses: string describing areas for improvement\n"
            "- ideal_answer: string containing a sample ideal answer for the question\n\n"
            "IMPORTANT: Return ONLY the JSON object, with no additional text or markdown formatting.\n"
            "Ensure the JSON is valid and can be parsed directly."
        )

        user_prompt = (
            "Please evaluate the following interview answer:\n\n"
            f"Question: {question}\n\n"
            f"Candidate's Answer: {user_answer}"
        )

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": self.config.http_referer,
            "X-Title": self.config.x_title,
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }

        logger.debug(f"[OpenRouter] Sending POST request to {self.url}")
        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)

            import os
            print("[OpenRouter][DEBUG] OPENROUTER_API_KEY:", os.getenv("OPENROUTER_API_KEY"))
            print("[OpenRouter][DEBUG] HTTP status_code:", resp.status_code)
            print("[OpenRouter][DEBUG] full response.text:", resp.text)

            logger.info(f"[OpenRouter] API Response Status Code: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"[OpenRouter] Network Request Failed: {type(e).__name__}: {e}")
            raise RuntimeError(f"OpenRouter request failed: {e}") from e


        logger.debug(f"[OpenRouter] Response Headers: {dict(resp.headers)}")
        logger.debug(f"[OpenRouter] Response Text: {resp.text[:500]}")  # First 500 chars to avoid log spam

        if resp.status_code == 401:
            logger.error("[OpenRouter] Authentication Failed (401) - Invalid API Key or insufficient permissions")
            try:
                error_data = resp.json()
                logger.error(f"[OpenRouter] Error details: {error_data}")
            except:
                logger.error(f"[OpenRouter] Raw response: {resp.text}")
            raise PermissionError("OpenRouter authentication failed (401)")

        if resp.status_code >= 400:
            logger.error(f"[OpenRouter] HTTP Error {resp.status_code}")
            try:
                error_data = resp.json()
                logger.error(f"[OpenRouter] Error JSON: {json.dumps(error_data, indent=2)}")
                
                if "error" in error_data:
                    error_msg = error_data["error"]
                    if isinstance(error_msg, dict):
                        logger.error(f"[OpenRouter] Error type: {error_msg.get('type')}, Message: {error_msg.get('message')}")
                    else:
                        logger.error(f"[OpenRouter] Error: {error_msg}")
            except:
                logger.error(f"[OpenRouter] Raw response text: {resp.text}")
            raise RuntimeError(f"OpenRouter error ({resp.status_code}): {resp.text}")

        logger.debug("[OpenRouter] Parsing response JSON")
        try:
            data = resp.json()
            logger.debug(f"[OpenRouter] JSON parsed successfully, keys: {list(data.keys())}")
        except ValueError as e:
            logger.error(f"[OpenRouter] Failed to parse response as JSON: {e}")
            logger.error(f"[OpenRouter] Raw response text: {resp.text}")
            raise RuntimeError("OpenRouter response was not valid JSON") from e

        logger.debug("[OpenRouter] Validating response structure")
        try:
            choices = data.get("choices")
            if not choices:
                logger.error(f"[OpenRouter] Missing 'choices' array in response. Keys present: {list(data.keys())}")
                logger.error(f"[OpenRouter] Full response: {json.dumps(data, indent=2)}")
                raise RuntimeError("OpenRouter response missing 'choices' field")
            
            if not isinstance(choices, list):
                logger.error(f"[OpenRouter] 'choices' is not a list, got: {type(choices)}")
                raise RuntimeError("OpenRouter 'choices' is not a list")
            
            if len(choices) == 0:
                logger.error("[OpenRouter] 'choices' array is empty")
                logger.error(f"[OpenRouter] Full response: {json.dumps(data, indent=2)}")
                raise RuntimeError("OpenRouter returned empty choices array")
            
            message = choices[0].get("message")
            if not message:
                logger.error(f"[OpenRouter] Missing 'message' in first choice. Structure: {list(choices[0].keys())}")
                raise RuntimeError("OpenRouter first choice missing 'message' field")
            
            if not isinstance(message, dict):
                logger.error(f"[OpenRouter] 'message' is not a dict, got: {type(message)}")
                raise RuntimeError("OpenRouter 'message' is not a dict")
            
            model_text = message.get("content")
            logger.debug(f"[OpenRouter] Message role: {message.get('role')}, Content length: {len(model_text) if model_text else 0}")
            
        except Exception as e:
            logger.error(f"[OpenRouter] Response structure validation failed: {e}")
            logger.error(f"[OpenRouter] Full response for inspection: {json.dumps(data, indent=2)}")
            raise RuntimeError(f"OpenRouter response missing expected fields: {e}") from e

        if not model_text:
            logger.error("[OpenRouter] Model returned empty content")
            logger.error(f"[OpenRouter] Full response: {json.dumps(data, indent=2)}")
            raise RuntimeError("OpenRouter returned empty content")

        logger.debug(f"[OpenRouter] Extracting JSON from model text (length: {len(model_text)})")
        logger.debug(f"[OpenRouter] Model text preview: {model_text[:200]}")
        
        try:
            result = _extract_json_object(model_text)
            logger.info(f"[OpenRouter] Successfully extracted evaluation: score={result.get('score')}, has_strengths={bool(result.get('strengths'))}, has_weaknesses={bool(result.get('weaknesses'))}")
            return result
        except Exception as e:
            logger.error(f"[OpenRouter] Failed to extract JSON object from model response: {e}")
            logger.error(f"[OpenRouter] Full model text: {model_text}")
            raise



class GrokProvider(AIProvider):
    """Grok (xAI) API provider implementation."""

    def __init__(self, config: GrokConfig):
        self.config = config
        self.url = "https://api.x.ai/v1/chat/completions"

    def evaluate(self, question: str, user_answer: str) -> Dict[str, Any]:
        """Evaluate answer using Grok API."""
        
        system_prompt = (
            "You are an expert technical interviewer evaluating a candidate's answer.\n"
            "You must respond with a valid JSON object containing exactly these fields:\n"
            "- score: integer from 1 to 10 (1 being poor, 10 being excellent)\n"
            "- strengths: string describing what the candidate did well\n"
            "- weaknesses: string describing areas for improvement\n"
            "- ideal_answer: string containing a sample ideal answer for the question\n\n"
            "IMPORTANT: Return ONLY the JSON object, with no additional text or markdown formatting.\n"
            "Ensure the JSON is valid and can be parsed directly."
        )

        user_prompt = (
            "Please evaluate the following interview answer:\n\n"
            f"Question: {question}\n\n"
            f"Candidate's Answer: {user_answer}"
        )

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=30)
        except requests.RequestException as e:
            raise RuntimeError(f"Grok request failed: {e}") from e

        if resp.status_code == 401:
            raise PermissionError("Grok authentication failed (401)")

        if resp.status_code >= 400:
            raise RuntimeError(f"Grok error ({resp.status_code}): {resp.text}")

        try:
            data = resp.json()
        except ValueError as e:
            raise RuntimeError("Grok response was not valid JSON") from e

        try:
            choices = data.get("choices") or []
            message = choices[0].get("message") or {}
            model_text = message.get("content")
        except Exception as e:
            raise RuntimeError(f"Grok response missing expected fields: {e}") from e

        if not model_text:
            raise RuntimeError("Grok returned empty content")

        return _extract_json_object(model_text)



def get_provider(provider_name: str) -> AIProvider:
    """
    Factory function to get the configured AI provider.
    
    Args:
        provider_name: One of 'openai', 'openrouter', 'grok'
    
    Returns:
        AIProvider instance configured with environment variables
    
    Raises:
        RuntimeError: If provider is unsupported or missing configuration
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    provider_name = provider_name.strip().lower()

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY environment variable")
        
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
        config = OpenAIConfig(api_key=api_key, model=model)
        return OpenAIProvider(config)

    elif provider_name == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")
        
        model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
        http_referer = os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost")
        x_title = os.getenv("OPENROUTER_X_TITLE", "AI Interview Simulator")
        
        config = OpenRouterConfig(
            api_key=api_key,
            model=model,
            http_referer=http_referer,
            x_title=x_title,
        )
        return OpenRouterProvider(config)

    elif provider_name == "grok":
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GROK_API_KEY environment variable")
        
        model = os.getenv("GROK_MODEL", "grok-2-latest")
        config = GrokConfig(api_key=api_key, model=model)
        return GrokProvider(config)

    else:
        raise RuntimeError(
            f"Unsupported AI_PROVIDER '{provider_name}'. "
            f"Supported providers: openai, openrouter, grok"
        )



def _extract_json_object(text: str) -> Dict[str, Any]:
    """Extract JSON object from model response text with detailed logging."""
    text = (text or "").strip()

    if text.startswith("{") and text.endswith("}"):
        logger.debug("[JSONExtractor] Text appears to be valid JSON (starts with { and ends with })")
        try:
            result = json.loads(text)
            logger.debug(f"[JSONExtractor] Successfully parsed JSON directly, keys: {list(result.keys())}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"[JSONExtractor] Failed to parse seemingly valid JSON: {e}")
            logger.error(f"[JSONExtractor] Text: {text[:300]}")
            raise

    logger.debug("[JSONExtractor] Text is not wrapped in braces, searching for JSON object...")
    start = text.find("{")
    end = text.rfind("}")
    
    if start == -1:
        logger.error("[JSONExtractor] No opening brace '{' found in text")
        logger.error(f"[JSONExtractor] Text preview: {text[:200]}")
        raise ValueError("No JSON object found in model output - missing opening brace")
    
    if end == -1:
        logger.error("[JSONExtractor] No closing brace '}' found in text")
        logger.error(f"[JSONExtractor] Text preview: {text[:200]}")
        raise ValueError("No JSON object found in model output - missing closing brace")
    
    if end <= start:
        logger.error(f"[JSONExtractor] Closing brace before opening brace (start={start}, end={end})")
        raise ValueError("No JSON object found in model output - invalid brace positions")

    json_text = text[start : end + 1]
    logger.debug(f"[JSONExtractor] Extracted JSON substring (length={len(json_text)})")
    logger.debug(f"[JSONExtractor] Extracted text: {json_text[:300]}")
    
    try:
        result = json.loads(json_text)
        logger.debug(f"[JSONExtractor] Successfully extracted JSON, keys: {list(result.keys())}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"[JSONExtractor] Failed to parse extracted JSON: {e}")
        logger.error(f"[JSONExtractor] Extracted text: {json_text}")
        raise

