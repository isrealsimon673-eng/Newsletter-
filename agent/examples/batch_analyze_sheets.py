#!/usr/bin/env python3
"""Example: Batch analyze companies from Google Sheets.

This script reads company profiles from a Google Sheet, runs the agent on each,
and writes results back to a different sheet.

Setup:
  1. Create a Google Cloud project and enable Sheets API
  2. Create a service account and download the JSON key
  3. Share your Google Sheet with the service account email
  4. Update CREDENTIALS_FILE and SPREADSHEET_ID below
"""

import sys
import os

try:
    from agent.agent import BusinessGrowthAgent
    from agent.connectors.google_sheets_connector import GoogleSheetsConnector
except Exception as e:
    print(f"Error importing: {e}")
    print("Make sure dependencies are installed: pip install -r agent/requirements.txt")
    sys.exit(1)


def main():
    # Configuration (update these!)
    CREDENTIALS_FILE = os.environ.get("GOOGLE_SHEETS_CREDENTIALS", "credentials.json")
    SPREADSHEET_ID = os.environ.get("GOOGLE_SHEETS_ID", "your-spreadsheet-id")

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: credentials file not found at {CREDENTIALS_FILE}")
        print("Set GOOGLE_SHEETS_CREDENTIALS environment variable or provide credentials.json")
        sys.exit(1)

    if SPREADSHEET_ID == "your-spreadsheet-id":
        print("Error: SPREADSHEET_ID not configured")
        print("Set GOOGLE_SHEETS_ID environment variable")
        sys.exit(1)

    print(f"Connecting to Google Sheets: {SPREADSHEET_ID}")
    try:
        connector = GoogleSheetsConnector(CREDENTIALS_FILE, SPREADSHEET_ID)
    except Exception as e:
        print(f"Failed to connect to Google Sheets: {e}")
        sys.exit(1)

    print("Creating agent (rule-based mode)...")
    agent = BusinessGrowthAgent(mode="rule")

    print("Reading profiles from 'Profiles' sheet...")
    try:
        results = connector.read_and_analyze(
            agent,
            profile_sheet="Profiles",
            results_sheet="Results",
        )
        print(f"Analyzed {len(results)} companies. Results written to 'Results' sheet.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
