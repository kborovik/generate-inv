import json

from pydantic_ai import Agent, UserError
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import Field, Session, SQLModel, func, select

from . import console
from .settings import ANTHROPIC_MODEL, DB_ENGINE


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


def generate_addresses() -> bool:
    """Generate 5 invoice items and store in database"""

    with Session(DB_ENGINE) as session:
        statement = select(Address.address_line1)
        present_addresses = session.exec(statement).all()

    system_prompt = (
        "You are creative synthetic data generation assistant. "
        "Your goal in life is to generate unique realistic postal addresses for the Canadian postal system. "
    )

    json_schema = json.dumps(Address.model_json_schema())

    user_prompt = (
        f"Generate 5 unique Canadian postal addresses. "
        f"Use JSON schema for each invoice line item: <json_schema>{json_schema}</json_schema>. "
        "Do not use item_sku or item_info that are present in the database. "
        f"Here is the list of item_sku and item_info in the current database: <database_data>{present_addresses}</database_data>. "
    )

    agent = Agent(
        model=ANTHROPIC_MODEL,
        result_type=list[Address],
        deps_type=None,
        system_prompt=[system_prompt],
        model_settings={
            "temperature": 1.0,
        },
    )

    try:
        console.print("Waiting for AI to generate addresses...")
        result = agent.run_sync(user_prompt=user_prompt)
    except UserError as error:
        console.print(error)
        return False

    console.print(
        f"Generated {len(result.data)} addresses. Request tokens: {result._usage.request_tokens}. Response tokens: {result._usage.response_tokens}."
    )

    new, dup = 0, 0
    with Session(DB_ENGINE) as session:
        for item in result.data:
            session.add(item)
            try:
                session.commit()
                new += 1
            except IntegrityError:
                session.rollback()
                dup += 1
                continue

    console.print(f"New addresses: {new}, duplicate addresses: {dup}")

    return True


def get_random_address(number: int = 1) -> list[Address]:
    """Get random address from database"""

    with Session(DB_ENGINE) as session:
        address = select(Address).order_by(func.random()).limit(number)
        present_addresses = session.exec(address).all()

    return present_addresses


def list_addresses() -> None:
    """List addresses from database"""

    from rich.table import Table

    with Session(DB_ENGINE) as session:
        statement = select(Address)
        addresses = session.exec(statement).all()

    table = Table(title="Addresses")

    table.add_column("Address Line 1", style="green")
    table.add_column("Address Line 2", style="green")
    table.add_column("City", style="blue")
    table.add_column("Province", style="magenta")
    table.add_column("Postal Code", style="yellow")

    for item in addresses:
        table.add_row(
            item.address_line1,
            item.address_line2,
            item.city,
            item.province,
            item.postal_code,
        )
    with console.pager(styles=True):
        console.print(table)


def create_address_schema() -> bool:
    """Create or migrate database schema"""
    try:
        SQLModel.metadata.create_all(DB_ENGINE)
        return True
    except OperationalError as error:
        console.print(f"Database connection error: {error}", style="red")
        return False
    except Exception as error:
        console.print(f"Failed to create schema: {error}", style="red")
        return False


def drop_address_schema() -> bool:
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
    get_random_address()
