from importlib.metadata import metadata
from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Exit, Option, Typer

package_name = metadata(__package__).get("name")
__version__ = metadata(__package__).get("version")

SETTINGS = Path.home() / ".config" / package_name / "settings.json"
SETTINGS.mkdir(parents=True, exist_ok=True)

DATA_DIR = Path.home() / ".local" / "share" / package_name
DATA_DIR.mkdir(parents=True, exist_ok=True)

INV_DIR = Path.home() / "Downloads" / package_name
INV_DIR.mkdir(parents=True, exist_ok=True)


cli = Typer(no_args_is_help=True)
console = Console()


@cli.command(no_args_is_help=True)
def company(
    number: Annotated[int, Option(help="Number of companies", show_default=False)],
) -> None:
    """Generate synthetic company"""
    from . import generate

    console.print(f"Generating {number} of companies")
    for count in range(number):
        console.print(f"Generating company number {count + 1}...")
        company = generate.company()
        console.print(company)
    raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice(
    number: Annotated[int, Option(help="Number of invoices", show_default=False)],
    output: Annotated[str | None, Option(help="Output directory")] = INV_DIR,
) -> None:
    """Generate synthetic invoice"""
    console.print(f"Generating {number} of invoices")
    console.print(f"Output file: {output}")
    raise Exit(0)


@cli.callback(invoke_without_command=True)
def callback(
    settings: Annotated[bool | None, Option("--settings", help="Show program settings")] = None,
    version: Annotated[bool | None, Option("--version", help="Show program version")] = None,
) -> None:
    """Generate synthetic invoice"""
    if version:
        console.print(f"Version: [green]{__version__}[/green]")
        raise Exit(0)
    elif settings:
        from .settings import settings

        console.print(str(settings))
        raise Exit(0)


if __name__ == "__main__":
    cli()
