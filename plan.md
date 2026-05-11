# Runalyze CLI Improvement Plan

This document outlines a plan to improve the code quality, maintainability, and testing of the Runalyze CLI tool (`runalyze.py`) and its test suite (`test_runalyze.py`).

## 1. Migrate from `urllib` to `requests`
The current implementation uses Python's built-in `urllib` to make HTTP requests. While this avoids external dependencies, it leads to verbose and less readable code, especially when handling JSON and HTTP errors.

**Action:** Replace `urllib` with the `requests` library.
*   Simplifies JSON serialization and deserialization.
*   Provides cleaner error handling (e.g., `response.raise_for_status()`).
*   Easier to mock in tests using libraries like `responses`.

## 2. Adopt a Modern CLI Framework
The current `argparse` implementation in `main()` is very long and manual. As more API endpoints are added, the parser setup will become increasingly difficult to manage.

**Action:** Migrate the CLI definition to a modern framework like `typer` or `click`.
*   **Typer:** Uses Python type hints to automatically generate CLI arguments and options, resulting in much cleaner and less boilerplate code.
*   Groups subcommands (e.g., `activity`, `metrics`, `equipment`) logically using decorators.

## 3. Refactor Code Structure and Error Handling
The script currently mixes API client logic, CLI argument parsing, and command execution in a single file, and relies heavily on `sys.exit(1)` for error handling.

**Action:** 
*   **Extract API Client:** Create a dedicated `RunalyzeClient` class to handle authentication, HTTP requests, and endpoint-specific methods. This isolates the network logic from the CLI presentation.
*   **Improve Error Handling:** Instead of calling `sys.exit()` deeply within `make_request`, raise custom exceptions (e.g., `RunalyzeAPIError`). Catch these exceptions at the top level of the CLI execution to print user-friendly error messages.
*   **Configurability:** Allow the `BASE_URL` to be overridden via an environment variable (e.g., `RUNALYZE_BASE_URL`) for easier testing or staging environments.

## 4. Enhance Test Coverage (`test_runalyze.py`)
The current tests cover basic token loading and request mocking.

**Action:**
*   Update tests to reflect the migration to `requests` (using `responses` or patching `requests.Session`).
*   **CLI Tests:** Add tests using the `CliRunner` (from `click.testing` or `typer.testing`) to verify that CLI commands execute correctly and return the expected output.
*   **Edge Cases:** Expand `test_parse_props` to handle more edge cases and malformed inputs.
*   **Error State Testing:** Add tests to ensure that API errors are gracefully caught and formatted for the user without exposing raw stack traces.

## 5. Add Pagination and Rate Limiting Support
The Runalyze API may return paginated results for `list` commands, and could enforce rate limits.

**Action:**
*   Implement automatic pagination handling in the `RunalyzeClient` for `list` operations.
*   Add logic to respect HTTP `429 Too Many Requests` responses and implement a backoff/retry mechanism.
