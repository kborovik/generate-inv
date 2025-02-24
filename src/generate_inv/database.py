from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.schema import CreateTable
from sqlmodel import create_engine

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
    console.print("Database statistics")


if __name__ == "__main__":
    show_schema()
