# BoundedRun

**Governed AI execution that turns objectives into bounded Codex work packages with risk gates, deterministic validation, and auditable receipts.**

BoundedRun is a standalone OpenAI Build Week project. It uses GPT-5.6 to convert a software objective into a structured plan, applies a local policy engine, permits only explicitly allow-listed handlers, validates the result, and persists a receipt that explains what happened and what should happen next.

## Why it exists

AI coding tools can produce changes quickly, but trustworthy execution requires more than code generation. A system must also know what it is allowed to do, prove that it stayed inside scope, stop at protected boundaries, and preserve evidence.

BoundedRun demonstrates that controlled middle ground:

- safe work can proceed inside an isolated demo;
- protected actions are blocked before execution;
- every result is supported by validation evidence;
- the app remains testable without exposing private projects or credentials.

## Demo flow

1. Enter a high-level objective.
2. GPT-5.6 produces a bounded plan when `OPENAI_API_KEY` is configured.
3. The deterministic policy engine classifies risk.
4. One allow-listed local handler executes.
5. Validation gates verify the artifact and protected boundaries.
6. SQLite stores a structured receipt.
7. The UI displays the plan, decision, evidence, and next action.

The application includes a deterministic fallback so judges can test the full product flow even without an OpenAI API key.

## Protected boundaries

BoundedRun does **not** execute:

- arbitrary shell commands;
- secret or credential access;
- production deployment;
- financial actions;
- destructive operations;
- personal data access;
- force pushes;
- external account or infrastructure mutations.

## Built with GPT-5.6 and Codex

### GPT-5.6

The app integrates the OpenAI Responses API. When `OPENAI_API_KEY` is available, `app/planner.py` sends the objective and local policy decision to `gpt-5.6`, requesting a structured execution plan constrained to the approved handler set. If the API is unavailable, the app falls back to a deterministic planner without bypassing policy or validation.

### Codex

Codex is used to implement, inspect, test, and improve the repository. The operating contract is defined in [`AGENTS.md`](AGENTS.md), and material Codex work is recorded in [`docs/CODEX_BUILD_LOG.md`](docs/CODEX_BUILD_LOG.md). The final Build Week submission will include the `/feedback` Session ID from the primary Codex implementation session.

## Local installation

Requirements: Python 3.11 or newer.

```bash
git clone https://github.com/Elinfiny/boundedrun.git
cd boundedrun
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install and run:

```bash
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Optional GPT-5.6 configuration

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-5.6"

# macOS/Linux
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-5.6"
```

Never commit the API key. The repository includes `.env.example` only.

## Validation

```bash
ruff check .
pytest --cov=app --cov-report=term-missing
```

## API

- `GET /health`
- `POST /api/runs`
- `GET /api/runs`
- `GET /api/runs/{run_id}`

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{"objective":"Add contribution guidelines and validate governance boundaries.","use_ai":false}'
```

## Repository isolation

This repository contains only synthetic demonstration logic. It does not contain or depend on AutomatedTrading, GenieFinds, ELWICO, AffiliateSocial, or any other private project, data, credentials, or proprietary workflow.
