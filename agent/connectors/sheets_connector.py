import os
from typing import List, Dict, Optional

try:
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import Request
    import gspread
except Exception:  # pragma: no cover - optional dependency
    gspread = None
    Credentials = None


class GoogleSheetsConnector:
    """Simple Google Sheets connector for reading/writing agent data.

    Requires a service account JSON key file. Set GOOGLE_SHEETS_KEY_PATH environment
    variable or pass key_file_path to the constructor.

    Usage:
        connector = GoogleSheetsConnector(spreadsheet_id, key_file_path)
        profiles = connector.read_profiles(sheet_name="Companies")
        connector.write_results(sheet_name="Results", results=output)
    """

    def __init__(self, spreadsheet_id: str, key_file_path: Optional[str] = None):
        if gspread is None:
            raise RuntimeError(
                "Google Sheets support requires 'google-auth' and 'gspread' packages. "
                "Install them: pip install google-auth-oauthlib gspread"
            )
        
        self.spreadsheet_id = spreadsheet_id
        key_path = key_file_path or os.environ.get("GOOGLE_SHEETS_KEY_PATH")
        
        if not key_path:
            raise ValueError(
                "key_file_path is required or set GOOGLE_SHEETS_KEY_PATH environment variable"
            )
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Service account key file not found: {key_path}")
        
        # Authenticate with Google Sheets API
        self.credentials = Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        self.client = gspread.Authorized(self.credentials)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)

    def read_profiles(self, sheet_name: str) -> List[Dict]:
        """Read company profiles from a sheet.

        Expected columns: Company, Profile, Market Notes
        Returns a list of dicts with keys: company, profile, market_notes
        """
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except Exception as e:
            raise ValueError(f"Sheet '{sheet_name}' not found: {e}")
        
        rows = worksheet.get_all_records()
        profiles = []
        
        for row in rows:
            profiles.append({
                "company": row.get("Company", ""),
                "profile": row.get("Profile", ""),
                "market_notes": row.get("Market Notes", ""),
            })
        
        return profiles

    def write_results(
        self, sheet_name: str, results: List[Dict], create_if_missing: bool = True
    ) -> Dict:
        """Write agent results to a sheet.

        Results should be a list of dicts with keys: company, strategies, prioritized
        Creates or appends to the sheet.
        """
        # Try to get the worksheet; create if it doesn't exist
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except Exception:
            if create_if_missing:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=5)
                # Add headers
                worksheet.append_row(["Company", "Top Strategy", "Impact", "Effort", "Actions"])
            else:
                raise ValueError(f"Sheet '{sheet_name}' not found and create_if_missing=False")
        
        # Append results
        for result in results:
            if not result:
                continue
            
            company = result.get("company", "")
            prioritized = result.get("prioritized", [])
            
            if prioritized:
                top = prioritized[0]
                strategy = top.get("title", "")
                impact = top.get("impact", "")
                effort = top.get("effort", "")
                actions = "; ".join(top.get("actions", [])[:2])  # First 2 actions
            else:
                strategy = impact = effort = actions = ""
            
            worksheet.append_row([company, strategy, impact, effort, actions])
        
        return {"status": "ok", "rows_written": len(results)}
