from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.crawl4ai import Crawl4aiTools
from dotenv import load_dotenv
from textwrap import dedent

load_dotenv()

jd_scraper_agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    markdown=True,
    show_tool_calls=True,
    tools = [Crawl4aiTools(max_length=None)],
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




jd = jd_scraper_agent.run("Here is the link to the job description: https://job-boards.greenhouse.io/ninjatrader/jobs/4535655006?gh_src=509adb6f3us&__jvsd=LinkedIn")

print(jd.content)

analysis = jd_analysis_agent.run(jd.content)
print(analysis.content)