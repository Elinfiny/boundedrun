# BoundedRun

**Governed AI execution that turns objectives into bounded Codex work packages with risk gates, deterministic validation, and auditable receipts.**

BoundedRun is a standalone OpenAI Build Week demonstration. It accepts a software objective, classifies its risk before planning, permits one of three local handlers, validates the resulting artifact, and stores a receipt that explains exactly what happened. A receipt can be reopened from run history or exported as a repository-scoped Codex work package.

The full product flow works without an API key. When `OPENAI_API_KEY` is present, the planner uses the OpenAI Responses API with `gpt-5.6` and a strict Pydantic structured-output contract. Missing credentials, model errors, and malformed responses use the same deterministic planner and are explicitly recorded in planner provenance.

## What the demo proves

- Policy runs before planning or execution.
- Protected objectives produce blocked receipts without artifacts.
- Safe and review objectives can use only `documentation_update`, `configuration_review`, or `test_validation`.
- GPT-5.6 output must validate as `ExecutionPlan` and cannot override the policy boundary.
- Deterministic fallback remains available without network access or credentials.
- Artifact SHA-256, validation gates, planner provenance, and the next action are visible in every new receipt.
- Stored receipts can be reopened and exported to Markdown or JSON without repeating execution.

BoundedRun never accepts commands to execute. Its handlers build synthetic in-memory artifacts; they do not provide a shell, deploy software, mutate an external account, collect secrets, move money, access PII, or reach into another repository.

## Architecture

```text
Objective
   │ normalize and validate
   ▼
Policy engine ── protected ──► blocked plan + receipt
   │ safe/review
   ▼
Planner ── API key ──► GPT-5.6 Responses API + strict ExecutionPlan
   │                    │ failure or malformed output
   └────────────────────┴──► deterministic plan + visible provenance
   ▼
Allow-listed handler
   ▼
Contract checks + SHA-256 evidence
   ▼
SQLite receipt ──► history / reopen / Markdown or JSON Codex export
```

The application is split into small boundaries:

- `app/policy.py`: deterministic safe, review, and protected classification.
- `app/planner.py`: GPT-5.6 structured planning and deterministic fallback.
- `app/executor.py`: the three allow-listed, in-memory handlers and validation evidence.
- `app/service.py`: orchestration, status selection, provenance, hashing, and receipt creation.
- `app/store.py`: local SQLite receipt persistence.
- `app/exporter.py`: repository-scoped Codex work-package construction and Markdown rendering.
- `app/main.py`: FastAPI routes and static UI delivery.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for contracts and trust boundaries.

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

Open `http://127.0.0.1:8000`. SQLite creates `boundedrun.db` in the current directory; the file is gitignored.

## Optional GPT-5.6 configuration

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-key"

# macOS/Linux
export OPENAI_API_KEY="your-key"
```

The model is intentionally fixed to `gpt-5.6`. Never commit an API key; `.env.example` contains only an empty placeholder. If the key is absent, invalid, or the API response fails the contract, the receipt shows why deterministic fallback was used.

## Demo flow

1. Start the app and choose **Safe documentation**.
2. Create the run and point out the safe risk badge, allow-listed handler, evidence summary, planner provenance, and artifact hash.
3. Download the Markdown work package.
4. Choose **Protected operation** and create the run.
5. Show that the protected receipt is red, blocked, and contains no artifact hash.
6. Reopen the safe receipt from **Stored run history** to prove persistence without re-execution.

A timed script for a video under three minutes is in [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md).

## API

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health |
| `POST` | `/api/runs` | Classify, plan, execute within bounds, validate, and store |
| `GET` | `/api/runs?limit=20` | List newest stored receipts |
| `GET` | `/api/runs/{run_id}` | Reopen one stored receipt |
| `GET` | `/api/runs/{run_id}/export?format=markdown` | Download a Markdown Codex package |
| `GET` | `/api/runs/{run_id}/export?format=json` | Download a JSON Codex package |

Create a deterministic run:

```bash
curl -X POST http://127.0.0.1:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{"objective":"Add contribution guidelines and validate governance boundaries.","use_ai":false}'
```

The export contains the normalized objective, full policy decision, allowed and blocked actions, ordered steps, validation gates, protected boundaries, evidence requirements, planner provenance, artifact hash, and repository-scoped Codex instructions. It is an instruction artifact only; BoundedRun does not invoke Codex or execute its contents.

## Validation

Run the same checks as CI:

```bash
ruff check .
pytest --cov=app --cov-report=term-missing
python scripts/smoke_test.py
```

The smoke test uses an isolated temporary SQLite database and covers `/health`, a validated safe receipt, a blocked protected receipt, Markdown export, and stored-receipt retrieval.

## Repository isolation

This repository contains only synthetic demonstration logic. It does not contain or depend on private projects, data, credentials, prompts, receipts, business logic, or proprietary workflows. The operating contract is in [`AGENTS.md`](AGENTS.md), and material Codex work is recorded in [`docs/CODEX_BUILD_LOG.md`](docs/CODEX_BUILD_LOG.md).
