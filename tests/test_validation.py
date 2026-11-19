"""Tests for Expense Tracker input validation."""

import unittest
from uuid import uuid1, uuid4

from expense_tracker.validation import (
    parse_amount_to_paise,
    validate_category,
    validate_date,
    validate_expense_id,
)


class ParseAmountToPaiseTests(unittest.TestCase):
    def test_converts_whole_rupees_to_paise(self) -> None:
        self.assertEqual(parse_amount_to_paise("12"), 1200)

    def test_converts_one_decimal_place_to_paise(self) -> None:
        self.assertEqual(parse_amount_to_paise("12.3"), 1230)

    def test_converts_two_decimal_places_to_paise(self) -> None:
        self.assertEqual(parse_amount_to_paise("12.34"), 1234)

    def test_converts_large_amount_without_rounding(self) -> None:
        self.assertEqual(
            parse_amount_to_paise("123456789012345678901234567890.12"),
            12345678901234567890123456789012,
        )

    def test_trims_surrounding_whitespace(self) -> None:
        self.assertEqual(parse_amount_to_paise("  12.34  "), 1234)

    def test_rejects_zero_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            parse_amount_to_paise("0")

    def test_rejects_negative_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive number"):
            parse_amount_to_paise("-1.00")

    def test_rejects_more_than_two_decimal_places(self) -> None:
        with self.assertRaisesRegex(ValueError, "at most two decimal places"):
            parse_amount_to_paise("1.234")

    def test_rejects_non_numeric_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive number"):
            parse_amount_to_paise("twelve")

    def test_rejects_non_string_amount(self) -> None:
        with self.assertRaisesRegex(ValueError, "provided as text"):
            parse_amount_to_paise(12)  # type: ignore[arg-type]


class ValidateDateTests(unittest.TestCase):
    def test_accepts_valid_date_and_preserves_input(self) -> None:
        value = "2024-02-29"
        self.assertEqual(validate_date(value), value)

    def test_rejects_impossible_calendar_date(self) -> None:
        with self.assertRaisesRegex(ValueError, "valid calendar date"):
            validate_date("2025-02-30")

    def test_rejects_date_with_non_padded_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            validate_date("2025-2-03")

    def test_rejects_date_with_extra_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            validate_date("2025-02-03 ")


class ValidateCategoryTests(unittest.TestCase):
    def test_preserves_category_spelling_and_whitespace(self) -> None:
        value = "  FoOd  "
        self.assertEqual(validate_category(value), value)

    def test_rejects_empty_category(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            validate_category("")

    def test_rejects_whitespace_only_category(self) -> None:
        with self.assertRaisesRegex(ValueError, "whitespace only"):
            validate_category(" \t\n")


class ValidateExpenseIdTests(unittest.TestCase):
    def test_accepts_canonical_uuid4_id_and_preserves_input(self) -> None:
        value = str(uuid4())
        self.assertEqual(validate_expense_id(value), value)

    def test_rejects_malformed_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical UUID4"):
            validate_expense_id("not-an-id")

    def test_rejects_non_uuid4_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical UUID4"):
            validate_expense_id(str(uuid1()))

    def test_rejects_noncanonical_uppercase_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical UUID4"):
            validate_expense_id(str(uuid4()).upper())


if __name__ == "__main__":
    unittest.main()
