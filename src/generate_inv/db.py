from sqlalchemy import Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from . import DB_FILE

ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=True, echo_pool=True)


class Base(DeclarativeBase):
    pass


class Address(Base):
    """Address table mirrors Address model in the types.py file."""

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(7), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Canada")


class Company(Base):
    """Company table mirrors Company model in the types.py file."""

    __tablename__ = "companies"

    company_id: Mapped[str] = mapped_column(String(5), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str] = mapped_column(String(255), nullable=False)

    # Foreign key relationships for addresses
    address_billing_fk: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    address_shipping_fk: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=True)

    # Relationship definitions
    address_billing: Mapped["Address"] = relationship("Address", foreign_keys=[address_billing_fk])
    address_shipping: Mapped["Address"] = relationship(
        "Address", foreign_keys=[address_shipping_fk]
    )


class InvoiceItems(Base):
    """Invoice items table mirrors InvoiceItem model in the types.py file."""

    __tablename__ = "invoice_items"

    item_sku: Mapped[str] = mapped_column(String(5), primary_key=True)
    item_info: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float(precision=2), nullable=False)
    total_price: Mapped[float] = mapped_column(Float(precision=2), nullable=False)


if __name__ == "__main__":
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
