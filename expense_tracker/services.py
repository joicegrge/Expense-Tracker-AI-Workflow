"""Core Expense Tracker operations."""

from pathlib import Path

from .models import Expense
from .storage import DEFAULT_EXPENSES_PATH, load_expenses, save_expenses
from .validation import (
    parse_amount_to_paise,
    validate_category,
    validate_date,
    validate_expense_id,
)

_NOTE_UNSET = object()


class ExpenseNotFoundError(LookupError):
    """Raised when a valid expense ID does not exist in the store."""


def add_expense(
    amount: str,
    category: str,
    date: str,
    note: str | None = None,
    *,
    storage_path: str | Path = DEFAULT_EXPENSES_PATH,
) -> Expense:
    """Validate and persist a new expense, returning the created object."""
    amount_paise = parse_amount_to_paise(amount)
    validated_category = validate_category(category)
    validated_date = validate_date(date)
    if note is not None and not isinstance(note, str):
        raise ValueError("Note must be a string or None.")

    expense = Expense(
        amount_paise=amount_paise,
        category=validated_category,
        date=validated_date,
        note=note,
    )
    expenses = load_expenses(storage_path)
    expenses.append(expense)
    save_expenses(expenses, storage_path)
    return expense


def list_expenses(
    *,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    storage_path: str | Path = DEFAULT_EXPENSES_PATH,
) -> list[Expense]:
    """Return expenses matching optional category and inclusive date filters."""
    category_key = validate_category(category).casefold() if category is not None else None
    start = validate_date(start_date) if start_date is not None else None
    end = validate_date(end_date) if end_date is not None else None

    if start is not None and end is not None and start > end:
        raise ValueError("Start date must be on or before end date.")

    expenses = load_expenses(storage_path)
    return [
        expense
        for expense in expenses
        if (category_key is None or expense.category.casefold() == category_key)
        and (start is None or expense.date >= start)
        and (end is None or expense.date <= end)
    ]


def summarize_by_category(
    *, storage_path: str | Path = DEFAULT_EXPENSES_PATH
) -> dict[str, int]:
    """Return paise totals by case-insensitive category, using first spelling."""
    totals: dict[str, int] = {}
    category_keys: dict[str, str] = {}

    for expense in load_expenses(storage_path):
        key = expense.category.casefold()
        display_category = category_keys.setdefault(key, expense.category)
        totals[display_category] = totals.get(display_category, 0) + expense.amount_paise

    return totals


def summarize_by_month(*, storage_path: str | Path = DEFAULT_EXPENSES_PATH) -> dict[str, int]:
    """Return total integer paise grouped by calendar month in YYYY-MM format."""
    totals: dict[str, int] = {}
    for expense in load_expenses(storage_path):
        month = expense.date[:7]
        totals[month] = totals.get(month, 0) + expense.amount_paise

    return totals


def edit_expense(
    expense_id: str,
    *,
    amount: str | None = None,
    category: str | None = None,
    date: str | None = None,
    note: str | None | object = _NOTE_UNSET,
    storage_path: str | Path = DEFAULT_EXPENSES_PATH,
) -> Expense:
    """Update supplied expense fields while retaining its original ID."""
    validated_id = validate_expense_id(expense_id)
    expenses = load_expenses(storage_path)
    expense_index = _find_expense_index(expenses, validated_id)
    current = expenses[expense_index]

    updated_amount = (
        parse_amount_to_paise(amount) if amount is not None else current.amount_paise
    )
    updated_category = (
        validate_category(category) if category is not None else current.category
    )
    updated_date = validate_date(date) if date is not None else current.date
    updated_note = current.note if note is _NOTE_UNSET else note
    if updated_note is not None and not isinstance(updated_note, str):
        raise ValueError("Note must be a string or None.")

    updated = Expense(
        amount_paise=updated_amount,
        category=updated_category,
        date=updated_date,
        note=updated_note,
        id=current.id,
    )
    expenses[expense_index] = updated
    save_expenses(expenses, storage_path)
    return updated


def delete_expense(
    expense_id: str, *, storage_path: str | Path = DEFAULT_EXPENSES_PATH
) -> Expense:
    """Delete and return an expense identified by its ID."""
    validated_id = validate_expense_id(expense_id)
    expenses = load_expenses(storage_path)
    expense_index = _find_expense_index(expenses, validated_id)
    deleted = expenses.pop(expense_index)
    save_expenses(expenses, storage_path)
    return deleted


def _find_expense_index(expenses: list[Expense], expense_id: str) -> int:
    for index, expense in enumerate(expenses):
        if expense.id == expense_id:
            return index

    raise ExpenseNotFoundError(f"Expense with ID '{expense_id}' was not found.")
