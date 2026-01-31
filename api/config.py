"""
Application Configuration
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Version
    VERSION: str = "1.0.0"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Database
    DATABASE_PATH: str = "story_generator.db"

    # Video platforms
    AVAILABLE_PLATFORMS: List[str] = ["kling", "hailuo", "jimeng", "tongyi"]
    DEFAULT_PLATFORM: str = "kling"

    # Story genres
    AVAILABLE_GENRES: List[str] = [
        "drama", "comedy", "action", "sci-fi", "fantasy",
        "romance", "horror", "thriller", "documentary", "animation"
    ]

    # Limits
    MAX_EPISODES: int = 10
    MAX_CHARACTERS: int = 10
    MAX_EPISODE_DURATION: int = 300  # seconds

    # Output directory for downloaded videos
    OUTPUT_DIR: str = "./output"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
