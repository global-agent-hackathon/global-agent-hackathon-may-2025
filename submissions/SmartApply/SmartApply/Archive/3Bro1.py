import os
import sys
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.agent.views import ActionResult

import anyio

from patchright.async_api import BrowserContext

# Load environment variables
_ = load_dotenv(find_dotenv())

# Setup logging
logger = logging.getLogger(__name__)

# Add parent directory to system path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Browser and Controller
browser = Browser(
    config=BrowserConfig(
        headless=False,
        chrome_instance_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    )
)
#browser = Browser()
controller = Controller()

import pandas as pd
df = pd.read_csv(r"JobsData.csv")
num_job = 0
#job_url = df["Apply_URL"].iloc[num_job]
job_url = "https://remotive.com/remote-jobs/design/brand-designer-1997613"

# --- Actions --- #
@controller.registry.action('Upload a file directly without opening file picker')
async def upload_resume_and_cover_letter(resume_path: str, coverLetter_path: str, browser: BrowserContext):
    import os
    if not os.path.isfile(resume_path):
        return ActionResult(error=f"Resume file '{resume_path}' does not exist.")
    if not os.path.isfile(coverLetter_path):
        return ActionResult(error=f"Cover letter file '{coverLetter_path}' does not exist.")

    page = await browser.get_current_page()

    # Find all input[type="file"] elements
    file_inputs = await page.query_selector_all('input[type="file"]')
    num_inputs = len(file_inputs)
    
    if num_inputs == 0:
        return ActionResult(error="No file input fields found on the page.")
        
    try:
        if num_inputs == 1:
            # If only one input, upload resume
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[0])
            await file_inputs[0].set_input_files(resume_path)
            return ActionResult(extracted_content="Uploaded resume to single file input.")
            
        elif num_inputs == 2:
            # If two inputs, upload resume first, then cover letter
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[0])
            await file_inputs[0].set_input_files(resume_path)
            
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[1])
            await file_inputs[1].set_input_files(coverLetter_path)
            return ActionResult(extracted_content="Uploaded resume and cover letter to two file inputs.")
            
        elif num_inputs >= 3:
            # If three or more inputs, use specific indices
            # Resume goes to index 1, cover letter to index 2
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[1])
            await file_inputs[1].set_input_files(resume_path)
            
            await page.evaluate("(element) => element.style.display = 'block'", file_inputs[2])
            await file_inputs[2].set_input_files(coverLetter_path)
            return ActionResult(extracted_content="Uploaded resume and cover letter to specific file inputs (indices 1 and 2).")

        return ActionResult(extracted_content=f"Successfully handled file uploads for {num_inputs} file input(s).")
    except Exception as e:
        return ActionResult(error=f"Upload failed: {str(e)}")


@controller.action('Read file content from available file paths')
async def read_file(path: str, file_path: list[str]):
    if path not in file_path:
        return ActionResult(error=f'File path {path} is not available')

    async with await anyio.open_file(path, 'r') as f:
        content = await f.read()
    logger.info(f'Read file content: {content[:100]}...')  # Only log first 100 chars
    return ActionResult(extracted_content=content, include_in_memory=True)

# --- Personal Details --- #
@controller.action('Fetch my personal details for form filling')
async def fetch_personal_details():
    personal_details = {
        "Email": "r2raviteja@gmail.com",
        "password": "-",
        "First name": "Raviteja",
        "middle name": "",
        "Last name": "Rachamadugu",
        "Phone number": "15216442399",
        "Language": "English",
        "Secondary Phone": None,
        "Street Address": "8",
        "City": "Munich",
        "State": "Germany",
        "Zip / Postal Code": None,
        "Country": "Germany",
        "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/"
    }
    logger.info(f'Fetched personal details.')
    return ActionResult(extracted_content=str(personal_details), include_in_memory=True)

personal_details = {
        "Email": "r2raviteja@gmail.com",
        "password": "QWERTYu123456&",
        "First name": "Raviteja",
        "middle name": "",
        "Last name": "Rachamadugu",
        "Phone number": "15216442399",
        "Language": "English",
        "Secondary Phone": None,
        "Street Address": None,
        "City": "Munich",
        "State": "Germany",
        "Zip / Postal Code": None,
        "Country": "Germany",
        "Salary":"60000",
        "Notice period":"1 month",
        "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/"
    }

# --- Main Function --- #
from langchain_openai import ChatOpenAI
llmo = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key= "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",
    model= "google/gemini-2.0-flash-exp:free",  # Free model
)

from langchain_groq import ChatGroq
llmq = ChatGroq(
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.7
)

llmg=ChatGoogleGenerativeAI(model='gemini-1.5-flash')
llmg=llmg

async def main():
    async with await browser.new_context() as context:
        resume_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/CV.pdf').resolve()
        coverLetter_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/User/CL.docx').resolve()
        available_file_paths = [str(resume_path),str(coverLetter_path)]
        job_url = "https://contra.com/opportunity/svEmslqA-brand-designer?utm_source=remotive&utm_medium=referral&utm_campaign=w18"
        # break the task into two parts
        task1 = f" Go to the job url: {job_url} and click 'Apply' button"
        task2 = f"Fill the form fields sequentially by index order
        fill the location field carefully - type the city 'Munich' and wait 4 seconds for dropdown suggestions to appear, then select 1st option"
        

        agent1 = Agent(
            task=task1,
            llm=llmg,
            controller=controller,
            browser=browser,
            browser_context=context,
            available_file_paths=available_file_paths,
        )

        result1 = await agent1.run()  # ⬅️ Capture the result

        agent2 = Agent(
            task=task2,
            llm=llmg,
            controller=controller,
            browser=browser,
            browser_context=context,
            available_file_paths=available_file_paths,
        )

        result2 = await agent2.run()  # ⬅️ Capture the result

        await browser.close()

    # Save the output to a file
    output_file = Path('agent_output.txt')

    final_result = result1.final_result()
    is_done = result1.is_done()
    has_errors = result1.has_errors()
    model_thoughts = result1.model_thoughts()
    action_results = result1.action_results()

    print("Final Result:")
    print(final_result)
    print("Is Done:")
    print(is_done)
    print("Has Errors:")
    print(has_errors)
    print("Model Thoughts:")
    print(model_thoughts)
    print("Action Results:")
    print(action_results)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(result1))


if __name__ == '__main__':
    asyncio.run(main())
