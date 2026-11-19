"""Tests for local JSON persistence of Expense objects."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from expense_tracker.models import Expense
from expense_tracker.storage import StorageError, load_expenses, save_expenses


class ExpenseStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)
        self.path = self.directory / "expenses.json"

    def make_expense(
        self,
        *,
        amount_paise: int = 1250,
        category: str = "Food",
        date: str = "2025-01-15",
        note: str | None = "Lunch",
        expense_id: str | None = None,
    ) -> Expense:
        return Expense(
            amount_paise=amount_paise,
            category=category,
            date=date,
            note=note,
            id=expense_id or str(uuid4()),
        )

    def test_save_and_load_preserves_all_expense_fields(self) -> None:
        expense = self.make_expense()

        save_expenses([expense], self.path)
        loaded = load_expenses(self.path)

        self.assertEqual(loaded, [expense])
        self.assertEqual(loaded[0].id, expense.id)
        self.assertEqual(loaded[0].amount_paise, 1250)
        self.assertEqual(loaded[0].category, "Food")
        self.assertEqual(loaded[0].date, "2025-01-15")
        self.assertEqual(loaded[0].note, "Lunch")

    def test_round_trip_preserves_missing_optional_note_as_none(self) -> None:
        expense = self.make_expense(note=None)

        save_expenses([expense], self.path)

        self.assertIsNone(load_expenses(self.path)[0].note)

    def test_load_defaults_missing_note_to_none(self) -> None:
        record = self.record_for(self.make_expense())
        record.pop("note")
        self.write_json([record])

        loaded = load_expenses(self.path)

        self.assertIsNone(loaded[0].note)

    def test_save_and_load_multiple_expenses(self) -> None:
        expenses = [self.make_expense(), self.make_expense(category="Transport")]

        save_expenses(expenses, self.path)

        self.assertEqual(load_expenses(self.path), expenses)

    def test_missing_file_creates_empty_store_and_returns_empty_list(self) -> None:
        missing_path = self.directory / "nested" / "expenses.json"

        loaded = load_expenses(missing_path)

        self.assertEqual(loaded, [])
        self.assertEqual(json.loads(missing_path.read_text(encoding="utf-8")), [])

    def test_malformed_json_raises_and_leaves_file_unchanged(self) -> None:
        original = b'{"expenses":'
        self.path.write_bytes(original)

        with self.assertRaisesRegex(StorageError, "not valid JSON"):
            load_expenses(self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_non_array_json_raises_and_leaves_file_unchanged(self) -> None:
        original = b'{"expenses": []}'
        self.path.write_bytes(original)

        with self.assertRaisesRegex(StorageError, "JSON array"):
            load_expenses(self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_unknown_record_fields_raise_and_leave_file_unchanged(self) -> None:
        record = self.record_for(self.make_expense())
        record["extra"] = "unexpected"
        original = json.dumps([record]).encode("utf-8")
        self.path.write_bytes(original)

        with self.assertRaisesRegex(StorageError, "unknown fields"):
            load_expenses(self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_boolean_amount_is_rejected_and_file_is_unchanged(self) -> None:
        record = self.record_for(self.make_expense())
        record["amount_paise"] = True
        original = json.dumps([record]).encode("utf-8")
        self.path.write_bytes(original)

        with self.assertRaisesRegex(StorageError, "positive integer"):
            load_expenses(self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_save_refuses_to_overwrite_malformed_existing_json(self) -> None:
        original = b"not json"
        self.path.write_bytes(original)

        with self.assertRaisesRegex(StorageError, "not valid JSON"):
            save_expenses([self.make_expense()], self.path)

        self.assertEqual(self.path.read_bytes(), original)

    def test_failed_atomic_replacement_preserves_existing_valid_file(self) -> None:
        original_expenses = [self.make_expense()]
        save_expenses(original_expenses, self.path)
        original_bytes = self.path.read_bytes()

        with (
            patch("expense_tracker.storage.os.replace", side_effect=OSError("blocked")),
            self.assertRaisesRegex(StorageError, "Could not safely write"),
        ):
            save_expenses([self.make_expense(category="Transport")], self.path)

        self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertEqual(list(self.directory.glob("*.tmp")), [])

    def test_save_creates_parent_directories(self) -> None:
        nested_path = self.directory / "nested" / "store" / "expenses.json"
        expense = self.make_expense()

        save_expenses([expense], nested_path)

        self.assertEqual(load_expenses(nested_path), [expense])

    def record_for(self, expense: Expense) -> dict[str, object]:
        return {
            "id": expense.id,
            "amount_paise": expense.amount_paise,
            "category": expense.category,
            "date": expense.date,
            "note": expense.note,
        }

    def write_json(self, value: object) -> None:
        self.path.write_text(json.dumps(value), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
