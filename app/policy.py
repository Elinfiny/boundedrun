from __future__ import annotations

import re

from app.models import PolicyDecision, RiskLevel

PROTECTED_PATTERNS: dict[str, str] = {
    r"\b(api[- ]?key|secret|credential|password|token)\b": "Access to secrets or credentials",
    r"\b(production|prod environment|live system)\b": "Production-system mutation",
    r"\b(deploy|publish|release)\b": "External publication or deployment",
    r"\b(delete|destroy|drop database|wipe)\b": "Destructive operation",
    r"\b(payment|purchase|money|trade|trading|bank)\b": "Financial authority",
    r"\b(force push|rewrite history)\b": "Irreversible source-control action",
    r"\b(dns|cloudflare|hosting account)\b": "External infrastructure mutation",
    r"\b(personal data|pii|customer data)\b": "Private or personal data access",
}

REVIEW_PATTERNS: dict[str, str] = {
    r"\b(create pull request|open pull request|merge)\b": "Repository publication boundary",
    r"\b(update dependencies|upgrade dependencies)\b": "Dependency-change review",
    r"\b(network request|external api)\b": "External network access",
}


def _matches(objective: str, patterns: dict[str, str]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for pattern, reason in patterns.items():
        match = re.search(pattern, objective, flags=re.IGNORECASE)
        if match:
            result.append((match.group(0), reason))
    return result


def evaluate_policy(objective: str) -> PolicyDecision:
    protected = _matches(objective, PROTECTED_PATTERNS)
    review = _matches(objective, REVIEW_PATTERNS)

    if protected:
        return PolicyDecision(
            risk_level=RiskLevel.PROTECTED,
            reasons=sorted({reason for _, reason in protected}),
            matched_terms=sorted({term.lower() for term, _ in protected}),
            allowed_actions=[
                "Inspect the request",
                "Produce a redacted plan",
                "Explain the boundary",
            ],
            blocked_actions=[
                "Read or expose secrets",
                "Mutate production or external accounts",
                "Perform destructive or financial actions",
            ],
        )

    if review:
        return PolicyDecision(
            risk_level=RiskLevel.REVIEW,
            reasons=sorted({reason for _, reason in review}),
            matched_terms=sorted({term.lower() for term, _ in review}),
            allowed_actions=["Plan", "Run local validation", "Create an isolated work package"],
            blocked_actions=["Publish, merge, or call external systems without an explicit gate"],
        )

    return PolicyDecision(
        risk_level=RiskLevel.SAFE,
        reasons=["No protected-action indicators were detected"],
        matched_terms=[],
        allowed_actions=[
            "Create an isolated work package",
            "Use a pre-approved local handler",
            "Run deterministic validation",
            "Generate an audit receipt",
        ],
        blocked_actions=["Any action outside the declared handler and validation gates"],
    )
