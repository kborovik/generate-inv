from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.schema import CreateTable
from sqlmodel import Session, create_engine, func, select

from . import DB_FILE, console

DB_ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)


def show_schema() -> None:
    """Show database schema"""
    inspector = inspect(DB_ENGINE)
    metadata = MetaData()

    for table_name in inspector.get_table_names():
        table = Table(table_name, metadata)

        try:
            inspector.reflect_table(table, None)
        except NoSuchTableError as table_name:
            console.print(f"Table '{table_name}' does not exist.", style="red")
            continue

        table_ddl = CreateTable(table).compile(DB_ENGINE)
        console.print(table_ddl)


def show_stats() -> None:
    """Show database statistics"""
    from rich.table import Table

    from .models import Address, Company, InvoiceItem

    with Session(DB_ENGINE) as session:
        address_count = session.scalar(select(func.count(Address.id)))
        company_count = session.scalar(select(func.count(Company.id)))
        invoice_item_count = session.scalar(select(func.count(InvoiceItem.id)))

    table = Table(title="Database Statistics")

    table.add_column("Table Name", style="green")
    table.add_column("Records Count", style="yellow")
    table.add_row("Address", str(address_count))
    table.add_row("Company", str(company_count))
    table.add_row("InvoiceItem", str(invoice_item_count))

    with console.pager(styles=True):
        console.print(table)


if __name__ == "__main__":
    show_schema()
