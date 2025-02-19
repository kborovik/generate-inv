"""
This module provides functionality for generating synthetic invoice and company data.

It uses Pydantic models and AI agents to create realistic test data for the invoice OCR system.
Key components:
- Company generation with unique IDs and Canadian addresses
- Invoice generation with line items
- Integration with database to avoid duplicates

Cody Instructions:
- Use Pydantic v2.0.0 and above
"""

import json
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel

from .__init__ import console
from .models import InvoiceItem
from .settings import ANTHROPIC_API_KEY, PYDANTIC_AI_MODEL
from .types import Company, Invoice

anthropic_model = AnthropicModel(
    model_name=PYDANTIC_AI_MODEL,
    api_key=ANTHROPIC_API_KEY,
)


@dataclass
class CompanyDeps:
    companies: list[tuple[str, str]] = None

    def __post_init__(self):
        # companies = db.find_company("")
        # self.companies = [(company.company_id, company.company_name) for company in companies]
        pass


company_agent = Agent(
    model=anthropic_model,
    model_settings={"temperature": 0.7},
    deps_type=CompanyDeps,
    result_type=Company,
    system_prompt=(
        "You are a helpful assistant that generates company information. "
        "Do not use company names or company IDs that are already in the database. "
    ),
)


@company_agent.system_prompt
def company_agent_system_prompt(context: RunContext[CompanyDeps]) -> str:
    companies = context.deps.companies
    return f"List of companies in database: {companies}"


def company() -> Company:
    """Generate synthetic company"""
    schema = json.dumps(Company.model_json_schema())

    user_prompt = (
        "Generate creative real life company names."
        "Generate unique company ID based on company name. "
        "Generate unique Canada postal billing address. "
        "Generate unique Canada postal shipping address. "
        "Generate unique email address based on company name. "
        "Generate unique website URL based on company name. "
        f"Use JSON schema: {schema} "
    )

    deps = CompanyDeps()

    try:
        result = company_agent.run_sync(user_prompt=user_prompt, deps=deps)
    except Exception as error:
        console.log(error)
        raise error

    console.print(
        f"Generated company {result.data.company_id} - {result.data.company_name}. Total tokens: {result._usage.total_tokens}"
    )

    return result.data


@dataclass
class InvoiceItemsDeps:
    invoice_items: list[tuple[str, str]] = None

    def __post_init__(self):
        # invoice_items = db.find_invoice_item("")
        # self.invoice_items = [
        #     (invoice_item.item_sku, invoice_item.item_info) for invoice_item in invoice_items
        # ]
        pass


invoice_agent = Agent(
    model=anthropic_model,
    deps_type=InvoiceItemsDeps,
    result_type=list[InvoiceItem],
    system_prompt=(
        "You are a helpful assistant that generates invoice line items. "
        "Do not use item_sku or item_info that are already in database. "
    ),
)


@invoice_agent.system_prompt
def invoice_agent_system_prompt(context: RunContext[InvoiceItemsDeps]) -> str:
    invoice_items = context.deps.invoice_items
    return f"List of item_sku and item_info in database: {invoice_items}"


def invoice_items(quantity: int = 5) -> list[InvoiceItem]:
    schema = json.dumps(InvoiceItem.model_json_schema())

    user_prompt = (
        f"Generate {quantity} computer equipment invoice line items. "
        "Avoid duplicate item_sku and item_info. "
        f"Use JSON schema for each invoice line item: {schema}"
    )

    deps = InvoiceItemsDeps()

    result = invoice_agent.run_sync(user_prompt=user_prompt, deps=deps)

    console.print(
        f"Generated {quantity} invoice line items. Total tokens: {result._usage.total_tokens}"
    )

    return result.data


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
