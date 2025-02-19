from pydantic import model_validator
from sqlmodel import Field, Session, SQLModel, create_engine

from . import DB_FILE, console


class InvoiceItem(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    item_sku: str = Field(
        description="Stock Keeping Unit (SKU) number, must be 4 uppercase letters followed by 1 number",
    )
    item_info: str = Field(
        description="Item or service short information description",
    )
    quantity: int = Field(
        description="Quantity of items",
    )
    unit_price: float = Field(
        description="Price per unit",
    )
    total_price: float = Field(
        description="Total price for the item",
        default=0.0,
    )

    @model_validator(mode="after")
    def calculate_total_price(self) -> "InvoiceItem":
        self.total_price = self.quantity * self.unit_price
        return self

    @property
    def unit_price_formatted(self) -> str:
        return f"${self.unit_price:,.2f}"

    @property
    def total_price_formatted(self) -> str:
        return f"${self.total_price:,.2f}"


DB_ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)

SQLModel.metadata.create_all(DB_ENGINE, checkfirst=True)

if __name__ == "__main__":
    from . import generate

    invoice_items = generate.invoice_items(quantity=5)
    console.print(invoice_items)

    with Session(DB_ENGINE) as session:
        session.add_all(invoice_items)
        session.commit()
