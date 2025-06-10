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

        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

        self.llm = ChatDeepSeek(
            base_url='https://api.deepseek.com/v1',
            model='deepseek-chat',
            api_key=SecretStr(api_key)
        )

        self.browser_session = BrowserSession(
            cdp_url="http://localhost:9222",
            keep_alive=True,
            headless=False,
            wait_for_network_idle_page_load_time=3.0,
            minimum_wait_page_load_time=1.0,
            maximum_wait_page_load_time=10.0,
            wait_between_actions=2.0,
            highlight_elements=True
        )

    async def start_browser_session(self):
        await self.browser_session.start()

    async def close_browser_session(self):
        await self.browser_session.close()

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
        
    async def go_to_url(self, url:str):

        agent = Agent(
            task=f"Go to the {url}",
            llm = self.llm,
            browser_session = self.browser_session
        )

        result = await agent.run(max_steps=30)
