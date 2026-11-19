# AI Usage Log

This log summarizes the AI-assisted work completed on the Expense Tracker. Prompts below are **prompt summaries**, not exact quotations. Outputs, review findings, and actions are based on the project development history.

## 1. Project instructions and Codex skills

**Prompt summary:** Establish the project rules from the assignment, create a root `AGENTS.md`, and then create the Add-Feature Workflow and Test Generator skills in their requested locations. The user required a plan and approval before creating the instruction file and later requested only the skill files.

**AI output:** Codex prepared project guidance for Python 3.13.0, standard-library runtime code, JSON persistence, `unittest`, Ruff, code style, testing expectations, specific “Never” rules, and a Definition of Done. It then created the reusable add-feature approval workflow and a test-generation workflow using `unittest` and temporary storage.

**What was wrong or missing:** In the Add-Feature skill, the initial frontmatter skill name did not match the `add-feature` folder name; the user noticed the editor warning. The assignment also specified at least eight meaningful tests, which the root project rules needed to preserve.

**My review/action:** I supplied the Python version as 3.13.0, reviewed and approved the proposed instructions and skill content, and pointed out the skill-name warning. The skill metadata was subsequently aligned to the folder name. I kept the workflows scoped to instructions and did not ask Codex to create application functionality at this stage.

## 2. Expense model and input validation

**Prompt summary:** Build the package and Expense model first, then plan and implement validation for amounts, dates, categories, and IDs in the approved Stage 2 files only.

**AI output:** Codex created a dataclass with a generated UUID4 ID, `amount_paise`, category, date, and optional note. The validation module uses `Decimal` for exact rupee-to-paise conversion, checks positive amounts with at most two decimal places, validates real dates in `YYYY-MM-DD` format, preserves category input, and checks canonical UUID4 IDs. Validation tests cover valid and invalid values.

**What was wrong or missing:** No significant implementation issue was identified at this stage. The package entry point was intentionally left as a placeholder until the CLI stage.

**My review/action:** I approved each stage plan before implementation and checked the exact file scope. I specifically required `Decimal`, preserved input spelling, actual calendar validation, canonical UUID4 IDs, and clear `ValueError` messages. I reviewed the implementation results and requested no expansion into storage or CLI behavior during these stages.

## 3. JSON storage and persistence

**Prompt summary:** Add JSON load/save functions using the existing model and validators, with missing-file initialization, safe writes, and tests isolated from personal data.

**AI output:** Codex implemented JSON conversion between records and `Expense` objects, preserving IDs, integer paise, category, date, and optional notes. A missing store is initialized as an empty list. Writes use a temporary file and atomic replacement. Malformed JSON and invalid record structures raise clear storage errors instead of replacing the original file. The tests use temporary directories.

**What was wrong or missing:** The proposed behavior needed explicit decisions about records with a missing note and unknown fields. Those points were surfaced before implementation rather than silently assumed.

**My review/action:** I approved the plan including missing-note and strict unknown-field behavior. I required booleans to be rejected as amounts and malformed or invalid existing JSON never to be overwritten. I reviewed the two-file scope and the test results before moving to service operations.

## 4. Core service operations and date-validation tests

**Prompt summary:** Implement add, list, filter, category and monthly summaries, edit, and delete using existing model, validation, and storage modules, with temporary JSON stores in tests. Later, add tests for invalid and impossible dates in both date-filter boundaries without changing service code.

**AI output:** Codex added the service layer and tests for the operations. Category filtering ignores case. Date-range filtering includes both boundaries. Summaries keep totals in integer paise; category totals combine case-insensitively and use the first encountered spelling as the key. Editing preserves the expense ID. A private note sentinel distinguishes “leave note unchanged” from explicitly clearing it. Unknown IDs produce a clear error.

**What was wrong or missing:** The original service tests did not directly cover invalid-format and impossible calendar dates supplied as both `start_date` and `end_date` to `list_expenses()`.

**My review/action:** I decided category summary spelling should follow the first matching category encountered. After reviewing the service implementation, I requested the missing date-filter tests only, including both bounds, and instructed Codex not to modify `services.py`. The service test suite grew from 16 to 20 tests; the full suite then had 53 tests.

## 5. CLI implementation and launch scope

**Prompt summary:** Plan an interactive numbered menu that connects to the service layer, then implement the approved CLI while allowing the necessary launch-file change so `python -m expense_tracker` works.

**AI output:** Codex created the nine-option interactive menu for adding, listing, filtering, summaries, editing, deleting, and exiting. The CLI delegates business logic to services, formats paise as rupees only for display, displays IDs, and handles input, storage, and unknown-ID errors. Edit prompts allow blank fields to retain existing values and provide explicit Keep, Change, and Clear note choices.

**What was wrong or missing:** The original requested scope named only `main.py`, but `python -m expense_tracker` runs `__main__.py`. Updating only `main.py` would not launch the application as requested. The user approved expanding the file scope to include `__main__.py` as the entry point that imports and calls `main()`.

**My review/action:** I approved the two-file scope explicitly. I reviewed the complete files, requested the explicit note choices, and required service-layer business logic and integer paise internally. The CLI was demonstrated with realistic inputs for each operation, and module launch was confirmed. The full unittest suite had 53 passing tests and Ruff passed at that stage.

## 6. README documentation

**Prompt summary:** Inspect the finished project and prepare a README covering features, actual structure, setup, use, data storage, tests, Ruff, and supported limitations; create it only after plan approval. Later, make the documented commands consistently use the Python 3.13 Windows Launcher.

**AI output:** Codex wrote a README with the nine menu options, realistic add-expense input, date and amount rules, filters, note editing, local JSON path, setup placeholders for the repository URL and folder, and test/lint commands. The commands were then updated to use `py -3.13`.

**What was wrong or missing:** The environment used for the work did not have `py` available as a launcher, so the final documented `py -3.13` commands could not be claimed as verified there. The user explicitly required that limitation to be stated honestly and required the README to exclude the assignment PDF from the application tree.

**My review/action:** I asked for consistent `py -3.13` commands and kept the repository URL and folder as placeholders because there was no configured remote. I required the README to reflect the actual project, not claim stretch goals, and not include personal expense records. The full suite passed (53 tests) and Ruff passed using the available Python environment; the unavailable launcher command was not represented as verified.

## 7. Git pre-commit hook

**Prompt summary:** Add a tracked POSIX-compatible pre-commit hook that runs the full unittest suite, supports Git for Windows, blocks commits on test failure or missing Python, and demonstrate both pass and block behavior in a disposable copy.

**AI output:** Codex created `.githooks/pre-commit`, which changes to the repository root, tries `python -m unittest discover -s tests -v`, falls back to `py -3.13 -m unittest discover -s tests -v`, and exits with a clear message if Python is unavailable or tests fail. It includes the activation command `git config core.hooksPath .githooks` and was staged with executable mode preserved.

**What was wrong or missing:** The actual environment did not initially expose the Python executable through the launcher names expected by the hook. A successful claim therefore required a controlled demonstration setup, rather than assuming the hook had executed.

**My review/action:** I required a real commit attempt in a disposable repository. The hook allowed a commit when the 53 tests passed. After a temporary failing test was added in that disposable copy, the hook blocked the commit and the repository’s head did not advance. The disposable copy was removed; application files and project tests were not changed for the demonstration.

## Permissions and Approval

During development I used an ask-first workflow: Codex inspected the project and proposed a scoped plan, waited for my explicit approval, implemented the approved change, and reported the files and checks for my review before I committed. This describes how I authorized the work. The project history does not confirm a particular underlying Codex UI permission mode, so I make no claim about settings such as Auto-edit or Sandboxed.
