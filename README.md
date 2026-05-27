# Runalyze CLI

A modern CLI tool to interact with the Runalyze API.

## Features
- **Modern CLI**: Built with `typer` for a clean, intuitive interface with subcommands.
- **Robust API Client**: Dedicated `RunalyzeClient` with support for:
  - Authentication via token.
  - Automatic Hydra pagination.
  - Rate limiting and retries (backoff mechanism).
  - Proper error handling with custom exceptions.
- **Improved Code Quality**: Refactored into modular components (`client.py`, `utils.py`, `runalyze.py`).
- **Comprehensive Testing**: Extensive test suite with high coverage using `pytest` and `responses`.

## Installation

This project uses `uv` for package management.

```bash
uv sync
```

## Configuration

Set your Runalyze API token as an environment variable or in a `.env` file:

```bash
export RUNALYZE_AUTH_TOKEN=your_token_here
```

You can also override the base URL for testing:

```bash
export RUNALYZE_BASE_URL=https://runalyze.com
```

## Usage

Use the `--help` flag to see available commands:

```bash
uv run runalyze.py --help
```

### Examples

**List activities:**
```bash
uv run runalyze.py activity list
```

**Get a specific activity:**
```bash
uv run runalyze.py activity get 12345
```

**Export an activity:**
```bash
uv run runalyze.py activity export 12345 fit
```

**Create a metric:**
```bash
uv run runalyze.py metrics create heartRateRest value=60
```

## Testing

Run tests with coverage:

```bash
uv run pytest --cov=runalyze --cov=client --cov=utils
```
