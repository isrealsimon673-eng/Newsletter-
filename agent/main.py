#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from agent.agent import BusinessGrowthAgent

try:
    from agent.llm_client import OpenAIClient
except Exception:
    OpenAIClient = None

try:
    from agent.connectors.slack_connector import SlackNotifier
except Exception:
    SlackNotifier = None


def main():
    p = argparse.ArgumentParser(description="Run Business Growth Agent on a profile file")
    p.add_argument("--profile", required=True, help="Path to company profile text file")
    p.add_argument("--market", required=False, help="Optional market notes file")
    p.add_argument("--mode", choices=["rule", "llm"], default="rule", help="Agent mode: 'rule' or 'llm'")
    args = p.parse_args()

    profile_text = Path(args.profile).read_text(encoding="utf-8")
    market_text = ""
    if args.market:
        market_text = Path(args.market).read_text(encoding="utf-8")

    p.add_argument("--slack-webhook", required=False, help="Optional Slack incoming webhook URL to post results")
    args = p.parse_args()

    profile_text = Path(args.profile).read_text(encoding="utf-8")
    market_text = ""
    if args.market:
        market_text = Path(args.market).read_text(encoding="utf-8")

    agent = None
    if args.mode == "llm":
        if OpenAIClient is None:
            raise RuntimeError("LLM support requires the 'openai' package. Install it via requirements and try again.")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment. Set it to use LLM mode.")
        llm = OpenAIClient(api_key=api_key)
        agent = BusinessGrowthAgent(mode="llm", llm_client=llm)
    else:
        agent = BusinessGrowthAgent(mode="rule")

    out = agent.run_profile(profile_text, market_text)
    print(json.dumps(out, indent=2))

    # Optionally send results to Slack
    slack_webhook = args.slack_webhook or os.environ.get("SLACK_WEBHOOK_URL")
    if slack_webhook:
        if SlackNotifier is None:
            raise RuntimeError("Slack notifier requires the 'requests' package. Install it and try again.")
        notifier = SlackNotifier(slack_webhook)
        prioritized = out.get("prioritized", [])
        try:
            res = notifier.send_summary(prioritized)
            print("Slack notification sent:", res)
        except Exception as e:
            print("Failed to send Slack notification:", e)


if __name__ == "__main__":
    main()
