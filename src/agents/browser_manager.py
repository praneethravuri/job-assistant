import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr
from browser_use import Agent, BrowserSession, Controller, ActionResult
from langchain_deepseek import ChatDeepSeek
from typing import Optional


class BrowserManager:

    def __init__(self):
        load_dotenv()

        # Get API key from environment
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY must be set in environment variables")

        self.llm = ChatDeepSeek(
            base_url='https://api.deepseek.com/v1',
            model='deepseek-chat',
            api_key=SecretStr(api_key)
        )

        self.browser_session = BrowserSession(
            cdp_url="http://localhost:9222",
            keep_alive=True,
            headless=True,
            wait_for_network_idle_page_load_time=0.2,
            minimum_wait_page_load_time=0.5,
            maximum_wait_page_load_time=3.0,
            wait_between_actions=0.5,
            highlight_elements=True,
            devtools=False,
            channel='chrome',
            args=[
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-background-timer-throttling',
                ],
            viewport={'width': 1280, 'height': 720},
            viewport_expansion=200,
            highlight_elements=False,
            include_dynamic_attributes=False,
            default_timeout=5000,
            default_navigation_timeout=10000
        )

    async def start_browser_session(self):
        """Initialize and start the browser session"""
        try:
            await self.browser_session.start()
            print("Browser session started successfully")
        except Exception as e:
            print(f"Failed to start browser session: {e}")
            raise

    async def close_browser_session(self):
        """Close the browser session"""
        try:
            await self.browser_session.close()
            print("Browser session closed successfully")
        except Exception as e:
            print(f"Error closing browser session: {e}")

    def identify_job_board(self, url: str) -> str:
        """
        Identify which job board the URL belongs to.

        Args:
            url: The job posting URL

        Returns:
            Job board identifier
        """
        url_lower = url.lower()

        if 'greenhouse.io' in url_lower:
            return 'greenhouse'
        elif 'lever.co' in url_lower:
            return 'lever'
        elif 'workday' in url_lower:
            return 'workday'
        elif 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'indeed.com' in url_lower:
            return 'indeed'
        elif 'glassdoor.com' in url_lower:
            return 'glassdoor'
        else:
            return 'generic'


    async def scrape_job_description(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Navigate to the URL and scrape the job description with retry logic.

        Args:
            url: The job posting URL to scrape
            max_retries: Maximum number of retry attempts

        Returns:
            The job description text or None if scraping failed
        """
        for attempt in range(max_retries):
            try:
                job_board = self.identify_job_board(url)
                print(
                    f"Attempt {attempt + 1}: Scraping {job_board} job posting from {url}")
                
                initial_actions = [
                    {'open_tab' : {'url': url}}
                ]

                # Create an agent to scrape the job description
                agent = Agent(
                    task=f"""Extract the complete job description. 
                    Please extract:
                    - Job title
                    - Company name
                    - Job requirements
                    - Job responsibilities
                    - Qualifications needed
                    - Any other relevant job details
                    
                    Format the response clearly and include all important information.""",
                    llm=self.llm,
                    browser_session=self.browser_session,
                    use_vision=False,
                    
                )

                # Run the agent to scrape the job description
                result = await agent.run(max_steps=15)

                # Extract the final result
                if result and hasattr(result, 'final_result'):
                    job_description = result.final_result()
                    # Basic validation
                    if job_description and len(job_description.strip()) > 50:
                        return job_description
                elif result:
                    job_description = str(result)
                    if job_description and len(job_description.strip()) > 50:
                        return job_description

                print(
                    f"Attempt {attempt + 1} failed: Insufficient job description content")

            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 5 seconds...")
                    await asyncio.sleep(5)

        print(
            f"Failed to scrape job description from {url} after {max_retries} attempts")
        return None

    async def go_to_url(self, url: str):
        """
        Navigate to a specific URL.

        Args:
            url: The URL to navigate to
        """
        try:
            agent = Agent(
                task=f"Go to {url}",
                llm=self.llm,
                browser_session=self.browser_session
            )

            result = await agent.run(max_steps=5)
            return result

        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            return None
