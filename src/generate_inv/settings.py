from sys import exit

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .__init__ import console


class Settings(BaseSettings):
    """Application settings."""

    PYDANTIC_AI_MODEL: str = Field(
        default="claude-3-5-haiku-latest",
        description="Anthropic LLM model",
    )
    ANTHROPIC_API_KEY: SecretStr = Field(
        default=None,
        description="Anthropic API key",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        json_file=".env.json",
    )


try:
    settings = Settings()
except ValidationError as error:
    console.log(f"Settings validation error: {error.json(indent=2)}")
    exit(1)
