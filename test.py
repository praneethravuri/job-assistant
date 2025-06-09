from textwrap import dedent
from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from pathlib import Path
from agno.utils.pprint import pprint_run_response
from agno.tools.reasoning import ReasoningTools
from agno.workflow import Workflow
from typing import Iterator
from pathlib import Path
import json

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATA_PATH = PROJECT_ROOT/ "data"
RESUME_PATH = DATA_PATH / "resume.yml"

class ResumeTailoringWorkflow(Workflow):

    job_post_scraping_agent: Agent = Agent(
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

    jd_analyzer_agent: Agent = Agent(
        name="Job Description Analyzer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        description=dedent("""
        You are an expert resume analyzer with decades of experience in the HR industry.
        Your job is to identify skills in a job description and present them in markdown format.
    """),
        instructions=dedent("""
        You need to create a skills-taxonomy framework using the provided markdown job description.
        Identify the core objectives and the skills critical to performing the roles and responsibilities outlined in that description.
        Create a comprehensive list of required skills, including both hard skills (e.g., programming languages, frameworks, software methodologies, practices, tools, testing, etc.) and soft skills (e.g., communication, leadership).
        Organize these skills into broader categories and subcategories. For example:

        - **Technical skills**: [data analytics, cloud computing, programming languages]
        - **Interpersonal skills**: [communication, negotiation, conflict resolution, cross-functional collaboration]
        - **Leadership skills**: [strategic thinking, team management, decision-making]

        Ensure your categories are exhaustive yet easy to navigate, without over-complicating the framework.
        Do not wrap the output in codeblocks
        Return a JSON object containing the company name, role, job id (if available), and skills. The output should look something like this:
        {
            "company_name": "...",
            "role": "...",
            "job_id": "...",
            "skills": {
                "technical_skills": [...],
                "interpersonal_skills": [...],
                "leadership_skills": [...],
                // any other categories as needed
            }
        }
    """),
        expected_output=dedent("""
        {
            "company_name": "Acme Corp",
            "role": "Software Engineer",
            "job_id": "123",
            "skills": {
                "technical_skills": ["Python", "CI/CD", "Django"],
                "interpersonal_skills": ["problem-solving", "cross-functional collaboration"],
                "leadership_skills": ["stakeholder management", "delegation"]
            }
        }
    """)
    )

    resume_tailor_agent: Agent = Agent(
        name="Resume Tailor",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[ReasoningTools(add_instructions=True)],
        description=dedent("""
        You are a resume-tailoring specialist with decades of experience crafting ATS-compliant resumes. 
        Your job is to identify, change, or add content to a candidate's resume based on the provided skills list. 
        You must incorporate all the skills mentioned in that list into the candidate's resume.

    """),
        instructions=dedent("""
        - You will be given a JSON object containing the job description analysis (jd_analysis) and the candidate's resume.
        - Go through the candidate's resume and identify which bullet points can accommodate the skills present in jd_analysis.
        - Limit yourself to five bullet points per work experience and four bullet points per project.
        - Identify which skills from the jd_analysis JSON you can map to each bullet point in the candidate's resume.
        - Try to incorporate those skills into existing bullet points, even if it means replacing a less relevant skill.
        - If you cannot incorporate a specific skill into any existing bullet point, create a new one—keeping the context of the relevant work experience or project in mind.
        - If you add a new bullet point, remove a less relevant one to maintain the maximum number of bullet points per section.
        - All technical skills successfully incorporated into bullet points must also be listed in their respective category in the Skills section.
        - Change the role title of the candidate's most recent work experience to match the role title in the job description.
        - Remove filler words, buzzwords, and jargon.
        - Ensure every bullet point includes a quantifying metric. Metrics should be specific and measurable—not vague terms like “reduced manual efforts by X%” or “streamlined workflow by Y%.”
        - Return the tailored resume in YAML format. Only output the resume—no explanatory text.
    """),
        expected_output=dedent("""
        header:
        name: "John Doe"
        contact:
            - "+1 555 123 4567"
            - "johndoe@example.com"
            - "https://johndoe.dev"

        work_experience:
        - company: "Acme Corp"
            location: "San Francisco, CA"
            position: "Software Engineer"
            start_date: "2021-06"
            end_date: "2023-08"
            bullets:
            - "Developed web applications using Python and React, improving user engagement by 20%."
            - "Implemented RESTful APIs and integrated them with third-party services."
        - company: "Beta Solutions"
            location: "Austin, TX"
            position: "Backend Developer"
            start_date: "2019-01"
            end_date: "2021-05"
            bullets:
            - "Designed microservices with Node.js and Docker, reducing deployment times by 30%."
            - "Collaborated with cross-functional teams to define API contracts and data models."

        education:
        - institution: "University of Example"
            location: "Example City, EX"
            degree: "B.S. in Computer Science"
            start_date: "2015-08"
            end_date: "2019-05"

        skills:
        - name: "Programming Languages"
            items:
            - "Python"
            - "JavaScript"
            - "Go"
        - name: "Frameworks & Libraries"
            items:
            - "React"
            - "Express"
            - "FastAPI"

        projects:
        - name: "Example Project One"
            bullets:
            - "Created a data-visualization dashboard using D3.js."
            - "Optimized database queries, reducing response time by 50%."
        - name: "Example Project Two"
            bullets:
            - "Developed a mobile app prototype with React Native."
            - "Integrated push notifications and authentication with OAuth."
    """)
    )

    def run(self, link: str) -> str:
        
        scraping_response = self.job_post_scraping_agent.run(f"Here is the job post link: {job_post_link}")
        print("=== JOB POST SCRAPING ===")
        print(scraping_response.content)
        print("="*15)

        analysis_response = self.jd_analyzer_agent.run(scraping_response.content)
        print("=== JOB DESCRIPTION ANALYSIS ===")
        analysis_response = analysis_response.content.replace('```json', '').replace('```', '')
        print(analysis_response)
        print("="*15)

        analysis_json = json.loads(analysis_response)

        resume_path = RESUME_PATH
        resume_text = resume_path.read_text(encoding='utf-8')

        combined_output = {
            "jd_analysis" : analysis_json,
            "resume" : resume_text
        }

        tailor_response = self.resume_tailor_agent.run(json.dumps(combined_output))

        print("=== TAILORED RESUME ===")
        print(tailor_response.content)

        return tailor_response.content




job_post_link = "https://jobs.ashbyhq.com/ramp/dbec16c5-4fa8-4e3e-84b2-e57ae8b4918a?src=LinkedIn"

if __name__ == "__main__":
    workflow = ResumeTailoringWorkflow()
    workflow.run(link=job_post_link)