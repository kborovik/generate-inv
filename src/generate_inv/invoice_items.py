import json
from decimal import Decimal

from pydantic_ai import Agent, UserError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel, select

from . import console
from .settings import ANTHROPIC_MODEL, DB_ENGINE


class InvoiceItem(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    item_sku: str = Field(
        description="Stock Keeping Unit (SKU) number, must be random 6 uppercase letters followed by random 3 number. Example: ABCDEF123",
        unique=True,
        index=True,
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
    def total_price(self) -> float:
        total_price = self.quantity * self.unit_price
        return f"${total_price:,.2f}"


def generate_invoice_items() -> list[InvoiceItem]:
    """Generate 5 invoice items and store in database"""

    with Session(DB_ENGINE) as session:
        statement = select(InvoiceItem.item_sku, InvoiceItem.item_info)
        present_invoice_items = session.exec(statement).all()

    system_prompt = (
        "You are a helpful assistant that generates invoice line items. "
        "Do not use item_sku or item_info that are already in database. "
        f"List of item_sku and item_info in database: {present_invoice_items}"
    )

    user_prompt = (
        f"Generate 5 computer equipment invoice line items. "
        "Avoid duplicate item_sku and item_info. "
        f"Use JSON schema for each invoice line item: {json.dumps(InvoiceItem.model_json_schema())}"
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
        console.print("Generating invoice items...")
        result = agent.run_sync(user_prompt=user_prompt)
    except UserError as error:
        console.print(error)
        return []

    console.print(
        f"Generated {len(result.data)} invoice items. Request tokens: {result._usage.request_tokens}. Response tokens: {result._usage.response_tokens}."
    )

    new = 0
    duplicate = 0
    with Session(DB_ENGINE) as session:
        for item in result.data:
            session.add(item)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                duplicate += 1
                continue
            session.commit()
            new += 1

    console.print(f"New invoice items: {new}, duplicate invoice items: {duplicate}")

    return result.data


def create_invoice_items_schema():
    """Create or migrate database schema"""
    SQLModel.metadata.create_all(DB_ENGINE)


if __name__ == "__main__":
    # SQLModel.metadata.drop_all(DB_ENGINE)
    create_invoice_items_schema()
    generate_invoice_items()
    # get_all_invoice_items()
