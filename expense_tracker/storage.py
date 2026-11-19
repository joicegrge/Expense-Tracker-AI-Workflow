"""Local JSON persistence for Expense objects."""

import json
import os
import tempfile
from collections.abc import Iterable
from pathlib import Path

from .models import Expense
from .validation import validate_category, validate_date, validate_expense_id

DEFAULT_EXPENSES_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.json"
_REQUIRED_FIELDS = {"id", "amount_paise", "category", "date"}
_ALLOWED_FIELDS = _REQUIRED_FIELDS | {"note"}


class StorageError(ValueError):
    """Raised when expense data cannot safely be read or written."""


def load_expenses(path: str | Path = DEFAULT_EXPENSES_PATH) -> list[Expense]:
    """Load expenses from JSON, creating an empty store if the file is missing."""
    file_path = Path(path)
    if not file_path.exists():
        _write_records_atomically([], file_path)
        return []

    return _load_existing_file(file_path)


def save_expenses(
    expenses: Iterable[Expense], path: str | Path = DEFAULT_EXPENSES_PATH
) -> None:
    """Atomically save expenses, refusing to replace an invalid existing store."""
    file_path = Path(path)
    records = [_expense_to_record(expense, index) for index, expense in enumerate(expenses)]

    if file_path.exists():
        _load_existing_file(file_path)

    _write_records_atomically(records, file_path)


def _load_existing_file(path: Path) -> list[Expense]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            records = json.load(stream)
    except json.JSONDecodeError as error:
        raise StorageError(f"Expense data in '{path}' is not valid JSON.") from error
    except UnicodeDecodeError as error:
        raise StorageError(f"Expense data in '{path}' is not valid UTF-8 text.") from error
    except OSError as error:
        raise StorageError(f"Could not read expense data from '{path}': {error}") from error

    if not isinstance(records, list):
        raise StorageError("Expense data must be a JSON array.")

    return [_record_to_expense(record, index) for index, record in enumerate(records)]


def _record_to_expense(record: object, index: int) -> Expense:
    if not isinstance(record, dict):
        raise StorageError(f"Expense record {index} must be a JSON object.")

    keys = set(record)
    missing_fields = _REQUIRED_FIELDS - keys
    unknown_fields = keys - _ALLOWED_FIELDS
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise StorageError(f"Expense record {index} is missing required fields: {missing}.")
    if unknown_fields:
        unknown = ", ".join(sorted(unknown_fields))
        raise StorageError(f"Expense record {index} has unknown fields: {unknown}.")

    expense_id = record["id"]
    amount_paise = record["amount_paise"]
    category = record["category"]
    expense_date = record["date"]
    note = record.get("note")

    try:
        validate_expense_id(expense_id)
        validate_category(category)
        validate_date(expense_date)
    except ValueError as error:
        raise StorageError(f"Expense record {index} has an invalid field: {error}") from error

    if type(amount_paise) is not int or amount_paise <= 0:
        raise StorageError(
            f"Expense record {index} amount_paise must be a positive integer."
        )
    if note is not None and not isinstance(note, str):
        raise StorageError(f"Expense record {index} note must be a string or null.")

    return Expense(
        amount_paise=amount_paise,
        category=category,
        date=expense_date,
        note=note,
        id=expense_id,
    )


def _expense_to_record(expense: Expense, index: int) -> dict[str, object]:
    if not isinstance(expense, Expense):
        raise StorageError(f"Item {index} to save must be an Expense object.")

    record = {
        "id": expense.id,
        "amount_paise": expense.amount_paise,
        "category": expense.category,
        "date": expense.date,
        "note": expense.note,
    }
    _record_to_expense(record, index)
    return record


def _write_records_atomically(records: list[dict[str, object]], path: Path) -> None:
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(records, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

        os.replace(temporary_path, path)
    except (OSError, TypeError, ValueError) as error:
        raise StorageError(f"Could not safely write expense data to '{path}': {error}") from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
