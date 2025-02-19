from generate_inv.types import Address, Company, InvoiceItem

COMPANIES = [
    Company(
        company_id="TEST1",
        company_name="Test Company 1",
        phone_number="+1-555-123-4567",
        email="contact@testcompany.com",
        website="https://testcompany.com",
        address_billing=Address(
            address_line1="789 Elm St",
            address_line2="Apt 5B",
            city="Toronto",
            province="ON",
            postal_code="M5A 1A1",
            country="Canada",
        ),
        address_shipping=None,
    ),
    Company(
        company_id="TEST2",
        company_name="Test Company 2",
        phone_number="+1-555-123-4567",
        email="contact@testcompany.com",
        website="https://testcompany.com",
        address_billing=Address(
            address_line1="789 Elm St",
            address_line2="Apt 5B",
            city="Toronto",
            province="ON",
            postal_code="M5A 1A1",
            country="Canada",
        ),
        address_shipping=Address(
            address_line1="789 Elm St",
            address_line2="Apt 5B",
            city="Toronto",
            province="ON",
            postal_code="M5A 1A1",
            country="Canada",
        ),
    ),
]

INVOICE_ITEMS = [
    InvoiceItem(
        item_sku="ABCD1",
        item_info="Widget Description 1",
        quantity=10,
        unit_price=10.0,
    ),
    InvoiceItem(
        item_sku="ABCD2",
        item_info="Widget Description 2",
        quantity=20,
        unit_price=20.00,
    ),
]
