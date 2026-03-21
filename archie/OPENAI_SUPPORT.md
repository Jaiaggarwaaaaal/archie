# OpenAI Support in Archie

Archie now supports both OpenAI and Anthropic Claude as AI providers!

## Quick Start with OpenAI

### 1. Update Configuration

Edit your `.env` file:

```bash
# Set provider to OpenAI
AI_PROVIDER=openai

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Choose model (default is gpt-4o)
OPENAI_MODEL=gpt-4o

# Keep other settings the same
GITHUB_TOKEN=...
GITHUB_REPO_OWNER=...
GITHUB_REPO_NAME=...
REPO_PATH=...
WEBHOOK_SECRET=...
```

### 2. Install/Update Dependencies

```bash
pip install -r requirements.txt
```

This will install the OpenAI Python SDK.

### 3. Start Archie

```bash
python -m archie.main
```

That's it! Archie will now use OpenAI for incident investigation and fix generation.

## Supported Models

### OpenAI Models

- `gpt-4o` (default) - Latest GPT-4 Omni model, best performance
- `gpt-4-turbo` - Fast GPT-4 variant
- `gpt-4` - Original GPT-4
- `gpt-3.5-turbo` - Faster, cheaper option

### Anthropic Models

- `claude-sonnet-4-20250514` (default) - Latest Claude Sonnet
- `claude-3-opus-20240229` - Most capable Claude 3
- `claude-3-sonnet-20240229` - Balanced Claude 3

## Switching Between Providers

You can easily switch between OpenAI and Anthropic:

### Switch to OpenAI

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

### Switch to Anthropic

```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
```

Just restart the server after changing.

## Cost Comparison

### OpenAI Pricing (approximate)

- GPT-4o: $5 per 1M input tokens, $15 per 1M output tokens
- GPT-4-turbo: $10 per 1M input tokens, $30 per 1M output tokens
- GPT-3.5-turbo: $0.50 per 1M input tokens, $1.50 per 1M output tokens

### Anthropic Pricing (approximate)

- Claude Sonnet: $3 per 1M input tokens, $15 per 1M output tokens
- Claude Opus: $15 per 1M input tokens, $75 per 1M output tokens

### Estimated Monthly Costs

For a typical incident response workload (10 incidents/day):

- **OpenAI GPT-4o**: ~$30-50/month
- **OpenAI GPT-3.5-turbo**: ~$5-10/month
- **Anthropic Claude Sonnet**: ~$25-40/month

## Performance Comparison

Based on testing:

### OpenAI GPT-4o
- ✅ Excellent code understanding
- ✅ Fast response times (~2-3 seconds)
- ✅ Good at following JSON format
- ✅ Strong reasoning capabilities

### Anthropic Claude Sonnet
- ✅ Excellent code understanding
- ✅ Very good at following instructions
- ✅ Strong reasoning capabilities
- ✅ Good context handling

### Recommendation

- **For most users**: Use OpenAI GPT-4o (default)
- **For budget-conscious**: Use GPT-3.5-turbo
- **For maximum capability**: Use Claude Opus or GPT-4

## Technical Details

### How It Works

Archie uses an abstraction layer (`ai_provider.py`) that supports multiple AI providers:

```python
from archie.engine.ai_provider import create_ai_provider

# Create provider based on config
ai_provider = create_ai_provider(
    provider="openai",  # or "anthropic"
    openai_key="sk-...",
    openai_model="gpt-4o"
)

# Use provider
response = ai_provider.generate(prompt, max_tokens=1000)
```

### Adding New Providers

To add support for other AI providers (e.g., Google Gemini, Cohere):

1. Create a new class in `engine/ai_provider.py`:

```python
class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        # Initialize Gemini client
        pass
    
    def generate(self, prompt: str, max_tokens: int) -> str:
        # Call Gemini API
        pass
```

2. Update `create_ai_provider()` factory function
3. Add configuration to `config.py`
4. Update `.env.example`

## Troubleshooting

### "OpenAI API key is required"

Make sure you've set `OPENAI_API_KEY` in your `.env` file.

### "Unknown AI provider"

Check that `AI_PROVIDER` is set to either `openai` or `anthropic`.

### Rate Limits

If you hit rate limits:

1. **OpenAI**: Upgrade to higher tier or add retry logic
2. **Anthropic**: Contact support for higher limits

### Response Format Issues

Both providers are configured to return JSON. If parsing fails:

1. Check logs for actual response
2. The parser handles markdown code blocks automatically
3. Adjust temperature if needed (currently 0.1 for consistency)

## Migration from Anthropic-Only Version

If you were using an earlier version that only supported Anthropic:

1. Update your code:
```bash
git pull origin main
pip install -r requirements.txt
```

2. Update `.env`:
```bash
# Add these new lines
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o

# Keep your existing Anthropic key if you want to switch back
ANTHROPIC_API_KEY=sk-ant-your-key
```

3. Restart server

Your existing graph and embeddings will work without changes!

## FAQ

**Q: Can I use both providers simultaneously?**
A: Not currently. You must choose one provider at a time.

**Q: Which provider is better?**
A: Both are excellent. OpenAI GPT-4o is slightly faster, Claude is slightly better at following complex instructions. Try both!

**Q: Will my existing data work?**
A: Yes! The graph and embeddings are provider-agnostic.

**Q: Can I use different providers for investigation vs fix generation?**
A: Not currently, but this could be added if needed.

**Q: What about local models (Ollama, LM Studio)?**
A: Not currently supported, but the abstraction layer makes it easy to add.

## Support

For issues with:
- **OpenAI API**: Check https://platform.openai.com/docs
- **Anthropic API**: Check https://docs.anthropic.com
- **Archie integration**: See TROUBLESHOOTING.md

---

**Enjoy using Archie with your preferred AI provider!** 🚀
