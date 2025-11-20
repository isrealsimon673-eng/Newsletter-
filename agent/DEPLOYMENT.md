# Deployment & Delivery

This guide covers containerization, deployment strategies, and operations.

## Docker

The included `Dockerfile` builds a lightweight Python 3.11 image (~200MB base).

Build:
```bash
docker build -t growth-agent .
```

Run rule-based agent locally:
```bash
docker run --rm growth-agent --profile agent/examples/sample_profile.txt --mode rule
```

Run with LLM mode (requires `OPENAI_API_KEY` in environment):
```bash
docker run --rm \
  -e OPENAI_API_KEY="sk-..." \
  growth-agent --profile agent/examples/sample_profile.txt --mode llm
```

Run with Slack webhook:
```bash
docker run --rm \
  -e SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..." \
  growth-agent --profile agent/examples/sample_profile.txt --mode rule
```

## OpenShift

The repository includes `.github/workflows/openshift.yml` for container deployment.
Refer to that workflow for setup of `OPENSHIFT_SERVER` and `OPENSHIFT_TOKEN` secrets.

## GitHub Actions

Two workflows are configured:

1. **tests.yml**: Runs on push/PR to main
   - Installs dependencies
   - Runs unit tests (pytest)
   - Lint checks (flake8)
   - Uploads coverage to Codecov

2. **openshift.yml**: Builds, pushes to GHCR, and deploys to OpenShift (on main push)
   - Requires OpenShift secrets configured

## Local Development

Install dependencies and run tests:

```bash
python -m pip install -r agent/requirements.txt
python -m pytest agent/tests/ -v
python -m flake8 agent --max-line-length=100
```

Run the agent:

```bash
python agent/main.py --profile agent/examples/sample_profile.txt --mode rule
```

## Environment Variables

Key environment variables for the agent:

- `OPENAI_API_KEY`: (optional) OpenAI API key for LLM mode
- `SLACK_WEBHOOK_URL`: (optional) Slack incoming webhook URL to post results
- `AGENT_MODE`: (optional, default: rule) Agent mode: 'rule' or 'llm'

See `.env.example` for a template.

## Next Steps (Future Enhancements)

- **Google Sheets connector**: Read company profiles and market data from a Google Sheet; write results back.
- **CRM connector**: Integrate with Salesforce, HubSpot, or similar to fetch customer segments and enrich with market data.
- **Email notifier**: Send summaries via email instead of (or in addition to) Slack.
- **Scheduling**: Add a scheduler (e.g., APScheduler) to run the agent on a cron schedule.
- **Dashboard**: Build a simple web UI to display strategy recommendations and historical runs.
- **Advanced LLM**: Use tools/function-calling for multi-turn conversations with the agent to refine strategies.
