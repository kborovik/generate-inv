"""Generate synthetic invoice data"""

from random import randint

from sqlmodel import Session, func, select

# from . import console
from .company import Company
from .database import DB_ENGINE
from .invoice_item import InvoiceItem
from .models import Invoice


def generate_invoice() -> Invoice:
    """Generate synthetic invoice data"""

    invoice_number = f"INV-{randint(100, 999)}"

    with Session(DB_ENGINE) as session:
        companies = session.exec(select(Company).order_by(func.random()).limit(2)).all()
        line_items = session.exec(
            select(InvoiceItem).order_by(func.random()).limit(randint(1, 10))
        ).all()

    invoice = Invoice(
        invoice_number=invoice_number,
        supplier=companies[0],
        customer=companies[1],
        line_items=line_items,
    )

    return invoice


def write_invoice(invoice: Invoice) -> bytes:
    """Create an invoice PDF"""

    from jinja2 import Environment, FileSystemLoader
    from weasyprint import HTML

    template_dir = Path(__file__).parent
    template = Environment(loader=FileSystemLoader(template_dir)).get_template("invoice.j2")

    # Render the template with the invoice data
    html_content = template.render(
        invoice_number=invoice.invoice_number,
        issue_date=invoice.issue_date.strftime("%Y-%m-%d"),
        due_date=invoice.due_date.strftime("%Y-%m-%d"),
        supplier=invoice.supplier,
        customer=invoice.customer,
        currency=invoice.currency.value,
        line_items=invoice.line_items,
        tax_rate=invoice.tax_rate_formatted,
        tax_total=invoice.tax_total_formatted,
        subtotal=invoice.subtotal_formatted,
        total=invoice.total_formatted,
    )

    pdf_bytes = HTML(string=html_content).write_pdf()

    return pdf_bytes


if __name__ == "__main__":
    from pathlib import Path

    from . import INV_DIR, console

    invoice = generate_invoice()
    console.print(invoice)
    pdf_bytes = write_invoice(invoice)
    Path(INV_DIR).joinpath(f"{invoice.invoice_number}.pdf").write_bytes(pdf_bytes)
