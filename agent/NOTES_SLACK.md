# Slack Notifications (Quick Guide)

You can post the agent's prioritized recommendations to Slack using an incoming
webhook. This guide explains the simple usage.

1) Configure
- Add `SLACK_WEBHOOK_URL` to your environment or pass `--slack-webhook` on the CLI.
- The example `.env.example` includes the `SLACK_WEBHOOK_URL` placeholder.

2) Install requirements

```bash
python -m pip install -r agent/requirements.txt
```

3) Run and post

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
python agent/main.py --profile agent/examples/sample_profile.txt --mode rule
```

Or provide webhook on CLI:

```bash
python agent/main.py --profile agent/examples/sample_profile.txt --mode rule --slack-webhook "https://hooks.slack.com/services/..."
```

Behavior
- The notifier posts the top 5 prioritized strategies as a Slack message (markdown blocks).
- If the `requests` package is missing the CLI will raise an error pointing you to install it.

Security
- Treat webhook URLs as secrets and avoid committing them to the repo.
- For production, consider a more secure integration (OAuth apps) and fine-grained access controls.
