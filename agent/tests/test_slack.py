import unittest
from agent.connectors.slack_connector import SlackNotifier


class TestSlackNotifier(unittest.TestCase):
    """Unit tests for SlackNotifier."""

    def test_init_requires_webhook_url(self):
        """Test that SlackNotifier requires a webhook URL."""
        with self.assertRaises(ValueError):
            SlackNotifier("")

    def test_init_accepts_webhook_url(self):
        """Test that SlackNotifier accepts a valid URL."""
        url = "https://hooks.slack.com/services/TEST"
        notifier = SlackNotifier(url)
        self.assertEqual(notifier.webhook_url, url)

    def test_build_text_formats_strategies(self):
        """Test that _build_text formats strategies correctly."""
        strategies = [
            {
                "title": "Test Strategy",
                "rationale": "Good reason",
                "actions": ["Action 1", "Action 2"],
            }
        ]
        notifier = SlackNotifier("https://hooks.slack.com/services/TEST")
        text = notifier._build_text(strategies)
        self.assertIn("Test Strategy", text)
        self.assertIn("Good reason", text)
        self.assertIn("Action 1", text)

    def test_build_text_limits_to_five_strategies(self):
        """Test that _build_text limits to top 5 strategies."""
        strategies = [
            {"title": f"Strategy {i}", "rationale": f"Reason {i}", "actions": []}
            for i in range(10)
        ]
        notifier = SlackNotifier("https://hooks.slack.com/services/TEST")
        text = notifier._build_text(strategies)
        # Should only contain first 5
        self.assertIn("Strategy 0", text)
        self.assertNotIn("Strategy 9", text)


if __name__ == "__main__":
    unittest.main()
