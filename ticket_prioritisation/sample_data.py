from __future__ import annotations

from .prioritizer import TicketInput


SAMPLE_TICKETS = [
    TicketInput(
        subject="Production checkout is down",
        message="URGENT: customers cannot pay and our checkout is down in production.",
        customer="Northstar Retail",
        customer_tier="enterprise",
        affected_users=480,
        revenue_at_risk=25000,
        hours_until_sla=0.5,
        channel="slack",
    ),
    TicketInput(
        subject="Need invoice corrected",
        message="The subscription invoice has the wrong billing address. Please help before renewal.",
        customer="BrightWorks",
        customer_tier="premium",
        affected_users=2,
        revenue_at_risk=1800,
        hours_until_sla=12,
    ),
    TicketInput(
        subject="Feature question",
        message="Thanks for the great product. Can you explain how exports work?",
        customer="Solo Studio",
        customer_tier="standard",
        affected_users=1,
        revenue_at_risk=0,
        hours_until_sla=48,
    ),
]
