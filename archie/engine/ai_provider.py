"""AI provider abstraction layer - supports OpenAI and Anthropic."""
import json
import logging
from typing import Dict, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate a response from the AI."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1
        )
        return response.choices[0].message.content


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Anthropic provider with model: {model}")
    
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using Anthropic."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


def create_ai_provider(
    provider: str,
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    openai_model: str = "gpt-4o",
    anthropic_model: str = "claude-sonnet-4-20250514"
) -> AIProvider:
    """Factory function to create AI provider."""
    
    if provider.lower() == "openai":
        if not openai_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        return OpenAIProvider(openai_key, openai_model)
    
    elif provider.lower() == "anthropic":
        if not anthropic_key:
            raise ValueError("Anthropic API key is required when using Anthropic provider")
        return AnthropicProvider(anthropic_key, anthropic_model)
    
    else:
        raise ValueError(f"Unknown AI provider: {provider}. Use 'openai' or 'anthropic'")


def parse_json_response(response_text: str) -> Dict:
    """Parse JSON from AI response, handling markdown code blocks."""
    import re
    
    # First try: direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.warning(f"Direct JSON parse failed: {e}")
    
    # Second try: extract from markdown code block
    try:
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning(f"Markdown extraction failed: {e}")
    
    # Third try: find JSON object with regex
    try:
        # Look for {...} pattern
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError) as e:
        logger.warning(f"Regex extraction failed: {e}")
    
    # Last resort: log the response and raise
    logger.error(f"Could not parse AI response. First 500 chars: {response_text[:500]}")
    raise ValueError(f"Could not parse AI response as JSON: {str(e)}")
