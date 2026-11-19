---
name: test-generator
description: Use when the user asks to create or improve unit tests for the Expense Tracker. Inspect existing behavior first, write focused unittest coverage, run checks, and report what each test verifies.
---

# Test Generator

Use this skill when the user asks for tests for an Expense Tracker feature, bug, or existing behavior. It can be used to add a new test module or extend tests when explicitly requested. It does not authorize changing application code.

Follow the root `AGENTS.md`. Use Python 3.13.0 and the standard-library `unittest` framework. Keep tests readable, focused, and based on observable behavior rather than private implementation details.

## Workflow

1. **Inspect before writing.** Read `AGENTS.md`, then inspect the relevant application code, existing tests, and README. Identify public functions or CLI behavior, current test conventions, files likely to add or change, and any gaps. Do not infer behavior from a feature name alone.
2. **Map scenarios.** For the requested behavior, list:
   - A normal successful scenario.
   - Invalid inputs and expected clear errors.
   - Relevant edge cases, such as empty data, boundaries, duplicates, or unknown IDs.
   - Storage behavior, if applicable, including missing or malformed JSON where relevant.
3. **Resolve uncertainty.** If expected behavior is not clear from the request, code, or project documentation, ask the user before encoding an assumption in tests. Briefly explain any assumptions that are safe and necessary.
4. **Keep scope to tests.** Create or update only the requested test files. Do not edit application code, configuration, dependencies, or existing tests unless the user explicitly requests those changes. If the tests reveal an application defect, report it and ask for authorization before changing application code.
5. **Write meaningful tests.** Use `unittest.TestCase` and descriptive test names. Each test should verify one behavior with useful assertions, including returned values, persisted results, CLI output, or clear errors as appropriate. Avoid tests that merely repeat implementation details.
6. **Isolate storage tests.** Use `tempfile.TemporaryDirectory` or `tempfile.NamedTemporaryFile` and point the storage code at the temporary location. Never read, overwrite, or commit personal expense data or the project's local data file.
7. **Explain the tests.** In the final summary, list each generated or changed test and state what behavior or case it verifies. Keep explanations specific enough that a reviewer can see the coverage at a glance.
8. **Run and report checks.** From the project root, run the relevant test module during iteration and then run the full suite with `python -m unittest discover -s tests -v`. Run `ruff check .` as specified in `AGENTS.md`. Report actual command outcomes, including unavailable tools or failures; do not claim success if a command did not pass. Do not change application code to make tests pass unless the user separately authorizes it.

## Example: tests for adding an expense

When asked to generate tests for adding an expense:

1. Inspect the add-expense implementation, date and amount validation, storage interface, existing tests, and documented CLI behavior. Determine the actual public entry point and how errors are represented.
2. Plan tests for a valid expense, a negative amount, an invalid calendar date, and any relevant boundary cases. If the behavior for zero amounts or date format is unclear, ask before deciding what the tests should expect.
3. Add tests only in the requested test file or a new focused test module. For example:
   - `test_add_expense_stores_valid_expense` verifies a valid amount, category, date, and optional note are recorded and returned as expected.
   - `test_add_expense_rejects_negative_amount` verifies a negative amount is rejected with the project's expected clear validation error and is not stored.
   - `test_add_expense_rejects_invalid_date` verifies an impossible date such as `2025-02-30` is rejected and is not stored.
   - `test_add_expense_uses_temporary_storage` verifies persistence through a temporary JSON path without touching the user's data file.
4. Run the relevant tests, the full `unittest` suite, and `ruff check .`. If a test exposes a defect in application code, report the failing test and request approval before modifying that code.
5. Summarise each test's purpose and the actual results of the commands run.
