"""Database tests for the invoice generator.

Cody instructions:
- Use SQLAlchemy v2.0 and above
- Use sQLAlchemy ORM Unit Work pattern
- Use SQLite for the database
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from data import INVOICE_ITEMS
from generate_inv import DB_FILE
from generate_inv.db import DbInvoiceItems

DB_ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=True)


def test_write_invoice_item():
    with Session(DB_ENGINE) as session:
        for item in INVOICE_ITEMS:
            db_item = DbInvoiceItems(
                item_sku=item.item_sku,
                item_info=item.item_info,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            session.add(db_item)
        session.commit()


@pytest.fixture(scope="session", autouse=True)
def cleanup_database():
    """Cleanup database after tests"""
    yield
