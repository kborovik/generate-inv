from pydantic import model_validator
from sqlmodel import Field, SQLModel, create_engine

from . import DB_FILE

DB_ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)


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


SQLModel.metadata.create_all(DB_ENGINE)

if __name__ == "__main__":
    pass
