#!/usr/bin/env python3
# main.py
# Install dependencies:
#   pip install browser-use langchain-google-genai pyyaml python-dotenv

import asyncio
import yaml
from pathlib import Path
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA = PROJECT_ROOT / "data"

# -----------------------------
# Helpers
# -----------------------------
def load_data(data_dir: Path) -> dict:
    """
    Load all YAML files from the specified directory into a dictionary.
    Returns a mapping from file stem to parsed YAML content.
    """
    data = {}
    for file_path in data_dir.glob("*.yml"):
        with file_path.open(encoding="utf-8") as f:
            data[file_path.stem] = yaml.safe_load(f)
    return data


def flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    """
    Flatten a nested dict into a single level dict with keys joined by `sep`.
    Lists are joined by commas.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = ", ".join(str(x) for x in v)
        else:
            items[new_key] = v
    return items

# -----------------------------
# Main
# -----------------------------
async def main():
    # Load environment variables (e.g., API keys)
    load_dotenv()

    # Load and flatten candidate data
    raw_data = load_data(DATA)
    flat_data = {}
    for section, content in raw_data.items():
        if isinstance(content, dict):
            flat_data.update(flatten_dict(content, parent_key=section))
        else:
            flat_data[section] = content

    # Build a mapping string for prompt
    mapping_lines = [f"- **{key}**: {value}" for key, value in flat_data.items()]
    mapping_str = "\n".join(mapping_lines)

    # Initialize the LLM for the browser agent
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

    # Construct the agent task prompt with explicit dropdown instructions
    task = f"""
1. Navigate to: https://job-boards.greenhouse.io/ninjatrader/jobs/4535655006?gh_src=509adb6f3us&__jvsd=LinkedIn
2. Click the "Apply" button to open the application form.
3. For each form field:
   - If the label or name matches one of the data keys below, fill with its value:
{mapping_str}
   - When you see a text input, type the value.
   - When you see a dropdown (<select>), click to open it, then choose the <option> whose visible text exactly matches (case-insensitive). If no exact match, pick the closest.
   - For radio buttons and checkboxes, select the option whose label or value matches the candidate data.
4. Do **not** upload a resume or cover letter.
5. Fill all other questions using your best judgment.
6. Do **not** click the "Submit" button. Wait for the user to manually close the browser when ready.
"""

    # Create and run the browser agent
    agent = Agent(
        task=task,
        llm=llm,
        enable_memory=False,
        # Example of additional options you can tweak:
        # headless=False,           # show the browser window
        # timeout=60,              # global timeout in seconds
    )
    result = await agent.run()

    # Output the agent's summary or logs
    print("=== Application Assistant Result ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
