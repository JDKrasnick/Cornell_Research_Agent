"""Configuration settings for the Cornell Lab Matchmaker.

Handles API keys, model settings, and database paths.
"""

#AI_Generated

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    semantic_scholar_api_key: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

    # Database paths
    database_path: Path = ROOT_DIR / os.getenv("DATABASE_PATH", "data/database.sqlite")
    vector_store_path: Path = ROOT_DIR / os.getenv("VECTOR_STORE_PATH", "data/embeddings")

    # Data paths
    raw_data_path: Path = ROOT_DIR / "data" / "raw"
    processed_data_path: Path = ROOT_DIR / "data" / "processed"

    # Model settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o")

    class Config:
        arbitrary_types_allowed = True


settings = Settings()