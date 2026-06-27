import unittest

from ticket_prioritisation.prioritizer import Prioritizer, TicketInput


class PrioritizerTest(unittest.TestCase):
    def test_critical_ticket_detects_revenue_and_sla_risk(self):
        ticket = TicketInput(
            subject="Checkout down",
            message="Urgent: production checkout is down and customers cannot pay.",
            customer="Northstar Retail",
            customer_tier="enterprise",
            affected_users=300,
            revenue_at_risk=20000,
            hours_until_sla=0.5,
        )

        result = Prioritizer().prioritize(ticket)

        self.assertEqual(result.priority, "Critical")
        self.assertGreaterEqual(result.score, 82)
        self.assertEqual(result.routing_team, "Platform engineering")
        self.assertIn("High-value account exposure", result.risk_flags)
        self.assertEqual(result.sla_target_minutes, 30)

    def test_low_risk_question_stays_low_or_medium(self):
        ticket = TicketInput(
            subject="Export question",
            message="Thanks, can you explain how account exports work?",
            customer_tier="standard",
            affected_users=1,
            revenue_at_risk=0,
            hours_until_sla=48,
        )

        result = Prioritizer().prioritize(ticket)

        self.assertIn(result.priority, {"Low", "Medium"})
        self.assertLess(result.score, 64)
        self.assertIn(result.routing_team, {"Customer support", "Data support"})

    def test_security_ticket_routes_to_security(self):
        ticket = TicketInput(
            subject="Possible security breach",
            message="We found a password leak and need immediate security help.",
            customer_tier="premium",
            affected_users=12,
            revenue_at_risk=0,
            hours_until_sla=3,
        )

        result = Prioritizer().prioritize(ticket)

        self.assertIn(result.priority, {"High", "Critical"})
        self.assertEqual(result.routing_team, "Security response")
        self.assertIn("Security-sensitive issue", result.risk_flags)


if __name__ == "__main__":
    unittest.main()
