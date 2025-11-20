import unittest
from agent.agent import BusinessGrowthAgent


class TestBusinessGrowthAgent(unittest.TestCase):
    """Unit tests for BusinessGrowthAgent."""

    def setUp(self):
        self.agent = BusinessGrowthAgent(mode="rule")

    def test_analyze_company_basic(self):
        """Test basic company profile analysis."""
        text = "We are a SaaS B2B startup with $500k ARR."
        result = self.agent.analyze_company(text)
        self.assertIn("saas", result.get("tags", []))
        self.assertIn("b2b", result.get("tags", []))
        self.assertEqual(result.get("revenue"), 500000)

    def test_analyze_company_revenue_million(self):
        """Test revenue parsing with millions."""
        text = "Our company has $2.5 million in revenue."
        result = self.agent.analyze_company(text)
        self.assertEqual(result.get("revenue"), 2500000)

    def test_analyze_company_stage_detection(self):
        """Test stage detection."""
        text = "Series A company"
        result = self.agent.analyze_company(text)
        self.assertEqual(result.get("stage"), "growth (Series A+)")

    def test_analyze_company_marketplace_tag(self):
        """Test marketplace tag detection."""
        text = "We run a marketplace platform for freelancers."
        result = self.agent.analyze_company(text)
        self.assertIn("marketplace", result.get("tags", []))

    def test_suggest_strategies_returns_list(self):
        """Test that strategy suggestions return a list."""
        company = {"tags": ["saas", "b2b"], "revenue": 500000, "stage": "growth"}
        strategies = self.agent.suggest_strategies(company)
        self.assertIsInstance(strategies, list)
        self.assertGreater(len(strategies), 0)

    def test_suggest_strategies_has_required_fields(self):
        """Test that strategies have required fields."""
        company = {"tags": ["saas"], "revenue": 100000}
        strategies = self.agent.suggest_strategies(company)
        for s in strategies:
            self.assertIn("title", s)
            self.assertIn("rationale", s)
            self.assertIn("actions", s)

    def test_prioritize_actions_returns_sorted_list(self):
        """Test that prioritization returns sorted strategies."""
        strategies = [
            {
                "title": "Strategy 1",
                "rationale": "High impact",
                "effort": "low",
                "impact": "high",
                "actions": ["action 1"],
            },
            {
                "title": "Strategy 2",
                "rationale": "Low impact",
                "effort": "high",
                "impact": "low",
                "actions": ["action 2"],
            },
        ]
        prioritized = self.agent.prioritize_actions(strategies)
        self.assertEqual(len(prioritized), 2)
        # High impact + low effort should rank first
        self.assertEqual(prioritized[0]["title"], "Strategy 1")

    def test_run_profile_returns_dict(self):
        """Test that run_profile returns a complete output dict."""
        text = "Acme is a SaaS startup with $1M ARR."
        output = self.agent.run_profile(text)
        self.assertIn("company", output)
        self.assertIn("strategies", output)
        self.assertIn("prioritized", output)
        self.assertIsInstance(output["company"], dict)
        self.assertIsInstance(output["strategies"], list)
        self.assertIsInstance(output["prioritized"], list)

    def test_run_profile_with_market_notes(self):
        """Test run_profile with market notes."""
        text = "SaaS startup"
        market = "Enterprise market is growing"
        output = self.agent.run_profile(text, market)
        self.assertIn("strategies", output)


if __name__ == "__main__":
    unittest.main()
