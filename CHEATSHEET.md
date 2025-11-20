# Agent Cheat Sheet

## Installation
```bash
git clone https://github.com/isrealsimon673-eng/Newsletter-.git
cd Newsletter-
python -m pip install -r agent/requirements.txt
```

## Quick Commands

### Basic (no config needed)
```bash
python agent/main.py --profile profile.txt
```

### With market notes
```bash
python agent/main.py --profile profile.txt --market market.txt
```

### LLM mode (AI-powered)
```bash
export OPENAI_API_KEY="sk-..."
python agent/main.py --profile profile.txt --mode llm
```

### Post to Slack
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
python agent/main.py --profile profile.txt --slack-webhook "$SLACK_WEBHOOK_URL"
```

### Batch analysis (Google Sheets)
```bash
export GOOGLE_SHEETS_CREDENTIALS="creds.json"
export GOOGLE_SHEETS_ID="sheet-id"
python agent/examples/batch_analyze_sheets.py
```

### Run tests
```bash
python -m pytest agent/tests/ -v
```

### Docker
```bash
docker build -t growth-agent .
docker run --rm growth-agent --profile agent/examples/sample_profile.txt
```

## Profile Format

Create a text file with company info:

```
Company Name: Acme Analytics
Type: SaaS B2B
Revenue: $2M ARR
Stage: Series A
Key Features: Real-time dashboards, data pipelines
Target: Mid-market retail chains
```

## Output Structure

```json
{
  "company": {
    "tags": ["saas", "b2b"],
    "revenue": 2000000,
    "stage": "growth (Series A+)",
    "model": "SaaS"
  },
  "strategies": [...],
  "prioritized": [
    {
      "title": "Strategy name",
      "rationale": "Why this works",
      "effort": "medium",
      "impact": "high",
      "actions": ["Action 1", "Action 2", "Action 3"]
    }
  ]
}
```

## Environment Variables

```bash
OPENAI_API_KEY          # OpenAI API key (optional, for LLM mode)
SLACK_WEBHOOK_URL       # Slack webhook (optional, for notifications)
GOOGLE_SHEETS_CREDENTIALS  # Path to service account JSON (optional)
GOOGLE_SHEETS_ID        # Google Sheets ID (optional)
```

## Python API

```python
from agent.agent import BusinessGrowthAgent

agent = BusinessGrowthAgent(mode="rule")
result = agent.run_profile("Company profile text", "Market notes")

# Access results
print(result["prioritized"][0]["title"])
```

## File Structure

```
agent/
├── agent.py                    # Core agent logic
├── main.py                     # CLI entry point
├── llm_client.py              # OpenAI integration
├── connectors/
│   ├── slack_connector.py     # Slack notifier
│   └── google_sheets_connector.py  # Google Sheets I/O
├── examples/
│   ├── sample_profile.txt     # Example company profile
│   └── batch_analyze_sheets.py  # Batch analysis script
├── tests/
│   ├── test_agent.py          # Agent tests (9)
│   ├── test_slack.py          # Slack tests (4)
│   └── test_google_sheets.py  # Sheets tests (3)
├── requirements.txt           # Python dependencies
└── README.md                  # Full documentation
```

## Links

- **README.md**: Full feature overview
- **DEPLOYMENT.md**: Docker, OpenShift, CI/CD
- **GOOGLE_SHEETS.md**: Google Sheets setup
- **NOTES_SLACK.md**: Slack integration

## Common Issues

| Issue | Solution |
|-------|----------|
| Import error | `pip install -r agent/requirements.txt` |
| OPENAI_API_KEY not set | `export OPENAI_API_KEY="sk-..."` |
| Slack fails | Install requests: `pip install requests` |
| Sheets auth fails | Check credentials.json path and service account sharing |

---

**Version**: 1.0 | **Tests**: 16 passing ✅ | **Python**: 3.9+ | **License**: MIT
