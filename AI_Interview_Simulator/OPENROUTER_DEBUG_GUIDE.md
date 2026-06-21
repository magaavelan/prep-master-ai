# OpenRouter Debugging Guide

This guide shows how to enable and view debug logs for OpenRouter API calls.

## Quick Start - Enable Debug Logging

Add this to your Django `settings.py` file:

```python
# Add this to config/settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'interviews.ai_providers': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'interviews.ai_service': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Debug Log Output Examples

### Success Case
```
[INFO] 2024-01-15 12:34:56.789 ai_providers - [OpenRouter] Starting answer evaluation
[DEBUG] 2024-01-15 12:34:56.790 ai_providers - [OpenRouter] Model: openai/gpt-4o, Question length: 45, Answer length: 120
[DEBUG] 2024-01-15 12:34:56.791 ai_providers - [OpenRouter] Sending POST request to https://openrouter.ai/api/v1/chat/completions
[INFO] 2024-01-15 12:34:57.123 ai_providers - [OpenRouter] API Response Status Code: 200
[DEBUG] 2024-01-15 12:34:57.124 ai_providers - [OpenRouter] Response Headers: {...}
[INFO] 2024-01-15 12:34:57.125 ai_service - [EvaluateAnswer] Successfully evaluated answer - score: 8
```

### Authentication Failure (401)
```
[INFO] 2024-01-15 12:34:56.789 ai_service - [EvaluateAnswer] Starting evaluation with provider: openrouter
[INFO] 2024-01-15 12:34:56.790 ai_providers - [OpenRouter] Starting answer evaluation
[DEBUG] 2024-01-15 12:34:56.791 ai_providers - [OpenRouter] Sending POST request to https://openrouter.ai/api/v1/chat/completions
[INFO] 2024-01-15 12:34:57.123 ai_providers - [OpenRouter] API Response Status Code: 401
[ERROR] 2024-01-15 12:34:57.124 ai_providers - [OpenRouter] Authentication Failed (401) - Invalid API Key or insufficient permissions
[ERROR] 2024-01-15 12:34:57.125 ai_providers - [OpenRouter] Error details: {"error": {"type": "invalid_api_key", "message": "Invalid API key provided"}}
[ERROR] 2024-01-15 12:34:57.126 ai_service - [EvaluateAnswer] PermissionError with openrouter: OpenRouter authentication failed (401)
[ERROR] 2024-01-15 12:34:57.127 ai_service - [EvaluateAnswer] Check your API key for provider: openrouter
[ERROR] 2024-01-15 12:34:57.128 ai_service - [EvaluateAnswer] Missing API key might be: OPENROUTER_API_KEY
```

### Rate Limiting (429)
```
[ERROR] 2024-01-15 12:34:57.123 ai_providers - [OpenRouter] HTTP Error 429
[ERROR] 2024-01-15 12:34:57.124 ai_providers - [OpenRouter] Error JSON: {
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please wait before making another request."
  }
}
[ERROR] 2024-01-15 12:34:57.125 ai_providers - [OpenRouter] Error type: rate_limit_exceeded, Message: Rate limit exceeded. Please wait before making another request.
```

### Invalid JSON Response
```
[ERROR] 2024-01-15 12:34:57.123 ai_providers - [OpenRouter] Failed to parse response as JSON: Expecting value: line 1 column 1 (char 0)
[ERROR] 2024-01-15 12:34:57.124 ai_providers - [OpenRouter] Raw response text: 502 Bad Gateway
```

### Missing "Choices" Field
```
[ERROR] 2024-01-15 12:34:57.124 ai_providers - [OpenRouter] Missing 'choices' array in response. Keys present: ['error', 'message']
[ERROR] 2024-01-15 12:34:57.125 ai_providers - [OpenRouter] Full response: {
  "error": {
    "type": "server_error",
    "message": "Internal server error"
  },
  "message": "Internal server error"
}
```

### JSON Extraction Failure
```
[ERROR] 2024-01-15 12:34:57.125 ai_providers - [JSONExtractor] Failed to parse extracted JSON: Expecting value: line 1 column 10 (char 9)
[ERROR] 2024-01-15 12:34:57.126 ai_providers - [JSONExtractor] Extracted text: { invalid json }
```

## Viewing Logs

### Option 1: Console Output (Development)
Logs print to terminal when running:
```bash
python manage.py runserver
```

### Option 2: File Logging
Logs save to `debug.log` in your project root:
```bash
# View last 50 lines
tail -50 debug.log

# Watch logs in real-time (Linux/Mac)
tail -f debug.log

# Watch logs in real-time (PowerShell)
Get-Content debug.log -Wait
```

### Option 3: Filter Logs
```bash
# Show only OpenRouter errors
grep "\[ERROR\].*OpenRouter" debug.log

# Show only authentication errors
grep "PermissionError\|authentication\|401" debug.log

# Show only JSON parsing errors
grep "JSONExtractor" debug.log

# Show only successful evaluations
grep "Successfully evaluated" debug.log
```

## Troubleshooting Checklist

Use these log patterns to diagnose issues:

| Issue | Log to Look For | Solution |
|-------|-----------------|----------|
| Invalid API Key | `401 Authentication Failed` | Check `OPENROUTER_API_KEY` in `.env` |
| Rate Limited | `429 rate_limit_exceeded` | Wait before retrying, consider queuing |
| Network Error | `RequestException: Connection` | Check internet connection and proxy |
| Invalid Response Format | `'choices' array is empty` or `Missing 'message'` | Contact OpenRouter support |
| JSON Parsing Error | `Failed to parse extracted JSON` | Model response format may have changed |
| Model Not Found | `error_type: model_not_found` | Verify model name in `OPENROUTER_MODEL` |
| Empty Response | `returned empty content` | Model may have timed out or errored |

## Common Environment Variables

Verify these are set in your `.env`:

```env
# Required
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Optional but recommended
OPENROUTER_MODEL=openai/gpt-4o
OPENROUTER_HTTP_REFERER=http://localhost:8000
OPENROUTER_X_TITLE=AI Interview Simulator
```

## Enabling Logs for Other Providers

For OpenAI:
```python
'interviews.ai_providers': {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
},
```

For Grok:
```python
'interviews.ai_providers': {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
},
```

## Production Logging

For production deployments, consider:

1. **Log rotation** - Prevent logs from growing indefinitely
```python
'file': {
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': 'debug.log',
    'maxBytes': 10485760,  # 10MB
    'backupCount': 5,
    'formatter': 'verbose',
}
```

2. **Syslog integration** - Send logs to centralized system
3. **Error tracking** - Use Sentry, DataDog, or similar
4. **Reduce verbosity** - Set level to `INFO` instead of `DEBUG`

## Testing Logs

Test your logging setup:

```python
# In Django shell: python manage.py shell
import logging
logger = logging.getLogger('interviews.ai_service')
logger.info("Test info message")
logger.error("Test error message")
```

You should see these messages in your logs immediately.
