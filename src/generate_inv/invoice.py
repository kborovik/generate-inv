"""
Cody Instructions:
- Use Pydantic v2.0.0 and above
"""

from datetime import datetime, timedelta

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, model_validator

# from . import console
from .company import Company
from .invoice_items import InvoiceItem
from .types import Currency


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
    tax_rate: int = Field(
        description="Tax rate applied to the invoice line_items expressed as a percentage",
        default=13,
    )
    currency: Currency = Field(
        description="Currency of invoice",
        default=Currency.CAD,
    )
    tax_total: float = Field(
        description="Total tax amount",
        default=0.0,
    )
    subtotal: float = Field(
        description="Subtotal of invoice line_items",
        default=0.0,
    )
    total: float = Field(
        description="Total of invoice line_items plus tax",
        default=0.0,
    )

    @model_validator(mode="after")
    def calculate_totals(self) -> "Invoice":
        self.subtotal = sum(item.total_price for item in self.line_items)
        self.tax_total = self.subtotal * (self.tax_rate / 100)
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


def invoice(invoice: Invoice) -> bytes:
    from weasyprint import HTML

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader("src/invoice_ocr"))
    template = env.get_template("invoice.j2")

    # Render the template with the invoice data
    html_content = template.render(
        invoice_number=invoice.invoice_number,
        issue_date=invoice.issue_date.strftime("%Y-%m-%d"),
        due_date=invoice.due_date.strftime("%Y-%m-%d"),
        supplier=invoice.supplier,
        customer=invoice.customer,
        currency=invoice.currency.value,
        line_items=invoice.line_items,
        tax_rate=invoice.tax_rate,
        tax_total=invoice.tax_total_formatted,
        subtotal=invoice.subtotal_formatted,
        total=invoice.total_formatted,
    )

    # html_file = Path(f"data/{invoice.invoice_number}.html")
    # html_file.write_text(html_content)
    # Convert HTML to PDF
    pdf_bytes = HTML(string=html_content).write_pdf()

    return pdf_bytes


if __name__ == "__main__":
    pass
