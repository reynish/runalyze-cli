---
name: runalyze-cli
description: Interact with the Runalyze running and fitness API via a CLI tool. Use when the user wants to query, manage, or analyze their running activities, health metrics (heart rate, HRV, sleep, blood glucose, etc.), equipment tracking, race results, tags, or training statistics stored in Runalyze. Also use when the user wants to upload activity files (FIT, GPX, TCX), export activity data, or sync changes. Trigger this skill whenever the user mentions Runalyze, running data, training logs, workout history, fitness tracking, activity uploads, health metrics, or equipment management — even if they don't explicitly name Runalyze.
---

# Runalyze CLI

A CLI tool for interacting with the Runalyze API. All output is structured JSON, designed for easy parsing and scripting. The tool is installed as `runalyze-cli` and run via `uv run runalyze-cli` from the skill directory.

## Prerequisites

The tool requires a Runalyze API token set as an environment variable or in a `.env` file in the project directory:

```bash
export RUNALYZE_AUTH_TOKEN=your_token_here
```

You can optionally override the base URL (useful for testing):

```bash
export RUNALYZE_BASE_URL=https://runalyze.com
```

Every command is invoked as:

```bash
uv run runalyze-cli <command> [subcommand] [arguments] [options]
```

All output goes to stdout as JSON. Errors go to stderr with a non-zero exit code.

## Command Reference

### Activities

Working with recorded activities (runs, rides, swims, etc.).

```bash
# List all activities (returns JSON array)
uv run runalyze-cli activity list [--limit N]

# Get a single activity by ID
uv run runalyze-cli activity get <id>

# Export an activity in a specific format
# Formats: fit, fit-original, fitlog, gpx, kml, tcx
uv run runalyze-cli activity export <id> <format>

# Upload an activity file (FIT, GPX, TCX, etc.)
uv run runalyze-cli activity upload <file_path>

# Check the processing status of an uploaded activity
uv run runalyze-cli activity upload-status <upload_id>
```

**Export behavior**: Text-based formats (GPX, TCX, KML) are returned as UTF-8 strings in the `content` field. Binary formats (FIT) are base64-encoded with an `"encoding": "base64"` field. To decode a binary export, use `base64.b64decode(data["content"])`.

**Upload flow**: Uploading is asynchronous. The `upload` command returns an upload ID. Poll `upload-status` with that ID until processing completes.

### Health Metrics

Reading and writing health data. Metric types are: `bloodGlucose`, `bloodPressure`, `bodyComposition`, `bodyTemperature`, `dailyNote`, `heartRateMax`, `heartRateRest`, `hrv`, `mental`, `sleep`.

```bash
# List metrics of a given type
uv run runalyze-cli metrics list <metric_type> [--limit N]

# Get a single metric entry
uv run runalyze-cli metrics get <metric_type> <id>

# Create a new metric entry
# Props are key=value pairs; JSON values are parsed automatically
uv run runalyze-cli metrics create <metric_type> [key=value ...]

# Example: log resting heart rate
uv run runalyze-cli metrics create heartRateRest value=60

# Example: log sleep with structured data
uv run runalyze-cli metrics create sleep duration=7.5 quality="good"

# Update an existing metric
uv run runalyze-cli metrics update <metric_type> <id> [key=value ...]

# Delete a metric
uv run runalyze-cli metrics delete <metric_type> <id>

# Get latest values across all metric types
uv run runalyze-cli metrics-latest
```

**Props parsing**: Key-value arguments use `key=value` syntax. Values that are valid JSON (numbers, booleans, `null`, arrays, objects) are parsed as JSON types. Everything else stays as a string. For example: `value=60` → integer 60, `note="felt good"` → string "felt good", `tags=["a","b"]` → list.

### Equipment

Tracking gear (shoes, bikes, etc.) and their usage.

```bash
# List all equipment
uv run runalyze-cli equipment list [--limit N]

# Get a single equipment item
uv run runalyze-cli equipment get <id>

# List equipment categories (e.g., "Shoes", "Bikes")
uv run runalyze-cli equipment categories [--limit N]

# Get a specific category
uv run runalyze-cli equipment category <id>

# List all equipment items within a category
uv run runalyze-cli equipment category-equipment <category_id> [--limit N]
```

### Race Results

Managing race results and personal records.

```bash
# List all race results
uv run runalyze-cli raceresult list [--limit N]

# Get a specific race result
uv run runalyze-cli raceresult get <id>

# Update a race result
uv run runalyze-cli raceresult update <id> [key=value ...]

# Delete a race result
uv run runalyze-cli raceresult delete <id>
```

### Tags

Managing activity tags for categorization.

```bash
# List all tags
uv run runalyze-cli tag list [--limit N]

# Get a specific tag
uv run runalyze-cli tag get <id>
```

### Settings

```bash
# List date range settings
uv run runalyze-cli settings date-range [--limit N]

# Get a specific date range
uv run runalyze-cli settings date-range-get <id>
```

### Statistics

```bash
# Get current training statistics
uv run runalyze-cli statistics current
```

### Services & Sync

```bash
# List connected services (Garmin, Polar, etc.)
uv run runalyze-cli services

# Sync changes to the API
uv run runalyze-cli sync-changes [key=value ...]
```

## Common Workflows

### "Show me my recent runs"

```bash
uv run runalyze-cli activity list --limit 10
```

Then if the user wants details on a specific activity, grab the `id` from the list output and:

```bash
uv run runalyze-cli activity get <id>
```

### "Export my last run as GPX"

```bash
uv run runalyze-cli activity list --limit 1
# Get the id from the output, then:
uv run runalyze-cli activity export <id> gpx
```

The GPX XML content will be in the `content` field of the JSON output. Save it to a file if needed.

### "Upload a workout file"

```bash
uv run runalyze-cli activity upload /path/to/activity.fit
# Returns {"id": "upload_id"} — check status:
uv run runalyze-cli activity upload-status <upload_id>
```

### "Log my resting heart rate"

```bash
uv run runalyze-cli metrics create heartRateRest value=58
```

### "What metrics have I tracked recently?"

```bash
uv run runalyze-cli metrics-latest
```

### "Show me my shoes and their mileage"

```bash
uv run runalyze-cli equipment categories
# Find the "Shoes" category id, then:
uv run runalyze-cli equipment category-equipment <category_id>
```

### "What are my race PRs?"

```bash
uv run runalyze-cli raceresult list
```

## Error Handling

The CLI exits with code 0 on success and code 1 on failure. Error messages are written to stderr in the format `Error: <message>`. Common errors include:

- **Missing token**: `RUNALYZE_AUTH_TOKEN not found.` — Set the environment variable or create a `.env` file.
- **Not Found**: The requested resource ID doesn't exist.
- **Forbidden**: The token is invalid or lacks permissions.
- **Rate limited**: The client retries automatically (up to 3 attempts with backoff), but may still fail on persistent limits.

## Tips for Agents

- All list commands support `--limit N` to cap the number of results. Use it to avoid pulling large datasets when you only need a few items.
- The API uses Hydra (JSON-LD) pagination — the CLI handles this transparently. List commands automatically fetch all pages unless `--limit` is specified.
- Output is always valid JSON on stdout. Parse it with `json.loads()` or pipe through `jq`.
- IDs are passed as strings on the CLI but are typically integers in the API.
- For bulk operations, chain commands: list → extract IDs → get/export each one.
- When creating or updating metrics, the `key=value` syntax means you can pass numbers, strings, booleans, lists, and objects without worrying about quoting — just write valid JSON for complex values.
