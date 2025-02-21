"""Typer CLI for generate_inv.

Cody instructions:
- Use Typer v0.15.0 and above
- Use Rich v13.0.0 and above
"""

from importlib.metadata import metadata
from pathlib import Path
from typing import Annotated

from rich.console import Console as RichConsole
from rich.traceback import install as rich_traceback
from typer import Exit, Option, Typer

__version__ = metadata(__package__).get("version")
package_name = metadata(__package__).get("name")

CONFIG_FILE = Path.home() / ".config" / package_name / "config.env"
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

DB_FILE = Path.home() / ".local" / "share" / package_name / f"{package_name}.db"
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

INV_DIR = Path.home() / "Downloads" / package_name
INV_DIR.mkdir(parents=True, exist_ok=True)

rich_traceback(show_locals=True)
console = RichConsole()

cli = Typer(no_args_is_help=True)


@cli.command(no_args_is_help=True)
def company(
    generate: Annotated[
        int | None, Option(help="Generate number of companies", show_default=False)
    ] = None,
    list: Annotated[bool | None, Option("--list", help="List Company")] = None,
) -> None:
    """Generate synthetic company"""

    if generate:
        for count in range(generate):
            console.print(f"Generating company number {count + 1} out of {generate}")
        raise Exit(0)

    elif list:
        console.print("List of companies")
        raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice_items(
    generate: Annotated[
        int | None, Option(help="Generate number of invoice items", show_default=False)
    ] = None,
    list: Annotated[bool | None, Option("--list", help="List Invoice Items")] = None,
) -> None:
    """Generate synthetic invoice items (5 items per run)"""

    if generate:
        from .invoice_items import create_invoice_items_schema, generate_invoice_items

        create_invoice_items_schema()
        for _ in range(generate):
            generate_invoice_items()
        raise Exit(0)

    elif list:
        from .invoice_items import list_invoice_items

        list_invoice_items()
        raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice(
    generate: Annotated[
        int | None, Option(help="Generate number of invoices", show_default=False)
    ] = None,
    output: Annotated[str | None, Option(help="Output directory")] = INV_DIR,
) -> None:
    """Generate synthetic invoice"""

    if generate:
        for count in range(generate):
            console.print(f"Generating invoice {count + 1} out of {generate}")
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
        console.print(f"Saved program settings to the file {CONFIG_FILE}")

    raise Exit(0)


@cli.command(no_args_is_help=True)
def db(
    stats: Annotated[bool | None, Option("--stats", help="Show database statistics")] = None,
    show_schema: Annotated[
        bool | None, Option("--show-schema", help="List database schema")
    ] = None,
    drop_schema: Annotated[
        bool | None, Option("--drop-schema", help="Drop database schema")
    ] = None,
) -> None:
    """Database operations"""
    from sqlalchemy import inspect

    from .settings import DB_ENGINE

    if stats:
        console.print(f"Database: {DB_ENGINE.url}")

    if show_schema:
        inspector = inspect(DB_ENGINE)
        for table_name in inspector.get_table_names():
            console.print(f"Table: {table_name}", style="bold blue")
            console.print(inspector.get_columns(table_name))
            console.print(f"    Unique: {inspector.get_unique_constraints(table_name)}")
            console.print(f"    Foreign Keys: {inspector.get_foreign_keys(table_name)}")
            console.print(f"    Indexes: {inspector.get_indexes(table_name)}")

    if drop_schema:
        from .invoice_items import drop_invoice_items_schema

        console.print("Dropping database schema for InvoiceItems")
        drop_invoice_items_schema()


@cli.callback(invoke_without_command=True)
def callback(
    version: Annotated[bool | None, Option("--version", help="Show program version")] = None,
) -> None:
    """Generate synthetic invoice"""
    if version:
        console.print(f"Version: [green]{__version__}[/green]")
        raise Exit(0)
