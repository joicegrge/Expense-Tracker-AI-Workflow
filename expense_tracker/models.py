"""Expense data model."""

from dataclasses import dataclass, field
from uuid import uuid4


def _new_expense_id() -> str:
    """Generate a unique string ID for an expense."""
    return str(uuid4())


@dataclass
class Expense:
    """Represent one expense using an amount stored in integer paise."""

    amount_paise: int
    category: str
    date: str
    note: str | None = None
    id: str = field(default_factory=_new_expense_id)
