# job-assistant

job-assistant is a toolkit for automating job applications and tailoring resumes using AI-powered agents.

## Overview

This repository contains two main components:

1. **jobs-applier**: Automates filling out web-based job application forms using a browser agent and your personal data.
2. **resume-tailor**: Scrapes and analyzes job descriptions, tailors a YAML-based resume to match the JD, and generates a formatted `.docx` file.

---

## Repository Structure

```
.gitignore
README.md            ← This file
requirements.txt     ← Python dependencies

data/                ← Directory for YAML data files
  ├─ personal_info.yml     ← Candidate personal data for form filling
  └─ resume.yml            ← Candidate resume data for tailoring
  └─ job_preferences.yml   ← Job preferences and other information

src/
  ├─ jobs-applier/
  │   └─ main.py        ← Script to run the application-filling agent
  └─ resume-tailor/
      ├─ main.py        ← Script to run scraping, analysis, tailoring, and docx generation
      └─ create_resume_docx.py  ← Utility to convert JSON resume to .docx
```

---

## Getting Started

### Prerequisites

* **Python 3.8+**
* **pip** (for installing dependencies)

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/job-assistant.git
   cd job-assistant
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Export your api key:

   ```ini
   setx GOOGLE_API_KEY your_google_api_key_here
   ```

---

## Data Folder (`data/`)

Place your YAML files under the `data/` directory. Below are example files you should create.

### 1. `personal_info.yml`

This file supplies personal and contact details used by the jobs-applier agent to fill forms.

```yaml
# data/personal_info.yml
first_name: John
last_name: Doe
phone_number: "+1 555 123 4567"
email: "johndoe@example.com"
address:
  street: "123 Main St"
  city: "Anytown"
  state: "CA"
  zip: "90210"
  country: "USA"
date_of_birth: "1985-01-15"
websites:
  personal_website: "https://johndoe.dev"
  portfolio: "https://github.com/johndoe"
  linkedin: "https://www.linkedin.com/in/johndoe"
passwords:
  first_preference: "Password123!"
  second_preference: "JDoe$ecure2025"
veterans_preference:
  disabled_veteran: false

```

### 2. `resume.yml`

This file defines your existing resume in a structured format. The tailoring agent will read this and output a matched JSON before converting to `.docx`.

```yaml
# data/resume.yml
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

```

### 3. `job_preferences.yml`

This file contains all of your job preferences and other options required to fill job applications

```yaml
# data/resume.yml
work_arrangements:
  remote: true
  hybrid: true
  onsite: true

experience_level:
  internship: false
  entry: true
  associate: true
  mid_senior_level: true
  director: false
  executive: false

job_types:
  full_time: true
  contract: false
  part_time: false
  temporary: false
  internship: false
  volunteer: true
  other: false

positions:
  - Software Engineer
  - Full-Stack Developer

locations:
  - United States

apply_once_at_company: true

sponsorship:
  current_visa: "F1 OPT"
  require_sponsorship: true
  require_future_sponsorship: true
  us_citizen: false
  permanent_resident: false
  lawful_permanent_resident: false
  us_person: false
  refugee: false
  asylum_seeker: false
  granted_asylum: false

mobility:
  willing_to_relocate: true
  relocation_assistance: true
  willing_to_commute: true
  max_commute_distance_miles: 100

how_did_you_hear_about_us:
  job_board: true
  company_website: false
  referral: false
  social_media: false
  networking_event: false
  career_fair: false
  linkedin: true
  careers_page: true
  other: false

company_blacklist: []
title_blacklist: []

restrictive_agreements:
  non_compete: false
  non_solicit: false
  confidentiality: false
  intellectual_property: false

worked_at_auditing_firms:
  prefer_not_to_say: true
  worked_at_deloitte: false
  worked_at_ernst_and_young: false
  worked_at_kpmg: false
  worked_at_pricewaterhousecoopers: false

government_employment:
  prefer_not_to_say: true
  government_employee: false
  government_contractor: false
  former_government_employee: false
  barred_from_receiving_government_contracts: false

relations_or_related_to_employees: false

previously_worked_at_company: false

romantic_relationships_in_company:
  prefer_not_to_say: true
  romatic_partners_in_company: false

consent:
  agree_to_terms_of_service: true
  agree_to_privacy_policy: true
  agree_to_cookie_policy: true
  agree_to_data_processing: true
  agree_to_data_storage: true
  agree_to_data_sharing: false
  agree_to_receive_updates: false
  agree_to_receive_marketing: false

e_signature: "John Doe"

preferred_locations:
  - Austin, TX
  - San Francisco, CA
  - New York, NY
  - Seattle, WA
  - San Jose, CA
  - Los Angeles, CA
  - Chicago, IL
  - Boston, MA
  - Washington, DC
  - Dallas, TX
  - Miami, FL
  - Atlanta, GA
  - Denver, CO
  - Phoenix, AZ
  - Philadelphia, PA
  - Houston, TX
  - Raleigh, NC
  - Charlotte, NC
  - Nashville, TN
  - Portland, OR

compensation:
  salary_min: 70000
  salary_max: 120000
  equity: optional

industries:
  - all

follow_up:
  enabled: true
  cadence_days: 7
  max_attempts: 3

communications:
  email: true
  sms: false
  linkedin_message: true

portfolio:
  website: "https://praneethravuri.com"
  github: "https://github.com/praneethravuri"
  linkedin: "https://linkedin.com/in/prav10"

interview:
  onsite: true
  virtual: true
  coding_challenge: true
```

---

## Usage

### 1. Automate Job Applications

```bash
python src/jobs-applier/main.py
```

* The script loads `data/personal_info.yml`, flattens the fields, and injects them into the browser automation task.
* Modify the Greenhouse URL and form instructions directly in `src/jobs-applier/main.py` under the `task` string.

### 2. Tailor Resume and Generate DOCX

```bash
python src/resume-tailor/main.py
```

This pipeline will:

1. Scrape the job description from the URL configured in `src/resume-tailor/main.py`.
2. Analyze and extract structured JD information.
3. Load your resume from `data/resume.yml`.
4. Produce a tailored JSON resume.
5. Convert the JSON into a `.docx` file named `<Company>_<Role>_<JobID>.docx` in the project root.

---