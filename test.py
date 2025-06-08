from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from pathlib import Path
from agno.utils.pprint import pprint_run_response

load_dotenv()

job_posting_scraper_agent = Agent(
    name="Job Posting Scraper",
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
    description=dedent("""
        You extract job description, role title, company name, and job ID from job postings.
        Format your response with clear sections for each piece of information.
        Do not modify the wording of the job description text; just extract and present it clearly.
        """),
    show_tool_calls=True,
    tools=[Crawl4aiTools(max_length=None)],
    instructions=dedent("""
        When scraping job postings, extract and present the information in this format:

        Note:
            - You need to find the job id from the webpage content and not from the URL.
            - If the job ID is not available, state "Not provided".
            - Neatly format the job title, company name, and job ID.
        
        ## Job Details
        **Role Title:** [extracted title]
        **Company Name:** [extracted company]
        **Job ID:** [extracted ID if available]
        
        ## Job Description
        [detailed description of responsibilities and requirements]
        """)
)

jd_analyzer_agent = Agent(
    name="Job Description Analyzer",
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
    description=dedent("""
        You are an expert resume analyzer with decades of experience in the HR industry.
        Your job is to identify skills in a job description and present them in markdown format.
    """),
    instructions=dedent("""
        You need to create a skills-taxonomy framework using the provided job description.
        Identify the core objectives and the skills critical to performing the roles and responsibilities outlined in that description.
        Create a comprehensive list of required skills, including both hard skills (e.g., programming languages, frameworks, software methodologies, practices, tools, testing, etc.) and soft skills (e.g., communication, leadership).
        Organize these skills into broader categories and subcategories. For example:

        - **Technical skills**: [data analytics, cloud computing, programming languages]
        - **Interpersonal skills**: [communication, negotiation, conflict resolution, cross-functional collaboration]
        - **Leadership skills**: [strategic thinking, team management, decision-making]

        Ensure your categories are exhaustive yet easy to navigate, without over-complicating the framework.
        Return only the list in markdown format and no other explanatory text.
    """),
    expected_output=dedent("""
        - **Technical skills**: [Python, CI/CD, SDLC, TDD, JUnit, Django]
        - **Interpersonal skills**: [problem-solving, cross-functional collaboration]
        - **Leadership skills**: [stakeholder management, performance feedback, delegation]
    """)
)

job_post_link = "https://jobs.ashbyhq.com/ramp/dbec16c5-4fa8-4e3e-84b2-e57ae8b4918a?src=LinkedIn"

# Step 1: Scrape the job posting
print("=== SCRAPING JOB POSTING ===")
scraper_response: RunResponse = job_posting_scraper_agent.run(f"Please scrape this job posting and extract the key information: {job_post_link}")

pprint_run_response(scraper_response, markdown=True)

# Step 2: Take the scraped content and analyze it for skills
if scraper_response.content:
    print("\n=== ANALYZING SKILLS ===")
    analyzer_response: RunResponse = jd_analyzer_agent.run(scraper_response.content)
    
    pprint_run_response(analyzer_response, markdown=True)
else:
    print("No content received from job posting scraper")