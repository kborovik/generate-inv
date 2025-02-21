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
        description="Stock Keeping Unit (SKU) number, must be 4 uppercase letters followed by 1 number",
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
    """Generate 10 invoice items and store in database"""

    with Session(DB_ENGINE) as session:
        statement = select(InvoiceItem.item_sku, InvoiceItem.item_info)
        present_invoice_items = session.exec(statement).all()

    system_prompt = (
        "You are a creative synthetic data generator agent. "
        "Generate unique invoice line items for a computer equipment shop based on the following guidelines: "
        " - Use realistic product names and descriptions. "
        " - Double-check that all required fields are included and that the data types are correct. "
    )

    user_prompt = (
        "Generate 10 invoice items based on the following JSON schema: "
        f"<schema>{json.dumps(InvoiceItem.model_json_schema())}</schema>"
        "Do not generate invoice items that are already in the database. "
        f"Here is the list of existing invoice items: <present_invoice_items>{present_invoice_items}</present_invoice_items>"
    )

    agent = Agent(
        model=ANTHROPIC_MODEL,
        result_type=list[InvoiceItem],
        system_prompt=system_prompt,
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
