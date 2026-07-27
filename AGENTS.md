# BoundedRun Codex Operating Contract

Policy version: `2.0.0`
Effective date: `2026-07-28`
Global adoption: `ACTIVE_CANONICAL_V2_PINNED`

## Scope

Work only in this repository. The project is a standalone public OpenAI Build Week demonstration and must not import code, data, credentials, prompts, receipts, strategies, or business logic from any private project.

Read and hash-verify `docs/GLOBAL_EXECUTION_CONTRACT_V2_ADOPTION.md` before modifying work. The pinned Global Execution Contract V2 is version `2.0.0`, SHA256 `9BB7A8704F76204BA324DB83AFA5FA88E37AB7150591FBC7742E14AF3BE771A0`.

## Required behavior

- Inspect before editing.
- Preserve accepted progress and use the smallest safe targeted patch.
- Determine and execute the next safe authorized action inside an exact validated non-protected scope without a generic approval loop.
- Convert repeated failures, delays, ambiguous outputs, and user corrections into validated persistent rules.
- Reevaluate historical OpenAI, Codex, connector, model, API, and tool limitations whenever a V2 trigger occurs.
- Select a verified model/tool route and use independent deterministic tests or review for material behavior changes.
- Keep the demo runnable without an API key through deterministic fallback behavior.
- Use the OpenAI Responses API with model `gpt-5.6` when `OPENAI_API_KEY` is configured, unless a newer verified route is adopted through the capability-evolution pipeline.
- Keep execution bounded to allow-listed handlers; do not add arbitrary shell execution.
- Add or update tests with every behavior change.
- Run `ruff check .` and `pytest` before reporting completion.
- Preserve audit receipts and protected-action blocking.
- Do not claim continuous monitoring, scheduling, or background execution without a verified automation receipt.
- Do not require the user to shuttle reports manually when canonical GitHub transport is available.

## Persistent improvement and capability adoption

Use:

`observe -> root cause -> targeted correction -> isolated test -> before/after comparison -> adopt or rollback -> persist`

Classify new capabilities as `ADOPT_NOW_SAFE`, `ADOPT_AFTER_GATE`, `WATCH_ONLY`, `REJECT_FOR_NOW`, or `REQUIRES_EXACT_USER_GATE`. Preserve the previous validated implementation as fallback until the new route stabilizes.

Operational self-improvement applies to rules, prompts, skills, validators, tests, routing, and tools. It does not authorize rewriting the underlying model or bypassing platform constraints.

## Monetization review

At each material macro-route, assess whether BoundedRun can support a bounded commercial validation as a developer tool, safe-agent runner, audit/control component, productized implementation service, or team integration.

Research, prototypes, offer design, and internal pricing analysis may proceed inside an exact non-protected task. Production deployment, customer data, contracts, payments, external-account mutation, secret collection, or public commercial claims require the exact applicable gate.

## Protected boundaries

Do not add production deployment, external-account mutation, secret collection, financial actions, personal data, force-push behavior, destructive repository actions, arbitrary shell execution, unbounded tools, recurring services, schedulers, daemons, or private-project imports.

## Reporting

A terminal report must include baseline, changed scope, tests, diff review, capability reevaluation, improvement decision, monetization review, protected-effects confirmation, next safe action, and `USER_ACTION=NONE` unless one unavoidable operation exists.

## Build Week evidence

Document material Codex contributions in `docs/CODEX_BUILD_LOG.md`. Before final submission, obtain a `/feedback` Session ID from the Codex session where most implementation work occurred.
