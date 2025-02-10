import os

import dotenv

from .__init__ import ENV_FILE, console

dotenv.load_dotenv(ENV_FILE)

PYDANTIC_AI_MODEL = os.getenv("PYDANTIC_AI_MODEL", "claude-3-5-haiku-latest")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def save_settings():
    dotenv.set_key(ENV_FILE, "PYDANTIC_AI_MODEL", PYDANTIC_AI_MODEL)
    dotenv.set_key(ENV_FILE, "ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)


def list_settings():
    console.print(f"PYDANTIC_AI_MODEL=[green]{PYDANTIC_AI_MODEL}[/green]")
    console.print(f"ANTHROPIC_API_KEY=[green]{ANTHROPIC_API_KEY}[/green]")
