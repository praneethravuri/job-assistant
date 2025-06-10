import os
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

class GoogleSheetClient:
    def __init__(self,
                 creds_path: Path = None,
                 sheet_id: str = None,
                 scopes: list = None):
        """
        Initialize the Google Sheets client.
        
        :param creds_path: Path to your service account JSON file.
        :param sheet_id:    The Google Sheet ID.
        :param scopes:      OAuth scopes for Google Sheets API.
        """
        load_dotenv()
        
        # Default values
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        if creds_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            creds_path = base_dir / "credentials.json"
        if sheet_id is None:
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            if sheet_id is None:
                raise ValueError("GOOGLE_SHEET_ID must be set in environment")

        # Authenticate and build client
        creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def read_row(self, row: int) -> list:
        """
        Read all the cells in a given row.
        
        :param row: Row number (1-based).
        :return:    List of cell values as strings.
        """
        return self.sheet.row_values(row)

    def get_last_cell(self, row: int) -> str:
        """
        Get the value of the last non-empty cell in a given row.
        
        :param row: Row number (1-based).
        :return:    Value of the last cell, or None if the row is empty.
        """
        values = self.read_row(row)
        return values[-1] if values else None

    def update_last_cell(self, row: int, new_value: str) -> None:
        """
        Update the last non-empty cell in a given row.
        If the row is empty, this will update cell (row, 1).
        
        :param row:       Row number (1-based).
        :param new_value: The value to write into the last cell.
        """
        values = self.read_row(row)
        if values:
            col = len(values)
        else:
            col = 1
        self.sheet.update_cell(row, col, new_value)
