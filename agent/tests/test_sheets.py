import unittest
from unittest.mock import patch, MagicMock
from agent.connectors.sheets_connector import GoogleSheetsConnector


class TestGoogleSheetsConnector(unittest.TestCase):
    """Unit tests for GoogleSheetsConnector."""

    @patch("agent.connectors.sheets_connector.gspread", None)
    def test_init_requires_gspread_installed(self):
        """Test that GoogleSheetsConnector requires gspread to be installed."""
        with self.assertRaises(RuntimeError):
            GoogleSheetsConnector("sheet-id")

    @patch("agent.connectors.sheets_connector.gspread")
    @patch("agent.connectors.sheets_connector.Credentials")
    def test_init_requires_key_file(self, mock_creds, mock_gspread):
        """Test that GoogleSheetsConnector requires a key file."""
        with self.assertRaises(ValueError):
            GoogleSheetsConnector("sheet-id", key_file_path=None)

    @patch("agent.connectors.sheets_connector.gspread")
    @patch("agent.connectors.sheets_connector.Credentials")
    def test_init_validates_key_file_exists(self, mock_creds, mock_gspread):
        """Test that GoogleSheetsConnector validates key file exists."""
        with self.assertRaises(FileNotFoundError):
            GoogleSheetsConnector("sheet-id", key_file_path="/nonexistent/path.json")

    @patch("agent.connectors.sheets_connector.gspread")
    @patch("agent.connectors.sheets_connector.Credentials")
    def test_read_profiles_parses_rows(self, mock_creds, mock_gspread):
        """Test that read_profiles returns parsed company profiles."""
        # Mock the Google Sheets API
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Company": "Acme", "Profile": "SaaS B2B", "Market Notes": "Growing"},
            {"Company": "Beta", "Profile": "Marketplace", "Market Notes": "Saturated"},
        ]
        
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        mock_gspread.Authorized.return_value.open_by_key.return_value = mock_spreadsheet
        mock_creds.from_service_account_file.return_value = MagicMock()
        
        # Create connector with mocked auth
        with patch("os.path.exists", return_value=True):
            connector = GoogleSheetsConnector("sheet-id", key_file_path="/fake/key.json")
            connector.spreadsheet = mock_spreadsheet
            
            profiles = connector.read_profiles("Companies")
            
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0]["company"], "Acme")
            self.assertEqual(profiles[1]["company"], "Beta")

    @patch("agent.connectors.sheets_connector.gspread")
    @patch("agent.connectors.sheets_connector.Credentials")
    def test_write_results_appends_to_sheet(self, mock_creds, mock_gspread):
        """Test that write_results appends results to sheet."""
        mock_worksheet = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        mock_gspread.Authorized.return_value.open_by_key.return_value = mock_spreadsheet
        mock_creds.from_service_account_file.return_value = MagicMock()
        
        with patch("os.path.exists", return_value=True):
            connector = GoogleSheetsConnector("sheet-id", key_file_path="/fake/key.json")
            connector.spreadsheet = mock_spreadsheet
            
            results = [
                {
                    "company": "Acme",
                    "prioritized": [
                        {
                            "title": "Improve onboarding",
                            "impact": "high",
                            "effort": "medium",
                            "actions": ["Action 1", "Action 2"],
                        }
                    ],
                }
            ]
            
            output = connector.write_results("Results", results)
            
            self.assertEqual(output["status"], "ok")
            self.assertEqual(output["rows_written"], 1)
            # Verify append_row was called
            self.assertTrue(mock_worksheet.append_row.called)


if __name__ == "__main__":
    unittest.main()
