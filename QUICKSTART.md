# Business Growth Agent — Quick Start Guide

Get up and running in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/isrealsimon673-eng/Newsletter-.git
cd Newsletter-

# Install dependencies
python -m pip install -r agent/requirements.txt
```

## Basic Usage (Rule-Based, No API Keys Required)

```bash
# Analyze a company profile
python agent/main.py --profile agent/examples/sample_profile.txt

# Output: JSON with company analysis, strategies, and prioritized recommendations
```

**Output format:**
```json
{
  "company": {
    "tags": ["saas", "b2b"],
    "revenue": 750000,
    "stage": "growth (Series A+)",
    "model": "SaaS"
  },
  "strategies": [
    {
      "title": "Improve onboarding conversion",
      "rationale": "Small onboarding improvements often increase activation and retention.",
      "effort": "medium",
      "impact": "high",
      "actions": ["Map current onboarding funnel...", "Run 3 A/B tests..."]
    }
  ],
  "prioritized": [
    // same strategies, sorted by impact/effort ratio
  ]
}
```

## Common Use Cases

### 1. Analyze a Single Company (CLI)

Create a text file with your company profile:

```bash
cat > my_company.txt << 'EOF'
Acme Analytics is a SaaS B2B startup with $2M ARR.
We build real-time data pipelines and dashboards for retail chains.
Target market: mid-market retailers with 50-500 stores.
Main competitors: Tableau, Looker (but for retail-specific use cases).
EOF

python agent/main.py --profile my_company.txt
```

### 2. Analyze with Market Notes

```bash
python agent/main.py \
  --profile my_company.txt \
  --market market_notes.txt
```

Where `market_notes.txt` contains context like:
```
Enterprise market is growing 20% YoY.
Buyers are heads of analytics and operations.
```

### 3. Batch Analyze Multiple Companies (Google Sheets)

Set up Google Sheets integration for bulk analysis:

```bash
export GOOGLE_SHEETS_CREDENTIALS="path/to/credentials.json"
export GOOGLE_SHEETS_ID="your-spreadsheet-id"
python agent/examples/batch_analyze_sheets.py
```

This reads from a "Profiles" sheet and writes results to a "Results" sheet.
See `GOOGLE_SHEETS.md` for full setup instructions.

### 4. Post Results to Slack

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
python agent/main.py \
  --profile my_company.txt \
  --slack-webhook "$SLACK_WEBHOOK_URL"
```

Or use the `--slack-webhook` CLI flag to override the environment variable.

### 5. Use LLM Mode (OpenAI)

For AI-powered strategy generation:

```bash
export OPENAI_API_KEY="sk-..."
python agent/main.py \
  --profile my_company.txt \
  --mode llm
```

The agent uses OpenAI's function-calling to generate and parse strategies as JSON.

## Understanding the Output

**Company Analysis:**
- `tags`: detected company type (saas, b2b, b2c, marketplace)
- `revenue`: extracted annual revenue in dollars
- `stage`: inferred stage (pre-seed/seed, growth, revenue-generating)
- `model`: business model (SaaS, etc.)

**Strategies:**
- `title`: strategy name
- `rationale`: why this strategy works
- `effort`: estimated effort (low, medium, high, very-high)
- `impact`: expected impact (low, medium, high, very-high)
- `actions`: concrete next steps (3 actionable items)

**Prioritized:**
- Same as strategies, but sorted by a score: `impact * 10 - effort * 5`
- Higher scores = do first

## Testing

Run the test suite to verify everything works:

```bash
python -m pytest agent/tests/ -v
```

All 16 tests should pass.

## Configuration Files

Create an `.env` file for environment variables (see `.env.example`):

```bash
cp agent/.env.example .env
# Edit .env with your credentials
```

Environment variables:
- `OPENAI_API_KEY`: OpenAI API key (optional, for LLM mode)
- `SLACK_WEBHOOK_URL`: Slack incoming webhook (optional, for notifications)
- `GOOGLE_SHEETS_CREDENTIALS`: Path to Google Cloud service account JSON (optional)
- `GOOGLE_SHEETS_ID`: Google Sheets spreadsheet ID (optional)

## Docker

Build and run the agent in a container:

```bash
docker build -t growth-agent .

# Rule-based mode
docker run --rm growth-agent \
  --profile agent/examples/sample_profile.txt

# LLM mode
docker run --rm -e OPENAI_API_KEY="sk-..." growth-agent \
  --profile agent/examples/sample_profile.txt --mode llm

# With Slack
docker run --rm -e SLACK_WEBHOOK_URL="https://..." growth-agent \
  --profile agent/examples/sample_profile.txt --slack-webhook "$SLACK_WEBHOOK_URL"
```

## API Usage (Python)

Use the agent programmatically:

```python
from agent.agent import BusinessGrowthAgent

agent = BusinessGrowthAgent(mode="rule")

profile_text = "SaaS B2B startup with $1M ARR..."
market_notes = "Enterprise market growing fast"

result = agent.run_profile(profile_text, market_notes)

# Access components
company = result["company"]
strategies = result["strategies"]
prioritized = result["prioritized"]

print(f"Stage: {company['stage']}")
print(f"Top strategy: {prioritized[0]['title']}")
```

## Next Steps

- **Extend strategies**: Edit `agent/agent.py` to add more rule-based strategies
- **Use LLM**: Set `OPENAI_API_KEY` and use `--mode llm` for AI-powered recommendations
- **Integrate with Slack**: Set `SLACK_WEBHOOK_URL` to post results to Slack channels
- **Batch analysis**: Use Google Sheets connector for bulk company analysis
- **Schedule runs**: Use APScheduler or cron to run analyses on a schedule

## Troubleshooting

### Import errors
```bash
python -m pip install -r agent/requirements.txt
```

### LLM mode fails: "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-..."
python agent/main.py --profile ... --mode llm
```

### Slack notification fails: "requests package not installed"
```bash
python -m pip install requests
```

### Google Sheets: "Credentials not found"
```bash
export GOOGLE_SHEETS_CREDENTIALS="path/to/credentials.json"
python agent/examples/batch_analyze_sheets.py
```

## Documentation

- `README.md`: Overview and features
- `DEPLOYMENT.md`: Docker, OpenShift, GitHub Actions
- `GOOGLE_SHEETS.md`: Google Sheets setup and usage
- `NOTES_SLACK.md`: Slack integration notes
- `agent/examples/`: Example scripts and data

## Support

For issues or questions, check:
1. The relevant `.md` file in `agent/` directory
2. Test examples in `agent/tests/`
3. Example scripts in `agent/examples/`

Good luck! 🚀
