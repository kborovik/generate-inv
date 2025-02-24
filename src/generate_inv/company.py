"""Generate synthetic company data"""

import json

from pydantic_ai import Agent
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from . import console
from .address import Address
from .database import DB_ENGINE
from .models import Company
from .settings import ANTHROPIC_MODEL


def generate_company() -> bool:
    """Generate synthetic company data"""

    with Session(DB_ENGINE) as session:
        statement = select(Company.company_id, Company.company_name)
        present_companies = session.exec(statement).all()

    system_prompt = (
        "You are creative synthetic data generation assistant. "
        "Your goal in life is to generate unique realistic Company profile data. "
    )

    json_schema = json.dumps(Company.model_json_schema())

    user_prompt = (
        f"Generate 5 unique Company profiles. "
        f"Use the following JSON schema to generate Company profile: <json_schema>{json_schema}</json_schema>. "
        "Do not use <company_id> or <company_name> that are present in the database. "
        f"Here is the list of companies in the current database: <database_data>{present_companies}</database_data>. "
    )

    agent = Agent(
        model=ANTHROPIC_MODEL,
        result_type=list[Company],
        deps_type=None,
        system_prompt=[system_prompt],
        model_settings={
            "temperature": 1.0,
        },
    )

    try:
        console.print("Waiting for AI to generate company data...")
        result = agent.run_sync(user_prompt=user_prompt)
    except Exception as error:
        console.print(error)
        return False

    new, dup = 0, 0
    with Session(DB_ENGINE) as session:
        random_addresses = session.exec(select(Address).order_by(func.random()).limit(2)).all()

        for company in result.data:
            company.address_billing_id = random_addresses[0].id
            company.address_shipping_id = random_addresses[1].id

            session.add(company)
            try:
                session.commit()
                new += 1
            except IntegrityError:
                session.rollback()
                dup += 1

    console.print(f"New companies: {new}, duplicate companies: {dup}")

    return True


def list_companies():
    """List companies from database"""
    from rich.table import Table

    with Session(DB_ENGINE) as session:
        statement = select(Company)
        companies = session.exec(statement).all()

    table = Table(title="Companies")

    table.add_column("Company ID", style="cyan")
    table.add_column("Company Name", style="green", no_wrap=True)
    table.add_column("Phone Number", style="blue")
    table.add_column("Email", style="magenta")
    table.add_column("Website", style="yellow")

    for item in companies:
        table.add_row(
            item.company_id,
            item.company_name,
            item.phone_number,
            item.email,
            item.website,
        )

    with console.pager(styles=True):
        console.print(table)


if __name__ == "__main__":
    pass
