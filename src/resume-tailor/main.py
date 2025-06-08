from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from textwrap import dedent
from pathlib import Path
import json
import re
import yaml
from create_resume_docx import generate_docx_from_json

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESUME = PROJECT_ROOT / "data" / "resume.yml"

jd_scraper_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
    show_tool_calls=True,
    tools=[Crawl4aiTools(max_length=None)],
    description=dedent("""\
        You are an expert job description scraper. Your task is to read and scrape job postings from various sources to extract the full text of the job description.
        You will be provided with a URL to a job posting, and you need to extract the full text of the job description from that page.
    """),
    instructions=dedent("""\
        1. Search Strategy:
            - Use the provided URL to scrape the job description.
            - Ensure you extract the full text of the job description, including all relevant sections such as responsibilities, qualifications, and company culture.
        2. Validation:
            - The extracted text should be complete and coherent.
            - Ensure that all sections of the job description are included.
        3. Output:
            - Provide the full text of the job description in a structured format.
    """)
)


jd_analysis_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    show_tool_calls=True,
    tools=[Crawl4aiTools(max_length=None)],
    description=dedent("""\
        You are a job description analyzer. Given a job description text, classify and organize its contents.
    """),
    instructions=dedent("""\
        1. Parse the job description into the following sections:
            - role_information:
                - Company Name
                - Role or Position Title
                - Job ID
                - Location
            - company_information:
                - industry_domain: list of phrases that describe the industry or domain of the company
                - mission_and_growth: list of phrases that describe the company's mission and growth
                - culture_and_values: list of phrases that describe the company's culture and values
            - responsibilities_and_duties:
                - architecture_and_development: list of phrases that describe the architecture and development responsibilities
                - collaboration_and_process: list of phrases that describe the collaboration and process responsibilities
                - support_and_ownership: list of phrases that describe the support and ownership responsibilities
            - core_hard_skills:
                - languages_and_frameworks: list of programming languages and frameworks required for the role (e.g. Java, Spring Boot, React, Golang, Python, FastAPI, etc.)
                - apis_and_protocols: list of APIs and protocols required for the role (e.g. REST, gRPC, GraphQL, Websockets, etc.)
                - databases_and_storage: list of databases and storage technologies required for the role (e.g. PostgreSQL, MySQL, MongoDB, Redis, etc.)
                - cloud_and_infrastructure: list of cloud and infrastructure technologies required for the role (e.g. AWS, Azure, Kubernetes, Docker, etc.)
                - devops_and_testing: list of DevOps and testing tools and practices required for the role (e.g. CI/CD, unit testing, integration testing, etc.)\
                - methodologies_and_practices: list of methodologies and practices required for the role (e.g. Agile, Scrum, TDD, BDD, etc.)
                - additional_skills_and_technologies: list of any additional skills or technologies mentioned in the job description that are relevant to the role
            - soft_skills_and_competencies: list of soft skills and competencies that are required for the role (e.g. cross-functional collaboration, communication, etc.)
            - qualifications_and_experience: list of requirements for the role, such as education, certifications, years of experience, etc.
            - repeated_phrases: list of phrases that are repeated in the job description
            - tone_of_company: the tone of the company (e.g. collaborative, innovative, fast-paced, mission-driven, etc.)
        2. Use exact wordings as they appear in the job description when possible. If a term is misspelled, correct it in the output. If a keyword's full name is not mentioned, write its full name (e.g. "Spring Boot" instead of "Spring").
        3. Output strictly as YAML. Maintain proper indentation and formatting.
    """),
)

resume_tailor_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
    show_tool_calls=True,
    tools=[],
    description=dedent("""\
        You are an expert resume-tailoring assistant. You will be given:
        
        1. The candidate’s resume in YAML format (loaded from `data/resume.yml`).
        2. A job description analysis in YAML format (from `jd_analysis_agent`).
        
        Your task is to integrate the two and produce a tailored resume as a JSON object with this schema:
        
        {
          "header": {
            "name": <string>,
            "contact": [<string>, …]
          },
          "work_experience": [
            {
              "company": <string>,
              "location": <string>,
              "position": <string>,
              "start_date": <string>,
              "end_date": <string>,
              "bullets": [<string>, …]
            },
            … more roles …
          ],
          "projects": [
            {
              "name": <string>,
              "bullets": [<string>, …]
            },
            … more projects …
          ],
          "skills": [
            {
              "name": <string>,
              "items": [<string>, …]
            },
            … additional categories …
          ],
          "education": [
            {
              "institution": <string>,
              "location": <string>,
              "degree": <string>,
              "start_date": <string>,
              "end_date": <string>
            },
            … more education entries …
          ]
        }
    """),
    instructions=dedent("""\
        ## 1. Integrate All JD Keywords / Technologies / Responsibilities into Bullets and Skills

        1. **Extracted Keywords List**  
           You will receive detailed analysis of the job description. This list may include hard skills, frameworks, methodologies, tools, soft skills, company information, etc.

        2. **Mandatory Inclusion in Bullets First**
           - **Every single item** which can be termed as a keyword in the job description analysis **must appear at least once** in the final resume JSON.
           - **Primary Goal:** Weave each term into an existing or new bullet point under the most relevant work experience role.
             - Use the **exact phrasing** from the job description analysis.
             - Bullets must be past-tense and action-focused (e.g., “Developed …”, “Configured …”).
           - **Secondary Option (Skills Section Only if Necessary):** Only if a term absolutely cannot fit into any bullet, place it under the Skills section—and only after attempting all bullet integrations.

        3. **When to Create a New Bullet**
           - If a keyword does not naturally fit into any existing bullet without awkwardness, **create a new bullet** at the bottom of the most relevant role.
           - New bullets should still quantify impact where possible (e.g., “Designed and implemented Micro-service Development pipelines, reducing deployment complexity by 30%”).

        ## 2. Highlight and Quantify

        1. **Order of Bullets**
           - Prioritize bullets that incorporate JD terms (including any you created).
           - For each role in **work_experience**, list up to **5 bullets**.
           - For each project in **projects**, list up to **4 bullets**.

        2. **Action Verbs & Metrics**
           - Begin every bullet with a strong verb (e.g., “Developed,” “Implemented,” “Optimized”).
           - Quantify results whenever possible (e.g., “reduced deployment time by 60%,” “processed 1 million+ JSON objects per hour”).

        ## 3. Adjusted Job Titles

        - Change the candidate’s job titles to match the **exact target position** when plausible (e.g., “Senior Software Engineer” instead of “Software Engineer”) without altering employer names, dates, or fabricating new positions.

        ## 4. Optimize Skills Section (Only After Bullets)

        1. **Maintain Original Categories**
           - Retain existing skill categories (e.g., “Programming Languages,” “Frameworks & Libraries”).
           - Add every JD keyword to the appropriate category **only after** it appears in a bullet.
        2. **Never Omit**
           - Place each remaining analysis term under Skills in its logical category.
           - If no existing category fits, create a new one named precisely for that domain (e.g., “Authentication Protocols” for “OIDC,” “OAuth,” “SAML”).

        **Output Format**
        - Output **strictly** as JSON, matching the schema in the description.
        - Do not include any extra keys or commentary.
        - Do not put the output in a code block.
        - Ensure proper JSON formatting with correct indentation.
    """)
)


jd_url = "https://job-boards.greenhouse.io/ninjatrader/jobs/4535655006?gh_src=509adb6f3us&__jvsd=LinkedIn"
jd_scrape = jd_scraper_agent.run(f"Here is the link: {jd_url}")

# Step 2: Analyze the scraped JD
analysis = jd_analysis_agent.run(jd_scrape.content)

# Step 3: Load candidate resume
resume_yaml = RESUME.read_text(encoding="utf-8")

# Step 4: Generate tailored resume JSON
tailored = resume_tailor_agent.run(f"Resume YAML:\n{resume_yaml}\n\nJD Analysis YAML:\n{analysis.content}")
json_output = tailored.content

# Step 5: Clean JSON output (remove code fences if any)
match_json = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_output, re.S)
clean_json_str = match_json.group(1) if match_json else json_output.strip()
resume_data = json.loads(clean_json_str)

# Step 6: Clean YAML analysis output
yaml_text = analysis.content
match_yaml = re.search(r'```(?:yaml)?\s*(.*?)\s*```', yaml_text, re.S)
clean_yaml_str = match_yaml.group(1) if match_yaml else yaml_text
analysis_dict = yaml.safe_load(clean_yaml_str)

# Step 7: Extract metadata for filename
role_info = analysis_dict.get('role_information', {})
company = role_info.get('Company Name', 'Resume')
role = role_info.get('Role or Position Title', 'Tailored')
job_id = role_info.get('Job ID', '')

# Build filename
safe = lambda s: re.sub(r'[^A-Za-z0-9]+', '_', s)
base_name = f"{safe(company)}_{safe(role)}"
if job_id and job_id.lower() != 'n/a':
    base_name += f"_{safe(job_id)}"
filename = f"{base_name}.docx"

# Step 8: Generate DOCX
generate_docx_from_json(resume_data, output_path=filename)
print(f"Generated resume document: {filename}")