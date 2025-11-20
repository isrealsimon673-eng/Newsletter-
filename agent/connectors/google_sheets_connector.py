import logging
from typing import List, Dict, Optional

try:
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    import gspread
    HAS_GOOGLE_SHEETS = True
except Exception:  # pragma: no cover - optional dependency
    gspread = None
    Credentials = None
    HAS_GOOGLE_SHEETS = False

logger = logging.getLogger(__name__)


class GoogleSheetsConnector:
    """Google Sheets connector to read company profiles and write strategy results.

    Requires a Google Cloud service account JSON key file.

    Usage:
        connector = GoogleSheetsConnector(credentials_file, spreadsheet_id)
        profiles = connector.read_profiles(sheet_name="Profiles")
        connector.write_results(results, sheet_name="Results")
    """

    def __init__(self, credentials_file: str, spreadsheet_id: str):
        """Initialize the connector with service account credentials.

        Args:
            credentials_file: path to Google Cloud service account JSON key
            spreadsheet_id: the Google Sheets spreadsheet ID
        """
        if not HAS_GOOGLE_SHEETS:
            raise RuntimeError("Google Sheets support requires gspread and google-auth. Install them and try again.")
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.client = self._authenticate()
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)

    def _authenticate(self):
        """Authenticate with Google Sheets API using service account."""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            return gspread.authorize(credentials)
        except Exception as e:
            logger.error("Failed to authenticate with Google Sheets: %s", e)
            raise RuntimeError(f"Google Sheets authentication failed: {e}")

    def read_profiles(self, sheet_name: str = "Profiles") -> List[Dict]:
        """Read company profiles from a Google Sheet.

        Expected columns: company_name, profile_text, market_notes (optional)

        Args:
            sheet_name: the worksheet name to read from

        Returns:
            list of dicts with keys: company_name, profile_text, market_notes
        """
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            records = worksheet.get_all_records()
            return records
        except Exception as e:
            logger.error("Failed to read profiles from %s: %s", sheet_name, e)
            raise RuntimeError(f"Failed to read profiles: {e}")

    def write_results(
        self,
        results: List[Dict],
        sheet_name: str = "Results",
        append: bool = True,
    ) -> int:
        """Write strategy results to a Google Sheet.

        Args:
            results: list of result dicts, each with keys:
                     company_name, prioritized (list of strategies)
            sheet_name: the worksheet name to write to
            append: if True, append to sheet; if False, clear and write

        Returns:
            number of rows written
        """
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except Exception:
            # Sheet doesn't exist; create it
            worksheet = self.spreadsheet.add_worksheet(sheet_name, rows=1, cols=3)

        if not append:
            worksheet.clear()

        # Prepare rows: company_name, top_strategy, top_rationale
        rows = [["company_name", "top_strategy", "top_rationale"]]
        for res in results:
            company_name = res.get("company_name", "Unknown")
            prioritized = res.get("prioritized", [])
            top_strategy = ""
            top_rationale = ""
            if prioritized:
                top_strategy = prioritized[0].get("title", "")
                top_rationale = prioritized[0].get("rationale", "")

            rows.append([company_name, top_strategy, top_rationale])

        # Write to sheet
        worksheet.append_rows(rows[1:])  # Skip header if appending to existing
        logger.info("Wrote %d results to %s", len(rows) - 1, sheet_name)
        return len(rows) - 1

    def read_and_analyze(
        self,
        agent,
        profile_sheet: str = "Profiles",
        results_sheet: str = "Results",
    ) -> List[Dict]:
        """Convenience method to read profiles, run the agent, and write results.

        Args:
            agent: a BusinessGrowthAgent instance
            profile_sheet: source worksheet name
            results_sheet: target worksheet name

        Returns:
            list of analysis results
        """
        profiles = self.read_profiles(profile_sheet)
        results = []
        for profile in profiles:
            company_name = profile.get("company_name", "Unknown")
            profile_text = profile.get("profile_text", "")
            market_notes = profile.get("market_notes", "")

            if not profile_text:
                logger.warning("Skipping %s: no profile_text", company_name)
                continue

            analysis = agent.run_profile(profile_text, market_notes)
            analysis["company_name"] = company_name
            results.append(analysis)

        self.write_results(results, results_sheet, append=False)
        return results
