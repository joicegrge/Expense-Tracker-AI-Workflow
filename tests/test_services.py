"""Tests for core Expense Tracker service operations."""

import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from expense_tracker.models import Expense
from expense_tracker.services import (
    ExpenseNotFoundError,
    add_expense,
    delete_expense,
    edit_expense,
    list_expenses,
    summarize_by_category,
    summarize_by_month,
)
from expense_tracker.storage import save_expenses


class ExpenseServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.path = Path(self.temporary_directory.name) / "expenses.json"

    def make_expense(
        self,
        amount_paise: int,
        category: str,
        date: str,
        note: str | None = None,
        expense_id: str | None = None,
    ) -> Expense:
        return Expense(
            amount_paise=amount_paise,
            category=category,
            date=date,
            note=note,
            id=expense_id or str(uuid4()),
        )

    def seed(self, *expenses: Expense) -> None:
        save_expenses(expenses, self.path)

    def test_add_expense_converts_amount_and_stores_fields(self) -> None:
        expense = add_expense(
            "12.34", "Food", "2025-01-15", "Lunch", storage_path=self.path
        )

        self.assertEqual(expense.amount_paise, 1234)
        self.assertEqual(expense.category, "Food")
        self.assertEqual(expense.date, "2025-01-15")
        self.assertEqual(expense.note, "Lunch")
        self.assertEqual(list_expenses(storage_path=self.path), [expense])

    def test_add_expense_accepts_missing_optional_note(self) -> None:
        expense = add_expense("10", "Food", "2025-01-15", storage_path=self.path)

        self.assertIsNone(expense.note)
        self.assertEqual(list_expenses(storage_path=self.path), [expense])

    def test_add_expense_rejects_invalid_amount_without_writing(self) -> None:
        with self.assertRaises(ValueError):
            add_expense("0", "Food", "2025-01-15", storage_path=self.path)

        self.assertFalse(self.path.exists())

    def test_list_expenses_returns_all_records(self) -> None:
        expenses = (
            self.make_expense(500, "Food", "2025-01-15"),
            self.make_expense(700, "Travel", "2025-02-20"),
        )
        self.seed(*expenses)

        self.assertEqual(list_expenses(storage_path=self.path), list(expenses))

    def test_category_filter_ignores_case_and_preserves_original_spelling(self) -> None:
        food = self.make_expense(500, "FoOd", "2025-01-15")
        travel = self.make_expense(700, "Travel", "2025-02-20")
        self.seed(food, travel)

        result = list_expenses(category="food", storage_path=self.path)

        self.assertEqual(result, [food])
        self.assertEqual(result[0].category, "FoOd")

    def test_date_range_includes_both_endpoints(self) -> None:
        before = self.make_expense(100, "Food", "2025-01-14")
        start = self.make_expense(200, "Food", "2025-01-15")
        middle = self.make_expense(300, "Food", "2025-01-16")
        end = self.make_expense(400, "Food", "2025-01-17")
        after = self.make_expense(500, "Food", "2025-01-18")
        self.seed(before, start, middle, end, after)

        result = list_expenses(
            start_date="2025-01-15",
            end_date="2025-01-17",
            storage_path=self.path,
        )

        self.assertEqual(result, [start, middle, end])

    def test_date_filter_accepts_one_open_boundary(self) -> None:
        earlier = self.make_expense(100, "Food", "2025-01-14")
        later = self.make_expense(200, "Food", "2025-01-16")
        self.seed(earlier, later)

        self.assertEqual(
            list_expenses(start_date="2025-01-15", storage_path=self.path), [later]
        )
        self.assertEqual(
            list_expenses(end_date="2025-01-15", storage_path=self.path), [earlier]
        )

    def test_date_range_rejects_start_after_end(self) -> None:
        with self.assertRaisesRegex(ValueError, "on or before"):
            list_expenses(
                start_date="2025-02-01",
                end_date="2025-01-01",
                storage_path=self.path,
            )

    def test_start_date_rejects_invalid_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            list_expenses(start_date="15-01-2025", storage_path=self.path)

    def test_start_date_rejects_impossible_calendar_date(self) -> None:
        with self.assertRaisesRegex(ValueError, "valid calendar date"):
            list_expenses(start_date="2025-02-30", storage_path=self.path)

    def test_end_date_rejects_invalid_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            list_expenses(end_date="15-01-2025", storage_path=self.path)

    def test_end_date_rejects_impossible_calendar_date(self) -> None:
        with self.assertRaisesRegex(ValueError, "valid calendar date"):
            list_expenses(end_date="2025-02-30", storage_path=self.path)

    def test_category_summary_combines_case_variants_using_first_spelling(self) -> None:
        first = self.make_expense(500, "Food", "2025-01-01")
        second = self.make_expense(250, "food", "2025-01-02")
        other = self.make_expense(300, "Rent", "2025-01-03")
        self.seed(first, second, other)

        self.assertEqual(
            summarize_by_category(storage_path=self.path),
            {"Food": 750, "Rent": 300},
        )

    def test_month_summary_groups_by_calendar_month(self) -> None:
        january_first = self.make_expense(500, "Food", "2025-01-01")
        january_later = self.make_expense(250, "Rent", "2025-01-31")
        february = self.make_expense(300, "Food", "2025-02-01")
        self.seed(january_first, january_later, february)

        self.assertEqual(
            summarize_by_month(storage_path=self.path),
            {"2025-01": 750, "2025-02": 300},
        )

    def test_empty_store_returns_empty_lists_and_summaries(self) -> None:
        self.assertEqual(list_expenses(storage_path=self.path), [])
        self.assertEqual(summarize_by_category(storage_path=self.path), {})
        self.assertEqual(summarize_by_month(storage_path=self.path), {})

    def test_edit_preserves_id_and_updates_requested_fields(self) -> None:
        original = self.make_expense(500, "Food", "2025-01-15", "Lunch")
        self.seed(original)

        updated = edit_expense(
            original.id,
            amount="23.45",
            category="Dining",
            storage_path=self.path,
        )

        self.assertEqual(updated.id, original.id)
        self.assertEqual(updated.amount_paise, 2345)
        self.assertEqual(updated.category, "Dining")
        self.assertEqual(updated.date, original.date)
        self.assertEqual(updated.note, original.note)
        self.assertEqual(list_expenses(storage_path=self.path), [updated])

    def test_edit_can_clear_optional_note(self) -> None:
        original = self.make_expense(500, "Food", "2025-01-15", "Lunch")
        self.seed(original)

        updated = edit_expense(original.id, note=None, storage_path=self.path)

        self.assertEqual(updated.id, original.id)
        self.assertIsNone(updated.note)

    def test_edit_unknown_id_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ExpenseNotFoundError, "was not found"):
            edit_expense(str(uuid4()), amount="12", storage_path=self.path)

    def test_delete_removes_and_returns_expense(self) -> None:
        target = self.make_expense(500, "Food", "2025-01-15")
        remaining = self.make_expense(700, "Travel", "2025-02-20")
        self.seed(target, remaining)

        deleted = delete_expense(target.id, storage_path=self.path)

        self.assertEqual(deleted, target)
        self.assertEqual(list_expenses(storage_path=self.path), [remaining])

    def test_delete_unknown_id_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ExpenseNotFoundError, "was not found"):
            delete_expense(str(uuid4()), storage_path=self.path)


if __name__ == "__main__":
    unittest.main()
