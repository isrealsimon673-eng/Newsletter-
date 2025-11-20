import unittest
from unittest.mock import Mock, patch, MagicMock


class TestGoogleSheetsConnector(unittest.TestCase):
    """Unit tests for GoogleSheetsConnector."""

    @patch("agent.connectors.google_sheets_connector.HAS_GOOGLE_SHEETS", True)
    @patch("agent.connectors.google_sheets_connector.gspread")
    @patch("agent.connectors.google_sheets_connector.Credentials")
    def test_init_requires_credentials_file(self, mock_creds, mock_gspread):
        """Test that init validates credentials file."""
        from agent.connectors.google_sheets_connector import GoogleSheetsConnector

        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_spreadsheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet

        connector = GoogleSheetsConnector("credentials.json", "sheet-id")
        self.assertEqual(connector.spreadsheet_id, "sheet-id")

    @patch("agent.connectors.google_sheets_connector.HAS_GOOGLE_SHEETS", True)
    @patch("agent.connectors.google_sheets_connector.gspread")
    @patch("agent.connectors.google_sheets_connector.Credentials")
    def test_read_profiles(self, mock_creds, mock_gspread):
        """Test reading profiles from a worksheet."""
        from agent.connectors.google_sheets_connector import GoogleSheetsConnector

        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_spreadsheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet

        mock_worksheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_records.return_value = [
            {
                "company_name": "Acme Corp",
                "profile_text": "SaaS B2B $1M ARR",
                "market_notes": "Enterprise market",
            }
        ]

        connector = GoogleSheetsConnector("credentials.json", "sheet-id")
        profiles = connector.read_profiles("Profiles")
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["company_name"], "Acme Corp")

    @patch("agent.connectors.google_sheets_connector.HAS_GOOGLE_SHEETS", True)
    @patch("agent.connectors.google_sheets_connector.gspread")
    @patch("agent.connectors.google_sheets_connector.Credentials")
    def test_write_results(self, mock_creds, mock_gspread):
        """Test writing results to a worksheet."""
        from agent.connectors.google_sheets_connector import GoogleSheetsConnector

        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_spreadsheet = Mock()
        mock_client.open_by_key.return_value = mock_spreadsheet

        mock_worksheet = Mock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        connector = GoogleSheetsConnector("credentials.json", "sheet-id")
        results = [
            {
                "company_name": "Acme Corp",
                "prioritized": [
                    {"title": "Growth Strategy", "rationale": "High impact"}
                ],
            }
        ]

        row_count = connector.write_results(results, "Results")
        self.assertEqual(row_count, 1)
        mock_worksheet.append_rows.assert_called_once()


if __name__ == "__main__":
    unittest.main()
