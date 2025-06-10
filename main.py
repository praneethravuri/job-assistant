import time
from src.tools.google_sheet_tools import GoogleSheetClient
from src.browser_manager import BrowserManager

# Initialize the google sheets client
# Initialize browser_use team leader agent
# Initialize resume tailoring team

"""
STEPS:

1. Initialize the google sheets client, browser_use team leader agent, and resume tailoring team
2. Fetch one row at a time from the google sheet
3. If the last row of the cell is filled, continue to the next row
4. If the last row of the cell is not filled
    - Take the url from the 3rd cell
    - Identify which job board it is
    - Send the url to that job board and then tell it to apply for the job
"""


def main():

    sheet_client = GoogleSheetClient()
    # browser_manager = BrowserManager()

    # shared_browser_session = browser_manager.start_browser_session()
    sheet = sheet_client.sheet
    row = 2
    print("Starting job application loop...")

    while True:
        # Read the entire row
        row_values = sheet_client.read_row(row)
        if not row_values:
            # No data in this row: move to next and continue
            row += 1
            # If you've scanned all populated rows, sleep to wait for new entries
            if row > sheet.row_count:
                print("Reached end of sheet, sleeping before retry...")
                row = 2
                time.sleep(60)
            continue

        # Check if the 5th cell (column E) is filled (status column)
        status = row_values[4] if len(row_values) >= 5 else ""
        if status.strip():
            # Already processed, move to next
            row += 1
            continue

        # Ensure there is a URL in the 3rd cell (column C)
        if len(row_values) < 3 or not row_values[2].strip():
            print(f"Row {row}: No URL found in column C, skipping.")
            row += 1
            continue

        url = row_values[2].strip()
        print(f"Row {row}: Processing URL: {url}")

    # browser_manager.close_browser_session()

if __name__ == "__main__":
    main()
