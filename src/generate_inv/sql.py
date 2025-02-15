from sqlalchemy import Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .__init__ import DB_FILE


class DbBase(DeclarativeBase):
    pass


class DbInvoiceItems(DbBase):
    """Invoice items table
    Corresponds to the InvoiceItem model in the types.py file.
    """

    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_sku: Mapped[str] = mapped_column(unique=True)
    item_info: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float(precision=2), nullable=False)
    total_price: Mapped[float] = mapped_column(Float(precision=2), nullable=False)


if __name__ == "__main__":
    engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)
    DbBase.metadata.create_all(engine)
