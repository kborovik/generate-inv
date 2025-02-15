from importlib.metadata import metadata
from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Exit, Option, Typer

__version__ = metadata(__package__).get("version")
package_name = metadata(__package__).get("name")

ENV_FILE = Path.home() / ".config" / package_name / "settings.env"
ENV_FILE.parent.mkdir(parents=True, exist_ok=True)

DB_FILE = Path.home() / ".local" / "share" / package_name / f"{package_name}.db"
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

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

    for count in range(number):
        console.print(f"Generating company number {count + 1} out of {number}")
        company = generate.company()
        console.print(company)
    raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice_items(
    number: Annotated[int, Option(help="Number of invoice items", show_default=False)],
) -> None:
    """Generate synthetic invoice items (5 items per run)"""
    from . import generate

    for count in range(number):
        console.print(f"Generating invoice item number {count + 1} out of {number}")
        invoice_items = generate.invoice_items(quantity=5)
        console.print(invoice_items)
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


@cli.command(no_args_is_help=True)
def settings(
    list: Annotated[bool | None, Option("--list", help="List program settings")] = None,
    save: Annotated[bool | None, Option("--save", help="Save program settings")] = None,
) -> None:
    """List or save program settings"""
    from .settings import list_settings, save_settings

    if list:
        list_settings()
    if save:
        save_settings()
        console.print(f"Saved program settings to the file {ENV_FILE}")

    raise Exit(0)


@cli.callback(invoke_without_command=True)
def callback(
    version: Annotated[bool | None, Option("--version", help="Show program version")] = None,
) -> None:
    """Generate synthetic invoice"""
    if version:
        console.print(f"Version: [green]{__version__}[/green]")
        raise Exit(0)


if __name__ == "__main__":
    cli()
