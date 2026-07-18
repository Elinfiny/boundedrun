# Architecture

BoundedRun separates planning, policy, execution, validation, and evidence.

1. **Objective intake** validates a user-provided software objective.
2. **Policy engine** classifies the objective as safe, review, or protected.
3. **Planner** uses GPT-5.6 when configured and a deterministic fallback otherwise.
4. **Bounded executor** permits only three local handlers: documentation update, configuration review, and test validation.
5. **Validation layer** checks handler allow-listing, artifact contracts, evidence digests, and protected-operation absence.
6. **Receipt store** persists structured evidence in SQLite.
7. **Web interface** presents the plan, risk, validation, and next action.

The prototype intentionally excludes arbitrary shell execution, production access, external account changes, secrets, financial actions, and private project data.
