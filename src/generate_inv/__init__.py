from importlib.metadata import version
from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Exit, Option, Typer

from . import generate

__version__ = version(__package__)

cli = Typer(no_args_is_help=True)
console = Console()

output_dir = Path.cwd() / "data"


@cli.command(no_args_is_help=True)
def company(
    number: Annotated[int, Option(help="Number of companies", show_default=False)],
) -> None:
    """Generate synthetic company"""
    console.print(f"Generating {number} of companies")
    for count in range(number):
        console.print(f"Generating company number {count + 1}...")
        company = generate.company()
        console.print(company)
    raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice(
    number: Annotated[int, Option(help="Number of invoices", show_default=False)],
    output: Annotated[str, Option(help="Output directory")] = output_dir,
) -> None:
    """Generate synthetic invoice"""
    console.print(f"Generating {number} of invoices")
    console.print(f"Output file: {output}")
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
