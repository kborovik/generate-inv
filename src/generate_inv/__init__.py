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

rich_traceback(show_locals=True, max_frames=5)
console = RichConsole()

cli = Typer(no_args_is_help=True)


@cli.command(no_args_is_help=True)
def address(
    generate: Annotated[int | None, Option(help="Generate addresses", show_default=False)] = None,
    list: Annotated[bool | None, Option("--list", help="List addresses")] = None,
) -> None:
    """Generate synthetic addresses (5 items per run)"""

    from .address import create_address_schema, generate_addresses, list_addresses

    if generate:
        for count in range(generate):
            console.print(f"Generating address batch {count + 1} out of {generate}")
            create_address_schema()
            generate_addresses()
        raise Exit(0)

    elif list:
        list_addresses()
        raise Exit(0)


@cli.command(no_args_is_help=True)
def company(
    generate: Annotated[int | None, Option(help="Generate company", show_default=False)] = None,
    list: Annotated[bool | None, Option("--list", help="List Company")] = None,
) -> None:
    """Generate synthetic company"""
    from .company import create_company_schema, generate_company, list_companies

    if generate:
        for count in range(generate):
            console.print(f"Generating company batch {count + 1} out of {generate}")
            create_company_schema()
            generate_company()
        raise Exit(0)

    elif list:
        list_companies()
        raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice_item(
    generate: Annotated[
        int | None,
        Option(help="Generate invoice items", show_default=False),
    ] = None,
    list: Annotated[bool | None, Option("--list", help="List Invoice Items")] = None,
) -> None:
    """Generate synthetic invoice items (5 items per run)"""

    if generate:
        from .invoice_item import create_invoice_items_schema, generate_invoice_items

        create_invoice_items_schema()
        for count in range(generate):
            console.print(f"Generating invoice items batch {count + 1} out of {generate}")
            generate_invoice_items()
        raise Exit(0)

    elif list:
        from .invoice_item import list_invoice_items

        list_invoice_items()
        raise Exit(0)


@cli.command(no_args_is_help=True)
def invoice(
    generate: Annotated[int | None, Option(help="Generate invoices", show_default=False)] = None,
    output: Annotated[str | None, Option(help="Output directory")] = INV_DIR,
) -> None:
    """Generate synthetic invoices"""

    if generate:
        for count in range(generate):
            console.print(f"Generating invoice {count + 1} out of {generate}")
        console.print(f"Output file: {output}")
        raise Exit(0)


@cli.command(no_args_is_help=True)
def database(
    stats: Annotated[bool | None, Option("--stats", help="Show database statistics")] = None,
    create_schema: Annotated[
        bool | None, Option("--create-schema", help="Create database DDL schema")
    ] = None,
    list_schema: Annotated[
        bool | None, Option("--show-schema", help="Show database DDL schema")
    ] = None,
    drop_schema: Annotated[
        bool | None, Option("--drop-schema", help="Create database DDL schema")
    ] = None,
) -> None:
    """Database operations"""

    if stats:
        from .database import show_stats

        show_stats()
        raise Exit(0)

    elif create_schema:
        from .address import create_address_schema
        from .company import create_company_schema
        from .invoice_item import create_invoice_items_schema

        create_invoice_items_schema()
        create_address_schema()
        create_company_schema()
        console.print("Created database schema")
        raise Exit(0)

    elif list_schema:
        from .database import show_schema

        show_schema()
        raise Exit(0)

    elif drop_schema:
        from .address import drop_address_schema
        from .company import drop_company_schema
        from .invoice_item import drop_invoice_items_schema

        drop_invoice_items_schema()
        drop_company_schema()
        drop_address_schema()
        console.print("Created database schema")
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
        raise Exit(0)

    elif save:
        save_settings()
        console.print(f"Saved program settings to the file {CONFIG_FILE}")
        raise Exit(0)


@cli.callback(invoke_without_command=True)
def callback(
    version: Annotated[bool | None, Option("--version", help="Show program version")] = None,
) -> None:
    """Generate synthetic invoice"""
    if version:
        console.print(f"Version: [green]{__version__}[/green]")
        raise Exit(0)
