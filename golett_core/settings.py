from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Core settings for the Golett application.
    
    Uses pydantic-settings to load from environment variables or .env file.
    """
    pydantic_mode: Literal["strict", "lax"] = "strict"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Single, reusable instance of the settings
settings = Settings() 