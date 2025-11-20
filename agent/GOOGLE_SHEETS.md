# Google Sheets Integration

The Business Growth Agent can read company profiles from a Google Sheet and write analysis results back.

## Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

### 2. Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details and click "Create and Continue"
4. Skip "Grant this service account access to project" (optional)
5. Click "Create Key" > "JSON"
6. Save the JSON key file (e.g., `credentials.json`)

### 3. Share Your Google Sheet

1. Create a Google Sheet or use an existing one
2. Note the spreadsheet ID (from the URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}`)
3. Share the sheet with the service account email (found in the JSON key: `client_email`)
4. Give it Editor access

### 4. Prepare Your Data

Create two worksheets in your Google Sheet:

**Profiles sheet** (columns):
- `company_name`: Name of the company
- `profile_text`: Free-text company description (required)
- `market_notes`: Optional market context

Example:
```
company_name | profile_text | market_notes
Acme Corp    | SaaS B2B startup, $1M ARR | Enterprise market growing 20% YoY
Startup Inc  | Marketplace for freelancers | Competitive market, 50+ players
```

**Results sheet** (auto-created):
- `company_name`: Name analyzed
- `top_strategy`: The highest-priority strategy
- `top_rationale`: Why this strategy is recommended

## Usage

### Command-line

```bash
export GOOGLE_SHEETS_CREDENTIALS="path/to/credentials.json"
export GOOGLE_SHEETS_ID="your-spreadsheet-id"
python agent/examples/batch_analyze_sheets.py
```

The script will:
1. Read profiles from the "Profiles" worksheet
2. Run the agent on each profile
3. Write results to the "Results" worksheet

### Python API

```python
from agent.agent import BusinessGrowthAgent
from agent.connectors.google_sheets_connector import GoogleSheetsConnector

# Initialize
connector = GoogleSheetsConnector("credentials.json", "spreadsheet-id")
agent = BusinessGrowthAgent(mode="rule")

# Read profiles and analyze
results = connector.read_and_analyze(agent)

# Or read/write separately
profiles = connector.read_profiles("Profiles")
# ... process profiles ...
connector.write_results(results, "Results")
```

## Security

- **Keep credentials.json secret**: Add it to `.gitignore` and never commit it
- **Use environment variables**: Store credentials path and spreadsheet ID as env vars
- **Limit sharing**: Only share the Google Sheet with the service account; don't share with team members unless necessary
- **Audit access**: Review sharing settings regularly

## Troubleshooting

### "Failed to authenticate"
- Check that the credentials.json file exists and is valid
- Verify the service account email has Editor access to the sheet

### "Worksheet not found"
- Create the worksheet manually or use the API to create it
- Check spelling of worksheet names (case-sensitive)

### "Permission denied"
- Ensure you've shared the Google Sheet with the service account email
- The service account needs Editor (not Viewer) permissions

## Next Steps

- Add email notifications when results are ready
- Schedule batch runs with APScheduler
- Add a web dashboard to visualize historical results
