# Contributing to Webex Meeting Data Exporter

Thanks for your interest in contributing. This document covers how to set up the project, run tests, and submit changes.

## Prerequisites

- Python 3.11 or later
- Node.js 18+ (for Prettier and lint-staged)

## Setup

1. Clone the repository and create a virtual environment:

```bash
git clone https://github.com/webex/meetings-exporter.git
cd meetings-exporter
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

2. Install the package with dev dependencies:

```bash
pip install -e ".[dev]"
npm install
```

3. Copy the environment template and add your Webex token for local testing:

```bash
cp env.template .env
# Edit .env and set WEBEX_ACCESS_TOKEN
```

## Running Tests

```bash
pytest tests/ -v
```

For coverage:

```bash
pytest tests/ -v --cov=meetings_exporter --cov-report=term-missing
```

## Code Style

- **Python**: We use [Ruff](https://docs.astral.sh/ruff/) for linting. Run `ruff check .` and `ruff check --fix .` to fix issues.
- **Markdown, JSON, JS**: We use [Prettier](https://prettier.io). Run `npx prettier . --check` or `npx prettier . --write`.

## Pre-Commit Hooks

After `npm install`, the Husky pre-commit hook runs Prettier and Ruff before each commit. To skip hooks for a single commit: `git commit -m "..." -n`.

## Submitting Changes

1. Create a branch from `main`
2. Make your changes and ensure tests pass
3. Run `ruff check .` and `npx prettier . --check`
4. Open a pull request with a clear description of the change
5. Ensure CI (Ruff, Prettier, pytest) passes

## Adding a New Export Backend

The exporter system is pluggable. To add a new backend (e.g. OneDrive, Dropbox):

1. Create a new class in `src/meetings_exporter/exporters/` that implements `MeetingExporter` (see `base.py`)
2. Add a factory function (e.g. `_create_onedrive(**kwargs)`) and register it in `_EXPORTER_REGISTRY` in `factory.py`
3. Add tests in `tests/test_exporters.py`
4. Document the new backend in the README and env.template

Use `meeting_formatter` for shared formatting (folder names, meeting details, summary text).
