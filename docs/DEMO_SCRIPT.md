# BoundedRun Demo Script

Target length: 2 minutes 30 seconds. Run the app without an API key so the audience sees deterministic fallback explicitly.

## 0:00–0:20 — Problem and promise

Show the landing page.

> AI can generate changes quickly, but trustworthy execution needs a boundary and evidence. BoundedRun turns a software objective into a governed Codex work package. It classifies risk first, permits only three local handlers, validates the artifact, and stores an auditable receipt.

Point to the header proof chips: three handlers, zero arbitrary commands, deterministic fallback.

## 0:20–1:00 — Safe run

Click **Safe documentation**, then **Create bounded run**.

> This objective is safe. With no API key, BoundedRun visibly selects its deterministic fallback instead of hiding an AI failure. The run still receives an ordered plan, an allow-listed documentation handler, four passing gates, and a SHA-256 artifact hash.

Point to the green result border, evidence summary, provenance line, allowed/blocked actions, and validation evidence. Click **Download Markdown** and briefly show that the package includes repository-scoped instructions and protected boundaries.

## 1:00–1:35 — Protected run

Click **Protected operation**, then **Create bounded run**.

> The same flow now detects secrets, production deployment, and deletion before execution. The result is visually red, status is blocked, handler is none, and no artifact was produced. The receipt is still stored so the stop itself is auditable.

Point to the blocked actions, `protected_boundary` validation, and “Not produced” artifact hash.

## 1:35–1:55 — History and evidence

Scroll to **Stored run history** and reopen the first safe receipt.

> Reopening reads the SQLite receipt; it does not repeat planning or execution. That makes the policy decision, planner provenance, evidence, and export reproducible for review.

## 1:55–2:25 — Architecture and validation

Show the README architecture diagram or terminal validation output.

> Under the UI, a strict Pydantic contract validates GPT-5.6 Responses API output. Any missing key, API error, malformed schema, or policy mismatch falls back deterministically and records why. The test suite covers all policy levels, all handlers, exports, stored receipts, and mocked AI failures with at least 90% application coverage.

## 2:25–2:30 — Close

Return to the UI.

> BoundedRun demonstrates useful AI execution in the controlled middle: bounded actions, visible decisions, deterministic proof.
