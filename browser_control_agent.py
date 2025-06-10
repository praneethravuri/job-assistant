import asyncio
from langchain_deepseek import ChatDeepSeek
from browser_use import Agent, BrowserSession, Controller, ActionResult
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# Custom controller for tab management
controller = Controller()

@controller.action('Switch to the newest opened tab')
async def switch_to_newest_tab(browser_session) -> ActionResult:
    """Switch to the most recently opened tab"""
    try:
        pages = browser_session.browser_context.pages
        if len(pages) > 1:
            newest_page = pages[-1]
            await newest_page.bring_to_front()
            return ActionResult(extracted_content=f"Switched to newest tab: {newest_page.url}")
        return ActionResult(extracted_content="No new tab to switch to")
    except Exception as e:
        return ActionResult(extracted_content=f"Error switching tabs: {str(e)}")

@controller.action('Close current tab and switch to main tab')
async def close_current_and_switch_to_main(browser_session) -> ActionResult:
    """Close the current tab and switch back to the main (first) tab"""
    try:
        pages = browser_session.browser_context.pages
        current_page = await browser_session.get_current_page()
        
        # Only close if we have more than one tab
        if len(pages) > 1:
            # Close the current tab
            await current_page.close()
            
            # Get updated pages list after closing
            remaining_pages = browser_session.browser_context.pages
            if remaining_pages:
                # Switch to the first tab (main tab)
                main_page = remaining_pages[0]
                await main_page.bring_to_front()
                return ActionResult(extracted_content=f"Closed current tab and switched to main tab: {main_page.url}")
            else:
                return ActionResult(extracted_content="Error: No tabs remaining after closing current tab")
        else:
            return ActionResult(extracted_content="Cannot close the last remaining tab")
    except Exception as e:
        return ActionResult(extracted_content=f"Error closing tab: {str(e)}")

async def main():
    llm = ChatDeepSeek(
        base_url='https://api.deepseek.com/v1',
        model='deepseek-chat', 
        api_key=SecretStr(api_key)
    )

    try:
        browser_session = BrowserSession(
            cdp_url="http://localhost:9222",
            keep_alive=True,
            headless=False,
            wait_for_network_idle_page_load_time=3.0,
            minimum_wait_page_load_time=1.0,
            maximum_wait_page_load_time=10.0,
            wait_between_actions=2.0,
            highlight_elements=True
        )

        agent = Agent(
            enable_memory=False,
            use_vision=False,
            task="""
            1. Go to https://jobright.ai/jobs/recommend
            2. Wait for the recommend page to open completely
            3. Find the first job posting
            4. Click the "Apply Now" button
            5. IMPORTANT: Immediately check if a new tab opened and switch to the newest tab
            6. Wait for the job details/application page to load completely
            7. Extract the following information:
                - Job title (exact text)
                - Job description (complete description)
                - Job ID (if available)
            8. Print the information in this format:
                Job Title: [extracted job title]
                Job ID: [extracted job ID or "Not found"]
                Job Description: [complete job description]
            9. Find and fill out the application form with random details
            10. Submit the application by clicking the submit button
            11. IMPORTANT: After submitting, close the current tab and switch back to the main tab
            12. STOP EXECUTION - Task completed successfully
            """,
            llm=llm,
            browser_session=browser_session,
            controller=controller,
            max_failures=5,
            retry_delay=15
        )

        print("Starting agent execution...")
        result = await agent.run(max_steps=50)
        print("Task completed successfully!")
        print("Final result:", result)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())