from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    PYDANTIC_AI_MODEL: str = Field(
        default="claude-3-5-haiku-latest",
        description="Anthropic LLM model",
    )
    ANTHROPIC_API_KEY: str = Field(
        default=None,
        description="Anthropic API key",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        json_file=".env.json",
    )


settings = Settings()
