import os
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

COMPANY_NAME = 0
ROLE = 1
JOB_ID = 2
URL = 3
STATUS = 4
ROW_LEN = 5


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
            base_dir = Path(__file__).resolve().parent.parent.parent
            creds_path = base_dir / "credentials.json"
        if sheet_id is None:
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            if sheet_id is None:
                raise ValueError("GOOGLE_SHEET_ID must be set in environment")

        # Authenticate and build client
        creds = Credentials.from_service_account_file(
            str(creds_path), scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def read_row(self, row: int) -> list:
        """
        Read all the cells in a given row.

        :param row: Row number (1-based).
        :return:    List of cell values as strings.
        """
        current_row = self.sheet.row_values(row)
        return current_row


    def update_status(self, row: int, new_value: str) -> None:
        self.sheet.update_cell(row, STATUS, new_value)

    def get_url(self, row: int) -> str:

        url = self.read_row(row)[URL]
        return url
    
    def check_application_status(self, row:int) -> False:

        current_row = self.read_row(row)
        if len(current_row) < ROW_LEN:
            return False
        
        return True


if __name__ == "__main__":
    client = GoogleSheetClient()
    for i in range(1, 11):
        print(f"Row: {i}")
        print(f"Row values: {client.read_row(i)}")
    print(f"Sheet title: {client.sheet.title}")
    print(f"Total rows: {client.sheet.row_count}")
    print(f"Row 1 data: {client.read_row(2)}")
    print(f"URL: {client.get_url(2)}")
