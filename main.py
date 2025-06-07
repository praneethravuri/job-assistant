from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
    show_tool_calls=True,
    tools = [Crawl4aiTools(max_length=None)],
    
)

detailed_request = """
Link: https://job-boards.greenhouse.io/ninjatrader/jobs/4535655006?gh_src=509adb6f3us&__jvsd=LinkedIn

STEP1:
Parse the url and extract the job description.

STEP2:
Extract the company name, job title, location, keywords, repeated phrases, and any other relevant information from the job description that will be useful in tailoring a resume.
"""

agent.print_response(detailed_request)