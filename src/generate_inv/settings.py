import os
import sys

import dotenv

from .__init__ import CONFIG_FILE, DB_FILE, INV_DIR, console

dotenv.load_dotenv(CONFIG_FILE)

PYDANTIC_AI_MODEL = os.getenv("PYDANTIC_AI_MODEL", "claude-3-5-haiku-latest")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

settings = {
    "PYDANTIC_AI_MODEL": PYDANTIC_AI_MODEL,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
}

if not ANTHROPIC_API_KEY:
    console.log(
        "[red]"
        "ANTHROPIC_API_KEY is not set. "
        f"Set it in the [yellow]{CONFIG_FILE}[/yellow] file "
        "or [yellow]`export ANTHROPIC_API_KEY=anthropic_api_key`[/yellow]."
        "[/red]"
    )
    sys.exit(1)


def save_settings():
    for key, value in settings.items():
        dotenv.set_key(CONFIG_FILE, key, value)


def list_settings():
    console.print("[blue]Configuration:[/blue]")
    console.print(f"Configuration File: [green]{CONFIG_FILE}[/green]")
    console.print(f"Database File: [green]{DB_FILE}[/green]")
    console.print(f"Invoice Output: [green]{INV_DIR}[/green]")
    console.print("[blue]Settings:[/blue]")
    for key, value in settings.items():
        console.print(f"{key}=[green]{value}[/green]")
