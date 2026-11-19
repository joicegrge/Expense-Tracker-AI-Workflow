"""Input validation for Expense Tracker values."""

import re
from datetime import date
from decimal import Decimal, localcontext
from uuid import UUID

_AMOUNT_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]{1,2})?")
_DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def parse_amount_to_paise(value: str) -> int:
    """Parse a positive INR amount and return its value in integer paise."""
    if not isinstance(value, str):
        raise ValueError("Amount must be provided as text.")  # noqa: TRY004

    amount_text = value.strip()
    if not _AMOUNT_PATTERN.fullmatch(amount_text):
        raise ValueError(
            "Amount must be a positive number with at most two decimal places."
        )

    amount = Decimal(amount_text)
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with localcontext() as context:
        context.prec = max(len(amount.as_tuple().digits) + 2, context.prec)
        return int(amount * 100)


def validate_date(value: str) -> str:
    """Return a date string if it is a real date in YYYY-MM-DD format."""
    if not isinstance(value, str) or not _DATE_PATTERN.fullmatch(value):
        raise ValueError("Date must use YYYY-MM-DD format.")

    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Date must be a valid calendar date.") from error

    return value


def validate_category(value: str) -> str:
    """Return a non-blank category without changing its original spelling."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Category cannot be empty or whitespace only.")

    return value


def validate_expense_id(value: str) -> str:
    """Return a canonical lowercase UUID4 expense ID, or raise ValueError."""
    if not isinstance(value, str):
        raise ValueError("Expense ID must be a canonical UUID4 string.")  # noqa: TRY004

    try:
        parsed_id = UUID(value)
    except ValueError as error:
        raise ValueError("Expense ID must be a canonical UUID4 string.") from error

    if parsed_id.version != 4 or str(parsed_id) != value:
        raise ValueError("Expense ID must be a canonical UUID4 string.")

    return value
