"""Interactive command-line interface for the Expense Tracker."""

from pathlib import Path

from .models import Expense
from .services import (
    ExpenseNotFoundError,
    add_expense,
    delete_expense,
    edit_expense,
    list_expenses,
    summarize_by_category,
    summarize_by_month,
)
from .storage import DEFAULT_EXPENSES_PATH

_MENU = """
Expense Tracker
1. Add an expense
2. List all expenses
3. Filter expenses by category
4. Filter expenses by date range
5. Show spending by category
6. Show spending by month
7. Edit an expense
8. Delete an expense
9. Exit
"""


def main(storage_path: str | Path = DEFAULT_EXPENSES_PATH) -> None:
    """Run the interactive Expense Tracker menu."""
    print("Welcome to Expense Tracker.")

    while True:
        print(_MENU)
        try:
            choice = input("Choose an option (1-9): ").strip()
            if choice == "9":
                print("Goodbye!")
                return

            _dispatch_choice(choice, storage_path)
        except (EOFError, KeyboardInterrupt):
            print("\nInput ended. Exiting Expense Tracker.")
            return
        except (ValueError, ExpenseNotFoundError) as error:
            print(f"Error: {error}")


def _dispatch_choice(choice: str, storage_path: str | Path) -> None:
    handlers = {
        "1": _add_expense,
        "2": _list_all_expenses,
        "3": _filter_by_category,
        "4": _filter_by_date_range,
        "5": _show_category_summary,
        "6": _show_month_summary,
        "7": _edit_expense,
        "8": _delete_expense,
    }
    handler = handlers.get(choice)
    if handler is None:
        print("Please choose a number from 1 to 9.")
        return

    handler(storage_path)


def _add_expense(storage_path: str | Path) -> None:
    print("\nAdd an expense")
    amount = input("Amount in rupees: ")
    category = input("Category: ")
    expense_date = input("Date (YYYY-MM-DD): ")
    note_text = input("Note (optional; press Enter to skip): ")
    note = note_text if note_text else None

    expense = add_expense(
        amount,
        category,
        expense_date,
        note,
        storage_path=storage_path,
    )
    print(f"Added expense {expense.id}: {_format_money(expense.amount_paise)}")


def _list_all_expenses(storage_path: str | Path) -> None:
    _print_expenses(list_expenses(storage_path=storage_path))


def _filter_by_category(storage_path: str | Path) -> None:
    category = input("Category to filter by: ")
    expenses = list_expenses(category=category, storage_path=storage_path)
    _print_expenses(expenses)


def _filter_by_date_range(storage_path: str | Path) -> None:
    start_date = input("Start date (YYYY-MM-DD, blank for no lower bound): ").strip()
    end_date = input("End date (YYYY-MM-DD, blank for no upper bound): ").strip()
    if not start_date and not end_date:
        print("Enter at least one date boundary to filter expenses.")
        return

    expenses = list_expenses(
        start_date=start_date or None,
        end_date=end_date or None,
        storage_path=storage_path,
    )
    _print_expenses(expenses)


def _show_category_summary(storage_path: str | Path) -> None:
    totals = summarize_by_category(storage_path=storage_path)
    if not totals:
        print("No expenses to summarize.")
        return

    print("\nSpending by category")
    for category, total_paise in totals.items():
        print(f"{category}: {_format_money(total_paise)}")


def _show_month_summary(storage_path: str | Path) -> None:
    totals = summarize_by_month(storage_path=storage_path)
    if not totals:
        print("No expenses to summarize.")
        return

    print("\nSpending by month")
    for month, total_paise in totals.items():
        print(f"{month}: {_format_money(total_paise)}")


def _edit_expense(storage_path: str | Path) -> None:
    print("\nEdit an expense (leave amount, category, or date blank to keep it)")
    expense_id = input("Expense ID: ").strip()
    amount = input("New amount in rupees (blank to keep): ")
    category = input("New category (blank to keep): ")
    expense_date = input("New date (YYYY-MM-DD, blank to keep): ")

    print("Note action: Keep / Change / Clear")
    note_action = input("Choose a note action: ").strip().casefold()
    updates: dict[str, str | None] = {
        "amount": amount or None,
        "category": category or None,
        "date": expense_date or None,
    }

    if note_action == "change":
        updates["note"] = input("New note: ")
    elif note_action == "clear":
        updates["note"] = None
    elif note_action != "keep":
        raise ValueError("Choose Keep, Change, or Clear for the note.")

    expense = edit_expense(expense_id, storage_path=storage_path, **updates)
    print(f"Updated expense {expense.id}.")


def _delete_expense(storage_path: str | Path) -> None:
    expense_id = input("Expense ID to delete: ").strip()
    expense = delete_expense(expense_id, storage_path=storage_path)
    print(f"Deleted expense {expense.id} ({_format_money(expense.amount_paise)}).")


def _print_expenses(expenses: list[Expense]) -> None:
    if not expenses:
        print("No matching expenses found.")
        return

    print("\nExpenses")
    for expense in expenses:
        note = expense.note if expense.note is not None else "-"
        print(
            f"ID: {expense.id} | Date: {expense.date} | "
            f"Category: {expense.category} | "
            f"Amount: {_format_money(expense.amount_paise)} | Note: {note}"
        )


def _format_money(amount_paise: int) -> str:
    """Format integer paise as rupees without floating-point conversion."""
    rupees, paise = divmod(amount_paise, 100)
    return f"₹{rupees:,}.{paise:02d}"


if __name__ == "__main__":
    main()
