# Generate Synthetic Data

This CLI tool generates synthetic invoices for testing and development.

## Installation

## Usage

### Help

```
generate-inv --help
```

### Generate Company Data

```
(0) > generate-inv company --generate 1

Generating company number 1 out of 1
Generated company QHIA5 - Quantum Horizon Innovations. Total tokens: 3937
{
  "company_id": "QHIA5",
  "company_name": "Quantum Horizon Innovations",
  "address_billing": {
    "address_line1": "1247 Tech Valley Drive",
    "address_line2": "Suite 305",
    "city": "Toronto",
    "province": "Ontario",
    "postal_code": "M5V 2T6",
    "country": "Canada"
  },
  "address_shipping": {
    "address_line1": "1247 Tech Valley Drive",
    "address_line2": "Suite 305",
    "city": "Toronto",
    "province": "Ontario",
    "postal_code": "M5V 2T6",
    "country": "Canada"
  },
  "phone_number": "+1 (416) 555-7890",
  "email": "contact@quantumhorizon.com",
  "website": "https://www.quantumhorizon.com"
}

```