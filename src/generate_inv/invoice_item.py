import json
from decimal import Decimal

from pydantic_ai import Agent
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel, select, func

from . import console
from .settings import ANTHROPIC_MODEL, DB_ENGINE


class InvoiceItem(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    item_sku: str = Field(
        description="Stock Keeping Unit (SKU) number, must be random 6 uppercase letters followed by random 3 numbers. Example: ABCDEF123",
        unique=True,
    )
    item_info: str = Field(
        description="Item or service short information description",
        unique=True,
    )
    quantity: int = Field(
        description="Quantity of items",
    )
    unit_price: Decimal = Field(
        description="Price per unit",
        decimal_places=2,
    )

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price


def generate_invoice_items() -> bool:
    """Generate 5 invoice items and store in database"""

    with Session(DB_ENGINE) as session:
        statement = select(InvoiceItem.item_sku, InvoiceItem.item_info)
        present_invoice_items = session.exec(statement).all()

    system_prompt = (
        "You are creative synthetic data generation assistant. "
        "Your goal in life is to generate unique realistic invoice line items for a computer equipment shop. "
    )

    user_prompt = (
        f"Generate 5 unique computer equipment invoice line items. "
        f"Use JSON schema for each invoice line item: <json_schema>{json.dumps(InvoiceItem.model_json_schema())}</json_schema>. "
        "Do not use item_sku or item_info that are present in the database. "
        f"Here is the list of item_sku and item_info in the current database: <database_data>{present_invoice_items}</database_data>. "
    )

    agent = Agent(
        model=ANTHROPIC_MODEL,
        result_type=list[InvoiceItem],
        deps_type=None,
        system_prompt=[system_prompt],
        model_settings={
            "temperature": 1.0,
        },
    )

    try:
        console.print("Waiting for AI to generate invoice items...")
        result = agent.run_sync(user_prompt=user_prompt)
    except Exception as error:
        console.print(error)
        return False

    console.print(
        f"Generated {len(result.data)} invoice items. Request tokens: {result._usage.request_tokens}. Response tokens: {result._usage.response_tokens}."
    )

    new, dup = 0, 0
    with Session(DB_ENGINE) as session:
        for item in result.data:
            session.add(item)
            try:
                session.commit()
                new += 1
            except IntegrityError:
                session.rollback()
                dup += 1
                continue

    console.print(f"New invoice items: {new}, duplicate invoice items: {dup}")

    return True


def get_random_invoice_item(number: int = 1) -> list[InvoiceItem]:
    """Get random invoice item from database"""

    with Session(DB_ENGINE) as session:
        address = select(InvoiceItem).order_by(func.random()).limit(number)
        result = session.exec(address).all()

    return result


def list_invoice_items() -> None:
    """List invoice items from database"""
    from rich.table import Table

    with Session(DB_ENGINE) as session:
        statement = select(InvoiceItem)
        invoice_items = session.exec(statement).all()

    table = Table(title="Invoice Items")

    table.add_column("SKU", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Quantity", justify="right", style="blue")
    table.add_column("Unit Price", justify="right", style="magenta")
    table.add_column("Total Price", justify="right", style="yellow")

    for item in invoice_items:
        table.add_row(
            item.item_sku,
            item.item_info,
            str(item.quantity),
            str(item.unit_price),
            str(item.total_price),
        )
    with console.pager(styles=True):
        console.print(table)


def create_invoice_items_schema() -> bool:
    """Create or migrate database schema"""
    try:
        SQLModel.metadata.create_all(DB_ENGINE)
        return True
    except Exception as error:
        console.print(error)
        return False


def drop_invoice_items_schema() -> bool:
    """Drop database schema"""
    try:
        SQLModel.metadata.drop_all(DB_ENGINE)
        return True
    except Exception as error:
        console.print(error)
        return False


if __name__ == "__main__":
    create_invoice_items_schema()
    generate_invoice_items()
