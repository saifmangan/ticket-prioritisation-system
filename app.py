from __future__ import annotations

import streamlit as st

from ticket_prioritisation.ai import build_ai_brief
from ticket_prioritisation.prioritizer import Prioritizer, TicketInput
from ticket_prioritisation.sample_data import SAMPLE_TICKETS


st.set_page_config(page_title="Ticket Prioritisation AI", page_icon="TPS", layout="wide")

prioritizer = Prioritizer()

st.title("Ticket Prioritisation AI")
st.caption("Revenue-aware support triage for teams that cannot afford missed escalations.")

sample_names = [f"{ticket.customer}: {ticket.subject}" for ticket in SAMPLE_TICKETS]
selected = st.sidebar.selectbox("Load customer demo", sample_names)
sample = SAMPLE_TICKETS[sample_names.index(selected)]

with st.sidebar:
    st.subheader("Commercial signal")
    customer = st.text_input("Customer", sample.customer)
    customer_tier = st.selectbox(
        "Tier",
        ["standard", "premium", "enterprise", "strategic", "free"],
        index=["standard", "premium", "enterprise", "strategic", "free"].index(sample.customer_tier),
    )
    affected_users = st.number_input("Affected users", min_value=1, value=sample.affected_users)
    revenue_at_risk = st.number_input("Revenue at risk (GBP)", min_value=0.0, value=float(sample.revenue_at_risk))
    hours_until_sla = st.number_input("Hours until SLA", min_value=0.0, value=float(sample.hours_until_sla or 24))
    channel = st.selectbox("Channel", ["email", "chat", "slack", "phone", "portal"], index=0)

subject = st.text_input("Subject", sample.subject)
message = st.text_area("Customer message", sample.message, height=180)

ticket = TicketInput(
    subject=subject,
    message=message,
    customer=customer,
    customer_tier=customer_tier,
    affected_users=int(affected_users),
    revenue_at_risk=float(revenue_at_risk),
    hours_until_sla=float(hours_until_sla),
    channel=channel,
)
result = prioritizer.prioritize(ticket)
brief = build_ai_brief(ticket, result)

metric_cols = st.columns(4)
metric_cols[0].metric("Priority", result.priority)
metric_cols[1].metric("Score", f"{result.score}/100")
metric_cols[2].metric("SLA target", f"{result.sla_target_minutes} min")
metric_cols[3].metric("Confidence", f"{result.confidence:.0%}")

left, right = st.columns([1, 1])

with left:
    st.subheader("Why it was prioritised")
    for reason in result.reasons:
        st.write(f"- {reason}")
    if result.risk_flags:
        st.subheader("Risk flags")
        for flag in result.risk_flags:
            st.warning(flag)

with right:
    st.subheader("Recommended response")
    st.write(f"**Route:** {result.routing_team}")
    for action in result.recommended_actions:
        st.write(f"- {action}")

st.subheader("AI customer brief")
st.json(brief)
