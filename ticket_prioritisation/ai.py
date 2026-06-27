from __future__ import annotations

import json
import os
from typing import Any

from .prioritizer import PrioritizationResult, TicketInput


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def build_ai_brief(ticket: TicketInput, result: PrioritizationResult) -> dict[str, Any]:
    """Return an LLM-generated brief when OpenAI is configured.

    The app works without this dependency. If the SDK or API key is missing,
    the caller receives a deterministic fallback that is still demo-friendly.
    """

    fallback = {
        "mode": "local-fallback",
        "summary": f"{ticket.customer} has a {result.priority.lower()} priority issue routed to {result.routing_team}.",
        "customer_reply": (
            f"Thanks for raising this. We have prioritised it as {result.priority} "
            f"and routed it to {result.routing_team}. We will provide the next update "
            f"within {result.sla_target_minutes} minutes."
        ),
        "internal_note": " | ".join(result.reasons),
    }

    if not os.getenv("OPENAI_API_KEY"):
        return fallback

    try:
        from openai import OpenAI

        client = OpenAI()
        prompt_payload = {
            "ticket": ticket.__dict__,
            "prioritisation": result.to_dict(),
        }
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert support operations assistant. "
                        "Write concise, commercially safe ticket triage output. "
                        "Return strict JSON with keys summary, customer_reply, internal_note."
                    ),
                },
                {"role": "user", "content": json.dumps(prompt_payload)},
            ],
        )
        text = response.output_text.strip()
        parsed = json.loads(text)
        parsed["mode"] = "openai"
        return parsed
    except Exception as exc:  # pragma: no cover - defensive integration fallback
        fallback["mode"] = "local-fallback-after-ai-error"
        fallback["ai_error"] = str(exc)
        return fallback
