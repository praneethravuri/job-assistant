import asyncio
from langchain_deepseek import ChatDeepSeek
from browser_use import Agent, BrowserSession, Controller, ActionResult
from pydantic import SecretStr, BaseModel
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# Base controller for shared functionality
base_controller = Controller()

@base_controller.action('Switch to the newest opened tab')
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

# Specialized Controllers for different website types
class JobSiteController(Controller):
    def __init__(self):
        super().__init__()
        # Inherit base actions
        self.registry.update(base_controller.registry)
        
    @Controller.action('Extract job information from JobRight')
    async def extract_jobright_info(self, browser_session) -> ActionResult:
        """Extract job information specifically from JobRight.ai"""
        try:
            page = await browser_session.get_current_page()
            # JobRight-specific extraction logic
            job_title = await page.locator('[data-testid="job-title"]').text_content()
            job_description = await page.locator('[data-testid="job-description"]').text_content()
            job_id = await page.locator('[data-testid="job-id"]').text_content()
            
            return ActionResult(
                extracted_content=f"Job Title: {job_title}\nJob ID: {job_id}\nJob Description: {job_description}",
                include_in_memory=True
            )
        except Exception as e:
            return ActionResult(extracted_content=f"Error extracting job info: {str(e)}")

    @Controller.action('Apply to job on JobRight')
    async def apply_jobright_job(self, application_data: dict, browser_session) -> ActionResult:
        """Apply to a job on JobRight with provided data"""
        try:
            page = await browser_session.get_current_page()
            # JobRight-specific application logic
            await page.fill('[name="name"]', application_data.get('name', 'John Doe'))
            await page.fill('[name="email"]', application_data.get('email', 'john@example.com'))
            await page.click('[data-testid="submit-application"]')
            
            return ActionResult(extracted_content="Application submitted successfully")
        except Exception as e:
            return ActionResult(extracted_content=f"Error applying to job: {str(e)}")

class LinkedInController(Controller):
    def __init__(self):
        super().__init__()
        self.registry.update(base_controller.registry)
        
    @Controller.action('Extract job information from LinkedIn')
    async def extract_linkedin_info(self, browser_session) -> ActionResult:
        """Extract job information specifically from LinkedIn"""
        try:
            page = await browser_session.get_current_page()
            # LinkedIn-specific extraction logic
            job_title = await page.locator('.job-title').text_content()
            company = await page.locator('.company-name').text_content()
            description = await page.locator('.job-description').text_content()
            
            return ActionResult(
                extracted_content=f"Job Title: {job_title}\nCompany: {company}\nDescription: {description}",
                include_in_memory=True
            )
        except Exception as e:
            return ActionResult(extracted_content=f"Error extracting LinkedIn job info: {str(e)}")

class IndeedController(Controller):
    def __init__(self):
        super().__init__()
        self.registry.update(base_controller.registry)
        
    @Controller.action('Extract job information from Indeed')
    async def extract_indeed_info(self, browser_session) -> ActionResult:
        """Extract job information specifically from Indeed"""
        # Indeed-specific logic here
        pass

# Specialized Agent Classes
class SpecializedAgent:
    def __init__(self, name: str, controller: Controller, llm, browser_session: BrowserSession):
        self.name = name
        self.controller = controller
        self.llm = llm
        self.browser_session = browser_session
        
    async def execute_task(self, task: str, max_steps: int = 20) -> str:
        """Execute a specialized task"""
        agent = Agent(
            task=task,
            llm=self.llm,
            browser_session=self.browser_session,
            controller=self.controller,
            max_failures=3,
            retry_delay=10
        )
        
        result = await agent.run(max_steps=max_steps)
        return result.final_result() if result.final_result() else "Task completed"

class JobApplicationTeam:
    def __init__(self, llm, browser_session: BrowserSession):
        self.llm = llm
        self.browser_session = browser_session
        
        # Create specialized agents
        self.agents = {
            'jobright': SpecializedAgent('JobRight Agent', JobSiteController(), llm, browser_session),
            'linkedin': SpecializedAgent('LinkedIn Agent', LinkedInController(), llm, browser_session),
            'indeed': SpecializedAgent('Indeed Agent', IndeedController(), llm, browser_session),
        }
        
        # Main coordinator agent
        self.coordinator = self._create_coordinator()
    
    def _create_coordinator(self):
        """Create the main coordinator agent with delegation capabilities"""
        coordinator_controller = Controller()
        
        @coordinator_controller.action('Delegate task to specialized agent')
        async def delegate_task(self, website_type: str, task: str, browser_session) -> ActionResult:
            """Delegate a task to a specialized agent based on website type"""
            try:
                if website_type.lower() in self.agents:
                    agent = self.agents[website_type.lower()]
                    result = await agent.execute_task(task)
                    return ActionResult(extracted_content=f"Delegated to {agent.name}: {result}")
                else:
                    return ActionResult(extracted_content=f"No specialized agent found for {website_type}")
            except Exception as e:
                return ActionResult(extracted_content=f"Delegation error: {str(e)}")
        
        return Agent(
            task="Coordinate job application tasks across different websites",
            llm=self.llm,
            browser_session=self.browser_session,
            controller=coordinator_controller,
            max_failures=5,
            retry_delay=15
        )
    
    async def execute_job_search_and_apply(self, target_websites: List[str]) -> Dict[str, str]:
        """Execute job search and application across multiple websites"""
        results = {}
        
        for website in target_websites:
            try:
                if website.lower() == 'jobright':
                    task = """
                    1. Go to https://jobright.ai/jobs/recommend
                    2. Find the first suitable job posting
                    3. Extract job information (title, description, ID)
                    4. Apply to the job with sample data
                    """
                    result = await self.agents['jobright'].execute_task(task)
                    results[website] = result
                    
                elif website.lower() == 'linkedin':
                    task = """
                    1. Go to LinkedIn jobs page
                    2. Search for relevant positions
                    3. Extract job information from the first result
                    4. Apply if possible
                    """
                    result = await self.agents['linkedin'].execute_task(task)
                    results[website] = result
                    
                # Add more website-specific logic as needed
                
            except Exception as e:
                results[website] = f"Error: {str(e)}"
        
        return results

# Updated main function
async def main():
    llm = ChatDeepSeek(
        base_url='https://api.deepseek.com/v1',
        model='deepseek-chat', 
        api_key=SecretStr(api_key)
    )

    try:
        # Create shared browser session
        browser_session = BrowserSession(
            cdp_url="http://localhost:9222",
            keep_alive=True,  # Keep browser alive for multiple agents
            headless=False,
            wait_for_network_idle_page_load_time=3.0,
            minimum_wait_page_load_time=1.0,
            maximum_wait_page_load_time=10.0,
            wait_between_actions=2.0,
            highlight_elements=True
        )

        # Create the job application team
        job_team = JobApplicationTeam(llm, browser_session)
        
        # Execute job search and application across multiple sites
        target_websites = ['jobright', 'linkedin']  # Add more as needed
        results = await job_team.execute_job_search_and_apply(target_websites)
        
        print("Job Application Results:")
        for website, result in results.items():
            print(f"\n{website.upper()}:")
            print(result)
            print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())