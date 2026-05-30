# Agent Instructions for Runalyze CLI

This project is a CLI tool designed primarily for use by AI agents. When contributing to or modifying this codebase, you **MUST** strictly adhere to the following rules:

## 1. Strict TDD (Red-Green-Refactor)
You must use a Test-Driven Development approach for all changes.
1. **Red (Failing Test)**: Write tests for the bug fix or feature *before* making any changes to the source code. Run the test and verify it fails.
2. **Green (Passing Test)**: Write the simplest implementation possible to make the failing test pass.
3. **Refactor**: Clean up the code, optimize, and remove duplication while keeping all tests green.

## 2. Use `uv` Exclusively
We use `uv` for all environment management, dependency resolution, and script execution.
*   **Running Scripts**: Always prefix script execution with `uv run` (e.g., `uv run runalyze.py`).
*   **Running Tests**: Always run tests using `uv run pytest`.
*   **Dependencies**: Manage dependencies using `uv add` or `uv pip`. Do not use standard `pip` or `venv`.

## 3. Pre-Push Lint & Format Gate
Before committing and pushing, you **MUST** run both lint and format checks and ensure they pass:

```bash
uv run ruff check src/ test_runalyze.py
uv run ruff format --check src/ test_runalyze.py
```

If `ruff format --check` reports files would be reformatted, run `uv run ruff format` to auto-fix:

```bash
uv run ruff format src/ test_runalyze.py
```

Never push code that fails these checks — CI enforces the same gates and will reject unlinted/unformatted code.

## 4. AI-First CLI Design
Since this CLI is consumed by agents, the design must prioritize machine readability:
*   **Machine-Readable Output**: Default to outputting structured JSON (`json.dumps`). Avoid pretty-printing tables or interactive prompts unless explicitly requested.
*   **Clear Error Handling**: Exit with appropriate non-zero status codes on failure. Output errors to `stderr` in a clear, consistent format.
