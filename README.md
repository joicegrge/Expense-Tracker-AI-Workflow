# Expense Tracker

A Python command-line application for recording and reviewing personal expenses. It stores expense data locally as JSON and displays INR amounts. The project targets Python 3.13.

## Features

- Add expenses with an amount, category, date, and optional note.
- List all expenses or filter by category and date range.
- Summarize spending by category or calendar month.
- Edit or delete expenses by their ID.
- Validate amounts, dates, categories, and expense IDs, with readable errors for invalid input.
- Persist expenses locally in a JSON file.

## Technology Stack

- Python 3.13
- JSON file storage
- `unittest` for automated tests
- Ruff for linting
- Runtime functionality uses only the Python standard library. Ruff is a development tool and must be installed in the Python environment used to run it.

## Project Structure

```text
.
├── .agents/
│   └── skills/
│       ├── add-feature/
│       │   └── SKILL.md
│       └── test-generator/
│           └── SKILL.md
├── expense_tracker/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   ├── storage.py
│   └── validation.py
├── tests/
│   ├── test_services.py
│   ├── test_storage.py
│   └── test_validation.py
├── .gitignore
├── AGENTS.md
└── README.md
```

The `data/` directory is created when the application first needs its default store. The local expense file is ignored by Git.

## Setup

In Windows PowerShell, clone the repository and enter the cloned directory. Replace the placeholders with your repository URL and the folder created by `git clone`:

```powershell
git clone <repository-url>
cd <repository-folder>
```

Verify that Python 3.13 is available through the Windows Python Launcher:

```powershell
py -3.13 --version
```

The application has no third-party runtime dependencies and does not require a virtual environment or package installation.

## Running the Application

From the project root, run:

```powershell
py -3.13 -m expense_tracker
```

The application displays a numbered menu. Enter the number of an option and follow the prompts. Select **9** to exit. Pressing Ctrl+C or reaching end-of-input also exits gracefully.

## Usage Guide

The menu has nine options:

1. **Add an expense** — enter the amount in rupees, category, date, and an optional note. For example: amount `245.75`, category `Groceries`, date `2025-05-10`, note `Weekly shop`. Press Enter at the note prompt to leave it empty.
2. **List all expenses** — display each expense, including its ID, date, category, amount, and note.
3. **Filter expenses by category** — enter a category to match without regard to letter case. The original category spelling remains displayed.
4. **Filter expenses by date range** — enter a start date and an end date. Both are inclusive. Either boundary may be left blank for an open-ended range, but at least one is required.
5. **Show spending by category** — show totals in paise converted to rupees for display. Category spelling variants are combined without regard to case; the first encountered spelling is used as the label.
6. **Show spending by month** — show totals grouped by calendar month in `YYYY-MM` format.
7. **Edit an expense** — enter its displayed ID. Leave the amount, category, or date blank to keep that value. For the note, choose **Keep**, **Change**, or **Clear**. Choosing Change prompts for the replacement note.
8. **Delete an expense** — enter its displayed ID. The expense is deleted immediately; the CLI does not ask for a second confirmation.
9. **Exit** — close the application.

Dates must use `YYYY-MM-DD`, for example `2025-05-10`. Amounts are entered as positive rupee values with up to two decimal places. The application stores them as integer paise and formats them as rupees with two decimal places when displaying them.

Invalid input, malformed stored data, and unknown IDs produce an error message and return to the menu.

## Data Storage

The default JSON file is `data/expenses.json`, created when needed. Expenses persist locally between runs. The file contains the expense records used by the application; it is excluded from Git to keep personal data out of the repository. Do not add personal expense records to this README.

## Running Tests

From the project root, run:

```powershell
py -3.13 -m unittest discover -s tests -v
```

The tests use temporary storage for file-based cases so they do not alter the default expense file.

## Running Ruff

From the project root in Windows PowerShell, run:

```powershell
py -3.13 -m ruff check .
```

Ruff must be installed in the Python environment selected by `py`.

## Limitations and Notes

- Data is stored in one local JSON file; the application does not provide cloud synchronization or multi-device sharing.
- Amounts are handled as INR only; multiple currencies are not supported.
- The interface is an interactive numbered menu and does not provide command-line subcommands or arguments.
