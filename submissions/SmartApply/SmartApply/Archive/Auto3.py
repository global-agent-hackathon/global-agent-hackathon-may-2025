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
controller = Controller()

# --- Actions --- #

@controller.action('Upload resume file to an upload element')
async def upload_resume(index: int, path: str, browser: BrowserContext, available_file_paths: list[str]):
    if path not in available_file_paths:
        return ActionResult(error=f'File path {path} is not available')

    if not os.path.exists(path):
        return ActionResult(error=f'File {path} does not exist')

    dom_el = await browser.get_dom_element_by_index(index)
    file_upload_dom_el = dom_el.get_file_upload_element()

    if file_upload_dom_el is None:
        msg = f'No file upload element found at index {index}'
        logger.info(msg)
        return ActionResult(error=msg)

    file_upload_el = await browser.get_locate_element(file_upload_dom_el)

    if file_upload_el is None:
        msg = f'No file upload element found at index {index}'
        logger.info(msg)
        return ActionResult(error=msg)

    try:
        await file_upload_el.set_input_files(path)
        msg = f'Successfully uploaded file at index {index}'
        logger.info(msg)
        return ActionResult(extracted_content=msg, include_in_memory=True)
    except Exception as e:
        msg = f'Failed to upload file: {str(e)}'
        logger.error(msg)
        return ActionResult(error=msg)

@controller.action('Read file content from available file paths')
async def read_file(path: str, available_file_paths: list[str]):
    if path not in available_file_paths:
        return ActionResult(error=f'File path {path} is not available')

    async with await anyio.open_file(path, 'r') as f:
        content = await f.read()
    logger.info(f'Read file content: {content[:100]}...')  # Only log first 100 chars
    return ActionResult(extracted_content=content, include_in_memory=True)



# --- Personal Details --- #

personal_details = {
    "Email": "r2raviteja@gmail.com",
    "password": "-",
    "First name": "Raviteja",
    "middle name": "",
    "Last name": "Rachamadugu",
    "Phone number": "+49 15216 442399",
    "Language": "English",
    "Secondary Phone": None,
    "Street Address": None,
    "City": "Munich",
    "State": "Germany",
    "Zip / Postal Code": None,
    "Country": "Germany",
    "LinkedIn profile": "https://www.linkedin.com/in/rraviteja/"
}

# --- Main Function --- #

async def main():
    resume_path = Path('C:/Users/960ra/PycharmProjects/SmartApply/CV.pdf').resolve()
    available_file_paths = [str(resume_path)]

    task = f"""
    Apply for the Data Analyst position at ESDS by filling the form fields sequentially.

    Context:
    Personal details: {personal_details}

    Instructions:
    1. Navigate to: https://forms.gle/Ld15dXuMDRuRbK45A
    2. Wait for page load (5 seconds).
    3. Detect input fields by index order.
    4. Fill fields based on labels using provided personal details.
    5. Leave blank if no data available.
    6. Wait 5 seconds after each field fill.
    7. For resume upload:
        - Trigger upload popup.
        - Upload file from path: {resume_path}
    8. Submit form after filling.
    
    Important:
    - Move only forward.
    - Skip if unsure.
    """

    agent = Agent(
        task=task,
        llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp'),
        controller=controller,
        browser=browser,
        available_file_paths=available_file_paths,
    )

    result = await agent.run()  # ⬅️ Capture the result

    await browser.close()

    # Save the output to a file
    output_file = Path('agent_output.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(result))

    output_file = Path('Con_output.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(controller))
    
    input('Press Enter to exit...')

# --- Entry Point --- #

if __name__ == '__main__':
    asyncio.run(main())
