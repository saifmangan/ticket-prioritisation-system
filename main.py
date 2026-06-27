from __future__ import annotations

import argparse
import json

from ticket_prioritisation.ai import build_ai_brief
from ticket_prioritisation.prioritizer import Prioritizer, TicketInput


def main() -> None:
    parser = argparse.ArgumentParser(description="Prioritise a support ticket.")
    parser.add_argument("--subject", default="Production login is down")
    parser.add_argument("--message", default="Urgent, our enterprise users cannot login and we are blocked.")
    parser.add_argument("--customer", default="Demo Customer")
    parser.add_argument("--tier", default="enterprise")
    parser.add_argument("--affected-users", type=int, default=50)
    parser.add_argument("--revenue-at-risk", type=float, default=5000)
    parser.add_argument("--hours-until-sla", type=float, default=2)
    parser.add_argument("--ai", action="store_true", help="Include optional OpenAI/customer brief output.")
    args = parser.parse_args()

    ticket = TicketInput(
        subject=args.subject,
        message=args.message,
        customer=args.customer,
        customer_tier=args.tier,
        affected_users=args.affected_users,
        revenue_at_risk=args.revenue_at_risk,
        hours_until_sla=args.hours_until_sla,
    )
    result = Prioritizer().prioritize(ticket)
    payload = result.to_dict()
    if args.ai:
        payload["ai_brief"] = build_ai_brief(ticket, result)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
