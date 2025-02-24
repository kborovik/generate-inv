from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel, model_validator
from sqlmodel import Field, SQLModel

from . import console
from .database import DB_ENGINE
from .types import Currency


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
    total_price: Decimal = Field(
        description="Total price of item",
        decimal_places=2,
        default=Decimal(0),
    )

    @model_validator(mode="after")
    def calculate_totals(self) -> "InvoiceItem":
        self.total_price = self.quantity * self.unit_price
        return self

    @property
    def unit_price_formatted(self) -> str:
        return f"${self.unit_price:,.2f} " + self.currency.value

    @property
    def total_price_formatted(self) -> str:
        return f"${self.total_price:,.2f} " + self.currency.value


class Address(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    address_line1: str = Field(
        description="Address Line 1, Required",
        unique=True,
    )
    address_line2: str = Field(
        description="Address Line 2, Optional",
    )
    city: str = Field(
        description="Canada City Name",
    )
    province: str = Field(
        description="Canada Province Name",
    )
    postal_code: str = Field(
        description="Canada Postal Code",
    )
    country: str = Field(
        description="Country Name",
        default="Canada",
    )


class Company(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    company_id: str = Field(
        description="Human readable Company ID, must be random 6 uppercase letters followed by random 3 numbers. Example: ABCDEF123",
        unique=True,
    )
    company_name: str = Field(
        description="Company name",
        unique=True,
    )
    address_billing_id: int | None = Field(
        description="Company billing address",
        foreign_key="address.id",
    )
    address_shipping_id: int | None = Field(
        description="Company shipping address",
        default=None,
        foreign_key="address.id",
    )
    phone_number: str = Field(
        description="Phone number. The phone number must be in North American Numbering Plan (NANP) format. Example: +1 (416) 456-7890",
    )
    email: str = Field(
        description="Email address, Example: example@example.com",
    )
    website: str = Field(
        description="Company website URL, Example: https://www.example.com",
    )


class Invoice(BaseModel):
    invoice_number: str = Field(
        description="Unique invoice identifier",
    )
    issue_date: datetime = Field(
        description="Date when invoice was issued",
        default_factory=lambda: datetime.now(),
    )
    payment_terms: datetime = Field(
        description="Payment terms number of days from issue date",
        default=30,
    )
    due_date: datetime = Field(
        description="Due date for payment",
        default_factory=lambda: datetime.now() + timedelta(days=30),
    )
    supplier: Company = Field(
        description="The name of the supplier company organization.",
    )
    customer: Company = Field(
        description="The address of the supplier company organization.",
    )
    line_items: list[InvoiceItem] = Field(
        description="List of items or services being billed",
        default_factory=list,
    )
    tax_rate: Decimal = Field(
        description="Tax rate applied to the invoice line_items expressed as a decimal",
        decimal_places=2,
        default=Decimal("0.13"),
    )
    currency: Currency = Field(
        description="Currency of invoice",
        default=Currency.CAD,
    )
    tax_total: Decimal = Field(
        description="Total tax amount",
        decimal_places=2,
        default=Decimal("0.0"),
    )
    subtotal: Decimal = Field(
        description="Subtotal of invoice line_items",
        decimal_places=2,
        default=Decimal("0.0"),
    )
    total: Decimal = Field(
        description="Total of invoice line_items plus tax",
        decimal_places=2,
        default=Decimal("0.0"),
    )

    @model_validator(mode="after")
    def calculate_totals(self) -> "Invoice":
        self.subtotal = sum(item.total_price for item in self.line_items)
        self.tax_total = self.subtotal * self.tax_rate
        self.total = self.subtotal + self.tax_total
        return self

    @property
    def tax_total_formatted(self) -> str:
        return f"${self.tax_total:,.2f} " + self.currency.value

    @property
    def subtotal_formatted(self) -> str:
        return f"${self.subtotal:,.2f} " + self.currency.value

    @property
    def total_formatted(self) -> str:
        return f"${self.total:,.2f} " + self.currency.value

    @property
    def tax_rate_formatted(self) -> str:
        return f"{self.tax_rate * Decimal(100)}" + "%"


def create_db_schema() -> bool:
    """Create or migrate database schema"""
    try:
        SQLModel.metadata.create_all(DB_ENGINE)
        return True
    except Exception as error:
        console.print(error)
        return False


def drop_db_schema() -> bool:
    """Drop database schema"""
    try:
        SQLModel.metadata.drop_all(DB_ENGINE)
        return True
    except Exception as error:
        console.print(error)
        return False
