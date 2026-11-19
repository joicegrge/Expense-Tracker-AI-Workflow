---
name: add-feature
description: Use when the user requests a new Expense Tracker feature. Inspect the project, propose a scoped plan, wait for explicit approval, then implement and verify the approved change.
---

# Add-Feature Workflow

Use this workflow for every new feature request in the Expense Tracker project. Follow the root `AGENTS.md`; if its instructions conflict with the user's request, follow the user and explain the conflict when relevant.

## Required workflow

1. **Restate the request.** Describe the requested feature in one or two plain-language sentences. Identify the observable behavior the user expects.
2. **Inspect the project.** Read `AGENTS.md` and examine the relevant source, tests, and README before proposing changes. Identify the specific files likely to change and any files that may need to be added. Do not assume the planned structure already exists.
3. **Propose a plan.** List the implementation steps, intended files, test coverage, and relevant checks. Call out material risks and assumptions. Ask about unresolved product behavior instead of silently choosing it.
4. **Wait for approval.** Present the plan and stop. Do not edit, create, delete, or run commands that change project state until the user explicitly approves the proposed plan. If the user changes the scope, revise the plan and obtain approval for the revised plan.
5. **Implement in small steps.** After approval, make focused changes within the approved scope. Keep CLI handling, expense logic, and JSON storage concerns separated. Use Python 3.13.0, readable `snake_case` names, four-space indentation, and the standard library at runtime unless the user approves another choice.
6. **Add or update tests.** Use `unittest`. Cover the new behavior, relevant invalid input, and edge cases. Use temporary files or directories for storage tests; never use or overwrite personal expense data. Maintain the project requirement of at least eight meaningful unit tests overall.
7. **Run checks.** From the project root, run `python -m unittest discover -s tests -v` and `ruff check .`. Run any additional relevant checks specified by `AGENTS.md` or the approved plan. Do not claim a check passed unless it completed successfully.
8. **Fix and rerun.** Fix issues introduced by the implementation, then rerun the relevant checks. If a check is unavailable or fails for an unrelated existing reason, report that clearly; do not conceal or misattribute it.
9. **Summarise results.** Report the files changed, functionality added, tests and lint checks run, and their actual results. Mention any remaining limitations or decisions needed. Review the diff and ensure no secrets or personal expense data are included.

## Example: monthly expense summary

When the user asks, "Add a monthly expense summary":

1. Restate the goal as showing total spending grouped by month, and clarify which date range or output format is expected if the request does not establish it.
2. Inspect the current expense model, date parsing, summary commands, JSON storage, tests, and README. Name the exact files that appear relevant.
3. Propose the smallest plan, such as adding monthly grouping to the existing summary logic, exposing it through the CLI, testing multiple months and invalid dates, and documenting the command. Identify assumptions about month boundaries and display format.
4. Show the plan and wait for explicit approval. Do not begin coding while waiting.
5. After approval, implement in small steps, add `unittest` cases for multiple months, empty data, and relevant date edge cases, then run the full test and lint commands.
6. Fix implementation-caused failures and rerun checks. Summarise the changed files and report the actual outcomes.
