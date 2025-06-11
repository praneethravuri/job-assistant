import asyncio
import time
from src.tools.google_sheet import GoogleSheetClient
from src.browser_manager import BrowserManager


async def main():
    sheet_client = GoogleSheetClient()
    browser_manager = BrowserManager()

    # Initialize the browser session
    await browser_manager.start_browser_session()

    sheet = sheet_client.sheet
    row = 2
    print("Starting job application loop...")

    try:
        while True:
            row_values = sheet_client.read_row(row)
            if not row_values:
                row += 1
                if row > sheet_client.sheet.row_count:
                    row = 2
                    time.sleep(60)
                continue

            if sheet_client.check_application_status(row):
                print(f"You have already applied for job in row: {row}")
                row += 1
                continue

            url = sheet_client.get_url(row)
            print(f"Row {row}: Processing URL: {url}")

            # Get job description by scraping the page
            job_description = await browser_manager.scrape_job_description(url)
            
            if job_description:
                print(f"Successfully scraped job description from {url}")
                # You can now use the job_description for further processing
                # For example, pass it to your resume tailor agent
                
                # After processing (successful or attempted):
                sheet_client.update_status(row, "applied")

                return
            else:
                print(f"Failed to scrape job description from {url}")
                sheet_client.update_status(row, "failed")
            
            row += 1

    finally:
        # Clean up browser session
        await browser_manager.close_browser_session()


if __name__ == "__main__":
    asyncio.run(main())