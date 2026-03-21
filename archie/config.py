from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # AI Provider - use either "openai" or "anthropic"
    ai_provider: str = "openai"
    
    # API Keys - provide the one you're using
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # OpenAI specific settings
    openai_model: str = "gpt-4o"
    
    # Anthropic specific settings
    anthropic_model: str = "claude-sonnet-4-20250514"
    
    # GitHub settings
    github_token: str
    github_repo_owner: str
    github_repo_name: str
    repo_path: str
    webhook_secret: str
    
    # Other settings
    embeddings_model: str = "all-MiniLM-L6-v2"
    lancedb_path: str = "./.lancedb"
    graph_persist_path: str = "./.graph.pkl"
    log_level: str = "INFO"

    class Config:
        # Look for .env in the archie directory (where this config.py file is)
        env_file = str(Path(__file__).parent / ".env")
        case_sensitive = False


settings = Settings()
