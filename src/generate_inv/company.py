"""Company Model
Cody Instructions:
- Use Python 3.12+
- Use Pydantic v2.0+
"""

import json

from pydantic_ai import Agent
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import Field, Session, SQLModel, select

from . import console
from .settings import ANTHROPIC_MODEL, DB_ENGINE


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
    address_billing: int | None = Field(
        description="Company billing address",
        foreign_key="address.id",
    )
    address_shipping: int | None = Field(
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


def generate_company() -> bool:
    """Generate synthetic company data"""
    from .address import get_random_address

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

    console.print(
        f"Generated {len(result.data)} companies. Request tokens: {result._usage.request_tokens}. Response tokens: {result._usage.response_tokens}."
    )

    new, dup = 0, 0
    with Session(DB_ENGINE) as session:
        for company in result.data:
            random_addresses = get_random_address(number=2)
            company.address_billing = random_addresses[0].id
            company.address_shipping = random_addresses[1].id

            try:
                session.add(company)
                session.commit()
                new += 1
            except IntegrityError:
                session.rollback()
                dup += 1

    console.print(f"New companies: {new}, duplicate companies: {dup}")

    return True


def list_companies() -> bool:
    """List companies from database

    Returns:
        bool: True if companies were listed successfully, False otherwise
    """
    try:
        from rich.table import Table

        with Session(DB_ENGINE) as session:
            statement = select(Company)
            companies = session.exec(statement).all()

        if not companies:
            console.print("No companies found in database", style="yellow")
            return True

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
        return True

    except OperationalError as error:
        console.print(f"Database connection error: {error}", style="red")
        return False
    except Exception as error:
        console.print(f"Failed to list companies: {error}", style="red")
        return False


def create_company_schema() -> bool:
    """Create or migrate database schema

    Returns:
        bool: True if schema was created/updated successfully, False otherwise
    """
    try:
        SQLModel.metadata.create_all(DB_ENGINE)
        return True
    except OperationalError as error:
        console.print(f"Database connection error: {error}", style="red")
        return False
    except Exception as error:
        console.print(f"Failed to create schema: {error}", style="red")
        return False


def drop_company_schema() -> bool:
    """Drop database schema"""
    try:
        SQLModel.metadata.drop_all(DB_ENGINE)
        return True
    except OperationalError as error:
        console.print(f"Database connection error: {error}", style="red")
        return False
    except Exception as error:
        console.print(f"Failed to drop schema: {error}", style="red")
        return False


if __name__ == "__main__":
    pass
