# Environment Variable Setup Guide for AI Interview Simulator

This guide explains how to properly configure environment variables for the AI Interview Simulator, specifically for OpenRouter API integration.

## Quick Fix Summary

The error **"Missing OPENROUTER_API_KEY environment variable"** occurs because the `.env` file was missing the `OPENROUTER_API_KEY` variable. This has been fixed by:

1. ✅ Renamed `OPENAI_API_KEY` to `OPENROUTER_API_KEY` in `.env`
2. ✅ Added comprehensive configuration with comments
3. ✅ Set `AI_PROVIDER=openrouter` as the default provider

## Step-by-Step Setup Instructions

### 1. Verify .env File Location

The `.env` file must be in the **root directory** of your Django project (same level as `manage.py`):

```
AI_Interview_Simulator/
├── .env                    # ← Must be here
├── manage.py
├── config/
│   ├── settings.py
│   └── urls.py
├── interviews/
├── users/
└── reports/
```

### 2. Install Required Dependencies

The project uses `python-dotenv` to load environment variables. Install it if not already installed:

```bash
pip install python-dotenv
```

Or if you have a requirements file:

```bash
pip install -r requirements.txt
```

### 3. Configure Your .env File

The `.env` file has been updated with the correct configuration. Here's what each variable does:

```bash
# AI Provider Selection
AI_PROVIDER=openrouter  # Options: openai, openrouter, grok (default: openrouter)

# OpenRouter Configuration (Required when AI_PROVIDER=openrouter)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here  # Your OpenRouter API key
OPENROUTER_MODEL=openai/gpt-4o                 # Model to use (default: openai/gpt-4o)
OPENROUTER_HTTP_REFERER=http://localhost       # Optional attribution header
OPENROUTER_X_TITLE=AI Interview Simulator      # Optional attribution header

# OpenAI Configuration (Only if AI_PROVIDER=openai)
# OPENAI_API_KEY=your-openai-key
# OPENAI_MODEL=gpt-4o

# Grok Configuration (Only if AI_PROVIDER=grok)
# GROK_API_KEY=your-grok-key
# GROK_MODEL=grok-2-latest
```

### 4. Get Your OpenRouter API Key

If you don't have an OpenRouter API key:

1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key and paste it in your `.env` file as `OPENROUTER_API_KEY`

### 5. Restart Django Development Server

**Important:** Environment variables are loaded when Django starts. After modifying `.env`, you **must restart** the Django server:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### 6. Verify Environment Variables Are Loaded

You can verify that the environment variables are correctly loaded by:

#### Option A: Check Django Shell
```bash
python manage.py shell
```
```python
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("OPENROUTER_API_KEY"))  # Should print your API key
```

#### Option B: Add Debug Print (Temporary)
Add this to `config/settings.py` after `load_dotenv()`:
```python
print(f"OPENROUTER_API_KEY loaded: {'Yes' if os.getenv('OPENROUTER_API_KEY') else 'No'}")
```

### 7. Test the AI Evaluation

Make a test request to trigger the AI evaluation:

```bash
# Example: Submit an answer to an interview
curl -X POST http://localhost:8000/api/interviews/1/answer/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "question": "What is Python?",
    "user_answer": "Python is a programming language."
  }'
```

Check the server logs for:
- `[OpenRouter] Starting answer evaluation`
- `[OpenRouter] API Response Status Code: 200`
- `[OpenRouter] Successfully extracted evaluation`

## Troubleshooting

### Error: "Missing OPENROUTER_API_KEY environment variable"

**Cause:** The `.env` file doesn't contain `OPENROUTER_API_KEY` or Django didn't load it.

**Solution:**
1. Verify `.env` file exists in the root directory
2. Check that `OPENROUTER_API_KEY` is defined (not commented out)
3. Restart Django server
4. Ensure `python-dotenv` is installed

### Error: "OpenRouter authentication failed (401)"

**Cause:** Invalid or expired API key.

**Solution:**
1. Verify your API key is correct (no extra spaces)
2. Check that your OpenRouter account has available credits
3. Regenerate a new API key if needed

### Error: "OpenRouter error (429)"

**Cause:** Rate limit exceeded.

**Solution:**
1. Wait a few minutes before retrying
2. Check your OpenRouter plan's rate limits
3. Consider upgrading your plan if you hit limits frequently

### Environment Variables Not Loading

**Symptoms:** `os.getenv("OPENROUTER_API_KEY")` returns `None`

**Solutions:**
1. **Check .env file location:** Must be in project root (same directory as `manage.py`)
2. **Check for typos:** Ensure variable name is exactly `OPENROUTER_API_KEY` (no extra spaces)
3. **Restart server:** Changes to `.env` only take effect after server restart
4. **Check python-dotenv:** Ensure it's installed and `load_dotenv()` is called in `settings.py`

## How Environment Variables Work in This Project

### Loading Chain:

1. **`.env` file** → Contains your API keys and configuration
2. **`config/settings.py`** → Calls `load_dotenv()` to load `.env` into `os.environ`
3. **`interviews/ai_service.py`** → Reads `os.getenv("OPENROUTER_API_KEY")`
4. **`interviews/ai_providers.py`** → Uses the API key to make requests

### Key Files:

- **`.env`** - Your environment configuration (DO NOT COMMIT TO GIT!)
- **`config/settings.py`** (lines 13-15, 166-183) - Loads `.env` and reads variables
- **`interviews/ai_service.py`** (lines 5-8, 49) - Reads `AI_PROVIDER` and calls provider
- **`interviews/ai_providers.py`** (lines 389-420) - Reads provider-specific keys

## Security Best Practices

### ✅ DO:
- Keep your `.env` file in `.gitignore`
- Use environment variables for all API keys
- Rotate API keys periodically
- Use different keys for development and production

### ❌ DON'T:
- Commit `.env` to version control
- Hardcode API keys in Python files
- Share your API keys publicly
- Use production keys in development

## Production Deployment

For production, use your hosting platform's environment variable management:

### Heroku:
```bash
heroku config:set OPENROUTER_API_KEY=your-key
heroku config:set AI_PROVIDER=openrouter
```

### Docker:
```yaml
# docker-compose.yml
environment:
  - OPENROUTER_API_KEY=your-key
  - AI_PROVIDER=openrouter
```

### AWS/GCP/Azure:
Use their respective secret management services (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault).

## Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [Django Settings Documentation](https://docs.djangoproject.com/en/6.0/topics/settings/)

## Need Help?

If you're still experiencing issues:

1. Check the Django server logs for detailed error messages
2. Verify all steps in this guide
3. Test with a simple Python script:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(os.getenv("OPENROUTER_API_KEY"))
   ```

---

**Last Updated:** 2026-06-12  
**Status:** ✅ Configuration Fixed - OpenRouter API integration should now work