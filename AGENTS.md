# BoundedRun Codex Operating Contract

## Scope
Work only in this repository. The project is a standalone OpenAI Build Week demonstration and must not import code, data, credentials, prompts, receipts, or business logic from any private project.

## Required behavior
- Inspect before editing.
- Keep the demo runnable without an API key through deterministic fallback behavior.
- Use the OpenAI Responses API with model `gpt-5.6` when `OPENAI_API_KEY` is configured.
- Keep execution bounded to allow-listed handlers; do not add arbitrary shell execution.
- Add or update tests with every behavior change.
- Run `ruff check .` and `pytest` before reporting completion.
- Preserve audit receipts and protected-action blocking.

## Protected boundaries
Do not add production deployment, external-account mutation, secret collection, financial actions, personal data, force-push behavior, or destructive repository actions.

## Build Week evidence
Document material Codex contributions in `docs/CODEX_BUILD_LOG.md`. Before final submission, obtain a `/feedback` Session ID from the Codex session where most implementation work occurred.
