# Runalyze CLI — Agent Skill Installer

Copy everything inside the fenced block below and paste it into your agent (OpenClaw, Hermes, etc.) to install the Runalyze skill.

````text
# Install Runalyze CLI Skill

Install the Runalyze CLI skill so I can query and manage my Runalyze data through you.

## Step 1 — Clone and install the tool

Run the following commands to install runalyze-cli:

```bash
git clone git@github.com:reynish/runalyze-cli.git ~/skills/runalyze-cli
cd ~/skills/runalyze-cli
uv sync
```

If the directory `~/skills/runalyze-cli` already exists, pull the latest instead:

```bash
cd ~/skills/runalyze-cli && git pull && uv sync
```

Verify the installation succeeded:

```bash
uv run runalyze-cli --help
```

## Step 2 — Configure the API key

Ask me for my Runalyze API token. You can tell me:

> "I need your Runalyze API token to set up the skill. You can generate one at https://runalyze.com/api (Settings → API)."

Once I give you the token, write it into a `.env` file:

```bash
echo "RUNALYZE_AUTH_TOKEN=<token>" > ~/skills/runalyze-cli/.env
```

Then verify it works by running:

```bash
cd ~/skills/runalyze-cli && uv run runalyze-cli services
```

If you get a JSON response, the skill is ready. If you get an auth error, ask me to check the token.

## How to use this skill

All commands must be run from the `~/skills/runalyze-cli` directory, prefixed with `uv run`:

```bash
cd ~/skills/runalyze-cli && uv run runalyze-cli <command>
```

### Available commands

| Area | Command | Description |
|---|---|---|
| Activities | `activity list [--limit N]` | List activities |
| | `activity get <id> [--trackdata]` | Get a single activity (with optional GPS/HR trackdata) |
| | `activity export <id> <fmt>` | Export activity (csv, fit, fit-original, fitlog, gpx, kml, tcx) |
| | `activity share-image <id> <fmt> [--output path]` | Export social image (portrait, square) |
| | `activity upload <file>` | Upload an activity file |
| | `activity upload-status <id>` | Check upload status |
| Metrics | `metrics list <type> [--limit N]` | List health metrics |
| | `metrics get <type> <id_or_date>` | Get a specific metric |
| | `metrics create <type> key=value ...` | Create a metric |
| | `metrics update <type> <id> key=value ...` | Update a metric |
| | `metrics delete <type> <id>` | Delete a metric |
| | `metrics bulk-upload [--file path] [key=value ...]` | Bulk upload health metrics |
| | `metrics forecast` | Get menstrual cycle forecast |
| | `metrics latest` / `metrics-latest` | Get latest metrics |
| Disease | `disease list [--limit N]` | List recorded diseases / injuries |
| | `disease get <id>` | Get disease details |
| | `disease create key=value ...` | Create disease entry |
| | `disease pain-level-list <id> [--limit N]` | List pain levels for disease |
| | `disease pain-level-get <id> <pl_id>` | Get specific pain level |
| | `disease pain-level-create <id> key=value ...` | Log pain level for disease |
| Equipment | `equipment list [--limit N]` | List equipment |
| | `equipment get <id>` | Get equipment item |
| | `equipment create key=value ...` | Create equipment item |
| | `equipment update <id> key=value ...` | Update equipment item |
| | `equipment delete <id>` | Delete equipment item |
| | `equipment categories` | List equipment categories |
| | `equipment category <id>` | Get category |
| | `equipment category-create key=value ...` | Create equipment category |
| | `equipment category-update <id> key=value ...` | Update equipment category |
| | `equipment category-delete <id>` | Delete equipment category |
| | `equipment category-equipment <id>` | List equipment in category |
| Race Results | `raceresult list [--limit N]` | List race results |
| | `raceresult get <id>` | Get race result |
| | `raceresult update <id> key=value ...` | Update race result |
| | `raceresult delete <id>` | Delete race result |
| Tags | `tag list [--limit N]` | List tags |
| | `tag get <id>` | Get tag |
| Settings | `settings date-range [--limit N]` | List date ranges |
| | `settings date-range-get <id>` | Get date range |
| | `settings date-range-create key=value ...` | Create date range |
| | `settings date-range-update <id> key=value ...` | Update date range |
| | `settings date-range-delete <id>` | Delete date range |
| Stats | `statistics current` | Get current statistics |
| | `statistics prognosis` | Get race prognosis |
| System | `services` | List available API services |
| | `sync-changes key=value ...` | Sync changes |

### Metric types

Valid metric types: `bloodGlucose`, `bloodPressure`, `bodyComposition`, `bodyTemperature`, `dailyNote`, `disease`, `heartRateMax`, `heartRateRest`, `hrv`, `menstrualCycle`, `mental`, `sleep`

### Important notes

- All output is JSON. Parse it to extract fields you need.
- Binary exports (FIT files) are returned as base64-encoded strings with an `"encoding": "base64"` key.
- Text exports (GPX, TCX, KML) are returned as plain strings in the `"content"` key.
- When creating or updating resources, pass properties as `key=value` arguments. JSON values are supported (e.g., `value=60`, `note="hello"`, `data=[1,2,3]`).
- The `--limit` flag caps the number of results across all paginated pages.

After installation, confirm to me that the skill is ready and show me a quick summary of what I can ask you to do with Runalyze.
````

---

## What this does

When a user pastes the prompt into their agent:

1. **Clones** `runalyze-cli` into `~/skills/runalyze-cli` and installs dependencies with `uv sync`
2. **Prompts the user** for their Runalyze API token and writes it to `.env`
3. **Verifies** the installation by calling the `services` endpoint
4. **Registers** the full command reference as agent context so the agent knows how to call every endpoint
