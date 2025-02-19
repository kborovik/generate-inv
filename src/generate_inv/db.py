"""Database schema for the invoice generator.

Cody instructions:
- Use SQLAlchemy v2.0 and above
- Use sQLAlchemy ORM Unit Work pattern
- Use SQLite for the database
"""

from sqlalchemy import Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from . import DB_FILE

DB_ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)


class DbBase(DeclarativeBase):
    pass


class DbAddress(DbBase):
    """Address table mirrors Address model in the types.py file."""

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address_line1: Mapped[str] = mapped_column(String, nullable=False)
    address_line2: Mapped[str] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    province: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False, default="Canada")


class DbCompany(DbBase):
    """Company table mirrors Company model in the types.py file."""

    __tablename__ = "companies"

    company_id: Mapped[str] = mapped_column(String, primary_key=True)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[str] = mapped_column(String, nullable=False)

    # Foreign key relationships for addresses
    address_billing_fk: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    address_shipping_fk: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=True)

    # Relationship definitions
    address_billing: Mapped["DbAddress"] = relationship(
        DbAddress, foreign_keys=[address_billing_fk]
    )
    address_shipping: Mapped["DbAddress"] = relationship(
        DbAddress, foreign_keys=[address_shipping_fk]
    )


class DbInvoiceItems(DbBase):
    """Invoice items table mirrors InvoiceItem model in the types.py file."""

    __tablename__ = "invoice_items"

    item_sku: Mapped[str] = mapped_column(String, primary_key=True)
    item_info: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float(precision=2), nullable=False)


DbBase.metadata.create_all(DB_ENGINE)


if __name__ == "__main__":
    pass
