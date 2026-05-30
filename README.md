# Runalyze CLI

An AI-first CLI for the [Runalyze](https://runalyze.com) API. Designed to be used by AI agents as an installable skill.

## Quick Start — Install as an Agent Skill

Copy the prompt from [`install.md`](./install.md) and paste it into your AI agent (OpenClaw, Hermes, etc.). The agent will:

1. Clone and install the CLI
2. Prompt you for your Runalyze API token
3. Verify everything works
4. Load the full command reference into context

**→ [Open install.md](./install.md) to get the prompt.**

## Features

- **AI-First Design**: All output is structured JSON — no tables, no interactive prompts.
- **Modern CLI**: Built with `typer` for a clean subcommand interface.
- **Robust API Client**: Dedicated `RunalyzeClient` with:
  - Authentication via token
  - Automatic Hydra pagination
  - Rate limiting and retries (backoff mechanism)
  - Proper error handling with custom exceptions
- **Comprehensive Testing**: Extensive test suite with high coverage using `pytest` and `responses`.

## Manual Installation

This project uses `uv` for package management.

```bash
git clone git@github.com:reynish/runalyze-cli.git
cd runalyze-cli
uv sync
```

## Configuration

Set your Runalyze API token in a `.env` file or as an environment variable:

```bash
echo "RUNALYZE_AUTH_TOKEN=your_token_here" > .env
```

Or:

```bash
export RUNALYZE_AUTH_TOKEN=your_token_here
```

You can also override the base URL for testing:

```bash
export RUNALYZE_BASE_URL=https://runalyze.com
```

## Usage

```bash
uv run runalyze-cli --help
```

### Examples

**List activities:**
```bash
uv run runalyze-cli activity list
```

**Get a specific activity:**
```bash
uv run runalyze-cli activity get 12345
```

**Export an activity:**
```bash
uv run runalyze-cli activity export 12345 fit
```

**Create a metric:**
```bash
uv run runalyze-cli metrics create heartRateRest value=60
```

## Testing

```bash
uv run pytest
```
