# Codex Build Log

This file records material work completed with Codex during OpenAI Build Week.

## Primary session

- `/feedback` Session ID: `PENDING`
- Primary implementation date: `2026-07-18`
- Branch: `codex/build-week-primary`
- Authoritative task: GitHub Issue #2, “Primary Codex implementation session for OpenAI Build Week”
- Implementation commit: `51d6c5a` (`Implement governed Build Week workflow`)

## Repository audit

Codex read the operating contract, product documentation, architecture, original build log, all application and test files, CI configuration, and Issue #2 before editing. The audited `main` baseline was commit `08865de` with 6 passing tests, 84% application coverage, a clean Ruff result, and no run-history or export UI.

The audit identified these material gaps:

- free-form JSON extraction hid GPT/API failures and did not enforce a strict output schema;
- the receipt exposed only a planner label, not provenance or fallback evidence;
- the `test_validation` artifact contract incorrectly failed because it called `all()` over an intentionally false `external_mutation` value;
- stored receipts had API primitives but no history/reopen experience;
- there was no Codex package export;
- UI rendering used dynamic `innerHTML` with planner-controlled strings;
- safe, review, protected, handler, malformed-model, export, API-error, and store paths lacked comprehensive tests.

## Material Codex contributions

- Replaced free-form response parsing with `responses.parse(model="gpt-5.6", text_format=ExecutionPlan)` and strict Pydantic models that forbid extra fields and require contiguous steps.
- Added policy-to-handler semantic checks and explicit, sanitized planner provenance for success, missing-key fallback, disabled AI, malformed output, and API failure.
- Added artifact SHA-256 and a compact evidence summary to receipts.
- Fixed the test-validation contract so `external_mutation: false` is treated as required safety evidence.
- Added Markdown and JSON Codex work-package export with repository scope, policy actions, steps, gates, boundaries, evidence requirements, provenance, and hashes.
- Rebuilt the interface with stored run history, receipt reopening, downloads, visible safe/protected states, inline loading/errors, accessible labels and live regions, reduced-motion support, safer DOM rendering, and responsive layouts.
- Expanded tests across policy levels, every allow-listed handler, planner failure/fallback mocks, API errors, persistence, export, status failure, normalization, and strict contracts.
- Added an isolated end-to-end smoke-test script and a sub-three-minute demo script.
- Rewrote the README and architecture document to match the implemented contracts and flow.

## Key decisions

1. The OpenAI model is fixed in code to `gpt-5.6`; an environment override cannot silently change the evaluated planner.
2. AI exceptions are represented only by exception class in provenance, never raw exception text that could contain sensitive context.
3. Export is derived from a stored receipt and never launches Codex, a shell, or an external repository operation.
4. Legacy receipts without detailed provenance remain exportable through a conservative derived provenance record.
5. Browser content is constructed with `textContent` and DOM nodes so objective or planner strings are not treated as HTML.

## Validation evidence

- `ruff check .`: passed, no findings.
- `pytest --cov=app --cov-report=term-missing`: 42 passed; 313 application statements; 100% coverage; one non-failing dependency deprecation warning from Starlette `TestClient`.
- `python scripts/smoke_test.py`: passed `/health`, safe validated receipt, protected blocked receipt, Markdown export, and stored receipt retrieval.
- Browser QA: passed safe/protected/history flows at the default desktop viewport and responsive layout at 390×844; no browser console warnings or errors.
- JavaScript syntax: `node --check app/static/app.js` passed.

The `/feedback` Session ID intentionally remains `PENDING` until the operator obtains it at the end of this primary Codex session.
