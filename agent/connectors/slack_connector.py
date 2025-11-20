import json
import logging
from typing import List, Dict, Optional

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Simple Slack notifier using an incoming webhook URL.

    Usage:
        notifier = SlackNotifier(webhook_url)
        notifier.send_summary(prioritized_actions)
    """

    def __init__(self, webhook_url: str):
        if not webhook_url:
            raise ValueError("webhook_url is required")
        if requests is None:
            raise RuntimeError("requests package is not installed; add it to requirements.txt")
        self.webhook_url = webhook_url

    def _build_text(self, prioritized: List[Dict]) -> str:
        lines = ["*Top recommended strategies*:\n"]
        for i, s in enumerate(prioritized[:5], start=1):
            lines.append(f"*{i}. {s.get('title')}* — {s.get('rationale')}")
            actions = s.get('actions', [])
            if actions:
                lines.append("• Actions:")
                for a in actions[:3]:
                    lines.append(f"  - {a}")
            lines.append("")
        return "\n".join(lines)

    def send_summary(self, prioritized: List[Dict], title: Optional[str] = None) -> Dict:
        payload = {
            "text": (title or "Business Growth Agent Recommendations"),
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": self._build_text(prioritized)}}
            ],
        }

        resp = requests.post(self.webhook_url, json=payload, timeout=10)
        if resp.status_code not in (200, 201):
            logger.error("Slack webhook failed: %s %s", resp.status_code, resp.text)
            raise RuntimeError(f"Slack webhook failed: {resp.status_code} {resp.text}")
        return {"status": "ok", "code": resp.status_code}
