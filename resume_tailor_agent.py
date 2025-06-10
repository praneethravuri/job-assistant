from textwrap import dedent
from agno.agent import Agent
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from pathlib import Path
from agno.tools.reasoning import ReasoningTools
from agno.workflow import Workflow
from pathlib import Path
import json
import yaml
from agno.models.openai import OpenAIChat
from agno.models.openai import OpenAIChat
from tools.resume_tailor_tools import generate_docx_from_json


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATA_PATH = PROJECT_ROOT / "data"
RESUME_PATH = DATA_PATH / "resume.yml"
out_dir = PROJECT_ROOT / "out"
out_dir.mkdir(exist_ok=True)


class ResumeTailoringWorkflow(Workflow):

    job_post_scraping_agent: Agent = Agent(
        name="Job Posting Scraper",
        model=OpenAIChat(id="gpt-4o"),
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
        model=OpenAIChat(id="gpt-4o"),
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
        Return a JSON object containing the company name, role, job id (if available), and skills. Remove '```' and '```json' in the output. The output should look something like this:
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
        model=OpenAIChat(id="gpt-4o", temperature=0.1),
        tools=[ReasoningTools(add_instructions=True)],
        description=dedent("""
        You are a resume-tailoring specialist with decades of experience crafting ATS-compliant resumes.
        Your job is to identify, change, or add content to a candidate's resume based on the provided skills list.
        You must incorporate all the skills mentioned in that list into the candidate's resume.

    """),
        instructions=dedent("""
        - You will be given a JSON object containing the job description analysis (jd_analysis) and the candidate's resume.
        - Go through the candidate's resume and identify which bullet points can accommodate the skills present in jd_analysis.
        - There can only be five bullets per work experience and four bullets per project. You cannot be lower or higher than the required number.
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

    yaml_to_json_converter_agent: Agent = Agent(
        name="YAML To JSON Converter",
        model=OpenAIChat(id="gpt-4o"),
        tools=[ReasoningTools(add_instructions=True)],
        description=dedent("""
        You are the best data serialization format converter.
        Your job is to convert a resume in YAML format into a JSON object matching the following schema:
        {
          "header": {
            "name": <string>,
            "contact": [<string>, ...]
          },
          "work_experience": [
            {
              "company": <string>,
              "location": <string>,
              "position": <string>,
              "start_date": <string>,
              "end_date": <string>,
              "bullets": [<string>, ...]
            }, ...
          ],
          "projects": [
            {
              "name": <string>,
              "bullets": [<string>, ...]
            }, ...
          ],
          "skills": [
            {
              "name": <string>,
              "items": [<string>, ...]
            }, ...
          ],
          "education": [
            {
              "institution": <string>,
              "location": <string>,
              "degree": <string>,
              "start_date": <string>,
              "end_date": <string>
            }, ...
          ]
        }
    """),
        instructions=dedent("""
        YYou will be given a resume in YAML format.
        Convert it into JSON that exactly matches the schema above.
        - Do not wrap the output in code fences.
        - Ensure valid JSON formatting and proper nesting.
        - Only output the json resume-no explanatory text.
    """),
        expected_output=dedent("""
  {
          "header": {
            "name": "John Doe",
            "contact": ["Anytown, CA", "+1 555 123 4567", "johndoe@example.com"]
          },
          "work_experience": [
            {
              "company": "Acme Corp",
              "location": "San Francisco, CA",
              "position": "Senior Software Engineer",
              "start_date": "June 2021",
              "end_date": "August 2023",
              "bullets": ["Developed ...", "Implemented ..."]
            }
          ],
          "projects": [
            {
              "name": "Example Project",
              "bullets": ["Created ...", "Optimized ..."]
            }
          ],
          "skills": [
            {
              "name": "Programming Languages",
              "items": ["Python", "JavaScript"]
            }
          ],
          "education": [
            {
              "institution": "University of Example",
              "location": "Example City, EX",
              "degree": "B.S. in Computer Science",
              "start_date": "August 2015",
              "end_date": "May 2019"
            }
          ]
        }
""")

    )

    def run(self, link: str) -> str:

        outputs = []

        # 1) Scrape JD
        scraping = self.job_post_scraping_agent.run(
            f"Here is the job post link: {link}")
        scraping_text = scraping.content.strip()
        outputs.append("## JOB POST SCRAPING")
        outputs.append(f"```{scraping_text}```")

        print(f"Scraping text: {scraping_text}")

        # 2) Analyze JD
        analysis_resp = self.jd_analyzer_agent.run(scraping_text)
        analysis_text = analysis_resp.content.replace(
            '```json', '').replace('```', '').strip()
        outputs.append("## JOB DESCRIPTION ANALYSIS")
        outputs.append(f"```{analysis_text}```")
        analysis_json = json.loads(analysis_text)

        print(f"Analysis response: {analysis_text}")

        # Store metadata
        company = analysis_json.get("company_name")
        role = analysis_json.get("role")
        job_id = analysis_json.get("job_id")

        # 3) Tailor resume to YAML
        raw_yaml = RESUME_PATH.read_text(encoding='utf-8')
        combined = {"jd_analysis": analysis_json,
                    "resume": yaml.safe_load(raw_yaml)}
        tailor_resp = self.resume_tailor_agent.run(json.dumps(combined))
        tailored_yaml = tailor_resp.content.strip()
        outputs.append("## TAILORED RESUME (YAML)")
        outputs.append(f"```{tailored_yaml}```")

        print(f"Tailored yaml: {tailored_yaml}")

        # 4) Convert YAML → JSON
        converter_resp = self.yaml_to_json_converter_agent.run(
            f"Here is the tailored resume in YAML format:\n{tailored_yaml}")
        json_resume = converter_resp.content.replace(
            '```json', '').replace('```', '').strip()
        outputs.append("## JSON RESUME")
        outputs.append(f"```{json_resume}```")

        print(f"Json resume: {json_resume}")

        resume_data = json.loads(json_resume)

        file_name = out_dir / "test.docx"
        generate_docx_from_json(resume_data, str(file_name))

        # 5) Company details
        outputs.append("## COMPANY DETAILS")
        outputs.append(
            f"- **Company:** {company}\n- **Role:** {role}\n- **Job ID:** {job_id}")

        # Write to markdown file
        md_path = PROJECT_ROOT / "outputs.md"
        with open(md_path, 'w', encoding='utf-8') as md:
            md.write("\n\n".join(outputs))

        print(f"All outputs written to {md_path}")
        return json_resume


job_post_link = "https://generalmotors.wd5.myworkdayjobs.com/careers_gm/job/Remote---New-York/Software-Engineer--AI-Solutions_JR-202509886"

if __name__ == "__main__":
    workflow = ResumeTailoringWorkflow()
    workflow.run(link=job_post_link)
