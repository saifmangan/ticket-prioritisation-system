from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from ticket_prioritisation.ai import build_ai_brief
from ticket_prioritisation.prioritizer import Prioritizer, TicketInput


app = FastAPI(
    title="Ticket Prioritisation AI",
    description="Explainable revenue and SLA-aware ticket prioritisation API.",
    version="1.0.0",
)
prioritizer = Prioritizer()


class TicketRequest(BaseModel):
    subject: str
    message: str
    customer: str = "Unknown customer"
    customer_tier: str = Field("standard", examples=["standard", "premium", "enterprise"])
    affected_users: int = Field(1, ge=1)
    revenue_at_risk: float = Field(0, ge=0)
    hours_until_sla: float | None = Field(None, ge=0)
    channel: str = "email"
    created_at: str | None = None
    include_ai_brief: bool = True


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/prioritise")
def prioritise_ticket(request: TicketRequest) -> dict:
    ticket = TicketInput(
        subject=request.subject,
        message=request.message,
        customer=request.customer,
        customer_tier=request.customer_tier,
        affected_users=request.affected_users,
        revenue_at_risk=request.revenue_at_risk,
        hours_until_sla=request.hours_until_sla,
        channel=request.channel,
        created_at=request.created_at,
    )
    result = prioritizer.prioritize(ticket)
    payload = result.to_dict()
    if request.include_ai_brief:
        payload["ai_brief"] = build_ai_brief(ticket, result)
    return payload
