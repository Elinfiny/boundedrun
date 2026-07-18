# Architecture

BoundedRun is a single-process FastAPI demonstration with explicit trust boundaries. It converts a software objective into evidence, not authority: the application can generate one synthetic local artifact, but it cannot run user-supplied commands or mutate an external system.

## Request lifecycle

1. `RunRequest` collapses whitespace and validates the objective length.
2. `evaluate_policy` deterministically classifies the normalized text as `safe`, `review`, or `protected`.
3. `create_plan` chooses a planning path:
   - with `OPENAI_API_KEY`, the OpenAI Python SDK calls `responses.parse` using model `gpt-5.6` and `ExecutionPlan` as the structured-output contract;
   - without a key, when AI is disabled, or after any API/schema/policy inconsistency, the deterministic planner produces the plan.
4. Planner provenance records whether AI was requested and attempted, which planner won, and whether fallback occurred. Exception text is not persisted, avoiding accidental secret leakage.
5. Protected policy decisions always stop with handler `none`. Non-protected plans must select one of the three handler enum values.
6. `execute_bounded` generates an in-memory documentation, configuration, or test-validation artifact and evaluates deterministic contracts.
7. `run_objective` derives the status, computes artifact SHA-256 when an artifact exists, creates a compact evidence summary, and stores the receipt in SQLite.
8. The API can list or reopen stored receipts. `export_run` derives a Markdown or JSON Codex work package from the stored receipt without executing it.

## Contracts

### Planner contract

`ExecutionPlan` and `PlanStep` forbid unknown fields. A valid plan requires:

- a bounded summary;
- an enum handler;
- one to eight contiguous, ordered steps beginning at one;
- at least one validation gate;
- at least one protected boundary.

The OpenAI SDK derives a strict structured-output schema from this Pydantic model. BoundedRun then applies an additional semantic check: protected objectives require `none`, while non-protected objectives cannot use `none`. A failure at either layer routes to deterministic planning and appears in the receipt.

### Execution contract

The runtime allow-list contains only:

- `documentation_update`: produces Markdown with objective, execution boundary, and evidence sections;
- `configuration_review`: produces JSON that explicitly disables network and production access;
- `test_validation`: produces deterministic JSON assertions for objective presence, minimum length, bounded mode, and absence of external mutation.

There is no generic command handler, subprocess call, eval path, external repository loader, deployment adapter, credential collector, or account client.

### Receipt contract

Every new receipt records:

- normalized objective and creation time;
- planner name plus detailed provenance;
- policy reasons, matched terms, allowed actions, and blocked actions;
- ordered plan and protected boundaries;
- validation results;
- artifact preview and SHA-256 when present;
- compact evidence summary, status, and next action.

SQLite persists the Pydantic JSON as the source of evidence. Export is derived from that stored receipt, so reopening and exporting do not repeat planning or execution.

### Codex export contract

The export contains the normalized objective, policy decision, allowed and blocked actions, ordered steps, validation gates, protected boundaries, evidence requirements, repository instructions, planner provenance, and artifact hash. Repository instructions constrain Codex to the current repository and repeat the protected boundaries. The export endpoint only serializes data and sets a download header.

## Failure behavior

- Invalid request bodies return FastAPI validation errors and create no receipt.
- Missing runs return `404 Run not found`.
- Invalid export formats return a validation error.
- Missing API configuration, API errors, empty parsed output, malformed structured output, and handler-policy mismatches use deterministic fallback with visible provenance.
- Any failed deterministic validation produces status `failed` and prevents a success next action.
- Protected policy decisions produce status `blocked`, a successful boundary-stop validation, and no artifact.

## Data and deployment boundary

The default database is the local, gitignored `boundedrun.db`. The project does not include production deployment, telemetry, tracking, analytics, external fonts, personal data, or private-project integration. The browser UI uses only same-origin API calls.
