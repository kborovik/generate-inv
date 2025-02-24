"""Generate synthetic invoice item data"""

import json

from pydantic_ai import Agent
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from . import console
from .database import DB_ENGINE
from .models import InvoiceItem
from .settings import ANTHROPIC_MODEL


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


if __name__ == "__main__":
    generate_invoice_items()
