#!/usr/bin/env python3
"""
Example: Run agent on company profiles from Google Sheets and write results back.

Usage:
    python agent/sheets_batch.py \
        --spreadsheet-id "YOUR_SHEET_ID" \
        --key-file path/to/service_account.json \
        --input-sheet "Companies" \
        --output-sheet "Results"

Requires:
    - GOOGLE_SHEETS_KEY_PATH env var or --key-file argument
    - A Google Sheet with columns: Company, Profile, Market Notes
"""

import argparse
import json
import os
from pathlib import Path

from agent.agent import BusinessGrowthAgent
from agent.connectors.sheets_connector import GoogleSheetsConnector


def main():
    p = argparse.ArgumentParser(
        description="Run Business Growth Agent on profiles from Google Sheets"
    )
    p.add_argument("--spreadsheet-id", required=True, help="Google Sheets spreadsheet ID")
    p.add_argument(
        "--key-file", required=False, help="Service account JSON key file path"
    )
    p.add_argument(
        "--input-sheet", default="Companies", help="Sheet name with company profiles"
    )
    p.add_argument(
        "--output-sheet", default="Results", help="Sheet name to write results to"
    )
    p.add_argument(
        "--mode", choices=["rule", "llm"], default="rule", help="Agent mode"
    )

    args = p.parse_args()

    # Initialize connector
    connector = GoogleSheetsConnector(args.spreadsheet_id, key_file_path=args.key_file)

    # Read profiles from input sheet
    print(f"Reading profiles from sheet '{args.input_sheet}'...")
    profiles = connector.read_profiles(args.input_sheet)
    print(f"Found {len(profiles)} company profiles.\n")

    # Initialize agent
    agent = BusinessGrowthAgent(mode=args.mode)

    # Process each profile
    results = []
    for profile_data in profiles:
        company = profile_data.get("company", "Unknown")
        profile_text = profile_data.get("profile", "")
        market_notes = profile_data.get("market_notes", "")

        print(f"Processing: {company}")
        output = agent.run_profile(profile_text, market_notes)
        
        # Flatten output for easier writing to sheets
        result_item = {
            "company": company,
            "strategies": output.get("strategies", []),
            "prioritized": output.get("prioritized", []),
        }
        results.append(result_item)

    # Write results to output sheet
    print(f"\nWriting {len(results)} results to sheet '{args.output_sheet}'...")
    write_output = connector.write_results(args.output_sheet, results)
    print(f"Done: {write_output}")


if __name__ == "__main__":
    main()
