"""Generate synthetic address data"""

import json

from pydantic_ai import Agent, UserError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from . import console
from .database import DB_ENGINE
from .models import Address
from .settings import ANTHROPIC_MODEL


def generate_addresses() -> bool:
    """Generate 5 invoice items and store in database"""

    with Session(DB_ENGINE) as session:
        present_addresses = session.exec(select(Address.address_line1)).all()

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


if __name__ == "__main__":
    list_addresses()
