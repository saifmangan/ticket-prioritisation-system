from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import math
import re
from typing import Any


URGENT_KEYWORDS = {
    "urgent",
    "asap",
    "immediately",
    "critical",
    "blocked",
    "down",
    "outage",
    "offline",
    "cannot",
    "can't",
    "failed",
    "failure",
    "broken",
    "crash",
    "crashing",
    "unable",
    "login",
    "payment",
    "billing",
    "security",
    "breach",
    "data loss",
    "compliance",
    "refund",
    "churn",
    "production",
}

NEGATIVE_KEYWORDS = {
    "angry",
    "frustrated",
    "unacceptable",
    "disappointed",
    "cancel",
    "leaving",
    "escalate",
    "manager",
    "lawsuit",
    "complaint",
}

POSITIVE_KEYWORDS = {"thanks", "thank you", "appreciate", "great", "good"}

CATEGORY_KEYWORDS = {
    "security": {"security", "breach", "vulnerability", "leak", "password", "2fa", "mfa"},
    "billing": {"invoice", "billing", "charged", "payment", "refund", "card", "subscription"},
    "access": {"login", "locked", "access", "permission", "sso", "auth", "password"},
    "availability": {"down", "outage", "offline", "unavailable", "production", "crash"},
    "data": {"missing data", "data loss", "export", "report", "sync", "duplicate"},
}

TIER_MULTIPLIER = {
    "enterprise": 1.25,
    "strategic": 1.22,
    "premium": 1.15,
    "growth": 1.05,
    "standard": 1.0,
    "free": 0.85,
}


@dataclass
class TicketInput:
    subject: str
    message: str
    customer: str = "Unknown customer"
    customer_tier: str = "standard"
    affected_users: int = 1
    revenue_at_risk: float = 0.0
    hours_until_sla: float | None = None
    channel: str = "email"
    created_at: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "TicketInput":
        allowed = {field.name for field in cls.__dataclass_fields__.values()}
        payload = {key: value for key, value in data.items() if key in allowed}
        return cls(**payload)


@dataclass
class PrioritizationResult:
    priority: str
    score: int
    confidence: float
    routing_team: str
    sla_target_minutes: int
    reasons: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    extracted_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Prioritizer:
    """Explainable revenue and SLA-aware ticket prioritiser.

    This class is deterministic so it can run in demos and tests without API
    keys. Optional LLM enrichment is layered on top in ``ai.py``.
    """

    def prioritize(self, ticket: TicketInput | dict[str, Any]) -> PrioritizationResult:
        if isinstance(ticket, dict):
            ticket = TicketInput.from_mapping(ticket)

        text = self._normalise(f"{ticket.subject} {ticket.message}")
        urgent_hits = self._keyword_hits(text, URGENT_KEYWORDS)
        negative_hits = self._keyword_hits(text, NEGATIVE_KEYWORDS)
        positive_hits = self._keyword_hits(text, POSITIVE_KEYWORDS)
        categories = self._categories(text)

        score = 18
        reasons: list[str] = []
        risk_flags: list[str] = []

        if urgent_hits:
            score += min(28, 8 + 4 * len(urgent_hits))
            reasons.append(f"Urgency language detected: {', '.join(urgent_hits[:5])}")

        if negative_hits:
            score += min(16, 5 + 3 * len(negative_hits))
            reasons.append(f"Customer sentiment risk: {', '.join(negative_hits[:4])}")

        if positive_hits and not negative_hits:
            score -= 4

        if "security" in categories:
            score += 24
            risk_flags.append("Security-sensitive issue")
        if "availability" in categories:
            score += 20
            risk_flags.append("Service availability risk")
        if "billing" in categories and ticket.revenue_at_risk > 0:
            score += 12
            risk_flags.append("Revenue-impacting billing issue")
        if "data" in categories:
            score += 10
            risk_flags.append("Data integrity concern")

        if ticket.affected_users >= 100:
            score += 18
            reasons.append(f"Broad user impact: {ticket.affected_users} affected users")
        elif ticket.affected_users >= 10:
            score += 10
            reasons.append(f"Team-level impact: {ticket.affected_users} affected users")
        elif ticket.affected_users > 1:
            score += 4

        if ticket.revenue_at_risk >= 10000:
            score += 18
            reasons.append(f"High revenue at risk: GBP {ticket.revenue_at_risk:,.0f}")
            risk_flags.append("High-value account exposure")
        elif ticket.revenue_at_risk >= 1000:
            score += 10
            reasons.append(f"Revenue at risk: GBP {ticket.revenue_at_risk:,.0f}")

        if ticket.hours_until_sla is not None:
            if ticket.hours_until_sla <= 1:
                score += 18
                reasons.append("SLA breach likely within 1 hour")
                risk_flags.append("Immediate SLA breach risk")
            elif ticket.hours_until_sla <= 4:
                score += 11
                reasons.append("SLA breach risk today")
            elif ticket.hours_until_sla <= 24:
                score += 5

        score = int(round(score * TIER_MULTIPLIER.get(ticket.customer_tier.lower(), 1.0)))
        score = max(0, min(100, score))

        priority, sla_target_minutes = self._priority(score)
        routing_team = self._routing_team(categories, text)
        actions = self._recommended_actions(priority, routing_team, risk_flags)
        confidence = self._confidence(score, len(reasons), len(categories))

        if not reasons:
            reasons.append("No major risk language found; prioritised by baseline SLA policy")

        extracted_signals = {
            "urgent_keywords": urgent_hits,
            "negative_keywords": negative_hits,
            "positive_keywords": positive_hits,
            "categories": categories,
            "ticket_age_hours": self._age_hours(ticket.created_at),
            "customer_tier": ticket.customer_tier.lower(),
        }

        return PrioritizationResult(
            priority=priority,
            score=score,
            confidence=confidence,
            routing_team=routing_team,
            sla_target_minutes=sla_target_minutes,
            reasons=reasons,
            recommended_actions=actions,
            risk_flags=risk_flags,
            extracted_signals=extracted_signals,
        )

    def _normalise(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _keyword_hits(self, text: str, keywords: set[str]) -> list[str]:
        hits = []
        for keyword in sorted(keywords):
            pattern = r"\b" + re.escape(keyword).replace(r"\ ", r"\s+") + r"\b"
            if re.search(pattern, text):
                hits.append(keyword)
        return hits

    def _categories(self, text: str) -> list[str]:
        categories = []
        for category, keywords in CATEGORY_KEYWORDS.items():
            if self._keyword_hits(text, keywords):
                categories.append(category)
        return categories

    def _priority(self, score: int) -> tuple[str, int]:
        if score >= 82:
            return "Critical", 30
        if score >= 64:
            return "High", 120
        if score >= 42:
            return "Medium", 480
        return "Low", 1440

    def _routing_team(self, categories: list[str], text: str) -> str:
        if "security" in categories:
            return "Security response"
        if "availability" in categories:
            return "Platform engineering"
        if "billing" in categories:
            return "Revenue operations"
        if "access" in categories:
            return "Identity and access"
        if "data" in categories:
            return "Data support"
        if "api" in text or "webhook" in text or "integration" in text:
            return "Integrations support"
        return "Customer support"

    def _recommended_actions(self, priority: str, routing_team: str, risk_flags: list[str]) -> list[str]:
        actions = [f"Route to {routing_team}", "Send acknowledgement with owner and next update time"]
        if priority in {"Critical", "High"}:
            actions.insert(0, "Escalate to duty manager")
            actions.append("Create an internal incident note with customer impact")
        if "Security-sensitive issue" in risk_flags:
            actions.append("Apply security handling and limit sensitive details in replies")
        if "High-value account exposure" in risk_flags:
            actions.append("Notify customer success owner")
        return actions

    def _confidence(self, score: int, reason_count: int, category_count: int) -> float:
        signal_strength = min(1.0, (reason_count * 0.18) + (category_count * 0.16))
        distance_from_boundary = min(abs(score - 42), abs(score - 64), abs(score - 82), 18) / 18
        return round(0.55 + (0.28 * signal_strength) + (0.17 * distance_from_boundary), 2)

    def _age_hours(self, created_at: str | None) -> float | None:
        if not created_at:
            return None
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            return round(max(0.0, (now - created).total_seconds() / 3600), 2)
        except ValueError:
            return None


def sigmoid(value: float) -> float:
    return 1 / (1 + math.exp(-value))
