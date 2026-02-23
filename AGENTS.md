# Webex Meeting Data Exporter – Agent Context

This file provides context for AI coding agents working on this project. For human-focused docs, see [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Design Principles

This project follows **SOLID** design principles:

- **S – Single Responsibility**: Each module/class has one reason to change. Split large functions.
- **O – Open/Closed**: Extend via new implementations (e.g. exporters) without modifying existing code.
- **L – Liskov Substitution**: Subtypes (e.g. `LocalFolderExporter`, `GoogleDriveExporter`) are substitutable for their base (`MeetingExporter`).
- **I – Interface Segregation**: Keep interfaces small and focused (e.g. `MeetingExporter.write()` only).
- **D – Dependency Inversion**: Depend on abstractions (e.g. `MeetingExporter`, protocols) not concretions. Inject dependencies where possible.

When adding or refactoring code, apply these principles.

## Project Overview

Python CLI that exports Webex meeting data (recordings, transcripts, summaries, action items) to local folders or Google Drive. Designed for use with tools like Gemini. Uses Webex Meetings API and Meeting Summaries API.

## Architecture

- **CLI** (`cli.py`): `list` and `export` subcommands. Entry point.
- **Ingestion** (`ingestion.py`): `collect_meeting_data()` fetches from Webex; `export_meeting()` orchestrates collect + write. Callable from CLI or future webhook handler.
- **WebexClient** (`webex_client.py`): HTTP client for Webex APIs.
- **Exporters** (`exporters/`): Pluggable backends. `MeetingExporter` ABC in `base.py`. Implementations: `LocalFolderExporter`, `GoogleDriveExporter`. Factory uses registry in `factory.py`.
- **meeting_formatter** (`meeting_formatter.py`): Shared formatting for folder names, meeting details, and summary text. Used by exporters (SRP).
- **webhook_utils** (`webhook_utils.py`): Parsing for Webex webhook payloads. For Phase 2 webhook server.

## Dev Environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
npm install
cp env.template .env
# Set WEBEX_ACCESS_TOKEN in .env
```

## Testing

```bash
pytest tests/ -v
pytest tests/ -v --cov=meetings_exporter --cov-report=term-missing
```

## Code Style

- **Python**: Ruff. `ruff check .` and `ruff check --fix .`. Line length 100.
- **Markdown, JSON, YAML**: Prettier. `npx prettier . --check` or `npx prettier . --write`.

## Security

- Never commit `.env`, `token.json`, or `*.credentials.json` (in `.gitignore`).
- Tokens and credentials via env vars only.
- `WEBEX_ACCESS_TOKEN` required for list/export.
- Google Drive uses minimal scope `drive.file`.

## Key Conventions

- **export_meeting(meeting_id, client=None, exporter=None, progress_callback=None)**: Reusable entry point. Use for CLI or webhooks. Pass `progress_callback=None` for silent.
- **Meeting IDs**: Must be individual instance IDs (e.g. `..._I_...`), not series. Required for summaries, recordings, transcripts.
- **Add new backends**: Implement `MeetingExporter` in `exporters/`, add a factory function, and register it in `_EXPORTER_REGISTRY` in `factory.py`. No need to modify `get_exporter()`.

## Roadmap

Webhooks (e.g. auto-export on recording ready) are planned. `webhook_utils` and `export_meeting()` are ready for Phase 2.
