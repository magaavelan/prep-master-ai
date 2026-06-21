# AI Provider Configuration Guide

This project supports multiple AI providers for interview answer evaluation. Switch between them using the `AI_PROVIDER` environment variable.

## Quick Start

### 1. OpenRouter (Recommended - Best Value)
```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_MODEL=openai/gpt-4o
OPENROUTER_HTTP_REFERER=http://localhost:8000
OPENROUTER_X_TITLE=AI Interview Simulator
```

**Models supported (examples):**
- `openai/gpt-4o` - Latest OpenAI GPT-4
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `anthropic/claude-3.5-sonnet` - Claude 3.5
- `meta-llama/llama-2-70b` - Open source Llama
- [Full list: https://openrouter.ai/docs#models](https://openrouter.ai/docs#models)

### 2. OpenAI (Native)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4o
```

**Models available:**
- `gpt-4o` - Latest GPT-4
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - Faster, cheaper option

### 3. Grok (xAI)
```env
AI_PROVIDER=grok
GROK_API_KEY=xai-xxxxx
GROK_MODEL=grok-2-latest
```

**Models available:**
- `grok-2-latest` - Latest Grok model
- `grok-vision-beta` - Vision capabilities

---

## Environment File Setup

Create a `.env` file in your project root:

```bash
# AI Provider selection (options: openrouter, openai, grok)
AI_PROVIDER=openrouter

# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-YOUR_API_KEY_HERE
OPENROUTER_MODEL=openai/gpt-4o
OPENROUTER_HTTP_REFERER=http://localhost:8000
OPENROUTER_X_TITLE=AI Interview Simulator

# OpenAI Configuration (if using openai provider)
# OPENAI_API_KEY=sk-proj-YOUR_API_KEY_HERE
# OPENAI_MODEL=gpt-4o

# Grok Configuration (if using grok provider)
# GROK_API_KEY=xai-YOUR_API_KEY_HERE
# GROK_MODEL=grok-2-latest
```

---

## Setup Instructions by Provider

### OpenRouter Setup
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up and create API key
3. Add to `.env`:
   ```env
   AI_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-v1-xxxxx
   ```

### OpenAI Setup
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create API key in API keys section
3. Add to `.env`:
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-xxxxx
   ```

### Grok (xAI) Setup
1. Visit [console.x.ai](https://console.x.ai)
2. Create API key
3. Add to `.env`:
   ```env
   AI_PROVIDER=grok
   GROK_API_KEY=xai-xxxxx
   ```

---

## Price Comparison (as of 2024)

| Provider | Model | Input | Output | Notes |
|----------|-------|-------|--------|-------|
| **OpenRouter** | openai/gpt-4o | $5/1M | $15/1M | Best value, multiple model access |
| **OpenAI** | gpt-4o | $5/1M | $15/1M | Official, best support |
| **Grok** | grok-2-latest | $8/1M | $24/1M | Latest reasoning model |
| **OpenRouter** | claude-3.5-sonnet | $3/1M | $15/1M | Good balance |
| **OpenRouter** | llama-2-70b | $0.00 | $0.00 | Free, open source |

---

## API Response Format

All providers return the same format:

```json
{
    "score": 8,
    "strengths": "Clear explanation of the concept...",
    "weaknesses": "Could have included more examples...",
    "ideal_answer": "The ideal answer would include..."
}
```

---

## Error Handling

### Authentication Failed (401)
- **OpenRouter**: Verify `OPENROUTER_API_KEY`
- **OpenAI**: Verify `OPENAI_API_KEY` and that it has sufficient credits
- **Grok**: Verify `GROK_API_KEY`

### Rate Limiting (429)
- Add retry logic to `ai_service.py`
- Consider using OpenRouter with fallback models

### Network Errors
- Application automatically returns fallback score (5) and generic feedback
- Check internet connection and API endpoint URLs

---

## Switching Providers at Runtime

To switch providers without restarting:

```python
import os
from interviews.ai_providers import get_provider

# Switch to a different provider
os.environ['AI_PROVIDER'] = 'grok'
os.environ['GROK_API_KEY'] = 'xai-xxxxx'

# Get the new provider
provider = get_provider('grok')
result = provider.evaluate(question, answer)
```

---

## Production Deployment

For production, use environment variables from your hosting platform:

**Heroku:**
```bash
heroku config:set AI_PROVIDER=openrouter
heroku config:set OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

**AWS Lambda / Render / Railway:**
Set environment variables in the deployment dashboard.

**Docker:**
```dockerfile
ENV AI_PROVIDER=openrouter
ENV OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
```

---

## Troubleshooting

### Provider not found error
```
RuntimeError: Unsupported AI_PROVIDER 'xxxx'
```
- Check spelling: `openrouter`, `openai`, or `grok`
- Verify `.env` file is being loaded

### Missing API Key error
```
RuntimeError: Missing XXX_API_KEY environment variable
```
- Add the API key to `.env`
- Reload Django: `python manage.py runserver`

### Invalid JSON response
- Some models may have formatting issues
- Try a different model or provider
- Check model availability in provider's documentation

---

## Adding a New Provider

1. Create a new provider class in `ai_providers.py`:
```python
class MyProviderName(AIProvider):
    def evaluate(self, question, user_answer):
        # Implement your API call here
        pass
```

2. Update `get_provider()` function to include your provider

3. Add environment variables documentation

---

**Questions or issues?** Check the individual provider's documentation or create an issue.
