# Expense Tracker Project Instructions

## Project overview

Build a small command-line expense tracker with Python and local JSON storage. Required features are adding, listing/filtering, summarizing, editing, and deleting expenses, with clear input errors. Keep AI workflow deliverables and the usage log in the repository as described in the assignment. Optional MCP integrations and custom commands are out of scope.

## Technology stack

- Python 3.13.0.
- JSON using Python's standard library for local persistent storage.
- `unittest` from the Python standard library for tests.
- Ruff for linting; use it as a development tool, not a runtime dependency.

## Commands

Run from the project root in PowerShell:

- Run the CLI: `python -m expense_tracker`
- Run tests: `python -m unittest discover -s tests -v`
- Lint: `ruff check .`

## Planned folder structure

```text
.
|-- expense_tracker/       # CLI, expense operations, and JSON storage
|-- tests/                 # Unit tests
|-- data/                  # Local expense JSON file; keep user data untracked
|-- .agents/skills/        # Assignment skills, to be added later
|-- .githooks/             # Assignment hook, to be added later
|-- docs/                  # AI usage log and reflection
|-- README.md              # Setup and usage instructions
|-- AGENTS.md              # Project rules
```

## Code style

- Use four spaces for indentation and descriptive `snake_case` names.
- Keep CLI handling, expense logic, and JSON file access in small, focused functions.
- Validate input at the boundary and report actionable errors without tracebacks for expected invalid input.
- Use only the standard library at runtime; add a development tool only when the project needs it.
- Keep persisted JSON readable and handle missing or malformed files explicitly.

## Testing guidelines

- Use `unittest`; write at least eight meaningful unit tests, including edge cases, as required by the assignment.
- Cover normal operations and invalid input, including negative amounts, invalid dates, and unknown expense IDs.
- Use temporary directories/files for storage tests so tests never alter a user's data.
- Run the full test command after changes to application behavior and report failures honestly.

## Never

- Never commit API keys, passwords, tokens, or other secrets.
- Never commit personal expense data or generated local data files.
- Never assume input or stored JSON is valid; validate it and handle errors clearly.
- Never add a runtime dependency for functionality available in the Python standard library.

## Definition of Done

A change is done when the requested behavior is implemented, relevant tests pass, `ruff check .` passes, expected invalid input produces clear errors, and the diff has been reviewed. For a project submission, include the required README, AI workflow deliverables, usage log, reflection, and clean meaningful commit history.
